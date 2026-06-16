// INE province reference data (code → display name + autonomous community).
// Codes "01".."52" are the INE province codes — they match geo_province.code and the
// seal/topojson join key. This is stable reference data (INE codes do not change), so
// it is embedded rather than fetched (there is no lightweight "list provinces" endpoint).
export interface ProvinceMeta {
  code: string;
  name: string;
  ccaa: string;
}

export const PROVINCES: ProvinceMeta[] = [
  { code: '01', name: 'Álava', ccaa: 'País Vasco' },
  { code: '02', name: 'Albacete', ccaa: 'Castilla-La Mancha' },
  { code: '03', name: 'Alicante', ccaa: 'C. Valenciana' },
  { code: '04', name: 'Almería', ccaa: 'Andalucía' },
  { code: '05', name: 'Ávila', ccaa: 'Castilla y León' },
  { code: '06', name: 'Badajoz', ccaa: 'Extremadura' },
  { code: '07', name: 'Illes Balears', ccaa: 'Illes Balears' },
  { code: '08', name: 'Barcelona', ccaa: 'Cataluña' },
  { code: '09', name: 'Burgos', ccaa: 'Castilla y León' },
  { code: '10', name: 'Cáceres', ccaa: 'Extremadura' },
  { code: '11', name: 'Cádiz', ccaa: 'Andalucía' },
  { code: '12', name: 'Castellón', ccaa: 'C. Valenciana' },
  { code: '13', name: 'Ciudad Real', ccaa: 'Castilla-La Mancha' },
  { code: '14', name: 'Córdoba', ccaa: 'Andalucía' },
  { code: '15', name: 'A Coruña', ccaa: 'Galicia' },
  { code: '16', name: 'Cuenca', ccaa: 'Castilla-La Mancha' },
  { code: '17', name: 'Girona', ccaa: 'Cataluña' },
  { code: '18', name: 'Granada', ccaa: 'Andalucía' },
  { code: '19', name: 'Guadalajara', ccaa: 'Castilla-La Mancha' },
  { code: '20', name: 'Gipuzkoa', ccaa: 'País Vasco' },
  { code: '21', name: 'Huelva', ccaa: 'Andalucía' },
  { code: '22', name: 'Huesca', ccaa: 'Aragón' },
  { code: '23', name: 'Jaén', ccaa: 'Andalucía' },
  { code: '24', name: 'León', ccaa: 'Castilla y León' },
  { code: '25', name: 'Lleida', ccaa: 'Cataluña' },
  { code: '26', name: 'La Rioja', ccaa: 'La Rioja' },
  { code: '27', name: 'Lugo', ccaa: 'Galicia' },
  { code: '28', name: 'Madrid', ccaa: 'Madrid' },
  { code: '29', name: 'Málaga', ccaa: 'Andalucía' },
  { code: '30', name: 'Murcia', ccaa: 'Murcia' },
  { code: '31', name: 'Navarra', ccaa: 'Navarra' },
  { code: '32', name: 'Ourense', ccaa: 'Galicia' },
  { code: '33', name: 'Asturias', ccaa: 'Asturias' },
  { code: '34', name: 'Palencia', ccaa: 'Castilla y León' },
  { code: '35', name: 'Las Palmas', ccaa: 'Canarias' },
  { code: '36', name: 'Pontevedra', ccaa: 'Galicia' },
  { code: '37', name: 'Salamanca', ccaa: 'Castilla y León' },
  { code: '38', name: 'Santa Cruz de Tenerife', ccaa: 'Canarias' },
  { code: '39', name: 'Cantabria', ccaa: 'Cantabria' },
  { code: '40', name: 'Segovia', ccaa: 'Castilla y León' },
  { code: '41', name: 'Sevilla', ccaa: 'Andalucía' },
  { code: '42', name: 'Soria', ccaa: 'Castilla y León' },
  { code: '43', name: 'Tarragona', ccaa: 'Cataluña' },
  { code: '44', name: 'Teruel', ccaa: 'Aragón' },
  { code: '45', name: 'Toledo', ccaa: 'Castilla-La Mancha' },
  { code: '46', name: 'Valencia', ccaa: 'C. Valenciana' },
  { code: '47', name: 'Valladolid', ccaa: 'Castilla y León' },
  { code: '48', name: 'Bizkaia', ccaa: 'País Vasco' },
  { code: '49', name: 'Zamora', ccaa: 'Castilla y León' },
  { code: '50', name: 'Zaragoza', ccaa: 'Aragón' },
  { code: '51', name: 'Ceuta', ccaa: 'Ceuta' },
  { code: '52', name: 'Melilla', ccaa: 'Melilla' },
];

export const PROVINCE_BY_CODE: Record<string, ProvinceMeta> = Object.fromEntries(
  PROVINCES.map((p) => [p.code, p]),
);

export function provinceName(code: string | null | undefined): string {
  if (!code) return '—';
  return PROVINCE_BY_CODE[code]?.name ?? code;
}
