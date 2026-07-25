import { useEffect, useRef, useState, type ReactNode } from 'react';
import { motion } from 'motion/react';
import { IconBrandGithubFilled } from '@tabler/icons-react';

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
/*                             Notification stack                             */
/* -------------------------------------------------------------------------- */

/** Slack mark, inlined verbatim — it is a brand logo, not an icon-set glyph. */
function SlackMark() {
  return (
    <svg
      width="17"
      height="16"
      viewBox="0 0 17 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="size-4"
    >
      <path
        d="M3.37492 10.1148C3.37492 11.0447 2.62335 11.7963 1.69344 11.7963C0.763533 11.7963 0.0119629 11.0447 0.0119629 10.1148C0.0119629 9.18492 0.763533 8.43335 1.69344 8.43335H3.37492V10.1148Z"
        fill="#E01E5A"
      />
      <path
        d="M4.21631 10.1148C4.21631 9.18492 4.96788 8.43335 5.89779 8.43335C6.8277 8.43335 7.57927 9.18492 7.57927 10.1148V14.3185C7.57927 15.2484 6.8277 16 5.89779 16C4.96788 16 4.21631 15.2484 4.21631 14.3185V10.1148Z"
        fill="#E01E5A"
      />
      <path
        d="M5.89754 3.3632C4.96763 3.3632 4.21606 2.61163 4.21606 1.68172C4.21606 0.751815 4.96763 0.000244141 5.89754 0.000244141C6.82745 0.000244141 7.57902 0.751815 7.57902 1.68172V3.3632H5.89754Z"
        fill="#36C5F0"
      />
      <path
        d="M5.89792 4.2168C6.82782 4.2168 7.57939 4.96837 7.57939 5.89828C7.57939 6.82819 6.82782 7.57975 5.89792 7.57975H1.68148C0.75157 7.57975 0 6.82819 0 5.89828C0 4.96837 0.75157 4.2168 1.68148 4.2168H5.89792Z"
        fill="#36C5F0"
      />
      <path
        d="M12.637 5.89828C12.637 4.96837 13.3885 4.2168 14.3184 4.2168C15.2484 4.2168 15.9999 4.96837 15.9999 5.89828C15.9999 6.82819 15.2484 7.57975 14.3184 7.57975H12.637V5.89828Z"
        fill="#2EB67D"
      />
      <path
        d="M11.7956 5.89792C11.7956 6.82782 11.044 7.57939 10.1141 7.57939C9.18419 7.57939 8.43262 6.82782 8.43262 5.89792V1.68148C8.43262 0.751571 9.18419 0 10.1141 0C11.044 0 11.7956 0.751571 11.7956 1.68148V5.89792Z"
        fill="#2EB67D"
      />
      <path
        d="M10.1143 12.637C11.0443 12.637 11.7958 13.3885 11.7958 14.3184C11.7958 15.2484 11.0443 15.9999 10.1143 15.9999C9.18443 15.9999 8.43286 15.2484 8.43286 14.3184V12.637H10.1143Z"
        fill="#ECB22E"
      />
      <path
        d="M10.1141 11.7963C9.18419 11.7963 8.43262 11.0447 8.43262 10.1148C8.43262 9.18492 9.18419 8.43335 10.1141 8.43335H14.3305C15.2604 8.43335 16.012 9.18492 16.012 10.1148C16.012 11.0447 15.2604 11.7963 14.3305 11.7963H10.1141Z"
        fill="#ECB22E"
      />
    </svg>
  );
}

type StackItem = {
  id: string;
  message: string;
  icon: ReactNode;
};

/** Notifications in SSR DOM order. */
const NOTIFICATIONS: StackItem[] = [
  { id: 'revision', message: 'Revision Completed', icon: <SlackMark /> },
  {
    id: 'hotfix',
    message: 'HOTFIX: update design',
    icon: <IconBrandGithubFilled className="size-4" />,
  },
  {
    id: 'design',
    message: 'Design Finalized',
    icon: (
      <img
        alt="Design Finalized"
        loading="lazy"
        width={20}
        height={20}
        decoding="async"
        className="rounded-full"
        src="/manu.webp"
      />
    ),
  },
];

const STACK_SIZE = NOTIFICATIONS.length;
/** Slot geometry: 0 is the front card, each step back sheds 10px and 6% scale. */
const CARD_OFFSET = 10;
const SCALE_FACTOR = 0.06;
/** How long a notification stays in front before the stack promotes. */
const CYCLE_MS = 5000;
/**
 * The captured resting state has `HOTFIX: update design` in front, which is the
 * DOM order two promotions in — so the stack opens on that state instead of on
 * the pre-hydration order.
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

function NotificationStack() {
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
      {NOTIFICATIONS.map((item, index) => {
        const slot = slotOf(index, tick);
        return (
          <motion.div
            key={item.id}
            className="absolute flex h-20 w-full flex-col justify-between rounded-lg bg-white p-4 shadow ring-1 shadow-black/10 ring-black/5"
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
                notification
              </span>
              {item.icon}
            </div>
            <p className="text-base text-neutral-700">{item.message}</p>
          </motion.div>
        );
      })}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

export function ProgressTrackingCard() {
  return (
    <div className="bg-natural-white relative col-span-1 min-h-(--box-min-height) overflow-hidden rounded-2xl p-4 pb-0 lg:col-span-2">
      <div className="h-full">
        <DotGrid />
        <h2 className="text-base font-medium text-black">
          Regular updates and
          <br />
          progress tracking
        </h2>
        <div className="relative flex h-full w-full items-center justify-end">
          <ProgressGauge />
          <NotificationStack />
        </div>
      </div>
    </div>
  );
}
