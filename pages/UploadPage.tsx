import { useState } from 'react'
import { PageHeader } from '../components/common/PageHeader'
import { useApiError } from '../hooks/useApiError'
import { useDocuments } from '../hooks/useDocuments'
import { documentService } from '../services/documentService'
import { isPdfFile } from '../utils/validators'

export const UploadPage = () => {
  const { refresh } = useDocuments()
  const getErrorMessage = useApiError()
  const [files, setFiles] = useState<File[]>([])
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    setError('')
    setMessage('')
    const validFiles = files.filter(isPdfFile)
    if (!validFiles.length) {
      setError('Select one or more PDF files first.')
      return
    }

    setLoading(true)
    try {
      await documentService.upload(validFiles)
      setFiles([])
      setMessage('Upload successful. Background processing has started.')
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Upload"
        title="Ingest new PDF documents"
        description="Drop policy handbooks, contracts, reports, manuals, invoices, or product documentation to generate searchable retrieval chunks."
      />

      <div className="rounded-[2rem] border border-dashed border-cyan-300 bg-cyan-50/70 p-8">
        <input
          multiple
          type="file"
          accept=".pdf,application/pdf"
          onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
          className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-4"
        />
        <div className="mt-6 flex flex-wrap gap-3">
          {files.map((file) => (
            <span key={file.name} className="rounded-full bg-white px-4 py-2 text-sm text-slate-700 shadow-sm">
              {file.name}
            </span>
          ))}
        </div>
        <div className="mt-6 flex items-center gap-4">
          <button
            type="button"
            onClick={handleUpload}
            disabled={loading}
            className="rounded-2xl bg-slate-950 px-5 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60"
          >
            {loading ? 'Uploading...' : 'Upload and process'}
          </button>
          {message ? <p className="text-sm text-emerald-700">{message}</p> : null}
          {error ? <p className="text-sm text-rose-600">{error}</p> : null}
        </div>
      </div>
    </div>
  )
}
