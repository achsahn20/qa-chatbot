import { PageHeader } from '../components/common/PageHeader'
import { useAuth } from '../hooks/useAuth'

export const SettingsPage = () => {
  const { user, logout } = useAuth()

  return (
    <div>
      <PageHeader
        eyebrow="Settings"
        title="Profile and workspace details"
        description="Review account information and manage your current authenticated session."
      />

      <div className="grid gap-4 lg:grid-cols-[1.1fr,0.9fr]">
        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
          <h3 className="text-lg font-semibold text-slate-950">Profile</h3>
          <dl className="mt-5 space-y-4 text-sm">
            <div>
              <dt className="text-slate-500">Name</dt>
              <dd className="mt-1 font-medium text-slate-900">{user?.full_name}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Email</dt>
              <dd className="mt-1 font-medium text-slate-900">{user?.email}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Role</dt>
              <dd className="mt-1 font-medium capitalize text-slate-900">{user?.role}</dd>
            </div>
          </dl>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
          <h3 className="text-lg font-semibold text-slate-950">Session</h3>
          <p className="mt-3 text-sm leading-6 text-slate-500">
            Your JWT access token is stored locally in the browser for this demo project. Sign out to clear the local session.
          </p>
          <button
            type="button"
            onClick={logout}
            className="mt-6 rounded-2xl bg-slate-950 px-5 py-3 font-semibold text-white transition hover:bg-slate-800"
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  )
}
