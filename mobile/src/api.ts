import Constants from 'expo-constants';

import {
  AnalysisStatusResponse,
  PickedFile,
  UploadResponse,
} from './types';

const DEFAULT_BACKEND_PORT = 8000;

/**
 * Resolve the backend base URL.
 *
 * Priority:
 *   1. `EXPO_PUBLIC_API_URL` env var (set this to reach a backend on another host,
 *      e.g. a tunnel: `EXPO_PUBLIC_API_URL=https://abc.trycloudflare.com`).
 *   2. The host serving the Expo bundle - in Expo Go on the same Wi-Fi this is the
 *      dev machine, which is almost always where the backend runs too, so the app
 *      works with zero configuration as long as the backend listens on 0.0.0.0:8000.
 */
function resolveBaseUrl(): string {
  const override = process.env.EXPO_PUBLIC_API_URL;
  if (override) {
    return override.replace(/\/+$/, '');
  }

  const hostUri =
    Constants.expoConfig?.hostUri ??
    // Older field name still present in some Expo Go builds.
    (Constants as unknown as { expoGoConfig?: { debuggerHost?: string } }).expoGoConfig
      ?.debuggerHost;

  if (hostUri) {
    const host = hostUri.split(':')[0];
    return `http://${host}:${DEFAULT_BACKEND_PORT}`;
  }

  return '';
}

export const API_BASE_URL = resolveBaseUrl();

/** Pull a useful message out of a failed response (FastAPI puts it in `detail`). */
async function errorFromResponse(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (body && typeof body.detail === 'string') {
      return body.detail;
    }
  } catch {
    // Non-JSON body; fall through to the status text.
  }
  return `Request failed (${res.status})`;
}

export async function uploadFiling(file: PickedFile): Promise<UploadResponse> {
  const form = new FormData();
  // React Native's fetch accepts this {uri, name, type} shape for multipart files.
  form.append('file', {
    uri: file.uri,
    name: file.name,
    type: file.mimeType,
  } as unknown as Blob);

  const res = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    throw new Error(await errorFromResponse(res));
  }
  return res.json();
}

export async function startAnalysis(
  analysisId: string,
  customPrompt?: string
): Promise<{ analysis_id: string; message: string; status: string }> {
  const form = new FormData();
  form.append('analysis_id', analysisId);
  if (customPrompt) {
    form.append('custom_prompt', customPrompt);
  }

  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    throw new Error(await errorFromResponse(res));
  }
  return res.json();
}

export async function getStatus(analysisId: string): Promise<AnalysisStatusResponse> {
  const res = await fetch(`${API_BASE_URL}/api/status/${analysisId}`);
  if (!res.ok) {
    throw new Error(await errorFromResponse(res));
  }
  return res.json();
}

export function reportUrl(analysisId: string): string {
  return `${API_BASE_URL}/api/report/${analysisId}`;
}
