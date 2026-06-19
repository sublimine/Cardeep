import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useProvinceEntities } from '../../api/hooks';
import { useSealMap } from '../../three/useSpainData';
import { provinceName, PROVINCE_BY_CODE } from '../../lib/provinces';
import { kindLabel } from '../../lib/kinds';
import { VERDICT_COLOR } from '../../three/mapColors';
import { formatInt } from '../../lib/format';
import { Badge } from '../ui/Badge';
import { DealerCard } from './DealerCard';
import type { SealVerdict } from '../../api/types';

const PAGE_SIZE = 60;

const VERDICT_LABEL: Record<SealVerdict, string> = {
  SELLADO: 'Sellado',
  PARCIAL: 'Parcial',
  GAP: 'Gap',
  NO_DENOM: 'Sin techo',
};

export function DealerBrowser({ prov }: { prov: string }) {
  const [page, setPage] = useState(1);
  const [activeKinds, setActiveKinds] = useState<Set<string>>(new Set());
  const [tier1Only, setTier1Only] = useState(false);
  const [query, setQuery] = useState('');

  const { data, isLoading, isError } = useProvinceEntities(prov, page, PAGE_SIZE);
  const cov = useSealMap('venta')[prov];
  const meta = PROVINCE_BY_CODE[prov];

  const items = useMemo(() => data?.items ?? [], [data]);

  // Facets present on this page (the API has no global facet endpoint; filters
  // apply to the loaded page — see note in docs/frontend/00-PLAN.md).
  const kindsPresent = useMemo(
    () => Array.from(new Set(items.map((e) => e.kind))).sort(),
    [items],
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter(
      (e) =>
        (activeKinds.size === 0 || activeKinds.has(e.kind)) &&
        (!tier1Only || e.is_tier1) &&
        (q === '' || (e.trade_name || e.legal_name || '').toLowerCase().includes(q)),
    );
  }, [items, activeKinds, tier1Only, query]);

  const toggleKind = (kind: string) => {
    setActiveKinds((prev) => {
      const next = new Set(prev);
      if (next.has(kind)) next.delete(kind);
      else next.add(kind);
      return next;
    });
  };

  return (
    <section className="dealers">
      <header className="explore__head">
        <div>
          <Link to="/explore" className="explore__back">
            ← Provincias
          </Link>
          <h1 className="explore__title">{provinceName(prov)}</h1>
          <p className="explore__sub">
            {meta?.ccaa}
            {cov && (
              <>
                {' · '}
                <Badge color={VERDICT_COLOR[cov.verdict]} variant="dot">
                  {VERDICT_LABEL[cov.verdict]}
                </Badge>{' '}
                {cov.coverage_pct != null ? `${cov.coverage_pct.toFixed(0)}% cobertura` : ''} ·{' '}
                {formatInt(cov.numerator)} dealers servidos
                {cov.denominator != null ? ` / techo ${formatInt(cov.denominator)}` : ''}
              </>
            )}
          </p>
        </div>
      </header>

      <div className="dealers__layout">
        <aside className="filters" aria-label="Filtros">
          <div className="filters__group">
            <label className="filters__label" htmlFor="dealer-search">
              Buscar
            </label>
            <input
              id="dealer-search"
              className="filters__input"
              type="search"
              placeholder="Nombre del dealer…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          {kindsPresent.length > 0 && (
            <div className="filters__group">
              <span className="filters__label">Tipo</span>
              {kindsPresent.map((k) => (
                <label key={k} className="filters__check">
                  <input
                    type="checkbox"
                    checked={activeKinds.has(k)}
                    onChange={() => toggleKind(k)}
                  />
                  {kindLabel(k)}
                </label>
              ))}
            </div>
          )}

          <div className="filters__group">
            <label className="filters__check">
              <input
                type="checkbox"
                checked={tier1Only}
                onChange={(e) => setTier1Only(e.target.checked)}
              />
              Solo Tier 1
            </label>
          </div>
        </aside>

        <div className="dealers__main">
          {isLoading && <div className="explore__state mono">Cargando dealers…</div>}
          {isError && (
            <div className="explore__state mono">
              No se pudieron cargar los dealers. ¿API arriba en :8090?
            </div>
          )}
          {!isLoading && !isError && (
            <>
              <div className="dealers__count mono">
                {filtered.length} de {items.length} en esta página
              </div>
              {filtered.length === 0 ? (
                <div className="explore__state mono">Ningún dealer coincide con el filtro.</div>
              ) : (
                <div className="dealers__grid">
                  {filtered.map((e) => (
                    <DealerCard key={e.cdp_code} entity={e} />
                  ))}
                </div>
              )}

              <nav className="pager" aria-label="Paginación">
                <button
                  className="chip"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  ← Anterior
                </button>
                <span className="pager__page mono">Página {page}</span>
                <button
                  className="chip"
                  disabled={!data?.has_more}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Siguiente →
                </button>
              </nav>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
