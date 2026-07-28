export const ActivityFeed = ({ items }: { items: Array<Record<string, string>> }) => (
  <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
    <h3 className="text-lg font-semibold text-slate-950">Latest activity</h3>
    <div className="mt-4 space-y-4">
      {items.length === 0 ? <p className="text-sm text-slate-500">No activity yet.</p> : null}
      {items.map((item, index) => (
        <div key={`${item.file_name}-${index}`} className="rounded-2xl border border-slate-200 bg-white p-4">
          <p className="text-sm font-semibold text-slate-900">{item.file_name}</p>
          <p className="mt-1 text-sm text-slate-500">Status: {item.status}</p>
          <p className="mt-1 text-xs text-slate-400">{item.uploaded_at}</p>
        </div>
      ))}
    </div>
  </div>
)
