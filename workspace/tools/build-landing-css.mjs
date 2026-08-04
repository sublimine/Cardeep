/**
 * Builds the landing's stylesheet.
 *
 * WHY THIS EXISTS
 * The landing was authored in the sibling `web/` app against Tailwind v4; this
 * app runs Tailwind v3. The landing leans on utilities v3 cannot generate at all
 * (`mask-*`, `bg-linear-*`, `size-0.75`, `duration-400`, the `**:` variant) and
 * on several whose VALUE changed between the two majors (`rounded-sm`,
 * `blur-sm`, `ring-3`). Re-authoring it in v3 would therefore change how it
 * looks, so instead its CSS is compiled by the v4 compiler exactly as `web/`
 * compiles it, then every selector is scoped under `.cx-v4`.
 *
 * Scoping is what keeps the two Tailwinds from fighting:
 *   - `#cx-v4 .rounded-sm` outranks v3's `.rounded-sm`, so the landing keeps v4
 *     values while the app keeps v3 values for the same class names.
 *   - v4's theme variables land on `#cx-v4` instead of `:root`, so its
 *     `--radius-*` / `--container-*` never overwrite the app's own tokens.
 *   - v4's preflight is confined to the landing subtree.
 *
 * Run `npm run landing:css` after editing anything under `src/landing-v4/`.
 */
import { execFileSync } from 'node:child_process';
import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import postcss from 'postcss';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

// An ID, not a class. Tailwind v4 wraps a number of utilities in `:where(...)`,
// which zeroes their internal specificity — scoping those with a class would
// leave them at (0,1,0), losing to this app's v3 `.space-x-8 > :not([hidden]) ~
// :not([hidden])` at (0,3,0). One ID outranks any number of classes, so the
// landing wins inside its subtree whatever v3 emits, while the uniform bump
// leaves the landing's own rules in their original relative order.
const SCOPE = '#cx-v4';
const ENTRY = join(ROOT, 'src/landing-v4/tailwind.entry.css');
const RAW = join(ROOT, 'node_modules/.cache/landing-raw.css');
const OUT = join(ROOT, 'src/landing-v4/landing.generated.css');

/** At-rules whose child rules are not selectors and must be left alone. */
const OPAQUE_AT_RULES = /^(-\w+-)?(keyframes|font-face|property|counter-style)$/i;

/** Selectors that mean "the document root" and must BECOME the scope element. */
const ROOT_TOKEN = /^(:root|:host|html|body)\b/;

/**
 * Rewrites one selector so it only ever matches inside the landing subtree.
 *
 * `:root`/`html`/`body` are remapped onto the scope element itself — prefixing
 * them instead (`.cx-v4 html`) would produce a selector that matches nothing,
 * silently dropping the theme variables and the page background. The universal
 * selector additionally keeps the scope element itself so preflight's
 * box-sizing and margin reset apply to the landing's own root node.
 */
function scopeSelector(selector) {
  const sel = selector.trim();
  if (!sel || sel.startsWith(SCOPE)) return sel;
  if (ROOT_TOKEN.test(sel)) return sel.replace(ROOT_TOKEN, SCOPE);
  if (sel === '*') return `${SCOPE}, ${SCOPE} *`;
  return `${SCOPE} ${sel}`;
}

const scopeLanding = {
  postcssPlugin: 'scope-landing',
  Once(root) {
    root.walkRules((rule) => {
      for (let node = rule.parent; node; node = node.parent) {
        if (node.type === 'atrule' && OPAQUE_AT_RULES.test(node.name)) return;
      }
      // Deduplicated because distinct root selectors (`:root, :host`) collapse
      // onto the same scope element.
      rule.selectors = [...new Set(rule.selectors.map(scopeSelector))];
    });

    // Flatten `@layer`, keeping every rule in source order.
    //
    // Not cosmetic: unlayered declarations outrank layered ones no matter how
    // specific the layered selector is, and Tailwind v3 emits this app's CSS
    // with no layers at all. Left in a layer, `.cx-v4 .text-sm` would lose to
    // the app's plain `.text-sm` and the scoping would buy nothing. Flattening
    // hands the cascade back to specificity, where the scope class wins by the
    // extra class it adds to every selector. It also keeps Tailwind v3's
    // PostCSS pass from erroring on a bare `@layer` it has no directive for.
    root.walkAtRules('layer', (atRule) => {
      if (atRule.nodes) atRule.replaceWith(atRule.nodes);
      else atRule.remove();
    });
  },
};

mkdirSync(dirname(RAW), { recursive: true });

// The v4 compiler is a devDependency of this app and resolves its own
// tailwindcss@4 from its nested tree, leaving the app's tailwindcss@3 alone.
// Called by its module path rather than through `node_modules/.bin`: both
// Tailwind majors publish a `tailwindcss` bin, so the shim is ambiguous here.
const CLI = join(ROOT, 'node_modules/@tailwindcss/cli/dist/index.mjs');

execFileSync(process.execPath, [CLI, '--input', ENTRY, '--output', RAW], {
  cwd: ROOT,
  stdio: ['ignore', 'ignore', 'inherit'],
});

/**
 * Emits a guard against the one conflict specificity cannot settle.
 *
 * Tailwind v4 moved translate/rotate/scale onto the standalone `translate`,
 * `rotate` and `scale` CSS properties; v3 still writes them into `transform`.
 * They are different properties, so for a class both majors generate — say
 * `-translate-x-1/2` — the app's v3 `transform: translate(-50%, …)` does not
 * lose to the landing's rule, it COMPOSES with it, and the element ends up
 * moved twice (this shifted the hero's arc by a full width, not half).
 *
 * So every class the landing styles through a standalone transform property
 * gets `transform: none` here. Emitted before the utilities, so that a v4 rule
 * legitimately setting `transform` on the same element still wins on ties.
 */
function transformGuard(css) {
  const classes = new Set();
  postcss.parse(css).walkRules((rule) => {
    if (!rule.some((d) => d.type === 'decl' && ['translate', 'rotate', 'scale'].includes(d.prop))) return;
    for (const m of rule.selector.matchAll(/\.((?:\\.|[\w-])+)/g)) classes.add(m[1]);
  });
  if (!classes.size) return '';
  const selector = [...classes].sort().map((c) => `${SCOPE} .${c}`).join(',\n');
  return `/* Neutralises Tailwind v3's \`transform\` for utilities v4 expresses as\n` +
    `   standalone translate/rotate/scale — see transformGuard() for why. */\n` +
    `${selector} {\n  transform: none;\n}\n`;
}

const raw = readFileSync(RAW, 'utf8');
const scoped = transformGuard(raw) + postcss([scopeLanding]).process(raw, { from: RAW, to: OUT }).css;

const header = `/**
 * GENERATED — do not edit. Run \`npm run landing:css\` instead.
 * Source: src/landing-v4/tailwind.entry.css, compiled by Tailwind v4 and
 * scoped under \`${SCOPE}\` by tools/build-landing-css.mjs.
 */\n`;

writeFileSync(OUT, header + scoped, 'utf8');
rmSync(RAW, { force: true });

const kb = (s) => `${(Buffer.byteLength(s) / 1024).toFixed(1)} KB`;
console.log(`landing:css  ${kb(raw)} compiled -> ${kb(header + scoped)} scoped under ${SCOPE}`);
