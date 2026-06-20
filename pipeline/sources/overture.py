"""VECTOR 2 — Geo-grid census: Overture Maps places (the free, OSM-orthogonal layer).

Overture's `places` theme is built from Google/Meta/Apple/TomTom/Microsoft feeds and
published as GeoParquet on a public S3 bucket under CC BY 4.0 — a capture mechanism
deliberately *orthogonal* to OSM (different contributors), which is exactly what the
exhaustiveness framework (§2) needs to lift the overlap `m` and tighten the estimate.

Coste cero: no key, no account. Queried in-process with DuckDB over the anonymous
public bucket (httpfs + spatial), filtered to Spain's bbox and the automotive primary
categories, with a hive-partition pushdown on `bbox` so we never download the planet.

Geo-grid note: Overture is already a global merged POI set, so a quadtree sweep is
unnecessary here — one bbox-filtered scan returns every Spanish automotive POI. The
adaptive-quadtree machinery in the plan is for the *capped* Google Places layer (paid,
60-results/cell), which is isolated below pending a key.

Recipe-first: set CARDEEP_OVERTURE_LIMIT to sample a handful for verify-then-delete;
unset for the full national census. If the public bucket is unreachable (offline runs)
or DuckDB lacks network, the adapter isolates cleanly (declared=None, fetch=[]) so the
orchestrator keeps going with the other vectors.
"""
from __future__ import annotations

import os
import re

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

# Anonymous S3 ListBucket over HTTPS — public bucket, no creds. Used to discover the newest
# release tag so the adapter never breaks when Overture ships a new dated release.
_LIST_URL = "https://overturemaps-us-west-2.s3.us-west-2.amazonaws.com/"

# Spain bounding box incl. Canarias, Ceuta y Melilla. Over-capture (S Portugal, S France)
# is harmless: those POIs carry no Spanish postcode/region and are dropped at INE geo-resolution.
_BBOX = {"xmin": -18.3, "xmax": 4.6, "ymin": 27.5, "ymax": 44.0}

# Overture `categories.primary` strings that denote an automotive point of sale/service.
# Kept explicit (not a LIKE) so the census is auditable and the VAM count is reproducible.
_AUTOMOTIVE_CATEGORIES = (
    "car_dealer",
    "car_dealership",
    "used_car_dealer",
    "automotive_repair_shop",
    "auto_repair",
    "automotive_parts_and_accessories",
    "auto_parts_and_supplies",
    "motorcycle_dealer",
    "truck_dealer",
    "car_wash_and_detail",
)

# Map Overture category -> cardeep kind. Anything automotive but not clearly sales -> garaje.
_KIND = {
    "car_dealer": "compraventa",
    "car_dealership": "compraventa",
    "used_car_dealer": "compraventa",
    "motorcycle_dealer": "compraventa",
    "truck_dealer": "compraventa",
}

# Fallback releases (verified present 2026-06) if the live S3 listing is unreachable. The
# adapter prefers the newest tag discovered from the bucket; these are the safety net.
_CANDIDATE_RELEASES = (
    "2026-06-17.0",
    "2026-05-20.0",
)

_BUCKET = "s3://overturemaps-us-west-2/release"


def _list_releases() -> list[str]:
    """Newest-first list of release tags from the public bucket (anonymous ListBucket)."""
    try:
        import requests

        r = requests.get(
            _LIST_URL,
            params={"list-type": "2", "prefix": "release/", "delimiter": "/"},
            timeout=30,
        )
        tags = re.findall(r"<Prefix>release/([^/<]+)/</Prefix>", r.text)
        return sorted(tags, reverse=True)
    except Exception:  # noqa: BLE001 — offline/listing blocked: caller falls back
        return []


def _duckdb_conn():
    import duckdb  # lazy: missing duckdb -> caught by caller -> isolate

    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET s3_region='us-west-2';")
    # Remote parquet metadata over HTTP is the bottleneck; give it room and cache footers.
    http_timeout = os.environ.get("CARDEEP_OVERTURE_HTTP_TIMEOUT", "300000")
    try:
        con.execute(f"SET http_timeout={int(http_timeout)}; SET http_retries=3; "
                    "SET enable_http_metadata_cache=true;")
    except Exception:  # noqa: BLE001 — older duckdb naming: best-effort tuning
        pass
    # The Overture bucket is public; anonymous (unsigned) access avoids needing credentials.
    try:
        con.execute("SET s3_access_key_id=''; SET s3_secret_access_key='';")
    except Exception:  # noqa: BLE001 — older duckdb: anonymous is the default, ignore
        pass
    return con


def _places_path(release: str) -> str:
    return f"{_BUCKET}/{release}/theme=places/type=place/*"


