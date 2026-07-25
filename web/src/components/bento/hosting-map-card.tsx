import { motion, useReducedMotion, type Variants } from 'motion/react';

import { Glass } from '@/components/ui/glass';
import { cn } from '@/lib/utils';
import { BENTO, FIGURES } from '@/content/site';
import { SPAIN_DOTS, SPAIN_MARKERS } from './spain-map-dots';

/* --------------------------------------------------------------- geometry */

/** Matches `rounded-2xl` on the sibling bento tiles. */
const CARD_RADIUS = 16;

/**
 * The dot field and the marker layer share one square box, so a marker's
 * `[x, y]` always lands on the dots it belongs to whatever the card measures.
 * Both boxes being square is also why Spain is never cropped or stretched.
 *
 * It hangs from the bottom, a header's height short of full: at the card's
 * narrowest the map is nearly as wide as the tile, and without that band the
 * Cantabrian markers would open their labels straight into the heading.
 */
const MAP_BOX =
  'absolute bottom-0 left-1/2 aspect-square h-[calc(100%-34px)] -translate-x-1/2';

/** Dot radius in viewBox units; the ink is the theme's, so the map inverts. */
const DOT_RADIUS = 0.34;
const DOT_OPACITY = 0.26;

/* ------------------------------------------------------------ choreography */

/**
 * The field is revealed as a west-to-east wave. One motion node per dot would
 * mean 1969 of them, so the dots are bucketed into vertical bands and a single
 * node drives each band: the wave reads identically and the card stays cheap.
 */
const WAVE_BANDS = 22;
const BAND_STAGGER = 0.038;
const BAND_DURATION = 0.5;

/** The scan line leads the wave front and runs exactly once. */
const SWEEP_DURATION = 1.15;

/** Keeps the scan line off the card's top and bottom edges. */
const SWEEP_FADE =
  'linear-gradient(to bottom, transparent 0%, #000 16%, #000 84%, transparent 100%)';

/** Markers land while the field is still settling, heaviest province first. */
const MARKERS_START = 0.75;
const MARKER_STAGGER = 0.05;
const MARKER_DURATION = 0.42;

/** Slight overshoot on the way in — a pop, not a bounce. */
const POP_EASE: [number, number, number, number] = [0.34, 1.32, 0.64, 1];

function buildBands() {
  const xs = SPAIN_DOTS.map(([x]) => x);
  const min = Math.min(...xs);
  const span = Math.max(...xs) - min || 1;
  const bands: (readonly [number, number])[][] = Array.from(
    { length: WAVE_BANDS },
    () => [],
  );

  for (const dot of SPAIN_DOTS) {
    const slot = Math.min(WAVE_BANDS - 1, Math.floor(((dot[0] - min) / span) * WAVE_BANDS));
    bands[slot].push(dot);
  }

  return bands;
}

const DOT_BANDS = buildBands();

/* ---------------------------------------------------------------- markers */

type ProvinceMarker = (typeof SPAIN_MARKERS)[number];

/** Marker diameter in px: `points` on a square-root scale so area reads true. */
const MARKER_MIN_SIZE = 7;
const MARKER_SIZE_RANGE = 12;
/** Breathing room around the dot, so the smallest provinces stay hoverable. */
const MARKER_PAD = 6;

const MAX_MARKER_POINTS = Math.max(...SPAIN_MARKERS.map((marker) => marker.points));

/** Smallest first in the DOM, so the heavier provinces paint over their neighbours. */
const MARKERS: ProvinceMarker[] = [...SPAIN_MARKERS].sort((a, b) => a.points - b.points);

/** Above this line the card has no room overhead, so the label flips underneath. */
const LABEL_FLIP_Y = 22;

function markerSize(points: number) {
  return MARKER_MIN_SIZE + Math.sqrt(points / MAX_MARKER_POINTS) * MARKER_SIZE_RANGE;
}

/* ------------------------------------------------------------------- copy */

/**
 * `site.ts` has no legend string for a chart it did not have; this one is new,
 * and it is literal — `points` is the province's count of points of sale,
 * normalised to the published national total in tools/mockups/build-map.mjs.
 */
const SIZE_LEGEND = 'puntos de venta por provincia';

