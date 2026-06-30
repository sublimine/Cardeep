# L'argus — Auditoría atómica (intel de automoción · valoración)

> Slug: `l-argus` · Subdominio cardeep: **valuation** · Web pública: https://www.largus.fr/cote/ ·
> Portal pro: https://pro.largus.fr (→ `prolargus.leboncoin.auto`) · API: https://developer.leboncoin.auto
> (antes `developer.largus.fr`) · API host: `https://api.leboncoin.auto`.
> Fecha auditoría: 2026-06-30. Doctrina VAM aplicada: cada bloque marcado [VERIFICADO]/[ASUMIDO] con fuente.
> **Nota de método:** la fuente de campos más rica es la colección Postman EN VIVO de la API Argus
> (2,8 MB, descargada vía `documenter.gw.postman.com/api/collections/12365936/2sB3HgRPsT`), cruzada con
> los datasheets PDF de producto y el comunicado de adquisición de Adevinta. Todo el inventario de campos
> de abajo es texto literal de esas fuentes, no inferido.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **L'argus** / **Cote Argus®** (marca de valoración) | [VERIFICADO] |
| Razón social editora | **SNEEP** — RCS 572 214 591 (París) | [VERIFICADO] (RCS impreso en datasheets PDF + Wikipedia) |
| Grupo / owner | **leboncoin Group** (filial de **Adevinta**). Adquisición de Argus Group anunciada 09/09/2019 y cerrada ~07/10/2019 | [VERIFICADO] (press release Adevinta) |
| Marca de datos hoy | Integrada en **"leboncoin auto"**: dominios `api.leboncoin.auto`, `developer.leboncoin.auto`, `prolargus.leboncoin.auto` (migración 301 observada en vivo desde `*.largus.fr`) | [VERIFICADO] (redirecciones HTTP en directo) |
| HQ | París, Île-de-France (Francia) | [VERIFICADO] |
| Fundación | **1927**, por Paul Rousseau (financiado por Ernest Loste); título original *L'argus de l'automobile et des locomotions* | [VERIFICADO] (Wikipedia + datasheets "depuis 1927") |
| Naturaleza | Editor de contenidos + proveedor de datos/valoración de automoción; "empresa familiar independiente" hasta 2019 | [VERIFICADO] |

**Segmentos de negocio del grupo (5)** [VERIFICADO, press release Adevinta]:
`Argus Information` · `Argus Valuation` · `Argus Solution` · `Argus Acquisition` · `Argus Consulting`.
Esta auditoría cubre a fondo **Information** (Référentiel = datos técnicos/comerciales) y **Valuation**
(Cote, Valeurs de marché, Valeur Résiduelle); **Solution** (software de gestión VO) se cubre parcialmente.

**Posición de mercado:** la **Cote Argus®** es la valor-pivot de referencia del VO en Francia desde 1927,
con **~90% de cuota** declarada en valoración de ocasión. "Seule valeur-pivot reconnue par les
professionnels de l'automobile, les professions réglementées et le grand public." [VERIFICADO] (press
release Adevinta + datasheet Cote).

**Cliente objetivo** [VERIFICADO, descripciones API + datasheets]: constructeurs (OEM), loueurs
(renting/leasing LLD-LOA), assureurs (peritaje/VRADE), concessionnaires/distribution, financeurs
(établissements financiers, garantisseurs), infomédiaires (portales y apps), professions réglementées
(notarios, expertos judiciales, administración) y **grand public** (particulares en largus.fr).

---

## 2. Cobertura y scope

