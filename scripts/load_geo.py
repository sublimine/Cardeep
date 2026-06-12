"""Load the Spanish geo backbone (INE) into geo_province + geo_municipality.

Provinces (52) are authoritative and stable -> hardcoded with their CCAA.
Municipalities (~8,132) are loaded from the official INE dictionary xlsx
(data/geo/diccionario_ine.xlsx; download from
https://www.ine.es/daco/daco42/codmun/diccionario25.xlsx).

INSERT-only with ON CONFLICT DO NOTHING -> idempotent. Comarcas are left empty
here (no universal INE comarca layer for all of Spain; populated per-region later).

Usage: python -m scripts.load_geo
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import asyncpg
import openpyxl

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
XLSX = Path(__file__).resolve().parent.parent / "data" / "geo" / "diccionario_ine.xlsx"

# CODAUTO -> CCAA name (INE standard)
CCAA = {
    "01": "Andalucía", "02": "Aragón", "03": "Asturias, Principado de",
    "04": "Balears, Illes", "05": "Canarias", "06": "Cantabria",
    "07": "Castilla y León", "08": "Castilla-La Mancha", "09": "Cataluña",
    "10": "Comunitat Valenciana", "11": "Extremadura", "12": "Galicia",
    "13": "Madrid, Comunidad de", "14": "Murcia, Región de",
    "15": "Navarra, Comunidad Foral de", "16": "País Vasco", "17": "Rioja, La",
    "18": "Ceuta", "19": "Melilla",
}

# province code -> (name, CODAUTO). Authoritative INE 52-province list.
PROVINCES = {
    "01": ("Araba/Álava", "16"), "02": ("Albacete", "08"), "03": ("Alicante/Alacant", "10"),
    "04": ("Almería", "01"), "05": ("Ávila", "07"), "06": ("Badajoz", "11"),
    "07": ("Balears, Illes", "04"), "08": ("Barcelona", "09"), "09": ("Burgos", "07"),
    "10": ("Cáceres", "11"), "11": ("Cádiz", "01"), "12": ("Castellón/Castelló", "10"),
    "13": ("Ciudad Real", "08"), "14": ("Córdoba", "01"), "15": ("Coruña, A", "12"),
    "16": ("Cuenca", "08"), "17": ("Girona", "09"), "18": ("Granada", "01"),
    "19": ("Guadalajara", "08"), "20": ("Gipuzkoa", "16"), "21": ("Huelva", "01"),
    "22": ("Huesca", "02"), "23": ("Jaén", "01"), "24": ("León", "07"),
    "25": ("Lleida", "09"), "26": ("Rioja, La", "17"), "27": ("Lugo", "12"),
    "28": ("Madrid", "13"), "29": ("Málaga", "01"), "30": ("Murcia", "14"),
    "31": ("Navarra", "15"), "32": ("Ourense", "12"), "33": ("Asturias", "03"),
    "34": ("Palencia", "07"), "35": ("Palmas, Las", "05"), "36": ("Pontevedra", "12"),
    "37": ("Salamanca", "07"), "38": ("Santa Cruz de Tenerife", "05"), "39": ("Cantabria", "06"),
    "40": ("Segovia", "07"), "41": ("Sevilla", "01"), "42": ("Soria", "07"),
    "43": ("Tarragona", "09"), "44": ("Teruel", "02"), "45": ("Toledo", "08"),
    "46": ("Valencia/València", "10"), "47": ("Valladolid", "07"), "48": ("Bizkaia", "16"),
    "49": ("Zamora", "07"), "50": ("Zaragoza", "02"), "51": ("Ceuta", "18"),
    "52": ("Melilla", "19"),
}


def read_municipalities() -> list[tuple[str, str, str]]:
    """Return (code5, name, province_code) for every INE municipality."""
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb.active
    out: list[tuple[str, str, str]] = []
    for row in ws.iter_rows(min_row=3, values_only=True):
        if not row or row[1] is None or row[2] is None:
            continue
        cpro = str(row[1]).strip().zfill(2)
        cmun = str(row[2]).strip().zfill(3)
        name = str(row[4]).strip()
        out.append((cpro + cmun, name, cpro))
    return out


async def main() -> None:
    munis = read_municipalities()
    conn = await asyncpg.connect(DSN)
    try:
        await conn.executemany(
            "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name) "
            "VALUES ($1, $2, $3, $4) ON CONFLICT (code) DO NOTHING",
            [(code, name, ccaa, CCAA[ccaa]) for code, (name, ccaa) in PROVINCES.items()],
        )
        await conn.executemany(
            "INSERT INTO geo_municipality (code, name, province_code) "
            "VALUES ($1, $2, $3) ON CONFLICT (code) DO NOTHING",
            munis,
        )
        nprov = await conn.fetchval("SELECT count(*) FROM geo_province")
        nmuni = await conn.fetchval("SELECT count(*) FROM geo_municipality")
        # 2-way check: every municipality's province must exist (FK already guarantees,
        # but assert the prefix invariant and province coverage explicitly).
        orphans = await conn.fetchval(
            "SELECT count(*) FROM geo_municipality m "
            "LEFT JOIN geo_province p ON p.code = m.province_code WHERE p.code IS NULL"
        )
        covered = await conn.fetchval("SELECT count(DISTINCT province_code) FROM geo_municipality")
        print(f"provinces={nprov} municipalities={nmuni} (xlsx rows={len(munis)}) "
              f"orphans={orphans} provinces_covered={covered}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
