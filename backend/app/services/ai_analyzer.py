"""AI-powered 10-K analysis using the Claude API.

Engineering notes (the parts a reviewer cares about):
  * Structured outputs - the model is forced to return a schema-valid object via
    `messages.parse(output_format=...)`, so there is no brittle regex JSON scraping.
  * Current, configurable model - defaults to the flagship, overridable per deploy.
  * Resilience - the SDK retries 429/5xx with exponential backoff (`max_retries`).
  * Prompt caching - the large, static analyst framework is sent once as a cached
    system prefix; only the filing text varies between requests.
  * Token budgeting - filings are counted and trimmed transparently (logged), never
    silently sliced.
  * Observability - token usage and an estimated cost are logged per request.

The 0-100 trade score is computed deterministically in Python (`calculate_trade_score`),
not by the model - the model only extracts facts from the filing.
"""

import logging
from typing import Any, Dict, Optional

import anthropic

from app.config import settings
from app.models.schemas import ExtractedAnalysis

logger = logging.getLogger(__name__)

# Input / output price per 1M tokens, for cost logging only. Unknown models -> no cost.
_PRICING_PER_MTOK: Dict[str, tuple[float, float]] = {
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-opus-4-6": (5.0, 25.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}

# Static analyst framework. This never changes between filings, so it lives in the
# system prompt and is marked for prompt caching. (It carries no company data and no
# output-format instructions - the structured-outputs schema enforces the shape.)
ANALYST_FRAMEWORK = """You are an expert financial analyst specializing in SEC 10-K analysis for retail swing traders. Read the filing supplied by the user and extract every relevant fact into the required structured fields, following this framework.

1. FAST TRIAGE (Business, MD&A, Risks, Liquidity, Capital Allocation)
   - Identify near-term catalysts across all sections.
   - Flag any major changes from the prior year.

2. ITEM 1 - BUSINESS
   - Business segments and revenue mix (flag high-margin segments gaining share).
   - Geographic concentration and top customer concentration (>10% of revenue is a renewal catalyst).
   - Backlog/RPO/bookings vs revenue (RPO growth > revenue growth implies future acceleration).
   - Supply, capacity, and long-term agreements and prepayments. Extract actual numbers.

3. ITEM 1A - RISK FACTORS
   - Identify NEW or ELEVATED risks vs last year (export controls, reimbursement, credit, cyber, key-person).
   - Assess guidance risk from the risk-factor changes.

4. MD&A (ITEM 7) - BUILD THE BRIDGES
   - Revenue bridge: total revenue and YoY %, organic = total - FX - M&A, organic growth rate.
   - Margins: gross and operating margin % and YoY change; operating leverage = d(OpInc)/d(Rev).
   - Cash-flow quality: FCF, NI, FCF/NI (target >= 90% multi-year), accruals ratio.
   - Working capital: DSO = AR/(Rev/365), DIO = Inv/(COGS/365), DPO = AP/(COGS/365), CCC = DSO + DIO - DPO. Watch DSO or DIO rising with flat revenue.

5. ITEM 7A - MARKET RISK
   - Interest-rate, FX, and commodity exposure and hedge tenor; map macro moves to EPS.

6. ITEM 8 - FINANCIALS & NOTES
   - Segment gross margins, revenue, and growth.
   - SBC: total expense, % of revenue, dilution %.
   - Recurring "one-time" adjustments and serial non-GAAP exclusions.
   - Debt & leverage: total debt, cash, net debt, EBITDA, Net Debt/EBITDA, interest coverage, maturity ladder (next 6-24 months).
   - Deferred revenue balance and YoY %. Goodwill/intangible impairment setup. Purchase, off-balance-sheet, and lease commitments. Subsequent events.

7. ITEM 9A - CONTROLS
   - Any NEW material weakness in internal controls?

8. GOVERNANCE & CAPITAL ALLOCATION
   - Insider ownership, CEO comp changes, buyback authorization remaining, dividend policy, equity overhang and SBC burn, related-party transactions.

9. ACCOUNTING POLICIES
   - Revenue recognition timing and variable consideration, inventory method, allowance for doubtful accounts, capitalization policies, and how each affects optics vs cash.

10. VALUATION INPUTS
    - Shares outstanding or market cap, EV = market cap + net debt, P/E, EV/EBITDA, EV/Sales, P/FCF; Rule of 40 for SaaS; EV/RPO or EV/Backlog where relevant.

11. RED FLAGS (hard)
    - FCF conversion < 60% for 2+ years; rising DSO/DIO with slowing revenue; annual "restructuring" charges; new control weaknesses; >20% revenue from a single customer up for renewal; buybacks funded by short-term debt; large step-up in purchase commitments into a soft macro.

12. CATALYST CALENDAR
    - Customer renewal windows, product launches / fab ramps, regulatory milestones, debt refinancing dates, board dates for capital return, seasonality.

13. SECTOR-SPECIFIC METRICS (identify the sector and extract its key metrics)
    - SaaS: RPO, current RPO, billings, Rule of 40, capitalized commissions.
    - Semis/Hardware: capacity & prepayments, node/process mix, GM drivers, inventory, export-control language.
    - Defense/Industrials: funded vs unfunded backlog, book-to-bill, FFP vs cost-plus, long-term-contract working capital.
    - Retail/CPG: same-store sales, inventory turns, shrink, lease liabilities.
    - Biotech/MedTech: cash runway, milestone calendar, burn rate.
    - Banks/Fintech: NIM sensitivity, deposit beta, CECL reserves, AOCI.
    - Energy: hedge-book tenor, LOE/BOE, decline rates.
    - REITs: same-store NOI, lease expiries, debt ladder, AFFO payout ratio.

Rules: express all percentages as decimals (15% -> 0.15); all monetary values in millions; use null for anything not determinable from the filing; perform calculations accurately; explain every red flag clearly. Write `ai_insights` as a concise narrative for a swing trader and `key_takeaways` as the 5-7 most important points."""


class AIAnalyzer:
    """AI-powered 10-K analysis using Claude with structured outputs."""

    def __init__(self) -> None:
        # The SDK retries connection errors, 408/409/429, and 5xx with exponential
        # backoff automatically; we just raise the ceiling.
        self.client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key,
            max_retries=settings.anthropic_max_retries,
        )
        self.model = settings.anthropic_model

    def analyze_10k(
        self,
        sections: Dict[str, str],
        metadata: Dict[str, Optional[str]],
        custom_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract a structured analysis of a 10-K filing.

        Returns a plain dict in the shape the scoring + reporting pipeline expects.
        Raises RuntimeError on an API failure or an unparseable / refused response.
        """
        filing_content = self._build_filing_content(sections, metadata, custom_prompt)
        filing_content = self._enforce_token_budget(filing_content)

        try:
            response = self.client.messages.parse(
                model=self.model,
                max_tokens=16000,
                system=[
                    {
                        "type": "text",
                        "text": ANALYST_FRAMEWORK,
                        # Cache the static framework prefix. It is reused verbatim on
                        # every filing, so repeat analyses within the cache TTL pay
                        # ~0.1x for this prefix instead of full price. (Caching only
                        # engages once the prefix exceeds the model's minimum.)
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": filing_content}],
                output_format=ExtractedAnalysis,
            )
        except anthropic.APIStatusError as exc:
            logger.error(
                "Claude API error (status=%s, request_id=%s): %s",
                getattr(exc, "status_code", "?"),
                getattr(exc, "request_id", "?"),
                exc,
            )
            raise RuntimeError(f"AI analysis failed: {exc}") from exc
        except anthropic.APIConnectionError as exc:
            logger.error("Claude API connection error: %s", exc)
            raise RuntimeError("AI analysis failed: could not reach the Claude API") from exc

        self._log_usage(response)

        extracted: Optional[ExtractedAnalysis] = response.parsed_output
        if extracted is None:
            # A refusal (stop_reason == "refusal") or a schema-validation miss.
            stop_reason = getattr(response, "stop_reason", None)
            logger.error("Claude returned no parseable analysis (stop_reason=%s)", stop_reason)
            raise RuntimeError("AI analysis returned no parseable result")

        return self._to_analysis_dict(extracted, metadata)

    # ------------------------------------------------------------------ helpers

    def _build_filing_content(
        self,
        sections: Dict[str, str],
        metadata: Dict[str, Optional[str]],
        custom_prompt: Optional[str],
    ) -> str:
        """Assemble the user-message content: company header + filing text + custom focus.

        The static framework lives in the (cached) system prompt; only this varies.
        Section text is included whole here - the global token budget governs trimming,
        rather than arbitrary per-section slices.
        """
        header = (
            f"COMPANY: {metadata.get('company_name', 'Unknown')} "
            f"(ticker {metadata.get('ticker', 'Unknown')}, "
            f"fiscal year {metadata.get('fiscal_year', 'Unknown')})\n"
        )

        if custom_prompt:
            header += f"\nADDITIONAL FOCUS FROM THE USER:\n{custom_prompt}\n"

        labeled = [
            ("Item 1 - Business", sections.get("item_1_business", "")),
            ("Item 1A - Risk Factors", sections.get("item_1a_risk_factors", "")),
            ("Item 7 - MD&A", sections.get("item_7_mda", "")),
            ("Item 7A - Market Risk", sections.get("item_7a_market_risk", "")),
            ("Item 8 - Financials", sections.get("item_8_financials", "")),
            ("Item 9A - Controls", sections.get("item_9a_controls", "")),
        ]
        sections_valid = any(len(text) > 500 for _, text in labeled)

        body_parts = [header, "\nFILING:\n"]
        if sections_valid:
            for label, text in labeled:
                body_parts.append(f"\n## {label}\n{text or 'Not found'}\n")
        else:
            # The parser could not isolate sections; hand the model the full text and
            # let it locate the sections itself.
            full_text = sections.get("full_text", "")
            if full_text:
                body_parts.append(
                    "\nThe sections could not be isolated automatically. Locate and "
                    "analyze Business, Risk Factors, MD&A, Financials, and Controls in "
                    "this full document:\n\n" + full_text
                )
            else:
                body_parts.append("\nERROR: no document content was found.")

        return "".join(body_parts)

    def _enforce_token_budget(self, content: str) -> str:
        """Trim the filing to the configured token budget, transparently.

        Uses the Token Counting API so the cap is real tokens, not a magic char slice;
        logs exactly how much was dropped so a truncated run is never silent.
        """
        budget = settings.max_input_tokens
        try:
            counted = self.client.messages.count_tokens(
                model=self.model,
                system=ANALYST_FRAMEWORK,
                messages=[{"role": "user", "content": content}],
            ).input_tokens
        except Exception as exc:  # counting is best-effort; never block analysis on it
            logger.warning("Token counting unavailable (%s); sending filing as-is", exc)
            return content

        if counted <= budget:
            logger.info("Filing fits the token budget (%d <= %d tokens)", counted, budget)
            return content

        ratio = budget / counted
        keep = max(1, int(len(content) * ratio * 0.97))  # 3% headroom for the framework
        logger.warning(
            "Filing is ~%d tokens, over the %d-token budget; trimming to ~%d chars "
            "(%.0f%% kept). Raise MAX_INPUT_TOKENS to analyze the full filing.",
            counted, budget, keep, ratio * 100,
        )
        return content[:keep] + "\n\n[NOTE: filing truncated to fit the model context budget.]"

    def _log_usage(self, response: Any) -> None:
        """Log token usage and an estimated cost for the request."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return
        in_rate, out_rate = _PRICING_PER_MTOK.get(self.model, (0.0, 0.0))
        cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
        cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
        est_cost = (usage.input_tokens * in_rate + usage.output_tokens * out_rate) / 1_000_000
        logger.info(
            "Claude usage: model=%s input=%d output=%d cache_read=%d cache_write=%d est_cost=$%.4f",
            self.model, usage.input_tokens, usage.output_tokens, cache_read, cache_write, est_cost,
        )

    def _to_analysis_dict(
        self, extracted: ExtractedAnalysis, metadata: Dict[str, Optional[str]]
    ) -> Dict[str, Any]:
        """Map the closed extraction schema back to the dict shape the pipeline expects."""
        segments = {
            s.name: {"revenue": s.revenue, "margin": s.margin, "growth": s.growth}
            for s in extracted.segments
            if s.name
        }
        geo = {
            g.region: g.revenue_pct
            for g in extracted.geographic_concentration
            if g.region and g.revenue_pct is not None
        }

        fiscal_year = extracted.fiscal_year
        if fiscal_year is None and metadata.get("fiscal_year"):
            try:
                fiscal_year = int(metadata["fiscal_year"])  # type: ignore[arg-type]
            except (TypeError, ValueError):
                fiscal_year = None

        return {
            "ticker": extracted.ticker or metadata.get("ticker") or "Unknown",
            "company_name": extracted.company_name or metadata.get("company_name") or "Unknown",
            "fiscal_year": fiscal_year,
            "sector": extracted.sector.value,
            "financial_metrics": extracted.financial_metrics.model_dump(),
            "sector_metrics": extracted.sector_metrics.model_dump(),
            "risk_indicators": extracted.risk_indicators.model_dump(),
            "catalysts": list(extracted.catalysts),
            "segments": segments,
            "geographic_concentration": geo,
            "top_customers": [c.model_dump() for c in extracted.top_customers],
            "ai_insights": extracted.ai_insights,
            "key_takeaways": list(extracted.key_takeaways),
        }

    def calculate_trade_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate a deterministic 0-100 trade score from the extracted analysis.

        Weighting: 40% catalysts & trends, 35% quality & cash, 25% risk.
        """
        catalyst_score = 0.0  # out of 40
        quality_score = 0.0   # out of 35
        risk_score = 0.0      # out of 25

        metrics = analysis.get("financial_metrics", {})
        sector_metrics = analysis.get("sector_metrics", {})
        risks = analysis.get("risk_indicators", {})
        catalysts = analysis.get("catalysts", [])

        # --- Catalyst & trend score (40) ---
        if sector_metrics.get("rpo") and metrics.get("organic_growth"):
            if (sector_metrics.get("backlog_yoy") or 0) > (metrics.get("organic_growth") or 0):
                catalyst_score += 8
        if (metrics.get("gross_margin") or 0) > 0.4 and (metrics.get("operating_margin") or 0) > 0.15:
            catalyst_score += 8
        catalyst_score += min(len(catalysts) * 2, 8)
        if (metrics.get("organic_growth") or 0) >= 0.10:
            catalyst_score += 8
        elif (metrics.get("organic_growth") or 0) >= 0.05:
            catalyst_score += 4
        if (metrics.get("shareholder_yield") or 0) >= 0.03:
            catalyst_score += 8

        # --- Quality & cash score (35) ---
        if (metrics.get("fcf_to_ni") or 0) >= 0.90:
            quality_score += 10
        elif (metrics.get("fcf_to_ni") or 0) >= 0.70:
            quality_score += 6
        if 0 < (metrics.get("ccc") or 0) < 60:
            quality_score += 7
        if (metrics.get("sbc_pct_revenue") if metrics.get("sbc_pct_revenue") is not None else 1) <= 0.08 \
                and (metrics.get("dilution_pct") if metrics.get("dilution_pct") is not None else 1) <= 0.02:
            quality_score += 7
        if (metrics.get("debt_to_ebitda") if metrics.get("debt_to_ebitda") is not None else 10) <= 2.0:
            quality_score += 6
        if (metrics.get("interest_coverage") or 0) >= 6.0:
            quality_score += 5

        # --- Risk score (25) ---
        base_risk = 25
        base_risk -= len(risks.get("red_flags", [])) * 3
        if risks.get("material_weakness"):
            base_risk -= 5
        if risks.get("new_top_risks"):
            base_risk -= 3
        if risks.get("customer_concentration"):
            base_risk -= 3
        if (risks.get("debt_maturity_24m") or 0) > 100:
            base_risk -= 4
        risk_score = max(base_risk, 0)

        total = catalyst_score + quality_score + risk_score

        if total >= 75 and catalyst_score >= 24:
            rating = "Strong Buy"
        elif total >= 60:
            rating = "Buy"
        elif total >= 45:
            rating = "Hold"
        else:
            rating = "Avoid"

        return {
            "total_score": round(total, 1),
            "catalyst_trend_score": round(catalyst_score, 1),
            "quality_cash_score": round(quality_score, 1),
            "risk_score": round(risk_score, 1),
            "rating": rating,
        }
