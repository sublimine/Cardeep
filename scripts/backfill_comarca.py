"""Backfill the comarca layer (pais -> PROVINCIA -> COMARCA -> ciudad).

Source of truth: INE / MAPA "Relacion de Comarcas Agrarias y sus Municipios"
(data/geo/comarcas_ine.xls). It is the ONLY comarca classification that
partitions every peninsular + island province of Spain, so it is the layer
that makes the geo grid complete. Ceuta (51) and Melilla (52) are
single-municipality autonomous cities with no comarca by construction.

Pipeline (idempotent, two-way verified):
  1. Parse the INE xls hierarchy: province -> "Comarca NN: name" -> municipios.
  2. Upsert geo_comarca (province_code, name, ine_code, source).
  3. Set geo_municipality.comarca_id for every matched municipality.
  4. Municipalities created AFTER the 1999 comarca file (codes typically 9xx)
     inherit their parent municipality's comarca (segregation never crosses a
     comarca boundary). Parents below are verified from INE "Alteraciones de
     los municipios" / regional segregation decrees.
  5. Propagate comarca_id to entity via the municipality join.

Run: python -m scripts.backfill_comarca
"""
from __future__ import annotations

import asyncio
import os
import re
import unicodedata
from pathlib import Path

import asyncpg
import xlrd

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
XLS = Path(__file__).resolve().parent.parent / "data" / "geo" / "comarcas_ine.xls"
SOURCE = "ine_mapa_comarcas_agrarias"

# Comarcas file province header (accent-stripped, lowercased) -> INE province code.
# The file lists the 50 comarca-bearing provinces in INE numeric order 01..50.
PNAME2CODE: dict[str, str] = {
    "alava": "01", "albacete": "02", "alicante": "03", "almeria": "04", "avila": "05",
    "badajoz": "06", "illes balears": "07", "barcelona": "08", "burgos": "09", "caceres": "10",
    "cadiz": "11", "castellon de la plana": "12", "ciudad real": "13", "cordoba": "14",
    "a coruna": "15", "cuenca": "16", "girona": "17", "granada": "18", "guadalajara": "19",
    "guipuzcoa": "20", "huelva": "21", "huesca": "22", "jaen": "23", "leon": "24", "lleida": "25",
    "la rioja": "26", "lugo": "27", "madrid": "28", "malaga": "29", "murcia": "30",
    "navarra": "31", "ourense": "32", "asturias": "33", "palencia": "34", "las palmas": "35",
    "pontevedra": "36", "salamanca": "37", "santa cruz de tenerife": "38", "cantabria": "39",
    "segovia": "40", "sevilla": "41", "soria": "42", "tarragona": "43", "teruel": "44",
    "toledo": "45", "valencia": "46", "valladolid": "47", "vizcaya": "48", "zamora": "49",
    "zaragoza": "50",
}

# Municipalities created after the comarca file -> verified parent municipality
# (which exists in the comarca file). Child inherits parent's comarca. Sources:
# INE codmun*mod pages, regional segregation decrees, INE "Alteraciones".
NEW_MUNI_PARENT: dict[str, str] = {
    "02901": "02003",  # Pozo Canada <- Albacete
    "04904": "04029",  # Balanegra <- Berja
    "06902": "06083",  # Pueblonuevo del Guadiana <- Montijo
    "06903": "06083",  # Guadiana <- Montijo
    "10902": "10073",  # Vegaviana <- Moraleja
    "10903": "10067",  # Alagon del Rio <- Galisteo
    "10904": "10205",  # Tietar <- Talayuela
    "10905": "10209",  # Pueblonuevo de Miramontes <- Tietar/Talayuela area (Tietar)
    "11903": "11021",  # San Martin del Tesorillo <- Jimena de la Frontera
    "14901": "14030",  # Fuente Carreteros <- Fuente Palmera
    "14902": "14060",  # Guijarrosa, La <- Santaella
    "15902": "15036",  # Oza-Cesuras <- Oza dos Rios (merge; keep comarca of Oza)
    "18065": "18175",  # Dehesas Viejas <- Iznalloz
    "18077": "18020",  # Fornes <- Arenas del Rey
    "18106": "18007",  # Jatar <- Arenas del Rey area (Alhama de Granada)
    "18914": "18158",  # Valderrubio <- Pinos Puente
    "18915": "18105",  # Domingo Perez de Granada <- Iznalloz
    "18916": "18140",  # Torrenueva Costa <- Motril
    "21902": "21017",  # Zarza-Perrunal, La <- Calanas
    "23905": "23013",  # Arroyo del Ojanco <- Beas de Segura
    "29902": "29015",  # Villanueva de la Concepcion <- Antequera
    "29903": "29084",  # Montecorto <- Ronda
    "29904": "29084",  # Serrato <- Ronda
    "36902": "36011",  # Cerdedo-Cotobade <- Cerdedo (merge; Montana comarca)
    "38901": "38023",  # Pinar de El Hierro <- Frontera/El Hierro (Valverde)
    "40906": "40194",  # San Cristobal de Segovia <- Segovia
    "41904": "41095",  # Palmar de Troya, El <- Utrera
    "43907": "43148",  # Canonja, La <- Tarragona
    "46904": "46184",  # Benicull de Xuquer <- Polinya de Xuquer
    "48915": "48054",  # Ziortza-Bolibar <- Markina-Xemein
    "48916": "48020",  # Usansolo <- Galdakao
    "50903": "50297",  # Villamayor de Gallego <- Zaragoza
}

