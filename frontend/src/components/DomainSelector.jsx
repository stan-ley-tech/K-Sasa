export default function DomainSelector({ domain, onChange }) {
  const btn = (key, label) => (
    <button
      key={key}
      className={`px-3 py-1 rounded ${domain===key?'bg-blue-600 text-white':'bg-gray-200'}`}
      onClick={()=>onChange(key)}
    >{label}</button>
  )
  return (
    <div className="flex gap-2">
      {btn('education','Education')}
      {btn('health','Health')}
      {btn('governance','Governance')}
    </div>
  )
}
