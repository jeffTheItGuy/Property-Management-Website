import { useEffect, useState } from 'react'
import api from '../api/client'
import DataTable from '../components/DataTable'
import { fmtCurrency } from '../utils/formatters'

export default function Payments() {
  const [payments, setPayments] = useState([])
  const [schedules, setSchedules] = useState([])
  const [tab, setTab] = useState('payments')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    lease_id: '', schedule_id: '', payment_method: 'ECOCASH', currency_code: 'USD',
    amount_paid: '', receipt_number: '', reference_number: '', period_from: '', period_to: ''
  })

  const fetch = () => {
    api.get('/payments/').then(r => setPayments(r.data))
    api.get('/payments/schedules/').then(r => setSchedules(r.data))
  }

  useEffect(() => { fetch() }, [])

  const submit = async (e) => {
    e.preventDefault()
    await api.post('/payments/', { ...form, amount_paid: parseFloat(form.amount_paid) })
    setShowForm(false)
    fetch()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title mb-0">Payments</h1>
        <div className="flex gap-2">
          <button onClick={() => setTab('schedules')} className={`text-sm px-3 py-1 rounded ${tab==='schedules'?'bg-emerald-700 text-white':'bg-gray-200'}`}>Schedules</button>
          <button onClick={() => setTab('payments')} className={`text-sm px-3 py-1 rounded ${tab==='payments'?'bg-emerald-700 text-white':'bg-gray-200'}`}>Payments</button>
          <button onClick={() => setShowForm(true)} className="btn-primary">+ Record Payment</button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <input className="input" placeholder="Lease ID" value={form.lease_id} onChange={e => setForm({...form, lease_id: e.target.value})} required />
          <input className="input" placeholder="Schedule ID (optional)" value={form.schedule_id} onChange={e => setForm({...form, schedule_id: e.target.value})} />
          <select className="input" value={form.payment_method} onChange={e => setForm({...form, payment_method: e.target.value})}>
            <option>CASH</option><option>BANK_TRANSFER</option><option>ECOCASH</option><option>ZIPIT</option><option>ONEMONEY</option><option>INNBUCKS</option>
          </select>
          <input className="input" placeholder="Amount" type="number" value={form.amount_paid} onChange={e => setForm({...form, amount_paid: e.target.value})} required />
          <input className="input" placeholder="Receipt Number" value={form.receipt_number} onChange={e => setForm({...form, receipt_number: e.target.value})} required />
          <input className="input" placeholder="Reference" value={form.reference_number} onChange={e => setForm({...form, reference_number: e.target.value})} />
          <input className="input" type="date" value={form.period_from} onChange={e => setForm({...form, period_from: e.target.value})} required />
          <input className="input" type="date" value={form.period_to} onChange={e => setForm({...form, period_to: e.target.value})} required />
          <div className="md:col-span-3 flex gap-2">
            <button className="btn-primary">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      {tab === 'payments' ? (
        <DataTable
          searchKey="receipt_number"
          columns={[
            { key: 'receipt_number', label: 'Receipt' },
            { key: 'amount_paid', label: 'Amount', format: (v, r) => fmtCurrency(v, r.currency_code) },
            { key: 'payment_method', label: 'Method' },
            { key: 'payment_date', label: 'Date' },
          ]}
          rows={payments.map(p => ({
            ...p,
            _actions: (
              <a href={`/api/v1/payments/${p.payment_id}/receipt`} target="_blank" rel="noreferrer" className="text-emerald-700 hover:underline text-xs">Receipt</a>
            )
          }))}
        />
      ) : (
        <DataTable
          searchKey="status"
          columns={[
            { key: 'due_date', label: 'Due' },
            { key: 'amount_due', label: 'Amount', format: (v, r) => fmtCurrency(v, r.currency_code) },
            { key: 'status', label: 'Status' },
          ]}
          rows={schedules.map(s => ({ ...s, _actions: <span /> }))}
        />
      )}
    </div>
  )
}