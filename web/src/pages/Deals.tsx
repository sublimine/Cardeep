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
import Input from '../components/Input'
import Select from '../components/Select'
import EmptyState from '../components/EmptyState'
import { Skeleton, TableSkeleton } from '../components/Skeleton'
import { Tooltip } from '../components/Tooltip'
import { cn } from '../lib/cn'
import { useDeals, useDealMutations, useDealsSummary, type DealsSummary } from '../hooks/useDeals'
import { useApi } from '../hooks/useApi'
import { STAGES, STAGE_LABELS, type KanbanStage } from '../hooks/useKanban'
import { useToast } from '../components/Toast'
import { ApiError } from '../api/client'
import type { Deal, Contact } from '../types'

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

// Expected value (Sigma amount x probability) and lead time come from the backend's
// /deals/summary (services/api/routers/crm_deals.py) — ONE computation, never a second
// client-side formula that could silently diverge (00-MASTER.md doctrine). Raw sums
// (won revenue, active count) are simple aggregates with no divergence risk and stay
// client-side.
function KpiRow({ deals, summary }: { deals: Deal[]; summary: DealsSummary | null }) {
  const active    = deals.filter(d => d.stage !== 'won' && d.stage !== 'lost')
  const won       = deals.filter(d => d.stage === 'won')
  const wonValue  = won.reduce((s, d) => s + (d.price ?? 0), 0)
  const pipelineFallback = active.reduce((s, d) => s + (d.price ?? 0), 0)

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
      label: 'Expected value',
      value: `€${((summary?.expectedValue ?? pipelineFallback) / 1000).toFixed(1)}k`,
      sub: 'Σ amount × probability',
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
      label: 'Lead time',
      value: summary?.avgLeadTimeDays != null ? `${summary.avgLeadTimeDays.toFixed(0)}d` : '—',
      sub: 'contact to close (90d)',
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

function KpiRowSkeleton() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {[0, 1, 2, 3].map(i => (
        <div key={i} className="glass rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <Skeleton className="h-2.5 w-16" />
            <Skeleton className="h-4 w-4" rounded="full" />
          </div>
          <Skeleton className="h-7 w-16" />
          <Skeleton className="h-2.5 w-24" />
        </div>
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
          const share = deals.length > 0 ? Math.round((count / deals.length) * 100) : 0
          return (
            <Tooltip
              key={s}
              content={`${STAGE_LABELS[s]} · ${count} ${count === 1 ? 'deal' : 'deals'} (${share}%)`}
            >
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 + i * 0.06 }}
                className="flex-1 flex flex-col items-center gap-1 cursor-default"
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
            </Tooltip>
          )
        })}
      </div>
    </div>
  )
}

function PipelineFunnelSkeleton() {
  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-3.5 w-16" />
      </div>
      <div className="flex items-end gap-2 h-20">
        {['h-[52px]', 'h-[38px]', 'h-[64px]', 'h-[28px]', 'h-[46px]', 'h-[20px]'].map((h, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-1">
            <div className="w-full flex items-end" style={{ height: 52 }}>
              <Skeleton className={cn('w-full', h)} />
            </div>
            <Skeleton className="h-2 w-10 mt-1" />
          </div>
        ))}
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
  // Server-computed probability (crm_deal.probability) is authoritative; the local
  // STAGE_PROB map is only a fallback for a deal the API hasn't priced yet.
  const prob    = deal.probability ?? STAGE_PROB[stage] ?? 0
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
            <span className={cn('text-xs font-bold tabular-nums', stageColor[stage])}>{prob}%</span>
          </div>
        </div>

        {/* Info grid */}
        <div className="grid grid-cols-2 gap-2.5">
          {[
            ['Value',    deal.price ? `€${deal.price.toLocaleString()}` : '—'],
            ['Age',      dealAge(deal.createdAt)],
            ['Created',  formatDate(deal.createdAt)],
            ['Updated',  formatDate(deal.updatedAt)],
          ].map(([k, v], i) => (
            <motion.div
              key={k}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04, duration: 0.22 }}
              className="glass rounded-lg p-3"
            >
              <p className="text-[10px] text-text-muted uppercase tracking-wide mb-1">{k}</p>
              <p className="text-sm font-semibold text-text-primary tabular-nums">{v}</p>
            </motion.div>
          ))}
        </div>

        {/* F5: census cross-reference chip — only rendered when it resolved for real */}
        {deal.vehicleContext && (
          <div className={cn(
            'rounded-lg p-3 border text-xs',
            deal.vehicleContext.stillListed
              ? 'bg-accent-blue/5 border-accent-blue/20 text-text-secondary'
              : 'bg-rose-500/5 border-rose-500/20 text-text-secondary',
          )}>
            {deal.vehicleContext.stillListed ? (
              <>
                <span className="font-semibold text-text-primary">{deal.vehicleContext.daysInStock} días en stock</span>
                {deal.vehicleContext.price != null && (
                  <> · precio actual €{deal.vehicleContext.price.toLocaleString()}</>
                )}
              </>
            ) : (
              <span className="font-semibold text-rose-500">Este vehículo ya no está anunciado</span>
            )}
          </div>
        )}

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
  const prob  = deal.probability ?? STAGE_PROB[stage] ?? 0

  return (
    <motion.div
      ref={ref}
      role="button"
      tabIndex={0}
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.97 }}
      whileHover={{ x: 2 }}
      transition={{ delay: idx * 0.035, duration: 0.22 }}
      onClick={onSelect}
      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect() } }}
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
        <span className={cn('text-[10px] font-bold tabular-nums', stageColor[stage])}>{prob}%</span>
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

