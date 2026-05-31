// Shapes returned by the Filing Analyst FastAPI backend. Kept in sync with the
// web client (frontend/src/types/analysis.ts) and the backend Pydantic schemas.

export enum AnalysisStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface UploadResponse {
  analysis_id: string;
  filename: string;
  file_size: number;
  status: AnalysisStatus;
}

export interface FinancialMetrics {
  revenue?: number;
  organic_growth?: number;
  gross_margin?: number;
  operating_margin?: number;
  fcf?: number;
  fcf_to_ni?: number;
  dso?: number;
  ccc?: number;
  net_debt?: number;
  debt_to_ebitda?: number;
  sbc_pct_revenue?: number;
  shareholder_yield?: number;
}

export interface RiskIndicators {
  material_weakness: boolean;
  new_top_risks: boolean;
  customer_concentration: boolean;
  red_flags: string[];
}

export interface TradeScore {
  total_score: number;
  catalyst_trend_score: number;
  quality_cash_score: number;
  risk_score: number;
  rating: string;
}

export interface AnalysisResult {
  analysis_id: string;
  ticker: string;
  company_name: string;
  fiscal_year?: number;
  sector: string;
  financial_metrics: FinancialMetrics;
  risk_indicators: RiskIndicators;
  trade_score: TradeScore;
  catalyst_info?: { catalysts: string[] };
  ai_insights: string;
  key_takeaways: string[];
}

export interface AnalysisStatusResponse {
  analysis_id: string;
  status: AnalysisStatus;
  progress: number;
  message?: string;
  result?: AnalysisResult;
  error?: string;
}

export interface PickedFile {
  uri: string;
  name: string;
  mimeType: string;
}
