import { motion } from 'framer-motion';
import Marquee from 'react-fast-marquee';

import { Button } from '@landing/components/ui/button';
import { Container } from '@landing/components/ui/container';
import { BRAND, FIGURES, SCALING, SOURCES } from '@landing/content/site';

type MosaicTile = { kind: 'outline' | 'filled' | 'point' };

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

/** 6x5 lattice of 75px cells behind the counter; first row sits above the viewBox. */
const LATTICE_X = [0, 75, 150, 225, 300, 375] as const;
const LATTICE_Y = [-49.2031, 25.7969, 100.797, 175.797, 250.797] as const;

const DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] as const;

const THOUSANDS_SEPARATOR = '.';

/**
 * The counter split into odometer cells. The Spanish thousands dot gets a cell
 * of its own so the digits either side keep rolling independently.
 */
const COUNTER_CELLS = String(SCALING.counterValue)
  .replace(/\B(?=(\d{3})+(?!\d))/g, THOUSANDS_SEPARATOR)
  .split('');

/**
 * Warm tiles drifting behind the pull-quote. `peak` is the opacity each tile
 * breathes up to; the SSR markup ships them all at `opacity: 0`.
 */
const QUOTE_TILES = [
  { x: 105.117, y: 28.7969, peak: 0.55 },
  { x: 249.117, y: 28.7969, peak: 0.9, group: 0.6, filter: 'url(#filter0_d_2637_2853)' },
  { x: 177.117, y: 100.797, peak: 1, group: 0.6, filter: 'url(#filter1_di_2637_2853)' },
  { x: 249.117, y: 100.797, peak: 0.7 },
  { x: 321.117, y: 100.797, peak: 0.45 },
  { x: 105.117, y: 172.797, peak: 0.5 },
  { x: 177.117, y: 172.797, peak: 0.85 },
  { x: 249.117, y: 172.797, peak: 1, group: 0.3, filter: 'url(#filter2_d_2637_2853)' },
  { x: 105.117, y: 100.797, peak: 0.6 },
  { x: 177.117, y: 28.7969, peak: 0.4 },
  { x: 321.117, y: 172.797, peak: 0.75 },
  { x: 177.117, y: 244.797, peak: 0.5 },
  { x: 249.117, y: 244.797, peak: 0.65 },
] as const;

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

function MosaicTileBody({ tile }: { tile: MosaicTile }) {
  if (tile.kind === 'point') {
    return (
      <div
        data-slot="tile-body"
        className="p-1 transition-all will-change-contents group-hover:p-0"
      >
        <div className="glass flex h-full w-full items-center justify-center rounded-lg">
          <span className="bg-primary size-2.5 rounded-full" />
        </div>
      </div>
    );
  }

  if (tile.kind === 'filled') {
    return <div data-slot="tile-body" className="glass-quiet" />;
  }

  return (
    <div
      data-slot="tile-body"
      className="border-natural-black/10 border transition-all group-hover:glass-quiet"
    />
  );
}

/**
 * One odometer column. All ten digits are stacked on top of each other and the
 * whole stack is shifted so `digit` lands on offset 0; columns to the right
 * start a beat later so the number rolls in left-to-right.
 *
 * Two details keep the roll honest for a five-digit number. The shift is a
 * percentage of the column's own height — one cell per step — so it stays exact
 * whatever size the counter renders at. And the in-view trigger sits on the
 * column, not on the digits: a digit parked eight cells below the fold would
 * never intersect the viewport, and its column would stay blank forever.
 */
function CounterColumn({ digit, index }: { digit: number; index: number }) {
  return (
    <motion.div
      className="relative inline-block w-[1ch] overflow-x-visible overflow-y-clip leading-none tabular-nums"
      initial="rolled"
      whileInView="settled"
      viewport={{ once: true }}
    >
      <div className="invisible">0</div>
      {DIGITS.map((value) => (
        <motion.span
          key={value}
          className="absolute inset-0 flex items-center justify-center"
          variants={{
            rolled: { y: `${value * 100}%` },
            settled: { y: `${(value - digit) * 100}%` },
          }}
          transition={{ duration: 1.4, delay: index * 0.12, ease: [0.16, 1, 0.3, 1] }}
        >
          {value}
        </motion.span>
      ))}
    </motion.div>
  );
}

