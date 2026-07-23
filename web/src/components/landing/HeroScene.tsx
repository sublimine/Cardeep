import { Canvas, useFrame } from '@react-three/fiber'
import { Environment, Float, MeshTransmissionMaterial } from '@react-three/drei'
import { Bloom, ChromaticAberration, EffectComposer, Noise, Vignette } from '@react-three/postprocessing'
import { Suspense, useMemo, useRef } from 'react'
import * as THREE from 'three'

const ACCENT = '#3B82F6'

/**
 * The verified censo, lit like a command-center instrument. Not a map of
 * Spain (that 3D idiom stays exclusive to /explore and /cobertura — explicit,
 * hard owner directive) and not a rendered car (no licensed/generated 3D asset
 * exists, faking one would misrepresent the product).
 */
function IndexCore({ reduceMotion }: { reduceMotion: boolean }) {
  const coreRef = useRef<THREE.Mesh>(null)
  const wireRef = useRef<THREE.Mesh>(null)

  useFrame((state, delta) => {
    if (reduceMotion) return
    if (coreRef.current) coreRef.current.rotation.y += delta * 0.1
    if (wireRef.current) wireRef.current.rotation.y -= delta * 0.06
    const targetX = state.pointer.y * 0.12
    const targetZ = state.pointer.x * 0.12
    if (coreRef.current) coreRef.current.rotation.x += (targetX - coreRef.current.rotation.x) * 0.04
    if (wireRef.current) wireRef.current.rotation.z += (targetZ - wireRef.current.rotation.z) * 0.04
  })

  return (
    <Float speed={reduceMotion ? 0 : 1.2} rotationIntensity={reduceMotion ? 0 : 0.2} floatIntensity={reduceMotion ? 0 : 0.5}>
      <mesh ref={wireRef} scale={1.5}>
        <icosahedronGeometry args={[1, 1]} />
        <meshBasicMaterial color={ACCENT} wireframe transparent opacity={0.22} />
      </mesh>
      <mesh ref={coreRef}>
        <icosahedronGeometry args={[1, 0]} />
        <MeshTransmissionMaterial
          thickness={1.1}
          roughness={0.04}
          transmission={1}
          ior={1.3}
          chromaticAberration={0.04}
          anisotropy={0.2}
          color={ACCENT}
          distortion={0.2}
          distortionScale={0.35}
          temporalDistortion={reduceMotion ? 0 : 0.1}
          emissive={ACCENT}
          emissiveIntensity={0.15}
        />
      </mesh>
    </Float>
  )
}

/**
 * Telemetry constellation — small nodes orbiting the core at three different
 * radii/speeds, each on its own inclined ring. The literal visual of "índice
 * vivo": a live, tracked set of points around a verified center, not
 * decorative sparkle.
 */
function OrbitRing({ radius, count, speed, tilt, reduceMotion }: { radius: number; count: number; speed: number; tilt: number; reduceMotion: boolean }) {
  const groupRef = useRef<THREE.Group>(null)
  const positions = useMemo(() => {
    return Array.from({ length: count }, (_, i) => (i / count) * Math.PI * 2)
  }, [count])

  useFrame((_, delta) => {
    if (reduceMotion || !groupRef.current) return
    groupRef.current.rotation.z += delta * speed
  })

  return (
    <group ref={groupRef} rotation={[tilt, 0, 0]}>
      {positions.map((angle, i) => (
        <mesh key={i} position={[Math.cos(angle) * radius, Math.sin(angle) * radius, 0]}>
          <sphereGeometry args={[0.028, 8, 8]} />
          <meshBasicMaterial color={ACCENT} />
        </mesh>
      ))}
    </group>
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
      camera={{ position: [0, 0, 4.6], fov: 36 }}
      style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}
    >
      <color attach="background" args={['#0a0a0a']} />
      <fog attach="fog" args={['#0a0a0a', 4, 9]} />
      <ambientLight intensity={0.35} />
      <directionalLight position={[3, 4, 2]} intensity={1.4} color={ACCENT} />
      <directionalLight position={[-3, -2, -2]} intensity={0.4} color="#5B96F8" />
      <Suspense fallback={null}>
        <IndexCore reduceMotion={reduceMotion} />
        <OrbitRing radius={2.1} count={10} speed={0.09} tilt={0.35} reduceMotion={reduceMotion} />
        <OrbitRing radius={2.6} count={14} speed={-0.06} tilt={-0.5} reduceMotion={reduceMotion} />
        <OrbitRing radius={3.1} count={8} speed={0.045} tilt={1.1} reduceMotion={reduceMotion} />
        <Environment preset="night" environmentIntensity={0.5} />
        <EffectComposer enableNormalPass={false}>
          <Bloom luminanceThreshold={0.15} luminanceSmoothing={0.4} intensity={0.9} mipmapBlur radius={0.7} />
          <ChromaticAberration
            offset={new THREE.Vector2(reduceMotion ? 0 : 0.0009, reduceMotion ? 0 : 0.0009)}
            radialModulation={false}
            modulationOffset={0}
          />
          <Noise opacity={0.035} />
          <Vignette eskil={false} offset={0.25} darkness={0.65} />
        </EffectComposer>
      </Suspense>
    </Canvas>
  )
}
