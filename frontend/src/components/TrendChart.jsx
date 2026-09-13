import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export default function TrendChart({ scores = [], zoneName }) {
  const data = scores.map((s) => ({
    date: s.score_date,
    score: s.health_score != null ? Number(s.health_score) : null,
  }))

  return (
    <div className="rounded-lg border border-watershed-deep/10 bg-white p-4 shadow-sm">
      <h3 className="font-display text-lg font-semibold text-watershed-deep">
        12-month health trend
      </h3>
      <p className="mb-3 text-sm text-watershed-deep/60">{zoneName || 'Select a zone'}</p>
      {data.length === 0 ? (
        <p className="text-sm text-watershed-deep/60">No score history yet.</p>
      ) : (
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d1d5db" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#1a5c45"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
