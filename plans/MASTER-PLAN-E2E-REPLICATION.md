# MASTER PLAN — CARDEEP E2E completo + Replicación (roadmap del mandato 2026-06-23)

> Derivado de la auditoría orquestada exhaustiva (workflow w1kocil4d, 9 agentes, 721k tokens,
> evidencia real código+DB). Owner: producto ENTERO end-to-end (cada punto de venta:
> discover→scrape→recipe→API→delta) integrado+estable, con configs/recetas, + BIBLIA A→Z
> replicable a otros países al 100%. Ejecución orquestada (workflows), un bloque verificado→siguiente.

## VEREDICTO HONESTO (auditoría)
CARDEEP-ES es un producto E2E vivo para UN país (espina API+delta excelente: 2.31M coches, 2.61M
eventos, 5 deltas, historia por coche/dealer). 4 frentes abiertos impiden el 100% del mandato:
1. **Replicación ROTA en código** — 5 blockers sin arreglar (codes.py:89 'CDP-ES-', sin country_code
   en 51 migraciones, paths data/ES//countries/ES/). Un país #2 colisiona en PK. ASPIRACIONAL hoy.
2. **Cosecha al 13%** (2.656/20.124 dealers-con-web; backlog drenable 10.452).
3. **Identidad parcial** — 339.800 particulares (79.8%) sin resolución; cross-source-dedup-v1 sin sellar;
   canónicos frágiles; el over-merge 113k (cerrado) prueba fragilidad.
4. **Estabilidad no-perfecta** — CI solo `pytest --collect-only` (verde NO prueba E2E); daemons
   session-bound sin systemd/watchdog; `cardeep_dev_only` en 158 archivos; rate-limit in-memory.

## PLAN MAESTRO (10 fases, ordenadas)
- **FASE 0 — Desbloquear replicación en código** [CRITICAL, prerequisito multi-país]: 5 blockers
  backward-compat, cero regresión ES (country_code DEFAULT 'ES' + PK/UNIQUE compuesto FK-safe; codes.py
  + paths con param country='ES'; golden test cdp byte-idéntico). → EN CURSO (workflow w97w3xv18).
- **FASE 1 — CI = prueba E2E real** [CRITICAL]: job seeded-snapshot que corre los 1447 tests en cada push
  (no solo --collect-only). Prioridad: delta-guard, identity-canonical, API-contract.
- **FASE 2 — Endurecer daemons + secretos** [CRITICAL ops]: systemd/supervisor+healthcheck/restart para
  los 3 daemons; heartbeat+TTL en advisory-lock (auto-release); secretos fuera del código (fail-fast prod).
- **FASE 3 — Cerrar identidad/dedup** [CRITICAL seam]: pipeline R-stratum para 339.800 particulares; sellar
  +servir cross-source-dedup-v1 via VAM; canónico=miembro más rico; tests-invariante (raíz over-merge).
- **FASE 4 — Exhaustividad cosecha ES** [CRITICAL censo]: acelerar drain dealerprobe (batch+host-pool, SLA
  semanas); tunear motor_es_wholesale; desgatear V3 dork (SearXNG self-host gratis) → 2.654 municipios.
- **FASE 5 — Recipe-first al 100%** [HIGH, base del bible]: migrar los 41 conectores a Recipe dataclass+
  RecipeHarness (sample-verify-delete+VAM); connector-registry (tabla/vista); arreglar v_dealer_recipe.
- **FASE 6 — Pulir espina API+delta** [MEDIUM]: backfill 24 GONE huérfanos; desbloquear fuentes REFUTED;
  enriquecer km en recetas; completar phash+backfill photo_hash; CARDEEP_API_KEY obligatorio.
- **FASE 7 — Bible ejecutable A→Z** [HIGH, mandato replicación]: docs/REPLICATION-PLAYBOOK con ejemplo
  trabajado (DE/IT) Fase 0-6 con comandos/queries/gates/rollback; per-stage runbooks; API_CONTRACT.md
  sellado; GUIDE-NEW-SOURCE-ADAPTER; COUNTRY-SWITCHOVER; refresco SYSTEM-A-Z con re-conteo CI.
- **FASE 8 — Piloto replicación E2E**: tras 0+7, un dealer país XX end-to-end (raw data/XX/, recipe
  countries/XX/, entity country_code='XX' CDP-XX-*, servido por API, delta) + CERO regresión ES.
- **FASE 9 — Auditoría adversarial + sello**: barrido multi-perspectiva (factual/senior/security/
  consistencia), re-medir conteos vivos, cero regresiones, sellar + memoria.

## WORKFLOWS RECOMENDADOS (orden de ejecución)
1. REPLICATION-FASE-0 (EN CURSO w97w3xv18) — country-parametrize, additive, golden.
2. CI-SEEDED-SNAPSHOT — DB determinista + 1447 tests en CI.
3. IDENTITY-R-STRATUM — dedup 339.8k particulares + sellar cross-source-dedup-v1.
4. HARVEST-DRAIN-ACCELERATE — dealerprobe batch/paralelo + motor_es + desgatear V3.
5. RECIPE-HARNESS-MIGRATION — 41 conectores a RecipeHarness + connector-registry.
6. OPS-HARDENING — systemd + heartbeat/TTL + secretos fail-fast + rate-limit distribuido + API_KEY.
7. BIBLE-EXECUTABLE — REPLICATION-PLAYBOOK + runbooks + API_CONTRACT + guías.
8. PILOTO-PAIS-XX — harvest piloto end-to-end país #2.
9. AUDITORIA-ADVERSARIAL-FINAL — re-medir + cero regresiones + sello.

## REPLICATION BLOCKERS (los 5, evidencia)
- codes.py:89 'CDP-ES-' literal; cdp_pair/cdp_code/canonical_key sin param country_code.
- CERO columna country_code en 51 migraciones; PK geo_province=(code) → colisión país #2 en '28'.
- Paths: recipe.py:58 'countries/ES/recipes'; harvest_dealer.py:57 'data/ES/'; triangulation.py:23 census ES.
- Discovery+identity ES-específicos (geo INE, overture bbox ES, phone_es, BORME/CIF, 46 adapters).
- API geo asume 2 niveles (provincia→municipio); DE/FR son 3 (Land/Kreis/Gemeinde).

## REGLA DE EJECUCIÓN
Paralelizar DENTRO de cada fase (workflows, agentes que OWNS un archivo, SIN worktree EPERM). Secuenciar
ENTRE fases que tocan datos/esquema servidos (un bloque verificado→siguiente; migraciones las aplica+verifica
el operador). Backward-compat + golden + Ferrari verde + cero regresión en cada fase. NO maquillar/forzar guards.
