import { motion, useReducedMotion, type Variants } from 'motion/react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { Glass } from '@/components/ui/glass';
import { PRINCIPLES, PRINCIPLES_CTA, PRINCIPLES_HEADING, type Principle } from '@/content/site';
import { cn } from '@/lib/utils';

/**
 * "Cómo trabajamos" — the five principles as a numbered manifesto.
 *
 * Not a carousel: an argument. The rules run down a single spine, every one of
 * them on screen without a control to press, and the cobalt hairline draws from
 * each number toward the next as you read, so the five read as one position
 * rather than five slides that happen to share a section.
 *
 * Two strings live here rather than in `@/content/site`: the module carries the
 * heading and the CTA but no kicker and no standfirst, and the section needs
 * both to open instead of starting mid-argument on the first rule.
 */
const KICKER = 'Cinco principios';
const STANDFIRST =
  'Las reglas que no negociamos. Son la razón por la que puedes fiarte de cada número que te enseñamos.';

const EASE_OUT = 'easeOut';
/** Expo-out: long tail, no overshoot — the words settle instead of arriving. */
const EASE_EXPO: [number, number, number, number] = [0.16, 1, 0.3, 1];

const HEADING_WORDS = PRINCIPLES_HEADING.split(' ');

/* ------------------------------------------------------------------ header */

const headerVariants: Variants = {
  hidden: {},
  show: { transition: { delayChildren: 0.05, staggerChildren: 0.06 } },
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

/* -------------------------------------------------------------- manifesto */

/**
 * One rule reveals as a chain, in the order it is read: the number, the panel
 * it belongs to, then the hairline that hands over to the next rule. The index
 * offsets the whole chain so rules that share a tall viewport still cascade
 * instead of landing together.
 */
const itemVariants: Variants = {
  hidden: {},
  show: (index: number) => ({
    transition: { delayChildren: index * 0.06, staggerChildren: 0.1 },
  }),
};

const markVariants: Variants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: EASE_OUT } },
};

const panelVariants: Variants = {
  hidden: { opacity: 0, y: 22 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: EASE_OUT } },
};

const trackVariants: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 0.4, ease: EASE_OUT } },
};

/** The cobalt draws downward, arriving as the next number comes into view. */
const drawVariants: Variants = {
  hidden: { scaleY: 0 },
  show: { scaleY: 1, transition: { duration: 0.85, delay: 0.2, ease: EASE_OUT } },
};

/**
 * Marks are always two digits. Dimming the leading zero keeps the counter
 * legible at display size without it shouting a digit nobody reads.
 */
function Mark({ mark }: { mark: string }) {
  const hasLeadingZero = mark.length > 1 && mark.startsWith('0');

  return (
    <>
      {hasLeadingZero ? (
        <span className="opacity-30 transition-opacity duration-300 group-hover:opacity-60">
          {mark.slice(0, 1)}
        </span>
      ) : null}
      {hasLeadingZero ? mark.slice(1) : mark}
    </>
  );
}

type PrincipleRowProps = {
  principle: Principle;
  index: number;
  isLast: boolean;
};

