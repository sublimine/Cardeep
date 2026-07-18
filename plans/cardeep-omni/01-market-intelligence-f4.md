# F4 — Ingesta DGT (`0077`+`ingest_dgt.py`) y corroboración (`0078`+`corroborate.py`, M8)

## CERRADO Y VERIFICADO (2026-07-18)

> "Primera tarea: descargar el diccionario de datos REAL de la DGT y confirmar el
> esquema (el [ASUMIDO] de §5 se cierra aquí)." — hecho, con dos hallazgos reales
> que la carta NO anticipaba, declarados íntegros en esta nota.

## 1. Esquema DGT confirmado contra la fuente primaria (no heredado de investigación previa)

Descargado el documento oficial *"Documento de interfaz de Envío de Datos
(Transferencias)"* directamente de
`https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/matraba/TRANSFERENCIAS_MATRABA.pdf`
(2026-07-18). 69 campos de ancho fijo, **suma exacta 714 bytes** — verificado
programáticamente sumando las 69 longitudes declaradas, y cruzado contra una línea
real del fichero descargado (715 bytes = 714 + salto de línea). **Cero discrepancia**
entre el interfaz documentado y el fichero real.

Campos usados por este pilar, offsets verificados byte a byte contra una fila real:

| Campo | Offset (0-indexed) | Ejemplo real verificado |
|---|---|---|
| FEC_TRAMITACION | `[9:17]` | `01062026` → 2026-06-01 |
| MARCA_ITV | `[17:47]` | `SUZUKI` |
| MODELO_ITV | `[47:69]` | `AN 400` |
| COD_TIPO | `[91:93]` | `50` (motocicleta) |
| COD_PROVINCIA_VEH | `[152:154]` | `BI` (Bizkaia) |
| CLAVE_TRAMITE | `[156:157]` | `2` (Transferencia — coherente: el fichero ES de transferencias) |
| BASTIDOR_ITV | `[70:91]` | `JS1BW11110***********` — 8 caracteres reales + asteriscos, confirma la restricción de bastidor desde 2025-02-01 |

Confirmado independientemente (no asumido): **sin campo de precio** en ninguno de los
69 campos.

## 2. HALLAZGOS REALES no anticipados por la carta (declarados, no maquillados)

### 2.1 Los códigos de provincia DGT NO son los códigos INE de Cardeep

La carta no mencionaba este riesgo. `COD_PROVINCIA_VEH` es la letra histórica de
matrícula (`M`=Madrid, `B`=Barcelona, `GC`=Las Palmas...), NO el código numérico INE
de 2 dígitos que usa `geo_province.code`. Construido
`pipeline/market/dgt_provinces.py::DGT_PROVINCE_TO_INE` cruzando DOS fuentes
primarias independientes: el Anexo I del PDF oficial + `SELECT code, name FROM
geo_province` en vivo. **Verificado al 100%**: los 396.069 registros de junio 2026
mapean a exactamente 52 códigos provinciales, **0 sin mapear**.

### 2.2 El fichero de transferencias incluye TODO tipo de vehículo, no solo turismos

DGT's `COD_TIPO` cubre camiones, motocicletas, remolques, tractores, etc. (Anexo I
§1.3.4, decenas de códigos). El censo de Cardeep es SOLO coches. Comparar el
`gone_count` de Cardeep contra un `dgt_count` sin filtrar habría inflado el
denominador con vehículos que Cardeep nunca rastrea. **Corregido en la raíz** (antes
de comprometer ningún dato): se añadió `cod_tipo` al esquema de `dgt_transfer`
(migración `0077`, columna incluida desde el primer commit — la migración se
revirtió y re-aplicó UNA vez internamente durante el desarrollo, antes de comprometer
nada a git, para incorporar esta columna) y `corroborate.py` filtra siempre a
`COD_TIPO='40'` (TURISMO).

## 3. Migraciones

