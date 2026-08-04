import { useEffect, useId, useRef, useState, type RefObject } from 'react';
import { motion, useReducedMotion, type Transition } from 'framer-motion';
import {
  Car,
  ChevronRight,
  Gauge,
  IdCard,
  LineChart,
  ShieldCheck,
  X,
  type LucideIcon,
} from 'lucide-react';

import PLATFORM_LOGOS from '@landing/data/platform-logos.json';
import { BENTO, SOURCES } from '@landing/content/site';
import { cn } from '@landing/lib/utils';

/* -------------------------------------------------------------------------- */
/*                                   Types                                    */
/* -------------------------------------------------------------------------- */

/**
 * The content block is authored under `as const`, so TypeScript widens every
 * chapter into its own literal shape and the events into a union whose members
 * disagree about which optional keys exist. Reading `event.platform` off that
 * union is an error even though the data is perfectly regular, so the shape is
 * declared once here and the block is read through it. This is the only cast in
 * the file and it narrows nothing that the content module does not already
 * guarantee — every field below exists on every record in `site.ts`.
 */
type EventTone = 'alert' | 'good';

type HistoryEvent = {
  date: string;
  text: string;
  value: string;
  tone?: EventTone;
  /** Key into the platform-logo manifest. Only the market chapter uses it. */
  platform?: string;
};

type Chapter = {
  id: string;
  tab: string;
  kicker: string;
  headline: string;
  detail: string;
  source: 'index' | 'dgt';
  origin: string;
  events: readonly HistoryEvent[];
};

const HISTORY = BENTO.history;
const CHAPTERS = HISTORY.chapters as readonly Chapter[];

/* -------------------------------------------------------------------------- */
/*                              Platform artwork                              */
/* -------------------------------------------------------------------------- */

type LogoEntry = {
  file: string;
  width: number;
  height: number;
  onDark: { file: string } | null;
};

const LOGOS = PLATFORM_LOGOS as unknown as Record<string, LogoEntry>;

/** Wordmark fallbacks, by platform name, for anything the manifest lacks. */
type Wordmark = { mark: string; accent: string };

const WORDMARKS = new Map<string, Wordmark>(
  SOURCES.map((source): [string, Wordmark] => [
    source.name,
    { mark: source.mark, accent: source.accent },
  ]),
);

/**
 * Optical height for a platform mark inside a timeline row, in CSS px.
 *
 * The seven marks have wildly different aspect ratios (coches.net is 130x20,
 * Milanuncios 1000x179, AutoScout24 1006x239), so they are matched on HEIGHT and
 * left to take whatever width that implies. Matching on width instead would make
 * the squat marks tower over the wide ones.
 */
const MARK_HEIGHT = 11;

/**
 * Per-mark optical correction, measured rather than eyeballed.
 *
 * Every file in the manifest fills its own viewBox, so scaling by the box gets
 * six of the seven right. AutoScout24 is the exception because its 2022 lockup is
 * not a wordmark, it is letters sitting on a yellow field: rendering each mark at
 * 88px tall and measuring the band its letterforms occupy gives 84/88 for
 * coches.net, 87/88 for Autocasión, 86/88 for motor.es — and 45/88 for
 * AutoScout24, whose type covers barely half of what it is matched against. Sized
 * on the field alone it reads as the runt of the row.
 *
 * The correction is deliberately partial. Equalising the LETTERS would need ~1.9x
 * and would leave the yellow field towering over its neighbours, so the mark is
 * nudged until it holds its own and no further; a boxed logo is matched on its
 * container, not on its type.
 */
const MARK_SCALE: Record<string, number> = { AutoScout24: 1.22 };

/**
 * A platform's real, official mark.
 *
 * WHY THIS EXISTS AT ALL. The previous build of this section — and the card
 * beside it — printed platform names as styled text because "no platform ships a
 * logo asset in public/logos". That was true when it was written and it is not
 * true now: `public/logos/platforms/` holds all seven marks, downloaded from the
 * platforms' own CDNs and from Wikimedia, with four official negative variants,
 * and `data/platform-logos.json` records where each one came from. When a
 * platform appears inside a visual surface it gets its LOGO.
 *
 * The manifest is still the authority rather than this file: if a name is not in
 * it, the mark degrades to that platform's wordmark from SOURCES (its own
 * lettering plus its accent), never to a substitute drawn from somewhere else. A
 * car marque's badge standing in for a portal's logo is precisely the shortcut
 * that made the last version dishonest.
 */
