import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

export default function MapView({ properties }) {
  const center = properties.length
    ? [properties[0].latitude, properties[0].longitude]
    : [-17.8252, 31.0335]

  return (
    <div className="h-96 rounded-lg overflow-hidden border">
      <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {properties.map((p) => (
          p.latitude && p.longitude && (
            <Marker key={p.property_id} position={[p.latitude, p.longitude]}>
              <Popup>
                <div className="text-sm">
                  <div className="font-bold">{p.property_name}</div>
                  <div>{p.address}</div>
                  <div className="text-gray-500">{p.city}, {p.suburb}</div>
                </div>
              </Popup>
            </Marker>
          )
        ))}
      </MapContainer>
    </div>
  )
}