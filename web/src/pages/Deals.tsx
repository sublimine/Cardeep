import { motion, AnimatePresence } from 'framer-motion'
import React, { useState } from 'react'
import {
  Plus, ChevronRight, TrendingUp, Target, DollarSign, Activity,
} from 'lucide-react'
import Card from '../components/Card'
import Button from '../components/Button'
import { Badge } from '../components/Badge'
import Avatar from '../components/Avatar'
import Modal from '../components/Modal'
import LoadingSpinner from '../components/LoadingSpinner'
import { cn } from '../lib/cn'
import { useDeals, useDealMutations } from '../hooks/useDeals'
import { STAGES, STAGE_LABELS, type KanbanStage } from '../hooks/useKanban'
import { useToast } from '../components/Toast'
import type { Deal } from '../types'

// ── Stage configuration — no violet/purple ────────────────────────────────────

const STAGE_PROB: Record<KanbanStage, number> = {
  lead: 15, contacted: 30, offer: 50, negotiation: 75, won: 100, lost: 0,
}

const stageColor: Record<KanbanStage, string> = {
  lead:        'text-blue-400',
  contacted:   'text-sky-400',
  offer:       'text-amber-400',
  negotiation: 'text-orange-400',
  won:         'text-emerald-400',
  lost:        'text-rose-400',
}

const stagePill: Record<KanbanStage, string> = {
  lead:        'bg-blue-500/10 border-blue-500/20 text-blue-400',
  contacted:   'bg-sky-500/10 border-sky-500/20 text-sky-400',
  offer:       'bg-amber-500/10 border-amber-500/20 text-amber-400',
  negotiation: 'bg-orange-500/10 border-orange-500/20 text-orange-400',
  won:         'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
  lost:        'bg-rose-500/10 border-rose-500/20 text-rose-400',
}

const stageBar: Record<KanbanStage, string> = {
  lead:        'bg-blue-400',
  contacted:   'bg-sky-400',
  offer:       'bg-amber-400',
  negotiation: 'bg-orange-400',
  won:         'bg-emerald-400',
  lost:        'bg-rose-400',
}

// ── Mock data ─────────────────────────────────────────────────────────────────

