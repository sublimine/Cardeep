import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, MapPin, Search, SlidersHorizontal } from 'lucide-react';

import { cardeep, type CountedProvince, type ProvinceMeta, type Stats } from '../../../api/cardeep';
import { FreeTextField } from './FreeTextField';
import {
  EMPTY_MAKE_SELECTION,
  MakeModelPicker,
  type MakeSelection,
} from './MakeModelPicker';
import { EMPTY_RANGE, KM_MAX, RangeFields, kmBucketRange, rangeLabel, type Range } from './RangeFields';
import { useParsedQuery } from './useParsedQuery';
import { useResultCount } from './useResultCount';

const EXPO = [0.16, 1, 0.3, 1] as const;

/** Closes a popover on outside click and on Escape. */
function useDismiss(open: boolean, close: () => void) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) close();
    };
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && close();
    document.addEventListener('mousedown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open, close]);
  return ref;
}

const FIELD =
  'flex h-11 w-full items-center gap-2.5 rounded-[11px] border border-white/10 bg-white/5 px-3.5 text-left ' +
  'transition-colors duration-200 hover:border-white/20 hover:bg-white/[0.07] ' +
  'outline-none focus:outline-none focus-visible:border-white/35 focus-visible:ring-2 focus-visible:ring-white/15';

const LABEL = 'text-[10px] font-semibold uppercase tracking-[0.14em] text-white/52';

/**
 * Popover surface — opaque on purpose, so the fields underneath stop reading
 * through it. `up` flips it above the trigger for the last field in the panel,
 * whose sheet would otherwise be cut off by the section's own overflow.
 */
function Sheet({
  children,
  up = false,
  scroll = true,
}: {
  children: React.ReactNode;
  up?: boolean;
  scroll?: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: up ? 6 : -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18, ease: EXPO }}
      /* `scroll` exists because a sheet that scrolls also CLIPS. The year and
       * kilometre sheet holds four dropdowns of its own, and each one is
       * absolutely positioned inside it — so `overflow-y-auto` on the parent cut
       * every one of them off at the sheet's edge. A list of options you cannot
       * see past the third is not a filter. Sheets whose content is a long list
       * still scroll; the one whose content is other popovers must not. */
      className={
        'glass-menu absolute left-0 right-0 z-50 rounded-[13px] p-1.5 ' +
        (scroll ? 'max-h-[19rem] overflow-y-auto ' : '') +
        (up ? 'bottom-[calc(100%+6px)]' : 'top-[calc(100%+6px)]')
      }
    >
      {children}
    </motion.div>
  );
}

function Row({ active, onClick, children }: { active?: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        'flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-[13px] transition-colors duration-150 ' +
        (active ? 'bg-white/12 text-white' : 'text-white/70 hover:bg-white/8 hover:text-white')
      }
    >
      {children}
    </button>
  );
}

/**
 * Provincia — the 52 real provinces, each with the stock it actually holds.
 *
 * Counted from `search_cube`, the same table the button reads, and narrowed by the
 * marque and model already chosen: with BMW selected, Madrid shows how many BMWs
 * are in Madrid, not how many cars are. A province offering a national figure
 * while a marque is in play would be advertising stock the search will not return.
 * Provinces with nothing matching are simply absent — an option that leads to zero
 * results is noise, and the count is what makes that decidable.
 */
