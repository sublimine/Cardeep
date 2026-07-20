import { useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import { useRef, useState } from 'react'
import * as THREE from 'three'
import { MAKE_GRAD, DEFAULT_GRAD } from '../VehiclePhoto'
import { CARD_W, CARD_H, type CardPlacement } from './layout'
import { STALE_DAYS } from '../config'
import { agingBand, type AgingBand } from '../derive'

// three.js material `color` props need a literal hex/rgb — they cannot resolve a
// CSS custom property like `var(--c-emerald)` (no DOM/CSSOM involved in the WebGL
// pipeline). This table is the one necessary exception to "always reference the
// token" — its values are kept byte-identical to derive.ts's own agingColor()
// (fresco/normal/envejecido map 1:1 to tokens.css's --c-emerald/--c-amber/--c-rose;
// critico has no token either, same literal zinc-700 derive.ts itself uses) so the
// 3D garage never disagrees with VehicleTable/VehicleDetailModal about a vehicle's
// freshness. Classification itself is NOT duplicated here — `agingBand` from
// derive.ts (the one documented canonical source, K3) is what decides the band.
const AGE_BAND_COLOR: Record<AgingBand, string> = {
  fresco: '#059669',
  normal: '#d97706',
  envejecido: '#e11d48',
  critico: '#3f3f46',
}

function ageColor(days: number): string {
  return AGE_BAND_COLOR[agingBand(days, STALE_DAYS)]
}

interface GarageCardProps {
  placement: CardPlacement
  days: number
  isDimmed: boolean
  isSelected: boolean
  showPhoto: boolean
  onHover: (ulid: string | null) => void
  onSelect: (ulid: string) => void
}

export default function GarageCard({ placement, days, isDimmed, isSelected, showPhoto, onHover, onSelect }: GarageCardProps) {
  const { vehicle, x, y, z, rotationY, make } = placement
  const groupRef = useRef<THREE.Group>(null)
  const [hovered, setHovered] = useState(false)
  const baseColor = (MAKE_GRAD[make] ?? DEFAULT_GRAD)[0]
  const targetScale = isDimmed ? 1 : (hovered || isSelected) ? 1.08 : 1

  useFrame(() => {
    if (!groupRef.current) return
    groupRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.18)
  })

  const opacity = isDimmed ? 0.08 : 1

  return (
    <group
      ref={groupRef}
      position={[x, y, z]}
      rotation={[0, rotationY, 0]}
      onPointerOver={e => { e.stopPropagation(); if (!isDimmed) { setHovered(true); onHover(vehicle.vehicle_ulid) } }}
      onPointerOut={e => { e.stopPropagation(); setHovered(false); onHover(null) }}
      onClick={e => { e.stopPropagation(); if (!isDimmed) onSelect(vehicle.vehicle_ulid) }}
    >
      {/* Selection glow — a slightly larger plane behind the card */}
      {isSelected && (
        <mesh position={[0, 0, -0.02]}>
          <planeGeometry args={[CARD_W + 0.14, CARD_H + 0.14]} />
          <meshBasicMaterial color="#3b82f6" transparent opacity={0.55 * opacity} />
        </mesh>
      )}

      {/* Base placeholder plane — always present (cheap; the photo, if any, sits in front).
          Emissive so it reads as a distinct glowing object against the near-black void
          instead of disappearing into it (there's no card border here like in 2D).
          Emissive intensity ticks up on hover/selection — the 3D equivalent of the
          2D Card component's hover glow, real feedback rather than just the scale bump. */}
      <mesh>
        <planeGeometry args={[CARD_W, CARD_H]} />
        <meshStandardMaterial
          color={baseColor}
          emissive={baseColor}
          emissiveIntensity={hovered || isSelected ? 0.95 : 0.7}
          roughness={0.7}
          transparent
          opacity={opacity}
        />
      </mesh>

      {/* Frame edge — thin light border so the card silhouette is legible in the void; brightens on hover/selection */}
      <mesh position={[0, 0, -0.005]}>
        <planeGeometry args={[CARD_W + 0.04, CARD_H + 0.04]} />
        <meshBasicMaterial color="#ffffff" transparent opacity={(hovered || isSelected ? 0.3 : 0.12) * opacity} />
      </mesh>

      {/* Bottom edge — days-in-stock semantic bar */}
      <mesh position={[0, -CARD_H / 2 + 0.03, 0.01]}>
        <planeGeometry args={[CARD_W, 0.06]} />
        <meshBasicMaterial color={ageColor(days)} transparent opacity={opacity} />
      </mesh>

      {!isDimmed && showPhoto && vehicle.photo_url && (
        <Html
          transform
          distanceFactor={6}
          position={[0, 0, 0.02]}
          occlude={false}
          style={{ pointerEvents: 'none', width: CARD_W * 100, height: CARD_H * 100 }}
        >
          <img
            src={vehicle.photo_url}
            alt=""
            referrerPolicy="no-referrer"
            style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 4, display: 'block' }}
            onError={e => { (e.currentTarget as HTMLImageElement).style.display = 'none' }}
          />
        </Html>
      )}
    </group>
  )
}
