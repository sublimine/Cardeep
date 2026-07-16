import { Suspense, lazy, useMemo, useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import { PageSkeleton } from '../../components/LoadingSpinner'
import EmptyState from '../../components/EmptyState'
import Button from '../../components/Button'
import { useDealerInventory } from './useDealerInventory'
import { useInventoryState, deriveVisible } from './useInventoryState'
import { applyFilters, buildChips, stockStats, toCsv, relativeDate } from './derive'
import DealerHeader from './DealerHeader'
import Toolbar from './Toolbar'
import FilterRail from './FilterRail'
import VehicleTable from './VehicleTable'
import VehicleGrid from './VehicleGrid'
import VehicleDetailModal from './VehicleDetailModal'
import ActivityDrawer from './ActivityDrawer'

const GarageScene = lazy(() => import('./garage/GarageScene'))

function downloadCsv(csv: string, filename: string) {
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export default function Inventory() {
  const { entity, vehicles, loadedCount, isComplete, loading, error, reload } = useDealerInventory()
  const state = useInventoryState()
  const [activityOpen, setActivityOpen] = useState(false)
  const [recentEventCount, setRecentEventCount] = useState<number | null>(null)
  const [filterRailOpen, setFilterRailOpen] = useState(false)

  // Stamped once per mount — freshness labels don't need sub-second precision.
  const [now] = useState(() => new Date())

  const filtered = useMemo(() => deriveVisible(vehicles, state.filters, state.sort, now), [vehicles, state.filters, state.sort, now])
  const chipPool = useMemo(() => applyFilters(vehicles, { ...state.filters, chip: null }, now), [vehicles, state.filters, now])
  const chips = useMemo(() => buildChips(chipPool, now), [chipPool, now])
  const stats = useMemo(() => stockStats(vehicles, now), [vehicles, now])

  const hasActiveFilters = state.filters.makes.length > 0 || state.filters.fuels.length > 0 || state.filters.transmissions.length > 0
    || state.filters.yearMin !== null || state.filters.yearMax !== null
    || state.filters.priceMin !== null || state.filters.priceMax !== null
    || state.filters.kmMin !== null || state.filters.kmMax !== null
    || state.filters.search !== '' || state.filters.chip !== null

  const freshnessLabel = useMemo(() => {
    if (vehicles.length === 0) return 'Sin datos aún'
    const maxLastSeen = vehicles.reduce((max, v) => Math.max(max, new Date(v.last_seen).getTime()), 0)
    return `Actualizado ${relativeDate(new Date(maxLastSeen).toISOString(), now)}`
  }, [vehicles, now])

  const selectedVehicle = state.selectedUlid ? vehicles.find(v => v.vehicle_ulid === state.selectedUlid) ?? null : null

  if (loading && vehicles.length === 0 && !error) return <PageSkeleton />

  if (error && vehicles.length === 0) {
    return (
      <div style={{ padding: '24px 28px' }}>
        <EmptyState
          title="No se pudo cargar el inventario"
          message={error}
          action={<Button onClick={reload}>Reintentar</Button>}
        />
      </div>
    )
  }

  return (
    <div style={{ padding: '20px 24px 48px', maxWidth: 1600, margin: '0 auto' }}>
      <DealerHeader
        entity={entity}
        loading={loading}
        stats={stats}
        isComplete={isComplete}
        loadedCount={loadedCount}
        recentEventCount={recentEventCount}
        onOpenActivity={() => setActivityOpen(true)}
      />

      <Toolbar
        search={state.filters.search}
        onSearchChange={state.setSearch}
        sort={state.sort}
        onSortChange={state.setSort}
        chips={chips}
        activeChip={state.filters.chip}
        onChipToggle={c => state.setChip(state.filters.chip === c ? null : c)}
        view={state.view}
        onViewChange={state.setView}
        visibleCount={filtered.length}
        loadedCount={loadedCount}
        totalExpected={entity?.available_inventory ?? null}
        isComplete={isComplete}
        onExportCsv={() => downloadCsv(toCsv(filtered, now), `cardeep_gyata_inventario_${now.toISOString().slice(0, 10)}.csv`)}
        freshnessLabel={freshnessLabel}
        onToggleFilters={() => setFilterRailOpen(o => !o)}
        hasActiveFilters={hasActiveFilters}
        onClearFilters={state.clearFilters}
      />

      <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
        <div className="inventory-filter-rail" style={{ display: filterRailOpen ? 'block' : undefined }}>
          <FilterRail
            vehicles={vehicles}
            filters={state.filters}
            onToggleMake={state.toggleMake}
            onToggleFuel={state.toggleFuel}
            onToggleTransmission={state.toggleTransmission}
            onYearRange={state.setYearRange}
            onPriceRange={state.setPriceRange}
            onKmRange={state.setKmRange}
            now={now}
          />
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          {filtered.length === 0 ? (
            <EmptyState title="Sin coincidencias" message="Ajusta la búsqueda o los filtros." />
          ) : state.view === 'tabla' ? (
            <VehicleTable vehicles={filtered} sort={state.sort} onSortChange={state.setSort} onSelect={state.selectVehicle} now={now} />
          ) : state.view === 'tarjetas' ? (
            <VehicleGrid vehicles={filtered} onSelect={state.selectVehicle} now={now} />
          ) : (
            <Suspense fallback={<div style={{ height: 560, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--t4)', fontSize: 13 }}>Preparando garaje…</div>}>
              <GarageScene vehicles={filtered} allVehicles={vehicles} onOpenDetail={state.selectVehicle} openUlid={state.selectedUlid} />
            </Suspense>
          )}
        </div>
      </div>

      <AnimatePresence>
        {selectedVehicle && (
          <VehicleDetailModal vehicle={selectedVehicle} onClose={() => state.selectVehicle(null)} now={now} />
        )}
      </AnimatePresence>

      <ActivityDrawer open={activityOpen} onClose={() => setActivityOpen(false)} now={now} onCountLoaded={setRecentEventCount} />

      <style>{`
        .filter-rail-toggle { display: none; }
        @media (max-width: 1100px) {
          .filter-rail-toggle { display: flex !important; }
          .inventory-filter-rail { display: none; }
          .inventory-filter-rail[style*="display: block"] {
            position: fixed; inset: 0; z-index: 150; padding: 16px; overflow-y: auto;
            background: var(--bg-base);
          }
        }
        @media (max-width: 720px) {
          .view-label { display: none; }
        }
      `}</style>
    </div>
  )
}
