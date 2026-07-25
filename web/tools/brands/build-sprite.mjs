// Normalise all 135 vehicle marks into one alpha sprite.
//
// The wall has to read as a single system, so every mark is reduced to its
// silhouette and scaled optically — fitted by height, capped by width — rather
// than to its raw bounding box, which would make wordmarks tower over badges.
// Painting the sprite as a CSS mask lets one asset serve both themes and the
// per-brand hover colour.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const WEB = path.resolve(HERE, '../..');

const catalog = JSON.parse(
  fs.readFileSync(path.join(HERE, 'catalog.source.json'), 'utf8').replace(/^﻿/, ''),
);

/** Device-pixel cell. Rendered at 2x the CSS box the wall uses. */
const CELL_W = 240;
const CELL_H = 120;
const COLS = 12;

/** Optical budget inside a cell — marks never touch the edges. */
const MAX_H = 76;
const MAX_W = 184;

const TRANSPARENT = { r: 255, g: 255, b: 255, alpha: 0 };

/** `fixed/` holds re-sourced artwork and the hand-set wordmarks, so it wins. */
function sourceFor(make) {
  for (const ext of ['svg', 'png']) {
    const fixed = path.join(HERE, 'fixed', `${make.slug}.${ext}`);
    if (fs.existsSync(fixed)) return fixed;
  }
  const si = path.join(HERE, 'si', `${make.slug}.svg`);
  if (fs.existsSync(si)) return si;
  for (const ext of ['svg', 'png', 'webp', 'jpg']) {
    const local = path.join(HERE, 'local', `${make.slug}.${ext}`);
    if (fs.existsSync(local)) return local;
  }
  return null;
}

/**
 * Some exported SVGs declare an empty `<clipPath>` and then reference it, which
 * clips the whole drawing away. Drop references to any clip path that has no
 * children so the artwork survives.
 */
function repairSvg(file) {
  const text = fs.readFileSync(file, 'utf8');
  const empty = new Set();
  for (const match of text.matchAll(/<clipPath id="([^"]+)"\s*>\s*<\/clipPath>/g)) {
    empty.add(match[1]);
  }
  if (empty.size === 0) return Buffer.from(text);
  let repaired = text;
  for (const id of empty) {
    repaired = repaired.replaceAll(`clip-path="url(#${id})"`, '');
  }
  return Buffer.from(repaired);
}

/** Source sharp accepts: a repaired buffer for SVGs, the path otherwise. */
function inputFor(file) {
  return file.endsWith('.svg') ? repairSvg(file) : file;
}

/** Rasterise SVGs near 1400px on their longest side; a fixed density either
 *  blurs small viewBoxes or blows past sharp's pixel ceiling on large ones. */
async function loadOptions(file) {
  if (!file.endsWith('.svg')) return { limitInputPixels: false };
  const probe = await sharp(inputFor(file), { density: 72, limitInputPixels: false }).metadata();
  const longest = Math.max(probe.width ?? 512, probe.height ?? 512);
  const density = Math.max(72, Math.min(1200, Math.round((1400 / longest) * 72)));
  return { density, limitInputPixels: false };
}

/**
 * Produce an RGBA buffer whose alpha is the mark and whose colour is white.
 *
 * Sources that already carry alpha keep theirs. Flat sources — a logo printed
 * on solid white — have their ink keyed out of the luminance instead, which is
 * the only signal those files actually contain.
 */
async function toSilhouette(file) {
  const opts = await loadOptions(file);
  const input = inputFor(file);
  const meta = await sharp(input, opts).metadata();

  if (meta.hasAlpha) {
    // Flatten colour away but keep the alpha: white ink, original shape.
    const { data, info } = await sharp(input, opts)
      .ensureAlpha()
      .raw()
      .toBuffer({ resolveWithObject: true });
    const out = Buffer.alloc(info.width * info.height * 4);
    for (let i = 0; i < info.width * info.height; i++) {
      out[i * 4] = 255;
      out[i * 4 + 1] = 255;
      out[i * 4 + 2] = 255;
      out[i * 4 + 3] = data[i * info.channels + 3];
    }
    return sharp(out, { raw: { width: info.width, height: info.height, channels: 4 } });
  }

  const { data, info } = await sharp(input, opts)
    .greyscale()
    .raw()
    .toBuffer({ resolveWithObject: true });
  const out = Buffer.alloc(info.width * info.height * 4);
  for (let i = 0; i < info.width * info.height; i++) {
    // Darker pixel -> more ink. Slight lift so near-white paper reads as empty.
    const ink = Math.max(0, Math.min(255, Math.round((255 - data[i * info.channels]) * 1.25)));
    out[i * 4] = 255;
    out[i * 4 + 1] = 255;
    out[i * 4 + 2] = 255;
    out[i * 4 + 3] = ink < 18 ? 0 : ink;
  }
  return sharp(out, { raw: { width: info.width, height: info.height, channels: 4 } });
}

