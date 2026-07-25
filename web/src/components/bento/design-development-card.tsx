import { useEffect, useRef, useState } from 'react';
import {
  AnimatePresence,
  animate,
  motion,
  useInView,
  useMotionValue,
  useReducedMotion,
  useTransform,
} from 'motion/react';

import { Button } from '@/components/ui/button';
import { Glass } from '@/components/ui/glass';
import { BENTO, FIGURES } from '@/content/site';

/**
 * "Índice nacional" — the lead bento card.
 *
 * The artwork is the index itself, running: rows arrive from the bottom, the
 * oldest dissolves into the fade at the top, and every stock count rolls up
 * from zero as its row lands. Underneath, the three national figures count
 * themselves in once the card is on screen. The motion carries the claim the
 * copy makes — this is not a snapshot, it is a census that never stops.
 *
 * On truth: naming real businesses would mean inventing them, so each row is
 * named by what the point of sale *is* — the trade categories the copy already
 * uses ("cada compraventa, cada concesionario, cada garaje de pueblo") — over a
 * real Spanish municipality. Stock counts are illustrative; the figures at the
 * foot are the stamped ones from `FIGURES`.
 */

/* ------------------------------------------------------------------- copy -- */

/**
 * Four strings `site.ts` has no equivalent for: the live badge and the three
 * column headers of the index table. Written in the same voice as the rest.
 */
const LIVE_LABEL = 'En vivo';
const COLUMN_LABELS = ['Punto de venta', 'Municipio', 'Coches'] as const;

/* ------------------------------------------------------------------- data -- */

type IndexRow = {
  /** What the point of sale is, not who it is. */
  kind: string;
  municipality: string;
  stock: number;
};

/** The pool the stream cycles through: fourteen municipalities, fourteen provinces. */
const POINTS: readonly IndexRow[] = [
  { kind: 'Concesionario', municipality: 'Vigo', stock: 312 },
  { kind: 'Compraventa', municipality: 'Getafe', stock: 148 },
  { kind: 'Multimarca', municipality: 'Elche', stock: 96 },
  { kind: 'Garaje', municipality: 'Cangas de Onís', stock: 11 },
  { kind: 'Compraventa', municipality: 'Manresa', stock: 74 },
  { kind: 'Concesionario', municipality: 'Lorca', stock: 203 },
  { kind: 'Multimarca', municipality: 'Talavera de la Reina', stock: 58 },
  { kind: 'Garaje', municipality: 'Baza', stock: 17 },
  { kind: 'Compraventa', municipality: 'Utrera', stock: 63 },
  { kind: 'Concesionario', municipality: 'Santiago de Compostela', stock: 176 },
  { kind: 'Multimarca', municipality: 'Ejea de los Caballeros', stock: 34 },
  { kind: 'Garaje', municipality: 'Almendralejo', stock: 26 },
  { kind: 'Compraventa', municipality: 'Xàtiva', stock: 45 },
  { kind: 'Concesionario', municipality: 'Tudela', stock: 129 },
];

/** The three stamped national figures, in the order they read best. */
const FIGURE_CELLS = [
  { id: 'dealers', prefix: FIGURES.dealers.prefix, raw: FIGURES.dealers.value, suffix: '', label: FIGURES.dealers.label },
  { id: 'vehicles', prefix: '', raw: FIGURES.vehicles.value, suffix: FIGURES.vehicles.suffix, label: FIGURES.vehicles.label },
  { id: 'provinces', prefix: '', raw: FIGURES.provinces.value, suffix: '', label: FIGURES.provinces.label },
] as const;

/* ------------------------------------------------------------------ timing -- */

/** Six rows fill the window the lead card gets on the large layout. */
const VISIBLE_ROWS = 6;
/** Slow enough to read a row before the next one lands, fast enough to feel live. */
const STREAM_INTERVAL_MS = 2300;
const REVEAL_DELAY = 0.28;
const ROW_STAGGER = 0.07;
const ROW_DURATION = 0.5;
const EASE = 'easeOut' as const;
/** One threshold for the card entrance and for arming the stream, so they fire together. */
const VIEWPORT_AMOUNT = 0.25;

/**
 * Shared column template. The header labels and every row use the same one, so
 * the list aligns as a table instead of drifting per row.
 */
const ROW_GRID = 'grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_3.5rem] items-center gap-3';

/* ------------------------------------------------------------------ number -- */

/** Spanish formatting: dot for thousands, comma for the decimal. */
function formatFigure(value: number, decimals: number) {
  const [whole, fraction] = value.toFixed(decimals).split('.');
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return fraction ? `${grouped},${fraction}` : grouped;
}

