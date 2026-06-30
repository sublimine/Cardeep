# Stat.vin (1VIN STAT) — Auditoría atómica

> **slug:** `stat-vin` · **subdominio de audit:** `vin-history` · **web:** https://stat.vin · siblings: https://delivery.vin (entrega/aduana) · https://statvin.tools (extensión Chrome)
> **Fecha auditoría:** 2026-06-30 · **Método:** WebFetch en vivo de home, `/statreport`, informe STAT real renderizado, `/about-us`, `/contact-us`, `/buy-report`, `/faq`, `/help-center`, `/vin-decoding`, tarjeta de lote `/vehicles/AUTOMOBILE/CHECKER`, `statvin.tools`, `delivery.vin` + verificación cruzada (Luxeo, Trustpilot, Scam-Detector, priceofbusiness). **Doctrina:** cada campo lleva fuente; **[V]** = verificado leyendo/renderizando la fuente · **[NV]** = no verificado / inferido (marcado siempre). Nada inventado; cuando la observación contradice una afirmación previa, gana la observación.
> **Veredicto express:** Stat.vin **NO es una guía de valoración** (no es KBB/Black Book/cap/Eurotax) **ni un Carfax/AutoCheck institucional**. Es un **agregador de historial de subastas de salvamento US/Canadá (Copart + IAAI) + Auto.ria (UA)** orientado a **importadores/exportadores** de coche siniestrado hacia **Europa del Este, Cáucaso, Polonia, países árabes y México**, con un **brokerage de puja+entrega end-to-end** detrás. Combina: (1) **checker GRATIS de historial de puja/venta** por VIN/LOTE (precio final, lote, daño, foto, vendedor); (2) un **informe de historial propio "STAT Report"** estilo VHR (**$4.90**/informe) que **replica el formato Carfax/AutoCheck** (timeline por dueño, odómetro, títulos, total loss); (3) **reventa de Carfax y AutoCheck** reales; (4) un **VIN decoder gratis**; (5) una **extensión de Chrome ("StatVIN Tools")** que **superpone datos sobre las páginas de lote de Copart/IAAI** (reserva del vendedor, nº de pujas, lotes similares, catálogo de piezas ETK); y (6) un **servicio de puja (web + extensión + app móvil) + entrega/aduana** vía depósito reembolsable (mín. **$2.000**, buying power 10×).
> **Identidad opaca:** marca legal en footer **"1VIN STAT"** (© 2020-2026; confirmada también en footer de `delivery.vin`); contacto vía **PBM (buzón privado) en Wilmington, Delaware**; teléfono **+1 (929)** (Nueva York); operador de perfil **rusófono/post-soviético** (idiomas RU/UK/KA + soporte "en ruso", mercados Ucrania/Georgia/Armenia). Sin matriz, dueño ni fundador público. **Trustpilot + Scam-Detector (trust score 34.8 / "Medium Risk", flags phishing/spam) registran quejas de cobro indebido y de datos inventados** → riesgo reputacional alto.
> **Patrón a copiar por cardeep:** (1) el **resumen "at-a-glance" de 12 contadores** ("Found: N records / No records found") como banda-cabecera tipo semáforo; (2) la **navegación por pestañas-ancla** sobre un informe largo; (3) el **timeline "DETAILED HISTORY" agrupado por dueño** con columnas `Date | Mileage | Source | Comments`; (4) la **tarjeta de lote de subasta** (Final bid, Lot, Mileage, Location, Seller, Damage, Sale document, Photos) como ficha mínima; (5) el **bloque "lotes similares" de la extensión** como proxy de valor de mercado por comparables.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca pública | **Stat.vin** / **StatVIN** | [V — header/footer, todas las páginas] |
| Marca legal (footer) | **1VIN STAT** — "© 2020-2026 - 1VIN STAT. AutoAuction Statistics v2.10.6" | [V — footer renderizado + footer de delivery.vin] |
| Título del informe | **"1 Vin Report"** (tab/title de `/statreport`) | [V — render] |
| Clones/afiliados | **stat-vin.com** ("Stat VIN — Copart & IAAI Auto Auction Bid History") · **statvin.net** ("Stat Vin — Vehicle History Reports & VIN Check") | [V — resultados de búsqueda; NV relación societaria entre dominios] |
| Dirección de contacto | **2810 North Church Street, PBM 29208, Wilmington, Delaware 19802-4447, US** | [V — /contact-us] |
| Naturaleza de la dirección | **PBM = Private Mail Box**; 2810 North Church St es dirección de **registered-agent / mass-registration** en Wilmington (no oficina real) | [V parcial — formato PBM explícito; NV que sea oficina operativa] |
| Teléfono | **+1 (929) 377 2229** (área 929 = Nueva York) | [V — header/footer, tel: link] |
| Email | **info@stat.vin** (general), **support@stat.vin** (soporte) | [V — /contact-us, /about-us, /help-center] |
| Soporte (horario) | **Lun–Vie, 09:00–20:00** | [V — /contact-us] |
| Redes | Instagram `instagram.com/stat.vin` · Facebook `facebook.com/statvin-112927524513109` · YouTube `channel/UCJz_Uk2O5wOlZz3HPs2sX3w` | [V — /contact-us, footer] |
| Extensión de marca (Chrome) | `chromewebstore.google.com/detail/stat-vin/nnfmkaglijgngnephnkgmaldmejandhk` — **5.0/5.0, 3.000+ usuarios activos, 100+ reseñas** | [V — statvin.tools] |
| App móvil | **Existe** (puja en tiempo real para depósitos ≥ $2.000); listado en Google Play / App Store **no localizado** | [V — /faq declara "Chrome extension or mobile app"; NV store listing] |
| Inicio de actividad | **2020** (copyright "© 2020-…") | [V — footer; aproximación por copyright] |
| Matriz / dueño / fundador | **No divulgado** en ninguna página | [NV — búsqueda dirigida sin resultado] |
| Perfil del operador | **Rusófono / post-soviético**: idiomas RU/UK/KA, mercados Ucrania/Georgia/Armenia/árabes/Polonia/México; Trustpilot menciona "strange Russian messages to confirm payment" | [V — case study Luxeo + Trustpilot + selector de idiomas] |

