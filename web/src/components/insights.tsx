import { useLayoutEffect, useRef, useState } from 'react';
import { motion, useAnimationFrame, useInView, useMotionValue, useReducedMotion } from 'motion/react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { Glass } from '@/components/ui/glass';
import {
  CAPABILITIES,
  CAPABILITIES_CTA,
  CAPABILITIES_HEADING,
  type Capability,
} from '@/content/site';

/**
 * The guarantees behind the index, on a belt that never stops.
 *
 * The old carousel hid four of the five cards behind 8px dots. A promise called
 * "un índice que no se cae" cannot be delivered by a control you have to hunt
 * for, so the cards now travel on their own: every one of them reaches the
 * reader without a single click, and the arrows are there for the reader who
 * wants to lead instead of follow.
 */

/* ---------------------------------------------------------------- copy add */

/**
 * Two strings the content module does not carry, because the belt did not exist
 * when it was written. Same voice as `BRAND_WALL.hint`: tell the reader what the
 * surface does, in the words a dealer would use.
 */
const RAIL_HINT = 'Pasa el cursor para pararlo';
const RAIL_PAUSED = 'En pausa';

/* -------------------------------------------------------------- mechanics */

/** px/s the belt travels when nothing is holding it — slow enough to ignore. */
const DRIFT_SPEED = 34;
/** Two sets cover the 1440px container; the third is headroom for ultra-wide. */
const COPIES = 3;
/** Cards dissolve into the gutter instead of being guillotined by the overflow. */
const EDGE_FADE = 'linear-gradient(90deg, transparent 0, #000 6%, #000 94%, transparent 100%)';

/** Keeps the track inside `(-setWidth, 0]`, the one interval that loops seamlessly. */
function wrapX(value: number, width: number) {
  if (width <= 0) return value;
  return -(((-value % width) + width) % width);
}

/* ------------------------------------------------------------------ glyphs */

/**
 * One mark per guarantee. A single repeated check said nothing about which card
 * you were reading; these are recognisable at a glance and survive the loop.
 */
const GLYPH_FALLBACK = <rect x="4" y="4" width="16" height="16" rx="5" />;

const GLYPHS: Record<string, React.ReactNode> = {
  // Coverage: a place on the map, and the ring around what is not closed yet.
  cobertura: (
    <>
      <path d="M12 21c4.4-4.6 6.6-8 6.6-10.6A6.6 6.6 0 0 0 5.4 10.4C5.4 13 7.6 16.4 12 21Z" />
      <circle cx="12" cy="10.3" r="2.4" />
    </>
  ),
  // Contrast: two readings travelling in opposite directions to meet.
  contraste: (
    <>
      <path d="M4 8.5h11M12 5.5l3 3-3 3" />
      <path d="M20 15.5H9M12 12.5l-3 3 3 3" />
    </>
  ),
  // History: the clock, kept.
  historial: (
    <>
      <circle cx="12" cy="12" r="8.4" />
      <path d="M12 7.2V12l3.2 1.9" />
    </>
  ),
  // Alerts: the flat line that spikes when something breaks.
  alertas: <path d="M3 12h3.6l2.5-6 3.8 12 2.6-6H21" />,
  // API: your own system, on the other side of the brackets.
  api: (
    <>
      <path d="M8.6 7.4 4 12l4.6 4.6" />
      <path d="M15.4 7.4 20 12l-4.6 4.6" />
      <path d="M13.4 5.6 10.6 18.4" />
    </>
  ),
};

function CapabilityGlyph({ id }: { id: string }) {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      {GLYPHS[id] ?? GLYPH_FALLBACK}
    </svg>
  );
}

/* -------------------------------------------------------------------- card */

type CardProps = {
  capability: Capability;
  index: number;
  reduced: boolean;
  /** Only the first set plays the entrance; the copies are off-screen when it runs. */
  entrance: boolean;
  revealed: boolean;
};

