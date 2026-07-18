// 09-trading-terminal Fase 3 — the real terminal, dato real, cero mock.
// Every number traces to a criterio C1-C10 of plans/cardeep-omni/09-trading-terminal.md,
// served live by /terminal/* (F2). Chart engine rescued in Fase 0 (indicators.ts/MarketChart.tsx/
// drawings.tsx/tools.ts/theme.ts) — this file wires it to REAL market_bucket_daily data instead
// of the demolished synthetic RNG generator.
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Search, Star, Info } from 'lucide-react'
import { cardeep, CardeepApiError, type TerminalSymbol, type TerminalRange, type TerminalSampleVehicle, type TerminalNewsItem } from '../api/cardeep'
import EmptyState from '../components/EmptyState'
import { MarketChart, type ActiveIndicator, type ChartType, type RangeLabel } from '../components/chart-engine/MarketChart'
import { useTheme } from '../components/chart-engine/theme'
import { INDICATOR_CATALOG } from '../components/chart-engine/indicators'
import { TOOL_GROUPS } from '../components/chart-engine/tools'
import type { Drawing } from '../components/chart-engine/drawings'
import { useTerminalSymbol } from './terminal/useTerminalSymbol'
import { getWatchlist, isWatched, toggleWatch } from './terminal/watchlist'
import Screener from './terminal/Screener'
import VehicleTicket from './terminal/VehicleTicket'

// Fase 3 reduction of the 95-tool arsenal (carta §6: "se reducen al set útil para este dato:
// líneas, medición, anotación") — cursors is the baseline interaction mode, the other three
// groups are the ones that map onto "líneas / medición / anotación".
const ENABLED_TOOL_GROUPS = new Set(['cursors', 'trend_lines', 'measure', 'text_notes'])
const REDUCED_TOOLS = TOOL_GROUPS.filter(g => ENABLED_TOOL_GROUPS.has(g.id))

