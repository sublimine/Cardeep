import { useEffect, useLayoutEffect, useMemo, useRef, useState, type RefObject } from 'react';
import { motion, useReducedMotion } from 'framer-motion';

import { BENTO } from '@landing/content/site';
import { SPAIN_DOTS, SPAIN_MARKERS } from './spain-map-dots';

/**
 * "Cobertura de España" — the market heat field.
 *
 * WHAT THE TWO PREVIOUS VERSIONS GOT WRONG, because it decides everything below.
 * The first painted all 1.969 dots the same translucent white and let sixteen
 * pins carry the message: that is a LOCATOR map — it says where the provinces
 * are, never how much is in them. The second tinted those same dots by density
 * and stopped there, which is why the verdict on it was "the same damn map with
 * more dots": a dot grid is still a dot grid however you colour it, and nothing
 * on it moved or answered the pointer.
 *
 * This is a continuous field instead — the thing a driver reads on a demand map
 * or a viewer reads on weather radar. Heat is summed as a gaussian over the
 * measured provinces, painted as a smooth surface, clipped to the coastline,
 * breathed slowly so it reads as alive rather than printed, and it resolves the
 * nearest province under the pointer anywhere on the map.
 *
 * WHAT IS REAL AND WHAT IS INTERPOLATED. `SPAIN_MARKERS` holds sixteen provinces
 * with counts measured against the live index. Those sixteen are the ONLY
 * quantities that exist. The field between them is interpolation and is labelled
 * as such on the card itself ("sobre N provincias medidas"); no number appears on
 * screen that was not measured, and the count in that sentence is derived from
 * the data so the copy can never drift from the array.
 */

/* -------------------------------------------------------------------------- */
/*                                 Heat field                                 */
/* -------------------------------------------------------------------------- */

/**
 * Resolution of the scalar field, in cells across the map square.
 *
 * The field is computed at this resolution and then drawn up to the canvas with
 * bilinear smoothing, which is what makes it CONTINUOUS rather than a grid of
 * tiles. 128 is not a compromise: a cell is 0.78 display units against a 4.1-unit
 * core kernel, so the narrowest gaussian in the mixture is still sampled five
 * times per standard deviation — well past the point where the upscale has
 * anything left to lose. Computing per device pixel instead would cost twenty
 * times more for a surface already band-limited far below this pitch.
 */
const FIELD_RES = 128;

/**
 * WHAT THE FIELD MEASURES, stated plainly because it decides the kernel: how much
 * indexed stock is within reach of a point, not how many dealers sit exactly on
 * it. That is a catchment, and it is why a spot ninety kilometres from Madrid is
 * warm — a dealer there competes in Madrid's market. The per-province COUNTS are
 * a different quantity and the markers carry them; the readout never reports the
 * field.
 *
 * Each province is therefore spread by TWO gaussians rather than one. Both are in
 * DATA units — the field inverts every cell back through the projection before
 * summing — so the kernel stays a real distance whatever the fit does to the
 * drawing. One unit is about ten kilometres:
 *   · a 40 km core, which is what makes Madrid, Barcelona and the Levante read as
 *     distinct cells rather than one smear;
 *   · a 90 km halo at 18% of the weight, which is what makes them a FIELD rather
 *     than sixteen circles.
 *
 * Both numbers were measured against the live canvas, not guessed. A single 75 km
 * kernel (what shipped before) put 57% of land pixels above 0.8 alpha — Teruel as
 * bright as Madrid, no contrast left. A single 45 km kernel fixed the contrast and
 * broke the map the other way: 26% of the country fell below 0.15 and Extremadura
 * and Castilla vanished into the black, which reads as "not covered" about
 * provinces the index simply has not measured separately. The mixture holds both
 * ends — 4% of land above 0.8, 2% below 0.15 — which is the histogram a radar
 * frame actually has.
 */
const CORE_SIGMA = 4;
const HALO_SIGMA = 9;
const HALO_WEIGHT = 0.18;
const TWO_CORE_SQ = 2 * CORE_SIGMA * CORE_SIGMA;
const TWO_HALO_SQ = 2 * HALO_SIGMA * HALO_SIGMA;

/**
 * Distance past which a province stops being summed at all, in data units.
 *
 * Not an approximation anyone has to take on faith: 34 units is 3.8 halo sigmas,
 * where the wider gaussian is down to 1.5·10⁻⁴. Against Madrid — the largest
 * weight in the country at 3.265 — the dropped term is 0.48 of a point of sale,
 * which after the log stretch is four thousandths of one step of a 256-entry
 * ramp. The cutoff is invisible and it removes roughly half the exponentials,
 * because at any cell most of the sixteen provinces are simply too far to matter.
 */
const KERNEL_CUTOFF_SQ = 34 * 34;

/**
 * The y below which the map is the peninsula and above which it is the Canary
 * INSET (peninsular dots stop at y 73.92; the inset starts at 91.08).
 *
 * Weight never crosses this line, and that is a correctness fix rather than a
 * refinement: an inset is a cartographic device, so the distance across it means
 * nothing. Left unguarded, Cádiz's 428 points of sale sat 21 units from the
 * islands and warmed them to 44% alpha — the map inventing a Canarian market out
 * of an Andalusian one. The index has measured no Canarian province, so the
 * islands correctly render at the cold floor and nothing else.
 */
const INSET_Y = 82;

/**
 * Display gamma applied after the log stretch.
 *
 * The log alone is not enough, and the reason is measurable. `log1p` over a
 * gaussian sum has almost no floor: any cell within reach of a city already sits
 * above 0.6 of the log maximum, so the normalised field came out with a median of
 * 0.82 and nothing to separate a real core from its surroundings. The log is
 * still right — it is what keeps Girona's 342 from collapsing into black against
 * Madrid's 3.265 — so it stays, and a gamma stretches the compressed midtones
 * back apart. Log stretch plus display gamma is the standard pairing wherever a
 * huge dynamic range has to survive an 8-bit ramp, radar and astronomy included.
 *
 * At 2.6 the land distribution measures p10 0.23 / p50 0.43 / p90 0.69, with 4% of
 * pixels above 0.8 and 88% in the readable middle: a few true cores over a country
 * that is present everywhere.
 */
