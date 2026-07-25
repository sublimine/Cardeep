// Replace the text-placeholder logo sources with real brand artwork.
//
// A previous pass fell back to typesetting the brand name for marks it could not
// find. Those are not logos, so this re-sources them: Simple Icons first, then
// Wikimedia Commons, writing into `fixed/` which the sprite builder prefers.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, 'fixed');
fs.mkdirSync(OUT, { recursive: true });

const catalog = JSON.parse(
  fs.readFileSync(path.join(HERE, 'catalog.source.json'), 'utf8').replace(/^﻿/, ''),
);

/** A source is degraded when it draws no shapes, or draws the brand name as text. */
function isDegraded(file) {
  if (!file.endsWith('.svg')) return false;
  const text = fs.readFileSync(file, 'utf8');
  const shapes = (text.match(/<(path|polygon|circle|rect|ellipse|use)\b/g) || []).length;
  return shapes === 0 || /<text[\s>]/.test(text) || text.length < 400;
}

const UA = { 'User-Agent': 'cardeep-brand-wall/1.0 (https://cardeep.vercel.app)' };

async function trySimpleIcons(make) {
  const slugs = [
    make.slug.replace(/-/g, ''),
    make.slug,
    make.name.toLowerCase().replace(/[^a-z0-9]/g, ''),
  ];
  for (const slug of slugs) {
    try {
      const res = await fetch(`https://cdn.simpleicons.org/${slug}`, { headers: UA });
      if (!res.ok) continue;
      const svg = await res.text();
      if (svg.startsWith('<svg') && /<path/.test(svg)) return svg;
    } catch {
      /* try the next spelling */
    }
  }
  return null;
}

async function tryCommons(make) {
  const queries = [`${make.name} logo`, `${make.name} car logo`, `${make.name} automobile logo`];
  for (const query of queries) {
    try {
      const api =
        'https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*' +
        '&generator=search&gsrnamespace=6&gsrlimit=8&prop=imageinfo&iiprop=url|mime' +
        `&gsrsearch=${encodeURIComponent(`${query} filetype:svg`)}`;
      const res = await fetch(api, { headers: UA });
      if (!res.ok) continue;
      const json = await res.json();
      const pages = Object.values(json?.query?.pages ?? {});
      for (const page of pages) {
        const info = page.imageinfo?.[0];
        if (!info?.url?.endsWith('.svg')) continue;
        const file = await fetch(info.url, { headers: UA });
        if (!file.ok) continue;
        const svg = await file.text();
        const shapes = (svg.match(/<(path|polygon|circle|rect|ellipse)\b/g) || []).length;
        if (shapes > 0 && svg.length > 500) return svg;
      }
    } catch {
      /* try the next phrasing */
    }
  }
  return null;
}

const degraded = catalog.filter((make) => {
  const local = path.join(HERE, 'local', `${make.slug}.svg`);
  return fs.existsSync(local) && isDegraded(local);
});

console.log(`degraded sources: ${degraded.length}`);

let fixed = 0;
const stillBad = [];
for (const make of degraded) {
  const svg = (await trySimpleIcons(make)) ?? (await tryCommons(make));
  if (svg) {
    fs.writeFileSync(path.join(OUT, `${make.slug}.svg`), svg);
    fixed++;
    console.log(`  ok    ${make.slug}`);
  } else {
    stillBad.push(make.slug);
    console.log(`  MISS  ${make.slug}`);
  }
}

console.log(`\nre-sourced ${fixed}/${degraded.length}`);
if (stillBad.length) console.log(`still typographic: ${stillBad.join(', ')}`);
