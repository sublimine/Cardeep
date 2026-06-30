# AutoScout24 — Auditoría atómica

> **slug:** `autoscout24` · **subdominio de audit:** `portal-insights` · **web:** https://www.autoscout24.de/ · **company:** https://www.autoscout24.com/company/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[VERIFICADO]` lo leído (≥2 fuentes donde se indica), `[NO-VERIFICADO]` lo no confirmado; nada inventado.
> **Veredicto express:** AutoScout24 es **el mayor marketplace de coche paneuropeo** (>30M usuarios/mes, >2M anuncios vivos, >45.000 dealers, 19 países + Canadá),
> propiedad de **Hellman & Friedman** desde 2020. Su negocio de **datos/inteligencia** NO es una guía de tasación clásica (Schwacke/Eurotax) ni un censo independiente
> (AutoUncle): es **inteligencia derivada de su propio inventario vivo**, empaquetada en tres capas. (1) **Preisbewertung** — un rating de precio de **5 niveles**
> (`Sehr guter Preis`→`Hoher Preis`) calculado por ML sobre **>10M datasets + >70 features de equipamiento** comparando los **últimos 14 meses**, visible como **badge en cada
> anuncio** (comprador) y en el panel del dealer. (2) **HändlerIQ** — set de **5 funciones IA por vehículo** (Preisbewertung, Inseratsqualität, Ausstattungsanalyse,
> **Standzeitprognose** = pronóstico de días-a-venta, **Wettbewerbsanalyse** = análisis competitivo regional), agrupadas en un **Händler-Dashboard** (oct-2025) con KPIs de
> performance (Standtage, Anfragen, Merkzettel, Suchaufrufe). (3) **Data licensing** — sus **estadísticas de vehículo + funciones HändlerIQ** se inyectan vía **API/DMS** en los
> **10 mayores proveedores de datos** (6 ya con HändlerIQ), llevando el dato al sistema donde el dealer trabaja a diario. Encima publica **inteligencia de mercado abierta**
> (MarktReport trimestral, Jahresanalyse, **Golf-Index**) = el ángulo "insights". Patrón directo a copiar para cardeep: **rating de precio semáforo en cada tarjeta + pronóstico de
> standzeit + análisis competitivo regional con distribución de km/edad/precio + recomendación accionable por coche, todo embebido tanto en portal propio como en el DMS del dealer**.

> **Aviso de desambiguación (CRÍTICO):**
> - **AutoScout24 GmbH** (Múnich, owner **Hellman & Friedman**) = el sujeto de este informe: pan-Europa (.de/.com/.it/.nl/.be/.fr/.at…) + Canadá (vía TRADER). [VERIFICADO]
> - **autoscout24.ch** (Suiza) lo opera **Swiss Marketplace Group (SMG)** — **owner DISTINTO** (TX Group/Ringier/General Atlantic). Sus páginas `b2b.autoscout24.ch` (abos, premium-pakete) y
>   el repo GitHub `smg-automotive/autoscout24-api-specs` pertenecen a SMG, **no** a H&F. Marco como SMG lo que venga de ahí. [VERIFICADO ≥2: b2b.autoscout24.ch, github smg-automotive]
> - **mobile.de** = competidor #1 en Alemania, propiedad de **Adevinta** — **empresa separada**, no confundir con AutoScout24. [VERIFICADO: conocimiento de sector]
> - **Nota de método:** las páginas de producto `autoscout24.de/haendlerportal/*` y las corporate-meldungen son accesibles y son fuente primaria. Las APIs (Swagger) y los PDF de MarktReport
>   se renderizan por JS/binario y no se leyeron verbatim; sus campos se reconstruyeron de las páginas HTML de producto y del press release en texto (presseportal).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre legal/comercial | **AutoScout24 GmbH** | [VERIFICADO ≥2: company portrait, corporate-meldungen] |
| Nombre fundacional | **MasterCar AG** (rebautizada AutoScout24) | [VERIFICADO: company portrait] |
| Grupo / owner | **Hellman & Friedman LLC** (PE americana, SF) — adquirió AutoScout24 a **Scout24 AG** por **€2.900M** (anunciado dic-2019, cerrado 2020) | [VERIFICADO ≥2: hf.com, Unquote, Mergr] |
| Fundación | **1998, en Múnich** | [VERIFICADO ≥2: company portrait, Crunchbase] |
| HQ | **Múnich** (Grünwald / "Campus München"), Alemania | [VERIFICADO ≥2: company page, search H&F] |
| Empleados | **~2.000** ("rund 2.000 Mitarbeitenden") | [VERIFICADO ≥2: zahlen, company portrait] |
| Usuarios | **>30M usuarios/mes** | [VERIFICADO ≥2: zahlen, portrait] |
| Anuncios | **>2M Fahrzeuginserate** (vivos) | [VERIFICADO ≥2: zahlen, portrait] |
| Dealers partner | **>45.000** (también citado "43.000" en notas anteriores) | [VERIFICADO ≥2: zahlen, corporate-meldungen] · ligera divergencia 43k↔45k por fecha |
| Países | **19 países** total; **11 core markets** nombrados + Canadá | [VERIFICADO ≥2: zahlen, portrait] |
| Posicionamiento | "**largest pan-European and Canadian online car market**" / "europaweit größter Online-Automarkt" | [VERIFICADO ≥2: portrait, corporate-meldungen] |
| Ingresos | **No divulgado** públicamente (PE, sin estados auditados abiertos) | [NO-VERIFICADO — ausente] |
| CCO citado | **Felix Frank** (Chief Commercial Officer) | [VERIFICADO: autohaus.de, corporate-meldung dashboard] |

