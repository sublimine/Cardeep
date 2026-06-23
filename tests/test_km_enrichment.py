"""Regression guard + documentation for the KM_CHANGE under-collection (audit km_enrich).

CONTEXT (verified against live PG :5433 + real source on 2026-06-23)
-------------------------------------------------------------------
vehicle_event delta-type distribution is lopsided:
    NEW           2,339,064  (87.67%)
    PRICE_CHANGE    145,892  ( 5.47%)
    GONE            109,153  ( 4.09%)
    PHOTO_CHANGE     62,132  ( 2.33%)
    KM_CHANGE        11,693  ( 0.44%)   <- ~12x under PRICE
KM is the rarest non-GONE delta. The audit traced this to a WIRING gap, NOT a
sensitivity gap in the shared diff helper:

  * 26 wholesale connectors route RE-SEEN vehicles through the shared
    pipeline.delta.emit_change_deltas (-> diff_vehicle), which has a correct
    KM_CHANGE branch (delta.py:326-334, incl. the NULL->valid promotion). These
    carry km: live wallapop 2,313 / coches_net 4,476 / milanuncios 2,871 /
    coches_com 813 KM_CHANGE.
  * autocasion_wholesale.py is the lone hold-out (predates the shared helper).
    It PARSES km (autocasion_wholesale.py:246-248) and writes it on the NEW
    insert (line 525), but on RE-SEEN it calls ONLY its bespoke
    capture_price_drop (price-only, lines 559-578) and upsert_vehicle's re-seen
    branch (lines 514-518) refreshes ONLY last_seen+status — never km/photo. So
    km is captured once then frozen; every later km (and photo) change is
    dropped. Live proof: autocasion_wholesale 4,073 PRICE_CHANGE but 0 KM and 0
    PHOTO; autocasion_census 3,538 PRICE / 0 KM / 0 PHOTO.

WHAT THIS FILE GUARDS
---------------------
1. Unit (DB-free): the shared diff_vehicle KM branch behaves correctly — change
   detected, NULL->valid promotion fills, junk km (Wallapop 1.5M sentinel /
   negative) is dropped, no false positive. This is the contract every "should
   carry km" connector inherits via emit_change_deltas; if it regresses, the
   km column silently stops filling fleet-wide.
2. Unit (DB-free, static source): the 26 connectors that SHOULD carry km DO wire
   emit_change_deltas (regression guard against a connector silently reverting
   to a NEW-only / bespoke path), and autocasion is pinned as the KNOWN gap
   (when the operator migrates it onto emit_change_deltas the pin flips and this
   test must be updated — see test docstring).
3. Integration (live PG, auto-skip): the under-collection is documented as a
   live assertion — connectors that should carry km DO (>0 KM_CHANGE) and
   autocasion's gap is recorded (0 KM / 0 PHOTO, >0 PRICE).

OPERATOR ACTION (the extractor fix — NOT applied here; live-connector edits are
risky and out of scope for a test file):
  Migrate autocasion_wholesale.py (and the census/facet variants that share
  process_ref) OFF the bespoke capture_price_drop and ONTO the shared
  pipeline.delta.emit_change_deltas, the SAME pattern the 26 connectors use:
  build the pre-run existing_snap {key:{vehicle_ulid,price,km,photo_url}} + the
  new_vehicles dict for the harvested window, then call
  emit_change_deltas(conn, existing_snap, new_vehicles, keys) inside the
  per-window transaction. That emits PRICE+KM+PHOTO deltas and refreshes the
  served row via COALESCE(sanitize(...)), junk-guarded by sanitize_km
  (price_sanity.py:69, nulls <0 and the >=1.5M Wallapop sentinel). It also
  fixes autocasion's 0 PHOTO_CHANGE in the same move. The residual KM gap after
  autocasion is structurally bounded: census/discovery source_keys never
  re-scrape the same listing, so they legitimately emit few/no km deltas.
  DO NOT widen the diff_vehicle km tolerance — the gap is wiring, not
  sensitivity.
"""
from __future__ import annotations

import asyncio
import pathlib
from dataclasses import dataclass

import asyncpg
import pytest

from pipeline.delta import diff_vehicle

# --------------------------------------------------------------------------- #
# Constants anchored to verified facts
# --------------------------------------------------------------------------- #

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

_PLATFORM_DIR = pathlib.Path(__file__).parents[1] / "pipeline" / "platform"

# Connectors that SHOULD carry km because they route RE-SEEN vehicles through
# the shared pipeline.delta.emit_change_deltas (which has the KM_CHANGE branch).
# Verified live to actually emit KM_CHANGE (counts captured 2026-06-23):
#   wallapop 2,313 / coches_net 4,476 / milanuncios 2,871 / coches_com 813.
# These four are the high-volume, re-scraping platform sources where a km change
# on a re-seen listing is both expected and observed.
_SHOULD_CARRY_KM = {
    "wallapop_wholesale": 2_313,
    "coches_net_wholesale": 4_476,
    "milanuncios_wholesale": 2_871,
    "coches_com_wholesale": 813,
}

