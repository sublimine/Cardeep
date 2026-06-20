// Display projection of the national MSE exhaustiveness certificate (/geo/exhaustiveness).
// Pure + presentational: collapses the raw cert (fractions 0..1, nullable fields) into ready-to-render
// strings. Honest by construction — a missing national cert (no build yet, or a too-thin stratum)
// returns { hasData: false }, so the UI states "pendiente" instead of fabricating a number.
import type { Exhaustiveness, ExhaustivenessCert } from '../api/types';

export interface CertView {
  hasData: boolean;
  coverageLowerPct: string | null; // conservative floor, e.g. "79.1"
  coveragePointPct: string | null; // point estimate, e.g. "84.6"
  ciBand: string | null; // N̂ confidence band, e.g. "1.847 – 2.013"
  kLists: number | null;
  nObs: number | null;
  sealed: boolean;
  method: string | null;
}

const EMPTY: CertView = {
  hasData: false,
  coverageLowerPct: null,
  coveragePointPct: null,
  ciBand: null,
  kLists: null,
  nObs: null,
  sealed: false,
  method: null,
};

function pct(fraction: number | null): string | null {
  return fraction === null ? null : (fraction * 100).toFixed(1);
}

function band(low: number | null, high: number | null): string | null {
  if (low === null || high === null) return null;
  const fmt = (n: number) => Math.round(n).toLocaleString('es-ES');
  return `${fmt(low)} – ${fmt(high)}`;
}

// Project the grand-national headline certificate (the segment-null + province-null row).
export function certView(ex: Exhaustiveness | undefined): CertView {
  const c: ExhaustivenessCert | null | undefined = ex?.national;
  if (!c) return EMPTY;
  return {
    hasData: true,
    coverageLowerPct: pct(c.coverage_lower),
    coveragePointPct: pct(c.coverage_point),
    ciBand: band(c.ci_low, c.ci_high),
    kLists: c.k_lists,
    nObs: c.n_obs,
    sealed: c.sealed,
    method: c.method,
  };
}
