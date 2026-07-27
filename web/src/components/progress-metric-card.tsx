import { useId, useMemo, useState } from 'react'
import { ArrowDown, ArrowRight, ArrowUp } from 'lucide-react'
import { Skeleton } from './Skeleton'
import {
  ACCENTS,
  formatCompact,
  MetricChart,
  SERIES_COLORS,
  type ChartSeries,
  type ChartView,
  type MetricAccent,
  type MetricSeries,
  type SeriesPoint,
} from './metric-chart'
import { PeriodSelect, type PeriodOption } from './metric-controls'

// Re-exported so consumers only need to import this one file.
export type { SeriesPoint, MetricSeries, MetricAccent, ChartView, PeriodOption }

export type CardSize = 'sm' | 'md' | 'lg'

export interface ProgressMetricCardProps {
  title: string
  total?: string | number
  /** Small muted line under the headline number (e.g. "€2.14M capital"). */
  sub?: string
  delta?: string
  deltaLabel?: string
  percent?: string
  trend?: 'up' | 'down' | 'flat'
  unit?: string
  period?: string
  periodOptions?: PeriodOption[]
  onPeriodChange?: (option: PeriodOption) => void
  defaultView?: ChartView
  accent?: MetricAccent
  /** Single series. Provide this, OR `series`. */
  data?: SeriesPoint[]
  /** Multiple named series. Takes priority over `data`. */
  series?: MetricSeries[]
  defaultIndex?: number
  size?: CardSize
  /** Show secondary peak/low/avg stats in the footer. */
  showStats?: boolean
  valueFormatter?: (value: number) => string
  dateFormatter?: (date: string) => string
  loading?: boolean
  className?: string
}

const DEFAULT_PERIODS: PeriodOption[] = [
  { label: 'Past 7 days', points: 4 },
  { label: 'Past 14 days', points: 7 },
  { label: 'Past 30 days' },
]

// Share of the card (from the right edge) occupied by the background chart.
const REGION_W = 66 // %
// Variation below this threshold reads as "flat" -> neutral accent.
const NEUTRAL_PCT = 0.5

interface SizeSpec {
  /** Fixed, not min — every card at this size must be pixel-identical so a
   * row of them stays symmetric regardless of title length or content. */
  h: string
  pad: string
  footer: string
  title: string
  headline: string
  /** Gap between title row and headline number — scales with the card, unlike
   * the other sizes' shared `mt-5` which only fit the two bigger sizes. */
  headGap: string
}

// `sm` is a genuinely landscape/compact card (~300x160, ~1.9:1 — close to the
// original reference's 762x380, ~2:1), not a shrunk-down `md`. A 4-up KPI row
// needs this; `md`/`lg` stay hero-sized for a 1-2-up "featured metric" layout.
const SIZES: Record<CardSize, SizeSpec> = {
  sm: { h: 'h-[168px]', pad: 'px-5 pt-4', footer: 'px-5 py-2.5', title: 'text-[12.5px]', headline: 'text-[32px]', headGap: 'mt-1.5' },
  md: { h: 'h-[380px]', pad: 'px-8 pt-7', footer: 'px-8 py-4', title: 'text-[17px]', headline: 'text-[72px]', headGap: 'mt-5' },
  lg: { h: 'h-[460px]', pad: 'px-10 pt-9', footer: 'px-10 py-5', title: 'text-[19px]', headline: 'text-[88px]', headGap: 'mt-5' },
}

const sliceWindow = (points: SeriesPoint[], n?: number) => (n && n < points.length ? points.slice(-n) : points)

