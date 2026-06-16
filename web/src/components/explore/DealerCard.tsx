import { Link } from 'react-router-dom';
import type { EntitySummary } from '../../api/types';
import { kindColor, kindLabel } from '../../lib/kinds';
import { Badge } from '../ui/Badge';

export function DealerCard({ entity }: { entity: EntitySummary }) {
  const name = (entity.trade_name || entity.legal_name || entity.cdp_code).trim();
  return (
    <Link to={`/dealer/${entity.cdp_code}`} className="dealercard">
      <div className="dealercard__top">
        <span className="dealercard__name">{name}</span>
        {entity.is_tier1 && (
          <span className="dealercard__tier" title="Tier 1 — plataforma de defensas duras">★</span>
        )}
      </div>
      <div className="dealercard__badges">
        <Badge color={kindColor(entity.kind)}>{kindLabel(entity.kind)}</Badge>
        {entity.status !== 'active' && <Badge color="#5c6883">{entity.status}</Badge>}
      </div>
      <span className="dealercard__cdp mono">{entity.cdp_code}</span>
      <span className="dealercard__cta">Ver inventario →</span>
    </Link>
  );
}