// ── New deal modal ────────────────────────────────────────────────────────────

interface ContactListResponse { contacts: Contact[]; total: number }

// F5 matcher (carta §8): deterministic SQL candidates from the tenant's OWN live
// inventory; the dealer confirms with a click — never auto-attached, never fabricated.
interface VehicleCandidate { vehicleUlid: string; label: string; daysInStock: number }
interface VehicleSearchResponse { candidates: VehicleCandidate[] }

function VehiclePicker({
  selected, onSelect, onClear,
}: { selected: VehicleCandidate | null; onSelect: (v: VehicleCandidate) => void; onClear: () => void }) {
  const [query, setQuery] = useState('')
  const searchPath = query.trim().length >= 2 ? `/deals/vehicle-search?q=${encodeURIComponent(query.trim())}` : ''
  const { data, loading } = useApi<VehicleSearchResponse>(searchPath, [searchPath])
  const candidates = data?.candidates ?? []

  if (selected) {
    return (
      <div className="w-full">
        <label className="block text-xs font-medium text-text-secondary mb-1.5 uppercase tracking-wide">
          Vehicle (optional)
        </label>
        <div className="flex items-center justify-between gap-2 px-3.5 py-2.5 rounded-md text-sm bg-glass-subtle border border-border-subtle">
          <span className="text-text-primary truncate">
            {selected.label} · {selected.daysInStock}d en stock
          </span>
          <button type="button" onClick={onClear} className="text-text-muted hover:text-text-primary shrink-0 text-xs">
            Cambiar
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full relative">
      <Input
        label="Vehicle (optional)"
        placeholder="Buscar por marca/modelo… (ej. BMW 320d)"
        value={query}
        onChange={e => setQuery(e.target.value)}
      />
      {query.trim().length >= 2 && (
        <div className="absolute z-10 mt-1 w-full rounded-md border border-border-subtle bg-bg-elevated shadow-elevation-2 max-h-48 overflow-y-auto">
          {loading ? (
            <p className="px-3 py-2 text-xs text-text-muted">Buscando…</p>
          ) : candidates.length === 0 ? (
            <p className="px-3 py-2 text-xs text-text-muted">Sin coincidencias en tu inventario.</p>
          ) : (
            candidates.map(c => (
              <button
                key={c.vehicleUlid}
                type="button"
                onClick={() => { onSelect(c); setQuery('') }}
                className="w-full text-left px-3 py-2 text-xs text-text-primary hover:bg-glass-medium transition-colors"
              >
                {c.label} · {c.daysInStock}d en stock
              </button>
            ))
          )}
        </div>
      )}
    </div>
  )
}

function NewDealModal({
  open, onClose, onCreated,
}: { open: boolean; onClose: () => void; onCreated: () => void }) {
  const { data: contactData } = useApi<ContactListResponse>(open ? '/contacts' : '')
  const { createDeal, loading } = useDealMutations()
  const { success, error: toastErr } = useToast()

  const [contactId, setContactId] = useState('')
  const [vehicle, setVehicle] = useState<VehicleCandidate | null>(null)
  const [price, setPrice] = useState('')
  const [priority, setPriority] = useState<'' | 'low' | 'medium' | 'high'>('')
  const [formError, setFormError] = useState<string | null>(null)

  const contacts = contactData?.contacts ?? []

  function reset() {
    setContactId(''); setVehicle(null); setPrice(''); setPriority(''); setFormError(null)
  }

  function handleClose() {
    reset()
    onClose()
  }

  async function handleSave() {
    if (!contactId) return
    setFormError(null)
    try {
      await createDeal({
        contactId,
        vehicleId: vehicle?.vehicleUlid || undefined,
        price: price.trim() ? Number(price) : undefined,
        priority: priority || undefined,
      })
      success('Deal created')
      onCreated()
      reset()
      onClose()
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Failed to create deal'
      setFormError(message)
      toastErr(message)
    }
  }

  return (
    <Modal open={open} onClose={handleClose} title="New Deal" size="sm">
      <div className="space-y-4">
        {contacts.length === 0 ? (
          <p className="text-xs text-text-muted">
            No contacts yet — create a contact first from the Contacts page.
          </p>
        ) : (
          <Select
            label="Contact"
            placeholder="Select a contact…"
            value={contactId}
            onChange={e => setContactId(e.target.value)}
            options={contacts.map(c => ({ value: c.id, label: `${c.name} (${c.email || c.phone || 's/d'})` }))}
          />
        )}
        <VehiclePicker selected={vehicle} onSelect={setVehicle} onClear={() => setVehicle(null)} />
        <Input
          label="Price (€, optional)"
          type="number"
          placeholder="25000"
          value={price}
          onChange={e => setPrice(e.target.value)}
        />
        <Select
          label="Priority (optional)"
          placeholder="—"
          value={priority}
          onChange={e => setPriority(e.target.value as typeof priority)}
          options={[
            { value: 'low', label: 'Low' },
            { value: 'medium', label: 'Medium' },
            { value: 'high', label: 'High' },
          ]}
        />
        {formError && <p className="text-xs text-accent-rose">{formError}</p>}
        <div className="flex gap-2 pt-1">
          <Button variant="secondary" size="sm" className="flex-1" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            className="flex-1"
            onClick={handleSave}
            disabled={!contactId}
            loading={loading}
          >
            Create deal
          </Button>
        </div>
      </div>
    </Modal>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Deals() {
  const { data, loading, error, reload }  = useDeals()
  const { data: summary }                = useDealsSummary()
  const { moveStage, loading: mutating } = useDealMutations()
  const { success }                    = useToast()
  const [selectedStage, setSelectedStage] = useState<KanbanStage | 'all'>('all')
  const [selectedDeal,  setSelectedDeal]  = useState<Deal | null>(null)
  const [newDealOpen,   setNewDealOpen]   = useState(false)

  // Honest empty array on failure — never a fabricated pipeline.
  const deals = data?.deals ?? []
  // Distinguishes "still waiting on the first response" from "server answered
  // with zero deals" — without this, the KPI row/funnel/pills flash at 0 on
  // every cold load before real numbers (or a real empty pipeline) land.
  const initialLoading = loading && !data

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
          {initialLoading ? (
            <Skeleton className="h-4 w-56 mt-1.5" />
          ) : (
            <p className="text-sm text-text-muted mt-0.5">
              {deals.filter(d => d.stage !== 'won' && d.stage !== 'lost').length} active ·&nbsp;
              {deals.filter(d => d.stage === 'won').length} won ·&nbsp;
              €{(deals.filter(d => d.stage !== 'lost').reduce((s, d) => s + (d.price ?? 0), 0) / 1000).toFixed(0)}k pipeline
            </p>
          )}
        </div>
        <Button icon={<Plus className="w-4 h-4" />} size="sm" loading={mutating} onClick={() => setNewDealOpen(true)}>
          New deal
        </Button>
      </div>

      {/* KPI row */}
      {initialLoading ? <KpiRowSkeleton /> : <KpiRow deals={deals} summary={summary ?? null} />}

      {/* Pipeline funnel */}
      {initialLoading ? <PipelineFunnelSkeleton /> : <PipelineFunnel deals={deals} />}

      {/* Stage filter pills */}
      {initialLoading ? (
        <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
          {['w-16', 'w-24', 'w-28', 'w-24', 'w-28', 'w-16', 'w-16'].map((w, i) => (
            <Skeleton key={i} rounded="full" className={cn('h-[26px]', w)} />
          ))}
        </div>
      ) : (
        <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
          <motion.button
            whileHover={{ scale: 1.03 }}
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
              whileHover={{ scale: 1.03 }}
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
      )}

      {/* Deal list */}
      <Card padding>
        {initialLoading ? (
          <TableSkeleton rows={6} />
        ) : error ? (
          <EmptyState
            icon={<Activity className="w-6 h-6" />}
            title="No se pudo cargar los deals"
            message="Hubo un error contactando al servidor."
            action={<Button size="sm" onClick={reload}>Reintentar</Button>}
          />
        ) : filteredDeals.length === 0 ? (
          <EmptyState
            icon={<Target className="w-6 h-6" />}
            title="No deals in this stage"
            message="Try another stage filter or create a new deal."
            action={
              selectedStage !== 'all' ? (
                <Button size="sm" variant="secondary" onClick={() => setSelectedStage('all')}>
                  Show all stages
                </Button>
              ) : (
                <Button size="sm" icon={<Plus className="w-4 h-4" />} onClick={() => setNewDealOpen(true)}>
                  New deal
                </Button>
              )
            }
          />
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

      {/* New deal modal */}
      <NewDealModal
        open={newDealOpen}
        onClose={() => setNewDealOpen(false)}
        onCreated={() => { reload() }}
      />
    </motion.div>
  )
}
