import { useEffect, useRef } from 'react';
import { animate, motion, useMotionValue, useMotionValueEvent, useReducedMotion } from 'framer-motion';

import { HERO } from '@landing/content/site';
import type { Stats } from '../../../api/cardeep';
import { useResultCount } from './useResultCount';

const EXPO = [0.16, 1, 0.3, 1] as const;
const SPRING = { type: 'spring', stiffness: 130, damping: 20, mass: 0.8 } as const;

/**
 * A census figure that counts up to its real value once.
 *
 * The number is written straight to the DOM node from a motion value. Routing it
 * through React state would re-render this column sixty times a second for a
 * purely visual flourish. It always lands on the exact figure the API returned —
 * the animation is how the number arrives, never what it says.
 */
function Counter({ value }: { value: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const mv = useMotionValue(0);
  const reduced = useReducedMotion();

  useMotionValueEvent(mv, 'change', (v) => {
    if (ref.current) ref.current.textContent = Math.round(v).toLocaleString('es-ES');
  });

  useEffect(() => {
    if (reduced) {
      if (ref.current) ref.current.textContent = value.toLocaleString('es-ES');
      return;
    }
    const controls = animate(mv, value, { duration: 1.6, ease: [0.16, 1, 0.3, 1] });
    return () => controls.stop();
  }, [value, reduced, mv]);

  return <span ref={ref}>0</span>;
}

/** One line of the headline, revealed word by word from behind its own edge. */
function Line({ text, accent, order }: { text: string; accent: boolean; order: number }) {
  const reduced = useReducedMotion();
  return (
    <span className="block">
      {text.split(' ').map((word, i) => (
        <span key={`${word}-${i}`} className="inline-block overflow-hidden pb-[0.06em] align-bottom">
          <motion.span
            className={'inline-block ' + (accent ? 'text-brand' : '')}
            initial={reduced ? false : { y: '115%', rotate: 4 }}
            animate={{ y: '0%', rotate: 0 }}
            transition={{ ...SPRING, delay: 0.06 + order * 0.16 + i * 0.055 }}
          >
            {word}
          </motion.span>
          {i < text.split(' ').length - 1 && <span>&nbsp;</span>}
        </span>
      ))}
    </span>
  );
}

/**
 * The left column: the claim, the reason, and the two ways in.
 *
 * The headline is the page's argument, so it gets the only theatrical motion —
 * each word rises from behind its own edge with a slight rotation, staggered
 * along the line. Everything below it fades in behind it, and the figures count
 * up to what the census actually says.
 */
export function HeroCopy({ stats }: { stats: Stats | null }) {
  const reduced = useReducedMotion();
  /* The same source the button quotes, not /stats.
   *
   * Both answer "how many cars", and until the cube was rebuilt on the canonical
   * grain they answered differently — /stats is precomputed into `product_stats`
   * and drifts a few hundred rows behind the live index. The definitions now agree,
   * but the SNAPSHOTS still would not, and a headline that says 1.482.719 above a
   * button that says 1.483.272 invites exactly the question a landing page cannot
   * afford. One query, one number, no explaining. `/search/count` with no filters
   * is cached and already fetched by the panel, so this costs nothing. */
  const { data: count } = useResultCount({});
  const total = count?.count ?? stats?.vehicles_unique_available ?? null;
  const rise = (delay: number) => ({
    initial: reduced ? false : { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.8, ease: EXPO, delay },
  });

  return (
    <div className="w-full shrink lg:max-w-[min(640px,48vw)]">
      {/* The eyebrow does two jobs at once: it says what this is before the
        * headline makes its claim, and "en vivo" pre-empts the question the
        * claim invites — how old is this? */}
      <motion.p
        {...rise(0.02)}
        className="mb-4 flex items-center gap-2 text-[11.5px] font-semibold uppercase tracking-[0.18em] text-white/55"
      >
        <span className="bg-brand h-1.5 w-1.5 rounded-full" />
        {HERO.eyebrow}
      </motion.p>
      <h1 className="text-[clamp(2.4rem,1.2rem+4.8vw,4.6rem)] font-semibold leading-[0.95] tracking-[-0.045em] text-white">
        {HERO.titleLines.map((line, i) => (
          <Line key={line} text={line} accent={i === HERO.titleLines.length - 1} order={i} />
        ))}
      </h1>

      {/**
        * The scale figure lives INSIDE the sentence now.
        *
        * What used to sit here was a row of three counters — vehicles, points of
        * sale, provinces — plus two buttons, on a page that already offered the
        * same two destinations from the navbar, the search panel and the rail
        * below. Four ways into one product on one screen is not generosity, it is
        * indecision, and the visitor pays for it by having to choose. The panel on
        * the right is the way in; this column is the argument for using it.
        *
        * The number still counts up, because watching it climb is what makes a
        * quantity feel like an inventory rather than a claim — it simply does that
        * inside the line it is arguing for.
        */}
      <motion.p {...rise(0.46)} className="mt-6 max-w-[48ch] text-[16.5px] leading-[1.55] text-white/75">
        {total !== null ? (
          <>
            <span className="font-semibold tabular-nums text-white">
              <Counter value={total} />
            </span>
            {HERO.subtitle.replace('{n}', '')}
          </>
        ) : (
          HERO.subtitleNoCount
        )}
      </motion.p>
      {/* The second line is the only sentence on the page whose verb belongs to
        * the reader. That is the whole correction: the version before this said
        * "Sabemos cuál vale lo que pide" — the company knows, and the reader is
        * handed nothing. */}
      <motion.p {...rise(0.56)} className="mt-2.5 max-w-[46ch] text-[15px] leading-[1.55] text-white/55">
        {HERO.subtitleSecond}
      </motion.p>
    </div>
  );
}
