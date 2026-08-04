"""Seed make_canon and derive make_alias from the live census (plan Bloque 0.1).

Three things happen here, in order:

  1. make_canon is loaded from the curated registry below. Every entry is a real
     marque; nothing is inferred. `vehicle_class` is what makes the picker honest —
     the census contains motorhomes (Benimar, Hymer, Adria), motorcycles (Yamaha,
     Ducati, Vespa) and trucks (MAN, Scania, DAF) alongside cars, and a *car* brand
     picker that lists them is wrong even though the rows are real. Those marques
     stay resolvable (a search for them still works) but are not listable.

  2. make_alias is DERIVED from the census, not typed. Every distinct spelling in
     `vehicle.make` is normalised with make_norm() and joined onto the registry's
     norm_key. This is the step that catches 'Mercedes Benz', 'MERCEDES_BENZ',
     'mercedes benz ' and 'lynk &amp; co' without anyone having enumerated them.

  3. Model-as-make spellings are mapped explicitly. A row whose make reads 'GOLF'
     (431 of them) is a Volkswagen Golf: the alias records both the marque and the
     model the value actually named, so the row can be repaired rather than dropped.

Spellings that resolve to nothing are REPORTED, never guessed — an unrecognised
marque is left for a human, which is the whole point of curating a registry instead
of pattern-matching at query time.

Run:  python scripts/seed_make_canon.py            # dry-run
      python scripts/seed_make_canon.py --apply     # write
"""
from __future__ import annotations

import asyncio
import sys

