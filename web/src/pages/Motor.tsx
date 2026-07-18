// Motor — "Sala de máquinas" (F5, 00-marketplace-engine.md §6b). Operator surface: engine
// badge (LATIENDO/DEGRADADO/PARADO), lease heartbeat, uptime 30d/90d track record (F6), the
// full 56-source table (frescura + breaker), and the open-alerts panel. Every number here
// traces to plans/cardeep-omni/00-marketplace-engine.md §4 — no MOCK_*, no hardcoded constant:
// a motor stopped on purpose MUST render PARADO with real stale dates, never a cached "live".
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Activity, AlertTriangle, Clock, RefreshCw, Radio, ShieldAlert, ShieldCheck, ShieldQuestion,
} from 'lucide-react'
import Card from '../components/Card'
import EmptyState from '../components/EmptyState'
import Button from '../components/Button'
import { Badge } from '../components/Badge'
import { PageSkeleton } from '../components/LoadingSpinner'
import {
  cardeep, CardeepApiError,
  type EngineStatus, type SourceHealthRow, type AlertRow, type AlertSeverity, type SourceHealthStatus,
} from '../api/cardeep'
import { GOOD, BAD, WARN } from '../lib/theme'

function errorMessage(err: unknown): string {
  if (err instanceof CardeepApiError) return err.message
  if (err instanceof Error) return err.message
  return 'Error desconocido al consultar la API de CARDEEP'
}

function timeAgo(iso: string | null, now: Date): string {
  if (!iso) return 'nunca'
  const ms = now.getTime() - new Date(iso).getTime()
  const min = Math.floor(ms / 60_000)
  if (min < 1) return 'hace instantes'
  if (min < 60) return `hace ${min} min`
  const h = Math.floor(min / 60)
  if (h < 24) return `hace ${h} h`
  return `hace ${Math.floor(h / 24)} d`
}

const BADGE_STYLE: Record<EngineStatus['badge'], { color: string; label: string }> = {
  LATIENDO: { color: GOOD, label: 'LATIENDO' },
  DEGRADADO: { color: WARN, label: 'DEGRADADO' },
  PARADO: { color: BAD, label: 'PARADO' },
}

// ---------------------------------------------------------------------------
// Data hook — three independent fetches (status/sources/alerts), each with its own
// loading/error so one slow endpoint never blanks the other two panels.
// ---------------------------------------------------------------------------

function useEngineRoom() {
  const [status, setStatus] = useState<EngineStatus | null>(null)
  const [sources, setSources] = useState<SourceHealthRow[] | null>(null)
  const [alerts, setAlerts] = useState<AlertRow[] | null>(null)
  const [statusError, setStatusError] = useState<string | null>(null)
  const [sourcesError, setSourcesError] = useState<string | null>(null)
  const [alertsError, setAlertsError] = useState<string | null>(null)
  const [gen, setGen] = useState(0)

  useEffect(() => {
    let cancelled = false
    setStatus(null); setStatusError(null)
    cardeep.engineStatus().then(d => { if (!cancelled) setStatus(d) })
      .catch((e: unknown) => { if (!cancelled) setStatusError(errorMessage(e)) })
    return () => { cancelled = true }
  }, [gen])

  useEffect(() => {
    let cancelled = false
    setSources(null); setSourcesError(null)
    cardeep.sources().then(d => { if (!cancelled) setSources(d) })
      .catch((e: unknown) => { if (!cancelled) setSourcesError(errorMessage(e)) })
    return () => { cancelled = true }
  }, [gen])

  useEffect(() => {
    let cancelled = false
    setAlerts(null); setAlertsError(null)
    cardeep.alerts(1, 100).then(d => { if (!cancelled) setAlerts(d.items) })
      .catch((e: unknown) => { if (!cancelled) setAlertsError(errorMessage(e)) })
    return () => { cancelled = true }
  }, [gen])

  return {
    status, sources, alerts, statusError, sourcesError, alertsError,
    reload: () => setGen(g => g + 1),
  }
}

// ---------------------------------------------------------------------------
// Header — badge + heartbeat + uptime
// ---------------------------------------------------------------------------