function PrincipleRow({ principle, index, isLast }: PrincipleRowProps) {
  const reduced = useReducedMotion();

  return (
    <motion.li
      className="group grid grid-cols-[var(--rail)_minmax(0,1fr)] grid-rows-[auto_1fr] gap-x-4 md:gap-x-7"
      custom={index}
      variants={itemVariants}
      initial={reduced ? 'show' : 'hidden'}
      whileInView="show"
      viewport={{ once: true, amount: 0.3 }}
    >
      {/*
        The ordinal is carried by the list itself, so the glyph is decoration for
        the eye only and stays out of the accessibility tree. Its top margin
        matches the panel's padding, which lands the digits' cap height on the
        title's: the number reads as that title's ordinal, not as a label
        floating above the panel.
      */}
      <motion.span
        aria-hidden
        variants={markVariants}
        className="text-primary font-dm-mono -tracking-sm col-start-1 row-start-1 mt-6 flex justify-center text-3xl leading-none font-medium md:mt-8 md:text-[2.75rem]"
      >
        <Mark mark={principle.mark} />
      </motion.span>

      <motion.div
        variants={panelVariants}
        whileHover={reduced ? undefined : { y: -3, transition: { duration: 0.25, ease: EASE_OUT } }}
        className={cn('col-start-2 row-start-1 row-span-2', isLast ? null : 'pb-5 md:pb-8')}
      >
        <Glass radius={20} interactive className="h-full">
          {/* Edge marker: it says which rule you are pointing at, the same
              gesture the comparison rows use. */}
          <span
            aria-hidden
            className="bg-primary pointer-events-none absolute inset-y-0 left-0 w-0.5 origin-center scale-y-0 transition-transform duration-300 group-hover:scale-y-100"
          />
          <div className="flex flex-col gap-3 p-6 md:gap-4 md:p-8">
            <h3 className="text-foreground -tracking-sm text-xl leading-7 font-medium md:text-2xl md:leading-8">
              {principle.title}
            </h3>
            <p className="text-muted-foreground -tracking-xs text-base leading-6 md:leading-7">
              {principle.body}
            </p>
          </div>
        </Glass>
      </motion.div>

      {/* The connector takes whatever height the panel leaves in the rail, so the
          spine is continuous however long a rule runs. The negative bottom margin
          carries it across the next number's top margin — without it the line
          would stop a row early and the sequence would read as five fragments. */}
      <motion.div
        aria-hidden
        variants={trackVariants}
        className={cn(
          'col-start-1 row-start-2 flex justify-center pt-3 md:pt-4',
          isLast ? null : '-mb-4 md:-mb-6',
        )}
      >
        <div
          className="relative w-px"
          style={{
            // The track has to survive the mist ground of the light theme, so it
            // is the strong hairline rather than the default one; the last rule
            // dissolves instead of stopping, because nothing follows it.
            background: isLast
              ? 'linear-gradient(180deg, var(--cd-line-strong) 0%, transparent 72%)'
              : 'var(--cd-line-strong)',
          }}
        >
          <motion.div
            variants={drawVariants}
            className="absolute inset-0 origin-top"
            style={{
              background: 'linear-gradient(180deg, var(--cd-accent) 0%, transparent 96%)',
            }}
          />
        </div>
      </motion.div>
    </motion.li>
  );
}

export function Feedback() {
  const reduced = useReducedMotion();

  return (
    <section id="principios" className="relative w-full">
      <Container className="grid gap-12 py-20 md:py-30 lg:grid-cols-[minmax(0,20rem)_minmax(0,1fr)] lg:gap-16 xl:gap-20">
        {/*
          The claim on the left, the evidence on the right. It is deliberately not
          sticky: the page's `main` carries `overflow-x: hidden`, which makes it
          the scrollport, and a sticky column inside it would compute as sticky
          and never actually stick. `self-start` keeps the block at the top of its
          row instead of stretching down the list.
        */}
        <motion.div
          className="flex flex-col gap-6 lg:self-start"
          variants={headerVariants}
          initial={reduced ? 'show' : 'hidden'}
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
        >
          <div className="flex flex-col gap-4">
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
              className="text-muted-foreground -tracking-xs max-w-md text-base leading-6 md:text-lg md:leading-7"
              variants={fadeUpVariants}
            >
              {STANDFIRST}
            </motion.p>
          </div>

          {/* Cobalt at the origin, dissolving into the hairline — the same
              gesture the spine makes, so the header and the list rhyme. */}
          <motion.div
            aria-hidden
            className="h-px w-full origin-left"
            style={{
              background:
                'linear-gradient(90deg, var(--cd-accent) 0%, var(--cd-line) 22%, var(--cd-line) 100%)',
            }}
            variants={ruleVariants}
          />

          <motion.div variants={fadeUpVariants}>
            <Button avatar="/shots/mark.webp">{PRINCIPLES_CTA}</Button>
          </motion.div>
        </motion.div>

        {/* The measure is capped by the list, not by the panels: every rule keeps
            the same line length however wide the viewport gets. */}
        <ol className="flex max-w-2xl flex-col [--rail:2.5rem] md:[--rail:4rem]">
          {PRINCIPLES.map((principle, index) => (
            <PrincipleRow
              key={principle.id}
              principle={principle}
              index={index}
              isLast={index === PRINCIPLES.length - 1}
            />
          ))}
        </ol>
      </Container>
    </section>
  );
}
