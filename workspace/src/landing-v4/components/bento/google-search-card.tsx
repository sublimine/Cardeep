import { useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { FileText, History, Layers } from 'lucide-react';

import { BENTO } from '@landing/content/site';
import { cn } from '@landing/lib/utils';

type Card = (typeof BENTO.history.cards)[number];

const GLYPHS = {
  precio: History,
  anuncio: Layers,
  papeles: FileText,
} as const;

/**
 * Resting geometry of the stack.
 *
 * Each card behind the front one drops 18px, sheds 5% of its width and tips a
 * degree and a half further. The tilt is what stops the stack reading as a
 * flat-packed accordion: three rectangles offset straight down look like a list
 * that failed to lay out; the same three rotated look like paper.
 */
const DROP = 18;
const SHRINK = 0.05;
const TILT = 1.5;
/** Row pitch once the deck is fanned. */
const FAN = 52;

/**
 * The record, as a deck.
 *
 * The stack IS the argument. A car's history is not three facts side by side, it
 * is one thing with layers, and a fanned deck says "there is more underneath"
 * without spending a line of copy saying it. Hovering the tile fans the deck;
 * hovering a sheet lifts that sheet clear of the others.
 */
function HistoryDeck() {
  const [open, setOpen] = useState(false);
  const [lifted, setLifted] = useState<string | null>(null);
  const reduced = useReducedMotion();
  const cards = BENTO.history.cards;

  return (
    <div
      className="relative mt-4 h-[176px] w-full"
      onPointerEnter={() => setOpen(true)}
      onPointerLeave={() => {
        setOpen(false);
        setLifted(null);
      }}
    >
      {cards.map((card: Card, i) => {
        const Glyph = GLYPHS[card.id];
        const isLifted = lifted === card.id;
        const y = open ? i * FAN : i * DROP;
        const scale = open ? 1 : 1 - i * SHRINK;
        const rotate = open ? 0 : i * TILT;

        return (
          <motion.article
            key={card.id}
            onPointerEnter={() => setLifted(card.id)}
            /* An OPAQUE sheet, not glass.
             *
             * `glass-quiet` here meant a blurred translucent card stacked on two
             * more of itself on top of the tile's own glass — four backdrop
             * filters deep, which composited into a white smear where the rear
             * sheets should have been. Paper stacks; glass on glass just fogs.
             * The surface token flips with the theme, so the deck stays opaque in
             * both. */
            className={cn(
              'bg-secondary absolute inset-x-0 top-0 rounded-xl border p-3 shadow-[0_6px_18px_-10px_rgb(5_20_44/0.5)]',
              isLifted ? 'border-brand/40' : 'border-foreground/10',
            )}
            style={{ zIndex: cards.length - i, transformOrigin: 'top center' }}
            animate={
              /* Reduced motion gets the deck already fanned and still. The
               * information is the point; the fan is only how it is revealed, so
               * the preference removes the reveal, never the content. */
              reduced
                ? { y: i * FAN, scale: 1, rotate: 0 }
                : { y: isLifted ? y - 6 : y, scale, rotate }
            }
            transition={{ type: 'spring', stiffness: 320, damping: 34 }}
          >
            <div className="flex items-start gap-2.5">
              {/* The paperwork sheet is deliberately NOT brand-coloured. Blue on
                * this page means "the index knows this"; the DGT's data is not
                * the index's, and colouring it the same would be the quietest
                * possible lie. */}
              <span
                className={cn(
                  'mt-px flex size-6 shrink-0 items-center justify-center rounded-md',
                  card.source === 'dgt'
                    ? 'bg-muted-foreground/12 text-muted-foreground'
                    : 'bg-brand/12 text-brand',
                )}
              >
                <Glyph className="size-3" strokeWidth={2.25} aria-hidden="true" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-muted-foreground font-mono text-[9.5px] tracking-[0.1em] uppercase">
                  {card.kicker}
                </p>
                <p className="text-foreground mt-0.5 text-[13px] leading-tight font-medium">
                  {card.headline}
                </p>
                <p className="text-muted-foreground mt-0.5 text-[11px] leading-tight">
                  {card.detail}
                </p>
              </div>
            </div>
          </motion.article>
        );
      })}
    </div>
  );
}

/**
 * The vehicle-record tile.
 *
 * What this replaces was a mocked Google-style search box that typed out a query
 * and returned one verdict: the listing was 1.340 € over the median. The page
 * already makes that point twice — the comparison table and the movements feed
 * both carry it — so this tile was spending the widest slot in the row on the
 * page's third-best telling of a claim it had already won.
 */
export function GoogleSearchCard() {
  return (
    <div className="glass col-span-1 max-h-(--box-min-height) min-h-(--box-min-height) overflow-hidden rounded-2xl p-4 lg:col-span-3">
      <h2 className="text-foreground text-base font-medium">{BENTO.history.title}</h2>
      {/* The tile's only line of copy, and it carries the whole promise: the
        * dealer assembles nothing. */}
      <p className="text-muted-foreground mt-1 text-[12px] leading-snug">{BENTO.history.lede}</p>
      <HistoryDeck />
    </div>
  );
}
