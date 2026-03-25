import { type FormEvent, useEffect, useMemo, useState } from 'react'
import {
  cancelAppointment,
  completeAppointment,
  confirmDepositCharge,
  createAppointment,
  createBalanceCharge,
  createDepositCharge,
  getAppointment,
  listAppointments,
  type AppointmentDetailOut,
  type AppointmentOut,
  type AppointmentStatus,
} from '../../api/appointments'
import { listCustomers, type CustomerOut } from '../../api/customers'
import { listServices, type ServiceOut } from '../../api/services'
import styles from './Dashboard.module.css'

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatAt(iso: string): string {
  const d = new Date(iso)
  const weekday = d.toLocaleDateString('pt-BR', { weekday: 'short' }).replace('.', '')
  const date = d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  const time = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  return `${weekday}, ${date} às ${time}`
}

function formatBRL(value: string | number): string {
  const n = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(n)) return 'R$ —'
  return `R$ ${n.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`
}

function extractError(err: unknown): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  return typeof detail === 'string' ? detail : 'Erro ao processar. Tente novamente.'
}

const STATUS_LABEL: Record<AppointmentStatus, string> = {
  draft: 'Rascunho',
  awaiting_deposit: 'Aguardando sinal',
  confirmed: 'Confirmado',
  completed: 'Concluído',
  no_show: 'Não compareceu',
  cancelled: 'Cancelado',
}

const STATUS_BADGE: Record<AppointmentStatus, string> = {
  draft: styles.badgeDefault,
  awaiting_deposit: styles.badgeAwaiting,
  confirmed: styles.badgeConfirmed,
  completed: styles.badgeCompleted,
  no_show: styles.badgeCancelled,
  cancelled: styles.badgeCancelled,
}

// ─── Component ────────────────────────────────────────────────────────────────