const DISPLAY_GAMMA = 2.6;

/** How many provinces the index has actually measured. Read from the data, never typed by hand. */
const MEASURED = SPAIN_MARKERS.length;
const MAX_POINTS = Math.max(...SPAIN_MARKERS.map((m) => m.points));

/* -------------------------------------------------------------------------- */
/*                                 Projection                                 */
/* -------------------------------------------------------------------------- */

/**
 * Radius used to fatten the dot cloud into a solid silhouette, in data units.
 *
 * `SPAIN_DOTS` is a 1.32-unit lattice, so its diagonal neighbours sit 1.867 apart
 * and any radius at or above half of that — 0.934 — closes every interior hole
 * while still tracing the real coastline. 0.95 takes the nearest safe value.
 *
 * WHY THE DOTS AND NOT d3-geo. `d3-geo`, `d3-composite-projections` and
 * `topojson-client` are all installed and `geoConicConformalSpain` would be the
 * textbook way to draw this — but the repo ships no TopoJSON: the only match on
 * disk is `src/types/topojson-client.d.ts`, a type stub. Projecting real geometry
 * would therefore mean fetching a boundary file at runtime, i.e. a network
 * dependency and a loading state on a bento tile. These dots were themselves
 * generated from the real province TopoJSON (see the header of the data file), so
 * the silhouette they reconstruct is the same geometry, resolved offline and
 * deterministically. The Canary inset the composite projection would give us is
 * already baked into the dots too.
 */
const MASK_DOT_RADIUS = 0.95;

/**
 * Distance the Canary inset is pulled up, in data units.
 *
 * The generator parked the inset far below the peninsula: peninsular dots stop at
 * y 73.92 and the islands do not start again until 91.08, so seventeen units —
 * 17% of the box — are guaranteed empty. Since the square is fitted to its
 * height, that empty band was costing the whole map a sixth of its size for
 * nothing. Closing twelve of those units leaves a five-unit channel, still a
 * clear visual break between mainland and inset, which is all the convention
 * requires.
 */
const INSET_GAP = 12;

/** Data y → plotted y, with the inset lifted. */
function liftInset(y: number) {
  return y > INSET_Y ? y - INSET_GAP : y;
}

/**
 * The divider in PLOTTED space, derived rather than typed: halfway between the
 * peninsula's southern tip and the lifted inset's northern edge. Used to decide
 * which side of the break a field cell belongs to.
 */
const PLOTTED_DIVIDER = (() => {
  let peninsulaMax = -Infinity;
  let insetMin = Infinity;
  for (const [, y] of SPAIN_DOTS) {
    if (y > INSET_Y) insetMin = Math.min(insetMin, y - INSET_GAP);
    else peninsulaMax = Math.max(peninsulaMax, y);
  }
  return (peninsulaMax + insetMin) / 2;
})();

/**
 * Fit of the plotted content into the 0-100 square the canvas draws.
 *
 * The raw data leaves slack on every side — the box was never trimmed to Spain —
 * and combined with the closed inset gap, fitting recovers roughly a fifth of the
 * map's linear size at the same tile height. The scale is a single factor for
 * both axes, so the country is never stretched.
 */
const FIT = (() => {
  let x0 = Infinity;
  let x1 = -Infinity;
  let y0 = Infinity;
  let y1 = -Infinity;
  for (const [x, y] of SPAIN_DOTS) {
    const py = liftInset(y);
    if (x < x0) x0 = x;
    if (x > x1) x1 = x;
    if (py < y0) y0 = py;
    if (py > y1) y1 = py;
  }
  // Padded by the mask radius, or the fattened coastline would be clipped square.
  x0 -= MASK_DOT_RADIUS;
  x1 += MASK_DOT_RADIUS;
  y0 -= MASK_DOT_RADIUS;
  y1 += MASK_DOT_RADIUS;
  const scale = 100 / Math.max(x1 - x0, y1 - y0);
  return {
    scale,
    ox: (100 - (x1 - x0) * scale) / 2 - x0 * scale,
    oy: (100 - (y1 - y0) * scale) / 2 - y0 * scale,
  };
})();

/** Data coordinates → the 0-100 display square. */
function plotX(x: number) {
  return x * FIT.scale + FIT.ox;
}
function plotY(y: number) {
  return liftInset(y) * FIT.scale + FIT.oy;
}
/** …and back, so the field can be summed in real kilometres. */
function unplotX(x: number) {
  return (x - FIT.ox) / FIT.scale;
}
function unplotY(y: number) {
  return (y - FIT.oy) / FIT.scale;
}

/**
 * Where the northernmost land sits inside the square, as a fraction of it.
 *
 * The fit centres the country, so the square always opens with a strip of empty
 * sea before Galicia and the Cantabrian coast begin. The layout below spends that
 * strip instead of stacking its own margin on top of it — worth about 9% of the
 * map's size, which on this tile is thirty-odd pixels.
 */
const PLOTTED_TOP = (() => {
  let top = Infinity;
  for (const [, y] of SPAIN_DOTS) top = Math.min(top, plotY(y) - MASK_DOT_RADIUS * FIT.scale);
  return Math.max(0, top) / 100;
})();

/**
 * Right edge of the Canary inset inside the square, as a fraction of it.
 *
 * The collapsed readout sits in the same horizontal band as the islands, so the
 * layout needs to know where they end. Taken from the data with the mask radius
 * added, because the silhouette is drawn fattened by exactly that much.
 */
