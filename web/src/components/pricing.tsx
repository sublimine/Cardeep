import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';

/** Feature list shared verbatim by the two half-width plans, repeats included. */
const PLAN_FEATURES = [
  'Custom Strategy & Wireframe',
  'High-Fidelity Design in Figma',
  'Development in Framer or Webflow',
  'Conversion-Focused Copywriting',
  'Smooth Animations & Interactions',
  'Basic SEO & Performance Optimization',
  'Unlimited Revisions',
  'Conversion-Focused Copywriting',
] as const;

/** Feature list of the full-width plan. The grid is row-major over two columns. */
const MULTI_PAGE_FEATURES = [
  'Custom Strategy & Wireframe',
  'High-Fidelity Design in Figma',
  'Development in Framer or Webflow',
  'High-Fidelity Design in Figma',
  'Conversion-Focused Copywriting',
  'Development in Framer or Webflow',
  'Conversion-Focused Copywriting',
  'High-Fidelity Design in Figma',
  'Unlimited Revisions',
  'Smooth Animations & Interactions',
  'Basic SEO & Performance Optimization',
  'Unlimited Revisions',
  'Conversion-Focused Copywriting',
  'Basic SEO & Performance Optimization',
] as const;

function FeatureItem({ label }: { label: string }) {
  return (
    <div className="text-muted-foreground flex items-center gap-2 text-sm leading-3.5 font-medium">
      <div className="bg-muted-foreground/50 size-2.5 rounded-full" />
      {label}
    </div>
  );
}

type PlanTitleProps = {
  top: string;
  bottom: string;
};

function PlanTitle({ top, bottom }: PlanTitleProps) {
  return (
    <div className="-tracking-xl text-2xl leading-8 font-medium">
      <span>{top}</span>
      <br />
      <span className="text-muted-foreground">{bottom}</span>
    </div>
  );
}

type PlanPriceProps = {
  amount: string;
};

function PlanPrice({ amount }: PlanPriceProps) {
  return (
    <div className="-tracking-xs text-3xl leading-9 font-medium">
      <span className="text-2xl">$</span>
      <span>{amount}</span>
      <span className="text-2xl">/mo</span>
    </div>
  );
}

type TestimonialProps = {
  className: string;
  avatar: string;
  name: string;
  role: string;
};

function Testimonial({ className, avatar, name, role }: TestimonialProps) {
  return (
    <div className={className}>
      <div className="flex w-full items-center justify-between">
        <div className="flex items-center gap-2">
          <img
            alt="Avatar"
            loading="lazy"
            width={32}
            height={32}
            decoding="async"
            className="size-8 rounded-full"
            src={avatar}
          />
          <span className="-tracking-xs text-muted-foreground text-sm leading-6.5 font-medium">
            {name}
            <span>,</span> {role}
          </span>
        </div>
        <div className="size-5.5">
          <GoogleLogo />
        </div>
      </div>
      <div className="-tracking-xs text-sm leading-5 font-medium">
        Aceternity and Manu are Cracked Devs!
      </div>
    </div>
  );
}

/**
 * Multi-gradient Google mark. Rendered twice on the page with the same gradient
 * ids, exactly as the target does — the second instance resolves the first
 * instance's defs, which are identical anyway.
 */
