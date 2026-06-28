"""Tests for pipeline/autopilot/supervisor.py — the SUPERVISA per-country health roll-up (Phase E3).

Two layers, mirroring the autopilot suite (tests/test_autopilot_state.py):

  * PURE (no DB): the :class:`CountryHealth` value object — its derived posture
    (``contaminated`` flips on ``violations > 0``; ``gestion_total`` sums the per-state
    histogram) and the frozen-ness of the roll-up dataclasses. These are
    ``@pytest.mark.unit`` predicates and need no database.

  * INTEGRATION (:5434 dry-run only): a synthetic ``XX`` tenant AND a synthetic ``ES``
    incumbent are seeded side by side (sharing the deliberate dup province code '28', the
    0053 coexistence), then ``health_rollup(conn, 'XX')`` is asserted to return XX's OWN
    health — servable dealers, proof violations, exhaustiveness seal, gestion-by-state and
    source health — completely ISOLATED from ES, and vice-versa. ``violations`` is 0 (no
    cross-country merge). The whole seed runs inside an asyncpg transaction that is ROLLED
    BACK, so the dry-run census is left byte-identical (entity stays 0 — proven after the
    rollback). Hard-pinned to :5434; refuses :5433 (live prod).

ISOLATION (inviolable): the integration layer NEVER touches :5433. It refuses any DSN that
mentions :5433 and skips when the dry-run DB is unreachable. Every write lands on the
caller-owned transaction and is rolled back — zero residue.
"""
from __future__ import annotations

import asyncio
import os

import pytest

from pipeline.autopilot.supervisor import (
    CountryHealth,
    SealHealth,
    SourceHealthRollup,
    health_rollup,
)

# ---------------------------------------------------------------------------
# Dry-run plumbing (mirrors tests/test_autopilot_state.py exactly)
# ---------------------------------------------------------------------------
_DRYRUN_DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5434/cardeep"
_SYNTH_CC = "XX"        # the architecture's synthetic onboarding country; never a real tenant
_INCUMBENT_CC = "ES"    # the synthetic incumbent (seeded here on :5434, NOT live :5433 production)

# Crockford base32 (no I, L, O, U) — the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


class _Rollback(Exception):
    """Sentinel: forces the asyncpg transaction to abort cleanly at test end."""


async def _ping(dsn: str) -> bool:
    try:
        import asyncpg

        conn = await asyncpg.connect(dsn, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


def _db_available() -> bool:
    dsn = _target_dsn()
    if "5433" in dsn:
        return False  # never probe live prod
    try:
        return asyncio.run(_ping(dsn))
    except Exception:
        return False


DB_AVAILABLE = _db_available()


def _ulid(tag: str) -> str:
    safe = "".join(c for c in tag.upper() if c in _CROCKFORD)
    return (safe + "0" * 26)[:26]


# ===========================================================================
# PURE unit layer — the CountryHealth value object (no DB, no network)
# ===========================================================================
class TestCountryHealthValueObject:
    """The roll-up's derived posture and immutability — pure, no database."""

    pytestmark = pytest.mark.unit

    @staticmethod
    def _health(*, violations: int, gestion: dict[str, int]) -> CountryHealth:
        return CountryHealth(
            country_code="XX",
            violations=violations,
            servable_dealers=7,
            seal=SealHealth(rows=2, sealed_segments=2, national_sealed=True,
                            national_coverage_lower=0.97),
            gestion_by_state=gestion,
            sources=SourceHealthRollup(total=3, healthy=2, silent=1),
        )

    def test_contaminated_is_false_when_no_violation(self) -> None:
        assert self._health(violations=0, gestion={}).contaminated is False

    def test_contaminated_is_true_when_violation_present(self) -> None:
        # A cross-country merge involving this tenant MUST flip the posture.
        assert self._health(violations=2, gestion={}).contaminated is True

    def test_gestion_total_sums_the_state_histogram(self) -> None:
        h = self._health(violations=0, gestion={"OPEN": 3, "RESOLVED": 1, "QUARANTINED": 2})
        assert h.gestion_total == 6

    def test_gestion_total_is_zero_for_empty_ledger(self) -> None:
        assert self._health(violations=0, gestion={}).gestion_total == 0

    def test_rollup_dataclasses_are_frozen(self) -> None:
        h = self._health(violations=0, gestion={"OPEN": 1})
        for obj, attr, val in (
            (h, "violations", 9), (h.seal, "rows", 9), (h.sources, "total", 9),
        ):
            with pytest.raises(Exception):
                setattr(obj, attr, val)  # frozen dataclass → FrozenInstanceError


# ===========================================================================
# INTEGRATION layer — per-country roll-up on the :5434 dry-run DB (rolled back)
# ===========================================================================
# Seeding helpers (FK + CHECK respecting), async on the caller-owned transaction.
# ---------------------------------------------------------------------------
async def _seed_geo(conn, cc: str, province: str = "28", muni: str = "28079") -> None:
    """Province + municipality for one tenant. The composite geo key is (country_code, code)
    since 0053, so ES and XX can share the numeric code '28' (the deliberate coexistence)."""
    await conn.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ($1, $2, '13', $3, $4) ON CONFLICT DO NOTHING",
        province, f"prov-{cc}-{province}", f"ccaa-{cc}", cc,
    )
    await conn.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
        "VALUES ($1, $2, $3, NULL, $4) ON CONFLICT DO NOTHING",
        muni, f"muni-{cc}-{muni}", province, cc,
    )


