import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/',
  timeout: 60000,
})

export async function agentAsk({ user_id, channel, domain, prompt, context }) {
  const { data } = await api.post('/agent/ask', { user_id, channel, domain, prompt, context })
  return data
}

export async function agentAction({ audit_id, action, payload }) {
  const { data } = await api.post('/agent/action', { audit_id, action, payload })
  return data
}

export async function listPending() {
  const { data } = await api.get('/admin/pending')
  return data.items || []
}

export async function approvePending(pending_id) {
  const { data } = await api.post('/admin/approve', { pending_id })
  return data
}

export async function declinePending(pending_id, reason='') {
  const { data } = await api.post('/admin/decline', { pending_id, reason })
  return data
}

export async function fetchMetrics() {
  const { data } = await api.get('/metrics')
  return data
}

export async function smsInbound({ from_number, text, domain }) {
  const { data } = await api.post('/sms/inbound', { from_number, text, domain })
  return data
}

export default api
