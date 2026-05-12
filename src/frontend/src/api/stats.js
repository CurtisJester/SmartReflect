// API helpers for the /stats/* dashboard endpoints.

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function getJson(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const getSummary = () => getJson('/stats/summary');

export const getMostAddicted = () => getJson('/stats/most_addicted');

export const getLeastAddicted = () => getJson('/stats/least_addicted');

export const getWeekendMaxxing = () => getJson('/stats/weekend_maxxing');

export const getScreenTimeHistogram = () => getJson('/stats/screen_time_histogram');

export const getAddictionBreakdown = () => getJson('/stats/addiction_breakdown');

export const getAgeBreakdown = () => getJson('/stats/age_breakdown');

export const getScatterSample = (n = 500) =>
  getJson(`/stats/scatter_sample?n=${n}`);

function buildExploreParams(filters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '' && value != null) params.set(key, value);
  });
  return params.toString();
}

export const getExploreRows = (filters = {}) => {
  const query = buildExploreParams(filters);
  return getJson(`/explore${query ? `?${query}` : ''}`);
};

export const getExploreExport = (filters = {}) => {
  const query = buildExploreParams(filters);
  return getJson(`/explore/export${query ? `?${query}` : ''}`);
};
