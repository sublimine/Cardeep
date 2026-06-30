# Auditoría atómica — ANWB Koerslijst (Autowaarde berekenen)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa/servicio de valoración de automoción (Países Bajos). Web: https://www.anwb.nl/auto/koerslijst
> Subdominio (taxonomía Cardeep): **valuation**.
> Fecha auditoría: 2026-06-30. Método: render EN VIVO de la herramienta con Playwright (recorrido completo de las 4 pantallas con matrícula real NL `H-804-XS` = VW Golf 1.6 TDI 2017, 95.000 km) + captura de endpoints de red (API interna ANWB) + páginas ANWB de seguro/dagwaarde y verkoopservice + reglas BPM de la Belastingdienst + sentencia Reclame Code (metodología verkoop vs inkoop) + Wikipedia/ANWB historia + blogs comparativos NL.
> Convención: **[V]** = verificado leyendo/observando la fuente · **[A]** = asumido/inferido/tercero (marcado siempre).
> Nota de entorno: la API de valoración (`/ratelist`) exige cabecera `x-auto-kosten-tool-id`; se capturaron URL y parámetros [V] pero el cuerpo JSON crudo no se extrajo (gate de cabecera + navegador compartido en contención). Los campos atómicos se verificaron por la UI renderizada, que es lo relevante para el placement de Cardeep.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca / producto | **ANWB Koerslijst** (rótulo de la web: "Autowaarde berekenen — Door middel van de ANWB Koerslijst") | [V] |
| Operador / owner | **Koninklijke Nederlandse Toeristenbond ANWB** (club automovilístico/turístico neerlandés; "Royal Dutch Touring Club") | [V] |
| Forma jurídica | **Vereniging** (asociación de miembros) con brazo comercial **ANWB B.V.** | [V] |
| Co-desarrollo | Desarrollada **"in samenwerking met BOVAG"** (asociación sectorial de empresas de movilidad/concesionarios) → de ahí "ANWB/BOVAG koerslijst" | [V] |
| Fundación ANWB | **1 de julio de 1883** (origen: Nederlandsche Vélocipèdisten-Bond → Algemene Nederlandse Wielrijdersbond) | [V] |
| HQ | **Den Haag** (La Haya), Wassenaarseweg 220, 2596 EC (barrio Benoordenhout) | [V] |
| Miembros | **~4,6 millones** (2024) | [V] |
| Categoría | Koerslijst / valoración de vehículos de ocasión (consumidor) + lista reconocida para uso fiscal (BPM) y de seguro (dagwaarde) | [V] |
| Backend técnico | API propia ANWB: `api.anwb.nl/car-information/backend-application` (el mismo backend sirve la "Autokosten tool"; cabecera `x-auto-kosten-tool-id`) | [V] |
| Proveedor de datos subyacentes | Datos de vehículo/motor/opciones ampliamente reportados como provistos por **Autotelex** (marktleider motorvoertuiggegevens desde 1964); identificación ligada a **RDW** (matrícula→datos + juicio NAP). ANWB no lo declara en la web | [A] datos Autotelex / [V] uso RDW |

### Clientes / usuarios objetivo
- **Particulares** (núcleo): saber qué vale su coche al comprar, vender, inruil o asegurar. [V]
- **Belastingdienst (Hacienda NL)**: la koerslijst ANWB es una de las koerslijsten aceptadas como prueba para la **depreciación del BPM** (impuesto de matriculación/importación). [V]
- **Aseguradoras**: base para la **dagwaarde** en caso de robo/total loss (ANWB Autoverzekering usa la propia ANWB Koerslijst + 10%). [V]
- **Leasing / financieras / sector**: citadas como usuarias de koerslijsten para valor de mercado. [A/tercero]

---

## 2. Cobertura

### Geográfica [V]
- **Países Bajos (NL) únicamente**. Es una **"Nederlandse koerslijst"** (requisito explícito de la Belastingdienst para fijar la depreciación en NL).

