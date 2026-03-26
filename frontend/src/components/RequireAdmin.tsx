import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const ADMIN_TENANT = 'reminda admin'

export function RequireAdmin() {
  const { user, isLoading } = useAuth()

  if (isLoading) return null

  const isAdmin =
    user?.role === 'owner' && user?.tenant_name?.toLowerCase() === ADMIN_TENANT

  return isAdmin ? <Outlet /> : <Navigate to="/app/agenda" replace />
}
