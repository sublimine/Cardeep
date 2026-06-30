# DAT Ibérica — DAT Automóvil Ibérica SLU

> Auditoría atómica · subdominio cardeep: **valuation** · prioridad 2
> Verificación: cada bloque marcado [V] (verificado ≥1 fuente directa) o [V2] (≥2 fuentes ortogonales) o [NO-VERIFICADO].
> Fecha auditoría: 2026-06-30. Términos de producto se conservan en su idioma original (ES/EN/DE).
> **Relación con auditoría hermana:** DAT Ibérica es la filial española de **DAT Group** (ver `dat-deutsche-automobil-treuhand.md`). Este informe NO repite el motor SilverDAT global; documenta el **producto español** (marca DAT Ibérica + alianza **GANVAM-DAT**) tal como se publica en `discover.datiberica.com`, y marca qué campos son específicos de España vs heredados del grupo.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre legal | **DAT AUTOMÓVIL IBÉRICA SLU** | [V2] footer del sitio + Infonif |
| NIF / CIF | **B62394762** | [V2] footer del sitio + Infonif |
| Marca comercial | **DAT Ibérica** · sitio comercial `discover.datiberica.com` · sitio corporativo `datiberica.com` | [V2] |
| HQ | **Rambla de Catalunya, 60, 1-1, 08007 Barcelona** (España) | [V] footer en todas las páginas |
| Contacto | Tel. **900 506 520** · `ventas@datiberica.com` | [V] INESE |
| Grupo / propiedad | Filial del **DAT Group** (Deutsche Automobil Treuhand), corporación tecnológica alemana | [V2] INESE + datgroup |
| Fundación del grupo | **1931** (DAT Group); "proveedor europeo líder en sistemas de información y servicios para automoción" | [V2] INESE + datgroup |
| Fundación de la SLU española | Año exacto de constitución | [NO-VERIFICADO] (existe con NIF B62394762; no recuperé fecha de alta) |
| Dirección España | **Luis Murias** (Director General) · Marius Burgstaller · Oscar García · Ignacio Brito | [V2] Murias verificado en INESE + eXpo Ganvam 2024 + autospare; resto [V] INESE |
| Alianza institucional | **GANVAM-DAT** — entidad neutral nacida de la alianza GANVAM (Asociación Nacional de Vendedores de Vehículos) + DAT Group | [V2] |
| Fecha de la alianza | **26 de enero de 2024** | [V2] autospare + posventa |
| Presentación de la alianza | Raúl Palacios (presidente GANVAM), Fernando Miguélez (DG GANVAM), Helmut Eifert (Managing Director Foreign Countries, DAT), Luis Murias (DG DAT Ibérica) | [V] búsqueda eXpo Ganvam 2024 |
| Agencia web | "Made by Matinum" (sitio WordPress + Elementor) | [V] footer |

**Lectura para cardeep:** DAT Ibérica es el **brazo español de un proveedor neutral europeo**, y su activo institucional es el sello **GANVAM-DAT** — "el valor de referencia oficial del mercado de VO en España", construido sobre la misma lógica de neutralidad que el DAT alemán (instancia neutral respaldada por la patronal del sector). Es el competidor español más directo en autoridad-de-valor a lo que cardeep aspira, con la diferencia de que DAT Ibérica vive de la **referencia de valor** (no de la huella digital de puntos de venta).

---

## 2. Categorías + cliente objetivo

**Categorías:**
1. **Identificación de vehículo + ficha técnica/equipamiento** (fastEquipments, €uropa-Code).
2. **Valoración VO (compra/venta + valores GANVAM-DAT)** (fastVO, fastValuate, weDAT).
3. **Índice de mercado / retención de valor residual** (Índice GANVAM-DAT, trimestral).
4. **Valoración masiva de stock/flota** (Valoración de Stock GANVAM-DAT + IdentifyVIN).
5. **Cálculo de reparación + peritación de daños por IA** (FastTrackAI, baremo EUROLACK).
6. **Gestión de siniestros colaborativa** (SilverDAT myClaim).
7. **Vehículo conectado / dato dinámico para renting** (SilverDAT Connect).

