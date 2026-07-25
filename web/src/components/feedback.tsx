import { useLayoutEffect, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { PRINCIPLES, PRINCIPLES_CTA, PRINCIPLES_HEADING, type Principle } from '@/content/site';
import { cn } from '@/lib/utils';

/**
 * One working principle, on the dark card the reference used for testimonials.
 *
 * `glass-dark` is built for panels that already sit on a dark section; this card
 * floats on the light page, so a full-bleed ink tint is painted as a pseudo
 * element — above the panel background, below the grid and the halo. The blur,
 * the hairline and the outer shadow still come from the utility, and the tint
 * keeps the white copy at AA while letting the ambient bloom read through.
 */
function PrincipleCard({ mark, title, body }: Principle) {
  return (
    <div className="glass-dark text-natural-white relative flex min-h-full w-full shrink-0 flex-col gap-30 overflow-hidden rounded-3xl p-8 before:absolute before:inset-0 before:bg-natural-black/80 before:content-[''] lg:w-170">
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
      <div className="relative z-10">
        <span className="text-natural-white/50 flex h-10 items-center font-mono text-2xl tracking-wider">
          {mark}
        </span>
      </div>
      <div className="relative z-10 flex flex-col gap-8">
        <span className="text-lg leading-6.5 font-medium">{title}</span>
        <p className="text-natural-white/80 text-base leading-6 font-medium">{body}</p>
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
    <section id="principios" className="w-full overflow-hidden">
      <Container className="flex flex-col gap-15 py-20 md:py-30">
        <div className="flex flex-col gap-6 md:flex-row md:justify-between">
          <h2 className="text-heading text-left text-4xl font-semibold tracking-tight md:text-5xl">
            {PRINCIPLES_HEADING}
          </h2>
          <div>
            <Button avatar="/shots/mark.webp">{PRINCIPLES_CTA}</Button>
          </div>
        </div>
        <div className="flex flex-col gap-10">
          <div>
            <div
              ref={trackRef}
              className="flex transition-transform duration-500 ease-out will-change-transform gap-6"
              style={{ transform: `translate3d(-${offset}px, 0, 0)` }}
            >
              {PRINCIPLES.map((principle) => (
                <PrincipleCard key={principle.id} {...principle} />
              ))}
            </div>
          </div>
          <div className="flex w-full items-center justify-center">
            <div className="glass-chip mx-auto flex h-fit w-fit items-center justify-center gap-3 rounded-full px-4 py-3">
              {PRINCIPLES.map((principle, dotIndex) => (
                <button
                  key={principle.id}
                  type="button"
                  aria-label={`Mostrar principio ${dotIndex + 1}`}
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