### Scope de vehículos [V/A]
- **Turismos (personenauto)** — verificado en vivo. [V]
- **Motos**: existe flujo análogo "ANWB motor verkopen / koerslijst motor". [A — no auditado en vivo]
- **Ocasión (occasions / VO)**; valor incl. **BTW & BPM**. [V]
- **Identificación**: por **kenteken** (matrícula NL) o manualmente por **merk + type + bouwjaar** (pestaña "Zoek op merk en type"). [V]
- **Límite práctico de antigüedad** ~**15 años** (no calcula bien coches más viejos). [A/tercero]
- **Detección de importación**: marca explícitamente "import auto" + mes/año de importación. [V]

---

## 3. Producto + campos atómicos

El producto central es **uno**: el asistente de valoración "ANWB Koerslijst" (gratuito, web + app). Alrededor hay productos adyacentes del mismo ecosistema de valor (Autoverkoopservice, Autokosten, Autoverzekering-dagwaarde) que se listan al final. Todos los campos siguientes están **verificados en vivo [V]** salvo marca contraria.

### 3.1 Entradas (input del usuario) [V]
- **Kenteken** (campo `licensePlate`) — pestaña "Zoek op kenteken".
- **Huidige kilometerstand** (campo `currentMileage`).
- **Merk / Type / Bouwjaar** — vía alternativa manual (pestaña "Zoek op merk en type"; selector `step-one-controller`).
- **Uitvoering** (selección de la versión exacta entre las coincidencias; p.ej. "GOLF 1.6TDI 81KW TREND" vs "…COMFORT").
- **Opties / Optiebedrag** — por vía kenteken se **autorrellena** como importe agregado desde los datos de matrícula; por vía manual se seleccionan opciones individuales. [V vía kenteken; A selección individual]
- **(Tasación ampliada/experta)** estado/conditie, fotos y daños → para una valoración más precisa. [A/tercero — no aparece en el flujo gratuito básico]

### 3.2 Identificación / especificación del vehículo (panel lateral persistente) [V]
- **Merk + model + uitvoering** (ej.: "VOLKSWAGEN GOLF 1.6TDI 81KW TREND").
- **Kenteken** (formateado, ej. "H-804-XS").
- **Bouwjaar** (mes + año, ej. "Maart 2017").
- **RDW oordeel kilometerstand** = **juicio NAP** de la lógica del cuentakilómetros: **"Logisch" / "Onlogisch"** (con tooltip explicativo). ← detección de posible fraude/rollback de km.
- **Ingevulde kilometerstand** (km introducidos por el usuario).
- **Catalogusprijs** (precio de catálogo del modelo base).
- **Optiebedrag** (importe total de opciones/accesorios de fábrica, "bovenop de standaard uitrusting").
- **Nieuwprijs** (= Catalogusprijs + Optiebedrag).
- **Brandstof** (ej. Diesel).
- **Transmissie** (ej. Handgeschakeld / automaat).
- **Aantal deuren** (ej. 5 deurs).
- **Vermogen** en kW (ej. 81KW).
- **Motor / cilindrada-tipo** (ej. 1.6 TDI).
- **Rango de años de la uitvoering** (ej. "2014 t/m 2017").
- **Import-detectie**: aviso "Dit betreft een import auto" + **fecha de importación** (ej. "geïmporteerd in juni 2020").

### 3.3 Salidas — valores de la koerslijst (pantalla de resultado) [V]
Tres bloques. Cifras de ejemplo = VW Golf 1.6 TDI 2017 / 95.000 km / import (ilustrativas).

**A. "Deze auto kopen?" → "Schatting waarde koop"** (rango: € 8.650 – € 11.250):
1. **Kopen bij BOVAG autobedrijf met garantie** (€ 10.650) — compra en concesionario BOVAG con garantía.
2. **Kopen bij merkdealer met garantie** (€ 11.250) — compra en concesionario oficial de marca con garantía.
3. **Rijklaarprijs** (€ 9.850) — precio "listo para circular".
4. **Aankoop bij een particulier** (€ 8.650) — compra a particular.