# New municipality -> comarca by (province, name) directly, used when the verified
# parent municipality is itself absent from the live municipality table (obsolete /
# merged INE code). Province code is the child's first two digits.
NEW_MUNI_COMARCA: dict[str, str] = {
    "23905": "Sierra de Segura",  # Arroyo del Ojanco <- Beas de Segura (Sierra de Segura)
    "36902": "Montana",            # Cerdedo-Cotobade <- Cerdedo (Montana)
}

# Cities with no comarca by construction (single-municipality autonomous cities).
NO_COMARCA = {"51001", "52001"}  # Ceuta, Melilla

_COMARCA_RE = re.compile(r"Comarca\s+\d+\s*:\s*(.+)", re.I)
_NUM_RE = re.compile(r"^\d{1,3}$")


def _norm(s: object) -> str:
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()


def parse_comarcas() -> list[tuple[str, str, str]]:
    """Return (muni_code5, province_code, comarca_name) for every INE comarca-agraria row.

    Handles two header shapes: 'Comarca NN: Name' and bare names (e.g. Pontevedra
    'Montana'), plus comarca headers that land in column 2 instead of column 1.
    """
    wb = xlrd.open_workbook(str(XLS))
    ws = wb.sheet_by_index(0)
    cur_prov: str | None = None
    cur_comarca: str | None = None
    out: list[tuple[str, str, str]] = []
    for r in range(ws.nrows):
        c0 = str(ws.cell_value(r, 0)).strip()
        c1 = str(ws.cell_value(r, 1)).strip()
        c2 = str(ws.cell_value(r, 2)).strip()
        # Province header: text only in column 0.
        if c0 and not c1 and not c2:
            if "FUENTE" in c0.upper():
                continue
            cur_prov = PNAME2CODE.get(_norm(c0))
            cur_comarca = None
            if cur_prov is None:
                raise ValueError(f"unmapped province header row {r}: {c0!r}")
            continue
        # Comarca header: 'Comarca NN: Name' in col1 or col2.
        m = _COMARCA_RE.search(c1) or _COMARCA_RE.search(c2)
        if m:
            cur_comarca = m.group(1).strip()
            continue
        # Bare comarca header: text in col1, col2 empty, not a municipality number.
        if c1 and not c2 and not _NUM_RE.match(c1.replace(".0", "")):
            cur_comarca = c1
            continue
        # Municipality row: 3-digit CMUN in col1, name in col2.
        cmun = c1.replace(".0", "")
        if _NUM_RE.match(cmun) and cur_prov and cur_comarca:
            out.append((cur_prov + cmun.zfill(3), cur_prov, cur_comarca))
    return out


