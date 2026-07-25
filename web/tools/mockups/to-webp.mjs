// Convert the rendered 2x PNGs into the WebP files the site ships.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(HERE, 'out');
const DEST = path.resolve(HERE, '../../public/shots');

fs.mkdirSync(DEST, { recursive: true });

const files = fs.readdirSync(SRC).filter((f) => f.endsWith('.png'));
let before = 0;
let after = 0;

for (const file of files) {
  const from = path.join(SRC, file);
  const to = path.join(DEST, file.replace(/\.png$/, '.webp'));
  const meta = await sharp(from).metadata();
  // Rendered at 2x, so a moderate quality still resolves crisply on retina
  // while keeping the page's image budget sane.
  await sharp(from).webp({ quality: 80, effort: 6 }).toFile(to);
  const a = fs.statSync(from).size;
  const b = fs.statSync(to).size;
  before += a;
  after += b;
  console.log(
    `${file.padEnd(20)} ${meta.width}x${meta.height}  ${(a / 1024).toFixed(0)}kb -> ${(b / 1024).toFixed(0)}kb`,
  );
}

console.log(`\ntotal ${(before / 1024).toFixed(0)}kb -> ${(after / 1024).toFixed(0)}kb into ${DEST}`);
