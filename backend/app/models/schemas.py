from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadResponse(BaseModel):
    analysis_id: str
    filename: str
    file_size: int
    status: AnalysisStatus


class AnalysisRequest(BaseModel):
    analysis_id: str
    custom_prompt: Optional[str] = Field(
        None,
        description="Custom analysis focus or specific items to extract"
    )


class SectorType(str, Enum):
    SAAS = "SaaS"
    SEMIS = "Semiconductors/Hardware"
    DEFENSE = "Defense/Industrials"
    RETAIL = "Retail/CPG"
    BIOTECH = "Biotech/MedTech"
    BANKS = "Banks/Fintech"
    ENERGY = "Energy"
    REITS = "REITs"
    OTHER = "Other"


class FinancialMetrics(BaseModel):
    # Revenue metrics
    revenue: Optional[float] = None
    organic_growth: Optional[float] = None
    fx_impact: Optional[float] = None
    ma_impact: Optional[float] = None

    # Margins
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None

    # Cash flow
    fcf: Optional[float] = None
    fcf_margin: Optional[float] = None
    fcf_to_ni: Optional[float] = None

    # Working capital
    dso: Optional[float] = None
    dio: Optional[float] = None
    dpo: Optional[float] = None
    ccc: Optional[float] = None

    # Leverage
    net_debt: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    interest_coverage: Optional[float] = None

    # SBC
    sbc_amount: Optional[float] = None
    sbc_pct_revenue: Optional[float] = None
    dilution_pct: Optional[float] = None

    # Capital allocation
    buybacks: Optional[float] = None
    dividends: Optional[float] = None
    shareholder_yield: Optional[float] = None

    # Other
    capex: Optional[float] = None
    deferred_revenue: Optional[float] = None
    deferred_revenue_yoy: Optional[float] = None
    accruals_ratio: Optional[float] = None


class SectorSpecificMetrics(BaseModel):
    # SaaS
    rpo: Optional[float] = None
    current_rpo: Optional[float] = None
    billings: Optional[float] = None
    rule_of_40: Optional[float] = None

    # Semis/Hardware
    backlog: Optional[float] = None
    backlog_yoy: Optional[float] = None

    # Defense
    funded_backlog: Optional[float] = None
    unfunded_backlog: Optional[float] = None
    book_to_bill: Optional[float] = None

    # Other sector-specific
    other_metrics: Optional[Dict[str, Any]] = None


class RiskIndicators(BaseModel):
    material_weakness: bool = False
    new_top_risks: bool = False
    customer_concentration: bool = False
    debt_maturity_24m: Optional[float] = None
    off_balance_commitments: Optional[float] = None
    red_flags: List[str] = []


class CatalystInfo(BaseModel):
    catalysts: List[str] = []
    catalyst_calendar: Dict[str, str] = {}


class TradeScore(BaseModel):
    total_score: float = Field(..., ge=0, le=100)
    catalyst_trend_score: float = Field(..., ge=0, le=40)
    quality_cash_score: float = Field(..., ge=0, le=35)
    risk_score: float = Field(..., ge=0, le=25)
    rating: str  # "Strong Buy", "Buy", "Hold", "Avoid"


# ---------------------------------------------------------------------------
# Structured-output schema for the Claude extraction step.
#
# This is a CLOSED schema (no free-form dicts) so it satisfies the JSON-schema
# constraints required by the Anthropic structured-outputs API. `messages.parse`
# generates the schema from these models, the API guarantees the response
# conforms, and the analyzer maps it back to the dict shapes the scoring and
# reporting pipeline expects. The 0-100 trade score is computed deterministically
# in Python, not by the model.
# ---------------------------------------------------------------------------


class SectorMetricsExtract(BaseModel):
    rpo: Optional[float] = None
    current_rpo: Optional[float] = None
    billings: Optional[float] = None
    rule_of_40: Optional[float] = None
    backlog: Optional[float] = None
    backlog_yoy: Optional[float] = None
    funded_backlog: Optional[float] = None
    unfunded_backlog: Optional[float] = None
    book_to_bill: Optional[float] = None


class SegmentDatum(BaseModel):
    name: str
    revenue: Optional[float] = None
    margin: Optional[float] = None
    growth: Optional[float] = None


class GeoConcentration(BaseModel):
    region: str
    revenue_pct: Optional[float] = None


class TopCustomer(BaseModel):
    name: str
    revenue_pct: Optional[float] = None


class ExtractedAnalysis(BaseModel):
    """The structured payload Claude extracts from a 10-K filing."""
    ticker: str = "Unknown"
    company_name: str = "Unknown"
    fiscal_year: Optional[int] = None
    sector: SectorType = SectorType.OTHER
    financial_metrics: FinancialMetrics = Field(default_factory=FinancialMetrics)
    sector_metrics: SectorMetricsExtract = Field(default_factory=SectorMetricsExtract)
    risk_indicators: RiskIndicators = Field(default_factory=RiskIndicators)
    catalysts: List[str] = Field(default_factory=list)
    segments: List[SegmentDatum] = Field(default_factory=list)
    geographic_concentration: List[GeoConcentration] = Field(default_factory=list)
    top_customers: List[TopCustomer] = Field(default_factory=list)
    ai_insights: str = ""
    key_takeaways: List[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    analysis_id: str
    ticker: str = "Unknown"
    company_name: str = "Unknown"
    fiscal_year: Optional[int] = None
    sector: SectorType

    financial_metrics: FinancialMetrics
    sector_metrics: SectorSpecificMetrics
    risk_indicators: RiskIndicators
    catalyst_info: CatalystInfo
    trade_score: TradeScore

    # Segment information
    segments: Optional[Dict[str, Any]] = None
    geographic_concentration: Optional[Dict[str, float]] = None
    top_customers: Optional[List[Dict[str, Any]]] = None

    # Additional insights
    ai_insights: str
    key_takeaways: List[str] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)
    excel_report_path: Optional[str] = None


class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: AnalysisStatus
    progress: int = Field(..., ge=0, le=100)
    message: Optional[str] = None
    result: Optional[AnalysisResult] = None
    error: Optional[str] = None
