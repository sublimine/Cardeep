import { useEffect, useRef, useState, type ReactNode } from 'react';
import { motion } from 'motion/react';
import { ArrowDown, Check, Plus } from 'lucide-react';
import { BENTO } from '@/content/site';

/* -------------------------------------------------------------------------- */
/*                              Decorative dots                               */
/* -------------------------------------------------------------------------- */

/** Grid pitch and dot edge, in CSS px, measured off the reference render. */
const DOT_PITCH = 8;
const DOT_SIZE = 4;
/**
 * Per-dot alpha range; the wrapper's `opacity-10` plus the masks do the rest.
 * The noise is squared before it is mapped onto the range because the reference
 * texture has far more near-invisible dots than a flat distribution produces —
 * squaring matches its measured mean darkness while keeping the same darkest dot.
 */
const DOT_MIN_ALPHA = 0.12;
const DOT_MAX_ALPHA = 0.8;

/** Deterministic value in [0, 1) per cell, so the texture never reshuffles. */
function cellNoise(col: number, row: number) {
  const seeded = Math.sin(col * 127.1 + row * 311.7) * 43758.5453;
  return seeded - Math.floor(seeded);
}

/**
 * Dot texture bleeding off the card's top-right corner.
 *
 * The reference never sizes its canvas, so the element keeps the 300x150
 * default backing store and maps 1:1 to CSS pixels — sizing it here would
 * change the dot pitch, so the attributes are deliberately left off.
 */
