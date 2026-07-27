import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [manager, setManager] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) { setLoading(false); return }
    api.get('/auth/me').then(r => setManager(r.data)).catch(() => {
      localStorage.removeItem('token')
    }).finally(() => setLoading(false))
  }, [])

  const login = async (phone, password) => {
    const params = new URLSearchParams()
    params.append('username', phone)
    params.append('password', password)
    const { data } = await api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    localStorage.setItem('token', data.access_token)
    const me = await api.get('/auth/me')
    setManager(me.data)
    return data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setManager(null)
  }

  return (
    <AuthContext.Provider value={{ manager, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)