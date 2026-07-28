import type { CitationItem } from '../../services/chatService'

export const CitationCard = ({ citation }: { citation: CitationItem }) => (
  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
    <div className="flex items-center justify-between gap-3">
      <p className="text-sm font-semibold text-slate-900">{citation.file_name}</p>
      <span className="rounded-full bg-cyan-100 px-2 py-1 text-xs font-medium text-cyan-700">Page {citation.page_number}</span>
    </div>
    <p className="mt-3 text-sm leading-6 text-slate-600">{citation.quote}</p>
  </div>
)