# The full adopter set wired to emit_change_deltas (the shared km path). Source
# of truth = `grep -rl emit_change_deltas pipeline/platform/*.py` -> 26 modules.
# If a connector here ever drops the import it has reverted to a km-blind path.
_EMIT_CHANGE_DELTAS_ADOPTERS = {
    "carandclassic_wholesale",
    "coches_com_wholesale",
    "coches_net_segments",
    "coches_net_wholesale",
    "dasweltauto_wholesale",
    "faciliteacoches_racc_wholesale",
    "group_importador_wholesale",
    "group_subastas_wholesale",
    "group_vo_chains_wholesale",
    "miclasico_wholesale",
    "milanuncios_wholesale",
    "motor_es_wholesale",
    "oem_audi_wholesale",
    "oem_bmw_mini_wholesale",
    "oem_ford_wholesale",
    "oem_hyundai_wholesale",
    "oem_kia_wholesale",
    "oem_mercedes_benz_wholesale",
    "oem_nissan_mazda_honda_wholesale",
    "oem_seat_cupra_new_stock",
    "oem_seat_cupra_wholesale",
    "oem_toyota_lexus_wholesale",
    "oem_volvo_jlr_suzuki_wholesale",
    "renew_wholesale",
    "spoticar_wholesale",
    "wallapop_wholesale",
}

# autocasion is the KNOWN under-collector (parses km, never re-diffs it).
_AUTOCASION_CONNECTOR = "autocasion_wholesale"

# Live event-type ratios (verified 2026-06-23). KM is ~12x under PRICE.
_KM_PCT_OF_PRICE_CEILING = 0.20  # KM_CHANGE/PRICE_CHANGE was 0.080 live; assert it stays under-collected


# --------------------------------------------------------------------------- #
# DB reachability gate (mirror tests/test_reconcile_gone_coverage.py)
# --------------------------------------------------------------------------- #

def _db_ok() -> bool:
    async def _p() -> bool:
        try:
            c = await asyncpg.connect(DSN, timeout=3)
            await c.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_p())
    except Exception:
        return False


SKIP_DB = pytest.mark.skipif(not _db_ok(), reason="cardeep-pg not reachable")


def _query(coro_fn):
    """Run a read-only coroutine against the live DB (no writes; nothing to roll back)."""
    async def body():
        c = await asyncpg.connect(DSN)
        try:
            return await coro_fn(c)
        finally:
            await c.close()
    return asyncio.run(body())


# --------------------------------------------------------------------------- #
# Test double for diff_vehicle's `new` argument
# --------------------------------------------------------------------------- #

@dataclass
class FakeVehicle:
    """Minimal scraped vehicle object consumed by diff_vehicle (attrs only)."""
    price: float | None = None
    km: int | None = None
    photo_url: str | None = None
    photo_hash: str | None = None


# =========================================================================== #
# 1. UNIT — the shared KM_CHANGE contract every "should carry km" connector
#    inherits via emit_change_deltas -> diff_vehicle. (DB-free.)
# =========================================================================== #

