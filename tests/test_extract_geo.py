"""
tests/test_extract_geo.py

GOLDEN -- Country-Autopilot Phase C: the GeoNames geo EXTRACTOR
(``pipeline/autopilot/extract_geo.py``).

What this pins (deterministic, NO network):
  * GeoNames `geoname` 19-col TSV parse + `hierarchy.txt` parse.
  * The admin tree build  region(ADM1) -> province(ADM2) -> municipality(PPL),
    including the parentage that can ONLY be resolved via hierarchy.txt (a PPL
    with an EMPTY admin2_code).
  * The cross-walk of a GeoNames admin/place code to an OFFICIAL code via a
    supplied Eurostat-LAU table, with the GeoNames-derived code as a DECLARED
    fallback (provenance recorded per row -> the CHECKPOINT is auditable).
  * Emission of the contract artifacts `countries/<CC>/geo/backbone.csv` +
    `centroides.csv`.
  * A loader that inserts country-scoped (country_code, code) rows into
    geo_province / geo_municipality on the :5434 dry-run, INSIDE a transaction
    that the test ROLLS BACK -- proving ES geo stays byte-identical and the new
    country never leaks into the ES scope.

The real network downloader is a SEPARATE function and is MOCKED here; the
extractor/build path never touches the network (asserted).

ISOLATION (inviolable): the DB test runs ONLY against the dry-run DB (:5434).
It HARD-REFUSES :5433 (live production) by DSN string AND asserts the census is
empty before seeding, then rolls back.
"""
from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import psycopg2
import pytest

from pipeline.autopilot import extract_geo as eg

# ---------------------------------------------------------------------------
# Fixtures on disk (synthetic country 'XX')
# ---------------------------------------------------------------------------
_FIX = Path(__file__).resolve().parent / "fixtures"
_GEONAMES_XX = _FIX / "geonames_xx.txt"
_HIERARCHY_XX = _FIX / "hierarchy_xx.txt"

# Eurostat-LAU cross-walk for 'XX': all provinces + 3/5 municipalities get an
# OFFICIAL code; the remaining 2 municipalities deliberately fall back to the
# DECLARED GeoNames-derived code (geonameid) -> both paths are exercised.
_XWALK = eg.CrossWalk(
    province={"01.A1": "NP", "01.A2": "EF", "02.B1": "SB"},
    municipality={3001: "NP001", 3002: "NP002", 3003: "EF001"},
)

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"


def _build_xx() -> "eg.GeoPack":
    rows = eg.parse_geonames(_GEONAMES_XX.read_text(encoding="utf-8"))
    hierarchy = eg.parse_hierarchy(_HIERARCHY_XX.read_text(encoding="utf-8"))
    return eg.build_geo_pack(
        rows, country_code="XX", hierarchy=hierarchy, crosswalk=_XWALK
    )


# ===========================================================================
# UNIT -- parse
# ===========================================================================
@pytest.mark.unit
def test_parse_geonames_19_cols():
    rows = eg.parse_geonames(_GEONAMES_XX.read_text(encoding="utf-8"))
    # 12 data rows in the fixture (incl. the 2 deliberately-excluded features).
    assert len(rows) == 12
    by_id = {r.geonameid: r for r in rows}
    adm1 = by_id[1001]
    assert (adm1.name, adm1.feature_class, adm1.feature_code, adm1.admin1_code) == (
        "Norland", "A", "ADM1", "01")
    ppl = by_id[3001]
    assert (ppl.feature_class, ppl.feature_code, ppl.admin1_code, ppl.admin2_code) == (
        "P", "PPLA", "01", "A1")
    assert ppl.lat == pytest.approx(11.10) and ppl.lon == pytest.approx(11.10)


@pytest.mark.unit
def test_parse_hierarchy_child_to_parent():
    h = eg.parse_hierarchy(_HIERARCHY_XX.read_text(encoding="utf-8"))
    # child -> parent
    assert h[3005] == 2003          # Capeside -> Southbay Province
    assert h[2001] == 1001          # Northport Province -> Norland
    assert len(h) == 8


# ===========================================================================
# UNIT -- admin tree (region/province/municipality) + hierarchy.txt parentage
# ===========================================================================
@pytest.mark.unit
def test_build_tree_levels_and_counts():
    pack = _build_xx()
    # 3 provinces (ADM2), 5 municipalities (PPL/PPLA; PPLX + mountain excluded).
    assert len(pack.provinces) == 3
    assert len(pack.municipalities) == 5
    # PPLX (3006) and the mountain (4001) must NOT appear as municipalities.
    muni_names = {m.name for m in pack.municipalities}
    assert "Old Harbor Ruins" not in muni_names and "Mount Nor" not in muni_names


