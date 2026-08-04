/**
 * The Cardeep mark: a "C" drawn as a dot matrix.
 *
 * It is the product in one glyph — an index built point by point — and it shares
 * a language with the rest of the page: the dot arrow inside every CTA and the
 * dotted map of Spain. Because it is a grid rather than a drawing, it stays
 * legible at 16px and needs no separate favicon artwork.
 */

/** `1` is a lit dot. Reading the rows top-to-bottom spells a C. */
const MARK = [
  [0, 1, 1, 1, 0],
  [1, 0, 0, 0, 1],
  [1, 0, 0, 0, 0],
  [1, 0, 0, 0, 1],
  [0, 1, 1, 1, 0],
] as const;

const CELL = 4;
const ORIGIN = 2;
const RADIUS = 1.35;

type LogoProps = {
  /** `light` for dark backgrounds, `dark` for light ones. */
  tone?: 'light' | 'dark';
  className?: string;
  title?: string;
};

export function Logo({ tone = 'light', className, title = 'Cardeep' }: LogoProps) {
  const lit = tone === 'light' ? '#ffffff' : '#05070c';
  const dim = tone === 'light' ? 'rgba(255,255,255,0.22)' : 'rgba(5,7,12,0.18)';

  return (
    <svg viewBox="0 0 20 20" className={className} role="img" aria-label={title}>
      {MARK.flatMap((row, y) =>
        row.map((on, x) => (
          <circle
            key={`${x}-${y}`}
            cx={ORIGIN + x * CELL}
            cy={ORIGIN + y * CELL}
            r={RADIUS}
            // The one accent dot marks the index's densest point, the way the map
            // does. It was the template's yellow; it is the brand's soft blue now,
            // so the mark carries one hue and the dot still reads as the accent
            // against both the white and the near-black dots around it.
            fill={on ? (x === 0 && y === 2 ? '#8ab9fd' : lit) : dim}
          />
        )),
      )}
    </svg>
  );
}