/** Reads a figure written for humans ('19.000', '1,5') back into a number. */
function parseFigure(raw: string) {
  return {
    amount: Number(raw.replace(/\./g, '').replace(',', '.')),
    decimals: raw.includes(',') ? 1 : 0,
  };
}

/**
 * A number that counts itself up. The value lives in a motion value and is
 * formatted through a transform, so the roll never re-renders React.
 */
function Ticker({
  target,
  decimals,
  duration,
  delay,
  run,
  reduced,
}: {
  target: number;
  decimals: number;
  duration: number;
  delay: number;
  run: boolean;
  reduced: boolean;
}) {
  const count = useMotionValue(reduced ? target : 0);
  const text = useTransform(count, (value) => formatFigure(value, decimals));

  useEffect(() => {
    // Reduced motion parks the number on its final value instead of rolling it.
    if (reduced) {
      count.set(target);
      return;
    }
    if (!run) return;
    const controls = animate(count, target, { duration, delay, ease: EASE });
    return () => controls.stop();
  }, [count, delay, duration, reduced, run, target]);

  return <motion.span>{text}</motion.span>;
}

/* ------------------------------------------------------------------ stream -- */

type FeedEntry = IndexRow & { key: number };

/**
 * The rolling window over the pool. One row leaves the top and one arrives at
 * the bottom per tick; the clock only starts once the card is on screen.
 */
