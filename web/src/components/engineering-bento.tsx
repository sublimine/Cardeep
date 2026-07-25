import type { ReactNode } from 'react';
import { motion, useReducedMotion, type Variants } from 'motion/react';

import { Container } from '@/components/ui/container';
import { BENTO, BRAND } from '@/content/site';
import { cn } from '@/lib/utils';
import { DesignDevelopmentCard } from '@/components/bento/design-development-card';
import { ProgressTrackingCard } from '@/components/bento/progress-tracking-card';
import { HostingMapCard } from '@/components/bento/hosting-map-card';
import { GoogleSearchCard } from '@/components/bento/google-search-card';
import { ComponentsCard } from '@/components/bento/components-card';

/**
 * Product bento, anchored at `#producto` for the navbar link.
 *
 * Two strings below are written here rather than in `@/content/site`: `BENTO`
 * carries the heading and the five card bodies but no kicker and no standfirst,
 * and the section needs both to open instead of starting mid-sentence.
 */
const KICKER = 'Dentro de Cardeep';
const STANDFIRST =
  'Cinco vistas del mismo mercado: quién vende, qué tiene, a qué precio y desde cuándo.';

/** Words rise out of their own clip box, in reading order. */
const HEADING_WORDS = BENTO.heading.split(' ');

const EASE_OUT = 'easeOut';
/** Expo-out: long tail, no overshoot — the words settle instead of arriving. */
const EASE_EXPO: [number, number, number, number] = [0.16, 1, 0.3, 1];

/**
 * One `whileInView` on the header block drives every part of it; the children
 * inherit the state through context and the stagger orders them, so the reveal
 * follows the hierarchy — kicker, heading, standfirst, stamp, rule.
 */
const headerVariants: Variants = {
  hidden: {},
  show: { transition: { delayChildren: 0.05, staggerChildren: 0.05 } },
};

const fadeUpVariants: Variants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.55, ease: EASE_OUT } },
};

const wordVariants: Variants = {
  hidden: { y: '110%' },
  show: { y: '0%', transition: { duration: 0.65, ease: EASE_EXPO } },
};

const ruleVariants: Variants = {
  hidden: { scaleX: 0 },
  show: { scaleX: 1, transition: { duration: 0.8, ease: EASE_OUT } },
};

/**
 * The stamp says the index is current, so the dot has to behave like a status
 * light: one slow breath, quiet enough to sit next to text and be ignored.
 */
function LiveDot() {
  const reduced = useReducedMotion();

  return (
    <span className="relative flex size-1.5 shrink-0">
      {reduced ? null : (
        <motion.span
          aria-hidden
          className="bg-primary absolute inset-0 rounded-full"
          animate={{ scale: [1, 2.6, 1], opacity: [0.45, 0, 0.45] }}
          transition={{ duration: 2.8, repeat: Infinity, ease: EASE_OUT }}
        />
      )}
      <span className="bg-primary relative size-1.5 rounded-full" />
    </span>
  );
}

/**
 * Grid position lives on the slot, not on the card inside it.
 *
 * The wrapper is what animates, so it has to be the grid item; `display: grid`
 * makes the card stretch to the slot on both axes exactly as it did when it was
 * the item itself, and `min-w-0` keeps a card's wide internals from forcing the
 * track open.
 */
function Slot({ index, className, children }: { index: number; className: string; children: ReactNode }) {
  const reduced = useReducedMotion();

  return (
    <motion.div
      className={cn('grid min-w-0', className)}
      initial={reduced ? false : { opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.6, delay: index * 0.09, ease: EASE_OUT }}
    >
      {children}
    </motion.div>
  );
}

export function EngineeringBento() {
  const reduced = useReducedMotion();

  return (
    <section id="producto" className="relative w-full">
      <Container className="flex flex-col gap-12 py-20 md:gap-16 md:py-28">
        <motion.div
          className="flex flex-col gap-8"
          variants={headerVariants}
          initial={reduced ? 'show' : 'hidden'}
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
        >
          <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
            <div className="flex max-w-3xl flex-col gap-4">
              <motion.span
                className="font-dm-mono text-muted-foreground -tracking-xs text-xs uppercase"
                variants={fadeUpVariants}
              >
                {KICKER}
              </motion.span>

              <h2 className="text-heading -tracking-lg text-4xl font-semibold text-balance md:text-5xl">
                {HEADING_WORDS.map((word, index) => (
                  // The clip box carries bottom padding so descenders survive it,
                  // and an equal negative margin so the line height is unchanged.
                  <span
                    key={`${word}-${index}`}
                    className="mr-[0.26em] -mb-[0.16em] inline-block overflow-hidden pb-[0.16em] align-bottom"
                  >
                    <motion.span className="inline-block" variants={wordVariants}>
                      {word}
                    </motion.span>
                  </span>
                ))}
              </h2>

              <motion.p
                className="text-muted-foreground -tracking-xs max-w-xl text-base leading-6 md:text-lg md:leading-7"
                variants={fadeUpVariants}
              >
                {STANDFIRST}
              </motion.p>
            </div>

            <motion.div
              className="glass-chip text-muted-foreground font-dm-mono -tracking-xs flex w-fit items-center gap-2 rounded-full px-3 py-1.5 text-xs md:mb-1"
              variants={fadeUpVariants}
            >
              <LiveDot />
              {BRAND.indexStamp}
            </motion.div>
          </div>

          {/* Section rule: cobalt at the origin, dissolving into the hairline —
              it draws from the left, which is where the cards start arriving. */}
          <motion.div
            aria-hidden
            className="h-px w-full origin-left"
            style={{
              background:
                'linear-gradient(90deg, var(--cd-accent) 0%, var(--cd-line) 18%, var(--cd-line) 100%)',
            }}
            variants={ruleVariants}
          />
        </motion.div>

        {/*
          The 19-column track: the feature card takes 6/19 and the four
          supporting cards share the remaining 13, collapsing to two columns and
          then one below `lg`. `--box-min-height` keeps those four on a common
          baseline height.
        */}
        <div className="grid grid-cols-19 gap-3">
          <Slot index={0} className="col-span-19 lg:col-span-6">
            <DesignDevelopmentCard />
          </Slot>

          <div className="col-span-19 grid grid-cols-1 gap-3 md:grid-cols-2 lg:col-span-13 lg:grid-cols-5 [--box-min-height:314px]">
            <Slot index={1} className="col-span-1 lg:col-span-2">
              <ProgressTrackingCard />
            </Slot>
            <Slot index={2} className="col-span-1 lg:col-span-3">
              <HostingMapCard />
            </Slot>
            <Slot index={3} className="col-span-1 lg:col-span-3">
              <GoogleSearchCard />
            </Slot>
            <Slot index={4} className="col-span-1 lg:col-span-2">
              <ComponentsCard />
            </Slot>
          </div>
        </div>
      </Container>
    </section>
  );
}