**B. "Deze auto verkopen?" → "Schatting waarde verkoop"** (rango: € 7.450 – € 8.650):
5. **Inruilen bij een autobedrijf** (€ 8.000) — valor de entrega/inruil en concesionario.
6. **Verkoop door een particulier** (€ 8.650) — venta entre particulares (estilo Marktplaats).
7. **Veilingprijs** (€ 7.450) — precio de subasta/mayorista.

**C. "Vervangingswaarde":**
8. **Vervangingswaarde i.v.m. total loss** (€ 9.650) — valor de reposición ante siniestro total (= base de la **dagwaarde** del seguro).

**Rangos agregados** (también salidas atómicas):
9. **Schatting waarde koop** (rango mín–máx de compra).
10. **Schatting waarde verkoop** (rango mín–máx de venta).

**Conceptos nombrados por ANWB en la intro** (promesa de la herramienta): "waarde bij koop of verkoop", **"de dagwaarde"** y **"de meeneemprijs"**. [V — texto de intro]
- *Nota honesta*: en el resultado en vivo del coche probado, "dagwaarde" se materializa como **Vervangingswaarde i.v.m. total loss**, y **"meeneemprijs"** (precio de venta rápida al contado) **no apareció como línea etiquetada independiente** — puede variar por vehículo/versión de la UI. Marcado [V-intro / no-etiquetado-en-resultado].

**Naturaleza de los valores** [V]: todos son **"richtprijzen"** = "gemiddelde prijzen **inclusief BTW & BPM**" (precios medios con IVA e impuesto de matriculación incluidos), asumiendo coche bien mantenido y **sin** tener en cuenta daños/piezas rotas.

**Para uso fiscal (BPM)** la koerslijst debe contener además [V — regla Belastingdienst]:
- **Historische nieuwprijs (consumentenprijs)** — precio nuevo histórico.
- **Nederlandse handelsinkoopwaarde** — valor de compra comercial neerlandés.
- (la ANWB Koerslijst expone Nieuwprijs/Catalogusprijs y los valores de inruil/inkoop que permiten derivar el % de afschrijving).

### 3.4 Acciones de salida [V]
- **Printen** (imprimir / generar copia del resultado).
- **Nieuwe berekening maken** (nueva consulta) · **Terug**.
- Cross-sell: **"Bereken de autokosten van deze auto"** → ANWB Autokosten; **"Je auto direct verkopen — gegarandeerde prijs"** → ANWB Autoverkoopservice.

### 3.5 Productos adyacentes del ecosistema (mismo backend/valor) 
- **ANWB Autoverkoopservice** [V]: bod garantizado para el coche; flujo aanvraag (gratis) → bod por email en 1 día hábil, válido 5 días → entrega en 14 días en punto de recogida (Wegenwachtstations / Logicx / garajes asociados) → pago al día siguiente. El bod = **media de pujas previas sobre coches comparables** + marktwaarde; influido por tellerstand correcto, onderhoudsboekje/facturas, APK. Servicekosten al vender (menor para socios).
- **ANWB Autokosten** [V]: calculadora de costes mensuales del coche (mismo backend "auto-kosten-tool").
- **ANWB Autoverzekering — dagwaarde** [V]: en robo/total loss paga **autowaarde conforme a la ANWB Koerslijst + 10%** (= marktwaarde). Define **dagwaarde / nieuwwaarde / aanschafwaarde / marktwaarde**; <1 año = nieuwwaarde; >1 año dentro de 12 meses de compra = aanschafwaarde (ampliable a 3 años).

---

## 4. Metodología y fuentes de datos