**Clientes objetivo (declarados por vertical en el sitio):**
- **Concesionarios** — identificación + tasación de stock VO, equipamientos actualizados. [V]
- **Vehículos de ocasión / compraventas** — tasación instantánea con valor GANVAM-DAT. [V]
- **Talleres** — presupuesto automático de reparación + valoración de daños con IA. [V]
- **Aseguradoras** — ciclo completo del siniestro (identificación → cierre de expediente), reducción de fraude. [V]
- **Peritos** — identificación exacta, valoración, peritación de daños. [V]
- **Empresas de renting** — valoración + gestión de contratos + control de estado a lo largo del ciclo de uso. [V]
- **Flotas corporativas** — valoración masiva, costes, rotación, mantenimiento del parque móvil. [V]
- **Abogados** — validación de equipamiento/versión (defensa pericial). [V]
- **Asistencia en carretera** — identificación de vehículo. [V]
- **OEM / marcas** y **alquiler de vehículos** — actores conectados en myClaim. [V]

---

## 3. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Geografía | **España** (mercado nacional; valor de referencia "del mercado español") | [V2] |
| Base de identificación (motor Identify-Code/€uropa-Code) | **73 marcas y más de 2.000 modelos**, con versiones, equipamiento (serie y opcional), precios, datos técnicos, emisiones y pesos | [V2] INESE + búsqueda datgroup |
| Marcas mostradas en home (logos) | ~**29-30 marcas**: Volvo, VW, Toyota, Tesla, Skoda, SEAT, Renault, Porsche, Peugeot, Opel, Mini, Mercedes, Maserati, Lexus, Lancia, Kia, Jeep, Honda, Ford, DS, Dacia, Cupra, Citroën, Chevrolet, BMW, Audi, Alfa Romeo, Abarth, Fiat | [V] home (marketing, subconjunto del motor) |
| Cobertura histórica (lanzamiento) | fastEquipments cubría **50 marcas** (turismos, vehículo comercial ligero, SUV) en su presentación inicial en Faconauto | [V] Infotaller (cifra de lanzamiento, anterior) |
| Scope tipo de vehículo (valor GANVAM-DAT en weDAT) | **Turismos · Vehículo Industrial Ligero · SUV · Motocicletas** | [V] wedat |
| Scope tipo de vehículo (motor SilverDAT, DAT Group ES) | Turismos · SUV · Motocicletas · Vehículo comercial ligero **≤3,5 t** · Camiones | [V] datgroup ES |
| Nuevo / usado | Foco **VO** (vehículo de ocasión). La **identificación** aplica a VN y VO; el **PVP oficial** es dato de nuevo | [V] |
| Edad valorable (fastValuate) | Vehículos de **hasta 20 años**, considerando equipamiento y kilometraje | [V2] INESE + búsqueda |
| Punto de referencia del índice residual | **36 meses** (3 años) post-matriculación; **60.000 km** (gasolina/híbrido/eléctrico) y **90.000 km** (diésel) | [V2] art_indiceganvam + autospare |
| Motorizaciones cubiertas en el índice | Gasolina · Diésel · Híbrido no enchufable (HEV) · Híbrido enchufable (PHEV) · Eléctrico puro (BEV) | [V2] art_indiceganvam + art_hibrido |

---

## 4. Productos + campos ATÓMICOS

> Nomenclatura comercial DAT Ibérica: los módulos llevan el paraguas **SilverDAT®** (fastVO, fastEquipments, fastValuate, myClaim, Connect) más la plataforma **weDAT®** y el sello de dato **GANVAM-DAT**.

---

### 4.1 weDAT® — plataforma integral multisoporte (núcleo comercial)
"Centraliza la identificación del vehículo, la valoración de daños y la presupuestación en una única plataforma." Adaptable a talleres, peritos, aseguradoras, concesionarios. [V2 wedat + home]

**Funciones / campos atómicos:**
- **Selección/identificación de vehículo** por `matrícula` y `VIN` → características técnicas, `equipamiento de serie`, `opcionales`. [V]
- **Valoración VO** con `valor GANVAM-DAT` para `turismos`, `vehículo industrial ligero`, `SUV`, `motocicletas`. [V]
- **Estimación y valoración de reparaciones** (cálculo de reparaciones + tasaciones). [V]
- **Cálculo de reparaciones con baremo `EUROLACK`** (sistema de pintura DAT-Eurolack). [V] art_semanaseguro
- **Tipología de recambio**: `OEM` · `IAM` · `Recambio verde` (reciclado). [V2] wedat + INESE
- **Múltiples baremos de pintura** disponibles. [V] wedat
- **Integración con procesos de peritación**. [V]
- **Incorpora FastTrackAI®** (análisis fotográfico guiado para identificación y estimación de daños). [V] art_semanaseguro
- Atributos clave: `Móvil` (multidispositivo, sin instalación) · `Innovador` · `Rápido`. [V]

