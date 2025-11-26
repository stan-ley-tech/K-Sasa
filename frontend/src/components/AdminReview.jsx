import { useEffect, useState } from 'react'
import { listPending, approvePending, declinePending } from '../utils/api'

export default function AdminReview() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const list = await listPending()
      setItems(list)
    } catch (e) {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t) }, [])

  const approve = async (id) => {
    await approvePending(id)
    load()
  }
  const decline = async (id) => {
    const reason = prompt('Reason for decline (optional)') || ''
    await declinePending(id, reason)
    load()
  }

  return (
    <div className="border rounded p-3 bg-white">
      <div className="font-semibold mb-2">Pending Actions</div>
      {loading && <div className="text-sm text-gray-500">Loading...</div>}
      {(!items || items.length===0) && <div className="text-sm text-gray-500">No pending items</div>}
      <div className="space-y-2">
        {items.map(it => (
          <div key={it.id} className="border rounded p-2">
            <div className="text-sm">ID: {it.id}</div>
            <div className="text-sm">Type: {it.type}</div>
            <div className="text-xs text-gray-600">Payload: {JSON.stringify(it.payload)}</div>
            <div className="mt-2 flex gap-2">
              <button onClick={()=>approve(it.id)} className="px-2 py-1 bg-green-600 text-white rounded">Approve</button>
              <button onClick={()=>decline(it.id)} className="px-2 py-1 bg-red-600 text-white rounded">Decline</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
