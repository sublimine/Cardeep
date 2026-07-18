import { motion } from 'framer-motion'
import React, { useState } from 'react'
import {
  DndContext, DragEndEvent, DragOverEvent, DragStartEvent,
  PointerSensor, useSensor, useSensors, DragOverlay, closestCenter,
} from '@dnd-kit/core'
import { SortableContext, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, AlertCircle, RefreshCw } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Button from '../components/Button'
import { cn } from '../lib/cn'
import { useKanban, STAGES, STAGE_LABELS, STAGE_WIPS, type KanbanStage } from '../hooks/useKanban'
import { useDealsSummary } from '../hooks/useDeals'
import type { Deal } from '../types'

// ── Per-stage visual config — no violet/purple ────────────────────────────────

const stageConfig: Record<KanbanStage, {
  zoneBg: string
  cardBar: string
  headerColor: string
  valuePill: string
}> = {
  lead:        { zoneBg: 'bg-blue-500/5 border-blue-500/15',     cardBar: 'bg-blue-400',    headerColor: 'text-blue-400',    valuePill: 'bg-blue-500/10 text-blue-400' },
  contacted:   { zoneBg: 'bg-sky-500/5 border-sky-500/15',       cardBar: 'bg-sky-400',     headerColor: 'text-sky-400',     valuePill: 'bg-sky-500/10 text-sky-400' },
  offer:       { zoneBg: 'bg-amber-500/5 border-amber-500/15',   cardBar: 'bg-amber-400',   headerColor: 'text-amber-400',   valuePill: 'bg-amber-500/10 text-amber-400' },
  negotiation: { zoneBg: 'bg-orange-500/5 border-orange-500/15', cardBar: 'bg-orange-400',  headerColor: 'text-orange-400',  valuePill: 'bg-orange-500/10 text-orange-400' },
  won:         { zoneBg: 'bg-emerald-500/5 border-emerald-500/15', cardBar: 'bg-emerald-400', headerColor: 'text-emerald-400', valuePill: 'bg-emerald-500/10 text-emerald-400' },
  lost:        { zoneBg: 'bg-rose-500/5 border-rose-500/15',     cardBar: 'bg-rose-400',    headerColor: 'text-rose-400',    valuePill: 'bg-rose-500/10 text-rose-400' },
}

// ── Kanban card ───────────────────────────────────────────────────────────────

