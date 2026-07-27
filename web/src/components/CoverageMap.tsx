import { motion } from 'framer-motion'
import React, { useEffect, useMemo, useRef, useState } from 'react'
import { geoPath } from 'd3-geo'
import { geoConicConformalSpain } from 'd3-composite-projections'
import { scaleQuantile } from 'd3-scale'
import { feature } from 'topojson-client'
import type { Topology } from 'topojson-client'
import { Table2, Map as MapIcon } from 'lucide-react'
import { cardeep, type ProvinceDemand, type ProvinceMeta } from '../api/cardeep'
import { useIsDark } from '../hooks/useIsDark'
import EmptyState from './EmptyState'
import esProvincesTopo from '../data/geo/es-provinces.json'

// dataviz skill — sequential magnitude, one hue, documented palette.md steps only
// (100/200/350/450/700 light; 700/600/450/400/250 dark — "flips anchor" so low
// value always recedes into the surface and high value always pops off it).
const LIGHT_STEPS = ['#cde2fb', '#9ec5f4', '#5598e7', '#2a78d6', '#0d366b']
const DARK_STEPS = ['#0d366b', '#184f95', '#2a78d6', '#3987e5', '#86b6ef']

const VIEW_W = 800
const VIEW_H = 600
const GIBRALTAR_ID = '54' // IGN cartographic void, not a real Spanish province

interface ProvinceRow {
  code: string
  name: string
  rate: number | null
  nAvailable: number | null
}

type ProvinceFeature = { type: 'Feature'; id?: string | number; properties: { name: string }; geometry: unknown }

