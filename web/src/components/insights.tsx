import { useLayoutEffect, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { cn } from '@/lib/utils';

type Testimonial = {
  logo: string;
  quote: string;
  avatar: string;
  name: string;
  role: string;
};

const TESTIMONIALS = [
  {
    logo: '/logos/1.webp',
    quote:
      "Excellent communication and professionalism: open to ideas, humble when views differ. We'll re-engage; can't wait for the next job together.",
    avatar: '/avatar/henrik.webp',
    name: 'Henrik Söderlund',
    role: 'CTO at Creme Digital',
  },
  {
    logo: '/logos/7.webp',
    quote:
      'Quick to respond, very professional, and shipped a site within a week. Looking forward to the next collaboration.',
    avatar: '/avatar/asriel.webp',
    name: 'Asriel Han',
    role: 'Founder / CTO at Advex AI',
  },
  {
    logo: '/logos/9.webp',
    quote:
      "The best front-end developer I've worked with. He took the requirements and ran with them. We're delighted with the product.",
    avatar: '/avatar/john.webp',
    name: 'John Shahawy',
    role: 'Founder at Moonbeam',
  },
  {
    logo: '/logos/10.webp',
    quote:
      'Exceptional attention to detail and a collaborative approach. Sarah delivered beyond our expectations.',
    avatar: '/avatar/avatar-1.webp',
    name: 'Sarah Johnson',
    role: 'Product Manager at TechCorp',
  },
  {
    logo: '/logos/11.webp',
    quote:
      'Incredible problem-solving skills and a great team player. Michael consistently delivers high-quality code on time.',
    avatar: '/avatar/avatar-2.webp',
    name: 'Michael Brown',
    role: 'Lead Developer at CodeCraft',
  },
] as const satisfies readonly Testimonial[];

function QuoteIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M22 17C22 17.5304 21.7893 18.0391 21.4142 18.4142C21.0391 18.7893 20.5304 19 20 19H6.828C6.29761 19.0001 5.78899 19.2109 5.414 19.586L3.212 21.788C3.1127 21.8873 2.9862 21.9549 2.84849 21.9823C2.71077 22.0097 2.56803 21.9956 2.43831 21.9419C2.30858 21.8881 2.1977 21.7971 2.11969 21.6804C2.04167 21.5637 2.00002 21.4264 2 21.286V5C2 4.46957 2.21071 3.96086 2.58579 3.58579C2.96086 3.21071 3.46957 3 4 3H20C20.5304 3 21.0391 3.21071 21.4142 3.58579C21.7893 3.96086 22 4.46957 22 5V17Z"
        stroke="#343434"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M14 13C14.5304 13 15.0391 12.7893 15.4142 12.4142C15.7893 12.0391 16 11.5304 16 11V9H14"
        stroke="#343434"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8 13C8.53043 13 9.03914 12.7893 9.41421 12.4142C9.78929 12.0391 10 11.5304 10 11V9H8"
        stroke="#343434"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function TestimonialCard({ logo, quote, avatar, name, role }: Testimonial) {
  return (
    <div className="bg-natural-white shadow-card-lg flex min-h-full w-full shrink-0 flex-col items-start justify-start gap-12 overflow-hidden rounded-3xl px-8 pt-8 pb-6 md:w-147">
      <div className="flex w-full items-center justify-between">
        <img
          alt="Brand Logo"
          loading="lazy"
          width={100}
          height={100}
          decoding="async"
          className="w-20 object-contain"
          src={logo}
        />
        <QuoteIcon />
      </div>
      <div className="flex h-full flex-col items-start justify-between gap-8">
        <div className="flex flex-col items-start justify-start gap-6 self-stretch">
          <div className="text-natural-black text-lg leading-6 font-medium">{quote}</div>
        </div>
        <div className="flex items-center gap-2">
          <img
            alt={name}
            loading="lazy"
            width={48}
            height={48}
            decoding="async"
            className="size-12 rounded-full"
            src={avatar}
          />
          <div className="flex flex-col gap-0.5">
            <div className="text-base leading-6 font-medium">{name}</div>
            <div className="text-muted-foreground text-base leading-6 font-medium">{role}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Testimonial carousel driven by a plain CSS transform transition — the track is
 * translated by the measured distance between slide 0 and the active slide, so
 * the peek layout stays correct at every breakpoint (cards are `w-full` on
 * mobile and a fixed 588px on `md`).
 */
export function Insights() {
  const trackRef = useRef<HTMLDivElement>(null);
  const [index, setIndex] = useState(0);
  const [offset, setOffset] = useState(0);

  useLayoutEffect(() => {
    const track = trackRef.current;
    if (!track) return;

    const measure = () => {
      const slides = Array.from(track.children) as HTMLElement[];
      const first = slides[0];
      const active = slides[index];
      if (!first || !active) return;
      setOffset(active.offsetLeft - first.offsetLeft);
    };

    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, [index]);

  return (
    <section className="w-full">
      <Container className="relative flex flex-col gap-15 py-20 md:py-30 lg:gap-20">
        <div className="flex flex-col items-center justify-between gap-8 md:items-start lg:flex-row lg:items-center">
          <h2 className="text-heading text-4xl font-semibold tracking-tight md:text-5xl text-center md:text-left">
            See Insights straight from our users
          </h2>
          <Button avatar="/manu.webp">Chat with us</Button>
        </div>
        <div className="flex flex-col gap-10">
          <div className="_overflow-hidden">
            <div
              ref={trackRef}
              className="flex gap-6 transition-transform duration-500 ease-out will-change-transform"
              style={{ transform: `translate3d(-${offset}px, 0, 0)` }}
            >
              {TESTIMONIALS.map((testimonial) => (
                <TestimonialCard key={testimonial.name} {...testimonial} />
              ))}
            </div>
          </div>
          <div className="flex w-full items-center justify-center">
            <div className="bg-natural-white shadow-card-lg mx-auto flex h-fit w-fit items-center justify-center gap-3 rounded-full px-4 py-3">
              {TESTIMONIALS.map((testimonial, dotIndex) => (
                <button
                  key={testimonial.name}
                  type="button"
                  aria-label={`Show testimonial ${dotIndex + 1}`}
                  aria-current={dotIndex === index}
                  onClick={() => setIndex(dotIndex)}
                  className={cn(
                    'size-2 cursor-pointer rounded-full transition-all duration-300',
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
