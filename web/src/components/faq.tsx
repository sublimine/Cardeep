import { useState } from 'react';
import * as Accordion from '@radix-ui/react-accordion';
import { ChevronDown } from 'lucide-react';
import { motion, useReducedMotion, type Variants } from 'motion/react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { Glass } from '@/components/ui/glass';
import { BRAND, FAQ } from '@/content/site';
import { cn } from '@/lib/utils';

/**
 * FAQ: the ask column on the left, the eight answers as one glass panel on the
 * right.
 *
 * Everything that moves here is reporting state. The rows arrive in reading
 * order, a cobalt marker travels to whichever question is open, the chevron
 * turns instead of being swapped for a second icon, and the answer rises as the
 * panel measures itself open. Nothing loops, so nothing has to be ignored.
 */

const EASE_OUT = 'easeOut';
/** Expo-out: long tail, no overshoot — things settle instead of arriving. */
const EASE_EXPO: [number, number, number, number] = [0.16, 1, 0.3, 1];

/**
 * Radix measures the panel and drives the height through the stylesheet's
 * keyframes; this only slows that 200ms default to the page's pace. Inline so it
 * outranks the shorthand the `animate-accordion-*` utilities set — and so the
 * reduced-motion rule in globals.css, which is `!important`, still wins.
 */
const PANEL_STYLE: React.CSSProperties = {
  animationDuration: '420ms',
  animationTimingFunction: 'cubic-bezier(0.16, 1, 0.3, 1)',
};

/** Words rise out of their own clip box, in reading order. */
const HEADING_WORDS = FAQ.heading.split(' ');

const groupVariants: Variants = {
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

const rowVariants: Variants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: EASE_OUT } },
};

type RowProps = {
  question: string;
  answer: string;
  index: number;
  open: boolean;
};

function Row({ question, answer, index, open }: RowProps) {
  const reduced = useReducedMotion();

  return (
    <Accordion.Item value={question} asChild>
      <motion.div
        variants={rowVariants}
        className="border-line relative border-t transition-colors duration-400 ease-out first:border-t-0"
        // The open row lifts a fraction off the panel. `--cd-glass-glow` is the
        // same 5%/7% cobalt the glass uses for its interior, so it reads as the
        // material catching light rather than as a second surface colour.
        style={{ background: open ? 'var(--cd-glass-glow)' : 'transparent' }}
      >
        <Accordion.Header className="relative flex">
          {/* One marker for the whole list: it travels to the open question
              instead of eight of them fading in and out. */}
          {open ? (
            <motion.span
              aria-hidden
              layoutId="faq-marker"
              className="bg-primary absolute top-1/2 left-1.5 -mt-3 h-6 w-0.5 rounded-full md:left-2"
              transition={{ duration: reduced ? 0 : 0.45, ease: EASE_EXPO }}
            />
          ) : null}

          <Accordion.Trigger className="group/q focus-visible:ring-primary/50 flex w-full cursor-pointer items-start gap-4 rounded-lg px-5 py-5 text-left outline-none focus-visible:ring-2 md:px-6">
            <span
              className={cn(
                'font-dm-mono w-7 shrink-0 pt-0.5 text-xs tabular-nums transition-colors duration-300 ease-out',
                open ? 'text-primary' : 'text-subtle group-hover/q:text-muted-foreground',
              )}
            >
              {String(index + 1).padStart(2, '0')}
            </span>

            <span
              className={cn(
                '-tracking-xs flex-1 text-base leading-6 font-medium transition-colors duration-300 ease-out md:text-lg md:leading-7',
                open ? 'text-foreground' : 'text-foreground/85 group-hover/q:text-foreground',
              )}
            >
              {question}
            </span>

            <span
              className={cn(
                'grid size-8 shrink-0 place-items-center rounded-full border transition-all duration-300 ease-out',
                open
                  ? 'bg-primary text-on-primary border-transparent'
                  : 'border-line text-muted-foreground group-hover/q:text-foreground group-hover/q:-translate-y-0.5 group-hover/q:border-[var(--cd-line-strong)]',
              )}
            >
              <ChevronDown
                className={cn(
                  'size-4 transition-transform duration-400 ease-out',
                  open && 'rotate-180',
                )}
                strokeWidth={2}
              />
            </span>
          </Accordion.Trigger>
        </Accordion.Header>

        <Accordion.Content
          style={PANEL_STYLE}
          className="overflow-hidden data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down"
        >
          {/* Radix mounts this only while the row is open, so the mount
              transition is the answer's entrance; the collapse is the height
              keyframe clipping it away. Indent matches the question's text
              column: gutter + index + gap. */}
          <motion.p
            initial={reduced ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.08, ease: EASE_OUT }}
            className="text-muted-foreground -tracking-xs max-w-[62ch] pr-5 pb-6 pl-16 text-sm leading-6 md:pr-6 md:pl-17 md:text-base md:leading-7"
          >
            {answer}
          </motion.p>
        </Accordion.Content>
      </motion.div>
    </Accordion.Item>
  );
}

