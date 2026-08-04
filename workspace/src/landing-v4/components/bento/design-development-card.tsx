import { motion, useReducedMotion } from 'framer-motion';

import { Button } from '@landing/components/ui/button';
import { BENTO } from '@landing/content/site';

/* -------------------------------------------------------------------------- */
/*                                   Radar                                    */
/* -------------------------------------------------------------------------- */

/**
 * Seconds for one full sweep.
 *
 * Slow enough that the beam reads as an instrument scanning rather than a
 * spinner, and slow enough that a marque stays lit long enough to be recognised
 * after the beam has passed it.
 */
const SWEEP_S = 7;

/** Range rings, as a fraction of the radar's radius. */
const RINGS = [0.34, 0.62, 0.9] as const;

/**
 * What the sweep finds.
 *
 * Every entry is a real file in `public/logos` — checked against the directory,
 * not assumed. There is no platform logo on disk (coches.net, AutoScout24,
 * Wallapop and the rest ship no asset), and inventing one is not an option, so
 * the radar shows what the index is actually FULL of: marques. That is also the
 * truer picture — the platforms are channels, the marques are the stock.
 *
 * `a` is the bearing in degrees clockwise from twelve o'clock, `r` the distance
 * from centre as a fraction of the radius. Positions are hand-placed rather than
 * generated: an even ring reads as decoration, an uneven scatter reads as a
 * reading.
 */
const BLIPS = [
  { file: 'seat.svg', name: 'SEAT', a: 22, r: 0.5 },
  { file: 'volkswagen.svg', name: 'Volkswagen', a: 58, r: 0.82 },
  { file: 'renault.svg', name: 'Renault', a: 96, r: 0.44 },
  { file: 'peugeot.svg', name: 'Peugeot', a: 133, r: 0.74 },
  { file: 'citroen.svg', name: 'Citroën', a: 168, r: 0.36 },
  { file: 'opel.svg', name: 'Opel', a: 196, r: 0.66 },
  { file: 'ford.svg', name: 'Ford', a: 228, r: 0.86 },
  { file: 'toyota.svg', name: 'Toyota', a: 254, r: 0.42 },
  { file: 'kia.svg', name: 'Kia', a: 288, r: 0.7 },
  { file: 'hyundai.svg', name: 'Hyundai', a: 316, r: 0.34 },
  { file: 'audi.svg', name: 'Audi', a: 340, r: 0.78 },
  { file: 'bmw.svg', name: 'BMW', a: 8, r: 0.9 },
] as const;

/** Polar bearing to a percentage offset inside the square radar box. */
function place(a: number, r: number) {
  const rad = ((a - 90) * Math.PI) / 180;
  return {
    left: `${50 + Math.cos(rad) * r * 46}%`,
    top: `${50 + Math.sin(rad) * r * 46}%`,
  };
}

/**
 * A marque, lit as the beam crosses it.
 *
 * The pulse is not on a loop of its own — its delay is derived from the blip's
 * own bearing, so it fires exactly when the sweep arrives and the two never drift
 * apart. That coupling is the whole illusion: a light that pulses NEAR a rotating
 * line is decoration; a light that pulses BECAUSE the line reached it is an
 * instrument.
 */
