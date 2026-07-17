# 00-MASTER — Síntesis cruzada del programa cardeep-omni

> Programa: cardeep-omni · Fecha: 2026-07-17 · Fase: MASTER (síntesis adversarial, cero código ejecutado).
> Fuente: las 10 cartas de sub-proyecto de `plans/cardeep-omni/` leídas COMPLETAS en esta sesión
> (3.502 líneas totales, verificado por `wc -l`). Las afirmaciones de código citadas aquí heredan
> la etiqueta de verificación de su carta de origen (cada carta declara sus anclajes archivo:línea);
> lo que este documento añade por cuenta propia es el CRUCE entre cartas, y cada hallazgo de cruce
> cita carta y sección exactas.
> Autoridad: este documento gobierna el ORDEN y las FRONTERAS entre pilares. Ante conflicto entre
> una carta y este MASTER en materia de ownership/orden, manda el MASTER; en materia de contenido
> interno del pilar, manda la carta.

---

## 1. Mapa de los 10 pilares

| # | Pilar | Archivo | Estado real (según su carta) | net-new |
|---|---|---|---|---|
| 00 | Motor de indexación total | `00-marketplace-engine.md` | Motor EXISTE y funcionó a escala (pico 490k eventos NEW/día) pero lleva ~18 días PARADO (heartbeat muerto 2026-06-29); watchdog murió con el vigilado; 6/56 breakers abiertos sin auto-recuperación. Lo net-new es la capa operativa: supervisión externa, half-open, cadencia adaptativa, superficie de estado. | Parcial (motor existe; ops/superficie = nuevo) |
| 01 | Inteligencia de mercado | `01-market-intelligence.md` | Investigación REAL y densa (693 empresas, 109 auditorías, 3.131 campos) + materia prima completa (`vehicle`/`vehicle_event`/`entity`/0023) + superficie 100% mock (Inteligencia/Arbitrage/Analitica hardcodeadas, 7.597 líneas huérfanas de terminal sintético). CERO capa de cómputo de mercado en backend. | No (research+datos existen; cómputo = nuevo) |
| 02 | Historial de vehículo | `02-history-reports.md` | Fachada Check/Dossier = vaporware total (tipos alineados a backend Go inexistente, proxy :8506 huérfano) + activo real enterrado: `vehicle_event` append-only servido por `/vehicles/{ulid}/history` end-to-end. Sin re-identificación GONE→reaparición. | Sí (el motor de vida = nuevo; el delta existe) |
| 03 | Garaje/flota dealer | `03-garage-fleet.md` | Capa A REAL end-to-end: inventario + garaje 3D sobre API viva, 1 dealer hardcoded (GYATA, 468 coches verificados por curl). Capa B (Kanban/Deals/Contacts/Finance) = mock total montado en router. Backend 100% solo-lectura, 0 endpoints de escritura. | No (visor real existe; escritura/comparables = nuevo) |
| 04 | Arbitraje | `04-arbitrage.md` | 5 señales diseñadas, 0 construidas. Primitivo estadístico REAL y testeado (`detect_price_trap`: cohortes, mediana+MAD, robust-z). 5,4M eventos medidos en DB viva. Cross-platform: 0 pares reales (photo_hash poblado en 0 vehículos; VIN17 solo 17.730). Frontend mock tras paywall mock. | No (primitivo+datos existen; señales = nuevo) |
| 05 | Multipublicación | `05-multiposting.md` | Net-new al 100%: cero código outbound, cero auth, cero credenciales, cero adaptadores. Todo lo existente apunta en dirección INBOUND (`platform_listing`). Cuello de botella = ACCESO de escritura (solo AS24 tiene API pública), no ingeniería. | Sí |
| 06 | CRM/chats unificados | `06-unified-crm-chat.md` | 7 páginas React ruteadas, 0 datos reales (todas isla con MOCK_*), 0 tablas CRM, 0 routers, 0 canales, 0 tiempo real. Modelo de tipos bien diseñado sin nada detrás. | Sí |
| 07 | Marketing | `07-marketing.md` | No existe en ninguna capa. Lo que aparenta marketing es mock (Analitica) o falsificación cliente-side (Assistant: "Imagen generada" = Math.random sobre Unsplash). Materia prima del feed/auditoría sí existe (`vehicle` campo a campo). | Sí |
| 08 | Foro/comunidad | `08-forum-community.md` | 100% net-new en las tres capas: 47 tablas reales y ninguna social, sin tabla user/account/session, sin rutas frontend. Gate duro del owner sobre cualquier frontend (protocolo registrado). | Sí |
| 09 | Terminal de trading | `09-trading-terminal.md` | Dos terminales muertos 100% sintéticos fuera del nav (un commit de vida cada uno) + artefacto tóxico `carNews()` (titulares fabricados atribuidos a marcas reales) + UNA pieza rescatable: motor de 53 indicadores testeado (`indicators.ts` + suite). Cero capa de agregación en backend. | Sí (núcleo nuevo; indicadores rescatables) |