function LatticeBackdrop() {
  return (
    <svg
      width="450"
      height="326"
      viewBox="0 0 450 326"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-fit"
    >
      <g clipPath="url(#clip0_2620_9398)">
        <rect width="450" height="325.2" fill="white" />
        {LATTICE_Y.map((y) =>
          LATTICE_X.map((x) => (
            <rect
              key={`${x}-${y}`}
              x={x}
              y={y}
              width="75"
              height="75"
              rx="8.27586"
              stroke="#F0F0F0"
              strokeWidth="0.775862"
            />
          )),
        )}
        <path
          d="M300 -42.9922V17.5251C300 22.0957 303.705 25.8009 308.276 25.8009H366.724C371.295 25.8009 375 29.5061 375 34.0768V92.525C375 97.0957 378.705 100.801 383.276 100.801H441.724C446.295 100.801 450 104.506 450 109.077V167.525C450 172.096 453.705 175.801 458.276 175.801H516.724C521.295 175.801 525 179.506 525 184.077V242.525C525 247.096 528.705 250.801 533.276 250.801H593.793M225 -42.9922V17.5251C225 22.0957 228.705 25.8009 233.276 25.8009H291.724C296.295 25.8009 300 29.5061 300 34.0768V92.525C300 97.0957 303.705 100.801 308.276 100.801H366.724C371.295 100.801 375 104.506 375 109.077V167.525C375 172.096 371.295 175.801 366.724 175.801H308.276C303.705 175.801 300 172.096 300 167.525V108.042L299.928 107.553C299.372 103.805 296.191 101.006 292.402 100.933L285.517 100.801H233.276C228.705 100.801 225 104.506 225 109.077V167.525C225 172.096 228.705 175.801 233.276 175.801H292.241L294.206 175.932C297.466 176.149 300 178.857 300 182.125V188.473M300 182.008V242.525C300 247.096 303.705 250.801 308.276 250.801H366.724C371.295 250.801 375 254.506 375 259.077V317.525C375 322.096 378.705 325.801 383.276 325.801H441.724C446.295 325.801 450 329.506 450 334.077V392.525C450 397.096 453.705 400.801 458.276 400.801H516.724C521.295 400.801 525 404.506 525 409.077V467.525C525 472.096 528.705 475.801 533.276 475.801H593.793"
          stroke="url(#paint0_linear_2620_9398)"
          strokeOpacity="0.8"
          strokeWidth="0.775862"
        />
        <rect
          y="420.516"
          width="420.517"
          height="225"
          transform="rotate(-90 0 420.516)"
          fill="url(#paint1_linear_2620_9398)"
        />
        <rect
          x="420.516"
          y="475.859"
          width="420.517"
          height="225"
          transform="rotate(-180 420.516 475.859)"
          fill="url(#paint2_linear_2620_9398)"
        />
        <ellipse
          cx="330.226"
          cy="256.448"
          rx="279.828"
          ry="238.448"
          fill="url(#paint3_radial_2620_9398)"
        />
      </g>
      <defs>
        <linearGradient
          id="paint0_linear_2620_9398"
          x1="225"
          y1="-42.9922"
          x2="585.517"
          y2="403.129"
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0.0819437" stopColor="#F7F7F7" />
          <stop offset="0.208333" stopColor="#EDDD9D" />
          <stop offset="0.526042" stopColor="#C471ED" />
          <stop offset="0.9375" stopColor="#F64F59" />
        </linearGradient>
        <linearGradient
          id="paint1_linear_2620_9398"
          x1="210.259"
          y1="420.516"
          x2="210.259"
          y2="645.516"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="white" />
          <stop offset="1" stopColor="white" stopOpacity="0" />
        </linearGradient>
        <linearGradient
          id="paint2_linear_2620_9398"
          x1="630.774"
          y1="475.859"
          x2="630.774"
          y2="700.859"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="white" />
          <stop offset="0.713542" stopColor="white" stopOpacity="0.7" />
          <stop offset="1" stopColor="white" stopOpacity="0" />
        </linearGradient>
        <radialGradient
          id="paint3_radial_2620_9398"
          cx="0"
          cy="0"
          r="1"
          gradientUnits="userSpaceOnUse"
          gradientTransform="translate(330.226 256.448) rotate(90) scale(238.448 279.828)"
        >
          <stop stopColor="white" />
          <stop offset="1" stopColor="white" stopOpacity="0" />
        </radialGradient>
        <clipPath id="clip0_2620_9398">
          <rect width="450" height="325.2" fill="white" />
        </clipPath>
      </defs>
    </svg>
  );
}