function Blip({ blip, index }: { blip: (typeof BLIPS)[number]; index: number }) {
  const reduced = useReducedMotion();
  const delay = (blip.a / 360) * SWEEP_S;

  return (
    <motion.span
      className="absolute flex size-8 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-[10px] border border-white/12 bg-white/[0.06]"
      style={place(blip.a, blip.r)}
      initial={reduced ? false : { opacity: 0, scale: 0.7 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.5, delay: 0.15 + index * 0.06, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* `invert` because the self-hosted marks are black-on-transparent and this
        * card is the page's darkest surface. */}
      <img
        src={`/logos/${blip.file}`}
        alt={blip.name}
        loading="lazy"
        className="max-h-4 max-w-4 object-contain opacity-85 invert"
      />
      {!reduced && (
        <motion.span
          aria-hidden
          className="ring-brand absolute inset-0 rounded-[10px] ring-1"
          animate={{ opacity: [0, 0.9, 0], scale: [1, 1.45, 1.75] }}
          transition={{
            duration: 1.5,
            delay,
            repeat: Infinity,
            repeatDelay: SWEEP_S - 1.5,
            ease: 'easeOut',
          }}
        />
      )}
    </motion.span>
  );
}

/**
 * The instrument.
 *
 * BUILT IN CSS AND DOM, NOT THREE.JS. The repo ships @react-three/fiber and drei,
 * so a rotating logo sphere was available, and it was rejected on cost: three plus
 * drei is hundreds of kilobytes of JavaScript and a live WebGL context, spent on
 * one tile of a bento grid a visitor may never scroll to. This is a conic
 * gradient, three rings and twelve images — one compositor-side rotation, no
 * JavaScript at all once mounted. On a landing page that is the right trade every
 * time.
 *
 * The sweep is a conic gradient rather than a drawn line because that carries a
 * decaying trail for free: bright at the leading edge, gone about ninety degrees
 * behind it. That decay is the difference between a radar and a clock hand.
 */
function Radar() {
  const reduced = useReducedMotion();

  return (
    <div className="relative mx-auto aspect-square w-full max-w-[280px]">
      {/* Range rings and axes. Hairlines only — the grid is a reference, and the
        * moment it competes with the marques for attention it has failed. */}
      <div className="absolute inset-0">
        {RINGS.map((r) => (
          <span
            key={r}
            className="absolute rounded-full border border-white/[0.07]"
            style={{
              left: `${50 - r * 46}%`,
              top: `${50 - r * 46}%`,
              width: `${r * 92}%`,
              height: `${r * 92}%`,
            }}
          />
        ))}
        <span className="absolute top-1/2 left-[4%] h-px w-[92%] bg-white/[0.05]" />
        <span className="absolute top-[4%] left-1/2 h-[92%] w-px bg-white/[0.05]" />
      </div>

      {/* The beam, clipped to the outer ring so it never paints the card's corners. */}
      <div className="absolute inset-0 overflow-hidden" style={{ clipPath: 'circle(46% at 50% 50%)' }}>
        <motion.div
          aria-hidden
          className="absolute inset-0"
          style={{
            background:
              'conic-gradient(from 0deg, rgb(18 110 253 / 0.55) 0deg, rgb(18 110 253 / 0.16) 24deg, rgb(18 110 253 / 0.04) 62deg, transparent 96deg, transparent 360deg)',
          }}
          animate={reduced ? { rotate: 34 } : { rotate: 360 }}
          transition={reduced ? { duration: 0 } : { duration: SWEEP_S, repeat: Infinity, ease: 'linear' }}
        />
      </div>

      {/* The centre: Cardeep's own position. Everything else is measured from it. */}
      <span className="bg-brand absolute top-1/2 left-1/2 size-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full shadow-[0_0_16px_2px_rgb(18_110_253/0.7)]" />

      {BLIPS.map((blip, index) => (
        <Blip key={blip.file} blip={blip} index={index} />
      ))}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

/**
 * The feature tile: "Índice nacional".
 *
 * What this replaces was a mocked browser window — grey chrome, traffic lights,
 * skeleton bars, a placeholder image tile. It said "there is a web app", which is
 * the one claim this section does not need to make and the least interesting
 * thing about the product. The sweep says the real one: Cardeep scans the whole
 * market, continuously, and pulls every marque in it into one index.
 */
export function DesignDevelopmentCard() {
  return (
    <motion.div
      className="bg-natural-black relative col-span-19 grid overflow-hidden rounded-2xl p-4 lg:col-span-6"
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.2 }}
    >
      {/* The bloom the instrument sits in, so the card has a light source rather
        * than a flat black ground. */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-24 left-1/2 size-[420px] -translate-x-1/2 rounded-full opacity-70 blur-3xl"
        style={{ background: 'radial-gradient(circle, rgb(18 110 253 / 0.22), transparent 68%)' }}
      />

      <div className="relative z-10 flex flex-col">
        <div className="px-2 pt-6 pb-2">
          <Radar />
        </div>

        <div className="mt-4 flex flex-col gap-6 px-4 py-4">
          <div className="relative">
            <h2 className="text-base font-medium text-white">{BENTO.feature.title}</h2>
            <p className="mt-4 text-base text-neutral-400">{BENTO.feature.body}</p>
          </div>
          <div>
            <Button className="my-4">{BENTO.feature.cta}</Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