const COVERAGE_NOTE = `${FIGURES.provinces.value} ${FIGURES.provinces.label}`;

/* --------------------------------------------------------------- variants */

/**
 * Every phase hangs off one `whileInView` on the card, so the order is fixed:
 * heading, then the wave west to east, then the markers, then the legend.
 * `reduce` collapses each phase to its resting state — no offsets, no loops.
 */
function bandVariants(reduce: boolean): Variants {
  return {
    hidden: { opacity: reduce ? 1 : 0 },
    shown: (index: number) => ({
      opacity: 1,
      transition: reduce
        ? { duration: 0 }
        : { duration: BAND_DURATION, delay: index * BAND_STAGGER, ease: 'easeOut' },
    }),
  };
}

const sweepVariants: Variants = {
  hidden: { opacity: 0, x: '-52%' },
  shown: {
    opacity: [0, 1, 1, 0],
    x: ['-52%', '52%'],
    transition: {
      x: { duration: SWEEP_DURATION, ease: 'linear' },
      opacity: { duration: SWEEP_DURATION, times: [0, 0.12, 0.72, 1], ease: 'linear' },
    },
  },
};

function markerVariants(reduce: boolean): Variants {
  return {
    hidden: reduce ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.3 },
    shown: (rank: number) => ({
      opacity: 1,
      scale: 1,
      transition: reduce
        ? { duration: 0 }
        : {
            duration: MARKER_DURATION,
            delay: MARKERS_START + rank * MARKER_STAGGER,
            ease: POP_EASE,
          },
    }),
  };
}

/** One province pulses — the busiest. Nine would be a strobe, not a signal. */
const haloVariants: Variants = {
  hidden: { opacity: 0, scale: 0.55 },
  shown: (rank: number) => ({
    opacity: [0, 0.5, 0],
    scale: [0.55, 1.1, 2],
    transition: {
      delay: MARKERS_START + rank * MARKER_STAGGER + 0.45,
      duration: 3.4,
      times: [0, 0.24, 1],
      ease: 'easeOut',
      repeat: Infinity,
      repeatDelay: 1.1,
    },
  }),
};

function fadeVariants(reduce: boolean, delay: number): Variants {
  return {
    hidden: reduce ? { opacity: 1, y: 0 } : { opacity: 0, y: 6 },
    shown: {
      opacity: 1,
      y: 0,
      transition: reduce ? { duration: 0 } : { duration: 0.5, delay, ease: 'easeOut' },
    },
  };
}

/* ------------------------------------------------------------------ parts */

/** The dot-matrix peninsula: 1969 circles from the real province outlines. */
function DotField({ variants }: { variants: Variants }) {
  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid slice"
      className="absolute inset-0 h-full w-full"
      aria-hidden
    >
      {/* Presentation via style, not attributes: `var()` only resolves in CSS. */}
      <g style={{ fill: 'var(--cd-fg)', fillOpacity: DOT_OPACITY }}>
        {DOT_BANDS.map((band, index) => (
          <motion.g key={`band-${index}`} custom={index} variants={variants}>
            {band.map(([cx, cy]) => (
              <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r={DOT_RADIUS} />
            ))}
          </motion.g>
        ))}
      </g>
    </svg>
  );
}

/**
 * The scan line: a soft accent band that crosses the box once, just ahead of
 * the wave front. It is the reveal's cause, which is the only reason it exists.
 */
function SweepLine() {
  return (
    <motion.span
      aria-hidden
      className="absolute inset-0"
      style={{
        background:
          'linear-gradient(90deg, transparent 46%, color-mix(in srgb, var(--cd-accent) 38%, transparent) 50%, transparent 54%)',
        maskImage: SWEEP_FADE,
        WebkitMaskImage: SWEEP_FADE,
      }}
      variants={sweepVariants}
    />
  );
}

/**
 * A province: an accent dot sized by its weight, a label that surfaces on hover
 * and, on the busiest one only, a slow halo. The hit area is the dot plus a few
 * pixels, so neighbours like Barcelona and Girona both stay reachable.
 */