export function Faq() {
  const reduced = useReducedMotion();
  // Opening the first question on load means the section shows an answer rather
  // than a wall of closed rows, and the marker has somewhere to start.
  const [openItem, setOpenItem] = useState<string>(FAQ.items[0].q);

  return (
    <section id="faq" className="relative w-full">
      <Container className="grid grid-cols-1 items-start gap-12 py-20 md:gap-16 md:py-28 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="flex flex-col gap-8 lg:sticky lg:top-28">
          <motion.div
            className="flex flex-col gap-6"
            variants={groupVariants}
            initial={reduced ? 'show' : 'hidden'}
            whileInView="show"
            viewport={{ once: true, amount: 0.4 }}
          >
            <motion.div
              variants={fadeUpVariants}
              className="glass-chip text-muted-foreground font-dm-mono -tracking-xs flex w-fit items-center gap-2 rounded-full px-3 py-1.5 text-xs uppercase"
            >
              <span className="text-primary tabular-nums">
                {String(FAQ.items.length).padStart(2, '0')}
              </span>
              preguntas
            </motion.div>

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
              variants={fadeUpVariants}
              className="text-muted-foreground -tracking-xs max-w-md text-base leading-6"
            >
              {FAQ.note}{' '}
              <a
                className="text-primary decoration-primary/40 hover:decoration-primary underline underline-offset-4 transition-colors duration-200"
                href={`mailto:${BRAND.email}`}
              >
                {BRAND.email}
              </a>
            </motion.p>

            {/* Section rule: cobalt at the origin, dissolving into the hairline. */}
            <motion.div
              aria-hidden
              variants={ruleVariants}
              className="h-px w-full origin-left"
              style={{
                background:
                  'linear-gradient(90deg, var(--cd-accent) 0%, var(--cd-line) 18%, var(--cd-line) 100%)',
              }}
            />
          </motion.div>

          <motion.div
            initial={reduced ? false : { opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.6, delay: 0.12, ease: EASE_OUT }}
          >
            <Glass radius={24} elevated interactive className="max-w-lg">
              <div className="flex flex-col gap-6 px-6 py-7 md:px-7">
                <div className="flex flex-col gap-3">
                  <span className="text-heading -tracking-sm text-xl leading-7 font-medium md:text-2xl md:leading-8">
                    {FAQ.cardTitle}
                  </span>
                  <span className="text-muted-foreground -tracking-xs text-base leading-6">
                    {FAQ.cardBody}
                  </span>
                </div>
                <div>
                  <Button avatar="/brand/cardeep-mark.png">{FAQ.cardCta}</Button>
                </div>
              </div>
            </Glass>
          </motion.div>
        </div>

        <motion.div
          variants={groupVariants}
          initial={reduced ? 'show' : 'hidden'}
          whileInView="show"
          viewport={{ once: true, amount: 0.15 }}
        >
          <Glass radius={24} elevated interactive>
            <Accordion.Root
              type="single"
              collapsible
              value={openItem}
              onValueChange={setOpenItem}
              className="flex w-full flex-col"
            >
              {FAQ.items.map((item, index) => (
                <Row
                  key={item.q}
                  question={item.q}
                  answer={item.a}
                  index={index}
                  open={openItem === item.q}
                />
              ))}
            </Accordion.Root>
          </Glass>
        </motion.div>
      </Container>
    </section>
  );
}
