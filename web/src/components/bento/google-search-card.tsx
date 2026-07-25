import type { ReactNode } from 'react';
import { motion, useReducedMotion } from 'motion/react';

import { Glass } from '@/components/ui/glass';
import { cn } from '@/lib/utils';
import { BENTO } from '@/content/site';

/* --------------------------------------------------------------- geometry */

/**
 * The readout is a histogram of price buckets 400 € wide. Twenty-one buckets put
 * the median in the exact middle column, so every overlay below can be anchored
 * off a plain percentage and the composition stays symmetric around it — the
 * dealer's own bar is then the only thing that breaks the symmetry.
 */
const BUCKETS = 21;
const MEDIAN_INDEX = 10;
const BUCKET_WIDTH = 400;

/**
 * Numeric form of the two figures the copy already states: the car is published
 * at 18.900 € and sits 1.340 € over the median. `site.ts` owns the strings; these
 * exist only so the geometry agrees with them — the dealer's bar lands exactly as
 * many buckets to the right as that gap buys, and the median price under the axis
 * is the subtraction, not a new claim.
 */
const OWN_PRICE = 18_900;
const OVER_MEDIAN = 1_340;
const MEDIAN_PRICE = OWN_PRICE - OVER_MEDIAN;
const OWN_INDEX = MEDIAN_INDEX + Math.round(OVER_MEDIAN / BUCKET_WIDTH);

/**
 * How full each bucket is, relative to the fullest one. Drawn rather than
 * sampled: the shape's only job is to say "the market clusters here, and you are
 * out on the expensive flank". No count is ever printed.
 */
const MARKET = [
  0.08, 0.12, 0.18, 0.26, 0.36, 0.48, 0.62, 0.76, 0.88, 0.97, 1, 0.96, 0.87, 0.75, 0.62, 0.5, 0.39,
  0.3, 0.22, 0.15, 0.1,
] as const;

/** Centre of a column, as a percentage of the plot width. */
function columnCentre(index: number) {
  return ((index + 0.5) / BUCKETS) * 100;
}

const MEDIAN_X = columnCentre(MEDIAN_INDEX);
const OWN_X = columnCentre(OWN_INDEX);
const GAP_SPAN = OWN_X - MEDIAN_X;
const GAP_LABEL_X = (MEDIAN_X + OWN_X) / 2;

/** Quiet bars deepen with how full the bucket is; the dealer's own goes solid. */
function bucketAlpha(weight: number) {
  return 0.3 + weight * 0.34;
}

/* ----------------------------------------------------------------- timing */

/**
 * The order is the argument: the market blooms outward from its median, then the
 * dealer's price drops onto it, then the gap between the two is measured out.
 */
const BAR_DELAY = 0.34;
const BAR_STEP = 0.03;
const LAND_DELAY = 1.06;
const GAP_DELAY = 1.34;

const VIEWPORT = { once: true, amount: 0.3 } as const;

/* ------------------------------------------------------------------- copy */

const QUERY_CHIPS = BENTO.price.query.split(' · ');
const [OWN_PRICE_TEXT, DAYS_TEXT] = BENTO.price.resultMeta.split(' · ');

/** Verdict split so the amount can carry the same accent the dealer's bar does. */
const VERDICT_CUT = BENTO.price.resultVerdict.indexOf('€') + 1;
const VERDICT_AMOUNT = BENTO.price.resultVerdict.slice(0, VERDICT_CUT);
const VERDICT_TEXT = BENTO.price.resultVerdict.slice(VERDICT_CUT).trim();

/**
 * Three strings `site.ts` does not carry: the two ends of the axis and the label
 * on the median tick. Written in the same voice — plain Spanish, no jargon — and
 * deliberately wordless about quantities, so the chart states nothing the copy
 * module has not already stated.
 */
