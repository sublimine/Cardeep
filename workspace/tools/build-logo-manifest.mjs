/**
 * Generate the logo manifest FROM DISK.
 *
 * `logo-ar.json` used to be maintained by hand, and the failure mode is the one
 * that already happened: twenty assets were retired and the file kept naming them,
 * so every brand row for Land Rover, Jaecoo, BAIC, Lotus and INEOS — 16.425 cars
 * between them — issued a hard 404 before falling back. A hand-written index of a
 * directory is a second source of truth for something the filesystem already knows.
 *
 * This makes the directory the only source. A file that is not there cannot be
 * named, and a file that is added is picked up without anyone remembering to.
 *
 * The aspect ratio is read from each SVG's own viewBox rather than assumed. Marque
 * marks range from roughly 1:1 to 7:1, and a column of logos only lines up if the
 * renderer knows which is which.
 *
 * Run: node tools/build-logo-manifest.mjs   (wired into `npm run landing:css`)
 */
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const LOGO_DIR = join(here, '..', 'public', 'logos');
const OUT = join(here, '..', 'src', 'landing-v4', 'data', 'logo-ar.json');

const VIEWBOX = /viewBox\s*=\s*["']\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)/i;
const WH = /<svg[^>]*\swidth\s*=\s*["']([\d.]+)[^>]*\sheight\s*=\s*["']([\d.]+)/i;

function aspectRatio(path) {
  try {
    const svg = readFileSync(path, 'utf8');
    const m = VIEWBOX.exec(svg) ?? WH.exec(svg);
    if (!m) return 1;
    const [w, h] = [Number(m[1]), Number(m[2])];
    return h > 0 ? Number((w / h).toFixed(3)) : 1;
  } catch {
    return 1;
  }
}

const files = readdirSync(LOGO_DIR, { withFileTypes: true })
  .filter((e) => e.isFile() && /\.(svg|png|webp)$/i.test(e.name))
  .map((e) => e.name)
  .sort();

const manifest = Object.fromEntries(
  files.map((name) => [
    name,
    /\.svg$/i.test(name) ? aspectRatio(join(LOGO_DIR, name)) : 1,
  ]),
);

writeFileSync(OUT, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
console.log(`logo-manifest  ${files.length} assets -> src/landing-v4/data/logo-ar.json`);
