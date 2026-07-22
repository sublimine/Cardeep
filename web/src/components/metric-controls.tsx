import React from 'react'
import { BarChart3, ChevronDown, LineChart } from 'lucide-react'
import { Dropdown } from './Dropdown'
import type { ChartView } from './metric-chart'

export interface PeriodOption {
  label: string
  points?: number
}

interface PeriodSelectProps {
  value: string
  options: PeriodOption[]
  onChange: (option: PeriodOption) => void
  accentText?: string
}

export function PeriodSelect({ value, options, onChange, accentText }: PeriodSelectProps) {
  return (
    <Dropdown
      align="end"
      trigger={
        <button
          type="button"
          className="pointer-events-auto flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[13px] font-medium text-[var(--text-muted)] outline-none transition-colors hover:text-[var(--text-primary)] focus-visible:ring-2 focus-visible:ring-[color:var(--border-focus)]"
        >
          {value}
          <ChevronDown className="h-3.5 w-3.5 opacity-70" />
        </button>
      }
      items={options.map((opt) => ({
        label: opt.label,
        checked: opt.label === value,
        onSelect: () => onChange(opt),
      }))}
    />
  )
}

interface ViewToggleProps {
  value: ChartView
  onChange: (view: ChartView) => void
}

const VIEWS: { key: ChartView; icon: typeof LineChart; label: string }[] = [
  { key: 'curve', icon: LineChart, label: 'Curve view' },
  { key: 'bar', icon: BarChart3, label: 'Bar view' },
]

export function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <div className="pointer-events-auto flex items-center gap-0.5 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] p-0.5">
      {VIEWS.map(({ key, icon: Icon, label }) => {
        const active = key === value
        return (
          <button
            key={key}
            type="button"
            aria-label={label}
            aria-pressed={active}
            onClick={() => onChange(key)}
            className={`flex h-5 w-5 items-center justify-center rounded-[6px] transition-colors focus-visible:ring-2 focus-visible:ring-[color:var(--border-focus)] ${
              active ? 'bg-[var(--bg-elevated)] text-[var(--text-primary)] shadow-[var(--shadow-1)]' : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
            }`}
          >
            <Icon className="h-3 w-3" strokeWidth={2.4} />
          </button>
        )
      })}
    </div>
  )
}
