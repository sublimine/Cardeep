// Publicaciones — Frente A of pilar 05-multiposting (plans/cardeep-omni/05-multiposting.md).
// Read-only: "donde esta y donde NO esta mi inventario, en que portal, con que
// divergencia de precio y que anomalias". Zero credenciales, zero escritura saliente
// (Frente B/C quedan fuera de alcance -- boton "Publicar" llega en F5, gated).
//
// Dealer scope: la MISMA convencion que 03-garage-fleet ya establecio para
// pages/inventory -- useAuthContext().user.tenantId (AUTH-0), nunca un cdp hardcoded.
import { useCallback, useEffect, useRef, useState } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import {
  Check, AlertTriangle, Clock, ExternalLink, RefreshCw, Radio, ImageOff,
} from 'lucide-react'
import Card from '../components/Card'
import EmptyState from '../components/EmptyState'
import Button from '../components/Button'
import { Badge } from '../components/Badge'
import LoadingSpinner, { PageSkeleton } from '../components/LoadingSpinner'
import { useAuthContext } from '../auth/AuthContext'
import {
  cardeep, CardeepApiError,
  type PublishingCoverage, type PublishingMatrixRow, type CoverageBand,
} from '../api/cardeep'
import { GOOD, BAD, WARN } from '../lib/theme'

const PAGE_SIZE = 100

// Shared focus-visible ring — mirrors Button.tsx's own focus treatment so every
// ad-hoc anchor on this page (listing links) matches house style.
const FOCUS_RING = 'outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary'

function errorMessage(err: unknown): string {
  if (err instanceof CardeepApiError) return err.message
  if (err instanceof Error) return err.message
  return 'Error desconocido al consultar la API de CARDEEP'
}

function hoursAgo(iso: string, now: Date): string {
  const h = (now.getTime() - new Date(iso).getTime()) / 3_600_000
  if (h < 1) return 'hace unos minutos'
  if (h < 24) return `hace ${Math.round(h)} h`
  return `hace ${Math.round(h / 24)} d`
}

// ---------------------------------------------------------------------------
// Animated number — mirrors pages/Arbitrage.tsx's AnimNum 1:1 (page-local by
// convention across this squad pass, not a shared component). Reserved for the
// coverage grid's hero percentage only; every other figure on the page stays a
// plain tabular-nums span so the counting effect doesn't dilute into noise.
// ---------------------------------------------------------------------------

function AnimNum({ to, suffix = '' }: { to: number; suffix?: string }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d = useTransform(sp, v => `${Math.round(v)}${suffix}`)
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span className="tabular-nums">{d}</motion.span>
}

// ---------------------------------------------------------------------------
// Data hook — coverage loads once; matrix loads progressively (same pattern as
// pages/inventory/useDealerInventory.ts). No mocks, no fallback fleet: a failed
// request surfaces as `error`, never as a silently-swapped placeholder.
// ---------------------------------------------------------------------------

function usePublishingData(cdp: string) {
  const [coverage, setCoverage] = useState<PublishingCoverage | null>(null)
  const [rows, setRows] = useState<PublishingMatrixRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isComplete, setIsComplete] = useState(false)
  const generationRef = useRef(0)

  const load = useCallback(() => {
    const generation = ++generationRef.current
    const isCurrent = () => generationRef.current === generation

    setCoverage(null)
    setRows([])
    setIsComplete(false)
    setError(null)
    setLoading(true)

    cardeep.publishingCoverage(cdp)
      .then(c => { if (isCurrent()) setCoverage(c) })
      .catch((e: unknown) => { if (isCurrent()) setError(s => s ?? errorMessage(e)) })

    async function loadAllPages() {
      let page = 1
      let all: PublishingMatrixRow[] = []
      for (;;) {
        const batch = await cardeep.publishingMatrix(cdp, page, PAGE_SIZE)
        if (!isCurrent()) return
        all = [...all, ...batch.items]
        setRows(all)
        setLoading(false)
        if (!batch.has_more) break
        page += 1
      }
      if (isCurrent()) setIsComplete(true)
    }

    loadAllPages().catch((e: unknown) => {
      if (isCurrent()) { setLoading(false); setError(s => s ?? errorMessage(e)) }
    })
  }, [cdp])

  useEffect(() => { load(); return () => { generationRef.current += 1 } }, [load])

  return { coverage, rows, loading, error, isComplete, reload: load }
}

