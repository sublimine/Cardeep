// Verdict → color for the 3D map. Mirrors the seal ramp in styles/tokens.css
// (Three.js needs hex literals, it can't read CSS custom properties).
import type { SealVerdict } from '../api/types';

export const VERDICT_COLOR: Record<SealVerdict, string> = {
  SELLADO: '#3b82f6', // --accent (cardeep Cobalt Blue) — sealed coverage (>=85%)
  PARCIAL: '#f5b33c', // --price-fair — partial (50-85%)
  GAP: '#f0556b', // --price-high — gap (<50%)
  NO_DENOM: '#5d6a8c', // --text-3 — no registral denominator to measure against
};

// A province present on the map but with no seal datum for the active segment.
export const NO_DATA_COLOR = '#1a2440';

export function verdictColor(verdict: SealVerdict | undefined): string {
  return verdict ? VERDICT_COLOR[verdict] : NO_DATA_COLOR;
}