def _categories_sql() -> str:
    cats = ",".join("'" + c.replace("'", "''") + "'" for c in _AUTOMOTIVE_CATEGORIES)
    return cats


class OvertureAdapter(SourceAdapter):
    """V2 — Overture Maps automotive POIs across Spain (free, OSM-orthogonal)."""

    source_key = "overture"

    def __init__(self) -> None:
        self._rows: list[dict] | None = None
        self._declared: int | None = None
        self._release: str | None = None
        self._isolated: str | None = None  # reason, if the vector self-isolated

    def _resolve_release(self, con) -> str | None:
        env = os.environ.get("CARDEEP_OVERTURE_RELEASE")
        if env:
            return env
        # Prefer the live bucket listing (newest tag), then the verified fallbacks. We probe
        # each with a 1-row read so a half-published release is skipped, not silently used.
        candidates = _list_releases() or list(_CANDIDATE_RELEASES)
        for rel in candidates:
            try:
                con.execute(
                    f"SELECT 1 FROM read_parquet('{_places_path(rel)}', hive_partitioning=1) LIMIT 1"
                ).fetchone()
                return rel
            except Exception:  # noqa: BLE001 — release absent/unreachable: try the next
                continue
        return None

    def _load(self) -> list[dict]:
        if self._rows is not None:
            return self._rows
        if self._isolated:
            return []
        try:
            con = _duckdb_conn()
        except Exception as e:  # noqa: BLE001
            self._isolated = f"duckdb unavailable: {e!r}"
            self._rows = []
            return self._rows
        rel = self._resolve_release(con)
        if not rel:
            self._isolated = ("no reachable Overture release (offline or bucket moved); "
                              "set CARDEEP_OVERTURE_RELEASE to pin one")
            self._rows = []
            return self._rows
        self._release = rel
        limit = os.environ.get("CARDEEP_OVERTURE_LIMIT")
        limit_sql = f" LIMIT {int(limit)}" if limit else ""
        cats = _categories_sql()
        where = (
            f"bbox.xmin BETWEEN {_BBOX['xmin']} AND {_BBOX['xmax']} "
            f"AND bbox.ymin BETWEEN {_BBOX['ymin']} AND {_BBOX['ymax']} "
            f"AND categories.primary IN ({cats})"
        )
        path = _places_path(rel)
        try:
            cur = con.execute(
                f"""
                SELECT
                    id,
                    names.primary AS name,
                    categories.primary AS category,
                    ST_X(geometry) AS lon,
                    ST_Y(geometry) AS lat,
                    addresses[1].freeform AS street,
                    addresses[1].locality AS locality,
                    addresses[1].postcode AS postcode,
                    addresses[1].region AS region,
                    addresses[1].country AS country,
                    phones[1] AS phone,
                    websites[1] AS website,
                    emails[1] AS email
                FROM read_parquet('{path}', hive_partitioning=1)
                WHERE {where}{limit_sql}
                """
            )
            cols = [d[0] for d in cur.description]
            self._rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            # No independent count oracle for Overture, and a global COUNT(*) re-scans the
            # planet. On a full run the filtered scan IS the census, so declared == rows;
            # on a sampled run (LIMIT) there is no honest declared -> None.
            self._declared = None if limit_sql else len(self._rows)
        except Exception as e:  # noqa: BLE001
            self._isolated = f"Overture query failed on release {rel}: {e!r}"
            self._rows = []
        finally:
            con.close()
        return self._rows

    def declared_count(self) -> int | None:
        self._load()
        return self._declared

    def fetch(self) -> list[DiscoveredEntity]:
        rows = self._load()
        if self._isolated:
            print(f"[overture] ISOLATED — {self._isolated}")
            return []
        print(f"[overture] release={self._release} rows={len(rows)}")
        out: list[DiscoveredEntity] = []
        for r in rows:
            name = (r.get("name") or "").strip()
            if not name:
                continue
            country = (r.get("country") or "").upper()
            if country and country != "ES":
                continue  # over-capture from the bbox: keep only Spain
            postcode = r.get("postcode")
            province = None
            if postcode and str(postcode)[:2].isdigit():
                province = str(postcode)[:2]
            cat = r.get("category") or ""
            out.append(DiscoveredEntity(
                kind=_KIND.get(cat, "garaje"),
                source_key=self.source_key,
                source_ref=str(r.get("id")),
                legal_name=name,
                trade_name=name,
                province_name=province or (r.get("region") or None),
                municipality_name=r.get("locality"),
                address=r.get("street"),
                postcode=str(postcode) if postcode else None,
                lat=r.get("lat"),
                lon=r.get("lon"),
                phone=r.get("phone"),
                email=r.get("email"),
                website=r.get("website"),
                extra={"overture_category": cat, "vector": 2,
                       "overture_release": self._release},
            ))
        return out
