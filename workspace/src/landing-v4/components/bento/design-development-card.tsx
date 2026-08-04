import { useCallback, useMemo, useState } from 'react';
import { motion, useReducedMotion, type Variants } from 'framer-motion';

import { Button } from '@landing/components/ui/button';
import { Logo } from '@landing/components/ui/logo';
import { LogoSphere, type SphereItem } from '@landing/components/ui/logo-sphere';
import { BENTO } from '@landing/content/site';
import { cn } from '@landing/lib/utils';

/* -------------------------------------------------------------------------- */
/*                                 Platforms                                  */
/* -------------------------------------------------------------------------- */

type Platform = { name: string; file: string };

/**
 * The seven Spanish platforms Cardeep indexes, each as its OWN official mark.
 *
 * WHAT THIS FIXES. The version this replaces put CAR MARQUE logos on the radar —
 * SEAT, Volkswagen, Renault — and justified it in a comment with "there is no
 * platform logo on disk". That was wrong twice. It was wrong as a fact: every one
 * of these files now exists under `public/logos/platforms`, five pulled from the
 * platforms' own CDNs and one from Wikimedia, with provenance recorded per file in
 * `data/platform-logos.json`. And it was wrong as a method: substituting a
 * different company's logo because the right one was inconvenient is precisely the
 * shortcut this repo forbids. A marque is stock; a platform is a channel. This
 * card is about the channels.
 *
 * WHY THE NEGATIVE VARIANTS. This card is `bg-natural-black` in BOTH themes, so
 * each entry points at whichever artwork is legible on black:
 *   - coches.net, AutoScout24, coches.com, motor.es publish a negative; used.
 *   - Wallapop (#13C1AC), Milanuncios (#18BA5D) and Autocasión (#E6301B) are
 *     single-colour marks that already clear black, so their positive is correct
 *     and no variant is needed — confirmed against the manifest, not assumed.
 *
 * One file, `coches-net-light.svg`, is flagged `derived: true` in the manifest: it
 * is the official artwork with one ink value swapped, because coches.net publishes
 * no negative of the plain wordmark. Not a redraw — no path or proportion differs.
 *
 * Deliberately NOT used here: `autoscout24.svg`, the positive. Its paths carry
 * `class="bcls-1"`/`"bcls-2"` with no `<style>` block defining them, so parts of
 * the lockup fall back to black fill. Verified by reading the file. The negative
 * carries its colours in inline `style` attributes and renders correctly, which is
 * the one this card needs anyway.
 */
const PLATFORMS: readonly Platform[] = [
  { name: 'coches.net', file: '/logos/platforms/coches-net-light.svg' },
  { name: 'AutoScout24', file: '/logos/platforms/autoscout24-light.svg' },
  { name: 'Wallapop', file: '/logos/platforms/wallapop.svg' },
  { name: 'Milanuncios', file: '/logos/platforms/milanuncios.svg' },
  { name: 'Autocasión', file: '/logos/platforms/autocasion.svg' },
  { name: 'coches.com', file: '/logos/platforms/coches-com-light.svg' },
  { name: 'motor.es', file: '/logos/platforms/motor-es-light.svg' },
];

/**
 * How many times the set goes round the sphere.
 *
 * Seven marks alone is a sparse necklace — half of them face away at any moment,
 * so the front would show three or four and read as a broken ring. Two passes give
 * 14 slots: roughly seven legible marks across the near face and seven more
 * dimmed behind, which is enough to close the volume.
 *
 * THREE passes (21 slots) was tried first and rejected on the evidence of a
 * render, not a guess. At that density the marks collided — coches.net sat on top
 * of AutoScout24, coches.com on AutoScout24 again, Milanuncios across motor.es —
 * and a platform logo you cannot read is worse than one that is not there, since
 * being able to read them is the entire point of this card. Density is not the
 * goal; legibility is, and the sphere still reads as full at 14.
 *
 * Repetition does not read as wallpaper, and that is a property of the lattice
 * rather than luck: consecutive slots sit a golden angle (137.5 degrees) apart in
 * longitude, so slot i and slot i+7 — the next copy of the same mark — land 242.5
 * degrees apart and at a different latitude. Two copies of one logo are never
 * neighbours and are almost never in the same hemisphere.
 *
 * It is also the honest reading. Each mark is a bearing Cardeep is pulling stock
 * from, not a directory entry, and the same platform is legitimately being read at
 * several bearings at once.
 */
