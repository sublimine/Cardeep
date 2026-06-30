# Auditoría atómica — Quattroruote Professional / Infocar

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de datos/valoración de automoción (Italia). Web: https://www.quattroruotepro.it/
> Fecha auditoría: 2026-06-30. Método: navegación exhaustiva del sitio IT + EN, páginas de producto, página corporativa, prensa Editoriale Domus + **descarga y parseo directo de los WSDL/XSD de sus 2 web services SOAP de producción** (`infocar.org`), que exponen el diccionario REAL de campos atómicos (1.104 nombres distintos; 867 campos de negocio tras filtrar plumbing) y las 76+29 operaciones de API. Cross-check con reseller independiente (karma-software) y prensa (edidomus.it, touchpoint.news).
> Convención: [V] = verificado leyendo la fuente · [A] = asumido/inferido (marcado siempre).
> Nota anti-alucinación: la mayoría de campos atómicos de §3 NO provienen de marketing sino del **esquema XSD de producción** (`ADSQPService.svc?xsd=xsd3`, 689 KB). Son los nombres reales que devuelve la API.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca comercial | **Quattroruote Professional** (razón social del área: "Quattroruote Prodotti e Servizi Professional") | [V] |
| Línea de producto/datos | **Infocar** (banca dati auto/moto/ricambi; marca histórica del dato) | [V] |
| Grupo / owner | **Editoriale Domus S.p.A.** — Quattroruote Professional es la *business unit* B2B de Editoriale Domus | [V] |
| Fundación grupo | **1929** (Gianni Mazzocchi compra la revista *Domus*) | [V] |
| Origen de la marca auto | Revista **Quattroruote** lanzada en **1956** por Gianni Mazzocchi | [V] |
| Origen del dato (Infocar) | **Banca Dati Auto creada en 1980**; >30 años de presencia en mercado auto y asegurador | [V] |
| HQ | **Via G. Mazzocchi, 1/3 — 20089 Rozzano (Milán), Italia** | [V] |
| Datos registrales | P.IVA/C.F. **07835550158** · REA Milán **1186124** · capital social **€5.000.000** | [V] |
| CEO | **Sofia Bordone** (nieta del fundador Gianni Mazzocchi) | [V] |
| Familia de marcas (grupo) | Quattroruote, **Ruoteclassiche**, **Dueruote** (→ alimentan Infocar Classic e Infocar Bike) | [V] |
| Partner de datos de mercado | **Indicata** (grupo **Autorola**) — provee la inteligencia de mercado online en tiempo real (motor de InstantWeb), partnership estratégica anunciada **23-feb-2021** | [V] |
| Penetración declarada | Banca dati usada por el **99% de las compañías de seguros** italianas; también rent-a-car | [V] |
| Categoría | Datos e inteligencia de automoción: identificación de vehículos, especificación técnica (~400 datos/vehículo), valoración usado, previsión de valores residuales, datos de mercado online en tiempo real, recambios/tiempos de reparación, software de gestión de concesionario (DMS) | [V] |

### Clientes objetivo (12 segmentos declarados en "Chi siamo") [V]
Fabricantes/importadores (case auto) · Concesionarios/rivenditori · Operadores de usado · Sociedades de **leasing/renting** · **Financieras** · **Compañías de seguros** · Talleres mecánicos · Carrocerías/peritos · Gestores de **flotas** · **Administración pública** · Centros de revisión · Consultoría/formación.

> Posicionamiento: a diferencia de Eurotax/DAT (datos puros pan-EU), Quattroruote Professional es **dato + plataforma operativa (gestionale)** anclada al mercado **italiano**, con autoridad editorial de la marca Quattroruote (las "Quotazioni Quattroruote" son referencia legal/de mercado en Italia).

---

## 2. Cobertura

### Geográfica [V]
- **Italia** (mercado nacional). El dato es la huella del parque comercializado en Italia; las quotazioni son las "Quotazioni Quattroruote" del mercado italiano. No es un proveedor pan-europeo (a diferencia de Autovista/Eurotax/DAT). [V]
- Expansión/uso internacional mencionado de forma genérica (Francia / mercados anglófonos) pero el núcleo es IT. [A]

### Volumen de parque (cross-verificado con reseller karma-software) [V]
- **>6.000 turismos** en comercialización actual.
- **>3.800 veicoli commerciali leggeri (VCL)** en comercialización actual.
- **50.000 turismos fuori produzione** (histórico desde **enero 1989**).
- **21.000 VCL fuori produzione** (histórico).
- Historia de producción cubierta: turismos **desde 1980**; VCL **desde 1993**. [V]
- **~400 informaciones técnicas por vehículo** organizadas en grupos funcionales (motor, prestaciones, dimensiones, etc.). [V — confirmado en página oficial y reseller]
- **60+ equipamientos estandarizados por versión**. [V]
- Quotazioni usado: **histórico 10 años** (detalle semestral para vehículos recientes); valoración hasta **15 años** de antigüedad (más allá → "veicoli storici"). [V]

### Scope de vehículos [V]
- **Tipos**: Turismo (Auto), Todoterreno/SUV (Fuoristrada), **Microvetture** (microcoches), **Veicoli Commerciali Leggeri** (VCL/pick-up), **Moto/ciclomotores** (Infocar Bike), **Vehículos clásicos y americanos** (Infocar Classic), **Vehículos industriales** (solo en banca dati ricambi/tempari). [V — flags `Auto/Fuoristrada/Microvetture/VeicoliCommerciali/Moto` en XSD]
- **Nuevo (VN) y usado (VO)**: configuración de VN (Configuratore) + quotazioni VO. [V]
- **Powertrains**: combustión, híbridos (bloque `DatiTecniciIbride`/`TipoIbridazione`/`VeicoloIbrido`), **eléctricos BEV** (bloques `DatiBatteria` + `DatiRicarica` + autonomía/PKC). [V]
- **Moto**: >2.700 motos y ciclomotores, **~50 especificaciones cada una**, datos técnicos desde **2000**, valoración usado **9 años**. [V]
- Insurance histórico: **108 meses (9 años)** de quotazioni anteriores para valoración a fecha de siniestro. [V]

