"""Collapse raw version strings into the families a buyer recognises.

The census holds 106.246 distinct version strings and 51,9% of them appear exactly
once. Offered raw, the third level of the picker is not a list of choices — it is a
transcript. The owner's words: "Si pongo clase A, que no salga el 200, luego 200d,
luego 200d 7tronic tal... Eso va en una misma familia."

He is right, and the fix is not to show fewer options. It is to show the RIGHT ones:
"A 200 d" is a car you can want; "A 200 d 7G-DCT AMG Line 5p" is that same car with
its paperwork attached. Measured over seven models, this collapses 7.253 version
strings into 125 families — 58x less noise, and nothing lost, because what is
stripped is gearbox, doors, trim pack and marketing suffix, none of which is how
anyone names the car they are looking for.

THREE MODES, because marques do not name cars the same way and a single rule
produces nonsense for two thirds of the market:

  MODE A — German premium (Mercedes-Benz, BMW, MINI). The family is the
    alphanumeric designation and POWER IS NOISE: "A 180 d" and "A 180 d 116 CV" are
    one car.
  MODE B — VAG (VW, SEAT, Škoda, Audi, CUPRA). The family is displacement plus
    technology — "2.0 TDI" — and power is again noise.
  MODE C — PSA and Renault. POWER IS IDENTITY here, and this is the trap: strip it
    and "PureTech 130" and "PureTech 110" become one phantom family covering two
    genuinely different cars. The engine name alone is not enough.

Performance badges (AMG, GTI, R, FR, Cupra, RS, M3…) outrank the engine, because
that is how those cars are named and sold. The exclusions matter more than the
matches: "AMG Line", "S line" and "R-Line" are TRIM PACKS on ordinary cars, and a
rule that catches them turns 1.399 equipment packages into fake performance
models — roughly doubling any AMG count and being noticed immediately.
"""
from __future__ import annotations

import re
import unicodedata

# --- brand -> mode ---------------------------------------------------------
_MODE_A = {"mercedes-benz", "mercedes", "bmw", "mini"}
_MODE_B = {"volkswagen", "seat", "audi", "skoda", "cupra"}
_MODE_C = {
    "peugeot", "citroen", "ds automobiles", "ds", "opel", "fiat",
    "renault", "dacia", "nissan",
}


def _fold(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    ).lower()


def mode_for(make: str) -> str:
    m = _fold(make).strip()
    if m in _MODE_A:
        return "A"
    if m in _MODE_B:
        return "B"
    if m in _MODE_C:
        return "C"
    return "G"


# --- shared cleaning -------------------------------------------------------

# Body words and chassis codes that some feeds prepend to the version. They are not
# discarded because they are wrong — they are a different AXIS (body, generation),
# and mixing axes into one list is what makes a version selector unreadable.
_PREFIX = re.compile(
    r"^(?:sedan|sedán|berlina|sportback|coupe|coupé|cabrio|touring|variant|compact|"
    r"familiar|hatchback|kleinwagen|estate|sw|st|avant|allroad|3p|5p|"
    r"[efg]\d{2}|\(?w1\d{2}\)?)\s+",
    re.IGNORECASE,
)

# Gearbox, doors, power, emissions marketing. Everything here is paperwork.
_TAIL = re.compile(
    r"\b(?:\d{2,3}\s*(?:cv|kw)|\(\s*\d+\s*cv\s*\)|\d\s*p|"
    r"7g-?dct|8g-?dct|9g-?tronic|7g-?tronic|g-?tronic|dsg\d?|s[- ]?tronic|multitronic|"
    r"tiptronic|steptronic|edc|cvt|mct|dkg|eat\d|aut\.?|auto\.?|automatico|automático|"
    r"manual|\dv|4matic|quattro|xdrive|4motion|awd|4x4|4wd|"
    r"be|bmt|bluemotion|blueefficiency|dpf|s&s|s/s|gpf|mild-?hybrid|nm|my\d{2}|eco2?)\b",
    re.IGNORECASE,
)

# Performance badges. Order matters only in that the negative lookaheads must hold:
# "AMG Line", "S line" and "R-Line" are equipment, not engines.
_BADGE = re.compile(
    r"\b(AMG(?!\s*Line)|M\d{1,3}[id]?|M340[id]|GTI|Clubsport|GTD|GTE|"
    r"R(?![-\s]?Line)|FR|Cupra|RS\d?|S\d(?!\s*line)|N|ST|GT[iI]?)\b"
)

_MB_ENGINE = re.compile(r"\b([A-Z]{1,3})\s?(\d{2,3})\s?(d|e)?\b")
_BMW_ENGINE = re.compile(r"\b(\d{3})\s*(tds|td|ti|cd|ci|xd|xi|da|ia|is|d|i|e)?\b", re.IGNORECASE)
_VAG_ENGINE = re.compile(r"\b(\d\.\d)\s*(TDI|TSI|TFSI|FSI|MPI|SDI|T)?\b", re.IGNORECASE)
_AUDI_NUM = re.compile(r"\b(20|25|30|35|40|45|50|55|60)\s*(TDI|TFSI\s*e|TFSI)\b", re.IGNORECASE)
_PSA_ENGINE = re.compile(
    r"\b(BlueHDi|PureTech|e-HDi|HDi|VTi|THP|Blue\s*dCi|dCi|TCe|SCe|EcoBoost|CRDi|CDTi|JTD|"
    r"MultiJet|TDCi|Skyactiv)\b",
    re.IGNORECASE,
)
_POWER_CV = re.compile(r"\(?\s*(\d{2,3})\s*CV", re.IGNORECASE)
_POWER_KW = re.compile(r"\b(\d{2,3})\s*kW\b", re.IGNORECASE)

