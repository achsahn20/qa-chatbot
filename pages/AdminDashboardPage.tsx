import { useEffect, useState } from 'react'
import { ActivityFeed } from '../components/admin/ActivityFeed'
import { PageHeader } from '../components/common/PageHeader'
import { StatCard } from '../components/dashboard/StatCard'
import { adminService } from '../services/adminService'

export const AdminDashboardPage = () => {
  const [dashboard, setDashboard] = useState<any>(null)
  const [analytics, setAnalytics] = useState<any>(null)

  useEffect(() => {
    const load = async () => {
      const [dashboardData, analyticsData] = await Promise.all([
        adminService.dashboard(),
        adminService.analytics('30d'),
      ])
      setDashboard(dashboardData)
      setAnalytics(analyticsData)
    }
    void load()
  }, [])

  const totals = dashboard?.totals

  return (
    <div>
      <PageHeader
        eyebrow="Admin"
        title="Platform monitoring"
        description="Inspect overall user activity, document throughput, and assistant usage from a single administrative view."
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Users" value={totals?.total_users ?? '...'} hint="Registered accounts" />
        <StatCard label="Documents" value={totals?.total_documents ?? '...'} hint="Stored PDFs" />
        <StatCard label="Ready indexes" value={totals?.ready_documents ?? '...'} hint="Searchable documents" />
        <StatCard label="Answers generated" value={analytics?.summary?.answers_generated ?? '...'} hint="Assistant output volume" />
      </div>

      <div className="mt-8 grid gap-4 xl:grid-cols-[1.15fr,0.85fr]">
        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
          <h3 className="text-lg font-semibold text-slate-950">30-day usage summary</h3>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="text-sm text-slate-500">Documents uploaded</p>
              <p className="mt-3 text-3xl font-semibold text-slate-950">{analytics?.summary?.documents_uploaded ?? '...'}</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="text-sm text-slate-500">Average latency</p>
              <p className="mt-3 text-3xl font-semibold text-slate-950">{analytics?.summary?.average_latency_ms ?? '...'} ms</p>
            </div>
          </div>
          <div className="mt-5 rounded-2xl border border-slate-200 bg-white p-4">
            <p className="text-sm font-semibold text-slate-900">Daily uploads</p>
            <div className="mt-3 space-y-2">
              {analytics?.uploads?.map((item: { date: string; count: number }) => (
                <div key={item.date} className="flex items-center justify-between text-sm text-slate-600">
                  <span>{item.date}</span>
                  <span className="font-semibold text-slate-900">{item.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <ActivityFeed items={dashboard?.latest_activity ?? []} />
      </div>
    </div>
  )
}
