"""Country-proof (red-team final): gestion_item must not collapse aggregated alerts cross-country.

The BY-KIND aggregated detectors keyed their dedupe_key on the kind alone:
  - staleness storm  -> "staleness|kind:{kind}|{bucket}"     (detect.py)
  - coverage_gap     -> "coverage_gap|{kind}|{bucket}"
gestion_item.UNIQUE(dedupe_key) then collapsed an ES alert and a DE alert of the same kind/bucket
into a SINGLE row in a 2-country census, erasing per-country granularity. (Quarantine / per-subject
items key on cdp_code / vehicle_ulid and were already country-safe.)

Fix: migration 0064 adds gestion_item.country_code (DEFAULT 'ES'); the two aggregated detectors
group by (country, kind), thread the country into the dedupe_key
('staleness|{country}|kind:{kind}|{bucket}', 'coverage_gap|{country}|{kind}|{bucket}') and carry
country_code on the AnomalyResult, which route.open_or_refresh writes. ES is byte-identical (the
single-tenant census is all 'ES', so the country segment is constant).

The mock tests prove the dedupe_keys no longer collide; the DB test (dry-run :5434) proves the
column exists, is written, and two countries persist as TWO rows (no ON CONFLICT collapse).

ISOLATION: the DB part runs ONLY against :5434. Honors CARDEEP_DSN (default :5434), HARD-REFUSES
:5433, and rolls back — zero residue.
"""
from __future__ import annotations

import asyncio
import os

import pytest

from pipeline.gestionador.detect import (
    AnomalyResult,
    COVERAGE_ANCHORS,
    STALENESS_STORM_THRESHOLD,
    _daily_bucket,
    detect_coverage_gap,
    detect_staleness,
)

_DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep")

_GARAJE_TTL_DAYS = 30  # 30d vs the 7d garaje TTL -> ratio ~4.3, well past the WARN floor


def _run(coro):
    return asyncio.run(coro)


def _make_conn(fetch_result):
    from unittest.mock import AsyncMock

    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=fetch_result)
    return conn


# ---------------------------------------------------------------------------
# (b.1) staleness STORM — country comes from the entity rows
# ---------------------------------------------------------------------------

class TestStalenessStormCountry:
    def test_es_and_de_storm_do_not_collapse(self) -> None:
        n = STALENESS_STORM_THRESHOLD + 1  # >threshold per (country, kind) -> a storm each
        rows = [
            {"cdp_code": f"CDP-ES-28-{i:04d}", "kind": "garaje", "last_seen": None,
             "age_seconds": _GARAJE_TTL_DAYS * 86400, "country_code": "ES"}
            for i in range(n)
        ] + [
            {"cdp_code": f"CDP-DE-28-{i:04d}", "kind": "garaje", "last_seen": None,
             "age_seconds": _GARAJE_TTL_DAYS * 86400, "country_code": "DE"}
            for i in range(n)
        ]
        conn = _make_conn(rows)
        results = _run(detect_staleness(conn))

        storms = [r for r in results if r.subject_type == "source"]
        assert len(storms) == 2, (
            f"ES and DE garaje storms must be TWO source-level items, not collapsed; got {len(storms)}"
        )
        by_country = {r.country_code: r for r in storms}
        assert set(by_country) == {"ES", "DE"}, f"storm country_codes: {set(by_country)!r}"

        bucket = _daily_bucket()
        assert by_country["ES"].dedupe_key == f"staleness|ES|kind:garaje|{bucket}"
        assert by_country["DE"].dedupe_key == f"staleness|DE|kind:garaje|{bucket}"
        assert by_country["ES"].dedupe_key != by_country["DE"].dedupe_key, "CROSS-COUNTRY DEDUPE COLLISION"

    def test_es_only_storm_is_byte_identical(self) -> None:
        """ES-only census: a single storm, country segment constant -> 'staleness|ES|kind:...'."""
        n = STALENESS_STORM_THRESHOLD + 1
        rows = [
            {"cdp_code": f"CDP-ES-08-{i:04d}", "kind": "garaje", "last_seen": None,
             "age_seconds": _GARAJE_TTL_DAYS * 86400, "country_code": "ES"}
            for i in range(n)
        ]
        results = _run(detect_staleness(_make_conn(rows)))
        storms = [r for r in results if r.subject_type == "source"]
        assert len(storms) == 1
        assert storms[0].country_code == "ES"
        assert storms[0].measured["stale_count"] == n
        assert storms[0].dedupe_key == f"staleness|ES|kind:garaje|{_daily_bucket()}"


