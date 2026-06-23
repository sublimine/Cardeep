// Shared rendering for vehicle_event / delta rows (used by Dealer activity + Vehicle history).
import { formatKm, formatPrice } from './format';

export const EVENT_LABEL: Record<string, string> = {
  NEW: 'Alta',
  GONE: 'Baja',
  PRICE_CHANGE: 'Precio',
  KM_CHANGE: 'Kilómetros',
  PHOTO_CHANGE: 'Foto',
};

export function eventLabel(eventType: string): string {
  return EVENT_LABEL[eventType] ?? eventType;
}

// vehicle_event old_value/new_value is a small jsonb object ({"price":40000} / {"km":80500}). Depending
// on whether the API has the jsonb codec active it arrives as an OBJECT or as a JSON-encoded STRING (and
// historically a bare number). Coerce all three so the PRICE/KM detail renders regardless — the prior
// `typeof === 'number'` check never matched the object/string and the detail was silently dropped.
function coerceNum(v: unknown, key: 'price' | 'km'): number | null {
  let val: unknown = v;
  if (typeof val === 'string') {
    try {
      val = JSON.parse(val);
    } catch {
      const n = Number(v);
      return Number.isFinite(n) ? n : null;
    }
  }
  if (val && typeof val === 'object') {
    const n = (val as Record<string, unknown>)[key];
    return typeof n === 'number' ? n : null;
  }
  return typeof val === 'number' ? val : null;
}

export function eventDetail(eventType: string, oldValue: unknown, newValue: unknown): string {
  if (eventType === 'PRICE_CHANGE') {
    const o = coerceNum(oldValue, 'price');
    const n = coerceNum(newValue, 'price');
    if (o !== null && n !== null) return `${formatPrice(o)} → ${formatPrice(n)}`;
  }
  if (eventType === 'KM_CHANGE') {
    const o = coerceNum(oldValue, 'km');
    const n = coerceNum(newValue, 'km');
    if (o !== null && n !== null) return `${formatKm(o)} → ${formatKm(n)}`;
  }
  return '';
}