function CapabilityCard({ capability, index, reduced, entrance, revealed }: CardProps) {
  const plays = entrance && !reduced;
  const position = String(index + 1).padStart(2, '0');
  const total = String(CAPABILITIES.length).padStart(2, '0');

  return (
    <motion.article
      className="h-[18.5rem] w-[19.5rem] shrink-0 md:h-[19.5rem] md:w-[23rem]"
      initial={plays ? { opacity: 0, y: 20 } : false}
      animate={plays && revealed ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.6, delay: index * 0.08, ease: 'easeOut' }}
      whileHover={reduced ? undefined : { y: -4 }}
    >
      <Glass radius={20} elevated interactive className="group h-full">
        <div className="flex h-full flex-col p-6 md:p-7">
          <div className="flex items-start justify-between gap-4">
            <span
              className="glass-chip grid size-11 shrink-0 place-items-center rounded-[14px]"
              style={{ color: 'var(--cd-accent)' }}
            >
              <CapabilityGlyph id={capability.id} />
            </span>
            <span className="font-dm-mono text-muted-foreground text-[11px] tracking-[0.18em]">
              {position} / {total}
            </span>
          </div>

          {/* Fills while the card holds the belt still — the feedback for the pause. */}
          <span
            aria-hidden
            className="bg-primary/60 mt-5 block h-px w-full origin-left scale-x-0 transition-transform duration-500 ease-out group-hover:scale-x-100"
          />

          <div className="mt-auto flex flex-col gap-3 pt-8">
            <span
              className="font-dm-mono text-[11px] uppercase tracking-[0.16em]"
              style={{ color: 'var(--cd-on-accent-soft)' }}
            >
              {capability.mark}
            </span>
            <h3 className="text-foreground -tracking-sm text-lg leading-7 font-semibold md:text-xl">
              {capability.title}
            </h3>
            <p className="text-muted-foreground text-base leading-6">{capability.body}</p>
          </div>
        </div>
      </Glass>
    </motion.article>
  );
}

/* ---------------------------------------------------------------- controls */

