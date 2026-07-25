import { motion, useReducedMotion, type Variants } from 'motion/react';
import { Copyright } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { Glass } from '@/components/ui/glass';
import { Wordmark } from '@/components/ui/logo';
import { ThemeToggle } from '@/components/ui/theme';
import { BRAND, FOOTER } from '@/content/site';

/**
 * Page footer: the closing statement, the four link columns and the legal bar.
 *
 * The section used to be painted black, which stranded it the moment the page
 * gained a light theme. Everything here now resolves through the theme
 * variables, so the footer is the same markup on both sides — a surface plane
 * lifted off the page, with the hero's photograph coming back one last time
 * behind the glass to close the loop.
 */

const EASE_OUT = 'easeOut';
/** Expo-out: long tail, no overshoot — things settle instead of arriving. */
const EASE_EXPO: [number, number, number, number] = [0.16, 1, 0.3, 1];

const CARD_RADIUS = 28;

type CssVars = React.CSSProperties & Record<`--${string}`, string>;

/**
 * The closing card veils its photograph with the theme's *own* surface colour
 * rather than a fixed white, so light and dark hide precisely the same amount
 * of it — one set of numbers, two correct results. The blur is thinner than the
 * site default because at 22px a skyline stops being a scene and becomes a
 * colour wash.
 */
const PLATE_GLASS: CssVars = {
  '--cd-glass-panel-hi': 'color-mix(in srgb, var(--cd-bg-elevated) 42%, transparent)',
  '--cd-glass-blur': 'blur(3px) saturate(150%) brightness(1.02)',
};

/**
 * Scrim over the photograph, in three parts: the cobalt bloom the hero opens
 * with, a horizontal wipe that clears the left third for the statement, and a
 * vertical fade that hands the bottom back to the watermark. The photograph
 * therefore lives where nothing is written, and the type never fights it.
 *
 * Every stop is mixed from `--cd-bg-elevated`, so light and dark veil the plate
 * by the same amount with their own surface colour — one set of numbers, two
 * correct results.
 */
const PLATE_SCRIM =
  'radial-gradient(70% 80% at 8% 4%, var(--cd-aurora-1), transparent 60%), ' +
  'linear-gradient(90deg, var(--cd-bg-elevated) 0%, color-mix(in srgb, var(--cd-bg-elevated) 86%, transparent) 26%, color-mix(in srgb, var(--cd-bg-elevated) 28%, transparent) 60%, color-mix(in srgb, var(--cd-bg-elevated) 10%, transparent) 100%), ' +
  'linear-gradient(180deg, transparent 0%, color-mix(in srgb, var(--cd-bg-elevated) 42%, transparent) 62%, var(--cd-bg-elevated) 100%)';

/** Ambient bloom, so the footer keeps the page's atmosphere under its own plane. */
const FOOTER_BLOOM =
  'radial-gradient(58rem 30rem at 6% 0%, var(--cd-aurora-1), transparent 62%), radial-gradient(46rem 26rem at 94% 96%, var(--cd-aurora-2), transparent 60%)';

const WATERMARK_INK =
  'linear-gradient(90deg, var(--cd-fg) 0%, color-mix(in srgb, var(--cd-fg) 38%, transparent) 44%, transparent 88%)';

/* ------------------------------------------------------------------ motion */

/** The card orchestrates its own contents: plate, stamp, words, CTA, watermark. */
const cardVariants: Variants = {
  hidden: { opacity: 0, y: 28 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: EASE_OUT, delayChildren: 0.14, staggerChildren: 0.05 },
  },
};

const plateVariants: Variants = {
  hidden: { scale: 1.08 },
  show: { scale: 1, transition: { duration: 1.4, ease: EASE_EXPO } },
};

const fadeUpVariants: Variants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.55, ease: EASE_OUT } },
};

const wordVariants: Variants = {
  hidden: { y: '110%' },
  show: { y: '0%', transition: { duration: 0.65, ease: EASE_EXPO } },
};

const watermarkVariants: Variants = {
  hidden: { opacity: 0, x: -28 },
  show: { opacity: 1, x: 0, transition: { duration: 1.1, ease: EASE_EXPO } },
};

/** Grouping node: animates nothing itself, only orders what it contains. */
const groupVariants: Variants = {
  hidden: {},
  show: { transition: { delayChildren: 0.05, staggerChildren: 0.07 } },
};

const columnVariants: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.045 } },
};