### Adquisiciones / cartera (clave para entender su músculo de datos+software)
| Activo | Año | Qué es | Estado |
|---|---|---|---|
| **LeasingMarkt.de** | **2020** | Portal de leasing/financiación (DE) — integrado como "family benefit" (20% dto. en requests) | [VERIFICADO ≥2: zahlen, service-pakete] |
| **AUTOproff** (mayoría) | **2022** (anunciado mar-2022) | Plataforma **B2B de subastas/wholesale** de coche usado (líder en Dinamarca, **120.000+ vehículos subastados en 2021**); aporta sourcing+remarketing al dealer | [VERIFICADO ≥2: autoscout24.com press, AIM Group, autovista24] |
| **TRADER Corporation** (Canadá) | **cerrado 11-dic-2024** (anunciado 16-ago-2024; comprado a **Thoma Bravo**) | Líder canadiense de **media + software de dealer/OEM + lender services**: **AutoTrader.ca + AutoHebdo.net** (26M visitas/mes, 450k+ anuncios, 5.000+ dealers), **AutoSync** (software dealer/OEM, 2.500+ subs), **Dealertrack** (financiación automotriz), **Collateral Management Solutions** (lien/recovery). Fundada 1975, Toronto | [VERIFICADO ≥2: Thoma Bravo press, themiddlemarket, autoremarketing] |

### Clientes objetivo (segmentos)
- **B2C:** compradores/vendedores particulares (>30M/mes) + tasación gratuita + Smyle (retail online).
- **B2B dealer:** **45.000+ concesionarios** (independientes y de marca) — el corazón del negocio de datos (HändlerIQ, packages, dashboard).
- **B2B wholesale:** dealers que compran/venden en subasta (AUTOproff).
- **Proveedores de datos / DMS:** **10 mayores data service providers** que integran las estadísticas+HändlerIQ de AutoScout24 en sus sistemas. [VERIFICADO: corporate-meldung Datendienstleister]
- **Prensa / mercado / OEM-analistas:** consumidores de la inteligencia abierta (MarktReport, Golf-Index, Spotlight).

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| **Core markets (11)** | **Alemania, Bélgica, Luxemburgo, Países Bajos, Italia, Francia, Austria, Noruega, Dinamarca, Polonia, Suecia** | [VERIFICADO ≥2: zahlen, portrait] |
| **Total países** | **19** ("Operations in 19 countries") + **Canadá** (vía TRADER) | [VERIFICADO ≥2: zahlen, portrait] |
| Países legacy citados | Bulgaria, Chequia, Croacia, Rumanía, Turquía, Ucrania, Hungría, España, Rusia aparecen en páginas/career históricas; **España NO figura como core market actual** | [VERIFICADO: company career page] · [NO-VERIFICADO el estatus operativo actual de cada uno] |
| Volumen de anuncios | **>2M Fahrzeuginserate** vivos (grupo) | [VERIFICADO ≥2: zahlen, portrait] |
| Base de cálculo de precio | **>10M datasets** alimentan el algoritmo de Marktpreis/Preisbewertung | [VERIFICADO ≥2: preislabels, fahrzeugbewertung, price-label-page] |
| Frescura | Precio en **tiempo real** desde la base de datos alemana; ventana de comparación **últimos 14 meses** | [VERIFICADO ≥2: fahrzeugbewertung, preislabels] |
| Scope nuevo/usado | **Usado = núcleo** del dato de precio; **nuevo** presente en marketplace; **Jahreswagen/Vorführwagen** como Fahrzeugart | [VERIFICADO ≥2: portrait, preislabels] |
| Tipos de vehículo | **Coches usados + nuevos, motos (Motorräder), vehículos de camping (Wohnmobile), vehículos comerciales (Nutzfahrzeuge)** | [VERIFICADO ≥2: portrait, company page] |
| Marcas | Todas (agnóstico — agrega el inventario de 45k dealers) | [VERIFICADO: naturaleza marketplace] |
| Cobertura del dato de mercado abierto | Comparativas paneuropeas en MarktReport/Jahresanalyse: **DE, BE, IT, AT, NL** (y Golf-Index en **5 naciones europeas**) | [VERIFICADO ≥2: mediacenter/daten, MarktReport] |

---

## 3. Productos + campos atómicos

> AutoScout24 expone **un motor de dato propietario** (precio de mercado + IA sobre su inventario vivo) a través de superficies B2C, B2B-dealer (HändlerIQ/Dashboard/packages),
> data-licensing (DMS) e inteligencia abierta. Los campos atómicos se reconstruyeron de las páginas de producto del **Händlerportal**, las **corporate-meldungen**, la página de
> **Fahrzeugbewertung**, la página de explicación de **Preisbewertung** y el **MarktReport Q3/2025**.

### 3.0 Preisbewertung — el rating de precio (la métrica-firma)
Compara el **Angebotspreis** (precio del anuncio) contra un **Marktpreis** calculado y devuelve un **price label** semáforo. [VERIFICADO ≥2: preislabels, price-label-page, search]
- **5 niveles (DE actual):** **`Sehr guter Preis`** · **`Guter Preis`** · **`Fairer Preis`** · **`Erhöhter Preis`** · **`Hoher Preis`**. Sin datos suficientes → **`KEINE ANGABE`**.
  - ⚠ Variante de 3 escalones positivos (**`Top Angebot`/`Gutes Angebot`/`Faires Angebot`**) observada en la página de explicación `.com` — posible rendering internacional/legado o subconjunto. [VERIFICADO la existencia de ambas; razón de divergencia NO-VERIFICADA]
- **Base de cálculo:** "intelligenter Algorithmus" / **Machine-Learning** sobre **>10M datasets** + **>70 features de equipamiento por vehículo** + "expert automotive knowledge".
- **Ventana:** vehículos disponibles en los **últimos 14 meses hasta hoy**.
- **Comparables:** mismo/similar modelo y equipamiento; **distingue dealer vs particular** (permite al dealer precio algo mayor).
- **Exclusiones del comparable:** precios atípicos (deutlich zu hoch/niedrig), **vehículos de accidente**, modificaciones a medida, **sellos/certificaciones**.
- **Caveat:** no considera el estado individual del coche (asume buen estado sin defectos mayores).

