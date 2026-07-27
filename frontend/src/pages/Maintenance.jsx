import { useEffect, useState } from 'react'
import api from '../api/client'
import DataTable from '../components/DataTable'

export default function Maintenance() {
  const [requests, setRequests] = useState([])
  const [units, setUnits] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ unit_id: '', title: '', description: '', priority: 'MEDIUM' })

  useEffect(() => {
    api.get('/maintenance/requests/').then(r => setRequests(r.data))
    api.get('/units/').then(r => setUnits(r.data))
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    await api.post('/maintenance/requests/', form)
    setShowForm(false)
    const r = await api.get('/maintenance/requests/')
    setRequests(r.data)
  }

  const updateStatus = async (id, status) => {
    await api.put(`/maintenance/requests/${id}`, { status })
    const r = await api.get('/maintenance/requests/')
    setRequests(r.data)
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title mb-0">Maintenance</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary">+ New Request</button>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <select className="input" value={form.unit_id} onChange={e => setForm({...form, unit_id: e.target.value})} required>
            <option value="">Select Unit</option>
            {units.map(u => <option key={u.unit_id} value={u.unit_id}>{u.unit_number}</option>)}
          </select>
          <input className="input" placeholder="Title" value={form.title} onChange={e => setForm({...form, title: e.target.value})} required />
          <select className="input" value={form.priority} onChange={e => setForm({...form, priority: e.target.value})}>
            <option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>EMERGENCY</option>
          </select>
          <textarea className="input md:col-span-3" placeholder="Description" rows={2} value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
          <div className="md:col-span-3 flex gap-2">
            <button className="btn-primary">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      <DataTable
        searchKey="title"
        columns={[
          { key: 'title', label: 'Issue' },
          { key: 'priority', label: 'Priority' },
          { key: 'status', label: 'Status' },
          { key: 'reported_at', label: 'Reported' },
        ]}
        rows={requests.map(r => ({
          ...r,
          _actions: (
            <div className="flex gap-2 justify-end">
              {r.status === 'OPEN' && <button onClick={() => updateStatus(r.request_id, 'IN_PROGRESS')} className="text-xs text-blue-600 hover:underline">Start</button>}
              {r.status === 'IN_PROGRESS' && <button onClick={() => updateStatus(r.request_id, 'COMPLETED')} className="text-xs text-emerald-700 hover:underline">Complete</button>}
            </div>
          )
        }))}
      />
    </div>
  )
}