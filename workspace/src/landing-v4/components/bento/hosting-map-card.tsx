import { useMemo, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';

import { BENTO } from '@landing/content/site';
import { SPAIN_DOTS, SPAIN_MARKERS } from './spain-map-dots';

/**
 * The map and the marker layer share one square box, so a marker's `[x, y]`
 * always lands on the dots it belongs to whatever the card ends up measuring.
 * Both boxes being square is also why `slice` never crops or stretches Spain.
 */
const MAP_BOX =
  'absolute top-1/2 left-1/2 aspect-square h-full -translate-x-1/2 -translate-y-1/2';

const MAP_DOT_RADIUS = 0.28;

/**
 * Falloff of one province's influence over the dot field, in viewBox units.
 *
 * Spain spans about ninety units here, so 7.5 spreads a province's weight across
 * roughly its own footprint and a little of its neighbours' — enough for adjacent
 * hot provinces to merge into one region (Madrid does not float alone; Barcelona
 * bleeds down the coast toward Tarragona) without smearing the whole peninsula
 * into a single wash.
 */
const SIGMA = 7.5;
const TWO_SIGMA_SQ = 2 * SIGMA * SIGMA;

/**
 * WHY THE SCALE IS LOGARITHMIC, and why that is the single most important
 * decision on this card.
 *
 * The real distribution is savage: Madrid holds 3.265 points of sale, Girona 342
 * — a factor of nearly ten between first and sixteenth, and the tail below them
 * is longer still. On a linear ramp Madrid saturates and everything else collapses
 * into the same near-black, so the map would say "there is Madrid, and there is
 * nothing", which is both ugly and FALSE: Girona holding 342 points of sale is a
 * real, dense market. A log scale keeps Madrid clearly first while leaving the
 * rest of the country legible, which is what a coverage map is for.
 */
function ramp(t: number) {
  /* One accent, three stops: an unlit dot is the same translucent white the map
   * has always used, and heat moves it through the soft brand blue to the full
   * one. No second hue enters — density is intensity here, not a rainbow. */
  const stops = [
    { at: 0, c: [255, 255, 255], a: 0.16 },
    { at: 0.55, c: [138, 185, 253], a: 0.55 },
    { at: 1, c: [18, 110, 253], a: 1 },
  ];
  const hi = stops.findIndex((s) => t <= s.at);
  if (hi <= 0) return `rgba(255,255,255,0.16)`;
  const lo = stops[hi - 1];
  const up = stops[hi];
  const k = (t - lo.at) / (up.at - lo.at);
  const mix = (i: number) => Math.round(lo.c[i] + (up.c[i] - lo.c[i]) * k);
  const alpha = (lo.a + (up.a - lo.a) * k).toFixed(3);
  return `rgba(${mix(0)},${mix(1)},${mix(2)},${alpha})`;
}

/**
 * The dot field, coloured by how much of the index sits near each dot.
 *
 * What this replaces painted all 1.969 dots the same translucent white and let
 * sixteen pins carry the whole message. That is a locator map, not a coverage
 * map: it says WHERE the provinces are, never how much is in them. Weighting the
 * field itself turns the country into the readout — the shape of the market shows
 * up in the ground, and the pins become labels on it rather than the data.
 *
 * Computed once. 1.969 dots against 16 provinces is 31.504 distance evaluations,
 * which costs well under a millisecond and never runs again.
 */
function DensityField() {
  const dots = useMemo(() => {
    const raw = SPAIN_DOTS.map(([x, y]) => {
      let heat = 0;
      for (const m of SPAIN_MARKERS) {
        const dx = x - m.x;
        const dy = y - m.y;
        heat += m.points * Math.exp(-(dx * dx + dy * dy) / TWO_SIGMA_SQ);
      }
      return { x, y, heat };
    });
    const max = Math.max(...raw.map((d) => d.heat));
    const norm = Math.log1p(max);
    return raw.map((d) => ({ ...d, t: norm > 0 ? Math.log1p(d.heat) / norm : 0 }));
  }, []);

  return (
    <svg viewBox="0 0 100 100" className={MAP_BOX} aria-hidden="true">
      {dots.map((d, i) => (
        <circle key={i} cx={d.x} cy={d.y} r={MAP_DOT_RADIUS} fill={ramp(d.t)} />
      ))}
    </svg>
  );
}

/* -------------------------------------------------------------------------- */
/*                                  Markers                                   */
/* -------------------------------------------------------------------------- */

const MAX_POINTS = Math.max(...SPAIN_MARKERS.map((m) => m.points));
const MARKER_MIN = 7;
const MARKER_RANGE = 13;

/** Square-root scale, so a marker's AREA tracks its count rather than its width. */
function markerSize(points: number) {
  return MARKER_MIN + Math.sqrt(points / MAX_POINTS) * MARKER_RANGE;
}

type Marker = (typeof SPAIN_MARKERS)[number];

/**
 * One province.
 *
 * The densest one takes the full-strength brand and a bloom; every other takes
 * the soft blue. That is the same rule the logo's accent dot follows — the index's
 * densest point is distinguished by INTENSITY, never by a second hue.
 */
function ProvinceMarker({
  marker,
  index,
  active,
  onEnter,
  onLeave,
}: {
  marker: Marker;
  index: number;
  active: boolean;
  onEnter: () => void;
  onLeave: () => void;
}) {
  const reduced = useReducedMotion();
  const size = markerSize(marker.points);
  const isLargest = marker.points === MAX_POINTS;

  return (
    <motion.button
      type="button"
      aria-label={`${marker.name}: ${marker.points.toLocaleString('es-ES')} puntos de venta`}
      onPointerEnter={onEnter}
      onPointerLeave={onLeave}
      onFocus={onEnter}
      onBlur={onLeave}
      className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer rounded-full outline-none"
      style={{ left: `${marker.x}%`, top: `${marker.y}%`, width: size, height: size }}
      initial={reduced ? false : { scale: 0, opacity: 0 }}
      whileInView={{ scale: 1, opacity: 1 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.45, delay: index * 0.05, ease: [0.16, 1, 0.3, 1] }}
    >
      <span
        className="absolute inset-0 rounded-full transition-transform duration-200"
        style={{
          background: isLargest ? 'var(--color-brand)' : 'rgba(138,185,253,0.85)',
          boxShadow: isLargest
            ? '0 0 18px 4px rgb(18 110 253 / 0.55)'
            : '0 0 10px 2px rgb(138 185 253 / 0.3)',
          transform: active ? 'scale(1.35)' : 'scale(1)',
        }}
      />
      {/* The halo only runs on the hovered province. A permanent pulse on sixteen
        * markers is sixteen things asking for attention at once, which is how the
        * previous version turned a reading into wallpaper. */}
      {active && !reduced && (
        <motion.span
          aria-hidden
          className="ring-brand absolute inset-0 rounded-full ring-1"
          animate={{ scale: [1, 2.1], opacity: [0.7, 0] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: 'easeOut' }}
        />
      )}
    </motion.button>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

/**
 * "Cobertura de España" — the coverage readout.
 *
 * The claim this tile has to land is that the index is not a Madrid product with
 * some provinces attached. So the country itself is the chart: every one of the
 * 1.969 dots is tinted by how much of the index sits near it, the sixteen
 * provinces the figures exist for are marked on top, and hovering one names it
 * and states its count. Nothing here is invented — the counts are the ones
 * already committed in `spain-map-dots.ts`, generated from the coverage research
 * against the live index.
 */
export function HostingMapCard() {
  const [active, setActive] = useState<string | null>(null);
  const hovered = SPAIN_MARKERS.find((m) => m.name === active) ?? null;

  return (
    <div
      id="cobertura"
      className="bg-natural-black relative col-span-1 min-h-(--box-min-height) overflow-hidden rounded-2xl lg:col-span-3"
    >
      <div className="relative h-full">
        <svg
          className="absolute -top-20 -left-80 z-40 rotate-45 fill-white/80 blur-3xl"
          width="100%"
          height="100%"
        >
          <ellipse cx="50%" cy="50%" rx="100" ry="60" />
        </svg>

        <div className="relative z-50 flex items-start justify-between p-4">
          <h2 className="text-base font-medium text-white">{BENTO.coverage.title}</h2>

          {/* The readout. It holds the hovered province, and falls back to the
            * legend so the card still explains its own colour when nothing is
            * under the pointer — a heat map with no key is a decoration. */}
          <div className="pointer-events-none min-w-[104px] text-right">
            {hovered ? (
              <>
                <p className="text-[13px] leading-tight font-medium text-white">{hovered.name}</p>
                <p className="text-brand-soft text-[11px] leading-tight tabular-nums">
                  {hovered.points.toLocaleString('es-ES')} puntos de venta
                </p>
              </>
            ) : (
              <div className="flex items-center justify-end gap-1.5">
                <span className="text-[10px] text-white/40">menos</span>
                <span
                  className="h-1.5 w-14 rounded-full"
                  style={{
                    background:
                      'linear-gradient(90deg, rgba(255,255,255,0.16), rgba(138,185,253,0.55), rgb(18,110,253))',
                  }}
                />
                <span className="text-[10px] text-white/40">más</span>
              </div>
            )}
          </div>
        </div>

        <div className="glass-dark absolute inset-0 w-full overflow-hidden mask-t-from-50% mask-radial-from-90%">
          <DensityField />
          <div className={MAP_BOX}>
            {SPAIN_MARKERS.map((marker, index) => (
              <ProvinceMarker
                key={marker.name}
                marker={marker}
                index={index}
                active={active === marker.name}
                onEnter={() => setActive(marker.name)}
                onLeave={() => setActive((cur) => (cur === marker.name ? null : cur))}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
