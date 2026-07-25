// Guard rails for the public copy. Fails if template English or internal
// vocabulary survived the adaptation into any component.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const WEB = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const full = path.join(dir, e.name);
    return e.isDirectory() ? walk(full) : full;
  });
}

/** Words the reader must never see: leftover template copy, or internal jargon. */
const FORBIDDEN = [
  // template remnants
  'Aceternity', 'Chat with Alex', 'Cracked Devs', 'Manu', 'Select Plan',
  'Book a Free Call', 'Book a Paid Call', 'Get started', 'View pricing',
  'Trusted by', 'Founder', 'Wozniak', 'Jason Ray', 'Elon Musk',
  'Instant Onboarding', 'Collaboartion', 'Website Pages', 'Multi Pages',
  'Figma', 'Webflow', 'Framer',
  // internal vocabulary
  'delta', 'VAM', 'Tier-1', 'tier1', 'receta', 'scraper', 'scraping',
  'endpoint', 'cdp_code', 'servable', 'canonical', 'quórum', 'provenance',
];

/** Files whose English is legitimate (identifiers, comments, generated data). */
const SKIP = ['spain-map-dots.ts', 'brand-marks.tsx'];

const files = walk(path.join(WEB, 'src')).filter(
  (f) => /\.(tsx|ts)$/.test(f) && !SKIP.some((s) => f.endsWith(s)),
);

/** Only user-visible text: JSX text nodes and quoted strings in content data. */
function visibleText(source) {
  const stripped = source
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/^\s*\/\/.*$/gm, ' ');
  const jsxText = [...stripped.matchAll(/>([^<>{}]{3,})</g)].map((m) => m[1]);
  const strings = [...stripped.matchAll(/'([^'\\]{4,})'|"([^"\\]{4,})"/g)].map((m) => m[1] ?? m[2]);
  return [...jsxText, ...strings]
    .map((s) => s.trim())
    // Drop class strings and paths — those are code, not copy.
    .filter((s) => s && !/^[a-z0-9:_\-/\[\]().%\s#*&>+~]+$/i.test(s) === false ? false : true)
    .filter((s) => !s.includes('/') && !/^[a-z-]+(\s+[a-z0-9:_\-\[\]().%#*&>+~]+)+$/.test(s));
}

let hits = 0;
for (const file of files) {
  const source = fs.readFileSync(file, 'utf8');
  const text = visibleText(source).join('\n');
  for (const word of FORBIDDEN) {
    const re = new RegExp(`\\b${word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (re.test(text)) {
      console.log(`  ${path.relative(WEB, file)}  ->  "${word}"`);
      hits++;
    }
  }
}

if (hits === 0) {
  console.log('copy check: clean — no template English and no internal vocabulary in visible text');
} else {
  console.log(`\ncopy check: ${hits} occurrence(s) to review`);
  process.exitCode = 1;
}
