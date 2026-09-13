import { useState } from 'react'
import { api } from '../api'

export default function RestorationForm({ zones = [], onCreated }) {
  const [form, setForm] = useState({
    zone_id: '',
    activity_date: new Date().toISOString().slice(0, 10),
    activity_type: 'planting',
    area_hectares: '',
    logged_by: '',
  })
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setStatus('')
    try {
      const row = await api.createRestoration({
        ...form,
        zone_id: Number(form.zone_id),
        area_hectares: Number(form.area_hectares),
        logged_by: form.logged_by || null,
      })
      setStatus(`Logged restoration #${row.id}`)
      onCreated?.(row)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form
      onSubmit={onSubmit}
      className="rounded-lg border border-watershed-deep/10 bg-white p-4 shadow-sm"
    >
      <h3 className="font-display text-lg font-semibold text-watershed-deep">
        Log restoration activity
      </h3>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
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
          Date
          <input
            type="date"
            className="mt-1 w-full rounded border border-watershed-deep/20 px-2 py-1.5"
            value={form.activity_date}
            onChange={(e) => setForm({ ...form, activity_date: e.target.value })}
            required
          />
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
          Area (hectares)
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
        <label className="text-sm sm:col-span-2">
          Logged by (optional)
          <input
            type="text"
            className="mt-1 w-full rounded border border-watershed-deep/20 px-2 py-1.5"
            value={form.logged_by}
            onChange={(e) => setForm({ ...form, logged_by: e.target.value })}
          />
        </label>
      </div>
      <button
        type="submit"
        className="mt-4 rounded bg-watershed-mid px-4 py-2 text-sm font-semibold text-white hover:bg-watershed-deep"
      >
        Save
      </button>
      {status && <p className="mt-2 text-sm text-green-700">{status}</p>}
      {error && <p className="mt-2 text-sm text-red-700">{error}</p>}
    </form>
  )
}
