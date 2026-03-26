import { type FormEvent, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  type BillingStatus,
  type CreateBillingIn,
  type TenantListItem,
  configureBilling,
  createTenant,
  createUser,
  listTenants,
} from '../../../api/admin'
import styles from './AdminTenants.module.css'

function billingBadge(status: BillingStatus | null): { label: string; cls: string } {
  if (status === 'active') return { label: 'Active', cls: styles.badgeGreen }
  if (status === 'trial' || status === 'grace') return { label: status === 'trial' ? 'Trial' : 'Grace', cls: styles.badgeAmber }
  if (status === 'late' || status === 'suspended' || status === 'cancelled')
    return { label: status === 'late' ? 'Late' : status === 'suspended' ? 'Suspenso' : 'Cancelado', cls: styles.badgeRed }
  return { label: 'Sem billing', cls: styles.badgeGray }
}

function extractError(err: unknown): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  return typeof detail === 'string' ? detail : 'Verifique os dados e tente novamente.'
}

export function AdminTenants() {
  const navigate = useNavigate()
  const [items, setItems] = useState<TenantListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [pageError, setPageError] = useState<string | null>(null)

  const [showWizard, setShowWizard] = useState(false)
  const [step, setStep] = useState(1)
  const [createdTenantId, setCreatedTenantId] = useState<string | null>(null)
  const [step1Done, setStep1Done] = useState(false)
  const [step2Done, setStep2Done] = useState(false)

  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [plan, setPlan] = useState('')
  const [monthlyPrice, setMonthlyPrice] = useState('')
  const [dueDay, setDueDay] = useState('')
  const [billingStatus, setBillingStatus] = useState<'trial' | 'active'>('trial')

  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    listTenants()
      .then(setItems)
      .catch(() => setPageError('Não foi possível carregar os tenants.'))
      .finally(() => setLoading(false))
  }, [])

  function openWizard() {
    setStep(1)
    setCreatedTenantId(null)
    setStep1Done(false)
    setStep2Done(false)
    setName('')
    setSlug('')
    setUsername('')
    setEmail('')
    setPassword('')
    setPlan('')
    setMonthlyPrice('')
    setDueDay('')
    setBillingStatus('trial')
    setFormError(null)
    setShowWizard(true)
  }

  function closeWizard() {
    if (submitting) return
    setShowWizard(false)
  }

  async function handleStep1(e: FormEvent) {
    e.preventDefault()
    setFormError(null)
    if (step1Done) {
      setStep(2)
      return
    }
    setSubmitting(true)
    try {
      const tenant = await createTenant({ name, slug })
      setCreatedTenantId(tenant.id)
      setStep1Done(true)
      setStep(2)
    } catch (err) {
      setFormError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleStep2(e: FormEvent) {
    e.preventDefault()
    setFormError(null)
    if (step2Done) {
      setStep(3)
      return
    }
    if (!createdTenantId) return
    setSubmitting(true)
    try {
      await createUser(createdTenantId, { username, email, password })
      setStep2Done(true)
      setStep(3)
    } catch (err) {
      setFormError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleStep3(e: FormEvent) {
    e.preventDefault()
    setFormError(null)
    if (!createdTenantId) return
    const price = parseFloat(monthlyPrice.replace(',', '.'))
    if (isNaN(price) || price < 0) {
      setFormError('Preço inválido.')
      return
    }
    const day = parseInt(dueDay, 10)
    if (isNaN(day) || day < 1 || day > 28) {
      setFormError('Dia de vencimento deve ser entre 1 e 28.')
      return
    }
    setSubmitting(true)
    try {
      const body: CreateBillingIn = {
        plan,
        monthly_price: price,
        due_day: day,
        billing_status: billingStatus,
        grace_days: 5,
        provider: 'manual_pix',
      }
      await configureBilling(createdTenantId, body)
      const fresh = await listTenants()
      setItems(fresh)
      setShowWizard(false)
    } catch (err) {
      setFormError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Tenants</h1>
        <button className={styles.btnNew} onClick={openWizard}>
          + Novo tenant
        </button>
      </div>

      {loading && (
        <div className={styles.skeletonList}>
          {[0, 1, 2].map((i) => (
            <div key={i} className={styles.skeleton} />
          ))}
        </div>
      )}

      {!loading && pageError && <p className={styles.pageError}>{pageError}</p>}

      {!loading && !pageError && items.length === 0 && (
        <div className={styles.empty}>
          <p className={styles.emptyText}>Nenhum tenant cadastrado.</p>
          <button className={styles.btnNew} onClick={openWizard}>
            Criar primeiro tenant
          </button>
        </div>
      )}

      {!loading && items.length > 0 && (
        <ul className={styles.list}>
          {items.map((t) => {
            const badge = billingBadge(t.billing_status)
            return (
              <li
                key={t.id}
                className={styles.card}
                onClick={() => navigate(`/app/admin/${t.id}`)}
              >
                <div className={styles.cardRow}>
                  <div className={styles.cardInfo}>
                    <span className={styles.cardName}>{t.name}</span>
                    <span className={styles.cardSlug}>{t.slug}</span>
                  </div>
                  <span className={`${styles.badge} ${badge.cls}`}>{badge.label}</span>
                </div>
              </li>
            )
          })}
        </ul>
      )}

      {showWizard && (
        <div className={styles.overlay} onClick={closeWizard}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Novo tenant</h2>
              <button className={styles.modalClose} onClick={closeWizard} type="button">
                ✕
              </button>
            </div>

            <div className={styles.stepBar}>
              {[1, 2, 3].map((n) => (
                <div key={n} className={`${styles.stepDot} ${step >= n ? styles.stepDotActive : ''}`}>
                  {n}
                </div>
              ))}
            </div>

            {step === 1 && (
              <form className={styles.form} onSubmit={handleStep1}>
                <p className={styles.stepLabel}>Passo 1 — Tenant</p>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="t-name">
                    Nome *
                  </label>
                  <input
                    id="t-name"
                    className={styles.input}
                    type="text"
                    placeholder="Salão da Maria"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    autoFocus
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="t-slug">
                    Slug *
                  </label>
                  <input
                    id="t-slug"
                    className={styles.input}
                    type="text"
                    placeholder="salao-maria"
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    required
                  />
                </div>
                {formError && <div className={styles.error}>{formError}</div>}
                <button className={styles.submit} type="submit" disabled={submitting}>
                  {submitting ? 'Criando...' : step1Done ? 'Continuar →' : 'Próximo →'}
                </button>
              </form>
            )}

            {step === 2 && (
              <form className={styles.form} onSubmit={handleStep2}>
                <p className={styles.stepLabel}>Passo 2 — Usuário inicial</p>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="u-username">
                    Username *
                  </label>
                  <input
                    id="u-username"
                    className={styles.input}
                    type="text"
                    placeholder="maria"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    autoFocus
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="u-email">
                    E-mail *
                  </label>
                  <input
                    id="u-email"
                    className={styles.input}
                    type="email"
                    placeholder="maria@exemplo.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="u-password">
                    Senha *
                  </label>
                  <input
                    id="u-password"
                    className={styles.input}
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                {formError && <div className={styles.error}>{formError}</div>}
                <div className={styles.wizardNav}>
                  <button
                    type="button"
                    className={styles.btnBack}
                    onClick={() => {
                      setFormError(null)
                      setStep(1)
                    }}
                  >
                    ← Voltar
                  </button>
                  <button className={styles.submit} type="submit" disabled={submitting}>
                    {submitting ? 'Salvando...' : step2Done ? 'Continuar →' : 'Próximo →'}
                  </button>
                </div>
              </form>
            )}

            {step === 3 && (
              <form className={styles.form} onSubmit={handleStep3}>
                <p className={styles.stepLabel}>Passo 3 — Billing</p>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="b-plan">
                    Plano *
                  </label>
                  <input
                    id="b-plan"
                    className={styles.input}
                    type="text"
                    placeholder="starter"
                    value={plan}
                    onChange={(e) => setPlan(e.target.value)}
                    required
                    autoFocus
                  />
                </div>
                <div className={styles.fieldRow}>
                  <div className={styles.field}>
                    <label className={styles.label} htmlFor="b-price">
                      Preço/mês (R$) *
                    </label>
                    <input
                      id="b-price"
                      className={styles.input}
                      type="text"
                      inputMode="decimal"
                      placeholder="99,00"
                      value={monthlyPrice}
                      onChange={(e) => setMonthlyPrice(e.target.value)}
                      required
                    />
                  </div>
                  <div className={styles.field}>
                    <label className={styles.label} htmlFor="b-due">
                      Dia vencimento *
                    </label>
                    <input
                      id="b-due"
                      className={styles.input}
                      type="number"
                      min="1"
                      max="28"
                      placeholder="10"
                      value={dueDay}
                      onChange={(e) => setDueDay(e.target.value)}
                      required
                    />
                  </div>
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="b-status">
                    Status inicial *
                  </label>
                  <select
                    id="b-status"
                    className={styles.input}
                    value={billingStatus}
                    onChange={(e) => setBillingStatus(e.target.value as 'trial' | 'active')}
                  >
                    <option value="trial">Trial</option>
                    <option value="active">Active</option>
                  </select>
                </div>
                {formError && <div className={styles.error}>{formError}</div>}
                <div className={styles.wizardNav}>
                  <button
                    type="button"
                    className={styles.btnBack}
                    onClick={() => {
                      setFormError(null)
                      setStep(2)
                    }}
                  >
                    ← Voltar
                  </button>
                  <button className={styles.submit} type="submit" disabled={submitting}>
                    {submitting ? 'Criando...' : 'Criar tenant'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