- **Base de valor = VENTA, no compra** [V — sentencia Reclame Code 2015/01132]: *"ANWB gaat uit van **verkoopwaarden**"* (valores de venta, perspectiva consumidor) frente a *"**Autotelex inkoopwaarden**"* (valores de compra/comercio). Esto explica que la ANWB tienda a dar cifras más altas que las listas profesionales de inkoop.
- **Co-desarrollo con BOVAG** [V]: usa la perspectiva del comercio organizado (concesionarios BOVAG/merkdealers) para las cifras de "kopen met garantie".
- **Datos de identificación/especificación** [V/A]: la entrada por matrícula resuelve marca/modelo/uitvoering/bouwjaar/brandstof/transmissie/deuren/kW/catalogusprijs/optiebedrag automáticamente; el **RDW oordeel kilometerstand** (NAP) y la **detección de import** provienen del registro RDW. Los `motorvoertuiggegevens` subyacentes se reportan (tercero) como de **Autotelex**.
- **Opciones**: la valoración "incluye het invullen van extra opties" (las opciones suben el valor). [V — Reclame Code]
- **Richtprijzen** = precios medios (incl. BTW & BPM), sin inspección física, sin ajuste por daños. [V]
- **Frecuencia de actualización**: ~mensual (tercero; no verificado en ANWB). [A]
- **Precisión**: desviación media citada ~5–10% (tercero; no verificado). [A]
- **Endpoints internos observados** [V]:
  - `GET /car-information/backend-application/api/v0/licensePlate/{kenteken}` → identificación/especificación del vehículo.
  - `GET /car-information/backend-application/api/v0/configuration/{configurationId}/**ratelist**?mileage=&licensePlateYear=&licensePlateMonth=&newPrice=&licensePlate=&optionsPrice=` → la **koerslijst** ("ratelist") con los valores koop/verkoop/vervangingswaarde. Requiere cabecera `x-auto-kosten-tool-id`.

---

## 5. Entrega

- **Web gratuita** [V]: asistente de 4 pasos en `anwb.nl/auto/koerslijst` (Next.js; SPA con routing cliente).
- **App móvil "ANWB Auto"** [V/A — citada por ANWB y terceros].
- **Salida imprimible** (botón Printen) [V].
- **Uso fiscal**: el resultado sirve como prueba de koerslijst para la **aangifte BPM** (importación/matriculación). [V]
- **Uso asegurador**: alimenta la dagwaarde de la póliza ANWB. [V]
- **API interna** (no publicada/no producto): `api.anwb.nl/car-information…` con cabecera propietaria. [V — endpoints; no hay API/feed B2B publicado para terceros]
- **No** se halló producto de **suscripción/feed/DMS B2B** ofrecido por ANWB para profesionales (a diferencia de AutotelexPRO/Eurotax/XRAY). [A — ausencia = GAP]

---

## 6. Precio

- **ANWB Koerslijst (consumidor): GRATIS.** [V]
- **ANWB Autoverkoopservice**: solicitud de bod **gratis**; se retienen **servicekosten** al vender (dependen del importe del bod; **menor tarifa para socios ANWB**). [V — importe exacto no público en esta auditoría]
- **Sin** nivel de pago / tarifa de koerslijst profesional descubrible por parte de ANWB. [A]

---

## 7. Placement — dónde se ubica cada dato en la UI
> Patrón a copiar por Cardeep. Asistente de **4 pasos** con **panel lateral derecho persistente** y **pantalla de resultado en 3 bloques**.

### Barra de pasos (siempre visible, arriba del formulario) [V]
`Kenteken` → `Uitvoering` → `Opties` → `ANWB Koerslijst` (breadcrumb navegable de la valoración).

### Paso 1 — "Kenteken" (entrada) [V]
- Dos pestañas: **"Zoek op kenteken"** / **"Zoek op merk en type"**.
- Campos: **Kenteken** (textbox) + **Huidige kilometerstand** (number). Botón **Verder**.
- Microcopy de promesa: "…waarde bij koop of verkoop, de dagwaarde en de meeneemprijs…".

### Paso 2 — "Uitvoering" (desambiguación de versión) [V]
- Panel central: **"N uitvoeringen gevonden"** + lista de radios; cada opción muestra **rango de años · deuren · brandstof · transmissie**. Enlace "Staat je uitvoering er niet bij?".
- **Panel lateral derecho** (aparece y persiste): cabecera con marca+modelo+uitvoering y bloque de datos: **Kenteken · Bouwjaar · RDW oordeel kilometerstand (con tooltip) · Ingevulde kilometerstand · Catalogusprijs · Optiebedrag · Nieuwprijs**.

