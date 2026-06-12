# T10 — Geocoding + Address Parsing: Live 2026 Tooling Audit

> **Domain:** Forward + **reverse** geocoding and address parsing/normalization for
> CARDEEP — turning the messy location signals on a Spanish car point-of-sale
> (`lat/lon`, a free-text street line, a half-spelled city, sometimes only a postcode)
> into the **authoritative INE administrative grid**: `province_code` (CHAR(2)) and
> `municipality_code` (CHAR(5)). Self-hostable, offline, no per-call cost, at the scale
> of the full Spanish dealer census and beyond.
>
> **Audited:** 2026-06-12. **Marking discipline:** every tool is **[VERIFIED]** (I fetched
> the repo / PyPI / release / dataset page this session, URL cited) or **[ASSUMED]**
> (inferred, not opened). No corpses are recommended.
>
> **Recency bar:** a library with no release in ~12 months is *suspect*; no commit in
> ~12 months is *dead for our purposes*. Stated explicitly per tool.

---

## 0. The CARDEEP-specific problem (why generic geocoder benchmarks lie)

CARDEEP does **not** want "an address string near a pin." It wants the **INE code** that
keys `geo_province` / `geo_municipality` (see `migrations/0001_geo.sql` **[VERIFIED, read
this session]**). The entire geo layer already exists:

- **`scripts/load_geo.py` [VERIFIED]** — loads the 52 INE provinces (hardcoded with CCAA)
  and ~8,132 municipalities from the official INE dictionary
  (`data/geo/diccionario_ine.xlsx`, sourced from
  `https://www.ine.es/daco/daco42/codmun/diccionario25.xlsx`). `geo_municipality` has
  `lat`/`lon` columns **that are currently NULL** (the INSERT only fills `code, name,
  province_code`).
- **`pipeline/geo.py::GeoResolver` [VERIFIED]** — accent/case/order-insensitive
  *name → INE code* resolver, bilingual-aware, with a curated province alias table
  (Menorca→07, Gipuzkoa→20, A Coruña→15, …). This is the **string path**.
- **`pipeline/geocode.py::ProvinceGeocoder` [VERIFIED]** — the *coordinate path*: a numpy
  nearest-labeled-point classifier. It pulls every entity that already has
  `lat/lon/province_code`, and for a new POI returns the `province_code` of the nearest
  labeled point (squared equirectangular distance with a `cos(lat)` longitude
  correction). No boundary polygons, no external dependency beyond numpy.

So the relevant questions are **not** "Nominatim vs Google accuracy on a random street."
They are:

1. **Reverse, province-level:** is the nearest-labeled-point classifier good enough? **(§5 — yes, with caveats.)**
2. **Reverse, municipality-level:** what is the upgrade path to assign the *exact* INE
   municipality from `lat/lon`? **(§6 — shapely + IGN polygons; this is the real upgrade.)**
3. **Address parsing:** when we only have a free-text Spanish address line, what splits it
   into `{road, house_number, city, postcode}` so `GeoResolver` can finish the job? **(§3 — libpostal.)**
4. **Forward / full geocoder:** do we ever need a Nominatim/Photon/Pelias-class engine,
   and if so which one? **(§2, §4 — Photon if anything; usually not.)**

A generic geocoder that hands back a display string and *its own* admin labels is a
**liability** here unless those labels carry **INE codes** — otherwise we pay to re-derive
what `GeoResolver` already does for free, and we inherit OSM's admin-naming noise.

---

## 1. Verdict up front