### 3.1 Objeto vehículo / anuncio — campos atómicos fuente
Atributos por vehículo que entran en el comparable (criterios de Preisbewertung) + inputs de Fahrzeugbewertung [VERIFICADO ≥2: preislabels, fahrzeugbewertung]:
- **Identidad:** `Marke` (make), `Modell` (model), `Version`/`Ausstattungslinie` (trim/línea de equipamiento).
- **Antigüedad/uso:** `Erstzulassung` (1ª matriculación, mes+año), `Kilometerstand` (km).
- **Mecánica:** `Kraftstoff`/`Kraftstoffart` (combustible), `Getriebe` (transmisión), `Leistung` (potencia, PS/kW), `Karosserieform` (carrocería), `Türen` (puertas), `Fahrzeugart` (nuevo/usado/Jahreswagen/Vorführwagen).
- **Medioambiente:** `Schadstoffklasse` (clase de emisiones), `Emissionsstandard` (norma, p.ej. Euro 6), `Kraftstoffverbrauch kombiniert` (consumo combinado), `CO2-Emissionen`.
- **Estado/legal:** `HU/AU` (fecha ITV/TÜV), `Gebrauchtwagengarantie` (garantía VO, flag), `Unfallfahrzeug` (flag accidente — excluye del comparable), `Siegel`/`Zertifizierung` (sello — excluido del comparable), `Fahrzeugzustand` (asumido bueno).
- **Comercial:** `Angebotspreis` (precio), `Verkäufertyp` (dealer/particular), `Standort`/`PLZ` (ubicación/CP), `Farbe` (color), `Bilder` (imágenes).
- **Equipamiento:** **70+ `Ausstattungsmerkmale`** (features de equipamiento).

### 3.2 Fahrzeugbewertung — tasación B2C gratuita
Tool de tasación gratis (sin VIN ni matrícula). [VERIFICADO: fahrzeugbewertung]
- **Inputs:** Marke, Modell, Erstzulassung (año+mes), Karosserieform, Kraftstoff, Getriebe, Leistung, Ausstattungslinie, Kilometerstand, **Email** (para recibir resultado).
- **Outputs (campos atómicos):** **`Preisempfehlung`** (precio recomendado para anunciar), **`Marktwert`** (valor de mercado actual), **`Preisspanne` con `Verhandlungsspielraum`** (rango con margen de negociación).
- **Método:** ML sobre comparables; **comparación contra >10M anuncios** de AutoScout24 DE; **"99% de los Angebotspreise"** incluidos (solo se excluyen outliers irreales); precio en tiempo real.
- **Caveat:** es media de **precio de anuncio**, NO precio de venta garantizado.

### 3.3 HändlerIQ — set de IA por vehículo (núcleo del negocio de datos B2B)
"Intelligentes Tool-Set" sobre los datos del mayor automarket europeo + IA; da **insights + Handlungsempfehlungen individuales por cada vehículo**. **5 funciones** [VERIFICADO ≥2: corporate-meldung Wettbewerbsanalyse, autohaus, mobilitree]:
1. **Preisbewertung** — competitividad del precio (ver 3.0): `Marktpreis`, `Preisbewertung-Label`, `Preisdifferenz vs Markt`.
2. **Inseratsqualität** (listing quality) — detecta debilidades de presentación del anuncio (datos incompletos, fotos, descripción) → `Inseratsqualität-Bewertung` + sugerencias.
3. **Ausstattungsanalyse** (equipment analysis) — compara el equipamiento del coche vs comparables; detecta **features que justifican sobreprecio** y **gaps que exigen rebaja** → `fehlende Ausstattung` + impacto en precio.
4. **Standzeitprognose** (standing-time forecast) — **pronostica los días hasta la venta** del vehículo → `Standzeitprognose` (días estimados); ayuda a vender Langsteher (long-standers).
5. **Wettbewerbsanalyse** (competitive analysis) — ver 3.4.
- **IA + acción:** "fortschrittliche AutoScout24 KI" detecta competidores y emite **`Handlungsempfehlungen`** (recomendaciones de optimización de precio/listing).
- **Claim de impacto:** ajustes de precio en los **primeros 60 días** pueden reducir la Standzeit **hasta en dos tercios**. [VERIFICADO: wettbewerbsanalyse page]

### 3.4 HändlerIQ Wettbewerbsanalyse — análisis competitivo regional (campos atómicos)
Inteligencia del entorno competitivo regional de vehículos comparables. [VERIFICADO ≥2: haendlerportal/wettbewerbsanalyse, corporate-meldung]
- **Preisvergleich:** `Konkurrenzpreise` (precios competencia), `Preisänderungen Wettbewerber` (cambios de precio rivales), `Preisspanne im Markt` (rango), **`Preis-Ranking-Position`** del propio vehículo.
- **Lista de vehículos rivales (por fila):** `Preis`, `Baujahr/Erstzulassung`, `Kilometerstand`, **`Standtage`** (días en mercado del rival), `Preisentwicklung` (evolución).
- **Distribución de mercado (diagramas):** **`Verteilung Laufleistung`** (km), **`Verteilung Erstzulassung`** (edad), **`Verteilung Preise`** (precio).
- **Ausstattungsvergleich:** equipamiento propio vs competencia (feature-by-feature).
- **Parámetros de mercado:** `Anzahl konkurrierender Fahrzeuge` (nº rivales), `Geografischer Umkreis/Region` (radio geográfico), **`Neue Wettbewerber-Fahrzeuge`** (nuevos entrantes en vivo), `Marketing-Intensität` de los anuncios rivales (qué productos de visibilidad han comprado), `Nachfrage-Metriken` (demanda comparada), `Sichtbarkeit` (visibilidad del inserto).
- **Disponibilidad:** fase de test gratuita para todos los partners en su Händlerbereich.

