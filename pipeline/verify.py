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
    """paths: {path_name: count}. TRUSTWORTHY if all paths agree within tolerance
    (relative). Returns the verdict."""
    values = [v for v in paths.values() if v is not None]
    if len(values) < 2:
        verdict = "UNVERIFIED"
        divergence = None
    else:
        lo, hi = min(values), max(values)
        divergence = (hi - lo) / hi if hi else 0.0
        verdict = "TRUSTWORTHY" if divergence <= tolerance else "REFUTED"
    primary_path, primary_value = next(iter(paths.items()))
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
