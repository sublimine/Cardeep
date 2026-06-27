# LLM-ROUTING-MATRIX — Capa LLM del Motor Genérico (enrutado por tarea)
> Destilado Ola 1.5 · Director Soberano (CEO-orquestador) · 2026-06-27 · estado: **DISEÑO/SPEC** (Capa-2 = 0 líneas en código hoy, ver §0).
> Fuente: `wave1-stages/_llm.json` (10 categorías investigadas, modelo-por-tarea). Doctrina: [`00-MASTER.md`](00-MASTER.md) · [`ANTI-DRIFT-HARDENING.md`](ANTI-DRIFT-HARDENING.md) · [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md) · [`README.md`](README.md).

---

## Cómo leer esta matriz (navegación)

Esta es la **Capa-2** del modelo de 3 capas ([`00-MASTER.md:12-15`](00-MASTER.md)): IA local obrera, barata, salida forzada por gramática, **llamada por el músculo determinista, no decide nada estratégico**. El determinismo (Capa-1) se queda donde ya gana; Claude (Capa-3) orquesta y adjudica lo irreversible.

**Regla de oro del enrutado** ([`00-MASTER.md:56-57`](00-MASTER.md)): cubrir con LLM **solo donde sube calidad O eficiencia**. Lo determinista (hashing, dedup exacto, geo exacto, regex de precio/km/año) **no se toca**: ya es exacto, auditable, €0 y más rápido que cualquier LLM.

**Leyenda de blindaje** ([`ANTI-DRIFT-HARDENING.md`](ANTI-DRIFT-HARDENING.md)):
- `[VERIFIED path:linea]` — leído en fuente primaria (model card HF / código del repo) esta sesión.
- `[VERIFIED·HF]` — spec/licencia/benchmark confirmado en model card de HuggingFace por el inquisidor de la categoría (registrado en `_llm.json`, no re-leído por mí esta sesión).
- `[ASSUMED]` — no confirmado en fuente primaria, o contestado entre inquisidores → pendiente de 2ª vía (§3). **Jamás se presenta como hecho.**
- `⚠` — open item con causa declarada (rotura integrada, no maquillada).

**Mapa a las 10 etapas** ([`00-MASTER.md:23-35`](00-MASTER.md)): extract/translate → etapa 3 ([`stages/03-extract.md`](stages/03-extract.md)) · classify/dedup/embeddings → etapa 4 ([`stages/04-identity.md`](stages/04-identity.md)) · vision → etapa 5 ([`stages/05-vehicle.md`](stages/05-vehicle.md)) · geo → etapa 6 (sin archivo aún) · recipe → etapa 2 ([`stages/02-scrape.md`](stages/02-scrape.md)) · source-discovery → etapa 1 ([`stages/01-discover.md`](stages/01-discover.md)) · anomaly → etapas 9/7 ([`stages/09-orchestrate.md`](stages/09-orchestrate.md), [`stages/07-quality-seal.md`](stages/07-quality-seal.md)).

---

## 0 · Estado real de la capa (honestidad cruda)

**La Capa-2 hoy es 0 código** [VERIFIED [`00-MASTER.md:14`](00-MASTER.md): *"HOY = 0 en código; se enciende donde se demuestre que el determinismo falla"*]. Por tanto **todo en este documento es DISEÑO/SPEC investigado, no un sistema corriendo**. Ningún modelo aquí está "en producción"; ninguna métrica de calidad propia (F1 por taxonomía/idioma) existe todavía. Lo que está probado es **el músculo determinista** (Capa-1) que estos LLM sólo asistirían en el residuo.

Dos consecuencias que el documento respeta:
1. **El piso es siempre €0 y determinista.** El GPU que da el LLM-local masivo es la **palanca €>0** ([`00-MASTER.md:9`](00-MASTER.md)) — se activa con caso de uso PROBADO + firma del owner, nunca por defecto.
2. **Auto-despliegue por país = aspiración, no hecho.** `00-MASTER` dice que `cover(CC)` instalará la config de enrutado en el bootstrap ([`00-MASTER.md:57`](00-MASTER.md)); eso es **[ASSUMED]** hasta que (a) exista código de Capa-2 y (b) la dimensión país esté enhebrada bajo el esquema (§ siguiente). Ver §4.

---

## ⚠ Dimensión país — la capa LLM hereda un motor country-BLIND (open item transversal)

**Hallazgo (espina dorsal, confirmado por todos los inquisidores e integrado aquí sin maquillar):** `country_code` se enhebró en el **esquema** (mig 0052/0053) y en el prefijo `cdp_code`, pero **NO en la lógica de pipeline/serving/orquestación**. El motor es genérico *por encima* del esquema y **country-blind por debajo**. Verificado de primera mano esta sesión:

| Vector country-blind | Evidencia [VERIFIED] |
|---|---|
| `country_code` existe en el esquema… | [`migrations/0052_country.sql:51-54`](../../migrations/0052_country.sql) (`ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'ES'` en geo_province/comarca/municipality/entity) |
| …pero el pipeline casi no lo usa | `country_code` aparece en sólo 2 archivos de `pipeline/` (`triangulation.py`, `paths.py`); **`geo.py` no lo usa** |
| Geo resuelve **sin filtro de país** y clavado a INE-ES | [`pipeline/geo.py:153,157`](../../pipeline/geo.py) (`SELECT … FROM geo_province / geo_municipality` sin `WHERE country_code`); alias ES `:61-73`; gazetteer INE `:46-48`; cascada "scoped to province — never cross-**province**" `:8` (no cross-**country**) |
| Dedup funde entidades **cross-país** (false-merge) | [`pipeline/identity/cluster_dealers.py:404-430`](../../pipeline/identity/cluster_dealers.py): aristas con clave `(norm_name, muni)` / `(phone, muni)` / `(host, muni)` — **sólo `municipality_code`, sin `country_code`**. DE reusa el code `28` de Madrid → mismo bucket union-find que un dealer ES |
| Anchos `CHAR(2)`/`CHAR(5)` = formato INE-ES | [`migrations/0001_geo.sql:5,19`](../../migrations/0001_geo.sql) ("INE province code, 2 digits" / "municipality code, 5 digits"); CHECK ES `left(code,2)=province_code` aplazado a onboarding [VERIFIED [`0052_country.sql:32-34`](../../migrations/0052_country.sql)] |
| `cdp_code` con segmento provincia INE-ES | Datos vivos todos `CDP-ES-NN-…` (NN = provincia INE 2-díg). Prefijo `CDP-{CC}-` es paramétrico [`00-MASTER.md:37`](00-MASTER.md), pero el segmento `NN` y el regex G1 `^CDP-ES-` son **[ASSUMED]** ES-clavados (no re-verifiqué el regex G1 en código esta sesión) |