function DotGrid() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let row = 0; row * DOT_PITCH < canvas.height; row++) {
      for (let col = 0; col * DOT_PITCH < canvas.width; col++) {
        const noise = cellNoise(col, row);
        const alpha =
          DOT_MIN_ALPHA + noise * noise * (DOT_MAX_ALPHA - DOT_MIN_ALPHA);
        ctx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
        ctx.fillRect(col * DOT_PITCH, row * DOT_PITCH, DOT_SIZE, DOT_SIZE);
      }
    }
  }, []);

  return (
    <div className="absolute top-0 -right-20 size-40 w-full mask-b-from-10% mask-radial-[100%_100%] mask-radial-from-25% mask-radial-at-right opacity-10">
      <div className="pointer-events-none select-none absolute">
        <canvas ref={canvasRef} className="block h-full w-full" />
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*                                Radial gauge                                */
/* -------------------------------------------------------------------------- */

/** Seconds the needle takes to sweep a full turn, and the pause between sweeps. */
const SWEEP_DURATION = 3.5;
const SWEEP_REST = 4.5;

/**
 * Donut gauge. The gradient arc carries motion's `pathLength` attributes exactly
 * as the reference ships them — the path is filled rather than stroked, so the
 * draw-on is invisible, but the markup stays faithful. The needle group spins a
 * full turn and settles back on its resting `rotate(360deg)`.
 */
function ProgressGauge() {
  return (
    <svg
      width="213"
      height="216"
      viewBox="0 0 213 216"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="absolute inset-x-0 top-2 mx-auto size-40 mask-b-from-50%"
    >
      <path
        d="M213 109.5C213 168.318 165.318 216 106.5 216C47.6817 216 0 168.318 0 109.5C0 50.6812 47.6817 2.99951 106.5 2.99951C165.318 2.99951 213 50.6812 213 109.5ZM46.237 109.5C46.237 142.782 73.2177 169.762 106.5 169.762C139.782 169.762 166.763 142.782 166.763 109.5C166.763 76.2172 139.782 49.2365 106.5 49.2365C73.2177 49.2365 46.237 76.2172 46.237 109.5Z"
        fill="#F8F8F8"
      />
      <motion.path
        d="M86.0381 4.98367C63.9665 9.3048 43.8295 20.5024 28.5131 36.9716C13.1967 53.4408 3.48731 74.3362 0.776455 96.6628C-1.9344 118.989 2.49248 141.601 13.4226 161.257C24.3527 180.913 41.225 196.604 61.6212 206.082C82.0173 215.559 104.89 218.336 126.962 214.015C149.033 209.694 169.171 198.497 184.487 182.027C199.803 165.558 209.513 144.663 212.224 122.336C214.934 100.01 210.508 77.3979 199.577 57.7419L159.168 80.2125C165.353 91.3348 167.858 104.13 166.324 116.763C164.79 129.397 159.296 141.22 150.629 150.539C141.962 159.858 130.568 166.195 118.078 168.64C105.589 171.085 92.6465 169.513 81.1053 164.151C69.5642 158.788 60.017 149.909 53.8322 138.787C47.6474 127.664 45.1425 114.869 46.6764 102.236C48.2103 89.6023 53.7044 77.7787 62.3712 68.4596C71.0379 59.1406 82.4325 52.8044 94.9216 50.3593L86.0381 4.98367Z"
        fill="url(#paint0_linear_1_614)"
        initial={{ pathLength: 0 }}
        whileInView={{ pathLength: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1.6, ease: 'easeInOut' }}
      />
      <motion.g
        style={{ transformOrigin: '50% 50%', transformBox: 'view-box' }}
        initial={{ rotate: 0 }}
        whileInView={{ rotate: 360 }}
        viewport={{ once: true }}
        transition={{
          duration: SWEEP_DURATION,
          ease: 'easeInOut',
          repeat: Infinity,
          repeatDelay: SWEEP_REST,
        }}
      >
        <rect
          x="84"
          y="0.380371"
          width="2"
          height="56"
          rx="1"
          transform="rotate(-10.9638 84 0.380371)"
          fill="white"
        />
        <rect
          x="84"
          y="0.380371"
          width="2"
          height="56"
          rx="1"
          transform="rotate(-10.9638 84 0.380371)"
          fill="url(#paint1_linear_1_614)"
        />
      </motion.g>
      <defs>
        <linearGradient
          id="paint0_linear_1_614"
          x1="13"
          y1="0"
          x2="121"
          y2="0"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#F0F0F0" />
          <stop offset="1" stopColor="#EDE5CB" />
        </linearGradient>
        <linearGradient
          id="paint1_linear_1_614"
          x1="88.669"
          y1="27.3238"
          x2="72.6514"
          y2="27.5191"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#F1F1F1" />
          <stop offset="1" stopColor="#C9B76E" />
        </linearGradient>
      </defs>
    </svg>
  );
}

/* -------------------------------------------------------------------------- */
/*                               Movement stack                               */
/* -------------------------------------------------------------------------- */

/** Market movements in SSR DOM order. */
const MOVEMENTS = BENTO.movements.items;

type MovementKind = (typeof MOVEMENTS)[number]['kind'];

/**
 * One neutral glyph per kind of movement: the price fell, the car sold, stock
 * came in. Same 16px box and same slot the reference brand marks occupied.
 */
const MOVEMENT_GLYPHS: Record<MovementKind, ReactNode> = {
  precio: <ArrowDown className="size-4 text-neutral-500" />,
  venta: <Check className="size-4 text-neutral-500" />,
  stock: <Plus className="size-4 text-neutral-500" />,
};

const STACK_SIZE = MOVEMENTS.length;
/** Slot geometry: 0 is the front card, each step back sheds 10px and 6% scale. */
const CARD_OFFSET = 10;
const SCALE_FACTOR = 0.06;
/** How long a movement stays in front before the stack promotes. */
const CYCLE_MS = 5000;
/**
 * The captured resting state has the second card in front, which is the DOM
 * order two promotions in — so the stack opens on that state instead of on the
 * pre-hydration order.
 */
const INITIAL_SLOT_OFFSET = 2;

/**
 * Slot a card occupies on a given tick. Every tick promotes each card one slot
 * forward, which for a three-card stack is the same as adding `STACK_SIZE - 1`,
 * so the front card wraps around to the back.
 */
function slotOf(index: number, tick: number) {
  return (index + INITIAL_SLOT_OFFSET + (STACK_SIZE - 1) * tick) % STACK_SIZE;
}

function MovementStack() {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const interval = setInterval(
      () => setTick((current) => (current + 1) % STACK_SIZE),
      CYCLE_MS,
    );
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative mb-8 w-full">
      {MOVEMENTS.map((item, index) => {
        const slot = slotOf(index, tick);
        return (
          <motion.div
            key={item.kind}
            className="glass absolute flex h-20 w-full flex-col justify-between rounded-lg p-4"
            style={{ transformOrigin: 'top center' }}
            animate={{
              top: slot * -CARD_OFFSET,
              scale: 1 - slot * SCALE_FACTOR,
              zIndex: STACK_SIZE - slot,
            }}
            transition={{ duration: 0.45, ease: 'easeOut' }}
          >
            <div className="flex justify-between">
              <span className="font-mono text-xs text-neutral-500">
                {item.kind}
              </span>
              {MOVEMENT_GLYPHS[item.kind]}
            </div>
            <p className="text-base text-neutral-700">{item.text}</p>
          </motion.div>
        );
      })}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

/**
 * The reference heading is a two-line block and the layout below it depends on
 * that height, so the title breaks before its last word rather than wrapping.
 */
const TITLE_BREAK = BENTO.movements.title.lastIndexOf(' ');
const TITLE_HEAD = BENTO.movements.title.slice(0, TITLE_BREAK);
const TITLE_TAIL = BENTO.movements.title.slice(TITLE_BREAK + 1);

export function ProgressTrackingCard() {
  return (
    <div className="glass relative col-span-1 min-h-(--box-min-height) overflow-hidden rounded-2xl p-4 pb-0 lg:col-span-2">
      <div className="h-full">
        <DotGrid />
        <h2 className="text-base font-medium text-black">
          {TITLE_HEAD}
          <br />
          {TITLE_TAIL}
        </h2>
        <div className="relative flex h-full w-full items-center justify-end">
          <ProgressGauge />
          <MovementStack />
        </div>
      </div>
    </div>
  );
}
