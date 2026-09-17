import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function WastePage() {
  const [trends, setTrends]     = useState([])
  const [wasteList, setWaste]   = useState([])
  const [meals, setMeals]       = useState([])
  const [form, setForm]         = useState({ meal_id: '', item_name: '', waste_kg: '', waste_category: 'plate_waste' })
  const [msg, setMsg]           = useState('')

  useEffect(() => {
    api.trends(14).then(r => setTrends(r.data || []))
    api.listWaste(30).then(setWaste)
    api.listMeals().then(setMeals)
  }, [])

  async function submit(e) {
    e.preventDefault(); setMsg('')
    if (!form.meal_id || !form.item_name || !form.waste_kg) return
    try {
      await api.recordWaste({ ...form, meal_id: Number(form.meal_id), waste_kg: Number(form.waste_kg) })
      setMsg('Waste record saved.')
      api.listWaste(30).then(setWaste)
      api.trends(14).then(r => setTrends(r.data || []))
    } catch (e) { setMsg('Error: ' + e.message) }
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="text-xl font-semibold">Waste Tracking</h1>

      {/* 14-day trend chart */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h2 className="text-sm font-semibold text-gray-600 mb-3">14-day Waste Trend (kg)</h2>
        {trends.length === 0 ? (
          <p className="text-sm text-gray-400">No trend data yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={trends}>
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Area type="monotone" dataKey="total_waste_kg" name="Waste (kg)" stroke="#ef4444" fill="#fee2e2" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Record waste form */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h2 className="text-sm font-semibold text-gray-600 mb-3">Record Waste</h2>
        <form onSubmit={submit} className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Meal</label>
            <select
              value={form.meal_id}
              onChange={e => setForm(f => ({ ...f, meal_id: e.target.value }))}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              <option value="">Select meal</option>
              {meals.map(m => (
                <option key={m.id} value={m.id}>{m.meal_date} {m.meal_type}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Item name</label>
            <input
              value={form.item_name}
              onChange={e => setForm(f => ({ ...f, item_name: e.target.value }))}
              placeholder="e.g. rice"
              className="border border-gray-300 rounded px-2 py-1 text-sm w-32"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Waste (kg)</label>
            <input
              type="number" step="0.1" min="0" value={form.waste_kg}
              onChange={e => setForm(f => ({ ...f, waste_kg: e.target.value }))}
              className="border border-gray-300 rounded px-2 py-1 text-sm w-24"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Category</label>
            <select
              value={form.waste_category}
              onChange={e => setForm(f => ({ ...f, waste_category: e.target.value }))}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              {['plate_waste','preparation_waste','storage_loss','spoilage'].map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <button type="submit" className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700">
            Save
          </button>
        </form>
        {msg && <p className="mt-2 text-sm text-green-600">{msg}</p>}
      </div>

      {/* Recent waste records */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h2 className="text-sm font-semibold text-gray-600 mb-3">Recent Waste Records (last 30 days)</h2>
        {wasteList.length === 0 ? (
          <p className="text-sm text-gray-400">No records yet.</p>
        ) : (
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase">
                <th className="text-left px-3 py-2">Item</th>
                <th className="text-right px-3 py-2">Waste (kg)</th>
                <th className="text-left px-3 py-2">Category</th>
                <th className="text-left px-3 py-2">Recorded</th>
              </tr>
            </thead>
            <tbody>
              {wasteList.slice(0, 20).map(w => (
                <tr key={w.id} className="border-t border-gray-100">
                  <td className="px-3 py-2">{w.item_name}</td>
                  <td className="px-3 py-2 text-right font-medium text-red-500">{w.waste_kg}</td>
                  <td className="px-3 py-2 text-gray-500">{w.waste_category}</td>
                  <td className="px-3 py-2 text-gray-400 text-xs">{w.recorded_at?.slice(0,10)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
