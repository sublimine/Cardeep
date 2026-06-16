// Entity-kind display metadata: Spanish label + a semantic accent color.
// Colors are deliberate (not decorative): trade dealers (oficial/compraventa) lean
// to the brand cyan family, scrap/auction/import to warmer or muted tones.
import type { EntityKind } from '../api/types';

export const KIND_LABEL: Record<EntityKind, string> = {
  compraventa: 'Compraventa',
  concesionario_oficial: 'Concesionario oficial',
  desguace: 'Desguace',
  garaje: 'Garaje',
  plataforma: 'Plataforma',
  particular: 'Particular',
  subasta: 'Subasta',
  oem_vo_portal: 'Portal OEM VO',
  importador: 'Importador',
  rent_a_car_vo: 'Rent a Car VO',
  cadena: 'Cadena',
};

export const KIND_COLOR: Record<EntityKind, string> = {
  concesionario_oficial: '#35e0d0',
  compraventa: '#5beadd',
  plataforma: '#6c5ce7',
  cadena: '#8b7cf0',
  rent_a_car_vo: '#4cc4f0',
  importador: '#4cc4f0',
  garaje: '#9aa6be',
  subasta: '#f5b33c',
  desguace: '#f0556b',
  oem_vo_portal: '#22c55e',
  particular: '#5c6883',
};

export function kindLabel(kind: EntityKind | string): string {
  return (KIND_LABEL as Record<string, string>)[kind] ?? kind;
}

export function kindColor(kind: EntityKind | string): string {
  return (KIND_COLOR as Record<string, string>)[kind] ?? '#9aa6be';
}
