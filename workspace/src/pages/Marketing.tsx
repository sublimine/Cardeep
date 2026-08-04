// Marketing — pilar 07-marketing (plans/cardeep-omni/07-marketing.md).
// "Tus anuncios, auditados contra el mercado real" — el mejor auditor + generador de
// anuncios de coche de España, cada afirmación anclada en el censo verificado.
//
// Dealer scope: misma convención que 03-garage-fleet/05-multiposting — useAuthContext()
// .user.tenantId (AUTH-0), nunca un cdp hardcoded.
//
// Bloques 1-3 (F4): "Arregla estos primero" (C1, gratis), "Radar de canales" (C3/C4/C5,
// Capa 1 — PremiumGate), "Feed listo para anunciarte" (C6, generación gratis). Bloque 4
// ("Descripción con pruebas", C7, F5): el dealer elige un coche de SU inventario (nunca
// texto libre); cada afirmación numérica del copy trae su fuente. 503 honesto cuando el
// proveedor LLM no está configurado (frontera de GASTO, plans/cardeep-omni/07-marketing.md
// F5) — nunca una plantilla disfrazada de generación real.
import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { AnimatePresence, motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import {
  AlertTriangle, CheckCircle2, ChevronDown, Download, ExternalLink, FileText, Gauge,
  Radio, RefreshCw, ShieldCheck, Sparkles, Lock,
} from 'lucide-react'
import Card from '../components/Card'
import EmptyState from '../components/EmptyState'
import Button from '../components/Button'
import Select from '../components/Select'
import Table from '../components/Table'
import { Badge } from '../components/Badge'
import { Skeleton } from '../components/Skeleton'
import { Tooltip } from '../components/Tooltip'
import { PageSkeleton } from '../components/LoadingSpinner'
import PremiumGate from '../components/PremiumGate'
import { useAuthContext } from '../auth/AuthContext'
import {
  cardeep, CardeepApiError,
  type ListingAuditItem, type ListingAuditMeta, type ChannelRadar, type ChannelRadarPlatform,
  type ChannelCoverageBand, type MarketingFeedTarget, type FeedReport,
} from '../api/cardeep'
import { marketingOps, AdCopyNotConfiguredError, type AdCopyResult } from '../api/marketingOps'
import type { Plan } from '../types'
import { ACCENT, GOOD, BAD, WARN } from '../lib/theme'
import { cn } from '../lib/cn'

// Shared focus-visible ring — mirrors Button.tsx's own focus treatment so every
// ad-hoc interactive element on this page (links, icon toggles) matches house style.
const FOCUS_RING = 'outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary'

function errorMessage(err: unknown): string {
  if (err instanceof CardeepApiError) return err.message
  if (err instanceof Error) return err.message
  return 'Error desconocido al consultar la API de CARDEEP'
}

function scoreColor(score: number): string {
  if (score >= 80) return GOOD
  if (score >= 50) return WARN
  return BAD
}

// ---------------------------------------------------------------------------
// AnimNum — spring count-up for hero-style figures (same pattern as
// Inteligencia's/Api's AnimNum; kept local since it isn't extracted into a
// shared component yet).
// ---------------------------------------------------------------------------

function AnimNum({ to, decimals = 0, prefix = '', suffix = '' }: { to: number; decimals?: number; prefix?: string; suffix?: string }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 90, damping: 18 })
  const d = useTransform(sp, v => `${prefix}${decimals ? v.toFixed(decimals) : Math.round(v)}${suffix}`)
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span>{d}</motion.span>
}

// ---------------------------------------------------------------------------
// Data hook — listing audit page 1 (worst-first) + channel radar. No mocks: a
// failed request surfaces as `error`, never a silently-swapped fleet of fake rows.
// ---------------------------------------------------------------------------

