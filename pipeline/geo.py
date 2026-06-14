"""Resolve province/municipality names to INE codes against the geo backbone.

Builds an in-memory index once per run. Matching is accent/case insensitive,
order-insensitive (token-sorted, so "La Rioja" == "Rioja, La"), handles
bilingual INE names, and carries a curated alias table for island/variant
province names that no normalization can bridge (e.g. Menorca -> Balears).

Resolution cascade (all lookups scoped to province — never cross-province):
  1. Exact    : normalised key in geo_municipality index.
  2. Fuzzy    : rapidfuzz WRatio >= 88 with two guards:
                  - query must be >= 4 chars (blocks bare articles like 'la'/'el')
                  - candidate must be >= max(4, len(query)//3) chars
                  (divisor=3 allows 'Palma' to match 'Palma de Mallorca')
  3. Locality : INE Nomenclátor of singular entities / population nuclei
                (~63 k locality->municipality pairs) loaded from
                data/geo/nomenclator_entidades_ine.csv at startup.
               Source: github.com/inigoflores/ds-codigos-postales-ine-es
               (derived from official INE Nomenclátor, MIT-compatible CC0).
"""
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

import asyncpg

# ---------------------------------------------------------------------------
# Tuning constants — validated by B4.1 probe (0 false positives at these values)
# ---------------------------------------------------------------------------
_FUZZY_CUTOFF: int = 88

# Minimum characters in the *query* before fuzzy is attempted.
# Prevents 'la' / 'las' / 'el' (len 2-3) from matching long municipality names via
# WRatio token-overlap (WRatio('las', 'las rozas de madrid') == 90).
_FUZZY_QUERY_MIN_LEN: int = 4

# Candidate length guard: candidate must have at least max(_FLOOR, len(query)//3) chars.
# Ratio 1/3 allows 'palma' (5 chars) to be a valid candidate for 'palma de mallorca' (17).
# The original probe used //2 which incorrectly excluded that case; //3 is correct.
_FUZZY_CAND_LEN_DIVISOR: int = 3
_FUZZY_CAND_LEN_FLOOR: int = 4

# Absolute path to the locality gazetteer CSV shipped with the repo
_GAZETTEER_PATH: Path = (
    Path(__file__).resolve().parent.parent / "data" / "geo" / "nomenclator_entidades_ine.csv"
)


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _sorted_key(text: str) -> str:
    return " ".join(sorted(_norm(text).split()))


# Province-name variants that normalization alone cannot bridge -> INE province code.
_PROVINCE_ALIASES: dict[str, str] = {
    "alava": "01", "araba": "01",
    "menorca": "07", "mallorca": "07", "ibiza": "07", "eivissa": "07",
    "formentera": "07", "islas baleares": "07", "illes balears": "07",
    "a coruna": "15", "la coruna": "15",
    "guipuzcoa": "20", "gipuzkoa": "20",
    "las palmas": "35", "gran canaria": "35", "fuerteventura": "35", "lanzarote": "35",
    "la rioja": "26",
    "vizcaya": "48", "bizkaia": "48",
    "gerona": "17", "lerida": "25", "orense": "32",
    "tenerife": "38", "santa cruz de tenerife": "38",
    "castellon": "12", "castello": "12",
}


def _load_gazetteer() -> dict[str, dict[str, str]]:
    """Load INE Nomenclátor locality -> municipality index into memory.

    Returns a dict[province_code, dict[locality_norm_key, municipality_code5]].
    Both *entidad_singular_nombre* and *nucleo_nombre* are indexed; duplicates
    within the same province map to the same municipality (the CSV guarantees
    locality names are unambiguous within a given municipality, and the province
    constraint already scopes resolution safely).

    Entries with name '*Diseminado*' are skipped (they have no useful locality
    name to match against).

    Source CSV columns (header row 0):
      codigo_postal, municipio_id, municipio_nombre,
      codigo_unidad_poblacional, entidad_singular_nombre, nucleo_nombre
    """
    index: dict[str, dict[str, set[str]]] = {}

    if not _GAZETTEER_PATH.exists():
        # Non-fatal: fuzzy still works; locality resolution unavailable.
        return index

    with _GAZETTEER_PATH.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            muni_code: str = row["municipio_id"].strip()
            if len(muni_code) != 5:
                continue
            prov_code: str = muni_code[:2]
            d = index.setdefault(prov_code, {})

            for field in ("entidad_singular_nombre", "nucleo_nombre"):
                raw: str = row.get(field, "").strip()
                if not raw:
                    continue
                raw_norm = _norm(raw)
                # Skip "Diseminado" / "*Diseminado*" — these are dispersed-area markers
                # in the INE Nomenclátor, not useful locality names to match against.
                # The marker appears both with asterisks ('*Diseminado*') and without
                # ('Diseminado') depending on the data vintage; normalise-and-compare.
                if raw_norm == "diseminado":
                    continue
                for key in (raw_norm, _sorted_key(raw)):
                    if key:
                        # Accumulate EVERY municipality a locality name maps to within the
                        # province, so a generic name shared by several ('San Martín',
                        # 'Santa María') is recognised as ambiguous downstream instead of
                        # being silently bound to whichever row was read first.
                        d.setdefault(key, set()).add(muni_code)

    return index


