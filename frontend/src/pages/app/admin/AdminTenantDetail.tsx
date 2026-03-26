import { type FormEvent, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  type BillingOut,
  type BillingStatus,
  type TenantDetail,
  cancelTenant,
  getTenant,
  registerPayment,
} from '../../../api/admin'
import styles from './AdminTenantDetail.module.css'

function formatBRL(value: string | number): string {
  const n = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(n)) return 'R$ —'
  return `R$ ${n.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`
}

function formatDate(iso: string): string {
  return new Date(`${iso}T12:00:00`).toLocaleDateString('pt-BR')
}

function billingBadgeClass(status: BillingStatus): string {
  if (status === 'active') return styles.badgeGreen
  if (status === 'trial' || status === 'grace') return styles.badgeAmber
  return styles.badgeRed
}

function billingLabel(status: BillingStatus): string {
  const labels: Record<BillingStatus, string> = {
    trial: 'Trial',
    active: 'Active',
    grace: 'Grace',
    late: 'Late',
    suspended: 'Suspenso',
    cancelled: 'Cancelado',
  }
  return labels[status]
}

function extractError(err: unknown): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  return typeof detail === 'string' ? detail : 'Ocorreu um erro. Tente novamente.'
}

export function AdminTenantDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [detail, setDetail] = useState<TenantDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [pageError, setPageError] = useState<string | null>(null)

  const [showPayment, setShowPayment] = useState(false)
  const [payAmount, setPayAmount] = useState('')
  const [payDate, setPayDate] = useState('')
  const [payTime, setPayTime] = useState('12:00')
  const [payNotes, setPayNotes] = useState('')
  const [paying, setPaying] = useState(false)
  const [payError, setPayError] = useState<string | null>(null)

  const [confirmCancel, setConfirmCancel] = useState(false)
  const [cancelling, setCancelling] = useState(false)
  const [cancelError, setCancelError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    getTenant(id)
      .then(setDetail)
      .catch(() => setPageError('Tenant não encontrado.'))
      .finally(() => setLoading(false))
  }, [id])

  async function handlePayment(e: FormEvent) {
    e.preventDefault()
    setPayError(null)
    const amount = parseFloat(payAmount.replace(',', '.'))
    if (isNaN(amount) || amount <= 0) {
      setPayError('Valor inválido.')
      return
    }
    if (!payDate) {
      setPayError('Data obrigatória.')
      return
    }
    const paid_at = new Date(`${payDate}T${payTime}:00`).toISOString()
    setPaying(true)
    try {
      const billing = await registerPayment(id!, { amount, paid_at, notes: payNotes || undefined })
      setDetail((prev) => (prev ? { ...prev, billing } : prev))
      setShowPayment(false)
      setPayAmount('')
      setPayDate('')
      setPayTime('12:00')
      setPayNotes('')
    } catch (err) {
      setPayError(extractError(err))
    } finally {
      setPaying(false)
    }
  }

  async function handleCancel() {
    setCancelError(null)
    setCancelling(true)
    try {
      const tenant = await cancelTenant(id!)
      setDetail((prev) => (prev ? { ...prev, tenant } : prev))
      setConfirmCancel(false)
    } catch (err) {
      setCancelError(extractError(err))
    } finally {
      setCancelling(false)
    }
  }

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.skeletonList}>
          {[0, 1, 2].map((i) => (
            <div key={i} className={styles.skeleton} />
          ))}
        </div>
      </div>
    )
  }

  if (pageError || !detail) {
    return (
      <div className={styles.page}>
        <p className={styles.pageError}>{pageError ?? 'Erro desconhecido.'}</p>
      </div>
    )
  }

  const { tenant, user, billing } = detail
  const isCancelled =
    billing?.billing_status === 'cancelled' || tenant.access_status === 'disabled'

  function BillingSection({ b }: { b: BillingOut }) {
    return (
      <>
        <div className={styles.detailRow}>
          <span className={styles.detailLabel}>Plano</span>
          <span className={styles.detailValue}>{b.plan}</span>
        </div>
        <div className={styles.detailRow}>
          <span className={styles.detailLabel}>Status</span>
          <span className={`${styles.badge} ${billingBadgeClass(b.billing_status)}`}>
            {billingLabel(b.billing_status)}
          </span>
        </div>
        <div className={styles.detailRow}>
          <span className={styles.detailLabel}>Preço/mês</span>
          <span className={styles.detailValue}>{formatBRL(b.monthly_price)}</span>
        </div>
        <div className={styles.detailRow}>
          <span className={styles.detailLabel}>Vencimento</span>
          <span className={styles.detailValue}>dia {b.due_day}</span>
        </div>
        <div className={styles.detailRow}>
          <span className={styles.detailLabel}>Período atual</span>
          <span className={styles.detailValue}>
            {formatDate(b.current_period_start)} – {formatDate(b.current_period_end)}
          </span>
        </div>
        {!isCancelled && (
          <button className={styles.btnAction} onClick={() => setShowPayment(true)}>
            Registrar pagamento
          </button>
        )}
      </>
    )
  }

  return (
    <div className={styles.page}>
      <div className={styles.breadcrumb}>
        <button className={styles.backLink} onClick={() => navigate('/app/admin')}>
          ← Tenants
        </button>
        <span className={styles.breadcrumbSep}>/</span>
        <span className={styles.breadcrumbCurrent}>{tenant.slug}</span>
      </div>

      <div className={styles.sections}>
        <div className={styles.section}>
          <p className={styles.sectionTitle}>Tenant</p>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Nome</span>
            <span className={styles.detailValue}>{tenant.name}</span>
          </div>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Slug</span>
            <span className={styles.detailValue}>{tenant.slug}</span>
          </div>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Acesso</span>
            <span className={styles.detailValue}>
              {tenant.access_status === 'enabled' ? 'Habilitado' : 'Desabilitado'}
            </span>
          </div>
        </div>

        <div className={styles.section}>
          <p className={styles.sectionTitle}>Usuário inicial</p>
          {user ? (
            <>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Username</span>
                <span className={styles.detailValue}>{user.username}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>E-mail</span>
                <span className={styles.detailValue}>{user.email}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Role</span>
                <span className={styles.detailValue}>{user.role}</span>
              </div>
            </>
          ) : (
            <p className={styles.emptySection}>Usuário não configurado.</p>
          )}
        </div>

        <div className={styles.section}>
          <p className={styles.sectionTitle}>Billing</p>
          {billing ? (
            <BillingSection b={billing} />
          ) : (
            <p className={styles.emptySection}>Billing não configurado.</p>
          )}
        </div>

        {!isCancelled && (
          <div className={styles.section}>
            {!confirmCancel ? (
              <button className={styles.btnDanger} onClick={() => setConfirmCancel(true)}>
                Cancelar tenant
              </button>
            ) : (
              <div className={styles.cancelBox}>
                <p className={styles.cancelWarning}>Tem certeza? Esta ação é irreversível.</p>
                {cancelError && <p className={styles.errorText}>{cancelError}</p>}
                <div className={styles.cancelActions}>
                  <button
                    className={styles.btnBack}
                    onClick={() => setConfirmCancel(false)}
                    disabled={cancelling}
                  >
                    Não, voltar
                  </button>
                  <button className={styles.btnDanger} onClick={handleCancel} disabled={cancelling}>
                    {cancelling ? 'Cancelando...' : 'Sim, cancelar'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {showPayment && (
        <div
          className={styles.overlay}
          onClick={() => {
            if (!paying) setShowPayment(false)
          }}
        >
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Registrar pagamento</h2>
              <button
                className={styles.modalClose}
                onClick={() => setShowPayment(false)}
                type="button"
              >
                ✕
              </button>
            </div>
            <form className={styles.form} onSubmit={handlePayment}>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="p-amount">
                  Valor (R$) *
                </label>
                <input
                  id="p-amount"
                  className={styles.input}
                  type="text"
                  inputMode="decimal"
                  placeholder="99,00"
                  value={payAmount}
                  onChange={(e) => setPayAmount(e.target.value)}
                  required
                  autoFocus
                />
              </div>
              <div className={styles.fieldRow}>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="p-date">
                    Data *
                  </label>
                  <input
                    id="p-date"
                    className={styles.input}
                    type="date"
                    value={payDate}
                    onChange={(e) => setPayDate(e.target.value)}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="p-time">
                    Hora *
                  </label>
                  <input
                    id="p-time"
                    className={styles.input}
                    type="time"
                    value={payTime}
                    onChange={(e) => setPayTime(e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="p-notes">
                  Observações
                </label>
                <textarea
                  id="p-notes"
                  className={styles.textarea}
                  placeholder="PIX transferência..."
                  value={payNotes}
                  onChange={(e) => setPayNotes(e.target.value)}
                  rows={2}
                />
              </div>
              {payError && <div className={styles.error}>{payError}</div>}
              <button className={styles.submit} type="submit" disabled={paying}>
                {paying ? 'Registrando...' : 'Confirmar pagamento'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
