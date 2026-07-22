import React, { useMemo, useRef, useState } from 'react'

export interface SeriesPoint {
  value: number
  date: string
}

export type MetricAccent = 'blue' | 'emerald' | 'rose' | 'amber' | 'neutral'
export type ChartView = 'curve' | 'bar'

export interface MetricSeries {
  name: string
  data: SeriesPoint[]
  accent?: MetricAccent
}

export interface ChartSeries {
  name: string
  data: SeriesPoint[]
  color: string
}

// Mirrors lib/theme.ts (ACCENT/GOOD/BAD/WARN) — one brand blue, three reserved
// data-semantic hues. `soft` is the same hue at low alpha for area fills/glow.
export const ACCENTS: Record<MetricAccent, { stroke: string; text: string; soft: string }> = {
  blue: { stroke: '#2563eb', text: '#2563eb', soft: 'rgba(37,99,235,0.16)' },
  emerald: { stroke: '#059669', text: '#059669', soft: 'rgba(5,150,105,0.16)' },
  rose: { stroke: '#e11d48', text: '#e11d48', soft: 'rgba(225,29,72,0.16)' },
  amber: { stroke: '#d97706', text: '#d97706', soft: 'rgba(217,119,6,0.16)' },
  neutral: { stroke: '#64748b', text: 'var(--text-muted)', soft: 'rgba(100,116,139,0.14)' },
}

// Categorical fixed order for multi-series charts (dataviz skill: never cycled
// arbitrarily). indigo/teal lead — the pair already validated for Api.tsx and
// Analitica.tsx's charts (ΔE 21.4 normal-vision, clears the ≥15 floor).
export const SERIES_COLORS = ['#4f46e5', '#0891b2', '#d97706', '#c026d3']

export function formatCompact(n: number): string {
  if (!Number.isFinite(n)) return '0'
  const abs = Math.abs(n)
  if (abs < 1000) return Math.round(n).toLocaleString('en-US')
  return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}

interface MetricChartProps {
  series: ChartSeries[]
  view: ChartView
  defaultIndex?: number
  valueFormatter: (value: number) => string
  dateFormatter: (date: string) => string
}

const PAD_X = 4
const PAD_TOP = 18
const PAD_BOTTOM = 10

// Catmull-Rom-derived cubic bezier — smooth without an external curve library.
function smoothPath(points: [number, number][]): string {
  if (points.length < 2) return ''
  if (points.length === 2) return `M${points[0][0]},${points[0][1]} L${points[1][0]},${points[1][1]}`
  let d = `M${points[0][0]},${points[0][1]}`
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i - 1] ?? points[i]
    const p1 = points[i]
    const p2 = points[i + 1]
    const p3 = points[i + 2] ?? p2
    const c1x = p1[0] + (p2[0] - p0[0]) / 6
    const c1y = p1[1] + (p2[1] - p0[1]) / 6
    const c2x = p2[0] - (p3[0] - p1[0]) / 6
    const c2y = p2[1] - (p3[1] - p1[1]) / 6
    d += ` C${c1x},${c1y} ${c2x},${c2y} ${p2[0]},${p2[1]}`
  }
  return d
}

