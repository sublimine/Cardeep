/**
 * Self-host the logos of the seven platforms Cardeep indexes.
 *
 * Measured before this existed: public/logos/ held 130 marque SVGs and ZERO
 * platform marks. The national index therefore rendered CAR marques — Audi,
 * BMW, Mercedes — in a rail that is supposed to name PLATFORMS. That was not a
 * missing asset, it was the wrong subject: the rail answers "where does Cardeep
 * read stock from", and a marque logo cannot answer it.
 *
 * Why this file is not a clone of fetch-brand-logos.mjs: there is no Simple
 * Icons for these. simple-icons has no autoscout24 and no wallapop, and
 * logo.clearbit.com is dead (returns 000). Every mark here was tracked down one
 * at a time, and the four routes that actually worked are all represented below:
 *
 *   1. Wikimedia Commons, for marks whose upload is public domain because the
 *      lockup sits below the threshold of originality (AutoScout24).
 *   2. The platform's OWN CDN, read out of its live header (Milanuncios,
 *      Autocasion, coches.com, motor.es, Wallapop).
 *   3. A header that inlines the mark as a base64 data URI rather than serving
 *      a file at all (coches.net) — no URL to curl, so it is embedded here.
 *   4. A second property of the same company, when the main site publishes only
 *      one polarity (coches.net PRO evidences the negative treatment).
 *
 * Three traps this script exists to remember, all of them found by RENDERING
 * the results rather than trusting a 200:
 *
 *   - Several platforms serve ONLY the variant their own header needs.
 *     Autocasion and motor.es both ship a white-on-transparent mark, which is
 *     invisible on a light background. In both cases the opposite polarity was
 *     sitting in the same folder under a guessable name. Always probe.
 *   - A 200 does not mean an image. Autocasion's CDN answers 404s with an HTML
 *     body, and AutoScout24's WAF answers unknown asset names with a 403 HTML
 *     page ~21KB long. Both would save happily as ".svg". Hence verify().
 *   - The Wikimedia SVG for Wallapop had its artwork filling only 72%x47% of
 *     its viewBox, so it rendered visibly smaller than every neighbour in the
 *     rail. Bytes and HTTP status say nothing about that; only measuring the
 *     ink bounding box does.
 *
 * Nothing here is drawn, traced or approximated. The single derived file is
 * coches.net's negative, and it is one colour substitution on the official
 * artwork — documented at DERIVED below.
 *
 * Run: node tools/fetch-platform-logos.mjs
 */
import { writeFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = join(here, '..', 'public', 'logos', 'platforms');

/**
 * Wikimedia rate-limits generic clients hard — the API starts answering "You
 * are making too many requests" within a handful of calls. A descriptive
 * User-Agent is their documented requirement, not a disguise, and the platform
 * CDNs also refuse a bare curl signature.
 */
const UA =
  'CardeepLogoFetcher/1.0 (https://cardeep.vercel.app; contacto via repo) ' +
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36';

/**
 * `file` is what lands on disk. `onDark` is a second, OFFICIAL polarity where
 * the platform publishes one — not a filter, not an invention. A landing that
 * reads in both themes needs both, and half of these brands ship both already.
 */
const PLATFORMS = [
  {
    name: 'coches.net',
    file: 'coches-net.svg',
    // No URL: coches.net inlines its wordmark as a base64 data URI inside the
    // server-rendered header (a.sui-TopbarUser-brand img). It is in neither the
    // JS bundle nor any /images path — every logo-ish filename under
    // s.ccdn.es/images/coches/ and /images/common/logos/ returns 404. The
    // payload is therefore carried here verbatim, exactly as coches.net serves it.
    inlineBase64: true,
    source: 'https://www.coches.net/',
  },
  {
    name: 'AutoScout24',
    file: 'autoscout24.svg',
    // Public domain on Commons. This is the POSITIVE lockup: yellow tab plus a
    // #333 "Scout24". AutoScout24's own site never serves it — their header is
    // dark, so they only ship the inverse (see onDark).
    url: 'https://upload.wikimedia.org/wikipedia/commons/f/fe/AutoScout24_Logo_horizontal_%282022%29.svg',
    onDark: {
      file: 'autoscout24-light.svg',
      // Content-hashed: this exact URL dies whenever AutoScout24 redeploys. To
      // refresh it, load autoscout24.es and read the src of a#as24-logo img.
      url: 'https://www.autoscout24.es/assets/as24-header-footer/as24-horizontal-inverse.19d65360.svg',
    },
  },
  {
    name: 'Wallapop',
    file: 'wallapop.svg',
    url: 'https://web-static.wallapop.com/nextjs/_next/static/media/wallapop-logo.a8a98573.svg',
    // Wallapop declares width/height but no viewBox, so the mark cannot scale:
    // set a CSS height and the SVG keeps its 182x40 intrinsic box. The viewBox
    // added here is the one its own attributes already imply. No coordinate,
    // path or colour is touched.
    addViewBoxFromSize: true,
  },
  {
    name: 'Milanuncios',
    file: 'milanuncios.svg',
    url: 'https://scm-milanuncios-frontend-pro.milanuncios.com/statics/images/common/logo.svg',
  },
  {
    name: 'Autocasión',
    file: 'autocasion.svg',
    // Their header serves logo-white.svg, which vanishes on a light surface.
    // The colour version was in the same folder under the plainer name.
    url: 'https://assets0.autocasion.com/ao-assets/img/logo.svg',
  },
  {
    name: 'coches.com',
    file: 'coches-com.svg',
    url: 'https://images.coches.com/_static_/cochescom/logos/logo.svg',
    onDark: {
      file: 'coches-com-light.svg',
      url: 'https://images.coches.com/_static_/cochescom/logos/logotipo-coches-light.svg',
    },
  },
  {
    name: 'motor.es',
    file: 'motor-es.svg',
    // Same trap as Autocasion, mirrored: the header serves -negativo, and
    // -positivo sits beside it. motor.es's own JSON-LD Organization block names
    // this artwork as the company image, which is as official as it gets.
    url: 'https://static.motor.es/imagenes/svg/motor-es-positivo.svg',
    onDark: {
      file: 'motor-es-light.svg',
      url: 'https://static.motor.es/imagenes/svg/motor-es-negativo.svg',
    },
  },
];

/**
 * The coches.net wordmark, byte for byte as coches.net's own header serves it:
 * "coches" in #000E23, ".net" in #E60E27, viewBox 0 0 130 20.
 */
const COCHES_NET_B64 =
  'PHN2ZyB2aWV3Qm94PSIwIDAgMTMwIDIwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxnIGNsaXAtcGF0aD0idXJsKCNhKSI+PHBhdGggZD0iTTEzLjkwOSAxMy42MjFoLTMuMjQ4di4wM2MtLjMzNiAxLjQxMS0xLjc3IDIuNDQyLTMuNDMyIDIuNDQyLTIuMzE4IDAtNC4wNTctMS44MzUtNC4wNTctNC4yNjIgMC0yLjQ0MiAxLjczOS00LjI5MiA0LjA1Ny00LjI5MiAxLjYzMiAwIDMuMDk2IDEgMy40MDEgMi4zMzZ2LjAzaDMuMjc5di0uMDQ2QzEzLjQ4MiA2Ljg0MSAxMC42MyA0LjU1IDcuMjc1IDQuNTUgMy4yMDMgNC41NSAwIDcuNzUxIDAgMTEuODQ2YzAgMi4wMDMuNzQ3IDMuODM4IDIuMTIgNS4xODggMS4zNTcgMS4zMzUgMy4xODcgMi4wNzggNS4xNyAyLjA3OCAzLjQ3NyAwIDYuMjY4LTIuMjkgNi42MzQtNS40M2wtLjAxNS0uMDZabTEzLjkwOS02Ljk0N2E3LjMxIDcuMzEgMCAwIDAtNS4xODUtMi4xMjRjLTQuMTE4IDAtNy4zMzYgMy4yMDEtNy4zMzYgNy4yOTYgMCA0LjA4IDMuMjE4IDcuMjY2IDcuMzM2IDcuMjY2IDQuMTE3IDAgNy4zMzUtMy4xODUgNy4zMzUtNy4yNjZhNy4xOSA3LjE5IDAgMCAwLTIuMTUtNS4xNzJabS01LjE4NSA5LjQ1Yy0yLjM4IDAtNC4xNjQtMS44NS00LjE2NC00LjI5MyAwLTIuNDU3IDEuOC00LjMyMyA0LjE2NC00LjMyMyAyLjMzMyAwIDQuMTYzIDEuODk2IDQuMTYzIDQuMzIzIDAgMi40MTItMS44MyA0LjI5My00LjE2MyA0LjI5M1ptMjIuNzg1LTIuNTAzaC0zLjI0OXYuMDNjLS4zMzUgMS40MTEtMS43NjkgMi40NDItMy40MzEgMi40NDItMi4zMTkgMC00LjA1Ny0xLjgzNS00LjA1Ny00LjI2MiAwLTIuNDQyIDEuNzM5LTQuMjkyIDQuMDU3LTQuMjkyIDEuNjMyIDAgMy4wOTYgMSAzLjQgMi4zMzZ2LjAzaDMuMjh2LS4wNDZjLS40MjctMy4wMTgtMy4yOC01LjMwOS02LjYzNS01LjMwOS00LjA4NyAwLTcuMjc0IDMuMjAxLTcuMjc0IDcuMjk2IDAgMi4wMDMuNzQ3IDMuODM4IDIuMTIgNS4xODggMS4zNTcgMS4zMzUgMy4xODcgMi4wNzggNS4xNyAyLjA3OCAzLjQ3NyAwIDYuMjY4LTIuMjkgNi42MzQtNS40M2wtLjAxNS0uMDZabTguNTU2LTYuMDk4YzEuODMgMCAzLjAwNCAxLjMyIDMuMDA0IDMuMzY4djcuODU3aDMuMjQ4VjEwLjhjMC0zLjc5Mi0yLjE2NS02LjI1LTUuNTItNi4yNWE1LjYzIDUuNjMgMCAwIDAtMy45NjYgMS42NGwtLjA3Ni4wNzVWMGgtMy4xNTd2MTguNzQ4aDMuMjE4di03LjY5YzAtMi4xMDkgMS4zMTItMy41MzUgMy4yNDgtMy41MzVaTTY5LjU5IDQuNTVjLTQuMDEgMC03LjI3NCAzLjMzNy03LjI3NCA3LjQzMyAwIDQuMDY1IDMuMDggNy4xMjkgNy4xNjggNy4xMjkgMy4zMSAwIDYuMDI0LTEuOTExIDYuNzQtNC43NDhsLjAxNi0uMDQ1aC0zLjE4OGwtLjAxNS4wM2MtLjM2NiAxLjIxNC0xLjcwOCAyLjAxNy0zLjM1NSAyLjAxNy0yLjE2NiAwLTMuODU5LTEuNDU2LTQuMTc5LTMuNjF2LS4wNDVoMTAuNzgzdi0uMDNjLjA3Ni0uNTQ2LjEwNi0xLjAxNy4xMDYtMS40MTEgMC0zLjc3Ny0yLjk4OS02LjcyLTYuODAxLTYuNzJabS0zLjg3MyA1LjUwNi4wMTUtLjA2Yy42NC0xLjY2OSAyLjEyLTIuNyAzLjg0My0yLjcgMS44MyAwIDMuMzI1IDEuMTY4IDMuNDc3IDIuNzE1di4wNDZoLTcuMzM1Wm0xOC42MDYuMjI4LjAxNS0uMDQ1LS4wMTUuMDQ1Yy0xLjYxNi0uMzM0LTMuMDA0LS42MjItMy4wMDQtMS43MyAwLTEuMTUyIDEuMTU5LTEuNTYxIDIuMTY1LTEuNTYxIDEuMjgxIDAgMi4zMDMuNzQzIDIuNDcxIDEuODJ2LjAzaDMuMTU3di0uMDQ1Qzg4LjgzNyA2LjE3MyA4Ni42ODcgNC41NSA4My41IDQuNTVjLTMuMDY2IDAtNS4yMTYgMS43NzUtNS4yMTYgNC4zMDggMCAyLjk0MyAyLjY2OSAzLjU2NSA0LjgxOSA0LjA1IDEuNjc4LjM4IDMuMTExLjcxMyAzLjExMSAxLjk0MiAwIDEuMDQ2LS45NDUgMS43MjktMi40MjUgMS43MjktMS41MjUgMC0yLjU5Mi0uODItMi43LTIuMDkzdi0uMDNoLTMuMDh2LjA0NWMuMjI5IDIuODUxIDIuNDQgNC42MjYgNS43OCA0LjYyNiAzLjI2NCAwIDUuNTUyLTEuODk2IDUuNTUyLTQuNjI2LjA0Ni0zLjE3LTIuNzYtMy43NDctNS4wMTgtNC4yMTdaIiBmaWxsPSIjMDAwRTIzIi8+PHBhdGggZD0iTTExNC4yMyA0LjU1Yy00LjAxMSAwLTcuMjc0IDMuMzM3LTcuMjc0IDcuNDMzIDAgNC4wNjUgMy4wOCA3LjEyOSA3LjE2OCA3LjEyOSAzLjMwOSAwIDYuMDI0LTEuOTExIDYuNzQxLTQuNzQ4bC4wMTUtLjA0NWgtMy4xODhsLS4wMTUuMDNjLS4zNjYgMS4yMTQtMS43MDggMi4wMTctMy4zNTUgMi4wMTctMi4xNjYgMC0zLjg1OS0xLjQ1Ni00LjE3OS0zLjYxdi0uMDQ1aDEwLjc4M3YtLjAzYy4wNzYtLjU0Ni4xMDYtMS4wMzIuMTA2LTEuNDExLS4wMTUtMy43NzctMi45ODktNi43Mi02LjgwMi02LjcyWm0tMy44NzMgNS41MDYuMDE1LS4wNmMuNjQtMS42NjkgMi4xMi0yLjcgMy44NDMtMi43IDEuODMgMCAzLjMyNSAxLjE2OCAzLjQ3NyAyLjcxNXYuMDQ2aC03LjMzNVptMTcuNTM4IDguNjkySDEzMHYtMi44MjFoLTEuNzA4Yy0xLjMyNyAwLTEuOTk4LS42OTgtMS45OTgtMi4wNjNWNy43MkgxMzBWNC45MTVoLTMuNzA2Vi45NTVoLTMuMjE4djEzLjEzNmMwIDMuMTI1IDEuNTg2IDQuNjU3IDQuODE5IDQuNjU3Wk05Ni41MDkgMTYuNjFhMi41ODQgMi41ODQgMCAwIDEtMi41OTMgMi41NzggMi41ODMgMi41ODMgMCAwIDEtMi41OTMtMi41NzkgMi41ODMgMi41ODMgMCAwIDEgMi41OTMtMi41NzggMi41ODQgMi41ODQgMCAwIDEgMi41OTMgMi41NzhaTTkyLjMxNSA0LjkzaDMuMDk2djEuNDFjMS4wNTItMS4xMDcgMi40Ny0xLjc3NCA0LjA4Ny0xLjc3NCAzLjI2NCAwIDUuNTA2IDIuMzY2IDUuNTA2IDYuMjM0djcuOTMzaC0zLjE3M1YxMC44OWMwLTEuOTQyLTEuMTEzLTMuNDEzLTMuMDY1LTMuNDEzLTEuOTA3IDAtMy4yOTQgMS4zOC0zLjI5NCAzLjU4di42OTdoLTMuMTU3VjQuOTNaIiBmaWxsPSIjRTYwRTI3Ii8+PC9nPjxkZWZzPjxjbGlwUGF0aCBpZD0iYSI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTAgMGgxMzB2MTkuMTczSDB6Ii8+PC9jbGlwUGF0aD48L2RlZnM+PC9zdmc+';

/**
 * The one derived file in this directory, and the reason it is allowed.
 *
 * coches.net publishes no negative of the plain wordmark. Every candidate path
 * under their CDN 404s, the JS bundle carries no second variant, and
 * /corporativo and /prensa answer 405. What their PRO portal DOES serve is the
 * same wordmark in negative — white letters, the same #E60E27 suffix, identical
 * letterforms — which settles what the official negative treatment is. That
 * asset is not reused directly because it carries the PRO badge, a different
 * sub-brand that has no business in a marketplace index.
 *
 * So the negative is produced by swapping one ink value on the official
 * artwork. No path data is altered. This is the only file here that is not a
 * byte-for-byte download, and it is flagged as derived in the manifest so it
 * can never be mistaken for one.
 */
const DERIVED = [
  {
    from: 'coches-net.svg',
    to: 'coches-net-light.svg',
    replace: ['#000E23', '#FFFFFF'],
    evidence: 'https://pro.coches.net/',
  },
];

/**
 * A 200 is not an image. Autocasion answers missing assets with an HTML body,
 * and AutoScout24's WAF answers an unknown asset name with a 21KB HTML 403 —
 * both of which would sit on disk as a perfectly convincing ".svg" until the
 * rail rendered blank. Check the bytes, not the status line.
 */
function verify(name, buf) {
  const head = buf.subarray(0, 1024).toString('utf8').toLowerCase();
  if (head.includes('<!doctype html') || head.includes('<html')) {
    return `${name}: HTML disfrazado de imagen (pagina de error), ${buf.length} bytes`;
  }
  const text = buf.toString('utf8');
  if (!text.includes('<svg')) return `${name}: sin elemento <svg>, ${buf.length} bytes`;
  if (!/viewBox=|width=/.test(text)) return `${name}: <svg> sin viewBox ni width`;
  if (buf.length < 400) return `${name}: solo ${buf.length} bytes, demasiado pequeno para un logotipo`;
  return null;
}

/** Give the mark the viewBox its own width/height already imply. */
function addViewBoxFromSize(svg) {
  if (/viewBox=/.test(svg)) return svg;
  const open = svg.match(/<svg([^>]*)>/);
  if (!open) return svg;
  const w = open[1].match(/width="([\d.]+)"/);
  const h = open[1].match(/height="([\d.]+)"/);
  if (!w || !h) return svg;
  return svg.replace('<svg ', `<svg viewBox="0 0 ${w[1]} ${h[1]}" `, 1);
}

async function download(url) {
  const res = await fetch(url, { headers: { 'User-Agent': UA, 'Accept-Language': 'es-ES,es;q=0.9' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return Buffer.from(await res.arrayBuffer());
}

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

const results = { saved: [], skipped: [], failed: [] };

/** One asset: fetch (or decode), normalise, verify, write. */
async function acquire(label, target, spec) {
  const path = join(OUT_DIR, target);
  if (existsSync(path)) {
    results.skipped.push(target);
    return;
  }
  try {
    let buf = spec.inlineBase64
      ? Buffer.from(COCHES_NET_B64, 'base64')
      : await download(spec.url);

    if (spec.addViewBoxFromSize) buf = Buffer.from(addViewBoxFromSize(buf.toString('utf8')), 'utf8');

    const problem = verify(label, buf);
    if (problem) {
      results.failed.push(problem);
      return;
    }
    writeFileSync(path, buf);
    results.saved.push(`${target} (${buf.length}b)`);
  } catch (err) {
    results.failed.push(`${label} -> ${target}: ${err.message}`);
  }
}

for (const p of PLATFORMS) {
  await acquire(p.name, p.file, p);
  if (p.onDark) await acquire(`${p.name} (negativo)`, p.onDark.file, p.onDark);
}

// Derived files run last: they read a file the loop above just wrote.
for (const d of DERIVED) {
  const target = join(OUT_DIR, d.to);
  if (existsSync(target)) {
    results.skipped.push(d.to);
    continue;
  }
  const sourcePath = join(OUT_DIR, d.from);
  if (!existsSync(sourcePath)) {
    results.failed.push(`${d.to}: falta el origen ${d.from}`);
    continue;
  }
  const src = readFileSync(sourcePath, 'utf8');
  const [from, to] = d.replace;
  // Refuse to guess. If the ink value is not there exactly once, the upstream
  // artwork has changed and the substitution must be re-checked by a human
  // rather than applied blind to whatever happens to match.
  const hits = src.split(from).length - 1;
  if (hits !== 1) {
    results.failed.push(`${d.to}: se esperaba ${from} exactamente 1 vez, encontrado ${hits} — revisar a mano`);
    continue;
  }
  const out = src.replace(from, to);
  writeFileSync(target, out, 'utf8');
  results.saved.push(`${d.to} (${Buffer.byteLength(out)}b, DERIVADO de ${d.from})`);
}

console.log(`descargados: ${results.saved.length}`);
for (const s of results.saved) console.log(`  + ${s}`);
console.log(`ya presentes: ${results.skipped.length}`);
if (results.failed.length) {
  console.log(`\nSIN FUENTE (${results.failed.length}):`);
  for (const f of results.failed) console.log(`  ! ${f}`);
  console.log(
    '\nUn hueco honesto vale mas que una marca falsa: registra el hueco en\n' +
      'src/landing-v4/data/platform-logos.json con file en null antes que rellenarlo.'
  );
}
