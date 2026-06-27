"""/geo/* — geographic entity listing and tree/completeness endpoints.

SU-D2 additions:
  - /geo/completeness: RATE_EXPENSIVE + cached (runs 7 sequential COUNT(*) queries
    over full entity + vehicle tables; changes only between harvests).
  - /geo/{province}/tree: RATE_EXPENSIVE + cached (GROUP BY over 50k+ entity rows
    per province; expensive and stable within a harvest window).
  - /geo/{province}/entities: RATE_DEFAULT + cached (paginated; stable between
    harvests — status/kind filters are enforced at DB write time).
  - /geo/{province}/municipalities/{muni}/entities: RATE_DEFAULT + cached (same
    stability contract as province listing, scoped to municipality).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, page_slice, require_api_key
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter

router = APIRouter()


# ---------------------------------------------------------------------------
# Static-path routes FIRST — must precede any /geo/{province_code}/... routes
# so FastAPI does not swallow "completeness" as a province_code value.
# ---------------------------------------------------------------------------

@router.get("/geo/completeness")
@limiter.limit(RATE_EXPENSIVE)
async def geo_completeness(
    request: Request,
    country: str = Query(default="ES", description="ISO-3166 alpha-2 tenant (default ES)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """National geo-completeness report for one tenant.

    Every count is scoped by ``country_code = $1`` (``country`` query param, default 'ES') so the
    coverage report belongs to ONE country, never a country-blind sum. With the default it is
    byte-identical to the historical report (today entity non-ES = 0).

    SU-D2: cached (sequential COUNT(*) queries; stable between harvests).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        # Geo-completeness is a DEALER coverage report: particulares are platform-attributed
        # C2C inventory, not geo-located points of sale (and mostly lack geo by nature — the
        # SU-A6 gap). Scoping to kind<>'particular' makes full_pct reflect real dealer coverage,
        # consistent with /geo/{prov}/entities and /geo/{prov}/tree.
        e_total = await c.fetchval(
            "SELECT count(*) FROM entity WHERE kind <> 'particular' AND country_code = $1", country)
        e_full = await c.fetchval(
            "SELECT count(*) FROM entity WHERE kind <> 'particular' AND province_code IS NOT NULL "
            "AND municipality_code IS NOT NULL AND comarca_id IS NOT NULL AND country_code = $1", country)
        e_no_comarca_city = await c.fetchval(
            "SELECT count(*) FROM entity WHERE kind <> 'particular' "
            "AND municipality_code IS NOT NULL AND comarca_id IS NULL AND country_code = $1", country)
        e_prov_only = await c.fetchval(
            "SELECT count(*) FROM entity WHERE kind <> 'particular' "
            "AND province_code IS NOT NULL AND municipality_code IS NULL AND country_code = $1", country)
        e_no_geo = await c.fetchval(
            "SELECT count(*) FROM entity WHERE kind <> 'particular' AND province_code IS NULL "
            "AND country_code = $1", country)
        v_total = await c.fetchval(
            "SELECT count(*) FROM vehicle v JOIN entity e ON e.entity_ulid=v.entity_ulid "
            "WHERE e.country_code = $1", country)
        v_full = await c.fetchval(
            "SELECT count(*) FROM vehicle v JOIN entity e ON e.entity_ulid=v.entity_ulid "
            "WHERE e.province_code IS NOT NULL AND e.municipality_code IS NOT NULL "
            "AND e.comarca_id IS NOT NULL AND e.country_code = $1", country)
        geo = {
            "provinces": await c.fetchval(
                "SELECT count(*) FROM geo_province WHERE country_code = $1", country),
            "comarcas": await c.fetchval(
                "SELECT count(*) FROM geo_comarca WHERE country_code = $1", country),
            "municipalities": await c.fetchval(
                "SELECT count(*) FROM geo_municipality WHERE country_code = $1", country),
            "municipalities_with_comarca": await c.fetchval(
                "SELECT count(*) FROM geo_municipality WHERE comarca_id IS NOT NULL "
                "AND country_code = $1", country),
        }
        response = ok({
            "geo_grid": geo,
            "entities": {
                "scope": "dealers (kind<>particular)",
                "total": e_total, "full_prov_comarca_muni": e_full,
                "municipality_no_comarca_ceuta_melilla": e_no_comarca_city,
                "province_only": e_prov_only, "no_geo": e_no_geo,
                "full_pct": round(100 * e_full / e_total, 2) if e_total else 0,
            },
            "vehicles": {
                "total": v_total, "full_prov_comarca_muni": v_full,
                "full_pct": round(100 * v_full / v_total, 2) if v_total else 0,
            },
        })
    return cache_set(request, response)


