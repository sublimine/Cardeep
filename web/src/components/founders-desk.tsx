import { Fragment } from 'react';
import Marquee from 'react-fast-marquee';
import { motion, useReducedMotion, type Variants } from 'motion/react';

import { Container } from '@/components/ui/container';
import { Glass } from '@/components/ui/glass';
import { MISSION, SOURCES } from '@/content/site';

/**
 * The mission, anchored at `#mision`.
 *
 * The section used to be the page's one hardcoded black band with a screenshot of
 * a map dropped into it. Both are gone: the ground is the theme's, and the proof
 * is built here — the three figures rise inside a glass panel that sits over a
 * field of points, a few of which keep lighting up. It is the same argument the
 * map made (a country covered point by point) without borrowing an image for it.
 */

/* ---------------------------------------------------------------- copy add */

/**
 * One string the content module does not carry. The marquee ran unlabelled, so
 * six platform marks under a mission statement read as customers. Same voice as
 * the section: what we do, in the words a dealer would use.
 */
const SOURCES_LABEL = 'Los sitios que miramos cada día';

/** The heading rises word by word, in reading order. */
const KICKER_WORDS = MISSION.kicker.split(' ');

/* -------------------------------------------------------------- mechanics */

const EASE_OUT = 'easeOut';
/** Expo-out: long tail, no overshoot — figures settle instead of arriving. */
const EASE_EXPO: [number, number, number, number] = [0.16, 1, 0.3, 1];

/** Lattice pitch in px. The painted field and the lit points share it. */
const CELL = 26;
/**
 * The field is drawn larger than the panel so its slow drift never walks an edge
 * into view. A whole number of cells, so the painted lattice and the lit points
 * stay in phase — with any other bleed the two grids would sit 13px apart.
 */
const BLEED = CELL * 2;
const LIT_SIZE = 5;

/**
 * The points that light up, in lattice cells from the panel's top-left. Placed by
 * hand rather than generated: no two neighbours fire together, the left half stays
 * populated for narrow panels, and the diagonal delay below turns the set into a
 * slow sweep across the field instead of random blinking.
 */
const LIT_POINTS = [
  { c: 1, r: 2 },
  { c: 4, r: 6 },
  { c: 2, r: 9 },
  { c: 6, r: 1 },
  { c: 7, r: 11 },
  { c: 9, r: 4 },
  { c: 11, r: 8 },
  { c: 12, r: 2 },
  { c: 5, r: 13 },
  { c: 10, r: 12 },
  { c: 15, r: 5 },
  { c: 17, r: 9 },
  { c: 19, r: 3 },
  { c: 21, r: 11 },
] as const;

/** Accent at partial strength: one value, correct in both themes, because the
    accent token itself already changes with the theme. */
const DOT_INK = 'color-mix(in oklab, var(--cd-accent) 52%, transparent)';
const DOT_GLOW = 'color-mix(in oklab, var(--cd-accent) 45%, transparent)';
const FIELD_MASK = 'radial-gradient(68% 66% at 50% 42%, #000 12%, transparent 88%)';
const EDGE_FADE = 'linear-gradient(90deg, transparent 0, #000 7%, #000 93%, transparent 100%)';

/* --------------------------------------------------------------- variants */

const groupVariants: Variants = {
  hidden: {},
  show: { transition: { delayChildren: 0.05, staggerChildren: 0.07 } },
};

const fadeUpVariants: Variants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.55, ease: EASE_OUT } },
};

const fadeVariants: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 0.5, ease: EASE_OUT } },
};

const wordVariants: Variants = {
  hidden: { y: '110%' },
  show: { y: '0%', transition: { duration: 0.65, ease: EASE_EXPO } },
};

const ruleVariants: Variants = {
  hidden: { scaleX: 0 },
  show: { scaleX: 1, transition: { duration: 0.7, ease: EASE_OUT } },
};

/** The panel arrives, then hands the reveal to its three figures. */
const panelVariants: Variants = {
  hidden: { opacity: 0, y: 26 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.65, ease: EASE_OUT, delayChildren: 0.2, staggerChildren: 0.14 },
  },
};

const figureVariants: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.04 } },
};

const charVariants: Variants = {
  hidden: { y: '115%' },
  show: { y: '0%', transition: { duration: 0.62, ease: EASE_EXPO } },
};

/* ------------------------------------------------------------------ field */

/**
 * The ground the figures stand on: a painted lattice of accent points, drifting
 * one cell at a time, with fourteen of them waking up in a diagonal sweep. The
 * drift is slow enough to be ignored and the mask keeps it away from the glass
 * edges, where it would read as texture instead of as a country.
 */