### 3.5 Händler-Dashboard — la consola (lanzado 07-oct-2025)
Sustituye el antiguo "Online-Händlerbereich"; **gratis para todos los partners**. Reúne todo en una **Home**. [VERIFICADO ≥2: corporate-meldung dashboard, autohaus, kfz-betrieb]
- **HändlerIQ integrado:** las 5 funciones IA en el Home, con **Schnellaktionen** (one-click) para corregir.
- **Performance-Kennzahlen (KPIs):** **`Standtage`** (días en mercado propios), **`Anfragen`/Leads**, **`Merkzetteleinträge`** (entradas en lista de deseos), **`Suchaufrufe`/`Suchanfragen`** (impresiones en búsqueda), `Aufrufe` (vistas).
- **Bewertungsmanagement:** nuevas **`Händlerbewertungen`** (reseñas) + tareas abiertas en la Home; **`Weiterempfehlungsrate`** (tasa de recomendación) para reputación de marca.

### 3.6 Service-Packages GO / SMART / PRO (desde 01-oct-2024)
Estructura de tarifa por paquetes (estilo mobile.de). [VERIFICADO ≥2: service-pakete, automobilwoche]
| Paquete | Sichtbarkeit | Incluye | 
|---|---|---|
| **GO** | estándar (orgánica) | KI-Tools clave: Lead+, Inseratsqualität, Preisbewertung, Ausstattungsanalyse, Wettbewerbsanalyse |
| **SMART** | **+100%** | todo GO + **Personalisierte Detailseite** + premium service |
| **PRO** | **+250%** | todo SMART + **HändlerHighlight** + **Eigene Fahrzeugempfehlungen** + **Logo en resultados con enlace al stock** |
- **Extras bookables:** **Nachfrage-KI powered by SalesTurbo** (visibilidad), **#SocialBoost** (Instagram/Facebook/Google Vehicle Ads; dto. 10% SMART/20% PRO), **AutoMatch** (prioridad de matching por tier), **NEU markieren** (contingente gratis 10/20/50% por tier), **SelectBoost** (booster exclusivo de sistemas de proveedores de datos), SuperDEAL, Exklusivangebot, Platzhirsch, Marketing-Power, FinanceBoost.
- **Family benefits:** **20% dto. LeasingMarkt.de** + **25% dto. AUTOproff Premium/Professional**.

### 3.7 Data licensing — estadísticas+IA en el DMS del dealer
"Integrar estadísticas de vehículo, funciones IA y productos de performance directamente en los sistemas de los proveedores de datos". [VERIFICADO ≥2: corporate-meldung Datendienstleister, autrado]
- **Alcance:** **los 10 mayores proveedores de datos** han integrado las **Fahrzeugstatistik-Daten** de AutoScout24; **6 de 10** ya soportan **funciones HändlerIQ**; más en preparación.
- **Datos integrados (vía API/DMS):** `Aufrufe` (vistas), `Leads`, `Standtage` + "weitere Datenpunkte zur Performance der eigenen Inserate"; **HändlerIQ** completo (Inseratsqualität, Preisbewertung, Ausstattungsanalyse, Standzeitprognose, Wettbewerbsanalyse) + **Handlungsempfehlungen por vehículo**; **SelectBoost** (exclusivo de estos sistemas).
- **Meta:** decisiones data-driven "donde el dealer trabaja a diario" (su propio Fahrzeugmanagementsystem/DMS).

### 3.8 Listing Creation API (oficial)
API REST oficial **write-only**, solo para dealers registrados. [VERIFICADO ≥2: api docs URL, scrapfly, github smg]
- **Capacidad:** crear/actualizar/publicar/eliminar anuncios + subir imágenes; **acceso de lectura a taxonomía** (make/model y otra info taxonómica de clasificación).
- **NO ofrece** endpoint público de **search/browse** de datos de vehículos (no hay API pública de consulta de mercado). [VERIFICADO ≥2: scrapfly, auto-api]
- ⚠ Una página de hub lista "SEARCH API / structured vehicle data access" — **NO-VERIFICADO** como API pública de consulta (probable acceso a taxonomía o producto B2B restringido; el contrato oficial es write-only).

### 3.9 AUTOproff — wholesale/subastas B2B (producto de cartera)
Plataforma digital B2B de compra-venta de coche usado entre dealers vía **subastas online**; líder en DK; **120k+ vehículos subastados en 2021**. Aporta al dealer de AutoScout24 **nuevas fuentes de inventario** y eficiencia de trade-in/wholesale. [VERIFICADO ≥2: autoscout24.com press, AIM Group]

### 3.10 Smyle — retail de coche usado online (B2C)
Compra de VO 100% online con entrega a domicilio en Alemania. [VERIFICADO ≥2: smyle page, corporate-meldung]
- **Criterios de calidad:** **≤6 años** y **≤100.000 km**; inspección experta; **mín. 6 meses de TÜV** a la venta; verificación técnica pre-entrega.
- **Estándares de desgaste (atómicos):** carrocería (arañazos ≤3cm, abolladuras ≤2cm diámetro, máx 4 daños de pintura pequeños), cristal (sin impactos en campo de visión del conductor; chips >3mm excluidos), interior, neumáticos (banda **≥3mm**).
- **Entrega:** nacional, **desde €599** (según CP), **~4–6 semanas**, matrícula propia, varianza de km hasta **1.000 km** por transporte.
- **Financiación:** partner **Openbank (ex-Santander)** — crédito clásico o cuota balloon, entrada flexible (incl. 0).
- **Garantía:** **12 meses** (Allianz; cubre mecánica/electrónica, excluye carrocería/chasis/cristal/embrague/pastillas). **Smyle Care:** seguro provisional (AXA) Haftpflicht+Vollkasko hasta 1 mes (franquicia €150/€500).
- **Devolución:** **21 días** money-back; recogida gratis; hasta 100 km libres, exceso a €1,00/km +IVA.
- **Datos por coche:** precio fijo (no negociable), edad, km, consumo/CO2, filtro "Online kaufen & Lieferung", fecha última TÜV.