---

### 4.2 SilverDAT® fastVO — valoración profesional de VO (compra/venta)
"Identificación y valoración precisa de vehículos en procesos de compra y venta." [V2 fastvo + home]

**Inputs:** `matrícula` o `VIN` (+ `kilometraje`, implícito en la valoración). [V]

**Campos atómicos de salida:**
- `datos técnicos del vehículo` (ficha técnica). [V]
- `equipamiento de serie`. [V]
- `equipamiento opcional`. [V]
- `valor de mercado del vehículo`. [V]
- `valor de compra` y `valor de venta` de mercado (tasaciones de VO). [V2] home + Infotaller ("valores de venta y compra de mercado")
- `informe de valoración` customizable (formato configurable por usuario). [V]

**Cualidades de producto:** `Personalizable` (flujo de trabajo, permisos, formatos de informe) · `Multiplataforma` · `Ágil` (pocos inputs → informe rápido). [V]

---

### 4.3 SilverDAT® fastEquipments — identificación + ficha técnica + PVP + ADAS
"Visión detallada del equipamiento original y opcional a partir de matrícula o VIN, accediendo a la base de datos oficial del fabricante." [V2 fastequipments + home]

**Inputs:** `matrícula` o `VIN` / `número de bastidor`. [V]

**Campos atómicos de salida:**
- `ficha técnica` completa. [V] home
- `versión exacta` / `acabado` del vehículo. [V2] home + art_semanaseguro
- `equipamiento de serie`. [V]
- `equipamiento opcional` / `extras`. [V]
- **`detección automática de opcionales`**. [V]
- **Sistemas `ADAS`** (asistencia a la conducción) entre los opcionales identificados. [V2] INESE + búsqueda datgroup
- `PVP oficial` (precio de venta al público). [V2] home + datgroup
- `configuraciones de fábrica` (todas, "sin margen de error"). [V]
- Identificación mediante **codificación oficial del fabricante** (`€uropa-Code` / `Identify-Code`). [V] art_semanaseguro

**Casos de uso declarados:** recompra, financiación, reventa, ajuste de valor de mercado, peritación. [V]

---

### 4.4 SilverDAT® fastValuate — identificación + valores GANVAM-DAT (evolución de fastEquipments)
"Evolución de fastEquipments: identificar y obtener de forma rápida los `valores de compra y venta GANVAM-DAT`." [V2 art_semanaseguro + INESE]

**Campos atómicos:**
- `valor de compra GANVAM-DAT`. [V]
- `valor de venta GANVAM-DAT`. [V]
- `valor de mercado` y `valor de tasación (appraisal)` de vehículos de **hasta 20 años**. [V2] INESE + búsqueda
- Ajuste por `equipamiento` y por `kilometraje`. [V2]
- Basado en `precios reales de transacción de múltiples fuentes`. [V2] INESE + búsqueda
- **`SoH (State of Health)` de batería** para valoración de VE (metodología de salud de batería). [V] INESE

**Orientado a:** concesionarios, compraventas, renting y flotas, departamentos de **remarketing**. Optimiza `trade-in`, `tasación`, decisiones estratégicas. [V] art_semanaseguro

---

### 4.5 FastTrackAI® — peritación de daños por IA / visión por computadora
"Estimaciones de daños y presupuestos de reparación en tiempo real, a partir de imágenes." Apoyado en la base SilverDAT®. [V2 fasttrackai + home]

**Input:** `imágenes del siniestro` (carga fotográfica guiada). [V]

**Flujo (3 pasos):** 1) usuario carga imágenes → 2) IA detecta e interpreta daños → 3) se genera presupuesto detallado. [V]

**Campos atómicos de salida:**
- `daños identificados` (detección por IA). [V]
- `detalle de piezas` (recambios). [V]
- `operaciones` de reparación. [V]
- `costes de reparación`. [V]
- `presupuesto detallado` de reparación (estimado). [V]
- `valoración inmediata y automatizada desde imágenes`. [V]

**Tecnología:** IA + visión por computadora sobre base SilverDAT®. **Compatible con otros sistemas** de valoración y gestión. [V]
**Target:** peritos, aseguradoras, talleres, empresas de renting. [V]

