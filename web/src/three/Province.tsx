// One province rendered as an extruded "data crystal": height encodes seal coverage,
// color encodes the verdict. Hover lifts it and brightens its emission; when another
// province is hovered, the rest dim back so the focus reads clearly.
import { useMemo, useRef } from 'react';
import { BufferGeometry, Color, ExtrudeGeometry, Path, Shape, type Mesh, type MeshStandardMaterial } from 'three';
import { useFrame, type ThreeEvent } from '@react-three/fiber';
import type { ProvinceShape } from '../lib/geo';

interface ProvinceProps {
  shape: ProvinceShape;
  depth: number;
  color: string;
  hovered: boolean;
  dimmed: boolean;
  onHover: (code: string | null) => void;
  onSelect: (code: string) => void;
}

const LIFT = 5.5; // world-up offset (extrude axis) when hovered
const LERP = 0.16;

export function Province({ shape, depth, color, hovered, dimmed, onHover, onSelect }: ProvinceProps) {
  const meshRef = useRef<Mesh>(null);
  const matRef = useRef<MeshStandardMaterial>(null);

  const geometry = useMemo(() => {
    const shapes: Shape[] = [];
    for (const poly of shape.polygons) {
      if (poly.outer.length < 3) continue;
      const s = new Shape();
      s.moveTo(poly.outer[0].x, poly.outer[0].y);
      for (let i = 1; i < poly.outer.length; i++) s.lineTo(poly.outer[i].x, poly.outer[i].y);
      for (const hole of poly.holes) {
        if (hole.length < 3) continue;
        const path = new Path();
        path.moveTo(hole[0].x, hole[0].y);
        for (let i = 1; i < hole.length; i++) path.lineTo(hole[i].x, hole[i].y);
        s.holes.push(path);
      }
      shapes.push(s);
    }
    if (shapes.length === 0) return new BufferGeometry();
    try {
      const geo = new ExtrudeGeometry(shapes, { depth, bevelEnabled: false });
      geo.computeVertexNormals();
      return geo;
    } catch (err) {
      if (import.meta.env.DEV) {
        // One malformed province must not blank the whole map.
        console.warn(`[map] extrude failed for province ${shape.code}`, err);
      }
      return new BufferGeometry();
    }
  }, [shape, depth]);

  const baseColor = useMemo(() => new Color(color), [color]);

  useFrame(() => {
    const mesh = meshRef.current;
    const mat = matRef.current;
    // Lift along the extrude axis (local +Z → world +Y after the group's -90deg X rotation).
    if (mesh) mesh.position.z += ((hovered ? LIFT : 0) - mesh.position.z) * LERP;
    if (mat) {
      const targetEmissive = hovered ? 1.35 : 0.42;
      mat.emissiveIntensity += (targetEmissive - mat.emissiveIntensity) * LERP;
      const targetOpacity = dimmed && !hovered ? 0.34 : 1;
      mat.opacity += (targetOpacity - mat.opacity) * LERP;
    }
  });

  return (
    <mesh
      ref={meshRef}
      geometry={geometry}
      onPointerOver={(e: ThreeEvent<PointerEvent>) => {
        e.stopPropagation();
        onHover(shape.code);
      }}
      onPointerOut={(e: ThreeEvent<PointerEvent>) => {
        e.stopPropagation();
        onHover(null);
      }}
      onClick={(e: ThreeEvent<MouseEvent>) => {
        e.stopPropagation();
        onSelect(shape.code);
      }}
    >
      <meshStandardMaterial
        ref={matRef}
        color={baseColor}
        emissive={baseColor}
        emissiveIntensity={0.42}
        metalness={0.4}
        roughness={0.32}
        transparent
        opacity={1}
      />
    </mesh>
  );
}