@pytest.mark.unit
def test_region_label_is_adm1():
    pack = _build_xx()
    prov = {p.code: p for p in pack.provinces}
    # region-label (ccaa-equiv) comes from the ADM1 parent.
    assert (prov["NP"].region_code, prov["NP"].region_name) == ("01", "Norland")
    assert (prov["EF"].region_code, prov["EF"].region_name) == ("01", "Norland")
    assert (prov["SB"].region_code, prov["SB"].region_name) == ("02", "Sudland")


@pytest.mark.unit
def test_municipality_parentage_via_hierarchy_when_admin2_empty():
    """Capeside (3005) has an EMPTY admin2_code in the fixture; its province
    parent ('SB') can ONLY be recovered through hierarchy.txt (2003 -> 3005).
    This proves hierarchy.txt parsing is load-bearing, not decorative."""
    pack = _build_xx()
    by_code = {m.code: m for m in pack.municipalities}
    cap = by_code["3005"]
    assert cap.name == "Capeside"
    assert cap.province_code == "SB"


# ===========================================================================
# UNIT -- cross-walk to OFFICIAL code (the CHECKPOINT) + declared fallback
# ===========================================================================
@pytest.mark.unit
def test_province_codes_are_official_from_crosswalk():
    pack = _build_xx()
    prov = {p.code: p for p in pack.provinces}
    assert set(prov) == {"NP", "EF", "SB"}
    assert all(p.code_source == "eurostat_lau" for p in pack.provinces)


@pytest.mark.unit
def test_municipality_official_vs_declared_fallback():
    pack = _build_xx()
    by_code = {m.code: m for m in pack.municipalities}
    # crosswalk hits -> official code + provenance 'eurostat_lau'
    assert by_code["NP001"].code_source == "eurostat_lau"
    assert by_code["EF001"].code_source == "eurostat_lau"
    # crosswalk misses (3004, 3005) -> DECLARED fallback = GeoNames geonameid
    assert by_code["3004"].code_source == "geonames_fallback"
    assert by_code["3005"].code_source == "geonames_fallback"


# ===========================================================================
# UNIT -- contract artifacts (backbone.csv + centroides.csv), deterministic
# ===========================================================================
@pytest.mark.unit
def test_backbone_csv_golden(tmp_path):
    pack = _build_xx()
    out = tmp_path / "backbone.csv"
    eg.write_backbone_csv(pack, out)
    got = out.read_text(encoding="utf-8").splitlines()
    assert got[0] == (
        "country_code,region_code,region_name,province_code,province_name,"
        "municipality_code,municipality_name,province_code_source,"
        "municipality_code_source")
    # 5 municipality rows, deterministically sorted by (province_code, municipality_code).
    assert len(got) == 1 + 5
    # spot-check the hierarchy-resolved fallback row.
    assert ("XX,02,Sudland,SB,Southbay Province,3005,Capeside,"
            "eurostat_lau,geonames_fallback") in got


@pytest.mark.unit
def test_centroides_csv_golden(tmp_path):
    pack = _build_xx()
    out = tmp_path / "centroides.csv"
    eg.write_centroides_csv(pack, out)
    got = out.read_text(encoding="utf-8").splitlines()
    assert got[0] == "country_code,municipality_code,lat,lon"
    assert len(got) == 1 + 5
    # centroid of Northport City (official code NP001).
    assert "XX,NP001,11.1,11.1" in got


# ===========================================================================
# UNIT -- the real downloader is SEPARATE and never invoked by extraction
# ===========================================================================
@pytest.mark.unit
def test_extract_country_orchestrator_writes_both_artifacts(tmp_path):
    """The file-based orchestrator parses the dump + hierarchy from disk, builds
    the pack, and writes both contract CSVs under out_dir. No network."""
    out = tmp_path / "XX" / "geo"
    pack = eg.extract_country(
        "XX", _GEONAMES_XX, _HIERARCHY_XX, out, crosswalk=_XWALK
    )
    assert len(pack.provinces) == 3 and len(pack.municipalities) == 5
    assert (out / "backbone.csv").exists() and (out / "centroides.csv").exists()
    # backbone has header + 5 LAU rows.
    assert len((out / "backbone.csv").read_text(encoding="utf-8").splitlines()) == 6


