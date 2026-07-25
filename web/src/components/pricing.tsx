import { motion, useReducedMotion, type Variants } from 'motion/react';

import { Container } from '@/components/ui/container';
import { Glass } from '@/components/ui/glass';
import { BRAND, COMPARISON, PRICING, type Plan } from '@/content/site';

/**
 * Pricing.
 *
 * Three plans, three equal glass columns, one decision. The section is built so
 * the eye can compare across the row rather than down a page: name, badge,
 * two-tone claim, price, action and the included list sit at the same height in
 * every card, which is what makes the differences legible.
 *
 * Scale is the plan we recommend, so it is the only one the layout raises its
 * voice for: a cobalt ring, a tinted tray, a floating label and a few pixels of
 * lift out of the row. Everything else stays identical, because a featured plan
 * only reads as featured when its neighbours are disciplined.
 *
 * The four strings below are written here because `@/content/site` has no field
 * for them: `PRICING` carries the heading, the contact note and the annual line,
 * but no kicker, no standfirst, no word for the recommendation and no label for
 * the feature list. Everything else — plan copy, prices, features, the annual
 * note and the three assurances — comes from the content module unchanged.
 */

const COPY = {
  kicker: 'Precios',
  standfirst:
    'Empieza gratis con la gestión completa de tu negocio y sube al mercado real cuando el índice te haya pagado el mes.',
  recommended: 'Recomendado',
  includes: 'Incluye',
} as const;

/** The plan the page argues for. */
const RECOMMENDED_ID = 'scale';

/** Already written for the closing cards of the comparison; true at the price too. */
const ASSURANCES = COMPARISON.perks.map((perk) => perk.title);

/**
 * Badge ink per tone, straight from the data: `good` takes the affirmative
 * green the page gives anything free or gained, `quiet` the muted grey. The
 * cobalt is spent on the recommendation and on the checks, so it stays loud.
 */
const BADGE_TONE: Record<Plan['badgeTone'], string> = {
  good: 'text-positive',
  quiet: 'text-muted-foreground',
};

/**
 * The recommended card's ring. Composed into the glass shadow rather than added
 * on top of it, so the panel still carries exactly one shadow.
 */
const RECOMMENDED_SURFACE: React.CSSProperties = {
  boxShadow:
    '0 0 0 1px color-mix(in srgb, var(--cd-accent) 62%, transparent),' +
    ' 0 34px 80px -34px color-mix(in srgb, var(--cd-accent) 50%, transparent),' +
    ' var(--cd-glass-shadow-lg)',
};

/**
 * The recommended plan's tray is tinted with the accent sheen. Only the image
 * layer is set, so the glass utility keeps owning the panel colour and blur.
 */
const RECOMMENDED_TRAY: React.CSSProperties = {
  backgroundImage: 'linear-gradient(152deg, var(--cd-glass-sheen), transparent 74%)',
};

const BADGE_SHADOW: React.CSSProperties = {
  boxShadow: '0 8px 22px -10px color-mix(in srgb, var(--cd-accent) 75%, transparent)',
};

/** Cobalt halo marking the recommended column, behind the glass it belongs to. */
const HALO: React.CSSProperties = {
  background: 'radial-gradient(58% 46% at 50% 6%, var(--cd-glass-sheen), transparent 72%)',
};

/* ------------------------------------------------------------------ motion */

const EASE_OUT = 'easeOut';
/** Expo-out: long tail, no overshoot — things settle instead of arriving. */
const EASE_EXPO: [number, number, number, number] = [0.16, 1, 0.3, 1];

const HEADING_WORDS = PRICING.heading.split(' ');

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

const chipVariants: Variants = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45, ease: EASE_OUT } },
};

/**
 * Cards arrive left to right; each one then deals its own feature list. The
 * delay is carried by `custom`, so the list of a later card never starts before
 * the card itself has landed.
 */
const cardVariants: Variants = {
  hidden: { opacity: 0, y: 32 },
  show: (index: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.62,
      ease: EASE_OUT,
      delay: index * 0.12,
      delayChildren: index * 0.12 + 0.26,
      staggerChildren: 0.045,
    },
  }),
};

const featureVariants: Variants = {
  hidden: { opacity: 0, x: -8 },
  show: { opacity: 1, x: 0, transition: { duration: 0.4, ease: EASE_OUT } },
};

/** Each check is stroked on, so a plan reads as a list being ticked off. */
const drawVariants: Variants = {
  hidden: { pathLength: 0, opacity: 0 },
  show: { pathLength: 1, opacity: 1, transition: { duration: 0.4, ease: EASE_OUT } },
};

/* ------------------------------------------------------------------- parts */