/** Crop to the alpha bounding box — sharp's trim keys on colour, which is
 *  useless here because every pixel is white. */
async function cropToInk(image) {
  const { data, info } = await image.png().toBuffer({ resolveWithObject: true });
  const { data: raw, info: rawInfo } = await sharp(data)
    .raw()
    .toBuffer({ resolveWithObject: true });
  let minX = rawInfo.width;
  let minY = rawInfo.height;
  let maxX = -1;
  let maxY = -1;
  for (let y = 0; y < rawInfo.height; y++) {
    for (let x = 0; x < rawInfo.width; x++) {
      if (raw[(y * rawInfo.width + x) * rawInfo.channels + 3] > 12) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  if (maxX < 0) throw new Error('no ink');
  const width = maxX - minX + 1;
  const height = maxY - minY + 1;
  // Return the box explicitly: sharp's metadata() describes the pipeline's
  // input, so asking the cropped instance would report the pre-crop size and
  // every optical scale below would be wrong.
  return {
    image: sharp(data).extract({ left: minX, top: minY, width, height }),
    width,
    height,
  };
}

const entries = [];
const missing = [];

for (const make of catalog) {
  const file = sourceFor(make);
  if (!file) {
    missing.push(make.slug);
    continue;
  }
  try {
    const cropped = await cropToInk(await toSilhouette(file));

    let scale = MAX_H / cropped.height;
    if (cropped.width * scale > MAX_W) scale = MAX_W / cropped.width;
    const w = Math.max(1, Math.min(MAX_W, Math.round(cropped.width * scale)));
    const h = Math.max(1, Math.min(MAX_H, Math.round(cropped.height * scale)));

    const cell = await cropped.image
      .resize(w, h)
      .extend({
        top: Math.floor((CELL_H - h) / 2),
        bottom: CELL_H - h - Math.floor((CELL_H - h) / 2),
        left: Math.floor((CELL_W - w) / 2),
        right: CELL_W - w - Math.floor((CELL_W - w) / 2),
        background: TRANSPARENT,
      })
      .png()
      .toBuffer();

    entries.push({ slug: make.slug, name: make.name, color: make.color, cell });
  } catch (error) {
    missing.push(`${make.slug} (${error.message})`);
  }
}

const rows = Math.ceil(entries.length / COLS);
console.log(`marks: ${entries.length}  grid: ${COLS}x${rows}  missing: ${missing.length}`);
if (missing.length) console.log('  ' + missing.join(', '));

const sprite = sharp({
  create: {
    width: COLS * CELL_W,
    height: rows * CELL_H,
    channels: 4,
    background: TRANSPARENT,
  },
}).composite(
  entries.map((entry, index) => ({
    input: entry.cell,
    left: (index % COLS) * CELL_W,
    top: Math.floor(index / COLS) * CELL_H,
  })),
);

const dest = path.join(WEB, 'public/brand/marks.webp');
fs.mkdirSync(path.dirname(dest), { recursive: true });
await sprite.webp({ quality: 90, alphaQuality: 100, effort: 6 }).toFile(dest);
console.log(`sprite -> ${dest} (${(fs.statSync(dest).size / 1024).toFixed(0)}kb)`);

const module_ = `// Generated by tools/brands/build-sprite.mjs — do not edit.
// ${entries.length} vehicle marks in one alpha sprite, painted as a CSS mask so a
// single asset serves both themes and the per-brand hover colour.

export const MARK_COLS = ${COLS};
export const MARK_ROWS = ${rows};
/** CSS size of one cell; the sprite itself is rendered at 2x. */
export const MARK_CELL = { width: ${CELL_W / 2}, height: ${CELL_H / 2} } as const;

export type VehicleMark = {
  readonly slug: string;
  readonly name: string;
  /** Official brand colour, used on hover. */
  readonly color: string;
  readonly col: number;
  readonly row: number;
};

export const VEHICLE_MARKS: readonly VehicleMark[] = [
${entries
  .map(
    (entry, index) =>
      `  { slug: '${entry.slug}', name: ${JSON.stringify(entry.name)}, color: '${entry.color}', col: ${index % COLS}, row: ${Math.floor(index / COLS)} },`,
  )
  .join('\n')}
];
`;
const modulePath = path.join(WEB, 'src/content/vehicle-marks.ts');
fs.writeFileSync(modulePath, module_);
console.log(`manifest -> ${modulePath} (${entries.length} marks)`);