| Layer | Pick | Status | Why |
|---|---|---|---|
| **Reverse → province (incumbent)** | **`ProvinceGeocoder` (numpy nearest-point) — KEEP** | ✅ in-repo | Free, zero-dep, accurate for *large contiguous* provinces; self-improves as labeled density grows. Good enough for province-level. |
| **Reverse → exact municipality (the upgrade)** | **shapely 2.x + IGN municipal polygons (es-atlas TopoJSON, INE-coded)** | ✅ **alive** (shapely 2.1.2, 2025-09-24) | True point-in-polygon. Exact INE `code5`. Offline, one-time data load, ~8k polygons → STRtree lookup in microseconds. |
| **Address parsing / normalization** | **libpostal via `postal` (pypostal)** | ✅ **revived** (postal 1.1.11, 2025-10-29; libpostal commit 2025-12-06; Senzing data v1.2.0, 2025-11-07) | The only credible OSS multilingual parser; Senzing re-trains the model on a 6–12 mo cadence. Splits messy ES address lines into components for `GeoResolver`. |
| **Spanish-official reverse REST (validation / hard cases)** | **CartoCiudad `reverseGeocode` (CNIG/IGN)** | ✅ **alive** (service updated 2024–2025) | Returns `provinceCode` + `muniCode` **with INE coding**, plus postal address. Authoritative, free, Spain-only. Use as an oracle / fallback, not a bulk dependency. |
| **Self-hosted full geocoder (only if forward search at scale is ever needed)** | **Photon** | ✅ **alive** (1.2.0, 2026-06-11) | Lightweight vs Nominatim, OpenSearch 3.x, typo-tolerant, **official per-country dumps** (download Spain, skip the planet import). |
| **Nominatim** | *heavy fallback* | ✅ **alive** (5.3.2, 2026-04-10) | Gold-standard accuracy + structured search, but PostgreSQL/PostGIS, days-long import, 64GB+ class hardware. Overkill for "lat/lon → INE code." |
| **Pelias** | *do not adopt for this* | 🟡 **alive but heavy/slowing** | Multi-source ES7/8 stack, no tagged releases, commercial steward (geocode.earth). Operationally heavier than Photon with no INE-code payoff. |
| **`reverse_geocoder` (thampiman) / RetroGeo / osm_rg** | ❌ **not for INE precision** | ✅ alive (wheel 2025-05-29) | Offline KD-tree over GeoNames cities>1000 → city/admin1/admin2 names, **no INE codes, no municipal polygons**. It is literally a generalized clone of our own nearest-point trick — adopting it is lateral, not an upgrade. |

**Bottom line.** The incumbent `ProvinceGeocoder` is **correct for province-level** and
should stay. The genuine, bulletproof upgrade is **shapely 2.x point-in-polygon against
INE-coded IGN municipal polygons** for *exact municipality* assignment — fully offline,
~8k polygons, no running service. Add **libpostal (`postal`)** for parsing free-text
Spanish address lines into components, feeding the existing `GeoResolver`. Keep
**CartoCiudad's reverse REST** as the authoritative Spanish oracle for hard cases and for
auditing the polygon layer. A heavy self-hosted geocoder (Photon > Nominatim > Pelias) is
**only** justified if CARDEEP later needs full forward street-level search — it is not
needed to satisfy "lat/lon → province/municipality."

---

## 2. Self-hosted full geocoders — the heavyweight tier

These solve forward + reverse street-level geocoding by running a full search engine over
OSM. For CARDEEP they are **mostly overkill**: we need an INE code from a coordinate, not a
street name from a query. Audited honestly so the decision is on record.

### 2.1 Nominatim — alive, gold-standard, **too heavy for our need**

- **Repo:** https://github.com/osm-search/Nominatim — **[VERIFIED]**
- **Latest release:** **5.3.2, 2026-04-10** (5.3.1 2026-04-10, 5.3.0 2026-04-03, 5.0.0 was
  the "Python package" transition). **[VERIFIED via release search]** Actively maintained.
- **Stack:** PostgreSQL + PostGIS + osm2pgsql. Import of a full country/planet is a
  multi-hour-to-multi-day job; production guidance is 64GB+ RAM class for large extents.
- **Strengths:** best-in-class structured address search and filtering; the de-facto OSM
  geocoder; excellent reverse accuracy at street level.
- **Weaknesses for CARDEEP:** enormous operational surface (a stateful Postgres geocoding
  DB *separate* from our app Postgres), slow import, and — decisively — its reverse output
  is **OSM admin names, not INE codes**. We would still have to run `GeoResolver` on its
  output, i.e. pay for an engine to hand us a string we then re-resolve. **Not worth it for
  reverse-to-code.** Only consider if CARDEEP needs full forward street geocoding for many
  countries.
- **Verdict:** ✅ alive, ❌ disproportionate for this task-domain.

### 2.2 Photon — alive, **the one to pick *if* a self-hosted engine is needed**

- **Repo:** https://github.com/komoot/photon — **[VERIFIED]** 2.9k★, Apache-2.0, ~1,744 commits.
- **Latest release:** **1.2.0, 2026-06-11** **[VERIFIED]** — released *yesterday* relative
  to this audit. Unambiguously alive.
