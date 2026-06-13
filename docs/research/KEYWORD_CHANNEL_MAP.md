# CARDEEP — KEYWORD → CHANNEL MAP · ESPAÑA (front `keyword_census`)

> **Qué es esto:** el mapa keyword-driven de *todo lugar donde se vende un coche usado*
> en España. Para cada término/keyword de búsqueda se lista el canal/operador que hay
> detrás, se cruza contra la taxonomía y entidades reales de la DB
> (`postgres://cardeep@localhost:5433/cardeep`, tabla `entity`), y se **MARCA en rojo
> cualquier tipo-de-canal u operador NUEVO** no presente en nuestra taxonomía.
>
> **Verificación:** keywords barridas en vivo vía WebSearch + WebFetch + curl_cffi
> chrome131 el **2026-06-13**. Cada conteo de DB es de **mi propia query** ese día.
> EXCLUYE redes sociales (FB/IG) por mandato del owner.
>
> **Hallazgo nuclear — distinción "estado-de-vehículo" vs "canal":** la mayoría de las
> keywords de coche usado (km0, seminuevo, demo, gerencia, dirección, cortesía, stock,
> garantizado, certificado) NO son canales: son **atributos/estados del vehículo** que
> se venden por los MISMOS canales ya censados (concesionario oficial, compraventa,
> portal VO de OEM). Son **filtros de inventario**, no operadores. Solo unas pocas
> familias de keyword revelan un **tipo-de-canal genuinamente nuevo** (ver §NUEVO).

---

## Taxonomía DB actual (referencia para el cruce)

`entity.kind` (12): `concesionario_oficial · agente_oficial · compraventa · garaje ·
desguace · rent_a_car_vo · subasta · importador · oem_vo_portal · plataforma · cadena ·
particular`

`entity.source_group` (11): `marketplace_generalist · marketplace_motor · oem_vo_portal ·
oem_dealer_network · chain · rentacar_vo · official_registry · association · directory ·
desguace_network · long_tail_web`

Conteos vivos (mi query 2026-06-13): total **368.500** entidades · `compraventa` 31.519 ·
`concesionario_oficial` 1.681 · `garaje` 7.220 · `desguace` 1.645 · `subasta` 94 ·
`oem_vo_portal` 14 · `plataforma` 10 · `cadena` 4 · `rent_a_car_vo` 3 ·
**`importador` 0** · **`agente_oficial` 0** · `particular` 326.310.

---

## Mapa keyword → canal

Leyenda canal: `[EXISTE]` = tipo ya en taxonomía con anchors en DB ·
`[FILTRO]` = la keyword es un estado/atributo del vehículo, mismo canal ya censado ·
`[NUEVO-TIPO]` = revela un tipo-de-canal sin slot en la taxonomía ·
`[NUEVO-OP]` = operador concreto faltante en DB.

### A. Keywords de "estado del vehículo" → FILTRO, no canal nuevo

| Keyword | Qué surfacea | Canal real | Veredicto |
|---|---|---|---|
| `venta de coches` / `coches de ocasión` / `coches de segunda mano` | coches.net, wallapop, milanuncios, AS24, autocasion, todo concesionario/compraventa | marketplace_* + compraventa + concesionario_oficial | `[EXISTE]` raíz del universo |
| `seminuevos` | concesionarios y portales VO (0-2 años, <25.000 km) | concesionario_oficial / oem_vo_portal / compraventa | `[FILTRO]` |
| `km0` / `kilómetro cero` | concesionario que matricula sin uso (<1.000 km); Gyata, Driveris, HR Motor, coches.net/km-0 | concesionario_oficial / cadena / compraventa | `[FILTRO]` |
| `coche de gerencia` / `coche de dirección` | uso interno marca/concesionario (<10-15k km); Renault Retail, Movento, milanuncios facet | concesionario_oficial / oem_vo_portal | `[FILTRO]` |
| `vehículo de demostración` / `demo` | coche de pruebas del concesionario; coches.net/km-0/demostracion | concesionario_oficial / oem_vo_portal | `[FILTRO]` |
| `coche de cortesía` | coche de sustitución del taller revendido | concesionario_oficial / garaje | `[FILTRO]` |
| `stock concesionario` / `vehículos disponibles` | inventario inmediato del dealer | concesionario_oficial / compraventa | `[FILTRO]` |
| `ocasión garantizado` / `certificado` / `sello de ocasión` | programas OEM (Das WeltAuto, VW Approved, renew "Refactory certified", Toyota 150-puntos, Spoticar, H Promise, MB Certified) + Carfax (OcasiónPlus) | oem_vo_portal (todos ya anchored) | `[FILTRO]` sobre canal existente |
| `outlet de coches` / `liquidación de stock` | sección de saldos de compraventas/cadenas (Yamovil, Canalcar, AutosportMoraleja, Carmotive, CarsyDreu, Coches Market) | compraventa / cadena | `[FILTRO]` |
| `coches baratos` / `ofertas` | mismo inventario, orden por precio | todos | `[FILTRO]` |
| regional: `cotxes d'ocasió` (cat) / `coches de ocasión Canarias/Galicia` | mismas plataformas con geo-filtro + buscadores regionales (Buscocoches, Catalunya Motor, Factoría de Automóviles) | marketplace_* (geo) + compraventa | `[FILTRO]` geo (+ aggregators regionales menores) |

