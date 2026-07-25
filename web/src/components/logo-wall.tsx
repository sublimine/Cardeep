import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';

import { Container } from '@/components/ui/container';

/**
 * Twenty logos exist but only fifteen slots are on screen. The wall keeps the
 * first fifteen on load, then periodically flips one slot to a logo from the
 * unused remainder, so the board never shows the same set for long.
 */
const LOGO_POOL_SIZE = 20;
const VISIBLE_SLOTS = 15;

/** How often a slot flips, and how many flip together. */
const FLIP_INTERVAL_MS = 3200;
const FLIPS_PER_TICK = 2;

const INITIAL_SLOTS = Array.from({ length: VISIBLE_SLOTS }, (_, index) => index + 1);

function pickReplacement(current: number[]): { slot: number; logo: number } | null {
  const shown = new Set(current);
  const bench = [];
  for (let logo = 1; logo <= LOGO_POOL_SIZE; logo++) {
    if (!shown.has(logo)) bench.push(logo);
  }
  if (bench.length === 0) return null;
  return {
    slot: Math.floor(Math.random() * current.length),
    logo: bench[Math.floor(Math.random() * bench.length)],
  };
}

type LogoSlotProps = {
  logo: number;
  index: number;
};

/**
 * One board slot. The 800px perspective on the wrapper is what turns the
 * `rotateX` swap into a physical flip rather than a squash.
 */
function LogoSlot({ logo, index }: LogoSlotProps) {
  return (
    <div className="relative h-6 w-30 transition-all duration-300" style={{ perspective: '800px' }}>
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.div
          key={logo}
          className="absolute inset-0"
          initial={{ opacity: 0, rotateX: -90 }}
          animate={{ opacity: 1, rotateX: 0 }}
          exit={{ opacity: 0, rotateX: 90 }}
          transition={{ duration: 0.5, delay: index * 0.04, ease: 'easeOut' }}
        >
          <img
            alt={`Company logo ${index + 1}`}
            draggable={false}
            loading="lazy"
            width={120}
            height={40}
            decoding="async"
            className="h-4 w-auto object-contain transition-opacity md:h-6"
            src={`/logos/${logo}.webp`}
          />
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export function LogoWall() {
  const [slots, setSlots] = useState<number[]>(INITIAL_SLOTS);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setSlots((current) => {
        let next = current;
        for (let i = 0; i < FLIPS_PER_TICK; i++) {
          const swap = pickReplacement(next);
          if (!swap) break;
          next = next.map((logo, index) => (index === swap.slot ? swap.logo : logo));
        }
        return next;
      });
    }, FLIP_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <Container className="max-w-7xl py-20">
      <h2 className="font-dm-mono -tracking-xs text-muted-foreground text-center text-sm leading-4 font-normal uppercase">
        Trusted by fast-growing startups
      </h2>
      <div className="mx-auto mt-12 flex max-w-6xl flex-wrap items-center justify-center gap-x-4 gap-y-4 md:gap-x-20 md:gap-y-14">
        {slots.map((logo, index) => (
          <LogoSlot key={index} logo={logo} index={index} />
        ))}
      </div>
    </Container>
  );
}
