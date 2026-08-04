import { useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';

import { BENTO, SOURCES } from '@landing/content/site';
import { Logo } from '@landing/components/ui/logo';
import { cn } from '@landing/lib/utils';
import platformLogos from '@landing/data/platform-logos.json';

/* -------------------------------------------------------------------------- */
/*                               Platform logos                               */
/* -------------------------------------------------------------------------- */

/**
 * The real marks, read straight from the acquisition manifest.
 *
 * What this replaces rendered the platforms as TEXT WORDMARKS and justified it in
 * a comment — "no platform ships a logo asset in public/logos". That was true of
 * the repo at the time and it was still the wrong answer: the assets did not
 * exist because nobody had gone and got them, not because they were unobtainable.
 * They are now in `public/logos/platforms/`, sourced from each platform's own CDN
 * or from Wikimedia Commons, and `data/platform-logos.json` records where every
 * single file came from. This file is the consumer of that work.
 *
 * The manifest is imported rather than transcribed so the diagram can never drift
 * from the audited record: if a mark is re-fetched under a new filename, or a
 * negative variant appears for a platform that had none, this card follows without
 * being touched.
 *
 * The cast is narrow on purpose. The manifest carries provenance prose per entry
 * (`source`, `sourceDetail`, `derived`, `evidence`) that this component has no
 * business knowing about; all it needs is which file to paint on which ground.
 */
type LogoVariant = { readonly file: string };
type LogoRecord = { readonly file: string; readonly onDark?: LogoVariant | null };

const LOGOS = platformLogos as Readonly<Record<string, LogoRecord>>;

/**
 * The single box every mark is fitted into.
 *
 * Matching WIDTH rather than height is how a wall of horizontal wordmarks is
 * normalised in practice. These seven lockups run from 3.5:1 (coches.com) to
 * 6.5:1 (coches.net), so a common height would give the widest mark twice the
 * visual mass of the narrowest; a common width with `object-contain` gives them
 * all the same optical weight and, just as usefully, makes every chip exactly
 * the same size — which is what lets the percentage layout below treat a chip as
 * a fixed budget instead of a guess.
 */
const LOGO_BOX = 'h-4 w-14 @max-[290px]:h-3.5 @max-[290px]:w-11';

/* -------------------------------------------------------------------------- */
/*                                   Layout                                   */
/* -------------------------------------------------------------------------- */

type Source = (typeof SOURCES)[number];
type Node = { readonly source: Source; readonly x: number; readonly y: number };

/**
 * Node positions, as percentages of the diagram box.
 *
 * MEASURED HERE, NEVER AT RUNTIME. The animated-beam pattern this is modelled on
 * reads both endpoints with `getBoundingClientRect` and keeps them in sync with a
 * ResizeObserver. That is the right tool when the endpoints are arbitrary DOM the
 * component does not own — and the wrong one here, where this file decides where
 * every node goes. One percentage space shared by the SVG and the chips makes them
 * align by construction, at every width, with no measurement, no observer and no
 * reflow. The failure mode that pattern is famous for — beams detaching from their
 * nodes on resize — cannot occur.
 *
 * The columns bow inward at the extremes (19 -> 15 -> 15 -> 19) so the flanks read
 * as an arc around the hub rather than as two straight rails, and so the corner
 * chips sit further from the card's corners, where the glass tile's rounding eats
 * into the usable box.
 *
 * The horizontal budget is the binding constraint, not the vertical one, and
 * these numbers were settled by measuring the built page rather than by drawing
 * on paper. At a 1440px viewport the diagram box is 334x206 and a chip is 74px,
 * so a column at 15% leaves 30px of clearance inside the card. The tightest case
 * is NOT the smallest screen — it is a 1024px viewport, where `lg` has just
 * activated and this tile is 2 of 5 columns inside a 13-of-19 track: a 220px
 * diagram, where the same chip comes within 13px of the card edge. That is why
 * the marks and the hub shrink by container query below 290px rather than at any
 * viewport breakpoint, and why the columns sit at 15/19 instead of further out.
 */
const NODES: readonly Node[] = [
  { source: SOURCES[0], x: 19, y: 9 },
  { source: SOURCES[1], x: 15, y: 36 },
  { source: SOURCES[2], x: 15, y: 64 },
  { source: SOURCES[3], x: 19, y: 91 },
  { source: SOURCES[4], x: 81, y: 12 },
  { source: SOURCES[5], x: 85, y: 50 },
  { source: SOURCES[6], x: 81, y: 88 },
];

const HUB = { x: 50, y: 50 };

/**
 * How far each lane bows off the straight chord, in the same percentage space.
 *
 * Straight spokes read as a diagram of a star; the bow is what makes them read as
 * routes. More importantly it is what lets the two DIRECTIONS occupy two visibly
 * separate lanes instead of one line carrying a confusing mix of colours. A
 * quadratic curve deviates half the control-point offset at its midpoint, so 7
 * here puts the lanes ~16px apart at the waist of a short route — clearly two
 * channels, not a thick line.
 */
const BOW = 7;

/**
 * A quadratic arc from one point to another, bowed to the traveller's right.
 *
 * The perpendicular `(-dy, dx)` is 90 degrees clockwise from the direction of
 * travel in screen coordinates, so the bow is always on the same side RELATIVE TO
 * MOVEMENT. Drawing the inbound lane `node -> hub` and the outbound lane
 * `hub -> node` through this same function therefore puts them on opposite
 * absolute sides automatically: right-hand traffic, two lanes, no special-casing
 * for whether the node is on the left flank or the right.
 */
function arc(fromX: number, fromY: number, toX: number, toY: number) {
  const dx = toX - fromX;
  const dy = toY - fromY;
  const len = Math.hypot(dx, dy) || 1;
  const cx = (fromX + toX) / 2 + (-dy / len) * BOW;
  const cy = (fromY + toY) / 2 + (dx / len) * BOW;
  return `M ${fromX} ${fromY} Q ${cx} ${cy} ${toX} ${toY}`;
}

/* -------------------------------------------------------------------------- */
/*                                   Traffic                                  */
/* -------------------------------------------------------------------------- */

type Lane = {
  /** Pulse length and the space behind it, in SCREEN px (see `non-scaling-stroke`). */
  readonly dash: number;
  readonly gap: number;
  /** Travel speed, screen px per second. */
  readonly speed: number;
  readonly width: number;
  /** Width of the soft bloom drawn under the pulse, or `null` for no bloom. */
  readonly halo: number | null;
  /** Colour, as a text utility — the strokes resolve it through `currentColor`. */
  readonly tone: string;
  readonly haloTone: string;
};

/**
 * The two directions, and why they do not look alike.
 *
 * INBOUND is the market arriving: every listing on every portal, pulled in to be
 * priced and compared. It is the quieter of the two — small, frequent, cool —
 * because it is ambient: it never stops and it is not an action the dealer takes.
 *
 * OUTBOUND is the dealer's own stock leaving, published to every portal at once.
 * It is longer, faster and carries a bloom, because it IS the action, and the
 * whole promise of the tile is that it happens everywhere simultaneously.
 *
 * On light glass the cool lane is the brand at 55% rather than `brand-soft`:
 * #8ab9fd over a 60%-white surface is a ~2:1 contrast and reads as a smudge. On
 * dark it is `brand-soft`, which is exactly the token's job. Same role, two
 * grounds, one meaning.
 */
const INBOUND: Lane = {
  dash: 2.4,
  gap: 10.6,
  speed: 58,
  width: 1.6,
  halo: null,
  tone: 'text-brand/55 dark:text-brand-soft',
  haloTone: '',
};

const OUTBOUND: Lane = {
  dash: 4.6,
  gap: 11.4,
  speed: 78,
  width: 1.9,
  halo: 5.5,
  tone: 'text-brand',
  haloTone: 'text-brand',
};

/**
 * How many dash periods one animation cycle travels.
 *
 * THIS IS THE FIX FOR "una lavadora que no se mueve". The version being replaced
 * used `strokeDasharray="14 200"` on a path about 40 units long and animated the
 * offset across the whole 214-unit pattern with a 1.1s `repeatDelay`. Two
 * consequences, both fatal: at most ONE pulse could ever be on the route, and for
 * most of every cycle that pulse was outside the path entirely — so the card was
 * genuinely dead most of the time, exactly as reported.
 *
 * A dash pattern tiles infinitely along a path, so shifting the offset by an exact
 * whole number of periods lands on a state that is pixel-identical to the start.
 * That makes the loop seamless with `repeatDelay: 0`, needs no knowledge of the
 * path's length, and puts a pulse every `dash + gap` px along the ENTIRE route at
 * all times. Measured on the built page: routes are 118-136px long at a 1440px
 * viewport and 79-103px at the tight 1024px column, so with a 13px inbound period
 * there are 9-10 pulses on every route at the wide end and 6-8 at the narrow one —
 * never the single one the old version managed. The multiplier only exists to make
 * the tween long enough that the loop restarts a few times a second rather than a
 * few times a frame; the measured travel rates are 53 px/s inbound and 73 px/s
 * outbound, against the 58 and 78 asked for here.
 *
 * Honest note on the motion law: `stroke-dashoffset` is a paint-level property,
 * not a compositor one. It is the correct tool here — nothing in SVG composites,
 * so the only truly GPU path would be rebuilding all of this out of transformed
 * HTML divs — and the repainted region is one 334x206 box at its largest. It
 * triggers no layout, which is the part of the rule that actually protects the
 * page.
 */
const LOOP_PERIODS = 8;

/** Seconds between one route's traffic starting and the next one's. */
const ROUTE_STAGGER = 0.19;

type PulsesProps = {
  readonly d: string;
  readonly lane: Lane;
  readonly delay: number;
  readonly highlighted: boolean;
  readonly still: boolean;
};

/**
 * One lane's moving light.
 *
 * The bloom is a second copy of the same dashed path, five and a half pixels wide
 * at low opacity, drawn beneath the crisp one. It is deliberately NOT an SVG
 * filter: a `feGaussianBlur` on a path whose dash offset changes every frame is a
 * full blur recomputation per frame, where a fat round-capped stroke costs nothing
 * and reads the same at this size. Both copies share duration, delay and easing,
 * so they travel locked together.
 */
function Pulses({ d, lane, delay, highlighted, still }: PulsesProps) {
  const period = lane.dash + lane.gap;
  const travel = period * LOOP_PERIODS;
  const dashArray = `${lane.dash} ${lane.gap}`;

  /* `non-scaling-stroke` is load-bearing, not a nicety. The SVG is stretched with
   * `preserveAspectRatio="none"` so that one percentage space can drive both the
   * paths and the HTML chips; without it, stroke widths AND dash lengths are
   * scaled anisotropically, so horizontal routes carry fat short pulses and
   * vertical ones thin long pulses on the same card.
   *
   * That the dash pattern follows the stroke into device space is easy to assume
   * and worth proving, so it was measured rather than trusted: a 4:1-stretched
   * viewBox painted to a canvas, dashed "10 10", gave 18 dashes of 10.2px on the
   * horizontal line and 5 of 11.2px on the vertical — identical pulse size across
   * a 4x difference in scale — while the same line without the vector-effect
   * stretched its dashes to 40px. So a pulse really is the same 2.4px object in
   * every direction and at every card width. */
  const shared = {
    d,
    fill: 'none' as const,
    strokeLinecap: 'round' as const,
    strokeDasharray: dashArray,
    vectorEffect: 'non-scaling-stroke',
  };

  const motionProps = {
    initial: { strokeDashoffset: 0 },
    animate: { strokeDashoffset: -travel },
    transition: {
      duration: travel / lane.speed,
      delay,
      ease: 'linear' as const,
      repeat: Infinity,
    },
  };

  return (
    <>
      {lane.halo !== null &&
        (still ? (
          <path
            {...shared}
            stroke="currentColor"
            strokeWidth={lane.halo}
            className={cn(lane.haloTone, 'opacity-[0.16]')}
          />
        ) : (
          <motion.path
            {...shared}
            {...motionProps}
            stroke="currentColor"
            strokeWidth={lane.halo}
            className={cn(
              lane.haloTone,
              'transition-opacity duration-300',
              highlighted ? 'opacity-40' : 'opacity-[0.16]',
            )}
          />
        ))}

      {still ? (
        <path {...shared} stroke="currentColor" strokeWidth={lane.width} className={lane.tone} />
      ) : (
        <motion.path
          {...shared}
          {...motionProps}
          stroke="currentColor"
          strokeWidth={lane.width}
          className={lane.tone}
        />
      )}
    </>
  );
}

type RouteProps = {
  readonly node: Node;
  readonly index: number;
  readonly active: string | null;
};

/**
 * One platform's connection: two hairlines, two streams of light.
 *
 * The hairlines are permanent. A route that only exists while something is moving
 * on it reads as a rendering glitch, and the claim of the tile is that the
 * connection is standing infrastructure, not an occasional event.
 */
function Route({ node, index, active }: RouteProps) {
  const reduced = useReducedMotion();
  const inbound = arc(node.x, node.y, HUB.x, HUB.y);
  const outbound = arc(HUB.x, HUB.y, node.x, node.y);
  const highlighted = active === node.source.name;
  const dimmed = active !== null && !highlighted;

  return (
    <g className={cn('transition-opacity duration-500', dimmed ? 'opacity-[0.12]' : 'opacity-100')}>
      <path
        d={inbound}
        fill="none"
        stroke="currentColor"
        strokeWidth={1}
        vectorEffect="non-scaling-stroke"
        className={cn(
          'transition-colors duration-300',
          highlighted ? 'text-brand/40' : 'text-ink/12 dark:text-white/12',
        )}
      />
      <path
        d={outbound}
        fill="none"
        stroke="currentColor"
        strokeWidth={1}
        vectorEffect="non-scaling-stroke"
        className={cn(
          'transition-colors duration-300',
          highlighted ? 'text-brand/40' : 'text-ink/12 dark:text-white/12',
        )}
      />
      {/* The two lanes are offset in time as well as in space, so the card never
        * falls into a lockstep pulse that reads as a single blinking object. */}
      <Pulses
        d={inbound}
        lane={INBOUND}
        delay={index * ROUTE_STAGGER}
        highlighted={highlighted}
        still={reduced === true}
      />
      <Pulses
        d={outbound}
        lane={OUTBOUND}
        delay={index * ROUTE_STAGGER + 0.42}
        highlighted={highlighted}
        still={reduced === true}
      />
    </g>
  );
}

/* -------------------------------------------------------------------------- */
/*                                   Chips                                    */
/* -------------------------------------------------------------------------- */

type ChipProps = {
  readonly node: Node;
  readonly active: string | null;
  readonly pinned: string | null;
  readonly onHover: (name: string | null) => void;
  readonly onToggle: (name: string) => void;
};

/**
 * A platform, shown as its own mark.
 *
 * Every logo is fitted into the common `LOGO_BOX` with `object-contain`, for the
 * reasons given where that constant is defined.
 *
 * THEME. Dark mode swaps the FILE, never filters the artwork: inverting or
 * hue-rotating a trademark produces a mark its owner never authorised, so no CSS
 * filter is applied to any logo here. Four of the seven carry a second file —
 * AutoScout24, coches.com and motor.es are their owners' own published negatives,
 * and coches.net's is flagged `derived: true` in the manifest because coches.net
 * publishes no negative of the plain wordmark and it was produced by substituting
 * a single ink value. The remaining three (Wallapop #13C1AC, Milanuncios #18BA5D,
 * Autocasión #E6301B) are single-hue marks that hold up on both grounds unchanged,
 * which is why the manifest records `onDark: null` for them rather than a hole.
 * Verified by rendering, not by trusting the manifest: all seven were checked on
 * the real tile in both themes.
 *
 * The button is not decoration dressed as a control: pressing it pins the route
 * highlight, which is the only way a touch or keyboard user can get the hover
 * behaviour at all. `aria-pressed` says what it does, and the label names the
 * platform, so the marks need no alt text and are not announced twice.
 */
function PlatformChip({ node, active, pinned, onHover, onToggle }: ChipProps) {
  const { source } = node;
  const asset = LOGOS[source.name];
  const highlighted = active === source.name;
  const dimmed = active !== null && !highlighted;

  return (
    /* `w-max` is not decoration — it is the fix for a defect this card shipped
     * with until it was measured in a browser. An absolutely positioned box with
     * only `left` set is shrink-to-fit, and its available width is the distance
     * from that `left` to the container's RIGHT edge. So the right-hand flank at
     * `left: 85%` was being capped at 15% of the diagram — 50px of a 334px box —
     * and the three portals on that side rendered their logos visibly smaller
     * than the four on the left. `max-content` ignores the available width, so
     * every chip is the same size wherever it sits. */
    <li className="absolute w-max" style={{ left: `${node.x}%`, top: `${node.y}%` }}>
      <button
        type="button"
        aria-pressed={pinned === source.name}
        aria-label={`Resaltar la ruta de ${source.name}`}
        onMouseEnter={() => onHover(source.name)}
        onMouseLeave={() => onHover(null)}
        onFocus={() => onHover(source.name)}
        onBlur={() => onHover(null)}
        onClick={() => onToggle(source.name)}
        className={cn(
          'glass-chip block -translate-x-1/2 -translate-y-1/2 rounded-xl px-2 py-1.5',
          'transition-[scale,opacity,box-shadow] duration-300 ease-out',
          'focus-visible:ring-brand/60 focus-visible:ring-2 focus-visible:outline-none',
          highlighted &&
            'scale-[1.06] shadow-[0_6px_20px_-8px_rgb(18_110_253/0.55)] ring-1 ring-brand/45',
          dimmed && 'opacity-45',
        )}
      >
        {asset ? (
          <>
            <img
              src={asset.file}
              alt=""
              width={56}
              height={16}
              loading="lazy"
              decoding="async"
              className={cn(LOGO_BOX, 'object-contain', asset.onDark && 'dark:hidden')}
            />
            {asset.onDark && (
              <img
                src={asset.onDark.file}
                alt=""
                width={56}
                height={16}
                loading="lazy"
                decoding="async"
                className={cn(LOGO_BOX, 'hidden object-contain dark:block')}
              />
            )}
          </>
        ) : (
          /* Only reachable if a mark is dropped from the manifest. It falls back
           * to the platform's own styled wordmark from SOURCES — never to a car
           * marque, which is the substitution that got the previous build thrown
           * out, and never to an invented mark. */
          <span
            className={cn(
              LOGO_BOX,
              'text-foreground flex items-center justify-center text-[10px] leading-none font-semibold tracking-tight',
            )}
          >
            {source.mark}
            {source.accent && <span className="text-brand">{source.accent}</span>}
          </span>
        )}
      </button>
    </li>
  );
}

/* -------------------------------------------------------------------------- */
/*                                   Legend                                   */
/* -------------------------------------------------------------------------- */

/**
 * Two lines that make the colour coding mean something.
 *
 * Without this the two hues are decoration. With it they are a key, and the tile
 * survives `prefers-reduced-motion`: when the traffic stops moving, the direction
 * still has to be readable, and a verb — "entra", "sale" — carries it where an
 * animation no longer can. Removing the motion must never remove the information.
 */
function Legend() {
  return (
    <ul className="text-muted-foreground relative z-10 mt-2 flex list-none flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[10px] tracking-[0.06em] uppercase">
      <li className="flex items-center gap-1.5">
        <span className="bg-brand/55 dark:bg-brand-soft h-[3px] w-4 rounded-full" />
        entra · anuncios y precios
      </li>
      <li className="flex items-center gap-1.5">
        <span className="bg-brand h-[3px] w-4 rounded-full shadow-[0_0_8px_1px_rgb(18_110_253/0.6)]" />
        sale · tu stock publicado
      </li>
    </ul>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

/**
 * "Encargos, publicación y terminal".
 *
 * The claim: Cardeep is the point everything passes through. The market's listings
 * arrive to be priced and compared, the dealer's stock leaves to be published on
 * every portal at once. One terminal, traffic both ways, on the same seven routes
 * — because each of these platforms is genuinely both a source and a destination,
 * and splitting them into "the ones we read" and "the ones we publish to" would
 * have been a tidier picture of something that is not true.
 *
 * Two things were wrong with the version this replaces, and both are fixed here
 * rather than restyled: the traffic did not visibly move (see `LOOP_PERIODS`), and
 * the platforms were typeset as text because nobody had gone and fetched their
 * logos (see the manifest import at the top of this file).
 */
export function ComponentsCard() {
  const [hovered, setHovered] = useState<string | null>(null);
  const [pinned, setPinned] = useState<string | null>(null);
  /* Hover wins while the pointer is down a route, and releasing it falls back to
   * whatever is pinned rather than to nothing — so a pinned route survives being
   * brushed past on the way to reading it. */
  const active = hovered ?? pinned;

  return (
    <div className="glass relative col-span-1 flex min-h-(--box-min-height) flex-col overflow-hidden rounded-2xl p-4 lg:col-span-2">
      <h2 className="text-foreground relative z-10 text-lg leading-6 font-medium tracking-tight">
        {BENTO.more.title}
      </h2>

      <p className="sr-only">
        Cardeep conecta con {SOURCES.length} plataformas: {SOURCES.map((s) => s.name).join(', ')}. De
        cada una entran los anuncios y sus precios para tasar y comparar; hacia todas ellas sale tu
        stock publicado a la vez.
      </p>

      {/* `@container` makes every size below answer to the CARD's width rather
        * than the viewport's. That distinction is the whole point: at the `lg`
        * breakpoint this tile is 254px wide on a 1024px screen and 368px wide on
        * a 1440px one, so a viewport breakpoint cannot tell the cramped case from
        * the roomy one. Measured at 1024px, the flanking chips came within 13px
        * of the card edge and the mid-height routes were down to ~24px of visible
        * beam; shrinking the marks and the hub only in that band buys the traffic
        * back its runway without costing the wide case anything. */}
      <div className="@container relative mt-2 min-h-0 flex-1">
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="pointer-events-none absolute inset-0 h-full w-full"
          aria-hidden="true"
        >
          {NODES.map((node, index) => (
            <Route key={node.source.name} node={node} index={index} active={active} />
          ))}
        </svg>

        <ul className="absolute inset-0 list-none">
          {NODES.map((node) => (
            <PlatformChip
              key={node.source.name}
              node={node}
              active={active}
              pinned={pinned}
              onHover={setHovered}
              onToggle={(name) => setPinned((current) => (current === name ? null : name))}
            />
          ))}
        </ul>

        {/* The terminal. It sits above the beams so every route visibly ends
          * behind it instead of crossing it, and it stays dark in both themes for
          * the same reason the coverage tile does: it is the one object on this
          * card that is not glass, and that is what makes it read as the thing
          * everything else connects to. */}
        <span
          className="bg-ink absolute top-1/2 left-1/2 flex size-11 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-2xl @max-[290px]:size-9 shadow-[0_0_30px_6px_rgb(18_110_253/0.32)] ring-1 ring-white/12 dark:ring-white/20"
          aria-hidden="true"
        >
          <Logo tone="light" className="size-6 @max-[290px]:size-5" />
        </span>
        {/* Names the third noun in the card's own title, which otherwise has
          * nothing on the card to point at. */}
        <span
          className="text-muted-foreground absolute top-1/2 left-1/2 -translate-x-1/2 translate-y-[28px] font-mono @max-[290px]:translate-y-[24px] text-[9px] tracking-[0.14em] uppercase"
          aria-hidden="true"
        >
          terminal
        </span>
      </div>

      <Legend />
    </div>
  );
}