function UptimeStat({ label, window }: { label: string; window: EngineStatus['uptime']['30d'] }) {
  const pct = window.uptime_pct
  return (
    <div className="rounded-[10px] p-3" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}>
      <div className="mb-1 text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>{label}</div>
      {pct === null ? (
        <div className="text-[13px] font-semibold" style={{ color: 'var(--text-muted)' }}>Sin histórico aún</div>
      ) : (
        <div className="text-[24px] font-extrabold leading-none" style={{ color: pct >= 99 ? GOOD : pct >= 90 ? WARN : BAD }}>
          {pct.toFixed(2)}%
        </div>
      )}
      <div className="mt-1 text-[10px]" style={{ color: 'var(--text-muted)' }}>
        {window.full_window_available
          ? `${window.requested_days} días observados`
          : `histórico corto: ${new Date(window.observed_from).toLocaleDateString('es-ES')} → hoy`}
      </div>
    </div>
  )
}

function EngineHeader({ status, now }: { status: EngineStatus; now: Date }) {
  const b = BADGE_STYLE[status.badge]
  return (
    <div className="mb-5">
      <div className="mb-3 flex flex-wrap items-center gap-3">
        <div
          className="flex items-center gap-2 rounded-full px-4 py-2"
          style={{ background: `${b.color}18`, border: `1px solid ${b.color}44` }}
        >
          <motion.span
            className="h-2.5 w-2.5 rounded-full"
            style={{ background: b.color, boxShadow: `0 0 8px ${b.color}` }}
            animate={status.badge === 'LATIENDO' ? { opacity: [1, 0.4, 1] } : undefined}
            transition={{ duration: 1.6, repeat: Infinity }}
          />
          <span className="text-[15px] font-extrabold tracking-wide" style={{ color: b.color }}>{b.label}</span>
        </div>
        <span className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
          último latido {timeAgo(status.lease.last_heartbeat, now)}
          {status.lease.holder && ` · holder=${status.lease.holder} · pid=${status.lease.pid}`}
        </span>
      </div>
      <div className="grid gap-2.5" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))' }}>
        <UptimeStat label="Uptime 30 días" window={status.uptime['30d']} />
        <UptimeStat label="Uptime 90 días" window={status.uptime['90d']} />
        <div className="rounded-[10px] p-3" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}>
          <div className="mb-1 text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>Replay desde arranque</div>
          <div className="text-[20px] font-extrabold leading-none" style={{ color: 'var(--text-primary)' }}>
            {status.replay_progress.sources_harvested_since_holder_started ?? '—'} / {status.replay_progress.sources_total}
          </div>
          <div className="mt-1 text-[10px]" style={{ color: 'var(--text-muted)' }} title={status.replay_progress.note}>fuentes cosechadas desde el arranque</div>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Sources table (§6b: nombre, tier, frescura, breaker, última cosecha)
// ---------------------------------------------------------------------------

const STATUS_STYLE: Record<SourceHealthStatus, { color: string; label: string; icon: typeof ShieldCheck }> = {
  healthy: { color: GOOD, label: 'Sana', icon: ShieldCheck },
  degraded: { color: WARN, label: 'Degradada', icon: ShieldQuestion },
  down: { color: BAD, label: 'Caída', icon: ShieldAlert },
  unknown: { color: '#94a3b8', label: 'Desconocida', icon: ShieldQuestion },
}

