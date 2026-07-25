import { useMemo, useRef, useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { ArrowRight, MapPin, Search } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { Glass } from '@/components/ui/glass';
import { Logo } from '@/components/ui/logo';
import { BRAND, FIGURES, HERO } from '@/content/site';
import { MARK_CELL, MARK_COLS, VEHICLE_MARKS } from '@/content/vehicle-marks';

/** Provinces offered as quick filters; the index covers all fifty-two. */
const PROVINCES = ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Málaga', 'Murcia'] as const;

const SPRITE = '/brand/marks.webp';

function MarkGlyph({ col, row, className }: { col: number; row: number; className?: string }) {
  return (
    <span
      aria-hidden
      className={className}
      style={{
        display: 'block',
        width: MARK_CELL.width,
        height: MARK_CELL.height,
        backgroundColor: 'currentColor',
        WebkitMaskImage: `url(${SPRITE})`,
        maskImage: `url(${SPRITE})`,
        WebkitMaskRepeat: 'no-repeat',
        maskRepeat: 'no-repeat',
        WebkitMaskSize: `${MARK_COLS * MARK_CELL.width}px auto`,
        maskSize: `${MARK_COLS * MARK_CELL.width}px auto`,
        WebkitMaskPosition: `-${col * MARK_CELL.width}px -${row * MARK_CELL.height}px`,
        maskPosition: `-${col * MARK_CELL.width}px -${row * MARK_CELL.height}px`,
      }}
    />
  );
}

/**
 * The search card, modelled on the terminal's own universe search: type a
 * marque and the index answers immediately. It runs against the real 135-brand
 * catalogue, so it is a working control rather than a picture of one.
 */
function SearchCard() {
  const [query, setQuery] = useState('');
  const [province, setProvince] = useState<string>('Madrid');
  const inputRef = useRef<HTMLInputElement>(null);

  const matches = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return VEHICLE_MARKS.slice(0, 5);
    return VEHICLE_MARKS.filter((mark) => mark.name.toLowerCase().includes(needle)).slice(0, 5);
  }, [query]);

  return (
    <Glass radius={22} elevated interactive className="w-full max-w-xl">
      <div className="flex flex-col gap-4 p-4 sm:p-5">
        <label
          className="flex items-center gap-3 rounded-2xl px-4 py-3"
          style={{ background: 'var(--cd-glass-panel)', border: '1px solid var(--cd-glass-border)' }}
        >
          <Search className="text-primary size-4 shrink-0" strokeWidth={2.2} />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Busca una marca, un modelo o un punto de venta"
            aria-label="Buscar en el índice"
            className="text-foreground placeholder:text-subtle -tracking-xs w-full bg-transparent text-sm outline-none"
          />
          <kbd className="text-subtle font-dm-mono hidden shrink-0 rounded-md px-1.5 py-0.5 text-[10px] sm:block"
            style={{ border: '1px solid var(--cd-glass-border)' }}>
            /
          </kbd>
        </label>

        <div className="flex flex-wrap items-center gap-1.5">
          <MapPin className="text-subtle mr-0.5 size-3.5" strokeWidth={2.2} />
          {PROVINCES.map((name) => (
            <button
              key={name}
              type="button"
              onClick={() => setProvince(name)}
              aria-pressed={province === name}
              className={
                province === name
                  ? 'bg-primary text-on-primary -tracking-xs cursor-pointer rounded-full px-2.5 py-1 text-[11px] font-medium'
                  : 'glass-chip text-muted-foreground hover:text-foreground -tracking-xs cursor-pointer rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors'
              }
            >
              {name}
            </button>
          ))}
        </div>

        <div className="flex flex-col gap-1">
          {matches.length === 0 ? (
            <p className="text-subtle -tracking-xs px-2 py-6 text-center text-xs">
              Ninguna marca coincide. En el índice hay {VEHICLE_MARKS.length}.
            </p>
          ) : (
            matches.map((mark) => (
              <button
                key={mark.slug}
                type="button"
                onClick={() => {
                  setQuery(mark.name);
                  inputRef.current?.focus();
                }}
                className="group flex cursor-pointer items-center gap-3 rounded-xl px-2.5 py-2 text-left transition-colors duration-200 hover:bg-[color:var(--cd-glass-panel)]"
              >
                <span className="text-muted-foreground group-hover:text-foreground grid w-16 shrink-0 place-items-center transition-colors">
                  <MarkGlyph col={mark.col} row={mark.row} className="scale-[0.62] opacity-80" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="text-foreground -tracking-xs block truncate text-[13px] font-medium">
                    {mark.name}
                  </span>
                  <span className="text-subtle block truncate text-[11px]">
                    {province} · puntos de venta con stock
                  </span>
                </span>
                <ArrowRight className="text-subtle group-hover:text-primary size-3.5 shrink-0 transition-colors" />
              </button>
            ))
          )}
        </div>

        <div
          className="flex items-center justify-between pt-1 text-[11px]"
          style={{ borderTop: '1px solid var(--cd-glass-border)' }}
        >
          <span className="text-subtle font-dm-mono -tracking-xs pt-2.5">
            {VEHICLE_MARKS.length} marcas · 52 provincias
          </span>
          <span className="text-subtle font-dm-mono -tracking-xs pt-2.5">{BRAND.indexStamp}</span>
        </div>
      </div>
    </Glass>
  );
}