### Frecuencia de actualización de quotazioni [V]
- **Turismos/SUV: mensual.**
- **Veicoli commerciali: bimestral.**
- **Moto: trimestral.**
- Datos de mercado online (InstantWeb/Indicata): **tiempo real / diario**. [V]

---

## 3. Productos + campos atómicos

> Estructura de oferta en 4 ejes: **(A) Banche Dati** (el dato crudo), **(B) Automotive** (plataforma de venta/valoración para concesionario), **(C) Assicurativo** (seguros), **(D) Autoriparativo** (taller/carrocería). Transversal: **Web Services SOAP** (entrega API) y **Business Intelligence**.
> Los campos marcados con `código` provienen del **XSD de producción** (verificado leyendo el esquema).

### 3.A — BANCHE DATI (el dato)

#### 3.A.1 Infocar Data (banca dati auto) [V]
Banca dati técnica + comercial. Núcleo de identificación: cada vehículo lleva un **Codice INFOCAR** que identifica unívocamente el *allestimento* (versión), más un **Codice INFOCAR AM (Anno-Mese)** que marca re-inmatriculaciones de un vehículo modificado técnica o comercialmente.
Campos de identificación y anagrafica (XSD `DatoMarca/DatoModello/DatoAllestimento/DatoAnagrafica`):
- `CodiceMarca`, `DescrizioneMarca` (marca).
- `CodiceModello`, `DescrizioneModello`, `DescrizioneComplessa`, `GruppoModello` (modelo).
- `CodiceInfocar`, `CodiceInfocarAM`, `CodiceAllestimento`, `Allestimento`, `DescrizioneAllestimento`, `CodiceVersione`, `Versione` (versión/allestimento).
- `CodiceSerie`, `CodiceSpeciale`, `SerieOpzionale`, `ProgressivoRCL`, `CodiceRuoteClassiche` (series/especiales/clásicos).
- `Segmento` (segmento A–J turismos / 1–7 comerciales), `Categoria`, `TipoCategoria`, `Carrozzeria`/`TipoCarrozzeria`, `FlagCategoria`.
- `InizioVendita`/`FineVendita`, `InizioImmatricolazione`/`FineImmatricolazione`, `PeriodoProduzione`, `PeriodoImmatricolazione` (ventanas comerciales y de matriculación).
- `CasaCostruttrice`, `CodiceCasaCostruttrice`, `DescrizioneCasa`, `ValoreCasa`, `FlagUfficiale` (constructor/importador oficial).
- `CodiceColoreEsterno`, `CodiceInterni`, `Colori`, `Esterni`, `Interni` (colores y tapicerías).
- `FlagVeicoloNuovo`, `FlagModelloSemplice`, `IndicatoreNazionalizzazione`.

Datos técnicos (~400 campos; XSD `DatiTecniciBase/DatiTecniciCompleti/CorpoDimensioni/MotorePrestazioni/MotoreTrasmissionePrestazioni`):
- **Motor**: `Alimentazione`, `Combustibile`/`TipoCombustibile`/`CodiceCombustibile`, `Cilindrata`, `NumeroCilindri`, `DisposizioneCilindri`, `ValvolePerCilindro`, `Sovralimentazione`/`TipoSovralimentazione`, `CodiceMotore`, `CodiceNucleoMotore`, `NucleoMotore`.
- **Prestaciones**: `PotenzaKW`, `PotenzaCV`, `PotenzaFiscale`, `PotenzaMaxGiriMinuto`, `PotenzaPiccoKW`/`PotenzaPiccoCV`, `CoppiaNm`, `CoppiaKgm`, `CoppiaMaxGiriMinuto`, `VelocitaMax`, `Accelerazione0100`, `RapportoPotenzaMassa`/`RapportoPotenzaMassima`.
- **Transmisión**: `Cambio`/`TipoCambio`, `NumeroMarce`, `Trazione`, `Trasmissione`.
- **Dimensiones/masas**: `LunghezzaMetri`, `LarghezzaMetri`, `AltezzaMetri`, `PassoMetri`, `MassaKG`, `MassaRimorchiabile`, `PortataKg`, `CapacitaBagagliaio1dm/2dm/3dm` (maletero mín/máx), `NumeroPorte`, `NumeroPosti`, `NumeroPostiAggiuntivi`/`Sottraibili`, `Tetto`.
- **Combustible/emisiones (NEDC)**: `Consumo1/2/3` (urbano/extraurbano/combinado), `Emissione1/2/3`, `EmissioneCO2`/`Co2`, `ClasseEuro`, `Normativa`, `Catalizzata`/`TipoCatalizzatore`, `DispositivoAntiInquinamento`, `CapacitaSerbatoioL`/`CapacitaSerbatoioKg`.
- **Neumáticos**: `PneumaticiMontabili`, `Pneumatico`, `Treno`, `Invernale`.
- **Bloque WLTP** (`DatiWltp/DatiTecniciCompletiWltp/CO2Wltp/ConsumiWltp/AutonomiaWltp`): `CO2Low/Medium/High/ExtraHigh` + `CO2Combinato` (+ versiones `Stimato`), `ConsumoLow/Medium/High/ExtraHigh/Combinato`, ciclos `CicliWltp`/`CicliWltpHybrid`, `Fuel1/Fuel2` desglosado urbano/extra/comb, `EquivalentAllElectric`, `ChargeSustaining`/`ChargeDepleting`.
- **Bloque eléctrico/batería** (`DatiBatteria`): `CapacitaLordakWh`, `CapacitaNettakWh`, `TensioneTotaleBatterie`, `NumeroElementiBatterie`, `MassaTotaleBatterieKg`, `SiglaTipoBatterie`/`CodiceTipoBatterie`, `Autonomia`/`AutonomiaMassima`/`AutonomiaMinima`/`AutonomiaUrbana`/`AutonomiaVelCostante`, `FunzionamentoElettricoPuro`.
- **Bloque recarga** (`DatiRicarica`): `PotenzaRicaricakW`/`PotenzaRicaricaRapida`, `TensioneRicaricaVolt`, `CorrenteRicaricaAmpere`, `TempoRicaricaOre/Minuti/Secondi`, `TempoRicaricaRapidaMin`, `CodiceTipoPresa`/`DescrizioneTipoPresa`, `CodiceModalitaRicarica`, `TipologiaCorrentePresa`.
- **Códigos homologación/constructor**: `CodiceOmologazione` (vía `GetCodiciOmologazione`), `DatiOmologazione`, `DatiTecniciOmologati`, `CodiciCasa` (vía `GetCodiciCasa`).
- **Otros**: `AltreInfo`, road tests/fiabilidad (mencionado en marketing), `ImmaginiRepertorio` (imágenes de repertorio).

