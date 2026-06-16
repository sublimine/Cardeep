// Seal coverage per province, from the live API (/geo/seal) or the static snapshot
// (public/geo/seal-snapshot.json) so the map is alive even when the API is offline.
import type { GeoSeal, SealVerdict } from '../api/types';

export type Segment = 'venta' | 'desguace';

export interface ProvinceCoverage {
  coverage_pct: number | null;
  verdict: SealVerdict;
  numerator: number;
  denominator: number | null;
}

export type SealMap = Record<string, ProvinceCoverage>;

// Shape of public/geo/seal-snapshot.json (generated from v_province_seal).
interface SnapshotShape {
  segments?: Record<string, Record<string, ProvinceCoverage>>;
}

const SNAPSHOT_URL = '/geo/seal-snapshot.json';

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

export async function loadSealSnapshot(segment: Segment): Promise<SealMap> {
  const res = await fetch(SNAPSHOT_URL);
  if (!res.ok) throw new Error(`seal snapshot HTTP ${res.status}`);
  const snap = (await res.json()) as SnapshotShape;
  return snap.segments?.[segment] ?? {};
}
