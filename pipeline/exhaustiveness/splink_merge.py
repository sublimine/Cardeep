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
from pipeline.identity.phone import phone_match_key
from pipeline.paths import DEFAULT_COUNTRY

_WS = re.compile(r"\s+")
_NONAL = re.compile(r"[^a-z0-9 ]+")
# Legal-form suffixes, matched at END after punctuation is collapsed to spaces, so "S.L." -> "s l"
# and "SLU" -> "slu" are both caught. The set is PER COUNTRY: each tenant strips its OWN legal forms
# and never another country's (an ES "s l" is a real token inside a German name, and vice-versa). ES is
# the verbatim original — byte-identical. After _NONAL collapses punctuation to spaces, the DE forms
# render as "gmbh", "gmbh co kg" (GmbH & Co. KG), "ag" and "e k" (e.K.); OPS extends a country's set
# (e.g. UG/KG/OHG/GbR) here. A country with no entry strips nothing.
_SUFFIX_ES = re.compile(
    r"\s+(s\s*l\s*u|s\s*a\s*u|s\s*l\s*l|s\s*l|s\s*a|s\s*c\s*p|s\s*c|c\s*b"
    r"|sociedad limitada|sociedad anonima|unipersonal)\s*$"
)
_SUFFIX_DE = re.compile(r"\s+(g\s*m\s*b\s*h(\s*co\s*k\s*g)?|a\s*g|e\s*k)\s*$")
_SUFFIX_BY_COUNTRY: dict[str, "re.Pattern[str]"] = {"ES": _SUFFIX_ES, "DE": _SUFFIX_DE}


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


def _norm_name(s: str | None, country_code: str = DEFAULT_COUNTRY) -> str | None:
    if not s:
        return None
    s = _fold(s.lower().strip())
    s = _NONAL.sub(" ", s)          # punctuation -> space first
    s = _WS.sub(" ", s).strip()
    suffix_re = _SUFFIX_BY_COUNTRY.get(country_code)
    if suffix_re is not None:
        s = suffix_re.sub("", s)    # then strip trailing legal form (the country's OWN set)
        s = _WS.sub(" ", s).strip()
    return s or None


def _host(url: str | None) -> str | None:
    if not url:
        return None
    m = re.search(r"https?://([^/]+)", url.lower())
    host = (m.group(1) if m else url.lower()).strip()
    host = re.sub(r"^www\.", "", host)
    return host or None


def _digits(phone: str | None, country_code: str = DEFAULT_COUNTRY) -> str | None:
    """Cross-source phone hard key via the country-aware identity authority (pipeline.identity.phone).

    ES (default) -> the validated 9-digit national key: byte-identical to the legacy last-9 for a real
    Spanish number, but a malformed string now yields None instead of a fragile substring — exactly the
    hardening cross_source_dedup already adopted (fewer false-positive phone edges). Non-ES -> a
    collision-proof E.164 key (a German +49 line can never collide with an ES +34 key)."""
    return phone_match_key(phone, country_code)


def _load_dealers(conn, country_code: str = DEFAULT_COUNTRY):
    import pandas as pd

    with conn.cursor() as cur:
        # Country filter (indexed idx_entity_country): province / municipality codes COLLIDE across
        # tenants (0053: DE '28' == ES Madrid '28'), so the dealer universe MUST be scoped to one
        # country or two tenants' dealers would block/merge together. ES is byte-identical (the
        # single-tenant census is all 'ES', so the filter returns the same rows as before).
        cur.execute(
            """
            SELECT e.entity_ulid,
                   COALESCE(e.trade_name, e.legal_name) AS name,
                   e.province_code, e.municipality_code,
                   e.phone, e.website, e.lat, e.lon
            FROM entity e
            WHERE e.kind::text IN %s
              AND e.country_code = %s
            """,
            (DEALER_KINDS, country_code),
        )
        rows = cur.fetchall()
    recs = []
    for ulid, name, prov, muni, phone, website, lat, lon in rows:
        nm = _norm_name(name, country_code)
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
                "phone": _digits(phone, country_code),
                "website_host": _host(website),
                "lat": float(lat) if lat is not None else None,
                "lon": float(lon) if lon is not None else None,
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


def run(build_run_id: str, *, dsn: str = DSN, match_threshold: float = 0.9,
        country_code: str = DEFAULT_COUNTRY) -> dict:
    """Run Splink dedupe over dealer entities and persist clusters. Returns summary.

    country_code : ISO-3166 alpha-2 tenant whose dealer universe is deduped. Scopes the entity load
                   and the name/phone keys to that country; defaults to 'ES' (byte-identical)."""
    if not splink_available():
        return {"status": "splink_unavailable"}

    from splink import DuckDBAPI, Linker, SettingsCreator, block_on
    import splink.comparison_library as cl

    conn = psycopg2.connect(dsn)
    try:
        df = _load_dealers(conn, country_code)
        n_in = len(df)

        settings = SettingsCreator(
            link_type="dedupe_only",
            blocking_rules_to_generate_predictions=[
                # block on muni + name PREFIX (not full name) so JaroWinkler can
                # score fuzzy full-name pairs inside the block.
                block_on("municipality_code", "name_prefix"),
                block_on("phone"),
                block_on("website_host"),
            ],
            comparisons=[
                cl.JaroWinklerAtThresholds("name", [0.92, 0.82]),
                cl.ExactMatch("municipality_code"),
                cl.ExactMatch("phone").configure(term_frequency_adjustments=True),
                cl.ExactMatch("website_host").configure(term_frequency_adjustments=True),
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
