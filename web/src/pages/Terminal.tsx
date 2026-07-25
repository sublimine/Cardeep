// 09-trading-terminal Fase 3 — the real terminal, dato real, cero mock.
// Every number traces to a criterio C1-C10 of plans/cardeep-omni/09-trading-terminal.md,
// served live by /terminal/* (F2). Chart engine rescued in Fase 0 (indicators.ts/MarketChart.tsx/
// drawings.tsx/tools.ts/theme.ts) — this file wires it to REAL market_bucket_daily data instead
// of the demolished synthetic RNG generator.
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { Search, Star, Info, Plus, Check, AlertTriangle, Gauge, Clock, Newspaper } from 'lucide-react'
import { cardeep, type TerminalSymbol, type TerminalRange, type TerminalSampleVehicle, type TerminalNewsItem } from '../api/cardeep'
import EmptyState from '../components/EmptyState'
import { Skeleton } from '../components/Skeleton'
import LoadingSpinner from '../components/LoadingSpinner'
import { Badge } from '../components/Badge'
import { Tooltip } from '../components/Tooltip'
import { MarketChart, type ActiveIndicator, type ChartType, type RangeLabel } from '../components/chart-engine/MarketChart'
import { useTheme } from '../components/chart-engine/theme'
import { INDICATOR_CATALOG, type IndicatorDef } from '../components/chart-engine/indicators'
import { TOOL_GROUPS } from '../components/chart-engine/tools'
import type { Drawing } from '../components/chart-engine/drawings'
import { useTerminalSymbol } from './terminal/useTerminalSymbol'
import { getWatchlist, isWatched, toggleWatch } from './terminal/watchlist'
import Screener from './terminal/Screener'
import VehicleTicket from './terminal/VehicleTicket'
import { cn } from '../lib/cn'
import { GOOD, BAD, WARN } from '../lib/theme'

// Fase 3 reduction of the 95-tool arsenal (carta §6: "se reducen al set útil para este dato:
// líneas, medición, anotación") — cursors is the baseline interaction mode, the other three
// groups are the ones that map onto "líneas / medición / anotación".
const ENABLED_TOOL_GROUPS = new Set(['cursors', 'trend_lines', 'measure', 'text_notes'])
const REDUCED_TOOLS = TOOL_GROUPS.filter(g => ENABLED_TOOL_GROUPS.has(g.id))

// A small, useful default indicator set — the full 53-indicator catalog is available via the
// picker below, never crammed onto the chart by default.
const DEFAULT_INDICATOR_IDS = ['sma', 'ema', 'bb']
const SLIDER_SPRING = { type: 'spring', stiffness: 380, damping: 30 } as const

function useDebounced<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(t)
  }, [value, delayMs])
  return debounced
}