@router.get("/geo/seal")
@limiter.limit(RATE_EXPENSIVE)
async def geo_seal(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Per-province SU-SEAL, by segment. VENTA = served CANONICAL dealers vs the DIRCE CNAE-451
    registral ceiling (SELLADO >=85% / PARCIAL 50-85% / GAP <50%). DESGUACE = discovery coverage:
    scrapyards found vs the DGT official census (SELLADO when found >= census). Backed by the live
    view v_province_seal (migrations 0042+0043) so it always reflects the current harvest. Cached +
    EXPENSIVE (GROUP BY over entities + dedup join; stable between harvests)."""
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    _METHODS = {
        "venta": "served_canonical / DIRCE-451 registral_ceiling (SELLADO>=85%)",
        "desguace": "found / DGT census (discovery; SELLADO when found>=census)",
    }
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            "SELECT province_code, segment, denominator, numerator, coverage_pct, verdict "
            "FROM v_province_seal ORDER BY segment, province_code")

    segments: dict[str, dict[str, Any]] = {}
    for r in rows:
        seg = segments.setdefault(r["segment"], {
            "method": _METHODS.get(r["segment"], ""),
            "national": {"numerator": 0, "denominator": 0},
            "distribution": {},
            "provinces": [],
        })
        den = int(r["denominator"]) if r["denominator"] is not None else None
        num = int(r["numerator"])
        seg["provinces"].append({
            "province_code": r["province_code"],
            "denominator": den,
            "numerator": num,
            "coverage_pct": float(r["coverage_pct"]) if r["coverage_pct"] is not None else None,
            "verdict": r["verdict"],
        })
        seg["national"]["numerator"] += num
        if den:
            seg["national"]["denominator"] += den
        seg["distribution"][r["verdict"]] = seg["distribution"].get(r["verdict"], 0) + 1

    for seg in segments.values():
        nat = seg["national"]
        nat["coverage_pct"] = round(100 * nat["numerator"] / nat["denominator"], 1) \
            if nat["denominator"] else 0

    response = ok({"segments": segments})
    return cache_set(request, response)


@router.get("/geo/exhaustiveness")
@limiter.limit(RATE_EXPENSIVE)
async def geo_exhaustiveness(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """National coverage CERTIFICATE — capture-recapture / MSE (Multi-Source Estimation).

    Distinct from /geo/seal (registral DIRCE ceiling): this serves the live view
    v_exhaustiveness_seal — the STATISTICAL lower bound on completeness from k orthogonal
    discovery lists (Chapman / stratified-sum). The grand-national row (segment AND
    province NULL) is the headline certificate: coverage_lower with CI, method, confidence,
    sealed flag, and build_run_id (re-executable provenance). Honest by construction — a
    thin stratum reports coverage_lower near 0 and sealed=false, never a fabricated 100%.
    Cached + EXPENSIVE; stable within a build. Authed (coverage scale is a competitive signal).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            "SELECT province_code, segment, k_lists, n_obs, n_hat, ci_low, ci_high, "
            "coverage_point, coverage_lower, method, confidence, seal_threshold, sealed, "
            "build_run_id, created_at FROM v_exhaustiveness_seal "
            "ORDER BY segment NULLS FIRST, province_code NULLS FIRST")

    def _cert(r: Any) -> dict[str, Any]:
        def _f(key: str, nd: int) -> float | None:
            return round(float(r[key]), nd) if r[key] is not None else None
        return {
            "k_lists": r["k_lists"],
            "n_obs": r["n_obs"],
            "n_hat": _f("n_hat", 1),
            "ci_low": _f("ci_low", 1),
            "ci_high": _f("ci_high", 1),
            "coverage_point": _f("coverage_point", 4),
            "coverage_lower": _f("coverage_lower", 4),
            "method": r["method"],
            "confidence": r["confidence"],
            "seal_threshold": _f("seal_threshold", 4),
            "sealed": r["sealed"],
        }

    national: dict[str, Any] | None = None
    build_run_id: str | None = None
    generated_at: str | None = None
    by_segment: dict[str, dict[str, Any]] = {}

    for r in rows:
        build_run_id = build_run_id or r["build_run_id"]
        if generated_at is None and r["created_at"] is not None:
            generated_at = r["created_at"].isoformat()
        seg, prov = r["segment"], r["province_code"]
        if seg is None:
            if prov is None:
                national = _cert(r)            # grand-national headline certificate
            continue                           # (no segmentless province rows today; defensive)
        bucket = by_segment.setdefault(seg, {"national": None, "provinces": []})
        if prov is None:
            bucket["national"] = _cert(r)
        else:
            entry = _cert(r)
            entry["province_code"] = prov
            bucket["provinces"].append(entry)

    response = ok({
        "certificate": "national_exhaustiveness_mse",
        "method": "capture-recapture / MSE (k orthogonal discovery lists)",
        "build_run_id": build_run_id,
        "generated_at": generated_at,
        "national": national,
        "by_segment": by_segment,
    })
    return cache_set(request, response)