> Nota: la versión española publicada NO detalla explícitamente `punto de impacto (POI)`, `Totalschaden/siniestro total` ni `valor residual del siniestrado` como campos discretos — sí están en el FastTrackAI del grupo alemán (ver informe DAT Deutsche §4.5). Marcado como [heredado-grupo, NO-publicado-ES].

---

### 4.6 SilverDAT® myClaim — gestión colaborativa de siniestros
"Plataforma integral que conecta aseguradoras, talleres, peritos, abogados, renting, marcas y clientes en un único entorno digital seguro." [V2 myclaim + home]

**Campos / capacidades atómicas:**
- `estado del siniestro` en tiempo real (visión global para todos los actores). [V]
- `trazabilidad y control` en cada fase. [V]
- `detección automática de opcionales` (hereda identificación). [V]
- Ciclo: `notificación inicial` → gestión → `liquidación` → `recuperación de costes`. [V]
- `comunicación` centralizada entre actores (reduce errores, duplicidades, tiempos). [V]
- `reducción del fraude` vía trazabilidad y coherencia de datos. [V] aseguradoras
- Compatible con otros sistemas y plataformas. [V]

**Actores conectados:** aseguradoras · abogados · peritos · asistencia en carretera · talleres · flotas/renting · clientes · alquiler de vehículos · OEM/marcas. [V]

---

### 4.7 Valoración de Stock (GANVAM-DAT) + IdentifyVIN — valoración masiva de flota/inventario
"GANVAM-DAT valora automáticamente y sin esfuerzo toda tu flota." [V2 stock + home]

**Campos / capacidades atómicas:**
- **`IdentifyVIN`** — identificación automatizada de cada vehículo por `VIN`. [V]
- `valor de venta` y `valor de compra` por vehículo. [V]
- Valoración basada en `valores de mercado reales` y `transacciones verificadas`. [V]
- `datos actualizados en tiempo real`. [V]
- **`carga masiva de inventario`** (valoración por lotes). [V]
- Capacidades del motor (DAT Group ES): `Predicción del Valor Futuro`, `valoración a diferentes fechas`, `análisis de rotación de stock`, `previsión de margen comercial`, valoraciones `pre/intermedia/post-proceso`. [V] datgroup ES

**Casos de uso:** cumplimiento financiero/contable y fiscal, transparencia, estrategia de promociones/renovaciones, eficiencia fiscal. [V]
**Target:** peritos, empresas de renting, concesionarios. [V]

---

### 4.8 Índice GANVAM-DAT — índice trimestral de mercado y retención de valor residual (MUY relevante para cardeep)
Referencia oficial en España del valor del vehículo usado; publicación **trimestral**. [V2 art_indiceganvam + art_hibrido]

**Métricas atómicas que publica el índice** (con cifras reales como prueba de existencia del campo):

*Volumen de mercado:*
- `volumen total de VO vendido` (unidades) — Q1-2026: **701.360 uds**. [V]
- `crecimiento interanual del volumen` (%) — Q1-2026: **+33,2%**. [V]
- `volumen por tramo de antigüedad` (uds) y su `crecimiento %` — tramos **0-1 año** (95.543 uds, +66,45%), **2-5** (141.886, +48,79%), **6-10** (112.864, +40,17%), **>10** (351.067, +19,72%). [V]
- `cuota de mercado por tramo de antigüedad` (%) — >10 años ≈ **50%** del mercado (Q1-2026); ">10 años = 57%" a cierre 2025. [V2] ambos artículos

*Precios:*
- `precio medio del VO` (€) — Q1-2026: **14.237 €** (−1,9% interanual); cierre-2025: **14.850 €** (+3,3% vs 2024). [V2]
- `precio medio de VO hasta 10 años` (€) — Q1-2026: **20.962 €** (−3,5% interanual). [V]
- `precio medio por tramo de antigüedad` (€): 0-1a **23.865 €** (−9,8%), 2-5a **19.412 €** (−4,3%), 6-10a **16.551 €** (−3%), 11-15a **10.580 €** (+1,5%), 15-20a **4.986 €** (−0,6%). [V]
- `precio medio ponderado por motorización` (€, ref. 3 años): Q1-2026 **17.750 €** (−4,29%). [V]