---

## 2. Contradicciones encontradas y su resolución

Cada una detectada por lectura cruzada de las cartas; la resolución es mandato de este MASTER.

### C-1 · Colisión de archivo y namespace: `services/api/routers/market.py` (01 vs 09)
- **Qué**: 01 §5 crea `market.py` con `/market/segments/...`, `/market/price-position/{ulid}`, `/market/provinces/demand`, `/market/dgt-corroboration`. 09 §5.2 crea EL MISMO archivo `market.py` con `/market/symbols`, `/market/{symbol_key}/ohlc|stats|rating`. Mismo fichero, contenidos incompatibles; además ambos definen jobs de agregación separados (01: `pipeline/market/compute_stats.py` → `market_stat`; 09: job diario → `market_bucket_daily`) que computan estadísticos casi idénticos (mediana de precio por make·model·provincia) con claves de cohorte distintas (01 incluye fuel+year_band; 09 no).
- **Resolución**: 01 es el dueño de `market.py` y del namespace `/market/*`. 09 renombra su router a `services/api/routers/terminal.py` con namespace `/terminal/*` (coherente con su ruta frontend). Las tablas se mantienen separadas (claves de cohorte genuinamente distintas) PERO el helper de percentiles/medianas/ventanas se factoriza UNA vez (junto con el helper de cohortes de `detect.py` que 04-F1 ya planifica extraer) y ambos jobs lo importan. Prohibido un tercer cálculo independiente de mediana-por-cohorte.

### C-2 · Colisión de página: `/arbitrage` reescrita por dos pilares con motores distintos (01 vs 04)
- **Qué**: 01 §6/F6 redefine `/arbitrage` como "anuncios con M2 ratio < 0.92 y n≥8". 04 (pilar entero) reescribe `Arbitrage.tsx` con deal-score robust-z (bandas z≤−3.5 / −2.0), tablas `cohort_stats`/`deal_score` y router propio. Dos definiciones de "chollo" incompatibles que darían rankings distintos en la misma pantalla.
- **Resolución**: 04 es el dueño único de `/arbitrage` y de la definición de "chollo" (su diseño es más profundo: universo `servable_vehicle`, frontera explícita con `price_trap`, endpoint de metodología). 01-F6 reduce su alcance sobre `/arbitrage` a NADA (se elimina esa sección de su F6; conserva `/inteligencia` y Analitica). 01-M2 (price-position ratio-a-mediana) sobrevive como la API general de posición de precio de un anuncio — consumida por 03-K9, 06-chip y 07-C2 — pero NO alimenta el ranking de chollos.

### C-3 · Cuatro esquemas de auth incompatibles (03, 05, 06, 08) — la colisión más grave del programa
- **Qué**: 03-F1 crea `dealer_account`+`dealer_membership`; 05-F3 crea `0073_dealer_account.sql` con `dealer_account`+`dealer_user` (semántica de tenant distinta a la de 03); 06-F1 crea `crm_tenant`+`crm_user`; 08-F1 crea `0073_app_user` con `app_user` (roles dealer/particular/staff)+`user_session`+`user_notification`. 04-F7 depende de "el pilar auth/billing" sin especificar cuál. Ejecutadas tal cual, son 4 migraciones en conflicto directo, 3 de ellas numeradas 0073, y 3 recableados distintos de `AuthContext.tsx`/`DEV_BYPASS` (03-F1, 05-F3, 08-F1).
- **Resolución**: se extrae un workstream transversal **AUTH-0** (no es un pilar nuevo con carta: es la fusión de 03-F1 + 05-F3 + 06-F1-tenancy + 08-F1 en UNA migración y UN router `auth.py`). Esquema base = el más general de los cuatro: `app_user` de 08 (roles dealer/particular/staff, argon2id, verificación de rol dealer vía `tax_id.py`) + la relación multi-rooftop de 03 (`dealer_membership`: user↔entity N:M) + `user_session` revocable + `user_notification` de 08. `crm_tenant` de 06 desaparece: el tenant ES la entity del dealer vía membership. Un solo desmontaje de `DEV_BYPASS`. Security review obligatoria (regla del repo). Cada carta afectada ejecuta su fase de auth CONSUMIENDO este esquema, no creando el suyo.