# ---------------------------------------------------------------------------
# GAP 1 fix: /geo/{province}/entities filters active non-particular
# GAP 3 new: /geo/{province}/municipalities/{muni}/entities
# ---------------------------------------------------------------------------

@router.get("/geo/{province_code}/entities")
@limiter.limit(RATE_DEFAULT)
async def entities_by_province(
    province_code: str,
    request: Request,
    country: str = Query(default="ES", description="ISO-3166 alpha-2 tenant (default ES)"),
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """List active non-particular entities for a province within one tenant.

    GAP-1 fix: adds WHERE status='active' AND kind <> 'particular'.
    Excludes C2C sellers and unverified entities — only trade point-of-sale
    dealers are returned.

    Country-scope (vector #5): WHERE se.country_code = $2 (``country`` query param,
    default 'ES') so a province query for one tenant never serves a same-numbered
    province in another (DE '28' coexists with ES Madrid '28' — migration 0053).

    Pagination (B3.1): accepts ``page``/``size``.

    SU-D2: cached (entity status/kind filtered at write time; stable between
    harvests).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        # AUDIT 2026-06-16 fix (F-A): collapse alias entities to their VAM-resolved canonical so the
        # list shows ONE row per real dealer (was serving raw servable_entity rows → "11Eleven x3",
        # "QUADIS Autolica x520"). cdp_code returned is the canonical; the dealer page resolves the
        # full cluster. See docs/DATA_INTEGRITY_AUDIT_2026-06-16.md.
        rows = await c.fetch(
            """
            SELECT * FROM (
                SELECT DISTINCT ON (vdr.resolved_cdp_code)
                       vdr.resolved_cdp_code AS cdp_code,
                       se.kind, se.trade_name, se.legal_name, se.municipality_code,
                       se.is_tier1, se.status
                  FROM servable_entity se
                  JOIN v_dealer_resolved vdr ON vdr.entity_ulid = se.entity_ulid
                 WHERE se.province_code = $1
                   AND se.country_code = $2
                   AND se.status = 'active'
                   AND se.kind <> 'particular'
                 ORDER BY vdr.resolved_cdp_code, se.trade_name NULLS LAST, se.cdp_code
            ) q
            ORDER BY q.trade_name NULLS LAST, q.cdp_code
            LIMIT $3 OFFSET $4
            """,
            province_code,
            country,
            size + 1,
            offset,
        )
        rows, has_more = page_slice(rows, size)
        response = ok(
            [dict(r) for r in rows],
            page=page,
            size=size,
            returned=len(rows),
            has_more=has_more,
            province=province_code,
            country=country,
        )
    return cache_set(request, response)


@router.get("/geo/{province_code}/municipalities/{muni_code}/entities")
@limiter.limit(RATE_DEFAULT)
async def entities_by_municipality(
    province_code: str,
    muni_code: str,
    request: Request,
    country: str = Query(default="ES", description="ISO-3166 alpha-2 tenant (default ES)"),
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-3: List active non-particular dealers in a specific municipality of one tenant.

    Scopes to province_code + municipality_code so callers can drill
    country → province → municipality without fetching the full province dump.
    Applies the same active/non-particular filter as /geo/{province}/entities.

    Country-scope (vector #5): WHERE country_code = $3 (``country`` query param,
    default 'ES') — a municipality_code is only unique within a tenant (0053).

    Pagination (B3.1): accepts ``page``/``size``.

    SU-D2: cached (same stability contract as province listing, scoped to muni).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT cdp_code, kind, trade_name, legal_name, municipality_code,
                   is_tier1, status
              FROM servable_entity
             WHERE province_code = $1
               AND municipality_code = $2
               AND country_code = $3
               AND status = 'active'
               AND kind <> 'particular'
             ORDER BY trade_name, cdp_code
             LIMIT $4 OFFSET $5
            """,
            province_code,
            muni_code,
            country,
            size + 1,
            offset,
        )
        rows, has_more = page_slice(rows, size)
        response = ok(
            [dict(r) for r in rows],
            page=page,
            size=size,
            returned=len(rows),
            has_more=has_more,
            province=province_code,
            municipality=muni_code,
            country=country,
        )
    return cache_set(request, response)


