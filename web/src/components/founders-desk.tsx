import Marquee from 'react-fast-marquee';

import { Container } from '@/components/ui/container';
import { AdobeMark, GoogleMark, MicrosoftMark } from '@/components/brand-marks';

/**
 * Chips scrolled by the marquee under Manu's note. The brand mark sits on the
 * right of each chip's header row.
 */
const TESTIMONIALS = [
  {
    name: 'Jason Ray',
    role: 'CEO',
    message: 'Aceternity and Manu are Cracked Devs!',
    avatar: '/avatar/avatar-1.webp',
    Brand: GoogleMark,
  },
  {
    name: 'Steve Wozniak',
    role: 'CTO',
    message: 'Aceternity and Manu are Cracked Devs!',
    avatar: '/avatar/avatar-2.webp',
    Brand: AdobeMark,
  },
  {
    name: 'Elon Musk',
    role: 'Founder',
    message: 'Aceternity and Manu are Cracked Devs!',
    avatar: '/avatar/avatar-3.webp',
    Brand: MicrosoftMark,
  },
] as const;

export function FoundersDesk() {
  return (
    <section className="bg-natural-black text-natural-white relative w-full overflow-hidden">
      <div className="absolute inset-0">
        <div className="relative h-full w-full">
          <div className="absolute top-71 -left-140 h-125.5 w-122 rounded-full bg-white blur-[214px]" />
          <div className="absolute top-0 -left-40 h-293 w-180 rounded-full bg-[#27251F] blur-[287px]" />
          <div className="absolute top-0 -right-100 h-293.75 w-180 rounded-full bg-[#27251F] blur-[287px]" />
          <div className="absolute top-10 right-52 h-141 w-197 bg-[linear-gradient(to_right,#181816_1px,transparent_1px),linear-gradient(to_bottom,#181816_1px,transparent_1px)] bg-size-[44px_44px] mask-[radial-gradient(circle,black_10%,transparent_100%)]" />
        </div>
      </div>
      <Container className="relative z-20 flex w-full flex-col gap-20 pt-20 pb-30">
        <div className="-tracking-xl text-6xl leading-18 font-medium">The Founder’s Desk</div>
        <div className="grid w-full grid-cols-1 justify-between gap-30 lg:grid-cols-5">
          <div className="relative lg:col-span-2">
            <img
              alt="Founder’s Desk"
              loading="lazy"
              width={1200}
              height={1200}
              decoding="async"
              className="w-full rounded-lg"
              src="/assets/workers.webp"
            />
          </div>
          <div className="flex h-full w-full flex-col justify-between gap-15 lg:col-span-3">
            <div className="flex flex-col gap-6">
              <div className="flex justify-end">
                <div className="flex items-center gap-5">
                  <a target="_blank" href="https://x.com/aceternitylabs">
                    <XLogo />
                  </a>
                  <a target="_blank" href="https://www.linkedin.com/company/aceternity">
                    <LinkedinLogo />
                  </a>
                  <a target="_blank" href="https://www.instagram.com/aceternity/">
                    <InstagramLogo />
                  </a>
                </div>
              </div>
              <span className="-tracking-xs text-lg leading-6.5 font-medium">
                Hi, <span className="underline">I'm Manu.</span>I've been building web applications
                for over 8 years. I've worked with startups, small businesses, and large enterprises
                to build and scale their web applications. People call me a "Full Stack" engineer but
                I prefer to call myself a problem solver :)
              </span>
              <span className="-tracking-xs text-lg leading-6.5 font-medium">
                I started Aceternity to help businesses build their web presence, providing unique
                web apps that stand out and scale well.
                <br />
                Also, I post relevant web development snippets and tips{' '}
                <a target="_blank" className="underline" href="https://x.com/mannupaaji">
                  on my twitter
                </a>{' '}
                and occassionally shitpost
              </span>
            </div>
            <div>
              <div className="relative w-full overflow-hidden flex h-full max-h-22 items-center mask-[linear-gradient(to_right,transparent,black_20%,black_80%,transparent)]">
                {/* Default speed (50px/s) over the ~908px chip row is what produces
                    the reference's 18.15s loop, so no props are passed. */}
                <Marquee>
                  {TESTIMONIALS.map(({ name, role, message, avatar, Brand }) => (
                    <div key={name} className="mx-2">
                      <Testimonial
                        name={name}
                        role={role}
                        message={message}
                        avatar={avatar}
                        brand={<Brand />}
                      />
                    </div>
                  ))}
                </Marquee>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}

