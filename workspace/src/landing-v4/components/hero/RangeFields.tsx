import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, ChevronDown } from 'lucide-react';

const EXPO = [0.16, 1, 0.3, 1] as const;
const THIS_YEAR = new Date().getFullYear();

export const KM_MAX = 250_000;

export interface Range {
  yearMin: number | null;
  yearMax: number | null;
  kmMin: number;
  kmMax: number;
}

export const EMPTY_RANGE: Range = { yearMin: null, yearMax: null, kmMin: 0, kmMax: KM_MAX };

/**
 * Non-linear scales, because a linear one lies about where the market is.
 *
 * Nobody shops in even 25.000 km increments across the whole range: the interesting
 * decisions are all bunched at the bottom (is it under 50.000? under 100.000?) and
 * essentially absent at the top, where "a lot" is the only distinction that matters.
 * Both incumbents measured — mobile.de and coches.net — space their options this way
 * for exactly that reason, and it is why a two-handle slider is the wrong control
 * here: a slider gives equal travel to every 10.000 km, so the range people actually
 * care about occupies a fifth of the track and lands imprecisely.
 *
 * The year scale is the same argument: one-year steps while the year still
 * identifies a generation, then five-year steps once it only identifies an era.
 */
const KM_STEPS = [
  0, 5_000, 10_000, 20_000, 30_000, 40_000, 50_000, 60_000, 70_000, 80_000, 90_000,
  100_000, 125_000, 150_000, 175_000, 200_000, KM_MAX,
];

const YEAR_STEPS = [
  ...Array.from({ length: 21 }, (_, i) => THIS_YEAR - i),
  2004, 1999, 1994, 1989,
];

/**
 * Always grouped, even at four digits.
 *
 * `toLocaleString('es-ES')` renders 5000 as "5000" and 10000 as "10.000", which is
 * correct Spanish — the RAE does not group four-digit numbers — and looks like a
 * bug in a column where the two sit one above the other. Typographic consistency
 * wins inside an aligned list of figures; prose elsewhere still uses the locale.
 */
const fmt = (n: number) => n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');

interface Option {
  value: number | null;
  label: string;
}

/**
 * One bound of a range.
 *
 * A listbox rather than a native `<select>`: the native control paints its popup
 * with the operating system's chrome, which on a dark glass panel means a white
 * rectangle in the middle of the design. That is precisely the "looks like plain
 * HTML" failure this field is being rebuilt to fix.
 */
function BoundSelect({
  label,
  value,
  options,
  onChange,
  custom,
}: {
  label: string;
  value: number | null;
  options: Option[];
  onChange: (v: number | null) => void;
  /** Enables the "type an exact figure" row. Kilometres only — a registration
   *  year is chosen from a known set and typing one is how you get 3025. */
  custom?: { placeholder: string; max: number };
}) {
  const [open, setOpen] = useState(false);
  const [typed, setTyped] = useState('');
  const current = options.find((o) => o.value === value) ?? options[0];

  const commitTyped = () => {
    const n = Number(typed.replace(/[^\d]/g, ''));
    if (!custom || !Number.isFinite(n) || n <= 0) return;
    // Snapped to the cube's grain and then DISPLAYED snapped, so the figure on
    // screen is always the figure that was counted.
    onChange(Math.min(snapKm(n), custom.max));
    setTyped('');
    setOpen(false);
  };

  return (
    <div className="relative min-w-0 flex-1">
      <span className="mb-1.5 block text-[9.5px] font-semibold uppercase tracking-[0.14em] text-white/40">
        {label}
      </span>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={
          'flex h-9 w-full items-center justify-between gap-1.5 rounded-[9px] border px-2.5 text-left ' +
          'text-[12.5px] tabular-nums transition-colors duration-200 ' +
          (value !== null
            ? 'border-white/25 bg-white/[0.10] text-white'
            : 'border-white/10 bg-white/5 text-white/60 hover:border-white/20')
        }
      >
        <span className="truncate">{current.label}</span>
        <ChevronDown
          size={13}
          className={'shrink-0 text-white/35 transition-transform duration-200 ' + (open ? 'rotate-180' : '')}
        />
      </button>

      {open && (
        <>
          {/* Click-away without a document listener: a transparent sheet under the
              list. Cheaper than binding and unbinding a global handler, and it
              cannot leak if the component unmounts while open. */}
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <motion.ul
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.16, ease: EXPO }}
            className="glass-menu absolute left-0 right-0 z-50 mt-1.5 max-h-52 overflow-y-auto rounded-[11px] p-1"
          >
            {/* The scale covers the decisions people actually make; this covers
             *  the one they occasionally need and a fixed list can never hold —
             *  "under 87.000, because that is what mine has". */}
            {custom && (
              <div className="sticky top-0 z-10 mb-1 flex items-center gap-1.5 rounded-md bg-white/[0.09] px-2 py-1.5 backdrop-blur">
                <input
                  inputMode="numeric"
                  value={typed}
                  onChange={(e) => setTyped(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      commitTyped();
                    }
                  }}
                  placeholder={custom.placeholder}
                  className="w-full bg-transparent text-[12.5px] tabular-nums text-white outline-none placeholder:text-white/30"
                />
                {typed && (
                  <button
                    type="button"
                    onClick={commitTyped}
                    className="shrink-0 rounded px-1.5 py-0.5 text-[10.5px] font-semibold text-brand hover:bg-white/10"
                  >
                    OK
                  </button>
                )}
              </div>
            )}
            {options.map((o) => (
              <li key={String(o.value)}>
                <button
                  type="button"
                  onClick={() => {
                    onChange(o.value);
                    setOpen(false);
                  }}
                  className={
                    'flex w-full items-center justify-between rounded-md px-2 py-1.5 text-left text-[12.5px] tabular-nums ' +
                    'transition-colors duration-150 ' +
                    (o.value === value ? 'bg-white/12 text-white' : 'text-white/70 hover:bg-white/8 hover:text-white')
                  }
                >
                  {o.label}
                  {o.value === value && <Check size={12} className="shrink-0" />}
                </button>
              </li>
            ))}
          </motion.ul>
        </>
      )}
    </div>
  );
}

