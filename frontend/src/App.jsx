import { useEffect, useMemo, useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import { api } from './api'
import AlertBanner from './components/AlertBanner'
import AttributionFooter from './components/AttributionFooter'
import CarbonCalculator from './components/CarbonCalculator'
import HealthScoreCard from './components/HealthScoreCard'
import MapView from './components/MapView'
import RestorationForm from './components/RestorationForm'
import TrendChart from './components/TrendChart'
import { PrivacyPage, TermsPage } from './pages/Legal'

function Dashboard() {
  const [zones, setZones] = useState([])
  const [alerts, setAlerts] = useState([])
  const [scores, setScores] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.getWatersheds(), api.getAlerts()])
      .then(([z, a]) => {
        setZones(z)
        setAlerts(a)
        if (z.length) setSelectedId(z[0].id)
      })
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    if (!selectedId) return
    api
      .getScores(selectedId)
      .then(setScores)
      .catch(() => setScores([]))
  }, [selectedId])

  const selected = useMemo(
    () => zones.find((z) => z.id === selectedId) || null,
    [zones, selectedId],
  )

  return (
    <div className="flex min-h-full flex-col bg-gradient-to-b from-watershed-mist via-white to-watershed-sand/40">
      <header className="border-b border-watershed-deep/10 bg-white/70 px-4 py-4 backdrop-blur">
        <h1 className="font-display text-2xl font-bold tracking-tight text-watershed-deep sm:text-3xl">
          WatershedOS
        </h1>
        <p className="text-sm text-watershed-deep/70">
          Watershed degradation intelligence for East Africa
        </p>
      </header>

      <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-4 p-4">
        {error && (
          <p className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
            {error} — is the API running at {import.meta.env.VITE_API_URL || 'http://localhost:8000'}?
          </p>
        )}
        <AlertBanner alerts={alerts} />

        <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
          <div className="h-[420px] lg:h-auto lg:min-h-[520px]">
            <MapView zones={zones} selectedId={selectedId} onSelect={setSelectedId} />
          </div>
          <HealthScoreCard zone={selected} />
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <TrendChart scores={scores} zoneName={selected?.name} />
          <RestorationForm zones={zones} />
        </div>

        <CarbonCalculator zones={zones} />
      </main>

      <AttributionFooter />
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/terms" element={<TermsPage />} />
    </Routes>
  )
}