*Retención de valor / valor residual:*
- **`retención de valor a 3 años` (% sobre precio de tarifa) por motorización** — el campo estrella del índice:
  - Híbrido no enchufable (HEV): **66,01%** (Q1-2026) / **68%** (cierre 2025) · precio medio 21.891 € / 21.352 €. [V2]
  - Gasolina: **58,13%** (Q1-2026) / **60,2%** (cierre 2025, ref. 60.000 km) · 15.991 € / 16.153 €. [V2]
  - Diésel: **54,84%** / **58,3%** · 22.329 €. [V2]
  - Híbrido enchufable (PHEV): **58,10%** / **59,4%** · 29.829 € / 30.734 €. [V2]
  - Eléctrico puro (BEV): **46,01%** / **48%** · 20.766 € / 21.884 €. [V2]
- `precio medio absoluto por motorización` (€). [V]
- Referencia metodológica estandarizada: **3 años + 60.000 km** (gas/híbrido/eléctrico) y **90.000 km** (diésel). [V2]

**Uso operativo del índice (declarado):** fijar `precio de reventa`, calcular `cuotas de financiación/renting`, ajustar `criterios de tasación`, `rotación de stock` y `políticas de recompra`. [V]

---

### 4.9 SilverDAT® Connect — vehículo conectado (dato dinámico para renting/flota)
"Integra identificación y configuración por VIN + datos dinámicos del vehículo conectado en un único flujo." [V] art_renting

**Campos atómicos:**
- `kilometraje real` (telemetría del vehículo conectado). [V]
- `estado real del vehículo`. [V]
- `necesidades de mantenimiento`. [V]
- `valor actual` y `valor residual (RV)` recalculados con dato real. [V]
- Conexión `activable/desactivable bajo demanda`; entornos `multi-OEM`. [V]
- Métricas de uso real para `reporting ESG / CSRD`. [V]
- Sin hardware adicional. [V]

**Impactos declarados:** optimización del valor residual, mantenimiento proactivo, planificación/remarketing, sostenibilidad/reporting. [V]

---

### 4.10 (Motor) SilverDAT® Identify-Code® / €uropa-Code® — base de identificación
Base de datos de identificación inequívoca subyacente a todos los módulos. [V2 INESE + búsqueda datgroup]

**Campos atómicos del registro de vehículo:**
- `marca` / `modelo` / `versión` (cobertura **73 marcas, 2.000+ modelos**). [V2]
- `equipamiento de serie` y `opcional`. [V2]
- `precios` (incl. `PVP`). [V2]
- `datos técnicos` (motor, etc.). [V2]
- `emisiones` (CO₂). [V2]
- `pesos`. [V2]
- `€uropa-Code` / `Identify-Code` (código de identificación del fabricante). [V]

---

## 5. Metodología / fuentes de dato

- **Entidad neutral GANVAM-DAT**: "facilita un valor de referencia a partir del análisis de **precios reales de transacción** y **precios de oferta**, entre otras fuentes." [V2] art_hibrido + autospare
- **Precios reales de transacción** registrados por **distribuidores y entidades financieras**. [V2] autospare + posventa
- **Precios de oferta** de las distintas **plataformas online**. [V] autospare
- DAT Group ES matiza el sesgo: valoraciones basadas en "**informes de transacciones de ventas reales y NO en precios publicados en internet**" — i.e. la transacción real es el ancla; el precio de oferta es contexto. [V] datgroup ES (nota: ligera tensión de énfasis entre las dos fuentes; ambas citadas)
- **Neutralidad institucional**: GANVAM (patronal española de vendedores) + DAT Group → "análisis imparcial, con total neutralidad". [V2]
- **IA + visión por computadora** sobre base **SilverDAT®** para peritación de daños (FastTrackAI). [V]
- **Codificación oficial del fabricante** (€uropa-Code/Identify-Code) y **base de datos oficial del fabricante** para identificación/specs. [V2]
- **SoH de batería** (diagnóstico de salud) para ajustar valor de VE. [V] INESE
- **Dato conectado** (telemetría: km real, estado) vía SilverDAT Connect para afinar valor residual. [V]
- Periodicidad del índice: **trimestral**; punto de referencia normalizado 36 meses / 60-90k km. [V2]
- Frecuencia de refresco de los valores de tasación: "datos actualizados en tiempo real" (declarado), sin cadencia exacta publicada. [V parcial]

---

