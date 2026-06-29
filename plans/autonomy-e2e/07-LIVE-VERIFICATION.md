# Autonomy E2E — 5.x · Verificación EN VIVO (el sistema escupe, E2E, contra :5433)

> Owner (2026-06-29): "verificar como si fuera la VPS, solo un poco… que realmente escupe, funciona
> toda, supervisas cada punto, gestionas fallos y mejoras… TODO SELLADO." Hecho — acotado, real,
> additive sobre `:5433`, supervisado punto por punto. 2 fallos reales **descubiertos y sellados**.

## INGESTA — el sistema cosecha en vivo ✅
`oem_seat_cupra_new_stock --brand cupra --pages 1 --limit 5` (feed OEM real, egress en vivo):
- **items seen: 12 · dealer items: 12 · cars caged: 12 · 0 dup** — el extractor ESCUPE.
- **VAM verdict: TRUSTWORTHY** (quórum like-with-like) · health: healthy / breaker closed · recipe aplicada.
- NEW delta = 0 → **idempotencia correcta** (esos 12 ya estaban; re-cosechar no duplica — eso ES el sistema bien).

## SERVICIO — la API escupe el censo al cliente ✅
Contenedor `cardeep-app` (Punto 3) contra `:5433`:
- `/health` → `{"status":"live","db":"ok"}`.
- `/sources` → estado real de las fuentes; `/entities/CDP-ES-08-SWN09H0C` → dealer completo (Ocasión Plus Mataró: provincia/muni/lat-lon/teléfono).
- `/stats` → **18.967 dealers · 1.576.673 vehículos disponibles · 3.4M eventos · 52 prov · 8132 muni**, en **0.126 s** (precomputed).

## FALLOS REALES — descubiertos en vivo y SELLADOS por causa raíz
1. **API no arrancaba** (`asyncpg: invalid DSN, scheme got ''`). Causa: el compose ponía `CARDEEP_DSN`
   en formato psycopg2-keyword, pero la API usa asyncpg (requiere URL `postgresql://`). **Fix:**
   `CARDEEP_DSN` como URL (la aceptan ambos drivers). Commit en `docker-compose.yml`.
2. **`/stats` colgaba (>35 s) → column `country_code` of product_stats does not exist.** Causa raíz:
   **gap de migraciones en `:5433`** — el cutover aplicó 0067-0072 ANTES de que se mergeara country-2
   (que trae 0065/0066), así que prod nunca aplicó 0065/0066. **Fix:** `migrate.py up` aplicó las
   faltantes (additive, ES-byte-identical) → `product_stats` ganó `country_code` →
   `refresh_product_stats` repobló → `/stats` 0.126 s. `:5433` ahora en 0072 SIN gaps.

## VEREDICTO
El sistema **escupe end-to-end en vivo**: cosecha (12 items, VAM TRUSTWORTHY) → procesa/cachea → sirve
(API, censo real en 126 ms). Supervisado en cada etapa; los 2 fallos que la verificación destapó están
sellados de raíz. **Lección:** tras un merge que añade migraciones, re-correr `migrate.py up` en prod
(el cutover dejó un gap temporal por orden cutover-antes-de-merge; ya cerrado).
