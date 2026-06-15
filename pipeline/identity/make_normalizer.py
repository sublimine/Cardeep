"""Canonical make normalizer — data-grounded brand taxonomy (audit P2 A-make-model-null-parse).

Two coupled defects this fixes:
  1. ~400k vehicles have make+model NULL despite a brand-led title (classifieds connectors like
     milanuncios deliberately leave make NULL; the brand sits in the title's leading token).
  2. The make field's casing is inconsistent even when populated (VOLKSWAGEN / Volkswagen,
     MERCEDES-BENZ / Mercedes-Benz / Mercedes all coexist), fragmenting the primary search axis.

The canonical map is grounded in the LIVE data (the top ~70 leading tokens of both-null titles and
the existing make distribution, 2026-06-15), not invented. HIGH PRECISION by design: a value is
normalized/recovered ONLY when it is a KNOWN brand — an unknown make is kept verbatim (never guessed),
and a non-brand leading token (stock/caravana/vendo/…) yields no make. Model is intentionally NOT
parsed here (title→model is too error-prone for a backfill).
"""
from __future__ import annotations

# lowercased token (make value OR title leading token) -> canonical display form.
# Acronym brands keep their official all-caps; the rest are Title-case. Aliases included.
_CANON: dict[str, str] = {
    "mercedes-benz": "Mercedes-Benz", "mercedes": "Mercedes-Benz", "mercedesbenz": "Mercedes-Benz",
    "volkswagen": "Volkswagen", "vw": "Volkswagen",
    "bmw": "BMW", "audi": "Audi", "peugeot": "Peugeot",
    "citroen": "Citroen", "citroën": "Citroen",
    "renault": "Renault", "seat": "SEAT", "ford": "Ford", "opel": "Opel", "toyota": "Toyota",
    "hyundai": "Hyundai", "nissan": "Nissan", "kia": "Kia", "fiat": "Fiat", "mini": "MINI",
    "volvo": "Volvo", "skoda": "Skoda", "škoda": "Skoda", "porsche": "Porsche",
    "land-rover": "Land Rover", "land rover": "Land Rover", "landrover": "Land Rover",
    "dacia": "Dacia", "mazda": "Mazda", "cupra": "CUPRA", "jeep": "Jeep", "honda": "Honda",
    "mitsubishi": "Mitsubishi", "suzuki": "Suzuki", "lexus": "Lexus", "jaguar": "Jaguar",
    "alfa": "Alfa Romeo", "alfa-romeo": "Alfa Romeo", "alfa romeo": "Alfa Romeo", "alfaromeo": "Alfa Romeo",
    "chevrolet": "Chevrolet", "mg": "MG", "ds": "DS", "smart": "smart", "ssangyong": "SsangYong",
    "maserati": "Maserati", "chrysler": "Chrysler", "tesla": "Tesla", "subaru": "Subaru",
    "byd": "BYD", "lynk": "Lynk & Co", "lynk&co": "Lynk & Co", "ferrari": "Ferrari", "abarth": "Abarth",
    "ebro": "EBRO", "lancia": "Lancia", "kgm": "KGM", "dodge": "Dodge", "infiniti": "Infiniti",
    "saab": "Saab", "lamborghini": "Lamborghini", "leapmotor": "Leapmotor", "iveco": "Iveco",
    "bentley": "Bentley", "aston": "Aston Martin", "aston-martin": "Aston Martin", "swm": "SWM",
    "daewoo": "Daewoo", "omoda": "Omoda", "jaecoo": "Jaecoo", "dfsk": "DFSK", "rover": "Rover",
    "cadillac": "Cadillac", "bestune": "Bestune", "alpine": "Alpine", "mahindra": "Mahindra",
    "isuzu": "Isuzu", "rolls-royce": "Rolls-Royce", "mclaren": "McLaren", "polestar": "Polestar",
}


def canonical_make(value: str | None) -> str | None:
    """Canonical display form for a make value if it is a KNOWN brand, else None."""
    if not value:
        return None
    return _CANON.get(value.strip().lower())


def make_from_title(title: str | None) -> str | None:
    """Canonical brand from a title's leading token, or None if it is not a known brand."""
    if not title or not title.strip():
        return None
    return _CANON.get(title.strip().split()[0].lower())


def normalize_make(make: str | None, title: str | None = None) -> str | None:
    """Canonical make for ingest/backfill.

    - Known brand (any casing)  -> its canonical form.
    - Empty/None make           -> recovered from the title's leading brand token (if known).
    - Non-empty unknown brand    -> kept verbatim (NEVER guessed — Law I: under-fill over mis-fill).
    """
    canon = canonical_make(make)
    if canon:
        return canon
    if make and make.strip():
        return make  # unknown brand — preserve, do not guess
    return make_from_title(title)