### 3.11 Inteligencia de mercado abierta (el ángulo "insights" / portal-insights)
Publicaciones de mercado sobre su propio dato. [VERIFICADO ≥2: mediacenter/daten, MarktReport Q3/2025, presseportal]
- **MarktReport (trimestral, DE):** estado del Gebrauchtwagenmarkt. **Campos atómicos (Q3/2025):** `Durchschnittspreis Gebrauchtwagen` (**€27.527**, sep-2025), `Preisänderung YoY` (**+0,6%**), `vs pico feb-2025` (**−2,4% / −€700**), **`Standzeit` media (58 días, +4 YoY)**, `Besitzumschreibungen` (~**560.000** en sep; **+6% YoY**; +1% trimestral), `Bestand` (**+1% YoY**, ~**25% bajo nivel pre-Corona**), `E-Auto Durchschnittspreis` (**€34.648**, **−3% YoY**, **+€7.120 / +26%** sobre la media), **Top-10 E-Auto** por precio+YoY (Tesla Model 3 €29.398 −14%; Audi Q4 e-tron €37.839 −22%; Renault ZOE €13.766 −7%; VW ID.3 €26.054 −2%; Tesla Model Y €38.045 −14%; VW ID.4 €34.880 −5%; smart fortwo €13.482 +2%; Hyundai KONA €26.551 −5%; Porsche Taycan €95.187 −5%; Škoda Enyaq €38.190 −12%).
- **Jahresanalyse / Jahresrückblick:** comparativa paneuropea (DE/BE/IT/AT/NL) de estabilidad de precio, oferta/demanda, ciclo de leasing; **E-Auto usado +6%** y **6,5% de la oferta VO alemana**.
- **Golf-Index:** precio del **VW Golf desde 2017** en **5 naciones europeas** + poder adquisitivo regional + tiempo-de-ahorro para comprar.
- **AutoScout24 Spotlight:** publicación de tendencias de mercado. [VERIFICADO: haendlerportal hub] · detalle [NO-VERIFICADO]
- **Encuestas:** precios de combustible, primer coche/financiación, "miedo al taller" (73% general / 91% Gen Z), demanda de leasing eléctrico.

---

## 4. Metodología y fuentes de datos

| Aspecto | Detalle | Estado |
|---|---|---|
| Naturaleza del dato | **Precio de ANUNCIO (Angebotspreis)** del propio inventario vivo de AutoScout24 — no precio de transacción confirmado | [VERIFICADO ≥2: preislabels, fahrzeugbewertung] |
| Fuente | **Inventario propietario** (>2M anuncios; >10M datasets históricos) de **45.000 dealers + particulares**; primer-party, no metasearch | [VERIFICADO ≥2: zahlen, preislabels] |
| Método de valoración | **Machine-Learning** comparando cada coche vs **comparables similares** (marca/modelo/edad/combustible/CV/transmisión/km/equipamiento) sobre **>70 features** + "expert knowledge" | [VERIFICADO ≥2: price-label-page, fahrzeugbewertung] |
| Ventana temporal | **Últimos 14 meses** hasta hoy (Preisbewertung); tiempo real (Fahrzeugbewertung) | [VERIFICADO ≥2: preislabels, fahrzeugbewertung] |
| Distinción seller | Algoritmo separa **dealer vs particular** | [VERIFICADO: preislabels] |
| Outliers | Excluye precios irreales / accidente / sellos / modificaciones | [VERIFICADO ≥2: preislabels, price-label-page] |
| IA de dealer | HändlerIQ usa "fortschrittliche KI" para detección de competidores, pronóstico de Standzeit, gaps de equipamiento y recomendaciones | [VERIFICADO ≥2: wettbewerbsanalyse, corporate-meldung] |
| Confidence score | **No expone score numérico de confianza**; cuando hay pocos comparables → **KEINE ANGABE** (en vez de un valor con intervalo) | [VERIFICADO: preislabels] |
| Limitación declarada | No considera estado individual del vehículo; asume buen estado | [VERIFICADO: preislabels] |

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **Web/App B2C** | Marketplace (.de/.com/.it/.nl/.be/.fr/.at…), apps iOS/Android ("AutoScout24: buying & leasing") | [VERIFICADO ≥2: portrait, App Store] |
| **Badge en anuncio** | Preisbewertung label en tarjetas de resultados y ficha de detalle (comprador) + página de explicación dedicada | [VERIFICADO ≥2: preislabels, price-label-page] |
| **Händler-Dashboard (web)** | Consola gratuita: HändlerIQ + KPIs + reviews (reemplaza el antiguo Händlerbereich) | [VERIFICADO ≥2: corporate-meldung dashboard, autohaus] |
| **Integración DMS (API)** | Estadísticas + HändlerIQ + SelectBoost embebidos en los **10 mayores proveedores de datos** | [VERIFICADO ≥2: corporate-meldung Datendienstleister, autrado] |
| **Listing Creation API (REST)** | Write-only para dealers (crear/gestionar anuncios + taxonomía) | [VERIFICADO ≥2: api docs, scrapfly] |
| **Subasta B2B (AUTOproff)** | Plataforma online de wholesale entre dealers | [VERIFICADO: autoscout24.com press] |
| **Retail online (Smyle)** | Compra + entrega + financiación + seguro + garantía | [VERIFICADO ≥2: smyle, corporate-meldung] |
| **Reportes / insights** | **MarktReport** trimestral (PDF), **Jahresanalyse**, **Golf-Index**, **Spotlight**, press releases (mediacenter/daten) | [VERIFICADO ≥2: mediacenter/daten, MarktReport] |
| **Magazine / editorial** | AutoScout24 Magazine (tests, contenido) | [VERIFICADO: portrait] |
| **Canales de lead** | LeadAssistent (IA), Kaufanfragen via WhatsApp, AnrufAssistent, AutoMatch | [VERIFICADO: haendlerportal hub] |