/** One tile of the warm grid drifting behind the pull-quote. */
function QuoteTile({ tile, index }: { tile: (typeof QUOTE_TILES)[number]; index: number }) {
  const rect = (
    <motion.rect
      x={tile.x}
      y={tile.y}
      width="72"
      height="72"
      fill="#F0C17B"
      fillOpacity="0.5"
      shapeRendering={'filter' in tile ? 'crispEdges' : undefined}
      initial={{ opacity: 0 }}
      animate={{ opacity: [0, tile.peak, 0] }}
      transition={{
        duration: 7,
        delay: index * 0.45,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  );

  if ('group' in tile) {
    return (
      <g opacity={tile.group} filter={tile.filter}>
        {rect}
      </g>
    );
  }

  return rect;
}

function QuoteBackdrop() {
  return (
    <svg
      width="497"
      height="346"
      viewBox="0 0 497 346"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <mask
        id="mask0_2637_2853"
        style={{ maskType: 'alpha' }}
        maskUnits="userSpaceOnUse"
        x="0"
        y="0"
        width="497"
        height="346"
      >
        <rect width="496.8" height="345.6" fill="url(#paint0_linear_2637_2853)" />
      </mask>
      <g mask="url(#mask0_2637_2853)">
        <mask
          id="mask1_2637_2853"
          style={{ maskType: 'alpha' }}
          maskUnits="userSpaceOnUse"
          x="0"
          y="0"
          width="497"
          height="346"
        >
          <rect width="496.8" height="345.6" fill="url(#paint1_linear_2637_2853)" />
        </mask>
        <g mask="url(#mask1_2637_2853)">
          {QUOTE_TILES.map((tile, index) => (
            <QuoteTile key={`${tile.x}-${tile.y}`} tile={tile} index={index} />
          ))}
        </g>
      </g>
      <defs>
        <filter
          id="filter0_d_2637_2853"
          x="245.117"
          y="28.7969"
          width="80"
          height="80"
          filterUnits="userSpaceOnUse"
          colorInterpolationFilters="sRGB"
        >
          <feFlood floodOpacity="0" result="BackgroundImageFix" />
          <feColorMatrix
            in="SourceAlpha"
            type="matrix"
            values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
            result="hardAlpha"
          />
          <feOffset dy="4" />
          <feGaussianBlur stdDeviation="2" />
          <feComposite in2="hardAlpha" operator="out" />
          <feColorMatrix
            type="matrix"
            values="0 0 0 0 0.792157 0 0 0 0 0.713726 0 0 0 0 0.596078 0 0 0 1 0"
          />
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_2637_2853" />
          <feBlend
            mode="normal"
            in="SourceGraphic"
            in2="effect1_dropShadow_2637_2853"
            result="shape"
          />
        </filter>
        <filter
          id="filter1_di_2637_2853"
          x="167.117"
          y="94.7969"
          width="92"
          height="92"
          filterUnits="userSpaceOnUse"
          colorInterpolationFilters="sRGB"
        >
          <feFlood floodOpacity="0" result="BackgroundImageFix" />
          <feColorMatrix
            in="SourceAlpha"
            type="matrix"
            values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
            result="hardAlpha"
          />
          <feOffset dy="4" />
          <feGaussianBlur stdDeviation="5" />
          <feComposite in2="hardAlpha" operator="out" />
          <feColorMatrix
            type="matrix"
            values="0 0 0 0 0.790264 0 0 0 0 0.712473 0 0 0 0 0.595785 0 0 0 1 0"
          />
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_2637_2853" />
          <feBlend
            mode="normal"
            in="SourceGraphic"
            in2="effect1_dropShadow_2637_2853"
            result="shape"
          />
          <feColorMatrix
            in="SourceAlpha"
            type="matrix"
            values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
            result="hardAlpha"
          />
          <feOffset dy="12" />
          <feGaussianBlur stdDeviation="8" />
          <feComposite in2="hardAlpha" operator="arithmetic" k2="-1" k3="1" />
          <feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.5 0" />
          <feBlend mode="normal" in2="shape" result="effect2_innerShadow_2637_2853" />
        </filter>
        <filter
          id="filter2_d_2637_2853"
          x="245.117"
          y="172.797"
          width="80"
          height="80"
          filterUnits="userSpaceOnUse"
          colorInterpolationFilters="sRGB"
        >
          <feFlood floodOpacity="0" result="BackgroundImageFix" />
          <feColorMatrix
            in="SourceAlpha"
            type="matrix"
            values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
            result="hardAlpha"
          />
          <feOffset dy="4" />
          <feGaussianBlur stdDeviation="2" />
          <feComposite in2="hardAlpha" operator="out" />
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0" />
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_2637_2853" />
          <feBlend
            mode="normal"
            in="SourceGraphic"
            in2="effect1_dropShadow_2637_2853"
            result="shape"
          />
        </filter>
        <linearGradient
          id="paint0_linear_2637_2853"
          x1="100.2"
          y1="172.8"
          x2="402.48"
          y2="172.8"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopOpacity="0" />
          <stop offset="0.354383" />
          <stop offset="0.79624" />
          <stop offset="1" stopOpacity="0" />
        </linearGradient>
        <linearGradient
          id="paint1_linear_2637_2853"
          x1="249.12"
          y1="23.76"
          x2="248.4"
          y2="327"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopOpacity="0" />
          <stop offset="0.397032" />
          <stop offset="0.70269" />
          <stop offset="1" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  );
}

/**
 * Shared shell for both marquee rows: clipped track whose ends fade out. The
 * reference painted two white overlays there; on glass those would read as
 * bright patches, so the track masks its own content instead.
 */
function MarqueeTrack({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative w-full overflow-hidden flex h-full max-h-22 items-center mask-[linear-gradient(to_right,transparent_0,black_6rem,black_calc(100%_-_6rem),transparent_100%)]">
      {children}
    </div>
  );
}

export function Scaling() {
  return (
    <section className="w-full">
      <Container className="flex flex-col gap-15 py-20 md:py-30">
        <h2 className="text-heading text-left text-4xl font-semibold tracking-tight md:text-5xl">
          {SCALING.heading}
        </h2>
        <div className="flex min-h-140 w-full flex-col-reverse gap-3 lg:grid lg:grid-cols-3 **:data-[slot=card]:glass **:data-[slot=card]:relative **:data-[slot=card]:overflow-hidden **:data-[slot=card]:rounded-2xl">
          <div data-slot="card" className="h-140 lg:h-full">
            <div className="group flex h-full flex-col justify-end p-8">
              <div className="absolute inset-0 grid h-fit scale-125 grid-cols-5 gap-3 *:data-[slot=tile-body]:h-20 *:data-[slot=tile-body]:w-20 *:data-[slot=tile-body]:rounded-lg mask-[radial-gradient(circle,rgba(0,0,0,1)_50%,rgba(0,0,0,0)_70%)]">
                {MOSAIC_TILES.map((tile, index) => (
                  <MosaicTileBody key={index} tile={tile} />
                ))}
              </div>
              <div className="flex flex-col gap-5">
                <span className="-tracking-xs text-lg leading-6 font-medium">
                  {SCALING.teamKicker}
                </span>
                <div>
                  <Button>{SCALING.teamCta}</Button>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:col-span-2 lg:grid-cols-2 lg:grid-rows-4">
            <div
              data-slot="card"
              className="row-span-1 md:row-span-3 md:min-h-105 lg:min-h-0 @container"
            >
              <div className="flex h-full flex-col justify-between gap-16 p-8">
                <div className="absolute inset-0">
                  <LatticeBackdrop />
                </div>
                <div className="z-10 flex flex-col gap-3">
                  {/* Five digits plus a separator need more room than the reference's
                      three, so the counter is sized off the card instead of fixed.
                      "19.000+" measures 4.12em wide; the divisor leaves 4% of slack. */}
                  <span
                    className="-tracking-xl flex leading-none font-medium"
                    style={{ fontSize: 'clamp(2.25rem, calc(23.25cqi - 14.9px), 6.25rem)' }}
                  >
                    <div className="flex items-center">
                      {COUNTER_CELLS.map((cell, index) =>
                        cell === THOUSANDS_SEPARATOR ? (
                          <span key={index} className="leading-none">
                            {cell}
                          </span>
                        ) : (
                          <CounterColumn key={index} digit={Number(cell)} index={index} />
                        ),
                      )}
                    </div>
                    {SCALING.counterSuffix}
                  </span>
                  <span className="text-muted-foreground -tracking-xs text-lg leading-6.5 font-medium">
                    {SCALING.counterLabel}
                  </span>
                </div>
                <div className="z-10">
                  <span className="-tracking-xs text-muted-foreground text-base leading-6">
                    {SCALING.body}
                  </span>
                </div>
              </div>
            </div>

            <div data-slot="card" className="row-span-1 h-20 md:row-span-1 md:h-full">
              <div className="relative flex h-full items-center">
                <MarqueeTrack>
                  <Marquee direction="left" speed={50} pauseOnHover pauseOnClick>
                    {FIGURE_CHIPS.map((figure) => (
                      <div
                        key={figure}
                        className="glass-chip mx-2 flex flex-shrink-0 items-center gap-2.5 rounded-lg object-contain px-2.5 py-1.75"
                      >
                        <div className="flex size-4 items-center justify-center">
                          <span className="bg-primary size-1.5 rounded-full" />
                        </div>
                        <span className="-tracking-xs text-sm leading-3.5 font-medium text-nowrap">
                          {figure}
                        </span>
                      </div>
                    ))}
                  </Marquee>
                </MarqueeTrack>
              </div>
            </div>

            <div data-slot="card" className="row-span-1 md:row-span-2">
              <div className="relative flex h-full flex-col justify-end gap-6 p-8">
                <div className="absolute inset-0">
                  <div className="-mt-11 ml-20">
                    <QuoteBackdrop />
                  </div>
                </div>
                <div className="z-10">
                  <span className="font-dm-mono -tracking-xs text-muted-foreground block w-20 text-sm leading-4 font-normal uppercase">
                    {BRAND.name}
                  </span>
                </div>
                <div className="-tracking-xs text-muted-foreground z-10 text-base leading-6 font-medium">
                  {SCALING.quote}
                </div>
                <div className="flex items-center gap-2 z-10">
                  <span className="-tracking-xs text-base leading-6 font-medium">
                    — {SCALING.quoteAuthor}
                  </span>
                  <span className="-tracking-xs text-muted-foreground text-base leading-6 font-medium">
                    {SCALING.quoteRole}
                  </span>
                </div>
              </div>
            </div>

            <div
              data-slot="card"
              className="col-span-1 min-h-20 md:col-span-2 md:h-full lg:min-h-0"
            >
              <div className="relative flex h-full items-center px-8">
                {/* The label sits over the track, so it needs to own its band:
                    raised above the chips and backed by a fade that lets them
                    slide out from behind it instead of colliding with it. */}
                <div className="glass-quiet relative z-10 -my-2 -ml-2 rounded-xl py-2 pr-6 pl-2">
                  <span className="-tracking-xs text-lg leading-6.5 font-medium text-nowrap">
                    {SCALING.sourcesLabel}
                  </span>
                </div>
                <MarqueeTrack>
                  <Marquee direction="right" speed={69} pauseOnHover pauseOnClick>
                    {SOURCES.map(({ name, mark, accent }) => (
                      <div
                        key={name}
                        className="glass-chip mx-6 flex h-14 shrink-0 items-center justify-center rounded-xl px-5"
                      >
                        <span className="-tracking-xs text-base leading-5 font-medium text-nowrap">
                          {mark}
                          {accent ? <span className="text-cardeep">{accent}</span> : null}
                        </span>
                      </div>
                    ))}
                  </Marquee>
                </MarqueeTrack>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