- `migrations/0077_dgt_transfer.sql`: `dgt_transfer_batch` + `dgt_transfer`.
  **Colisión de FK real encontrada y corregida**: `geo_province`'s PK real es
  COMPUESTA `(country_code, code)` (un refactor multi-país posterior a como
  `0002_entities.sql` lo documentaba originalmente) — un FK de una sola columna
  `REFERENCES geo_province(code)` falló con `InvalidForeignKeyError` en el primer
  intento de aplicar. Corregido con un FK compuesto `(country_code, province_code)
  REFERENCES geo_province(country_code, code)` y `country_code CHAR(2) DEFAULT
  'ES'`, verificado contra `pg_constraint` en vivo (no asumido de la migración vieja).
- `migrations/0078_dgt_corroboration.sql`: `dgt_corroboration_run` + `dgt_corroboration`.
- **Bug de sintaxis encontrado y corregido**: comentarios `--` terminados en `;` en
  medio de un `CREATE TABLE` rompen el splitter de `scripts/migrate.py` (que corta
  por líneas terminadas en `;` sin distinguir comentario de sentencia). Corregido
  reescribiendo los comentarios afectados en mi propia migración — no se tocó
  `scripts/migrate.py` (herramienta compartida, fuera de este alcance).
- Ambas migraciones: aplicadas, rollback probado dentro de una transacción
  deliberadamente abortada (patrón F0/F1/F2).

## 4. Ingesta real (protocolo §7: doble descarga + hash idéntico)

```
batch_id=01KXS82N3H4VN2QG8WZNHTWRCA
month=202606
source_url=https://www.dgt.es/microdatos/salida/2026/6/vehiculos/transferencias/export_mensual_trf_202606.zip
zip_sha256=e74a3a2f132a4b9e536a9b1cbf66116bfa299ed072681d1b14c3cb98787359be
zip_size_bytes=40.396.793
n_rows_parsed=396.069 (1 línea truncada/malformada descartada, documentada)
n_rows_transferencia=396.069 (100% — confirma que el fichero es puramente de transferencias)
double_download_verified=TRUE (segunda descarga independiente, MISMO hash exacto)
280.236 de 396.069 filas son COD_TIPO=40 (TURISMO)
```

**Nota sobre la URL real** (hallazgo, no en la carta): el mes en la URL NO va con
cero a la izquierda (`.../2026/6/...`, no `.../2026/06/...`) — verificado extrayendo
los 138 enlaces reales de
`https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/transacciones-automoviles-mensual.html`
por HTML crudo (una herramienta de resumen por IA sobre la misma página sugirió
erróneamente el cero a la izquierda — descartado tras verificación directa,
antialucinación en acción).

## 5. Corroboración M8 (real, calculada, publicada con honestidad cruda)

```
run_id=01KXS870AFRAQE3MERCYZGRTBN
cohortes=89.144 (nivel marca + nivel marca+modelo combinados)
totales nivel-marca nacional: gone=370.413  dgt(turismo)=280.236
```

### Hallazgo honesto: la ventana de GONE de Cardeep para junio es PARCIAL, no el mes completo

`vehicle_event` para GONE en junio 2026 solo cubre **2026-06-12 → 2026-06-28** (16
días), no el mes completo — el pipeline de Cardeep arrancó su historial el 12 de
junio (per F0). Comparar un `gone_count` de 16 días reales de scraping contra un
`dgt_count` de DGT del mes COMPLETO es una comparación desigual, declarada aquí, no
escondida — mejorará automáticamente según se acumule más historia.

### Ejemplo real de cohorte (Madrid, marca a marca, nivel provincial)

| Marca | gone_count | dgt_count (turismo) | ratio |
|---|---|---|---|
| Mercedes-Benz | 9.464 | 2.387 | 25,2% |
| Volkswagen | 7.440 | 3.150 | 42,3% |
| BMW | 6.890 | 2.722 | 39,5% |
| Peugeot | 6.647 | 3.618 | 54,4% |
| Renault | 5.504 | 3.648 | 66,3% |
| SEAT | 4.805 | 2.933 | 61,0% |