function KanbanCard({ deal, isDragging }: { deal: Deal; isDragging?: boolean }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: deal.id,
    data: { stage: deal.stage },
  })
  const cfg = stageConfig[deal.stage as KanbanStage]
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.35 : 1,
  }

  const age = Math.floor((Date.now() - new Date(deal.createdAt || Date.now()).getTime()) / 86400000)

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="relative glass rounded-lg overflow-hidden pl-2.5 group select-none"
    >
      {/* Stage accent bar */}
      <span className={cn('absolute left-0 inset-y-0 w-[3px]', cfg.cardBar)} />

      <div className="flex items-start gap-2 p-3">
        <button
          {...attributes}
          {...listeners}
          className="mt-0.5 text-text-muted hover:text-text-secondary cursor-grab active:cursor-grabbing touch-none shrink-0 transition-colors"
          aria-label="Drag to reorder"
        >
          <GripVertical className="w-3.5 h-3.5" />
        </button>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-text-primary truncate leading-snug">
            {deal.vehicleName ?? `Deal #${deal.id.slice(0, 6)}`}
          </p>
          <p className="text-xs text-text-muted mt-0.5 truncate">
            {deal.contactName ?? 'Unknown contact'}
          </p>

          <div className="flex items-center justify-between mt-2.5 gap-2">
            {deal.price ? (
              <span className="text-xs font-bold text-text-primary tabular-nums">
                €{deal.price.toLocaleString()}
              </span>
            ) : (
              <span className="text-xs text-text-muted">—</span>
            )}
            {age > 0 && (
              <span className="text-[10px] text-text-muted tabular-nums shrink-0">
                {age}d
              </span>
            )}
          </div>

          {/* F5: census cross-reference chip — only when it resolved for real */}
          {deal.vehicleContext && (
            <p className={cn(
              'text-[10px] mt-1.5 truncate',
              deal.vehicleContext.stillListed ? 'text-text-muted' : 'text-rose-400 font-semibold',
            )}>
              {deal.vehicleContext.stillListed
                ? `${deal.vehicleContext.daysInStock}d en tu stock`
                : 'Ya no está anunciado'}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Kanban column ─────────────────────────────────────────────────────────────

function KanbanColumn({
  stage,
  deals,
  activeId,
}: {
  stage: KanbanStage
  deals: Deal[]
  activeId: string | null
}) {
  const limit      = STAGE_WIPS[stage]
  const over       = limit > 0 && deals.length > limit
  const cfg        = stageConfig[stage]
  const pct        = limit > 0 ? Math.min(100, (deals.length / limit) * 100) : 0
  const totalValue = deals.reduce((s, d) => s + (d.price ?? 0), 0)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: STAGES.indexOf(stage) * 0.05 }}
      className="flex flex-col gap-2 min-w-[240px] md:min-w-0 md:flex-1"
    >
      {/* Column header */}
      <div className="px-1">
        <div className="flex items-center justify-between mb-1">
          <span className={cn('text-[11px] font-bold uppercase tracking-wider', cfg.headerColor)}>
            {STAGE_LABELS[stage]}
          </span>
          <div className="flex items-center gap-1.5">
            {totalValue > 0 && (
              <span className={cn('text-[10px] font-semibold px-1.5 py-0.5 rounded', cfg.valuePill)}>
                €{(totalValue / 1000).toFixed(0)}k
              </span>
            )}
            <span className="text-xs px-1.5 py-0.5 rounded-full bg-glass-medium text-text-muted font-medium tabular-nums">
              {deals.length}
            </span>
            {over && <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
          </div>
        </div>

        {/* WIP progress bar */}
        {limit > 0 && (
          <div className="h-0.5 bg-glass-medium rounded-full overflow-hidden">
            <motion.div
              className={cn('h-full rounded-full', over ? 'bg-rose-400' : cfg.cardBar)}
              initial={{ width: 0 }}
              animate={{ width: `${pct}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
        )}
      </div>

      {/* Drop zone */}
      <SortableContext
        id={stage}
        items={deals.map(d => d.id)}
        strategy={verticalListSortingStrategy}
      >
        <div
          className={cn(
            'flex flex-col gap-2 min-h-[80px] p-2 rounded-xl border-2 transition-colors flex-1',
            over ? 'border-rose-500/30 bg-rose-500/5' : cn('border-2', cfg.zoneBg),
          )}
        >
          {deals.map(deal => (
            <KanbanCard key={deal.id} deal={deal} isDragging={deal.id === activeId} />
          ))}

          {deals.length === 0 && (
            <div className="flex items-center justify-center h-12 text-text-muted text-[11px]">
              Drop here
            </div>
          )}
        </div>
      </SortableContext>
    </motion.div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Kanban() {
  const { board: apiBoard, loading, error, moveCard, reload } = useKanban()
  const { data: summary } = useDealsSummary()
  const [activeId,    setActiveId]    = useState<string | null>(null)
  const [activeStage, setActiveStage] = useState<KanbanStage | null>(null)

  // Honest board: on fetch failure useKanban's own empty initial state stands —
  // never a fabricated pipeline (carta §4 "regla transversal de honestidad de producto").
  const board = apiBoard

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
  )

  function findStageOf(id: string): KanbanStage | null {
    for (const s of STAGES) {
      if ((board[s] as Deal[]).some(d => d.id === id)) return s
    }
    return null
  }

  function onDragStart(e: DragStartEvent) {
    setActiveId(String(e.active.id))
    setActiveStage(findStageOf(String(e.active.id)))
  }

  function onDragOver(_e: DragOverEvent) {}

  async function onDragEnd(e: DragEndEvent) {
    const { active, over } = e
    setActiveId(null)
    setActiveStage(null)
    if (!over) return

    const from    = findStageOf(String(active.id))
    const toStage = STAGES.includes(over.id as KanbanStage)
      ? (over.id as KanbanStage)
      : findStageOf(String(over.id))

    if (!from || !toStage || from === toStage) return
    await moveCard(String(active.id), from, toStage)
  }

  const activeDeal = activeId
    ? (board[activeStage ?? 'lead'] as Deal[]).find(d => d.id === activeId) ?? null
    : null

  const totalDeals = STAGES.reduce((n, s) => n + (board[s] as Deal[]).length, 0)

  // carta §6 Kanban spec: "Tienes 41.300 € en juego" (Σ amount×probability) + "De contacto
  // a venta: 12 días de media" (90d lead time) — both computed once by the backend
  // (/deals/summary), never re-derived client-side (00-MASTER.md "un solo cálculo").
  const expectedValueLabel = summary
    ? `€${summary.expectedValue.toLocaleString('es-ES', { maximumFractionDigits: 0 })} en juego`
    : null
  const leadTimeLabel = summary?.avgLeadTimeDays != null
    ? `${summary.avgLeadTimeDays.toFixed(0)} días de contacto a venta`
    : null

  return (
    <div className="p-4 md:p-6 space-y-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Kanban Board</h1>
          <p className="text-sm text-text-muted mt-0.5">
            {totalDeals} deals in pipeline
            {expectedValueLabel && <> · {expectedValueLabel}</>}
            {leadTimeLabel && <> · {leadTimeLabel}</>}
          </p>
        </div>
        {loading && <LoadingSpinner size="sm" />}
      </div>

      {/* Honest error banner — never a silently-swapped fabricated board */}
      {error && (
        <EmptyState
          icon={<AlertCircle className="w-6 h-6" />}
          title="No se pudo cargar el tablero"
          message="Hubo un error contactando al servidor."
          action={<Button size="sm" icon={<RefreshCw className="w-3.5 h-3.5" />} onClick={reload}>Reintentar</Button>}
        />
      )}

      {/* Board */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={onDragStart}
        onDragOver={onDragOver}
        onDragEnd={onDragEnd}
      >
        <div className="flex gap-3 overflow-x-auto pb-4 -mx-4 px-4 md:mx-0 md:px-0 flex-1">
          {STAGES.map(stage => (
            <KanbanColumn
              key={stage}
              stage={stage}
              deals={board[stage] as Deal[]}
              activeId={activeId}
            />
          ))}
        </div>

        <DragOverlay dropAnimation={null}>
          {activeDeal ? (
            <div className="glass rounded-lg shadow-elevation-4 p-3 w-60 rotate-1 border border-border-active">
              <p className="text-sm font-semibold text-text-primary truncate">
                {activeDeal.vehicleName ?? `Deal #${activeDeal.id.slice(0, 6)}`}
              </p>
              {activeDeal.contactName && (
                <p className="text-xs text-text-muted mt-0.5">{activeDeal.contactName}</p>
              )}
              {activeDeal.price && (
                <p className="text-xs font-bold text-text-primary mt-2">
                  €{activeDeal.price.toLocaleString()}
                </p>
              )}
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>
    </div>
  )
}