### C-4 · Dos CRM para las mismas páginas (03 vs 06)
- **Qué**: 03-F5 crea `dealer_lead`/`dealer_deal` ("CRM mínimo") y decide el destino de Contacts/Inbox; 06 crea el schema completo `crm_contact`/`crm_deal`/`crm_conversation`/... y recablea Contacts/Deals/Kanban. Dos schemas de deal para las mismas pantallas.
- **Resolución**: 06 es el dueño único del dominio CRM (schema `crm_*`, páginas Contacts/Deals/Inbox/Calendar/Notes). 03-F5 se REDEFINE: no crea `dealer_lead`/`dealer_deal`; consume `crm_deal` de 06 (el enlace deal↔`vehicle_ulid` que 03 quiere ya existe en el schema de 06). 03 conserva íntegro lo que es suyo y ortogonal: `fleet_ops`/`fleet_ops_event` (estado operativo del VEHÍCULO, no del comprador).

### C-5 · Colisión de ruta: `/kanban` = tablero de vehículos (03) Y tablero de deals (06)
- **Qué**: 03 §6.2 reconstruye `/kanban` como pipeline de VEHÍCULO (Entrada→Preparación→Publicado→Reservado→Vendido→Entregado; tarjetas = `vehicle_ulid`, transiciones en `fleet_ops`). 06 §4/§6 reconstruye Kanban como pipeline de DEAL (Nuevo→Contactado→Oferta→Negociando→Vendido/Perdido; tarjetas = deals, `crm_deal_stage_event`). Misma ruta, dos productos distintos.
- **Resolución**: son DOS tableros legítimos y ambos viven. `/kanban` queda para el pipeline de deals (06, coherente con el grupo CRM del nav). El tablero de vehículos de 03 vive dentro del workspace de flota (ruta nueva bajo su superficie, p.ej. `/vehicles/tablero` o pestaña de "Mi flota"). Las cartas se enmiendan en sus F0 respectivas.

### C-6 · Migración `0073` reservada por cinco cartas
- **Qué**: 01 (`0073_market_stat`), 05 (`0073_dealer_account`), 06 (`0073+ crm_*`), 07 (`≥0073 listing_audit`), 08 (`0073_app_user`). Todas declaran "re-verificar contra `ls migrations/` al ejecutar" — el riesgo está declarado, pero sin autoridad de asignación choca igual.
- **Resolución**: la numeración la asigna el ORDEN DE CONSTRUCCIÓN de §4 de este MASTER, secuencialmente, en el momento de ejecutar cada fase. Ninguna carta "posee" un número. Regla operativa: el ejecutor de cada fase toma `max(ls migrations/)+1` y actualiza su carta con el número real consumido.

### C-7 · Ventana del Market Days Supply: 45 días (01) vs 90 días (03) para la misma métrica con el mismo nombre
- **Qué**: 01-M4 define MDS con ventana 45d citando "estándar vAuto"; 03-K10 define MDS con GONE de últimos 90d/90. El mismo dealer vería dos "días de stock" distintos para el mismo segmento en `/inteligencia` y en "Mi flota". (03 además cita a vAuto como procedencia — inconsistencia interna).
- **Resolución**: ventana única = 45 días (la que la propia investigación de 01 §2 documenta como fórmula vAuto). 03-K10 se enmienda. Regla general derivada: ver C-12 (registro único de umbrales).

### C-8 · Estado de la DB: cartas en desacuerdo (00/01/04 vs 02/09)
- **Qué**: 00 (RECON por 3 vías), 01 y 04 verifican DB VIVA (cardeep-pg Up, queries ejecutadas, 5,4M eventos contados) con motor PARADO. 02 §1 dice "el stack estaba parado (Docker/DB caídos, 2026-06-27) y esta sesión no levantó la DB"; 09 §5.2 dice "DB parada según memoria de proyecto".
- **Resolución**: manda el RECON de 00 (3 vías independientes, la más reciente y profunda): **DB viva, motor muerto, datos congelados a 2026-06-28/29**. Las notas de 02 y 09 son stale (heredadas de memoria del 06-27); sus planes de medición F0 siguen siendo válidos y ahora ejecutables sin levantar nada.