Equipamiento (XSD `Equipaggiamento/EquipaggiamentoListino/EquipaggiamentoPacchetto` + reglas):
- `CodiceEquipaggiamento`, `Descrizione`, `Prezzo`/`PrezzoListino`, `Serie`/`SerieOpzionale`/`FlgSerieOpzionale` (de serie vs opcional), `FlagPack`/`ComposizionePack` (paquetes).
- **Reglas de configuración** (vía `GetEquipaggiamentiRegole`): `EquipaggiamentoEsclusione` (exclusiones), `EquipaggiamentoInclusione` (inclusiones), `EquipaggiamentoVincolo` (vínculos), `RaggruppamentoVincolo`, `CodiceQRTIncomp` (incompatibilidades), `CodiceOptIncluso/Escluso/Vincolato`.
- **Equipamiento normalizado** (`GetEquipNormalizzati` → `EquipaggiamentoNormalizzato`): mapeo a un diccionario estándar.
- **Equipamiento cualificante** (`EquipaggiamentoQualificante`): los opcionales que **mueven la quotazione**, con `ValoreAssoluto` y `ValorePercentuale`.
- **Listini ufficiali** completos con paquetes y vínculos técnicos/comerciales del fabricante.

#### 3.A.2 Infocar Bike (banca dati moto) [V]
- >2.700 motos/ciclomotores; **~50 specs por vehículo**; identificación marca/modelo/allestimento; `CodiceInfobikePRG`.
- Datos técnicos desde 2000; listini; quotazioni usado 9 años.

#### 3.A.3 Infocar Classic (banca dati clásicos) [V]
- Integración con **Ruoteclassiche**: valoración de coches, todoterreno, motos y **coches americanos** clásicos; `CodiceRuoteClassiche`, `ProgressivoRCL`, `CodiceRCLPrg`.

#### 3.A.4 Banca Dati Ricambi & Tempari (recambios y tiempos) [V]
- Identificación de pieza por matrícula / vehículo / código motor / diccionario técnico.
- `CodiceRicambio`, `DescrizioneRicambio`, `PrezzoListino` (listini actualizados + códigos constructor `CodiciCasa`).
- **Tiempos estándar** de desmontaje/reparación/sustitución (método **Microtempi**): `OreManoOpera`, `CostoOrarioManoOpera`, `TempoRicarica`/tiempos por intervención.
- **Disegni tecnici / esplosi** con zoom y identificación gráfica de pieza (`SvgCarrozzeria`, `ImmagineSvg`, `CodiceSVG`, `LinkSVG`, `VistaFoto`).
- Compatibilidad **TecDoc** (piezas equivalentes). [V]

### 3.B — AUTOMOTIVE (plataforma concesionario)

#### 3.B.1 Infocar Web (plataforma DMS / gestionale online) — producto estrella [V]
Software cloud + app móvil (iOS/Android). Módulos verificados:

**Identificación**
- Búsqueda **por targa** (`GetInfocarDaTarga`/`GetInfocarDaTargaAvanzato` → `DatoInfocarDaTarga`, `DatoAllestimentoTarga`): reconstruye versión/motorización/equipamiento.
- Búsqueda **por telaio/VIN** (`GetInfocarDaTelaio` + `GetConfigurazioneDaVIN` → `VeicoloDaVin` con `ListaEquipaggiamenti` + `ListaInformazioniCasa`): equipamiento de fábrica + info de casa.
- `RisultatoUnivoco`/`VersioniIndividuate` (resolución de ambigüedad de versión).

**Quotazioni Q|P** (valoración oficial Quattroruote)
- Tres valores (ver §3.B.3): **vendita**, **ritiro**, **web**; hasta 15 años; ajuste por km y estado.

**InstantWeb** (inteligencia de mercado online — motor Indicata)
- Analiza anuncios de usado online en tiempo real: oferta, demanda, precios. Campos: ver §3.B.4.

**Configuratore** (configurador VN)
- Todas las marcas; lógica oficial del fabricante; checkboxes de color (seleccionado/obligatorio/incompatible); selección versión/motorización/allestimento/optional con `EquipaggiamentoEsclusione/Inclusione/Vincolo`.

**Stato d'Uso** (informe de estado)
- Interfaz simplificada (app móvil); integrada con banca dati ricambi & tempari; `Stato di carrozzeria`, `Stato meccanico`, `InterventiCarrozzeria`, `InterventiMeccanica`.

**Stock control**
- Monitoreo por vehículo, KPIs personalizables, tiempo en stock (`giorni_in_vendita`), estado comercial, coherencia con la demanda (`Giacenze`, `Giacenza_generica`/`specifica`).

**Multipubblicatore** (publicador multi-portal)
- Publicación centralizada a: **Autoscout24, Subito.it, Quattroruote Usato, Moto.it, Vetrinamotori, Automoto, Tuttoannunci, Autosupermarket**. Códigos `CodificaAS24`/`CodiciAutoscout`/`CodiciPubblicazione`.