type TestimonialProps = {
  name: string;
  role: string;
  message: string;
  avatar: string;
  brand: React.ReactNode;
};

function Testimonial({ name, role, message, avatar, brand }: TestimonialProps) {
  return (
    <div className="flex flex-col gap-2 rounded-xl border p-3 border-natural-white/10">
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
            <span>, </span>
            {role}
          </span>
        </div>
        <div className="size-5.5">{brand}</div>
      </div>
      <div className="-tracking-xs text-sm leading-5 font-medium">{message}</div>
    </div>
  );
}

function XLogo() {
  return (
    <svg
      className="text-muted-foreground hover:text-natural-white size-4 transition-colors"
      fill="none"
      viewBox="0 0 1200 1227"
    >
      <path
        fill="currentColor"
        d="M714.163 519.284 1160.89 0h-105.86L667.137 450.887 357.328 0H0l468.492 681.821L0 1226.37h105.866l409.625-476.152 327.181 476.152H1200L714.137 519.284h.026ZM569.165 687.828l-47.468-67.894-377.686-540.24h162.604l304.797 435.991 47.468 67.894 396.2 566.721H892.476L569.165 687.854v-.026Z"
      />
    </svg>
  );
}

function LinkedinLogo() {
  return (
    <svg
      className="text-muted-foreground hover:text-natural-white size-4 transition-colors"
      preserveAspectRatio="xMidYMid"
      viewBox="0 0 256 256"
    >
      <path
        d="M218.123 218.127h-37.931v-59.403c0-14.165-.253-32.4-19.728-32.4-19.756 0-22.779 15.434-22.779 31.369v60.43h-37.93V95.967h36.413v16.694h.51a39.907 39.907 0 0 1 35.928-19.733c38.445 0 45.533 25.288 45.533 58.186l-.016 67.013ZM56.955 79.27c-12.157.002-22.014-9.852-22.016-22.009-.002-12.157 9.851-22.014 22.008-22.016 12.157-.003 22.014 9.851 22.016 22.008A22.013 22.013 0 0 1 56.955 79.27m18.966 138.858H37.95V95.967h37.97v122.16ZM237.033.018H18.89C8.58-.098.125 8.161-.001 18.471v219.053c.122 10.315 8.576 18.582 18.89 18.474h218.144c10.336.128 18.823-8.139 18.966-18.474V18.454c-.147-10.33-8.635-18.588-18.966-18.453"
        fill="currentColor"
      />
    </svg>
  );
}

