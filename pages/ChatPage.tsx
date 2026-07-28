import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { CitationCard } from '../components/chat/CitationCard'
import { MessageBubble } from '../components/chat/MessageBubble'
import { PageHeader } from '../components/common/PageHeader'
import { useApiError } from '../hooks/useApiError'
import { useChatSessions } from '../hooks/useChat'
import { useDocuments } from '../hooks/useDocuments'
import { chatService, type ChatMessageItem, type CitationItem } from '../services/chatService'

export const ChatPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const activeSessionId = searchParams.get('session')
  const { sessions, refresh: refreshSessions } = useChatSessions()
  const { documents } = useDocuments()
  const getErrorMessage = useApiError()

  const [messages, setMessages] = useState<ChatMessageItem[]>([])
  const [question, setQuestion] = useState('')
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([])
  const [citations, setCitations] = useState<CitationItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadMessages = async () => {
      if (!activeSessionId) {
        setMessages([])
        return
      }
      try {
        const data = await chatService.getMessages(activeSessionId)
        setMessages(data)
        const lastAssistant = [...data].reverse().find((message) => message.role === 'assistant')
        setCitations(lastAssistant?.citations_json ?? [])
      } catch (err) {
        setError(getErrorMessage(err))
      }
    }

    void loadMessages()
  }, [activeSessionId, getErrorMessage])

  const readyDocuments = useMemo(() => documents.filter((item) => item.status === 'ready'), [documents])

  const ensureSession = async () => {
    if (activeSessionId) {
      return activeSessionId
    }
    const session = await chatService.createSession('New RAG session')
    await refreshSessions()
    setSearchParams({ session: session.id })
    return session.id
  }

  const handleAsk = async () => {
    if (!question.trim()) {
      return
    }
    setError('')
    setLoading(true)
    try {
      const sessionId = await ensureSession()
      const prompt = question
      setMessages((current) => [
        ...current,
        {
          id: `temp-user-${Date.now()}`,
          session_id: sessionId,
          role: 'user',
          content: prompt,
          created_at: new Date().toISOString(),
        },
      ])
      setQuestion('')
      const response = await chatService.askQuestion(sessionId, {
        question: prompt,
        document_ids: selectedDocumentIds.length ? selectedDocumentIds : undefined,
      })
      const refreshed = await chatService.getMessages(sessionId)
      setMessages(refreshed)
      setCitations(response.citations)
      await refreshSessions()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Ask"
        title="Grounded document chatbot"
        description="Select one or more indexed documents, ask a question in plain English, and review the answer with supporting citations."
      />

      <div className="grid gap-6 xl:grid-cols-[0.95fr,1.3fr,0.95fr]">
        <section className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-950">Sessions</h3>
            <button
              type="button"
              onClick={async () => {
                const session = await chatService.createSession('New session')
                await refreshSessions()
                setSearchParams({ session: session.id })
              }}
              className="rounded-xl bg-slate-950 px-3 py-2 text-xs font-semibold text-white"
            >
              New
            </button>
          </div>
          <div className="mt-4 space-y-3">
            {sessions.map((session) => (
              <button
                key={session.id}
                type="button"
                onClick={() => setSearchParams({ session: session.id })}
                className={`w-full rounded-2xl border px-4 py-3 text-left transition ${
                  activeSessionId === session.id ? 'border-cyan-400 bg-white' : 'border-slate-200 bg-white/80'
                }`}
              >
                <p className="font-medium text-slate-900">{session.title || 'Untitled session'}</p>
                <p className="mt-1 text-xs text-slate-500">{new Date(session.last_message_at).toLocaleString()}</p>
              </button>
            ))}
            {sessions.length === 0 ? <p className="text-sm text-slate-500">Create your first session to start chatting.</p> : null}
          </div>
        </section>

        <section className="flex min-h-[38rem] flex-col rounded-3xl border border-slate-200 bg-white">
          <div className="border-b border-slate-200 px-5 py-4">
            <p className="text-sm text-slate-500">Scoped documents</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {readyDocuments.map((document) => {
                const selected = selectedDocumentIds.includes(document.id)
                return (
                  <button
                    key={document.id}
                    type="button"
                    onClick={() =>
                      setSelectedDocumentIds((current) =>
                        selected ? current.filter((item) => item !== document.id) : [...current, document.id],
                      )
                    }
                    className={`rounded-full px-3 py-2 text-xs font-semibold transition ${
                      selected ? 'bg-cyan-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {document.original_file_name}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto px-5 py-5">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {messages.length === 0 ? <p className="text-sm text-slate-500">Ask about policies, clauses, deadlines, pricing, or procedures inside your uploaded PDFs.</p> : null}
          </div>

          <div className="border-t border-slate-200 px-5 py-4">
            {error ? <p className="mb-3 text-sm text-rose-600">{error}</p> : null}
            <div className="flex gap-3">
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask a grounded question about your uploaded documents..."
                rows={3}
                className="flex-1 rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-cyan-500"
              />
              <button
                type="button"
                onClick={handleAsk}
                disabled={loading}
                className="rounded-2xl bg-cyan-600 px-5 py-3 font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-60"
              >
                {loading ? 'Thinking...' : 'Ask'}
              </button>
            </div>
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
          <h3 className="text-lg font-semibold text-slate-950">Source references</h3>
          <div className="mt-4 space-y-4">
            {citations.map((citation) => (
              <CitationCard key={citation.chunk_id} citation={citation} />
            ))}
            {citations.length === 0 ? <p className="text-sm text-slate-500">Citations will appear here after the assistant answers.</p> : null}
          </div>
        </section>
      </div>
    </div>
  )
}