**Dispatcher (IA)** + **Image Management IA**
- Generación automática de anuncios optimizados (`GetDescrizioneIA` → `NoteIA`/`NoteAnnuncio`); procesado fotográfico automático + **watermark digital** anti-copia.

**Firma Elettronica Avanzata (FEA)**
- Firma de contratos dentro de Infocar Web (`SetFirmaDigitale`/`GetDocumentoFirmato`/`GetElencoDocumentiFirmati`): `Firmatario`, `StatoFirma`, `DocumentoFirmato`, `LinkFirma`, `Metadati`, `TipologiaDocumento`.

**Leadcars** — gestión de leads integrada en el ciclo de venta.

**Integraciones externas dentro de la ficha**:
- **CarVertical**: historial de vehículo, **siniestros**, historial de servicio, lecturas de odómetro, certificación. [V — vía partner, no dato propio]
- **Vincoli e Gravami**: integración directa con servicio **ACI** (`GetFermoAmministrativoEGravami` → `Esito`/`EsitoGravami`, `ServiziACI`, `FermoAmministrativo`, `NumeroPassaggi` de propiedad, `DataAttoProprieta`). [V]
- **Infocar PKC (Power Check Control)**: certificación de **eficiencia de batería** para BEV/PHEV (`GetBatteryStatusCertificate` → `BatteryStatus`, `LinkDownload`). [V]

#### 3.B.2 Infocar Preview (software de valores residuales / forecast) [V]
- Horizontes de previsión: **6, 12, 24, 36, 48, 60 meses** (turismos; hasta **72 meses** motos).
- Valores de **vendita** y **ritiro** para VN y VO.
- Personalización por **km previstos de recorrido** (VN) y por **fecha 1ª inmatriculación + fecha previsto rientro + km estimados** (VO).
- Clasificación de cada Codice Infocar en **6 categorías de valor residual** (capacidad de mantener valor en el tiempo) → cada vehículo tiene su **curva de depreciación**.
- Análisis de varianza vs modelos predictivos; historización de valores de ediciones anteriores.
- **Basket de vehículos** para análisis de tendencia de valores previsivos de una flota; impacto económico de toda la flota.
- Campos XSD (`PrevisioneNuovo`/`PrevisioneUsato`): `Mese`, `Percorrenza`, `VenditaAssoluta`, `RitiroAssoluto`, `VenditaPerc`/`RitiroPerc` (VN); `VenditaPercListino`/`RitiroPercListino` + `VenditaPercPAC`/`RitiroPercPAC` (VO, % sobre listino y sobre prezzo chiavi-in-mano). `AnnoPrevisione`/`MesePrevisione`, `Stimata` (flag estimado). API: `GetPrevisioneNuovo/UsatoStandard` y `...Personalizzata` (+ variantes `AF`).

#### 3.B.3 Quotazioni On Line (QOL) / Quotazioni Quattroruote [V]
**Tres quotazioni** (definiciones oficiales):
- **Quotazione di vendita** = valor al que el vehículo puede ser **comprado por un privado** (retail). Campo XSD `QuotazioneVendita`/`QuotazioneStandardVendita`/`QuotazioneMensileVendita`.
- **Quotazione di ritiro** = valor aplicado en **permuta ante un operador profesional** (trade-in). Campo `QuotazioneRitiro`/`QuotazioneStandardRitiro`/`QuotazioneMensileRitiro`.
- **Quotazione Web** = análisis de datos de mercado en tiempo real (InstantWeb). Campo `ValoreInstantWeb`.
Ajustes (XSD `DatoQuotazioneStandard`/`DatoQuotazionePersonalizzata`):
- `ChilometriTeorici`/`ChilometriTeoriciStandard`/`ChilometriTeoriciMensili` (km teóricos de referencia).
- `CorrettivoChilometrico` (**ajuste por km: +0,3% por cada 1.000 km por debajo de la media; −0,3% por encima**), `CorrettivoChilometricoApplicato`.
- `CorrettivoImmatricolazioneAutocarro` (corrección por matriculación como autocarro).
- `CorrettivoNoteQualificanti` (corrección por equipamiento cualificante reconocido por el mercado: absoluto o %).
- `EdizioneQuotazione`, `AnzianitaAllaEdizione` (antigüedad a la edición).
- **Quotazione storica** (`GetQuotazioneStorica`/`GetEdizioniStoriche` → `DatoQuotazioneStorica`): valor a una fecha pasada (clave seguros).
- **Quotazione certificata** (`GetQuotazioneCertificata` → `LinkStampaCertificata`): valoración certificada imprimible.

#### 3.B.4 InstantWeb / Valutazione Web (datos de mercado online — Indicata) [V]
Aporta 3 indicadores (press Indicata): **valor del anuncio web**, **time-to-sell (giacenza)**, **varianza de precio por geolocalización**.
Campos XSD (`InstantWebData`/`ValutazioneWebData`/`VeicoloAnnuncio`/`Annuncio`/`Rotazione`):
- `ValoreInstantWeb`, `ValoreAcquisto`, `ValoreVendita` (valores de mercado online: compra/venta).
- **Rotazione (días de venta/rotación)** `GiorniRotazione` + `Rotazione{Marca, Media, Mercato, Similare}` (rotación a nivel marca / media / mercado / similares).
- `AnalisiRotazione`, `InteressiGiorniVendita`, `GiorniVendita`.
- **Por anuncio competidor** (`VeicoloAnnuncio`/`Annuncio`): `Allestimento`/`version_name`, `Chilometri`/`km`, `Immatricolazione`, `PrezzoMercato`, **`PrezzoMercatoPerc` (price-to-market %)**, `ComparazionePrezzo`, `DifferenzaPrezzo` (delta vs valor), `DifferenzaKm`, `Venditore`/`publisher_name`/`publisher_phone`, `provenienza`, `region`/`province`/`town`/`geo`/`Latitudine`/`Longitudine` (geolocalización), `link`/`link_active` (enlace al anuncio).
- **Historial de precio del anuncio**: `primo_prezzo`, `ultimo_prezzo`, `numero_cambi_prezzo` (nº cambios de precio), `data_creazione`/`data_ultima_modifica`, `giorni_in_vendita`, **`scostamento_valutazione`** (desviación vs valoración).
- **Matriz de valoración multi-fuente** (`Valutazioni`, 20 campos): `Generica`/`Specifica`/`Privati` × escenarios `hard/medium/soft/custom`, con desglose **por portal** (`Privati_generica_autoscout24_*`, `Privati_generica_subito_*`). + `Numero_veicoli`/`Totale_db` (tamaño de muestra), `RangeKm`/`RangeAnni`/`RangeScarto` (rangos de búsqueda comparable), `AnalisiVeicoli` (online vs offline por marca/modelo/allestimento).

