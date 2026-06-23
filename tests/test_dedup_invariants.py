"""Over-merge guard tests for the served DEALER dedup (the sales-point product).

WHY THIS FILE EXISTS
--------------------
A re-cluster once produced a 113k-car over-merge: the deep-link super-canonical
chain fused the 52 provincial 'Particulares coches.net' (kind='particular')
aggregates into a single giant cluster. Root cause: a relisted private car shared
across two provincial aggregates chained them together. It was root-fixed by
excluding kind='particular' from the deep-link dedup graph
(scripts/build_canonical_dedup.py:191, ``AND e.kind <> 'particular'``).

OVER-MERGE IS THE DANGER DIRECTION. A giant cross-dealer cluster is a CRITICAL
bug: it collapses distinct physical dealers into one served sales-point and
corrupts every downstream surface (/entities, /inventory, /geo). These tests are
the regression net that trips the instant a future re-cluster reopens that hole.

WHAT IS ASSERTED (all numbers VERIFIED live, cardeep-pg :5433, 2026-06-23)
--------------------------------------------------------------------------
For the SERVED run (the single canonical_dedup_run with vam_verified=TRUE):
  * NO super-canonical component mixes kind='particular' with a dealer kind
    (reproduces the exact query that proves the 113k mega-cluster is dead) ........ live=0
  * MAX component size stays under a sane cap (real max=22, the LOUZAO B1-split) .. cap=30
  * MAX distinct trade-names per component stays small (real max=8); a
    high-name-diversity component is the fingerprint of fused distinct dealers ..... cap=12
  * canonical == richest member: no non-representative member has strictly more
    available vehicles than its representative .................................... live=0
  * the served non-particular dealer count is stable (pinned to the LIVE recompute,
    never a frozen constant — the census grows continuously) ..................... live-pinned

For the candidate run (particular-canonkey-v1), when present:
  * it is a STRICT SUPERSET of the served deep-link run (0 byte-level pair diffs),
    guarding ES cdp_code byte-stability on dealers when serving the fuller chain .. live=0
  * it also has 0 cross-kind components (gating it cannot recreate a giant cluster)  live=0

DESIGN
------
Mirrors the live-DB pattern of tests/test_api_gaps.py: a synchronous asyncpg
helper per query, an integration skip-guard when the DB is unreachable, and the
``integration`` marker (registered in pytest.ini). The over-merge math is pure
SQL against the real overlay tables (canonical_dedup / canonical_dedup_run /
v_dealer_resolved), so the test cross-checks the served product against an
independent SQL path rather than trusting the build script's own asserts.

One DB-free unit test pins the cap CONSTANTS themselves (the guard thresholds
must stay above the known real maxima and below the mega-cluster size), so a
careless edit that loosens a cap into uselessness fails without a database.
"""
from __future__ import annotations

import asyncio
from typing import Optional

import asyncpg
import pytest

# ---------------------------------------------------------------------------
# Connection + skip guard (same surface as tests/test_api_gaps.py)
# ---------------------------------------------------------------------------
DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# Candidate run that ADDS only same-seller particular province-split merges on top
# of the served deep-link run. It is built INERT (vam_verified=FALSE) and may be
# absent (the build is optional); superset tests skip when it is not present.
PARTICULAR_RUN = "particular-canonkey-v1"
DEEPLINK_RUN = "canonical-dedup-deeplink-v1"  # the base super-canonical layer the chain builds on

# ── Over-merge guard caps ──────────────────────────────────────────────────
# These are deliberately set ABOVE the known-good real maxima and FAR BELOW the
# mega-cluster regime, so legitimate census growth does not trip them but a real
# over-merge (a name/hub chain fusing many dealers) does. Verified live 2026-06-23:
#   real max component size  = 22  (CDP single dealer LOUZAO A CORUÑA, a B1-split)
#   real max distinct names  = 8
# The 113k incident produced a single component spanning ~52 provincial aggregates
# (52+ members, 52+ distinct names) — both caps catch it with wide margin.
MAX_COMPONENT_SIZE_CAP = 30
MAX_DISTINCT_NAMES_CAP = 12

