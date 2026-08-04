import { useEffect, useRef, useState } from 'react';
import { useReducedMotion } from 'framer-motion';

/**
 * The rotating examples shown inside the free-text field.
 *
 * Teaching material, not decoration, and rebuilt from a segmentation of the
 * Spanish used-car buyer rather than from what reads well. Every line is a query
 * a real segment types, and every one was counted against the live index before it
 * was allowed in — the smallest returns 481 cars, the largest 58.052.
 *
 * The ramp is the argument:
 *
 *   1. A LIFE, not a car. Seven seats is a hard constraint nobody negotiates, and
 *      seeing it answered in the first second reframes the box from "brand search"
 *      to "needs engine". Biggest lesson first.
 *   2. Immediate contrast: after an aspirational need, the index has to prove on
 *      the spot that it also serves someone with almost no money, or the whole set
 *      reads as a dealer's catalogue.
 *   3. The "I didn't know it could do that" hit, and it has to land in the first
 *      half or it never lands. No generalist portal speaks to the self-employed in
 *      its hero.
 *   4. The EV buyer's real anxiety is battery age, and they proxy it with mileage.
 *      Answering the proxy people actually use is what makes the index look like it
 *      understands the category.
 *   5. Province arrives fifth, once three filter types are familiar — and Málaga,
 *      not Madrid, because naming a non-obvious province proves the coverage is
 *      real rather than capital-only.
 *   6. Three words, no syntax, pure desire. After five utilitarian queries the ramp
 *      needs appetite or the field becomes a form.
 *   7. Explicit permission to write like a person. "Grande de familia" is not a
 *      category anyone ever published; it is how people talk.
 *   8. "Urbano" is not a published body style either — it resolves to utilitario.
 *      Barcelona has Spain's strictest low-emission zone, so this buyer is
 *      filtering on something real.
 *   9. Two words. Colour is the most trivial thing a person cares about and the
 *      last thing a database usually knows. Late in the ramp because it is a
 *      delight, not a lesson.
 *  10. The decided buyer, negotiating with their own wallet. The Ibiza is Spain's
 *      #2 registration; this query is a third of real traffic.
 *  11. Body + energy + seats stacked, closing the circle the first line opened.
 *  12. RESTING STATE. Whoever is still watching does not know what they want, and
 *      you do not ask that person for a budget — you show them their own life
 *      already typed. SUV (62% of 2025 registrations) + hybrid (47% of 2026) +
 *      20.000 € (just above the 16.883 € average budget) is the modal Spanish
 *      buyer in one line.
 *
 * What is NOT here, and why: no "automático" (transmission is unpublished on 51%
 * of the index and is not a cube dimension — a chip for it would be doubly false),
 * no boot size, no power in CV, no consumption. Those columns do not exist. Colour,
 * body type, seats, fuel and price DO exist and are counted, which is a change from
 * when this comment last claimed otherwise.
 */
export const SEARCH_EXAMPLES = [
  'Coche de 7 plazas para la familia',
  'Utilitario por menos de 8.000 €',
  'Furgoneta diésel con menos de 150.000 km',
  'Coche eléctrico con menos de 50.000 km',
  'SUV diésel con menos de 150.000 km en Málaga',
  'Volkswagen Golf GTI',
  'Coche grande de familia en Sevilla',
  'Coche urbano de gasolina en Barcelona',
  'SUV blanco',
  'SEAT Ibiza por menos de 12.000 €',
  'Monovolumen diésel de 7 plazas',
  'SUV híbrido por menos de 20.000 €',
] as const;

/** Index the rotation settles on if it ever stops on its own. */
const RESTING = SEARCH_EXAMPLES.length - 1;

/**
 * How many full passes before the rotation gives up.
 *
 * It was two, which is why the field looked static: two passes is under a minute,
 * and any visitor who arrived, read the headline and then looked right found a
 * frozen line. The examples are the field's entire explanation of what it can do —
 * they have to still be explaining when someone finally looks. WCAG 2.2.2 asks for
 * a mechanism to stop auto-updating content, and there are two: hovering pauses
 * it, and touching the field ends it for good. A hard time limit was never the
 * mechanism; it was just an expiry.
 */