#### 3.B.5 Infocar Fleet [V]
- Gestión de car policy de empresa: configuración de perfil de conductor, set up de car list. [V — descripción de marketing; sin diccionario de campos público]

#### 3.B.6 Business Intelligence (automotive) [V]
- Análisis de mercado para soporte a lanzamientos de producto y gestión de cliente. [V]

### 3.C — ASSICURATIVO (seguros)

#### 3.C.1 Infocar Ins (banca dati assicurazioni) [V]
- Turismos, fuoristrada, VCL/pick-up vendidos en Italia últimos 10 años.
- Contenido: descripciones, **códigos de identificación**, características técnicas, **precios**, equipamiento, **quotazioni usato**.

#### 3.C.2 Insurance Pro (herramienta de valoración de siniestros) [V]
- Identificación por **targa** (hasta 1.000 consultas/abono), Codice Infocar o keyword.
- **Quotazioni Quattroruote en tiempo real** actualizadas al mes corriente.
- **Histórico 9 años (108 meses)** para valorar a fecha de siniestro (`QuotazioneStorica`).
- Análisis: prezzo di listino, allestimenti e optional principali.
- Cobertura: auto, SUV, VCL/pick-up, moto (moto en formato PDF). **Precio: €280 + IVA (€341,60) / 12 meses**.

#### 3.C.3 Valore Assicurato (publicación valor asegurado) [V]
- Publicación mensual sobre turismos, fuoristrada, VCL del mercado italiano (ventana 10 años).

#### 3.C.4 Business Intelligence (seguros) [V]
- **Network scoring**, **índice de riesgo de flota**, **clasificación de la red de talleres/reparadores**, analítica big data + formación dedicada.

### 3.D — AUTORIPARATIVO (taller/carrocería)

#### 3.D.1 Infocar Repair (preventivatore meccanica + carrozzeria) [V]
- Estimador mecánica + carrocería integrados; piezas originales y equivalentes; trazabilidad por codici casa.
- Campos preventivo (XSD `PreventivoMeccanica`/`PreventivoCarrozzeria`/`DatoDanno`): `Danno`, `Ricambio`/`CodiceRicambio`/`DescrizioneRicambio`, `ImportoRicambi`/`TotaleRicambi`, `OreManoOpera`/`CostoManodopera`/`ImportoManodOpera`/`TotaleManoOpera`, `CostoOrarioManoOpera`, `StringaInterventi`, `RicambiCarrozzeria`/`RicambiMeccanica`, `NotaCarrozzeria`/`NotaMeccanica`.
- **Daño guiado por SVG**: `GetSvgCarrozzeria`/`GetDanno` (selección gráfica de la pieza dañada), `GetCodiciRiparazione`/`...ConSimili` (códigos RT + vehículos similares).

#### 3.D.2 Tagliando / Manutenzione programmata (mantenimiento) [V]
- Planes de mantenimiento (XSD `PianoManutenzione`/`IntervalloTagliando`/`RicambioTagliando`): `GetPianiTagliando`, `GetIntervalliTagliando`, `GetPreventivoTagliando` → `DescrizionePiano`, `IntervalliSelezionati`, `RicambiTagliando`, `TotaleTagliando`, `TipologiaTagliando`.
- **Iconos de testigos** (`GetIconeSpie` → `IconaSpiaFile`, `CodiceSpia`).

#### 3.D.3 Infocar Wintouch / Infocar WINNC [V]
- **Wintouch**: control de tiempos de mano de obra y rentabilidad; integra contabilidad.
- **WINNC**: gestión del daño en carrocería, estimación automatizada, documentación cliente/aseguradora.

#### 3.D.4 Infocar Listini Ricambi Web [V]
- Consulta online de listini de recambios por matrícula. **Precio: €310 + IVA (flat 12 meses, consultas ilimitadas + 700 identificaciones por targa)**.