async def _seed_dealer(conn, *, cc: str, cdp: str, province: str = "28", muni: str = "28079") -> None:
    """One in-scope, servable sales point: kind='compraventa', status='active'
    (v_servable_dealer includes compraventa regardless of inventory — mirrors the
    test_country_isolation_serving golden)."""
    await conn.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES ($1, $2, 'compraventa', $3, $3, $4, $5, $6, 'active')",
        _ulid(cdp.replace("-", "")), cdp, f"dealer {cc}", province, muni, cc,
    )


async def _seed_source(conn, *, cc: str, source_key: str, status: str,
                       last_event_sql: str, interval_h: int, is_fail: bool = False) -> None:
    """One source_health row scoped to a tenant (mig 0068). ``last_event_sql`` is an
    inline SQL timestamp expression (e.g. ``now() - interval '1000 hours'``) controlling the
    silence predicate; written to last_fail when ``is_fail`` else last_ok."""
    col = "last_fail" if is_fail else "last_ok"
    await conn.execute(
        f"INSERT INTO source_health "
        f"(source_key, {col}, status, harvest_interval_hours, country_code) "
        f"VALUES ($1, {last_event_sql}, $2, $3, $4)",
        source_key, status, interval_h, cc,
    )


async def _seed_gestion(conn, *, cc: str, dedupe_key: str, state: str, lane: str,
                        quarantines: bool, closed: bool) -> None:
    """One gestion_item ticket scoped to a tenant (mig 0064). dedupe_key is UNIQUE."""
    await conn.execute(
        "INSERT INTO gestion_item "
        "(detector, subject_type, subject_key, severity, measured, lane, state, "
        " quarantines, closed_at, dedupe_key, country_code) "
        "VALUES ('staleness', 'source', $1, 'warning', '{}'::jsonb, $2, $3, $4, "
        f"       {'now()' if closed else 'NULL'}, $5, $6)",
        f"kind:{dedupe_key}", lane, state, quarantines, dedupe_key, cc,
    )


async def _seed_exhaustiveness(conn, *, cc: str, build: str, created_at_sql: str,
                               sealed: bool, coverage_lower: float) -> None:
    """A two-row exhaustiveness certificate for one tenant: the grand-national headline
    (province AND segment NULL) + one per-province stratum (mig 0060 country_code)."""
    cov_pt = round(coverage_lower + 0.06, 2)
    for province, segment in ((None, None), ("28", "compraventa")):
        await conn.execute(
            "INSERT INTO exhaustiveness_estimate "
            "(build_run_id, province_code, segment, k_lists, n_obs, n_hat, ci_low, ci_high, "
            " coverage_point, coverage_lower, method, confidence, seal_threshold, sealed, "
            f" country_code, created_at) "
            f"VALUES ($1, $2, $3, 4, 100, 120, 110, 130, $4, $5, 'stratified_sum', 'high', "
            f"        0.95, $6, $7, {created_at_sql})",
            build, province, segment, cov_pt, coverage_lower, sealed, cc,
        )