- **Stack:** Java 21+, **OpenSearch 3.x** when run against an external DB (embedded server
  otherwise). Import is **built on Nominatim** data but GraphHopper publishes **weekly
  dumps for the whole world AND for selected countries** — so you can pull a **Spain-only
  database** and skip the Nominatim import entirely. Planet DB ≈ 95GB; a country extract is
  far smaller.
- **Strengths:** lightweight relative to Nominatim, typo-tolerant search-as-you-type,
  native reverse geocoding, country/region filtering, no Postgres dependency. Setup is
  hours, not days.
- **Weaknesses:** still a running JVM + OpenSearch service to operate and update; reverse
  output is again OSM admin labels (no INE codes), so `GeoResolver` still runs downstream.
  64GB RAM recommended for planet (much less for Spain-only).
- **Verdict:** ✅ alive and modern. **The correct choice in this tier** — but only adopt it
  if/when forward street-level search becomes a real requirement. For pure reverse-to-INE,
  §6 (shapely + polygons) beats it on simplicity, cost, and exactness.

### 2.3 Pelias — alive but **do not adopt for this domain**

- **Repo:** https://github.com/pelias/pelias — **[VERIFIED]** 3.5k★, **"No releases
  published"** (versioning lives in sub-repos like `pelias/model`), Elasticsearch **7 and 8**.
- **Maintenance:** stewarded by **geocode.earth** (commercial hosted Pelias). The umbrella
  repo shows ongoing issues/commits but no tagged releases; the project leans on its
  commercial sponsor. I could **not** find a 2025 "maintenance mode" announcement
  **[VERIFIED — searched, not found]**, so I will not claim one; but the operational
  signal (multi-repo microservice stack, ES7/8, no umbrella releases) is heavier than
  Photon for no CARDEEP-specific benefit.
- **Strengths:** unifies OSM + OpenAddresses + GeoNames + Who's-on-First; strong full-text
  forward search; good multi-source coverage.
- **Weaknesses for CARDEEP:** a multi-container microservice fleet on Elasticsearch is the
  most operationally expensive option here, and like the others it yields no INE codes.
- **Verdict:** 🟡 alive, ❌ wrong tool for "lat/lon → INE code." Photon dominates it for our
  use case.

> **Tier conclusion.** None of the three heavyweight engines is needed to satisfy the
> mandate, because none returns INE codes — we would run `GeoResolver` on their output
> regardless. If a self-hosted engine is ever required for forward search, it is **Photon**,
> with a **Spain-only GraphHopper dump**.

---

## 3. Address parsing / normalization — libpostal

When CARDEEP holds only a free-text Spanish address line
(`"C/ Gran Vía 32, 4º B, 28013 Madrid"`) and no clean `city`/`postcode` fields, something
must split it into components before `GeoResolver.municipality_code(...)` can run.

### 3.1 libpostal + `postal` (pypostal) — **RECOMMENDED** ✅ (revived)

- **Core repo:** https://github.com/openvenues/libpostal — **[VERIFIED]** 4.8k★, **not
  archived**. The headline tagged release is ancient (**v1.1 "Walla Walla", 2018**) and the
  *original* statistical model dates to 2016 — this is what makes people declare it dead.
  **It isn't.**
- **Commit recency [VERIFIED]:** `commits/master` shows active 2025 work — most recent
  **2025-12-06** ("update-senzing-data-v1.2.0"), plus **2025-10-18** version bump 1.1.3→1.1.4
  and a real parser fix (`clear context->separators on each parse`). So: **alive at the
  source level in late 2025.**
- **Data model — the actual story [VERIFIED]:** **Senzing** adopted libpostal and now ships
  a **re-trained, modernized data model**: `Senzing/libpostal-data` **v1.2.0, released
  2025-11-07**, "latest data from all sources," 12,982 test addresses across **88
  countries**. Senzing has publicly committed to a **new model every 6–12 months**. This is
  the thing that was stagnant (2016 model) and is now maintained.
- **Python binding [VERIFIED]:** `postal` on PyPI — **1.1.11, 2025-10-29** (the prior
  release was 1.1.10 in 2022, so the 2025 release is the revival landing in the binding
  too). Python 3 supported. There is also a community **`pypostal-multiarch`** fork
  **[VERIFIED — exists]** offering modern multi-arch wheels (useful where building the C lib
  is painful, e.g. CI/containers).