### 3.E — WEB SERVICES / API (capa de entrega de datos)
Dos endpoints SOAP de producción verificados:
- **ADSQPService** (moderno, `infocar.org/QPServices/Services/ADSQPService.svc`): **76 operaciones**.
- **InfocarService.asmx** (legacy, `infocar.org/webservicesinfocar/`): **29 operaciones**.
Catálogo de operaciones ADS (capacidad expuesta): `GetMarche`, `GetModelli(Completi)`, `GetAllestimenti`, `GetInfocarDaTarga(Avanzato)`, `GetInfocarDaTelaio`, `GetConfigurazioneDaTarga`, `GetConfigurazioneDaVIN`, `GetDatiTecniciDettagliati`, `GetDatiTecniciCompleti(ConWltp)`, `GetDatiTecniciBatterie`, `GetDatiWltpDinamici`, `GetEquipaggiamentiListino`, `GetEquipaggiamentiRegole`, `GetEquipNormalizzati`, `GetUltimiEquipCasa`, `GetListinoAllestimento`, `GetCodiciCasa`, `GetCodiciOmologazione`, `GetCodiciCarrozzeria`, `GetCodiciRiparazione(ConSimili)`, `GetQuotazioneStandard`, `GetQuotazionePersonalizzata`, `GetQuotazioneStorica`, `GetQuotazioneCertificata`, `GetQuotazioneNoteQualificanti`, `GetPrevisioneNuovo/UsatoStandard`, `GetPrevisioneNuovo/UsatoPersonalizzata` (+AF), `GetInstantWebData`/`GetNewInstantWebData`, `GetValutazioneWebData`, `GetInstantWebReportUrl`, `GetReportIndicata`, `GetDanno`, `GetPreventivoCarrozzeria/Meccanica/Tagliando`, `GetPianiTagliando`, `GetIntervalliTagliando`, `GetSvgCarrozzeria`, `GetIconeSpie`, `GetBatteryStatusCertificate`, `GetFermoAmministrativoEGravami`, `GetInfoProprieta`, `SetFirmaDigitale`/`GetDocumentoFirmato`/`GetElencoDocumentiFirmati`/`EliminaFirmaDigitale`, `GetDescrizioneIA`, `GetImmaginiRepertorio`, `GetCodiciAutoscout`/`GetCodiciPubblicazione`, `GetMarcheConfigurazioneVIN`, `GetMarcheWltpDinamici`, `GetCodiciInfocarEliminati`, `GetDizionariECodici`, `GetInterrogazioniReport`/`GetInterrogazioniTarga` (consumo), `GetVersioneServizio`, `GetEcho`.
- Distribución de Infocar Data también **"On demand" vía Web Service**. [V]
- Autenticación: credenciales (`credenziali`, `Account`, `ClientID`/`ClientSecret`, `CasUserName`/`WebServicesUserName`). Salida JSON o XML (`DatiReportJson`/`DatiReportXML`, `ResponseType`). [V — campos en XSD]

---

## 4. Metodología y fuentes de datos [V]

- **Banca Dati Auto desde 1980**: dato normalizado a partir de (1) **listini ufficiali** y fichas técnicas de fabricantes/importadores, (2) **códigos de homologación del CED del Ministerio de Transportes** (homologaciones depositadas), (3) vehículos efectivamente comercializados en Italia.
- **Codice INFOCAR**: clave única que identifica el allestimento; el sufijo **AM (Anno-Mese)** versiona cambios técnicos/comerciales. Es el "NatCode italiano" de facto.
- **Quotazioni**: elaboradas por el **equipo de Market Analysis** de Quattroruote a partir de la banca dati + **encuestas online a operadores profesionales** (sentiment de mercado), precios efectivos del usado y tendencias. Doble verdad explícita: **vendita** (lo que paga un privado / retail) vs **ritiro** (lo que da un profesional en permuta / trade-in).
- **Ajuste por km**: regla declarada **±0,3% por cada 1.000 km** respecto a la percorrenza teórica estándar.
- **Equipamiento cualificante**: solo los opcionales **reconocidos por el mercado** alteran la quotazione (valor absoluto o porcentual).
- **Microtempi**: método propio para tiempos de reparación/sustitución, elaborado por su estructura técnica en colaboración con confederaciones de artesanos.
- **InstantWeb / datos de mercado online**: provistos por **Indicata (grupo Autorola)** — scraping/normalización de anuncios de usado online en tiempo real → valor web, **giacenza/time-to-sell**, varianza geográfica de precio. Recíprocamente Indicata adopta la identificación por targa + banca dati Infocar. [V]
- **WLTP dinámico**: integra proveedores WLTP por marca (`GetMarcheWltpDinamici`/`WltpProvider`), con datos estimados marcados (`*Stimato`/`Stimata`).
- **Frecuencia**: quotazioni auto **mensual**, comerciales **bimestral**, moto **trimestral**; datos de mercado online **tiempo real**; historización por ediciones (`EdizioneQuotazione`, ediciones históricas hasta 9–10 años).
- **Repertorio de imágenes** y disegni tecnici/esplosi propios (`ImmaginiRepertorio`, SVG carrozzeria) para casi la totalidad del parque.

---

## 5. Entrega

[V] Modalidades:
- **Plataforma web cloud** ("gestionale online"): **Infocar Web** (login `account.quattroruotepro.it`).
- **App móvil iOS/Android**: módulo **Stato d'Uso** para peritación en campo.
- **Web Services SOAP** (2 endpoints, 76+29 operaciones): integración a sistemas del cliente; salida JSON/XML; autenticación por credenciales/ClientID-Secret.
- **Distribución "On demand"** de Infocar Data vía Web Service.
- **Integración DMS** (Infocar Web se integra con gestionales de concesionario).
- **Broadcasting / Multipubblicatore** a 8+ portales (Autoscout24, Subito.it, Quattroruote Usato, Moto.it, etc.).
- **Publicaciones / ficheros**: PDF (Valore Assicurato mensual, quotazione certificata, moto en Insurance Pro), informes.
- **Firma electrónica avanzada (FEA)** integrada (salida de documentos firmados).

---

## 6. Precio

- **Mayoritariamente bajo cotización** (contacto comercial). Dos puntos de precio **públicos verificados**:
  - **Insurance Pro**: **€280 + IVA (€341,60) / 12 meses**, hasta 1.000 consultas por targa. [V]
  - **Infocar Listini Ricambi Web**: **€310 + IVA / 12 meses**, consultas ilimitadas (flat) + 700 identificaciones por targa. [V]
- Modelo: **suscripción anual** + **límites de consultas** (campos de cuota en XSD: `InterrogazioniTotali`/`InterrogazioniResidue`/`InterrogazioniEffettuate`, `CreditiTotali`/`CreditiUsati`, `ReportsTotali`/`ReportsUtilizzati`, `NumeroLicenze`) → modelo **pay-per-use / por créditos** en la API. [V]
- Referencia consumer (no B2B): Quattroruote.it Q Premium €6,90/mes. [V — contexto]
- Importe de Infocar Web / Infocar Data / Preview / API: **no público (GAP)** — cotización a medida. [V que no es público]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. Mapeo pantalla/sección → dato.

