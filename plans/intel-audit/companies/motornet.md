# Auditoría atómica — Motornet (Sanguinetti Editore S.p.A · marca Eurotax Italia)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Plataforma italiana de datos/valoración de automoción. Web producto/portal: https://www.motornet.it/ · Portal de valoración con login: https://adm.motornet.it/ (AutoDataManager) · Portal legacy: http://www2.motornet.it/portale/ (503 al auditar) · Editor: Sanguinetti Editore S.p.A.
> Fecha auditoría: 2026-06-30. Método: navegación exhaustiva de www.motornet.it (sitemap completo + 18 páginas de producto en `/prodotti/*` + páginas de sección `/quotazioni-usato-eurotax`, `/statistiche-quotazioni-usato`, `/svalutazione-*` por vertical + chi-siamo + contatti), portal `adm.motornet.it` (login + descripción de producto), + verificación cruzada de identidad/propiedad con prensa (NewsMondo, Infomotori, APAID, JD Power, Thoma Bravo, Autovista24) y agregadores (Bloomberg, ZoomInfo, Europages).
> Convención: [V] = verificado leyendo la fuente · [A] = asumido/inferido (marcado siempre). El subdominio `valuation.motornet.it` indicado en el encargo **NO existe** (DNS NXDOMAIN, ver §Gaps); la valoración se sirve vía `adm.motornet.it`.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca de producto | **Motornet** (motornet.it) | [V] |
| Razón social / editor | **Sanguinetti Editore S.p.A** | [V] |
| Marca de dato/valoración | **Eurotax** (Blu y Giallo) — comercializada en Italia por Sanguinetti bajo licencia | [V — chi-siamo + NewsMondo + APAID] |
| Categoría | Listini de vehículo **nuevo** + **quotazioni Eurotax del usado** (valoración estadística de mercado) + datos técnicos/catálogo + servicios administrativos (ACI/targa) + report de historial de vehículo + price intelligence online (StreetPrice) | [V] |
| Posicionamiento | **"Il riferimento in Italia per le quotazioni dei veicoli usati"** (la referencia en Italia para quotazioni del usado) | [V — home] |
| HQ | **Via Ulrico Hoepli, 7 — 20121 Milano (MI), Italia** | [V — chi-siamo/contatti + Waze/Yelp/Europages] |
| Fundación (Italia) | **1964** — "Sanguinetti Indagini di mercato" inicia el monitoreo continuo del sector motoristico en Italia | [V] |
| Hito editorial | **Desde 1978** las publicaciones Eurotax son editadas por **Sanguinetti Editore** | [V] |
| Origen marca Eurotax | **1957** — Hans Schwacke (Fráncfort) inicia la observación sistemática del mercado del usado; luego se internacionaliza como Eurotax | [V] |
| Antigüedad declarada | **"Da oltre 55 anni"** (libretti Eurotax, +55 años de uso/reconocimiento sectorial) | [V] |
| Capital social | **€200.000** | [V — búsqueda corporativa] |
| P.IVA / C.F. | **04156070155** · Codice Univoco **USAL8PV** | [V] |
| Soporte | **Tel. 02-86462716** · **info@sanguinettieditore.it** | [V — portal adm] |

