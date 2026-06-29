"""Splink probabilistic cross-source merge (§V6) for the exhaustiveness MSE.

Why: the capture unit for capture-recapture must be the *physical dealer*. The
existing deterministic dedup (v_dealer_resolved) leaves many cross-source
duplicates split, so two lists that both saw the same dealer can fail to overlap
-> small m -> wide CI. Splink links entities probabilistically (Fellegi-Sunter,
DuckDB) on name + municipality (+ phone + website + geo), recovering overlaps the
deterministic pass missed and tightening the denominator interval.

Output: discovery_splink_cluster (entity_ulid -> splink_cluster), consumed by
capture.build(unit="splink").

Pure-DuckDB, no admin, no R. If Splink is absent, callers fall back to the
deterministic resolved unit.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

import psycopg2

from pipeline.exhaustiveness.capture import DEALER_KINDS, DSN

_WS = re.compile(r"\s+")
_NONAL = re.compile(r"[^a-z0-9 ]+")
# legal-form suffixes, matched at END after punctuation is collapsed to spaces,
# so "S.L." -> "s l" and "SLU" -> "slu" are both caught.
_SUFFIX = re.compile(
    r"\s+(s\s*l\s*u|s\s*a\s*u|s\s*l\s*l|s\s*l|s\s*a|s\s*c\s*p|s\s*c|c\s*b"
    r"|sociedad limitada|sociedad anonima|unipersonal)\s*$"
)


@lru_cache(maxsize=1)
def splink_available() -> bool:
    try:
        import splink  # noqa: F401

        return True
    except Exception:
        return False


def _fold(s: str) -> str:
    """Strip accents/diacritics to ASCII (automoción -> automocion)."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )


def _norm_name(s: str | None) -> str | None:
    if not s:
        return None
    s = _fold(s.lower().strip())
    s = _NONAL.sub(" ", s)          # punctuation -> space first
    s = _WS.sub(" ", s).strip()
    s = _SUFFIX.sub("", s)          # then strip trailing legal form
    s = _WS.sub(" ", s).strip()
    return s or None


def _host(url: str | None) -> str | None:
    if not url:
        return None
    m = re.search(r"https?://([^/]+)", url.lower())
    host = (m.group(1) if m else url.lower()).strip()
    host = re.sub(r"^www\.", "", host)
    return host or None


def _digits(phone: str | None) -> str | None:
    if not phone:
        return None
    d = re.sub(r"\D+", "", phone)
    return d[-9:] if len(d) >= 9 else None


def _norm_cif(cif: str | None) -> str | None:
    """Spanish fiscal id normalised to 9 alnum chars, or None for placeholders/garbage (mirrors
    cluster_dealers._normalize_cif). The strongest cross-source identity signal for the MSE capture
    unit: an exact CIF match links the same legal company across sources/municipalities, recovering
    overlaps that name/geo fuzziness misses — without the over-merge risk of a fuzzy key."""
    if not cif:
        return None
    c = re.sub(r"[^A-Z0-9]", "", cif.upper())
    if len(c) != 9 or len(set(c)) == 1:
        return None
    return c


