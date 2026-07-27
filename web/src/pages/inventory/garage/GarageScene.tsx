import { Canvas, useFrame, useThree, invalidate } from '@react-three/fiber'
import { OrbitControls, Stars, Text } from '@react-three/drei'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import type { VehicleListItem } from '../../../api/cardeep'
import EmptyState from '../../../components/EmptyState'
import { daysInStock, groupByMake } from '../derive'
import { computeGarageLayout, MIN_RADIUS, type CardPlacement } from './layout'
import { usePhotoBudget } from './usePhotoBudget'
import GarageCard from './GarageCard'
import GarageHud from './GarageHud'

const BG_COLOR = '#050510'

function hasWebGL(): boolean {
  try {
    const canvas = document.createElement('canvas')
    return !!(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch {
    return false
  }
}

interface SceneContentProps {
  cards: CardPlacement[]
  visibleUlids: Set<string>
  selectedUlid: string | null
  hoveredUlid: string | null
  photoEligible: Set<string>
  now: Date
  onHover: (ulid: string | null) => void
  onSelect: (ulid: string) => void
  onControlsEnd: (camera: THREE.Vector3) => void
  flyTo: { x: number; y: number; z: number; target: THREE.Vector3 } | null
  reducedMotion: boolean
  autoRotate: boolean
  resetSignal: number
  /** Position of the largest pavilion — used to aim the initial/reset camera at real content instead of empty space. */
  initialLookAt: { x: number; y: number; z: number }
}

function SceneContent({
  cards, visibleUlids, selectedUlid, hoveredUlid, photoEligible, now,
  onHover, onSelect, onControlsEnd, flyTo, reducedMotion, autoRotate, resetSignal, initialLookAt,
}: SceneContentProps) {
  const { camera } = useThree()
  const controlsRef = useRef<any>(null)
  const flyingRef = useRef(false)

  useEffect(() => { flyingRef.current = flyTo !== null }, [flyTo])

  // Initial pose + reset — pulled back from center so the largest pavilion (real
  // content, not an arbitrary direction) is framed immediately on mount.
  useEffect(() => {
    const backX = initialLookAt.x * 0.7
    const backZ = initialLookAt.z * 0.7
    camera.position.set(backX, 4.6, backZ)
    controlsRef.current?.target.set(initialLookAt.x, 4, initialLookAt.z)
    controlsRef.current?.update()
    invalidate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetSignal, initialLookAt.x, initialLookAt.z])

  useFrame(() => {
    if (flyTo && flyingRef.current) {
      const dist = camera.position.distanceTo(new THREE.Vector3(flyTo.x, flyTo.y, flyTo.z))
      if (reducedMotion || dist < 0.05) {
        camera.position.set(flyTo.x, flyTo.y, flyTo.z)
        controlsRef.current?.target.copy(flyTo.target)
        flyingRef.current = false
      } else {
        camera.position.lerp(new THREE.Vector3(flyTo.x, flyTo.y, flyTo.z), 0.08)
        controlsRef.current?.target.lerp(flyTo.target, 0.08)
      }
      controlsRef.current?.update()
      invalidate()
    }
  })

  return (
    <>
      <ambientLight intensity={0.9} />
      <directionalLight position={[10, 20, 10]} intensity={0.6} />
      <fog attach="fog" args={[BG_COLOR, 20, 90]} />
      {!reducedMotion && <Stars radius={80} depth={40} count={800} factor={2} fade speed={0} />}

      {cards.map(placement => (
        <GarageCard
          key={placement.vehicle.vehicle_ulid}
          placement={placement}
          days={daysInStock(placement.vehicle.first_seen, now)}
          isDimmed={!visibleUlids.has(placement.vehicle.vehicle_ulid)}
          isSelected={selectedUlid === placement.vehicle.vehicle_ulid}
          showPhoto={photoEligible.has(placement.vehicle.vehicle_ulid) || hoveredUlid === placement.vehicle.vehicle_ulid || selectedUlid === placement.vehicle.vehicle_ulid}
          onHover={onHover}
          onSelect={onSelect}
        />
      ))}

      {useMemo(() => computeGarageLayout(groupByMake(cards.map(c => c.vehicle))).labels, [cards]).map(label => (
        <Text
          key={label.make}
          position={[label.x, label.y, label.z]}
          fontSize={0.5}
          color="#9aa6be"
          anchorX="center"
          anchorY="middle"
        >
          {label.make.toUpperCase()} · {label.count}
        </Text>
      ))}

      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.08}
        minDistance={4}
        maxDistance={55}
        minPolarAngle={Math.PI * 0.15}
        maxPolarAngle={Math.PI * 0.55}
        autoRotate={autoRotate && !reducedMotion}
        autoRotateSpeed={0.5}
        onEnd={() => onControlsEnd(camera.position.clone())}
        makeDefault
      />
    </>
  )
}

interface GarageSceneProps {
  vehicles: readonly VehicleListItem[]
  allVehicles: readonly VehicleListItem[]
  /** Opens the real vehicle detail modal (URL `?v=`) — only called from an explicit "Abrir ficha" action. */
  onOpenDetail: (ulid: string) => void
  /** The ulid the modal is currently open for (if any) — synced into local focus so a deep-link lands the camera on the right card. */
  openUlid: string | null
}

export default function GarageScene({ vehicles, allVehicles, onOpenDetail, openUlid }: GarageSceneProps) {
  const [now] = useState(() => new Date())
  // Camera focus is a SEPARATE, lighter concept than "the modal is open": clicking a
  // card in 3D dollies the camera and shows the HUD mini-card, it does NOT open the
  // full modal (spec: "el HUD inferior muestra la mini-ficha" on click; only the HUD's
  // "Abrir ficha" button opens the real modal).
  const [focusedUlid, setFocusedUlid] = useState<string | null>(openUlid)
  const [hoveredUlid, setHoveredUlid] = useState<string | null>(null)
  const [autoRotate, setAutoRotate] = useState(false)
  const [resetSignal, setResetSignal] = useState(0)
  const [hintDismissed, setHintDismissed] = useState(false)
  const reducedMotion = useMemo(() => typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches, [])

  // A deep-link (?v=) opened while already in the garage view should focus that card too.
  useEffect(() => { if (openUlid) setFocusedUlid(openUlid) }, [openUlid])

  const layout = useMemo(() => computeGarageLayout(groupByMake(allVehicles)), [allVehicles])
  const visibleUlids = useMemo(() => new Set(vehicles.map(v => v.vehicle_ulid)), [vehicles])
  const { eligible: photoEligible, recompute } = usePhotoBudget(layout.cards)

  const pinned = useMemo(() => [focusedUlid, hoveredUlid].filter((v): v is string => v !== null), [focusedUlid, hoveredUlid])

  useEffect(() => {
    recompute({ x: 0, y: 3, z: 0 }, pinned)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pinned])

  const focusedPlacement = focusedUlid ? layout.cards.find(c => c.vehicle.vehicle_ulid === focusedUlid) ?? null : null
  const focusedIndex = focusedUlid ? vehicles.findIndex(v => v.vehicle_ulid === focusedUlid) : -1

  const flyTo = useMemo(() => {
    if (!focusedPlacement) return null
    const r = Math.max(MIN_RADIUS * 0.4, layout.radius - 7)
    const theta = Math.atan2(focusedPlacement.z, focusedPlacement.x)
    return {
      x: r * Math.cos(theta), y: focusedPlacement.y + 0.3, z: r * Math.sin(theta),
      target: new THREE.Vector3(focusedPlacement.x, focusedPlacement.y, focusedPlacement.z),
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusedUlid])

  const stepFocus = useCallback((dir: 1 | -1) => {
    if (vehicles.length === 0) return
    const idx = focusedIndex === -1 ? 0 : (focusedIndex + dir + vehicles.length) % vehicles.length
    setFocusedUlid(vehicles[idx].vehicle_ulid)
  }, [vehicles, focusedIndex])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setFocusedUlid(null)
      if (e.key === 'ArrowLeft') stepFocus(-1)
      if (e.key === 'ArrowRight') stepFocus(1)
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [stepFocus])

  if (!hasWebGL()) {
    return (
      <div style={{ padding: '48px 0' }}>
        <EmptyState
          title="Tu navegador no soporta WebGL"
          message="El Garaje 3D necesita WebGL. Puedes seguir viendo el inventario en Tabla o Tarjetas."
        />
      </div>
    )
  }

  return (
    <div style={{ position: 'relative', height: 620, borderRadius: 18, overflow: 'hidden', background: BG_COLOR, border: '1px solid var(--border-default)', boxShadow: 'var(--shadow-card)' }}>
      <Canvas
        dpr={[1, 1.5]}
        frameloop="demand"
        camera={{ fov: 60, near: 0.1, far: 200 }}
        gl={{ antialias: true, powerPreference: 'high-performance' }}
        onClick={() => setHintDismissed(true)}
      >
        <color attach="background" args={[BG_COLOR]} />
        <SceneContent
          cards={layout.cards}
          visibleUlids={visibleUlids}
          selectedUlid={focusedUlid}
          hoveredUlid={hoveredUlid}
          photoEligible={photoEligible}
          now={now}
          initialLookAt={layout.labels[0] ?? { x: 0, y: 0, z: -Math.max(MIN_RADIUS, layout.radius) }}
          onHover={setHoveredUlid}
          onSelect={setFocusedUlid}
          onControlsEnd={pos => recompute(pos, pinned)}
          flyTo={flyTo}
          reducedMotion={reducedMotion}
          autoRotate={autoRotate}
          resetSignal={resetSignal}
        />
      </Canvas>

      <GarageHud
        selected={focusedPlacement?.vehicle ?? null}
        selectedIndex={Math.max(0, focusedIndex)}
        total={vehicles.length}
        onPrev={() => stepFocus(-1)}
        onNext={() => stepFocus(1)}
        onOpenDetail={() => focusedUlid && onOpenDetail(focusedUlid)}
        onDeselect={() => setFocusedUlid(null)}
        onResetCamera={() => setResetSignal(s => s + 1)}
        autoRotate={autoRotate}
        onToggleAutoRotate={() => setAutoRotate(a => !a)}
        showHint={!hintDismissed}
        now={now}
      />
    </div>
  )
}