const INSET_RIGHT = (() => {
  let right = 0;
  for (const [x, y] of SPAIN_DOTS) {
    if (y > INSET_Y) right = Math.max(right, plotX(x) + MASK_DOT_RADIUS * FIT.scale);
  }
  return right / 100;
})();

/** Every measured province in display space, computed once and shared. */
const PLOTTED_MARKERS = SPAIN_MARKERS.map((marker) => ({
  marker,
  x: plotX(marker.x),
  y: plotY(marker.y),
}));

let fieldCache: Float32Array | null = null;
let shimmerCache: Float32Array | null = null;

/**
 * The static field: normalised heat per cell, in [0, 1].
 *
 * WHY THE SCALE IS COMPRESSED AT ALL, and why that is the most important
 * decision on this card. The real distribution is savage: Madrid holds 3.265
 * points of sale against Girona's 342, a factor of nearly ten between first and
 * sixteenth, and the unmeasured tail runs lower still. On a linear ramp Madrid
 * saturates and the rest of the country collapses into the same near-black, so
 * the map would say "there is Madrid, and there is nothing" — which is both ugly
 * and FALSE, because Girona holding 342 points of sale is a real, dense market.
 * The log keeps Madrid clearly first while leaving the country legible; the gamma
 * above puts back the contrast the log costs.
 *
 * 16.384 cells against 16 provinces at two gaussians each would be half a million
 * exponentials; the distance cutoff removes about half of them. It is paid once
 * for the lifetime of the tab and never again — the animation re-reads this array
 * instead of recomputing it, and the whole build is deferred until the card is
 * near the viewport (see BUILD_MARGIN).
 */
function heatField(): Float32Array {
  if (fieldCache) return fieldCache;

  const cells = new Float32Array(FIELD_RES * FIELD_RES);
  let max = 0;

  for (let j = 0; j < FIELD_RES; j++) {
    // Cells are addressed in DISPLAY space and inverted back to data, so the
    // kernel keeps working in real kilometres however the fit is tuned.
    const plotted = ((j + 0.5) / FIELD_RES) * 100;
    // Everything below the break is the Canary inset, and the index has measured
    // no province there, so it stays at zero — never warmed from the mainland.
    if (unplotY(plotted) > PLOTTED_DIVIDER) continue;
    const y = unplotY(plotted);
    for (let i = 0; i < FIELD_RES; i++) {
      const x = unplotX(((i + 0.5) / FIELD_RES) * 100);
      let heat = 0;
      for (const m of SPAIN_MARKERS) {
        const dx = x - m.x;
        const dy = y - m.y;
        const d2 = dx * dx + dy * dy;
        if (d2 > KERNEL_CUTOFF_SQ) continue;
        heat +=
          m.points *
          ((1 - HALO_WEIGHT) * Math.exp(-d2 / TWO_CORE_SQ) +
            HALO_WEIGHT * Math.exp(-d2 / TWO_HALO_SQ));
      }
      const value = Math.log1p(heat);
      cells[j * FIELD_RES + i] = value;
      if (value > max) max = value;
    }
  }

  const gains = new Float32Array(FIELD_RES * FIELD_RES);
  for (let k = 0; k < cells.length; k++) {
    const t = max > 0 ? Math.pow(cells[k] / max, DISPLAY_GAMMA) : 0;
    cells[k] = t;
    gains[k] = SHIMMER * 4 * t * (1 - t);
  }

  fieldCache = cells;
  shimmerCache = gains;
  return cells;
}

/** Per-cell shimmer amplitude, built with the field it belongs to. */
function shimmerGains(): Float32Array {
  if (!shimmerCache) heatField();
  return shimmerCache as Float32Array;
}

/* ------------------------------------------------------------------- ramp */

/**
 * The colour ramp: radar logic, ONE hue family.
 *
 * Weather radar encodes magnitude by walking green → yellow → red, which is a
 * second, third and fourth accent — exactly what this design system forbids. So
 * magnitude is carried by INTENSITY inside Cardeep's blue instead: the middle is
 * the brand at full chroma and the core runs up to a near-white blue, the way the
 * eye already reads "hot" on a dark ground. Nothing green, yellow or red enters,
 * and the map still reads as a radar because the gradient is continuous and the
 * peaks are the brightest thing on the card.
 *
 * The first stop is NOT transparent, and that is deliberate. Extremadura, Zamora
 * and the Canaries land at zero heat, and a transparent floor would delete them
 * from the map — a coverage map that dissolves the parts of the country it has
 * not measured is worse than no map. They keep a cold slate-blue so the coastline
 * is always whole, and every step of the ramp rises in luminance from there, so
 * brightness alone carries magnitude for anyone who cannot separate the hues.
 */
const RAMP_STOPS: readonly { at: number; rgb: readonly [number, number, number]; a: number }[] = [
  { at: 0.0, rgb: [96, 132, 190], a: 0.24 },
  { at: 0.22, rgb: [23, 96, 220], a: 0.36 },
  { at: 0.5, rgb: [18, 110, 253], a: 0.64 },
  { at: 0.76, rgb: [116, 172, 255], a: 0.85 },
  { at: 1.0, rgb: [216, 233, 255], a: 0.96 },
];

const RAMP_SIZE = 256;

function buildRamp(): Uint8ClampedArray {
  const lut = new Uint8ClampedArray(RAMP_SIZE * 4);
  for (let k = 0; k < RAMP_SIZE; k++) {
    const t = k / (RAMP_SIZE - 1);
    let hi = 1;
    while (hi < RAMP_STOPS.length - 1 && t > RAMP_STOPS[hi].at) hi++;
    const lo = RAMP_STOPS[hi - 1];
    const up = RAMP_STOPS[hi];
    const span = up.at - lo.at;
    const f = span > 0 ? (t - lo.at) / span : 0;
    const q = k * 4;
    lut[q] = lo.rgb[0] + (up.rgb[0] - lo.rgb[0]) * f;
    lut[q + 1] = lo.rgb[1] + (up.rgb[1] - lo.rgb[1]) * f;
    lut[q + 2] = lo.rgb[2] + (up.rgb[2] - lo.rgb[2]) * f;
    lut[q + 3] = (lo.a + (up.a - lo.a) * f) * 255;
  }
  return lut;
}

