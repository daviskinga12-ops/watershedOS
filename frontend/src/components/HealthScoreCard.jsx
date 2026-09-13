function scoreColor(score) {
  if (score == null) return '#9ca3af'
  if (score <= 40) return '#dc2626'
  if (score <= 70) return '#ea580c'
  return '#16a34a'
}

export default function HealthScoreCard({ zone, score }) {
  const value = score ?? zone?.latest_health_score
  return (
    <div className="rounded-lg border border-watershed-deep/10 bg-white p-4 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-watershed-deep/60">Health score</p>
      <h2 className="font-display text-xl font-semibold text-watershed-deep">
        {zone?.name || 'Select a zone'}
      </h2>
      <div className="mt-3 flex items-end gap-3">
        <span
          className="font-display text-4xl font-bold tabular-nums"
          style={{ color: scoreColor(value) }}
        >
          {value != null ? Number(value).toFixed(1) : '—'}
        </span>
        <span className="mb-1 text-sm text-watershed-deep/60">/ 100</span>
      </div>
      <p className="mt-2 text-sm text-watershed-deep/70">
        Zone type: {zone?.zone_type || '—'} · Zone-level aggregate only
      </p>
      <div className="mt-3 flex gap-2 text-xs">
        <span className="inline-flex items-center gap-1">
          <span className="h-2 w-2 rounded-sm bg-red-600" /> 0–40
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="h-2 w-2 rounded-sm bg-orange-600" /> 41–70
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="h-2 w-2 rounded-sm bg-green-600" /> 71–100
        </span>
      </div>
    </div>
  )
}