// ---------------------------------------------------------------------------
// Coverage semaphore header (S4.1, S6.1)
// ---------------------------------------------------------------------------

const BAND_COLOR: Record<CoverageBand, string> = { verde: GOOD, ambar: WARN, rojo: BAD }
const BAND_LABEL: Record<CoverageBand, string> = { verde: 'Buena cobertura', ambar: 'Cobertura parcial', rojo: 'Cobertura baja' }

function CoverageHeader({ coverage }: { coverage: PublishingCoverage }) {
  const anyListed = coverage.platforms.reduce((acc, p) => acc + p.n_listed, 0)
  const inAnyPortal = coverage.total_available > 0
    ? Math.min(coverage.total_available, Math.max(...coverage.platforms.map(p => p.n_listed), 0))
    : 0

  return (
    <div className="mb-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}>
        <p className="mb-[5px] font-mono text-[11px] tracking-[0.03em]" style={{ color: 'var(--text-muted)' }}>Multiposting · visibilidad cross-portal</p>
        <h1 className="mb-1.5 text-[22px] font-extrabold leading-none tracking-[-0.02em]" style={{ color: 'var(--text-primary)' }}>Tu stock en los portales</h1>
        <p className="mb-4 max-w-2xl text-[12px] leading-[1.55]" style={{ color: 'var(--text-muted)' }}>
          {coverage.total_available === 0 ? (
            'Sin inventario disponible ahora mismo.'
          ) : coverage.platforms.length === 0 ? (
            <>Ninguno de tus <strong className="tabular-nums" style={{ color: 'var(--text-primary)' }}>{coverage.total_available}</strong> coches aparece en un portal todavía.</>
          ) : (
            <>
              Al menos <strong className="tabular-nums" style={{ color: 'var(--text-primary)' }}>{inAnyPortal}</strong> de tus{' '}
              <strong className="tabular-nums" style={{ color: 'var(--text-primary)' }}>{coverage.total_available}</strong> coches están en algún portal{' '}
              (<strong className="tabular-nums" style={{ color: 'var(--text-primary)' }}>{anyListed.toLocaleString()}</strong> anuncios activos en total).
            </>
          )}
        </p>
      </motion.div>

      {coverage.platforms.length > 0 && (
        <div className="grid gap-2.5" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))' }}>
          {coverage.platforms.map((p, i) => (
            <motion.div
              key={p.cdp_code}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05, duration: 0.38, ease: [0.32, 0.72, 0, 1] }}
            >
              <Card hover className="!p-3.5 h-full">
                <div className="mb-1.5 flex items-center justify-between gap-2">
                  <span className="truncate text-[12.5px] font-semibold" style={{ color: 'var(--text-primary)' }}>{p.trade_name ?? p.cdp_code}</span>
                  <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: BAND_COLOR[p.band], boxShadow: `0 0 6px ${BAND_COLOR[p.band]}` }} />
                </div>
                <div className="mb-1 text-[22px] font-extrabold leading-none tracking-[-0.02em]" style={{ color: BAND_COLOR[p.band] }}>
                  <AnimNum to={Math.round(p.coverage_pct * 100)} suffix="%" />
                </div>
                <div className="text-[10.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>
                  {p.n_listed.toLocaleString()} de {coverage.total_available.toLocaleString()} coches · {BAND_LABEL[p.band]}
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Matrix cell (S4.1-S4.4, S6.2)
// ---------------------------------------------------------------------------

function MatrixCell({ row, platformCdp, now }: { row: PublishingMatrixRow; platformCdp: string; now: Date }) {
  const edge = row.platforms.find(p => p.cdp_code === platformCdp)

  if (!edge) {
    return <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>No publicado</span>
  }

  if (edge.anomaly === 'sold_still_listed') {
    return (
      <div className="flex flex-col gap-0.5">
        <Badge color="red" dot pulse>Vendido, sigue publicado</Badge>
        <a
          href={edge.listing_url} target="_blank" rel="noreferrer"
          className={`inline-flex items-center gap-1 text-[10px] transition-colors hover:text-[var(--text-secondary)] ${FOCUS_RING}`}
          style={{ color: 'var(--text-muted)' }}
        >
          Ver anuncio <ExternalLink className="h-2.5 w-2.5" />
        </a>
      </div>
    )
  }

  if (edge.anomaly === 'available_removed') {
    return <Badge color="orange" dot>Retirado del portal</Badge>
  }

  if (edge.status === 'removed') {
    return <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Retirado (histórico)</span>
  }

  // status === 'listed'
  const divergent = edge.divergence?.flag ?? false
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-1.5">
        {divergent ? <AlertTriangle className="h-3 w-3 shrink-0" style={{ color: WARN }} /> : <Check className="h-3 w-3 shrink-0" style={{ color: GOOD }} />}
        <a
          href={edge.listing_url} target="_blank" rel="noreferrer"
          className={`group inline-flex items-center gap-1 text-[11.5px] font-medium transition-colors hover:underline ${FOCUS_RING}`}
          style={{ color: 'var(--text-primary)' }}
        >
          Publicado <ExternalLink className="h-2.5 w-2.5 opacity-60 transition-colors group-hover:text-[var(--c-brand-soft)]" />
        </a>
        {edge.old_listing && (
          <span title="Anuncio más viejo que la mediana de rotación de su segmento">
            <Clock className="h-3 w-3" style={{ color: 'var(--text-muted)' }} />
          </span>
        )}
      </div>
      {divergent && edge.platform_price != null && (
        <span className="text-[10.5px] tabular-nums" style={{ color: WARN }}>
          Aquí a {row.price?.toLocaleString('es-ES')} € · portal a {edge.platform_price.toLocaleString('es-ES')} €
        </span>
      )}
      <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>visto {hoursAgo(edge.last_seen, now)}</span>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main table (S6.2)
// ---------------------------------------------------------------------------

function MatrixTable({ rows, platformColumns, now }: { rows: PublishingMatrixRow[]; platformColumns: PublishingCoverage['platforms']; now: Date }) {
  return (
    <Card className="!p-0 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <th className="sticky left-0 z-10 whitespace-nowrap p-3 text-[10.5px] font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)', background: 'var(--bg-elevated)' }}>Coche</th>
              {platformColumns.map(p => (
                <th key={p.cdp_code} className="min-w-[180px] whitespace-nowrap p-3 text-[10.5px] font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
                  {p.trade_name ?? p.cdp_code}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* No per-row entrance stagger here on purpose — this list can grow into the
               hundreds/thousands as pages stream in (PAGE_SIZE=100, progressive load), so
               animating every row would both tank frame time and never finish "settling".
               The table container itself gets one fade-in from the caller instead. */}
            {rows.map(row => (
              <tr key={row.vehicle_ulid} className="group transition-colors hover:bg-[var(--bg-hover)]" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td className="sticky left-0 z-10 p-3 align-top transition-colors group-hover:bg-[var(--bg-hover)]" style={{ background: 'var(--bg-elevated)' }}>
                  <div className="flex items-center gap-2.5">
                    {row.photo_url
                      ? <img src={row.photo_url} alt="" className="h-9 w-12 shrink-0 rounded object-cover" style={{ background: 'var(--bg-surface)' }} />
                      : (
                        <div className="flex h-9 w-12 shrink-0 items-center justify-center rounded" style={{ background: 'var(--bg-surface)' }}>
                          <ImageOff className="h-3.5 w-3.5" style={{ color: 'var(--text-muted)' }} />
                        </div>
                      )}
                    <div className="min-w-0">
                      <div className="truncate text-[12px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {row.make} {row.model}
                      </div>
                      <div className="text-[10.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>
                        {row.year ?? '—'} · {row.price != null ? `${row.price.toLocaleString('es-ES')} €` : 'sin precio'}
                        {row.status === 'gone' && <span style={{ color: BAD }}> · vendido</span>}
                      </div>
                    </div>
                  </div>
                </td>
                {platformColumns.map(p => (
                  <td key={p.cdp_code} className="p-3 align-top">
                    <MatrixCell row={row} platformCdp={p.cdp_code} now={now} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

function PublicacionesForDealer({ cdp }: { cdp: string }) {
  const { coverage, rows, loading, error, isComplete, reload } = usePublishingData(cdp)
  const [now] = useState(() => new Date())

  if (loading && rows.length === 0 && !coverage && !error) return <PageSkeleton />

  if (error && rows.length === 0 && !coverage) {
    return (
      <div className="p-[24px_28px]">
        <EmptyState
          icon={<Radio className="h-6 w-6" />}
          title="No se pudo cargar el estado de publicación"
          message={error}
          action={<Button onClick={reload}>Reintentar</Button>}
        />
      </div>
    )
  }

  const platformColumns = coverage?.platforms ?? []
  // A sub-request (coverage OR matrix) failed but the OTHER one still resolved —
  // surface it inline instead of dropping it silently. The full-page EmptyState
  // above only fires when BOTH are empty; this is the "partial degradation" branch,
  // reusing the same `error` the hook already tracks — no new data wiring.
  const partialError = error && (coverage || rows.length > 0) ? error : null

  return (
    <div className="mx-auto p-[20px_24px_48px]" style={{ maxWidth: 1600 }}>
      {coverage && <CoverageHeader coverage={coverage} />}

      {partialError && (
        <div className="mb-3 flex items-center gap-1.5 text-[11px]" style={{ color: WARN }}>
          <AlertTriangle className="h-3 w-3 shrink-0" />
          {partialError}
        </div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05, duration: 0.32 }}
        className="mb-3 flex items-center justify-between"
      >
        <span className="flex items-center gap-1.5 text-[11px] tabular-nums" style={{ color: 'var(--text-muted)' }}>
          {!isComplete && <LoadingSpinner size="sm" className="h-3 w-3" />}
          {isComplete ? `${rows.length.toLocaleString()} coches cargados` : `Cargando… ${rows.length.toLocaleString()} coches`}
        </span>
        <Button variant="secondary" size="sm" loading={loading} icon={<RefreshCw className="h-3 w-3" />} onClick={reload}>
          Actualizar
        </Button>
      </motion.div>

      {rows.length === 0 ? (
        <EmptyState
          icon={<Radio className="h-6 w-6" />}
          title="Sin inventario que mostrar"
          message="Este dealer no tiene coches disponibles ni anomalías de publicación pendientes ahora mismo."
        />
      ) : (
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.42, ease: [0.32, 0.72, 0, 1] }}>
          <MatrixTable rows={rows} platformColumns={platformColumns} now={now} />
        </motion.div>
      )}

      <p className="mt-4 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
        Publicar directamente desde aquí (AutoScout24 vía API oficial, feeds de Google/Meta) llega
        en una fase próxima. Coches.net, Wallapop y Milanuncios dependen de un acuerdo de acceso con
        cada portal — no tienen API de escritura pública hoy.
      </p>
    </div>
  )
}

export default function Publicaciones() {
  const { user } = useAuthContext()
  const cdp = user?.tenantId || null

  if (!cdp) {
    return (
      <div className="p-[24px_28px]">
        <EmptyState
          icon={<Radio className="h-6 w-6" />}
          title="Sin perfil de dealer"
          message="Reclama tu ficha de dealer (Ajustes → Reclamar dealer) para ver dónde está publicado tu inventario en cada portal."
        />
      </div>
    )
  }

  return <PublicacionesForDealer cdp={cdp} />
}
