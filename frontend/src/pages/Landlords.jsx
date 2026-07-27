import { useEffect, useState } from 'react'
import api from '../api/client'
import DataTable from '../components/DataTable'

export default function Landlords() {
  const [rows, setRows] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ full_name: '', national_id: '', phone: '', email: '', address: '', bank_details: '' })

  const fetch = () => api.get('/landlords/').then(r => setRows(r.data))

  useEffect(() => { fetch() }, [])

  const submit = async (e) => {
    e.preventDefault()
    await api.post('/landlords/', form)
    setShowForm(false)
    setForm({ full_name: '', national_id: '', phone: '', email: '', address: '', bank_details: '' })
    fetch()
  }

  const remove = async (id) => {
    if (!confirm('Delete this landlord?')) return
    await api.delete(`/landlords/${id}`)
    fetch()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title mb-0">Landlords</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary">+ Add Landlord</button>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <input className="input" placeholder="Full Name" value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} required />
          <input className="input" placeholder="National ID" value={form.national_id} onChange={e => setForm({...form, national_id: e.target.value})} required />
          <input className="input" placeholder="Phone" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} required />
          <input className="input" placeholder="Email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
          <input className="input" placeholder="Address" value={form.address} onChange={e => setForm({...form, address: e.target.value})} />
          <input className="input" placeholder="Bank Details" value={form.bank_details} onChange={e => setForm({...form, bank_details: e.target.value})} />
          <div className="md:col-span-3 flex gap-2">
            <button className="btn-primary">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      <DataTable
        searchKey="full_name"
        columns={[
          { key: 'full_name', label: 'Name' },
          { key: 'phone', label: 'Phone' },
          { key: 'national_id', label: 'National ID' },
          { key: 'is_active', label: 'Active', format: v => v ? 'Yes' : 'No' },
        ]}
        rows={rows.map(r => ({
          ...r,
          _actions: (
            <div className="flex gap-2 justify-end">
              <button onClick={() => remove(r.landlord_id)} className="text-red-600 hover:underline text-xs">Delete</button>
            </div>
          )
        }))}
      />
    </div>
  )
}