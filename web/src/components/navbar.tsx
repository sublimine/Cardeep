import { useCallback, useEffect, useRef, useState } from 'react';
import {
  AnimatePresence,
  motion,
  useMotionValueEvent,
  useReducedMotion,
  useScroll,
  useSpring,
} from 'motion/react';

import { Button } from '@/components/ui/button';
import { Glass } from '@/components/ui/glass';
import { Logo } from '@/components/ui/logo';
import { ThemeToggle } from '@/components/ui/theme';
import { BRAND, PRIMARY_CTA } from '@/content/site';
import { cn } from '@/lib/utils';

/**
 * The five accesses the page actually resolves, in reading order of importance.
 *
 * `NAV_LINKS` in `@/content/site` still carries the older four and misses both
 * `#marcas` and `#cobertura`, so the bar keeps its own list until the content
 * module catches up. Every label here already exists in the site's vocabulary.
 */
const NAV_ITEMS = [
  { label: 'Índice', href: '#indice' },
  { label: 'Marcas', href: '#marcas' },
  { label: 'Producto', href: '#producto' },
  { label: 'Cobertura', href: '#cobertura' },
  { label: 'Precios', href: '#precios' },
] as const;

const SHEET_ID = 'nav-sheet';
const PILL_RADIUS = 26;

/** Asymmetric thresholds: the bar docks at 24px but only undocks back at 8px,
 *  so parking the scroll on the boundary cannot strobe the material. */
const DOCK_ENTER = 24;
const DOCK_EXIT = 8;

type ThemeVars = React.CSSProperties & Record<`--${string}`, string>;

/**
 * While the bar floats over the hero photograph it is an island of light ink,
 * whatever the page theme is — the plate underneath is dark in both.
 *
 * Rebinding the theme variables rather than hardcoding `text-white` keeps every
 * child correct too, including the theme switch, whose chip would otherwise be
 * an opaque white pill sitting on a night-time skyline.
 */
const HERO_INK: ThemeVars = {
  '--cd-fg': 'var(--cd-mist)',
  '--cd-fg-muted': 'color-mix(in srgb, var(--cd-mist) 76%, transparent)',
  '--cd-fg-subtle': 'color-mix(in srgb, var(--cd-mist) 55%, transparent)',
  '--cd-line': 'color-mix(in srgb, var(--cd-mist) 20%, transparent)',
  '--cd-glass-panel': 'color-mix(in srgb, var(--cd-mist) 12%, transparent)',
  '--cd-glass-panel-hi': 'color-mix(in srgb, var(--cd-mist) 17%, transparent)',
  '--cd-glass-border': 'color-mix(in srgb, var(--cd-mist) 24%, transparent)',
  '--cd-glass-specular': 'color-mix(in srgb, var(--cd-mist) 26%, transparent)',
};

/** Which of the five sections currently owns the reading band. */
function useActiveSection() {
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    const targets = NAV_ITEMS.map((item) => document.getElementById(item.href.slice(1))).filter(
      (element): element is HTMLElement => element !== null,
    );
    if (targets.length === 0) return;

    // Heights, not just membership: the product grid physically contains the
    // coverage card, so both straddle the band and the smaller one is the
    // more specific — and therefore the true — answer.
    const straddling = new Map<string, number>();

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) straddling.set(entry.target.id, entry.boundingClientRect.height);
          else straddling.delete(entry.target.id);
        }
        let best: string | null = null;
        let smallest = Number.POSITIVE_INFINITY;
        for (const [id, height] of straddling) {
          if (height < smallest) {
            best = id;
            smallest = height;
          }
        }
        setActive(best);
      },
      { rootMargin: '-42% 0px -52% 0px' },
    );

    targets.forEach((target) => observer.observe(target));
    return () => observer.disconnect();
  }, []);

  return active;
}

/** Two rules that become a cross — the button states what it will do next. */
function MenuGlyph({ open, instant }: { open: boolean; instant: boolean }) {
  const transition = { duration: instant ? 0 : 0.32, ease: 'easeOut' } as const;
  return (
    <span aria-hidden className="relative grid size-5 place-items-center">
      <motion.span
        className="bg-foreground absolute h-px w-4.5 rounded-full"
        animate={{ y: open ? 0 : -3.5, rotate: open ? 45 : 0 }}
        transition={transition}
      />
      <motion.span
        className="bg-foreground absolute h-px w-4.5 rounded-full"
        animate={{ y: open ? 0 : 3.5, rotate: open ? -45 : 0 }}
        transition={transition}
      />
    </span>
  );
}