| Eje | Detalle | Estado |
|---|---|---|
| País | **Francia** (mercado francés). Cote/valeurs ancladas al parc y mercado FR | [VERIFICADO] |
| Idiomas API | FR + versión EN completa de la doc | [VERIFICADO] |
| Tipos de vehículo | **VP** (voitures particulières), **VUL/VU** (utilitaires légers ≤3,5 t), **2 roues**, **quads** y **véhicules sans permis** | [VERIFICADO] (datasheet Référentiel + body-types API) |
| Nuevo vs usado | **VN y VO**. Précisamente: catálogo VN (precios y specs constructor) + valoración VO + valores residuales a futuro VN/VO | [VERIFICADO] |
| Volumen referencial (datasheet 04/2016) | VP: 60 marcas / 393 modelos / 15 316 véhicules / **268 infos por vehículo**; VUL: 25 / 84 / 5 202 / 219; 2-roues: 55 / 451 / 1 764 / 35 | [VERIFICADO] (datasheet, cifras de 2016 — hoy probablemente mayores [ASUMIDO]) |
| Body-types soportados (API) | Berline, Break, Coupé, Cabriolet, Coupé-cabriolet, Monospace, SUV, Crossover, Routière, Sportive, Pick-Up, Ludospace, Fourgon, Fourgonnette, Combi, Minibus, Société, Plancher/Plateau/Châssis Cabine, Benne, Grand Volume, Dérivé de VP-N1, Tout terrain; **2 roues:** Scooter, Roadster, Trail, Trial, Enduro, Cross, Supermotard, Custom, Cyclo, 3 roues | [VERIFICADO] (tabla body-type API) |
| Histórico (mercado) | Transacciones desde 2000 (14 M acumuladas), anuncios/stocks desde 2009 (5 M), demandas de Cote desde 2004 | [VERIFICADO] (datasheet Cote) |

---

## 3. Productos de datos + lista ATÓMICA de campos

### 3.1 Référentiel Argus® (datos técnicos y comerciales VN/VO) — *segmento Information*

Base de datos modular que identifica un vehículo por **catégorie → marque → modèle → sous-modèle →
génération → phase → version → période**, con specs técnicas, equipamiento y precios. Reconocimiento por
**CNIT / Type Mine** desde 1998. Enriquecido a diario por analistas. API JSON:API REST (`/specs/2.0/...`),
60 tipos de recurso. Es la espina dorsal de identificación de todo lo demás. [VERIFICADO]

**Identificación / taxonomía (campos por recurso):**
- **category:** `name`
- **make:** `name`, `legacy-id`, `position-quote` (popularidad por nº de cotaciones), `start-date`, `end-date`
- **model:** `name`, `legacy-id`, `start-date`, `end-date`
- **submodel:** `name`, `full-nicename`, `short-nicename`, `position-quote`, `legacy-id`, `start-date`, `end-date`
- **generation:** `name`, `full-nicename`, `short-nicename`, `body-type`, `body-type-classified-ad`, `segment`, `segment-code`, `segment-europe`, `segment-referentiel`, `position`, `legacy-id`, `start-date`, `end-date`
- **phase:** `name`, `full-nicename`, `short-nicename`, `position`, `legacy-id`, `start-date`, `end-date` (una *phase* = restyling/mejora técnica)
- **version:** `name`, `full-nicename`, `short-nicename`, `number-of-doors`, `number-of-places`, `trim-level` (finition), `lcv-body-type`, `position`, `position-quote`, `quote-ratio`, `quotable`, `prevarable`, `first-quote-at`, `legacy-id`, `start-date`, `end-date` (recurso "intersección", el más completo)
- **period:** `model-year` (millésime), `price-including-vat` (prix TTC), `price-excluding-vat` (prix HT), `manufacturer-spec-1/-2/-3` (códigos constructor, full-text), `start-date`, `start-date-type`, `end-date`, `end-date-type`

**Motor / energía:**
- **energy:** `name`, `code`, `master-code`, `master-id`, `master-name`, `legacy-id`
- **engine:** `market-name`, `power-market-name`, `full-nicename`, `acronym`, `din-horsepower` (ChDIN), `fiscal-horsepower` (puissance fiscale), `kilowatt` (kW), `cubic-capacity` (cilindrada), `liter-capacity`, `number-of-valves`, `compression-ratio`, `bore-and-stroke` (alésage×course), `configuration`, `layout`, `injection-system`, `supply` (alimentación), `torque` (par), `max-power-rpm`, `max-torque-rpm`, `standard-emission` (norma Euro)
- **battery (EV/híbrido):** `capacity` {value,unit}, `power` {horsepower,kilowatt,label}, `operating-voltage`, `micro-hybrid-voltage`, `recharge-time` {minimum,maximum,unit}, `charging-cable-length`, `used-for-traction`, `cost` {currency,value}, `weight`, `description`
- **fuel-cell (H2):** `fuel`, `fuel-cell-type`, `maximum-power`, `power-density`, `volume`, `weight`
- **tank:** `fuel`, `fuel-total-capacity` {value,unit}, `hydrogen`

