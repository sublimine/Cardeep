import { motion, useReducedMotion } from 'motion/react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { Glass } from '@/components/ui/glass';
import { BRAND, FIGURES, SCALING, SOURCES } from '@/content/site';
import { cn } from '@/lib/utils';

/**
 * "Construido para el mercado español" — the coverage bento.
 *
 * Every surface here is liquid glass over the page aurora and every colour
 * resolves through the theme variables, so the section is the same markup in
 * light and dark. The four alpha masks below use `#000` / `transparent`: those
 * are opacity stops for a CSS mask, not palette colours.
 */

/* ------------------------------------------------------------------ mosaic */

type MosaicTile = { kind: 'outline' | 'filled' | 'point' };

const MOSAIC_COLS = 5;

/**
 * The 5x4 tile mosaic behind the coverage card, in DOM order. `point` tiles are
 * the ones carrying an accent dot: a sales point sitting on the national grid.
 */
const MOSAIC_TILES: readonly MosaicTile[] = [
  { kind: 'outline' },
  { kind: 'outline' },
  { kind: 'outline' },
  { kind: 'outline' },
  { kind: 'outline' },
  { kind: 'outline' },
  { kind: 'outline' },
  { kind: 'point' },
  { kind: 'filled' },
  { kind: 'outline' },
  { kind: 'outline' },
  { kind: 'point' },
  { kind: 'outline' },
  { kind: 'point' },
  { kind: 'filled' },
  { kind: 'outline' },
  { kind: 'filled' },
  { kind: 'point' },
  { kind: 'outline' },
  { kind: 'outline' },
];

const MOSAIC_MASK = 'radial-gradient(circle at 50% 50%, #000 46%, transparent 72%)';

/* ----------------------------------------------------------------- lattice */

/** 6x5 lattice of 75px cells behind the counter; the first row sits above the viewBox. */
const LATTICE_X = [0, 75, 150, 225, 300, 375] as const;
const LATTICE_Y = [-49.2, 25.8, 100.8, 175.8, 250.8] as const;

/**
 * A single route stepping up through the lattice, drawn on scroll. It reads as
 * coverage advancing across the grid, and it lands on four cell junctions —
 * which is where the accent nodes light up, each one as the line reaches it.
 * `at` is the node's position along the path, 0 to 1.
 *
 * It runs entirely inside the card's empty middle band — below the counter and
 * its label, above the body copy — so it never crosses a word.
 */
const TRACE_PATH =
  'M -12 250.8 H 140 Q 150 250.8 150 240.8 V 185.8 Q 150 175.8 160 175.8 H 462';

const TRACE_DURATION = 1.6;

const TRACE_NODES = [
  { x: 150, y: 250.8, at: 0.28 },
  { x: 150, y: 175.8, at: 0.42 },
  { x: 300, y: 175.8, at: 0.69 },
] as const;

const LATTICE_MASK = 'radial-gradient(150% 130% at 55% 52%, #000 0%, #000 50%, transparent 96%)';

/* ----------------------------------------------------------------- counter */

const DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] as const;

const THOUSANDS_SEPARATOR = '.';

const ROLL_DURATION = 1.35;
const ROLL_STEP = 0.11;

/**
 * The counter split into odometer cells. The Spanish thousands dot gets a cell
 * of its own so the digits either side keep rolling independently.
 */
const COUNTER_CELLS = String(SCALING.counterValue)
  .replace(/\B(?=(\d{3})+(?!\d))/g, THOUSANDS_SEPARATOR)
  .split('');

/** The suffix waits for the last column to land, so the number reads as final. */
const SUFFIX_DELAY = 0.15 + (COUNTER_CELLS.length - 1) * ROLL_STEP + ROLL_DURATION * 0.75;

/* ------------------------------------------------------------------- quote */

/**
 * Accent tiles filling in behind the pull-quote — the same 72px module as the
 * lattice and the mosaic, so the three backdrops read as one grid seen from
 * three distances. `peak` is the opacity each tile settles at.
 */
