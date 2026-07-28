import { Link } from 'react-router-dom'
import { APP_NAME } from '../utils/constants'

export const LandingPage = () => (
  <div className="min-h-screen bg-transparent px-4 py-8 text-slate-900">
    <div className="mx-auto max-w-6xl rounded-[2rem] border border-white/70 bg-white/75 px-6 py-8 shadow-2xl shadow-slate-200/70 backdrop-blur md:px-10 md:py-12">
      <header className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.32em] text-cyan-700">Production-Style AI Portfolio Project</p>
          <h1 className="mt-4 text-5xl font-semibold tracking-tight text-slate-950 md:text-6xl">
            {APP_NAME} for policies, contracts, reports, and product documentation.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            Upload business PDFs, generate searchable embeddings, and answer questions with grounded citations that include file name, page number, and matched text.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link to="/signup" className="rounded-2xl bg-cyan-600 px-5 py-3 font-semibold text-white transition hover:bg-cyan-700">
              Start Building
            </Link>
            <Link to="/login" className="rounded-2xl border border-slate-300 px-5 py-3 font-semibold text-slate-700 transition hover:border-cyan-400 hover:text-cyan-700">
              Sign In
            </Link>
          </div>
        </div>
        <div className="grid gap-4 rounded-[2rem] bg-slate-950 p-6 text-slate-100 lg:w-[26rem]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
            <p className="text-sm text-slate-400">Upload pipeline</p>
            <p className="mt-2 text-xl font-semibold">PDF {'->'} parse {'->'} chunk {'->'} embed {'->'} cite</p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
            <p className="text-sm text-slate-400">Target teams</p>
            <p className="mt-2 text-sm leading-6 text-slate-200">
              Law firms, HR teams, hospitals, SaaS support teams, training departments, and knowledge-base operations.
            </p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
            <p className="text-sm text-slate-400">Core promise</p>
            <p className="mt-2 text-sm leading-6 text-slate-200">
              No black-box answers. Every response stays grounded in uploaded documents and points back to evidence.
            </p>
          </div>
        </div>
      </header>

      <section className="mt-12 grid gap-4 md:grid-cols-3">
        {[
          ['Secure workspaces', 'JWT auth, user-isolated documents, and role-based admin visibility.'],
          ['Grounded RAG', 'Page-level parsing, chunk retrieval, and answer generation with source references.'],
          ['Business-ready workflow', 'Upload, index, query, review citations, and inspect usage analytics in one dashboard.'],
        ].map(([title, description]) => (
          <div key={title} className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
            <h2 className="text-xl font-semibold text-slate-950">{title}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
          </div>
        ))}
      </section>
    </div>
  </div>
)