### Paso 3 — "Opties" [V]
- Por vía kenteken: muestra **Optiebedrag** agregado (€) con explicación ("Hoe meer uitrusting, hoe hoger de waarde"). (Vía manual: selección de opciones individuales.)

### Paso 4 — "ANWB Koerslijst" (resultado) [V]
- **Aviso superior condicional**: "Let op! Dit betreft een import auto…" (+ "Deze auto kopen?").
- **Bloque 1 "Deze auto kopen?"** → encabezado **"Schatting waarde koop"** + rango grande, y 4 líneas etiquetadas: BOVAG-dealer met garantie / merkdealer met garantie / Rijklaarprijs / Aankoop bij particulier. CTA "Tips kopen occasion".
- **Bloque 2 "Deze auto verkopen?"** → **"Schatting waarde verkoop"** + rango, y 3 líneas: Inruilen bij autobedrijf / Verkoop door particulier / Veilingprijs. CTA "Tips auto verkopen".
- **Bloque 3 "Vervangingswaarde"** → línea **"Vervangingswaarde i.v.m. total loss"**.
- **Disclaimer** (asterisco) bajo los bloques: richtprijzen, sin inspección, incl. BTW & BPM.
- **Acciones**: Printen · Terug · Nieuwe berekening maken.
- **Panel lateral derecho** persiste con la ficha técnica del vehículo + cross-sell a **ANWB Autokosten** (costes mensuales) y a **ANWB Autoverkoopservice** (bod garantizado).

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Autoridad/confianza de marca**: ANWB (Koninklijke, 1883, ~4,6M socios) + respaldo **BOVAG** → la koerslijst de consumidor de referencia en NL, **reconocida por la Belastingdienst para BPM** y usada por aseguradoras/leasing.
- [V] **Desglose por CONTEXTO DE TRANSACCIÓN en lenguaje de consumidor**: distingue explícitamente compra en **BOVAG-dealer con garantía** vs **merkdealer con garantía** vs **rijklaarprijs** vs **particulier**, y en venta **inruil** vs **particulier** vs **veiling** — granularidad de "perspectiva de venta" que las listas de inkoop profesionales no presentan así.
- [V] **Valor de reposición total-loss integrado** + acoplamiento directo con **ANWB Autoverzekering** (dagwaarde = koerslijst + 10%).
- [V] **Cierre de bucle valor→liquidez**: del resultado se salta a **Autoverkoopservice** (bod garantizado, media de pujas reales comparables) y a **Autokosten** (coste mensual).
- [V] **Señales de integridad inline**: **RDW oordeel kilometerstand (NAP: Logisch/Onlogisch)** y **detección de import** dentro del propio flujo.
- [V] **Gratis, instantáneo, kenteken-driven**, en web y app.

## 9. Gaps (lo que NO ofrece / no expone)
- [A] **Sin producto B2B publicado** (ni API, ni feed, ni integración DMS, ni dashboard pro) para profesionales — frente a AutotelexPRO / Eurotax / XRAY. La API `car-information/ratelist` es interna y está gateada por cabecera.
- [V] **Base = verkoopwaarden** (orientada al consumidor); **no** entrega la profundidad de **inkoopwaarde/handelswaarde** ni la actualización **diaria** que el comercio necesita (territorio de Autotelex; ANWB ~mensual [A]).
- [V] **Sin ajuste por daños/estado** en el flujo gratuito; richtprijzen que **asumen** coche bien mantenido.
- [V] **Sin historial de vehículo** (siniestros, propietarios, ITV) más allá del flag NAP del RDW; no es Carfax/autoDNA.
- [A] **Techo ~15 años** de antigüedad; coches más viejos no se valoran de forma fiable.
- [V] **Metodología/fuente de datos opacas**: ANWB no declara en su web el proveedor de datos (reportado tercero: Autotelex) ni el algoritmo; no publica precisión/frecuencia.
- [A] **Sin previsión de valor residual / curva de depreciación / TCO como dato** (Autokosten es una calculadora de consumidor separada, no un feed).
- [V] **Sin transparencia de precio** para cualquier nivel profesional (porque no existe públicamente).
- [A] **Sin valoración multi-mercado/transfronteriza** (solo NL, por diseño fiscal).