function Provincia({
  value,
  onChange,
  make,
  model,
}: {
  value: ProvinceMeta | null;
  onChange: (v: ProvinceMeta | null) => void;
  make?: string;
  model?: string;
}) {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<CountedProvince[]>([]);
  const [query, setQuery] = useState('');
  const ref = useDismiss(open, () => setOpen(false));

  useEffect(() => {
    const c = new AbortController();
    cardeep
      .searchProvinces({ ...(make ? { make } : {}), ...(model ? { model } : {}) }, c.signal)
      .then(setItems)
      .catch(() => {});
    return () => c.abort();
  }, [make, model]);

  const q = query.trim().toLowerCase();
  const list = items.filter((p) => p.name.toLowerCase().includes(q));

  return (
    <div className="relative" ref={ref}>
      <span className={LABEL}>Provincia</span>
      <button type="button" onClick={() => setOpen((o) => !o)} className={FIELD + ' mt-1.5'}>
        <MapPin size={13} className="shrink-0 text-white/35" />
        <span className="min-w-0 flex-1 truncate text-[13.5px] text-white">{value?.name ?? 'Toda España'}</span>
        <ChevronDown
          size={14}
          className={'shrink-0 text-white/40 transition-transform duration-200 ' + (open ? 'rotate-180' : '')}
        />
      </button>

      {open && (
        <Sheet>
          <div className="sticky top-0 mb-1 flex items-center gap-2 rounded-lg bg-white/5 px-2.5 py-2">
            <Search size={12} className="shrink-0 text-white/35" />
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar provincia…"
              className="w-full bg-transparent text-[13px] text-white outline-none placeholder:text-white/30"
            />
          </div>
          <Row
            onClick={() => {
              onChange(null);
              setOpen(false);
            }}
          >
            Toda España
          </Row>
          {list.map((p) => (
            <Row
              key={p.code}
              active={value?.code === p.code}
              onClick={() => {
                onChange(p);
                setOpen(false);
              }}
            >
              <span className="min-w-0 flex-1 truncate">{p.name}</span>
              <span className="shrink-0 text-[11px] tabular-nums text-white/35">
                {p.n.toLocaleString('es-ES')}
              </span>
            </Row>
          ))}
        </Sheet>
      )}
    </div>
  );
}

/* Range, its empty value and its scales now live with the control that owns them
 * (RangeFields). Keeping the shape here while the widget lived elsewhere is how
 * the two drift apart. */

/**
 * Año y kilómetros.
 *
 * The trigger stays; everything behind it was rebuilt. See RangeFields for why
 * the two scrolling year columns and the two-handle track are gone.
 */
function AnoKm({ value, onChange }: { value: Range; onChange: (v: Range) => void }) {
  const [open, setOpen] = useState(false);
  const ref = useDismiss(open, () => setOpen(false));

  const active =
    value.yearMin !== null || value.yearMax !== null || value.kmMin > 0 || value.kmMax < KM_MAX;

  return (
    <div className="relative" ref={ref}>
      <span className={LABEL}>Año y kilómetros</span>
      <button type="button" onClick={() => setOpen((o) => !o)} className={FIELD + ' mt-1.5'}>
        <SlidersHorizontal size={13} className="shrink-0 text-white/35" />
        <span className="min-w-0 flex-1 truncate text-[13.5px] text-white">{rangeLabel(value)}</span>
        {active ? (
          <span
            role="button"
            tabIndex={0}
            aria-label="Quitar filtro"
            onClick={(e) => {
              e.stopPropagation();
              onChange(EMPTY_RANGE);
            }}
            className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-white/15 text-[11px] leading-none text-white/80 transition-colors hover:bg-white/25"
          >
            &times;
          </span>
        ) : (
          <ChevronDown
            size={14}
            className={'shrink-0 text-white/40 transition-transform duration-200 ' + (open ? 'rotate-180' : '')}
          />
        )}
      </button>

      {open && (
        <Sheet up scroll={false}>
          <RangeFields value={value} onChange={onChange} />
        </Sheet>
      )}
    </div>
  );
}
/**
 * The hero's search window — a replica of the panel CARDEX ships on its own
 * landing, adapted to a single-country index (its country selector becomes the
 * 52 real Spanish provinces) and to Cardeep's accent.
 *
 * The glass values are CARDEX's, kept rather than re-tuned: `glass-panel`
 * carries the blur/saturate pair, the gradient fill and the inset top highlight.
 *
 * The button states the exact number of cars the current filters match, and it
 * updates as they change. It used to quote the national total when nothing was
 * chosen and fall back to "Buscar en el índice" the moment anything was — because
 * no endpoint could answer the filtered question in a usable time. `/search/count`
 * now answers it in 43-60 ms against `search_cube`, exactly rather than estimated,
 * so the promise on the button and the result behind it are the same number.
 *
 * Free text is the one filter the counter cannot include: it is resolved by the
 * search layer, not by the cube. When there is a query, the button stops quoting a
 * figure rather than quoting one it knows is wrong.
 */
