import { useEffect, useState } from 'react'
import { fetchMetrics } from '../utils/api'

export default function MetricsDashboard() {
  const [m, setM] = useState({ total_requests: 0, average_latency_ms: 0, task_completion_rate: 0 })
  const load = async () => {
    try { setM(await fetchMetrics()) } catch (e) { /* ignore */ }
  }
  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t) }, [])
  return (
    <div className="border rounded p-3 bg-white">
      <div className="font-semibold mb-2">Metrics</div>
      <div className="text-sm">Total requests: {m.total_requests}</div>
      <div className="text-sm">Average latency: {m.average_latency_ms} ms</div>
      <div className="text-sm">Task completion rate: {(Number(m.task_completion_rate||0)*100).toFixed(1)}%</div>
    </div>
  )
}