# ---------------------------------------------------------------------------
# (b.2) coverage_gap — country comes from the (country, kind) anchor + covered slice
# ---------------------------------------------------------------------------

class TestCoverageGapCountry:
    def test_es_and_de_gap_do_not_collapse(self) -> None:
        from unittest.mock import patch

        # DE anchor for the same kind, so DE coverage is evaluated against its OWN floor.
        de_anchors = dict(COVERAGE_ANCHORS)
        de_anchors[("DE", "garaje")] = 29_955
        covered_rows = [
            {"country_code": "ES", "kind": "garaje", "covered": 100},  # far below ES floor
            {"country_code": "DE", "kind": "garaje", "covered": 100},  # far below DE floor
        ]
        with patch("pipeline.gestionador.detect.COVERAGE_ANCHORS", de_anchors):
            results = _run(detect_coverage_gap(_make_conn(covered_rows)))

        garaje = [r for r in results if r.subject_key == "garaje"]
        by_country = {r.country_code: r for r in garaje}
        assert set(by_country) == {"ES", "DE"}, (
            f"ES and DE garaje gaps must be TWO items, not collapsed; countries={set(by_country)!r}"
        )
        bucket = _daily_bucket()
        assert by_country["ES"].dedupe_key == f"coverage_gap|ES|garaje|{bucket}"
        assert by_country["DE"].dedupe_key == f"coverage_gap|DE|garaje|{bucket}"
        assert by_country["ES"].dedupe_key != by_country["DE"].dedupe_key, "CROSS-COUNTRY DEDUPE COLLISION"

    def test_es_only_gap_is_byte_identical(self) -> None:
        """ES-only census fires the same critical garaje gap, now keyed 'coverage_gap|ES|garaje|...'."""
        covered_rows = [{"country_code": "ES", "kind": "garaje", "covered": 100}]
        results = _run(detect_coverage_gap(_make_conn(covered_rows)))
        garaje = [r for r in results if r.subject_key == "garaje"]
        assert len(garaje) == 1
        assert garaje[0].country_code == "ES"
        assert garaje[0].severity == "critical"          # covered 100 < 29955 anchor breach
        assert garaje[0].quarantines is False
        assert garaje[0].dedupe_key == f"coverage_gap|ES|garaje|{_daily_bucket()}"


# ---------------------------------------------------------------------------
# (b.3) DB round-trip (dry-run :5434): column exists, is written, no cross-country collapse
# ---------------------------------------------------------------------------

class _Rollback(Exception):
    pass


@pytest.mark.skipif("5433" in _DSN, reason="needs the :5434 dry-run; refuses live :5433")
class TestGestionItemCountryColumnDB:
    def test_two_countries_persist_as_two_rows_with_country_code(self) -> None:
        _run(self._body())

    async def _body(self) -> None:
        import asyncpg

        from pipeline.gestionador.route import open_or_refresh

        bucket = _daily_bucket()
        conn = await asyncpg.connect(_DSN)
        try:
            async with conn.transaction():
                made = {}
                for country in ("ES", "DE"):
                    anomaly = AnomalyResult(
                        detector="staleness",
                        subject_type="source",
                        subject_key="kind:__gi_country_dbtest__",
                        severity="critical",
                        score=1.0,
                        measured={"k": 1, "country": country},
                        baseline=None,
                        lane="ESCALATE_GASTO",
                        quarantines=False,
                        dedupe_key=f"staleness|{country}|kind:__gi_country_dbtest__|{bucket}",
                        country_code=country,
                    )
                    made[country] = await open_or_refresh(conn, anomaly, actor="dbtest")

                # Two distinct rows (the country-threaded dedupe_keys did NOT collapse).
                assert made["ES"] != made["DE"], (
                    "CROSS-COUNTRY COLLAPSE: ES and DE aggregated items shared a gestion_item row"
                )
                rows = await conn.fetch(
                    "SELECT id, country_code FROM gestion_item WHERE id = ANY($1::bigint[])",
                    [made["ES"], made["DE"]],
                )
                got = {r["id"]: r["country_code"] for r in rows}
                assert got[made["ES"]] == "ES", f"ES item country_code = {got.get(made['ES'])!r}"
                assert got[made["DE"]] == "DE", f"DE item country_code = {got.get(made['DE'])!r}"
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()
