import { useCallback, useRef, useState } from 'react';
import { motion, useAnimationFrame, useMotionValue, useReducedMotion } from 'framer-motion';
import { ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react';

import type { OpportunityVehicle } from '../../../api/cardeep';
import { useOpportunities } from './useOpportunities';

const SPRING = { type: 'spring', stiffness: 120, damping: 22, mass: 0.9 } as const;

/* Photograph-first, small. The reference the owner gave is a travel site's
 * "Popular Destinations" rail: the picture IS the card, and the words sit on top
 * of it at the bottom edge.
 *
 * The version before this one was a thumbnail beside a text block — legible, and
 * completely inert. A car is bought with the eyes first, so the image gets the
 * whole tile and the type earns its place over it. Same footprint, an order of
 * magnitude more appetite. */
const CARD_W = 158;
const CARD_H = 112;
const GAP = 10;
const STEP = CARD_W + GAP;

/**
 * Track speed in px/s.
 *
 * 26 was too slow to register as motion at all. Measured in the browser, the rail
 * was moving exactly as designed — 39px in 1.5s — but at that rate a 158px card
 * takes six seconds to cross its own width, and a glance lasts about one. The
 * rail read as a static row of tiles, which is the worst of both: the cost of an
 * animation frame every frame, and none of the signal that the index is live.
 *
 * 56 puts a card's width at about three seconds. Fast enough that the movement is
 * unmistakable in the first second of the page, slow enough that a price and a
 * model still resolve as they pass — and it stops under the pointer, which is
 * where actual reading happens.
 */
const SPEED = 56;

const eur = (n: number) => `${n.toLocaleString('es-ES')} €`;

/**
 * One opportunity.
 *
 * The discount is the headline, because it is the only thing here that is ours:
 * the photograph, the model and the price all come from the listing, while
 * "−34%" is Cardeep's own reading of that price against every comparable car in
 * the index. It is rendered as a percentage rather than in euros because a share
 * is legible without knowing the segment — 3.000 € under is a rounding error on
 * a Urus and a third of the price on a Panda.
 */
function OpportunityCard({ v, index }: { v: OpportunityVehicle; index: number }) {
  const [broken, setBroken] = useState(false);
  const reduced = useReducedMotion();

  return (
    <motion.a
      href="/marketplace"
      initial={reduced ? false : { opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...SPRING, delay: Math.min(index, 8) * 0.045 }}
      style={{ width: CARD_W, height: CARD_H }}
      className="group relative block shrink-0 overflow-hidden rounded-2xl bg-ink ring-1 ring-white/10 transition-shadow duration-300 hover:ring-white/25 hover:shadow-[0_18px_40px_-20px_rgb(18_110_253/0.55)]"
    >
      {!broken && (
        <img
          src={v.photo}
          alt=""
          loading="lazy"
          decoding="async"
          referrerPolicy="no-referrer"
          onError={() => setBroken(true)}
          className="absolute inset-0 h-full w-full object-cover transition-transform duration-[900ms] ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:scale-[1.07]"
        />
      )}

      {/* The veil. A gradient only across the lower half, so the photograph keeps
          its top two thirds and the type still clears its background. */}
      <span
        aria-hidden
        className="absolute inset-x-0 bottom-0 h-2/3"
        style={{ background: 'linear-gradient(180deg, rgb(5 20 44/0) 0%, rgb(5 20 44/0.82) 72%, rgb(5 20 44/0.94) 100%)' }}
      />

      {v.savings_pct !== null && (
        <span
          title={`${eur(v.savings_eur)} por debajo de la mediana de ${v.cohort_n} coches comparables`}
          className="absolute right-1.5 top-1.5 rounded-md bg-emerald-400/20 px-1.5 py-[2px] text-[10px] font-semibold tabular-nums text-emerald-200 backdrop-blur-sm"
        >
          −{v.savings_pct}%
        </span>
      )}

      <div className="absolute inset-x-0 bottom-0 p-2">
        <p className="truncate text-[11.5px] font-semibold leading-tight text-white">
          {v.make} {v.model}
        </p>
        <div className="mt-0.5 flex items-baseline justify-between gap-1.5">
          <span className="whitespace-nowrap text-[12.5px] font-semibold leading-none tracking-[-0.02em] tabular-nums text-white/95">
            {eur(v.price)}
          </span>
          <span className="shrink-0 text-[9.5px] tabular-nums text-white/50">{v.year}</span>
        </div>
      </div>
    </motion.a>
  );
}

/**
 * The opportunity rail along the floor of the cover.
 *
 * The list is rendered twice and translated by exactly one copy's width, so the
 * seam never shows and the loop never visibly restarts. Constant velocity is the
 * one place linear timing is right — easing a marquee makes it breathe like a
 * failing engine. It stops under the pointer so a card can be read.
 *
 * The arrows are NOT decoration and NOT conditional. Driving the rail purely by
 * the drift leaves anyone browsing with `prefers-reduced-motion` — a system
 * setting, not an exotic case — staring at a strip that neither moves nor can be
 * moved. Honouring the preference means removing the automatic motion, never
 * removing the way through.
 *
 * Width is capped at roughly half the section: the rail belongs under the text
 * column, not under the search panel. A full-width rail turned the bottom of the
 * cover into a second competing surface.
 */
export function MarketStrip() {
  const { items, ready } = useOpportunities(10);
  const reduced = useReducedMotion();

  const x = useMotionValue(0);
  const hovering = useRef(false);
  const nudge = useRef(0); // pixels the arrows still owe the track
  const span = (CARD_W + GAP) * items.length;

  useAnimationFrame((_, delta) => {
    if (!span) return;
    const dt = Math.min(delta, 48) / 1000; // a backgrounded tab must not teleport the rail
    let next = x.get();

    if (nudge.current !== 0) {
      const stepPx = nudge.current * Math.min(1, dt * 6);
      next -= stepPx;
      nudge.current -= stepPx;
      if (Math.abs(nudge.current) < 0.5) nudge.current = 0;
    } else if (!reduced && !hovering.current) {
      next -= dt * SPEED;
    }

    if (next <= -span) next += span;
    if (next > 0) next -= span;
    x.set(next);
  });

  const page = useCallback((dir: 1 | -1) => {
    nudge.current += dir * STEP * 2;
  }, []);

  if (!items.length) return null;

  const loop = [...items, ...items];
  const asOf = items[0]?.as_of ? new Date(items[0].as_of) : null;
  const hours = asOf ? Math.floor((Date.now() - asOf.getTime()) / 3_600_000) : null;
  const freshness =
    hours === null ? null : hours < 48 ? `hace ${hours} h` : `hace ${Math.floor(hours / 24)} días`;

  return (
    <section
      aria-label="Oportunidades detectadas en el índice"
      className="relative w-full px-4 sm:px-6 lg:max-w-[54%] lg:px-8"
    >
      <div className="mb-2.5 flex items-end justify-between gap-4">
        <p className="text-[12px] font-medium text-white/50">
          Por debajo de su mercado
          {/* The verdict is a snapshot. Saying how old it is costs one clause and
              is the difference between a measurement and a boast. */}
          {freshness && <span className="text-white/30"> · calculado {freshness}</span>}
        </p>

        <div className="flex shrink-0 items-center gap-1.5">
          {([[-1, ChevronLeft], [1, ChevronRight]] as const).map(([dir, Icon]) => (
            <motion.button
              key={dir}
              type="button"
              onClick={() => page(dir)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.92 }}
              transition={SPRING}
              aria-label={dir < 0 ? 'Anteriores' : 'Siguientes'}
              className="glass-chip-dark flex h-7 w-7 items-center justify-center rounded-full text-white/70 hover:text-white"
            >
              <Icon size={14} />
            </motion.button>
          ))}
          <motion.a
            href="/marketplace"
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            transition={SPRING}
            className="glass-chip-dark group ml-0.5 flex h-7 items-center gap-1.5 rounded-full px-3 text-[11.5px] font-medium text-white"
          >
            Ver todas
            <ArrowRight size={12} className="transition-transform duration-300 group-hover:translate-x-0.5" />
          </motion.a>
        </div>
      </div>

      {/* The rail dissolves into the page at both ends instead of being chopped. */}
      <div
        className="overflow-hidden"
        onPointerEnter={() => (hovering.current = true)}
        onPointerLeave={() => (hovering.current = false)}
        /* Faded on the RIGHT only. A symmetric mask ate the left edge of the first
         * card — at this size that is a third of a price — while the rail's left
         * edge is already the section's own margin and needs no softening. The
         * right edge is where the rail runs off the page, so that is where the
         * dissolve belongs. */
        style={{
          maskImage: 'linear-gradient(90deg, #000 0%, #000 92%, transparent)',
          WebkitMaskImage: 'linear-gradient(90deg, #000 0%, #000 92%, transparent)',
        }}
      >
        <motion.div className="flex w-max" style={{ gap: GAP, x }}>
          {loop.map((v, i) => (
            <OpportunityCard key={`${v.id}-${i}`} v={v} index={i} />
          ))}
        </motion.div>
      </div>
      {!ready && <div style={{ height: CARD_H }} />}
    </section>
  );
}