export function MetricChart({ series, view, defaultIndex, valueFormatter, dateFormatter }: MetricChartProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [hoverIndex, setHoverIndex] = useState<number | null>(null)
  const gradId = useMemo(() => `mc-grad-${Math.random().toString(36).slice(2, 9)}`, [])

  const primary = series[0]
  const count = primary?.data.length ?? 0
  const activeIndex = hoverIndex ?? (defaultIndex !== undefined ? Math.min(defaultIndex, count - 1) : null)

  const { width, height } = { width: 100, height: 100 } // viewBox units, scales via CSS
  const allValues = series.flatMap((s) => s.data.map((d) => d.value))
  const minV = Math.min(...allValues, 0)
  const maxV = Math.max(...allValues, 1)
  const span = maxV - minV || 1

  const plotW = width - PAD_X * 2
  const plotH = height - PAD_TOP - PAD_BOTTOM
  const xAt = (i: number) => PAD_X + (count > 1 ? (i / (count - 1)) * plotW : plotW / 2)
  const yAt = (v: number) => PAD_TOP + plotH - ((v - minV) / span) * plotH

  function handleMove(e: React.MouseEvent<SVGSVGElement>) {
    if (!svgRef.current || count === 0) return
    const rect = svgRef.current.getBoundingClientRect()
    const relX = ((e.clientX - rect.left) / rect.width) * width
    const t = (relX - PAD_X) / plotW
    const idx = Math.round(t * (count - 1))
    setHoverIndex(Math.max(0, Math.min(count - 1, idx)))
  }

  const showTooltip = activeIndex !== null && count > 0
  const tipX = showTooltip ? xAt(activeIndex!) : 0
  const tipAlign = tipX > width - 24 ? 'right' : tipX < 24 ? 'left' : 'center'

  return (
    <div className="relative h-full w-full">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        className="h-full w-full cursor-crosshair"
        onMouseMove={handleMove}
        onMouseLeave={() => setHoverIndex(null)}
      >
        <defs>
          {series.map((s, i) => (
            <linearGradient key={s.name} id={`${gradId}-${i}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={s.color} stopOpacity={0.28} />
              <stop offset="100%" stopColor={s.color} stopOpacity={0} />
            </linearGradient>
          ))}
        </defs>

        {activeIndex !== null && (
          <line
            x1={xAt(activeIndex)}
            x2={xAt(activeIndex)}
            y1={PAD_TOP - 4}
            y2={height - PAD_BOTTOM}
            stroke="currentColor"
            className="text-foreground/[0.10]"
            strokeWidth={0.6}
            vectorEffect="non-scaling-stroke"
          />
        )}

        {view === 'bar' ? (
          series.map((s, si) => {
            const barW = (plotW / Math.max(count, 1)) * 0.52
            return s.data.map((d, i) => {
              const x = xAt(i) - barW / 2
              const y = yAt(d.value)
              const isActive = i === activeIndex
              return (
                <rect
                  key={`${s.name}-${i}`}
                  x={x + si * (barW * 0.08)}
                  y={y}
                  width={barW}
                  height={Math.max(0.5, height - PAD_BOTTOM - y)}
                  rx={1.2}
                  fill={s.color}
                  opacity={isActive || activeIndex === null ? 0.85 : 0.4}
                />
              )
            })
          })
        ) : (
          series.map((s, i) => {
            const pts: [number, number][] = s.data.map((d, idx) => [xAt(idx), yAt(d.value)])
            const path = smoothPath(pts)
            const areaPath =
              pts.length > 0
                ? `${path} L${pts[pts.length - 1][0]},${height - PAD_BOTTOM} L${pts[0][0]},${height - PAD_BOTTOM} Z`
                : ''
            return (
              <g key={s.name}>
                {i === 0 && <path d={areaPath} fill={`url(#${gradId}-${i})`} stroke="none" />}
                <path
                  d={path}
                  fill="none"
                  stroke={s.color}
                  strokeWidth={1.6}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  vectorEffect="non-scaling-stroke"
                />
              </g>
            )
          })
        )}

        {activeIndex !== null &&
          series.map((s) => {
            const d = s.data[activeIndex]
            if (!d) return null
            return (
              <circle
                key={s.name}
                cx={xAt(activeIndex)}
                cy={yAt(d.value)}
                r={2.2}
                fill={s.color}
                stroke="var(--bg-elevated)"
                strokeWidth={1}
                vectorEffect="non-scaling-stroke"
              />
            )
          })}
      </svg>

      {showTooltip && primary?.data[activeIndex!] && (
        <div
          className="pointer-events-none absolute top-1 z-20 min-w-max rounded-[10px] border border-[var(--border-default)] bg-[var(--bg-elevated)] px-2.5 py-1.5 shadow-[var(--shadow-card)]"
          style={{
            left: `${tipX}%`,
            transform:
              tipAlign === 'right' ? 'translateX(-100%)' : tipAlign === 'left' ? 'translateX(0%)' : 'translateX(-50%)',
          }}
        >
          <div className="mb-0.5 text-[10px] font-medium text-[var(--text-muted)]">
            {dateFormatter(primary.data[activeIndex!].date)}
          </div>
          {series.map((s) => (
            <div key={s.name} className="flex items-center gap-1.5 text-[11px] font-semibold text-[var(--text-primary)]">
              {series.length > 1 && <span className="h-1.5 w-1.5 rounded-full" style={{ background: s.color }} />}
              {valueFormatter(s.data[activeIndex!]?.value ?? 0)}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
