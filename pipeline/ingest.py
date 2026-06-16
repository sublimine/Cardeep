"""FASE 4 — API/INGEST with the live delta engine.

Upserts the dealer entity and reconciles its inventory against the harvest:
  NEW           -> insert vehicle + event
  GONE          -> available vehicle no longer harvested -> status=gone + event
  PRICE_CHANGE  -> price differs -> update price + event
  PHOTO_CHANGE  -> photo_url differs -> update + event
  KM_CHANGE     -> km differs -> update + event
Unchanged rows only refresh last_seen (never an UPDATE of non-mutated data).
Closes with a VAM count quorum (declared == available in DB).

B2.3 — GONE guard: the sweep only fires when harvested >= declared * 0.95.
A partial drain (timeout/error at page N of M) skips the sweep and fires an alert
instead, preventing false GONEs from corrupting the inventory.
"""
from __future__ import annotations

import json

import asyncpg

from pipeline.ids import ulid
from pipeline.identity.make_normalizer import normalize_make
from pipeline.price_sanity import sanitize_km, sanitize_price, sanitize_year, sanitize_year_km
from pipeline.sources.autoscout24 import DealerHarvest, RECIPE_VERSION
from pipeline.geo import GeoResolver
from pipeline.verify import record_count_verdict
from pipeline.delta_guard import should_emit_gone
from pipeline.ops.health import fire_alert, build_origin, resolve_alerts
from services.api.codes import cdp_code


async def _event(conn, vulid, eulid, etype, old, new):
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, old_value, new_value) "
        "VALUES ($1,$2,$3,$4,$5::jsonb,$6::jsonb)",
        ulid(), vulid, eulid, etype,
        json.dumps(old) if old is not None else None,
        json.dumps(new) if new is not None else None)


