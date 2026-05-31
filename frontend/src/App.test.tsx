import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { analysisApi } from './services/api';
import { AnalysisStatus, AnalysisStatusResponse } from './types/analysis';

jest.mock('./services/api', () => ({
  analysisApi: {
    upload10K: jest.fn(),
    startAnalysis: jest.fn(),
    getStatus: jest.fn(),
    downloadReport: jest.fn(() => 'http://localhost/report'),
    healthCheck: jest.fn(),
  },
}));

const mockedApi = analysisApi as jest.Mocked<typeof analysisApi>;

const completedStatus: AnalysisStatusResponse = {
  analysis_id: 'abc',
  status: AnalysisStatus.COMPLETED,
  progress: 100,
  message: 'Analysis complete',
  result: {
    analysis_id: 'abc',
    ticker: 'ACME',
    company_name: 'Acme Corp',
    fiscal_year: 2024,
    sector: 'SaaS',
    financial_metrics: { revenue: 1000, gross_margin: 0.6 },
    risk_indicators: {
      material_weakness: false,
      new_top_risks: false,
      customer_concentration: false,
      red_flags: ['Customer concentration risk'],
    },
    trade_score: {
      total_score: 72.5,
      catalyst_trend_score: 30,
      quality_cash_score: 25,
      risk_score: 17.5,
      rating: 'Buy',
    },
    catalyst_info: { catalysts: ['New product launch'] },
    ai_insights: 'Solid quality compounder.',
    key_takeaways: ['Strong free cash flow', 'Durable growth'],
  },
};

beforeEach(() => {
  jest.clearAllMocks();
});

test('renders the upload screen on first load', () => {
  render(<App />);
  expect(screen.getByText(/10-K Analysis Platform/i)).toBeInTheDocument();
  expect(
    screen.getByRole('button', { name: /Analyze 10-K/i })
  ).toBeDisabled();
});

test('runs the upload -> poll -> results flow', async () => {
  mockedApi.upload10K.mockResolvedValue({
    analysis_id: 'abc',
    filename: 'filing.txt',
    file_size: 5,
    status: AnalysisStatus.PENDING,
  });
  mockedApi.startAnalysis.mockResolvedValue({
    analysis_id: 'abc',
    message: 'Analysis started',
    status: 'processing',
  });
  mockedApi.getStatus.mockResolvedValue(completedStatus);

  const { container } = render(<App />);

  // Select a file via the hidden file input, then start the analysis.
  const fileInput = container.querySelector('#file-input') as HTMLInputElement;
  const file = new File(['filing contents'], 'filing.txt', { type: 'text/plain' });
  await userEvent.upload(fileInput, file);

  const analyzeButton = screen.getByRole('button', { name: /Analyze 10-K/i });
  await waitFor(() => expect(analyzeButton).toBeEnabled());
  await userEvent.click(analyzeButton);

  await waitFor(() => expect(mockedApi.upload10K).toHaveBeenCalledTimes(1));
  expect(mockedApi.startAnalysis).toHaveBeenCalledWith('abc', undefined);

  // The poll picks up the completed status and the results render.
  await waitFor(
    () => expect(screen.getByText(/Acme Corp/i)).toBeInTheDocument(),
    { timeout: 4000 }
  );
  expect(screen.getByText('Buy')).toBeInTheDocument();
  expect(screen.getByText(/Strong free cash flow/i)).toBeInTheDocument();
});

test('shows an error when analysis fails', async () => {
  mockedApi.upload10K.mockResolvedValue({
    analysis_id: 'abc',
    filename: 'filing.txt',
    file_size: 5,
    status: AnalysisStatus.PENDING,
  });
  mockedApi.startAnalysis.mockResolvedValue({
    analysis_id: 'abc',
    message: 'Analysis started',
    status: 'processing',
  });
  mockedApi.getStatus.mockResolvedValue({
    analysis_id: 'abc',
    status: AnalysisStatus.FAILED,
    progress: 0,
    message: 'Analysis failed',
    error: 'Could not parse filing',
  });

  const { container } = render(<App />);
  const fileInput = container.querySelector('#file-input') as HTMLInputElement;
  await userEvent.upload(fileInput, new File(['x'], 'filing.txt', { type: 'text/plain' }));
  await userEvent.click(screen.getByRole('button', { name: /Analyze 10-K/i }));

  await waitFor(
    () => expect(screen.getByText(/Could not parse filing/i)).toBeInTheDocument(),
    { timeout: 4000 }
  );
});
