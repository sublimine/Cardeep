// Motor — "Sala de máquinas" (F5, 00-marketplace-engine.md §6b). Operator surface: engine
// badge (LATIENDO/DEGRADADO/PARADO), lease heartbeat, uptime 30d/90d track record (F6), the
// full 56-source table (frescura + breaker), and the open-alerts panel. Every number here
// traces to plans/cardeep-omni/00-marketplace-engine.md §4 — no MOCK_*, no hardcoded constant:
// a motor stopped on purpose MUST render PARADO with real stale dates, never a cached "live".
import { useEffect, useState } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import {
  Activity, AlertTriangle, Clock, RefreshCw, Radio, ShieldAlert, ShieldCheck, ShieldQuestion, Timer,
} from 'lucide-react'
import Card from '../components/Card'
import EmptyState from '../components/EmptyState'
import Button from '../components/Button'
import Table from '../components/Table'
import { Badge } from '../components/Badge'
import { PageSkeleton } from '../components/LoadingSpinner'
import {
  cardeep, CardeepApiError,
  type EngineStatus, type SourceHealthRow, type AlertRow, type AlertSeverity, type SourceHealthStatus,
} from '../api/cardeep'
import { ACCENT, GOOD, BAD, WARN } from '../lib/theme'

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

// Mirror of timeAgo but for forward-looking timestamps (job next_run_time) — the
// engine schedules jobs in the future, "hace X" would read backwards for those.
function timeUntil(iso: string | null, now: Date): string {
  if (!iso) return 'sin programar'
  const ms = new Date(iso).getTime() - now.getTime()
  if (ms <= 0) return 'en curso'
  const min = Math.round(ms / 60_000)
  if (min < 1) return 'en instantes'
  if (min < 60) return `en ${min} min`
  const h = Math.floor(min / 60)
  return h < 24 ? `en ${h} h` : `en ${Math.floor(h / 24)} d`
}

const BADGE_STYLE: Record<EngineStatus['badge'], { color: string; label: string }> = {
  LATIENDO: { color: GOOD, label: 'LATIENDO' },
  DEGRADADO: { color: WARN, label: 'DEGRADADO' },
  PARADO: { color: BAD, label: 'PARADO' },
}

// ---------------------------------------------------------------------------
// AnimNum — spring count-up for hero stat values. Same pattern as
// Inteligencia.tsx's AnimNum: a motion value spun up via useSpring so the
// number eases toward its target instead of snapping in on mount/refresh.
// ---------------------------------------------------------------------------

