import { motion } from 'motion/react';

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

export function GoogleSearchCard() {
  return (
    <div className="bg-natural-white col-span-1 max-h-(--box-min-height) min-h-(--box-min-height) overflow-hidden rounded-2xl p-4 lg:col-span-3">
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
            <g clipPath="url(#clip0_2620_9398)">
              <rect width="450" height="325.2" fill="white" />
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
        </div>
        <div className="z-10 justify-start text-lg leading-6 font-medium">Get found on Google</div>
        <div className="z-10 flex flex-col gap-2">
          <motion.div
            className="bg-natural-white shadow-card-md flex w-96 flex-col items-start justify-start gap-4 rounded-full py-3.5"
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={VIEWPORT_ONCE}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          >
            <div className="inline-flex items-center justify-start self-stretch px-4">
              <div className="flex flex-1 items-center justify-between">
                <div className="relative flex items-center justify-start gap-3">
                  <GoogleMark />
                  <div className="relative flex items-center">
                    {/* Typewriter: the query is revealed by growing the clipped box to its text width. */}
                    <motion.div
                      className="text-muted-foreground overflow-hidden text-sm leading-4 font-normal whitespace-nowrap"
                      initial={{ width: 0 }}
                      whileInView={{ width: 'auto' }}
                      viewport={VIEWPORT_ONCE}
                      transition={{ duration: 1, delay: 0.4, ease: 'linear' }}
                    >
                      Best GTM tools for business operations
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
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="text-muted-foreground"
                >
                  <path
                    d="M8 12.6665V14.6665"
                    stroke="currentColor"
                    strokeWidth="1.33333"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M12.6666 6.6665V7.99984C12.6666 9.23751 12.1749 10.4245 11.2998 11.2997C10.4246 12.1748 9.2376 12.6665 7.99992 12.6665C6.76224 12.6665 5.57526 12.1748 4.70009 11.2997C3.82492 10.4245 3.33325 9.23751 3.33325 7.99984V6.6665"
                    stroke="currentColor"
                    strokeWidth="1.33333"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M10 3.3335C10 2.22893 9.10457 1.3335 8 1.3335C6.89543 1.3335 6 2.22893 6 3.3335V8.00016C6 9.10473 6.89543 10.0002 8 10.0002C9.10457 10.0002 10 9.10473 10 8.00016V3.3335Z"
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
                className="shadow-card-md absolute top-16.5 left-1/2 h-24 w-72 -translate-x-1/2 rounded-xl bg-white px-2.5 py-3"
                delay={1.4}
              />
              <ResultCardShell
                className="shadow-card-md absolute top-9 left-1/2 h-28 w-80 -translate-x-1/2 rounded-2xl bg-white px-2.5 py-3"
                delay={1.3}
              />
              <motion.div
                className="shadow-card-md absolute top-0 left-0 inline-flex w-96 flex-col items-start justify-center gap-3 rounded-2xl border border-black/8 bg-white px-3 py-3.5"
                initial={{ opacity: 0, y: 18, scale: 0.98 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={VIEWPORT_ONCE}
                transition={{ duration: 0.5, delay: 1.2, ease: 'easeOut' }}
              >
                <div className="inline-flex items-center justify-start gap-3">
                  <div className="overflow-hidden">
                    <svg
                      width="27"
                      height="27"
                      viewBox="0 0 27 27"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      className="size-8"
                    >
                      <path
                        fillRule="evenodd"
                        clipRule="evenodd"
                        d="M13.3333 26.6667C20.6971 26.6667 26.6667 20.6971 26.6667 13.3333C26.6667 5.96954 20.6971 0 13.3333 0C5.96952 0 0 5.96954 0 13.3333C0 20.6971 5.96952 26.6667 13.3333 26.6667ZM17.4929 6.21123C17.6953 5.49204 16.9974 5.06676 16.36 5.52087L7.46207 11.8597C6.77081 12.3522 6.87954 13.3333 7.62541 13.3333H9.96847V13.3152H14.535L10.8141 14.6281L9.17381 20.4555C8.97134 21.1747 9.66921 21.5999 10.3067 21.1458L19.2046 14.807C19.8959 14.3145 19.7871 13.3333 19.0413 13.3333H15.4881L17.4929 6.21123Z"
                        fill="#155EEF"
                      />
                    </svg>
                  </div>
                  <div className="inline-flex flex-col items-start justify-center gap-1">
                    <div className="justify-start text-center text-sm leading-4 font-normal text-zinc-800">
                      Acme.io
                    </div>
                    <div className="inline-flex items-center justify-start gap-1">
                      <div className="justify-start text-center text-xs leading-3 font-normal text-neutral-400">
                        www.acme.io
                      </div>
                      <BreadcrumbChevron />
                      <div className="justify-start text-center text-xs leading-3 font-normal text-neutral-400">
                        outbound
                      </div>
                      <BreadcrumbChevron />
                      <div className="justify-start text-center text-xs leading-3 font-normal text-neutral-400">
                        sales
                      </div>
                    </div>
                  </div>
                </div>
                <div className="justify-start text-center text-sm leading-4 font-normal text-zinc-800">
                  All in one outbound platform
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

/** One of the two empty cards stacked behind the search result. */
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

/** 4x7 separator between the URL breadcrumb segments. */
function BreadcrumbChevron() {
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

/** The multicolour Google "G", transcribed verbatim from the reference markup. */
function GoogleMark() {
  return (
    <svg
      xmlnsXlink="http://www.w3.org/1999/xlink"
      xmlSpace="preserve"
      overflow="hidden"
      viewBox="0 0 268.152 273.883"
      className="size-4"
    >
      <defs>
        <linearGradient id="google__a">
          <stop offset="0" stopColor="#0fbc5c" />
          <stop offset="1" stopColor="#0cba65" />
        </linearGradient>
        <linearGradient id="google__g">
          <stop offset=".231" stopColor="#0fbc5f" />
          <stop offset=".312" stopColor="#0fbc5f" />
          <stop offset=".366" stopColor="#0fbc5e" />
          <stop offset=".458" stopColor="#0fbc5d" />
          <stop offset=".54" stopColor="#12bc58" />
          <stop offset=".699" stopColor="#28bf3c" />
          <stop offset=".771" stopColor="#38c02b" />
          <stop offset=".861" stopColor="#52c218" />
          <stop offset=".915" stopColor="#67c30f" />
          <stop offset="1" stopColor="#86c504" />
        </linearGradient>
        <linearGradient id="google__h">
          <stop offset=".142" stopColor="#1abd4d" />
          <stop offset=".248" stopColor="#6ec30d" />
          <stop offset=".312" stopColor="#8ac502" />
          <stop offset=".366" stopColor="#a2c600" />
          <stop offset=".446" stopColor="#c8c903" />
          <stop offset=".54" stopColor="#ebcb03" />
          <stop offset=".616" stopColor="#f7cd07" />
          <stop offset=".699" stopColor="#fdcd04" />
          <stop offset=".771" stopColor="#fdce05" />
          <stop offset=".861" stopColor="#ffce0a" />
        </linearGradient>
        <linearGradient id="google__f">
          <stop offset=".316" stopColor="#ff4c3c" />
          <stop offset=".604" stopColor="#ff692c" />
          <stop offset=".727" stopColor="#ff7825" />
          <stop offset=".885" stopColor="#ff8d1b" />
          <stop offset="1" stopColor="#ff9f13" />
        </linearGradient>
        <linearGradient id="google__b">
          <stop offset=".231" stopColor="#ff4541" />
          <stop offset=".312" stopColor="#ff4540" />
          <stop offset=".458" stopColor="#ff4640" />
          <stop offset=".54" stopColor="#ff473f" />
          <stop offset=".699" stopColor="#ff5138" />
          <stop offset=".771" stopColor="#ff5b33" />
          <stop offset=".861" stopColor="#ff6c29" />
          <stop offset="1" stopColor="#ff8c18" />
        </linearGradient>
        <linearGradient id="google__d">
          <stop offset=".408" stopColor="#fb4e5a" />
          <stop offset="1" stopColor="#ff4540" />
        </linearGradient>
        <linearGradient id="google__c">
          <stop offset=".132" stopColor="#0cba65" />
          <stop offset=".21" stopColor="#0bb86d" />
          <stop offset=".297" stopColor="#09b479" />
          <stop offset=".396" stopColor="#08ad93" />
          <stop offset=".477" stopColor="#0aa6a9" />
          <stop offset=".568" stopColor="#0d9cc6" />
          <stop offset=".667" stopColor="#1893dd" />
          <stop offset=".769" stopColor="#258bf1" />
          <stop offset=".859" stopColor="#3086ff" />
        </linearGradient>
        <linearGradient id="google__e">
          <stop offset=".366" stopColor="#ff4e3a" />
          <stop offset=".458" stopColor="#ff8a1b" />
          <stop offset=".54" stopColor="#ffa312" />
          <stop offset=".616" stopColor="#ffb60c" />
          <stop offset=".771" stopColor="#ffcd0a" />
          <stop offset=".861" stopColor="#fecf0a" />
          <stop offset=".915" stopColor="#fecf08" />
          <stop offset="1" stopColor="#fdcd01" />
        </linearGradient>
        <linearGradient
          xlinkHref="#google__a"
          id="google__s"
          x1="219.7"
          x2="254.467"
          y1="329.535"
          y2="329.535"
          gradientUnits="userSpaceOnUse"
        />
        <radialGradient
          xlinkHref="#google__b"
          id="google__m"
          cx="109.627"
          cy="135.862"
          r="71.46"
          fx="109.627"
          fy="135.862"
          gradientTransform="matrix(-1.93688 1.043 1.45573 2.55542 290.525 -400.634)"
          gradientUnits="userSpaceOnUse"
        />
        <radialGradient
          xlinkHref="#google__c"
          id="google__n"
          cx="45.259"
          cy="279.274"
          r="71.46"
          fx="45.259"
          fy="279.274"
          gradientTransform="matrix(-3.5126 -4.45809 -1.69255 1.26062 870.8 191.554)"
          gradientUnits="userSpaceOnUse"
        />
        <radialGradient
          xlinkHref="#google__d"
          id="google__l"
          cx="304.017"
          cy="118.009"
          r="47.854"
          fx="304.017"
          fy="118.009"
          gradientTransform="matrix(2.06435 0 0 2.59204 -297.679 -151.747)"
          gradientUnits="userSpaceOnUse"
        />
        <radialGradient
          xlinkHref="#google__e"
          id="google__o"
          cx="181.001"
          cy="177.201"
          r="71.46"
          fx="181.001"
          fy="177.201"
          gradientTransform="matrix(-.24858 2.08314 2.96249 .33417 -255.146 -331.164)"
          gradientUnits="userSpaceOnUse"
        />
        <radialGradient
          xlinkHref="#google__f"
          id="google__p"
          cx="207.673"
          cy="108.097"
          r="41.102"
          fx="207.673"
          fy="108.097"
          gradientTransform="matrix(-1.2492 1.34326 -3.89684 -3.4257 880.501 194.905)"
          gradientUnits="userSpaceOnUse"
        />
        <radialGradient
          xlinkHref="#google__g"
          id="google__r"
          cx="109.627"
          cy="135.862"
          r="71.46"
          fx="109.627"
          fy="135.862"
          gradientTransform="matrix(-1.93688 -1.043 1.45573 -2.55542 290.525 838.683)"
          gradientUnits="userSpaceOnUse"
        />
        <radialGradient
          xlinkHref="#google__h"
          id="google__j"
          cx="154.87"
          cy="145.969"
          r="71.46"
          fx="154.87"
          fy="145.969"
          gradientTransform="matrix(-.0814 -1.93722 2.92674 -.11625 -215.135 632.86)"
          gradientUnits="userSpaceOnUse"
        />
        <filter
          id="google__q"
          width="1.097"
          height="1.116"
          x="-.048"
          y="-.058"
          colorInterpolationFilters="sRGB"
        >
          <feGaussianBlur stdDeviation="1.701" />
        </filter>
        <filter
          id="google__k"
          width="1.033"
          height="1.02"
          x="-.017"
          y="-.01"
          colorInterpolationFilters="sRGB"
        >
          <feGaussianBlur stdDeviation=".242" />
        </filter>
        <clipPath id="google__i" clipPathUnits="userSpaceOnUse">
          <path d="M371.378 193.24H237.083v53.438h77.167c-1.241 7.563-4.026 15.003-8.105 21.786-4.674 7.773-10.451 13.69-16.373 18.196-17.74 13.498-38.42 16.258-52.783 16.258-36.283 0-67.283-23.286-79.285-54.928-.484-1.149-.805-2.335-1.197-3.507a81.115 81.115 0 0 1-4.101-25.448c0-9.226 1.569-18.057 4.43-26.398 11.285-32.897 42.985-57.467 80.179-57.467 7.481 0 14.685.884 21.517 2.648a77.668 77.668 0 0 1 33.425 18.25l40.834-39.712c-24.839-22.616-57.219-36.32-95.844-36.32-30.878 0-59.386 9.553-82.748 25.7-18.945 13.093-34.483 30.625-44.97 50.985-9.753 18.879-15.094 39.8-15.094 62.294 0 22.495 5.35 43.633 15.103 62.337v.126c10.302 19.857 25.368 36.954 43.678 49.988 15.997 11.386 44.68 26.551 84.031 26.551 22.63 0 42.687-4.051 60.375-11.644 12.76-5.478 24.065-12.622 34.301-21.804 13.525-12.132 24.117-27.139 31.347-44.404 7.23-17.265 11.097-36.79 11.097-57.957 0-9.858-.998-19.87-2.689-28.968Z" />
        </clipPath>
      </defs>
      <g clipPath="url(#google__i)" transform="matrix(.95792 0 0 .98525 -90.174 -78.856)">
        <path
          fill="url(#google__j)"
          d="M92.076 219.958c.148 22.14 6.501 44.983 16.117 63.424v.127c6.949 13.392 16.445 23.97 27.26 34.452l65.327-23.67c-12.36-6.235-14.246-10.055-23.105-17.026-9.054-9.066-15.802-19.473-20.004-31.677h-.17l.17-.127c-2.765-8.058-3.037-16.613-3.14-25.503Z"
          filter="url(#google__k)"
        />
        <path
          fill="url(#google__l)"
          d="M237.083 79.025c-6.456 22.526-3.988 44.421 0 57.161 7.457.006 14.64.888 21.45 2.647a77.662 77.662 0 0 1 33.424 18.25l41.88-40.726c-24.81-22.59-54.667-37.297-96.754-37.332Z"
          filter="url(#google__k)"
        />
        <path
          fill="url(#google__m)"
          d="M236.943 78.847c-31.67 0-60.91 9.798-84.871 26.359a145.533 145.533 0 0 0-24.332 21.15c-1.904 17.744 14.257 39.551 46.262 39.37 15.528-17.936 38.495-29.542 64.056-29.542l.07.002-1.044-57.335c-.048 0-.093-.004-.14-.004Z"
          filter="url(#google__k)"
        />
        <path
          fill="url(#google__n)"
          d="m341.475 226.379-28.268 19.285c-1.24 7.562-4.028 15.002-8.107 21.786-4.674 7.772-10.45 13.69-16.373 18.196-17.702 13.47-38.328 16.244-52.687 16.255-14.842 25.102-17.444 37.675 1.043 57.934 22.877-.016 43.157-4.117 61.046-11.796 12.931-5.551 24.388-12.792 34.761-22.097 13.706-12.295 24.442-27.503 31.769-45 7.327-17.497 11.245-37.282 11.245-58.734Z"
          filter="url(#google__k)"
        />
        <path
          fill="#3086ff"
          d="M234.996 191.21v57.498h136.006c1.196-7.874 5.152-18.064 5.152-26.5 0-9.858-.996-21.899-2.687-30.998Z"
          filter="url(#google__k)"
        />
        <path
          fill="url(#google__o)"
          d="M128.39 124.327c-8.394 9.119-15.564 19.326-21.249 30.364-9.753 18.879-15.094 41.83-15.094 64.324 0 .317.026.627.029.944 4.32 8.224 59.666 6.649 62.456 0-.004-.31-.039-.613-.039-.924 0-9.226 1.57-16.026 4.43-24.367 3.53-10.289 9.056-19.763 16.123-27.926 1.602-2.031 5.875-6.397 7.121-9.016.475-.997-.862-1.557-.937-1.908-.083-.393-1.876-.077-2.277-.37-1.275-.929-3.8-1.414-5.334-1.845-3.277-.921-8.708-2.953-11.725-5.06-9.536-6.658-24.417-14.612-33.505-24.216Z"
          filter="url(#google__k)"
        />
        <path
          fill="url(#google__p)"
          d="M162.099 155.857c22.112 13.301 28.471-6.714 43.173-12.977l-25.574-52.664a144.74 144.74 0 0 0-26.543 14.504c-12.316 8.512-23.192 18.9-32.176 30.72Z"
          filter="url(#google__q)"
        />
        <path
          fill="url(#google__r)"
          d="M171.099 290.222c-29.683 10.641-34.33 11.023-37.062 29.29a144.806 144.806 0 0 0 16.792 13.984c15.996 11.386 46.766 26.551 86.118 26.551.046 0 .09-.004.137-.004v-59.157l-.094.002c-14.736 0-26.512-3.843-38.585-10.527-2.977-1.648-8.378 2.777-11.123.799-3.786-2.729-12.9 2.35-16.183-.938Z"
          filter="url(#google__k)"
        />
        <path
          fill="url(#google__s)"
          d="M219.7 299.023v59.996c5.506.64 11.236 1.028 17.247 1.028 6.026 0 11.855-.307 17.52-.872v-59.748a105.119 105.119 0 0 1-17.477 1.461c-5.932 0-11.7-.686-17.29-1.865Z"
          filter="url(#google__k)"
          opacity=".5"
        />
      </g>
    </svg>
  );
}
