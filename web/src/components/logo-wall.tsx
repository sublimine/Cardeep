import { motion, useReducedMotion } from 'motion/react';

import { Container } from '@/components/ui/container';
import { SOURCE_WALL_KICKER, SOURCE_WALL_NOTE, SOURCE_WALL_UNIT, SOURCES } from '@/content/site';

/**
 * The tier-1 platforms the index reads.
 *
 * Each one shows its own mark above its name — a wall of bare domain text said
 * nothing, and these are the seven places the Spanish used-car market actually
 * lives. The plates lift on hover and the row assembles with a stagger, so the
 * band has motion without becoming a carousel.
 */
export function LogoWall() {
  const reduced = useReducedMotion();

  return (
    <section id="fuentes" className="w-full">
      <Container className="max-w-7xl py-20">
        <div className="flex flex-col items-center gap-3 text-center">
          <h2 className="font-dm-mono -tracking-xs text-muted-foreground text-sm leading-4 font-normal uppercase">
            {SOURCE_WALL_KICKER}
          </h2>
          <p className="text-muted-foreground -tracking-xs max-w-xl text-sm leading-5">
            {SOURCE_WALL_NOTE}
          </p>
        </div>

        <div className="mx-auto mt-12 flex max-w-6xl flex-wrap items-stretch justify-center gap-3 md:gap-4">
          {SOURCES.map((source, index) => (
            <motion.div
              key={source.name}
              initial={reduced ? false : { opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.4 }}
              transition={{ duration: 0.5, delay: index * 0.07, ease: 'easeOut' }}
              whileHover={reduced ? undefined : { y: -4 }}
              className="glass group flex w-[8.5rem] cursor-default flex-col items-center gap-3 rounded-2xl px-4 py-5 transition-shadow duration-300 md:w-40"
            >
              <img
                src={source.logo}
                alt={source.name}
                width={128}
                height={128}
                loading="lazy"
                decoding="async"
                className="size-10 rounded-xl object-contain transition-transform duration-300 group-hover:scale-110 md:size-11"
              />
              <span className="flex flex-col items-center gap-1 text-center">
                <span className="text-foreground -tracking-sm text-sm leading-4 font-semibold">
                  {source.name}
                </span>
                {/* The count is the argument: not "we support this portal" but
                    "we have counted this many cars in it". */}
                <span className="text-primary font-dm-mono -tracking-xs text-[13px] leading-4 font-medium">
                  {source.count}
                </span>
                <span className="text-subtle -tracking-xs text-[10px] leading-3">
                  {SOURCE_WALL_UNIT}
                </span>
              </span>
            </motion.div>
          ))}
        </div>
      </Container>
    </section>
  );
}