**Qué es (categoría real):** plataforma de **inteligencia de subastas de salvamento US/CA para el comprador-importador**, con **brokerage de compra + logística** detrás. El producto-gancho es el **historial de subasta gratuito** (Copart/IAAI); el monetizable es el **informe de pago + la intermediación de compra/entrega** (depósito + service fee + shipping). La capa de "vehicle history report" propia (STAT Report) **imita la estética y los campos de Carfax/AutoCheck** con datos de procedencia no declarada.

### Categorías de producto / negocio [V]
1. **Free Auction History Checker** — historial de puja/venta por VIN o LOTE en Copart e IAAI (US & Canada) + Auto.ria (UA).
2. **STAT Report** ("1 Vin Report") — informe de historial propio por VIN, de pago (**$4.90**).
3. **Reventa de Carfax** y **reventa de AutoCheck** (página `/buy-report`, ambos con sample visible).
4. **Free VIN Decoder** (`/vin-decoding`).
5. **StatVIN Tools** — extensión de Chrome que superpone datos en Copart/IAAI/Auto.ria.
6. **Car Delivery** — shipping terrestre+marítimo+aduana (sibling `delivery.vin`).
7. **Auction bidding brokerage** — registro + **Security Deposit (Buyer Power, mín. $2.000)** → pujar (web / extensión / **app móvil**) / ganar / pagar / enviar.
8. **Smart Car Finder** — matcher por preguntas sobre lotes activos Copart/IAAI.
9. **Auction calendar / discovery** — Buy Now, Auction Today/Tomorrow/This Week/Next Week, Popular cars day/week/month/year.
10. **Blog SEO** (MSRP by VIN, owner by VIN, alternativas a Carfax…) — motor de captación orgánica.

### Clientes objetivo [V]
**Importadores/exportadores y compradores particulares** de coche siniestrado US→(Europa del Este, Cáucaso, Polonia, países árabes, México) · **dealers/flippers** de salvamento · **casas de subasta** (consumidores de su estadística). /about-us declara: "dealer, auction house, or individual buyer".

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| **Geografía del DATO (origen)** | **EE.UU. + Canadá** vía **Copart (US&CA)** e **IAAI (US&CA)**; **Ucrania** vía **Auto.ria.com**; "and other partners" | [V — homepage, FAQ, case study Luxeo] |
| **Geografía de ENTREGA (destino)** | **UE:** Austria, Bélgica, Bulgaria, Croacia, Chequia, Dinamarca, Estonia, Finlandia, Francia, Alemania, Grecia, Hungría, Italia, Letonia, Lituania, Luxemburgo, Países Bajos, Polonia, Portugal, Rumanía, Eslovaquia, Eslovenia, España, Suecia, Ucrania. **Oriente Medio/Asia:** Georgia, EAU, Irak. (+ opción **"Purchase for Domestic Use"** = mantener el coche en US/CA sin exportar.) | [V — delivery.vin + /faq] |
| **Puertos de destino** | **Rotterdam, Bremerhaven, Klaipeda, Gdynia, Poti** | [V — /faq] |
| Mercados de tráfico (SEO) | **Ucrania, Georgia, Armenia, países árabes, Polonia, México** | [V — case study Luxeo] |
| Búsqueda | por **VIN (17 díg.)**, **LOTE**, o **Marca-Modelo-Año (From/To)** | [V — caja de búsqueda] |
| VHR (STAT Report) | Datos US-céntricos por VIN (DMVs estatales, dealers, títulos, seguros, OEM) — caso real: matrículas/títulos NJ/CA/FL/PA | [V — sample renderizado] |
| Escala BBDD | **"tens of millions of records"** (decenas de millones), "continuously updated" | [V — case study Luxeo] |
| Tráfico web | **183.000 visitas/mes (sep-2023) → 508.000 (nov-2024)**, +177.6% en 16 meses; pico ~325.000 clics/mes | [V — case study Luxeo] |
| Frecuencia | **Actualización diaria** de estado de subasta, precios y disponibilidad de lotes | [V — FAQ] |
| Idiomas | **5 verificados en vivo** en home, /about-us y /contact-us + schema `Organization`: **EN, RU, ES, PT, KA (georgiano)**. El case study Luxeo afirma **hasta 9** (añade UK, AR, PL, FR) — **no verificado en vivo esta pasada**. | [V — 5 en site; NV — 9 (solo Luxeo)] |