import asyncpg

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# (slug, display_name, country, legal_group, vehicle_class, status, successor_slug)
# Ordered by group so the curation is auditable by eye. `status='rebranded'` carries
# a successor so a search for the old name still lands on live stock.
MARQUES: list[tuple[str, str, str | None, str | None, str, str, str | None]] = [
    # ── Stellantis ────────────────────────────────────────────────────────────
    ("peugeot",        "Peugeot",         "FR", "Stellantis", "car", "active", None),
    ("citroen",        "Citroën",         "FR", "Stellantis", "car", "active", None),
    ("ds",             "DS Automobiles",  "FR", "Stellantis", "car", "active", None),
    ("opel",           "Opel",            "DE", "Stellantis", "car", "active", None),
    ("vauxhall",       "Vauxhall",        "GB", "Stellantis", "car", "active", None),
    ("fiat",           "Fiat",            "IT", "Stellantis", "car", "active", None),
    ("abarth",         "Abarth",          "IT", "Stellantis", "car", "active", None),
    ("alfa-romeo",     "Alfa Romeo",      "IT", "Stellantis", "car", "active", None),
    ("lancia",         "Lancia",          "IT", "Stellantis", "car", "active", None),
    ("maserati",       "Maserati",        "IT", "Stellantis", "car", "active", None),
    ("jeep",           "Jeep",            "US", "Stellantis", "car", "active", None),
    ("chrysler",       "Chrysler",        "US", "Stellantis", "car", "active", None),
    ("dodge",          "Dodge",           "US", "Stellantis", "car", "active", None),
    ("ram",            "RAM",             "US", "Stellantis", "van", "active", None),
    # ── Volkswagen Group ──────────────────────────────────────────────────────
    ("volkswagen",     "Volkswagen",      "DE", "Volkswagen AG", "car", "active", None),
    ("audi",           "Audi",            "DE", "Volkswagen AG", "car", "active", None),
    ("seat",           "SEAT",            "ES", "Volkswagen AG", "car", "active", None),
    ("cupra",          "CUPRA",           "ES", "Volkswagen AG", "car", "active", None),
    ("skoda",          "Škoda",           "CZ", "Volkswagen AG", "car", "active", None),
    ("porsche",        "Porsche",         "DE", "Volkswagen AG", "car", "active", None),
    ("bentley",        "Bentley",         "GB", "Volkswagen AG", "car", "active", None),
    ("lamborghini",    "Lamborghini",     "IT", "Volkswagen AG", "car", "active", None),
    ("bugatti",        "Bugatti",         "FR", "Bugatti Rimac", "car", "active", None),
    # ── BMW Group ─────────────────────────────────────────────────────────────
    ("bmw",            "BMW",             "DE", "BMW Group", "car", "active", None),
    ("mini",           "MINI",            "GB", "BMW Group", "car", "active", None),
    ("rolls-royce",    "Rolls-Royce",     "GB", "BMW Group", "car", "active", None),
    # ── Mercedes-Benz Group ───────────────────────────────────────────────────
    ("mercedes-benz",  "Mercedes-Benz",   "DE", "Mercedes-Benz Group", "car", "active", None),
    ("mercedes-amg",   "Mercedes-AMG",    "DE", "Mercedes-Benz Group", "car", "active", None),
    ("maybach",        "Maybach",         "DE", "Mercedes-Benz Group", "car", "active", None),
    ("smart",          "smart",           "DE", "Mercedes-Benz Group", "car", "active", None),
    # ── Geely ─────────────────────────────────────────────────────────────────
    ("volvo",          "Volvo",           "SE", "Geely", "car", "active", None),
    ("polestar",       "Polestar",        "SE", "Geely", "car", "active", None),
    ("lynk-co",        "Lynk & Co",       "CN", "Geely", "car", "active", None),
    ("lotus",          "Lotus",           "GB", "Geely", "car", "active", None),
    ("zeekr",          "Zeekr",           "CN", "Geely", "car", "active", None),
    ("livan",          "Livan",           "CN", "Geely", "car", "active", None),
    # ── Renault ───────────────────────────────────────────────────────────────
    ("renault",        "Renault",         "FR", "Renault Group", "car", "active", None),
    ("dacia",          "Dacia",           "RO", "Renault Group", "car", "active", None),
    ("alpine",         "Alpine",          "FR", "Renault Group", "car", "active", None),
    # ── Japan ─────────────────────────────────────────────────────────────────
    ("toyota",         "Toyota",          "JP", "Toyota", "car", "active", None),
    ("lexus",          "Lexus",           "JP", "Toyota", "car", "active", None),
    ("daihatsu",       "Daihatsu",        "JP", "Toyota", "car", "active", None),
    ("honda",          "Honda",           "JP", "Honda", "car", "active", None),
    ("nissan",         "Nissan",          "JP", "Nissan", "car", "active", None),
    ("infiniti",       "Infiniti",        "JP", "Nissan", "car", "active", None),
    ("mazda",          "Mazda",           "JP", "Mazda", "car", "active", None),
    ("mitsubishi",     "Mitsubishi",      "JP", "Mitsubishi", "car", "active", None),
    ("subaru",         "Subaru",          "JP", "Subaru", "car", "active", None),
    ("suzuki",         "Suzuki",          "JP", "Suzuki", "car", "active", None),
    ("isuzu",          "Isuzu",           "JP", "Isuzu", "van", "active", None),
    # ── Korea ─────────────────────────────────────────────────────────────────
    ("hyundai",        "Hyundai",         "KR", "Hyundai Motor Group", "car", "active", None),
    ("kia",            "Kia",             "KR", "Hyundai Motor Group", "car", "active", None),
    ("genesis",        "Genesis",         "KR", "Hyundai Motor Group", "car", "active", None),
    ("kgm",            "KGM",             "KR", "KG Mobility", "car", "active", None),
    ("ssangyong",      "SsangYong",       "KR", "KG Mobility", "car", "rebranded", "kgm"),
    ("daewoo",         "Daewoo",          "KR", None, "car", "defunct", None),
    # ── Reino Unido / deportivos ──────────────────────────────────────────────
    ("jaguar",         "Jaguar",          "GB", "JLR", "car", "active", None),
    ("land-rover",     "Land Rover",      "GB", "JLR", "car", "active", None),
    ("aston-martin",   "Aston Martin",    "GB", None, "car", "active", None),
    ("mclaren",        "McLaren",         "GB", None, "car", "active", None),
    ("morgan",         "Morgan",          "GB", None, "car", "active", None),
    ("caterham",       "Caterham",        "GB", None, "car", "active", None),
    ("ineos",          "INEOS",           "GB", None, "car", "active", None),
    ("rover",          "Rover",           "GB", None, "car", "defunct", None),
    ("mg",             "MG",              "GB", "SAIC", "car", "active", None),
    ("maxus",          "Maxus",           "CN", "SAIC", "van", "active", None),
    ("ferrari",        "Ferrari",         "IT", None, "car", "active", None),
    ("saab",           "Saab",            "SE", None, "car", "defunct", None),
    # ── Estados Unidos ────────────────────────────────────────────────────────
    ("ford",           "Ford",            "US", "Ford", "car", "active", None),
    ("lincoln",        "Lincoln",         "US", "Ford", "car", "active", None),
    ("chevrolet",      "Chevrolet",       "US", "General Motors", "car", "active", None),
    ("cadillac",       "Cadillac",        "US", "General Motors", "car", "active", None),
    ("gmc",            "GMC",             "US", "General Motors", "van", "active", None),
    ("buick",          "Buick",           "US", "General Motors", "car", "active", None),
    ("corvette",       "Corvette",        "US", "General Motors", "car", "active", None),
    ("hummer",         "Hummer",          "US", "General Motors", "car", "active", None),
    ("pontiac",        "Pontiac",         "US", "General Motors", "car", "defunct", None),
    ("tesla",          "Tesla",           "US", "Tesla", "car", "active", None),
    ("rivian",         "Rivian",          "US", None, "car", "active", None),
    ("lucid",          "Lucid",           "US", None, "car", "active", None),
    # ── China ─────────────────────────────────────────────────────────────────
    ("byd",            "BYD",             "CN", "BYD", "car", "active", None),
    ("chery",          "Chery",           "CN", "Chery", "car", "active", None),
    ("omoda",          "Omoda",           "CN", "Chery", "car", "active", None),
    ("jaecoo",         "Jaecoo",          "CN", "Chery", "car", "active", None),
    ("exeed",          "Exeed",           "CN", "Chery", "car", "active", None),
    ("great-wall",     "Great Wall",      "CN", "GWM", "car", "active", None),
    ("haval",          "Haval",           "CN", "GWM", "car", "active", None),
    ("ora",            "ORA",             "CN", "GWM", "car", "active", None),
    ("wey",            "WEY",             "CN", "GWM", "car", "active", None),
    ("dfsk",           "DFSK",            "CN", "Dongfeng", "car", "active", None),
    ("dongfeng",       "Dongfeng",        "CN", "Dongfeng", "car", "active", None),
    ("seres",          "Seres",           "CN", "Seres", "car", "active", None),
    ("changan",        "Changan",         "CN", "Changan", "car", "active", None),
    ("geely",          "Geely",           "CN", "Geely", "car", "active", None),
    ("baic",           "BAIC",            "CN", "BAIC", "car", "active", None),
    ("gac",            "GAC",             "CN", "GAC", "car", "active", None),
    ("aiways",         "Aiways",          "CN", None, "car", "active", None),
    ("xpeng",          "XPENG",           "CN", None, "car", "active", None),
    ("nio",            "NIO",             "CN", None, "car", "active", None),
    ("leapmotor",      "Leapmotor",       "CN", "Leapmotor", "car", "active", None),
    ("hongqi",         "Hongqi",          "CN", "FAW", "car", "active", None),
    ("bestune",        "Bestune",         "CN", "FAW", "car", "active", None),
    ("jac",            "JAC",             "CN", "JAC", "car", "active", None),
    ("swm",            "SWM",             "CN", None, "car", "active", None),
    ("yudo",           "Yudo",            "CN", None, "car", "active", None),
    ("skywell",        "Skywell",         "CN", None, "car", "active", None),
    ("foton",          "Foton",           "CN", None, "van", "active", None),
    # ── Otros mercados ────────────────────────────────────────────────────────
    ("tata",           "Tata",            "IN", "Tata Motors", "car", "active", None),
    ("mahindra",       "Mahindra",        "IN", "Mahindra", "car", "active", None),
    ("lada",           "Lada",            "RU", "AvtoVAZ", "car", "active", None),
    ("ebro",           "EBRO",            "ES", "EV Motors", "car", "active", None),
    ("santana",        "Santana",         "ES", None, "car", "defunct", None),
    ("simca",          "Simca",           "FR", None, "car", "defunct", None),
    ("talbot",         "Talbot",          "FR", None, "car", "defunct", None),
    ("austin",         "Austin",          "GB", None, "car", "defunct", None),
    ("galloper",       "Galloper",        "ES", None, "car", "defunct", None),
    ("dr",             "DR Automobiles",  "IT", "DR", "car", "active", None),
    ("evo",            "EVO",             "IT", "DR", "car", "active", None),
    ("xev",            "XEV",             "IT", None, "car", "active", None),
    # ── Cuadriciclos ligeros ──────────────────────────────────────────────────
    ("aixam",          "Aixam",           "FR", None, "car", "active", None),
    ("ligier",         "Ligier",          "FR", None, "car", "active", None),
    ("microcar",       "Microcar",        "FR", None, "car", "active", None),
    ("chatenet",       "Chatenet",        "FR", None, "car", "active", None),
    # ── Industrial (no listable en un selector de coches) ─────────────────────
    ("iveco",          "Iveco",           "IT", "Iveco Group", "van", "active", None),
    ("man",            "MAN",             "DE", "Traton", "truck", "active", None),
    ("scania",         "Scania",          "SE", "Traton", "truck", "active", None),
    ("daf",            "DAF",             "NL", "Paccar", "truck", "active", None),
    # ── Autocaravanas ─────────────────────────────────────────────────────────
    ("benimar",        "Benimar",         "ES", None, "motorhome", "active", None),
    ("mclouis",        "McLouis",         "IT", None, "motorhome", "active", None),
    ("challenger",     "Challenger",      "FR", None, "motorhome", "active", None),
    ("rimor",          "Rimor",           "IT", None, "motorhome", "active", None),
    ("giottiline",     "Giottiline",      "IT", None, "motorhome", "active", None),
    ("roller-team",    "Roller Team",     "IT", None, "motorhome", "active", None),
    ("adria",          "Adria",           "SI", None, "motorhome", "active", None),
    ("hymer",          "Hymer",           "DE", None, "motorhome", "active", None),
    ("elnagh",         "Elnagh",          "IT", None, "motorhome", "active", None),
    ("burstner",       "Bürstner",        "DE", None, "motorhome", "active", None),
    ("knaus",          "Knaus",           "DE", None, "motorhome", "active", None),
    ("dethleffs",      "Dethleffs",       "DE", None, "motorhome", "active", None),
    ("pilote",         "Pilote",          "FR", None, "motorhome", "active", None),
    ("weinsberg",      "Weinsberg",       "DE", None, "motorhome", "active", None),
    ("itineo",         "Itineo",          "FR", None, "motorhome", "active", None),
    ("sunlight",       "Sunlight",        "DE", None, "motorhome", "active", None),
    ("sterckeman",     "Sterckeman",      "FR", None, "motorhome", "active", None),
    # ── Motocicletas ──────────────────────────────────────────────────────────
    ("yamaha",         "Yamaha",          "JP", None, "motorcycle", "active", None),
    ("kawasaki",       "Kawasaki",        "JP", None, "motorcycle", "active", None),
    ("ducati",         "Ducati",          "IT", "Volkswagen AG", "motorcycle", "active", None),
    ("aprilia",        "Aprilia",         "IT", "Piaggio", "motorcycle", "active", None),
    ("piaggio",        "Piaggio",         "IT", "Piaggio", "motorcycle", "active", None),
    ("vespa",          "Vespa",           "IT", "Piaggio", "motorcycle", "active", None),
    ("moto-guzzi",     "Moto Guzzi",      "IT", "Piaggio", "motorcycle", "active", None),
    ("ktm",            "KTM",             "AT", None, "motorcycle", "active", None),
    ("triumph",        "Triumph",         "GB", None, "motorcycle", "active", None),
    ("zontes",         "Zontes",          "CN", None, "motorcycle", "active", None),
    ("voge",           "Voge",            "CN", None, "motorcycle", "active", None),
    ("qjmotor",        "QJMotor",         "CN", None, "motorcycle", "active", None),
    ("cfmoto",         "CFMOTO",          "CN", None, "motorcycle", "active", None),
    ("supersoco",      "Super Soco",      "CN", None, "motorcycle", "active", None),
    ("sym",            "SYM",             "TW", None, "motorcycle", "active", None),
    ("kymco",          "KYMCO",           "TW", None, "motorcycle", "active", None),
]

