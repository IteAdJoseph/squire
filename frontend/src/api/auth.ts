import { apiClient } from './client'

export interface LoginRequest {
  tenant_slug: string
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface MeResponse {
  id: string
  username: string
  email: string
  role: 'owner' | 'admin' | 'operator'
  tenant_id: string
  tenant_name: string
  billing_status: string | null
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>('/auth/login', data)
  return res.data
}

export async function getMe(): Promise<MeResponse> {
  const res = await apiClient.get<MeResponse>('/auth/me')
  return res.data
}
