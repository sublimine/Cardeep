// Turn the real Spain province TopoJSON into a dot matrix for the artwork.
//
// The peninsula + Balearics are laid out in the main box and the Canaries are
// placed as an inset, which is the standard convention for Spanish maps — drawing
// them at true longitude would shrink the mainland to a smudge.
//
// Output: tools/mockups/map-data.js  (plain globals, loaded by index.html)

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));

/** Both files were written by tools that prepend a BOM; strip it before parsing. */
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^﻿/, ''));

const topo = readJson(path.join(HERE, 'es-provinces.json'));
const coverage = readJson(
  path.resolve(HERE, '../../../docs/research/territorial/coverage_province.json'),
);

/* ----------------------------------------------------------- topojson ----- */

const { scale: [sx, sy], translate: [tx, ty] } = topo.transform;

/** Delta-decode one arc into absolute [lon, lat] pairs. */
const arcs = topo.arcs.map((arc) => {
  let x = 0;
  let y = 0;
  return arc.map(([dx, dy]) => {
    x += dx;
    y += dy;
    return [x * sx + tx, y * sy + ty];
  });
});

const arcPoints = (index) => (index < 0 ? arcs[~index].slice().reverse() : arcs[index]);

function ringToPoints(ring) {
  const out = [];
  for (const idx of ring) {
    const pts = arcPoints(idx);
    // Arcs share endpoints; drop the duplicate seam.
    out.push(...(out.length ? pts.slice(1) : pts));
  }
  return out;
}

/** Every province as { code, name, rings: [[lon,lat],...][] }. */
const provinces = topo.objects.provinces.geometries.map((g) => {
  const polys = g.type === 'MultiPolygon' ? g.arcs : [g.arcs];
  return {
    code: String(g.properties?.code ?? g.id ?? '').padStart(2, '0'),
    name: g.properties?.name ?? '',
    rings: polys.flatMap((poly) => poly.map(ringToPoints)),
  };
});

console.log(`provinces: ${provinces.length}`);

/* ------------------------------------------------------------ projection -- */

const CANARY = new Set(['35', '38']);
const isCanary = (p) => CANARY.has(p.code);

function bboxOf(list) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const p of list) {
    for (const ring of p.rings) {
      for (const [x, y] of ring) {
        if (x < minX) minX = x;
        if (y < minY) minY = y;
        if (x > maxX) maxX = x;
        if (y > maxY) maxY = y;
      }
    }
  }
  return { minX, minY, maxX, maxY };
}

const mainland = provinces.filter((p) => !isCanary(p));
const canaries = provinces.filter(isCanary);
const bMain = bboxOf(mainland);
const bCan = bboxOf(canaries);
console.log('mainland bbox', bMain);
console.log('canaries bbox', bCan);

/**
 * Mercator-ish latitude correction so Spain is not vertically squashed:
 * one degree of longitude is cos(lat) as wide as one of latitude.
 */
const LAT0 = ((bMain.minY + bMain.maxY) / 2) * (Math.PI / 180);
const K = Math.cos(LAT0);

function makeProjector(box, target) {
  const w = (box.maxX - box.minX) * K;
  const h = box.maxY - box.minY;
  const s = Math.min(target.w / w, target.h / h);
  const ox = target.x + (target.w - w * s) / 2;
  const oy = target.y + (target.h - h * s) / 2;
  return ([lon, lat]) => [ox + (lon - box.minX) * K * s, oy + (box.maxY - lat) * s];
}

// Mainland fills the box; the Canaries sit small in the bottom-left corner.
const projMain = makeProjector(bMain, { x: 2, y: 1, w: 96, h: 84 });
const projCan = makeProjector(bCan, { x: 2, y: 88, w: 30, h: 11 });

/* ------------------------------------------------------------ rasterise --- */

