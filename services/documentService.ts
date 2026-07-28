import { api } from './api'

export interface DocumentItem {
  id: string
  owner_id: string
  original_file_name: string
  mime_type: string
  file_size: number
  page_count: number | null
  status: string
  processing_error: string | null
  uploaded_at: string
  processed_at: string | null
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}

export const documentService = {
  upload: async (files: File[]) => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    const { data } = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
  list: async (params?: { page?: number; limit?: number; status?: string; search?: string }) => {
    const { data } = await api.get<PaginatedResponse<DocumentItem>>('/documents', { params })
    return data
  },
  get: async (documentId: string) => {
    const { data } = await api.get<DocumentItem>(`/documents/${documentId}`)
    return data
  },
  remove: async (documentId: string) => {
    const { data } = await api.delete(`/documents/${documentId}`)
    return data
  },
  process: async (documentId: string, force_reprocess = false) => {
    const { data } = await api.post(`/documents/${documentId}/process`, { force_reprocess })
    return data
  },
}