const AXIS_LOW = 'más barato';
const AXIS_HIGH = 'más caro';
const MEDIAN_LABEL = 'Mediana';
const MEDIAN_PRICE_TEXT = `${new Intl.NumberFormat('es-ES').format(MEDIAN_PRICE)} €`;

/* ------------------------------------------------------------------ parts */

/** Anchors an overlay on a column centre, so motion never owns that transform. */
function ColumnAnchor({
  x,
  className,
  children,
}: {
  x: number;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div className={cn('absolute -translate-x-1/2', className)} style={{ left: `${x}%` }}>
      {children}
    </div>
  );
}

/** One price bucket. The dealer's own takes the full accent the moment it lands. */
function MarketBar({ weight, index, reduced }: { weight: number; index: number; reduced: boolean }) {
  const height = `${weight * 100}%`;
  const quiet = bucketAlpha(weight);
  const settled = index === OWN_INDEX ? 1 : quiet;

  return (
    <div className="relative">
      <motion.div
        className="absolute bottom-0 left-[14%] w-[72%] rounded-t-[2px]"
        style={{ background: 'var(--cd-accent)' }}
        initial={{ height: reduced ? height : '0%', opacity: reduced ? settled : quiet }}
        whileInView={{ height, opacity: settled }}
        viewport={VIEWPORT}
        transition={{
          height: {
            duration: 0.5,
            delay: reduced ? 0 : BAR_DELAY + Math.abs(index - MEDIAN_INDEX) * BAR_STEP,
            ease: 'easeOut',
          },
          opacity: { duration: 0.45, delay: reduced ? 0 : LAND_DELAY, ease: 'easeOut' },
        }}
      />
    </div>
  );
}

/**
 * The dealer's column lit from underneath. The gate fades the halo in once the
 * price has landed; the breath inside it is slow enough to ignore.
 */
function OwnGlow({ reduced }: { reduced: boolean }) {
  return (
    <ColumnAnchor x={OWN_X} className="bottom-0 h-24 w-16">
      <motion.div
        aria-hidden
        className="size-full"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={VIEWPORT}
        transition={{ duration: 0.6, delay: reduced ? 0 : LAND_DELAY, ease: 'easeOut' }}
      >
        <motion.div
          className="size-full rounded-full blur-2xl"
          style={{ background: 'var(--cd-accent)' }}
          animate={reduced ? { opacity: 0.26 } : { opacity: [0.2, 0.34, 0.2] }}
          transition={
            reduced ? { duration: 0 } : { duration: 7, repeat: Infinity, ease: 'easeInOut' }
          }
        />
      </motion.div>
    </ColumnAnchor>
  );
}

/**
 * Dashed rule on the median: the reading everything else is measured against.
 * It is drawn in the ink colour rather than a grey, because it has to stay legible
 * where it crosses the fullest bucket — over the glass and over the accent alike.
 */
function MedianTick({ reduced }: { reduced: boolean }) {
  return (
    <ColumnAnchor x={MEDIAN_X} className="top-[46px] bottom-0 w-px">
      <motion.div
        aria-hidden
        className="size-full origin-top opacity-[0.55]"
        style={{
          backgroundImage:
            'repeating-linear-gradient(to bottom, var(--cd-fg) 0 3px, transparent 3px 7px)',
        }}
        initial={{ scaleY: reduced ? 1 : 0 }}
        whileInView={{ scaleY: 1 }}
        viewport={VIEWPORT}
        transition={{ duration: 0.5, delay: reduced ? 0 : 0.26, ease: 'easeOut' }}
      />
    </ColumnAnchor>
  );
}

/**
 * The punchline, drawn as a measurement: the bracket grows from the median tick
 * until its far end reaches the dealer's column, and only then names the gap.
 */
