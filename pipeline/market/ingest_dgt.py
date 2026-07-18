"""ingest_dgt.py — DGT monthly vehicle-transfer microdata ingestion (F4,
01-market-intelligence). Cero LLM en el camino crítico (carta §8): parser
determinista sobre un dataset público con diccionario de datos oficial.

Source verified live 2026-07-18 (not assumed):
  - Download URL pattern: https://www.dgt.es/microdatos/salida/{year}/{month}/
    vehiculos/transferencias/export_mensual_trf_{YYYYMM}.zip — month is NOT
    zero-padded (verified by parsing the real HTML link list on
    https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/
    transacciones-automoviles-mensual.html; a zero-padded URL 404s).
  - File is fixed-width text, one record per line, 714 bytes + newline (verified:
    the 69 fields declared in the official "Documento de interfaz de Envío de
    Datos (Transferencias)" PDF sum to EXACTLY 714 — no discrepancy with the real
    file). Byte offsets below for the columns this pilar needs are re-verified
    against a real downloaded sample (COD_PROVINCIA_VEH="BI"=Bizkaia,
    CLAVE_TRAMITE="2"=Transferencia, BASTIDOR_ITV 8 real chars + '*' padding all
    matched the real bytes exactly).
  - No VIN, no price in this dataset (confirmed against the primary source, not
    carried over from the carta's own prior research).

Ingest philosophy: store every row AS-IS (whatever CLAVE_TRAMITE value it carries),
filtering happens downstream in corroborate.py — mirrors the project's broader
"ingest everything, filter at serving/query time" pattern (e.g. price_sanity.py).
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import io
import os
import urllib.request
import zipfile
from datetime import date, datetime, timezone

import asyncpg

from pipeline.ids import ulid
from pipeline.market.dgt_provinces import map_province

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

DGT_BASE_URL = "https://www.dgt.es/microdatos/salida"
_USER_AGENT = "Mozilla/5.0 (compatible; Cardeep-market-intelligence/1.0)"

# Byte offsets (0-indexed, [start:end)) verified against the real interface PDF
# (sums to 714) AND a real downloaded sample line — see module docstring.
_OFF_FEC_TRAMITACION = (9, 17)
_OFF_MARCA = (17, 47)
_OFF_MODELO = (47, 69)
_OFF_COD_TIPO = (91, 93)
_OFF_COD_PROVINCIA_VEH = (152, 154)
_OFF_CLAVE_TRAMITE = (156, 157)

# COD_TIPO value for passenger cars (Anexo I §1.3.4) — Cardeep's census is cars
# only; corroborate.py filters DGT rows to this code so M8 never compares against
# a denominator inflated by trucks/motorcycles/trailers/tractors/etc.
COD_TIPO_TURISMO = "40"

RECORD_LENGTH = 714  # bytes per record, excluding line terminator


def build_url(year: int, month: int) -> str:
    """The real DGT monthly-transfer ZIP URL — month is NOT zero-padded."""
    return f"{DGT_BASE_URL}/{year}/{month}/vehiculos/transferencias/export_mensual_trf_{year:04d}{month:02d}.zip"


def _fetch_bytes(url: str, timeout: int = 120) -> bytes:
    """Synchronous download (urllib) — DGT's site has no known async-friendly
    client precedent in this codebase; kept simple and explicit."""
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"DGT download failed: HTTP {resp.status} for {url}")
        return resp.read()


def _parse_fec_tramitacion(raw: str) -> date | None:
    """DDMMYYYY -> date. Returns None on malformed input (never raises, never
    guesses — a malformed row's date becomes NULL-equivalent... but fec_tramitacion
    is NOT NULL in the schema, so a malformed date is a hard parse error the
    caller must surface, not silently swallow)."""
    raw = raw.strip()
    if len(raw) != 8 or not raw.isdigit():
        return None
    try:
        return date(int(raw[4:8]), int(raw[2:4]), int(raw[0:2]))
    except ValueError:
        return None


def parse_line(line: str) -> dict | None:
    """Parse one fixed-width record into the subset of fields this pilar stores.

    Returns None if the line is too short to contain all the fields we slice
    (a truncated/corrupt trailing line) — the caller counts and reports these,
    never silently drops without a trace.
    """
    if len(line) < _OFF_CLAVE_TRAMITE[1]:
        return None
    fec = _parse_fec_tramitacion(line[_OFF_FEC_TRAMITACION[0]:_OFF_FEC_TRAMITACION[1]])
    if fec is None:
        return None
    marca = line[_OFF_MARCA[0]:_OFF_MARCA[1]].strip() or None
    modelo = line[_OFF_MODELO[0]:_OFF_MODELO[1]].strip() or None
    cod_tipo = line[_OFF_COD_TIPO[0]:_OFF_COD_TIPO[1]].strip() or None
    cod_provincia_dgt = line[_OFF_COD_PROVINCIA_VEH[0]:_OFF_COD_PROVINCIA_VEH[1]].strip() or None
    clave_tramite = line[_OFF_CLAVE_TRAMITE[0]:_OFF_CLAVE_TRAMITE[1]].strip() or None
    return {
        "fec_tramitacion": fec,
        "marca": marca,
        "modelo": modelo,
        "cod_tipo": cod_tipo,
        "cod_provincia_dgt": cod_provincia_dgt,
        "province_code": map_province(cod_provincia_dgt),
        "clave_tramite": clave_tramite,
    }


def parse_records(raw_text: bytes) -> tuple[list[dict], int]:
    """Parse the full file content. Returns (parsed_rows, n_malformed_lines)."""
    text = raw_text.decode("latin-1")  # DGT fixed-width files are Latin-1, not UTF-8
    # Windows-style CRLF or plain LF — split universally, drop trailing empty line.
    lines = text.splitlines()
    rows: list[dict] = []
    n_bad = 0
    for line in lines:
        if not line.strip():
            continue
        parsed = parse_line(line)
        if parsed is None:
            n_bad += 1
            continue
        rows.append(parsed)
    return rows, n_bad


async def ingest_month(
    conn: asyncpg.Connection, year: int, month: int, *, verify_double_download: bool = True
) -> str:
    """Download, verify, parse, and store one month of DGT transfer microdata.

    Returns the new batch_id. Raises RuntimeError if a batch for this month
    already exists (idempotency guard — re-ingesting silently would violate the
    project's MVCC doctrine; an operator must explicitly handle a re-ingest).
    """
    month_str = f"{year:04d}{month:02d}"
    existing = await conn.fetchval(
        "SELECT batch_id FROM dgt_transfer_batch WHERE month = $1", month_str
    )
    if existing is not None:
        raise RuntimeError(
            f"dgt_transfer_batch already has a batch for {month_str} (batch_id={existing}) — "
            f"re-ingestion is not automatic; delete the old batch explicitly first if a re-run is intended."
        )

    url = build_url(year, month)
    raw_zip = _fetch_bytes(url)
    sha256_1 = hashlib.sha256(raw_zip).hexdigest()

    double_verified = False
    sha256_2 = None
    if verify_double_download:
        raw_zip_2 = _fetch_bytes(url)
        sha256_2 = hashlib.sha256(raw_zip_2).hexdigest()
        double_verified = sha256_2 == sha256_1

    zf = zipfile.ZipFile(io.BytesIO(raw_zip))
    names = zf.namelist()
    if len(names) != 1:
        raise RuntimeError(f"expected exactly 1 file inside the DGT zip, found {names}")
    raw_text = zf.read(names[0])

    rows, n_bad = parse_records(raw_text)
    n_transferencia = sum(1 for r in rows if r["clave_tramite"] == "2")
    n_turismo = sum(1 for r in rows if r["cod_tipo"] == COD_TIPO_TURISMO)

    batch_id = ulid()
    notes_parts = []
    if n_bad:
        notes_parts.append(f"{n_bad} malformed/truncated lines skipped")
    notes_parts.append(f"{n_turismo} of {len(rows)} rows are COD_TIPO={COD_TIPO_TURISMO} (TURISMO)")

    async with conn.transaction():
        await conn.execute(
            """
            INSERT INTO dgt_transfer_batch
                (batch_id, month, source_url, zip_sha256, zip_size_bytes,
                 n_rows_parsed, n_rows_transferencia, double_download_verified,
                 double_download_sha256, notes)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
            """,
            batch_id, month_str, url, sha256_1, len(raw_zip),
            len(rows), n_transferencia, double_verified, sha256_2,
            "; ".join(notes_parts),
        )
        if rows:
            await conn.copy_records_to_table(
                "dgt_transfer",
                records=[
                    (batch_id, r["fec_tramitacion"], r["marca"], r["modelo"], r["cod_tipo"],
                     r["cod_provincia_dgt"], "ES", r["province_code"], r["clave_tramite"])
                    for r in rows
                ],
                columns=[
                    "batch_id", "fec_tramitacion", "marca", "modelo", "cod_tipo",
                    "cod_provincia_dgt", "country_code", "province_code", "clave_tramite",
                ],
            )
    return batch_id


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--no-double-download", action="store_true")
    args = parser.parse_args()

    conn = await asyncpg.connect(DSN, command_timeout=300)
    try:
        batch_id = await ingest_month(
            conn, args.year, args.month, verify_double_download=not args.no_double_download
        )
        row = await conn.fetchrow(
            "SELECT * FROM dgt_transfer_batch WHERE batch_id = $1", batch_id
        )
        for k, v in dict(row).items():
            print(f"{k}={v}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
