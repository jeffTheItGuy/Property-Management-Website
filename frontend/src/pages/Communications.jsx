import { useEffect, useState } from 'react'
import api from '../api/client'
import DataTable from '../components/DataTable'

export default function Communications() {
  const [logs, setLogs] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ phone: '', message: '', recipient_type: 'TENANT' })

  const fetch = () => api.get('/communications/sms/').then(r => setLogs(r.data))
  useEffect(() => { fetch() }, [])

  const submit = async (e) => {
    e.preventDefault()
    await api.post('/communications/sms/send', form)
    setShowForm(false)
    setForm({ phone: '', message: '', recipient_type: 'TENANT' })
    fetch()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title mb-0">SMS Communications</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary">+ Send SMS</button>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card mb-4 grid grid-cols-1 gap-4">
          <div className="flex gap-4">
            <input className="input flex-1" placeholder="Phone" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} required />
            <select className="input w-48" value={form.recipient_type} onChange={e => setForm({...form, recipient_type: e.target.value})}>
              <option>TENANT</option><option>LANDLORD</option><option>MANAGER</option>
            </select>
          </div>
          <textarea className="input" rows={3} placeholder="Message" value={form.message} onChange={e => setForm({...form, message: e.target.value})} required />
          <div className="flex gap-2">
            <button className="btn-primary">Send</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      <DataTable
        searchKey="phone"
        columns={[
          { key: 'phone', label: 'Phone' },
          { key: 'recipient_type', label: 'To' },
          { key: 'message', label: 'Message' },
          { key: 'status', label: 'Status' },
          { key: 'created_at', label: 'Sent At' },
        ]}
        rows={logs.map(l => ({ ...l, _actions: <span /> }))}
      />
    </div>
  )
}