const QUOTE_TILES = [
  { x: 105, y: 29, peak: 0.12 },
  { x: 249, y: 29, peak: 0.2 },
  { x: 177, y: 101, peak: 0.22 },
  { x: 249, y: 101, peak: 0.15 },
  { x: 321, y: 101, peak: 0.1 },
  { x: 105, y: 173, peak: 0.11 },
  { x: 177, y: 173, peak: 0.19 },
  { x: 249, y: 173, peak: 0.22 },
  { x: 105, y: 101, peak: 0.13 },
  { x: 177, y: 29, peak: 0.09 },
  { x: 321, y: 173, peak: 0.17 },
  { x: 177, y: 245, peak: 0.11 },
  { x: 249, y: 245, peak: 0.14 },
] as const;

const QUOTE_MASK = 'radial-gradient(120% 105% at 62% 22%, #000 0%, #000 40%, transparent 82%)';

/* ------------------------------------------------------------------ chips */

/**
 * The strip above the pull-quote: the index's headline figures and the date it
 * was last refreshed. Composed from `FIGURES` so no number is written twice.
 */
const FIGURE_CHIPS: readonly string[] = [
  `${FIGURES.vehicles.value}${FIGURES.vehicles.suffix} ${FIGURES.vehicles.label}`,
  `${FIGURES.provinces.value} ${FIGURES.provinces.label}`,
  `${FIGURES.municipalities.prefix}${FIGURES.municipalities.value} ${FIGURES.municipalities.label}`,
  `${FIGURES.sources.value} ${FIGURES.sources.label}`,
  BRAND.indexStamp,
];

/* ------------------------------------------------------------------ pieces */

/**
 * One panel of the bento: the entrance lives on the wrapper and the material on
 * the `Glass` inside, because a node cannot hold an entrance and a hover state
 * for the same property without one clobbering the other.
 */
function Panel({
  children,
  className,
  delay,
  reduced,
}: {
  children: React.ReactNode;
  className?: string;
  delay: number;
  reduced: boolean;
}) {
  return (
    <motion.div
      className={className}
      initial={reduced ? false : { opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.55, delay, ease: 'easeOut' }}
    >
      <Glass radius={20} interactive className="h-full">
        {children}
      </Glass>
    </motion.div>
  );
}

/**
 * One mosaic tile. It answers to three labels handed down by the card: `hidden`
 * and `shown` for the scroll entrance, `lift` for the hover. Both delays derive
 * from the tile's diagonal (row + column), so the grid assembles and later rises
 * as a wave running from the top-left corner outwards.
 */
function MosaicTile({
  tile,
  index,
  reduced,
}: {
  tile: MosaicTile;
  index: number;
  reduced: boolean;
}) {
  const wave = ((index % MOSAIC_COLS) + Math.floor(index / MOSAIC_COLS)) * 0.045;
  const isPoint = tile.kind === 'point';

  return (
    <motion.div
      className="size-20"
      variants={{
        hidden: reduced ? { opacity: 1, scale: 1, y: 0 } : { opacity: 0, scale: 0.82, y: 0 },
        shown: {
          opacity: 1,
          scale: 1,
          y: 0,
          transition: { duration: 0.5, delay: 0.2 + wave, ease: 'easeOut' },
        },
        lift: {
          // Points carry information, so they travel further than the empty grid.
          y: isPoint ? -11 : -6,
          scale: isPoint ? 1.08 : 1.04,
          transition: { duration: 0.42, delay: wave * 0.55, ease: 'easeOut' },
        },
      }}
    >
      {isPoint ? (
        <div className="h-full w-full p-1">
          <div className="glass grid h-full w-full place-items-center rounded-lg">
            <span
              className="bg-primary size-2.5 rounded-full"
              style={{ boxShadow: '0 0 0 5px var(--cd-glass-sheen)' }}
            />
          </div>
        </div>
      ) : tile.kind === 'filled' ? (
        <div className="glass-quiet h-full w-full rounded-xl" />
      ) : (
        // Narrowed to the paint properties: `all` would drag the backdrop filter
        // of twelve tiles through every frame of the hover.
        <div className="border-line h-full w-full rounded-xl border transition-[background-color,border-color] duration-500 group-hover:glass-quiet" />
      )}
    </motion.div>
  );
}