def _load_dealers(conn):
    import pandas as pd

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT e.entity_ulid,
                   COALESCE(e.trade_name, e.legal_name) AS name,
                   e.province_code, e.municipality_code,
                   e.phone, e.website, e.lat, e.lon, e.cif
            FROM entity e
            WHERE e.kind::text IN %s
            """,
            (DEALER_KINDS,),
        )
        rows = cur.fetchall()
    recs = []
    for ulid, name, prov, muni, phone, website, lat, lon, cif in rows:
        nm = _norm_name(name)
        recs.append(
            {
                "unique_id": ulid,
                "name": nm,
                # 4-char prefix: blocking key that still lets JaroWinkler score
                # fuzzy full-name pairs *within* the block (exact-name blocking
                # would hide the very fuzzy matches Splink exists to catch).
                "name_prefix": (nm[:4] if nm else None),
                "province_code": prov,
                "municipality_code": muni,
                "phone": _digits(phone),
                "website_host": _host(website),
                "lat": float(lat) if lat is not None else None,
                "lon": float(lon) if lon is not None else None,
                "cif": _norm_cif(cif),
            }
        )
    return pd.DataFrame.from_records(recs)


def _resolved_map(conn) -> dict[str, str]:
    """entity_ulid -> resolved_ulid (existing deterministic dedup)."""
    with conn.cursor() as cur:
        cur.execute("SELECT entity_ulid, resolved_ulid FROM v_dealer_resolved")
        return {e: r for e, r in cur.fetchall()}


class _UF:
    def __init__(self):
        self.p: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.p.setdefault(x, x)
        root = x
        while self.p[root] != root:
            root = self.p[root]
        while self.p[x] != root:
            self.p[x], x = root, self.p[x]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            # deterministic: lower id is the root
            lo, hi = sorted((ra, rb))
            self.p[hi] = lo


def run(build_run_id: str, *, dsn: str = DSN, match_threshold: float = 0.9) -> dict:
    """Run Splink dedupe over dealer entities and persist clusters. Returns summary."""
    if not splink_available():
        return {"status": "splink_unavailable"}

    from splink import DuckDBAPI, Linker, SettingsCreator, block_on
    import splink.comparison_library as cl

    conn = psycopg2.connect(dsn)
    try:
        df = _load_dealers(conn)
        n_in = len(df)

        settings = SettingsCreator(
            link_type="dedupe_only",
            blocking_rules_to_generate_predictions=[
                # block on muni + name PREFIX (not full name) so JaroWinkler can
                # score fuzzy full-name pairs inside the block.
                block_on("municipality_code", "name_prefix"),
                block_on("phone"),
                block_on("website_host"),
                block_on("cif"),   # CIF block: same legal company across muni/source (T2.1/T2.2)
            ],
            comparisons=[
                cl.JaroWinklerAtThresholds("name", [0.92, 0.82]),
                cl.ExactMatch("municipality_code"),
                cl.ExactMatch("phone").configure(term_frequency_adjustments=True),
                cl.ExactMatch("website_host").configure(term_frequency_adjustments=True),
                # CIF exact: the strongest cross-source link (same fiscal id = same company),
                # over-merge-safe — recovers overlaps name/geo miss, tightening the MSE denominator.
                cl.ExactMatch("cif").configure(term_frequency_adjustments=True),
            ],
            retain_intermediate_calculation_columns=False,
        )
        db_api = DuckDBAPI()
        linker = Linker(df, settings, db_api)

        # Train: u by random sampling; m by EM on strong blocking rules.
        linker.training.estimate_probability_two_random_records_match(
            [block_on("phone"), block_on("website_host")], recall=0.6
        )
        linker.training.estimate_u_using_random_sampling(max_pairs=3_000_000)
        for rule in (block_on("municipality_code", "name_prefix"), block_on("phone")):
            try:
                linker.training.estimate_parameters_using_expectation_maximisation(rule)
            except Exception:
                pass

        preds = linker.inference.predict(threshold_match_probability=match_threshold)
        clusters = linker.clustering.cluster_pairwise_predictions_at_threshold(
            preds, threshold_match_probability=match_threshold
        )
        cdf = clusters.as_pandas_dataframe()[["unique_id", "cluster_id"]]
        splink_collapsed = len(cdf) - cdf["cluster_id"].nunique()

        # UNION the Splink equivalence relation with the existing deterministic
        # dedup so the capture unit is NEVER finer than v_dealer_resolved (that
        # would lower overlap). Capture unit = connected component of both.
        resolved = _resolved_map(conn)
        uf = _UF()
        for ent, res in resolved.items():
            uf.union(ent, res)  # existing dedup edges
        by_cluster: dict[object, list[str]] = {}
        for r in cdf.itertuples(index=False):
            by_cluster.setdefault(r.cluster_id, []).append(r.unique_id)
        for members in by_cluster.values():
            first = members[0]
            for other in members[1:]:
                uf.union(first, other)  # splink edges
        # Persist only DEALER entities (the capture universe); their component id
        # carries the unified resolved+splink merge. Non-dealer entities are
        # irrelevant to the MSE and skipped to keep the write lean.
        dealer_ids = set(df["unique_id"].tolist())
        rows = [
            (ent, uf.find(ent), None, build_run_id) for ent in dealer_ids
        ]
        n_clusters = len({uf.find(e) for e in dealer_ids})

        from psycopg2.extras import execute_values

        with conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM discovery_splink_cluster WHERE build_run_id = %s",
                (build_run_id,),
            )
            execute_values(
                cur,
                """
                INSERT INTO discovery_splink_cluster
                    (entity_ulid, splink_cluster, match_weight, build_run_id)
                VALUES %s
                ON CONFLICT (entity_ulid, build_run_id) DO NOTHING
                """,
                rows,
                page_size=5000,
            )
        # dealer-scoped comparison (apples to apples): distinct units among the
        # SAME dealer entities under resolved-only vs unified(resolved+splink).
        resolved_units_dealer = len({resolved.get(e, e) for e in dealer_ids})
        unified_units_dealer = n_clusters
        return {
            "status": "ok",
            "dealer_entities_in": n_in,
            "resolved_units_dealer": resolved_units_dealer,
            "unified_units_dealer": unified_units_dealer,
            "splink_pairs_collapsed": int(splink_collapsed),
            "net_extra_merges_vs_resolved": int(resolved_units_dealer - unified_units_dealer),
            "match_threshold": match_threshold,
        }
    finally:
        conn.close()
