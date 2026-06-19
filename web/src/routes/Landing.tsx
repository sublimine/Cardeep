import { lazy, Suspense, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useStats } from '../api/hooks';
import { useSealMap } from '../three/useSpainData';
import { VERDICT_COLOR } from '../three/mapColors';
import { Panel } from '../components/ui/Panel';
import { formatInt } from '../lib/format';
import type { SealVerdict, Stats } from '../api/types';
import './Landing.css';

// Three.js map is lazy-loaded so it stays out of the initial bundle.
const SpainMap = lazy(() => import('../three/SpainMap'));

// Verified live counts as of 2026-06-20 (Postgres :5433 census). Graceful fallback
// so the hero never renders empty if /stats is offline; the live map + coverage +
// explorer still read straight from the API (/geo/seal, /geo/{prov}/entities).
const FALLBACK: Stats = {
  dealers: 61_729,
  vehicles_unique_available: 1_704_968,
  events: 0,
  provinces: 52,
  municipalities: 8_132,
};

interface Metric {
  label: string;
  value: number;
  hint: string;
}

function buildMetrics(s: Stats): Metric[] {
  return [
    { label: 'Coches únicos', value: s.vehicles_unique_available, hint: 'en venta, deduplicados' },
    { label: 'Puntos de venta', value: s.dealers, hint: 'concesionarios · compraventas · desguaces' },
    { label: 'Provincias', value: s.provinces, hint: 'cobertura nacional' },
    { label: 'Municipios', value: s.municipalities, hint: 'hasta el último pueblo' },
  ];
}

const COVERAGE_SEGMENTS: { verdict: SealVerdict; label: string }[] = [
  { verdict: 'SELLADO', label: 'Sellado' },
  { verdict: 'PARCIAL', label: 'Parcial' },
  { verdict: 'GAP', label: 'Gap' },
];

export function Landing() {
  const { data, isError } = useStats();
  const stats = data ?? FALLBACK;
  const isLive = !!data && !isError;
  const metrics = buildMetrics(stats);

  const seal = useSealMap('venta');
  const coverage = useMemo(() => {
    const ps = Object.values(seal);
    const dist: Record<string, number> = { SELLADO: 0, PARCIAL: 0, GAP: 0, NO_DENOM: 0 };
    let num = 0;
    let den = 0;
    for (const p of ps) {
      dist[p.verdict] = (dist[p.verdict] ?? 0) + 1;
      num += p.numerator;
      den += p.denominator ?? 0;
    }
    return { total: ps.length, dist, num, den, pct: den ? (100 * num) / den : 0 };
  }, [seal]);

  return (
    <div className="landing">
      <section className="hero" aria-labelledby="hero-title">
        <div className="container hero__inner">
          <div className="hero__copy">
            <p className="hero__eyebrow">
              <span className="hero__eyebrow-dot" aria-hidden="true" />
              Inteligencia de mercado · Automoción · España
            </p>

            <h1 id="hero-title" className="hero__title">
              El mapa completo de un mercado
              <br />
              que hoy <span className="hero__accent">nadie tiene entero</span>.
            </h1>

            <p className="hero__sub">
              Cada coche en venta de España, desde la gran plataforma hasta el garaje
              perdido en la montaña. Indexado, deduplicado y verificado — servido por
              una API viva con su delta completo.
            </p>

            <div className="hero__actions">
              <Link to="/explore" className="btn btn--primary">
                Explorar el inventario
              </Link>
              <a
                className="btn btn--ghost"
                href="https://github.com/sublimine/Cardeep"
                target="_blank"
                rel="noreferrer noopener"
              >
                Acceso API
              </a>
            </div>
          </div>

          <div className="hero__stage">
            <div className="hero__map-backdrop">
              <div className="hero__grid" aria-hidden="true" />
              <div className="hero__sweep" aria-hidden="true" />
              <div className="hero__glow" aria-hidden="true" />
              <Suspense fallback={null}>
                <SpainMap />
              </Suspense>
            </div>
          </div>
        </div>

        <section className="command" aria-label="Cobertura nacional de venta">
          <div className="container command__inner">
            <Panel className="coverage">
              <div className="coverage__head">
                <span className="coverage__title">Cobertura nacional · venta</span>
                <span className={`livetag${isLive ? ' is-live' : ''}`}>
                  <span className="livetag__dot" aria-hidden="true" />
                  {isLive ? 'Datos en vivo' : 'Última instantánea'}
                </span>
              </div>

              {coverage.total > 0 ? (
                <>
                  <div className="coverage__figure">
                    <span className="coverage__pct mono">
                      {coverage.pct.toFixed(1)}
                      <i>%</i>
                    </span>
                    <span className="coverage__den mono">
                      {formatInt(coverage.num)} dealers servidos · censo registral{' '}
                      {formatInt(coverage.den)}
                    </span>
                  </div>

                  <div
                    className="coverage__bar"
                    role="img"
                    aria-label={`${coverage.dist.SELLADO} provincias selladas, ${coverage.dist.PARCIAL} parciales, ${coverage.dist.GAP} con gap`}
                  >
                    {COVERAGE_SEGMENTS.map((s) => {
                      const n = coverage.dist[s.verdict] ?? 0;
                      const w = coverage.total ? (n / coverage.total) * 100 : 0;
                      return w > 0 ? (
                        <span
                          key={s.verdict}
                          className="coverage__seg"
                          style={{ width: `${w}%`, background: VERDICT_COLOR[s.verdict] }}
                        />
                      ) : null;
                    })}
                  </div>

                  <div className="coverage__keys mono">
                    {COVERAGE_SEGMENTS.map((s) => (
                      <span key={s.verdict} className="coverage__key">
                        <i style={{ background: VERDICT_COLOR[s.verdict] }} />
                        {s.label} {coverage.dist[s.verdict] ?? 0}
                      </span>
                    ))}
                    <span className="coverage__key coverage__key--muted">
                      {coverage.total} provincias
                    </span>
                  </div>
                </>
              ) : (
                <div className="coverage__skeleton" aria-hidden="true" />
              )}
            </Panel>

            <div className="command__stats">
              {metrics.map((m) => (
                <div key={m.label} className="stat">
                  <span className="stat__label">{m.label}</span>
                  <span className="stat__value mono">{formatInt(m.value)}</span>
                  <span className="stat__hint">{m.hint}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </section>
    </div>
  );
}
