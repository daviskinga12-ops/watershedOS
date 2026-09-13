import { useState } from 'react'
import { api } from '../api'

export default function CarbonCalculator({ zones = [] }) {
  const [form, setForm] = useState({
    zone_id: '',
    activity_type: 'planting',
    area_hectares: '',
    ndvi_mean: '0.4',
  })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      const out = await api.estimateCarbon({
        zone_id: Number(form.zone_id),
        activity_type: form.activity_type,
        area_hectares: Number(form.area_hectares),
        ndvi_mean: Number(form.ndvi_mean),
      })
      setResult(out)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="rounded-lg border border-watershed-deep/10 bg-white p-4 shadow-sm">
      <h3 className="font-display text-lg font-semibold text-watershed-deep">
        Carbon credit calculator
      </h3>
      <p className="mt-1 rounded bg-amber-50 px-2 py-1 text-xs text-amber-900">
        Estimate — pending VM0047 methodology. Placeholder only; not Verra-compliant.
      </p>
      <form onSubmit={onSubmit} className="mt-3 grid gap-3 sm:grid-cols-2">
        <label className="text-sm">
          Zone
          <select
            className="mt-1 w-full rounded border border-watershed-deep/20 px-2 py-1.5"
            value={form.zone_id}
            onChange={(e) => setForm({ ...form, zone_id: e.target.value })}
            required
          >
            <option value="">Select…</option>
            {zones.map((z) => (
              <option key={z.id} value={z.id}>
                {z.name}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Activity
          <select
            className="mt-1 w-full rounded border border-watershed-deep/20 px-2 py-1.5"
            value={form.activity_type}
            onChange={(e) => setForm({ ...form, activity_type: e.target.value })}
          >
            <option value="planting">Planting</option>
            <option value="gabion">Gabion</option>
            <option value="terrace">Terrace</option>
          </select>
        </label>
        <label className="text-sm">
          Area (ha)
          <input
            type="number"
            min="0.01"
            step="0.01"
            className="mt-1 w-full rounded border border-watershed-deep/20 px-2 py-1.5"
            value={form.area_hectares}
            onChange={(e) => setForm({ ...form, area_hectares: e.target.value })}
            required
          />
        </label>
        <label className="text-sm">
          NDVI mean (proxy)
          <input
            type="number"
            min="-1"
            max="1"
            step="0.01"
            className="mt-1 w-full rounded border border-watershed-deep/20 px-2 py-1.5"
            value={form.ndvi_mean}
            onChange={(e) => setForm({ ...form, ndvi_mean: e.target.value })}
          />
        </label>
        <button
          type="submit"
          className="sm:col-span-2 rounded bg-watershed-clay px-4 py-2 text-sm font-semibold text-white hover:opacity-90"
        >
          Estimate
        </button>
      </form>
      {error && <p className="mt-2 text-sm text-red-700">{error}</p>}
      {result && (
        <div className="mt-3 space-y-1 text-sm text-watershed-deep">
          <p>
            Verra pathway (proxy): <strong>{result.verra_tco2e}</strong> tCO2e
          </p>
          <p>
            Gold Standard (proxy): <strong>{result.gold_standard_tco2e}</strong> tCO2e
          </p>
          <p>
            Market value (~${result.price_usd_per_tco2e}/t):{' '}
            <strong>${result.estimated_value_usd}</strong>
          </p>
          <p className="text-xs text-amber-800">{result.disclaimer}</p>
        </div>
      )}
    </div>
  )
}
