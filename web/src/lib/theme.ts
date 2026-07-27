/**
 * One brand accent drives structure everywhere; green/rose/amber carry meaning
 * (trend up/down/warn) only — no per-page rainbow of near-identical blues.
 * Kept as literal hex — not `var(--c-*)` — because call sites need the
 * `${hex}NN`-style alpha-suffix trick, which only works on hex strings.
 * Values mirror tokens.css 1:1 (--c-violet/--c-emerald/--c-rose/--c-amber).
 */
export const ACCENT = '#3b82f6'
export const GOOD = '#059669'
export const BAD = '#e11d48'
export const WARN = '#d97706'