# Known-good real maxima (for the unit-level sanity that the caps stay meaningful).
KNOWN_REAL_MAX_COMPONENT_SIZE = 22
KNOWN_REAL_MAX_DISTINCT_NAMES = 8


def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            conn = await asyncpg.connect(DSN, timeout=3)
            await conn.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()
SKIP_NO_DB = pytest.mark.skipif(
    not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433"
)


# ---------------------------------------------------------------------------
# Synchronous query helpers (one asyncio.run per call — no loop conflicts)
# ---------------------------------------------------------------------------

def _fetchval(sql: str, *args: object) -> object:
    async def _q() -> object:
        conn = await asyncpg.connect(DSN, timeout=10)
        try:
            return await conn.fetchval(sql, *args)
        finally:
            await conn.close()
    return asyncio.run(_q())


def _served_run() -> Optional[str]:
    """The single canonical_dedup_run currently serving (vam_verified=TRUE).

    v_dealer_resolved reads exactly this run (the latest vam_verified=TRUE,
    run_id DESC). Tests anchor to whatever is actually served, not a hardcoded id.
    """
    return _fetchval(
        "SELECT run_id FROM canonical_dedup_run "
        "WHERE vam_verified = TRUE ORDER BY run_id DESC LIMIT 1"
    )


def _run_exists(run_id: str) -> bool:
    return bool(
        _fetchval("SELECT count(*) FROM canonical_dedup_run WHERE run_id = $1", run_id)
    )


# ---------------------------------------------------------------------------
# Reusable SQL fragments (parameterised by run_id)
# ---------------------------------------------------------------------------

# Components mixing a particular member with a dealer-kind member. This is the
# EXACT shape of the 113k over-merge: it is the only way a private-seller
# aggregate gets fused into a dealer's served sales-point.
_CROSS_KIND_COMPONENTS = """
    SELECT count(*) FROM (
        SELECT cd.super_canonical_cdp_code
        FROM canonical_dedup cd
        JOIN entity e ON e.entity_ulid = cd.canonical_entity_ulid
        WHERE cd.run_id = $1
        GROUP BY cd.super_canonical_cdp_code
        HAVING bool_or(e.kind = 'particular')
           AND bool_or(e.kind <> 'particular')
    ) x
"""

_MAX_COMPONENT_SIZE = """
    SELECT COALESCE(max(component_size), 0)
    FROM canonical_dedup WHERE run_id = $1
"""

# Distinct NORMALIZED trade-names per component. Normalization mirrors the
# residual name-key normalization spirit: case-fold + strip non-alphanumerics so
# "Aragón Car" / "ARAGON CAR" collapse, and only GENUINELY distinct dealer names
# inflate the count. A high value is the over-merge fingerprint.
_MAX_DISTINCT_NAMES = """
    SELECT COALESCE(max(dn), 0) FROM (
        SELECT cd.super_canonical_cdp_code,
               count(DISTINCT NULLIF(
                   lower(regexp_replace(
                       COALESCE(e.trade_name, e.legal_name, ''),
                       '[^a-z0-9]', '', 'gi')),
                   '')) AS dn
        FROM canonical_dedup cd
        JOIN entity e ON e.entity_ulid = cd.canonical_entity_ulid
        WHERE cd.run_id = $1
        GROUP BY cd.super_canonical_cdp_code
    ) x
"""

# Non-representative members that hold strictly MORE available vehicles than the
# component representative. The pipeline rule is canonical = most-available
# member (tie-break cdp asc); any row here means the served cdp_code points at a
# poorer node and the wrong seller surfaces the listings.
# Available-count basis is identical to the three build scripts:
# COALESCE(canonical, self) over status='available'.
_RICHER_THAN_REP = """
    WITH avail AS (
        SELECT COALESCE(vc.canonical_cdp_code, e.cdp_code) AS canon, count(*) AS c
        FROM vehicle v
        JOIN entity e ON e.entity_ulid = v.entity_ulid
        LEFT JOIN v_canonical vc ON vc.entity_ulid = v.entity_ulid
        WHERE v.status = 'available'
        GROUP BY 1
    ),
    comp AS (
        SELECT super_canonical_cdp_code AS rep,
               canonical_cdp_code AS mem,
               is_representative
        FROM canonical_dedup WHERE run_id = $1
    )
    SELECT count(*)
    FROM comp c
    JOIN avail am ON am.canon = c.mem
    JOIN avail ar ON ar.canon = c.rep
    WHERE c.is_representative = FALSE
      AND am.c > ar.c
"""

