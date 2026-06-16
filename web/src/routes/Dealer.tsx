import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useEntity, useEntityDelta, useEntityInventory } from '../api/hooks';
import { VehicleCard } from '../components/vehicle/VehicleCard';
import { Badge } from '../components/ui/Badge';
import { kindColor, kindLabel } from '../lib/kinds';
import { provinceName } from '../lib/provinces';
import { formatDate, formatInt } from '../lib/format';
import { eventDetail, eventLabel } from '../lib/events';
import './dealer.css';

const PAGE_SIZE = 24;

export function Dealer() {
  const { cdp } = useParams();
  const { data: entity, isLoading, isError } = useEntity(cdp);
  const [page, setPage] = useState(1);
  const inv = useEntityInventory(cdp, page, PAGE_SIZE);
  const delta = useEntityDelta(cdp, 1, 8);

  if (isLoading) {
    return (
      <div className="container">
        <div className="explore__state mono">Cargando dealer…</div>
      </div>
    );
  }
  if (isError || !entity) {
    return (
      <div className="container">
        <div className="explore__state mono">Dealer no encontrado ({cdp}).</div>
      </div>
    );
  }

  const name = (entity.trade_name || entity.legal_name || entity.cdp_code).trim();
  const items = inv.data?.items ?? [];

  return (
    <div className="container dealer">
      <header className="dealer__head">
        <Link to={`/explore?prov=${entity.province_code ?? ''}`} className="explore__back">
          ← {provinceName(entity.province_code)}
        </Link>
        <div className="dealer__headrow">
          <h1 className="dealer__name">{name}</h1>
          {entity.is_tier1 && <span className="dealer__tier" title="Tier 1">★ Tier 1</span>}
        </div>
        <div className="dealer__badges">
          <Badge color={kindColor(entity.kind)}>{kindLabel(entity.kind)}</Badge>
          <Badge variant="dot" color="#9aa6be">{provinceName(entity.province_code)}</Badge>
          {entity.status !== 'active' && <Badge color="#5c6883">{entity.status}</Badge>}
        </div>

        <dl className="dealer__facts">
          <div>
            <dt>Inventario disponible</dt>
            <dd className="mono">{formatInt(entity.available_inventory)} coches</dd>
          </div>
          {entity.n_aliases > 0 && (
            <div>
              <dt>Fichas agrupadas</dt>
              <dd className="mono">{formatInt(entity.n_aliases + 1)}</dd>
            </div>
          )}
          {entity.website && (
            <div>
              <dt>Web</dt>
              <dd>
                <a href={entity.website} target="_blank" rel="noreferrer noopener" className="dealer__link">
                  Sitio oficial ↗
                </a>
              </dd>
            </div>
          )}
          {entity.phone && (
            <div>
              <dt>Teléfono</dt>
              <dd className="mono">{entity.phone}</dd>
            </div>
          )}
          <div>
            <dt>cdp_code</dt>
            <dd className="mono dealer__cdp">{entity.canonical_cdp_code}</dd>
          </div>
        </dl>
      </header>

      <div className="dealer__layout">
        <section className="dealer__inventory">
          <h2 className="dealer__h2">
            Inventario <span className="mono dealer__count">{formatInt(entity.available_inventory)}</span>
          </h2>

          {inv.isLoading && <div className="explore__state mono">Cargando inventario…</div>}
          {inv.isError && <div className="explore__state mono">No se pudo cargar el inventario.</div>}
          {!inv.isLoading && !inv.isError && (
            <>
              {items.length === 0 ? (
                <div className="explore__state mono">Sin coches disponibles en esta página.</div>
              ) : (
                <div className="dealer__grid">
                  {items.map((v) => (
                    <VehicleCard key={v.vehicle_ulid} vehicle={v} />
                  ))}
                </div>
              )}
              <nav className="pager" aria-label="Paginación">
                <button className="chip" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>
                  ← Anterior
                </button>
                <span className="pager__page mono">Página {page}</span>
                <button className="chip" disabled={!inv.data?.has_more} onClick={() => setPage((p) => p + 1)}>
                  Siguiente →
                </button>
              </nav>
            </>
          )}
        </section>

        <aside className="dealer__activity">
          <h2 className="dealer__h2">Actividad reciente</h2>
          {delta.data && delta.data.items.length > 0 ? (
            <ul className="timeline">
              {delta.data.items.map((e, i) => (
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
            <p className="dealer__muted">Sin eventos recientes registrados.</p>
          )}
        </aside>
      </div>
    </div>
  );
}
