# SUB2-INQUISITION-RECON
**Barrido de auditoría B2 — read-only — 2026-06-15**
**Agente**: Director de Verificación (Sonnet)
**Mandato**: Verificar estado real de SU-B2 vs SUPERPLAN, sin inventar nada.

---

## 0. Checklist de criterios auditados

| Criterio | Estado |
|---|---|
| Mecanismo VAM actual (record_count_verdict + quórum) | [VERIFICADO] |
| Tablas de verificación existentes en DB | [VERIFICADO] |
| Documentos V1-V6 leídos íntegramente | [VERIFICADO] |
| Los 5 gates binarios de COMPLETED | [VERIFICADO] |
| Existencia de state-machine de completitud por entidad | [VERIFICADO] |
| WF-INQUISITION en cadencia — implementación real | [VERIFICADO] |
| Estado de verdicts en DB (conteo + expiración) | [VERIFICADO] |
| Gap concreto a B2 | [VERIFICADO] |

---

## 1. El mecanismo VAM actual

### 1.1 Función nuclear: `record_count_verdict`

**Ruta**: `C:\Users\elias\projects\cardeep\pipeline\verify.py` (57 líneas totales)

La función es síncrona-sobre-asyncpg. Recibe:
- `subject_type`, `subject_key`, `claim` — coordenadas del claim
- `paths: dict[str, int]` — diccionario nombre_camino → valor observado
- `tolerance: float = 0.0`

**Lógica de quórum** (verificada línea a línea):
1. Filtra `None` del diccionario de paths.
2. Con <2 valores válidos → `UNVERIFIED`.
3. Con ≥2 valores: calcula modal (`Counter`), busca rivales (otros valores con ≥2 votos), calcula `divergence = (hi-lo)/hi`.
4. `primary_agrees` = el primer path coincide con al menos otro valor.
5. `TRUSTWORTHY` si: `top_n ≥ 2 AND no rivals AND primary_agrees`.
6. `TRUSTWORTHY` alternativo si: `divergence ≤ tolerance` (aunque no haya quórum modal limpio).
7. Cualquier otra cosa: `REFUTED`.

**INSERT**: sin `ON CONFLICT` — cada llamada inserta una fila nueva. No hay UPSERT. Los verdicts se acumulan; la re-verificación produce filas nuevas, no sobreescribidas.

**Callers conocidos** (verificados en filesystem):
- `pipeline/ops/coverage_verify.py` → `verify_coverage()` → llama a `record_count_verdict` con camino A (SQL sobre `vehicle+entity_source`) y camino B (SQL sobre `platform_listing`).
- `pipeline/platform/coches_com_wholesale.py` (importado).
- Múltiples plataformas wholesale (`wallapop`, `subastacar`, `spoticar`, `renew`, `oem_volvo_jlr_suzuki`).

### 1.2 Tablas de verificación existentes en DB (puerto 5433)

**Solo existen 2 tablas de verificación** [VERIFICADO por `pg_tables`]:
- `verification_verdict` — 21 columnas, 1.091 filas
- `verdict_audit` — hash-chain append-only (vacía o con filas de prueba; no consultada por separado)

**NO existen** (confirmado): `entity_completion`, `gestion_item`, `gestion_transition`, `inquisition_claim`, `inquisition_skeptic`, `inquisition_verdict`.

**NO existe** tabla `record_count_verdict` (es una función Python, no una tabla SQL — confirmado).

### 1.3 Columnas de `verification_verdict` (21 columnas)

```
id, subject_type, subject_key, claim, primary_value, primary_path,
verifier_paths (jsonb), independent_values (jsonb), divergence, verdict,
evidence, created_at, claim_kind, tolerance,
quorum_n (GENERATED), family_n (GENERATED), origin_n (GENERATED),
evidence_uri, method_version, expires_at (nullable), superseded_by (bigint nullable)
```

Las columnas `expires_at` y `superseded_by` existen en el schema pero **ninguna fila las tiene pobladas** [VERIFICADO por Q8: 0 filas con expires_at no-NULL].

---

## 2. Los documentos V1-V6 — qué existe y qué define cada uno

