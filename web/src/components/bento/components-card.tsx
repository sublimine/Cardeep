import type { CSSProperties } from 'react';
import { motion } from 'motion/react';

/** Colour of the dormant PCB traces. */
const TRACE_COLOR = '#F2F2F2';

/** Colour of the travelling pulse and of the chip itself. */
const PULSE_COLOR = '#FA9A63';

/**
 * A plate renders every trace twice: once dormant (flat `#F2F2F2` stroke) and once as a
 * dashed pulse painted with `tailGradient`. The three plates differ only in how many
 * layers the pulse is built from.
 */
type PlateStyle = 'blur' | 'shadow' | 'plain';

type PulseLayer = {
  strokeWidth: string;
  opacity?: number;
  style?: CSSProperties;
};

const PULSE_LAYERS: Record<PlateStyle, readonly PulseLayer[]> = {
  blur: [{ strokeWidth: '2.5', style: { filter: 'blur(0.4px)' } }],
  shadow: [
    { strokeWidth: '2.5' },
    {
      strokeWidth: '1.5',
      opacity: 0.3,
      style: { filter: `drop-shadow(0 0 12px ${PULSE_COLOR})` },
    },
  ],
  plain: [{ strokeWidth: '2.5' }, { strokeWidth: '1.5', opacity: 0.3 }],
};

type Plate = {
  /** Placement of the plate inside the 336x314 graphic box. */
  position: string;
  width: number;
  height: number;
  /** Path `d` strings, shared by the dormant trace and its pulse. */
  paths: readonly string[];
  dashArray: string;
  /**
   * Length of one dash period. Advancing `strokeDashoffset` by exactly one period
   * returns the pattern to its starting phase, so the loop has no visible seam.
   */
  period: number;
  style: PlateStyle;
  /** Seconds for one pulse period. */
  duration: number;
  /** Seconds added per trace, so the traces in a plate fire in sequence. */
  stagger: number;
  /** Seconds added to the whole plate, so plates never pulse in lockstep. */
  offset: number;
};

const PLATES: readonly Plate[] = [
  {
    position: 'absolute bottom-6.5 left-0',
    width: 201,
    height: 166,
    paths: [
      'M12.427 165.594V126.58L32.3598 103.929H200.148',
      'M200.148 85.8084H27.8296L0.648438 113.896',
      'M0.648438 70.4057H200.148',
      'M200.148 50.4728H22.3934L0.648438 30.54',
      'M0.648438 0.640625L32.3598 32.352H200.148',
    ],
    dashArray: '60 500',
    period: 560,
    style: 'blur',
    duration: 6,
    stagger: 0.9,
    offset: 0,
  },
  {
    position: 'absolute top-1 left-0',
    width: 303,
    height: 124,
    paths: [
      'M241.461 -19.625V7.85497L301.26 68.5597V123.375',
      'M284.045 123.375V77.6201L221.528 15.1033V-19.625',
      'M109.641 -20.625L152.669 26.8818H210.656L265.924 83.0563V123.375',
      'M247.803 122.875V91.2107L200.689 44.0966H79.2799L15.1406 -21.125',
      'M0.640625 -5.625L69.3134 62.2174H192.535L229.683 98.459V123.375',
    ],
    dashArray: '30 500',
    period: 530,
    style: 'shadow',
    duration: 5,
    stagger: 0.7,
    offset: 0.35,
  },
  {
    position: 'absolute right-0.5 bottom-1',
    width: 167,
    height: 56,
    paths: [
      'M118.875 0V64.2816L169.613 115.926V142',
      'M99.8516 0V76.966L144.664 121V142',
      'M82.6391 0V83.3087L30.1641 142.5M63.6122 0V74.2483L0.664062 142.5',
      'M136.094 0V51.5975L178.678 96.8995H296.463',
    ],
    dashArray: '30 500',
    period: 530,
    style: 'plain',
    duration: 5,
    stagger: 0.55,
    offset: 0.15,
  },
];

/** The three chip pins down the left edge and the three down the right edge. */
const SIDE_PIN_OFFSETS = ['top-0', 'top-[17px]', 'top-[34px]', 'top-[51px]', 'top-[68px]'] as const;

/** Pins along the top and bottom edges are identical; only the row wrapper differs. */
const EDGE_PIN_COUNT = 5;