@pytest.mark.unit
class TestSharedKmDeltaContract:
    """diff_vehicle is the single km-diff brain for the 26 emit_change_deltas
    connectors. If this contract breaks, km silently stops filling fleet-wide —
    the exact failure mode autocasion exhibits, but for everyone."""

    def test_km_change_detected(self) -> None:
        """A re-seen vehicle whose odometer advanced must emit KM_CHANGE."""
        old = {"price": None, "km": 80_000, "photo_url": None}
        new = FakeVehicle(km=82_000)
        events = diff_vehicle(old, new)
        km = [e for e in events if e["event_type"] == "KM_CHANGE"]
        assert len(km) == 1, "odometer advance must emit exactly one KM_CHANGE"
        assert km[0]["old_value"] == {"km": 80_000}
        assert km[0]["new_value"] == {"km": 82_000}

    def test_km_null_old_promotes_to_value(self) -> None:
        """NULL->valid promotion: a listing first seen without km that later
        publishes one must FILL (emit KM_CHANGE old=None->new), not stay NULL
        forever. The old asymmetric guard dropped this transition fleet-wide."""
        old = {"price": None, "km": None, "photo_url": None}
        new = FakeVehicle(km=50_000)
        events = diff_vehicle(old, new)
        km = [e for e in events if e["event_type"] == "KM_CHANGE"]
        assert len(km) == 1
        assert km[0]["old_value"] == {"km": None}
        assert km[0]["new_value"] == {"km": 50_000}

    def test_km_unchanged_no_event(self) -> None:
        """Identical odometer between runs must NOT emit a spurious KM_CHANGE."""
        old = {"price": None, "km": 60_000, "photo_url": None}
        new = FakeVehicle(km=60_000)
        assert not any(e["event_type"] == "KM_CHANGE" for e in diff_vehicle(old, new))

    def test_km_int_float_no_false_positive(self) -> None:
        """An int km vs the same value as a numeric string-parsed int is unchanged."""
        old = {"price": None, "km": 100_000, "photo_url": None}
        new = FakeVehicle(km=int("100000"))
        assert not any(e["event_type"] == "KM_CHANGE" for e in diff_vehicle(old, new))

    def test_junk_km_sentinel_dropped(self) -> None:
        """sanitize_km nulls the Wallapop 1.5M UNSET sentinel and negatives, so a
        junk scrape never overwrites a valid stored km via the delta path
        (price_sanity.py:69, >= 1.5M boundary)."""
        old = {"price": None, "km": 90_000, "photo_url": None}
        for junk in (-1, 1_500_000, 2_000_000):
            events = diff_vehicle(old, FakeVehicle(km=junk))
            assert not any(e["event_type"] == "KM_CHANGE" for e in events), (
                f"junk km {junk} must be sanitized to None -> no KM_CHANGE"
            )

    def test_km_none_new_no_event(self) -> None:
        """If the fresh scrape has no km (None), do not emit KM_CHANGE — absence
        is not a change (mirrors the price None-new rule)."""
        old = {"price": None, "km": 70_000, "photo_url": None}
        new = FakeVehicle(km=None)
        assert not any(e["event_type"] == "KM_CHANGE" for e in diff_vehicle(old, new))


# =========================================================================== #
# 2. UNIT — static source guard: who SHOULD carry km does wire the shared path,
#    and autocasion is pinned as the KNOWN gap. (DB-free; reads source text.)
# =========================================================================== #

@pytest.mark.unit
class TestKmWiringStaticGuard:
    """Source-level regression guard. The km under-collection is a WIRING gap:
    carriers route re-seen vehicles through emit_change_deltas; the hold-out
    (autocasion) does not. Pin both so a silent revert is caught at test time."""

    @staticmethod
    def _src(connector: str) -> str:
        return (_PLATFORM_DIR / f"{connector}.py").read_text(encoding="utf-8")

    def test_high_volume_carriers_wire_emit_change_deltas(self) -> None:
        """The four live high-volume km carriers must keep wiring the shared
        delta path. Losing the import = reverting to a km-blind re-seen path."""
        for connector in _SHOULD_CARRY_KM:
            src = self._src(connector)
            assert "emit_change_deltas" in src, (
                f"{connector}.py must route re-seen vehicles through "
                f"pipeline.delta.emit_change_deltas to carry KM_CHANGE; the "
                f"import is gone -> km will silently stop filling for this source."
            )

    def test_full_adopter_set_intact(self) -> None:
        """All 26 connectors recorded as emit_change_deltas adopters still wire
        it. This is the fleet-wide km/photo/price delta backbone."""
        missing = sorted(
            c for c in _EMIT_CHANGE_DELTAS_ADOPTERS
            if "emit_change_deltas" not in self._src(c)
        )
        assert not missing, (
            f"connectors dropped emit_change_deltas (km/photo deltas regress): {missing}"
        )

    def test_autocasion_is_the_known_gap(self) -> None:
        """PINNED KNOWN-GAP: autocasion parses km but does NOT route re-seen
        vehicles through the shared delta helper — it uses its bespoke
        price-only capture_price_drop, so it emits 0 KM_CHANGE / 0 PHOTO_CHANGE.

        WHEN THE OPERATOR FIXES IT (migrate autocasion onto emit_change_deltas,
        per this module's docstring), this assertion WILL FAIL — that failure is
        the signal to move autocasion into _EMIT_CHANGE_DELTAS_ADOPTERS /
        _SHOULD_CARRY_KM and delete this pin. Until then it documents the gap so
        the regression-guard set above stays honest (autocasion must NOT be
        silently counted among the carriers)."""
        src = self._src(_AUTOCASION_CONNECTOR)
        # It DOES parse km (capability is present; the gap is the re-seen wiring).
        assert "kilometers" in src, (
            "autocasion is expected to PARSE km (ad['kilometers']); if it no "
            "longer does, the analysis premise changed — re-audit."
        )
        # It still uses the bespoke price-only delta, NOT the shared helper.
        assert "capture_price_drop" in src, (
            "autocasion's bespoke price-only delta marker vanished — re-check "
            "whether it migrated to emit_change_deltas (then update this pin)."
        )
        assert "emit_change_deltas" not in src, (
            "autocasion now imports emit_change_deltas — the km/photo gap is "
            "FIXED. Move 'autocasion_wholesale' into _EMIT_CHANGE_DELTAS_ADOPTERS "
            "and _SHOULD_CARRY_KM, then remove this known-gap pin."
        )


