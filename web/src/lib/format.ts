// es-ES formatters, centralized so every surface renders numbers the same way.
const intFmt = new Intl.NumberFormat('es-ES');

export function formatInt(n: number | null | undefined): string {
  return n == null ? '—' : intFmt.format(n);
}

export function formatPrice(value: number | null | undefined, currency = 'EUR'): string {
  if (value == null) return 'Consultar';
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: currency || 'EUR',
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatKm(km: number | null | undefined): string {
  return km == null ? '— km' : `${intFmt.format(km)} km`;
}

export function formatYear(year: number | null | undefined): string {
  return year == null ? '—' : String(year);
}

// "12 jun 2026" — short date from an ISO/PG timestamp string.
export function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  const d = new Date(value.replace(' ', 'T'));
  if (Number.isNaN(d.getTime())) return '—';
  return new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short', year: 'numeric' }).format(d);
}