function useMarketingData(cdp: string) {
  const [items, setItems] = useState<ListingAuditItem[]>([])
  const [meta, setMeta] = useState<ListingAuditMeta | null>(null)
  const [radar, setRadar] = useState<ChannelRadar | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    Promise.all([
      cardeep.listingAudit(cdp, { page: 1, size: 50 }),
      cardeep.channelRadar(cdp).catch(() => null), // radar is Capa 1 — a 403/empty is not fatal to the page
    ])
      .then(([audit, radarData]) => {
        setItems(audit.items)
        setMeta(audit.meta as unknown as ListingAuditMeta)
        setRadar(radarData)
      })
      .catch((e: unknown) => setError(errorMessage(e)))
      .finally(() => setLoading(false))
  }, [cdp])

  useEffect(() => { load() }, [load])

  return { items, meta, radar, loading, error, reload: load }
}

// ---------------------------------------------------------------------------
// Cabecera KPI
// ---------------------------------------------------------------------------

function HeaderKpis({ meta }: { meta: ListingAuditMeta }) {
  const cards = [
    {
      icon: Gauge, label: 'Nota media de anuncio',
      node: meta.avg_score != null ? <AnimNum to={meta.avg_score} suffix="/100" /> : 'Sin datos',
      sub: `${meta.audited_count.toLocaleString('es-ES')} de ${meta.total_available.toLocaleString('es-ES')} coches auditados`,
      color: meta.avg_score != null ? scoreColor(meta.avg_score) : 'var(--text-muted)',
    },
    {
      icon: AlertTriangle, label: 'Precio incoherente entre plataformas',
      node: <AnimNum to={meta.incoherent_price_count} />,
      sub: 'Google rechaza el feed por esto',
      color: meta.incoherent_price_count > 0 ? BAD : GOOD,
    },
  ]
  return (
    <div className="mb-5 grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))' }}>
      {cards.map((c, i) => (
        <motion.div
          key={c.label}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06, duration: 0.34, ease: [0.32, 0.72, 0, 1] }}
        >
          <Card hover className="!p-4">
            <div className="mb-2 flex items-center gap-1.5">
              <c.icon className="h-3.5 w-3.5" style={{ color: c.color }} />
              <span className="text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>{c.label}</span>
            </div>
            <div className="mb-1 text-[26px] font-extrabold leading-none tabular-nums" style={{ color: c.color }}>{c.node}</div>
            <div className="text-[10.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>{c.sub}</div>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Bloque 1 — "Arregla estos primero"
// ---------------------------------------------------------------------------

function AuditRow({ item, index }: { item: ListingAuditItem; index: number }) {
  const [expanded, setExpanded] = useState(false)
  const failed = item.checks.filter(c => !c.passed)
  const color = scoreColor(item.score)
  // Worst-first list (docstring above): the first row is the single highest-priority
  // fix, so it earns the glow treatment — emphasis, not sentiment (matches how Api.tsx
  // reserves `glow` for "the featured item", never for "this number is good news").
  const isTopPriority = index === 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.03, 0.4), duration: 0.3, ease: [0.32, 0.72, 0, 1] }}
    >
      <Card hover glow={isTopPriority} className="!p-3.5">
        <div className="flex items-start gap-3">
          {item.photo_url
            ? <img
                src={item.photo_url}
                alt={item.title ?? `${item.make ?? ''} ${item.model ?? ''}`.trim()}
                className="h-14 w-20 shrink-0 rounded-lg object-cover"
                style={{ background: 'var(--bg-surface)' }}
              />
            : <div className="h-14 w-20 shrink-0 rounded-lg" style={{ background: 'var(--bg-surface)' }} />}

          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-2">
              <div className="min-w-0">
                <div className="truncate text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {item.title ?? (`${item.make ?? ''} ${item.model ?? ''}`.trim() || 'Sin título')}
                </div>
                <div className="text-[10.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>
                  {item.year ?? '—'} · {item.price != null ? `${item.price.toLocaleString('es-ES')} ${item.currency ?? '€'}` : 'sin precio'}
                </div>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <div className="text-right">
                  <div className="text-[20px] font-extrabold leading-none tabular-nums" style={{ color }}>{item.score}</div>
                  <div className="text-[9px]" style={{ color: 'var(--text-muted)' }}>/100</div>
                </div>
                <motion.a
                  href={item.deep_link} target="_blank" rel="noreferrer"
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className={cn('flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-[11px] font-medium', FOCUS_RING)}
                  style={{ background: `${ACCENT}17`, border: `1px solid ${ACCENT}38`, color: ACCENT }}
                >
                  Ver anuncio <ExternalLink className="h-3 w-3" />
                </motion.a>
              </div>
            </div>

            {failed.length > 0 ? (
              <button
                onClick={() => setExpanded(e => !e)}
                aria-expanded={expanded}
                className={cn('mt-2 flex items-center gap-1.5 rounded-md', FOCUS_RING)}
              >
                <Badge color="red">
                  <AlertTriangle className="h-3 w-3" />
                  {failed.length} {failed.length === 1 ? 'problema' : 'problemas'} detectado{failed.length === 1 ? '' : 's'}
                </Badge>
                <motion.span animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }} className="flex">
                  <ChevronDown className="h-3 w-3" style={{ color: 'var(--text-muted)' }} />
                </motion.span>
              </button>
            ) : (
              <Badge color="green" className="mt-2">
                <CheckCircle2 className="h-3 w-3" /> Anuncio impecable
              </Badge>
            )}

            <AnimatePresence initial={false}>
              {expanded && failed.length > 0 && (
                <motion.div
                  key="checks"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.22, ease: [0.32, 0.72, 0, 1] }}
                  className="overflow-hidden"
                >
                  <ul className="mt-2 flex flex-col gap-1 border-t pt-2" style={{ borderColor: 'var(--border-subtle)' }}>
                    {failed.map(c => (
                      <li key={c.check_id} className="text-[11px]" style={{ color: 'var(--text-secondary)' }}>
                        <span style={{ color: BAD }}>·</span> {c.message}
                      </li>
                    ))}
                  </ul>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

