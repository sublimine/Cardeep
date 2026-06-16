import { Link } from 'react-router-dom';
import { useStats } from '../api/hooks';
import type { Stats } from '../api/types';
import './Landing.css';

// Verified live counts as of 2026-06-16 (services/api/routers/ops.py /stats).
// Used as graceful fallback so the hero never renders empty if the API is offline.
const FALLBACK: Stats = {
  dealers: 40_194,
  vehicles_unique_available: 1_486_285,
  events: 0,
  provinces: 52,
  municipalities: 8_132,
};

const nf = new Intl.NumberFormat('es-ES');

interface Metric {
  label: string;
  value: number;
  hint: string;
}

function buildMetrics(s: Stats): Metric[] {
  return [
    { label: 'Coches únicos', value: s.vehicles_unique_available, hint: 'en venta, deduplicados' },
    { label: 'Puntos de venta', value: s.dealers, hint: 'concesionarios, compraventas, desguaces' },
    { label: 'Provincias', value: s.provinces, hint: 'cobertura nacional' },
    { label: 'Municipios', value: s.municipalities, hint: 'hasta el último pueblo' },
  ];
}

export function Landing() {
  const { data, isError } = useStats();
  const stats = data ?? FALLBACK;
  const isLive = !!data && !isError;
  const metrics = buildMetrics(stats);

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

          <div className="hero__stage" aria-hidden="true">
            <div className="hero__map-backdrop">
              <div className="hero__grid" />
              <div className="hero__sweep" />
              <div className="hero__glow" />
            </div>
          </div>
        </div>

        <div className="hero__metrics">
          <div className="container hero__metrics-inner">
            <span className={`hero__livetag${isLive ? ' is-live' : ''}`}>
              <span className="hero__livedot" aria-hidden="true" />
              {isLive ? 'Datos en vivo' : 'Última instantánea'}
            </span>
            <dl className="metrics">
              {metrics.map((m) => (
                <div key={m.label} className="metric">
                  <dt className="metric__label">{m.label}</dt>
                  <dd className="metric__value mono">{nf.format(m.value)}</dd>
                  <dd className="metric__hint">{m.hint}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </section>
    </div>
  );
}