## 6. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Plataforma web / multisoporte** | weDAT®, fastVO, fastEquipments, myClaim: web responsive, **sin instalar nada**, multidispositivo (`Móvil`) | [V2] |
| **Móvil / fotográfico** | FastTrackAI® por carga de imágenes (análisis fotográfico guiado) | [V] |
| **Informes** | `informe de valoración` customizable (formato/flujo/permisos configurables por usuario) | [V] fastvo |
| **Carga masiva** | `carga masiva de inventario` para valoración de stock/flota por lotes | [V] stock |
| **Integración entre sistemas** | "integración estandarizada, segura y en tiempo real", conectando todos los actores del ciclo de vida; compatible con **SilverDAT3**, DMS y procesos de peritación de terceros | [V] art_semanaseguro |
| **API pública** | **NO publicada** — no hay documentación REST/SOAP abierta; la integración se entrega como "solución estandarizada" bajo acuerdo (mismo patrón que el grupo DAT) | [NO-VERIFICADO/[ASUMIDO] por analogía con grupo] |
| **Vehículo conectado** | SilverDAT Connect: feed de telemetría multi-OEM, activable bajo demanda | [V] |
| **Publicaciones** | Índice GANVAM-DAT trimestral (notas/artículos en `discover.datiberica.com/actualidad`) | [V] |
| **Captación comercial** | Todo el sitio empuja a "Solicita tu demo" (formulario lead); no hay autoservicio de alta online | [V] |

---

## 7. Modelo de precio

- **NO publicado.** Ninguna página de DAT Ibérica muestra tarifas; el sitio es 100% lead-gen ("Solicita tu demo / Más info"). [V — verificado por ausencia en las 17 páginas]
- Por analogía con el grupo, el motor **SilverDAT** se comercializa en Alemania por **suscripción 12 meses + cuota base mensual + pago por transacción** (VIN, cálculo, valoración) — ver informe DAT Deutsche §7. Aplicabilidad a la tarifa española: **[ASUMIDO, no verificado para ES]**. [ASUMIDO]
- El **valor GANVAM-DAT** se posiciona como referencia sectorial neutral (posible licenciamiento institucional vía GANVAM); modelo económico exacto no descubierto. [NO-VERIFICADO]

---

## 8. Patrón de COLOCACIÓN (lo que cardeep imita)

> El sitio es marketing (sin capturas de la app viva). El placement se deriva del **flujo descrito por producto** + el patrón SilverDAT del grupo (informe DAT Deutsche §8). Marcado [flujo] cuando se infiere del producto, no de una pantalla publicada.

| Dato | DÓNDE lo coloca DAT Ibérica | Estado |
|---|---|---|
| Identificación + ficha técnica + equipamiento + PVP | **Cabecera de entrada por matrícula/VIN** → panel de "identidad del vehículo" autorrellenado al instante (fastEquipments); precede a cualquier valoración o cálculo | [flujo] |
| `valor de compra` + `valor de venta` GANVAM-DAT | **Panel de resultado de valoración**: las dos cifras protagonistas (compra/venta) tras identificar (fastVO/fastValuate) | [flujo] |
| `equipamiento de serie / opcional` + ADAS | **Bloque desplegable de equipamiento** bajo la identificación; base del ajuste de valor | [flujo] |
| `valor de mercado` por VIN en lote | **Grid de stock** con valoración masiva por filas (Valoración de Stock + IdentifyVIN); carga masiva → columnas compra/venta | [flujo] stock |
| `retención de valor a 3 años` por motorización + precio medio | **Dashboard/artículo trimestral del Índice GANVAM-DAT**: tiles por motorización (HEV/gasolina/diésel/PHEV/BEV) + series por tramo de antigüedad | [V] art_indiceganvam |
| `precio medio` y `volumen` por tramo de antigüedad | **Informe del Índice** (tablas por tramo 0-1/2-5/6-10/11-15/15-20 años) | [V] |
| Daño + `piezas/operaciones/costes/presupuesto` | **Pantalla de siniestro FastTrackAI**: carga de fotos → IA marca daños → desglose de piezas/operaciones/coste → presupuesto detallado | [V] flujo 3 pasos |
| `estado del siniestro` + trazabilidad | **Timeline colaborativo de myClaim**: estado en tiempo real visible para todos los actores, fase a fase | [V] myclaim |
| `km real` + `valor residual` recalculado | **Vista de activo conectado (SilverDAT Connect)**: telemetría → RV dinámico, para renting/flota | [V] art_renting |
| Documento / informe | **Informe de valoración customizable** (formato configurable) | [V] fastvo |

