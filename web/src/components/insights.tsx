import { useLayoutEffect, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import {
  CAPABILITIES,
  CAPABILITIES_CTA,
  CAPABILITIES_HEADING,
  type Capability,
} from '@/content/site';
import { cn } from '@/lib/utils';

/**
 * Sits where the reference put a quote bubble. These cards state what the index
 * guarantees, not what somebody said about it, so the glyph is a check inside a
 * panel — same 24px box, same stroke weight and colour as the mark it replaces.
 */
function VerifiedIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect
        x="3"
        y="3"
        width="18"
        height="18"
        rx="4"
        stroke="#343434"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path
        d="M8 12.25L10.75 15L16 9.5"
        stroke="#343434"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function CapabilityCard({ mark, title, body }: Capability) {
  return (
    <div className="glass flex min-h-full w-full shrink-0 flex-col items-start justify-start gap-12 overflow-hidden rounded-3xl px-8 pt-8 pb-6 md:w-147">
      <div className="flex w-full items-center justify-between">
        <span className="text-muted-foreground font-mono text-sm leading-6 tracking-wider uppercase">
          {mark}
        </span>
        <VerifiedIcon />
      </div>
      <div className="flex h-full flex-col items-start justify-between gap-8">
        <div className="flex flex-col items-start justify-start gap-6 self-stretch">
          <div className="text-natural-black text-lg leading-6 font-medium">{title}</div>
        </div>
        <p className="text-heading text-base leading-6 font-medium">{body}</p>
      </div>
    </div>
  );
}

/**
 * Capability carousel driven by a plain CSS transform transition — the track is
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
            {CAPABILITIES_HEADING}
          </h2>
          <Button avatar="/shots/mark.webp">{CAPABILITIES_CTA}</Button>
        </div>
        <div className="flex flex-col gap-10">
          <div className="_overflow-hidden">
            <div
              ref={trackRef}
              className="flex gap-6 transition-transform duration-500 ease-out will-change-transform"
              style={{ transform: `translate3d(-${offset}px, 0, 0)` }}
            >
              {CAPABILITIES.map((capability) => (
                <CapabilityCard key={capability.id} {...capability} />
              ))}
            </div>
          </div>
          <div className="flex w-full items-center justify-center">
            <div className="glass-chip mx-auto flex h-fit w-fit items-center justify-center gap-3 rounded-full px-4 py-3">
              {CAPABILITIES.map((capability, dotIndex) => (
                <button
                  key={capability.id}
                  type="button"
                  aria-label={`Mostrar capacidad ${dotIndex + 1}`}
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
