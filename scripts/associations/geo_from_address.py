"""Extract (postcode, town, province) from free-form Spanish dealer addresses and
resolve to INE province_code + municipality_code via the live geo tables.

Handles the two AEDRA formats plus generic comma forms:
  'POLG. SARATXO P. 5-6 -01470 - AMURRIO -ALAVA'
  'Mare de Deu de Nuria, 1, 08830, Sant Boi de Llobregat, BARCELONA'
  'C/ ZABAL BAJO, 22 - LA LINEA 11300- CADIZ'
"""
from __future__ import annotations

import re

from dedup_upsert import normalize_name  # type: ignore

# Province-name -> INE code aliases for tokens that are NOT exact geo_province names
# (island / historical / bilingual variants seen in association data).
PROV_TOKEN = {
    "alava": "01", "araba": "01", "albacete": "02", "alicante": "03", "alacant": "03",
    "almeria": "04", "avila": "05", "badajoz": "06", "baleares": "07", "balears": "07",
    "islasbaleares": "07", "illesbalears": "07", "mallorca": "07", "palmademallorca": "07",
    "palma": "07", "menorca": "07", "ibiza": "07", "eivissa": "07", "barcelona": "08",
    "burgos": "09", "caceres": "10", "cadiz": "11", "castellon": "12", "castello": "12",
    "ciudadreal": "13", "cordoba": "14", "coruna": "15", "lacoruna": "15", "acoruna": "15",
    "cuenca": "16", "girona": "17", "gerona": "17", "granada": "18", "guadalajara": "19",
    "guipuzcoa": "20", "gipuzkoa": "20", "huelva": "21", "huesca": "22", "jaen": "23",
    "leon": "24", "lleida": "25", "lerida": "25", "larioja": "26", "rioja": "26",
    "logrono": "26", "lugo": "27", "madrid": "28", "malaga": "29", "murcia": "30",
    "navarra": "31", "nafarroa": "31", "ourense": "32", "orense": "32", "asturias": "33",
    "oviedo": "33", "palencia": "34", "laspalmas": "35", "palmas": "35",
    "grancanaria": "35", "fuerteventura": "35", "lanzarote": "35", "pontevedra": "36",
    "vigo": "36", "salamanca": "37", "santacruzdetenerife": "38", "tenerife": "38",
    "lapalma": "38", "gomera": "38", "hierro": "38", "cantabria": "39", "santander": "39",
    "segovia": "40", "sevilla": "41", "soria": "42", "tarragona": "43", "teruel": "44",
    "toledo": "45", "valencia": "46", "valladolid": "47", "vizcaya": "48", "bizkaia": "48",
    "bilbao": "48", "zamora": "49", "zaragoza": "50", "ceuta": "51", "melilla": "52",
    # broad island grouping fallbacks
    "islascanarias": None,  # ambiguous (35 or 38) -> resolve by town later
    "canarias": None,
}

POSTCODE_RE = re.compile(r"\b(\d{5})\b")


def _split_tokens(addr: str):
    # normalise separators: commas and dashes both delimit the tail (town/province)
    a = addr.replace("–", "-").replace("—", "-")
    parts = re.split(r"[,]", a)
    return [p.strip() for p in parts if p.strip()]


def parse_address(addr: str):
    """Return dict(postcode, town, province_token)."""
    if not addr:
        return {"postcode": None, "town": None, "province_token": None}
    m = POSTCODE_RE.search(addr)
    postcode = m.group(1) if m else None
    province_token = None
    town = None

    parts = _split_tokens(addr)
    if len(parts) >= 2:
        # comma form: ... , TOWN , PROVINCE   (province is last segment)
        province_token = parts[-1]
        town = parts[-2]
        # town segment may carry the postcode ('17200 Palafrugell') -> strip it
        town = POSTCODE_RE.sub("", town).strip(" -")
        # ACEVAS form: 'STREET  TOWN,  PROVINCE ZIP' -> only 2 parts, town is the
        # tail of the FIRST part after a double space, province is in the last part.
        if len(parts) == 2 and re.search(r"\s{2,}", parts[0]):
            head_tail = re.split(r"\s{2,}", parts[0])[-1].strip()
            if head_tail:
                town = POSTCODE_RE.sub("", head_tail).strip(" -")
            province_token = POSTCODE_RE.sub("", parts[1]).strip(" -.")
    else:
        # dash-only form: 'STREET -PC - TOWN -PROVINCE'
        chunks = [c.strip() for c in re.split(r"-", addr) if c.strip()]
        if len(chunks) >= 2:
            province_token = chunks[-1]
            town = POSTCODE_RE.sub("", chunks[-2]).strip()
    # if province token still contains the town merged ('LA LINEA 11300'), the real
    # province is in the FINAL dash chunk handled above; otherwise clean it.
    if province_token:
        province_token = POSTCODE_RE.sub("", province_token).strip(" -.")
    return {"postcode": postcode, "town": town, "province_token": province_token}


def resolve(geo, addr: str, province_hint: str | None = None):
    """Return (province_code, municipality_code, postcode)."""
    p = parse_address(addr or "")
    prov_code = None
    # 1) explicit province token
    for cand in (p["province_token"], province_hint):
        if not cand:
            continue
        key = normalize_name(cand)
        if key in PROV_TOKEN and PROV_TOKEN[key]:
            prov_code = PROV_TOKEN[key]
            break
        gc = geo.province(cand)
        if gc:
            prov_code = gc
            break
    # Fallback: province may be the final dash- or comma-delimited token even when
    # the structured parse picked the wrong segment (street carries commas).
    if not prov_code:
        tail_tokens = [t.strip(" -.") for t in re.split(r"[,\-]", addr) if t.strip(" -.")]
        for cand in reversed(tail_tokens[-3:]):
            key = normalize_name(cand)
            if key in PROV_TOKEN and PROV_TOKEN[key]:
                prov_code = PROV_TOKEN[key]
                break
            gc = geo.province(cand)
            if gc:
                prov_code = gc
                break
    muni_code = None
    if p["town"] and prov_code:
        muni_code = geo.municipality(p["town"], prov_code)
        # ACEVAS-style: town sits as the double-space tail of the penultimate
        # comma segment ('km 28  COLMENAR VIEJO'). Retry with that tail.
        if not muni_code:
            parts = _split_tokens(addr)
            for seg in (parts[-2] if len(parts) >= 2 else "", p["town"]):
                if not seg:
                    continue
                tail = re.split(r"\s{2,}", seg)[-1].strip()
                tail = POSTCODE_RE.sub("", tail).strip(" -")
                if tail and tail != p["town"]:
                    mc = geo.municipality(tail, prov_code)
                    if mc:
                        muni_code = mc
                        break
    # 2) fall back: derive province from postcode prefix (first 2 digits = INE province)
    if not prov_code and p["postcode"]:
        pp = p["postcode"][:2]
        if pp in {f"{i:02d}" for i in range(1, 53)}:
            prov_code = pp
            if p["town"]:
                muni_code = geo.municipality(p["town"], prov_code)
    return prov_code, muni_code, p["postcode"]