# Extra spellings that make_norm() cannot bridge on its own, because the census
# uses a SHORTER name than the marque's full one. 'DS' normalises to DS, but the
# registry stores 'DS Automobiles' -> DSAUTOMOBILES, so the two never meet. Found by
# the unresolved report below, not guessed: DS alone is 14,062 cars.
EXTRA_ALIASES: dict[str, str] = {
    "DS": "ds",
    "DR": "dr",
    "GREATWALL": "great-wall",
    "ROLLERTEAM": "roller-team",
    "MOTOGUZZI": "moto-guzzi",
    "MERCEDESAMG": "mercedes-amg",
    "MERCEDES": "mercedes-benz",
    "PEUGOT": "peugeot",      # a real, repeated misspelling in the census
    "WOLKSWAGUEN": "volkswagen",
    "CITROEM": "citroen",
    # What a Spanish buyer types for the folded marques. Without these the fold
    # removes the make facet and gives nothing back: someone searching "AMG" would
    # simply find nothing.
    "AMG": "mercedes-benz",
    "MERCEDESMAYBACH": "mercedes-benz",
    "CHEVROLETCORVETTE": "chevrolet",
    "SANGYONG": "kgm",
    "SSANGYONGKGM": "kgm",
}

# Marques found in the unresolved report and identified by hand. Motorhome and
# motorcycle makers dominate the tail — real vehicles, real brands, but not cars,
# so they resolve (a search for them works) while staying out of the car picker.
TAIL_MARQUES: list[tuple[str, str, str | None, str | None, str, str, str | None]] = [
    ("harley-davidson", "Harley-Davidson", "US", None, "motorcycle", "active", None),
    ("silence",         "Silence",         "ES", None, "motorcycle", "active", None),
    ("macbor",          "Macbor",          "ES", None, "motorcycle", "active", None),
    ("wottan",          "Wottan",          "ES", None, "motorcycle", "active", None),
    ("rapido",          "Rapido",          "FR", None, "motorhome", "active", None),
    ("carado",          "Carado",          "DE", None, "motorhome", "active", None),
    ("mobilvetta",      "Mobilvetta",      "IT", None, "motorhome", "active", None),
    ("etrusco",         "Etrusco",         "IT", None, "motorhome", "active", None),
    ("hobby",           "Hobby",           "DE", None, "motorhome", "active", None),
    ("chausson",        "Chausson",        "FR", None, "motorhome", "active", None),
    ("laika",           "Laika",           "IT", None, "motorhome", "active", None),
    ("bavaria",         "Bavaria",         "DE", None, "motorhome", "active", None),
]