function InstagramLogo() {
  return (
    <svg
      width="265"
      height="265"
      viewBox="0 0 265 265"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-muted-foreground hover:text-natural-white size-4 transition-colors"
    >
      <g clipPath="url(#clip0_2623_9670)">
        <path
          d="M132.512 0C96.528 0 92.0104 0.157707 77.8772 0.800656C63.7723 1.44765 54.1446 3.67977 45.7183 6.95652C37.0038 10.3397 29.6119 14.8687 22.247 22.235C14.8767 29.5999 10.3483 36.9918 6.95412 45.7046C3.66765 54.1317 1.43177 63.7624 0.798718 77.8628C0.165668 91.9969 0 96.5151 0 132.5C0 168.485 0.16028 172.987 0.800064 187.12C1.44928 201.225 3.68246 210.855 6.95546 219.279C10.343 227.993 14.8699 235.387 22.2376 242.752C29.5998 250.122 36.993 254.659 45.7008 258.044C54.1325 261.32 63.7629 263.554 77.8665 264.199C91.9996 264.842 96.5131 265 132.496 265C168.484 265 172.986 264.842 187.12 264.199C201.225 263.552 210.866 261.32 219.295 258.044C228.007 254.66 235.388 250.122 242.75 242.752C250.121 235.387 254.649 227.993 258.043 219.282C261.301 210.855 263.537 201.223 264.199 187.124C264.834 172.99 265 168.485 265 132.5C265 96.5151 264.834 91.9996 264.2 77.8655C263.537 63.7598 261.301 54.1317 258.045 45.7073C254.649 36.9918 250.121 29.5999 242.75 22.235C235.38 14.8647 228.01 10.3371 219.287 6.95652C210.841 3.67977 201.206 1.4463 187.1 0.800656C172.967 0.157707 168.467 0 132.472 0H132.512ZM120.626 23.8781C124.155 23.8727 128.09 23.8781 132.512 23.8781C167.89 23.8781 172.084 24.0048 186.055 24.6396C198.973 25.23 205.985 27.3893 210.655 29.2023C216.838 31.6042 221.247 34.4753 225.882 39.112C230.519 43.7488 233.391 48.1659 235.798 54.3501C237.611 59.0138 239.772 66.0269 240.361 78.9452C240.994 92.9135 241.133 97.1082 241.133 132.47C241.133 167.83 240.995 172.026 240.361 185.994C239.768 198.912 237.611 205.924 235.798 210.589C233.396 216.772 230.519 221.176 225.882 225.81C221.244 230.448 216.841 233.318 210.655 235.72C205.99 237.542 198.973 239.696 186.055 240.286C172.087 240.92 167.89 241.059 132.512 241.059C97.1314 241.059 92.9398 240.921 78.9709 240.286C66.0513 239.689 59.0406 237.531 54.3669 235.717C48.1845 233.316 43.7666 230.445 39.1292 225.807C34.4918 221.17 31.6215 216.764 29.2132 210.578C27.4003 205.913 25.2398 198.902 24.6512 185.983C24.0155 172.015 23.8889 167.819 23.8889 132.437C23.8889 97.0543 24.0155 92.8798 24.6512 78.9115C25.2412 65.9932 27.3989 58.9814 29.2132 54.3123C31.6148 48.1281 34.4918 43.7111 39.1292 39.0743C43.7666 34.4362 48.1832 31.5665 54.3669 29.1578C59.038 27.3368 66.0513 25.1828 78.9709 24.5898C91.1942 24.0371 95.9313 23.8727 120.626 23.8444V23.8781ZM203.241 45.8785C194.462 45.8785 187.341 52.9914 187.341 61.773C187.341 70.5505 194.462 77.6728 203.241 77.6728C212.019 77.6728 219.14 70.5505 219.14 61.773C219.14 52.9941 212.019 45.8731 203.24 45.8731L203.241 45.8785ZM132.512 64.4553C94.9332 64.4553 64.4674 94.9219 64.4674 132.5C64.4674 170.078 94.9346 200.53 132.513 200.53C170.092 200.53 200.546 170.078 200.546 132.5C200.546 94.9219 170.088 64.4553 132.509 64.4553H132.512ZM132.512 88.3333C156.905 88.3333 176.68 108.107 176.68 132.5C176.68 156.892 156.903 176.667 132.512 176.667C108.12 176.667 88.3455 156.892 88.3455 132.5C88.3455 108.106 108.118 88.3333 132.512 88.3333Z"
          fill="currentColor"
        />
      </g>
      <defs>
        <clipPath id="clip0_2623_9670">
          <rect width="264.583" height="264.583" fill="currentColor" />
        </clipPath>
      </defs>
    </svg>
  );
}