### B. Keywords que SÍ revelan canal/operador → cruce y flags

| Keyword | Canal que surfacea | Operadores clave | Estado en DB |
|---|---|---|---|
| `subasta de vehículos` (B2B) | plataformas de subasta para profesionales | Autorola ✓, Ayvens Carmarket ✓, BCA ✓ · **CarCollect, Manheim.es, LocalizaVO** | parcial — 3 anchored, **3 NUEVO-OP** |
| `compro tu coche` / `vendemos tu coche` / `tasación online` | compradores-revendedores con tasación instantánea | OcasiónPlus ✓, Crestanevada ✓, Autofesa ✓, compramostucoche/AUTO1 ✓, Driveris ✓, Yamovil ✓, Dursan ✓, Sibuscascoche ✓, Esmicoche ✓ · **MODRIVE** | mayoría ya como `compraventa`; el *servicio de compra* no se modela como canal aparte → ver nota |
| `renting fin de contrato` / `renting flexible venta` / `coches de flota` / `vehículos de empresa` | **leasing/renting operacional vendiendo su ex-flota VO** | Arval, Alphabet, Athlon, Northgate, Ayvens — todos presentes como `compraventa` sueltas, **sin source_group `renting_vo` ni su portal VO oficial** | **NUEVO-TIPO** (ver §NUEVO-1) |
| `plataforma VO con financiación` | agregador VO bancario | **faciliteacoches.com** (CaixaBank + Arval; "tiendas oficiales") | **NUEVO-OP / NUEVO-TIPO** (ver §NUEVO-2) |
| `coches importados` / `importación de Alemania` | **importadores a la carta / stock alemán** | TrendCars ✓(compraventa), Carismatic ✓ · **Raceocasion, ImportyGarage, DeutscheCars, Europa Automotive, importarcochesalemania** | `kind='importador'` existe pero **0 entidades** → **NUEVO-TIPO sin poblar** (ver §NUEVO-3) |
| `coches clásicos` / `youngtimer` / `coche de colección` | **marketplaces de clásicos/coleccionismo** | **ComprococheClasico, AutoClassic24, JJDluxeGarage, Francisco Pueche** (+ facets clásicos en wallapop/milanuncios/coches.net) | **NUEVO-TIPO sin slot** (ver §NUEVO-4) |
| `concesionario online` / `entrega a domicilio` | retailers digital-native | Clicars ✓, Carplus ✓, Autohero ✓ · CarHay ✓, Carways ✓, Autoconfi ✓, ComprayConduce ✓ (todos `compraventa`) | `[EXISTE]` como compraventa/cadena (delivery = atributo, no canal) |
| `coche de club` / `RACC ocasión` | **portal VO de auto-club** | **cochesocasion.racc.es** (RACC) | **NUEVO-OP** menor (auto-club como agregador VO) |
| `furgonetas de ocasión` / `vehículo comercial derivado de turismo` | comerciales ligeros en los mismos canales | Spoticar ✓, OcasiónPlus ✓, Crestanevada ✓, Driveris ✓ · Terry Ocasión | `[FILTRO]` (scope cars-only; derivados de turismo borderline) |

---

## §NUEVO — tipos-de-canal / operadores faltantes (lo que esta pasada DESTAPA)

### NUEVO-1 · `renting_vo` (leasing operacional vendiendo ex-flota) — TIPO FALTANTE
**Distinto de `rentacar_vo`** (que es alquiler turístico: Centauro/OK/Record). Aquí el
operador es **renting/leasing operacional B2B** que liquida su flota a fin de contrato por
portal VO propio:
- **Arval** (`arval.es/vehiculos-de-ocasion` — 200 curl_cffi, listados client-side) — BNP Paribas
- **Alphabet** (`alphabet.com/.../Vehiculos-de-ocasion` — 200, SSR shell, inventario JS) — BMW Group
- **Athlon** (`athlon.com/es/vehiculos-de-ocasion/`, "Athlon Car Outlet", venta a particular) — 200
- **Northgate** (`northgate.es/vehiculos-ocasion`, líder VI renting) — 200
- **Ayvens** (`ayvens.com/.../vehiculos-usados/` — antes LeasePlan/ALD; ya tiene `chain` anchor + Carmarket subasta)

