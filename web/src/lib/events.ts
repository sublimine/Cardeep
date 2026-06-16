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

export function eventDetail(eventType: string, oldValue: unknown, newValue: unknown): string {
  if (eventType === 'PRICE_CHANGE' && typeof oldValue === 'number' && typeof newValue === 'number') {
    return `${formatPrice(oldValue)} → ${formatPrice(newValue)}`;
  }
  if (eventType === 'KM_CHANGE' && typeof oldValue === 'number' && typeof newValue === 'number') {
    return `${formatKm(oldValue)} → ${formatKm(newValue)}`;
  }
  return '';
}
