"""VERIFICAR — VAM count quorum. Persists a verification_verdict.

A count is TRUSTWORTHY only if >=2 orthogonal paths agree within tolerance.
"""
from __future__ import annotations

import json

import asyncpg


async def record_count_verdict(
    conn: asyncpg.Connection,
    *,
    subject_type: str,
    subject_key: str,
    claim: str,
    paths: dict[str, int],
    tolerance: float = 0.0,
) -> str:
    """paths: {path_name: count}. Quorum rule (mandate: ">=2 orthogonal paths agree"):
    TRUSTWORTHY when the modal value is supported by >=2 paths and no rival value also
    reaches >=2 (a clean majority). A lone divergent path (e.g. a source counter that
    over-counts duplicates) does not refute when >=2 independent paths agree."""
    from collections import Counter

    items = [(k, v) for k, v in paths.items() if v is not None]
    values = [v for _, v in items]
    primary_path, primary_value = next(iter(paths.items()))
    if len(values) < 2:
        verdict, divergence = "UNVERIFIED", None
    else:
        freq = Counter(values)
        (top_val, top_n), = freq.most_common(1)
        rivals = [val for val, n in freq.items() if n >= 2 and val != top_val]
        lo, hi = min(values), max(values)
        divergence = (hi - lo) / hi if hi else 0.0
        # The primary path (what actually landed, e.g. db_ingested) MUST agree with at
        # least one other path — otherwise a fetched/declared pair could mask real
        # ingestion loss (collisions/skips). Silent data loss never reads as TRUSTWORTHY.
        primary_agrees = sum(1 for v in values if v == primary_value) >= 2
        if top_n >= 2 and not rivals and primary_agrees:
            verdict = "TRUSTWORTHY"
        elif divergence <= tolerance:
            verdict = "TRUSTWORTHY"
        else:
            verdict = "REFUTED"
    await conn.execute(
        """INSERT INTO verification_verdict
             (subject_type, subject_key, claim, primary_value, primary_path,
              verifier_paths, independent_values, divergence, verdict, evidence)
           VALUES ($1,$2,$3,$4,$5,$6::jsonb,$7::jsonb,$8,$9,$10)""",
        subject_type, subject_key, claim, str(primary_value), primary_path,
        json.dumps(list(paths.keys())), json.dumps(paths), divergence, verdict,
        f"paths={paths}",
    )
    return verdict