Hoy en DB aparecen como filas `compraventa` dispersas (Arval Barcelona/Coruña/Sevilla;
Athlon Car Outlet; Northgate Ocasión; Ayvens Leganés) **sin agruparse bajo un
`source_group='renting_vo'` ni conectar su portal VO oficial**. Recomendación: nuevo
`source_group renting_vo` (espejo de `rentacar_vo`), un connector wholesale por operador
(patrón `group_rentacar_vo_wholesale.py`), inventario JS → camoufox/API.

### NUEVO-2 · `faciliteacoches.com` — agregador VO bancario (TIPO + OP) — FALTANTE
Plataforma VO de **CaixaBank** con financiación, modelo "tiendas oficiales" que agrega
Arval + dealers. `200` a curl_cffi chrome131 (764 KB SSR, sig=174 → atribución/precio en
HTML). **No existe en DB.** Es un `marketplace_motor`/agregador con atribución dealer →
candidato de cosecha directa. **NUEVO-OP claro.**

### NUEVO-3 · `importador` — kind EXISTE, 0 ENTIDADES — TIPO VACÍO
La taxonomía ya tiene `kind='importador'` pero **0 filas**. Familia real y reachable:
- **Raceocasion** (`raceocasion.es` — 200, sig=48, stock SSR)
- **MODRIVE** (`modrive.com/coches-segunda-mano/` — 200, sig=243, stock SSR rico)
- **Europa Automotive** (`europamotive.com` — 200, shell SSR, listado JS)
- ImportyGarage, DeutscheCars, importarcochesalemania.online (probar superficie)
- TrendCars y Carismatic ya en DB como `compraventa` → reclasificar a `importador`.

Estos venden VO importado (mayormente DE) con ahorro ~10-20%. Connector tipo
compraventa-mono-owner; reachable €0 (curl_cffi). **Poblar el `kind` vacío.**

### NUEVO-4 · marketplaces de COCHES CLÁSICOS / youngtimer — TIPO SIN SLOT — FALTANTE
Segmento sin tipo en la taxonomía ni entidades (`%clasico%`/`%classic%` solo dan
particulares y un garaje de detailing). Operadores:
- **ComprococheClasico** (`comprococheclasico.es`) · **AutoClassic24** (`autoclassic24.com`,
  marketplace global) · **JJDluxeGarage** · **Francisco Pueche** (`pueche.com`).
- Más facets de clásicos dentro de wallapop/milanuncios/coches.net (ya cubiertos por esas
  plataformas; el delta son los marketplaces especialistas).
Decisión owner pendiente: ¿in-scope clásicos? Si sí → nuevo `kind`/`source_group`
`classic_marketplace`. Si no → declarar excluido explícito.

### NUEVO-5 · subastas B2B no censadas — OPERADORES FALTANTES
`source_group='official_registry'` tiene subastas de Autorola/Ayvens/BCA pero faltan:
- **CarCollect** (`carcollect.com/es` — 200, app JS; oferta de leasing+dealers)
- **Manheim.es** (Cox Automotive — login-walled, B2B duro; oferta Europcar+leasing+OEM)
- **LocalizaVO** (`localizavo.es` — SSR shell, subastas semanales para profesionales;
  oferta rentacar+flotas+dealers+particulares)
Reachability: LocalizaVO/CarCollect públicas (shell SSR, inventario tras login/JS);
**Manheim requiere login** → honestamente *muro B2B*, no free-vector sin credenciales.

---

## Honestidad — huecos genuinos / no-alcanzables-gratis declarados

- **Manheim.es**: subasta B2B login-walled. Sin credenciales de profesional, el inventario
  no es alcanzable por vector gratis. Hueco honesto (no se inventa stock).
- **Arval / Alphabet / Athlon VO**: shell SSR `200` pero el listado de coches se pinta
  client-side (sig bajo) → requiere camoufox o reversear su BFF/API. Reachable con esfuerzo
  browser, no con curl plano.
- **faciliteacoches**: `403` a WebFetch pero `200` a curl_cffi chrome131 → reachable con
  fingerprint Chrome (no con HTTP plano).
- **Clásicos**: pendiente de decisión de scope del owner antes de construir connector.
- Las keywords de "estado de vehículo" (km0/seminuevo/gerencia/etc.) **no abren ningún
  canal nuevo** — confirmado: son filtros sobre canales ya censados. No se fuerza un
  tipo-de-canal donde no lo hay.

## Δ a aplicar (resumen accionable para el Director)

1. Crear `source_group='renting_vo'` + connectors Arval/Alphabet/Athlon/Northgate/Ayvens VO.
2. Conectar **faciliteacoches.com** (agregador VO CaixaBank, curl_cffi, atribución dealer).
3. **Poblar `kind='importador'`** (Raceocasion, MODRIVE, Europa Automotive, ImportyGarage,
   DeutscheCars) y reclasificar TrendCars/Carismatic.
4. Añadir subastas B2B reachable: **LocalizaVO, CarCollect** (Manheim declarado walled).
5. RACC ocasión como operador VO de auto-club (menor).
6. Decidir scope de **coches clásicos**; si in-scope, crear tipo `classic_marketplace`.
