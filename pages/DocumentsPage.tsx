import { useState } from 'react'
import { PageHeader } from '../components/common/PageHeader'
import { DocumentStatusBadge } from '../components/documents/DocumentStatusBadge'
import { useApiError } from '../hooks/useApiError'
import { useDocuments } from '../hooks/useDocuments'
import { documentService } from '../services/documentService'
import { formatBytes, formatDateTime } from '../utils/formatters'

export const DocumentsPage = () => {
  const { documents, loading, refresh } = useDocuments()
  const [workingId, setWorkingId] = useState<string | null>(null)
  const [error, setError] = useState('')
  const getErrorMessage = useApiError()

  const handleDelete = async (documentId: string) => {
    setWorkingId(documentId)
    setError('')
    try {
      await documentService.remove(documentId)
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setWorkingId(null)
    }
  }

  const handleReprocess = async (documentId: string) => {
    setWorkingId(documentId)
    setError('')
    try {
      await documentService.process(documentId, true)
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setWorkingId(null)
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Library"
        title="Uploaded documents"
        description="Track file status, inspect processing outcomes, and re-run indexing when a document changes."
      />

      {error ? <p className="mb-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}

      <div className="overflow-hidden rounded-3xl border border-slate-200">
        <table className="min-w-full bg-white text-left">
          <thead className="bg-slate-50 text-sm text-slate-500">
            <tr>
              <th className="px-4 py-3 font-medium">File</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Pages</th>
              <th className="px-4 py-3 font-medium">Size</th>
              <th className="px-4 py-3 font-medium">Uploaded</th>
              <th className="px-4 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((document) => (
              <tr key={document.id} className="border-t border-slate-100 text-sm text-slate-700">
                <td className="px-4 py-4">
                  <div>
                    <p className="font-semibold text-slate-900">{document.original_file_name}</p>
                    {document.processing_error ? <p className="mt-1 text-xs text-rose-600">{document.processing_error}</p> : null}
                  </div>
                </td>
                <td className="px-4 py-4">
                  <DocumentStatusBadge status={document.status} />
                </td>
                <td className="px-4 py-4">{document.page_count ?? '-'}</td>
                <td className="px-4 py-4">{formatBytes(document.file_size)}</td>
                <td className="px-4 py-4">{formatDateTime(document.uploaded_at)}</td>
                <td className="px-4 py-4">
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => handleReprocess(document.id)}
                      disabled={workingId === document.id}
                      className="rounded-xl border border-slate-300 px-3 py-2 text-xs font-semibold transition hover:border-cyan-400 hover:text-cyan-700"
                    >
                      Reprocess
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDelete(document.id)}
                      disabled={workingId === document.id}
                      className="rounded-xl border border-rose-200 px-3 py-2 text-xs font-semibold text-rose-700 transition hover:bg-rose-50"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!loading && documents.length === 0 ? <p className="px-4 py-8 text-sm text-slate-500">No documents uploaded yet.</p> : null}
      </div>
    </div>
  )
}
