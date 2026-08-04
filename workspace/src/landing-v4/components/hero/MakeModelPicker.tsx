import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronLeft, Search } from 'lucide-react';

import { cardeep, type CensusMake } from '../../../api/cardeep';
import { BrandMark } from './BrandMark';

const EXPO = [0.16, 1, 0.3, 1] as const;

export interface MakeSelection {
  make: CensusMake | null;
  model: string | null;
  submodel: string | null;
}

export const EMPTY_MAKE_SELECTION: MakeSelection = { make: null, model: null, submodel: null };

interface Counted {
  label: string;
  n: number;
}

const fmt = (n: number) => n.toLocaleString('es-ES');

function Row({
  active,
  onClick,
  children,
  count,
}: {
  active?: boolean;
  onClick: () => void;
  children: React.ReactNode;
  count?: number;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        'flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-[13px] transition-colors duration-150 ' +
        (active ? 'bg-white/12 text-white' : 'text-white/70 hover:bg-white/[0.09] hover:text-white')
      }
    >
      {children}
      {count !== undefined && (
        <span className="ml-auto shrink-0 text-[11px] tabular-nums text-white/35">{fmt(count)}</span>
      )}
    </button>
  );
}

/** The one-line "you are here" strip at the top of levels 2 and 3. */
function Crumb({ label, onBack }: { label: string; onBack: () => void }) {
  return (
    <button
      type="button"
      onClick={onBack}
      className="mb-1 flex w-full items-center gap-1.5 rounded-lg px-2 py-1.5 text-left text-[11.5px] font-medium text-white/50 transition-colors duration-150 hover:bg-white/[0.07] hover:text-white/80"
    >
      <ChevronLeft size={13} className="shrink-0" />
      {label}
    </button>
  );
}

/**
 * Marca → Modelo → Versión.
 *
 * A drill, not three separate fields. Clicking Mercedes-Benz opens its models;
 * clicking Clase C opens the versions filed under it — C 220 d, C 200 d Estate,
 * Coupé C 220 d — with the whole model offered first, so choosing "all of Clase C"
 * costs one click and is never buried under the specific versions. Two very
 * different buyers arrive at this control: one knows the exact car, one knows the
 * shape of it, and a picker that only serves the second makes the first scroll.
 *
 * Everything on screen is counted, and counted from `search_cube` — the same table
 * the submit button reads. Before that they came from different sources and
 * disagreed by twenty thousand cars on Mercedes-Benz alone.
 *
 * Versions exist for 44.3% of the census. A model with none simply shows none; the
 * roll-up is always there, so the control never dead-ends.
 */