### Ficha de vehículo en Infocar Web (resultado de búsqueda por targa/VIN) [V]
- **Cabecera**: identificación resuelta (Marca · Modello · Allestimento · Codice Infocar) + `AnnoMeseImmatricolazione`. Si hay ambigüedad → selector de versiones (`VersioniIndividuate`).
- **Pestaña Dati tecnici**: ~400 campos agrupados (Motor / Prestazioni / Dimensioni-Masse / Consumi-Emissioni / WLTP / Batteria-Ricarica para EV). Datos estimados marcados con sufijo "Stimato".
- **Pestaña Equipaggiamenti**: serie vs optional, paquetes, reglas de incompatibilidad; resaltado del **equipamiento cualificante** que afecta al valor.
- **Bloque Quotazione (lateral/inferior)**: tras introducir **targa + km reales** → **Quotazione di vendita** y **Quotazione di ritiro** lado a lado, con el `CorrettivoChilometrico` aplicado visible y la `EdizioneQuotazione`. Botón a **Quotazione certificata** (PDF imprimible).
- **Integraciones en la ficha** (botones/iconos): CarVertical (historial/siniestros), Vincoli e Gravami (ACI), Infocar PKC (batería BEV).

### Pantalla InstantWeb / Valutazione Web (mercado en tiempo real) [V]
- **KPI superior**: `ValoreInstantWeb` (valor de mercado online) + `GiorniRotazione`/Rotazione (días de venta / rotación: media, mercado, similares) como proxy de demanda.
- **Lista de anuncios comparables**: por fila → versión, km, inmatricolazione, **PrezzoMercato + PrezzoMercatoPerc (price-to-market %)**, **DifferenzaPrezzo** (delta vs valoración), `scostamento_valutazione`, **giorni_in_vendita**, **numero_cambi_prezzo** (con `primo_prezzo`→`ultimo_prezzo`), venditore + provenienza + ubicación (geo/region/province/town), enlace al anuncio (`link`).
- **Mapa**: geolocalización de los anuncios (`Latitudine`/`Longitudine`) para varianza de precio por zona.
- **Matriz de escenarios** (`Valutazioni`): valor en escenarios hard/medium/soft y por canal (concesionario vs privados; Autoscout24 vs Subito) — distinta "agresividad" de pricing.

### Pantalla Infocar Preview (valores residuales) [V]
- **Tabla/curva de depreciación**: filas por horizonte (6/12/24/36/48/60 m), columnas **Vendita** y **Ritiro** en valor **absoluto** y **% sobre listino / % sobre PAC**, condicionadas a `Percorrenza` (km).
- **Categoría de retención de valor** (1 de 6) del vehículo.
- **Basket / flota**: vista agregada de tendencia de valores previsivos + impacto económico de la flota; comparación con ediciones históricas.

### Stock / Giacenze (panel concesionario) [V]
- Por vehículo en stock: `giorni_in_vendita`, estado comercial, KPI personalizables, coherencia con demanda (giacenza generica vs specifica).
- **Cálculo de pricing del concesionario** (`CalcoloPrezzoAcquisto`/`CalcoloPrezzoVendita`): `PrezzoMassimoAcquisto`, `Profitto`, `SpeseRipristino` (reacondicionamiento), `SpeseMarketing`, `CostoGaranzia`, `InteressiGiorniVendita`, `Deprezzamento`, `RiduzionePianificata`, `PrezzoVenditaPreventivato`.

### Preventivatore taller/carrozzeria (Infocar Repair) [V]
- **Selección gráfica del daño sobre SVG** de la carrocería → genera líneas de `Ricambio` (importe) + `ManoOpera` (horas × tarifa) → `TotaleRicambi` + `TotaleManoOpera` + total preventivo. Iconos de testigos/spie como ayuda.

### Insurance Pro (peritación de siniestro) [V]
- Input targa → identificación + **Quotazione storica a fecha de siniestro** (de 108 meses de histórico) + listino/optional → valor para liquidación.

### Multipubblicatore / Dispatcher [V]
- Una sola interfaz → genera anuncio (descripción IA, fotos con watermark) y lo despacha a 8+ portales con su codificación específica.

---

## 8. Diferencial (lo que ofrece y otras no)

- [V] **Autoridad editorial "Quattroruote"**: las **Quotazioni Quattroruote** son referencia de mercado/jurídica en Italia; usadas por el **99% de aseguradoras**. Marca centenaria (Editoriale Domus 1929, revista 1956, dato 1980).
- [V] **Dato + plataforma operativa en un solo proveedor**: no solo venden el valor, venden el **gestionale del concesionario** (Infocar Web) donde el dato se *usa* — identificación, configurador, stock, pricing, publicación multi-portal, **firma electrónica**, leads, IA de anuncios. Cobertura del ciclo comercial completo.
- [V] **Triple valor de usado nativo**: **vendita (retail)** + **ritiro (trade-in)** + **web (mercado online en tiempo real)** en la misma ficha, con ajuste por km transparente (±0,3%/1.000 km) y **equipamiento cualificante** valorizado individualmente.
- [V] **InstantWeb (Indicata)**: price-to-market %, **days-to-sell/rotación**, historial de cambios de precio por anuncio, geolocalización, y **matriz de escenarios hard/medium/soft por canal y por portal** (Autoscout24/Subito) — granularidad de pricing competitivo poco común.
- [V] **Quotazione storica 9–10 años + quotazione certificata (PDF)** — pensado para **peritación de siniestros** y liquidación aseguradora (nicho donde domina en IT).
- [V] **Profundidad técnica WLTP + EV**: bloque batería (kWh bruto/neto, nº celdas, tensión, masa) + recarga (tipo presa, potencia kW, tiempos, modalidad) + **Infocar PKC** (certificado de salud de batería BEV/PHEV) — diferencial frente a guías de valoración clásicas.
- [V] **Integración ACI nativa** (fermo amministrativo, gravami, passaggi di proprietà) y **CarVertical** (historial/siniestros) dentro de la ficha — el dato legal/historial que Eurotax IT no expone.
- [V] **Vertical taller completo**: Microtempi propios + esplosi/SVG + preventivatore mecánica y carrocería + planes de tagliando, integrado con la valoración (estado de uso descuenta del valor).
- [V] **API SOAP madura y muy granular** (76+29 métodos, JSON/XML, modelo por créditos) — superficie de integración amplia y documentada (WSDL/XSD públicos).