**Consumo / emisiones (consumption):** `urban-fuel`, `extra-urban-fuel`, `combined-fuel` (conso mixte), `co2-emission-level` (CO2), `carbon-monoxide`, `nitrous-oxyde`, `particulate-matter`, `total-hydrocarbons`, `electric-range` (autonomía elec.), `driving-cycle`, `driving-cycles`

**Dimensiones / peso / maletero:**
- **dimension:** `length`, `width`, `height`, `height-including-roof-rails`, `wheelbase` (empattement), `front-track`, `rear-track`, `front-overhang`, `rear-overhang`, `ground-clearance` (garde au sol), `approach-angle`, `departure-angle`, `brake-over-angle`, `drag-coefficent` (Cx), `fuel-tank-capacity`, `lcv-height-type`, `lcv-wheelbase-type`
- **weight:** `kerbweight` (poids à vide), `kerbweight-including-driver`, `payload` (charge utile), `gross-vehicle-rating` (PTAC), `gross-combined-rating` (PTRA), `braked-trailer`, `unbraked-trailer`
- **boot (coffre):** `capacity`, `maximum-capacity`, `minimum-capacity`, `third-row-capacity`, `usable-length`, `usable-width`, `load-still-height`, `maximum-length`

**Prestaciones / chasis / rodaje:**
- **performance:** `maximum-speed` (V-max), `da-0-100kph` (0-100 km/h), `da-0-1000m`
- **platform:** `chassis-type`, `chassis-material`, `front-suspension-type`, `rear-suspension-type`, `suspensions` {front,rear,type}, `brakes` {front,rear,parking,regenerative,controller}, `power-steering`, `power-steering-type`, `power-steering-assistance`, `steering-wheel-lock-to-lock-turns`, `turning-circle-between-kerbs`, `turning-circle-wall-to-wall`, `euroncap-ratings`, `lcv-cab-type`
- **gearbox:** `name`, `code`, `marketing-name`, `subtype` (manuelle/automatique…), `number-of-gears`
- **transmission:** `driven-wheels` (tracción), `marketing-name`, `number-of-gears`
- **tyre:** `front`, `rear`, `front-sizes` {width, aspect-ratio, rim-diameter, radial-construction, size}, `rear-sizes` {…}, `construction-type`, `wheel-type`, `sparewheel-type`
- **warranty:** `manufacturer` {years,mileage}, `anti-corrosion` {years,mileage}, `battery` {years,mileage}

**Equipamiento (de serie / opción, con precios y lógica):**
- **feature-category:** `name`
- **feature** (atributo): `name`, `legacy-id`, `manufacturer-spec` (código constructor), `price-including-vat`, `price-excluding-vat` · filtro `availability` = standard|optional
- **equipment:** `name`, `legacy-id`, `manufacturer-spec`, `price-including-vat`, `price-excluding-vat`
- **pack:** `name`, `legacy-id`, `manufacturer-spec`, `price-including-vat`, `price-excluding-vat`
- Del datasheet: **Couleur**, **Sellerie**, **GPS**, **Climatisation**, **Xénon** (ejemplos), "l'intégralité des options **y compris leurs liens logiques**" + módulo **Équipements différenciants** (frecuencia de la finición en el parc francés)

> Cobertura declarada: ≈150 caractéristiques techniques por reconocimiento CNIT/Type Mine; hasta **268
> informaciones por vehículo VP** (incluyendo equip. serie y opción). [VERIFICADO]

