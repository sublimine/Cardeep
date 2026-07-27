import { Fragment } from 'react';
import { motion } from 'motion/react';
import { BENTO } from '@/content/site';

/**
 * Lattice behind the card: 6 columns x 5 rows of 75px cells. The exported SVG
 * omits `x` on the first column, so we reproduce that rather than emitting `x="0"`.
 */
const GRID_COLUMNS = [0, 75, 150, 225, 300, 375] as const;
const GRID_ROWS = ['-49.2031', '25.7969', '100.797', '175.797', '250.797'] as const;

/** Resting widths of the two result skeleton lines, measured off the reference render. */
const SKELETON_WIDTHS = [320, 192] as const;

/** Shared entrance for the search pill and the stacked result cards. */
const VIEWPORT_ONCE = { once: true } as const;

/** The result's metadata line, split into the chevron-separated segments it renders as. */
const RESULT_META_SEGMENTS = BENTO.price.resultMeta.split(' · ');

/**
 * "Precio real" — the query pill types a vehicle out, and the stacked result cards
 * settle underneath with the dealer's own listing and where it sits in the market.
 * The export keeps its original name so the bento grid's import stays untouched.
 */
export function GoogleSearchCard() {
  return (
    <div className="glass col-span-1 max-h-(--box-min-height) min-h-(--box-min-height) overflow-hidden rounded-2xl p-4 lg:col-span-3">
      <div className="relative flex h-full flex-col gap-10">
        <div className="absolute inset-0 translate-x-5">
          <svg
            width="450"
            height="326"
            viewBox="0 0 450 326"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-full h-fit"
          >
            {/* No opaque backing plate: the washes below are veils over the glass,
                not paint on white, so the panel keeps refracting the page bloom. */}
            <g clipPath="url(#clip0_2620_9398)">
              {GRID_ROWS.map((y) =>
                GRID_COLUMNS.map((x) => (
                  <rect
                    key={`${x}-${y}`}
                    x={x === 0 ? undefined : x}
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
              {/* The three white washes keep their direction and falloff; only their peak
                  opacity drops, so they frost the lattice instead of sealing the glass. */}
              <linearGradient
                id="paint1_linear_2620_9398"
                x1="210.259"
                y1="420.516"
                x2="210.259"
                y2="645.516"
                gradientUnits="userSpaceOnUse"
              >
                <stop stopColor="white" stopOpacity="0.55" />
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
                <stop stopColor="white" stopOpacity="0.55" />
                <stop offset="0.713542" stopColor="white" stopOpacity="0.4" />
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
                <stop stopColor="white" stopOpacity="0.5" />
                <stop offset="1" stopColor="white" stopOpacity="0" />
              </radialGradient>
              <clipPath id="clip0_2620_9398">
                <rect width="450" height="325.2" fill="white" />
              </clipPath>
            </defs>
          </svg>
        </div>
        <div className="z-10 justify-start text-lg leading-6 font-medium">{BENTO.price.title}</div>
        <div className="z-10 flex flex-col gap-2">
          <motion.div
            className="glass flex w-96 flex-col items-start justify-start gap-4 rounded-full py-3.5"
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={VIEWPORT_ONCE}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          >
            <div className="inline-flex items-center justify-start self-stretch px-4">
              <div className="flex flex-1 items-center justify-between">
                <div className="relative flex items-center justify-start gap-3">
                  <SearchMark />
                  <div className="relative flex items-center">
                    {/* Typewriter: the query is revealed by growing the clipped box to its text width. */}
                    <motion.div
                      className="text-muted-foreground overflow-hidden text-sm leading-4 font-normal whitespace-nowrap"
                      initial={{ width: 0 }}
                      whileInView={{ width: 'auto' }}
                      viewport={VIEWPORT_ONCE}
                      transition={{ duration: 1, delay: 0.4, ease: 'linear' }}
                    >
                      {BENTO.price.query}
                    </motion.div>
                    {/* Typing caret. `origin-top-left` is only meaningful for a scale
                        animation, so the blink collapses the rule rather than fading it. */}
                    <motion.div
                      aria-hidden="true"
                      className="bg-muted-foreground absolute top-0 -right-2 h-4 w-px origin-top-left"
                      animate={{ scaleY: [1, 1, 0, 0] }}
                      transition={{
                        duration: 1.1,
                        times: [0, 0.5, 0.5, 1],
                        ease: 'linear',
                        repeat: Infinity,
                      }}
                    />
                  </div>
                </div>
                {/* Trailing affordance: refine the query by year, motor or province. */}
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="text-muted-foreground"
                >
                  <path
                    d="M14.6667 2H1.33334L6.66667 8.30667V12.6667L9.33334 14V8.30667L14.6667 2Z"
                    stroke="currentColor"
                    strokeWidth="1.33333"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            </div>
          </motion.div>
          <div className="relative h-[calc(var(--box-min-height)-100px)] w-96 mask-[linear-gradient(0deg,rgba(255,255,255,0)_0%,rgba(255,255,255,1)_50%)]">
            <div className="relative h-full">
              <ResultCardShell
                className="glass absolute top-16.5 left-1/2 h-24 w-72 -translate-x-1/2 rounded-xl px-2.5 py-3"
                delay={1.4}
              />
              <ResultCardShell
                className="glass absolute top-9 left-1/2 h-28 w-80 -translate-x-1/2 rounded-2xl px-2.5 py-3"
                delay={1.3}
              />
              <motion.div
                className="glass absolute top-0 left-0 inline-flex w-96 flex-col items-start justify-center gap-3 rounded-2xl px-3 py-3.5"
                initial={{ opacity: 0, y: 18, scale: 0.98 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={VIEWPORT_ONCE}
                transition={{ duration: 0.5, delay: 1.2, ease: 'easeOut' }}
              >
                <div className="inline-flex items-center justify-start gap-3">
                  <div className="overflow-hidden">
                    <VehicleMark />
                  </div>
                  <div className="inline-flex flex-col items-start justify-center gap-1">
                    <div className="justify-start text-center text-sm leading-4 font-normal text-zinc-800">
                      {BENTO.price.resultTitle}
                    </div>
                    <div className="inline-flex items-center justify-start gap-1">
                      {RESULT_META_SEGMENTS.map((segment, index) => (
                        <Fragment key={segment}>
                          {index > 0 && <MetaSeparator />}
                          <div className="justify-start text-center text-xs leading-3 font-normal text-neutral-400">
                            {segment}
                          </div>
                        </Fragment>
                      ))}
                    </div>
                  </div>
                </div>
                {/* The punchline: where this price lands against the rest of the market. */}
                <div className="justify-start text-center text-sm leading-4 font-normal text-amber-700">
                  {BENTO.price.resultVerdict}
                </div>
                <div className="flex flex-col items-start justify-start gap-1.5">
                  {SKELETON_WIDTHS.map((width, index) => (
                    <motion.div
                      key={width}
                      className="h-2.5 rounded-[99px] bg-zinc-100"
                      initial={{ width: 0 }}
                      whileInView={{ width }}
                      viewport={VIEWPORT_ONCE}
                      transition={{ duration: 0.5, delay: 1.7 + index * 0.1, ease: 'easeOut' }}
                    />
                  ))}
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/** One of the two empty cards stacked behind the price result. */
function ResultCardShell({ className, delay }: { className: string; delay: number }) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 18, scale: 0.98 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={VIEWPORT_ONCE}
      transition={{ duration: 0.5, delay, ease: 'easeOut' }}
    />
  );
}

/** 4x7 separator between the segments of the result's metadata line. */
function MetaSeparator() {
  return (
    <svg width="4" height="7" viewBox="0 0 4 7" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M0.375 6.375L3.375 3.375L0.375 0.375"
        stroke="#A9A9A8"
        strokeWidth="0.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/** Leading glyph of the query pill: a plain magnifier in the Cardeep blue. */
function SearchMark() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-cardeep size-4"
    >
      <circle cx="7.33333" cy="7.33333" r="4.66667" stroke="currentColor" strokeWidth="1.33333" />
      <path
        d="M13.3333 13.3333L10.6333 10.6333"
        stroke="currentColor"
        strokeWidth="1.33333"
        strokeLinecap="round"
      />
    </svg>
  );
}

/**
 * Avatar of the result row: a car silhouette knocked out of the Cardeep-blue disc,
 * scaled and centred inside the 27px box the reference mark occupied.
 */
function VehicleMark() {
  return (
    <svg
      width="27"
      height="27"
      viewBox="0 0 27 27"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="size-8"
    >
      <circle cx="13.3333" cy="13.3333" r="13.3333" fill="#155EEF" />
      <g
        transform="translate(4.7 3.9) scale(0.72)"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
        <path d="M9 17h6" />
        <circle cx="7" cy="17" r="2" />
        <circle cx="17" cy="17" r="2" />
      </g>
    </svg>
  );
}