function AnimNum({ to, decimals = 0, suffix = '' }: { to: number; decimals?: number; suffix?: string }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d  = useTransform(sp, v => `${decimals ? v.toFixed(decimals) : Math.round(v)}${suffix}`)
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span className="tabular-nums">{d}</motion.span>
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
  const color = pct === null ? 'var(--text-muted)' : pct >= 99 ? GOOD : pct >= 90 ? WARN : BAD
  return (
    <Card className="!p-3">
      <div className="mb-1 text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>{label}</div>
      {pct === null ? (
        <div className="text-[13px] font-semibold" style={{ color: 'var(--text-muted)' }}>Sin histórico aún</div>
      ) : (
        <>
          <div className="text-[24px] font-extrabold leading-none" style={{ color }}>
            <AnimNum to={pct} decimals={2} suffix="%" />
          </div>
          <div className="mt-1.5 h-1 overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
            <motion.div
              className="h-full rounded-full"
              style={{ background: color }}
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(100, pct)}%` }}
              transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
            />
          </div>
        </>
      )}
      <div className="mt-1.5 text-[10px]" style={{ color: 'var(--text-muted)' }}>
        {window.full_window_available
          ? `${window.requested_days} días observados`
          : `histórico corto: ${new Date(window.observed_from).toLocaleDateString('es-ES')} → hoy`}
      </div>
    </Card>
  )
}

function EngineHeader({ status, now }: { status: EngineStatus; now: Date }) {
  const b = BADGE_STYLE[status.badge]
  return (
    <div className="mb-5">
      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="mb-3 flex flex-wrap items-center gap-3">
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
      </motion.div>

      <div className="grid gap-2.5" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))' }}>
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05, duration: 0.3 }}>
          <UptimeStat label="Uptime 30 días" window={status.uptime['30d']} />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.10, duration: 0.3 }}>
          <UptimeStat label="Uptime 90 días" window={status.uptime['90d']} />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15, duration: 0.3 }}>
          <Card className="!p-3">
            <div className="mb-1 text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>Replay desde arranque</div>
            <div className="text-[20px] font-extrabold leading-none tabular-nums" style={{ color: 'var(--text-primary)' }}>
              {status.replay_progress.sources_harvested_since_holder_started !== null
                ? <AnimNum to={status.replay_progress.sources_harvested_since_holder_started} />
                : '—'}
              {' / '}{status.replay_progress.sources_total}
            </div>
            <div className="mt-1 text-[10px]" style={{ color: 'var(--text-muted)' }} title={status.replay_progress.note}>fuentes cosechadas desde el arranque</div>
          </Card>
        </motion.div>
      </div>

      {status.jobs.length > 0 && (
        <div className="mt-3 flex flex-wrap items-center gap-1.5">
          <span className="mr-1 flex items-center gap-1 text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>
            <Timer className="h-3 w-3" /> Próximas ejecuciones
          </span>
          {status.jobs.map((job, i) => (
            <motion.span
              key={job.id}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.03, duration: 0.22 }}
              className="rounded-full px-2.5 py-1 text-[10px]"
              style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}
            >
              <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{job.id}</span>{' '}
              <span className="tabular-nums" style={{ color: 'var(--text-muted)' }}>{timeUntil(job.next_run_time, now)}</span>
            </motion.span>
          ))}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Sources table (§6b: nombre, tier, frescura, breaker, última cosecha) — built
// on the shared Table component (row entrance stagger + consistent chrome)
// instead of a hand-rolled <table>.
// ---------------------------------------------------------------------------

const STATUS_STYLE: Record<SourceHealthStatus, { color: string; label: string; icon: typeof ShieldCheck }> = {
  healthy: { color: GOOD, label: 'Sana', icon: ShieldCheck },
  degraded: { color: WARN, label: 'Degradada', icon: ShieldQuestion },
  down: { color: BAD, label: 'Caída', icon: ShieldAlert },
  unknown: { color: '#94a3b8', label: 'Desconocida', icon: ShieldQuestion },
}

function SourcesTable({ sources, now }: { sources: SourceHealthRow[]; now: Date }) {
  return (
    <Card>
      <Table
        columns={[
          {
            key: 'source_key',
            header: 'Fuente',
            render: (s: SourceHealthRow) => (
              <span className="text-[11.5px] font-medium" style={{ color: 'var(--text-primary)' }}>{s.source_key}</span>
            ),
          },
          {
            key: 'group',
            header: 'Grupo',
            render: (s: SourceHealthRow) => (
              <Badge color={s.is_tier1 ? 'blue' : 'gray'}>{s.is_tier1 ? 'Portal grande' : 'Vendedor directo'}</Badge>
            ),
          },
          {
            key: 'status',
            header: 'Frescura',
            render: (s: SourceHealthRow) => {
              const st = STATUS_STYLE[s.status] ?? STATUS_STYLE.unknown
              const Icon = st.icon
              return (
                <div className="flex items-center gap-1.5">
                  <Icon className="h-3 w-3 shrink-0" style={{ color: st.color }} />
                  <span className="text-[11px] font-semibold" style={{ color: st.color }}>{st.label}</span>
                </div>
              )
            },
          },
          {
            key: 'consecutive_fails',
            header: 'Fallos seguidos',
            className: 'tabular-nums whitespace-nowrap',
            render: (s: SourceHealthRow) => (
              <span className="text-[11px]" style={{ color: s.consecutive_fails >= 3 ? BAD : 'var(--text-secondary)' }}>
                {s.consecutive_fails}
              </span>
            ),
          },
          {
            key: 'last_ok',
            header: 'Última OK',
            render: (s: SourceHealthRow) => (
              <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>{timeAgo(s.last_ok, now)}</span>
            ),
          },
          {
            key: 'last_fail',
            header: 'Último fallo',
            render: (s: SourceHealthRow) => (
              <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>{timeAgo(s.last_fail, now)}</span>
            ),
          },
        ]}
        data={sources}
        keyExtractor={s => s.source_key}
      />
    </Card>
  )
}

// ---------------------------------------------------------------------------
// Alerts panel (§6b)
// ---------------------------------------------------------------------------

const SEV_COLOR: Record<AlertSeverity, string> = { critical: BAD, warning: WARN, info: ACCENT }

function AlertsPanel({ alerts, now }: { alerts: AlertRow[]; now: Date }) {
  if (alerts.length === 0) {
    return <EmptyState icon={<AlertTriangle className="h-6 w-6" />} title="Sin alertas abiertas" message="No hay alertas activas ahora mismo." />
  }
  return (
    <div className="flex flex-col gap-2">
      {alerts.map((a, i) => (
        <motion.div
          key={a.id}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.04, duration: 0.24 }}
          className="relative flex items-start gap-2.5 overflow-hidden rounded-[10px] p-3 pl-4"
          style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
        >
          <span className="absolute inset-y-0 left-0 w-1" style={{ background: SEV_COLOR[a.severity] }} aria-hidden />
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" style={{ color: SEV_COLOR[a.severity] }} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-[10.5px] font-bold uppercase tracking-wide" style={{ color: SEV_COLOR[a.severity] }}>{a.origin}</span>
              <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{timeAgo(a.created_at, now)}</span>
            </div>
            <div className="mt-0.5 text-[11.5px]" style={{ color: 'var(--text-primary)' }}>{a.message}</div>
          </div>
        </motion.div>
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
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.32, ease: [0.32, 0.72, 0, 1] }} className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="mb-1 flex items-center gap-2 text-[20px] font-bold" style={{ color: 'var(--text-primary)' }}>
            <Activity className="h-5 w-5" /> Sala de máquinas
          </h1>
          <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
            Estado real del motor de cosecha — cada número traza a un dato verificado, nunca a un mock.
          </p>
        </div>
        <Button variant="ghost" size="sm" icon={<RefreshCw className="h-3 w-3" />} onClick={reload}>
          Actualizar
        </Button>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.06, duration: 0.36, ease: [0.32, 0.72, 0, 1] }}>
        {statusError ? (
          <div className="mb-5">
            <EmptyState icon={<Radio className="h-6 w-6" />} title="No se pudo leer el estado del motor" message={statusError} action={<Button onClick={reload}>Reintentar</Button>} />
          </div>
        ) : status ? (
          <EngineHeader status={status} now={now} />
        ) : null}
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.14, duration: 0.36, ease: [0.32, 0.72, 0, 1] }}>
        <div className="mb-2 flex items-center gap-1.5 text-[12px] font-bold" style={{ color: 'var(--text-primary)' }}>
          <Clock className="h-3.5 w-3.5" /> Fuentes (<span className="tabular-nums">{sources?.length ?? 0}</span>)
        </div>
        {sourcesError ? (
          <EmptyState icon={<Radio className="h-6 w-6" />} title="No se pudo leer el estado de las fuentes" message={sourcesError} action={<Button onClick={reload}>Reintentar</Button>} />
        ) : sources && sources.length > 0 ? (
          <SourcesTable sources={sources} now={now} />
        ) : sources ? (
          <EmptyState icon={<Radio className="h-6 w-6" />} title="Sin fuentes registradas" />
        ) : null}
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.22, duration: 0.36, ease: [0.32, 0.72, 0, 1] }} className="mt-6">
        <div className="mb-2 flex items-center gap-1.5 text-[12px] font-bold" style={{ color: 'var(--text-primary)' }}>
          <AlertTriangle className="h-3.5 w-3.5" /> Alertas abiertas (<span className="tabular-nums">{alerts?.length ?? 0}</span>)
        </div>
        {alertsError ? (
          <EmptyState icon={<Radio className="h-6 w-6" />} title="No se pudieron leer las alertas" message={alertsError} action={<Button onClick={reload}>Reintentar</Button>} />
        ) : alerts ? (
          <AlertsPanel alerts={alerts} now={now} />
        ) : null}
      </motion.div>
    </div>
  )
}