---

## 6. Precio (modelo)

| Producto | Modelo | Estado |
|---|---|---|
| **Service-Packages GO/SMART/PRO** | Suscripción por niveles (DE, desde 01-oct-2024); **precio no público** ("Infos und Preise auf Anfrage") | [VERIFICADO ≥2: service-pakete, automobilwoche] · precio exacto [NO-VERIFICADO] |
| **HändlerIQ + Dashboard** | **Gratis** dentro del service-package (Dashboard "kostenfrei für alle Partner"); Wettbewerbsanalyse en **test gratuito** | [VERIFICADO ≥2: corporate-meldung dashboard, wettbewerbsanalyse] |
| **Extras** | SalesTurbo/SocialBoost/AutoMatch/SelectBoost/NEU markieren — bookables con dto. por tier | [VERIFICADO: service-pakete] |
| **Fahrzeugbewertung (B2C)** | **Gratis** | [VERIFICADO: fahrzeugbewertung] |
| **Smyle** | Precio fijo del coche + **entrega desde €599** + financiación Openbank | [VERIFICADO: smyle] |
| **AUTOproff** | Membership Premium/Professional (dto. 25% para partners AS24) | [VERIFICADO: service-pakete] |
| **LeasingMarkt.de** | Requests con 20% dto. para partners | [VERIFICADO: service-pakete] |
| **Data licensing (DMS)** | Vía acuerdos con proveedores de datos (B2B, sin tarifa pública) | [VERIFICADO: corporate-meldung] · tarifa [NO-VERIFICADO] |
| **MarktReport / insights** | **Gratis/abierto** (PR/marketing) | [VERIFICADO: mediacenter/daten] |

---

## 7. Placement (dónde colocan cada dato — patrón a copiar por cardeep)

| Dato / métrica | Dónde se coloca (pantalla/sección) | Estado |
|---|---|---|
| **Preisbewertung label (5 niveles)** | **Badge semáforo en CADA tarjeta de resultado + ficha de detalle** (comprador); **panel "Fahrzeuge verwalten"** y **al introducir precio** (dealer); **página de explicación dedicada** del label | [VERIFICADO ≥2: preislabels, price-label-page] |
| **Marktpreis / Preisdifferenz** | Junto al label, en la ficha del vehículo y en HändlerIQ | [VERIFICADO: preislabels] |
| **Fahrzeugbewertung (Preisempfehlung/Marktwert/rango)** | **Resultado de la tasación B2C** (enviado por email; valor + rango con margen) | [VERIFICADO: fahrzeugbewertung] |
| **HändlerIQ (5 funciones + recomendación)** | **Home del Händler-Dashboard** (resumen) + **por vehículo** en la lista de inventario, con Schnellaktionen | [VERIFICADO ≥2: corporate-meldung dashboard, autohaus] |
| **Standzeitprognose (días a venta)** | Métrica IA por vehículo dentro de HändlerIQ/Dashboard | [VERIFICADO ≥2: dashboard, mobilitree] |
| **Wettbewerbsanalyse — preisranking + lista rival** | **Reiter/Tab "Wettbewerbsanalyse"** en la lista de vehículos; lista de rivales con precio/edad/km/Standtage/evolución | [VERIFICADO: wettbewerbsanalyse] |
| **Distribución de mercado (km/edad/precio)** | **Diagramas en la vista de detalle** de Wettbewerbsanalyse | [VERIFICADO: wettbewerbsanalyse] |
| **Ausstattungsvergleich** | Sección de comparación de equipamiento (propio vs competencia) en HändlerIQ | [VERIFICADO: wettbewerbsanalyse] |
| **KPIs de performance (Standtage/Anfragen/Merkzettel/Suchaufrufe)** | **Home del Dashboard**, vista central de KPIs | [VERIFICADO ≥2: dashboard, autohaus] |
| **Händlerbewertungen / Weiterempfehlungsrate** | **Home del Dashboard** (notificación + tareas) + página de reseñas del dealer | [VERIFICADO ≥2: dashboard] |
| **Estadísticas + HändlerIQ (licenciados)** | **Dentro del DMS/sistema del proveedor de datos** (donde el dealer trabaja) | [VERIFICADO: corporate-meldung Datendienstleister] |
| **MarktReport / Golf-Index (mercado)** | **PDF/PR de mercado** (mediacenter), separado del per-vehículo | [VERIFICADO ≥2: mediacenter/daten, MarktReport] |
| **Smyle (datos por coche)** | Ficha del coche en el shop online (precio fijo, edad, km, consumo, filtro de entrega) | [VERIFICADO: smyle] |

---

## 8. Diferencial (lo que ofrece y otros no)

