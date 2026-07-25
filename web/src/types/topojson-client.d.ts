// @types/topojson-client imports from "topojson-specification", which was
// unpublished from npm in 2023 (verified: npm 404) — no way to install it.
// Minimal local shim covering only what CoverageMap.tsx actually calls.
declare module 'topojson-client' {
  import type { Feature, FeatureCollection, GeoJsonProperties, Geometry } from 'geojson';

  export interface TopologyObject {
    type: 'GeometryCollection';
    geometries: Array<{
      type: string;
      id?: string | number;
      properties?: GeoJsonProperties;
      arcs: unknown;
    }>;
  }

  export interface Topology {
    type: 'Topology';
    objects: Record<string, TopologyObject>;
    arcs: number[][][];
    transform?: { scale: [number, number]; translate: [number, number] };
  }

  export function feature(
    topology: Topology,
    object: TopologyObject,
  ): FeatureCollection<Geometry, GeoJsonProperties> & { features: Array<Feature & { id?: string | number }> };
}
