import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AnalysisResult } from '../types';

const RATING_COLORS: Record<string, string> = {
  'Strong Buy': '#00B050',
  Buy: '#92D050',
  Hold: '#FFC000',
  Avoid: '#FF0000',
};

function ratingColor(rating: string): string {
  return RATING_COLORS[rating] ?? '#666';
}

function formatPercent(value?: number): string {
  if (value === undefined || value === null) return 'N/A';
  return `${(value * 100).toFixed(1)}%`;
}

function formatCurrency(value?: number): string {
  if (value === undefined || value === null) return 'N/A';
  return `$${value.toFixed(0)}M`;
}

function formatNumber(value: number | undefined, decimals = 1, suffix = ''): string {
  if (value === undefined || value === null) return 'N/A';
  return `${value.toFixed(decimals)}${suffix}`;
}

function ScoreBar({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <View style={styles.scoreRow}>
      <Text style={styles.scoreLabel}>{label}</Text>
      <View style={styles.scoreTrack}>
        <View style={[styles.scoreFill, { width: `${pct}%` }]} />
      </View>
      <Text style={styles.scoreNumber}>
        {value.toFixed(1)}/{max}
      </Text>
    </View>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.metric}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );
}

export default function AnalysisResults({ result }: { result: AnalysisResult }) {
  const { financial_metrics: m, risk_indicators: risks, trade_score: score } = result;
  const catalysts = result.catalyst_info?.catalysts ?? [];

  return (
    <View>
      <View style={styles.header}>
        <Text style={styles.company}>
          {result.company_name} ({result.ticker})
        </Text>
        <Text style={styles.subhead}>
          {result.sector}
          {result.fiscal_year ? ` • FY ${result.fiscal_year}` : ''}
        </Text>
      </View>

      {/* Trade score */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Trade Score</Text>
        <View style={styles.scoreHeader}>
          <View style={styles.totalScore}>
            <Text style={styles.totalScoreValue}>{score.total_score.toFixed(1)}</Text>
            <Text style={styles.totalScoreMax}>/100</Text>
          </View>
          <View style={[styles.ratingBadge, { backgroundColor: ratingColor(score.rating) }]}>
            <Text style={styles.ratingText}>{score.rating}</Text>
          </View>
        </View>
        <ScoreBar label="Catalyst & Trend" value={score.catalyst_trend_score} max={40} />
        <ScoreBar label="Quality & Cash" value={score.quality_cash_score} max={35} />
        <ScoreBar label="Risk" value={score.risk_score} max={25} />
      </View>

      {/* Key takeaways */}
      {result.key_takeaways.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Key Takeaways</Text>
          {result.key_takeaways.map((t, i) => (
            <Text key={i} style={styles.bullet}>
              • {t}
            </Text>
          ))}
        </View>
      )}

      {/* Financial metrics */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Financial Metrics</Text>
        <View style={styles.metricsGrid}>
          <Metric label="Revenue" value={formatCurrency(m.revenue)} />
          <Metric label="Organic Growth" value={formatPercent(m.organic_growth)} />
          <Metric label="Gross Margin" value={formatPercent(m.gross_margin)} />
          <Metric label="Operating Margin" value={formatPercent(m.operating_margin)} />
          <Metric label="FCF" value={formatCurrency(m.fcf)} />
          <Metric label="FCF/NI" value={formatNumber(m.fcf_to_ni, 2)} />
          <Metric label="DSO" value={formatNumber(m.dso, 0, ' days')} />
          <Metric label="Cash Conv. Cycle" value={formatNumber(m.ccc, 0, ' days')} />
          <Metric label="Net Debt" value={formatCurrency(m.net_debt)} />
          <Metric label="Debt/EBITDA" value={formatNumber(m.debt_to_ebitda, 1, 'x')} />
          <Metric label="SBC % Revenue" value={formatPercent(m.sbc_pct_revenue)} />
          <Metric label="Shareholder Yield" value={formatPercent(m.shareholder_yield)} />
        </View>
      </View>

      {/* Red flags */}
      {risks.red_flags.length > 0 && (
        <View style={[styles.card, styles.riskCard]}>
          <Text style={styles.cardTitle}>⚠️ Red Flags</Text>
          {risks.red_flags.map((flag, i) => (
            <Text key={i} style={styles.bullet}>
              • {flag}
            </Text>
          ))}
        </View>
      )}

      {/* Catalysts */}
      {catalysts.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>📈 Catalysts</Text>
          {catalysts.map((c, i) => (
            <Text key={i} style={styles.bullet}>
              • {c}
            </Text>
          ))}
        </View>
      )}

      {/* AI insights */}
      {!!result.ai_insights && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>AI Analysis</Text>
          <Text style={styles.insights}>{result.ai_insights}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  header: { marginBottom: 12 },
  company: { fontSize: 22, fontWeight: '700', color: '#1a2233' },
  subhead: { fontSize: 14, color: '#667085', marginTop: 2 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e6e9ef',
  },
  riskCard: { borderColor: '#f5c2c2', backgroundColor: '#fff7f7' },
  cardTitle: { fontSize: 16, fontWeight: '700', color: '#1a2233', marginBottom: 12 },
  scoreHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  totalScore: { flexDirection: 'row', alignItems: 'baseline' },
  totalScoreValue: { fontSize: 40, fontWeight: '800', color: '#1a2233' },
  totalScoreMax: { fontSize: 18, color: '#98a2b3', marginLeft: 2 },
  ratingBadge: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 999 },
  ratingText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  scoreRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  scoreLabel: { width: 110, fontSize: 13, color: '#475467' },
  scoreTrack: {
    flex: 1,
    height: 8,
    backgroundColor: '#eef1f6',
    borderRadius: 999,
    overflow: 'hidden',
    marginHorizontal: 8,
  },
  scoreFill: { height: 8, backgroundColor: '#2e6df6', borderRadius: 999 },
  scoreNumber: { width: 56, fontSize: 12, color: '#475467', textAlign: 'right' },
  bullet: { fontSize: 14, color: '#344054', lineHeight: 21, marginBottom: 6 },
  metricsGrid: { flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -6 },
  metric: {
    width: '50%',
    paddingHorizontal: 6,
    marginBottom: 14,
  },
  metricLabel: { fontSize: 12, color: '#667085', marginBottom: 2 },
  metricValue: { fontSize: 16, fontWeight: '600', color: '#1a2233' },
  insights: { fontSize: 14, color: '#344054', lineHeight: 22 },
});