const PASSES = 2;

/* -------------------------------------------------------------------------- */
/*                                Radar chrome                                */
/* -------------------------------------------------------------------------- */

/**
 * The plate's outer radius, in the 0-100 viewBox.
 *
 * Deliberately equal to the sphere's own radius (`RADIUS_RATIO` = 0.38 of the box,
 * so 38 units here). The first attempt drew rings out to 46 and ticks out to 46,
 * which put the whole rim OUTSIDE the sphere: on screen the ticks read as loose
 * dashes floating around the marks rather than as an instrument the sphere sits
 * in. Matching the radii makes the outer ring land exactly on the sphere's limb
 * and ties the two together.
 */
const PLATE_R = 39;
/** Range rings, as a fraction of the plate's radius. */
const RINGS = [0.42, 0.72, 1] as const;
/** Bearing ticks around the rim; every sixth is a long one, so quadrants read. */
const TICKS = Array.from({ length: 24 }, (_, i) => i);

const EASE: [number, number, number, number] = [0.16, 1, 0.3, 1];

/**
 * The plate the sphere turns above: range rings, bearing ticks and a sweep.
 *
 * The sweep is a conic gradient rather than a drawn line because the gradient
 * carries its own decaying trail — bright at the leading edge, gone about ninety
 * degrees behind. That decay is the whole difference between a radar and a clock
 * hand, and it costs one element.
 *
 * Nothing here animates on its own. `LogoSphere` rotates this entire plate from
 * the sphere's yaw, so the sweep is driven by the same hand that drags the marks:
 * flick the sphere and the sweep spins up with it, let go and both coast down
 * together. Two independent loops would have read as two unrelated animations.
 */
function RadarPlate() {
  return (
    <div className="absolute inset-0">
      {/* Quieter than the first pass, which peaked at 0.42 alpha and read as an
        * opaque blue pie slice sitting ON the marks instead of behind them. The
        * beam is the room's light, not a subject. */}
      <div
        className="absolute inset-0"
        style={{
          clipPath: `circle(${PLATE_R}% at 50% 50%)`,
          background:
            'conic-gradient(from 0deg, rgb(18 110 253 / 0.26) 0deg, rgb(18 110 253 / 0.08) 30deg, rgb(18 110 253 / 0.02) 70deg, transparent 104deg, transparent 360deg)',
        }}
      />
      <svg viewBox="0 0 100 100" className="absolute inset-0 size-full" aria-hidden="true">
        {RINGS.map((r) => (
          <circle
            key={r}
            cx="50"
            cy="50"
            r={r * PLATE_R}
            fill="none"
            stroke="rgb(255 255 255 / 0.07)"
            strokeWidth="0.25"
          />
        ))}
        <line
          x1={50 - PLATE_R}
          y1="50"
          x2={50 + PLATE_R}
          y2="50"
          stroke="rgb(255 255 255 / 0.05)"
          strokeWidth="0.25"
        />
        <line
          x1="50"
          y1={50 - PLATE_R}
          x2="50"
          y2={50 + PLATE_R}
          stroke="rgb(255 255 255 / 0.05)"
          strokeWidth="0.25"
        />
        {TICKS.map((i) => {
          const angle = (i * 15 * Math.PI) / 180;
          const major = i % 6 === 0;
          const inner = PLATE_R - (major ? 4 : 2);
          return (
            <line
              key={i}
              x1={50 + Math.sin(angle) * inner}
              y1={50 - Math.cos(angle) * inner}
              x2={50 + Math.sin(angle) * PLATE_R}
              y2={50 - Math.cos(angle) * PLATE_R}
              stroke={major ? 'rgb(255 255 255 / 0.22)' : 'rgb(255 255 255 / 0.1)'}
              strokeWidth="0.35"
            />
          );
        })}
      </svg>
    </div>
  );
}