# ---------------------------------------------------------------------------
# Existing geo endpoints (unchanged logic)
# ---------------------------------------------------------------------------

@router.get("/geo/{province_code}/tree")
@limiter.limit(RATE_EXPENSIVE)
async def province_inventory_tree(
    province_code: str,
    request: Request,
    country: str = Query(default="ES", description="ISO-3166 alpha-2 tenant (default ES)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Province inventory grouped pais -> PROVINCIA -> COMARCA -> ciudad, for one tenant.

    Country-scope (vector #5): every read is scoped by ``country_code = $2`` (``country``
    query param, default 'ES'). The geo_municipality join is matched on BOTH code AND
    country_code (the geo PK is composite since 0053) so the tree never folds a same-numbered
    foreign municipality into a Spanish province.

    SU-D2: cached (GROUP BY over 50k+ entity rows; stable within a harvest
    window; tree structure changes only when new dealers are ingested).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        prov = await c.fetchrow(
            "SELECT code, name, ccaa_code, ccaa_name FROM geo_province "
            "WHERE code=$1 AND country_code=$2",
            province_code, country)
        if prov is None:
            return err(f"province {province_code} not found")
        rows = await c.fetch(
            """SELECT co.id AS comarca_id, co.name AS comarca, co.ine_code,
                      m.code AS municipality_code, m.name AS municipality,
                      count(e.entity_ulid) AS entities,
                      count(*) FILTER (WHERE e.kind='compraventa')          AS compraventa,
                      count(*) FILTER (WHERE e.kind='concesionario_oficial') AS oficial,
                      count(*) FILTER (WHERE e.kind='desguace')             AS desguace,
                      count(*) FILTER (WHERE e.kind='plataforma')           AS plataforma,
                      count(*) FILTER (WHERE e.kind='garaje')               AS garaje,
                      count(*) FILTER (WHERE e.kind='subasta')              AS subasta,
                      count(*) FILTER (WHERE e.kind='oem_vo_portal')        AS oem_vo_portal,
                      count(*) FILTER (WHERE e.kind='importador')           AS importador,
                      count(*) FILTER (WHERE e.kind='rent_a_car_vo')        AS rent_a_car_vo
                 FROM servable_entity e
                 JOIN geo_municipality m ON m.code = e.municipality_code
                                        AND m.country_code = e.country_code
                 JOIN geo_comarca      co ON co.id = m.comarca_id
                WHERE e.province_code = $1 AND e.country_code = $2 AND e.comarca_id IS NOT NULL
                  AND e.kind <> 'particular'
                GROUP BY co.id, co.name, co.ine_code, m.code, m.name
                HAVING count(e.entity_ulid) > 0
                ORDER BY co.ine_code, entities DESC, m.name""",
            province_code, country)
        comarcas: dict[int, dict[str, Any]] = {}
        prov_total = 0
        for r in rows:
            node = comarcas.setdefault(r["comarca_id"], {
                "comarca_id": r["comarca_id"], "ine_code": r["ine_code"],
                "name": r["comarca"], "entities": 0, "municipalities": []})
            node["entities"] += r["entities"]
            prov_total += r["entities"]
            node["municipalities"].append({
                "municipality_code": r["municipality_code"], "name": r["municipality"],
                "entities": r["entities"], "compraventa": r["compraventa"],
                "oficial": r["oficial"], "desguace": r["desguace"],
                "plataforma": r["plataforma"], "garaje": r["garaje"],
                "subasta": r["subasta"], "oem_vo_portal": r["oem_vo_portal"],
                "importador": r["importador"], "rent_a_car_vo": r["rent_a_car_vo"]})
        # Audit P2 E-geo-tree: scope to active non-particular dealers, matching the rest of this
        # response (e.kind<>'particular' at :242) and /geo/{province}/entities — otherwise this
        # summary count silently included C2C particulares + unverified rows the tree excludes.
        province_only = await c.fetchval(
            "SELECT count(*) FROM servable_entity WHERE province_code=$1 AND municipality_code IS NULL "
            "AND kind <> 'particular' AND status = 'active' AND country_code=$2",
            province_code, country)
        tree = {
            "province": {"code": prov["code"], "name": prov["name"],
                         "ccaa_code": prov["ccaa_code"], "ccaa_name": prov["ccaa_name"]},
            "comarcas": list(comarcas.values()),
            "entities_geo_clean": prov_total,
            "entities_province_only_no_municipality": province_only,
        }
        response = ok(tree, comarca_count=len(comarcas), province=province_code, country=country)
    return cache_set(request, response)
