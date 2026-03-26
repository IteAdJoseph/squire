import { apiClient } from './client'

export type BillingStatus = 'trial' | 'active' | 'grace' | 'late' | 'suspended' | 'cancelled'
export type AccessStatus = 'enabled' | 'disabled'
export type UserRole = 'owner' | 'admin' | 'operator'

export interface TenantOut {
  id: string
  name: string
  slug: string
  access_status: AccessStatus
  created_at: string
}

export interface UserOut {
  id: string
  tenant_id: string
  email: string
  username: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface BillingOut {
  id: string
  tenant_id: string
  plan: string
  monthly_price: string
  due_day: number
  grace_days: number
  billing_status: BillingStatus
  provider: string
  current_period_start: string
  current_period_end: string
  next_due_date: string
  cancelled_at: string | null
  created_at: string
  updated_at: string
}

export interface TenantListItem {
  id: string
  name: string
  slug: string
  access_status: AccessStatus
  billing_status: BillingStatus | null
  created_at: string
}

export interface TenantDetail {
  tenant: TenantOut
  user: UserOut | null
  billing: BillingOut | null
}

export interface CreateTenantIn {
  name: string
  slug: string
}

export interface CreateUserIn {
  email: string
  username: string
  password: string
  role?: UserRole
}

export interface CreateBillingIn {
  plan: string
  monthly_price: number
  due_day: number
  grace_days?: number
  provider?: string
  billing_status: 'trial' | 'active'
}

export interface PaymentIn {
  amount: number
  paid_at: string
  notes?: string
}

export async function listTenants(): Promise<TenantListItem[]> {
  const { data } = await apiClient.get<TenantListItem[]>('/admin/tenants')
  return data
}

export async function getTenant(id: string): Promise<TenantDetail> {
  const { data } = await apiClient.get<TenantDetail>(`/admin/tenants/${id}`)
  return data
}

export async function createTenant(body: CreateTenantIn): Promise<TenantOut> {
  const { data } = await apiClient.post<TenantOut>('/admin/tenants', body)
  return data
}

export async function createUser(tenantId: string, body: CreateUserIn): Promise<UserOut> {
  const { data } = await apiClient.post<UserOut>(`/admin/tenants/${tenantId}/users`, body)
  return data
}

export async function configureBilling(tenantId: string, body: CreateBillingIn): Promise<BillingOut> {
  const { data } = await apiClient.post<BillingOut>(`/admin/tenants/${tenantId}/billing`, body)
  return data
}

export async function registerPayment(tenantId: string, body: PaymentIn): Promise<BillingOut> {
  const { data } = await apiClient.post<BillingOut>(`/admin/tenants/${tenantId}/billing/payments`, body)
  return data
}

export async function cancelTenant(tenantId: string): Promise<TenantOut> {
  const { data } = await apiClient.post<TenantOut>(`/admin/tenants/${tenantId}/cancel`)
  return data
}