# Sub-brands that FOLD into a parent, and the far longer list that must not.
#
# The owner's complaint was that "hay varias marcas de la misma marca" and someone
# hunting an AMG inside Mercedes will not find it. Measured against the census, only
# five marques actually suffer that bug — and the three he named split three ways:
#
#   * Mercedes-AMG is real and broken: 22 model names exist under BOTH makes
#     (A 45 AMG = 4 cars here, 72 there). Nobody in Spain buys "un Mercedes-AMG";
#     they buy "un Mercedes AMG". coches.net has no AMG brand at all.
#   * BMW M and Audi RS do NOT exist as makes in the census — zero rows. They live
#     correctly at model level (M2, M4, X5 M, RS3, RS6). Creating them as makes
#     would MANUFACTURE the very bug being reported.
#   * SsangYong/KGM was not in the brief and is the biggest instance: 4.486 cars,
#     13 duplicated model names, because KGM is SsangYong's 2023 rename and both
#     were listable.
#
# What must NOT fold, with the reason in the buyer's terms rather than the
# corporate chart: CUPRA (63% of its stock are nameplates SEAT never sold, own
# dealerships), DS (DS 7 Crossback never existed as a Citroën), Abarth (shares
# NAMES with Fiat but not cars, and at a different price), Alpine (folding it would
# also capture 581 Renaults carrying the "Esprit Alpine" TRIM), Polestar (23 Volvos
# carry "Polestar Engineered" as a trim), MINI, smart, and the Chinese marques sold
# in Spain under their own name — Omoda, Jaecoo, EBRO, Lynk & Co — whose parent
# (Chery, Geely) has almost no stock and which no Spanish buyer would think to type.
SUB_BRAND_FOLD: dict[str, str] = {
    "MERCEDESAMG": "mercedes-benz",
    "MAYBACH": "mercedes-benz",
    "CORVETTE": "chevrolet",
    "SSANGYONG": "kgm",
    # VAUXHALL is deliberately NOT here. It looks like the same case and is not:
    # the three Vauxhalls in the census are 1960s-70s British classics (Victor
    # 1963/65, Viva 1979), not rebadged Opels, and an alias would re-file them as
    # Opels in the cube. Three cars is not a reason to publish a falsehood. It stays
    # its own marque, unlisted, and still resolves if someone types it.
}

