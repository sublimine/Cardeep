"""Build the discovery_capture matrix from the live DB and read it back.

The capture unit is the *resolved* (cross-source deduped) entity
(v_dealer_resolved.resolved_ulid), so a dealer seen in OSM and in autocasion
collapses to ONE capture row per list — the fix for the old m=10 problem where
unmerged entity_ulids undercounted the overlap.

Strata: province_code x segment (4 broad dealer types) ~ 52 x 4.
"""

from __future__ import annotations

import psycopg2

from pipeline.exhaustiveness.lists import bucket_for, orthogonal_buckets

DSN = "postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep"

DEALER_KINDS = (
    "compraventa",
    "concesionario_oficial",
    "desguace",
    "garaje",
    "subasta",
    "importador",
    "cadena",
    "rent_a_car_vo",
    "oem_vo_portal",
)

# kind -> 4 broad segments (province x segment ~ 200 strata, per §2.2)
_SEGMENT: dict[str, str] = {
    "compraventa": "compraventa",
    "concesionario_oficial": "concesionario",
    "desguace": "desguace",
    "garaje": "otros",
    "subasta": "otros",
    "importador": "otros",
    "cadena": "otros",
    "rent_a_car_vo": "otros",
    "oem_vo_portal": "otros",
}


def segment_for(kind: str) -> str:
    return _SEGMENT.get(kind, "otros")


def _fetch_raw(conn, *, unit: str = "resolved", splink_run_id: str | None = None,
               country_code: str = "ES"):
    """(capture_unit, province_code, kind, source_key) for dealer entities.

    unit="resolved" : capture unit = v_dealer_resolved.resolved_ulid (baseline).
    unit="splink"   : capture unit = discovery_splink_cluster.splink_cluster
                      (probabilistic merge; tighter overlaps). Entities absent
                      from the Splink run fall back to their resolved_ulid.
    country_code    : ISO-3166 alpha-2 tenant filter. Province codes COLLIDE across
                      tenants (0053: DE '28' == ES '28'), so the matrix must be built
                      per country; the entity census carries country_code (0052), so
                      it filters on COALESCE(re.country_code, e.country_code) — the
                      resolved entity's country, falling back to the source entity's.
                      Defaults to 'ES': byte-identical for today's sole tenant.
    """
    if unit == "splink":
        run = splink_run_id or "splink-current"
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(sc.splink_cluster, dr.resolved_ulid) AS unit_id,
                       COALESCE(re.province_code, e.province_code)    AS province_code,
                       COALESCE(re.kind::text, e.kind::text)          AS kind,
                       es.source_key
                FROM entity_source es
                JOIN entity e             ON e.entity_ulid = es.entity_ulid
                JOIN v_dealer_resolved dr ON dr.entity_ulid = es.entity_ulid
                LEFT JOIN discovery_splink_cluster sc
                       ON sc.entity_ulid = es.entity_ulid AND sc.build_run_id = %s
                LEFT JOIN entity re       ON re.entity_ulid = dr.resolved_ulid
                WHERE e.kind::text IN %s
                  AND COALESCE(re.country_code, e.country_code) = %s
                """,
                (run, DEALER_KINDS, country_code),
            )
            return cur.fetchall()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT dr.resolved_ulid,
                   COALESCE(re.province_code, e.province_code) AS province_code,
                   COALESCE(re.kind::text, e.kind::text)       AS kind,
                   es.source_key
            FROM entity_source es
            JOIN entity e            ON e.entity_ulid = es.entity_ulid
            JOIN v_dealer_resolved dr ON dr.entity_ulid = es.entity_ulid
            LEFT JOIN entity re      ON re.entity_ulid = dr.resolved_ulid
            WHERE e.kind::text IN %s
              AND COALESCE(re.country_code, e.country_code) = %s
            """,
            (DEALER_KINDS, country_code),
        )
        return cur.fetchall()


