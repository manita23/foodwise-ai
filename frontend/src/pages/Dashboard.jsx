import { useEffect, useState, memo } from 'react'
import { api } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const StatCard = memo(function StatCard({ label, value, sub, color = 'blue' }) {
  const colors = { blue: 'border-blue-500 bg-blue-50', green: 'border-green-500 bg-green-50', amber: 'border-amber-500 bg-amber-50', red: 'border-red-500 bg-red-50' }
  return (
    <div className={`rounded-lg border-l-4 p-4 ${colors[color]}`}>
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
})

export default function Dashboard() {
  const [trends, setTrends]         = useState([])
  const [forecast, setForecast]     = useState(null)
  const [pending, setPending]       = useState(0)
  const [loading, setLoading]       = useState(true)

  useEffect(() => {
    Promise.all([
      api.trends(30),
      api.forecast({ meal_type: 'lunch', horizon_meals: 3 }),
      api.listRecommendations('pending'),
    ]).then(([t, f, recs]) => {
      setTrends(t.data || [])
      setForecast(f)
      setPending(recs.length)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-gray-400">Loading dashboard…</p>

  // Use last 7 days of available data for chart; all available data for stats
  const chartData = trends.slice(-7)
  const totalWaste = trends.reduce((s, d) => s + d.total_waste_kg, 0).toFixed(1)
  const avgWastePct = trends.length
    ? (trends.reduce((s, d) => s + d.waste_pct, 0) / trends.length).toFixed(1)
    : '—'
  const nextMeal = forecast?.forecast?.[0]

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Dashboard</h1>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label={`${trends.length}-day total waste`} value={`${totalWaste} kg`} color="red" />
        <StatCard label="Avg waste %" value={avgWastePct !== '—' ? `${avgWastePct}%` : '—'} color="amber" />
        <StatCard
          label="Next meal forecast"
          value={nextMeal ? `${nextMeal.predicted_kg} kg` : '—'}
          sub={forecast?.meal_type}
          color="blue"
        />
        <StatCard
          label="Pending approvals"
          value={pending}
          sub="recommendations awaiting review"
          color={pending > 0 ? 'amber' : 'green'}
        />
      </div>

      {/* 7-day waste chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-sm font-semibold text-gray-600 mb-3">Recent Waste vs Consumption (kg)</h2>
        {chartData.length === 0 ? (
          <p className="text-sm text-gray-400">No trend data yet. Import some historical data.</p>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} barGap={2}>
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="total_consumption_kg" name="Consumption" fill="#93c5fd" radius={[3,3,0,0]} />
              <Bar dataKey="total_waste_kg" name="Waste" fill="#fca5a5" radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Forecast summary */}
      {forecast && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-600 mb-1">
            Next {forecast.forecast.length} {forecast.meal_type} meals — demand forecast
          </h2>
          <p className="text-xs text-gray-400 mb-3">Model: {forecast.model_used} · Mode: {forecast.mode}</p>
          <div className="flex gap-4 flex-wrap">
            {forecast.forecast.map((p) => (
              <div key={p.label} className="bg-blue-50 rounded p-3 min-w-28">
                <p className="text-xs text-gray-500">{p.label}</p>
                <p className="font-semibold">{p.predicted_kg} kg</p>
                <p className={`text-xs ${p.surplus_kg > 0 ? 'text-amber-600' : 'text-green-600'}`}>
                  surplus {p.surplus_kg} kg
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