# Marques retired from the picker. Folded children plus Zeekr, which is a genuinely
# separate premium marque with three cars — too few to be a useful facet, and never
# to be aliased into Geely.
NOT_LISTABLE = ("mercedes-amg", "maybach", "corvette", "vauxhall", "ssangyong", "zeekr")

# Spellings where the census put a MODEL (or a sub-brand) in the make field. The row
# is a real car; the value simply named the wrong thing. `implied_model` lets a later
# pass repair the model too instead of only fixing the marque.
MODEL_AS_MAKE: dict[str, tuple[str, str | None]] = {
    "GOLF":       ("volkswagen", "Golf"),
    "POLO":       ("volkswagen", "Polo"),
    "PASSAT":     ("volkswagen", "Passat"),
    "TOURAN":     ("volkswagen", "Touran"),
    "IBIZA":      ("seat", "Ibiza"),
    "LEON":       ("seat", "León"),
    "CLIO":       ("renault", "Clio"),
    "MEGANE":     ("renault", "Mégane"),
    "TUCSON":     ("hyundai", "Tucson"),
    "KONA":       ("hyundai", "Kona"),
    "I10":        ("hyundai", "i10"),
    "I20":        ("hyundai", "i20"),
    "I30":        ("hyundai", "i30"),
    "RANGEROVER": ("land-rover", "Range Rover"),
    "LAND":       ("land-rover", None),
    "WOLKSWAGEN": ("volkswagen", None),
}


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN, command_timeout=900)
    try:
        if apply:
            await conn.executemany(
                """
                INSERT INTO make_canon (slug, norm_key, display_name, country_iso,
                                        legal_group, vehicle_class, status, successor_slug)
                VALUES ($1, make_norm($2), $2, $3, $4, $5, $6, NULL)
                ON CONFLICT (slug) DO UPDATE
                   SET display_name = EXCLUDED.display_name,
                       country_iso  = EXCLUDED.country_iso,
                       legal_group  = EXCLUDED.legal_group,
                       vehicle_class= EXCLUDED.vehicle_class,
                       status       = EXCLUDED.status,
                       updated_at   = now()
                """,
                [(m[0], m[1], m[2], m[3], m[4], m[5]) for m in MARQUES + TAIL_MARQUES],
            )
            # Successors in a second pass: the target row has to exist first.
            for slug, _d, _c, _g, _v, _s, succ in MARQUES:
                if succ:
                    await conn.execute(
                        "UPDATE make_canon SET successor_slug=$2 WHERE slug=$1", slug, succ)
            # Only cars and vans belong in a car brand picker. The rest stay
            # resolvable but never render as a logo tile.
            await conn.execute(
                "UPDATE make_canon SET is_listable = (vehicle_class = ANY (ARRAY['car','van']))")

            # KGM carries BOTH names in its label. The rename is two years old and
            # most of the stock was sold as a SsangYong; a picker that says only
            # "KGM" asks the owner of a Tivoli to recognise a brand they have never
            # heard of.
            await conn.execute(
                "UPDATE make_canon SET display_name = 'KGM (SsangYong)' WHERE slug = 'kgm'")
            # The alias now points straight at the parent, so the successor walk is
            # no longer the route — clearing it keeps one mechanism doing the job
            # instead of two that could disagree.
            await conn.execute(
                "UPDATE make_canon SET successor_slug = NULL WHERE slug = 'ssangyong'")
            await conn.execute(
                "UPDATE make_canon SET is_listable = false WHERE slug = ANY($1::text[])",
                list(NOT_LISTABLE))

            await conn.execute(
                """
                INSERT INTO make_alias (alias_norm, alias_raw, canon_slug, kind, n_seen)
                SELECT s.k, s.ejemplo, c.slug,
                       CASE WHEN s.ejemplo = c.display_name THEN 'exact' ELSE 'normalized' END,
                       s.n
                  FROM (SELECT make_norm(make) AS k, min(make) AS ejemplo, count(*)::int AS n
                          FROM vehicle
                         WHERE make IS NOT NULL AND btrim(make) <> ''
                         GROUP BY 1) s
                  JOIN make_canon c ON c.norm_key = s.k
                ON CONFLICT (alias_norm) DO UPDATE SET n_seen = EXCLUDED.n_seen
                """)
            # The fold runs LAST among the alias writes so it wins over whatever the
            # census-derived pass wrote for the same spelling.
            for norm, slug in {**EXTRA_ALIASES, **SUB_BRAND_FOLD}.items():
                await conn.execute(
                    """
                    INSERT INTO make_alias (alias_norm, alias_raw, canon_slug, kind)
                    VALUES ($1, $1, $2, 'normalized')
                    ON CONFLICT (alias_norm) DO UPDATE SET canon_slug = EXCLUDED.canon_slug
                    """, norm, slug)
            for norm, (slug, model) in MODEL_AS_MAKE.items():
                await conn.execute(
                    """
                    INSERT INTO make_alias (alias_norm, alias_raw, canon_slug, kind, implied_model)
                    VALUES ($1, $1, $2, 'model_as_make', $3)
                    ON CONFLICT (alias_norm) DO UPDATE
                       SET canon_slug = EXCLUDED.canon_slug, kind = 'model_as_make',
                           implied_model = EXCLUDED.implied_model
                    """, norm, slug, model)

        canon_n = await conn.fetchval("SELECT count(*) FROM make_canon")
        alias_n = await conn.fetchval("SELECT count(*) FROM make_alias")
        listable = await conn.fetchval("SELECT count(*) FROM make_canon WHERE is_listable")
        print(f"make_canon: {canon_n} marcas ({listable} listables) | make_alias: {alias_n}")

        cov = await conn.fetchrow(
            """
            SELECT count(*) FILTER (WHERE a.canon_slug IS NOT NULL) AS resueltas,
                   count(*) AS total
              FROM vehicle v
              LEFT JOIN make_alias a ON a.alias_norm = make_norm(v.make)
             WHERE v.status='available' AND v.make IS NOT NULL AND btrim(v.make) <> ''
            """)
        pct = 100 * cov["resueltas"] / cov["total"] if cov["total"] else 0
        print(f"cobertura del censo con marca: {cov['resueltas']:,}/{cov['total']:,} ({pct:.2f}%)")

        print("\nsin resolver (top 20 — para curación humana, NUNCA adivinadas):")
        rows = await conn.fetch(
            """
            SELECT make_norm(v.make) AS k, min(v.make) AS ejemplo, count(*)::int AS n
              FROM vehicle v
              LEFT JOIN make_alias a ON a.alias_norm = make_norm(v.make)
             WHERE v.status='available' AND v.make IS NOT NULL AND btrim(v.make) <> ''
               AND a.canon_slug IS NULL
             GROUP BY 1 ORDER BY 3 DESC LIMIT 20
            """)
        for r in rows:
            print(f"    {r['k']!r:32} {r['n']:>7,}  ej. {r['ejemplo']!r}")

        if not apply:
            print("\nDRY-RUN — no writes. Re-run with --apply.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