async def _seed_xx(conn) -> None:
    """XX tenant: 2 servable dealers, 1 healthy + 1 silent source, OPEN + IN_PROGRESS gestion,
    a SEALED national certificate (coverage_lower 0.97)."""
    await _seed_geo(conn, _SYNTH_CC)
    await _seed_dealer(conn, cc=_SYNTH_CC, cdp="CDP-XX-28-XXAAA001")
    await _seed_dealer(conn, cc=_SYNTH_CC, cdp="CDP-XX-28-XXAAA002")
    # one healthy (fresh) source; one SILENT (last event 1000h ago vs 24h cadence → > 2x).
    await _seed_source(conn, cc=_SYNTH_CC, source_key="xx_fresh", status="healthy",
                       last_event_sql="now()", interval_h=168)
    await _seed_source(conn, cc=_SYNTH_CC, source_key="xx_silent", status="down",
                       last_event_sql="now() - interval '1000 hours'", interval_h=24,
                       is_fail=True)
    await _seed_gestion(conn, cc=_SYNTH_CC, dedupe_key="xx_open", state="OPEN",
                        lane="RESEARCH", quarantines=False, closed=False)
    await _seed_gestion(conn, cc=_SYNTH_CC, dedupe_key="xx_in_progress", state="IN_PROGRESS",
                        lane="RESEARCH", quarantines=False, closed=False)
    await _seed_exhaustiveness(conn, cc=_SYNTH_CC, build="BUILD-XX", created_at_sql="now()",
                               sealed=True, coverage_lower=0.97)


async def _seed_es(conn) -> None:
    """ES incumbent: 3 servable dealers, 2 healthy + 0 silent sources, 1 QUARANTINED gestion,
    an UNSEALED national certificate (coverage_lower 0.50) — every figure distinct from XX."""
    await _seed_geo(conn, _INCUMBENT_CC)
    for n in (1, 2, 3):
        await _seed_dealer(conn, cc=_INCUMBENT_CC, cdp=f"CDP-ES-28-ESAAA00{n}")
    await _seed_source(conn, cc=_INCUMBENT_CC, source_key="es_fresh1", status="healthy",
                       last_event_sql="now()", interval_h=168)
    await _seed_source(conn, cc=_INCUMBENT_CC, source_key="es_fresh2", status="healthy",
                       last_event_sql="now() - interval '10 hours'", interval_h=168)
    await _seed_gestion(conn, cc=_INCUMBENT_CC, dedupe_key="es_quar", state="QUARANTINED",
                        lane="QUARANTINE", quarantines=True, closed=False)
    await _seed_exhaustiveness(conn, cc=_INCUMBENT_CC, build="BUILD-ES", created_at_sql="now()",
                               sealed=False, coverage_lower=0.50)


