interface StatCardProps {
  label: string
  value: string | number
  hint: string
}

export const StatCard = ({ label, value, hint }: StatCardProps) => (
  <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
    <p className="text-sm font-medium text-slate-500">{label}</p>
    <p className="mt-4 text-3xl font-semibold text-slate-950">{value}</p>
    <p className="mt-2 text-sm text-slate-500">{hint}</p>
  </div>
)