class GeoResolver:
    def __init__(self) -> None:
        self._muni: dict[str, dict[str, str]] = {}          # prov_code -> {muni key: code5}
        self._prov: dict[str, str] = {}                     # province key -> code2
        self._city_global: dict[str, set[tuple[str, str]]] = {}  # muni key -> {(prov, code5)}
        self._locality: dict[str, dict[str, set[str]]] = {}  # prov_code -> {locality key: {code5}}
        # _muni_names[prov_code] stores the list of (canonical_norm_key, code5) for fuzzy matching
        self._muni_names: dict[str, list[tuple[str, str]]] = {}

    def _index_prov(self, name: str, code: str) -> None:
        self._prov.setdefault(_norm(name), code)
        self._prov.setdefault(_sorted_key(name), code)
        for part in re.split(r"[/,]", name):
            p = _norm(part)
            if p:
                self._prov.setdefault(p, code)

    @classmethod
    async def load(cls, conn: asyncpg.Connection) -> "GeoResolver":
        self = cls()
        for r in await conn.fetch("SELECT code, name FROM geo_province"):
            self._index_prov(r["name"], r["code"])
        for k, v in _PROVINCE_ALIASES.items():
            self._prov.setdefault(k, v)
        for r in await conn.fetch("SELECT code, name, province_code FROM geo_municipality"):
            d = self._muni.setdefault(r["province_code"], {})
            keys: set[str] = {_norm(r["name"]), _sorted_key(r["name"])}
            for part in re.split(r"[/,]", r["name"]):
                p = _norm(part)
                # Skip bare articles / prepositions that appear as isolated fragments
                # from bilingual names like "Acebeda, La" or "Rozas de Madrid, Las".
                # These 2-3 character tokens ('la', 'las', 'el', 'los', 'de', 'sa', 'es')
                # would otherwise match any city payload that starts with those strings.
                if p and len(p) >= 4:
                    keys.add(p)
            for k in keys:
                d.setdefault(k, r["code"])
                self._city_global.setdefault(k, set()).add((r["province_code"], r["code"]))

        # Build fuzzy candidate list per province: unique (norm_key, code5) pairs.
        # We use the normalised primary key only (not sorted_key) to avoid duplicate
        # candidates that would inflate the list with no additional coverage.
        for prov_code, d in self._muni.items():
            # Deduplicate: multiple norm-keys may map to the same code; keep all keys
            # because fuzzy matching needs the full name variant to score correctly.
            self._muni_names[prov_code] = list(d.items())

        # Load INE Nomenclátor locality gazetteer (in-memory, ~63k pairs)
        self._locality = _load_gazetteer()

        return self

    # ------------------------------------------------------------------
    # Public API — signatures unchanged (B4 contract)
    # ------------------------------------------------------------------

    def resolve_city_global(self, city: str | None) -> tuple[str | None, str | None]:
        """Resolve a bare city name to (province_code, municipality_code) only when it
        maps to exactly one municipality nationally (unambiguous). Else (None, None)."""
        if not city:
            return (None, None)
        hits = self._city_global.get(_norm(city)) or self._city_global.get(_sorted_key(city))
        if hits and len(hits) == 1:
            prov, code = next(iter(hits))
            return (prov, code)
        return (None, None)

    def province_code(self, name_or_code: str | None) -> str | None:
        if not name_or_code:
            return None
        s = str(name_or_code).strip()
        if s.isdigit():
            c = s.zfill(2)
            return c if c in self._muni else None
        return self._prov.get(_norm(s)) or self._prov.get(_sorted_key(s))

    def municipality_code(self, province_code: str | None, muni_name: str | None) -> str | None:
        """Resolve a municipality name to its 5-digit INE code within a province.

        Cascade (all scoped strictly to *province_code*):
          1. Exact match on normalised / token-sorted key.
          2. Fuzzy match: rapidfuzz WRatio >= 88 with query/candidate length guards.
          3. INE Nomenclátor locality lookup (pedanías, parroquias, barrios).
        Returns None if no step resolves.
        """
        if not province_code or not muni_name:
            return None

        d = self._muni.get(province_code, {})

        # Step 1 — exact (original behaviour, zero regression)
        exact = d.get(_norm(muni_name)) or d.get(_sorted_key(muni_name))
        if exact:
            return exact

        # Step 2 — fuzzy
        code = self._fuzzy_match(province_code, muni_name)
        if code:
            return code

        # Step 3 — INE Nomenclátor locality gazetteer
        return self._locality_match(province_code, muni_name)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fuzzy_match(self, province_code: str, muni_name: str) -> str | None:
        """Fuzzy match *muni_name* against official municipality names in *province_code*.

        Two province-scoped tiers:

          A. Token-subset (ambiguity-safe). If the query's tokens are a subset of EXACTLY
             ONE municipality name, it is a confident short-form/prefix match
             ('Burgo de Osma' -> 'Burgo de Osma-Ciudad de Osma'). If they are a subset of
             TWO OR MORE distinct municipalities ('San Martín' ⊆ both 'San Martín del Rey
             Aurelio' and 'San Martín de Oscos'), the bare name is genuinely ambiguous ->
             return None ("better a hole than a lie"). WRatio cannot catch this: it breaks
             such ties artificially by length, so the subset test must run first.
          B. WRatio fallback, only when the query is NOT a subset of any municipality
             (richer or variant forms: 'Palma de Mallorca' -> 'Palma', 'Orense' ->
             'Ourense'). Guards: query >= _FUZZY_QUERY_MIN_LEN; candidate length floor;
             score >= _FUZZY_CUTOFF. Validated by the B4.1 probe (0 false positives).
        """
        candidates = self._muni_names.get(province_code)
        if not candidates:
            return None

        query_norm = _norm(muni_name)
        if not query_norm or len(query_norm) < _FUZZY_QUERY_MIN_LEN:
            return None

        # Tier A — token-subset ambiguity guard (must precede scoring).
        query_tokens = set(query_norm.split())
        supersets = {
            code for key, code in candidates
            if query_tokens <= set(key.split())
        }
        if len(supersets) >= 2:
            return None                      # ambiguous short form -> confess the gap
        if len(supersets) == 1:
            return next(iter(supersets))     # unique superset -> confident prefix match

        # Tier B — WRatio fallback (query is not a token-subset of any municipality).
        try:
            from rapidfuzz.process import extractOne
            from rapidfuzz.fuzz import WRatio
        except ImportError:
            return None

        min_cand_len = max(_FUZZY_CAND_LEN_FLOOR, len(query_norm) // _FUZZY_CAND_LEN_DIVISOR)
        eligible: list[tuple[str, str]] = [
            (key, code) for key, code in candidates
            if len(key) >= min_cand_len
        ]
        if not eligible:
            return None

        keys = [key for key, _ in eligible]
        result = extractOne(
            query_norm, keys, scorer=WRatio, processor=None,
            score_cutoff=_FUZZY_CUTOFF,
        )
        if result is None:
            return None
        _best_key, _score, idx = result
        return eligible[idx][1]

    def _locality_match(self, province_code: str, locality_name: str) -> str | None:
        """Look up a pedanía / parroquia / barrio name in the INE Nomenclátor index.

        A locality name that maps to MORE THAN ONE municipality within the province
        (generic names like 'San Martín' or 'Santa María' that recur as hamlets across
        many municipalities) is ambiguous -> return None rather than bind it to an
        arbitrary one ("better a hole than a lie")."""
        loc_index = self._locality.get(province_code, {})
        if not loc_index:
            return None
        codes = loc_index.get(_norm(locality_name)) or loc_index.get(_sorted_key(locality_name))
        if codes and len(codes) == 1:
            return next(iter(codes))
        return None
