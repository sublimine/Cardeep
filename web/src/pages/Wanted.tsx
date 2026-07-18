// web/src/pages/Wanted.tsx — 08-forum-community F3: "/community/wanted", the tablón "Se
// busca" (carta §6.1, PRIORITY 1 of the pilar). Real data end-to-end against
// services/api/routers/wanted.py — zero mocks (grep-verifiable: no MOCK_*/SEED constant
// in this file).
import { useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Search, MapPin, Clock, TrendingUp, ExternalLink, CheckCircle2, X, Star, Users,
} from 'lucide-react'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import Select from '../components/Select'
import Modal from '../components/Modal'
import EmptyState from '../components/EmptyState'
import { Badge } from '../components/Badge'
import { PageSkeleton } from '../components/LoadingSpinner'
import { Tabs } from '../components/Tabs'
import { useToast } from '../components/Toast'
import { ApiError } from '../api/client'
import {
  wantedApi,
  type WantedListing, type WantedMatch, type ProvinceOption, type Pulse, type DemandRow, type Liveness,
} from '../api/wanted'

const TTL_OPTIONS = [
  { value: '7', label: '7 días' },
  { value: '14', label: '14 días' },
  { value: '30', label: '30 días' },
  { value: '60', label: '60 días' },
]

const FUEL_OPTIONS = [
  { value: 'gasolina', label: 'Gasolina' },
  { value: 'diesel', label: 'Diésel' },
  { value: 'hibrido', label: 'Híbrido' },
  { value: 'electrico', label: 'Eléctrico' },
  { value: 'glp', label: 'GLP' },
]

const CLOSE_REASON_OPTIONS = [
  { value: 'bought_via_cardeep', label: 'Comprado vía Cardeep' },
  { value: 'bought_elsewhere', label: 'Comprado fuera' },
  { value: 'no_longer_interested', label: 'Ya no me interesa' },
]

function errorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    // wanted.py's validation/authorization errors raise plain FastAPI HTTPException
    // ({"detail": "..."}), unlike its ok()-enveloped success responses (module docstring
    // of services/api/routers/wanted.py) — try to unwrap that shape first.
    try {
      const parsed = JSON.parse(err.message) as { detail?: string }
      if (parsed.detail) return parsed.detail
    } catch {
      /* not JSON — fall through to the raw message */
    }
    return err.message
  }
  if (err instanceof Error) return err.message
  return 'Error desconocido'
}

// ---------------------------------------------------------------------------
// Hero pulse (carta §4.9) — three numbers, never fabricated.
// ---------------------------------------------------------------------------