function FixThisFirstBlock({ items }: { items: ListingAuditItem[] }) {
  const shown = items.slice(0, 20)
  return (
    <div className="mb-6">
      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="mb-3">
        <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Arregla estos primero</h2>
        <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
          Tus coches con peor nota de anuncio, ordenados de peor a mejor.
          {items.length > 20 && ` Mostrando los 20 con peor nota de ${items.length.toLocaleString('es-ES')} cargados.`}
        </p>
      </motion.div>
      {items.length === 0 ? (
        <EmptyState icon={<ShieldCheck className="h-6 w-6" />} title="Aún sin auditoría" message="El motor de auditoría todavía no ha procesado tu inventario." />
      ) : (
        <div className="flex flex-col gap-2.5">
          {shown.map((item, i) => <AuditRow key={item.vehicle_ulid} item={item} index={i} />)}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Bloque 2 — "Radar de canales" (Capa 1)
// ---------------------------------------------------------------------------

const BAND_COLOR: Record<ChannelCoverageBand, string> = { verde: GOOD, ambar: WARN, rojo: BAD }

// Column defs for the shared Table — moved out of bespoke <table> markup so this
// block gets Table's built-in staggered row entrance for free (dataviz/foundation
// ambition), same as every other list on this page.
const RADAR_COLUMNS: { key: string; header: string; render: (p: ChannelRadarPlatform) => ReactNode }[] = [
  {
    key: 'platform', header: 'Plataforma',
    render: p => <span className="text-[12px] font-semibold" style={{ color: 'var(--text-primary)' }}>{p.trade_name ?? p.cdp_code}</span>,
  },
  {
    key: 'coverage', header: 'Cobertura',
    render: p => (
      <div className="flex items-center gap-1.5">
        <span className="h-1.5 w-1.5 rounded-full" style={{ background: BAND_COLOR[p.band] }} />
        <span className="text-[12px] font-bold tabular-nums" style={{ color: BAND_COLOR[p.band] }}>{Math.round(p.coverage_pct * 100)}%</span>
        <span className="text-[10.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>({p.n_listed.toLocaleString('es-ES')})</span>
      </div>
    ),
  },
  {
    key: 'divergent', header: 'Divergencias',
    render: p => <span className="text-[12px] tabular-nums" style={{ color: p.n_divergent > 0 ? BAD : 'var(--text-secondary)' }}>{p.n_divergent.toLocaleString('es-ES')}</span>,
  },
  {
    key: 'days', header: 'Días hasta baja (mediana)',
    render: p => p.median_days_to_gone != null
      ? (
        <span className="text-[12px] tabular-nums" style={{ color: 'var(--text-secondary)' }}>
          {p.median_days_to_gone.toFixed(0)} d <span style={{ color: 'var(--text-muted)' }}>(N={p.median_days_to_gone_n})</span>
        </span>
      )
      : <span className="text-[12px]" style={{ color: 'var(--text-muted)' }}>{p.median_days_to_gone_reason}</span>,
  },
]

function ChannelRadarBlock({ radar, plan }: { radar: ChannelRadar | null; plan: Plan }) {
  return (
    <div className="mb-6">
      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="mb-3">
        <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Radar de canales</h2>
        <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>Dónde estás publicado, con qué divergencia de precio, y cuánto tardan en venderse coches como los tuyos en cada plataforma.</p>
      </motion.div>

      <PremiumGate feature="channel-radar" userPlan={plan} what="Desglose completo por plataforma: divergencia de precio y días-hasta-baja con su N">
        {!radar || radar.platforms.length === 0 ? (
          <EmptyState icon={<Radio className="h-6 w-6" />} title="Sin presencia en plataformas todavía" message="Ninguno de tus coches aparece cross-listado en otro portal ahora mismo." />
        ) : (
          <Card>
            <Table columns={RADAR_COLUMNS} data={radar.platforms} keyExtractor={p => p.cdp_code} />
          </Card>
        )}
      </PremiumGate>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Bloque 3 — "Feed listo para anunciarte"
// ---------------------------------------------------------------------------

const FEED_TARGETS: { id: MarketingFeedTarget; label: string; desc: string }[] = [
  { id: 'google_vehicle_ads', label: 'Google Vehicle Ads', desc: 'CSV compatible con Merchant Center' },
  { id: 'meta_aia', label: 'Meta (Facebook/Instagram)', desc: 'CSV para Automotive Inventory Ads' },
  { id: 'schema_org_jsonld', label: 'Datos estructurados', desc: 'JSON-LD schema.org para tu web' },
]

function FeedCard({ cdp, target, label, desc, index }: { cdp: string; target: MarketingFeedTarget; label: string; desc: string; index: number }) {
  const [report, setReport] = useState<FeedReport | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    cardeep.feedReport(cdp, target)
      .then(setReport)
      .catch(() => setReport(null)) // no export generated yet — honest empty, not an error banner
      .finally(() => setLoading(false))
  }, [cdp, target])

  const validPct = report?.valid_pct
  const color = validPct == null ? 'var(--text-muted)' : validPct >= 80 ? GOOD : validPct >= 40 ? WARN : BAD

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.32, ease: [0.32, 0.72, 0, 1] }}
    >
      <Card hover className="!p-4">
        <div className="mb-2 flex items-center gap-1.5">
          <FileText className="h-3.5 w-3.5" style={{ color: ACCENT }} />
          <span className="text-[12.5px] font-bold" style={{ color: 'var(--text-primary)' }}>{label}</span>
        </div>
        <p className="mb-3 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{desc}</p>

        {loading ? (
          <Skeleton className="mb-3 h-6 w-16" />
        ) : (
          <div className="mb-3 text-[22px] font-extrabold leading-none tabular-nums" style={{ color }}>
            {validPct != null ? <AnimNum to={validPct} suffix="%" /> : '—'}
            <span className="ml-1.5 text-[10.5px] font-normal" style={{ color: 'var(--text-muted)' }}>válido</span>
          </div>
        )}
        {report && report.item_count > report.valid_count && (
          <p className="mb-3 text-[10.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>
            {(report.item_count - report.valid_count).toLocaleString('es-ES')} de {report.item_count.toLocaleString('es-ES')} coches excluidos (ver informe al descargar)
          </p>
        )}

        <motion.a
          href={cardeep.feedDownloadUrl(cdp, target)} download
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={cn('flex w-full items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-[11.5px] font-semibold', FOCUS_RING)}
          style={{ background: `${ACCENT}17`, border: `1px solid ${ACCENT}38`, color: ACCENT }}
        >
          <Download className="h-3.5 w-3.5" /> Descargar
        </motion.a>
      </Card>
    </motion.div>
  )
}

function FeedBlock({ cdp }: { cdp: string }) {
  return (
    <div className="mb-6">
      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="mb-3">
        <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Feed listo para anunciarte</h2>
        <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
          Cardeep genera el fichero; la campaña la creas y pagas tú en tu cuenta de Google/Meta.
        </p>
      </motion.div>
      <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))' }}>
        {FEED_TARGETS.map((t, i) => <FeedCard key={t.id} cdp={cdp} target={t.id} label={t.label} desc={t.desc} index={i} />)}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Bloque 4 — "Descripción con pruebas" (C7, F5)
// ---------------------------------------------------------------------------

function AdCopyClaimsList({ claims }: { claims: AdCopyResult['claims'] }) {
  return (
    <ul className="mt-2 flex flex-col gap-1">
      {claims.map((c, i) => (
        <motion.li
          key={c.claim_id}
          initial={{ opacity: 0, x: -4 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.08 + i * 0.05, duration: 0.22 }}
          className="text-[10.5px]"
          style={{ color: 'var(--text-muted)' }}
        >
          <Tooltip content={c.provenance}>
            <span className="cursor-help">
              <span style={{ color: ACCENT }}>●</span> {c.text}
            </span>
          </Tooltip>
        </motion.li>
      ))}
    </ul>
  )
}

function AdCopyBlock({ items }: { items: ListingAuditItem[] }) {
  const [selected, setSelected] = useState<string>('')
  const [result, setResult] = useState<AdCopyResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [notConfigured, setNotConfigured] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const generate = useCallback(() => {
    if (!selected) return
    setLoading(true)
    setResult(null)
    setNotConfigured(null)
    setError(null)
    marketingOps.generateAdCopy(selected)
      .then(setResult)
      .catch((e: unknown) => {
        if (e instanceof AdCopyNotConfiguredError) setNotConfigured(e.message)
        else setError(e instanceof Error ? e.message : 'Error al generar la descripción')
      })
      .finally(() => setLoading(false))
  }, [selected])

  const vehicleOptions = items.map(i => ({
    value: i.vehicle_ulid,
    label: `${i.title ?? `${i.make ?? ''} ${i.model ?? ''}`.trim()}${i.year ? ` (${i.year})` : ''}`,
  }))

  return (
    <div className="mb-6">
      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="mb-3">
        <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Descripción con pruebas</h2>
        <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
          Elige un coche de tu inventario. Cada afirmación del texto trae su fuente — nunca un dato inventado.
        </p>
      </motion.div>

      <Card className="!p-4">
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="min-w-[240px] flex-1">
            <Select
              value={selected}
              onChange={e => { setSelected(e.target.value); setResult(null); setNotConfigured(null); setError(null) }}
              options={vehicleOptions}
              placeholder="Selecciona un coche de tu inventario…"
            />
          </div>
          <Button onClick={generate} disabled={!selected} loading={loading} icon={<Sparkles className="h-3.5 w-3.5" />}>
            {loading ? 'Generando…' : 'Generar descripción'}
          </Button>
        </div>

        <AnimatePresence mode="wait">
          {notConfigured && (
            <motion.div
              key="not-configured"
              initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.22 }}
              className="mt-3.5 flex items-start gap-2 rounded-lg p-3"
              style={{ background: `${WARN}14`, border: `1px solid ${WARN}38` }}
            >
              <Lock className="mt-0.5 h-3.5 w-3.5 shrink-0" style={{ color: WARN }} />
              <p className="text-[11.5px]" style={{ color: 'var(--text-secondary)' }}>
                Generación no disponible todavía: requiere que el propietario active un proveedor de IA y apruebe
                el presupuesto por generación. El motor está listo — solo falta esa activación.
              </p>
            </motion.div>
          )}

          {error && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.22 }}
              className="mt-3.5 rounded-lg p-3"
              style={{ background: `${BAD}14`, border: `1px solid ${BAD}38` }}
            >
              <p className="text-[11.5px]" style={{ color: BAD }}>{error}</p>
            </motion.div>
          )}

          {result && result.status === 'rejected' && (
            <motion.div
              key="rejected"
              initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.22 }}
              className="mt-3.5 rounded-lg p-3"
              style={{ background: `${BAD}14`, border: `1px solid ${BAD}38` }}
            >
              <p className="text-[11.5px] font-semibold" style={{ color: BAD }}>
                Generación rechazada: contenía cifras sin respaldo verificado ({result.unbacked_numerals.join(', ')}).
              </p>
            </motion.div>
          )}

          {result && result.status === 'grounded' && result.output_text && (
            <motion.div
              key="grounded"
              initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.22 }}
              className="mt-3.5 rounded-lg p-3.5"
              style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
            >
              <p className="text-[12.5px] leading-relaxed" style={{ color: 'var(--text-primary)' }}>{result.output_text}</p>
              <AdCopyClaimsList claims={result.claims} />
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

