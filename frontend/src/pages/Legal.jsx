export function PrivacyPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="font-display text-3xl font-bold text-watershed-deep">Privacy Policy</h1>
      <p className="mt-4 text-sm text-watershed-deep/80">
        Placeholder pending registered business entity. WatershedOS processes zone-level
        satellite aggregates. Identifiable land-ownership or community data is not joined
        without written consent. Personal data (e.g. alert emails) is retained only per the
        documented retention schedule and purged by scheduled jobs.
      </p>
      <a className="mt-6 inline-block text-sm underline" href="/">
        ← Back to dashboard
      </a>
    </main>
  )
}

export function TermsPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="font-display text-3xl font-bold text-watershed-deep">Terms of Service</h1>
      <p className="mt-4 text-sm text-watershed-deep/80">
        Placeholder pending registered business entity. Health scores and carbon estimates
        are decision-support outputs, not legal determinations of land use or Verra-certified
        credits until methodology gaps are closed.
      </p>
      <a className="mt-6 inline-block text-sm underline" href="/">
        ← Back to dashboard
      </a>
    </main>
  )
}