**Patrón maestro DAT Ibérica → cardeep:** (1) cabecera de identidad por matrícula/VIN con equipamiento + PVP → (2) dos cifras GANVAM-DAT protagonistas (compra/venta) → (3) bloque de equipamiento/ADAS que justifica el ajuste → (4) modo "stock" con grid masivo por VIN → (5) **dashboard de índice de mercado por motorización y antigüedad** (retención de valor a 3 años) → (6) flujo de siniestro foto→IA→presupuesto → (7) timeline colaborativo de expediente. El sello **GANVAM-DAT** es el "marchamo de neutralidad" que cardeep debería emular como autoridad-de-dato.

---

## 9. Diferencial (lo que DAT Ibérica ofrece y pocas/ninguna otra en ES)

1. **Sello GANVAM-DAT** = **valor de referencia OFICIAL del VO español**, avalado por la patronal GANVAM + neutralidad DAT. Autoridad institucional difícil de replicar (igual que cardeep busca ser censo-autoridad). [V2]
2. **Índice GANVAM-DAT trimestral** con **retención de valor a 3 años por motorización** (HEV/gasolina/diésel/PHEV/BEV) normalizada a 36 meses/60-90k km — métrica residual pública y comparable. [V2]
3. **Dato de transacción real** (registrado por distribuidores **y entidades financieras**) como ancla, no solo precios de oferta online. [V2]
4. **Suite end-to-end en español**: identificación → valoración GANVAM-DAT → cálculo de reparación (EUROLACK) → peritación IA → siniestro colaborativo → vehículo conectado. [V2]
5. **SoH de batería** integrado en la valoración de VE. [V]
6. **ADAS** identificados a nivel de opcional por matrícula/VIN (relevante para coste de reparación y valor). [V2]
7. **Respaldo del motor europeo DAT** (73 marcas/2.000+ modelos, base oficial de fabricante) bajo marca local. [V2]
8. **FastTrackAI fotográfico** en español para peritación instantánea desde el móvil. [V]
9. **SilverDAT Connect** (dato conectado multi-OEM, activable) para RV dinámico en renting. [V]

---

## 10. Gaps (lo que DAT Ibérica NO ofrece / debilidades)

1. **No es proveedor de historial de vehículo** (siniestros previos, titularidades, fraude de km consolidado, procedencia tipo HPI/CARFAX). Captura km en valoración, no un registro histórico. [V por ausencia]
2. **No publica `días-para-vender` / `market days supply` por unidad** ni un `price-to-market %` numérico por anuncio (a diferencia de Indicata/vAuto). Su índice es agregado de mercado, no instrumento por ficha. [V por ausencia]
3. **Cobertura solo España** (el resto del mundo lo cubren otras filiales DAT). [V2]
4. **Sin tarifa pública** — todo "bajo demanda/demo"; fricción de evaluación. [V]
5. **Sin API/documentación pública** para desarrolladores; integración mediada por acuerdo. [NO-VERIFICADO público]
6. **Sitio comercial ligero** (marketing WordPress): no expone profundidad de campos ni la app viva; muchos campos atómicos hay que inferirlos del motor del grupo o de INESE, no del sitio ES. [V]
7. **No expone datos de subasta/wholesale en vivo** ni arbitraje cross-plataforma. [V por ausencia]
8. **Campos de daño avanzados (POI, siniestro total, residual del siniestrado)** no publicados en la versión ES de FastTrackAI (sí en el grupo DE). [V por ausencia en ES]
9. **Indicador demanda/oferta y velocidad de rotación granular por modelo/región** no es producto; solo lecturas agregadas del índice. [V por ausencia]
10. **Inconsistencias de cobertura entre fuentes** (29-30 marcas en logos vs 50 en lanzamiento vs 73 en motor Identify-Code) — el dato comercial visible subrepresenta el motor real. [V — reportado, no resuelto]

---

## 11. Fuentes (URLs)

