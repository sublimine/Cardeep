// Report public assets no source file references, so dead weight from the
// template can be deleted rather than shipped.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const WEB = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PUBLIC = path.join(WEB, 'public');

function walk(dir, base = dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const full = path.join(dir, e.name);
    return e.isDirectory() ? walk(full, base) : ['/' + path.relative(base, full).replace(/\\/g, '/')];
  });
}

/** Every source file that could reference an asset. */
const sources = [
  ...walk(path.join(WEB, 'src')).map((p) => path.join(WEB, 'src', p)),
  path.join(WEB, 'index.html'),
];
const haystack = sources.map((f) => fs.readFileSync(f, 'utf8')).join('\n');

const assets = walk(PUBLIC);
const unused = assets.filter((a) => {
  // Fonts are referenced from fonts.css by filename; check the basename too.
  const base = a.split('/').pop();
  return !haystack.includes(a) && !haystack.includes(base);
});

const used = assets.length - unused.length;
console.log(`assets: ${assets.length}   referenced: ${used}   unreferenced: ${unused.length}\n`);

const byDir = new Map();
let bytes = 0;
for (const a of unused) {
  const dir = a.split('/').slice(0, -1).join('/') || '/';
  byDir.set(dir, (byDir.get(dir) ?? 0) + 1);
  bytes += fs.statSync(path.join(PUBLIC, a)).size;
}
for (const [dir, n] of [...byDir].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(n).padStart(4)}  ${dir || '/'}`);
}
console.log(`\nreclaimable: ${(bytes / 1024).toFixed(0)} kb`);
fs.writeFileSync(path.join(WEB, 'tools', 'unused-assets.txt'), unused.join('\n'));
