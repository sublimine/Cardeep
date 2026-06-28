"""GeoNames -> country geo-pack EXTRACTOR (Country-Autopilot, Phase C).

Derives a new country's geo backbone from the FREE, CC-BY GeoNames dump
(`allCountries.txt` / `<CC>.txt`, the `geoname` table 19-col TSV) plus
`hierarchy.txt`, and emits the contract artifacts the generic engine already
consumes:

    countries/<CC>/geo/backbone.csv     L1 + region-label + LAU + official code
    countries/<CC>/geo/centroides.csv   lat/lon per municipality (KNN seed)

and a loader that inserts country-scoped ``(country_code, code)`` rows into
``geo_province`` / ``geo_municipality`` (the caller owns the transaction; the
test rolls back, so nothing persists).

Admin-tree mapping (the CHECKPOINT -- judgement, not mechanical)
---------------------------------------------------------------
GeoNames exposes feature codes ADM1 (top region), ADM2 (sub-region), and
populated places (feature_class 'P': PPL/PPLA/...). Cardeep's schema is
``geo_province`` (the subdivision that forms the cdp_code segment) carrying a
region label (``ccaa_code``/``ccaa_name``), and ``geo_municipality`` (LAU).

The DEFAULT mapping is chosen to be byte-faithful to the ES ground truth
(`scripts/load_geo.py`): the INE *province* == GeoNames **ADM2**, and the INE
*autonomous community* (the ``ccaa`` region label) == GeoNames **ADM1**. Hence:

    region-label (ccaa)  <- ADM1
    geo_province         <- ADM2   (falls back to ADM1 when a country has no
                                    ADM2 tier)
    geo_municipality     <- populated places (feature_class 'P', admin-relevant
                                    feature codes)

This level->tier binding is the per-country "manifiesto de mapeo de niveles" of
COUNTRY-PACK-CONTRACT.md (Etapa 6) and is parameterised via ``GeoLevelMapping``
so a country whose official subdivision is ADM1 (or whose LAU set is supplied by
an authoritative Eurostat-LAU table) can override it. It is a DECLARED CHECKPOINT
because a wrong binding silently mis-mints every cdp_code for the country.

Official-code cross-walk (the second CHECKPOINT)
------------------------------------------------
GeoNames admin/place codes are NOT national official codes. When a Eurostat-LAU
cross-walk is supplied (``CrossWalk``), the official code is taken from it
(provenance ``eurostat_lau``). Otherwise the extractor falls back to a code
DERIVED from GeoNames and records the provenance as ``geonames_fallback`` so the
gap is auditable per row (never silently presented as official):
    * province fallback     = ``admin1_code + admin2_code`` (country-unique).
    * municipality fallback = the GeoNames ``geonameid`` (globally unique).

Determinism / network
---------------------
``parse_*`` and ``build_geo_pack`` are pure and never touch the network. The
real download is the separate :func:`download_geonames` (mocked in tests).
"""
from __future__ import annotations

import csv
import io
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

# ---------------------------------------------------------------------------
# GeoNames `geoname` table format -- the 19 tab-separated columns.
# [ASSUMED] matches the documented GeoNames export schema (geoname table /
# allCountries readme); not re-fetched live in this environment. The parser is
# tolerant of >19 columns and ignores the ones the extractor does not use.
# ---------------------------------------------------------------------------
GEONAMES_NUM_COLS: int = 19

_COL_GEONAMEID = 0
_COL_NAME = 1
_COL_ASCIINAME = 2
_COL_LAT = 4
_COL_LON = 5
_COL_FEATURE_CLASS = 6
_COL_FEATURE_CODE = 7
_COL_COUNTRY = 8
_COL_ADMIN1 = 10
_COL_ADMIN2 = 11
_COL_POPULATION = 14

