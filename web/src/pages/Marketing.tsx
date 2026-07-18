// Marketing — pilar 07-marketing (plans/cardeep-omni/07-marketing.md).
// "Tus anuncios, auditados contra el mercado real" — el mejor auditor + generador de
// anuncios de coche de España, cada afirmación anclada en el censo verificado.
//
// Dealer scope: misma convención que 03-garage-fleet/05-multiposting — useAuthContext()
// .user.tenantId (AUTH-0), nunca un cdp hardcoded.
//
// Bloques 1-3 (F4): "Arregla estos primero" (C1, gratis), "Radar de canales" (C3/C4/C5,
// Capa 1 — PremiumGate), "Feed listo para anunciarte" (C6, generación gratis). Bloque 4
// ("Descripción con pruebas", C7) llega en F5 — no simulado aquí mientras tanto.
import { useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  AlertTriangle, CheckCircle2, Download, ExternalLink, FileText, Gauge,
  Radio, RefreshCw, ShieldCheck,
} from 'lucide-react'
import Card from '../components/Card'
import EmptyState from '../components/EmptyState'
import Button from '../components/Button'
import { PageSkeleton } from '../components/LoadingSpinner'
import PremiumGate from '../components/PremiumGate'
import { useAuthContext } from '../auth/AuthContext'
import {
  cardeep, CardeepApiError,
  type ListingAuditItem, type ListingAuditMeta, type ChannelRadar,
  type ChannelCoverageBand, type MarketingFeedTarget, type FeedReport,
} from '../api/cardeep'
import type { Plan } from '../types'
import { ACCENT, GOOD, BAD, WARN } from '../lib/theme'
import { cn } from '../lib/cn'

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
      value: meta.avg_score != null ? `${meta.avg_score.toFixed(0)}/100` : 'Sin datos',
      sub: `${meta.audited_count.toLocaleString()} de ${meta.total_available.toLocaleString()} coches auditados`,
      color: meta.avg_score != null ? scoreColor(meta.avg_score) : 'var(--text-muted)',
    },
    {
      icon: AlertTriangle, label: 'Precio incoherente entre plataformas',
      value: meta.incoherent_price_count.toLocaleString(),
      sub: 'Google rechaza el feed por esto', color: meta.incoherent_price_count > 0 ? BAD : GOOD,
    },
  ]
  return (
    <div className="mb-5 grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))' }}>
      {cards.map((c, i) => (
        <motion.div key={c.label} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
          <Card className="!p-4">
            <div className="mb-2 flex items-center gap-1.5">
              <c.icon className="h-3.5 w-3.5" style={{ color: c.color }} />
              <span className="text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>{c.label}</span>
            </div>
            <div className="mb-1 text-[26px] font-extrabold leading-none" style={{ color: c.color }}>{c.value}</div>
            <div className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{c.sub}</div>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Bloque 1 — "Arregla estos primero"
// ---------------------------------------------------------------------------

function AuditRow({ item }: { item: ListingAuditItem }) {
  const [expanded, setExpanded] = useState(false)
  const failed = item.checks.filter(c => !c.passed)
  const color = scoreColor(item.score)

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}>
      <Card className="!p-3.5">
        <div className="flex items-start gap-3">
          {item.photo_url
            ? <img src={item.photo_url} alt="" className="h-14 w-20 shrink-0 rounded-lg object-cover" style={{ background: 'var(--bg-surface)' }} />
            : <div className="h-14 w-20 shrink-0 rounded-lg" style={{ background: 'var(--bg-surface)' }} />}

          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-2">
              <div className="min-w-0">
                <div className="truncate text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {item.title ?? (`${item.make ?? ''} ${item.model ?? ''}`.trim() || 'Sin título')}
                </div>
                <div className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
                  {item.year ?? '—'} · {item.price != null ? `${item.price.toLocaleString('es-ES')} ${item.currency ?? '€'}` : 'sin precio'}
                </div>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <div className="text-right">
                  <div className="text-[20px] font-extrabold leading-none" style={{ color }}>{item.score}</div>
                  <div className="text-[9px]" style={{ color: 'var(--text-muted)' }}>/100</div>
                </div>
                <a href={item.deep_link} target="_blank" rel="noreferrer"
                   className="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-[11px] font-medium"
                   style={{ background: `${ACCENT}17`, border: `1px solid ${ACCENT}38`, color: ACCENT }}>
                  Ver anuncio <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            </div>

            {failed.length > 0 ? (
              <button onClick={() => setExpanded(e => !e)} className="mt-2 text-left text-[11px] font-medium" style={{ color: BAD }}>
                {failed.length} {failed.length === 1 ? 'problema' : 'problemas'} detectado{failed.length === 1 ? '' : 's'} {expanded ? '▲' : '▼'}
              </button>
            ) : (
              <div className="mt-2 flex items-center gap-1.5 text-[11px]" style={{ color: GOOD }}>
                <CheckCircle2 className="h-3 w-3" /> Anuncio impecable
              </div>
            )}

            {expanded && (
              <ul className="mt-2 flex flex-col gap-1 border-t pt-2" style={{ borderColor: 'var(--border-subtle)' }}>
                {failed.map(c => (
                  <li key={c.check_id} className="text-[11px]" style={{ color: 'var(--text-secondary)' }}>
                    <span style={{ color: BAD }}>·</span> {c.message}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

function FixThisFirstBlock({ items }: { items: ListingAuditItem[] }) {
  return (
    <div className="mb-6">
      <div className="mb-3">
        <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Arregla estos primero</h2>
        <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>Tus coches con peor nota de anuncio, ordenados de peor a mejor.</p>
      </div>
      {items.length === 0 ? (
        <EmptyState icon={<ShieldCheck className="h-6 w-6" />} title="Aún sin auditoría" message="El motor de auditoría todavía no ha procesado tu inventario." />
      ) : (
        <div className="flex flex-col gap-2.5">
          {items.slice(0, 20).map(item => <AuditRow key={item.vehicle_ulid} item={item} />)}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Bloque 2 — "Radar de canales" (Capa 1)
// ---------------------------------------------------------------------------

const BAND_COLOR: Record<ChannelCoverageBand, string> = { verde: GOOD, ambar: WARN, rojo: BAD }

function ChannelRadarBlock({ radar, plan }: { radar: ChannelRadar | null; plan: Plan }) {
  return (
    <div className="mb-6">
      <div className="mb-3">
        <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Radar de canales</h2>
        <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>Dónde estás publicado, con qué divergencia de precio, y cuánto tardan en venderse coches como los tuyos en cada plataforma.</p>
      </div>

      <PremiumGate feature="channel-radar" userPlan={plan} what="Desglose completo por plataforma: divergencia de precio y días-hasta-baja con su N">
        {!radar || radar.platforms.length === 0 ? (
          <EmptyState icon={<Radio className="h-6 w-6" />} title="Sin presencia en plataformas todavía" message="Ninguno de tus coches aparece cross-listado en otro portal ahora mismo." />
        ) : (
          <Card className="!p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-left">
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    {['Plataforma', 'Cobertura', 'Divergencias', 'Días hasta baja (mediana)'].map(h => (
                      <th key={h} className="whitespace-nowrap p-3 text-[10.5px] font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {radar.platforms.map(p => (
                    <tr key={p.cdp_code} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td className="p-3 text-[12px] font-semibold" style={{ color: 'var(--text-primary)' }}>{p.trade_name ?? p.cdp_code}</td>
                      <td className="p-3">
                        <div className="flex items-center gap-1.5">
                          <span className="h-1.5 w-1.5 rounded-full" style={{ background: BAND_COLOR[p.band] }} />
                          <span className="text-[12px] font-bold" style={{ color: BAND_COLOR[p.band] }}>{Math.round(p.coverage_pct * 100)}%</span>
                          <span className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>({p.n_listed})</span>
                        </div>
                      </td>
                      <td className="p-3 text-[12px]" style={{ color: p.n_divergent > 0 ? BAD : 'var(--text-secondary)' }}>{p.n_divergent}</td>
                      <td className="p-3 text-[12px]" style={{ color: 'var(--text-secondary)' }}>
                        {p.median_days_to_gone != null
                          ? <>{p.median_days_to_gone.toFixed(0)} d <span style={{ color: 'var(--text-muted)' }}>(N={p.median_days_to_gone_n})</span></>
                          : <span style={{ color: 'var(--text-muted)' }}>{p.median_days_to_gone_reason}</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
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

function FeedCard({ cdp, target, label, desc }: { cdp: string; target: MarketingFeedTarget; label: string; desc: string }) {
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
    <Card className="!p-4">
      <div className="mb-2 flex items-center gap-1.5">
        <FileText className="h-3.5 w-3.5" style={{ color: ACCENT }} />
        <span className="text-[12.5px] font-bold" style={{ color: 'var(--text-primary)' }}>{label}</span>
      </div>
      <p className="mb-3 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{desc}</p>

      {loading ? (
        <div className="mb-3 h-6 w-16 animate-pulse rounded" style={{ background: 'var(--bg-surface)' }} />
      ) : (
        <div className="mb-3 text-[22px] font-extrabold leading-none" style={{ color }}>
          {validPct != null ? `${validPct.toFixed(0)}%` : '—'}
          <span className="ml-1.5 text-[10.5px] font-normal" style={{ color: 'var(--text-muted)' }}>válido</span>
        </div>
      )}
      {report && report.item_count > report.valid_count && (
        <p className="mb-3 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
          {report.item_count - report.valid_count} de {report.item_count} coches excluidos (ver informe al descargar)
        </p>
      )}

      <a href={cardeep.feedDownloadUrl(cdp, target)} download
         className="flex w-full items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-[11.5px] font-semibold"
         style={{ background: `${ACCENT}17`, border: `1px solid ${ACCENT}38`, color: ACCENT }}>
        <Download className="h-3.5 w-3.5" /> Descargar
      </a>
    </Card>
  )
}

function FeedBlock({ cdp }: { cdp: string }) {
  return (
    <div className="mb-6">
      <div className="mb-3">
        <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Feed listo para anunciarte</h2>
        <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
          Cardeep genera el fichero; la campaña la creas y pagas tú en tu cuenta de Google/Meta.
        </p>
      </div>
      <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))' }}>
        {FEED_TARGETS.map(t => <FeedCard key={t.id} cdp={cdp} target={t.id} label={t.label} desc={t.desc} />)}
      </div>
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
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h1 className="mb-1 text-[20px] font-bold" style={{ color: 'var(--text-primary)' }}>Tus anuncios, auditados contra el mercado real</h1>
          <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Cada afirmación anclada en el censo cross-plataforma verificado — nunca un texto genérico.</p>
        </div>
        <button onClick={reload} className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[11px]" style={{ color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)' }}>
          <RefreshCw className={cn('h-3 w-3', loading && 'animate-spin')} /> Actualizar
        </button>
      </div>

      {meta && <HeaderKpis meta={meta} />}
      <FixThisFirstBlock items={items} />
      <ChannelRadarBlock radar={radar} plan={plan} />
      <FeedBlock cdp={cdp} />
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