### Scope de vehículo [V]
- **Salvamento / siniestrado / total-loss** de subastas de seguros US/CA como núcleo; también lotes "clean" y "Buy Now".
- **Tipos (nav de búsqueda):** **Automobile, Motorcycle, Boats** (homepage); la nav ampliada cita además **Dirt Bike, Trailer, Travel trailer, Motorhome, Jet Ski**. Mucho más amplio que coche.
- **Granularidad:** por **VIN** o por **número de LOTE** de Copart/IAAI.
- **Histórico:** múltiples pasadas del mismo VIN por subasta a lo largo del tiempo (ver §3 "Auction sales history": un VIN puede tener N registros de venta con fechas/lotes/precios distintos — caso real: 3 pasadas).

---

## 3. Productos + campos atómicos

> Fuente de verdad del schema = **informe STAT renderizado en vivo** (VIN `ZARFAECN3J7574666`, 2018 Alfa Romeo Giulia Ti Sport) + **tarjeta de lote renderizada** (VIN `A12224975027C` Copart, `A12732743078` IAAI) + página `/statreport` + extensión `statvin.tools` + `/vin-decoding` + `/buy-report` + `/faq`.

### 3.1 STAT Report — informe de historial propio (producto núcleo de pago) [V]
Estructura **verificada** del informe (etiquetas verbatim):

**(A) Cabecera**
- `REPORT DATE` (p.ej. "2025.06.19")
- `Vehicle history report` + título `Year Make Model Trim` (p.ej. "2018 ALFA ROMEO GIULIA TI SPORT")
- `VIN-number`

**(B) Resumen "at-a-glance" — 12 contadores** (cada uno: `Found: N records` o `No records found`; valores reales del VIN de muestra entre paréntesis):
1. `Photo` (No records found)
2. `Auction sales history` (3)
3. `Ownership history` (3)
4. `Total loss` (1)
5. `Structural damage` (2)
6. `Airbag deployment` (No records found)
7. `Odometer check` (1)
8. `Accident/damage` (3)
9. `Manufacturer recall` (3)
10. `Basic warranty` (1)
11. `Damage history` (2)
12. `Sales history` (4)

**(C) Navegación por pestañas-ancla:** `Vehicle details` · `Auction sales history` · `Ownership history` · `Damage history` · `Detailed History` · `Sales history`

**(D) VEHICLE DETAILS**
- `Year` (2018) · `Country` (ubicación/registro, "Englishtown (NJ)") · `Make` (ALFA ROMEO) · `Model` (GIULIA) · `Fuel type` (Gasoline) · `Drive unit` (Rear Wheel Drive / Front / AWD / 4WD) · `Engine` (cadena "2.0L 280HP I4 DI TURBO" → desplazamiento, HP, cilindros/config, inducción)

**(E) AUCTION SALES HISTORY** — tabla, columnas: `Lot number` · `Price` (+ estado `Sold`/`Not Sold`). (Caso real: 3 pasadas por subasta del mismo VIN.)

**(F) OWNERSHIP HISTORY** — `Found: N owners`; por dueño (`Owner 1..N`):
- `Year purchased` · `Type of owner` (Personal lease / Personal / Fleet / Rental / …) · `Estimated length of ownership` · `Estimated miles driven per year` · `Last reported odometer reading`

**(G) DAMAGE HISTORY** — por registro: `Date` · `Mileage` · **`Damage location`** (diagrama del coche con cuadrantes **`Front` / `Right` / `Back` / `Left`**)

**(H) DETAILED DAMAGE HISTORY** — tabla por dueño, columnas: `Date` · `Mileage` · `Source` · `Comments` (severidad minor/moderate; tipo front-end / rear-end collision; `Functional damage reported`; `Structural damage reported`; `Vehicle damaged in multiple places`; `TOTAL LOSS VEHICLE`)

