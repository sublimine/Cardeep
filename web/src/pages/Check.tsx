import { Car, Construction } from 'lucide-react'

// ── Page ──────────────────────────────────────────────────────────────────────
//
// QUARANTINED (02-history-reports F0, 2026-07-18): this page used to orchestrate
// a report/dossier pair of hooks fetching `/check/*` through the legacy generic
// fetch client, dev-proxied to a port nothing in this repo ever served
// (docker-compose.yml only defines cardeep-pg/api/autopilot). Zero backend ever
// existed for those routes (services/api/main.py registers ops/entities/geo/
// vehicles/platforms only) — see plans/cardeep-omni/02-history-reports.md §1.
//
// The two report-fetching hooks and the dossier sub-component are deleted (dead
// weight, zero other consumers). CheckLanding.tsx/CheckReport.tsx are KEPT
// untouched — F3 rewires them to the real client (web/src/api/cardeep.ts) and
// the real "Vida en mercado" data (GET /vehicles/{ulid}/lifetime, built in
// F1/F2). The route itself is removed from App.tsx/Shell.tsx so nothing serves
// this mock even accidentally; this component is intentionally unreachable
// until F3.
export default function CheckPage() {
  return (
    <div className="min-h-[100dvh] bg-bg-primary">
      <header className="h-12 sticky top-0 z-[var(--z-overlay)] bg-bg-surface/70 backdrop-blur-md border-b border-border-subtle flex items-center px-5">
        <a href="/" className="flex items-center gap-2.5 group">
          <div className="w-6 h-6 bg-accent-blue rounded-md flex items-center justify-center shadow-glow-blue transition-all duration-200 group-hover:shadow-none">
            <Car className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-semibold tracking-tight text-text-primary text-sm">
            CARDEEP
            <span className="text-accent-blue font-normal ml-1.5">Check</span>
          </span>
        </a>
      </header>

      <main className="max-w-sm mx-auto px-5 py-20 text-center">
        <div className="w-12 h-12 rounded-xl bg-amber-500/15 ring-1 ring-amber-500/20 flex items-center justify-center mx-auto mb-5">
          <Construction className="w-5 h-5 text-accent-amber" />
        </div>
        <h1 className="text-base font-semibold text-text-primary mb-1.5">
          En reconstrucción
        </h1>
        <p className="text-sm text-text-secondary leading-relaxed">
          Cardeep no tiene acceso a titularidad, ITV ni siniestros — esa maqueta ha sido
          retirada. Estamos construyendo el historial que sí podemos verificar: la vida
          en mercado de cada vehículo por unidad física (días en mercado, bajadas de
          precio, dealers que lo han tenido, re-publicaciones). Vuelve pronto.
        </p>
      </main>
    </div>
  )
}
