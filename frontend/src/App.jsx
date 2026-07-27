import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Landlords from './pages/Landlords'
import Properties from './pages/Properties'
import Units from './pages/Units'
import Leases from './pages/Leases'
import Payments from './pages/Payments'
import Maintenance from './pages/Maintenance'
import Communications from './pages/Communications'
import Reports from './pages/Reports'

function RequireAuth({ children }) {
  const { manager, loading } = useAuth()
  if (loading) return <div className="p-10">Loading...</div>
  return manager ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<RequireAuth><Layout /></RequireAuth>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/landlords" element={<Landlords />} />
        <Route path="/properties" element={<Properties />} />
        <Route path="/units" element={<Units />} />
        <Route path="/leases" element={<Leases />} />
        <Route path="/payments" element={<Payments />} />
        <Route path="/maintenance" element={<Maintenance />} />
        <Route path="/communications" element={<Communications />} />
        <Route path="/reports" element={<Reports />} />
      </Route>
    </Routes>
  )
}