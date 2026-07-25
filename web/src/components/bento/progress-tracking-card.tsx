import { useEffect, useState } from 'react';
import { motion, useReducedMotion, type Variants } from 'motion/react';
import { ArrowDown, Check, Plus, type LucideIcon } from 'lucide-react';

import { Glass } from '@/components/ui/glass';
import { BENTO, BRAND } from '@/content/site';

/* -------------------------------------------------------------------------- */
/*                                   Copy                                     */
/* -------------------------------------------------------------------------- */

/**
 * Not in `site.ts`: the header needs a two-word status marker and the content
 * module only carries the long form ("Índice nacional en vivo"). Same voice.
 */
const LIVE_LABEL = 'En vivo';

/* -------------------------------------------------------------------------- */
/*                                 Movements                                  */
/* -------------------------------------------------------------------------- */

const MOVEMENTS = BENTO.movements.items;

type MovementKind = (typeof MOVEMENTS)[number]['kind'];

/** One glyph and one semantic colour per kind of movement. */
const MOVEMENT_STYLE: Record<MovementKind, { icon: LucideIcon; tone: string }> = {
  /** A price drop is the reader's good news, so it takes the positive tone. */
  precio: { icon: ArrowDown, tone: 'var(--cd-positive)' },
  /** A sale is a settled fact rather than an opportunity: plain ink. */
  venta: { icon: Check, tone: 'var(--cd-fg)' },
  /** New stock is something to act on: the brand accent. */
  stock: { icon: Plus, tone: 'var(--cd-accent)' },
};

/** `"Bajada de precio · −1.200 €"` → the headline and the figure that carries it. */
function splitMovement(text: string) {
  const at = text.indexOf(' · ');
  if (at === -1) return { headline: text, detail: '' };
  return { headline: text.slice(0, at), detail: text.slice(at + 3) };
}

/* -------------------------------------------------------------------------- */
/*                              Stack geometry                                */
/* -------------------------------------------------------------------------- */

/** Cards visible at once. Position 0 is the front card. */
const DEPTH = 3;
const CARD_HEIGHT = 88;
/** How far each card behind the front one rises, and how much it recedes. */
const SLOT_RISE = 16;
const SLOT_SCALE = 0.05;
const SLOT_OPACITY = [1, 0.6, 0.32];
/** Travel of the card leaving the front of the stack. */
const EXIT_DROP = 20;
/**
 * Promotion ripples backwards: the front card takes its place first and the
 * queue settles behind it. The lag is also what keeps the card arriving at the
 * back from showing up while the one it repeats is still fading out — with only
 * three movements in the list, the two are the same notification.
 */
const SLOT_LAG = 0.13;
const STACK_HEIGHT = CARD_HEIGHT + (DEPTH - 1) * SLOT_RISE;
/** Calm enough to read one movement and then ignore the rest. */
const CYCLE_MS = 4500;

/**
 * Positions rendered on every tick: the card on its way out (-1) plus the
 * visible stack. Keeping the leaving card mounted is what lets it slide out and
 * fade instead of vanishing, and it costs nothing — by the time its slot is
 * recycled it is already at zero opacity.
 */
const POSITIONS = Array.from({ length: DEPTH + 1 }, (_, index) => index - 1);

/** Index into the movement list, for a head counter that only ever grows. */
function movementAt(id: number) {
  const size = MOVEMENTS.length;
  return MOVEMENTS[((id % size) + size) % size];
}