function PlatformMark({ name }: { name: string }) {
  const entry = LOGOS[name];

  if (!entry) {
    const wordmark = WORDMARKS.get(name);
    return (
      <span className="text-foreground text-[10.5px] leading-none font-semibold">
        {wordmark ? wordmark.mark : name}
        {wordmark?.accent ? <span className="text-brand-soft">{wordmark.accent}</span> : null}
      </span>
    );
  }

  /* Width is derived from the manifest's real intrinsic box rather than left to
   * `auto`, so the row reserves the right space on the very first paint and the
   * timeline never reflows as the SVGs land. */
  const height = Math.round(MARK_HEIGHT * (MARK_SCALE[name] ?? 1));
  const width = Math.round((height * entry.width) / entry.height);

  return (
    <span className="inline-flex shrink-0 translate-y-px items-center align-middle">
      <img
        src={entry.file}
        alt={name}
        width={width}
        height={height}
        style={{ height }}
        /* Marks with an official negative are swapped wholesale on dark. The
         * ones without (Milanuncios, Wallapop, Autocasión) are single-colour and
         * read on both grounds, which the manifest states explicitly — they are
         * not missing a variant, they do not need one. */
        className={cn('block w-auto', entry.onDark && 'dark:hidden')}
      />
      {entry.onDark ? (
        <img
          src={entry.onDark.file}
          alt=""
          aria-hidden="true"
          width={width}
          height={height}
          style={{ height }}
          className="hidden w-auto dark:block"
        />
      ) : null}
    </span>
  );
}

/* -------------------------------------------------------------------------- */
/*                             Chapter vocabulary                             */
/* -------------------------------------------------------------------------- */

const GLYPHS: Record<string, LucideIcon> = {
  origen: IdCard,
  itv: Gauge,
  cargas: ShieldCheck,
  mercado: LineChart,
};

/**
 * Source is the one thing on this tile that may never be decorative.
 *
 * Blue means "the index produced this": Cardeep saw the listing, kept every
 * version of it, and can show its price, its portals, its photos and its
 * disappearances because it holds them. Grey means somebody else produced it —
 * the DGT, the ITV stations, a lender — and Cardeep is only carrying it. Painting
 * the paperwork in the brand colour would claim data this product cannot derive
 * from an open market, which is the quietest way a page can lie.
 */
const SOURCE_STYLE = {
  index: { chip: 'bg-brand/12 text-brand', dot: 'bg-brand' },
  dgt: { chip: 'bg-muted-foreground/15 text-muted-foreground', dot: 'bg-muted-foreground' },
} as const;

/** The tone ramp for a single dated event. `undefined` is the neutral majority. */
const EVENT_DOT: Record<EventTone, string> = {
  alert: 'bg-dusty-red',
  good: 'bg-dusty-green',
};

const EVENT_TEXT: Record<EventTone, string> = {
  /* `--color-dusty-red` is #ff6464 on light, which is a fine dot and an illegible
   * body colour on a near-white card; the darker sibling carries the text there
   * and the token itself (#ff8383 on dark) takes over where it reads properly. */
  alert: 'text-[#b3403a] dark:text-dusty-red font-medium',
  good: 'text-foreground',
};

/**
 * The focus treatment, designed rather than inherited.
 *
 * Because opening a chapter moves focus programmatically, Chrome applies
 * `:focus-visible` and paints its default ring — which on the open panel showed
 * up as a hard blue rule slicing across the report. A surface that manages focus
 * has to dress it too: one brand ring, on the same radius the element already
 * carries, in both themes.
 */
const FOCUS =
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/55 ' +
  'focus-visible:ring-offset-1 focus-visible:ring-offset-background';

/**
 * The morph. Stiff enough to feel mechanical rather than floaty, damped just
 * short of critical so a card arriving in the strip settles instead of bouncing.
 */
const SPRING: Transition = { type: 'spring', stiffness: 260, damping: 30, mass: 0.85 };
const STILL: Transition = { duration: 0 };

