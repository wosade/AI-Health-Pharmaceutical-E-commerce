import api from './index.js'

export function analyticsSummary() {
  return api.get('/api/analytics/summary')
}

export function analyticsCharts() {
  return api.get('/api/analytics/charts')
}

export function adminChat(question) {
  return api.post('/api/agent/admin/chat', { question })
}

export function clientChat(question) {
  return api.post('/api/agent/client/chat', { question })
}