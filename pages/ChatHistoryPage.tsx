import { Link } from 'react-router-dom'
import { PageHeader } from '../components/common/PageHeader'
import { useChatSessions } from '../hooks/useChat'
import { formatDateTime } from '../utils/formatters'

export const ChatHistoryPage = () => {
  const { sessions } = useChatSessions()

  return (
    <div>
      <PageHeader
        eyebrow="History"
        title="Session history"
        description="Review prior question threads and reopen any conversation with its saved answer trail."
      />

      <div className="space-y-4">
        {sessions.map((session) => (
          <Link
            key={session.id}
            to={`/chat?session=${session.id}`}
            className="block rounded-3xl border border-slate-200 bg-slate-50 p-5 transition hover:border-cyan-400"
          >
            <p className="text-lg font-semibold text-slate-950">{session.title || 'Untitled session'}</p>
            <p className="mt-2 text-sm text-slate-500">Last updated {formatDateTime(session.last_message_at)}</p>
          </Link>
        ))}
        {sessions.length === 0 ? <p className="text-sm text-slate-500">No sessions yet. Start one from the chat page.</p> : null}
      </div>
    </div>
  )
}
