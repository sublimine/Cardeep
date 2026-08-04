"""Seed model_attributes — body type and segment as a property of the MODEL.

Why the model and not the listing: a Ford Galaxy is a monovolumen because of what
it is, not because of what its advert says. Colour has to be read per car; shape
does not. Measured on the census, body-type words appear in 2.0% of titles — so
labelling listings could never answer "grande de familia", while labelling models
can, and there are three orders of magnitude fewer of them.

These labels are written BY HAND, deliberately.

The alternative considered was a local qwen2.5:7b pass, which measured 83% accuracy
on this taxonomy with a constrained prompt and emitted `4-5` where an integer was
required. For a table this small — the head of the census is a few hundred rows,
and each row is leveraged across roughly 2,300 listings — 83% is not a saving, it
is 17% of the fleet mislabelled at the point where the product makes its cleverest
claim. Every row below is a car the author can identify on sight.

`is_family` is not a synonym for "big". It is the question a buyer is actually
asking with "coche grande de familia": can five people and their luggage travel in
it. That makes it true for familiares, monovolúmenes and mid/large SUVs, and false
for a 5-door utilitario however many seats it technically has.

Run:  python scripts/seed_model_attributes.py            # dry-run
      python scripts/seed_model_attributes.py --apply
"""
from __future__ import annotations

import asyncio
import sys