async def ingest_dealer(conn: asyncpg.Connection, geo: GeoResolver, harvest: DealerHarvest,
                        source_key: str = "as24") -> dict:
    d = harvest.dealer
    if d is None or not d.province_code:
        return {"error": "no dealer / province", "ingested": 0}
    # province must be a real Spanish INE province (01-52); a bad postcode (e.g. zip
    # "89xxx") yields an out-of-range code that would violate the geo FK — skip honestly.
    if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"):
        return {"error": f"province {d.province_code} out of Spain range (bad postcode)", "ingested": 0}

    muni = geo.municipality_code(d.province_code, d.city)
    code = cdp_code(province_code=d.province_code, domain=d.website, name=d.company_name,
                    municipality_code=muni, address=d.street)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, kind_source, legal_name, trade_name,
               province_code, municipality_code, address, postcode, website, is_tier1,
               status, recipe_version, first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa','platform_label',$3,$3,$4,$5,$6,$7,$8,FALSE,'active',$9,$10, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(), recipe_version = EXCLUDED.recipe_version""",
        eulid, code, d.company_name, d.province_code, muni, d.street, d.zip, d.website,
        RECIPE_VERSION, source_key)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, source_key, d.source_dealer_id)

    # current snapshot in DB for this entity
    existing = {r["deep_link"]: r for r in await conn.fetch(
        "SELECT vehicle_ulid, deep_link, price, km, photo_url, status FROM vehicle WHERE entity_ulid=$1",
        eulid)}
    harvested_links = set()
    counts = {"new": 0, "price_change": 0, "photo_change": 0, "km_change": 0, "gone": 0, "unchanged": 0}

    for v in harvest.vehicles:
        harvested_links.add(v.deep_link)
        row = existing.get(v.deep_link)
        # Audit P2 A-junk-sentinel / A-km-year: null unambiguous junk at the boundary (price <=0 or
        # >€10M; km <0 or >1.5M; year <1900 or > next model-year) so impossible values never enter
        # inventory, distort distributions, or trigger a false change event. Used for new and updated.
        price_clean = sanitize_price(v.price)
        km_clean = sanitize_km(v.km)
        year_clean = sanitize_year(v.year)
        # Cross-field impossible-age gate (P8): a ~0-1-yr car with huge km is jointly impossible;
        # NULL both (which field is the parse error is ambiguous, price-dependent). Conservative band.
        year_clean, km_clean = sanitize_year_km(year_clean, km_clean)
        if row is None:
            vulid = ulid()
            # Audit P2 A-make-model: canonical make at the ingest boundary — normalizes a known
            # brand's casing and recovers make from the title's leading brand token when the
            # connector left it NULL (classifieds carry the brand only in the title). Unknown
            # brands are preserved verbatim (never guessed).
            make_norm = normalize_make(v.make, v.title)
            await conn.execute(
                """INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
                       year, km, price, fuel, transmission, photo_url, vin_ref, recipe_version, status)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,'available')""",
                vulid, eulid, v.deep_link, v.title, make_norm, v.model, year_clean, km_clean, price_clean,
                v.fuel, v.transmission, v.photo_url, v.vin_ref, RECIPE_VERSION)
            await _event(conn, vulid, eulid, "NEW", None,
                         {"price": price_clean, "title": v.title})
            counts["new"] += 1
        else:
            vulid = row["vehicle_ulid"]
            changed = False
            set_cols = {}   # columns to fold into ONE merged UPDATE (no per-field dead tuples)
            # Price: fill on NULL→valid promotion AND on value change. The old guard
            # `row["price"] is not None` silently dropped the NULL→valid fill (12k+ vehicles
            # stuck NULL despite the scraper carrying a price).
            if price_clean is not None and (row["price"] is None or float(price_clean) != float(row["price"])):
                set_cols["price"] = price_clean
                await _event(conn, vulid, eulid, "PRICE_CHANGE",
                             {"price": float(row["price"]) if row["price"] is not None else None},
                             {"price": price_clean})
                counts["price_change"] += 1; changed = True
            if km_clean is not None and (row["km"] is None or int(km_clean) != int(row["km"])):
                set_cols["km"] = km_clean
                await _event(conn, vulid, eulid, "KM_CHANGE", {"km": row["km"]}, {"km": km_clean})
                counts["km_change"] += 1; changed = True
            if v.photo_url and v.photo_url != row["photo_url"]:
                set_cols["photo_url"] = v.photo_url
                await _event(conn, vulid, eulid, "PHOTO_CHANGE", {"photo": row["photo_url"]}, {"photo": v.photo_url})
                counts["photo_change"] += 1; changed = True
            if row["status"] != "available":
                set_cols["status"] = "available"
                changed = True
            # ONE merged UPDATE (changed columns + last_seen) → exactly one tuple version per row,
            # instead of a separate UPDATE per field plus an unconditional last_seen UPDATE (which
            # produced up to 3 instantly-dead tuples per changed vehicle per run). Column names are
            # a fixed internal set (never user input); values are parameterized.
            if set_cols:
                cols = list(set_cols.keys())
                assignments = ", ".join(f"{c}=${i + 1}" for i, c in enumerate(cols))
                await conn.execute(
                    f"UPDATE vehicle SET {assignments}, last_seen=now() WHERE vehicle_ulid=${len(cols) + 1}",
                    *[set_cols[c] for c in cols], vulid)
            else:
                await conn.execute("UPDATE vehicle SET last_seen=now() WHERE vehicle_ulid=$1", vulid)
            counts["unchanged"] += int(not changed)

    # GONE: available rows in DB not in this harvest — guarded by B2.3 delta_guard.
    # The sweep only fires when the harvest is demonstrably complete (>=95% of declared).
    # A partial drain (timeout/error cutting pagination early) would otherwise mark the
    # un-fetched pages' vehicles as gone — a false GONE that corrupts the inventory.
    previous_available = sum(1 for r in existing.values() if r["status"] == "available")
    allow_gone, gone_reason = should_emit_gone(
        harvested=len(harvested_links),
        declared=harvest.declared_count,
        previous_available=previous_available,
    )
    if allow_gone:
        for link, row in existing.items():
            if link not in harvested_links and row["status"] == "available":
                await conn.execute("UPDATE vehicle SET status='gone' WHERE vehicle_ulid=$1", row["vehicle_ulid"])
                await _event(conn, row["vehicle_ulid"], eulid, "GONE",
                             {"price": float(row["price"]) if row["price"] else None}, None)
                counts["gone"] += 1
        # Auto-resolve any lingering gone_guard alert for this exact dealer CDP code.
        # The guard is now satisfied (harvest complete >= 95% declared), so the alert
        # that fired on a prior partial run is no longer actionable — close it.
        await resolve_alerts(conn, build_origin("as24", "gone_guard", code))
    else:
        counts["gone_suppressed"] = previous_available - len(
            harvested_links.intersection(
                {lk for lk, r in existing.items() if r["status"] == "available"}
            )
        )
        await fire_alert(
            conn,
            origin=build_origin("as24", "gone_guard", code),
            severity="warning",
            message=(
                f"GONE sweep suppressed for dealer {code}: {gone_reason}"
            ),
            payload={
                "cdp_code": code,
                "harvested": len(harvested_links),
                "declared": harvest.declared_count,
                "previous_available": previous_available,
                "gone_suppressed": counts["gone_suppressed"],
                "reason": gone_reason,
            },
        )

    available = await conn.fetchval(
        "SELECT count(*) FROM vehicle WHERE entity_ulid=$1 AND status='available'", eulid)
    verdict = await record_count_verdict(
        conn, subject_type="entity_inventory", subject_key=code,
        claim="available inventory == source declared count",
        paths={"db_available": available, "harvested": len(harvest.vehicles),
               "source_declared": harvest.declared_count},
        tolerance=0.0)
    return {"cdp_code": code, "entity_ulid": eulid, "available": available,
            "declared": harvest.declared_count, "verdict": verdict, **counts}