Ratios entre 25% y 66% — **DGT siempre por debajo de GONE de Cardeep**, consistente
con la propia tesis de la carta: "el delta GONE=vendido es el eslabón MÁS DÉBIL"
(§2, veredicto adversarial punto 2). Un anuncio "retirado" no siempre es un coche
"vendido" (puede ser retirado, expirado, movido de plataforma, duplicado) — M8 mide
EXACTAMENTE esa brecha, con honestidad, tal como la carta pide.

## 6. Reconciliación mensual contra cifras públicas (protocolo §7, fila "agregados nacionales")

Fuente real: [motor16.com, "El mercado de vehículos de ocasión en España crece un
1,9% y supera el millón de operaciones hasta junio"](https://www.motor16.com/las-ultimas-noticias/mercado-ocasion-espana-junio-2026/) —
**GANVAM reporta 186.775 turismos de ocasión vendidos en junio 2026** (+6,5%
interanual). Mi conteo DGT de TURISMOS transferidos en junio: **280.236**.

**Desviación explicada, no maquillada**: GANVAM es "inferencia estadística sobre
muestra voluntaria de empresas" (carta §2, fila GANVAM) — mide VENTAS mediadas por
negocio/concesionario mediante estimación muestral. Mi conteo DGT es el CENSO
COMPLETO de transferencias de titularidad de turismos, que incluye traspasos
particular-a-particular, herencias, y reasignaciones de flota que el método de
GANVAM excluye o estima de forma distinta. Ratio 280.236/186.775 ≈ 1,5× — plausible
dado que "transferencia de titularidad" (DGT, censo) y "venta mediada por negocio"
(GANVAM, muestra) son, literalmente, magnitudes distintas — exactamente el tipo de
desviación que la carta anticipó documentar ("censo≠ventas").

## 7. Router — M8 añadido a `market.py`

`GET /market/dgt-corroboration` (query: `province`, `make`, `model` — todos
opcionales; `model` omitido devuelve solo filas a nivel de marca). Nunca fabrica un
ratio: `gone_count=0` → `ratio=null`, nunca una división inventada. 6/6 tests de
contrato verdes contra el run real.

## 8. Verificación completa

- **Parser**: 16 tests unitarios puros (`tests/test_ingest_dgt.py`) — línea real de
  ejemplo verificada campo a campo, mapeo de provincia (52/52), casos borde (línea
  corta, fecha inválida, código sin mapear).
- **Corroboración**: 5 tests (`tests/test_corroborate.py`) — límites de mes,
  cómputo de cohortes con fixtures sintéticos con valores calculados a mano (3 DGT
  turismo + 1 DGT motocicleta excluida / 5 GONE Cardeep → ratio 3/5 exacto),
  cohorte presente en un solo lado NUNCA se esconde (INNER JOIN habría ocultado
  exactamente este caso).
- **Router M8**: 6 tests de contrato (`tests/test_market_router_m8.py`) contra el
  run real publicado.
- **Ingesta real de producción**: 1 mes (junio 2026) ingerido con doble
  descarga+hash idéntico ✓; corroboración computada y documentada con honestidad
  cruda (ratios 25-66%, explicados, no maquillados) ✓; reconciliación mensual
  contra GANVAM con desviación explicada ✓.

## Cierre F4

Los 3 criterios de la carta §9-F4 en verde, más 2 hallazgos reales no anticipados
por la carta (mapeo de provincia DGT↔INE; filtrado por tipo de vehículo) resueltos en
la raíz antes de comprometer ningún dato. El [ASUMIDO] del esquema DGT que la carta
declaraba en §5 queda [VERIFICADO] con evidencia primaria doble (documento oficial +
fichero real descargado y parseado byte a byte).
