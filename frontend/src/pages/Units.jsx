import { useEffect, useState } from 'react'
import api from '../api/client'
import DataTable from '../components/DataTable'
import { fmtCurrency } from '../utils/formatters'

export default function Units() {
  const [rows, setRows] = useState([])
  const [properties, setProperties] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ property_id: '', unit_number: '', unit_type: '1_BED', current_rent: '', rent_currency: 'USD', deposit_months: 1 })

  useEffect(() => {
    api.get('/units/').then(r => setRows(r.data))
    api.get('/properties/').then(r => setProperties(r.data))
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    await api.post(`/properties/${form.property_id}/units`, { ...form, current_rent: parseFloat(form.current_rent) })
    setShowForm(false)
    setForm({ property_id: '', unit_number: '', unit_type: '1_BED', current_rent: '', rent_currency: 'USD', deposit_months: 1 })
    const r = await api.get('/units/')
    setRows(r.data)
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title mb-0">Units</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary">+ Add Unit</button>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <select className="input" value={form.property_id} onChange={e => setForm({...form, property_id: e.target.value})} required>
            <option value="">Select Property</option>
            {properties.map(p => <option key={p.property_id} value={p.property_id}>{p.property_name}</option>)}
          </select>
          <input className="input" placeholder="Unit Number" value={form.unit_number} onChange={e => setForm({...form, unit_number: e.target.value})} required />
          <select className="input" value={form.unit_type} onChange={e => setForm({...form, unit_type: e.target.value})}>
            <option>BEDSITTER</option><option>1_BED</option><option>2_BED</option><option>3_BED</option><option>4_BED</option><option>OFFICE</option><option>SHOP</option><option>WAREHOUSE</option>
          </select>
          <input className="input" placeholder="Rent" type="number" value={form.current_rent} onChange={e => setForm({...form, current_rent: e.target.value})} required />
          <input className="input" placeholder="Deposit Months" type="number" value={form.deposit_months} onChange={e => setForm({...form, deposit_months: e.target.value})} required />
          <div className="md:col-span-3 flex gap-2">
            <button className="btn-primary">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      <DataTable
        searchKey="unit_number"
        columns={[
          { key: 'unit_number', label: 'Unit' },
          { key: 'unit_type', label: 'Type' },
          { key: 'current_rent', label: 'Rent', format: (v, r) => fmtCurrency(v, r.rent_currency) },
          { key: 'status', label: 'Status' },
        ]}
        rows={rows.map(r => ({ ...r, _actions: <span /> }))}
      />
    </div>
  )
}