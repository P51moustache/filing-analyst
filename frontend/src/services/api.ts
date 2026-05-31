import axios from 'axios';
import { UploadResponse, AnalysisStatusResponse } from '../types/analysis';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analysisApi = {
  /**
   * Upload a 10-K document
   */
  upload10K: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<UploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Start analysis of uploaded document
   */
  startAnalysis: async (
    analysisId: string,
    customPrompt?: string
  ): Promise<{ analysis_id: string; message: string; status: string }> => {
    const formData = new FormData();
    formData.append('analysis_id', analysisId);
    if (customPrompt) {
      formData.append('custom_prompt', customPrompt);
    }

    const response = await api.post('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Get analysis status
   */
  getStatus: async (analysisId: string): Promise<AnalysisStatusResponse> => {
    const response = await api.get<AnalysisStatusResponse>(
      `/api/status/${analysisId}`
    );
    return response.data;
  },

  /**
   * Download Excel report
   */
  downloadReport: (analysisId: string): string => {
    return `${API_BASE_URL}/api/report/${analysisId}`;
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string; message: string }> => {
    const response = await api.get('/api/health');
    return response.data;
  },
};

export default api;