/**
 * One odometer column. All ten digits are stacked on top of each other and the
 * whole stack is shifted so `digit` lands on offset 0; columns to the right
 * start a beat later so the number rolls in left-to-right.
 *
 * Two details keep the roll honest for a five-digit number. The shift is a
 * percentage of the column's own height — one cell per step — so it stays exact
 * whatever size the counter renders at. And the trigger lives on the counter
 * row, not here: a digit parked eight cells below the fold would never intersect
 * the viewport, and its column would stay blank forever.
 */
function CounterColumn({
  digit,
  index,
  reduced,
}: {
  digit: number;
  index: number;
  reduced: boolean;
}) {
  return (
    <motion.span
      className="relative inline-block w-[1ch] overflow-x-visible overflow-y-clip leading-none tabular-nums"
      variants={{ rolled: {}, settled: {} }}
    >
      <span className="invisible">0</span>
      {DIGITS.map((value) => (
        <motion.span
          key={value}
          className="absolute inset-0 flex items-center justify-center"
          variants={{
            rolled: { y: `${(reduced ? value - digit : value) * 100}%` },
            settled: { y: `${(value - digit) * 100}%` },
          }}
          transition={{
            duration: reduced ? 0 : ROLL_DURATION,
            delay: reduced ? 0 : 0.15 + index * ROLL_STEP,
            ease: [0.16, 1, 0.3, 1],
          }}
        >
          {value}
        </motion.span>
      ))}
    </motion.span>
  );
}

/** The national grid behind the counter, with the coverage route drawn on it. */
function LatticeBackdrop({ reduced }: { reduced: boolean }) {
  return (
    <svg
      width="450"
      height="326"
      viewBox="0 0 450 326"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
      className="h-auto w-full"
    >
      <defs>
        <linearGradient
          id="cd-scaling-trace"
          x1="0"
          y1="326"
          x2="450"
          y2="0"
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0" style={{ stopColor: 'var(--cd-accent)', stopOpacity: 0 }} />
          <stop offset="0.28" style={{ stopColor: 'var(--cd-accent)', stopOpacity: 0.85 }} />
          <stop offset="0.82" style={{ stopColor: 'var(--cd-accent)', stopOpacity: 0.5 }} />
          <stop offset="1" style={{ stopColor: 'var(--cd-accent)', stopOpacity: 0 }} />
        </linearGradient>
      </defs>
      {LATTICE_Y.map((y) =>
        LATTICE_X.map((x) => (
          <rect
            key={`${x}-${y}`}
            x={x}
            y={y}
            width={75}
            height={75}
            rx={8.28}
            strokeWidth={0.9}
            style={{ stroke: 'var(--cd-line)' }}
          />
        )),
      )}
      <motion.path
        d={TRACE_PATH}
        fill="none"
        strokeWidth={1.5}
        strokeLinecap="round"
        stroke="url(#cd-scaling-trace)"
        variants={{
          hidden: reduced ? { pathLength: 1, opacity: 1 } : { pathLength: 0, opacity: 0 },
          shown: {
            pathLength: 1,
            opacity: 1,
            transition: { duration: TRACE_DURATION, delay: 0.2, ease: 'easeOut' },
          },
        }}
      />
      {TRACE_NODES.map((node) => {
        // Halo then core, same delay: the junction lights as the line reaches it.
        const delay = 0.2 + node.at * TRACE_DURATION;
        return [
          { r: 9, peak: 0.16, key: 'halo' },
          { r: 3.4, peak: 1, key: 'core' },
        ].map((ring) => (
          <motion.circle
            key={`${node.x}-${node.y}-${ring.key}`}
            cx={node.x}
            cy={node.y}
            r={ring.r}
            style={{ fill: 'var(--cd-accent)' }}
            variants={{
              hidden: reduced ? { opacity: ring.peak } : { opacity: 0 },
              shown: {
                opacity: ring.peak,
                transition: { duration: 0.4, delay, ease: 'easeOut' },
              },
            }}
          />
        ));
      })}
    </svg>
  );
}