/**
 * Año y kilómetros.
 *
 * What this replaces: two scrolling columns of every year since 1990 and a
 * two-handle drag track, both painted on a near-black sheet. Three separate
 * problems — a scroll list is the least precise way to pick from a known set, a
 * drag track cannot express "under 100.000" without hunting for it, and the sheet
 * inverted the panel's own elevation. The list is now bounded and non-linear, the
 * bounds are stated rather than dragged to, and the sheet sits on the elevation
 * ladder like every other surface.
 *
 * The two bounds filter each other: "desde" can never offer a value above the
 * chosen "hasta", so an impossible range cannot be expressed in the first place.
 * Validating after the fact would mean showing an error for something the control
 * should simply not have allowed.
 */
export function RangeFields({ value, onChange }: { value: Range; onChange: (v: Range) => void }) {
  const yearFrom: Option[] = [
    { value: null, label: 'Cualquiera' },
    ...YEAR_STEPS.filter((y) => value.yearMax === null || y <= value.yearMax).map((y) => ({
      value: y,
      label: String(y),
    })),
  ];
  const yearTo: Option[] = [
    { value: null, label: 'Cualquiera' },
    ...YEAR_STEPS.filter((y) => value.yearMin === null || y >= value.yearMin).map((y) => ({
      value: y,
      label: String(y),
    })),
  ];
  const kmFrom: Option[] = KM_STEPS.filter((k) => k < value.kmMax).map((k) => ({
    value: k,
    label: k === 0 ? 'Sin mínimo' : `${fmt(k)} km`,
  }));
  const kmTo: Option[] = KM_STEPS.filter((k) => k > value.kmMin).map((k) => ({
    value: k,
    label: k >= KM_MAX ? `${fmt(KM_MAX)}+ km` : `${fmt(k)} km`,
  }));

  return (
    <div className="p-1">
      <div className="flex gap-2.5">
        <BoundSelect
          label="Año desde"
          value={value.yearMin}
          options={yearFrom}
          onChange={(y) => onChange({ ...value, yearMin: y })}
        />
        <BoundSelect
          label="Año hasta"
          value={value.yearMax}
          options={yearTo}
          onChange={(y) => onChange({ ...value, yearMax: y })}
        />
      </div>

      <div className="my-3 h-px bg-white/10" />

      <div className="flex gap-2.5">
        <BoundSelect
          label="Km desde"
          value={value.kmMin}
          options={kmFrom}
          onChange={(k) => onChange({ ...value, kmMin: k ?? 0 })}
          custom={{ placeholder: 'Escribe los km…', max: KM_MAX }}
        />
        <BoundSelect
          label="Km hasta"
          value={value.kmMax}
          options={kmTo}
          onChange={(k) => onChange({ ...value, kmMax: k ?? KM_MAX })}
          custom={{ placeholder: 'Escribe los km…', max: KM_MAX }}
        />
      </div>
    </div>
  );
}

/** The cube's kilometre grain. Mirrors `km_bucket_of()` (migration 0102). */
export const KM_GRAIN = 5_000;

/** Any figure the user types is pulled onto the grain, so what the field displays
 *  is always what the counter counted. Silent rounding is the thing this avoids. */
export const snapKm = (km: number) => Math.round(km / KM_GRAIN) * KM_GRAIN;

/**
 * The kilometre filter, expressed in the cube's own bucket indices.
 *
 * `search_cube` stores counts per kilometre bucket at a uniform 5.000 km
 * (migration 0102). This is the other half of `km_bucket_of()`, and a silent
 * disagreement between the two would produce confidently wrong numbers — so the
 * arithmetic here is deliberately the same shape as the SQL.
 *
 * The display scale (KM_STEPS) stays non-linear because that is how people
 * choose; the STORAGE grain is uniform because that is what makes an arbitrary
 * typed figure countable. Separating the two is what allows both.
 *
 * Bucket i covers [i×5.000, (i+1)×5.000). "Desde X" is the bucket X starts in;
 * "hasta Y" is the bucket below Y, so the bound reads as "under Y" exactly.
 */
export function kmBucketRange(value: Range): { min: number | null; max: number | null } {
  return {
    min: value.kmMin > 0 ? Math.floor(snapKm(value.kmMin) / KM_GRAIN) : null,
    max: value.kmMax < KM_MAX ? Math.max(0, Math.floor(snapKm(value.kmMax) / KM_GRAIN) - 1) : null,
  };
}

/** The trigger's summary line. Kept next to the control it describes so the two
 *  can never drift apart. */
export function rangeLabel(value: Range): string {
  const yearActive = value.yearMin !== null || value.yearMax !== null;
  const kmActive = value.kmMin > 0 || value.kmMax < KM_MAX;

  const year = !yearActive
    ? null
    : value.yearMin !== null && value.yearMax !== null
      ? `${value.yearMin}–${value.yearMax}`
      : value.yearMin !== null
        ? `desde ${value.yearMin}`
        : `hasta ${value.yearMax}`;

  const kmHi = value.kmMax >= KM_MAX ? `${fmt(KM_MAX)}+` : fmt(value.kmMax);
  const km = !kmActive ? null : value.kmMin > 0 ? `${fmt(value.kmMin)}–${kmHi} km` : `hasta ${kmHi} km`;

  return [year, km].filter(Boolean).join('  ·  ') || 'Sin límite';
}