### 3.2 Cote Argus® + Valeurs Argus® de marché (valoración) — *segmento Valuation* — **NÚCLEO**

"El único outil 5-en-1": comprar mejor / anunciar mejor / revender mejor / gestionar stock mejor.
Estructurado en **ciclo de vida VO: Reprise → Annonce → Vente → Gestion**. Vía web (largus.fr,
pro.largus.fr) y API asíncrona (`POST /checkout/3.0/valorizations` → websocket/polling → `GET .../values`).
[VERIFICADO]

**Mapa oficial offer → subtype → nombre comercial** (literal de la doc API, oferta `extended-market-values`):

| `subtype` (campo respuesta) | Nombre comercial (libellé Argus) | Qué es |
|---|---|---|
| `custom-market-values` | **Cote Argus®** (web: *Cote Argus Personnalisée®*) | Cote de référence à dire d'expert, editada desde 1927; base de reprise/valorización de stock |
| `displayed-selling-values` | **Valeur Argus Annonces®** | Prix d'annonce conseillé (a partir de últimos precios mostrados que dispararon transacción) |
| `btoc-transaction-values` | **Valeur Argus Transaction®** (B2C) | Estimación del precio de venta real a **particular**, sobre observatorio de reventas efectivas FR |
| `btob-transaction-values` | **Valeur Argus Transaction®** (B2B) | Estimación del precio de venta real a **profesional** |
| `initial-prices` | **Prix du Neuf** | Precio catálogo del vehículo (del Référentiel) |
| `expected-refurbishment-costs` | **Frais de remise en état attendus** | Coste esperado de reacondicionamiento |

**Producto adicional del datasheet (web):**
- **Délai Argus Rotation®** = mediana de tiempo de detención (de compra a venta) de vehículos similares
  → *days-to-sell / coste de detención*. Ej. "36 jours". [VERIFICADO datasheet]
- **Marge de Manœuvre** = límite de precio recomendado no superar (asociado a Valeur Annonces) →
  expuesto en API como **`leeway`** {`percentage`, `value`}. [VERIFICADO]
- **SONAR Argus Annonces®** y **SONAR Argus Transactions®** = herramientas paramétrables que muestran
  ejemplos reales de anuncios / transacciones anonimizadas de vehículos similares en la zona de chalandise
  o toda Francia. [VERIFICADO datasheet]

**Campos atómicos del objeto `values` (respuesta de valoración):**
`value` (importe €), `standard-value` (valor a km estándar), `subtype` (tipo de valor, ver tabla),
`confidence-index` (índice de confianza 0-10), `confidence-intervals` {`min`, `max`, `probability`},
`dispersion` (dispersión del mercado), `leeway` {`percentage`,`value`} (=Marge de Manœuvre),
`influence` {`body`, `mileage`, `options`, `professional-fees`, `release`} (descomposición del efecto de
cada factor sobre el valor), `region-plus` / `region-minus` (ajuste regional ±), `mileage`, `released-at`
(mise en circulation), `application-type`, `has-map` (¿hay mapa de dispersión geográfica?), `label`,
`message`, `info`, `publishable`, `case`. [VERIFICADO API]

**Parámetros de entrada (recurso `valorization`):** `version` (id del Référentiel), `mileage`,
`released-at` (1ª matriculación), `calculated-for` (fecha de cálculo → cote a fecha pasada / stock),
`geolocalisation` (código INSEE/CP → cote regionalizada), `makes` (región), `business-target` (`btoc`/`btob`),
`offer`, `features` (ids de equipamiento). Variantes de `offer`: `extended-market-values`,
`market-value`, `past-stock-market-value` (cote de stock a fecha pasada), cote personnalisée, y
**frais professionnels** en modo `percent` o `fixed`. [VERIFICADO API]

> Reglas de elegibilidad (errores 422 documentados): no se cotiza si vehículo **no particular**, de
> **prestige**, **km < 10**, **km > 300 000**, **mise en circulation < 6 meses** o **> 10 años**. La
> Valeur Transaction® está disponible para VO de **6 a 12 meses** (novedad). [VERIFICADO]