**DAT Ibérica directas (primarias, `discover.datiberica.com`):**
- `https://discover.datiberica.com/` — home, catálogo, verticales, identidad/HQ, alianza GANVAM-DAT, índice (actualidad)
- `https://discover.datiberica.com/wedat/` — weDAT®: identificación, valor GANVAM-DAT (turismos/VIL/SUV/motos), recambio OEM/IAM/verde, baremos de pintura
- `https://discover.datiberica.com/fastvo/` — fastVO: matrícula/VIN, datos técnicos, equipamiento serie/opcional, valor de mercado, informe customizable
- `https://discover.datiberica.com/fastequipments/` — fastEquipments: equipamiento original/opcional, configuraciones de fábrica, detección automática de opcionales, PVP
- `https://discover.datiberica.com/fasttrackai/` — FastTrackAI: imágenes→IA→piezas/operaciones/costes→presupuesto; base SilverDAT
- `https://discover.datiberica.com/myclaim/` — SilverDAT myClaim: actores, estado en tiempo real, trazabilidad, ciclo notificación→liquidación→recuperación
- `https://discover.datiberica.com/valoracion-de-stock-vehiculos/` — Valoración de Stock GANVAM-DAT + IdentifyVIN, carga masiva, valor compra/venta
- `https://discover.datiberica.com/art_indiceganvam/` — Índice GANVAM-DAT Q1-2026: volumen, precios y retención por tramo y motorización
- `https://discover.datiberica.com/art_hibridonoenchufable/` — Índice cierre-2025: retención por motorización (68% HEV), metodología "transacción real + oferta"
- `https://discover.datiberica.com/art_optimizargestionrrenting/` — SilverDAT Connect: dato conectado, km real, RV dinámico, ESG/CSRD
- `https://discover.datiberica.com/art_datibericasemanaseguro/` — weDAT (EUROLACK, FastTrackAI), fastEquipments (ADAS/codificación), fastValuate (valores compra/venta GANVAM-DAT, remarketing)
- `https://discover.datiberica.com/{talleres,vehiculos-de-ocasion,renting,aseguradoras,concesionarios,flotas}/` — verticales (necesidades por cliente, ciclo renting, fraude aseguradoras)

**Secundarias / verificación cruzada:**
- `https://directorio.inese.es/dat-iberica/` — perfil sector seguros: DAT Group 1931, Identify-Code/€uropa-Code (73 marcas/2.000+ modelos, ADAS, emisiones, pesos), fastValuate (20 años, SoH VE), dirección (Luis Murias), contacto
- `https://autospare.es/motor/acuerdo-ganvam-y-dat/` — alianza GANVAM-DAT **26-ene-2024**, metodología (transacción real + oferta), 36 meses/60.000 km, ejemplo 71,5% retención
- `https://www.posventa.com/...nace-ganvam-dat...` — nacimiento de GANVAM-DAT como entidad neutral
- `https://www.datgroup.com/es-es/productos-1/valoracion-de-vehiculo-usado/` — motor SilverDAT ES: tipos (turismos/SUV/motos/VCL ≤3,5t/camiones), Predicción del Valor Futuro, valoración a fechas, rotación, margen, "transacciones reales no internet"
- `https://www.datgroup.com/es-es/productos-1/{vin-request,silverdat-3}/` y `https://www.datgroup.com/products/vehicle-identification/` — identificación/€uropa-Code (cobertura, ADAS)
- `https://www.infotaller.tv/chapa_y_pintura/dat-iberica-software-fasequipments-fastvo-congreso-faconauto_0_1191180900.html` — lanzamiento fastEquipments/fastVO (50 marcas, matrícula/VIN, SilverDAT3)
- `https://ganvam.es/expoganvam/expo-ganvam-2024/` + YouTube "Camino a eXpo GANVAM 2024 - Luis Murias" — liderazgo Luis Murias (DG DAT Ibérica)
- `https://infonif.economia3.com/ficha-empresa/dat-automovil-iberica-sl` — NIF B62394762

---

### Notas de verificación
- **Cobertura de marcas**: 29-30 (logos home, marketing) vs 50 (lanzamiento Infotaller) vs **73 marcas/2.000+ modelos** (motor Identify-Code, INESE+datgroup). La cifra autoritativa del motor es **73**; las menores son subconjuntos comerciales/de época. Reportado, no resuelto.
- **Año de constitución de la SLU** española: NO verificado (existe con NIF B62394762).
- **Año exacto del lanzamiento Faconauto** de fastVO/fastEquipments: la edición "XXVII" y su año no se fijan con confianza desde una sola fuente; DAT Ibérica fue patrocinador oro de **Faconauto 2025** y presentó "nueva generación" de fastVO. Se evita anclar un año duro no verificable.
- **Campos de daño FastTrackAI** (POI, siniestro total, residual): existen en el producto del grupo alemán; NO publicados en la página ES. Marcados como heredado-grupo, no-publicado-ES.
- **Cifras del índice**: dos cortes temporales (Q1-2026 y cierre-2025) → los % difieren por trimestre; ambos citados con su periodo. No son contradicción.
- **Precio**: ausencia total de tarifa en ES verificada; modelo del grupo citado como [ASUMIDO] no extrapolable con certeza.