/* -------------------------------------------------------------------------- */
/*                                  Timeline                                  */
/* -------------------------------------------------------------------------- */

/**
 * A chapter's chronology: one spine, one dot per event, a date column that never
 * moves, and the value flushed right so a reader can scan prices and readings
 * down a single edge.
 *
 * This is the part the previous version had none of. It showed three summary
 * headlines — "5 bajadas desde el alta", "ITV, titulares y cargas" — and called
 * that a history. A history is dated; a headline is a claim about one. Every row
 * here carries the day it happened.
 */
function Timeline({ chapter }: { chapter: Chapter }) {
  const neutralDot = SOURCE_STYLE[chapter.source].dot;

  const last = chapter.events.length - 1;

  return (
    /* `min-h-full` plus `justify-center` is what stops a four-event chapter from
     * sitting in the top half of the panel with 50px of nothing under it. It is
     * also the only form of centring that is safe inside a scroller: the list can
     * never be shorter than the box, so free space — and therefore centring —
     * only exists when the content fits. The ten-event chapter overflows, the
     * list grows past `min-h-full`, and it scrolls from its first row as usual,
     * with none of the clipped-top failure that centring a scroll container
     * normally causes. */
    <ol className="flex min-h-full flex-col justify-center">
      {chapter.events.map((event, index) => (
        <li key={`${event.date}-${event.text}`} className="relative flex items-start gap-2 py-[5px] pl-4">
          {/* The spine is drawn per row rather than as one absolute rule down the
            * list, so it begins at the first dot and ends at the last however the
            * list is positioned. A single absolute line assumed the list started
            * at the top of the panel, and trailed off into empty space the moment
            * a short chapter was centred. */}
          {last > 0 ? (
            <span
              aria-hidden="true"
              className={cn(
                'bg-foreground/12 absolute left-[3px] w-px',
                /* 10px is the dot's centre: `top-[6px]` plus half of `size-[7px]`.
                 * The first row's segment starts there and the last row's ends
                 * there, so the line is bounded by the chronology itself. */
                index === 0
                  ? 'top-[10px] bottom-0'
                  : index === last
                    ? 'top-0 h-[10px]'
                    : 'inset-y-0',
              )}
            />
          ) : null}
          <span
            aria-hidden="true"
            className={cn(
              /* The ring is the card's own fill, so each dot punches a clean hole
               * in the spine instead of sitting on top of a visible line. */
              'ring-secondary absolute top-[6px] left-0 size-[7px] rounded-full ring-2',
              event.tone ? EVENT_DOT[event.tone] : neutralDot,
            )}
          />
          {/* The date column is sized to the longest date the content can hold
            * ("12 mar 2019" at 9.5px mono) and forbidden from wrapping. At 58px
            * every full date broke onto a second line and each row grew to
            * double height, which pushed half the chronology below the fold. */}
          <time className="text-muted-foreground w-[70px] shrink-0 font-mono text-[9.5px] leading-[1.6] tracking-tight whitespace-nowrap tabular-nums">
            {event.date}
          </time>
          <span
            className={cn(
              'flex min-w-0 flex-1 flex-wrap items-center gap-x-1.5 text-[11px] leading-[1.45]',
              event.tone ? EVENT_TEXT[event.tone] : 'text-foreground',
            )}
          >
            {event.text}
            {event.platform ? <PlatformMark name={event.platform} /> : null}
          </span>
          <span
            className={cn(
              'shrink-0 text-right font-mono text-[10px] leading-[1.5] tabular-nums',
              event.tone === 'alert'
                ? 'text-[#b3403a] dark:text-dusty-red font-medium'
                : 'text-muted-foreground',
            )}
          >
            {event.value}
          </span>
        </li>
      ))}
    </ol>
  );
}

/* -------------------------------------------------------------------------- */
/*                          The three chapter states                          */
/* -------------------------------------------------------------------------- */

type ChapterProps = {
  chapter: Chapter;
  layoutId: string;
  transition: Transition;
};

/**
 * Resting state: one of four cells in the record's index.
 *
 * `borderRadius` is an inline style rather than a `rounded-*` class on purpose.
 * A layout animation rescales the box, and a radius declared in CSS is rescaled
 * with it — the corners visibly go oval mid-flight. Framer only corrects the
 * radius it owns, which means the value has to be handed to it.
 */
