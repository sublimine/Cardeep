"""
tests/test_served_queries_have_country.py

META-GUARD -- every SERVED census query carries a country dimension (vector #5,
anti-regression of the serving blindfold).

This test does NOT seed data. It statically scans the SQL embedded in the serving
surface (``services/api/**`` routers + ``services/api/stats.py``/``deps.py`` + the
mint-time geo backbone ``pipeline/geo.py``) and FAILS if any query that reads the
served census of entities/vehicles lacks a ``country_code`` predicate/dimension AND
is not scoped by a single entity/vehicle identity. It is the binding guard that the
next person who adds ``FROM servable_entity WHERE province_code = $1`` (with no
country) is stopped at test time, not in production with a German dealer served to a
Spanish query.

CLASSIFICATION
--------------
  census surface : the SQL reads servable_entity / servable_vehicle / v_servable_dealer
                   / v_dealer_resolved / v_canonical_vehicle, or ``FROM/JOIN entity``,
                   ``FROM/JOIN vehicle``, or a geo backbone table. (\\b word-boundaries
                   keep ``vehicle`` from matching ``vehicle_event`` and ``entity`` from
                   matching ``entity_completion``.)
  PASS iff       : the SQL contains ``country_code`` (explicit dimension/predicate), OR
                   it is scoped by a single identity -- ``cdp_code = $/%``,
                   ``entity_ulid = $/%/ANY``, ``vehicle_ulid = $/%``,
                   ``platform_entity_ulid = $/%`` -- because a cdp_code/ulid already
                   pins the tenant and the country-proof clustering (#1-#4) guarantees a
                   cluster never spans borders. Monitoring tables (alert, source_health),
                   product_stats and the per-province seal views are not census surfaces.
"""
from __future__ import annotations

import ast
import os
import re
from pathlib import Path

import psycopg2
import pytest

_REPO = Path(__file__).resolve().parent.parent

# Every file whose SQL can reach the served census of entities/vehicles.
_SERVING_FILES = (
    "services/api/routers/geo.py",
    "services/api/routers/entities.py",
    "services/api/routers/vehicles.py",
    "services/api/routers/platforms.py",
    "services/api/routers/ops.py",
    "services/api/stats.py",
    "services/api/deps.py",
    "pipeline/geo.py",
)

# A SQL string reads the served CENSUS iff it names one of these row surfaces.
_CENSUS_SURFACE = re.compile(
    r"\b(servable_entity|servable_vehicle|v_servable_dealer|v_dealer_resolved|"
    r"v_canonical_vehicle)\b"
    r"|\bfrom\s+entity\b|\bjoin\s+entity\b"
    r"|\bfrom\s+vehicle\b|\bjoin\s+vehicle\b"
    r"|\bfrom\s+geo_province\b|\bfrom\s+geo_municipality\b|\bfrom\s+geo_comarca\b",
    re.IGNORECASE,
)

# Country-safe WITHOUT an explicit country_code: scoped by a single entity/vehicle
# identity (the cdp_code / *_ulid pins the tenant; #1-#4 keep clusters single-country).
_BY_IDENTITY = re.compile(
    r"\bcdp_code\s*=\s*[\$%]"
    r"|\bentity_ulid\s*\)?\s*=\s*[\$%]"
    r"|\bentity_ulid\s*=\s*any"
    r"|\bvehicle_ulid\s*=\s*[\$%]"
    r"|\bplatform_entity_ulid\s*=\s*[\$%]",
    re.IGNORECASE,
)

_COUNTRY = re.compile(r"\bcountry_code\b", re.IGNORECASE)

_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"


def _iter_sql_literals(path: Path):
    """Yield (lineno, sql) for every string literal that looks like a SQL query.

    Uses ``ast`` (not regex) so Python implicit string concatenation is already
    merged into one node -- a multi-line query is seen whole, never split."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            low = node.value.lower()
            if "select" in low and "from" in low:
                yield node.lineno, node.value


def _census_offenders() -> list[tuple[str, int, str]]:
    offenders: list[tuple[str, int, str]] = []
    for rel in _SERVING_FILES:
        path = _REPO / rel
        assert path.exists(), f"serving file vanished from the scan set: {rel}"
        for lineno, sql in _iter_sql_literals(path):
            norm = " ".join(sql.split())
            if not _CENSUS_SURFACE.search(norm):
                continue
            if _COUNTRY.search(norm) or _BY_IDENTITY.search(norm):
                continue
            offenders.append((rel, lineno, norm[:140]))
    return offenders


@pytest.mark.unit
def test_every_served_census_query_carries_country():
    """No served census query may be country-blind (unless scoped by a single identity)."""
    offenders = _census_offenders()
    assert not offenders, (
        "SERVED census query without a country dimension (no `country_code` predicate "
        "and not scoped by a single entity/vehicle identity):\n"
        + "\n".join(f"  {f}:{ln}  {sql}" for f, ln, sql in offenders)
        + "\n\nAdd `AND country_code = $N` (default the request to 'ES') or scope the "
        "query by cdp_code/entity_ulid/vehicle_ulid."
    )


@pytest.mark.unit
def test_scan_actually_sees_served_queries():
    """Guard the guard: the scanner must actually find census SQL in the serving files
    (a silent zero-match would make the offender test vacuously green)."""
    seen = 0
    for rel in _SERVING_FILES:
        for _ln, sql in _iter_sql_literals(_REPO / rel):
            if _CENSUS_SURFACE.search(" ".join(sql.split())):
                seen += 1
    assert seen >= 10, f"scanner saw only {seen} census queries -- the matcher is broken"


# ---------------------------------------------------------------------------
# Structural (DB): the served census views expose the country dimension
# ---------------------------------------------------------------------------
def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


@pytest.mark.integration
def test_served_views_expose_country_dimension():
    """servable_entity and v_servable_dealer MUST project country_code (read-only check;
    refuses :5433, skips if unreachable). v_dealer_resolved is intentionally excluded:
    it is a resolution map keyed by cdp_code (which embeds the country) and the
    country-proof clustering already forbids a cross-border cluster."""
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip("refusing to introspect :5433 (live production); use the :5434 dry-run")
    try:
        conn = psycopg2.connect(dsn, connect_timeout=3)
    except Exception:
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")
    try:
        with conn.cursor() as cur:
            for view in ("servable_entity", "v_servable_dealer"):
                cur.execute(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name = %s AND column_name = 'country_code'",
                    (view,),
                )
                assert cur.fetchone() is not None, (
                    f"served view '{view}' does not expose country_code -- the served "
                    "census has no tenant dimension (apply migration 0058).")
    finally:
        conn.close()