export function MakeModelPicker({
  value,
  onChange,
}: {
  value: MakeSelection;
  onChange: (v: MakeSelection) => void;
}) {
  const [open, setOpen] = useState(false);
  const [makes, setMakes] = useState<CensusMake[] | null>(null);
  const [models, setModels] = useState<Counted[] | null>(null);
  const [subs, setSubs] = useState<Counted[] | null>(null);
  const [query, setQuery] = useState('');

  useEffect(() => {
    if (!open || makes) return;
    const c = new AbortController();
    cardeep.searchMakes(c.signal).then(setMakes).catch(() => setMakes([]));
    return () => c.abort();
  }, [open, makes]);

  useEffect(() => {
    if (!value.make) {
      setModels(null);
      return;
    }
    const c = new AbortController();
    setModels(null);
    cardeep
      .searchModels(value.make.make, c.signal)
      .then((rows) => setModels(rows.map((r) => ({ label: r.model, n: r.n }))))
      .catch(() => setModels([]));
    return () => c.abort();
  }, [value.make]);

  useEffect(() => {
    if (!value.make || !value.model) {
      setSubs(null);
      return;
    }
    const c = new AbortController();
    setSubs(null);
    cardeep
      .searchSubmodels(value.make.make, value.model, c.signal)
      .then((rows) => setSubs(rows.map((r) => ({ label: r.submodel, n: r.n }))))
      .catch(() => setSubs([]));
    return () => c.abort();
  }, [value.make, value.model]);

  const makeLabel = value.make ? (value.make.display ?? value.make.make) : null;
  const label = !makeLabel
    ? 'Cualquiera'
    : value.submodel
      ? `${makeLabel} ${value.submodel}`
      : value.model
        ? `${makeLabel} ${value.model}`
        : makeLabel;

  const q = query.trim().toLowerCase();
  const level: 0 | 1 | 2 = !value.make ? 0 : !value.model ? 1 : 2;

  const shownMakes = (makes ?? []).filter(
    (m) => m.make.toLowerCase().includes(q) || (m.display ?? '').toLowerCase().includes(q),
  );
  const shownModels = (models ?? []).filter((m) => m.label.toLowerCase().includes(q));
  const shownSubs = (subs ?? []).filter((s) => s.label.toLowerCase().includes(q));

  const placeholder =
    level === 0 ? 'Buscar marca…' : level === 1 ? 'Buscar modelo…' : 'Buscar versión…';

  return (
    <div className="relative">
      <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-white/52">
        Marca y modelo
      </span>
      <button
        type="button"
        onClick={() => {
          setOpen((o) => !o);
          setQuery('');
        }}
        className={
          'mt-1.5 flex h-11 w-full items-center gap-2.5 rounded-[11px] border border-white/10 bg-white/5 px-3.5 text-left ' +
          'transition-colors duration-200 hover:border-white/20 hover:bg-white/[0.07]'
        }
      >
        {value.make && <BrandMark slug={value.make.slug} name={makeLabel ?? ''} />}
        <span className="min-w-0 flex-1 truncate text-[13.5px] text-white">{label}</span>
        <ChevronDown
          size={14}
          className={'shrink-0 text-white/40 transition-transform duration-200 ' + (open ? 'rotate-180' : '')}
        />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.18, ease: EXPO }}
            className="glass-menu absolute left-0 right-0 top-[calc(100%+6px)] z-50 max-h-[19rem] overflow-y-auto rounded-[13px] p-1.5"
          >
            <div className="sticky top-0 z-10 mb-1 flex items-center gap-2 rounded-lg bg-white/[0.09] px-2.5 py-2 backdrop-blur">
              <Search size={12} className="shrink-0 text-white/35" />
              <input
                autoFocus
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={placeholder}
                className="w-full bg-transparent text-[13px] text-white outline-none placeholder:text-white/30"
              />
            </div>

            {level === 0 &&
              (makes === null ? (
                <div className="px-2.5 py-3 text-[12.5px] text-white/40">Cargando marcas…</div>
              ) : (
                shownMakes.map((b) => (
                  <Row
                    key={b.slug + b.make}
                    count={b.n}
                    onClick={() => {
                      onChange({ make: b, model: null, submodel: null });
                      setQuery('');
                    }}
                  >
                    <BrandMark slug={b.slug} name={b.display ?? b.make} />
                    <span className="min-w-0 flex-1 truncate">{b.display ?? b.make}</span>
                  </Row>
                ))
              ))}

            {level === 1 && (
              <>
                <Crumb
                  label="Todas las marcas"
                  onBack={() => {
                    onChange(EMPTY_MAKE_SELECTION);
                    setQuery('');
                  }}
                />
                {models === null ? (
                  <div className="px-2.5 py-3 text-[12.5px] text-white/40">Cargando modelos…</div>
                ) : (
                  shownModels.map((m) => (
                    <Row
                      key={m.label}
                      count={m.n}
                      onClick={() => {
                        onChange({ ...value, model: m.label, submodel: null });
                        setQuery('');
                      }}
                    >
                      <span className="min-w-0 flex-1 truncate">{m.label}</span>
                    </Row>
                  ))
                )}
              </>
            )}

            {level === 2 && (
              <>
                <Crumb
                  label={`Modelos de ${makeLabel}`}
                  onBack={() => {
                    onChange({ ...value, model: null, submodel: null });
                    setQuery('');
                  }}
                />
                {/* The whole model, always first and always present. Someone who
                    wants "a Clase C" should never have to read past nineteen
                    engine variants to say so. */}
                <Row
                  active={value.submodel === null}
                  onClick={() => {
                    onChange({ ...value, submodel: null });
                    setOpen(false);
                  }}
                >
                  <span className="min-w-0 flex-1 truncate font-medium">
                    {value.model} · todas las versiones
                  </span>
                </Row>
                <div className="my-1 h-px bg-white/10" />
                {subs === null ? (
                  <div className="px-2.5 py-3 text-[12.5px] text-white/40">Cargando versiones…</div>
                ) : shownSubs.length === 0 ? (
                  <div className="px-2.5 py-3 text-[12px] leading-snug text-white/35">
                    Sin versiones publicadas para este modelo.
                  </div>
                ) : (
                  shownSubs.map((s) => (
                    <Row
                      key={s.label}
                      count={s.n}
                      active={value.submodel === s.label}
                      onClick={() => {
                        onChange({ ...value, submodel: s.label });
                        setOpen(false);
                      }}
                    >
                      <span className="min-w-0 flex-1 truncate">{s.label}</span>
                    </Row>
                  ))
                )}
              </>
            )}
          </motion.div>
        </>
      )}
    </div>
  );
}