- **Strengths:** the *only* battle-tested multilingual OSS parser; handles Spanish street
  abbreviations (`C/`, `Avda.`, `P.º`), floor/door suffixes, and `28013`-style postcodes;
  trained on global OSM/OpenAddresses so it generalizes to the EU expansion countries too.
- **Weaknesses:** **heavy install** — it's a C library (≈2GB of model data on disk, GBs of
  RAM to load), not a `pip install`-and-go. On Windows the native build is the classic pain
  point (use WSL/Docker or `pypostal-multiarch` wheels). It **parses**, it does not assign
  codes — the components still flow into `GeoResolver`.
- **Verdict:** ✅ **revived and recommended.** Treat it as a *component extractor* that feeds
  the existing INE resolver. Gate it behind the case "we have a raw address string and no
  clean city/postcode," so the 2GB model only loads when actually needed.

> **No credible successor exists.** There is no 2026 library that replaces libpostal for
> multilingual parsing; the "successor" *is* Senzing's re-trained model inside the same
> project. LLM-based parsing (T07/T08) is an option for the messiest long-tail lines but is
> slower and non-deterministic — keep it as a last-resort fallback, not the default.

---

## 4. Quick liveness ledger (everything I opened)

| Tool | Latest signal | Date | Status | Source |
|---|---|---|---|---|
| Nominatim | release 5.3.2 | 2026-04-10 | ✅ alive | github.com/osm-search/Nominatim/releases |
| Photon | release 1.2.0 | 2026-06-11 | ✅ alive | github.com/komoot/photon |
| Pelias | commits, no umbrella release | 2025/26 | 🟡 alive, heavy | github.com/pelias/pelias |
| libpostal (core) | commit `master` | 2025-12-06 | ✅ alive | github.com/openvenues/libpostal/commits/master |
| Senzing libpostal-data | release v1.2.0 | 2025-11-07 | ✅ alive | github.com/Senzing/libpostal-data |
| `postal` (pypostal) | release 1.1.11 | 2025-10-29 | ✅ alive | pypi.org/project/postal |
| shapely | release 2.1.2 | 2025-09-24 | ✅ alive | pypi.org/project/shapely |
| es-atlas (IGN TopoJSON) | release v0.6.0 | 2024-02-10 | 🟡 alive-ish (data stable) | github.com/martgnz/es-atlas |
| CartoCiudad REST (CNIG) | service update | 2024–2025 | ✅ alive | github.com/IDEESpain/Cartociudad |
| `reverse_geocoder` (thampiman) | wheel | 2025-05-29 | ✅ alive (wrong granularity) | pypi.org/project/reverse_geocoder |

---

## 5. The incumbent, graded honestly — `ProvinceGeocoder`

**Is the numpy nearest-labeled-point classifier good enough for province-level? — Yes,
with two named caveats.**

**Why it works.** Spanish provinces are **large, contiguous** regions. If the nearest
*already-labeled* entity is in province X, the unlabeled POI is almost certainly in X too.
The method:

- is **free and zero-dependency** (numpy only) — no polygons, no service, no data download;
- is **self-improving**: every new labeled entity (DGT scrapyards, OEM dealers with known
  province) densifies the reference set and tightens accuracy automatically;
- uses correct geometry for the scale (`cos(lat)` longitude scaling, squared distance for a
  monotonic nearest-neighbor — no need for true haversine).

**Caveat 1 — border misclassification.** Near a **province border**, the nearest labeled
point can sit on the *wrong side*. The probability of error scales with (border length) /
(local labeled-point density). For province-level reporting this is a **small, bounded
error**, acceptable today. It is **not** acceptable for municipality-level (borders are
everywhere). → that's exactly why §6 exists.

**Caveat 2 — cold/sparse regions.** Where labeled density is low (early in a region's
coverage), "nearest" can be tens of km away and cross a border. Mitigated as coverage grows;
worth a **sanity guard** (reject/flag if nearest labeled point is implausibly far, e.g.
>40 km).

**Performance note.** `nearest_province` is **O(N) per query** (full numpy scan of all
labeled points). At ~13k points it's trivially fast. As the labeled set grows to 100k+ and
queries batch up, swap the linear scan for a **`scipy.spatial.cKDTree`** (build once, query
in O(log N)) — same data, same answer, orders of magnitude faster. This is a drop-in
internal change, not an architectural one.