### 3.3 Identification par l'immatriculation (matrícula → carte grise + vehículo) — v3.0 y v3.1

`POST /checkout/3.x/matchings` con la matrícula (7 caracteres) → devuelve la **carte grise** y una lista de
**candidates** (versiones probables) ordenadas por popularidad. [VERIFICADO]

**Campos `registration-card` (carte grise):** `vin-code` (VIN), `cnit-code` (CNIT — solo v3.1),
`tvv-code` (Type-Variante-Version — solo v3.1), `color`, `first-registration-date`, `registration-date`,
`fiscal-power` (puissance fiscale), `carbon-emission` (CO2 g/km).
**Campos `candidates`:** `version-id`, `suggested` (bool, mejor match), `quote-ratio` (indicador de
popularidad/probabilidad). **Campo `matching`:** `registration`, `offer` (`identification-by-registration`).
[VERIFICADO API]

### 3.4 Valeur Résiduelle Argus® / Prevar® (valores residuales a futuro) — *segmento Valuation/Solution*

Anticipa la **decote** futura (VR a término) para fijar engagement de reprise y mensualidades en **LOA**
(Location avec Option d'Achat) y **LLD** (Location Longue Durée), VN o VO. Cliente: financeurs,
distributeurs, constructeurs, loueurs, garantisseurs. Herramienta web **Prevar®** ("outil de référence
depuis 1998") + API `POST /api/public/v1/residual-value` (+ `/sandbox`). [VERIFICADO]

**Parámetros de entrada:** `vehicle_id` (obl.), `release_at` (1ª matriculación, obl.), `return_at` (fecha
de retorno, obl., dentro de `simulation_parameters`), `contract_mileage` (km máx. del contrato),
`mileage` (km al inicio), `initial_price` (prix du neuf override), `feature_ids`, `simulate_at` (fecha de
simulación; fecha pasada ⇒ búsqueda en Archive, solo VN), `customization_amount` (±€ sobre la VR),
`customization_percent` (% de la VR). Hasta **400 pares km/fecha** por petición; límite **6 250 km/mes**.
**Salida:** `manufacturer_price`, y por escenario: `value` (VR €), `ratio` (VR % = valor/prix neuf),
`custom_value`, `custom_ratio`, `return_at`, `contract_mileage`. [VERIFICADO API]

**Prevar® (web) — campos/funciones extra:** `Indice` (índice de décote Argus) + **historique des indices
de décote**, `Tarif TTC`, `Impact Options`, `Série`, `Profils` (perfiles personalizables/paramétricos),
`Durée` (meses), `Km`, `Date livraison`, `Date retour`, `VN/Arch` (nuevo/archivo), `Statut`. Funciones:
**matrice globale** (nube de resultados durée×km), **matrice personnalisée**, comparación simultánea de
**hasta 3 vehículos**, lista de **vehículos equivalentes**, gestión de **parc**, import desde **Excel**,
export Excel, suivi de consumo, comptes-fils (subcuentas). [VERIFICADO datasheet Prevar 3]

**Kilometrajes estándar usados en la VR (VP):** Essence **15 000**, Diesel/Hybride **25 000**,
Electrique **12 500**, Gaz/Hydrogène **20 000** km/año (+ tablas específicas VUL y 2-roues). [VERIFICADO API]

### 3.5 Otros activos del grupo (mención, fuera de núcleo de datos)

- **VRADE** (Valeur de Remplacement À Dire d'Expert): valor de referencia para **peritaje de seguros**
  (siniestros). Producto/término citado en foros y servicios Argus. [ASUMIDO parcial — término verificado en largus.fr/forum, alcance exacto NO auditado al átomo]
- **Software de gestión VO** (segmento *Solution*): **Prevar®**, y citados por Wikipedia **Planet VO** y
  **Cardiff VO**. ⚠ *Planet VO* es producto de marca **autobiz** (empresa distinta); la relación de
  propiedad NO está verificada — no atribuir a L'argus sin confirmar. [NO-VERIFICADO la propiedad]
- **Le Bon Observatoire du VO** (observatorio de stocks/mercado VO) — leboncoin/Argus. [ASUMIDO]
- Editorial/medios: revista (bimestral desde 2015), largus.fr (essais, nouveautés, actus, guide d'achat,
  annonces, forum), app móvil. [VERIFICADO]

---

## 4. Metodología / fuentes de datos

[VERIFICADO datasheet Cote + descripciones API]
- **Référentiel:** alimentado a diario por un equipo de analistas de datos de automoción (>10 años);
  combina tarifas constructor (técnica + equip. de serie), opciones con sus liens logiques, y
  reconocimiento por CNIT/Type Mine.
- **Cote Argus® (custom-market-values):** valor de referencia "à dire d'expert", editado desde 1927.
- **Valeur Argus Annonces® (displayed-selling-values):** explotación estadística de **~250 000 stocks
  semanales** (histórico >5 M de anuncios distintos desde 2009) — últimos precios que dispararon venta.
- **Valeur Argus Transaction® (btob/btoc):** observatorio de **valeurs de revente efectivas** —
  **1 500 000 transacciones/año** (histórico 14 M desde 2000).
- **Demanda:** **+12 000 000 demandas de Cote/año** desde 2004 (señal de popularidad → `position`,
  `quote-ratio`).
- Proceso: **flux de données anonymisées → traitement statistique**. Reservado a clientes pro (las de
  mercado); la Cote de referencia es pública.
- VR/Prevar: curva de decote por combinación vehículo + perfil + par durée/km, con índices históricos.

---

## 5. Entrega (delivery)

[VERIFICADO]
- **API REST** (JSON:API) — la entrega estrella. Auth **OAuth 2.0** (token 120 min). 3 modos: particular
  sin cuenta cote, profesional con cuenta cote (`grant_type=password`), profesional sin cuenta cote.
  Acceso solo bajo **contrato anual** (cuenta de test mediante comercial). Valores en **modo asíncrono**
  (POST → websocket `data.url` o polling 250 ms → GET). Soporta **batch** (`batches`, máx. 10 vehículos).
  Endpoints: `/specs/2.0/*` (Référentiel), `/checkout/3.0/valorizations` (Valeurs),
  `/checkout/3.1/matchings` (immatriculation), `/api/public/v1/residual-value` (VR). Doc Postman pública.
- **Portal web pro** (pro.largus.fr / prolargus.leboncoin.auto): consulta de cote + valeurs + Prevar.
- **Web pública** (largus.fr/cote): Cote Argus Personnalisée para grand public.
- **Software/outils en línea:** Prevar® (gestión de VR), SONAR (comparables).
- **Excel:** import/export de parc y resultados en Prevar.
- **Integración DMS / app propietaria:** la API está pensada para integrarse "directamente en su software
  o aplicación propietaria" (infomédiaires, concesionarios, portales).
- **Migración:** existe un *webservice* Prevar legacy migrado a la API (params armonizados a inglés).

---

## 6. Modelo de precio

[ASUMIDO / parcialmente verificado] No hay tarifa pública. Verificado: el acceso a API exige **suscripción
a contrato anual** y el alta la gestiona el servicio comercial; las **valeurs de marché** están reservadas
a **clientes profesionales Argus** (de pago), mientras la **Cote de referencia** es accesible al gran
público (gratuita en largus.fr, con upsells). La cuenta "cote" pro (username/password) implica un contrato
de cotación. Modelo: **suscripción B2B + por consulta/cotación** (no se descubre la cifra). [NO-VERIFICADO el importe]

---

## 7. Placement (DÓNDE coloca cada dato — patrón para cardeep)

> Este es el patrón que cardeep imita para ubicar cada métrica. Derivado del datasheet "Cote Argus &
> Valeurs Argus de marché" (layout pro real) + la web largus.fr/cote (grand public) + la doc API.

**A) Dashboard de valoración pro — fila de 5 valores anclada al ciclo de vida (patrón maestro).**
El datasheet muestra una **barra horizontal de 5 tarjetas-valor** siempre visible, mapeada a la fase del
ciclo VO. De izquierda a derecha:

| Posición | Tarjeta (dato) | Fase del ciclo | Ej. |
|---|---|---|---|
| 1 | **Cote Argus Personnalisée®** | Reprise | 9 882 € |
| 2 | **Valeur Argus Annonces®** (+ Marge de Manœuvre) | Annonce | 12 212 € |
| 3 | **Valeur Argus Transactions®** | Vente | 10 543 € |
| 4 | **Prix du neuf** | Gestion | 19 900 € |
| 5 | **Délai Argus Rotation®** | Gestion | 36 jours |

Cada tarjeta lleva un botón/acceso **SONAR** para abrir los comparables. → *cardeep: cabecera de la ficha
de coche = fila de tarjetas-valor por fase (tasar → publicar → vender → gestionar), no una sola cifra.*

**B) Ficha de coche / identificación (web + API).** Entrada por **(a)** selección
marque→modèle→motorisation→finition + **date de mise en circulation** + **kilométrage** + **options**, o
**(b) matrícula** o **(c) carte grise** (CNIT). El bloque de identificación muestra specs del Référentiel
(prix du neuf, técnica, equip. serie/opción). Las **candidates** (versiones probables) se listan ordenadas
por popularidad con la "suggested" arriba. → *cardeep: ficha = identificación por matrícula/VIN + specs +
acceso a las valoraciones.*

**C) Detalle de un valor (panel de confianza).** Junto al importe, la API entrega `confidence-index`,
`confidence-intervals` (min/max), `dispersion`, `leeway` (Marge de Manœuvre) e `influence` (desglose del
efecto de km/options/release/region). → *cardeep: cada precio mostrado con su intervalo de confianza,
dispersión y "palancas" que lo mueven; jamás una cifra desnuda.*