const MOCK_DEALS: Deal[] = [
  { id: 'd1', tenantId: 't', contactId: 'c1', vehicleId: 'v1', stage: 'lead',        createdAt: '2026-04-10T10:00:00Z', updatedAt: '2026-04-18T10:00:00Z', vehicleName: 'BMW 320d xDrive',   contactName: 'Maria Santos', price: 28500 },
  { id: 'd2', tenantId: 't', contactId: 'c2', vehicleId: 'v2', stage: 'contacted',   createdAt: '2026-04-08T09:00:00Z', updatedAt: '2026-04-17T14:00:00Z', vehicleName: 'Audi A4 2.0 TDI',   contactName: 'John Doe',     price: 31000 },
  { id: 'd3', tenantId: 't', contactId: 'c3', vehicleId: 'v3', stage: 'offer',       createdAt: '2026-04-06T08:00:00Z', updatedAt: '2026-04-16T11:00:00Z', vehicleName: 'Mercedes C220 AMG', contactName: 'Anna Weber',   price: 35000 },
  { id: 'd4', tenantId: 't', contactId: 'c4', vehicleId: 'v4', stage: 'negotiation', createdAt: '2026-04-04T07:00:00Z', updatedAt: '2026-04-15T16:00:00Z', vehicleName: 'VW Golf 8 GTI',     contactName: 'Peter Klein',  price: 26000 },
  { id: 'd5', tenantId: 't', contactId: 'c5', vehicleId: 'v5', stage: 'won',         createdAt: '2026-04-01T06:00:00Z', updatedAt: '2026-04-14T09:00:00Z', vehicleName: 'BMW X3 M40i',       contactName: 'Sophie L.',    price: 44000 },
  { id: 'd6', tenantId: 't', contactId: 'c6', vehicleId: 'v6', stage: 'lost',        createdAt: '2026-03-28T05:00:00Z', updatedAt: '2026-04-11T12:00:00Z', vehicleName: 'Peugeot 308 GT',    contactName: 'Hans Müller',  price: 22500 },
  { id: 'd7', tenantId: 't', contactId: 'c7', vehicleId: 'v7', stage: 'contacted',   createdAt: '2026-04-12T10:00:00Z', updatedAt: '2026-04-18T08:00:00Z', vehicleName: 'Seat Ateca FR',     contactName: 'Clara Rossi',  price: 27800 },
  { id: 'd8', tenantId: 't', contactId: 'c8', vehicleId: 'v8', stage: 'offer',       createdAt: '2026-04-09T10:00:00Z', updatedAt: '2026-04-17T10:00:00Z', vehicleName: 'Skoda Octavia RS',  contactName: 'Tom Brown',    price: 23400 },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

function dealAge(createdAt: string): string {
  const days = Math.floor((Date.now() - new Date(createdAt).getTime()) / 86400000)
  if (days === 0) return 'Today'
  if (days === 1) return '1d'
  return `${days}d`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

// ── KPI summary row ───────────────────────────────────────────────────────────

function KpiRow({ deals }: { deals: Deal[] }) {
  const active    = deals.filter(d => d.stage !== 'won' && d.stage !== 'lost')
  const won       = deals.filter(d => d.stage === 'won')
  const pipeline  = active.reduce((s, d) => s + (d.price ?? 0), 0)
  const wonValue  = won.reduce((s, d) => s + (d.price ?? 0), 0)
  const convRate  = deals.length > 0 ? Math.round((won.length / deals.length) * 100) : 0

  const kpis = [
    {
      icon: <Activity className="w-4 h-4 text-accent-blue" />,
      label: 'Active deals',
      value: active.length,
      sub: `${deals.length} total`,
      accent: 'text-accent-blue',
    },
    {
      icon: <DollarSign className="w-4 h-4 text-amber-400" />,
      label: 'Pipeline value',
      value: `€${(pipeline / 1000).toFixed(0)}k`,
      sub: 'active deals',
      accent: 'text-amber-400',
    },
    {
      icon: <TrendingUp className="w-4 h-4 text-emerald-400" />,
      label: 'Won revenue',
      value: `€${(wonValue / 1000).toFixed(0)}k`,
      sub: `${won.length} deals closed`,
      accent: 'text-emerald-400',
    },
    {
      icon: <Target className="w-4 h-4 text-text-secondary" />,
      label: 'Conversion',
      value: `${convRate}%`,
      sub: 'lead to close',
      accent: 'text-text-secondary',
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {kpis.map((k, i) => (
        <motion.div
          key={k.label}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06, duration: 0.28 }}
          className="glass rounded-xl p-4"
        >
          <div className="flex items-center justify-between mb-3">
            <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">
              {k.label}
            </p>
            {k.icon}
          </div>
          <p className={cn('text-2xl font-bold tabular-nums leading-none mb-1', k.accent)}>
            {k.value}
          </p>
          <p className="text-[11px] text-text-muted">{k.sub}</p>
        </motion.div>
      ))}
    </div>
  )
}

// ── Pipeline funnel ───────────────────────────────────────────────────────────

function PipelineFunnel({ deals }: { deals: Deal[] }) {
  const grouped: Record<KanbanStage, Deal[]> = Object.fromEntries(
    STAGES.map(s => [s, deals.filter(d => d.stage === s)]),
  ) as Record<KanbanStage, Deal[]>

  const maxCount = Math.max(...STAGES.map(s => grouped[s].length), 1)

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm font-semibold text-text-primary">Pipeline funnel</p>
        <p className="text-xs text-text-muted">{deals.length} deals</p>
      </div>
      <div className="flex items-end gap-2 h-20">
        {STAGES.map((s, i) => {
          const count = grouped[s].length
          const pct   = maxCount > 0 ? (count / maxCount) * 100 : 0
          return (
            <motion.div
              key={s}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 + i * 0.06 }}
              className="flex-1 flex flex-col items-center gap-1"
            >
              <span className="text-[10px] font-bold text-text-muted tabular-nums">{count}</span>
              <div className="w-full rounded-sm overflow-hidden" style={{ height: 52, background: 'var(--border-subtle)' }}>
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: `${pct}%` }}
                  transition={{ delay: 0.25 + i * 0.06, duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
                  className={cn('w-full rounded-sm mt-auto', stageBar[s])}
                  style={{ marginTop: `${100 - pct}%` }}
                />
              </div>
              <span className={cn('text-[9px] font-bold uppercase tracking-wider truncate w-full text-center', stageColor[s])}>
                {STAGE_LABELS[s]}
              </span>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

// ── Deal detail modal ─────────────────────────────────────────────────────────

function DealDetailModal({
  deal, onClose, onAdvance, canAdvance,
}: {
  deal: Deal; onClose: () => void; onAdvance: () => void; canAdvance: boolean
}) {
  const stage   = deal.stage as KanbanStage
  const prob    = STAGE_PROB[stage] ?? 0
  const stageIdx = STAGES.indexOf(stage)

  return (
    <Modal open onClose={onClose} title={deal.vehicleName ?? 'Deal'} size="sm">
      <div className="space-y-4">
        {/* Contact + stage */}
        <div className="flex items-center gap-3 pb-4 border-b border-border-subtle">
          <Avatar name={deal.contactName ?? '?'} size="md" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-text-primary truncate">{deal.contactName}</p>
            <p className="text-xs text-text-muted">{deal.vehicleName}</p>
          </div>
          <span className={cn(
            'text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border',
            stagePill[stage],
          )}>
            {STAGE_LABELS[stage]}
          </span>
        </div>

        {/* Stage progression */}
        <div>
          <div className="flex gap-1 mb-3">
            {STAGES.slice(0, -1).map((s, i) => (
              <div
                key={s}
                className={cn(
                  'flex-1 h-1 rounded-full transition-all duration-300',
                  i <= stageIdx && stage !== 'lost'
                    ? stageBar[stage]
                    : 'bg-border-subtle',
                )}
              />
            ))}
          </div>
          <div className="flex items-center justify-between">
            <p className="text-xs text-text-muted">Win probability</p>
            <span className={cn('text-xs font-bold', stageColor[stage])}>{prob}%</span>
          </div>
        </div>

        {/* Info grid */}
        <div className="grid grid-cols-2 gap-2.5">
          {[
            ['Value',    deal.price ? `€${deal.price.toLocaleString()}` : '—'],
            ['Age',      dealAge(deal.createdAt)],
            ['Created',  formatDate(deal.createdAt)],
            ['Updated',  formatDate(deal.updatedAt)],
          ].map(([k, v]) => (
            <div key={k} className="glass rounded-lg p-3">
              <p className="text-[10px] text-text-muted uppercase tracking-wide mb-1">{k}</p>
              <p className="text-sm font-semibold text-text-primary">{v}</p>
            </div>
          ))}
        </div>

        {canAdvance && (
          <Button onClick={onAdvance} className="w-full" icon={<ChevronRight className="w-4 h-4" />}>
            Advance to {STAGE_LABELS[STAGES[STAGES.indexOf(stage) + 1] as KanbanStage]}
          </Button>
        )}
      </div>
    </Modal>
  )
}

// ── Deal list row ─────────────────────────────────────────────────────────────

interface DealRowProps {
  deal: Deal
  idx: number
  onSelect: () => void
  onAdvance: () => void
  canAdvance: boolean
}

// forwardRef: AnimatePresence mode="popLayout" attaches a ref to each direct
// child to measure it during exit animations — a plain function component
// can't accept that ref, which React warns about at runtime.
const DealRow = React.forwardRef<HTMLDivElement, DealRowProps>(function DealRow(
  { deal, idx, onSelect, onAdvance, canAdvance },
  ref,
) {
  const stage = deal.stage as KanbanStage
  const prob  = STAGE_PROB[stage] ?? 0

  return (
    <motion.div
      ref={ref}
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ delay: idx * 0.035, duration: 0.22 }}
      onClick={onSelect}
      className="flex items-center gap-3 py-3.5 px-1 border-b border-border-subtle/50 last:border-0 cursor-pointer hover:bg-glass-subtle rounded-md -mx-1 transition-colors group"
    >
      <Avatar name={deal.contactName ?? '?'} size="sm" />

      {/* Main info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-text-primary truncate">
          {deal.vehicleName ?? 'Unknown vehicle'}
        </p>
        <p className="text-xs text-text-muted">{deal.contactName}</p>
      </div>

      {/* Probability bar */}
      <div className="hidden sm:flex flex-col items-end gap-1 w-20 shrink-0">
        <span className={cn('text-[10px] font-bold', stageColor[stage])}>{prob}%</span>
        <div className="w-full h-1 rounded-full bg-border-subtle overflow-hidden">
          <div
            className={cn('h-full rounded-full transition-all', stageBar[stage])}
            style={{ width: `${prob}%` }}
          />
        </div>
      </div>

      {/* Value */}
      {deal.price && (
        <span className="text-sm font-bold text-text-primary tabular-nums shrink-0">
          €{deal.price.toLocaleString()}
        </span>
      )}

      {/* Age */}
      <span className="hidden md:block text-[11px] text-text-muted tabular-nums shrink-0 w-8 text-right">
        {dealAge(deal.createdAt)}
      </span>

      {/* Stage badge */}
      <span className={cn(
        'hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border shrink-0',
        stagePill[stage],
      )}>
        {STAGE_LABELS[stage]}
      </span>

      {/* Advance button */}
      {canAdvance && (
        <motion.button
          whileTap={{ scale: 0.92 }}
          onClick={e => { e.stopPropagation(); onAdvance() }}
          className="flex items-center gap-1 text-xs px-2 py-1 rounded-md glass border-border-subtle text-text-secondary hover:text-text-primary transition-colors shrink-0 opacity-0 group-hover:opacity-100"
        >
          Next <ChevronRight className="w-3 h-3" />
        </motion.button>
      )}
    </motion.div>
  )
})

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Deals() {
  const { data, loading }              = useDeals()
  const { moveStage, loading: mutating } = useDealMutations()
  const { success }                    = useToast()
  const [selectedStage, setSelectedStage] = useState<KanbanStage | 'all'>('all')
  const [selectedDeal,  setSelectedDeal]  = useState<Deal | null>(null)

  const deals = data?.deals ?? MOCK_DEALS

  const grouped: Record<KanbanStage, Deal[]> = Object.fromEntries(
    STAGES.map(s => [s, deals.filter(d => d.stage === s)]),
  ) as Record<KanbanStage, Deal[]>

  async function handleAdvance(deal: Deal) {
    const idx = STAGES.indexOf(deal.stage as KanbanStage)
    if (idx < 0 || idx >= STAGES.length - 2) return
    const next = STAGES[idx + 1]
    await moveStage(deal.id, next)
    success(`Deal moved to ${STAGE_LABELS[next]}`)
    setSelectedDeal(null)
  }

  const filteredDeals = selectedStage === 'all'
    ? deals
    : deals.filter(d => d.stage === selectedStage)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-4 md:p-6 space-y-5 max-w-7xl mx-auto"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Deals</h1>
          <p className="text-sm text-text-muted mt-0.5">
            {deals.filter(d => d.stage !== 'won' && d.stage !== 'lost').length} active ·&nbsp;
            {deals.filter(d => d.stage === 'won').length} won ·&nbsp;
            €{(deals.filter(d => d.stage !== 'lost').reduce((s, d) => s + (d.price ?? 0), 0) / 1000).toFixed(0)}k pipeline
          </p>
        </div>
        <Button icon={<Plus className="w-4 h-4" />} size="sm" loading={mutating}>
          New deal
        </Button>
      </div>

      {/* KPI row */}
      <KpiRow deals={deals} />

      {/* Pipeline funnel */}
      <PipelineFunnel deals={deals} />

      {/* Stage filter pills */}
      <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
        <motion.button
          whileTap={{ scale: 0.96 }}
          onClick={() => setSelectedStage('all')}
          className={cn(
            'px-3 py-1.5 text-xs font-semibold rounded-full border transition-colors whitespace-nowrap',
            selectedStage === 'all'
              ? 'bg-accent-blue border-accent-blue/30 text-white'
              : 'glass border-border-subtle text-text-secondary hover:text-text-primary',
          )}
        >
          All · {deals.length}
        </motion.button>
        {STAGES.map(s => (
          <motion.button
            key={s}
            whileTap={{ scale: 0.96 }}
            onClick={() => setSelectedStage(s)}
            className={cn(
              'px-3 py-1.5 text-xs font-semibold rounded-full border transition-colors whitespace-nowrap',
              selectedStage === s
                ? stagePill[s]
                : 'glass border-border-subtle text-text-secondary hover:text-text-primary',
            )}
          >
            {STAGE_LABELS[s]} · {grouped[s]?.length ?? 0}
          </motion.button>
        ))}
      </div>

      {/* Deal list */}
      <Card padding>
        {loading ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : filteredDeals.length === 0 ? (
          <p className="text-sm text-text-muted text-center py-8">No deals in this stage.</p>
        ) : (
          <>
            {/* List header */}
            <div className="hidden md:flex items-center gap-3 pb-2.5 mb-1 border-b border-border-subtle text-[10px] text-text-muted uppercase tracking-wider font-semibold px-1">
              <div className="w-8 shrink-0" />
              <div className="flex-1">Deal</div>
              <div className="w-20 text-right">Win %</div>
              <div className="w-20 text-right">Value</div>
              <div className="w-8 text-right">Age</div>
              <div className="w-20">Stage</div>
              <div className="w-14" />
            </div>

            <AnimatePresence mode="popLayout">
              {filteredDeals.map((d, idx) => {
                const stageIdx  = STAGES.indexOf(d.stage as KanbanStage)
                const canAdvance = stageIdx >= 0 && stageIdx < STAGES.length - 2

                return (
                  <DealRow
                    key={d.id}
                    deal={d}
                    idx={idx}
                    onSelect={() => setSelectedDeal(d)}
                    onAdvance={() => handleAdvance(d)}
                    canAdvance={canAdvance}
                  />
                )
              })}
            </AnimatePresence>
          </>
        )}
      </Card>

      {/* Deal detail modal */}
      {selectedDeal && (
        <DealDetailModal
          deal={selectedDeal}
          onClose={() => setSelectedDeal(null)}
          onAdvance={() => handleAdvance(selectedDeal)}
          canAdvance={
            STAGES.indexOf(selectedDeal.stage as KanbanStage) >= 0 &&
            STAGES.indexOf(selectedDeal.stage as KanbanStage) < STAGES.length - 2
          }
        />
      )}
    </motion.div>
  )
}