**Verdict:** **keep it for province-level.** It is the right amount of engineering for a
large-region classifier. Add a far-distance guard and (at scale) a cKDTree index.

---

## 6. The real upgrade — exact municipality via shapely + INE polygons

Municipality assignment from `lat/lon` **cannot** be done reliably by nearest-labeled-point
(municipal borders are dense; nearest-neighbor will straddle them constantly). The correct,
exact, **offline** method is **point-in-polygon** against official municipal boundaries.

### 6.1 The engine — shapely 2.x ✅

- **PyPI:** https://pypi.org/project/shapely — **[VERIFIED]** **2.1.2, 2025-09-24** (2.1.1
  2025-05-19, 2.1.0 2025-04-03). Python ≥3.10, GEOS ≥3.9, NumPy ≥1.21. Production-stable,
  Windows/macOS/Linux wheels.
- **Why shapely 2.x specifically:** it ships a vectorized **`STRtree`** spatial index and
  `shapely.contains`/`contains_xy` array operations. Build the R-tree over ~8,132 municipal
  polygons **once**, then each `lat/lon` lookup is a microsecond-scale index query +
  exact polygon test. No service, no per-call cost, fully offline.

### 6.2 The data — INE-coded municipal polygons

The boundaries must carry **INE codes** so the output maps straight onto `geo_municipality`.
Ranked options:

1. **es-atlas TopoJSON (RECOMMENDED for ingest) — [VERIFIED]**
   - Repo: https://github.com/martgnz/es-atlas — pre-built TopoJSON of Spain
     **municipalities / provinces / regions**, generated from **IGN** shapefiles, **CC-BY 4.0**.
   - **Every feature carries its INE identifier and name** — exactly what we need to join to
     `geo_municipality.code`. Tunable simplification (`1e-4`) and quantization (`1e4`).
   - Status: latest tagged build **v0.6.0, 2024-02-10**. Administrative borders barely move
     year to year, so a 2024 build is operationally current; if absolute freshness is needed,
     regenerate from the live IGN source (below) — the repo *is* the recipe.
2. **IGN / CNIG official source (authoritative, for regeneration) — [VERIFIED]**
   - "Base de Datos de Divisiones Administrativas de España" (BDLJE), published by **CNIG**:
     https://centrodedescargas.cnig.es/CentroDescargas/limites-municipales-provinciales-autonomicos
     (series **LILIM**). Formats: **Shapefile / GML / GeoJSON** via WFS/ATOM.
     WFS: `https://www.ign.es/wfs-inspire/unidades-administrativas`.
   - This is the canonical polygon source; es-atlas is a convenience build on top of it.
3. **mapSpain (R, reference only) — [VERIFIED exists]** — `rOpenSpain/mapSpain`, IGN
   CartoBase SIANE / GISCO. Great provenance but R-native; use as a cross-check, not a
   Python dependency.

### 6.3 Integration sketch (offline, no service)

```python
# pipeline/muni_geocode.py  —  exact INE municipality from lat/lon (point-in-polygon)
from __future__ import annotations
import json
from shapely.geometry import shape, Point
from shapely import STRtree

class MunicipalityGeocoder:
    """Assign the exact INE municipality (code5) to a lat/lon by point-in-polygon
    against IGN municipal boundaries (es-atlas / CNIG, INE-coded). Built once."""

    def __init__(self, geoms: list, codes: list[str]) -> None:
        self._geoms = geoms                 # list[shapely.Polygon/MultiPolygon]
        self._codes = codes                 # parallel list of INE code5
        self._tree = STRtree(geoms)         # vectorized R-tree, built once

    @classmethod
    def from_geojson(cls, path: str) -> "MunicipalityGeocoder":
        with open(path, encoding="utf-8") as fh:
            fc = json.load(fh)
        geoms, codes = [], []
        for feat in fc["features"]:
            # es-atlas/IGN: INE code lives in feature props — confirm the exact key
            # (e.g. "id" / "cod_ine" / "NATCODE") against the file you ingest.
            code5 = str(feat["properties"].get("id") or feat["properties"]["cod_ine"])
            geoms.append(shape(feat["geometry"]))
            codes.append(code5.zfill(5))
        return cls(geoms, codes)

    def municipality_code(self, lat: float | None, lon: float | None) -> str | None:
        if lat is None or lon is None:
            return None
        pt = Point(float(lon), float(lat))         # GeoJSON is (lon, lat)
        for idx in self._tree.query(pt):           # R-tree candidates (bbox prefilter)
            if self._geoms[idx].contains(pt):      # exact polygon test
                return self._codes[idx]
        return None                                # off-grid / offshore -> caller falls back
```