---

## 10. Fuentes (URLs)
- https://www.anwb.nl/auto/koerslijst — herramienta "Autowaarde berekenen" (render en vivo de las 4 pantallas; H-804-XS). [V]
- API observada en vivo: `api.anwb.nl/car-information/backend-application/api/v0/licensePlate/{kenteken}` y `…/configuration/{id}/ratelist?mileage&licensePlateYear&licensePlateMonth&newPrice&optionsPrice` (cabecera `x-auto-kosten-tool-id`). [V]
- https://www.anwb.nl/auto/verkopen/waarde-bepalen — richtprijzen, factores, limitaciones. [V]
- https://www.anwb.nl/verzekeringen/autoverzekering/dagwaarde-auto — dagwaarde = ANWB Koerslijst + 10%; definiciones nieuwwaarde/aanschafwaarde/marktwaarde. [V]
- https://www.anwb.nl/auto/verkopen/verkoopservice (+ /hoe-werkt-de-anwb-verkoopservice, /zo-wordt-de-prijs-bepaald, /tarieven) — Autoverkoopservice (bod garantizado, proceso, servicekosten). [V]
- https://www.anwb.nl/over-anwb (+ /over-anwb/geschiedenis) — identidad: vereniging, HQ Den Haag, ANWB B.V., 1883. [V]
- https://nl.wikipedia.org/wiki/ANWB — fundación 1/7/1883, nombre Koninklijke Nederlandse Toeristenbond, ~4,6M leden (2024). [V]
- https://www.belastingdienst.nl/.../bpm-afschrijving-koerslijst-taxatierapport-forfaitaire-tabel — reglas BPM: koerslijst con historische nieuwprijs (consumentenprijs) + Nederlandse handelsinkoopwaarde; fórmula del afschrijvingspercentage; "alle opties". [V]
- https://www.reclamecode.nl/uitspraak/?uitspraakId=146976 (caso 2015/01132) — "ANWB gaat uit van verkoopwaarden" vs "Autotelex inkoopwaarden"; inruilprijs = richtprijs basada en Autotelex; ANWB incluye het invullen van extra opties. [V vía resumen; el HTML directo devolvió 522 en una toma]
- https://autotelex.nl/en/ — Autotelex marktleider motorvoertuiggegevens (desde 1964); datos a dealers/leasing/aseguradoras/importadores/bancos/Belastingdienst (contexto de proveedor/competidor). [V]
- https://www.ikwilvanmijnautoaf.nl/blog/autowaarde-opvragen-bij-anwb-koerslijst-of-autotelex y /wat-is-mijn-auto-waard — comparativa ANWB vs Autotelex; definiciones dagwaarde/inruilwaarde/marktwaarde/vervangingswaarde; afirmaciones de ~mensual/5–10%/≤15 años. [A/tercero]
- https://kentekencheck.me/anwb-koerslijst/ y https://kentekencheck.net/anwb-autowaarde/ y https://actueelplatform.nl/blog/wat-is-mijn-auto-waard-anwb/ y https://hoeveelautos.nl/artikelen/anwb-waarde-auto-checken/ — pasos, factores, datos RDW/BOVAG. [A/tercero corroborante]
- RDW Open Data (`opendata.rdw.nl/resource/m9d7-ebf2.json`) — matrícula de prueba válida (H804XS, VW Golf 2017). [V]

> Verificación: el set de campos de salida (10 valores + rangos), la ficha técnica del panel lateral, el flujo de 4 pasos y el placement están **verificados por render en vivo [V]**. La identidad corporativa, la base "verkoopwaarden", las reglas BPM y la dagwaarde-seguro están verificadas con fuente primaria/oficial [V]. Proveedor de datos (Autotelex), frecuencia mensual, desviación 5–10% y techo de 15 años quedan como **[A]/tercero**. La API de valoración existe y se observaron sus parámetros [V], pero el JSON crudo no se extrajo (cabecera propietaria + navegador compartido en contención); no se inventa su esquema.
