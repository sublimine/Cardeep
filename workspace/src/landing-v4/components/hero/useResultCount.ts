import { useEffect, useRef, useState } from 'react';

import { cardeep, type SearchCount, type SearchCountParams } from '../../../api/cardeep';

/* Continuous controls need a debounce; discrete ones (picking a marque, a
 * province) do not — those are single, intentional acts and the count comes back
 * in 43-60 ms. 250 ms is the compromise, low enough that the number feels
 * attached to the click. */
const DEBOUNCE_MS = 250;

interface ResultCount {
  /** Last known count. Deliberately survives across refetches — see note below. */
  data: SearchCount | null;
  pending: boolean;
}

/**
 * The number the submit button promises.
 *
 * Two things this does that a naive `useEffect` + `fetch` does not:
 *
 * ABORT, not just debounce. Debouncing delays the NEXT request; it does nothing
 * about the one already in flight. Without an AbortController plus the request-id
 * guard below, a slow early response can land after a fast later one and leave the
 * button showing a count for filters the user has already changed — the classic
 * race, and the failure is invisible because the number still looks plausible.
 *
 * NEVER BLANK WHILE LOADING. The previous count stays on screen with a pending
 * state rather than being cleared. A counter exists to set expectations, and
 * flashing to empty on every keystroke destroys the very thing it is for.
 */
export function useResultCount(params: SearchCountParams): ResultCount {
  const [data, setData] = useState<SearchCount | null>(null);
  const [pending, setPending] = useState(false);
  const requestId = useRef(0);

  // Serialised so the effect re-runs on VALUE change, not on the identity of the
  // object literal the caller rebuilds every render.
  const key = JSON.stringify(params);

  useEffect(() => {
    const id = ++requestId.current;
    const controller = new AbortController();
    setPending(true);

    const timer = setTimeout(() => {
      cardeep
        .searchCount(JSON.parse(key) as SearchCountParams, controller.signal)
        .then((value) => {
          // A response from a superseded request is discarded even if it arrives
          // last. `id` is what makes that decidable.
          if (id === requestId.current) setData(value);
        })
        .catch(() => {
          /* An unreachable counter leaves the last honest number in place rather
             than inventing one or showing zero. */
        })
        .finally(() => {
          if (id === requestId.current) setPending(false);
        });
    }, DEBOUNCE_MS);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [key]);

  return { data, pending };
}
