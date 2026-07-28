import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { APP_NAME } from '../../utils/constants'

const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
  `rounded-xl px-4 py-2 text-sm font-medium transition ${
    isActive ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-900/20' : 'text-slate-600 hover:bg-white/80'
  }`

export const AppShell = () => {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-transparent text-slate-900">
      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 lg:px-6">
        <aside className="hidden w-72 shrink-0 rounded-3xl border border-white/70 bg-white/70 p-5 backdrop-blur xl:block">
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-700">Workspace</p>
            <h1 className="mt-2 text-2xl font-semibold text-slate-900">{APP_NAME}</h1>
            <p className="mt-2 text-sm text-slate-500">Upload PDFs, retrieve grounded answers, and monitor usage.</p>
          </div>

          <nav className="flex flex-col gap-2">
            <NavLink to="/dashboard" className={navLinkClasses}>
              Dashboard
            </NavLink>
            <NavLink to="/upload" className={navLinkClasses}>
              Upload
            </NavLink>
            <NavLink to="/documents" className={navLinkClasses}>
              Documents
            </NavLink>
            <NavLink to="/chat" className={navLinkClasses}>
              Chat
            </NavLink>
            <NavLink to="/history" className={navLinkClasses}>
              History
            </NavLink>
            {user?.role === 'admin' ? (
              <NavLink to="/admin" className={navLinkClasses}>
                Admin
              </NavLink>
            ) : null}
            <NavLink to="/settings" className={navLinkClasses}>
              Settings
            </NavLink>
          </nav>

          <div className="mt-8 rounded-2xl bg-slate-950 p-4 text-sm text-slate-100">
            <p className="font-semibold">{user?.full_name}</p>
            <p className="mt-1 text-slate-400">{user?.email}</p>
            <button
              type="button"
              onClick={logout}
              className="mt-4 w-full rounded-xl border border-slate-700 px-3 py-2 text-left text-sm transition hover:border-cyan-400 hover:text-cyan-300"
            >
              Sign out
            </button>
          </div>
        </aside>

        <main className="min-h-[calc(100vh-3rem)] flex-1 rounded-[2rem] border border-white/70 bg-white/75 p-4 shadow-2xl shadow-slate-200/70 backdrop-blur md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