function GoogleLogo() {
  return (
    <svg
      xmlnsXlink="http://www.w3.org/1999/xlink"
      xmlSpace="preserve"
      overflow="hidden"
      viewBox="0 0 268.152 273.883"
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
      <g
        clipPath="url(#google__i)"
        transform="matrix(.95792 0 0 .98525 -90.174 -78.856)"
      >
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

export function Pricing() {
  return (
    <section className="w-full">
      <Container className="flex flex-col gap-20 py-20 md:py-30">
        <div className="flex w-full flex-col justify-between gap-4 lg:flex-row">
          <h2 className="text-heading text-left text-4xl font-semibold tracking-tight md:text-5xl">
            Extensive Pricing Plans
          </h2>
          <div className="-tracking-xs text-base leading-6 font-medium md:text-nowrap">
            Doubts? Reach out to us at{' '}
            <a
              className="text-dusty-green underline underline-offset-3"
              href="mailto:contact@aceternity.com"
            >
              contact@aceternity.com
            </a>{' '}
            or{' '}
            <button className="cursor-pointer text-dusty-green underline underline-offset-3">
              chat with us
            </button>
          </div>
        </div>
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="relative flex flex-col gap-2.5 overflow-hidden rounded-3xl p-3 bg-natural-white text-natural-black">
              <div className="relative z-10 flex flex-col gap-16 rounded-2xl px-6 pt-4 pb-6 bg-secondary">
                <div className="flex flex-col gap-6">
                  <div className="flex w-fit flex-col gap-3 md:flex-row md:items-center">
                    <span className="-tracking-sm text-lg leading-5">Components</span>
                    <div className="flex items-center gap-2 rounded-full px-4 py-1.5 bg-dusty-red/10 text-dusty-red">
                      All slots booked for November.
                    </div>
                  </div>
                  <PlanTitle
                    top="Tailored Website Components"
                    bottom="for Fast Moving Brands"
                  />
                </div>
                <div className="flex w-full flex-col gap-10 md:flex-row md:items-end md:justify-between md:gap-0">
                  <div className="flex flex-col gap-4">
                    <PlanPrice amount="4995" />
                    <div>
                      <Button avatar="/manu.webp">Select Plan</Button>
                    </div>
                  </div>
                  <Testimonial
                    className="flex flex-col gap-2 rounded-xl border p-3 border-natural-black/10"
                    avatar="/avatar/avatar-1.webp"
                    name="Jason Ray"
                    role="CEO"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4.5 px-3 py-6">
                {PLAN_FEATURES.map((feature, index) => (
                  <FeatureItem key={index} label={feature} />
                ))}
              </div>
            </div>
            <div className="relative flex flex-col gap-2.5 overflow-hidden rounded-3xl p-3 bg-natural-black text-natural-white">
              <div className="absolute top-0 left-0 h-48 w-44 -translate-x-1/5 -translate-y-1/5">
                <div className="absolute top-0 left-[61.27px] h-48 w-28 rounded-full bg-stone-800 blur-2xl" />
                <div className="absolute top-[45.09px] left-0 size-20 rounded-full bg-white blur-[34.09px]" />
              </div>
              <div className="relative z-10 flex flex-col gap-16 rounded-2xl px-6 pt-4 pb-6 bg-secondary/15">
                <div className="flex flex-col gap-6">
                  <div className="flex w-fit flex-col gap-3 md:flex-row md:items-center">
                    <span className="-tracking-sm text-lg leading-5">Website Pages</span>
                    <div className="flex items-center gap-2 rounded-full px-4 py-1.5 text-dusty-green bg-[color-mix(in_oklab,var(--color-dusty-green)_30%,#fff)]">
                      2 Spots Available
                    </div>
                  </div>
                  <PlanTitle
                    top="Tailored Website Components"
                    bottom="for Fast Moving Brands"
                  />
                </div>
                <div className="flex w-full flex-col gap-10 md:flex-row md:items-end md:justify-between md:gap-0">
                  <div className="flex flex-col gap-4">
                    <PlanPrice amount="6995" />
                    <div>
                      <Button avatar="/manu.webp">Select Plan</Button>
                    </div>
                  </div>
                  <Testimonial
                    className="flex flex-col gap-2 rounded-xl border p-3 border-natural-white/10"
                    avatar="/avatar/avatar-2.webp"
                    name="Steve Wozniak"
                    role="CTO"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4.5 px-3 py-6">
                {PLAN_FEATURES.map((feature, index) => (
                  <FeatureItem key={index} label={feature} />
                ))}
              </div>
            </div>
          </div>
          <div className="relative grid grid-cols-1 gap-6 overflow-hidden rounded-3xl px-4 py-4 lg:grid-cols-2 lg:gap-2.5 lg:px-5 lg:py-5 bg-natural-white text-natural-black">
            <div className="flex h-full flex-col justify-between gap-16 lg:pl-4">
              <div className="flex flex-col gap-6">
                <div className="flex w-fit flex-col gap-3 md:flex-row md:items-center">
                  <span className="-tracking-sm text-lg leading-5">Multi Pages</span>
                  <div className="flex items-center gap-2 rounded-full px-4 py-1.5 bg-dusty-red/10 text-dusty-red">
                    All slots booked for November.
                  </div>
                </div>
                <PlanTitle
                  top="Tailored Multi Page Websites"
                  bottom="for Best Conversion Rates"
                />
              </div>
              <div className="flex flex-col gap-4">
                <PlanPrice amount="12.499" />
                <div>
                  <Button avatar="/manu.webp">Select Plan</Button>
                </div>
              </div>
            </div>
            <div className="bg-secondary grid grid-cols-1 gap-4.5 rounded-xl px-8 py-6 md:grid-cols-2">
              {MULTI_PAGE_FEATURES.map((feature, index) => (
                <FeatureItem key={index} label={feature} />
              ))}
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