# Populated-place feature codes that count as an LAU/municipality. PPLX (section
# of a populated place), PPLH (historical), PPLQ (abandoned), PPLW (destroyed)
# are deliberately EXCLUDED -- they are not local administrative units.
DEFAULT_MUNI_FEATURE_CODES: frozenset[str] = frozenset(
    {"PPL", "PPLA", "PPLA2", "PPLA3", "PPLA4", "PPLA5", "PPLC", "PPLG", "PPLS"}
)

_FEATURE_CLASS_POPULATED = "P"

# Provenance tags for the official-code cross-walk (the CHECKPOINT).
SOURCE_OFFICIAL = "eurostat_lau"
SOURCE_FALLBACK = "geonames_fallback"


# ===========================================================================
# Immutable value objects
# ===========================================================================
@dataclass(frozen=True)
class GeoNamesRow:
    """One parsed GeoNames `geoname` record (only the fields we use)."""

    geonameid: int
    name: str
    asciiname: str
    lat: float | None
    lon: float | None
    feature_class: str
    feature_code: str
    country_code: str
    admin1_code: str
    admin2_code: str
    population: int


@dataclass(frozen=True)
class GeoLevelMapping:
    """Which GeoNames feature codes populate each Cardeep geo tier.

    Defaults match the ES ground truth (province == ADM2, region == ADM1, LAU ==
    populated place). Override per country in its manifest.
    """

    region_feature: str = "ADM1"
    province_feature: str = "ADM2"
    municipality_feature_codes: frozenset[str] = DEFAULT_MUNI_FEATURE_CODES


DEFAULT_MAPPING = GeoLevelMapping()