function DotField({ reduced }: { reduced: boolean }) {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
      <motion.div
        className="absolute"
        style={{
          inset: -BLEED,
          backgroundImage: `radial-gradient(circle, ${DOT_INK} 1.4px, transparent 1.6px)`,
          backgroundSize: `${CELL}px ${CELL}px`,
          maskImage: FIELD_MASK,
          WebkitMaskImage: FIELD_MASK,
        }}
        animate={reduced ? undefined : { x: [0, CELL, 0], y: [0, -CELL, 0] }}
        transition={{ duration: 46, repeat: Infinity, ease: 'easeInOut' }}
      >
        {LIT_POINTS.map(({ c, r }) => {
          // Both derived from the cell, so the sweep is deterministic: points on
          // the same diagonal fire together, and the period varies just enough
          // that the field never falls into lockstep.
          const delay = ((c + r) % 6) * 0.62;
          const cycle = 2.9 + ((c * 7 + r * 3) % 5) * 0.32;

          return (
            <motion.span
              key={`${c}-${r}`}
              className="absolute block rounded-full"
              style={{
                left: BLEED + CELL / 2 + c * CELL,
                top: BLEED + CELL / 2 + r * CELL,
                width: LIT_SIZE,
                height: LIT_SIZE,
                marginLeft: -LIT_SIZE / 2,
                marginTop: -LIT_SIZE / 2,
                background: 'var(--cd-accent)',
                boxShadow: `0 0 12px 2px ${DOT_GLOW}`,
              }}
              // `initial={false}` would resolve a keyframe array to its last value
              // and skip the loop entirely, so the moving path declares its start.
              initial={reduced ? false : { opacity: 0, scale: 0.45 }}
              animate={
                reduced ? { opacity: 0.45, scale: 1 } : { opacity: [0, 0.95, 0], scale: [0.45, 1, 0.45] }
              }
              transition={
                reduced
                  ? { duration: 0 }
                  : { duration: cycle, delay, repeat: Infinity, repeatDelay: 3.1, ease: 'easeInOut' }
              }
            />
          );
        })}
      </motion.div>
    </div>
  );
}

/* ---------------------------------------------------------------- figures */

type FigureProps = {
  value: string;
  label: string;
  /** The first figure opens the stack, so it carries no divider above it. */
  first: boolean;
};

/**
 * One figure. The value is split so it can rise digit by digit out of its own clip
 * box; the split is hidden from assistive tech and the whole line is announced once.
 */
function Figure({ value, label, first }: FigureProps) {
  return (
    <motion.div className="group flex flex-col gap-4" variants={figureVariants}>
      {first ? null : (
        <motion.span
          aria-hidden
          className="relative block h-px w-full origin-left"
          style={{ background: 'var(--cd-line)' }}
          variants={ruleVariants}
        >
          {/* Hover feedback: the divider under the figure you are reading fills
              with accent, left to right. */}
          <span className="bg-primary absolute inset-0 origin-left scale-x-0 transition-transform duration-500 ease-out group-hover:scale-x-100" />
        </motion.span>
      )}

      {/* Below `sm` the widest figure and its label cannot share a line, and one
          row wrapping while the other two did not read as a mistake. So all three
          stack there and all three sit on one baseline above it. */}
      <div className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between sm:gap-x-5">
        <span className="sr-only">{`${value} ${label}`}</span>

        <span
          aria-hidden
          className="text-heading -tracking-xl block text-5xl leading-none font-medium md:text-6xl"
          style={{ fontVariantNumeric: 'tabular-nums' }}
        >
          {[...value].map((char, index) => (
            // The clip box carries bottom padding so nothing is shaved off, and an
            // equal negative margin so the line height is unchanged.
            <span
              key={`${char}-${index}`}
              className="-mb-[0.14em] inline-block overflow-hidden pb-[0.14em] align-bottom"
            >
              <motion.span className="inline-block" variants={charVariants}>
                {/* A lone space would be the only content of its clip box and collapse to
                    nothing, printing `1,5M`; the no-break space keeps its width. */}
                {char === ' ' ? '\u00A0' : char}
              </motion.span>
            </span>
          ))}
        </span>

        <motion.span
          aria-hidden
          className="font-dm-mono text-muted-foreground group-hover:text-foreground text-xs tracking-[0.14em] uppercase transition-colors duration-300"
          variants={fadeVariants}
        >
          {label}
        </motion.span>
      </div>
    </motion.div>
  );
}

/* ---------------------------------------------------------------- section */