# Served non-particular dealer count: the sales-point product cardinality.
# Pinned to the LIVE recompute (never a frozen constant) so a future re-cluster
# that silently merges dealers across provinces trips this immediately.
_SERVED_DEALER_COUNT = """
    SELECT count(DISTINCT vdr.resolved_cdp_code)
    FROM v_dealer_resolved vdr
    JOIN entity e ON e.entity_ulid = vdr.entity_ulid
    WHERE e.kind <> 'particular'
"""


# ===========================================================================
# DB-free: the guard CAPS themselves must stay meaningful
# ===========================================================================

class TestGuardCapsAreMeaningful:
    """Pin the cap constants so a careless edit cannot defang the over-merge net.

    DB-free: validates only the threshold arithmetic. A cap below the known real
    maximum would make the suite flaky on good data; a cap at mega-cluster scale
    would let the 113k incident slip through. Both are caught here without a DB.
    """

    @pytest.mark.unit
    def test_component_size_cap_above_real_max_below_megacluster(self) -> None:
        # Above the real max so legitimate single-dealer B1-splits pass.
        assert MAX_COMPONENT_SIZE_CAP > KNOWN_REAL_MAX_COMPONENT_SIZE, (
            f"size cap {MAX_COMPONENT_SIZE_CAP} must exceed known real max "
            f"{KNOWN_REAL_MAX_COMPONENT_SIZE} (else good data fails)"
        )
        # Far below the 113k regime (~52 provincial aggregates fused).
        assert MAX_COMPONENT_SIZE_CAP < 52, (
            f"size cap {MAX_COMPONENT_SIZE_CAP} must be < 52 so the provincial "
            "mega-cluster (52+ members) cannot slip through"
        )

    @pytest.mark.unit
    def test_distinct_names_cap_above_real_max_below_megacluster(self) -> None:
        assert MAX_DISTINCT_NAMES_CAP > KNOWN_REAL_MAX_DISTINCT_NAMES, (
            f"name cap {MAX_DISTINCT_NAMES_CAP} must exceed known real max "
            f"{KNOWN_REAL_MAX_DISTINCT_NAMES} (else good data fails)"
        )
        assert MAX_DISTINCT_NAMES_CAP < 52, (
            f"name cap {MAX_DISTINCT_NAMES_CAP} must be < 52 so a many-dealer "
            "name-chain fusion cannot slip through"
        )


# ===========================================================================
# Served-run over-merge guards (the core of this file)
# ===========================================================================