function RailButton({
  label,
  direction,
  reduced,
  onClick,
}: {
  label: string;
  direction: 'prev' | 'next';
  reduced: boolean;
  onClick: () => void;
}) {
  return (
    <motion.button
      type="button"
      aria-label={label}
      onClick={onClick}
      whileHover={reduced ? undefined : { y: -2 }}
      whileTap={{ scale: 0.94 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="glass-chip text-foreground hover:text-primary focus-visible:ring-primary grid size-11 shrink-0 cursor-pointer place-items-center rounded-full outline-none transition-colors duration-300 focus-visible:ring-2"
    >
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden
      >
        <path d={direction === 'prev' ? 'M14 6 8 12l6 6' : 'M10 6l6 6-6 6'} />
      </svg>
    </motion.button>
  );
}

/* ----------------------------------------------------------------- section */

export function Insights() {
  const reduced = useReducedMotion() ?? false;
  const railRef = useRef<HTMLDivElement>(null);
  const setRef = useRef<HTMLDivElement>(null);

  // Two observers, two jobs: one arms the entrance once, the other keeps the
  // belt still while the section is off-screen so it is where you left it.
  const revealed = useInView(railRef, { once: true, amount: 0.3 });
  const onScreen = useInView(railRef, { amount: 0.15 });

  const [paused, setPaused] = useState(false);

  const x = useMotionValue(0);
  const progress = useMotionValue(0);
  const widthRef = useRef(0);
  const speedRef = useRef(0);
  /** px still owed to the belt by an arrow press, spent over the next frames. */
  const nudgeRef = useRef(0);

  useLayoutEffect(() => {
    const node = setRef.current;
    if (!node) return;

    // Card widths are responsive, so the loop distance is measured, not assumed.
    const measure = () => {
      widthRef.current = node.getBoundingClientRect().width;
    };

    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  useAnimationFrame((_timestamp, delta) => {
    const width = widthRef.current;
    if (!width) return;

    // A backgrounded tab hands back a huge delta; clamp it or the belt teleports.
    const seconds = Math.min(delta, 64) / 1000;
    const target = paused || reduced || !onScreen ? 0 : DRIFT_SPEED;
    speedRef.current += (target - speedRef.current) * Math.min(1, seconds * 5);
    if (Math.abs(speedRef.current) < 0.05) speedRef.current = 0;

    let travel = speedRef.current * seconds;

    // Arrow presses are spent as momentum, not as a jump cut: the belt
    // accelerates, carries you one card along and settles back into its drift.
    const pending = nudgeRef.current;
    if (pending !== 0) {
      const taken = reduced || Math.abs(pending) < 0.5 ? pending : pending * (1 - Math.exp(-seconds * 6.5));
      nudgeRef.current = pending - taken;
      travel += taken;
    }

    if (travel === 0) return;
    const next = wrapX(x.get() - travel, width);
    x.set(next);
    progress.set(-next / width);
  });

  const step = (direction: 1 | -1) => {
    const width = widthRef.current;
    if (!width) return;
    nudgeRef.current += (direction * width) / CAPABILITIES.length;
  };

  return (
    <section className="w-full">
      <Container className="flex flex-col gap-12 py-20 md:gap-16 md:py-30">
        <motion.div
          initial={reduced ? false : { opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="flex flex-col items-center justify-between gap-8 text-center md:items-start md:text-left lg:flex-row lg:items-center"
        >
          <h2 className="text-heading -tracking-lg text-4xl font-semibold md:text-5xl">
            {CAPABILITIES_HEADING}
          </h2>
          <Button avatar="/shots/mark.webp">{CAPABILITIES_CTA}</Button>
        </motion.div>

        <div className="flex flex-col gap-8">
          <motion.div
            ref={railRef}
            initial={reduced ? false : { opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            onMouseEnter={() => setPaused(true)}
            onMouseLeave={() => setPaused(false)}
            className="relative -mx-4 overflow-hidden py-6 sm:-mx-6 lg:-mx-8"
            style={{ WebkitMaskImage: EDGE_FADE, maskImage: EDGE_FADE }}
          >
            <motion.div
              className="flex w-max pl-4 will-change-transform sm:pl-6 lg:pl-8"
              style={{ x }}
            >
              {Array.from({ length: COPIES }, (_, copy) => (
                <div
                  key={copy}
                  ref={copy === 0 ? setRef : undefined}
                  aria-hidden={copy > 0}
                  className="flex shrink-0 gap-6 pr-6"
                >
                  {CAPABILITIES.map((capability, index) => (
                    <CapabilityCard
                      key={`${copy}-${capability.id}`}
                      capability={capability}
                      index={index}
                      reduced={reduced}
                      entrance={copy === 0}
                      revealed={revealed}
                    />
                  ))}
                </div>
              ))}
            </motion.div>
          </motion.div>

          <motion.div
            initial={reduced ? false : { opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.5, delay: 0.12, ease: 'easeOut' }}
            className="flex flex-col items-center gap-4"
          >
            <div className="flex items-center gap-4 sm:gap-5">
              <RailButton
                label="Ver la tarjeta anterior"
                direction="prev"
                reduced={reduced}
                onClick={() => step(-1)}
              />
              {/* Where the belt is inside its loop — the dots said the same thing
                  in five discrete steps and asked to be clicked. */}
              <div
                className="relative h-1 w-28 overflow-hidden rounded-full sm:w-44"
                style={{
                  background: 'var(--cd-line)',
                  opacity: paused ? 0.5 : 1,
                  transition: 'opacity 300ms ease',
                }}
              >
                <motion.span
                  aria-hidden
                  className="bg-primary absolute inset-y-0 left-0 w-full origin-left rounded-full"
                  style={{ scaleX: progress }}
                />
              </div>
              <RailButton
                label="Ver la tarjeta siguiente"
                direction="next"
                reduced={reduced}
                onClick={() => step(1)}
              />
            </div>

            <span
              className="font-dm-mono text-xs transition-colors duration-300"
              style={{ color: paused ? 'var(--cd-accent)' : 'var(--cd-fg-subtle)' }}
            >
              {paused ? RAIL_PAUSED : RAIL_HINT}
            </span>
          </motion.div>
        </div>
      </Container>
    </section>
  );
}
