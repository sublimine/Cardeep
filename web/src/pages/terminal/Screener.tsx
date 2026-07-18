// 09-trading-terminal Fase 3b — screener: technical (Δ/DOM) + fundamental-censal (stock,
// dealers) columns combined in ONE table (TradingView Stock Screener pattern, carta §6).
// Cero mock: sourced entirely from GET /terminal/screener.
import { useEffect, useState } from 'react'
import { ArrowDown, ArrowUp } from 'lucide-react'
import { cardeep, CardeepApiError, type TerminalScreenerRow } from '../../api/cardeep'
import EmptyState from '../../components/EmptyState'
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
      <div className="flex items-center gap-3 px-4 py-2 border-b border-border-subtle">
        <input
          value={province}
          onChange={e => setProvince(e.target.value.toUpperCase().slice(0, 2))}
          placeholder="Provincia (28, 08...)"
          className="w-40 px-2 py-1 text-xs rounded bg-glass-medium border border-border-subtle"
        />
        <span className="text-xs text-text-muted">{rows?.length ?? 0} símbolos</span>
      </div>

      {error && <EmptyState title="No se pudo cargar el screener" message={error} />}
      {!error && rows && rows.length === 0 && (
        <EmptyState title="Sin símbolos" message="Ningún símbolo activo con esos filtros." />
      )}

      {!error && rows && rows.length > 0 && (
        <div className="flex-1 overflow-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-glass-medium backdrop-blur">
              <tr className="text-left text-text-muted">
                <th className="px-3 py-2 font-medium">Símbolo</th>
                <th className="px-3 py-2 font-medium">Prov.</th>
                <th className="px-3 py-2 font-medium text-right">€ mediana</th>
                <SortableHeader label="Stock" sortKey="active_count" current={sort} onSort={setSort} />
                <SortableHeader label="Altas" sortKey="new_count" current={sort} onSort={setSort} />
                <SortableHeader label="Salidas" sortKey="gone_count" current={sort} onSort={setSort} />
                <SortableHeader label="DOM P50" sortKey="dom_p50_days" current={sort} onSort={setSort} />
                <th className="px-3 py-2 font-medium text-right">Presión</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => {
                const pressure = r.price_change_down_count + r.price_change_up_count > 0
                  ? (100 * r.price_change_down_count) / (r.price_change_down_count + r.price_change_up_count)
                  : null
                return (
                  <tr
                    key={r.symbol_key}
                    onClick={() => onSelectSymbol(r.symbol_key)}
                    className="border-b border-border-subtle/50 hover:bg-glass-medium cursor-pointer transition-colors"
                  >
                    <td className="px-3 py-2 font-medium">{r.make} {r.model}</td>
                    <td className="px-3 py-2 text-text-muted">{r.province_code ?? 'ES'}</td>
                    <td className="px-3 py-2 text-right tabular-nums">
                      {r.median_price != null ? `€${Math.round(r.median_price).toLocaleString('es-ES')}` : '—'}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums">{r.active_count}</td>
                    <td className="px-3 py-2 text-right tabular-nums" style={{ color: GOOD }}>+{r.new_count}</td>
                    <td className="px-3 py-2 text-right tabular-nums" style={{ color: BAD }}>-{r.gone_count}</td>
                    <td className="px-3 py-2 text-right tabular-nums">{r.dom_p50_days != null ? `${Math.round(r.dom_p50_days)}d` : '—'}</td>
                    <td className="px-3 py-2 text-right tabular-nums">
                      {pressure != null ? (
                        <span style={{ color: pressure > 25 ? BAD : undefined }}>{pressure.toFixed(0)}%</span>
                      ) : '—'}
                    </td>
                  </tr>
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
      className="px-3 py-2 font-medium text-right cursor-pointer select-none"
      onClick={() => onSort(sortKey)}
    >
      <span className={active ? 'text-text-primary' : ''}>{label}</span>
      {active && (sortKey === 'gone_count' ? <ArrowDown className="inline w-3 h-3 ml-1" /> : <ArrowUp className="inline w-3 h-3 ml-1" />)}
    </th>
  )
}
