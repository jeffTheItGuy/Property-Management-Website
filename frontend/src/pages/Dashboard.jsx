import { useEffect, useState } from 'react'
import api from '../api/client'
import { fmtCurrency } from '../utils/formatters'

export default function Dashboard() {
  const [stats, setStats] = useState({ properties: 0, occupied: 0, overdue: 0, maintenance: 0 })
  const [recent, setRecent] = useState([])

  useEffect(() => {
    api.get('/properties/').then(r => {
      const props = r.data
      const units = props.flatMap(p => p.units || [])
      setStats({
        properties: props.length,
        occupied: units.filter(u => u.status === 'OCCUPIED').length,
        overdue: 0,
        maintenance: 0
      })
    })
    api.get('/payments/schedules/?overdue=true').then(r => setStats(s => ({ ...s, overdue: r.data.length })))
    api.get('/maintenance/requests/?status=OPEN').then(r => setStats(s => ({ ...s, maintenance: r.data.length })))
    api.get('/payments/').then(r => setRecent(r.data.slice(0, 5)))
  }, [])

  const cards = [
    { label: 'Properties', value: stats.properties },
    { label: 'Occupied Units', value: stats.occupied },
    { label: 'Overdue Payments', value: stats.overdue, danger: true },
    { label: 'Open Maintenance', value: stats.maintenance, warn: true },
  ]

  return (
    <div>
      <h1 className="page-title">Dashboard</h1>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {cards.map(c => (
          <div key={c.label} className={`card ${c.danger ? 'border-l-4 border-red-500' : c.warn ? 'border-l-4 border-amber-500' : ''}`}>
            <div className="text-gray-500 text-sm">{c.label}</div>
            <div className="text-2xl font-bold">{c.value}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <h2 className="font-semibold mb-3">Recent Payments</h2>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left"><tr><th className="px-3 py-2">Receipt</th><th className="px-3 py-2">Amount</th><th className="px-3 py-2">Date</th></tr></thead>
          <tbody className="divide-y">
            {recent.map(p => (
              <tr key={p.payment_id} className="hover:bg-gray-50">
                <td className="px-3 py-2">{p.receipt_number}</td>
                <td className="px-3 py-2">{fmtCurrency(p.amount_paid, p.currency_code)}</td>
                <td className="px-3 py-2">{new Date(p.payment_date).toLocaleDateString()}</td>
              </tr>
            ))}
            {recent.length === 0 && <tr><td colSpan={3} className="px-3 py-4 text-center text-gray-500">No recent payments</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}