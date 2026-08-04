/**
 * Self-host the marque logos instead of asking a third-party CDN for them.
 *
 * Measured before this existed: 70 of the 104 listable marques had no local asset,
 * covering 1.353.488 cars — 91% of the index — and every one of them, including
 * Mercedes-Benz, Peugeot, Volkswagen and BMW, was fetched from cdn.simpleicons.org
 * at render time. That is why logos kept "disappearing": a marque without a local
 * file has no logo the moment the CDN is slow, blocked, or has dropped the icon,
 * and Simple Icons removes brands twice a year without notice.
 *
 * Source: the Simple Icons repository, licensed CC0-1.0 — public domain, no
 * attribution required. The `source` URL of each icon (the marque's own brand
 * page) is recorded anyway, because provenance for a trademark should be written
 * down whether or not a licence compels it.
 *
 * These marks are monochrome by design. On a dark interface that is a coherent
 * choice rather than a compromise — and a mark that is always there beats a
 * full-colour one that sometimes is not.
 *
 * Run: node tools/fetch-brand-logos.mjs
 */
import { writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = join(here, '..', 'public', 'logos');
const BASE = 'https://raw.githubusercontent.com/simple-icons/simple-icons/master/icons';

/** cardeep slug -> simple-icons file name (without .svg). */
const MAP = {
  'mercedes-benz': 'mercedes', peugeot: 'peugeot', volkswagen: 'volkswagen',
  bmw: 'bmw', audi: 'audi', renault: 'renault', citroen: 'citroen', ford: 'ford',
  seat: 'seat', opel: 'opel', kia: 'kia', toyota: 'toyota', nissan: 'nissan',
  hyundai: 'hyundai', fiat: 'fiat', skoda: 'skoda', volvo: 'volvo', dacia: 'dacia',
  mini: 'mini', mazda: 'mazda', jeep: 'jeep', mg: 'mg', porsche: 'porsche',
  mitsubishi: 'mitsubishi', honda: 'honda', suzuki: 'suzuki', chevrolet: 'chevrolet',
  smart: 'smart', iveco: 'iveco', subaru: 'subaru', tesla: 'tesla',
  chrysler: 'chrysler', maserati: 'maserati', infiniti: 'infiniti', ferrari: 'ferrari',
  bentley: 'bentley', lamborghini: 'lamborghini', man: 'man',
  'aston-martin': 'astonmartin', cadillac: 'cadillac', scania: 'scania', daf: 'daf',
  ktm: 'ktm', vespa: 'vespa', polestar: 'polestar', lada: 'lada',
  'rolls-royce': 'rollsroyce', mahindra: 'mahindra', mclaren: 'mclaren', ram: 'ram',
  bugatti: 'bugatti', cupra: 'cupra', 'alfa-romeo': 'alfaromeo', jaguar: 'jaguar',
  lexus: 'lexus', 'land-rover': 'landrover', abarth: 'abarth', lancia: 'lancia',
  dodge: 'dodge', byd: 'byd', geely: 'geely', 'great-wall': 'greatwallmotors',
  haval: 'haval', chery: 'chery', hongqi: 'hongqi', nio: 'nio', xpeng: 'xpeng',
  wey: 'wey', lucid: 'lucidmotors', rivian: 'rivian', genesis: 'genesis',
  buick: 'buick', gmc: 'gmc', lincoln: 'lincoln', acura: 'acura', isuzu: 'isuzu',
  daihatsu: 'daihatsu', tata: 'tatamotors', ssangyong: 'ssangyong', kgm: 'ssangyong',
  saab: 'saab', rover: 'rover', 'lynk-co': 'lynkandco', zeekr: 'zeekr',
  aiways: 'aiways', leapmotor: 'leapmotor', ora: 'ora', jac: 'jac',
  changan: 'changan', baic: 'baic', dongfeng: 'dongfeng', foton: 'foton',
  yamaha: 'yamahamotorcorporation', kawasaki: 'kawasaki', ducati: 'ducati',
  aprilia: 'aprilia', piaggio: 'piaggio', triumph: 'triumph',
  'harley-davidson': 'harleydavidson', 'moto-guzzi': 'motoguzzi',
  kymco: 'kymco', sym: 'sym', hummer: 'hummer', pontiac: 'pontiac',
};

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

const results = { saved: [], skipped: [], failed: [] };

for (const [slug, icon] of Object.entries(MAP)) {
  const target = join(OUT_DIR, `${slug}.svg`);
  if (existsSync(target)) {
    results.skipped.push(slug);
    continue;
  }
  try {
    const res = await fetch(`${BASE}/${icon}.svg`);
    if (!res.ok) {
      results.failed.push(`${slug} (${icon}: HTTP ${res.status})`);
      continue;
    }
    let svg = await res.text();
    // `currentColor` lets one asset serve the selected and unselected states
    // instead of shipping two files or filtering the mark at render time.
    svg = svg.replace(/<svg /, '<svg fill="currentColor" ');
    writeFileSync(target, svg, 'utf8');
    results.saved.push(slug);
  } catch (err) {
    results.failed.push(`${slug} (${err.message})`);
  }
}

console.log(`descargados: ${results.saved.length}`);
console.log(`ya presentes: ${results.skipped.length}`);
if (results.failed.length) {
  console.log(`SIN FUENTE (${results.failed.length}): ${results.failed.join(', ')}`);
}
