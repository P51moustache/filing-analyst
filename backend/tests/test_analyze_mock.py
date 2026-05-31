"""Full analyze_10k path with the Claude API mocked out (offline).

Monkeypatches both messages.count_tokens (token-budget step) and messages.parse
(structured-outputs call) so the entire extract -> map pipeline runs with no key
and no network, proving the wiring around the SDK is correct.
"""

from app.services.ai_analyzer import AIAnalyzer
from app.models.schemas import (
    ExtractedAnalysis,
    FinancialMetrics,
    SectorMetricsExtract,
    RiskIndicators,
    SegmentDatum,
    GeoConcentration,
    TopCustomer,
    SectorType,
)


class _StubUsage:
    def __init__(self):
        self.input_tokens = 1200
        self.output_tokens = 800
        self.cache_read_input_tokens = 1000
        self.cache_creation_input_tokens = 200


class _StubParseResponse:
    def __init__(self, parsed_output):
        self.parsed_output = parsed_output
        self.usage = _StubUsage()
        self.stop_reason = "end_turn"


class _StubCountResponse:
    def __init__(self):
        self.input_tokens = 1000


def _extracted() -> ExtractedAnalysis:
    return ExtractedAnalysis(
        ticker="X",
        company_name="Co",
        fiscal_year=2024,
        sector=SectorType.SEMIS,
        financial_metrics=FinancialMetrics(revenue=2000.0, gross_margin=0.55),
        sector_metrics=SectorMetricsExtract(backlog=900.0, backlog_yoy=0.2),
        risk_indicators=RiskIndicators(red_flags=[]),
        catalysts=["fab ramp", "export-control relief"],
        segments=[SegmentDatum(name="Compute", revenue=1500.0, margin=0.6, growth=0.3)],
        geographic_concentration=[GeoConcentration(region="APAC", revenue_pct=0.5)],
        top_customers=[TopCustomer(name="Hyperscaler", revenue_pct=0.22)],
        ai_insights="Cyclical upturn with backlog support.",
        key_takeaways=["takeaway one", "takeaway two"],
    )


def test_analyze_10k_full_path_with_mocked_api(monkeypatch):
    analyzer = AIAnalyzer()
    expected = _extracted()

    def fake_parse(*args, **kwargs):
        # The schema is passed as output_format; we just confirm the call shape and
        # return a stub the way the real SDK would.
        assert kwargs.get("output_format") is ExtractedAnalysis
        return _StubParseResponse(expected)

    def fake_count_tokens(*args, **kwargs):
        return _StubCountResponse()

    monkeypatch.setattr(analyzer.client.messages, "parse", fake_parse)
    monkeypatch.setattr(analyzer.client.messages, "count_tokens", fake_count_tokens)

    result = analyzer.analyze_10k(
        {"item_1_business": "x" * 600},
        {"ticker": "X", "company_name": "Co", "fiscal_year": "2024"},
    )

    assert result["ticker"] == "X"
    assert result["company_name"] == "Co"
    assert result["fiscal_year"] == 2024
    assert result["sector"] == "Semiconductors/Hardware"
    # catalysts mapped straight through
    assert result["catalysts"] == ["fab ramp", "export-control relief"]
    # segments reshaped to a name-keyed dict
    assert result["segments"] == {
        "Compute": {"revenue": 1500.0, "margin": 0.6, "growth": 0.3}
    }
    # geographic concentration reshaped to a region-keyed dict
    assert result["geographic_concentration"] == {"APAC": 0.5}
    # top customers as a list of dicts
    assert result["top_customers"] == [{"name": "Hyperscaler", "revenue_pct": 0.22}]
