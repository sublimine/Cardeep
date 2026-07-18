"""DGT alpha province code -> Cardeep INE numeric province code mapping.

DGT's ``COD_PROVINCIA_VEH`` field (the historic vehicle-registration-plate province
letter, e.g. 'M' for Madrid, 'B' for Barcelona) is NOT the same code space as
Cardeep's ``geo_province.code`` (2-digit INE numeric, e.g. '28' for Madrid). This is
a genuine finding of F4 (01-market-intelligence) — the carta's §5 design did not
anticipate a code-space mismatch, only a schema-shape [ASUMIDO].

Built from TWO independent primary sources, cross-referenced by province name:
  1. The official DGT "Documento de interfaz de Envío de Datos (Transferencias)"
     PDF, Anexo I §1.3.6 COD_PROVINCIA_VEH (fetched 2026-07-18).
  2. A live ``SELECT code, name FROM geo_province`` against cardeep-pg (2026-07-18).

DS ("Desconocido") and EX ("Extranjero") are DGT sentinels with no corresponding
Cardeep province — deliberately absent from this dict (never guessed); callers must
treat a missing key as "unmapped", storing NULL, not silently choosing a fallback.
"""
from __future__ import annotations

DGT_PROVINCE_TO_INE: dict[str, str] = {
    "VI": "01",  # Araba/Álava
    "AB": "02",  # Albacete
    "A":  "03",  # Alicante/Alacant
    "AL": "04",  # Almería
    "AV": "05",  # Ávila
    "BA": "06",  # Badajoz
    "IB": "07",  # Balears (Illes)
    "B":  "08",  # Barcelona
    "BU": "09",  # Burgos
    "CC": "10",  # Cáceres
    "CA": "11",  # Cádiz
    "CS": "12",  # Castellón/Castelló
    "CR": "13",  # Ciudad Real
    "CO": "14",  # Córdoba
    "C":  "15",  # Coruña (A)
    "CU": "16",  # Cuenca
    "GI": "17",  # Girona
    "GR": "18",  # Granada
    "GU": "19",  # Guadalajara
    "SS": "20",  # Gipuzkoa
    "H":  "21",  # Huelva
    "HU": "22",  # Huesca
    "J":  "23",  # Jaén
    "LE": "24",  # León
    "L":  "25",  # Lleida
    "LO": "26",  # Rioja (La)
    "LU": "27",  # Lugo
    "M":  "28",  # Madrid
    "MA": "29",  # Málaga
    "MU": "30",  # Murcia
    "NA": "31",  # Navarra
    "OU": "32",  # Ourense
    "O":  "33",  # Asturias
    "P":  "34",  # Palencia
    "GC": "35",  # Palmas (Las)
    "PO": "36",  # Pontevedra
    "SA": "37",  # Salamanca
    "TF": "38",  # Santa Cruz de Tenerife
    "S":  "39",  # Cantabria
    "SG": "40",  # Segovia
    "SE": "41",  # Sevilla
    "SO": "42",  # Soria
    "T":  "43",  # Tarragona
    "TE": "44",  # Teruel
    "TO": "45",  # Toledo
    "V":  "46",  # Valencia/València
    "VA": "47",  # Valladolid
    "BI": "48",  # Bizkaia
    "ZA": "49",  # Zamora
    "Z":  "50",  # Zaragoza
    "CE": "51",  # Ceuta
    "ML": "52",  # Melilla
}

# DGT sentinels with no geographic mapping (deliberately excluded from the dict
# above; listed here so a lookup miss can be classified as "known sentinel" vs
# "genuinely unexpected code" for QC/alerting purposes).
DGT_NON_GEOGRAPHIC_CODES: frozenset[str] = frozenset({"DS", "EX"})


def map_province(dgt_code: str | None) -> str | None:
    """Map a raw DGT province code to Cardeep's INE code, or None if unmapped.

    Never raises — an unrecognized code (including DS/EX, or a genuinely unexpected
    value never seen in the Anexo I table) returns None, and the caller stores NULL
    rather than guessing.
    """
    if dgt_code is None:
        return None
    return DGT_PROVINCE_TO_INE.get(dgt_code.strip())
