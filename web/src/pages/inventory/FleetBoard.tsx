// 03-garage-fleet F3 — "Tablero" (§6.2): the VEHICLE pipeline, Entrada -> Preparación
// -> Publicado -> Reservado -> Vendido -> Entregado. Lives inside "Mi flota" as a
// view (never at /kanban — 00-MASTER.md C-5 assigns that route to pilar 06's DEAL
// pipeline). Every card is a real vehicle_ulid with its real photo/price; moving a
// card writes to fleet_ops via PATCH /dealer/vehicles/{ulid}/status (dealerOps.ts).
import { useState } from 'react'
import {
  DndContext, type DragEndEvent, type DragStartEvent,
  PointerSensor, useSensor, useSensors, DragOverlay, closestCenter,
} from '@dnd-kit/core'
import { SortableContext, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, Tag } from 'lucide-react'
import type { VehicleListItem } from '../../api/cardeep'
import { useToast } from '../../components/Toast'
import { CardSkeleton } from '../../components/Skeleton'
import EmptyState from '../../components/EmptyState'
import { formatPrice, daysInStock } from './derive'
import { FLEET_OPS_STATUSES, FLEET_OPS_STATUS_LABELS, type FleetOpsStatus } from '../../api/dealerOps'
import { useFleetBoard } from './useFleetBoard'
import VehiclePhoto from './VehiclePhoto'
import PriceOverrideForm from './PriceOverrideForm'

// Status palette — DATA semantics only (tokens.css v3.1: teal/emerald/amber/rose/sky
// are reserved for exactly this, brand blue for the "live" stage; no violet anywhere).
const STAGE_COLOR: Record<FleetOpsStatus, string> = {
  entrada: 'var(--t4)',
  preparacion: 'var(--c-amber)',
  publicado: 'var(--c-blue)',
  reservado: 'var(--c-sky)',
  vendido: 'var(--c-emerald)',
  entregado: 'var(--c-teal)',
}

interface CardProps {
  vehicle: VehicleListItem
  now: Date
  onOverride: (ulid: string) => void
  isDragging?: boolean
  /** Entrance stagger index — capped by the caller, purely cosmetic on mount. */
  enterDelay?: number
}

function VehicleCard({ vehicle, now, onOverride, isDragging, enterDelay = 0 }: CardProps) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: vehicle.vehicle_ulid })
  // NOTE: only opacity/animation-delay are set via a CSS class (below) — `transform`
  // stays exclusively on this inline style, owned by dnd-kit. Mixing a transform-based
  // CSS entrance animation in here would race dnd-kit's own positioning transform.
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.35 : 1, animationDelay: `${enterDelay}ms` }

  return (
    <div
      ref={setNodeRef}
      className="glass fleet-card"
      style={{ ...style, borderRadius: 12, overflow: 'hidden', display: 'flex', gap: 8, padding: 8 }}
    >
      <button {...attributes} {...listeners} aria-label="Arrastrar" className="fleet-drag-handle" style={{ display: 'flex', alignItems: 'flex-start', paddingTop: 4, background: 'none', border: 'none', color: 'var(--t4)', cursor: 'grab' }}>
        <GripVertical style={{ width: 13, height: 13 }} />
      </button>
      <div style={{ width: 48, height: 36, borderRadius: 8, overflow: 'hidden', flexShrink: 0 }}>
        <VehiclePhoto photoUrl={vehicle.photo_url} make={vehicle.make} />
      </div>
      <div style={{ minWidth: 0, flex: 1 }}>
        <p style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--t1)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {vehicle.title ?? `${vehicle.make} ${vehicle.model}`}
        </p>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 2 }}>
          <span className="tabular-nums" style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--t2)', fontFamily: 'JetBrains Mono, monospace' }}>
            {formatPrice(vehicle.price, vehicle.currency)}
          </span>
          <span className="tabular-nums" style={{ fontSize: 10, color: 'var(--t4)' }}>{daysInStock(vehicle.first_seen, now)}d</span>
        </div>
        <button
          onClick={() => onOverride(vehicle.vehicle_ulid)}
          className="fleet-reprice-btn"
          style={{ display: 'flex', alignItems: 'center', gap: 3, marginTop: 4, fontSize: 10, fontWeight: 700, color: 'var(--c-blue)', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
        >
          <Tag style={{ width: 10, height: 10 }} /> Reprecio
        </button>
      </div>
    </div>
  )
}

const CARD_STAGGER_CAP = 8