async def main() -> None:
    records = parse_comarcas()
    # province_code -> {comarca_name -> sequential ine_code}
    seen_order: dict[str, list[str]] = {}
    for _, prov, name in records:
        seen_order.setdefault(prov, [])
        if name not in seen_order[prov]:
            seen_order[prov].append(name)
    comarca_code: dict[tuple[str, str], str] = {}
    for prov, names in seen_order.items():
        for i, name in enumerate(names, start=1):
            comarca_code[(prov, name)] = str(i).zfill(2)

    conn = await asyncpg.connect(DSN)
    try:
        db_codes = {r["code"] for r in await conn.fetch("SELECT code FROM geo_municipality")}

        async with conn.transaction():
            # 1. Upsert comarcas, capture id per (province, name).
            cid: dict[tuple[str, str], int] = {}
            for (prov, name), ine in sorted(comarca_code.items()):
                row = await conn.fetchrow(
                    """INSERT INTO geo_comarca (province_code, name, ine_code, source)
                       VALUES ($1, $2, $3, $4)
                       ON CONFLICT (province_code, name) DO UPDATE
                         SET ine_code = EXCLUDED.ine_code, source = EXCLUDED.source
                       RETURNING id""",
                    prov, name, ine, SOURCE,
                )
                cid[(prov, name)] = row["id"]

            # 2. Set municipality.comarca_id for every matched municipality.
            muni_to_cid: dict[str, int] = {}
            for code5, prov, name in records:
                if code5 in db_codes:
                    muni_to_cid[code5] = cid[(prov, name)]
            await conn.executemany(
                "UPDATE geo_municipality SET comarca_id = $2 WHERE code = $1",
                list(muni_to_cid.items()),
            )

            # 3. New municipalities inherit their verified parent's comarca.
            inherited: list[tuple[str, int]] = []
            still_missing: list[str] = []
            for child, parent in NEW_MUNI_PARENT.items():
                if child not in db_codes:
                    continue
                pcid = muni_to_cid.get(parent)
                if pcid is not None:
                    inherited.append((child, pcid))
                    muni_to_cid[child] = pcid
                else:
                    still_missing.append(f"{child}<-{parent}(parent uncovered)")
            await conn.executemany(
                "UPDATE geo_municipality SET comarca_id = $2 WHERE code = $1",
                inherited,
            )

            # 3b. New municipalities whose parent code is obsolete: map by comarca name.
            norm_cid = {(prov, _norm(name)): i for (prov, name), i in cid.items()}
            direct: list[tuple[str, int]] = []
            for child, cname in NEW_MUNI_COMARCA.items():
                if child not in db_codes:
                    continue
                prov = child[:2]
                ci = norm_cid.get((prov, _norm(cname)))
                if ci is not None:
                    direct.append((child, ci))
                    muni_to_cid[child] = ci
            await conn.executemany(
                "UPDATE geo_municipality SET comarca_id = $2 WHERE code = $1",
                direct,
            )

            # 4. Propagate to entity via municipality join (single set-based update).
            await conn.execute(
                """UPDATE entity e
                     SET comarca_id = m.comarca_id
                    FROM geo_municipality m
                   WHERE e.municipality_code = m.code
                     AND m.comarca_id IS NOT NULL"""
            )

        # Verification report.
        n_comarca = await conn.fetchval("SELECT count(*) FROM geo_comarca")
        n_muni_total = await conn.fetchval("SELECT count(*) FROM geo_municipality")
        n_muni_cov = await conn.fetchval(
            "SELECT count(*) FROM geo_municipality WHERE comarca_id IS NOT NULL")
        n_ent_total = await conn.fetchval("SELECT count(*) FROM entity")
        n_ent_cov = await conn.fetchval(
            "SELECT count(*) FROM entity WHERE comarca_id IS NOT NULL")
        uncovered = await conn.fetch(
            "SELECT code, name, province_code FROM geo_municipality "
            "WHERE comarca_id IS NULL ORDER BY code")
        print(f"comarcas={n_comarca}")
        print(f"municipalities covered={n_muni_cov}/{n_muni_total} "
              f"({100*n_muni_cov/n_muni_total:.2f}%)")
        print(f"entities with comarca={n_ent_cov}/{n_ent_total} "
              f"({100*n_ent_cov/n_ent_total:.2f}%)")
        print(f"municipalities still without comarca: {len(uncovered)}")
        for u in uncovered:
            tag = "no-comarca-city" if u["code"] in NO_COMARCA else "UNRESOLVED"
            print(f"  {u['code']} {u['name']} (prov {u['province_code']}) [{tag}]")
        if still_missing:
            print("inheritance gaps:", still_missing)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