/** The accent tile field behind the pull-quote, filling in on scroll. */
function QuoteBackdrop({ reduced }: { reduced: boolean }) {
  return (
    <svg
      width="497"
      height="346"
      viewBox="0 0 497 346"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      {QUOTE_TILES.map((tile, index) => (
        <motion.rect
          key={`${tile.x}-${tile.y}`}
          x={tile.x}
          y={tile.y}
          width={72}
          height={72}
          rx={8.28}
          style={{ fill: 'var(--cd-accent)' }}
          variants={{
            hidden: reduced ? { opacity: tile.peak } : { opacity: 0 },
            shown: {
              opacity: tile.peak,
              transition: { duration: 0.7, delay: 0.25 + index * 0.06, ease: 'easeOut' },
            },
          }}
        />
      ))}
    </svg>
  );
}

/**
 * Shared shell for both marquee rows.
 *
 * The track holds the row twice and travels exactly one copy, so the seam never
 * lands mid-cycle; each item carries its own horizontal margin rather than a
 * flex gap, which is what keeps the two copies exactly half the track apart.
 * Hovering anywhere on the row parks the animation where it stands.
 */
function MarqueeRow({
  children,
  animationClass,
  fade,
}: {
  children: React.ReactNode;
  animationClass: string;
  fade: string;
}) {
  const mask = `linear-gradient(90deg, transparent, #000 ${fade}, #000 calc(100% - ${fade}), transparent)`;

  return (
    <div
      className="group/row relative flex h-full max-h-22 w-full items-center overflow-hidden"
      style={{ maskImage: mask, WebkitMaskImage: mask }}
    >
      <div
        className={cn(
          'flex w-max shrink-0 will-change-transform group-hover/row:[animation-play-state:paused]',
          animationClass,
        )}
      >
        <div className="flex shrink-0 items-center">{children}</div>
        <div aria-hidden className="flex shrink-0 items-center">
          {children}
        </div>
      </div>
    </div>
  );
}