function FeatureLine({ label, lead }: { label: string; lead: boolean }) {
  return (
    <motion.li variants={featureVariants} className="flex items-start gap-2.5">
      <span className="text-primary mt-1 shrink-0">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden focusable="false">
          <motion.path
            d="M13.1 4.6L6.35 11.4L2.9 8.1"
            stroke="currentColor"
            strokeWidth="1.7"
            strokeLinecap="round"
            strokeLinejoin="round"
            variants={drawVariants}
          />
        </svg>
      </span>
      <span
        className={
          lead
            ? 'text-foreground -tracking-xs text-sm leading-6 font-medium'
            : 'text-muted-foreground -tracking-xs text-sm leading-6'
        }
      >
        {label}
      </span>
    </motion.li>
  );
}

/**
 * Spanish puts the currency after the figure, so the euro sign trails the
 * amount. Plans priced «A medida» carry neither symbol nor period and drop a
 * size, and the row keeps a fixed height so the three prices share a baseline
 * and the three calls to action line up across the row.
 */
function PlanPrice({ plan }: { plan: Plan }) {
  const hasCurrency = plan.price.endsWith('€');
  const amount = hasCurrency ? plan.price.slice(0, -1).trim() : plan.price;

  return (
    <div className="flex min-h-14 items-end">
      <div className="flex items-baseline gap-1.5">
        <span
          className={
            hasCurrency
              ? 'text-foreground -tracking-lg text-5xl leading-none font-semibold tabular-nums'
              : 'text-foreground -tracking-sm text-3xl leading-none font-semibold'
          }
        >
          {amount}
        </span>
        {hasCurrency ? (
          <span className="text-foreground text-2xl leading-none font-medium">€</span>
        ) : null}
        {plan.period ? (
          <span className="text-muted-foreground -tracking-xs text-base leading-6">
            {plan.period}
          </span>
        ) : null}
      </div>
    </div>
  );
}

const CTA_BASE =
  'group/cta -tracking-xs flex w-full items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm leading-5 font-medium transition-transform duration-300 ease-out hover:-translate-y-0.5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary';

/**
 * Access is granted from the inbox, so every plan's action opens the same mail
 * as the rest of the page. Only the fill separates them: the recommended plan
 * is solid cobalt, its neighbours are glass — same size, same slot.
 */
function PlanCta({ plan, featured }: { plan: Plan; featured: boolean }) {
  return (
    <a
      href={`mailto:${BRAND.email}`}
      className={
        featured
          ? `${CTA_BASE} bg-primary text-on-primary`
          : `${CTA_BASE} glass-chip text-foreground`
      }
    >
      {plan.cta}
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        aria-hidden
        focusable="false"
        className="transition-transform duration-300 ease-out group-hover/cta:translate-x-1"
      >
        <path
          d="M3 8h9.5M9 4.5L12.5 8L9 11.5"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </a>
  );
}

function PlanCard({ plan, index }: { plan: Plan; index: number }) {
  const reduced = useReducedMotion();
  const featured = plan.id === RECOMMENDED_ID;

  return (
    <motion.div
      className={featured ? 'relative max-lg:mt-7 lg:-my-4' : 'relative'}
      variants={cardVariants}
      custom={index}
      initial={reduced ? 'show' : 'hidden'}
      whileInView="show"
      viewport={{ once: true, amount: 0.3 }}
      whileHover={
        reduced
          ? undefined
          : { y: featured ? -6 : -4, transition: { duration: 0.28, ease: EASE_OUT } }
      }
    >
      {featured ? (
        <>
          <span
            aria-hidden
            className="pointer-events-none absolute -inset-x-5 -inset-y-8 z-0 rounded-[44px]"
            style={HALO}
          />
          <span
            className="bg-primary text-on-primary -tracking-xs absolute top-0 left-1/2 z-[2] -translate-x-1/2 -translate-y-1/2 rounded-full px-3.5 py-1.5 text-xs leading-4 font-medium"
            style={BADGE_SHADOW}
          >
            {COPY.recommended}
          </span>
        </>
      ) : null}

      <Glass
        radius={24}
        elevated={featured}
        interactive
        className="relative z-[1] h-full"
        style={featured ? RECOMMENDED_SURFACE : undefined}
      >
        <div className="flex h-full flex-col gap-6 p-6 md:p-7">
          <div className="flex flex-col gap-5">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-foreground -tracking-sm text-lg leading-6 font-medium">
                {plan.name}
              </span>
              <span
                className={`glass-chip -tracking-xs rounded-full px-3 py-1 text-xs leading-5 font-medium ${BADGE_TONE[plan.badgeTone]}`}
              >
                {plan.badge}
              </span>
            </div>
            <div className="-tracking-xl text-2xl leading-8 font-medium">
              <span className="text-foreground">{plan.title}</span>
              <br />
              <span className="text-muted-foreground">{plan.titleAccent}</span>
            </div>
          </div>

          {/* Price and action share an inset tray, so the decision sits on its
              own surface instead of floating in the middle of the card. */}
          <div
            className="glass-quiet flex flex-col gap-5 rounded-2xl p-5"
            style={featured ? RECOMMENDED_TRAY : undefined}
          >
            <PlanPrice plan={plan} />
            <PlanCta plan={plan} featured={featured} />
          </div>

          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <span className="font-dm-mono text-subtle -tracking-xs text-xs uppercase">
                {COPY.includes}
              </span>
              <span aria-hidden className="border-line h-px flex-1 border-t" />
            </div>
            <ul className="flex flex-col gap-2.5">
              {plan.features.map((feature, featureIndex) => (
                <FeatureLine key={feature} label={feature} lead={featureIndex === 0} />
              ))}
            </ul>
          </div>
        </div>
      </Glass>
    </motion.div>
  );
}

