import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const nav = [
  { to: '/', label: 'Dashboard' },
  { to: '/landlords', label: 'Landlords' },
  { to: '/properties', label: 'Properties' },
  { to: '/units', label: 'Units' },
  { to: '/leases', label: 'Leases' },
  { to: '/payments', label: 'Payments' },
  { to: '/maintenance', label: 'Maintenance' },
  { to: '/communications', label: 'SMS' },
  { to: '/reports', label: 'Reports' },
]

export default function Layout() {
  const { manager, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <aside className="w-full md:w-56 bg-emerald-900 text-white flex-shrink-0">
        <div className="p-4 font-bold text-lg border-b border-emerald-800">ZimRental</div>
        <nav className="flex flex-row md:flex-col overflow-x-auto md:overflow-visible">
          {nav.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                `px-4 py-3 text-sm hover:bg-emerald-800 whitespace-nowrap ${isActive ? 'bg-emerald-800 font-semibold' : ''}`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto p-4 border-t border-emerald-800 hidden md:block">
          <div className="text-xs text-emerald-200 mb-2">{manager?.full_name || 'Manager'}</div>
          <button onClick={handleLogout} className="text-xs underline hover:text-white">Logout</button>
        </div>
      </aside>

      <main className="flex-1 p-4 md:p-6 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}