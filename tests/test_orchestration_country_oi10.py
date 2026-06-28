"""OI-10 de-blinding goldens — orchestration tables country-scoped + the :silence ZOMBIE fix.

THE ZOMBIE (live in prod, affects EVERY country). The silence watchdog fires a
``<source>:silence`` alert when a source goes quiet, but NOTHING ever resolves it:
``health.record_run`` on success only closes ``<source>:scrape`` / ``<source>:discover``
origins (``build_origin(source_key, phase)``, phase in {scrape, discover}). So a source that
RECOVERS leaves its ``:silence`` alert open forever — observability rots in every country
(~7 zombies). This file pins the ROOT fix: ``resolve_recovered_silence_alerts()`` closes a
``:silence`` alert the moment its source is no longer silent, run every watchdog cycle.

THE COUNTRY DIMENSION. Migration 0068 (additive mirror of 0052) adds ``country_code CHAR(2)
NOT NULL DEFAULT 'ES'`` to the orchestration tables (source_health / harvest_run /
scheduler_lease), and ``_due_sources`` / ``find_silent_sources`` / the silence resolver scope
``WHERE country_code = ANY(active_countries())``. With the single ES tenant the result set is
BYTE-IDENTICAL to today (every existing row is ES), and a 2nd country's producers become
independently observable.

ISOLATION (inviolable). The DB parts run ONLY against the dry-run (:5434). They honor
``CARDEEP_DSN`` (default :5434), HARD-REFUSE :5433 (live production) by DSN string, use
UNIQUE synthetic source_keys (``__oi10_*``), and either roll back (read-only scope proofs) or
DELETE every synthetic row in a ``finally`` (the commit-bearing zombie proof) — so :5434 is
byte-identical after the run. No real source_health/alert row is read into an assertion.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent

# Dry-run DSN (:5434). NEVER :5433 (live production). psycopg2.connect accepts the URL form.
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"


def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


DSN = _target_dsn()


def _db_available() -> bool:
    try:
        import psycopg2
        conn = psycopg2.connect(DSN, connect_timeout=3)
        conn.close()
        return True
    except Exception:
        return False


DB_AVAILABLE = _db_available()

# Golden isolation guard (mirrors tests/test_country_coexistence.py): refuse :5433 by DSN
# string AND skip when the dry-run is unreachable. Synthetic rows + rollback/cleanup keep
# :5434 byte-identical.
_DB_GATE = pytest.mark.skipif(
    (not DB_AVAILABLE) or ("5433" in DSN),
    reason="dry-run cardeep-pg not reachable, or refusing :5433 (live production); "
           "point CARDEEP_DSN at the :5434 dry-run",
)

# Tables the OI-10 migration adds the country dimension to.
_ORCH_TABLES = ("source_health", "harvest_run", "scheduler_lease")


def _connect():
    import psycopg2
    return psycopg2.connect(DSN)


def _seed_silent_source(cur, source_key: str, *, country_code: str,
                        interval_h: int = 24, hours_since: int = 100) -> None:
    """INSERT a source_health row that is SILENT (last_fail older than 2x interval).

    hours_since (100h) > 2 x interval_h (48h) => the source is silent by the watchdog rule.
    consecutive_fails stays 0 so it is also DUE (breaker closed) for the _due_sources proof.
    """
    cur.execute(
        "INSERT INTO source_health "
        "(source_key, last_fail, harvest_interval_hours, is_tier1, status, country_code) "
        "VALUES (%s, now() - (%s || ' hours')::interval, %s, FALSE, 'down', %s)",
        (source_key, str(hours_since), interval_h, country_code),
    )


# ===========================================================================
# (a) BYTE-IDENTITY — the default country scope is exactly ['ES'] (DB-free)
# ===========================================================================
@pytest.mark.unit
class TestActiveCountriesDefaultIsEs:
    """The orchestration scope defaults to active_countries() == ['ES']; with the single
    tenant every WHERE country_code = ANY(['ES']) is a no-op over the all-ES census, so the
    result set is byte-identical to the pre-OI-10 unscoped query."""

    def test_active_countries_is_es(self):
        from pipeline.ops.registry import active_countries
        assert active_countries() == ["ES"]


# ===========================================================================
# (b) MIGRATION 0068 — country_code on the 3 orchestration tables, head 0068, no own drift
# ===========================================================================
@_DB_GATE
@pytest.mark.integration
class TestMigration0068Applied:
    """source_health / harvest_run / scheduler_lease each carry country_code CHAR(2) NOT NULL
    DEFAULT 'ES' (additive mirror of 0052), 0068 is in the ledger, and 0068's ledger sha256
    matches the file on disk (no OWN drift — pre-existing FILE-MISSING from sibling branches
    such as 0065/0066 is not this migration's concern)."""

    def test_country_code_added_to_orchestration_tables(self):
        conn = _connect()
        try:
            with conn.cursor() as cur:
                for table in _ORCH_TABLES:
                    cur.execute(
                        "SELECT data_type, character_maximum_length, is_nullable, column_default "
                        "FROM information_schema.columns "
                        "WHERE table_name=%s AND column_name='country_code'",
                        (table,),
                    )
                    row = cur.fetchone()
                    assert row is not None, (
                        f"{table}.country_code missing — migration 0068 not applied to this DB")
                    data_type, maxlen, is_nullable, default = row
                    assert data_type == "character", f"{table}.country_code is {data_type}, want CHAR"
                    assert maxlen == 2, f"{table}.country_code width {maxlen}, want 2"
                    assert is_nullable == "NO", f"{table}.country_code must be NOT NULL"
                    assert default is not None and "ES" in default, (
                        f"{table}.country_code default {default!r} must be 'ES'")
        finally:
            conn.close()

    def test_existing_rows_default_to_es(self):
        """Every pre-existing orchestration row is stamped 'ES' by the DEFAULT (zero NULL,
        zero non-ES) — the byte-identity backfill of the additive migration."""
        conn = _connect()
        try:
            with conn.cursor() as cur:
                for table in _ORCH_TABLES:
                    cur.execute(
                        f"SELECT count(*) FROM {table} "
                        f"WHERE country_code IS NULL OR country_code <> 'ES'")
                    non_es = cur.fetchone()[0]
                    assert non_es == 0, (
                        f"{table} has {non_es} row(s) not stamped 'ES' — additive default broke")
        finally:
            conn.close()

    def test_0068_in_ledger_without_own_drift(self):
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT filename, sha256 FROM schema_migrations WHERE version='0068'")
                row = cur.fetchone()
            assert row is not None, "0068 not in schema_migrations — run scripts.migrate up"
            filename, ledger_sha = row
            disk = (_REPO_ROOT / "migrations" / filename)
            assert disk.exists(), f"0068 file {filename} missing on disk"
            cur_sha = hashlib.sha256(disk.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            assert cur_sha == ledger_sha, (
                "0068 OWN drift: ledger sha != disk sha (the migration file changed post-apply)")
        finally:
            conn.close()


# ===========================================================================
# (c) THE ZOMBIE FIX — an open :silence alert RESOLVES when the source returns
# ===========================================================================
@_DB_GATE
@pytest.mark.integration
class TestSilenceZombieResolved:
    """resolve_recovered_silence_alerts() closes a ``:silence`` alert the moment its source is
    no longer silent — the root fix for the alert that record_run could never reach. Commits
    (mirrors fire_silence_alert_sync); every synthetic row is deleted in a finally."""

    def test_recovered_source_silence_alert_is_resolved(self):
        from pipeline.ops.silence_watchdog import (
            find_silent_sources,
            resolve_recovered_silence_alerts,
        )
        src = f"__oi10_zombie_{uuid.uuid4().hex[:8]}"
        origin = f"{src}:silence"
        conn = _connect()
        try:
            with conn.cursor() as cur:
                # 1. Seed a SILENT ES source + an OPEN :silence alert (the watchdog state today).
                _seed_silent_source(cur, src, country_code="ES")
                cur.execute(
                    "INSERT INTO alert (origin, severity, message, payload) "
                    "VALUES (%s, 'critical', 'source silent', '{}'::jsonb) RETURNING id",
                    (origin,),
                )
                alert_id = cur.fetchone()[0]
            conn.commit()

            # sanity: the source IS currently silent and the alert IS open.
            assert src in {r["source_key"] for r in find_silent_sources(conn)}
            with conn.cursor() as cur:
                cur.execute("SELECT resolved_at FROM alert WHERE id=%s", (alert_id,))
                assert cur.fetchone()[0] is None, "alert should start open (the zombie)"

            # 2. The source RUNS AGAIN: record_run stamps last_ok=now() on source_health. (Today a
            #    scrape recovery resolves <src>:scrape only — the :silence alert stays a zombie.)
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE source_health SET last_ok=now(), last_fail=NULL, "
                    "status='healthy', consecutive_fails=0 WHERE source_key=%s", (src,))
            conn.commit()
            assert src not in {r["source_key"] for r in find_silent_sources(conn)}, (
                "source should no longer be silent after it ran again")

            # 3. THE FIX: the watchdog's recovery sweep closes the open :silence alert.
            resolved = resolve_recovered_silence_alerts(conn)
            assert src in resolved, "the recovered source's :silence alert was not resolved"
            with conn.cursor() as cur:
                cur.execute("SELECT resolved_at FROM alert WHERE id=%s", (alert_id,))
                assert cur.fetchone()[0] is not None, (
                    "ZOMBIE: :silence alert still open after the source recovered")
        finally:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM alert WHERE origin=%s", (origin,))
                cur.execute("DELETE FROM source_health WHERE source_key=%s", (src,))
            conn.commit()
            conn.close()

    def test_still_silent_source_alert_stays_open(self):
        """A source that is STILL silent keeps its :silence alert open — the resolver closes
        only RECOVERED sources, never silences a live fault."""
        from pipeline.ops.silence_watchdog import resolve_recovered_silence_alerts
        src = f"__oi10_silent_{uuid.uuid4().hex[:8]}"
        origin = f"{src}:silence"
        conn = _connect()
        try:
            with conn.cursor() as cur:
                _seed_silent_source(cur, src, country_code="ES")  # last_fail 100h ago, still silent
                cur.execute(
                    "INSERT INTO alert (origin, severity, message, payload) "
                    "VALUES (%s, 'warning', 'source silent', '{}'::jsonb) RETURNING id",
                    (origin,),
                )
                alert_id = cur.fetchone()[0]
            conn.commit()

            resolved = resolve_recovered_silence_alerts(conn)
            assert src not in resolved, "a still-silent source must NOT be resolved"
            with conn.cursor() as cur:
                cur.execute("SELECT resolved_at FROM alert WHERE id=%s", (alert_id,))
                assert cur.fetchone()[0] is None, "still-silent alert must remain open"
        finally:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM alert WHERE origin=%s", (origin,))
                cur.execute("DELETE FROM source_health WHERE source_key=%s", (src,))
            conn.commit()
            conn.close()

    def test_resolver_ignores_non_silence_origin(self):
        """The silence resolver targets only ``:silence`` origins; a recovered source's
        ``:scrape`` alert is owned by record_run and must NOT be touched here."""
        from pipeline.ops.silence_watchdog import resolve_recovered_silence_alerts
        src = f"__oi10_scrape_{uuid.uuid4().hex[:8]}"
        scrape_origin = f"{src}:scrape"
        conn = _connect()
        try:
            with conn.cursor() as cur:
                # A RECOVERED source (ran just now) with a stray open :scrape alert.
                cur.execute(
                    "INSERT INTO source_health "
                    "(source_key, last_ok, harvest_interval_hours, is_tier1, status, country_code) "
                    "VALUES (%s, now(), 24, FALSE, 'healthy', 'ES')", (src,))
                cur.execute(
                    "INSERT INTO alert (origin, severity, message, payload) "
                    "VALUES (%s, 'warning', 'scrape fault', '{}'::jsonb) RETURNING id",
                    (scrape_origin,),
                )
                alert_id = cur.fetchone()[0]
            conn.commit()

            resolved = resolve_recovered_silence_alerts(conn)
            assert src not in resolved, "scrape origin must not be reported by the silence resolver"
            with conn.cursor() as cur:
                cur.execute("SELECT resolved_at FROM alert WHERE id=%s", (alert_id,))
                assert cur.fetchone()[0] is None, ":scrape alert must be untouched by silence resolver"
        finally:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM alert WHERE origin=%s", (scrape_origin,))
                cur.execute("DELETE FROM source_health WHERE source_key=%s", (src,))
            conn.commit()
            conn.close()


# ===========================================================================
# (d) COUNTRY SCOPE — ES default is byte-identical; an explicit set widens it (read-only)
# ===========================================================================
@_DB_GATE
@pytest.mark.integration
class TestOrchestrationCountryScope:
    """Seed an ES and a DE silent/due source inside a rolled-back transaction. The default
    (active_countries() == ['ES']) sees ES only — DE is invisible to the ES tenant, so the ES
    result set is byte-identical to today. An explicit ['ES','DE'] sees both (scoping works)."""

    def test_find_silent_sources_default_is_es_only(self):
        from pipeline.ops.silence_watchdog import find_silent_sources
        es_src = f"__oi10_es_{uuid.uuid4().hex[:8]}"
        de_src = f"__oi10_de_{uuid.uuid4().hex[:8]}"
        conn = _connect()
        try:
            conn.autocommit = False
            with conn.cursor() as cur:
                _seed_silent_source(cur, es_src, country_code="ES")
                _seed_silent_source(cur, de_src, country_code="DE")

                default_keys = {r["source_key"] for r in find_silent_sources(conn)}
                assert es_src in default_keys, "ES silent source must be detected by default"
                assert de_src not in default_keys, (
                    "DE silent source leaked into the ES-default scope — not byte-identical")

                both_keys = {r["source_key"] for r in find_silent_sources(conn, countries=["ES", "DE"])}
                assert es_src in both_keys and de_src in both_keys, (
                    "explicit ['ES','DE'] must see both tenants' silent sources")
        finally:
            conn.rollback()
            conn.close()

    def test_due_sources_default_is_es_only(self):
        from pipeline.ops.scheduler import _due_sources
        es_src = f"__oi10_esdue_{uuid.uuid4().hex[:8]}"
        de_src = f"__oi10_dedue_{uuid.uuid4().hex[:8]}"
        conn = _connect()
        try:
            conn.autocommit = False
            with conn.cursor() as cur:
                _seed_silent_source(cur, es_src, country_code="ES")
                _seed_silent_source(cur, de_src, country_code="DE")

                default_keys = {r[0] for r in _due_sources(conn)}
                assert es_src in default_keys, "ES due source must be scheduled by default"
                assert de_src not in default_keys, (
                    "DE due source leaked into the ES-default scheduler scope — not byte-identical")

                both_keys = {r[0] for r in _due_sources(conn, countries=["ES", "DE"])}
                assert es_src in both_keys and de_src in both_keys, (
                    "explicit ['ES','DE'] must schedule both tenants' due sources")
        finally:
            conn.rollback()
            conn.close()