**(I) DETAILED HISTORY** — **timeline cronológico agrupado por dueño**, columnas `Date` · `Mileage` · `Source` · `Comments`. `Source` = DMV estatal / dealer (con **nombre + ciudad + teléfono**) / fabricante (FCA US LLC) / Auto Auction / Dealer Inventory / Damage Report. Tipos de evento **verbatim verificados en vivo**:
- `Vehicle manufactured and shipped to original dealer`
- `Vehicle offered for sale` · `Vehicle sold` · `Vehicle purchase reported`
- `Vehicle serviced` (+ sub-ítems: `Maintenance inspection completed`, `Fluids checked`, `Oil and filter changed`, `Tire repaired`, `Wheels checked`, `PCM reprogrammed`, `Vehicle washed/detailed`)
- `Title issued or updated` · `Registration issued or renewed`
- `Loan or lien reported`
- `Damage reported` · `Accident reported`
- `Odometer reading reported`
- `Vehicle repossessed`
- `Vehicle recovered after theft`
- `TOTAL LOSS VEHICLE` · `SALVAGE TITLE/CERTIFICATE ISSUED` · `RECONSTRUCTED TITLE ISSUED` · `NOT ACTUAL MILEAGE TITLE ISSUED`

**(J) SALES HISTORY** — tabla, columnas: `Date` · `Seller` (nombre/ciudad/teléfono o "Auto Auction" o DMV) · `Odometer`

**(K) Otros campos declarados** (página `/statreport`): `Title history`, `Salvage/insurance records`, `Accident records`, **`Vehicle passport information`** (+ `Transmission type`).

**(L) Disclaimer (footer del informe):** "This Stat Report history report is based on information provided by the Stat Report and available as of <fecha>… Stat Report further disclaims all warranties…" → **texto de VHR genérico con el proveedor original sustituido por "Stat Report"** (señal de feed white-label).

> Nota de procedencia: la **profundidad** del DETAILED HISTORY (eventos de taller con nombre+teléfono del dealer, window sticker, números de título, PCM reprogrammed) es **propia de un feed agregador clase Carfax/AutoCheck/NMVTIS-reseller**. El proveedor exacto **no se declara** → **[NV]**. No se inventa.

### 3.2 Free Auction History Checker — tarjeta de lote (producto-gancho) [V]
Campos de la **tarjeta de resultado** (render real, lotes Copart/IAAI):
- Fuente: `Copart` / `IAAI`
- `Year Make Model` (p.ej. "1977 CHECKER MARATHON")
- `VIN` (p.ej. A12224975027C)
- **`Lot number`** (p.ej. 76464085)
- **`Mileage`** ("N/A" o "64,601 mi")
- **`Location`** (estado-branch, p.ej. "OR - PORTLAND NORTH" / "Provo (UT)")
- **`Seller`** = tipo (`Insurance` / `Dealer`) **+ nombre del vendedor** (p.ej. "Charitable adult rides & services")
- **`Damage`** (p.ej. "Burn", "Rear")
- **`Sale document`** / Title code (p.ej. "Clear (UTAH)")
- `Sale date/time` + estado `This vehicle has been sold` / no vendido
- **`Final bid`** / Price (p.ej. "100 USD", "875 USD")
- `Photos`

### 3.3 Campos de lote ampliados (página de detalle + extensión) [V/NV]
Conjunto de campos de listado de subasta que stat.vin refleja (estándar Copart/IAAI):
- `Primary Damage` · `Secondary Damage` · `Loss type`
- `Estimated Retail Value (ERV)` / `ACV` (valor pre-daño que el vendedor aporta a Copart) — **passthrough**, no es valoración propia
- `Odometer` + `Odometer brand` (Actual / Not Actual / Exempt)
- `Title code` / `Sale document`
- `Run-and-drive status` · `Keys` (present/not) · `Gearbox`/`Transmission`
- `Body style` · `Cylinders` · `Drive type` · `Fuel` · `Engine` · `Trim` · `Vehicle type`
- `Color`
- `Seller type` · `Seller name` · `Seller reserve` (extensión)
- `Number of bids placed per lot` (IAAI, extensión)
- `Accident score`
- `Sale status` · `Sale date/time` · `Final bid` · `Photos`

> Estos campos ampliados están **[V]** como categoría (búsqueda + extensión + estándar Copart/IAAI); el detalle por-lote no se renderizó campo-a-campo (cards SPA sin deep-link estable) → granularidad marcada **[NV parcial]**.

### 3.4 StatVIN Tools — extensión de Chrome (gratis) [V]
"Official browser extension for Copart and IAAI auctions"; superpone sobre las páginas de lote:
- `Full vehicle VIN code`
- `Seller type` · `Seller reserve`
- `Number of bids placed per lot` (IAAI)
- `Bidding history` (Copart + IAAI)
- `Sales history of vehicles and models` (Copart + IAAI)
- `Information about technical equipment of the vehicle`
- `Catalog with vehicle part numbers` (**ETK Catalog**, gratis — números de pieza)
- `Information about similar lots previously traded at auctions` (**comparables** → proxy de valor de mercado)
- `Filterable model statistics`
- Plataformas: Copart, IAAI, **Autoria**. 5.0/5.0, 3.000+ usuarios, 100+ reseñas. "Free for Google Chrome", desktop.

