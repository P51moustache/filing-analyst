"""Exact-value tests for AIAnalyzer.calculate_trade_score (pure, no API).

Each expected number is computed by hand from the rules in
app/services/ai_analyzer.py::calculate_trade_score. Assertions are exact so a
change to the scoring weights breaks the test loudly.
"""

from app.services.ai_analyzer import AIAnalyzer


def test_strong_analysis_scores_full_marks():
    analyzer = AIAnalyzer()

    # Designed to max out every catalyst/quality clause and trip no risk penalty.
    analysis = {
        "financial_metrics": {
            "organic_growth": 0.20,      # >= 0.10  -> +8 ; truthy for clause 1
            "gross_margin": 0.60,        # > 0.40
            "operating_margin": 0.30,    # > 0.15  -> +8 (with gross_margin)
            "shareholder_yield": 0.05,   # >= 0.03 -> +8
            "fcf_to_ni": 1.0,            # >= 0.90 -> +10
            "ccc": 30,                   # 0 < ccc < 60 -> +7
            "sbc_pct_revenue": 0.05,     # <= 0.08
            "dilution_pct": 0.01,        # <= 0.02 -> +7 (both)
            "debt_to_ebitda": 1.0,       # <= 2.0  -> +6
            "interest_coverage": 10.0,   # >= 6.0  -> +5
        },
        "sector_metrics": {
            "rpo": 5000,                 # truthy for clause 1
            "backlog_yoy": 0.30,         # 0.30 > organic_growth 0.20 -> +8
        },
        "risk_indicators": {
            "material_weakness": False,
            "new_top_risks": False,
            "customer_concentration": False,
            "debt_maturity_24m": 0,
            "red_flags": [],
        },
        "catalysts": ["a", "b", "c", "d"],  # min(4*2, 8) = +8
    }

    result = analyzer.calculate_trade_score(analysis)

    # catalyst = 8 + 8 + 8 + 8 + 8 = 40 ; quality = 10 + 7 + 7 + 6 + 5 = 35 ; risk = 25
    assert result["catalyst_trend_score"] == 40.0
    assert result["quality_cash_score"] == 35.0
    assert result["risk_score"] == 25.0
    assert result["total_score"] == 100.0
    assert result["rating"] == "Strong Buy"


def test_weak_analysis_scores_near_zero_and_avoid():
    analyzer = AIAnalyzer()

    analysis = {
        "financial_metrics": {
            "organic_growth": 0.0,       # < 0.05 -> +0
            "gross_margin": 0.20,        # <= 0.40 -> clause fails
            "operating_margin": 0.05,
            "shareholder_yield": 0.0,    # < 0.03 -> +0
            "fcf_to_ni": 0.5,            # < 0.70 -> +0
            "ccc": 90,                   # not < 60 -> +0
            "sbc_pct_revenue": 0.20,     # > 0.08 -> clause fails -> +0
            "dilution_pct": 0.10,
            "debt_to_ebitda": 5.0,       # > 2.0 -> +0
            "interest_coverage": 1.0,    # < 6.0 -> +0
        },
        "sector_metrics": {
            "rpo": None,                 # falsy -> clause 1 +0
            "backlog_yoy": None,
        },
        "risk_indicators": {
            "material_weakness": True,    # -5
            "new_top_risks": True,        # -3
            "customer_concentration": True,  # -3
            "debt_maturity_24m": 200,     # > 100 -> -4
            "red_flags": ["f1", "f2", "f3"],  # 3 * -3 = -9
        },
        "catalysts": [],                  # +0
    }

    result = analyzer.calculate_trade_score(analysis)

    # catalyst = 0 ; quality = 0 ; risk = 25 - 9 - 5 - 3 - 3 - 4 = 1
    assert result["catalyst_trend_score"] == 0.0
    assert result["quality_cash_score"] == 0.0
    assert result["risk_score"] == 1.0
    assert result["total_score"] == 1.0
    assert result["rating"] == "Avoid"


def test_mid_analysis_exercises_partial_branches_and_hold():
    analyzer = AIAnalyzer()

    analysis = {
        "financial_metrics": {
            "organic_growth": 0.06,      # >= 0.05 but < 0.10 -> +4
            "gross_margin": 0.45,        # > 0.40
            "operating_margin": 0.16,    # > 0.15 -> +8
            "shareholder_yield": 0.02,   # < 0.03 -> +0
            "fcf_to_ni": 0.75,           # >= 0.70 but < 0.90 -> +6
            "ccc": 50,                   # 0 < ccc < 60 -> +7
            # sbc_pct_revenue / debt_to_ebitda omitted -> treated as 1 / 10 -> clauses fail
            "interest_coverage": 6.0,    # >= 6.0 -> +5
        },
        "sector_metrics": {
            "rpo": 1000,                 # truthy, but...
            "backlog_yoy": 0.05,         # 0.05 > organic_growth 0.06 is False -> +0
        },
        "risk_indicators": {
            "red_flags": ["only-one"],    # 1 * -3 = -3
            "debt_maturity_24m": 50,      # not > 100
        },
        "catalysts": ["x", "y"],          # min(2*2, 8) = +4
    }

    result = analyzer.calculate_trade_score(analysis)

    # catalyst = 0 + 8 + 4 + 4 + 0 = 16 ; quality = 6 + 7 + 0 + 0 + 5 = 18 ; risk = 25 - 3 = 22
    assert result["catalyst_trend_score"] == 16.0
    assert result["quality_cash_score"] == 18.0
    assert result["risk_score"] == 22.0
    assert result["total_score"] == 56.0
    assert result["rating"] == "Hold"