export function Hero() {
  const reduced = useReducedMotion();

  return (
    <div id="indice" className="w-full p-2">
      <div className="relative isolate flex min-h-[42rem] w-full flex-col overflow-hidden rounded-3xl md:min-h-[46rem]">
        {/* Backdrop: a market at dusk, every light a point of sale. */}
        <img
          src="/hero/skyline.webp"
          alt=""
          aria-hidden
          className="absolute inset-0 -z-20 size-full object-cover"
          style={{ backgroundImage: 'url(/hero/skyline-tiny.webp)', backgroundSize: 'cover' }}
        />
        {/* Scrim: keeps the plate legible under type in either theme and pulls it
            toward the brand's cobalt instead of the photo's warm horizon. */}
        <div
          aria-hidden
          className="absolute inset-0 -z-10"
          style={{
            background:
              'linear-gradient(180deg, rgb(7 11 20 / 0.82) 0%, rgb(7 11 20 / 0.62) 38%, rgb(7 11 20 / 0.88) 100%), radial-gradient(90% 70% at 18% 10%, rgb(59 130 246 / 0.28), transparent 60%)',
          }}
        />

        <Container className="relative z-10 flex flex-1 flex-col justify-center gap-10 py-20 lg:flex-row lg:items-center lg:justify-between lg:gap-16">
          <motion.div
            className="flex max-w-xl flex-col items-start"
            initial={reduced ? false : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: 'easeOut' }}
          >
            <span className="glass-chip inline-flex items-center gap-2 rounded-full py-1 pr-3 pl-1.5 text-white">
              <Logo className="size-5 text-white" />
              <span className="-tracking-xs text-[11px] font-medium">{HERO.badgeNote}</span>
            </span>

            <h1 className="-tracking-xl mt-6 text-4xl font-semibold text-balance text-white sm:text-5xl lg:text-6xl">
              {HERO.title}
            </h1>

            <p className="-tracking-xs mt-5 max-w-lg text-base leading-6 text-white/72">
              {HERO.subtitle}
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Button avatar="/brand/cardeep-mark.png">{HERO.cta}</Button>
              <a
                href="#producto"
                className="glass-chip -tracking-xs inline-flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium text-white transition-transform duration-200 hover:-translate-y-0.5"
              >
                Ver qué hay dentro
                <ArrowRight className="size-3.5" />
              </a>
            </div>

            <dl className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-4">
              {[FIGURES.dealers, FIGURES.vehicles, FIGURES.provinces].map((figure) => (
                <div key={figure.label} className="flex flex-col">
                  <dt className="-tracking-lg text-2xl font-semibold text-white">
                    {'prefix' in figure ? figure.prefix : ''}
                    {figure.value}
                    {'suffix' in figure ? figure.suffix : ''}
                  </dt>
                  <dd className="-tracking-xs text-[11px] text-white/55">{figure.label}</dd>
                </div>
              ))}
            </dl>
          </motion.div>

          <motion.div
            className="w-full lg:max-w-xl"
            initial={reduced ? false : { opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.75, delay: 0.12, ease: 'easeOut' }}
          >
            <SearchCard />
          </motion.div>
        </Container>
      </div>
    </div>
  );
}
