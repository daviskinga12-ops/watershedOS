const YEAR = new Date().getFullYear()

export default function AttributionFooter() {
  return (
    <footer className="border-t border-watershed-deep/10 bg-white/80 px-4 py-3 text-xs text-watershed-deep/70">
      <p>Contains modified Copernicus Sentinel data [{YEAR}]</p>
      <p>CHIRPS data from Climate Hazards Center, UCSB</p>
      <p>OpenLandMap soil data © OpenLandMap contributors — Creative Commons CC BY 4.0</p>
      <p className="mt-1">
        <a className="underline" href="/privacy">
          Privacy Policy
        </a>
        {' · '}
        <a className="underline" href="/terms">
          Terms of Service
        </a>
      </p>
    </footer>
  )
}