export function FoundersDesk() {
  const reduced = useReducedMotion();

  return (
    <section id="mision" className="relative w-full overflow-hidden">
      <Container className="relative z-10 flex w-full flex-col gap-12 py-20 md:gap-16 md:py-30">
        <motion.div
          className="flex flex-col gap-6"
          variants={groupVariants}
          initial={reduced ? 'show' : 'hidden'}
          whileInView="show"
          viewport={{ once: true, amount: 0.5 }}
        >
          <h2 className="text-heading -tracking-lg text-4xl font-semibold text-balance md:text-5xl">
            {KICKER_WORDS.map((word, index) => (
              // The word space is a real text node between the clip boxes rather
              // than a margin: a margin looks identical but leaves the heading
              // reading "Lamisión" to a screen reader and to anyone copying it.
              <Fragment key={`${word}-${index}`}>
                {index > 0 ? ' ' : null}
                <span className="-mb-[0.16em] inline-block overflow-hidden pb-[0.16em] align-bottom">
                  <motion.span className="inline-block" variants={wordVariants}>
                    {word}
                  </motion.span>
                </span>
              </Fragment>
            ))}
          </h2>

          {/* Section rule: accent at the origin, dissolving into the hairline. */}
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

        <div className="grid grid-cols-1 items-stretch gap-10 lg:grid-cols-12 lg:gap-14">
          <motion.div
            className="flex flex-col justify-center gap-7 lg:col-span-6"
            variants={groupVariants}
            initial={reduced ? 'show' : 'hidden'}
            whileInView="show"
            viewport={{ once: true, amount: 0.3 }}
          >
            <motion.p
              className="text-foreground -tracking-xs text-lg leading-7 md:text-xl md:leading-8"
              variants={fadeUpVariants}
            >
              {MISSION.paragraphs[0]}
            </motion.p>

            <motion.p
              className="text-muted-foreground -tracking-xs text-base leading-7 md:text-lg md:leading-7"
              variants={fadeUpVariants}
            >
              {MISSION.paragraphs[1]}
            </motion.p>

            {/* The closing line is the claim the section is judged on, so it gets
                the accent rule and the ink weight the body does not. */}
            <motion.p
              className="border-primary text-foreground -tracking-xs border-l-2 pl-5 text-base leading-7 font-medium md:text-lg"
              variants={fadeUpVariants}
            >
              {MISSION.closing}
            </motion.p>
          </motion.div>

          <motion.div
            className="relative lg:col-span-6"
            variants={panelVariants}
            initial={reduced ? 'show' : 'hidden'}
            whileInView="show"
            viewport={{ once: true, amount: 0.3 }}
          >
            {/* Glass only looks like glass when there is something behind it to
                refract, so the panel gets its own slow light source. */}
            <motion.div
              aria-hidden
              className="pointer-events-none absolute -inset-6 z-0 rounded-[2.25rem]"
              style={{
                background:
                  'radial-gradient(58% 54% at 30% 22%, var(--cd-aurora-1), transparent 70%), radial-gradient(50% 46% at 78% 82%, var(--cd-aurora-2), transparent 72%)',
                filter: 'blur(18px)',
              }}
              animate={reduced ? undefined : { opacity: [0.72, 1, 0.72], scale: [1, 1.04, 1] }}
              transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
            />

            <Glass radius={24} elevated interactive className="relative z-10 h-full">
              <div className="relative flex h-full min-h-[22rem] flex-col justify-between gap-6 p-7 md:gap-8 md:p-9">
                <DotField reduced={reduced ?? false} />

                <div className="relative z-10 flex h-full flex-col justify-between gap-6 md:gap-8">
                  {MISSION.stats.map(({ value, label }, index) => (
                    <Figure key={label} value={value} label={label} first={index === 0} />
                  ))}
                </div>
              </div>
            </Glass>
          </motion.div>
        </div>

        <motion.div
          className="flex flex-col gap-5"
          initial={reduced ? false : { opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.55, ease: EASE_OUT }}
        >
          <span className="font-dm-mono text-subtle text-xs tracking-[0.14em] uppercase">
            {SOURCES_LABEL}
          </span>

          <div
            className="relative w-full overflow-hidden"
            style={{ maskImage: EDGE_FADE, WebkitMaskImage: EDGE_FADE }}
          >
            {/* `gradient` off: its overlay is painted in a fixed colour, which
                would strand the fade on one of the two themes. The mask above
                does the same job and inverts for free. */}
            <Marquee speed={38} autoFill gradient={false} pauseOnHover play={!reduced}>
              {SOURCES.map(({ name, logo }) => (
                <div key={name} className="mx-2 py-1">
                  <SourceMark name={name} logo={logo} />
                </div>
              ))}
            </Marquee>
          </div>
        </motion.div>
      </Container>
    </section>
  );
}

type SourceMarkProps = {
  name: string;
  logo: string;
};

/** One indexed platform: its mark and its name, on a glass chip that lifts when
    the reader stops the belt on it. */
function SourceMark({ name, logo }: SourceMarkProps) {
  return (
    <div className="glass group flex items-center gap-2.5 rounded-xl px-5 py-3 transition-transform duration-300 hover:-translate-y-0.5">
      <img
        src={logo}
        alt=""
        aria-hidden
        width={128}
        height={128}
        loading="lazy"
        decoding="async"
        className="size-5 rounded-md object-contain transition-transform duration-300 group-hover:scale-110"
      />
      <span className="text-foreground -tracking-xs text-sm leading-5 font-medium">{name}</span>
    </div>
  );
}
