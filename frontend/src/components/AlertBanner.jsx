export default function AlertBanner({ alerts = [] }) {
  if (!alerts.length) return null

  return (
    <div className="space-y-2">
      {alerts.map((a) => (
        <div
          key={a.id}
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900"
        >
          <strong className="font-semibold">Alert:</strong>{' '}
          {a.alert_type.replaceAll('_', ' ')}
          {a.zone_name ? ` — ${a.zone_name}` : ` — zone ${a.zone_id}`}
          {a.alert_type === 'health_score_low' && ' (health score < 40)'}
        </div>
      ))}
    </div>
  )
}
