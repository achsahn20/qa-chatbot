import { useEffect, useState } from 'react'
import { documentService, type DocumentItem } from '../services/documentService'

export const useDocuments = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)

  const refresh = async () => {
    setLoading(true)
    try {
      const response = await documentService.list({ page: 1, limit: 50 })
      setDocuments(response.items)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void refresh()
  }, [])

  return { documents, loading, refresh }
}
