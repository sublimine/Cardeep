import type { ReactNode } from 'react';
import { motion } from 'motion/react';
import {
  WORLD_MAP_DOT_FILL,
  WORLD_MAP_DOT_RADIUS,
  WORLD_MAP_ROWS,
} from './world-map-dots';

/** Seconds between consecutive pin entrances, applied in DOM order. */
const PIN_STAGGER = 0.12;

type PinPosition = {
  /** Percentage offsets inside the masked map layer. */
  top: string;
  left: string;
};

type AvatarPin = PinPosition & {
  kind: 'avatar';
  alt: string;
  src: string;
};

type ServerPin = PinPosition & {
  kind: 'server';
};

type MapPin = AvatarPin | ServerPin;

/** The ten pins, in DOM order: five portraits, then five server nodes. */
const MAP_PINS: readonly MapPin[] = [
  { kind: 'avatar', top: '32%', left: '68%', alt: 'India', src: '/manu.webp' },
  {
    kind: 'avatar',
    top: '72%',
    left: '82%',
    alt: 'Australia',
    src: '/avatar/unsplash-portrait-3.jpg',
  },
  {
    kind: 'avatar',
    top: '28%',
    left: '15%',
    alt: 'California',
    src: '/avatar/unsplash-portrait-2.jpg',
  },
  {
    kind: 'avatar',
    top: '40%',
    left: '52%',
    alt: 'Dubai',
    src: '/avatar/unsplash-portrait-1.jpg',
  },
  {
    kind: 'avatar',
    top: '65%',
    left: '35%',
    alt: 'Brazil',
    src: '/avatar/unsplash-portrait-4.jpg',
  },
  { kind: 'server', top: '35%', left: '22%' },
  { kind: 'server', top: '22%', left: '47%' },
  { kind: 'server', top: '26%', left: '53%' },
  { kind: 'server', top: '38%', left: '78%' },
  { kind: 'server', top: '30%', left: '85%' },
];

/**
 * The dot-matrix continents: 8550 circles across 115 latitude rows, each row
 * stored as `[cy, ...cx]` so the coordinate table stays compact.
 */
function WorldMapDots() {
  return (
    <svg
      viewBox="0 0 210 100"
      className="h-full w-full"
      preserveAspectRatio="xMidYMid slice"
    >
      {WORLD_MAP_ROWS.flatMap((row) => {
        const [cy, ...cxs] = row;
        return cxs.map((cx) => (
          <circle
            key={`${cy}-${cx}`}
            cx={cx}
            cy={cy}
            r={WORLD_MAP_DOT_RADIUS}
            fill={WORLD_MAP_DOT_FILL}
          />
        ));
      })}
    </svg>
  );
}

/**
 * Shared pin shell: scales in once on scroll and carries the looping halo.
 * The halo keeps the source's inline `animation-*` declarations even though the
 * loop itself is driven by motion, so the rendered markup matches the target.
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
        className="absolute h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/10"
        style={{ animationDuration: '2s', animationIterationCount: 'infinite' }}
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: [0.55, 0], scale: [0.5, 1.8] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
      />
      {children}
    </motion.div>
  );
}

/** Portrait pin: the wrapper rests at `scale(0.8)`, so 28px renders at ~22px. */
function AvatarPinBody({ alt, src }: Pick<AvatarPin, 'alt' | 'src'>) {
  return (
    <div
      className="absolute -translate-x-1/2 -translate-y-1/2"
      style={{ transform: 'scale(0.8)' }}
    >
      <div className="relative h-7 w-7 overflow-hidden rounded-full border border-neutral-500 shadow-lg">
        <img
          alt={alt}
          loading="lazy"
          width={28}
          height={28}
          decoding="async"
          className="h-full w-full object-cover"
          src={src}
        />
      </div>
    </div>
  );
}

/** Server pin: rises 20px while scaling up from nothing. */
function ServerPinBody({ index }: { index: number }) {
  return (
    <motion.div
      className="absolute -translate-x-1/2 -translate-y-1/2"
      initial={{ y: 20, scale: 0 }}
      whileInView={{ y: 0, scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * PIN_STAGGER, ease: 'easeOut' }}
    >
      <div className="flex h-7 w-7 items-center justify-center rounded-full border border-neutral-500 bg-neutral-900 shadow-lg">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="h-4 w-4 text-neutral-500"
        >
          <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
          <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
          <line x1="6" y1="6" x2="6.01" y2="6" />
          <line x1="6" y1="18" x2="6.01" y2="18" />
        </svg>
      </div>
    </motion.div>
  );
}

/**
 * "Hosting, Deployment & Maintenance" — the black bento card: a blurred
 * rotated glow behind the title, over a masked dot-matrix world map dotted
 * with teammate portraits and server nodes.
 */
export function HostingMapCard() {
  return (
    <div className="bg-natural-black relative col-span-1 min-h-(--box-min-height) overflow-hidden rounded-2xl lg:col-span-3">
      <div className="relative h-full">
        <svg
          className="absolute -top-20 -left-80 z-40 rotate-45 fill-white/80 blur-3xl"
          width="100%"
          height="100%"
        >
          <ellipse cx="50%" cy="50%" rx="100" ry="60" />
        </svg>
        <h2 className="relative z-50 p-4 text-base font-medium text-white">
          Hosting, Deployment &amp; Maintenance
        </h2>
        <div className="absolute inset-0 w-full overflow-hidden bg-neutral-950 mask-t-from-50% mask-radial-from-90%">
          <WorldMapDots />
          {MAP_PINS.map((pin, index) => (
            <PinShell
              key={`${pin.top}-${pin.left}`}
              top={pin.top}
              left={pin.left}
              index={index}
            >
              {pin.kind === 'avatar' ? (
                <AvatarPinBody alt={pin.alt} src={pin.src} />
              ) : (
                <ServerPinBody index={index} />
              )}
            </PinShell>
          ))}
        </div>
      </div>
    </div>
  );
}
