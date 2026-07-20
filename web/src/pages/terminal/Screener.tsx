// 09-trading-terminal Fase 3b — screener: technical (Δ/DOM) + fundamental-censal (stock,
// dealers) columns combined in ONE table (TradingView Stock Screener pattern, carta §6).
// Cero mock: sourced entirely from GET /terminal/screener.
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowDown, ArrowUp, MapPin, AlertTriangle, SearchX } from 'lucide-react'
import { cardeep, CardeepApiError, type TerminalScreenerRow } from '../../api/cardeep'
import EmptyState from '../../components/EmptyState'
import { TableSkeleton } from '../../components/Skeleton'
import { cn } from '../../lib/cn'
import { GOOD, BAD } from '../../lib/theme'

type SortKey = 'active_count' | 'new_count' | 'gone_count' | 'dom_p50_days'

interface ScreenerProps {
  onSelectSymbol: (symbolKey: string) => void
}

export default function Screener({ onSelectSymbol }: ScreenerProps) {
  const [rows, setRows] = useState<TerminalScreenerRow[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [sort, setSort] = useState<SortKey>('active_count')
  const [province, setProvince] = useState('')

  useEffect(() => {
    let cancelled = false
    setRows(null)
    setError(null)
    cardeep.terminalScreener({ sort, province: province || undefined, limit: 50 })
      .then(data => { if (!cancelled) setRows(data) })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof CardeepApiError ? err.message : 'Error al cargar el screener')
      })
    return () => { cancelled = true }
  }, [sort, province])

  return (
    <div className="flex flex-col h-full">
      <motion.div
        initial={{ opacity: 0, y: -6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="flex items-center gap-3 px-4 py-2.5 border-b border-border-subtle"
      >
        <div className="relative">
          <MapPin className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-text-muted" />
          <input
            value={province}
            onChange={e => setProvince(e.target.value.toUpperCase().slice(0, 2))}
            placeholder="Provincia (28, 08...)"
            className="w-44 pl-8 pr-2.5 py-1.5 text-xs rounded-md bg-glass-medium border border-border-subtle text-text-primary placeholder:text-text-muted transition-colors focus-visible:border-accent-blue/50 outline-none"
          />
        </div>
        <span className="text-xs text-text-muted tabular-nums">{rows?.length ?? 0} símbolos</span>
      </motion.div>

      {error && <EmptyState icon={<AlertTriangle className="w-6 h-6" />} title="No se pudo cargar el screener" message={error} />}

      {!error && rows === null && (
        <div className="flex-1 overflow-auto p-4">
          <TableSkeleton rows={10} />
        </div>
      )}

      {!error && rows && rows.length === 0 && (
        <EmptyState icon={<SearchX className="w-6 h-6" />} title="Sin símbolos" message="Ningún símbolo activo con esos filtros." />
      )}

      {!error && rows && rows.length > 0 && (
        <div className="flex-1 overflow-auto">
          <table className="w-full text-xs">
            <thead
              className="sticky top-0 bg-glass-medium z-10"
              style={{ backdropFilter: 'var(--glass-blur)', WebkitBackdropFilter: 'var(--glass-blur)' }}
            >
              <tr className="text-left text-text-muted border-b border-border-subtle">
                <th className="px-3 py-2.5 font-medium">Símbolo</th>
                <th className="px-3 py-2.5 font-medium">Prov.</th>
                <th className="px-3 py-2.5 font-medium text-right">€ mediana</th>
                <SortableHeader label="Stock" sortKey="active_count" current={sort} onSort={setSort} />
                <SortableHeader label="Altas" sortKey="new_count" current={sort} onSort={setSort} />
                <SortableHeader label="Salidas" sortKey="gone_count" current={sort} onSort={setSort} />
                <SortableHeader label="DOM P50" sortKey="dom_p50_days" current={sort} onSort={setSort} />
                <th className="px-3 py-2.5 font-medium text-right">Presión</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, idx) => {
                const pressure = r.price_change_down_count + r.price_change_up_count > 0
                  ? (100 * r.price_change_down_count) / (r.price_change_down_count + r.price_change_up_count)
                  : null
                const pressureAlert = pressure != null && pressure > 25
                return (
                  <motion.tr
                    key={r.symbol_key}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: Math.min(idx, 20) * 0.02, duration: 0.2 }}
                    onClick={() => onSelectSymbol(r.symbol_key)}
                    tabIndex={0}
                    role="button"
                    onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelectSymbol(r.symbol_key) } }}
                    className="border-b border-border-subtle/50 hover:bg-glass-subtle cursor-pointer transition-colors duration-150 outline-none focus-visible:bg-glass-subtle"
                  >
                    <td className="px-3 py-2.5 font-medium text-text-primary">{r.make} {r.model}</td>
                    <td className="px-3 py-2.5 text-text-muted">{r.province_code ?? 'ES'}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums text-text-primary">
                      {r.median_price != null ? `€${Math.round(r.median_price).toLocaleString('es-ES')}` : '—'}
                    </td>
                    <td className="px-3 py-2.5 text-right tabular-nums text-text-primary">{r.active_count}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums" style={{ color: GOOD }}>+{r.new_count}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums" style={{ color: BAD }}>-{r.gone_count}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums text-text-primary">{r.dom_p50_days != null ? `${Math.round(r.dom_p50_days)}d` : '—'}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums">
                      {pressure != null ? (
                        <span
                          className={cn('inline-block px-1.5 py-0.5 rounded-full', pressureAlert && 'font-semibold')}
                          style={pressureAlert ? { background: `${BAD}1a`, color: BAD } : undefined}
                        >
                          {pressure.toFixed(0)}%
                        </span>
                      ) : '—'}
                    </td>
                  </motion.tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function SortableHeader({
  label, sortKey, current, onSort,
}: { label: string; sortKey: SortKey; current: SortKey; onSort: (k: SortKey) => void }) {
  const active = current === sortKey
  return (
    <th
      className="px-3 py-2.5 font-medium text-right cursor-pointer select-none hover:text-text-secondary transition-colors duration-150 outline-none focus-visible:text-accent-blue"
      onClick={() => onSort(sortKey)}
      tabIndex={0}
      role="button"
      aria-pressed={active}
      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort(sortKey) } }}
    >
      <span className={active ? 'text-text-primary' : ''}>{label}</span>
      {active && (sortKey === 'gone_count' ? <ArrowDown className="inline w-3 h-3 ml-1" /> : <ArrowUp className="inline w-3 h-3 ml-1" />)}
    </th>
  )
}