Esto **ya está elevado a invariante mecánico** en [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md) (fix + guard + golden cross-country, €0). Esta matriz **no lo re-litiga**; declara cómo la rotura impacta el enrutado LLM y qué exige la capa antes de servir un 2º país:

| Categoría LLM | Cómo le pega el country-blind | Qué exige (hardening) |
|---|---|---|
| **dedup-adjudicate** | El adjudicador LLM vive **aguas abajo** del bloqueo country-blind (`cluster_dealers.py:404-430`): recibe (y el auto-merge determinista ya funde) pares ES↔DE. | `country_code` como **gate duro ANTES del LLM**: distinto país → AUTO-DISTINCT, nunca se adjudica; el `evidence` del prompt **debe** llevar `country_code`. Bloqueado por el golden de COUNTRY-PROOF. |
| **geo-disambiguate** | La recuperación de candidatos (`geo.py`) es ES-INE-only y sin filtro de país: para un 2º país no hay candidatos correctos (o peor, elige uno ES para una dirección DE). | Retrieval **country-scoped** + adaptador de gazetteer por país (INE/INSEE/AGS/ISTAT) antes de enrutar geo-LLM a no-ES. La gramática de salida (índice de candidato) ya impide alucinar un code. |
| **extract-fields / translate-normalize** | Emiten campos geo + `cdp_code` con formato `CHAR(2)/CHAR(5)` INE y CHECK `left(code,2)=province_code` ES-clavado. "Locale" se usa como proxy de país y está ES-clavado. | Grammars/enums/gazetteers/golden-sets **keyed por país** (y por idioma ≠ país: ES se habla fuera de ES, DE en DE/AT/CH). Aplazado a la migración de onboarding. |
| **anomaly-escalation / source-discovery** | Locks globales + API mezcla países; los `decision_request` y el registro de denominadores no scopean país; el scheduler due-select/silence/locks sin predicado de país. | `country_code` en el envelope `decision_request` y en el registro de fuentes-denominador; routing de escalada y denominadores **por país**. |

**Criterio de aceptación de la capa LLM** (heredado de COUNTRY-PROOF): ninguna categoría se declara country-proof sin su **golden cross-country en verde** ([`COUNTRY-PROOF-INVARIANT.md:13-25,52`](COUNTRY-PROOF-INVARIANT.md)). Hasta entonces, el enrutado LLM es **single-tenant ES `[ASSUMED]`-multi-país**.

---

## 1 · Tabla resumen (categoría · modelo · licencia · local/cloud · €0)

