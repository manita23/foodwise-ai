import { useState } from 'react'
import { api } from '../services/api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

export default function ForecastPage() {
  const [mealType, setMealType] = useState('lunch')
  const [horizon, setHorizon]   = useState(3)
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')

  async function runForecast() {
    setLoading(true); setError('')
    try {
      const r = await api.forecast({ meal_type: mealType, horizon_meals: horizon })
      setResult(r)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const chartData = result?.forecast.map((p, i) => ({
    name: p.label,
    'Predicted (kg)': p.predicted_kg,
    'Surplus (kg)': p.surplus_kg,
  })) ?? []

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-xl font-semibold">Demand Forecast</h1>

      <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
        <div className="flex gap-4 flex-wrap items-end">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Meal type</label>
            <select
              value={mealType}
              onChange={e => setMealType(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              {['breakfast','lunch','dinner','snack'].map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Horizon (meals)</label>
            <input
              type="number" min={1} max={10} value={horizon}
              onChange={e => setHorizon(Number(e.target.value))}
              className="border border-gray-300 rounded px-2 py-1 text-sm w-20"
            />
          </div>
          <button
            onClick={runForecast}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Running…' : 'Run Forecast'}
          </button>
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        {result && (
          <>
            <p className="text-xs text-gray-400">
              Model: {result.model_used} · Mode: {result.mode}
            </p>
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={chartData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <ReferenceLine y={0} stroke="#e5e7eb" />
                <Line type="monotone" dataKey="Predicted (kg)" stroke="#3b82f6" strokeWidth={2} dot />
                <Line type="monotone" dataKey="Surplus (kg)" stroke="#f59e0b" strokeWidth={2} dot strokeDasharray="4 2" />
              </LineChart>
            </ResponsiveContainer>

            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-50 text-xs text-gray-500 uppercase">
                  <th className="text-left px-3 py-2">Meal</th>
                  <th className="text-right px-3 py-2">Predicted (kg)</th>
                  <th className="text-right px-3 py-2">Surplus (kg)</th>
                </tr>
              </thead>
              <tbody>
                {result.forecast.map(p => (
                  <tr key={p.label} className="border-t border-gray-100">
                    <td className="px-3 py-2">{p.label}</td>
                    <td className="px-3 py-2 text-right">{p.predicted_kg}</td>
                    <td className={`px-3 py-2 text-right font-medium ${p.surplus_kg > 0 ? 'text-amber-600' : 'text-green-600'}`}>
                      {p.surplus_kg}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </div>
    </div>
  )
}
