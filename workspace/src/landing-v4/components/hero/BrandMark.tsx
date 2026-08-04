import { useState } from 'react';

import LOGO_FILES from '../../data/logo-ar.json';

/**
 * Canonical slug -> logo filename, where the two genuinely disagree. The census
 * calls the marque Mercedes-Benz; the logo set filed it under mercedes. Only real
 * mismatches belong here — hyphenated filenames already fold to the same slug on
 * their own.
 */
const LOGO_SLUG_ALIASES: Record<string, string> = {
  mercedesbenz: 'mercedes',
  'mercedes-benz': 'mercedes',
  landrover: 'landrover',
  'land-rover': 'landrover',
  'alfa-romeo': 'alfaromeo',
  'aston-martin': 'astonmartin',
  'rolls-royce': 'rollsroyce',
  'lynk-co': 'lynkco',
  'great-wall': 'greatwall',
  'moto-guzzi': 'motoguzzi',
  'roller-team': 'rollerteam',
  vw: 'volkswagen',
};

const LOGO_BY_SLUG: Record<string, string> = Object.fromEntries(
  Object.keys(LOGO_FILES as Record<string, number>).map((file) => [
    file.replace(/\.[a-z0-9]+$/i, '').replace(/[^a-z0-9]/gi, '').toLowerCase(),
    file,
  ]),
);

/** Slugs the CDN has already refused this session — a miss is remembered so
 *  re-opening the list costs nothing and the console stays quiet. */
const CDN_MISSES = new Set<string>();

function key(slug: string): string {
  return slug.replace(/[^a-z0-9]/gi, '').toLowerCase();
}

/**
 * Two letters that mean something.
 *
 * Taking the first two characters gave "Land Rover" the monogram "LA", which
 * reads as a truncation rather than a mark. A marque written as several words is
 * initialled — LR, AR, MB — because that is how people already abbreviate them,
 * and a fallback that matches the reader's own shorthand looks chosen instead of
 * left over.
 */
function monogram(name: string): string {
  const words = name.split(/[\s-]+/).filter((w) => /[\p{L}\p{N}]/u.test(w));
  if (words.length > 1) {
    return words.slice(0, 2).map((w) => w[0]).join('').toUpperCase();
  }
  return name.replace(/[^\p{L}\p{N}]/gu, '').slice(0, 2).toUpperCase();
}

/**
 * A marque's own mark.
 *
 * Three sources, tried in order: the self-hosted set, Simple Icons for the marques
 * it covers, and a monogram as the last resort.
 *
 * The monogram is DESIGNED, not a text node in a system font. Twenty-four of the
 * files in the self-hosted set are an Arial `<text>` element pretending to be a
 * trademark — LAND ROVER, with twenty-one thousand cars in the index, is one of
 * them — and that is a large part of why the picker read as unfinished. A fallback
 * that looks deliberate is honest; one that looks like a broken image is not. This
 * one uses the product's own type and glass treatment, so a marque without an
 * asset still belongs to the interface.
 */
export function BrandMark({ slug, name }: { slug: string; name: string }) {
  const k = key(slug);
  const local = LOGO_BY_SLUG[k] ?? LOGO_BY_SLUG[key(LOGO_SLUG_ALIASES[slug] ?? LOGO_SLUG_ALIASES[k] ?? '')];
  const cdn = !local && !CDN_MISSES.has(k);
  const [stage, setStage] = useState<0 | 1 | 2>(local ? 0 : cdn ? 1 : 2);

  if (stage === 2) {
    return (
      <span
        aria-hidden
        className="flex h-5 w-5 shrink-0 items-center justify-center rounded-[6px] border border-white/12 bg-white/[0.07] text-[8.5px] font-semibold leading-none tracking-[0.02em] text-white/75"
      >
        {monogram(name)}
      </span>
    );
  }

  const src = stage === 0 ? `/logos/${local}` : `https://cdn.simpleicons.org/${k}/ffffff`;
  return (
    <span className="flex h-5 w-5 shrink-0 items-center justify-center">
      <img
        key={src}
        src={src}
        alt=""
        loading="lazy"
        onError={() => {
          if (stage === 1) CDN_MISSES.add(k);
          setStage((v) => (v === 0 ? 1 : 2));
        }}
        className="max-h-5 max-w-5 object-contain opacity-90"
      />
    </span>
  );
}
