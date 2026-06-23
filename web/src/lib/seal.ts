// Seal coverage per province, derived ONLY from the live API (/geo/seal). The static snapshot
// fallback was removed: a frozen JSON drifted from the live seal and painted wrong verdicts.
import type { GeoSeal, SealVerdict } from '../api/types';

export type Segment = 'venta' | 'desguace';

export interface ProvinceCoverage {
  coverage_pct: number | null;
  verdict: SealVerdict;
  numerator: number;
  denominator: number | null;
}

export type SealMap = Record<string, ProvinceCoverage>;

// Build a code→coverage map for one segment from the live GeoSeal envelope.
export function sealMapFromLive(seal: GeoSeal, segment: Segment): SealMap {
  const seg = seal.segments[segment];
  const out: SealMap = {};
  if (!seg) return out;
  for (const p of seg.provinces) {
    out[p.province_code] = {
      coverage_pct: p.coverage_pct,
      verdict: p.verdict,
      numerator: p.numerator,
      denominator: p.denominator,
    };
  }
  return out;
}