**D) Comparables (SONAR).** Pantalla paramétrable con anuncios (Annonces) o transacciones anonimizadas
(Transactions) de vehículos similares por zona de chalandise o toda Francia. → *cardeep: vista "mercado
similar" filtrable por radio geográfico.*

**E) Matriz de valor residual (Prevar).** Tabla **durée (meses) × kilométrage** con la VR en € en cada
celda (matrice globale = nube; matrice personnalisée = pares elegidos), comparación de hasta 3 vehículos
lado a lado, e índice de decote con su histórico. → *cardeep: panel de proyección = grid durée×km + curva
de depreciación + comparador.*

**F) Ajuste regional / geográfico.** `geolocalisation` de entrada y `region-plus`/`region-minus` +
`has-map` de salida → mapa de dispersión geográfica del valor. → *cardeep: toggle "ajustar a mi zona".*

---

## 8. Diferencial (lo que ofrece y otras no)

- **Autoridad/cobertura del mercado FR:** ~90% de cuota y estatus de "valor-pivot" legal/regulado desde
  1927; reconocida por professions réglementées (peso institucional difícil de replicar). [VERIFICADO]
- **Triple capa de valor coherente:** valor à dire d'expert (Cote) + valor de anuncio (Annonces) + valor
  de transacción real (Transaction B2B y B2C) — separados y etiquetados, no un único "market value". [VERIFICADO]
