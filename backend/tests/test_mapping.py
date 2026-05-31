"""Tests for AIAnalyzer._to_analysis_dict (pure mapping, no API).

Verifies the closed ExtractedAnalysis schema is reshaped into the dict shapes the
scoring + reporting pipeline expects: lists of objects become name/region-keyed
dicts, nested models become plain dicts, and scalar lists pass through.
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


def _build_extracted() -> ExtractedAnalysis:
    return ExtractedAnalysis(
        ticker="X",
        company_name="ExampleCo",
        fiscal_year=2024,
        sector=SectorType.SAAS,
        financial_metrics=FinancialMetrics(revenue=1000.0, gross_margin=0.6),
        sector_metrics=SectorMetricsExtract(rpo=500.0),
        risk_indicators=RiskIndicators(red_flags=["concentration"]),
        catalysts=["product launch", "buyback authorization"],
        segments=[
            SegmentDatum(name="Cloud", revenue=700.0, margin=0.65, growth=0.25),
            SegmentDatum(name="Services", revenue=300.0, margin=0.30, growth=0.05),
        ],
        geographic_concentration=[GeoConcentration(region="Americas", revenue_pct=0.7)],
        top_customers=[TopCustomer(name="BigCorp", revenue_pct=0.15)],
        ai_insights="Solid quality compounder.",
        key_takeaways=["k1", "k2"],
    )


def test_to_analysis_dict_reshapes_collections():
    analyzer = AIAnalyzer()
    extracted = _build_extracted()

    result = analyzer._to_analysis_dict(extracted, {"ticker": "X"})

    # segments -> dict keyed by name
    assert isinstance(result["segments"], dict)
    assert set(result["segments"].keys()) == {"Cloud", "Services"}
    assert result["segments"]["Cloud"] == {"revenue": 700.0, "margin": 0.65, "growth": 0.25}

    # geographic_concentration -> dict keyed by region
    assert isinstance(result["geographic_concentration"], dict)
    assert result["geographic_concentration"] == {"Americas": 0.7}

    # financial_metrics -> plain dict (model_dump)
    assert isinstance(result["financial_metrics"], dict)
    assert result["financial_metrics"]["revenue"] == 1000.0
    assert result["financial_metrics"]["gross_margin"] == 0.6

    # catalysts -> list, passed through verbatim
    assert isinstance(result["catalysts"], list)
    assert result["catalysts"] == ["product launch", "buyback authorization"]

    # top_customers -> list of dicts
    assert isinstance(result["top_customers"], list)
    assert result["top_customers"] == [{"name": "BigCorp", "revenue_pct": 0.15}]

    # scalar passthrough / metadata
    assert result["ticker"] == "X"
    assert result["company_name"] == "ExampleCo"
    assert result["fiscal_year"] == 2024
    assert result["sector"] == "SaaS"
    assert result["ai_insights"] == "Solid quality compounder."
    assert result["key_takeaways"] == ["k1", "k2"]
