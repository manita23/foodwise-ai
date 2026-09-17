import { useState } from 'react'
import { api } from '../services/api'

const EXAMPLES = [
  'Is it safe to serve rice that has been in the bain-marie for 4 hours?',
  'How can I reduce lunch waste this week?',
  'What are our allergen labelling requirements?',
]

function AnswerBlock({ answer }) {
  // Highlight RECOMMENDATION: block
  const parts = answer.split(/(RECOMMENDATION:.*)/s)
  return (
    <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
      {parts.map((part, i) =>
        part.startsWith('RECOMMENDATION:') ? (
          <div key={i} className="mt-3 bg-amber-50 border border-amber-300 rounded p-3 text-amber-800 text-sm font-mono">
            {part}
          </div>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </div>
  )
}

export default function QAPage() {
  const [question, setQuestion] = useState('')
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')

  async function submit(q) {
    const text = q || question
    if (!text.trim()) return
    setLoading(true); setResult(null); setError('')
    try {
      const r = await api.qa(text)
      setResult(r)
      setQuestion(text)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-xl font-semibold">Ask AI — powered by IBM Granite</h1>
      <p className="text-sm text-gray-500">
        Ask about food safety, waste reduction, or institutional policy.
        Answers are grounded in your uploaded policy documents.
      </p>

      {/* Example questions */}
      <div className="flex flex-wrap gap-2">
        {EXAMPLES.map(ex => (
          <button
            key={ex}
            onClick={() => { setQuestion(ex); submit(ex) }}
            className="text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-3 py-1 hover:bg-blue-100"
          >
            {ex.length > 55 ? ex.slice(0, 52) + '…' : ex}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <textarea
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit() } }}
          placeholder="Type your question…"
          rows={3}
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
        />
        <button
          onClick={() => submit()}
          disabled={loading || !question.trim()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 self-end"
        >
          {loading ? '…' : 'Ask'}
        </button>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {/* Answer */}
      {result && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xs bg-blue-100 text-blue-700 rounded px-2 py-0.5 font-medium">
              IBM Granite · {result.mode} mode
            </span>
            {result.recommendation_created && (
              <span className="text-xs bg-amber-100 text-amber-700 rounded px-2 py-0.5 font-medium">
                ⚠️ Recommendation created — awaiting approval
              </span>
            )}
          </div>

          <AnswerBlock answer={result.answer} />

          {result.sources?.length > 0 && (
            <div className="text-xs text-gray-400 border-t border-gray-100 pt-2">
              <span className="font-medium">Sources: </span>
              {result.sources.join(' · ')}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