@dataclass(frozen=True)
class CrossWalk:
    """Eurostat-LAU cross-walk GeoNames-code -> OFFICIAL code.

    ``province`` is keyed by the GeoNames province key ("<admin1>.<admin2>", or
    "<admin1>" when the province tier is ADM1). ``municipality`` is keyed by the
    GeoNames ``geonameid``. A missing key -> declared GeoNames fallback.
    """

    province: Mapping[str, str] = field(default_factory=dict)
    municipality: Mapping[int, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ProvinceRow:
    """A ``geo_province`` row: the cdp-segment subdivision + its region label."""

    country_code: str
    code: str            # official subdivision code (-> geo_province.code)
    name: str
    region_code: str     # ccaa-equivalent 2-char label code (-> ccaa_code)
    region_name: str     # -> ccaa_name
    code_source: str     # SOURCE_OFFICIAL | SOURCE_FALLBACK


@dataclass(frozen=True)
class MunicipalityRow:
    """A ``geo_municipality`` row (LAU) with its centroid."""

    country_code: str
    code: str            # official LAU code (-> geo_municipality.code)
    name: str
    province_code: str   # FK -> geo_province.code (same official code)
    lat: float | None
    lon: float | None
    code_source: str     # SOURCE_OFFICIAL | SOURCE_FALLBACK


@dataclass(frozen=True)
class GeoPack:
    """The fully-derived geo pack for one country (sorted, deterministic)."""

    country_code: str
    provinces: tuple[ProvinceRow, ...]
    municipalities: tuple[MunicipalityRow, ...]
    unresolved_municipalities: tuple[int, ...] = ()

    def backbone_rows(self) -> list[dict[str, str]]:
        """One dict per municipality joined to its province + region label."""
        by_prov = {p.code: p for p in self.provinces}
        rows: list[dict[str, str]] = []
        for m in self.municipalities:
            p = by_prov.get(m.province_code)
            rows.append(
                {
                    "country_code": self.country_code,
                    "region_code": p.region_code if p else "",
                    "region_name": p.region_name if p else "",
                    "province_code": m.province_code,
                    "province_name": p.name if p else "",
                    "municipality_code": m.code,
                    "municipality_name": m.name,
                    "province_code_source": p.code_source if p else "",
                    "municipality_code_source": m.code_source,
                }
            )
        rows.sort(key=lambda r: (r["province_code"], r["municipality_code"]))
        return rows


# ===========================================================================
# Parsing (pure; no network)
# ===========================================================================
def _to_float(raw: str) -> float | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _to_int(raw: str, default: int = 0) -> int:
    raw = raw.strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def parse_geonames(text: str | Iterable[str]) -> tuple[GeoNamesRow, ...]:
    """Parse a GeoNames `geoname` 19-col TSV dump into ``GeoNamesRow`` records.

    Tolerant: blank lines are skipped, rows with fewer than ``GEONAMES_NUM_COLS``
    columns are skipped (malformed), extra columns are ignored.
    """
    lines = text.splitlines() if isinstance(text, str) else list(text)
    out: list[GeoNamesRow] = []
    for line in lines:
        if not line or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        if len(f) < GEONAMES_NUM_COLS:
            continue
        out.append(
            GeoNamesRow(
                geonameid=_to_int(f[_COL_GEONAMEID]),
                name=f[_COL_NAME].strip(),
                asciiname=f[_COL_ASCIINAME].strip(),
                lat=_to_float(f[_COL_LAT]),
                lon=_to_float(f[_COL_LON]),
                feature_class=f[_COL_FEATURE_CLASS].strip(),
                feature_code=f[_COL_FEATURE_CODE].strip(),
                country_code=f[_COL_COUNTRY].strip(),
                admin1_code=f[_COL_ADMIN1].strip(),
                admin2_code=f[_COL_ADMIN2].strip(),
                population=_to_int(f[_COL_POPULATION]),
            )
        )
    return tuple(out)


def parse_hierarchy(text: str | Iterable[str]) -> dict[int, int]:
    """Parse GeoNames `hierarchy.txt` (parentId<TAB>childId<TAB>type) into a
    child-geonameid -> parent-geonameid map. 'ADM'-typed links win over untyped
    ones when a child appears more than once (admin parentage is preferred)."""
    lines = text.splitlines() if isinstance(text, str) else list(text)
    child_to_parent: dict[int, int] = {}
    child_typed: set[int] = set()
    for line in lines:
        if not line or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        if len(f) < 2:
            continue
        parent = _to_int(f[0], default=-1)
        child = _to_int(f[1], default=-1)
        if parent < 0 or child < 0:
            continue
        link_type = f[2].strip() if len(f) >= 3 else ""
        is_adm = link_type == "ADM"
        if child in child_to_parent and child in child_typed and not is_adm:
            continue  # keep the already-recorded ADM parent
        child_to_parent[child] = parent
        if is_adm:
            child_typed.add(child)
    return child_to_parent


# ===========================================================================
# Cross-walk to OFFICIAL code (the CHECKPOINT)
# ===========================================================================
def _province_key(admin1_code: str, admin2_code: str) -> str:
    return f"{admin1_code}.{admin2_code}" if admin2_code else admin1_code


def crosswalk_province_code(
    admin1_code: str, admin2_code: str, crosswalk: CrossWalk | None
) -> tuple[str, str]:
    """Return (official_code, provenance). Falls back to a country-unique code
    derived from the GeoNames admin codes, DECLARED via ``SOURCE_FALLBACK``."""
    key = _province_key(admin1_code, admin2_code)
    if crosswalk and key in crosswalk.province:
        return crosswalk.province[key], SOURCE_OFFICIAL
    fallback = f"{admin1_code}{admin2_code}" if admin2_code else admin1_code
    return fallback, SOURCE_FALLBACK


def crosswalk_municipality_code(
    geonameid: int, crosswalk: CrossWalk | None
) -> tuple[str, str]:
    """Return (official_code, provenance). Falls back to the GeoNames geonameid
    (globally unique), DECLARED via ``SOURCE_FALLBACK``."""
    if crosswalk and geonameid in crosswalk.municipality:
        return crosswalk.municipality[geonameid], SOURCE_OFFICIAL
    return str(geonameid), SOURCE_FALLBACK


def _region_code_map(admin1_codes: Iterable[str]) -> dict[str, str]:
    """Deterministic ADM1 -> 2-char region (ccaa) code. Uses the admin1 code
    verbatim when it already fits CHAR(2) (zero-padding a bare numeric), else
    assigns a stable ordinal by sorted admin1 code (cap 99 regions)."""
    codes = sorted({c for c in admin1_codes if c})
    out: dict[str, str] = {}
    ordinal = 0
    for c in codes:
        if len(c) <= 2:
            out[c] = c.zfill(2) if c.isdigit() else c.rjust(2)
        else:
            ordinal += 1
            out[c] = str(ordinal).zfill(2)
    return out


# ===========================================================================
# Build the admin tree -> GeoPack
# ===========================================================================
def _resolve_province_row(
    ppl: GeoNamesRow,
    adm_by_key: Mapping[tuple[str, str], GeoNamesRow],
    province_by_geonameid: Mapping[int, GeoNamesRow],
    hierarchy: Mapping[int, int],
) -> GeoNamesRow | None:
    """Find the province-tier ADM row a populated place belongs to.

    Primary: the PPL's own (admin1_code, admin2_code). Fallback: walk the
    hierarchy.txt parent chain until a province-tier geonameid is reached
    (this is the path a PPL with an empty admin2_code MUST take). Pure: all
    indices are passed in (no shared mutable state)."""
    if ppl.admin2_code:
        hit = adm_by_key.get((ppl.admin1_code, ppl.admin2_code))
        if hit is not None:
            return hit
    seen: set[int] = set()
    cur = ppl.geonameid
    while cur in hierarchy and cur not in seen:
        seen.add(cur)
        cur = hierarchy[cur]
        if cur in province_by_geonameid:
            return province_by_geonameid[cur]
    return None


def build_geo_pack(
    rows: Iterable[GeoNamesRow],
    *,
    country_code: str,
    hierarchy: Mapping[int, int] | None = None,
    mapping: GeoLevelMapping = DEFAULT_MAPPING,
    crosswalk: CrossWalk | None = None,
) -> GeoPack:
    """Assemble the country geo pack from parsed GeoNames rows.

    region-label <- ADM1, geo_province <- ADM2 (or ADM1 when the country has no
    ADM2 tier), geo_municipality <- populated places. Official codes via the
    cross-walk with a declared GeoNames fallback. Pure / deterministic.
    """
    hierarchy = hierarchy or {}
    country_rows = [r for r in rows if r.country_code == country_code]

    # ADM1 region label index.
    adm1_by_code = {
        r.admin1_code: r
        for r in country_rows
        if r.feature_code == mapping.region_feature and r.admin1_code
    }
    region_code_for = _region_code_map(adm1_by_code.keys())

    # Province tier: ADM2 when present anywhere, else fall back to ADM1.
    has_adm2 = any(r.feature_code == mapping.province_feature for r in country_rows)
    province_feature = mapping.province_feature if has_adm2 else mapping.region_feature
    province_src_rows = [r for r in country_rows if r.feature_code == province_feature]

    # Index provinces by (admin1, admin2) and by geonameid (for hierarchy walk).
    adm_by_key: dict[tuple[str, str], GeoNamesRow] = {}
    province_by_geonameid: dict[int, GeoNamesRow] = {}
    for r in province_src_rows:
        adm_by_key[(r.admin1_code, r.admin2_code)] = r
        province_by_geonameid[r.geonameid] = r

    def _region(admin1_code: str) -> tuple[str, str]:
        rc = region_code_for.get(admin1_code, (admin1_code[:2] or "00").rjust(2))
        adm1 = adm1_by_code.get(admin1_code)
        rname = adm1.name if adm1 else admin1_code
        return rc, rname

    # Provinces.
    provinces: list[ProvinceRow] = []
    prov_official_for_geonameid: dict[int, str] = {}
    for r in province_src_rows:
        admin2 = r.admin2_code if has_adm2 else ""
        code, src = crosswalk_province_code(r.admin1_code, admin2, crosswalk)
        rc, rname = _region(r.admin1_code)
        provinces.append(
            ProvinceRow(
                country_code=country_code,
                code=code,
                name=r.name,
                region_code=rc,
                region_name=rname,
                code_source=src,
            )
        )
        prov_official_for_geonameid[r.geonameid] = code

    # Municipalities (populated places).
    municipalities: list[MunicipalityRow] = []
    unresolved: list[int] = []
    for r in country_rows:
        if r.feature_class != _FEATURE_CLASS_POPULATED:
            continue
        if r.feature_code not in mapping.municipality_feature_codes:
            continue
        parent = _resolve_province_row(
            r, adm_by_key, province_by_geonameid, hierarchy
        )
        if parent is None:
            unresolved.append(r.geonameid)
            continue
        prov_code = prov_official_for_geonameid[parent.geonameid]
        code, src = crosswalk_municipality_code(r.geonameid, crosswalk)
        municipalities.append(
            MunicipalityRow(
                country_code=country_code,
                code=code,
                name=r.name,
                province_code=prov_code,
                lat=r.lat,
                lon=r.lon,
                code_source=src,
            )
        )

    provinces.sort(key=lambda p: p.code)
    municipalities.sort(key=lambda m: m.code)
    return GeoPack(
        country_code=country_code,
        provinces=tuple(provinces),
        municipalities=tuple(municipalities),
        unresolved_municipalities=tuple(sorted(unresolved)),
    )


# ===========================================================================
# Contract artifacts: backbone.csv + centroides.csv
# ===========================================================================
_BACKBONE_HEADER = [
    "country_code", "region_code", "region_name", "province_code",
    "province_name", "municipality_code", "municipality_name",
    "province_code_source", "municipality_code_source",
]


def write_backbone_csv(pack: GeoPack, path: str | Path) -> Path:
    """Emit ``countries/<CC>/geo/backbone.csv`` (L1 + region-label + LAU +
    official code + per-code provenance)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_BACKBONE_HEADER)
        w.writeheader()
        for row in pack.backbone_rows():
            w.writerow(row)
    return path


def write_centroides_csv(pack: GeoPack, path: str | Path) -> Path:
    """Emit ``countries/<CC>/geo/centroides.csv`` (lat/lon per municipality),
    sorted by municipality code; municipalities without a centroid are skipped."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["country_code", "municipality_code", "lat", "lon"])
        for m in sorted(pack.municipalities, key=lambda x: x.code):
            if m.lat is None or m.lon is None:
                continue
            w.writerow([pack.country_code, m.code, m.lat, m.lon])
    return path


# ===========================================================================
# Loader: insert country-scoped (country_code, code) rows. Caller owns the txn.
# ===========================================================================
def load_geo_pack(cursor, pack: GeoPack) -> tuple[int, int]:
    """INSERT the pack's provinces then municipalities into geo_province /
    geo_municipality via a psycopg2 *cursor*. Provinces first (the municipality
    FK targets them). ON CONFLICT DO NOTHING -> idempotent, mirroring
    scripts/load_geo.py. NO commit/rollback here -- the caller owns the
    transaction (the test rolls back, so nothing persists). Returns the count of
    province / municipality rows the pack contains.
    """
    if pack.provinces:
        cursor.executemany(
            "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
            "VALUES (%s, %s, %s, %s, %s) "
            "ON CONFLICT (country_code, code) DO NOTHING",
            [
                (p.code, p.name, p.region_code, p.region_name, p.country_code)
                for p in pack.provinces
            ],
        )
    if pack.municipalities:
        cursor.executemany(
            "INSERT INTO geo_municipality "
            "(code, name, province_code, comarca_id, lat, lon, country_code) "
            "VALUES (%s, %s, %s, NULL, %s, %s, %s) "
            "ON CONFLICT (country_code, code) DO NOTHING",
            [
                (m.code, m.name, m.province_code, m.lat, m.lon, m.country_code)
                for m in pack.municipalities
            ],
        )
    return len(pack.provinces), len(pack.municipalities)


# ===========================================================================
# Convenience orchestrator (pure: parse files -> build -> write artifacts)
# ===========================================================================
def extract_country(
    country_code: str,
    geonames_path: str | Path,
    hierarchy_path: str | Path | None,
    out_dir: str | Path,
    *,
    mapping: GeoLevelMapping = DEFAULT_MAPPING,
    crosswalk: CrossWalk | None = None,
) -> GeoPack:
    """Parse the GeoNames dump + hierarchy from disk, build the pack, and write
    ``backbone.csv`` + ``centroides.csv`` under ``out_dir``. No network."""
    rows = parse_geonames(Path(geonames_path).read_text(encoding="utf-8"))
    hierarchy: dict[int, int] = {}
    if hierarchy_path is not None and Path(hierarchy_path).exists():
        hierarchy = parse_hierarchy(Path(hierarchy_path).read_text(encoding="utf-8"))
    pack = build_geo_pack(
        rows, country_code=country_code, hierarchy=hierarchy,
        mapping=mapping, crosswalk=crosswalk,
    )
    out_dir = Path(out_dir)
    write_backbone_csv(pack, out_dir / "backbone.csv")
    write_centroides_csv(pack, out_dir / "centroides.csv")
    return pack


# ===========================================================================
# REAL network downloader -- SEPARATE, mocked in tests, never called by extract.
# ===========================================================================
_GEONAMES_BASE = "https://download.geonames.org/export/dump"


def download_geonames(
    country_code: str,
    dest_dir: str | Path,
    *,
    opener=None,
) -> tuple[Path, Path]:
    """Download + unzip the GeoNames per-country dump (``<CC>.zip`` -> ``<CC>.txt``)
    and the global ``hierarchy.zip`` -> ``hierarchy.txt`` into ``dest_dir``.

    This is the ONLY network I/O in the module and is intentionally isolated so
    the extractor and its tests stay deterministic. ``opener`` is injectable
    (defaults to ``urllib.request.urlopen``) purely for future testability.
    Returns (geonames_txt_path, hierarchy_txt_path).
    """
    if opener is None:  # pragma: no cover - real network path, not unit-tested
        from urllib.request import urlopen

        opener = urlopen

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    def _fetch_zip(url: str, member_suffix: str) -> Path:
        with opener(url) as resp:  # pragma: no cover - network
            payload = resp.read()
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            member = next(n for n in zf.namelist() if n.endswith(member_suffix))
            target = dest / Path(member).name
            target.write_bytes(zf.read(member))
        return target

    cc = country_code.upper()
    geo_txt = _fetch_zip(f"{_GEONAMES_BASE}/{cc}.zip", f"{cc}.txt")
    hier_txt = _fetch_zip(f"{_GEONAMES_BASE}/hierarchy.zip", "hierarchy.txt")
    return geo_txt, hier_txt


__all__ = [
    "GEONAMES_NUM_COLS",
    "DEFAULT_MUNI_FEATURE_CODES",
    "SOURCE_OFFICIAL",
    "SOURCE_FALLBACK",
    "GeoNamesRow",
    "GeoLevelMapping",
    "DEFAULT_MAPPING",
    "CrossWalk",
    "ProvinceRow",
    "MunicipalityRow",
    "GeoPack",
    "parse_geonames",
    "parse_hierarchy",
    "crosswalk_province_code",
    "crosswalk_municipality_code",
    "build_geo_pack",
    "write_backbone_csv",
    "write_centroides_csv",
    "load_geo_pack",
    "extract_country",
    "download_geonames",
]
