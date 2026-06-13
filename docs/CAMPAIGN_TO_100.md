# CAMPAÑA AL 100% — Cardeep

> Plan maestro de cierre desde el estado real (~60%) hasta el producto definido en `CLAUDE.md`:
> una base de datos viva y verificada con el 100% de los dealers y plataformas de España y todo
> su inventario en tiempo real. Documento de mando del Director. Estado vivo en `PROGRESO.md`;
> el plan de fases original sigue en `docs/MASTER_PLAN.md` (P0-P12) — esta campaña es la ruta de
> cierre operativa que lo absorbe en 6 bloques con gate binario.

## Método de ejecución (mando)

- **Cadena de mando:** Director + Inquisidor en Opus 4.8; **constructores en Fable 5** (`model: fable`).
- **Workflows átomo:** cada bloque se monta como workflow(s) verificados; el E2E por dealer cubre
  descubrir → scrapear → receta → API → evicción. Nada se da por bueno sin verificar por ≥2 caminos.
- **Huella:** todo a GitHub `main`, documentado (recetas, estado, decisiones). Estructura en carpetas.
- **Coste:** €0 salvo muros Tier-1 autorizados uno a uno. LLM local para lo masivo donde el hardware
  dé; estadística (Splink) para dedup; inteligencia cara solo para decidir el slice ambiguo.
- **Evicción:** guardado el inventario + receta + config, el crudo se evicta por capacidad del PC
  (tombstone como prueba de vida). El PC es débil (AMD, sin CUDA, 16GB) — la evicción es obligada.

## Los 6 bloques (orden por desbloqueo)

| # | Bloque | Gate de cierre (binario, verificable en DB) | Estado |
|---|---|---|---|
| **B1** | Cerebro local + Identidad única | dealer↔1 cdp_code canónico (alias no-destructivo); tasa dup <0,1% por ≥2 caminos VAM | **EN CURSO** |
| **B2** | Latido continuo | scheduler crash-safe re-cosechando por tier (24h/7d/30d); delta GONE/NEW reales 2ª pasada; governor multiproceso | pendiente |
| **B3** | Auto-reparación real + API blindada | fallo inyectado→alerta origen-exacto→auto-repair cierra lazo sin caer; 7 alertas vivas cerradas; API paginada/cacheada | pendiente |
| **B4** | Geo al átomo | geocode-gap 32,5%→<2%; cada entidad a municipio/comarca | pendiente |
| **B5** | Cobertura total + filtrado | sells_cars resuelto; particular vs dealer decidido; Canarias/Ceuta/Melilla cerrados; cada segmento sellado o gap-con-causa | pendiente |
| **B6** | Sello 52/52 + separación física | SPAIN-SEALED (denominador medido + numerador VAM por provincia); `platforms/_tier1/` separado | pendiente |

## B1 — estado y hallazgos del reconocimiento (2026-06-14)

Reconocimiento de 4 vías (workflow `cardeep-b1-recon`). El "problema de identidad" son **tres** con raíces distintas:

| Sub-problema | Magnitud [VERIFICADO DB] | Raíz | Herramienta |
|---|---|---|---|
| A. Explosión OEM-VO | 39 clusters >20 = 4.042 filas de ~39 dealers | **Bug de ingesta**: clave de dealer inestable (fragmento por-coche) | Fix de código (B1.0) |
| B. Dup cross-source | 4.004 grupos / 9.266 filas | Mismo dealer en N plataformas con claves distintas | Splink (B1.3) |
| C. Dup intra-source | 270 grupos / 3.986 filas (milanuncios) | Drain sin dedup por author_id | Fix en el drain (B1.1) |

Datos duros: **CIF 100% vacío** (0/42.880), **website 4,4%**, **municipio 67%**. Blocking principal = nombre+municipio fuzzy.
Hardware: **CPU-only AMD, sin CUDA; vLLM inviable; Ollama qwen3 a ~10 t/s**. Dedup masiva = Splink (CPU, €0); LLM solo slice ambiguo (<2k pares).

### B1.0 — erradicar la explosión OEM-VO  *(CERRADO 2026-06-14)*
Auditados los 13 conectores OEM-VO (workflow Sonnet; Fable 5 sin acceso Mythos). **2 inestables arreglados**: `oem_mercedes_benz`
(clave `dealer:{dealerCode-por-coche}` → explosión 480 entidades / 488 coches, ratio 1.02) y `das_weltauto` (BNR VW multi-formato
`C311K`/`0311K`/`30060` → 18 dealers fragmentados ×2-3). Ambos unificados a la clave **conservadora `name + municipio`** (`address=None`);
el id por-coche queda solo como `source_ref`. El código postal se deja FUERA del hash a propósito (un card que no parsee su CP
fragmentaría); separar dos sucursales legítimas del mismo nombre+municipio se delega a `entity_cluster` (B1.3). **11 conectores
restantes SANOS** y no tocados (dealer_id estable del portal: spoticar, toyota_lexus, audi, bmw/mini, hyundai, volvo_jlr_suzuki,
nissan, kia, seat_cupra, renew, ford). 18 tests verdes. Forward-fix; lo histórico lo colapsa B1.3.

### Secuencia B1
`B1.0` forward-fix OEM-VO → `B1.1` dedup drain milanuncios → `B1.2` migración `entity_cluster`/`entity_cluster_run`/`v_canonical` →
`B1.3` job Splink v4.0.16 sobre PostgreSQL (blocking que excluye dominios OEM corporativos) → `B1.4` canónico determinista
(fuente→riqueza→antigüedad→lexicográfico) → `B1.5` VAM 3 caminos → `B1.6` API resuelve cualquier código→canónico.

## Diseño de identidad inmutable (B1.2)

`cdp_code` nunca se reescribe. Se superpone:
- `entity_cluster(cluster_run_id, cdp_code, canonical_cdp_code, match_probability, ...)`
- `entity_cluster_run(cluster_run_id, splink_version, threshold, n_in, n_clusters, vam_verified, ...)`
- vista `v_canonical` resuelve `cdp_code → canonical_cdp_code` en query-time (solo el run con `vam_verified=TRUE`).

## Log
- 2026-06-14 — Reconocimiento B1 cerrado (4 vías). Raíz explosión OEM-VO confirmada. Plan de campaña sellado.
- 2026-06-14 — Fable 5 sin acceso (Mythos restringido). Routing efectivo de la campaña: **Sonnet construye, Opus dirige y verifica**.
- 2026-06-14 — B1.0 CERRADO: `mercedes_benz` + `das_weltauto` arreglados (clave `name+municipio`); 11 conectores OEM-VO restantes auditados sanos; 18 tests verdes.
- 2026-06-14 — MISSION.md sellado (super-prompt maestro, asignado como /goal). Splink 4.0.16 instalado y verificado (importa con pandas 3.0.3).
- 2026-06-14 — B1.2: migración `0020_entity_cluster` aplicada y verificada (overlay no-destructivo `entity_cluster` + `entity_cluster_run` + vista `v_canonical`; FK por `entity_ulid` porque `cdp_code` solo tiene unique index; `vam_verdict_id`→`verification_verdict(id)`). Falso positivo descartado: `migrate.py` está limpio (no tiene el NameError que un agente reportó). Siguiente: B1.3 (job Splink sobre el overlay) → B1.1 (dedup drain milanuncios).