1. **Escala de primer-party paneuropea**: >2M anuncios vivos + >10M datasets de **su propio** inventario de 45k dealers — el precio sale del mercado real que ellos mismos operan (no metasearch, no curva teórica). [VERIFICADO]
2. **Preisbewertung como badge semáforo de 5 niveles** sobre cada anuncio — confianza instantánea para el comprador y guía de pricing para el dealer; la métrica-firma copiable. [VERIFICADO]
3. **HändlerIQ = 5 funciones IA accionables por coche** (precio, calidad de anuncio, equipamiento, **Standzeitprognose**, competencia) con **Handlungsempfehlungen** one-click. [VERIFICADO]
4. **Standzeitprognose** (pronóstico de días-a-venta) como output nativo + claim cuantificado (ajuste en 60 días → −2/3 de Standzeit). [VERIFICADO]
5. **Wettbewerbsanalyse regional** con **distribución de km/edad/precio** y lista de rivales en vivo (precio/Standtage/evolución) — radar competitivo dentro del portal. [VERIFICADO]
6. **Data-out al DMS**: lleva sus estadísticas + IA a los **10 mayores proveedores de datos** (6 con HändlerIQ) — el dato vive donde el dealer trabaja, no solo en su portal. [VERIFICADO]
7. **Pila vertical completa**: marketplace + tasación + IA de pricing + **wholesale (AUTOproff)** + **retail online (Smyle)** + **leasing (LeasingMarkt.de)** + (Canadá) **software de dealer (AutoSync) y financiación (Dealertrack)** vía TRADER. [VERIFICADO]
8. **Inteligencia de mercado abierta de marca** (MarktReport, **Golf-Index** desde 2017, Jahresanalyse) — autoridad de mercado + generación de demanda. [VERIFICADO]
9. **Packages estilo SaaS** (GO/SMART/PRO con +100%/+250% visibilidad) que empaquetan visibilidad + IA + social en niveles. [VERIFICADO]
10. **Distingue dealer vs particular** en el cálculo de precio (matiz que guías genéricas no siempre hacen). [VERIFICADO]

---

## 9. Gaps (lo que NO ofrece / límites)

1. **Asking price, NO transaction price** — todo el dato de precio es de anuncio del propio portal; sin precio de venta confirmado. [VERIFICADO]
2. **Sin API pública de consulta/valoración** — la API oficial es **write-only** (Listing Creation); no hay endpoint público de search ni de valuation programática (a diferencia de AutoUncle/AutoGrab). [VERIFICADO]
3. **Sin valor residual / forecast de depreciación** como producto propio nombrado — no compite con Schwacke/Autovista RVM/Gold Book iQ en curvas RV a 12-60 meses. [NO-VERIFICADO presencia — ausente de la oferta pública] |
4. **Sin provenance/VIN history** (siniestros, propietarios, robo, lecturas de km, write-off) — no es un AutoCheck/HPI; el dato es precio+specs de anuncio. [VERIFICADO — ausente] |
5. **Sin confidence score numérico / intervalo** — usa **KEINE ANGABE** cuando faltan comparables, sin banda de confianza. [VERIFICADO] |
6. **Preisbewertung ignora el estado individual** del coche (asume buen estado) — limita precisión por unidad. [VERIFICADO] |
7. **Precio de packages no público** — "auf Anfrage"; no verificable la tarifa exacta. [NO-VERIFICADO] |
8. **Cobertura del dato de precio = mayormente DE** para Fahrzeugbewertung (base alemana); el alcance exacto del cálculo país-a-país no está documentado verbatim. [NO-VERIFICADO el detalle por país] |
9. **Discrepancias menores de cifras** (43k↔45k dealers; labels 5 vs 3-positivos; "SEARCH API" no confirmada). [VERIFICADO la divergencia] |
10. **Dependencia del primer-party**: si un segmento tiene poco inventario en AutoScout24, el dato pierde densidad (vs censos que agregan 2.600+ webs). [VERIFICADO conceptual] |
11. **Confusión de marca con autoscout24.ch (SMG) y mobile.de (Adevinta)** — entidades distintas; mucho material "AutoScout24" online no es del grupo H&F. [VERIFICADO — riesgo de fuente] |
12. **Equipamiento por VIN código-a-código no es su core** (no es JATO/DAT); usa ~70 features declarados en el anuncio, no build-data OEM por VIN. [VERIFICADO — naturaleza marketplace] |

---

## 10. Fuentes