function TracePlate({ plate }: { plate: Plate }) {
  const layers = PULSE_LAYERS[plate.style];

  return (
    <div className={plate.position}>
      <svg
        width={plate.width}
        height={plate.height}
        viewBox={`0 0 ${plate.width} ${plate.height}`}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {plate.paths.map((d) => (
          <path key={d} d={d} stroke={TRACE_COLOR} strokeWidth="1.81208" />
        ))}
        {plate.paths.map((d, index) => (
          <g key={d}>
            {layers.map((layer) => (
              <motion.path
                key={layer.strokeWidth}
                d={d}
                stroke="url(#tailGradient)"
                strokeWidth={layer.strokeWidth}
                strokeLinecap="round"
                fill="none"
                opacity={layer.opacity}
                strokeDasharray={plate.dashArray}
                style={layer.style}
                // SSR ships every pulse at offset 0; the loop drives it one full dash
                // period forward, which lands back on the starting phase.
                animate={{ strokeDashoffset: [0, -plate.period] }}
                transition={{
                  duration: plate.duration,
                  delay: plate.offset + index * plate.stagger,
                  repeat: Infinity,
                  ease: 'linear',
                }}
              />
            ))}
          </g>
        ))}
        <defs>
          <linearGradient id="tailGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={PULSE_COLOR} stopOpacity="0" />
            <stop offset="50%" stopColor={PULSE_COLOR} stopOpacity="1" />
            <stop offset="100%" stopColor={PULSE_COLOR} stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

/** The dimmed companion chip clipped by the bottom-left corner of the graphic box. */
function GhostChip() {
  return (
    <div className="absolute -bottom-48 left-12 -translate-x-full -translate-y-full">
      <div className="absolute -top-3 right-8 h-3 w-1.5 bg-[#EEEEEE]" />
      <div className="relative size-28 rounded-3xl bg-white/50 shadow-[0px_2px_12px_0px_rgba(0,0,0,0.12)]" />
    </div>
  );
}

/** The orange chip with its four rows of pins and four blurred highlight blobs. */
function Chip() {
  return (
    <div className="absolute right-3 bottom-16">
      <div className="absolute -inset-3">
        <div className="absolute top-1/2 h-20 w-3 -translate-y-1/2">
          {SIDE_PIN_OFFSETS.map((top) => (
            <div key={top} className={`absolute ${top} left-0 h-1.5 w-3 bg-[#EEEEEE]`} />
          ))}
        </div>
        <div className="absolute top-1/2 right-0 h-20 w-3 -translate-y-1/2">
          {SIDE_PIN_OFFSETS.map((top) => (
            <div key={top} className={`absolute ${top} right-0 h-1.5 w-3 bg-[#EEEEEE]`} />
          ))}
        </div>
        <div className="absolute left-1/2 flex h-3 w-20 -translate-x-1/2 items-center gap-3">
          {Array.from({ length: EDGE_PIN_COUNT }, (_, index) => (
            <div key={index} className="h-3 w-1.5 self-stretch bg-[#EEEEEE]" />
          ))}
        </div>
        <div className="absolute bottom-0 left-1/2 flex h-3 w-20 -translate-x-1/2 items-center gap-3">
          {Array.from({ length: EDGE_PIN_COUNT }, (_, index) => (
            <div key={index} className="h-3 w-1.5 self-stretch bg-[#EEEEEE]" />
          ))}
        </div>
      </div>
      <div className="relative size-28 overflow-hidden rounded-3xl bg-[#FA9A63] shadow-[0px_3.200000047683716px_9.600000381469727px_0px_rgba(0,0,0,0.12)]">
        <div className="absolute top-[-25.60px] left-[26.80px] size-16 rounded-full bg-orange-200 blur-[48px]" />
        <div className="absolute top-[82.38px] left-[-47.20px] h-32 w-5 origin-top-left rotate-[-59.09deg] rounded-full bg-orange-200 blur-[48px]" />
        <div className="absolute top-[-35.30px] left-[113.80px] h-16 w-14 rounded-full bg-white blur-[48px]" />
        <div className="absolute top-[45.60px] left-[63.20px] h-44 w-36 rounded-full bg-orange-200/60 blur-[160px]" />
      </div>
    </div>
  );
}

/**
 * Bento card 1-3: a circuit board of traced lines feeding a chip, with the heading
 * floating above it. The graphic box is masked so the top half fades out behind the copy.
 */
export function ComponentsCard() {
  return (
    <div className="bg-natural-white col-span-1 min-h-(--box-min-height) overflow-hidden rounded-2xl lg:col-span-2">
      <div className="relative p-4">
        <div className="absolute inset-0">
          <div className="relative ml-4 h-[314px] w-[336px] scale-110 overflow-hidden mask-[linear-gradient(180deg,rgba(255,255,255,0)_0%,rgba(0,0,0,1)_50%)]">
            {PLATES.map((plate) => (
              <TracePlate key={plate.position} plate={plate} />
            ))}
            <GhostChip />
            <Chip />
          </div>
        </div>
        <div className="text-lg leading-6 font-medium tracking-tight z-10 relative">
          Components, Dashboards and Everything else
        </div>
      </div>
    </div>
  );
}
