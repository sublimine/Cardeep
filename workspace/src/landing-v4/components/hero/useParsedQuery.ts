import { useEffect, useRef, useState } from 'react';

import { cardeep, type ParsedQuery } from '../../../api/cardeep';

const DEBOUNCE_MS = 300;

/**
 * What the sentence in the free-text field actually means.
 *
 * Calls `/search/parse`, which resolves a written query against the census's own
 * dictionaries — every marque and model it holds, the 52 provinces, and the body
 * types labelled per model — and returns structured filters plus, critically, the
 * words it could NOT resolve.
 *
 * That last part is the whole point. The product's standing rule is that nothing
 * random is ever shown, and the way random results get into a search is a query
 * being quietly widened when part of it was not understood. Surfacing the leftover
 * words lets the interface say "no entendí «plazas»" instead of silently searching
 * for something else.
 *
 * Debounced and abortable for the same reason the counter is: a slow early
 * response landing after a fast later one would describe a sentence the user has
 * already changed.
 */
export function useParsedQuery(query: string): { parsed: ParsedQuery | null } {
  const [parsed, setParsed] = useState<ParsedQuery | null>(null);
  const requestId = useRef(0);

  useEffect(() => {
    const text = query.trim();
    if (text.length < 3) {
      setParsed(null);
      return;
    }

    const id = ++requestId.current;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      cardeep
        .searchParse(text, controller.signal)
        .then((value) => {
          if (id === requestId.current) setParsed(value);
        })
        .catch(() => {
          /* leave the last understanding in place rather than inventing one */
        });
    }, DEBOUNCE_MS);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query]);

  return { parsed };
}