# =========================================================================== #
# 3. INTEGRATION — live documentation of the under-collection. (Auto-skip.)
# =========================================================================== #

async def _km_count(c: asyncpg.Connection, source_key: str) -> int:
    return await c.fetchval(
        "SELECT count(*) FROM vehicle_event ve "
        "JOIN entity_source es ON es.entity_ulid = ve.entity_ulid "
        "WHERE es.source_key = $1 AND ve.event_type = 'KM_CHANGE'",
        source_key,
    ) or 0


async def _type_count(c: asyncpg.Connection, source_key: str, event_type: str) -> int:
    return await c.fetchval(
        "SELECT count(*) FROM vehicle_event ve "
        "JOIN entity_source es ON es.entity_ulid = ve.entity_ulid "
        "WHERE es.source_key = $1 AND ve.event_type = $2",
        source_key, event_type,
    ) or 0


@SKIP_DB
@pytest.mark.integration
class TestKmCollectionLive:
    """Live assertions documenting the km under-collection on the served
    timeline. Read-only; nothing written, nothing to roll back."""

    def test_should_carry_km_connectors_do(self) -> None:
        """Every connector that SHOULD carry km (wired to emit_change_deltas)
        has a non-zero KM_CHANGE history. A zero here means a high-volume
        carrier silently stopped emitting km deltas."""
        def check(c):
            async def run():
                failures = []
                for source_key in _SHOULD_CARRY_KM:
                    n = await _km_count(c, source_key)
                    if n <= 0:
                        failures.append(source_key)
                return failures
            return run()
        failures = _query(check)
        assert not failures, (
            f"km-carrier sources with ZERO KM_CHANGE (regression): {failures}"
        )

    def test_autocasion_km_gap_documented(self) -> None:
        """KNOWN GAP (live): autocasion_wholesale has PRICE_CHANGE history but
        ZERO KM_CHANGE and ZERO PHOTO_CHANGE — it never re-diffs km/photo on
        re-seen listings. This asserts the gap as it stands so a future fix
        (km/photo start flowing) is a visible, deliberate change."""
        def check(c):
            async def run():
                price = await _type_count(c, _AUTOCASION_CONNECTOR, "PRICE_CHANGE")
                km = await _type_count(c, _AUTOCASION_CONNECTOR, "KM_CHANGE")
                photo = await _type_count(c, _AUTOCASION_CONNECTOR, "PHOTO_CHANGE")
                return price, km, photo
            return run()
        price, km, photo = _query(check)
        assert price > 0, (
            "autocasion is expected to have PRICE_CHANGE history (its bespoke "
            "capture_price_drop works); 0 here means the source is dormant — "
            "the km-gap assertion below would be vacuous."
        )
        assert km == 0, (
            f"autocasion emitted {km} KM_CHANGE — the km gap appears FIXED. "
            f"Update this test + promote autocasion to a km carrier."
        )
        assert photo == 0, (
            f"autocasion emitted {photo} PHOTO_CHANGE — the photo gap appears "
            f"FIXED. Update this test + promote autocasion."
        )

    def test_km_is_globally_under_collected_vs_price(self) -> None:
        """Document the headline ratio: fleet-wide KM_CHANGE is a small fraction
        of PRICE_CHANGE (~8% live). This is the symptom the autocasion fix +
        future carrier wiring should shrink. Guards against a silent collapse
        of km collection to ~0 while price keeps flowing."""
        def check(c):
            async def run():
                km = await c.fetchval(
                    "SELECT count(*) FROM vehicle_event WHERE event_type='KM_CHANGE'") or 0
                price = await c.fetchval(
                    "SELECT count(*) FROM vehicle_event WHERE event_type='PRICE_CHANGE'") or 0
                return km, price
            return run()
        km, price = _query(check)
        assert price > 0, "no PRICE_CHANGE history — DB not populated as expected"
        ratio = km / price
        # Lower bound: km collection has NOT collapsed to ~zero (some carriers work).
        assert ratio > 0.0, "KM_CHANGE collapsed to zero fleet-wide (carriers broken)"
        # Upper bound: km is STILL under-collected vs price (the documented state).
        # When autocasion + more carriers are wired, this ceiling can be raised.
        assert ratio < _KM_PCT_OF_PRICE_CEILING, (
            f"KM_CHANGE/PRICE_CHANGE = {ratio:.3f} >= {_KM_PCT_OF_PRICE_CEILING}; "
            f"km collection improved past the documented under-collection — raise "
            f"the ceiling and update the km_enrich analysis (this is good news)."
        )