### C-9 · Dependencia oculta no declarada: 02-F1 está gateada por la captura de identidad que mide/programa 04 — y las cartas no se citan entre sí
- **Qué**: 02-F1 (re-identificación de por vida) exige doble señal por eslabón (`vin_ref` exacto O `photo_hash` exacto + corroborante) y declara como hueco F0 "cobertura de vin_ref/photo_hash no verificada". Pero 04 §1.4 YA la midió en la DB viva: **`photo_hash` poblado en 0 vehículos; VIN de 17 caracteres en solo 17.730** (de ~2,3M). Es decir: la señal photo_hash de 02 hoy NO EXISTE, y la señal VIN cubre <1% del censo. 04-F6 es quien programa poblar `photo_hash` y extender captura de VIN. Ninguna de las dos cartas referencia a la otra en este punto.
- **Resolución**: se declara el workstream compartido **IDENTIDAD-CAPTURA** (poblar `photo_hash`, extender VIN en recetas) como upstream común de 02-F1, 04-F6 y 09-C5 (inferencia de venta). Se construye UNA vez (el trabajo vive donde 04-F6 lo describe, por ser quien lo especificó con la doctrina anti-over-merge). 02-F0 hereda las cifras ya medidas por 04 (no re-mide desde cero) y su F1 arranca sabiendo que en v1 la cadena dependerá de vin_ref+firma corroborada hasta que photo_hash se puieble. Además: 09-Fase-4 (inferencia de venta "sin reaparición en 14 días") debe CONSUMIR el motor `lifetime_link` de 02-F1 en cuanto exista — su heurística propia sobre `vehicle_cluster` no detecta reapariciones semanas después en otro dealer, exactamente lo que 02 construye.

### C-10 · Propiedad de la corrección del blueprint §3.10 (05 vs 06 vs 07)
- **Qué**: 05-F0 corrige §3.10 (etiqueta NOW + números 0033-0035); 06-F0 corrige lo mismo; 07 delega en 06 y solo verifica ("la deuda se salda una vez, no tres" — la propia carta 07 ya vio el riesgo).
- **Resolución**: la corrección la ejecuta quien llegue primero de {05-F0, 06-F0} (regla del primer llegado que 07 §6 ya formuló para Inbox, generalizada), citando ambas cartas en el diff; el otro verifica en su F0 y no re-edita. Igual para `Inbox.tsx`/`MOCK_CONVS` (tres cartas lo tocan: 05-F2, 06-F3, 07-F0): dueño = 06; si 06-F3 no ha aterrizado cuando 05-F2 o 07-F0 ejecuten, el primero lo retira con empty-state honesto y lo registra en el tracker de 06.

### C-11 · `/terminal` y la carpeta `terminal/`: tres cartas con planes de demolición solapados (01, 04, 09)
- **Qué**: 09-F0 demuele `Market.tsx`+`intelligence.ts` y pone en cuarentena `terminal/` rescatando `indicators.ts`+tests+`MarketChart.tsx`+`drawings.tsx`. 01-F6 elimina "el universo sintético de terminal/" salvo la custodia de 09 (coherente). 04-F0 quiere "sacar /terminal de la navegación de producto" y eliminar/degradar `terminal/Arbitrage.tsx` — pero 09 verificó contra `Shell.tsx:20` que `/terminal` YA está fuera del nav (solo la ruta pervive en `App.tsx:86-87`).
- **Resolución**: 09 es el dueño único del destino de `Market.tsx`, `Terminal.tsx` y toda la carpeta `terminal/` (incluida `terminal/Arbitrage.tsx`). 04-F0 se reduce a una verificación (confirmar que nada sintético es navegable sin etiqueta — ya cierto hoy) y a su decisión de owner registrada. 01-F6 limita su demolición a `Inteligencia.tsx`/`Analitica.tsx`/`Api.tsx` y verifica que 09-F0 ejecutó la suya. Nadie borra dos veces.

### C-12 · Inconsistencia sistémica de umbrales mínimos y cohortes entre pilares
- **Qué**: n mínimo para mostrar un agregado: 8 (01-M1, 03-K9, 07-C2) · 15 (04 Tier-A y geo-celdas) · 30 (04 Tier-B, 05-radar, 09-C2) · 50 (04 ciclos de tiempo). Definición de "comparable/cohorte": make+model+year±1+fuel+provincia (01) · +km±20% (03, 07) · make+model+year sin geo (04) · make·model·provincia sin year/fuel (09) · make+model+year±1+banda km (05). Cada elección está citada y razonada EN su carta, pero el producto final mostraría al mismo dealer números incoherentes entre pantallas sin explicación.
- **Resolución**: no se fuerza un umbral único (las citas difieren legítimamente: iSeeCars/MMR/Mercari), pero se crea el **registro único de cohortes y umbrales** — un archivo de constantes compartido en backend (extensión natural del helper factorizado de C-1) donde cada (métrica, cohorte, n-mín, ventana) vive UNA vez con su procedencia. Toda carta referencia ese registro; el endpoint de metodología de 04 (`/arbitrage/methodology`) se generaliza a `/methodology` del programa. Divergencias entre pantallas deben ser explicables desde ese registro o se unifican.