function MovementStack({ active }: { active: boolean }) {
  const reduced = useReducedMotion();
  const [head, setHead] = useState(0);

  useEffect(() => {
    // The loop is infinite, so it stays off under reduced motion, and it does
    // not start until the card has actually been seen.
    if (!active || reduced) return;
    const timer = window.setInterval(() => setHead((current) => current + 1), CYCLE_MS);
    return () => window.clearInterval(timer);
  }, [active, reduced]);

  return (
    <div className="relative w-full" style={{ height: STACK_HEIGHT }}>
      {POSITIONS.map((position) => {
        const id = head + position;
        const item = movementAt(id);
        const { icon: Icon, tone } = MOVEMENT_STYLE[item.kind];
        const { headline, detail } = splitMovement(item.text);
        const leaving = position < 0;

        return (
          <motion.div
            key={id}
            // The leaving card repeats the one at the back of the stack.
            aria-hidden={leaving}
            className="absolute inset-x-0 bottom-0"
            style={{
              height: CARD_HEIGHT,
              transformOrigin: 'center bottom',
              zIndex: leaving ? DEPTH + 1 : DEPTH - position,
            }}
            initial={
              reduced
                ? false
                : {
                    opacity: 0,
                    y: -(DEPTH - 1) * SLOT_RISE - 8,
                    scale: 1 - (DEPTH - 1) * SLOT_SCALE,
                  }
            }
            animate={
              leaving
                ? { opacity: 0, y: EXIT_DROP, scale: 0.97 }
                : {
                    opacity: SLOT_OPACITY[position],
                    y: -position * SLOT_RISE,
                    scale: 1 - position * SLOT_SCALE,
                  }
            }
            transition={
              leaving
                ? { duration: 0.45, ease: 'easeOut' }
                : { duration: 0.55, ease: 'easeOut', delay: position * SLOT_LAG }
            }
          >
            <Glass radius={12} elevated glow={false} className="h-full">
              <div className="flex flex-1 items-center gap-3 px-3.5">
                <span
                  className="glass-chip grid size-9 shrink-0 place-items-center rounded-[10px]"
                  style={{
                    color: tone,
                    background: `color-mix(in srgb, ${tone} 14%, transparent)`,
                  }}
                >
                  <Icon className="size-4" strokeWidth={2.4} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="text-foreground block truncate text-[13px] font-medium tracking-tight">
                    {headline}
                  </span>
                  {detail ? (
                    <span className="text-muted-foreground font-dm-mono mt-0.5 block truncate text-[11px]">
                      {detail}
                    </span>
                  ) : null}
                </span>
              </div>
            </Glass>
          </motion.div>
        );
      })}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*                                 Live mark                                  */
/* -------------------------------------------------------------------------- */

/**
 * Status marker for the header. Cobalt rather than green: green is reserved for
 * a movement that is good news, this only says the index is receiving.
 */
function LiveMark() {
  const reduced = useReducedMotion();

  return (
    <span className="glass-chip mt-0.5 flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1">
      <span className="relative grid size-1.5 shrink-0 place-items-center">
        {reduced ? null : (
          <motion.span
            aria-hidden
            className="absolute inset-0 rounded-full"
            style={{ background: 'var(--cd-accent)' }}
            animate={{ scale: [1, 2.4], opacity: [0.5, 0] }}
            transition={{ duration: 2.4, ease: 'easeOut', repeat: Infinity, repeatDelay: 0.6 }}
          />
        )}
        <span className="size-1.5 rounded-full" style={{ background: 'var(--cd-accent)' }} />
      </span>
      <span className="text-muted-foreground font-dm-mono text-[10px] tracking-[0.08em] uppercase">
        {LIVE_LABEL}
      </span>
    </span>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

/**
 * Header, stack and stamp reveal in reading order off a single observer, so the
 * three bands cannot fire out of order the way three separate ones would when
 * the card is scrolled into view from below.
 */
const CARD_REVEAL: Variants = {
  hidden: {},
  shown: { transition: { delayChildren: 0.12, staggerChildren: 0.08 } },
};

const BAND_REVEAL: Variants = {
  hidden: { opacity: 0, y: 8 },
  shown: { opacity: 1, y: 0, transition: { duration: 0.45, ease: 'easeOut' } },
};

export function ProgressTrackingCard() {
  const reduced = useReducedMotion();
  const [seen, setSeen] = useState(false);

  return (
    <Glass radius={16} interactive className="col-span-1 min-h-(--box-min-height) lg:col-span-2">
      <motion.div
        className="flex min-h-0 flex-1 flex-col gap-4 p-4"
        variants={CARD_REVEAL}
        initial={reduced ? 'shown' : 'hidden'}
        whileInView="shown"
        viewport={{ once: true, amount: 0.3 }}
        onViewportEnter={() => setSeen(true)}
      >
        <motion.div variants={BAND_REVEAL} className="flex items-start justify-between gap-3">
          <h3 className="text-foreground -tracking-xs text-base leading-5 font-medium text-balance">
            {BENTO.movements.title}
          </h3>
          <LiveMark />
        </motion.div>

        <motion.div variants={BAND_REVEAL} className="flex min-h-0 flex-1 items-center">
          <MovementStack active={seen} />
        </motion.div>

        <motion.div
          variants={BAND_REVEAL}
          className="pt-3"
          style={{ borderTop: '1px solid var(--cd-glass-border)' }}
        >
          <span className="text-muted-foreground font-dm-mono -tracking-xs block truncate text-[11px]">
            {BRAND.indexStamp}
          </span>
        </motion.div>
      </motion.div>
    </Glass>
  );
}
