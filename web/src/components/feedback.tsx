import { useLayoutEffect, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { cn } from '@/lib/utils';

/**
 * Base gradients of the Google mark: `[id, [[offset, color], …]]`. Eight further
 * gradients below reference these through `xlink:href` and only add geometry.
 */
const GOOGLE_BASE_GRADIENTS = [
  [
    'google__a',
    [
      ['0', '#0fbc5c'],
      ['1', '#0cba65'],
    ],
  ],
  [
    'google__g',
    [
      ['.231', '#0fbc5f'],
      ['.312', '#0fbc5f'],
      ['.366', '#0fbc5e'],
      ['.458', '#0fbc5d'],
      ['.54', '#12bc58'],
      ['.699', '#28bf3c'],
      ['.771', '#38c02b'],
      ['.861', '#52c218'],
      ['.915', '#67c30f'],
      ['1', '#86c504'],
    ],
  ],
  [
    'google__h',
    [
      ['.142', '#1abd4d'],
      ['.248', '#6ec30d'],
      ['.312', '#8ac502'],
      ['.366', '#a2c600'],
      ['.446', '#c8c903'],
      ['.54', '#ebcb03'],
      ['.616', '#f7cd07'],
      ['.699', '#fdcd04'],
      ['.771', '#fdce05'],
      ['.861', '#ffce0a'],
    ],
  ],
  [
    'google__f',
    [
      ['.316', '#ff4c3c'],
      ['.604', '#ff692c'],
      ['.727', '#ff7825'],
      ['.885', '#ff8d1b'],
      ['1', '#ff9f13'],
    ],
  ],
  [
    'google__b',
    [
      ['.231', '#ff4541'],
      ['.312', '#ff4540'],
      ['.458', '#ff4640'],
      ['.54', '#ff473f'],
      ['.699', '#ff5138'],
      ['.771', '#ff5b33'],
      ['.861', '#ff6c29'],
      ['1', '#ff8c18'],
    ],
  ],
  [
    'google__d',
    [
      ['.408', '#fb4e5a'],
      ['1', '#ff4540'],
    ],
  ],
  [
    'google__c',
    [
      ['.132', '#0cba65'],
      ['.21', '#0bb86d'],
      ['.297', '#09b479'],
      ['.396', '#08ad93'],
      ['.477', '#0aa6a9'],
      ['.568', '#0d9cc6'],
      ['.667', '#1893dd'],
      ['.769', '#258bf1'],
      ['.859', '#3086ff'],
    ],
  ],
  [
    'google__e',
    [
      ['.366', '#ff4e3a'],
      ['.458', '#ff8a1b'],
      ['.54', '#ffa312'],
      ['.616', '#ffb60c'],
      ['.771', '#ffcd0a'],
      ['.861', '#fecf0a'],
      ['.915', '#fecf08'],
      ['1', '#fdcd01'],
    ],
  ],
] as const;

/** Painted shapes of the Google mark, in paint order. */
const GOOGLE_PATHS = [
  {
    fill: 'url(#google__j)',
    filter: 'url(#google__k)',
    d: 'M92.076 219.958c.148 22.14 6.501 44.983 16.117 63.424v.127c6.949 13.392 16.445 23.97 27.26 34.452l65.327-23.67c-12.36-6.235-14.246-10.055-23.105-17.026-9.054-9.066-15.802-19.473-20.004-31.677h-.17l.17-.127c-2.765-8.058-3.037-16.613-3.14-25.503Z',
  },
  {
    fill: 'url(#google__l)',
    filter: 'url(#google__k)',
    d: 'M237.083 79.025c-6.456 22.526-3.988 44.421 0 57.161 7.457.006 14.64.888 21.45 2.647a77.662 77.662 0 0 1 33.424 18.25l41.88-40.726c-24.81-22.59-54.667-37.297-96.754-37.332Z',
  },
  {
    fill: 'url(#google__m)',
    filter: 'url(#google__k)',
    d: 'M236.943 78.847c-31.67 0-60.91 9.798-84.871 26.359a145.533 145.533 0 0 0-24.332 21.15c-1.904 17.744 14.257 39.551 46.262 39.37 15.528-17.936 38.495-29.542 64.056-29.542l.07.002-1.044-57.335c-.048 0-.093-.004-.14-.004Z',
  },
  {
    fill: 'url(#google__n)',
    filter: 'url(#google__k)',
    d: 'm341.475 226.379-28.268 19.285c-1.24 7.562-4.028 15.002-8.107 21.786-4.674 7.772-10.45 13.69-16.373 18.196-17.702 13.47-38.328 16.244-52.687 16.255-14.842 25.102-17.444 37.675 1.043 57.934 22.877-.016 43.157-4.117 61.046-11.796 12.931-5.551 24.388-12.792 34.761-22.097 13.706-12.295 24.442-27.503 31.769-45 7.327-17.497 11.245-37.282 11.245-58.734Z',
  },
  {
    fill: '#3086ff',
    filter: 'url(#google__k)',
    d: 'M234.996 191.21v57.498h136.006c1.196-7.874 5.152-18.064 5.152-26.5 0-9.858-.996-21.899-2.687-30.998Z',
  },
  {
    fill: 'url(#google__o)',
    filter: 'url(#google__k)',
    d: 'M128.39 124.327c-8.394 9.119-15.564 19.326-21.249 30.364-9.753 18.879-15.094 41.83-15.094 64.324 0 .317.026.627.029.944 4.32 8.224 59.666 6.649 62.456 0-.004-.31-.039-.613-.039-.924 0-9.226 1.57-16.026 4.43-24.367 3.53-10.289 9.056-19.763 16.123-27.926 1.602-2.031 5.875-6.397 7.121-9.016.475-.997-.862-1.557-.937-1.908-.083-.393-1.876-.077-2.277-.37-1.275-.929-3.8-1.414-5.334-1.845-3.277-.921-8.708-2.953-11.725-5.06-9.536-6.658-24.417-14.612-33.505-24.216Z',
  },
  {
    fill: 'url(#google__p)',
    filter: 'url(#google__q)',
    d: 'M162.099 155.857c22.112 13.301 28.471-6.714 43.173-12.977l-25.574-52.664a144.74 144.74 0 0 0-26.543 14.504c-12.316 8.512-23.192 18.9-32.176 30.72Z',
  },
  {
    fill: 'url(#google__r)',
    filter: 'url(#google__k)',
    d: 'M171.099 290.222c-29.683 10.641-34.33 11.023-37.062 29.29a144.806 144.806 0 0 0 16.792 13.984c15.996 11.386 46.766 26.551 86.118 26.551.046 0 .09-.004.137-.004v-59.157l-.094.002c-14.736 0-26.512-3.843-38.585-10.527-2.977-1.648-8.378 2.777-11.123.799-3.786-2.729-12.9 2.35-16.183-.938Z',
  },
  {
    fill: 'url(#google__s)',
    filter: 'url(#google__k)',
    opacity: '.5',
    d: 'M219.7 299.023v59.996c5.506.64 11.236 1.028 17.247 1.028 6.026 0 11.855-.307 17.52-.872v-59.748a105.119 105.119 0 0 1-17.477 1.461c-5.932 0-11.7-.686-17.29-1.865Z',
  },
] as const;

const GOOGLE_CLIP_PATH_D =
  'M371.378 193.24H237.083v53.438h77.167c-1.241 7.563-4.026 15.003-8.105 21.786-4.674 7.773-10.451 13.69-16.373 18.196-17.74 13.498-38.42 16.258-52.783 16.258-36.283 0-67.283-23.286-79.285-54.928-.484-1.149-.805-2.335-1.197-3.507a81.115 81.115 0 0 1-4.101-25.448c0-9.226 1.569-18.057 4.43-26.398 11.285-32.897 42.985-57.467 80.179-57.467 7.481 0 14.685.884 21.517 2.648a77.668 77.668 0 0 1 33.425 18.25l40.834-39.712c-24.839-22.616-57.219-36.32-95.844-36.32-30.878 0-59.386 9.553-82.748 25.7-18.945 13.093-34.483 30.625-44.97 50.985-9.753 18.879-15.094 39.8-15.094 62.294 0 22.495 5.35 43.633 15.103 62.337v.126c10.302 19.857 25.368 36.954 43.678 49.988 15.997 11.386 44.68 26.551 84.031 26.551 22.63 0 42.687-4.051 60.375-11.644 12.76-5.478 24.065-12.622 34.301-21.804 13.525-12.132 24.117-27.139 31.347-44.404 7.23-17.265 11.097-36.79 11.097-57.957 0-9.858-.998-19.87-2.689-28.968Z';

function CalLogo() {
  return (
    <img
      alt="Jack Hudson's company logo"
      loading="lazy"
      width={120}
      height={120}
      decoding="async"
      className="h-10 object-contain"
      src="/logos/cal.webp"
    />
  );
}

function GoogleLogo() {
  return (
    <div className="h-10">
      <svg
        xmlnsXlink="http://www.w3.org/1999/xlink"
        xmlSpace="preserve"
        overflow="hidden"
        viewBox="0 0 268.152 273.883"
        className="h-10 w-auto"
      >
        <defs>
          {GOOGLE_BASE_GRADIENTS.map(([id, stops]) => (
            <linearGradient key={id} id={id}>
              {stops.map(([offset, color]) => (
                <stop key={offset} offset={offset} stopColor={color} />
              ))}
            </linearGradient>
          ))}
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
            <path d={GOOGLE_CLIP_PATH_D} />
          </clipPath>
        </defs>
        <g
          clipPath="url(#google__i)"
          transform="matrix(.95792 0 0 .98525 -90.174 -78.856)"
        >
          {GOOGLE_PATHS.map((path) => (
            <path
              key={path.fill}
              fill={path.fill}
              d={path.d}
              filter={path.filter}
              opacity={'opacity' in path ? path.opacity : undefined}
            />
          ))}
        </g>
      </svg>
    </div>
  );
}

function RaycastLogo() {
  return (
    <div className="h-10">
      <svg className="h-10 w-auto" viewBox="0 0 28 28" fill="none">
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M7 18.079V21L0 14L1.46 12.54L7 18.081V18.079ZM9.921 21H7L14 28L15.46 26.54L9.921 21ZM26.535 15.462L27.996 14L13.996 0L12.538 1.466L18.077 7.004H14.73L10.864 3.146L9.404 4.606L11.809 7.01H10.129V17.876H20.994V16.196L23.399 18.6L24.859 17.14L20.994 13.274V9.927L26.535 15.462ZM7.73 6.276L6.265 7.738L7.833 9.304L9.294 7.844L7.73 6.276ZM20.162 18.708L18.702 20.17L20.268 21.738L21.73 20.276L20.162 18.708ZM4.596 9.41L3.134 10.872L7 14.738V11.815L4.596 9.41ZM16.192 21.006H13.268L17.134 24.872L18.596 23.41L16.192 21.006Z"
          fill="#FF6363"
        />
      </svg>
    </div>
  );
}

function MicrosoftLogo() {
  return (
    <div className="h-10">
      <svg className="h-10 w-auto" viewBox="0 0 256 256" preserveAspectRatio="xMidYMid">
        <path fill="#F1511B" d="M121.666 121.666H0V0h121.666z" />
        <path fill="#80CC28" d="M256 121.666H134.335V0H256z" />
        <path fill="#00ADEF" d="M121.663 256.002H0V134.336h121.663z" />
        <path fill="#FBBC09" d="M256 256.002H134.335V134.336H256z" />
      </svg>
    </div>
  );
}

function AdobeLogo() {
  return (
    <div className="h-10">
      <svg className="h-10 w-auto" viewBox="0 0 91 80" fill="none">
        <g clipPath="url(#adobe__clip0_906_1839)">
          <path d="M56.9686 0H90.4318V80L56.9686 0Z" fill="#EB1000" />
          <path d="M33.4632 0H0V80L33.4632 0Z" fill="#EB1000" />
          <path
            d="M45.1821 29.4668L66.5199 80.0002H52.5657L46.1982 63.9461H30.6182L45.1821 29.4668Z"
            fill="#EB1000"
          />
        </g>
        <defs>
          <clipPath id="adobe__clip0_906_1839">
            <rect width="90.4318" height="80" fill="white" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

const FEEDBACK = [
  {
    logo: <CalLogo />,
    quote:
      '“Working with Manu and his team was a masterclass in design engineering. They didn’t just create a website they built a high-performance, thoughtfully engineered product.”',
    name: 'Jack Hudson',
    role: 'VP of Engineering, Cal.com',
  },
  {
    logo: <GoogleLogo />,
    quote:
      '“Manu\'s team rapidly iterated with our stakeholders and delivered a thoughtful, usable product that exceeded expectations.”',
    name: 'Priya Singh',
    role: 'Product Manager, Google',
  },
  {
    logo: <RaycastLogo />,
    quote:
      '“The collaboration and clarity from Manu\'s team made a significant impact on our roadmap.”',
    name: "Liam O'Connor",
    role: 'Head of Design, Raycast',
  },
  {
    logo: <MicrosoftLogo />,
    quote: '“Technical excellence paired with strong product sense — highly recommended.”',
    name: 'Sara Williams',
    role: 'Engineering Manager, Microsoft',
  },
  {
    logo: <AdobeLogo />,
    quote: '“They helped us scale design systems and ship faster across teams.”',
    name: 'Carlos Mendez',
    role: 'Design Systems Lead, Adobe',
  },
] as const;

type FeedbackCardProps = {
  logo: React.ReactNode;
  quote: string;
  name: string;
  role: string;
};

function FeedbackCard({ logo, quote, name, role }: FeedbackCardProps) {
  return (
    <div className="bg-natural-black text-natural-white relative flex min-h-full w-full shrink-0 flex-col gap-30 overflow-hidden rounded-3xl p-8 lg:w-170">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#181816_1px,transparent_1px),linear-gradient(to_bottom,#181816_1px,transparent_1px)] bg-size-[44px_44px] mask-[radial-gradient(circle,black_10%,transparent_100%)]" />
      <div className="absolute inset-0">
        <div className="relative h-full w-full">
          {/* Warm halo bleeding in from the card's top-left corner. */}
          <div className="absolute top-0 left-0 h-48 w-44 -translate-x-1/2 -translate-y-1/2">
            <div className="absolute top-5 left-20 h-48 w-28 rounded-full bg-[#27251F] blur-2xl" />
            <div className="absolute top-11.25 left-10 size-20 rounded-full bg-white blur-[34px]" />
          </div>
        </div>
      </div>
      <div className="relative z-10">{logo}</div>
      <div className="relative z-10 flex flex-col gap-8">
        <span className="text-lg leading-6.5 font-medium">{quote}</span>
        <div className="flex gap-2 text-base leading-6 font-medium">
          <span>{name}</span>
          <span className="text-muted-foreground">{role}</span>
        </div>
      </div>
    </div>
  );
}

export function Feedback() {
  const [index, setIndex] = useState(0);
  const [offset, setOffset] = useState(0);
  const trackRef = useRef<HTMLDivElement>(null);

  // Slide width is responsive (full-width below lg, 680px above), so the
  // translate distance is measured from the laid-out slides instead of assumed.
  useLayoutEffect(() => {
    const track = trackRef.current;
    if (!track) return;

    const measure = () => {
      const first = track.children[0] as HTMLElement | undefined;
      const current = track.children[index] as HTMLElement | undefined;
      if (!first || !current) return;
      setOffset(current.offsetLeft - first.offsetLeft);
    };

    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(track);
    return () => observer.disconnect();
  }, [index]);

  return (
    <section className="w-full overflow-hidden">
      <Container className="flex flex-col gap-15 py-20 md:py-30">
        <div className="flex flex-col gap-6 md:flex-row md:justify-between">
          <h2 className="text-heading text-left text-4xl font-semibold tracking-tight md:text-5xl">
            What people have been saying
          </h2>
          <div>
            <Button avatar="/manu.webp">Chat with us</Button>
          </div>
        </div>
        <div className="flex flex-col gap-10">
          <div>
            <div
              ref={trackRef}
              className="flex transition-transform duration-500 ease-out will-change-transform gap-6"
              style={{ transform: `translate3d(-${offset}px, 0, 0)` }}
            >
              {FEEDBACK.map((item) => (
                <FeedbackCard
                  key={item.name}
                  logo={item.logo}
                  quote={item.quote}
                  name={item.name}
                  role={item.role}
                />
              ))}
            </div>
          </div>
          <div className="flex w-full items-center justify-center">
            <div className="bg-natural-white shadow-card-lg mx-auto flex h-fit w-fit items-center justify-center gap-3 rounded-full px-4 py-3">
              {FEEDBACK.map((item, dotIndex) => (
                <button
                  key={item.name}
                  type="button"
                  aria-label={`Show feedback ${dotIndex + 1}`}
                  aria-current={dotIndex === index}
                  onClick={() => setIndex(dotIndex)}
                  className={cn(
                    'cursor-pointer size-2 rounded-full transition-all duration-300',
                    dotIndex === index
                      ? 'bg-heading'
                      : 'bg-natural-black/15 hover:bg-natural-black/30',
                  )}
                />
              ))}
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
