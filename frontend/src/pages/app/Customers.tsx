import { type FormEvent, useEffect, useState } from 'react'
import {
  type CustomerOut,
  createCustomer,
  deleteCustomer,
  listCustomers,
  updateCustomer,
} from '../../api/customers'
import styles from './Customers.module.css'

/** Converte número brasileiro para E.164. Ex: "(11) 98765-4321" → "+5511987654321" */
function toE164(phone: string): string {
  const digits = phone.replace(/\D/g, '')
  if (digits.startsWith('55') && digits.length >= 12) return `+${digits}`
  if (digits.length >= 10) return `+55${digits}`
  return phone
}

function extractError(err: unknown): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  return typeof detail === 'string' ? detail : 'Verifique os dados e tente novamente.'
}

export function Customers() {
  const [items, setItems] = useState<CustomerOut[]>([])
  const [loading, setLoading] = useState(true)
  const [pageError, setPageError] = useState<string | null>(null)

  // create / edit modal
  const [showModal, setShowModal] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState<CustomerOut | null>(null)
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  // delete confirm modal
  const [deletingCustomer, setDeletingCustomer] = useState<CustomerOut | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  useEffect(() => {
    listCustomers()
      .then(setItems)
      .catch(() => setPageError('Não foi possível carregar os clientes.'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!showModal && !deletingCustomer) return
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        if (!submitting && !deleting) {
          setShowModal(false)
          setDeletingCustomer(null)
        }
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [showModal, deletingCustomer, submitting, deleting])

  function openCreate() {
    setEditingCustomer(null)
    setName('')
    setPhone('')
    setNotes('')
    setFormError(null)
    setShowModal(true)
  }

  function openEdit(c: CustomerOut) {
    setEditingCustomer(c)
    setName(c.name)
    setPhone(c.phone)
    setNotes(c.notes ?? '')
    setFormError(null)
    setShowModal(true)
  }

  function closeModal() {
    if (submitting) return
    setShowModal(false)
    setEditingCustomer(null)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      if (editingCustomer) {
        const updated = await updateCustomer(editingCustomer.id, {
          name,
          phone: toE164(phone),
          notes: notes.trim() || null,
        })
        setItems((prev) => prev.map((c) => (c.id === updated.id ? updated : c)))
      } else {
        const created = await createCustomer({
          name,
          phone: toE164(phone),
          notes: notes.trim() || undefined,
        })
        setItems((prev) => [created, ...prev])
      }
      setShowModal(false)
    } catch (err) {
      setFormError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete() {
    if (!deletingCustomer) return
    setDeleteError(null)
    setDeleting(true)
    try {
      await deleteCustomer(deletingCustomer.id)
      setItems((prev) => prev.filter((c) => c.id !== deletingCustomer.id))
      setDeletingCustomer(null)
    } catch (err) {
      setDeleteError(extractError(err))
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Clientes</h1>
        <button className={styles.btnNew} onClick={openCreate}>
          + Novo cliente
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
          <p className={styles.emptyText}>Nenhum cliente cadastrado ainda.</p>
          <button className={styles.btnNew} onClick={openCreate}>
            Cadastrar primeiro cliente
          </button>
        </div>
      )}

      {!loading && items.length > 0 && (
        <ul className={styles.list}>
          {items.map((c) => (
            <li key={c.id} className={styles.card}>
              <div className={styles.cardMain}>
                <span className={styles.cardName}>{c.name}</span>
                <span className={styles.cardPhone}>{c.phone}</span>
                {c.notes && <span className={styles.cardNotes}>{c.notes}</span>}
              </div>
              <div className={styles.cardActions}>
                <button
                  className={styles.btnIcon}
                  title="Editar"
                  onClick={() => openEdit(c)}
                >
                  ✎
                </button>
                <button
                  className={`${styles.btnIcon} ${styles.btnIconDanger}`}
                  title="Remover"
                  onClick={() => {
                    setDeleteError(null)
                    setDeletingCustomer(c)
                  }}
                >
                  ✕
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* ─── Create / Edit modal ─── */}
      {showModal && (
        <div className={styles.overlay} onClick={closeModal}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>
                {editingCustomer ? 'Editar cliente' : 'Novo cliente'}
              </h2>
              <button className={styles.modalClose} onClick={closeModal} type="button">
                ✕
              </button>
            </div>

            <form className={styles.form} onSubmit={handleSubmit}>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="c-name">
                  Nome *
                </label>
                <input
                  id="c-name"
                  className={styles.input}
                  type="text"
                  placeholder="Maria da Silva"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  autoFocus
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label} htmlFor="c-phone">
                  Telefone *{' '}
                  <span className={styles.hint}>WhatsApp</span>
                </label>
                <input
                  id="c-phone"
                  className={styles.input}
                  type="tel"
                  placeholder="(11) 99999-9999"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label} htmlFor="c-notes">
                  Observações
                </label>
                <textarea
                  id="c-notes"
                  className={styles.textarea}
                  placeholder="Preferências, alergias, etc."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                />
              </div>

              {formError && <div className={styles.error}>{formError}</div>}

              <button className={styles.submit} type="submit" disabled={submitting}>
                {submitting
                  ? 'Salvando...'
                  : editingCustomer
                    ? 'Salvar alterações'
                    : 'Salvar cliente'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* ─── Delete confirm modal ─── */}
      {deletingCustomer && (
        <div
          className={styles.overlay}
          onClick={() => {
            if (!deleting) setDeletingCustomer(null)
          }}
        >
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Remover cliente</h2>
              <button
                className={styles.modalClose}
                onClick={() => setDeletingCustomer(null)}
                type="button"
                disabled={deleting}
              >
                ✕
              </button>
            </div>
            <div className={styles.deleteBody}>
              <p className={styles.deleteText}>
                Remover <strong>{deletingCustomer.name}</strong>? Esta ação não pode ser
                desfeita.
              </p>
              {deleteError && <div className={styles.error}>{deleteError}</div>}
              <div className={styles.deleteActions}>
                <button
                  className={styles.btnCancel}
                  onClick={() => setDeletingCustomer(null)}
                  disabled={deleting}
                >
                  Cancelar
                </button>
                <button
                  className={styles.btnDelete}
                  onClick={handleDelete}
                  disabled={deleting}
                >
                  {deleting ? 'Removendo...' : 'Remover'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
