"""FASE 3 — RECETA. Persist a versioned, reusable extraction recipe per dealer.

The recipe is the asset that lets Cardeep re-scrape without the raw crude. For
structured sources (AS24 __NEXT_DATA__) the recipe records the source engine,
the field map, and the version. Stored as YAML under countries/ES/.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

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


def _yaml_dump(obj, indent=0) -> str:
    pad = "  " * indent
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.append(_yaml_dump(v, indent + 1))
            else:
                lines.append(f"{pad}{k}: {v}")
    elif isinstance(obj, list):
        for v in obj:
            lines.append(f"{pad}- {v}")
    else:
        lines.append(f"{pad}{obj}")
    return "\n".join(lines)


def write_recipe(cdp_code: str, recipe: dict = None) -> Path:
    """Persist recipe.yaml for a dealer under countries/ES/recipes/<cdp_code>.yaml."""
    recipe = recipe or AS24_RECIPE
    out_dir = ROOT / "countries" / "ES" / "recipes"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{cdp_code}.yaml"
    header = f"# Cardeep extraction recipe — {cdp_code}\n# Reusable; re-scrape without raw crude.\n"
    path.write_text(header + _yaml_dump(recipe) + "\n", encoding="utf-8")
    return path
