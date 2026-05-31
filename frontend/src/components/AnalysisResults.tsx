import React from 'react';
import { AnalysisResult } from '../types/analysis';

interface AnalysisResultsProps {
  result: AnalysisResult;
  onDownloadReport: () => void;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  result,
  onDownloadReport,
}) => {
  const formatPercent = (value?: number) => {
    if (value === undefined || value === null) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatCurrency = (value?: number) => {
    if (value === undefined || value === null) return 'N/A';
    return `$${value.toFixed(0)}M`;
  };

  const formatNumber = (value?: number, decimals: number = 1) => {
    if (value === undefined || value === null) return 'N/A';
    return value.toFixed(decimals);
  };

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'Strong Buy':
        return '#00B050';
      case 'Buy':
        return '#92D050';
      case 'Hold':
        return '#FFC000';
      case 'Avoid':
        return '#FF0000';
      default:
        return '#666';
    }
  };

  const metrics = result.financial_metrics;
  const risks = result.risk_indicators;
  const score = result.trade_score;

  return (
    <div className="analysis-results">
      <div className="results-header">
        <div className="company-info">
          <h2>
            {result.company_name} ({result.ticker})
          </h2>
          <p>
            {result.sector} • FY {result.fiscal_year}
          </p>
        </div>
        <button className="download-btn" onClick={onDownloadReport}>
          📊 Download Excel Report
        </button>
      </div>

      {/* Trade Score */}
      <div className="score-card">
        <h3>Trade Score</h3>
        <div className="score-display">
          <div className="total-score">
            <div className="score-value">{score.total_score.toFixed(1)}</div>
            <div className="score-max">/100</div>
          </div>
          <div
            className="rating-badge"
            style={{ backgroundColor: getRatingColor(score.rating) }}
          >
            {score.rating}
          </div>
        </div>
        <div className="score-breakdown">
          <div className="score-item">
            <span className="score-label">Catalyst & Trend</span>
            <span className="score-bar">
              <span
                className="score-fill"
                style={{ width: `${(score.catalyst_trend_score / 40) * 100}%` }}
              />
            </span>
            <span className="score-number">
              {score.catalyst_trend_score.toFixed(1)}/40
            </span>
          </div>
          <div className="score-item">
            <span className="score-label">Quality & Cash</span>
            <span className="score-bar">
              <span
                className="score-fill"
                style={{ width: `${(score.quality_cash_score / 35) * 100}%` }}
              />
            </span>
            <span className="score-number">
              {score.quality_cash_score.toFixed(1)}/35
            </span>
          </div>
          <div className="score-item">
            <span className="score-label">Risk</span>
            <span className="score-bar">
              <span
                className="score-fill"
                style={{ width: `${(score.risk_score / 25) * 100}%` }}
              />
            </span>
            <span className="score-number">
              {score.risk_score.toFixed(1)}/25
            </span>
          </div>
        </div>
      </div>

      {/* Key Takeaways */}
      <div className="section">
        <h3>Key Takeaways</h3>
        <ul className="takeaways-list">
          {result.key_takeaways.map((takeaway, idx) => (
            <li key={idx}>{takeaway}</li>
          ))}
        </ul>
      </div>

      {/* Financial Metrics */}
      <div className="section">
        <h3>Financial Metrics</h3>
        <div className="metrics-grid">
          <div className="metric">
            <label>Revenue</label>
            <div className="value">{formatCurrency(metrics.revenue)}</div>
          </div>
          <div className="metric">
            <label>Organic Growth</label>
            <div className="value">{formatPercent(metrics.organic_growth)}</div>
          </div>
          <div className="metric">
            <label>Gross Margin</label>
            <div className="value">{formatPercent(metrics.gross_margin)}</div>
          </div>
          <div className="metric">
            <label>Operating Margin</label>
            <div className="value">{formatPercent(metrics.operating_margin)}</div>
          </div>
          <div className="metric">
            <label>FCF</label>
            <div className="value">{formatCurrency(metrics.fcf)}</div>
          </div>
          <div className="metric">
            <label>FCF/NI Ratio</label>
            <div className="value">{formatNumber(metrics.fcf_to_ni, 2)}</div>
          </div>
          <div className="metric">
            <label>DSO</label>
            <div className="value">{formatNumber(metrics.dso, 0)} days</div>
          </div>
          <div className="metric">
            <label>Cash Conversion Cycle</label>
            <div className="value">{formatNumber(metrics.ccc, 0)} days</div>
          </div>
          <div className="metric">
            <label>Net Debt</label>
            <div className="value">{formatCurrency(metrics.net_debt)}</div>
          </div>
          <div className="metric">
            <label>Debt/EBITDA</label>
            <div className="value">{formatNumber(metrics.debt_to_ebitda)}x</div>
          </div>
          <div className="metric">
            <label>SBC % Revenue</label>
            <div className="value">{formatPercent(metrics.sbc_pct_revenue)}</div>
          </div>
          <div className="metric">
            <label>Shareholder Yield</label>
            <div className="value">{formatPercent(metrics.shareholder_yield)}</div>
          </div>
        </div>
      </div>

      {/* Risk Indicators */}
      {risks.red_flags && risks.red_flags.length > 0 && (
        <div className="section risk-section">
          <h3>⚠️ Red Flags</h3>
          <ul className="red-flags-list">
            {risks.red_flags.map((flag, idx) => (
              <li key={idx}>{flag}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Catalysts */}
      {result.catalyst_info?.catalysts && result.catalyst_info.catalysts.length > 0 && (
        <div className="section">
          <h3>📈 Catalysts</h3>
          <ul className="catalysts-list">
            {result.catalyst_info.catalysts.map((catalyst, idx) => (
              <li key={idx}>{catalyst}</li>
            ))}
          </ul>
        </div>
      )}

      {/* AI Insights */}
      <div className="section">
        <h3>AI Analysis</h3>
        <div className="insights-text">{result.ai_insights}</div>
      </div>
    </div>
  );
};

export default AnalysisResults;