function Column({ status, vehicles, now, onOverride }: { status: FleetOpsStatus; vehicles: VehicleListItem[]; now: Date; onOverride: (ulid: string) => void }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, minWidth: 220, flex: '1 1 0' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 2px' }}>
        <span style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: STAGE_COLOR[status] }}>
          {FLEET_OPS_STATUS_LABELS[status]}
        </span>
        <span className="tabular-nums" style={{ fontSize: 11, color: 'var(--t4)', fontWeight: 700 }}>{vehicles.length}</span>
      </div>
      <SortableContext id={status} items={vehicles.map(v => v.vehicle_ulid)} strategy={verticalListSortingStrategy}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, minHeight: 80, padding: 6, borderRadius: 12, border: '1px dashed var(--border-subtle)', flex: 1 }}>
          {vehicles.map((v, idx) => (
            <VehicleCard key={v.vehicle_ulid} vehicle={v} now={now} onOverride={onOverride} enterDelay={Math.min(idx, CARD_STAGGER_CAP) * 25} />
          ))}
          {vehicles.length === 0 && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 48, fontSize: 11, color: 'var(--t4)', fontStyle: 'italic' }}>Vacío</div>
          )}
        </div>
      </SortableContext>
    </div>
  )
}

export default function FleetBoard({ cdp, vehicles, now }: { cdp: string; vehicles: readonly VehicleListItem[]; now: Date }) {
  const { board, loading, error, moveVehicle, priceOverride } = useFleetBoard(cdp, vehicles)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [overrideUlid, setOverrideUlid] = useState<string | null>(null)
  const { error: toastError } = useToast()
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }))

  function findStageOf(ulid: string): FleetOpsStatus | null {
    for (const s of FLEET_OPS_STATUSES) if (board[s].some(v => v.vehicle_ulid === ulid)) return s
    return null
  }

  function onDragStart(e: DragStartEvent) { setActiveId(String(e.active.id)) }

  async function onDragEnd(e: DragEndEvent) {
    const { active, over } = e
    setActiveId(null)
    if (!over) return
    const from = findStageOf(String(active.id))
    const to = (FLEET_OPS_STATUSES as string[]).includes(String(over.id))
      ? (String(over.id) as FleetOpsStatus)
      : findStageOf(String(over.id))
    if (!from || !to || from === to) return
    try {
      await moveVehicle(String(active.id), to)
    } catch {
      toastError('No se pudo mover el vehículo — reintenta')
    }
  }

  const activeVehicle = activeId ? vehicles.find(v => v.vehicle_ulid === activeId) ?? null : null
  const overrideVehicle = overrideUlid ? vehicles.find(v => v.vehicle_ulid === overrideUlid) ?? null : null

  if (loading) {
    return (
      <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 8 }}>
        {FLEET_OPS_STATUSES.map(s => (
          <div key={s} style={{ display: 'flex', flexDirection: 'column', gap: 8, minWidth: 220, flex: '1 1 0' }}>
            <div className="skeleton" style={{ height: 13, width: '55%', borderRadius: 6 }} />
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ))}
      </div>
    )
  }
  if (error) return <EmptyState title="No se pudo cargar el tablero" message={error} />

  return (
    <>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragStart={onDragStart} onDragEnd={onDragEnd}>
        <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 8 }}>
          {FLEET_OPS_STATUSES.map(s => (
            <Column key={s} status={s} vehicles={board[s]} now={now} onOverride={setOverrideUlid} />
          ))}
        </div>
        <DragOverlay dropAnimation={null}>
          {activeVehicle && (
            <div className="glass" style={{ borderRadius: 12, padding: 8, display: 'flex', gap: 8, width: 220, boxShadow: 'var(--shadow-card-hover)' }}>
              <div style={{ width: 48, height: 36, borderRadius: 8, overflow: 'hidden', flexShrink: 0 }}>
                <VehiclePhoto photoUrl={activeVehicle.photo_url} make={activeVehicle.make} />
              </div>
              <div style={{ minWidth: 0, flex: 1 }}>
                <p style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--t1)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {activeVehicle.title ?? `${activeVehicle.make} ${activeVehicle.model}`}
                </p>
                <span className="tabular-nums" style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--t2)', fontFamily: 'JetBrains Mono, monospace' }}>
                  {formatPrice(activeVehicle.price, activeVehicle.currency)}
                </span>
              </div>
            </div>
          )}
        </DragOverlay>
      </DndContext>

      {overrideVehicle && (
        <PriceOverrideForm
          vehicle={overrideVehicle}
          onClose={() => setOverrideUlid(null)}
          onSubmit={async (targetPrice, reason) => {
            await priceOverride(overrideVehicle.vehicle_ulid, targetPrice, reason)
            setOverrideUlid(null)
          }}
        />
      )}

      <style>{`
        @keyframes fleetCardIn { from { opacity: 0; } to { opacity: 1; } }
        .fleet-card { animation: fleetCardIn 0.22s ease-out backwards; transition: border-color 0.15s, box-shadow 0.15s; }
        .fleet-card:hover { border-color: var(--glass-border-hi); box-shadow: var(--shadow-card-hover); }
        .fleet-drag-handle:hover { color: var(--t2); }
        .fleet-reprice-btn { transition: opacity 0.12s; }
        .fleet-reprice-btn:hover, .fleet-reprice-btn:focus-visible { opacity: 0.75; }
      `}</style>
    </>
  )
}
