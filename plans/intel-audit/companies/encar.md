# Auditoría atómica — Encar (엔카닷컴 / Encar.com)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa: **el marketplace + portal de datos de coche usado #1 de Corea del Sur**. No es una guía editorial de valores (tipo KBB/Eurotax) ni un proveedor B2B API-first de datos en bruto; es un **portal transaccional B2C/B2B2C** cuya enorme base de anuncios y transacciones genera (a) una **tasación de mercado propietaria a escala** ("엔카시세" / EncarPrice, sobre big data de 1,2M+ coches/año), (b) un **sistema de confianza propietario** (엔카진단 Encar Diagnosis + 엔카보증 Encar Guarantee + 성능점검 inspección legal + 카히스토리 historial de seguros), y (c) un **índice de mercado publicado mensualmente a la prensa** (la "inteligencia" visible). Web (producto del scope): https://www.encar.com/ · sitio de exportación EN: https://global.encar.com/gate.
> Categoría taxonómica asignada por el orquestador (campo `subdomain`): **portal-insights**. Es una **etiqueta de categoría del orquestador, NO un host DNS**. Subdominios reales de Encar verificados por uso directo en esta auditoría: `www.encar.com`, `car.encar.com`, `fem.encar.com`, `m.encar.com`, `api.encar.com`, `global.encar.com` (+ `encarmagazine.com`, `encar.team`). No probé `portal-insights.encar.com` como host.
> Fecha auditoría: 2026-06-30. Método: navegación/render de encar.com (lista `dc_carsearchlist`, sitio export `global.encar.com`), **lectura directa de la API JSON pública de Encar** (`api.encar.com/search/car/list/general` y `api.encar.com/v1/readside/vehicle/{id}` — schema de campos leído de respuesta real), avisos oficiales (rediseño VDP 2024-12-05), páginas de producto (diagnóstico, home service, garantía, 비교견적), prensa sectorial (boletines de시세 jun-2026), CAR Group FY25 H1 results, ko.wikipedia/namu.wiki/한국경제 (historia), law.go.kr (성능점검기록부 별지 제82호), carhistory.or.kr (보험이력), AIM Group, THE VC, Carapis.
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre).
> Nota idioma: Encar es **mayoritariamente en coreano**; términos reproducidos en hangul + traducción. La UI renderizó facetas en otros idiomas según locale del navegador; los nombres de campo atómicos se tomaron del **JSON de la API real** (idioma-neutro) y de fuentes coreanas.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **Encar / 엔카 / 엔카닷컴 / Encar.com** (histórico **SK엔카** / SK Encar) | [V] |
| Razón social | **엔카닷컴 주식회사 (Encar.com Co., Ltd.)** — antes 엔카네트워크(주) → SK C&C 엔카 → SK엔카닷컴 | [V] |
| Reg. mercantil (사업자등록번호) | **104-86-54476** (mostrado en el footer de encar.com) | [V] |
| Categoría | **Marketplace transaccional de coche usado #1 de Corea** ("대한민국 No.1 중고차 플랫폼" / "드림카 플랫폼") con valoración de mercado propietaria, sistema de inspección/garantía propio, historial integrado y publicación de índice de mercado. Modelo: dealer-advertising + value-added products (no API de datos B2B autoservicio). | [V] |
| Fundación | **Enero 2000** — nace como TF de nuevo negocio de SK(주) ("Vision 21 Project", negocio #1). Web SK엔카 abierta jun-2000; **constitución como sociedad independiente dic-2000** (엔카네트워크(주)). | [V] |
| HQ | **Seúl, Corea del Sur** (sede corporativa; "Encar Trust Transaction Zone" en el complejo de automoción de **Gangseo, Seúl** para transacción presencial). | [V] |
| Propiedad actual | **100% CAR Group Limited** (ASX:CAR, Australia; antes carsales.com Ltd). Encar = filial surcoreana íntegramente participada. | [V] |
| Grupo matriz | **CAR Group** — portfolio: **carsales** (Australia), **Encar** (Corea), **Trader Interactive** (EE.UU.), **chileautos** (Chile), mayoría de **webmotors** (Brasil). Encar ≈ **12% de los ingresos del grupo**. | [V] |
| Peso en grupo | Segmento **Asia**; Encar ≈ 12% de revenue de CAR Group. | [V] |
| Cotización | Indirecta vía **CAR Group Limited (ASX:CAR)**. | [V] |
| Empleados | **Cientos** (perfiles de empleo coreanos: Jobplanet/Saramin/잡코리아 listan a 엔카닷컴㈜ como mediana-grande). Cifra exacta no divulgada aquí. | [A — rango por agregadores de empleo] |
| Sitios | `www.encar.com` (portal PC), `car.encar.com` / `fem.encar.com` / `m.encar.com` (nuevo front + móvil), `api.encar.com` (API que sirve el SPA), **`global.encar.com`** (exportación, inglés), `encarmagazine.com` (contenido), `encar.team` (corporativo/empleo). | [V] |
| Apps | **Encar app** en iOS (App Store id404512755) y Android (`com.encar.encarMobileApp`) — "중고차 필수 플랫폼, 내차팔기, 내차시세". | [V] |

### Hitos / cronología [V]
- **2000.01** — Nace como TF de nuevo negocio de SK(주) ("Vision 21 Project", negocio #1).
- **2000.06** — Apertura de la web **SK엔카**.
- **2000.12** — Constitución de sociedad independiente, entra en el grupo SK; razón social **엔카네트워크(주)**.
- **2007.09** — Campaña **클린엔카 (Clean Encar)**: primero del sector en **허위매물 신고제** (denuncia de anuncios falsos), **삼진아웃제** (tres-strikes), **marca de agua Encar**.
- **2013.05** — **SK C&C(주)** absorbe 엔카네트워크 → "SK C&C 엔카".
- **2014.04** — **JV con la australiana Carsales.com**: se constituye **SK엔카닷컴** (distribución online de usado). Carsales toma ~49,9%.
- **2015.07** — Lanza **비교견적 (comparative quote)**: subasta inversa entre dealers para mostrar el **precio más alto** al vendedor.
- **2016–2018** — Carsales adquiere el resto de la participación de SK; **ene-2018: 100% del grupo Carsales** (conversión a empresa de inversión extranjera). *(CAR Group: "remaining 51% in 2016"; fuentes coreanas: conversión formal 2018 — ver Gaps).*
- **2020.05** — Renombrada **엔카닷컴㈜ (Encar.com Co.)**; se elimina la marca SK "tras 21 años" (한국경제).
- **2024** — Despliegue de **Encar Guarantee** (59% de penetración en nuevos anuncios, H1 FY25), escalado de **Encar Home**, expansión de sucursales, **Dealer Direct** (trade-in). Rediseño de la VDP de PC (2024-12-05).
- **2025.07** — Lanzamiento de **엔카진단++ (Encar Diagnosis++)** (~100 ítems, fotos de bajos, garantía 90 días/5.000km, devolución 7 días).

### Clientes objetivo (segmentos) [V/A]
1. **Compradores de coche usado** (núcleo B2C — buscador + Diagnosis + Guarantee + Home Service). [V]
2. **Vendedores particulares** (내차팔기: 비교견적 con dealers, 내차시세 valoración, venta directa). [V]
3. **Dealers de usado** (clientes de pago: registran inventario, compran productos de anuncio premium, Diagnosis, Guarantee; red de partners de 비교견적). [V — fuente de ingresos principal]
4. **Empresas / leasing / rent-a-car / flotas** (disposición de activos vía 비교견적/Dealer Direct; valoración B2B). [V]
5. **Compradores internacionales / exportadores** (global.encar.com, con partners de export: Alrawasi, River Trading, Pick Plus). [V]
6. **Prensa / medios** (boletines mensuales de시세 = la "inteligencia" pública; "según Encar"). [V]
7. **[A]** Terceros que **scrapean** los datos como proxy de un feed B2B (Carapis, auctionsapi, auto-api) — indicio de que NO hay API B2B oficial autoservicio.

---

## 2. Cobertura

### Geográfica [V]
- **Corea del Sur** (mercado doméstico nuclear: inventario por **지역/시·도** — Seúl, Gyeonggi, Daegu, Busan… `OfficeCityState`).
- **Exportación internacional** vía **global.encar.com** (sitio en inglés, precios en **USD**, partners de export y shipping) — pero el inventario y la inteligencia siguen siendo el parque surcoreano.
- **Sin** operación de marketplace en otros países (eso lo cubren las hermanas del grupo: carsales/Trader Interactive/chileautos/webmotors).

### Escala (cifras — varias fuentes, ver Gaps) [V]
- **Live, leído de la API de Encar (2026-06-30):** **156.891** coches **usados domésticos (국산)** anunciados (`Count` del endpoint `search/car/list/general`, filtro `CarType.Y`). Importado + comercial/especial elevan el total. [V — primera mano]
- **Autodescripción:** "**대한민국 No.1**" plataforma de usado. [V]
- **~40%** del registro **anual** de matriculaciones de usado en Corea; **~1,2M** vehículos registrados/año en el marketplace; **~15M** vehículos a lo largo de dos décadas (AIM Group). [V — 3º]
- **~60% de cuota / 500.000+ anuncios activos** (Carapis, 3º; cifra superior — ver Gaps). [V — 3º, baja confianza]
- Base para el índice de시세: **big data de 1,2M+ coches/año** (autodescripción/EncarPrice). [V]

### Scope de vehículos [V]
- **Solo USADO** (no es portal de coche nuevo).
- Segmentos del menú: **국내/국산** (doméstico), **수입** (importado), **환경/친환경·전기** (EV/eco), **화물·특수·승합** (carga/especial/comercial-furgón).
- Atributos: turismos, SUV, sedán, eléctricos/híbridos, comerciales ligeros y especiales.

---

## 3. Productos + campos atómicos

Arquitectura **portal web + apps + API interna que sirve el SPA** (no API pública B2B). Bloques: (A) Buscador + tarjeta de anuncio, (B) Ficha de vehículo / VDP (modelo de datos completo), (C) 엔카시세 EncarPrice (valoración), (D) 엔카진단 Diagnosis + 엔카보증 Guarantee (confianza), (E) 성능점검기록부 (inspección legal), (F) 보험이력/카히스토리 (historial), (G) 내차팔기 (venta: 비교견적 + Dealer Direct), (H) Home Service / Meetgo (entrega), (I) Índice de mercado publicado (insights), (J) Export (global).

### — BLOQUE A: BUSCADOR + TARJETA DE ANUNCIO —

### 3.1 Lista de búsqueda + tarjeta (search result card) [V — leído en vivo]
Total por categoría visible (ej. "**156,898대**"). Cada tarjeta (placement crítico) expone:
- **Badge de confianza**: `진단++` / `진단+` (Encar Diagnosis++/+), `엔카홈서비스`, `엔카보증` (Guarantee) — esquina superior.
- `찜` (favorito / wishlist) + contador.
- **Identidad**: 제조사+모델+트림 (ej. "쉐보레(GM대우) 더 넥스트 스파크 LT 플러스"; "기아 K5 3세대 1.6 터보 시그니처").
- **연식 (año)**: formato "15/11식(16년형)" = matriculación 2015/11, **año-modelo (형식년도)** 2016.
- **주행거리 (km)**: "87,795km".
- **연료 (combustible)**: "가솔린/디젤/전기/하이브리드".
- **지역 (región)**: "대구/경기/서울".
- **성능기록 (link al registro de성능점검)**.
- **Comentario del dealer / tags** (texto libre): "무사고. 주행거리 짧음.최저가 제시차량 TAX 100% 계산서발행가능차량".
- **Opciones destacadas**: "드라이브와이즈,HUD,크렐사운드,스마트커넥트,썬루프,네비게이션".
- **Badges de condición/comercial**: `최저가구매가능차량` (precio mínimo), `상태양호차량` (buen estado), `특옵션차량` (opciones especiales), `짧은주행거리차량` (km bajo), `1인소유차량` (1 dueño), `비흡연차량` (no fumador), `24시간상담가능` (consulta 24h), `계산서발행가능차량` (factura emisible).
- **가격 (precio)**: en **만원** (10.000 KRW) — "580만원", "1,790만원".

**Campos atómicos del search result (JSON `search/car/list`, leídos en vivo):** `Id`, `Separation`, `Trust` [`ExtendWarranty`, `HomeService`], `ServiceMark` [`EncarMeetgo`, `EncarDiagnosisP1`], `Condition` [`Inspection`, `Record`, `Resume`], `Photo`, `Photos[]` {`type`,`location`,`updatedDate`,`ordering`}, `Manufacturer`, `Model`, `Badge` (trim), `BadgeDetail` (sub-trim), `GreenType` (eco N/Y), `FuelType`, `Year` (AAAAMM matriculación), `FormYear` (año-modelo), `Mileage`, `HomeServiceVerification`, `ServiceCopyCar` (alerta VIN duplicado/DUPLICATION), `Price`, `SellType` (일반/…), `BuyType` [`Delivery`], `OfficeCityState` (región).

**Orden (sort):** `ModifiedDate` (recién actualizados), + precio/km/año/relevancia [A].

### — BLOQUE B: FICHA DE VEHÍCULO (VDP) — modelo de datos completo [V — leído de `api.encar.com/v1/readside/vehicle/{id}`] —

Raíz del objeto: `vehicleId`, `vehicleType`, **`vin`**, **`vehicleNo`** (matrícula), `manage`, `category`, `advertisement`, `contact`, `spec`, `photos`, `options`, `condition`, `partnership`, `contents`, `view`.

**`category` (identidad/catálogo):** `type`, `manufacturerCd`/`manufacturerName`/`manufacturerEnglishName`, `modelGroupCd`/`modelGroupName`/`modelGroupEnglishName`, `modelCd`/`modelName`, `gradeCd`/`gradeName`/`gradeEnglishName`, `gradeDetailCd`/`gradeDetailName`/`gradeDetailEnglishName`, `yearMonth` (matriculación), `formYear` (año-modelo), `domestic` (doméstico/importado), `importType`, **`originPrice`** (precio nuevo/MSRP de fábrica), **`jatoVehicleId`** (mapeo al catálogo de **JATO Dynamics**), `warranty` { `userDefined`, `companyName`, `bodyMonth`, `bodyMileage`, `transmissionMonth`, `transmissionMileage` }.

**`advertisement` (anuncio/servicios):** `type`, `price`, `status`, `salesStatus`, `warrantyStyleColor`, `trust`, `hotMark`, `oneLineText`, **`directInspected`** (진단 directo), **`preVerified`**, **`extendWarranty`** / **`deemedExtendWarranty`** (garantía extendida), **`homeService`**, **`meetGo`**, **`preDelivery`**, `leaseRentInfo` (info leasing/rent), **`encarPassType`** / `encarPassCategoryType`, **`underBodyPhotos`** / `hasUnderBodyPhoto` (fotos de bajos), `advertisementType`, **`diagnosisCar`** (es coche diagnosticado).

**`spec` (especificación/condición física):** `type`, `mileage`, `displacement` (cilindrada), `transmissionName`, `fuelCd`/`fuelName`, `colorName`/`customColor`, `seatCount`, `bodyName` (carrocería), `tradeType`, `tradeOwnerType`, `tradeCompanyName`.

**`options`:** `type`, **`standard`** (equipamiento de serie), **`etc`**, **`choice`** (opcional), **`tuning`** (modificaciones) — arrays de opciones.

**`condition`:** `accident` (objeto de historial de accidente — formato/visualización), `inspection` (objeto del성능점검 — formato/visualización), `seizing` (con conteos — gravámenes/embargos/압류).

**`contact` (vendedor):** `userId`, `userType`, `no`, `address`, `contactType`, **`isVerifyOwner`** (propietario verificado), **`isOwnerPartner`**.

**`partnership`:** info de dealer/empresa, **centros de diagnóstico** y contacto.

**`contents`:** `text` (descripción), `meetGoText`.

**`manage` (gestión/engagement):** `registDateTime`, `firstAdvertisedDateTime`, `modifyDateTime`, **`subscribeCount`** (nº de favoritos/찜), **`viewCount`** (visitas), `reRegistered`, `webReserved`, `dummy`/`dummyVehicleId`.

**`view`:** flags de presentación: `encarDiagnosis`, `encarMeetGo`, `photoPlus`, etc.

**`photos[]`:** `code`, `path`, `type`, `updateDateTime`, `desc`.

**Secciones de la VDP (orden oficial, rediseño 2024-12-05):** **기본정보** (info básica) → **옵션정보** (opciones) → **차량상태** (estado del vehículo: 성능점검 + 사고/보험이력) → **보증현황** (garantía: Diagnosis/Guarantee) → **금융** (financiación) → **판매자정보** (vendedor) → **모델리뷰** (review del modelo) → **구매가이드** (guía de compra) → **시세** (valoración de mercado del modelo).

### — BLOQUE C: 엔카시세 / EncarPrice (valoración) [V] —

Tasación de mercado propietaria, **gratuita**, sobre big data de **1,2M+ coches/año**; "estándar del usado coreano". Tools: **내차시세** (mi-coche-precio) y **시세조회** (consulta de시세). 

**Inputs:** **número de matrícula + nombre del titular** (lookup automático), o manual (`브랜드/제조사`, `모델`, `세부 트림/등급`, `연식 범위`, `연료`); refinables por `등록 지역` (región), `주행거리 구간` (banda de km), `옵션 사양` (썬루프/네비 etc.).
**Outputs (campos atómicos):**
- **평균시세** (precio medio de mercado).
- **최고가 / 최저가** (máximo / mínimo).
- **상위권가 / 프리미엄** (tier superior) y **하위권가 / 저가 매물** (tier bajo).
- **시세 추이 그래프** (gráfico de tendencia reciente del precio del modelo).
- **등록대수** (nº de anuncios registrados de ese modelo/condición) [A — mostrado como contexto de liquidez].
- **감가 기준표** (tabla de depreciación; `fem.encar.com/estimate/depreciaction-table`).
- Variación por **지역** y **주행거리** (mismo modelo, distinto시세).

### — BLOQUE D: 엔카진단 (Diagnosis) + 엔카보증 (Guarantee) — confianza [V] —

#### 3.2 엔카진단 (Encar Diagnosis) — inspección propietaria con grados
Inspección hecha por **"진단 마스터" de Encar** en centros de diagnóstico nacionales; solo coches con **bastidor normal (무사고/normal frame)** obtienen la marca 엔카진단. **Niveles:** `진단+` (Diagnosis+ / P1) y `진단++` (Diagnosis++ / P2).
- **등급 (grado): 3 grados de confianza** según resultado de la inspección (comparables de un vistazo).
- **Verifica**: 사고유무 (accidente), 모델/등급 (modelo/trim), 옵션 (opciones).
- **진단++** añade: **~100 ítems de inspección**, **원동기/변속기** (motor/transmisión: códigos de fallo, testigos), **누유/누수** (fugas/agua), **fotos de bajos públicas** (하부 사진), neumáticos, luces, verificación de opciones, **estado de gestión del vehículo verificado por Encar** ("Encar Diagnosis Plus").
- **Compensación**: si hay error en 사고이력/등급/옵션, **dentro de 3 meses o 5.000km** (lo que antes ocurra).
- **진단++ incluye sin coste**: garantía de rendimiento **90 días / 5.000km** (vs estándar 30 días / 2.000km) + **devolución 7 días** + entrega nacional + verificación presencial (Encar Trust Transaction Zone, Gangseo).

#### 3.3 엔카보증 (Encar Guarantee) — inspección + garantía de powertrain
Producto de garantía que cubre **motor/transmisión** con plazos (`bodyMonth`/`bodyMileage`/`transmissionMonth`/`transmissionMileage` en el objeto `warranty`). **Penetración: 59% de los nuevos anuncios de Encar** (CAR Group H1 FY25). Garantía extendida adicional ~**6 meses / 10.000km**.

### — BLOQUE E: 성능·상태점검기록부 (Performance & Condition Inspection Record) [V] —
Formulario **legal obligatorio** (자동차관리법 제58조; 별지 제82호서식). El dealer debe entregarlo al comprador. **~69 ítems**. Campos atómicos:
- **Datos**: 주행거리 (km), 차대번호 (VIN), 배출가스 (emisiones), 색상 (color), 주요옵션 (opciones), 리콜유무 (recall), 튜닝 (tuning), 특별이력 (historial especial), 용도변경이력 (cambio de uso).
- **외판부위 (paneles exteriores, 8)**: 후드(capó), 프론트휀더(aleta del.), 도어(puertas), 트렁크리드(portón), 라디에이터서포터, 루프패널(techo), 쿼터패널, 사이드실패널.
- **주요골격 (estructura principal, 10)**: 프론트패널, 크로스맴버, 인사이드패널, 사이드맴버, 휠하우스, 대쉬패널, 플로어패널, 필러패널, 리어패널, 트렁크플로어 — estado: **교환(cambio)/판금(chapa)/용접(soldadura)/부식(corrosión)/흠집(rayón)/손상(daño)**.
- **주요장치 (sistemas)**: 원동기(motor), 변속기(transmisión), 동력전달장치(transmisión de potencia), 조향장치(dirección), 제동장치(freno), 전기장치(eléctrico) + 누유/누수 (fugas aceite/refrigerante).

### — BLOQUE F: 보험이력 / 카히스토리 (Insurance/Vehicle history) [V] —
Integrado desde **보험개발원 카히스토리 (KIDI CarHistory)**. Ítems atómicos:
- **자동차 용도 변경** (cambio de uso: 렌트/리스/영업용 → 자가용 / rent/lease/comercial → particular).
- **소유자 변경** (nº de cambios de propietario).
- **보험 사고 이력** (siniestros de seguro): **내차 피해** (daño a mi coche) / **타차 가해** (daño causado a terceros), con **conteo** y **수리비** (coste de reparación) por evento.
- **특수 사고 이력** (siniestros especiales): **전손** (siniestro total), **도난** (robo), **침수** (inundación).
- **신차 출고일** (fecha de salida de fábrica) y **주행거리 이력** (historial de km).
- *Latencia de reflejo en CarHistory: ~2,5–3 meses tras el siniestro.*

### — BLOQUE G: 내차팔기 (venta) — 비교견적 + Dealer Direct [V] —
- **비교견적 (comparative quote)**: el vendedor introduce su coche; **dealers partner pujan** para mostrar el **precio más alto** sin reuniones presenciales (subasta inversa). Red de dealers con **reglas de penalización**.
- **Dealer Direct** (trade-in): producto de retoma directa (CAR Group H1 FY25).
- **진단등록 / 보증판매**: el vendedor puede registrar con 진단/보증 para más confianza.

### — BLOQUE H: 엔카홈서비스 / 엔카밋고 (entrega) [V] —
- **엔카홈서비스 (Home Service)**: el coche **inspeccionado se entrega a casa**; **7 días de prueba** ("7일간 타보고 결정") antes de decidir la compra; devolución si no convence.
- **엔카밋고 (Encar Meetgo, Beta)**: transacción de confianza **presencial (방문) o por entrega (배송)** (`BuyType: Delivery`, flag `meetGo`/`preDelivery`).

### — BLOQUE I: Índice de mercado publicado (insights) [V] —
Encar publica **mensualmente** a la prensa coreana un **boletín de tendencia de시세** del usado (la "inteligencia" pública). Métricas atómicas del boletín (ej. **junio 2026**):
- **Variación media de시세 MoM (%)** global y por origen: **−3,98%** total (국산 −3,88% / 수입 −4,12%).
- **% de cambio por modelo** (ej. Kia K8 2.5 2WD Noblesse −5,07%; Genesis GV80 2.5T AWD −4,85%; Audi Q5 45 TFSI quattro Premium −6,53% = mayor caída).
- **Recomendación "구매 적기" (mejor momento de compra)** por modelo/segmento.
- **Comentario de defensa de시세 de EV** (resiliencia de eléctricos).
- **Metodología declarada del índice**: big data de Encar; **37 modelos populares año 2023** (국산+수입); base **무사고, 주행거리 60.000km**.

### — BLOQUE J: Export (global.encar.com) [V] —
Marketplace de **exportación en inglés** (precios en **USD**). Campos en EN: Make, Model, **generation/chassis code**, Trim/variant, Year (registration), Mileage (km), Fuel (Diesel/Gasoline/Gasoline Hybrid), Location/region, Price (USD), **Inspection badge (Diagnosis P1/P2)**. Filtros: brand (global + coreano), condición (near-new vs general), nivel de verificación (Diagnosis P1/P2), tipo de listado (general vs branded). Servicios: **free vehicle & history reports** para listados de export, verificación experta, acceso a **insurance history**, **export partners** (Alrawasi, River Trading, Pick Plus), shipping/documentación, soporte multi-idioma.

---

## 4. Metodología y fuentes de datos [V]
- **Modelo = marketplace transaccional**: el inventario lo suben **dealers** (y particulares); Encar lo normaliza contra un **catálogo de specs (mapeo `jatoVehicleId` → JATO Dynamics)** y `originPrice` (MSRP). [V]
- **엔카시세 (valoración)**: estadística propietaria sobre **big data de 1,2M+ coches/año** (anuncios + transacciones), segmentada por modelo/trim/año/región/km/opciones; devuelve media + máx/mín + tiers + tendencia. [V]
- **Confianza multicapa**: (1) **성능점검기록부** legal (inspección obligatoria del dealer, ~69 ítems); (2) **엔카진단** propietario (진단 마스터, 3 grados, 진단++ ~100 ítems + fotos de bajos); (3) **엔카보증** (garantía de powertrain); (4) **카히스토리** (보험개발원, siniestros/uso/propietarios/전손·도난·침수). [V]
- **Índice de mercado**: derivado de la base de anuncios; muestra controlada (**37 modelos, 2023, 60.000km, 무사고**) para comparabilidad MoM. [V]
- **AI**: el grupo invierte en plataforma y "value-added services"; menciones de **AI/big data para recomendaciones** y posibles capacidades de visión. **"Encar Vision AI" como producto nombrado NO verificado** en fuente primaria (ver Gaps). [A]
- **Fuentes de terceros enlazadas en datos**: 보험개발원 카히스토리 (historial), JATO (catálogo de specs vía `jatoVehicleId`). [V]

---

## 5. Entrega
- **Portal web** (`www.encar.com`, `car.encar.com`) + **móvil** (`m.encar.com`) + **apps iOS/Android** — canal primario. [V]
- **API JSON interna** (`api.encar.com/...`) que sirve el SPA; **pública de facto** (sin auth observada en endpoints de lista/detalle), pero **no documentada como producto B2B**. La escrapean terceros (Carapis, auctionsapi, auto-api). [V]
- **Informes de inspección/historial** embebidos en la VDP (성능점검기록부, 보험이력/카히스토리, fotos de bajos). [V]
- **Boletines de시세** a la prensa (PDF/nota; syndication editorial). [V]
- **Sitio de exportación** `global.encar.com` con free vehicle & history reports en EN. [V]
- **[A]** Sin **feed bulk / SFTP / Excel** ni **integración DMS** ni **API B2B autoservicio con plan de precios** documentados. La data se entrega como producto terminado (anuncio, valoración, informe, índice), no como feed crudo licenciado.

---

## 6. Precio
**B2C gratis (búsqueda, 내차시세, 비교견적); monetización B2B vía dealers + productos de valor añadido.** [V/A]

| Ítem | Precio | Estado |
|---|---|---|
| Búsqueda + 엔카시세/내차시세 + 비교견적 (vendedor) | **Gratis** (consumidor) | [V] |
| **엔카보증 (Guarantee)** | **110.000원** (coche < 50M원) / **220.000원** (≥ 50M원) | [V] |
| **Garantía extendida** | **~2.300원/día** (hasta ~6 meses / 10.000km) | [V] |
| **엔카진단++** | **incluye sin coste** garantía 90 días/5.000km + devolución 7 días | [V] |
| **카히스토리 (보험이력, vía KIDI)** | no-socio **2.200원/consulta**; socio **770원** (hasta 5/año) | [V — tarifa KIDI] |
| **Dealers (ingreso principal)** | **차량등록 이용권** (cupos de registro), **프리미엄 광고 상품** (productos de anuncio premium, auto-update), Diagnosis/Guarantee, comisiones de Home Service/financiación | [V — existen; tarifas exactas no públicas] |
| **TAM dealer-advertising (Corea, framing CAR Group)** | **5,5M transacciones × ~$100 gasto medio de marketing/coche** | [V] |

- **Financieros (CAR Group):** **H1 FY25** (6m a dic-2024) grupo: revenue **AUD $579M**, EBITDA **$292M** (proforma $302M, margen 55%). **Encar ≈ 12% del revenue del grupo**. Dato de medio año previo citado: Asia/Encar **AUD $65M** revenue (+10% YoY), adj. EBITDA **AUD $29M** (+6%). [V — atribución temporal con cautela, ver Gaps] 
- **Encar Guarantee: 59% de penetración** en nuevos anuncios (H1 FY25). [V]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep: mapeo pantalla/sección → dato.

### Tarjeta de anuncio (lista de búsqueda) — "ficha de coche" [V — visto en vivo]
- **Esquina/encima de la foto**: badges de confianza **진단++/진단+ / 엔카홈서비스 / 엔카보증** (el sello es lo primero que se ve) + `찜` (favorito).
- **Bloque identidad**: 제조사+모델+트림, **연식 (matriculación + año-modelo)**, foto.
- **Bloque hechos**: 주행거리(km) · 연료 · 지역 · enlace **성능기록**.
- **Bloque comercial**: tags (`최저가구매가능차량`, `1인소유차량`, `비흡연차량`, `24시간상담가능`…) + comentario del dealer.
- **Precio** (만원) abajo-derecha.

### VDP (ficha de vehículo) — secuencia oficial [V]
**기본정보** (manufacturer/model/grade/gradeDetail, año, km, combustible, cilindrada, color, carrocería, asientos, **VIN/matrícula**) → **옵션정보** (standard/choice/etc/tuning) → **차량상태** (성능점검기록부 con 외판/골격 + **보험이력/카히스토리** + fotos de bajos si 진단++) → **보증현황** (Diagnosis grado + Guarantee/warranty months·km) → **금융** (financiación) → **판매자정보** (dealer, isVerifyOwner) → **모델리뷰** → **구매가이드** → **시세** (평균/최고/최저 + gráfico de tendencia del modelo).
- **Engagement** (`viewCount`, `subscribeCount`/찜) mostrado junto al anuncio.

### Pantalla 엔카시세 / 내차시세 — valoración [V]
- **Input**: matrícula + titular (o manual).
- **Cifra central**: **평균시세**; a los lados **최고가/최저가** y tiers **프리미엄 / 저가 매물**.
- **Gráfico**: **시세 추이** (tendencia temporal del modelo).
- **Contexto**: 등록대수 + 감가 기준표 (depreciación) + variación por 지역/주행거리.

### Boletín de mercado (prensa) — "market intelligence" pública [V]
- Titular: **% medio de cambio MoM** (global y 국산/수입).
- Tabla por modelo: **modelo · % cambio MoM** + destacado de mayor caída.
- Recuadro: **"구매 적기"** (mejores compras del mes) + nota EV.
- Pie metodológico: muestra (37 modelos, 2023, 60.000km, 무사고).

### Sitio de export (global) — para comprador internacional [V]
- Tarjeta en EN con **Inspection badge (P1/P2)**, precio **USD**, chassis code; free vehicle & history report enlazado.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Tasación de mercado a escala nacional gratuita (엔카시세)** sobre 1,2M+ coches/año, **integrada como sección de la propia VDP** (시세 del modelo en la misma ficha) y como herramienta por matrícula — convierte el portal en el **estándar de precio del usado coreano**.
- [V] **Sistema de confianza propietario multicapa único**: inspección legal (성능점검) + **엔카진단 con 3 grados** + **진단++ (~100 ítems + fotos de bajos públicas)** + **엔카보증 (garantía powertrain, 59% penetración)** + **카히스토리** — todo embebido y con **compensación contractual** (3 meses/5.000km) y **devolución 7 días**.
- [V] **Home Service con 7 días de prueba** (entrega a casa, devolución) — fricción de compra casi de e-commerce, raro en usado.
- [V] **Índice de mercado mensual publicado** (변동 MoM por modelo, mejor momento de compra, EV) con **metodología declarada** (37 modelos/2023/60.000km/무사고) — autoridad de marca + SEO, alimenta la prensa nacional.
- [V] **Mapeo a catálogo JATO (`jatoVehicleId`) + `originPrice`** — normalización de specs y referencia al precio nuevo dentro del propio dato del anuncio.
- [V] **Brazo de exportación nativo (global.encar.com)** con free history reports en EN y partners de shipping — monetiza el parque coreano hacia compradores internacionales.
- [V] **Respaldo de CAR Group** (carsales): disciplina de producto/pricing de marketplace probada en 5 países.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Solo Corea del Sur** (+ export del parque coreano). Sin cobertura de mercado en otros países (lo cubren las hermanas del grupo).
- [V] **No es proveedor de datos B2B API-first**: la API `api.encar.com` sirve el SPA y es escrapeada por terceros, pero **no hay producto de datos documentado, ni plan de precios, ni SLA, ni feed bulk/SFTP/Excel, ni integración DMS**. La "inteligencia" se entrega como producto terminado (valoración, informe, índice), no como feed licenciado.
- [V] **No es guía de valores editorial** (tipo Eurotax/KBB) con matrices trade/retail/wholesale ni **valores residuales/forecasting** para leasing/flotas; el시세 es **media de mercado observada**, no un valor normativo prospectivo.
- [V] **Sin TCO / running costs / SMR** (tiempos de reparación, precios de pieza, mantenimiento programado).
- [V] **Days-to-sell / market days supply / price-to-market% NO publicados como métrica** al usuario (a diferencia de iSeeCars/vAuto); `viewCount`/`subscribeCount` son proxies de demanda, no un índice formal de velocidad de venta.
- [V] **Historial dependiente de 3º (보험개발원/KIDI)** y con **latencia 2,5–3 meses**; no es un informe de propiedad propio.
- [V] **Marca histórica confusa**: aún citada como "SK엔카" pese a no pertenecer a SK desde 2018/2020 (renombrada Encar.com 2020).
- [V] **Cifras de escala divergentes**: live ~157k usados domésticos (API) vs "500k+ activos / 60% cuota" (Carapis, 3º) vs "40% de matriculaciones / 1,2M·año" (AIM) — no hay un único dato consolidado y datado público.
- [V] **Ambigüedad en el año de toma de control 100% por carsales** (CAR Group: 2016; fuentes coreanas: conversión formal ene-2018).
- [A] **"Encar Vision AI"** aparece en resúmenes secundarios pero **no lo confirmé en fuente primaria de Encar**; trato la capacidad AI como genérica (recomendación/big data), no como producto nombrado verificado.
- [A] **Tarifas de dealer exactas** (차량등록 이용권 / 프리미엄 광고) **no públicas**; solo confirmadas su existencia y la de Guarantee/garantía extendida.
- [A] **Metodología fina del엔카시세** (pesos, tratamiento de outliers) no publicada: "big data" sin fórmula auditable.

---

## 10. Fuentes (URLs)
- https://www.encar.com/ — portal: menú (국내/수입/환경/화물·특수·승합), 시세 평가, 진단+/++, 워런티+, 클린카, 대출 3.9%, reg. mercantil 104-86-54476, tel 1599-5455.
- https://www.encar.com/dc/dc_carsearchlist.do?carType=kor — **lista en vivo**: total "156,898대", estructura de tarjeta (badges 진단++, 연식, km, 연료, 지역, 성능기록, tags, opciones, 만원).
- https://api.encar.com/search/car/list/general?count=true&q=(And.Hidden.N._.CarType.Y.) — **API de lista (leída en vivo)**: `Count`=156.891; campos del search result (Id, Trust, ServiceMark, Condition, Manufacturer, Model, Badge, BadgeDetail, FuelType, Year, FormYear, Mileage, Price, BuyType, OfficeCityState…).
- https://api.encar.com/v1/readside/vehicle/42196809 — **API de detalle (leída en vivo)**: schema completo (manage, category con `jatoVehicleId`/`originPrice`/warranty, advertisement, contact, spec, photos, options, condition, partnership, contents, view, vin, vehicleNo).
- https://www.encar.com/cs/cs_helpdesk.do?method=noticeRead&boardId=014&regid=280831 — aviso oficial: **rediseño VDP PC 2024-12-05**, orden de 9 secciones (기본정보→…→시세).
- https://fem.encar.com/diagnosis y https://car.encar.com/diagnosis/intro y https://fem.encar.com/cars/report/diagnosis-range — 엔카진단: 무사고/등급(3)/옵션, compensación 3개월·5,000km.
- https://jasonryu.net/2025/07/23/new-service-encardotcom-encar-analysis-plus-plus/ — 진단++: ~100 ítems, 원동기/변속기/누유, fotos de bajos, garantía 90일/5,000km, devolución 7일.
- https://www.hankyung.com/article/2024022722551 — 진단: 차량 이력 공개, fiabilidad.
- https://www.motoya.co.kr/news/articleView.html?idxno=43600 — 진단++ con fotos de bajos (하부 사진).
- https://www.encar.com/pr/pr_price.do y https://m.encar.com/pr/price.do y https://viewtree.kr/엔카-중고차-시세-조회-방법-a-to-z — 엔카시세: 평균/최고/최저, tiers 프리미엄/저가, 시세 추이 그래프, inputs y refinos.
- https://fem.encar.com/estimate/depreciaction-table — 감가 기준표 (depreciación).
- https://www.law.go.kr/ (별지 제82호서식, 중고자동차 성능·상태점검기록부) y https://namu.wiki/w/성능상태점검기록부 y https://www.kaiwa.org/inspection — **~69 ítems**: 외판 8 / 골격 10 + 원동기/변속기/조향/제동/전기/누유 + 주행거리/차대번호/배출가스/튜닝/특별이력/용도변경/색상/옵션/리콜.
- https://www.carhistory.or.kr/serviceInfo/carhistory.page — 카히스토리 (보험개발원): 용도변경/소유자변경/보험사고(내차피해·타차가해)/특수사고(전손·도난·침수); tarifa 2,200원 / 770원.
- https://www.encar.com/es/es_insurance_v01.html y https://m.encar.com/ca/ca_history_v04.htm — boletín/sample de 보험이력 en la VDP.
- https://aimgroup.com/2025/03/11/encar-accounts-for-40-of-used-car-registration-in-south-korea/ — ~40% de matriculaciones, ~1,2M/año, ~15M en dos décadas; revenue AUD$65M (6m, +10%), EBITDA AUD$29M (+6%).
- https://aimgroup.com/2024/03/01/encar-introduces-vehicle-history-information-service/ — servicio de información de historial (10+ piezas).
- https://cargroup.com/wp-content/uploads/2025/02/FY25-Half-Year-Results-Presentation-2.pdf y https://app.sharelinktechnologies.com/announcement/asx/34daa04805bf3cc2dd658b5bf7bf2d71 — H1 FY25: grupo revenue AUD$579M / EBITDA $292M; **Encar Guarantee 59% penetración**, Encar Home, Dealer Direct.
- https://en.wikipedia.org/wiki/CAR_Group — propiedad: 49% (mar-2014) + 51% (2016); portfolio carsales/Encar/Trader Interactive/chileautos/webmotors; Encar ≈ 12% revenue.
- https://ko.wikipedia.org/wiki/엔카닷컴 y https://namu.wiki/w/엔카닷컴 y https://www.hankyung.com/article/202004200821g — cronología 2000→2020 (SK Vision 21 → 엔카네트워크 → SK C&C → JV carsales 2014 → 100% carsales 2018 → 엔카닷컴 2020).
- https://www.encar.com/hs/homeservice.do y https://www.encar.com/mt/meetgo.do — Home Service (7일 시승) y Meetgo (방문/배송).
- https://www.encar.com/ew/extendwarrant.do?method=guide&type=periodprice — garantía/precio (보증기간·가격).
- https://global.encar.com/gate — sitio export EN: campos (chassis code, USD, Diagnosis P1/P2), partners (Alrawasi, River Trading, Pick Plus).
- Boletines de시세 (prensa, jun-2026): https://www.autoview.co.kr/ko-kr/articles/100572 , https://www.dt.co.kr/article/12067699 , https://www.motorgraph.com/news/articleView.html?idxno=43935 — −3,98% MoM, 37 modelos 2023, 60.000km, 무사고; K8 −5,07%, GV80 −4,85%, Audi Q5 −6,53%.
- https://carapis.com/parsers/encar.com/intro y /features — campos escrapeables (make/model/trim/year/fuel/transmission/mileage/inspection sheet/accident/repair/price+price history/options/dealer/location/photos); ~500k activos / ~60% cuota (3º).
- https://www.crunchbase.com/organization/sk-encar y https://www.zoominfo.com/c/encar/431613188 y https://thevc.kr/encarcom — perfil corporativo (SK Encar / 엔카닷컴㈜).

> Verificación: identidad e historia corporativa contrastadas con ≥3 fuentes (ko.wikipedia + namu.wiki + 한국경제 + CAR Group/Wikipedia). **Schema de campos atómicos leído de la API JSON real de Encar** (lista + detalle), no inferido. Estructura de la VDP de aviso oficial de Encar (2024-12-05). 시세 y diagnóstico de páginas de producto + reviews coreanas. 성능점검기록부 del formulario legal (law.go.kr). 보험이력 de carhistory.or.kr (KIDI). Financieros de CAR Group H1 FY25 + AIM. Discrepancias (escala 157k vs 500k vs 40%; año de control 2016 vs 2018; "Encar Vision AI" no confirmado; tarifas de dealer) marcadas explícitamente, no resueltas por invención. `subdomain` "portal-insights" = etiqueta taxonómica del orquestador, no host DNS (no probado como host; subdominios reales usados: www/car/fem/m/api/global).
