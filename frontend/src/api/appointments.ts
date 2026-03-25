import { apiClient } from './client'

export type AppointmentStatus =
  | 'draft'
  | 'awaiting_deposit'
  | 'confirmed'
  | 'completed'
  | 'no_show'
  | 'cancelled'

export type ChargeStatus = 'pending' | 'paid' | 'expired' | 'cancelled'
export type ChargeType = 'deposit' | 'balance'

export interface AppointmentOut {
  id: string
  tenant_id: string
  customer_id: string
  service_id: string
  scheduled_at: string
  total_price: string
  deposit_amount: string
  balance_amount: string
  status: AppointmentStatus
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ChargeOut {
  id: string
  tenant_id: string
  appointment_id: string
  type: ChargeType
  amount: string
  status: ChargeStatus
  external_ref: string | null
  paid_at: string | null
  expires_at: string | null
  created_at: string
  updated_at: string
}

export interface AppointmentDetailOut {
  appointment: AppointmentOut
  charges: ChargeOut[]
}

export interface AppointmentCreateIn {
  customer_id: string
  service_id: string
  scheduled_at: string
  notes?: string
}

export async function listAppointments(): Promise<AppointmentOut[]> {
  const { data } = await apiClient.get<AppointmentOut[]>('/appointments')
  return data
}

export async function getAppointment(id: string): Promise<AppointmentDetailOut> {
  const { data } = await apiClient.get<AppointmentDetailOut>(`/appointments/${id}`)
  return data
}

export async function createAppointment(body: AppointmentCreateIn): Promise<AppointmentOut> {
  const { data } = await apiClient.post<AppointmentOut>('/appointments', body)
  return data
}

export async function createDepositCharge(id: string): Promise<ChargeOut> {
  const { data } = await apiClient.post<ChargeOut>(`/appointments/${id}/charges/deposit`)
  return data
}

export async function confirmDepositCharge(id: string): Promise<ChargeOut> {
  const { data } = await apiClient.post<ChargeOut>(
    `/appointments/${id}/charges/deposit/confirm`,
    {},
  )
  return data
}

export async function completeAppointment(id: string): Promise<AppointmentOut> {
  const { data } = await apiClient.post<AppointmentOut>(`/appointments/${id}/complete`)
  return data
}

export async function createBalanceCharge(id: string): Promise<ChargeOut> {
  const { data } = await apiClient.post<ChargeOut>(`/appointments/${id}/charges/balance`)
  return data
}

export async function cancelAppointment(id: string): Promise<AppointmentOut> {
  const { data } = await apiClient.post<AppointmentOut>(`/appointments/${id}/cancel`)
  return data
}