function ChapterCard({
  chapter,
  layoutId,
  transition,
  buttonRef,
  onOpen,
}: ChapterProps & {
  buttonRef: (node: HTMLButtonElement | null) => void;
  onOpen: (id: string) => void;
}) {
  const Glyph = GLYPHS[chapter.id];
  const style = SOURCE_STYLE[chapter.source];
  const isIndex = chapter.source === 'index';

  return (
    <motion.button
      ref={buttonRef}
      type="button"
      layoutId={layoutId}
      transition={transition}
      style={{ borderRadius: 12 }}
      onClick={() => onOpen(chapter.id)}
      aria-expanded={false}
      className={cn(
        'group relative flex h-full min-w-0 flex-col overflow-hidden border p-2.5 text-left',
        'shadow-[0_6px_18px_-12px_rgb(5_20_44/0.45)] transition-colors duration-200',
        FOCUS,
        /* The chapter Cardeep actually owns is the only one carrying the brand,
         * so the eye lands on the index's own contribution first. */
        isIndex
          ? 'border-brand/25 bg-brand/[0.055] hover:border-brand/55'
          : 'bg-secondary border-foreground/10 hover:border-foreground/25',
      )}
    >
      <span className="flex items-center gap-1.5">
        <span
          className={cn(
            'flex size-[18px] shrink-0 items-center justify-center rounded-md',
            style.chip,
          )}
        >
          <Glyph className="size-3" strokeWidth={2.25} aria-hidden="true" />
        </span>
        <span className="text-muted-foreground truncate font-mono text-[8.5px] tracking-[0.11em] uppercase">
          {chapter.kicker}
        </span>
        <span aria-hidden="true" className={cn('ml-auto size-1.5 shrink-0 rounded-full', style.dot)} />
        {/* The chevron sits in a bordered well rather than floating as a bare
          * glyph. A still frame of this tile has to say "these open" on its own —
          * the last version relied entirely on hover to reveal that anything was
          * interactive, which tells a touch screen nothing and a screenshot less. */}
        <span className="border-foreground/15 group-hover:border-brand/50 group-hover:bg-brand/10 flex size-[15px] shrink-0 items-center justify-center rounded-md border transition-colors duration-200">
          <ChevronRight
            aria-hidden="true"
            className="text-muted-foreground/70 group-hover:text-brand size-2.5 transition-transform duration-200 group-hover:translate-x-px"
          />
        </span>
      </span>

      {/* `truncate`, not `line-clamp-1`. The clamp switches the box to
        * `-webkit-box`, which crops on the line box rather than on the glyph box
        * and beheaded every descender on the tile — "Libre de cargas desde 2024"
        * lost the tail of its g, "4 bajadas y una reaparición" its j and p. */}
      <span className="text-foreground mt-1.5 truncate text-[12.5px] leading-[1.35] font-medium">
        {chapter.headline}
      </span>
      {/* The chapter's origin is NOT repeated here. Four cards each carrying a
        * fourth line of 8px monospace overflowed a 92px cell and collided with
        * the detail above it; the coloured dot beside the kicker already maps to
        * the legend, and the panel names the source in full the moment it opens. */}
      <span className="text-muted-foreground mt-0.5 line-clamp-2 text-[10.5px] leading-[1.35]">
        {chapter.detail}
      </span>
    </motion.button>
  );
}