### C-13 · Conteo de migraciones: "72 migraciones" (05 §1.1) vs 66 archivos con huecos numerados 0001–0072 (06, 08, 03)
- **Qué**: menor. 05 §1.1 dice "las 72 migraciones"; 06 §1 corrigió por conteo directo: 66 archivos, numeración con huecos (faltan 0008, 0010-0012, 0014-0015).
- **Resolución**: cifra canónica = 66 archivos / última `0072` (doble vía: 06 y 08 coinciden por caminos distintos). 05 enmienda la frase en su F0.

---

## 3. Dependencias entre pilares (qué bloquea a qué)

### Bloqueos duros (sin esto, el downstream no puede cerrar)

| Upstream | Downstream bloqueado | Naturaleza |
|---|---|---|
| **00-F0..F2** (motor vivo + replay) | TODOS los pilares de producto | Datos congelados desde 2026-06-28. Los gates de frescura de las cartas (04: `last_seen ≤72h` para aparecer en ranking; 05: matriz de cobertura; 06: chip "visto hace Nh"; 09: sello de frescura) devolverían CERO filas o todo stale con el motor muerto. 01 puede CONSTRUIR sobre el histórico congelado (backfill), pero su gate de publicación ±3% intersemanal exige runs sucesivos sobre datos vivos. |
| **AUTH-0** (C-3) | 03-F1+, 04-F7, 05-F3+, 06-F1+, 08-F1+ | Cuatro pilares no pueden abrir su superficie autenticada sin el esquema único. |
| **01-F1..F3** (market_stat + M1/M2 + market.py) | 03-F4 (K9/K10/K11), 06-F5 (chip price-position), 07-F2 (C2), 04-F1 (helper de cohortes compartido), 09 (sustrato de agregación) | El motor de comparables se construye UNA vez en 01 (su carta lo declara; 03 y 07 lo consumen; C-1/C-2 lo refuerzan). |
| **IDENTIDAD-CAPTURA** (photo_hash + VIN; vive en 04-F6) | 02-F1 (señal de eslabón), 04-F6 (pares cross-platform), 09-Fase4 (inferencia de venta) | Hoy: photo_hash=0, VIN17=17.730 (C-9). Sin esto, la señal cross-platform y la cadena de vida operan bajo mínimos. |
| **02-F1** (lifetime_link) | 09-Fase4 (inferencia de venta robusta) | La reaparición diferida en otro dealer solo la detecta el motor de 02 (C-9). |
| **06-F4** (canal email vivo) | 06-F5 (cruce censo necesita conversaciones), 07-F6 (atribución de leads) | Declarado en las propias cartas. |

### Gates del owner (fuera del control de ingeniería; no bloquean el resto)
- 08-F0: OK explícito del owner sobre TODO el pilar antes de una línea de frontend (protocolo duro registrado).
- 05-F5 (cuenta AS24 real) y 05-F7 / 06-F7 (WhatsApp) / 07-F5 (coste copy) / 02-F5 (convenio DGT/ITV): fases de gasto/acceso, selladas como "contract-verified con hueco declarado" si el acceso no llega.
- 04-F0: decisión registrada del owner sobre el destino final de `/terminal` (default de la carta: fuera del nav — ya cierto).

### Dependencias blandas (mejoran, no bloquean)
- 01-F4 (corroboración DGT M8) eleva la honestidad de M3/M4/M5 (01), K11 (03), curvas de 04-F4 y C5 de 09 — todos etiquetan "retirada ≠ venta" hasta entonces.
- 05-F1/F2 (Frente A solo-lectura) no depende de AUTH para su API (patrón `platforms.py` con API-key), sí para la pantalla `/pro/*`.

---

## 4. Orden de construcción recomendado — con la justificación honesta

### Veredicto sobre "inteligencia de mercado es el pilar de mayor apalancamiento": **CONFIRMADO, con un matiz de orden**

