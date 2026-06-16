// Load the Spain provinces TopoJSON and project it to centered 2D world coordinates
// ready to be turned into Three.js extruded shapes. Join key: feature.id === INE
// province code ("01".."52") === geo_province.code === seal province_code.
import { feature } from 'topojson-client';
import { geoConicConformalSpain } from 'd3-composite-projections';

export interface Vec2 {
  x: number;
  y: number;
}

export interface ProvincePolygon {
  outer: Vec2[];
  holes: Vec2[][];
}

export interface ProvinceShape {
  code: string;
  name: string;
  polygons: ProvincePolygon[];
  centroid: Vec2;
}

const TOPO_URL = '/geo/es-provinces.topo.json';
const WORLD_W = 120; // target world width (Three units) the whole map fits into

// Minimal shapes for the slices of GeoJSON/TopoJSON we touch (avoids pulling
// topojson-specification types; we validate the join by id at runtime).
type Ring = [number, number][];
interface GeoFeature {
  id: string | number;
  properties: { name?: string } | null;
  geometry: { type: 'Polygon' | 'MultiPolygon'; coordinates: Ring[] | Ring[][] } | null;
}
interface FeatureCollection {
  features: GeoFeature[];
}
interface Topology {
  objects: Record<string, unknown>;
}

function ringsOf(geom: NonNullable<GeoFeature['geometry']>): Ring[][] {
  // Normalize to an array of polygons, each polygon = array of rings.
  if (geom.type === 'Polygon') return [geom.coordinates as Ring[]];
  return geom.coordinates as Ring[][];
}

export async function loadProvinceShapes(): Promise<ProvinceShape[]> {
  const res = await fetch(TOPO_URL);
  if (!res.ok) throw new Error(`failed to load ${TOPO_URL}: HTTP ${res.status}`);
  const topo = (await res.json()) as Topology;

  const fc = feature(
    topo as never,
    topo.objects.provinces as never,
  ) as unknown as FeatureCollection;

  const projection = geoConicConformalSpain();
  const height = Math.round(WORLD_W * 0.78);
  projection.fitSize([WORLD_W, height], fc as never);

  // Pass 1 — project every coordinate, remember bounds.
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;

  interface RawProvince {
    code: string;
    name: string;
    polygons: { outer: Vec2[]; holes: Vec2[][] }[];
  }
  const raw: RawProvince[] = [];

  const projectRing = (ring: Ring): Vec2[] => {
    const out: Vec2[] = [];
    for (const [lon, lat] of ring) {
      const p = projection([lon, lat]);
      if (!p) continue;
      const v = { x: p[0], y: p[1] };
      if (v.x < minX) minX = v.x;
      if (v.x > maxX) maxX = v.x;
      if (v.y < minY) minY = v.y;
      if (v.y > maxY) maxY = v.y;
      out.push(v);
    }
    return out;
  };

  for (const f of fc.features) {
    if (!f.geometry) continue;
    const polys = ringsOf(f.geometry).map((rings) => ({
      outer: projectRing(rings[0]),
      holes: rings.slice(1).map(projectRing),
    }));
    raw.push({
      code: String(f.id).padStart(2, '0'),
      name: f.properties?.name ?? String(f.id),
      polygons: polys,
    });
  }

  // Pass 2 — recenter to origin and flip Y so geographic north is +Y in shape space.
  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;
  const recenter = (v: Vec2): Vec2 => ({ x: v.x - cx, y: -(v.y - cy) });

  // GeoJSON rings are closed (last point == first) and may carry coincident vertices;
  // a zero-length closing segment breaks three.js Earcut ("reading 'next'"). Strip the
  // duplicate closing vertex, drop consecutive duplicates and any non-finite points.
  const EPS = 1e-6;
  const clean = (ring: Vec2[]): Vec2[] => {
    const out: Vec2[] = [];
    for (const v of ring) {
      if (!Number.isFinite(v.x) || !Number.isFinite(v.y)) continue;
      const last = out[out.length - 1];
      if (last && Math.abs(last.x - v.x) < EPS && Math.abs(last.y - v.y) < EPS) continue;
      out.push(v);
    }
    if (out.length > 1) {
      const f = out[0];
      const l = out[out.length - 1];
      if (Math.abs(f.x - l.x) < EPS && Math.abs(f.y - l.y) < EPS) out.pop();
    }
    return out;
  };

  return raw.map((p) => {
    const polygons = p.polygons
      .map((poly) => ({
        outer: clean(poly.outer.map(recenter)),
        holes: poly.holes.map((h) => clean(h.map(recenter))).filter((h) => h.length >= 3),
      }))
      .filter((poly) => poly.outer.length >= 3);
    // Centroid = mean of the largest polygon's outer ring (for labels / camera focus).
    const largest = polygons.reduce(
      (best, poly) => (poly.outer.length > best.outer.length ? poly : best),
      polygons[0] ?? { outer: [], holes: [] },
    );
    const centroid = largest.outer.reduce(
      (acc, v, _i, arr) => ({ x: acc.x + v.x / arr.length, y: acc.y + v.y / arr.length }),
      { x: 0, y: 0 },
    );
    return { code: p.code, name: p.name, polygons, centroid };
  });
}
