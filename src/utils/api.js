/** API Client — communicates with FastAPI backend */
import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' }
});

export async function runEngagement(params) {
  const resp = await api.post('/run-engagement', params);
  return resp.data;
}

export async function computeNez(params = {}) {
  const resp = await api.get('/compute-nez', { params });
  return resp.data;
}

export async function getScenarios() {
  const resp = await api.get('/scenarios');
  return resp.data;
}

export function createTelemetryStream(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return new EventSource(`${API_BASE}/telemetry/stream?${qs}`);
}

export async function healthCheck() {
  const resp = await api.get('/health');
  return resp.data;
}

export default api;
