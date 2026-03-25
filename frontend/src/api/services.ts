import { apiClient } from './client'

export interface ServiceOut {
  id: string
  tenant_id: string
  name: string
  duration_minutes: number
  total_price: string
  deposit_amount: string
  is_active: boolean
  created_at: string
}

export interface ServiceCreateIn {
  name: string
  duration_minutes: number
  total_price: number
  deposit_amount?: number
}

export async function listServices(): Promise<ServiceOut[]> {
  const { data } = await apiClient.get<ServiceOut[]>('/services')
  return data
}

export async function createService(body: ServiceCreateIn): Promise<ServiceOut> {
  const { data } = await apiClient.post<ServiceOut>('/services', body)
  return data
}
