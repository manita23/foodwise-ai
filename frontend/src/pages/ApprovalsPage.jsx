import { useEffect, useState } from 'react'
import { api } from '../services/api'

const STATUS_STYLES = {
  pending:  'bg-amber-100 text-amber-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
}

export default function ApprovalsPage() {
  const [recs, setRecs]       = useState([])
  const [filter, setFilter]   = useState('pending')
  const [loading, setLoading] = useState(true)
  const [actioning, setAct]   = useState(null)

  const load = (s) => {
    setLoading(true)
    api.listRecommendations(s || undefined).then(setRecs).finally(() => setLoading(false))
  }

  useEffect(() => { load(filter) }, [filter])

  async function act(id, action) {
    setAct(id)
    try {
      if (action === 'approve') await api.approve(id, 'admin')
      else await api.reject(id, 'admin')
      load(filter)
    } finally { setAct(null) }
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Approval Queue</h1>
        <p className="text-xs text-gray-400">
          All AI recommendations require human sign-off before any action is taken.
        </p>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2">
        {['pending','approved','rejected',''].map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`text-sm px-3 py-1 rounded-full border ${filter === s ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 text-gray-600 hover:bg-gray-50'}`}
          >
            {s || 'all'}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : recs.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center text-gray-400 text-sm">
          No recommendations with status "{filter || 'any'}" yet.
          <br />Ask a question on the <strong>Ask AI</strong> page to generate one.
        </div>
      ) : (
        <div className="space-y-3">
          {recs.map(r => (
            <div key={r.id} className="bg-white border border-gray-200 rounded-lg p-4 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800">{r.recommendation}</p>
                  {r.rationale && (
                    <p className="text-xs text-gray-500 mt-1">{r.rationale}</p>
                  )}
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${STATUS_STYLES[r.status] || ''}`}>
                  {r.status}
                </span>
              </div>

              <div className="flex items-center gap-2 text-xs text-gray-400">
                <span>Source: {r.source}</span>
                <span>·</span>
                <span>{r.created_at?.slice(0, 16).replace('T', ' ')}</span>
                {r.reviewed_by && (
                  <>
                    <span>·</span>
                    <span>Reviewed by {r.reviewed_by}</span>
                  </>
                )}
              </div>

              {r.status === 'pending' && (
                <div className="flex gap-2 pt-1">
                  <button
                    onClick={() => act(r.id, 'approve')}
                    disabled={actioning === r.id}
                    className="bg-green-600 text-white text-xs px-3 py-1 rounded hover:bg-green-700 disabled:opacity-50"
                  >
                    ✓ Approve
                  </button>
                  <button
                    onClick={() => act(r.id, 'reject')}
                    disabled={actioning === r.id}
                    className="bg-red-100 text-red-700 text-xs px-3 py-1 rounded hover:bg-red-200 disabled:opacity-50"
                  >
                    ✗ Reject
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
