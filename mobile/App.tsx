import { StatusBar } from 'expo-status-bar';
import * as DocumentPicker from 'expo-document-picker';
import * as WebBrowser from 'expo-web-browser';
import React, { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StatusBar as RNStatusBar,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import AnalysisResults from './src/components/AnalysisResults';
import {
  API_BASE_URL,
  getStatus,
  reportUrl,
  startAnalysis,
  uploadFiling,
} from './src/api';
import {
  AnalysisStatus,
  AnalysisStatusResponse,
  PickedFile,
} from './src/types';

const ACCEPTED_TYPES = ['application/pdf', 'text/html', 'text/plain'];
const POLL_INTERVAL_MS = 2000;
const MAX_CONSECUTIVE_ERRORS = 3;

export default function App() {
  const [file, setFile] = useState<PickedFile | null>(null);
  const [customPrompt, setCustomPrompt] = useState('');
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [status, setStatus] = useState<AnalysisStatusResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Avoid a state update after the screen is reset/unmounted mid-poll.
  const cancelled = useRef(false);

  useEffect(() => {
    return () => {
      cancelled.current = true;
    };
  }, []);

  // Poll for status once an analysis is running, tolerating transient failures.
  useEffect(() => {
    if (!analysisId) return;

    let consecutiveErrors = 0;
    const interval = setInterval(async () => {
      try {
        const next = await getStatus(analysisId);
        consecutiveErrors = 0;
        if (cancelled.current) return;
        setStatus(next);
        if (
          next.status === AnalysisStatus.COMPLETED ||
          next.status === AnalysisStatus.FAILED
        ) {
          clearInterval(interval);
        }
      } catch (err) {
        consecutiveErrors += 1;
        if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS && !cancelled.current) {
          setError(err instanceof Error ? err.message : 'Lost connection to the server');
          clearInterval(interval);
        }
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [analysisId]);

  const pickFile = async () => {
    const result = await DocumentPicker.getDocumentAsync({
      type: ACCEPTED_TYPES,
      copyToCacheDirectory: true,
    });
    if (result.canceled || result.assets.length === 0) return;
    const asset = result.assets[0];
    setFile({
      uri: asset.uri,
      name: asset.name,
      mimeType: asset.mimeType ?? 'application/octet-stream',
    });
    setError(null);
  };

  const analyze = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);
    try {
      const uploaded = await uploadFiling(file);
      await startAnalysis(uploaded.analysis_id, customPrompt.trim() || undefined);
      cancelled.current = false;
      setAnalysisId(uploaded.analysis_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const openReport = () => {
    if (analysisId) {
      WebBrowser.openBrowserAsync(reportUrl(analysisId));
    }
  };

  const reset = () => {
    cancelled.current = true;
    setFile(null);
    setCustomPrompt('');
    setAnalysisId(null);
    setStatus(null);
    setError(null);
  };

  const isAnalyzing =
    status?.status === AnalysisStatus.PROCESSING ||
    status?.status === AnalysisStatus.PENDING ||
    (!!analysisId && !status);
  const isDone = status?.status === AnalysisStatus.COMPLETED && !!status.result;
  const isFailed = status?.status === AnalysisStatus.FAILED || (!analysisId && !!error);

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="light" />
      <View style={styles.appHeader}>
        <Text style={styles.appTitle}>📊 Filing Analyst</Text>
        <Text style={styles.appSubtitle}>AI-powered 10-K analysis</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        {!API_BASE_URL && (
          <View style={[styles.banner, styles.bannerWarn]}>
            <Text style={styles.bannerText}>
              Could not detect the backend host. Set EXPO_PUBLIC_API_URL to your
              machine's address, e.g. http://192.168.1.20:8000
            </Text>
          </View>
        )}

        {/* Upload screen */}
        {!analysisId && !isFailed && (
          <View>
            <Pressable
              style={({ pressed }) => [styles.dropzone, pressed && styles.pressed]}
              onPress={pickFile}
              disabled={isUploading}
            >
              <Text style={styles.dropIcon}>{file ? '📄' : '📤'}</Text>
              {file ? (
                <Text style={styles.fileName}>{file.name}</Text>
              ) : (
                <>
                  <Text style={styles.dropTitle}>Choose a 10-K file</Text>
                  <Text style={styles.dropHint}>PDF, HTML, or TXT</Text>
                </>
              )}
            </Pressable>

            <Text style={styles.label}>Custom analysis focus (optional)</Text>
            <TextInput
              style={styles.input}
              placeholder="E.g. focus on semiconductor capacity and export controls…"
              placeholderTextColor="#98a2b3"
              value={customPrompt}
              onChangeText={setCustomPrompt}
              editable={!isUploading}
              multiline
            />

            <Pressable
              style={({ pressed }) => [
                styles.primaryBtn,
                (!file || isUploading) && styles.btnDisabled,
                pressed && styles.pressed,
              ]}
              onPress={analyze}
              disabled={!file || isUploading}
            >
              {isUploading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.primaryBtnText}>Analyze 10-K</Text>
              )}
            </Pressable>

            {!!error && <Text style={styles.errorText}>{error}</Text>}
          </View>
        )}

        {/* Analyzing screen */}
        {isAnalyzing && (
          <View style={styles.centered}>
            <ActivityIndicator size="large" color="#2e6df6" />
            <Text style={styles.analyzingTitle}>Analyzing…</Text>
            <Text style={styles.analyzingMsg}>{status?.message ?? 'Starting up'}</Text>
            <View style={styles.progressTrack}>
              <View style={[styles.progressFill, { width: `${status?.progress ?? 0}%` }]} />
            </View>
            <Text style={styles.progressText}>{status?.progress ?? 0}%</Text>
          </View>
        )}

        {/* Results screen */}
        {isDone && status?.result && (
          <View>
            <AnalysisResults result={status.result} />
            <Pressable
              style={({ pressed }) => [styles.primaryBtn, pressed && styles.pressed]}
              onPress={openReport}
            >
              <Text style={styles.primaryBtnText}>📊 Open Excel Report</Text>
            </Pressable>
            <Pressable
              style={({ pressed }) => [styles.secondaryBtn, pressed && styles.pressed]}
              onPress={reset}
            >
              <Text style={styles.secondaryBtnText}>← Analyze another 10-K</Text>
            </Pressable>
          </View>
        )}

        {/* Failure screen */}
        {isFailed && (
          <View style={styles.centered}>
            <Text style={styles.failTitle}>Analysis failed</Text>
            <Text style={styles.failMsg}>{status?.error ?? error ?? 'Unknown error'}</Text>
            <Pressable
              style={({ pressed }) => [styles.secondaryBtn, pressed && styles.pressed]}
              onPress={reset}
            >
              <Text style={styles.secondaryBtnText}>Try again</Text>
            </Pressable>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: '#f4f6fa',
    paddingTop: Platform.OS === 'android' ? RNStatusBar.currentHeight : 0,
  },
  appHeader: { backgroundColor: '#1a2233', paddingVertical: 18, paddingHorizontal: 20 },
  appTitle: { color: '#fff', fontSize: 22, fontWeight: '800' },
  appSubtitle: { color: '#aab4c5', fontSize: 13, marginTop: 2 },
  scroll: { padding: 16, paddingBottom: 48 },
  banner: { borderRadius: 10, padding: 12, marginBottom: 14 },
  bannerWarn: { backgroundColor: '#fff4e5', borderWidth: 1, borderColor: '#ffd9a0' },
  bannerText: { color: '#8a5a00', fontSize: 13, lineHeight: 19 },
  dropzone: {
    backgroundColor: '#fff',
    borderRadius: 14,
    borderWidth: 2,
    borderColor: '#cdd7e6',
    borderStyle: 'dashed',
    paddingVertical: 36,
    alignItems: 'center',
    marginBottom: 18,
  },
  dropIcon: { fontSize: 38, marginBottom: 8 },
  dropTitle: { fontSize: 17, fontWeight: '600', color: '#1a2233' },
  dropHint: { fontSize: 13, color: '#667085', marginTop: 4 },
  fileName: { fontSize: 15, fontWeight: '600', color: '#1a2233', paddingHorizontal: 16, textAlign: 'center' },
  label: { fontSize: 13, fontWeight: '600', color: '#475467', marginBottom: 8 },
  input: {
    backgroundColor: '#fff',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e6e9ef',
    padding: 12,
    minHeight: 84,
    textAlignVertical: 'top',
    fontSize: 14,
    color: '#1a2233',
    marginBottom: 18,
  },
  primaryBtn: {
    backgroundColor: '#2e6df6',
    borderRadius: 10,
    paddingVertical: 15,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  btnDisabled: { backgroundColor: '#aac1f7' },
  secondaryBtn: { paddingVertical: 14, alignItems: 'center' },
  secondaryBtnText: { color: '#2e6df6', fontSize: 15, fontWeight: '600' },
  pressed: { opacity: 0.85 },
  centered: { alignItems: 'center', paddingVertical: 40 },
  analyzingTitle: { fontSize: 20, fontWeight: '700', color: '#1a2233', marginTop: 18 },
  analyzingMsg: { fontSize: 14, color: '#667085', marginTop: 6 },
  progressTrack: {
    width: '100%',
    height: 8,
    backgroundColor: '#e6eaf1',
    borderRadius: 999,
    overflow: 'hidden',
    marginTop: 18,
  },
  progressFill: { height: 8, backgroundColor: '#2e6df6' },
  progressText: { fontSize: 13, color: '#475467', marginTop: 8 },
  errorText: { color: '#c0392b', fontSize: 14, marginTop: 4, textAlign: 'center' },
  failTitle: { fontSize: 20, fontWeight: '700', color: '#c0392b' },
  failMsg: { fontSize: 14, color: '#667085', marginTop: 8, textAlign: 'center' },
});