Evidencia (de las cartas, no de intuición):
1. **Investigación ya pagada**: 693 empresas, 109 auditorías al átomo, 3.131 campos, PLACEMENT-MAP con 1.353 patrones (01 §1, verificado por conteo en su RECON). Ningún otro pilar tiene ni una fracción de ese trabajo previo hecho.
2. **Materia prima completa y medida**: 2.542.358 NEW / 458.436 GONE / 267.193 PRICE_CHANGE en DB viva (medido por 04 §1.4), esquema de segmentación geo ya existente, dedup 0023 con gate — 01 no necesita ni una fuente nueva, ni auth, ni permiso de nadie para su núcleo.
3. **Es el pilar con MÁS consumidores aguas abajo**: seis de los otros nueve consumen su motor — 03 (K9/K10/K11), 04 (helper de cohortes + medianas), 05 (radar §4.7), 06 (chip F5), 07 (C2), 09 (sustrato de agregación). Ningún otro pilar es dependencia de más de dos.
4. **Distancia corta**: ~95% SQL determinista (confesión de la propia carta), cero LLM en camino crítico, patrón run+gate ya probado en el repo (0023).

El matiz: **mayor apalancamiento ≠ primero en términos absolutos**. 00-F0..F2 va antes porque es barato (rebuild + `docker compose up -d autopilot` + verificación, servicio ya definido en `docker-compose.yml:63-72`) y porque sin motor vivo el programa entero construye vitrinas sobre datos muertos — la frase de la propia carta 00: "sin motor latiendo, todos los demás pilares sirven datos muertos". El segundo candidato a máximo apalancamiento sería 04 (primitivo `detect_price_trap` vivo y testeado, distancia mínima a paridad), pero su deal-score depende del sustrato de cohortes que se factoriza con 01 — lo que refuerza, no refuta, la primacía de 01.

### Orden (bloques; dentro de un bloque hay paralelismo seguro si se respeta el mapa de ownership de §5)

**BLOQUE 0 — Cimientos (serie, corto):**
1. **00-F0..F2** — revivir el motor supervisado, watchdog externo, replay + triage de breakers. Gate absoluto del programa.
2. **Barrido documental único** — corrección coordinada de blueprint §3.5/§3.10/§3.11 + `Api.tsx` (una pasada, dueños según C-10; incluye las enmiendas a cartas que este MASTER ordena: C-2, C-4, C-5, C-7, C-13).
3. **09-Fase0** — demolición de `Market.tsx` + `intelligence.ts` (el artefacto tóxico `carNews()` no sobrevive ni un bloque más) + rescate de `indicators.ts`. Barato, sin dependencias, desbloquea la parte de demolición de 01-F6.

**BLOQUE 1 — El motor de producto (paralelo):**
4. **01-F0..F5** — verdad de volumen, `market_stat`, M1-M10, `market.py`, DGT, price-position. El pilar de mayor apalancamiento, ejecutado primero entre los de producto.
5. **02-F0..F2** — cifras heredadas de 04 (C-9), motor `lifetime_link`, API. Backend puro, cero colisión de archivos con 01.
6. **AUTH-0** — esquema único (C-3) + security review. Se ejecuta en este bloque para que el Bloque 2 abra con auth real.
7. **00-F3..F4** (half-open, cadencia adaptativa) en paralelo — es del dominio del motor, no toca `web/src`.

**BLOQUE 2 — Superficies de dealer (paralelo tras AUTH-0 y 01):**
8. **03-F1..F4** — auth consumida, "Mi flota" real, escritura `fleet_ops`, comparables CONSUMIENDO 01 (K9=M2; MDS ventana 45d por C-7).
9. **04-F1..F5** — deal-score sobre el helper compartido, dueño único de `/arbitrage` (C-2), time/geo-arbitrage. 04-F6 (identidad-captura) arranca aquí como workstream de fondo (C-9).
10. **05-F0..F2** — Frente A solo-lectura (matriz de publicación); F4 (feeds) y F5 (AS24) después, F5 sujeta a credencial del owner.

**BLOQUE 3 — Capas de relación y presentación (paralelo):**
11. **06-F1..F6** — CRM completo, dueño de Contacts/Deals/Kanban (C-4/C-5), email como primer canal, cruce censo con M2 de 01.
12. **07-F0..F5** — auditoría de anuncio, feeds, copy grounded; consume C2 de 01; F6 integra con 05/06.
13. **09-Fases1..6** — agregación diaria + terminal real bajo namespace `/terminal/*` (C-1), inferencia de venta consumiendo `lifetime_link` de 02 (C-9).
14. **00-F5..F6** — superficie de estado + ledger de uptime (necesita frontend estable de los bloques previos para integrarse en Dashboard/Marketplace).

**BLOQUE 4 — Comunidad (último a propósito):**
15. **08-F0..F6** — exige AUTH-0 (hecho), OK explícito del owner (gate F0) y una plataforma con usuarios reales a los que servir. Su propia carta ordena el tablón "Se busca" antes que el foro para no exhibir un foro fantasma. Ponerlo antes sería construir la sala de fiestas de un edificio sin inquilinos.

