export enum AnalysisStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
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
  fx_impact?: number;
  ma_impact?: number;
  gross_margin?: number;
  operating_margin?: number;
  fcf?: number;
  fcf_margin?: number;
  fcf_to_ni?: number;
  dso?: number;
  dio?: number;
  dpo?: number;
  ccc?: number;
  net_debt?: number;
  debt_to_ebitda?: number;
  interest_coverage?: number;
  sbc_amount?: number;
  sbc_pct_revenue?: number;
  dilution_pct?: number;
  buybacks?: number;
  dividends?: number;
  shareholder_yield?: number;
  capex?: number;
  deferred_revenue?: number;
  deferred_revenue_yoy?: number;
  accruals_ratio?: number;
}

export interface RiskIndicators {
  material_weakness: boolean;
  new_top_risks: boolean;
  customer_concentration: boolean;
  debt_maturity_24m?: number;
  off_balance_commitments?: number;
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
  catalyst_info?: { catalysts: string[]; catalyst_calendar?: Record<string, string> };
  ai_insights: string;
  key_takeaways: string[];
  excel_report_path?: string;
}

export interface AnalysisStatusResponse {
  analysis_id: string;
  status: AnalysisStatus;
  progress: number;
  message?: string;
  result?: AnalysisResult;
  error?: string;
}
