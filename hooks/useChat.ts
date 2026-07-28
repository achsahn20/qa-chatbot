import { useEffect, useState } from 'react'
import { chatService, type ChatSessionItem } from '../services/chatService'

export const useChatSessions = () => {
  const [sessions, setSessions] = useState<ChatSessionItem[]>([])
  const [loading, setLoading] = useState(true)

  const refresh = async () => {
    setLoading(true)
    try {
      const response = await chatService.listSessions({ page: 1, limit: 50 })
      setSessions(response.items)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void refresh()
  }, [])

  return { sessions, loading, refresh }
}
