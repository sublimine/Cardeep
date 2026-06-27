"""
tests/test_cdp_check_multicountry.py

GOLDEN -- the SCHEMA-LAYER cdp_code CHECK country-proof (generic-engine, schema vector).

THE BUG THIS LOCKS
------------------
``migrations/0033_evict.sql`` shipped ``capacity_ledger`` and ``audit_eviction``
with a cdp_code CHECK baked to Spain + a 2-DIGIT-NUMERIC province::

    CHECK (cdp_code ~ '^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$')

``pipeline/evict.py`` writes ONE row into EACH of these ledgers inside the single
eviction transaction (see ``test_evict.py::TestEvictApply``). For any country #2
dealer the minted cdp_code is e.g. ``CDP-DE-091-AB23CDEF`` (country 'DE', German
Kreis-width province '091') or ``CDP-FR-2A-CDEFGHJK`` (Corsica's alphanumeric
department '2A'). Both FAIL the ES-baked regex -> the ledger INSERT is rejected ->
the eviction transaction ABORTS for the entire second country.

``migrations/0062_cdp_check_country_generic.sql`` generalises both CHECKs to::

    ^CDP-[A-Z]{2}-[0-9A-Z]{2,8}-[0-9A-HJKMNP-TV-Z]{8}$

mirroring the served-identity validator ``pipeline/complete.py::_CDP_CODE_RE``
(commit 052fa8f: country '^CDP-[A-Z]{2}-', uppercase-alphanumeric province) and the
REAL shape minted by ``services/api/codes.py::mint_code`` over the VARCHAR(8) geo
backbone of migration 0059 (province is geo_province.code: alphanumeric, 2..8 wide;
suffix is 8 Crockford-base32 chars, no I/L/O/U).

WHAT IS ASSERTED
----------------
  accepts country #2 : DE/FR/IT/PT real province grammars INSERT cleanly into BOTH
                       ledgers (RED before 0062 -- rejected; GREEN after).
  ES byte-identical  : a valid ES code still INSERTs (the old surface is a strict
                       subset of the new one -> zero regression; passes in BOTH states).
  not over-widened   : malformed shapes (lowercase country, lowercase province char,
                       a 9-char over-ceiling province, an I/L/O/U in the Crockford
                       suffix, a wrong-width suffix, a missing province segment) STAY
                       rejected by both CHECKs (state-invariant -- pass in both states).

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES
:5433 (live production) by DSN string -- the refuse happens BEFORE any connect, so
:5433 is never even opened. Every INSERT runs inside a transaction that is ROLLED
BACK on teardown, so the dry-run stays byte-identical. capacity_ledger / audit_eviction
carry NO foreign key, so the rows are fully self-contained (no census seed needed).
"""
from __future__ import annotations

import os

import psycopg2
import pytest
from psycopg2 import errors as pg_errors

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

pytestmark = pytest.mark.integration

# The two ledgers carrying the cdp_code CHECK generalised by 0062.
_TABLES = ["capacity_ledger", "audit_eviction"]

# Codes the generalised CHECK MUST accept. The first is ES (also valid under the old
# 0033 regex -> proves the ES surface is byte-identical: it passes pre- AND post-0062).
# The rest are real country #2 administrative grammars, each REJECTED by the old
# ES-baked regex and ACCEPTED only once 0062 is applied (the RED->GREEN flip):
_VALID_CODES = [
    "CDP-ES-28-SYNT0001",        # ES Madrid (control) -- 2-digit numeric province, valid in BOTH states
    "CDP-DE-091-AB23CDEF",       # DE -- German Kreis-width 3-digit province (the red-team code)
    "CDP-FR-2A-CDEFGHJK",        # FR -- Corsica's alphanumeric 2-char department '2A'
    "CDP-IT-RM-23456789",        # IT -- 2-letter province 'RM' (Roma)
    "CDP-PT-PT11A-MNPQRST0",      # PT -- NUTS-style 5-char alphanumeric province 'PT11A'
    "CDP-DE-09175001-ABCDEFGH",  # DE -- 8-char province at the VARCHAR(8) ceiling of 0059
]