import asyncpg

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# (make, model, body_type, segment, seats, is_family)
# body_type ∈ utilitario | compacto | berlina | familiar | suv | monovolumen |
#             coupe | cabrio | furgoneta | pickup
# segment   ∈ A | B | C | D | E | F | comercial   (European segment convention)
LABELS: list[tuple[str, str, str, str, int | None, bool]] = [
    # ── Volkswagen ────────────────────────────────────────────────────────────
    ("Volkswagen", "Golf",        "compacto",    "C", 5, False),
    ("Volkswagen", "Polo",        "utilitario",  "B", 5, False),
    ("Volkswagen", "Passat",      "berlina",     "D", 5, True),
    ("Volkswagen", "Tiguan",      "suv",         "C", 5, True),
    ("Volkswagen", "T-Roc",       "suv",         "B", 5, False),
    ("Volkswagen", "T-Cross",     "suv",         "B", 5, False),
    ("Volkswagen", "Taigo",       "suv",         "B", 5, False),
    ("Volkswagen", "Touran",      "monovolumen", "C", 7, True),
    ("Volkswagen", "Touareg",     "suv",         "E", 5, True),
    ("Volkswagen", "Caddy",       "furgoneta",   "comercial", 5, True),
    ("Volkswagen", "Transporter", "furgoneta",   "comercial", 3, False),
    ("Volkswagen", "Multivan",    "monovolumen", "comercial", 7, True),
    ("Volkswagen", "Arteon",      "berlina",     "D", 5, True),
    ("Volkswagen", "ID.3",        "compacto",    "C", 5, False),
    ("Volkswagen", "ID.4",        "suv",         "C", 5, True),
    # ── SEAT / CUPRA ──────────────────────────────────────────────────────────
    ("SEAT",  "Ibiza",     "utilitario",  "B", 5, False),
    ("SEAT",  "Leon",      "compacto",    "C", 5, False),
    ("SEAT",  "Arona",     "suv",         "B", 5, False),
    ("SEAT",  "Ateca",     "suv",         "C", 5, True),
    ("SEAT",  "Tarraco",   "suv",         "D", 7, True),
    ("SEAT",  "Alhambra",  "monovolumen", "D", 7, True),
    ("SEAT",  "Altea",     "monovolumen", "C", 5, True),
    ("SEAT",  "Toledo",    "berlina",     "C", 5, False),
    ("SEAT",  "Mii",       "utilitario",  "A", 4, False),
    ("CUPRA", "Formentor", "suv",         "C", 5, True),
    ("CUPRA", "León",      "compacto",    "C", 5, False),
    ("CUPRA", "Ateca",     "suv",         "C", 5, True),
    ("CUPRA", "Born",      "compacto",    "C", 5, False),
    ("CUPRA", "Terramar",  "suv",         "C", 5, True),
    # ── Audi ──────────────────────────────────────────────────────────────────
    ("Audi", "A1", "utilitario", "B", 5, False),
    ("Audi", "A3", "compacto",   "C", 5, False),
    ("Audi", "A4", "berlina",    "D", 5, True),
    ("Audi", "A5", "coupe",      "D", 5, False),
    ("Audi", "A6", "berlina",    "E", 5, True),
    ("Audi", "A7", "coupe",      "E", 5, False),
    ("Audi", "A8", "berlina",    "F", 5, True),
    ("Audi", "Q2", "suv",        "B", 5, False),
    ("Audi", "Q3", "suv",        "C", 5, True),
    ("Audi", "Q5", "suv",        "D", 5, True),
    ("Audi", "Q7", "suv",        "E", 7, True),
    ("Audi", "Q8", "suv",        "E", 5, True),
    ("Audi", "TT", "coupe",      "C", 4, False),
    # ── BMW ───────────────────────────────────────────────────────────────────
    ("BMW", "Serie 1", "compacto", "C", 5, False),
    ("BMW", "Serie 2", "coupe",    "C", 5, False),
    ("BMW", "Serie 3", "berlina",  "D", 5, True),
    ("BMW", "Serie 4", "coupe",    "D", 5, False),
    ("BMW", "Serie 5", "berlina",  "E", 5, True),
    ("BMW", "Serie 6", "coupe",    "E", 5, False),
    ("BMW", "Serie 7", "berlina",  "F", 5, True),
    ("BMW", "Serie 8", "coupe",    "F", 4, False),
    ("BMW", "X1", "suv", "C", 5, True),
    ("BMW", "X2", "suv", "C", 5, False),
    ("BMW", "X3", "suv", "D", 5, True),
    ("BMW", "X4", "suv", "D", 5, False),
    ("BMW", "X5", "suv", "E", 7, True),
    ("BMW", "X6", "suv", "E", 5, False),
    ("BMW", "X7", "suv", "F", 7, True),
    ("BMW", "Z4", "cabrio", "D", 2, False),
    # ── Mercedes-Benz ─────────────────────────────────────────────────────────
    ("Mercedes-Benz", "Clase A",   "compacto",    "C", 5, False),
    ("Mercedes-Benz", "Clase B",   "monovolumen", "C", 5, True),
    ("Mercedes-Benz", "Clase C",   "berlina",     "D", 5, True),
    ("Mercedes-Benz", "Clase E",   "berlina",     "E", 5, True),
    ("Mercedes-Benz", "Clase S",   "berlina",     "F", 5, True),
    ("Mercedes-Benz", "Clase CLA", "berlina",     "C", 5, False),
    ("Mercedes-Benz", "Clase CLS", "coupe",       "E", 5, False),
    ("Mercedes-Benz", "Clase GLA", "suv",         "B", 5, False),
    ("Mercedes-Benz", "Clase GLB", "suv",         "C", 7, True),
    ("Mercedes-Benz", "Clase GLC", "suv",         "D", 5, True),
    ("Mercedes-Benz", "Clase GLE", "suv",         "E", 7, True),
    ("Mercedes-Benz", "Clase GLS", "suv",         "F", 7, True),
    ("Mercedes-Benz", "Clase G",   "suv",         "E", 5, True),
    ("Mercedes-Benz", "Clase M",   "suv",         "E", 5, True),
    ("Mercedes-Benz", "Clase V",   "monovolumen", "comercial", 7, True),
    ("Mercedes-Benz", "Vito",      "furgoneta",   "comercial", 3, False),
    ("Mercedes-Benz", "Sprinter",  "furgoneta",   "comercial", 3, False),
    ("Mercedes-Benz", "Citan",     "furgoneta",   "comercial", 5, False),
    # ── Peugeot ───────────────────────────────────────────────────────────────
    ("Peugeot", "108",     "utilitario",  "A", 5, False),
    ("Peugeot", "208",     "utilitario",  "B", 5, False),
    ("Peugeot", "2008",    "suv",         "B", 5, False),
    ("Peugeot", "308",     "compacto",    "C", 5, False),
    ("Peugeot", "3008",    "suv",         "C", 5, True),
    ("Peugeot", "408",     "berlina",     "C", 5, True),
    ("Peugeot", "5008",    "suv",         "D", 7, True),
    ("Peugeot", "508",     "berlina",     "D", 5, True),
    ("Peugeot", "206",     "utilitario",  "B", 5, False),
    ("Peugeot", "207",     "utilitario",  "B", 5, False),
    ("Peugeot", "307",     "compacto",    "C", 5, False),
    ("Peugeot", "407",     "berlina",     "D", 5, True),
    ("Peugeot", "Rifter",  "monovolumen", "comercial", 5, True),
    ("Peugeot", "Partner", "furgoneta",   "comercial", 3, False),
    ("Peugeot", "Expert",  "furgoneta",   "comercial", 3, False),
    ("Peugeot", "Boxer",   "furgoneta",   "comercial", 3, False),
    ("Peugeot", "Traveller", "monovolumen", "comercial", 8, True),
    # ── Citroën ───────────────────────────────────────────────────────────────
    ("Citroën", "C1",           "utilitario",  "A", 5, False),
    ("Citroën", "C3",           "utilitario",  "B", 5, False),
    ("Citroën", "C3 Aircross",  "suv",         "B", 5, False),
    ("Citroën", "C4",           "compacto",    "C", 5, False),
    ("Citroën", "C4 Cactus",    "suv",         "B", 5, False),
    ("Citroën", "C4 Picasso",   "monovolumen", "C", 5, True),
    ("Citroën", "C4 Grand Picasso", "monovolumen", "C", 7, True),
    ("Citroën", "C5",           "berlina",     "D", 5, True),
    ("Citroën", "C5 Aircross",  "suv",         "C", 5, True),
    ("Citroën", "Berlingo",     "monovolumen", "comercial", 5, True),
    ("Citroën", "Jumpy",        "furgoneta",   "comercial", 3, False),
    ("Citroën", "Jumper",       "furgoneta",   "comercial", 3, False),
    ("Citroën", "Xsara",        "compacto",    "C", 5, False),
    ("Citroën", "C-Elysée",     "berlina",     "C", 5, False),
    # ── Renault / Dacia ───────────────────────────────────────────────────────
    ("Renault", "Clio",    "utilitario",  "B", 5, False),
    ("Renault", "Captur",  "suv",         "B", 5, False),
    ("Renault", "Megane",  "compacto",    "C", 5, False),
    ("Renault", "Arkana",  "suv",         "C", 5, True),
    ("Renault", "Kadjar",  "suv",         "C", 5, True),
    ("Renault", "Austral", "suv",         "C", 5, True),
    ("Renault", "Scenic",  "monovolumen", "C", 5, True),
    ("Renault", "Grand Scenic", "monovolumen", "C", 7, True),
    ("Renault", "Espace",  "monovolumen", "D", 7, True),
    ("Renault", "Kangoo",  "monovolumen", "comercial", 5, True),
    ("Renault", "Trafic",  "furgoneta",   "comercial", 3, False),
    ("Renault", "Master",  "furgoneta",   "comercial", 3, False),
    ("Renault", "Twingo",  "utilitario",  "A", 4, False),
    ("Renault", "Zoe",     "utilitario",  "B", 5, False),
    ("Renault", "Laguna",  "berlina",     "D", 5, True),
    ("Dacia",   "Sandero", "utilitario",  "B", 5, False),
    ("Dacia",   "Duster",  "suv",         "C", 5, True),
    ("Dacia",   "Jogger",  "familiar",    "C", 7, True),
    ("Dacia",   "Logan",   "berlina",     "C", 5, True),
    ("Dacia",   "Lodgy",   "monovolumen", "C", 7, True),
    ("Dacia",   "Spring",  "utilitario",  "A", 4, False),
    # ── Ford / Opel ───────────────────────────────────────────────────────────
    ("Ford", "Fiesta",   "utilitario",  "B", 5, False),
    ("Ford", "Focus",    "compacto",    "C", 5, False),
    ("Ford", "Puma",     "suv",         "B", 5, False),
    ("Ford", "Kuga",     "suv",         "C", 5, True),
    ("Ford", "EcoSport", "suv",         "B", 5, False),
    ("Ford", "Mondeo",   "berlina",     "D", 5, True),
    ("Ford", "S-Max",    "monovolumen", "D", 7, True),
    ("Ford", "Galaxy",   "monovolumen", "D", 7, True),
    ("Ford", "C-Max",    "monovolumen", "C", 5, True),
    ("Ford", "Explorer", "suv",         "E", 7, True),
    ("Ford", "Transit",  "furgoneta",   "comercial", 3, False),
    ("Ford", "Transit Custom", "furgoneta", "comercial", 3, False),
    ("Ford", "Ranger",   "pickup",      "comercial", 5, False),
    ("Opel", "Corsa",       "utilitario",  "B", 5, False),
    ("Opel", "Astra",       "compacto",    "C", 5, False),
    ("Opel", "Mokka",       "suv",         "B", 5, False),
    ("Opel", "Crossland",   "suv",         "B", 5, False),
    ("Opel", "Grandland",   "suv",         "C", 5, True),
    ("Opel", "Grandland X", "suv",         "C", 5, True),
    ("Opel", "Insignia",    "berlina",     "D", 5, True),
    ("Opel", "Zafira",      "monovolumen", "C", 7, True),
    ("Opel", "Combo",       "monovolumen", "comercial", 5, True),
    ("Opel", "Vivaro",      "furgoneta",   "comercial", 3, False),
    ("Opel", "Meriva",      "monovolumen", "B", 5, True),
    # ── Asiáticas ─────────────────────────────────────────────────────────────
    ("Nissan",  "Micra",   "utilitario", "B", 5, False),
    ("Nissan",  "Juke",    "suv",        "B", 5, False),
    ("Nissan",  "Qashqai", "suv",        "C", 5, True),
    ("Nissan",  "X-Trail", "suv",        "D", 7, True),
    ("Nissan",  "Leaf",    "compacto",   "C", 5, False),
    ("Toyota",  "Aygo",       "utilitario", "A", 4, False),
    ("Toyota",  "Yaris",      "utilitario", "B", 5, False),
    ("Toyota",  "Yaris Cross","suv",        "B", 5, False),
    ("Toyota",  "Corolla",    "compacto",   "C", 5, False),
    ("Toyota",  "C-HR",       "suv",        "C", 5, False),
    ("Toyota",  "Rav4",       "suv",        "D", 5, True),
    ("Toyota",  "Auris",      "compacto",   "C", 5, False),
    ("Toyota",  "Land Cruiser","suv",       "E", 7, True),
    ("Toyota",  "Proace",     "furgoneta",  "comercial", 3, False),
    ("Hyundai", "i10",     "utilitario", "A", 5, False),
    ("Hyundai", "i20",     "utilitario", "B", 5, False),
    ("Hyundai", "i30",     "compacto",   "C", 5, False),
    ("Hyundai", "Bayon",   "suv",        "B", 5, False),
    ("Hyundai", "Kona",    "suv",        "B", 5, False),
    ("Hyundai", "Tucson",  "suv",        "C", 5, True),
    ("Hyundai", "Santa Fe","suv",        "D", 7, True),
    ("Hyundai", "Ioniq",   "compacto",   "C", 5, False),
    ("Kia", "Picanto",  "utilitario", "A", 5, False),
    ("Kia", "Rio",      "utilitario", "B", 5, False),
    ("Kia", "Stonic",   "suv",        "B", 5, False),
    ("Kia", "Ceed",     "compacto",   "C", 5, False),
    ("Kia", "XCeed",    "suv",        "C", 5, False),
    ("Kia", "Niro",     "suv",        "C", 5, True),
    ("Kia", "Sportage", "suv",        "C", 5, True),
    ("Kia", "Sorento",  "suv",        "D", 7, True),
    ("Kia", "Carens",   "monovolumen","C", 7, True),
    ("Mazda", "2",     "utilitario", "B", 5, False),
    ("Mazda", "3",     "compacto",   "C", 5, False),
    ("Mazda", "6",     "berlina",    "D", 5, True),
    ("Mazda", "CX-3",  "suv",        "B", 5, False),
    ("Mazda", "CX-30", "suv",        "C", 5, False),
    ("Mazda", "CX-5",  "suv",        "D", 5, True),
    ("Honda", "Civic", "compacto", "C", 5, False),
    ("Honda", "CR-V",  "suv",      "D", 5, True),
    ("Honda", "Jazz",  "utilitario","B", 5, False),
    ("Honda", "HR-V",  "suv",      "B", 5, False),
    ("Suzuki", "Swift",  "utilitario", "B", 5, False),
    ("Suzuki", "Vitara", "suv",        "C", 5, True),
    ("Suzuki", "S-Cross","suv",        "C", 5, True),
    ("Mitsubishi", "ASX",     "suv", "C", 5, True),
    ("Mitsubishi", "Outlander","suv", "D", 7, True),
    ("MG", "ZS",   "suv",      "B", 5, False),
    ("MG", "HS",   "suv",      "C", 5, True),
    ("MG", "MG3",  "utilitario","B", 5, False),
    ("MG", "MG4",  "compacto", "C", 5, False),
    ("MG", "Marvel R", "suv",  "D", 5, True),
    # ── Otras europeas ────────────────────────────────────────────────────────
    ("Fiat", "500",   "utilitario",  "A", 4, False),
    ("Fiat", "500X",  "suv",         "B", 5, False),
    ("Fiat", "500L",  "monovolumen", "B", 5, True),
    ("Fiat", "Panda", "utilitario",  "A", 5, False),
    ("Fiat", "Tipo",  "compacto",    "C", 5, False),
    ("Fiat", "Punto", "utilitario",  "B", 5, False),
    ("Fiat", "Ducato","furgoneta",   "comercial", 3, False),
    ("Fiat", "Doblo", "monovolumen", "comercial", 5, True),
    ("Škoda", "Fabia",   "utilitario", "B", 5, False),
    ("Škoda", "Octavia", "compacto",   "C", 5, True),
    ("Škoda", "Superb",  "berlina",    "D", 5, True),
    ("Škoda", "Kamiq",   "suv",        "B", 5, False),
    ("Škoda", "Karoq",   "suv",        "C", 5, True),
    ("Škoda", "Kodiaq",  "suv",        "D", 7, True),
    ("Škoda", "Scala",   "compacto",   "C", 5, False),
    ("Volvo", "XC40", "suv",     "C", 5, True),
    ("Volvo", "XC60", "suv",     "D", 5, True),
    ("Volvo", "XC90", "suv",     "E", 7, True),
    ("Volvo", "V40",  "compacto","C", 5, False),
    ("Volvo", "V60",  "familiar","D", 5, True),
    ("Volvo", "V90",  "familiar","E", 5, True),
    ("Volvo", "S60",  "berlina", "D", 5, True),
    ("MINI", "Mini",       "utilitario", "B", 4, False),
    ("MINI", "Cooper",     "utilitario", "B", 4, False),
    ("MINI", "Countryman", "suv",        "C", 5, True),
    ("MINI", "Clubman",    "familiar",   "C", 5, False),
    ("Jeep", "Renegade", "suv", "B", 5, False),
    ("Jeep", "Compass",  "suv", "C", 5, True),
    ("Jeep", "Avenger",  "suv", "B", 5, False),
    ("Jeep", "Cherokee", "suv", "D", 5, True),
    ("Jeep", "Wrangler", "suv", "D", 5, False),
    ("Alfa Romeo", "Giulietta", "compacto", "C", 5, False),
    ("Alfa Romeo", "Giulia",    "berlina",  "D", 5, True),
    ("Alfa Romeo", "Stelvio",   "suv",      "D", 5, True),
    ("Alfa Romeo", "Tonale",    "suv",      "C", 5, True),
    ("Land Rover", "Range Rover Evoque", "suv", "D", 5, True),
    ("Land Rover", "Range Rover Sport",  "suv", "E", 5, True),
    ("Land Rover", "Range Rover",        "suv", "F", 5, True),
    ("Land Rover", "Discovery",          "suv", "E", 7, True),
    ("Land Rover", "Discovery Sport",    "suv", "D", 7, True),
    ("Land Rover", "Defender",           "suv", "E", 5, True),
    ("Porsche", "Cayenne", "suv",    "E", 5, True),
    ("Porsche", "Macan",   "suv",    "D", 5, True),
    ("Porsche", "911",     "coupe",  "S", 4, False),
    ("Porsche", "Panamera","berlina","F", 5, True),
    ("Porsche", "Taycan",  "berlina","F", 5, True),
    ("DS Automobiles", "DS 3",            "utilitario", "B", 5, False),
    ("DS Automobiles", "DS 3 Crossback",  "suv",        "B", 5, False),
    ("DS Automobiles", "DS 4",            "compacto",   "C", 5, False),
    ("DS Automobiles", "DS 7 Crossback",  "suv",        "D", 5, True),
    ("Tesla", "Model 3", "berlina", "D", 5, True),
    ("Tesla", "Model Y", "suv",     "D", 5, True),
    ("Tesla", "Model S", "berlina", "F", 5, True),
    ("Tesla", "Model X", "suv",     "F", 7, True),
    ("Lynk & Co", "01", "suv", "C", 5, True),
    ("Omoda", "5", "suv", "C", 5, True),
    ("Iveco", "Daily", "furgoneta", "comercial", 3, False),
]


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN, command_timeout=600)
    try:
        if apply:
            await conn.executemany(
                """
                INSERT INTO model_attributes
                       (make_raw, model, body_type, segment, seats, is_family,
                        source, confidence, reviewed_by)
                VALUES ($1, $2, $3, $4, $5, $6, 'human', 1.0, 'cardeep')
                ON CONFLICT (make_raw, model) DO UPDATE
                   SET body_type = EXCLUDED.body_type,
                       segment   = EXCLUDED.segment,
                       seats     = EXCLUDED.seats,
                       is_family = EXCLUDED.is_family,
                       source    = 'human',
                       confidence= 1.0,
                       updated_at= now()
                """,
                LABELS,
            )

        total = await conn.fetchval("SELECT count(*) FROM model_attributes")
        # What share of the live index these labels actually reach. The point of
        # labelling the head is coverage, so coverage is the number to report —
        # not how many rows were typed.
        cov = await conn.fetchrow(
            """
            SELECT sum(c.n) FILTER (WHERE ma.body_type IS NOT NULL)::bigint AS cubierto,
                   sum(c.n)::bigint AS total
              FROM (SELECT make, model, sum(n)::int AS n FROM search_cube
                     WHERE make <> '' AND model <> '' GROUP BY 1, 2) c
              LEFT JOIN model_attributes ma
                     ON ma.make_raw = c.make AND ma.model = c.model
            """)
        pct = 100 * cov["cubierto"] / cov["total"] if cov["total"] else 0
        print(f"model_attributes: {total} pares etiquetados a mano")
        print(f"cobertura del parque: {cov['cubierto']:,}/{cov['total']:,} ({pct:.1f}%)")

        fam = await conn.fetchval(
            """
            SELECT sum(c.n)::bigint
              FROM (SELECT make, model, sum(n)::int AS n FROM search_cube
                     WHERE make <> '' AND model <> '' GROUP BY 1, 2) c
              JOIN model_attributes ma ON ma.make_raw = c.make AND ma.model = c.model
             WHERE ma.is_family
            """)
        print(f'"grande de familia" alcanzaría: {fam:,} coches')

        if not apply:
            print("\nDRY-RUN — no writes. Re-run with --apply.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
