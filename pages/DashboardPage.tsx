import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { PageHeader } from '../components/common/PageHeader'
import { StatCard } from '../components/dashboard/StatCard'
import { useChatSessions } from '../hooks/useChat'
import { useDocuments } from '../hooks/useDocuments'

export const DashboardPage = () => {
  const { documents, loading: docsLoading } = useDocuments()
  const { sessions, loading: sessionsLoading } = useChatSessions()

  const readyDocuments = useMemo(() => documents.filter((item) => item.status === 'ready').length, [documents])

  return (
    <div>
      <PageHeader
        eyebrow="Overview"
        title="Document intelligence workspace"
        description="Monitor uploads, jump back into recent conversations, and keep your retrieval-ready PDFs organized."
        action={
          <div className="flex gap-3">
            <Link to="/upload" className="rounded-2xl bg-cyan-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700">
              Upload PDFs
            </Link>
            <Link to="/chat" className="rounded-2xl border border-slate-300 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-cyan-400 hover:text-cyan-700">
              Open chat
            </Link>
          </div>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total documents" value={docsLoading ? '...' : documents.length} hint="All PDFs in your workspace" />
        <StatCard label="Ready for Q&A" value={docsLoading ? '...' : readyDocuments} hint="Indexed and searchable" />
        <StatCard label="Chat sessions" value={sessionsLoading ? '...' : sessions.length} hint="Reusable question threads" />
        <StatCard
          label="Needs attention"
          value={docsLoading ? '...' : documents.filter((item) => item.status === 'failed').length}
          hint="Uploads that failed processing"
        />
      </div>

      <div className="mt-8 grid gap-4 xl:grid-cols-[1.35fr,0.95fr]">
        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
          <h3 className="text-xl font-semibold text-slate-950">Recent documents</h3>
          <div className="mt-4 space-y-4">
            {documents.slice(0, 5).map((document) => (
              <div key={document.id} className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3">
                <div>
                  <p className="font-medium text-slate-900">{document.original_file_name}</p>
                  <p className="text-sm text-slate-500">{document.status}</p>
                </div>
                <Link to="/documents" className="text-sm font-semibold text-cyan-700">
                  View
                </Link>
              </div>
            ))}
            {documents.length === 0 ? <p className="text-sm text-slate-500">No documents yet. Upload your first PDF to begin.</p> : null}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
          <h3 className="text-xl font-semibold text-slate-950">Recent sessions</h3>
          <div className="mt-4 space-y-4">
            {sessions.slice(0, 5).map((session) => (
              <Link
                key={session.id}
                to={`/chat?session=${session.id}`}
                className="block rounded-2xl border border-slate-200 bg-white px-4 py-3 transition hover:border-cyan-400"
              >
                <p className="font-medium text-slate-900">{session.title || 'Untitled session'}</p>
                <p className="text-sm text-slate-500">{new Date(session.last_message_at).toLocaleString()}</p>
              </Link>
            ))}
            {sessions.length === 0 ? <p className="text-sm text-slate-500">Create a chat session to start asking questions.</p> : null}
          </div>
        </div>
      </div>
    </div>
  )
}