export default function Terminal() {
  const p = useTheme()
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounced(query, 250)
  const [searchResults, setSearchResults] = useState<TerminalSymbol[]>([])
  const [selected, setSelected] = useState<TerminalSymbol | null>(null)
  const [range, setRange] = useState<RangeLabel>('ALL')
  const [chartType] = useState<ChartType>('candle')
  const [activeIndicators, setActiveIndicators] = useState<ActiveIndicator[]>(() =>
    INDICATOR_CATALOG
      .filter(d => DEFAULT_INDICATOR_IDS.includes(d.id))
      .map(d => ({ uid: d.id, def: d, params: Object.fromEntries(d.inputs.map(i => [i.name, i.default])) })),
  )
  const [tool, setTool] = useState('cross')
  const [drawings, setDrawings] = useState<Drawing[]>([])
  const [tab, setTab] = useState<'chart' | 'screener'>('chart')
  const [ticketVehicle, setTicketVehicle] = useState<TerminalSampleVehicle | null>(null)
  const [, forceWatchlistRerender] = useState(0)
  const crossRef = useRef<unknown>(null)

  const { bars, stats, loading, error } = useTerminalSymbol(selected?.symbol_key ?? null, range as TerminalRange)
  const [news, setNews] = useState<TerminalNewsItem[]>([])

  // The terminal paints its own neutral canvas (tokens.css `body.on-terminal`) so the workspace's
  // colourful mesh never bleeds behind the trading chrome — documented in tokens.css/App.tsx but
  // never actually toggled from here until now.
  useEffect(() => {
    document.body.classList.add('on-terminal')
    return () => { document.body.classList.remove('on-terminal') }
  }, [])

  useEffect(() => {
    if (!debouncedQuery.trim()) { setSearchResults([]); return }
    let cancelled = false
    cardeep.terminalSymbols(debouncedQuery.trim())
      .then(items => { if (!cancelled) setSearchResults(items) })
      .catch(() => { if (!cancelled) setSearchResults([]) })
    return () => { cancelled = true }
  }, [debouncedQuery])

  useEffect(() => {
    // C10: fundamental externo real — solo items V5-verificados. Sin fabricación ni relleno
    // si no hay ítems para este símbolo (el panel simplemente no se muestra, per carta §6).
    let cancelled = false
    cardeep.terminalNews({ symbolKey: selected?.symbol_key, limit: 8 })
      .then(items => { if (!cancelled) setNews(items) })
      .catch(() => { if (!cancelled) setNews([]) })
    return () => { cancelled = true }
  }, [selected?.symbol_key])

  const watchlist = useMemo(() => getWatchlist(), [])
  void watchlist // referenced for the initial render; toggled state re-read on demand below

  const handleSelect = useCallback((s: TerminalSymbol) => {
    setSelected(s)
    setQuery(`${s.make} ${s.model}`)
    setSearchResults([])
  }, [])

  const toggleIndicator = useCallback((id: string) => {
    setActiveIndicators(prev => {
      if (prev.some(i => i.uid === id)) return prev.filter(i => i.uid !== id)
      const def = INDICATOR_CATALOG.find(d => d.id === id)
      if (!def) return prev
      return [...prev, { uid: id, def, params: Object.fromEntries(def.inputs.map(i => [i.name, i.default])) }]
    })
  }, [])

  const insufficient = stats && stats.insufficient_sample
  const readyStats = stats && !stats.insufficient_sample ? stats : null

  return (
    <div className="flex flex-col h-full">
      {/* Barra de mando */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-center gap-3 px-4 py-2.5 border-b border-border-subtle"
      >
        <div className="relative flex-1 max-w-md group">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted transition-colors duration-150 group-focus-within:text-accent-blue" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="320d málaga..."
            className="w-full pl-8 pr-3 py-1.5 text-sm rounded-md bg-glass-medium border border-border-subtle text-text-primary placeholder:text-text-muted outline-none transition-colors duration-150 focus-visible:border-accent-blue/50"
          />
          <AnimatePresence>
            {searchResults.length > 0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.97, y: -4 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.97, y: -4 }}
                transition={SLIDER_SPRING}
                className="absolute top-full left-0 right-0 mt-1.5 glass-lg rounded-lg z-20 max-h-64 overflow-y-auto"
              >
                {searchResults.map(s => (
                  <button
                    key={s.symbol_key}
                    onClick={() => handleSelect(s)}
                    className="w-full text-left px-3 py-2 text-sm outline-none transition-colors duration-150 hover:bg-glass-medium focus-visible:bg-glass-medium flex items-center justify-between"
                  >
                    <span className="text-text-primary">{s.make} {s.model}</span>
                    <Badge color="gray">{s.province_code ?? 'ES'}</Badge>
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="flex items-center gap-0.5 p-0.5 rounded-lg glass">
          {(['1M', '3M', '6M', '1Y', 'ALL'] as RangeLabel[]).map(r => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={cn(
                'relative z-10 px-2.5 py-1 text-xs font-medium rounded-md transition-colors duration-150',
                range === r ? 'text-white' : 'text-text-muted hover:text-text-secondary'
              )}
            >
              {range === r && (
                <motion.span
                  layoutId="range-indicator"
                  className="absolute inset-0 rounded-md bg-accent-blue shadow-glow-blue"
                  style={{ zIndex: -1 }}
                  transition={SLIDER_SPRING}
                />
              )}
              {r}
            </button>
          ))}
        </div>

        {selected && (
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={() => { toggleWatch(selected.symbol_key); forceWatchlistRerender(n => n + 1) }}
            className="p-1.5 rounded-md hover:bg-glass-medium transition-colors duration-150"
            title="Watchlist"
          >
            <motion.span
              key={isWatched(selected.symbol_key) ? 'on' : 'off'}
              initial={{ scale: 0.5 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 500, damping: 15 }}
              className="block"
            >
              <Star className={cn('w-4 h-4', isWatched(selected.symbol_key) ? 'fill-current text-accent-amber' : 'text-text-muted')} />
            </motion.span>
          </motion.button>
        )}

        <div className="ml-auto flex items-center gap-1.5 text-xs text-text-muted">
          {readyStats?.latest_bucket && (
            <span className="flex items-center gap-1" title="Sello de frescura (C3/C5)">
              <Clock className="w-3 h-3 shrink-0" />
              datos a {new Date(readyStats.latest_bucket.computed_at).toLocaleString('es-ES')}
            </span>
          )}
        </div>

        <div className="flex items-center gap-0.5 p-0.5 rounded-lg glass">
          {(['chart', 'screener'] as const).map(v => (
            <button
              key={v}
              onClick={() => setTab(v)}
              className={cn(
                'relative z-10 px-3 py-1 text-xs font-medium rounded-md transition-colors duration-150',
                tab === v ? 'text-white' : 'text-text-muted hover:text-text-secondary'
              )}
            >
              {tab === v && (
                <motion.span
                  layoutId="view-indicator"
                  className="absolute inset-0 rounded-md bg-accent-blue shadow-glow-blue"
                  style={{ zIndex: -1 }}
                  transition={SLIDER_SPRING}
                />
              )}
              {v === 'chart' ? 'Chart' : 'Screener'}
            </button>
          ))}
        </div>
      </motion.div>

      {tab === 'screener' ? (
        <Screener onSelectSymbol={(key) => {
          const parts = key.split('|')
          setSelected({ symbol_key: key, make: parts[0], model: parts[1], province_code: parts[2] === 'NAT' ? null : parts[2], level: parts[2] === 'NAT' ? 'model_nat' : 'model_prov', first_bucket: '', last_bucket: '' })
          setTab('chart')
        }} />
      ) : !selected ? (
        <EmptyState
          icon={<Search className="w-6 h-6" />}
          title="Busca un símbolo"
          message="make · modelo · provincia — p.ej. '320d málaga'. Solo se muestran símbolos con muestra suficiente (C2: ≥30 activos, ≥5 eventos)."
        />
      ) : (
        <div className="flex flex-1 min-h-0">
          {/* Chart central */}
          <div className="flex-1 flex flex-col min-w-0">
            <div className="flex items-center gap-1 px-3 py-1.5 border-b border-border-subtle overflow-x-auto">
              {INDICATOR_CATALOG.filter(d => DEFAULT_INDICATOR_IDS.includes(d.id) || activeIndicators.some(a => a.uid === d.id)).map(d => {
                const isActive = activeIndicators.some(a => a.uid === d.id)
                return (
                  <motion.button
                    key={d.id}
                    whileTap={{ scale: 0.93 }}
                    onClick={() => toggleIndicator(d.id)}
                    className={cn(
                      'px-2 py-0.5 text-[11px] rounded-full whitespace-nowrap transition-colors duration-150',
                      isActive ? 'bg-accent-blue/15 text-accent-blue ring-1 ring-accent-blue/20' : 'text-text-muted hover:text-text-secondary hover:bg-glass-subtle'
                    )}
                  >
                    {d.name}
                  </motion.button>
                )
              })}
              <IndicatorPicker onAdd={toggleIndicator} active={activeIndicators.map(a => a.uid)} />
            </div>

            <div className="flex items-center gap-1 px-3 py-1.5 border-b border-border-subtle overflow-x-auto">
              {REDUCED_TOOLS.map((g, gi) => (
                <div key={g.id} className="flex items-center gap-1">
                  {gi > 0 && <span className="w-px h-4 bg-border-subtle mx-1 shrink-0" aria-hidden />}
                  {g.tools.map(t => (
                    <Tooltip key={t.id} content={t.label}>
                      <motion.button
                        whileTap={{ scale: 0.92 }}
                        onClick={() => setTool(t.id)}
                        className={cn(
                          'px-1.5 py-1 text-[10px] rounded-md whitespace-nowrap transition-colors duration-150',
                          tool === t.id ? 'bg-accent-blue/15 text-accent-blue' : 'text-text-muted hover:text-text-secondary hover:bg-glass-subtle'
                        )}
                      >
                        {t.label}
                      </motion.button>
                    </Tooltip>
                  ))}
                </div>
              ))}
            </div>

            {error && <EmptyState icon={<AlertTriangle className="w-6 h-6" />} title="No se pudo cargar el símbolo" message={error} />}
            {insufficient && !error && (
              <EmptyState icon={<Gauge className="w-6 h-6" />} title="Muestra insuficiente" message={(stats as { reason: string }).reason} />
            )}
            {!error && !insufficient && (
              <MarketChart
                p={p}
                data={bars}
                symbol={selected.symbol_key}
                range={range}
                chartType={chartType}
                indicators={activeIndicators}
                compare={[]}
                compareData={{}}
                tool={tool}
                color={p.accent}
                drawings={drawings}
                onAddDrawing={d => setDrawings(prev => [...prev, d])}
                onUpdateDrawing={(id, pts) => setDrawings(prev => prev.map(d => d.id === id ? { ...d, pts } : d))}
                onDeleteDrawing={id => setDrawings(prev => prev.filter(d => d.id !== id))}
                hideDrawings={false}
                lockDrawings={false}
                magnet={false}
                onCross={b => { crossRef.current = b }}
              />
            )}
            {loading && (
              <div className="flex items-center gap-2 px-4 py-2 text-xs text-text-muted">
                <LoadingSpinner size="sm" /> Cargando barras…
              </div>
            )}
          </div>

          {/* Panel derecho — "El mercado de este coche" (C8) */}
          <div className="w-80 border-l border-border-subtle bg-glass-subtle overflow-auto p-4 space-y-4">
            <div className="flex items-center gap-1.5">
              <h3 className="text-sm font-semibold text-text-primary">El mercado de este coche</h3>
              <Tooltip content="Datos agregados de mercado para este símbolo, calculados a partir del censo de anuncios activos (C8).">
                <button type="button" aria-label="Qué es este panel" className="cursor-help outline-none text-text-muted">
                  <Info className="w-3.5 h-3.5" />
                </button>
              </Tooltip>
            </div>

            {!readyStats && loading && (
              <div className="space-y-2">
                <Skeleton className="h-14" />
                <div className="grid grid-cols-2 gap-2">
                  <Skeleton className="h-14" />
                  <Skeleton className="h-14" />
                </div>
              </div>
            )}

            {!readyStats && !loading && (
              <EmptyState icon={<Gauge className="w-6 h-6" />} title="Sin datos censales" message="Todavía no hay agregado de mercado para este símbolo." />
            )}

            {readyStats && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }} className="space-y-4">
                <p className="text-xs text-text-secondary">
                  {selected.make} {selected.model} · {selected.province_code ?? 'España'}
                </p>

                <div className="grid grid-cols-2 gap-2">
                  <StatTile label="Profesionales" value={readyStats.n_dealers} />
                  <StatTile label="Unidades activas" value={readyStats.active_count} />
                  {readyStats.latest_bucket?.dom_p50_days != null && (
                    <StatTile label="DOM P50" value={Math.round(readyStats.latest_bucket.dom_p50_days)} suffix=" d" />
                  )}
                  {readyStats.price_pressure.pct != null && (
                    <StatTile
                      label="Bajó precio (30d)"
                      value={readyStats.price_pressure.pct}
                      suffix="%"
                      tone={readyStats.price_pressure.alert ? 'warn' : undefined}
                    />
                  )}
                  {readyStats.concentration_top5_pct != null && (
                    <StatTile label="Top-5 stock" value={readyStats.concentration_top5_pct} suffix="%" />
                  )}
                </div>

                {readyStats.price_pressure.alert && (
                  <div
                    className="flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium"
                    style={{ background: `${WARN}1a`, border: `1px solid ${WARN}38`, color: WARN }}
                  >
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                    Mercado bajo presión (&gt;25% con bajada de precio)
                  </div>
                )}

                <div>
                  <h4 className="text-[10px] font-semibold uppercase tracking-wide text-text-muted mb-2">Cinta de eventos</h4>
                  {readyStats.latest_bucket ? (
                    <p className="text-xs text-text-secondary tabular-nums">
                      {readyStats.latest_bucket.bucket_date}:{' '}
                      <span style={{ color: GOOD }}>{readyStats.latest_bucket.new_count} altas</span>,{' '}
                      <span style={{ color: BAD }}>{readyStats.latest_bucket.gone_count} salidas</span>
                    </p>
                  ) : (
                    <p className="text-xs text-text-muted">Sin bucket calculado aún.</p>
                  )}
                </div>

                <div>
                  <h4 className="text-[10px] font-semibold uppercase tracking-wide text-text-muted mb-2">Anuncios (muestra)</h4>
                  <ul className="space-y-1">
                    {readyStats.sample_vehicles.map((v, i) => (
                      <motion.li
                        key={v.vehicle_ulid}
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.03, duration: 0.2 }}
                      >
                        <button
                          onClick={() => setTicketVehicle(v)}
                          className="w-full text-left text-xs px-2 py-1.5 rounded-md outline-none transition-colors duration-150 hover:bg-glass-medium focus-visible:bg-glass-medium flex items-center justify-between"
                        >
                          <span className="text-text-secondary">{v.year ?? '—'} · {v.km != null ? `${v.km.toLocaleString('es-ES')} km` : '— km'}</span>
                          <span className="tabular-nums font-medium text-text-primary">{v.price != null ? `€${Math.round(v.price).toLocaleString('es-ES')}` : '—'}</span>
                        </button>
                      </motion.li>
                    ))}
                  </ul>
                </div>

                {news.length > 0 && (
                  <div>
                    <h4 className="text-[10px] font-semibold uppercase tracking-wide text-text-muted mb-2 flex items-center gap-1">
                      <Newspaper className="w-3 h-3" /> Fundamental (C10)
                    </h4>
                    <ul className="space-y-2">
                      {news.map((n, i) => (
                        <motion.li
                          key={n.news_ulid}
                          initial={{ opacity: 0, y: 4 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.03, duration: 0.2 }}
                        >
                          <a
                            href={n.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="block px-2 py-1.5 rounded-md transition-colors duration-150 hover:bg-glass-medium group"
                          >
                            <Badge color="gray" className="mb-1">{n.source_name}</Badge>
                            <p className="text-xs text-text-secondary group-hover:text-text-primary transition-colors duration-150">{n.title}</p>
                          </a>
                        </motion.li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        </div>
      )}

      <VehicleTicket
        open={!!ticketVehicle}
        symbolKey={selected?.symbol_key ?? ''}
        vehicleUlid={ticketVehicle?.vehicle_ulid ?? ''}
        deepLink={ticketVehicle?.deep_link ?? ''}
        onClose={() => setTicketVehicle(null)}
      />
    </div>
  )
}

/** Ports Inteligencia.tsx's `AnimNum` spring-counter pattern for the right rail's hero
 * numbers — value is only ever mounted once `readyStats` resolves, never against a guess. */
function AnimNum({ to, suffix = '' }: { to: number; suffix?: string }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d = useTransform(sp, v => `${Math.round(v)}${suffix}`)
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span>{d}</motion.span>
}

function StatTile({ label, value, suffix = '', tone }: { label: string; value: number; suffix?: string; tone?: 'warn' }) {
  const color = tone === 'warn' ? WARN : 'var(--text-primary)'
  return (
    <div className="glass rounded-md px-2.5 py-2">
      <div className="text-[9.5px] font-semibold uppercase tracking-wide text-text-muted mb-0.5">{label}</div>
      <div className="text-base font-bold tabular-nums" style={{ color }}>
        <AnimNum to={value} suffix={suffix} />
      </div>
    </div>
  )
}

function IndicatorPicker({ onAdd, active }: { onAdd: (id: string) => void; active: string[] }) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const onOutside = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', onOutside)
    return () => document.removeEventListener('mousedown', onOutside)
  }, [open])

  // INDICATOR_CATALOG is already grouped contiguously by category — flag the first item of
  // each run so the picker can render a sticky-feeling section header without re-sorting.
  const grouped = useMemo(() => {
    let prevCategory = ''
    return INDICATOR_CATALOG.map((d: IndicatorDef) => {
      const showHeader = d.category !== prevCategory
      prevCategory = d.category
      return { def: d, showHeader }
    })
  }, [])

  return (
    <div className="relative" ref={rootRef}>
      <motion.button
        whileTap={{ scale: 0.95 }}
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-1 px-2 py-0.5 text-[11px] rounded-full text-text-muted transition-colors duration-150 hover:text-text-secondary hover:bg-glass-subtle"
      >
        <Plus className="w-3 h-3" /> indicador
      </motion.button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, scale: 0.97, y: -4 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: -4 }}
            transition={SLIDER_SPRING}
            className="absolute top-full right-0 mt-1.5 w-60 max-h-80 overflow-y-auto glass-lg rounded-lg z-20 p-1"
          >
            {grouped.map(({ def, showHeader }) => {
              const isActive = active.includes(def.id)
              return (
                <div key={def.id}>
                  {showHeader && (
                    <div className="px-2.5 pt-2 pb-1 text-[10px] font-semibold uppercase tracking-wide text-text-muted">
                      {def.category}
                    </div>
                  )}
                  <button
                    onClick={() => { onAdd(def.id); setOpen(false) }}
                    className={cn(
                      'w-full flex items-center gap-2 text-left px-2.5 py-1.5 rounded-md text-xs outline-none transition-colors duration-150',
                      isActive ? 'text-accent-blue bg-accent-blue/10' : 'text-text-secondary hover:text-text-primary hover:bg-glass-medium focus-visible:bg-glass-medium'
                    )}
                  >
                    <span className="w-3.5 shrink-0">{isActive && <Check className="w-3.5 h-3.5" />}</span>
                    {def.name}
                  </button>
                </div>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