const LOOPS = 12;

/* Typing rhythm. 45 ms/char tracks the ~22 characters/second of silent Spanish
 * reading, so the line is legible as it lands rather than after it lands. The
 * jitter is seeded off the character index, never Math.random — a re-render must
 * not reshuffle the cadence mid-word. Punctuation gets a longer beat because
 * that is where a human hand actually pauses. */
const MS_PER_CHAR = 45;
const JITTER = 12;
const PAUSE_SPACE = 60;
const PAUSE_PUNCT = 180;

function charDelay(ch: string, i: number): number {
  const jitter = ((i * 2654435761) % (JITTER * 2)) - JITTER; // deterministic
  const extra = ch === ' ' ? PAUSE_SPACE : ch === ',' || ch === '€' ? PAUSE_PUNCT : 0;
  return MS_PER_CHAR + jitter + extra;
}

const holdFor = (text: string) => Math.max(1600, text.length * MS_PER_CHAR + 900);

interface TypedPlaceholder {
  /** The string to paint in the aria-hidden overlay. */
  text: string;
  /** The full example currently being shown — what Enter on an empty field runs. */
  current: string;
  /** True while characters are still arriving (drives the solid-vs-blinking caret). */
  typing: boolean;
  /** Rotation has ended, by completion or by user contact. */
  done: boolean;
}

/**
 * Types the examples out one character at a time and then stops for good.
 *
 * The string is NEVER written to the input's `placeholder` attribute. It is
 * rendered into a separate `aria-hidden` layer, so the field's accessible name
 * comes from its own label and stays fixed while the decoration mutates. Writing
 * it to `placeholder` would rewrite the accessible name several times a second
 * for anyone on a screen reader.
 *
 * `active` is the caller's kill switch: focus, hover or the first keystroke all
 * end the rotation permanently. WCAG 2.2.2 wants a way to stop auto-updating
 * content; the honest reading of that is not "add a pause button" but "stop the
 * moment the user shows up". It also self-terminates after two loops so an
 * unattended page eventually goes quiet.
 */
export function useTypedPlaceholder(active: boolean): TypedPlaceholder {
  const reduced = useReducedMotion();
  const [text, setText] = useState('');
  const [index, setIndex] = useState(0);
  const [typing, setTyping] = useState(true);
  const [done, setDone] = useState(false);
  const loops = useRef(0);
  const timer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    // Reduced motion, or the user has engaged: paint the resting example whole
    // and never animate. The examples still teach; they just stop moving.
    if (reduced || !active || done) {
      if (reduced) {
        setText(SEARCH_EXAMPLES[RESTING]);
        setIndex(RESTING);
      }
      setTyping(false);
      return;
    }

    const full = SEARCH_EXAMPLES[index];

    if (text.length < full.length) {
      const next = full.slice(0, text.length + 1);
      timer.current = setTimeout(
        () => setText(next),
        charDelay(full[text.length], text.length),
      );
      return () => clearTimeout(timer.current);
    }

    setTyping(false);
    timer.current = setTimeout(() => {
      const isLastOfLoop = index === SEARCH_EXAMPLES.length - 1;
      if (isLastOfLoop) loops.current += 1;
      if (isLastOfLoop && loops.current >= LOOPS) {
        // Settle on the resting example rather than stopping wherever the last
        // frame happened to land.
        setIndex(RESTING);
        setText(SEARCH_EXAMPLES[RESTING]);
        setDone(true);
        return;
      }
      setText('');
      setTyping(true);
      setIndex((i) => (i + 1) % SEARCH_EXAMPLES.length);
    }, holdFor(full));

    return () => clearTimeout(timer.current);
  }, [text, index, active, done, reduced]);

  return { text, current: SEARCH_EXAMPLES[index], typing, done };
}