**Fuera de orden (gated permanente):** 05-F7 (Frente C portales cerrados), 06-F7 (WhatsApp), 02-F5 (institucional), 00-F7 (governor Redis, gate horizonte EU), 03-F6 (garaje 3D fase 2). No consumen ni una hora sin su gate abierto.

**Justificación honesta del orden completo**: no es "lo fácil primero" — es apalancamiento medido: (a) 00 primero porque es el multiplicador de TODO lo demás al coste más bajo del programa; (b) 01 primero entre producto porque es el único pilar cuya salida consumen otros seis y cuya investigación ya está amortizada; (c) AUTH-0 en el Bloque 1 porque es el cuello de botella compartido de cuatro pilares y su coste de hacerlo cuatro veces mal supera con mucho el de hacerlo una vez bien; (d) 08 último porque sus dos frenos (owner + masa de usuarios) son externos a la ingeniería y su valor depende de que el resto exista.

---

## 5. Riesgos de ejecutarlo todo en paralelo sin coordinación

### 5.1 Colisiones de archivos en `web/src` (medidas contra las cartas)

| Archivo | Pilares que lo tocan | Riesgo sin coordinación |
|---|---|---|
| `web/src/pages/Arbitrage.tsx` | 01-F6, 04-F3 | Dos reescrituras con motores distintos (C-2). Resuelto: dueño 04. |
| `web/src/pages/{Kanban,Contacts,Deals}.tsx` | 03 (§6.2/§6.4/F5), 06 (F3) | Dos productos sobre las mismas páginas (C-4/C-5). Resuelto: dueño 06. |
| `web/src/pages/Inbox.tsx` | 05-F2, 06-F3/F4, 07-F0 | Triple retirada del mock (C-10). Resuelto: dueño 06, regla primer-llegado. |
| `web/src/pages/Analitica.tsx` | 01-F6 (SALES_DATA→M*, decisión fusionar), 07-F0/F4 (panel CHANNELS) | Merge conflicts y decisiones de página contradictorias. Regla: 01 decide el destino de la página; 07 posee solo el panel CHANNELS y se pliega a esa decisión. |
| `web/src/auth/AuthContext.tsx` + `DEV_BYPASS` | 03-F1, 05-F3, 08-F1 (y 04-F7 lo referencia) | Tres recableados de auth distintos (C-3). Resuelto: AUTH-0 lo hace una vez. |
| `web/src/layout/Shell.tsx` (NAV_GROUPS) | 03 (retira), 05 (añade /pro), 06 (retira /chat), 07 (añade Marketing), 08 (añade COMUNIDAD), 09 (añade terminal) | Seis manos en el mismo array = conflictos permanentes y un nav incoherente. Regla: el nav se toca al CIERRE de cada fase (como ya exige 09-Fase3), en commits atómicos de una sola entrada. |
| `web/src/App.tsx` (rutas) | prácticamente todos | Ídem: commits atómicos por ruta, nunca refactors de rutas en fases de pilar. |
| `web/src/api/cardeep.ts` | 01, 04, 05, 06, 07, 09 (todos "extienden el cliente") | Seis extensiones simultáneas. Regla: añadir métodos es append-only por secciones comentadas por pilar; prohibido reordenar/renombrar métodos ajenos. |
| `web/src/pages/terminal/*` + `Market.tsx` | 01-F6, 04-F0, 09-F0 | Triple demolición (C-11). Resuelto: dueño 09. |
| `docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md` | 03-F0 (§3.11), 05-F0/06-F0 (§3.10), 09-F0 (§3.5) | Tres correcciones simultáneas del mismo doc. Resuelto: barrido documental único del Bloque 0. |

### 5.2 Bifurcación de esquema y de números
- **Sin C-3**: hasta 3 migraciones `0073` incompatibles el mismo día, con `dealer_account` significando dos cosas distintas según qué rama mergea primero.
- **Sin C-1/C-12**: tres implementaciones de mediana-por-cohorte (01, 04, 09) + cuatro definiciones de comparable + tres n-mínimos → el mismo coche etiquetado "chollo" en una pantalla, "en mercado" en otra y "muestra insuficiente" en una tercera. Para un producto cuya identidad ES la verificabilidad, esa incoherencia visible destruye exactamente la confianza que se vende. Es el riesgo más corrosivo del paralelismo: no rompe el build — rompe la credibilidad.
- **Sin C-7**: métricas con el mismo nombre y ventanas distintas conviviendo en producción.

