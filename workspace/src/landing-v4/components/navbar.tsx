import { IconMenu2 } from '@tabler/icons-react';
import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';

import { BRAND, NAV_LINKS, PRIMARY_CTA } from '@landing/content/site';

/**
 * Top navigation, fixed over the cover.
 *
 * It starts floating on the photograph and docks as the hero leaves: a glass
 * plate fades in behind it and the bar settles the 16px it was hovering. Fixed
 * rather than absolute because a navigation that scrolls away with the hero
 * stops being navigation the moment it matters.
 *
 * Both driven properties are compositor-safe — the plate's opacity and the bar's
 * translate. Nothing here animates height or padding, which would relayout the
 * page on every scroll frame (rules/web/performance.md).
 *
 * The links sit in their own glass pill: the hero's top-right is open sky, and
 * white type on a bright sky is the one place on this page where contrast
 * genuinely fails.
 */
export function Navbar() {
  const reduced = useReducedMotion();
  const { scrollY } = useScroll();

  // The plate appears over the first 130px — enough to read as a response to
  // scrolling rather than a flicker on the first wheel notch.
  const plate = useTransform(scrollY, [0, 130], [0, 1]);
  const lift = useTransform(scrollY, [0, 130], [16, 0]);

  return (
    <nav className="fixed inset-x-0 top-0 z-50 w-full">
      <motion.div
        aria-hidden
        style={{ opacity: reduced ? undefined : plate }}
        className="glass-chip-dark absolute inset-0 border-x-0 border-t-0 border-b border-white/10"
      />

      <motion.div
        style={{ y: reduced ? 0 : lift }}
        className="max-w-container relative mx-auto px-4 lg:px-8"
      >
        <div className="flex h-16 items-center justify-between">
          <div className="flex shrink-0 items-center gap-2 lg:min-w-45">
            <a className="flex items-center" href="/" aria-label={BRAND.name}>
              {/* Cardeep's own mark, lifted from the master lockup. */}
              <img src="/hero/cardeep-mark.png" alt={BRAND.name} className="h-8 w-auto" />
            </a>
          </div>

          <div className="hidden md:block">
            <div className="glass-chip-dark flex items-center gap-1 rounded-full px-2 py-1.5">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  className="text-natural-white/75 hover:text-natural-white rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors duration-200 hover:bg-white/10"
                  href={link.href}
                >
                  {link.label}
                </a>
              ))}
            </div>
          </div>

          <div className="hidden md:block">
            <motion.a
              href="/login"
              whileHover={{ scale: 1.04, y: -1 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              className="bg-brand inline-flex items-center rounded-full px-5 py-2.5 text-sm font-semibold text-white shadow-[0_12px_30px_-12px_rgb(18_110_253/0.8)]"
            >
              {PRIMARY_CTA}
            </motion.a>
          </div>

          <div className="md:hidden">
            <button aria-label="Abrir menú" className="p-2 text-white/80 hover:text-white">
              <IconMenu2 className="size-6 text-natural-white" />
            </button>
          </div>
        </div>
      </motion.div>
    </nav>
  );
}
