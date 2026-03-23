import { type FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login as apiLogin } from '../api/auth'
import { useAuth } from '../contexts/AuthContext'
import styles from './Login.module.css'

export function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [tenantSlug, setTenantSlug] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const { access_token } = await apiLogin({
        tenant_slug: tenantSlug,
        username,
        password,
      })
      await login(access_token)
      navigate('/app', { replace: true })
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 403) {
        setError('Sua conta está suspensa. Entre em contato com o suporte.')
      } else {
        setError('Usuário ou senha incorretos.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>
          re<span className="dot">·</span>min<span className="dot">·</span>da
        </div>

        <p className={styles.title}>Bem-vindo de volta</p>
        <p className={styles.subtitle}>Entre na sua conta para continuar</p>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="tenant_slug">
              Seu negócio
            </label>
            <input
              id="tenant_slug"
              className={styles.input}
              type="text"
              placeholder="meu-salao"
              value={tenantSlug}
              onChange={(e) => setTenantSlug(e.target.value)}
              required
              autoComplete="organization"
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="username">
              Usuário
            </label>
            <input
              id="username"
              className={styles.input}
              type="text"
              placeholder="seu.usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="password">
              Senha
            </label>
            <input
              id="password"
              className={styles.input}
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          {error && <div className={styles.error}>{error}</div>}

          <button className={styles.submit} type="submit" disabled={loading}>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <p className={styles.back}>
          <Link to="/">← Voltar para o início</Link>
        </p>
      </div>
    </div>
  )
}
