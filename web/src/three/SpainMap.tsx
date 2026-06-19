// The hero: a navigable 3D choropleth of Spain. Each province is extruded by its
// "venta" seal coverage and coloured by verdict. Hover reads out the numbers; click
// drills into that province's inventory. Data is live (/geo/seal) with a static
// snapshot fallback, so the map is never empty. This module is lazy-loaded so Three.js
// stays out of the initial bundle.
import { useState, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, ContactShadows } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { Province } from './Province';
import { useProvinceShapes, useSealMap } from './useSpainData';
import { VERDICT_COLOR, verdictColor } from './mapColors';
import type { SealVerdict } from '../api/types';
import './SpainMap.css';

const MIN_DEPTH = 1.5;
const MAX_DEPTH = 22;

function depthFor(coverage: number | null | undefined): number {
  const c = Math.max(0, Math.min(100, coverage ?? 0));
  return MIN_DEPTH + (c / 100) * (MAX_DEPTH - MIN_DEPTH);
}

const prefersReducedMotion =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function SceneLights() {
  return (
    <>
      <ambientLight intensity={0.55} />
      <directionalLight position={[40, 80, 25]} intensity={1.15} />
      <pointLight position={[-45, 35, -25]} intensity={0.7} color="#6366f1" />
      <pointLight position={[30, 20, 40]} intensity={0.4} color="#3b82f6" />
    </>
  );
}

function MapState({ children }: { children: ReactNode }) {
  return <div className="spainmap__state mono">{children}</div>;
}

const VERDICT_LABEL: Record<SealVerdict, string> = {
  SELLADO: 'Sellado',
  PARCIAL: 'Parcial',
  GAP: 'Gap',
  NO_DENOM: 'Sin techo',
};

export default function SpainMap() {
  const { data: shapes, isError } = useProvinceShapes();
  const seal = useSealMap('venta');
  const [hovered, setHovered] = useState<string | null>(null);
  const navigate = useNavigate();

  if (isError) return <MapState>No se pudo cargar el mapa.</MapState>;
  if (!shapes) return <MapState>Cargando mapa…</MapState>;

  const hoveredShape = hovered ? shapes.find((s) => s.code === hovered) ?? null : null;
  const cov = hovered ? seal[hovered] : undefined;

  return (
    <div className="spainmap">
      <Canvas
        camera={{ position: [0, 56, 74], fov: 42 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true }}
        onPointerMissed={() => setHovered(null)}
      >
        <color attach="background" args={['#080c15']} />
        <fog attach="fog" args={['#080c15', 95, 240]} />
        <SceneLights />
        <group rotation={[-Math.PI / 2, 0, 0]}>
          {shapes.map((s) => {
            const c = seal[s.code];
            return (
              <Province
                key={s.code}
                shape={s}
                depth={depthFor(c?.coverage_pct)}
                color={verdictColor(c?.verdict)}
                hovered={hovered === s.code}
                dimmed={hovered !== null}
                onHover={setHovered}
                onSelect={(code) => navigate(`/explore?prov=${code}`)}
              />
            );
          })}
        </group>
        <ContactShadows
          position={[0, -0.2, 0]}
          scale={175}
          blur={2.6}
          far={46}
          opacity={0.6}
          color="#05070c"
        />
        <OrbitControls
          enablePan={false}
          enableDamping
          dampingFactor={0.08}
          minDistance={48}
          maxDistance={170}
          minPolarAngle={0.25}
          maxPolarAngle={Math.PI / 2.25}
          autoRotate={!prefersReducedMotion}
          autoRotateSpeed={0.35}
          target={[0, 0, 0]}
        />
        <EffectComposer>
          <Bloom mipmapBlur luminanceThreshold={0.5} luminanceSmoothing={0.25} intensity={0.9} radius={0.72} />
        </EffectComposer>
      </Canvas>

      <div className="spainmap__legend mono" aria-hidden="true">
        <span><i style={{ background: VERDICT_COLOR.SELLADO }} />Sellado</span>
        <span><i style={{ background: VERDICT_COLOR.PARCIAL }} />Parcial</span>
        <span><i style={{ background: VERDICT_COLOR.GAP }} />Gap</span>
      </div>

      <div className="spainmap__hud" role="status" aria-live="polite">
        {hoveredShape ? (
          <>
            <span className="hud__prov">{hoveredShape.name}</span>
            <span className="hud__line">
              {cov && (
                <span className={`hud__badge hud__badge--${cov.verdict.toLowerCase()}`}>
                  {VERDICT_LABEL[cov.verdict]}
                </span>
              )}
              <span className="hud__cov mono">
                {cov?.coverage_pct != null ? `${cov.coverage_pct.toFixed(0)}%` : '—'}
              </span>
            </span>
            <span className="hud__meta mono">
              {cov ? `${cov.numerator} dealers servidos` : 'sin dato de cobertura'}
              {cov?.denominator != null ? ` · techo ${cov.denominator}` : ''}
            </span>
          </>
        ) : (
          <span className="hud__hint">Cobertura de venta — pasa el cursor o gira el mapa</span>
        )}
      </div>
    </div>
  );
}
