const API_BASE = import.meta.env.VITE_API_BASE || '/api';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  health: () => request('/health'),
  movement: () => request('/movement'),
  features: () => request('/features'),
  baseline: () => request('/baseline'),
  insight: () => request('/insight'),
  history: (limit = 30) => request(`/history?limit=${limit}`),
  sensor: (sample) => request('/sensor', { method: 'POST', body: JSON.stringify(sample) }),
  session: (payload = {}) => request('/session', { method: 'POST', body: JSON.stringify(payload) }),
};