const RAMP = buildRamp();

/**
 * The legend's gradient, sampled from the very LUT the canvas paints with, so the
 * key can never drift from the map it explains. A heat map without a key is a
 * decoration, and a key that lies about its own map is worse than none.
 */
const RAMP_CSS = `linear-gradient(90deg, ${Array.from({ length: 9 }, (_, i) => {
  const t = i / 8;
  const q = Math.round(t * (RAMP_SIZE - 1)) * 4;
  return `rgba(${RAMP[q]},${RAMP[q + 1]},${RAMP[q + 2]},${(RAMP[q + 3] / 255).toFixed(3)}) ${(t * 100).toFixed(0)}%`;
}).join(', ')})`;

/* ------------------------------------------------------------------ mask */

/** Feathering of the coastline when the heat is clipped to land, in CSS px. */
const COAST_BLUR = 'blur(1.5px)';
/** Halo cast by the landmass onto the black card, in CSS px. */
const GLOW_BLUR = 20;
const GLOW_ALPHA = 0.2;
/**
 * A whisper of neutral under the coastline. The ramp's first stop already keeps
 * unmeasured land visible, so this is not carrying the silhouette any more — it
 * only stops the cold half of the map from being pure single-hue blue.
 */
const LAND_ALPHA = 0.04;

/* --------------------------------------------------------------- shimmer */

/**
 * Amplitude of the breathing modulation.
 *
 * The brief is "movimiento real, actual y vivo del mercado", so the field cannot
 * be a print. A slow travelling wave modulates each cell around its static heat.
 *
 * WHY THE AMPLITUDE IS SHAPED, AND NOT FLAT. A flat ±13% was measured doing real
 * damage: Madrid and Barcelona are only 10% apart at the top of the ramp, so with
 * the two cells in opposite phase the canvas rendered Barcelona brighter than
 * Madrid — the animation contradicting the data underneath it. The amplitude is
 * therefore weighted by 4·t·(1−t), a parabola that is zero at both ends of the
 * ramp and widest in the middle. The consequence is exact: the hottest cell in
 * the country cannot move at all, so first place is nailed down, while the wave
 * stays at full strength across the mid-field, which is most of the map and where
 * it actually reads. The weight depends only on the static field, so it is
 * precomputed once and costs one multiply per cell per frame.
 */
const SHIMMER = 0.13;
/** Below this, a cell is empty enough that modulating it would only cost cycles. */
const SHIMMER_FLOOR = 0.02;

/* -------------------------------------------------------------------------- */
/*                                  Geometry                                  */
/* -------------------------------------------------------------------------- */

type Geometry = { ox: number; oy: number; side: number };
type Box = { w: number; h: number };

/**
 * The header's height is MEASURED, not assumed, and that is a bug fix rather than
 * a nicety. A constant band was right at the tile's two wide sizes and wrong at
 * its narrowest: below about 340px the title and the scope line each wrap, the
 * header grows from 56px to 107px, and a fixed band put that text straight on top
 * of Galicia. Observing the header instead means the map is laid out under
 * whatever the type actually did, at any width, in any language.
 */
const HEADER_FALLBACK = 60;
const HEADER_GAP = 6;
const SIDE_MARGIN = 28;
const BOTTOM_MARGIN = 6;

/**
 * Below this width the full readout cannot sit anywhere on the card without
 * covering land, so it collapses to a single line. Measured, not chosen: at 388px
 * the four-line panel already reaches the coastal glow and the header clears the
 * Atlantic by three pixels; at 308px it covers the Almería coast outright
 * (alpha 201 where open sea reads 1). The threshold keys off width alone so it
 * cannot oscillate against the header height it influences.
 *
 * WHERE THIS STOPS BEING TRUE, stated rather than glossed. Counting land pixels
 * under the chip for all sixteen labels at every width gives zero from a 288px
 * card upward — that is a 320px viewport, this design's narrowest breakpoint. At
 * 268px only the widest label, "Pontevedra 343 puntos de venta" at 201px, still
 * crosses the easternmost Canary island, by 40 device pixels under translucent
 * glass; the other fifteen clear it. Buying those back would mean shrinking the
 * map from 208 to 184px at the size where it is already smallest, or truncating a
 * province's name, and both are worse than the thing they fix.
 */
const COMPACT_WIDTH = 400;

/**
 * The readout's own box, shared with the geometry below rather than living only
 * in its className — the map is positioned so as not to collide with it, so the
 * two cannot be allowed to drift apart.
 */
const READOUT_WIDTH = 176;
const READOUT_INSET = 16;
const READOUT_CLEARANCE = 4;
/**
 * Widest the collapsed readout ever gets, measured across all sixteen provinces
 * rather than estimated: "Pontevedra 343 puntos de venta" renders at 201px, and
 * nothing truncates at any tile width.
 */
const COMPACT_READOUT_WIDTH = 201;

/**
 * The fraction of the square the readout is allowed to reach back over.
 *
 * Measured off the plotted geometry, not guessed: on the shortest tile the panel's
 * top edge sits at 63% of the square's height, and the right-most land below that
 * line — the Almería coast — stops at x 62.3%. Anything from 64% out is open
 * Mediterranean, so 66% lets the panel sit in the sea corner with a margin
 * instead of forcing the map away from the middle of the card. The Canary inset
 * (x 5.1-25.5) is nowhere near it.
 */
const READOUT_LAND_CLEAR = 0.66;

/** Where the square sits if nothing else on the card objects: centred. */
const MAP_BIAS_X = 0.5;