function useIndexStream(active: boolean) {
  const [feed, setFeed] = useState<FeedEntry[]>(() =>
    POINTS.slice(0, VISIBLE_ROWS).map((point, index) => ({ ...point, key: index })),
  );
  const cursor = useRef(VISIBLE_ROWS);

  useEffect(() => {
    if (!active) return;
    const timer = setInterval(() => {
      setFeed((current) => {
        const next = POINTS[cursor.current % POINTS.length];
        const entry: FeedEntry = { ...next, key: cursor.current };
        cursor.current += 1;
        return [...current.slice(1), entry];
      });
    }, STREAM_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [active]);

  return feed;
}

function StreamRow({ entry, delay, reduced }: { entry: FeedEntry; delay: number; reduced: boolean }) {
  return (
    <motion.li
      layout
      className={`glass-chip ${ROW_GRID} rounded-xl px-3 py-2.5`}
      initial={{ opacity: 0, y: reduced ? 0 : 26, scale: reduced ? 1 : 0.97 }}
      // Two details, both about the seam between one row and the next.
      // The stagger belongs to the entrance only: on the shared transition it
      // would also delay a settled row's slide up, tearing the list apart.
      // And the fade runs far shorter than the slide, so the arriving row is
      // solid while it is still rising out of the bottom edge — otherwise its
      // slot reads as a hole for as long as it takes to fade in.
      animate={{
        opacity: 1,
        y: 0,
        scale: 1,
        transition: {
          duration: ROW_DURATION,
          delay,
          ease: EASE,
          opacity: { duration: 0.18, delay, ease: EASE },
        },
      }}
      exit={{ opacity: 0, scale: reduced ? 1 : 0.97, transition: { duration: 0.3, ease: EASE } }}
      transition={{ layout: { duration: 0.45, ease: EASE } }}
    >
      <span className="flex min-w-0 items-center gap-2">
        <span aria-hidden className="bg-primary size-1.5 shrink-0 rounded-full" />
        <span className="text-foreground truncate text-[13px] leading-4 font-medium">
          {entry.kind}
        </span>
      </span>
      <span className="text-muted-foreground truncate text-[13px] leading-4">
        {entry.municipality}
      </span>
      <span className="text-foreground text-right font-mono text-[13px] leading-4 tabular-nums">
        <Ticker
          target={entry.stock}
          decimals={0}
          duration={0.7}
          delay={delay}
          run
          reduced={reduced}
        />
      </span>
    </motion.li>
  );
}

/* -------------------------------------------------------------------- card -- */

export function DesignDevelopmentCard() {
  const shellRef = useRef<HTMLDivElement>(null);
  const inView = useInView(shellRef, { once: true, amount: VIEWPORT_AMOUNT });
  const reduced = useReducedMotion() ?? false;
  const feed = useIndexStream(inView && !reduced);

  return (
    // Grid placement and the card's own entrance belong to the bento slot that
    // wraps this component; what is left here is the hover lift and the
    // choreography inside the panel.
    <motion.div
      ref={shellRef}
      className="flex min-w-0"
      whileHover={reduced ? undefined : { y: -3, transition: { duration: 0.25, ease: EASE } }}
    >
      <Glass radius={20} elevated interactive className="h-full w-full">
        <div className="flex h-full min-h-0 flex-col gap-5 p-5">
          <header className="flex items-start justify-between gap-4">
            <motion.h2
              className="text-foreground text-base leading-6 font-medium"
              initial={{ opacity: 0, y: reduced ? 0 : 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: VIEWPORT_AMOUNT }}
              transition={{ duration: 0.45, delay: 0.05, ease: EASE }}
            >
              {BENTO.feature.title}
            </motion.h2>
            <motion.span
              className="glass-chip inline-flex shrink-0 items-center gap-2 rounded-full px-2.5 py-1"
              initial={{ opacity: 0, y: reduced ? 0 : 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: VIEWPORT_AMOUNT }}
              transition={{ duration: 0.45, delay: 0.1, ease: EASE }}
            >
              <span className="relative flex size-1.5 shrink-0">
                {reduced ? null : (
                  <motion.span
                    aria-hidden
                    className="bg-primary absolute inset-0 rounded-full"
                    animate={{ opacity: [0.5, 0], scale: [1, 2.8] }}
                    transition={{ duration: 2.3, repeat: Infinity, ease: EASE }}
                  />
                )}
                <span className="bg-primary relative size-1.5 rounded-full" />
              </span>
              <span className="text-muted-foreground text-[11px] leading-4">{LIVE_LABEL}</span>
            </motion.span>
          </header>

          <motion.p
            className="text-muted-foreground max-w-prose text-sm leading-relaxed"
            initial={{ opacity: 0, y: reduced ? 0 : 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: VIEWPORT_AMOUNT }}
            transition={{ duration: 0.45, delay: 0.14, ease: EASE }}
          >
            {BENTO.feature.body}
          </motion.p>

          <div className="flex min-h-0 flex-1 flex-col">
            <motion.div
              className={`border-line ${ROW_GRID} border-b px-3 pb-2`}
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true, amount: VIEWPORT_AMOUNT }}
              transition={{ duration: 0.4, delay: 0.2, ease: EASE }}
            >
              {COLUMN_LABELS.map((label, index) => (
                <span
                  key={label}
                  className={
                    'text-subtle text-[10px] leading-3 font-medium tracking-[0.14em] uppercase' +
                    (index === COLUMN_LABELS.length - 1 ? ' text-right' : '')
                  }
                >
                  {label}
                </span>
              ))}
            </motion.div>

            {/* The window the index runs through. The list is pinned to the
                bottom edge, so a new row rises into it from underneath and the
                oldest one is already inside the top fade when it leaves. */}
            <div className="relative flex min-h-[17rem] flex-1 flex-col justify-end overflow-hidden pt-2 mask-t-from-80%">
              <ul className="flex flex-col gap-2">
                <AnimatePresence mode="popLayout">
                  {inView
                    ? feed.map((entry) => (
                        <StreamRow
                          key={entry.key}
                          entry={entry}
                          // Only the first painted window staggers; everything
                          // after it is a single row arriving on its own.
                          delay={entry.key < VISIBLE_ROWS ? REVEAL_DELAY + entry.key * ROW_STAGGER : 0}
                          reduced={reduced}
                        />
                      ))
                    : null}
                </AnimatePresence>
              </ul>
            </div>
          </div>

          <motion.div
            className="border-line grid grid-cols-3 gap-3 border-t pt-4"
            initial={{ opacity: 0, y: reduced ? 0 : 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: VIEWPORT_AMOUNT }}
            transition={{ duration: 0.5, delay: 0.5, ease: EASE }}
          >
            {FIGURE_CELLS.map((cell, index) => {
              const { amount, decimals } = parseFigure(cell.raw);
              return (
                <div key={cell.id} className="flex flex-col gap-1">
                  <span className="text-foreground font-mono text-xl leading-6 tabular-nums">
                    {cell.prefix}
                    <Ticker
                      target={amount}
                      decimals={decimals}
                      duration={1.2}
                      delay={0.55 + index * 0.1}
                      run={inView}
                      reduced={reduced}
                    />
                    {cell.suffix}
                  </span>
                  <span className="text-muted-foreground text-[11px] leading-4">{cell.label}</span>
                </div>
              );
            })}
          </motion.div>

          {/* No date stamp here: the section header already carries it, and a
              third copy in the same bento would be noise. */}
          <motion.div
            initial={{ opacity: 0, y: reduced ? 0 : 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: VIEWPORT_AMOUNT }}
            transition={{ duration: 0.5, delay: 0.6, ease: EASE }}
          >
            <Button>{BENTO.feature.cta}</Button>
          </motion.div>
        </div>
      </Glass>
    </motion.div>
  );
}
