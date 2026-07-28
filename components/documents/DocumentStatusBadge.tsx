interface DocumentStatusBadgeProps {
  status: string
}

const statusMap: Record<string, string> = {
  uploaded: 'bg-amber-100 text-amber-700',
  processing: 'bg-sky-100 text-sky-700',
  ready: 'bg-emerald-100 text-emerald-700',
  failed: 'bg-rose-100 text-rose-700',
}

export const DocumentStatusBadge = ({ status }: DocumentStatusBadgeProps) => (
  <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusMap[status] ?? 'bg-slate-100 text-slate-600'}`}>
    {status}
  </span>
)