function MarketingForDealer({ cdp, plan }: { cdp: string; plan: Plan }) {
  const { items, meta, radar, loading, error, reload } = useMarketingData(cdp)

  if (loading && items.length === 0 && !meta) return <PageSkeleton />

  if (error && items.length === 0) {
    return (
      <div style={{ padding: '24px 28px' }}>
        <EmptyState icon={<AlertTriangle className="h-6 w-6" />} title="No se pudo cargar Marketing" message={error} action={<Button onClick={reload}>Reintentar</Button>} />
      </div>
    )
  }

  return (
    <div className="mx-auto p-[20px_24px_48px]" style={{ maxWidth: 1400 }}>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.32, ease: [0.32, 0.72, 0, 1] }}
        className="mb-5 flex items-center justify-between"
      >
        <div>
          <h1 className="mb-1 text-[20px] font-bold" style={{ color: 'var(--text-primary)' }}>Tus anuncios, auditados contra el mercado real</h1>
          <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Cada afirmación anclada en el censo cross-plataforma verificado — nunca un texto genérico.</p>
        </div>
        <motion.button
          onClick={reload}
          disabled={loading}
          whileHover={loading ? undefined : { scale: 1.03, background: 'var(--bg-hover)' }}
          whileTap={loading ? undefined : { scale: 0.96 }}
          className={cn('flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[11px] disabled:opacity-50 disabled:pointer-events-none', FOCUS_RING)}
          style={{ color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)' }}
        >
          <RefreshCw className={cn('h-3 w-3', loading && 'animate-spin')} /> Actualizar
        </motion.button>
      </motion.div>

      {meta && <HeaderKpis meta={meta} />}
      <FixThisFirstBlock items={items} />
      <ChannelRadarBlock radar={radar} plan={plan} />
      <FeedBlock cdp={cdp} />
      <AdCopyBlock items={items} />
    </div>
  )
}

export default function Marketing() {
  const { user } = useAuthContext()
  const cdp = user?.tenantId || null
  const plan: Plan = user?.plan ?? 'starter'

  if (!cdp) {
    return (
      <div style={{ padding: '24px 28px' }}>
        <EmptyState
          icon={<ShieldCheck className="h-6 w-6" />}
          title="Sin perfil de dealer"
          message="Reclama tu ficha de dealer (Ajustes → Reclamar dealer) para auditar tus anuncios contra el mercado real."
        />
      </div>
    )
  }

  return <MarketingForDealer cdp={cdp} plan={plan} />
}