/**
 * Placement of the map square.
 *
 * The horizontal rule is not taste. The readout is anchored bottom-RIGHT, so every
 * pixel the map moves right pushes more of it under the panel; the bias is capped
 * so the panel can only ever overlap the sea corner. On the wide tile the cap does
 * not bite at all and the map stays centred; on the narrow one-column tile it
 * pushes the map left until the panel's left edge lands exactly on the 66% line.
 */
function geometryFor({ w, h }: Box, headerBand: number, compact: boolean): Geometry {
  /* The square is bottom-anchored, so the constraint is on where its LAND starts,
   * not where its box starts: `oy + PLOTTED_TOP·side ≥ headerBand`, solved for
   * side. Reserving the header's height against the box instead would double-count
   * the sea the projection already leaves above Galicia. */
  const byHeight = (h - headerBand - BOTTOM_MARGIN) / (1 - PLOTTED_TOP);
  const side = Math.max(0, Math.min(w - SIDE_MARGIN, byHeight));
  const slack = Math.max(0, w - side);
  const centred = slack * MAP_BIAS_X;
  /* Each form of the readout is held off different land. The tall panel reaches
   * up into the latitudes of the Almería coast, so it is kept out past the 66%
   * line; the collapsed one sits low, where the only land is the Canary inset, so
   * it is kept east of the islands instead. Both are caps on how far right the
   * map may sit, never on its size. */
  const clear = compact
    ? w - READOUT_INSET - COMPACT_READOUT_WIDTH - side * INSET_RIGHT - READOUT_CLEARANCE
    : w - READOUT_INSET - READOUT_WIDTH - side * READOUT_LAND_CLEAR;
  return {
    side,
    ox: Math.max(0, Math.min(centred, Math.max(0, clear))),
    oy: Math.max(0, h - side - BOTTOM_MARGIN),
  };
}

/**
 * Element size in CSS px, tracked so the canvas can stay DPR-correct through
 * resizes.
 *
 * BORDER box, not content box, and the difference was a real bug: `contentRect`
 * excludes padding, so measuring the header — which carries `p-4` — reported 40px
 * for a block that occupies 72. The map was reserving 32px less than the text
 * actually took, and only escaped a collision because the fitted projection
 * happens to leave a margin at the top of its square.
 */
function useBox(ref: RefObject<HTMLElement>): Box {
  const [box, setBox] = useState<Box>({ w: 0, h: 0 });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry) return;
      const border = entry.borderBoxSize?.[0];
      const w = Math.round(border ? border.inlineSize : entry.contentRect.width);
      const h = Math.round(border ? border.blockSize : entry.contentRect.height);
      setBox((cur) => (cur.w === w && cur.h === h ? cur : { w, h }));
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [ref]);

  return box;
}

/* -------------------------------------------------------------------------- */
/*                                   Canvas                                   */
/* -------------------------------------------------------------------------- */

/** The offscreen buffers one size of the card needs. */
type Buffers = {
  field: HTMLCanvasElement;
  fieldCtx: CanvasRenderingContext2D;
  image: ImageData;
  mask: HTMLCanvasElement;
  backdrop: HTMLCanvasElement;
};

/**
 * Builds the three buffers for a given size:
 *   · `field`   — FIELD_RES², repainted every frame and drawn up with smoothing.
 *   · `mask`    — the landmass as pure alpha, used to CLIP the heat so the
 *                 gaussian tails never bleed into the Atlantic.
 *   · `backdrop`— the cold country plus its halo, composited underneath.
 *
 * The mask and the backdrop are built at CSS resolution rather than device
 * resolution: both are blurred on use, so the extra pixels would buy nothing and
 * cost four times the memory on a retina panel. The visible canvas IS
 * device-resolution — that one has crisp gradients to lose.
 */
function buildBuffers(geo: Geometry, box: Box): Buffers | null {
  const { w, h } = box;

  const field = document.createElement('canvas');
  field.width = FIELD_RES;
  field.height = FIELD_RES;
  const fieldCtx = field.getContext('2d');
  if (!fieldCtx) return null;

  /* ------------------------------------------------------------ landmass */
  const mask = document.createElement('canvas');
  mask.width = w;
  mask.height = h;
  const maskCtx = mask.getContext('2d');
  if (!maskCtx) return null;
  maskCtx.fillStyle = '#fff';
  maskCtx.beginPath();
  const r = ((MASK_DOT_RADIUS * FIT.scale) / 100) * geo.side;
  for (const [x, y] of SPAIN_DOTS) {
    const cx = geo.ox + (plotX(x) / 100) * geo.side;
    const cy = geo.oy + (plotY(y) / 100) * geo.side;
    /* `moveTo` before each arc, or consecutive circles get joined by a chord.
     * One path with 1.969 subpaths and a single fill, not 1.969 fills. */
    maskCtx.moveTo(cx + r, cy);
    maskCtx.arc(cx, cy, r, 0, Math.PI * 2);
  }
  maskCtx.fill();

  /* ------------------------------------------------------------ backdrop */
  const backdrop = document.createElement('canvas');
  backdrop.width = w;
  backdrop.height = h;
  const backCtx = backdrop.getContext('2d');
  if (!backCtx) return null;
  /* Blur the silhouette, then repaint it brand-blue through `source-in`, which
   * keeps the blurred alpha and replaces only the colour. That single pass
   * gives both the halo spilling onto the black card and the faint blue floor
   * inside the coastline. */
  backCtx.filter = `blur(${GLOW_BLUR}px)`;
  backCtx.globalAlpha = GLOW_ALPHA;
  backCtx.drawImage(mask, 0, 0);
  backCtx.filter = 'none';
  backCtx.globalAlpha = 1;
  backCtx.globalCompositeOperation = 'source-in';
  backCtx.fillStyle = 'rgb(18,110,253)';
  backCtx.fillRect(0, 0, w, h);
  backCtx.globalCompositeOperation = 'source-over';
  backCtx.globalAlpha = LAND_ALPHA;
  backCtx.drawImage(mask, 0, 0);
  backCtx.globalAlpha = 1;

  return { field, fieldCtx, image: fieldCtx.createImageData(FIELD_RES, FIELD_RES), mask, backdrop };
}