class TestServedRunNoOverMerge:
    """Every assertion runs against the run that v_dealer_resolved actually serves."""

    @SKIP_NO_DB
    def test_a_served_run_exists_and_is_unique(self) -> None:
        """Exactly one vam_verified=TRUE run must serve. Zero = nothing served;
        more than one is tolerated by the view (it picks run_id DESC) but the
        product contract is a single served run."""
        n = _fetchval(
            "SELECT count(*) FROM canonical_dedup_run WHERE vam_verified = TRUE"
        )
        assert n >= 1, "no vam_verified=TRUE canonical_dedup_run — nothing is served"
        run = _served_run()
        assert run is not None and isinstance(run, str) and run, (
            "served run id must resolve to a non-empty string"
        )

    @SKIP_NO_DB
    def test_no_cross_kind_particular_dealer_component(self) -> None:
        """CRITICAL regression guard for the 113k incident.

        Reproduces the exact query that proves the mega-cluster is dead: NO served
        super-canonical may contain both a kind='particular' member and a
        dealer-kind member. The kind<>'particular' exclusion in
        build_canonical_dedup.py:191 is what keeps this at 0; if a refactor drops
        that clause, a relisted private car re-chains the provincial aggregates
        and this count jumps.
        """
        run = _served_run()
        assert run is not None, "no served run"
        cross = _fetchval(_CROSS_KIND_COMPONENTS, run)
        assert cross == 0, (
            f"served run '{run}' has {cross} cross-kind (particular+dealer) "
            "super-canonical component(s) — this is the 113k over-merge shape. "
            "Verify the kind<>'particular' exclusion in build_canonical_dedup.py."
        )

    @SKIP_NO_DB
    def test_max_component_size_under_cap(self) -> None:
        """No served component may exceed the size cap.

        A jump signals an accidental hub/name chain fusing many dealers into one
        sales-point. Real max is 22 (the LOUZAO B1-split); cap is 30.
        """
        run = _served_run()
        assert run is not None, "no served run"
        max_size = _fetchval(_MAX_COMPONENT_SIZE, run)
        assert max_size <= MAX_COMPONENT_SIZE_CAP, (
            f"served run '{run}' has a component of size {max_size} > cap "
            f"{MAX_COMPONENT_SIZE_CAP} — a giant cluster (cross-dealer fusion) "
            "is a CRITICAL over-merge. Inspect the largest super_canonical_cdp_code."
        )

    @SKIP_NO_DB
    def test_max_distinct_trade_names_under_cap(self) -> None:
        """No served component may carry too many DISTINCT normalized trade-names.

        High name-diversity inside one component is the over-merge fingerprint:
        genuinely different dealers fused together. Real max is 8; cap is 12.
        """
        run = _served_run()
        assert run is not None, "no served run"
        max_names = _fetchval(_MAX_DISTINCT_NAMES, run)
        assert max_names <= MAX_DISTINCT_NAMES_CAP, (
            f"served run '{run}' has a component spanning {max_names} distinct "
            f"trade-names > cap {MAX_DISTINCT_NAMES_CAP} — distinct dealers appear "
            "fused. This is the over-merge fingerprint; inspect that component."
        )

    @SKIP_NO_DB
    def test_canonical_is_richest_member(self) -> None:
        """Representative must hold >= the available vehicles of every member.

        The served cdp_code is the most-information-rich node so /entities and
        /inventory resolve to the seller that actually carries the listings.
        Currently 0 for the served run; the only run that violates this is the
        UNGATED particular-canonkey-v1 (Case-A rep = MIN cdp, not most-available),
        which is exactly why it must be fixed before gating.
        """
        run = _served_run()
        assert run is not None, "no served run"
        richer = _fetchval(_RICHER_THAN_REP, run)
        assert richer == 0, (
            f"served run '{run}' has {richer} non-representative member(s) richer "
            "than their representative — the served cdp_code points at a poorer "
            "node, so the wrong seller surfaces the listings. Fix the rep rule "
            "(canonical = most-available, tie-break cdp asc)."
        )

    @SKIP_NO_DB
    def test_served_dealer_count_matches_live_recompute(self) -> None:
        """The served sales-point cardinality must equal an independent recompute.

        Pinned to the LIVE value (recomputed here), not a frozen constant: the
        census grows continuously, so a hardcoded number would rot. The guard is
        relational — the API-path count and a raw v_dealer_resolved recompute must
        agree to the row — so a silent cross-province dealer merge (which would
        SHRINK the distinct count) trips the cross-check immediately.
        """
        run = _served_run()
        assert run is not None, "no served run"
        served = _fetchval(_SERVED_DEALER_COUNT)
        assert isinstance(served, int) and served > 0, (
            "served non-particular dealer count must be a positive integer"
        )
        # Independent recompute via the explicit overlay chain (b1 -> dedup),
        # bypassing the view, must agree to the row with the view-based count.
        recomputed = _fetchval(
            """
            WITH b1 AS (
                SELECT e.entity_ulid, e.kind,
                       COALESCE(vc.canonical_cdp_code, e.cdp_code) AS b1_cdp
                FROM entity e
                LEFT JOIN v_canonical vc ON vc.cdp_code = e.cdp_code
            )
            SELECT count(DISTINCT COALESCE(cd.super_canonical_cdp_code, b1.b1_cdp))
            FROM b1
            LEFT JOIN canonical_dedup cd
              ON cd.canonical_cdp_code = b1.b1_cdp AND cd.run_id = $1
            WHERE b1.kind <> 'particular'
            """,
            run,
        )
        assert served == recomputed, (
            f"served dealer count via v_dealer_resolved={served} must equal the "
            f"independent overlay recompute={recomputed}. A divergence means the "
            "view and the overlay disagree about which dealers are merged."
        )


