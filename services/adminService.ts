import { api } from './api'
import type { DocumentItem } from './documentService'
import type { AuthUser } from './authService'

export const adminService = {
  dashboard: async () => {
    const { data } = await api.get('/admin/dashboard')
    return data
  },
  analytics: async (range = '30d') => {
    const { data } = await api.get('/admin/analytics', { params: { range } })
    return data
  },
  users: async () => {
    const { data } = await api.get<{ items: AuthUser[]; total: number; page: number; limit: number }>('/admin/users')
    return data
  },
  documents: async () => {
    const { data } = await api.get<{ items: DocumentItem[]; total: number; page: number; limit: number }>(
      '/admin/documents',
    )
    return data
  },
}
