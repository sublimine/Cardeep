"""External triangulation seam (§2.7): contrast N̂ against an independent census.

The capture-recapture N̂ is believable only if it agrees with a census built by a
*different* mechanism. The canonical anchor for Spanish dealers is INE DIRCE
(enterprises by CNAE 4511 "venta de automóviles" / 4531-4532 / 4520 talleres) and,
secondarily, DGT authorised-centre counts.

This module is the wired seam: drop a CSV with columns
    province_code,segment,n_external
under countries/ES/census/ and it is loaded into the {(province,segment): N}
dict that seal.compute(external_census=...) consumes, and compared against N̂.

No census figures are fabricated here. Until the real DIRCE/DGT extract is placed,
``load_external_census`` returns {} and triangulation is reported as
"pending external census load" — the pipeline runs, the anchor is just absent.
"""

from __future__ import annotations

import csv
import pathlib

CENSUS_DIR = pathlib.Path(__file__).resolve().parents[2] / "countries" / "ES" / "census"
DEFAULT_CSV = CENSUS_DIR / "dirce_cnae451.csv"


def load_external_census(path: pathlib.Path | None = None) -> dict[tuple[str | None, str | None], float]:
    """Load {(province_code, segment): n_external} from a census CSV.

    Expected header: province_code,segment,n_external. A row with empty
    province_code or segment encodes a national / all-segment anchor (None key).
    Returns {} if the file is absent (seam wired, data pending).
    """
    p = path or DEFAULT_CSV
    if not p.exists():
        return {}
    out: dict[tuple[str | None, str | None], float] = {}
    with p.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            prov = (row.get("province_code") or "").strip() or None
            seg = (row.get("segment") or "").strip() or None
            try:
                n = float(row["n_external"])
            except (KeyError, ValueError):
                continue
            out[(prov, seg)] = n
    return out


def triangulate(n_hat: float, n_external: float | None) -> dict:
    """Compare N̂ to the external census. Returns ratio + verdict.

    verdict: 'consistent' if 0.7 <= N̂/ext <= 1.4; 'n_hat_high' / 'n_hat_low'
    otherwise; 'no_anchor' when the external figure is missing.
    """
    if n_external is None or n_external <= 0:
        return {"verdict": "no_anchor", "n_external": n_external}
    ratio = n_hat / n_external
    if ratio > 1.4:
        verdict = "n_hat_high"      # listas correlacionadas no modeladas o dedup imperfecto
    elif ratio < 0.7:
        verdict = "n_hat_low"       # cobertura externa más amplia / strata faltantes
    else:
        verdict = "consistent"
    return {"verdict": verdict, "ratio": round(ratio, 3), "n_external": n_external}


def status() -> str:
    n = len(load_external_census())
    return f"loaded {n} anchors from {DEFAULT_CSV}" if n else (
        f"pending external census (drop CSV at {DEFAULT_CSV})"
    )
