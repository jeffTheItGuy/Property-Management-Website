import { useState } from 'react'

export default function Reports() {
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [year, setYear] = useState(new Date().getFullYear())
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')

  const download = (url, name) => {
    const link = document.createElement('a')
    link.href = url
    link.download = name
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  return (
    <div>
      <h1 className="page-title">Reports</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold mb-3">Monthly Report (Excel)</h2>
          <div className="flex gap-2 items-end">
            <div>
              <label className="block text-xs font-medium mb-1">Year</label>
              <input className="input" type="number" value={year} onChange={e => setYear(e.target.value)} />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Month</label>
              <input className="input" type="number" min={1} max={12} value={month} onChange={e => setMonth(e.target.value)} />
            </div>
            <button onClick={() => download(`/api/v1/reports/monthly?year=${year}&month=${month}`, `report_${year}_${month}.xlsx`)} className="btn-primary">Download</button>
          </div>
        </div>

        <div className="card">
          <h2 className="font-semibold mb-3">Payment Ledger (Excel)</h2>
          <div className="flex gap-2 items-end">
            <div>
              <label className="block text-xs font-medium mb-1">From</label>
              <input className="input" type="date" value={from} onChange={e => setFrom(e.target.value)} />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">To</label>
              <input className="input" type="date" value={to} onChange={e => setTo(e.target.value)} />
            </div>
            <button onClick={() => from && to && download(`/api/v1/reports/payments?from_date=${from}&to_date=${to}`, `ledger_${from}_to_${to}.xlsx`)} className="btn-primary">Download</button>
          </div>
        </div>

        <div className="card md:col-span-2">
          <h2 className="font-semibold mb-3">Property GeoJSON Export</h2>
          <button onClick={() => download('/api/v1/reports/properties/geojson', 'properties_export.geojson')} className="btn-secondary">Export GeoJSON</button>
        </div>
      </div>
    </div>
  )
}