export default function CoverageMap() {
  const isDark = useIsDark()
  const [demand, setDemand] = useState<ProvinceDemand[] | null>(null)
  const [meta, setMeta] = useState<ProvinceMeta[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [hover, setHover] = useState<{ code: string; x: number; y: number } | null>(null)
  const [asTable, setAsTable] = useState(false)
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    const ctrl = new AbortController()
    setLoading(true)
    setError(null)
    Promise.all([cardeep.marketProvincesDemand(ctrl.signal), cardeep.metaProvinces(ctrl.signal)])
      .then(([d, m]) => { setDemand(d); setMeta(m) })
      .catch((err: Error) => { if (err.name !== 'AbortError') setError(err.message) })
      .finally(() => setLoading(false))
    return () => ctrl.abort()
  }, [])

  const rowsByCode = useMemo(() => {
    const map = new Map<string, ProvinceRow>()
    for (const p of meta ?? []) map.set(p.code, { code: p.code, name: p.name, rate: null, nAvailable: null })
    for (const d of demand ?? []) {
      const existing = map.get(d.province_code)
      const row: ProvinceRow = {
        code: d.province_code,
        name: existing?.name ?? d.province_code,
        rate: d.absorption_rate,
        nAvailable: d.n_available,
      }
      map.set(d.province_code, row)
    }
    return map
  }, [meta, demand])

  const { features, path } = useMemo(() => {
    const topology = esProvincesTopo as unknown as Topology
    const collection = feature(topology, topology.objects.provinces)
    const real = { ...collection, features: collection.features.filter((f) => String(f.id) !== GIBRALTAR_ID) }
    const projection = geoConicConformalSpain().fitSize([VIEW_W, VIEW_H], real)
    return { features: real.features as unknown as ProvinceFeature[], path: geoPath(projection) }
  }, [])

  const colorScale = useMemo(() => {
    const rates = [...rowsByCode.values()].map((r) => r.rate).filter((r): r is number => r !== null)
    const steps = isDark ? DARK_STEPS : LIGHT_STEPS
    if (rates.length === 0) return null
    return scaleQuantile<string>().domain(rates).range(steps)
  }, [rowsByCode, isDark])

  const noDataFill = 'var(--glass-md)'
  const noDataStroke = 'var(--border-subtle)'

  function fillFor(code: string): string {
    const row = rowsByCode.get(code)
    if (!row || row.rate === null || !colorScale) return noDataFill
    return colorScale(row.rate)
  }

  const sortedRows = useMemo(
    () => [...rowsByCode.values()].sort((a, b) => (b.rate ?? -1) - (a.rate ?? -1)),
    [rowsByCode],
  )
  const withRateCount = sortedRows.filter((r) => r.rate !== null).length

  if (loading) {
    return <div className="h-[420px] rounded-[10px] skeleton" />
  }
  if (error) {
    return (
      <EmptyState
        title="Mapa de demanda no disponible"
        message={error}
      />
    )
  }
  if (rowsByCode.size === 0) {
    return <EmptyState title="Sin cohortes publicadas todavía" message="Ningún run de market_stat con M5 publicado aún." />
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="relative"
    >
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-medium" style={{ color: 'var(--t1)' }}>Demanda por provincia</h3>
          <p className="text-xs" style={{ color: 'var(--t4)' }}>
            Absorción M5 (GONE / disponible, ventana 30d) · {withRateCount} de {rowsByCode.size} provincias con cohorte propia
          </p>
        </div>
        <button
          type="button"
          onClick={() => setAsTable((v) => !v)}
          className="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-md border transition-colors"
          style={{ borderColor: 'var(--border-default)', color: 'var(--t3)' }}
          aria-pressed={asTable}
        >
          {asTable ? <MapIcon className="w-3.5 h-3.5" /> : <Table2 className="w-3.5 h-3.5" />}
          {asTable ? 'Ver mapa' : 'Ver tabla'}
        </button>
      </div>

      {asTable ? (
        <div className="overflow-auto max-h-[420px] rounded-[10px] border" style={{ borderColor: 'var(--border-subtle)' }}>
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left" style={{ color: 'var(--t4)' }}>
                <th className="px-3 py-2">Provincia</th>
                <th className="px-3 py-2 text-right">Absorción</th>
                <th className="px-3 py-2 text-right">Disponibles</th>
              </tr>
            </thead>
            <tbody>
              {sortedRows.map((r) => (
                <tr key={r.code} className="border-t" style={{ borderColor: 'var(--border-subtle)' }}>
                  <td className="px-3 py-1.5" style={{ color: 'var(--t1)' }}>{r.name}</td>
                  <td className="px-3 py-1.5 text-right tabular-nums" style={{ color: 'var(--t2)' }}>
                    {r.rate !== null ? `${(r.rate * 100).toFixed(1)}%` : 'sin cohorte'}
                  </td>
                  <td className="px-3 py-1.5 text-right tabular-nums" style={{ color: 'var(--t3)' }}>
                    {r.nAvailable !== null ? r.nAvailable.toLocaleString('es-ES') : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <>
          <svg
            ref={svgRef}
            viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
            role="img"
            aria-label={`Mapa de absorción de demanda por provincia. ${sortedRows.length} provincias.`}
            className="w-full h-auto max-h-[420px]"
            onMouseLeave={() => setHover(null)}
          >
            {features.map((f) => {
              const code = String(f.id)
              const row = rowsByCode.get(code)
              return (
                <path
                  key={code}
                  d={path(f as never) ?? undefined}
                  fill={fillFor(code)}
                  stroke={row?.rate != null ? 'var(--border-active)' : noDataStroke}
                  strokeWidth={hover?.code === code ? 1.5 : 0.75}
                  style={{ transition: 'stroke-width 120ms ease, filter 120ms ease', cursor: 'pointer' }}
                  className={hover?.code === code ? 'brightness-110' : undefined}
                  aria-label={`${row?.name ?? code}: ${row?.rate != null ? `${(row.rate * 100).toFixed(1)}% absorción` : 'sin cohorte suficiente'}`}
                  onMouseMove={(e) => {
                    const rect = svgRef.current?.getBoundingClientRect()
                    if (!rect) return
                    setHover({ code, x: e.clientX - rect.left, y: e.clientY - rect.top })
                  }}
                />
              )
            })}
          </svg>

          {hover && rowsByCode.get(hover.code) && (
            <div
              className="glass-lg absolute z-10 px-3 py-2 rounded-[10px] pointer-events-none text-xs"
              style={{ left: hover.x + 12, top: hover.y + 12, minWidth: 140 }}
            >
              <div className="font-medium mb-0.5" style={{ color: 'var(--t1)' }}>{rowsByCode.get(hover.code)!.name}</div>
              {rowsByCode.get(hover.code)!.rate !== null ? (
                <>
                  <div className="tabular-nums" style={{ color: 'var(--t2)' }}>
                    {(rowsByCode.get(hover.code)!.rate! * 100).toFixed(1)}% absorción
                  </div>
                  <div className="tabular-nums" style={{ color: 'var(--t4)' }}>
                    {rowsByCode.get(hover.code)!.nAvailable!.toLocaleString('es-ES')} disponibles
                  </div>
                </>
              ) : (
                <div style={{ color: 'var(--t4)' }}>Cohorte insuficiente</div>
              )}
            </div>
          )}

          <div className="flex items-center gap-2 mt-3 text-[11px]" style={{ color: 'var(--t4)' }}>
            <span>Baja</span>
            {(isDark ? DARK_STEPS : LIGHT_STEPS).map((c) => (
              <span key={c} className="w-5 h-3 rounded-sm inline-block" style={{ background: c }} />
            ))}
            <span>Alta</span>
            <span className="w-3 h-3 rounded-sm inline-block ml-3" style={{ background: noDataFill, border: `1px solid ${noDataStroke}` }} />
            <span>Sin cohorte</span>
          </div>
        </>
      )}
    </motion.div>
  )
}