### 5.3 Deuda de diseño inconsistente
- Las cartas comparten patrones que cada una piensa construir por su cuenta: badge "n + ventana + computed_at" (01 §7, 04 §6, 05 §7.6, 07 §7, 09 §6), estados vacíos honestos, tooltip "cómo se calcula", gate CI anti-mock (01 §7, 04 §7-V6... cada una con su grep propio). Construidos seis veces = seis variantes visuales y seis regex de CI que divergen. Regla: componentes compartidos (`MetaBadge`, `EmptyStateHonesto`, `MethodologyLink`) se construyen en el primer pilar que los necesite (01, por orden) y los demás los importan; el gate CI anti-mock es UNO, repo-wide, con lista blanca por página — no un grep por carta.
- Precedente ya observado por 01 §1: `AnimNum`/`Spark` duplicados copy-paste entre Inteligencia/Arbitrage/Analitica. El paralelismo sin regla multiplica ese patrón.
- Restos de marca violeta confinados en `terminal/` (09 §1.1): cualquier rescate paralelo sin el gate de grep de 09-F0 reintroduce estilo huérfano.

### 5.4 Contención de base de datos y del scheduler
- Los pilares planifican en conjunto ≥8 jobs batch nuevos (compute_stats de 01, comparables de 03, score/decay/geo de 04, feeds de 05, IMAP de 06, audit de 07, agregación de 09, link_lifetimes de 02) contra la misma cardeep-pg. Sin coordinación, corren ad-hoc, fuera del scheduler durable del motor (que 00 acaba de revivir) y pueden coincidir con la cosecha en serie — exactamente el escenario multi-productor que el diseño single-producer del scheduler (scheduler.py, cicatriz AS24) existe para impedir. Regla: todo job batch de pilar se registra en el scheduler de 00 (APScheduler durable), nunca como proceso suelto; los jobs pesados respetan la doctrina MVCC (INSERT run nuevo + DELETE caducado, jamás UPDATE masivo) que las cartas ya adoptan individualmente.

### 5.5 Gates del owner pisoteados
- En paralelismo ciego, 08 empezaría frontend sin el OK explícito que su carta declara innegociable (rechazo previo documentado), y 05-F5/06-F7/07-F5 incurrirían en gasto sin autorización. El orden de §4 los pone estructuralmente detrás de sus gates.

---

## Reglas operativas del programa (derivadas de §2-§5)

1. **Numeración de migraciones**: `max(ls migrations/)+1` en el momento de ejecutar; la carta se actualiza con el número real (C-6).
2. **Ownership de archivo**: la tabla §5.1 es vinculante. Tocar un archivo ajeno = coordinar antes por enmienda de carta.
3. **Un solo helper estadístico** (cohortes/percentiles/ventanas) y **un solo registro de umbrales** con procedencia (C-1, C-12).
4. **Un solo esquema de identidad** (AUTH-0, C-3) y **un solo CRM** (06, C-4).
5. **Regla del primer llegado** para demoliciones compartidas (Inbox, blueprint), con registro en el tracker del dueño (C-10, C-11).
6. **Nav y rutas**: commits atómicos, al cierre de fase, nunca durante.
7. **Jobs batch**: registrados en el scheduler durable de 00; cero procesos sueltos.
8. **Gate CI anti-mock único** repo-wide; las variantes por carta se consolidan al implementarse el primero.
9. Este MASTER se enmienda con evidencia nueva, igual que las cartas; el estado de ejecución del programa se persiste en `plans/cardeep-omni/` (tracker por bloque), nunca solo en contexto volátil.

---

## Resumen

Diez cartas sólidas individualmente, con cinco choques estructurales entre ellas que este MASTER resuelve antes de que cuesten código: el archivo `market.py` y el namespace `/market/*` disputados entre 01 y 09; la página `/arbitrage` disputada entre 01 y 04; cuatro esquemas de auth incompatibles (03/05/06/08) fusionados en AUTH-0; dos CRM para las mismas páginas (03/06) resuelto a favor de 06; y la dependencia oculta más peligrosa — la re-identificación de por vida de 02 gateada por una captura de identidad (photo_hash=0 hoy) que solo 04 había medido y programado. El orden de construcción confirma a 01-market-intelligence como el pilar de mayor apalancamiento (investigación amortizada + materia prima medida + seis pilares consumidores), con el matiz de que 00 (revivir el motor parado 18 días) va antes por ser el multiplicador universal al coste mínimo, y 08 va último por sus frenos externos (owner + masa de usuarios). El paralelismo sin este documento habría producido: tres migraciones 0073 en conflicto, tres motores de mediana-por-cohorte divergentes, seis manos en Shell.tsx, y un producto que muestra números incoherentes entre pantallas — la única forma de perder, para un producto cuya identidad es la verificabilidad.