@pytest.mark.integration
@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="dry-run cardeep-pg not reachable at :5434 (or CARDEEP_DSN points at :5433)",
)
class TestHealthRollupOnDryRun:
    """The per-country roll-up, proven isolated XX↔ES, all inside an aborted txn."""

    def test_refuses_live_prod_dsn(self) -> None:
        assert "5433" not in _target_dsn(), "integration DSN must be the :5434 dry-run"

    def test_per_country_rollup_isolated_and_clean_after_rollback(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        import asyncpg

        dsn = _target_dsn()
        assert "5433" not in dsn  # belt-and-braces inside the coroutine
        conn = await asyncpg.connect(dsn)
        try:
            try:
                async with conn.transaction():
                    # Pre-condition guard: the dry-run census must be EMPTY before we seed
                    # (production holds ~452k; this proves we are not pointed at :5433).
                    assert await conn.fetchval("SELECT count(*) FROM entity") == 0, (
                        "target DB is not the empty dry-run — refusing to seed")

                    # BASELINE captured BEFORE any seed. XX must be pristine (the synthetic
                    # onboarding tenant has zero pre-existing rows); ES is the incumbent and may
                    # carry a dry-run baseline (e.g. source_health rows default-stamped 'ES' by
                    # mig 0068), so ES is asserted by DELTA against this baseline — honest about
                    # the real :5434 state instead of assuming an empty incumbent.
                    xx_base = await health_rollup(conn, _SYNTH_CC)
                    es_base = await health_rollup(conn, _INCUMBENT_CC)
                    assert (xx_base.servable_dealers == 0 and xx_base.seal.rows == 0
                            and xx_base.gestion_by_state == {} and xx_base.sources.total == 0), (
                        f"XX is not pristine in the dry-run — cannot prove exact isolation: {xx_base}")

                    await _seed_xx(conn)
                    await _seed_es(conn)

                    xx = await health_rollup(conn, _SYNTH_CC)
                    es = await health_rollup(conn, _INCUMBENT_CC)

                    # ---- XX roll-up: EXACT (XX was pristine ⇒ its roll-up IS its seed) -----
                    # If ANY ES figure (baseline or freshly-seeded) leaked, these exact equalities break.
                    assert xx.country_code == "XX"
                    assert xx.violations == 0, (
                        f"XX must be clean (no cross-country merge); got {xx.violations}")
                    assert xx.contaminated is False
                    assert xx.servable_dealers == 2, (
                        f"XX servable dealers must be 2 (its own), got {xx.servable_dealers} "
                        "— ES's 3 dealers leaked into XX's roll-up")
                    assert xx.seal.rows == 2 and xx.seal.sealed_segments == 2
                    assert xx.seal.national_sealed is True
                    assert xx.seal.national_coverage_lower == pytest.approx(0.97)
                    assert xx.gestion_by_state == {"OPEN": 1, "IN_PROGRESS": 1}, (
                        f"XX gestion-by-state leaked: {xx.gestion_by_state}")
                    assert (xx.sources.total, xx.sources.healthy, xx.sources.silent) == (2, 1, 1)

                    # ---- ES roll-up: DELTA == exactly the ES seed (baseline untouched by XX) ----
                    assert es.country_code == "ES"
                    assert es.violations == 0
                    assert es.servable_dealers - es_base.servable_dealers == 3, (
                        f"ES served census delta must be +3 (its own seed); base "
                        f"{es_base.servable_dealers} -> {es.servable_dealers}")
                    assert es.seal.rows - es_base.seal.rows == 2
                    assert es.seal.national_sealed is False
                    assert es.seal.national_coverage_lower == pytest.approx(0.50)
                    assert es.gestion_by_state.get("QUARANTINED", 0) \
                        - es_base.gestion_by_state.get("QUARANTINED", 0) == 1
                    assert es.sources.total - es_base.sources.total == 2
                    assert es.sources.healthy - es_base.sources.healthy == 2
                    assert es.sources.silent - es_base.sources.silent == 0, (
                        "ES silent delta must be 0 — XX's silent source leaked into ES")

                    # ---- Cross-isolation: XX's seed never moved the ES baseline, and vice-versa ----
                    assert xx.servable_dealers != es.servable_dealers
                    assert es_base.servable_dealers == 0, "XX seed leaked dealers into the ES baseline"
                    assert "OPEN" not in es.gestion_by_state and "IN_PROGRESS" not in es.gestion_by_state, (
                        "XX gestion states surfaced under ES — country scope leaked")
                    assert "QUARANTINED" not in xx.gestion_by_state, (
                        "ES gestion state surfaced under XX — country scope leaked")

                    raise _Rollback()
            except _Rollback:
                pass

            # ---- After rollback: :5434 is byte-identical (zero residue) ------------
            assert await conn.fetchval("SELECT count(*) FROM entity") == 0, (
                "ROLLBACK LEAK: the synthetic seed survived — dry-run is not clean")
        finally:
            await conn.close()
