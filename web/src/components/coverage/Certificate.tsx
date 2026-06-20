import { useGeoExhaustiveness } from '../../api/hooks';
import { certView } from '../../lib/exhaustiveness';
import { Badge } from '../ui/Badge';
import './certificate.css';

// The statistical FLOOR (MSE capture-recapture lower bound) — the honest complement to the served
// registral coverage shown above it. The big figure says "this much is served"; this credential says
// "and we can statistically prove completeness is at least this much". Honest by construction: with no
// build the national cert is null and we state "pendiente de build", never a fabricated number.
export function Certificate() {
  const { data } = useGeoExhaustiveness();
  const v = certView(data);

  return (
    <div className="cert">
      <div className="cert__divider" aria-hidden="true" />
      <div className="cert__row">
        <span className="cert__label">
          Suelo estadístico · MSE
          <span className="cert__hint">captura-recaptura · k listas ortogonales</span>
        </span>

        {v.hasData ? (
          <span className="cert__value">
            <span className="cert__pct mono">
              ≥&nbsp;{v.coverageLowerPct}
              <i>%</i>
            </span>
            <Badge
              variant={v.sealed ? 'solid' : 'outline'}
              color={v.sealed ? 'var(--seal-sellado)' : 'var(--seal-parcial)'}
              title={v.method ?? undefined}
            >
              {v.sealed ? 'Sellado' : 'Parcial'}
            </Badge>
          </span>
        ) : (
          <span className="cert__pending mono">pendiente de build</span>
        )}
      </div>

      {v.hasData && (
        <p className="cert__meta mono">
          {v.kLists} listas · {v.nObs?.toLocaleString('es-ES')} observados
          {v.coveragePointPct ? ` · estimación ${v.coveragePointPct}%` : ''}
          {v.ciBand ? ` · IC N̂ ${v.ciBand}` : ''}
        </p>
      )}
    </div>
  );
}
