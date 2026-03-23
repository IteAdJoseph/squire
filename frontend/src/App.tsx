import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { RedirectIfAuth } from './components/RedirectIfAuth'
import { RequireAuth } from './components/RequireAuth'
import { Landing } from './pages/Landing'
import { Login } from './pages/Login'
import { AppShell } from './pages/app/AppShell'
import { Dashboard } from './pages/app/Dashboard'
import { Customers } from './pages/app/Customers'
import { Services } from './pages/app/Services'

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Landing />} />

          <Route element={<RedirectIfAuth />}>
            <Route path="/login" element={<Login />} />
          </Route>

          <Route element={<RequireAuth />}>
            <Route path="/app" element={<AppShell />}>
              <Route index element={<Navigate to="agenda" replace />} />
              <Route path="agenda" element={<Dashboard />} />
              <Route path="clientes" element={<Customers />} />
              <Route path="servicos" element={<Services />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
