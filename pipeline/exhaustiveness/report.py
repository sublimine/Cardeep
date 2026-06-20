"""Coverage report endpoint: certified % coverage by province x type and global.

Reads v_exhaustiveness_seal (latest build) and returns a structured report. This
is the queryable surface the mandate asks for: per stratum and global coverage
with its CI and seal verdict.
"""

from __future__ import annotations

import psycopg2

from pipeline.exhaustiveness.capture import DSN


def coverage_report(*, dsn: str = DSN) -> dict:
    """Return {national: {...}, strata: [{...}]} from the latest sealed build."""
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT province_code, segment, k_lists, n_obs, n_hat,
                       ci_low, ci_high, coverage_point, coverage_lower,
                       method, confidence, seal_threshold, sealed
                FROM v_exhaustiveness_seal
                ORDER BY (province_code IS NULL) DESC, n_obs DESC
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    cols = [
        "province_code", "segment", "k_lists", "n_obs", "n_hat", "ci_low",
        "ci_high", "coverage_point", "coverage_lower", "method", "confidence",
        "seal_threshold", "sealed",
    ]
    national = None
    strata = []
    for r in rows:
        d = dict(zip(cols, r))
        if d["province_code"] is None and d["segment"] is None:
            national = d
        else:
            strata.append(d)
    return {"national": national, "strata": strata, "n_strata": len(strata)}


if __name__ == "__main__":
    import json

    rep = coverage_report()
    print(json.dumps(rep["national"], indent=2, default=str))
    print(f"... + {rep['n_strata']} strata")
