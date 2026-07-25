import { useEffect, useMemo, useRef, useState } from 'react';
import {
  AnimatePresence,
  animate,
  motion,
  useInView,
  useMotionValue,
  useReducedMotion,
  useScroll,
  useTransform,
  type Variants,
} from 'motion/react';
import { ArrowRight } from 'lucide-react';

import { Container } from '@/components/ui/container';
import { Glass } from '@/components/ui/glass';
import { Logo } from '@/components/ui/logo';
import { BRAND, SURFACES, SURFACES_HEADING } from '@/content/site';
import { cn } from '@/lib/utils';

/**
 * The product tour: six surfaces of the platform, one at a time.
 *
 * Six tiles side by side ask the visitor to choose before they know what they
 * are choosing between, and each render ends up too small to read. So the
 * section is a single viewport instead: a rail of surface names drives one large
 * glass screen that cross-fades between the real interface renders, and the tour
 * advances on its own so a visitor who does nothing still sees all six.
 *
 * The countdown is visible — the active row fills with cobalt over its dwell —
 * because a thing that moves without warning reads as a glitch. Hovering holds
 * it; picking a surface hands over control for good and drains the fill.
 */

/** Seconds each surface holds the viewport before the tour moves on. */
const DWELL_SECONDS = 7;

/** `tags` is one string; the separator is the same middot used across the copy. */
const TAG_SEPARATOR = ' · ';

const detailGroup: Variants = {
  hidden: { transition: { staggerChildren: 0.04, staggerDirection: -1 } },
  visible: { transition: { staggerChildren: 0.07, delayChildren: 0.06 } },
};

function detailItemVariants(reduced: boolean): Variants {
  return {
    hidden: { opacity: 0, y: reduced ? 0 : 12, transition: { duration: 0.2, ease: 'easeOut' } },
    visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: 'easeOut' } },
  };
}

function railItemVariants(reduced: boolean): Variants {
  return {
    hidden: { opacity: 0, y: reduced ? 0 : 10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: 'easeOut' } },
  };
}

const railGroup: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.06 } },
};

/** `01`, `02`… — the position in the tour, not a claim about anything. */
function ordinal(value: number) {
  return String(value).padStart(2, '0');
}