/** One figure from the index. Both copies of the row share the same entrance. */
function FigureChip({
  label,
  index,
  reduced,
}: {
  label: string;
  index: number;
  reduced: boolean;
}) {
  return (
    <motion.div
      className="glass-chip mx-1.5 flex shrink-0 items-center gap-2.5 rounded-xl px-3 py-2"
      variants={{
        hidden: reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 },
        shown: {
          opacity: 1,
          y: 0,
          transition: { duration: 0.5, delay: 0.1 + index * 0.08, ease: 'easeOut' },
        },
      }}
      whileHover={{ y: -3 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <span className="flex size-4 items-center justify-center">
        <span className="bg-primary size-1.5 rounded-full" />
      </span>
      <span className="-tracking-xs text-sm leading-4 font-medium text-nowrap">{label}</span>
    </motion.div>
  );
}

/** One indexed platform: its mark, then its name. */
function SourceChip({
  name,
  logo,
  index,
  reduced,
}: {
  name: string;
  logo: string;
  index: number;
  reduced: boolean;
}) {
  return (
    <motion.div
      className="glass-chip mx-2.5 flex h-14 shrink-0 items-center gap-3 rounded-xl px-5"
      variants={{
        hidden: reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 },
        shown: {
          opacity: 1,
          y: 0,
          transition: { duration: 0.5, delay: 0.1 + index * 0.06, ease: 'easeOut' },
        },
      }}
      whileHover={{ y: -3 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <img
        src={logo}
        alt=""
        aria-hidden
        width={128}
        height={128}
        loading="lazy"
        decoding="async"
        className="size-6 shrink-0 rounded-md object-contain"
      />
      <span className="-tracking-xs text-base leading-5 font-medium text-nowrap">{name}</span>
    </motion.div>
  );
}

/* ----------------------------------------------------------------- section */

export function Scaling() {
  const reduced = Boolean(useReducedMotion());

  return (
    <section className="w-full">
      <Container className="flex flex-col gap-15 py-20 md:py-30">
        <motion.h2
          className="text-heading -tracking-lg text-left text-4xl font-semibold md:text-5xl"
          initial={reduced ? false : { opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.55, ease: 'easeOut' }}
        >
          {SCALING.heading}
        </motion.h2>

        <div className="flex min-h-140 w-full flex-col-reverse gap-3 lg:grid lg:grid-cols-3">
          {/* Coverage mosaic ------------------------------------------------ */}
          <Panel delay={0.08} reduced={reduced} className="h-140 lg:h-full">
            <motion.div
              className="group relative flex h-full flex-col justify-end p-8"
              initial="hidden"
              whileInView="shown"
              whileHover="lift"
              viewport={{ once: true, amount: 0.25 }}
              variants={{ hidden: {}, shown: {}, lift: {} }}
            >
              <div
                className="pointer-events-none absolute inset-0 grid h-fit scale-125 grid-cols-5 gap-3"
                style={{ maskImage: MOSAIC_MASK, WebkitMaskImage: MOSAIC_MASK }}
              >
                {MOSAIC_TILES.map((tile, index) => (
                  <MosaicTile key={index} tile={tile} index={index} reduced={reduced} />
                ))}
              </div>
              <motion.div
                className="relative flex flex-col gap-5"
                variants={{
                  hidden: reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 14 },
                  shown: {
                    opacity: 1,
                    y: 0,
                    transition: { duration: 0.55, delay: 0.3, ease: 'easeOut' },
                  },
                }}
              >
                <span className="-tracking-xs text-lg leading-6 font-medium">
                  {SCALING.teamKicker}
                </span>
                <div>
                  <Button>{SCALING.teamCta}</Button>
                </div>
              </motion.div>
            </motion.div>
          </Panel>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:col-span-2 lg:grid-cols-2 lg:grid-rows-4">
            {/* Counter ----------------------------------------------------- */}
            <Panel
              delay={0}
              reduced={reduced}
              className="row-span-1 md:row-span-3 md:min-h-105 lg:min-h-0"
            >
              <div className="@container relative flex h-full flex-col justify-between gap-16 p-8">
                <motion.div
                  className="pointer-events-none absolute inset-0"
                  style={{ maskImage: LATTICE_MASK, WebkitMaskImage: LATTICE_MASK }}
                  initial="hidden"
                  whileInView="shown"
                  viewport={{ once: true, amount: 0.3 }}
                  variants={{ hidden: {}, shown: {} }}
                >
                  <LatticeBackdrop reduced={reduced} />
                </motion.div>

                <div className="relative z-10 flex flex-col gap-3">
                  {/* Five digits plus a separator need more room than the reference's
                      three, so the counter is sized off the card instead of fixed.
                      "19.000+" measures 4.12em wide; the divisor leaves 4% of slack. */}
                  <motion.span
                    className="-tracking-xl flex leading-none font-medium"
                    style={{ fontSize: 'clamp(2.25rem, calc(23.25cqi - 14.9px), 6.25rem)' }}
                    initial="rolled"
                    whileInView="settled"
                    viewport={{ once: true, amount: 0.5 }}
                    variants={{ rolled: {}, settled: {} }}
                  >
                    <span className="flex items-center">
                      {COUNTER_CELLS.map((cell, index) =>
                        cell === THOUSANDS_SEPARATOR ? (
                          <span key={index} className="leading-none">
                            {cell}
                          </span>
                        ) : (
                          <CounterColumn
                            key={index}
                            digit={Number(cell)}
                            index={index}
                            reduced={reduced}
                          />
                        ),
                      )}
                    </span>
                    <motion.span
                      className="text-primary"
                      initial={reduced ? false : { opacity: 0, x: -8 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true, amount: 0.5 }}
                      transition={{
                        duration: 0.45,
                        delay: reduced ? 0 : SUFFIX_DELAY,
                        ease: 'easeOut',
                      }}
                    >
                      {SCALING.counterSuffix}
                    </motion.span>
                  </motion.span>
                  <span className="text-muted-foreground -tracking-xs text-lg leading-6.5 font-medium">
                    {SCALING.counterLabel}
                  </span>
                </div>

                <div className="relative z-10">
                  <span className="-tracking-xs text-muted-foreground text-base leading-6">
                    {SCALING.body}
                  </span>
                </div>
              </div>
            </Panel>

            {/* Figures ------------------------------------------------------ */}
            <Panel delay={0.16} reduced={reduced} className="row-span-1 h-20 md:row-span-1 md:h-full">
              <motion.div
                className="relative flex h-full items-center"
                initial="hidden"
                whileInView="shown"
                viewport={{ once: true, amount: 0.4 }}
                variants={{ hidden: {}, shown: {} }}
              >
                <MarqueeRow
                  fade="4rem"
                  animationClass="animate-[marquee-x_38s_linear_infinite]"
                >
                  {FIGURE_CHIPS.map((figure, index) => (
                    <FigureChip key={figure} label={figure} index={index} reduced={reduced} />
                  ))}
                </MarqueeRow>
              </motion.div>
            </Panel>

            {/* Pull-quote --------------------------------------------------- */}
            <Panel delay={0.22} reduced={reduced} className="row-span-1 md:row-span-2">
              <div className="relative flex h-full flex-col justify-end gap-6 p-8">
                <motion.div
                  className="pointer-events-none absolute inset-0"
                  style={{ maskImage: QUOTE_MASK, WebkitMaskImage: QUOTE_MASK }}
                  initial="hidden"
                  whileInView="shown"
                  viewport={{ once: true, amount: 0.3 }}
                  variants={{ hidden: {}, shown: {} }}
                >
                  <div className="-mt-11 ml-20">
                    <QuoteBackdrop reduced={reduced} />
                  </div>
                </motion.div>

                {/* A band of light crossing the panel every eleven seconds — slow
                    enough to read past, and it sits under the type. */}
                {reduced ? null : (
                  <motion.span
                    aria-hidden
                    className="pointer-events-none absolute inset-y-0 -left-1/4 z-[2] w-1/4"
                    style={{
                      skewX: -12,
                      background:
                        'linear-gradient(90deg, transparent, var(--cd-glass-sheen), transparent)',
                    }}
                    initial={{ x: '0%' }}
                    animate={{ x: ['0%', '620%'] }}
                    transition={{
                      duration: 6,
                      repeat: Infinity,
                      repeatDelay: 5,
                      ease: 'easeInOut',
                    }}
                  />
                )}

                <div className="relative z-10">
                  <span className="font-dm-mono -tracking-xs text-muted-foreground block w-20 text-sm leading-4 font-normal uppercase">
                    {BRAND.name}
                  </span>
                </div>
                <p className="-tracking-xs text-muted-foreground relative z-10 text-base leading-6 font-medium">
                  {SCALING.quote}
                </p>
                <div className="relative z-10 flex items-center gap-2">
                  <span className="-tracking-xs text-base leading-6 font-medium">
                    — {SCALING.quoteAuthor}
                  </span>
                  <span className="-tracking-xs text-muted-foreground text-base leading-6 font-medium">
                    {SCALING.quoteRole}
                  </span>
                </div>
              </div>
            </Panel>

            {/* Sources ------------------------------------------------------ */}
            <Panel
              delay={0.28}
              reduced={reduced}
              className="col-span-1 min-h-20 md:col-span-2 md:h-full lg:min-h-0"
            >
              <motion.div
                className="relative flex h-full items-center px-8"
                initial="hidden"
                whileInView="shown"
                viewport={{ once: true, amount: 0.4 }}
                variants={{ hidden: {}, shown: {} }}
              >
                {/* The label sits over the track, so it needs to own its band:
                    raised above the chips and backed by a fade that lets them
                    slide out from behind it instead of colliding with it. */}
                <div className="glass-quiet relative z-10 -my-2 -ml-2 rounded-xl py-2 pr-6 pl-2">
                  <span className="-tracking-xs text-lg leading-6.5 font-medium text-nowrap">
                    {SCALING.sourcesLabel}
                  </span>
                </div>
                <MarqueeRow
                  fade="5rem"
                  animationClass="animate-[marquee-x_46s_linear_infinite_reverse]"
                >
                  {SOURCES.map(({ name, logo }, index) => (
                    <SourceChip
                      key={name}
                      name={name}
                      logo={logo}
                      index={index}
                      reduced={reduced}
                    />
                  ))}
                </MarqueeRow>
              </motion.div>
            </Panel>
          </div>
        </div>
      </Container>
    </section>
  );
}
