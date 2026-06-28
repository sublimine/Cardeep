"""Recipe -> delta bridge (country-autopilot §02 build-order D): tie the cracker's
VERIFIED extraction to the live delta engine.

THE GAP THIS CLOSES
-------------------
Today the recipe path and the delta path run SEPARATELY. The harness
(``recipe_harness.py`` step 5) and the cracker (``recipe_cracker.py``:
``sample.parsed.clear()``) VERIFY a bounded sample and then DELETE it — the
verified cars never reach ``vehicle`` and no ``vehicle_event`` is ever emitted. So a
recipe can be VERIFIED while inventory stays empty and the timeline silent. This
bridge is the OPT-IN tie: given a VERIFIED recipe's already-minted ``cdp_code`` and
its extracted cars, it ingests them and emits the five canonical delta events
(NEW / PRICE_CHANGE / KM_CHANGE / PHOTO_CHANGE / GONE). The cracker stays free to
*only-verify* (today's behaviour) OR to *verify + ingest + delta* (call this).

REUSE, NOT REIMPLEMENTATION
---------------------------
The delta SEMANTICS are NOT re-derived here — they are the shared, connector-agnostic
machinery of ``pipeline.delta`` (the same emitters the 26 wholesale connectors use):
  * PRICE/KM/PHOTO on RE-SEEN cars  -> :func:`pipeline.delta.emit_change_deltas`
                                       (which calls the pure ``diff_vehicle``);
  * GONE on retired cars            -> :func:`pipeline.delta.emit_gone_events`
                                       (idempotent, append-only timeline);
  * GONE SAFETY                     -> :func:`pipeline.delta_guard.should_emit_gone`
                                       (B2.3: never retire on a partial/bounded harvest).
Only the NEW-vehicle INSERT + NEW event is written directly here — exactly as every
connector and ``pipeline.ingest`` already do it (there is NO shared NEW helper in the
codebase; the NEW event is ``old=NULL, new={"price","title"}``, the ingest.py
convention).

WHY NOT ``pipeline.ingest.ingest_dealer``?
------------------------------------------
``ingest_dealer`` is the AutoScout24 / ES path: it REQUIRES a ``DealerHarvest`` whose
dealer carries a Spanish province in ``01..52`` (it hard-rejects anything else),
RE-DERIVES its OWN cdp_code from the dealer fields, and needs a live ``GeoResolver``.
The cracker is country-generic and is keyed by an ALREADY-MINTED ``cdp_code``. Routing
the generic cracker output back through that ES dealer path would re-introduce the
exact ES-hardcoding the country-autopilot exists to remove. So the bridge reuses the
connector-agnostic ``pipeline.delta`` emitters and is keyed by ``cdp_code`` —
source-agnostic and country-agnostic. It branches on NO country and reads NO geo.

GONE ON A BOUNDED SAMPLE (the load-bearing safety point)
--------------------------------------------------------
The cracker pulls a BOUNDED sample (k≈3-5), not necessarily the whole inventory.
Running a naive GONE over a sample would retire the dealer's real stock. The bridge
therefore gates GONE through ``should_emit_gone(harvested, declared, previous_available)``
with the ``declared`` total the caller passes (the cracker's ``Sample.declared``):
GONE fires only when the harvest is provably complete (``harvested >= declared*0.95``),
otherwise it is SUPPRESSED and reported in ``gone_suppressed`` — never a false GONE.

dry_run
-------
Default ``dry_run=True`` runs the FULL ingest+delta inside a SAVEPOINT and ROLLS IT
BACK: the caller gets the exact event counts that WOULD be emitted with zero
persistence (sample-verify-delete doctrine; safe to preview against any DB). With
``dry_run=False`` the savepoint is released and the writes land in the caller's
transaction. Either way the caller owns the OUTER transaction boundary.

INPUT CONTRACT
--------------
``vehicles`` is the cracker sample: an iterable of either dicts (``Sample.parsed`` is
``[asdict(Vehicle) ...]``) or objects, each exposing the ``pipeline.sources.autoscout24``
``Vehicle`` field names: ``deep_link`` (required — the per-listing key), ``vin_ref``,
``title``, ``make``, ``model``, ``year``, ``km``, ``price``, ``fuel``,
``transmission``, ``photo_url``, and optionally ``photo_hash``. Items with no
``deep_link`` cannot be keyed and are skipped (counted in ``skipped_no_link``).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, fields
from typing import Iterable

import asyncpg

from pipeline.delta import emit_change_deltas, emit_gone_events
from pipeline.delta_guard import should_emit_gone
from pipeline.ids import ulid
from pipeline.identity.make_normalizer import normalize_make
from pipeline.price_sanity import sanitize_km, sanitize_price, sanitize_year, sanitize_year_km


# ---------------------------------------------------------------------------
# Vehicle normalization — accept the cracker's dicts OR objects, uniformly.
# Field names mirror pipeline.sources.autoscout24.Vehicle (the sample's asdict shape).
# ---------------------------------------------------------------------------
@dataclass
class _Veh:
    deep_link: str
    vin_ref: str | None = None
    title: str | None = None
    make: str | None = None
    model: str | None = None
    year: int | None = None
    km: int | None = None
    price: float | None = None
    fuel: str | None = None
    transmission: str | None = None
    photo_url: str | None = None
    photo_hash: str | None = None


_VEH_FIELDS = tuple(f.name for f in fields(_Veh))


def _get(item: object, key: str):
    """Read ``key`` from a dict OR an object attribute (None when absent)."""
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _normalize(item: object) -> _Veh | None:
    """Coerce one cracker car (dict or object) into a :class:`_Veh`; None if unkeyable."""
    deep_link = _get(item, "deep_link")
    if not deep_link:
        return None
    return _Veh(**{name: _get(item, name) for name in _VEH_FIELDS})


# ---------------------------------------------------------------------------
# The bridge.
# ---------------------------------------------------------------------------
async def ingest_and_delta(
    conn: asyncpg.Connection,
    cdp_code: str,
    source_key: str,
    vehicles: Iterable[object],
    *,
    declared: int | None = None,
    recipe_version: int | None = None,
    dry_run: bool = True,
) -> dict:
    """Ingest the cracker's VERIFIED cars for ``cdp_code`` and emit the five delta events.

    Args:
        conn:           Active asyncpg connection. The bridge runs its work in a SAVEPOINT
                        of the caller's transaction (the caller owns the outer boundary).
        cdp_code:       The recipe's already-minted entity code. The entity MUST already
                        exist (minted at discovery); a missing entity returns an honest
                        ``{"error": ...}`` — never a silent pass and never a re-mint.
        source_key:     Provenance key (e.g. the winning rung's source) recorded on
                        ``entity_source`` and used as the source attestation.
        vehicles:       The cracker sample (see the module INPUT CONTRACT).
        declared:       The source's declared inventory total (the cracker's
                        ``Sample.declared``). Drives the GONE safety guard so a bounded
                        sample cannot retire real stock. ``None`` falls back to the
                        ``previous_available`` probe (see ``should_emit_gone``).
        recipe_version: Optional version stamp written to ``vehicle.recipe_version`` for
                        NEW rows. Left ``NULL`` when omitted (the recipe YAML is the
                        version source of truth; the bridge never invents one).
        dry_run:        ``True`` (default) -> roll the SAVEPOINT back (preview the counts,
                        persist nothing). ``False`` -> release it (writes land in the
                        caller's transaction).

    Returns:
        A summary dict: ``new / price_change / km_change / photo_change / gone`` counts,
        plus ``cdp_code, entity_ulid, source_key, harvested, reseen, previous_available,
        declared, gone_allowed, gone_reason, gone_suppressed, skipped_no_link, dry_run``.
        On a missing entity: ``{"error", "cdp_code", "entity_ulid": None, ...}``.
    """
    tx = conn.transaction()
    await tx.start()
    try:
        result = await _ingest_and_delta(
            conn, cdp_code, source_key, vehicles,
            declared=declared, recipe_version=recipe_version)
    except BaseException:
        # Surface failures honestly: undo this bridge's savepoint, never a half-write.
        await tx.rollback()
        raise
    # dry_run previews: the counts are already computed; discard the writes.
    if dry_run:
        await tx.rollback()
    else:
        await tx.commit()
    return {**result, "dry_run": dry_run}


async def _ingest_and_delta(
    conn: asyncpg.Connection,
    cdp_code: str,
    source_key: str,
    vehicles: Iterable[object],
    *,
    declared: int | None,
    recipe_version: int | None,
) -> dict:
    counts = {"new": 0, "price_change": 0, "km_change": 0, "photo_change": 0, "gone": 0}

    # 1) Normalize + dedup by deep_link (first wins, mirroring harvest_dealer's seen-set).
    norm: list[_Veh] = []
    seen_links: set[str] = set()
    skipped_no_link = 0
    for raw in vehicles:
        v = _normalize(raw)
        if v is None:
            skipped_no_link += 1
            continue
        if v.deep_link in seen_links:
            continue
        seen_links.add(v.deep_link)
        norm.append(v)

    # 2) Resolve the entity by cdp_code. It must pre-exist (minted at discovery): the
    #    bridge ties an EXISTING entity to the delta, it does not mint identities.
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", cdp_code)
    if eulid is None:
        return {
            "error": f"no entity for cdp_code {cdp_code!r}; mint it at discovery before the tie",
            "cdp_code": cdp_code, "entity_ulid": None, "source_key": source_key,
            "harvested": len(norm), "reseen": 0, "previous_available": 0,
            "declared": declared, "gone_allowed": False, "gone_reason": "entity missing",
            "gone_suppressed": 0, "skipped_no_link": skipped_no_link, **counts,
        }

    # 3) Attest the source (provenance), mirroring ingest_dealer's entity_source upsert.
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, source_key, cdp_code)

    # 4) Current DB snapshot for this entity, keyed by deep_link. photo_hash is pulled so the
    #    re-seen snapshot can drive diff_vehicle's content-aware (perceptual-hash) PHOTO_CHANGE
    #    path — the bridge writes photo_hash on NEW, so it must also offer it back for comparison.
    existing = {r["deep_link"]: r for r in await conn.fetch(
        "SELECT vehicle_ulid, deep_link, price, km, photo_url, photo_hash, status "
        "FROM vehicle WHERE entity_ulid=$1", eulid)}
    previous_available = sum(1 for r in existing.values() if r["status"] == "available")

    # 5) Reconcile harvested cars: NEW inserts inline; RE-SEEN routed to emit_change_deltas.
    harvested_links: set[str] = set()
    reseen_snap: dict[tuple[str, str], dict] = {}
    reseen_new: dict[tuple[str, str], _Veh] = {}
    reseen_keys: list[tuple[str, str]] = []

    for v in norm:
        harvested_links.add(v.deep_link)
        row = existing.get(v.deep_link)
        if row is None:
            await _insert_new(conn, eulid, v, recipe_version)
            counts["new"] += 1
            continue
        # Re-seen: feed the shared PRICE/KM/PHOTO emitter (key convention = (entity, link),
        # so emit_change_deltas reads entity_ulid from key[0], matching the connectors).
        key = (eulid, v.deep_link)
        reseen_snap[key] = {
            "vehicle_ulid": row["vehicle_ulid"], "price": row["price"],
            "km": row["km"], "photo_url": row["photo_url"], "photo_hash": row["photo_hash"]}
        reseen_new[key] = v
        reseen_keys.append(key)
        # A previously-gone car re-seen this run is re-listed (mirrors ingest_dealer).
        if row["status"] != "available":
            await conn.execute(
                "UPDATE vehicle SET status='available', last_seen=now() WHERE vehicle_ulid=$1",
                row["vehicle_ulid"])

    # PRICE/KM/PHOTO_CHANGE via the shared, tested emitter (reuse — NOT reimplemented).
    change_counts = await emit_change_deltas(conn, reseen_snap, reseen_new, reseen_keys)
    counts["price_change"] = change_counts.get("PRICE_CHANGE", 0)
    counts["km_change"] = change_counts.get("KM_CHANGE", 0)
    counts["photo_change"] = change_counts.get("PHOTO_CHANGE", 0)

    # Refresh last_seen for EVERY re-seen vehicle (changed or not), mirroring ingest_dealer: a
    # re-seen car WAS seen this run. emit_change_deltas only touches rows whose price/km/photo
    # changed, so this explicit batched touch keeps last_seen truthful and stops a downstream
    # last_seen-based sweep (reconcile_gone) from false-retiring unchanged bridge inventory.
    if reseen_keys:
        await conn.execute(
            "UPDATE vehicle SET last_seen=now() WHERE vehicle_ulid = ANY($1::text[])",
            [reseen_snap[k]["vehicle_ulid"] for k in reseen_keys])

    # 6) GONE — guarded so a bounded/partial sample can never retire real inventory.
    allow_gone, gone_reason = should_emit_gone(
        harvested=len(harvested_links), declared=declared,
        previous_available=previous_available)
    gone_suppressed = 0
    if allow_gone:
        gone_ulids: list[str] = []
        for link, row in existing.items():
            if link not in harvested_links and row["status"] == "available":
                # Flip status first (fires the gone->listing propagation trigger), then
                # emit the GONE event via the shared emitter (price snapshot + idempotent).
                await conn.execute(
                    "UPDATE vehicle SET status='gone' WHERE vehicle_ulid=$1", row["vehicle_ulid"])
                gone_ulids.append(row["vehicle_ulid"])
        counts["gone"] = await emit_gone_events(conn, gone_ulids)
    else:
        gone_suppressed = sum(
            1 for link, row in existing.items()
            if link not in harvested_links and row["status"] == "available")

    return {
        "cdp_code": cdp_code, "entity_ulid": eulid, "source_key": source_key,
        "harvested": len(harvested_links), "reseen": len(reseen_keys),
        "previous_available": previous_available, "declared": declared,
        "gone_allowed": allow_gone, "gone_reason": gone_reason,
        "gone_suppressed": gone_suppressed, "skipped_no_link": skipped_no_link, **counts,
    }


async def _insert_new(conn: asyncpg.Connection, eulid: str, v: _Veh,
                      recipe_version: int | None) -> None:
    """Insert a NEW vehicle (sanitized at the boundary) + its NEW event.

    Boundary cleaning mirrors ``pipeline.ingest.ingest_dealer`` exactly: junk price/km/year
    are nulled (never enter inventory or fire a false change), the cross-field impossible
    age band is applied, and the make is canonicalized (recovered from the title when the
    extractor left it NULL). The NEW event is ``old=NULL, new={"price","title"}`` — the
    one NEW convention shared by ingest.py and every wholesale connector.
    """
    price_clean = sanitize_price(v.price)
    km_clean = sanitize_km(v.km)
    year_clean = sanitize_year(v.year)
    year_clean, km_clean = sanitize_year_km(year_clean, km_clean)
    make_norm = normalize_make(v.make, v.title)
    vulid = ulid()
    await conn.execute(
        """INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
               year, km, price, fuel, transmission, photo_url, photo_hash, vin_ref,
               recipe_version, status)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,'available')""",
        vulid, eulid, v.deep_link, v.title, make_norm, v.model, year_clean, km_clean,
        price_clean, v.fuel, v.transmission, v.photo_url, v.photo_hash, v.vin_ref,
        recipe_version)
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value) VALUES ($1,$2,$3,'NEW',NULL,$4::jsonb)",
        ulid(), vulid, eulid,
        json.dumps({"price": float(price_clean) if price_clean is not None else None,
                    "title": v.title}))
