import { useEffect, useState } from 'react'
import api from '../api/client'
import DataTable from '../components/DataTable'
import MapView from '../components/MapView'

export default function Properties() {
  const [rows, setRows] = useState([])
  const [tab, setTab] = useState('list')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    landlord_id: '', property_code: '', property_name: '', property_type: 'HOUSE',
    address: '', city: '', suburb: '', latitude: '', longitude: ''
  })

  const fetch = () => api.get('/properties/').then(r => setRows(r.data))
  useEffect(() => { fetch() }, [])

  const submit = async (e) => {
    e.preventDefault()
    const payload = { ...form, latitude: form.latitude ? parseFloat(form.latitude) : null, longitude: form.longitude ? parseFloat(form.longitude) : null }
    await api.post('/properties/', payload)
    setShowForm(false)
    setForm({ landlord_id: '', property_code: '', property_name: '', property_type: 'HOUSE', address: '', city: '', suburb: '', latitude: '', longitude: '' })
    fetch()
  }

  const remove = async (id) => {
    if (!confirm('Delete property?')) return
    await api.delete(`/properties/${id}`)
    fetch()
  }

  const mapProps = rows.filter(r => r.latitude && r.longitude)

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="page-title mb-0">Properties</h1>
        <div className="flex gap-2">
          <button onClick={() => setTab(tab === 'list' ? 'map' : 'list')} className="btn-secondary">
            {tab === 'list' ? 'Show Map' : 'Show List'}
          </button>
          <button onClick={() => setShowForm(true)} className="btn-primary">+ Add Property</button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <input className="input" placeholder="Landlord ID" value={form.landlord_id} onChange={e => setForm({...form, landlord_id: e.target.value})} required />
          <input className="input" placeholder="Property Code" value={form.property_code} onChange={e => setForm({...form, property_code: e.target.value})} required />
          <input className="input" placeholder="Property Name" value={form.property_name} onChange={e => setForm({...form, property_name: e.target.value})} required />
          <select className="input" value={form.property_type} onChange={e => setForm({...form, property_type: e.target.value})}>
            <option>HOUSE</option><option>COTTAGE</option><option>APARTMENT</option><option>OFFICE</option><option>SHOP</option><option>INDUSTRIAL</option>
          </select>
          <input className="input" placeholder="City" value={form.city} onChange={e => setForm({...form, city: e.target.value})} required />
          <input className="input" placeholder="Suburb" value={form.suburb} onChange={e => setForm({...form, suburb: e.target.value})} required />
          <input className="input" placeholder="Address" value={form.address} onChange={e => setForm({...form, address: e.target.value})} required />
          <input className="input" placeholder="Latitude" value={form.latitude} onChange={e => setForm({...form, latitude: e.target.value})} />
          <input className="input" placeholder="Longitude" value={form.longitude} onChange={e => setForm({...form, longitude: e.target.value})} />
          <div className="md:col-span-3 flex gap-2">
            <button className="btn-primary">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      {tab === 'list' ? (
        <DataTable
          searchKey="property_name"
          columns={[
            { key: 'property_code', label: 'Code' },
            { key: 'property_name', label: 'Name' },
            { key: 'property_type', label: 'Type' },
            { key: 'city', label: 'City' },
            { key: 'suburb', label: 'Suburb' },
            { key: 'status', label: 'Status' },
          ]}
          rows={rows.map(r => ({
            ...r,
            _actions: (
              <div className="flex gap-2 justify-end">
                <button onClick={() => remove(r.property_id)} className="text-red-600 hover:underline text-xs">Delete</button>
              </div>
            )
          }))}
        />
      ) : (
        <MapView properties={mapProps} />
      )}
    </div>
  )
}