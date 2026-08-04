"""Free-text query understanding — the deterministic lane.

Turns a Spanish sentence into structured filters. No model call, no network, no
embedding: a tokenizer, the census's own dictionaries, and a handful of patterns
for the way Spanish states a bound.

WHY DETERMINISTIC FIRST. Measured on the live index, an expert query
("mercedes c63 amg") resolves lexically in ~2.4 ms while a naive one
("coche rojo grande de familia") returns literally nothing, because the words are
not in the corpus — colour words appear in 0.04% of titles and body-type words in
2.0%. The naive lane is not a text-search problem at all; it is a vocabulary
problem, and the vocabulary lives in two places this module reads:

  * `make_canon` / `make_alias` and the cube's own model list — every marque and
    model the census actually holds, so "mercedes" resolves without anyone having
    typed a synonym list.
  * `model_attributes` — body type, segment, seats and is_family, hand-labelled per
    MODEL rather than per listing (a Ford Galaxy is a monovolumen by construction).
    This is what makes "grande de familia" answerable at all.

WHAT IT REFUSES TO DO. It never guesses. A token it cannot resolve is returned in
`unresolved` rather than dropped or approximated, so the caller can say "no
entendí X" instead of silently searching for something else. The owner's rule —
never show random results — is enforced here, at the point where a query would
otherwise be quietly widened into nonsense.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Vocabulary that is genuinely fixed (everything else is read from the census)
# ---------------------------------------------------------------------------

# Fuel. The census stores 110 raw variants; these are the words a person types.
_FUEL: dict[str, str] = {
    "diesel": "diesel", "diésel": "diesel", "gasoil": "diesel", "gasóleo": "diesel",
    "gasolina": "gasolina", "bencina": "gasolina",
    "electrico": "electrico", "eléctrico": "electrico", "electrica": "electrico",
    "ev": "electrico",
    "hibrido": "hibrido", "híbrido": "hibrido", "hibrida": "hibrido",
    "phev": "hibrido_enchufable", "enchufable": "hibrido_enchufable",
    "glp": "glp", "gnc": "gnc",
}

# Body words, mapped onto the taxonomy `model_attributes` uses.
_BODY: dict[str, str] = {
    "utilitario": "utilitario", "urbano": "utilitario", "citycar": "utilitario",
    "compacto": "compacto",
    "berlina": "berlina", "sedan": "berlina", "sedán": "berlina",
    "familiar": "familiar", "ranchera": "familiar", "estate": "familiar",
    "touring": "familiar", "avant": "familiar", "sportwagon": "familiar",
    "suv": "suv", "todoterreno": "suv", "4x4": "suv", "crossover": "suv",
    "monovolumen": "monovolumen", "mpv": "monovolumen", "furgo": "monovolumen",
    "coupe": "coupe", "cupé": "coupe", "coupé": "coupe",
    "cabrio": "cabrio", "descapotable": "cabrio", "convertible": "cabrio",
    "furgoneta": "furgoneta", "furgón": "furgoneta", "comercial": "furgoneta",
    "pickup": "pickup", "pick-up": "pickup",
}

# Colours, restricted to the vocabulary the URL harvest actually produced. A word
# outside this set is left unresolved rather than matched approximately.
_COLOR: dict[str, str] = {
    "blanco": "blanco", "blanca": "blanco", "negro": "negro", "negra": "negro",
    "gris": "gris", "plata": "plata", "plateado": "plata", "azul": "azul",
    "rojo": "rojo", "roja": "rojo", "verde": "verde", "amarillo": "amarillo",
    "naranja": "naranja", "marron": "marron", "marrón": "marron",
    "beige": "beige", "dorado": "dorado", "granate": "granate",
    "burdeos": "burdeos", "violeta": "violeta", "morado": "violeta",
}

# "grande de familia", "para la familia", "familiar grande" — the phrase a buyer
# uses when they mean space, not a body style. Resolved to `is_family`, which is
# the column that answers it honestly.
# Longest first: "grande de familia" has to win over "de familia", or the word
# "grande" survives into `unresolved` and the interface reports not understanding
# something it understood perfectly.
_FAMILY_PHRASES = (
    "grande de familia", "grande para la familia", "familiar grande",
    "para la familia", "de familia", "para familia",
)

_AUTOMATIC = ("automatico", "automático", "automatica", "automática", "cambio automatico")
_MANUAL = ("manual", "cambio manual")

# Words that carry no filter. Removing them stops the resolver from reporting the
# entire sentence as unresolved noise.
_STOPWORDS = frozenset("""
coche coches carro auto autos vehiculo vehículo vehiculos quiero busco buscar
necesito me gustaria gustaría un una el la los las de del al a en con por para y o
que mas más menos hasta desde entre sobre unos unas algo bueno buena barato barata
km kms kilometros kilómetros euros eur año años cerca zona provincia
""".split())

_NUM = r"(\d{1,3}(?:[.\s]\d{3})+|\d+)"


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )


def norm(text: str) -> str:
    """Lowercase, accent-free, punctuation-free — the shape every lookup uses.

    The currency symbol is SPELLED OUT before the strip, and that one line is load
    bearing. Every price pattern below ends in `(?:euros?|eur|€)`, and the strip ran
    first — so the `€` branch was dead code and "menos de 20.000 €" resolved to
    nothing at all. Three of the seven examples the field was teaching people to
    type carried a `€`, which means the interface was demonstrating a syntax its own
    parser discarded. The eval corpus never caught it because every case in it wrote
    "euros"; a test suite that only speaks the way the author writes cannot find the
    way a user writes.
    """
    spelled = text.replace("€", " euros ").replace("$", " euros ")
    return re.sub(r"[^a-z0-9\s]", " ", _strip_accents(spelled.lower())).strip()


def _to_int(raw: str) -> int:
    return int(re.sub(r"[.\s]", "", raw))


@dataclass
class ParsedQuery:
    """What a sentence resolved to. Every field is optional; nothing is invented."""

    make: str | None = None
    model: str | None = None
    submodel: str | None = None
    province_code: str | None = None
    province_name: str | None = None
    fuel: str | None = None
    body_type: str | None = None
    is_family: bool | None = None
    color: str | None = None
    seats_min: int | None = None
    transmission: str | None = None
    price_max: int | None = None
    price_min: int | None = None
    km_max: int | None = None
    km_min: int | None = None
    year_min: int | None = None
    year_max: int | None = None
    unresolved: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v not in (None, [], {})}


class QueryParser:
    """Resolves sentences against dictionaries loaded once from the census.

    Built by `load()` rather than at import time: the vocabularies ARE the data,
    and rebuilding the cube changes them.
    """

    def __init__(
        self,
        makes: dict[str, str],
        models: dict[str, list[tuple[str, str]]],
        provinces: dict[str, tuple[str, str]],
    ) -> None:
        self._makes = makes            # normalised marque -> canonical display
        self._models = models          # canonical make -> [(normalised, display)]
        self._provinces = provinces    # normalised name -> (code, display)

    # -- construction --------------------------------------------------------
    @classmethod
    async def load(cls, conn: Any) -> "QueryParser":
        # ONLY marques that exist in make_canon.
        #
        # Taking the marque list straight from the cube looked obvious and was
        # wrong: the census's `make` column still contains values that are not
        # brands — "DIESEL", "Electrico", "Coche", "...." — and being longer than
        # "bmw" they won the longest-match race. "BMW Serie 3 diésel" resolved to
        # make=DIESEL with bmw left unresolved. The curated registry is the only
        # list that answers "is this a marque"; the cube answers "is it present".
        # Both conditions are required.
        make_rows = await conn.fetch(
            """
            SELECT DISTINCT s.make
              FROM search_cube s
              JOIN make_canon mc ON mc.norm_key = make_norm(s.make)
             WHERE s.make <> ''
            """)
        makes = {norm(r["make"]): r["make"] for r in make_rows}

        # Aliases give the spellings a person types that the census does not use
        # ("mercedes" for Mercedes-Benz, "vw" for Volkswagen).
        alias_rows = await conn.fetch(
            """
            SELECT ma.alias_norm, mc.display_name
              FROM make_alias ma JOIN make_canon mc ON mc.slug = ma.canon_slug
             WHERE ma.kind <> 'model_as_make'
            """)
        for r in alias_rows:
            makes.setdefault(norm(r["alias_norm"]), r["display_name"])

        model_rows = await conn.fetch(
            "SELECT DISTINCT make, model FROM search_cube WHERE make <> '' AND model <> ''")
        models: dict[str, list[tuple[str, str]]] = {}
        for r in model_rows:
            models.setdefault(r["make"], []).append((norm(r["model"]), r["model"]))
        # Longest first, so "Serie 3" wins over "3" and "C3 Aircross" over "C3".
        for k in models:
            models[k].sort(key=lambda t: -len(t[0]))

        prov_rows = await conn.fetch(
            "SELECT code, name FROM geo_province WHERE country_code = 'ES'")
        provinces: dict[str, tuple[str, str]] = {}
        for r in prov_rows:
            code, name = r["code"], r["name"]
            provinces[norm(name)] = (code, name)
            # The table holds INE names, and nobody types those. Three shapes have
            # to answer to one province:
            #   "Alicante/Alacant"  — both halves of a bilingual name
            #   "Balears, Illes"    — the article moved to the end, INE-style
            #   "Coruña, A"         — same, and the half that matters is "Coruña"
            for part in re.split(r"[/,]", name):
                part = norm(part)
                if part:
                    provinces.setdefault(part, (code, name))
            if "," in name:
                head, _, tail = name.partition(",")
                provinces.setdefault(norm(f"{tail} {head}"), (code, name))

        # Castilian names for provinces the register lists under their co-official
        # form. These are not synonyms a normaliser can derive — they are different
        # words — and a Spanish product whose search fails on "Islas Baleares" or
        # "Vizcaya" is failing on the way most of the country writes.
        for spanish, code in {
            "islas baleares": "07", "baleares": "07",
            "la coruna": "15", "coruna": "15",
            "gerona": "17", "lerida": "25", "orense": "32",
            "alava": "01", "guipuzcoa": "20", "vizcaya": "48",
            "la rioja": "26", "castellon": "12",
            "santa cruz de tenerife": "38", "tenerife": "38",
            "las palmas": "35", "gran canaria": "35",
        }.items():
            match = next((p for p in prov_rows if p["code"] == code), None)
            if match:
                provinces.setdefault(norm(spanish), (code, match["name"]))

        return cls(makes, models, provinces)

    # -- parsing -------------------------------------------------------------
    def parse(self, text: str) -> ParsedQuery:
        out = ParsedQuery()
        raw = norm(text)
        if not raw:
            return out

        consumed: list[str] = []

        def take(phrase: str) -> None:
            """Remove a resolved phrase so its words are not reported unresolved."""
            nonlocal raw
            raw = raw.replace(phrase, " ", 1)
            consumed.append(phrase)

        # 1. Bounds first: they carry digits, and digits also appear in model names
        #    ("208", "Serie 3"). Consuming the bound phrases before matching models
        #    is what stops "menos de 15.000 €" from being read as a model.
        raw = self._take_bounds(raw, out, take)

        # 1b. Seats. "7 plazas" is a hard, non-negotiable constraint and the single
        #     most common way a Spanish family states what it needs — and it was
        #     landing in `unresolved` while "familiar" quietly resolved to the
        #     estate BODY STYLE. The owner's own example, "coche familiar 7
        #     plazas", answered 4.001 cars when it means 58.052: fourteen times
        #     fewer, and a different set of cars.
        m = re.search(r"\b([2-9])\s*(?:plazas|asientos)\b", raw)
        if m:
            out.seats_min = int(m.group(1))
            take(m.group(0))
        else:
            for word, count in (("siete", 7), ("nueve", 9), ("cinco", 5), ("dos", 2)):
                if re.search(rf"\b{word}\s*(?:plazas|asientos)\b", raw):
                    out.seats_min = count
                    take(f"{word} plazas")
                    take(f"{word} asientos")
                    break

        # 2. Fixed vocabularies BEFORE marques and models.
        #
        # Order is load-bearing. Marque matching is longest-first, so a six-letter
        # word beats a three-letter one — and "diésel" is longer than "bmw".
        # Consuming the words whose meaning is fixed (fuel, colour, body,
        # transmission) before looking for a brand is what keeps a fuel from being
        # read as one.
        for word, value in _FUEL.items():
            if re.search(rf"\b{re.escape(norm(word))}\b", raw):
                out.fuel = value
                take(norm(word))
                break
        for word, value in _COLOR.items():
            if re.search(rf"\b{re.escape(norm(word))}\b", raw):
                out.color = value
                take(norm(word))
                break
        for phrase in _FAMILY_PHRASES:
            if norm(phrase) in raw:
                out.is_family = True
                take(norm(phrase))
                break
        # Body words are matched ALL at once, not first-wins.
        #
        # "un suv familiar" contains two of them, and taking whichever the dict
        # happened to list first resolved it to `familiar` and left "suv"
        # unresolved — the opposite of what the sentence says. When "familiar"
        # appears alongside a real body style it is not the style, it is the
        # requirement: room for a family. So the style wins the body slot and
        # `familiar` is promoted to `is_family`.
        hits = [
            (value, norm(word))
            for word, value in _BODY.items()
            if re.search(rf"\b{re.escape(norm(word))}\b", raw)
        ]
        if hits:
            styles = [h for h in hits if h[0] != "familiar"]
            if styles and any(h[0] == "familiar" for h in hits):
                out.is_family = True
            chosen = styles[0] if styles else hits[0]
            out.body_type = chosen[0]
            for _, word in hits:
                take(word)

        # "familiar" beside a seat count is not a body style.
        #
        # On its own the word means the estate/ranchera shape, and that is how the
        # vocabulary maps it. But "coche familiar 7 plazas" is not asking for an
        # estate with seven seats — a combination that barely exists — it is asking
        # for room for seven, and the word "familiar" is doing emotional work, not
        # taxonomic. When a seat count is present the count wins and the word is
        # demoted to the requirement it actually expresses.
        if out.seats_min is not None and out.body_type == "familiar":
            out.body_type = None
            out.is_family = True
        for word in _AUTOMATIC:
            if norm(word) in raw:
                out.transmission = "automatico"
                take(norm(word))
                break
        else:
            for word in _MANUAL:
                if norm(word) in raw:
                    out.transmission = "manual"
                    take(norm(word))
                    break

        # 3. Marque and model BEFORE province.
        #
        # Spain names provinces after things that are also cars. "seat leon 2020"
        # resolved to the province of León — correct as a lookup, useless as an
        # answer — because province matching ran first and consumed the word.
        # Resolving the marque and its model first means "León" is already spoken
        # for when the geography is considered; a bare "en León" still lands,
        # because nothing else claimed it.
        for key in sorted(self._makes, key=len, reverse=True):
            if re.search(rf"\b{re.escape(key)}\b", raw):
                out.make = self._makes[key]
                take(key)
                break

        # The model is chosen by WHERE it matches, not by how long it is.
        #
        # "mercedes clase c 220 d" contains both "clase c" and "c 220 d" — the
        # second only because dirty rows let a version leak into the model column.
        # Longest-first made it a coin toss between two seven-character matches and
        # it picked the version, yielding model="C 220 d" with "clase" orphaned.
        # The earliest match is the right tie-break: a person writes the model
        # before its version, always.
        if out.make:
            candidates = [
                (m.start(), -len(nmodel), display, nmodel)
                for nmodel, display in self._models.get(out.make, [])
                if nmodel and (m := re.search(rf"\b{re.escape(nmodel)}\b", raw))
            ]
            if candidates:
                _, _, display, nmodel = min(candidates)
                out.model = display
                take(nmodel)

        # 4. Province, on what the marque and model did not claim. Longest name
        #    first so "Santa Cruz de Tenerife" is not shadowed by a shorter match
        #    inside it.
        for key in sorted(self._provinces, key=len, reverse=True):
            if re.search(rf"\b{re.escape(key)}\b", raw):
                out.province_code, out.province_name = self._provinces[key]
                take(key)
                break

        # 5. A bare year, but ONLY here — after the model has had its chance.
        #
        # "peugeot 2008" and "seat leon 2020" are the same shape and mean opposite
        # things: one is a model, the other a year. Reading four digits as a year up
        # front would have eaten the 2008, the 3008 and the 5008 out of Peugeot's
        # range. Waiting until the model is resolved makes the ambiguity resolve
        # itself — whatever the model did not claim is a year.
        #
        # Exact, not "from". Someone writing "León 2020" means a 2020 León; the
        # open-ended reading has its own words ("desde 2020") and they are matched
        # earlier.
        if out.year_min is None and out.year_max is None:
            m = re.search(r"\b(19\d{2}|20[0-4]\d)\b", raw)
            if m:
                out.year_min = out.year_max = int(m.group(1))
                take(m.group(1))

        # 6. Anything left that is not filler. Reported, never guessed at.
        out.unresolved = [
            w for w in raw.split()
            if w and w not in _STOPWORDS and not w.isdigit() and len(w) > 1
        ]
        return out

    @staticmethod
    def _take_bounds(raw: str, out: ParsedQuery, take) -> str:
        """Price, kilometres and year bounds, in the shapes Spanish states them."""
        patterns: list[tuple[str, str]] = [
            # price
            (rf"(?:por\s+)?menos de {_NUM}\s*(?:euros?|eur|€)", "price_max"),
            (rf"(?:por\s+)?(?:hasta|maximo|max) {_NUM}\s*(?:euros?|eur|€)", "price_max"),
            (rf"{_NUM}\s*(?:euros?|eur|€) o menos", "price_max"),
            (rf"(?:mas de|desde|minimo) {_NUM}\s*(?:euros?|eur|€)", "price_min"),
            # kilometres
            (rf"(?:con\s+)?menos de {_NUM}\s*(?:km|kms|kilometros)", "km_max"),
            (rf"(?:hasta|maximo|max) {_NUM}\s*(?:km|kms|kilometros)", "km_max"),
            (rf"(?:mas de|desde) {_NUM}\s*(?:km|kms|kilometros)", "km_min"),
            # year — anchored to four digits so a price never lands here
            (r"(?:desde|a partir de|del?) (19\d{2}|20\d{2})", "year_min"),
            (r"(?:hasta|antes de) (19\d{2}|20\d{2})", "year_max"),
            (r"(?:de|del) (19\d{2}|20\d{2})", "year_min"),
        ]
        for pattern, field_name in patterns:
            if getattr(out, field_name) is not None:
                continue
            m = re.search(pattern, raw)
            if m:
                setattr(out, field_name, _to_int(m.group(1)))
                take(m.group(0))
                raw = raw.replace(m.group(0), " ", 1)

        # A bare price with no unit ("por 15000") is deliberately NOT matched: it is
        # indistinguishable from a kilometre figure or a model number, and guessing
        # which would be exactly the kind of confident error this module exists to
        # avoid.
        return raw