function SourcesTable({ sources, now }: { sources: SourceHealthRow[]; now: Date }) {
  return (
    <Card className="!p-0 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              {['Fuente', 'Grupo', 'Frescura', 'Fallos seguidos', 'Última OK', 'Último fallo'].map(h => (
                <th key={h} className="whitespace-nowrap p-2.5 text-[10px] font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sources.map(s => {
              const st = STATUS_STYLE[s.status] ?? STATUS_STYLE.unknown
              const Icon = st.icon
              return (
                <tr key={s.source_key} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td className="p-2.5 text-[11.5px] font-medium" style={{ color: 'var(--text-primary)' }}>{s.source_key}</td>
                  <td className="p-2.5">
                    <Badge color={s.is_tier1 ? 'blue' : 'gray'}>{s.is_tier1 ? 'Portal grande' : 'Vendedor directo'}</Badge>
                  </td>
                  <td className="p-2.5">
                    <div className="flex items-center gap-1.5">
                      <Icon className="h-3 w-3 shrink-0" style={{ color: st.color }} />
                      <span className="text-[11px] font-semibold" style={{ color: st.color }}>{st.label}</span>
                    </div>
                  </td>
                  <td className="p-2.5 text-[11px] tabular-nums" style={{ color: s.consecutive_fails >= 3 ? BAD : 'var(--text-secondary)' }}>
                    {s.consecutive_fails}
                  </td>
                  <td className="p-2.5 text-[11px]" style={{ color: 'var(--text-muted)' }}>{timeAgo(s.last_ok, now)}</td>
                  <td className="p-2.5 text-[11px]" style={{ color: 'var(--text-muted)' }}>{timeAgo(s.last_fail, now)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

// ---------------------------------------------------------------------------
// Alerts panel (§6b)
// ---------------------------------------------------------------------------

const SEV_COLOR: Record<AlertSeverity, string> = { critical: BAD, warning: WARN, info: '#3b82f6' }

function AlertsPanel({ alerts, now }: { alerts: AlertRow[]; now: Date }) {
  if (alerts.length === 0) {
    return <EmptyState icon={<AlertTriangle className="h-6 w-6" />} title="Sin alertas abiertas" message="No hay alertas activas ahora mismo." />
  }
  return (
    <div className="flex flex-col gap-2">
      {alerts.map(a => (
        <div
          key={a.id}
          className="flex items-start gap-2.5 rounded-[10px] p-3"
          style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderLeft: `2px solid ${SEV_COLOR[a.severity]}` }}
        >
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" style={{ color: SEV_COLOR[a.severity] }} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-[10.5px] font-bold uppercase tracking-wide" style={{ color: SEV_COLOR[a.severity] }}>{a.origin}</span>
              <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{timeAgo(a.created_at, now)}</span>
            </div>
            <div className="mt-0.5 text-[11.5px]" style={{ color: 'var(--text-primary)' }}>{a.message}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Motor() {
  const { status, sources, alerts, statusError, sourcesError, alertsError, reload } = useEngineRoom()
  const [now] = useState(() => new Date())

  const loading = !status && !sources && !alerts && !statusError && !sourcesError && !alertsError
  if (loading) return <PageSkeleton />

  return (
    <div className="mx-auto p-[20px_24px_48px]" style={{ maxWidth: 1400 }}>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="mb-1 flex items-center gap-2 text-[20px] font-bold" style={{ color: 'var(--text-primary)' }}>
            <Activity className="h-5 w-5" /> Sala de máquinas
          </h1>
          <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
            Estado real del motor de cosecha — cada número traza a un dato verificado, nunca a un mock.
          </p>
        </div>
        <button
          onClick={reload}
          className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[11px]"
          style={{ color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)' }}
        >
          <RefreshCw className="h-3 w-3" /> Actualizar
        </button>
      </div>

      {statusError ? (
        <div className="mb-5">
          <EmptyState icon={<Radio className="h-6 w-6" />} title="No se pudo leer el estado del motor" message={statusError} action={<Button onClick={reload}>Reintentar</Button>} />
        </div>
      ) : status ? (
        <EngineHeader status={status} now={now} />
      ) : null}

      <div className="mb-2 flex items-center gap-1.5 text-[12px] font-bold" style={{ color: 'var(--text-primary)' }}>
        <Clock className="h-3.5 w-3.5" /> Fuentes ({sources?.length ?? 0})
      </div>
      {sourcesError ? (
        <EmptyState icon={<Radio className="h-6 w-6" />} title="No se pudo leer el estado de las fuentes" message={sourcesError} action={<Button onClick={reload}>Reintentar</Button>} />
      ) : sources && sources.length > 0 ? (
        <SourcesTable sources={sources} now={now} />
      ) : sources ? (
        <EmptyState icon={<Radio className="h-6 w-6" />} title="Sin fuentes registradas" />
      ) : null}

      <div className="mb-2 mt-6 flex items-center gap-1.5 text-[12px] font-bold" style={{ color: 'var(--text-primary)' }}>
        <AlertTriangle className="h-3.5 w-3.5" /> Alertas abiertas ({alerts?.length ?? 0})
      </div>
      {alertsError ? (
        <EmptyState icon={<Radio className="h-6 w-6" />} title="No se pudieron leer las alertas" message={alertsError} action={<Button onClick={reload}>Reintentar</Button>} />
      ) : alerts ? (
        <AlertsPanel alerts={alerts} now={now} />
      ) : null}
    </div>
  )
}
