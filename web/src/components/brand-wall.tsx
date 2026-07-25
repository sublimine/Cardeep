import { useMemo, useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';

import { Container } from '@/components/ui/container';
import { BRAND_WALL } from '@/content/site';
import { MARK_CELL, MARK_COLS, VEHICLE_MARKS, type VehicleMark } from '@/content/vehicle-marks';

/**
 * Every vehicle marque in the index — all 135 — as one continuous wall.
 *
 * The marks come from a single alpha sprite painted as a CSS mask, so they are
 * one flat colour by default and the wall reads as a system rather than a
 * ransom note of competing logos. Hovering lifts a mark into its own official
 * colour: the brand is still there, it just waits to be asked.
 */

const SPRITE = '/brand/marks.webp';

/** Rows drift in alternating directions; the wall breathes without scrolling. */
const ROW_SIZE = 15;
const DRIFT_PX = 26;

function MarkTile({ mark, hovered, onHover }: {
  mark: VehicleMark;
  hovered: boolean;
  onHover: (slug: string | null) => void;
}) {
  return (
    <button
      type="button"
      title={mark.name}
      aria-label={mark.name}
      onMouseEnter={() => onHover(mark.slug)}
      onMouseLeave={() => onHover(null)}
      onFocus={() => onHover(mark.slug)}
      onBlur={() => onHover(null)}
      className="group relative grid shrink-0 place-items-center rounded-xl px-3 py-2 transition-colors duration-300 outline-none"
      style={{ width: MARK_CELL.width + 24, height: MARK_CELL.height + 16 }}
    >
      <span
        aria-hidden
        className="transition-[background-color,opacity,transform] duration-300 group-hover:scale-[1.06] group-focus-visible:scale-[1.06]"
        style={{
          width: MARK_CELL.width,
          height: MARK_CELL.height,
          // One sprite, painted through a mask: colour is ours to choose.
          backgroundColor: hovered ? mark.color : 'var(--cd-fg)',
          opacity: hovered ? 1 : 0.42,
          WebkitMaskImage: `url(${SPRITE})`,
          maskImage: `url(${SPRITE})`,
          WebkitMaskRepeat: 'no-repeat',
          maskRepeat: 'no-repeat',
          WebkitMaskSize: `${MARK_COLS * MARK_CELL.width}px auto`,
          maskSize: `${MARK_COLS * MARK_CELL.width}px auto`,
          WebkitMaskPosition: `-${mark.col * MARK_CELL.width}px -${mark.row * MARK_CELL.height}px`,
          maskPosition: `-${mark.col * MARK_CELL.width}px -${mark.row * MARK_CELL.height}px`,
        }}
      />
    </button>
  );
}

export function BrandWall() {
  const [hovered, setHovered] = useState<string | null>(null);
  const reduced = useReducedMotion();

  const rows = useMemo(() => {
    const out: VehicleMark[][] = [];
    for (let i = 0; i < VEHICLE_MARKS.length; i += ROW_SIZE) {
      out.push(VEHICLE_MARKS.slice(i, i + ROW_SIZE));
    }
    return out;
  }, []);

  const active = hovered ? VEHICLE_MARKS.find((mark) => mark.slug === hovered) : null;

  return (
    <section id="marcas" className="w-full">
      <Container className="flex flex-col gap-12 py-20 md:py-30">
        <div className="flex flex-col gap-4 md:max-w-3xl">
          <span className="font-dm-mono -tracking-xs text-muted-foreground text-xs uppercase">
            {BRAND_WALL.kicker}
          </span>
          <h2 className="text-heading -tracking-lg text-left text-4xl font-semibold md:text-5xl">
            {BRAND_WALL.heading}
          </h2>
          <p className="text-muted-foreground -tracking-xs max-w-xl text-base leading-6">
            {BRAND_WALL.body}
          </p>
        </div>

        <div
          className="relative -mx-4 overflow-hidden px-4"
          style={{
            // Fade the edges so the rows read as part of a larger field.
            WebkitMaskImage:
              'linear-gradient(90deg, transparent, #000 6%, #000 94%, transparent)',
            maskImage: 'linear-gradient(90deg, transparent, #000 6%, #000 94%, transparent)',
          }}
        >
          <div className="flex flex-col items-center gap-1">
            {rows.map((row, rowIndex) => (
              // Entrance and drift are separate elements: one plays once on
              // scroll, the other loops forever, and a single node cannot hold
              // two conflicting transitions.
              <motion.div
                key={rowIndex}
                initial={reduced ? false : { opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.2 }}
                transition={{ duration: 0.55, delay: rowIndex * 0.05, ease: 'easeOut' }}
              >
                <motion.div
                  className="flex items-center justify-center gap-1"
                  animate={
                    reduced ? undefined : { x: rowIndex % 2 === 0 ? [0, DRIFT_PX, 0] : [0, -DRIFT_PX, 0] }
                  }
                  transition={{
                    duration: 18 + (rowIndex % 3) * 4,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                >
                  {row.map((mark) => (
                    <MarkTile
                      key={mark.slug}
                      mark={mark}
                      hovered={hovered === mark.slug}
                      onHover={setHovered}
                    />
                  ))}
                </motion.div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* The readout replaces a tooltip: one calm line, always in the same place. */}
        <div className="flex h-6 items-center justify-center">
          <span
            className="font-dm-mono -tracking-xs text-xs transition-colors duration-300"
            style={{ color: active ? active.color : 'var(--cd-fg-subtle)' }}
          >
            {active ? active.name : BRAND_WALL.hint}
          </span>
        </div>
      </Container>
    </section>
  );
}
