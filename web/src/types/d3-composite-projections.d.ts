// No @types package exists for d3-composite-projections (verified: npm 404).
// Minimal ambient declaration — only the one export CoverageMap actually uses.
declare module 'd3-composite-projections' {
  import type { GeoProjection } from 'd3-geo';

  export function geoConicConformalSpain(): GeoProjection;
}