/**
 * How early the surface is built, in CSS px of scroll distance.
 *
 * NOTHING is computed until the card comes within this margin of the viewport.
 * Building eagerly on mount was measured at 40-70ms of main thread in one block —
 * the field is 16.384 cells against 16 provinces at two gaussians each — which is
 * a long task, and it was landing in whatever else the page was doing at the time.
 *
 * 400px is chosen to guarantee the surface is finished BEFORE it is seen rather
 * than to push the work as late as possible, and the honest consequence is that
 * on a tall viewport where the tile sits just under the fold it still builds
 * during load. What the deferral buys there is ordering, not absence. With the
 * cutoff above, a cold build now reaches first paint in about 110ms spread across
 * frames, with no single task crossing the 50ms long-task threshold, and the loop
 * afterwards holds 60fps.
 */
const BUILD_MARGIN = '400px';

function HeatFieldCanvas({ geo, box, reduced }: { geo: Geometry; box: Box; reduced: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  /* LAYOUT effect, deliberately. The bento row's height is not stable — the
   * movements card beside this one runs an animated list, and its growth restates
   * the row from 382 to 440px and back every few seconds. With a passive effect
   * the canvas kept its old backing store for one frame after each of those, and
   * `h-full` stretched the map 15% vertically for that frame. Running before paint
   * removes the stretched frame entirely; the expensive build is still deferred to
   * the observer below, so nothing heavy moved into the layout phase. */
  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || geo.side <= 0 || box.w <= 0 || box.h <= 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    /* Capped at 2: beyond that the field is oversampled anyway and the fill rate
     * on a 3x panel is spent for nothing the eye can resolve. */
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const { w, h } = box;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);

    let buffers: Buffers | null = null;

    /* Separable trig tables. The wave is sin(ax+t)+sin(by-t)+sin(c(x+y)+t); the
     * third term is expanded with sin(a+b) so every trig call depends on one
     * axis only. That is 6·128 calls per frame instead of 3·16.384 — the same
     * picture for a fiftieth of the transcendental work. */
    const sx = new Float32Array(FIELD_RES);
    const sy = new Float32Array(FIELD_RES);
    const sinA = new Float32Array(FIELD_RES);
    const cosA = new Float32Array(FIELD_RES);
    const sinB = new Float32Array(FIELD_RES);
    const cosB = new Float32Array(FIELD_RES);

    const paintField = (buf: Buffers, cells: Float32Array, gains: Float32Array, time: number) => {
      const { fieldCtx, image } = buf;
      for (let i = 0; i < FIELD_RES; i++) {
        const x = ((i + 0.5) / FIELD_RES) * 100;
        const y = x; // the field is square, so the axis samples coincide
        sx[i] = Math.sin(x * 0.09 + time * 0.55);
        sy[i] = Math.sin(y * 0.11 - time * 0.4);
        const a = x * 0.06 + time * 0.85;
        sinA[i] = Math.sin(a);
        cosA[i] = Math.cos(a);
        const b = y * 0.06;
        sinB[i] = Math.sin(b);
        cosB[i] = Math.cos(b);
      }

      const data = image.data;
      let p = 0;
      for (let j = 0; j < FIELD_RES; j++) {
        const row = j * FIELD_RES;
        const syj = sy[j];
        const sbj = sinB[j];
        const cbj = cosB[j];
        for (let i = 0; i < FIELD_RES; i++) {
          const base = cells[row + i];
          let t = base;
          if (base > SHIMMER_FLOOR) {
            const wave = 0.5 * sx[i] + 0.3 * syj + 0.2 * (sinA[i] * cbj + cosA[i] * sbj);
            t = base * (1 + gains[row + i] * wave);
            if (t < 0) t = 0;
            else if (t > 1) t = 1;
          }
          const q = ((t * (RAMP_SIZE - 1)) | 0) * 4;
          data[p++] = RAMP[q];
          data[p++] = RAMP[q + 1];
          data[p++] = RAMP[q + 2];
          data[p++] = RAMP[q + 3];
        }
      }
      fieldCtx.putImageData(image, 0, 0);
    };

    const composite = (buf: Buffers) => {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0, 0, w, h);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';
      /* The upscale IS the interpolation: the browser resamples 128² cells onto
       * the device grid, which is what turns a lattice of values into a
       * continuous surface. */
      ctx.drawImage(buf.field, geo.ox, geo.oy, geo.side, geo.side);
      ctx.globalCompositeOperation = 'destination-in';
      ctx.filter = COAST_BLUR;
      ctx.drawImage(buf.mask, 0, 0, w, h);
      ctx.filter = 'none';
      ctx.globalCompositeOperation = 'destination-over';
      ctx.drawImage(buf.backdrop, 0, 0, w, h);
      ctx.globalCompositeOperation = 'source-over';
    };

    const render = (time: number) => {
      if (!buffers) buffers = buildBuffers(geo, box);
      if (!buffers) return;
      paintField(buffers, heatField(), shimmerGains(), time);
      composite(buffers);
    };

    /* The loop is gated on visibility, and so is the build above it. A card three
     * screens down has no business holding a frame budget — nor a slice of the
     * page's first render. */
    const started = performance.now();
    let raf = 0;
    let running = false;
    const frame = (now: number) => {
      if (!running) return;
      render((now - started) / 1000);
      raf = requestAnimationFrame(frame);
    };
    const start = () => {
      if (running) return;
      running = true;
      raf = requestAnimationFrame(frame);
    };
    const stop = () => {
      running = false;
      cancelAnimationFrame(raf);
    };

    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries[0]?.isIntersecting) {
          stop();
          return;
        }
        /* Reduced motion still gets the whole picture, just once and still. The
         * preference removes the movement, never the information. */
        if (reduced) {
          render(0);
          observer.disconnect();
          return;
        }
        start();
      },
      { rootMargin: BUILD_MARGIN },
    );
    observer.observe(canvas);

    return () => {
      observer.disconnect();
      stop();
    };
  }, [geo.ox, geo.oy, geo.side, box.w, box.h, reduced]);

  /* Sized in CSS px from the SAME state the backing store is built from, never
   * stretched with `inset-0 h-full`. The row's height moves under this card while
   * a neighbour animates, and a ResizeObserver's setState reaches the DOM a frame
   * after the layout it describes — even from a layout effect, because React
   * schedules the re-render rather than applying it inline. Stretched to fit, that
   * lag showed as a 20% vertically squashed Spain for sixteen frames out of six
   * hundred. Sized explicitly, the same lag can only leave a few unpainted pixels
   * at the edge of a card that is already black there. */
  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="pointer-events-none absolute top-0 left-0 block"
      style={{ width: box.w, height: box.h }}
    />
  );
}