/* ------------------------------------------------------------------ pieces */

/**
 * Status light on the index stamp — one slow breath, the same 2.8s cadence the
 * product sections use, quiet enough to sit beside text and be ignored.
 */
function IndexPulse() {
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

/** `ctaTitle` carries its own line break; honour it instead of guessing a wrap. */
const CTA_LINES = FOOTER.ctaTitle.split('\n');

/**
 * The closing card, and the landing place for the navbar's "API" link: access
 * is requested rather than self-served, so that link ends at this CTA.
 */
function ClosingCard() {
  const reduced = useReducedMotion();

  return (
    <motion.div
      className="relative isolate"
      variants={cardVariants}
      initial={reduced ? 'show' : 'hidden'}
      whileInView="show"
      viewport={{ once: true, amount: 0.25 }}
    >
      {/* The photograph sits behind the panel, so the glass refracts it exactly
          as it refracts the page — the material stays intact, all six layers. */}
      <div
        aria-hidden
        className="absolute inset-0 overflow-hidden"
        style={{ borderRadius: CARD_RADIUS }}
      >
        <motion.img
          src="/hero/skyline.webp"
          alt=""
          width={2000}
          height={1125}
          loading="lazy"
          decoding="async"
          variants={plateVariants}
          className="size-full object-cover object-[62%_58%]"
          style={{ opacity: 0.9, filter: 'saturate(0.5) contrast(1.06)' }}
        />
        <div className="absolute inset-0" style={{ background: PLATE_SCRIM }} />
      </div>

      <Glass id="api" radius={CARD_RADIUS} elevated interactive style={PLATE_GLASS}>
        {/* Giant watermark: the wordmark bleeding off the bottom edge, clipped by
            the panel, so only its shoulders show under the statement. The outer
            node reveals it, the inner one keeps it drifting. */}
        <motion.div
          aria-hidden
          variants={watermarkVariants}
          className="pointer-events-none absolute -bottom-[0.34em] -left-2 select-none md:-left-4"
        >
          <motion.span
            className="-tracking-xl block bg-clip-text text-[120px] leading-none font-medium text-transparent md:text-[220px] lg:text-[280px]"
            style={{ backgroundImage: WATERMARK_INK, opacity: 0.13 }}
            animate={reduced ? undefined : { y: [0, -8, 0] }}
            transition={{ duration: 16, repeat: Infinity, ease: 'easeInOut' }}
          >
            {FOOTER.watermark}
          </motion.span>
        </motion.div>

        <div className="relative z-10 flex min-h-[21rem] flex-1 flex-col gap-10 p-6 md:min-h-[25rem] md:p-12 lg:p-14">
          <div className="flex flex-col-reverse items-start gap-6 md:flex-row md:justify-between md:gap-12">
            <h2 className="text-heading -tracking-lg max-w-2xl text-4xl leading-[1.06] font-semibold sm:text-5xl lg:text-6xl">
              {CTA_LINES.map((line) => (
                <span key={line} className="block">
                  {line.split(' ').map((word, index) => (
                    // The clip box carries bottom padding so descenders survive
                    // it, and an equal negative margin so line height is unchanged.
                    <span
                      key={`${word}-${index}`}
                      className="mr-[0.24em] -mb-[0.16em] inline-block overflow-hidden pb-[0.16em] align-bottom"
                    >
                      <motion.span className="inline-block" variants={wordVariants}>
                        {word}
                      </motion.span>
                    </span>
                  ))}
                </span>
              ))}
            </h2>

            <motion.div
              variants={fadeUpVariants}
              className="glass-chip text-muted-foreground font-dm-mono -tracking-xs flex w-fit shrink-0 items-center gap-2 rounded-full px-3 py-1.5 text-xs"
            >
              <IndexPulse />
              {BRAND.indexStamp}
            </motion.div>
          </div>

          <motion.div variants={fadeUpVariants} className="mt-auto md:self-end">
            {/* The accent box reveals the Cardeep mark on hover — no invented
                portrait. The click lands on the plans, where access is asked for. */}
            <Button
              avatar="/brand/cardeep-mark.png"
              onClick={() => {
                window.location.hash = '#precios';
              }}
            >
              {FOOTER.cta}
            </Button>
          </motion.div>
        </div>
      </Glass>
    </motion.div>
  );
}

type FooterLink = {
  readonly label: string;
  readonly href: string;
};

type FooterColumn = {
  readonly title: string;
  readonly links: readonly FooterLink[];
};

function LinkColumn({ title, links }: FooterColumn) {
  return (
    <motion.div variants={columnVariants} className="flex flex-col gap-5">
      <motion.h3
        variants={fadeUpVariants}
        className="text-subtle font-dm-mono -tracking-xs text-[11px] uppercase"
      >
        {title}
      </motion.h3>
      <ul className="flex flex-col gap-3">
        {links.map((link) => (
          <motion.li key={link.label} variants={fadeUpVariants}>
            <a
              className="group text-muted-foreground hover:text-foreground focus-visible:text-foreground -tracking-sm relative inline-block text-sm leading-5 font-medium outline-none transition-colors duration-200"
              href={link.href}
            >
              {link.label}
              {/* The rule draws from the left instead of a browser underline
                  appearing all at once — transform only, so it stays cheap. */}
              <span
                aria-hidden
                className="bg-primary absolute -bottom-0.5 left-0 h-px w-full origin-left scale-x-0 transition-transform duration-300 ease-out group-hover:scale-x-100 group-focus-visible:scale-x-100"
              />
            </a>
          </motion.li>
        ))}
      </ul>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ footer */

export function SiteFooter() {
  const reduced = useReducedMotion();

  return (
    <footer className="bg-surface relative w-full overflow-hidden">
      {/* Boundary between the page and its closing plane: cobalt at the origin,
          dissolving into the hairline, drawn as the footer arrives. */}
      <motion.div
        aria-hidden
        className="absolute inset-x-0 top-0 z-10 h-px origin-left"
        style={{
          background:
            'linear-gradient(90deg, var(--cd-accent) 0%, var(--cd-line) 22%, var(--cd-line) 100%)',
        }}
        initial={reduced ? false : { scaleX: 0 }}
        whileInView={{ scaleX: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.9, ease: EASE_OUT }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{ background: FOOTER_BLOOM }}
      />

      <Container className="relative z-10 flex flex-col gap-16 pt-16 pb-10 md:gap-24 md:pt-24">
        <ClosingCard />

        <motion.div
          className="grid grid-cols-1 gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.75fr)] lg:gap-16"
          variants={groupVariants}
          initial={reduced ? 'show' : 'hidden'}
          whileInView="show"
          viewport={{ once: true, amount: 0.3 }}
        >
          <motion.div variants={columnVariants} className="flex flex-col gap-5">
            <motion.div variants={fadeUpVariants}>
              <a
                href="/"
                aria-label={BRAND.name}
                className="inline-flex w-fit transition-transform duration-300 ease-out hover:-translate-y-0.5"
              >
                <Wordmark />
              </a>
            </motion.div>
            <motion.p
              variants={fadeUpVariants}
              className="text-muted-foreground -tracking-xs max-w-xs text-sm leading-6"
            >
              {FOOTER.blurb}
            </motion.p>
          </motion.div>

          <div className="grid grid-cols-2 gap-x-6 gap-y-10 sm:grid-cols-4">
            {FOOTER.columns.map((column) => (
              <LinkColumn key={column.title} title={column.title} links={column.links} />
            ))}
          </div>
        </motion.div>

        <motion.div
          id="legal"
          className="border-line flex w-full flex-col gap-5 border-t pt-6 md:flex-row md:items-center md:justify-between"
          variants={groupVariants}
          initial={reduced ? 'show' : 'hidden'}
          whileInView="show"
          viewport={{ once: true, amount: 0.5 }}
        >
          <motion.span
            variants={fadeUpVariants}
            className="text-subtle -tracking-xs flex items-center gap-1.5 text-xs leading-5 font-medium"
          >
            <Copyright aria-hidden className="size-3 shrink-0" strokeWidth={1.75} />
            {/* The mark to the left already draws the ©; drop the duplicate glyph. */}
            {FOOTER.legal.replace(/^©\s*/, '')}
          </motion.span>

          <motion.div variants={fadeUpVariants} className="flex items-center gap-4">
            {/* Cardeep has no social accounts yet: one live address beats three
                dead profiles. */}
            <a
              className="text-muted-foreground hover:text-foreground -tracking-xs text-xs leading-5 font-medium transition-colors duration-200"
              href={`mailto:${BRAND.email}`}
            >
              {BRAND.email}
            </a>
            {/* The theme is reachable from the end of the page too, not only the bar. */}
            <ThemeToggle />
          </motion.div>
        </motion.div>
      </Container>
    </footer>
  );
}
