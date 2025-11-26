export default function ResponseBox({ response }) {
  if (!response) return null
  const { reply, citations, confidence } = response
  return (
    <div className="space-y-2">
      <div className="text-sm text-gray-700">Confidence: {(Number(confidence||0)*100).toFixed(1)}%</div>
      <pre className="whitespace-pre-wrap bg-white border rounded p-3 text-sm">{reply}</pre>
      {citations && citations.length>0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {citations.map((c, i) => (
            <div key={i} className="text-xs text-gray-600 border rounded p-2">
              <div className="font-semibold">{c.source}</div>
              <div className="line-clamp-2">{c.snippet}</div>
              <div>score: {Number(c.score || 0).toFixed(3)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