# Codes the CHECK MUST keep rejecting (proves 0062 widened the country/province surface
# WITHOUT dropping the shape guard). Each is malformed under BOTH the old and new regex,
# so these are state-invariant: they pass (raise CheckViolation) before AND after 0062.
_MALFORMED_CODES = [
    "CDP-de-28-SYNT0001",         # lowercase country (country class is [A-Z]{2})
    "CDP-ES-2a-SYNT0001",         # lowercase province char (province class is [0-9A-Z])
    "CDP-ES-123456789-SYNT0001",  # province 9 chars -- over the 8-wide VARCHAR(8) ceiling
    "CDP-ES-28-SYNT000I",         # 'I' in the Crockford suffix (I/L/O/U are excluded)
    "CDP-ES-28-SYNT001",          # suffix 7 chars -- the Crockford block is exactly 8
    "CDP-ES-SYNT0001",            # missing the province segment entirely
]


# ---------------------------------------------------------------------------
# Connection + isolation guard (same surface as the other country goldens)
# ---------------------------------------------------------------------------
def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


def _db_reachable(dsn: str) -> bool:
    try:
        psycopg2.connect(dsn, connect_timeout=3).close()
        return True
    except Exception:
        return False


@pytest.fixture
def dry_conn():
    """A transactional connection to the dry-run DB, rolled back on teardown.

    Isolation guard against the live census:
      1. refuse any DSN pointing at :5433 (live production) BEFORE connecting;
      2. skip if the DB is unreachable.
    No empty-census guard is needed: this golden only writes self-contained rows into
    capacity_ledger / audit_eviction (no FK to entity), and rolls them back -- it never
    reads or mutates the census, so it runs safely against an empty OR populated dry-run.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the cdp-check golden against :5433 (live production); "
            "point CARDEEP_DSN at the :5434 dry-run")
    if not _db_reachable(dsn):
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


def _insert_cdp(cur, table: str, cdp: str) -> None:
    """Minimal NOT-NULL-respecting insert into the target ledger (reason has no default
    on audit_eviction; capacity_ledger needs only cdp_code -- the rest default)."""
    if table == "capacity_ledger":
        cur.execute("INSERT INTO capacity_ledger (cdp_code) VALUES (%s)", (cdp,))
    else:
        cur.execute(
            "INSERT INTO audit_eviction (cdp_code, reason) VALUES (%s, %s)",
            (cdp, "golden-0062"),
        )


# ---------------------------------------------------------------------------
# accepts: ES (byte-identical) + every real country #2 province grammar
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("cdp", _VALID_CODES)
@pytest.mark.parametrize("table", _TABLES)
def test_check_accepts_country_and_province_grammars(dry_conn, table: str, cdp: str) -> None:
    """The generalised cdp_code CHECK accepts ES (control) AND a second country's real
    administrative codes. RED before 0062 for every non-ES code (CheckViolation);
    GREEN after. ES is valid in both states (the old regex is a strict subset)."""
    with dry_conn.cursor() as cur:
        _insert_cdp(cur, table, cdp)  # must NOT raise once 0062 is applied
        cur.execute(
            f"SELECT count(*) FROM {table} WHERE cdp_code = %s", (cdp,)  # noqa: S608 (table from fixed allowlist)
        )
        assert cur.fetchone()[0] == 1, f"{cdp} should have inserted into {table}"
    dry_conn.rollback()  # leave the dry-run byte-identical between params


# ---------------------------------------------------------------------------
# rejects: malformed shapes stay rejected (no over-widening) -- state-invariant
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("cdp", _MALFORMED_CODES)
@pytest.mark.parametrize("table", _TABLES)
def test_check_still_rejects_malformed(dry_conn, table: str, cdp: str) -> None:
    """0062 widened the country + province surface WITHOUT dropping the shape guard:
    malformed codes still violate the CHECK on both ledgers, before and after the fix."""
    with dry_conn.cursor() as cur:
        with pytest.raises(pg_errors.CheckViolation):
            _insert_cdp(cur, table, cdp)
    dry_conn.rollback()  # clear the aborted transaction for a clean teardown