def build(
    build_run_id: str,
    *,
    dsn: str = DSN,
    replace: bool = True,
    unit: str = "resolved",
    splink_run_id: str | None = None,
    country_code: str = "ES",
) -> dict:
    """Populate discovery_capture for a build_run_id. Returns a summary dict.

    country_code : ISO-3166 alpha-2 tenant this build captures. Filters the entity
                   census (province codes collide across tenants — 0053) and is stamped
                   on every discovery_capture row so a per-country read never pools two
                   tenants' strata. Defaults to 'ES': byte-identical for the sole tenant.
    """
    conn = psycopg2.connect(dsn)
    try:
        raw = _fetch_raw(conn, unit=unit, splink_run_id=splink_run_id,
                         country_code=country_code)
        # collapse to distinct (resolved_ulid, bucket) with stratum metadata
        seen: dict[tuple[str, str], tuple[str | None, str]] = {}
        for resolved_ulid, province, kind, source_key in raw:
            bucket = bucket_for(source_key)
            seg = segment_for(kind) if kind else "otros"
            key = (resolved_ulid, bucket)
            if key not in seen:
                seen[key] = (province, seg)
        rows = [
            (ru, bucket, prov, seg, build_run_id, country_code)
            for (ru, bucket), (prov, seg) in seen.items()
        ]
        with conn, conn.cursor() as cur:
            # ensure the lists exist in the reference table
            from pipeline.exhaustiveness.lists import LIST_METADATA, ORTHOGONAL_LISTS

            for lk, (cls, desc) in LIST_METADATA.items():
                cur.execute(
                    """
                    INSERT INTO discovery_list (list_key, orthogonality_class, description, is_orthogonal)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (list_key) DO UPDATE
                      SET orthogonality_class = EXCLUDED.orthogonality_class,
                          description = EXCLUDED.description,
                          is_orthogonal = EXCLUDED.is_orthogonal
                    """,
                    (lk, cls, desc, lk in ORTHOGONAL_LISTS),
                )
            if replace:
                cur.execute(
                    "DELETE FROM discovery_capture WHERE build_run_id = %s",
                    (build_run_id,),
                )
            cur.executemany(
                """
                INSERT INTO discovery_capture
                    (resolved_ulid, list_key, province_code, segment, build_run_id, country_code)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (resolved_ulid, list_key, build_run_id) DO NOTHING
                """,
                rows,
            )
        return {
            "build_run_id": build_run_id,
            "unit": unit,
            "raw_links": len(raw),
            "capture_rows": len(rows),
            "distinct_resolved": len({ru for (ru, _b) in seen}),
        }
    finally:
        conn.close()


def read_patterns(
    build_run_id: str,
    *,
    dsn: str = DSN,
    include_mkt: bool = False,
    province_code: str | None = None,
    segment: str | None = None,
    country_code: str = "ES",
) -> dict[tuple[str | None, str | None], dict[tuple[int, ...], int]]:
    """Read capture patterns per stratum.

    Returns {(province_code, segment): {pattern_tuple: freq}} where pattern is a
    0/1 tuple over ``orthogonal_buckets(include_mkt)`` order. The all-zero pattern
    (entities captured by no orthogonal list) is excluded — it is the unobserved
    cell the MSE estimates.

    country_code : ISO-3166 alpha-2 tenant filter (the same scope seal.compute
                   certifies). Province codes collide across tenants (0053), so the
                   read MUST scope to one country or two tenants' '28' strata pool.
                   Defaults to 'ES': byte-identical for today's sole tenant.
    """
    buckets = orthogonal_buckets(include_mkt)
    idx = {b: i for i, b in enumerate(buckets)}
    conn = psycopg2.connect(dsn)
    try:
        where = ["build_run_id = %s", "country_code = %s"]
        params: list = [build_run_id, country_code]
        if province_code is not None:
            where.append("province_code = %s")
            params.append(province_code)
        if segment is not None:
            where.append("segment = %s")
            params.append(segment)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT resolved_ulid, province_code, segment, list_key
                FROM discovery_capture
                WHERE {' AND '.join(where)}
                """,
                tuple(params),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    # group: (stratum, resolved_ulid) -> set of bucket indices
    by_unit: dict[tuple, tuple[str | None, str | None, list[int]]] = {}
    for resolved_ulid, prov, seg, list_key in rows:
        if list_key not in idx:
            continue  # MKT excluded when include_mkt is False
        ukey = (prov, seg, resolved_ulid)
        if ukey not in by_unit:
            by_unit[ukey] = (prov, seg, [0] * len(buckets))
        by_unit[ukey][2][idx[list_key]] = 1

    out: dict[tuple[str | None, str | None], dict[tuple[int, ...], int]] = {}
    for (prov, seg, _ru), (_p, _s, vec) in by_unit.items():
        pat = tuple(vec)
        if not any(pat):
            continue
        stratum = (prov, seg)
        out.setdefault(stratum, {})
        out[stratum][pat] = out[stratum].get(pat, 0) + 1
    return out, buckets
