import { motion, useReducedMotion } from 'framer-motion';

import { BENTO, SOURCES } from '@landing/content/site';
import { Logo } from '@landing/components/ui/logo';

/* -------------------------------------------------------------------------- */
/*                                   Layout                                   */
/* -------------------------------------------------------------------------- */

/**
 * Node positions, as percentages of the diagram box.
 *
 * MEASURED, NOT MEASURED-AT-RUNTIME. The animated-beam pattern this is modelled
 * on reads both endpoints with `getBoundingClientRect` and keeps them in sync
 * with a ResizeObserver. That is the right tool when the endpoints are arbitrary
 * DOM the component does not own — and the wrong one here, where this file
 * decides where every node goes. Sharing one percentage space between the SVG
 * and the chips makes them align by construction, at every width, with no
 * measurement, no observer and no reflow. The failure mode that pattern is
 * famous for — beams detaching from their nodes on resize — cannot occur.
 *
 * `dir` is what the beam MEANS. Inbound is the market's data arriving to be
 * priced; outbound is the dealer's stock going out to be published. The hub sits
 * between the two, which is the claim the card makes.
 */
const NODES = [
  { at: SOURCES[0], x: 12, y: 16, dir: 'in' },
  { at: SOURCES[1], x: 8, y: 50, dir: 'in' },
  { at: SOURCES[2], x: 12, y: 84, dir: 'in' },
  { at: SOURCES[3], x: 88, y: 16, dir: 'out' },
  { at: SOURCES[4], x: 92, y: 50, dir: 'out' },
  { at: SOURCES[5], x: 88, y: 84, dir: 'out' },
] as const;

const HUB = { x: 50, y: 50 };

/** Seconds for one beam to travel its path, and the gap between departures. */
const BEAM_S = 2.2;
const BEAM_GAP = 1.1;

/**
 * A quadratic curve from a node to the hub, bowed away from the straight line.
 *
 * Straight spokes would read as a diagram of a star; the bow is what makes them
 * read as routes. The control point is pushed perpendicular to the chord, so the
 * bow always bends the same way relative to travel whatever the node's angle.
 */
function path(x: number, y: number) {
  const mx = (x + HUB.x) / 2;
  const my = (y + HUB.y) / 2;
  const dx = HUB.x - x;
  const dy = HUB.y - y;
  const len = Math.hypot(dx, dy) || 1;
  const bow = 12;
  return `M ${x} ${y} Q ${mx + (-dy / len) * bow} ${my + (dx / len) * bow} ${HUB.x} ${HUB.y}`;
}

/* -------------------------------------------------------------------------- */
/*                                   Beams                                    */
/* -------------------------------------------------------------------------- */

/**
 * One route, and the light travelling it.
 *
 * The route itself is a permanent hairline — the connection exists whether or not
 * something is moving on it, and a line that only appears when lit reads as a
 * glitch. The beam is a short dash driven along that same path by
 * `strokeDashoffset`, which is the technique the card already used for its circuit
 * traces and the reason it stays on the compositor.
 *
 * Direction carries the meaning without a legend: inbound beams run node -> hub,
 * outbound run hub -> node, and the two are simply the same animation with the
 * offset reversed.
 */
function Beam({ node, index }: { node: (typeof NODES)[number]; index: number }) {
  const reduced = useReducedMotion();
  const d = path(node.x, node.y);
  const inbound = node.dir === 'in';
  /* One dash and a gap longer than the path, so exactly one pulse is ever in
   * flight and the loop has no seam. */
  const DASH = 14;
  const GAP = 200;

  return (
    <g>
      <path d={d} fill="none" stroke="currentColor" strokeWidth="0.4" className="text-brand/15" />
      {!reduced && (
        <motion.path
          d={d}
          fill="none"
          stroke="url(#cx-beam)"
          strokeWidth="1.1"
          strokeLinecap="round"
          strokeDasharray={`${DASH} ${GAP}`}
          initial={{ strokeDashoffset: inbound ? DASH + GAP : 0 }}
          animate={{ strokeDashoffset: inbound ? -GAP : DASH + GAP }}
          transition={{
            duration: BEAM_S,
            delay: index * (BEAM_GAP / NODES.length) + (inbound ? 0 : BEAM_GAP / 2),
            repeat: Infinity,
            repeatDelay: BEAM_GAP,
            ease: 'easeInOut',
          }}
        />
      )}
    </g>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

/**
 * "Encargos, publicación y terminal".
 *
 * What this replaces was a printed-circuit illustration: three plates of traced
 * lines feeding an orange chip. It was well made and it said nothing — a chip is
 * not what this product does, and the card's largest element being an orange
 * square made the tile read as a different product from the ones beside it.
 *
 * This says the actual claim. Cardeep is the point everything passes through:
 * the platforms' listings arrive to be priced and compared, the dealer's stock
 * leaves to be published on all of them at once. One hub, traffic both ways.
 */
export function ComponentsCard() {
  return (
    <div className="glass relative col-span-1 flex min-h-(--box-min-height) flex-col overflow-hidden rounded-2xl p-4 lg:col-span-2">
      <h2 className="text-foreground relative z-10 text-lg leading-6 font-medium tracking-tight">
        {BENTO.more.title}
      </h2>

      <div className="relative mt-2 min-h-0 flex-1">
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="absolute inset-0 h-full w-full"
          aria-hidden="true"
        >
          <defs>
            <linearGradient id="cx-beam" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#126efd" stopOpacity="0" />
              <stop offset="50%" stopColor="#126efd" stopOpacity="1" />
              <stop offset="100%" stopColor="#8ab9fd" stopOpacity="0" />
            </linearGradient>
          </defs>
          {NODES.map((node, index) => (
            <Beam key={node.at.name} node={node} index={index} />
          ))}
        </svg>

        {/* The platforms. Wordmarks rather than logos because no platform ships a
          * logo asset in public/logos, and a fabricated mark is not an option. */}
        {NODES.map((node) => (
          <span
            key={node.at.name}
            /* `glass-chip`, not `glass-chip-dark`, and a theme token for the
             * text. The dark chip carries white type, which on this tile — glass
             * over the page's LIGHT ground — rendered the platform name white on
             * near-white and left only the blue accent visible. */
            className="glass-chip text-foreground absolute -translate-x-1/2 -translate-y-1/2 rounded-full px-2 py-1 text-[10px] leading-none font-medium whitespace-nowrap"
            style={{ left: `${node.x}%`, top: `${node.y}%` }}
          >
            {node.at.mark}
            {node.at.accent && <span className="text-brand-soft">{node.at.accent}</span>}
          </span>
        ))}

        {/* The hub. It sits above the beams so every route visibly terminates
          * behind it rather than crossing it. */}
        <span className="absolute top-1/2 left-1/2 flex size-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-2xl bg-[#0b1526] shadow-[0_0_28px_6px_rgb(18_110_253/0.35)] ring-1 ring-white/12">
          <Logo tone="light" className="size-6" />
        </span>
      </div>
    </div>
  );
}