export function Dashboard() {
  const [appointments, setAppointments] = useState<AppointmentOut[]>([])
  const [customers, setCustomers] = useState<CustomerOut[]>([])
  const [services, setServices] = useState<ServiceOut[]>([])
  const [loading, setLoading] = useState(true)
  const [pageError, setPageError] = useState<string | null>(null)

  const [showCreate, setShowCreate] = useState(false)
  const [formCustomerId, setFormCustomerId] = useState('')
  const [formServiceId, setFormServiceId] = useState('')
  const [formDate, setFormDate] = useState('')
  const [formTime, setFormTime] = useState('')
  const [formNotes, setFormNotes] = useState('')
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  const [detailId, setDetailId] = useState<string | null>(null)
  const [detail, setDetail] = useState<AppointmentDetailOut | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  const customerMap = useMemo(
    () => new Map(customers.map((c) => [c.id, c.name])),
    [customers],
  )
  const serviceMap = useMemo(
    () => new Map(services.map((s) => [s.id, s.name])),
    [services],
  )
  const sorted = useMemo(
    () =>
      [...appointments].sort(
        (a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime(),
      ),
    [appointments],
  )

  useEffect(() => {
    Promise.all([listAppointments(), listCustomers(), listServices()])
      .then(([appts, custs, svcs]) => {
        setAppointments(appts)
        setCustomers(custs)
        setServices(svcs)
      })
      .catch(() => setPageError('Não foi possível carregar a agenda.'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!showCreate) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeCreate()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [showCreate])

  useEffect(() => {
    if (!detailId) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeDetail()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [detailId])

  // ─── Modal criar ──────────────────────────────────────────────────────────

  function openCreate() {
    const today = new Date().toISOString().split('T')[0]
    setFormCustomerId(customers[0]?.id ?? '')
    setFormServiceId(services[0]?.id ?? '')
    setFormDate(today)
    setFormTime('09:00')
    setFormNotes('')
    setCreateError(null)
    setShowCreate(true)
  }

  function closeCreate() {
    if (creating) return
    setShowCreate(false)
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    setCreateError(null)
    setCreating(true)
    try {
      const scheduledAt = new Date(`${formDate}T${formTime}:00`).toISOString()
      const created = await createAppointment({
        customer_id: formCustomerId,
        service_id: formServiceId,
        scheduled_at: scheduledAt,
        notes: formNotes.trim() || undefined,
      })
      setAppointments((prev) => [created, ...prev])
      setShowCreate(false)
    } catch (err) {
      setCreateError(extractError(err))
    } finally {
      setCreating(false)
    }
  }

  // ─── Modal detalhe ────────────────────────────────────────────────────────

  async function openDetail(id: string) {
    setDetailId(id)
    setDetail(null)
    setDetailLoading(true)
    setActionError(null)
    try {
      setDetail(await getAppointment(id))
    } catch {
      setDetailId(null)
    } finally {
      setDetailLoading(false)
    }
  }

  function closeDetail() {
    if (actionLoading) return
    setDetailId(null)
    setDetail(null)
    setActionError(null)
  }

  async function refreshDetail(id: string) {
    const fresh = await getAppointment(id)
    setDetail(fresh)
    setAppointments((prev) => prev.map((a) => (a.id === id ? fresh.appointment : a)))
  }

  async function handleAction(action: () => Promise<unknown>) {
    if (!detailId) return
    setActionLoading(true)
    setActionError(null)
    try {
      await action()
      await refreshDetail(detailId)
    } catch (err) {
      setActionError(extractError(err))
    } finally {
      setActionLoading(false)
    }
  }

  // ─── Lógica do detalhe ───────────────────────────────────────────────────

  const appt = detail?.appointment
  const charges = detail?.charges ?? []
  const depositCharge = charges.find((c) => c.type === 'deposit' && c.status !== 'cancelled')
  const balanceCharge = charges.find((c) => c.type === 'balance' && c.status !== 'cancelled')

  const canGenerateDeposit =
    appt?.status === 'awaiting_deposit' &&
    !depositCharge &&
    parseFloat(appt.deposit_amount) > 0

  const canConfirmDeposit =
    appt?.status === 'awaiting_deposit' && depositCharge?.status === 'pending'

  const canComplete = appt?.status === 'confirmed'

  const canCancel =
    appt !== undefined && !['completed', 'cancelled'].includes(appt.status)

  const canGenerateBalance =
    appt?.status === 'completed' && parseFloat(appt?.balance_amount ?? '0') > 0 && !balanceCharge

  const hasBalancePending = appt?.status === 'completed' && balanceCharge?.status === 'pending'

  const hasActions =
    canGenerateDeposit ||
    canConfirmDeposit ||
    canComplete ||
    canCancel ||
    canGenerateBalance ||
    hasBalancePending

  // ─── JSX ─────────────────────────────────────────────────────────────────

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Agenda</h1>
        <button className={styles.btnNew} onClick={openCreate}>
          + Novo agendamento
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

      {!loading && !pageError && sorted.length === 0 && (
        <div className={styles.empty}>
          <p className={styles.emptyText}>Nenhum agendamento ainda.</p>
          <button className={styles.btnNew} onClick={openCreate}>
            Criar primeiro agendamento
          </button>
        </div>
      )}

      {!loading && sorted.length > 0 && (
        <ul className={styles.list}>
          {sorted.map((a) => (
            <li
              key={a.id}
              className={styles.card}
              onClick={() => openDetail(a.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && openDetail(a.id)}
            >
              <div className={styles.cardRow}>
                <span className={styles.cardAt}>{formatAt(a.scheduled_at)}</span>
                <span className={`${styles.badge} ${STATUS_BADGE[a.status]}`}>
                  {STATUS_LABEL[a.status]}
                </span>
              </div>
              <span className={styles.cardName}>{customerMap.get(a.customer_id) ?? '—'}</span>
              <span className={styles.cardMeta}>
                {serviceMap.get(a.service_id) ?? '—'} · {formatBRL(a.total_price)}
              </span>
            </li>
          ))}
        </ul>
      )}

      {/* ─── Modal: Criar agendamento ─── */}
      {showCreate && (
        <div className={styles.overlay} onClick={closeCreate}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Novo agendamento</h2>
              <button className={styles.modalClose} onClick={closeCreate} type="button">
                ✕
              </button>
            </div>
            <form className={styles.form} onSubmit={handleCreate}>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="a-customer">
                  Cliente *
                </label>
                <select
                  id="a-customer"
                  className={styles.input}
                  value={formCustomerId}
                  onChange={(e) => setFormCustomerId(e.target.value)}
                  required
                >
                  {customers.length === 0 && (
                    <option value="">Nenhum cliente cadastrado</option>
                  )}
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.field}>
                <label className={styles.label} htmlFor="a-service">
                  Serviço *
                </label>
                <select
                  id="a-service"
                  className={styles.input}
                  value={formServiceId}
                  onChange={(e) => setFormServiceId(e.target.value)}
                  required
                >
                  {services.length === 0 && (
                    <option value="">Nenhum serviço cadastrado</option>
                  )}
                  {services.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} — {formatBRL(s.total_price)}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.fieldRow}>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="a-date">
                    Data *
                  </label>
                  <input
                    id="a-date"
                    className={styles.input}
                    type="date"
                    value={formDate}
                    onChange={(e) => setFormDate(e.target.value)}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="a-time">
                    Horário *
                  </label>
                  <input
                    id="a-time"
                    className={styles.input}
                    type="time"
                    value={formTime}
                    onChange={(e) => setFormTime(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className={styles.field}>
                <label className={styles.label} htmlFor="a-notes">
                  Observações
                </label>
                <textarea
                  id="a-notes"
                  className={styles.textarea}
                  placeholder="Informações adicionais..."
                  value={formNotes}
                  onChange={(e) => setFormNotes(e.target.value)}
                  rows={2}
                />
              </div>

              {createError && <div className={styles.error}>{createError}</div>}

              <button className={styles.submit} type="submit" disabled={creating}>
                {creating ? 'Criando...' : 'Criar agendamento'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* ─── Modal: Detalhe + ações ─── */}
      {detailId && (
        <div className={styles.overlay} onClick={closeDetail}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Agendamento</h2>
              <button className={styles.modalClose} onClick={closeDetail} type="button">
                ✕
              </button>
            </div>

            {detailLoading && (
              <div className={styles.form}>
                <div className={styles.skeleton} style={{ height: 120 }} />
              </div>
            )}

            {!detailLoading && appt && (
              <div className={styles.detailBody}>
                <div className={styles.detailSection}>
                  <div className={styles.detailRow}>
                    <span className={styles.detailLabel}>Data</span>
                    <span className={styles.detailValue}>{formatAt(appt.scheduled_at)}</span>
                  </div>
                  <div className={styles.detailRow}>
                    <span className={styles.detailLabel}>Cliente</span>
                    <span className={styles.detailValue}>
                      {customerMap.get(appt.customer_id) ?? '—'}
                    </span>
                  </div>
                  <div className={styles.detailRow}>
                    <span className={styles.detailLabel}>Serviço</span>
                    <span className={styles.detailValue}>
                      {serviceMap.get(appt.service_id) ?? '—'}
                    </span>
                  </div>
                  <div className={styles.detailRow}>
                    <span className={styles.detailLabel}>Status</span>
                    <span className={`${styles.badge} ${STATUS_BADGE[appt.status]}`}>
                      {STATUS_LABEL[appt.status]}
                    </span>
                  </div>
                  <div className={styles.detailRow}>
                    <span className={styles.detailLabel}>Total</span>
                    <span className={styles.detailValue}>{formatBRL(appt.total_price)}</span>
                  </div>
                  {parseFloat(appt.deposit_amount) > 0 && (
                    <div className={styles.detailRow}>
                      <span className={styles.detailLabel}>Sinal</span>
                      <span className={styles.detailValue}>
                        {formatBRL(appt.deposit_amount)}
                      </span>
                    </div>
                  )}
                  {parseFloat(appt.balance_amount) > 0 && (
                    <div className={styles.detailRow}>
                      <span className={styles.detailLabel}>Saldo</span>
                      <span className={styles.detailValue}>
                        {formatBRL(appt.balance_amount)}
                      </span>
                    </div>
                  )}
                  {appt.notes && (
                    <div className={styles.detailRow}>
                      <span className={styles.detailLabel}>Obs.</span>
                      <span className={styles.detailValue}>{appt.notes}</span>
                    </div>
                  )}
                </div>

                {charges.length > 0 && (
                  <div className={styles.detailSection}>
                    <p className={styles.sectionTitle}>Cobranças</p>
                    {charges.map((c) => (
                      <div key={c.id} className={styles.chargeRow}>
                        <span>
                          {c.type === 'deposit' ? 'Sinal' : 'Saldo'} — {formatBRL(c.amount)}
                        </span>
                        <span className={styles.chargeStatus}>
                          {c.status === 'pending' && 'Pendente'}
                          {c.status === 'paid' &&
                            `Pago${c.paid_at ? ` em ${new Date(c.paid_at).toLocaleDateString('pt-BR')}` : ''}`}
                          {c.status === 'cancelled' && 'Cancelado'}
                          {c.status === 'expired' && 'Expirado'}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {hasActions && (
                  <div className={styles.actions}>
                    {canGenerateDeposit && (
                      <button
                        className={styles.submit}
                        disabled={actionLoading}
                        onClick={() => handleAction(() => createDepositCharge(appt.id))}
                      >
                        {actionLoading ? '...' : 'Gerar cobrança de sinal'}
                      </button>
                    )}

                    {canConfirmDeposit && (
                      <button
                        className={styles.submit}
                        disabled={actionLoading}
                        onClick={() => handleAction(() => confirmDepositCharge(appt.id))}
                      >
                        {actionLoading ? '...' : 'Confirmar sinal pago'}
                      </button>
                    )}

                    {canComplete && (
                      <button
                        className={styles.submit}
                        disabled={actionLoading}
                        onClick={() => handleAction(() => completeAppointment(appt.id))}
                      >
                        {actionLoading ? '...' : 'Concluir atendimento'}
                      </button>
                    )}

                    {canGenerateBalance && (
                      <button
                        className={styles.submit}
                        disabled={actionLoading}
                        onClick={() => handleAction(() => createBalanceCharge(appt.id))}
                      >
                        {actionLoading ? '...' : 'Gerar cobrança de saldo'}
                      </button>
                    )}

                    {hasBalancePending && (
                      <p className={styles.balanceInfo}>
                        Saldo pendente: {formatBRL(appt.balance_amount)} — aguardando pagamento
                      </p>
                    )}

                    {canCancel && (
                      <button
                        className={styles.btnDanger}
                        disabled={actionLoading}
                        onClick={() => handleAction(() => cancelAppointment(appt.id))}
                      >
                        {actionLoading ? '...' : 'Cancelar agendamento'}
                      </button>
                    )}

                    {actionError && <div className={styles.error}>{actionError}</div>}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