/* -------------------------------------------------------------------------- */
/*                                  Markers                                   */
/* -------------------------------------------------------------------------- */

type Marker = (typeof SPAIN_MARKERS)[number];

const MARKER_MIN = 6;
const MARKER_RANGE = 9;

/** Square-root scale, so a marker's AREA tracks its count rather than its width. */
function markerSize(points: number) {
  return MARKER_MIN + Math.sqrt(points / MAX_POINTS) * MARKER_RANGE;
}

/**
 * One measured province, as an anchor on the field.
 *
 * Hollow, not solid: sixteen filled dots over a glowing surface fight it for
 * attention and win, which flattens the very reading they are supposed to
 * annotate. A thin bright ring with a dark halo underneath stays legible over
 * both the black card and the hottest core without hiding either.
 *
 * The old version gave the largest marker the full brand and a bloom while the
 * rest took the soft blue. That distinction is gone because the field now makes
 * it: Madrid is the brightest thing on the map by construction, and marking it
 * twice would be the map arguing with itself.
 */
function ProvinceMarker({
  plotted,
  index,
  active,
  onFocus,
  onBlur,
}: {
  plotted: (typeof PLOTTED_MARKERS)[number];
  index: number;
  active: boolean;
  onFocus: () => void;
  onBlur: () => void;
}) {
  const reduced = useReducedMotion();
  const { marker } = plotted;
  const size = markerSize(marker.points);

  return (
    <motion.button
      type="button"
      aria-label={`${marker.name}: ${marker.points.toLocaleString('es-ES')} puntos de venta`}
      onFocus={onFocus}
      onBlur={onBlur}
      className="absolute cursor-pointer rounded-full outline-none focus-visible:ring-2 focus-visible:ring-white/70"
      style={{
        left: `${plotted.x}%`,
        top: `${plotted.y}%`,
        width: size,
        height: size,
        marginLeft: -size / 2,
        marginTop: -size / 2,
      }}
      initial={reduced ? false : { scale: 0, opacity: 0 }}
      whileInView={{ scale: 1, opacity: 1 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.45, delay: index * 0.04, ease: [0.16, 1, 0.3, 1] }}
    >
      <span
        className="absolute inset-0 rounded-full"
        style={{
          border: '1px solid rgba(223,238,255,0.82)',
          background:
            'radial-gradient(circle, rgba(223,238,255,0.5) 0%, rgba(18,110,253,0.05) 68%)',
          boxShadow: active
            ? '0 0 0 1px rgba(18,110,253,0.75), 0 0 18px 4px rgba(18,110,253,0.5)'
            : '0 0 8px 2px rgba(2,8,20,0.65)',
          transform: active ? 'scale(1.3)' : 'scale(1)',
          transition: 'transform 220ms cubic-bezier(0.16,1,0.3,1), box-shadow 220ms linear',
        }}
      />
      {/* The halo runs on the resolved province only. A permanent pulse on sixteen
        * markers is sixteen things asking for attention at once, which is how a
        * reading turns into wallpaper. */}
      {active && !reduced && (
        <motion.span
          aria-hidden="true"
          className="absolute inset-0 rounded-full"
          style={{ border: '1px solid rgba(138,185,253,0.9)' }}
          animate={{ scale: [1, 2.6], opacity: [0.75, 0] }}
          transition={{ duration: 1.6, repeat: Infinity, ease: 'easeOut' }}
        />
      )}
    </motion.button>
  );
}

/* -------------------------------------------------------------------------- */
/*                                  Readout                                   */
/* -------------------------------------------------------------------------- */

/** Rank is counted, not assumed from the array's order, so a reordered dataset stays honest. */
function rankOf(marker: Marker) {
  return SPAIN_MARKERS.filter((m) => m.points > marker.points).length + 1;
}

/**
 * The value panel.
 *
 * It always holds a real province — at rest, the densest one — so the card never
 * shows an empty socket waiting for a hover, and a reader who never touches it
 * still leaves with a fact. Moving the pointer swaps which fact.
 */
