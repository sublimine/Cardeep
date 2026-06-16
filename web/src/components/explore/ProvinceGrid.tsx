import { useMemo, useState } from 'react';
import { PROVINCES } from '../../lib/provinces';
import { useSealMap } from '../../three/useSpainData';
import { VERDICT_COLOR } from '../../three/mapColors';
import { formatInt } from '../../lib/format';
import { Badge } from '../ui/Badge';
import type { SealVerdict } from '../../api/types';

const VERDICT_LABEL: Record<SealVerdict, string> = {
  SELLADO: 'Sellado',
  PARCIAL: 'Parcial',
  GAP: 'Gap',
  NO_DENOM: 'Sin techo',
};

type SortKey = 'coverage' | 'name';

interface ProvinceGridProps {
  onPick: (code: string) => void;
}

export function ProvinceGrid({ onPick }: ProvinceGridProps) {
  const seal = useSealMap('venta');
  const [sort, setSort] = useState<SortKey>('coverage');

  const items = useMemo(() => {
    const arr = PROVINCES.map((p) => ({ ...p, cov: seal[p.code] }));
    arr.sort((a, b) =>
      sort === 'name'
        ? a.name.localeCompare(b.name, 'es')
        : (b.cov?.coverage_pct ?? -1) - (a.cov?.coverage_pct ?? -1),
    );
    return arr;
  }, [seal, sort]);

  return (
    <section className="provgrid">
      <header className="explore__head">
        <div>
          <h1 className="explore__title">Explora por provincia</h1>
          <p className="explore__sub">
            52 provincias · cobertura de venta sobre el censo registral. Elige una para ver sus
            puntos de venta y su inventario.
          </p>
        </div>
        <div className="explore__sort">
          <button
            className={`chip${sort === 'coverage' ? ' is-on' : ''}`}
            onClick={() => setSort('coverage')}
          >
            Cobertura
          </button>
          <button
            className={`chip${sort === 'name' ? ' is-on' : ''}`}
            onClick={() => setSort('name')}
          >
            A–Z
          </button>
        </div>
      </header>

      <div className="provgrid__grid">
        {items.map((p) => {
          const verdict = p.cov?.verdict;
          return (
            <button key={p.code} className="provcard" onClick={() => onPick(p.code)}>
              <div className="provcard__top">
                <span className="provcard__name">{p.name}</span>
                <span className="provcard__ccaa">{p.ccaa}</span>
              </div>
              <div className="provcard__metric">
                <span className="provcard__cov mono">
                  {p.cov?.coverage_pct != null ? `${p.cov.coverage_pct.toFixed(0)}%` : '—'}
                </span>
                {verdict && (
                  <Badge color={VERDICT_COLOR[verdict]} variant="dot">
                    {VERDICT_LABEL[verdict]}
                  </Badge>
                )}
              </div>
              <div className="provcard__track" aria-hidden="true">
                <span
                  className="provcard__fill"
                  style={{
                    width: `${Math.min(100, p.cov?.coverage_pct ?? 0)}%`,
                    background: verdict ? VERDICT_COLOR[verdict] : 'var(--line)',
                  }}
                />
              </div>
              <span className="provcard__dealers mono">
                {p.cov ? `${formatInt(p.cov.numerator)} dealers servidos` : 'sin dato'}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
