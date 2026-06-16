import { Link } from 'react-router-dom';
import type { VehicleListItem } from '../../api/types';
import { formatKm, formatPrice } from '../../lib/format';
import './vcard.css';

export function VehicleCard({ vehicle }: { vehicle: VehicleListItem }) {
  const title = (vehicle.title || `${vehicle.make ?? ''} ${vehicle.model ?? ''}`).trim() || 'Vehículo';
  const specs = [
    vehicle.year != null ? String(vehicle.year) : null,
    vehicle.km != null ? formatKm(vehicle.km) : null,
    vehicle.fuel,
    vehicle.transmission,
  ]
    .filter(Boolean)
    .join(' · ');

  return (
    <Link to={`/vehicle/${vehicle.vehicle_ulid}`} className="vcard">
      <div className="vcard__media">
        {vehicle.photo_url ? (
          <img src={vehicle.photo_url} alt={title} loading="lazy" width={400} height={300} />
        ) : (
          <div className="vcard__noimg mono">sin foto</div>
        )}
        {vehicle.status !== 'available' && <span className="vcard__status">{vehicle.status}</span>}
      </div>
      <div className="vcard__body">
        <span className="vcard__title">{title}</span>
        <span className="vcard__specs mono">{specs || '—'}</span>
        <span className="vcard__price mono">{formatPrice(vehicle.price, vehicle.currency ?? 'EUR')}</span>
      </div>
    </Link>
  );
}
