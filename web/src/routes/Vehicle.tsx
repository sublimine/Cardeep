import { Link, useNavigate, useParams } from 'react-router-dom';
import { useVehicle, useVehicleHistory, useVehiclePlatforms } from '../api/hooks';
import { Badge } from '../components/ui/Badge';
import { eventDetail, eventLabel } from '../lib/events';
import { formatDate, formatKm, formatPrice } from '../lib/format';
import './dealer.css'; // shared detail styles (timeline, section headings, links)
import './vehicle.css';

interface Spec {
  label: string;
  value: string | null;
}

export function Vehicle() {
  const { ulid } = useParams();
  const navigate = useNavigate();
  const { data: v, isLoading, isError } = useVehicle(ulid);
  const history = useVehicleHistory(ulid, 1, 50);
  const platforms = useVehiclePlatforms(ulid);

  if (isLoading) {
    return (
      <div className="container">
        <div className="explore__state mono">Cargando vehículo…</div>
      </div>
    );
  }
  if (isError || !v) {
    return (
      <div className="container">
        <div className="explore__state mono">Vehículo no encontrado ({ulid}).</div>
      </div>
    );
  }

  const title = (v.title || `${v.make ?? ''} ${v.model ?? ''}`).trim() || 'Vehículo';
  const specs: Spec[] = [
    { label: 'Marca', value: v.make },
    { label: 'Modelo', value: v.model },
    { label: 'Año', value: v.year != null ? String(v.year) : null },
    { label: 'Kilómetros', value: v.km != null ? formatKm(v.km) : null },
    { label: 'Combustible', value: v.fuel },
    { label: 'Cambio', value: v.transmission },
  ];
  const owningDealer = platforms.data?.vehicle.owning_dealer;

  return (
    <div className="container vehicle">
      <button className="explore__back vehicle__back" onClick={() => navigate(-1)}>
        ← Atrás
      </button>

      <div className="vehicle__hero">
        <div className="vehicle__media">
          {v.photo_url ? (
            <img src={v.photo_url} alt={title} width={800} height={600} />
          ) : (
            <div className="vehicle__noimg mono">sin foto</div>
          )}
        </div>

        <div className="vehicle__info">
          <h1 className="vehicle__title">{title}</h1>
          <div className="vehicle__price mono">{formatPrice(v.price, v.currency ?? 'EUR')}</div>

          <div className="vehicle__badges">
            <Badge color={v.status === 'available' ? '#22c55e' : '#f0556b'}>
              {v.status === 'available' ? 'Disponible' : v.status}
            </Badge>
            {!v.is_canonical && (
              <Badge variant="outline" color="#6c5ce7">
                ficha alias
              </Badge>
            )}
          </div>

          <dl className="vehicle__specs">
            {specs
              .filter((s) => s.value)
              .map((s) => (
                <div key={s.label}>
                  <dt>{s.label}</dt>
                  <dd className="mono">{s.value}</dd>
                </div>
              ))}
          </dl>

          {v.deep_link && (
            <a href={v.deep_link} target="_blank" rel="noreferrer noopener" className="btn btn--primary vehicle__cta">
              Ver anuncio original ↗
            </a>
          )}

          {owningDealer && (
            <Link to={`/dealer/${owningDealer.cdp_code}`} className="vehicle__dealer">
              Vendido por <strong>{(owningDealer.name ?? owningDealer.cdp_code).trim()}</strong>
            </Link>
          )}

          <div className="vehicle__seen mono">
            Visto del {formatDate(v.first_seen)} al {formatDate(v.last_seen)}
            {!v.is_canonical && (
              <>
                {' · '}
                <Link to={`/vehicle/${v.canonical_vehicle_ulid}`} className="dealer__link">
                  ver ficha canónica
                </Link>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="vehicle__sections">
        <section className="vehicle__section">
          <h2 className="dealer__h2">Historial</h2>
          {history.data && history.data.items.length > 0 ? (
            <ul className="timeline">
              {history.data.items.map((e, i) => (
                <li key={`${e.observed_at}-${i}`} className="timeline__item">
                  <span className={`timeline__dot timeline__dot--${e.event_type.toLowerCase()}`} />
                  <div className="timeline__body">
                    <span className="timeline__label">{eventLabel(e.event_type)}</span>
                    {eventDetail(e.event_type, e.old_value, e.new_value) && (
                      <span className="timeline__detail mono">
                        {eventDetail(e.event_type, e.old_value, e.new_value)}
                      </span>
                    )}
                    <span className="timeline__date mono">{formatDate(e.observed_at)}</span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="dealer__muted">Sin historial registrado.</p>
          )}
        </section>

        <section className="vehicle__section">
          <h2 className="dealer__h2">
            Plataformas{' '}
            {platforms.data && (
              <span className="mono dealer__count">{platforms.data.platforms.length}</span>
            )}
          </h2>
          {platforms.data && platforms.data.platforms.length > 0 ? (
            <ul className="platforms">
              {platforms.data.platforms.map((p) => (
                <li key={`${p.cdp_code}-${p.listing_ref ?? ''}`} className="platforms__item">
                  <div className="platforms__head">
                    <span className="platforms__name">{(p.trade_name ?? p.cdp_code).trim()}</span>
                    {p.is_tier1 && <span className="dealer__tier" title="Tier 1">★</span>}
                  </div>
                  <span className="platforms__price mono">{formatPrice(p.platform_price)}</span>
                  {p.listing_url && (
                    <a href={p.listing_url} target="_blank" rel="noreferrer noopener" className="dealer__link">
                      Ver listado ↗
                    </a>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="dealer__muted">No figura en plataformas de terceros.</p>
          )}
        </section>
      </div>
    </div>
  );
}
