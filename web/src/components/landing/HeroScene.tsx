import { Canvas, useFrame } from '@react-three/fiber'
import { Environment } from '@react-three/drei'
import { Bloom, ChromaticAberration, EffectComposer, Noise, Vignette } from '@react-three/postprocessing'
import { Suspense, useMemo, useRef } from 'react'
import * as THREE from 'three'

// Warm amber, matching the reference's horizon-glow mood exactly (owner
// correction 2026-07-23: an earlier pass re-themed this to brand blue and
// added a wireframe icosahedron centerpiece — both unrequested substitutions.
// This page replicates the reference's actual hero, which is pure atmosphere:
// a sparse scattered dust field + a horizon glow, no 3D object at all
// (confirmed via Playwright against the live reference).
const ACCENT = '#F5A623'
const DUST_COUNT = 90

function DustField({ reduceMotion }: { reduceMotion: boolean }) {
  const pointsRef = useRef<THREE.Points>(null)

  const { positions, speeds } = useMemo(() => {
    const pos = new Float32Array(DUST_COUNT * 3)
    const spd = new Float32Array(DUST_COUNT)
    for (let i = 0; i < DUST_COUNT; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 16
      pos[i * 3 + 1] = (Math.random() - 0.5) * 9
      pos[i * 3 + 2] = (Math.random() - 0.5) * 6 - 2
      spd[i] = 0.04 + Math.random() * 0.08
    }
    return { positions: pos, speeds: spd }
  }, [])

  useFrame((_, delta) => {
    if (reduceMotion || !pointsRef.current) return
    const attr = pointsRef.current.geometry.attributes.position as THREE.BufferAttribute
    for (let i = 0; i < DUST_COUNT; i++) {
      const y = attr.getY(i) + speeds[i] * delta
      attr.setY(i, y > 4.5 ? -4.5 : y)
    }
    attr.needsUpdate = true
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial color={ACCENT} size={0.045} transparent opacity={0.75} sizeAttenuation />
    </points>
  )
}

interface HeroSceneProps {
  className?: string
}

export default function HeroScene({ className }: HeroSceneProps) {
  const reduceMotion = useMemo(
    () => typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    []
  )

  return (
    <Canvas
      className={className}
      dpr={[1, 1.75]}
      gl={{ alpha: true, antialias: true, powerPreference: 'high-performance' }}
      camera={{ position: [0, 0, 6], fov: 42 }}
      style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}
    >
      <color attach="background" args={['#0a0a0a']} />
      <fog attach="fog" args={['#0a0a0a', 5, 12]} />
      <ambientLight intensity={0.2} />
      <Suspense fallback={null}>
        <DustField reduceMotion={reduceMotion} />
        <Environment preset="night" environmentIntensity={0.25} />
        <EffectComposer enableNormalPass={false}>
          <Bloom luminanceThreshold={0.2} luminanceSmoothing={0.4} intensity={0.4} mipmapBlur radius={0.5} />
          <ChromaticAberration
            offset={new THREE.Vector2(reduceMotion ? 0 : 0.0006, reduceMotion ? 0 : 0.0006)}
            radialModulation={false}
            modulationOffset={0}
          />
          <Noise opacity={0.03} />
          <Vignette eskil={false} offset={0.25} darkness={0.6} />
        </EffectComposer>
      </Suspense>
    </Canvas>
  )
}
