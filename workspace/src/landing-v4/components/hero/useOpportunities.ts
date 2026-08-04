import { useEffect, useState } from 'react';

import { cardeep, type OpportunityVehicle } from '../../../api/cardeep';

interface Opportunities {
  items: OpportunityVehicle[];
  /** True once the request has settled, so the strip can stop reserving space. */
  ready: boolean;
}

/**
 * The vehicles the deal-score run judged underpriced (`GET /market/opportunities`).
 *
 * This replaces the random showcase the strip used to draw from. A `TABLESAMPLE`
 * of the census proves the index is real; it does not identify an opportunity,
 * and a strip that says "oportunidades" over randomly drawn cars is making a
 * claim its own query cannot support.
 *
 * On failure the list stays EMPTY and the strip renders nothing rather than
 * falling back to invented cars — the rule `useLandingStats` follows for the
 * census figures and that `tests/test_web_no_fabricated_data.py` enforces. An
 * empty strip is honest; a fabricated one is not.
 */
export function useOpportunities(limit = 10): Opportunities {
  const [items, setItems] = useState<OpportunityVehicle[]>([]);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    cardeep
      .marketOpportunities(limit, controller.signal)
      .then((v) => {
        if (!controller.signal.aborted) setItems(v);
      })
      .catch(() => {
        /* leave the strip empty — see the note above */
      })
      .finally(() => {
        if (!controller.signal.aborted) setReady(true);
      });

    return () => controller.abort();
  }, [limit]);

  return { items, ready };
}
