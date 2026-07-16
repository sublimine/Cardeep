import { useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import { useRef, useState } from 'react'
import * as THREE from 'three'
import { MAKE_GRAD, DEFAULT_GRAD } from '../VehiclePhoto'
import { CARD_W, CARD_H, type CardPlacement } from './layout'
import { STALE_DAYS } from '../config'

function ageColor(days: number): string {
  if (days < 30) return '#059669'
  if (days < STALE_DAYS) return '#d97706'
  return '#e11d48'
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
          instead of disappearing into it (there's no card border here like in 2D). */}
      <mesh>
        <planeGeometry args={[CARD_W, CARD_H]} />
        <meshStandardMaterial
          color={baseColor}
          emissive={baseColor}
          emissiveIntensity={0.7}
          roughness={0.7}
          transparent
          opacity={opacity}
        />
      </mesh>

      {/* Frame edge — thin light border so the card silhouette is legible in the void */}
      <mesh position={[0, 0, -0.005]}>
        <planeGeometry args={[CARD_W + 0.04, CARD_H + 0.04]} />
        <meshBasicMaterial color="#ffffff" transparent opacity={0.12 * opacity} />
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
