"""Shared "run the matcher for one listing" logic + the incremental background job.

``match_one_listing`` is THE single implementation of "score a wanted_listing against the
live census and persist wanted_match rows" — called synchronously from
``services/api/routers/wanted.py`` (POST /wanted, for the instant "hay N ahora mismo") AND
from ``wanted_matcher_job`` below (the scheduled incremental re-score). One code path, per
the carta's own §7.3 requirement that "el matcher es SQL determinista: ambas vias DEBEN
coincidir" — there is only one vía here, not two that could drift.

Registration: ``wanted_matcher_job`` is wired into ``pipeline/ops/scheduler.py``'s durable
APScheduler (never a standalone process — 00-MASTER.md "Reglas operativas" #7). Cadence is
short (WANTED_MATCHER_CADENCE_MINUTES, default 10) because the carta's entire competitive
claim (§3/§4.4) is reacting to ``vehicle_event NEW`` fast — "AutoTrader alerta en batch 1
vez/dia... Cardeep dispara sobre el hook incremental".
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import asyncpg

from pipeline.ids import ulid
from pipeline.wanted.matcher import (
    MATCH_NOTIFY_THRESHOLD,
    WantedCriteria,
    build_candidate_query,
    build_count_query,
)

log = logging.getLogger(__name__)

WANTED_MATCHER_CADENCE_MINUTES: int = 10


async def _adjacent_provinces(conn: asyncpg.Connection, province_code: str) -> frozenset[str]:
    rows = await conn.fetch(
        "SELECT adjacent_province_code FROM geo_province_adjacency "
        "WHERE country_code = 'ES' AND province_code = $1",
        province_code,
    )
    return frozenset(r["adjacent_province_code"] for r in rows)


async def match_one_listing(conn: asyncpg.Connection, listing: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    """Score the live census for one wanted_listing and UPSERT wanted_match rows.

    Returns (persisted_top_matches, exact_total_count) — the count is UNCAPPED
    (build_count_query), the persisted/returned list is capped at
    matcher.DEFAULT_CANDIDATE_LIMIT (best-score-first).
    """
    wanted_criteria = WantedCriteria(
        make=listing["make"], model=listing["model"],
        year_min=listing["year_min"], year_max=listing["year_max"],
        km_max=listing["km_max"],
        price_max=float(listing["price_max"]) if listing["price_max"] is not None else None,
        province_code=listing["province_code"],
    )
    adjacent = await _adjacent_provinces(conn, listing["province_code"])
    sql, params = build_candidate_query(wanted_criteria, adjacent)
    rows = await conn.fetch(sql, *params)
    count_sql, count_params = build_count_query(wanted_criteria, adjacent)
    exact_count = await conn.fetchval(count_sql, *count_params)

    if not rows:
        return [], exact_count

    now = datetime.now(timezone.utc)
    by_vehicle = {r["vehicle_ulid"]: r for r in rows}
    match_ulids = [ulid() for _ in rows]
    vehicle_ulids = [r["vehicle_ulid"] for r in rows]
    scores = [round(float(r["match_score"]), 2) for r in rows]

    # Bulk UPSERT via a single round-trip (a per-row Python loop measured >4s for 500
    # candidates on cardeep-pg — up to 1000 sequential SELECT+INSERT/UPDATE calls; same class
    # of bug PROGRESO.md already documents for 09-trading-terminal's sale inference: "INSERT
    # por fila -> executemany"/set-based). `xmax = 0` is the standard Postgres idiom for "this
    # row was inserted just now by THIS statement" vs. updated via the ON CONFLICT arm — it
    # lets one statement tell new matches from re-scored ones without a second round-trip.
    async with conn.transaction():
        upserted = await conn.fetch(
            """
            INSERT INTO wanted_match (wanted_match_ulid, wanted_ulid, vehicle_ulid, match_score, matched_at, notified_at)
            SELECT u.match_ulid, $1, u.vehicle_ulid, u.score, $2::timestamptz,
                   CASE WHEN u.score >= $3::numeric THEN $2::timestamptz ELSE NULL END
              FROM unnest($4::text[], $5::text[], $6::numeric[]) AS u(match_ulid, vehicle_ulid, score)
            ON CONFLICT (wanted_ulid, vehicle_ulid) DO UPDATE SET
                match_score = EXCLUDED.match_score,
                notified_at = COALESCE(wanted_match.notified_at,
                                        CASE WHEN EXCLUDED.match_score >= $3::numeric THEN $2::timestamptz ELSE NULL END)
            RETURNING wanted_match_ulid, vehicle_ulid, match_score, matched_at, notified_at, clicked_at,
                      (xmax = 0) AS was_inserted
            """,
            listing["wanted_ulid"], now, MATCH_NOTIFY_THRESHOLD, match_ulids, vehicle_ulids, scores,
        )

        newly_notified = [u for u in upserted if u["was_inserted"] and u["notified_at"] is not None]
        if newly_notified:
            notif_ulids = [ulid() for _ in newly_notified]
            notif_users = [listing["user_ulid"]] * len(newly_notified)
            notif_types = ["wanted_match"] * len(newly_notified)
            notif_payloads = [
                {
                    "wanted_ulid": listing["wanted_ulid"],
                    "wanted_match_ulid": u["wanted_match_ulid"],
                    "vehicle_ulid": u["vehicle_ulid"],
                    "match_score": float(u["match_score"]),
                    "make": by_vehicle[u["vehicle_ulid"]]["make"],
                    "model": by_vehicle[u["vehicle_ulid"]]["model"],
                    "price": float(by_vehicle[u["vehicle_ulid"]]["price"])
                    if by_vehicle[u["vehicle_ulid"]]["price"] is not None else None,
                }
                for u in newly_notified
            ]
            await conn.executemany(
                "INSERT INTO user_notification (notification_ulid, user_ulid, type, payload) VALUES ($1, $2, $3, $4)",
                list(zip(notif_ulids, notif_users, notif_types, notif_payloads)),
            )

    results = [
        {
            **dict(by_vehicle[u["vehicle_ulid"]]),
            "match_score": float(u["match_score"]),
            "wanted_match_ulid": u["wanted_match_ulid"],
            "matched_at": u["matched_at"],
            "notified_at": u["notified_at"],
            "clicked_at": u["clicked_at"],
        }
        for u in upserted
    ]
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results, exact_count


async def _expire_stale_listings(conn: asyncpg.Connection) -> int:
    """carta §4.4 TTL: 'al vencer, status=expired y deja de matchear.' Cheap, additive
    UPDATE — never touches a row that is not actually past its own expires_at."""
    result = await conn.execute(
        "UPDATE wanted_listing SET status = 'expired', updated_at = now() "
        "WHERE status = 'open' AND expires_at <= now()"
    )
    # asyncpg execute() returns a tag string like "UPDATE 3"
    try:
        return int(result.split()[-1])
    except (ValueError, IndexError):
        return 0


async def run_matcher_incremental(dsn: str) -> dict[str, int]:
    """Re-score every OPEN wanted_listing against the current census.

    Correctness over cleverness for v1: rather than tracking a fragile "since which
    vehicle_event" cursor, this simply re-runs match_one_listing (idempotent UPSERT, cheap
    relative to the harvest cadence) for every still-open listing on each tick. Expired
    listings are flipped first so they never get scored. Never raises — a per-listing
    failure is logged and skipped so one bad row cannot take the whole job down (same
    resilience contract as every other job in pipeline/ops/scheduler.py).
    """
    conn = await asyncpg.connect(dsn)
    try:
        await conn.set_type_codec("jsonb", encoder=__import__("json").dumps, decoder=__import__("json").loads, schema="pg_catalog")
        expired = await _expire_stale_listings(conn)

        listings = await conn.fetch("SELECT * FROM wanted_listing WHERE status = 'open'")
        matched_listings = 0
        total_new_matches = 0
        errors = 0
        for row in listings:
            listing = dict(row)
            try:
                before = await conn.fetchval(
                    "SELECT COUNT(*) FROM wanted_match WHERE wanted_ulid = $1", listing["wanted_ulid"]
                )
                results, _exact_count = await match_one_listing(conn, listing)
                after = await conn.fetchval(
                    "SELECT COUNT(*) FROM wanted_match WHERE wanted_ulid = $1", listing["wanted_ulid"]
                )
                matched_listings += 1
                total_new_matches += max(0, after - before)
            except Exception:
                errors += 1
                log.exception("wanted matcher: failed to score listing %s", listing.get("wanted_ulid"))
        return {
            "listings_scored": matched_listings,
            "listings_expired": expired,
            "new_matches": total_new_matches,
            "errors": errors,
        }
    finally:
        await conn.close()
