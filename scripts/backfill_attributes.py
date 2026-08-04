"""Backfill colour and trim from data the census already owns (plan Bloque 0.5).

Neither attribute needs a network call: both are already inside the database and
have simply never been extracted into a column.

  COLOUR  <- deep_link. Several platforms encode the colour as a hyphen-delimited
            token in the URL path, immediately before the listing identifier
            ('...-gasolina-verde-<uuid>', '...-beige-cat_ma52mo18921-<uuid>').
            Measured 2026-08-03: 278,218 available rows carry one, and the
            distribution (blanco > gris > negro > azul > rojo) matches the known
            shape of the Spanish fleet, which is the sanity check that this is a
            real signal and not a regex finding noise. The match is anchored to
            the PATH — the scheme+host is stripped first — so a dealer domain
            containing a colour word cannot produce a false positive.

  TRIM    <- vehicle_event.new_value->>'version'. The connectors DO capture the
            version; the ingest INSERT simply had no column to put it in, so it
            survives only inside the event payload. The most recent event wins.

Both passes write provenance ('url_slug' / 'source') alongside the value, because
a figure computed over these columns has to be able to say where each value came
from. Nothing here guesses: a row that does not match is left NULL.

Batched by vehicle_ulid so no single transaction holds locks over millions of rows
(a full-table UPDATE deadlocked against autovacuum on this table once already).

Run:  python scripts/backfill_attributes.py            # dry-run (counts, no writes)
      python scripts/backfill_attributes.py --apply     # execute
"""
from __future__ import annotations

import asyncio
import sys
import time

import asyncpg

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

BATCH = 100_000

# Canonical colour vocabulary. Keys are the tokens as they appear in URLs; values
# are the canonical form stored. Only genuine synonyms are folded — burdeos and
# granate are both dark reds but the market treats them as distinct, so they stay
# apart rather than being flattened for tidiness.
COLOR_CANON: dict[str, str] = {
    "blanco": "blanco", "negro": "negro", "gris": "gris",
    "plata": "plata", "plateado": "plata",
    "azul": "azul", "rojo": "rojo", "verde": "verde", "amarillo": "amarillo",
    "naranja": "naranja", "marron": "marron", "beige": "beige", "dorado": "dorado",
    "granate": "granate", "burdeos": "burdeos",
    "violeta": "violeta", "morado": "violeta",
    "celeste": "celeste", "turquesa": "turquesa", "bronce": "bronce",
    "antracita": "antracita", "perla": "perla",
}
_COLOR_ALT = "|".join(COLOR_CANON)
_COLOR_MAP_VALUES = ",".join(f"('{k}','{v}')" for k, v in COLOR_CANON.items())

# regexp_replace strips scheme+host so only the path is searched.
_COLOR_EXPR = (
    f"(regexp_match(regexp_replace(deep_link,'^https?://[^/]+',''), '-({_COLOR_ALT})-'))[1]"
)

_COLOR_COUNT = f"""
SELECT count(*) FROM vehicle
WHERE color IS NULL AND deep_link IS NOT NULL AND {_COLOR_EXPR} IS NOT NULL
"""

_TRIM_COUNT = """
SELECT count(DISTINCT e.vehicle_ulid)
FROM vehicle_event e JOIN vehicle v ON v.vehicle_ulid = e.vehicle_ulid
WHERE v.trim IS NULL AND e.new_value ? 'version' AND btrim(e.new_value->>'version') <> ''
"""


async def _batched(conn: asyncpg.Connection, label: str, sql: str, apply: bool) -> int:
    """Run `sql` (which must UPDATE at most BATCH rows) until it stops changing rows."""
    if not apply:
        return 0
    total = 0
    started = time.monotonic()
    while True:
        tag = await conn.execute(sql)
        n = int(tag.rsplit(" ", 1)[1])
        total += n
        if n:
            print(f"  {label}: +{n:,} (acumulado {total:,}, {time.monotonic()-started:.0f}s)", flush=True)
        if n < BATCH:
            return total


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN, command_timeout=1800)
    try:
        color_n = await conn.fetchval(_COLOR_COUNT)
        trim_n = await conn.fetchval(_TRIM_COUNT)
        print(f"colour candidates : {color_n:,}")
        print(f"trim candidates   : {trim_n:,}")

        if not apply:
            rows = await conn.fetch(
                f"SELECT right(deep_link,52) AS tail, {_COLOR_EXPR} AS c FROM vehicle "
                f"WHERE color IS NULL AND {_COLOR_EXPR} IS NOT NULL LIMIT 6"
            )
            print("  colour sample (url tail -> colour):")
            for r in rows:
                print(f"    {r['tail']!r:56} -> {r['c']}")
            print("\nDRY-RUN — no writes. Re-run with --apply.")
            return

        color_sql = f"""
        UPDATE vehicle v
           SET color = m.canon, color_source = 'url_slug'
          FROM (VALUES {_COLOR_MAP_VALUES}) m(raw, canon)
         WHERE v.vehicle_ulid IN (
                   SELECT vehicle_ulid FROM vehicle
                    WHERE color IS NULL AND deep_link IS NOT NULL
                      AND {_COLOR_EXPR} IS NOT NULL
                    LIMIT {BATCH})
           AND {_COLOR_EXPR.replace('deep_link', 'v.deep_link')} = m.raw
        """
        c = await _batched(conn, "colour", color_sql, apply)

        trim_sql = f"""
        UPDATE vehicle v
           SET trim = s.version, trim_source = 'source'
          FROM (
              SELECT DISTINCT ON (e.vehicle_ulid)
                     e.vehicle_ulid, btrim(e.new_value->>'version') AS version
                FROM vehicle_event e
                JOIN vehicle vv ON vv.vehicle_ulid = e.vehicle_ulid AND vv.trim IS NULL
               WHERE e.new_value ? 'version' AND btrim(e.new_value->>'version') <> ''
               ORDER BY e.vehicle_ulid, e.observed_at DESC
               LIMIT {BATCH}
          ) s
         WHERE v.vehicle_ulid = s.vehicle_ulid
        """
        t = await _batched(conn, "trim", trim_sql, apply)

        print(f"\nAPPLIED. colour: {c:,} | trim: {t:,}")
        row = await conn.fetchrow(
            "SELECT count(*) FILTER (WHERE color IS NOT NULL) AS c, "
            "       count(*) FILTER (WHERE trim IS NOT NULL) AS t, count(*) AS n "
            "  FROM vehicle WHERE status='available'"
        )
        print(f"available: colour {row['c']:,} ({100*row['c']/row['n']:.1f}%) | "
              f"trim {row['t']:,} ({100*row['t']/row['n']:.1f}%)")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