## 9. Gaps (lo que NO ofrece / no expone)

- [V] **Cobertura solo Italia**: no es pan-europeo (Eurotax/Autovista/DAT cubren 15–27 mercados). Sin codificación armonizada cross-border ni arbitraje geográfico internacional.
- [V] **Sin historial de siniestros/km propio**: el historial de daños/odómetro lo aporta **CarVertical** (tercero), no es dato propio; sin verificación antifraude de cuentakilómetros propia.
- [V] **Precios opacos**: solo 2 importes públicos (Insurance Pro €280, Listini Ricambi €310); Infocar Web/Data/Preview/API **bajo cotización** (GAP de importe).
- [A] **Documentación API orientada a SOAP/WSDL** (no REST/OpenAPI público); puede ser barrera para integradores modernos. No se publican rate limits ni diccionario en lenguaje de negocio (solo el XSD técnico).
- [V] **TCO/coste total de propiedad no es producto explícito** (vs Car Cost Expert de Autovista): hay piezas (depreciación, mantenimiento, recambios) pero **no un módulo TCO empaquetado** descubrible.
- [V] **Consultoría pre-lanzamiento de VR para OEM** (tipo "Car to Market") **no ofertada** como tal; Infocar Preview es forecast sobre catálogo, no consultoría con drivers de marca.
- [A] **Datos EV de mercado/penetración/batería a nivel industria** (tipo EV Volumes) no ofertados: la profundidad EV es a nivel de **especificación de vehículo**, no de inteligencia de mercado de baterías.
- [V] **Moto en seguros aún en PDF** (no totalmente servido por API en ese vertical). [V — declarado en Insurance Pro]
- [A] **Marketing rehúsa enumerar el diccionario**: las páginas de producto hablan de beneficios; el catálogo atómico real **solo es observable vía el XSD** del web service (lo que esta auditoría explotó).

---

## 10. Fuentes (URLs)

- https://www.quattroruotepro.it/ — homepage, navegación, líneas de producto.
- https://www.quattroruotepro.it/en/automotive-2/ — catálogo automotive (Infocar Web/Preview/QOL/Fleet/Bike/Classic/BI).
- https://www.quattroruotepro.it/prodotto/infocar-web/ — módulos de Infocar Web (identificación, Q|P, InstantWeb, configuratore, stato d'uso, stock, multipubblicatore, IA, FEA, Leadcars, CarVertical, ACI, PKC).
- https://www.quattroruotepro.it/prodotto/infocar-data/ y /banca-dati-auto-infocar-data/ — banca dati auto (~400 datos, Codice Infocar/AM, listini, omologazione).
- https://www.quattroruotepro.it/banche-dati/ — Infocar Data / Bike / Ricambi & Tempari (coberturas).
- https://www.quattroruotepro.it/prodotto/infocar-preview/ — valores residuales (6–60 m, 6 categorías, basket).
- https://www.quattroruotepro.it/prodotto/quotazioni-on-line/ — quotazione vendita/ritiro/web, ±0,3%/1.000 km, frecuencias.
- https://www.quattroruotepro.it/quotazioni-quattroruote-.../quotazioni-quattroruote-fonti-informative/ — metodología (BD 1980, segmentos A–J, trim L0-L3/P0-P3/V0-V3, encuestas online).
- https://www.quattroruotepro.it/en/insurance/ y /prodotto/infocar-ins/ y /prodotto/infocar-insurance-pro/ — seguros (Infocar Ins, Insurance Pro €280, Valore Assicurato, 108 meses, BI scoring).
- https://www.quattroruotepro.it/autoriparativo/ — taller (Infocar Repair, Wintouch, WINNC, Ricambi & Tempari, Microtempi).
- https://www.quattroruotepro.it/prodotto/infocar-listini-ricambi-web/ — €310+IVA flat.
- https://www.quattroruotepro.it/chi-siamo/ — identidad (Editoriale Domus, Rozzano, P.IVA 07835550158, capital €5M, 12 segmentos).
- **https://www.infocar.org/QPServices/Services/ADSQPService.svc?wsdl** + `?xsd=xsd0..6` — **WSDL/XSD de producción** (76 operaciones, 1.104 nombres, diccionario atómico completo). *Fuente primaria de §3.*
- **http://www.infocar.org/webservicesinfocar/infocarservice.asmx?WSDL** — 2º web service legacy (29 operaciones).
- https://www.edidomus.it/it/press/2021/02/23/quattroruote-professional-partnership-strategica-con-indicata.html — partnership **Indicata/Autorola** (valor web, time-to-sell, geo-varianza).
- https://it.wikipedia.org/wiki/Editoriale_Domus + https://www.edidomus.it/ — grupo, fundación 1929, marcas, Sofia Bordone.
- https://www.karma-software.com/kars/banca-dati-quattroruote-professional.html — **reseller independiente** (cross-verificación: 6.000 turismos / 3.800 VCL / 50.000+21.000 fuori produzione, desde 1980/1993, Microtempi, esplosi).
- https://www.touchpoint.news/2022/03/30/editoriale-domus-... — contexto editorial Quattroruote/Ruoteclassiche.

> Verificación: §3 (campos atómicos) procede del **parseo directo del XSD de producción** (PyMuPDF no; descarga curl + parse Python del esquema XML, 689 KB) → nombres reales, no marketing. Identidad y coberturas verificadas con ≥2 fuentes (página oficial + reseller independiente + prensa de grupo). Precios: solo los 2 importes públicos hallados; resto bajo cotización (GAP declarado, no inventado).