- **`influence` desglosado:** la API devuelve cuánto pesa cada factor (carrocería, km, opciones, frais
  profesionales, antigüedad) sobre el valor — explicabilidad poco común. [VERIFICADO]
- **`confidence-index` + `confidence-intervals` + `dispersion`** por valor: incertidumbre cuantificada. [VERIFICADO]
- **Délai Argus Rotation®** (days-to-sell como mediana real de detención) integrado con el valor. [VERIFICADO]
- **Identificación por matrícula con CNIT/TVV** (v3.1) + lista de candidates con probabilidad. [VERIFICADO]
- **VR con personalización fina** (customization_amount/percent, 400 escenarios, perfiles, LOA/LLD). [VERIFICADO]
- **Référentiel hasta 268 datos/vehículo** incluyendo liens logiques de opciones y frecuencia de finición
  en el parc real. [VERIFICADO]
- **SONAR**: comparables reales (anuncios y transacciones anonimizadas) embebidos. [VERIFICADO]

---

## 9. Gaps (lo que NO ofrece / límites)

- **Solo Francia** — sin cobertura paneuropea propia (contrastar con JATO/Autovista/Indicata). [VERIFICADO]
- **Sin historial de vehículo profundo:** no expone historial de siniestros, nº de propietarios,
  mantenimiento ni verificación de km (entrega CO2/fiscal/VIN de la carte grise, pero no un vehicle-history
  tipo Carfax/Histovec). [VERIFICADO por ausencia en API]