function MarkerPin({
  marker,
  rank,
  reduce,
  variants,
  isBusiest,
}: {
  marker: ProvinceMarker;
  rank: number;
  reduce: boolean;
  variants: Variants;
  isBusiest: boolean;
}) {
  const size = markerSize(marker.points);
  const box = size + MARKER_PAD;
  const labelBelow = marker.y < LABEL_FLIP_Y;

  return (
    <motion.div
      className="group pointer-events-auto absolute flex items-center justify-center hover:z-30"
      style={{
        top: `${marker.y}%`,
        left: `${marker.x}%`,
        width: box,
        height: box,
        // Centring by margin keeps `transform` free for the entrance animation.
        marginTop: -box / 2,
        marginLeft: -box / 2,
      }}
      custom={rank}
      variants={variants}
    >
      {isBusiest && !reduce ? (
        <motion.span
          aria-hidden
          className="pointer-events-none absolute inset-0 rounded-full"
          style={{
            border: '1px solid color-mix(in srgb, var(--cd-accent) 45%, transparent)',
            background: 'color-mix(in srgb, var(--cd-accent) 10%, transparent)',
          }}
          custom={rank}
          variants={haloVariants}
        />
      ) : null}

      <span
        className="rounded-full transition-[translate,scale] duration-200 ease-out group-hover:-translate-y-[3px] group-hover:scale-[1.14]"
        style={{
          width: size,
          height: size,
          background: 'var(--cd-accent)',
          boxShadow: '0 0 0 3px color-mix(in srgb, var(--cd-accent) 16%, transparent)',
        }}
      />

      <span
        className={cn(
          'glass-chip pointer-events-none absolute left-1/2 -translate-x-1/2 rounded-md px-2 py-[3px] text-[10px] leading-none font-medium whitespace-nowrap text-foreground opacity-0 transition-opacity duration-200 group-hover:opacity-100',
          labelBelow ? 'top-full mt-2' : 'bottom-full mb-2',
        )}
      >
        {marker.name}
      </span>
    </motion.div>
  );
}

/* ------------------------------------------------------------------- card */

/**
 * "Cobertura de España" — the dot field wakes up west to east behind a single
 * scan line, the provinces land heaviest first, and the busiest one keeps
 * breathing. Size is the only encoding, so the legend says what it means.
 */
export function HostingMapCard() {
  const reduce = useReducedMotion() ?? false;
  const bands = bandVariants(reduce);
  const markers = markerVariants(reduce);

  return (
    <Glass
      id="cobertura"
      radius={CARD_RADIUS}
      interactive
      className="col-span-1 min-h-(--box-min-height) lg:col-span-3"
    >
      <motion.div
        className="relative h-full w-full p-4"
        variants={{ hidden: {}, shown: {} }}
        initial="hidden"
        whileInView="shown"
        viewport={{ once: true, amount: 0.3 }}
      >
        <div className={cn(MAP_BOX, 'pointer-events-none')}>
          <DotField variants={bands} />
          {reduce ? null : <SweepLine />}
          {MARKERS.map((marker, index) => (
            <MarkerPin
              key={marker.name}
              marker={marker}
              rank={MARKERS.length - 1 - index}
              reduce={reduce}
              variants={markers}
              isBusiest={marker.points === MAX_MARKER_POINTS}
            />
          ))}
        </div>

        <motion.header
          className="relative z-10 flex flex-col gap-1"
          variants={fadeVariants(reduce, 0.05)}
        >
          <h2 className="text-base font-medium text-foreground">{BENTO.coverage.title}</h2>
          <p className="text-[11px] leading-none text-muted-foreground">{COVERAGE_NOTE}</p>
        </motion.header>

        <motion.p
          className="absolute right-4 bottom-4 z-10 flex items-center gap-2 text-[10px] tracking-[0.03em] text-muted-foreground"
          variants={fadeVariants(reduce, MARKERS_START + MARKERS.length * MARKER_STAGGER + 0.2)}
        >
          <span aria-hidden className="flex items-center gap-1.5">
            <span
              className="block h-[5px] w-[5px] rounded-full"
              style={{ background: 'color-mix(in srgb, var(--cd-accent) 55%, transparent)' }}
            />
            <span
              className="block h-[10px] w-[10px] rounded-full"
              style={{ background: 'var(--cd-accent)' }}
            />
          </span>
          {SIZE_LEGEND}
        </motion.p>
      </motion.div>
    </Glass>
  );
}
