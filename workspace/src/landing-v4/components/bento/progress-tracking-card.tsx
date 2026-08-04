import { useEffect, useRef } from 'react';
import {
  Activity,
  AlertTriangle,
  Check,
  Clock,
  MapPin,
  Plus,
  Target,
  TrendingDown,
  type LucideIcon,
} from 'lucide-react';

import { BENTO } from '@landing/content/site';
import { AnimatedList } from '@landing/components/ui/animated-list';
import { cn } from '@landing/lib/utils';

/* -------------------------------------------------------------------------- */
/*                              Decorative dots                               */
/* -------------------------------------------------------------------------- */

/** Grid pitch and dot edge, in CSS px, measured off the reference render. */
const DOT_PITCH = 8;
const DOT_SIZE = 4;
/**
 * Per-dot alpha range; the wrapper's `opacity-10` plus the masks do the rest.
 * The noise is squared before it is mapped onto the range because the reference
 * texture has far more near-invisible dots than a flat distribution produces —
 * squaring matches its measured mean darkness while keeping the same darkest dot.
 */
const DOT_MIN_ALPHA = 0.12;
const DOT_MAX_ALPHA = 0.8;

/** Deterministic value in [0, 1) per cell, so the texture never reshuffles. */
function cellNoise(col: number, row: number) {
  const seeded = Math.sin(col * 127.1 + row * 311.7) * 43758.5453;
  return seeded - Math.floor(seeded);
}

/**
 * Dot texture bleeding off the card's top-right corner.
 *
 * The reference never sizes its canvas, so the element keeps the 300x150
 * default backing store and maps 1:1 to CSS pixels — sizing it here would
 * change the dot pitch, so the attributes are deliberately left off.
 */
function DotGrid() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let row = 0; row * DOT_PITCH < canvas.height; row++) {
      for (let col = 0; col * DOT_PITCH < canvas.width; col++) {
        const noise = cellNoise(col, row);
        const alpha =
          DOT_MIN_ALPHA + noise * noise * (DOT_MAX_ALPHA - DOT_MIN_ALPHA);
        ctx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
        ctx.fillRect(col * DOT_PITCH, row * DOT_PITCH, DOT_SIZE, DOT_SIZE);
      }
    }
  }, []);

  return (
    <div className="absolute top-0 -right-20 size-40 w-full mask-b-from-10% mask-radial-[100%_100%] mask-radial-from-25% mask-radial-at-right opacity-10">
      <div className="pointer-events-none select-none absolute">
        <canvas ref={canvasRef} className="block h-full w-full" />
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Feed                                    */
/* -------------------------------------------------------------------------- */

type Movement = (typeof BENTO.movements.items)[number];
type Tone = Movement['tone'];

/**
 * One glyph per alert kind. The icon is the only thing the reader parses before
 * the text, so it carries the CATEGORY, never the sentiment — sentiment is the
 * tone's job, and encoding both in one mark makes neither legible.
 */
const GLYPHS: Record<Movement['kind'], LucideIcon> = {
  competencia: TrendingDown,
  arbitraje: MapPin,
  'tu stock': AlertTriangle,
  rotación: Clock,
  vendido: Check,
  mercado: Activity,
  oportunidad: Target,
  'stock nuevo': Plus,
};

/**
 * Tone is money, not decoration: `warn` is money leaving the business, `good` is
 * money arriving, `brand` is information that is neither. Three roles, one accent
 * plus the two semantic hues the theme already defines — nothing here introduces
 * a colour the design system does not own.
 */
const TONES: Record<Tone, string> = {
  warn: 'bg-dusty-red/12 text-[#b3403a]',
  good: 'bg-dusty-green/12 text-dusty-green',
  brand: 'bg-brand/10 text-brand',
};

function MovementRow({ item }: { item: Movement }) {
  const Glyph = GLYPHS[item.kind];

  return (
    <figure className="glass-quiet mb-2 flex w-full items-start gap-2.5 rounded-xl p-2.5">
      <span
        className={cn(
          'mt-px flex size-7 shrink-0 items-center justify-center rounded-lg',
          TONES[item.tone],
        )}
      >
        <Glyph className="size-3.5" strokeWidth={2.25} aria-hidden="true" />
      </span>
      <div className="min-w-0 flex-1">
        <figcaption className="flex items-baseline justify-between gap-2">
          <span className="font-mono text-[10px] uppercase tracking-[0.1em] text-neutral-500">
            {item.kind}
          </span>
          <span className="shrink-0 text-[10px] text-neutral-400">
            {item.time}
          </span>
        </figcaption>
        <p className="mt-0.5 text-[13px] leading-[1.35] font-medium text-black">
          {item.text}
        </p>
        <p className="mt-0.5 text-[11.5px] leading-[1.35] text-neutral-500">
          {item.meta}
        </p>
      </div>
    </figure>
  );
}

/* -------------------------------------------------------------------------- */
/*                                    Card                                    */
/* -------------------------------------------------------------------------- */

/**
 * The reference heading is a two-line block and the layout below it depends on
 * that height, so the title breaks before its last word rather than wrapping.
 */
const TITLE_BREAK = BENTO.movements.title.lastIndexOf(' ');
const TITLE_HEAD = BENTO.movements.title.slice(0, TITLE_BREAK);
const TITLE_TAIL = BENTO.movements.title.slice(TITLE_BREAK + 1);

/**
 * What this card used to be: a donut gauge with a sweeping needle beside a stack
 * of three cards that promoted on a timer. The gauge measured nothing — it was a
 * dial with no quantity behind it — and three rotating strings cannot carry the
 * claim the section makes. A feed can, because a feed is what the product is:
 * the market moving, and Cardeep telling you which movements are yours.
 */
export function ProgressTrackingCard() {
  return (
    <div className="glass relative col-span-1 flex min-h-(--box-min-height) flex-col overflow-hidden rounded-2xl p-4 lg:col-span-2">
      <DotGrid />
      <h2 className="relative text-base font-medium text-black">
        {TITLE_HEAD}
        <br />
        {TITLE_TAIL}
      </h2>
      {/* The feed runs to the card's bottom edge and is faded out there rather
        * than clipped, so the newest row reads as the top of something ongoing
        * instead of the whole of something short. */}
      <div className="relative mt-3 min-h-0 flex-1 mask-b-from-72%">
        <AnimatedList visibleCount={3} delay={2800}>
          {BENTO.movements.items.map((item) => (
            <MovementRow key={item.kind} item={item} />
          ))}
        </AnimatedList>
      </div>
    </div>
  );
}