export default function ProgressMetricCard({
  title,
  total,
  sub,
  delta,
  deltaLabel = 'today',
  percent,
  trend,
  unit,
  period = 'Past 30 days',
  periodOptions,
  onPeriodChange,
  defaultView = 'curve',
  accent,
  data,
  series,
  defaultIndex,
  size = 'md',
  showStats = true,
  valueFormatter,
  dateFormatter,
  loading = false,
  className = '',
}: ProgressMetricCardProps) {
  const gridId = `grid-${useId().replace(/:/g, '')}`
  const sz = SIZES[size]
  const shell = `relative flex ${sz.h} w-full flex-col overflow-hidden rounded-[var(--radius-2xl)] border border-[var(--border-default)] bg-[var(--bg-elevated)] shadow-[var(--shadow-card)] ${className}`

  const periods = periodOptions ?? DEFAULT_PERIODS
  const [selectedLabel, setSelectedLabel] = useState(period)
  // No in-card view toggle (moved out per owner direction — it ate space a
  // dense KPI row can't spare); `defaultView` alone still picks curve vs bar.
  const view: ChartView = defaultView

  // Normalizes the input into a list of series (a plain `data` array becomes one series).
  const baseSeries: MetricSeries[] = useMemo(
    () => (series?.length ? series : [{ name: title, data: data ?? [], accent }]),
    [series, data, title, accent],
  )

  const selectedOption = periods.find((p) => p.label === selectedLabel) ?? periods[periods.length - 1]

  // Slices every series to the chosen period.
  const visibleSeries = useMemo(
    () => baseSeries.map((s) => ({ ...s, data: sliceWindow(s.data, selectedOption?.points) })),
    [baseSeries, selectedOption],
  )

  const primary = visibleSeries[0]
  const isMulti = visibleSeries.length > 1
  const hasData = (primary?.data.length ?? 0) >= 2

  // Every figure derives from the primary series so the card stays internally
  // consistent and reacts to period changes. Explicit props still win.
  const stats = useMemo(() => {
    const vals = primary?.data.map((d) => d.value) ?? []
    const sum = vals.reduce((a, b) => a + b, 0)
    const first = vals[0] ?? 0
    const last = vals[vals.length - 1] ?? 0
    const prev = vals[vals.length - 2] ?? first
    const net = last - first
    return {
      sum,
      net,
      pct: first ? (net / first) * 100 : 0,
      step: last - prev,
      peak: vals.length ? Math.max(...vals) : 0,
      low: vals.length ? Math.min(...vals) : 0,
      avg: vals.length ? sum / vals.length : 0,
    }
  }, [primary])

  // Color follows direction (last vs first point), with a neutral dead zone.
  const resolvedTrend: 'up' | 'down' | 'flat' =
    trend ?? (Math.abs(stats.pct) < NEUTRAL_PCT ? 'flat' : stats.net >= 0 ? 'up' : 'down')
  const resolvedAccent: MetricAccent =
    accent ?? (resolvedTrend === 'up' ? 'emerald' : resolvedTrend === 'down' ? 'rose' : 'neutral')
  const color = ACCENTS[resolvedAccent]
  const TrendIcon = resolvedTrend === 'flat' ? ArrowRight : resolvedTrend === 'down' ? ArrowDown : ArrowUp

  const fmtCompact = valueFormatter ?? formatCompact
  const fmtFull = valueFormatter ?? ((n: number) => n.toLocaleString() + (unit ? ` ${unit}` : ''))
  const fmtDate = dateFormatter ?? ((d: string) => d)
  const sign = (n: number) => (n >= 0 ? '+' : '−') + fmtCompact(Math.abs(n))

  const displayTotal = total ?? fmtCompact(stats.sum)
  const displayDelta = delta ?? sign(stats.step)
  const displayPercent = percent ?? `${Math.abs(stats.pct).toFixed(1)}%`

  // Each series' color: explicit accent -> categorical palette -> title's own color.
  const chartSeries: ChartSeries[] = visibleSeries.map((s, i) => ({
    name: s.name,
    data: s.data,
    color: s.accent ? ACCENTS[s.accent].stroke : isMulti ? SERIES_COLORS[i % SERIES_COLORS.length] : color.stroke,
  }))

  const lastIndex = (primary?.data.length ?? 1) - 1
  const fallback = Math.min(defaultIndex ?? lastIndex, lastIndex)
  // At `sm` size the default tooltip collides with the period-select trigger
  // in the same top-right corner (most visible in dense KPI rows, 4-up).
  // Tooltip becomes hover-only there instead of auto-shown.
  const chartDefaultIndex = size === 'sm' ? undefined : fallback

  const handlePeriodChange = (option: PeriodOption) => {
    setSelectedLabel(option.label)
    onPeriodChange?.(option)
  }

  if (loading) {
    const skeletonHeadline = size === 'sm' ? 'h-8 w-28' : 'h-14 w-48'
    const skeletonChart = size === 'sm' ? 'h-12 w-full' : 'h-24 w-full'
    return (
      <div className={shell} aria-busy="true">
        <div className={`flex flex-1 flex-col ${sz.pad}`}>
          <div className="flex items-center justify-between">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-5 w-24" />
          </div>
          <Skeleton className={`${sz.headGap} ${skeletonHeadline}`} rounded="lg" />
          <Skeleton className={`mt-auto ${skeletonChart}`} rounded="lg" />
        </div>
        <div className={`border-t border-[var(--border-subtle)] ${sz.footer}`}>
          <Skeleton className="h-4 w-40" />
        </div>
      </div>
    )
  }

  if (!hasData) {
    return (
      <div className={shell}>
        <div className={`flex flex-1 flex-col ${sz.pad}`}>
          <h3 className={`${sz.title} font-semibold tracking-tight text-[var(--text-primary)]`}>{title}</h3>
          <div className="flex flex-1 flex-col items-center justify-center gap-1 py-10 text-center">
            <p className="text-sm font-medium text-[var(--text-primary)]">No data yet</p>
            <p className="text-xs text-[var(--text-muted)]">Metrics will appear once data is available.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={shell}>
      {/* Chart region (right side, behind the content). Wash + dot-grid + the
       * actual line/area fade in/out together as ONE unit — from the
       * number-zone boundary on the left, AND out again before the opaque
       * footer on the bottom. Without the second fade, the chart got cut off
       * clean by the footer's solid background + border, same "parón seco"
       * as the left edge had before, just rotated 90°. */}
      <div className="absolute inset-y-0 right-0 z-0" style={{ width: `${REGION_W}%` }}>
        <div
          className="absolute inset-0"
          style={{
            WebkitMaskImage: 'linear-gradient(to bottom, black 68%, transparent 96%)',
            maskImage: 'linear-gradient(to bottom, black 68%, transparent 96%)',
          }}
        >
          <div
            className="absolute inset-0"
            style={{
              WebkitMaskImage: 'linear-gradient(to right, transparent 0%, black 36%)',
              maskImage: 'linear-gradient(to right, transparent 0%, black 36%)',
            }}
          >
            <div
              className="absolute inset-0"
              style={{ background: `linear-gradient(to left, ${color.stroke}1f, transparent 75%)` }}
            />
            <div className="absolute inset-0 text-[var(--text-primary)] opacity-[0.13]">
              <svg className="h-full w-full" aria-hidden>
                <defs>
                  <pattern id={gridId} width="14" height="14" patternUnits="userSpaceOnUse">
                    <circle cx="1" cy="1" r="1" fill="currentColor" />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill={`url(#${gridId})`} />
              </svg>
            </div>

            <MetricChart
              series={chartSeries}
              view={view}
              defaultIndex={chartDefaultIndex}
              valueFormatter={fmtFull}
              dateFormatter={fmtDate}
            />
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className={`pointer-events-none relative z-10 flex flex-1 flex-col ${sz.pad}`}>
        {/* Title alone on the left; period filter + percent stacked top-right —
         * per owner direction, not spread across the row (which is what wrapped
         * long titles and "Past 30 days" onto a second line and broke row
         * symmetry, since a wrapped title grows past its siblings' height). */}
        <div className="flex items-start justify-between gap-3">
          <h3 className={`${sz.title} truncate font-semibold tracking-tight text-[var(--text-primary)]`}>{title}</h3>
          <div className="flex shrink-0 flex-col items-end gap-1">
            <PeriodSelect value={selectedLabel} options={periods} onChange={handlePeriodChange} accentText={color.text} />
            <span className="flex items-center gap-1 whitespace-nowrap text-[13px] font-medium" style={{ color: color.text }}>
              <TrendIcon size={14} strokeWidth={2.5} />
              {displayPercent}
            </span>
          </div>
        </div>

        {/* Legend (multi-series only) */}
        {isMulti && (
          <div className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-1">
            {chartSeries.map((s) => (
              <span key={s.name} className="flex items-center gap-1.5 text-[12px] text-[var(--text-muted)]">
                <span className="h-2 w-2 rounded-full" style={{ background: s.color }} />
                {s.name}
              </span>
            ))}
          </div>
        )}

        <div className={`${sz.headGap} ${sz.headline} font-medium leading-none tracking-tight text-[var(--text-primary)]`}>
          {displayTotal}
        </div>
        {sub && <div className="mt-1 text-[10.5px] text-[var(--text-muted)]">{sub}</div>}
      </div>

      {/* Opaque footer: delta on the left, secondary stats on the right */}
      <div
        className={`relative z-10 flex items-center justify-between gap-4 border-t border-[var(--border-subtle)] bg-[var(--bg-elevated)] ${sz.footer} text-[14px]`}
      >
        <div>
          <span className="font-medium" style={{ color: color.text }}>
            {displayDelta}
          </span>{' '}
          <span className="text-[var(--text-muted)]">{deltaLabel}</span>
        </div>
        {showStats && (
          <div className="flex items-center gap-2.5 text-[12px] text-[var(--text-muted)]">
            <span>
              <span className="font-medium text-[var(--text-secondary)]">{fmtCompact(stats.peak)}</span> peak
            </span>
            <span className="opacity-40">·</span>
            <span>
              <span className="font-medium text-[var(--text-secondary)]">{fmtCompact(stats.low)}</span> low
            </span>
            <span className="opacity-40">·</span>
            <span>
              <span className="font-medium text-[var(--text-secondary)]">{fmtCompact(Math.round(stats.avg))}</span> avg
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