**Pipeline wiring.** In `pipeline/ingest.py`, the resolution order becomes a clean cascade,
each step authoritative, each falling back:

1. **Hard string path (unchanged):** if a clean `city`/`province` exists →
   `GeoResolver.municipality_code(...)` / `resolve_city_global(...)`. Deterministic, free.
2. **Address parse (new, §3):** if only a raw address line → libpostal → components → back
   to step 1.
3. **Polygon path (new, §6):** if `lat/lon` present →
   `MunicipalityGeocoder.municipality_code(lat, lon)` → exact INE `code5`; derive
   `province_code = code5[:2]` for free (the schema already enforces this prefix invariant).
4. **Province fallback (incumbent, §5):** if the point is off-grid or the file lacks a
   polygon → `ProvinceGeocoder.nearest_province(...)` for at least a province-level answer.
5. **Oracle (§7):** unresolved hard cases → CartoCiudad reverse REST.

This makes municipality assignment **exact where we have a coordinate**, keeps the cheap
incumbent as a province-level safety net, and adds **one offline data file + shapely** — no
running geocoding service anywhere.

**Bonus:** the same polygons let you **backfill `geo_municipality.lat/lon`** (currently NULL
in `load_geo.py`) using polygon centroids (`geom.representative_point()`), which improves any
nearest-centroid heuristics downstream.

---

## 7. Spanish-official oracle — CartoCiudad reverse REST (CNIG/IGN)

- **Repo / docs:** https://github.com/IDEESpain/Cartociudad — **[VERIFIED]** EUPL-1.2.
  Base: `https://www.cartociudad.es/geocoder/api/geocoder/`.
  - Forward: `…/candidates` (typeahead) and `…/find`.
  - **Reverse: `…/reverseGeocode`** → returns the **postal address** *and* administrative
    units **community / province / municipality with INE coding** (`provinceCode`,
    `muniCode`). **[VERIFIED]** Service was updated through **2024–2025** (CartoCiudad
    geocoder modernized 2022; candidates method extended 2024–2025).
- **Why it matters:** this is the **authoritative Spanish reverse geocoder that already
  speaks INE** — unlike Nominatim/Photon/Pelias, its output drops straight into our schema
  with no re-resolution. It is the natural **oracle**: use it to (a) resolve the hard tail
  the offline cascade misses, and (b) **audit** the §6 polygon layer (spot-check that our
  point-in-polygon `muniCode` agrees with CartoCiudad's).
- **Why not make it the bulk dependency:** it's an external HTTP service (rate/availability
  not contractually guaranteed in the public docs; no documented SLA). Keep CARDEEP's bulk
  path **offline** (shapely + polygons) and reserve CartoCiudad for the **long tail and
  validation**, which keeps us free, fast, and resilient to the service going down.
- **Postal-code data:** CartoCiudad and the INE dictionary already cover the province/
  municipality grid CARDEEP keys on; a dedicated postcode→municipality table
  (e.g. derived from CartoCiudad or INE) is a *nice-to-have* for the "only a postcode"
  case, not a blocker. The first two digits of a Spanish postcode == province code, which
  already gives a free province-level answer with zero data.

---

## 8. Recommendation, integration notes, sample config

**Adopt, in priority order:**

1. **Keep `ProvinceGeocoder`** for province-level reverse (§5). Add a **far-distance guard**
   (flag if nearest labeled point > ~40 km) and, once labeled points exceed ~100k, swap the
   linear numpy scan for **`scipy.spatial.cKDTree`** (drop-in, same answers).
2. **Add `MunicipalityGeocoder` (shapely 2.x + es-atlas/IGN INE-coded polygons)** for **exact
   municipality** reverse (§6). This is the headline upgrade. One offline GeoJSON/TopoJSON
   file, an `STRtree` built once, microsecond lookups, no service.
