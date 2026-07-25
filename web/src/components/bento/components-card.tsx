import { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { ClipboardList, LineChart, Share2, type LucideIcon } from 'lucide-react';

import { Glass } from '@/components/ui/glass';
import { BENTO } from '@/content/site';

type SurfaceTile = {
  id: string;
  label: string;
  Icon: LucideIcon;
};

/**
 * The three surfaces `BENTO.more.title` names. site.ts carries that heading as a
 * single sentence and has no per-surface strings for this card, so each label is
 * one of its own three nouns — no new claim is made about any of them.
 */
const SURFACE_TILES: readonly SurfaceTile[] = [
  { id: 'encargos', label: 'Encargos', Icon: ClipboardList },
  { id: 'publicacion', label: 'Publicación', Icon: Share2 },
  { id: 'terminal', label: 'Terminal', Icon: LineChart },
];

/** How long a tile holds the highlight before it travels to the next one. */
const CYCLE_MS = 2600;

/**
 * Bento card 1-3: the three surfaces that sit next to the index, as three equal
 * glass tiles. A single cobalt highlight travels between them — one element with
 * a shared `layoutId`, so the light moves rather than blinking on and off, which
 * is what tells the eye these are one set of three and not three loose icons.
 */
export function ComponentsCard() {
  const reduced = useReducedMotion();
  const [cycled, setCycled] = useState(0);
  const [hovered, setHovered] = useState<number | null>(null);

  // The pointer takes the highlight over while it rests on a tile; the loop
  // resumes from a full period once it leaves.
  useEffect(() => {
    if (reduced || hovered !== null) return;
    const timer = setInterval(
      () => setCycled((current) => (current + 1) % SURFACE_TILES.length),
      CYCLE_MS,
    );
    return () => clearInterval(timer);
  }, [reduced, hovered]);

  const active = hovered ?? cycled;

  return (
    <Glass radius={16} interactive className="col-span-1 min-h-(--box-min-height) lg:col-span-2">
      <div className="flex min-h-0 flex-1 flex-col gap-4 p-4">
        <motion.h3
          className="text-foreground -tracking-xs text-base leading-5 font-medium text-balance"
          initial={reduced ? false : { opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        >
          {BENTO.more.title}
        </motion.h3>

        <div className="grid min-h-0 flex-1 grid-cols-3 items-center gap-2.5">
          {SURFACE_TILES.map(({ id, label, Icon }, index) => {
            const isActive = index === active;

            return (
              <motion.div
                key={id}
                className="glass-chip relative flex h-44 flex-col items-center justify-between overflow-hidden rounded-xl px-2 py-4"
                onMouseEnter={() => setHovered(index)}
                onMouseLeave={() => setHovered(null)}
                initial={reduced ? false : { opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                whileHover={
                  reduced ? undefined : { y: -3, transition: { duration: 0.25, ease: 'easeOut' } }
                }
                viewport={{ once: true, amount: 0.3 }}
                transition={{ duration: 0.5, delay: index * 0.08, ease: 'easeOut' }}
              >
                {isActive ? (
                  <motion.span
                    aria-hidden
                    layoutId="more-active-surface"
                    className="pointer-events-none absolute inset-0 rounded-xl"
                    style={{
                      background:
                        'radial-gradient(115% 76% at 50% 100%, var(--cd-glass-sheen), transparent 74%)',
                      border: '1px solid color-mix(in srgb, var(--cd-accent) 34%, transparent)',
                    }}
                    // A spring with no bounce: the light slides, it never overshoots.
                    transition={{ type: 'spring', bounce: 0, duration: 0.55 }}
                  >
                    <span className="bg-primary absolute inset-x-4 bottom-0 h-0.5 rounded-full" />
                  </motion.span>
                ) : null}

                <motion.span
                  aria-hidden
                  className={
                    isActive
                      ? 'text-primary relative block transition-colors duration-300'
                      : 'text-muted-foreground relative block transition-colors duration-300'
                  }
                  animate={reduced ? undefined : { scale: isActive ? 1.08 : 1 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                >
                  <Icon className="size-5" strokeWidth={1.75} />
                </motion.span>

                <span
                  className={
                    isActive
                      ? 'text-foreground -tracking-xs relative text-center text-[11px] leading-tight font-medium transition-colors duration-300'
                      : 'text-muted-foreground -tracking-xs relative text-center text-[11px] leading-tight font-medium transition-colors duration-300'
                  }
                >
                  {label}
                </span>
              </motion.div>
            );
          })}
        </div>
      </div>
    </Glass>
  );
}