### 3.5 Free VIN Decoder (`/vin-decoding`) [V]
Salida (básica): `Manufacturer` · `Make` · `Model` · `Year of production` · `Plant of production` · `Engine type` · `Car specifications`. Capacidades adicionales citadas: "search car parts", "check the car's history", "check the market value of a new or used car". El blog "MSRP by VIN" añade `MSRP` · `Trim level` · `included features` como capacidades de decode. **Sin tabla atómica de opciones/packages/equipamiento** → decode superficial.

### 3.6 Reventa Carfax / AutoCheck (`/buy-report`) [V]
- Ofrece **Carfax report** y **AutoCheck report** (ambos con **sample visible**); **precio no publicado**.
- Estructura descrita (Carfax): bloque **`Owner information`** (año de compra, tipo de propiedad, tiempo de propiedad, estado/ciudad de uso, millaje anual estimado, odómetro más reciente por dueño) + bloque **`Vehicle condition`** (con **triángulos rojos de alerta "ALERT!"** para daño/avería en cada periodo de propiedad). AutoCheck: sin desglose de secciones en la página.
- Modelo: **solo el primer bloque "general information" gratis** como preview; informe completo de pago. Rationale legal: "the database service is a paid, private property, the resale of which is prohibited by intellectual property law".

### 3.7 Servicios de compra + entrega [V]
- **Auction bidding:** registro → **Security Deposit (Buyer Power, mín. $2.000)** → pujar (web auto-bid a todos los niveles; **extensión Chrome o app móvil** para puja en tiempo real, requiere depósito ≥ $2.000) → ganar → pagar lote+fees → enviar.
- **Buying power:** **10× el depósito** ($2.000 → $20.000 de poder de compra). Tras ganar, parte del depósito se **"congela"** hasta completar el pago; el sistema **bloquea nuevas pujas** cuando el depósito restante baja de **$1.000**.
- **Bidding en dos etapas:** **Pre-Bid** (días antes) + **Live Auction** (tiempo real, minutos).
- **Free reports con depósito:** "users who have made a deposit gain access to free vehicle history reports"; **nº de checks gratis mensuales crece con el depósito**.
- **Car Delivery (delivery.vin):** flujo de 5 pasos → (1) cuenta + depósito reembolsable; (2) búsqueda + puja (pre-bid/live); (3) factura post-victoria con desglose; (4) pickup de subasta → warehouse → export prep; (5) llegada, descarga y entrega final con **documentos de aduana subidos por el dashboard** (+ inland carrier opcional). "Bid, buy and ship… all on our platform".
- **Member Fees / Help Center:** How to Bid, Registration & Membership, Buyer Power & Security Deposit, Lot information, Payment, Delivery, + Rules & Policies (General, Membership, Security Deposit, Bidding, Payment, Delivery) y Member Fees.

---

## 4. Metodología / fuentes de datos

| Elemento | Detalle | Estado |
|---|---|---|
| Fuentes de subasta | **Copart.com (US&CA)**, **IAAI.com (US&CA)**, **Auto.ria.com (UA)**, "and other partners" | [V — homepage, FAQ, case study] |
| Operación | **Agregación/consolidación** de listings de subasta en un solo lugar, "updated daily" | [V — FAQ, homepage] |
| Feed del STAT Report (VHR) | Datos US de **DMVs estatales, dealers/talleres, títulos, aseguradoras, fabricantes (OEM), subastas** — clase Carfax/AutoCheck; FAQ resume contenido como "registration history, insurance claims, mileage data, vehicle status, maintenance records"; **proveedor exacto no divulgado** | [V estructura — sample render; NV proveedor] |
| Valoración / "selling price data" | /about-us cita "precise selling price data… based on comprehensive market analysis and historical trends" + "key statistics on vehicle performance, market trends, and sales patterns" vía "real-time data and advanced algorithms" — pero el output observable son **precios de subasta históricos crudos + ERV/ACV de Copart + lotes similares**, no índices de valoración | [V parcial — afirmado; NV índice de valor propio] |
| Frecuencia | **Diaria** (estado de subasta, precios, disponibilidad) | [V — FAQ] |
| Disclaimer | Responsabilidad declinada; "información tan buena como sus fuentes; puede haber omisiones" | [V — disclaimer del informe] |

---

## 5. Entrega (delivery del dato/servicio)