### Cadena de propiedad (verificada) [V]
- **Marca Eurotax** (y el **Autovista Code**, catálogo técnico subyacente) = propiedad de **Autovista Group**.
- **Autovista Group** (6 marcas: Autovista, **Eurotax**, **Glass's**, **Schwacke**, Rødboka, EV Volumes) fue **adquirido por J.D. Power** (cierre **1-mar-2024**); accionista previo **Hayfin Capital Management**. **J.D. Power** es propiedad de **Thoma Bravo** (desde 2019). [V — JD Power press + Thoma Bravo + Autovista24]
- **Sanguinetti Editore S.p.A** = **licenciataria EXCLUSIVA para Italia** del brand Eurotax **y propietaria de la marca Motornet**. [V — search Eurotax/Autovista]
- Síntesis del linaje: **Thoma Bravo → J.D. Power → Autovista Group → marca Eurotax → Sanguinetti Editore (licencia Italia) → plataforma Motornet**. Las quotazioni italianas las **determina y publica Sanguinetti** (no Autovista directamente); Eurotax es el canal de comercialización del Autovista Code en Italia. [V]

### Clientes objetivo (declarados, chi-siamo) [V]
**concessionari · operatori del settore · compagnie di assicurazioni · società finanziarie e di leasing · noleggiatori (rent/renting) · periti · tribunali · dogane** (peritos, tribunales y aduanas como usuarios oficiales del valor de referencia). Más: testate giornalistiche, agenzie di comunicazione y software house (vía Plug-in/API).

---

## 2. Cobertura

### Geográfica [V]
- **Italia** es el mercado de Motornet (plataforma + quotazioni italianas). Motornet/Sanguinetti operan **solo Italia**.
- La **marca Eurotax** a nivel internacional (vía Autovista Group y otros licenciatarios) está presente en **Austria, Bélgica, Países Bajos, España, Suiza, Alemania, Francia, Portugal, Italia** + expansión a Europa del Este. [V — chi-siamo] (pero Motornet **no** vende multi-país desde un único producto; ver Gaps.)

### Scope de vehículos (muy amplio — 6+ macro-categorías) [V — sitemap + banche dati + libretti]
1. **Auto / Autovetture** (incl. **fuoristrada/SUV**) — `auto`.
2. **Veicoli Commerciali** — `vcom`.
3. **Veicoli Industriali** — `vind`.
4. **Due Ruote / Moto** + **Mini-Car** — `moto`.
5. **Caravan** + **Camper** — `caravan`, `camper`.
6. **Macchine Agricole**: **trattori** + **mietitrebbia** (cosechadoras) — `trattori`, `mietitrebbia`.
7. **Nautica**: **imbarcazioni** (embarcaciones) + **motori** (motores marinos/fueraborda) — `imbarcazioni`, `motori`.

### Scope temporal y nuevo/usado [V]
- **Nuevo**: listini, especificaciones técnicas, configurador/preventivo (modelos en producción, Km0, fuera de producción vendidos en los últimos 100 días) + "Modelli in arrivo".
- **Usado**: quotazioni Eurotax. Base de datos de **todos los vehículos comercializados en Italia desde los años 1970 hasta hoy**.
- **Quotazioni Eurotax**: para vehículos matriculados **desde 2000** (valores históricos desde 2000).
- **Retrodatación/históricos** (varía por producto — variación real, no flatten): Online/ADM **2008→hoy**; Pacchetto crediti **2015→hoy**; portal ADM muestra rango **2011–2026**; Web Analysis usa banche dati Eurotax Autovetture **desde 2007**.
- Granularidad de identificación: **marca → modello → allestimento** (versión exacta) → **delta de accesorios de serie por allestimento**.

### Escala de la muestra de mercado [V]
- Panel de **"oltre 450 concessionari"** distribuidos en todo el territorio nacional (chi-siamo); **500+ dealerships** citadas en libretti (variación menor entre fuentes, declarada).

---

## 3. Productos + campos atómicos

Catálogo completo: **18 productos/servicios** en `/prodotti/*` + **3 servicios gratuitos** (Listini del nuovo, Modelli in arrivo, Statistiche quotazioni usato). Organizados por bloque funcional.

### — Bloque VALORACIÓN / DATO NÚCLEO —

### 3.1 Quotazioni usato Eurotax — Blu & Giallo (producto raíz) [V]
El valor de referencia. **Dos cotizaciones** sobre el mismo vehículo:
- **Eurotax Blu (Compera / acquisto)** — para **commercianti** (concesionarios/revendedores): **precio de compra** = lo que el profesional debería pagar (referencia trade-in/wholesale). [V — chi-siamo + NewsMondo]
- **Eurotax Giallo (Vendita)** — referencia de **venta**, orientada al **privato**: precio máximo razonable de venta de un usado. [V — NewsMondo]
- **Correzione km (ajuste por kilometraje)**: ambos valores se corrigen por km respecto a la media esperada según **año de matriculación + cilindrada** (ej.: gasolina 1.0 de 2011 ≈ ≤90.000 km esperados); **menos km → valor sube, más km → valor baja**. [V — NewsMondo]
- **Valutazione retrodatata** (valor a fecha pasada) con corrección km. [V]
- **Valori storici Eurotax** (serie histórica del valor). [V]
- **Perímetro de fiabilidad**: vehículos matriculados en la última década aprox., desgaste medio, sin daños graves, mantenimiento regular. [V — NewsMondo]
- Cubre las **6+ categorías** (auto, vcom, vind, moto, caravan/camper, agrícola, náutica).

### 3.2 Banche Dati Motornet — base de datos / Web Service (núcleo de integración) [V]
"Database completo, aggiornato in tempo reale, fornibile anche in modalità **Web Service**." Contenido atómico:
- **Anagrafica del vehículo**: denominación oficial, características técnicas, **prezzi di listino**, **fecha inicio/fin de producción**.
- **Quotazioni**: **Eurotax Blu (Compera)** y **Giallo (Vendita)** con impacto del kilometraje.
- **Accessori**: registro de **accesorios de serie** y **opcionales** oficiales + **valores residuales** de accesorios + **vincoli/constraints de pacchetti** (qué opción excluye/obliga a otra).
- **Specifiche EV / ricarica**: **tempo di ricarica · tipo di corrente · potenza · voltaggio · corrente massima (range) · tipo di fase · codice connettore · descrizione connettore**.
- **Costi e tempi di riparazione**: **meccanica** y **carrozzeria** (coste y tiempos — dato tipo SMR).
- Valoraciones Eurotax para matriculados 2000→hoy.
- Entrega: **raw data** (varios formatos) **o Web Service** (REST/SOAP) integrable, **modificable/extensible** a medida del cliente.

### 3.3 AutoDataManager (ADM) Web — software de valoración de permuta y stock (estrella PRO) [V]
`adm.motornet.it`. "Il software più attendibile e completo per determinare il **valore di permuta**." Campos:
- **Valore di permuta** (trade-in) base **Eurotax + correzione km**.
- **Perizia personalizzata** con parámetros ajustables: **stato/uso del veicolo** · **valore residuo accessori non di serie** · **scostamento km** (sobre/bajo la media) · **costi di riparazione meccanica e di carrozzeria** importantes.
- **Valutazioni retrodatate** (todos los meses 2008→hoy; portal muestra 2011–2026) y **valori storici desde 2000** para matriculados desde 2000.
- **Ricerca per targa** con diferenciación de **pacchetto accessori** (delta).
- **Valorizzazione dello stock** con **caricamento automatico da DMS/CRM**.
- **Sincronizzazione real-time** con WebApp Motornet.
- **Perizia stampabile** con cálculo **IVA** (referencia "IVA al 40%" / "iva inclusa").
- **Workflow de ruoli/aprobación** (perfiles de empresa).
- Categorías: autovetture, fuoristrada, veicoli commerciali. Acceso: **abbonamento** (login user/password).

### 3.4 Motornet Online — quotazione Eurotax online (alternativa al libro) [V]
"Il Software più completo… la quotazione Eurotax OnLine con correzioni km, valutazione retrodatata, listini e caratteristiche del nuovo." Módulos/campos:
- **Consultazione Libro**: publicaciones Eurotax actuales e históricas (**archivio 2008→hoy**).
- **Valutazione Rapida**: **valore base Eurotax** · **valore con correzione km** · **valori storici Eurotax (2008+)**.
- **Statistiche Quotazioni Usato**: **svalutazione per marca / modelli / segmento** · **Top 5 più/meno svalutati** · **variazioni di valutazione**.
- **Listini del Nuovo**: **specifiche tecniche · foto · prezzi di listino · accessori di serie · optional · confronto fino a 3 veicoli**.
- **Ricerca per targa** con **delta accessori**.
- **Valutazioni retrodatate** con corrección km.
- **Perizia** con **ruoli aziendali**.
- **Valorizzazione stock** del usado.
- **Sincronizzazione real-time** con la WebApp.
- Actualización: **ogni primo del mese** valutazioni Eurotax actualizadas; todas las versiones siempre actualizadas.

### 3.5 Libretti Eurotax — publicaciones impresas [V]
Listini + quotazioni Eurotax impresas. Por categoría (frecuencia · años cotizados · marcas · modelos · páginas):
- **Auto/SUV**: mensual · 9–10 años · 64 marcas · ~15.000 modelos · ~550 pág.
- **Veicoli Commerciali**: bimestral · 10 años · 28 marcas · ~9.300 modelos · ~400 pág.
- **Moto/Mini-car**: semestral · 9 años · 49/12 marcas · 2.800/245 modelos · ~260 pág.
- **Caravan/Camper**: semestral · 9 años · 20/41 marcas · 950/7.250 modelos · ~400 pág.
- **Nautica**: semestral · 9 años · 180/11 marcas · 6.400/1.962 modelos · ~440 pág.
- **Macchine Agricole**: semestral · **15 años** · 29/6 marcas · 6.200/530 modelos · ~300 pág.
- **Sin publicidad de fabricantes** en los libretti (garantía de independencia del contenido).

### — Bloque NUEVO / CONFIGURACIÓN —

### 3.6 Preventivo del Nuovo (Preventivatore) — configurador + propuesta de compra [V]
"Configura le autovetture Nuove di tutti i marchi." Vehículos: nuevos en producción · **Km0** · fuera de producción vendidos en los últimos 100 días. Campos:
- **Dati cliente** archivados para contacto futuro.
- **Tipo veicolo** (Nuovo / Km0 / recente) + selección por **codice prodotto** o menú.
- **Regime IVA** (corriente / 4% / personalizado).
- **Accessori di serie** (códigos oficiales + descripciones).
- **Optional a pagamento** con reglas de **gestione pacchetti**.
- **Accessori after-market** con costes.
- **Scheda tecnica completa**.
- **IPT e costi di messa su strada** (auto-calculados por **provincia**).
- **Incentivi**: estatales · regionales · provinciales · comunales · de fabricante.
- **Sconti**: % o valor absoluto; **permuta** y **rottamazione** (achatarramiento).
- **Valutazione veicolo in permuta** (integra la cote Eurotax).
- **Costi aggiuntivi**: kit consegna · contributi ambientali · servizi speciali.
- **Modalità di pagamento**.
- Output: **preventivo stampabile · poster per concessionaria · PDF · invio email automatico**. Entrega: software · web service API · DMS.

### 3.7 Plug-in — Configuratore del nuovo embebible [V]
"Integrabili in ogni sito web tramite un apposito **script**." Para **testate giornalistiche, agenzie di comunicazione, software house**. Campos/atributos:
- **Configuratore del nuovo** de todas las marcas: modalidades de búsqueda múltiples · **salvataggio e confronto modelli** · **dati tecnici** · **aggiornamento real-time**.
- 5 ventajas: personalizable · responsive · "estremamente rapido" · integración fácil · real-time.
- Acceso alternativo vía **REST/SOAP** a las banche dati Eurotax-Motornet; consultoría de integración a medida.

### — Bloque MOVILIDAD / LEADS —

### 3.8 WebApp Motornet — valoración móvil [V]
"Per valutare i tuoi veicoli lontano dalla scrivania" (iOS/Android, smartphone/tablet). Campos:
- **Ricerca per targa**.
- **Quotazione Eurotax + correzione km** en tiempo real.
- **Cattura e archiviazione foto** de inspección desde el dispositivo.
- **Perizie** on-site.
- **Sincronizzazione** con AutoDataManager y Motornet Online.
- Compra: **pacchetti pay-per-consultazione** o **abbonamento flat**.

### 3.9 Leads App Motornet — captación de leads en eventos [V]
"Per acquisire i nominativi di potenziali clienti durante eventi e presentazioni." Flujo/campos:
- **Formulario de cliente** (datos personales).
- **Datos del veicolo attuale** del cliente.
- **Prezzo del nuovo** del fabricante.
- El cliente recibe por **email** dos valoraciones: **valore commerciale del veicolo attuale** + **prezzo di listino del nuovo**.
- Datos archivados en **DB dedicada** accesible siempre con credenciales.

### — Bloque ANALÍTICA / MERCADO —

### 3.10 Motornet Web Analysis — analítica de svalutazione y valor residual [V]
"Servizi statistici e analisi di mercato con supporto grafico" (login user/password). Capacidades/campos:
- **Analisi di svalutazione**.
- **Valori residui** (vs listini actuales o históricos).
- **Standard Analysis**: análisis preconfigurados por Sanguinetti (50+ años de experiencia).
- **Custom Analysis**: filtros **mercato generale · marca · gamma · modelli · segmento · tipo**.
- **Banche dati Eurotax Autovetture dal 2007** cruzables.
- Análisis de **período único o comparativo** entre fechas de BBDD.
- **Export xlsx** · archivar · imprimir · actualizar.

### 3.11 Statistiche Quotazioni Usato (gratuito) — andamento de mercado [V]
Sección pública por vertical (auto/moto/vind/vcom). Métricas (labels):
- **Svalutazione marca** (por marca; desgloses por **segmento · alimentazione · carrozzeria**).
- **Svalutazione segmento** (por **cilindrata · carrozzeria · porte · todas las versiones**).
- **Top 5 modelli +/- svalutati** (más/menos depreciados, vehículos con **1 año de antigüedad**).
- **Variazione valutazioni** (vehículos con 1 año de uso, comparación **mensile (MoM)** y **annuale (YoY)**).
- Páginas: `/<vertical>/svalutazione-marca`, `/<vertical>/svalutazione-segmento/<id>`. Datos numéricos renderizados por JS tras seleccionar marca/segmento (no en HTML plano).

### 3.12 StreetPrice — price intelligence de anuncios online [V]
"Analizza milioni di annunci online per singolo **modello, allestimento e optional** per suggerire il miglior posizionamento del **prezzo di vendita online**." Campos:
- **Prezzo Consigliato** (equilibrio margen↔tiempo de venta).
- **Prezzo Massimo** (maximiza margen sin perder competitividad).
- **Prezzo Minimo** (acelera venta sin sacrificar margen severamente).
- **Tempi di giacenza media nel web** (días medios en publicación) por allestimento específico.
- **Confronto annunci propri vs competitor**.
- **Filtro geográfico**: nacional o regional/provincial.
- Fuente: "milioni di annunci online" (metodología/fuentes concretas **no divulgadas**).

### — Bloque HISTORIAL / ADMINISTRATIVO (datos oficiales) —

### 3.13 Report Motornet — informe 360° de historial (estilo Carfax/autoDNA) [V]
"Servizio sicuro, semplice e dettagliato per la valutazione a 360° del veicolo." Para **autovetture, veicoli commerciali, due ruote**. **12 secciones/campos**:
1. **Data e paese di prima immatricolazione**.
2. **Numero e tipo di passaggio di proprietà**.
3. **Storico delle revisioni e chilometraggi rilevati** (historial de km de las ITV).
4. **Data della prossima revisione**.
5. **Fermi amministrativi, ipoteche e confische** (gravámenes).
6. **Valutazione economica del veicolo (Eurotax)**.
7. **Prezzo di listino iniziale + andamento svalutazione**.
8. **Prezzo medio di vendita online (StreetPrice)**.
9. **Classe Euro e CO2**.
10. **Consumo urbano · extraurbano · misto**.
11. **Specifiche tecniche**.
12. **Informazioni su uso e destinazione d'uso**.
- Fuentes: **ACI** (matriculación, revisioni, km, gravámenes) + **Eurotax** (valoración) + **StreetPrice** (precio online). Entrega: en segundos (formato no especificado, [A] digital/PDF).

### 3.14 Ricerca per targa — identificación oficial por matrícula [V]
"Per autovetture, Veicoli Commerciali e Due Ruote." Campos de salida:
- **Marca · Modello**.
- **Telaio (chassis/VIN)**.
- **Data prima immatricolazione** (Italia y **estero**) + **paese di origine estero**.
- **Codice motore**.
- **Data ultima revisione**.
- **Chilometraggio all'ultima revisione**.
- **Allestimento corretto** + **delta accessori di serie** por allestimento.
- (Owner/propietario **no** se devuelve aquí.) Entrega: ADM Web · Motornet Online · Web Service · Pacchetto Quotazioni · WebApp · LeadsApp.

### 3.15 Ricerca per VIN — configuración exacta de fábrica [V]
"L'unico servizio che permette di conoscere l'esatta configurazione di un veicolo uscito dalla fabbrica." Veículos **desde 2016**. Campos:
- **Allestimento esatto** (versión/trim).
- **Data di produzione**.
- **Prezzo di listino**.
- **Accessori di serie**.
- **Accessori a pagamento** (opcionales).
- Integra con **AutoDataManager** y **WebService**.

### 3.16 Check Fermo Amministrativo [V]
Input: **targa + codice fiscale/partita IVA** del titular. Salida = **semáforo**:
- **Verde**: "NON sono presenti vincoli o ipoteche".
- **Giallo**: discrepancia de datos, verificar.
- **Rosso**: "Sono presenti vincolo o gravami".
- Fuente **ACI**; **"L'informazione fornita non ha valore giuridico"** (screening preliminar).

### 3.17 Servizi ACI — datos oficiales de propiedad/locazione [V]
Dos servicios:
- **Dati ultimo passaggio di proprietà**: **data ultimo atto di proprietà** · **valore veicolo all'ultimo passaggio** · **numero di passaggi di proprietà** (incl. minivolture) · **flag minivolture** del último passaggio.
- **Scadenza locazione**: **data scadenza locazione** · **data scadenza patto riservato dominio (PRD)** · **data scadenza usufrutto**.

### — Bloque SERVICIOS —

### 3.18 Karrycar — marketplace de transporte de vehículos [V]
"Il primo portale in Italia dedicato al trasporto auto e veicoli per privati e aziende." Cotización instantánea por **algoritmo**; bisarca o conductor; Italia + Europa; 3–10 días hábiles; pago al reservar; API para software houses. (Servicio logístico, no de dato de valoración.)

### 3.19 Servizios gratuitos adicionales [V]
- **Listini del nuovo**: prezzi di listino + specifiche tecniche del nuovo (gratis).
- **Modelli in arrivo**: previews de modelos próximos (gratis; sin ficha de campos detallada en home).

---

## 4. Metodología y fuentes de datos [V]
- **Valor Eurotax italiano = investigación de mercado**, **NO porcentajes fijos de depreciación**. Lo determina **Sanguinetti Indagini di mercato** desde **1964**. [V — libretti]
- **Panel de concesionarios oficiales**: **reuniones bimestrales/trimestrales** con dealers oficiales + encuestas en **450–500+ concesionarios** en todo el territorio + **muestreo por marca** para evitar sesgo competitivo. [V — libretti/chi-siamo]
- **Catálogo técnico subyacente = Autovista Code** (de Autovista Group): estandariza cientos de atributos técnicos por vehículo; Eurotax es el canal de comercialización del Autovista Code en Italia. [V]
- **Corrección por kilometraje**: km esperado en función de **año de matriculación + cilindrada**; desviación al alza/baja ajusta el valor. [V]
- **Perímetro de la cote**: matriculados ~última década, desgaste medio, sin daños graves, mantenimiento regular (fuera de eso, valoración no fiable). [V]
- **StreetPrice**: análisis de **millones de anuncios online** por modello/allestimento/optional (fuentes concretas no divulgadas). [V]
- **Datos oficiales ACI**: matriculación, revisioni, km de ITV, gravámenes, passaggi di proprietà, locazione — integrados en Report/Targa/Fermo/Servizi ACI. [V]
- **Frecuencia**: quotazioni Eurotax actualizadas **el día 1 de cada mes**; banche dati **en tiempo real**; libretti según frecuencia por categoría (mensual a semestral). [V]
- **Independencia**: sin publicidad de fabricantes en los libretti. [V]

---

## 5. Entrega [V]
- **Libretti impresos** (Libretti Eurotax) — canal histórico.
- **Software de escritorio / web PRO**: **AutoDataManager** (`adm.motornet.it`, login, abbonamento).
- **Plataforma web**: **Motornet Online** (sincronizada con WebApp).
- **Portal legacy**: `www2.motornet.it/portale` (503 al auditar — probable obsoleto/migrado). [V — 503]
- **WebApp móvil** (iOS/Android): WebApp Motornet, Leads App.
- **Web Service REST y/o SOAP**: acceso a todas las categorías por **número definido de crediti a usar dentro del año**; **modificable/extensible** a medida; consultoría de integración disponible.
- **Plug-in embebible** vía script (configuratore del nuovo) para webs de terceros.
- **Raw data / banche dati** (varios formatos) para integración en sistemas informativos.
- **Integración DMS/CRM**: carga automática de stock en ADM.
- **Export BI**: **xlsx** (Web Analysis).
- **PDF / email**: preventivi, perizie, quotazioni, valoraciones de leads.
- **Report digital** (Report Motornet, en segundos).
- **API logística** (Karrycar) para software houses.

---

## 6. Precio
- **No público.** [V]
- Modelos: **abbonamento** (ADM, Web Analysis) · **pacchetti pay-per-consultazione** (WebApp) · **Web Service por crediti anuales** (Pacchetto Quotazioni = "soluzione più economica per consultare le quotazioni"). [V]
- Tarifa concreta vía **formulario de contacto** (nome, azienda, email, telefono, note) / tel. **02-86462716**. [V]
- **Importe concreto = GAP** (no descubrible públicamente). Karrycar sí es gratis-cotizar / pago al reservar (servicio logístico). [V]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. Mapeo pantalla/sección → dato.

### Resultado de valoración (ADM / Motornet Online / WebApp) [V/A]
1. **Entrada por targa** (o marca→modello→allestimento) → **identificación del vehículo**: allestimento corretto + **delta accessori** del allestimento (pantalla de selección/confirmación).
2. **Bloque de valores** (núcleo): **Eurotax Blu (Compera)** y **Eurotax Giallo (Vendita)** lado a lado.
3. **Control de km**: campo/ajuste de **correzione km** que recalcula el valor en vivo.
4. **Panel de personalización (perizia)**: **stato del veicolo · valore residuo accessori non di serie · scostamento km · costi riparazione meccanica/carrozzeria** → valor de permuta ajustado.
5. **Selector temporal**: **valutazione retrodatata** (mes/año) + serie de **valori storici**.
6. **Salida**: **perizia stampabile PDF** con **IVA**; push a **DMS/CRM** (stock).

### Ficha de NUEVO (Listini / Preventivatore) [V]
- **Listini del nuovo**: ficha con **specifiche tecniche · foto · prezzo di listino · accessori di serie/optional · confronto fino a 3**.
- **Preventivatore**: flujo configurador → **regime IVA**, **accessori/pacchetti**, **IPT por provincia**, **incentivi** (estatal→comunal→costruttore), **sconti/permuta/rottamazione**, **valutazione permuta** → **preventivo PDF/poster/email**.

### Statistiche (sección pública, por vertical) [V]
- Página de entrada con **selector de categoría** (Auto/Moto/Veicoli industriali/Veicoli commerciali).
- **Svalutazione marca**: dropdown "SELEZIONA LA MARCA" → gráfico de andamento por marca (desglose segmento/alimentazione/carrozzeria).
- **Svalutazione segmento**: por cilindrata/carrozzeria/porte.
- **Ranking Top 5 +/- svalutati** (1 año) + **Variazione valutazioni** (MoM/YoY) — bloques de ranking/tendencia.

### StreetPrice — panel del dealer [V]
- Por **allestimento**: tres precios (**Consigliato / Massimo / Minimo**) + **giacenza media web** (días) + **propios vs competidores** + **filtro geográfico** (nazionale/regionale/provinciale).

### Report Motornet — informe de página única (estilo Carfax) [V]
- Una sola vista con las **12 secciones** en orden: identidad/immatricolazione → passaggi → **storico revisioni+km** → prossima revisione → **gravámenes** → **valutazione Eurotax** → listino+svalutazione → **StreetPrice** → Euro/CO2 → consumi → specifiche → uso.

### Ricerca per targa / VIN — resultado de una línea [V]
- **Targa** → ficha de homologación (marca, modello, telaio, immatricolazione, codice motore, revisione+km, allestimento+delta).
- **VIN** (2016+) → **allestimento esatto + data produzione + listino + accessori serie/pagamento** (single-click).

### Fermo Amministrativo — semáforo [V]
- Input targa+CF/P.IVA → **luz verde/giallo/rosso** (presencia de gravámenes) + disclaimer "nessun valore giuridico".

### Plug-in — configurador embebido [V]
- Widget del **configuratore del nuovo** dentro de la web del cliente (testate/agenzie), con búsqueda/confronto/dati tecnici en tiempo real.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Es el estándar oficial de valoración en Italia**: Eurotax (Autovista Code) vía licenciatario exclusivo; **usado por peritos, tribunales, aduanas, aseguradoras, leasing y noleggiatori** como referencia de mercado.
- [V] **Doble valor Blu/Giallo en un mismo vehículo**: precio de **compra del dealer (Blu)** y de **venta al privato (Giallo)** — separación canal explícita.
- [V] **Metodología de panel de concesionarios** (450–500+, reuniones periódicas, muestreo anti-sesgo), **no** porcentajes fijos ni solo crawling estadístico.
- [V] **Scope de vehículos excepcionalmente amplio**: incluye **náutica (imbarcazioni + motori marini), macchine agricole (trattori, mietitrebbia), caravan/camper, veicoli industriali** — cobertura rara entre peers de valoración.
- [V] **Profundidad histórica/retrodatación** (valores Eurotax desde 2000; retrodatación 2008/2015; analítica desde 2007) + **catálogo desde los años 70**.
- [V] **Specs EV en el catálogo** (tiempo de carga, conector, voltaje, fase, corriente) integradas en la banca dati.
- [V] **Costes y tiempos de reparación (meccanica + carrozzeria)** en la base de datos — dato tipo SMR poco común en un valorador.
- [V] **Report Motornet = historial 360° estilo Carfax** combinando **datos oficiales ACI** (passaggi, revisioni, **km history**, gravámenes) + **valoración Eurotax** + **StreetPrice** + **Euro/CO2/consumi** en un único informe.
- [V] **Acceso a datos administrativos oficiales ACI** (passaggi di proprietà, valore ultimo passaggio, minivolture, fermo amministrativo, scadenze locazione/PRD/usufrutto) — capa legal/administrativa que los puros valoradores no tienen.
- [V] **StreetPrice**: inteligencia de **precio real de anuncios online** (Consigliato/Massimo/Minimo + **giacenza media web** + propios vs competidores) — capa de mercado transaccional sobre la cote editorial.
- [V] **Preventivatore del nuovo muy granular** (IPT por provincia, incentivi estatales→comunales→costruttore, permuta/rottamazione, pacchetti de optional).
- [V] **Omnicanal de entrega**: impreso · desktop · web · móvil · Web Service REST/SOAP · plug-in embebible · DMS · xlsx · PDF.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Subdominio `valuation.motornet.it` NO existe** (DNS NXDOMAIN): la valoración se sirve por `adm.motornet.it` (AutoDataManager) y `motornet.it`. El "subdominio valuation" del encargo no es válido para Motornet.
- [V] **Solo Italia**: Motornet no vende valoración multi-país desde un único producto (la red Eurotax internacional la operan Autovista y otros licenciatarios, no Motornet).
- [V] **Precio no público** (abbonamento/crediti/contacto; ningún importe descubrible).
- [V/A] **Sin documentación técnica de API pública**: el Web Service REST/SOAP es "contáctanos por crediti"; **no hay esquema JSON, endpoints, auth, rate limits ni diccionario de campos** expuestos públicamente.
- [A] **Sin producto de valor residual FUTURO / forecast** (RV a 24-48 meses, curvas prospectivas tipo Autovista Residual Value / autobizFuture): Motornet expone **histórico + actual + retrodatado**, no una previsión forward nombrada.
- [A] **Sin TCO / coste total de propiedad** como producto.
- [A] **Sin IA de detección de daños sobre foto**: la WebApp captura/archiva fotos y la perizia es **manual**; no hay análisis automático de daños (vs Noa/Monk de autobiz).
- [V] **Ricerca per VIN limitada a vehículos desde 2016** (poca profundidad histórica de decode VIN).
- [V] **StreetPrice no divulga fuentes ni metodología** (qué portales, volumen, frescura).
- [A] **Sin índices normalizados de mercado tipo "price-to-market %", "market days supply", índice demanda/oferta nacional**: ofrece **svalutazione %, giacenza media web (StreetPrice), variazione MoM/YoY**, pero no esos índices con esa nomenclatura.
- [V] **Estadísticas públicas renderizadas por JS** (números no disponibles en HTML plano; no hay endpoint abierto/CSV de las series de svalutazione).
- [A] **Sin valor de reemplazo/total-loss para seguro como producto distinto** (aunque las aseguradoras usan la cote Eurotax como input).
- [V] **Portal legacy `www2.motornet.it/portale` caído (503)** al auditar.

---

## 10. Fuentes (URLs)
- https://www.motornet.it/ — home, posicionamiento "il riferimento in Italia", servizi gratuiti.
- https://www.motornet.it/chi-siamo — identidad: 1964 Sanguinetti Indagini, 1978 Sanguinetti Editore, origen Eurotax 1957 Schwacke, países Eurotax, 450+ concesionarios, clientes objetivo.
- https://www.motornet.it/contatti — HQ Via Hoepli 7 Milano, datos fiscales.
- https://www.motornet.it/prodotti — catálogo de 18 productos con descripción de una línea (incl. Report Motornet, StreetPrice).
- https://www.motornet.it/prodotti/libretti — libretti por categoría (frecuencia/años/marcas/modelos/páginas), metodología panel de dealers, sin publicidad.
- https://www.motornet.it/prodotti/banchedati — banca dati: anagrafica, Blu/Giallo, accessori+residui, specs EV (ricarica/connettore), costi/tempi riparazione, Web Service.
- https://www.motornet.it/prodotti/adm — AutoDataManager: valore di permuta, perizia personalizzata, retrodatazione 2008, storici 2000, DMS/CRM, IVA, ruoli.
- https://adm.motornet.it/ — portal de login ADM: "valore di permuta", 2011–2026, IVA inclusa, parámetros, abbonamento, soporte 02-86462716.
- https://www.motornet.it/prodotti/online — Motornet Online: consultazione libro, valutazione rapida, statistiche, listini nuovo, targa, retrodatate, sync webapp.
- https://www.motornet.it/prodotti/nuovo — Preventivatore: IVA, accessori/pacchetti, IPT provincia, incentivi, sconti/permuta/rottamazione, PDF/poster/email.
- https://www.motornet.it/prodotti/plugin — Plug-in configuratore embebible vía script; REST/SOAP; testate/agenzie/software house.
- https://www.motornet.it/prodotti/pacchetti — Pacchetto crediti: targa, Blu/Giallo, correzione km, retrodatata 2015, accessori, scheda tecnica, PDF/email.
- https://www.motornet.it/prodotti/webapp — WebApp móvil iOS/Android: targa, quotazione+km real-time, foto, perizie, sync ADM/Online.
- https://www.motornet.it/prodotti/leadsapp — Leads App: form cliente, veicolo attuale, prezzo nuovo, 2 valutazioni por email, DB dedicada.
- https://www.motornet.it/prodotti/webanalysis — Web Analysis: svalutazione, valori residui, standard/custom, filtros, banche dati 2007, export xlsx.
- https://www.motornet.it/prodotti/streetprice — StreetPrice: Consigliato/Massimo/Minimo, giacenza media web, propios vs competitor, geo.
- https://www.motornet.it/prodotti/report-motornet — Report 360°: 12 secciones (immatricolazione, passaggi, storico revisioni+km, gravámenes, Eurotax, listino+svalutazione, StreetPrice, Euro/CO2, consumi, specs, uso); fuentes ACI/Eurotax/StreetPrice.
- https://www.motornet.it/prodotti/targa — Ricerca per targa: marca, modello, telaio, immatricolazione It/estero, paese, codice motore, ultima revisione+km, allestimento+delta.
- https://www.motornet.it/prodotti/vin — Ricerca per VIN (2016+): allestimento esatto, data produzione, listino, accessori serie/pagamento.
- https://www.motornet.it/prodotti/fermo — Check Fermo Amministrativo: input targa+CF/P.IVA, semáforo verde/giallo/rosso, fuente ACI, sin valor jurídico.
- https://www.motornet.it/prodotti/serviziaci — Servizi ACI: ultimo passaggio (data, valore, numero, minivolture) + scadenza locazione (locazione/PRD/usufrutto).
- https://www.motornet.it/prodotti/karrycar — Karrycar: marketplace de transporte, algoritmo de precio, API.
- https://www.motornet.it/auto/statistiche-quotazioni-usato — métricas: svalutazione marca/segmento, Top 5 +/- svalutati, variazione MoM/YoY.
- https://www.motornet.it/auto/svalutazione-marca · /vind/svalutazione-segmento/<id> — páginas de svalutazione (datos por JS).
- https://www.motornet.it/sitemap.xml + /sitemap/prodotti.xml + /sitemap/resto.xml — estructura completa, verticales (auto/moto/vcom/vind/camper/caravan/trattori/mietitrebbia/imbarcazioni/motori), niveles modello→allestimento.
- https://newsmondo.it/eurotax-blu-e-giallo/motori/ — definición Blu (commercianti/acquisto) vs Giallo (privati/vendita) + correzione km (2ª fuente).
- https://www.infomotori.com/auto/sanguinetti-i-signori-dei-listini-auto-con-eurotax_292677/ — Sanguinetti como editor histórico de los listini Eurotax (2ª fuente identidad).
- https://peritiauto.wordpress.com/eurotax/ (APAID) — Blu/Giallo desde la óptica del perito (3ª fuente).
- https://www.jdpower.com/business/press-releases/autovista-group-acquisition-close + https://www.thomabravo.com/press-releases/...autovista-group + https://autovista24.autovistagroup.com/news/jd-power-completes-acquisition-of-autovista-group/ — propiedad: J.D. Power (Thoma Bravo) cierra adquisición de Autovista Group (1-mar-2024), 6 marcas incl. Eurotax/Glass's/Schwacke.
- (NXDOMAIN) https://valuation.motornet.it/ — subdominio inexistente (DNS ENOTFOUND).
- (503) http://www2.motornet.it/portale/Home.html — portal legacy no disponible.
- Bloomberg / ZoomInfo / Europages / Waze / Yelp — verificación cruzada de razón social, HQ y datos corporativos.

> Verificación: identidad y **propiedad** contrastadas con ≥2 fuentes ortogonales (motornet/chi-siamo + NewsMondo + Infomotori + APAID para Eurotax/Blu/Giallo; JD Power + Thoma Bravo + Autovista24 para la cadena Autovista→J.D. Power). Campos de producto [V] leídos directamente de las 18 páginas `/prodotti/*` + portal ADM. Variaciones reales de profundidad histórica (2000/2007/2008/2011/2015) declaradas sin aplanar. Subdominio `valuation` verificado inexistente (NXDOMAIN). Precio, docs de API, RV forecast, TCO e IA de daños = no hallados (marcados [A]/GAP, no inventados).