function CoverageReadout({ marker, compact }: { marker: Marker; compact: boolean }) {
  const share = marker.points / MAX_POINTS;

  /* The collapsed form. It drops the rank and the bar, not the two things that
   * matter — which province and how many points of sale — and it is short enough
   * to sit in the strip below the peninsula, clear of both the mainland and the
   * Canary inset, on a tile too narrow to hold the full panel anywhere. */
  if (compact) {
    return (
      <div
        /* The arbitrary value needs underscores: `calc(100%-32px)` is not a
         * subtraction, it is one unparseable token, and Tailwind emits nothing at
         * all for it — the class was silently absent from the compiled sheet
         * until this was checked against the build. */
        className="glass-chip-dark pointer-events-none absolute z-30 flex max-w-[calc(100%_-_32px)] items-baseline gap-1.5 rounded-lg px-2.5 py-1.5"
        style={{ right: READOUT_INSET, bottom: READOUT_INSET }}
      >
        <span className="truncate text-[12px] leading-tight font-medium text-white">
          {marker.name}
        </span>
        <span className="text-brand-soft shrink-0 text-[11px] leading-tight tabular-nums">
          {marker.points.toLocaleString('es-ES')} puntos de venta
        </span>
      </div>
    );
  }

  return (
    <div
      className="glass-chip-dark pointer-events-none absolute z-30 rounded-xl px-3 py-2.5"
      style={{ right: READOUT_INSET, bottom: READOUT_INSET, width: READOUT_WIDTH }}
    >
      <p className="font-mono text-[9.5px] tracking-[0.12em] text-white/45 uppercase">
        N.º {rankOf(marker)} de {MEASURED} medidas
      </p>
      <p className="mt-1 text-[14px] leading-tight font-medium text-white">{marker.name}</p>
      <p className="text-brand-soft mt-0.5 text-[11.5px] leading-tight tabular-nums">
        {marker.points.toLocaleString('es-ES')} puntos de venta
      </p>
      {/* Scaled on the X axis rather than sized in pixels: width is a layout
        * property and animating it would relayout the panel every frame. */}
      <div className="mt-2 h-[3px] w-full overflow-hidden rounded-full bg-white/12">
        <div
          className="h-full w-full origin-left rounded-full transition-transform duration-300 ease-out"
          style={{
            transform: `scaleX(${share})`,
            background: 'linear-gradient(90deg, rgba(18,110,253,0.9), rgba(216,233,255,0.95))',
          }}
        />
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

/** The province the panel rests on when nothing is being pointed at. */
const DEFAULT_MARKER = SPAIN_MARKERS.reduce((a, b) => (b.points > a.points ? b : a));

/** Nearest measured province to a point given in map-square percentages. */
function nearestMarker(vx: number, vy: number): Marker {
  let best = PLOTTED_MARKERS[0];
  let bestDistance = Infinity;
  for (const p of PLOTTED_MARKERS) {
    const dx = p.x - vx;
    const dy = p.y - vy;
    const d = dx * dx + dy * dy;
    if (d < bestDistance) {
      bestDistance = d;
      best = p;
    }
  }
  return best.marker;
}

export function HostingMapCard() {
  const shellRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const box = useBox(shellRef);
  const header = useBox(headerRef);
  const reduced = useReducedMotion() ?? false;

  const compact = box.w > 0 && box.w < COMPACT_WIDTH;
  const headerBand = (header.h > 0 ? header.h : HEADER_FALLBACK) + HEADER_GAP;
  const geo = useMemo(
    () => geometryFor(box, headerBand, compact),
    [box, headerBand, compact],
  );

  const [activeName, setActiveName] = useState<string | null>(null);
  const active = SPAIN_MARKERS.find((m) => m.name === activeName) ?? DEFAULT_MARKER;

  return (
    <div
      id="cobertura"
      ref={shellRef}
      className="bg-natural-black relative col-span-1 min-h-(--box-min-height) overflow-hidden rounded-2xl lg:col-span-3"
    >
      {/* Ambient light in the corner, kept BEHIND the field so it lifts the black
        * card without washing the heat out. */}
      <svg
        className="pointer-events-none absolute -top-24 -left-72 z-0 rotate-45 fill-white/45 blur-3xl"
        width="100%"
        height="100%"
        aria-hidden="true"
      >
        <ellipse cx="50%" cy="50%" rx="90" ry="55" />
      </svg>

      <HeatFieldCanvas geo={geo} box={box} reduced={reduced} />

      {/* The interactive surface is exactly the map square, so the readout and the
        * header never steal the pointer and "nearest province" always means
        * nearest to a point that is actually on the map. */}
      {geo.side > 0 && (
        <div
          className="absolute z-20"
          style={{ left: geo.ox, top: geo.oy, width: geo.side, height: geo.side }}
          onPointerMove={(event) => {
            const rect = event.currentTarget.getBoundingClientRect();
            if (rect.width <= 0) return;
            const vx = ((event.clientX - rect.left) / rect.width) * 100;
            const vy = ((event.clientY - rect.top) / rect.height) * 100;
            const next = nearestMarker(vx, vy);
            setActiveName((cur) => (cur === next.name ? cur : next.name));
          }}
          onPointerLeave={() => setActiveName(null)}
        >
          {PLOTTED_MARKERS.map((plotted, index) => (
            <ProvinceMarker
              key={plotted.marker.name}
              plotted={plotted}
              index={index}
              active={active.name === plotted.marker.name}
              onFocus={() => setActiveName(plotted.marker.name)}
              onBlur={() => setActiveName(null)}
            />
          ))}
        </div>
      )}

      <div
        ref={headerRef}
        className="pointer-events-none relative z-30 flex items-start justify-between gap-3 p-4"
      >
        <div className="min-w-0">
          <h2 className="text-base font-medium text-white">{BENTO.coverage.title}</h2>
          {/* The scope disclosure, and it is not decoration: the field between the
            * markers is interpolation, and the card says so in the same breath as
            * it shows it. The count comes from the data, so this sentence cannot
            * outlive the array it describes — and the short form keeps the claim
            * when the tile is too narrow for the sentence. */}
          <p className="mt-0.5 text-[11px] leading-tight text-white/45">
            {compact
              ? `${MEASURED} provincias medidas`
              : `Intensidad de mercado sobre ${MEASURED} provincias medidas`}
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-1.5 pt-0.5">
          <span className="text-[10px] text-white/40">menos</span>
          <span className="h-1.5 w-14 rounded-full" style={{ background: RAMP_CSS }} />
          <span className="text-[10px] text-white/40">más</span>
        </div>
      </div>

      <CoverageReadout marker={active} compact={compact} />
    </div>
  );
}
