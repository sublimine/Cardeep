import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';

/**
 * The photograph the whole hero is built on, plus the treatment that makes it
 * carry white type and glass without either giving way.
 *
 * Three deliberate layers, in this order:
 *
 *  1. The image. Served AVIF → WebP → JPEG at two widths. The source is
 *     1200x800, so a full-bleed hero at desktop widths is already upscaling it;
 *     the scale below is set just past 1.0 and paired with the grain layer so
 *     the softness reads as depth of field rather than as a stretched file.
 *     `object-position` keeps the children right of centre, in the gap the copy
 *     and the search panel leave open.
 *
 *  2. Two scrims. A vertical one anchors the bottom so the market strip has
 *     something solid to sit on, and a horizontal one darkens the left third
 *     where the headline lives. One combined scrim cannot do both without
 *     flattening the picture — the sky has to stay bright for the glass above
 *     it to have anything to refract.
 *
 *  3. Grain. Static, very low opacity, `mix-blend-overlay`. It hides the JPEG's
 *     gradient banding across the sky, which is exactly where a large blurred
 *     panel would otherwise reveal it.
 */
export function HeroBackdrop() {
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll();

  // Compositor-only parallax: the picture drifts slower than the page and lifts
  // a hair, so the glass appears to float above it. Transform and opacity only —
  // nothing here can trigger layout (rules/web/performance.md).
  const y = useTransform(scrollYProgress, [0, 0.35], ['0%', '14%']);
  const scale = useTransform(scrollYProgress, [0, 0.35], [1.05, 1.16]);

  return (
    <div className="absolute inset-0 overflow-hidden" aria-hidden>
      <motion.div
        className="absolute inset-0"
        style={reduced ? { scale: 1.04 } : { y, scale }}
      >
        <picture>
          <source
            type="image/avif"
            srcSet="/hero/hero-familia-1600.avif 1600w, /hero/hero-familia-2400.avif 2400w"
            sizes="100vw"
          />
          <source
            type="image/webp"
            srcSet="/hero/hero-familia-1600.webp 1600w, /hero/hero-familia-2400.webp 2400w"
            sizes="100vw"
          />
          <img
            src="/hero/hero-familia.jpg"
            alt=""
            width={2400}
            height={1600}
            /* Lowercase: React 18 does not map the camelCase spelling and passes
               it through as an unknown DOM attribute. */
            {...{ fetchpriority: 'high' }}
            decoding="async"
            className="h-full w-full object-cover object-[60%_22%] lg:object-[68%_center]"
          />
        </picture>
      </motion.div>

      {/* Vertical scrim — floor for the market strip, air at the top for the sky. */}
      <div
        className="absolute inset-0"
        style={{
          background:
            'linear-gradient(to bottom, rgb(6 10 20 / 0.42) 0%, rgb(6 10 20 / 0.10) 26%, rgb(6 10 20 / 0.30) 58%, rgb(6 10 20 / 0.88) 100%)',
        }}
      />
      {/* Horizontal scrim — a bed for the headline without touching the right side. */}
      <div
        className="absolute inset-0"
        style={{
          background:
            'linear-gradient(90deg, rgb(6 10 20 / 0.74) 0%, rgb(6 10 20 / 0.34) 34%, transparent 62%)',
        }}
      />
      {/* Grain. It drifts a couple of pixels on a long loop: static grain over a
          photograph reads as a dirty screen, moving grain reads as film. Two
          transforms per cycle, nothing that touches layout. */}
      <motion.div
        animate={reduced ? undefined : { x: [0, -6, 3, 0], y: [0, 4, -5, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -inset-8 opacity-[0.16] mix-blend-overlay"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E\")",
        }}
      />
    </div>
  );
}