/** Parked state: the chapters that are not open, docked into the strip. */
function ChapterTab({
  chapter,
  layoutId,
  transition,
  buttonRef,
  onOpen,
}: ChapterProps & {
  buttonRef: (node: HTMLButtonElement | null) => void;
  onOpen: (id: string) => void;
}) {
  const Glyph = GLYPHS[chapter.id];
  const style = SOURCE_STYLE[chapter.source];

  return (
    <motion.button
      ref={buttonRef}
      type="button"
      layoutId={layoutId}
      transition={transition}
      style={{ borderRadius: 8 }}
      onClick={() => onOpen(chapter.id)}
      aria-expanded={false}
      /* The accessible name has to survive the label being dropped on a narrow
       * tile, so it is stated rather than left to the visible text. */
      aria-label={chapter.kicker}
      className={cn(
        'bg-secondary border-foreground/10 hover:border-foreground/30 flex h-full shrink-0',
        'items-center gap-1 overflow-hidden border px-1.5 transition-colors duration-200',
        FOCUS,
        chapter.source === 'index' && 'border-brand/25 bg-brand/[0.055] hover:border-brand/55',
      )}
    >
      <span
        className={cn('flex size-3.5 shrink-0 items-center justify-center rounded', style.chip)}
      >
        <Glyph className="size-2.5" strokeWidth={2.5} aria-hidden="true" />
      </span>
      {/* Sized against the TILE, not the viewport.
        *
        * The two do not track each other here: the tile is 343px wide at a 375px
        * viewport, 354px at 768px, 387px at 1024px and only 558px at 1440px,
        * because the bento goes from one column to two and then to a five-column
        * track. A `sm:` breakpoint therefore revealed the labels at 768px — where
        * the tile is at its NARROWEST — and the third tab was clipped by the edge
        * of the strip. A container query asks the only question that matters: is
        * there room here. */
      }
      <span className="text-muted-foreground hidden font-mono text-[8.5px] tracking-[0.1em] whitespace-nowrap uppercase @min-[440px]:inline">
        {chapter.tab}
      </span>
    </motion.button>
  );
}