export function Projects() {
  const reduced = useReducedMotion() ?? false;

  const sectionRef = useRef<HTMLElement>(null);
  const showcaseRef = useRef<HTMLDivElement>(null);
  const railRef = useRef<HTMLDivElement>(null);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const runRef = useRef<ReturnType<typeof animate> | null>(null);

  const [index, setIndex] = useState(0);
  /** Sticky: once the visitor picks a surface, the tour stops driving itself. */
  const [manual, setManual] = useState(false);
  /** Transient: pointer or keyboard focus inside the showcase. */
  const [held, setHeld] = useState(false);

  const progress = useMotionValue(0);
  const inView = useInView(showcaseRef, { amount: 0.3 });

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start end', 'end start'],
  });
  const watermarkY = useTransform(scrollYProgress, [0, 1], [28, -28]);

  const detailItem = useMemo(() => detailItemVariants(reduced), [reduced]);
  const railItem = useMemo(() => railItemVariants(reduced), [reduced]);

  const active = SURFACES[index];
  const tags = useMemo(() => active.tags.split(TAG_SEPARATOR), [active.tags]);

  // The dwell countdown lives on a motion value, so seven seconds of ticking
  // never re-renders the section — and pausing holds it exactly where it was.
  useEffect(() => {
    if (reduced || manual) {
      const drain = animate(progress, 0, { duration: 0.35, ease: 'easeOut' });
      return () => drain.stop();
    }

    progress.set(0);
    const run = animate(progress, 1, {
      duration: DWELL_SECONDS,
      ease: 'linear',
      onComplete: () => setIndex((current) => (current + 1) % SURFACES.length),
    });
    runRef.current = run;

    return () => {
      run.stop();
      runRef.current = null;
    };
  }, [index, manual, progress, reduced]);

  useEffect(() => {
    const run = runRef.current;
    if (!run) return;
    if (held || !inView) run.pause();
    else run.play();
  }, [held, index, inView, manual]);

  // Keep the selected tab in sight while the rail is a horizontal scroller.
  useEffect(() => {
    const rail = railRef.current;
    const tab = tabRefs.current[index];
    if (!rail || !tab) return;
    if (rail.scrollWidth <= rail.clientWidth) return;

    rail.scrollTo({
      left: Math.max(0, tab.offsetLeft - (rail.clientWidth - tab.clientWidth) / 2),
      behavior: reduced ? 'auto' : 'smooth',
    });
  }, [index, reduced]);

  const select = (next: number) => {
    setIndex(next);
    setManual(true);
  };

  const onRailKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const last = SURFACES.length - 1;
    let next: number | null = null;

    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
      next = index === last ? 0 : index + 1;
    } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
      next = index === 0 ? last : index - 1;
    } else if (event.key === 'Home') {
      next = 0;
    } else if (event.key === 'End') {
      next = last;
    }

    if (next === null) return;
    event.preventDefault();
    select(next);
    tabRefs.current[next]?.focus();
  };

  return (
    <section id="dentro" ref={sectionRef} className="relative w-full overflow-hidden">
      <Container className="relative flex flex-col py-24 md:py-32">
        {/* The heading is the watermark: one line, larger than anything else on
            the page, dissolving toward its own baseline. It drifts against the
            scroll so the showcase reads as sitting in front of it. */}
        <motion.div
          initial={reduced ? false : { opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <motion.h2
            className="-tracking-xl w-full font-semibold text-transparent select-none"
            style={{
              y: reduced ? 0 : watermarkY,
              fontSize: 'clamp(2.25rem, 9.6vw, 9.5rem)',
              lineHeight: 0.92,
              whiteSpace: 'nowrap',
              backgroundImage:
                'linear-gradient(180deg, color-mix(in oklab, var(--cd-fg) 34%, transparent) 0%, transparent 86%)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
            }}
          >
            {SURFACES_HEADING}
          </motion.h2>
        </motion.div>

        <div
          ref={showcaseRef}
          className="relative z-10 -mt-2 grid grid-cols-1 gap-8 md:-mt-6 lg:-mt-10 lg:grid-cols-12 lg:gap-10"
          onMouseEnter={() => setHeld(true)}
          onMouseLeave={() => setHeld(false)}
          onFocusCapture={() => setHeld(true)}
          onBlurCapture={(event) => {
            if (!event.currentTarget.contains(event.relatedTarget)) setHeld(false);
          }}
        >
          {/* Rail — a row of tabs on mobile, a column of names on desktop. One
              tablist either way, so the keyboard contract never changes. */}
          <motion.div
            ref={railRef}
            role="tablist"
            aria-label={SURFACES_HEADING}
            onKeyDown={onRailKeyDown}
            variants={railGroup}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="lg:border-line relative -mx-4 flex gap-2 overflow-x-auto px-4 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden lg:col-span-4 lg:mx-0 lg:flex-col lg:justify-center lg:gap-1 lg:overflow-x-visible lg:border-l lg:px-0 lg:pb-0"
          >
            {SURFACES.map((surface, position) => {
              const isActive = position === index;

              return (
                <motion.button
                  key={surface.id}
                  ref={(node) => {
                    tabRefs.current[position] = node;
                  }}
                  id={`surface-tab-${surface.id}`}
                  type="button"
                  role="tab"
                  aria-selected={isActive}
                  aria-controls="surface-panel"
                  tabIndex={isActive ? 0 : -1}
                  onClick={() => select(position)}
                  variants={railItem}
                  className="group relative shrink-0 cursor-pointer rounded-full px-4 py-2.5 text-left outline-none lg:w-full lg:rounded-2xl lg:px-5 lg:py-4"
                >
                  {isActive ? (
                    <>
                      {/* The pane slides between rows rather than blinking on,
                          so the eye follows the selection instead of hunting. */}
                      <motion.span
                        aria-hidden
                        layoutId="surface-tab-pane"
                        initial={false}
                        transition={
                          reduced
                            ? { duration: 0 }
                            : { type: 'spring', stiffness: 420, damping: 38, mass: 0.9 }
                        }
                        className="glass-chip absolute inset-0 rounded-full lg:rounded-2xl"
                      >
                        <span className="bg-primary absolute inset-y-3 left-0 hidden w-0.5 rounded-full lg:block" />
                      </motion.span>
                      {/* The dwell made visible: cobalt fills the row, then the
                          viewport changes. Nothing moves unannounced. The fill
                          is clipped by a wrapper so scaling it never drags the
                          corner radius out of shape. */}
                      <span
                        aria-hidden
                        className="absolute inset-0 overflow-hidden rounded-full lg:rounded-2xl"
                      >
                        <motion.span
                          initial={false}
                          style={{ scaleX: progress }}
                          className="bg-primary/12 absolute inset-0 origin-left"
                        />
                      </span>
                    </>
                  ) : null}

                  <span className="relative flex items-center gap-3">
                    <span
                      className={cn(
                        'font-dm-mono text-[11px] tabular-nums transition-colors duration-300',
                        isActive ? 'text-primary' : 'text-subtle',
                      )}
                    >
                      {ordinal(position + 1)}
                    </span>
                    <span
                      className={cn(
                        '-tracking-xs text-sm font-medium whitespace-nowrap transition-colors duration-300 lg:text-base',
                        isActive
                          ? 'text-foreground'
                          : 'text-muted-foreground group-hover:text-foreground',
                      )}
                    >
                      {surface.title}
                    </span>
                  </span>
                </motion.button>
              );
            })}
          </motion.div>

          <motion.div
            id="surface-panel"
            role="tabpanel"
            aria-labelledby={`surface-tab-${active.id}`}
            className="flex flex-col gap-8 lg:col-span-8"
            initial={reduced ? false : { opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.25 }}
            transition={{ duration: 0.6, delay: 0.08, ease: 'easeOut' }}
          >
            <Glass radius={24} elevated interactive className="w-full">
              <div
                className="flex items-center justify-between gap-4 px-4 py-3 sm:px-5"
                style={{ borderBottom: '1px solid var(--cd-glass-border)' }}
              >
                <span className="flex min-w-0 items-center gap-2">
                  <Logo className="text-primary size-4 shrink-0" />
                  <span className="font-dm-mono text-muted-foreground -tracking-xs truncate text-[11px]">
                    {BRAND.indexStamp}
                  </span>
                </span>
                <span className="font-dm-mono text-subtle shrink-0 text-[11px] tabular-nums">
                  {ordinal(index + 1)} / {ordinal(SURFACES.length)}
                </span>
              </div>

              {/* All six renders are stacked and cross-faded: no blank frame
                  while a file loads, and the outgoing screen falls back a
                  fraction as the incoming one settles. */}
              <div className="relative aspect-4/3 w-full sm:aspect-3/2">
                {SURFACES.map((surface, position) => {
                  const isActive = position === index;

                  return (
                    <motion.div
                      key={surface.id}
                      aria-hidden={!isActive}
                      className="pointer-events-none absolute inset-3 flex items-center justify-center sm:inset-5"
                      initial={false}
                      animate={{ opacity: isActive ? 1 : 0, scale: isActive ? 1 : 1.015 }}
                      transition={{ duration: reduced ? 0 : 0.55, ease: 'easeOut' }}
                    >
                      <img
                        src={surface.image}
                        alt={`Cardeep · ${surface.title}`}
                        loading="lazy"
                        decoding="async"
                        className="max-h-full max-w-full rounded-lg object-contain"
                        style={{
                          border: '1px solid var(--cd-glass-border)',
                          boxShadow: 'var(--cd-glass-shadow)',
                        }}
                      />
                    </motion.div>
                  );
                })}
              </div>
            </Glass>

            {/* Fixed floor so the copy swapping underneath never shifts the
                viewport above it. */}
            {/* Floors measured against the tallest of the six at 320, 360 and
                560px — the widths where the copy rewraps — so swapping the
                block never nudges the viewport above it. */}
            <div className="relative min-h-54 min-[360px]:min-h-44 min-[560px]:min-h-40">
              <AnimatePresence mode="wait" initial={false}>
                <motion.div
                  key={active.id}
                  variants={detailGroup}
                  initial="hidden"
                  animate="visible"
                  exit="hidden"
                  className="flex flex-col items-start gap-4"
                >
                  <motion.h3
                    variants={detailItem}
                    className="text-foreground -tracking-lg text-2xl font-semibold md:text-3xl"
                  >
                    {active.title}
                  </motion.h3>
                  <motion.p
                    variants={detailItem}
                    className="text-muted-foreground -tracking-xs max-w-xl text-base leading-6"
                  >
                    {active.body}
                  </motion.p>
                  <motion.div
                    variants={detailItem}
                    className="flex w-full flex-wrap items-center gap-2"
                  >
                    {tags.map((tag) => (
                      <span
                        key={tag}
                        className="glass-chip text-muted-foreground -tracking-xs rounded-full px-3 py-1.5 text-[11px] font-medium"
                      >
                        {tag}
                      </span>
                    ))}
                    <a
                      href={active.href}
                      aria-label={`Ver ${active.title}`}
                      className="group text-primary -tracking-xs ml-auto inline-flex items-center gap-1.5 text-sm font-medium transition-transform duration-200 hover:-translate-y-0.5"
                    >
                      Ver
                      <ArrowRight className="size-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
                    </a>
                  </motion.div>
                </motion.div>
              </AnimatePresence>
            </div>
          </motion.div>
        </div>
      </Container>
    </section>
  );
}