@pytest.mark.unit
def test_extraction_never_touches_network():
    """build_geo_pack / parse* are pure: the network downloader is a distinct
    function. Patch it to explode and prove the extract path never calls it."""
    with mock.patch.object(
        eg, "download_geonames", side_effect=AssertionError("network used!")
    ):
        pack = _build_xx()
    assert len(pack.provinces) == 3 and len(pack.municipalities) == 5


# ===========================================================================
# INTEGRATION (:5434 dry-run) -- country-scoped load, ES byte-identical, rollback
# ===========================================================================
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
    """Transactional connection to the dry-run DB, rolled back on teardown.

    Triple isolation guard against the live census (identical to the geo-width
    golden): refuse :5433; skip if unreachable; refuse to seed unless BOTH
    ``entity`` and ``vehicle`` are EMPTY.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the extract-geo golden against :5433 (live production); "
            "point CARDEEP_DSN at the :5434 dry-run")
    if not _db_reachable(dsn):
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")
    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM entity")
        n_entities = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM vehicle")
        n_vehicles = cur.fetchone()[0]
    if n_entities != 0 or n_vehicles != 0:
        conn.close()
        pytest.skip(
            f"target DB has {n_entities} entities / {n_vehicles} vehicles -- not the "
            "empty dry-run; refusing to seed against a populated census")
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


def _seed_es_baseline(cur) -> None:
    """A known ES province + municipality to prove the XX load never touches ES."""
    cur.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ('99', 'ES-Baseline-Prov', '97', 'ES-Baseline-Reg', 'ES')")
    cur.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, "
        "lat, lon, country_code) VALUES ('99001', 'ES-Baseline-Muni', '99', NULL, "
        "1.0, 2.0, 'ES')")


@pytest.mark.integration
def test_load_geo_pack_country_scoped(dry_conn):
    """The loader inserts XX provinces+municipalities under country_code='XX',
    the FK chain resolves (muni.province_code -> geo_province), centroids land in
    geo_municipality.lat/lon, and the seeded ES rows stay byte-identical. Rolled
    back by the fixture -> the dry-run returns to 0/0."""
    pack = _build_xx()
    with dry_conn.cursor() as cur:
        _seed_es_baseline(cur)
        n_prov, n_muni = eg.load_geo_pack(cur, pack)
        assert (n_prov, n_muni) == (3, 5)

        # XX rows present, correctly scoped.
        cur.execute("SELECT count(*) FROM geo_province WHERE country_code='XX'")
        assert cur.fetchone()[0] == 3
        cur.execute("SELECT count(*) FROM geo_municipality WHERE country_code='XX'")
        assert cur.fetchone()[0] == 5

        # FK chain + region label: Capeside (hierarchy-resolved, fallback code).
        cur.execute(
            "SELECT m.province_code, p.name, p.ccaa_code, p.ccaa_name, m.lat, m.lon "
            "FROM geo_municipality m JOIN geo_province p "
            "  ON p.country_code = m.country_code AND p.code = m.province_code "
            "WHERE m.country_code='XX' AND m.code='3005'")
        prov_code, prov_name, ccaa_code, ccaa_name, lat, lon = cur.fetchone()
        assert prov_code == "SB" and prov_name == "Southbay Province"
        assert ccaa_code.strip() == "02" and ccaa_name == "Sudland"
        assert float(lat) == pytest.approx(21.30) and float(lon) == pytest.approx(21.35)

        # ES byte-identity: the seeded ES province is untouched; no XX leaked into ES.
        cur.execute(
            "SELECT name, ccaa_name FROM geo_province "
            "WHERE country_code='ES' AND code='99'")
        assert cur.fetchone() == ("ES-Baseline-Prov", "ES-Baseline-Reg")
        cur.execute("SELECT count(*) FROM geo_province WHERE country_code='ES'")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM geo_municipality WHERE country_code='ES'")
        assert cur.fetchone()[0] == 1


@pytest.mark.integration
def test_load_is_rerun_safe_within_txn(dry_conn):
    """A second load of the same pack inside the same txn is a no-op (ON CONFLICT
    DO NOTHING) -> idempotent, mirroring scripts/load_geo.py."""
    pack = _build_xx()
    with dry_conn.cursor() as cur:
        eg.load_geo_pack(cur, pack)
        eg.load_geo_pack(cur, pack)  # must not raise on duplicate PKs
        cur.execute("SELECT count(*) FROM geo_province WHERE country_code='XX'")
        assert cur.fetchone()[0] == 3
        cur.execute("SELECT count(*) FROM geo_municipality WHERE country_code='XX'")
        assert cur.fetchone()[0] == 5
