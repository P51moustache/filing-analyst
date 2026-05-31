import React, { useState, useEffect } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import AnalysisResults from './components/AnalysisResults';
import { analysisApi } from './services/api';
import {
  AnalysisStatus,
  AnalysisStatusResponse,
} from './types/analysis';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [customPrompt, setCustomPrompt] = useState('');
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [status, setStatus] = useState<AnalysisStatusResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Poll for status updates
  useEffect(() => {
    if (!analysisId) return;

    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await analysisApi.getStatus(analysisId);
        setStatus(statusResponse);

        // Stop polling if completed or failed
        if (
          statusResponse.status === AnalysisStatus.COMPLETED ||
          statusResponse.status === AnalysisStatus.FAILED
        ) {
          clearInterval(pollInterval);
        }
      } catch (err: any) {
        console.error('Error polling status:', err);
        setError(err.message);
        clearInterval(pollInterval);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [analysisId]);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setError(null);

    try {
      // Upload file
      const uploadResponse = await analysisApi.upload10K(selectedFile);
      setAnalysisId(uploadResponse.analysis_id);

      // Start analysis
      await analysisApi.startAnalysis(
        uploadResponse.analysis_id,
        customPrompt || undefined
      );

      setIsUploading(false);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || err.message);
      setIsUploading(false);
    }
  };

  const handleDownloadReport = () => {
    if (!analysisId) return;
    window.open(analysisApi.downloadReport(analysisId), '_blank');
  };

  const handleReset = () => {
    setSelectedFile(null);
    setCustomPrompt('');
    setAnalysisId(null);
    setStatus(null);
    setError(null);
  };

  const isAnalyzing =
    status?.status === AnalysisStatus.PROCESSING ||
    status?.status === AnalysisStatus.PENDING;

  return (
    <div className="App">
      <header className="App-header">
        <h1>📊 10-K Analysis Platform</h1>
        <p>AI-Powered Financial Analysis for Swing Traders</p>
      </header>

      <main className="App-main">
        {!analysisId && (
          <div className="upload-section">
            <FileUpload
              onFileSelect={handleFileSelect}
              disabled={isUploading}
            />

            <div className="prompt-section">
              <label htmlFor="custom-prompt">
                Custom Analysis Focus (Optional)
              </label>
              <textarea
                id="custom-prompt"
                placeholder="E.g., Focus on semiconductor capacity expansion and export controls..."
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                disabled={isUploading}
                rows={4}
              />
            </div>

            <button
              className="analyze-btn"
              onClick={handleAnalyze}
              disabled={!selectedFile || isUploading}
            >
              {isUploading ? 'Uploading...' : 'Analyze 10-K'}
            </button>

            {error && <div className="error-message">{error}</div>}
          </div>
        )}

        {isAnalyzing && status && (
          <div className="analyzing-section">
            <div className="spinner" />
            <h2>Analyzing Document...</h2>
            <p>{status.message}</p>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${status.progress}%` }}
              />
            </div>
            <div className="progress-text">{status.progress}%</div>
          </div>
        )}

        {status?.status === AnalysisStatus.COMPLETED && status.result && (
          <>
            <AnalysisResults
              result={status.result}
              onDownloadReport={handleDownloadReport}
            />
            <button className="reset-btn" onClick={handleReset}>
              ← Analyze Another 10-K
            </button>
          </>
        )}

        {status?.status === AnalysisStatus.FAILED && (
          <div className="error-section">
            <h2>Analysis Failed</h2>
            <p>{status.error || 'An unknown error occurred'}</p>
            <button className="reset-btn" onClick={handleReset}>
              Try Again
            </button>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>
          Powered by Claude AI • Analyzes Business, MD&A, Risks, Financials &
          More
        </p>
      </footer>
    </div>
  );
}

export default App;