/**
 * Floating navigation.
 *
 * Over the hero plate the bar carries no surface at all — only light ink on the
 * photograph. Past 24px of scroll a liquid-glass pill fades under it and the ink
 * returns to the page theme, so the bar reads as part of the hero at rest and as
 * a floating panel once the page is in motion. A cobalt hairline along the pill
 * reports how far down the page you are, and the underline slides between links
 * as sections take over the reading band.
 */
export function Navbar() {
  const reduced = useReducedMotion() ?? false;
  const { scrollY, scrollYProgress } = useScroll();
  const active = useActiveSection();
  const triggerRef = useRef<HTMLButtonElement>(null);

  const [scrolled, setScrolled] = useState(
    () => typeof window !== 'undefined' && window.scrollY > DOCK_ENTER,
  );
  const [open, setOpen] = useState(false);

  useMotionValueEvent(scrollY, 'change', (latest) => {
    setScrolled((previous) => (previous ? latest > DOCK_EXIT : latest > DOCK_ENTER));
  });

  /** Opening the sheet also raises the plate: one panel, one material. */
  const docked = scrolled || open;

  const smoothed = useSpring(scrollYProgress, { stiffness: 140, damping: 30, mass: 0.35 });
  const progress = reduced ? scrollYProgress : smoothed;

  const close = useCallback(() => setOpen(false), []);

  // Escape closes the sheet and hands focus back to the control that opened it.
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      setOpen(false);
      triggerRef.current?.focus();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open]);

  // Growing past the breakpoint hides the sheet by CSS; the state has to follow
  // or the trigger keeps announcing itself as expanded.
  useEffect(() => {
    const media = window.matchMedia('(min-width: 768px)');
    const onChange = (event: MediaQueryListEvent) => {
      if (event.matches) setOpen(false);
    };
    media.addEventListener('change', onChange);
    return () => media.removeEventListener('change', onChange);
  }, []);

  /** Tight spring, no overshoot: the underline arrives, it does not bounce. */
  const linkMotion = reduced
    ? { duration: 0 }
    : { type: 'spring' as const, stiffness: 420, damping: 38 };

  return (
    // Above z-50: the coverage card raises its own heading to 50, and a fixed bar
    // that ties on z-index loses on document order — that heading would paint over
    // this one and swallow its clicks on the way past.
    <motion.header
      className="fixed inset-x-0 top-0 z-[100]"
      initial={reduced ? false : { y: -28, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.55, ease: 'easeOut', delay: 0.05 }}
    >
      <div className="max-w-container mx-auto px-3 sm:px-4 lg:px-8">
        <div className="relative mt-2 sm:mt-3" style={docked ? undefined : HERO_INK}>
          {/* The material, painted behind the row so it can fade without the
              content ever moving. Glass carries its own six layers. */}
          <motion.div
            aria-hidden
            className="pointer-events-none absolute inset-0"
            initial={false}
            animate={{
              opacity: docked ? 1 : 0,
              y: docked ? 0 : -6,
              scale: docked ? 1 : 0.985,
            }}
            transition={{ duration: reduced ? 0 : 0.35, ease: 'easeOut' }}
          >
            <Glass radius={PILL_RADIUS} elevated className="size-full">
              {null}
            </Glass>
            {/* Reading progress: the only line on the bar, and it reports something. */}
            <motion.span
              className="bg-primary absolute right-8 bottom-1.5 left-8 h-px origin-left rounded-full opacity-55"
              style={{ scaleX: progress }}
            />
          </motion.div>

          <div className="relative flex h-14 items-center gap-3 px-3 sm:h-16 sm:px-4">
            <div className="flex flex-1 items-center">
              <a
                href="/"
                aria-label={BRAND.name}
                className="text-foreground group inline-flex items-center rounded-full p-1 transition-colors duration-300"
              >
                <Logo className="size-8 transition-transform duration-300 ease-out group-hover:-translate-y-0.5" />
              </a>
            </div>

            <nav aria-label="Principal" className="hidden items-center gap-0.5 md:flex">
              {NAV_ITEMS.map((item) => {
                const isActive = active === item.href.slice(1);
                return (
                  <a
                    key={item.href}
                    href={item.href}
                    aria-current={isActive ? 'location' : undefined}
                    className={cn(
                      '-tracking-xs relative rounded-full px-3 py-2 text-sm font-medium transition-colors duration-300 hover:bg-[color:var(--cd-glass-panel)]',
                      isActive ? 'text-foreground' : 'text-muted-foreground hover:text-foreground',
                    )}
                  >
                    {item.label}
                    {isActive ? (
                      <motion.span
                        layoutId="nav-active"
                        aria-hidden
                        className="bg-primary absolute inset-x-3 bottom-0.5 h-0.5 rounded-full"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={linkMotion}
                      />
                    ) : null}
                  </a>
                );
              })}
            </nav>

            <div className="flex flex-1 items-center justify-end gap-2">
              <ThemeToggle className="hidden md:inline-flex" />
              <div className="hidden md:block">
                <Button avatar="/shots/mark.webp">{PRIMARY_CTA}</Button>
              </div>
              <button
                ref={triggerRef}
                type="button"
                onClick={() => setOpen((value) => !value)}
                aria-expanded={open}
                aria-controls={SHEET_ID}
                aria-label={open ? 'Cerrar menú' : 'Abrir menú'}
                className="glass-chip text-foreground grid size-10 cursor-pointer place-items-center rounded-full transition-transform duration-200 hover:-translate-y-0.5 md:hidden"
              >
                <MenuGlyph open={open} instant={reduced} />
              </button>
            </div>
          </div>

          <AnimatePresence>
            {open ? (
              <>
                <motion.div
                  key="scrim"
                  aria-hidden
                  onClick={close}
                  className="fixed inset-0 -z-10 md:hidden"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: reduced ? 0 : 0.25, ease: 'easeOut' }}
                  style={{ background: 'color-mix(in srgb, var(--cd-bg) 62%, transparent)' }}
                />
                <motion.div
                  key="sheet"
                  id={SHEET_ID}
                  className="absolute inset-x-0 top-full pt-2 md:hidden"
                  initial={reduced ? { opacity: 0 } : { opacity: 0, y: -10, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={reduced ? { opacity: 0 } : { opacity: 0, y: -8, scale: 0.985 }}
                  transition={{ duration: reduced ? 0 : 0.32, ease: 'easeOut' }}
                >
                  <Glass radius={22} elevated interactive className="p-2">
                    <nav aria-label="Menú" className="flex flex-col">
                      {NAV_ITEMS.map((item, index) => {
                        const isActive = active === item.href.slice(1);
                        return (
                          <motion.a
                            key={item.href}
                            href={item.href}
                            onClick={close}
                            aria-current={isActive ? 'location' : undefined}
                            initial={reduced ? false : { opacity: 0, y: 6 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{
                              duration: reduced ? 0 : 0.4,
                              delay: reduced ? 0 : 0.05 + index * 0.045,
                              ease: 'easeOut',
                            }}
                            className={cn(
                              '-tracking-xs flex items-center justify-between rounded-2xl px-4 py-3 text-[15px] font-medium transition-colors duration-200 hover:bg-[color:var(--cd-glass-panel)]',
                              isActive ? 'text-foreground' : 'text-muted-foreground',
                            )}
                          >
                            {item.label}
                            {isActive ? (
                              <span aria-hidden className="bg-primary size-1.5 rounded-full" />
                            ) : null}
                          </motion.a>
                        );
                      })}
                    </nav>

                    <motion.div
                      className="mt-2 flex items-center justify-between gap-3 px-2 pt-3"
                      style={{ borderTop: '1px solid var(--cd-glass-border)' }}
                      initial={reduced ? false : { opacity: 0, y: 6 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{
                        duration: reduced ? 0 : 0.4,
                        delay: reduced ? 0 : 0.05 + NAV_ITEMS.length * 0.045,
                        ease: 'easeOut',
                      }}
                    >
                      <ThemeToggle />
                      <Button avatar="/shots/mark.webp" onClick={close}>
                        {PRIMARY_CTA}
                      </Button>
                    </motion.div>
                  </Glass>
                </motion.div>
              </>
            ) : null}
          </AnimatePresence>
        </div>
      </div>
    </motion.header>
  );
}
