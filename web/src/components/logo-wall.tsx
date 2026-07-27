import { motion } from 'motion/react';

import { Container } from '@/components/ui/container';
import { SOURCE_WALL_KICKER, SOURCES } from '@/content/site';

/**
 * The wall of platforms the index reads. There is no hidden pool to rotate
 * through — the seven are the seven — so the board is static once assembled and
 * only the staggered entrance survives from the original flip board.
 */

type Source = (typeof SOURCES)[number];

type SourceMarkProps = {
  source: Source;
  index: number;
};

/**
 * One board slot. The 800px perspective on the wrapper is what turns the
 * `rotateX` entrance into a physical flip rather than a squash.
 */
function SourceMark({ source, index }: SourceMarkProps) {
  return (
    <div className="relative h-6 w-30 transition-all duration-300" style={{ perspective: '800px' }}>
      <motion.div
        className="absolute inset-0 flex items-center"
        initial={{ opacity: 0, rotateX: -90 }}
        animate={{ opacity: 1, rotateX: 0 }}
        transition={{ duration: 0.5, delay: index * 0.04, ease: 'easeOut' }}
      >
        <span className="text-heading -tracking-sm text-sm leading-none font-semibold whitespace-nowrap md:text-base">
          {source.mark}
          {source.accent ? (
            <span className="text-muted-foreground font-normal">{source.accent}</span>
          ) : null}
        </span>
      </motion.div>
    </div>
  );
}

export function LogoWall() {
  return (
    <Container className="max-w-7xl py-20">
      <h2 className="font-dm-mono -tracking-xs text-muted-foreground text-center text-sm leading-4 font-normal uppercase">
        {SOURCE_WALL_KICKER}
      </h2>
      {/* The reference wall held fifteen logos and wrapped naturally; seven sources
          at the original 80px gap wrap 6 + 1 and orphan the last mark, so the gap
          tightens just enough to keep the row whole. */}
      <div className="mx-auto mt-12 flex max-w-6xl flex-wrap items-center justify-center gap-x-4 gap-y-4 md:gap-x-12 md:gap-y-14">
        {SOURCES.map((source, index) => (
          <SourceMark key={source.name} source={source} index={index} />
        ))}
      </div>
    </Container>
  );
}
