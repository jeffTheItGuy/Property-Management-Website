import { useEffect, useState } from 'react'
import api from '../api/client'
import DataTable from '../components/DataTable'
import { fmtCurrency } from '../utils/formatters'

export default function Leases() {
  const [rows, setRows] = useState([])
  const [units, setUnits] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    lease_number: '', unit_id: '', primary_tenant_id: '', start_date: '', end_date: '',
    base_rent: '', deposit_amount: '', payment_due_day: 1, status: 'DRAFT'
  })

  useEffect(() => {
    api.get('/leases/').then(r => setRows(r.data))
    api.get('/units/').then(r => setUnits(r.data))
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    const payload = {
      ...form,
      base_rent: parseFloat(form.base_rent),
      deposit_amount: parseFloat(form.deposit_amount),
      payment_due_day: parseInt(form.payment_due_day),
    }
    await api.post('/leases/', payload)
    setShowForm(false)
    const r = await api.get('/leases/')
    setRows(r.data)
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title mb-0">Leases</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary">+ New Lease</button>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <input className="input" placeholder="Lease Number" value={form.lease_number} onChange={e => setForm({...form, lease_number: e.target.value})} required />
          <select className="input" value={form.unit_id} onChange={e => setForm({...form, unit_id: e.target.value})} required>
            <option value="">Select Unit</option>
            {units.map(u => <option key={u.unit_id} value={u.unit_id}>{u.unit_number} ({u.property?.property_name || 'Property'})</option>)}
          </select>
          <input className="input" placeholder="Tenant ID" value={form.primary_tenant_id} onChange={e => setForm({...form, primary_tenant_id: e.target.value})} required />
          <input className="input" type="date" value={form.start_date} onChange={e => setForm({...form, start_date: e.target.value})} required />
          <input className="input" type="date" value={form.end_date} onChange={e => setForm({...form, end_date: e.target.value})} required />
          <input className="input" placeholder="Base Rent" type="number" value={form.base_rent} onChange={e => setForm({...form, base_rent: e.target.value})} required />
          <input className="input" placeholder="Deposit" type="number" value={form.deposit_amount} onChange={e => setForm({...form, deposit_amount: e.target.value})} required />
          <input className="input" placeholder="Due Day" type="number" value={form.payment_due_day} onChange={e => setForm({...form, payment_due_day: e.target.value})} required />
          <select className="input" value={form.status} onChange={e => setForm({...form, status: e.target.value})}>
            <option>DRAFT</option><option>ACTIVE</option><option>ENDED</option><option>BREACHED</option>
          </select>
          <div className="md:col-span-3 flex gap-2">
            <button className="btn-primary">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      <DataTable
        searchKey="lease_number"
        columns={[
          { key: 'lease_number', label: 'Lease #' },
          { key: 'base_rent', label: 'Rent', format: (v, r) => fmtCurrency(v, r.rent_currency) },
          { key: 'start_date', label: 'Start' },
          { key: 'end_date', label: 'End' },
          { key: 'status', label: 'Status' },
        ]}
        rows={rows.map(r => ({ ...r, _actions: <span /> }))}
      />
    </div>
  )
}