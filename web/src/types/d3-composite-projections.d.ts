// Minimal ambient types for d3-composite-projections (no official @types package).
// We only use geoConicConformalSpain — the Spain conic-conformal projection that
// also insets the Canary Islands, so the choropleth reads as a single compact map.
declare module 'd3-composite-projections' {
  import type { GeoProjection } from 'd3-geo';
  export function geoConicConformalSpain(): GeoProjection;
}