/** Calendar glyph for the annual line: what it costs to pay the year up front. */
const CALENDAR_PATHS = [
  'M6.667 1.667v2.5',
  'M13.333 1.667v2.5',
  'M4.167 3.333h11.666c.92 0 1.667.746 1.667 1.667v11.667c0 .92-.746 1.666-1.667 1.666H4.167c-.92 0-1.667-.746-1.667-1.666V5c0-.92.747-1.667 1.667-1.667Z',
  'M2.5 8.333h15',
] as const;

/** Annual price and the way in, under the row. */
function PricingFooter() {
  const reduced = useReducedMotion();

  return (
    <motion.div
      initial={reduced ? false : { opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.4 }}
      transition={{ duration: 0.55, ease: EASE_OUT }}
    >
      <Glass radius={20}>
        <div className="flex flex-col gap-4 px-6 py-5 md:flex-row md:items-center md:justify-between">
          <div className="flex items-start gap-3">
            <span className="text-primary mt-0.5 shrink-0">
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                aria-hidden
                focusable="false"
              >
                {CALENDAR_PATHS.map((d) => (
                  <path
                    key={d}
                    d={d}
                    stroke="currentColor"
                    strokeWidth="1.25"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                ))}
              </svg>
            </span>
            <span className="text-foreground -tracking-xs text-sm leading-6 font-medium">
              {PRICING.annualNote}
            </span>
          </div>
          <p className="text-muted-foreground -tracking-xs text-sm leading-6">
            {PRICING.note}{' '}
            <a
              className="text-primary underline underline-offset-4 transition-opacity duration-200 hover:opacity-80"
              href={`mailto:${BRAND.email}`}
            >
              {BRAND.email}
            </a>{' '}
            o{' '}
            <a
              className="text-primary underline underline-offset-4 transition-opacity duration-200 hover:opacity-80"
              href={`mailto:${BRAND.email}`}
            >
              {PRICING.noteCta}
            </a>
          </p>
        </div>
      </Glass>
    </motion.div>
  );
}

export function Pricing() {
  const reduced = useReducedMotion();

  return (
    <section id="precios" className="w-full">
      <Container className="flex flex-col gap-12 py-20 md:gap-16 md:py-30">
        <motion.div
          className="flex flex-col gap-8"
          variants={headerVariants}
          initial={reduced ? 'show' : 'hidden'}
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
        >
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="flex max-w-2xl flex-col gap-4">
              <motion.span
                className="font-dm-mono text-muted-foreground -tracking-xs text-xs uppercase"
                variants={fadeUpVariants}
              >
                {COPY.kicker}
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
                {COPY.standfirst}
              </motion.p>
            </div>

            <ul className="flex flex-wrap gap-2">
              {ASSURANCES.map((assurance) => (
                <motion.li
                  key={assurance}
                  variants={chipVariants}
                  className="glass-chip text-muted-foreground -tracking-xs flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs leading-5 font-medium"
                >
                  <span aria-hidden className="bg-primary size-1.5 rounded-full" />
                  {assurance}
                </motion.li>
              ))}
            </ul>
          </div>

          {/* Section rule: cobalt at the origin, dissolving into the hairline. */}
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

        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-1 items-stretch gap-6 lg:grid-cols-3">
            {PRICING.plans.map((plan, index) => (
              <PlanCard key={plan.id} plan={plan} index={index} />
            ))}
          </div>

          <PricingFooter />
        </div>
      </Container>
    </section>
  );
}