| Canal | Detalle | Estado |
|---|---|---|
| **Web portal (SPA)** | stat.vin, multi-idioma (5 verificados), tras **Cloudflare**; búsqueda por VIN/LOTE/MMA | [V — render] |
| **Informe web** | STAT Report en URL pública `/statreport/show-report/<VIN>/<token>`; vista larga con tabs-ancla | [V — render] |
| **PDF / imprimible** | Probable (formato VHR clásico), no confirmado como descarga | [NV] |
| **Extensión Chrome** | StatVIN Tools — overlay en Copart/IAAI/Auto.ria | [V — chromewebstore + statvin.tools] |
| **App móvil** | Para puja en tiempo real (depósito ≥ $2.000); store listing no localizado | [V — FAQ; NV store] |
| **Cuenta + depósito** | Registro/Login; Buyer Power (Security Deposit ≥ $2.000) para pujar; depósito desbloquea informes gratis | [V — FAQ, Help Center] |
| **Delivery** | sibling **delivery.vin** (shipping + aduana; footer "1VIN STAT") | [V — render] |
| **API / feed / DMS / Excel** | **No documentado públicamente** (consumer-only; la "integración" es la extensión) | [NV — ninguna doc de API hallada] |
| **Notificaciones** | Web Push | [V — render] |

---

## 6. Precio

| Producto / concepto | Precio | Detalle | Estado |
|---|---|---|---|
| **STAT Report (1 informe)** | **$4.90** | Informe de historial propio por VIN | [V — /statreport] |
| **STAT Report ×3** | **$13.23** | **$4.41**/informe | [V — /statreport] |
| **STAT Report ×10** | **$41.65** | **$4.17**/informe | [V — /statreport] |
| **STAT Report ×20** | **$78.40** | **$3.92**/informe | [V — /statreport] |
| **STAT Report ×50** | **$183.75** | **$3.68**/informe | [V — /statreport] |
| **Free Auction History Checker** | **Gratis** | Historial de puja/venta por VIN/LOTE | [V — homepage, CHECKER] |
| **VIN Decoder** | **Gratis** | Decode básico | [V — /vin-decoding] |
| **StatVIN Tools (extensión)** | **Gratis** | Overlay Copart/IAAI/Auto.ria | [V — statvin.tools] |
| **Carfax / AutoCheck (reventa)** | **No mostrado** | Precio no publicado en /buy-report; primer bloque gratis | [NV importe] |
| **Security Deposit (Buyer Power)** | **mín. $2.000**, reembolsable | Habilita pujar (buying power 10×); desbloquea informes gratis | [V — FAQ] |
| **Stat.vin Service Fee** | **$450** (fijo, único, independiente del destino) | Comisión de la plataforma por compra | [V — FAQ] |
| **Bank fees (transfer internacional)** | **$10–$50** | No incluido en el calculador | [V — FAQ] |
| **Costes de entrega (delivery.vin)** | Por cotización | Componentes: **Lot price + Auction fees (Copart/IAAI) + Logistics charges + Port charges** | [V — delivery.vin] |

> El cobro de ~**$4 USD** del STAT Report aparece en quejas de Trustpilot (coincide con $4.90). [V — Trustpilot]

---

## 7. Placement — dónde coloca cada dato en su UI (patrón a copiar por cardeep)

