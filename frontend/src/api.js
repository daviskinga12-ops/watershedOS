const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }
  return res.json()
}

export const api = {
  getWatersheds: () => request('/watersheds'),
  getScores: (id) => request(`/watersheds/${id}/scores`),
  getLatestScore: (id) => request(`/watersheds/${id}/health-score`),
  getAlerts: () => request('/alerts'),
  subscribeAlerts: (body) => request('/alerts/subscribe', { method: 'POST', body: JSON.stringify(body) }),
  createRestoration: (body) => request('/restoration', { method: 'POST', body: JSON.stringify(body) }),
  estimateCarbon: (body) => request('/carbon/estimate', { method: 'POST', body: JSON.stringify(body) }),
}