- **Sin telemática / datos de uso en tiempo real.** [VERIFICADO por ausencia]
- **No cotiza nichos:** vehículos no particulares, de prestige, km<10 o >300 000, <6 meses o >10 años. [VERIFICADO]
- **Sin precios de subasta/wholesale ni arbitraje cross-platform** explícitos en la API (Transaction es
  retail B2B/B2C, no precio de remate). [VERIFICADO por ausencia]
- **Sin market-days-supply / price-to-market %** como tales: ofrece Délai Rotation (días) y dispersión,
  pero no un índice oferta/demanda ni un % price-to-market estandarizado. [VERIFICADO por ausencia]
- **VR limitada a VP/VUL** con tope 6 250 km/mes; archive solo para VN. [VERIFICADO]
- **Acceso de pago y bajo contrato anual:** sin self-service ni tarifa pública. [VERIFICADO]
- **Precio:** importe no descubrible públicamente. [NO-VERIFICADO]

---

## 10. Fuentes (URLs)

- API Argus (colección Postman en vivo, fuente primaria de campos): `https://developer.leboncoin.auto`
  (ex `https://developer.largus.fr`) · datos JSON: `https://documenter.gw.postman.com/api/collections/12365936/2sB3HgRPsT` · host API `https://api.leboncoin.auto`. [VERIFICADO en vivo]
- Datasheet "Cote Argus & Valeurs Argus de marché" (PDF): `https://pro.largus.fr/pro/static/pdf/produits/Cote_Argus_et_Valeurs_Argus_de_marche.pdf` (ed. 04/2016). [VERIFICADO]
- Datasheet "Référentiel Argus" (PDF): `https://pro.largus.fr/pro/static/pdf/produits/Referentiel_Argus.pdf` (ed. 06/2014). [VERIFICADO]
- Datasheet "Prevar 3" (PDF): `https://pro.largus.fr/pro/static/pdf/produits/Prevar_3.pdf` (ed. 10/2015) · landing `https://prevar3.largus.fr/`. [VERIFICADO]
- Web pública Cote: `https://www.largus.fr/cote/` y `https://www.largus.fr/cote/carte-grise/`. [VERIFICADO]
- Portal pro: `https://pro.largus.fr/cote/` (403 anti-bot; contenido vía datasheets + API). [VERIFICADO acceso]
- Identidad/owner: `https://en.wikipedia.org/wiki/L'Argus` + Adevinta press release "leboncoin Group finalises the acquisition of Argus Group" `https://adevinta.com/press-releases/adevintas-leboncoin-group-finalises-the-acquisition-of-argus-group-2/`. [VERIFICADO ≥2 fuentes]
- RCS editor SNEEP 572 214 591 (impreso en los 3 datasheets). [VERIFICADO]
- Référentiel/CNIT (corroboración): `https://www.cardiff.fr/fonctionnalites/referentiel-argus.php`. [VERIFICADO]

---

### Anexo — recuento de campos por producto
- **Référentiel Argus®:** ~140 campos atómicos (8 niveles de taxonomía + 18 grupos de specs).
- **Cote/Valeurs Argus®:** ~30 (7 valores comerciales + objeto `values` de 20+ + params).
- **Identification immatriculation:** ~12.
- **Valeur Résiduelle/Prevar®:** ~25.