/**
 * Cardeep at the centre of the sphere.
 *
 * The composition is the argument: the marks are the market, orbiting; the one
 * fixed, lit thing they orbit is Cardeep. Because the core sits on the z = 0 plane
 * the near marks pass in FRONT of it and the far ones behind, which is what stops
 * the sphere reading as a flat ring with a badge pasted on.
 */
function Core({ still }: { still: boolean }) {
  return (
    <span className="relative flex size-9 items-center justify-center rounded-full border border-white/15 bg-black">
      <motion.span
        aria-hidden
        className="absolute -inset-5 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgb(18 110 253 / 0.4), transparent 70%)',
        }}
        animate={still ? { opacity: 0.7 } : { opacity: [0.45, 0.85, 0.45] }}
        transition={still ? { duration: 0 } : { duration: 3.4, repeat: Infinity, ease: 'easeInOut' }}
      />
      <Logo tone="light" className="relative size-[18px]" />
    </span>
  );
}

/**
 * Chip geometry, in px.
 *
 * These are not styling choices, they are part of the projection, which is why
 * they live as numbers and are applied inline rather than as arbitrary Tailwind
 * values. `LogoSphere` puts the sphere's radius at 39% of its box precisely so the
 * remaining 11% per side can hold half a chip: at the 380px cap this card gives it
 * that is 41.8px of margin against a 41px half-chip, so a mark sitting on the limb
 * at three or nine o'clock lands just inside the card instead of being clipped by
 * it. Change `CHIP_W` and `RADIUS_RATIO` has to move with it.
 */
const CHIP_W = 82;
const CHIP_H = 27;
/** The mark's box inside the chip, leaving a consistent optical inset. */
const MARK_W = 68;
const MARK_H = 14;

/**
 * One platform mark, as a chip on the sphere.
 *
 * Fixed width, not intrinsic: all seven are wide wordmarks but their aspect ratios
 * run from 3.5:1 (coches.com) to 6.5:1 (coches.net), and letting each chip take its
 * logo's own width would give the sphere seven different chip sizes and no rhythm.
 * A common chip with `object-contain` inside lets every mark keep its own
 * proportions while the field stays even. It also means the widest wordmark is
 * bounded by `MARK_W` and the squarest by `MARK_H`, so none of them out-sizes the
 * rest — which is the failure mode that made an earlier Wallapop asset, whose
 * artwork filled only part of its viewBox, render visibly tiny next to its
 * neighbours.
 *
 * `draggable={false}` is load-bearing, not hygiene: without it the browser's native
 * image drag steals the pointer the moment a drag starts on a logo, and since the
 * logos cover most of the sphere the whole interaction would appear broken.
 */
function PlatformChip({ platform }: { platform: Platform }) {
  return (
    <span
      className="flex items-center justify-center rounded-full border border-white/12 bg-white/[0.06] px-2 transition-colors duration-200 hover:border-white/35 hover:bg-white/[0.12]"
      style={{ width: CHIP_W, height: CHIP_H }}
    >
      <img
        src={platform.file}
        alt=""
        loading="lazy"
        draggable={false}
        className="object-contain"
        style={{ maxWidth: MARK_W, maxHeight: MARK_H }}
      />
    </span>
  );
}

/**
 * The line under the sphere.
 *
 * At rest it names what is on screen and teaches the affordance in the same
 * breath, which is the only honest way to advertise a drag surface — a sphere that
 * spins by itself gives no hint that it can be grabbed. On hover it swaps for the
 * platform under the cursor.
 *
 * Both states are always mounted and cross-faded on opacity, and `name` keeps the
 * last platform after the pointer leaves, so the label fades out instead of
 * blanking mid-transition.
 *
 * They are stacked with GRID rather than absolute positioning, which is the whole
 * trick here. Both children are placed in the same cell, so they overlap for the
 * crossfade AND both still contribute to the row's height — the row is always as
 * tall as its tallest state and never shifts the copy underneath. The first
 * attempt used `absolute inset-0` inside a fixed `h-5`, which looked right on a
 * desktop column and broke at 375px, where the hint wraps to two lines and the
 * second line escaped the box.
 */
