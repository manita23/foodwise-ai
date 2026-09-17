const BASE = '/api/v1'

async function get(path) {
  const r = await fetch(`${BASE}${path}`)
  if (!r.ok) throw new Error(`GET ${path} → ${r.status}`)
  return r.json()
}

async function post(path, body) {
  const r = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(`POST ${path} → ${r.status}`)
  return r.json()
}

export const api = {
  health: ()                      => get('/health'.replace('/api/v1', '')),
  forecast: (body)                => post('/forecast', body),
  qa: (question)                  => post('/qa', { question }),
  listWaste: (days = 30)          => get(`/waste?days=${days}`),
  recordWaste: (body)             => post('/waste', body),
  trends: (days = 7)              => get(`/waste/trends?days=${days}`),
  listMeals: ()                   => get('/meals'),
  createMeal: (body)              => post('/meals', body),
  importCSV: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return fetch(`${BASE}/meals/import`, { method: 'POST', body: fd }).then(r => r.json())
  },
  listRecommendations: (status)   => get(`/recommendations${status ? `?status=${status}` : ''}`),
  approve: (id, reviewed_by)      => post(`/recommendations/${id}/approve`, { reviewed_by }),
  reject:  (id, reviewed_by)      => post(`/recommendations/${id}/reject`,  { reviewed_by }),
}
