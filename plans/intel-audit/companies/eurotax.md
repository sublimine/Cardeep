# Auditoría atómica — Eurotax (JD Power / Autovista Group)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de datos/valoración de automoción. Web: https://eurotax.es/ (marca local "JD Power Eurotax ES").
> Fecha auditoría: 2026-06-30. Método: navegación exhaustiva del sitio ES + sitio de grupo autovista.com + PDFs de producto (Guía Market Radar, FAQ AutowertNet) extraídos con PyMuPDF + verificación cruzada con prensa (JD Power, BusinessWire, Crunchbase).
> Convención: [V] = verificado leyendo la fuente · [A] = asumido/inferido (marcado siempre).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | Eurotax (rebrandeada en la web a **"JD Power Eurotax ES"**) | [V] |
| Grupo / owner | **Autovista Group** (marcas: Autovista, Eurotax, Glass's, Schwacke, Rødboka, EV Volumes) | [V] |
| Owner último | **J.D. Power** (respaldada por el fondo **Thoma Bravo**); adquisición de Autovista Group anunciada el **12-sep-2023**, cierre posterior (~2024) | [V] |
| Owner anterior | **Hayfin Capital Management** (gestora europea de activos alternativos) | [V] |
| Raíces históricas | Construida sobre los pioneros **William Glass** (Glass's, UK) y **Hans Schwacke** (Schwacke, Alemania). Eurotax lanzada como filiales en Bélgica, Italia, Países Bajos y Suiza por **Helmuth H. Lederer** | [V] |
| Hitos corporativos | 1998 Hicks, Muse, Tate & Furst compra Glass's Information Systems; 2000 compra Eurotax AG → fusión en **EurotaxGlass's AG**, registrada en **Freienbach (Suiza)**. Rebrand posterior a Autovista Group (negocio puramente digital) | [V] |
| "Pioneros desde" | Insights basados en datos "desde principios de los años 1930" (claim de grupo) | [V] |
| Entidad / soporte ES | Operación española vía eurotax.es; contacto soporte **customer@eurotax.es** (FAQ) y **customer@autovistagroup.com** (suscripciones) | [V] |
| HQ grupo | Raíz suiza (Freienbach). HQ operativo de Autovista Group habitualmente citado en Londres | [A] |
| Categoría | Datos e inteligencia de automoción: identificación de vehículos, especificaciones, valoración, valores residuales, previsión, costes de reparación/mantenimiento, TCO, datos EV | [V] |

### Clientes objetivo (9 sectores declarados)
[V] Concesionarios · Fabricantes e importadores (OEM) · Flotas y finanzas (leasing/renting/financieras) · Aseguradoras · Talleres y peritos · Remarketing · Servicios profesionales (consultoría) · Administración pública · Telemática.

---

## 2. Cobertura

### Geográfica (varía por producto) [V]
- **AutovistaVALUATION**: 15 mercados europeos.
- **Compare**: 15 mercados.
- **Residual Value Monitor**: 17 mercados.
- **Residual Value Intelligence**: 7 mercados europeos.
- **AutovistaREFORECAST**: 13 mercados.
- **Car Cost Expert**: 12 mercados (Alemania, España, Francia, Italia, Reino Unido, Bélgica, Países Bajos, Austria, Suiza, Polonia, Chequia, Rumanía).
- **Car to Market**: 20 países, 750+ expertos.
- **EV Volumes**: más de 130 mercados.
- Identificación: 99% de vehículos identificables solo con el código de matriculación; cobertura de especificación 99% del parque europeo incluyendo eléctricos e híbridos; precisión >97% del parque europeo.

### Scope de vehículos [V]
- **Tipos**: Turismo, Todo terreno (SUV), Vehículo comercial ligero / LCV (hasta 3.500 kg P.M.A.), Motocicletas (solo en AutovistaVALUATION).
- **Nuevo y usado** (VN y VO). Valoración de VO hasta **15 años** de antigüedad (AutowertNet/Eurotax).
- **Powertrains**: combustión, híbridos (HEV/MHEV/PHEV), eléctricos (BEV), FCEV (en EV Volumes).
- **Exclusiones explícitas** (AutowertNet): vehículos de gama alta de baja comercialización, vehículos de importación, motocicletas y vehículos industriales > 3.500 kg P.M.A.

---

## 3. Productos + campos atómicos

Catálogo completo (17 productos/módulos enumerados desde `product-sitemap.xml` + plataforma AutowertNet + features Market Radar/Repair Estimate).

### 3.1 Eurotax / AutowertNet (plataforma web principal de VO en España)
Reúne valoración, identificación, daños, stock y broadcasting. Módulos: Vehicle Identification, Valuation, **Market Radar**, **Repair Estimate** ("Speedy-Zone"), Broadcasting, Stock Management, User Administration ("Mi cuenta"). [V]
Campos/funciones:
- Identificación precisa del vehículo (incluye todas las opciones y paquetes de opciones).
- Identificación por matrícula o bastidor (VIN) en un único paso.
- Tipos: Turismo / SUV / LCV ≤3.500 kg.
- Valoración de VO hasta 15 años de antigüedad.
- Valor en el pasado (histórico).
- Valores de compra y de venta.
- Ajustes definidos por el cliente.
- Ajuste por antigüedad y kilometraje.
- Valoración de equipamiento y opciones.
- Herramienta de valoración de daños (Repair Estimate).
- Registro de ofertas, transacciones y contactos.
- "Valoraciones existentes" con usuario creador.
- Datos del cliente en la valoración impresa.
- Broadcasting de anuncios a portales.
- Control de stock comercial.
- Campos obligatorios valoración: fecha de matriculación, tipo de vehículo, marca, modelo, kilometraje, matrícula.

### 3.2 Market Radar (módulo de inteligencia de mercado en tiempo real dentro de Eurotax)
Compara ofertas de VO en portales clasificados, elimina ofertas fantasma/particulares/precios trampa, y entrega el **valor SPOT**. [V]
Campos:
- **Valor SPOT** (valor de oferta VO más actualizado y exacto para la región del usuario, en tiempo real; basado en ofertas online de la región delimitada).
- Diferencia precio de oferta vs valor SPOT (delta, p.ej. +2.810€ / −2.010€ / −20€).
- **Media de días para la venta** (indicador de deseabilidad/rotación).
- **Días que lleva anunciado** cada vehículo (con historial: nº de cambios de precio y fechas, al pasar el cursor).
- Indicador de demanda/deseabilidad (ALTA / MEDIA).
- Posición de su vehículo en el mercado.
- Grado de semejanza (Estrella=igualdad exacta por códigos Eurotax / Verde=muy alta / Amarillo=alta / Rojo=media).
- Ofertas VO vs vehículos ya vendidos (pestañas).
- Precio del vehículo de cada anuncio competidor.
- Radio de búsqueda (área/región/nacional) o código postal.
- Nº de ofertas/listados (sin límite de búsquedas).
- Filtro por palabras clave y por rango de kilómetros.
- Enlace al anuncio original en el portal (icono cámara).

### 3.3 AutovistaVALUATION (feed de valores residuales) [V]
- Valores residuales (turismos, LCV, motocicletas).
- Kilometraje medio.
- Cobertura 99% de vehículos y LCV, 15 mercados europeos.
- Feed único armonizado (codificación de vehículo única paneuropea).
- Casos: cálculo de pérdida total (aseguradoras), valoración de flota, gestión de riesgo de leasing, posicionamiento competitivo.

### 3.4 Autovista API (AutovistaAPI) — 6 módulos de datos vía API [V]
- **Identification**: conjuntos completos de datos, código único de vehículo, identifica todos los vehículos europeos.
- **Specification**: alineación del motor, pesos, número de tiempos, otras entradas del fabricante.
- **Valuation**: datos de valoración y precio exactos.
- **Prediction**: predicciones de valores residuales.
- **Technical**: información técnica de cualquier vehículo europeo (incluye EV/híbridos).
- **Cost Data**: costes técnicos, de especificación y de reparación a lo largo del ciclo de vida.
- Entrega a sistemas del cliente vía API; cloud, pago por uso.

### 3.5 VIN API [V]
- Input: VIN.
- Equipamiento instalado de fábrica.
- Paquetes extra.
- Historial completo del vehículo (perfil completo a partir de datos OEM).
- Equipamiento de serie.
- Emisiones.
- Consumo.
- Dimensiones.
- Rendimiento del motor (potencia).
- Actualización mensual; compatible con resto de productos Autovista.
- Casos: leasing pricing, trade-in, coste de reparación, valoración, gestión de inventario.

### 3.6 AutovistaSPEC (datos de especificación) [V]
- Hasta 20 años de histórico de especificaciones.
- Datos estandarizados entre marcas.
- Configurador multimarca (estructura consistente).
- Tipos de motor / especificaciones de motor.
- Datos técnicos del vehículo.
- EV/híbridos: tiempo de carga, autonomía/rango, capacidad de batería.
- Entrega: importación CSV a cualquier BBDD (scripts de creación de BBDD + guías de integración).

### 3.7 Forecast Web (previsión de VR para contratos de leasing) [V]
- Previsión de VR para fijar posición de riesgo al inicio del contrato.
- Valoración de mercado actualizada al final del contrato (remarketing).
- Depreciación de extras opcionales (cálculo individual).
- Parámetros de depreciación de equipamiento especial (individual o alineado a mercado).
- Horizontes: VN hasta 6 años/400.000 km; VO hasta 6 años, edad máx 10 años/400.000 km; LCV nuevo hasta 6 años/550.000 km; LCV usado hasta 6 años, máx 10 años/550.000 km.
- Comparación contra observaciones de mercado local (inflación, escasez de suministro, regulación).

### 3.8 Reforecast / Reforecast Online [V]
- Re-evaluación del rendimiento de contratos "en un clic".
- Valoración con depreciación de extras opcionales genuinos (valores de compra y reventa).
- Parámetros de depreciación de equipamiento especial (comerciabilidad).
- Valoraciones y previsiones para terminación anticipada de contrato (valor justo).
- Evaluación de inventario en cualquier momento/dispositivo.

### 3.9 AutovistaREFORECAST (feed de re-previsión) [V]
- Valor actual y futuro del vehículo (hasta 10 años de proyección).
- Re-valoraciones ilimitadas durante la suscripción.
- Multi-escenario: mismo vehículo a distintas edades/kilometrajes.
- Previsión de VR alineada a fecha elegida.
- Valoración ajustada por edad y kilometraje.
- Enriquecimiento con datos de especificación; salida CSV estandarizada.
- Cobertura 99% turismos+LCV, 13 mercados. Casos: Basilea II, valoración de capital, remarketing.

### 3.10 Compare (comparación de VR real vs previsto en Europa) [V]
- Comparación de VR reales y previstos a nivel nacional e internacional.
- Observaciones reales de mercado (monitorización regional de factores económicos locales).
- Gráfico de evolución de VR (subida/bajada en el tiempo).
- Oportunidades de remarketing actuales y futuras entre mercados.
- Escala: 100.000 vehículos nuevos, 200.000 usados, 15 mercados. Actualización mensual.

### 3.11 Residual Value Intelligence [V]
- Tendencias de VR en principales mercados europeos.
- VR por marca, segmento y tipo de combustible.
- Histórico hasta 4 años.
- Previsión de evolución a horizonte 3 años.
- Benchmark de VR vs competidores.
- Vehículos con mayor VR y menor coste de propiedad.
- Cobertura: 42 marcas, 14 segmentos, 7 mercados.
- UI: dashboards personalizables, gráficos con código de color, pestañas filtrables, comparación rápida desde home.
- Leasing: calcula ~85% de las cuotas de leasing.

### 3.12 Residual Value Monitor [V]
- Seguimiento de tendencias de VR entre mercados europeos.
- Histórico hasta 4 años.
- Benchmark comparativo individual vs competidores.
- Dashboards/paneles personalizados.
- Cobertura: 38 marcas, 17 mercados.
- Flujo de 5 pasos: seleccionar modelos → ranking por rendimiento → comparar flota vs competidores → variaciones por periodo → causas de variación de VR (facelifts, efecto lanzamiento).
- Precios de venta por región + media de días para vender (decisión de dónde comercializar).

### 3.13 Car to Market (consultoría pre-lanzamiento de VR para OEM) [V]
- Evaluación y mejora del VR antes del lanzamiento (hasta 4 años antes).
- 3 fases: Fase 0 conceptualización → Fase 1 estrategia de producto → Fase 2 previsión final de VR por variante (powertrains y niveles de acabado).
- **16 drivers de VR analizados**: fortalezas/debilidades del concepto; calidad percibida; feedback de mercado; estrategia go-to-market; niveles de equipamiento; planificación de volumen; estructura de incentivos; usabilidad diaria; autonomía; capacidad de carga; eficiencia de coste; benchmarks de rendimiento; consumo de combustible; consumo de energía; rendimiento de VR de marca; posicionamiento competitivo.
- Base: millones de datos de coches usados + miles de observaciones reales. Cubre 65% de lanzamientos europeos.

### 3.14 Car Cost Expert (coste total de propiedad / TCO) [V]
- Cálculo y simulación de TCO.
- Componentes: depreciación, equipamiento y accesorios, costes de mantenimiento, gastos operativos (combustible/energía), seguro/impuestos [parcial].
- 600+ gamas de modelos, 12 mercados, 300+ combinaciones kilometraje/edad.
- Entrada de valores propios del cliente.
- Salida: export Excel, informe PDF, dashboard con desglose de TCO.

### 3.15 AutovistaREPAIR (datos de reparación, compatible TecDoc) [V]
- Cálculo preciso de coste de reparación de cualquier vehículo.
- Precios de piezas originales OEM.
- Previsión de piezas de desgaste (para TCO).
- Visualizaciones gráficas interactivas de componentes (identificación por clic).
- Diagramas de taller para localizar piezas.
- Datos de pintura (fuente **AZT**, opcional).
- Código de catálogo de piezas TecDoc.
- Soporte en idioma local; datasets mejorados con ML.

### 3.16 AutovistaSMR (Service, Maintenance & Repair, compatible TecDoc) [V]
- Tiempos de servicio OEM.
- Piezas de mantenimiento.
- Costes de mano de obra / tiempos de mano de obra.
- Calendario de mantenimiento (previsión) y predicción de reparación anual.
- Estimación de piezas de desgaste (para TCO).
- Precios de recambios + tiempos de mano de obra asociados.
- Programación de mantenimiento (flota road-ready).
- ML sobre datos crudos; idioma local; TecDoc (opcional).

### 3.17 EV Volumes (datos e inteligencia de eléctricos) [V]
- Ventas de EV por OEM y modelo.
- Tamaño de mercado y penetración.
- Tracker de ventas mensual.
- Powertrains: BEV, PHEV, FCEV, HEV, MHEV.
- Envíos de baterías (kWh) por fabricante y OEM.
- Química de celda de batería y composición de cátodo.
- Identificación de fabricante de celda.
- Ruteo geográfico de envíos de batería por país.
- Futuros lanzamientos de modelos.
- Expansión de infraestructura de carga.
- Instalaciones por tipo de conector por país.
- Especificaciones EV granulares y precios.
- 130+ mercados, actualización mensual; export Excel/PDF/CSV.

### 3.18 Data & API Solutions (capa de entrega de datos) [V]
- Identificación por VRM/VIN/NatCode (99% solo con código de matriculación).
- Especificaciones técnicas con códigos NatCode.
- Histórico de precios 20 años.
- Valores de mercado en tiempo real.
- Previsión de VR hasta 120 meses.
- Costes de servicio/mantenimiento.
- Precios de piezas y mano de obra por matrícula.
- Valoraciones ajustadas por km (16 combinaciones edad/kilometraje).
- Datos de piezas OEM.
- Entrega: API (cloud, pago por uso), data feeds (bulk), carga masiva VIN.

---

## 4. Metodología y fuentes de datos [V]
- **Reuniones editoriales mensuales**: el equipo analiza sectores/fabricantes/modelos de mayor rendimiento y calcula valores de depreciación; revisión por anomalías.
- Espectro: desde previsiones iniciales de modelos en preproducción hasta valores de VO de coches de 10+ años.
- **Codificación de vehículo única paneuropea** (código Eurotax / NatCode) que armoniza datos independientes del sector.
- **Valor SPOT vs valor base Eurotax**:
  - *SPOT* = sobre ofertas VO online de la región delimitada por el usuario, en tiempo real (lo que se pide).
  - *Base Eurotax* = sobre ventas efectivamente realizadas, a valores reales, en todo el territorio nacional, en el mes anterior (lo que se paga).
- Fuentes: portales clasificados de VO (listados online), datos OEM, observaciones reales de mercado, transacciones, 20+ años de histórico; pintura vía AZT; piezas vía TecDoc.
- **Recursos humanos + IA**: ~400 especialistas (grupo) / 750+ expertos (Car to Market) + modelado estadístico avanzado + IA/ML; benchmarking contra transacciones reales; ajustes por mercado regional.
- **Frecuencia**: API/valores de mercado actualizados **a diario**; especificaciones, Compare, EV Volumes y VIN API **mensual**; Market Radar **diario/tiempo real**.
- Eliminación de ruido: Market Radar filtra ofertas fantasma, anuncios de particulares y precios trampa.

---

## 5. Entrega
[V] Modalidades:
- **Plataformas web/cloud** (login portal): AutowertNet/Eurotax, Compare, Forecast Web, Reforecast Online, Residual Value Intelligence, Residual Value Monitor, Car Cost Expert, Market Radar (abre página de resultados en nueva pestaña del navegador).
- **API REST/cloud** (pago por uso): Autovista API (6 módulos), VIN API.
- **Data feeds / bulk**: AutovistaVALUATION, AutovistaREFORECAST, AutovistaSPEC (CSV), AutovistaREPAIR, AutovistaSMR.
- **Ficheros**: CSV (SPEC/REFORECAST), Excel + PDF (Car Cost Expert, EV Volumes), informe PDF (Car to Market).
- **Integración DMS / sistemas del cliente** vía API y feeds estandarizados.
- **Broadcasting** a portales clasificados (salida de anuncios).
- Históricamente: **SOAP web services** (`webservices.eurotaxglass.com/wsdl/identification.wsdl`) [V — endpoint legacy hallado en búsqueda].

---

## 6. Precio
- **No público**. No hay página de tarifas; modelo por **suscripción** (nº de usuarios ligado al tipo de suscripción en AutowertNet) y **API pago por uso**. Cotización vía contacto (customer@autovistagroup.com). Prueba gratuita ("acuerdo de prueba") disponible en varios productos. [V que no es público; importe = GAP]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. Mapeo pantalla → dato.

### AutowertNet — Pantalla de valoración [V]
- **Parte superior / formulario**: campos obligatorios (fecha de matriculación, tipo de vehículo, marca, modelo, kilometraje, matrícula). Selector de lista de versiones.
- **Parte inferior de la pantalla**: resultado de la valoración (valores de compra/venta) tras "Guardar y actualizar valoración".
- **Lista "Valoraciones existentes"**: cada fila muestra el usuario creador.
- **Impresión**: datos del cliente + nombre/apellidos del usuario que imprime, automáticos.
- **Menú "Mi cuenta" → Administrar usuarios**: gestión de usuarios/contraseña/idioma/contacto.

### Market Radar — Pantalla "Resultado de la búsqueda" (11 elementos documentados) [V]
1. **Posición de su vehículo** (destacada respecto a la competencia).
2. **Lista de vehículos similares** (resultados de la búsqueda).
3. **Código de color de semejanza** por fila: Estrella (exacta), Verde (muy alta), Amarillo (alta), Rojo (media).
4. **Pestañas** para alternar entre *ofertas VO* y *vehículos ya vendidos*.
5. **Media de nº de días para la venta** (indicador de deseabilidad) — métrica agregada destacada.
6. **Vista gráfica** de diferencias entre precios de oferta y valor SPOT.
7. **Gráfico comparativo** precio de oferta vs valor SPOT por vehículo.
8. **Días anunciado** por fila (hover → historial de cambios de precio y fechas).
9. **Filtro por palabras clave** (arriba a la izquierda).
10. **Radio de búsqueda** / territorio nacional (control de área); afinado por rango de km.
11. **Icono de cámara** por fila → abre el anuncio original en el portal de origen.
- Acceso a Market Radar: 3 vías (icono junto a la valoración / icono en la fila del vehículo en la lista de Stock / icono dentro de estimación en Stock).

### Listado de competidores (tarjeta de oferta) [V — Guía Market Radar p.1]
Cada tarjeta de anuncio rival muestra: nombre del concesionario · versión + fecha (Audi A4 2.0 TDI 10/2009) · precio (19.500€) · días en stock (169 días) · delta vs SPOT (+2.810€) · badge de demanda (ALTA) · mapa con radio (1 mi / 2 km).

### Residual Value Intelligence — Dashboard [V]
- Dashboards personalizables; gráficos con **código de color** mostrando cambios en el tiempo; **pestañas filtrables** por perspectiva; comparación rápida desde la home; mapa de rendimiento europeo; pestaña de previsión a 3 años.

### Residual Value Monitor — Panel [V]
- Paneles personalizados; vista de **ranking** de modelos por rendimiento; vista de **comparación vs competidores**; vista de **variación por periodo**; identificación de **causas** (facelift, lanzamiento).

### Compare — Vista central [V]
- Comparación nacional/internacional de vehículos similares; **gráfico de forecast** de subida/bajada de VR en el tiempo; visión completa de mercado desde un sistema central.

### Car Cost Expert — Salida [V]
- Dashboard con **desglose de TCO** + exportación Excel / informe PDF.

### Car to Market — Informe pre-lanzamiento [V]
- Informe por fases (0/1/2) con los **16 drivers de VR**; previsión final por variante.

### VIN API / Eurotax — Identificación [V]
- Input VIN o matrícula en **un solo paso** → perfil completo del vehículo con todo el equipamiento de fábrica y opciones.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Valor SPOT en tiempo real por región** sobre listados online limpios (sin particulares/fantasma/trampa) — *junto a* el valor base sobre transacciones reales nacionales: doble verdad "lo que se pide vs lo que se paga".
- [V] **Codificación de vehículo única paneuropea** (NatCode/código Eurotax) que armoniza 15-17 mercados → comparación de VR real vs previsto **transfronteriza** (Compare, RV Monitor/Intelligence) = arbitraje geográfico de remarketing.
- [V] **Cobertura de ciclo de vida 360°** en un solo proveedor: identificación → especificación → valoración → previsión VR → reparación/mantenimiento (SMR) → TCO → datos EV.
- [V] **Consultoría pre-lanzamiento de VR (Car to Market)** hasta 4 años antes con 16 drivers — servicio que va más allá de un dato.
- [V] **EV Volumes**: profundidad de batería (kWh, química de celda, cátodo, fabricante de celda, ruteo por país) y 130+ mercados — raro en competidores de valoración.
- [V] **Días anunciado con historial de cambios de precio** y media de días para la venta como proxy de demanda, integrados en el flujo de tasación.
- [V] Compatibilidad **TecDoc** y datos de pintura **AZT** en reparación.
- [V] Respaldo **OEM-aprobado** para previsión de VR y autoridad de marca centenaria (Glass's/Schwacke/Eurotax) ahora bajo J.D. Power.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Precios no públicos**: ningún importe/tarifa descubrible (solo "contactar").
- [V] **Sin historial de siniestros/accidentes por VIN** (tipo Carfax/autoDNA): ofrecen "full vehicle history" como *perfil de specs*, no historial de daños/propietarios/ITV/km certificado.
- [V] **Sin verificación de kilometraje real** (no detección de fraude de cuentakilómetros).
- [V] **Market Radar no cubre** vehículos de baja comercialización, baja producción, km exagerado o >10 años (no calcula SPOT ahí).
- [V] **AutowertNet excluye** gama alta de baja venta, importaciones, motos y industriales >3.500 kg.
- [V] **Métricas tipo "price-to-market %" y "market days supply"** no nombradas como tales (usan "días para la venta" y delta vs SPOT; no un índice normalizado de price-to-market).
- [A] **Sin marketplace transaccional propio** (no venden el coche; broadcasting a portales de terceros).
- [A] **Documentación técnica de API limitada en público** (no se exponen formatos JSON/XML, auth, rate limits, diccionario completo de campos) — barrera para integradores.
- [A] Cobertura de motos y FCEV muy parcial (motos solo en VALUATION; FCEV solo en EV Volumes).
- [V] Las páginas ES de marketing **rehúsan enumerar** el diccionario de campos (orientadas a beneficio, no a especificación) — opacidad de catálogo de datos.

---

## 10. Fuentes (URLs)
- https://eurotax.es/ — homepage, marca "JD Power Eurotax ES".
- https://eurotax.es/product/eurotax/ — producto Eurotax (campos VO).
- https://eurotax.es/product/autovistavaluation/ — AutovistaVALUATION.
- https://eurotax.es/product/autovistaapi/ — 6 módulos API.
- https://eurotax.es/product/autovistaspec/ — especificaciones.
- https://eurotax.es/product/forecast-web/ — horizontes de previsión.
- https://eurotax.es/product/reforecast/ y /product/autovistareforecast/ — re-previsión.
- https://eurotax.es/product/compare/ — comparación VR.
- https://eurotax.es/product/car-to-market/ y https://autovista.com/product/car-to-market/ — 16 drivers de VR.
- https://eurotax.es/product/car-cost-expert/ — TCO, 12 mercados.
- https://eurotax.es/product/residual-value-monitor/ — 38 marcas/17 mercados.
- https://eurotax.es/product/residual-value-intelligence/ — 42 marcas/14 segmentos/7 mercados.
- https://eurotax.es/product/ev-volumes/ — datos de batería/EV.
- https://eurotax.es/product/autovistarepair/ y /product/autovistasmr/ — reparación/SMR (TecDoc/AZT).
- https://eurotax.es/product/data-api-solutions/ y https://autovista.com/product/data-solutions/ — entrega/feeds, 120 meses, 16 combos km.
- https://eurotax.es/autowertnet-product-support/ — módulos AutowertNet.
- https://eurotax.es/wp-content/uploads/sites/10/2024/06/ES_AutowertNet_FAQ.pdf — FAQ (tipos vehículo, 15 años, campos obligatorios, exclusiones, Market Radar/Repair Estimate).
- https://eurotax.es/wp-content/uploads/sites/10/2023/05/Market-Radar-Guia-de-Inicio-2a-edicion.pdf — **Guía Market Radar** (11 elementos de la pantalla de resultados, valor SPOT, layout de tarjetas).
- https://eurotax.es/valoracion-y-tasacion/como-puedo-conocer-los-precios-de-venta-en-tiempo-real-de-mi-zona/ — Market Radar / SPOT / días en stock.
- https://eurotax.es/valoracion-y-tasacion/donde-deberia-comercializar-mis-vehiculos/ — arbitraje regional (RV Monitor).
- https://eurotax.es/sector/concesionarios/ y /sector/aseguradoras/ — placement por segmento.
- https://eurotax.es/nuestra-precision/ — metodología (reuniones editoriales mensuales).
- https://autovista.com/product/autovista-api/ , https://autovista.com/product/vin-api/ , https://autovista.com/products/ , https://autovista.com/pricing-valuations-data/ , https://autovista.com/pricing-valuations/where-can-i-find-live-retail-prices/ — catálogo y métricas grupo.
- https://www.jdpower.com/business/press-releases/autovista-group-acquisition-close + BusinessWire 2023-09-12 — adquisición J.D. Power/Thoma Bravo.
- https://autovistagroup.com/about-autovista-group/our-history-old + Crunchbase — historia (Glass's/Schwacke/Lederer, EurotaxGlass's AG Freienbach, Hayfin).
- https://webservices.eurotaxglass.com/wsdl/identification.wsdl — endpoint SOAP legacy.

> Verificación: la mayoría de campos [V] proceden de lectura directa de páginas de producto y de los 2 PDFs (extraídos con PyMuPDF). Identidad corporativa verificada con ≥2 fuentes (JD Power/BusinessWire + Crunchbase/Autovista history). Importe de precio y HQ exacto = no verificables públicamente (marcados [A]/GAP).
