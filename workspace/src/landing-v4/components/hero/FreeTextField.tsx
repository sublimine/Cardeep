import { useState } from 'react';
import { Search } from 'lucide-react';

import { useTypedPlaceholder } from './useTypedPlaceholder';

interface FreeTextFieldProps {
  value: string;
  onChange: (value: string) => void;
  /** Enter pressed on an empty field — runs whatever example is on screen. */
  onRunExample: (example: string) => void;
}

/**
 * The sentence field: the one control on this page that accepts a whole query.
 *
 * Three things distinguish it from the input it replaces.
 *
 * THE RIM. A field that can answer a sentence has to advertise it before anyone
 * risks typing one. `field-beam` runs a soft highlight along the field's own
 * border — low at rest, firmer on hover, full on focus. It stops for good at the
 * first character: an invitation that keeps running after it has been accepted is
 * just noise. What this replaces lit the entire box from behind, which read as a
 * glowing control rather than a lit edge; see the utility for why this is also
 * not the hairline arc that came before that.
 *
 * THE EXAMPLES. They are typed into an `aria-hidden` overlay, never into the
 * `placeholder` attribute. The attribute is the LAST fallback in the accessible
 * name computation, so writing a rotating string into it would rewrite the
 * field's accessible name several times a second for anyone using a screen
 * reader or voice control. The name comes from `aria-label` and never moves; the
 * decoration moves.
 *
 * ENTER ON EMPTY. The documented failure mode of placeholder text is that people
 * read it as a value that is already filled in and press Enter. Rather than
 * fight that, this field honours it: Enter on an empty box runs the example
 * being shown. The misconception becomes the fastest path to a real result.
 * The submit button is deliberately NOT wired to it — its label promises the
 * whole index, and a control has to do what its label says.
 */
export function FreeTextField({ value, onChange, onRunExample }: FreeTextFieldProps) {
  /* Two different things, which the first version had collapsed into one.
   *
   * `engaged` is the user having touched the field — focus, a keystroke, a
   * character. That ends the rotation for good.
   * `paused` is the pointer resting over it. That is someone READING, and it
   * should hold the line still so they can, then let it continue.
   *
   * Collapsing them meant `onPointerEnter` killed the animation permanently: the
   * cursor crossing the panel on its way anywhere else froze the examples for the
   * rest of the visit, which is exactly why the field looked static. Pausing on
   * hover and stopping on contact are both valid WCAG 2.2.2 mechanisms; killing
   * on hover is neither, it is just a bug wearing a rule's clothes. */
  const [engaged, setEngaged] = useState(false);
  const [paused, setPaused] = useState(false);
  const { text, current, typing, done } = useTypedPlaceholder(!engaged && !paused);

  const empty = value.length === 0;
  const showOverlay = empty && text.length > 0;

  return (
    <div
      className={
        /* The fill stays solid. It was made solid when the effect was a gradient
         * sitting BEHIND the box, which at 5% white shone through and tinted the
         * whole control; the beam no longer needs that, but the field still reads
         * better as a distinct surface than its siblings. The static border stays
         * too, and now it is load-bearing: it is the track the beam travels. */
        'field-beam flex h-11 w-full items-center gap-2.5 rounded-[11px] border border-white/10 ' +
        'bg-[rgb(9_16_32/0.72)] px-3.5 transition-colors duration-200 focus-within:border-white/25 ' +
        (empty && !engaged ? 'field-beam-idle' : '')
      }
      onPointerEnter={() => setPaused(true)}
      onPointerLeave={() => setPaused(false)}
    >
      <Search size={14} className="shrink-0 text-white/40" />

      {/* The input and its decoration share one box so the overlay lines up with
          the caret exactly, whatever the field's width ends up being. */}
      <div className="relative min-w-0 flex-1">
        {showOverlay && (
          <span
            aria-hidden
            className="pointer-events-none absolute inset-y-0 left-0 flex items-center whitespace-nowrap text-[13.5px] text-white/40"
          >
            {text}
            <span
              className={
                'ml-px inline-block h-[1.05em] w-px translate-y-[1px] bg-white/55 ' +
                (typing ? '' : 'animate-pulse')
              }
            />
          </span>
        )}
        <input
          value={value}
          aria-label="Buscar coches en el índice"
          onChange={(e) => {
            setEngaged(true);
            onChange(e.target.value);
          }}
          onFocus={() => setEngaged(true)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && empty) {
              e.preventDefault();
              onRunExample(done || engaged ? current : current);
            }
          }}
          /* Empty on purpose: the visible examples live in the overlay above, and
             duplicating them here would put a mutating string into the accessible
             name. A static fallback appears only once the rotation is over and the
             overlay has nothing to paint. */
          placeholder={showOverlay ? '' : 'Marca, modelo, presupuesto, provincia…'}
          className="w-full bg-transparent text-[13.5px] text-white outline-none placeholder:text-white/35"
        />
      </div>
    </div>
  );
}
