import { type FormEvent, useEffect, useState } from 'react'
import { createService, listServices, type ServiceOut } from '../../api/services'
import styles from './Services.module.css'

function formatBRL(value: string | number): string {
  const n = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(n)) return 'R$ —'
  return `R$ ${n.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`
}

function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes} min`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m === 0 ? `${h}h` : `${h}h ${m}min`
}

export function Services() {
  const [items, setItems] = useState<ServiceOut[]>([])
  const [loading, setLoading] = useState(true)
  const [pageError, setPageError] = useState<string | null>(null)

  const [showModal, setShowModal] = useState(false)
  const [name, setName] = useState('')
  const [duration, setDuration] = useState('')
  const [totalPrice, setTotalPrice] = useState('')
  const [depositAmount, setDepositAmount] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    listServices()
      .then(setItems)
      .catch(() => setPageError('Não foi possível carregar os serviços.'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!showModal) return
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') closeModal()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [showModal])

  function openModal() {
    setName('')
    setDuration('')
    setTotalPrice('')
    setDepositAmount('')
    setFormError(null)
    setShowModal(true)
  }

  function closeModal() {
    if (submitting) return
    setShowModal(false)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setFormError(null)

    const total = parseFloat(totalPrice.replace(',', '.'))
    const deposit = depositAmount.trim() ? parseFloat(depositAmount.replace(',', '.')) : 0

    if (isNaN(total) || total < 0) {
      setFormError('Preço total inválido.')
      return
    }
    if (deposit > total) {
      setFormError('O sinal não pode ser maior que o preço total.')
      return
    }

    setSubmitting(true)
    try {
      const created = await createService({
        name,
        duration_minutes: parseInt(duration, 10),
        total_price: total,
        deposit_amount: deposit,
      })
      setItems((prev) => [created, ...prev])
      setShowModal(false)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
      setFormError(typeof detail === 'string' ? detail : 'Verifique os dados e tente novamente.')
    } finally {
      setSubmitting(false)
    }
  }

  const depositValue = parseFloat(depositAmount.replace(',', '.'))
  const totalValue = parseFloat(totalPrice.replace(',', '.'))
  const depositWarning =
    depositAmount.trim() && !isNaN(depositValue) && !isNaN(totalValue) && depositValue > totalValue

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Serviços</h1>
        <button className={styles.btnNew} onClick={openModal}>
          + Novo serviço
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
          <p className={styles.emptyText}>Nenhum serviço cadastrado ainda.</p>
          <button className={styles.btnNew} onClick={openModal}>
            Cadastrar primeiro serviço
          </button>
        </div>
      )}

      {!loading && items.length > 0 && (
        <ul className={styles.list}>
          {items.map((s) => (
            <li key={s.id} className={styles.card}>
              <div className={styles.cardTop}>
                <span className={styles.cardName}>{s.name}</span>
                <span className={styles.cardDuration}>{formatDuration(s.duration_minutes)}</span>
              </div>
              <div className={styles.cardBottom}>
                <span className={styles.cardPrice}>{formatBRL(s.total_price)}</span>
                {parseFloat(s.deposit_amount) > 0 ? (
                  <span className={styles.tagDeposit}>
                    Sinal: {formatBRL(s.deposit_amount)}
                  </span>
                ) : (
                  <span className={styles.tagNoDeposit}>Sem sinal</span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {showModal && (
        <div className={styles.overlay} onClick={closeModal}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Novo serviço</h2>
              <button className={styles.modalClose} onClick={closeModal} type="button">
                ✕
              </button>
            </div>

            <form className={styles.form} onSubmit={handleSubmit}>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="s-name">
                  Nome *
                </label>
                <input
                  id="s-name"
                  className={styles.input}
                  type="text"
                  placeholder="Corte feminino"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  autoFocus
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label} htmlFor="s-duration">
                  Duração (minutos) *
                </label>
                <input
                  id="s-duration"
                  className={styles.input}
                  type="number"
                  placeholder="60"
                  min="1"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  required
                />
              </div>

              <div className={styles.fieldRow}>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="s-price">
                    Preço total (R$) *
                  </label>
                  <input
                    id="s-price"
                    className={styles.input}
                    type="text"
                    inputMode="decimal"
                    placeholder="150,00"
                    value={totalPrice}
                    onChange={(e) => setTotalPrice(e.target.value)}
                    required
                  />
                </div>

                <div className={styles.field}>
                  <label className={styles.label} htmlFor="s-deposit">
                    Sinal (R$)
                  </label>
                  <input
                    id="s-deposit"
                    className={`${styles.input} ${depositWarning ? styles.inputWarn : ''}`}
                    type="text"
                    inputMode="decimal"
                    placeholder="50,00"
                    value={depositAmount}
                    onChange={(e) => setDepositAmount(e.target.value)}
                  />
                </div>
              </div>

              {depositWarning && (
                <p className={styles.warn}>O sinal não pode ser maior que o preço total.</p>
              )}

              {formError && <div className={styles.error}>{formError}</div>}

              <button className={styles.submit} type="submit" disabled={submitting}>
                {submitting ? 'Salvando...' : 'Salvar serviço'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
