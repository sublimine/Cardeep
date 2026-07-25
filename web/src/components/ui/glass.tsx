import { motion, useMotionTemplate, useMotionValue } from 'motion/react';

import { cn } from '@/lib/utils';

/**
 * Liquid glass — the material every raised surface on the page is made of.
 *
 * A blur alone reads as frosted plastic. Real glass needs its edges to behave,
 * so this composes six layers, each doing one job:
 *   1. the blurred, saturated, slightly brightened backdrop
 *   2. a refraction border: a 1px gradient ring, bright on the light-facing
 *      flank and almost gone on the shadowed one
 *   3. a specular highlight along the top edge
 *   4. an inner accent glow that gives the panel interior depth
 *   5. a sheen that follows the pointer (motion values, so it never re-renders)
 *   6. fine grain, which is what actually kills gradient banding on large panels
 *
 * Every value comes from the theme variables, so the same component is correct
 * in light and dark without a single conditional.
 */

/** Fractal-noise tile, inlined so layer 6 costs no request. */
const NOISE =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")";

function GlassLayers({ radius, glow }: { radius: number; glow: boolean }) {
  return (
    <>
      {/* (2) refraction border */}
      <span
        aria-hidden
        className="pointer-events-none absolute inset-0 z-[1]"
        style={{
          borderRadius: radius,
          padding: 1,
          background: `linear-gradient(145deg, var(--cd-glass-refract-a) 0%, var(--cd-glass-refract-b) 42%, transparent 58%, var(--cd-glass-refract-b) 82%, var(--cd-glass-refract-a) 100%)`,
          WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
          WebkitMaskComposite: 'xor',
          maskComposite: 'exclude',
        }}
      />
      {/* (3) specular top highlight */}
      <span
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 z-[1] h-[46%]"
        style={{
          borderRadius: `${radius}px ${radius}px 0 0`,
          background:
            'radial-gradient(120% 100% at 50% 0%, var(--cd-glass-specular) 0%, transparent 64%)',
          opacity: 0.6,
        }}
      />
      {/* (4) inner accent glow */}
      {glow ? (
        <span
          aria-hidden
          className="pointer-events-none absolute inset-0 z-0"
          style={{ borderRadius: radius, boxShadow: 'inset 0 0 56px var(--cd-glass-glow)' }}
        />
      ) : null}
      {/* (6) grain */}
      <span
        aria-hidden
        className="pointer-events-none absolute inset-0 z-[2] mix-blend-overlay"
        style={{
          borderRadius: radius,
          backgroundImage: NOISE,
          opacity: 'var(--cd-glass-noise)' as unknown as number,
        }}
      />
    </>
  );
}

type GlassProps = {
  children: React.ReactNode;
  /** Corner radius in px; the decoration layers need the number, not a class. */
  radius?: number;
  /** Denser fill and a longer shadow, for panels that should sit forward. */
  elevated?: boolean;
  /** Enables layer 5, the pointer sheen. */
  interactive?: boolean;
  glow?: boolean;
  className?: string;
  style?: React.CSSProperties;
  id?: string;
};

export function Glass({
  children,
  radius = 16,
  elevated = false,
  interactive = false,
  glow = true,
  className,
  style,
  id,
}: GlassProps) {
  const mx = useMotionValue(-400);
  const my = useMotionValue(-400);
  const opacity = useMotionValue(0);
  const sheen = useMotionTemplate`radial-gradient(260px circle at ${mx}px ${my}px, var(--cd-glass-sheen), transparent 62%)`;

  const pointer = interactive
    ? {
        onMouseMove: (event: React.MouseEvent<HTMLDivElement>) => {
          const box = event.currentTarget.getBoundingClientRect();
          mx.set(event.clientX - box.left);
          my.set(event.clientY - box.top);
        },
        onMouseEnter: () => opacity.set(1),
        onMouseLeave: () => opacity.set(0),
      }
    : {};

  return (
    <div
      id={id}
      className={cn('relative overflow-hidden', className)}
      style={{
        borderRadius: radius,
        background: elevated ? 'var(--cd-glass-panel-hi)' : 'var(--cd-glass-panel)',
        backdropFilter: 'var(--cd-glass-blur)',
        WebkitBackdropFilter: 'var(--cd-glass-blur)',
        border: '1px solid var(--cd-glass-border)',
        boxShadow: elevated ? 'var(--cd-glass-shadow-lg)' : 'var(--cd-glass-shadow)',
        ...style,
      }}
      {...pointer}
    >
      <GlassLayers radius={radius} glow={glow} />
      {interactive ? (
        <motion.span
          aria-hidden
          className="pointer-events-none absolute inset-0 z-[2] mix-blend-soft-light"
          style={{ borderRadius: radius, background: sheen, opacity }}
        />
      ) : null}
      <div className="relative z-[3] flex h-full min-h-0 flex-col">{children}</div>
    </div>
  );
}
