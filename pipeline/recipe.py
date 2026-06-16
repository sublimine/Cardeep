"""FASE 3 — RECETA. Persist a versioned, reusable extraction recipe per dealer.

The recipe is the asset that lets Cardeep re-scrape without the raw crude. For
structured sources (AS24 __NEXT_DATA__) the recipe records the source engine,
the field map, and the version. Stored as YAML under countries/ES/.
"""
from __future__ import annotations

import logging
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger(__name__)

AS24_RECIPE = {
    "version": 1,
    "source": "autoscout24",
    "engine": "http+next_data",
    "access": "open (Chrome UA; SSR __NEXT_DATA__)",
    "enumeration": "/profesionales/{slug}?atype=C&page=N until numberOfResults reached",
    "field_map": {
        "deep_link": "listing.url (prefixed with host)",
        "vin_ref": "listing.id",
        "make": "listing.vehicle.make",
        "model": "listing.vehicle.model",
        "year": "listing.tracking.firstRegistration (MM-YYYY -> YYYY)",
        "km": "listing.tracking.mileage",
        "price": "listing.tracking.price",
        "fuel": "listing.vehicle.fuel",
        "transmission": "listing.vehicle.transmission",
        "photo_url": "listing.images[0]",
        "dealer": "listing.seller {id, companyName, links.infoPage->slug}",
        "location": "listing.location {zip->province, city, street}",
    },
}


def write_recipe(cdp_code: str, recipe: dict | None = None) -> Path:
    """Persist recipe.yaml for a dealer under countries/ES/recipes/<cdp_code>.yaml.

    Serialized with the YAML library (NOT a hand-rolled dumper): the old _yaml_dump emitted bare
    `key: value` with no quoting, so any value containing ': ' (e.g. a facet enumeration like
    'FACET partition (depth-cap fix): seller_type') produced UNPARSEABLE YAML — silently corrupting
    the dealer's only durable recipe asset, which then no loader (complete/evict/reshape) could read
    back (green-review Q4). yaml.dump escapes correctly.

    R2: the serialized YAML is round-tripped back here so a serialization defect fails at WRITE time,
    not silently at read time. R3: overwriting an existing recipe with a semantically DIFFERENT one
    is logged (the coches.net _tier1 last-writer-wins clobber was previously silent).
    """
    recipe = recipe or AS24_RECIPE
    if not isinstance(recipe, dict) or not recipe:
        raise ValueError(
            f"write_recipe({cdp_code}): recipe must be a non-empty dict, got {type(recipe).__name__}")

    out_dir = ROOT / "countries" / "ES" / "recipes"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{cdp_code}.yaml"
    header = f"# Cardeep extraction recipe — {cdp_code}\n# Reusable; re-scrape without raw crude.\n"
    body = yaml.dump(recipe, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # R2 — round-trip self-check: the YAML we are about to persist MUST parse back to the recipe.
    if yaml.safe_load(body) != recipe:
        raise ValueError(
            f"write_recipe({cdp_code}): recipe did not round-trip through YAML — refusing to write a "
            f"file no loader could read back")

    # R3 — clobber visibility: a different module writing the SAME cdp_code with a DIFFERENT recipe
    # used to silently last-writer-win. Compare semantically (format-agnostic) and log the clobber.
    if path.exists():
        try:
            old_recipe = yaml.safe_load(path.read_text(encoding="utf-8"))  # ignores the # header
        except Exception:
            old_recipe = None  # old file unparseable (the very bug being fixed) — just overwrite
        if old_recipe is not None and old_recipe != recipe:
            log.warning(
                "write_recipe: %s.yaml already holds a DIFFERENT recipe — overwriting (possible "
                "clobber: two modules writing the same cdp_code)", cdp_code)

    path.write_text(header + body, encoding="utf-8")
    return path