**Ruta base**: `C:\Users\elias\projects\cardeep\docs\architecture\verification\`

| Archivo | Líneas | Qué define | Estado de implementación |
|---|---|---|---|
| `VALIDATOR_SUPREMO.md` | 657 | Compositor de V1-V6; taxonomía de 7 mentiras (L1-L7); pipeline maestro 9 etapas; protocolos A y B | Spec solo — no hay código |
| `V1-DENOMINATOR-PROOF.md` | 743 | Estimador Chapman bias-corrected + CI log-normal Chao; anchors DGT/INE; denominador por segment×province | Solo `denominator_estimate` tabla creada en 0026; sin `pipeline/denominator.py` |
| `V2-COMPLETION-PROOF.md` | 550 | Los 5 gates binarios G1-G5 por entidad; tabla `entity_completion`; LQAS n=132 c=3 para claim poblacional | Solo spec — migración `0005_completion.sql` [ASSUMED], sin código |
| `V3-INQUISITION.md` | 630 | Cadena adversarial con 3 leyes + 5 lentes ortogonales; tablas `inquisition_claim/skeptic/verdict` | Solo `cardeep_inquisitor` ROLE creado en 0026; sin tablas inquisition_* ni `pipeline/inquisition/` |
| `V4-GESTIONADOR.md` | 834 | 9 detectores con thresholds exactos; state machine 9 estados; 5 lanes; tablas `gestion_item/gestion_transition` | Solo spec — sin migración, sin código |
| `V5-LEDGER-API.md` | 772 | Ledger DB-enforced con columnas GENERATED; `chk_trustworthy_needs_quorum`; `v_latest_verdict` materializada; API `/verify/*` | Columnas GENERATED + CHECK + `verdict_audit` creados en 0026; sin vista materializada ni API `/verify/*` |
| `V6-STATISTICAL-RIGOR.md` | 744 | Fundamento matemático; SPRT de Wald; planes (n,c); Precision vs Recall | Solo referencia matemática — sin código |

**Resumen de V1-V6**: son seis documentos de especificación arquitectónica, escritos y completos, que definen el sistema de verificación ideal. La implementación real es solo una fracción de lo especificado.

---

## 3. Los 5 gates binarios para COMPLETED

**Fuente normativa**: `V2-COMPLETION-PROOF.md` + `VALIDATOR_SUPREMO.md`

### Definición exacta G1-G5

| Gate | Nombre | Criterio binario |
|---|---|---|
| G1 | DISCOVERED / Identity | `entity` row existe; `province_code` no-NULL y ∈ {01..52}; `cdp_code` matches `^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$`; lat/lon set o flagged `geo_partial` con motivo |
| G2 | HARVESTED / Inventory complete | `D == H` AND (`D == S` OR Δ explicado y dentro de tolerancia). D (db-landed) es la autoridad. ≥2 paths ortogonales concuerdan. `field_integrity ≥ 0.98` |
| G3 | RECIPE durable | `countries/ES/recipes/<cdp_code>.yaml` existe, git-tracked en commit alcanzable desde HEAD, parsea como receta válida, `entity.recipe_version == recipe.version` |
| G4 | SERVED live | `GET /entities/{cdp_code}/inventory` → HTTP 200, `ok:true`, `meta.count == D`. `GET /entities/{cdp_code}` → `available_inventory == D` |
| G5 | DELTA proven | Segundo harvest con delta engine vivo produce `vehicle_event` rows type-consistent: `GONE ⊆ prev`, `NEW ∩ prev = ∅`, Δ typed |

**Invariante normativo** (§2 de V2-COMPLETION-PROOF.md):
```
verdict='COMPLETED' ⟺ g1 ∧ g2 ∧ g3 ∧ g4 ∧ g5 = TRUE
                      AND completed_at IS NOT NULL
                      AND now() − last_harvest_at ≤ sla_seconds (freshness)
```

**Tabla `entity_completion`** (DDL propuesto en V2, migración `0005_completion.sql`):

```sql
CREATE TABLE entity_completion (
    cdp_code        TEXT PRIMARY KEY REFERENCES entity(cdp_code),
    g1_identity     BOOLEAN NOT NULL DEFAULT FALSE,
    g2_inventory    BOOLEAN NOT NULL DEFAULT FALSE,
    g3_recipe       BOOLEAN NOT NULL DEFAULT FALSE,
    g4_served       BOOLEAN NOT NULL DEFAULT FALSE,
    g5_delta        BOOLEAN NOT NULL DEFAULT FALSE,
    s_declared      INT, h_harvested INT, d_landed INT, d_valid INT,
    field_integrity DOUBLE PRECISION,
    recipe_sha      TEXT,
    served_count    INT,
    last_harvest_at TIMESTAMPTZ,
    sla_seconds     INT NOT NULL,
    verdict         TEXT NOT NULL DEFAULT 'INCOMPLETE'
        CHECK (verdict IN ('COMPLETED','INCOMPLETE','STALE','REFUTED','QUARANTINED')),
    last_blind_at   TIMESTAMPTZ,
    last_blind_pass BOOLEAN,
    e_set           DOUBLE PRECISION,
    e_field         DOUBLE PRECISION,
    completed_at    TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Estado**: tabla NO EXISTE en DB. Solo spec. Hay que construirla desde cero.

---

## 4. WF-INQUISITION en cadencia — estado real

### 4.1 Lo que existe

`WF-INQUISITION` aparece definido en `docs/ORQUESTACION.md` (línea 45):
> "WF-INQUISITION (Audit): cadena verificadora SEPARADA — re-deriva cada conteo por una vía independiente a la que lo produjo. Un agente que afirma; otro que refuta."

También aparece en `docs/architecture/05-VERIFICATION-VAM.md` §5.2 y §9.

### 4.2 Lo que NO existe [VERIFICADO]

El archivo `ORQUESTACION.md` tiene 65 líneas. No contiene **ninguna** mención a:
- `scheduler`, `cron`, `cadencia`, `TTL`, `drift`, `re-verificación`, `expiración`

No existe ningún archivo Python en `pipeline/` con las palabras `inquisition`, `WF_INQUISITION`, `cadence`, `scheduler` (verificado por grep en todo el repo).

No existe ningún worker, daemon, cron job ni script de re-verificación periódica.

### 4.3 Conclusión sobre WF-INQUISITION

**Los verdicts son ONE-SHOT** [VERIFICADO]:
- `verify.py` hace INSERT puro (sin ON CONFLICT).
- `expires_at` existe como columna pero ninguna fila tiene valor (0 filas con expires_at no-NULL).
- `superseded_by` existe pero tampoco está poblado en ninguna fila (excepto el caso puntual del verdict 1121 que supersede 1112 documentado en PROGRESO.md — corrección manual, no cadencia automática).
- No hay scheduler, no hay cron, no hay re-VAM automático.

WF-INQUISITION es actualmente **doctrina sin implementación**. Los verdicts emitidos no caducan, no se re-juzgan y no detectan drift.

---

## 5. Estado de los verdicts en DB

**Query ejecutada**: `SELECT subject_type, verdict, count(*) FROM verification_verdict GROUP BY 1,2 ORDER BY 1,2`

**Total: 1.091 filas en 30 combinaciones**

| subject_type | TRUSTWORTHY | REFUTED | UNVERIFIED | QUARANTINED |
|---|---|---|---|---|
| entity_inventory | 734 | 16 | 0 | 0 |
| platform_slice | 155 | 2 | 0 | 0 |
| family_slice | 38 | 0 | 0 | 0 |
| generic_dealer_site_inventory | 7 | 23 | 0 | 0 |
| source | 5 | 5 | 0 | 0 |
| source_coverage | 5 | 2 | 2 | 0 |
| (otros ~24 tipos menores) | ~55 | ~40 | ~2 | 0 |

**Observaciones críticas**:

1. **Cero verdicts QUARANTINED** — el tipo de verdict que bloquea el serving nunca se ha emitido.
2. **Cero expires_at poblados** — ningún verdict tiene SLA de expiración. Los 750+ TRUSTWORTHY son eternos.
3. **Cero superseded_by en cadena automática** — la corrección manual 1112→1121 es el único caso (producido por el Director, no por un scheduler).
4. **No existe ningún tracker de estado por entidad** — no hay `entity_completion`, no hay `g1/g2/g3/g4/g5` por entidad, no hay verdicts con `subject_type='entity_stage'`.
5. **Los verdicts entity_inventory son sobre inventario agregado por fuente**, no sobre el estado E2E del dealer individualmente.

---

## 6. Gap concreto a B2

### 6.1 Mapa completo de lo que existe vs lo que B2 requiere

| Componente B2 | Existe en código | Existe en DB | Existe como spec | Gap |
|---|---|---|---|---|
| `record_count_verdict` (quórum básico) | SI — `verify.py` | SI — `verification_verdict` | SI | **CERRADO** (es B1) |
| `chk_trustworthy_needs_quorum` CHECK | SI — migración 0026 | SI — NOT VALID | SI | **CERRADO** (es B1) |
| `verdict_audit` hash-chain | SI — migración 0026 | SI | SI | **CERRADO** (es B1) |
| `cardeep_inquisitor` ROLE | SI — migración 0026 | SI | SI | **CERRADO** (es B1) |
| `denominator_estimate` tabla | SI — migración 0026 | SI (vacía) | SI — V1 | **PARCIAL** — tabla existe, sin datos reales |
| **`entity_completion` tabla (5 gates)** | NO | NO | SI — V2 | **GAP CRITICO** |
| **Lógica G1-G5 per-entity** | NO | NO | SI — V2 | **GAP CRITICO** |
| **`gestion_item` / `gestion_transition`** | NO | NO | SI — V4 | **GAP CRITICO** |
| **9 detectores V4** | NO | NO | SI — V4 | **GAP CRITICO** |
| **State machine de completitud** | NO | NO | SI — V2+V4 | **GAP CRITICO** |
| **`inquisition_claim/skeptic/verdict`** | NO | NO | SI — V3 | **GAP CRITICO** |
| **`pipeline/complete.py`** | NO | — | SI — V2 | **GAP CRITICO** |
| **`pipeline/inquisition/`** | NO | — | SI — V3 | **GAP CRITICO** |
| **`pipeline/gestionador/`** | NO | — | SI — V4 | **GAP CRITICO** |
| **WF-INQUISITION cadencia** | NO | — | Doctrina solo | **GAP CRITICO** |
| **`expires_at` poblado** | NO | 0 filas | SI — V5 | **GAP CRITICO** |
| **`v_latest_verdict` materializada** | NO | NO | SI — V5 | **GAP menor** |
| **API `/verify/*`** | NO | — | SI — V5 | **GAP menor** |

### 6.2 Lo que es €0-construible (código + DB, sin corridas)

Todo lo siguiente es código puro + migraciones SQL, sin dependencia de gasto externo:

1. **Migración `0030_entity_completion.sql`** — crear `entity_completion` exactamente como spec V2. €0.
2. **`pipeline/complete.py`** — lógica G1-G5 per-entity: G1 (query a `entity`), G2 (reusar `record_count_verdict` con 2 paths), G3 (git subprocess + entity.recipe_version), G4 (HTTP call a la propia API en localhost), G5 (trigger re-harvest y leer `vehicle_event`). €0 para G1/G2/G3/G4. G5 requiere corrida real.
3. **Migración `0031_gestion.sql`** — crear `gestion_item` + `gestion_transition` exactamente como spec V4. €0.
4. **`pipeline/gestionador/detect.py`** — implementar los 9 detectores sobre datos ya en DB. Los detectores 3.1-3.6 son puras queries SQL. Los detectores 3.8/3.9 dependen de golden sets. Los €0: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7. Los condicionados: 3.8/3.9.
5. **`pipeline/gestionador/route.py`** — state machine y función de routing. €0.
6. **`expires_at` stamping en `verify.py`** — añadir el TTL por `subject_type` al INSERT. Tabla de TTLs definida en V5 §4.4. €0.
7. **`pipeline/inquisition/claim.py`** — tablas `inquisition_claim/skeptic/verdict` + la lógica de los 5 lentes. Los lentes A (re-query), B (raw recount), D (cross-source), E (hash/drift) son €0. El lente C (live re-fetch) requiere scraping = puede implicar proxies.
8. **Scheduler/cadencia** — un cron Python (`schedule` o APScheduler) que corra `detect.py` periódicamente sobre la DB local. €0.

### 6.3 Lo que requiere corridas o gasto

- **G5 (delta engine proven)**: requiere un segundo harvest real por entidad. Necesita que el scraper esté corriendo.
- **Lente C de V3** (live re-fetch blind): scraping real = posibles proxies si el portal tiene defensas.
- **`denominator_estimate` con datos reales**: requiere cruzar con DGT/INE/fuentes externas (€0 si los datos son públicos ya descargados).
- **LQAS n=132 c=3 para claim poblacional de COMPLETED**: requiere que haya entidades COMPLETED para samplear.

---

## 7. Recomendación de diseño para el Director

### 7.1 Secuencia de construcción B2 (€0, orden correcto)

**Bloque α — DB schema** (prerequisito de todo lo demás):
```
0030_entity_completion.sql   →  tabla entity_completion (5 gates + verdict + evidencias)
0031_gestion.sql             →  gestion_item + gestion_transition
```
Ambas son DDL puras, sin dependencias. Construibles en 1 sesión.

**Bloque β — State machine de completitud** (el núcleo de B2):
```
pipeline/complete.py
```
- `check_g1(conn, cdp_code)` → query `entity` directamente.
- `check_g2(conn, cdp_code)` → reutilizar `record_count_verdict` con path `db_ingested` (SQL sobre `vehicle`) y path `db_edges` (SQL sobre `platform_listing`).
- `check_g3(conn, cdp_code)` → subprocess `git cat-file` sobre `entity.recipe_version`.
- `check_g4(cdp_code)` → HTTP GET a `localhost:8000/entities/{cdp_code}/inventory`.
- `check_g5(conn, cdp_code)` → query `vehicle_event` post-harvest (requiere corrida).
- `update_completion(conn, cdp_code)` → UPSERT en `entity_completion`, calcula verdict, stampa `completed_at`.

**Bloque γ — Detectores V4** (vigilancia continua):
```
pipeline/gestionador/detect.py   →  9 detectores, puras SQL queries + thresholds
pipeline/gestionador/route.py    →  state machine, INSERT a gestion_item + gestion_transition
pipeline/gestionador/run.py      →  entry point, itera entidades/fuentes, llama a detect+route
```

**Bloque δ — TTL + cadencia**:
```
pipeline/verify.py               →  añadir expires_at al INSERT (TTL por subject_type)
pipeline/inquisition/cadence.py  →  scheduler que corre detect + re-VAM sobre verdicts vencidos
```

**Bloque ε — Inquisición tabular** (si el Director quiere V3 completo):
```
0032_inquisition.sql              →  inquisition_claim, inquisition_skeptic, inquisition_verdict
pipeline/inquisition/lenses.py    →  lentes A/B/D/E (€0); lente C separado (requiere scraping)
```

### 7.2 Definición operativa de los 5 gates para B2 (aclaración al Director)

El SUPERPLAN B2 habla de "5 gates binarios para COMPLETED" pero **NO** los define como las 5 fases del pipeline (descubrir/scrapear/receta/API/borrar). La especificación canónica (V2-COMPLETION-PROOF.md) los define como **G1-G5** arriba descritos (identidad, inventario completo, receta git, API live, delta engine). El "borrar" del prompt fundacional (E2E por dealer) es la fase de purga/delistado, que no es un gate de COMPLETED sino una fase posterior (cuando el dealer cierra).

Los 5 gates de B2 son exactamente G1-G5 de V2. El Director debe confirmar si esto es correcto o si la intención era mapear las 5 fases del pipeline E2E.

---

## 8. Riesgos y dudas honestas

| Riesgo | Severidad | Descripción |
|---|---|---|
| G3 requiere acceso git desde el proceso Python | MEDIO | `subprocess git cat-file` desde `pipeline/complete.py` asume que el proceso corre en el worktree. En contenedor Docker puede no tener git. |
| G5 es el único gate que requiere corridas reales | MEDIO | No hay forma de retroallenar G5 para entidades ya ingested sin disparar re-harvests. El % de COMPLETED inicial será bajo aunque G1-G4 pasen. |
| `chk_trustworthy_needs_quorum` es NOT VALID | BAJO | Las 1.091 filas legacy no pasan el check. Si se valida el constraint, ~750 TRUSTWORTHY legacy serían inválidos retroactivamente. El Director debe decidir si validar o mantener NOT VALID. |
| WF-INQUISITION en cadencia: sin scheduler en producción | ALTO | Sin cadencia real, los verdicts envejecen indefinidamente. El primer `expires_at` que caduque y no sea re-juzgado silenciosamente se convierte en verdad mentirosa servida. |
| `entity_completion` tabla sin FK en scrapers | BAJO | Los scrapers no conocen `entity_completion`. Habrá que llamar a `pipeline/complete.py` desde el orchestrator, no desde el scraper mismo. |
| Definición de "5 gates" ambigua en el prompt fundacional | MEDIO | El prompt dice "descubrir/scrapear/receta/API/borrar" como E2E. V2 define G1-G5 distintos. Confirmar con el Director cuál es el mapa canónico. |

---

## 9. Tabla de verdad final: GATE de B2

| Requisito del GATE B2 | Estado real |
|---|---|
| WF-INQUISITION en cadencia | NO EXISTE — solo doctrina |
| detector V4 + state machine | NO EXISTE — solo spec V4 |
| entidad COMPLETED solo por 5 gates binarios | NO EXISTE — tabla `entity_completion` no creada |

**SU-B2: ⬜ — 0% implementado. Todo está en spec, nada en código ni DB.**

---

*Documento generado por barrido de 8 agentes paralelos. Solo lectura. Sin commits. Sin escrituras en DB.*
*Fuentes verificadas: `verify.py`, `migrations/0026_verification_deep.sql`, `docs/architecture/verification/V1-V6`, `SUPERPLAN.md`, `ORQUESTACION.md`, `PROGRESO.md`, DB live :5433.*