function PulseHero({ pulse, liveness }: { pulse: Pulse | null; liveness: Liveness | null }) {
  return (
    <div className="mb-6 grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))' }}>
      <Card className="!p-4">
        <div className="text-[11px] uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Peticiones abiertas</div>
        <div className="mt-1 text-[26px] font-extrabold" style={{ color: 'var(--text-primary)' }}>{pulse?.wanted_open ?? '—'}</div>
      </Card>
      <Card className="!p-4">
        <div className="text-[11px] uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Coincidencias servidas (7d)</div>
        <div className="mt-1 text-[26px] font-extrabold" style={{ color: 'var(--text-primary)' }}>{pulse?.matches_served_7d ?? '—'}</div>
      </Card>
      <Card className="!p-4">
        <div className="text-[11px] uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Hilos activos (24h)</div>
        <div className="mt-1 text-[26px] font-extrabold" style={{ color: 'var(--text-primary)' }}>{pulse?.threads_active_24h ?? '—'}</div>
        <div className="mt-0.5 text-[10px]" style={{ color: 'var(--text-muted)' }}>Foro: próxima fase</div>
      </Card>
      <Card className="!p-4">
        <div className="text-[11px] uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Tasa de coincidencia viva (30d)</div>
        <div className="mt-1 text-[26px] font-extrabold" style={{ color: 'var(--text-primary)' }}>
          {liveness?.match_liveness_rate != null ? `${Math.round(liveness.match_liveness_rate * 100)}%` : '—'}
        </div>
        <div className="mt-0.5 text-[10px]" style={{ color: 'var(--text-muted)' }}>
          {liveness ? `${liveness.live_at_click}/${liveness.total_clicks} clics con coche aún disponible` : 'Sin clics todavía'}
        </div>
      </Card>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Publish form
// ---------------------------------------------------------------------------

interface PublishFormProps {
  provinces: ProvinceOption[]
  onPublished: (listing: WantedListing, matchesNow: number, top: WantedMatch[]) => void
}

function PublishForm({ provinces, onPublished }: PublishFormProps) {
  const { error: toastErr, success } = useToast()
  const [make, setMake] = useState('')
  const [model, setModel] = useState('')
  const [yearMin, setYearMin] = useState('')
  const [yearMax, setYearMax] = useState('')
  const [kmMax, setKmMax] = useState('')
  const [priceMax, setPriceMax] = useState('')
  const [fuel, setFuel] = useState('')
  const [province, setProvince] = useState('')
  const [ttlDays, setTtlDays] = useState('30')
  const [submitting, setSubmitting] = useState(false)

  const submit = useCallback(async () => {
    if (!make.trim() || !province) {
      toastErr('Marca y provincia son obligatorias')
      return
    }
    setSubmitting(true)
    try {
      const { data, meta } = await wantedApi.create({
        make: make.trim(),
        model: model.trim() || null,
        year_min: yearMin ? Number(yearMin) : null,
        year_max: yearMax ? Number(yearMax) : null,
        km_max: kmMax ? Number(kmMax) : null,
        price_max: priceMax ? Number(priceMax) : null,
        fuel: fuel || null,
        province_code: province,
        ttl_days: Number(ttlDays) as 7 | 14 | 30 | 60,
      })
      const matchesNow = (meta.matches_now as number) ?? 0
      const top = (meta.top_matches as WantedMatch[]) ?? []
      success(`Búsqueda publicada — ${matchesNow} coincidencias ahora mismo`)
      onPublished(data, matchesNow, top)
      setMake(''); setModel(''); setYearMin(''); setYearMax(''); setKmMax(''); setPriceMax(''); setFuel('')
    } catch (err) {
      toastErr(errorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }, [make, model, yearMin, yearMax, kmMax, priceMax, fuel, province, ttlDays, onPublished, success, toastErr])

  return (
    <Card className="mb-6">
      <div className="mb-4 flex items-center gap-2">
        <Search className="h-4 w-4" style={{ color: 'var(--accent-blue, #3b82f6)' }} />
        <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Publicar búsqueda</h2>
      </div>
      <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))' }}>
        <Input label="Marca" placeholder="Volkswagen" value={make} onChange={(e) => setMake(e.target.value)} />
        <Input label="Modelo (opcional)" placeholder="Golf" value={model} onChange={(e) => setModel(e.target.value)} />
        <Input label="Año desde" type="number" value={yearMin} onChange={(e) => setYearMin(e.target.value)} />
        <Input label="Año hasta" type="number" value={yearMax} onChange={(e) => setYearMax(e.target.value)} />
        <Input label="Km máx." type="number" value={kmMax} onChange={(e) => setKmMax(e.target.value)} />
        <Input label="Precio máx. (€)" type="number" value={priceMax} onChange={(e) => setPriceMax(e.target.value)} />
        <Select label="Combustible" placeholder="Cualquiera" options={FUEL_OPTIONS} value={fuel} onChange={(e) => setFuel(e.target.value)} />
        <Select
          label="Provincia"
          placeholder="Selecciona"
          options={provinces.map((p) => ({ value: p.code, label: p.name }))}
          value={province}
          onChange={(e) => setProvince(e.target.value)}
        />
        <Select label="Vigencia" options={TTL_OPTIONS} value={ttlDays} onChange={(e) => setTtlDays(e.target.value)} />
      </div>
      <div className="mt-4 flex justify-end">
        <Button onClick={submit} loading={submitting} icon={<Search className="h-4 w-4" />}>
          Publicar búsqueda
        </Button>
      </div>
    </Card>
  )
}

// ---------------------------------------------------------------------------
// Match row
// ---------------------------------------------------------------------------

function MatchRow({ match, onClickThrough, onReview }: {
  match: WantedMatch
  onClickThrough: (m: WantedMatch) => void
  onReview: (m: WantedMatch) => void
}) {
  return (
    <div className="flex items-center gap-3 rounded-lg p-3" style={{ border: '1px solid var(--border-subtle)' }}>
      {match.photo_url
        ? <img src={match.photo_url} alt="" className="h-14 w-20 shrink-0 rounded object-cover" style={{ background: 'var(--bg-surface)' }} />
        : <div className="h-14 w-20 shrink-0 rounded" style={{ background: 'var(--bg-surface)' }} />}
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            {match.make} {match.model}
          </span>
          <Badge color={match.match_score >= 70 ? 'green' : match.match_score >= 50 ? 'yellow' : 'gray'}>
            {Math.round(match.match_score)} pts
          </Badge>
        </div>
        <div className="mt-0.5 text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
          {match.year ?? '—'} · {match.km != null ? `${match.km.toLocaleString('es-ES')} km` : '—'} ·{' '}
          {match.price != null ? `${match.price.toLocaleString('es-ES')} €` : 'sin precio'}
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        {match.deep_link && (
          <a
            href={match.deep_link}
            target="_blank"
            rel="noreferrer"
            onClick={() => onClickThrough(match)}
            className="inline-flex items-center gap-1 rounded-md px-2.5 py-1.5 text-[11.5px] font-medium"
            style={{ border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}
          >
            Ver anuncio <ExternalLink className="h-3 w-3" />
          </a>
        )}
        {match.clicked_at && (
          <button
            onClick={() => onReview(match)}
            className="inline-flex items-center gap-1 rounded-md px-2.5 py-1.5 text-[11.5px] font-medium"
            style={{ border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}
          >
            <Star className="h-3 w-3" /> Valorar
          </button>
        )}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Review modal (carta §4.6 — 4 named axes + veredicto global, double-blind)
// ---------------------------------------------------------------------------

function StarPicker({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((n) => (
        <button key={n} type="button" onClick={() => onChange(n)}>
          <Star
            className="h-5 w-5"
            fill={n <= value ? 'currentColor' : 'none'}
            style={{ color: n <= value ? '#f59e0b' : 'var(--text-muted)' }}
          />
        </button>
      ))}
    </div>
  )
}

function ReviewModal({ match, onClose, onSubmitted }: {
  match: WantedMatch | null
  onClose: () => void
  onSubmitted: () => void
}) {
  const { error: toastErr, success } = useToast()
  const [trato, setTrato] = useState(5)
  const [veraz, setVeraz] = useState(5)
  const [disponibilidad, setDisponibilidad] = useState(5)
  const [agilidad, setAgilidad] = useState(5)
  const [overall, setOverall] = useState(5)
  const [comment, setComment] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const submit = useCallback(async () => {
    if (!match) return
    setSubmitting(true)
    try {
      const { data } = await wantedApi.submitReview(match.wanted_match_ulid, {
        axis_trato: trato, axis_anuncio_veraz: veraz, axis_disponibilidad_real: disponibilidad,
        axis_agilidad: agilidad, overall, comment: comment.trim() || null, reviewer_role: 'buyer',
      })
      success(
        data.revealed
          ? 'Valoración publicada'
          : 'Valoración guardada — se revelará cuando el dealer responda o pasen 14 días (doble ciego)',
      )
      onSubmitted()
      onClose()
    } catch (err) {
      toastErr(errorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }, [match, trato, veraz, disponibilidad, agilidad, overall, comment, success, toastErr, onSubmitted, onClose])

  return (
    <Modal open={match !== null} onClose={onClose} title="Valorar al dealer" size="md">
      <div className="space-y-4">
        {[
          { label: 'Trato', value: trato, set: setTrato },
          { label: 'Anuncio veraz', value: veraz, set: setVeraz },
          { label: 'Disponibilidad real', value: disponibilidad, set: setDisponibilidad },
          { label: 'Agilidad', value: agilidad, set: setAgilidad },
        ].map((axis) => (
          <div key={axis.label} className="flex items-center justify-between">
            <span className="text-[13px]" style={{ color: 'var(--text-primary)' }}>{axis.label}</span>
            <StarPicker value={axis.value} onChange={axis.set} />
          </div>
        ))}
        <div className="flex items-center justify-between border-t pt-3" style={{ borderColor: 'var(--border-subtle)' }}>
          <span className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>Veredicto global</span>
          <StarPicker value={overall} onChange={setOverall} />
        </div>
        <textarea
          className="w-full rounded-md p-3 text-sm"
          style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}
          rows={3}
          placeholder="Comentario (opcional)"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
        <p className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
          Doble ciego (Airbnb): ni tú ni el dealer veréis la valoración del otro hasta que ambos
          hayáis enviado la vuestra, o hasta que pasen 14 días.
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button onClick={submit} loading={submitting}>Enviar valoración</Button>
        </div>
      </div>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Listing card (with expandable matches)
// ---------------------------------------------------------------------------

function ListingCard({ listing, onChanged }: { listing: WantedListing; onChanged: () => void }) {
  const { error: toastErr, success } = useToast()
  const [expanded, setExpanded] = useState(false)
  const [matches, setMatches] = useState<WantedMatch[] | null>(null)
  const [loadingMatches, setLoadingMatches] = useState(false)
  const [closing, setClosing] = useState(false)
  const [closeReason, setCloseReason] = useState('no_longer_interested')
  const [reviewTarget, setReviewTarget] = useState<WantedMatch | null>(null)

  const loadMatches = useCallback(async () => {
    setLoadingMatches(true)
    try {
      const { data } = await wantedApi.matches(listing.wanted_ulid, 1, 100)
      setMatches(data)
    } catch (err) {
      toastErr(errorMessage(err))
    } finally {
      setLoadingMatches(false)
    }
  }, [listing.wanted_ulid, toastErr])

  useEffect(() => {
    if (expanded && matches === null) void loadMatches()
  }, [expanded, matches, loadMatches])

  const handleClickThrough = useCallback((m: WantedMatch) => {
    wantedApi.clickMatch(m.wanted_match_ulid).catch(() => {})
    setMatches((prev) => prev?.map((x) => (x.wanted_match_ulid === m.wanted_match_ulid ? { ...x, clicked_at: new Date().toISOString() } : x)) ?? null)
  }, [])

  const handleClose = useCallback(async () => {
    setClosing(true)
    try {
      await wantedApi.close(listing.wanted_ulid, closeReason as 'bought_via_cardeep' | 'bought_elsewhere' | 'no_longer_interested')
      success('Búsqueda cerrada')
      onChanged()
    } catch (err) {
      toastErr(errorMessage(err))
    } finally {
      setClosing(false)
    }
  }, [listing.wanted_ulid, closeReason, onChanged, success, toastErr])

  const daysLeft = Math.max(0, Math.ceil((new Date(listing.expires_at).getTime() - Date.now()) / 86_400_000))

  return (
    <Card className="mb-3">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0 cursor-pointer" onClick={() => setExpanded((e) => !e)}>
          <div className="flex items-center gap-2">
            <span className="text-[14px] font-bold" style={{ color: 'var(--text-primary)' }}>{listing.make} {listing.model}</span>
            <Badge color={listing.status === 'open' ? 'green' : listing.status === 'closed' ? 'gray' : 'yellow'}>
              {listing.status}
            </Badge>
          </div>
          <div className="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-0.5 text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
            {(listing.year_min || listing.year_max) && <span>{listing.year_min ?? '—'}–{listing.year_max ?? '—'}</span>}
            {listing.km_max && <span>≤{listing.km_max.toLocaleString('es-ES')} km</span>}
            {listing.price_max && <span>≤{listing.price_max.toLocaleString('es-ES')} €</span>}
            <span className="inline-flex items-center gap-1"><MapPin className="h-3 w-3" /> {listing.province_code}</span>
            {listing.status === 'open' && (
              <span className="inline-flex items-center gap-1"><Clock className="h-3 w-3" /> caduca en {daysLeft}d</span>
            )}
          </div>
        </div>
        {listing.status === 'open' && (
          <div className="flex shrink-0 items-center gap-2">
            <Select
              options={CLOSE_REASON_OPTIONS}
              value={closeReason}
              onChange={(e) => setCloseReason(e.target.value)}
              className="!w-auto !py-1.5 text-[11.5px]"
            />
            <Button size="sm" variant="secondary" onClick={handleClose} loading={closing}>Cerrar</Button>
          </div>
        )}
      </div>

      {expanded && (
        <div className="mt-4 space-y-2 border-t pt-4" style={{ borderColor: 'var(--border-subtle)' }}>
          {loadingMatches && <div className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Cargando coincidencias…</div>}
          {!loadingMatches && matches?.length === 0 && (
            <div className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Sin coincidencias vivas ahora mismo.</div>
          )}
          {matches?.map((m) => (
            <MatchRow key={m.wanted_match_ulid} match={m} onClickThrough={handleClickThrough} onReview={setReviewTarget} />
          ))}
        </div>
      )}

      <ReviewModal match={reviewTarget} onClose={() => setReviewTarget(null)} onSubmitted={onChanged} />
    </Card>
  )
}

// ---------------------------------------------------------------------------
// Demand aggregate (carta §6.1 "cara pública del tablón")
// ---------------------------------------------------------------------------

function DemandPanel({ demand }: { demand: DemandRow[] }) {
  if (demand.length === 0) {
    return (
      <EmptyState
        icon={<Users className="h-6 w-6" />}
        title="Sin demanda agregada todavía"
        message="En cuanto haya peticiones abiertas, aquí verás qué busca el mercado por provincia."
      />
    )
  }
  return (
    <div className="space-y-1.5">
      {demand.slice(0, 15).map((row, i) => (
        <div key={`${row.province_code}-${row.make}-${row.fuel ?? ''}`} className="flex items-center justify-between rounded-md px-3 py-2" style={{ background: i % 2 === 0 ? 'transparent' : 'var(--bg-surface)' }}>
          <span className="text-[12.5px]" style={{ color: 'var(--text-primary)' }}>
            <strong>{row.buyers}</strong> {row.buyers === 1 ? 'comprador busca' : 'compradores buscan'} {row.make}{row.fuel ? ` (${row.fuel})` : ''} en {row.province_name}
          </span>
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Wanted() {
  const [loading, setLoading] = useState(true)
  const [provinces, setProvinces] = useState<ProvinceOption[]>([])
  const [pulse, setPulse] = useState<Pulse | null>(null)
  const [liveness, setLiveness] = useState<Liveness | null>(null)
  const [demand, setDemand] = useState<DemandRow[]>([])
  const [mine, setMine] = useState<WantedListing[]>([])
  const [tab, setTab] = useState<'open' | 'closed'>('open')
  const [justPublished, setJustPublished] = useState<{ matchesNow: number; top: WantedMatch[] } | null>(null)

  const loadAll = useCallback(async () => {
    const [p, l, d, m] = await Promise.all([
      wantedApi.pulse().then((r) => r.data).catch(() => null),
      wantedApi.liveness().then((r) => r.data).catch(() => null),
      wantedApi.demand().then((r) => r.data).catch(() => []),
      wantedApi.listMine().then((r) => r.data).catch(() => []),
    ])
    setPulse(p); setLiveness(l); setDemand(d); setMine(m)
  }, [])

  useEffect(() => {
    wantedApi.provinces().then((r) => setProvinces(r.data)).catch(() => {})
    loadAll().finally(() => setLoading(false))
  }, [loadAll])

  const handlePublished = useCallback((listing: WantedListing, matchesNow: number, top: WantedMatch[]) => {
    setJustPublished({ matchesNow, top })
    setMine((m) => [listing, ...m])
    void loadAll()
  }, [loadAll])

  if (loading) return <PageSkeleton />

  const openListings = mine.filter((w) => w.status === 'open' || w.status === 'matched')
  const closedListings = mine.filter((w) => w.status === 'closed' || w.status === 'expired')

  return (
    <div className="mx-auto p-[20px_24px_48px]" style={{ maxWidth: 1200 }}>
      <div className="mb-5">
        <h1 className="mb-1 text-[20px] font-bold" style={{ color: 'var(--text-primary)' }}>Se busca</h1>
        <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
          Publica lo que buscas y te avisamos en cuanto aparece en cualquier plataforma del mercado — no solo en una.
        </p>
      </div>

      <PulseHero pulse={pulse} liveness={liveness} />

      <PublishForm provinces={provinces} onPublished={handlePublished} />

      {justPublished && (
        <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <Card style={{ borderColor: 'var(--accent-blue, #3b82f6)' }}>
            <div className="mb-2 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" style={{ color: '#3b82f6' }} />
              <span className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>
                Ahora mismo hay {justPublished.matchesNow.toLocaleString('es-ES')} que encajan
              </span>
              <button onClick={() => setJustPublished(null)} className="ml-auto"><X className="h-4 w-4" style={{ color: 'var(--text-muted)' }} /></button>
            </div>
            <div className="space-y-2">
              {justPublished.top.slice(0, 5).map((m) => (
                <MatchRow key={m.wanted_match_ulid} match={m} onClickThrough={() => wantedApi.clickMatch(m.wanted_match_ulid).catch(() => {})} onReview={() => {}} />
              ))}
            </div>
          </Card>
        </motion.div>
      )}

      <Tabs
        value={tab}
        onValueChange={(v) => setTab(v as 'open' | 'closed')}
        items={[
          {
            value: 'open',
            label: `Abiertas (${openListings.length})`,
            content: openListings.length === 0
              ? <EmptyState icon={<CheckCircle2 className="h-6 w-6" />} title="Sin búsquedas abiertas" message="Publica tu primera búsqueda arriba." />
              : <>{openListings.map((w) => <ListingCard key={w.wanted_ulid} listing={w} onChanged={loadAll} />)}</>,
          },
          {
            value: 'closed',
            label: `Cerradas (${closedListings.length})`,
            content: closedListings.length === 0
              ? <EmptyState icon={<CheckCircle2 className="h-6 w-6" />} title="Sin búsquedas cerradas" />
              : <>{closedListings.map((w) => <ListingCard key={w.wanted_ulid} listing={w} onChanged={loadAll} />)}</>,
          },
        ]}
      />

      <div className="mt-8">
        <h2 className="mb-3 text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Qué busca el mercado ahora</h2>
        <Card>
          <DemandPanel demand={demand} />
        </Card>
      </div>
    </div>
  )
}