function pointInRing(px, py, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if (yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

const STEP = 1.32;
const dots = [];
for (const [list, proj] of [[mainland, projMain], [canaries, projCan]]) {
  const projected = list.map((p) => ({ ...p, rings: p.rings.map((r) => r.map(proj)) }));
  for (let y = 0; y <= 100; y += STEP) {
    for (let x = 0; x <= 100; x += STEP) {
      for (const p of projected) {
        let hit = false;
        for (const ring of p.rings) if (pointInRing(x, y, ring)) hit = !hit;
        if (hit) {
          dots.push([+x.toFixed(2), +y.toFixed(2)]);
          break;
        }
      }
    }
  }
}
console.log(`dots: ${dots.length}`);

/* --------------------------------------------- real per-province figures --- */

/**
 * The territorial research counts every discovered record, including empty ones
 * and scrapyards — the inflated definition the owner rejected. The published
 * figure is the filtered one from services/api/stats.py. Keep the real relative
 * distribution but normalise it to the published total so no screen contradicts
 * another.
 */
const PUBLISHED_DEALERS = 19048;
const rawTotal = coverage.provinces.reduce((sum, p) => sum + p.ours_all, 0);
const norm = PUBLISHED_DEALERS / rawTotal;

/**
 * `covB` compares what we hold against INE's official count of vehicle-sales
 * businesses, so it is a genuine completeness signal. Below 0.8 the province is
 * still being widened, and the artwork says so instead of rounding up.
 */
const SEALED_AT = 0.8;

const byCount = [...coverage.provinces]
  .sort((a, b) => b.ours_all - a.ours_all)
  .map((p) => ({
    code: p.code,
    // INE writes "Coruña, A" and "Rioja, La"; restore natural Spanish order.
    name: p.province.split('/')[0].replace(/^(.+), (A|La|El|Las|Los)$/, '$2 $1'),
    points: Math.round(p.ours_all * norm),
    sealed: p.covB >= SEALED_AT,
  }));

const widening = byCount.filter((p) => !p.sealed).length;
console.log(`provinces still widening (covB < ${SEALED_AT}): ${widening}`);

console.log('top provinces:', byCount.slice(0, 6).map((p) => `${p.name}=${p.points}`).join(' '));

/** Province centroid (average of its outline points) → where to plant a marker. */
const centroids = {};
for (const p of mainland.concat(canaries)) {
  const proj = isCanary(p) ? projCan : projMain;
  let sxs = 0, sys = 0, n = 0;
  for (const ring of p.rings) {
    for (const pt of ring) {
      const [x, y] = proj(pt);
      sxs += x;
      sys += y;
      n++;
    }
  }
  if (n) centroids[p.code] = [+(sxs / n).toFixed(2), +(sys / n).toFixed(2)];
}

const markers = byCount
  .slice(0, 16)
  .filter((p) => centroids[p.code])
  .map((p) => ({ x: centroids[p.code][0], y: centroids[p.code][1], name: p.name, points: p.points }));

/* The bento's coverage card renders the same geometry inside the app. */
const tsModule = `// Generated by tools/mockups/build-map.mjs from the real province TopoJSON.
// Peninsula + Balearics fill the box; the Canaries sit as an inset, the usual
// convention for Spanish maps. Coordinates are in a 0-100 viewBox.
// ${dots.length} dots across ${provinces.length} provinces — do not edit by hand.

export const SPAIN_DOTS: readonly (readonly [number, number])[] = ${JSON.stringify(dots)};

/** Province markers sized by their share of the index. */
export const SPAIN_MARKERS: readonly { x: number; y: number; name: string; points: number }[] =
  ${JSON.stringify(markers)};
`;
fs.writeFileSync(path.resolve(HERE, '../../src/components/bento/spain-map-dots.ts'), tsModule);
console.log(`spain-map-dots.ts written (${(tsModule.length / 1024).toFixed(0)}kb)`);

const out = `/* Generated by build-map.mjs from the real province TopoJSON — do not edit. */
window.SPAIN_DOTS = ${JSON.stringify(dots)};
window.SPAIN_MARKERS = ${JSON.stringify(markers)};
window.SPAIN_TOP = ${JSON.stringify(byCount.slice(0, 8))};
window.SPAIN_TOTAL = ${PUBLISHED_DEALERS};
`;
fs.writeFileSync(path.join(HERE, 'map-data.js'), out);
console.log(`map-data.js written (${(out.length / 1024).toFixed(0)}kb)  markers=${markers.length}`);
