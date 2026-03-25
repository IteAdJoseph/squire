import { apiClient } from './client'

export interface CustomerOut {
  id: string
  tenant_id: string
  name: string
  phone: string
  notes: string | null
  is_active: boolean
  created_at: string
}

export interface CustomerCreateIn {
  name: string
  phone: string
  notes?: string
}

export async function listCustomers(): Promise<CustomerOut[]> {
  const { data } = await apiClient.get<CustomerOut[]>('/customers')
  return data
}

export async function createCustomer(body: CustomerCreateIn): Promise<CustomerOut> {
  const { data } = await apiClient.post<CustomerOut>('/customers', body)
  return data
}