function Readout({ name, active }: { name: string; active: boolean }) {
  const base =
    'col-start-1 row-start-1 flex items-center justify-center gap-2 text-center transition-opacity duration-300';

  return (
    <div className="mt-4 grid">
      <span
        className={cn(
          base,
          'text-[10px] tracking-[0.16em] text-white/40 uppercase',
          active ? 'opacity-0' : 'opacity-100',
        )}
      >
        Plataformas indexadas · arrastra para girar
      </span>
      {/* Not uppercased: these are brand names, and `coches.net` is not `COCHES.NET`. */}
      <span
        className={cn(base, 'text-xs text-white/85', active ? 'opacity-100' : 'opacity-0')}
        aria-live="polite"
      >
        <span className="bg-brand size-1 shrink-0 rounded-full" />
        {name}
      </span>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

const CARD: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.14, delayChildren: 0.04 } },
};

const RISE: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.65, ease: EASE } },
};

/**
 * The feature tile: "Índice nacional".
 *
 * Two things were wrong with what this replaces and both are fixed here rather
 * than restyled. It showed car marques instead of the platforms the card is about
 * (see `PLATFORMS`), and it did not respond to input at all — a conic gradient on
 * a CSS loop over twelve fixed positions, which is a picture OF a radar. This is a
 * real sphere you can grab, throw and stop, whose marks dim and shrink as they go
 * round the back, over a plate driven by the same gesture.
 *
 * It also had `initial="hidden" whileInView="visible"` with no `variants` anywhere
 * on the subtree, so the entrance it appeared to declare did nothing. The variants
 * exist now and the two blocks stagger in.
 */
export function DesignDevelopmentCard() {
  const prefersReduced = useReducedMotion();
  const still = prefersReduced === true;

  const [hovered, setHovered] = useState<string | null>(null);
  const [lastName, setLastName] = useState(PLATFORMS[0].name);

  const handleHover = useCallback((name: string | null) => {
    setHovered(name);
    if (name) setLastName(name);
  }, []);

  /** Slots walk the platform list, so copy n of a mark lands 7 lattice steps on. */
  const items = useMemo<SphereItem[]>(
    () =>
      Array.from({ length: PLATFORMS.length * PASSES }, (_, i) => {
        const platform = PLATFORMS[i % PLATFORMS.length];
        return {
          key: `${platform.name}-${i}`,
          name: platform.name,
          node: <PlatformChip platform={platform} />,
        };
      }),
    [],
  );

  /* Built from the data so it can never drift from what is actually rendered.
   * Every chip is aria-hidden — a screen reader reading the same seven marks
   * `PASSES` times over is noise, not access — so this sentence is the whole
   * description. */
  const label = `Esfera interactiva con las plataformas que indexa Cardeep: ${PLATFORMS.map((p) => p.name).join(', ')}. Arrástrala con el ratón o gírala con las flechas del teclado.`;

  return (
    <motion.div
      className="bg-natural-black relative col-span-19 grid overflow-hidden rounded-2xl p-4 lg:col-span-6"
      variants={CARD}
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
        <motion.div variants={RISE} className="px-2 pt-6 pb-2">
          {/* Capped because below `lg` this card spans the full grid and would
            * otherwise blow the sphere up to the width of the page. 380px is
            * sized to the lg column (6 of 19 minus padding), so at the breakpoint
            * that matters the instrument fills its card instead of floating in
            * the middle of it. */}
          <div className="mx-auto w-full max-w-[380px]">
            <LogoSphere
              items={items}
              label={label}
              onHoverChange={handleHover}
              backdrop={<RadarPlate />}
              core={<Core still={still} />}
            />
          </div>
          <Readout name={lastName} active={hovered !== null} />
        </motion.div>

        <motion.div variants={RISE} className="mt-4 flex flex-col gap-6 px-4 py-4">
          <div className="relative">
            <h2 className="text-base font-medium text-white">{BENTO.feature.title}</h2>
            <p className="mt-4 text-base text-neutral-400">{BENTO.feature.body}</p>
          </div>
          <div>
            <Button className="my-4">{BENTO.feature.cta}</Button>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