3. **Add libpostal (`postal`)** for parsing raw Spanish address lines into components (§3),
   gated to the case where clean `city`/`postcode` are absent so the 2GB model loads lazily.
4. **Wire CartoCiudad `reverseGeocode`** as the **oracle/fallback + polygon-layer auditor**
   (§7) — not the bulk path.
5. **Do NOT** stand up Nominatim/Pelias for this. **Photon** *only* if forward street-level
   search becomes a real requirement (then use a Spain-only GraphHopper dump). **Do NOT**
   adopt `reverse_geocoder` — wrong granularity, no INE codes.

**`requirements.txt` additions (pin minor; consistent with the repo's existing style):**

```text
# Geo / reverse-geocoding (T10)
shapely>=2.1,<2.2          # point-in-polygon municipality assignment (GEOS>=3.9 bundled in wheels)
scipy>=1.13                # cKDTree for ProvinceGeocoder at 100k+ labeled points (optional, scale tier)

# Address parsing (T10) — heavy native lib; install behind a feature flag / in WSL or Docker.
# Requires the libpostal C library + ~2GB model data; not a pure-pip install on Windows.
# postal>=1.1.11           # pypostal binding to libpostal (Senzing data model v1.2.0)
#   Windows note: build libpostal under WSL/Docker, or use community wheels:
#   pypostal-multiarch      # multi-arch prebuilt wheels (alternative to building from source)
```

**Data acquisition (one-time, offline):**

```bash
# Municipal boundary polygons, INE-coded, from the IGN-derived es-atlas build:
#   https://github.com/martgnz/es-atlas   (CC-BY 4.0; features carry INE id + name)
# Or regenerate fresh from the canonical CNIG source (series LILIM):
#   https://centrodedescargas.cnig.es/CentroDescargas/limites-municipales-provinciales-autonomicos
#   WFS: https://www.ign.es/wfs-inspire/unidades-administrativas
# Place under data/geo/ (e.g. data/geo/municipios_ine.geojson) next to diccionario_ine.xlsx.
# Attribution required: "Instituto Geográfico Nacional (IGN)".
```

**CartoCiudad oracle call (validation / long-tail fallback):**

```text
GET https://www.cartociudad.es/geocoder/api/geocoder/reverseGeocode
    ?lon={lon}&lat={lat}&outputformat=geojson
# Response carries postal address + provinceCode + muniCode (INE-coded).
# Use to: resolve the tail the offline cascade misses, and audit MunicipalityGeocoder.
```

**Net effect.** CARDEEP gains **exact, offline, free, INE-keyed municipality precision**
from coordinates, while keeping the proven province-level classifier as a safety net and an
authoritative Spanish oracle for the hard tail — with **no running geocoding service** added
to the stack.

---

## 9. Sources (all [VERIFIED] this session unless noted)

- Nominatim releases — https://github.com/osm-search/Nominatim/releases ; release history https://nominatim.org/release-history/
- Photon — https://github.com/komoot/photon
- Pelias — https://github.com/pelias/pelias ; steward https://geocode.earth/
- libpostal core — https://github.com/openvenues/libpostal ; commits https://github.com/openvenues/libpostal/commits/master
- Senzing libpostal data model — https://github.com/Senzing/libpostal-data ; context https://senzing.com/what-is-libpostal/
- pypostal (`postal`) — https://pypi.org/project/postal/ ; multiarch fork https://github.com/kaiz11/pypostal-multiarch
- shapely — https://pypi.org/project/shapely/
- es-atlas (IGN TopoJSON, INE-coded) — https://github.com/martgnz/es-atlas
- CNIG / IGN administrative divisions (LILIM, BDLJE) — https://centrodedescargas.cnig.es/CentroDescargas/limites-municipales-provinciales-autonomicos ; dataset record https://datos.gob.es/en/catalogo/e00125901-spaignllm ; WFS https://www.ign.es/wfs-inspire/unidades-administrativas
- CartoCiudad REST geocoder — https://github.com/IDEESpain/Cartociudad
- mapSpain (R, reference) — https://github.com/rOpenSpain/mapSpain
- INE municipality dictionary (already in repo) — https://www.ine.es/daco/daco42/codmun/diccionario25.xlsx
- `reverse_geocoder` (thampiman) — https://pypi.org/project/reverse_geocoder/ ; repo https://github.com/thampiman/reverse-geocoder
