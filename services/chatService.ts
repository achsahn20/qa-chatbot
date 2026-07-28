import { api } from './api'

export interface ChatSessionItem {
  id: string
  user_id: string
  title: string | null
  status: string
  created_at: string
  updated_at: string
  last_message_at: string
}

export interface CitationItem {
  chunk_id: string
  file_name: string
  page_number: number
  quote: string
  score?: number | null
}

export interface ChatMessageItem {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  citations_json?: CitationItem[] | null
  created_at: string
}

export interface ChatAnswerResponse {
  answer: string
  citations: CitationItem[]
  session_id: string
  message_id: string
}

export const chatService = {
  createSession: async (title?: string) => {
    const { data } = await api.post<ChatSessionItem>('/chat/sessions', { title })
    return data
  },
  listSessions: async (params?: { page?: number; limit?: number }) => {
    const { data } = await api.get<{ items: ChatSessionItem[]; total: number; page: number; limit: number }>(
      '/chat/sessions',
      { params },
    )
    return data
  },
  getMessages: async (sessionId: string) => {
    const { data } = await api.get<ChatMessageItem[]>(`/chat/sessions/${sessionId}/messages`)
    return data
  },
  askQuestion: async (sessionId: string, payload: { question: string; document_ids?: string[] }) => {
    const { data } = await api.post<ChatAnswerResponse>(`/chat/sessions/${sessionId}/ask`, payload)
    return data
  },
}