/** Open state: the same element, now the report itself. */
function ChapterPanel({
  chapter,
  layoutId,
  transition,
  reduced,
  headerRef,
  onClose,
}: ChapterProps & {
  reduced: boolean;
  headerRef: RefObject<HTMLButtonElement>;
  onClose: () => void;
}) {
  const Glyph = GLYPHS[chapter.id];
  const style = SOURCE_STYLE[chapter.source];

  return (
    <motion.div
      layoutId={layoutId}
      transition={transition}
      style={{ borderRadius: 12 }}
      className={cn(
        'bg-secondary border-foreground/10 absolute inset-0 flex flex-col overflow-hidden border',
        'shadow-[0_10px_30px_-18px_rgb(5_20_44/0.55)]',
        chapter.source === 'index' && 'border-brand/25',
      )}
    >
      {/* The whole header collapses the chapter, so the target is a bar and not a
        * 12px glyph. The X is the affordance, not the hit area. */}
      <button
        ref={headerRef}
        type="button"
        onClick={onClose}
        aria-expanded={true}
        className={cn(
          'group flex shrink-0 items-center gap-1.5 px-2.5 pt-2 pb-1.5 text-left',
          /* No ring offset on this one: the header is flush with the panel's own
           * edge, and an offset ring would be clipped by `overflow-hidden` into
           * the same hard rule the default outline produced. */
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/45 focus-visible:ring-inset',
        )}
      >
        <span
          className={cn(
            'flex size-[18px] shrink-0 items-center justify-center rounded-md',
            style.chip,
          )}
        >
          {/* Same glyph metrics as the resting card: this element IS that card,
            * and a mark that changed weight halfway through the morph would give
            * the illusion away. */}
          <Glyph className="size-3" strokeWidth={2.25} aria-hidden="true" />
        </span>
        <span className="text-foreground shrink-0 text-[12px] leading-none font-medium">
          {chapter.kicker}
        </span>
        <span className="border-foreground/12 text-muted-foreground ml-1 flex min-w-0 items-center gap-1 rounded-full border px-1.5 py-[3px] font-mono text-[8px] tracking-[0.1em] uppercase">
          <span aria-hidden="true" className={cn('size-1 shrink-0 rounded-full', style.dot)} />
          <span className="truncate">{chapter.origin}</span>
        </span>
        <span className="text-muted-foreground/60 group-hover:text-foreground group-hover:bg-foreground/8 ml-auto flex size-[18px] shrink-0 items-center justify-center rounded-md transition-colors">
          <X className="size-3" strokeWidth={2.5} aria-hidden="true" />
        </span>
      </button>

      <span aria-hidden="true" className="bg-foreground/10 mx-2.5 h-px shrink-0" />

      {/* The chronology is faded in a beat AFTER the box has begun to open. During
        * a layout animation the box is transformed, and anything inside it that is
        * not itself projected rides that transform — text would arrive squashed to
        * the size of the closed card and stretch out. Letting the box travel first
        * and the content arrive second costs 90ms and removes the smear entirely.
        *
        * It scrolls INSIDE the panel because this tile is pinned to 314px in both
        * directions: a chapter that grew the container would drag the whole bento
        * row with it. */}
      <motion.div
        initial={reduced ? false : { opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={reduced ? STILL : { delay: 0.09, duration: 0.26, ease: [0.16, 1, 0.3, 1] }}
        className={cn(
          'min-h-0 flex-1 overflow-y-auto px-2.5 pt-1.5 pb-2 mask-b-from-92%',
          '[scrollbar-width:thin] [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-thumb]:rounded-full',
          '[&::-webkit-scrollbar-thumb]:bg-foreground/15 [&::-webkit-scrollbar-track]:bg-transparent',
        )}
      >
        <Timeline chapter={chapter} />
      </motion.div>
    </motion.div>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

/**
 * The vehicle record, as a dossier that opens.
 *
 * WHAT THIS REPLACES, AND WHY IT FAILED. The last version was three summary cards
 * fanned on hover. Three things were wrong with it and all three were visible in
 * a screenshot. It was not a history: no row on it carried a date, so a tile
 * promising "todo lo que le ha pasado a un coche" showed no events at all. Its
 * own geometry hid it: each sheet dropped 18px onto the one behind, which put the
 * second and third kickers physically underneath the card in front — two of the
 * three titles were unreadable at rest. And it answered only to the pointer, so
 * on a touch screen, and for anyone driving the page from a keyboard, nothing on
 * the tile was reachable at all; a scripted pass over the rendered page found
 * zero focusable controls inside it.
 *
 * WHAT IT IS NOW. Four chapters of one car's life, each a button. Opening one
 * sends the other three up into the strip and expands the chosen one into a dated
 * chronology, and every one of those moves is a real layout animation — the same
 * element travels from grid cell to rail or to panel under spring physics, rather
 * than one box being hidden while another appears. Clicking the open chapter's
 * header puts it back.
 *
 * THE HONESTY LINE, WHICH IS THE POINT OF THE LEGEND. Cardeep derives the market
 * chapter from its own index and marks it in the brand blue. Registration,
 * keepers, ITV, finance and accident data come from the DGT, from ITV stations and
 * from lenders; those chapters are drawn in grey and each names its own origin.
 * The tile never implies the index produced something it cannot produce — and the
 * single most valuable row on it, the odometer that disagrees with the last ITV,
 * is worth something precisely BECAUSE the two families are kept apart.
 */
export function GoogleSearchCard() {
  const [openId, setOpenId] = useState<string | null>(null);
  const uid = useId();
  const reduced = useReducedMotion() ?? false;

  /**
   * Focus has to follow the disclosure, because the control the user pressed
   * stops existing the instant they press it.
   *
   * A scripted keyboard pass caught this: tabbing to a chapter and hitting Enter
   * opened the panel and then dropped focus onto `<body>`, because the grid card
   * that had focus unmounted. The next Tab restarted from the top of the page —
   * the user had been thrown out of the component by using it. Opening moves
   * focus to the panel's header (the control that closes it again); closing
   * returns it to the chapter's own card. `preventScroll` matters: focusing
   * normally scrolls the element into view, and scrolling the page while a layout
   * animation is in flight drags the projection out from under it.
   */
  const moveFocus = useRef(false);
  const lastOpened = useRef<string | null>(null);
  const panelHeader = useRef<HTMLButtonElement>(null);
  const controls = useRef(new Map<string, HTMLButtonElement>());

  const registerControl = (id: string) => (node: HTMLButtonElement | null) => {
    if (node) controls.current.set(id, node);
    else controls.current.delete(id);
  };

  useEffect(() => {
    if (!moveFocus.current) return;
    moveFocus.current = false;
    const target = openId ? panelHeader.current : controls.current.get(lastOpened.current ?? '');
    target?.focus({ preventScroll: true });
  }, [openId]);

  const openChapter = CHAPTERS.find((chapter) => chapter.id === openId) ?? null;
  const transition = reduced ? STILL : SPRING;
  const layoutIdFor = (chapter: Chapter) => `${uid}-history-${chapter.id}`;

  const open = (id: string) => {
    moveFocus.current = true;
    lastOpened.current = id;
    setOpenId(id);
  };

  const close = () => {
    moveFocus.current = true;
    setOpenId(null);
  };

  return (
    /* `@container` makes every size decision below ask about the TILE's width
      * instead of the window's. The bento hands this card 343px at a 375px
      * viewport and 354px at 768px — narrower at the larger window — so viewport
      * breakpoints answer the wrong question by construction. */
    <div className="glass @container col-span-1 flex max-h-(--box-min-height) min-h-(--box-min-height) flex-col overflow-hidden rounded-2xl p-4 lg:col-span-3">
      <header className="flex shrink-0 items-baseline justify-between gap-3">
        <h2 className="text-foreground truncate text-base leading-6 font-medium">
          {HISTORY.title}
        </h2>
        {/* The legend is the contract with the reader: one colour is ours, one is
          * not. It is the smallest type on the tile and the most important. */}
        <span className="text-muted-foreground flex shrink-0 items-center gap-2 font-mono text-[8px] tracking-[0.1em] uppercase">
          <span className="flex items-center gap-1">
            <span aria-hidden="true" className="bg-brand size-1.5 rounded-full" />
            {HISTORY.legend.index}
          </span>
          <span className="flex items-center gap-1">
            <span aria-hidden="true" className="bg-muted-foreground size-1.5 rounded-full" />
            {HISTORY.legend.official}
          </span>
        </span>
      </header>

      <p className="text-muted-foreground mt-0.5 shrink-0 text-[11.5px] leading-snug">
        {HISTORY.lede}
      </p>

      <div className="mt-2.5 flex min-h-0 flex-1 flex-col gap-2">
        {/* The strip. It always carries the subject of the record; when a chapter
          * is open it also becomes the dock the other three fly into. */}
        <div className="flex h-7 shrink-0 items-stretch gap-1.5">
          <span className="glass-quiet flex min-w-0 shrink items-center gap-1.5 rounded-lg px-2">
            <Car className="text-brand size-3 shrink-0" strokeWidth={2.25} aria-hidden="true" />
            <span className="text-foreground truncate text-[11px] leading-none font-medium">
              {HISTORY.vehicle.model} · {HISTORY.vehicle.year}
            </span>
            {/* The masked chassis number is how a real vehicle report identifies
              * its subject. It is the first thing dropped when the tabs need the
              * room, and it only appears once the tile is wide enough to seat it
              * without pushing anything off the strip. */}
            {openChapter === null ? (
              <span className="text-muted-foreground/70 hidden shrink-0 font-mono text-[9px] leading-none @min-[490px]:inline">
                {HISTORY.vehicle.vin}
              </span>
            ) : null}
          </span>

          {openChapter === null ? (
            <span className="text-muted-foreground/75 ml-auto flex min-w-0 items-center truncate font-mono text-[8px] tracking-[0.12em] uppercase">
              {HISTORY.handsOff}
            </span>
          ) : (
            <div className="ml-auto flex min-w-0 items-stretch gap-1.5">
              {CHAPTERS.filter((chapter) => chapter.id !== openId).map((chapter) => (
                <ChapterTab
                  key={chapter.id}
                  chapter={chapter}
                  layoutId={layoutIdFor(chapter)}
                  transition={transition}
                  buttonRef={registerControl(chapter.id)}
                  onOpen={open}
                />
              ))}
            </div>
          )}
        </div>

        {/* The body. Two arrangements of the same four elements — never two sets
          * of elements, which is what makes the move a move. */}
        <div className="relative min-h-0 flex-1">
          {openChapter === null ? (
            <div className="grid h-full grid-cols-2 grid-rows-2 gap-2">
              {CHAPTERS.map((chapter) => (
                <ChapterCard
                  key={chapter.id}
                  chapter={chapter}
                  layoutId={layoutIdFor(chapter)}
                  transition={transition}
                  buttonRef={registerControl(chapter.id)}
                  onOpen={open}
                />
              ))}
            </div>
          ) : (
            <ChapterPanel
              chapter={openChapter}
              layoutId={layoutIdFor(openChapter)}
              transition={transition}
              reduced={reduced}
              headerRef={panelHeader}
              onClose={close}
            />
          )}
        </div>
      </div>
    </div>
  );
}