// A small, useful default indicator set — the full 53-indicator catalog is available via the
// picker below, never crammed onto the chart by default.
const DEFAULT_INDICATOR_IDS = ['sma', 'ema', 'bb']

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
      <div className="flex items-center gap-3 px-4 py-2 border-b border-border-subtle">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="320d málaga..."
            className="w-full pl-8 pr-2 py-1.5 text-sm rounded bg-glass-medium border border-border-subtle"
          />
          {searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 rounded bg-glass-heavy border border-border-subtle shadow-card-hover z-20 max-h-64 overflow-auto">
              {searchResults.map(s => (
                <button
                  key={s.symbol_key}
                  onClick={() => handleSelect(s)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-glass-medium flex items-center justify-between"
                >
                  <span>{s.make} {s.model}</span>
                  <span className="text-xs text-text-muted">{s.province_code ?? 'ES'}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {(['1M', '3M', '6M', '1Y', 'ALL'] as RangeLabel[]).map(r => (
          <button
            key={r}
            onClick={() => setRange(r)}
            className={`px-2 py-1 text-xs rounded ${range === r ? 'bg-accent text-white' : 'bg-glass-medium text-text-muted'}`}
          >
            {r}
          </button>
        ))}

        {selected && (
          <button
            onClick={() => { toggleWatch(selected.symbol_key); forceWatchlistRerender(n => n + 1) }}
            className="p-1.5 rounded hover:bg-glass-medium"
            title="Watchlist"
          >
            <Star className={`w-4 h-4 ${isWatched(selected.symbol_key) ? 'fill-current text-warn' : ''}`} />
          </button>
        )}

        <div className="ml-auto flex items-center gap-2 text-xs text-text-muted">
          {readyStats?.latest_bucket && (
            <span title="Sello de frescura (C3/C5)">
              datos a {new Date(readyStats.latest_bucket.computed_at).toLocaleString('es-ES')}
            </span>
          )}
        </div>

        <div className="flex rounded bg-glass-medium p-0.5">
          <button onClick={() => setTab('chart')} className={`px-3 py-1 text-xs rounded ${tab === 'chart' ? 'bg-accent text-white' : ''}`}>Chart</button>
          <button onClick={() => setTab('screener')} className={`px-3 py-1 text-xs rounded ${tab === 'screener' ? 'bg-accent text-white' : ''}`}>Screener</button>
        </div>
      </div>

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
            <div className="flex items-center gap-1 px-3 py-1 border-b border-border-subtle overflow-x-auto">
              {INDICATOR_CATALOG.filter(d => DEFAULT_INDICATOR_IDS.includes(d.id) || activeIndicators.some(a => a.uid === d.id)).map(d => (
                <button
                  key={d.id}
                  onClick={() => toggleIndicator(d.id)}
                  className={`px-2 py-0.5 text-[11px] rounded whitespace-nowrap ${activeIndicators.some(a => a.uid === d.id) ? 'bg-accent-dim text-accent-text' : 'text-text-muted'}`}
                >
                  {d.name}
                </button>
              ))}
              <IndicatorPicker onAdd={toggleIndicator} active={activeIndicators.map(a => a.uid)} />
            </div>

            <div className="flex items-center gap-1 px-3 py-1 border-b border-border-subtle">
              {REDUCED_TOOLS.flatMap(g => g.tools).map(t => (
                <button
                  key={t.id}
                  onClick={() => setTool(t.id)}
                  title={t.label}
                  className={`px-1.5 py-0.5 text-[10px] rounded ${tool === t.id ? 'bg-accent-dim' : ''}`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {error && <EmptyState title="No se pudo cargar el símbolo" message={error} />}
            {insufficient && !error && (
              <EmptyState title="Muestra insuficiente" message={(stats as { reason: string }).reason} />
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
            {loading && <div className="px-4 py-2 text-xs text-text-muted">Cargando…</div>}
          </div>

          {/* Panel derecho — "El mercado de este coche" (C8) */}
          <div className="w-80 border-l border-border-subtle overflow-auto p-4 space-y-4">
            <h3 className="text-sm font-semibold flex items-center gap-1">
              El mercado de este coche <Info className="w-3 h-3 text-text-muted" />
            </h3>
            {readyStats ? (
              <>
                <p className="text-xs text-text-secondary leading-relaxed">
                  <strong>{readyStats.n_dealers}</strong> profesionales tienen {selected.make} {selected.model} en {selected.province_code ?? 'España'} ·{' '}
                  <strong>{readyStats.active_count}</strong> unidades
                  {readyStats.latest_bucket?.dom_p50_days != null && (
                    <> · P50 <strong>{Math.round(readyStats.latest_bucket.dom_p50_days)}</strong> días en venta</>
                  )}
                  {readyStats.price_pressure.pct != null && (
                    <> · <strong>{readyStats.price_pressure.pct.toFixed(0)}%</strong> ha bajado precio (30d)</>
                  )}
                  {readyStats.concentration_top5_pct != null && (
                    <> · el top-5 concentra el <strong>{readyStats.concentration_top5_pct.toFixed(0)}%</strong> del stock</>
                  )}
                </p>
                {readyStats.price_pressure.alert && (
                  <div className="px-2 py-1.5 rounded bg-warn/10 text-warn text-xs">Mercado bajo presión (&gt;25% con bajada de precio)</div>
                )}

                <div>
                  <h4 className="text-xs font-medium text-text-muted mb-2">Cinta de eventos</h4>
                  {readyStats.latest_bucket ? (
                    <p className="text-xs">
                      {readyStats.latest_bucket.bucket_date}: {readyStats.latest_bucket.new_count} altas, {readyStats.latest_bucket.gone_count} salidas
                    </p>
                  ) : (
                    <p className="text-xs text-text-muted">Sin bucket calculado aún.</p>
                  )}
                </div>

                <div>
                  <h4 className="text-xs font-medium text-text-muted mb-2">Anuncios (muestra)</h4>
                  <ul className="space-y-1">
                    {readyStats.sample_vehicles.map(v => (
                      <li key={v.vehicle_ulid}>
                        <button
                          onClick={() => setTicketVehicle(v)}
                          className="w-full text-left text-xs px-2 py-1 rounded hover:bg-glass-medium flex items-center justify-between"
                        >
                          <span>{v.year} · {v.km?.toLocaleString('es-ES')} km</span>
                          <span className="tabular-nums">{v.price != null ? `€${Math.round(v.price).toLocaleString('es-ES')}` : '—'}</span>
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>

                {news.length > 0 && (
                  <div>
                    <h4 className="text-xs font-medium text-text-muted mb-2">Fundamental (C10)</h4>
                    <ul className="space-y-2">
                      {news.map(n => (
                        <li key={n.news_ulid}>
                          <a href={n.source_url} target="_blank" rel="noreferrer" className="block text-xs hover:underline">
                            <span className="text-text-muted">{n.source_name}</span> — {n.title}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            ) : (
              !loading && <p className="text-xs text-text-muted">Sin datos censales.</p>
            )}
          </div>
        </div>
      )}

      {ticketVehicle && (
        <VehicleTicket
          symbolKey={selected!.symbol_key}
          vehicleUlid={ticketVehicle.vehicle_ulid}
          deepLink={ticketVehicle.deep_link}
          onClose={() => setTicketVehicle(null)}
        />
      )}
    </div>
  )
}

function IndicatorPicker({ onAdd, active }: { onAdd: (id: string) => void; active: string[] }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="relative">
      <button onClick={() => setOpen(o => !o)} className="px-2 py-0.5 text-[11px] rounded text-text-muted">
        + indicador
      </button>
      {open && (
        <div className="absolute top-full right-0 mt-1 w-56 max-h-72 overflow-auto rounded bg-glass-heavy border border-border-subtle shadow-card-hover z-20">
          {INDICATOR_CATALOG.map(d => (
            <button
              key={d.id}
              onClick={() => { onAdd(d.id); setOpen(false) }}
              className={`w-full text-left px-3 py-1.5 text-xs hover:bg-glass-medium ${active.includes(d.id) ? 'text-accent' : ''}`}
            >
              {d.name} <span className="text-text-muted">({d.category})</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
