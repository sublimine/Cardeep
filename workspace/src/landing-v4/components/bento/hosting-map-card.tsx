import type { ReactNode } from 'react';
import { motion } from 'framer-motion';

import { BENTO } from '@landing/content/site';
import { SPAIN_DOTS, SPAIN_MARKERS } from './spain-map-dots';

/** Seconds between consecutive pin entrances, applied in DOM order. */
const PIN_STAGGER = 0.12;

/**
 * Dot geometry. The reference used a near-black fill because its world map was
 * only texture; here the map carries the section's whole message, so the dots are
 * lifted to a translucent white that still sits behind the markers.
 */
const MAP_DOT_RADIUS = 0.26;
const MAP_DOT_FILL = 'rgba(255,255,255,0.30)';

/**
 * The map and the marker layer share one square box, so a marker's `[x, y]`
 * always lands on the dots it belongs to whatever the card ends up measuring.
 * Both boxes being square is also why `slice` never crops or stretches Spain.
 */
const MAP_BOX =
  'absolute top-1/2 left-1/2 aspect-square h-full -translate-x-1/2 -translate-y-1/2';

/** Marker diameter in px: `points` on a square-root scale, largest at 23px. */
const MARKER_MIN_SIZE = 8;
const MARKER_SIZE_RANGE = 15;

const MAX_MARKER_POINTS = Math.max(...SPAIN_MARKERS.map((marker) => marker.points));

function markerSize(points: number) {
  return MARKER_MIN_SIZE + Math.sqrt(points / MAX_MARKER_POINTS) * MARKER_SIZE_RANGE;
}

type PinPosition = {
  /** Percentage offsets inside the masked map layer. */
  top: string;
  left: string;
};

/**
 * The dot-matrix peninsula: 1969 circles plotted from the real province
 * outlines, with the Balearics in place and the Canaries as an inset.
 */
function SpainMapDots() {
  return (
    <svg
      viewBox="0 0 100 100"
      className={MAP_BOX}
      preserveAspectRatio="xMidYMid slice"
    >
      {SPAIN_DOTS.map(([cx, cy]) => (
        <circle
          key={`${cx}-${cy}`}
          cx={cx}
          cy={cy}
          r={MAP_DOT_RADIUS}
          fill={MAP_DOT_FILL}
        />
      ))}
    </svg>
  );
}

/**
 * Shared pin shell: scales in once on scroll and carries the looping halo.
 * The halo keeps the source's inline `animation-*` declarations even though the
 * loop itself is driven by motion, so the rendered markup matches the target.
 * Its half-size offset rides on motion's own transform, because an inline
 * transform would otherwise win over the translate utilities.
 */
function PinShell({
  top,
  left,
  index,
  children,
}: PinPosition & { index: number; children: ReactNode }) {
  return (
    <motion.div
      className="absolute"
      style={{ top, left }}
      initial={{ opacity: 0, scale: 0 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * PIN_STAGGER, ease: 'easeOut' }}
    >
      <motion.div
        className="absolute h-6 w-6 rounded-full bg-white/10"
        style={{ animationDuration: '2s', animationIterationCount: 'infinite' }}
        initial={{ opacity: 0, scale: 0.5, x: '-50%', y: '-50%' }}
        animate={{ opacity: [0.55, 0], scale: [0.5, 1.8], x: '-50%', y: '-50%' }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
      />
      {children}
    </motion.div>
  );
}

/** Province marker: a glass dot sized by that province's weight in the index. */
function MarkerPinBody({ name, points }: { name: string; points: number }) {
  const size = markerSize(points);
  const isLargest = points === MAX_MARKER_POINTS;

  return (
    <div
      className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full"
      style={{
        width: size,
        height: size,
        // The busiest province takes the accent; the rest read as lit points on
        // the grid rather than the grey smudges a neutral glass chip produced.
        background: isLargest ? 'var(--color-primary)' : 'rgba(96,165,250,0.85)',
        boxShadow: isLargest
          ? '0 0 0 3px rgb(255 204 0 / 0.18), 0 0 14px 2px rgb(255 204 0 / 0.35)'
          : '0 0 0 3px rgb(96 165 250 / 0.16), 0 0 10px 1px rgb(96 165 250 / 0.28)',
      }}
    >
      <span className="sr-only">{name}</span>
    </div>
  );
}

/**
 * "Cobertura de España" — the black bento card: a blurred rotated glow behind
 * the title, over a masked dot-matrix Spain carrying one marker per province,
 * sized by how much of the index that province holds.
 */
export function HostingMapCard() {
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
        <h2 className="relative z-50 p-4 text-base font-medium text-white">
          {BENTO.coverage.title}
        </h2>
        <div className="glass-dark absolute inset-0 w-full overflow-hidden mask-t-from-50% mask-radial-from-90%">
          <SpainMapDots />
          <div className={MAP_BOX}>
            {SPAIN_MARKERS.map((marker, index) => (
              <PinShell
                key={marker.name}
                top={`${marker.y}%`}
                left={`${marker.x}%`}
                index={index}
              >
                <MarkerPinBody name={marker.name} points={marker.points} />
              </PinShell>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