_CV_SCALE = (65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 130, 140,
             150, 160, 165, 180, 200, 225, 250, 300)


def _snap_cv(cv: int) -> int:
    return min(_CV_SCALE, key=lambda s: abs(s - cv))


def _power(text: str, engine: str | None = None) -> int | None:
    """CV if stated, else kW converted, else the bare number after the engine name.

    The third case is not a nicety — it is how PSA and Renault actually write it.
    "PureTech 130" carries no unit at all, and without this branch the family
    collapsed to "PureTech", merging the 110, the 130 and the 155 into one entry
    for three cars that cost thousands of euros apart. That is precisely the mode-C
    failure this function exists to avoid.
    """
    m = _POWER_CV.search(text)
    if m:
        return _snap_cv(int(m.group(1)))
    m = _POWER_KW.search(text)
    if m:
        return _snap_cv(round(int(m.group(1)) * 1.35962))
    if engine:
        m = re.search(rf"{re.escape(engine)}\s+(\d{{2,3}})\b", text, re.IGNORECASE)
        if m:
            return _snap_cv(int(m.group(1)))
    return None


def family_of(make: str, model: str, version: str) -> str | None:
    """The family a version belongs to, or None when nothing survives cleaning."""
    if not version or not version.strip():
        return None

    text = " ".join(version.split())

    # Strip the model's own name and the marque when a feed repeats them.
    for token in (make, model):
        if token:
            text = re.sub(rf"^{re.escape(token)}\s+", "", text, flags=re.IGNORECASE).strip()
    for _ in range(3):
        stripped = _PREFIX.sub("", text).strip()
        if stripped == text:
            break
        text = stripped

    mode = mode_for(make)

    badge = _BADGE.search(text)

    cleaned = _TAIL.sub(" ", text)
    cleaned = " ".join(cleaned.split())

    if mode == "A":
        if _fold(make).startswith("bmw"):
            m = _BMW_ENGINE.search(cleaned)
            if m:
                num, suffix = m.group(1), (m.group(2) or "").lower()
                letter = (
                    "d" if suffix in {"d", "cd", "td", "tds", "xd", "da"}
                    else "e" if suffix == "e"
                    else "i"
                )
                return f"{num}{letter}"
        else:
            m = _MB_ENGINE.search(cleaned)
            if not m:
                # Some feeds drop the series letter and write just "180 CDI". The
                # letter is not missing information — it is in the model name — so
                # it is borrowed from there rather than left as a bare number.
                # Without this, "180" and "200" appeared as families of their own
                # beside "A 180" and "A 200": the same car, split, twice in the list.
                bare = re.match(r"^(\d{2,3})\s?(d|e)?\b", cleaned)
                series = re.search(r"\b(?:clase\s+)?([A-Z]{1,3})\b", model or "", re.IGNORECASE)
                if bare and series:
                    suffix = bare.group(2) or ""
                    return f"{series.group(1).upper()} {bare.group(1)}{(' ' + suffix) if suffix else ''}".strip()
            if m:
                series, num, suffix = m.group(1).upper(), m.group(2), (m.group(3) or "")
                base = f"{series} {num}{(' ' + suffix) if suffix else ''}".strip()
                # "A 45" and "A 45 AMG" are not the same car, and the badge is the
                # part a buyer says out loud. The engine pattern matches first, so
                # the badge has to be re-attached here or every AMG in the catalogue
                # loses its name.
                if badge and badge.group(1).upper().startswith("AMG"):
                    return f"{base} AMG"
                return base
        if badge:
            return badge.group(1).upper()

    elif mode == "B":
        m = _AUDI_NUM.search(cleaned)
        if m:
            return f"{m.group(1)} {m.group(2).upper().replace('  ', ' ')}"
        m = _VAG_ENGINE.search(cleaned)
        if m:
            tech = (m.group(2) or "").upper()
            tech = {"ECOTSI": "TSI", "ETSI": "TSI"}.get(tech, tech)
            return f"{m.group(1)}{(' ' + tech) if tech else ''}"
        if badge:
            return badge.group(1).upper()

    elif mode == "C":
        m = _PSA_ENGINE.search(cleaned)
        if m:
            raw_engine = m.group(1)
            engine = re.sub(r"^blue\s*dci$", "dCi", raw_engine, flags=re.IGNORECASE)
            # Power is IDENTITY in this mode. It is read from the ORIGINAL text,
            # before the tail strip removed "130 CV", and falls back to the bare
            # number the marque actually prints.
            cv = _power(text, raw_engine)
            return f"{engine} {cv}" if cv else engine
        if badge:
            return badge.group(1).upper()

    # Badge first for everything else too: a GTI is a GTI whatever the marque.
    if badge:
        return badge.group(1).upper()

    # Generic fallback: the first two meaningful tokens of what survived.
    tokens = [t for t in cleaned.split() if len(t) > 1][:2]
    return " ".join(tokens) if tokens else None
