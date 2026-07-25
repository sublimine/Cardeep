import Marquee from 'react-fast-marquee';

import { Container } from '@/components/ui/container';
import { MISSION, SOURCES } from '@/content/site';

export function FoundersDesk() {
  return (
    <section
      id="mision"
      className="bg-natural-black text-natural-white relative w-full overflow-hidden"
    >
      <div className="absolute inset-0">
        <div className="relative h-full w-full">
          <div className="absolute top-71 -left-140 h-125.5 w-122 rounded-full bg-white blur-[214px]" />
          <div className="absolute top-0 -left-40 h-293 w-180 rounded-full bg-[#27251F] blur-[287px]" />
          <div className="absolute top-0 -right-100 h-293.75 w-180 rounded-full bg-[#27251F] blur-[287px]" />
          <div className="absolute top-10 right-52 h-141 w-197 bg-[linear-gradient(to_right,#181816_1px,transparent_1px),linear-gradient(to_bottom,#181816_1px,transparent_1px)] bg-size-[44px_44px] mask-[radial-gradient(circle,black_10%,transparent_100%)]" />
        </div>
      </div>
      <Container className="relative z-20 flex w-full flex-col gap-20 pt-20 pb-30">
        <div className="-tracking-xl text-6xl leading-18 font-medium">{MISSION.kicker}</div>
        <div className="grid w-full grid-cols-1 justify-between gap-30 lg:grid-cols-5">
          <div className="relative lg:col-span-2">
            <img
              alt={MISSION.imageAlt}
              loading="lazy"
              width={944}
              height={944}
              decoding="async"
              className="w-full rounded-lg"
              src="/shots/mision.webp"
            />
          </div>
          <div className="flex h-full w-full flex-col justify-between gap-15 lg:col-span-3">
            <div className="flex flex-col gap-6">
              <div className="flex justify-end">
                {/* Wrapping keeps the three figures inside the section's
                    overflow-hidden on narrow viewports; at lg they stay on one row. */}
                <div className="flex flex-wrap items-center justify-end gap-5">
                  {MISSION.stats.map(({ value, label }) => (
                    <div
                      key={label}
                      className="glass-chip-dark flex items-baseline gap-2 rounded-full px-4 py-1.5"
                    >
                      <span className="-tracking-xs text-sm leading-6.5 font-medium">{value}</span>
                      <span className="-tracking-xs text-muted-foreground text-sm leading-6.5 font-medium">
                        {label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <span className="-tracking-xs text-lg leading-6.5 font-medium">
                {MISSION.paragraphs[0]}
              </span>
              <span className="-tracking-xs text-lg leading-6.5 font-medium">
                {MISSION.paragraphs[1]}
                <br />
                {MISSION.closing}
              </span>
            </div>
            <div>
              <div className="relative w-full overflow-hidden flex h-full max-h-22 items-center mask-[linear-gradient(to_right,transparent,black_20%,black_80%,transparent)]">
                {/* Speed and direction stay the reference defaults (50px/s, leftward),
                    so no props are passed; only the chip row's content changed. */}
                <Marquee>
                  {SOURCES.map(({ name, mark, accent }) => (
                    <div key={name} className="mx-2">
                      <SourceMark mark={mark} accent={accent} />
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

type SourceMarkProps = {
  mark: string;
  accent: string;
};

/** Typographic wordmark for one indexed platform: name plus its muted suffix. */
function SourceMark({ mark, accent }: SourceMarkProps) {
  return (
    <div className="glass-dark flex items-center rounded-xl px-5 py-3">
      <span className="-tracking-xs text-sm leading-5 font-medium">{mark}</span>
      {accent ? (
        <span className="-tracking-xs text-muted-foreground text-sm leading-5 font-medium">
          {accent}
        </span>
      ) : null}
    </div>
  );
}
