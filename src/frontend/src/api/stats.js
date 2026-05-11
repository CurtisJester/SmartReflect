// API helpers for the /stats/* dashboard endpoints.

const API_BASE = 'http://localhost:8000';

async function getJson(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const getSummary = () => getJson('/stats/summary');

export const getScreenTimeHistogram = (bins = 10) =>
  getJson(`/stats/screen_time_histogram?bins=${bins}`);

export const getAddictionBreakdown = () => getJson('/stats/addiction_breakdown');

export const getScatterSample = (n = 500) =>
  getJson(`/stats/scatter_sample?n=${n}`);