| # | Categoría | Modelo recomendado | Licencia | Local/Cloud | €0 | Verif. |
|---|---|---|---|---|:---:|---|
| 1 | **extract-fields** | Qwen3-4B-Instruct-2507 | Apache-2.0 | either (local-first) | ✅ | `[VERIFIED·HF]` |
| 2 | **classify-dealer** | mmBERT-base (fine-tuned seq-cls) | MIT | local | ✅ | `[VERIFIED·HF]` modelo · F1-taxonomía `[ASSUMED]` |
| 3 | **dedup-adjudicate** | Qwen3.5-35B-A3B (thinking) **⚠`[ASSUMED]`** · piso: DeepSeek-R1-Distill-Qwen-14B `[VERIFIED·HF]` | Apache-2.0 / MIT | local | ✅ | recomendado **contestado** (§3 #1) |
| 4 | **embeddings-blocking** | Qwen3-Embedding-0.6B | Apache-2.0 | local | ✅ | `[VERIFIED·HF]` |
| 5 | **geo-disambiguate** | Qwen3-8B (instruct) | Apache-2.0 | local | ✅ | `[VERIFIED·HF]` |
| 6 | **vision-photo** | Qwen3-VL-4B/8B-Instruct (+ SigLIP2 + pHash para matching) | Apache-2.0 | local | ✅ | `[VERIFIED·HF]` (235B licencia `[ASSUMED]`) |
| 7 | **recipe-synth** | Qwen3-Coder-Next (80B-A3B MoE) | Apache-2.0 | local | ✅ | `[VERIFIED·HF]` |
| 8 | **translate-normalize** | Qwen3-Embedding-0.6B + Qwen3-4B-Instruct (cola) | Apache-2.0 | local | ✅ | `[VERIFIED·HF]` |
| 9 | **source-discovery** | Tongyi-DeepResearch-30B-A3B (+ Mistral Large 3 lectura UE) | Apache-2.0 | local | ✅ | `[VERIFIED·HF]` |
| 10 | **anomaly-escalation** | Qwen3-30B-A3B-Instruct-2507 (non-thinking) | Apache-2.0 | local | ✅ | `[VERIFIED·HF]` |

**Lectura del cuadro:** 10/10 categorías €0 local-first; 9/10 Apache-2.0 (classify-dealer = MIT, igual de limpio). **Único modelo recomendado contestado: dedup-adjudicate** — descansa en un checkpoint Qwen3.5-35B-A3B que 3 de 5 inquisidores **no** pudieron confirmar en fuente primaria (§3 #1); su **piso verificado** es DeepSeek-R1-Distill-Qwen-14B (MIT, 98.23% F1 OpenSanctions Pairs `[VERIFIED·HF]`). Cloud/€>0 (DeepSeek-V4, Claude) sólo como palanca capa-3.

---

## 2 · Matriz por categoría

> Plantilla por categoría: **Modelo** · **Determinista (se queda)** · **Guardrail cero-pérdida** · **A→Z** · **Claude (capa-3)** · **€0 vs €>0** · **Dimensión-país** (donde es load-bearing).

### 2.1 · extract-fields — campos del residuo ambiguo del anuncio
**Modelo:** `Qwen3-4B-Instruct-2507` · Apache-2.0 · 4B (3.6B non-emb), 262K ctx, non-thinking · either (local-first) · €0 `[VERIFIED·HF]`.
- **Determinista (se queda):** precio/km/año por regex + normalización de moneda/separadores; combustible/cambio por gazetteer multilingüe a **enum CERRADO**; make por gazetteer ~60 OEM + rapidfuzz; dedup exacto (hash), geo exacto. El LLM **sólo** entra en el residuo sin anclas: split model/trim (`Golf 2.0 TDI GTD`→model=Golf, trim=GTD), precio ambiguo (cuota/PVP/IVA/tachado), cola de combustible/cambio (PHEV, DSG→automático).
- **Guardrail cero-pérdida (5 capas):** (1) decodificación por gramática vLLM+xgrammar (`guided_json` sobre JSON-Schema) → 0 parse-fails, enum/regex en la gramática → emitir fuera de vocabulario es **físicamente imposible** (mapea [`ANTI-DRIFT-HARDENING.md:§1.1`](ANTI-DRIFT-HARDENING.md)); (2) cross-check det.↔LLM en precio/km/año → **gana el determinista**, se marca el conflicto (`§1.5`); (3) gate de confianza (logprob) → cola Claude; (4) provenance por campo (`§1.2`); (5) golden-set multilingüe F1 con gate de CI cero-regresión (`§1.6`).
- **A→Z:** blob HTML → preproceso (readability, strip boilerplate, locale, pre-extracción regex/gazetteer + score) → router (alta-confianza y consistente → emite **sin LLM**; si no → LLM) → Qwen3-4B en vLLM (`guided_json` + gramática de enums) → registro canónico make/model/trim/precio/km/combustible/cambio + provenance → verificación (cross-check, enum, golden-F1) → commit PG / escala a Claude.
- **Claude (capa-3):** fuera del hot-path; adjudica strings model/trim novedosos/contaminados, semántica de precio en conflicto, idioma nuevo donde el 4B duda; diseña/evoluciona plantilla + gramática y cura el set etiquetado multilingüe.
- **€0 vs €>0:** €0 = Tier-0 determinista (CPU) + GLiNER2-multi (205M CPU) + Qwen3-4B GGUF Q4/Q8 en CPU/GPU consumo (llama.cpp). €>0 (gate: backlog nacional + firma) = 1 GPU L4/A10/4090 con vLLM+xgrammar para batched; tier VLM (NuExtract) sólo si hace falta extracción **visual** a escala.
- **Dimensión-país:** los campos geo y el `cdp_code` que emite heredan el formato INE-ES `CHAR(2)/CHAR(5)` (ver § transversal). Locale ≠ país: la gramática/gazetteer deben keyear por país+idioma.

### 2.2 · classify-dealer — tipología del punto de venta (conjunto cerrado)
**Modelo:** `mmBERT-base` fine-tuned (seq-cls multiclase + cabeza segment) · MIT · 307M (140M small CPU), ctx 8192 · local · €0 `[VERIFIED·HF]`. *Matiz honesto: aquí "LLM-amenable" = un **encoder aprendido** bate al determinismo en la porción ambigua; el óptimo es la cascada gazetteer→encoder→LLM-pequeño→Claude, no "LLM en todo".*
- **Determinista (se queda):** gazetteer/regex de **alta precisión** resuelve la cabeza inequívoca a coste 0 (Desguace/Schrott/Casse→desguace; Concesionario Oficial/Vertragshändler+marca→concesionario_oficial; Taller/Werkstatt→garaje). También: dedup exacto, validación final del enum, derivación de `segment` por lookup marca→premium/generalista, umbral+routing.
- **Guardrail cero-pérdida:** (1) conjunto cerrado: softmax sobre 6 clases + cola generativa con gramática enum XGrammar → **0 etiquetas inválidas**; (2) confianza calibrada (temperature scaling) + umbral de abstención τ → escala encoder→Qwen3-4B→Claude, nunca adivina; (3) 2ª vía: gazetteer y encoder deben concordar en la cabeza, discrepancia → escala; (4) gold eval por idioma, gate macro-F1 ≥ baseline determinista (cero-regresión); (5) fallback conservador → `no-es-dealer`/`particular` + flag; **jamás fabricar `concesionario_oficial`** (clase de alto valor) sin evidencia.
- **A→Z:** nombre+snippet+idioma → preproceso (quita ruido jurídico, trunca 8192) → **gazetteer det.** (salta el modelo en inequívocos) → mmBERT forward + softmax 6-clases + cabeza segment → calibración → conf≥τ acepta / conf<τ escala Qwen3-4B→Claude → validación enum → escribe label+segment+confianza+provenance → gate gold → **active-learning** (las muestras de baja confianza/adjudicadas por Claude reentrenan el encoder: profesor→alumno).
- **Claude (capa-3):** gold labeling de cold-start por país/idioma (etiqueta miles, el encoder sirve millones); adjudica el límite `concesionario_oficial` vs `compraventa` Tier-1; evolución irreversible de taxonomía/segment; firma del gate al abrir país.
- **€0 vs €>0:** €0 = gazetteer + mmBERT/EmbeddingGemma/GLiClass en CPU o GPU libre (Colab/Kaggle); entrenar = pocas GPU-horas one-off en compute prestado. €>0 (gate: backlog/SLA o bootstrap masivo + firma) = batch Qwen3-4B+ en GPU alquilada. El encoder local es siempre el suelo.
- **Dimensión-país:** `segment` y gazetteer son por país; el gold eval se mide **por idioma** antes de publicar (no hay F1 público para esta taxonomía → §3 #3).

### 2.3 · dedup-adjudicate — banda gris del entity-matching (irreversible)
**Modelo:** `Qwen3.5-35B-A3B` (thinking) **⚠`[ASSUMED]`** · Apache-2.0 · 35B/3B activos MoE, 262K ctx · local · €0. **Piso verificado:** `DeepSeek-R1-Distill-Qwen-14B` · MIT · 14B denso (~8-9GB en 4-bit) · **98.23% F1** en OpenSanctions Pairs `[VERIFIED·HF]` (vs reglas 91.33%, GPT-4o 98.95%). *El recomendado Qwen3.5 está contestado entre inquisidores (§3 #1); hasta confirmarlo en HF + calibrar en hold-out local, **el piso manda**.*
- **Determinista (se queda):** **el grueso NO toca LLM.** Blocking/generación de candidatos; short-circuit por clave fuerte (mismo VAT/cdp_code/dominio/teléfono E.164 → AUTO-MERGE); baja-similitud → AUTO-DISTINCT; features (rapidfuzz Jaro-Winkler/token-set, libpostal, geo, legal-suffix); union-find + cierre transitivo. *El propio paper recomienda invertir en blocking/clustering, no en el pairwise (saturado ~98%).*
- **Guardrail cero-pérdida (7 capas):** (1) salida fija por gramática `{verdict: same|different|uncertain, confidence, evidence_fields[], conflicting_signals[]}` → 0 malformados; (2) **2ª vía determinista**: cada `evidence_field` citado se **re-verifica** contra los registros reales (caza racionalización alucinada); (3) umbral de confianza calibrado en hold-out → abstención `uncertain`, nunca verdict forzado; (4) **sesgo asimétrico conservador**: ante duda → DISTINCT (un MERGE erróneo colapsa dos entidades reales, caro de deshacer); (5) alto riesgo (Tier-1, cross-script) → concordancia 2-de-2 (Qwen3.5 + Magistral) o self-consistency, si no hay consenso → Claude; (6) fallback al scorer de reglas si el LLM cae; (7) **gate de promoción**: Qwen3.5 sólo sustituye al distill-14B tras igualar/superar su F1 en hold-out local.
- **A→Z:** par candidato (del blocking) → preproceso det. (normaliza legal-suffix/dirección/teléfono/VAT; feature-vector) → gate det. (clave-fuerte→MERGE; todo-débil→DISTINCT; intermedio→banda gris) → Qwen3.5-35B-A3B (thinking) + gramática JSON-schema → `{verdict, confidence, evidence, conflicts}` → verificación (schema + re-chequeo de evidencia + umbral + sesgo DISTINCT) → commit union-find (alta confianza) / escala (uncertain, Tier-1, cross-script, desacuerdo 2-de-2 → Claude).
- **Claude (capa-3):** MERGE de alto valor/Tier-1 (corona, grandes grupos), transliteración cross-script no-UE (modo de fallo del benchmark), escalados `uncertain`, desempate Qwen3.5↔Magistral, y la POLÍTICA de qué cuenta como "misma" entidad.
- **€0 vs €>0:** €0 = blocking det. + Qwen3.5 (o el distill-14B verificado) cuantizado en hardware modesto (MoE 3B activos → CPU/1-GPU). €>0 (gate: backlog de banda gris o caso irreversible + firma) = GPU dedicada o API metered (Claude/DeepSeek-V4) para capa-3 de máximo riesgo.
- **Dimensión-país ⚠:** **el impacto más fuerte.** El bloqueo upstream es country-blind [VERIFIED `cluster_dealers.py:404-430`]: el LLM puede recibir pares ES↔DE y el auto-merge det. ya los funde antes. **Hardening obligatorio:** `country_code` como gate duro pre-LLM (distinto país → AUTO-DISTINCT) y en el `evidence` del prompt. Bloqueado por el golden cross-country de [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md).

### 2.4 · embeddings-blocking — recall de candidatos cross-lingüe
**Modelo:** `Qwen3-Embedding-0.6B` · Apache-2.0 · 600M, MRL dim 32-1024, 32K ctx · local · €0 `[VERIFIED·HF]`. *Genera candidatos, **no decide** — la precisión la fija el adjudicador (2.3).*
- **Determinista (se queda):** el embedding **complementa**, no sustituye, el blocking exacto. Quedan det.: dedup por content-hash y nombre normalizado; fonético (Double Metaphone/Soundex, Cologne para DE); geo-exacto (CP, celda lat/long); claves estructuradas (teléfono E.164, dominio, VAT/NIF); trigram/edit-distance (pg_trgm). El embedding sólo aporta la rebanada semántica/cross-lingüe/reordenada que el léxico no alcanza.
- **Guardrail cero-pérdida:** (1) el embedding sólo **PROPONE** con alto recall, nunca decide → un embedding flojo no degrada ninguna decisión de merge; (2) candidatos = UNIÓN(claves deterministas, ANN top-k) → sólo **añade** recall, jamás quita garantías det.; (3) calibración del umbral coseno sobre pares etiquetados por idioma (recall@k, Pair-Completeness, Reduction-Ratio); (4) puerta de precisión por cross-encoder reranker (Qwen3-Reranker-0.6B/4B o bge-reranker-v2-m3) antes del adjudicador caro; (5) fallback: si el embedding cae, el blocking det. sigue generando candidatos (recall degradado, cero outage); (6) auditoría adversarial sobre duplicados-conocidos difíciles.
- **A→Z:** texto nombre/anuncio → normaliza (sufijos legales, unicode-fold, idioma) → emite claves det. → Qwen3-Embedding-0.6B con instrucción de tarea, vector truncado por Matryoshka → pgvector/FAISS HNSW ANN top-k → **UNIÓN** con candidatos det. → poda por reranker → pares → adjudicador (2.3) → commit grafo + cachea vector por content-hash.
- **Claude (capa-3):** adjudica los pares que el reranker no separa (merges cross-lingüe ambiguos, oficial vs independiente, elección de entidad canónica). El embedding nunca escala un merge solo.
- **€0 vs €>0:** €0 = Qwen3-Embedding-0.6B (o EmbeddingGemma-300M si el cuello es CPU/edge) + ANN pgvector + claves det. €>0 (gate: déficit de recall medido en idiomas/scripts no-UE + firma) = GPU para re-embed masivo o subir a Qwen3-Embedding-4B / Llama-Embed-Nemotron-8B (SOTA cross-lingual). **Jina-v3 EXCLUIDO** (CC-BY-NC, no comercial) `[VERIFIED·HF]`.
- **Dimensión-país:** el umbral ANN se calibra por idioma; reutiliza pgvector sobre el PG/pglite existente (sin infra nueva). El country-scoping del par lo impone el gate de dedup (2.3), no el embedding.

### 2.5 · geo-disambiguate — elegir el código administrativo correcto
**Modelo:** `Qwen3-8B` (instruct, hybrid thinking) · Apache-2.0 · ~8B denso · local · €0 `[VERIFIED·HF]`. *La tarea es elegir entre candidatos **ya recuperados** del gazetteer con razonamiento ligero → 8B es el óptimo calidad/throughput, no hace falta frontera.*
- **Determinista (se queda):** lookup exacto en gazetteer, dedup exacto, fuzzy trigram/edit-distance, tablas CP↔unidad administrativa, punto-en-polígono, país por TLD/teléfono, recuperación por embeddings, y **—crítico— la ASIGNACIÓN del código administrativo SIEMPRE sale del gazetteer/geocoder autoritativo** (GeoNames, OSM/Nominatim, INE/INSEE/AGS/ISTAT/CAOP), **nunca generada por el modelo**.
- **Guardrail cero-pérdida:** (1) decodificación restringida a vocabulario **CERRADO**: el LLM sólo emite un índice/ID del set de candidatos recuperado, o `ABSTAIN` → alucinar un code inexistente es estructuralmente imposible; (2) 2ª vía det.: el code elegido se cruza con CP↔unidad, punto-en-polígono, provincia/región, hint de país → contradicción → rechazo+escala; (3) top-1 único y de alta confianza salta el LLM (100% det.); (4) fallback al top-1 del geocoder con flag; (5) provenance por fila + muestreo de auditoría.
- **A→Z:** dirección/municipio libre + hint país → preproceso (normaliza, expande abreviaturas, idioma, NER toponímico) → **recuperación det.** en gazetteer/geocoder → top-K candidatos con metadatos → rama: ¿único y alta confianza? → devuelve det. €0; si no → Qwen3-8B con gramática restringida al índice → elige/abstiene → verificación det. (CP↔unidad, polígono, región) → emite code+confianza+provenance / escala a Claude → commit.
- **Claude (capa-3):** señales contradictorias donde la verificación rechaza; **onboarding de la jerarquía administrativa de un país NUEVO** (mapear códigos oficiales, exónimos — decisión de schema casi irreversible); "no hay candidato pero el texto referencia un lugar"; auditoría adversarial.
- **€0 vs €>0:** €0 = gazetteer/geocoder + Qwen3-8B (o 4B) local cuantizado. €>0 (gate: volumen residual × latencia, u onboarding a escala + firma) = GPU compartida (vLLM Qwen3-8B/14B o Gemma-3-12B). Palanca €0 opcional: LoRA de Qwen3-4B sobre resoluciones ya verificadas.
- **Dimensión-país ⚠:** **el segundo impacto más fuerte.** `geo.py` recupera **sin filtro de país y clavado a INE-ES** [VERIFIED `geo.py:153,157,61-73`]: para un 2º país no hay candidatos correctos. **Hardening:** retrieval country-scoped + adaptador de gazetteer por país (etapa 6, motor=cascada / pack=árbol administrativo) **antes** de enrutar geo-LLM a no-ES.

### 2.6 · vision-photo — tipo de imagen, atributos y OCR de carteles
**Modelo:** `Qwen3-VL-4B-Instruct` (workhorse) / `8B` (casos duros) · Apache-2.0 (2B-32B + 30B-A3B; 235B licencia `[ASSUMED]`) · local · €0 `[VERIFIED·HF]`. *Matiz: **la mitad de MATCHING de esta tarea NO es LLM-generativa** — es encoder frozen + ANN + pHash. El VLM gana sólo en razonamiento/atributos/OCR multilingüe, y por eso corre **gated, jamás por foto**.*
- **Determinista (se queda):** (1) **pHash** = verdad de duplicado exacto/casi-exacto (µs CPU, intocable); (2) encoder de embeddings **FROZEN** (SigLIP2 Apache-2.0 / DINOv3) + ANN coseno FAISS = near-dup semántico + same-unit + probe lineal stock-vs-real, corre sobre el **100%** de fotos en CPU/GPU modesta. Pasar el VLM por cada foto sería 10-100× más caro sin mejorar el dedup.
- **Guardrail cero-pérdida:** (a) pHash sigue siendo ground-truth; el embedding sólo **SUMA** recall con umbral calibrado, nunca revierte pHash; (b) salida del VLM por gramática/JSON-schema con enums estrictos `{real_lot_photo|studio_render|catalog_stock|screenshot|collage|other}` + booleanos watermark/overlay → cero texto libre; (c) umbral + ABSTENCIÓN → dudoso a cola Claude/humano; (d) 2ª vía: make/model del VLM se cruza con texto del listing + OCR matrícula/VIN + voto de vecinos-embedding; (e) modelos congelados/versionados + gold-set de regresión, fallback = pHash + vecino-embedding.
- **A→Z:** fotos → preproceso (decode, strip EXIF, resize, **dedup pHash primero**) → encode embedding (SigLIP2/DINOv3) → ANN FAISS (dedup/same-unit) + probe lineal stock-vs-real → fiable y no-ambiguo: COMMIT; ambiguo o se piden atributos: VLM Qwen3-VL (JSON-schema) extrae make/model/trim/color/carrocería + clasifica tipo + OCR watermark → 2ª vía + gate → COMMIT / escala → los labels engordan el gold-set y reentrenan el probe.
- **Claude (capa-3):** define el rubric stock-vs-real y el gold-set; arbitra clusters donde se juega si una foto-cluster es un punto de venta físico real o un revendedor reposteando catálogo OEM (juicio estratégico del censo de huella digital); decide swaps de modelo (cambio irreversible de pipeline).
- **€0 vs €>0:** €0 = pHash + SigLIP2/DINOv3 (CPU/GPU modesta) + probe lineal + Qwen3-VL-2B/4B en GPU local para llamadas gated. €>0 (gate: volumen de fotos ambiguas que supere el throughput local + firma) = Qwen3-VL-8B/30B-A3B a escala censal o API hosted.
- **Dimensión-país:** OCR multilingüe (32 idiomas) cubre carteles/marcas de agua ES/DE/FR/IT/PT — la dimensión país aquí es de idioma del cartel, no de código administrativo.

### 2.7 · recipe-synth — síntesis/reparación de recetas de extracción
**Modelo:** `Qwen3-Coder-Next` (80B-A3B MoE, Gated-DeltaNet) · Apache-2.0 · 80B/3B activos, 256K ctx, GGUF ~40-45GB · local · €0 `[VERIFIED·HF]` (SWE-bench Verified 70.6 / Pro 44.3). *El LLM **SINTETIZA**; el determinismo **EJECUTA, DETECTA y VALIDA**.*
- **Determinista (se queda):** (1) la **ejecución** del selector contra el DOM (lxml/parsel) — es un parser; (2) preproceso HTML→DOM-limpio; (3) **detección de recipe-rot** por harness de aserciones (campos vacíos, drift de conteo, regex teléfono/CP/email, JSON-schema) — detectar rot con LLM sería más caro y menos fiable; (4) validación de campos; (5) dedup/hashing de páginas.
- **Guardrail cero-pérdida:** (1) gramática/JSON-schema → cero selectores malformados; (2) **2ª vía det. "execute-and-verify"**: cada receta sintetizada se **ejecuta** inmediatamente sobre la página muestra y su salida se contrasta con aserciones + rango de conteo; receta que no extrae datos válidos se **RECHAZA** y se realimenta (self-repair acotado a N); (3) golden-fixture congelado para Tier-1 → cero regresión silenciosa; (4) escalera con piso duro: workhorse→GLM-4.7→Claude, el piso lo impone el validador; (5) fallback honesto: si todos los tiers fallan validación → marca para Claude/owner, **nunca publica receta rota en silencio**.
- **A→Z:** URL/HTML muestra (en rot: + receta vieja + fallo) → preproceso det. (fetch; Playwright si JS-heavy; strip; poda DOM; idioma) → Qwen3-Coder-Next (schema-constrained; prompt = DOM limpio + spec de campos + esquema) → receta (selectores CSS/XPath + field-map) → **verificación det. execute-and-verify** (ejecuta, asevera, golden-fixture, self-repair) → commit de receta **versionada** al registry / escala GLM-4.7→Claude (Tier-1 → firma owner antes de bendecir).
- **Claude (capa-3):** ~1-2% genuinamente difícil/irreversible: Tier-1 donde los abiertos no pasan validación, DOM adversarial/anti-bot, ambigüedad de cuál estrategia es canónica, y **bendecir la receta canónica de una fuente faro** de la que depende el censo nacional.
- **€0 vs €>0:** €0 = Qwen3-Coder-Next local (GGUF en llama.cpp/vLLM; viable CPU+RAM por los 3B activos) + toda la verificación det. €>0 (gate: tasa de fallo-validación sostenida o fuente Tier-1 valiosa + firma) = GLM-4.7 / DeepSeek-V4-Pro self-host o API, Claude capa-3.
- **Dimensión-país:** las recetas son por plataforma/fuente (pack de país, etapa 2); el motor de síntesis es invariante.

### 2.8 · translate-normalize — canonicalización cross-lingüe de carrocería/combustible/trim
**Modelo:** `Qwen3-Embedding-0.6B` (motor de normalización) + `Qwen3-4B-Instruct` + XGrammar (cola generativa) · Apache-2.0 · local · €0 `[VERIFIED·HF]`. *90% MATCHING/canonicalización (Limousine/berlina/saloon/sedan→1 centroide), no generación. **NLLB-200 PROHIBIDO** (CC-BY-NC + traduce nombres propios) `[VERIFIED·HF]`.*
- **Determinista (se queda):** la **identidad** de marca/modelo (nombres propios) **NO se traduce**: VW Golf ≠ golf deporte, SEAT ≠ asiento. Cabeza Pareto = gazetteer canónico make→model→generación + alias + rapidfuzz `[VERIFIED geo.py:278 usa rapidfuzz]`. También det.: dedup por hash, parsing numérico (cilindrada, kW↔CV, año), códigos motor/caja por regex (TDI/dCi/PureTech/EAT8/4MATIC), VIN/WMI. **El LLM nunca sobreescribe un match det. de alta confianza.**
- **Guardrail cero-pérdida:** decodificación por gramática (XGrammar/GBNF) a enum canónico → emitir fuera de taxonomía es **físicamente imposible**; cascada de umbrales (léxico exacto → rapidfuzz≥θ → coseno≥τ → LLM); clase de **ABSTENCIÓN `UNKNOWN`** obligatoria (nunca fuerza encaje); 2ª vía = acuerdo entre dos familias de embeddings (Qwen3 + e5/BGE-M3) o back-mapping → sólo auto-commit si concuerdan; entidades nuevas **no se autocrean** (van a revisión); cada resolución confirmada se añade como alias → la cabeza crece, la cola y el coste LLM se encogen.
- **A→Z:** crudo (ES/DE/FR/IT/PT) → preproc (NFKC, expansión de abreviaturas) → [1] léxico+rapidfuzz≥θ → canónico €0 → [2] embed 0.6B, coseno≥τ vs centroides → canónico €0 → [3] Qwen3-4B + XGrammar → canónico o UNKNOWN → [4] 2ª vía inter-embedding → [5] ambiguo/Tier-1 → Claude → [6] commit + alias nuevo (auto-aprendizaje).
- **Claude (capa-3):** desambiguación cross-mercado (mismo trim = cosas distintas por país), fronteras de generación/año, colisiones de marca; diseño/auditoría del **esquema de taxonomía canónica**; toda **fusión de entidades canónicas** (difícil de revertir).
- **€0 vs €>0:** €0 = léxico + rapidfuzz + Qwen3-Embedding-0.6B (CPU) + Qwen3-4B Q4 (GBNF). €>0 (gate: backlog × latencia para re-normalización masiva histórica + firma) = vLLM+XGrammar y/o Qwen3-Embedding-8B en GPU.
- **Dimensión-país:** el "mismo trim por país" es exactamente el caso Claude; la taxonomía canónica debe ser país-consciente sin duplicar la identidad de marca.

### 2.9 · source-discovery — hallar el registro/denominador autoritativo de un país
**Modelo:** `Tongyi-DeepResearch-30B-A3B` (+ `Mistral Large 3` lectura in-language UE) · Apache-2.0 · 30.5B/3.3B activos MoE · local · €0 `[VERIFIED·HF]` (BrowseComp 43.4 / GAIA 70.9 / FRAMES 90.6). *Único open-weight RL-entrenado para búsqueda profunda multi-hop — la capacidad que aquí bate al determinismo.*
- **Determinista (se queda):** el crawl (fetch HTTP, robots.txt, sitemap, HTML→texto), canonicalización de dominio, dedup de URLs, y **el MAPA CACHEADO de registros conocidos** (ES→BORME/DIRCE-INE, DE→Handelsregister, FR→INSEE-SIRENE, IT→Registro Imprese, PT→RNPC). Para un país ya mapeado **NO se invoca LLM**: es lookup O(1). Re-derivar una verdad estable es quemar computo y arriesgar alucinación.
- **Guardrail cero-pérdida:** (1) JSON-schema tipado por candidato `{country, source_name, url, source_type, authority_tier, language, evidence_url, evidence_snippet, confidence}` → cero texto libre; (2) 2ª vía det.: se acepta sólo si resuelve a dominio vivo (HTTP 200), la autoridad casa con señal esperada (TLD oficial .gob/.gouv/.gov o cita en 2ª búsqueda independiente) y aporta **evidencia citada, nunca inventada**; (3) umbral + gate → bajo umbral o Tier-1 → Claude antes de commit; (4) el mapa cacheado es el suelo, el LLM sólo **añade**; (5) eval offline con golden de ~30 países de denominador conocido.
- **A→Z:** país + hints idioma + queries semilla → preproceso (carga mapa cacheado; si mapeado+verificado → emite cacheado, **FIN sin LLM**) → no-mapeado/refresco: bucle agéntico Tongyi (ReAct, tools search+fetch; Mistral Large 3 asiste lectura UE) → candidatos JSON-schema → verificación det. (HTTP vivo + TLD/autoridad + corroboración 2ª fuente) → gate → commit al registro de fuentes / Claude (baja/Tier-1) → re-scan trimestral.
- **Claude (capa-3):** países sin registro central evidente, estructuras federales/fragmentadas, no-UE de gobernanza opaca, y el **juicio de qué cuenta como denominador autoritativo** con candidatos en conflicto; curación inicial del mapa cacheado + revisión del golden.
- **€0 vs €>0:** €0 = Tongyi + Mistral Large 3 sobre GPU local/existente o free-tier; discovery es **batch de baja frecuencia y alto valor** (1 pasada/país + refresco trimestral), tolera latencia alta. €>0 (gate: país Tier-1 con confianza bajo umbral, o cadencia que exija palanca GPU + firma) = llamada puntual a Claude API.
- **Dimensión-país ⚠:** el registro de fuentes-denominador **debe scopear `country_code`**; los locks/API globales (ver § transversal) mezclarían denominadores entre países. **Caveat load-bearing:** el RL de Tongyi es EN/ZH → para fuentes en lengua UE se apoya/cae a Mistral Large 3 (no es una sola caja).

### 2.10 · anomaly-escalation — narrar la anomalía y empaquetar el `decision_request`
**Modelo:** `Qwen3-30B-A3B-Instruct-2507` (non-thinking) · Apache-2.0 · 30.5B/3.3B activos MoE, 262K ctx · local · €0 `[VERIFIED·HF]`. *El modelo **NARRA, no decide**; non-thinking = rápido, controlable, menos divagación fabricada.*
- **Determinista (se queda):** la **DETECCIÓN** de la anomalía NO la toca el LLM: outliers (z-score/IQR), violaciones de regla, validación de schema, dedup por hashing, distancia geo, regex de precios/IDs, integridad referencial → todo computa el `evidence payload`. También det.: el **schema** del envelope `decision_request`, el routing por severidad, los umbrales, la dedup de escaladas (idempotency key) y el ensamblado+validación del JSON. El LLM sólo rellena lenguaje natural (`por_que_sospechoso`, `resumen`, `pregunta_para_Claude`).
- **Guardrail cero-pérdida (5 capas):** (1) gramática/JSON-schema (GBNF/XGrammar/`guided_json`) → envelope siempre schema-válido; (2) **validador de GROUNDING anti-fabricación**: cada número/ID/URL citado en la narrativa **debe existir literalmente** en el evidence dict; si cita un valor inexistente → rechazo+regeneración; (3) fallback det.: tras 2 fallos o modelo caído → narrativa por **plantilla** desde la evidencia (la escalada sale igual, cero cliff); (4) gating por severidad → la narración **nunca decide**, Tier-1/irreversible llega a Claude pase lo que pase; (5) temp baja (0.2-0.3) para fidelidad, no creatividad.
- **A→Z:** el motor det. marca registro/cluster y emite evidence payload (signal_type, observado/esperado, z-score/rule_id, fuentes, cdp_code, locale) → preproceso (evidence dict compacto, locale, dedup contra escaladas abiertas, tier de severidad) → Qwen3-30B-A3B con gramática de `{por_que_sospechoso, resumen, pregunta}` en el idioma del registro (temp baja, non-thinking) → el código envuelve en el envelope canónico → verificación (grounding + JSON-schema + guard PII; fallo → regenera 1× → plantilla det.) → encola el `decision_request`; Tier-1 → Claude/cola humana; menores → revisión batched.
- **Claude (capa-3):** es el **CONSUMIDOR** del `decision_request` en lo más difícil: decisiones irreversibles, caza de receta Tier-1, ambigüedad estratégica, evidencia contradictoria. El modelo local **prepara** el paquete; Claude emite el **JUICIO**. Audita periódicamente una muestra por deriva de fidelidad.
- **€0 vs €>0:** €0 = Qwen3-30B-A3B (o 4B/8B tier barato) local vía llama.cpp/vLLM cuantizado + gramática; la plantilla de fallback es €0 y siempre disponible. €>0 (gate: volumen de escaladas > SLA local, o batch Tier-1 que exija más fidelidad multilingüe no-UE + firma) = palanca GPU / Qwen3.5-235B hosted. El consumo de Claude es la vía €>0 deliberada para los poquísimos casos duros.
- **Dimensión-país ⚠:** `cdp_code` y `locale` del evidence payload heredan el pin ES (ver § transversal); el envelope y el routing de escalada **deben scopear país** (locks globales mezclarían colas entre países).

---

## 3 · Pendiente de verificar por 2ª vía (flags `[ASSUMED]`)

> Respeta el mandato: los flags "A VERIFICAR antes de producción" de las notas se listan aquí como `[ASSUMED]` pendientes de 2ª vía, **no como hechos**. Ordenados por impacto.

| # | Flag `[ASSUMED]` | Categoría(s) | 2ª vía requerida | Impacto si falla |
|---|---|---|---|---|
| 1 | **Qwen3.5/Qwen3.6-35B-A3B existe como checkpoint instruct/thinking de texto en fuente primaria.** Contestado: dedup y source-discovery lo dan `[VERIFIED·HF]`; geo, anomaly y extract lo dan **NO confirmado / secundario**. Por blindaje (un ASSUMED jamás se presenta como VERIFIED), prevalece la versión conservadora. | dedup (**recomendado**), source-discovery (alt), anomaly (upgrade), geo (alt), extract (alt) | Confirmar nombre+specs del checkpoint en HF / blog del lab Qwen | **ALTO** — es el modelo recomendado de dedup; sin confirmar, dedup cae a su piso verificado DeepSeek-R1-Distill-Qwen-14B (98.23% F1) |
| 2 | **F1 de entity-matching de Qwen3.5/Magistral 2026** está extrapolado de la clase del distill-14B, no medido directamente. | dedup | Hold-out local etiquetado estilo OpenSanctions Pairs **antes** de confiarle MERGE | **ALTO** — MERGE es irreversible; el gate de promoción lo bloquea hasta igualar el F1 del distill-14B |
| 3 | **F1 de la taxonomía dealer (6 clases)** — no existe gold público para ESTA taxonomía. | classify-dealer | Gold eval propio por idioma; gate macro-F1 ≥ baseline determinista | **MEDIO** — bloquea publicar el encoder por país |
| 4 | **gliner2-multi-v1 cubre ES/DE/FR/IT/PT** (la card dice "6 idiomas" sin enumerarlos). | extract-fields | Leer card / probar; si no cubre, usar GLiNER multilingüe sobre mDeBERTa | **MEDIO** — afecta el tier CPU barato que descarga el grueso |
| 5 | **NuExtract3 base = "Qwen3.5-4B"** (lo afirma su propia card, no el repo oficial Qwen). | extract-fields (alt) | Confirmar en repo oficial Qwen | BAJO — es alternativa VLM, no el workhorse |
| 6 | **Licencia de Qwen3-VL-235B.** | vision-photo | Reconfirmar en HF (2B-32B + 30B-A3B sí Apache-2.0 verificado) | BAJO — 235B es ruta €>0, no el workhorse 4B/8B |
| 7 | **Licencia de InternVL3.** | vision-photo (2ª vía de voto) | Verificar licencia en HF | BAJO — cross-check opcional |
| 8 | **Moondream3 BSL-1.1 prohíbe "third-party service".** | vision-photo (alt edge) | Revisar términos antes de exponerlo como servicio | BAJO |
| 9 | **Fechas exactas de release de GLM-4.7 y DeepSeek-V4-Pro** (WebFetch confundió arxiv-id con fecha). | recipe-synth (alts) | Confirmar en blog del lab | BAJO — specs/licencia/benchmarks SÍ verificados en HF |
| 10 | **GLM-5.x / Kimi K2.6 / DeepSeek-V4-Pro·Flash / MiniMax M3 / Qwen3.7-Plus / Holo3-35B-A3B** — sólo en agregadores. | source-discovery (no usados como base) | Confirmar contra fuente primaria antes de adoptar | BAJO — explícitamente no son la recomendación |
| 11 | **Existencia de una línea Qwen3.x-Embedding más nueva que jun-2025.** | translate-normalize, embeddings-blocking | Revisar HF Qwen | BAJO — el 0.6B de jun-2025 es el suelo verificado |
| 12 | **Gemma 3 / EmbeddingGemma = licencia Gemma** (uso comercial con restricciones), **NO Apache.** | extract (alt), classify (alt), geo (alt), translate (alt) | Leer Gemma Terms antes de mezclar en el carril €0-limpio | BAJO — son alternativas; el carril limpio es Apache/MIT |
| 13 | **Regex G1 `^CDP-ES-` clavado a ES** (datos `CDP-ES-*` verificados; el regex G1 en código no re-leído esta sesión). | transversal (anomaly, identity) | Leer el validador G1 en código | MEDIO — bloquea onboarding del país #2 (ver § transversal) |
| 14 | **Auto-despliegue de la config de enrutado por `cover(CC)`** ([`00-MASTER.md:57`](00-MASTER.md)). | toda la capa | Existir código de Capa-2 (hoy 0) + dimensión país enhebrada bajo el esquema | MEDIO — la capa es DISEÑO, no sistema corriendo (§0) |

**Nota de coherencia (blindaje):** el conflicto del flag #1 es exactamente el caso "memoria/afirmación de un agente contradice lo observado por otro" → se resuelve por la regla del blindaje: prevalece `[ASSUMED]`, y el recomendado de dedup **no se transcribe como hecho** mientras 3 de 5 inquisidores no lo confirmen en fuente primaria. El piso (DeepSeek-R1-Distill-14B) es el verificado y es lo que se sirve hasta promover.

---

## 4 · Auto-despliegue por país (cómo `cover(CC)` instalaría esta capa)

**Estado: `[ASSUMED]` / aspiración** (flag §3 #14). El diseño: la campaña `cover(country_code)` ([`COVER-NEW-COUNTRY.md`](COVER-NEW-COUNTRY.md)) instalaría, en el estado `BOOTSTRAPPED`, la **config de enrutado** como parte del pack profundo por país ([`00-MASTER.md:17-21`](00-MASTER.md)):

```
routing_config[country_code] = {
  per_task: { model_id, endpoint, grammar/JSON-schema, prompt_template,
              gazetteer_adapter, golden_set_ref, escalation_thresholds },
  euro0_default: true,                # GPU = palanca con firma
  country_scoped: true               # gate duro de país (dedup/geo/escalada)
}
```

**Bloqueadores antes de que esto sea real (no maquillados):**
1. **Capa-2 = 0 código hoy** (§0). Primero existe el runtime de IA local con gramática + 2ª vía + fallback.
2. **Dimensión país bajo el esquema** (§ transversal): grammars/gazetteers/golden-sets **keyed por país+idioma**; gate de país en dedup/geo/escalada; golden cross-country verde ([`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md)).
3. **Locale ≠ país:** la config debe separar idioma (gramática/OCR/normalización) de país (códigos administrativos/denominador/aislamiento).

Hasta cerrar los tres, la matriz es **single-tenant ES** y multi-país `[ASSUMED]`.

---

## Procedencia y BLINDAJE

- **Insumo destilado:** `wave1-stages/_llm.json` (10 categorías, recommended/alternatives/deterministic_stays/quality_guardrail/efficiency/az_path/claude_role/euro0_path/notes). Los specs/licencias/benchmarks de modelos son `[VERIFIED·HF]` **por los inquisidores de cada categoría** (registrado en las `notes` del JSON); **no los re-leí en HF esta sesión** — por honestidad se etiquetan `·HF`, no como lectura propia.
- **Verificado de primera mano esta sesión (código del repo):** country-blindness del motor — `pipeline/geo.py:8,46-48,61-73,153,157,278` · `pipeline/identity/cluster_dealers.py:404-430` · `migrations/0001_geo.sql:5,19` · `migrations/0052_country.sql:32-34,38,51-54` · `migrations/0053_country_onboarding.sql:53-54` · datos `cdp_code` = `CDP-ES-*` · `country_code` en `pipeline/` sólo en `triangulation.py`+`paths.py`.
- **Lo `[ASSUMED]` (§3) no se presenta como hecho.** El único modelo recomendado contestado (dedup, Qwen3.5-35B-A3B) lleva su piso verificado y su gate de promoción.
- **Roturas integradas, no maquilladas:** la capa es diseño (Capa-2 = 0 código) y hereda un motor country-blind; ambas quedan declaradas como open items con causa y con su vía de cierre (COUNTRY-PROOF + runtime de Capa-2), no transcritas como "hecho/funciona".
- **Mapeo a `ANTI-DRIFT-HARDENING`:** gramática-constrained = §1.1 (anti-fabricación) · provenance por campo = §1.2 · cross-check det.↔LLM = §1.5 · golden+CI = §1.6 · escalada-no-adivinar = §2.3 · contrato autocontenido por job = §2.1.