| Dato | Dónde lo coloca Stat.vin |
|---|---|
| Identidad (Year/Make/Model/Trim/VIN) | **Cabecera** del STAT Report |
| Resumen de existencia de datos (12 categorías) | **Banda "at-a-glance"** bajo la cabecera — contadores `Found: N records / No records found` (semáforo de presencia) |
| Navegación del dossier | **Pestañas-ancla** sticky: Vehicle details · Auction sales history · Ownership history · Damage history · Detailed History · Sales history |
| Specs (year/country/make/model/fuel/drive/engine) | Sección **VEHICLE DETAILS** |
| Pujas/ventas en subasta del VIN | Sección **AUCTION SALES HISTORY** (tabla Lot/Price/Sold) |
| Propiedad por dueño (años, millas/año, odómetro) | Sección **OWNERSHIP HISTORY** (tarjetas Owner 1..N) |
| Daño con localización | Sección **DAMAGE HISTORY** con **diagrama del coche** (Front/Right/Back/Left) |
| Detalle de daño | **DETAILED DAMAGE HISTORY** (Date/Mileage/Source/Comments) |
| Cronología completa de eventos | Sección **DETAILED HISTORY** — **timeline agrupado por dueño** (Date/Mileage/Source/Comments) |
| Ventas/transferencias | Sección **SALES HISTORY** (Date/Seller/Odometer) |
| Legal/cobertura | **Footer** del informe (disclaimer) |
| Ficha de lote de subasta | **Tarjeta de resultado** del checker (Final bid, Lot, Mileage, Location, Seller, Damage, Sale document, Photos) |
| Reserva del vendedor, nº de pujas, lotes similares, piezas (ETK) | **Overlay de la extensión** directamente sobre la página de lote de Copart/IAAI |
| Decode rápido | Herramienta standalone **/vin-decoding** |
| Reventa Carfax/AutoCheck (owners + condition + alertas) | Página **/buy-report** (preview gratis del primer bloque) |
| Coste total de compra (lote+fees+logística+puerto+service fee) | **Calculador / factura** del flujo de delivery (delivery.vin) |
| Comparativa de proveedores | Página **/best-carfax-alternatives** (posicionamiento) |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Historial de subasta de salvamento GRATIS** (Copart + IAAI + Auto.ria) por VIN/LOTE: precio final, lote, daño, vendedor, foto — el gancho que las guías de valoración y los VHR de pago no dan gratis.
2. **Extensión de navegador** que **inyecta datos en las propias páginas de Copart/IAAI** (seller reserve, nº de pujas IAAI, lotes similares, **catálogo de piezas ETK** con part numbers, estadística de modelo filtrable) — herramienta operativa para el postor, rara en el sector de "historial".
3. **One-stop importador:** historial + puja (web/extensión/**app móvil**) + pago + **entrega/aduana** a EU/Cáucaso/Polonia/países árabes/México, todo en una marca (con delivery.vin), con **buying power 10×** y **service fee plano $450**.
4. **VHR propio ultra-barato ($4.90)** + **reventa de Carfax y AutoCheck** en la misma tienda → cubre los tres a un click.
5. **Multi-idioma para mercados de importación** (RU/UK/KA/AR/PL/PT/ES/FR) que los incumbentes US (Carfax/AutoCheck) ignoran.
6. **"Lotes similares" como proxy de valor de mercado** por comparables de subasta (no es índice, pero orienta el precio).
7. **Cobertura de tipos amplia** (moto, dirt bike, trailer, motorhome, jet ski, boats), no solo coche.

---

## 9. Gaps (lo que NO ofrece / debilidades)

1. **No es valoración — gap central para cardeep.** Cero índices: **sin** residual %, retail/trade/wholesale, days-to-sell, market days supply, price-to-market %, curva de depreciación, ajuste por km, índice demanda/oferta. Su "valor" = **precios de subasta históricos crudos + ERV/ACV de Copart (passthrough) + lotes similares**. No compite con KBB/Black Book/cap/Eurotax/Autovista.
2. **Geografía del dato = US/CA (+UA vía Auto.ria).** **Ningún dato de matriculación EU de primera mano**; el VHR es US-céntrico (DMVs estatales). Para huella digital España/EU sirve **solo como patrón de UI**, no como fuente. (La parte EU es de *entrega física*, no de dato.)
3. **Reputación / confianza (riesgo alto).** Trustpilot recoge: "incomplete… charge me ~4 USD… scam", "unauthorised charge… my bank cancelled my card", "they scammed me by saying my car showed an accident… real report showed no such thing… support tried to gaslight me", "strange Russian messages to confirm payment… hacker scam". **Scam-Detector: trust score 34.8 / "Medium Risk"**, flags de phishing/spam, "recommended to be avoided". [V — Trustpilot + Scam-Detector]
4. **Opacidad societaria.** Sin matriz/fundador; marca legal "1VIN STAT"; contacto **PBM (virtual) en Delaware**; teléfono NY. Baja transparencia institucional.
5. **Procedencia del STAT Report no divulgada** + disclaimer find-replaced ("based on information provided by the Stat Report"); cobertura inherentemente incompleta. **Fotos a menudo "No records found"** en el VHR propio (caso de muestra).
6. **Sin API / feed / integración DMS / export Excel** documentados; la única "integración" es la extensión de Chrome. No es producto B2B/dato estructurado.
7. **VIN decoder superficial** (manufacturer/make/model/year/plant/engine; sin tabla atómica de opciones/packages/equipamiento ni MSRP estructurado).
8. **No es censo de concesionarios ni marketplace de inventario** (categoría distinta de cardeep; no indexa la huella online de puntos de venta).
9. **SPA + Cloudflare** → no es fuente limpia/estable para scraping; cards enrutadas por SPA sin deep-link estable; `/vehicle-search` y `/popular-cars` quedan vacías/404 sin query.
10. **Inconsistencias de autodescripción:** **5 idiomas verificados en site vs 9 afirmados por Luxeo**; "professional VIN lookups" (about) vs brokerage de subasta (FAQ/Help Center); copy reciclado; múltiples dominios clon (**stat-vin.com**, **statvin.net**) que diluyen identidad y elevan riesgo de phishing/percepción.

---

## 10. Fuentes (URLs)

**Stat.vin (WebFetch en vivo, 2026-06-30)**
- https://stat.vin/ — qué es, auctions Copart/IAAI US&CA, tipos (auto/moto/boats), idiomas (5), Smart Car Finder, "Free to use / under 2 minutes".
- https://stat.vin/statreport — **pricing vivo** ($4.90 / 3=$13.23 / 10=$41.65 / 20=$78.40 / 50=$183.75) + lista de secciones del informe (incl. "Vehicle passport information", "Salvage/insurance records", "Accident records") + link al sample.
- https://stat.vin/statreport/show-report/ZARFAECN3J7574666/t6rq0P7C76J9oaAZ — **STAT Report real** (2018 Alfa Romeo Giulia): 12 contadores at-a-glance (con counts reales), VEHICLE DETAILS, AUCTION SALES HISTORY, OWNERSHIP HISTORY, DAMAGE HISTORY + diagrama Front/Right/Back/Left, DETAILED DAMAGE HISTORY, DETAILED HISTORY timeline por dueño (Date/Mileage/Source/Comments) con event-types verbatim, SALES HISTORY, disclaimer.
- https://stat.vin/vehicles/AUTOMOBILE/CHECKER — **tarjeta de lote real** (Copart VIN A12224975027C / IAAI VIN A12732743078): Lot number, Mileage, Location, Seller (tipo+nombre), Damage, Sale document, Final bid, Photos, Sold status.
- https://stat.vin/faq — checker gratis con depósito; **depósito mín. $2.000, buying power 10× ($20.000), freeze, bloqueo < $1.000**; Pre-Bid + Live; **app móvil**; **service fee $450**; **bank fees $10-50**; puertos Rotterdam/Bremerhaven/Klaipeda/Gdynia/Poti; "Purchase for Domestic Use"; fuentes (Copart/IAAI), update diario.
- https://stat.vin/about-us — "professional VIN lookups", "selling price data via market analysis and historical trends", "key statistics… market trends… sales patterns", clientes (dealer/auction house/individual buyer), idiomas (5).
- https://stat.vin/contact-us — **dirección Delaware PBM**, +1 (929) 377 2229, info@/support@, horario Lun–Vie 09:00–20:00, redes, idiomas (5).
- https://stat.vin/buy-report — **reventa Carfax + AutoCheck** (samples visibles); estructura Carfax (Owner information / Vehicle condition con triángulos rojos "ALERT!"); preview gratis del primer bloque; rationale IP-law.
- https://stat.vin/vin-decoding — VIN decoder gratis (manufacturer/make/model/year/plant/engine/specs; "search car parts"; "market value").
- https://stat.vin/help-center — categorías (How to Bid, Registration & Membership, Buyer Power & Security Deposit, Lot information, Payment, Delivery) + Rules & Policies + Member Fees + "bid, buy and ship… all on our platform".

**Sibling / extensión**
- https://statvin.tools — extensión Chrome: VIN, seller type/reserve, nº pujas (IAAI), bidding history, sales history, technical equipment, ETK part catalog, lotes similares, filterable model statistics; 5.0/5.0, 3.000+ usuarios; Copart/IAAI/Autoria.
- https://chromewebstore.google.com/detail/stat-vin/nnfmkaglijgngnephnkgmaldmejandhk — listado de la extensión.
- https://delivery.vin/ — servicio de entrega (footer **"1VIN STAT"**): flujo 5 pasos, destinos UE + Georgia/EAU/Irak, customs por dashboard, componentes de coste (lot price/auction fees/logistics/port charges).

**Terceros / verificación cruzada**
- https://luxeo.team/organic-rise-statvin-183k-500k-monthly-traffic/ — **tráfico 183k→508k/mes (+177.6%, sep-2023→nov-2024)**, "tens of millions of records", fuentes Copart/IAAI/Auto.ria, mercados Ucrania/Georgia/Armenia/árabes/Polonia/México, idiomas (afirma hasta 9: añade UK/AR/PL/FR).
- https://www.trustpilot.com/review/stat.vin — **quejas de cobro indebido y datos inventados** ("scam", "~4 USD", "unauthorised charge", "showed an accident… real report showed no such thing", "strange Russian messages to confirm payment"); ~5 reseñas.
- https://www.scam-detector.com/validator/stat-vin-review/ — **trust score 34.8 / "Medium Risk"**, flags phishing/spam, "recommended to be avoided" (fetch directo 403; datos vía snippet de búsqueda).
- https://priceofbusiness.com/vin-stat-to-check-car-auction-history-how-to-use/ — uso del checker (corrobora función + agregación de "insurance companies, government agencies, auction houses").
- https://stat-vin.com/ y https://statvin.net/ — dominios clon (marca/relación societaria no confirmada).
- Estándar Copart/IAAI (ERV/ACV, Primary/Secondary Damage, Sale Status, Odometer brand): documentación de soporte Copart/IAAI/AutoBidMaster que stat.vin refleja.

> **Marcas [NV] / discrepancias declaradas:** matriz/dueño/fundador (no divulgados; búsqueda dirigida sin resultado); dirección Delaware = PBM virtual (no oficina confirmada); **proveedor real del feed del STAT Report** (no declarado; estructura clase Carfax/AutoCheck con disclaimer find-replaced); existencia de **PDF/API/Excel** (no hallada); **precio de la reventa Carfax/AutoCheck** (no publicado); **store listing de la app móvil** (no localizado; existencia afirmada por su FAQ); detalle campo-a-campo de la **página de lote** (cards SPA sin deep-link, conjunto inferido del estándar Copart/IAAI + extensión); "selling price data via algorithms" afirmado pero **sin índice de valoración observable**; **5 idiomas verificados en site vs 9 afirmados por Luxeo**; relación con clones **stat-vin.com / statvin.net**. Nada de lo anterior se presenta como verificado.
