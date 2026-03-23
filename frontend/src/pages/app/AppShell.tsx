import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import styles from './AppShell.module.css'

const ADMIN_TENANT = 'reminda-admin'

function CalendarIcon() {
  return (
    <svg className={styles.navIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="5" width="18" height="17" rx="2.5" />
      <path d="M3 11h18M8 3v4M16 3v4" />
      <rect x="8" y="14" width="3" height="3" rx="0.5" fill="currentColor" stroke="none" />
    </svg>
  )
}

function PersonIcon() {
  return (
    <svg className={styles.navIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 20c0-3.87 3.13-7 7-7s7 3.13 7 7" />
    </svg>
  )
}

function ScissorsIcon() {
  return (
    <svg className={styles.navIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="6" cy="6" r="2.5" />
      <circle cx="6" cy="18" r="2.5" />
      <path d="M8.12 8.12L12 12m0 0l8-8M12 12l-3.88 3.88M12 12l8 8" />
    </svg>
  )
}

function SettingsIcon() {
  return (
    <svg className={styles.navIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
    </svg>
  )
}

function LogoutIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" />
    </svg>
  )
}

export function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const isAdmin = user?.role === 'owner' && user?.tenant_name?.toLowerCase() === ADMIN_TENANT

  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  const navClass = ({ isActive }: { isActive: boolean }) =>
    `${styles.navItem}${isActive ? ` ${styles.active}` : ''}`

  const bottomClass = ({ isActive }: { isActive: boolean }) =>
    `${styles.bottomNavItem}${isActive ? ` ${styles.active}` : ''}`

  return (
    <div className={styles.shell}>
      {/* ─── Sidebar (desktop) ─── */}
      <aside className={styles.sidebar}>
        <Link to="/" className={styles.sidebarLogo}>
          re<span className="dot">·</span>min<span className="dot">·</span>da
        </Link>

        <nav className={styles.nav}>
          <NavLink to="/app/agenda" className={navClass}>
            <CalendarIcon /> Agenda
          </NavLink>
          <NavLink to="/app/clientes" className={navClass}>
            <PersonIcon /> Clientes
          </NavLink>
          <NavLink to="/app/servicos" className={navClass}>
            <ScissorsIcon /> Serviços
          </NavLink>
          {isAdmin && (
            <NavLink to="/app/admin" className={navClass}>
              <SettingsIcon /> Admin
            </NavLink>
          )}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.userInfo}>
            <span className={styles.userName}>{user?.username}</span>
            <span className={styles.tenantName}>{user?.tenant_name}</span>
          </div>
          <button className={styles.logoutBtn} onClick={handleLogout}>
            <LogoutIcon /> Sair
          </button>
        </div>
      </aside>

      {/* ─── Main content ─── */}
      <main className={styles.main}>
        <Outlet />
      </main>

      {/* ─── Bottom nav (mobile) ─── */}
      <nav className={styles.bottomNav}>
        <div className={styles.bottomNavInner}>
          <NavLink to="/app/agenda" className={bottomClass}>
            <CalendarIcon />
            Agenda
          </NavLink>
          <NavLink to="/app/clientes" className={bottomClass}>
            <PersonIcon />
            Clientes
          </NavLink>
          <NavLink to="/app/servicos" className={bottomClass}>
            <ScissorsIcon />
            Serviços
          </NavLink>
          {isAdmin && (
            <NavLink to="/app/admin" className={bottomClass}>
              <SettingsIcon />
              Admin
            </NavLink>
          )}
        </div>
      </nav>
    </div>
  )
}