| # | URL | Qué verifica |
|---|---|---|
| 1 | https://www.autoscout24.com/company/about-autoscout24/company-profile/portrait/ | Portrait oficial: ~2.000 empleados, >30M usuarios, >2M anuncios, >45k dealers, 11 core markets, 19 países + Canadá, fundación 1998 (MasterCar AG), productos (coches/motos/camping/comerciales/Smyle/Magazine), subsidiarias |
| 2 | https://autoscout24.de/unternehmen/ueber-uns/zahlen | Cifras: ~2.000 empleados, 30M+ usuarios, 2M+ anuncios, 45k dealers, 19 países; adquisiciones LeasingMarkt.de 2020 / AutoProff 2022 / TRADER fin-2024; lista de 11 core markets |
| 3 | https://hf.com/hf-to-acquire-autoscout24/ ; https://www.unquote.com/dach/official-record/3017695/ | Owner Hellman & Friedman; **€2.9bn** desde Scout24 (dic-2019) |
| 4 | https://www.autoscout24.de/haendlerportal/preislabels/ | **Preisbewertung:** 5 labels (Sehr guter/Guter/Fairer/Erhöhter/Hoher Preis) + KEINE ANGABE; >10M datasets; >70 features; ventana 14 meses; dealer vs particular; criterios de comparación (HU/AU, carrocería, Schadstoffklasse, Erstzulassung, Fahrzeugart, garantía, Getriebe, Kraftstoff, consumo, km, Leistung, norma, puertas); placement (verwalten/precio/búsqueda/detalle) |
| 5 | https://www.autoscout24.com/priceevaluation/price-label-explanation-page/6a60d039-d231-471e-ba90-7d9be0ec37de?culture=de-DE | Página de explicación del label (UI viva); variante 3-positivos (Top/Gutes/Faires Angebot); ML + >10M datasets; exclusiones (accidente/sellos/modificaciones/outliers); criterios (marca/modelo/edad/combustible/CV/transmisión/km/equipamiento) |
| 6 | https://www.autoscout24.de/fahrzeugbewertung/ | **Fahrzeugbewertung B2C:** inputs (Marke/Modell/Erstzulassung/Karosserie/Kraftstoff/Getriebe/Leistung/Ausstattungslinie/km/email); outputs (Preisempfehlung/Marktwert/rango con Verhandlungsspielraum); ML; >10M anuncios; "99% Angebotspreise"; sin VIN/matrícula |
| 7 | https://www.autoscout24.de/haendlerportal/wettbewerbsanalyse/ | **Wettbewerbsanalyse:** campos (Konkurrenzpreise, Preisänderungen, Preisspanne, Preis-Ranking; lista rival con Preis/Baujahr/km/Standtage/Preisentwicklung; distribución km/Erstzulassung/Preise; Ausstattungsvergleich; nº rivales; Umkreis; nuevos rivales; Marketing-Intensität); IA + Handlungsempfehlungen; claim 60 días → −2/3 Standzeit; API/DMS |
| 8 | https://www.autoscout24.de/unternehmen/corporate-meldungen/autoscout24-wettbewerbsanalyse-ab-sofort-verfuegbar-neues-ki-tool-liefert-haendlern-entscheidende-wettbewerbseinblicke/ | HändlerIQ = 5 funciones; 8 datapoints (precio/visibilidad/demanda/equipamiento/gaps/evolución/nuevos rivales/marketing); test gratis; 2M anuncios / 43k dealers |
| 9 | https://www.autoscout24.de/unternehmen/corporate-meldungen/neues-autoscout24-haendler-dashboard-mehr-transparenz-einfachere-bedienung-und-ki-unterstuetzung-fuer-den-handel/ ; https://www.autohaus.de/nachrichten/gw-trends/ki-funktionen-im-dashboard-autoscout24-modernisiert-haendlerbereich-3718960 | **Händler-Dashboard 07-oct-2025:** Home + 5 HändlerIQ + Schnellaktionen; KPIs (Standtage/Anfragen/Merkzettel/Suchaufrufe); Bewertungsmanagement; CCO Felix Frank; gratis |
| 10 | https://www.autoscout24.de/haendlerportal/service-pakete/ ; https://www.automobilwoche.de/autohandel/wie-mobilede-autoscout24-jetzt-auch-mit-paketpreisen/ | **Packages GO/SMART/PRO** (01-oct-2024); +100%/+250%; Lead+/Inseratsqualität/Preisbewertung/Ausstattungsanalyse/Wettbewerbsanalyse; extras (SalesTurbo/SocialBoost/AutoMatch/SelectBoost/NEU markieren); family benefits (LeasingMarkt 20% / AUTOproff 25%) |
| 11 | https://www.autoscout24.de/unternehmen/corporate-meldungen/autoscout24-intensiviert-partnerschaft-mit-datendienstleistern/ ; https://www.autrado.de/news/autoscout24-statistik-integriert | **Data licensing:** 10 mayores proveedores integran estadísticas; 6 con HändlerIQ; datos (Aufrufe/Leads/Standtage); SelectBoost exclusivo DMS; meta data-driven en el DMS |
| 12 | https://www.thomabravo.com/press-releases/autoscout24-finalizes-agreement-to-acquire-trader-corporation ; https://www.themiddlemarket.com/latest-news/autoscout24-buys-trader-from-thoma-bravo | **TRADER Corporation** (cerrado 11-dic-2024, ex-Thoma Bravo): AutoTrader.ca + AutoHebdo.net (26M visitas, 450k anuncios, 5k dealers), AutoSync (software), Dealertrack (financiación), Collateral Mgmt; Toronto 1975 |
| 13 | https://www.autoscout24.com/company/press-releases/autoscout24-to-acquire-a-majority-stake-in-digital-wholesale-platform-autoproff/ ; https://aimgroup.com/2022/03/28/autoscout24-to-buy-digital-wholesale-platform-autoproff/ | **AUTOproff** (mayoría, mar-2022): subastas B2B wholesale; líder DK; 120k+ vehículos 2021; sourcing+trade-in para dealers |
| 14 | https://www.autoscout24.de/smyle/ ; https://www.autoscout24.de/unternehmen/mediacenter/corporate-meldungen/autoscout24-smyle-bietet-autokauf-im-online-shop/ | **Smyle:** ≤6 años/≤100k km; TÜV ≥6m; estándares de desgaste; entrega desde €599 (4-6 sem); Openbank financiación; Allianz garantía 12m; AXA Smyle Care; 21 días devolución |
| 15 | https://www.presseportal.de/pm/13984/6152677 ; https://www.autoscout24.de/unternehmen/mediacenter/daten/ | **MarktReport Q3/2025:** €27.527 avg (+0,6% YoY, −2,4% vs pico); Standzeit 58 días (+4); Besitzumschreibungen ~560k (+6%); Bestand +1% (−25% vs pre-Corona); E-Auto €34.648 (−3%, +€7.120/+26%); Top-10 E-Auto; Golf-Index (desde 2017, 5 países); Jahresanalyse (DE/BE/IT/AT/NL); E-Auto VO +6% / 6,5% oferta |
| 16 | https://listing-creation.api.autoscout24.com/docs ; https://scrapfly.io/blog/posts/how-to-scrape-autoscout24 ; https://github.com/smg-automotive/autoscout24-api-specs | **Listing Creation API** write-only (crear/gestionar anuncios + taxonomía make/model); sin search público; repo SMG con 4 OpenAPI specs (openapi/fs24/listing-distribution/swiftcourt) — SMG ≠ H&F |

> **Nota de método:** fuentes primarias = páginas de producto `autoscout24.de/haendlerportal/*`, `corporate-meldungen`, `fahrzeugbewertung`, `preislabels` y `company portrait` (todas accesibles y leídas). Las APIs Swagger
> y los PDF de MarktReport se renderizan por JS/binario y NO se leyeron verbatim: sus campos se tomaron de las páginas HTML de producto y del press release en texto (presseportal). Divergencias declaradas
> (43k↔45k dealers; 5 labels vs 3-positivos; "SEARCH API" no confirmada). Desambiguación marcada: **AutoScout24 GmbH (H&F)** ≠ **autoscout24.ch (SMG)** ≠ **mobile.de (Adevinta)**. Sin invención: lo no leído va como
> [NO-VERIFICADO].