export function SearchPanel({ stats }: { stats: Stats | null }) {
  const [query, setQuery] = useState('');
  const [mm, setMm] = useState<MakeSelection>(EMPTY_MAKE_SELECTION);
  const [prov, setProv] = useState<ProvinceMeta | null>(null);
  const [range, setRange] = useState<Range>(EMPTY_RANGE);

  const hasQuery = query.trim().length > 0;
  const km = kmBucketRange(range);
  const { parsed } = useParsedQuery(query);

  /* The sentence and the fields feed ONE set of filters.
   *
   * A written query does not replace the controls and the controls do not ignore
   * the query — whichever is more specific wins per dimension, with the explicit
   * click taking precedence, because a control the user physically set is a
   * stronger statement of intent than a word in a sentence. The result is that
   * typing "BMW Serie 3 diésel por menos de 15.000 €" moves the counter, instead
   * of the counter ignoring everything the visitor just wrote. */
  const { data: count, pending } = useResultCount({
    ...(parsed?.make ? { make: parsed.make } : {}),
    ...(parsed?.model ? { model: parsed.model } : {}),
    ...(parsed?.submodel ? { submodel: parsed.submodel } : {}),
    ...(parsed?.color ? { color: parsed.color } : {}),
    ...(parsed?.body_type ? { body_type: parsed.body_type } : {}),
    ...(parsed?.is_family ? { is_family: true } : {}),
    /* Every one of these is a chip the panel draws. Leaving them out of the count
     * while drawing them was the bug that made the button read 256.825 under a
     * chip meaning 2.226 — a hundred and fifteen times the truth. The rule now has
     * no exception: if it is shown, it is counted. */
    ...(parsed?.fuel ? { fuel: parsed.fuel } : {}),
    ...(parsed?.seats_min ? { seats_min: parsed.seats_min } : {}),
    ...(parsed?.price_min ? { price_min: parsed.price_min } : {}),
    ...(parsed?.price_max ? { price_max: parsed.price_max } : {}),
    ...(parsed?.province_code ? { province: parsed.province_code } : {}),
    ...(parsed?.year_min ? { year_min: parsed.year_min } : {}),
    ...(parsed?.year_max ? { year_max: parsed.year_max } : {}),
    ...(mm.make ? { make: mm.make.make } : {}),
    ...(mm.model ? { model: mm.model } : {}),
    ...(mm.submodel ? { submodel: mm.submodel } : {}),
    ...(prov ? { province: prov.code } : {}),
    ...(range.yearMin !== null ? { year_min: range.yearMin } : {}),
    ...(range.yearMax !== null ? { year_max: range.yearMax } : {}),
    ...(km.min !== null ? { km_min_bucket: km.min } : {}),
    ...(km.max !== null ? { km_max_bucket: km.max } : {}),
  });

  /* What the sentence was understood to mean, in the order a person would say it.
   * Rendered as chips under the field so the visitor can SEE the interpretation
   * and correct it, rather than trusting a black box. */
  const chips: string[] = parsed
    ? [
        parsed.make && !mm.make ? [parsed.make, parsed.model, parsed.submodel].filter(Boolean).join(' ') : null,
        parsed.color ?? null,
        parsed.seats_min ? `${parsed.seats_min} plazas` : null,
        parsed.is_family && !parsed.seats_min ? 'para familia' : null,
        parsed.body_type ?? null,
        parsed.fuel ?? null,
        /* Deliberately NOT a chip. `transmission` is unpublished on 51% of the
         * index and is not a cube dimension, so a chip for it would promise a
         * filter the counter cannot apply — the exact class of lie the rest of
         * this list was just fixed to stop telling. It stays in the parse output
         * (the marketplace can use it) and off the panel. */
        parsed.province_name && !prov ? parsed.province_name : null,
        parsed.price_max ? `hasta ${parsed.price_max.toLocaleString('es-ES')} €` : null,
        parsed.km_max ? `hasta ${parsed.km_max.toLocaleString('es-ES')} km` : null,
        parsed.year_min ? `desde ${parsed.year_min}` : null,
      ].filter((v): v is string => Boolean(v))
    : [];

  const go = (freeText: string) => {
    const p = new URLSearchParams();
    if (freeText.trim()) p.set('q', freeText.trim());
    if (mm.make) p.set('make', mm.make.make);
    if (mm.model) p.set('model', mm.model);
    if (mm.submodel) p.set('submodel', mm.submodel);
    if (prov) p.set('province', prov.code);
    if (range.yearMin) p.set('year_min', String(range.yearMin));
    if (range.yearMax) p.set('year_max', String(range.yearMax));
    if (range.kmMin > 0) p.set('km_min', String(range.kmMin));
    if (range.kmMax < KM_MAX) p.set('km_max', String(range.kmMax));
    window.location.href = `/marketplace${p.toString() ? `?${p}` : ''}`;
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    go(query);
  };

  return (
    <motion.form
      onSubmit={submit}
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: EXPO, delay: 0.3 }}
      className="glass-panel w-[clamp(318px,26vw,364px)] shrink-0 rounded-[22px] p-[18px_18px_16px]"
    >
      <div className="mb-3 text-[10px] font-semibold uppercase tracking-[0.16em] text-white/55">
        Busca en toda España
      </div>

      <FreeTextField value={query} onChange={setQuery} onRunExample={go} />

      {(chips.length > 0 || (parsed?.unresolved?.length ?? 0) > 0) && (
        <div className="mt-2 flex flex-wrap items-center gap-1.5">
          {chips.map((c) => (
            <span
              key={c}
              className="rounded-full border border-brand/30 bg-brand/12 px-2 py-[3px] text-[10.5px] font-medium text-white/85"
            >
              {c}
            </span>
          ))}
          {/* Said out loud, never swallowed. A word we could not place would
              otherwise widen the search into results nobody asked for. */}
          {parsed?.unresolved?.length ? (
            <span className="text-[10.5px] text-white/35">
              sin entender: {parsed.unresolved.join(', ')}
            </span>
          ) : null}
        </div>
      )}

      {/* The fields assemble one after another instead of appearing as a block —
          the panel reads as being built, which is what it does. */}
      <div className="mt-3 space-y-3">
        {[
          <MakeModelPicker key="mm" value={mm} onChange={setMm} />,
          <Provincia key="prov" value={prov} onChange={setProv} make={mm.make?.make} model={mm.model ?? undefined} />,
          <AnoKm key="ano" value={range} onChange={setRange} />,
        ].map((field, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, ease: EXPO, delay: 0.42 + i * 0.09 }}
          >
            {field}
          </motion.div>
        ))}
      </div>

      <motion.button
        type="submit"
        whileHover={{ scale: 1.02, y: -2 }}
        whileTap={{ scale: 0.98, y: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        className="bg-brand-fill mt-4 w-full rounded-[11px] py-3.5 text-[14px] font-semibold tracking-[-0.01em] text-white shadow-[0_12px_32px_-10px_rgb(18_110_253/0.75)]"
      >
        {/* Never blanked while refetching — the previous honest number stays and
            simply dims. A counter that flashes empty on every change destroys the
            expectation it exists to set. */}
        <span className={pending ? 'opacity-70 transition-opacity duration-200' : ''}>
          {!count
            ? 'Buscar en el índice'
            : count.count === 0
              ? 'Sin resultados · prueba a quitar un filtro'
              : `Ver ${count.count.toLocaleString('es-ES')} coches`}
        </span>
      </motion.button>

      {/* Two disclosures, both of which most products would leave out.
          The mileage one is the honest half of a filter: a car whose kilometres
          the source never published cannot be shown as matching a kilometre
          bound, and saying how many were set aside is the difference between a
          filter and a quiet omission. */}
      {count && count.unknown_km_excluded > 0 && (
        <p className="mt-2.5 text-center text-[10.5px] leading-snug text-white/40">
          {count.unknown_km_excluded.toLocaleString('es-ES')} anuncios sin kilómetros publicados
          quedan fuera de este filtro
        </p>
      )}
      {count && count.unknown_color_excluded > 0 && (
        <p className="mt-2 text-center text-[10.5px] leading-snug text-white/40">
          {count.unknown_color_excluded.toLocaleString('es-ES')} coches más podrían valer: nadie
          publicó su color
        </p>
      )}
    </motion.form>
  );
}