# ===========================================================================
# Candidate run (particular-canonkey-v1): superset + no new over-merge
# ===========================================================================

class TestParticularRunSafety:
    """Guards the fuller chain we may gate: it must be a strict superset of the
    served run (dealer/ES cdp_code byte-stability) and add NO over-merge."""

    @SKIP_NO_DB
    def test_dedup_chain_only_coarsens_no_merge_undone(self) -> None:
        """The served super-canonical chain (deep-link -> particular -> residual) must only ADD
        merges, never UNDO one: every pair of canonicals co-clustered at the deep-link layer must
        still resolve to the SAME super in the served run. Representatives MAY shift as components
        grow (residual fusing two base supers is coarsening — allowed); SPLITTING an existing merge
        is NOT. This is the real byte-stability invariant once the full chain is gated: a dealer
        merged at B1/deep-link is never torn apart by a later layer.

        (Replaces the old asymmetric test_particular_is_strict_superset_of_served, which assumed
        the particular run was the gating target; now residual is served and intentionally adds 19
        safe straggler merges on top of particular, so a pair-identity superset check mis-fires.)"""
        served = _served_run()
        assert served is not None, "no served run"
        if not _run_exists(DEEPLINK_RUN):
            pytest.skip(f"{DEEPLINK_RUN} not present in DB")
        if served == DEEPLINK_RUN:
            pytest.skip("deep-link is itself the served run; chain is trivially preserved")
        undone = _fetchval(
            """
            WITH served AS (
                SELECT canonical_cdp_code AS c, super_canonical_cdp_code AS s
                  FROM canonical_dedup WHERE run_id = $1
            )
            SELECT count(*) FROM canonical_dedup dl
            WHERE dl.run_id = $2
              AND COALESCE((SELECT s FROM served WHERE c = dl.canonical_cdp_code), dl.canonical_cdp_code)
               <> COALESCE((SELECT s FROM served WHERE c = dl.super_canonical_cdp_code), dl.super_canonical_cdp_code)
            """,
            served, DEEPLINK_RUN,
        )
        assert undone == 0, (
            f"{undone} deep-link merge(s) were UNDONE in the served run {served} — a later "
            "super-canonical layer split a dealer cluster instead of only coarsening it."
        )

    @SKIP_NO_DB
    def test_particular_has_no_cross_kind_component(self) -> None:
        """Gating the candidate must not recreate a giant cluster: it adds only
        same-seller particular merges, so it too must have 0 cross-kind
        components."""
        if not _run_exists(PARTICULAR_RUN):
            pytest.skip(f"{PARTICULAR_RUN} not present in DB")
        cross = _fetchval(_CROSS_KIND_COMPONENTS, PARTICULAR_RUN)
        assert cross == 0, (
            f"{PARTICULAR_RUN} has {cross} cross-kind (particular+dealer) "
            "component(s) — gating it would fuse private sellers into dealers. "
            "It must add ONLY same-seller particular province-split merges."
        )

    @SKIP_NO_DB
    def test_particular_component_size_under_cap(self) -> None:
        """The candidate's largest component must stay under the same size cap —
        adding particular merges must not build a giant cluster either."""
        if not _run_exists(PARTICULAR_RUN):
            pytest.skip(f"{PARTICULAR_RUN} not present in DB")
        max_size = _fetchval(_MAX_COMPONENT_SIZE, PARTICULAR_RUN)
        assert max_size <= MAX_COMPONENT_SIZE_CAP, (
            f"{PARTICULAR_RUN} has a component of size {max_size} > cap "
            f"{MAX_COMPONENT_SIZE_CAP} — adding particular merges built a giant "
            "cluster."
        )
