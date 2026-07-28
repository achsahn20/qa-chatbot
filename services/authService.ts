import { api } from './api'

export interface AuthUser {
  id: string
  full_name: string
  email: string
  role: 'user' | 'admin'
  is_active: boolean
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export const authService = {
  signup: async (payload: { full_name: string; email: string; password: string }) => {
    const { data } = await api.post<AuthResponse>('/auth/signup', payload)
    return data
  },
  login: async (payload: { email: string; password: string }) => {
    const { data } = await api.post<AuthResponse>('/auth/login', payload)
    return data
  },
  me: async () => {
    const { data } = await api.get<AuthUser>('/auth/me')
    return data
  },
}