function GapBracket({ reduced }: { reduced: boolean }) {
  return (
    <>
      <motion.div
        aria-hidden
        className="absolute top-[46px] h-2"
        style={{ left: `${MEDIAN_X}%` }}
        initial={{ width: reduced ? `${GAP_SPAN}%` : '0%' }}
        whileInView={{ width: `${GAP_SPAN}%` }}
        viewport={VIEWPORT}
        transition={{ duration: 0.55, delay: reduced ? 0 : GAP_DELAY, ease: 'easeOut' }}
      >
        <span
          className="absolute inset-x-0 top-1/2 h-px"
          style={{ background: 'var(--cd-accent)' }}
        />
        <span className="absolute top-0 left-0 h-2 w-px" style={{ background: 'var(--cd-accent)' }} />
        <span
          className="absolute top-0 right-0 h-2 w-px"
          style={{ background: 'var(--cd-accent)' }}
        />
      </motion.div>
      <ColumnAnchor x={GAP_LABEL_X} className="top-[26px]">
        {/* The figure steps to the deeper accent: the same cobalt reads as a fill
            at 11px but not as type, and this is the number the card is about. */}
        <motion.span
          className="font-dm-mono -tracking-xs block text-[11px] leading-4 font-medium whitespace-nowrap"
          style={{ color: 'var(--cd-on-accent-soft)' }}
          initial={reduced ? false : { opacity: 0, y: 4 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={VIEWPORT}
          transition={{ duration: 0.4, delay: reduced ? 0 : GAP_DELAY + 0.3, ease: 'easeOut' }}
        >
          {VERDICT_AMOUNT}
        </motion.span>
      </ColumnAnchor>
    </>
  );
}

/** The dealer's own price, dropping onto the column it belongs to. */
function OwnMarker({ reduced }: { reduced: boolean }) {
  return (
    <>
      <ColumnAnchor x={OWN_X} className="top-0">
        <motion.span
          className="glass-chip inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 whitespace-nowrap"
          initial={reduced ? false : { opacity: 0, y: -16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={VIEWPORT}
          transition={{ duration: 0.5, delay: reduced ? 0 : LAND_DELAY, ease: 'easeOut' }}
        >
          <span
            aria-hidden
            className="size-1.5 rounded-full"
            style={{ background: 'var(--cd-accent)' }}
          />
          <span className="text-muted-foreground -tracking-xs text-[10px] leading-4">
            {BENTO.price.resultTitle}
          </span>
          <span className="text-foreground font-dm-mono -tracking-xs text-[11px] leading-4 font-medium">
            {OWN_PRICE_TEXT}
          </span>
        </motion.span>
      </ColumnAnchor>
      {/* Hairline tying the label to its column; the bracket's far tick continues it. */}
      <ColumnAnchor x={OWN_X} className="top-[24px] h-[22px] w-px">
        <motion.div
          aria-hidden
          className="size-full origin-top opacity-45"
          style={{ background: 'var(--cd-accent)' }}
          initial={{ scaleY: reduced ? 1 : 0 }}
          whileInView={{ scaleY: 1 }}
          viewport={VIEWPORT}
          transition={{ duration: 0.35, delay: reduced ? 0 : LAND_DELAY + 0.2, ease: 'easeOut' }}
        />
      </ColumnAnchor>
    </>
  );
}

/** Plot area: bars on a baseline, with every marker anchored to a column centre. */
function PricePlot({ reduced }: { reduced: boolean }) {
  return (
    <div className="relative h-[148px] w-full">
      <OwnGlow reduced={reduced} />
      <motion.div
        aria-hidden
        className="bg-line absolute inset-x-0 bottom-0 h-px origin-left"
        initial={{ scaleX: reduced ? 1 : 0 }}
        whileInView={{ scaleX: 1 }}
        viewport={VIEWPORT}
        transition={{ duration: 0.6, delay: reduced ? 0 : 0.2, ease: 'easeOut' }}
      />
      <div
        aria-hidden
        className="absolute inset-x-0 bottom-px grid h-[86px]"
        style={{ gridTemplateColumns: `repeat(${BUCKETS}, minmax(0, 1fr))` }}
      >
        {MARKET.map((weight, index) => (
          <MarketBar key={index} weight={weight} index={index} reduced={reduced} />
        ))}
      </div>
      <MedianTick reduced={reduced} />
      <GapBracket reduced={reduced} />
      <OwnMarker reduced={reduced} />
    </div>
  );
}

/** Axis: which way is cheap, which way is dear, and what the middle costs. */
function PriceAxis({ reduced }: { reduced: boolean }) {
  return (
    <motion.div
      className="relative h-4 w-full"
      initial={reduced ? false : { opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={VIEWPORT}
      transition={{ duration: 0.5, delay: reduced ? 0 : 0.62, ease: 'easeOut' }}
    >
      <span className="text-muted-foreground absolute top-0 left-0 text-[10px] leading-4">
        {AXIS_LOW}
      </span>
      <ColumnAnchor x={MEDIAN_X} className="top-0 flex items-baseline gap-1.5 whitespace-nowrap">
        <span className="text-muted-foreground text-[10px] leading-4">{MEDIAN_LABEL}</span>
        <span className="text-foreground font-dm-mono -tracking-xs text-[11px] leading-4 font-medium">
          {MEDIAN_PRICE_TEXT}
        </span>
      </ColumnAnchor>
      <span className="text-muted-foreground absolute top-0 right-0 text-[10px] leading-4">
        {AXIS_HIGH}
      </span>
    </motion.div>
  );
}

/* ------------------------------------------------------------------- card */

/**
 * "Precio real" — where this car sits in its own market, read off the whole
 * distribution instead of a single reference price. The export keeps its original
 * name so the bento grid's import stays untouched.
 */
export function GoogleSearchCard() {
  const reduced = useReducedMotion() ?? false;

  return (
    <motion.div
      className="col-span-1 min-h-(--box-min-height) lg:col-span-3"
      whileHover={reduced ? undefined : { y: -3 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <Glass radius={16} elevated interactive className="h-full p-4">
        <div className="flex min-h-0 flex-1 flex-col justify-between gap-4">
          <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
            <motion.h3
              className="text-lg leading-6 font-medium tracking-tight"
              initial={reduced ? false : { opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={VIEWPORT}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            >
              {BENTO.price.title}
            </motion.h3>
            <div className="flex flex-wrap items-center gap-1.5">
              {QUERY_CHIPS.map((chip, index) => (
                <motion.span
                  key={chip}
                  className="glass-chip text-muted-foreground -tracking-xs rounded-full px-2.5 py-1 text-[11px] leading-4 whitespace-nowrap"
                  initial={reduced ? false : { opacity: 0, y: 6 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={VIEWPORT}
                  transition={{
                    duration: 0.4,
                    delay: reduced ? 0 : 0.08 + index * 0.07,
                    ease: 'easeOut',
                  }}
                >
                  {chip}
                </motion.span>
              ))}
            </div>
          </div>

          <div className="flex shrink-0 flex-col gap-2">
            <PricePlot reduced={reduced} />
            <PriceAxis reduced={reduced} />
          </div>

          <motion.div
            className="flex flex-wrap items-center justify-between gap-x-3 gap-y-2"
            initial={reduced ? false : { opacity: 0, y: 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={VIEWPORT}
            transition={{ duration: 0.5, delay: reduced ? 0 : GAP_DELAY + 0.3, ease: 'easeOut' }}
          >
            <p className="text-muted-foreground -tracking-xs text-[13px] leading-4">
              <span className="font-dm-mono font-medium" style={{ color: 'var(--cd-on-accent-soft)' }}>
                {VERDICT_AMOUNT}
              </span>{' '}
              {VERDICT_TEXT}
            </p>
            <span className="glass-chip text-muted-foreground -tracking-xs rounded-full px-2.5 py-1 text-[11px] leading-4 whitespace-nowrap">
              {DAYS_TEXT}
            </span>
          </motion.div>
        </div>
      </Glass>
    </motion.div>
  );
}
