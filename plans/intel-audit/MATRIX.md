# Catálogo de campos × cobertura (matriz)

> Derivado de **109** auditorías. 6878 campos atómicos únicos (normalizados, pre-canonicalización).
> Subdominios: valuation 28, wholesale-intelligence 17, portal-insights 17, market-intelligence 14, official-data 11, vin-history 9, spec-catalog 6, valuation (etiqueta de vertical cardeep; NO existe como subdominio DNS real — valuation/values/valuengine/api/developer/portal/app.blackbook.com no resuelven [HTTP 000], y /valuation/ devuelve 403) 1, valuation (NO RESUELVE a fecha de auditoría — DNS NXDOMAIN para valuation.audatex.es y valuation.audatex.com; www.audatex.es tampoco conecta ni desde egress español, servidor retirado tras el rebrand a Solera). La capacidad "valuation" existe como PRODUCTO: AudaValue/VALUEpilot/Valuation Manager/ICV (EU), Typical Market Value + Autosource (US/global) y valor de mercado de AUTOonline (ES) 1, valuation.autotelex.nl = host de backend/API de valoración (devuelve "webserver is functioning normally"; no es UI pública, es el endpoint del webservice de valoración SOAP/XML). APIs públicas con Swagger viven bajo *.autotelexpro.nl. [V] 1, valuation.motornet.it NO EXISTE (DNS NXDOMAIN/ENOTFOUND). La valoración se sirve por adm.motornet.it (AutoDataManager, portal con login) y www.motornet.it; portal legacy www2.motornet.it/portale devuelve 503. 1, valuation (etiqueta de vertical cardeep; valuation.orangebookvalue.com NO resuelve - NXDOMAIN/HTTP 000 verificado 2026-06-30; pero orangebookvalue.com/valuation SÍ existe HTTP 200 y es la calculadora núcleo) 1, valuation.levi-itzhak.co.il does NOT resolve (DNS ERR_NAME_NOT_RESOLVED, verified). No such subdomain exists. Real valuation surfaces: free app (com.levinew.app), B2B agents portal (portal.levi-itzhak.co.il / portal01.levi-itzhak.co.il, Cloudflare-gated login), public model-code conversion tool (portal.levi-itzhak.co.il/leviconvert/PublicConversion.aspx), website + printed monthly magazine. 1, VERIFICADO que el subdominio "market-intelligence" NO existe: market-intelligence.indicata.com no resuelve (HTTP 000) e indicata.com/market-intelligence/ devuelve 404. "Market intelligence" es la categoria/descriptor del producto, no un subdominio. El subdominio operativo real es pro.indicata.com (plataforma SaaS, login federado AWS Cognito via auth.indicata.com). 1

## Table-stakes (≥38/109 empresas) — cardeep DEBE tenerlos

| Campo | nº | Empresas (muestra) |
|---|---|---|
| Marca | 93 | ACV Auctions, ALG (Automotive Lease Guide) — JD Power ALG, AUTO1 Group, Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc) |
| Modelo | 93 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones), ANWB Koerslijst (Autowaarde berekenen), AUTO1 Group, Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc) |
| Kilometraje / odómetro | 85 | ACV Auctions, ALG (Automotive Lease Guide) — JD Power ALG, AUTO1 Group, Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc) |
| Motor / potencia | 84 | ACV Auctions, ANWB Koerslijst (Autowaarde berekenen), AUTO1 Group, Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc) |
| Versión / trim | 83 | AUTO1 Group, Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc), AutoCheck (by Experian), AutoGrab |
| Geolocalización / región | 76 | ACV Auctions, ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones), Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc), AutoCheck (by Experian) |
| VIN | 75 | ACV Auctions, ALG (Automotive Lease Guide) — JD Power ALG, AUTO1 Group, Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc) |
| Carrocería / segmento | 74 | ALG (Automotive Lease Guide) — JD Power ALG, AUTO1 Group, Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc), AutoCheck (by Experian) |
| Ventas / matriculaciones | 65 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones), AUTO1 Group, Audatex España (Solera), Auto Trader UK (Autotrader Group plc), AutoCheck (by Experian), AutoGrab |
| Concesionario / vendedor | 63 | ACV Auctions, ANWB Koerslijst (Autowaarde berekenen), AUTO1 Group, Accu-Trade (AccuTrade), AutoGrab, AutoUncle |
| Transmisión | 62 | AUTO1 Group, Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc), AutoGrab, AutoScout24 |
| Equipamiento opcional | 57 | ACV Auctions, ALG (Automotive Lease Guide) — JD Power ALG, Audatex España (Solera), Auto Trader UK (Autotrader Group plc), AutoGrab, AutoUncle |
| Historial de siniestros | 57 | ACV Auctions, ANWB Koerslijst (Autowaarde berekenen), Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc), AutoCheck (by Experian) |
| Año / fecha | 56 | ACV Auctions, ALG (Automotive Lease Guide) — JD Power ALG, Accu-Trade (AccuTrade), AutoCheck (by Experian), AutoGrab, AutoUncle |
| Combustible | 56 | AUTO1 Group, Auto Trader UK (Autotrader Group plc), AutoCheck (by Experian), AutoGrab, AutoScout24, Autorola |
| Color | 54 | AUTO1 Group, Accu-Trade (AccuTrade), Audatex España (Solera), AutoGrab, AutoScout24, AutoUncle |
| Oferta / inventario (volumen) | 51 | ACV Auctions, ALG (Automotive Lease Guide) — JD Power ALG, ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones), Accu-Trade (AccuTrade), Auto Trader UK (Autotrader Group plc), AutoGrab |
| Retail / private value | 48 | ACV Auctions, ALG (Automotive Lease Guide) — JD Power ALG, ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones), AutoGrab, Autovista Group, Black Book (National Auto Research — Hearst) |
| CO2 / emisiones | 44 | Auto Trader UK (Autotrader Group plc), AutoCheck (by Experian), AutoGrab, AutoScout24, AutoUncle, Autovista Group |
| Carga financiera / prenda | 44 | ALG (Automotive Lease Guide) — JD Power ALG, Accu-Trade (AccuTrade), Auto Trader UK (Autotrader Group plc), AutoCheck (by Experian), Autotelex B.V., Black Book (National Auto Research — Hearst) |
| Índice de demanda | 42 | ALG (Automotive Lease Guide) — JD Power ALG, Accu-Trade (AccuTrade), Auto Trader UK (Autotrader Group plc), AutoGrab, AutoUncle, Autorola |
| Nº de propietarios | 41 | Accu-Trade (AccuTrade), Audatex España (Solera), AutoCheck (by Experian), AutoGrab, Autotelex B.V., Autovista Group |
| Dimensiones / peso | 39 | AutoGrab, Autotelex B.V., Autovista Group, BCA (British Car Auctions), Black Book (National Auto Research — Hearst), CARFAX |
| Días en stock / time-to-sell | 39 | Accu-Trade (AccuTrade), Audatex España (Solera), Auto Trader UK (Autotrader Group plc), AutoGrab, Autorola, Autovista Group |
| ITV / MOT / inspección | 38 | ACV Auctions, Auto Trader UK (Autotrader Group plc), AutoCheck (by Experian), AutoGrab, BCA (British Car Auctions), CCC Intelligent Solutions |
| Trade / wholesale value | 38 | ALG (Automotive Lease Guide) — JD Power ALG, AUTO1 Group, Accu-Trade (AccuTrade), AutoGrab, AutoUncle, Autotelex B.V. |

## Diferenciadores / nicho (≤2 empresas) — oportunidad para cardeep

| Campo | nº | Empresa(s) |
|---|---|---|
| 360度内装画像 (360 interior: roof/driver/rear, zoom) | 2 | Autohome (汽车之家), USS (ユー・エス・エス) Co., Ltd. |
| Año (del VIN) | 2 | Audatex España (Solera), REPUVE — Registro Público Vehicular |
| Aantal deuren | 2 | ANWB Koerslijst (Autowaarde berekenen), RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| 车贷ABS投资支持 (auto-loan ABS investment support) | 2 | Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd., mobile.de |
| Acquisition Insights: local market activity | 2 | CarGurus, CarOffer (a CarGurus company) |
| ACV (Actual Cash Value) | 2 | ClearVin, IAA (Insurance Auto Auctions) |
| Additional Equipment | 2 | CCC Intelligent Solutions, Vehicle Databases |
| airbags | 2 | IAA (Insurance Auto Auctions), Vehicle Databases |
| Announcements (defectos que disparan arbitraje) | 2 | Copart, Inc., Cox Automotive |
| APR | 2 | Cox Automotive Europe, JATO Dynamics |
| artEndDate (Additional Rate of Tax End Date) | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| aspiration | 2 | AutoGrab, DataOne Software (DataOne, LLC) |
| Auction end time / time remaining | 2 | Autorola, Dealer Auction |
| auction_price | 2 | Stat.vin (1VIN STAT), Vehicle Databases |
| AutoCheck Score (1-100) | 2 | AutoCheck (by Experian), Experian Automotive (AutoCheck) |
| AutoGrade condition score (0.0-5.0) | 2 | Manheim, OPENLANE |
| automatedVehicle | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| Average sold price (wholesale) | 2 | Cox Automotive Europe, Dealer Auction |
| average vehicle age | 2 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH), Dealer Auction |
| axles | 2 | NHTSA vPIC (Product Information Catalog and Vehicle Listing), mobile.de |
| badge | 2 | AutoGrab, Encar (엔카닷컴 / Encar.com) |
| Besitzumschreibungen (volumen de transferencias de propiedad) | 2 | AutoScout24, DAT (Deutsche Automobil Treuhand GmbH) |
| body_subtype | 2 | DataOne Software (DataOne, LLC), MarketCheck (MarketCheck Cars Inc) |
| Body-type (filter dimension) | 2 | Autovista Group, S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Build Sheet (OEM options/packages by VIN) | 2 | CCC Intelligent Solutions, Copart, Inc. |
| Código eco (CODIGO_ECO_ITV) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Código postal (ajuste geográfico de precio) | 2 | Dirección General de Tráfico (DGT), coches.net |
| Cargo volume (l) | 2 | DataOne Software (DataOne, LLC), Schwacke (Schwacke GmbH / JD Power Autovista) |
| Catalogusprijs | 2 | ANWB Koerslijst (Autowaarde berekenen), RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Categoría de vehículo eléctrico (PHEV/REEV/HEV/BEV) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| category | 2 | INDICATA (Autorola Group), mobile.de |
| Central locking | 2 | BCA (British Car Auctions), CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| chrome_style_id | 2 | Accu-Trade (AccuTrade), ChromeData (part of J.D. Power / Autodata Solutions Division) |
| clase (class) | 2 | Fasecolda — Guía de Valores, REPUVE — Registro Público Vehicular |
| Clasificación Reglamento de Vehículos (Anexo II RD 2822) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Clean Loan Value (credito potencial sobre el vehiculo) | 2 | ALG (Automotive Lease Guide) — JD Power ALG, J.D. Power Valuation Services |
| 'Coming Soon' placeholder (vehiculo en recon) | 2 | ACV Auctions, MAX Digital (ACV MAX) |
| Company name (lead) | 2 | Autotelex B.V., Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| competitive positioning | 2 | GlobalData Automotive, INDICATA (Autorola Group) |
| Compression ratio | 2 | RedBook, Schwacke (Schwacke GmbH / JD Power Autovista) |
| Condition report (damage / warning lights / missing equipment / MOT advisories) | 2 | CarOffer (a CarGurus company), Dealer Auction |
| constructionYear | 2 | Autotelex B.V., mobile.de |
| Contraseña de homologación | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| couleur (color) | 2 | HistoVec, L'argus (Cote Argus®) |
| Country code | 2 | RedBook, Schwacke (Schwacke GmbH / JD Power Autovista) |
| country_of_origin | 2 | AutoGrab, IAA (Insurance Auto Auctions) |
| Current bid | 2 | Mahindra First Choice Wheels (MFCWL), OPENLANE |
| Current state of title | 2 | Experian Automotive (AutoCheck), NMVTIS / VehicleHistory.gov |
| cylinderCapacity [NV bulk] | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| Daños (damages) | 2 | AUTO1 Group, Cox Automotive Europe |
| Daily Vehicle Volume (Pulse KPI) | 2 | Black Book (National Auto Research — Hearst), Canadian Black Book |
| data_source | 2 | MarketCheck (MarketCheck Cars Inc), Vehicle Databases |
| dateOfLastV5CIssued | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| Days to turn (days-to-sell) | 2 | Black Book (National Auto Research — Hearst), Canadian Black Book |
| defect.dangerous (boolean) | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| defect.text | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| defect.type (FAIL/ADVISORY/MAJOR/DANGEROUS/MINOR/USER ENTERED) | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| Derivative | 2 | Auto Trader UK (Autotrader Group plc), cap hpi (CAP + HPI, a Solera company) |
| Destination charge | 2 | Black Book (National Auto Research — Hearst), Vehicle Databases |
| detailed_history_event_date | 2 | CARFAX, Experian Automotive (AutoCheck) |
| Diagnostic Trouble Codes (DTCs) | 2 | ACV Auctions, Manheim |
| Distance from buyer | 2 | Cars Commerce (Cars.com Inc.), Dealer Auction |
| Distancia entre ejes 1-2 (DISTANCIA_EJES_12_ITV) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Distintivo ambiental (0 Emisiones/ECO/C/B) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| distintivo ambiental DGT (0 / ECO / B / C / sin etiqueta) | 2 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA), km77.com |
| Drive (drivetrain type) | 2 | AutoGrab, RedBook |
| Durchschnittspreis Gebrauchtwagen (precio medio VO) | 2 | AutoScout24, DAT (Deutsche Automobil Treuhand GmbH) |
| Eco-innovación (ECO_INNOVACION_ITV) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| electrification_level | 2 | NHTSA vPIC (Product Information Catalog and Vehicle Listing), Vehicle Databases |
| Electronic Stability Control (ESC) | 2 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group), NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Estimated market value | 2 | Cars Commerce (Cars.com Inc.), HPI Check (HPI Ltd, a Solera company) |
| european target price | 2 | Autorola, INDICATA (Autorola Group) |
| euroStatus | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| event_type | 2 | Mahindra First Choice Wheels (MFCWL), Vehicle Databases |
| Ex-showroom price | 2 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group), Mahindra First Choice Wheels (MFCWL) |
| exhaust_system | 2 | BCA (British Car Auctions), Vehicle Databases |
| Fair Market Value | 2 | CCC Intelligent Solutions, MarketCheck (MarketCheck Cars Inc) |
| feature category | 2 | Auto Trader UK (Autotrader Group plc), DataOne Software (DataOne, LLC) |
| feature.name | 2 | ChromeData (part of J.D. Power / Autodata Solutions Division), L'argus (Cote Argus®) |
| Fecha de tramitación (FEC_TRAMITACION) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Fog lights | 2 | BCA (British Car Auctions), CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Forecast horizon (months, up to 120 / 6yr-200k km) | 2 | RedBook, Schwacke (Schwacke GmbH / JD Power Autovista) |
| Front-end gross profit | 2 | MAX Digital (ACV MAX), vAuto |
| fuel | 2 | AutoGrab, mobile.de |
| Fuel Capacity (L) | 2 | RedBook, Vehicle Databases |
| Fuel Delivery | 2 | AutoGrab, RedBook |
| Guide price | 2 | BCA (British Car Auctions), Motorway |
| gvwr | 2 | ChromeData (part of J.D. Power / Autodata Solutions Division), Vehicle Databases |
| hammer_price | 2 | BCA (British Car Auctions), MarketCheck (MarketCheck Cars Inc) |
| History-Based Value (VIN-specific value) | 2 | CARFAX Canada, S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| impressions | 2 | CLASSIC.COM, Urban Science |
| Indicador de renting (RENTING / Servicio de Renting) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| instant offer (match price) | 2 | CarOffer (a CarGurus company), Edmunds |
| interior_condition | 2 | OPENLANE, Vehicle Databases |
| interior_features | 2 | TrueCar, Vehicle Databases |
| invoice | 2 | ChromeData (part of J.D. Power / Autodata Solutions Division), Vehicle Databases |
| Invoice price | 2 | Black Book (National Auto Research — Hearst), DataOne Software (DataOne, LLC) |
| [MED·Habitabilidad 2ª fila] Isofix (cm) | 2 | Autohome (汽车之家), km77.com |
| IVA | 2 | Quattroruote Professional / Infocar (Editoriale Domus), km77.com |
| KBB (Kelley Blue Book) value | 2 | ACV Auctions, Stockwave (vAuto · Cox Automotive) |
| Kenteken (input licensePlate) | 2 | ANWB Koerslijst (Autowaarde berekenen), RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Kilometers Driven (odometro) | 2 | Mahindra First Choice Wheels (MFCWL), Orange Book Value (OBV) |
| Kilometerstand (mileage) | 2 | AutoScout24, Schwacke (Schwacke GmbH / JD Power Autovista) |
| latitude | 2 | Copart, Inc., MarketCheck (MarketCheck Cars Inc) |
| Listing type (Fixed-price / Auction / Make-offer) | 2 | CLASSIC.COM, ClearVin |
| Llamadas a revisión pendientes (recalls) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Local market data (oferta/demanda retail local) | 2 | ACV Auctions, Accu-Trade (AccuTrade) |
| Longitud (pintura) | 2 | Audatex España (Solera), km77.com |
| longitude | 2 | Copart, Inc., MarketCheck (MarketCheck Cars Inc) |
| Manufacturer build data (OEM/factory specs) | 2 | Manheim, vAuto |
| Manufacturer Name | 2 | Historia Pojazdu (gov.pl) / CEPiK, NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| markedForExport | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| market_alerts (DMS) | 2 | AutoUncle, CLASSIC.COM |
| market average price | 2 | CarOffer (a CarGurus company), TrueCar |
| marketability score | 2 | Autorola, INDICATA (Autorola Group) |
| Marque | 2 | HistoVec, La Centrale |
| Masa en orden de marcha (MASA_ORDEN_MARCHA_ITV) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| max_torque | 2 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group), DataOne Software (DataOne, LLC) |
| Maximum price | 2 | Black Book (National Auto Research — Hearst), Canadian Black Book |
| Mean price | 2 | Black Book (National Auto Research — Hearst), Canadian Black Book |
| mechanical | 2 | Copart, Inc., Vehicle Databases |
| Median price | 2 | Black Book (National Auto Research — Hearst), Canadian Black Book |
| Merk (entrada manual) | 2 | ANWB Koerslijst (Autowaarde berekenen), RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| message (estado de la peticion) | 2 | ChromeData (part of J.D. Power / Autodata Solutions Division), Datium Insights |
| Minimum price | 2 | Black Book (National Auto Research — Hearst), Canadian Black Book |
| modelDescription (modelo) | 2 | Datium Insights, mobile.de |
| monthly payment | 2 | Cox Automotive Europe, S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| motExpiryDate | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| motStatus (Valid/Not valid/No details held/No results) | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| Municipio | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), MSI - Sistemas de Inteligencia de Mercado, S.A. |
| MUVVI index value (Jan 1997=100) | 2 | Cox Automotive, Manheim |
| Número de plazas máximo (NUM_PLAZAS_MAX) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Número de transmisiones (NUM_TRANSMISIONES) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| NADA value | 2 | MAX Digital (ACV MAX), Stockwave (vAuto · Cox Automotive) |
| NatCode (national search-tree code) | 2 | Autovista Group, Schwacke (Schwacke GmbH / JD Power Autovista) |
| Number of keys | 2 | Autorola, Motorway |
| Number of price changes | 2 | Black Book (National Auto Research — Hearst), Canadian Black Book |
| Numero de plazas (seats) | 2 | MSI - Sistemas de Inteligencia de Mercado, S.A., Sumauto (SUMAUTO MOTOR S.L.) |
| Nutzungsausfallentschaedigung (loss-of-use comp.) | 2 | DAT (Deutsche Automobil Treuhand GmbH), Schwacke (Schwacke GmbH / JD Power Autovista) |
| oil_capacity | 2 | DataOne Software (DataOne, LLC), Vehicle Databases |
| On-Road (GST) price | 2 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group), Mahindra First Choice Wheels (MFCWL) |
| Paint condition | 2 | OPENLANE, Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Part-exchange value | 2 | Auto Trader UK (Autotrader Group plc), Cox Automotive Europe |
| Parts prices (OEM-sourced, monthly) | 2 | Glass's, cap hpi (CAP + HPI, a Solera company) |
| Photo count | 2 | CLASSIC.COM, Cars Commerce (Cars.com Inc.) |
| plant_city | 2 | NHTSA vPIC (Product Information Catalog and Vehicle Listing), Vehicle Databases |
| Plate change history (previous plates + dates) | 2 | Motorway, cap hpi (CAP + HPI, a Solera company) |
| plate_state | 2 | AutoGrab, Vehicle Databases |
| Plazas de pie (PLAZAS_PIE) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| PPSR certificate (finance owing / encumbrance) | 2 | RedBook, carsales (carsales.com.au) |
| Precio (price) | 2 | MSI - Sistemas de Inteligencia de Mercado, S.A., km77.com |
| price_drop_indicator | 2 | CarGurus, iSeeCars |
| Private sale price | 2 | AutoGrab, RedBook |
| Private sale value | 2 | Auto Trader UK (Autotrader Group plc), HPI Check (HPI Ltd, a Solera company) |
| Procedencia (fabricación nacional/importación UE/no UE/subasta) | 2 | Dirección General de Tráfico (DGT), REPUVE — Registro Público Vehicular |
| Purchase history (VIN Values) | 2 | J.D. Power Valuation Services, Urban Science |
| radio (DAB) | 2 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group), mobile.de |
| rear_suspension | 2 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group), Vehicle Databases |
| RedBook Code (RBC) | 2 | Datium Insights, RedBook |
| Reducción eco (REDUCCION_ECO_ITV) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Retail margin | 2 | Cox Automotive Europe, Dealer Auction |
| Retail valuation | 2 | Auto Trader UK (Autotrader Group plc), vAuto |
| revenueWeight | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| safety | 2 | Copart, Inc., Vehicle Databases |
| Sale time | 2 | BCA (British Car Auctions), Copart, Inc. |
| Score factor: Age | 2 | AutoCheck (by Experian), Experian Automotive (AutoCheck) |
| seats | 2 | Auto Trader UK (Autotrader Group plc), mobile.de |
| Serie | 2 | Guazi (瓜子二手车) / Chehaoduo Group, Quattroruote Professional / Infocar (Editoriale Domus) |
| source | 2 | ChromeData (part of J.D. Power / Autodata Solutions Division), MarketCheck (MarketCheck Cars Inc) |
| standard_seating | 2 | ClearVin, Vehicle Databases |
| Standtage (days in stock) | 2 | AutoScout24, Schwacke (Schwacke GmbH / JD Power Autovista) |
| state | 2 | MarketCheck (MarketCheck Cars Inc), Vehicle Databases |
| std_seating | 2 | DataOne Software (DataOne, LLC), MarketCheck (MarketCheck Cars Inc) |
| Stock Number (Stock #) | 2 | CarGurus, IAA (Insurance Auto Auctions) |
| Stock turn (rotación/standtijd de stock) | 2 | Autotelex B.V., INDICATA (Autorola Group) |
| style (vehicle_style name) | 2 | Auto Trader UK (Autotrader Group plc), DataOne Software (DataOne, LLC) |
| styleId (Chrome Style ID) | 2 | ChromeData (part of J.D. Power / Autodata Solutions Division), Edmunds |
| Suspension type | 2 | ClearVin, Historia Pojazdu (gov.pl) / CEPiK |
| Tara (kerb/unladen weight) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), MSI - Sistemas de Inteligencia de Mercado, S.A. |
| taxDueDate | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| Taxes (tipo + valor %) | 2 | GT Motive, Mahindra First Choice Wheels (MFCWL) |
| taxStatus (Taxed/SORN/Untaxed/Not Taxed for on Road Use) | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| Telaio (chassis/VIN) | 2 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia), Quattroruote Professional / Infocar (Editoriale Domus) |
| Tipo de alimentación (mono/bi/flexicombustible) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Tipo de daño (Noa) | 2 | DAT Ibérica (DAT Automóvil Ibérica SLU), autobiz (autobiz Group) |
| Tipo de posesión (V venta / S subasta — COD_POSESION) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Tipo del vehículo base | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| tire_size | 2 | ClearVin, Vehicle Databases |
| Tire tread depth | 2 | ACV Auctions, OPENLANE |
| tire_type | 2 | ClearVin, DataOne Software (DataOne, LLC) |
| title | 2 | AutoGrab, AutoUncle |
| Title number | 2 | AutoCheck (by Experian), NMVTIS / VehicleHistory.gov |
| Torque rpm (from/to) | 2 | AutoGrab, Schwacke (Schwacke GmbH / JD Power Autovista) |
| Transmision | 2 | Eurotax (JD Power / Autovista Group), MSI - Sistemas de Inteligencia de Mercado, S.A. |
| typeApproval | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| Typical Negotiation adjustment (~4-7%) | 2 | CCC Intelligent Solutions, Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Usage type (Personal/Commercial/Fleet/Rental/Taxi/Lease) | 2 | ClearVin, TrueCar |
| Vía anterior (mm) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Vía posterior (mm) | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| Valor de compra (trade) GANVAM-DAT | 2 | DAT Ibérica (DAT Automóvil Ibérica SLU), GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Valor de mercado | 2 | Audatex España (Solera), Sumauto (SUMAUTO MOTOR S.L.) |
| Valor GANVAM-DAT (valor de referencia oficial VO Espana) | 2 | DAT (Deutsche Automobil Treuhand GmbH), DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Value history (retail value back to Jan 2014) | 2 | Kelley Blue Book, Motorway |
| VDP URL | 2 | Black Book (National Auto Research — Hearst), MarketCheck (MarketCheck Cars Inc) |
| vehicle_class | 2 | Experian Automotive (AutoCheck), Vehicle Databases |
| Vehicle description (year/make/model/trim/engine/body) | 2 | J.D. Power Valuation Services, carsales (carsales.com.au) |
| Vehicle history highlights | 2 | ACV Auctions, MAX Digital (ACV MAX) |
| Vehicle Identity Check | 2 | HPI Check (HPI Ltd, a Solera company), cap hpi (CAP + HPI, a Solera company) |
| vehicle_size | 2 | Vehicle Databases, iSeeCars |
| Vehicle SubType | 2 | Historia Pojazdu (gov.pl) / CEPiK, IAA (Insurance Auto Auctions) |
| VehicleId | 2 | GOV.UK MOT History & DVLA Vehicle Enquiry, RedBook |
| Versión del vehículo base | 2 | DGT — Informe de Vehículo (Dirección General de Tráfico), Dirección General de Tráfico (DGT) |
| warranty type | 2 | ClearVin, DataOne Software (DataOne, LLC) |
| wheelbase_type | 2 | AutoGrab, NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| wheelplan | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| Wholesale Average (benchmark, average condition) | 2 | Canadian Black Book, Manheim |
| Wiederbeschaffungswert (replacement value) | 2 | DAT (Deutsche Automobil Treuhand GmbH), Schwacke (Schwacke GmbH / JD Power Autovista) |
| Window Stickers (factory rebate) | 2 | MAX Digital (ACV MAX), vAuto |
| yearOfManufacture | 2 | DVLA (Driver and Vehicle Licensing Agency), GOV.UK MOT History & DVLA Vehicle Enquiry |
| ZIP code | 2 | Urban Science, Vehicle Databases |
| % de cumplimiento del objetivo 2030 (Fit for 55) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| % de cuota de leasing calculable (~85%) | 1 | Eurotax (JD Power / Autovista Group) |
| % diferença / posição vs FIPE | 1 | Webmotors |
| % stock sold through network | 1 | INDICATA (Autorola Group) |
| +50 data points de negocio/financieros/marketing por anunciante | 1 | autobiz (autobiz Group) |
| 0-100km/h加速 | 1 | Autohome (汽车之家) |
| 0-62 / acceleration [PARCIAL] | 1 | JATO Dynamics |
| 0to100_kmph | 1 | AutoGrab |
| 0to60_mph | 1 | AutoGrab |
| 12-month claim probability indicator | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| 15+ Live Market View data points (pricing/demanda/oferta/subasta side-by-side) | 1 | vAuto |
| 16 drivers de VR (calidad percibida, go-to-market, equipamiento, volumen, incentivos, usabilidad, autonomia, carga, eficiencia coste, rendimiento, consumo combustible, consumo energia, VR de marca, posicionamiento, fortalezas/debilidades concepto, feedback mercado) | 1 | Eurotax (JD Power / Autovista Group) |
| 16 key residual-value drivers (Car to Market report) | 1 | Glass's |
| 160+ customizable rule data fields | 1 | ACV Auctions |
| 1st-party data enrich (additional vehicles owned, financial profile) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| [EQUIP·Equipaje] 2 posavasos delanteros y 2 traseros | 1 | km77.com |
| 20+ criterios de precio y atractividad de marketing (MyStock) | 1 | autobiz (autobiz Group) |
| 24 Hour With-a-Look approval window | 1 | CarOffer (a CarGurus company) |
| £30,000 data guarantee | 1 | HPI Check (HPI Ltd, a Solera company) |
| 30+ KPIs de mercado personalizables (Barometer) | 1 | autobiz (autobiz Group) |
| 30+ variables de regresion hedonica / matriz de coeficientes | 1 | Datium Insights |
| 比车300估值 低/高 X万 (delta vs Che300 valuation) | 1 | Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd. |
| 检测报告 300+项 (inspection report) | 1 | Autohome (汽车之家) |
| 360-degree exterior views | 1 | ACV Auctions |
| 360-degree images (Fyusion 3D) | 1 | Manheim |
| 360-degree interior views | 1 | ACV Auctions |
| 360-degree View (with sounds) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| [EQUIP·Multimedia] 4 puertos USB de carga (2x18W y 2x60W) | 1 | km77.com |
| 4 roues motrices | 1 | La Centrale |
| 45-Day Guaranteed Sell offer price | 1 | CarOffer (a CarGurus company) |
| 5YCTO Value Rating (Among the Best / Lower Cost Than Most / Average / Higher Cost Than Most) | 1 | Kelley Blue Book |
| 60+ high-resolution photos | 1 | ACV Auctions |
| 7-day valuation validity (re-confirm mileage) | 1 | Motorway |
| 70+ Ausstattungsmerkmale (equipment features) | 1 | AutoScout24 |
| 80+ provenance data points / 20+ data sources | 1 | cap hpi (CAP + HPI, a Solera company) |
| 90 Days to Sale (consumer journey) | 1 | Urban Science |
| A/B/C柱切割焊接 (pillar cut/weld signal) | 1 | Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd. |
| 傷 A1/A2/A3 (scratch by size) | 1 | USS (ユー・エス・エス) Co., Ltd. |
| aangedreven_as (traccion) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aangedreven_rupsband_indicator | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aanhangwagen_autonoom_geremd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aanhangwagen_middenas_geremd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Aankoop bij een particulier | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Aanschafwaarde (seguro) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| aantal_assen | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantal_cilinders | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantal_eigenaren_prive_zakelijk (OVI, nº propietarios) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantal_gebreken_geconstateerd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantal_passagiers_zitplaatsen_wettelijk | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantal_rolstoelplaatsen | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantal_staanplaatsen | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantal_wielen | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantal_zitplaatsen | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantaldeuren_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantalpassagiers_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantalrolstoelplaatsen_ogr_bgr | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aantalzitplaatsen_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| aanwijzingsnummer | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Abandon flag | 1 | Experian Automotive (AutoCheck) |
| ABI insurers group rating (GB) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Abolladuras de panel (mm) | 1 | Cox Automotive Europe |
| abs_system | 1 | Vehicle Databases |
| ABS warning light | 1 | BCA (British Car Auctions) |
| ABS/EBD/ESP | 1 | Autohome (汽车之家) |
| AC function score | 1 | Mahindra First Choice Wheels (MFCWL) |
| 自适应巡航 ACC | 1 | Autohome (汽车之家) |
| Accelerated Search | 1 | IAA (Insurance Auto Auctions) |
| acceleration | 1 | Vehicle Databases |
| Acceleration / top speed (performance) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| acceleration_to_100 (0-100) | 1 | DataOne Software (DataOne, LLC) |
| acceleration_to_60 (0-60) | 1 | DataOne Software (DataOne, LLC) |
| Accelerazione0100 | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| [EQUIP·Confort] Acceso sin llave | 1 | km77.com |
| Accessori after-market + costi | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Accessori di serie (codici + descrizioni) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| accessories (accesorios) | 1 | Autotelex B.V. |
| Accessories condition (missing items) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Accessories cost | 1 | RedBook |
| Account: financing changes | 1 | Experian Automotive (AutoCheck) |
| Account: payoff indicators | 1 | Experian Automotive (AutoCheck) |
| Account: title loan additions | 1 | Experian Automotive (AutoCheck) |
| AccuTrade: Galves Market Ready Value | 1 | Cars Commerce (Cars.com Inc.) |
| AccuTrade GID (gid) | 1 | Accu-Trade (AccuTrade) |
| AccuTrade: gross_profit_retail | 1 | Cars Commerce (Cars.com Inc.) |
| AccuTrade: gross_profit_wholesale | 1 | Cars Commerce (Cars.com Inc.) |
| AccuTrade: OBD-II diagnostic deduction | 1 | Cars Commerce (Cars.com Inc.) |
| AccuTrade: real_cash_value / guaranteed_offer | 1 | Cars Commerce (Cars.com Inc.) |
| AccuTrade: reconditioning_cost | 1 | Cars Commerce (Cars.com Inc.) |
| ACES codes | 1 | Experian Automotive (AutoCheck) |
| ACES codes & descriptions | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| ACES VCdb identifiers | 1 | DataOne Software (DataOne, LLC) |
| ACES Vehicle ID | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| ACES VehicleID | 1 | DataOne Software (DataOne, LLC) |
| ACH funding | 1 | IAA (Insurance Auto Auctions) |
| 시세 변ación por 지역 (región) | 1 | Encar (엔카닷컴 / Encar.com) |
| acquire_acquisition_management_tracking | 1 | carsales (carsales.com.au) |
| acquire_analytics_dashboard_team_performance | 1 | carsales (carsales.com.au) |
| acquire_find_opportunities_filter_220k_cars | 1 | carsales (carsales.com.au) |
| acquire_livemarket_data_per_listing | 1 | carsales (carsales.com.au) |
| acquire_onthego_remote_appraisal | 1 | carsales (carsales.com.au) |
| acquire_rego_id_lookup | 1 | carsales (carsales.com.au) |
| Acquisition / capture rate | 1 | Accu-Trade (AccuTrade) |
| Acquisition channel recommendation (trade/auction/private-party) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Acquisition Insights: estimated turn time | 1 | CarOffer (a CarGurus company) |
| actie_radius_enkel_elektrisch_wltp (autonomia EV) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| actie_radius_extern_opladen_wltp | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| actieradius | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| actieradius_extern_oplaadbaar | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Active Safety System Note | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| actual_cash_value_acv | 1 | Stat.vin (1VIN STAT) |
| Actual recon cost (after service) | 1 | VINCUE (DealerCue Automotive Corp.) |
| actual vehicle photo (inventory feed) | 1 | DataOne Software (DataOne, LLC) |
| ACV Estimate (precio de venta predicho por ML) | 1 | ACV Auctions |
| ACV Guarantee guaranteed payout (paga diferencia / upside al seller) | 1 | ACV Auctions |
| ad / listing quality | 1 | INDICATA (Autorola Group) |
| ad budget reinvestment % (10-15%) | 1 | Urban Science |
| Ad Frequency | 1 | Urban Science |
| Adaptive Cruise Control (ACC) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Adaptive Driving Beam (ADB) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Adaptive Headlights | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| 智能硬件/ADAS芯片 | 1 | Autohome (汽车之家) |
| ADAS / safety / driver assistance features | 1 | JATO Dynamics |
| ADAS integration/calibracion | 1 | GT Motive |
| ADAS operating min/max distance | 1 | DataOne Software (DataOne, LLC) |
| ADAS operating min/max speed | 1 | DataOne Software (DataOne, LLC) |
| ADAS system (e.g. DiPilot / DiPilot 100) | 1 | CarNewsChina Data (China EV DataTracker) |
| AdBlue need flag | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| AdBlue tank capacity (l) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Add/deducts (option-level value adjustments, auto-applied) | 1 | Canadian Black Book |
| Additional Error Text | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Additional history: Abandoned | 1 | AutoCheck (by Experian) |
| Additional history: Corrected Title | 1 | AutoCheck (by Experian) |
| Additional history: Repossessed | 1 | AutoCheck (by Experian) |
| Additional Parts Information | 1 | GT Motive |
| additional_vehicles | 1 | AutoGrab |
| additionalBuildData.description | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| additionalBuildData.invoice | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| additionalBuildData.label | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| additionalBuildData.value | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| additionele_massa_alternatieve_aandrijving | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| address | 1 | Vehicle Databases |
| Adjustable Headlamps | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Adjustable Headrest | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Adjustable Steering | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Adjusted Comparable Value | 1 | CCC Intelligent Solutions |
| Adjusted MMR (on-demand via API) | 1 | Manheim |
| Adjusted Vehicle Value | 1 | CCC Intelligent Solutions |
| Adjusted vs Base value distinction | 1 | ClearVin |
| adjustedBy: EVBH (Electric Vehicle Battery Health) | 1 | Cox Automotive |
| Adjuster name | 1 | CCC Intelligent Solutions |
| Adjustment % (km/condition) | 1 | RedBook |
| adjustment.override.max_kms | 1 | AutoGrab |
| adjustment.override.min_kms | 1 | AutoGrab |
| adjustment.retail_adjustment | 1 | AutoGrab |
| adjustment.trade_adjustment | 1 | AutoGrab |
| Ads: audiência qualificada (perfil demográfico) | 1 | Webmotors |
| Ads: Conteúdo 360º (branded content) | 1 | Webmotors |
| Ads: CRM Push | 1 | Webmotors |
| Ads: Loja Oficial (showroom oficial) | 1 | Webmotors |
| Ads: Smart Lead (leads cualificados + leads coche nuevo) | 1 | Webmotors |
| adsCategoryIdDescriptions | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| adsCategoryIds | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| adsTypeIdDescriptions | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| adsTypeIds | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| adult_occupant_protection_score | 1 | carVertical |
| Advanced data analytics / customizable reporting | 1 | ACV Auctions |
| Advert descriptions / listing text | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Advert images | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| advertisement status / salesStatus | 1 | Encar (엔카닷컴 / Encar.com) |
| advertisementCategory | 1 | Autotelex B.V. |
| advertisementTitle | 1 | Autotelex B.V. |
| advertisementUrl | 1 | Autotelex B.V. |
| advertiserVehicleHighlight (1-3) | 1 | Auto Trader UK (Autotrader Group plc) |
| Advertising history (historial publicitario) | 1 | Autotelex B.V. |
| adverts.soldPrice.amountGBP | 1 | Auto Trader UK (Autotrader Group plc) |
| aerodynamic_drag | 1 | DataOne Software (DataOne, LLC) |
| aerodynamische_voorziening | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| AFC: floorplan revolving credit line | 1 | OPENLANE |
| AFC: Pay with AFC (floorea precio + auction fees + transporte) | 1 | OPENLANE |
| AFC: plazo hasta 90 dias | 1 | OPENLANE |
| AFC: recomendaciones de vehiculo por historial | 1 | OPENLANE |
| Afschrijvingspercentage BPM (derivado: (nieuwprijs − handelsinkoopwaarde)/(consumentenprijs/100)) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| afstand_hart_koppeling_tot_achterzijde | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| afstand_tot_volgende_as | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| afstand_voorzijde_tot_hart_koppeling | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| After-factory equipment adjustment | 1 | CCC Intelligent Solutions |
| after-sales potential per territory | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| aftermarket by channel (Garages, VM Networks, Autocentres, Tire Specialists, Parts Accessories, Online Sales, Hypermarkets, Petrol Stations, Fast Fits, Crash Repair/Bodyshops) | 1 | GlobalData Automotive |
| aftermarket by product family (Wear & Tear, Service, Tires, Consumables, Crash Repair, Mechanical, Accessories) | 1 | GlobalData Automotive |
| aftermarket CAGR | 1 | GlobalData Automotive |
| aftermarket part value (market size) | 1 | GlobalData Automotive |
| aftermarket part volume | 1 | GlobalData Automotive |
| Aftermarket tint | 1 | Accu-Trade (AccuTrade) |
| Aftermarket upgrades itemizados con valor en dolares | 1 | MAX Digital (ACV MAX) |
| AfterSales: customer marketing analytics | 1 | cap hpi (CAP + HPI, a Solera company) |
| AfterSales: retention / loyalty metrics | 1 | cap hpi (CAP + HPI, a Solera company) |
| AfterSales: service customer targeting | 1 | cap hpi (CAP + HPI, a Solera company) |
| AFV share (%) | 1 | Dealer Auction |
| afwijkende_maximum_snelheid | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Age adjustment | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Agreed Value (insurance) | 1 | RedBook |
| agregación de expedientes | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| ahorro energético (kWh) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| ai_buyer_signals_preferences_next_steps | 1 | carsales (carsales.com.au) |
| ai_call_transcription_summary_gemini | 1 | carsales (carsales.com.au) |
| ai_contextual_buyer_summary | 1 | carsales (carsales.com.au) |
| ai_intent_detection_hot_leads | 1 | carsales (carsales.com.au) |
| ai_lead_prioritization_likelihood_to_convert | 1 | carsales (carsales.com.au) |
| ai_offer_creation_support_data_backed | 1 | carsales (carsales.com.au) |
| AI SEO-optimized vehicle description (incluye OEM build data) | 1 | MAX Digital (ACV MAX) |
| AI vehicle description (AI Description Writer/Builder) | 1 | VINCUE (DealerCue Automotive Corp.) |
| AI vehicle descriptions (SEO-optimized) | 1 | ACV Auctions |
| AI-generated listing descriptions (Smart Descriptions) | 1 | JATO Dynamics |
| air_bag_deployment | 1 | Vehicle Databases |
| Air Conditioner | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| air_conditioning_type | 1 | AutoGrab |
| air.performance_benchmarking (vs nacional/estatal) | 1 | AutoGrab |
| air.weighted_retained_value | 1 | AutoGrab |
| airbag | 1 | mobile.de |
| Airbag availability | 1 | ClearVin |
| [EQUIP·Seguridad] Airbag central delantero | 1 | km77.com |
| Airbag Deployed | 1 | AutoCheck (by Experian) |
| Airbag deployment status | 1 | IAA (Insurance Auto Auctions) |
| [EQUIP·Seguridad] Airbag frontal acompañante | 1 | km77.com |
| [EQUIP·Seguridad] Airbag frontal conductor | 1 | km77.com |
| Airbag warning light | 1 | BCA (British Car Auctions) |
| [EQUIP·Seguridad] Airbags de cabeza delanteros y traseros | 1 | km77.com |
| [EQUIP·Seguridad] Airbags laterales delanteros | 1 | km77.com |
| [EQUIP·Seguridad] Airbags laterales traseros | 1 | km77.com |
| Airbags por posición (rodilla/lateral/cabeza) | 1 | Audatex España (Solera) |
| [EQUIP·Confort] Aire acondicionado | 1 | km77.com |
| aire acondicionado SI/NO (airconditioningShow) | 1 | Fasecolda — Guía de Valores |
| [EQUIP·Seguridad] Aislamiento térmico y doble acristalamiento lateral | 1 | km77.com |
| Aisle/Stall | 1 | IAA (Insurance Auto Auctions) |
| ajuste de RV vehiculo-a-vehiculo (override manual) | 1 | Datium Insights |
| ajuste de valor por equipamiento (depreciación de opcionales) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Ajuste por antigüedad/edad | 1 | Audatex España (Solera) |
| Ajuste por antiguedad/edad | 1 | Eurotax (JD Power / Autovista Group) |
| Ajuste por blindagem (vehículo blindado) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Ajuste por condición técnica | 1 | Audatex España (Solera) |
| Ajuste por cor | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Ajuste por opcionais / equipamento (airbag, direção hidráulica, etc.) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Ajuste por quilometragem (km rodados) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| [EQUIP·Varios] Alarma antirrobo | 1 | km77.com |
| Alerta de discrepancia de recon (declarado vs IA) | 1 | autobiz (autobiz Group) |
| [EQUIP·Seguridad] Alerta de fatiga del conductor | 1 | km77.com |
| Alertas de precio de anuncios similares (priceAlertsSimilarListings) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Alerte prix | 1 | La Centrale |
| Alimentazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| AllElectric | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| AllElectric_City | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| AllElectric_Comb | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Allestimento | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Allestimento esatto (versione/trim) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Allestimento_offline | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Allestimento_online | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| alloy wheel photos (head-on, full alloy) | 1 | Motorway |
| Alloy Wheels | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| alloyWheels | 1 | mobile.de |
| Altas | 1 | REPUVE — Registro Público Vehicular |
| altBodyType | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Alternative derivative lookup (cap ID/code/type) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Alternative fuels | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| AltezzaMetri | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| altModelName | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| altStyleName | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Altura (mm) | 1 | km77.com |
| [MED·Maletero] Altura del borde de carga (cm) | 1 | km77.com |
| [MED·Habitabilidad 1ª fila] Altura libre (cm) | 1 | km77.com |
| [MED·Habitabilidad 1ª fila] Altura libre con techo solar (cm) | 1 | km77.com |
| ambit.radius (km) | 1 | mobile.de |
| ambit.zipcode | 1 | mobile.de |
| American_Made_Index_score (100-point) | 1 | Cars Commerce (Cars.com Inc.) |
| AMI factor: parts_sourcing (AALA) | 1 | Cars Commerce (Cars.com Inc.) |
| AMI factor: US_factory_employment | 1 | Cars Commerce (Cars.com Inc.) |
| Amount above/below market ($) | 1 | Edmunds |
| Amperaje del alternador | 1 | Audatex España (Solera) |
| AnalisiRotazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ANCAP Safety Rating | 1 | RedBook |
| Anchura (mm) | 1 | km77.com |
| [MED·Habitabilidad 1ª fila] Anchura a los hombros (cm) | 1 | km77.com |
| Ancienneté du pro (Agent depuis) | 1 | La Centrale |
| Android Auto | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Anfragen / Leads (inquiries) | 1 | AutoScout24 |
| Angebotspreis (offer price) | 1 | AutoScout24 |
| angle_of_approach | 1 | DataOne Software (DataOne, LLC) |
| angle_of_departure | 1 | DataOne Software (DataOne, LLC) |
| Anio de produccion (productionDate) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Année (millésime) | 1 | La Centrale |
| AnnoImmatricolazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| AnnoInfocar | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| AnnoMeseImmatricolazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| AnnoPrevisione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Announcements / disclosures | 1 | ACV Auctions |
| Announcements/remarks | 1 | Manheim |
| Antenna | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| anti_lock_brakes | 1 | Vehicle Databases |
| Anti-lock Brake System (ABS) | 1 | ClearVin |
| Anti-lock Braking System (ABS) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| [EQUIP·Seguridad] Antibloqueo de frenos (ABS) | 1 | km77.com |
| Antigüedad / edad del vehículo (parque) | 1 | Dirección General de Tráfico (DGT) |
| Antiguedad/año del vehiculo (parque) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Antilock Braking System (ABS) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Anuncio: Com garantia (flag) | 1 | Standvirtual |
| Anuncio: Combustível | 1 | Standvirtual |
| Anuncio: Cor | 1 | Standvirtual |
| [VO] Anuncio de coche usado (coches77 / KM77 VO) | 1 | km77.com |
| Anuncio: Estado (Usado/Novo) | 1 | Standvirtual |
| [A] Anuncio: IUC | 1 | Standvirtual |
| [A] Anuncio: Livro de revisões | 1 | Standvirtual |
| [A] Anuncio: Lugares | 1 | Standvirtual |
| Anuncio: Nº de portas | 1 | Standvirtual |
| [A] Anuncio: Nº de proprietários | 1 | Standvirtual |
| [A] Anuncio: Não fumador | 1 | Standvirtual |
| [A] Anuncio: Norma de emissões | 1 | Standvirtual |
| Anuncio: Potência (cv) | 1 | Standvirtual |
| Anuncio: Preço (EUR) | 1 | Standvirtual |
| Anuncio: Quilómetros (km) | 1 | Standvirtual |
| [A] Anuncio: Registo de serviço | 1 | Standvirtual |
| Anuncio: Tipo de Caixa (transmisión) | 1 | Standvirtual |
| Anuncio: Tipo de cor | 1 | Standvirtual |
| [A] Anuncio: Tração | 1 | Standvirtual |
| Anuncio: Valor Fixo (flag precio no negociable) | 1 | Standvirtual |
| Anuncio: Versão | 1 | Standvirtual |
| Anzahl der Vorbesitzer (numero de propietarios anteriores) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Anzahl konkurrierender Fahrzeuge (# competing vehicles) | 1 | AutoScout24 |
| AnzianitaAllaEdizione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| API adjustedForecastPricing.wholesale | 1 | Manheim |
| API bestMatch flag | 1 | Manheim |
| API: catálogo | 1 | Webmotors |
| API: consulta de leads | 1 | Webmotors |
| API currency (USD) | 1 | Manheim |
| API: estoque / itens | 1 | Webmotors |
| API: estoque site | 1 | Webmotors |
| API forecast date (up to 106 weeks ahead) | 1 | Manheim |
| API forecastDate/edition (Mondays) | 1 | Manheim |
| API forecastedAverageGrade | 1 | Manheim |
| API forecastedPricing (unadjusted) | 1 | Manheim |
| API: inclusão de leads | 1 | Webmotors |
| API: interações | 1 | Webmotors |
| API: listing create/update/publish/remove (write-only) | 1 | AutoScout24 |
| API sampleSize | 1 | Manheim |
| API token (generacion para mostrar precios OBV) | 1 | Orange Book Value (OBV) |
| API zipCode | 1 | Manheim |
| aportación al saldo de la balanza comercial española | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| aportación del sector al Estado (€) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| [EQUIP·Confort] Apoyabrazos central delantero | 1 | km77.com |
| [EQUIP·Confort] Apoyabrazos central trasero | 1 | km77.com |
| Apple CarPlay | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| [EQUIP·Multimedia] Apple CarPlay / Android Auto | 1 | km77.com |
| application-type | 1 | L'argus (Cote Argus®) |
| Apport (€) | 1 | La Centrale |
| appraisal close ratio | 1 | CarOffer (a CarGurus company) |
| Appraisal report (PDF/email) | 1 | BCA (British Car Auctions) |
| Appraisal Snapshot (saved appraisal) | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| appraisalDate (fecha de tasación) | 1 | Autotelex B.V. |
| Appraiser name | 1 | CCC Intelligent Solutions |
| Appraiser/Adjuster name | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Approval time tracking | 1 | vAuto |
| Approximate condition (excellent/good/fair/poor) | 1 | Accu-Trade (AccuTrade) |
| apr_estimate | 1 | TrueCar |
| apte_a_circuler | 1 | HistoVec |
| Arañazos (mm) | 1 | Cox Automotive Europe |
| Arañazos/grietas de paragolpes (mm) | 1 | Cox Automotive Europe |
| Arbeitswerte AW (unidades de trabajo / baremos MO) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Arbitration eligibility (defectos elegibles) | 1 | ACV Auctions |
| arbitration rate / status | 1 | CarOffer (a CarGurus company) |
| Army/government deduction (צבא) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| [EQUIP·Confort] Arranque sin llave | 1 | km77.com |
| Articles | 1 | Kelley Blue Book |
| articulated / semi-trailer (Sattelzug) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| As Described Guarantee: elegibilidad (93% del inventario) | 1 | OPENLANE |
| As Described Guarantee: ventana 5 dias compra / 7 dias entrega (con transporte OPENLANE) | 1 | OPENLANE |
| as_nummer | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| AS-IS flag (5-6% del inventario) | 1 | OPENLANE |
| Asegurado | 1 | Audatex España (Solera) |
| [EQUIP·Confort] Asiento de conductor con memoria | 1 | km77.com |
| [EQUIP·Confort] Asiento del conductor con ajuste lumbar | 1 | km77.com |
| [EQUIP·Equipaje] Asiento trasero abatible 40/60 | 1 | km77.com |
| [EQUIP·Confort] Asientos delanteros con ajuste de altura | 1 | km77.com |
| [EQUIP·Confort] Asientos delanteros con ajuste eléctrico (8 vías conductor/6 acompañante) | 1 | km77.com |
| [EQUIP·Confort] Asientos delanteros con calefacción | 1 | km77.com |
| [EQUIP·Confort] Asientos delanteros deportivos | 1 | km77.com |
| [EQUIP·Confort] Asientos delanteros ventilados | 1 | km77.com |
| Asignación automática a canales de venta (Pilot) | 1 | autobiz (autobiz Group) |
| [EQUIP·Seguridad] Asistente de frenada | 1 | km77.com |
| [EQUIP·Seguridad] Asistente de luz de cruce/carretera | 1 | km77.com |
| [EQUIP·Seguridad] Asistente de parada de emergencia | 1 | km77.com |
| [EQUIP·Multimedia] Asistente de voz | 1 | km77.com |
| Asistente IA generativa (WhatsApp: precificação + crédito + recomendações) | 1 | Webmotors |
| [EQUIP·Seguridad] Asistente para atascos | 1 | km77.com |
| Asking-vs-selling spread (%) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| asking/listed price | 1 | CarGurus |
| Asset register valuation / financial exposure | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Assignments Received | 1 | IAA (Insurance Auto Auctions) |
| Assisted driving chip (e.g. NVIDIA DRIVE Orin N) | 1 | CarNewsChina Data (China EV DataTracker) |
| Assurance (estimation partenaire) | 1 | La Centrale |
| At-a-Glance: Additional History status | 1 | AutoCheck (by Experian) |
| At-a-Glance: Certified Pre-Owned status | 1 | AutoCheck (by Experian) |
| At-a-glance profitability report (con vs sin herramienta) | 1 | MAX Digital (ACV MAX) |
| At-a-Glance: Service/Repair status | 1 | AutoCheck (by Experian) |
| atglance_airbag_deployment_count | 1 | Stat.vin (1VIN STAT) |
| atglance_auction_sales_history_count | 1 | Stat.vin (1VIN STAT) |
| atglance_basic_warranty_count | 1 | Stat.vin (1VIN STAT) |
| atglance_photo_count | 1 | Stat.vin (1VIN STAT) |
| atglance_sales_history_count | 1 | Stat.vin (1VIN STAT) |
| Atributo: richtprijzen = precios medios incl. BTW & BPM | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Atributos del vehiculo (make/model/derivado/edad/km/fuel) | 1 | Cox Automotive Europe |
| Auction announced_at_auction date | 1 | ClearVin |
| Auction Announcements (structural damage) | 1 | Experian Automotive (AutoCheck) |
| Auction condition (Run & Drive / WON'T START) | 1 | ClearVin |
| auction_date | 1 | Vehicle Databases |
| Auction images[] | 1 | ClearVin |
| Auction lot / auctionId | 1 | ClearVin |
| auction_lot_number | 1 | Stat.vin (1VIN STAT) |
| Auction Run Lists (ACV / Manheim / ADESA) | 1 | ACV Auctions |
| auction_sale_date | 1 | Stat.vin (1VIN STAT) |
| Auction sales forecast / prediccion (total por evento) | 1 | Hagerty |
| auction_sold_status | 1 | Stat.vin (1VIN STAT) |
| Auction title state | 1 | ClearVin |
| Auction transactions ACV + other auctions (input) | 1 | ACV Auctions |
| Auction type (Open/Closed) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Auction Value - Average | 1 | J.D. Power Valuation Services |
| Auction Value - High | 1 | J.D. Power Valuation Services |
| Auction Value - Low | 1 | J.D. Power Valuation Services |
| Auction vendor (Copart/IAA) | 1 | ClearVin |
| Auction/sale name | 1 | Autorola |
| AuctionACCESS membership ($103/individual/year) | 1 | Manheim |
| Auctions summary tab | 1 | Manheim |
| Audascan message (mensaje por aseguradora) | 1 | Autotelex B.V. |
| AudaVIN flag (Yes/No) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| audit trail (registro de cambios y busquedas por usuario) | 1 | Datium Insights |
| Aufrufe (views) | 1 | AutoScout24 |
| Ausstattungsanalyse (fehlende Ausstattung + impacto en precio) | 1 | AutoScout24 |
| Ausstattungsvergleich eigen vs Konkurrenz (equipment comparison) | 1 | AutoScout24 |
| autenticacao (código de autenticação verificável da consulta) | 1 | FIPE (Tabela Fipe Veículos) |
| Auto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| auto-bid increment (GBP 50) | 1 | Motorway |
| auto-panorama exterior 360 | 1 | mobile.de |
| auto-panorama interior 360 | 1 | mobile.de |
| Auto-Reverse System for Windows and Sunroofs | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| AutoCalc Adjusted Price | 1 | RedBook |
| autocheck_report | 1 | Stat.vin (1VIN STAT) |
| AutoCheck Snapshot (vehicle history, Experian) | 1 | Manheim |
| AutoCheck vehicle history snapshot (integrado, gratis en US CR) | 1 | OPENLANE |
| AutoGrade label: 1 Rough | 1 | Manheim |
| AutoGrade label: 2 Below Average | 1 | Manheim |
| AutoGrade label: 3 Average | 1 | Manheim |
| AutoGrade label: 4 Clean | 1 | Manheim |
| AutoGrade score (1.0-5.0) | 1 | Cox Automotive |
| AutoGrade score 0-5 (estándar Manheim/NAAA) | 1 | Copart, Inc. |
| AutoGuru: comparação pátio vs lojas rivais próximas | 1 | Webmotors |
| AutoGuru: idade média do estoque | 1 | Webmotors |
| AutoGuru: margem ideal de compra/venda | 1 | Webmotors |
| AutoGuru: melhor sortimento do pátio | 1 | Webmotors |
| AutoGuru: melhor tempo de pátio | 1 | Webmotors |
| AutoGuru: parâmetros de preço competitivo | 1 | Webmotors |
| AutoGuru: preço vs concorrência (above/below) | 1 | Webmotors |
| AutoGuru: quantidades em estoque | 1 | Webmotors |
| AutoGuru: quilometragem do estoque | 1 | Webmotors |
| AutoGuru: tempo médio de venda | 1 | Webmotors |
| Autoinsights: atividade por município | 1 | Webmotors |
| Autoinsights: carros mais procurados (ranking) | 1 | Webmotors |
| Autoinsights: estudos temáticos (intenção de compra, elétricos, automáticos, SUV, manutenção) | 1 | Webmotors |
| Autoinsights: itens opcionais mais procurados | 1 | Webmotors |
| Autoinsights: motos mais procuradas (ranking) | 1 | Webmotors |
| Autoinsights: perfil do usuário (gênero / idade) | 1 | Webmotors |
| Autoinsights: preferência de cor | 1 | Webmotors |
| Autoinsights: recortes temporais (mensal / trimestral / semestral / anual) | 1 | Webmotors |
| Autoinsights: termômetros de busca | 1 | Webmotors |
| AutoIQ: Ad-to-short-form content | 1 | Standvirtual |
| AutoIQ: AI-generated listing descriptions (voz del dealer) | 1 | Standvirtual |
| AutoIQ: Centralized lead dashboard | 1 | Standvirtual |
| AutoIQ: Image management / visual enhancement | 1 | Standvirtual |
| AutoIQ: Pricing recommendations | 1 | Standvirtual |
| AutoIQ: Video-to-listing | 1 | Standvirtual |
| AutoMatch exact-equipment competitive match | 1 | vAuto |
| Automated appraisal in ACV MAX (VIPER) | 1 | ACV Auctions |
| Automated customer offer (ClearCar) | 1 | ACV Auctions |
| automatische Neubewertung (auto revaluation) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Automotive ID | 1 | Autovista Group |
| Automotive ID / Autovista ID | 1 | Eurotax (JD Power / Autovista Group) |
| autoniq: AuctionNet data | 1 | OPENLANE |
| autoniq: AutoCheck report | 1 | OPENLANE |
| autoniq: autoniq Market Report | 1 | OPENLANE |
| autoniq: Black Book value | 1 | OPENLANE |
| autoniq: CARFAX report | 1 | OPENLANE |
| autoniq: CarValue (ADESA) value | 1 | OPENLANE |
| autoniq: Galves value | 1 | OPENLANE |
| autoniq: Kelley Blue Book value | 1 | OPENLANE |
| autoniq: listas / wishlist / notas / fotos | 1 | OPENLANE |
| autoniq: MMR (Manheim Market Report) value | 1 | OPENLANE |
| autoniq: PMR (Pipeline Market Report, 175+ subastas EDGE) | 1 | OPENLANE |
| autoniq: Retail Index | 1 | OPENLANE |
| autoniq Wholesale Index: average wholesale price | 1 | OPENLANE |
| autoniq Wholesale Index: radio 50-3000 millas | 1 | OPENLANE |
| autoniq Wholesale Index: ventana 90 dias / refresco diario (ADESA + DealerBlock data) | 1 | OPENLANE |
| Autonomía del vehículo eléctrico (km) | 1 | Dirección General de Tráfico (DGT) |
| Autonomía eléctrica (km) | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Autonomía eléctrica WLTP (km) | 1 | km77.com |
| AutoPay / estado de repago | 1 | Cox Automotive Europe |
| autotelexId (ATX id) | 1 | Autotelex B.V. |
| Autoviza: analyse des ventes du véhicule | 1 | La Centrale |
| Autoviza: dates + kilométrage des contrôles techniques | 1 | La Centrale |
| Autoviza: données carte grise certifiées | 1 | La Centrale |
| Autoviza: durée de détention par propriétaire | 1 | La Centrale |
| Autoviza: existence vérifiée | 1 | La Centrale |
| Autoviza: historique du kilométrage | 1 | La Centrale |
| Autoviza: nombre de propriétaires précédents | 1 | La Centrale |
| Autoviza: numéro de série (VIN) certifié | 1 | La Centrale |
| Autoviza: opérations/entretien effectués | 1 | La Centrale |
| Autoviza: sinistres / réparations à dire d'expert (points d'attention) | 1 | La Centrale |
| Autoviza: usage privé uniquement | 1 | La Centrale |
| Autoviza: usages antérieurs détectés (taxi/VTC/auto-école) | 1 | La Centrale |
| AutoWriter (descripcion IA especifica del vehiculo) | 1 | vAuto |
| Aux belt / pulley noise | 1 | BCA (British Car Auctions) |
| Auxiliary Operations | 1 | GT Motive |
| Availability Index (inventory/supply levels) | 1 | CarGurus |
| availability_status | 1 | MarketCheck (MarketCheck Cars Inc) |
| availabilityVerified | 1 | AutoUncle |
| availableFrom | 1 | Autotelex B.V. |
| availableUntil | 1 | Autotelex B.V. |
| Avec livraison (filtre) | 1 | La Centrale |
| Average age (months) | 1 | Cox Automotive Europe |
| Average comparable price ($) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Average EV transaction price | 1 | Cox Automotive |
| Average LCV/van selling price | 1 | BCA (British Car Auctions) |
| average_paid_price | 1 | TrueCar |
| Average Price (Avg) | 1 | CLASSIC.COM |
| Average retail sold price (por vehiculo) | 1 | Cox Automotive Europe |
| Average Sale (Moving Average) | 1 | CLASSIC.COM |
| Average sale value | 1 | ClearVin |
| Average Selling Price (ASP) | 1 | IAA (Insurance Auto Auctions) |
| Average time to sell | 1 | RedBook |
| Average used car selling price (£) | 1 | BCA (British Car Auctions) |
| average wheel track (avg-rozstaw-kol) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| averageEVBH | 1 | Cox Automotive |
| averageGrade | 1 | Cox Automotive |
| AVILOO FLASH test report + score | 1 | BCA (British Car Auctions) |
| [EQUIP·Seguridad] Aviso de cinturón en todas las plazas | 1 | km77.com |
| [EQUIP·Seguridad] Aviso de colisión frontal y frenado autónomo de emergencia (AEB) | 1 | km77.com |
| [EQUIP·Seguridad] Aviso de colisión trasera | 1 | km77.com |
| award citation | 1 | DataOne Software (DataOne, LLC) |
| award criteria (engine/transmission-specific) | 1 | DataOne Software (DataOne, LLC) |
| award name | 1 | DataOne Software (DataOne, LLC) |
| award snippet | 1 | DataOne Software (DataOne, LLC) |
| award source/awarding party | 1 | DataOne Software (DataOne, LLC) |
| award type | 1 | DataOne Software (DataOne, LLC) |
| award website | 1 | DataOne Software (DataOne, LLC) |
| Awards (window sticker / merchandising) | 1 | MAX Digital (ACV MAX) |
| Axle Configuration | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| axle_ratio | 1 | Vehicle Databases |
| axle spacing (rozstaw osi) [Moj Pojazd] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| [EQUIP·Seguridad] Ayuda de aparcamiento delantero | 1 | km77.com |
| [EQUIP·Seguridad] Ayuda de aparcamiento trasero | 1 | km77.com |
| [EQUIP·Seguridad] Ayuda de arranque en cuesta | 1 | km77.com |
| AZT paint data | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| B2B: Lead (cobro por lead) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| B2B: price per report / ahorro | 1 | autoDNA |
| B2B: Virtual online showroom | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Back-end gross (store historical, by MMT) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Backup Camera | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Bad/branded VHR (carfax_has_bad_vhr) | 1 | Accu-Trade (AccuTrade) |
| Badge condicional de precio (conditionalPriceBadge) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Badge: CPO Badge (manufacturer-certified pre-owned) | 1 | CARFAX Canada |
| badge venta urgente (车主急售) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| BadgeDetail / 세부등급 (sub-trim) (+ EnglishName) | 1 | Encar (엔카닷컴 / Encar.com) |
| Baja definitiva — motivo (desguace/agotamiento/antigüedad/renovación/exportación/oficio abandono/oficio seguridad/tratamiento residual) | 1 | Dirección General de Tráfico (DGT) |
| Baja telemática ('En desguace') | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Baja telemática / En desguace (BAJA_TELEMATICA) | 1 | Dirección General de Tráfico (DGT) |
| Baja temporal (IND_BAJA_TEMP) | 1 | Dirección General de Tráfico (DGT) |
| Bajas | 1 | REPUVE — Registro Público Vehicular |
| Bajas de propiedad (deregistrations) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| balloon note payment | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| bank_fees | 1 | Stat.vin (1VIN STAT) |
| Barómetro: precio medio del seminuevo (€) + variación (%) | 1 | coches.net |
| Barómetro: precio medio por Comunidad Autónoma (€) + ranking | 1 | coches.net |
| Barómetro: precio medio por franja de antigüedad (€ + %) | 1 | coches.net |
| Barómetro: récord histórico de precio (€ + fecha) | 1 | coches.net |
| Barómetro: variación del precio por CCAA (%) | 1 | coches.net |
| Barómetro: variación interanual del precio medio (%) | 1 | coches.net |
| Barómetro: variación mensual del precio medio (%) | 1 | coches.net |
| Baremo de pintura (CESVIMAP/Centro Zaragoza/fabricante/manual) | 1 | Audatex España (Solera) |
| baremo de pintura EUROLACK (DAT-Eurolack) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Barra estabilizadora delantera | 1 | km77.com |
| Barra estabilizadora trasera | 1 | km77.com |
| Base Imponible | 1 | Audatex España (Solera) |
| Base MMR (precio mayorista medio de transacciones recientes, excl. outliers) | 1 | Cox Automotive |
| Base MMR value (wholesale average) | 1 | Manheim |
| Base Price ($) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| base_towing_capacity | 1 | DataOne Software (DataOne, LLC) |
| Base valuation (₹) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Base value (por cada tipo de valor) | 1 | J.D. Power Valuation Services |
| Base Vehicle Value | 1 | CCC Intelligent Solutions |
| baseInvoice | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| basePrice | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| basic_equipment_info | 1 | carVertical |
| Batalla (mm) | 1 | km77.com |
| Batería: Capacidad útil (kWh) | 1 | km77.com |
| Batería: Capacidad total (kWh) | 1 | km77.com |
| Batería: Situación | 1 | km77.com |
| Batería: Tipo | 1 | km77.com |
| Baureihe (serie del modelo) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Beauty images | 1 | BCA (British Car Auctions) |
| bed_code | 1 | DataOne Software (DataOne, LLC) |
| Bed Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| bedrijf_adres (straat/huisnummer/postcode/plaats) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Behavior Prediction Score (0-100) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Behavioural risk indicators | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Beleihungswert [NO-VERIFICADO] | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| benchmark comparison (equitable, local-preference adjusted) | 1 | Urban Science |
| benchmark de precision vs competidores | 1 | Datium Insights |
| Benchmark VR vs competidores | 1 | Eurotax (JD Power / Autovista Group) |
| Benchmarking coste medio propio vs mercado por tipo de vehículo | 1 | Audatex España (Solera) |
| benchmarks (10+ countries) | 1 | AutoUncle |
| benefitStatement.definition | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| benefitStatement.statement | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| benefitStatement.title | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| beschaedigte Teile (piezas danadas detectadas por IA) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| beschrijving_van_het_herstel | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Best Buy Award (segment + overall) | 1 | Kelley Blue Book |
| Best Resale Value Award (5-yr % retained) | 1 | Kelley Blue Book |
| Best sale route / channel recommendation | 1 | Autorola |
| Best time to contact (0-3) | 1 | Accu-Trade (AccuTrade) |
| Bestand / Angebotsvolumen (stock/supply volume + vs pre-Corona) | 1 | AutoScout24 |
| bestMatch (mejor coincidencia de configuración) | 1 | Cox Automotive |
| BEV-Erfahrung / BEV-Kaufabsicht (experiencia/intencion de compra VE) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| BEV/PHEV/ICE mix % by market | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Bewertungs-Details (adjusted value) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| bid / bidding history (puja/historial de pujas) | 1 | Autotelex B.V. |
| Bid increments (£50 / £100 / £200) | 1 | Dealer Auction |
| BID4U (proxy bid) | 1 | Copart, Inc. |
| Bidder counts (market activity) | 1 | IAA (Insurance Auto Auctions) |
| BidFast purchase offer amount (30-day validity) | 1 | IAA (Insurance Auto Auctions) |
| Bids per vehicle / total bids | 1 | Dealer Auction |
| bijzonderheid_code | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| bijzonderheid_code_omschrijving | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| bijzonderheid_eenheid | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| bijzonderheid_variabele_tekst | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Bilder (images) | 1 | AutoScout24 |
| Bill reimbursement recommendation (casualty) | 1 | CCC Intelligent Solutions |
| Billboards (branding/ofertas del dealer) | 1 | vAuto |
| Black Book real-time price (US, embebido en VDP) | 1 | OPENLANE |
| Black Book Vehicle ID | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Black Book Wholesale Average | 1 | Stockwave (vAuto · Cox Automotive) |
| Blacklist / RC status | 1 | Mahindra First Choice Wheels (MFCWL) |
| Blend procedures | 1 | CCC Intelligent Solutions |
| Blended incentive spend | 1 | vAuto |
| Blind Spot Intervention (BSI) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Blind Spot Warning (BSW) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| block_type | 1 | DataOne Software (DataOne, LLC) |
| Bloqueos / restricciones | 1 | REPUVE — Registro Público Vehicular |
| Bluetooth | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Bluetooth Connectivity | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Blur detection / photo quality validation | 1 | CCC Intelligent Solutions |
| Boîte de vitesse | 1 | La Centrale |
| Body / structure data | 1 | Autovista Group |
| Body Class | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Body condition | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| body_config | 1 | AutoGrab |
| body_config_type | 1 | AutoGrab |
| Body repair defects | 1 | Manheim |
| bodyName / 차종 (carrocería) | 1 | Encar (엔카닷컴 / Encar.com) |
| Bodywork (carroceria) | 1 | GT Motive |
| bolt_pattern | 1 | Vehicle Databases |
| Booking Assistant eyeCatcher highlight | 1 | mobile.de |
| Booking Assistant topOfPage placement | 1 | mobile.de |
| Booking/scheduling slot (inspection/maintenance) | 1 | Autorola |
| Bookmark / save count | 1 | CLASSIC.COM |
| Books de valor (integrados) | 1 | MAX Digital (ACV MAX) |
| boot / luggage capacity [PARCIAL] | 1 | JATO Dynamics |
| boot interior photo (empty) | 1 | Motorway |
| Boot Opening | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Boot Space | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| boot.capacity (volume coffre) | 1 | L'argus (Cote Argus®) |
| boot.maximum-capacity | 1 | L'argus (Cote Argus®) |
| boot.minimum-capacity | 1 | L'argus (Cote Argus®) |
| boot.third-row-capacity | 1 | L'argus (Cote Argus®) |
| Borderline total-loss flag | 1 | Copart, Inc. |
| bounds.retail.lower | 1 | AutoGrab |
| bounds.retail.upper | 1 | AutoGrab |
| bounds.trade.lower | 1 | AutoGrab |
| bounds.trade.upper | 1 | AutoGrab |
| Bouwjaar (entrada manual) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| boxStyle | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| BPM (impuesto matriculación) | 1 | Autotelex B.V. |
| BPM según informe de tasación (tegenbewijsregeling) | 1 | Autotelex B.V. |
| BPM según koerslijst (lista de cotización) | 1 | Autotelex B.V. |
| BPM-indicatie (estimación previa) | 1 | Autotelex B.V. |
| Brake energy recovery | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| brake_fluid | 1 | Vehicle Databases |
| Brake fluid level | 1 | BCA (British Car Auctions) |
| Brake lights | 1 | BCA (British Car Auctions) |
| Brake pad replacement timing & cost | 1 | HPI Check (HPI Ltd, a Solera company) |
| Brake pedal pressure / servo assistance | 1 | BCA (British Car Auctions) |
| Brake System Description | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Brake System Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Brake wear indicator light | 1 | BCA (British Car Auctions) |
| brakedTowingCapacity (capacidad arrastre con freno) | 1 | Autotelex B.V. |
| Brakes condition | 1 | OPENLANE |
| Brakes score | 1 | Mahindra First Choice Wheels (MFCWL) |
| Brakes, wheels & tyres [128] | 1 | BCA (British Car Auctions) |
| braking_distance | 1 | DataOne Software (DataOne, LLC) |
| Branch | 1 | IAA (Insurance Auto Auctions) |
| branded_title | 1 | Vehicle Databases |
| Branded Title flag/value | 1 | CCC Intelligent Solutions |
| Branding/title: Inactive designation | 1 | CARFAX Canada |
| Branding/title: Lemon / CAMVAP designation | 1 | CARFAX Canada |
| Branding/title: Rebuilt title | 1 | CARFAX Canada |
| Brandstof | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| brandstof_omschrijving (tipo combustible) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| brandstof_verbruik_gecombineerd_wltp | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| brandstof_verbruik_gewogen_gecombineerd_wltp | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| brandstofverbruik_gecombineerd_nedc | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| brandstofverbruik_gewogen_gecombineerd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| breakover_angle | 1 | DataOne Software (DataOne, LLC) |
| breedte | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| breedte_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Broadcasting de anuncios a portales | 1 | Eurotax (JD Power / Autovista Group) |
| bruto_bpm (impuesto matriculacion bruto) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| build_code | 1 | MarketCheck (MarketCheck Cars Inc) |
| build_data.feature.code | 1 | AutoGrab |
| build_data.feature.value | 1 | AutoGrab |
| Build quality [RV driver] | 1 | Autovista Group |
| Build quality factor | 1 | Manheim |
| build rules | 1 | JATO Dynamics |
| build_sheet_factory_data | 1 | iSeeCars |
| buildDate | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| buildSource | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| buildyear | 1 | Autotelex B.V. |
| built | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| bulk file content description (opis-zawartosci) [Pliki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| bulk file creation date (data-utworzenia-pliku) [Pliki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| bulk file format description (opis-formatu-pliku) [Pliki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| bulk file metadata URL (url-do-metadanych-pliku) [Pliki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| bulk file resource type, e.g. pojazdy (typ-zasobu-bedacego-zawartoscia) [Pliki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| bulk file URL (url-do-pliku) [Pliki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Bulk Pricing (upload CSV/Excel, resultado <10s) | 1 | Orange Book Value (OBV) |
| Bulk Report Download (basic / premium) | 1 | Orange Book Value (OBV) |
| Bulk valuation (CSV/list upload) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Bus Floor Configuration Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Bus Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Business KPI: QARSD (Quarterly Average Revenue per Subscribing Dealer) | 1 | CarGurus |
| Business rules / auto-approval / reduccion de suplementos | 1 | GT Motive |
| Buy fee | 1 | vAuto |
| buy_now_price | 1 | MarketCheck (MarketCheck Cars Inc) |
| buy order: desired condition | 1 | CarOffer (a CarGurus company) |
| buy order: desired price (limite) | 1 | CarOffer (a CarGurus company) |
| buy order: quantity / quota | 1 | CarOffer (a CarGurus company) |
| Buy Plan Indicator (green star — fit to store buy plan) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Buy-it-now price recommendation | 1 | Autorola |
| Buy-Through Rate (BTR) | 1 | Urban Science |
| buy/sell (network action) | 1 | Urban Science |
| Buyback compensation (hasta 110% J.D. Power NADAguides retail + $500 accesorios) | 1 | Experian Automotive (AutoCheck) |
| Buyback guarantee | 1 | Mahindra First Choice Wheels (MFCWL) |
| buyback_guarantee_eligibility_flag | 1 | CARFAX |
| buyback_payout_110pct_of_hbv | 1 | CARFAX |
| Buyback Protection eligibility | 1 | AutoCheck (by Experian) |
| Buyback Protection eligibility / badge | 1 | Experian Automotive (AutoCheck) |
| Buyer fee (Cost Calculator) | 1 | IAA (Insurance Auto Auctions) |
| Buyer fees financiados | 1 | Cox Automotive Europe |
| Buyer fees per vehicle | 1 | Mahindra First Choice Wheels (MFCWL) |
| Buyer transaction fee | 1 | Dealer Auction |
| buying preference | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| BuyType (Delivery) | 1 | Encar (엔카닷컴 / Encar.com) |
| by GVW (gross vehicle weight) class | 1 | GlobalData Automotive |
| by OEM market | 1 | GlobalData Automotive |
| by supplier / company (223 suppliers) | 1 | GlobalData Automotive |
| Código 55 (importe fijo de pintura) | 1 | Audatex España (Solera) |
| Código de clase de matrícula | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| código de homologación (homoloCode, cruce RUNT) | 1 | Fasecolda — Guía de Valores |
| Código de procedencia | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Código de servicio del vehículo | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Código de tipo de vehículo | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| código Fasecolda (8 dígitos, único; 3 marca + 2 tipología + 3 consecutivo) | 1 | Fasecolda — Guía de Valores |
| Código INE de municipio (COD_MUNICIPIO_INE_VEH) | 1 | Dirección General de Tráfico (DGT) |
| Código INE del municipio | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Código Molicar / Código KBB-Molicar (CodMolicar) — join key | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Código opcional (descripción) | 1 | Audatex España (Solera) |
| Código postal del domicilio | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Códigos de pintura | 1 | Audatex España (Solera) |
| cálculo estructurado de reparaciones | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| cámara de reversa SI/NO (reverseCameraShow) | 1 | Fasecolda — Guía de Valores |
| [EQUIP·Seguridad] Cámara de visión 360º | 1 | km77.com |
| [EQUIP·Seguridad] Cámara de visión trasera | 1 | km77.com |
| câmbio / transmissão | 1 | Webmotors |
| C-PAS追加画像 (up to 9 seller custom images) | 1 | USS (ユー・エス・エス) Co., Ltd. |
| Cab Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| CADSI: 3-month outlook | 1 | Cox Automotive |
| CADSI: costs | 1 | Cox Automotive |
| CADSI: current market | 1 | Cox Automotive |
| CADSI: customer traffic | 1 | Cox Automotive |
| CADSI: EV sales sentiment | 1 | Cox Automotive |
| CADSI: F&I | 1 | Cox Automotive |
| CADSI: limiting factors | 1 | Cox Automotive |
| CADSI: índice overall (0=débil / 50=estable / 100=fuerte) | 1 | Cox Automotive |
| CADSI: price pressure | 1 | Cox Automotive |
| CADSI: profitability | 1 | Cox Automotive |
| Calc: affordability | 1 | Edmunds |
| Calc: auto loan payment | 1 | Edmunds |
| Calc: lease payment | 1 | Edmunds |
| Calc: lease vs buy | 1 | Edmunds |
| Calcolo IVA (iva inclusa / IVA al 40%) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Calculation window (~13 months) | 1 | Manheim |
| Calculo de coste de reparacion | 1 | Eurotax (JD Power / Autovista Group) |
| Calculo de danos / repair estimate (Speedy-Zone) | 1 | Eurotax (JD Power / Autovista Group) |
| Calendario de mantenimiento (prevision) | 1 | Eurotax (JD Power / Autovista Group) |
| calibrations_dynamic_static | 1 | Vehicle Databases |
| Cam | 1 | RedBook |
| cam_type | 1 | DataOne Software (DataOne, LLC) |
| campaign analytics / bid optimization metric | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Campaign Description | 1 | AutoCheck (by Experian) |
| campaign_number | 1 | Vehicle Databases |
| campaignNo | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Camshaft drive | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| canal de comunicación | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| candidate.quote-ratio (popularidad/probabilidad) | 1 | L'argus (Cote Argus®) |
| candidate.suggested (mejor match) | 1 | L'argus (Cote Argus®) |
| CAP Clean peak (%) | 1 | Dealer Auction |
| CAP Clean performance (%) | 1 | Dealer Auction |
| CAP Clean price (reference filter) | 1 | BCA (British Car Auctions) |
| CAP Code (vehicle identifier) | 1 | cap hpi (CAP + HPI, a Solera company) |
| CAP Code identifier | 1 | HPI Check (HPI Ltd, a Solera company) |
| CAP ID | 1 | cap hpi (CAP + HPI, a Solera company) |
| cap value movements | 1 | Cox Automotive Europe |
| Capacidad (pasajeros/carga) | 1 | REPUVE — Registro Público Vehicular |
| capacidad de carga kg (capacityLoad) | 1 | Fasecolda — Guía de Valores |
| capacidad de pasajeros (capacityPassengers) | 1 | Fasecolda — Guía de Valores |
| CapacitaBagagliaio1dm | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CapacitaBagagliaio2dm | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CapacitaBagagliaio3dm | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CapacitaLordakWh | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CapacitaNettakWh | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CapacitaSerbatoioKg | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CapacitaSerbatoioL | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| capacity_cc | 1 | AutoGrab |
| Capilaridad de red secundaria | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| captura de volatilidad / eventos black swan | 1 | Datium Insights |
| Car Buyer Journey (tiempo de compra, satisfacción, canales online/offline) | 1 | Cox Automotive |
| car_city | 1 | MarketCheck (MarketCheck Cars Inc) |
| Car Loan eligibility/EMI (Rupyy) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| car policy details | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Car rankings (por tipo de vehiculo) | 1 | J.D. Power Valuation Services |
| car_state | 1 | MarketCheck (MarketCheck Cars Inc) |
| car_street | 1 | MarketCheck (MarketCheck Cars Inc) |
| car_type (comparison factor) | 1 | AutoUncle |
| 车型/款型/car_type_id (model/trim input) | 1 | Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd. |
| Car Values output: IMV (retail price) | 1 | CarGurus |
| Car Values output: Private Sale Value / Private Sale Estimate | 1 | CarGurus |
| car_zip | 1 | MarketCheck (MarketCheck Cars Inc) |
| características da venda | 1 | Webmotors |
| Caracteristicas de uso/desgaste | 1 | Cox Automotive Europe |
| Caramel escrow/title-transfer status | 1 | Edmunds |
| Caratteristiche tecniche / scheda tecnica completa | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| carfax_clean_title | 1 | MarketCheck (MarketCheck Cars Inc) |
| carfax_integration (iVIN Pro) | 1 | iSeeCars |
| carfax_related_documents | 1 | Stat.vin (1VIN STAT) |
| CARFAX Smart Field (one-owner/clean history) | 1 | vAuto |
| carfax_snapshot (accidents/damage+severity/open recalls/last odometer/usage/owners/service/CPO) | 1 | CARFAX |
| CARFAX Status (badge/check/caution) | 1 | Stockwave (vAuto · Cox Automotive) |
| carfax_vehicle_condition_alert | 1 | Stat.vin (1VIN STAT) |
| [EQUIP·Varios] Carga bidireccional V2L (3 kW) | 1 | km77.com |
| Carga: Hipoteca mobiliaria | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| [EQUIP·Multimedia] Carga inalámbrica para smartphone 15W (2 puntos) | 1 | km77.com |
| Carga: Leasing | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Carga: Potencia máxima CA (kW) | 1 | km77.com |
| Carga: Potencia máxima CC (kW) | 1 | km77.com |
| Carga: Precinto | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Carga: Renting | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Carga: Tiempo de carga 10-80% en CC | 1 | km77.com |
| Carga/gravamen — Hipoteca Mobiliaria | 1 | Dirección General de Tráfico (DGT) |
| Carga/gravamen — Leasing | 1 | Dirección General de Tráfico (DGT) |
| Carga/gravamen — Precinto | 1 | Dirección General de Tráfico (DGT) |
| cargo_room | 1 | iSeeCars |
| cargo_volume_rear_seats_down | 1 | DataOne Software (DataOne, LLC) |
| cargo_volume_row3_down | 1 | DataOne Software (DataOne, LLC) |
| CarGurus Index (aggregate avg used-car price, UK & US) | 1 | CarGurus |
| CarOffer: ~45-day sell guarantee (histórico) | 1 | CarGurus |
| CarOffer Buying Matrix: standing buy orders / limit orders / quotas | 1 | CarGurus |
| CarOffer: Instant Max Cash Offer (IMCO, consumer cash offer) | 1 | CarGurus |
| CarOffer TradeGrade: instant offer in appraisal tool (trade-ins/lease returns/auction cars) | 1 | CarGurus |
| carOrigin / vehicleOrigin | 1 | Autotelex B.V. |
| carOriginDescription | 1 | Autotelex B.V. |
| Carpets condition | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| CarPlay/CarLife | 1 | Autohome (汽车之家) |
| Carrier total-loss threshold | 1 | IAA (Insurance Auto Auctions) |
| carrosserie_national (J.3) | 1 | HistoVec |
| carrosserie_UE (J.2) | 1 | HistoVec |
| carrosseriecode (EU 2007/46/EG) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| carrosserietype | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Carrozzeria | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| carsales_approved_badge_4star_160k_10y | 1 | carsales (carsales.com.au) |
| Écart à la cote / valuation gap (valor autobiz vs precio publicado) | 1 | autobiz (autobiz Group) |
| CarValue: % to Retail | 1 | OPENLANE |
| CarValue: factores ML (depreciacion, estacionalidad, macro, odometro, CR, sale location) | 1 | OPENLANE |
| CarValue: input bid + fees | 1 | OPENLANE |
| CarValue: input recon cost | 1 | OPENLANE |
| CarValue: input transport cost | 1 | OPENLANE |
| CarValue: Profit Calculator (Retail - Transport - Recon - Bid/fees = profit) | 1 | OPENLANE |
| CarValue: Retail-Bid Spread | 1 | OPENLANE |
| CasaCostruttrice | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| cash contributions | 1 | JATO Dynamics |
| Cash For Clunkers eligibility | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Catálogo: comparador de coches (lado a lado) | 1 | coches.net |
| Catálogo: precios por versión | 1 | coches.net |
| Catalizzata | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| catalytic converter / absorber fitted (katalizator-pochlaniacz) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Catastrophic modeling value (insurance) | 1 | Black Book (National Auto Research — Hearst) |
| categoría (category: liviano pasajeros/liviano carga/motos/pesado carga/pesado pasajeros) | 1 | Fasecolda — Guía de Valores |
| Categoría de homologación europea (M1/N1/L…) | 1 | Dirección General de Tráfico (DGT) |
| Categoría de homologación UE (M1/N1/L…) | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| categorie_defect | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| categorie_UE (J) | 1 | HistoVec |
| category.EPAClass | 1 | Edmunds |
| category.market | 1 | Edmunds |
| category.name | 1 | L'argus (Cote Argus®) |
| category.primaryBodyType | 1 | Edmunds |
| category.vehicleSize | 1 | Edmunds |
| category.vehicleStyle | 1 | Edmunds |
| category.vehicleType | 1 | Edmunds |
| Causa de variacion de VR (facelift, efecto lanzamiento) | 1 | Eurotax (JD Power / Autovista Group) |
| Cavity Protection Matrix (UK) | 1 | GT Motive |
| CCPA consent | 1 | Accu-Trade (AccuTrade) |
| CCTV / security status | 1 | Mahindra First Choice Wheels (MFCWL) |
| Ce que l'IA a repéré (équipements destacados) | 1 | La Centrale |
| Cell-maker tracking | 1 | Glass's |
| Census: date sold | 1 | cap hpi (CAP + HPI, a Solera company) |
| Census: distance & drive time to retail | 1 | cap hpi (CAP + HPI, a Solera company) |
| Census: market trends & forecasting | 1 | cap hpi (CAP + HPI, a Solera company) |
| Census: sales opportunity quantification | 1 | cap hpi (CAP + HPI, a Solera company) |
| Census: vehicle age | 1 | cap hpi (CAP + HPI, a Solera company) |
| Census: vehicle types (cars/LCV/HGV/bikes/motorhomes/agricultural) | 1 | cap hpi (CAP + HPI, a Solera company) |
| center_bore | 1 | Vehicle Databases |
| central vs store-level offer control | 1 | CarOffer (a CarGurus company) |
| centralLocking | 1 | mobile.de |
| Certificado de Conformidad (CoC) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Certificado DGT de transferencia de responsabilidad | 1 | Audatex España (Solera) |
| certificate_of_destruction_issued | 1 | AutoGrab |
| certificate_of_title | 1 | carVertical |
| certificate.created_at | 1 | AutoGrab |
| certificate.id | 1 | AutoGrab |
| certificate.url (PDF) | 1 | AutoGrab |
| certified / CPO badge | 1 | Cars Commerce (Cars.com Inc.) |
| certified_pre_owned_cpo_indicator | 1 | CARFAX |
| Certified Pre-Owned / Courtesy buyback | 1 | AutoCheck (by Experian) |
| Certified Pre-Owned (CPO) premium value | 1 | J.D. Power Valuation Services |
| Certified Pre-Owned (CPO) price | 1 | Edmunds |
| CertiFirst certification status | 1 | Mahindra First Choice Wheels (MFCWL) |
| change-of-address / append | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Charge lead 1 condition (OEM or not) | 1 | BCA (British Car Auctions) |
| Charge lead 2 condition | 1 | BCA (British Car Auctions) |
| Charge port condition | 1 | BCA (British Car Auctions) |
| Charger Level | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| ChargeSust_Comb | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ChargeSustaining | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| chart / table auto-generation (1-click) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| chassisVin (VIN) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| Chat 24/7 (CarGurus rep on listing) | 1 | CarGurus |
| Check performed date/time | 1 | HPI Check (HPI Ltd, a Solera company) |
| Check reference number | 1 | HPI Check (HPI Ltd, a Solera company) |
| Cherished plate transfers | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| child_occupant_protection_score | 1 | carVertical |
| Child Safety Locks | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Chilometraggi rilevati alle revisioni (km history) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Chilometraggio all'ultima revisione | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| ChilometriTeorici | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ChilometriTeoriciMensili | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ChilometriTeoriciStandard | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| China EV sales (monthly units, macro) | 1 | CarNewsChina Data (China EV DataTracker) |
| Chrome ACode | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| chrome_body_id | 1 | Accu-Trade (AccuTrade) |
| Chrome extension overlay | 1 | CarOffer (a CarGurus company) |
| Chrome YMMID | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| chromeCode | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| CI_annule | 1 | HistoVec |
| CI_date_annulation | 1 | HistoVec |
| CI_declare_perdue | 1 | HistoVec |
| CI_declare_volee | 1 | HistoVec |
| CI_duplicata | 1 | HistoVec |
| CicliWltp | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CicliWltpHybrid | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ciclo de vida del vehículo | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Ciclo de vida del vehiculo (altas/bajas/transferencias) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| [EQUIP·Confort] Cierre centralizado | 1 | km77.com |
| [EQUIP·Seguridad] Cierre de seguridad para niños en puertas traseras | 1 | km77.com |
| CIF del taller | 1 | Audatex España (Solera) |
| cilinderinhoud | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| cilindraje cc (cylinderCapacity) | 1 | Fasecolda — Guía de Valores |
| Cilindrata | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CilindrataA | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CilindrataDa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CIN (Codigo de Identificacion del Navio) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| [EQUIP·Seguridad] Cinturones delanteros regulables en altura | 1 | km77.com |
| City-level ICE comparison sales | 1 | CarNewsChina Data (China EV DataTracker) |
| ciudad (城市) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Claim cost (KPI) | 1 | GT Motive |
| Claim number | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Claim reference number | 1 | CCC Intelligent Solutions |
| claim.claimID | 1 | AutoGrab |
| claim.claimNumber | 1 | AutoGrab |
| claim.claimValuation | 1 | AutoGrab |
| claim.reportURL | 1 | AutoGrab |
| Claimant name | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Claims Companion condition assessment | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Claims management | 1 | cap hpi (CAP + HPI, a Solera company) |
| Claims payout value | 1 | Black Book (National Auto Research — Hearst) |
| Clase de matrícula (ordinaria/turística/remolque/diplomática/reservada/especial/ciclomotor/temporal/histórica) | 1 | Dirección General de Tráfico (DGT) |
| Clasificación pérdida total vs reparable por foto (Intelligent Triage) | 1 | Audatex España (Solera) |
| classe_CritAir_vignette (derivada: 1-5/ELECTRIQUE/NON_CLASSE) | 1 | HistoVec |
| classe_environnementale_UE (V.9) | 1 | HistoVec |
| Classe Euro | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| ClasseEuro | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| classic_drive | 1 | Vehicle Databases |
| classic_fuel | 1 | Vehicle Databases |
| CLASSIC.COM Market Benchmark (CMB) | 1 | CLASSIC.COM |
| classificatie_toegevoegd_object | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Clave de trámite | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Clave del trámite (CLAVE_TRAMITE) | 1 | Dirección General de Tráfico (DGT) |
| Clave vehicular | 1 | REPUVE — Registro Público Vehicular |
| ClearCar Capture (AI imaging + self-inspection) | 1 | ACV Auctions |
| ClearCar Price (digital value estimate widget en web del dealer) | 1 | ACV Auctions |
| Click rates | 1 | VINCUE (DealerCue Automotive Corp.) |
| Climate control / Air conditioning | 1 | ClearVin |
| climatisation | 1 | mobile.de |
| [EQUIP·Confort] Climatización por bomba de calor | 1 | km77.com |
| [EQUIP·Confort] Climatizador bizona | 1 | km77.com |
| Cloned / false identity | 1 | cap hpi (CAP + HPI, a Solera company) |
| Cloned / false identity indicator | 1 | HPI Check (HPI Ltd, a Solera company) |
| 续航 CLTC | 1 | Autohome (汽车之家) |
| clutch | 1 | Vehicle Databases |
| Clutch slip test | 1 | BCA (British Car Auctions) |
| CMB trend direction (flecha up/down) | 1 | CLASSIC.COM |
| Co-Driver: AI vehicle description | 1 | Auto Trader UK (Autotrader Group plc) |
| Co-Driver: missing image detection | 1 | Auto Trader UK (Autotrader Group plc) |
| Co-Driver: optimal image ordering | 1 | Auto Trader UK (Autotrader Group plc) |
| co2Class | 1 | mobile.de |
| CO2Combinato | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CO2CombinatoMassimo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CO2CombinatoMinimo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| cO2Combined (CO2 combinado) | 1 | Autotelex B.V. |
| CO2ExtraHigh | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CO2High | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CO2Low | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CO2Medium | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CO2Wltp | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Cobertura 100% del hammer price | 1 | Cox Automotive Europe |
| Cobertura del mercado objetivo | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Cobertura territorial | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Cockpit: crédito pré-aprovado del comprador | 1 | Webmotors |
| Cockpit: leads / contatos (CRM) | 1 | Webmotors |
| Cockpit: performance do negócio / indicadores | 1 | Webmotors |
| cocNumber | 1 | Autotelex B.V. |
| Code Boost IQ: banner OBD2 nivel 'Confirmed trouble codes' | 1 | OPENLANE |
| Code Boost IQ: banner OBD2 nivel 'High probability of repair needed' | 1 | OPENLANE |
| Code Boost IQ: banner OBD2 nivel 'No trouble codes' | 1 | OPENLANE |
| Code Boost IQ: probabilidad predictiva de reparacion / arbitraje | 1 | OPENLANE |
| code_mogelijk_gevaar (ONG/TEL/BRA/MIL) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Code postal | 1 | La Centrale |
| code_toelichting_tellerstandoordeel | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| code_wijze_informeren (BRI/BEL/ADV/NTB) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| codelinksrechtsrijdend | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Codice connettore (EV) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Codice motore | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| CodiceAlimentazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceAllestimento | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceCasa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceCasaCostruttrice | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceCombustibile | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceEquipaggiamento | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceInfobikePRG | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceInfocar | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceInfocarAM | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceInterni | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceModalitaMisuraTempo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceModalitaRicarica | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceMotivazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceMotore | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceNucleoMotore | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceOmologazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceOptEscluso | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceOptIncluso | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceOptVincolato | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceQRTIncomp | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceRCLPrg | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceRT | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceRuoteClassiche | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceSerie | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceSpeciale | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceSpia | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceStruttura | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceSVG | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceTipoBatterie | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceTipoPresa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiceVIN | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodiciAutoscout | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CodificaAS24 | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| codigo_fipe (formato XXXXXX-X, 7 dígitos) | 1 | FIPE (Tabela Fipe Veículos) |
| Codigo unico de vehiculo Eurotax / NatCode (codificacion paneuropea) | 1 | Eurotax (JD Power / Autovista Group) |
| coding type of type-subtype-purpose (rodzaj-kodowania-rodzaj-podrodzaj-przeznaczenie) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Coeficiente aerodinámico Cx | 1 | km77.com |
| collateral_validation_type_condition | 1 | CARFAX |
| Comb_Weighted | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Combination prices | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Combined Braking System (CBS) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| combined_litres_100km | 1 | AutoGrab |
| combustível | 1 | Webmotors |
| Combustibile | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| comfort & convenience features | 1 | JATO Dynamics |
| comfort_features | 1 | TrueCar |
| Commentaire du vendeur | 1 | La Centrale |
| Commercial new & used residual monitor | 1 | cap hpi (CAP + HPI, a Solera company) |
| Commercial trailer type (11 types) | 1 | Black Book (National Auto Research — Hearst) |
| commercial use (taxi/rental/lease/fleet/police) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| commercial-to-private market transition | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Common Problems (problemas mas probables del VIN) | 1 | vAuto |
| communautaire_codes_eu (codigos del kentekenbewijs J/D/R/K/B/I/G/F/O en OVI) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Comp relevance score (%) | 1 | CLASSIC.COM |
| company activity / industry (branch) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| company address | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| company car flag | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| company car taxation (BIK) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| company contact details | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| company financials | 1 | GlobalData Automotive |
| company innovations | 1 | GlobalData Automotive |
| company news & key developments | 1 | GlobalData Automotive |
| company profile | 1 | GlobalData Automotive |
| Company-owned deduction (רכב חברה) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| company/fleet detail (contact/title/phone/revenue/employees/SIC) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| companystockOwner | 1 | Autotelex B.V. |
| companystockType | 1 | Autotelex B.V. |
| Comparable adjusted value | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Comparable: build quality | 1 | Manheim |
| Comparable City/State (proximity) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Comparable condition reports | 1 | ACV Auctions |
| Comparable data source (Vast / Cars.com / Leading Internet Auto Site) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Comparable date observed | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Comparable equipment list | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| comparable listings (comp set) | 1 | CarOffer (a CarGurus company) |
| Comparable rank # | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Comparable recently sold vehicles | 1 | VINCUE (DealerCue Automotive Corp.) |
| Comparable sale: condicion del ejemplar | 1 | Hagerty |
| Comparable: sale date | 1 | Manheim |
| Comparable sale: fecha de venta | 1 | Hagerty |
| Comparable sale: fotos | 1 | Hagerty |
| Comparable sale: fuente / casa de subasta | 1 | Hagerty |
| Comparable sale: market commentary (comentario de mercado) | 1 | Hagerty |
| Comparable sale: notas de equipamiento/opciones | 1 | Hagerty |
| Comparable: sale price | 1 | Manheim |
| Comparable Stock # | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Comparable vehicle: Distance (straight-line to loss) | 1 | CCC Intelligent Solutions |
| Comparable vehicle: Take Price | 1 | CCC Intelligent Solutions |
| comparable vehicles (side-by-side) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Comparable vehicles nearby (listings) | 1 | Canadian Black Book |
| comparable_vehicles_side_by_side (year/make/model/trim/options/location/mileage/history) | 1 | CARFAX |
| comparables | 1 | MarketCheck (MarketCheck Cars Inc) |
| # comparables located | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| comparables_scatter_chart (vs linea de market price) | 1 | iSeeCars |
| Comparacion de precios | 1 | Cox Automotive Europe |
| comparacion multi-vehiculo de curvas RV | 1 | Datium Insights |
| Comparador de Precios Avanzado (precio vs competencia/mercado) | 1 | coches.net |
| ComparazionePrezzo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Compare Similar Vehicles (features/performance) | 1 | Orange Book Value (OBV) |
| competition level (number of competing vehicles) | 1 | INDICATA (Autorola Group) |
| Competitive analysis | 1 | ACV Auctions |
| Competitive derivative comparison | 1 | cap hpi (CAP + HPI, a Solera company) |
| Competitive residual analysis (quarterly) | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| competitive RV benchmark | 1 | INDICATA (Autorola Group) |
| Competitive sales trends (Elite) | 1 | Experian Automotive (AutoCheck) |
| Competitive set (identicos en mercado vivo) | 1 | vAuto |
| competitive win/loss (media planning) | 1 | Urban Science |
| Competitive win/loss through service over time | 1 | VINCUE (DealerCue Automotive Corp.) |
| competitor_strategies | 1 | TrueCar |
| Competitor View (similar stock in market) | 1 | Auto Trader UK (Autotrader Group plc) |
| complete_customer_profile_truecar_access | 1 | TrueCar |
| completed_repairs (CA) | 1 | CARFAX |
| completedDate (mot test) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| Compliance date (NEVDIS) | 1 | RedBook |
| compliance_plate | 1 | AutoGrab |
| complianceDate (ISO-8601, primer dia del mes/anyo) | 1 | Datium Insights |
| Comportamiento real de mercado | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| composite group financial benchmark | 1 | Urban Science |
| ComposizionePack | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| comprador del vehículo | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| compression | 1 | DataOne Software (DataOne, LLC) |
| Compromiso (SI/NO) | 1 | Audatex España (Solera) |
| Comunidad Autónoma (nivel de agregación) | 1 | Dirección General de Tráfico (DGT) |
| Concealed proxy bid | 1 | BCA (British Car Auctions) |
| Concept strengths/weaknesses (perceived quality) [RV driver] | 1 | Autovista Group |
| Condición itemCondition (nuevo/ocasión/km0/seminuevo) | 1 | coches.net |
| Condicion/defectos de interior | 1 | Cox Automotive Europe |
| Condition #1 (Concours) value | 1 | Hagerty |
| Condition #2 (Excellent) value | 1 | Hagerty |
| Condition #3 (Good) value | 1 | Hagerty |
| Condition #4 (Fair) value | 1 | Hagerty |
| condition_confirmed_inperson | 1 | TrueCar |
| Condition description text per sub-category (Typical Condition Statement) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Condition flags (Inspection / Record / Resume) | 1 | Encar (엔카닷컴 / Encar.com) |
| Condition of body (CR) | 1 | Copart, Inc. |
| Condition preferences (warning lights/tire/frame/title) | 1 | ACV Auctions |
| Condition questionnaire | 1 | ACV Auctions |
| Condition Rating (per component, appraiser-selected) | 1 | CCC Intelligent Solutions |
| Condition rating score (escala 10 puntos por aspecto: interior, frenos, neumaticos) | 1 | MAX Digital (ACV MAX) |
| Condition rating value impact | 1 | CCC Intelligent Solutions |
| condition_score (1-5: Poor/Fair/Average/Good/Excellent) | 1 | AutoGrab |
| Condition tier definition / guidelines (rollover por condicion) | 1 | Hagerty |
| Condition-adjusted price (Great/Good/Fair) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Condition-adjusted valuation | 1 | Auto Trader UK (Autotrader Group plc) |
| Condition-based offers | 1 | ACV Auctions |
| condition.seizing (gravámenes / 압류 / embargo, con conteo) | 1 | Encar (엔카닷컴 / Encar.com) |
| conditionsRequired (Clean/Average/Below/Retail) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Conductor habitual designado | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| [EQUIP·Multimedia] Conexión Bluetooth para teléfono | 1 | km77.com |
| confidence (match quality: standard) | 1 | AutoGrab |
| Confidence of Sale (probability within target days) | 1 | Auto Trader UK (Autotrader Group plc) |
| Confidence score | 1 | RedBook |
| confidence-index (índice de confianza) | 1 | L'argus (Cote Argus®) |
| confidence-intervals.max | 1 | L'argus (Cote Argus®) |
| confidence-intervals.min | 1 | L'argus (Cote Argus®) |
| confidence-intervals.probability | 1 | L'argus (Cote Argus®) |
| confidenceInterval.priceRange.adjustedHigh | 1 | Cox Automotive |
| confidenceInterval.priceRange.adjustedLow | 1 | Cox Automotive |
| configuraciones de fábrica | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Confische (presenza) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Confronto annunci propri vs competitor | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Confronto fino a 3 veicoli | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| conquest / competitor audience (customizable) | 1 | Urban Science |
| conquest / new customer acquisition | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| conquest rate (network) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Cons (Could Be Better) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Consolidated Condition Report (single VDP view, 2025) | 1 | Manheim |
| Consommation (L/100km) | 1 | La Centrale |
| Consommation Faible (flag) | 1 | La Centrale |
| Consommation max (filtre) | 1 | La Centrale |
| Constancia de aseguramiento | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| constructionDate | 1 | mobile.de |
| constructionMonth | 1 | Autotelex B.V. |
| consultoría / soporte al negocio | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Consumer category ratings | 1 | Edmunds |
| consumer_complaints | 1 | iSeeCars |
| Consumer demographics (Elite) | 1 | Experian Automotive (AutoCheck) |
| Consumer email | 1 | Accu-Trade (AccuTrade) |
| Consumer first/last name | 1 | Accu-Trade (AccuTrade) |
| Consumer Intelligence - buy/sell preference analytics | 1 | Orange Book Value (OBV) |
| Consumer Intelligence - market overview | 1 | Orange Book Value (OBV) |
| consumer market value estimate (estimacion de valor de mercado) | 1 | Datium Insights |
| Consumer number of reviews | 1 | Edmunds |
| Consumer Offer Report (inputs de valoracion + deducciones) | 1 | vAuto |
| Consumer Overall Rating (of 5) | 1 | Kelley Blue Book |
| Consumer Overall star rating (of 5) | 1 | Edmunds |
| Consumer phone / cell_phone | 1 | Accu-Trade (AccuTrade) |
| Consumer postal_code (factor regional de pricing) | 1 | Accu-Trade (AccuTrade) |
| consumer_preferences | 1 | TrueCar |
| Consumer rating: comfort | 1 | Kelley Blue Book |
| Consumer rating count (based on N ratings) | 1 | Kelley Blue Book |
| Consumer rating: performance | 1 | Kelley Blue Book |
| Consumer rating: quality | 1 | Kelley Blue Book |
| Consumer rating: reliability | 1 | Kelley Blue Book |
| Consumer rating: styling | 1 | Kelley Blue Book |
| Consumer rating: value | 1 | Kelley Blue Book |
| Consumer recommend % | 1 | Edmunds |
| Consumer Review (owner) | 1 | Kelley Blue Book |
| Consumer review date | 1 | Edmunds |
| Consumer review text | 1 | Edmunds |
| Consumer Satisfaction Award | 1 | Cars Commerce (Cars.com Inc.) |
| Consumer star distribution (5★-1★) | 1 | Edmunds |
| Consumer Summary (AI-generated) | 1 | Edmunds |
| Consumer Verified Rating - driving experience | 1 | J.D. Power Valuation Services |
| Consumer Verified Rating - quality & reliability | 1 | J.D. Power Valuation Services |
| Consumer Verified Rating - service experience | 1 | J.D. Power Valuation Services |
| consumerInformation.item.conditionNote | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| consumerInformation.item.name | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| consumerInformation.item.value | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| consumerInformation.type | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Consumerprice (precio de consumo/lista) | 1 | Autotelex B.V. |
| consumerPriceGross | 1 | mobile.de |
| consumerPriceNet | 1 | mobile.de |
| ConsumiWltp | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| contact.address (ubicación dealer) | 1 | Encar (엔카닷컴 / Encar.com) |
| contact.userType / userId (tipo de vendedor) | 1 | Encar (엔카닷컴 / Encar.com) |
| Contacto de flota (direccion/telefono/email) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| contents.text (descripción del dealer) | 1 | Encar (엔카닷컴 / Encar.com) |
| Conteo mensual de anunciantes profesionales por red | 1 | autobiz (autobiz Group) |
| [EQUIP·Decoración] Contorno de ventanillas cromado | 1 | km77.com |
| Contract equity | 1 | RedBook |
| contribución al PIB (%) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| [EQUIP·Seguridad] Control de crucero adaptativo (ACC) | 1 | km77.com |
| [EQUIP·Seguridad] Control de crucero inteligente | 1 | km77.com |
| [EQUIP·Seguridad] Control de estabilidad (ESP) | 1 | km77.com |
| Control de estabilidad/ESP | 1 | Audatex España (Solera) |
| [EQUIP·Seguridad] Control de presión de neumáticos (TPMS) | 1 | km77.com |
| Control de stock / inventario | 1 | Eurotax (JD Power / Autovista Group) |
| [EQUIP·Seguridad] Control de tracción | 1 | km77.com |
| Control de velocidad | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| control del valor por etapa del ciclo de vida | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| controle_technique_date | 1 | HistoVec |
| controle_technique_nature (VTP/VTC/CV/CVC) | 1 | HistoVec |
| controle_technique_nature_libelle | 1 | HistoVec |
| controle_technique_resultat (A/AP/S/SP/R/RP/X) | 1 | HistoVec |
| controle_technique_resultat_libelle (Favorable / Defavorable defaillances majeures / Defavorable defaillances critiques / Report) | 1 | HistoVec |
| controles_techniques_date_mise_a_jour | 1 | HistoVec |
| controles_techniques_donnee_disponible | 1 | HistoVec |
| Conversión UT-hora (10 UT/h; BMW 12 UT/h) | 1 | Audatex España (Solera) |
| Convertible / sunroof electrics | 1 | BCA (British Car Auctions) |
| Convertible roof condition | 1 | BCA (British Car Auctions) |
| convertible roof up/down photos (conditional) | 1 | Motorway |
| Convertible top condition | 1 | OPENLANE |
| Coolant system level | 1 | BCA (British Car Auctions) |
| cooling | 1 | Vehicle Databases |
| Cooling medium | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Cooling Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| CoppiaKgm | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CoppiaMaxGiriMinuto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CoppiaNm | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| copyright | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| cor | 1 | Webmotors |
| Corrected Title | 1 | Experian Automotive (AutoCheck) |
| Corredor de valor (value corridor, rango min-máx) | 1 | Audatex España (Solera) |
| CorrenteRicaricaAmpere | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CorrenteRicaricaRapida | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CorrettivoChilometrico | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CorrettivoChilometricoApplicato | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CorrettivoImmatricolazioneAutocarro | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CorrettivoNoteQualificanti | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Cosmetic defects | 1 | Manheim |
| Cosmetic irregularities / paint quality | 1 | ACV Auctions |
| Cost / pence-per-mile (TCO, derived) | 1 | cap hpi (CAP + HPI, a Solera company) |
| cost_desc | 1 | Vehicle Databases |
| cost_high | 1 | Vehicle Databases |
| cost_low | 1 | Vehicle Databases |
| cost_name_parts_labor | 1 | Vehicle Databases |
| cost_per_sale | 1 | AutoUncle |
| cost per unit sold | 1 | Urban Science |
| Cost to Market % (via conexion Provision) [RECONSTRUIDO] | 1 | Stockwave (vAuto · Cox Automotive) |
| Cost to Market (%) — objetivo 84% / spread 16% | 1 | MAX Digital (ACV MAX) |
| Cost to Market (%) — spread coste adquisicion+recon vs retail medio (benchmark <=84%) | 1 | vAuto |
| Cost to Run: Fuel/Energy cost (incl EV energy) | 1 | RedBook |
| Cost to Run: On-road costs (registration, govt duties, CTP insurance, levies) | 1 | RedBook |
| Cost to Run: Servicing | 1 | RedBook |
| Cost to Run: Tyres | 1 | RedBook |
| Cost-to-Market (CTM) indicator | 1 | VINCUE (DealerCue Automotive Corp.) |
| Cost-to-market spread | 1 | vAuto |
| Coste de equipamiento y accesorios | 1 | Eurotax (JD Power / Autovista Group) |
| Coste de garantía | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Coste de reacondicionamiento (auto desde grid de costes) | 1 | autobiz (autobiz Group) |
| Coste de reparación (Noa) | 1 | autobiz (autobiz Group) |
| Coste de transporte por ruta (más rápida vs más barata) | 1 | AUTO1 Group |
| Coste por día en stock | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Costes / tiempos de mano de obra | 1 | Eurotax (JD Power / Autovista Group) |
| costes de reparación | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Costes logísticos / de transporte | 1 | autobiz (autobiz Group) |
| Costi aggiuntivi (kit consegna, contributi ambientali, servizi) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Costi di messa su strada (auto-calcolati per provincia) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Costi di riparazione carrozzeria | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Costi di riparazione meccanica | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| costModel co2Costs | 1 | mobile.de |
| costModel fuelPrice | 1 | mobile.de |
| CostoGaranzia | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CostoManodopera | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CostoOrarioManoOpera | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Cote affinée (personnalisée) | 1 | La Centrale |
| Cote Argus® (custom-market-values, cote de référence) | 1 | L'argus (Cote Argus®) |
| Cote Argus Personnalisée® (web) | 1 | L'argus (Cote Argus®) |
| Cote brute (valeur véhicule moyen) | 1 | La Centrale |
| Couleurs extérieur | 1 | La Centrale |
| Couleurs intérieur | 1 | La Centrale |
| Country of Assembly | 1 | AutoCheck (by Experian) |
| Country of origin / pais de origen | 1 | autoDNA |
| Couple cumulé (Nm @ tr/min) | 1 | La Centrale |
| Coverage stat: 1.3M valuation reports completed in 2024 | 1 | CARFAX Canada |
| Coverage stat: access to 30B+ data records | 1 | CARFAX Canada |
| Coverage stat: access to >90% of all Canadian vehicle listing data | 1 | CARFAX Canada |
| Cox Auto Rates & Incentives (rates/rebates/incentives) | 1 | DataOne Software (DataOne, LLC) |
| Cox Forecast: fleet sales forecast | 1 | Cox Automotive |
| Cox Forecast: new-vehicle sales forecast | 1 | Cox Automotive |
| Cox Forecast: retail sales forecast | 1 | Cox Automotive |
| Cox Forecast: SAAR | 1 | Cox Automotive |
| Cox Intelligence: AI-infused MMR valuations | 1 | Cox Automotive |
| Cox Intelligence: Trade Desk (curación/negociación asistida IA) | 1 | Cox Automotive |
| Cox Intelligence: Vehicle recommendation score (ML vs perfil de puja/compra) | 1 | Cox Automotive |
| cpc (Certificate of Professional Competence) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| CPO Compliance Review result | 1 | OPENLANE |
| CPO data | 1 | MAX Digital (ACV MAX) |
| CPO eligibility | 1 | Experian Automotive (AutoCheck) |
| CPO flag | 1 | Black Book (National Auto Research — Hearst) |
| CPO history (history factor) | 1 | Canadian Black Book |
| cpo_indicator | 1 | TrueCar |
| CPO premium ($1,000-$2,000) | 1 | Kelley Blue Book |
| CPO program performance | 1 | INDICATA (Autorola Group) |
| CPO sale flag (99% US coverage) | 1 | Urban Science |
| CPO value (when applicable) | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| CR additional photos | 1 | Copart, Inc. |
| CR videos (2 internos/externos) | 1 | Copart, Inc. |
| created_at | 1 | MarketCheck (MarketCheck Cars Inc) |
| creationDate | 1 | mobile.de |
| crecimiento interanual del volumen (%) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Credit line / limite de funding | 1 | Cox Automotive Europe |
| credit score | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| credit tier | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| CreditIQ: APR | 1 | Cars Commerce (Cars.com Inc.) |
| CreditIQ: down_payment | 1 | Cars Commerce (Cars.com Inc.) |
| CreditIQ: instant_loan_approval / decision | 1 | Cars Commerce (Cars.com Inc.) |
| CreditIQ: lender_match (BYOL, 800+ lenders) | 1 | Cars Commerce (Cars.com Inc.) |
| CreditIQ: loan_term | 1 | Cars Commerce (Cars.com Inc.) |
| CreditIQ: penny-perfect monthly_payment | 1 | Cars Commerce (Cars.com Inc.) |
| CreditIQ: pre-approval | 1 | Cars Commerce (Cars.com Inc.) |
| CreditiTotali | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| CreditiUsati | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Crit'air max (filtre) | 1 | La Centrale |
| CRM / lead management | 1 | Mahindra First Choice Wheels (MFCWL) |
| CRM lead match / Re-Engage (active/unsold by Year-Make-Model) | 1 | VINCUE (DealerCue Automotive Corp.) |
| CRM share | 1 | MAX Digital (ACV MAX) |
| Cross-border admin: aduanas / IVA / BPM | 1 | OPENLANE |
| cross-border opportunity / route | 1 | INDICATA (Autorola Group) |
| Cross-Border Potential Score | 1 | autobiz (autobiz Group) |
| cross-border price | 1 | INDICATA (Autorola Group) |
| Cross-country weighted average value | 1 | Glass's |
| Cross-market / like-for-like RV comparison | 1 | Autovista Group |
| CRS ID (powersports) | 1 | DataOne Software (DataOne, LLC) |
| Cruise Control | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Crush / disposal watch | 1 | cap hpi (CAP + HPI, a Solera company) |
| CTM + PTM+ investment buckets | 1 | VINCUE (DealerCue Automotive Corp.) |
| [EQUIP·Decoración] Cuadro de instrumentos digital de 26 cm (10,25") | 1 | km77.com |
| cubicCapacity (ccm) | 1 | mobile.de |
| Cuenta atrás de fin de subasta (24h) | 1 | AUTO1 Group |
| Cuentakilómetros — Fecha de lectura | 1 | Dirección General de Tráfico (DGT) |
| Cuentakilómetros — Origen (ITV/declaración voluntaria/talleres) | 1 | Dirección General de Tráfico (DGT) |
| cuota % (sobre total) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| cuota % de alternativos sobre producción total | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Cuota ajustada | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Cuota de financiacion (financeRate) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Cuota de leasing / detalles leasing (leasingRate/leasingDetails) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| cuota modal logística - carretera % | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| cuota modal logística - ferrocarril % | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| cuota modal logística - marítimo % | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Cup Holders | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Currency code | 1 | Copart, Inc. |
| Current / highest bid | 1 | Dealer Auction |
| Current bid / High bid | 1 | Copart, Inc. |
| Current bid / price | 1 | Autorola |
| Current days in stock (input) | 1 | Auto Trader UK (Autotrader Group plc) |
| current market value (Car Value Tracker) | 1 | Motorway |
| Current Sale Highlights (comentarios GM) | 1 | Copart, Inc. |
| Current title issue date | 1 | ClearVin |
| Current title state | 1 | ClearVin |
| current_title_status | 1 | Vehicle Databases |
| Current type (AC/DC) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| current valuation | 1 | INDICATA (Autorola Group) |
| Current value | 1 | Autovista Group |
| Current value forecast (B2B) | 1 | Hagerty |
| Custom economic scenario residual | 1 | Black Book (National Auto Research — Hearst) |
| Custom Motorcycle Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Custom recon metrics | 1 | vAuto |
| Custom repair line items | 1 | Glass's |
| Customer address: street/house_number/postal_code/city/province/country (lead) | 1 | Autotelex B.V. |
| Customer email (lead) | 1 | Autotelex B.V. |
| Customer engagement triggers (MOT reminders / pricing updates) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| customer_incentives | 1 | TrueCar |
| customer retention (from outgoing model) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Customer salutation/initials/first_name/infix/last_name (lead) | 1 | Autotelex B.V. |
| Customer telephone (lead) | 1 | Autotelex B.V. |
| Customer-to-car matching | 1 | vAuto |
| customer.additional_fields | 1 | AutoGrab |
| customer.external_id | 1 | AutoGrab |
| customer.id | 1 | AutoGrab |
| customer.monitor_end_date | 1 | AutoGrab |
| customer.monitor_start_date | 1 | AutoGrab |
| customer.rego | 1 | AutoGrab |
| customer.sale_date | 1 | AutoGrab |
| customer.state | 1 | AutoGrab |
| customer.vehicle_title | 1 | AutoGrab |
| Customer/salesperson signature capture | 1 | BCA (British Car Auctions) |
| customerId | 1 | mobile.de |
| customerNumber | 1 | mobile.de |
| customerReferenceNumber (id de peticion) | 1 | Datium Insights |
| CVS: Measurements A-G | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| CVS: Wheelbase (WB) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Cycle time (KPI) | 1 | GT Motive |
| Cycle-time optimization (IntelliSeller) | 1 | Copart, Inc. |
| Cylinder angle (V-engines) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| cylinder_arrangement | 1 | AutoGrab |
| Cylindrée (cm³) | 1 | La Centrale |
| cylindree_cm3 (P.1) | 1 | HistoVec |
| Días en stock / duración de publicación | 1 | autobiz (autobiz Group) |
| Début commercialisation | 1 | La Centrale |
| Délai Argus Rotation® (days-to-sell, mediana de detención) | 1 | L'argus (Cote Argus®) |
| Daño de llanta/rueda | 1 | Cox Automotive Europe |
| Daño de panel estructural | 1 | Cox Automotive Europe |
| Dagwaarde (nombrada en intro; materializa como Vervangingswaarde) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Dagwaarde / vervangingswaarde (valor de día/reposición, excl. IVA y BPM) | 1 | Autotelex B.V. |
| Danno | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Dashboard: Category/Fuel-type split (PV/CV/3W/2W/EV) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Dashboard: MoM Growth % | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| dashboard photo (steering wheel + centre console + gearstick) | 1 | Motorway |
| Dashboard: Total Production (units) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Dashboard: Total Sales (units) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Dashboard: YoY Growth % | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| DAT Euro-Code (codigo identificador 15 digitos) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| data_consulta (timestamp da consulta) | 1 | FIPE (Tabela Fipe Veículos) |
| Data di produzione (decode VIN, 2016+) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Data e paese di prima immatricolazione | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| data entry date (data-wprowadzenia-danych) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Data fine produzione | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Data inizio produzione | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| data plate type (rodzaj-tabliczki-znamionowej) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Data prossima revisione | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Data scadenza locazione | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Data scadenza patto riservato dominio (PRD) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Data scadenza usufrutto | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| data_sources_count | 1 | carVertical |
| data_sources_countries_count | 1 | carVertical |
| Data ultima revisione | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Data ultimo atto di proprieta | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| DataAttoProprieta | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DataCleanse: GDPR-compliant flag por vehiculo | 1 | Manheim UK |
| DataCleanse: personal data on documentation (obscured/redacted) | 1 | Manheim UK |
| DataCleanse: sat nav destination history (removed) | 1 | Manheim UK |
| DataCleanse: synced mobile data (removed) | 1 | Manheim UK |
| DataImmatricolazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DataImmatricolazioneEstera | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DataOne VehicleID | 1 | DataOne Software (DataOne, LLC) |
| DataPrimaImmatricolazioneItalia | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| dataSource (dvsa/dvla/dva ni) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| Date automobile obtained | 1 | NMVTIS / VehicleHistory.gov |
| Date de publication (days-on-market) | 1 | La Centrale |
| date_derniere_procedure_VE | 1 | HistoVec |
| date_fin_derniere_procedure_VE | 1 | HistoVec |
| date_mise_a_jour_rapport | 1 | HistoVec |
| Date of Loss Adjustment (depreciation since loss date) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| date_of_manufacture | 1 | Vehicle Databases |
| Date of purchase (point-of-quote pre-fill) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| date of sale | 1 | Urban Science |
| date_of_title_issuance | 1 | Vehicle Databases |
| date_v5c_issued | 1 | AutoGrab |
| dateCreated | 1 | Autotelex B.V. |
| dateOfLastKeeperChange [NV bulk] | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| dateRegistered | 1 | Autotelex B.V. |
| DatiOmologazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DatiTecniciOmologati | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DatiumInstantVal (valor de la valoracion, importe) | 1 | Datium Insights |
| DatiumInstantValCurrency (AUD) | 1 | Datium Insights |
| Datos / tiempos de pintura (fuente AZT) | 1 | Eurotax (JD Power / Autovista Group) |
| datos de contacto (proporcionados por fabricante) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| datos de contacto actualizados (DGT) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Datos de inventario (número y tipo de anuncios) | 1 | autobiz (autobiz Group) |
| datos de negocio VO (usado) diarios | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| datos de Red (concesionarios/puntos de venta) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Datos de subasta de restos AUTOonline | 1 | Audatex España (Solera) |
| Datos estadísticos personalizados (a medida) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Datos integrados de DMS/ERP/CRM (postventa) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Datos oficiales DGT del vehículo / historial (INTEVES) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Datos técnicos (JATO) | 1 | coches.net |
| datos técnicos / ficha técnica del vehículo | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Datos técnicos del vehículo | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Datos telemáticos | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| datum_aankondiging_producent | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| datum_eerste_tenaamstelling_in_nederland | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| datum_eerste_toelating | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| datum_eigenaren_geinformeerd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| datum_informeren_eigenaar | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| datum_inschrijving_voertuig_in_nederland (OVI) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| datum_laatste_tenaamstelling (OVI) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| datum_melding_bij_rdw | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| datum_tenaamstelling | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Day & Night Rear View Mirror | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| day of week (dzien-tygodnia) [Statystyki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Days in stock / days to sale | 1 | Cox Automotive Europe |
| days listed / time on the forecourt | 1 | CarGurus |
| Days reduced for assignment | 1 | IAA (Insurance Auto Auctions) |
| Days-to-acquisition | 1 | ACV Auctions |
| Daytime Running Light (DRL) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| daytimeRunningLamps | 1 | mobile.de |
| dc_fast_charge_connector | 1 | Vehicle Databases |
| deal_badge (Great Deal / Good Deal / Fair Deal / Fair Price / Well-Equipped) | 1 | Cars Commerce (Cars.com Inc.) |
| deal_badge accuracy MdAPE (~4%) | 1 | Cars Commerce (Cars.com Inc.) |
| deal_badge ML feature: seasonality | 1 | Cars Commerce (Cars.com Inc.) |
| deal score | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Deals: advertSaved flag | 1 | Auto Trader UK (Autotrader Group plc) |
| Deals: buyer preferences | 1 | Auto Trader UK (Autotrader Group plc) |
| Deals: dealIntentScore | 1 | Auto Trader UK (Autotrader Group plc) |
| Deals: intent | 1 | Auto Trader UK (Autotrader Group plc) |
| Deals: localCustomer flag | 1 | Auto Trader UK (Autotrader Group plc) |
| Deals: reservation status & fee | 1 | Auto Trader UK (Autotrader Group plc) |
| dealScore (numeric deal score) | 1 | CarGurus |
| DealShield Buyer's Adjustment fee | 1 | Manheim |
| DealShield eligibility (<=20yr, <$100k, <250k mi; excl. TMU/TRA/salvage/branded) | 1 | Manheim |
| DealShield for-any-reason return | 1 | Manheim |
| DealShield: garantía devolución 21 días / 500 millas (reembolso total incl. fees) | 1 | Cox Automotive |
| DealShield refund (100% guaranteed amount + buy-fee) | 1 | Manheim |
| DealShield return window (21 days) | 1 | Manheim |
| DealShield Select (actualizaciones de inventario cualificado) | 1 | Cox Automotive |
| decision makers (per company) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| declaration_valant_saisie_DVS_date | 1 | HistoVec |
| declaration_valant_saisie_nom_autorite | 1 | HistoVec |
| Decode Accuracy ('Decodes Correctly') | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Decode de matrícula (plate) | 1 | autobiz (autobiz Group) |
| decoder_car_specifications | 1 | Stat.vin (1VIN STAT) |
| Decoder: factory equipment | 1 | autoDNA |
| decoder_included_features | 1 | Stat.vin (1VIN STAT) |
| decoder_manufacturer | 1 | Stat.vin (1VIN STAT) |
| decoder_plant_of_production | 1 | Stat.vin (1VIN STAT) |
| Deductible | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| defection / losses | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| defection alert (CRM / API notification) | 1 | Urban Science |
| defections (to competitor) | 1 | Urban Science |
| Defectos de pintura (mm) | 1 | Cox Automotive Europe |
| defectos destacados en pagina 1 (瑕疵明示) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| defects / condition (ML signal) | 1 | Motorway |
| defleet timing | 1 | INDICATA (Autorola Group) |
| Delinquency indicator | 1 | Black Book (National Auto Research — Hearst) |
| delivery_auction_fees | 1 | Stat.vin (1VIN STAT) |
| delivery_charges | 1 | MarketCheck (MarketCheck Cars Inc) |
| delivery_customs_documents | 1 | Stat.vin (1VIN STAT) |
| delivery_destination_port | 1 | Stat.vin (1VIN STAT) |
| Delivery fees financiados | 1 | Cox Automotive Europe |
| delivery_logistics_charges | 1 | Stat.vin (1VIN STAT) |
| delivery_lot_price | 1 | Stat.vin (1VIN STAT) |
| delivery_port_charges | 1 | Stat.vin (1VIN STAT) |
| deliveryCharges | 1 | Edmunds |
| deliveryDate | 1 | mobile.de |
| deliveryPeriod | 1 | mobile.de |
| Delta accessori di serie per allestimento | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| delve.benchmarking | 1 | AutoGrab |
| delve.pricing_sales_trend | 1 | AutoGrab |
| delve.time_to_sell | 1 | AutoGrab |
| demographics | 1 | Urban Science |
| demontagedatum | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Denominación comercial / Tipo (homologación) | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Denominazione ufficiale del veicolo | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Denuncia de fraude del anuncio (fraudReport) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Deposit | 1 | Cox Automotive Europe |
| deposit amount | 1 | JATO Dynamics |
| deposito de puja en subasta (auction deposit) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Deprezzamento | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Derecho de tanteo / right of first refusal (Guaranteed) | 1 | autobiz (autobiz Group) |
| Derivado / especificacion | 1 | Cox Automotive Europe |
| DERIVADO: agrupacion 'Monitor and repair if necessary' (minor+advisory) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| DERIVADO: agrupacion 'Repair immediately' (dangerous+major) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| derivativeId | 1 | Auto Trader UK (Autotrader Group plc) |
| [EQUIP·Seguridad] Desactivación de airbag del pasajero delantero | 1 | km77.com |
| Descripción de operación | 1 | Audatex España (Solera) |
| Descripción de operación de pintura (P. sustitución/reparación) | 1 | Audatex España (Solera) |
| Descripcion de ruedas y neumaticos | 1 | Cox Automotive Europe |
| description | 1 | mobile.de |
| Descrizione connettore (EV) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| DescrizioneAllestimento | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizioneCasa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizioneComplessa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizioneCompleta | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizioneEstesa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizioneModalitaRicarica | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizioneMotivazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizionePiano | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizioneRT | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizioneTipoBatterie | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DescrizioneTipoPresa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| descuento aplicado (已减X万) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Descuento M.O. (%) | 1 | Audatex España (Solera) |
| Descuento medio aplicado | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Descuento oficial | 1 | km77.com |
| Descuento sobre total M.O. (cód 33) | 1 | Audatex España (Solera) |
| Descuento sobre total M.O. pintura (cód 59) | 1 | Audatex España (Solera) |
| Descuento sobre total sin IVA (cód 88) | 1 | Audatex España (Solera) |
| designChange | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| designChangeReason | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| despacho de aduanas | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| destination | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| destination_charge / destination fee | 1 | DataOne Software (DataOne, LLC) |
| destination_fee | 1 | TrueCar |
| Destination Market | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| destinationCharge | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Destrucción de vehículo | 1 | REPUVE — Registro Público Vehicular |
| Desviacion objetivo vs oportunidad real | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| detailed_history_comments | 1 | Stat.vin (1VIN STAT) |
| detailed_history_date | 1 | Stat.vin (1VIN STAT) |
| detailed_history_event_comment_description | 1 | CARFAX |
| Detailed History event: data source | 1 | Experian Automotive (AutoCheck) |
| detailed_history_event_type | 1 | Stat.vin (1VIN STAT) |
| Detailed History event: type/description | 1 | Experian Automotive (AutoCheck) |
| detailed_history_source | 1 | Stat.vin (1VIN STAT) |
| detailed_history_source_of_record | 1 | CARFAX |
| Detailed narrative condition descriptions | 1 | ACV Auctions |
| detailUrl (AutoUncle page) | 1 | AutoUncle |
| detalle técnico del vehículo | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| detección automática de opcionales | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| [EQUIP·Varios] Detección de alcohol (ADS) | 1 | km77.com |
| detección de daños por IA fotográfica (piezas dañadas) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| detección de fraude | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Detected OBD2 codes (escaneo BlueDriver / Bluetooth) | 1 | OPENLANE |
| [EQUIP·Seguridad] Detector de vehículos en ángulo muerto | 1 | km77.com |
| deterministic ad-exposure-to-sale match (first-party) | 1 | Urban Science |
| Devaluation code (Entwertungscode) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| devolucion sin motivo 7 dias (<=450km) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Diámetro de giro entre bordillos (m) | 1 | km77.com |
| Diagnosis system | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| diagnosisCar (es coche diagnosticado) | 1 | Encar (엔카닷컴 / Encar.com) |
| Diagnostics (codigos de averia, sin detalle publico) | 1 | GT Motive |
| Diagramas de taller / visualizacion grafica de piezas | 1 | Eurotax (JD Power / Autovista Group) |
| Diamètre braquage murs | 1 | La Centrale |
| Diamètre des jantes arrière | 1 | La Centrale |
| Diamètre des jantes avant | 1 | La Centrale |
| Dias que lleva anunciado cada vehiculo | 1 | Eurotax (JD Power / Autovista Group) |
| dictionary total record count (ilosc-rekordow-slownika) [Slowniki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| dictionary value key (klucz-slownika) [Slowniki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| diferencia en puntos porcentuales (dif. p.p.) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| DifferenzaKm | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DifferenzaPrezzo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Digital Buyer Protection: missing exterior equipment | 1 | Manheim |
| Digital Buyer Protection: unacceptable paintwork | 1 | Manheim |
| Digital Cluster | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Digital Cluster Size | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Digital Deal: appointment scheduling | 1 | CarGurus |
| Digital Deal: custom APR (no credit check) | 1 | CarGurus |
| Digital Deal F&I: GAP | 1 | CarGurus |
| Digital Deal F&I: Tire & Wheel | 1 | CarGurus |
| Digital Deal F&I: VSC (Vehicle Service Contract) | 1 | CarGurus |
| Digital Deal: hard-pull credit application (AutoFi; BoA/Chase/US Bank/Huntington/Exeter/Regional Acceptance/Santander/Truist/TD/Westlake/Wells Fargo/ACA +33 captive) | 1 | CarGurus |
| Digital Deal lead type: Appt – Digital Deal | 1 | CarGurus |
| Digital Deal lead type: Deposit – Digital Deal | 1 | CarGurus |
| Digital Deal lead type: Digital Deal (base, trade-in/F&I) | 1 | CarGurus |
| Digital Deal lead type: Hard Pull – Digital Deal | 1 | CarGurus |
| Digital Deal lead type: Soft Pull – Digital Deal | 1 | CarGurus |
| Digital Deal: lender routing by payment-to-income ratio + credit score threshold | 1 | CarGurus |
| Digital Deal: pre-qualification soft pull (GLS, Westlake, Capital One) | 1 | CarGurus |
| Digital Deal: reservation deposit ($500 via Stripe) | 1 | CarGurus |
| Digital Deal sale price: delivery fee | 1 | CarGurus |
| Digital Deal sale price: down payment | 1 | CarGurus |
| Digital Deal sale price: taxes (third-party tool by location + zip) | 1 | CarGurus |
| Digital paint depth readings (espesor de pintura) | 1 | OPENLANE |
| Digital Showroom website | 1 | ACV Auctions |
| Digital vehicle imagery (360 exterior + interior) | 1 | cap hpi (CAP + HPI, a Solera company) |
| dim. calidad del vehiculo (车辆质量) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| dim. coste de uso (使用成本) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| dim. experiencia de conduccion (驾乘感受) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| dimensión: canal | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| dimensión: periodo | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| dimensión: versión | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Diminished value (insurance) | 1 | Black Book (National Auto Research — Hearst) |
| Dirección a las cuatro ruedas | 1 | km77.com |
| Dirección: Asistencia variable con la velocidad | 1 | km77.com |
| [EQUIP·Seguridad] Dirección asistida | 1 | km77.com |
| Dirección: Desmultiplicación no lineal | 1 | km77.com |
| Dirección: Desmultiplicación variable con la velocidad | 1 | km77.com |
| Dirección fiscal del vehículo | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Dirección: Tipo | 1 | km77.com |
| Dirección: Tipo de asistencia | 1 | km77.com |
| direccion (地址) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Direct Offer (push notifications, +14% inquiries) | 1 | mobile.de |
| directInspected (진단 directo) | 1 | Encar (엔카닷컴 / Encar.com) |
| disc_front | 1 | Vehicle Databases |
| Discount | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| discount composition by category | 1 | JATO Dynamics |
| discount rate (transaction) | 1 | JATO Dynamics |
| Discounts (I/D, % o importe fijo) | 1 | GT Motive |
| dispersion (dispersión de mercado) | 1 | L'argus (Cote Argus®) |
| Disposal value forecast | 1 | cap hpi (CAP + HPI, a Solera company) |
| Disposal-to-auction | 1 | BCA (British Car Auctions) |
| Disposition / event (Crush / Parts / Retained / Salvage / Scrap / Sold / To Be Determined) | 1 | NMVTIS / VehicleHistory.gov |
| Disposition value: Crush | 1 | NMVTIS / VehicleHistory.gov |
| Disposition value: Parts | 1 | NMVTIS / VehicleHistory.gov |
| Disposition value: Retained | 1 | NMVTIS / VehicleHistory.gov |
| Disposition value: Scrap | 1 | NMVTIS / VehicleHistory.gov |
| Disposition value: Sold | 1 | NMVTIS / VehicleHistory.gov |
| Disposition value: To Be Determined (TBD) | 1 | NMVTIS / VehicleHistory.gov |
| Dispositivo / chip RFID (almacena el NCI; leíble por arco) | 1 | REPUVE — Registro Público Vehicular |
| DispositivoAntiInquinamento | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| DisposizioneCilindri | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| disqualification.reimposedDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| disqualification.removalDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| disqualification.startDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| disqualification.suspensionStatus | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| Disruptor Roundup (monthly disruptive themes) | 1 | GlobalData Automotive |
| dist | 1 | MarketCheck (MarketCheck Cars Inc) |
| distancia a la media UE (puntos) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Distribución de asientos | 1 | km77.com |
| Distribución de reparaciones por comunidad autónoma | 1 | Audatex España (Solera) |
| [EQUIP·Seguridad] Distribución electrónica de frenado (EBD) | 1 | km77.com |
| division | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| DMA dynamics (current + historical, down to dealer level) | 1 | Urban Science |
| DMS / lead-management integration (DealerWeb, enquiryMAX, Pinewood) | 1 | BCA (British Car Auctions) |
| DMS: Conversation history | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| DMS: Customer follow-ups (call/WhatsApp) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| DMS: Incoming leads | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| dms_sales_verification_required | 1 | TrueCar |
| DMS: Walk-in database | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| dmsReference | 1 | Autotelex B.V. |
| Documentation/Title fee | 1 | IAA (Insurance Auto Auctions) |
| DocumentoFirmato | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Documentos de servicio / historial (fotos) | 1 | AUTO1 Group |
| Documents / certificates (upload) | 1 | Autorola |
| Dollar Volume | 1 | CLASSIC.COM |
| dom | 1 | MarketCheck (MarketCheck Cars Inc) |
| dom_180 | 1 | MarketCheck (MarketCheck Cars Inc) |
| dom_active | 1 | MarketCheck (MarketCheck Cars Inc) |
| domestic (doméstico vs importado) | 1 | Encar (엔카닷컴 / Encar.com) |
| domestic_use_account | 1 | Stat.vin (1VIN STAT) |
| Door mirror glass + adjustment | 1 | BCA (British Car Auctions) |
| Door Skin Allowance (UK) | 1 | GT Motive |
| Door-to-door transport quote | 1 | IAA (Insurance Auto Auctions) |
| dos_active | 1 | MarketCheck (MarketCheck Cars Inc) |
| down payment | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| down_payment_input | 1 | TrueCar |
| down_payment_percentage | 1 | MarketCheck (MarketCheck Cars Inc) |
| Downside risk | 1 | RedBook |
| Drivability assessment | 1 | IAA (Insurance Auto Auctions) |
| drive_layout | 1 | carVertical |
| Drive Line Type | 1 | IAA (Insurance Auto Auctions) |
| drive_unit | 1 | Stat.vin (1VIN STAT) |
| drive-time analysis | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| driveby_soundlevel_db | 1 | AutoGrab |
| drivenWheels | 1 | Edmunds |
| Driver Airbag | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Driver Assist | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Driver Attention Warning (ADAS) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Driver Side (LHD/RHD) | 1 | CLASSIC.COM |
| driver.dateOfBirth | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| driver.firstNames | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| driver.gender | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| driver.surname | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| driveType (FWD/RWD/AWD/4WD/6x4/6x6/8x6/8x8) | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| driving_axle | 1 | AutoGrab |
| driving_habits_usage_intensity_periods | 1 | carVertical |
| Driving-school deduction (לימוד נהיגה) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| drivingLicenceNumber | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| drivingMode (chain/belt, motorbikes) | 1 | mobile.de |
| drivingWheels | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Dual pricing (doble precio) | 1 | Autotelex B.V. |
| Duplicate Title | 1 | Experian Automotive (AutoCheck) |
| Durée de la garantie (mois) | 1 | La Centrale |
| Durchschnittliche Standzeit Markt (avg market standing time, días) | 1 | AutoScout24 |
| duree_detention_proprietaire_actuel_annees | 1 | HistoVec |
| dvla_body_desc | 1 | AutoGrab |
| DVLA data integration | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| dvla_fuel_desc | 1 | AutoGrab |
| DVLA lookup: doors | 1 | cap hpi (CAP + HPI, a Solera company) |
| DVLA lookup: mass data | 1 | cap hpi (CAP + HPI, a Solera company) |
| DVLA lookup: seating | 1 | cap hpi (CAP + HPI, a Solera company) |
| dvla_manufacturer_desc | 1 | AutoGrab |
| DVLA vehicle check | 1 | Autovista Group |
| dvla_wheelplan | 1 | AutoGrab |
| dvlaId (PARCIAL, recien matriculados) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| DVSA data integration | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Dynamic Brake Support (DBS) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Dynamically updated pricing display | 1 | ACV Auctions |
| E-Auto Durchschnittspreis (avg EV price) | 1 | AutoScout24 |
| E-Auto Marktanteil VO (EV used-car market share) | 1 | AutoScout24 |
| E-Auto Preisaufschlag (EV price premium vs media) | 1 | AutoScout24 |
| e-bike bikeGearType | 1 | mobile.de |
| e-bike frameHeight | 1 | mobile.de |
| e-bike frameMaterial | 1 | mobile.de |
| e-bike frameShape | 1 | mobile.de |
| e-bike motorPosition | 1 | mobile.de |
| e-bike numberOfGears | 1 | mobile.de |
| e-bike wheelSize | 1 | mobile.de |
| e-mobility penetration rate | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Early Release Values (modelos sin historial usado) | 1 | J.D. Power Valuation Services |
| Editions available (by original cost) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Editorial comment on value movement (commentDate, comment) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Editorial Top 10 Lists | 1 | Kelley Blue Book |
| editorial vehicle overview/review text | 1 | DataOne Software (DataOne, LLC) |
| editorial.AutoBriefReview | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| editorial.AwardsAndAccolades | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| editorial.NewCarTestDriveReview | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| EdizioneQuotazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Edmunds Rating (0-10 composite) | 1 | Edmunds |
| Edmunds Suggested Price (new, ex-TMV New) | 1 | Edmunds |
| Edmunds value | 1 | MAX Digital (ACV MAX) |
| eerste_kleur | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| einddatum_gebrek | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Elect_Weighted | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Electric continuous torque 30min (Nm) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Electric continuous torque 60min (Nm) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Electric peak torque (Nm) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Electric vehicle plug type | 1 | RedBook |
| Electric window operation (per window NSF/NSR/OSF/OSR) | 1 | BCA (British Car Auctions) |
| Electrical score | 1 | Mahindra First Choice Wheels (MFCWL) |
| ElectricCons_City | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ElectricCons_Comb | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| electricHeatedSeats | 1 | mobile.de |
| ElectricRange_City | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ElectricRange_Comb | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| electricWindows | 1 | mobile.de |
| Electronic brake assistance | 1 | ClearVin |
| Electronic Brakeforce Distribution (EBD) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Electronic invoicing (total loss/reparado/especialista/inherited/retail) | 1 | GT Motive |
| Electronic parking aid | 1 | ClearVin |
| Electronic part-exchange appraisal (Appraisal App) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Electronic Vehicle Record (EVR) | 1 | VINCUE (DealerCue Automotive Corp.) |
| elektriciteitsverbruik_gewogen_gecombineerd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| elektriciteitsverbruik_volledig_elektrisch | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| elektrisch_verbruik_enkel_elektrisch_wltp | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| elektrisch_verbruik_extern_opladen_wltp | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| [EQUIP·Confort] Elevalunas eléctricos delanteros | 1 | km77.com |
| [EQUIP·Confort] Elevalunas eléctricos traseros | 1 | km77.com |
| eligibility flags (branded title/damage/mileage/age/exotic/non-drivable/no local interest) | 1 | CarOffer (a CarGurus company) |
| Eliminar constante de pintura CESVIMAP (cód 84) | 1 | Audatex España (Solera) |
| Email (header de auth) | 1 | Datium Insights |
| Email del taller | 1 | Audatex España (Solera) |
| [EQUIP·Varios] Embellecedores metálicos en umbrales de puertas | 1 | km77.com |
| EMI Amount (editable) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| emissie_deeltjes_type1_wltp | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| emissieklasse (emissiecode_omschrijving) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Empattement | 1 | La Centrale |
| empleo directo del sector (nº puestos) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| employee_ratings | 1 | Cars Commerce (Cars.com Inc.) |
| encarPassType / encarPassCategoryType | 1 | Encar (엔카닷컴 / Encar.com) |
| End of Production (EOP) date | 1 | GlobalData Automotive |
| End of Term value | 1 | Black Book (National Auto Research — Hearst) |
| end-of-sales / phase-out date | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| End-of-term value | 1 | RedBook |
| End-of-term value / settlement figure | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| endorsement.offenceCode | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| endorsement.offenceDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| endorsement.offenceLegalDescription | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| endorsement.penaltyPoints | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| endorsement.penaltyPointsExpiryDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| energie_type_carburant (P.3) | 1 | HistoVec |
| energy & technology trends (25-year) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Energy cost (EV) | 1 | Autovista Group |
| energy.code | 1 | L'argus (Cote Argus®) |
| energy.master-code | 1 | L'argus (Cote Argus®) |
| energy.master-name | 1 | L'argus (Cote Argus®) |
| energy.name | 1 | L'argus (Cote Argus®) |
| energylabel (etiqueta energética) | 1 | Autotelex B.V. |
| Enhanced Vehicles (icono) | 1 | Copart, Inc. |
| Enlace al anuncio original en portal | 1 | Eurotax (JD Power / Autovista Group) |
| enquiry.enquirer (first_name/last_name/email/mobile) | 1 | AutoGrab |
| enquiry.vehicle (make/model/badge/series/year) | 1 | AutoGrab |
| Enterprise Dashboard - day-wise query graph (14 dias) | 1 | Orange Book Value (OBV) |
| Enterprise Dashboard - queries last 15 days | 1 | Orange Book Value (OBV) |
| Enterprise Dashboard - queries last 30 days | 1 | Orange Book Value (OBV) |
| Enterprise Dashboard - reports downloaded (basic/premium) | 1 | Orange Book Value (OBV) |
| Enterprise Dashboard - subscription status | 1 | Orange Book Value (OBV) |
| Enterprise Dashboard - total queries lifetime | 1 | Orange Book Value (OBV) |
| Enterprise multi-rooftop appraisal status | 1 | vAuto |
| Entertainment (spec) | 1 | Copart, Inc. |
| Entertainment System | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Entidad de registro nautico | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Entidad federativa que registró el vehículo | 1 | REPUVE — Registro Público Vehicular |
| entitlement.categoryCode (A/B/C...) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| entitlement.categoryLegalDescription | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| entitlement.categoryType | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| entitlement.expiryDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| entitlement.fromDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| entitlement.restrictionCode | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| entitlement.restrictionDescription | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| entrada/down payment (首付) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| envío en formato impreso (logística postal) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| environmental_compliance_level | 1 | carVertical |
| Environmental fee | 1 | IAA (Insurance Auto Auctions) |
| epa_city | 1 | Vehicle Databases |
| epa_combined | 1 | Vehicle Databases |
| EPA Green Score - Air Pollution score | 1 | DataOne Software (DataOne, LLC) |
| EPA Green Score - Greenhouse Gas score | 1 | DataOne Software (DataOne, LLC) |
| epa_highway | 1 | Vehicle Databases |
| EPA SmartWay Elite status | 1 | DataOne Software (DataOne, LLC) |
| EPA SmartWay status | 1 | DataOne Software (DataOne, LLC) |
| equip_abs_esp_brake_systems | 1 | carVertical |
| equip_airbags | 1 | carVertical |
| equip_audio_radio_speakers | 1 | carVertical |
| equip_brakes_front | 1 | carVertical |
| equip_brakes_rear | 1 | carVertical |
| equip_climate_ac | 1 | carVertical |
| equip_cruise_control | 1 | carVertical |
| equip_headlamps_lighting | 1 | carVertical |
| equip_navigation_device | 1 | carVertical |
| equip_park_distance_control | 1 | carVertical |
| equip_steering_wheel | 1 | carVertical |
| equip_tires | 1 | carVertical |
| equip_trailer_hitch | 1 | carVertical |
| equip_wheels | 1 | carVertical |
| EquipaggiamentoEsclusione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| EquipaggiamentoInclusione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| EquipaggiamentoNormalizzato | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| EquipaggiamentoQualificante | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| EquipaggiamentoVincolo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Equipamento: Conforto e Outros Equipamentos | 1 | Standvirtual |
| Equipamento: Electrónica e Assistência à Condução | 1 | Standvirtual |
| Equipamento: Segurança | 1 | Standvirtual |
| Equipamento: Áudio e Multimédia (Bluetooth, Rádio, Porta USB, Sistema de navegação, Ecrã táctil) | 1 | Standvirtual |
| equipamiento | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Equipamiento / opciones (auto-importado vía DAT por VIN) | 1 | AUTO1 Group |
| Equipamiento: Confort y conveniencia (comfortAndConvenience) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Equipamiento de fábrica instalado | 1 | autobiz (autobiz Group) |
| Equipamiento de seguridad | 1 | Eurotax (JD Power / Autovista Group) |
| Equipamiento: Entretenimiento / Medios | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Equipamiento: Extras | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Equipamiento instalado de fabrica | 1 | Eurotax (JD Power / Autovista Group) |
| Equipamiento: Seguridad | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Equipamiento/features (por importancia) | 1 | Cox Automotive Europe |
| Equipment adjustment (per-feature, e.g. Heated Seats) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Equipment: airbag count | 1 | autoDNA |
| Equipment: audio system | 1 | autoDNA |
| Equipment catalogue | 1 | RedBook |
| Equipment: climate control / heating | 1 | autoDNA |
| Equipment code | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Equipment: electric windows / elevalunas | 1 | autoDNA |
| equipment_groups | 1 | Vehicle Databases |
| Equipment Information Source (VIN Decoder/VIN Query/Interface) | 1 | GT Motive |
| Equipment list — Entertainment | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Equipment list — Exterior | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Equipment list — Interior | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Equipment list — Mechanical | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Equipment list — Safety | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Equipment: mirrors / espejos | 1 | autoDNA |
| Equipment: navigation system / navegador | 1 | autoDNA |
| Equipment Plant Code (DOT) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Equipment text / short | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Equipment Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Equipment: window tint / lunas | 1 | autoDNA |
| equipment.availability (STANDARD/OPTIONAL/UNKNOWN) | 1 | Edmunds |
| equipment.name | 1 | L'argus (Cote Argus®) |
| equipment.price-excluding-vat | 1 | L'argus (Cote Argus®) |
| equipment.price-including-vat | 1 | L'argus (Cote Argus®) |
| Equipment/accessories detected list | 1 | J.D. Power Valuation Services |
| equipmentType (AUDIO_SYSTEM/COLOR/ENGINE/FEE/HOLDBACK/OPTION/TELEMATICS/TIRES/TRANSMISSION/WARRANTY/WHEELS) | 1 | Edmunds |
| equitable sales target | 1 | Urban Science |
| equity position | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| equity.equity_position | 1 | AutoGrab |
| equity.positive_equity | 1 | AutoGrab |
| EquivalentAllElectric | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| erkenning (tipo: APK/gas/tachograaf/export/demontage/bedrijfsvoorraad/handelaarskenteken/Kentekenloket...) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| error | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Error Code | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| [MED·Prueba] Error del cuentakilómetros (%) | 1 | km77.com |
| Error Text | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| error.code | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| error.detail | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| error.status | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| error.title | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| Ersatzwagenklasse (clase de vehiculo de sustitucion) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| escrow / garantia del pago (车款居间担保) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| EsitoGravami | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| esp | 1 | mobile.de |
| Especificaciones del vehículo (taxonomía JATO) | 1 | autobiz (autobiz Group) |
| Especificaciones EV granulares | 1 | Eurotax (JD Power / Autovista Group) |
| espejos eléctricos (electricMirrors) | 1 | Fasecolda — Guía de Valores |
| establishment address | 1 | Autotelex B.V. |
| establishment city | 1 | Autotelex B.V. |
| establishment email | 1 | Autotelex B.V. |
| establishment phoneNumber | 1 | Autotelex B.V. |
| establishment zipCode | 1 | Autotelex B.V. |
| establishmentId | 1 | Autotelex B.V. |
| establishmentName / name | 1 | Autotelex B.V. |
| Estadísticas avanzadas: favoritos por anuncio | 1 | coches.net |
| Estadísticas avanzadas: informe mensual de performance del anuncio | 1 | coches.net |
| Estadísticas avanzadas: llamadas por anuncio | 1 | coches.net |
| Estadísticas avanzadas: mensajes por anuncio | 1 | coches.net |
| Estadísticas avanzadas: visitas por anuncio | 1 | coches.net |
| estado (recorte regional) | 1 | Webmotors |
| Estado / UF (27 unidades federativas) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Estado actual y futuro del vehículo | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Estado de aseguramiento (seguro obligatorio SOA) | 1 | Dirección General de Tráfico (DGT) |
| Estado de auditoria | 1 | Cox Automotive Europe |
| Estado de batería (State of Health) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Estado de conservação | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| estado de la comunicación | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Estado de neumaticos | 1 | Cox Automotive Europe |
| Estado de titulo (title) | 1 | Cox Automotive Europe |
| Estado del movimiento | 1 | Cox Automotive Europe |
| Estado en watchlist (lista de seguimiento) | 1 | AUTO1 Group |
| Estado global semáforo (sin incidencias / con avisos / con incidencias) | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Estado: nuevo/ocasion/Km0/seminuevo/clasico/demo (condition) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| estado nuevo/usado (valueModel.estado) | 1 | Fasecolda — Guía de Valores |
| estado real del vehículo (dato conectado) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| estado recien listado (新上架/Newly listed) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Estado/condición del vehículo (opcional) | 1 | coches.net |
| Estado/condición técnica actual | 1 | Audatex España (Solera) |
| Estado/Situación (Avance/En avance) | 1 | Audatex España (Solera) |
| Estatus de inscripción (correcto proceso de inscripción) | 1 | REPUVE — Registro Público Vehicular |
| Esterni | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Estimación de reparación línea a línea | 1 | Audatex España (Solera) |
| [HERRAMIENTA] Estimación de valor del coche (¿cuánto vale tu coche?) | 1 | km77.com |
| Estimacion de piezas de desgaste | 1 | Eurotax (JD Power / Autovista Group) |
| Estimacion de punto unico (value, pricing_type=gp) | 1 | Accu-Trade (AccuTrade) |
| estimacion oficial/precio justo (官方估价) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Estimate line item (line-level) | 1 | CCC Intelligent Solutions |
| Estimate Number / Estimate Id | 1 | GT Motive |
| Estimated / potential retail margin (£) | 1 | Dealer Auction |
| estimated_annual_fuel_cost | 1 | Vehicle Databases |
| estimated APR | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Estimated fuel cost (12,000 miles/yr) | 1 | HPI Check (HPI Ltd, a Solera company) |
| estimated fuel costs | 1 | Auto Trader UK (Autotrader Group plc) |
| estimated_monthly_payment_lease | 1 | MarketCheck (MarketCheck Cars Inc) |
| estimated_monthly_payment_loan_calc | 1 | TrueCar |
| estimated pricing (VIN decode) | 1 | JATO Dynamics |
| estimated_retail | 1 | AutoGrab |
| Estimated Retail - Above | 1 | Cox Automotive |
| Estimated Retail - Average | 1 | Cox Automotive |
| Estimated Retail - Below | 1 | Cox Automotive |
| estimated sale price (instant RPM output) | 1 | Motorway |
| estimated_trade | 1 | AutoGrab |
| Estimated trade profit generated (£) | 1 | Dealer Auction |
| estimated_value_per_mode | 1 | carsales (carsales.com.au) |
| estimateTmv | 1 | Edmunds |
| eStock Card (ficha de stock electronica) | 1 | MAX Digital (ACV MAX) |
| Estrés de batería | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| estructura de antiguedad de flota (车龄结构) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| estudio de mercado a medida | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| estudio sectorial | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| ETAG code | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Etapa de ciclo de vida (factory order -> disposal) | 1 | Cox Automotive Europe |
| Etiqueta ambiental / distintivo DGT (emissionSticker) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Etiqueta de precio: Superprecio / Buen precio / ... / Caro (priceEvaluation) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Etiqueta/distintivo ambiental DGT | 1 | coches.net |
| Etiquetas de medioambiente UE/Umwelt (environmentEuDirective/Labels) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Euro NCAP (rating de seguridad) | 1 | Dirección General de Tráfico (DGT) |
| europese_uitvoeringcategorie_toevoeging | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| europese_voertuigcategorie | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| europese_voertuigcategorie_toevoeging | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Eurotax Blu (Compera / prezzo di acquisto dealer-trade-in) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Eurotax Giallo (Vendita / prezzo di vendita al privato) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| EV Drive Unit | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| EV forecast | 1 | Glass's |
| EV Index (base ene-2015=100) + YoY % | 1 | Cox Automotive |
| EV market forecast | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| EV market penetration (%) | 1 | CarNewsChina Data (China EV DataTracker) |
| EV market sizing | 1 | Autovista Group |
| EV pricing | 1 | Autovista Group |
| EV sales (by OEM & model) | 1 | Autovista Group |
| EV share (%) | 1 | Dealer Auction |
| EV share / trends | 1 | IAA (Insurance Auto Auctions) |
| EV share growth trajectory | 1 | GlobalData Automotive |
| EV specifications | 1 | DataOne Software (DataOne, LLC) |
| EV type (Mild Hybrid / BEV / FCEV; 8 electrification types) | 1 | GlobalData Automotive |
| EV vs ICE / fuel-type trend | 1 | INDICATA (Autorola Group) |
| ev.federalRebate | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| ev.stateRebate | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| ev.utilityRebate | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| eVA condition adjustment | 1 | Manheim UK |
| eVA consumer valuation widget / lead-gen (white-label) | 1 | Manheim UK |
| eVA future/forward value (hasta 6 meses por adelantado) | 1 | Manheim UK |
| eVA Insight: forecourt-vs-wholesale decision | 1 | Manheim UK |
| eVA LCV: racking and accessories | 1 | Manheim UK |
| eVA LCV: signwriting presence | 1 | Manheim UK |
| eVA LCV: usage and wear characteristics (tolerancia van) | 1 | Manheim UK |
| eVA part-exchange value | 1 | Manheim UK |
| eVA real-time valuation | 1 | Manheim UK |
| eVA rule-builder pricing adjustments | 1 | Manheim UK |
| eVA Self-Inspect: number of keys (input) | 1 | Manheim UK |
| eVA Self-Inspect: vehicle images (input) | 1 | Manheim UK |
| eVA UK: cobertura Cars + LCV | 1 | Cox Automotive |
| eVA UK: modos de captura (online/in-store/roadside/self-inspect) | 1 | Cox Automotive |
| eVA UK: Part-exchange value | 1 | Cox Automotive |
| eVA Underwrite: guaranteed purchase price (Cox compra, pago 24h) | 1 | Manheim UK |
| Evaluación de condición/calidad del vehículo | 1 | AUTO1 Group |
| Evaluacion de red paralela/competencia | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Evaluacion de riesgo (Basilea II) | 1 | Eurotax (JD Power / Autovista Group) |
| Evaluation date | 1 | Mahindra First Choice Wheels (MFCWL) |
| EVBH score 0-100 (salud de batería VIN-específica) | 1 | Cox Automotive |
| Event Data Recorder (EDR) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| event_date | 1 | Vehicle Databases |
| event_details | 1 | Vehicle Databases |
| Event end time | 1 | Mahindra First Choice Wheels (MFCWL) |
| Event start time | 1 | Mahindra First Choice Wheels (MFCWL) |
| eventDate (KADOE keeper-at-date-of-event) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| evento: baja | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| evento: transferencia | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| EVM-identified add/deducts (AVT) | 1 | Black Book (National Auto Research — Hearst) |
| evolución temporal del mercado | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| evox match flags (year/make/model/trim/body_type/cab_type/doors/drive_type) | 1 | DataOne Software (DataOne, LLC) |
| evox match VIF | 1 | DataOne Software (DataOne, LLC) |
| Evox VIF | 1 | DataOne Software (DataOne, LLC) |
| evpulse.retained_value_pct_movement | 1 | AutoGrab |
| exakte Ausstattung ab Werk (equipamiento exacto de fabrica) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Excess (franquicia) | 1 | GT Motive |
| Excess Wear and Tear (EWT) estimate (off-lease) | 1 | OPENLANE |
| Exchange value (valor de intercambio) | 1 | Orange Book Value (OBV) |
| executionTimeMS | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Exhaust leaks / secure | 1 | BCA (British Car Auctions) |
| Exit strategy (retail / wholesale / subprime) | 1 | Stockwave (vAuto · Cox Automotive) |
| Expansion de infraestructura de carga | 1 | Eurotax (JD Power / Autovista Group) |
| Expected costs (input) | 1 | Auto Trader UK (Autotrader Group plc) |
| Expected price indicator rating | 1 | Auto Trader UK (Autotrader Group plc) |
| Expected transaction timeframe (ready now / 2-6 meses / curious) | 1 | Accu-Trade (AccuTrade) |
| expectedDate | 1 | Autotelex B.V. |
| expectedPrice (=IMV reference) | 1 | CarGurus |
| expediente CAE | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Experian AutoCheck (vehicle history summary) | 1 | CCC Intelligent Solutions |
| Expert Overall Rating (0.0-5.0) | 1 | Kelley Blue Book |
| Expert rating: comfort | 1 | Kelley Blue Book |
| Expert rating: performance | 1 | Kelley Blue Book |
| Expert rating: quality | 1 | Kelley Blue Book |
| Expert rating: reliability | 1 | Kelley Blue Book |
| Expert rating: styling | 1 | Kelley Blue Book |
| Expert rating: value | 1 | Kelley Blue Book |
| Expert Review (editorial) | 1 | Kelley Blue Book |
| Expert Review Overall Rating | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Expert Reviews (pros/cons) | 1 | Orange Book Value (OBV) |
| expert_star_rating | 1 | TrueCar |
| Expert Sub-rating: Drive Experience | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Expert Sub-rating: Exterior | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Expert Sub-rating: Features | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Expert Sub-rating: Interior | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Expert Sub-rating: Safety | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Expert Verdict | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| expiryDate (mot test) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| Explication du prix (vs moyenne des véhicules similaires) | 1 | La Centrale |
| exploradoras/antiniebla SI/NO (explorersShow) | 1 | Fasecolda — Guía de Valores |
| ext_bidding_history | 1 | Stat.vin (1VIN STAT) |
| ext_etk_parts_catalog_numbers | 1 | Stat.vin (1VIN STAT) |
| ext_number_of_bids_iaai | 1 | Stat.vin (1VIN STAT) |
| ext_sales_history_models | 1 | Stat.vin (1VIN STAT) |
| ext_similar_lots_comparables | 1 | Stat.vin (1VIN STAT) |
| ext_technical_equipment | 1 | Stat.vin (1VIN STAT) |
| extended_data.vehicle_type_description | 1 | AutoGrab |
| Extended Guarantee: hasta 14 dias | 1 | OPENLANE |
| extendWarranty / deemedExtendWarranty (garantía extendida) | 1 | Encar (엔카닷컴 / Encar.com) |
| Exterior (spec) | 1 | Copart, Inc. |
| exterior_condition | 1 | Vehicle Databases |
| Exterior cosmetic defects (dents/scratches/chips/paint per panel) | 1 | BCA (British Car Auctions) |
| exterior_features | 1 | Vehicle Databases |
| exterior is_two_tone | 1 | DataOne Software (DataOne, LLC) |
| exterior_paint_description | 1 | Vehicle Databases |
| exterior photos x4 (45-degree corners, plate visible, doors closed) | 1 | Motorway |
| exterior primary_rgb_code (r,g,b) | 1 | DataOne Software (DataOne, LLC) |
| Exterior score (x/10) | 1 | Mahindra First Choice Wheels (MFCWL) |
| exterior secondary_rgb_code (r,g,b) | 1 | DataOne Software (DataOne, LLC) |
| external / manufacturer price contribution | 1 | JATO Dynamics |
| external_dms_id | 1 | AutoGrab |
| externalUrl (original seller listing) | 1 | AutoUncle |
| Extras/opcionales (JATO) | 1 | coches.net |
| Facelift / launch value-change effect | 1 | Autovista Group |
| facelift event | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Facelift information (national) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Facelift/launch uplift effect | 1 | Glass's |
| facility guideline adherence | 1 | Urban Science |
| facility type recommendation | 1 | Urban Science |
| Factory car warranty | 1 | ClearVin |
| Factory rebates (aplicados automaticamente) | 1 | vAuto |
| Factory upgrades itemizados con valor en dolares | 1 | MAX Digital (ACV MAX) |
| facturación del sector (€) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Fahrassistenzsysteme (sistemas ADAS) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Fahrzeugart (new/used/Jahreswagen/Vorführwagen) | 1 | AutoScout24 |
| Fahrzeugbewertung estimated value (consumer) | 1 | mobile.de |
| Fahrzeugzustand (condition, asumido bueno) | 1 | AutoScout24 |
| Fair cash-out value (total loss) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| fair_market_value_max | 1 | Vehicle Databases |
| fair_market_value_min | 1 | Vehicle Databases |
| Fair Purchase Price (CPO) | 1 | Kelley Blue Book |
| Fair value / valor de colateral (IFRS13, cartera) | 1 | autobiz (autobiz Group) |
| Family (model) | 1 | RedBook |
| FamilyId | 1 | RedBook |
| Farbcode (codigo de color/pintura) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| [EQUIP·Seguridad] Faros antiniebla | 1 | km77.com |
| [EQUIP·Seguridad] Faros LED | 1 | km77.com |
| Fases de pintura (paint stages) | 1 | Audatex España (Solera) |
| fast-moving vs slow-moving classification | 1 | INDICATA (Autorola Group) |
| 원동기 fault codes / 경고등 (motor: códigos de fallo, testigos) | 1 | Encar (엔카닷컴 / Encar.com) |
| favorite_shop | 1 | CARFAX |
| feature[] / excludeFeature[] (extended equipment set) | 1 | mobile.de |
| feature factoryCodes | 1 | Auto Trader UK (Autotrader Group plc) |
| feature genericName | 1 | Auto Trader UK (Autotrader Group plc) |
| feature name | 1 | DataOne Software (DataOne, LLC) |
| feature rarityRating | 1 | Auto Trader UK (Autotrader Group plc) |
| Feature Tour | 1 | IAA (Insurance Auto Auctions) |
| feature value | 1 | DataOne Software (DataOne, LLC) |
| feature valueRating | 1 | Auto Trader UK (Autotrader Group plc) |
| Feature-adjusted valuation | 1 | Auto Trader UK (Autotrader Group plc) |
| feature-category.name | 1 | L'argus (Cote Argus®) |
| feature.availability (série/option) | 1 | L'argus (Cote Argus®) |
| feature.description | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.featureKeyAnswers | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.id | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.installCause | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.isEVFeature | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.isHybridFeature | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.isStandard | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.key | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.nameNoBrand | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.price-excluding-vat | 1 | L'argus (Cote Argus®) |
| feature.price-including-vat | 1 | L'argus (Cote Argus®) |
| feature.rankingValue | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.sectionId | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.sectionName | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| feature.subSectionId | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Featured flag | 1 | CLASSIC.COM |
| features | 1 | MarketCheck (MarketCheck Cars Inc) |
| features_exterior | 1 | Vehicle Databases |
| features_interior | 1 | Vehicle Databases |
| Fecha de fabricacion (build date) | 1 | Eurotax (JD Power / Autovista Group) |
| Fecha de impresión | 1 | Audatex España (Solera) |
| Fecha de inscripción / registro | 1 | REPUVE — Registro Público Vehicular |
| Fecha de peritación | 1 | Audatex España (Solera) |
| Fecha de producción | 1 | autobiz (autobiz Group) |
| Fecha de tarifa (price list date) | 1 | Audatex España (Solera) |
| Fecha de trámite | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Fecha del trámite (FEC_TRAMITE) | 1 | Dirección General de Tráfico (DGT) |
| feed scope (dealer/zip/state/national) | 1 | DataOne Software (DataOne, LLC) |
| Fermo amministrativo (presenza) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| FermoAmministrativo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ffo.build_sheet_lines | 1 | AutoGrab |
| ffo.match_category | 1 | AutoGrab |
| ffo.match_score (0.6-1) | 1 | AutoGrab |
| ficha técnica / especificaciones | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| fifth_wheel_capacity_lb | 1 | Vehicle Databases |
| [EQUIP·Seguridad] Fijación ISOFIX en acompañante | 1 | km77.com |
| [EQUIP·Seguridad] Fijaciones ISOFIX traseras exteriores | 1 | km77.com |
| filtro Abaixo da FIPE | 1 | Webmotors |
| [EQUIP·Confort] Filtro de aire PM 2.5 | 1 | km77.com |
| [EQUIP·Confort] Filtro de habitáculo | 1 | km77.com |
| FiltroCarrozzeria | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Filtros de búsqueda + alertas / search requests guardadas | 1 | AUTO1 Group |
| Fin commercialisation | 1 | La Centrale |
| final de placa | 1 | Webmotors |
| final_drive_axle_ratio | 1 | Vehicle Databases |
| final sale price (highest accepted offer) | 1 | Motorway |
| Final sale price histórico (Sales Data) | 1 | Copart, Inc. |
| Financiación: simulación Santander integrada | 1 | Webmotors |
| Financing cost (total + Y1-Y5; APR 3.09%, 60mo, 10% down) | 1 | Kelley Blue Book |
| Finanzierungsquote / Leasingquote (cuota de financiacion/leasing) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| find_service_centers_verified_reviews | 1 | CARFAX |
| fine detail: where, when, and vehicle in which received (szczegoly mandatu) [Moj Pojazd] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| FineImmatricolazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| fines / mandates: paid vs unpaid (mandaty: oplacone/nieoplacone) [Moj Pojazd] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| FineVendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Finition | 1 | La Centrale |
| Firmatario | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| First & reverse test drive | 1 | BCA (British Car Auctions) |
| first_seen_at | 1 | MarketCheck (MarketCheck Cars Inc) |
| first_seen_at_date | 1 | MarketCheck (MarketCheck Cars Inc) |
| first_seen_at_mc | 1 | MarketCheck (MarketCheck Cars Inc) |
| first_seen_at_mc_date | 1 | MarketCheck (MarketCheck Cars Inc) |
| first_seen_at_source | 1 | MarketCheck (MarketCheck Cars Inc) |
| first_seen_at_source_date | 1 | MarketCheck (MarketCheck Cars Inc) |
| first_seen_date | 1 | MarketCheck (MarketCheck Cars Inc) |
| first_seen_vdp_url | 1 | MarketCheck (MarketCheck Cars Inc) |
| firstAdmissionDate / datum eerste toelating | 1 | Autotelex B.V. |
| firstUsedDate | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| Fiscalidad transfronteriza (cross-border taxation) | 1 | autobiz (autobiz Group) |
| fitment | 1 | Vehicle Databases |
| Fixed cost | 1 | Autovista Group |
| flag coche incendiado (火烧车) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| flag coche inundado (泡水车) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Flag de oportunidad de venta internacional (10-15% de vehículos) | 1 | autobiz (autobiz Group) |
| Flag minivolture (ultimo passaggio) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Flag: service actions (acciones de servicio) | 1 | autoDNA |
| Flag specialized (sin pricing AccuTrade) | 1 | Accu-Trade (AccuTrade) |
| FlagCategoria | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| FlagPack | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Flags de riesgo/coste | 1 | Cox Automotive Europe |
| FlagUfficiale | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| FlagVeicoloNuovo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| fleet composition | 1 | GlobalData Automotive |
| fleet netting (parent/subsidiary) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| fleet score per statistical district | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| fleet size (per company) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| fleet size class | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| fleet vehicle type (PC/LCV/HCV) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| fleetNumber | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| fleetOnly | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| FlgSerieOpzionale | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Flood Risk Check | 1 | AutoCheck (by Experian) |
| Floor price (reserva) | 1 | OPENLANE |
| Floorplan advance hasta 100% + floor planning fee + interes diario | 1 | ACV Auctions |
| Fluid costs | 1 | cap hpi (CAP + HPI, a Solera company) |
| Foldable Rear Seat | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Folio de Constancia de Inscripción (FCI, folio de lote/holograma) | 1 | REPUVE — Registro Público Vehicular |
| Follow Me Home Headlamps | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| follow-up / noncompliance correction plan | 1 | Urban Science |
| follow-up bid above reserve | 1 | CarOffer (a CarGurus company) |
| follow-up question interpretation | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| # For sale (live inventory count per market) | 1 | CLASSIC.COM |
| For You personalized recommendations (AI) | 1 | Manheim |
| forcedInduction | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Forecast / prognóstico de preço | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Forecast: adjustedForecastPricing.adjustedBy (Color/Grade/Odometer/Region) | 1 | Cox Automotive |
| Forecast: adjustedForecastPricing.wholesale (valor forecast ajustado) | 1 | Cox Automotive |
| Forecast clean/average/below by month (plusValues) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Forecast Curve (1-36 months) | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Forecast de subida/bajada de VR en el tiempo (grafico) | 1 | Eurotax (JD Power / Autovista Group) |
| Forecast: edition (fecha de publicación) | 1 | Cox Automotive |
| Forecast evidence / rationale (editorial) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Forecast: forecastDate (lunes de la edición) | 1 | Cox Automotive |
| Forecast: forecastedAverageGrade | 1 | Cox Automotive |
| Forecast: forecastedPricing (valor forecast sin ajustar) | 1 | Cox Automotive |
| forecast horizon 5 years (to ~2030-2031) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Forecast horizon up to 60 months / 5 years | 1 | cap hpi (CAP + HPI, a Solera company) |
| Forecast: horizonte hasta 106 semanas | 1 | Cox Automotive |
| Forecast input: current & historical retailer pricing | 1 | Auto Trader UK (Autotrader Group plc) |
| Forecast input: seasonal pricing trends | 1 | Auto Trader UK (Autotrader Group plc) |
| Forecast value | 1 | Glass's |
| Forecast value at contract start | 1 | Glass's |
| Forecast value-retention % (Residual Value Awards) | 1 | Canadian Black Book |
| forecast values per quarter / month | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| forecast vs reality gap | 1 | INDICATA (Autorola Group) |
| Forecast with RedBook pricing | 1 | RedBook |
| Forecast with user-defined price | 1 | RedBook |
| forecast.nextMonth.retail | 1 | Cox Automotive |
| forecast.nextMonth.wholesale | 1 | Cox Automotive |
| forecast.nextYear.retail | 1 | Cox Automotive |
| forecast.nextYear.wholesale | 1 | Cox Automotive |
| Forecasting / tendencias de mercado (Car Digital Track) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| foreign risk flag: scrapping (zlomowanie) [autoDNA] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| foreign risk flag: traffic ban / not admitted to traffic (zakaz ruchu / niedopuszczony do ruchu) [autoDNA] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| foreign risk flag: used as taxi (uzytkowanie jako taxi) [autoDNA] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| fork_rake_angle | 1 | Vehicle Databases |
| Form completion rate (65%+) | 1 | ACV Auctions |
| Formato de venta B2B (precio fijo/puja abierta/blind/sellada/one-by-one/agrupada) | 1 | autobiz (autobiz Group) |
| formulario técnico TRA050 | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Formularios de lead (leadsRange/galleryLeadForm) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| FormYear / 형식년도 (año-modelo) | 1 | Encar (엔카닷컴 / Encar.com) |
| Foto del veicolo (cattura e archiviazione) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Foto's (tasación ampliada) [A] | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Fotos (documentacion fotografica) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Fotos del coche (set guiado) | 1 | AUTO1 Group |
| Fotos del vehículo | 1 | autobiz (autobiz Group) |
| Fotos del vehiculo (vehicle_photos, additional_images, primary image) | 1 | Accu-Trade (AccuTrade) |
| fréquence-finition-dans-le-parc | 1 | L'argus (Cote Argus®) |
| Frais de remise en état attendus (expected-refurbishment-costs) | 1 | L'argus (Cote Argus®) |
| Frame / structural assessment (TrueFrame, siniestro) | 1 | ACV Auctions |
| Franchise value (channel-segmented retail) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Franchise vs independent sales comparison | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Franquicia (deducible) | 1 | Audatex España (Solera) |
| Fraud detection flags | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| fraud_flag_rate_evasion | 1 | CARFAX |
| Fraud flags | 1 | Experian Automotive (AutoCheck) |
| Free AutoCheck Report (Experian): AutoCheck Score | 1 | Cars Commerce (Cars.com Inc.) |
| free_carfax_report_link_per_listing | 1 | CARFAX |
| Free preview: data availability semaphore (que datos existen pre-pago) | 1 | autoDNA |
| free_reports_with_deposit | 1 | Stat.vin (1VIN STAT) |
| Freigabe (autorizacion/liberacion de reparacion) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| [EQUIP·Confort] Freno de estacionamiento automático | 1 | km77.com |
| Freno delantero (tipo) | 1 | km77.com |
| Freno trasero (tipo) | 1 | km77.com |
| Frenos - condición (brakes) | 1 | AUTO1 Group |
| frenos ABS SI/NO (absShow) | 1 | Fasecolda — Guía de Valores |
| frequencyId (1-9) | 1 | Edmunds |
| Frequently purchased complementary items (accesorios) | 1 | Orange Book Value (OBV) |
| front_brake_diameter | 1 | Vehicle Databases |
| front_head_room | 1 | Vehicle Databases |
| front_hip_room | 1 | Vehicle Databases |
| front_legroom | 1 | Vehicle Databases |
| front_seat_type | 1 | Vehicle Databases |
| front_shoulder_room | 1 | Vehicle Databases |
| Front Suspension | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| front_suspension_size | 1 | Vehicle Databases |
| front_suspension_type | 1 | Vehicle Databases |
| Front tire age (excellent/good/poor) | 1 | Accu-Trade (AccuTrade) |
| front_tire_order_code | 1 | Vehicle Databases |
| front_tire_pressure | 1 | Vehicle Databases |
| front_tire_size | 1 | Vehicle Databases |
| Front Tires condition | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| front_track | 1 | DataOne Software (DataOne, LLC) |
| Front track size | 1 | ClearVin |
| front_travel | 1 | Vehicle Databases |
| front_wheel_diameter | 1 | Vehicle Databases |
| Front-end gross (store historical, by MMT) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Front/rear suspension, steering & underframe [128] | 1 | BCA (British Car Auctions) |
| fuel & electricity cost (tax guide) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| fuel_capacity_litres | 1 | AutoGrab |
| fuel cards (per fleet) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| fuel_control | 1 | Vehicle Databases |
| fuel_cost_comparison | 1 | Vehicle Databases |
| Fuel Delivery/Fuel Injection Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| fuel_induction | 1 | DataOne Software (DataOne, LLC) |
| fuel_quality | 1 | DataOne Software (DataOne, LLC) |
| Fuel Tank Size | 1 | ClearVin |
| fuel-cell.fuel | 1 | L'argus (Cote Argus®) |
| fuel-cell.fuel-cell-type | 1 | L'argus (Cote Argus®) |
| fuel-cell.volume | 1 | L'argus (Cote Argus®) |
| Fuel-Tank Material | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Fuel-Tank Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| fuel-type / EV trends | 1 | Motorway |
| fuel-type category (BEV/FCV/HEV/ICE/MEV/Plug-in) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| fuel-type forecast (5 years) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Fuel-type RV benchmark (percentage-point difference) | 1 | Autovista Group |
| Fuel-type split (EV / PHEV / HEV %) | 1 | Dealer Auction |
| Fuel1 | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Fuel1_Comb | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Fuel2 | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Fuel2_Comb | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| fuelCapacity | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| fuelEconomy.city | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| fuelEconomy.hwy | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| fuelEconomy.unit | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| fuelEconomyNEDCCombinedMPG | 1 | Auto Trader UK (Autotrader Group plc) |
| fuelEconomyWLTPCombinedMPG | 1 | Auto Trader UK (Autotrader Group plc) |
| fuelType / brandstof | 1 | Autotelex B.V. |
| Full provenance check | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| fullServiceHistory | 1 | mobile.de |
| [EQUIP·Confort] Función Follow me home | 1 | km77.com |
| Funding request (Partner Finance link) | 1 | BCA (British Car Auctions) |
| FunzionamentoElettricoPuro | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Fuoristrada | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Future / contract-end value (up to 5 years) | 1 | Autovista Group |
| Future / projected values | 1 | HPI Check (HPI Ltd, a Solera company) |
| Future resale price (predictor) | 1 | Orange Book Value (OBV) |
| future RV curve | 1 | INDICATA (Autorola Group) |
| future vehicle specifications (4000+ vehicles) | 1 | GlobalData Automotive |
| Future/forecast value (1-72 month projections) | 1 | Canadian Black Book |
| Future/Trended forecast +30 days (~1% accuracy) | 1 | Auto Trader UK (Autotrader Group plc) |
| Future/Trended forecast +60 days | 1 | Auto Trader UK (Autotrader Group plc) |
| Future/Trended forecast +90 days (~3% to 3 months) | 1 | Auto Trader UK (Autotrader Group plc) |
| Future/Trended forecast up to 6 months (~5%) | 1 | Auto Trader UK (Autotrader Group plc) |
| Génération | 1 | La Centrale |
| gage_date | 1 | HistoVec |
| gage_nom_creancier | 1 | HistoVec |
| Galeria 25+ fotos (min 25-26) | 1 | OPENLANE |
| galeria de fotos | 1 | Webmotors |
| Galves Market Ready Value (wholesale reacondicionado/auction-ready) | 1 | Accu-Trade (AccuTrade) |
| Galves value | 1 | Stockwave (vAuto · Cox Automotive) |
| Garantía | 1 | coches.net |
| Garantia (warranty) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Garantie (mois) | 1 | La Centrale |
| Garantie constructeur (km) | 1 | La Centrale |
| Gas system LPG/GPM addition (מערכת גפ"מ) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Gas tank capacity + unit | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| gasinstallatie_tank_inhoud | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| [HERRAMIENTA] Gasto anual estimado del coche (calculadora) | 1 | km77.com |
| Gasto en medios / baskets por medio (JorecaAdvertisers) | 1 | autobiz (autobiz Group) |
| Gastos de transferencia | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Gastos operativos | 1 | Eurotax (JD Power / Autovista Group) |
| gauge.confidence | 1 | AutoGrab |
| gauge.fill (0-1) | 1 | AutoGrab |
| gauge.sample_size | 1 | AutoGrab |
| gauge.vehicle_title | 1 | AutoGrab |
| gcwr | 1 | Vehicle Databases |
| GDV-Schnittstelle (insurer interface) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| gear_ratios | 1 | Vehicle Databases |
| Gear Shift Indicator | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| gears | 1 | DataOne Software (DataOne, LLC) |
| Gebrauchtwagengarantie (used-car warranty flag) | 1 | AutoScout24 |
| gebrek_artikel_nummer | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| gebrek_identificatie | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| gebrek_omschrijving (defecto) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| gebrek_paragraaf_nummer | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Gegarandeerd bod (Autoverkoopservice; media de pujas reales comparables) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| geluidsniveau_rijdend | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| geluidsniveau_stationair | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| gemiddelde_lading_waarde | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| generation | 1 | Auto Trader UK (Autotrader Group plc) |
| generation.body-type | 1 | L'argus (Cote Argus®) |
| generation.body-type-classified-ad | 1 | L'argus (Cote Argus®) |
| generation.full-nicename | 1 | L'argus (Cote Argus®) |
| generation.name | 1 | L'argus (Cote Argus®) |
| generation.position | 1 | L'argus (Cote Argus®) |
| generation.short-nicename | 1 | L'argus (Cote Argus®) |
| Generica_custom | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Generica_hard | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Generica_medium | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Generica_soft | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| genre_national (J.1) | 1 | HistoVec |
| geremde_as_indicator | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| geremde_rupsband_indicator | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Gesamtreparaturkosten (coste total de reparacion) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Gesamtschaden (valoracion total del dano) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| geschaetzte Wertminderung (estimated depreciation) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| gestión de contratos (alta / uso / devolución / remarketing) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| gestión multietapa del proceso de rellamada | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| gevelnaam | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| giorni_in_vendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| GiorniRotazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| GiorniVendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Glance (evaluacion rapida de potencial) | 1 | vAuto |
| Glass condition | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Glass Condition adjustment | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| glass_repairs (CA) | 1 | CARFAX |
| Glasses Code (NVIC valido) | 1 | Datium Insights |
| Global NCAP Child Safety Rating | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Global NCAP Safety Rating | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Global Search (~1M vehiculos, 7 canales de sourcing) | 1 | vAuto |
| Glove Box | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Glow plug warning light | 1 | BCA (British Car Auctions) |
| Go-to-market strategy [RV driver] | 1 | Autovista Group |
| Golf-Index (VW Golf price index desde 2017, 5 países) | 1 | AutoScout24 |
| Good Price / Great Price badge | 1 | Kelley Blue Book |
| Google Performance Max reach (YouTube/Gmail/Google) | 1 | mobile.de |
| Google/Alexa Connectivity | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| government incentive programmes | 1 | JATO Dynamics |
| GPS + timestamp | 1 | Mahindra First Choice Wheels (MFCWL) |
| grado de condicion S/A/B/C/D (export auction grade) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Grado de semejanza (Estrella exacta/Verde/Amarillo/Rojo) | 1 | Eurotax (JD Power / Autovista Group) |
| Grado NAMA car (1/2/3/4/5/U) | 1 | Cox Automotive Europe |
| Grado NAMA LCV | 1 | Cox Automotive Europe |
| Granular EV specifications and prices | 1 | Glass's |
| Graphic part mapping (click-to-price) | 1 | Glass's |
| Gravámenes (liens) | 1 | REPUVE — Registro Público Vehicular |
| Green Star / Greenhouse Rating | 1 | RedBook |
| GreenType (eco N/Y) | 1 | Encar (엔카닷컴 / Encar.com) |
| Grid row (posición en yard) | 1 | Copart, Inc. |
| Gross margin | 1 | ACV Auctions |
| gross_margin_metric | 1 | TrueCar |
| Gross per copy / gross per unit | 1 | VINCUE (DealerCue Automotive Corp.) |
| Gross profit retail estimado (path retail) | 1 | Accu-Trade (AccuTrade) |
| Gross profit tracking / ROI | 1 | Accu-Trade (AccuTrade) |
| Gross profit wholesale estimado (path liquidacion) | 1 | Accu-Trade (AccuTrade) |
| Gross Return % on ACV | 1 | IAA (Insurance Auto Auctions) |
| gross_trainweight_kg | 1 | AutoGrab |
| gross_vehicleweight_kg | 1 | AutoGrab |
| grossVehicleWeightKG | 1 | Auto Trader UK (Autotrader Group plc) |
| Ground Clearance Unladen | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Group average prices | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Group code | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Group stock management | 1 | BCA (British Car Auctions) |
| group-level performance | 1 | Urban Science |
| group-level reports | 1 | CarOffer (a CarGurus company) |
| growth brands (by market share and volume) | 1 | Urban Science |
| grupo de actualización (groupUpdate) | 1 | Fasecolda — Guía de Valores |
| GT Fusion: capa de transformacion foto/IA -> presupuesto | 1 | GT Motive |
| GT Fusion: deteccion de dano por IA (piezas danadas) | 1 | GT Motive |
| GT QCheck: confirmacion/correccion de referencia OE | 1 | GT Motive |
| GT QCheck: deteccion de parts leakage / duplicacion | 1 | GT Motive |
| GT QCheck: verificacion masiva de lista de piezas | 1 | GT Motive |
| [EQUIP·Equipaje] Guantera con iluminación | 1 | km77.com |
| Guarantee tier <$6.000 (engine noise, head gasket, transmission, transfer case, differential) | 1 | OPENLANE |
| Guarantee tier $6.001+ (rear main seal, frame damage, suspension, cosmetic, power accessories, climate control) | 1 | OPENLANE |
| Guaranteed First Bid / minimo garantizado (Manheim Upside) | 1 | vAuto |
| Guaranteed First Bid (GFB) floor = MMR | 1 | Manheim |
| guaranteed_savings_certificate_printable | 1 | TrueCar |
| Guaranteed Value (valor asegurado acordado, sin depreciacion) | 1 | Hagerty |
| GVW class (1-8) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Händlerbewertungen (dealer reviews) | 1 | AutoScout24 |
| Hagelschaden BVAT (dano de granizo segun norma) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Hagerty Hundred (100 Y/M/M mas populares asegurados, media condicion #2) | 1 | Hagerty |
| Hagerty Market Rating (indice 0-100) | 1 | Hagerty |
| Hallazgos de la prueba de conducción (test drive findings) | 1 | AUTO1 Group |
| Halogen Headlamps | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Handbrake / parking brake test | 1 | BCA (British Car Auctions) |
| handelsbenaming (denominacion comercial/modelo) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| handelsbenamingfabrikant | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Handelsspanne (margen comercial configurable) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Handelswaarde excl. IVA (tradevalueExcludingVAT) | 1 | Autotelex B.V. |
| Handlungsempfehlungen (recomendaciones IA accionables por coche) | 1 | AutoScout24 |
| harmonised multi-market RV view | 1 | INDICATA (Autorola Group) |
| has_keys | 1 | Vehicle Databases |
| has_secured_parties | 1 | AutoGrab |
| has_written_off_records | 1 | AutoGrab |
| has-map (mapa de dispersión geográfica) | 1 | L'argus (Cote Argus®) |
| Hauteur | 1 | La Centrale |
| HBV adjustment: vehicle use type (rental/fleet/personal) | 1 | CARFAX Canada |
| HBV adjustment: weekly adjusted market trends | 1 | CARFAX Canada |
| HBV redemption window: 14 days from purchase | 1 | CARFAX Canada |
| HBV refresh: every 7 days | 1 | CARFAX Canada |
| head_room | 1 | iSeeCars |
| head_room_front | 1 | DataOne Software (DataOne, LLC) |
| head_room_rear | 1 | DataOne Software (DataOne, LLC) |
| head_room_third_row | 1 | DataOne Software (DataOne, LLC) |
| heading | 1 | MarketCheck (MarketCheck Cars Inc) |
| Headlamp Light Source | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Headlights (high/low beam) | 1 | BCA (British Car Auctions) |
| headlightType | 1 | mobile.de |
| Headliner condition | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Headroom | 1 | ClearVin |
| heated_front_seats | 1 | Vehicle Databases |
| heated_seat | 1 | Vehicle Databases |
| Heated steering wheel | 1 | ClearVin |
| Heater | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| heavy commercial vehicles | 1 | GlobalData Automotive |
| hefas (eje elevable) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| heightMM | 1 | Auto Trader UK (Autotrader Group plc) |
| HGV / truck value | 1 | cap hpi (CAP + HPI, a Solera company) |
| High (extremo superior del rango) | 1 | ACV Auctions |
| High Bid | 1 | CLASSIC.COM |
| High risk / security marker (UK / One Auto API) | 1 | Experian Automotive (AutoCheck) |
| high_value_features | 1 | MarketCheck (MarketCheck Cars Inc) |
| High-resolution images / 360 | 1 | Manheim |
| High-risk vehicle alert (Security Watch) | 1 | cap hpi (CAP + HPI, a Solera company) |
| highest buy offer | 1 | CarOffer (a CarGurus company) |
| Highest volumers | 1 | Glass's |
| highest-bidder status notification | 1 | Motorway |
| Highest/High Authentic Value | 1 | VINCUE (DealerCue Automotive Corp.) |
| Highlights / puntos destacados | 1 | AUTO1 Group |
| Hill Assist | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| HIN (Hull Identification Number, marine) | 1 | RedBook |
| hip_room_front | 1 | DataOne Software (DataOne, LLC) |
| hip_room_rear | 1 | DataOne Software (DataOne, LLC) |
| hip_room_third_row | 1 | DataOne Software (DataOne, LLC) |
| Histórico de precio: bajada de precio (delta €, ej. - 1 000 EUR) | 1 | Standvirtual |
| Histórico de precio: Preço mais baixo (flag precio mínimo alcanzado) | 1 | Standvirtual |
| Histórico de precio: precio anterior (tachado, ej. 24 900 EUR) | 1 | Standvirtual |
| Historial de precios del anuncio (basic/extendedPriceHistoryLink) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Historial de servicio (service history) | 1 | Cox Automotive Europe |
| Historial de servicio/mantenimiento | 1 | Audatex España (Solera) |
| Historial tecnico del vehiculo | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Historial/provenance del vehiculo | 1 | Cox Automotive Europe |
| Historic Monitor (forecast) values | 1 | cap hpi (CAP + HPI, a Solera company) |
| Historic used values time series | 1 | cap hpi (CAP + HPI, a Solera company) |
| Historic valuation (retail/trade/part-ex, past date) | 1 | Auto Trader UK (Autotrader Group plc) |
| Historic valuation data | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Historic valuations up to 3 years (MVM) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Historical accuracy (published residual vs actual resale) | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Historical advert data (price/spec/description) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Historical averages | 1 | Manheim |
| Historical performance insights (IntelliSeller) | 1 | Copart, Inc. |
| Historical price — value at a past date (מחיר היסטורי / ארכיון) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| historical_prices | 1 | carVertical |
| Historical title issue date | 1 | ClearVin |
| Historical title state | 1 | ClearVin |
| Historical values | 1 | J.D. Power Valuation Services |
| historical_vehicle_photos | 1 | carVertical |
| historicalAverages.last30Days (precio + odómetro) | 1 | Cox Automotive |
| historicalAverages.lastMonth | 1 | Cox Automotive |
| historicalAverages.lastSixMonths | 1 | Cox Automotive |
| historicalAverages.lastTwoMonths | 1 | Cox Automotive |
| historicalAverages.lastYear | 1 | Cox Automotive |
| Historico de especificaciones 20 anos | 1 | Eurotax (JD Power / Autovista Group) |
| Historico de VR (hasta 4 anos) | 1 | Eurotax (JD Power / Autovista Group) |
| Historique Disponible (flag) | 1 | La Centrale |
| Historique du véhicule (filtre disponibilité) | 1 | La Centrale |
| historique_operation_date | 1 | HistoVec |
| historique_operation_date_annulation | 1 | HistoVec |
| historique_operation_type (vocabulaire ~120 types: immatriculation, changement de titulaire, cession, gage, OTCI, DVS, OVE, reparation controlee/DEC_VE, rapport d'expert, destruction, import, immobilisation, duplicata, perte titre, modif caracteristiques, sortie territoire...) | 1 | HistoVec |
| Historische nieuwprijs / consumentenprijs (requisito koerslijst BPM) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| History Adjusted Value (VIN-specific) | 1 | Black Book (National Auto Research — Hearst) |
| history_expert_reviews | 1 | carsales (carsales.com.au) |
| history_market_comparison_pricing | 1 | carsales (carsales.com.au) |
| History overview (contador de eventos por tipo) | 1 | autoDNA |
| history_pricing_guide_30day_autoupdate | 1 | carsales (carsales.com.au) |
| History reports (integrados) | 1 | MAX Digital (ACV MAX) |
| History-Adjusted value | 1 | Canadian Black Book |
| history.event.marketplace | 1 | AutoGrab |
| history.event.price | 1 | AutoGrab |
| history.event.timestamp | 1 | AutoGrab |
| history.event.type (listing/delisting/price_change) | 1 | AutoGrab |
| history.listing_sources | 1 | AutoGrab |
| history.listing_urls | 1 | AutoGrab |
| Holding cost | 1 | vAuto |
| Holding costs | 1 | Glass's |
| holding period (tenure) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Home Service: 7일 시승 (7 días de prueba en casa) | 1 | Encar (엔카닷컴 / Encar.com) |
| homeService flag (엔카홈서비스) | 1 | Encar (엔카닷컴 / Encar.com) |
| homologación / tipo de homologación | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| hoogte_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| hoogte_voertuig | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Horizonte de prevision (corto/medio/largo plazo) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Horn | 1 | BCA (British Car Auctions) |
| hotMark | 1 | Encar (엔카닷컴 / Encar.com) |
| household analytics | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| household demographics | 1 | Urban Science |
| HPG Average Value (condicion #3, todos los vehiculos) | 1 | Hagerty |
| HPG Median Value (condicion #3) | 1 | Hagerty |
| HSN (Herstellerschluesselnummer) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| httpStatusCode | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| HU/AU (fecha ITV/TÜV) | 1 | AutoScout24 |
| HUD抬头显示 | 1 | Autohome (汽车之家) |
| Huidige kilometerstand (input currentMileage) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Hybrid share (%) | 1 | Dealer Auction |
| Hybrid system torque | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Hypothecation | 1 | Mahindra First Choice Wheels (MFCWL) |
| IA: AutoGPT (asistente agéntico sobre ChatGPT; rollout PT pendiente) | 1 | Standvirtual |
| IA: Descrição Automática do Anúncio (ahorra ~5 min, -40% tiempo, 87% adopción) | 1 | Standvirtual |
| IA: Instant Ad (anuncio desde foto/vídeo) | 1 | Standvirtual |
| IA: Respostas Automáticas (24/7) | 1 | Standvirtual |
| IA: Vídeo Automático (vertical/Reels) | 1 | Standvirtual |
| IAA 360 View (interior+exterior spin+zoom) | 1 | IAA (Insurance Auto Auctions) |
| IAA High Resolution Images | 1 | IAA (Insurance Auto Auctions) |
| IAA Key Images | 1 | IAA (Insurance Auto Auctions) |
| IAA Vehicle Score (0-50) | 1 | IAA (Insurance Auto Auctions) |
| IBB reference/benchmark price | 1 | Mahindra First Choice Wheels (MFCWL) |
| ICV (Insured's Declared Value) | 1 | Audatex España (Solera) |
| ID Reach | 1 | Urban Science |
| iDEAL payment link / enlace de pago | 1 | Autotelex B.V. |
| Identical/comparable vehicles on the market today | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Identidad profesional del comprador (tax ID, grupo, postal, legal) | 1 | autobiz (autobiz Group) |
| Identificacion en un solo paso (VIN o matricula) | 1 | Eurotax (JD Power / Autovista Group) |
| idle_speed | 1 | Vehicle Databases |
| Ignition | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| iihs_safety_rating | 1 | CARFAX |
| Image background type (white / dealership) | 1 | RedBook |
| Image characteristics | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Image count | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Image downloads (high-quality, post-purchase) | 1 | BCA (British Car Auctions) |
| Image links | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Image overlays (badges/icons) | 1 | vAuto |
| Image thumbnail | 1 | Copart, Inc. |
| Image types A/B/C | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Image URL | 1 | Black Book (National Auto Research — Hearst) |
| image.url | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| imageAlt | 1 | AutoUncle |
| imageCount | 1 | mobile.de |
| imagenes (图片) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Imagenes/fotos del vehiculo | 1 | Cox Automotive Europe |
| Imagery: >=12 high-resolution exterior shots | 1 | Manheim UK |
| Imagery: 360-degree rotatable images | 1 | Manheim UK |
| Imagery: interior shots | 1 | Manheim UK |
| images / fotos | 1 | Autotelex B.V. |
| Images / videos (media library ChromeData) | 1 | J.D. Power Valuation Services |
| Images count (per listing) | 1 | Dealer Auction |
| Images high-res | 1 | Copart, Inc. |
| imageUrl | 1 | AutoUncle |
| ImmagineSvg | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ImmaginiRepertorio | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| immobilizer | 1 | mobile.de |
| Impago del IVTM | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Impound date | 1 | ClearVin |
| IMS syndication | 1 | CarOffer (a CarGurus company) |
| IMV input: vehicle history | 1 | CarGurus |
| imvPrice | 1 | CarGurus |
| in_transit | 1 | MarketCheck (MarketCheck Cars Inc) |
| in-group instant offer (point of appraisal) | 1 | CarOffer (a CarGurus company) |
| in-market incentive program | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| in-market status score | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| In-service date | 1 | AutoCheck (by Experian) |
| In-stock valuation | 1 | Auto Trader UK (Autotrader Group plc) |
| Inbound private-party leads | 1 | VINCUE (DealerCue Automotive Corp.) |
| Incentive: cash rebate | 1 | Edmunds |
| Incentive: lease special (monthly/term) | 1 | Edmunds |
| incentive level distribution (volume-weighted) | 1 | JATO Dynamics |
| Incentive spending | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Incentive structure [RV driver] | 1 | Autovista Group |
| incentive value / gift card / virtual card | 1 | Urban Science |
| incentive.cash | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.consumerCash | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.currentRetail | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.giveaways | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.lease | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.moneyFactors | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.paymentWaivers | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.residuals | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.retailIncentives | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.specialPrograms | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentive.subventedAPR | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| incentives | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Incentives / rebates / OEM rates (ChromeData Lender Desk, mapeados a zip) | 1 | J.D. Power Valuation Services |
| Incentivi comunali | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Incentivi del costruttore | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Incentivi statali | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Incidencia denegatoria | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| incidents | 1 | AutoGrab |
| increasesResidualValue (flag por opción/paquete: aumenta valor residual) | 1 | Autotelex B.V. |
| incremental unit sales (network action impact, +32% case) | 1 | Urban Science |
| Incremental Vehicle Sales % | 1 | Urban Science |
| incremental wholesale parts opportunity | 1 | Urban Science |
| Independent value (channel-segmented retail) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Index: 1950s American (19 americanos 50s) | 1 | Hagerty |
| Index: Affordable Classics (13 coches ~$40k 50s-70s) | 1 | Hagerty |
| Index: Blue Chip (25 coleccionables posguerra) | 1 | Hagerty |
| Index: British Car (10 deportivos britanicos 50s-70s) | 1 | Hagerty |
| Index: Ferrari (13 Ferraris de calle 50s-70s) | 1 | Hagerty |
| Index: Japanese Vehicle (19 japoneses 60s-2010s) | 1 | Hagerty |
| Index: Muscle Car (muscle cars raros/codiciados) | 1 | Hagerty |
| Index: Postwar German (21 BMW/Mercedes/Porsche 50s-70s) | 1 | Hagerty |
| Index: RADindex (21 vehiculos 80s-90s) | 1 | Hagerty |
| Index: Supercar (15 supercars/hypercars modernos) | 1 | Hagerty |
| Index: Truck & SUV (18 trucks/SUV 40s-90s) | 1 | Hagerty |
| Indicador de baja definitiva | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Indicador de baja temporal | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Indicador de barniz antirrayado | 1 | Audatex España (Solera) |
| Indicador de calidad de texto del anuncio | 1 | autobiz (autobiz Group) |
| Indicador de denegatoria | 1 | Dirección General de Tráfico (DGT) |
| Indicador de embargado (IND_EMBARGO) | 1 | Dirección General de Tráfico (DGT) |
| indicador de entorno/ambiental de vehículo autónomo y conectado (0-100) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| indicador de penetración de vehículo electrificado (0-100) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Indicador de precintado (IND_PRECINTO) | 1 | Dirección General de Tráfico (DGT) |
| indicador global de electromovilidad (0-100) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Indicador nuevo/usado (IND_NUEVO_USADO) | 1 | Dirección General de Tráfico (DGT) |
| Indicadores de calidad del anuncio (fotos presentes, alineación de precio, antigüedad de publicación) | 1 | autobiz (autobiz Group) |
| Indicadores de transacciones pasadas | 1 | autobiz (autobiz Group) |
| indicator_attr_badge | 1 | carsales (carsales.com.au) |
| indicator_attr_body | 1 | carsales (carsales.com.au) |
| indicator_attr_series | 1 | carsales (carsales.com.au) |
| indicator_exclusion_age_band_2y_15y | 1 | carsales (carsales.com.au) |
| indicator_exclusion_insufficient_data | 1 | carsales (carsales.com.au) |
| indicator_exclusion_price_band_5k_70k | 1 | carsales (carsales.com.au) |
| indicator_exclusion_written_off | 1 | carsales (carsales.com.au) |
| IndicatoreNazionalizzazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Indicators / hazard lights | 1 | BCA (British Car Auctions) |
| indice de recomendacion (推荐指数, escala 10) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Induction (aspirated/turbo) | 1 | RedBook |
| Industry: % loans at 0% APR | 1 | Edmunds |
| Industry: % shoppers $1,000+/mo payment | 1 | Edmunds |
| Industry: APR (avg new) | 1 | Edmunds |
| Industry: ATP used (1-yr, 3-yr) | 1 | Edmunds |
| Industry: Average loan amount | 1 | Edmunds |
| Industry: Average Transaction Price (ATP) new | 1 | Edmunds |
| Industry: Down payment (avg) | 1 | Edmunds |
| industry drivers | 1 | GlobalData Automotive |
| Industry: Incentives as % of ATP | 1 | Edmunds |
| Industry: Lease penetration | 1 | Edmunds |
| Industry: Loan term | 1 | Edmunds |
| Industry: Monthly payment (financed) | 1 | Edmunds |
| Industry: Negative equity | 1 | Edmunds |
| industry pulse (thought leaders) | 1 | GlobalData Automotive |
| Industry: SAAR / new vehicle sales forecast | 1 | Edmunds |
| inferred_sales_count_90d | 1 | MarketCheck (MarketCheck Cars Inc) |
| Inflated valuation detection | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| influence.body (efecto carrocería) | 1 | L'argus (Cote Argus®) |
| influence.professional-fees (frais professionnels) | 1 | L'argus (Cote Argus®) |
| influence.release (efecto antigüedad) | 1 | L'argus (Cote Argus®) |
| Informazioni su uso e destinazione d'uso | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Informe de tasación PDF | 1 | autobiz (autobiz Group) |
| informe de valoración customizable | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| informe de vehículos predefinido | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| infotainment features | 1 | JATO Dynamics |
| Infracciones | 1 | REPUVE — Registro Público Vehicular |
| ingangsdatum_gebrek | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Ingevulde kilometerstand | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| InizioImmatricolazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| InizioVendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Injury prediction (casualty AI) | 1 | CCC Intelligent Solutions |
| Input MMR: country (parámetro internacional) | 1 | Cox Automotive |
| Input MMR: date (histórica hasta 2018-11-01) | 1 | Cox Automotive |
| Input MMR: evbh | 1 | Cox Automotive |
| Input MMR: excludeBuild | 1 | Cox Automotive |
| Input MMR: extendedCoverage | 1 | Cox Automotive |
| Input MMR: include | 1 | Cox Automotive |
| Input MMR: orderBy | 1 | Cox Automotive |
| Input MMR: orgId | 1 | Cox Automotive |
| Input MMR: SUBSERIES | 1 | Cox Automotive |
| Input MMR: zipCode | 1 | Cox Automotive |
| inrichting (carroceria/uso) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Inruilen bij een autobedrijf | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Inserats-Analyse 60-day sale probability (Verkaufswahrscheinlichkeit, first 60 Standtage) | 1 | mobile.de |
| Inserats-Analyse Marktvergleich (similar competitor vehicles, up to ~100 attributes) | 1 | mobile.de |
| Inserats-Analyse next price-label delta (EUR to reach next category) | 1 | mobile.de |
| Inserats-Analyse performance metrics (views/emails/calls/parkings) | 1 | mobile.de |
| Inserats-Analyse search-results page | 1 | mobile.de |
| Inserats-Analyse search-results position (rank) | 1 | mobile.de |
| Inseratsqualität-Bewertung (listing quality score) | 1 | AutoScout24 |
| Insight: anomaly reporting (variance vs competitors) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Insight: company car performance | 1 | cap hpi (CAP + HPI, a Solera company) |
| Insight: leasing price lists | 1 | cap hpi (CAP + HPI, a Solera company) |
| Insight: position summary & threats | 1 | cap hpi (CAP + HPI, a Solera company) |
| Insight: tyre prices (NL) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Insight: van performance | 1 | cap hpi (CAP + HPI, a Solera company) |
| Insights abiertos (Diário Automóvel): precio medio / barómetros / tendencias VO (datos ACAP) | 1 | Standvirtual |
| Insights: affordability metrics | 1 | Cars Commerce (Cars.com Inc.) |
| Insights: hybrid_share | 1 | Cars Commerce (Cars.com Inc.) |
| Insights: New Car Pricing Index (NCPI = coste total compra+financiacion vs MSRP, %) | 1 | Cars Commerce (Cars.com Inc.) |
| Insights: new_days_on_lot | 1 | Cars Commerce (Cars.com Inc.) |
| Insights: new_vehicle_sales (SAAR, YoY) | 1 | Cars Commerce (Cars.com Inc.) |
| Insights: price_band_breakdown (<$20K, <$30K) | 1 | Cars Commerce (Cars.com Inc.) |
| Insights: used_days_on_lot / days_to_turn | 1 | Cars Commerce (Cars.com Inc.) |
| Insights: used_vehicle_sales | 1 | Cars Commerce (Cars.com Inc.) |
| Inspector notes / additional info | 1 | BCA (British Car Auctions) |
| Inspector/assessor | 1 | Mahindra First Choice Wheels (MFCWL) |
| Instalaciones por tipo de conector por pais | 1 | Eurotax (JD Power / Autovista Group) |
| install_type (factory/port/dealer) | 1 | DataOne Software (DataOne, LLC) |
| installationHeight (mm) | 1 | mobile.de |
| installed_equipment | 1 | MarketCheck (MarketCheck Cars Inc) |
| instant buy fee ($350) | 1 | CarOffer (a CarGurus company) |
| Instant consumer part-exchange valuation (Consumer Pro) | 1 | BCA (British Car Auctions) |
| instant_offer_adjustment_flag | 1 | carsales (carsales.com.au) |
| Instant Offer eligibility (<=2018, <$30k, CarMax <100mi) | 1 | Edmunds |
| instant_offer_input_state | 1 | carsales (carsales.com.au) |
| instant_offer_validity_7_days | 1 | carsales (carsales.com.au) |
| instant_offer_value | 1 | carsales (carsales.com.au) |
| inStockDate | 1 | Autotelex B.V. |
| Insured Declared Value IDV (InsuranceDekho) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Insured name | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Insurer contact | 1 | ClearVin |
| Insurer name | 1 | ClearVin |
| Integracion VHR (CarFax / AutoCheck / CarProof) | 1 | Accu-Trade (AccuTrade) |
| Intelligent recommendations (forecourt + bid-history based) | 1 | Dealer Auction |
| Intelligent review triage | 1 | GT Motive |
| Intención/estado del proyecto de reprise | 1 | autobiz (autobiz Group) |
| Intent / manipulation signals | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| intent signals (demanda shopper + oferta mercado, >10B/mes) | 1 | CarOffer (a CarGurus company) |
| intent-to-buy score | 1 | Urban Science |
| Inter-company transfers | 1 | ACV Auctions |
| inter-group transfer bill-of-sale | 1 | CarOffer (a CarGurus company) |
| Interactive map | 1 | MAX Digital (ACV MAX) |
| Intercooler | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| InteressiGiorniVendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Interior (spec) | 1 | Copart, Inc. |
| Interior cosmetic defects | 1 | BCA (British Car Auctions) |
| interior fabric_type / upholstery type | 1 | DataOne Software (DataOne, LLC) |
| Interior fittings & electrical controls [128] | 1 | BCA (British Car Auctions) |
| interior is_two_tone | 1 | DataOne Software (DataOne, LLC) |
| interior primary_rgb_code | 1 | DataOne Software (DataOne, LLC) |
| Interior score (x/10) | 1 | Mahindra First Choice Wheels (MFCWL) |
| interior secondary_rgb_code | 1 | DataOne Software (DataOne, LLC) |
| interior_volume | 1 | DataOne Software (DataOne, LLC) |
| Interior wear | 1 | Manheim |
| interiorType (leather/alcantara) | 1 | mobile.de |
| internalNumber | 1 | mobile.de |
| internalReference | 1 | Autotelex B.V. |
| Internet/online price - high valuation | 1 | cap hpi (CAP + HPI, a Solera company) |
| Internet/online price - low valuation | 1 | cap hpi (CAP + HPI, a Solera company) |
| Interni | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| InterrogazioniResidue | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| InterrogazioniTotali | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| IntervalloTagliando | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| intervalMonth | 1 | Edmunds |
| Intervalos de mantenimiento | 1 | Eurotax (JD Power / Autovista Group) |
| InterventiCarrozzeria | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| InterventiMeccanica | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Invasiones territoriales | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| InVendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Invernale | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| inversión en I+D del sector (€) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Inverter coolant level | 1 | BCA (British Car Auctions) |
| Invoerrechten (derechos de importación) | 1 | Autotelex B.V. |
| invoiceMax | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| invoiceMin | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Invoicing assignment (asignación de facturación) | 1 | Autotelex B.V. |
| [EQUIP·Confort] Ionizador de aire interior | 1 | km77.com |
| IoT projects (3200 / 100+ countries) | 1 | GlobalData Automotive |
| Ipoteche (presenza) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| IPT (imposta provinciale di trascrizione, per provincia) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| is_certified | 1 | MarketCheck (MarketCheck Cars Inc) |
| is_fuel_catalyst | 1 | AutoGrab |
| is_platform_shared | 1 | AutoGrab |
| is_searchable | 1 | MarketCheck (MarketCheck Cars Inc) |
| ISOFIX Child Seat Mounts | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| isOwnerPartner | 1 | Encar (엔카닷컴 / Encar.com) |
| issueNumber | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| Issues count / Good items count | 1 | Mahindra First Choice Wheels (MFCWL) |
| isVerifyOwner (propietario verificado) | 1 | Encar (엔카닷컴 / Encar.com) |
| ISWS presale listings search (run-lists) | 1 | Manheim |
| isYellow (matrícula amarilla/comercial) | 1 | Autotelex B.V. |
| Italian system code | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Item number | 1 | Copart, Inc. |
| ITS institute code (kod-instytutu-transportu-samochodowego) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| ivin_best_time_to_buy | 1 | iSeeCars |
| ivin_best_time_to_sell | 1 | iSeeCars |
| ivin_market_value_price_analysis (local fair market) | 1 | iSeeCars |
| ivin_selling_history (cambios de precio, anuncios previos) | 1 | iSeeCars |
| ivin_similar_cars_comparison (price/mileage/market value) | 1 | iSeeCars |
| ivin_vehicle_condition_analysis (avg miles vs edad) | 1 | iSeeCars |
| Izmo image mapping | 1 | DataOne Software (DataOne, LLC) |
| jaar_laatste_registratie_tellerstand | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| JATO ID (decode link id) | 1 | JATO Dynamics |
| JATO UID / Instance ID (global unique vehicle id) | 1 | JATO Dynamics |
| jatoVehicleId (mapeo a catálogo JATO Dynamics) | 1 | Encar (엔카닷컴 / Encar.com) |
| JavaScript Widget (multiples dimensiones) | 1 | Orange Book Value (OBV) |
| Job frequencies | 1 | cap hpi (CAP + HPI, a Solera company) |
| Job Status / Estimate Status (Calculated/Not Calculated/Open/Closed) | 1 | GT Motive |
| JSI record source / consolidator | 1 | NMVTIS / VehicleHistory.gov |
| JSI reporting entity type: Individual | 1 | NMVTIS / VehicleHistory.gov |
| JSI reporting entity type: Insurer | 1 | NMVTIS / VehicleHistory.gov |
| JSI reporting entity type: Recycler | 1 | NMVTIS / VehicleHistory.gov |
| JSI reporting entity type: Shredder | 1 | NMVTIS / VehicleHistory.gov |
| Kaufkraft / Zeit-bis-Kauf (purchasing power / time-to-buy regional) | 1 | AutoScout24 |
| kba HSN (Herstellerschlüsselnummer) | 1 | mobile.de |
| kba TSN (Typschlüsselnummer) | 1 | mobile.de |
| KBA-Schluessel (clave oficial HSN-TSN) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| KBB (Kelley Blue Book) ID mapping | 1 | DataOne Software (DataOne, LLC) |
| KBB Instant Cash Offer (ICO) | 1 | Stockwave (vAuto · Cox Automotive) |
| KBB Instant Cash Offer value | 1 | vAuto |
| KEINE ANGABE (estado sin label por pocos comparables) | 1 | AutoScout24 |
| Kelley Blue Book Car ID | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Kelley Blue Book (KBB) value | 1 | MAX Digital (ACV MAX) |
| Key (present) | 1 | IAA (Insurance Auto Auctions) |
| key competitors taking share | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| KeyLess Entry | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Keyless Ignition | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| keys | 1 | Vehicle Databases |
| Keys available (has keys) | 1 | Copart, Inc. |
| Keys condition | 1 | Mahindra First Choice Wheels (MFCWL) |
| keys_present | 1 | Stat.vin (1VIN STAT) |
| Kibbutz/institution deduction | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Kilómetros (ficha) | 1 | coches.net |
| [MED·Prueba] Kilómetros de la prueba (iniciales/finales) | 1 | km77.com |
| Kilómetros del vehículo (km) | 1 | coches.net |
| Kilométrage | 1 | La Centrale |
| Kilométrage Faible (flag) | 1 | La Centrale |
| kilométrage-standard (Essence 15000 / Diesel-Hybride 25000 / Electrique 12500 / Gaz-Hydrogène 20000 km/an) | 1 | L'argus (Cote Argus®) |
| kilowatt | 1 | AutoGrab |
| klasse_hybride_elektrisch_voertuig (OVC/NOVC-HEV/FCHV) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| klassifizierende Daten | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Konkurrenzpreise (competitor prices) | 1 | AutoScout24 |
| Kopen bij BOVAG autobedrijf met garantie | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| KPI de rendimiento de remarketing | 1 | autobiz (autobiz Group) |
| KPI eficiencia operativa | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| KPI estandarizado de postventa | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| KPI monitoring por tienda | 1 | vAuto |
| KPI objetivo 2030: 100% eléctrico en 2035 | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| KPI objetivo 2030: cuota de producción electrificada (>=40%) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| KPI objetivo 2030: empleo (1,9M) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| KPI objetivo 2030: inversión pública (€6.000M) y privada (~€40.000M) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| KPI objetivo 2030: producción (2,7M uds) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| KPI objetivo 2030: valor del sector (€120.000M) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| KPI overlay on map | 1 | Urban Science |
| KPI productividad | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| KPI rentabilidad | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| KPIs personalizables | 1 | autobiz (autobiz Group) |
| línea / referencia 1 (line1) | 1 | Fasecolda — Guía de Valores |
| Línea / versión [A] | 1 | REPUVE — Registro Público Vehicular |
| La Centrale Pro: filtres/alertes personnalisés | 1 | La Centrale |
| La Centrale Pro: inventaire B2B (opportunités de sourcing, ~50 000) | 1 | La Centrale |
| La Centrale Pro: messagerie intégrée (+WhatsApp) | 1 | La Centrale |
| laadvermogen | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Labor hours | 1 | CCC Intelligent Solutions |
| Labour category (Mechanics/Panel/Paint/Electrical/Trim) | 1 | GT Motive |
| Lackierung / Lackierungsaufwaende (pintura: DAT-Eurolack/AZT-Lack/fabricante) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Lackierungskosten (coste de pintura del dano) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| lado de conduccion LHD/RHD (rudder) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Lane Centering Assistance | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Lane Departure Warning (LDW) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Lane Keeping Assistance (LKA) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Lane monitor alert (Stockwave Plus) | 1 | Stockwave (vAuto · Cox Automotive) |
| Lane number | 1 | Manheim |
| Lane/Run | 1 | IAA (Insurance Auto Auctions) |
| language | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Largeur pneu arrière | 1 | La Centrale |
| Largeur pneu avant | 1 | La Centrale |
| Largeur sans rétros | 1 | La Centrale |
| LarghezzaMetri | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Last CPO (Certified Pre-Owned) Date | 1 | Experian Automotive (AutoCheck) |
| Last enquiries: check frequency | 1 | autoDNA |
| Last enquiries: check timestamps | 1 | autoDNA |
| Last enquiries: map | 1 | autoDNA |
| last_known_titling_state | 1 | CARFAX |
| last_seen_at | 1 | MarketCheck (MarketCheck Cars Inc) |
| last_seen_at_date | 1 | MarketCheck (MarketCheck Cars Inc) |
| last_seen_date | 1 | MarketCheck (MarketCheck Cars Inc) |
| last_seen_vdp_url | 1 | MarketCheck (MarketCheck Cars Inc) |
| Last Title Date | 1 | Experian Automotive (AutoCheck) |
| Last Title State | 1 | Experian Automotive (AutoCheck) |
| last_update_date (bulk) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| last_updated | 1 | Vehicle Databases |
| lastMotTestDate (bulk) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| Latitudine | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Laufzeit (plazo de pronostico, hasta 72 meses) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| LCV: accesorios | 1 | Cox Automotive Europe |
| LCV: condicion zona de carga (load area) | 1 | Cox Automotive Europe |
| LCV: estanterias/racking | 1 | Cox Automotive Europe |
| LCV load volume [PARCIAL] | 1 | JATO Dynamics |
| LCV payload [PARCIAL] | 1 | JATO Dynamics |
| LCV: rotulacion (signwriting) | 1 | Cox Automotive Europe |
| LCV value | 1 | cap hpi (CAP + HPI, a Solera company) |
| lead (LeadBox, CRM-synced: Dealer Desk / Auto-CRM / CATCH) | 1 | AutoUncle |
| lead capture (contact) | 1 | INDICATA (Autorola Group) |
| Lead contact (nome/cognome, email, telefono, azienda) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Lead: nombre, apellidos, teléfono, email, mensaje | 1 | autobiz (autobiz Group) |
| lead quality | 1 | Urban Science |
| Lead source / atribucion (cid, aff_cid, pag_id, vdp, partner_offer_id, origin_type) | 1 | Accu-Trade (AccuTrade) |
| lead_source_marketplace_affinity | 1 | TrueCar |
| lead source performance | 1 | Urban Science |
| Lead time (per order/gateway) | 1 | Autorola |
| Lead volume (del CRM / interes del consumidor) | 1 | MAX Digital (ACV MAX) |
| lead-potential forecast (impacto de cambio de precio) | 1 | CarOffer (a CarGurus company) |
| Leads (per day / by MMT / MTD leads) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Leads / Inquiries (listing analytics) | 1 | CLASSIC.COM |
| Leads de WhatsApp IA 24/7 (+20% incrementales / +55% conversion) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| leads_high_intent_buyer | 1 | TrueCar |
| Leads = oportunidad real de negocio (KPI B2B) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Lease amount remaining | 1 | Accu-Trade (AccuTrade) |
| lease_down_payment | 1 | MarketCheck (MarketCheck Cars Inc) |
| lease_emp | 1 | MarketCheck (MarketCheck Cars Inc) |
| Lease monthly payment | 1 | Accu-Trade (AccuTrade) |
| Lease number payments (meses restantes) | 1 | Accu-Trade (AccuTrade) |
| lease payment | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| lease_payment_estimate | 1 | TrueCar |
| lease_term | 1 | MarketCheck (MarketCheck Cars Inc) |
| leaseRentInfo (info leasing/rent) | 1 | Encar (엔카닷컴 / Encar.com) |
| leasing classification | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Leasing-financial deduction (ליסינג מימוני) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Leasing-operational deduction (ליסינג תפעולי) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Leather flag | 1 | Black Book (National Auto Research — Hearst) |
| Leather upholstery addition (ריפודי עור) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Leather Wrapped Steering Wheel | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Lebenszykluskurve (curva de ciclo de vida / depreciacion) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Lectura de arco RFID/LPR (paso del vehículo + alerta en tiempo real) | 1 | REPUVE — Registro Público Vehicular |
| Lecturas del cuentakilómetros (fecha) | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| LED DRLs | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| LED Fog Lamps | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| LED Headlamps | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| LED Taillights | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| leg_room | 1 | iSeeCars |
| leg_room_front | 1 | DataOne Software (DataOne, LLC) |
| leg_room_rear | 1 | DataOne Software (DataOne, LLC) |
| leg_room_third_row | 1 | DataOne Software (DataOne, LLC) |
| legacy_id | 1 | AutoGrab |
| Legislation / regulatory compliance data (WLTP/NEDC) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Legroom | 1 | ClearVin |
| Lender criteria | 1 | vAuto |
| Lender: Loan-to-Value (LTV) threshold input | 1 | AutoCheck (by Experian) |
| lender name | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Lender: value impact of negative events (30%+) | 1 | AutoCheck (by Experian) |
| lenderDesk.captiveVsNonCaptive | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| lenderDesk.cashProgram | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| lenderDesk.creditTiers | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| lenderDesk.fees | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| lenderDesk.leaseProgram | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| lenderDesk.lenderGuidelines | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| lenderDesk.loanProgram | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| lenderDesk.paymentQuote (loan/lease) | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| lenderDesk.terms | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Lending Value (wholesale/retail lender benchmark; B2B only) | 1 | Kelley Blue Book |
| lengte | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| lengte_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| lengthMM | 1 | Auto Trader UK (Autotrader Group plc) |
| lessor vehicle holding period | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Letter date | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Letter of guarantee | 1 | IAA (Insurance Auto Auctions) |
| Libro de mantenimiento completo si/no (hasFullServiceHistory) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| licence.validFrom | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| licence.validTo (expiry) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| licenceStatus (Valid) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| licenceType (Full/Provisional) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| License/circulation fee + renewal (אגרת רישוי וחידושה) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| licensedWeight (kg) | 1 | mobile.de |
| licensePlate / kenteken | 1 | Autotelex B.V. |
| Licensing group — private + commercial up to 4t (קבוצת רישוי) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Lidar (yes/no, filtro) | 1 | CarNewsChina Data (China EV DataTracker) |
| life stage | 1 | Urban Science |
| Lifecycle gateway status (arrival/handover/return/inspection/sales) | 1 | Autorola |
| Lifecycle stage (recon to retail) | 1 | VINCUE (DealerCue Automotive Corp.) |
| lifecycle timeline dates | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Lifecycle trend | 1 | cap hpi (CAP + HPI, a Solera company) |
| lifestyle | 1 | Urban Science |
| lifestyle gallery photo (shot_code/shot_name) | 1 | DataOne Software (DataOne, LLC) |
| liftingCapacity (kg, commercial) | 1 | mobile.de |
| light commercial vehicles (LCV) in operation | 1 | GlobalData Automotive |
| Lightbulbs (appraisal-like de un clic) | 1 | vAuto |
| Lights status | 1 | OPENLANE |
| Limitaciones de disposición | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| [EQUIP·Confort] Limpiaparabrisas automático | 1 | km77.com |
| Line-item work approval | 1 | vAuto |
| Lineas de daño con hasta 5 imagenes c/u | 1 | Cox Automotive Europe |
| link | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| link_active | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Link al Condition Report completo | 1 | OPENLANE |
| linked vehicles (RV de grupo enlazado) | 1 | Datium Insights |
| LinkStampaCertificata | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| LinkSVG | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| lista de equipamiento/configuracion (配置/equipment[]) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Lista de lenders para payoff (equity/lenders) | 1 | Accu-Trade (AccuTrade) |
| Listado de vehículos a nombre del solicitante | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Listing: 360-degree imagery | 1 | Manheim UK |
| listing_ancap_safety_rating | 1 | carsales (carsales.com.au) |
| Listing: CAP pricing intelligence (valor CAP, gratis) | 1 | Manheim UK |
| listing_compliance_date | 1 | carsales (carsales.com.au) |
| Listing condition (New/Used) | 1 | ClearVin |
| listing_confidence | 1 | MarketCheck (MarketCheck Cars Inc) |
| listing_date (Newest/Oldest listed) | 1 | Cars Commerce (Cars.com Inc.) |
| listing_doors | 1 | carsales (carsales.com.au) |
| listing_drive | 1 | carsales (carsales.com.au) |
| Listing: Glass's valuation data (gratis) | 1 | Manheim UK |
| Listing: high-resolution images | 1 | Manheim UK |
| Listing photo gallery (count) | 1 | ClearVin |
| listing_photos | 1 | CARFAX |
| Listing: sale lane / lot number | 1 | Manheim UK |
| Listing: save-search / stock alerts (24/7) | 1 | Manheim UK |
| listing_seats | 1 | carsales (carsales.com.au) |
| listing_series | 1 | carsales (carsales.com.au) |
| Listing status (For Sale / Sold / Not Sold / High Bid) | 1 | CLASSIC.COM |
| Listing URL / item URL | 1 | Copart, Inc. |
| Listing: vehicle appraisal data | 1 | Manheim UK |
| Listing: vehicle provenance information | 1 | Manheim UK |
| Listing/post date | 1 | ClearVin |
| live_auction | 1 | Stat.vin (1VIN STAT) |
| live_comparables / similar_cars_for_sale | 1 | AutoUncle |
| Live market data appraisal (trade-in) | 1 | ACV Auctions |
| Live market value (retail & trade) | 1 | Autorola |
| Live sale audio/video | 1 | BCA (British Car Auctions) |
| Live value movement count (6M between monthly publications) | 1 | cap hpi (CAP + HPI, a Solera company) |
| livemarket_annual_stock_turn | 1 | carsales (carsales.com.au) |
| livemarket_delisted_sold_data_12m | 1 | carsales (carsales.com.au) |
| livemarket_historical_pricing | 1 | carsales (carsales.com.au) |
| livemarket_last_delisted_price | 1 | carsales (carsales.com.au) |
| livemarket_listing_leads_enquiries | 1 | carsales (carsales.com.au) |
| livemarket_listing_views | 1 | carsales (carsales.com.au) |
| livemarket_market_benchmarking | 1 | carsales (carsales.com.au) |
| livemarket_realtime_pricing_vs_similar | 1 | carsales (carsales.com.au) |
| livemarket_stock_age | 1 | carsales (carsales.com.au) |
| livemarket_weekly_pricing_opportunities | 1 | carsales (carsales.com.au) |
| [EQUIP·Seguridad] Llamada de emergencia (eCall) | 1 | km77.com |
| Llamadas: origen y atencion (Call Tracking IA) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Llantas - condición (rims) | 1 | AUTO1 Group |
| [EQUIP·Llantas] Llantas de aleación (medida/acabado, p.ej. 19" 235/45 bicolor) | 1 | km77.com |
| [EQUIP·Confort] Llave digital | 1 | km77.com |
| loadCapacity (kg) | 1 | mobile.de |
| Loading capacity / Cargo volume | 1 | ClearVin |
| Loan payoff | 1 | Copart, Inc. |
| loan_record | 1 | Vehicle Databases |
| loan term | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| loan_term_input | 1 | TrueCar |
| loan-to-value (LTV) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Loan/Whole value (xclean/clean/avg/rough) | 1 | ClearVin |
| Local competitor insights | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| local consumer preference | 1 | Urban Science |
| local_market_report_by_zip (iVIN Pro) | 1 | iSeeCars |
| Local market trends | 1 | MAX Digital (ACV MAX) |
| Local vehicle insights | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| local/national composite benchmark | 1 | Urban Science |
| Localidad del domicilio del vehículo | 1 | Dirección General de Tráfico (DGT) |
| Localidad del vehículo | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Localisation (CP / ville / carte) | 1 | La Centrale |
| localização (cidade / estado) | 1 | Webmotors |
| Localización de daño por IA sobre foto (Qapter) | 1 | Audatex España (Solera) |
| Logística de retirada del vehículo (toda España) | 1 | Audatex España (Solera) |
| Logbook loan / inherited debt | 1 | cap hpi (CAP + HPI, a Solera company) |
| logbook loan check | 1 | Motorway |
| Logbook loan indicator | 1 | HPI Check (HPI Ltd, a Solera company) |
| Logistics / transport cost | 1 | VINCUE (DealerCue Automotive Corp.) |
| Logistics / vehicle movement | 1 | Mahindra First Choice Wheels (MFCWL) |
| Lohnkosten (coste de mano de obra) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Long order codes | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Long type name | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| longitud mm (long) | 1 | Fasecolda — Guía de Valores |
| [MED·Habitabilidad 2ª fila] Longitud/piernas (cm) | 1 | km77.com |
| Longitudine | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Longueur | 1 | La Centrale |
| Loss category ABI Cat A/B/S/N (UK/EU) | 1 | Copart, Inc. |
| Loss Date | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Loss forecast | 1 | Black Book (National Auto Research — Hearst) |
| Loss reserves | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Loss Vehicle | 1 | CCC Intelligent Solutions |
| losses (direct attribution) | 1 | Urban Science |
| Lot condition code | 1 | Copart, Inc. |
| Lot date / Listed date | 1 | CLASSIC.COM |
| lot_final_bid | 1 | Stat.vin (1VIN STAT) |
| lot_photos | 1 | Stat.vin (1VIN STAT) |
| lot_sale_datetime | 1 | Stat.vin (1VIN STAT) |
| lot_sale_document_title_code | 1 | Stat.vin (1VIN STAT) |
| lot_sold_status | 1 | Stat.vin (1VIN STAT) |
| lot_source_copart_iaai | 1 | Stat.vin (1VIN STAT) |
| LotVision bulk search (up to 300 vehicles) | 1 | Manheim |
| LotVision DTC Codes column (7,000+ generic SAE codes) | 1 | Manheim |
| LotVision DTC description + last-read timestamp | 1 | Manheim |
| LotVision search by Work Order number (post-purchase) | 1 | Manheim |
| LotVision Show My Position | 1 | Manheim |
| Low (extremo inferior del rango) | 1 | ACV Auctions |
| Lowest Sale | 1 | CLASSIC.COM |
| loyalty matrix | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| LTM (Last Twelve Months) window | 1 | CLASSIC.COM |
| LTV (loan-to-value) over time | 1 | Black Book (National Auto Research — Hearst) |
| lubrication_system | 1 | Vehicle Databases |
| [EQUIP·Confort] Luces automáticas | 1 | km77.com |
| [EQUIP·Decoración] Luces traseras LED | 1 | km77.com |
| Luggage / boot capacity | 1 | cap hpi (CAP + HPI, a Solera company) |
| lumbar_adjustment | 1 | Vehicle Databases |
| lumbar_support | 1 | Vehicle Databases |
| [EQUIP·Confort] Lunas tintadas | 1 | km77.com |
| [EQUIP·Confort] Lunas traseras sobretintadas | 1 | km77.com |
| [EQUIP·Seguridad] Luneta térmica | 1 | km77.com |
| LunghezzaMetri | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| luxury_features | 1 | TrueCar |
| [EQUIP·Confort] Luz anticharco | 1 | km77.com |
| [EQUIP·Confort] Luz de lectura delantera | 1 | km77.com |
| [EQUIP·Confort] Luz de lectura trasera | 1 | km77.com |
| [EQUIP·Seguridad] Luz diurna LED | 1 | km77.com |
| [EQUIP·Confort] Luz en los marcos de las puertas | 1 | km77.com |
| [EQUIP·Confort] Luz interior ambiental | 1 | km77.com |
| [EQUIP·Confort] Luz interior en zona de pies | 1 | km77.com |
| LV production volume (forecast) | 1 | GlobalData Automotive |
| Média anual de referência (variação 2024) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Mínimo (código opcional) | 1 | Audatex España (Solera) |
| Método de reparación óptimo (reparar vs sustituir) | 1 | Audatex España (Solera) |
| métricas de uso real para reporting ESG / CSRD | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Máximo (código opcional) | 1 | Audatex España (Solera) |
| M.O. pintura (UTS) | 1 | Audatex España (Solera) |
| m.Q average price (Durchschnittspreis) | 1 | mobile.de |
| m.Q average price change (YoY %) | 1 | mobile.de |
| m.Q average vehicle age (Durchschnittsalter) | 1 | mobile.de |
| m.Q car parc / fleet stock (Bestand der Pkw-Flotte, millions) | 1 | mobile.de |
| m.Q top searched equipment features (% e.g. Schiebedach/Standheizung/CarPlay) | 1 | mobile.de |
| m.Q top searched vehicle types (% Limousine/Kombi/SUV) | 1 | mobile.de |
| m.Q total listings (Inserate count) | 1 | mobile.de |
| Macro trend time series (since 2007) | 1 | CarNewsChina Data (China EV DataTracker) |
| Macro-categoria (CodMacroCategoria) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| macro-economic overlay | 1 | INDICATA (Autorola Group) |
| Macroeconomic factors | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| made_in | 1 | MarketCheck (MarketCheck Cars Inc) |
| Maintenance & Repairs (total + Y1-Y5) | 1 | Kelley Blue Book |
| maintenance codes | 1 | DataOne Software (DataOne, LLC) |
| maintenance_conditions_normal_severe | 1 | Vehicle Databases |
| maintenance_had_one_condition | 1 | Vehicle Databases |
| Maintenance interval | 1 | Autovista Group |
| Maintenance intervals (time) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| maintenance_menus | 1 | Vehicle Databases |
| Maintenance Minder items / services due | 1 | AutoCheck (by Experian) |
| maintenance_tracking_auto_store | 1 | CARFAX |
| maintenance_value | 1 | Vehicle Databases |
| maintenance_value_high | 1 | Vehicle Databases |
| maintenance_value_low | 1 | Vehicle Databases |
| maintenanceActionId | 1 | Edmunds |
| Maior valorização / maior desvalorização del mes | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Major bodyshop repair | 1 | BCA (British Car Auctions) |
| makeDescription (marca) | 1 | Datium Insights |
| MakeId | 1 | RedBook |
| MakeName | 1 | RedBook |
| [EQUIP·Equipaje] Maletero con iluminación | 1 | km77.com |
| Manage Offers | 1 | IAA (Insurance Auto Auctions) |
| Manager approval (aprobacion de oferta de trade) | 1 | MAX Digital (ACV MAX) |
| [EQUIP·Confort] Mando de apertura a distancia | 1 | km77.com |
| [EQUIP·Seguridad] Mandos multifunción en volante | 1 | km77.com |
| Manheim App: real-time notifications | 1 | Cox Automotive |
| Manheim App: Simulcast (puja en vivo) | 1 | Cox Automotive |
| Manheim Express: Guaranteed First Bid / Upside | 1 | Cox Automotive |
| Manheim Express/App: AutoCheck Snapshot (historial Experian) | 1 | Cox Automotive |
| Mantenimiento (registro electrónico de talleres) | 1 | Dirección General de Tráfico (DGT) |
| Manufacture date (fecha de fabricacion) | 1 | GT Motive |
| manufactureDate | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| Manufacturer Address/City/State/Country | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| manufacturer_code | 1 | MarketCheck (MarketCheck Cars Inc) |
| Manufacturer DBA/Trade Names | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Manufacturer Id | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| manufacturer_incentives | 1 | TrueCar |
| Manufacturer marketing message | 1 | Black Book (National Auto Research — Hearst) |
| manufacturer rebates | 1 | JATO Dynamics |
| Manufacturer specifications | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Manufacturer Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Manufacturer warranty status effect (אחריות יצרן) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| manufacturerCode | 1 | Edmunds |
| ManufacturerIdentificationCode | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| manufacturerName (fabricante de la opción) | 1 | Autotelex B.V. |
| manufacturerWarrantyCorrosionDurationYears | 1 | Auto Trader UK (Autotrader Group plc) |
| manufacturerWarrantyStandardDurationYears | 1 | Auto Trader UK (Autotrader Group plc) |
| manufactureYear (PARCIAL, recien matriculados) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| Manufacturing plant | 1 | ClearVin |
| Mapeo de red competitiva | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Marge de Manœuvre (leeway.percentage / leeway.value) | 1 | L'argus (Cote Argus®) |
| Marge/KPIs (margin per vehicle) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Margen VO vs VN | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Margin adjustment | 1 | RedBook |
| margin_gap_vs_hammer | 1 | MarketCheck (MarketCheck Cars Inc) |
| Margin protection | 1 | MAX Digital (ACV MAX) |
| Margin vs days-to-sale trade-off | 1 | MAX Digital (ACV MAX) |
| Marke (make) | 1 | AutoScout24 |
| Market | 1 | IAA (Insurance Auto Auctions) |
| Market activity tracking (by model/geography/dealer group) | 1 | Canadian Black Book |
| Market average / comparison to rest of market | 1 | MAX Digital (ACV MAX) |
| Market: average age (months) | 1 | Manheim UK |
| market_average_price_baseline | 1 | carsales (carsales.com.au) |
| Market: average sold price (wholesale) | 1 | Manheim UK |
| Market: buyer attendance per auction | 1 | Manheim UK |
| Market: CAP value movement / CAP performance (% vs CAP) | 1 | Manheim UK |
| market channel: Manufacturers (Car Manufacturer) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| market channel: Private Market | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| market channel: Short-Term Rental / Rent-a-car (RAC) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| market channel: True Fleet (genuine company fleet) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Market Driven Value (actual cash value / ACV) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Market fit (encaje con mercado local oferta/demanda) | 1 | Accu-Trade (AccuTrade) |
| Market: fuel-type split (petrol/diesel/hybrid/PHEV/BEV) | 1 | Manheim UK |
| Market growth forecast / CAGR | 1 | Mahindra First Choice Wheels (MFCWL) |
| Market Guide 2.0: forecast precio a 30 dias | 1 | OPENLANE |
| Market Guide 2.0: forecast precio a 60 dias | 1 | OPENLANE |
| Market Guide 2.0: forecast precio a 90 dias | 1 | OPENLANE |
| Market Guide: Average wholesale price | 1 | OPENLANE |
| Market Guide filtro: date sold | 1 | OPENLANE |
| Market Guide filtro: fuel | 1 | OPENLANE |
| Market Guide: Highest wholesale price | 1 | OPENLANE |
| Market Guide: historical lookback 30-180 dias (ajuste estacional) | 1 | OPENLANE |
| Market Guide: Lowest wholesale price | 1 | OPENLANE |
| Market health | 1 | Cox Automotive Europe |
| Market Health by vehicle age band (≤1y/1-3y/3-5y/5-10y/>10y) | 1 | mobile.de |
| Market Health Gesamtmarkt change (YoY %) | 1 | mobile.de |
| Market Health index value (supply Inserate / demand Leads, Ø=100) | 1 | mobile.de |
| Market Insight filter: age band | 1 | Auto Trader UK (Autotrader Group plc) |
| Market Insight Market Condition (supply vs demand) | 1 | Auto Trader UK (Autotrader Group plc) |
| market opportunity (quantified) | 1 | Urban Science |
| Market overview (vs whole retail market) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| market penetration | 1 | GlobalData Automotive |
| Market Rating: Auction Median Price of Cars Sold (12m) | 1 | Hagerty |
| Market Rating: Auction Overall Count of Cars Sold (media movil 12m) | 1 | Hagerty |
| Market Rating band (deflacionario <35 / plano 40-50 / peak 60-75 / burbuja >80) | 1 | Hagerty |
| Market Rating: Correlated Instrument - precio mediano de vivienda US | 1 | Hagerty |
| Market Rating: Correlated Instrument - precio spot del oro | 1 | Hagerty |
| Market Rating: Correlated Instrument - retail sales | 1 | Hagerty |
| Market Rating: Correlated Instrument - S&P 500 | 1 | Hagerty |
| Market Rating: Expert Opinion Market Survey (escala 1-100) | 1 | Hagerty |
| Market Rating: HPG Indices input (Hundred + Blue Chip, condicion #2) | 1 | Hagerty |
| Market Rating: Insured Values Broad Market ratio ($20k-$200k, sube vs baja) | 1 | Hagerty |
| Market Rating: Insured Values High End ratio (>$200k, sube vs baja) | 1 | Hagerty |
| Market Rating: Private Sales % Selling Above Insured Values | 1 | Hagerty |
| Market Rating: Private Sales Average Sales Price (12m) | 1 | Hagerty |
| Market: retail metrics (price/demand, granularidad parcial) | 1 | Manheim UK |
| market_sector_code | 1 | AutoGrab |
| market size | 1 | JATO Dynamics |
| Market strategy | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| market trend analysis | 1 | INDICATA (Autorola Group) |
| market_trends | 1 | AutoUncle |
| Market: used transaction volume forecast | 1 | Manheim UK |
| Market Value Assessor (combined current+retail+forecast value) | 1 | Autovista Group |
| Market value comparisons / comps | 1 | ACV Auctions |
| market_value_condition_average | 1 | Vehicle Databases |
| market_value_condition_clean | 1 | Vehicle Databases |
| market_value_condition_rough | 1 | Vehicle Databases |
| market_value_lower_bound | 1 | Cars Commerce (Cars.com Inc.) |
| Market Value of the vehicle (umbral siniestro total; no en todos los mercados) | 1 | GT Motive |
| market_value_upper_bound | 1 | Cars Commerce (Cars.com Inc.) |
| Market: wholesale market health index (escala 1-100; first of its kind) | 1 | Manheim UK |
| Market-backed total-loss valuation | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Market-Based factor: daily market data | 1 | CARFAX Canada |
| Market-Based factor: province | 1 | CARFAX Canada |
| Market-Based factor: seasonality | 1 | CARFAX Canada |
| Market-Based Value (point) | 1 | CARFAX Canada |
| marketcheck_price | 1 | MarketCheck (MarketCheck Cars Inc) |
| marketClass | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| marketing attribution (sales match to real transactions) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Marketing-Intensität Wettbewerber (competitor marketing/visibility products) | 1 | AutoScout24 |
| marketplace_image_url | 1 | AutoGrab |
| marketplace_price | 1 | AutoGrab |
| marketplace_price_type | 1 | AutoGrab |
| Marktanteile Handel (cuota freier/Marken/Privat) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Marktentwicklung (market development panel) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Marktpreis (market price calculado) | 1 | AutoScout24 |
| Marktwaarde (seguro = dagwaarde/Koerslijst + 10%) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Marktwert (market value B2C) | 1 | AutoScout24 |
| Masa máxima técnicamente admisible / MMTA | 1 | Dirección General de Tráfico (DGT) |
| Masa maxima autorizada / MMA (grossVehicleWeight) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| mass in running order (masa-pojazdu-gotowego-do-jazdy) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| massa_bedrijfsklaar_min_max | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| massa_ledig_voertuig | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| massa_rijklaar | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| MassaKG | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| massaledig_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| massarijklaar_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| MassaRimorchiabile | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| MassaTotaleBatterieKg | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Material de pintura (total) | 1 | Audatex España (Solera) |
| Materiales de pintura por superficie | 1 | Audatex España (Solera) |
| materiele_gevolgen | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| max bid (proxy) | 1 | Motorway |
| Max Margin recommendation | 1 | CarOffer (a CarGurus company) |
| max_offer.admin | 1 | AutoGrab |
| max_offer.lot | 1 | AutoGrab |
| max_offer.price | 1 | AutoGrab |
| max_offer.profit_margin | 1 | AutoGrab |
| max_offer.reconditioning | 1 | AutoGrab |
| max_offer.transport | 1 | AutoGrab |
| max_payload | 1 | DataOne Software (DataOne, LLC) |
| max_seating | 1 | DataOne Software (DataOne, LLC) |
| max_speed_kmh | 1 | AutoGrab |
| max_torque_at (rpm) | 1 | DataOne Software (DataOne, LLC) |
| max_towing_capacity | 1 | DataOne Software (DataOne, LLC) |
| max trailer gross mass with brake (max-masa-calkowita-przyczepy-z-hamulcem) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| max trailer gross mass without brake (max-masa-calkowita-ciagnietej-przyczepy-bez-hamulca) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Max Vehicle Severity | 1 | Experian Automotive (AutoCheck) |
| max_vermogen_15_minuten | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| maxconstructiesnelheid_ahw_ogr_bgr | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| maximale_constructiesnelheid | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Maximum / proxy bid | 1 | Dealer Auction |
| maximum axle load (maksymalny-nacisk-osi) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| maximum_last_onder_vooras_koppeling | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| maximum_massa_samenstelling | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| maximum_massa_trekken_ongeremd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| maximum_ondersteunende_snelheid | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| maximum payload (maksymalna-ladownosc) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| maximum_trekken_massa_geremd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| maximum wheel track (max-rozstaw-kol) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| maximummassa_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| maxondersteundesnelheid_ogr_bgr | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| maxverticalebelastopkopp_ogr_bgr | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| mc_category | 1 | MarketCheck (MarketCheck Cars Inc) |
| mc_rooftop_id | 1 | MarketCheck (MarketCheck Cars Inc) |
| mc_website_id | 1 | MarketCheck (MarketCheck Cars Inc) |
| mds | 1 | MarketCheck (MarketCheck Cars Inc) |
| Mechanical: AC | 1 | Accu-Trade (AccuTrade) |
| Mechanical: brakes | 1 | Accu-Trade (AccuTrade) |
| Mechanical breakdown repairs | 1 | GT Motive |
| Mechanical: catalytic converter | 1 | Accu-Trade (AccuTrade) |
| Mechanical condition | 1 | Mahindra First Choice Wheels (MFCWL) |
| Mechanical defects | 1 | Manheim |
| Mechanical: exhaust | 1 | Accu-Trade (AccuTrade) |
| Mechanical: head gasket | 1 | Accu-Trade (AccuTrade) |
| Mechanical: oil leak | 1 | Accu-Trade (AccuTrade) |
| Mechanical: other (+ mechanical_other_note) | 1 | Accu-Trade (AccuTrade) |
| Mechanical: sunroof/moonroof | 1 | Accu-Trade (AccuTrade) |
| Mechanical: suspension | 1 | Accu-Trade (AccuTrade) |
| Mechanical/technical condition | 1 | Autorola |
| Media | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Media CPM | 1 | Urban Science |
| Media Network: % buy within 6 months (81-83%) | 1 | Cars Commerce (Cars.com Inc.) |
| Media Network: % undecided what to buy (72-73%) | 1 | Cars Commerce (Cars.com Inc.) |
| Media Network: % undecided where to buy (88-90%) | 1 | Cars Commerce (Cars.com Inc.) |
| Media Network: impressions to high-intent shoppers | 1 | Cars Commerce (Cars.com Inc.) |
| Media Network: sales_influenced_by_Cars.com (+29%) | 1 | Cars Commerce (Cars.com Inc.) |
| Media Network: unique_monthly_in_market_shoppers (26-29M) | 1 | Cars Commerce (Cars.com Inc.) |
| Media Network: website_leads (2x) | 1 | Cars Commerce (Cars.com Inc.) |
| media UE de cada indicador de electromovilidad | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| mediaGallery.view.backgroundDescription | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| mediaGallery.view.shotCode | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| mediahouse_audience_buying_journey_stage | 1 | carsales (carsales.com.au) |
| mediahouse_audience_intent_based | 1 | carsales (carsales.com.au) |
| mediahouse_audience_socio_demographic_profiles | 1 | carsales (carsales.com.au) |
| mediahouse_carsales_capi_attribution | 1 | carsales (carsales.com.au) |
| mediahouse_carsales_id_people_targeting | 1 | carsales (carsales.com.au) |
| mediahouse_carsales_match_firstparty_lookalike | 1 | carsales (carsales.com.au) |
| Medias sectoriales anonimizadas | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| medida: cuota | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Medida de llanta delantera | 1 | km77.com |
| Medida de llanta trasera | 1 | km77.com |
| Medida de llanta/llanta de aleación | 1 | Audatex España (Solera) |
| Medida de neumáticos | 1 | Audatex España (Solera) |
| medida: unidades | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| medida: variación | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| medium commercial vehicles | 1 | GlobalData Automotive |
| Meeneemprijs (nombrada en intro; no etiquetada en el resultado del coche probado) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| meer_informatie_op_internet | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| meer_informatie_via_telefoonnummer | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Meetgo: 방문/배송 (visita/entrega trusted) | 1 | Encar (엔카닷컴 / Encar.com) |
| meetGo flag (엔카밋고) | 1 | Encar (엔카닷컴 / Encar.com) |
| mejor momento para vender (最佳卖车时机) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| meld_datum_door_keuringsinstantie | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| meld_tijd_door_keuringsinstantie | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| meldende_producent_distributeur | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| member_only_offers | 1 | TrueCar |
| Mensualité (€/mois) | 1 | La Centrale |
| Mercado relevante depurado por canales | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Mercato | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Merchandise Health score | 1 | CarOffer (a CarGurus company) |
| Merchandising performance | 1 | VINCUE (DealerCue Automotive Corp.) |
| merk_object_toegevoegd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| merkantiler Minderwert [NO-VERIFICADO] | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| merkcoderdw | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Merkzetteleinträge (watchlist entries) | 1 | AutoScout24 |
| mes de vigencia / actualización mensual del valor | 1 | Fasecolda — Guía de Valores |
| mes_referencia (ex.: 'abril de 2026') | 1 | FIPE (Tabela Fipe Veículos) |
| Mese | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| MeseImmatricolazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| MeseInfocar | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| MesePrevisione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| metallic | 1 | mobile.de |
| Method Of Delivery | 1 | RedBook |
| metodo de envio (Container / Ro-Ro) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| mfgCampaignNo | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| mfrModelCode (MMC) | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| MI dashboard (insights, trend monitoring, descarga de datos) | 1 | GT Motive |
| Microvetture | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Mietwagen-Preisindex / Mietwagenklasse | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Mietwagenklasse (clase de alquiler, 11 clases) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| miles | 1 | MarketCheck (MarketCheck Cars Inc) |
| Miles driven | 1 | IAA (Insurance Auto Auctions) |
| milieuklasse_eg_goedkeuring_licht | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| milieuklasse_eg_goedkeuring_zwaar | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| min_ground_clearance | 1 | Vehicle Databases |
| min_kerbweight_kg | 1 | AutoGrab |
| Min seats | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Minimum bid recommendation (IntelliSeller) | 1 | Copart, Inc. |
| Minimum transaction threshold (6/year + 2/90 days) | 1 | Manheim |
| minimum wheel track (min-rozstaw-kol) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Minimum wholesale guarantee (buy limit por adelantado) | 1 | MAX Digital (ACV MAX) |
| minimumKerbWeightKG | 1 | Auto Trader UK (Autotrader Group plc) |
| minimummassavoltooid | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| MiniVoltura | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Minor bodyshop repair | 1 | BCA (British Car Auctions) |
| Miscellaneous Adjustments (Minor Work) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| missing vehicle details flag | 1 | CarOffer (a CarGurus company) |
| missing/lost service traffic | 1 | Urban Science |
| Mitchell's repair pricing | 1 | OPENLANE |
| Mixture/feed system | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| MMR Licensed Data status | 1 | Manheim |
| MMR retention % | 1 | Cox Automotive |
| MMR retention rate (price-to-market) | 1 | Manheim |
| MMR Wholesale Average (Manheim Market Report) | 1 | Stockwave (vAuto · Cox Automotive) |
| mobile.de Marktpreis (computed market price) | 1 | mobile.de |
| mobileAdId | 1 | mobile.de |
| Mobility Trends: encuesta de comportamiento del consumidor (intención renting, combustible preferido, presupuesto €, antigüedad, km anuales, prestaciones) | 1 | coches.net |
| Mobility Trends: evolución anual del precio medio VO (%) | 1 | coches.net |
| Mobility Trends: evolución mensual del precio medio VO (€) | 1 | coches.net |
| Mod: aftermarket kit | 1 | Accu-Trade (AccuTrade) |
| Mod: catalytic converter | 1 | Accu-Trade (AccuTrade) |
| Mod: exhaust | 1 | Accu-Trade (AccuTrade) |
| Modèle | 1 | La Centrale |
| Modèle commercial | 1 | La Centrale |
| Mod: performance | 1 | Accu-Trade (AccuTrade) |
| Mod: spoiler | 1 | Accu-Trade (AccuTrade) |
| Mod: stereo | 1 | Accu-Trade (AccuTrade) |
| Mod: sunroof/moonroof | 1 | Accu-Trade (AccuTrade) |
| Mod: suspension lifted | 1 | Accu-Trade (AccuTrade) |
| Mod: suspension lowered | 1 | Accu-Trade (AccuTrade) |
| Mod: wheel | 1 | Accu-Trade (AccuTrade) |
| Modalita di pagamento | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Mode prix: Prix total / Leasing (LOA) | 1 | La Centrale |
| modele (marque + nom commercial) | 1 | HistoVec |
| modelFleet | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| ModelGroup / 모델그룹 (+ EnglishName) | 1 | Encar (엔카닷컴 / Encar.com) |
| modelID (Chrome YMMID) | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| modelName | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| modelRange | 1 | mobile.de |
| modelYear | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| modelYearId | 1 | Edmunds |
| Modification identification | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| modificationDate | 1 | mobile.de |
| modo_de_pesquisa (entrada: 'Pesquisa por Marca' | 'Pesquisa por Código Fipe') | 1 | FIPE (Tabela Fipe Veículos) |
| moeda_e_base (R$, pagamento à vista, consumidor final pessoa física, mercado nacional) | 1 | FIPE (Tabela Fipe Veículos) |
| mogelijk_gevaar | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| MoM change (%) | 1 | CarNewsChina Data (China EV DataTracker) |
| Moneda (priceCurrency) | 1 | coches.net |
| monetización CAE (≈1.000 €/turismo, vigente hasta 2030) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| money factor | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Monitoring Subscription layer: Monthly Vehicle History Report | 1 | CARFAX Canada |
| Monitorización de cumplimiento de políticas | 1 | Audatex España (Solera) |
| Monitorización de rendimiento de compradores (recon declarado vs IA) | 1 | autobiz (autobiz Group) |
| Monster Bid | 1 | Copart, Inc. |
| montagedatum (objeto incorporado) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Month-on-month change (£ and %) | 1 | BCA (British Car Auctions) |
| month-over-month change | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| monthly_average_value_12mo_history | 1 | iSeeCars |
| Monthly EV sales tracker | 1 | Autovista Group |
| Monthly Offers | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| monthly_payment_estimate (Est. $/mo) | 1 | Cars Commerce (Cars.com Inc.) |
| monthly payment view (by DMA) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| monthly repayment / payment | 1 | JATO Dynamics |
| Monthly sales units (per model) | 1 | CarNewsChina Data (China EV DataTracker) |
| Monthly static used car value | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| monthly value-change email alert | 1 | Motorway |
| more_information_link (lead) | 1 | Autotelex B.V. |
| Most desirable | 1 | Glass's |
| Most Recent Sale price | 1 | CLASSIC.COM |
| Motivo de baja (informe) | 1 | Dirección General de Tráfico (DGT) |
| Motivo de la baja | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Moto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Motorcycle / bike used value | 1 | cap hpi (CAP + HPI, a Solera company) |
| Motorcycle Chassis Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Motorcycle class fee | 1 | CCC Intelligent Solutions |
| motorcycle coverage | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Motorcycle Suspension Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Motorisierung (motorizacion) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| motorização (input tasador) | 1 | Webmotors |
| Motorización | 1 | Audatex España (Solera) |
| Motorway Move transport status (from GBP 99) | 1 | Motorway |
| Motorway Pay single-transfer payout (seller + finance provider + fees) | 1 | Motorway |
| motTest.completedDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| motTest.expiryDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| motTest.motTestNumber | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| motTest.testResult | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| motTestDueDate (primer MOT, recien matriculados) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| motTestNumber | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| motTests[] (array) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| mpge | 1 | Vehicle Databases |
| msa_code | 1 | MarketCheck (MarketCheck Cars Inc) |
| ミッション MT/AT/CAT (transmission) | 1 | USS (ユー・エス・エス) Co., Ltd. |
| multi-angle interior/exterior images | 1 | DataOne Software (DataOne, LLC) |
| Multi-out: retail potential | 1 | vAuto |
| Multi-out: subprime potential | 1 | vAuto |
| Multi-out: wholesale potential | 1 | vAuto |
| multilingual query support | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Multimarkenkonfigurator + Listenpreis (configurador VN multimarca + PVP) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Municipio de pago del IVTM | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Municipio IVTM (domicilio fiscal) | 1 | Dirección General de Tráfico (DGT) |
| Mutaciones diarias in/out de stock | 1 | Autotelex B.V. |
| MUVVI 20 market-class sub-indices | 1 | Manheim |
| MUVVI adjusted wholesale price (mix/mileage/seasonal) | 1 | Manheim |
| MUVVI ajuste de mix (media móvil 24 meses por market class) | 1 | Cox Automotive |
| MUVVI ajuste estacional (método Census Bureau / Census X) | 1 | Cox Automotive |
| MUVVI eliminación de outliers (2.6 desv. estándar en precio Y millas) | 1 | Cox Automotive |
| MUVVI EV index (Jan 2015=100) | 1 | Manheim |
| MUVVI mid-month reading | 1 | Manheim |
| MUVVI MoM % change | 1 | Cox Automotive |
| MUVVI MoM change | 1 | Manheim |
| MUVVI Non-EV index | 1 | Manheim |
| MUVVI precios no-ajustados YoY % | 1 | Cox Automotive |
| MUVVI unadjusted wholesale price | 1 | Manheim |
| MUVVI YoY % change | 1 | Cox Automotive |
| MUVVI YoY change | 1 | Manheim |
| MVM coverage (cars/LCV/bikes/HGV/imports) | 1 | cap hpi (CAP + HPI, a Solera company) |
| MVM PDF report | 1 | cap hpi (CAP + HPI, a Solera company) |
| Nº/código de operación de M.O. | 1 | Audatex España (Solera) |
| Nº de biedingen (pujas) — tendencia mensual | 1 | Autotelex B.V. |
| Nº de reparaciones (nacional/provincial) | 1 | Audatex España (Solera) |
| Nº de taxaties (tasaciones) — tendencia mensual | 1 | Autotelex B.V. |
| Nº de tipos de transacción disponibles (54) | 1 | Audatex España (Solera) |
| número de airbags (airbags) | 1 | Fasecolda — Guía de Valores |
| número de CAE (1 CAE = 1 kWh) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Número de Constancia de Inscripción (NCI, 8 alfanumérico, único) | 1 | REPUVE — Registro Público Vehicular |
| número de ejes (axles) | 1 | Fasecolda — Guía de Valores |
| número de fábricas (17 plantas) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Número de fotos por anuncio | 1 | autobiz (autobiz Group) |
| Número de Identificación Vehicular (NIV/VIN, 17 caracteres) | 1 | REPUVE — Registro Público Vehicular |
| Número de placa(s) / emplacamiento | 1 | REPUVE — Registro Público Vehicular |
| Número de pujas (number of bids) | 1 | AUTO1 Group |
| Número de serie (chasis) | 1 | REPUVE — Registro Público Vehicular |
| Número de vehículos a la venta (oferta de mercado) | 1 | autobiz (autobiz Group) |
| Número de visualizaciones (views, reporting al vendedor) | 1 | AUTO1 Group |
| Nº Póliza | 1 | Audatex España (Solera) |
| Nº Valoración | 1 | Audatex España (Solera) |
| naam_bedrijf (empresa erkend) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Nachfrageindikatoren (demand indicators) | 1 | AutoScout24 |
| nags_number | 1 | Vehicle Databases |
| NAMA: defectos visibles a 2m a 90 grados +/-45 | 1 | Manheim UK |
| NAMA: dent count & size por panel | 1 | Manheim UK |
| NAMA: exterior condition (cosmetico) | 1 | Manheim UK |
| NAMA: interior condition | 1 | Manheim UK |
| NAMA: paint defect count por panel/bumper | 1 | Manheim UK |
| NAMA: significant interior defects | 1 | Manheim UK |
| Name of individual/entity from whom automobile was obtained (solo law enforcement) | 1 | NMVTIS / VehicleHistory.gov |
| Name of individual/entity to whom title was issued (titleholder — solo law enforcement) | 1 | NMVTIS / VehicleHistory.gov |
| nameWoTrim | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| NatCode / Glass's code | 1 | Glass's |
| nationaal_opgegeven_aantal_voertuigen_terugroepactie | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| National market code | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| National Paint Adjustment (AZT) | 1 | GT Motive |
| nationalDelivery (radius/period/fee) | 1 | mobile.de |
| natural_disaster_event_date | 1 | carVertical |
| natural_disaster_exposure_flag | 1 | carVertical |
| natural_disaster_severity | 1 | carVertical |
| natural_disaster_type | 1 | carVertical |
| natural-language query (Ask Dataforce chat) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| [EQUIP·Multimedia] Navegador | 1 | km77.com |
| Navigation aid | 1 | ClearVin |
| Navigation flag | 1 | Black Book (National Auto Research — Hearst) |
| Navigation operation | 1 | OPENLANE |
| navigationSystem | 1 | mobile.de |
| ncap_adult_occupant_protection_percentage | 1 | AutoGrab |
| ncap_child_occupant_protection_percentage | 1 | AutoGrab |
| ncap_overall_rating | 1 | AutoGrab |
| ncap_pedestrian_protection_percentage | 1 | AutoGrab |
| ncap_safety_assist_percentage | 1 | AutoGrab |
| NCSA Map Exc Approved By | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| NCSA Map Exc Approved On | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| NCSA Mapping Exception | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| NCSA Note | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Índice: % depreciação / valorização (vista consumidor) | 1 | Webmotors |
| Índice: evolução do preço médio | 1 | Webmotors |
| Índice mercado: 구매 적기 (mejor momento de compra) | 1 | Encar (엔카닷컴 / Encar.com) |
| Índice mercado: EV 시세 방어 (resiliencia EV) | 1 | Encar (엔카닷컴 / Encar.com) |
| Índice mercado: 시세 변동 MoM % global | 1 | Encar (엔카닷컴 / Encar.com) |
| Índice mercado: 시세 변동 por origen (국산/수입) | 1 | Encar (엔카닷컴 / Encar.com) |
| Índice: recorte por Estado | 1 | Webmotors |
| Índice: recorte por quilometragem | 1 | Webmotors |
| Índice: variação % acumulada anual | 1 | Webmotors |
| Índice: variação % mensal | 1 | Webmotors |
| necesidades de mantenimiento | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| 续航 NEDC | 1 | Autohome (汽车之家) |
| NEDC figures (legacy) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Nederlandse handelsinkoopwaarde (requisito koerslijst BPM / derivable) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Negative equity indicator | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Negative equity transactions (YoY) | 1 | IAA (Insurance Auto Auctions) |
| Negative Score Factors | 1 | Experian Automotive (AutoCheck) |
| Énergie | 1 | La Centrale |
| Net Adjusted Market Value (settlement amount) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Net price / incl. all expenses (NP3) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Net returns | 1 | IAA (Insurance Auto Auctions) |
| net_torque | 1 | Vehicle Databases |
| netto_max_vermogen_elektrisch | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| nettomaximumvermogen (kW) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| netTorque | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| netTorque.rpm | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| network_avg_monthly_searches_88M | 1 | carsales (carsales.com.au) |
| network_avg_monthly_users_8_9M | 1 | carsales (carsales.com.au) |
| network_avg_monthly_video_views_10M | 1 | carsales (carsales.com.au) |
| network coverage | 1 | Urban Science |
| network coverage gaps | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| network financial health (OEM to dealer) | 1 | Urban Science |
| network health | 1 | Urban Science |
| network_members_count_15_2M_16M | 1 | carsales (carsales.com.au) |
| network profitability | 1 | INDICATA (Autorola Group) |
| Network type (open / closed) | 1 | Dealer Auction |
| network_user_signals_3_7B | 1 | carsales (carsales.com.au) |
| Neue Wettbewerber-Fahrzeuge (new competitor listings, live) | 1 | AutoScout24 |
| Neuf uniquement (filtre) | 1 | La Centrale |
| Neumáticos - condición (tires) | 1 | AUTO1 Group |
| [MED·Prueba] Neumáticos de la unidad (medida y marca/modelo) | 1 | km77.com |
| Neumáticos delanteros | 1 | km77.com |
| Neumáticos traseros | 1 | km77.com |
| new_car_calendar_release_dates | 1 | carsales (carsales.com.au) |
| new_car_certified_preowned_info | 1 | carsales (carsales.com.au) |
| new_car_compare_cars | 1 | carsales (carsales.com.au) |
| new_car_expert_review_score_out_of_100 | 1 | carsales (carsales.com.au) |
| New Car Fair Purchase Price | 1 | Kelley Blue Book |
| New car forecast (upside/baseline/downside 12m) | 1 | Cox Automotive Europe |
| new_car_lifestyle_category | 1 | carsales (carsales.com.au) |
| New car price | 1 | Mahindra First Choice Wheels (MFCWL) |
| new_car_rrp_pricing | 1 | carsales (carsales.com.au) |
| New car value / new car data | 1 | Canadian Black Book |
| new_used_pricing (OEM) | 1 | AutoUncle |
| New Vehicle Module (alta de flotas) | 1 | GT Motive |
| New vehicle price (formato New) | 1 | Orange Book Value (OBV) |
| New Vehicle Price Now (precio on-road actual del modelo nuevo) | 1 | Orange Book Value (OBV) |
| New Vehicle Price Then (precio on-road original del ano de compra) | 1 | Orange Book Value (OBV) |
| new vehicle sale flag (96% US coverage) | 1 | Urban Science |
| New Vehicle Value (Low / Average / High, weekly) | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| New Vehicle Value - Average | 1 | J.D. Power Valuation Services |
| New Vehicle Value - High | 1 | J.D. Power Valuation Services |
| New Vehicle Value - Low | 1 | J.D. Power Valuation Services |
| new+used transaction signal | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| newly_listed | 1 | Vehicle Databases |
| NextGear stock funding (100% of cost at checkout) | 1 | Motorway |
| NHTSA 5-Star overall safety rating | 1 | DataOne Software (DataOne, LLC) |
| NHTSA 5-star safety rating | 1 | ClearVin |
| nhtsa_overall_rating | 1 | Vehicle Databases |
| NHTSA rating by impact type | 1 | DataOne Software (DataOne, LLC) |
| NHTSA record | 1 | CCC Intelligent Solutions |
| nhtsa_safety_rating | 1 | CARFAX |
| NICB (National Insurance Crime Bureau) record | 1 | CCC Intelligent Solutions |
| Nieuwprijs (= Catalogusprijs + Optiebedrag) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Nieuwwaarde (seguro) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| NIVE (número ITV) | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Niveau d'équipement | 1 | La Centrale |
| niveau_sonore_dBA (U.1) | 1 | HistoVec |
| Nivel de competitividad de precios | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Nivel de daño pintura metálica (LE/LS/L/LI/LI1) | 1 | Audatex España (Solera) |
| Nivel de daño pintura plástico (LE1/LE/L/LI/LI1) | 1 | Audatex España (Solera) |
| NMR Check (compare vs DB) | 1 | cap hpi (CAP + HPI, a Solera company) |
| NMR Investigation (clocking detection) | 1 | cap hpi (CAP + HPI, a Solera company) |
| NMR reading date | 1 | HPI Check (HPI Ltd, a Solera company) |
| NMR reading source (recorded by) | 1 | HPI Check (HPI Ltd, a Solera company) |
| NMR sources (DVLA, V5, MOT/VOSA, auctions, insurance claims, leasing) | 1 | cap hpi (CAP + HPI, a Solera company) |
| NMVTIS current title state | 1 | Experian Automotive (AutoCheck) |
| NMVTIS junk records | 1 | Experian Automotive (AutoCheck) |
| NMVTIS previous titles by jurisdiction | 1 | Experian Automotive (AutoCheck) |
| NMVTIS title data | 1 | AutoCheck (by Experian) |
| NMVTIS title issue date | 1 | Experian Automotive (AutoCheck) |
| No. of Airbags | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| No. of Cylinders | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| No. of Speakers | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| nom_commercial (D.3) | 1 | HistoVec |
| Nombre de cylindres | 1 | La Centrale |
| Nombre de empresa (flota) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Nombre de municipio (MUNICIPIO) | 1 | Dirección General de Tráfico (DGT) |
| Nombre de places | 1 | La Centrale |
| Nombre de portes | 1 | La Centrale |
| nombre_de_procedures_VE (sinistres a reparation controlee) | 1 | HistoVec |
| Nombre de rapports | 1 | La Centrale |
| Nombre de soupapes par cylindre | 1 | La Centrale |
| nombre_de_titulaires | 1 | HistoVec |
| Nombre del taller | 1 | Audatex España (Solera) |
| nominaal_continu_maximumvermogen (electrico) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Non-EV Index + YoY % | 1 | Cox Automotive |
| Non-Land Use | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Non-runner flag | 1 | BCA (British Car Auctions) |
| non-US prefix coverage | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Norma anticontaminación (Euro) | 1 | Audatex España (Solera) |
| normal/standard service schedule | 1 | DataOne Software (DataOne, LLC) |
| normalized equipment description | 1 | DataOne Software (DataOne, LLC) |
| Normativa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Norme Euro | 1 | La Centrale |
| NotaCarrozzeria | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NotaMeccanica | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Note | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Note du vendeur + avis | 1 | La Centrale |
| NoteAnnuncio | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NoVA rate (AT) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| novedad del registro (novelty) | 1 | Fasecolda — Guía de Valores |
| NPS (Guaranteed) | 1 | autobiz (autobiz Group) |
| Nube/scatter de distribución de precios | 1 | autobiz (autobiz Group) |
| NucleoMotore | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| num_cylinders | 1 | AutoGrab |
| num_doors | 1 | AutoGrab |
| num_gears | 1 | AutoGrab |
| num_seats | 1 | AutoGrab |
| number_axles | 1 | AutoGrab |
| number of /pojazdy method calls (ilosc-wyszukan) [Statystyki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Number of adverts / advert volume | 1 | Glass's |
| Number of auction runs | 1 | IAA (Insurance Auto Auctions) |
| Number of Auctions Included | 1 | Cox Automotive |
| number of axles (liczba-osi) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Number of bids | 1 | Dealer Auction |
| number_of_bids_per_lot_iaai | 1 | Stat.vin (1VIN STAT) |
| Number of bolts | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Number of chargers (turbo) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Number of cylinders | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| number_of_motors | 1 | Vehicle Databases |
| number of photographs / too few pictures (flag) | 1 | INDICATA (Autorola Group) |
| Number of previous keepers | 1 | cap hpi (CAP + HPI, a Solera company) |
| number_of_reviews | 1 | TrueCar |
| Number of Seat Rows | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| number_of_speeds | 1 | Vehicle Databases |
| Number of strokes | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Number of tyres | 1 | Mahindra First Choice Wheels (MFCWL) |
| number_of_units_affected | 1 | Vehicle Databases |
| number of vehicles registered in selected period | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Number of Wheels | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| number_previous_keepers | 1 | AutoGrab |
| numberOfPreviousKeepers [NV bulk] | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| numberOfPreviousOwners | 1 | mobile.de |
| numero_cambi_prezzo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| numero_CNIT (D.2.1) | 1 | HistoVec |
| Numero de cilindros (cylinders/cylinderCapacity) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Numero de key fobs | 1 | Accu-Trade (AccuTrade) |
| Numero de llaves | 1 | Cox Automotive Europe |
| Numero de marchas (gear/gears) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| numero de plazas/seats (座位数) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| numero_de_reception (K) | 1 | HistoVec |
| Numero di passaggi di proprieta (incl. minivolture) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Numero_veicoli | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NumeroCilindri | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NumeroElementiBatterie | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NumeroLicenze | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NumeroMarce | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NumeroPassaggi | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NumeroPorte | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NumeroPosti | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NumeroPostiAggiuntivi | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| NumeroPostiSottraibili | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| numOfDoors | 1 | Edmunds |
| NUTS3 level | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| NVD change dates (model year/price/options/equipment/tech) | 1 | cap hpi (CAP + HPI, a Solera company) |
| OBD / OBDII diagnostic scan | 1 | ACV Auctions |
| obd_cause | 1 | Vehicle Databases |
| obd_code | 1 | Vehicle Databases |
| obd_definition | 1 | Vehicle Databases |
| OBD diagnostic result (Assured/128) | 1 | BCA (British Car Auctions) |
| OBD-II diagnostic deduction (coste de reparacion por fallo) | 1 | Accu-Trade (AccuTrade) |
| OBD-II trouble codes escaneados (109.000) / mapeados (11.000) | 1 | Accu-Trade (AccuTrade) |
| objetivo de electromovilidad por CCAA | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| observación (observation) | 1 | Fasecolda — Guía de Valores |
| Observatoire: prix moyen/médian VO (€) | 1 | La Centrale |
| Observatoire: évolution des prix (% trimestre/an) | 1 | La Centrale |
| Observatoire: évolution par âge | 1 | La Centrale |
| Observatoire: évolution par motorisation | 1 | La Centrale |
| OC validity reminder (przypomnienie OC) [Moj Pojazd] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| 车辆登记证书 OCR (registration certificate fields) | 1 | Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd. |
| 车辆合格证 OCR 12字段: 合格证编号/车架号/排放标准/发动机编号 (conformity cert 12 fields) | 1 | Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd. |
| 行驶证 OCR 21字段 (vehicle license 21 fields) | 1 | Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd. |
| 驾驶证 OCR 9字段 (driver license 9 fields) | 1 | Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd. |
| ocr_confidence | 1 | Vehicle Databases |
| ocr_detected_plate_text | 1 | Vehicle Databases |
| Odor | 1 | Accu-Trade (AccuTrade) |
| OEM build data (todos los OEM principales) | 1 | MAX Digital (ACV MAX) |
| OEM build data validation (ChromeData) | 1 | J.D. Power Valuation Services |
| OEM connection (ej. GM D2C2) | 1 | vAuto |
| OEM customers per plant | 1 | GlobalData Automotive |
| oem_incentive_program | 1 | MarketCheck (MarketCheck Cars Inc) |
| OEM marketing equipment description | 1 | DataOne Software (DataOne, LLC) |
| oem_numbers | 1 | Vehicle Databases |
| OEM pack content & configuration (VINView Pro) | 1 | JATO Dynamics |
| OEM product plans | 1 | GlobalData Automotive |
| OEM rebates | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| OEM Recommended Maintenance Schedule (by mileage interval) | 1 | AutoCheck (by Experian) |
| OEM Repair Methods/procedures | 1 | CCC Intelligent Solutions |
| OEM service schedule (time-based interval) | 1 | DataOne Software (DataOne, LLC) |
| OEM warning codes | 1 | DataOne Software (DataOne, LLC) |
| OEM window sticker / Monroney (35M+, 16 marcas) | 1 | MAX Digital (ACV MAX) |
| OEM window stickers (QR-enabled, synced) | 1 | ACV Auctions |
| OEM-Certified build data (Toyota/Lexus/Scion/Honda/Acura) | 1 | VINCUE (DealerCue Automotive Corp.) |
| OEM-Linked Competitive Sets (like-mine vehicles) | 1 | VINCUE (DealerCue Automotive Corp.) |
| oemCode | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| offer_price_offer_of_one | 1 | TrueCar |
| Offer status (draft/completed/processed) | 1 | Accu-Trade (AccuTrade) |
| offer targeting (model / individual vehicle / inventory age / geography / lead source) | 1 | Urban Science |
| offer trigger (page view / site reentry / KPI completion) | 1 | Urban Science |
| offer validity (7 dias / +250 millas) | 1 | CarOffer (a CarGurus company) |
| OfficeCityState / 지역 (región del anuncio) | 1 | Encar (엔카닷컴 / Encar.com) |
| Offsite (badge) | 1 | IAA (Insurance Auto Auctions) |
| Offsite address | 1 | Copart, Inc. |
| Oil warning light | 1 | BCA (British Car Auctions) |
| Oil/coolant contamination | 1 | BCA (British Car Auctions) |
| Olor (odour) | 1 | Cox Automotive Europe |
| omschrijving_defect | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| On-board charger standard indicator | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| On-board voltage (V) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| on-site appraisal (real-life condition check at collection) | 1 | Motorway |
| oneLineText (descripción de una línea) | 1 | Encar (엔카닷컴 / Encar.com) |
| online business plan | 1 | Urban Science |
| opcionais / itens opcionais (extras) | 1 | Webmotors |
| Opciones value-impacting vacs[] (add/deduct A/D, selected, mutex, disabled) | 1 | Accu-Trade (AccuTrade) |
| Open Repair Order (RO) alert | 1 | VINCUE (DealerCue Automotive Corp.) |
| OPENLANE Inspect (EU): categorias de daño (mirrors, roof arcades) | 1 | OPENLANE |
| OPENLANE Inspect (EU): descripcion de daños tecnicos | 1 | OPENLANE |
| OPENLANE Inspect (EU): fotos offline de daño exterior/interior | 1 | OPENLANE |
| OPENLANE Inspect (EU): identificacion de vehiculo + datos basicos -> OPENLANE Sell portal | 1 | OPENLANE |
| openstaande_terugroepactie_indicator (recall abierto) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Operación E (sustituir) | 1 | Audatex España (Solera) |
| Operación ET (sustitución parcial) | 1 | Audatex España (Solera) |
| Operación H (tratamiento anticorrosivo) | 1 | Audatex España (Solera) |
| Operación I (reparar, marcado con *) | 1 | Audatex España (Solera) |
| Operación IT (tiempo de reparación parcial) | 1 | Audatex España (Solera) |
| Operación N (desmontar/montar) | 1 | Audatex España (Solera) |
| Operación P (comprobar) | 1 | Audatex España (Solera) |
| Operación R (daños ocultos, posición 1000) | 1 | Audatex España (Solera) |
| Operación S (conceptos varios, posición 1000) | 1 | Audatex España (Solera) |
| Operación U (tratamiento de bajos) | 1 | Audatex España (Solera) |
| Operación V (verificar/alinear/marcar) | 1 | Audatex España (Solera) |
| operaciones de reparación | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| operador / sujeto obligado / entidad delegada | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| operating_lease | 1 | carVertical |
| operatingHours | 1 | mobile.de |
| Operation/task type (Replace/Repair/Remove&refit/Paint/Anti-corrosion/Verify/Adjust/Strip-refit/Polish) | 1 | GT Motive |
| opgegeven_maximum_snelheid | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| oplegger_geremd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| opmerkingen_rdw | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| opposition_OTCI_date (transfert certificat immatriculation) | 1 | HistoVec |
| opposition_OTCI_PV_date (amendes / proces-verbal) | 1 | HistoVec |
| opposition_OVE_date (vehicule endommage) | 1 | HistoVec |
| opposition_OVEI_date | 1 | HistoVec |
| Optiebedrag (importe opciones de fábrica) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Opties / Optiebedrag (autorrelleno por kenteken o selección manual) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| optimal_buy_timing | 1 | carVertical |
| optimal_sell_timing | 1 | carVertical |
| optimización de costes (uso / mantenimiento / devolución) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Optimización E por I (diferencia % y € sustituir vs reparar) | 1 | Audatex España (Solera) |
| Optimizacion de stock | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| [EQUIP·Seguridad] Ordenador de viaje | 1 | km77.com |
| Order codes (OEM) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| OreManoOpera | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ORG document id | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Original Equipment Guide (OEG) | 1 | Audatex España (Solera) |
| Original in-service date | 1 | ClearVin |
| Originality (Original / Highly Original / Modified / Custom / Project) | 1 | CLASSIC.COM |
| originally right-hand drive (kierownica-po-prawej-stronie-pierwotnie) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Origination history adjustment (AVT) | 1 | Black Book (National Auto Research — Hearst) |
| originPrice / 신차가 (precio nuevo / MSRP) | 1 | Encar (엔카닷컴 / Encar.com) |
| ORVM Turn Indicators | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| other | 1 | Vehicle Databases |
| Other Bus Info | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Other factory extras/equipment (מפרט/אבזור) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Other issues (+ other_issues_repair_cost) | 1 | Accu-Trade (AccuTrade) |
| Other Motorcycle Info | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Other Restraint System Info | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Other Trailer Info | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Other vehicle history report events (HAV input) | 1 | Black Book (National Auto Research — Hearst) |
| Other warning lights | 1 | BCA (British Car Auctions) |
| OTR price | 1 | cap hpi (CAP + HPI, a Solera company) |
| Out of Pocket Expenses (sum) | 1 | Kelley Blue Book |
| Outbound private-party leads (Facebook/Craigslist/Autotrader/Cars.com) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Outlier flag/asterisco (excluye ventas canadienses previas y vehículos <50 millas) | 1 | Cox Automotive |
| Outside Rear View Mirror (ORVM) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Over Speeding Alert | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Over the Air (OTA) Updates | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Over-average / Overdriven alert | 1 | ClearVin |
| overall condition (detailed) | 1 | Motorway |
| Overall quality score (e.g. 7.9) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Overall rating (e.g. Excellent Buy) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Overall Vehicle Condition rating | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| overlay de datos de reventa reales sobre la curva | 1 | Datium Insights |
| overlay.all_images | 1 | AutoGrab |
| overlay.avg_kms | 1 | AutoGrab |
| overlay.avg_odo | 1 | AutoGrab |
| overlay.avg_price | 1 | AutoGrab |
| overlay.contact_name | 1 | AutoGrab |
| overlay.contact_number | 1 | AutoGrab |
| overlay.cover_image_url (90 días) | 1 | AutoGrab |
| overlay.drive_away_price | 1 | AutoGrab |
| overlay.listing.price | 1 | AutoGrab |
| overlay.listing.source | 1 | AutoGrab |
| overlay.listing.url | 1 | AutoGrab |
| overlay.price_before_govt_charges | 1 | AutoGrab |
| overlay.price_drop_count | 1 | AutoGrab |
| overlay.price_includes_govt_charges | 1 | AutoGrab |
| overlay.price_when_new (RRP) | 1 | AutoGrab |
| overlay.primary_description | 1 | AutoGrab |
| overlay.rego | 1 | AutoGrab |
| overlay.starting_price | 1 | AutoGrab |
| overlay.stock_no | 1 | AutoGrab |
| overlay.tag_ids (trash/damaged/writeoff) | 1 | AutoGrab |
| Overstock reduction | 1 | ACV Auctions |
| Overturned/Rollover | 1 | AutoCheck (by Experian) |
| overview marketing photo | 1 | DataOne Software (DataOne, LLC) |
| Owed amount (saldo del prestamo) | 1 | Accu-Trade (AccuTrade) |
| own repair workshop indicator | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Owned From (per owner) | 1 | AutoCheck (by Experian) |
| Pérdidas | 1 | REPUVE — Registro Público Vehicular |
| P11D / BIK percentages (3 tax years) | 1 | cap hpi (CAP + HPI, a Solera company) |
| P11D value | 1 | cap hpi (CAP + HPI, a Solera company) |
| país (country) | 1 | Fasecolda — Guía de Valores |
| País de origen | 1 | autobiz (autobiz Group) |
| pack pricing | 1 | JATO Dynamics |
| pack.name | 1 | L'argus (Cote Argus®) |
| pack.price-excluding-vat | 1 | L'argus (Cote Argus®) |
| pack.price-including-vat | 1 | L'argus (Cote Argus®) |
| Pacote (option package) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Paese di origine estero | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Pago de tenencias y contribuciones | 1 | REPUVE — Registro Público Vehicular |
| Pago por transferencia bancaria | 1 | Audatex España (Solera) |
| Paint defects | 1 | Manheim |
| Paint material cost (AZT-sourced) | 1 | Autovista Group |
| Paint Material Index (%) | 1 | GT Motive |
| Paint Meter Readings (repintado/chapa) | 1 | ACV Auctions |
| Paint operation/time | 1 | GT Motive |
| Paint system (Manufacturer/AZT/Cevismap/Centro Zaragoza/Manual/Without Paint) | 1 | GT Motive |
| pais de destino de envio (50-70+ paises) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Pan-EU RV benchmark (vía DAT/L'Argus/Quattroruote) | 1 | Autotelex B.V. |
| [EQUIP·Multimedia] Pantalla táctil orientable de 39,6 cm (15,6") | 1 | km77.com |
| Par máximo (Nm) | 1 | km77.com |
| paramrijweerstand_f0 (resistencia rodadura) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| paramrijweerstand_f1 | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| paramrijweerstand_f2 | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| [EQUIP·Confort] Parasoles con espejos de cortesía iluminados | 1 | km77.com |
| Parking Assist | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Parking cost (₹) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Parking Sensors | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| parkingAssistants | 1 | mobile.de |
| Part code (TecDoc compatible) | 1 | Glass's |
| Part description (descripcion de pieza) | 1 | GT Motive |
| part_drawing_scheme | 1 | Vehicle Databases |
| Part identification (replaced OE numbers) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Part multi-reference | 1 | GT Motive |
| part_name | 1 | Vehicle Databases |
| Part supersession (nuevo nº de pieza) | 1 | GT Motive |
| Part-exchange underwrite (Consumer Pro +) | 1 | BCA (British Car Auctions) |
| Part-exchange valuation (retailer) | 1 | Auto Trader UK (Autotrader Group plc) |
| partial_plate_identification | 1 | CARFAX |
| partner_preferred_pricing | 1 | TrueCar |
| partner_targeted_incentives | 1 | TrueCar |
| partnership (dealer / centro de diagnóstico) | 1 | Encar (엔카닷컴 / Encar.com) |
| Parts availability (near real-time) | 1 | CCC Intelligent Solutions |
| Parts history (subrogation audit) | 1 | CCC Intelligent Solutions |
| Parts Platform Filter (%) | 1 | GT Motive |
| Parts price (near real-time) | 1 | CCC Intelligent Solutions |
| Parts Query (nº OEM -> vehiculos/operaciones) | 1 | GT Motive |
| Parts recommendation (sourcing rules) | 1 | CCC Intelligent Solutions |
| Parts Suppliers | 1 | GT Motive |
| passDoors | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Passenger Airbag | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| passenger cars in operation | 1 | GlobalData Automotive |
| passenger_volume | 1 | DataOne Software (DataOne, LLC) |
| passenger_volume_third_row | 1 | DataOne Software (DataOne, LLC) |
| PassoMetri | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Past / historical values | 1 | HPI Check (HPI Ltd, a Solera company) |
| patents database (filterable) | 1 | GlobalData Automotive |
| pay GBP 1 above next bidder (once reserve hit) | 1 | Motorway |
| payload_capacity | 1 | Vehicle Databases |
| payload_volume_square_metres | 1 | AutoGrab |
| Payment Calculator input: APR / interest rate | 1 | CarGurus |
| Payment Calculator input: credit score band | 1 | CarGurus |
| Payment Calculator input: down payment | 1 | CarGurus |
| Payment Calculator input: loan term | 1 | CarGurus |
| Payment Calculator: monthly payment | 1 | CarGurus |
| PDF report (idioma/tipo configurable) | 1 | GT Motive |
| Peak sale value | 1 | ClearVin |
| Pearlescent Uplift (%) | 1 | GT Motive |
| penalty points (punkty karne) [Moj Pojazd / Sprawdz punkty karne] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Pence-per-mile (PPM) / PCH valuation | 1 | cap hpi (CAP + HPI, a Solera company) |
| Período de baja | 1 | Dirección General de Tráfico (DGT) |
| Período de la baja | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Per-category record counts (summary badges) | 1 | ClearVin |
| Per-lot IBB price analytics | 1 | Mahindra First Choice Wheels (MFCWL) |
| per-site vs anonymised-competitor performance breakdown | 1 | JATO Dynamics |
| percent change (vs prior period) | 1 | Urban Science |
| percent_similar_cars_priced_higher | 1 | iSeeCars |
| Percorrenza | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PercorrenzaPrevista | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PerfectFit best-fit ranking | 1 | DataOne Software (DataOne, LLC) |
| PerfectFit proprietary vehicle/equipment score | 1 | DataOne Software (DataOne, LLC) |
| Perfil completo del vehiculo / full vehicle history (specs) | 1 | Eurotax (JD Power / Autovista Group) |
| Perfil de comprador VO | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Perfil de la gama de producto | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Perfil mecánico / condición mecánica | 1 | autobiz (autobiz Group) |
| performance_features | 1 | TrueCar |
| Performance optimization (turn & gross trends) | 1 | ACV Auctions |
| performance.da-0-1000m | 1 | L'argus (Cote Argus®) |
| performance.da-0-100kph (0-100 km/h) | 1 | L'argus (Cote Argus®) |
| performance.maximum-speed (V-max) | 1 | L'argus (Cote Argus®) |
| Period type (daily/monthly/yearly) | 1 | RedBook |
| period.end-date | 1 | L'argus (Cote Argus®) |
| period.end-date-type | 1 | L'argus (Cote Argus®) |
| period.price-excluding-vat (prix HT) | 1 | L'argus (Cote Argus®) |
| period.price-including-vat (prix TTC) | 1 | L'argus (Cote Argus®) |
| period.start-date | 1 | L'argus (Cote Argus®) |
| period.start-date-type | 1 | L'argus (Cote Argus®) |
| Periodo | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| PeriodoFineQuotazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PeriodoImmatricolazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PeriodoInizioQuotazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PeriodoProduzione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Periodos de reprise (trade-in periods) | 1 | autobiz (autobiz Group) |
| permissible axle load (dopuszczalny-nacisk-osi) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| permissible GVW of vehicle combination (dopuszczalna-masa-calkowita-zespolu-pojazdow) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| permissible payload (dopuszczalna-ladownosc) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| personal behaviors | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| personal_use_badge | 1 | CARFAX |
| Personalized Predictions (dealer-performance model) | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| pesos del vehículo | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Pesos del vehiculo | 1 | Eurotax (JD Power / Autovista Group) |
| Pet-free / smoke-free status | 1 | Dealer Auction |
| phase.full-nicename | 1 | L'argus (Cote Argus®) |
| phase.name | 1 | L'argus (Cote Argus®) |
| phase.position | 1 | L'argus (Cote Argus®) |
| phase.short-nicename | 1 | L'argus (Cote Argus®) |
| phone | 1 | MarketCheck (MarketCheck Cars Inc) |
| photo | 1 | iSeeCars |
| Photo availability indicator | 1 | autoDNA |
| Photo carousel | 1 | MAX Digital (ACV MAX) |
| Photo categories (Exterior / Interior / Mechanical / Documents) | 1 | CLASSIC.COM |
| photo gallery | 1 | CarGurus |
| photo_links | 1 | MarketCheck (MarketCheck Cars Inc) |
| photo_links_cached | 1 | MarketCheck (MarketCheck Cars Inc) |
| Photo management (branded overlays, why-buy placeholders, intelligent photo tags) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Photo overlays de features/promociones | 1 | Accu-Trade (AccuTrade) |
| Photo principal | 1 | Encar (엔카닷컴 / Encar.com) |
| Photo upload (outline-match exterior/interior) | 1 | ACV Auctions |
| photo_url | 1 | MarketCheck (MarketCheck Cars Inc) |
| photo.match_confidence (high/medium/low) | 1 | AutoGrab |
| photo.type (stock/generated) | 1 | AutoGrab |
| photo.url | 1 | AutoGrab |
| Photos / Photo Gallery | 1 | GT Motive |
| Photos / Vidéo (galerie) | 1 | La Centrale |
| photos_availability | 1 | iSeeCars |
| photos_count | 1 | carVertical |
| photos_date | 1 | carVertical |
| Photos[] gallery (type, location, updatedDate, ordering) | 1 | Encar (엔카닷컴 / Encar.com) |
| photos_interior_exterior | 1 | TrueCar |
| PianoManutenzione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Picotazos/defectos de cristal (mm) | 1 | Cox Automotive Europe |
| Piezas de mantenimiento | 1 | Eurotax (JD Power / Autovista Group) |
| Pilot Match: overlay concurrence | 1 | La Centrale |
| Pilot Match: overlay prix (sur sites externes/subastas/DMS) | 1 | La Centrale |
| Pilot Price: annonces concurrentes similaires (nº) | 1 | La Centrale |
| Pilot Price: décryptage marché (graphique évolution/distribution) | 1 | La Centrale |
| Pilot Price: marge | 1 | La Centrale |
| Pilot Price: modifications de prix | 1 | La Centrale |
| Pilot Price: nouvelles annonces publiées | 1 | La Centrale |
| Pilot Price: prix conseillé d'achat | 1 | La Centrale |
| Pilot Price: prix conseillé de vente | 1 | La Centrale |
| Pilot Price: recommandation IA en langage naturel (historique + demande locale) | 1 | La Centrale |
| Pilot Price: rotation estimée (days-to-sell) | 1 | La Centrale |
| Pilot Price: tension du marché | 1 | La Centrale |
| Pilot Price: véhicules vendus | 1 | La Centrale |
| Pilot Trends: tendances du marché | 1 | La Centrale |
| Pilot Trends: évolution des ventes par modèle commercial | 1 | La Centrale |
| [EQUIP·Decoración] Pintura (color) | 1 | km77.com |
| [EQUIP·Decoración] Pintura metalizada | 1 | km77.com |
| plaats_chassisnummer (ubicacion VIN) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| plaatscode_as (voor/achter) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| placa (plate; consulta placa→código) | 1 | Fasecolda — Guía de Valores |
| places_assises (S.1) | 1 | HistoVec |
| places_debout (S.2) | 1 | HistoVec |
| plant | 1 | DataOne Software (DataOne, LLC) |
| plant capacity | 1 | GlobalData Automotive |
| plant code | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Plant Company Name | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Plant Country | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Plant State | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Plant Status | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| plant utilization | 1 | GlobalData Automotive |
| Planta de producción | 1 | Audatex España (Solera) |
| Plate change date | 1 | HPI Check (HPI Ltd, a Solera company) |
| plate_change_list | 1 | AutoGrab |
| Plate sequence number (10 plates) | 1 | cap hpi (CAP + HPI, a Solera company) |
| platform_desc | 1 | AutoGrab |
| platform.brakes (front/rear/parking/regenerative) | 1 | L'argus (Cote Argus®) |
| platform.chassis-material | 1 | L'argus (Cote Argus®) |
| platform.chassis-type | 1 | L'argus (Cote Argus®) |
| platform.euroncap-ratings | 1 | L'argus (Cote Argus®) |
| platform.front-suspension-type | 1 | L'argus (Cote Argus®) |
| platform.lcv-cab-type | 1 | L'argus (Cote Argus®) |
| platform.rear-suspension-type | 1 | L'argus (Cote Argus®) |
| platform.steering-wheel-lock-to-lock-turns | 1 | L'argus (Cote Argus®) |
| platform.turning-circle-between-kerbs | 1 | L'argus (Cote Argus®) |
| platform.turning-circle-wall-to-wall | 1 | L'argus (Cote Argus®) |
| Plazo de funding (hasta 150 dias) | 1 | Cox Automotive Europe |
| Plug-in hibrido si/no (isPluginHybrid) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| PM2.5过滤 | 1 | Autohome (汽车之家) |
| PneumaticiMontabili | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Pneumatico | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Poached Data (serviced vehicle appears on competitor lot) | 1 | VINCUE (DealerCue Automotive Corp.) |
| POI Einschlagpunkt (punto de impacto, daño viejo vs nuevo) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Poids à vide | 1 | La Centrale |
| Point-in-time value (current or historical date) | 1 | RedBook |
| Points forts (badges détectés par IA) | 1 | La Centrale |
| police_databases_checked_countries | 1 | carVertical |
| Policy number | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Pollution norm history | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| pooling credits & fine calculation | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Poor Previous Paintwork (PPR) flag | 1 | BCA (British Car Auctions) |
| popular_cars_rank | 1 | MarketCheck (MarketCheck Cars Inc) |
| Popular Mention: Comfort | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Popular Mention: Interior | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Popular Mention: Looks | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Popular Mention: Price | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Popular Mention: Space | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Porcentaje (código opcional) | 1 | Audatex España (Solera) |
| [EQUIP·Confort] Portón trasero eléctrico | 1 | km77.com |
| portas | 1 | Webmotors |
| PortataKgA | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PortataKgDa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Portfolio valuation / risk | 1 | RedBook |
| Posición del volante | 1 | Audatex España (Solera) |
| Posicion de su vehiculo en el mercado | 1 | Eurotax (JD Power / Autovista Group) |
| Positive Score Factors | 1 | Experian Automotive (AutoCheck) |
| Positive/negative equity flag | 1 | IAA (Insurance Auto Auctions) |
| Possible Values | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| post_date | 1 | Vehicle Databases |
| Potencia auxiliar (auxiliaryPower) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Potencia fiscal (CVF) | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Potencia fiscal en CVF (POTENCIA_ITV) | 1 | Dirección General de Tráfico (DGT) |
| Potencia máxima (CV / kW) | 1 | km77.com |
| Potencia neta máxima (kW) | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Potencial de facturación (provincia/código postal) | 1 | Audatex España (Solera) |
| Potencial de postventa | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Potencial de reparaciones (provincia/código postal) | 1 | Audatex España (Solera) |
| potential / net transaction price | 1 | JATO Dynamics |
| Potenza di ricarica (EV) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| PotenzaCV | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PotenzaFiscale | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PotenzaKW | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PotenzaMaxGiriMinuto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PotenzaPiccoCV | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PotenzaPiccoKW | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PotenzaRicaricakW | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PotenzaRicaricaRapida | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| powerAssistedSteering | 1 | mobile.de |
| powerRPM | 1 | Autotelex B.V. |
| powerUnit | 1 | Autotelex B.V. |
| PPSR processing status | 1 | RedBook |
| PPSR reference id | 1 | RedBook |
| PPSR report (certificate URLs) | 1 | RedBook |
| ppsr.has_changed | 1 | AutoGrab |
| ppsr.has_expired | 1 | AutoGrab |
| pre_bid | 1 | Stat.vin (1VIN STAT) |
| preço anunciado (asking price) | 1 | Webmotors |
| Preço por versão diferenciado (S / SE / SE Plus) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| preço Tabela FIPE (referencia mostrada en la ficha) | 1 | Webmotors |
| Preço usado / seminovo (por tiempo de uso) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Pre-launch / opinion forecast | 1 | cap hpi (CAP + HPI, a Solera company) |
| Precio de competidores (actualizado a diario) | 1 | Eurotax (JD Power / Autovista Group) |
| Precio de reprise online garantizado | 1 | autobiz (autobiz Group) |
| Precio de reserva (reserve price) | 1 | autobiz (autobiz Group) |
| Precio del anuncio (€) | 1 | coches.net |
| Precio en condicion Excellent | 1 | Orange Book Value (OBV) |
| Precio en condicion Fair | 1 | Orange Book Value (OBV) |
| Precio en condicion Good | 1 | Orange Book Value (OBV) |
| Precio en condicion Very Good | 1 | Orange Book Value (OBV) |
| Precio estimado de cierre / 'que precio voy a obtener' (output tasador) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| precio FOB en USD (export) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Precio Instant Purchase / direct buy (compra inmediata) | 1 | AUTO1 Group |
| Precio mínimo de venta / reserva (reserve price) | 1 | AUTO1 Group |
| Precio medio de venta mayorista mensual (mean sales price por categoría) | 1 | AUTO1 Group |
| precio medio del VO (€) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| precio medio del VO hasta 10 años (€) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| precio medio ponderado por motorización (ref. 3 años) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| precio medio por motorización (gasolina/diésel/HEV/PHEV/BEV) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| precio medio por tramo de antigüedad (0-1/2-5/6-10/11-15/15-20 años) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Precio medio VO (global / por antigüedad / por motorización) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Precio medio/estimado de mercado (valor medio de unidades similares) | 1 | coches.net |
| Precio rebajado por profesional (traderReducedPrice) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Precio recomendado de venta (output tasador) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Precio retail base | 1 | Audatex España (Solera) |
| Precio sin IVA / IVA deducible (netPrice/isVatLabelLegallyRequired) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Precio y referencia de lunas/cristales (AudaGlass) | 1 | Audatex España (Solera) |
| Precios de transacciones reales (portales de venta online) | 1 | Audatex España (Solera) |
| Precios de venta en tiempo real (live retail) | 1 | Eurotax (JD Power / Autovista Group) |
| Precios EV | 1 | Eurotax (JD Power / Autovista Group) |
| Precios reales de transacción (distribuidores/financieras) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Precision de valoracion (hasta 99%) | 1 | Cox Automotive Europe |
| [EQUIP·Confort] Preclimatización del habitáculo | 1 | km77.com |
| Predecessor-successor RV link | 1 | Autovista Group |
| preDelivery | 1 | Encar (엔카닷컴 / Encar.com) |
| Prediccion de rendimiento del vehiculo (area local) | 1 | Cox Automotive Europe |
| Prediccion de reparacion anual | 1 | Eurotax (JD Power / Autovista Group) |
| Predicted accuracy (dentro de $100 del precio final) | 1 | MAX Digital (ACV MAX) |
| Predicted likelihood vehicle on road in 5 years | 1 | Experian Automotive (AutoCheck) |
| Predicted outcome / action-based forecast | 1 | MAX Digital (ACV MAX) |
| Predicted outcomes (action-based forecasts) | 1 | ACV Auctions |
| predicted purchase next 0-3 months / 90 days | 1 | Urban Science |
| Predictive Average Days to Sale | 1 | VINCUE (DealerCue Automotive Corp.) |
| Predictive maintenance scheduling | 1 | Glass's |
| predictive signal: company filings | 1 | GlobalData Automotive |
| predictive signal: deals (M&A / PE / VC) | 1 | GlobalData Automotive |
| predictive signal: jobs / hiring | 1 | GlobalData Automotive |
| predictive signal: news | 1 | GlobalData Automotive |
| predictive signal: patents | 1 | GlobalData Automotive |
| predictive signal: social media sentiment | 1 | GlobalData Automotive |
| Predictive vehicle value (per rooftop) | 1 | ACV Auctions |
| Preferred contact method (email/phone/text) | 1 | Accu-Trade (AccuTrade) |
| Preisänderung MoM/YoY % (price change) | 1 | AutoScout24 |
| Preisänderungen Wettbewerber (competitor price changes) | 1 | AutoScout24 |
| Preisbarometer average used price | 1 | mobile.de |
| Preisbarometer listing stock (Bestand) + YoY change | 1 | mobile.de |
| Preisbewertung-Label: Erhöhter Preis | 1 | AutoScout24 |
| Preisbewertung-Label: Fairer Preis | 1 | AutoScout24 |
| Preisbewertung-Label: Guter Preis | 1 | AutoScout24 |
| Preisbewertung-Label: Hoher Preis | 1 | AutoScout24 |
| Preisbewertung-Label: Sehr guter Preis | 1 | AutoScout24 |
| Preisdifferenz vs Markt (difference vs market price) | 1 | AutoScout24 |
| Preisempfehlung (precio recomendado para anunciar) | 1 | AutoScout24 |
| Preisentwicklung Wettbewerber (competitor price trend) | 1 | AutoScout24 |
| Preisspanne / Verhandlungsspielraum (price range + negotiation margin) | 1 | AutoScout24 |
| Preisspanne im Markt (market price range) | 1 | AutoScout24 |
| Preliminary ProQuote (valor predictivo salvamento) | 1 | Copart, Inc. |
| Premium Imagery Sets (up to 75 photos) | 1 | IAA (Insurance Auto Auctions) |
| premium service schedule | 1 | DataOne Software (DataOne, LLC) |
| Premium Studio Still (front 3/4) | 1 | DataOne Software (DataOne, LLC) |
| Preselection of the cheapest part | 1 | GT Motive |
| PresenzaDatiWltp | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| presupuesto detallado de reparación (estimado) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Pretensioner | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Prevar.comparaison-3-vehicules | 1 | L'argus (Cote Argus®) |
| Prevar.historique-indices-decote | 1 | L'argus (Cote Argus®) |
| Prevar.indice-de-decote | 1 | L'argus (Cote Argus®) |
| Prevar.matrice-globale (durée×km) | 1 | L'argus (Cote Argus®) |
| Prevar.matrice-personnalisée | 1 | L'argus (Cote Argus®) |
| Prevar.profils (perfiles paramétricos) | 1 | L'argus (Cote Argus®) |
| Prevar.tarif-ttc | 1 | L'argus (Cote Argus®) |
| Prevar.vehicules-equivalents | 1 | L'argus (Cote Argus®) |
| preVerified | 1 | Encar (엔카닷컴 / Encar.com) |
| previous purchase | 1 | Urban Science |
| previous_title_status | 1 | Vehicle Databases |
| Previous/last state of title | 1 | NMVTIS / VehicleHistory.gov |
| previousOwners (count) | 1 | Auto Trader UK (Autotrader Group plc) |
| previsión de margen comercial | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| previsión por horizonte (corto/medio plazo) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| previsión variación % | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Prevision de VR a 3 anos / hasta 120 meses (10 anos) | 1 | Eurotax (JD Power / Autovista Group) |
| Prevision mercado VO turismos (ForCar VO) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Prevision VR al inicio de contrato (posicion de riesgo) | 1 | Eurotax (JD Power / Autovista Group) |
| PrezziIvati | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Prezzo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Prezzo di listino (nuovo) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Prezzo di listino del nuovo per il lead | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Prezzo di listino iniziale + andamento svalutazione | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Prezzo di vendita online Consigliato (StreetPrice) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Prezzo di vendita online Massimo (StreetPrice) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Prezzo di vendita online Minimo (StreetPrice) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| prezzo_listino | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| prezzo_ritiro | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PrezzoChiaviInMano | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PrezzoListino | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PrezzoMassimoAcquisto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PrezzoMercato | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PrezzoMercatoPerc | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PrezzoPreventivato | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| PrezzoVenditaPreventivato | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Price below market / favorable pricing highlight | 1 | MAX Digital (ACV MAX) |
| Price bracket (sub-£10k / over £10k / £25k cap) | 1 | Dealer Auction |
| Price category / VAT status (margin vs VAT-qualifying) | 1 | Autorola |
| price_change_percent | 1 | MarketCheck (MarketCheck Cars Inc) |
| Price Checker rating | 1 | Edmunds |
| price_development | 1 | AutoUncle |
| Price development / tendencia de evolución de precio | 1 | autobiz (autobiz Group) |
| price_drop_amount | 1 | Cars Commerce (Cars.com Inc.) |
| price_drop_notification | 1 | Cars Commerce (Cars.com Inc.) |
| price_drop_notification / price_alarm | 1 | AutoUncle |
| price_drop_notifications | 1 | TrueCar |
| Price Evaluation: Abaixo da média (etiqueta) | 1 | Standvirtual |
| Price Evaluation: Acima da média (etiqueta) | 1 | Standvirtual |
| Price Evaluation: Dentro da média (etiqueta) [V live] | 1 | Standvirtual |
| price_graph_transaction_distribution | 1 | TrueCar |
| Price Indicator: Fair price | 1 | Auto Trader UK (Autotrader Group plc) |
| Price Indicator: Good price | 1 | Auto Trader UK (Autotrader Group plc) |
| Price Indicator: Great price | 1 | Auto Trader UK (Autotrader Group plc) |
| Price Indicator: Higher price | 1 | Auto Trader UK (Autotrader Group plc) |
| Price Indicator label (Great/Good/Fair/Higher/Lower + £ variance) | 1 | Dealer Auction |
| Price Indicator: Lower price | 1 | Auto Trader UK (Autotrader Group plc) |
| Price Indicator: No Analysis (no label) flag | 1 | Auto Trader UK (Autotrader Group plc) |
| Price indicator rating band lower (GBP) | 1 | Auto Trader UK (Autotrader Group plc) |
| Price indicator rating band upper (GBP) | 1 | Auto Trader UK (Autotrader Group plc) |
| price inflation metric | 1 | JATO Dynamics |
| Price movements | 1 | RedBook |
| price_new / nieuwprijs (precio nuevo) | 1 | Autotelex B.V. |
| price not changed recently (flag) | 1 | INDICATA (Autorola Group) |
| price_predictor_retail | 1 | MarketCheck (MarketCheck Cars Inc) |
| Price provisional flag | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Price Radar: días en campaña / antigüedad de publicación | 1 | coches.net |
| Price Radar: desviación respecto al precio medio de mercado (price-to-market %) | 1 | coches.net |
| Price Radar: detección de activos tóxicos (stock estancado) | 1 | coches.net |
| Price rank | 1 | vAuto |
| price type | 1 | mobile.de |
| price vs IMV (%) | 1 | CarOffer (a CarGurus company) |
| Price when new (at-new value) | 1 | HPI Check (HPI Ltd, a Solera company) |
| priceassist_average_time_to_sell_days | 1 | carsales (carsales.com.au) |
| priceassist_price_comparison_vs_similar | 1 | carsales (carsales.com.au) |
| priceassist_recommended_price_for_target_time | 1 | carsales (carsales.com.au) |
| priceassist_similar_cars_for_sale_now_count | 1 | carsales (carsales.com.au) |
| priceassist_similar_cars_sold_12m_count | 1 | carsales (carsales.com.au) |
| priceCommentary | 1 | Auto Trader UK (Autotrader Group plc) |
| priceDifferential / Savings (asking price vs IMV) | 1 | CarGurus |
| priceIndicatorRating (advert) | 1 | Auto Trader UK (Autotrader Group plc) |
| priceRange.high | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| priceRange.low | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| priceRating / AutoScore (Super price | Good price | Fair price | A bit pricey | Expensive) | 1 | AutoUncle |
| priceRating label (VERY_GOOD_PRICE) | 1 | mobile.de |
| priceRating labelRange.from (EUR per tier) | 1 | mobile.de |
| priceRating labelRange.to (EUR per tier) | 1 | mobile.de |
| priceRating NO_RATING + reason codes (11) | 1 | mobile.de |
| prices.amount | 1 | Autotelex B.V. |
| prices.amountExVat | 1 | Autotelex B.V. |
| prices.currency / currencySymbol / countrycode | 1 | Autotelex B.V. |
| prices.priceType | 1 | Autotelex B.V. |
| prices.taxIncluded | 1 | Autotelex B.V. |
| prices.vatPercentage | 1 | Autotelex B.V. |
| priceValue (numeric) | 1 | AutoUncle |
| PriceVantage: 10B+ monthly shopper intent signals | 1 | CarGurus |
| PriceVantage: IMS syndication (price push to Inventory Management System) | 1 | CarGurus |
| PriceVantage: IMV lookup | 1 | CarGurus |
| PriceVantage: lead-potential forecast (impact of price change before applying) | 1 | CarGurus |
| PriceVantage price recommendation (turn-time-based) | 1 | CarOffer (a CarGurus company) |
| PriceVantage: turn time goal | 1 | CarGurus |
| Pricing alignment / adherence a la recomendacion | 1 | vAuto |
| Pricing Comparison | 1 | Orange Book Value (OBV) |
| pricing_intelligence | 1 | AutoUncle |
| Pricing score | 1 | RedBook |
| Pricing shifts | 1 | VINCUE (DealerCue Automotive Corp.) |
| pricing strategy (avg price-to-market by age band) | 1 | INDICATA (Autorola Group) |
| Pricing Tool: increase-price-without-dropping-deal-rating opportunities | 1 | CarGurus |
| Pricing Tool: 'mark as sold' action (24h feed sync) | 1 | CarGurus |
| pricing_trends | 1 | TrueCar |
| PrimaImmatricolazioneEstera | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| primary_compression_ratio | 1 | Vehicle Databases |
| primary_drive_rear_wheel | 1 | Vehicle Databases |
| Primary point of impact (First Look AI) | 1 | CCC Intelligent Solutions |
| primo_prezzo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Print Value Report | 1 | MAX Digital (ACV MAX) |
| Prior-repair / Special Adjustment (e.g. rebuilt transmission) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| priorización de tecnología de conectividad (encuesta a fabricantes) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| private offer delivery (text / email / website overlay / API) | 1 | Urban Science |
| Private valuation (retailer) | 1 | Auto Trader UK (Autotrader Group plc) |
| Privati_custom | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Privati_generica_autoscout24_medium | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Privati_generica_subito_medium | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Privati_hard | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Privati_medium | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Privati_soft | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Privatverkaufswert [NO-VERIFICADO] | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Privatverkaufswert / Marktwert (valor de venta privada / mercado) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Prix (€) | 1 | La Centrale |
| Prix du Neuf (initial-prices) | 1 | L'argus (Cote Argus®) |
| Prix neuf (€) | 1 | La Centrale |
| PRO: gestión de stock multi-tipología | 1 | coches.net |
| PRO: iTasador (tasador integrado para aprovisionamiento) | 1 | coches.net |
| PRO: multipublicación (coches.net + Milanuncios + web propia + >40 portales) | 1 | coches.net |
| PRO: posicionamiento/subidas de stock (cada 3/6 días/mensual) | 1 | coches.net |
| PRO: tracking telefónico (origen, atendidas/no atendidas, perdidas, estadísticas) | 1 | coches.net |
| PRO: vídeos en anuncio / vídeos corporativos | 1 | coches.net |
| procedure_VE_en_cours_PVE | 1 | HistoVec |
| Procurement channel mix (exchange %) | 1 | Mahindra First Choice Wheels (MFCWL) |
| producción de comerciales+industriales (unidades) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| producción de turismos (unidades) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| producción de vehículos alternativos/electrificados (unidades) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| producción mensual / acumulado / variación % | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Product competitiveness | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| product_eenheid | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Product image / photo | 1 | CarNewsChina Data (China EV DataTracker) |
| product launch timing / pipeline | 1 | GlobalData Automotive |
| product leakage to non-branded retailers | 1 | INDICATA (Autorola Group) |
| product_omschrijving | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| product portfolio per plant / supplier | 1 | GlobalData Automotive |
| production by bodystyle | 1 | GlobalData Automotive |
| production by plant / factory | 1 | GlobalData Automotive |
| production by platform | 1 | GlobalData Automotive |
| production by vehicle program | 1 | GlobalData Automotive |
| production forecast (plant capacity/export/body style) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| production method (sposob-produkcji) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| production_serial_numbers | 1 | iSeeCars |
| Profesional: Call tracker | 1 | Standvirtual |
| Profesional: Estadísticas de rendimiento por anuncio (vistas/contactos) | 1 | Standvirtual |
| Profesional: Perfil do comprador (buyer profile data) | 1 | Standvirtual |
| Profesional: Posición del anuncio en los resultados de búsqueda (tiempo real) | 1 | Standvirtual |
| Profesional: Recomendaciones de ajuste de precio/marketing (modelos lentos) | 1 | Standvirtual |
| profile-accuracy / re-guide flag (new damage) | 1 | Motorway |
| Profiles & schemes management | 1 | GT Motive |
| Profit / gross projection (por vehiculo) | 1 | MAX Digital (ACV MAX) |
| Profit corridor indicator | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Profit Funnel report | 1 | Accu-Trade (AccuTrade) |
| Profit objective | 1 | vAuto |
| Profit potential / ROI por vehiculo | 1 | vAuto |
| Profit target / Business Plans (filtro por profit potential) | 1 | vAuto |
| Profit target / profit potential | 1 | Stockwave (vAuto · Cox Automotive) |
| Profit vs speed (margin vs days-to-sale tradeoff) | 1 | ACV Auctions |
| Profitto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| [MED·Maletero] Profundidad (cm) | 1 | km77.com |
| Programmatic / proxy bidding (S.A.M.) | 1 | ACV Auctions |
| ProgressivoRCL | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Projected front-end gross / PVR | 1 | Stockwave (vAuto · Cox Automotive) |
| Projected/forecasted value (next month) | 1 | Manheim |
| Projector Headlamps | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| proof of purchase (if registered keeper < 3 months) | 1 | Motorway |
| property_rights_restrictions | 1 | carVertical |
| Propriétaire Première main (flag) | 1 | La Centrale |
| proprietaire_actuel_anonymise | 1 | HistoVec |
| Pros (Good Things) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Provenance (procedencia) | 1 | Hagerty |
| Provenance check (via Experian, separate subscription) | 1 | Glass's |
| provenienza | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| province | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| province name (nazwa-wojewodztwa) [Statystyki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Provision Appraised Value (sigue al vehiculo compra->venta) | 1 | Stockwave (vAuto · Cox Automotive) |
| Provisioning value | 1 | RedBook |
| PTAC_kg (F.2) | 1 | HistoVec |
| PTAV_poids_a_vide_kg (G.1) | 1 | HistoVec |
| PTES_pt_en_service_kg (G) | 1 | HistoVec |
| PTRA_kg (F.3) [API] | 1 | HistoVec |
| PTTA_pt_techniquement_admissible_kg (F.1) | 1 | HistoVec |
| Public (badge) | 1 | IAA (Insurance Auto Auctions) |
| publicatiedatum_rdw | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| publicationDate | 1 | Autotelex B.V. |
| publishable | 1 | L'argus (Cote Argus®) |
| publisher_name | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| publisher_phone | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Publishes to AutoCheck VHR | 1 | ACV Auctions |
| Publishes to Carfax VHR | 1 | ACV Auctions |
| PUC certificate | 1 | Mahindra First Choice Wheels (MFCWL) |
| Puissance DIN (ch) | 1 | La Centrale |
| Puissance fiscale (CV) | 1 | La Centrale |
| puissance_fiscale_ch | 1 | HistoVec |
| Puja actual (current bid) | 1 | AUTO1 Group |
| Pujas de compradores profesionales | 1 | Audatex España (Solera) |
| Puntos de interes (POI: hoteles/bancos/parking/gasolineras/restaurantes) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Puntos de severidad de daño | 1 | Cox Automotive Europe |
| puntuacion del vehiculo (车辆评分) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Purchase price aseguradora (importador + lista) | 1 | Autotelex B.V. |
| purchase-likelihood score | 1 | Urban Science |
| purchase-rate lift multiplier (10x overall / 25x brand / 7x segment / 5x EV / 2.5x vs competitors) | 1 | Urban Science |
| Purpose (Buy / Sell) | 1 | Orange Book Value (OBV) |
| qualityCheck descriptionLength (min 500 / optimal 1000 chars / current) | 1 | mobile.de |
| qualityCheck image overlays result | 1 | mobile.de |
| qualityCheck image vehicleFocus result | 1 | mobile.de |
| qualityCheck image vehicleVisibility result | 1 | mobile.de |
| qualityCheck imageQuality score | 1 | mobile.de |
| qualityCheck imageQuantity (min 10 / optimal 25 / current) | 1 | mobile.de |
| qualityCheck overallQualityCheck (0-100) | 1 | mobile.de |
| qualityCheck status | 1 | mobile.de |
| Quantidade de passageiros / plazas (QtdPassageiro) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Quantity (cantidad) | 1 | GT Motive |
| Quick Check (precio puntual) | 1 | Orange Book Value (OBV) |
| quilometragem (km) | 1 | Webmotors |
| Quimica de celda y composicion de catodo | 1 | Eurotax (JD Power / Autovista Group) |
| Équipements de sécurité (liste itemizada) | 1 | La Centrale |
| Équipements extérieur (liste) | 1 | La Centrale |
| Équipements intérieur (liste) | 1 | La Centrale |
| QuotazioneMensileRitiro | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| QuotazioneMensileVendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| QuotazioneRitiro | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| QuotazioneStandardRitiro | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| QuotazioneStandardVendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| QuotazioneStorica | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| QuotazioneVendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| QuotazioneVenditaPersonalizzata | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Quote de movimiento (precio) | 1 | Cox Automotive Europe |
| Quote manipulation indicators | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Réf. pro / Réf. annonce | 1 | La Centrale |
| Régimen BPM más favorable (selección automática) | 1 | Autotelex B.V. |
| Régions et pays voisins (filtre) | 1 | La Centrale |
| Rachat Express: attestation de paiement <48h | 1 | La Centrale |
| Rachat Express: estimation gratuite (<2 min, plaque+km) | 1 | La Centrale |
| Rachat Express: offre de rachat ferme (€) | 1 | La Centrale |
| Rachat Express: RDV concessionnaire agréé (300) | 1 | La Centrale |
| radar equipment type (wyposazenie-i-rodzaj-urzadzenia-radarowego) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Radio de conduccion por minutos (isocronas) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| [EQUIP·Multimedia] Radio digital | 1 | km77.com |
| Radio functionality | 1 | OPENLANE |
| RaggruppamentoVincolo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| rang_titulaire (1er/2e...) | 1 | HistoVec |
| RangeAnni | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| rangeCombined (autonomía combinada) | 1 | Autotelex B.V. |
| rangeElectric (autonomía eléctrica) | 1 | Autotelex B.V. |
| RangeKm | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| RangeScarto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Rango de precio del listado (lowPrice–highPrice) | 1 | coches.net |
| Rango/fecha de producción (DESDE mm-aaaa) | 1 | Audatex España (Solera) |
| ranking de producción (2º de Europa / Top-10 mundial) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| ranking internacional de países VA/VC | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Rapport h/L pneu arrière | 1 | La Centrale |
| Rapport h/L pneu avant | 1 | La Centrale |
| rapport_puissance_masse [API] | 1 | HistoVec |
| RapportoPotenzaMassa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| RapportoPotenzaMassima | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Rated speed rpm (from/to) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Ratio VO:VN | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| RC status | 1 | Mahindra First Choice Wheels (MFCWL) |
| RC verification (registration details, VAHAN) | 1 | Mahindra First Choice Wheels (MFCWL) |
| RDW oordeel kilometerstand (juicio NAP: Logisch/Onlogisch) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| RDW raw data estructurada | 1 | Autotelex B.V. |
| rdwConstruction | 1 | Autotelex B.V. |
| Re-auction recommendation (IntelliSeller) | 1 | Copart, Inc. |
| Re-valoraciones ilimitadas multi-escenario (edad/km) | 1 | Eurotax (JD Power / Autovista Group) |
| real auction outcomes (ML signal) | 1 | Motorway |
| Real cash value / guaranteed offer (price.offer) | 1 | Accu-Trade (AccuTrade) |
| Real Market Value (RMV) — composite valuation | 1 | VINCUE (DealerCue Automotive Corp.) |
| real_time_value_calculation | 1 | TrueCar |
| Real-time auction market data (~1.000 vehiculos/semana) | 1 | Accu-Trade (AccuTrade) |
| Real-time collaboration experto-reparador | 1 | GT Motive |
| Real-time daily valuation | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Real-time market valuation (ACV VIPER) | 1 | MAX Digital (ACV MAX) |
| Real-time notifications (new app) | 1 | Manheim |
| Real-time SMS alerts (tire replacement + acquisition lead: mileage/title/recommended offer) | 1 | ACV Auctions |
| Real-time valuation (BCA Market Price) | 1 | BCA (British Car Auctions) |
| Real-time vehicle offer (rooftop-specific) | 1 | ACV Auctions |
| Real-Time Vehicle Tracking | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Rear AC Vents | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| rear_brake_diameter | 1 | Vehicle Databases |
| Rear Camera | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Rear Cross Traffic Alert | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| rear_head_room | 1 | Vehicle Databases |
| rear_hip_room | 1 | Vehicle Databases |
| rear_legroom | 1 | Vehicle Databases |
| Rear Parcel Tray | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Rear Seat Headrest | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| rear_seats | 1 | Vehicle Databases |
| rear_shoulder_room | 1 | Vehicle Databases |
| rear_suspension_size | 1 | Vehicle Databases |
| rear_suspension_type | 1 | Vehicle Databases |
| Rear tire age (excellent/good/poor) | 1 | Accu-Trade (AccuTrade) |
| rear_tire_order_code | 1 | Vehicle Databases |
| rear_tire_pressure | 1 | Vehicle Databases |
| rear_tire_size | 1 | Vehicle Databases |
| rear_tire_type | 1 | DataOne Software (DataOne, LLC) |
| Rear Tires condition | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| rear_track | 1 | DataOne Software (DataOne, LLC) |
| Rear track size | 1 | ClearVin |
| rear_travel | 1 | Vehicle Databases |
| Rear view mirror | 1 | BCA (British Car Auctions) |
| Rear Visibility System | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| rear_wheel_dia | 1 | DataOne Software (DataOne, LLC) |
| rear_wheel_diameter | 1 | Vehicle Databases |
| Rear Window Defogger | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Rear Window Washer | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Rear Window Wiper | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Reason for loss | 1 | AutoCheck (by Experian) |
| reasonCode (KADOE) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| Reasoning (key data signals + market factors) | 1 | ACV Auctions |
| Reasoning / key data signals (explicabilidad) | 1 | MAX Digital (ACV MAX) |
| Rebuilt title (is_rebuilt_title) | 1 | Accu-Trade (AccuTrade) |
| Recargo perla/bicapa (+2% materiales) | 1 | Audatex España (Solera) |
| Receipt document (generated) | 1 | Autorola |
| Recent comparable sales (lista + grafico) | 1 | Hagerty |
| Recent comparable transaction data | 1 | ACV Auctions |
| recent_comparables | 1 | MarketCheck (MarketCheck Cars Inc) |
| recent purchaser exclusion (suppression) | 1 | Urban Science |
| Recent Transactions - average kilometers driven | 1 | Orange Book Value (OBV) |
| Recent Transactions (50, ult. 3 meses) - average selling price | 1 | Orange Book Value (OBV) |
| Recent Transactions - highest selling price | 1 | Orange Book Value (OBV) |
| Recent Transactions - lowest selling price | 1 | Orange Book Value (OBV) |
| Recomendación de precio / precio final | 1 | autobiz (autobiz Group) |
| Recomendacion de distribucion/canal de inventario | 1 | Cox Automotive Europe |
| Recomendacion de reacondicionamiento | 1 | Cox Automotive Europe |
| recommended / optimal price | 1 | INDICATA (Autorola Group) |
| Recommended acquisition / appraisal price (por canal) | 1 | vAuto |
| Recommended price adjustment (subir/bajar) | 1 | MAX Digital (ACV MAX) |
| Recon alerts (problemas comunes por year/make/model) | 1 | MAX Digital (ACV MAX) |
| Recon estimate (at appraisal) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Recon plan templates | 1 | vAuto |
| Recon step/stage tracking | 1 | vAuto |
| Recon variance (estimate vs actual, VIN-level) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Recon variance breakdown by appraiser/advisor/source/store | 1 | VINCUE (DealerCue Automotive Corp.) |
| Reconditioning cost (mecanico + cosmetico) | 1 | Accu-Trade (AccuTrade) |
| Reconditioning cost estimate | 1 | Stockwave (vAuto · Cox Automotive) |
| Reconditioning estimate | 1 | vAuto |
| Reconditioning expectation (implied by grade) | 1 | Manheim |
| Reconditioning issue flags (por YMM) | 1 | ACV Auctions |
| [EQUIP·Seguridad] Reconocimiento de señales de tráfico | 1 | km77.com |
| reconstructed_title_issued_flag | 1 | Stat.vin (1VIN STAT) |
| record_confidence | 1 | MarketCheck (MarketCheck Cars Inc) |
| record_source | 1 | MarketCheck (MarketCheck Cars Inc) |
| recorded_selling_prices | 1 | carVertical |
| Recovery status | 1 | ClearVin |
| [EQUIP·Varios] Recuperación de la energía de frenado | 1 | km77.com |
| Recycling charge | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| RedBook ID | 1 | RedBook |
| RedBook watermark | 1 | RedBook |
| RedbookCodeLegacy | 1 | RedBook |
| redemption (identity verified / fraud detection / 30s) | 1 | Urban Science |
| redline | 1 | DataOne Software (DataOne, LLC) |
| reducción de fraude (trazabilidad y coherencia de datos) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| reduced_price | 1 | Vehicle Databases |
| reembolso integro vitalicio (accidente/incendio/inundacion) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| reemplazo/garantia 30 dias | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| ref_miles | 1 | MarketCheck (MarketCheck Cars Inc) |
| ref_miles_dt | 1 | MarketCheck (MarketCheck Cars Inc) |
| ref_price | 1 | MarketCheck (MarketCheck Cars Inc) |
| ref_price_dt | 1 | MarketCheck (MarketCheck Cars Inc) |
| Ref. Expediente | 1 | Audatex España (Solera) |
| Ref. Valoración | 1 | Audatex España (Solera) |
| Reference Number | 1 | GT Motive |
| referenceNumber (KADOE) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| referencia 3 / versión (line3) | 1 | Fasecolda — Guía de Valores |
| referentiecode_producent | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| referentiecode_rdw (recall) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Referrals (listing analytics) | 1 | CLASSIC.COM |
| Refurbishment adjustment | 1 | CCC Intelligent Solutions |
| Refurbishment cost (₹) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Região (12 macro-regiones comerciales B2B) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Regime IVA (corrente / 4% / personalizzato) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Register of Approved Vehicles (RAV) reference | 1 | RedBook |
| registratie_datum_goedkeuring_afschrijvingsmoment_bpm | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| regulatory trends | 1 | GlobalData Automotive |
| Release / launch date | 1 | CarNewsChina Data (China EV DataTracker) |
| Release Date | 1 | RedBook |
| release_month | 1 | AutoGrab |
| remaining_lifespan (años de vida útil restante - metrica firma) | 1 | iSeeCars |
| remarks (lead) | 1 | Autotelex B.V. |
| Remote Door Lock/Unlock | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Remote ignition | 1 | ClearVin |
| Remove and install / R&I (estimate line) | 1 | CCC Intelligent Solutions |
| Renewal pricing optimization (MOT tracking) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| renewalDate | 1 | mobile.de |
| Rental / ex-hire deduction (השכרה / החכרה) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Rental cost reduction | 1 | IAA (Insurance Auto Auctions) |
| Rental penetration (adjustable residual-sensitivity input) | 1 | Canadian Black Book |
| Rentals flag | 1 | Copart, Inc. |
| Repair / claim status (eRepair) | 1 | Autorola |
| Repair authorisation (fleet/leasing) | 1 | GT Motive |
| Repair by Hail Formula (recargo aluminio/cavidad/adhesivo) | 1 | GT Motive |
| repair_decision | 1 | AutoGrab |
| repair_description | 1 | Vehicle Databases |
| Repair estimate | 1 | IAA (Insurance Auto Auctions) |
| repair_estimates (CA) | 1 | CARFAX |
| Repair estimation data (AudaEnterpriseGold) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Repair or replace (estimate line) | 1 | CCC Intelligent Solutions |
| repair_title | 1 | Vehicle Databases |
| repair_value_id | 1 | Vehicle Databases |
| Repairable vs total-loss determination | 1 | IAA (Insurance Auto Auctions) |
| Reparaturen / Reparaturaufwand (reparaciones) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Reparaturkosten Markt (coste medio de reparacion) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Reparaturkostenkalkulation (damage repair cost) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Reparaturweg (via de reparacion) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Reparieren vs ersetzen (decision reparar vs sustituir) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| replacement / holding time expectation | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Replacement cost | 1 | Autovista Group |
| Replacement value (valor de reemplazo, seguros) | 1 | autobiz (autobiz Group) |
| Repo agent & vehicle release management | 1 | Mahindra First Choice Wheels (MFCWL) |
| report_average_dom | 1 | MarketCheck (MarketCheck Cars Inc) |
| report_average_price | 1 | MarketCheck (MarketCheck Cars Inc) |
| Report: CarGurus Intelligence Report (monthly dealer-facing) | 1 | CarGurus |
| Report: Consumer Insights Report (annual survey 3000+ buyers/sellers) | 1 | CarGurus |
| report_date | 1 | Stat.vin (1VIN STAT) |
| report_ev_share_percent | 1 | MarketCheck (MarketCheck Cars Inc) |
| Report generation date / fecha del informe | 1 | autoDNA |
| Report ID | 1 | Mahindra First Choice Wheels (MFCWL) |
| report_price_band_distribution | 1 | MarketCheck (MarketCheck Cars Inc) |
| Report reference number | 1 | CCC Intelligent Solutions |
| Report Run Date/Time | 1 | AutoCheck (by Experian) |
| report_total_listings | 1 | MarketCheck (MarketCheck Cars Inc) |
| report_total_rooftops | 1 | MarketCheck (MarketCheck Cars Inc) |
| report_url | 1 | Vehicle Databases |
| report.source.build_data | 1 | AutoGrab |
| report.source.ppsr | 1 | AutoGrab |
| report.source.valuation | 1 | AutoGrab |
| report.source.vehicle_details | 1 | AutoGrab |
| Reporte de recuperación (vehículo recuperado) | 1 | REPUVE — Registro Público Vehicular |
| Reporting entity address | 1 | NMVTIS / VehicleHistory.gov |
| Reporting entity category | 1 | ClearVin |
| Reporting entity contact (phone/email) | 1 | ClearVin |
| Reporting entity contact info | 1 | NMVTIS / VehicleHistory.gov |
| Reporting entity name | 1 | ClearVin |
| Reporting entity type (Individual / Insurer / Recycler / Salvage Pool / Shredder) | 1 | NMVTIS / VehicleHistory.gov |
| Repossessed flag | 1 | Experian Automotive (AutoCheck) |
| Repossession stock status | 1 | Autorola |
| representación gráfica de KPI | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| representación métrica de KPI | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Repricing advice | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| repricing recommendation | 1 | INDICATA (Autorola Group) |
| Reprise (estimation) | 1 | La Centrale |
| Request number (report ID) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| requestDate | 1 | Datium Insights |
| Requested-by (client) | 1 | Mahindra First Choice Wheels (MFCWL) |
| requestedDate / returnedDate / href / count (metadatos API) | 1 | Cox Automotive |
| research report snippets | 1 | GlobalData Automotive |
| Reserve | 1 | CLASSIC.COM |
| Reserve price recommendation | 1 | Autorola |
| reserve pricing | 1 | INDICATA (Autorola Group) |
| reserve_tank_capacity | 1 | Vehicle Databases |
| Reserve-met indicator | 1 | Dealer Auction |
| reserved | 1 | mobile.de |
| Residual by vehicle age (1-10 years) | 1 | RedBook |
| Residual sensitivity to incentives | 1 | Black Book (National Auto Research — Hearst) |
| Residual sensitivity to rental penetration | 1 | Black Book (National Auto Research — Hearst) |
| residual-value.custom_ratio | 1 | L'argus (Cote Argus®) |
| residual-value.custom_value | 1 | L'argus (Cote Argus®) |
| residual-value.input.customization_amount (±€) | 1 | L'argus (Cote Argus®) |
| residual-value.input.feature_ids | 1 | L'argus (Cote Argus®) |
| residual-value.input.initial_price | 1 | L'argus (Cote Argus®) |
| residual-value.input.release_at | 1 | L'argus (Cote Argus®) |
| residual-value.input.simulate_at (archive si pasado) | 1 | L'argus (Cote Argus®) |
| residual-value.input.vehicle_id | 1 | L'argus (Cote Argus®) |
| residual-value.manufacturer_price (prix neuf constructor) | 1 | L'argus (Cote Argus®) |
| residual-value.ratio (VR % = valor/prix neuf) | 1 | L'argus (Cote Argus®) |
| residual-value.return_at (fecha retorno) | 1 | L'argus (Cote Argus®) |
| residual-value.value (VR €) | 1 | L'argus (Cote Argus®) |
| residual.initial_kms | 1 | AutoGrab |
| residual.kms | 1 | AutoGrab |
| residual.score | 1 | AutoGrab |
| residual.valuation | 1 | AutoGrab |
| residual.yearly_kms | 1 | AutoGrab |
| responseMetrics: advertViews | 1 | Auto Trader UK (Autotrader Group plc) |
| responseMetrics: naturalAdvertViews | 1 | Auto Trader UK (Autotrader Group plc) |
| responseMetrics: paidPPCAdvertViews | 1 | Auto Trader UK (Autotrader Group plc) |
| responseMetrics: searchViews | 1 | Auto Trader UK (Autotrader Group plc) |
| Rest-BPM (BPM residual usado importado) | 1 | Autotelex B.V. |
| restraint_systems_others | 1 | Vehicle Databases |
| restraint type | 1 | DataOne Software (DataOne, LLC) |
| restraintTypes | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Restrições (Decoder) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Restwaarde actual (current residual value) | 1 | Autotelex B.V. |
| Restwaarde futura (future residual value) | 1 | Autotelex B.V. |
| Resultado de subasta en 48h | 1 | Audatex España (Solera) |
| resumen del tasador (评估师总结) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Retail Accelerator alert: ageing / overage stock | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail Accelerator alert: incorrect pricing | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail Accelerator alert: out-of-strategy vehicle | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail Accelerator alert: valuation change | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail Accelerator: competitor activity review | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail Accelerator: dynamic performance reporting | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail Accelerator: overage policy (plan) | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail Accelerator: pricing policy (plan) | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail Accelerator: required stock turn (plan) | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail ad performance | 1 | VINCUE (DealerCue Automotive Corp.) |
| Retail Back: maximum price to pay (retail - costs - target gross margin) | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail DMS sales transactions (input) | 1 | ACV Auctions |
| Retail equipped value | 1 | ClearVin |
| Retail Intelligence metrics | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Retail photos / AI photo generation | 1 | MAX Digital (ACV MAX) |
| Retail Rating (1-100) | 1 | Auto Trader UK (Autotrader Group plc) |
| Retail sales (units) | 1 | CarNewsChina Data (China EV DataTracker) |
| retail_turnover | 1 | MarketCheck (MarketCheck Cars Inc) |
| retail vs business sales channel | 1 | JATO Dynamics |
| Retail vs wholesale recommendation (por unidad) | 1 | MAX Digital (ACV MAX) |
| Retail/wholesale exit strategy recommendation | 1 | ACV Auctions |
| retailAdverts.price | 1 | Auto Trader UK (Autotrader Group plc) |
| RetailPer4mance: sales experience | 1 | Urban Science |
| RetailPer4mance: traffic | 1 | Urban Science |
| RetailPer4mance: value proposition | 1 | Urban Science |
| Retained value comparison (like-for-like) | 1 | Glass's |
| retained_value_pct (vs RRP) | 1 | AutoGrab |
| Retainer/saved costs (rental) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Retención de valor a 3 años (%) (36 meses / 60.000 km) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| retención de valor a 3 años por motorización (% sobre precio de tarifa) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| [EQUIP·Seguridad] Retrovisor interior antideslumbramiento automático | 1 | km77.com |
| [EQUIP·Seguridad] Retrovisores exteriores con calefacción | 1 | km77.com |
| [EQUIP·Confort] Retrovisores exteriores con memoria | 1 | km77.com |
| [EQUIP·Confort] Retrovisores exteriores orientables eléctricamente | 1 | km77.com |
| [EQUIP·Confort] Retrovisores exteriores plegables eléctricamente | 1 | km77.com |
| Returns | 1 | IAA (Insurance Auto Auctions) |
| Review: Cons | 1 | Edmunds |
| Review: Edmunds says (verdict) | 1 | Edmunds |
| Review: Pros | 1 | Edmunds |
| Review: What's new | 1 | Edmunds |
| rfl_12_month_y1 (road tax) | 1 | AutoGrab |
| rfl_12_month_y2_to_y6 | 1 | AutoGrab |
| rfl_12_month_y2_to_y6_premium | 1 | AutoGrab |
| rfl_6_month_y2_to_y6 | 1 | AutoGrab |
| rfl_6_month_y2_to_y6_premium | 1 | AutoGrab |
| rfrAndComments[]/defects[] (array) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| RicambiCarrozzeria | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| RicambiMeccanica | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| RiduzionePianificata | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| right-hand drive (kierownica-po-prawej-stronie) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Rijklaarprijs | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Rim diameter | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Rim material | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Rim screw-hole circle | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| risicobeoordeling_rdw | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Risikobestand (inventario de riesgo >90 dias, % y EUR/dia) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Risk flag on user value modification | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| risk_models (origination/insurance) | 1 | AutoUncle |
| RisultatoUnivoco | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| RitiroAssoluto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| RitiroPerc | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| RitiroPercListino | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| RitiroPercPAC | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| RMS: profit uplift $/vehículo ($100-200) | 1 | Cox Automotive |
| RMS: Reconditioning Optimization (reparaciones VIN-específicas vía AutoGrade) | 1 | Cox Automotive |
| RMV: projected days to turn (how fast it'll turn) | 1 | VINCUE (DealerCue Automotive Corp.) |
| RMV: projected retail sell price (what it'll sell for) | 1 | VINCUE (DealerCue Automotive Corp.) |
| RMV: recommended price to pay (what to pay) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Road test result (<=10 mi, 70 mph) [128] | 1 | BCA (British Car Auctions) |
| Roadside assistance (AssistFirst) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Roadworthiness issues | 1 | autoDNA |
| roadworthy | 1 | mobile.de |
| ROAS (return on ad spend) | 1 | Urban Science |
| roetfilter_af_fabriek_apk (OVI) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| rollover_rating | 1 | Vehicle Databases |
| RON Rating | 1 | RedBook |
| roof is_two_tone | 1 | DataOne Software (DataOne, LLC) |
| roof primary_rgb_code | 1 | DataOne Software (DataOne, LLC) |
| roof secondary_rgb_code | 1 | DataOne Software (DataOne, LLC) |
| roof_type | 1 | AutoGrab |
| Rooftop-specific pricing | 1 | ACV Auctions |
| Rotazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Rottamazione (allowance achatarramiento) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| RPI like-for-like price growth (%) | 1 | Auto Trader UK (Autotrader Group plc) |
| RPI mix growth (%) | 1 | Auto Trader UK (Autotrader Group plc) |
| rrp_adjustment | 1 | AutoGrab |
| rrp_overwrite | 1 | AutoGrab |
| RTO: Insurer | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| RTO: PUCC Upto | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| RTO: RC Number | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| RTV (Real Time Valuation) | 1 | RedBook |
| RTV Type: Base (base vehicle) | 1 | RedBook |
| RTV Type: Market (option-equipped) | 1 | RedBook |
| rubber price forecast | 1 | GlobalData Automotive |
| Rueckwirkende Bewertung zum Stichtag (valoracion retroactiva a fecha) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Run & Drive status | 1 | Copart, Inc. |
| run_and_drive_status | 1 | Stat.vin (1VIN STAT) |
| Run list position | 1 | OPENLANE |
| Run number | 1 | Manheim |
| Running / side lights | 1 | BCA (British Car Auctions) |
| Running cost per month | 1 | HPI Check (HPI Ltd, a Solera company) |
| Running costs | 1 | cap hpi (CAP + HPI, a Solera company) |
| runs_drives | 1 | Vehicle Databases |
| rupsonderstelconfiguratiecode | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Rutas de conduccion | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| RV ajustado por riesgo (risk outlook del usuario) | 1 | Datium Insights |
| RV benchmark vs competitors | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| RV performance ranking | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| RV predecessor-successor tracking | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| RV pressure | 1 | INDICATA (Autorola Group) |
| RV risk metric | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| RV slice por periodo de tiempo | 1 | Datium Insights |
| RV style & class | 1 | Black Book (National Auto Research — Hearst) |
| RV type (travel trailer/park model/motor home/truck camper/camping trailer) | 1 | Black Book (National Auto Research — Hearst) |
| RV value drivers / trends | 1 | INDICATA (Autorola Group) |
| S.A.M. Alerts (notifica para aprobar) | 1 | ACV Auctions |
| S.A.M. API / S.A.M. UI | 1 | ACV Auctions |
| S.A.M. Bids (proxy automatico 24/7) | 1 | ACV Auctions |
| SAAR (seasonally adjusted annualized rate) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| SAE Automation Level From | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| SAE Automation Level To | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| SAE autonomous level (base) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| safety_assist_score | 1 | carVertical |
| Safety: IIHS ratings [campos NO-VERIFICADO] | 1 | Edmunds |
| Safety: NHTSA ratings [campos NO-VERIFICADO] | 1 | Edmunds |
| safety_overall_star_rating | 1 | carVertical |
| safety_rating_source_org | 1 | carVertical |
| safety_ratings | 1 | iSeeCars |
| safety_score_explanation | 1 | carVertical |
| safetyInfo.condition | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| safetyInfo.description | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| safetyInfo.note | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| safetyInfo.source (e.g. NHTSA) | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| safetyInfo.value (e.g. 5 Star) | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| saldo comercial de vehículos (€) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| saldo comercial total de automoción (€) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Sale channel (Bid Now / Buy Now / Live Online / xBid / EuroShop) | 1 | BCA (British Car Auctions) |
| Sale date/time | 1 | Manheim |
| Sale day of week | 1 | Copart, Inc. |
| sale_document | 1 | Vehicle Databases |
| Sale format (timed / same-day / buy-now) | 1 | Dealer Auction |
| Sale format: 45-min auction (estados Upcoming/Active/Closing/Pending/Purchases, proxy bid) | 1 | OPENLANE |
| Sale format: Open Sale / Timed (programadas) | 1 | OPENLANE |
| Sale format: Simulcast (live, run list exportable, indicador LIVE, auto-bid, join <=1h) | 1 | OPENLANE |
| Sale Info (sale date/time) | 1 | IAA (Insurance Auto Auctions) |
| Sale light (semáforo condición/venta) | 1 | Copart, Inc. |
| Sale light: Blue (title not present) | 1 | Manheim |
| Sale light: Green (free of known major arbitrable defects, ride & drive) | 1 | Manheim |
| Sale light: Green+Yellow (free except announced) | 1 | Manheim |
| Sale light: Red / Limited As-Is | 1 | Manheim |
| Sale light: Yellow / Limited Guarantee (announced condition, limits arbitration) | 1 | Manheim |
| Sale price / hammer price | 1 | Cox Automotive Europe |
| Sale price vs CAP | 1 | Dealer Auction |
| Sale results / run list | 1 | Cox Automotive Europe |
| Sale results CSV download | 1 | Copart, Inc. |
| Sale title state | 1 | Copart, Inc. |
| Sale title type / Title code | 1 | Copart, Inc. |
| Sale type (Bid / Buy Now / OVE Timed 24/7 / Live Sales) | 1 | Manheim |
| sales (direct attribution) | 1 | Urban Science |
| Sales Count | 1 | CLASSIC.COM |
| Sales event history (images/mileage/price/text) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| sales figures per territory | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| sales forecast (7 & 12 year, brand level) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| sales generated | 1 | Urban Science |
| sales_history_date | 1 | Stat.vin (1VIN STAT) |
| sales performance | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| sales potential | 1 | Urban Science |
| sales_time_forecast (expected days to sell) | 1 | AutoUncle |
| sales transactions PII-free (Cross-Sell) | 1 | DataOne Software (DataOne, LLC) |
| Sales type (open/closed-tender/buy-now/bid-or-buy/live/24h) | 1 | Autorola |
| salesperson performance | 1 | Urban Science |
| sampleSize (nº transacciones en la muestra) | 1 | Cox Automotive |
| saved_search_recommendations | 1 | TrueCar |
| Saved searches | 1 | BCA (British Car Auctions) |
| Saved Searches / wish lists | 1 | vAuto |
| Saved-vehicle alerts (comparables/cambios) | 1 | CLASSIC.COM |
| savingText (savings amount vs market) | 1 | AutoUncle |
| Scenario forecast - Inflation | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Scenario forecast - Long-Term Growth | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Scenario forecast - Mild Recession | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Scenario forecast - Severe Recession | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Scenario forecast - Stagnation | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Scenario-based residual - adverse economic | 1 | Black Book (National Auto Research — Hearst) |
| Scenario-based residual - baseline economic | 1 | Black Book (National Auto Research — Hearst) |
| Scenario-based residual - severe/stressed economic | 1 | Black Book (National Auto Research — Hearst) |
| Schade/daños (tasación ampliada) [A] | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Schadenart (tipo de dano) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Schadensakte (expediente digital de siniestro) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Schadstoffklasse (emissions class) | 1 | AutoScout24 |
| Schatting waarde koop (rango mín-máx) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Schatting waarde verkoop (rango mín-máx) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Schedule test drive | 1 | Edmunds |
| Scheduled service items | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Schwacke Tagespreis (daily live-retail price) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Schwacke-Code | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| schwackeCode | 1 | mobile.de |
| Sconti (percentuale o valore assoluto) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Score: Comfort | 1 | Edmunds |
| Score: Driving/Performance | 1 | Edmunds |
| Score factor: Vehicle Class | 1 | AutoCheck (by Experian) |
| Score factor: Vehicle Use and Events | 1 | AutoCheck (by Experian) |
| Score: Interior | 1 | Edmunds |
| Score position (below / within / above range) | 1 | Experian Automotive (AutoCheck) |
| Score: Storage/Utility | 1 | Edmunds |
| Score: Technology | 1 | Edmunds |
| Score: Value/Good Value | 1 | Edmunds |
| Score: Wildcard | 1 | Edmunds |
| scostamento_valutazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| scraped_at | 1 | MarketCheck (MarketCheck Cars Inc) |
| scraped_at_date | 1 | MarketCheck (MarketCheck Cars Inc) |
| scrapedAt / last_updated | 1 | AutoUncle |
| scrappage rate development | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| scrappage schemes | 1 | JATO Dynamics |
| Screen washers (front/rear) | 1 | BCA (British Car Auctions) |
| search_alert (new-match + price-drop) | 1 | AutoUncle |
| Search history en la misma pantalla | 1 | OPENLANE |
| Search Page | 1 | CarGurus |
| Search Rank (e.g. '22 out of 436 based on this search') | 1 | CarGurus |
| Seasonal adjustment | 1 | Manheim |
| Seasonal trend | 1 | cap hpi (CAP + HPI, a Solera company) |
| Seasonal trends | 1 | VINCUE (DealerCue Automotive Corp.) |
| Seasonality | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| seasonally adjusted (SA) volume | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Seat Belt Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Seat Capacity | 1 | RedBook |
| seat_material | 1 | Vehicle Databases |
| seat_type | 1 | Vehicle Databases |
| seatCount / 승차정원 (asientos) | 1 | Encar (엔카닷컴 / Encar.com) |
| seated places (liczba-miejsc-siedzacych) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Seating / seats | 1 | cap hpi (CAP + HPI, a Solera company) |
| seating_capacity / seats | 1 | iSeeCars |
| seating_rows | 1 | DataOne Software (DataOne, LLC) |
| seatingCapacity | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| Seats condition | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| seats photo (front + back) | 1 | Motorway |
| Secondary market performance | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| sector / branch (industry of registrant) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| sector scorecard ranking | 1 | GlobalData Automotive |
| Securitization valuation | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| security_deposit | 1 | Stat.vin (1VIN STAT) |
| Security Watch 'at risk' marker | 1 | HPI Check (HPI Ltd, a Solera company) |
| [EQUIP·Seguridad] Selector de modo de conducción | 1 | km77.com |
| Sell My Car: instant cash offer (<2 min, dealer network / The Car Buying Group UK) | 1 | CarGurus |
| Sell sub-type (To Individual / To Dealer) | 1 | Orange Book Value (OBV) |
| selling price | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| sello de certificación + timestamp + id de transacción (signature/id) | 1 | Fasecolda — Guía de Valores |
| SellType / 판매유형 (일반…) | 1 | Encar (엔카닷컴 / Encar.com) |
| selo Super Preço (5-15% abaixo da FIPE + calidad) | 1 | Webmotors |
| selo Vistoriado (coche inspeccionado) | 1 | Webmotors |
| Semaforo vincoli/gravami (verde/giallo/rosso) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Separation | 1 | Encar (엔카닷컴 / Encar.com) |
| Serie de precios desestacionalizada (descomposición aditiva a 12 meses) | 1 | AUTO1 Group |
| serie de valor multi-año (valueModel[], curva de depreciación observada) | 1 | Fasecolda — Guía de Valores |
| SerieOpzionale | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| SerieOpzionaleProgressivo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Series2 | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Service & maintenance parts | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Service & maintenance price | 1 | Glass's |
| service & parts department profitability (aftersales FinancialView) | 1 | Urban Science |
| service advisor performance | 1 | Urban Science |
| service bay optimization (optimal number of bays) | 1 | Urban Science |
| Service cost benchmarking | 1 | Glass's |
| Service cost by term & distance | 1 | cap hpi (CAP + HPI, a Solera company) |
| Service Count | 1 | Experian Automotive (AutoCheck) |
| service_date | 1 | Vehicle Databases |
| service_description (oil change/tire rotation/inspection/repair) | 1 | CARFAX |
| service_fee_450 | 1 | Stat.vin (1VIN STAT) |
| service intervals (mileage e.g. 10000mi / time e.g. 12mo) | 1 | Motorway |
| Service intervals / schedules | 1 | Glass's |
| service_reminders (oil/tire/safety/emission) | 1 | CARFAX |
| service retention rate | 1 | Urban Science |
| Service schedule | 1 | Autovista Group |
| service_type | 1 | Vehicle Databases |
| service-history value adjust | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| service-loyal customer defection | 1 | Urban Science |
| Service-to-acquisition outcome (traded/competitor/returned) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Service/Gate fee | 1 | IAA (Insurance Auto Auctions) |
| Service/repair/maintenance performed | 1 | AutoCheck (by Experian) |
| ServiceCopyCar (alerta VIN duplicado / DUPLICATION) | 1 | Encar (엔카닷컴 / Encar.com) |
| Serviceintervall (intervalo de servicio por km real) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| ServiceMark (EncarMeetgo / EncarDiagnosisP1/P2) | 1 | Encar (엔카닷컴 / Encar.com) |
| Servicing / maintenance record | 1 | Autorola |
| Servicio: Acesso a leilões BCA (sourcing wholesale) | 1 | Standvirtual |
| Servicio: coche por suscripción/renting | 1 | coches.net |
| Servicio del vehículo (particular/público/taxi/alquiler con-sin conductor/escuela/agrícola/obras/escolar/mercancías peligrosas) | 1 | Dirección General de Tráfico (DGT) |
| Servicio: Entrega em casa | 1 | Standvirtual |
| Servicio: Financiación | 1 | coches.net |
| Servicio: Financiamento (cuota mensual ajustable a entrada y plazo; Santander Consumer/Cofidis) | 1 | Standvirtual |
| Servicio: Histórico do veículo (carVertical: accidentes/daños, +40 países, -20%) | 1 | Standvirtual |
| Servicio: Informe de vehículos (historial por matrícula; proveedor no verificado) | 1 | coches.net |
| Servicio: Inspeção (Controlauto: 200-350 parâmetros, custos de reparação estimados) | 1 | Standvirtual |
| Servicio: Serviço de retoma (trade-in) | 1 | Standvirtual |
| [EQUIP·Multimedia] Servicios en la nube | 1 | km77.com |
| [EQUIP·Varios] Servicios remotos | 1 | km77.com |
| ServiziACI | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Set Floor Price (reserve) | 1 | CarOffer (a CarGurus company) |
| Set-to-loan ratio (LTV) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Settlement / total-loss valuation | 1 | cap hpi (CAP + HPI, a Solera company) |
| Settlement figure (total loss) | 1 | Glass's |
| settlement value (insurance) | 1 | INDICATA (Autorola Group) |
| severe service schedule | 1 | DataOne Software (DataOne, LLC) |
| Severidad del daño (Noa) | 1 | autobiz (autobiz Group) |
| share performance impact | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| shopper connections (text/chat leads + map clicks + website visits) | 1 | CarOffer (a CarGurus company) |
| Shopper engagement data | 1 | MAX Digital (ACV MAX) |
| Short-term forecast (1-36 / 3-36 months) | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Short-term forecast value (% ajuste; 1-36 meses productos / 3-60 meses ALG) | 1 | J.D. Power Valuation Services |
| short-term sales forecast / Nowcast (current + next month) | 1 | JATO Dynamics |
| shortlist | 1 | Motorway |
| Shoulder room | 1 | ClearVin |
| shoulder_room_front | 1 | DataOne Software (DataOne, LLC) |
| shoulder_room_rear | 1 | DataOne Software (DataOne, LLC) |
| shoulder_room_third_row | 1 | DataOne Software (DataOne, LLC) |
| Show ratio / buy ratio (lead quality) | 1 | ACV Auctions |
| showroom visits | 1 | Urban Science |
| Side Airbag | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Side Airbag-Rear | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Siegel/Zertifizierung (certified seal, excluido del comparable) | 1 | AutoScout24 |
| sighting.at | 1 | AutoGrab |
| sighting.lead_id | 1 | AutoGrab |
| sighting.listing_title | 1 | AutoGrab |
| sighting.listing_url | 1 | AutoGrab |
| sigla_combustivel (G / A / D) | 1 | FIPE (Tabela Fipe Veículos) |
| SiglaTipoBatterie | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| sillas eléctricas (electricChairs) | 1 | Fasecolda — Guía de Valores |
| Similare | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Simulcast (puja/compra en vivo online) | 1 | vAuto |
| single bill of sale | 1 | CarOffer (a CarGurus company) |
| single stock photo (full/thumb location) | 1 | DataOne Software (DataOne, LLC) |
| Single-driver modifier — reduces leasing deduction (נהג יחיד) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| sistema de alimentación (foodSystem) | 1 | Fasecolda — Guía de Valores |
| sistema de impresión de etiquetas B2B (fabricantes/concesionarios/talleres/ITV) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| sistemas ADAS (asistencia a la conducción) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Situação cadastral do veículo (Decoder) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Situación de baja (temporal/definitiva) | 1 | Dirección General de Tráfico (DGT) |
| Situación legal / estatus jurídico (vínculo a proceso judicial) | 1 | REPUVE — Registro Público Vehicular |
| size of PARC | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Skill Level (T1/T2/T3) | 1 | GT Motive |
| skip_trace_data_feed | 1 | CARFAX |
| Small Sample Size icon (muestra insuficiente) | 1 | Cox Automotive |
| Small sample size indicator | 1 | Manheim |
| Smart Fields (auto-pull trim/mileage/features) | 1 | vAuto |
| Smart pricing / price guidance | 1 | Cox Automotive Europe |
| Smart Repair / Spot Repair | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| SMART repair items (PDR, alloy refurb, glass, minor paint/trim) | 1 | BCA (British Car Auctions) |
| smart search filters (body type SUV/EV/high-performance, make/model, mileage, age, price, condition) | 1 | Motorway |
| Smart tags (damage annotation) | 1 | Manheim |
| Smartwatch App | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| smog_rating | 1 | Vehicle Databases |
| Smyle: Festpreis (fixed non-negotiable price) | 1 | AutoScout24 |
| Smyle: Garantie 12 Monate (Allianz warranty) | 1 | AutoScout24 |
| Smyle: Lieferkosten (delivery fee desde 599 EUR) | 1 | AutoScout24 |
| Smyle: TÜV-Restlaufzeit (TÜV validity ≥6m) | 1 | AutoScout24 |
| Smyle: Zustandskriterien (≤6 años / ≤100.000 km) | 1 | AutoScout24 |
| SnapLot 360 (spin 360 interior/exterior + video) | 1 | vAuto |
| Social Plus auto-promotion (high-Standzeit vehicles) | 1 | mobile.de |
| socio-demographic data | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| sociodemographic data | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Sold Listings | 1 | CLASSIC.COM |
| Sold price | 1 | CLASSIC.COM |
| Sold price + (S) sold indicator | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| sold_vins | 1 | MarketCheck (MarketCheck Cars Inc) |
| soldDate | 1 | Autotelex B.V. |
| SONAR Argus Annonces® (anuncios comparables) | 1 | L'argus (Cote Argus®) |
| SONAR Argus Transactions® (transacciones anonimizadas comparables) | 1 | L'argus (Cote Argus®) |
| [EQUIP·Multimedia] Sonido Dynaudio de 12 altavoces | 1 | km77.com |
| soort_erkenning_keuringsinstantie | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| soort_melding_ki_omschrijving | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| soort_toegevoegd_object_omschrijving | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Source (auction house / dealer) + View Source link | 1 | CLASSIC.COM |
| sourceUrl | 1 | AutoUncle |
| sourcing & commodity price forecast (10-year) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Sovralimentazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Speakers | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Special features / equipment (sat-nav, heated seats) | 1 | Dealer Auction |
| Special note | 1 | Copart, Inc. |
| Special-edition texts | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Specialist charge | 1 | GT Motive |
| Specialty equipment/feature adjustment | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Specialty pre-loss market value | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Specifica_custom | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Specifica_hard | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Specifica_medium | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Specifica_soft | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| specifications | 1 | iSeeCars |
| speedControl (cruise control) | 1 | mobile.de |
| SpeseMarketing | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| SpeseRipristino | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| spoorbreedte (ancho de via) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Spot price (current) | 1 | Glass's |
| Spring type | 1 | ClearVin |
| squishVins | 1 | Edmunds |
| Staat/conditie (tasación ampliada) [A] | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| staatscourant_indeling (tarifa) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Stand-in value (seller internal) | 1 | Dealer Auction |
| Standard GVWR | 1 | ClearVin |
| standard tyre sizes | 1 | JATO Dynamics |
| Standard Viewing Angle (2m, 90 +/-45) | 1 | Cox Automotive Europe |
| standard-value (valor a km estándar) | 1 | L'argus (Cote Argus®) |
| standardCurbWeight | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| standardEquipment (equipamiento de serie) | 1 | Autotelex B.V. |
| standardGVWR | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Standardised replacement value (valor de reemplazo estandarizado) | 1 | autobiz (autobiz Group) |
| Standardized appraisals | 1 | ACV Auctions |
| Standardized digital condition summary | 1 | ACV Auctions |
| standardized service naming | 1 | DataOne Software (DataOne, LLC) |
| standardPayload | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| standardTowingCapacity | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| standing buy order / limit order | 1 | CarOffer (a CarGurus company) |
| standing places (liczba-miejsc-stojacych) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Standtage / Standzeit (dias en stock por combustible) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Standtage Wettbewerber (competitor days on market) | 1 | AutoScout24 |
| Standzeitprognose (standing-time forecast, días a venta) | 1 | AutoScout24 |
| Start Code (Run & Drive / Starts / Stationary) | 1 | IAA (Insurance Auto Auctions) |
| Start Date / Modification Date | 1 | GT Motive |
| Start of Production (SOP) date | 1 | GlobalData Automotive |
| Start price | 1 | Autorola |
| Start price recommendation | 1 | Autorola |
| start pricing | 1 | INDICATA (Autorola Group) |
| Start support | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| start-of-sales date | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Start-Stop system | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| starter | 1 | Vehicle Databases |
| State / RTO | 1 | Mahindra First Choice Wheels (MFCWL) |
| State and local fees (title/license/registration, 53k+) | 1 | CCC Intelligent Solutions |
| State Fees (total + Y1-Y5; license, registration, sales tax) | 1 | Kelley Blue Book |
| state_for_pricing (estatal vs nacional) | 1 | AutoGrab |
| State Title Brands check | 1 | Experian Automotive (AutoCheck) |
| Static gear selection | 1 | BCA (British Car Auctions) |
| stationary_soundlevel_db | 1 | AutoGrab |
| stationary_soundlevel_rpm | 1 | AutoGrab |
| statistic.calls | 1 | mobile.de |
| statistic.emails | 1 | mobile.de |
| statistic.impressions | 1 | mobile.de |
| statistic.parkings (watchlist saves) | 1 | mobile.de |
| statistics date (data-statystyki) [Statystyki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Stato/uso del veicolo (ajuste por condicion) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| StatoFirma | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| stats.count | 1 | MarketCheck (MarketCheck Cars Inc) |
| stats.max | 1 | MarketCheck (MarketCheck Cars Inc) |
| stats.mean | 1 | MarketCheck (MarketCheck Cars Inc) |
| stats.median | 1 | MarketCheck (MarketCheck Cars Inc) |
| stats.min | 1 | MarketCheck (MarketCheck Cars Inc) |
| stats.missing | 1 | MarketCheck (MarketCheck Cars Inc) |
| stats.percentiles | 1 | MarketCheck (MarketCheck Cars Inc) |
| stats.stddev | 1 | MarketCheck (MarketCheck Cars Inc) |
| stats.sum | 1 | MarketCheck (MarketCheck Cars Inc) |
| stats.sum_of_squares | 1 | MarketCheck (MarketCheck Cars Inc) |
| 원동기 status (motor) | 1 | Encar (엔카닷컴 / Encar.com) |
| status_date | 1 | MarketCheck (MarketCheck Cars Inc) |
| Steel / crushed-car (scrap) prices | 1 | IAA (Insurance Auto Auctions) |
| Steering | 1 | RedBook |
| Steering Column | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Steering noise (full lock) | 1 | BCA (British Car Auctions) |
| Steering score | 1 | Mahindra First Choice Wheels (MFCWL) |
| Steering system / posicion volante (LHD/RHD) | 1 | autoDNA |
| Stimata | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| stock alerts (matching dealer preferences) | 1 | Motorway |
| Stock alerts sent (count) | 1 | Dealer Auction |
| stock clearance discounts | 1 | JATO Dynamics |
| Stock days / reducción de días en stock (claim de venta rápida) | 1 | AUTO1 Group |
| stock_feed_id | 1 | AutoGrab |
| Stock ID | 1 | Mahindra First Choice Wheels (MFCWL) |
| stock_listing_activity | 1 | carsales (carsales.com.au) |
| stock_no | 1 | MarketCheck (MarketCheck Cars Inc) |
| Stock Optimizer: composition du stock | 1 | La Centrale |
| Stock Optimizer: recommandation de repositionnement/canal | 1 | La Centrale |
| Stock Optimizer: véhicules à rotation lente | 1 | La Centrale |
| Stock photos | 1 | Edmunds |
| Stock Policy match | 1 | Dealer Auction |
| Stock position (posición de stock) | 1 | Autotelex B.V. |
| Stock pricing (Stockview) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| stock trends | 1 | INDICATA (Autorola Group) |
| stock_type (new/used/CPO) | 1 | Cars Commerce (Cars.com Inc.) |
| Stock value (valor de stock) | 1 | Autotelex B.V. |
| stock vs trade recommendation | 1 | INDICATA (Autorola Group) |
| Stock-level decision data (reserve / rerun) | 1 | IAA (Insurance Auto Auctions) |
| Stock/smart alerts | 1 | Cox Automotive Europe |
| stockImage.filename | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Stocking gaps | 1 | VINCUE (DealerCue Automotive Corp.) |
| stocking recommendation (optimum stock to purchase) | 1 | INDICATA (Autorola Group) |
| Stocking strategy alignment | 1 | ACV Auctions |
| Stocking-level recommendation (segun mercado + preferencias + exit strategy) | 1 | Stockwave (vAuto · Cox Automotive) |
| stockNumber | 1 | Autotelex B.V. |
| stockStatus | 1 | Autotelex B.V. |
| Stockwave Max Bid (puja maxima recomendada para cumplir profit goal) | 1 | Stockwave (vAuto · Cox Automotive) |
| Stockwave Strategy Action (indicador numerico +/-) | 1 | Stockwave (vAuto · Cox Automotive) |
| stone chips declaration (mandatory) | 1 | Motorway |
| storage_capacity | 1 | Vehicle Databases |
| Storage cost reduction | 1 | IAA (Insurance Auto Auctions) |
| Storage fee | 1 | IAA (Insurance Auto Auctions) |
| Storico delle revisioni | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| strategic trend indicator (CV) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Strategy grid: historical sales 125-day | 1 | Stockwave (vAuto · Cox Automotive) |
| Strategy grid: overstock vs understock indicator | 1 | Stockwave (vAuto · Cox Automotive) |
| Strategy grid: price class/band (fila) | 1 | Stockwave (vAuto · Cox Automotive) |
| street | 1 | MarketCheck (MarketCheck Cars Inc) |
| Stress-test scenario | 1 | Glass's |
| StringaInterventi | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Structural Condition (rocker panels, pillars, frame) | 1 | Cox Automotive |
| Structured description (overview / exterior condition / interior condition / terms) | 1 | Dealer Auction |
| study_best_value_for_money (5y/10y) | 1 | iSeeCars |
| study_cargo_space_ranking | 1 | iSeeCars |
| study_compared_to_average_multiplier | 1 | iSeeCars |
| study_deals_availability_index (% vs media por mes/festivo) | 1 | iSeeCars |
| study_gas_price_impact_by_state | 1 | iSeeCars |
| study_most_popular_used_cars_by_city_state | 1 | iSeeCars |
| study_percent_chance_reaching_250000_miles (longevidad) | 1 | iSeeCars |
| study_reliability_rating | 1 | iSeeCars |
| study_resale_value_percent | 1 | iSeeCars |
| study_safety_ranking | 1 | iSeeCars |
| study_towing_capacity_ranking | 1 | iSeeCars |
| studyPrice.activeSafetyFeatures | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| studyPrice.passiveSafetyFeatures | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| style_id | 1 | DataOne Software (DataOne, LLC) |
| style name | 1 | Edmunds |
| styleDescription | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| styleName | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Styles | 1 | Copart, Inc. |
| sub-style | 1 | Auto Trader UK (Autotrader Group plc) |
| Subcanal de venta | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| subcategorie_nederland | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| subcategorie_voertuig_europees | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| subdivision | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Submittal type (565/566) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| submodel.body | 1 | Edmunds |
| submodel.full-nicename | 1 | L'argus (Cote Argus®) |
| submodel.modelName | 1 | Edmunds |
| submodel.name | 1 | L'argus (Cote Argus®) |
| submodel.niceName | 1 | Edmunds |
| submodel.position-quote | 1 | L'argus (Cote Argus®) |
| submodel.short-nicename | 1 | L'argus (Cote Argus®) |
| Subprime green light | 1 | vAuto |
| subscribeCount / 찜 (favoritos) | 1 | Encar (엔카닷컴 / Encar.com) |
| Subseries | 1 | Manheim |
| subtitle (version/variant) | 1 | AutoUncle |
| Subtotal | 1 | Audatex España (Solera) |
| subtype (tipo de valor) | 1 | L'argus (Cote Argus®) |
| Suchaufrufe / Suchanfragen (search impressions) | 1 | AutoScout24 |
| Suggested price moves (raise/lower) | 1 | ACV Auctions |
| Sum Insured / premium-setting input | 1 | RedBook |
| Sum of comparables ($) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Sun Roof | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Sundry parts (% / importe / importe max) | 1 | GT Motive |
| sunroof (Schiebedach) | 1 | mobile.de |
| Sunroof / moonroof operation | 1 | OPENLANE |
| Sunroof addition (גג נפתח / סאן רוף) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Superficie de pintura (dm²) | 1 | Audatex España (Solera) |
| Supermarket value (channel-segmented retail) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Superseded part identification | 1 | Glass's |
| Superseded title flag | 1 | NMVTIS / VehicleHistory.gov |
| Supplier order status | 1 | Autorola |
| supplier performance | 1 | GlobalData Automotive |
| SureCheck: brakes check | 1 | Manheim UK |
| SureCheck: claims period 7 days / 250 miles | 1 | Manheim UK |
| SureCheck: direccion | 1 | Cox Automotive Europe |
| SureCheck: frenos | 1 | Cox Automotive Europe |
| SureCheck: inspector accreditation (IMI-approved / NAMA-accredited) | 1 | Manheim UK |
| SureCheck level cars: Bronze / Silver / Gold / EV | 1 | Manheim UK |
| SureCheck level LCV: LCV / LCV-EV | 1 | Manheim UK |
| SureCheck: non-invasive multi-point mechanical check | 1 | Manheim UK |
| SureCheck: safety & operational standards checklist (pass/fail) | 1 | Manheim UK |
| SureCheck: steering check | 1 | Manheim UK |
| SureCheck: transmision/caja | 1 | Cox Automotive Europe |
| SureCheck: up to 56 check points | 1 | Manheim UK |
| Surgical comp sets (trim/build/options drill-down) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Suspensión delantera: estructura | 1 | km77.com |
| Suspensión delantera: resorte | 1 | km77.com |
| suspensión trasera (rearSuspension) | 1 | Fasecolda — Guía de Valores |
| Suspensión trasera: estructura | 1 | km77.com |
| Suspensión trasera: resorte | 1 | km77.com |
| suspension_date | 1 | HistoVec |
| suspension_motif | 1 | HistoVec |
| suspension_remise_du_titre | 1 | HistoVec |
| suspension_retrait_du_titre | 1 | HistoVec |
| Suspension score | 1 | Mahindra First Choice Wheels (MFCWL) |
| suspension_type_front_cont | 1 | Vehicle Databases |
| Suspicious non-disclosure detection | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Swiss Stammnummer linking | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| SWOT analysis (RV Report OEM) | 1 | Autotelex B.V. |
| Symboling (insurance) | 1 | Black Book (National Auto Research — Hearst) |
| Syndication (500+ third-party integrations) | 1 | ACV Auctions |
| Syndication a 500+ sitios de 3os (CarGurus, Cars.com, Autotrader) | 1 | MAX Digital (ACV MAX) |
| Syndication channels/status (Google/Facebook/Instagram/marketplaces) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Syndication targets (web dealer + Autotrader + terceros) | 1 | vAuto |
| synthese_situation_administrative (veredicto Rien a signaler / anomalie) | 1 | HistoVec |
| System errors | 1 | ACV Auctions |
| systemId | 1 | Datium Insights |
| Türen (doors) | 1 | AutoScout24 |
| tabela_de_referencia (parâmetro de entrada: mês/ano) | 1 | FIPE (Tabela Fipe Veículos) |
| tacómetro (tachometer) | 1 | Fasecolda — Guía de Valores |
| tachographCard.cardExpiryDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| tachographCard.cardNumber | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| tachographCard.cardStartOfValidityDate | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| tachographCard.cardStatus | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| Tailgate electric window | 1 | BCA (British Car Auctions) |
| Tamano de mercado y penetracion EV | 1 | Eurotax (JD Power / Autovista Group) |
| tank_1_capacity | 1 | DataOne Software (DataOne, LLC) |
| tank_2_capacity | 1 | DataOne Software (DataOne, LLC) |
| tank_capacity | 1 | Vehicle Databases |
| tank.fuel | 1 | L'argus (Cote Argus®) |
| tank.fuel-total-capacity | 1 | L'argus (Cote Argus®) |
| tank.hydrogen | 1 | L'argus (Cote Argus®) |
| [EQUIP·Decoración] Tapicería de cuero | 1 | km77.com |
| tapicería en cuero SI/NO (upholsteryLeatherShow) | 1 | Fasecolda — Guía de Valores |
| Targa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TargaEstera | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TargaPrecedente | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Target gross margin (input) | 1 | Auto Trader UK (Autotrader Group plc) |
| Target group (fleet/retail) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| tarief (EUR) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| tariefclustering | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| tarifa / precio del distintivo (IVA incl.) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Tarifa €/hora de mano de obra | 1 | Audatex España (Solera) |
| Tarifa de (mes/año) | 1 | km77.com |
| task workflow status (notifications/escalations) | 1 | Urban Science |
| taxClass | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| taxes & fees (total loss) | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| taxi_indicator | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Taxi valuation basis / deduction (מונית) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| taxonomy: bodyTypes | 1 | Auto Trader UK (Autotrader Group plc) |
| taxonomy: cabTypes | 1 | Auto Trader UK (Autotrader Group plc) |
| taxonomy: fuelTypes | 1 | Auto Trader UK (Autotrader Group plc) |
| taxonomy: styles / subStyles | 1 | Auto Trader UK (Autotrader Group plc) |
| taxonomy: vehicleTypes | 1 | Auto Trader UK (Autotrader Group plc) |
| taxonomy: wheelbaseTypes | 1 | Auto Trader UK (Autotrader Group plc) |
| TCPA consent | 1 | Accu-Trade (AccuTrade) |
| tech-feature price premium (+91% in 2025) | 1 | Motorway |
| Technical specifications | 1 | Copart, Inc. |
| technicalSpec.group | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| technicalSpec.header | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| technicalSpec.measurementUnit | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| technicalSpec.title | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| technicalSpec.value.condition | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| technician performance | 1 | Urban Science |
| technician staffing requirement | 1 | Urban Science |
| technisch_toegestane_maximum_aslast | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| technisch_toelaatbaar_massa_koppelpunt | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| technisch_toelaatbaar_maximum_massa_rupsbandset | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| technische_max_massa_voertuig | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| technology | 1 | Vehicle Databases |
| technology & convenience add-ons (VINView Pro) | 1 | JATO Dynamics |
| technology_features | 1 | TrueCar |
| [EQUIP·Confort] Techo solar panorámico | 1 | km77.com |
| techo solar/sunroof SI/NO (sunroofShow) | 1 | Fasecolda — Guía de Valores |
| techSpec.description | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| techSpec.id | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| techSpec.name | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| techSpec.nameNoBrand | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| techSpec.rankingValue | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| techSpec.unitOfMeasure | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| techSpec.value | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Tecnología de pintura (Solvent M.S./base agua) | 1 | Audatex España (Solera) |
| Telematikdaten / Live-Kilometer (telematica km en vivo) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Tell-Tale icons | 1 | Manheim |
| tellerstandoordeel (juicio km: Logisch/Onlogisch/Geen oordeel) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Tempi di giacenza media nel web (days-on-web) per allestimento | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Tempi di riparazione carrozzeria | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Tempi di riparazione meccanica | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Tempo di ricarica (EV) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| TempoRicaricaMinuti | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TempoRicaricaOre | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TempoRicaricaRapidaMin | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TempoRicaricaSecondi | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Ten (10) pricing proof points | 1 | MAX Digital (ACV MAX) |
| tenaamstellen_mogelijk | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Tendencia de niveles de restwaarde (mensual) | 1 | Autotelex B.V. |
| Tender proposal (propuesta de licitación seguros) | 1 | Autotelex B.V. |
| TensioneRicaricaRapida | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TensioneRicaricaVolt | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TensioneTotaleBatterie | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Term (financiacion) | 1 | Cox Automotive Europe |
| termination (network action) | 1 | Urban Science |
| territorial encroachment detection | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| terugroep_code_status (O=abierta/P=reparada) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| terugroep_merk | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| terugroep_status | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| terugroep_type | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| test_drive_booking | 1 | AutoUncle |
| Tested: 0-60 acceleration | 1 | Edmunds |
| Tested: braking distance | 1 | Edmunds |
| testResult (PASSED/FAILED/null) | 1 | GOV.UK MOT History & DVLA Vehicle Enquiry |
| Tetto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Text overlays (warranty/cert/pricing) | 1 | vAuto |
| tgk_aantalwielen | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| tgk_voertuigcategorie | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| thematic scorecard score (company x theme) | 1 | GlobalData Automotive |
| theme map (top 10 themes: tech/macro/industry/ESG) | 1 | GlobalData Automotive |
| theme market size & growth forecast | 1 | GlobalData Automotive |
| theme timeline | 1 | GlobalData Automotive |
| Third-party pricing comparisons | 1 | ACV Auctions |
| Third-party pricing data | 1 | ACV Auctions |
| Third-party private-party leads (KBB ICO) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Thousands of images per drive-through (VIPER) | 1 | ACV Auctions |
| thread_size | 1 | Vehicle Databases |
| Tiempo de carga (EV) | 1 | Eurotax (JD Power / Autovista Group) |
| Tiempo de conduccion | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| tiempo de entrega (35-45 dias) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Tiempo en UT (unidades de trabajo) | 1 | Audatex España (Solera) |
| Tiempos de servicio OEM | 1 | Eurotax (JD Power / Autovista Group) |
| tiempos y baremos de reparación | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Tiempos y baremos de reparacion (ES) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Tier 1 sales attribution lift | 1 | Urban Science |
| Tier 2 sales attribution lift | 1 | Urban Science |
| tijdstip_laatste_tenaamstelling (OVI) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Time left / countdown dinámico | 1 | Copart, Inc. |
| Time remaining | 1 | OPENLANE |
| time_to_prep | 1 | MarketCheck (MarketCheck Cars Inc) |
| Time-to-line | 1 | VINCUE (DealerCue Automotive Corp.) |
| Time-to-line / recon days (2.8 dias mas rapido) | 1 | vAuto |
| Timeline: Data Source (State Agency/Motor Vehicle Dept./Auto Insurance Source/Police Report/Auction) | 1 | AutoCheck (by Experian) |
| Timeline: Details/Event description | 1 | AutoCheck (by Experian) |
| Timeline efficiencies | 1 | IAA (Insurance Auto Auctions) |
| Timeline: Event Date | 1 | AutoCheck (by Experian) |
| timeline_event_records | 1 | carVertical |
| Timeline: service entry / piezas reemplazadas | 1 | autoDNA |
| Timeline: vehicle use - leasing/fleet | 1 | autoDNA |
| Timeline: vehicle use - rental | 1 | autoDNA |
| Timeline: vehicle use - taxi | 1 | autoDNA |
| timestamp | 1 | Datium Insights |
| tipo (novo / seminovo / usado) | 1 | Webmotors |
| tipo de caja mecánica/automática (typeBox) | 1 | Fasecolda — Guía de Valores |
| Tipo de combustível | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| tipo de dirección hidráulica/eléctrica (typeAddress) | 1 | Fasecolda — Guía de Valores |
| tipo de energia (燃油/新能源) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| tipo de faros halógeno/LED (typeHeadlights) | 1 | Fasecolda — Guía de Valores |
| tipo de frenos (brakes) | 1 | Fasecolda — Guía de Valores |
| tipo de listado (sealed-bid auction / live auction / buy-it-now) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| Tipo de mercado nautico (nuevo/ocasion/importacion) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Tipo de moto/ciclomotor | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Tipo de motorización (BEV/PHEV/HEV/gasolina/diésel) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Tipo de pintura (bicapa metálico/sólido) | 1 | Audatex España (Solera) |
| Tipo de pricing (ranged vs gp) | 1 | Accu-Trade (AccuTrade) |
| tipo de transmision (变速箱 MT/AT) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| tipo de vehículo: Autobuses | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| tipo de vehículo: Comercial ligero | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| tipo de vehículo: Industriales | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| tipo de vehículo: Motos/Ciclos/Quad | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| tipo de vehículo: Tractores | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| tipo de vehículo: Turismos | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Tipo di corrente (EV) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Tipo di fase (EV) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Tipo di passaggio di proprieta | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| tipo_veiculo (1=carro, 2=moto, 3=caminhão) | 1 | FIPE (Tabela Fipe Veículos) |
| Tipo y duración de carga | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| TipoCarrozzeria | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipoCatalizzatore | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipoCategoria | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipoCombustibile | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipoGuida | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipoIbridazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipoImpianto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipologiaCorrentePresa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipologiaDocumento | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipologiaTagliando | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TipoSovralimentazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| [EQUIP·Decoración] Tiradores de puertas retráctiles eléctricamente | 1 | km77.com |
| Tire condition scan (precision 1/32 pulgada) | 1 | MAX Digital (ACV MAX) |
| Tire photos | 1 | ACV Auctions |
| Tire Pressure Monitor | 1 | ClearVin |
| Tire Pressure Monitoring System (TPMS) Type | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Tire tread % remaining | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Tire tread depth to nearest 1/32" (4 tires) | 1 | ACV Auctions |
| Tire tread images | 1 | IAA (Insurance Auto Auctions) |
| Tires & Wheels (tamaño/condición/precio) | 1 | Cox Automotive |
| Title / Sale Document | 1 | IAA (Insurance Auto Auctions) |
| title_check_branding | 1 | MarketCheck (MarketCheck Cars Inc) |
| title_description | 1 | Vehicle Databases |
| title fee | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| title_history | 1 | Stat.vin (1VIN STAT) |
| title information / title brands | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| title_issue_date | 1 | CARFAX |
| Title issue date / last title date | 1 | NMVTIS / VehicleHistory.gov |
| title_issued_or_updated | 1 | Stat.vin (1VIN STAT) |
| Title issues / branding (history factor) | 1 | Canadian Black Book |
| title processing status / time | 1 | CarOffer (a CarGurus company) |
| Title Procurement (state title law) | 1 | IAA (Insurance Auto Auctions) |
| title_record | 1 | Vehicle Databases |
| title_state | 1 | CARFAX |
| title_status | 1 | Vehicle Databases |
| Title status / title history | 1 | ACV Auctions |
| Title status / Title Tracker | 1 | IAA (Insurance Auto Auctions) |
| Title status / tracking (Title Express) | 1 | Copart, Inc. |
| Title transferred to insurer name | 1 | AutoCheck (by Experian) |
| title_type | 1 | Vehicle Databases |
| Title type / event (original, duplicate, lien release, transfer, superseded) | 1 | NMVTIS / VehicleHistory.gov |
| title_washing_alert_police | 1 | CARFAX |
| title_washing_flag | 1 | CARFAX |
| titulaire_code_postal | 1 | HistoVec |
| titulaire_identite_nom_anonymise (particulier) | 1 | HistoVec |
| titulaire_prenoms_anonymises | 1 | HistoVec |
| titulaire_raison_sociale_anonymisee (personne morale) | 1 | HistoVec |
| titulaire_siren_anonymise | 1 | HistoVec |
| TMU flag (True Mileage Unknown) | 1 | CLASSIC.COM |
| TMV national price | 1 | Edmunds |
| tmvRecommendedRating | 1 | Edmunds |
| toegestane_maximum_massa_voertuig | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| toerental_geluidsniveau | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| [EQUIP·Confort] Toma de 12 voltios | 1 | km77.com |
| Top 100 Markets ranking (crecimiento YoY del CMB) | 1 | CLASSIC.COM |
| Top bidder | 1 | OPENLANE |
| top_features | 1 | TrueCar |
| Top models by CAP Clean | 1 | Dealer Auction |
| Top models by margin | 1 | Dealer Auction |
| Top Rated Awards (Car/SUV/Truck + EV + Best of the Best) | 1 | Edmunds |
| Top Sale (Highest Sale) | 1 | CLASSIC.COM |
| top_speed_mph | 1 | AutoGrab |
| top VC deal trends | 1 | GlobalData Automotive |
| topSpeedMPH | 1 | Auto Trader UK (Autotrader Group plc) |
| torque_derived_from | 1 | AutoGrab |
| torque_lbft | 1 | AutoGrab |
| torque_nm | 1 | AutoGrab |
| torqueRPM | 1 | Autotelex B.V. |
| totaal_aantal_voertuigen_terugroepactie | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| TOTAL | 1 | Audatex España (Solera) |
| total acquisition cost (WLTP: incl registration + tax) | 1 | JATO Dynamics |
| total_active_cars_for_ymmt | 1 | MarketCheck (MarketCheck Cars Inc) |
| total API method calls per day (laczna-ilosc-wyswietlen) [Statystyki] | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Total breakdown: Labour total | 1 | GT Motive |
| Total breakdown: Paint total | 1 | GT Motive |
| Total breakdown: Parts total | 1 | GT Motive |
| Total Car Check valuation | 1 | Motorway |
| total_cars_sold_in_last_45_days | 1 | MarketCheck (MarketCheck Cars Inc) |
| Total Connections (leads count) | 1 | CarGurus |
| Total cost estimate by zip | 1 | IAA (Insurance Auto Auctions) |
| Total cost to acquire (buy fee + transporte + recon) | 1 | Stockwave (vAuto · Cox Automotive) |
| Total cost to acquire (buy fee + transporte + recon) vs retail target | 1 | vAuto |
| Total cost to bidder (₹) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Total horas de reparación (UTS -> h/min) | 1 | Audatex España (Solera) |
| Total Listings | 1 | CLASSIC.COM |
| Total M.O. | 1 | Audatex España (Solera) |
| Total M.O. CH/MEC (UT + €) | 1 | Audatex España (Solera) |
| total number of seats/places (liczba-miejsc-ogolem) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| Total piezas (nº + importe) | 1 | Audatex España (Solera) |
| Total pintura | 1 | Audatex España (Solera) |
| Total € por operación | 1 | Audatex España (Solera) |
| total_price | 1 | Vehicle Databases |
| Total Saves (shopper saves count) | 1 | CarGurus |
| Total torque (Nm) | 1 | CarNewsChina Data (China EV DataTracker) |
| Total Varios | 1 | Audatex España (Solera) |
| Total-loss recommendation (reparar vs pérdida total) | 1 | Copart, Inc. |
| Total-loss threshold, varies by use (אובדן גמור/להלכה) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Total-loss weighted score (Loss Advisor) | 1 | IAA (Insurance Auto Auctions) |
| Totale_db | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TotaleManoOpera | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TotaleRicambi | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| TotaleTagliando | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Totalschaden (flag de siniestro total) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| touch-up paint code (mfr code) | 1 | DataOne Software (DataOne, LLC) |
| Touchscreen | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Touchscreen Size | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Tow Away Alert | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| tow_capacity_lb | 1 | Vehicle Databases |
| tow hook / hitch fitted (hak) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| tow_status | 1 | Vehicle Databases |
| Towing agency | 1 | ClearVin |
| Towing suggestion (drivable vs needs tow) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| town | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| tracción delantera/trasera/total (traction) | 1 | Fasecolda — Guía de Valores |
| Tracking de pujas en tiempo real / mejor puja | 1 | autobiz (autobiz Group) |
| Traction Control | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Traction pack diagnostics | 1 | BCA (British Car Auctions) |
| trade / wholesale price | 1 | INDICATA (Autorola Group) |
| Trade Average value (CAP Average) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Trade Below Average value (CAP Below) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Trade Capture report | 1 | Accu-Trade (AccuTrade) |
| Trade Clean value (CAP Clean) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Trade destination assignment (trade/subasta/sucursal) | 1 | Autotelex B.V. |
| Trade valuation (value excluding margin) | 1 | Auto Trader UK (Autotrader Group plc) |
| tradeAdverts.price | 1 | Auto Trader UK (Autotrader Group plc) |
| TradeGrade (point-of-appraisal bid/grade) | 1 | CarOffer (a CarGurus company) |
| trail | 1 | Vehicle Databases |
| trailer attachment type | 1 | DataOne Software (DataOne, LLC) |
| trailer detail | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| trailer subtype | 1 | DataOne Software (DataOne, LLC) |
| trailer type | 1 | DataOne Software (DataOne, LLC) |
| Trailer Type Connection | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Tramos de eslora | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Transaccional: Autopago (escrow comprador-vendedor) | 1 | Webmotors |
| Transaccional: CarDelivery (compra 100% online) | 1 | Webmotors |
| Transaccional: Troca+Troco (cambio + diferencia en dinero) | 1 | Webmotors |
| transaction / sales price (dealer, anonymised) | 1 | JATO Dynamics |
| transaction price | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Transactions table (30-day sample, up to 100 comparables) | 1 | Manheim |
| Transactions table - condition | 1 | Cox Automotive |
| Transactions table - sale date | 1 | Cox Automotive |
| Transactions table - sale price | 1 | Cox Automotive |
| Transfer disclosure requirements (app movil) | 1 | Accu-Trade (AccuTrade) |
| Transferencias (cambios de titularidad VO) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Transmisión (del VIN) | 1 | Audatex España (Solera) |
| Transmisión: Número de relaciones/marchas | 1 | km77.com |
| Transmisión: Tipo de embrague | 1 | km77.com |
| Transmisión: Tipo de mando | 1 | km77.com |
| Transmisión: Tipo de mecanismo | 1 | km77.com |
| Transmisión: Tipo de tracción | 1 | km77.com |
| Transmissie | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Transport cost (en Bill of Sale, floorplanable) | 1 | ACV Auctions |
| Transport costs | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Transport VAT | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| transportation / delivery (distancia ~600mi / ~7 dias) | 1 | CarOffer (a CarGurus company) |
| Transportation cost | 1 | vAuto |
| Transportation cost estimate | 1 | Stockwave (vAuto · Cox Automotive) |
| Trasmissione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Trazione | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Trended historic valuation (6 months back) | 1 | Auto Trader UK (Autotrader Group plc) |
| trending influencer content | 1 | GlobalData Automotive |
| Trending Markets por tramo de precio (<$40K, <$100K, $100K–$500K, $500K–$1M, >$1M) | 1 | CLASSIC.COM |
| Treno | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| [EQUIP·Seguridad] Tres reposacabezas traseros | 1 | km77.com |
| Triage recommendation (total loss vs repairable) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Trigger: auction announcement | 1 | Experian Automotive (AutoCheck) |
| Trigger: Buyback Protection eligibility | 1 | Experian Automotive (AutoCheck) |
| Trigger: CPO eligibility | 1 | Experian Automotive (AutoCheck) |
| Trigger: portfolio analysis | 1 | Experian Automotive (AutoCheck) |
| Trigger: vehicle repossession | 1 | Experian Automotive (AutoCheck) |
| Trim2 | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| trimLine | 1 | mobile.de |
| truck age (antiguedad) | 1 | Datium Insights |
| truck asset description (descripcion detallada) | 1 | Datium Insights |
| Truck class code & name (Class 4-8) | 1 | Black Book (National Auto Research — Hearst) |
| truck detail | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| truck photos (fotos del activo) | 1 | Datium Insights |
| truck salePrice (precio de venta real) | 1 | Datium Insights |
| true_cash_offer_valid_3_days | 1 | TrueCar |
| True/Fair market value (IBB) | 1 | Mahindra First Choice Wheels (MFCWL) |
| truecar_price_estimate | 1 | TrueCar |
| trunk_volume | 1 | Vehicle Databases |
| Trust flags (ExtendWarranty / HomeService) | 1 | Encar (엔카닷컴 / Encar.com) |
| tsb_date | 1 | Vehicle Databases |
| tsb_number | 1 | Vehicle Databases |
| tsb_pdf | 1 | Vehicle Databases |
| tsb_summary | 1 | Vehicle Databases |
| tsb_title | 1 | Vehicle Databases |
| TSN (Typschluesselnummer) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| ttl.cityTax | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| ttl.countyTax | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| ttl.federalTax | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| ttl.stateTax | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Turbo | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Turbo Charger | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| turn-time goal | 1 | CarOffer (a CarGurus company) |
| turn-time performance (5x vs competidores) | 1 | CarOffer (a CarGurus company) |
| turning_circle | 1 | DataOne Software (DataOne, LLC) |
| Turning diameter | 1 | ClearVin |
| Turning Radius | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Turnover data | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Tutela (titular menor de edad / tutela judicial — COD_TUTELA) | 1 | Dirección General de Tráfico (DGT) |
| tweede_kleur | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Tweeters | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| type | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| type_approval_category | 1 | AutoGrab |
| type_carrosserie_europese_omschrijving | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Type d'utilisateur (acheteur/vendeur) | 1 | La Centrale |
| type_de_reception | 1 | HistoVec |
| Type de véhicule | 1 | La Centrale |
| Type de vendeur (Particulier / Professionnel / Pro vérifié) | 1 | La Centrale |
| type designation (typ) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| type_gasinstallatie | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Type name | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| type of car (SUV / marca lujo / segmento) | 1 | Datium Insights |
| type_remsysteem_voertuig_code | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| type-subtype-purpose code (kod-rodzaj-podrodzaj-przeznaczenie) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| typeaanduidingfabrikant | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| typegoedkeuringsnummer | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Typical Value — National | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Typical Value — State | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Tyre condition | 1 | Autorola |
| Tyre condition (%) / tyre life per wheel | 1 | Mahindra First Choice Wheels (MFCWL) |
| Tyre cost | 1 | Autovista Group |
| tyre cracked / split flag (perished) | 1 | Motorway |
| Tyre cross-section (ratio) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Tyre design | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Tyre diameter | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Tyre load rating | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Tyre prices (SMR) | 1 | cap hpi (CAP + HPI, a Solera company) |
| Tyre profile | 1 | cap hpi (CAP + HPI, a Solera company) |
| Tyre replacement timing & cost | 1 | HPI Check (HPI Ltd, a Solera company) |
| Tyre Services (tarifas pactadas) | 1 | GT Motive |
| Tyre Size | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Tyre speed index (ECE) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Tyre tread depth (per tyre x 3 points) | 1 | BCA (British Car Auctions) |
| tyre tread depth & condition | 1 | Motorway |
| tyre tread photos (head-on front + back) | 1 | Motorway |
| Tyre Type | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Tyre wall observations (cuts/wear/punctures/canvas) | 1 | BCA (British Car Auctions) |
| tyre.construction-type | 1 | L'argus (Cote Argus®) |
| tyre.front | 1 | L'argus (Cote Argus®) |
| tyre.front-sizes.aspect-ratio | 1 | L'argus (Cote Argus®) |
| tyre.front-sizes.radial-construction | 1 | L'argus (Cote Argus®) |
| tyre.front-sizes.rim-diameter | 1 | L'argus (Cote Argus®) |
| tyre.rear | 1 | L'argus (Cote Argus®) |
| tyre.sparewheel-type | 1 | L'argus (Cote Argus®) |
| tyre.wheel-type | 1 | L'argus (Cote Argus®) |
| 凹み U1/U2/U3 (dent by size) | 1 | USS (ユー・エス・エス) Co., Ltd. |
| Ubicación / país de origen del vehículo | 1 | AUTO1 Group |
| Ubicacion/tracking del vehiculo (ETA) | 1 | Cox Automotive Europe |
| uitlaatemissieniveau | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| uitstoot_deeltjes_licht | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| uitstoot_deeltjes_zwaar | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| uitvoering | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Uitvoering/versie (selección entre coincidencias) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| UK car production | 1 | Cox Automotive Europe |
| ukvd_body_shape | 1 | AutoGrab |
| ukvd_mark | 1 | AutoGrab |
| ukvd_series_desc | 1 | AutoGrab |
| ultimo_prezzo | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Umbral de pérdida total (% sobre valor, ~80%) | 1 | Audatex España (Solera) |
| unbrakedTowingCapacity (sin freno) | 1 | Autotelex B.V. |
| Under-body Coating Matrix (UK) | 1 | GT Motive |
| underBodyPhotos / hasUnderBodyPhoto (fotos de bajos) | 1 | Encar (엔카닷컴 / Encar.com) |
| Undercarriage images | 1 | IAA (Insurance Auto Auctions) |
| Undercarriage photos (Virtual Lift, 2.000+ fotos del bajo) | 1 | ACV Auctions |
| underwriting_rating_data (patented) | 1 | CARFAX |
| Unidades en plan / days on plan | 1 | Cox Automotive Europe |
| unidades producidas (total) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Uniform Condition Adjustment (dealer-ready vs normal-wear) | 1 | CCC Intelligent Solutions |
| Universal Condition Report (deducciones/adiciones itemizadas, consumer-facing) | 1 | Accu-Trade (AccuTrade) |
| Unnamed issue | 1 | Accu-Trade (AccuTrade) |
| up to 6 tracked vehicles (account) | 1 | Motorway |
| Upcoming car price | 1 | Mahindra First Choice Wheels (MFCWL) |
| updated_at | 1 | MarketCheck (MarketCheck Cars Inc) |
| Updated date (recency) | 1 | CLASSIC.COM |
| Upgraded Simulcast (in-app) | 1 | Manheim |
| Upholstery | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| uploadSticky | 1 | mobile.de |
| upstream_vehicle (descripción de la autoridad de matriculación) | 1 | AutoGrab |
| €uropa-Code / Identify-Code (código de identificación del fabricante) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| US: buyback/warranty returns (lemon) | 1 | autoDNA |
| US: current market value / valor de mercado actual | 1 | autoDNA |
| US dismantling shop: scrappage + reporting person | 1 | autoDNA |
| US: GVW (gross vehicle weight) | 1 | autoDNA |
| us_origin_flag | 1 | carVertical |
| US: safety faults | 1 | autoDNA |
| US title records: issuance date | 1 | autoDNA |
| US title records: state | 1 | autoDNA |
| US use: agricultural | 1 | autoDNA |
| US use: police | 1 | autoDNA |
| US use: taxi | 1 | autoDNA |
| US use: test vehicle | 1 | autoDNA |
| usage_classification_personal_rental_commercial_government | 1 | Vehicle Databases |
| usage_fleet | 1 | Vehicle Databases |
| usage history | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| usage_lease | 1 | Vehicle Databases |
| usage_livery | 1 | Vehicle Databases |
| usage patterns / vehicle trends | 1 | GlobalData Automotive |
| Usage Types | 1 | Experian Automotive (AutoCheck) |
| usageType (e.g. CLASSIC) | 1 | mobile.de |
| USB Charger | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| USB Ports | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| USD/CNY exchange rate (dated) | 1 | CarNewsChina Data (China EV DataTracker) |
| Use: Commercial | 1 | Experian Automotive (AutoCheck) |
| Use: Fleet | 1 | Experian Automotive (AutoCheck) |
| Use: Government | 1 | Experian Automotive (AutoCheck) |
| Use: Lease | 1 | Experian Automotive (AutoCheck) |
| Use: Personal | 1 | Experian Automotive (AutoCheck) |
| Use: Police | 1 | Experian Automotive (AutoCheck) |
| Use: Rental | 1 | Experian Automotive (AutoCheck) |
| Use: Taxi | 1 | Experian Automotive (AutoCheck) |
| used_as_driving_school_vehicle | 1 | carVertical |
| used_as_handicap_vehicle | 1 | carVertical |
| used_as_police_vehicle | 1 | carVertical |
| used_as_rental | 1 | carVertical |
| used_as_taxi | 1 | carVertical |
| used_as_transport_vehicle | 1 | carVertical |
| Used Car Fair Purchase Price | 1 | Kelley Blue Book |
| Used car forecast | 1 | Cox Automotive Europe |
| Used car price | 1 | Mahindra First Choice Wheels (MFCWL) |
| Used car transactions | 1 | Cox Automotive Europe |
| Used listing: AI Expert condition/price assessment | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Used listing: Certified badge | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Used listing: Descriptive Summary | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Used listing: Featured Indicator | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Used listing: Kilometers Driven | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Used listing: Original Price | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Used listing: Savings Amount | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Used listing: Sort (Distance/Added Date/Price/Kms/Year) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Used price (current) | 1 | RedBook |
| Used vehicle market value (real-time) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Used Vehicle Retention Index (points) | 1 | Canadian Black Book |
| Used Vehicle Retention Index (UVI) value | 1 | Black Book (National Auto Research — Hearst) |
| Used-car market size (units) | 1 | Mahindra First Choice Wheels (MFCWL) |
| used-car market valuation (via autobiz partner) | 1 | JATO Dynamics |
| Used-vehicle performance | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| usedPrivateParty | 1 | Edmunds |
| User Id (header de auth) | 1 | Datium Insights |
| User Operations (name/code/task/job/qty/price/labour time/group) | 1 | GT Motive |
| User Overall Rating (N reviews) | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| User Ratings and Reviews (de droom.in) | 1 | Orange Book Value (OBV) |
| userId | 1 | Datium Insights |
| Uso previo (previous usage) | 1 | Cox Automotive Europe |
| Usuario creador de la valoracion | 1 | Eurotax (JD Power / Autovista Group) |
| Vía delantera (mm) | 1 | km77.com |
| Vía trasera (mm) | 1 | km77.com |
| V5 document presence (logbook) | 1 | Dealer Auction |
| V5C (logbook) issue date | 1 | HPI Check (HPI Ltd, a Solera company) |
| v5c_qty | 1 | AutoGrab |
| V5C (logbook) serial number | 1 | HPI Check (HPI Ltd, a Solera company) |
| Valet Mode | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Valeur Argus Annonces® (displayed-selling-values, prix d'annonce conseillé) | 1 | L'argus (Cote Argus®) |
| Valeur Argus Transaction® B2B (btob-transaction-values) | 1 | L'argus (Cote Argus®) |
| Valeur Argus Transaction® B2C (btoc-transaction-values) | 1 | L'argus (Cote Argus®) |
| Valeur estimée € (cote) | 1 | La Centrale |
| Valeur résiduelle projetée par année (2026-2030) | 1 | La Centrale |
| validación / captura de expediente | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| validationErrorMessage | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| validVin | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Valor (moto/ciclomotor/quad) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| valor actual del vehículo | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Valor actual del vehiculo | 1 | Eurotax (JD Power / Autovista Group) |
| Valor ajustado por condicion | 1 | Cox Automotive Europe |
| Valor B2B (trade/wholesale) | 1 | autobiz (autobiz Group) |
| Valor B2C (retail profesional a particular) | 1 | autobiz (autobiz Group) |
| Valor base Eurotax (ventas reales nacionales mes anterior) | 1 | Eurotax (JD Power / Autovista Group) |
| Valor C2C (entre particulares) | 1 | autobiz (autobiz Group) |
| valor comercial base (bcpp, miles de COP) | 1 | Fasecolda — Guía de Valores |
| Valor de compra / recompra (trade) | 1 | Eurotax (JD Power / Autovista Group) |
| Valor de cotação / valor comercial atualizado (ValCotacao) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Valor de cotação completo, com opcionais (ValCotacaoCompleto) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Valor de la lectura de kilómetros | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| Valor de mercado a nivel estatal | 1 | Audatex España (Solera) |
| Valor de mercado a nivel nacional | 1 | Audatex España (Solera) |
| valor de mercado del vehículo | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Valor de mercado real | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Valor de mercado VO (precio real de venta profesional→cliente final / retail) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Valor de portfolio / valoracion de flota | 1 | Eurotax (JD Power / Autovista Group) |
| Valor de reposición/replacement value | 1 | Audatex España (Solera) |
| Valor de subasta calculado al céntimo (AUTOonline) | 1 | Audatex España (Solera) |
| valor de tasación / appraisal | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Valor del índice de precios mayorista (puntos, base 100 = ene-2015) | 1 | AUTO1 Group |
| Valor en el pasado (historico) | 1 | Eurotax (JD Power / Autovista Group) |
| Valor fijo (código opcional) | 1 | Audatex España (Solera) |
| valor médio de similares anunciados (above/below market) | 1 | Webmotors |
| Valor Médio Nacional | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Valor Network (venta por distribuidores de la marca) | 1 | autobiz (autobiz Group) |
| valor (preço médio em R$, à vista, mercado nacional, do mês de referência) — único valor, sem split venda/compra | 1 | FIPE (Tabela Fipe Veículos) |
| Valor para comércio e financiamento (contexto legacy) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Valor para consulta/vistoria de sinistro (contexto legacy) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Valor SPOT (oferta VO regional en tiempo real) | 1 | Eurotax (JD Power / Autovista Group) |
| valor Tabela Webmotors (precio medio de mercado real de la plataforma) | 1 | Webmotors |
| Valor Venal | 1 | Audatex España (Solera) |
| valoración a diferentes fechas (retroactiva) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Valoración cross-border por mercado (22 mercados) | 1 | autobiz (autobiz Group) |
| Valoración del vehículo usado (Boletín Blanco) | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Valoración Euro NCAP (estrellas) | 1 | DGT — Informe de Vehículo (Dirección General de Tráfico) |
| valoración masiva / por lotes (stock) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| valoración pre / intermedia / post-proceso | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Valoración VO de vehículos >12 años | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Valoracion actualizada al final de contrato | 1 | Eurotax (JD Power / Autovista Group) |
| Valoracion de equipamiento/extras (depreciacion de opciones) | 1 | Eurotax (JD Power / Autovista Group) |
| Valoracion en tiempo real | 1 | Cox Automotive Europe |
| valoraciones acumuladas (prueba social: 22.578.926 PPP desde 2018; 1M+ requests InstantVal desde 2018) | 1 | Datium Insights |
| Valore commerciale veicolo attuale (lead) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Valore di permuta (trade-in) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Valore residuo accessori non di serie | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Valore veicolo all'ultimo passaggio di proprieta | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| ValoreAcquisto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ValoreAssoluto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ValoreAtto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ValoreCasa | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ValoreInstantWeb | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| ValorePercentuale | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Valores de referencia de mercado | 1 | Eurotax (JD Power / Autovista Group) |
| ValoreVendita | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Valori residui degli accessori | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Valori residui vs listini attuali/storici | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Valori storici Eurotax (serie historica desde 2000) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| valorization.input.business-target (btoc/btob) | 1 | L'argus (Cote Argus®) |
| valorization.input.calculated-for (fecha de cálculo / cote a fecha pasada) | 1 | L'argus (Cote Argus®) |
| valorization.input.feature-ids | 1 | L'argus (Cote Argus®) |
| valorization.input.offer (extended-market-values / past-stock-market-value / personnalisée / frais percent|fixed) | 1 | L'argus (Cote Argus®) |
| valorization.input.released-at (mise en circulation) | 1 | L'argus (Cote Argus®) |
| Valuador input alterno: Matrícula | 1 | Standvirtual |
| Valuador input: Potência (opcional) | 1 | Standvirtual |
| Valuador input: Quilometragem | 1 | Standvirtual |
| Valuador input: Tipo de carroçaria | 1 | Standvirtual |
| Valuador input: Tipo de combustível | 1 | Standvirtual |
| Valuador input: Versão / Motorização | 1 | Standvirtual |
| Valuador: intervalo de preços estimado (rango €, ej. EUR 26.140 - EUR 31.050) | 1 | Standvirtual |
| Valuation amountExcludingVatGBP | 1 | Auto Trader UK (Autotrader Group plc) |
| Valuation amountGBP | 1 | Auto Trader UK (Autotrader Group plc) |
| Valuation amountNoVatGBP (commercial/VI) | 1 | Auto Trader UK (Autotrader Group plc) |
| Valuation certificate | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Valuation date | 1 | cap hpi (CAP + HPI, a Solera company) |
| valuation_input_condition | 1 | carsales (carsales.com.au) |
| Valuation Input: Kilometers driven | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Valuation Input: Overall condition | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| valuation_input_state | 1 | carsales (carsales.com.au) |
| valuation_mode_buying | 1 | carsales (carsales.com.au) |
| valuation_mode_selling | 1 | carsales (carsales.com.au) |
| valuation_mode_trading_in | 1 | carsales (carsales.com.au) |
| Valuation Notes (appraiser + system) | 1 | CCC Intelligent Solutions |
| Valuation ratio (repair cost / value) | 1 | Glass's |
| Valuation Total (Actual Cash Value / ACV) | 1 | CCC Intelligent Solutions |
| valuation.auctionValue | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| valuation.created_at | 1 | AutoGrab |
| valuation.historicalValue | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| valuation.kms | 1 | AutoGrab |
| valuation.loanValue | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| valuation.price | 1 | AutoGrab |
| valuation.pricing_id | 1 | AutoGrab |
| valuation.retailValue | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| valuation.score (confidence 0-1) | 1 | AutoGrab |
| valuation.wholesaleValue | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| valuationType (Auction | Fixed Price | Pickles Go Tenders | Pickles Online | Dealer Retail | Private Retail | Wholesale | Trade In | Wholesale Buy Price) | 1 | Datium Insights |
| value (importe €) | 1 | L'argus (Cote Argus®) |
| value_adjustment_title_brands | 1 | CARFAX |
| value_adjustment_usage_type | 1 | CARFAX |
| Value factors (factores que aumentan/disminuyen valor — B2B) | 1 | Autotelex B.V. |
| Value Index (retail vs MSRP) | 1 | ClearVin |
| Value movement reason / which derivative moved | 1 | cap hpi (CAP + HPI, a Solera company) |
| Value scenario: Buying Privately | 1 | CARFAX Canada |
| Value scenario: Selling Privately | 1 | CARFAX Canada |
| Value scenario: Trading In (with tax savings factored in) | 1 | CARFAX Canada |
| value through equipment changes | 1 | JATO Dynamics |
| value_tracking_over_time | 1 | CARFAX |
| Value trend / direccion (sube o baja) | 1 | Hagerty |
| value-chain position (leader / challenger) | 1 | GlobalData Automotive |
| Value-retention rating (3-year) | 1 | Kelley Blue Book |
| Valutazione_generica | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Valutazione retrodatata (valore a fecha pasada, 2008/2011/2015 segun producto) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Valutazione_specifica | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Valutazione veicolo in permuta | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| valve_gear | 1 | AutoGrab |
| valve_timing | 1 | DataOne Software (DataOne, LLC) |
| Valve Train Design | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| valves | 1 | DataOne Software (DataOne, LLC) |
| ValvolePerCilindro | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Variação de preço mensual % (0km / seminovo / usado) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Variação por idade (por ano modelo) | 1 | Molicar (KBB Brasil — Tabela Molicar) |
| Variable cost | 1 | Autovista Group |
| Variables macroeconomicas | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| variación % del comercio exterior (mensual/semestral/anual) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Variación acumulada en el año del índice (YTD %) | 1 | AUTO1 Group |
| Variación interanual del índice (YoY %) | 1 | AUTO1 Group |
| variación interanual del precio (%) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| Variación mes a mes del índice (MoM %) | 1 | AUTO1 Group |
| Variacion de VR por periodo | 1 | Eurotax (JD Power / Autovista Group) |
| Variacion interanual de precio % (Car Digital Track) | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Variazione valutazioni MoM (mensile) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Variazione valutazioni YoY (annuale) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| VAT amount | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| VAT flag (UK) | 1 | Copart, Inc. |
| VAT-inclusive valuation flag | 1 | cap hpi (CAP + HPI, a Solera company) |
| vatable | 1 | mobile.de |
| vatMargin (BTW/marge) | 1 | Autotelex B.V. |
| vatNumber | 1 | Autotelex B.V. |
| vatRate | 1 | mobile.de |
| VDP views / engagement (+62% VDPs/coche) | 1 | vAuto |
| VED cost for 12 months | 1 | HPI Check (HPI Ltd, a Solera company) |
| Veh Adj (vehicle-description difference adjustment) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| vehículo afectado (VIN / matrícula) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| vehículo eléctrico (matrícula/VIN) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Vehículos comparables | 1 | Audatex España (Solera) |
| vehículos totales transportados (logística) | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Vehicle Affordability Index (semanas de ingreso medio para comprar) | 1 | Cox Automotive |
| Vehicle age / antiguedad | 1 | autoDNA |
| vehicle age distribution | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Vehicle age mix (4-7yr share) | 1 | Mahindra First Choice Wheels (MFCWL) |
| Vehicle archive photos / fotos historicas | 1 | autoDNA |
| Vehicle Aspect (grouping + vehicle count) | 1 | RedBook |
| Vehicle assessment description | 1 | Copart, Inc. |
| Vehicle attractiveness (atractividad del vehículo) | 1 | autobiz (autobiz Group) |
| Vehicle Base Price (typical, market-specific) | 1 | Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation) |
| Vehicle category/body — private/commercial/truck/bus/minibus/van/tow-truck/taxi | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| vehicle class M2/M3 (bus/coach) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| vehicle class N1 (LCV/van) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| vehicle class N2 (medium goods) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| vehicle class N3 (heavy truck) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Vehicle condition / condition report | 1 | vAuto |
| Vehicle condition tier (Below average / Average / Clean) | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Vehicle data source (source / vehicle_source) | 1 | Accu-Trade (AccuTrade) |
| vehicle_description_pros_cons | 1 | TrueCar |
| Vehicle Descriptor | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Vehicle desirability indicator | 1 | Glass's |
| vehicle_detail_page_views | 1 | AutoUncle |
| Vehicle Detail Pages (VDP) | 1 | ACV Auctions |
| Vehicle details (make/model/colour/engine/year/fuel) | 1 | cap hpi (CAP + HPI, a Solera company) |
| vehicle details score | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| Vehicle disposition (SOLD/CRUSHED/TO BE DETERMINED) | 1 | ClearVin |
| Vehicle execution | 1 | ALG (Automotive Lease Guide) — JD Power ALG |
| Vehicle history — AutoCheck summary | 1 | VINCUE (DealerCue Automotive Corp.) |
| Vehicle history — CarFax summary | 1 | VINCUE (DealerCue Automotive Corp.) |
| vehicle_history_report_carfax_or_autocheck | 1 | TrueCar |
| Vehicle History Report (title, accidents, odometer, owners) via AutoCheck | 1 | Kelley Blue Book |
| Vehicle history timeline (manufacture to present) | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Vehicle hotness / profit opportunity ranking | 1 | Stockwave (vAuto · Cox Automotive) |
| vehicle_id (AGID, AutoGrab ID canónico, color-agnóstico) | 1 | AutoGrab |
| Vehicle image | 1 | HPI Check (HPI Ltd, a Solera company) |
| Vehicle images (up to 20 interior/exterior compositions) | 1 | RedBook |
| Vehicle intake | 1 | Mahindra First Choice Wheels (MFCWL) |
| Vehicle Intelligence 360 (listing IA generativa + datos completos) | 1 | vAuto |
| Vehicle Journey (ventas previas + actividad subasta + registros de servicio) | 1 | vAuto |
| vehicle lifecycle charts | 1 | GlobalData Automotive |
| Vehicle lookup valuation (by VRM) | 1 | Auto Trader UK (Autotrader Group plc) |
| Vehicle of interest VOI (type new/cpo/used + YMM/VIN/stock/odometer) | 1 | Accu-Trade (AccuTrade) |
| vehicle origin / provenance (pochodzenie-pojazdu) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| vehicle_passport_information | 1 | Stat.vin (1VIN STAT) |
| vehicle path (classic used / rental / daily registration) | 1 | Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH) |
| Vehicle pedigree (rasgo del score) | 1 | Accu-Trade (AccuTrade) |
| vehicle plants (footprint) | 1 | GlobalData Automotive |
| Vehicle Prep / Pre-Titling event | 1 | AutoCheck (by Experian) |
| vehicle purpose / intended use (przeznaczenie-pojazdu) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| vehicle_recovered | 1 | carVertical |
| Vehicle release/exit | 1 | Mahindra First Choice Wheels (MFCWL) |
| vehicle_repossessed_flag | 1 | Stat.vin (1VIN STAT) |
| Vehicle reservation (reserva de vehículo) | 1 | Autotelex B.V. |
| vehicle sales history (Cross-Sell) | 1 | DataOne Software (DataOne, LLC) |
| Vehicle Score severity band (Non-Repairable/Severe/Major/Moderate/Minor/Little) | 1 | IAA (Insurance Auto Auctions) |
| Vehicle sold by insurer | 1 | AutoCheck (by Experian) |
| vehicle_source_id | 1 | Accu-Trade (AccuTrade) |
| Vehicle Stability Control | 1 | ClearVin |
| vehicle_status | 1 | MarketCheck (MarketCheck Cars Inc) |
| Vehicle status tags | 1 | VINCUE (DealerCue Automotive Corp.) |
| Vehicle style | 1 | Black Book (National Auto Research — Hearst) |
| vehicle_summary (AI-generated) | 1 | AutoGrab |
| vehicle_taxation_class | 1 | AutoGrab |
| Vehicle technology details | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Vehicle title doc type | 1 | ClearVin |
| Vehicle type code | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| Vehicle usage (history factor) | 1 | Canadian Black Book |
| vehicle_usage_type (personal/lease/corporate-fleet/rental/taxi/police/commercial/government) | 1 | CARFAX |
| Vehicle usage type / fleet-rental-personal (HAV input) | 1 | Black Book (National Auto Research — Hearst) |
| Vehicle valuation trends (wholesale/retail) | 1 | J.D. Power Valuation Services |
| vehicle_wheelbase_mm | 1 | AutoGrab |
| vehicleAgeInMonths (rango 6-120) | 1 | Datium Insights |
| vehicleClass | 1 | mobile.de |
| vehicleDescription (descripcion del vehiculo) | 1 | Datium Insights |
| vehicleIdName (RedbookCode | GlassesCode | RegistrationPlate | VIN) | 1 | Datium Insights |
| vehicleIdValue (identificador del vehiculo) | 1 | Datium Insights |
| vehicleNo / 차량번호 (matrícula) | 1 | Encar (엔카닷컴 / Encar.com) |
| vehicles in operation (PARC) annual count | 1 | GlobalData Automotive |
| vehicles-in-operation (VIO/PARC) count | 1 | S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026) |
| vehicleStatusMessage (stolen/scrapped/exported marker) | 1 | DVLA (Driver and Vehicle Licensing Agency) |
| vehicleTarget (destino del vehículo) | 1 | Autotelex B.V. |
| vehicleType (turismo/moto/comercial/camper) | 1 | Autotelex B.V. |
| vehicule_a_usage_agricole | 1 | HistoVec |
| vehicule_a_usage_de_collection | 1 | HistoVec |
| vehicule_declare_vole (FOVeS) | 1 | HistoVec |
| VeicoliCommerciali | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| VeicoloIbrido | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Veilingprijs | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| [MED·Prueba] Velocidad de la prueba de esquiva / moose test (km/h) | 1 | km77.com |
| Velocidad máxima (km/h) | 1 | km77.com |
| VelocitaMax | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| VenditaAssoluta | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| VenditaPerc | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| VenditaPercListino | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| VenditaPercPAC | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Venditore | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| verbod_voor_rijden_op_de_weg (OVI, prohibicion de circular) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Verbundarbeiten (trabajos combinados) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Verbundmaterialanzeige (indicacion de material compuesto) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Verificación de valoración por reglas paramétricas (AudaCheck) | 1 | Audatex España (Solera) |
| verificador autonómico (CCAA) | 1 | IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA) |
| Verkäufertyp (dealer vs private) | 1 | AutoScout24 |
| Verkoop door een particulier | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| Verkoopwaarde / sales value (con y sin IVA) | 1 | Autotelex B.V. |
| verlengde_cabine_indicator | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Vermogen (kW) | 1 | ANWB Koerslijst (Autowaarde berekenen) |
| vermogen_massarijklaar (relacion potencia/masa) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Versión exacta | 1 | GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT |
| Verteilung Preise (price distribution chart) | 1 | AutoScout24 |
| verticale_belasting_koppelpunt_getrokken_voertuig | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| vervaldatum_apk | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| vervaldatum_keuring (APK) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| vervaldatum_tachograaf | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| VFACTS build data | 1 | RedBook |
| VFACTS paint data | 1 | RedBook |
| VHR summary: Last Registered Province | 1 | CARFAX Canada |
| VHR summary: U.S. History indicator | 1 | CARFAX Canada |
| VI Data: 360-degree images | 1 | Cox Automotive |
| VI Data: 6 high-resolution images con hotspots | 1 | Cox Automotive |
| VI Data: Diagnostic Trouble Codes (DTC/OBD-II) | 1 | Cox Automotive |
| VI Data: High-value features highlighted | 1 | Cox Automotive |
| VI Data: Mechanical condition observations (ruido/transmisión/fugas/escape) | 1 | Cox Automotive |
| video | 1 | TrueCar |
| Video count | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Video reviews | 1 | Edmunds |
| videos HD (视频) | 1 | Guazi (瓜子二手车) / Chehaoduo Group |
| videoUrl | 1 | mobile.de |
| vidrios eléctricos (electricGlasses) | 1 | Fasecolda — Guía de Valores |
| vielversprechender Bestand (promising inventory) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| View count (visibility) | 1 | CLASSIC.COM |
| viewCount (visitas) | 1 | Encar (엔카닷컴 / Encar.com) |
| Views (listing analytics) | 1 | CLASSIC.COM |
| Vignette Crit'Air (niveau) | 1 | La Centrale |
| Vincoli/constraints di pacchetti accessori | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| VINCUE Value Rank (proprietary dynamic algorithmic grade) | 1 | VINCUE (DealerCue Automotive Corp.) |
| VINguard previous sales | 1 | CCC Intelligent Solutions |
| VINguard vehicle title information | 1 | CCC Intelligent Solutions |
| vinProcessed | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| vinSubmitted | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| VinTel OBD-II diagnostic report (technical condition) | 1 | VINCUE (DealerCue Automotive Corp.) |
| VIO (Vehicles in Operation) | 1 | Experian Automotive (AutoCheck) |
| Visão 360º (foto + vídeo) | 1 | Webmotors |
| Visibilidad: % uplift de vistas por tier (+70% / +120% / +230%) | 1 | Standvirtual |
| Visibilidad / posicionamiento de stock | 1 | Sumauto (SUMAUTO MOTOR S.L.) |
| Visibilidad: Super Ad | 1 | Standvirtual |
| Visibilidad: To Top (subir a lo alto, ×2/×3/×4 por tier) | 1 | Standvirtual |
| Visibilidad: Top Potencies | 1 | Standvirtual |
| Visibilidad: Top Stand (20.000 impresiones) | 1 | Standvirtual |
| VistaFoto | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| Vistoria: acessórios e extras | 1 | Webmotors |
| Vistoria: chapa suporte | 1 | Webmotors |
| Vistoria: condição do chassi nos vidros (parabrisa / portas / vigia) | 1 | Webmotors |
| Vistoria: data de vistoria | 1 | Webmotors |
| Vistoria: documentação / modificação no CRLV | 1 | Webmotors |
| Vistoria: estrutura veicular (pontos estruturais da carroceria) | 1 | Webmotors |
| Vistoria: ETA's (etiquetas autodestrutíveis: motor / batente porta / assoalho) | 1 | Webmotors |
| Vistoria: gravação do chassi | 1 | Webmotors |
| Vistoria: histórico de leilão | 1 | Webmotors |
| Vistoria: histórico de roubo/furto | 1 | Webmotors |
| Vistoria: histórico de sinistro | 1 | Webmotors |
| Vistoria: indicações de reparo | 1 | Webmotors |
| Vistoria: nº câmbio (BIN / veículo) | 1 | Webmotors |
| Vistoria: nº chassi (BIN / veículo / documento) | 1 | Webmotors |
| Vistoria: nº laudo | 1 | Webmotors |
| Vistoria: numeração do câmbio | 1 | Webmotors |
| Vistoria: numeração identificadora do chassi | 1 | Webmotors |
| Vistoria: placa | 1 | Webmotors |
| Vistoria: placa dianteira | 1 | Webmotors |
| Vistoria: placa traseira | 1 | Webmotors |
| Vistoria: RENAVAM | 1 | Webmotors |
| Visual Boost AI: overlay de daño exterior sobre 8 imagenes a 45 grados | 1 | OPENLANE |
| Visual Boost AI: tipos de daño detectados (hail, paint peel, detached panels, broken lights, rust, scratches, dents, cracks) | 1 | OPENLANE |
| Visual Boost AI: toggle on/off del comprador | 1 | OPENLANE |
| Vitesse max (km/h) | 1 | La Centrale |
| vitesse_moteur_regime_min-1 (U.2) | 1 | HistoVec |
| vname | 1 | Vehicle Databases |
| VO Certificado/CPO | 1 | coches.net |
| VOC (Voice of Customer) | 1 | Autohome (汽车之家) |
| voertuigklasse (bus M2/M3: I/II/III, A/B) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| voertuigklasse_omschrijving | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| voertuigsoort (tipo de vehiculo) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Volúmenes de stock (Cockpit) | 1 | autobiz (autobiz Group) |
| [EQUIP·Seguridad] Volante con ajuste horizontal | 1 | km77.com |
| [EQUIP·Seguridad] Volante con ajuste vertical | 1 | km77.com |
| [EQUIP·Decoración] Volante con calefacción | 1 | km77.com |
| [EQUIP·Decoración] Volante de cuero | 1 | km77.com |
| volgnummer_wijziging_eu_typegoedkeuring | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Vollmachten (poderes) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| Voltaggio (EV) | 1 | Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia) |
| Volume du coffre | 1 | La Centrale |
| Volume du réservoir (L) | 1 | La Centrale |
| Volume planning [RV driver] | 1 | Autovista Group |
| Volumen de transacciones VO (censo real) | 1 | MSI - Sistemas de Inteligencia de Mercado, S.A. |
| Volumen del segundo maletero (l) | 1 | km77.com |
| volumen logístico - número de camiones | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| volumen logístico - número de trenes | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| volumen logístico - vehículos por puerto/barco | 1 | ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones) |
| Volumen mínimo de maletero con dos filas (l) | 1 | km77.com |
| volumen por tramo de antigüedad (unidades) | 1 | DAT Ibérica (DAT Automóvil Ibérica SLU) |
| [MED·Maletero] Volumen VDA (l) | 1 | km77.com |
| Évolution du prix (courbe de dépréciation future) | 1 | La Centrale |
| VPM: auto-consign tracking | 1 | Cox Automotive |
| VPM: centralized payment/settlement | 1 | Cox Automotive |
| VPM: In-service vehicle tracking (driver/mileage/location) | 1 | Cox Automotive |
| VPM: online remarketing | 1 | Cox Automotive |
| VPM: real-time vehicle status | 1 | Cox Automotive |
| VPM: transportation quote tracking | 1 | Cox Automotive |
| VPM: vehicle grounding | 1 | Cox Automotive |
| VR por mercado/pais | 1 | Eurotax (JD Power / Autovista Group) |
| vRank (via conexion Provision) [RECONSTRUIDO] | 1 | Stockwave (vAuto · Cox Automotive) |
| vRank — posicion competitiva ponderando equipamiento y odometro | 1 | vAuto |
| vSquare (recalculo en vivo de appraisal amount/profit objective/price rank/posicion) | 1 | vAuto |
| vulnerable_road_user_protection_score | 1 | carVertical |
| 補修・板金 W1/W2/W3 (repaint/repair quality) | 1 | USS (ユー・エス・エス) Co., Ltd. |
| wacht_op_keuren | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Waiting Period | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| wam_verzekerd (seguro WAM) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Warning light ABS | 1 | Accu-Trade (AccuTrade) |
| Warning light AC | 1 | Accu-Trade (AccuTrade) |
| Warning light airbag | 1 | Accu-Trade (AccuTrade) |
| Warning light brake | 1 | Accu-Trade (AccuTrade) |
| Warning light SRS | 1 | Accu-Trade (AccuTrade) |
| Warning light suspension fault | 1 | Accu-Trade (AccuTrade) |
| Warning light TPMS | 1 | Accu-Trade (AccuTrade) |
| Warning light traction control | 1 | Accu-Trade (AccuTrade) |
| Warning lights (general) | 1 | Accu-Trade (AccuTrade) |
| Warning lights / dashboard lights | 1 | ACV Auctions |
| warranty | 1 | mobile.de |
| warranty_basic | 1 | Vehicle Databases |
| warranty_check | 1 | carsales (carsales.com.au) |
| warranty_corrosion | 1 | Vehicle Databases |
| Warranty coverage (comparador) | 1 | J.D. Power Valuation Services |
| Warranty Coverage Details (term/miles) | 1 | AutoCheck (by Experian) |
| Warranty coverage status (active/expired) | 1 | ClearVin |
| Warranty Coverage Type (Basic/Battery/Corrosion/Powertrain/Roadside Assistance/Safety Restraint) | 1 | AutoCheck (by Experian) |
| Warranty expiration | 1 | ClearVin |
| Warranty info | 1 | MAX Digital (ACV MAX) |
| Warranty information | 1 | Manheim |
| warranty miles | 1 | DataOne Software (DataOne, LLC) |
| warranty months | 1 | DataOne Software (DataOne, LLC) |
| warranty name | 1 | DataOne Software (DataOne, LLC) |
| Warranty program validation | 1 | Experian Automotive (AutoCheck) |
| Warranty Remaining Miles | 1 | AutoCheck (by Experian) |
| Warranty Remaining Time | 1 | AutoCheck (by Experian) |
| warranty_roadside_assistance | 1 | Vehicle Databases |
| Warranty transferability | 1 | ClearVin |
| warranty.anti-corrosion.years | 1 | L'argus (Cote Argus®) |
| warranty.basic | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| warranty.companyName | 1 | Encar (엔카닷컴 / Encar.com) |
| warranty.corrosionPerforation | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| warranty.maintenance | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| warranty.manufacturer.years | 1 | L'argus (Cote Argus®) |
| warranty.roadside | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| Waste EPA Charge (oil/tyres/other) | 1 | GT Motive |
| Watchlist / personal notes | 1 | BCA (British Car Auctions) |
| Watchlist flag (seguir vehiculo) | 1 | Hagerty |
| wear and tear declaration (mandatory) | 1 | Motorway |
| Wear part costs | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| weekly_value_update | 1 | CARFAX |
| weggedrag_code (suspension L/G/A) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Weighted/calculated online price (מחיר משוקלל) | 1 | Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group |
| Weiterempfehlungsrate (recommendation rate) | 1 | AutoScout24 |
| well_maintained_indicator | 1 | CARFAX |
| Werbemanager social reach (Instagram/Facebook) | 1 | mobile.de |
| Wettbewerbsposition / Preis-Ranking-Position (competitive position) | 1 | AutoScout24 |
| Wettbewerbspreise (competitor prices) | 1 | Schwacke (Schwacke GmbH / JD Power Autovista) |
| wettelijk_toegestane_maximum_aslast | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| What Others Have Paid (precios de transacciones comparables) | 1 | Orange Book Value (OBV) |
| what-if scenario (EV adoption / policy / tariff / disruptive tech) | 1 | Urban Science |
| Wheel Base | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| Wheel Covers | 1 | CarDekho (Girnar Software Pvt Ltd / CarDekho Group) |
| wheel_dia | 1 | DataOne Software (DataOne, LLC) |
| Wheel scratches / corrosion | 1 | BCA (British Car Auctions) |
| Wheel Size Front (inches) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| wheel_size_inches | 1 | Vehicle Databases |
| Wheel Size Rear (inches) | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| wheel_tightening_torque | 1 | Vehicle Databases |
| wheel track of steered and other axles (rozstaw-kol-osi-kierowanej-pozostalych-osi) | 1 | Historia Pojazdu (gov.pl) / CEPiK |
| wheel_type | 1 | Vehicle Databases |
| Wheelbase (inches) From | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| Wheelbase (inches) To | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| wheelbaseMM | 1 | Auto Trader UK (Autotrader Group plc) |
| wheelFormula | 1 | mobile.de |
| Wheelie Mitigation | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| white/transparent background | 1 | DataOne Software (DataOne, LLC) |
| Whole life cost | 1 | cap hpi (CAP + HPI, a Solera company) |
| Whole-of-market valuation | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| Wholesale flag | 1 | Copart, Inc. |
| Wholesale Hub (holding wholesale + envio bulk a subasta) | 1 | vAuto |
| Wholesale price | 1 | RedBook |
| Wholesale price - Above | 1 | Cox Automotive |
| Wholesale price - Average | 1 | Cox Automotive |
| Wholesale price - Below | 1 | Cox Automotive |
| Wholesale sales (units) | 1 | CarNewsChina Data (China EV DataTracker) |
| Wholesale valuation | 1 | vAuto |
| Wholesale/Retail Spread | 1 | Cox Automotive |
| widthMM | 1 | Auto Trader UK (Autotrader Group plc) |
| wielbasis | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| wielbasis_ondergrens_bovengrens | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| wijze_waarop_u_wordt_geinformeerd | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Window sticker base price | 1 | ClearVin |
| window_sticker_data | 1 | MarketCheck (MarketCheck Cars Inc) |
| window_sticker_info | 1 | iSeeCars |
| Windows | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| windshield_features_rain_sensor_lane_departure | 1 | Vehicle Databases |
| Wiper arm movement (front/rear) | 1 | BCA (British Car Auctions) |
| Withdrawn Vehicles | 1 | RedBook |
| 续航 WLTC | 1 | Autohome (汽车之家) |
| WLTP examinationDate / validUntil | 1 | cap hpi (CAP + HPI, a Solera company) |
| WLTP values (per configuration) | 1 | JATO Dynamics |
| WltpProvider | 1 | Quattroruote Professional / Infocar (Editoriale Domus) |
| WMI code | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| WMI Date Available To Public | 1 | NHTSA vPIC (Product Information Catalog and Vehicle Listing) |
| wmiCountry | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| wmiManufacturer | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| WOK status | 1 | Autotelex B.V. |
| WorldManufacturerIdentifier (WMI) | 1 | ChromeData (part of J.D. Power / Autodata Solutions Division) |
| written_off_check | 1 | carsales (carsales.com.au) |
| Written valuation report (B2B) | 1 | Hagerty |
| Written-Off History | 1 | RedBook |
| Written-off vehicle assessment | 1 | Percayso Vehicle Intelligence (formerly Cazana) |
| WTF scores (Lotpop integration) | 1 | VINCUE (DealerCue Automotive Corp.) |
| Yard name | 1 | Copart, Inc. |
| Yard number | 1 | Copart, Inc. |
| YearGroupId | 1 | RedBook |
| your_price_net_after_incentives | 1 | TrueCar |
| YoY change (%) | 1 | CarNewsChina Data (China EV DataTracker) |
| Z-Moto (motocicletas, mano de obra media) | 1 | GT Motive |
| Zeitwert (valor temporal/depreciado) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |
| zeroToOneHundredKMPHSeconds | 1 | Auto Trader UK (Autotrader Group plc) |
| zeroToSixtyMPHSeconds | 1 | Auto Trader UK (Autotrader Group plc) |
| zip | 1 | MarketCheck (MarketCheck Cars Inc) |
| zip_code_localization | 1 | TrueCar |
| zip-code performance (Cross-Sell) | 1 | DataOne Software (DataOne, LLC) |
| ZIP-level media opportunity | 1 | Urban Science |
| zuinigheidsclassificatie (etiqueta energetica A-G) | 1 | RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority) |
| Zustandskriterien (criterios de estado/condicion) | 1 | DAT (Deutsche Automobil Treuhand GmbH) |

## Catálogo completo (todos los campos, por frecuencia)

| Campo | nº |
|---|---|
| Marca | 93 |
| Modelo | 93 |
| Kilometraje / odómetro | 85 |
| Motor / potencia | 84 |
| Versión / trim | 83 |
| Geolocalización / región | 76 |
| VIN | 75 |
| Carrocería / segmento | 74 |
| Ventas / matriculaciones | 65 |
| Concesionario / vendedor | 63 |
| Transmisión | 62 |
| Equipamiento opcional | 57 |
| Historial de siniestros | 57 |
| Año / fecha | 56 |
| Combustible | 56 |
| Color | 54 |
| Oferta / inventario (volumen) | 51 |
| Retail / private value | 48 |
| CO2 / emisiones | 44 |
| Carga financiera / prenda | 44 |
| Índice de demanda | 42 |
| Nº de propietarios | 41 |
| Dimensiones / peso | 39 |
| Días en stock / time-to-sell | 39 |
| ITV / MOT / inspección | 38 |
| Trade / wholesale value | 38 |
| Consumo / eficiencia | 37 |
| List price (nuevo) | 37 |
| Autonomía EV | 35 |
| Import / export | 33 |
| Precio de mercado en vivo | 33 |
| Batería EV | 31 |
| Depreciación | 31 |
| Tracción | 30 |
| Seguro (coste/grupo) | 29 |
| Check de robo | 28 |
| Recall / campaña | 27 |
| Price-to-market / posición | 25 |
| Matrícula (VRM) | 23 |
| Cuota de mercado | 22 |
| Equipamiento de serie | 22 |
| Valor residual (abs) | 22 |
| Ajuste por km | 21 |
| Impuesto / matriculación | 19 |
| Histórico / índice de precio | 18 |
| Specs (ficha técnica) | 18 |
| Componentes / piezas | 17 |
| Carga EV | 15 |
| Valor residual — forecast | 14 |
| Cylinders | 14 |
| Vehicle type (car/van/motorbike) | 14 |
| Historial de servicio | 13 |
| Coste mantenimiento / SMR | 12 |
| Doors | 11 |
| condition | 8 |
| Condition adjustment | 7 |
| Matrícula | 7 |
| Private Party value | 7 |
| Coste por km / mensual | 6 |
| Airbag deployment (HAV input) | 6 |
| Series | 6 |
| wheelbase | 6 |
| number of seats | 5 |
| Reserve price (seller-set) | 5 |
| Sale date | 5 |
| sale_status | 5 |
| Torque (Nm) | 5 |
| TCO (coste total) | 4 |
| Valor residual % (RV%) | 4 |
| Condition tier (Excellent / Very Good / Good / Fair / Poor) | 4 |
| country | 4 |
| currency | 4 |
| Fuel cost | 4 |
| fuelType (Regular/Premium/Diesel/Electric/Flex/CNG/Propane/Ethanol/Methanol/NaturalGas/Gaseous) | 4 |
| Lot number | 4 |
| Manufacturer | 4 |
| Market value (advert-based, insurance) | 4 |
| Número de plazas | 4 |
| número de puertas (doors) | 4 |
| point of impact | 4 |
| price | 4 |
| seating_capacity | 4 |
| Tipo de vehiculo (Turismo / SUV / LCV <=3500kg) | 4 |
| top speed [PARCIAL] | 4 |
| Vehicle Age | 4 |
| Vehicle condition (verified, photo capture) | 4 |
| Versión | 4 |
| Auction Value (wholesale; B2B only) | 3 |
| bodyType (SUV/sedan/estate...) | 3 |
| Bore (mm) | 3 |
| Buy It Now price | 3 |
| buy-it-now price | 3 |
| Canal de venta | 3 |
| Categoria | 3 |
| city | 3 |
| Compañía aseguradora | 3 |
| country_of_manufacture | 3 |
| Fecha de proceso | 3 |
| front_brake_type | 3 |
| Fuel tank capacity | 3 |
| ground_clearance | 3 |
| images | 3 |
| Instant Cash Offer (fixed, 7-day valid) | 3 |
| listing_id | 3 |
| Loss Type (Collision/etc.) | 3 |
| Market trend | 3 |
| Number of doors (מספר דלתות) | 3 |
| Numero de puertas (doors) | 3 |
| Plate (yearMonth) | 3 |
| Potencia (CV/KW) | 3 |
| QR code (tracking de campana) | 3 |
| rear_brake_type | 3 |
| Safety features (comparador) | 3 |
| steering_type | 3 |
| Stroke (mm) | 3 |
| Tipo de vehículo (turismo/todoterreno/moto/ciclomotor/quad/microcoche/industrial/tractor) | 3 |
| towing_capacity | 3 |
| Valves Per Cylinder | 3 |
| VDP Views (per day / by MMT) | 3 |
| Vehicle Category (14 tipos: Car, Bike/Motorcycle, Scooter, Plane, Bicycle, Taxi, Truck, Bus, Tractor, Electric Car, Electric Scooter, Electric Bike, Three-wheeler) | 3 |
| Vehicle history (via AutoCheck/Experian - partner, no propio) | 3 |
| Vehicle history report (accidentes) | 3 |
| Vehicle photos (merchandising) | 3 |
| warranty status | 3 |
| 360度内装画像 (360 interior: roof/driver/rear, zoom) | 2 |
| Año (del VIN) | 2 |
| Aantal deuren | 2 |
| 车贷ABS投资支持 (auto-loan ABS investment support) | 2 |
| Acquisition Insights: local market activity | 2 |
| ACV (Actual Cash Value) | 2 |
| Additional Equipment | 2 |
| airbags | 2 |
| Announcements (defectos que disparan arbitraje) | 2 |
| APR | 2 |
| artEndDate (Additional Rate of Tax End Date) | 2 |
| aspiration | 2 |
| Auction end time / time remaining | 2 |
| auction_price | 2 |
| AutoCheck Score (1-100) | 2 |
| AutoGrade condition score (0.0-5.0) | 2 |
| automatedVehicle | 2 |
| Average sold price (wholesale) | 2 |
| average vehicle age | 2 |
| axles | 2 |
| badge | 2 |
| Besitzumschreibungen (volumen de transferencias de propiedad) | 2 |
| body_subtype | 2 |
| Body-type (filter dimension) | 2 |
| Build Sheet (OEM options/packages by VIN) | 2 |
| Código eco (CODIGO_ECO_ITV) | 2 |
| Código postal (ajuste geográfico de precio) | 2 |
| Cargo volume (l) | 2 |
| Catalogusprijs | 2 |
| Categoría de vehículo eléctrico (PHEV/REEV/HEV/BEV) | 2 |
| category | 2 |
| Central locking | 2 |
| chrome_style_id | 2 |
| clase (class) | 2 |
| Clasificación Reglamento de Vehículos (Anexo II RD 2822) | 2 |
| Clean Loan Value (credito potencial sobre el vehiculo) | 2 |
| 'Coming Soon' placeholder (vehiculo en recon) | 2 |
| Company name (lead) | 2 |
| competitive positioning | 2 |
| Compression ratio | 2 |
| Condition report (damage / warning lights / missing equipment / MOT advisories) | 2 |
| constructionYear | 2 |
| Contraseña de homologación | 2 |
| couleur (color) | 2 |
| Country code | 2 |
| country_of_origin | 2 |
| Current bid | 2 |
| Current state of title | 2 |
| cylinderCapacity [NV bulk] | 2 |
| Daños (damages) | 2 |
| Daily Vehicle Volume (Pulse KPI) | 2 |
| data_source | 2 |
| dateOfLastV5CIssued | 2 |
| Days to turn (days-to-sell) | 2 |
| defect.dangerous (boolean) | 2 |
| defect.text | 2 |
| defect.type (FAIL/ADVISORY/MAJOR/DANGEROUS/MINOR/USER ENTERED) | 2 |
| Derivative | 2 |
| Destination charge | 2 |
| detailed_history_event_date | 2 |
| Diagnostic Trouble Codes (DTCs) | 2 |
| Distance from buyer | 2 |
| Distancia entre ejes 1-2 (DISTANCIA_EJES_12_ITV) | 2 |
| Distintivo ambiental (0 Emisiones/ECO/C/B) | 2 |
| distintivo ambiental DGT (0 / ECO / B / C / sin etiqueta) | 2 |
| Drive (drivetrain type) | 2 |
| Durchschnittspreis Gebrauchtwagen (precio medio VO) | 2 |
| Eco-innovación (ECO_INNOVACION_ITV) | 2 |
| electrification_level | 2 |
| Electronic Stability Control (ESC) | 2 |
| Estimated market value | 2 |
| european target price | 2 |
| euroStatus | 2 |
| event_type | 2 |
| Ex-showroom price | 2 |
| exhaust_system | 2 |
| Fair Market Value | 2 |
| feature category | 2 |
| feature.name | 2 |
| Fecha de tramitación (FEC_TRAMITACION) | 2 |
| Fog lights | 2 |
| Forecast horizon (months, up to 120 / 6yr-200k km) | 2 |
| Front-end gross profit | 2 |
| fuel | 2 |
| Fuel Capacity (L) | 2 |
| Fuel Delivery | 2 |
| Guide price | 2 |
| gvwr | 2 |
| hammer_price | 2 |
| History-Based Value (VIN-specific value) | 2 |
| impressions | 2 |
| Indicador de renting (RENTING / Servicio de Renting) | 2 |
| instant offer (match price) | 2 |
| interior_condition | 2 |
| interior_features | 2 |
| invoice | 2 |
| Invoice price | 2 |
| [MED·Habitabilidad 2ª fila] Isofix (cm) | 2 |
| IVA | 2 |
| KBB (Kelley Blue Book) value | 2 |
| Kenteken (input licensePlate) | 2 |
| Kilometers Driven (odometro) | 2 |
| Kilometerstand (mileage) | 2 |
| latitude | 2 |
| Listing type (Fixed-price / Auction / Make-offer) | 2 |
| Llamadas a revisión pendientes (recalls) | 2 |
| Local market data (oferta/demanda retail local) | 2 |
| Longitud (pintura) | 2 |
| longitude | 2 |
| Manufacturer build data (OEM/factory specs) | 2 |
| Manufacturer Name | 2 |
| markedForExport | 2 |
| market_alerts (DMS) | 2 |
| market average price | 2 |
| marketability score | 2 |
| Marque | 2 |
| Masa en orden de marcha (MASA_ORDEN_MARCHA_ITV) | 2 |
| max_torque | 2 |
| Maximum price | 2 |
| Mean price | 2 |
| mechanical | 2 |
| Median price | 2 |
| Merk (entrada manual) | 2 |
| message (estado de la peticion) | 2 |
| Minimum price | 2 |
| modelDescription (modelo) | 2 |
| monthly payment | 2 |
| motExpiryDate | 2 |
| motStatus (Valid/Not valid/No details held/No results) | 2 |
| Municipio | 2 |
| MUVVI index value (Jan 1997=100) | 2 |
| Número de plazas máximo (NUM_PLAZAS_MAX) | 2 |
| Número de transmisiones (NUM_TRANSMISIONES) | 2 |
| NADA value | 2 |
| NatCode (national search-tree code) | 2 |
| Number of keys | 2 |
| Number of price changes | 2 |
| Numero de plazas (seats) | 2 |
| Nutzungsausfallentschaedigung (loss-of-use comp.) | 2 |
| oil_capacity | 2 |
| On-Road (GST) price | 2 |
| Paint condition | 2 |
| Part-exchange value | 2 |
| Parts prices (OEM-sourced, monthly) | 2 |
| Photo count | 2 |
| plant_city | 2 |
| Plate change history (previous plates + dates) | 2 |
| plate_state | 2 |
| Plazas de pie (PLAZAS_PIE) | 2 |
| PPSR certificate (finance owing / encumbrance) | 2 |
| Precio (price) | 2 |
| price_drop_indicator | 2 |
| Private sale price | 2 |
| Private sale value | 2 |
| Procedencia (fabricación nacional/importación UE/no UE/subasta) | 2 |
| Purchase history (VIN Values) | 2 |
| radio (DAB) | 2 |
| rear_suspension | 2 |
| RedBook Code (RBC) | 2 |
| Reducción eco (REDUCCION_ECO_ITV) | 2 |
| Retail margin | 2 |
| Retail valuation | 2 |
| revenueWeight | 2 |
| safety | 2 |
| Sale time | 2 |
| Score factor: Age | 2 |
| seats | 2 |
| Serie | 2 |
| source | 2 |
| standard_seating | 2 |
| Standtage (days in stock) | 2 |
| state | 2 |
| std_seating | 2 |
| Stock Number (Stock #) | 2 |
| Stock turn (rotación/standtijd de stock) | 2 |
| style (vehicle_style name) | 2 |
| styleId (Chrome Style ID) | 2 |
| Suspension type | 2 |
| Tara (kerb/unladen weight) | 2 |
| taxDueDate | 2 |
| Taxes (tipo + valor %) | 2 |
| taxStatus (Taxed/SORN/Untaxed/Not Taxed for on Road Use) | 2 |
| Telaio (chassis/VIN) | 2 |
| Tipo de alimentación (mono/bi/flexicombustible) | 2 |
| Tipo de daño (Noa) | 2 |
| Tipo de posesión (V venta / S subasta — COD_POSESION) | 2 |
| Tipo del vehículo base | 2 |
| tire_size | 2 |
| Tire tread depth | 2 |
| tire_type | 2 |
| title | 2 |
| Title number | 2 |
| Torque rpm (from/to) | 2 |
| Transmision | 2 |
| typeApproval | 2 |
| Typical Negotiation adjustment (~4-7%) | 2 |
| Usage type (Personal/Commercial/Fleet/Rental/Taxi/Lease) | 2 |
| Vía anterior (mm) | 2 |
| Vía posterior (mm) | 2 |
| Valor de compra (trade) GANVAM-DAT | 2 |
| Valor de mercado | 2 |
| Valor GANVAM-DAT (valor de referencia oficial VO Espana) | 2 |
| Value history (retail value back to Jan 2014) | 2 |
| VDP URL | 2 |
| vehicle_class | 2 |
| Vehicle description (year/make/model/trim/engine/body) | 2 |
| Vehicle history highlights | 2 |
| Vehicle Identity Check | 2 |
| vehicle_size | 2 |
| Vehicle SubType | 2 |
| VehicleId | 2 |
| Versión del vehículo base | 2 |
| warranty type | 2 |
| wheelbase_type | 2 |
| wheelplan | 2 |
| Wholesale Average (benchmark, average condition) | 2 |
| Wiederbeschaffungswert (replacement value) | 2 |
| Window Stickers (factory rebate) | 2 |
| yearOfManufacture | 2 |
| ZIP code | 2 |
| % de cumplimiento del objetivo 2030 (Fit for 55) | 1 |
| % de cuota de leasing calculable (~85%) | 1 |
| % diferença / posição vs FIPE | 1 |
| % stock sold through network | 1 |
| +50 data points de negocio/financieros/marketing por anunciante | 1 |
| 0-100km/h加速 | 1 |
| 0-62 / acceleration [PARCIAL] | 1 |
| 0to100_kmph | 1 |
| 0to60_mph | 1 |
| 12-month claim probability indicator | 1 |
| 15+ Live Market View data points (pricing/demanda/oferta/subasta side-by-side) | 1 |
| 16 drivers de VR (calidad percibida, go-to-market, equipamiento, volumen, incentivos, usabilidad, autonomia, carga, eficiencia coste, rendimiento, consumo combustible, consumo energia, VR de marca, posicionamiento, fortalezas/debilidades concepto, feedback mercado) | 1 |
| 16 key residual-value drivers (Car to Market report) | 1 |
| 160+ customizable rule data fields | 1 |
| 1st-party data enrich (additional vehicles owned, financial profile) | 1 |
| [EQUIP·Equipaje] 2 posavasos delanteros y 2 traseros | 1 |
| 20+ criterios de precio y atractividad de marketing (MyStock) | 1 |
| 24 Hour With-a-Look approval window | 1 |
| £30,000 data guarantee | 1 |
| 30+ KPIs de mercado personalizables (Barometer) | 1 |
| 30+ variables de regresion hedonica / matriz de coeficientes | 1 |
| 比车300估值 低/高 X万 (delta vs Che300 valuation) | 1 |
| 检测报告 300+项 (inspection report) | 1 |
| 360-degree exterior views | 1 |
| 360-degree images (Fyusion 3D) | 1 |
| 360-degree interior views | 1 |
| 360-degree View (with sounds) | 1 |
| [EQUIP·Multimedia] 4 puertos USB de carga (2x18W y 2x60W) | 1 |
| 4 roues motrices | 1 |
| 45-Day Guaranteed Sell offer price | 1 |
| 5YCTO Value Rating (Among the Best / Lower Cost Than Most / Average / Higher Cost Than Most) | 1 |
| 60+ high-resolution photos | 1 |
| 7-day valuation validity (re-confirm mileage) | 1 |
| 70+ Ausstattungsmerkmale (equipment features) | 1 |
| 80+ provenance data points / 20+ data sources | 1 |
| 90 Days to Sale (consumer journey) | 1 |
| A/B/C柱切割焊接 (pillar cut/weld signal) | 1 |
| 傷 A1/A2/A3 (scratch by size) | 1 |
| aangedreven_as (traccion) | 1 |
| aangedreven_rupsband_indicator | 1 |
| aanhangwagen_autonoom_geremd | 1 |
| aanhangwagen_middenas_geremd | 1 |
| Aankoop bij een particulier | 1 |
| Aanschafwaarde (seguro) | 1 |
| aantal_assen | 1 |
| aantal_cilinders | 1 |
| aantal_eigenaren_prive_zakelijk (OVI, nº propietarios) | 1 |
| aantal_gebreken_geconstateerd | 1 |
| aantal_passagiers_zitplaatsen_wettelijk | 1 |
| aantal_rolstoelplaatsen | 1 |
| aantal_staanplaatsen | 1 |
| aantal_wielen | 1 |
| aantal_zitplaatsen | 1 |
| aantaldeuren_ondergrens_bovengrens | 1 |
| aantalpassagiers_ondergrens_bovengrens | 1 |
| aantalrolstoelplaatsen_ogr_bgr | 1 |
| aantalzitplaatsen_ondergrens_bovengrens | 1 |
| aanwijzingsnummer | 1 |
| Abandon flag | 1 |
| ABI insurers group rating (GB) | 1 |
| Abolladuras de panel (mm) | 1 |
| abs_system | 1 |
| ABS warning light | 1 |
| ABS/EBD/ESP | 1 |
| AC function score | 1 |
| 自适应巡航 ACC | 1 |
| Accelerated Search | 1 |
| acceleration | 1 |
| Acceleration / top speed (performance) | 1 |
| acceleration_to_100 (0-100) | 1 |
| acceleration_to_60 (0-60) | 1 |
| Accelerazione0100 | 1 |
| [EQUIP·Confort] Acceso sin llave | 1 |
| Accessori after-market + costi | 1 |
| Accessori di serie (codici + descrizioni) | 1 |
| accessories (accesorios) | 1 |
| Accessories condition (missing items) | 1 |
| Accessories cost | 1 |
| Account: financing changes | 1 |
| Account: payoff indicators | 1 |
| Account: title loan additions | 1 |
| AccuTrade: Galves Market Ready Value | 1 |
| AccuTrade GID (gid) | 1 |
| AccuTrade: gross_profit_retail | 1 |
| AccuTrade: gross_profit_wholesale | 1 |
| AccuTrade: OBD-II diagnostic deduction | 1 |
| AccuTrade: real_cash_value / guaranteed_offer | 1 |
| AccuTrade: reconditioning_cost | 1 |
| ACES codes | 1 |
| ACES codes & descriptions | 1 |
| ACES VCdb identifiers | 1 |
| ACES Vehicle ID | 1 |
| ACES VehicleID | 1 |
| ACH funding | 1 |
| 시세 변ación por 지역 (región) | 1 |
| acquire_acquisition_management_tracking | 1 |
| acquire_analytics_dashboard_team_performance | 1 |
| acquire_find_opportunities_filter_220k_cars | 1 |
| acquire_livemarket_data_per_listing | 1 |
| acquire_onthego_remote_appraisal | 1 |
| acquire_rego_id_lookup | 1 |
| Acquisition / capture rate | 1 |
| Acquisition channel recommendation (trade/auction/private-party) | 1 |
| Acquisition Insights: estimated turn time | 1 |
| actie_radius_enkel_elektrisch_wltp (autonomia EV) | 1 |
| actie_radius_extern_opladen_wltp | 1 |
| actieradius | 1 |
| actieradius_extern_oplaadbaar | 1 |
| Active Safety System Note | 1 |
| actual_cash_value_acv | 1 |
| Actual recon cost (after service) | 1 |
| actual vehicle photo (inventory feed) | 1 |
| ACV Estimate (precio de venta predicho por ML) | 1 |
| ACV Guarantee guaranteed payout (paga diferencia / upside al seller) | 1 |
| ad / listing quality | 1 |
| ad budget reinvestment % (10-15%) | 1 |
| Ad Frequency | 1 |
| Adaptive Cruise Control (ACC) | 1 |
| Adaptive Driving Beam (ADB) | 1 |
| Adaptive Headlights | 1 |
| 智能硬件/ADAS芯片 | 1 |
| ADAS / safety / driver assistance features | 1 |
| ADAS integration/calibracion | 1 |
| ADAS operating min/max distance | 1 |
| ADAS operating min/max speed | 1 |
| ADAS system (e.g. DiPilot / DiPilot 100) | 1 |
| AdBlue need flag | 1 |
| AdBlue tank capacity (l) | 1 |
| Add/deducts (option-level value adjustments, auto-applied) | 1 |
| Additional Error Text | 1 |
| Additional history: Abandoned | 1 |
| Additional history: Corrected Title | 1 |
| Additional history: Repossessed | 1 |
| Additional Parts Information | 1 |
| additional_vehicles | 1 |
| additionalBuildData.description | 1 |
| additionalBuildData.invoice | 1 |
| additionalBuildData.label | 1 |
| additionalBuildData.value | 1 |
| additionele_massa_alternatieve_aandrijving | 1 |
| address | 1 |
| Adjustable Headlamps | 1 |
| Adjustable Headrest | 1 |
| Adjustable Steering | 1 |
| Adjusted Comparable Value | 1 |
| Adjusted MMR (on-demand via API) | 1 |
| Adjusted Vehicle Value | 1 |
| Adjusted vs Base value distinction | 1 |
| adjustedBy: EVBH (Electric Vehicle Battery Health) | 1 |
| Adjuster name | 1 |
| Adjustment % (km/condition) | 1 |
| adjustment.override.max_kms | 1 |
| adjustment.override.min_kms | 1 |
| adjustment.retail_adjustment | 1 |
| adjustment.trade_adjustment | 1 |
| Ads: audiência qualificada (perfil demográfico) | 1 |
| Ads: Conteúdo 360º (branded content) | 1 |
| Ads: CRM Push | 1 |
| Ads: Loja Oficial (showroom oficial) | 1 |
| Ads: Smart Lead (leads cualificados + leads coche nuevo) | 1 |
| adsCategoryIdDescriptions | 1 |
| adsCategoryIds | 1 |
| adsTypeIdDescriptions | 1 |
| adsTypeIds | 1 |
| adult_occupant_protection_score | 1 |
| Advanced data analytics / customizable reporting | 1 |
| Advert descriptions / listing text | 1 |
| Advert images | 1 |
| advertisement status / salesStatus | 1 |
| advertisementCategory | 1 |
| advertisementTitle | 1 |
| advertisementUrl | 1 |
| advertiserVehicleHighlight (1-3) | 1 |
| Advertising history (historial publicitario) | 1 |
| adverts.soldPrice.amountGBP | 1 |
| aerodynamic_drag | 1 |
| aerodynamische_voorziening | 1 |
| AFC: floorplan revolving credit line | 1 |
| AFC: Pay with AFC (floorea precio + auction fees + transporte) | 1 |
| AFC: plazo hasta 90 dias | 1 |
| AFC: recomendaciones de vehiculo por historial | 1 |
| Afschrijvingspercentage BPM (derivado: (nieuwprijs − handelsinkoopwaarde)/(consumentenprijs/100)) | 1 |
| afstand_hart_koppeling_tot_achterzijde | 1 |
| afstand_tot_volgende_as | 1 |
| afstand_voorzijde_tot_hart_koppeling | 1 |
| After-factory equipment adjustment | 1 |
| after-sales potential per territory | 1 |
| aftermarket by channel (Garages, VM Networks, Autocentres, Tire Specialists, Parts Accessories, Online Sales, Hypermarkets, Petrol Stations, Fast Fits, Crash Repair/Bodyshops) | 1 |
| aftermarket by product family (Wear & Tear, Service, Tires, Consumables, Crash Repair, Mechanical, Accessories) | 1 |
| aftermarket CAGR | 1 |
| aftermarket part value (market size) | 1 |
| aftermarket part volume | 1 |
| Aftermarket tint | 1 |
| Aftermarket upgrades itemizados con valor en dolares | 1 |
| AfterSales: customer marketing analytics | 1 |
| AfterSales: retention / loyalty metrics | 1 |
| AfterSales: service customer targeting | 1 |
| AFV share (%) | 1 |
| afwijkende_maximum_snelheid | 1 |
| Age adjustment | 1 |
| Agreed Value (insurance) | 1 |
| agregación de expedientes | 1 |
| ahorro energético (kWh) | 1 |
| ai_buyer_signals_preferences_next_steps | 1 |
| ai_call_transcription_summary_gemini | 1 |
| ai_contextual_buyer_summary | 1 |
| ai_intent_detection_hot_leads | 1 |
| ai_lead_prioritization_likelihood_to_convert | 1 |
| ai_offer_creation_support_data_backed | 1 |
| AI SEO-optimized vehicle description (incluye OEM build data) | 1 |
| AI vehicle description (AI Description Writer/Builder) | 1 |
| AI vehicle descriptions (SEO-optimized) | 1 |
| AI-generated listing descriptions (Smart Descriptions) | 1 |
| air_bag_deployment | 1 |
| Air Conditioner | 1 |
| air_conditioning_type | 1 |
| air.performance_benchmarking (vs nacional/estatal) | 1 |
| air.weighted_retained_value | 1 |
| airbag | 1 |
| Airbag availability | 1 |
| [EQUIP·Seguridad] Airbag central delantero | 1 |
| Airbag Deployed | 1 |
| Airbag deployment status | 1 |
| [EQUIP·Seguridad] Airbag frontal acompañante | 1 |
| [EQUIP·Seguridad] Airbag frontal conductor | 1 |
| Airbag warning light | 1 |
| [EQUIP·Seguridad] Airbags de cabeza delanteros y traseros | 1 |
| [EQUIP·Seguridad] Airbags laterales delanteros | 1 |
| [EQUIP·Seguridad] Airbags laterales traseros | 1 |
| Airbags por posición (rodilla/lateral/cabeza) | 1 |
| [EQUIP·Confort] Aire acondicionado | 1 |
| aire acondicionado SI/NO (airconditioningShow) | 1 |
| [EQUIP·Seguridad] Aislamiento térmico y doble acristalamiento lateral | 1 |
| Aisle/Stall | 1 |
| ajuste de RV vehiculo-a-vehiculo (override manual) | 1 |
| ajuste de valor por equipamiento (depreciación de opcionales) | 1 |
| Ajuste por antigüedad/edad | 1 |
| Ajuste por antiguedad/edad | 1 |
| Ajuste por blindagem (vehículo blindado) | 1 |
| Ajuste por condición técnica | 1 |
| Ajuste por cor | 1 |
| Ajuste por opcionais / equipamento (airbag, direção hidráulica, etc.) | 1 |
| Ajuste por quilometragem (km rodados) | 1 |
| [EQUIP·Varios] Alarma antirrobo | 1 |
| Alerta de discrepancia de recon (declarado vs IA) | 1 |
| [EQUIP·Seguridad] Alerta de fatiga del conductor | 1 |
| Alertas de precio de anuncios similares (priceAlertsSimilarListings) | 1 |
| Alerte prix | 1 |
| Alimentazione | 1 |
| AllElectric | 1 |
| AllElectric_City | 1 |
| AllElectric_Comb | 1 |
| Allestimento | 1 |
| Allestimento esatto (versione/trim) | 1 |
| Allestimento_offline | 1 |
| Allestimento_online | 1 |
| alloy wheel photos (head-on, full alloy) | 1 |
| Alloy Wheels | 1 |
| alloyWheels | 1 |
| Altas | 1 |
| altBodyType | 1 |
| Alternative derivative lookup (cap ID/code/type) | 1 |
| Alternative fuels | 1 |
| AltezzaMetri | 1 |
| altModelName | 1 |
| altStyleName | 1 |
| Altura (mm) | 1 |
| [MED·Maletero] Altura del borde de carga (cm) | 1 |
| [MED·Habitabilidad 1ª fila] Altura libre (cm) | 1 |
| [MED·Habitabilidad 1ª fila] Altura libre con techo solar (cm) | 1 |
| ambit.radius (km) | 1 |
| ambit.zipcode | 1 |
| American_Made_Index_score (100-point) | 1 |
| AMI factor: parts_sourcing (AALA) | 1 |
| AMI factor: US_factory_employment | 1 |
| Amount above/below market ($) | 1 |
| Amperaje del alternador | 1 |
| AnalisiRotazione | 1 |
| ANCAP Safety Rating | 1 |
| Anchura (mm) | 1 |
| [MED·Habitabilidad 1ª fila] Anchura a los hombros (cm) | 1 |
| Ancienneté du pro (Agent depuis) | 1 |
| Android Auto | 1 |
| Anfragen / Leads (inquiries) | 1 |
| Angebotspreis (offer price) | 1 |
| angle_of_approach | 1 |
| angle_of_departure | 1 |
| Anio de produccion (productionDate) | 1 |
| Année (millésime) | 1 |
| AnnoImmatricolazione | 1 |
| AnnoInfocar | 1 |
| AnnoMeseImmatricolazione | 1 |
| AnnoPrevisione | 1 |
| Announcements / disclosures | 1 |
| Announcements/remarks | 1 |
| Antenna | 1 |
| anti_lock_brakes | 1 |
| Anti-lock Brake System (ABS) | 1 |
| Anti-lock Braking System (ABS) | 1 |
| [EQUIP·Seguridad] Antibloqueo de frenos (ABS) | 1 |
| Antigüedad / edad del vehículo (parque) | 1 |
| Antiguedad/año del vehiculo (parque) | 1 |
| Antilock Braking System (ABS) | 1 |
| Anuncio: Com garantia (flag) | 1 |
| Anuncio: Combustível | 1 |
| Anuncio: Cor | 1 |
| [VO] Anuncio de coche usado (coches77 / KM77 VO) | 1 |
| Anuncio: Estado (Usado/Novo) | 1 |
| [A] Anuncio: IUC | 1 |
| [A] Anuncio: Livro de revisões | 1 |
| [A] Anuncio: Lugares | 1 |
| Anuncio: Nº de portas | 1 |
| [A] Anuncio: Nº de proprietários | 1 |
| [A] Anuncio: Não fumador | 1 |
| [A] Anuncio: Norma de emissões | 1 |
| Anuncio: Potência (cv) | 1 |
| Anuncio: Preço (EUR) | 1 |
| Anuncio: Quilómetros (km) | 1 |
| [A] Anuncio: Registo de serviço | 1 |
| Anuncio: Tipo de Caixa (transmisión) | 1 |
| Anuncio: Tipo de cor | 1 |
| [A] Anuncio: Tração | 1 |
| Anuncio: Valor Fixo (flag precio no negociable) | 1 |
| Anuncio: Versão | 1 |
| Anzahl der Vorbesitzer (numero de propietarios anteriores) | 1 |
| Anzahl konkurrierender Fahrzeuge (# competing vehicles) | 1 |
| AnzianitaAllaEdizione | 1 |
| API adjustedForecastPricing.wholesale | 1 |
| API bestMatch flag | 1 |
| API: catálogo | 1 |
| API: consulta de leads | 1 |
| API currency (USD) | 1 |
| API: estoque / itens | 1 |
| API: estoque site | 1 |
| API forecast date (up to 106 weeks ahead) | 1 |
| API forecastDate/edition (Mondays) | 1 |
| API forecastedAverageGrade | 1 |
| API forecastedPricing (unadjusted) | 1 |
| API: inclusão de leads | 1 |
| API: interações | 1 |
| API: listing create/update/publish/remove (write-only) | 1 |
| API sampleSize | 1 |
| API token (generacion para mostrar precios OBV) | 1 |
| API zipCode | 1 |
| aportación al saldo de la balanza comercial española | 1 |
| aportación del sector al Estado (€) | 1 |
| [EQUIP·Confort] Apoyabrazos central delantero | 1 |
| [EQUIP·Confort] Apoyabrazos central trasero | 1 |
| Apple CarPlay | 1 |
| [EQUIP·Multimedia] Apple CarPlay / Android Auto | 1 |
| application-type | 1 |
| Apport (€) | 1 |
| appraisal close ratio | 1 |
| Appraisal report (PDF/email) | 1 |
| Appraisal Snapshot (saved appraisal) | 1 |
| appraisalDate (fecha de tasación) | 1 |
| Appraiser name | 1 |
| Appraiser/Adjuster name | 1 |
| Approval time tracking | 1 |
| Approximate condition (excellent/good/fair/poor) | 1 |
| apr_estimate | 1 |
| apte_a_circuler | 1 |
| Arañazos (mm) | 1 |
| Arañazos/grietas de paragolpes (mm) | 1 |
| Arbeitswerte AW (unidades de trabajo / baremos MO) | 1 |
| Arbitration eligibility (defectos elegibles) | 1 |
| arbitration rate / status | 1 |
| Army/government deduction (צבא) | 1 |
| [EQUIP·Confort] Arranque sin llave | 1 |
| Articles | 1 |
| articulated / semi-trailer (Sattelzug) | 1 |
| As Described Guarantee: elegibilidad (93% del inventario) | 1 |
| As Described Guarantee: ventana 5 dias compra / 7 dias entrega (con transporte OPENLANE) | 1 |
| as_nummer | 1 |
| AS-IS flag (5-6% del inventario) | 1 |
| Asegurado | 1 |
| [EQUIP·Confort] Asiento de conductor con memoria | 1 |
| [EQUIP·Confort] Asiento del conductor con ajuste lumbar | 1 |
| [EQUIP·Equipaje] Asiento trasero abatible 40/60 | 1 |
| [EQUIP·Confort] Asientos delanteros con ajuste de altura | 1 |
| [EQUIP·Confort] Asientos delanteros con ajuste eléctrico (8 vías conductor/6 acompañante) | 1 |
| [EQUIP·Confort] Asientos delanteros con calefacción | 1 |
| [EQUIP·Confort] Asientos delanteros deportivos | 1 |
| [EQUIP·Confort] Asientos delanteros ventilados | 1 |
| Asignación automática a canales de venta (Pilot) | 1 |
| [EQUIP·Seguridad] Asistente de frenada | 1 |
| [EQUIP·Seguridad] Asistente de luz de cruce/carretera | 1 |
| [EQUIP·Seguridad] Asistente de parada de emergencia | 1 |
| [EQUIP·Multimedia] Asistente de voz | 1 |
| Asistente IA generativa (WhatsApp: precificação + crédito + recomendações) | 1 |
| [EQUIP·Seguridad] Asistente para atascos | 1 |
| Asking-vs-selling spread (%) | 1 |
| asking/listed price | 1 |
| Asset register valuation / financial exposure | 1 |
| Assignments Received | 1 |
| Assisted driving chip (e.g. NVIDIA DRIVE Orin N) | 1 |
| Assurance (estimation partenaire) | 1 |
| At-a-Glance: Additional History status | 1 |
| At-a-Glance: Certified Pre-Owned status | 1 |
| At-a-glance profitability report (con vs sin herramienta) | 1 |
| At-a-Glance: Service/Repair status | 1 |
| atglance_airbag_deployment_count | 1 |
| atglance_auction_sales_history_count | 1 |
| atglance_basic_warranty_count | 1 |
| atglance_photo_count | 1 |
| atglance_sales_history_count | 1 |
| Atributo: richtprijzen = precios medios incl. BTW & BPM | 1 |
| Atributos del vehiculo (make/model/derivado/edad/km/fuel) | 1 |
| Auction announced_at_auction date | 1 |
| Auction Announcements (structural damage) | 1 |
| Auction condition (Run & Drive / WON'T START) | 1 |
| auction_date | 1 |
| Auction images[] | 1 |
| Auction lot / auctionId | 1 |
| auction_lot_number | 1 |
| Auction Run Lists (ACV / Manheim / ADESA) | 1 |
| auction_sale_date | 1 |
| Auction sales forecast / prediccion (total por evento) | 1 |
| auction_sold_status | 1 |
| Auction title state | 1 |
| Auction transactions ACV + other auctions (input) | 1 |
| Auction type (Open/Closed) | 1 |
| Auction Value - Average | 1 |
| Auction Value - High | 1 |
| Auction Value - Low | 1 |
| Auction vendor (Copart/IAA) | 1 |
| Auction/sale name | 1 |
| AuctionACCESS membership ($103/individual/year) | 1 |
| Auctions summary tab | 1 |
| Audascan message (mensaje por aseguradora) | 1 |
| AudaVIN flag (Yes/No) | 1 |
| audit trail (registro de cambios y busquedas por usuario) | 1 |
| Aufrufe (views) | 1 |
| Ausstattungsanalyse (fehlende Ausstattung + impacto en precio) | 1 |
| Ausstattungsvergleich eigen vs Konkurrenz (equipment comparison) | 1 |
| autenticacao (código de autenticação verificável da consulta) | 1 |
| Auto | 1 |
| auto-bid increment (GBP 50) | 1 |
| auto-panorama exterior 360 | 1 |
| auto-panorama interior 360 | 1 |
| Auto-Reverse System for Windows and Sunroofs | 1 |
| AutoCalc Adjusted Price | 1 |
| autocheck_report | 1 |
| AutoCheck Snapshot (vehicle history, Experian) | 1 |
| AutoCheck vehicle history snapshot (integrado, gratis en US CR) | 1 |
| AutoGrade label: 1 Rough | 1 |
| AutoGrade label: 2 Below Average | 1 |
| AutoGrade label: 3 Average | 1 |
| AutoGrade label: 4 Clean | 1 |
| AutoGrade score (1.0-5.0) | 1 |
| AutoGrade score 0-5 (estándar Manheim/NAAA) | 1 |
| AutoGuru: comparação pátio vs lojas rivais próximas | 1 |
| AutoGuru: idade média do estoque | 1 |
| AutoGuru: margem ideal de compra/venda | 1 |
| AutoGuru: melhor sortimento do pátio | 1 |
| AutoGuru: melhor tempo de pátio | 1 |
| AutoGuru: parâmetros de preço competitivo | 1 |
| AutoGuru: preço vs concorrência (above/below) | 1 |
| AutoGuru: quantidades em estoque | 1 |
| AutoGuru: quilometragem do estoque | 1 |
| AutoGuru: tempo médio de venda | 1 |
| Autoinsights: atividade por município | 1 |
| Autoinsights: carros mais procurados (ranking) | 1 |
| Autoinsights: estudos temáticos (intenção de compra, elétricos, automáticos, SUV, manutenção) | 1 |
| Autoinsights: itens opcionais mais procurados | 1 |
| Autoinsights: motos mais procuradas (ranking) | 1 |
| Autoinsights: perfil do usuário (gênero / idade) | 1 |
| Autoinsights: preferência de cor | 1 |
| Autoinsights: recortes temporais (mensal / trimestral / semestral / anual) | 1 |
| Autoinsights: termômetros de busca | 1 |
| AutoIQ: Ad-to-short-form content | 1 |
| AutoIQ: AI-generated listing descriptions (voz del dealer) | 1 |
| AutoIQ: Centralized lead dashboard | 1 |
| AutoIQ: Image management / visual enhancement | 1 |
| AutoIQ: Pricing recommendations | 1 |
| AutoIQ: Video-to-listing | 1 |
| AutoMatch exact-equipment competitive match | 1 |
| Automated appraisal in ACV MAX (VIPER) | 1 |
| Automated customer offer (ClearCar) | 1 |
| automatische Neubewertung (auto revaluation) | 1 |
| Automotive ID | 1 |
| Automotive ID / Autovista ID | 1 |
| autoniq: AuctionNet data | 1 |
| autoniq: AutoCheck report | 1 |
| autoniq: autoniq Market Report | 1 |
| autoniq: Black Book value | 1 |
| autoniq: CARFAX report | 1 |
| autoniq: CarValue (ADESA) value | 1 |
| autoniq: Galves value | 1 |
| autoniq: Kelley Blue Book value | 1 |
| autoniq: listas / wishlist / notas / fotos | 1 |
| autoniq: MMR (Manheim Market Report) value | 1 |
| autoniq: PMR (Pipeline Market Report, 175+ subastas EDGE) | 1 |
| autoniq: Retail Index | 1 |
| autoniq Wholesale Index: average wholesale price | 1 |
| autoniq Wholesale Index: radio 50-3000 millas | 1 |
| autoniq Wholesale Index: ventana 90 dias / refresco diario (ADESA + DealerBlock data) | 1 |
| Autonomía del vehículo eléctrico (km) | 1 |
| Autonomía eléctrica (km) | 1 |
| Autonomía eléctrica WLTP (km) | 1 |
| AutoPay / estado de repago | 1 |
| autotelexId (ATX id) | 1 |
| Autoviza: analyse des ventes du véhicule | 1 |
| Autoviza: dates + kilométrage des contrôles techniques | 1 |
| Autoviza: données carte grise certifiées | 1 |
| Autoviza: durée de détention par propriétaire | 1 |
| Autoviza: existence vérifiée | 1 |
| Autoviza: historique du kilométrage | 1 |
| Autoviza: nombre de propriétaires précédents | 1 |
| Autoviza: numéro de série (VIN) certifié | 1 |
| Autoviza: opérations/entretien effectués | 1 |
| Autoviza: sinistres / réparations à dire d'expert (points d'attention) | 1 |
| Autoviza: usage privé uniquement | 1 |
| Autoviza: usages antérieurs détectés (taxi/VTC/auto-école) | 1 |
| AutoWriter (descripcion IA especifica del vehiculo) | 1 |
| Aux belt / pulley noise | 1 |
| Auxiliary Operations | 1 |
| Availability Index (inventory/supply levels) | 1 |
| availability_status | 1 |
| availabilityVerified | 1 |
| availableFrom | 1 |
| availableUntil | 1 |
| Avec livraison (filtre) | 1 |
| Average age (months) | 1 |
| Average comparable price ($) | 1 |
| Average EV transaction price | 1 |
| Average LCV/van selling price | 1 |
| average_paid_price | 1 |
| Average Price (Avg) | 1 |
| Average retail sold price (por vehiculo) | 1 |
| Average Sale (Moving Average) | 1 |
| Average sale value | 1 |
| Average Selling Price (ASP) | 1 |
| Average time to sell | 1 |
| Average used car selling price (£) | 1 |
| average wheel track (avg-rozstaw-kol) | 1 |
| averageEVBH | 1 |
| averageGrade | 1 |
| AVILOO FLASH test report + score | 1 |
| [EQUIP·Seguridad] Aviso de cinturón en todas las plazas | 1 |
| [EQUIP·Seguridad] Aviso de colisión frontal y frenado autónomo de emergencia (AEB) | 1 |
| [EQUIP·Seguridad] Aviso de colisión trasera | 1 |
| award citation | 1 |
| award criteria (engine/transmission-specific) | 1 |
| award name | 1 |
| award snippet | 1 |
| award source/awarding party | 1 |
| award type | 1 |
| award website | 1 |
| Awards (window sticker / merchandising) | 1 |
| Axle Configuration | 1 |
| axle_ratio | 1 |
| axle spacing (rozstaw osi) [Moj Pojazd] | 1 |
| [EQUIP·Seguridad] Ayuda de aparcamiento delantero | 1 |
| [EQUIP·Seguridad] Ayuda de aparcamiento trasero | 1 |
| [EQUIP·Seguridad] Ayuda de arranque en cuesta | 1 |
| AZT paint data | 1 |
| B2B: Lead (cobro por lead) | 1 |
| B2B: price per report / ahorro | 1 |
| B2B: Virtual online showroom | 1 |
| Back-end gross (store historical, by MMT) | 1 |
| Backup Camera | 1 |
| Bad/branded VHR (carfax_has_bad_vhr) | 1 |
| Badge condicional de precio (conditionalPriceBadge) | 1 |
| Badge: CPO Badge (manufacturer-certified pre-owned) | 1 |
| badge venta urgente (车主急售) | 1 |
| BadgeDetail / 세부등급 (sub-trim) (+ EnglishName) | 1 |
| Baja definitiva — motivo (desguace/agotamiento/antigüedad/renovación/exportación/oficio abandono/oficio seguridad/tratamiento residual) | 1 |
| Baja telemática ('En desguace') | 1 |
| Baja telemática / En desguace (BAJA_TELEMATICA) | 1 |
| Baja temporal (IND_BAJA_TEMP) | 1 |
| Bajas | 1 |
| Bajas de propiedad (deregistrations) | 1 |
| balloon note payment | 1 |
| bank_fees | 1 |
| Barómetro: precio medio del seminuevo (€) + variación (%) | 1 |
| Barómetro: precio medio por Comunidad Autónoma (€) + ranking | 1 |
| Barómetro: precio medio por franja de antigüedad (€ + %) | 1 |
| Barómetro: récord histórico de precio (€ + fecha) | 1 |
| Barómetro: variación del precio por CCAA (%) | 1 |
| Barómetro: variación interanual del precio medio (%) | 1 |
| Barómetro: variación mensual del precio medio (%) | 1 |
| Baremo de pintura (CESVIMAP/Centro Zaragoza/fabricante/manual) | 1 |
| baremo de pintura EUROLACK (DAT-Eurolack) | 1 |
| Barra estabilizadora delantera | 1 |
| Barra estabilizadora trasera | 1 |
| Base Imponible | 1 |
| Base MMR (precio mayorista medio de transacciones recientes, excl. outliers) | 1 |
| Base MMR value (wholesale average) | 1 |
| Base Price ($) | 1 |
| base_towing_capacity | 1 |
| Base valuation (₹) | 1 |
| Base value (por cada tipo de valor) | 1 |
| Base Vehicle Value | 1 |
| baseInvoice | 1 |
| basePrice | 1 |
| basic_equipment_info | 1 |
| Batalla (mm) | 1 |
| Batería: Capacidad útil (kWh) | 1 |
| Batería: Capacidad total (kWh) | 1 |
| Batería: Situación | 1 |
| Batería: Tipo | 1 |
| Baureihe (serie del modelo) | 1 |
| Beauty images | 1 |
| bed_code | 1 |
| Bed Type | 1 |
| bedrijf_adres (straat/huisnummer/postcode/plaats) | 1 |
| Behavior Prediction Score (0-100) | 1 |
| Behavioural risk indicators | 1 |
| Beleihungswert [NO-VERIFICADO] | 1 |
| benchmark comparison (equitable, local-preference adjusted) | 1 |
| benchmark de precision vs competidores | 1 |
| Benchmark VR vs competidores | 1 |
| Benchmarking coste medio propio vs mercado por tipo de vehículo | 1 |
| benchmarks (10+ countries) | 1 |
| benefitStatement.definition | 1 |
| benefitStatement.statement | 1 |
| benefitStatement.title | 1 |
| beschaedigte Teile (piezas danadas detectadas por IA) | 1 |
| beschrijving_van_het_herstel | 1 |
| Best Buy Award (segment + overall) | 1 |
| Best Resale Value Award (5-yr % retained) | 1 |
| Best sale route / channel recommendation | 1 |
| Best time to contact (0-3) | 1 |
| Bestand / Angebotsvolumen (stock/supply volume + vs pre-Corona) | 1 |
| bestMatch (mejor coincidencia de configuración) | 1 |
| BEV-Erfahrung / BEV-Kaufabsicht (experiencia/intencion de compra VE) | 1 |
| BEV/PHEV/ICE mix % by market | 1 |
| Bewertungs-Details (adjusted value) | 1 |
| bid / bidding history (puja/historial de pujas) | 1 |
| Bid increments (£50 / £100 / £200) | 1 |
| BID4U (proxy bid) | 1 |
| Bidder counts (market activity) | 1 |
| BidFast purchase offer amount (30-day validity) | 1 |
| Bids per vehicle / total bids | 1 |
| bijzonderheid_code | 1 |
| bijzonderheid_code_omschrijving | 1 |
| bijzonderheid_eenheid | 1 |
| bijzonderheid_variabele_tekst | 1 |
| Bilder (images) | 1 |
| Bill reimbursement recommendation (casualty) | 1 |
| Billboards (branding/ofertas del dealer) | 1 |
| Black Book real-time price (US, embebido en VDP) | 1 |
| Black Book Vehicle ID | 1 |
| Black Book Wholesale Average | 1 |
| Blacklist / RC status | 1 |
| Blend procedures | 1 |
| Blended incentive spend | 1 |
| Blind Spot Intervention (BSI) | 1 |
| Blind Spot Warning (BSW) | 1 |
| block_type | 1 |
| Bloqueos / restricciones | 1 |
| Bluetooth | 1 |
| Bluetooth Connectivity | 1 |
| Blur detection / photo quality validation | 1 |
| Boîte de vitesse | 1 |
| Body / structure data | 1 |
| Body Class | 1 |
| Body condition | 1 |
| body_config | 1 |
| body_config_type | 1 |
| Body repair defects | 1 |
| bodyName / 차종 (carrocería) | 1 |
| Bodywork (carroceria) | 1 |
| bolt_pattern | 1 |
| Booking Assistant eyeCatcher highlight | 1 |
| Booking Assistant topOfPage placement | 1 |
| Booking/scheduling slot (inspection/maintenance) | 1 |
| Bookmark / save count | 1 |
| Books de valor (integrados) | 1 |
| boot / luggage capacity [PARCIAL] | 1 |
| boot interior photo (empty) | 1 |
| Boot Opening | 1 |
| Boot Space | 1 |
| boot.capacity (volume coffre) | 1 |
| boot.maximum-capacity | 1 |
| boot.minimum-capacity | 1 |
| boot.third-row-capacity | 1 |
| Borderline total-loss flag | 1 |
| bounds.retail.lower | 1 |
| bounds.retail.upper | 1 |
| bounds.trade.lower | 1 |
| bounds.trade.upper | 1 |
| Bouwjaar (entrada manual) | 1 |
| boxStyle | 1 |
| BPM (impuesto matriculación) | 1 |
| BPM según informe de tasación (tegenbewijsregeling) | 1 |
| BPM según koerslijst (lista de cotización) | 1 |
| BPM-indicatie (estimación previa) | 1 |
| Brake energy recovery | 1 |
| brake_fluid | 1 |
| Brake fluid level | 1 |
| Brake lights | 1 |
| Brake pad replacement timing & cost | 1 |
| Brake pedal pressure / servo assistance | 1 |
| Brake System Description | 1 |
| Brake System Type | 1 |
| Brake wear indicator light | 1 |
| brakedTowingCapacity (capacidad arrastre con freno) | 1 |
| Brakes condition | 1 |
| Brakes score | 1 |
| Brakes, wheels & tyres [128] | 1 |
| braking_distance | 1 |
| Branch | 1 |
| branded_title | 1 |
| Branded Title flag/value | 1 |
| Branding/title: Inactive designation | 1 |
| Branding/title: Lemon / CAMVAP designation | 1 |
| Branding/title: Rebuilt title | 1 |
| Brandstof | 1 |
| brandstof_omschrijving (tipo combustible) | 1 |
| brandstof_verbruik_gecombineerd_wltp | 1 |
| brandstof_verbruik_gewogen_gecombineerd_wltp | 1 |
| brandstofverbruik_gecombineerd_nedc | 1 |
| brandstofverbruik_gewogen_gecombineerd | 1 |
| breakover_angle | 1 |
| breedte | 1 |
| breedte_ondergrens_bovengrens | 1 |
| Broadcasting de anuncios a portales | 1 |
| bruto_bpm (impuesto matriculacion bruto) | 1 |
| build_code | 1 |
| build_data.feature.code | 1 |
| build_data.feature.value | 1 |
| Build quality [RV driver] | 1 |
| Build quality factor | 1 |
| build rules | 1 |
| build_sheet_factory_data | 1 |
| buildDate | 1 |
| buildSource | 1 |
| buildyear | 1 |
| built | 1 |
| bulk file content description (opis-zawartosci) [Pliki] | 1 |
| bulk file creation date (data-utworzenia-pliku) [Pliki] | 1 |
| bulk file format description (opis-formatu-pliku) [Pliki] | 1 |
| bulk file metadata URL (url-do-metadanych-pliku) [Pliki] | 1 |
| bulk file resource type, e.g. pojazdy (typ-zasobu-bedacego-zawartoscia) [Pliki] | 1 |
| bulk file URL (url-do-pliku) [Pliki] | 1 |
| Bulk Pricing (upload CSV/Excel, resultado <10s) | 1 |
| Bulk Report Download (basic / premium) | 1 |
| Bulk valuation (CSV/list upload) | 1 |
| Bus Floor Configuration Type | 1 |
| Bus Type | 1 |
| Business KPI: QARSD (Quarterly Average Revenue per Subscribing Dealer) | 1 |
| Business rules / auto-approval / reduccion de suplementos | 1 |
| Buy fee | 1 |
| buy_now_price | 1 |
| buy order: desired condition | 1 |
| buy order: desired price (limite) | 1 |
| buy order: quantity / quota | 1 |
| Buy Plan Indicator (green star — fit to store buy plan) | 1 |
| Buy-it-now price recommendation | 1 |
| Buy-Through Rate (BTR) | 1 |
| buy/sell (network action) | 1 |
| Buyback compensation (hasta 110% J.D. Power NADAguides retail + $500 accesorios) | 1 |
| Buyback guarantee | 1 |
| buyback_guarantee_eligibility_flag | 1 |
| buyback_payout_110pct_of_hbv | 1 |
| Buyback Protection eligibility | 1 |
| Buyback Protection eligibility / badge | 1 |
| Buyer fee (Cost Calculator) | 1 |
| Buyer fees financiados | 1 |
| Buyer fees per vehicle | 1 |
| Buyer transaction fee | 1 |
| buying preference | 1 |
| BuyType (Delivery) | 1 |
| by GVW (gross vehicle weight) class | 1 |
| by OEM market | 1 |
| by supplier / company (223 suppliers) | 1 |
| Código 55 (importe fijo de pintura) | 1 |
| Código de clase de matrícula | 1 |
| código de homologación (homoloCode, cruce RUNT) | 1 |
| Código de procedencia | 1 |
| Código de servicio del vehículo | 1 |
| Código de tipo de vehículo | 1 |
| código Fasecolda (8 dígitos, único; 3 marca + 2 tipología + 3 consecutivo) | 1 |
| Código INE de municipio (COD_MUNICIPIO_INE_VEH) | 1 |
| Código INE del municipio | 1 |
| Código Molicar / Código KBB-Molicar (CodMolicar) — join key | 1 |
| Código opcional (descripción) | 1 |
| Código postal del domicilio | 1 |
| Códigos de pintura | 1 |
| cálculo estructurado de reparaciones | 1 |
| cámara de reversa SI/NO (reverseCameraShow) | 1 |
| [EQUIP·Seguridad] Cámara de visión 360º | 1 |
| [EQUIP·Seguridad] Cámara de visión trasera | 1 |
| câmbio / transmissão | 1 |
| C-PAS追加画像 (up to 9 seller custom images) | 1 |
| Cab Type | 1 |
| CADSI: 3-month outlook | 1 |
| CADSI: costs | 1 |
| CADSI: current market | 1 |
| CADSI: customer traffic | 1 |
| CADSI: EV sales sentiment | 1 |
| CADSI: F&I | 1 |
| CADSI: limiting factors | 1 |
| CADSI: índice overall (0=débil / 50=estable / 100=fuerte) | 1 |
| CADSI: price pressure | 1 |
| CADSI: profitability | 1 |
| Calc: affordability | 1 |
| Calc: auto loan payment | 1 |
| Calc: lease payment | 1 |
| Calc: lease vs buy | 1 |
| Calcolo IVA (iva inclusa / IVA al 40%) | 1 |
| Calculation window (~13 months) | 1 |
| Calculo de coste de reparacion | 1 |
| Calculo de danos / repair estimate (Speedy-Zone) | 1 |
| Calendario de mantenimiento (prevision) | 1 |
| calibrations_dynamic_static | 1 |
| Cam | 1 |
| cam_type | 1 |
| campaign analytics / bid optimization metric | 1 |
| Campaign Description | 1 |
| campaign_number | 1 |
| campaignNo | 1 |
| Camshaft drive | 1 |
| canal de comunicación | 1 |
| candidate.quote-ratio (popularidad/probabilidad) | 1 |
| candidate.suggested (mejor match) | 1 |
| CAP Clean peak (%) | 1 |
| CAP Clean performance (%) | 1 |
| CAP Clean price (reference filter) | 1 |
| CAP Code (vehicle identifier) | 1 |
| CAP Code identifier | 1 |
| CAP ID | 1 |
| cap value movements | 1 |
| Capacidad (pasajeros/carga) | 1 |
| capacidad de carga kg (capacityLoad) | 1 |
| capacidad de pasajeros (capacityPassengers) | 1 |
| CapacitaBagagliaio1dm | 1 |
| CapacitaBagagliaio2dm | 1 |
| CapacitaBagagliaio3dm | 1 |
| CapacitaLordakWh | 1 |
| CapacitaNettakWh | 1 |
| CapacitaSerbatoioKg | 1 |
| CapacitaSerbatoioL | 1 |
| capacity_cc | 1 |
| Capilaridad de red secundaria | 1 |
| captura de volatilidad / eventos black swan | 1 |
| Car Buyer Journey (tiempo de compra, satisfacción, canales online/offline) | 1 |
| car_city | 1 |
| Car Loan eligibility/EMI (Rupyy) | 1 |
| car policy details | 1 |
| Car rankings (por tipo de vehiculo) | 1 |
| car_state | 1 |
| car_street | 1 |
| car_type (comparison factor) | 1 |
| 车型/款型/car_type_id (model/trim input) | 1 |
| Car Values output: IMV (retail price) | 1 |
| Car Values output: Private Sale Value / Private Sale Estimate | 1 |
| car_zip | 1 |
| características da venda | 1 |
| Caracteristicas de uso/desgaste | 1 |
| Caramel escrow/title-transfer status | 1 |
| Caratteristiche tecniche / scheda tecnica completa | 1 |
| carfax_clean_title | 1 |
| carfax_integration (iVIN Pro) | 1 |
| carfax_related_documents | 1 |
| CARFAX Smart Field (one-owner/clean history) | 1 |
| carfax_snapshot (accidents/damage+severity/open recalls/last odometer/usage/owners/service/CPO) | 1 |
| CARFAX Status (badge/check/caution) | 1 |
| carfax_vehicle_condition_alert | 1 |
| [EQUIP·Varios] Carga bidireccional V2L (3 kW) | 1 |
| Carga: Hipoteca mobiliaria | 1 |
| [EQUIP·Multimedia] Carga inalámbrica para smartphone 15W (2 puntos) | 1 |
| Carga: Leasing | 1 |
| Carga: Potencia máxima CA (kW) | 1 |
| Carga: Potencia máxima CC (kW) | 1 |
| Carga: Precinto | 1 |
| Carga: Renting | 1 |
| Carga: Tiempo de carga 10-80% en CC | 1 |
| Carga/gravamen — Hipoteca Mobiliaria | 1 |
| Carga/gravamen — Leasing | 1 |
| Carga/gravamen — Precinto | 1 |
| cargo_room | 1 |
| cargo_volume_rear_seats_down | 1 |
| cargo_volume_row3_down | 1 |
| CarGurus Index (aggregate avg used-car price, UK & US) | 1 |
| CarOffer: ~45-day sell guarantee (histórico) | 1 |
| CarOffer Buying Matrix: standing buy orders / limit orders / quotas | 1 |
| CarOffer: Instant Max Cash Offer (IMCO, consumer cash offer) | 1 |
| CarOffer TradeGrade: instant offer in appraisal tool (trade-ins/lease returns/auction cars) | 1 |
| carOrigin / vehicleOrigin | 1 |
| carOriginDescription | 1 |
| Carpets condition | 1 |
| CarPlay/CarLife | 1 |
| Carrier total-loss threshold | 1 |
| carrosserie_national (J.3) | 1 |
| carrosserie_UE (J.2) | 1 |
| carrosseriecode (EU 2007/46/EG) | 1 |
| carrosserietype | 1 |
| Carrozzeria | 1 |
| carsales_approved_badge_4star_160k_10y | 1 |
| Écart à la cote / valuation gap (valor autobiz vs precio publicado) | 1 |
| CarValue: % to Retail | 1 |
| CarValue: factores ML (depreciacion, estacionalidad, macro, odometro, CR, sale location) | 1 |
| CarValue: input bid + fees | 1 |
| CarValue: input recon cost | 1 |
| CarValue: input transport cost | 1 |
| CarValue: Profit Calculator (Retail - Transport - Recon - Bid/fees = profit) | 1 |
| CarValue: Retail-Bid Spread | 1 |
| CasaCostruttrice | 1 |
| cash contributions | 1 |
| Cash For Clunkers eligibility | 1 |
| Catálogo: comparador de coches (lado a lado) | 1 |
| Catálogo: precios por versión | 1 |
| Catalizzata | 1 |
| catalytic converter / absorber fitted (katalizator-pochlaniacz) | 1 |
| Catastrophic modeling value (insurance) | 1 |
| categoría (category: liviano pasajeros/liviano carga/motos/pesado carga/pesado pasajeros) | 1 |
| Categoría de homologación europea (M1/N1/L…) | 1 |
| Categoría de homologación UE (M1/N1/L…) | 1 |
| categorie_defect | 1 |
| categorie_UE (J) | 1 |
| category.EPAClass | 1 |
| category.market | 1 |
| category.name | 1 |
| category.primaryBodyType | 1 |
| category.vehicleSize | 1 |
| category.vehicleStyle | 1 |
| category.vehicleType | 1 |
| Causa de variacion de VR (facelift, efecto lanzamiento) | 1 |
| Cavity Protection Matrix (UK) | 1 |
| CCPA consent | 1 |
| CCTV / security status | 1 |
| Ce que l'IA a repéré (équipements destacados) | 1 |
| Cell-maker tracking | 1 |
| Census: date sold | 1 |
| Census: distance & drive time to retail | 1 |
| Census: market trends & forecasting | 1 |
| Census: sales opportunity quantification | 1 |
| Census: vehicle age | 1 |
| Census: vehicle types (cars/LCV/HGV/bikes/motorhomes/agricultural) | 1 |
| center_bore | 1 |
| central vs store-level offer control | 1 |
| centralLocking | 1 |
| Certificado de Conformidad (CoC) | 1 |
| Certificado DGT de transferencia de responsabilidad | 1 |
| certificate_of_destruction_issued | 1 |
| certificate_of_title | 1 |
| certificate.created_at | 1 |
| certificate.id | 1 |
| certificate.url (PDF) | 1 |
| certified / CPO badge | 1 |
| certified_pre_owned_cpo_indicator | 1 |
| Certified Pre-Owned / Courtesy buyback | 1 |
| Certified Pre-Owned (CPO) premium value | 1 |
| Certified Pre-Owned (CPO) price | 1 |
| CertiFirst certification status | 1 |
| change-of-address / append | 1 |
| Charge lead 1 condition (OEM or not) | 1 |
| Charge lead 2 condition | 1 |
| Charge port condition | 1 |
| Charger Level | 1 |
| ChargeSust_Comb | 1 |
| ChargeSustaining | 1 |
| chart / table auto-generation (1-click) | 1 |
| chassisVin (VIN) | 1 |
| Chat 24/7 (CarGurus rep on listing) | 1 |
| Check performed date/time | 1 |
| Check reference number | 1 |
| Cherished plate transfers | 1 |
| child_occupant_protection_score | 1 |
| Child Safety Locks | 1 |
| Chilometraggi rilevati alle revisioni (km history) | 1 |
| Chilometraggio all'ultima revisione | 1 |
| ChilometriTeorici | 1 |
| ChilometriTeoriciMensili | 1 |
| ChilometriTeoriciStandard | 1 |
| China EV sales (monthly units, macro) | 1 |
| Chrome ACode | 1 |
| chrome_body_id | 1 |
| Chrome extension overlay | 1 |
| Chrome YMMID | 1 |
| chromeCode | 1 |
| CI_annule | 1 |
| CI_date_annulation | 1 |
| CI_declare_perdue | 1 |
| CI_declare_volee | 1 |
| CI_duplicata | 1 |
| CicliWltp | 1 |
| CicliWltpHybrid | 1 |
| ciclo de vida del vehículo | 1 |
| Ciclo de vida del vehiculo (altas/bajas/transferencias) | 1 |
| [EQUIP·Confort] Cierre centralizado | 1 |
| [EQUIP·Seguridad] Cierre de seguridad para niños en puertas traseras | 1 |
| CIF del taller | 1 |
| cilinderinhoud | 1 |
| cilindraje cc (cylinderCapacity) | 1 |
| Cilindrata | 1 |
| CilindrataA | 1 |
| CilindrataDa | 1 |
| CIN (Codigo de Identificacion del Navio) | 1 |
| [EQUIP·Seguridad] Cinturones delanteros regulables en altura | 1 |
| City-level ICE comparison sales | 1 |
| ciudad (城市) | 1 |
| Claim cost (KPI) | 1 |
| Claim number | 1 |
| Claim reference number | 1 |
| claim.claimID | 1 |
| claim.claimNumber | 1 |
| claim.claimValuation | 1 |
| claim.reportURL | 1 |
| Claimant name | 1 |
| Claims Companion condition assessment | 1 |
| Claims management | 1 |
| Claims payout value | 1 |
| Clase de matrícula (ordinaria/turística/remolque/diplomática/reservada/especial/ciclomotor/temporal/histórica) | 1 |
| Clasificación pérdida total vs reparable por foto (Intelligent Triage) | 1 |
| classe_CritAir_vignette (derivada: 1-5/ELECTRIQUE/NON_CLASSE) | 1 |
| classe_environnementale_UE (V.9) | 1 |
| Classe Euro | 1 |
| ClasseEuro | 1 |
| classic_drive | 1 |
| classic_fuel | 1 |
| CLASSIC.COM Market Benchmark (CMB) | 1 |
| classificatie_toegevoegd_object | 1 |
| Clave de trámite | 1 |
| Clave del trámite (CLAVE_TRAMITE) | 1 |
| Clave vehicular | 1 |
| ClearCar Capture (AI imaging + self-inspection) | 1 |
| ClearCar Price (digital value estimate widget en web del dealer) | 1 |
| Click rates | 1 |
| Climate control / Air conditioning | 1 |
| climatisation | 1 |
| [EQUIP·Confort] Climatización por bomba de calor | 1 |
| [EQUIP·Confort] Climatizador bizona | 1 |
| Cloned / false identity | 1 |
| Cloned / false identity indicator | 1 |
| 续航 CLTC | 1 |
| clutch | 1 |
| Clutch slip test | 1 |
| CMB trend direction (flecha up/down) | 1 |
| Co-Driver: AI vehicle description | 1 |
| Co-Driver: missing image detection | 1 |
| Co-Driver: optimal image ordering | 1 |
| co2Class | 1 |
| CO2Combinato | 1 |
| CO2CombinatoMassimo | 1 |
| CO2CombinatoMinimo | 1 |
| cO2Combined (CO2 combinado) | 1 |
| CO2ExtraHigh | 1 |
| CO2High | 1 |
| CO2Low | 1 |
| CO2Medium | 1 |
| CO2Wltp | 1 |
| Cobertura 100% del hammer price | 1 |
| Cobertura del mercado objetivo | 1 |
| Cobertura territorial | 1 |
| Cockpit: crédito pré-aprovado del comprador | 1 |
| Cockpit: leads / contatos (CRM) | 1 |
| Cockpit: performance do negócio / indicadores | 1 |
| cocNumber | 1 |
| Code Boost IQ: banner OBD2 nivel 'Confirmed trouble codes' | 1 |
| Code Boost IQ: banner OBD2 nivel 'High probability of repair needed' | 1 |
| Code Boost IQ: banner OBD2 nivel 'No trouble codes' | 1 |
| Code Boost IQ: probabilidad predictiva de reparacion / arbitraje | 1 |
| code_mogelijk_gevaar (ONG/TEL/BRA/MIL) | 1 |
| Code postal | 1 |
| code_toelichting_tellerstandoordeel | 1 |
| code_wijze_informeren (BRI/BEL/ADV/NTB) | 1 |
| codelinksrechtsrijdend | 1 |
| Codice connettore (EV) | 1 |
| Codice motore | 1 |
| CodiceAlimentazione | 1 |
| CodiceAllestimento | 1 |
| CodiceCasa | 1 |
| CodiceCasaCostruttrice | 1 |
| CodiceCombustibile | 1 |
| CodiceEquipaggiamento | 1 |
| CodiceInfobikePRG | 1 |
| CodiceInfocar | 1 |
| CodiceInfocarAM | 1 |
| CodiceInterni | 1 |
| CodiceModalitaMisuraTempo | 1 |
| CodiceModalitaRicarica | 1 |
| CodiceMotivazione | 1 |
| CodiceMotore | 1 |
| CodiceNucleoMotore | 1 |
| CodiceOmologazione | 1 |
| CodiceOptEscluso | 1 |
| CodiceOptIncluso | 1 |
| CodiceOptVincolato | 1 |
| CodiceQRTIncomp | 1 |
| CodiceRCLPrg | 1 |
| CodiceRT | 1 |
| CodiceRuoteClassiche | 1 |
| CodiceSerie | 1 |
| CodiceSpeciale | 1 |
| CodiceSpia | 1 |
| CodiceStruttura | 1 |
| CodiceSVG | 1 |
| CodiceTipoBatterie | 1 |
| CodiceTipoPresa | 1 |
| CodiceVIN | 1 |
| CodiciAutoscout | 1 |
| CodificaAS24 | 1 |
| codigo_fipe (formato XXXXXX-X, 7 dígitos) | 1 |
| Codigo unico de vehiculo Eurotax / NatCode (codificacion paneuropea) | 1 |
| coding type of type-subtype-purpose (rodzaj-kodowania-rodzaj-podrodzaj-przeznaczenie) | 1 |
| Coeficiente aerodinámico Cx | 1 |
| collateral_validation_type_condition | 1 |
| Comb_Weighted | 1 |
| Combination prices | 1 |
| Combined Braking System (CBS) | 1 |
| combined_litres_100km | 1 |
| combustível | 1 |
| Combustibile | 1 |
| comfort & convenience features | 1 |
| comfort_features | 1 |
| Commentaire du vendeur | 1 |
| Commercial new & used residual monitor | 1 |
| Commercial trailer type (11 types) | 1 |
| commercial use (taxi/rental/lease/fleet/police) | 1 |
| commercial-to-private market transition | 1 |
| Common Problems (problemas mas probables del VIN) | 1 |
| communautaire_codes_eu (codigos del kentekenbewijs J/D/R/K/B/I/G/F/O en OVI) | 1 |
| Comp relevance score (%) | 1 |
| company activity / industry (branch) | 1 |
| company address | 1 |
| company car flag | 1 |
| company car taxation (BIK) | 1 |
| company contact details | 1 |
| company financials | 1 |
| company innovations | 1 |
| company news & key developments | 1 |
| company profile | 1 |
| Company-owned deduction (רכב חברה) | 1 |
| company/fleet detail (contact/title/phone/revenue/employees/SIC) | 1 |
| companystockOwner | 1 |
| companystockType | 1 |
| Comparable adjusted value | 1 |
| Comparable: build quality | 1 |
| Comparable City/State (proximity) | 1 |
| Comparable condition reports | 1 |
| Comparable data source (Vast / Cars.com / Leading Internet Auto Site) | 1 |
| Comparable date observed | 1 |
| Comparable equipment list | 1 |
| comparable listings (comp set) | 1 |
| Comparable rank # | 1 |
| Comparable recently sold vehicles | 1 |
| Comparable sale: condicion del ejemplar | 1 |
| Comparable: sale date | 1 |
| Comparable sale: fecha de venta | 1 |
| Comparable sale: fotos | 1 |
| Comparable sale: fuente / casa de subasta | 1 |
| Comparable sale: market commentary (comentario de mercado) | 1 |
| Comparable sale: notas de equipamiento/opciones | 1 |
| Comparable: sale price | 1 |
| Comparable Stock # | 1 |
| Comparable vehicle: Distance (straight-line to loss) | 1 |
| Comparable vehicle: Take Price | 1 |
| comparable vehicles (side-by-side) | 1 |
| Comparable vehicles nearby (listings) | 1 |
| comparable_vehicles_side_by_side (year/make/model/trim/options/location/mileage/history) | 1 |
| comparables | 1 |
| # comparables located | 1 |
| comparables_scatter_chart (vs linea de market price) | 1 |
| Comparacion de precios | 1 |
| comparacion multi-vehiculo de curvas RV | 1 |
| Comparador de Precios Avanzado (precio vs competencia/mercado) | 1 |
| ComparazionePrezzo | 1 |
| Compare Similar Vehicles (features/performance) | 1 |
| competition level (number of competing vehicles) | 1 |
| Competitive analysis | 1 |
| Competitive derivative comparison | 1 |
| Competitive residual analysis (quarterly) | 1 |
| competitive RV benchmark | 1 |
| Competitive sales trends (Elite) | 1 |
| Competitive set (identicos en mercado vivo) | 1 |
| competitive win/loss (media planning) | 1 |
| Competitive win/loss through service over time | 1 |
| competitor_strategies | 1 |
| Competitor View (similar stock in market) | 1 |
| complete_customer_profile_truecar_access | 1 |
| completed_repairs (CA) | 1 |
| completedDate (mot test) | 1 |
| Compliance date (NEVDIS) | 1 |
| compliance_plate | 1 |
| complianceDate (ISO-8601, primer dia del mes/anyo) | 1 |
| Comportamiento real de mercado | 1 |
| composite group financial benchmark | 1 |
| ComposizionePack | 1 |
| comprador del vehículo | 1 |
| compression | 1 |
| Compromiso (SI/NO) | 1 |
| Comunidad Autónoma (nivel de agregación) | 1 |
| Concealed proxy bid | 1 |
| Concept strengths/weaknesses (perceived quality) [RV driver] | 1 |
| Condición itemCondition (nuevo/ocasión/km0/seminuevo) | 1 |
| Condicion/defectos de interior | 1 |
| Condition #1 (Concours) value | 1 |
| Condition #2 (Excellent) value | 1 |
| Condition #3 (Good) value | 1 |
| Condition #4 (Fair) value | 1 |
| condition_confirmed_inperson | 1 |
| Condition description text per sub-category (Typical Condition Statement) | 1 |
| Condition flags (Inspection / Record / Resume) | 1 |
| Condition of body (CR) | 1 |
| Condition preferences (warning lights/tire/frame/title) | 1 |
| Condition questionnaire | 1 |
| Condition Rating (per component, appraiser-selected) | 1 |
| Condition rating score (escala 10 puntos por aspecto: interior, frenos, neumaticos) | 1 |
| Condition rating value impact | 1 |
| condition_score (1-5: Poor/Fair/Average/Good/Excellent) | 1 |
| Condition tier definition / guidelines (rollover por condicion) | 1 |
| Condition-adjusted price (Great/Good/Fair) | 1 |
| Condition-adjusted valuation | 1 |
| Condition-based offers | 1 |
| condition.seizing (gravámenes / 압류 / embargo, con conteo) | 1 |
| conditionsRequired (Clean/Average/Below/Retail) | 1 |
| Conductor habitual designado | 1 |
| [EQUIP·Multimedia] Conexión Bluetooth para teléfono | 1 |
| confidence (match quality: standard) | 1 |
| Confidence of Sale (probability within target days) | 1 |
| Confidence score | 1 |
| confidence-index (índice de confianza) | 1 |
| confidence-intervals.max | 1 |
| confidence-intervals.min | 1 |
| confidence-intervals.probability | 1 |
| confidenceInterval.priceRange.adjustedHigh | 1 |
| confidenceInterval.priceRange.adjustedLow | 1 |
| configuraciones de fábrica | 1 |
| Confische (presenza) | 1 |
| Confronto annunci propri vs competitor | 1 |
| Confronto fino a 3 veicoli | 1 |
| conquest / competitor audience (customizable) | 1 |
| conquest / new customer acquisition | 1 |
| conquest rate (network) | 1 |
| Cons (Could Be Better) | 1 |
| Consolidated Condition Report (single VDP view, 2025) | 1 |
| Consommation (L/100km) | 1 |
| Consommation Faible (flag) | 1 |
| Consommation max (filtre) | 1 |
| Constancia de aseguramiento | 1 |
| constructionDate | 1 |
| constructionMonth | 1 |
| consultoría / soporte al negocio | 1 |
| Consumer category ratings | 1 |
| consumer_complaints | 1 |
| Consumer demographics (Elite) | 1 |
| Consumer email | 1 |
| Consumer first/last name | 1 |
| Consumer Intelligence - buy/sell preference analytics | 1 |
| Consumer Intelligence - market overview | 1 |
| consumer market value estimate (estimacion de valor de mercado) | 1 |
| Consumer number of reviews | 1 |
| Consumer Offer Report (inputs de valoracion + deducciones) | 1 |
| Consumer Overall Rating (of 5) | 1 |
| Consumer Overall star rating (of 5) | 1 |
| Consumer phone / cell_phone | 1 |
| Consumer postal_code (factor regional de pricing) | 1 |
| consumer_preferences | 1 |
| Consumer rating: comfort | 1 |
| Consumer rating count (based on N ratings) | 1 |
| Consumer rating: performance | 1 |
| Consumer rating: quality | 1 |
| Consumer rating: reliability | 1 |
| Consumer rating: styling | 1 |
| Consumer rating: value | 1 |
| Consumer recommend % | 1 |
| Consumer Review (owner) | 1 |
| Consumer review date | 1 |
| Consumer review text | 1 |
| Consumer Satisfaction Award | 1 |
| Consumer star distribution (5★-1★) | 1 |
| Consumer Summary (AI-generated) | 1 |
| Consumer Verified Rating - driving experience | 1 |
| Consumer Verified Rating - quality & reliability | 1 |
| Consumer Verified Rating - service experience | 1 |
| consumerInformation.item.conditionNote | 1 |
| consumerInformation.item.name | 1 |
| consumerInformation.item.value | 1 |
| consumerInformation.type | 1 |
| Consumerprice (precio de consumo/lista) | 1 |
| consumerPriceGross | 1 |
| consumerPriceNet | 1 |
| ConsumiWltp | 1 |
| contact.address (ubicación dealer) | 1 |
| contact.userType / userId (tipo de vendedor) | 1 |
| Contacto de flota (direccion/telefono/email) | 1 |
| contents.text (descripción del dealer) | 1 |
| Conteo mensual de anunciantes profesionales por red | 1 |
| [EQUIP·Decoración] Contorno de ventanillas cromado | 1 |
| Contract equity | 1 |
| contribución al PIB (%) | 1 |
| [EQUIP·Seguridad] Control de crucero adaptativo (ACC) | 1 |
| [EQUIP·Seguridad] Control de crucero inteligente | 1 |
| [EQUIP·Seguridad] Control de estabilidad (ESP) | 1 |
| Control de estabilidad/ESP | 1 |
| [EQUIP·Seguridad] Control de presión de neumáticos (TPMS) | 1 |
| Control de stock / inventario | 1 |
| [EQUIP·Seguridad] Control de tracción | 1 |
| Control de velocidad | 1 |
| control del valor por etapa del ciclo de vida | 1 |
| controle_technique_date | 1 |
| controle_technique_nature (VTP/VTC/CV/CVC) | 1 |
| controle_technique_nature_libelle | 1 |
| controle_technique_resultat (A/AP/S/SP/R/RP/X) | 1 |
| controle_technique_resultat_libelle (Favorable / Defavorable defaillances majeures / Defavorable defaillances critiques / Report) | 1 |
| controles_techniques_date_mise_a_jour | 1 |
| controles_techniques_donnee_disponible | 1 |
| Conversión UT-hora (10 UT/h; BMW 12 UT/h) | 1 |
| Convertible / sunroof electrics | 1 |
| Convertible roof condition | 1 |
| convertible roof up/down photos (conditional) | 1 |
| Convertible top condition | 1 |
| Coolant system level | 1 |
| cooling | 1 |
| Cooling medium | 1 |
| Cooling Type | 1 |
| CoppiaKgm | 1 |
| CoppiaMaxGiriMinuto | 1 |
| CoppiaNm | 1 |
| copyright | 1 |
| cor | 1 |
| Corrected Title | 1 |
| Corredor de valor (value corridor, rango min-máx) | 1 |
| CorrenteRicaricaAmpere | 1 |
| CorrenteRicaricaRapida | 1 |
| CorrettivoChilometrico | 1 |
| CorrettivoChilometricoApplicato | 1 |
| CorrettivoImmatricolazioneAutocarro | 1 |
| CorrettivoNoteQualificanti | 1 |
| Cosmetic defects | 1 |
| Cosmetic irregularities / paint quality | 1 |
| Cost / pence-per-mile (TCO, derived) | 1 |
| cost_desc | 1 |
| cost_high | 1 |
| cost_low | 1 |
| cost_name_parts_labor | 1 |
| cost_per_sale | 1 |
| cost per unit sold | 1 |
| Cost to Market % (via conexion Provision) [RECONSTRUIDO] | 1 |
| Cost to Market (%) — objetivo 84% / spread 16% | 1 |
| Cost to Market (%) — spread coste adquisicion+recon vs retail medio (benchmark <=84%) | 1 |
| Cost to Run: Fuel/Energy cost (incl EV energy) | 1 |
| Cost to Run: On-road costs (registration, govt duties, CTP insurance, levies) | 1 |
| Cost to Run: Servicing | 1 |
| Cost to Run: Tyres | 1 |
| Cost-to-Market (CTM) indicator | 1 |
| Cost-to-market spread | 1 |
| Coste de equipamiento y accesorios | 1 |
| Coste de garantía | 1 |
| Coste de reacondicionamiento (auto desde grid de costes) | 1 |
| Coste de reparación (Noa) | 1 |
| Coste de transporte por ruta (más rápida vs más barata) | 1 |
| Coste por día en stock | 1 |
| Costes / tiempos de mano de obra | 1 |
| costes de reparación | 1 |
| Costes logísticos / de transporte | 1 |
| Costi aggiuntivi (kit consegna, contributi ambientali, servizi) | 1 |
| Costi di messa su strada (auto-calcolati per provincia) | 1 |
| Costi di riparazione carrozzeria | 1 |
| Costi di riparazione meccanica | 1 |
| costModel co2Costs | 1 |
| costModel fuelPrice | 1 |
| CostoGaranzia | 1 |
| CostoManodopera | 1 |
| CostoOrarioManoOpera | 1 |
| Cote affinée (personnalisée) | 1 |
| Cote Argus® (custom-market-values, cote de référence) | 1 |
| Cote Argus Personnalisée® (web) | 1 |
| Cote brute (valeur véhicule moyen) | 1 |
| Couleurs extérieur | 1 |
| Couleurs intérieur | 1 |
| Country of Assembly | 1 |
| Country of origin / pais de origen | 1 |
| Couple cumulé (Nm @ tr/min) | 1 |
| Coverage stat: 1.3M valuation reports completed in 2024 | 1 |
| Coverage stat: access to 30B+ data records | 1 |
| Coverage stat: access to >90% of all Canadian vehicle listing data | 1 |
| Cox Auto Rates & Incentives (rates/rebates/incentives) | 1 |
| Cox Forecast: fleet sales forecast | 1 |
| Cox Forecast: new-vehicle sales forecast | 1 |
| Cox Forecast: retail sales forecast | 1 |
| Cox Forecast: SAAR | 1 |
| Cox Intelligence: AI-infused MMR valuations | 1 |
| Cox Intelligence: Trade Desk (curación/negociación asistida IA) | 1 |
| Cox Intelligence: Vehicle recommendation score (ML vs perfil de puja/compra) | 1 |
| cpc (Certificate of Professional Competence) | 1 |
| CPO Compliance Review result | 1 |
| CPO data | 1 |
| CPO eligibility | 1 |
| CPO flag | 1 |
| CPO history (history factor) | 1 |
| cpo_indicator | 1 |
| CPO premium ($1,000-$2,000) | 1 |
| CPO program performance | 1 |
| CPO sale flag (99% US coverage) | 1 |
| CPO value (when applicable) | 1 |
| CR additional photos | 1 |
| CR videos (2 internos/externos) | 1 |
| created_at | 1 |
| creationDate | 1 |
| crecimiento interanual del volumen (%) | 1 |
| Credit line / limite de funding | 1 |
| credit score | 1 |
| credit tier | 1 |
| CreditIQ: APR | 1 |
| CreditIQ: down_payment | 1 |
| CreditIQ: instant_loan_approval / decision | 1 |
| CreditIQ: lender_match (BYOL, 800+ lenders) | 1 |
| CreditIQ: loan_term | 1 |
| CreditIQ: penny-perfect monthly_payment | 1 |
| CreditIQ: pre-approval | 1 |
| CreditiTotali | 1 |
| CreditiUsati | 1 |
| Crit'air max (filtre) | 1 |
| CRM / lead management | 1 |
| CRM lead match / Re-Engage (active/unsold by Year-Make-Model) | 1 |
| CRM share | 1 |
| Cross-border admin: aduanas / IVA / BPM | 1 |
| cross-border opportunity / route | 1 |
| Cross-Border Potential Score | 1 |
| cross-border price | 1 |
| Cross-country weighted average value | 1 |
| Cross-market / like-for-like RV comparison | 1 |
| CRS ID (powersports) | 1 |
| Cruise Control | 1 |
| Crush / disposal watch | 1 |
| CTM + PTM+ investment buckets | 1 |
| [EQUIP·Decoración] Cuadro de instrumentos digital de 26 cm (10,25") | 1 |
| cubicCapacity (ccm) | 1 |
| Cuenta atrás de fin de subasta (24h) | 1 |
| Cuentakilómetros — Fecha de lectura | 1 |
| Cuentakilómetros — Origen (ITV/declaración voluntaria/talleres) | 1 |
| cuota % (sobre total) | 1 |
| cuota % de alternativos sobre producción total | 1 |
| Cuota ajustada | 1 |
| Cuota de financiacion (financeRate) | 1 |
| Cuota de leasing / detalles leasing (leasingRate/leasingDetails) | 1 |
| cuota modal logística - carretera % | 1 |
| cuota modal logística - ferrocarril % | 1 |
| cuota modal logística - marítimo % | 1 |
| Cup Holders | 1 |
| Currency code | 1 |
| Current / highest bid | 1 |
| Current bid / High bid | 1 |
| Current bid / price | 1 |
| Current days in stock (input) | 1 |
| current market value (Car Value Tracker) | 1 |
| Current Sale Highlights (comentarios GM) | 1 |
| Current title issue date | 1 |
| Current title state | 1 |
| current_title_status | 1 |
| Current type (AC/DC) | 1 |
| current valuation | 1 |
| Current value | 1 |
| Current value forecast (B2B) | 1 |
| Custom economic scenario residual | 1 |
| Custom Motorcycle Type | 1 |
| Custom recon metrics | 1 |
| Custom repair line items | 1 |
| Customer address: street/house_number/postal_code/city/province/country (lead) | 1 |
| Customer email (lead) | 1 |
| Customer engagement triggers (MOT reminders / pricing updates) | 1 |
| customer_incentives | 1 |
| customer retention (from outgoing model) | 1 |
| Customer salutation/initials/first_name/infix/last_name (lead) | 1 |
| Customer telephone (lead) | 1 |
| Customer-to-car matching | 1 |
| customer.additional_fields | 1 |
| customer.external_id | 1 |
| customer.id | 1 |
| customer.monitor_end_date | 1 |
| customer.monitor_start_date | 1 |
| customer.rego | 1 |
| customer.sale_date | 1 |
| customer.state | 1 |
| customer.vehicle_title | 1 |
| Customer/salesperson signature capture | 1 |
| customerId | 1 |
| customerNumber | 1 |
| customerReferenceNumber (id de peticion) | 1 |
| CVS: Measurements A-G | 1 |
| CVS: Wheelbase (WB) | 1 |
| Cycle time (KPI) | 1 |
| Cycle-time optimization (IntelliSeller) | 1 |
| Cylinder angle (V-engines) | 1 |
| cylinder_arrangement | 1 |
| Cylindrée (cm³) | 1 |
| cylindree_cm3 (P.1) | 1 |
| Días en stock / duración de publicación | 1 |
| Début commercialisation | 1 |
| Délai Argus Rotation® (days-to-sell, mediana de detención) | 1 |
| Daño de llanta/rueda | 1 |
| Daño de panel estructural | 1 |
| Dagwaarde (nombrada en intro; materializa como Vervangingswaarde) | 1 |
| Dagwaarde / vervangingswaarde (valor de día/reposición, excl. IVA y BPM) | 1 |
| Danno | 1 |
| Dashboard: Category/Fuel-type split (PV/CV/3W/2W/EV) | 1 |
| Dashboard: MoM Growth % | 1 |
| dashboard photo (steering wheel + centre console + gearstick) | 1 |
| Dashboard: Total Production (units) | 1 |
| Dashboard: Total Sales (units) | 1 |
| Dashboard: YoY Growth % | 1 |
| DAT Euro-Code (codigo identificador 15 digitos) | 1 |
| data_consulta (timestamp da consulta) | 1 |
| Data di produzione (decode VIN, 2016+) | 1 |
| Data e paese di prima immatricolazione | 1 |
| data entry date (data-wprowadzenia-danych) | 1 |
| Data fine produzione | 1 |
| Data inizio produzione | 1 |
| data plate type (rodzaj-tabliczki-znamionowej) | 1 |
| Data prossima revisione | 1 |
| Data scadenza locazione | 1 |
| Data scadenza patto riservato dominio (PRD) | 1 |
| Data scadenza usufrutto | 1 |
| data_sources_count | 1 |
| data_sources_countries_count | 1 |
| Data ultima revisione | 1 |
| Data ultimo atto di proprieta | 1 |
| DataAttoProprieta | 1 |
| DataCleanse: GDPR-compliant flag por vehiculo | 1 |
| DataCleanse: personal data on documentation (obscured/redacted) | 1 |
| DataCleanse: sat nav destination history (removed) | 1 |
| DataCleanse: synced mobile data (removed) | 1 |
| DataImmatricolazione | 1 |
| DataImmatricolazioneEstera | 1 |
| DataOne VehicleID | 1 |
| DataPrimaImmatricolazioneItalia | 1 |
| dataSource (dvsa/dvla/dva ni) | 1 |
| Date automobile obtained | 1 |
| Date de publication (days-on-market) | 1 |
| date_derniere_procedure_VE | 1 |
| date_fin_derniere_procedure_VE | 1 |
| date_mise_a_jour_rapport | 1 |
| Date of Loss Adjustment (depreciation since loss date) | 1 |
| date_of_manufacture | 1 |
| Date of purchase (point-of-quote pre-fill) | 1 |
| date of sale | 1 |
| date_of_title_issuance | 1 |
| date_v5c_issued | 1 |
| dateCreated | 1 |
| dateOfLastKeeperChange [NV bulk] | 1 |
| dateRegistered | 1 |
| DatiOmologazione | 1 |
| DatiTecniciOmologati | 1 |
| DatiumInstantVal (valor de la valoracion, importe) | 1 |
| DatiumInstantValCurrency (AUD) | 1 |
| Datos / tiempos de pintura (fuente AZT) | 1 |
| datos de contacto (proporcionados por fabricante) | 1 |
| datos de contacto actualizados (DGT) | 1 |
| Datos de inventario (número y tipo de anuncios) | 1 |
| datos de negocio VO (usado) diarios | 1 |
| datos de Red (concesionarios/puntos de venta) | 1 |
| Datos de subasta de restos AUTOonline | 1 |
| Datos estadísticos personalizados (a medida) | 1 |
| Datos integrados de DMS/ERP/CRM (postventa) | 1 |
| Datos oficiales DGT del vehículo / historial (INTEVES) | 1 |
| Datos técnicos (JATO) | 1 |
| datos técnicos / ficha técnica del vehículo | 1 |
| Datos técnicos del vehículo | 1 |
| Datos telemáticos | 1 |
| datum_aankondiging_producent | 1 |
| datum_eerste_tenaamstelling_in_nederland | 1 |
| datum_eerste_toelating | 1 |
| datum_eigenaren_geinformeerd | 1 |
| datum_informeren_eigenaar | 1 |
| datum_inschrijving_voertuig_in_nederland (OVI) | 1 |
| datum_laatste_tenaamstelling (OVI) | 1 |
| datum_melding_bij_rdw | 1 |
| datum_tenaamstelling | 1 |
| Day & Night Rear View Mirror | 1 |
| day of week (dzien-tygodnia) [Statystyki] | 1 |
| Days in stock / days to sale | 1 |
| days listed / time on the forecourt | 1 |
| Days reduced for assignment | 1 |
| Days-to-acquisition | 1 |
| Daytime Running Light (DRL) | 1 |
| daytimeRunningLamps | 1 |
| dc_fast_charge_connector | 1 |
| deal_badge (Great Deal / Good Deal / Fair Deal / Fair Price / Well-Equipped) | 1 |
| deal_badge accuracy MdAPE (~4%) | 1 |
| deal_badge ML feature: seasonality | 1 |
| deal score | 1 |
| Deals: advertSaved flag | 1 |
| Deals: buyer preferences | 1 |
| Deals: dealIntentScore | 1 |
| Deals: intent | 1 |
| Deals: localCustomer flag | 1 |
| Deals: reservation status & fee | 1 |
| dealScore (numeric deal score) | 1 |
| DealShield Buyer's Adjustment fee | 1 |
| DealShield eligibility (<=20yr, <$100k, <250k mi; excl. TMU/TRA/salvage/branded) | 1 |
| DealShield for-any-reason return | 1 |
| DealShield: garantía devolución 21 días / 500 millas (reembolso total incl. fees) | 1 |
| DealShield refund (100% guaranteed amount + buy-fee) | 1 |
| DealShield return window (21 days) | 1 |
| DealShield Select (actualizaciones de inventario cualificado) | 1 |
| decision makers (per company) | 1 |
| declaration_valant_saisie_DVS_date | 1 |
| declaration_valant_saisie_nom_autorite | 1 |
| Decode Accuracy ('Decodes Correctly') | 1 |
| Decode de matrícula (plate) | 1 |
| decoder_car_specifications | 1 |
| Decoder: factory equipment | 1 |
| decoder_included_features | 1 |
| decoder_manufacturer | 1 |
| decoder_plant_of_production | 1 |
| Deductible | 1 |
| defection / losses | 1 |
| defection alert (CRM / API notification) | 1 |
| defections (to competitor) | 1 |
| Defectos de pintura (mm) | 1 |
| defectos destacados en pagina 1 (瑕疵明示) | 1 |
| defects / condition (ML signal) | 1 |
| defleet timing | 1 |
| Delinquency indicator | 1 |
| delivery_auction_fees | 1 |
| delivery_charges | 1 |
| delivery_customs_documents | 1 |
| delivery_destination_port | 1 |
| Delivery fees financiados | 1 |
| delivery_logistics_charges | 1 |
| delivery_lot_price | 1 |
| delivery_port_charges | 1 |
| deliveryCharges | 1 |
| deliveryDate | 1 |
| deliveryPeriod | 1 |
| Delta accessori di serie per allestimento | 1 |
| delve.benchmarking | 1 |
| delve.pricing_sales_trend | 1 |
| delve.time_to_sell | 1 |
| demographics | 1 |
| demontagedatum | 1 |
| Denominación comercial / Tipo (homologación) | 1 |
| Denominazione ufficiale del veicolo | 1 |
| Denuncia de fraude del anuncio (fraudReport) | 1 |
| Deposit | 1 |
| deposit amount | 1 |
| deposito de puja en subasta (auction deposit) | 1 |
| Deprezzamento | 1 |
| Derecho de tanteo / right of first refusal (Guaranteed) | 1 |
| Derivado / especificacion | 1 |
| DERIVADO: agrupacion 'Monitor and repair if necessary' (minor+advisory) | 1 |
| DERIVADO: agrupacion 'Repair immediately' (dangerous+major) | 1 |
| derivativeId | 1 |
| [EQUIP·Seguridad] Desactivación de airbag del pasajero delantero | 1 |
| Descripción de operación | 1 |
| Descripción de operación de pintura (P. sustitución/reparación) | 1 |
| Descripcion de ruedas y neumaticos | 1 |
| description | 1 |
| Descrizione connettore (EV) | 1 |
| DescrizioneAllestimento | 1 |
| DescrizioneCasa | 1 |
| DescrizioneComplessa | 1 |
| DescrizioneCompleta | 1 |
| DescrizioneEstesa | 1 |
| DescrizioneModalitaRicarica | 1 |
| DescrizioneMotivazione | 1 |
| DescrizionePiano | 1 |
| DescrizioneRT | 1 |
| DescrizioneTipoBatterie | 1 |
| DescrizioneTipoPresa | 1 |
| descuento aplicado (已减X万) | 1 |
| Descuento M.O. (%) | 1 |
| Descuento medio aplicado | 1 |
| Descuento oficial | 1 |
| Descuento sobre total M.O. (cód 33) | 1 |
| Descuento sobre total M.O. pintura (cód 59) | 1 |
| Descuento sobre total sin IVA (cód 88) | 1 |
| designChange | 1 |
| designChangeReason | 1 |
| despacho de aduanas | 1 |
| destination | 1 |
| destination_charge / destination fee | 1 |
| destination_fee | 1 |
| Destination Market | 1 |
| destinationCharge | 1 |
| Destrucción de vehículo | 1 |
| Desviacion objetivo vs oportunidad real | 1 |
| detailed_history_comments | 1 |
| detailed_history_date | 1 |
| detailed_history_event_comment_description | 1 |
| Detailed History event: data source | 1 |
| detailed_history_event_type | 1 |
| Detailed History event: type/description | 1 |
| detailed_history_source | 1 |
| detailed_history_source_of_record | 1 |
| Detailed narrative condition descriptions | 1 |
| detailUrl (AutoUncle page) | 1 |
| detalle técnico del vehículo | 1 |
| detección automática de opcionales | 1 |
| [EQUIP·Varios] Detección de alcohol (ADS) | 1 |
| detección de daños por IA fotográfica (piezas dañadas) | 1 |
| detección de fraude | 1 |
| Detected OBD2 codes (escaneo BlueDriver / Bluetooth) | 1 |
| [EQUIP·Seguridad] Detector de vehículos en ángulo muerto | 1 |
| deterministic ad-exposure-to-sale match (first-party) | 1 |
| Devaluation code (Entwertungscode) | 1 |
| devolucion sin motivo 7 dias (<=450km) | 1 |
| Diámetro de giro entre bordillos (m) | 1 |
| Diagnosis system | 1 |
| diagnosisCar (es coche diagnosticado) | 1 |
| Diagnostics (codigos de averia, sin detalle publico) | 1 |
| Diagramas de taller / visualizacion grafica de piezas | 1 |
| Diamètre braquage murs | 1 |
| Diamètre des jantes arrière | 1 |
| Diamètre des jantes avant | 1 |
| Dias que lleva anunciado cada vehiculo | 1 |
| dictionary total record count (ilosc-rekordow-slownika) [Slowniki] | 1 |
| dictionary value key (klucz-slownika) [Slowniki] | 1 |
| diferencia en puntos porcentuales (dif. p.p.) | 1 |
| DifferenzaKm | 1 |
| DifferenzaPrezzo | 1 |
| Digital Buyer Protection: missing exterior equipment | 1 |
| Digital Buyer Protection: unacceptable paintwork | 1 |
| Digital Cluster | 1 |
| Digital Cluster Size | 1 |
| Digital Deal: appointment scheduling | 1 |
| Digital Deal: custom APR (no credit check) | 1 |
| Digital Deal F&I: GAP | 1 |
| Digital Deal F&I: Tire & Wheel | 1 |
| Digital Deal F&I: VSC (Vehicle Service Contract) | 1 |
| Digital Deal: hard-pull credit application (AutoFi; BoA/Chase/US Bank/Huntington/Exeter/Regional Acceptance/Santander/Truist/TD/Westlake/Wells Fargo/ACA +33 captive) | 1 |
| Digital Deal lead type: Appt – Digital Deal | 1 |
| Digital Deal lead type: Deposit – Digital Deal | 1 |
| Digital Deal lead type: Digital Deal (base, trade-in/F&I) | 1 |
| Digital Deal lead type: Hard Pull – Digital Deal | 1 |
| Digital Deal lead type: Soft Pull – Digital Deal | 1 |
| Digital Deal: lender routing by payment-to-income ratio + credit score threshold | 1 |
| Digital Deal: pre-qualification soft pull (GLS, Westlake, Capital One) | 1 |
| Digital Deal: reservation deposit ($500 via Stripe) | 1 |
| Digital Deal sale price: delivery fee | 1 |
| Digital Deal sale price: down payment | 1 |
| Digital Deal sale price: taxes (third-party tool by location + zip) | 1 |
| Digital paint depth readings (espesor de pintura) | 1 |
| Digital Showroom website | 1 |
| Digital vehicle imagery (360 exterior + interior) | 1 |
| dim. calidad del vehiculo (车辆质量) | 1 |
| dim. coste de uso (使用成本) | 1 |
| dim. experiencia de conduccion (驾乘感受) | 1 |
| dimensión: canal | 1 |
| dimensión: periodo | 1 |
| dimensión: versión | 1 |
| Diminished value (insurance) | 1 |
| Dirección a las cuatro ruedas | 1 |
| Dirección: Asistencia variable con la velocidad | 1 |
| [EQUIP·Seguridad] Dirección asistida | 1 |
| Dirección: Desmultiplicación no lineal | 1 |
| Dirección: Desmultiplicación variable con la velocidad | 1 |
| Dirección fiscal del vehículo | 1 |
| Dirección: Tipo | 1 |
| Dirección: Tipo de asistencia | 1 |
| direccion (地址) | 1 |
| Direct Offer (push notifications, +14% inquiries) | 1 |
| directInspected (진단 directo) | 1 |
| disc_front | 1 |
| Discount | 1 |
| discount composition by category | 1 |
| discount rate (transaction) | 1 |
| Discounts (I/D, % o importe fijo) | 1 |
| dispersion (dispersión de mercado) | 1 |
| Disposal value forecast | 1 |
| Disposal-to-auction | 1 |
| Disposition / event (Crush / Parts / Retained / Salvage / Scrap / Sold / To Be Determined) | 1 |
| Disposition value: Crush | 1 |
| Disposition value: Parts | 1 |
| Disposition value: Retained | 1 |
| Disposition value: Scrap | 1 |
| Disposition value: Sold | 1 |
| Disposition value: To Be Determined (TBD) | 1 |
| Dispositivo / chip RFID (almacena el NCI; leíble por arco) | 1 |
| DispositivoAntiInquinamento | 1 |
| DisposizioneCilindri | 1 |
| disqualification.reimposedDate | 1 |
| disqualification.removalDate | 1 |
| disqualification.startDate | 1 |
| disqualification.suspensionStatus | 1 |
| Disruptor Roundup (monthly disruptive themes) | 1 |
| dist | 1 |
| distancia a la media UE (puntos) | 1 |
| Distribución de asientos | 1 |
| Distribución de reparaciones por comunidad autónoma | 1 |
| [EQUIP·Seguridad] Distribución electrónica de frenado (EBD) | 1 |
| division | 1 |
| DMA dynamics (current + historical, down to dealer level) | 1 |
| DMS / lead-management integration (DealerWeb, enquiryMAX, Pinewood) | 1 |
| DMS: Conversation history | 1 |
| DMS: Customer follow-ups (call/WhatsApp) | 1 |
| DMS: Incoming leads | 1 |
| dms_sales_verification_required | 1 |
| DMS: Walk-in database | 1 |
| dmsReference | 1 |
| Documentation/Title fee | 1 |
| DocumentoFirmato | 1 |
| Documentos de servicio / historial (fotos) | 1 |
| Documents / certificates (upload) | 1 |
| Dollar Volume | 1 |
| dom | 1 |
| dom_180 | 1 |
| dom_active | 1 |
| domestic (doméstico vs importado) | 1 |
| domestic_use_account | 1 |
| Door mirror glass + adjustment | 1 |
| Door Skin Allowance (UK) | 1 |
| Door-to-door transport quote | 1 |
| dos_active | 1 |
| down payment | 1 |
| down_payment_input | 1 |
| down_payment_percentage | 1 |
| Downside risk | 1 |
| Drivability assessment | 1 |
| drive_layout | 1 |
| Drive Line Type | 1 |
| drive_unit | 1 |
| drive-time analysis | 1 |
| driveby_soundlevel_db | 1 |
| drivenWheels | 1 |
| Driver Airbag | 1 |
| Driver Assist | 1 |
| Driver Attention Warning (ADAS) | 1 |
| Driver Side (LHD/RHD) | 1 |
| driver.dateOfBirth | 1 |
| driver.firstNames | 1 |
| driver.gender | 1 |
| driver.surname | 1 |
| driveType (FWD/RWD/AWD/4WD/6x4/6x6/8x6/8x8) | 1 |
| driving_axle | 1 |
| driving_habits_usage_intensity_periods | 1 |
| Driving-school deduction (לימוד נהיגה) | 1 |
| drivingLicenceNumber | 1 |
| drivingMode (chain/belt, motorbikes) | 1 |
| drivingWheels | 1 |
| Dual pricing (doble precio) | 1 |
| Duplicate Title | 1 |
| Durée de la garantie (mois) | 1 |
| Durchschnittliche Standzeit Markt (avg market standing time, días) | 1 |
| duree_detention_proprietaire_actuel_annees | 1 |
| dvla_body_desc | 1 |
| DVLA data integration | 1 |
| dvla_fuel_desc | 1 |
| DVLA lookup: doors | 1 |
| DVLA lookup: mass data | 1 |
| DVLA lookup: seating | 1 |
| dvla_manufacturer_desc | 1 |
| DVLA vehicle check | 1 |
| dvla_wheelplan | 1 |
| dvlaId (PARCIAL, recien matriculados) | 1 |
| DVSA data integration | 1 |
| Dynamic Brake Support (DBS) | 1 |
| Dynamically updated pricing display | 1 |
| E-Auto Durchschnittspreis (avg EV price) | 1 |
| E-Auto Marktanteil VO (EV used-car market share) | 1 |
| E-Auto Preisaufschlag (EV price premium vs media) | 1 |
| e-bike bikeGearType | 1 |
| e-bike frameHeight | 1 |
| e-bike frameMaterial | 1 |
| e-bike frameShape | 1 |
| e-bike motorPosition | 1 |
| e-bike numberOfGears | 1 |
| e-bike wheelSize | 1 |
| e-mobility penetration rate | 1 |
| Early Release Values (modelos sin historial usado) | 1 |
| Editions available (by original cost) | 1 |
| Editorial comment on value movement (commentDate, comment) | 1 |
| Editorial Top 10 Lists | 1 |
| editorial vehicle overview/review text | 1 |
| editorial.AutoBriefReview | 1 |
| editorial.AwardsAndAccolades | 1 |
| editorial.NewCarTestDriveReview | 1 |
| EdizioneQuotazione | 1 |
| Edmunds Rating (0-10 composite) | 1 |
| Edmunds Suggested Price (new, ex-TMV New) | 1 |
| Edmunds value | 1 |
| eerste_kleur | 1 |
| einddatum_gebrek | 1 |
| Elect_Weighted | 1 |
| Electric continuous torque 30min (Nm) | 1 |
| Electric continuous torque 60min (Nm) | 1 |
| Electric peak torque (Nm) | 1 |
| Electric vehicle plug type | 1 |
| Electric window operation (per window NSF/NSR/OSF/OSR) | 1 |
| Electrical score | 1 |
| ElectricCons_City | 1 |
| ElectricCons_Comb | 1 |
| electricHeatedSeats | 1 |
| ElectricRange_City | 1 |
| ElectricRange_Comb | 1 |
| electricWindows | 1 |
| Electronic brake assistance | 1 |
| Electronic Brakeforce Distribution (EBD) | 1 |
| Electronic invoicing (total loss/reparado/especialista/inherited/retail) | 1 |
| Electronic parking aid | 1 |
| Electronic part-exchange appraisal (Appraisal App) | 1 |
| Electronic Vehicle Record (EVR) | 1 |
| elektriciteitsverbruik_gewogen_gecombineerd | 1 |
| elektriciteitsverbruik_volledig_elektrisch | 1 |
| elektrisch_verbruik_enkel_elektrisch_wltp | 1 |
| elektrisch_verbruik_extern_opladen_wltp | 1 |
| [EQUIP·Confort] Elevalunas eléctricos delanteros | 1 |
| [EQUIP·Confort] Elevalunas eléctricos traseros | 1 |
| eligibility flags (branded title/damage/mileage/age/exotic/non-drivable/no local interest) | 1 |
| Eliminar constante de pintura CESVIMAP (cód 84) | 1 |
| Email (header de auth) | 1 |
| Email del taller | 1 |
| [EQUIP·Varios] Embellecedores metálicos en umbrales de puertas | 1 |
| EMI Amount (editable) | 1 |
| emissie_deeltjes_type1_wltp | 1 |
| emissieklasse (emissiecode_omschrijving) | 1 |
| Empattement | 1 |
| empleo directo del sector (nº puestos) | 1 |
| employee_ratings | 1 |
| encarPassType / encarPassCategoryType | 1 |
| End of Production (EOP) date | 1 |
| End of Term value | 1 |
| end-of-sales / phase-out date | 1 |
| End-of-term value | 1 |
| End-of-term value / settlement figure | 1 |
| endorsement.offenceCode | 1 |
| endorsement.offenceDate | 1 |
| endorsement.offenceLegalDescription | 1 |
| endorsement.penaltyPoints | 1 |
| endorsement.penaltyPointsExpiryDate | 1 |
| energie_type_carburant (P.3) | 1 |
| energy & technology trends (25-year) | 1 |
| Energy cost (EV) | 1 |
| energy.code | 1 |
| energy.master-code | 1 |
| energy.master-name | 1 |
| energy.name | 1 |
| energylabel (etiqueta energética) | 1 |
| Enhanced Vehicles (icono) | 1 |
| Enlace al anuncio original en portal | 1 |
| enquiry.enquirer (first_name/last_name/email/mobile) | 1 |
| enquiry.vehicle (make/model/badge/series/year) | 1 |
| Enterprise Dashboard - day-wise query graph (14 dias) | 1 |
| Enterprise Dashboard - queries last 15 days | 1 |
| Enterprise Dashboard - queries last 30 days | 1 |
| Enterprise Dashboard - reports downloaded (basic/premium) | 1 |
| Enterprise Dashboard - subscription status | 1 |
| Enterprise Dashboard - total queries lifetime | 1 |
| Enterprise multi-rooftop appraisal status | 1 |
| Entertainment (spec) | 1 |
| Entertainment System | 1 |
| Entidad de registro nautico | 1 |
| Entidad federativa que registró el vehículo | 1 |
| entitlement.categoryCode (A/B/C...) | 1 |
| entitlement.categoryLegalDescription | 1 |
| entitlement.categoryType | 1 |
| entitlement.expiryDate | 1 |
| entitlement.fromDate | 1 |
| entitlement.restrictionCode | 1 |
| entitlement.restrictionDescription | 1 |
| entrada/down payment (首付) | 1 |
| envío en formato impreso (logística postal) | 1 |
| environmental_compliance_level | 1 |
| Environmental fee | 1 |
| epa_city | 1 |
| epa_combined | 1 |
| EPA Green Score - Air Pollution score | 1 |
| EPA Green Score - Greenhouse Gas score | 1 |
| epa_highway | 1 |
| EPA SmartWay Elite status | 1 |
| EPA SmartWay status | 1 |
| equip_abs_esp_brake_systems | 1 |
| equip_airbags | 1 |
| equip_audio_radio_speakers | 1 |
| equip_brakes_front | 1 |
| equip_brakes_rear | 1 |
| equip_climate_ac | 1 |
| equip_cruise_control | 1 |
| equip_headlamps_lighting | 1 |
| equip_navigation_device | 1 |
| equip_park_distance_control | 1 |
| equip_steering_wheel | 1 |
| equip_tires | 1 |
| equip_trailer_hitch | 1 |
| equip_wheels | 1 |
| EquipaggiamentoEsclusione | 1 |
| EquipaggiamentoInclusione | 1 |
| EquipaggiamentoNormalizzato | 1 |
| EquipaggiamentoQualificante | 1 |
| EquipaggiamentoVincolo | 1 |
| Equipamento: Conforto e Outros Equipamentos | 1 |
| Equipamento: Electrónica e Assistência à Condução | 1 |
| Equipamento: Segurança | 1 |
| Equipamento: Áudio e Multimédia (Bluetooth, Rádio, Porta USB, Sistema de navegação, Ecrã táctil) | 1 |
| equipamiento | 1 |
| Equipamiento / opciones (auto-importado vía DAT por VIN) | 1 |
| Equipamiento: Confort y conveniencia (comfortAndConvenience) | 1 |
| Equipamiento de fábrica instalado | 1 |
| Equipamiento de seguridad | 1 |
| Equipamiento: Entretenimiento / Medios | 1 |
| Equipamiento: Extras | 1 |
| Equipamiento instalado de fabrica | 1 |
| Equipamiento: Seguridad | 1 |
| Equipamiento/features (por importancia) | 1 |
| Equipment adjustment (per-feature, e.g. Heated Seats) | 1 |
| Equipment: airbag count | 1 |
| Equipment: audio system | 1 |
| Equipment catalogue | 1 |
| Equipment: climate control / heating | 1 |
| Equipment code | 1 |
| Equipment: electric windows / elevalunas | 1 |
| equipment_groups | 1 |
| Equipment Information Source (VIN Decoder/VIN Query/Interface) | 1 |
| Equipment list — Entertainment | 1 |
| Equipment list — Exterior | 1 |
| Equipment list — Interior | 1 |
| Equipment list — Mechanical | 1 |
| Equipment list — Safety | 1 |
| Equipment: mirrors / espejos | 1 |
| Equipment: navigation system / navegador | 1 |
| Equipment Plant Code (DOT) | 1 |
| Equipment text / short | 1 |
| Equipment Type | 1 |
| Equipment: window tint / lunas | 1 |
| equipment.availability (STANDARD/OPTIONAL/UNKNOWN) | 1 |
| equipment.name | 1 |
| equipment.price-excluding-vat | 1 |
| equipment.price-including-vat | 1 |
| Equipment/accessories detected list | 1 |
| equipmentType (AUDIO_SYSTEM/COLOR/ENGINE/FEE/HOLDBACK/OPTION/TELEMATICS/TIRES/TRANSMISSION/WARRANTY/WHEELS) | 1 |
| equitable sales target | 1 |
| equity position | 1 |
| equity.equity_position | 1 |
| equity.positive_equity | 1 |
| EquivalentAllElectric | 1 |
| erkenning (tipo: APK/gas/tachograaf/export/demontage/bedrijfsvoorraad/handelaarskenteken/Kentekenloket...) | 1 |
| error | 1 |
| Error Code | 1 |
| [MED·Prueba] Error del cuentakilómetros (%) | 1 |
| Error Text | 1 |
| error.code | 1 |
| error.detail | 1 |
| error.status | 1 |
| error.title | 1 |
| Ersatzwagenklasse (clase de vehiculo de sustitucion) | 1 |
| escrow / garantia del pago (车款居间担保) | 1 |
| EsitoGravami | 1 |
| esp | 1 |
| Especificaciones del vehículo (taxonomía JATO) | 1 |
| Especificaciones EV granulares | 1 |
| espejos eléctricos (electricMirrors) | 1 |
| establishment address | 1 |
| establishment city | 1 |
| establishment email | 1 |
| establishment phoneNumber | 1 |
| establishment zipCode | 1 |
| establishmentId | 1 |
| establishmentName / name | 1 |
| Estadísticas avanzadas: favoritos por anuncio | 1 |
| Estadísticas avanzadas: informe mensual de performance del anuncio | 1 |
| Estadísticas avanzadas: llamadas por anuncio | 1 |
| Estadísticas avanzadas: mensajes por anuncio | 1 |
| Estadísticas avanzadas: visitas por anuncio | 1 |
| estado (recorte regional) | 1 |
| Estado / UF (27 unidades federativas) | 1 |
| Estado actual y futuro del vehículo | 1 |
| Estado de aseguramiento (seguro obligatorio SOA) | 1 |
| Estado de auditoria | 1 |
| Estado de batería (State of Health) | 1 |
| Estado de conservação | 1 |
| estado de la comunicación | 1 |
| Estado de neumaticos | 1 |
| Estado de titulo (title) | 1 |
| Estado del movimiento | 1 |
| Estado en watchlist (lista de seguimiento) | 1 |
| Estado global semáforo (sin incidencias / con avisos / con incidencias) | 1 |
| Estado: nuevo/ocasion/Km0/seminuevo/clasico/demo (condition) | 1 |
| estado nuevo/usado (valueModel.estado) | 1 |
| estado real del vehículo (dato conectado) | 1 |
| estado recien listado (新上架/Newly listed) | 1 |
| Estado/condición del vehículo (opcional) | 1 |
| Estado/condición técnica actual | 1 |
| Estado/Situación (Avance/En avance) | 1 |
| Estatus de inscripción (correcto proceso de inscripción) | 1 |
| Esterni | 1 |
| Estimación de reparación línea a línea | 1 |
| [HERRAMIENTA] Estimación de valor del coche (¿cuánto vale tu coche?) | 1 |
| Estimacion de piezas de desgaste | 1 |
| Estimacion de punto unico (value, pricing_type=gp) | 1 |
| estimacion oficial/precio justo (官方估价) | 1 |
| Estimate line item (line-level) | 1 |
| Estimate Number / Estimate Id | 1 |
| Estimated / potential retail margin (£) | 1 |
| estimated_annual_fuel_cost | 1 |
| estimated APR | 1 |
| Estimated fuel cost (12,000 miles/yr) | 1 |
| estimated fuel costs | 1 |
| estimated_monthly_payment_lease | 1 |
| estimated_monthly_payment_loan_calc | 1 |
| estimated pricing (VIN decode) | 1 |
| estimated_retail | 1 |
| Estimated Retail - Above | 1 |
| Estimated Retail - Average | 1 |
| Estimated Retail - Below | 1 |
| estimated sale price (instant RPM output) | 1 |
| estimated_trade | 1 |
| Estimated trade profit generated (£) | 1 |
| estimated_value_per_mode | 1 |
| estimateTmv | 1 |
| eStock Card (ficha de stock electronica) | 1 |
| Estrés de batería | 1 |
| estructura de antiguedad de flota (车龄结构) | 1 |
| estudio de mercado a medida | 1 |
| estudio sectorial | 1 |
| ETAG code | 1 |
| Etapa de ciclo de vida (factory order -> disposal) | 1 |
| Etiqueta ambiental / distintivo DGT (emissionSticker) | 1 |
| Etiqueta de precio: Superprecio / Buen precio / ... / Caro (priceEvaluation) | 1 |
| Etiqueta/distintivo ambiental DGT | 1 |
| Etiquetas de medioambiente UE/Umwelt (environmentEuDirective/Labels) | 1 |
| Euro NCAP (rating de seguridad) | 1 |
| europese_uitvoeringcategorie_toevoeging | 1 |
| europese_voertuigcategorie | 1 |
| europese_voertuigcategorie_toevoeging | 1 |
| Eurotax Blu (Compera / prezzo di acquisto dealer-trade-in) | 1 |
| Eurotax Giallo (Vendita / prezzo di vendita al privato) | 1 |
| EV Drive Unit | 1 |
| EV forecast | 1 |
| EV Index (base ene-2015=100) + YoY % | 1 |
| EV market forecast | 1 |
| EV market penetration (%) | 1 |
| EV market sizing | 1 |
| EV pricing | 1 |
| EV sales (by OEM & model) | 1 |
| EV share (%) | 1 |
| EV share / trends | 1 |
| EV share growth trajectory | 1 |
| EV specifications | 1 |
| EV type (Mild Hybrid / BEV / FCEV; 8 electrification types) | 1 |
| EV vs ICE / fuel-type trend | 1 |
| ev.federalRebate | 1 |
| ev.stateRebate | 1 |
| ev.utilityRebate | 1 |
| eVA condition adjustment | 1 |
| eVA consumer valuation widget / lead-gen (white-label) | 1 |
| eVA future/forward value (hasta 6 meses por adelantado) | 1 |
| eVA Insight: forecourt-vs-wholesale decision | 1 |
| eVA LCV: racking and accessories | 1 |
| eVA LCV: signwriting presence | 1 |
| eVA LCV: usage and wear characteristics (tolerancia van) | 1 |
| eVA part-exchange value | 1 |
| eVA real-time valuation | 1 |
| eVA rule-builder pricing adjustments | 1 |
| eVA Self-Inspect: number of keys (input) | 1 |
| eVA Self-Inspect: vehicle images (input) | 1 |
| eVA UK: cobertura Cars + LCV | 1 |
| eVA UK: modos de captura (online/in-store/roadside/self-inspect) | 1 |
| eVA UK: Part-exchange value | 1 |
| eVA Underwrite: guaranteed purchase price (Cox compra, pago 24h) | 1 |
| Evaluación de condición/calidad del vehículo | 1 |
| Evaluacion de red paralela/competencia | 1 |
| Evaluacion de riesgo (Basilea II) | 1 |
| Evaluation date | 1 |
| EVBH score 0-100 (salud de batería VIN-específica) | 1 |
| Event Data Recorder (EDR) | 1 |
| event_date | 1 |
| event_details | 1 |
| Event end time | 1 |
| Event start time | 1 |
| eventDate (KADOE keeper-at-date-of-event) | 1 |
| evento: baja | 1 |
| evento: transferencia | 1 |
| EVM-identified add/deducts (AVT) | 1 |
| evolución temporal del mercado | 1 |
| evox match flags (year/make/model/trim/body_type/cab_type/doors/drive_type) | 1 |
| evox match VIF | 1 |
| Evox VIF | 1 |
| evpulse.retained_value_pct_movement | 1 |
| exakte Ausstattung ab Werk (equipamiento exacto de fabrica) | 1 |
| Excess (franquicia) | 1 |
| Excess Wear and Tear (EWT) estimate (off-lease) | 1 |
| Exchange value (valor de intercambio) | 1 |
| executionTimeMS | 1 |
| Exhaust leaks / secure | 1 |
| Exit strategy (retail / wholesale / subprime) | 1 |
| Expansion de infraestructura de carga | 1 |
| Expected costs (input) | 1 |
| Expected price indicator rating | 1 |
| Expected transaction timeframe (ready now / 2-6 meses / curious) | 1 |
| expectedDate | 1 |
| expectedPrice (=IMV reference) | 1 |
| expediente CAE | 1 |
| Experian AutoCheck (vehicle history summary) | 1 |
| Expert Overall Rating (0.0-5.0) | 1 |
| Expert rating: comfort | 1 |
| Expert rating: performance | 1 |
| Expert rating: quality | 1 |
| Expert rating: reliability | 1 |
| Expert rating: styling | 1 |
| Expert rating: value | 1 |
| Expert Review (editorial) | 1 |
| Expert Review Overall Rating | 1 |
| Expert Reviews (pros/cons) | 1 |
| expert_star_rating | 1 |
| Expert Sub-rating: Drive Experience | 1 |
| Expert Sub-rating: Exterior | 1 |
| Expert Sub-rating: Features | 1 |
| Expert Sub-rating: Interior | 1 |
| Expert Sub-rating: Safety | 1 |
| Expert Verdict | 1 |
| expiryDate (mot test) | 1 |
| Explication du prix (vs moyenne des véhicules similaires) | 1 |
| exploradoras/antiniebla SI/NO (explorersShow) | 1 |
| ext_bidding_history | 1 |
| ext_etk_parts_catalog_numbers | 1 |
| ext_number_of_bids_iaai | 1 |
| ext_sales_history_models | 1 |
| ext_similar_lots_comparables | 1 |
| ext_technical_equipment | 1 |
| extended_data.vehicle_type_description | 1 |
| Extended Guarantee: hasta 14 dias | 1 |
| extendWarranty / deemedExtendWarranty (garantía extendida) | 1 |
| Exterior (spec) | 1 |
| exterior_condition | 1 |
| Exterior cosmetic defects (dents/scratches/chips/paint per panel) | 1 |
| exterior_features | 1 |
| exterior is_two_tone | 1 |
| exterior_paint_description | 1 |
| exterior photos x4 (45-degree corners, plate visible, doors closed) | 1 |
| exterior primary_rgb_code (r,g,b) | 1 |
| Exterior score (x/10) | 1 |
| exterior secondary_rgb_code (r,g,b) | 1 |
| external / manufacturer price contribution | 1 |
| external_dms_id | 1 |
| externalUrl (original seller listing) | 1 |
| Extras/opcionales (JATO) | 1 |
| Facelift / launch value-change effect | 1 |
| facelift event | 1 |
| Facelift information (national) | 1 |
| Facelift/launch uplift effect | 1 |
| facility guideline adherence | 1 |
| facility type recommendation | 1 |
| Factory car warranty | 1 |
| Factory rebates (aplicados automaticamente) | 1 |
| Factory upgrades itemizados con valor en dolares | 1 |
| facturación del sector (€) | 1 |
| Fahrassistenzsysteme (sistemas ADAS) | 1 |
| Fahrzeugart (new/used/Jahreswagen/Vorführwagen) | 1 |
| Fahrzeugbewertung estimated value (consumer) | 1 |
| Fahrzeugzustand (condition, asumido bueno) | 1 |
| Fair cash-out value (total loss) | 1 |
| fair_market_value_max | 1 |
| fair_market_value_min | 1 |
| Fair Purchase Price (CPO) | 1 |
| Fair value / valor de colateral (IFRS13, cartera) | 1 |
| Family (model) | 1 |
| FamilyId | 1 |
| Farbcode (codigo de color/pintura) | 1 |
| [EQUIP·Seguridad] Faros antiniebla | 1 |
| [EQUIP·Seguridad] Faros LED | 1 |
| Fases de pintura (paint stages) | 1 |
| fast-moving vs slow-moving classification | 1 |
| 원동기 fault codes / 경고등 (motor: códigos de fallo, testigos) | 1 |
| favorite_shop | 1 |
| feature[] / excludeFeature[] (extended equipment set) | 1 |
| feature factoryCodes | 1 |
| feature genericName | 1 |
| feature name | 1 |
| feature rarityRating | 1 |
| Feature Tour | 1 |
| feature value | 1 |
| feature valueRating | 1 |
| Feature-adjusted valuation | 1 |
| feature-category.name | 1 |
| feature.availability (série/option) | 1 |
| feature.description | 1 |
| feature.featureKeyAnswers | 1 |
| feature.id | 1 |
| feature.installCause | 1 |
| feature.isEVFeature | 1 |
| feature.isHybridFeature | 1 |
| feature.isStandard | 1 |
| feature.key | 1 |
| feature.nameNoBrand | 1 |
| feature.price-excluding-vat | 1 |
| feature.price-including-vat | 1 |
| feature.rankingValue | 1 |
| feature.sectionId | 1 |
| feature.sectionName | 1 |
| feature.subSectionId | 1 |
| Featured flag | 1 |
| features | 1 |
| features_exterior | 1 |
| features_interior | 1 |
| Fecha de fabricacion (build date) | 1 |
| Fecha de impresión | 1 |
| Fecha de inscripción / registro | 1 |
| Fecha de peritación | 1 |
| Fecha de producción | 1 |
| Fecha de tarifa (price list date) | 1 |
| Fecha de trámite | 1 |
| Fecha del trámite (FEC_TRAMITE) | 1 |
| feed scope (dealer/zip/state/national) | 1 |
| Fermo amministrativo (presenza) | 1 |
| FermoAmministrativo | 1 |
| ffo.build_sheet_lines | 1 |
| ffo.match_category | 1 |
| ffo.match_score (0.6-1) | 1 |
| ficha técnica / especificaciones | 1 |
| fifth_wheel_capacity_lb | 1 |
| [EQUIP·Seguridad] Fijación ISOFIX en acompañante | 1 |
| [EQUIP·Seguridad] Fijaciones ISOFIX traseras exteriores | 1 |
| filtro Abaixo da FIPE | 1 |
| [EQUIP·Confort] Filtro de aire PM 2.5 | 1 |
| [EQUIP·Confort] Filtro de habitáculo | 1 |
| FiltroCarrozzeria | 1 |
| Filtros de búsqueda + alertas / search requests guardadas | 1 |
| Fin commercialisation | 1 |
| final de placa | 1 |
| final_drive_axle_ratio | 1 |
| final sale price (highest accepted offer) | 1 |
| Final sale price histórico (Sales Data) | 1 |
| Financiación: simulación Santander integrada | 1 |
| Financing cost (total + Y1-Y5; APR 3.09%, 60mo, 10% down) | 1 |
| Finanzierungsquote / Leasingquote (cuota de financiacion/leasing) | 1 |
| find_service_centers_verified_reviews | 1 |
| fine detail: where, when, and vehicle in which received (szczegoly mandatu) [Moj Pojazd] | 1 |
| FineImmatricolazione | 1 |
| fines / mandates: paid vs unpaid (mandaty: oplacone/nieoplacone) [Moj Pojazd] | 1 |
| FineVendita | 1 |
| Finition | 1 |
| Firmatario | 1 |
| First & reverse test drive | 1 |
| first_seen_at | 1 |
| first_seen_at_date | 1 |
| first_seen_at_mc | 1 |
| first_seen_at_mc_date | 1 |
| first_seen_at_source | 1 |
| first_seen_at_source_date | 1 |
| first_seen_date | 1 |
| first_seen_vdp_url | 1 |
| firstAdmissionDate / datum eerste toelating | 1 |
| firstUsedDate | 1 |
| Fiscalidad transfronteriza (cross-border taxation) | 1 |
| fitment | 1 |
| Fixed cost | 1 |
| flag coche incendiado (火烧车) | 1 |
| flag coche inundado (泡水车) | 1 |
| Flag de oportunidad de venta internacional (10-15% de vehículos) | 1 |
| Flag minivolture (ultimo passaggio) | 1 |
| Flag: service actions (acciones de servicio) | 1 |
| Flag specialized (sin pricing AccuTrade) | 1 |
| FlagCategoria | 1 |
| FlagPack | 1 |
| Flags de riesgo/coste | 1 |
| FlagUfficiale | 1 |
| FlagVeicoloNuovo | 1 |
| fleet composition | 1 |
| fleet netting (parent/subsidiary) | 1 |
| fleet score per statistical district | 1 |
| fleet size (per company) | 1 |
| fleet size class | 1 |
| fleet vehicle type (PC/LCV/HCV) | 1 |
| fleetNumber | 1 |
| fleetOnly | 1 |
| FlgSerieOpzionale | 1 |
| Flood Risk Check | 1 |
| Floor price (reserva) | 1 |
| Floorplan advance hasta 100% + floor planning fee + interes diario | 1 |
| Fluid costs | 1 |
| Foldable Rear Seat | 1 |
| Folio de Constancia de Inscripción (FCI, folio de lote/holograma) | 1 |
| Follow Me Home Headlamps | 1 |
| follow-up / noncompliance correction plan | 1 |
| follow-up bid above reserve | 1 |
| follow-up question interpretation | 1 |
| # For sale (live inventory count per market) | 1 |
| For You personalized recommendations (AI) | 1 |
| forcedInduction | 1 |
| Forecast / prognóstico de preço | 1 |
| Forecast: adjustedForecastPricing.adjustedBy (Color/Grade/Odometer/Region) | 1 |
| Forecast: adjustedForecastPricing.wholesale (valor forecast ajustado) | 1 |
| Forecast clean/average/below by month (plusValues) | 1 |
| Forecast Curve (1-36 months) | 1 |
| Forecast de subida/bajada de VR en el tiempo (grafico) | 1 |
| Forecast: edition (fecha de publicación) | 1 |
| Forecast evidence / rationale (editorial) | 1 |
| Forecast: forecastDate (lunes de la edición) | 1 |
| Forecast: forecastedAverageGrade | 1 |
| Forecast: forecastedPricing (valor forecast sin ajustar) | 1 |
| forecast horizon 5 years (to ~2030-2031) | 1 |
| Forecast horizon up to 60 months / 5 years | 1 |
| Forecast: horizonte hasta 106 semanas | 1 |
| Forecast input: current & historical retailer pricing | 1 |
| Forecast input: seasonal pricing trends | 1 |
| Forecast value | 1 |
| Forecast value at contract start | 1 |
| Forecast value-retention % (Residual Value Awards) | 1 |
| forecast values per quarter / month | 1 |
| forecast vs reality gap | 1 |
| Forecast with RedBook pricing | 1 |
| Forecast with user-defined price | 1 |
| forecast.nextMonth.retail | 1 |
| forecast.nextMonth.wholesale | 1 |
| forecast.nextYear.retail | 1 |
| forecast.nextYear.wholesale | 1 |
| Forecasting / tendencias de mercado (Car Digital Track) | 1 |
| foreign risk flag: scrapping (zlomowanie) [autoDNA] | 1 |
| foreign risk flag: traffic ban / not admitted to traffic (zakaz ruchu / niedopuszczony do ruchu) [autoDNA] | 1 |
| foreign risk flag: used as taxi (uzytkowanie jako taxi) [autoDNA] | 1 |
| fork_rake_angle | 1 |
| Form completion rate (65%+) | 1 |
| Formato de venta B2B (precio fijo/puja abierta/blind/sellada/one-by-one/agrupada) | 1 |
| formulario técnico TRA050 | 1 |
| Formularios de lead (leadsRange/galleryLeadForm) | 1 |
| FormYear / 형식년도 (año-modelo) | 1 |
| Foto del veicolo (cattura e archiviazione) | 1 |
| Foto's (tasación ampliada) [A] | 1 |
| Fotos (documentacion fotografica) | 1 |
| Fotos del coche (set guiado) | 1 |
| Fotos del vehículo | 1 |
| Fotos del vehiculo (vehicle_photos, additional_images, primary image) | 1 |
| fréquence-finition-dans-le-parc | 1 |
| Frais de remise en état attendus (expected-refurbishment-costs) | 1 |
| Frame / structural assessment (TrueFrame, siniestro) | 1 |
| Franchise value (channel-segmented retail) | 1 |
| Franchise vs independent sales comparison | 1 |
| Franquicia (deducible) | 1 |
| Fraud detection flags | 1 |
| fraud_flag_rate_evasion | 1 |
| Fraud flags | 1 |
| Free AutoCheck Report (Experian): AutoCheck Score | 1 |
| free_carfax_report_link_per_listing | 1 |
| Free preview: data availability semaphore (que datos existen pre-pago) | 1 |
| free_reports_with_deposit | 1 |
| Freigabe (autorizacion/liberacion de reparacion) | 1 |
| [EQUIP·Confort] Freno de estacionamiento automático | 1 |
| Freno delantero (tipo) | 1 |
| Freno trasero (tipo) | 1 |
| Frenos - condición (brakes) | 1 |
| frenos ABS SI/NO (absShow) | 1 |
| frequencyId (1-9) | 1 |
| Frequently purchased complementary items (accesorios) | 1 |
| front_brake_diameter | 1 |
| front_head_room | 1 |
| front_hip_room | 1 |
| front_legroom | 1 |
| front_seat_type | 1 |
| front_shoulder_room | 1 |
| Front Suspension | 1 |
| front_suspension_size | 1 |
| front_suspension_type | 1 |
| Front tire age (excellent/good/poor) | 1 |
| front_tire_order_code | 1 |
| front_tire_pressure | 1 |
| front_tire_size | 1 |
| Front Tires condition | 1 |
| front_track | 1 |
| Front track size | 1 |
| front_travel | 1 |
| front_wheel_diameter | 1 |
| Front-end gross (store historical, by MMT) | 1 |
| Front/rear suspension, steering & underframe [128] | 1 |
| fuel & electricity cost (tax guide) | 1 |
| fuel_capacity_litres | 1 |
| fuel cards (per fleet) | 1 |
| fuel_control | 1 |
| fuel_cost_comparison | 1 |
| Fuel Delivery/Fuel Injection Type | 1 |
| fuel_induction | 1 |
| fuel_quality | 1 |
| Fuel Tank Size | 1 |
| fuel-cell.fuel | 1 |
| fuel-cell.fuel-cell-type | 1 |
| fuel-cell.volume | 1 |
| Fuel-Tank Material | 1 |
| Fuel-Tank Type | 1 |
| fuel-type / EV trends | 1 |
| fuel-type category (BEV/FCV/HEV/ICE/MEV/Plug-in) | 1 |
| fuel-type forecast (5 years) | 1 |
| Fuel-type RV benchmark (percentage-point difference) | 1 |
| Fuel-type split (EV / PHEV / HEV %) | 1 |
| Fuel1 | 1 |
| Fuel1_Comb | 1 |
| Fuel2 | 1 |
| Fuel2_Comb | 1 |
| fuelCapacity | 1 |
| fuelEconomy.city | 1 |
| fuelEconomy.hwy | 1 |
| fuelEconomy.unit | 1 |
| fuelEconomyNEDCCombinedMPG | 1 |
| fuelEconomyWLTPCombinedMPG | 1 |
| fuelType / brandstof | 1 |
| Full provenance check | 1 |
| fullServiceHistory | 1 |
| [EQUIP·Confort] Función Follow me home | 1 |
| Funding request (Partner Finance link) | 1 |
| FunzionamentoElettricoPuro | 1 |
| Fuoristrada | 1 |
| Future / contract-end value (up to 5 years) | 1 |
| Future / projected values | 1 |
| Future resale price (predictor) | 1 |
| future RV curve | 1 |
| future vehicle specifications (4000+ vehicles) | 1 |
| Future/forecast value (1-72 month projections) | 1 |
| Future/Trended forecast +30 days (~1% accuracy) | 1 |
| Future/Trended forecast +60 days | 1 |
| Future/Trended forecast +90 days (~3% to 3 months) | 1 |
| Future/Trended forecast up to 6 months (~5%) | 1 |
| Génération | 1 |
| gage_date | 1 |
| gage_nom_creancier | 1 |
| Galeria 25+ fotos (min 25-26) | 1 |
| galeria de fotos | 1 |
| Galves Market Ready Value (wholesale reacondicionado/auction-ready) | 1 |
| Galves value | 1 |
| Garantía | 1 |
| Garantia (warranty) | 1 |
| Garantie (mois) | 1 |
| Garantie constructeur (km) | 1 |
| Gas system LPG/GPM addition (מערכת גפ"מ) | 1 |
| Gas tank capacity + unit | 1 |
| gasinstallatie_tank_inhoud | 1 |
| [HERRAMIENTA] Gasto anual estimado del coche (calculadora) | 1 |
| Gasto en medios / baskets por medio (JorecaAdvertisers) | 1 |
| Gastos de transferencia | 1 |
| Gastos operativos | 1 |
| gauge.confidence | 1 |
| gauge.fill (0-1) | 1 |
| gauge.sample_size | 1 |
| gauge.vehicle_title | 1 |
| gcwr | 1 |
| GDV-Schnittstelle (insurer interface) | 1 |
| gear_ratios | 1 |
| Gear Shift Indicator | 1 |
| gears | 1 |
| Gebrauchtwagengarantie (used-car warranty flag) | 1 |
| gebrek_artikel_nummer | 1 |
| gebrek_identificatie | 1 |
| gebrek_omschrijving (defecto) | 1 |
| gebrek_paragraaf_nummer | 1 |
| Gegarandeerd bod (Autoverkoopservice; media de pujas reales comparables) | 1 |
| geluidsniveau_rijdend | 1 |
| geluidsniveau_stationair | 1 |
| gemiddelde_lading_waarde | 1 |
| generation | 1 |
| generation.body-type | 1 |
| generation.body-type-classified-ad | 1 |
| generation.full-nicename | 1 |
| generation.name | 1 |
| generation.position | 1 |
| generation.short-nicename | 1 |
| Generica_custom | 1 |
| Generica_hard | 1 |
| Generica_medium | 1 |
| Generica_soft | 1 |
| genre_national (J.1) | 1 |
| geremde_as_indicator | 1 |
| geremde_rupsband_indicator | 1 |
| Gesamtreparaturkosten (coste total de reparacion) | 1 |
| Gesamtschaden (valoracion total del dano) | 1 |
| geschaetzte Wertminderung (estimated depreciation) | 1 |
| gestión de contratos (alta / uso / devolución / remarketing) | 1 |
| gestión multietapa del proceso de rellamada | 1 |
| gevelnaam | 1 |
| giorni_in_vendita | 1 |
| GiorniRotazione | 1 |
| GiorniVendita | 1 |
| Glance (evaluacion rapida de potencial) | 1 |
| Glass condition | 1 |
| Glass Condition adjustment | 1 |
| glass_repairs (CA) | 1 |
| Glasses Code (NVIC valido) | 1 |
| Global NCAP Child Safety Rating | 1 |
| Global NCAP Safety Rating | 1 |
| Global Search (~1M vehiculos, 7 canales de sourcing) | 1 |
| Glove Box | 1 |
| Glow plug warning light | 1 |
| Go-to-market strategy [RV driver] | 1 |
| Golf-Index (VW Golf price index desde 2017, 5 países) | 1 |
| Good Price / Great Price badge | 1 |
| Google Performance Max reach (YouTube/Gmail/Google) | 1 |
| Google/Alexa Connectivity | 1 |
| government incentive programmes | 1 |
| GPS + timestamp | 1 |
| grado de condicion S/A/B/C/D (export auction grade) | 1 |
| Grado de semejanza (Estrella exacta/Verde/Amarillo/Rojo) | 1 |
| Grado NAMA car (1/2/3/4/5/U) | 1 |
| Grado NAMA LCV | 1 |
| Granular EV specifications and prices | 1 |
| Graphic part mapping (click-to-price) | 1 |
| Gravámenes (liens) | 1 |
| Green Star / Greenhouse Rating | 1 |
| GreenType (eco N/Y) | 1 |
| Grid row (posición en yard) | 1 |
| Gross margin | 1 |
| gross_margin_metric | 1 |
| Gross per copy / gross per unit | 1 |
| Gross profit retail estimado (path retail) | 1 |
| Gross profit tracking / ROI | 1 |
| Gross profit wholesale estimado (path liquidacion) | 1 |
| Gross Return % on ACV | 1 |
| gross_trainweight_kg | 1 |
| gross_vehicleweight_kg | 1 |
| grossVehicleWeightKG | 1 |
| Ground Clearance Unladen | 1 |
| Group average prices | 1 |
| Group code | 1 |
| Group stock management | 1 |
| group-level performance | 1 |
| group-level reports | 1 |
| growth brands (by market share and volume) | 1 |
| grupo de actualización (groupUpdate) | 1 |
| GT Fusion: capa de transformacion foto/IA -> presupuesto | 1 |
| GT Fusion: deteccion de dano por IA (piezas danadas) | 1 |
| GT QCheck: confirmacion/correccion de referencia OE | 1 |
| GT QCheck: deteccion de parts leakage / duplicacion | 1 |
| GT QCheck: verificacion masiva de lista de piezas | 1 |
| [EQUIP·Equipaje] Guantera con iluminación | 1 |
| Guarantee tier <$6.000 (engine noise, head gasket, transmission, transfer case, differential) | 1 |
| Guarantee tier $6.001+ (rear main seal, frame damage, suspension, cosmetic, power accessories, climate control) | 1 |
| Guaranteed First Bid / minimo garantizado (Manheim Upside) | 1 |
| Guaranteed First Bid (GFB) floor = MMR | 1 |
| guaranteed_savings_certificate_printable | 1 |
| Guaranteed Value (valor asegurado acordado, sin depreciacion) | 1 |
| GVW class (1-8) | 1 |
| Händlerbewertungen (dealer reviews) | 1 |
| Hagelschaden BVAT (dano de granizo segun norma) | 1 |
| Hagerty Hundred (100 Y/M/M mas populares asegurados, media condicion #2) | 1 |
| Hagerty Market Rating (indice 0-100) | 1 |
| Hallazgos de la prueba de conducción (test drive findings) | 1 |
| Halogen Headlamps | 1 |
| Handbrake / parking brake test | 1 |
| handelsbenaming (denominacion comercial/modelo) | 1 |
| handelsbenamingfabrikant | 1 |
| Handelsspanne (margen comercial configurable) | 1 |
| Handelswaarde excl. IVA (tradevalueExcludingVAT) | 1 |
| Handlungsempfehlungen (recomendaciones IA accionables por coche) | 1 |
| harmonised multi-market RV view | 1 |
| has_keys | 1 |
| has_secured_parties | 1 |
| has_written_off_records | 1 |
| has-map (mapa de dispersión geográfica) | 1 |
| Hauteur | 1 |
| HBV adjustment: vehicle use type (rental/fleet/personal) | 1 |
| HBV adjustment: weekly adjusted market trends | 1 |
| HBV redemption window: 14 days from purchase | 1 |
| HBV refresh: every 7 days | 1 |
| head_room | 1 |
| head_room_front | 1 |
| head_room_rear | 1 |
| head_room_third_row | 1 |
| heading | 1 |
| Headlamp Light Source | 1 |
| Headlights (high/low beam) | 1 |
| headlightType | 1 |
| Headliner condition | 1 |
| Headroom | 1 |
| heated_front_seats | 1 |
| heated_seat | 1 |
| Heated steering wheel | 1 |
| Heater | 1 |
| heavy commercial vehicles | 1 |
| hefas (eje elevable) | 1 |
| heightMM | 1 |
| HGV / truck value | 1 |
| High (extremo superior del rango) | 1 |
| High Bid | 1 |
| High risk / security marker (UK / One Auto API) | 1 |
| high_value_features | 1 |
| High-resolution images / 360 | 1 |
| High-risk vehicle alert (Security Watch) | 1 |
| highest buy offer | 1 |
| Highest volumers | 1 |
| highest-bidder status notification | 1 |
| Highest/High Authentic Value | 1 |
| Highlights / puntos destacados | 1 |
| Hill Assist | 1 |
| HIN (Hull Identification Number, marine) | 1 |
| hip_room_front | 1 |
| hip_room_rear | 1 |
| hip_room_third_row | 1 |
| Histórico de precio: bajada de precio (delta €, ej. - 1 000 EUR) | 1 |
| Histórico de precio: Preço mais baixo (flag precio mínimo alcanzado) | 1 |
| Histórico de precio: precio anterior (tachado, ej. 24 900 EUR) | 1 |
| Historial de precios del anuncio (basic/extendedPriceHistoryLink) | 1 |
| Historial de servicio (service history) | 1 |
| Historial de servicio/mantenimiento | 1 |
| Historial tecnico del vehiculo | 1 |
| Historial/provenance del vehiculo | 1 |
| Historic Monitor (forecast) values | 1 |
| Historic used values time series | 1 |
| Historic valuation (retail/trade/part-ex, past date) | 1 |
| Historic valuation data | 1 |
| Historic valuations up to 3 years (MVM) | 1 |
| Historical accuracy (published residual vs actual resale) | 1 |
| Historical advert data (price/spec/description) | 1 |
| Historical averages | 1 |
| Historical performance insights (IntelliSeller) | 1 |
| Historical price — value at a past date (מחיר היסטורי / ארכיון) | 1 |
| historical_prices | 1 |
| Historical title issue date | 1 |
| Historical title state | 1 |
| Historical values | 1 |
| historical_vehicle_photos | 1 |
| historicalAverages.last30Days (precio + odómetro) | 1 |
| historicalAverages.lastMonth | 1 |
| historicalAverages.lastSixMonths | 1 |
| historicalAverages.lastTwoMonths | 1 |
| historicalAverages.lastYear | 1 |
| Historico de especificaciones 20 anos | 1 |
| Historico de VR (hasta 4 anos) | 1 |
| Historique Disponible (flag) | 1 |
| Historique du véhicule (filtre disponibilité) | 1 |
| historique_operation_date | 1 |
| historique_operation_date_annulation | 1 |
| historique_operation_type (vocabulaire ~120 types: immatriculation, changement de titulaire, cession, gage, OTCI, DVS, OVE, reparation controlee/DEC_VE, rapport d'expert, destruction, import, immobilisation, duplicata, perte titre, modif caracteristiques, sortie territoire...) | 1 |
| Historische nieuwprijs / consumentenprijs (requisito koerslijst BPM) | 1 |
| History Adjusted Value (VIN-specific) | 1 |
| history_expert_reviews | 1 |
| history_market_comparison_pricing | 1 |
| History overview (contador de eventos por tipo) | 1 |
| history_pricing_guide_30day_autoupdate | 1 |
| History reports (integrados) | 1 |
| History-Adjusted value | 1 |
| history.event.marketplace | 1 |
| history.event.price | 1 |
| history.event.timestamp | 1 |
| history.event.type (listing/delisting/price_change) | 1 |
| history.listing_sources | 1 |
| history.listing_urls | 1 |
| Holding cost | 1 |
| Holding costs | 1 |
| holding period (tenure) | 1 |
| Home Service: 7일 시승 (7 días de prueba en casa) | 1 |
| homeService flag (엔카홈서비스) | 1 |
| homologación / tipo de homologación | 1 |
| hoogte_ondergrens_bovengrens | 1 |
| hoogte_voertuig | 1 |
| Horizonte de prevision (corto/medio/largo plazo) | 1 |
| Horn | 1 |
| hotMark | 1 |
| household analytics | 1 |
| household demographics | 1 |
| HPG Average Value (condicion #3, todos los vehiculos) | 1 |
| HPG Median Value (condicion #3) | 1 |
| HSN (Herstellerschluesselnummer) | 1 |
| httpStatusCode | 1 |
| HU/AU (fecha ITV/TÜV) | 1 |
| HUD抬头显示 | 1 |
| Huidige kilometerstand (input currentMileage) | 1 |
| Hybrid share (%) | 1 |
| Hybrid system torque | 1 |
| Hypothecation | 1 |
| IA: AutoGPT (asistente agéntico sobre ChatGPT; rollout PT pendiente) | 1 |
| IA: Descrição Automática do Anúncio (ahorra ~5 min, -40% tiempo, 87% adopción) | 1 |
| IA: Instant Ad (anuncio desde foto/vídeo) | 1 |
| IA: Respostas Automáticas (24/7) | 1 |
| IA: Vídeo Automático (vertical/Reels) | 1 |
| IAA 360 View (interior+exterior spin+zoom) | 1 |
| IAA High Resolution Images | 1 |
| IAA Key Images | 1 |
| IAA Vehicle Score (0-50) | 1 |
| IBB reference/benchmark price | 1 |
| ICV (Insured's Declared Value) | 1 |
| ID Reach | 1 |
| iDEAL payment link / enlace de pago | 1 |
| Identical/comparable vehicles on the market today | 1 |
| Identidad profesional del comprador (tax ID, grupo, postal, legal) | 1 |
| Identificacion en un solo paso (VIN o matricula) | 1 |
| idle_speed | 1 |
| Ignition | 1 |
| iihs_safety_rating | 1 |
| Image background type (white / dealership) | 1 |
| Image characteristics | 1 |
| Image count | 1 |
| Image downloads (high-quality, post-purchase) | 1 |
| Image links | 1 |
| Image overlays (badges/icons) | 1 |
| Image thumbnail | 1 |
| Image types A/B/C | 1 |
| Image URL | 1 |
| image.url | 1 |
| imageAlt | 1 |
| imageCount | 1 |
| imagenes (图片) | 1 |
| Imagenes/fotos del vehiculo | 1 |
| Imagery: >=12 high-resolution exterior shots | 1 |
| Imagery: 360-degree rotatable images | 1 |
| Imagery: interior shots | 1 |
| images / fotos | 1 |
| Images / videos (media library ChromeData) | 1 |
| Images count (per listing) | 1 |
| Images high-res | 1 |
| imageUrl | 1 |
| ImmagineSvg | 1 |
| ImmaginiRepertorio | 1 |
| immobilizer | 1 |
| Impago del IVTM | 1 |
| Impound date | 1 |
| IMS syndication | 1 |
| IMV input: vehicle history | 1 |
| imvPrice | 1 |
| in_transit | 1 |
| in-group instant offer (point of appraisal) | 1 |
| in-market incentive program | 1 |
| in-market status score | 1 |
| In-service date | 1 |
| In-stock valuation | 1 |
| Inbound private-party leads | 1 |
| Incentive: cash rebate | 1 |
| Incentive: lease special (monthly/term) | 1 |
| incentive level distribution (volume-weighted) | 1 |
| Incentive spending | 1 |
| Incentive structure [RV driver] | 1 |
| incentive value / gift card / virtual card | 1 |
| incentive.cash | 1 |
| incentive.consumerCash | 1 |
| incentive.currentRetail | 1 |
| incentive.giveaways | 1 |
| incentive.lease | 1 |
| incentive.moneyFactors | 1 |
| incentive.paymentWaivers | 1 |
| incentive.residuals | 1 |
| incentive.retailIncentives | 1 |
| incentive.specialPrograms | 1 |
| incentive.subventedAPR | 1 |
| incentives | 1 |
| Incentives / rebates / OEM rates (ChromeData Lender Desk, mapeados a zip) | 1 |
| Incentivi comunali | 1 |
| Incentivi del costruttore | 1 |
| Incentivi statali | 1 |
| Incidencia denegatoria | 1 |
| incidents | 1 |
| increasesResidualValue (flag por opción/paquete: aumenta valor residual) | 1 |
| incremental unit sales (network action impact, +32% case) | 1 |
| Incremental Vehicle Sales % | 1 |
| incremental wholesale parts opportunity | 1 |
| Independent value (channel-segmented retail) | 1 |
| Index: 1950s American (19 americanos 50s) | 1 |
| Index: Affordable Classics (13 coches ~$40k 50s-70s) | 1 |
| Index: Blue Chip (25 coleccionables posguerra) | 1 |
| Index: British Car (10 deportivos britanicos 50s-70s) | 1 |
| Index: Ferrari (13 Ferraris de calle 50s-70s) | 1 |
| Index: Japanese Vehicle (19 japoneses 60s-2010s) | 1 |
| Index: Muscle Car (muscle cars raros/codiciados) | 1 |
| Index: Postwar German (21 BMW/Mercedes/Porsche 50s-70s) | 1 |
| Index: RADindex (21 vehiculos 80s-90s) | 1 |
| Index: Supercar (15 supercars/hypercars modernos) | 1 |
| Index: Truck & SUV (18 trucks/SUV 40s-90s) | 1 |
| Indicador de baja definitiva | 1 |
| Indicador de baja temporal | 1 |
| Indicador de barniz antirrayado | 1 |
| Indicador de calidad de texto del anuncio | 1 |
| Indicador de denegatoria | 1 |
| Indicador de embargado (IND_EMBARGO) | 1 |
| indicador de entorno/ambiental de vehículo autónomo y conectado (0-100) | 1 |
| indicador de penetración de vehículo electrificado (0-100) | 1 |
| Indicador de precintado (IND_PRECINTO) | 1 |
| indicador global de electromovilidad (0-100) | 1 |
| Indicador nuevo/usado (IND_NUEVO_USADO) | 1 |
| Indicadores de calidad del anuncio (fotos presentes, alineación de precio, antigüedad de publicación) | 1 |
| Indicadores de transacciones pasadas | 1 |
| indicator_attr_badge | 1 |
| indicator_attr_body | 1 |
| indicator_attr_series | 1 |
| indicator_exclusion_age_band_2y_15y | 1 |
| indicator_exclusion_insufficient_data | 1 |
| indicator_exclusion_price_band_5k_70k | 1 |
| indicator_exclusion_written_off | 1 |
| IndicatoreNazionalizzazione | 1 |
| Indicators / hazard lights | 1 |
| indice de recomendacion (推荐指数, escala 10) | 1 |
| Induction (aspirated/turbo) | 1 |
| Industry: % loans at 0% APR | 1 |
| Industry: % shoppers $1,000+/mo payment | 1 |
| Industry: APR (avg new) | 1 |
| Industry: ATP used (1-yr, 3-yr) | 1 |
| Industry: Average loan amount | 1 |
| Industry: Average Transaction Price (ATP) new | 1 |
| Industry: Down payment (avg) | 1 |
| industry drivers | 1 |
| Industry: Incentives as % of ATP | 1 |
| Industry: Lease penetration | 1 |
| Industry: Loan term | 1 |
| Industry: Monthly payment (financed) | 1 |
| Industry: Negative equity | 1 |
| industry pulse (thought leaders) | 1 |
| Industry: SAAR / new vehicle sales forecast | 1 |
| inferred_sales_count_90d | 1 |
| Inflated valuation detection | 1 |
| influence.body (efecto carrocería) | 1 |
| influence.professional-fees (frais professionnels) | 1 |
| influence.release (efecto antigüedad) | 1 |
| Informazioni su uso e destinazione d'uso | 1 |
| Informe de tasación PDF | 1 |
| informe de valoración customizable | 1 |
| informe de vehículos predefinido | 1 |
| infotainment features | 1 |
| Infracciones | 1 |
| ingangsdatum_gebrek | 1 |
| Ingevulde kilometerstand | 1 |
| InizioImmatricolazione | 1 |
| InizioVendita | 1 |
| Injury prediction (casualty AI) | 1 |
| Input MMR: country (parámetro internacional) | 1 |
| Input MMR: date (histórica hasta 2018-11-01) | 1 |
| Input MMR: evbh | 1 |
| Input MMR: excludeBuild | 1 |
| Input MMR: extendedCoverage | 1 |
| Input MMR: include | 1 |
| Input MMR: orderBy | 1 |
| Input MMR: orgId | 1 |
| Input MMR: SUBSERIES | 1 |
| Input MMR: zipCode | 1 |
| inrichting (carroceria/uso) | 1 |
| Inruilen bij een autobedrijf | 1 |
| Inserats-Analyse 60-day sale probability (Verkaufswahrscheinlichkeit, first 60 Standtage) | 1 |
| Inserats-Analyse Marktvergleich (similar competitor vehicles, up to ~100 attributes) | 1 |
| Inserats-Analyse next price-label delta (EUR to reach next category) | 1 |
| Inserats-Analyse performance metrics (views/emails/calls/parkings) | 1 |
| Inserats-Analyse search-results page | 1 |
| Inserats-Analyse search-results position (rank) | 1 |
| Inseratsqualität-Bewertung (listing quality score) | 1 |
| Insight: anomaly reporting (variance vs competitors) | 1 |
| Insight: company car performance | 1 |
| Insight: leasing price lists | 1 |
| Insight: position summary & threats | 1 |
| Insight: tyre prices (NL) | 1 |
| Insight: van performance | 1 |
| Insights abiertos (Diário Automóvel): precio medio / barómetros / tendencias VO (datos ACAP) | 1 |
| Insights: affordability metrics | 1 |
| Insights: hybrid_share | 1 |
| Insights: New Car Pricing Index (NCPI = coste total compra+financiacion vs MSRP, %) | 1 |
| Insights: new_days_on_lot | 1 |
| Insights: new_vehicle_sales (SAAR, YoY) | 1 |
| Insights: price_band_breakdown (<$20K, <$30K) | 1 |
| Insights: used_days_on_lot / days_to_turn | 1 |
| Insights: used_vehicle_sales | 1 |
| Inspector notes / additional info | 1 |
| Inspector/assessor | 1 |
| Instalaciones por tipo de conector por pais | 1 |
| install_type (factory/port/dealer) | 1 |
| installationHeight (mm) | 1 |
| installed_equipment | 1 |
| instant buy fee ($350) | 1 |
| Instant consumer part-exchange valuation (Consumer Pro) | 1 |
| instant_offer_adjustment_flag | 1 |
| Instant Offer eligibility (<=2018, <$30k, CarMax <100mi) | 1 |
| instant_offer_input_state | 1 |
| instant_offer_validity_7_days | 1 |
| instant_offer_value | 1 |
| inStockDate | 1 |
| Insured Declared Value IDV (InsuranceDekho) | 1 |
| Insured name | 1 |
| Insurer contact | 1 |
| Insurer name | 1 |
| Integracion VHR (CarFax / AutoCheck / CarProof) | 1 |
| Intelligent recommendations (forecourt + bid-history based) | 1 |
| Intelligent review triage | 1 |
| Intención/estado del proyecto de reprise | 1 |
| Intent / manipulation signals | 1 |
| intent signals (demanda shopper + oferta mercado, >10B/mes) | 1 |
| intent-to-buy score | 1 |
| Inter-company transfers | 1 |
| inter-group transfer bill-of-sale | 1 |
| Interactive map | 1 |
| Intercooler | 1 |
| InteressiGiorniVendita | 1 |
| Interior (spec) | 1 |
| Interior cosmetic defects | 1 |
| interior fabric_type / upholstery type | 1 |
| Interior fittings & electrical controls [128] | 1 |
| interior is_two_tone | 1 |
| interior primary_rgb_code | 1 |
| Interior score (x/10) | 1 |
| interior secondary_rgb_code | 1 |
| interior_volume | 1 |
| Interior wear | 1 |
| interiorType (leather/alcantara) | 1 |
| internalNumber | 1 |
| internalReference | 1 |
| Internet/online price - high valuation | 1 |
| Internet/online price - low valuation | 1 |
| Interni | 1 |
| InterrogazioniResidue | 1 |
| InterrogazioniTotali | 1 |
| IntervalloTagliando | 1 |
| intervalMonth | 1 |
| Intervalos de mantenimiento | 1 |
| InterventiCarrozzeria | 1 |
| InterventiMeccanica | 1 |
| Invasiones territoriales | 1 |
| InVendita | 1 |
| Invernale | 1 |
| inversión en I+D del sector (€) | 1 |
| Inverter coolant level | 1 |
| Invoerrechten (derechos de importación) | 1 |
| invoiceMax | 1 |
| invoiceMin | 1 |
| Invoicing assignment (asignación de facturación) | 1 |
| [EQUIP·Confort] Ionizador de aire interior | 1 |
| IoT projects (3200 / 100+ countries) | 1 |
| Ipoteche (presenza) | 1 |
| IPT (imposta provinciale di trascrizione, per provincia) | 1 |
| is_certified | 1 |
| is_fuel_catalyst | 1 |
| is_platform_shared | 1 |
| is_searchable | 1 |
| ISOFIX Child Seat Mounts | 1 |
| isOwnerPartner | 1 |
| issueNumber | 1 |
| Issues count / Good items count | 1 |
| isVerifyOwner (propietario verificado) | 1 |
| ISWS presale listings search (run-lists) | 1 |
| isYellow (matrícula amarilla/comercial) | 1 |
| Italian system code | 1 |
| Item number | 1 |
| ITS institute code (kod-instytutu-transportu-samochodowego) | 1 |
| ivin_best_time_to_buy | 1 |
| ivin_best_time_to_sell | 1 |
| ivin_market_value_price_analysis (local fair market) | 1 |
| ivin_selling_history (cambios de precio, anuncios previos) | 1 |
| ivin_similar_cars_comparison (price/mileage/market value) | 1 |
| ivin_vehicle_condition_analysis (avg miles vs edad) | 1 |
| Izmo image mapping | 1 |
| jaar_laatste_registratie_tellerstand | 1 |
| JATO ID (decode link id) | 1 |
| JATO UID / Instance ID (global unique vehicle id) | 1 |
| jatoVehicleId (mapeo a catálogo JATO Dynamics) | 1 |
| JavaScript Widget (multiples dimensiones) | 1 |
| Job frequencies | 1 |
| Job Status / Estimate Status (Calculated/Not Calculated/Open/Closed) | 1 |
| JSI record source / consolidator | 1 |
| JSI reporting entity type: Individual | 1 |
| JSI reporting entity type: Insurer | 1 |
| JSI reporting entity type: Recycler | 1 |
| JSI reporting entity type: Shredder | 1 |
| Kaufkraft / Zeit-bis-Kauf (purchasing power / time-to-buy regional) | 1 |
| kba HSN (Herstellerschlüsselnummer) | 1 |
| kba TSN (Typschlüsselnummer) | 1 |
| KBA-Schluessel (clave oficial HSN-TSN) | 1 |
| KBB (Kelley Blue Book) ID mapping | 1 |
| KBB Instant Cash Offer (ICO) | 1 |
| KBB Instant Cash Offer value | 1 |
| KEINE ANGABE (estado sin label por pocos comparables) | 1 |
| Kelley Blue Book Car ID | 1 |
| Kelley Blue Book (KBB) value | 1 |
| Key (present) | 1 |
| key competitors taking share | 1 |
| KeyLess Entry | 1 |
| Keyless Ignition | 1 |
| keys | 1 |
| Keys available (has keys) | 1 |
| Keys condition | 1 |
| keys_present | 1 |
| Kibbutz/institution deduction | 1 |
| Kilómetros (ficha) | 1 |
| [MED·Prueba] Kilómetros de la prueba (iniciales/finales) | 1 |
| Kilómetros del vehículo (km) | 1 |
| Kilométrage | 1 |
| Kilométrage Faible (flag) | 1 |
| kilométrage-standard (Essence 15000 / Diesel-Hybride 25000 / Electrique 12500 / Gaz-Hydrogène 20000 km/an) | 1 |
| kilowatt | 1 |
| klasse_hybride_elektrisch_voertuig (OVC/NOVC-HEV/FCHV) | 1 |
| klassifizierende Daten | 1 |
| Konkurrenzpreise (competitor prices) | 1 |
| Kopen bij BOVAG autobedrijf met garantie | 1 |
| KPI de rendimiento de remarketing | 1 |
| KPI eficiencia operativa | 1 |
| KPI estandarizado de postventa | 1 |
| KPI monitoring por tienda | 1 |
| KPI objetivo 2030: 100% eléctrico en 2035 | 1 |
| KPI objetivo 2030: cuota de producción electrificada (>=40%) | 1 |
| KPI objetivo 2030: empleo (1,9M) | 1 |
| KPI objetivo 2030: inversión pública (€6.000M) y privada (~€40.000M) | 1 |
| KPI objetivo 2030: producción (2,7M uds) | 1 |
| KPI objetivo 2030: valor del sector (€120.000M) | 1 |
| KPI overlay on map | 1 |
| KPI productividad | 1 |
| KPI rentabilidad | 1 |
| KPIs personalizables | 1 |
| línea / referencia 1 (line1) | 1 |
| Línea / versión [A] | 1 |
| La Centrale Pro: filtres/alertes personnalisés | 1 |
| La Centrale Pro: inventaire B2B (opportunités de sourcing, ~50 000) | 1 |
| La Centrale Pro: messagerie intégrée (+WhatsApp) | 1 |
| laadvermogen | 1 |
| Labor hours | 1 |
| Labour category (Mechanics/Panel/Paint/Electrical/Trim) | 1 |
| Lackierung / Lackierungsaufwaende (pintura: DAT-Eurolack/AZT-Lack/fabricante) | 1 |
| Lackierungskosten (coste de pintura del dano) | 1 |
| lado de conduccion LHD/RHD (rudder) | 1 |
| Lane Centering Assistance | 1 |
| Lane Departure Warning (LDW) | 1 |
| Lane Keeping Assistance (LKA) | 1 |
| Lane monitor alert (Stockwave Plus) | 1 |
| Lane number | 1 |
| Lane/Run | 1 |
| language | 1 |
| Largeur pneu arrière | 1 |
| Largeur pneu avant | 1 |
| Largeur sans rétros | 1 |
| LarghezzaMetri | 1 |
| Last CPO (Certified Pre-Owned) Date | 1 |
| Last enquiries: check frequency | 1 |
| Last enquiries: check timestamps | 1 |
| Last enquiries: map | 1 |
| last_known_titling_state | 1 |
| last_seen_at | 1 |
| last_seen_at_date | 1 |
| last_seen_date | 1 |
| last_seen_vdp_url | 1 |
| Last Title Date | 1 |
| Last Title State | 1 |
| last_update_date (bulk) | 1 |
| last_updated | 1 |
| lastMotTestDate (bulk) | 1 |
| Latitudine | 1 |
| Laufzeit (plazo de pronostico, hasta 72 meses) | 1 |
| LCV: accesorios | 1 |
| LCV: condicion zona de carga (load area) | 1 |
| LCV: estanterias/racking | 1 |
| LCV load volume [PARCIAL] | 1 |
| LCV payload [PARCIAL] | 1 |
| LCV: rotulacion (signwriting) | 1 |
| LCV value | 1 |
| lead (LeadBox, CRM-synced: Dealer Desk / Auto-CRM / CATCH) | 1 |
| lead capture (contact) | 1 |
| Lead contact (nome/cognome, email, telefono, azienda) | 1 |
| Lead: nombre, apellidos, teléfono, email, mensaje | 1 |
| lead quality | 1 |
| Lead source / atribucion (cid, aff_cid, pag_id, vdp, partner_offer_id, origin_type) | 1 |
| lead_source_marketplace_affinity | 1 |
| lead source performance | 1 |
| Lead time (per order/gateway) | 1 |
| Lead volume (del CRM / interes del consumidor) | 1 |
| lead-potential forecast (impacto de cambio de precio) | 1 |
| Leads (per day / by MMT / MTD leads) | 1 |
| Leads / Inquiries (listing analytics) | 1 |
| Leads de WhatsApp IA 24/7 (+20% incrementales / +55% conversion) | 1 |
| leads_high_intent_buyer | 1 |
| Leads = oportunidad real de negocio (KPI B2B) | 1 |
| Lease amount remaining | 1 |
| lease_down_payment | 1 |
| lease_emp | 1 |
| Lease monthly payment | 1 |
| Lease number payments (meses restantes) | 1 |
| lease payment | 1 |
| lease_payment_estimate | 1 |
| lease_term | 1 |
| leaseRentInfo (info leasing/rent) | 1 |
| leasing classification | 1 |
| Leasing-financial deduction (ליסינג מימוני) | 1 |
| Leasing-operational deduction (ליסינג תפעולי) | 1 |
| Leather flag | 1 |
| Leather upholstery addition (ריפודי עור) | 1 |
| Leather Wrapped Steering Wheel | 1 |
| Lebenszykluskurve (curva de ciclo de vida / depreciacion) | 1 |
| Lectura de arco RFID/LPR (paso del vehículo + alerta en tiempo real) | 1 |
| Lecturas del cuentakilómetros (fecha) | 1 |
| LED DRLs | 1 |
| LED Fog Lamps | 1 |
| LED Headlamps | 1 |
| LED Taillights | 1 |
| leg_room | 1 |
| leg_room_front | 1 |
| leg_room_rear | 1 |
| leg_room_third_row | 1 |
| legacy_id | 1 |
| Legislation / regulatory compliance data (WLTP/NEDC) | 1 |
| Legroom | 1 |
| Lender criteria | 1 |
| Lender: Loan-to-Value (LTV) threshold input | 1 |
| lender name | 1 |
| Lender: value impact of negative events (30%+) | 1 |
| lenderDesk.captiveVsNonCaptive | 1 |
| lenderDesk.cashProgram | 1 |
| lenderDesk.creditTiers | 1 |
| lenderDesk.fees | 1 |
| lenderDesk.leaseProgram | 1 |
| lenderDesk.lenderGuidelines | 1 |
| lenderDesk.loanProgram | 1 |
| lenderDesk.paymentQuote (loan/lease) | 1 |
| lenderDesk.terms | 1 |
| Lending Value (wholesale/retail lender benchmark; B2B only) | 1 |
| lengte | 1 |
| lengte_ondergrens_bovengrens | 1 |
| lengthMM | 1 |
| lessor vehicle holding period | 1 |
| Letter date | 1 |
| Letter of guarantee | 1 |
| Libro de mantenimiento completo si/no (hasFullServiceHistory) | 1 |
| licence.validFrom | 1 |
| licence.validTo (expiry) | 1 |
| licenceStatus (Valid) | 1 |
| licenceType (Full/Provisional) | 1 |
| License/circulation fee + renewal (אגרת רישוי וחידושה) | 1 |
| licensedWeight (kg) | 1 |
| licensePlate / kenteken | 1 |
| Licensing group — private + commercial up to 4t (קבוצת רישוי) | 1 |
| Lidar (yes/no, filtro) | 1 |
| life stage | 1 |
| Lifecycle gateway status (arrival/handover/return/inspection/sales) | 1 |
| Lifecycle stage (recon to retail) | 1 |
| lifecycle timeline dates | 1 |
| Lifecycle trend | 1 |
| lifestyle | 1 |
| lifestyle gallery photo (shot_code/shot_name) | 1 |
| liftingCapacity (kg, commercial) | 1 |
| light commercial vehicles (LCV) in operation | 1 |
| Lightbulbs (appraisal-like de un clic) | 1 |
| Lights status | 1 |
| Limitaciones de disposición | 1 |
| [EQUIP·Confort] Limpiaparabrisas automático | 1 |
| Line-item work approval | 1 |
| Lineas de daño con hasta 5 imagenes c/u | 1 |
| link | 1 |
| link_active | 1 |
| Link al Condition Report completo | 1 |
| linked vehicles (RV de grupo enlazado) | 1 |
| LinkStampaCertificata | 1 |
| LinkSVG | 1 |
| lista de equipamiento/configuracion (配置/equipment[]) | 1 |
| Lista de lenders para payoff (equity/lenders) | 1 |
| Listado de vehículos a nombre del solicitante | 1 |
| Listing: 360-degree imagery | 1 |
| listing_ancap_safety_rating | 1 |
| Listing: CAP pricing intelligence (valor CAP, gratis) | 1 |
| listing_compliance_date | 1 |
| Listing condition (New/Used) | 1 |
| listing_confidence | 1 |
| listing_date (Newest/Oldest listed) | 1 |
| listing_doors | 1 |
| listing_drive | 1 |
| Listing: Glass's valuation data (gratis) | 1 |
| Listing: high-resolution images | 1 |
| Listing photo gallery (count) | 1 |
| listing_photos | 1 |
| Listing: sale lane / lot number | 1 |
| Listing: save-search / stock alerts (24/7) | 1 |
| listing_seats | 1 |
| listing_series | 1 |
| Listing status (For Sale / Sold / Not Sold / High Bid) | 1 |
| Listing URL / item URL | 1 |
| Listing: vehicle appraisal data | 1 |
| Listing: vehicle provenance information | 1 |
| Listing/post date | 1 |
| live_auction | 1 |
| live_comparables / similar_cars_for_sale | 1 |
| Live market data appraisal (trade-in) | 1 |
| Live market value (retail & trade) | 1 |
| Live sale audio/video | 1 |
| Live value movement count (6M between monthly publications) | 1 |
| livemarket_annual_stock_turn | 1 |
| livemarket_delisted_sold_data_12m | 1 |
| livemarket_historical_pricing | 1 |
| livemarket_last_delisted_price | 1 |
| livemarket_listing_leads_enquiries | 1 |
| livemarket_listing_views | 1 |
| livemarket_market_benchmarking | 1 |
| livemarket_realtime_pricing_vs_similar | 1 |
| livemarket_stock_age | 1 |
| livemarket_weekly_pricing_opportunities | 1 |
| [EQUIP·Seguridad] Llamada de emergencia (eCall) | 1 |
| Llamadas: origen y atencion (Call Tracking IA) | 1 |
| Llantas - condición (rims) | 1 |
| [EQUIP·Llantas] Llantas de aleación (medida/acabado, p.ej. 19" 235/45 bicolor) | 1 |
| [EQUIP·Confort] Llave digital | 1 |
| loadCapacity (kg) | 1 |
| Loading capacity / Cargo volume | 1 |
| Loan payoff | 1 |
| loan_record | 1 |
| loan term | 1 |
| loan_term_input | 1 |
| loan-to-value (LTV) | 1 |
| Loan/Whole value (xclean/clean/avg/rough) | 1 |
| Local competitor insights | 1 |
| local consumer preference | 1 |
| local_market_report_by_zip (iVIN Pro) | 1 |
| Local market trends | 1 |
| Local vehicle insights | 1 |
| local/national composite benchmark | 1 |
| Localidad del domicilio del vehículo | 1 |
| Localidad del vehículo | 1 |
| Localisation (CP / ville / carte) | 1 |
| localização (cidade / estado) | 1 |
| Localización de daño por IA sobre foto (Qapter) | 1 |
| Logística de retirada del vehículo (toda España) | 1 |
| Logbook loan / inherited debt | 1 |
| logbook loan check | 1 |
| Logbook loan indicator | 1 |
| Logistics / transport cost | 1 |
| Logistics / vehicle movement | 1 |
| Lohnkosten (coste de mano de obra) | 1 |
| Long order codes | 1 |
| Long type name | 1 |
| longitud mm (long) | 1 |
| [MED·Habitabilidad 2ª fila] Longitud/piernas (cm) | 1 |
| Longitudine | 1 |
| Longueur | 1 |
| Loss category ABI Cat A/B/S/N (UK/EU) | 1 |
| Loss Date | 1 |
| Loss forecast | 1 |
| Loss reserves | 1 |
| Loss Vehicle | 1 |
| losses (direct attribution) | 1 |
| Lot condition code | 1 |
| Lot date / Listed date | 1 |
| lot_final_bid | 1 |
| lot_photos | 1 |
| lot_sale_datetime | 1 |
| lot_sale_document_title_code | 1 |
| lot_sold_status | 1 |
| lot_source_copart_iaai | 1 |
| LotVision bulk search (up to 300 vehicles) | 1 |
| LotVision DTC Codes column (7,000+ generic SAE codes) | 1 |
| LotVision DTC description + last-read timestamp | 1 |
| LotVision search by Work Order number (post-purchase) | 1 |
| LotVision Show My Position | 1 |
| Low (extremo inferior del rango) | 1 |
| Lowest Sale | 1 |
| loyalty matrix | 1 |
| LTM (Last Twelve Months) window | 1 |
| LTV (loan-to-value) over time | 1 |
| lubrication_system | 1 |
| [EQUIP·Confort] Luces automáticas | 1 |
| [EQUIP·Decoración] Luces traseras LED | 1 |
| Luggage / boot capacity | 1 |
| lumbar_adjustment | 1 |
| lumbar_support | 1 |
| [EQUIP·Confort] Lunas tintadas | 1 |
| [EQUIP·Confort] Lunas traseras sobretintadas | 1 |
| [EQUIP·Seguridad] Luneta térmica | 1 |
| LunghezzaMetri | 1 |
| luxury_features | 1 |
| [EQUIP·Confort] Luz anticharco | 1 |
| [EQUIP·Confort] Luz de lectura delantera | 1 |
| [EQUIP·Confort] Luz de lectura trasera | 1 |
| [EQUIP·Seguridad] Luz diurna LED | 1 |
| [EQUIP·Confort] Luz en los marcos de las puertas | 1 |
| [EQUIP·Confort] Luz interior ambiental | 1 |
| [EQUIP·Confort] Luz interior en zona de pies | 1 |
| LV production volume (forecast) | 1 |
| Média anual de referência (variação 2024) | 1 |
| Mínimo (código opcional) | 1 |
| Método de reparación óptimo (reparar vs sustituir) | 1 |
| métricas de uso real para reporting ESG / CSRD | 1 |
| Máximo (código opcional) | 1 |
| M.O. pintura (UTS) | 1 |
| m.Q average price (Durchschnittspreis) | 1 |
| m.Q average price change (YoY %) | 1 |
| m.Q average vehicle age (Durchschnittsalter) | 1 |
| m.Q car parc / fleet stock (Bestand der Pkw-Flotte, millions) | 1 |
| m.Q top searched equipment features (% e.g. Schiebedach/Standheizung/CarPlay) | 1 |
| m.Q top searched vehicle types (% Limousine/Kombi/SUV) | 1 |
| m.Q total listings (Inserate count) | 1 |
| Macro trend time series (since 2007) | 1 |
| Macro-categoria (CodMacroCategoria) | 1 |
| macro-economic overlay | 1 |
| Macroeconomic factors | 1 |
| made_in | 1 |
| Maintenance & Repairs (total + Y1-Y5) | 1 |
| maintenance codes | 1 |
| maintenance_conditions_normal_severe | 1 |
| maintenance_had_one_condition | 1 |
| Maintenance interval | 1 |
| Maintenance intervals (time) | 1 |
| maintenance_menus | 1 |
| Maintenance Minder items / services due | 1 |
| maintenance_tracking_auto_store | 1 |
| maintenance_value | 1 |
| maintenance_value_high | 1 |
| maintenance_value_low | 1 |
| maintenanceActionId | 1 |
| Maior valorização / maior desvalorização del mes | 1 |
| Major bodyshop repair | 1 |
| makeDescription (marca) | 1 |
| MakeId | 1 |
| MakeName | 1 |
| [EQUIP·Equipaje] Maletero con iluminación | 1 |
| Manage Offers | 1 |
| Manager approval (aprobacion de oferta de trade) | 1 |
| [EQUIP·Confort] Mando de apertura a distancia | 1 |
| [EQUIP·Seguridad] Mandos multifunción en volante | 1 |
| Manheim App: real-time notifications | 1 |
| Manheim App: Simulcast (puja en vivo) | 1 |
| Manheim Express: Guaranteed First Bid / Upside | 1 |
| Manheim Express/App: AutoCheck Snapshot (historial Experian) | 1 |
| Mantenimiento (registro electrónico de talleres) | 1 |
| Manufacture date (fecha de fabricacion) | 1 |
| manufactureDate | 1 |
| Manufacturer Address/City/State/Country | 1 |
| manufacturer_code | 1 |
| Manufacturer DBA/Trade Names | 1 |
| Manufacturer Id | 1 |
| manufacturer_incentives | 1 |
| Manufacturer marketing message | 1 |
| manufacturer rebates | 1 |
| Manufacturer specifications | 1 |
| Manufacturer Type | 1 |
| Manufacturer warranty status effect (אחריות יצרן) | 1 |
| manufacturerCode | 1 |
| ManufacturerIdentificationCode | 1 |
| manufacturerName (fabricante de la opción) | 1 |
| manufacturerWarrantyCorrosionDurationYears | 1 |
| manufacturerWarrantyStandardDurationYears | 1 |
| manufactureYear (PARCIAL, recien matriculados) | 1 |
| Manufacturing plant | 1 |
| Mapeo de red competitiva | 1 |
| Marge de Manœuvre (leeway.percentage / leeway.value) | 1 |
| Marge/KPIs (margin per vehicle) | 1 |
| Margen VO vs VN | 1 |
| Margin adjustment | 1 |
| margin_gap_vs_hammer | 1 |
| Margin protection | 1 |
| Margin vs days-to-sale trade-off | 1 |
| Marke (make) | 1 |
| Market | 1 |
| Market activity tracking (by model/geography/dealer group) | 1 |
| Market average / comparison to rest of market | 1 |
| Market: average age (months) | 1 |
| market_average_price_baseline | 1 |
| Market: average sold price (wholesale) | 1 |
| Market: buyer attendance per auction | 1 |
| Market: CAP value movement / CAP performance (% vs CAP) | 1 |
| market channel: Manufacturers (Car Manufacturer) | 1 |
| market channel: Private Market | 1 |
| market channel: Short-Term Rental / Rent-a-car (RAC) | 1 |
| market channel: True Fleet (genuine company fleet) | 1 |
| Market Driven Value (actual cash value / ACV) | 1 |
| Market fit (encaje con mercado local oferta/demanda) | 1 |
| Market: fuel-type split (petrol/diesel/hybrid/PHEV/BEV) | 1 |
| Market growth forecast / CAGR | 1 |
| Market Guide 2.0: forecast precio a 30 dias | 1 |
| Market Guide 2.0: forecast precio a 60 dias | 1 |
| Market Guide 2.0: forecast precio a 90 dias | 1 |
| Market Guide: Average wholesale price | 1 |
| Market Guide filtro: date sold | 1 |
| Market Guide filtro: fuel | 1 |
| Market Guide: Highest wholesale price | 1 |
| Market Guide: historical lookback 30-180 dias (ajuste estacional) | 1 |
| Market Guide: Lowest wholesale price | 1 |
| Market health | 1 |
| Market Health by vehicle age band (≤1y/1-3y/3-5y/5-10y/>10y) | 1 |
| Market Health Gesamtmarkt change (YoY %) | 1 |
| Market Health index value (supply Inserate / demand Leads, Ø=100) | 1 |
| Market Insight filter: age band | 1 |
| Market Insight Market Condition (supply vs demand) | 1 |
| market opportunity (quantified) | 1 |
| Market overview (vs whole retail market) | 1 |
| market penetration | 1 |
| Market Rating: Auction Median Price of Cars Sold (12m) | 1 |
| Market Rating: Auction Overall Count of Cars Sold (media movil 12m) | 1 |
| Market Rating band (deflacionario <35 / plano 40-50 / peak 60-75 / burbuja >80) | 1 |
| Market Rating: Correlated Instrument - precio mediano de vivienda US | 1 |
| Market Rating: Correlated Instrument - precio spot del oro | 1 |
| Market Rating: Correlated Instrument - retail sales | 1 |
| Market Rating: Correlated Instrument - S&P 500 | 1 |
| Market Rating: Expert Opinion Market Survey (escala 1-100) | 1 |
| Market Rating: HPG Indices input (Hundred + Blue Chip, condicion #2) | 1 |
| Market Rating: Insured Values Broad Market ratio ($20k-$200k, sube vs baja) | 1 |
| Market Rating: Insured Values High End ratio (>$200k, sube vs baja) | 1 |
| Market Rating: Private Sales % Selling Above Insured Values | 1 |
| Market Rating: Private Sales Average Sales Price (12m) | 1 |
| Market: retail metrics (price/demand, granularidad parcial) | 1 |
| market_sector_code | 1 |
| market size | 1 |
| Market strategy | 1 |
| market trend analysis | 1 |
| market_trends | 1 |
| Market: used transaction volume forecast | 1 |
| Market Value Assessor (combined current+retail+forecast value) | 1 |
| Market value comparisons / comps | 1 |
| market_value_condition_average | 1 |
| market_value_condition_clean | 1 |
| market_value_condition_rough | 1 |
| market_value_lower_bound | 1 |
| Market Value of the vehicle (umbral siniestro total; no en todos los mercados) | 1 |
| market_value_upper_bound | 1 |
| Market: wholesale market health index (escala 1-100; first of its kind) | 1 |
| Market-backed total-loss valuation | 1 |
| Market-Based factor: daily market data | 1 |
| Market-Based factor: province | 1 |
| Market-Based factor: seasonality | 1 |
| Market-Based Value (point) | 1 |
| marketcheck_price | 1 |
| marketClass | 1 |
| marketing attribution (sales match to real transactions) | 1 |
| Marketing-Intensität Wettbewerber (competitor marketing/visibility products) | 1 |
| marketplace_image_url | 1 |
| marketplace_price | 1 |
| marketplace_price_type | 1 |
| Marktanteile Handel (cuota freier/Marken/Privat) | 1 |
| Marktentwicklung (market development panel) | 1 |
| Marktpreis (market price calculado) | 1 |
| Marktwaarde (seguro = dagwaarde/Koerslijst + 10%) | 1 |
| Marktwert (market value B2C) | 1 |
| Masa máxima técnicamente admisible / MMTA | 1 |
| Masa maxima autorizada / MMA (grossVehicleWeight) | 1 |
| mass in running order (masa-pojazdu-gotowego-do-jazdy) | 1 |
| massa_bedrijfsklaar_min_max | 1 |
| massa_ledig_voertuig | 1 |
| massa_rijklaar | 1 |
| MassaKG | 1 |
| massaledig_ondergrens_bovengrens | 1 |
| massarijklaar_ondergrens_bovengrens | 1 |
| MassaRimorchiabile | 1 |
| MassaTotaleBatterieKg | 1 |
| Material de pintura (total) | 1 |
| Materiales de pintura por superficie | 1 |
| materiele_gevolgen | 1 |
| max bid (proxy) | 1 |
| Max Margin recommendation | 1 |
| max_offer.admin | 1 |
| max_offer.lot | 1 |
| max_offer.price | 1 |
| max_offer.profit_margin | 1 |
| max_offer.reconditioning | 1 |
| max_offer.transport | 1 |
| max_payload | 1 |
| max_seating | 1 |
| max_speed_kmh | 1 |
| max_torque_at (rpm) | 1 |
| max_towing_capacity | 1 |
| max trailer gross mass with brake (max-masa-calkowita-przyczepy-z-hamulcem) | 1 |
| max trailer gross mass without brake (max-masa-calkowita-ciagnietej-przyczepy-bez-hamulca) | 1 |
| Max Vehicle Severity | 1 |
| max_vermogen_15_minuten | 1 |
| maxconstructiesnelheid_ahw_ogr_bgr | 1 |
| maximale_constructiesnelheid | 1 |
| Maximum / proxy bid | 1 |
| maximum axle load (maksymalny-nacisk-osi) | 1 |
| maximum_last_onder_vooras_koppeling | 1 |
| maximum_massa_samenstelling | 1 |
| maximum_massa_trekken_ongeremd | 1 |
| maximum_ondersteunende_snelheid | 1 |
| maximum payload (maksymalna-ladownosc) | 1 |
| maximum_trekken_massa_geremd | 1 |
| maximum wheel track (max-rozstaw-kol) | 1 |
| maximummassa_ondergrens_bovengrens | 1 |
| maxondersteundesnelheid_ogr_bgr | 1 |
| maxverticalebelastopkopp_ogr_bgr | 1 |
| mc_category | 1 |
| mc_rooftop_id | 1 |
| mc_website_id | 1 |
| mds | 1 |
| Mechanical: AC | 1 |
| Mechanical: brakes | 1 |
| Mechanical breakdown repairs | 1 |
| Mechanical: catalytic converter | 1 |
| Mechanical condition | 1 |
| Mechanical defects | 1 |
| Mechanical: exhaust | 1 |
| Mechanical: head gasket | 1 |
| Mechanical: oil leak | 1 |
| Mechanical: other (+ mechanical_other_note) | 1 |
| Mechanical: sunroof/moonroof | 1 |
| Mechanical: suspension | 1 |
| Mechanical/technical condition | 1 |
| Media | 1 |
| Media CPM | 1 |
| Media Network: % buy within 6 months (81-83%) | 1 |
| Media Network: % undecided what to buy (72-73%) | 1 |
| Media Network: % undecided where to buy (88-90%) | 1 |
| Media Network: impressions to high-intent shoppers | 1 |
| Media Network: sales_influenced_by_Cars.com (+29%) | 1 |
| Media Network: unique_monthly_in_market_shoppers (26-29M) | 1 |
| Media Network: website_leads (2x) | 1 |
| media UE de cada indicador de electromovilidad | 1 |
| mediaGallery.view.backgroundDescription | 1 |
| mediaGallery.view.shotCode | 1 |
| mediahouse_audience_buying_journey_stage | 1 |
| mediahouse_audience_intent_based | 1 |
| mediahouse_audience_socio_demographic_profiles | 1 |
| mediahouse_carsales_capi_attribution | 1 |
| mediahouse_carsales_id_people_targeting | 1 |
| mediahouse_carsales_match_firstparty_lookalike | 1 |
| Medias sectoriales anonimizadas | 1 |
| medida: cuota | 1 |
| Medida de llanta delantera | 1 |
| Medida de llanta trasera | 1 |
| Medida de llanta/llanta de aleación | 1 |
| Medida de neumáticos | 1 |
| medida: unidades | 1 |
| medida: variación | 1 |
| medium commercial vehicles | 1 |
| Meeneemprijs (nombrada en intro; no etiquetada en el resultado del coche probado) | 1 |
| meer_informatie_op_internet | 1 |
| meer_informatie_via_telefoonnummer | 1 |
| Meetgo: 방문/배송 (visita/entrega trusted) | 1 |
| meetGo flag (엔카밋고) | 1 |
| mejor momento para vender (最佳卖车时机) | 1 |
| meld_datum_door_keuringsinstantie | 1 |
| meld_tijd_door_keuringsinstantie | 1 |
| meldende_producent_distributeur | 1 |
| member_only_offers | 1 |
| Mensualité (€/mois) | 1 |
| Mercado relevante depurado por canales | 1 |
| Mercato | 1 |
| Merchandise Health score | 1 |
| Merchandising performance | 1 |
| merk_object_toegevoegd | 1 |
| merkantiler Minderwert [NO-VERIFICADO] | 1 |
| merkcoderdw | 1 |
| Merkzetteleinträge (watchlist entries) | 1 |
| mes de vigencia / actualización mensual del valor | 1 |
| mes_referencia (ex.: 'abril de 2026') | 1 |
| Mese | 1 |
| MeseImmatricolazione | 1 |
| MeseInfocar | 1 |
| MesePrevisione | 1 |
| metallic | 1 |
| Method Of Delivery | 1 |
| metodo de envio (Container / Ro-Ro) | 1 |
| mfgCampaignNo | 1 |
| mfrModelCode (MMC) | 1 |
| MI dashboard (insights, trend monitoring, descarga de datos) | 1 |
| Microvetture | 1 |
| Mietwagen-Preisindex / Mietwagenklasse | 1 |
| Mietwagenklasse (clase de alquiler, 11 clases) | 1 |
| miles | 1 |
| Miles driven | 1 |
| milieuklasse_eg_goedkeuring_licht | 1 |
| milieuklasse_eg_goedkeuring_zwaar | 1 |
| min_ground_clearance | 1 |
| min_kerbweight_kg | 1 |
| Min seats | 1 |
| Minimum bid recommendation (IntelliSeller) | 1 |
| Minimum transaction threshold (6/year + 2/90 days) | 1 |
| minimum wheel track (min-rozstaw-kol) | 1 |
| Minimum wholesale guarantee (buy limit por adelantado) | 1 |
| minimumKerbWeightKG | 1 |
| minimummassavoltooid | 1 |
| MiniVoltura | 1 |
| Minor bodyshop repair | 1 |
| Miscellaneous Adjustments (Minor Work) | 1 |
| missing vehicle details flag | 1 |
| missing/lost service traffic | 1 |
| Mitchell's repair pricing | 1 |
| Mixture/feed system | 1 |
| MMR Licensed Data status | 1 |
| MMR retention % | 1 |
| MMR retention rate (price-to-market) | 1 |
| MMR Wholesale Average (Manheim Market Report) | 1 |
| mobile.de Marktpreis (computed market price) | 1 |
| mobileAdId | 1 |
| Mobility Trends: encuesta de comportamiento del consumidor (intención renting, combustible preferido, presupuesto €, antigüedad, km anuales, prestaciones) | 1 |
| Mobility Trends: evolución anual del precio medio VO (%) | 1 |
| Mobility Trends: evolución mensual del precio medio VO (€) | 1 |
| Mod: aftermarket kit | 1 |
| Mod: catalytic converter | 1 |
| Mod: exhaust | 1 |
| Modèle | 1 |
| Modèle commercial | 1 |
| Mod: performance | 1 |
| Mod: spoiler | 1 |
| Mod: stereo | 1 |
| Mod: sunroof/moonroof | 1 |
| Mod: suspension lifted | 1 |
| Mod: suspension lowered | 1 |
| Mod: wheel | 1 |
| Modalita di pagamento | 1 |
| Mode prix: Prix total / Leasing (LOA) | 1 |
| modele (marque + nom commercial) | 1 |
| modelFleet | 1 |
| ModelGroup / 모델그룹 (+ EnglishName) | 1 |
| modelID (Chrome YMMID) | 1 |
| modelName | 1 |
| modelRange | 1 |
| modelYear | 1 |
| modelYearId | 1 |
| Modification identification | 1 |
| modificationDate | 1 |
| modo_de_pesquisa (entrada: 'Pesquisa por Marca' | 'Pesquisa por Código Fipe') | 1 |
| moeda_e_base (R$, pagamento à vista, consumidor final pessoa física, mercado nacional) | 1 |
| mogelijk_gevaar | 1 |
| MoM change (%) | 1 |
| Moneda (priceCurrency) | 1 |
| monetización CAE (≈1.000 €/turismo, vigente hasta 2030) | 1 |
| money factor | 1 |
| Monitoring Subscription layer: Monthly Vehicle History Report | 1 |
| Monitorización de cumplimiento de políticas | 1 |
| Monitorización de rendimiento de compradores (recon declarado vs IA) | 1 |
| Monster Bid | 1 |
| montagedatum (objeto incorporado) | 1 |
| Month-on-month change (£ and %) | 1 |
| month-over-month change | 1 |
| monthly_average_value_12mo_history | 1 |
| Monthly EV sales tracker | 1 |
| Monthly Offers | 1 |
| monthly_payment_estimate (Est. $/mo) | 1 |
| monthly payment view (by DMA) | 1 |
| monthly repayment / payment | 1 |
| Monthly sales units (per model) | 1 |
| Monthly static used car value | 1 |
| monthly value-change email alert | 1 |
| more_information_link (lead) | 1 |
| Most desirable | 1 |
| Most Recent Sale price | 1 |
| Motivo de baja (informe) | 1 |
| Motivo de la baja | 1 |
| Moto | 1 |
| Motorcycle / bike used value | 1 |
| Motorcycle Chassis Type | 1 |
| Motorcycle class fee | 1 |
| motorcycle coverage | 1 |
| Motorcycle Suspension Type | 1 |
| Motorisierung (motorizacion) | 1 |
| motorização (input tasador) | 1 |
| Motorización | 1 |
| Motorway Move transport status (from GBP 99) | 1 |
| Motorway Pay single-transfer payout (seller + finance provider + fees) | 1 |
| motTest.completedDate | 1 |
| motTest.expiryDate | 1 |
| motTest.motTestNumber | 1 |
| motTest.testResult | 1 |
| motTestDueDate (primer MOT, recien matriculados) | 1 |
| motTestNumber | 1 |
| motTests[] (array) | 1 |
| mpge | 1 |
| msa_code | 1 |
| ミッション MT/AT/CAT (transmission) | 1 |
| multi-angle interior/exterior images | 1 |
| Multi-out: retail potential | 1 |
| Multi-out: subprime potential | 1 |
| Multi-out: wholesale potential | 1 |
| multilingual query support | 1 |
| Multimarkenkonfigurator + Listenpreis (configurador VN multimarca + PVP) | 1 |
| Municipio de pago del IVTM | 1 |
| Municipio IVTM (domicilio fiscal) | 1 |
| Mutaciones diarias in/out de stock | 1 |
| MUVVI 20 market-class sub-indices | 1 |
| MUVVI adjusted wholesale price (mix/mileage/seasonal) | 1 |
| MUVVI ajuste de mix (media móvil 24 meses por market class) | 1 |
| MUVVI ajuste estacional (método Census Bureau / Census X) | 1 |
| MUVVI eliminación de outliers (2.6 desv. estándar en precio Y millas) | 1 |
| MUVVI EV index (Jan 2015=100) | 1 |
| MUVVI mid-month reading | 1 |
| MUVVI MoM % change | 1 |
| MUVVI MoM change | 1 |
| MUVVI Non-EV index | 1 |
| MUVVI precios no-ajustados YoY % | 1 |
| MUVVI unadjusted wholesale price | 1 |
| MUVVI YoY % change | 1 |
| MUVVI YoY change | 1 |
| MVM coverage (cars/LCV/bikes/HGV/imports) | 1 |
| MVM PDF report | 1 |
| Nº/código de operación de M.O. | 1 |
| Nº de biedingen (pujas) — tendencia mensual | 1 |
| Nº de reparaciones (nacional/provincial) | 1 |
| Nº de taxaties (tasaciones) — tendencia mensual | 1 |
| Nº de tipos de transacción disponibles (54) | 1 |
| número de airbags (airbags) | 1 |
| número de CAE (1 CAE = 1 kWh) | 1 |
| Número de Constancia de Inscripción (NCI, 8 alfanumérico, único) | 1 |
| número de ejes (axles) | 1 |
| número de fábricas (17 plantas) | 1 |
| Número de fotos por anuncio | 1 |
| Número de Identificación Vehicular (NIV/VIN, 17 caracteres) | 1 |
| Número de placa(s) / emplacamiento | 1 |
| Número de pujas (number of bids) | 1 |
| Número de serie (chasis) | 1 |
| Número de vehículos a la venta (oferta de mercado) | 1 |
| Número de visualizaciones (views, reporting al vendedor) | 1 |
| Nº Póliza | 1 |
| Nº Valoración | 1 |
| naam_bedrijf (empresa erkend) | 1 |
| Nachfrageindikatoren (demand indicators) | 1 |
| nags_number | 1 |
| NAMA: defectos visibles a 2m a 90 grados +/-45 | 1 |
| NAMA: dent count & size por panel | 1 |
| NAMA: exterior condition (cosmetico) | 1 |
| NAMA: interior condition | 1 |
| NAMA: paint defect count por panel/bumper | 1 |
| NAMA: significant interior defects | 1 |
| Name of individual/entity from whom automobile was obtained (solo law enforcement) | 1 |
| Name of individual/entity to whom title was issued (titleholder — solo law enforcement) | 1 |
| nameWoTrim | 1 |
| NatCode / Glass's code | 1 |
| nationaal_opgegeven_aantal_voertuigen_terugroepactie | 1 |
| National market code | 1 |
| National Paint Adjustment (AZT) | 1 |
| nationalDelivery (radius/period/fee) | 1 |
| natural_disaster_event_date | 1 |
| natural_disaster_exposure_flag | 1 |
| natural_disaster_severity | 1 |
| natural_disaster_type | 1 |
| natural-language query (Ask Dataforce chat) | 1 |
| [EQUIP·Multimedia] Navegador | 1 |
| Navigation aid | 1 |
| Navigation flag | 1 |
| Navigation operation | 1 |
| navigationSystem | 1 |
| ncap_adult_occupant_protection_percentage | 1 |
| ncap_child_occupant_protection_percentage | 1 |
| ncap_overall_rating | 1 |
| ncap_pedestrian_protection_percentage | 1 |
| ncap_safety_assist_percentage | 1 |
| NCSA Map Exc Approved By | 1 |
| NCSA Map Exc Approved On | 1 |
| NCSA Mapping Exception | 1 |
| NCSA Note | 1 |
| Índice: % depreciação / valorização (vista consumidor) | 1 |
| Índice: evolução do preço médio | 1 |
| Índice mercado: 구매 적기 (mejor momento de compra) | 1 |
| Índice mercado: EV 시세 방어 (resiliencia EV) | 1 |
| Índice mercado: 시세 변동 MoM % global | 1 |
| Índice mercado: 시세 변동 por origen (국산/수입) | 1 |
| Índice: recorte por Estado | 1 |
| Índice: recorte por quilometragem | 1 |
| Índice: variação % acumulada anual | 1 |
| Índice: variação % mensal | 1 |
| necesidades de mantenimiento | 1 |
| 续航 NEDC | 1 |
| NEDC figures (legacy) | 1 |
| Nederlandse handelsinkoopwaarde (requisito koerslijst BPM / derivable) | 1 |
| Negative equity indicator | 1 |
| Negative equity transactions (YoY) | 1 |
| Negative Score Factors | 1 |
| Énergie | 1 |
| Net Adjusted Market Value (settlement amount) | 1 |
| Net price / incl. all expenses (NP3) | 1 |
| Net returns | 1 |
| net_torque | 1 |
| netto_max_vermogen_elektrisch | 1 |
| nettomaximumvermogen (kW) | 1 |
| netTorque | 1 |
| netTorque.rpm | 1 |
| network_avg_monthly_searches_88M | 1 |
| network_avg_monthly_users_8_9M | 1 |
| network_avg_monthly_video_views_10M | 1 |
| network coverage | 1 |
| network coverage gaps | 1 |
| network financial health (OEM to dealer) | 1 |
| network health | 1 |
| network_members_count_15_2M_16M | 1 |
| network profitability | 1 |
| Network type (open / closed) | 1 |
| network_user_signals_3_7B | 1 |
| Neue Wettbewerber-Fahrzeuge (new competitor listings, live) | 1 |
| Neuf uniquement (filtre) | 1 |
| Neumáticos - condición (tires) | 1 |
| [MED·Prueba] Neumáticos de la unidad (medida y marca/modelo) | 1 |
| Neumáticos delanteros | 1 |
| Neumáticos traseros | 1 |
| new_car_calendar_release_dates | 1 |
| new_car_certified_preowned_info | 1 |
| new_car_compare_cars | 1 |
| new_car_expert_review_score_out_of_100 | 1 |
| New Car Fair Purchase Price | 1 |
| New car forecast (upside/baseline/downside 12m) | 1 |
| new_car_lifestyle_category | 1 |
| New car price | 1 |
| new_car_rrp_pricing | 1 |
| New car value / new car data | 1 |
| new_used_pricing (OEM) | 1 |
| New Vehicle Module (alta de flotas) | 1 |
| New vehicle price (formato New) | 1 |
| New Vehicle Price Now (precio on-road actual del modelo nuevo) | 1 |
| New Vehicle Price Then (precio on-road original del ano de compra) | 1 |
| new vehicle sale flag (96% US coverage) | 1 |
| New Vehicle Value (Low / Average / High, weekly) | 1 |
| New Vehicle Value - Average | 1 |
| New Vehicle Value - High | 1 |
| New Vehicle Value - Low | 1 |
| new+used transaction signal | 1 |
| newly_listed | 1 |
| NextGear stock funding (100% of cost at checkout) | 1 |
| NHTSA 5-Star overall safety rating | 1 |
| NHTSA 5-star safety rating | 1 |
| nhtsa_overall_rating | 1 |
| NHTSA rating by impact type | 1 |
| NHTSA record | 1 |
| nhtsa_safety_rating | 1 |
| NICB (National Insurance Crime Bureau) record | 1 |
| Nieuwprijs (= Catalogusprijs + Optiebedrag) | 1 |
| Nieuwwaarde (seguro) | 1 |
| NIVE (número ITV) | 1 |
| Niveau d'équipement | 1 |
| niveau_sonore_dBA (U.1) | 1 |
| Nivel de competitividad de precios | 1 |
| Nivel de daño pintura metálica (LE/LS/L/LI/LI1) | 1 |
| Nivel de daño pintura plástico (LE1/LE/L/LI/LI1) | 1 |
| NMR Check (compare vs DB) | 1 |
| NMR Investigation (clocking detection) | 1 |
| NMR reading date | 1 |
| NMR reading source (recorded by) | 1 |
| NMR sources (DVLA, V5, MOT/VOSA, auctions, insurance claims, leasing) | 1 |
| NMVTIS current title state | 1 |
| NMVTIS junk records | 1 |
| NMVTIS previous titles by jurisdiction | 1 |
| NMVTIS title data | 1 |
| NMVTIS title issue date | 1 |
| No. of Airbags | 1 |
| No. of Cylinders | 1 |
| No. of Speakers | 1 |
| nom_commercial (D.3) | 1 |
| Nombre de cylindres | 1 |
| Nombre de empresa (flota) | 1 |
| Nombre de municipio (MUNICIPIO) | 1 |
| Nombre de places | 1 |
| Nombre de portes | 1 |
| nombre_de_procedures_VE (sinistres a reparation controlee) | 1 |
| Nombre de rapports | 1 |
| Nombre de soupapes par cylindre | 1 |
| nombre_de_titulaires | 1 |
| Nombre del taller | 1 |
| nominaal_continu_maximumvermogen (electrico) | 1 |
| Non-EV Index + YoY % | 1 |
| Non-Land Use | 1 |
| Non-runner flag | 1 |
| non-US prefix coverage | 1 |
| Norma anticontaminación (Euro) | 1 |
| normal/standard service schedule | 1 |
| normalized equipment description | 1 |
| Normativa | 1 |
| Norme Euro | 1 |
| NotaCarrozzeria | 1 |
| NotaMeccanica | 1 |
| Note | 1 |
| Note du vendeur + avis | 1 |
| NoteAnnuncio | 1 |
| NoVA rate (AT) | 1 |
| novedad del registro (novelty) | 1 |
| NPS (Guaranteed) | 1 |
| Nube/scatter de distribución de precios | 1 |
| NucleoMotore | 1 |
| num_cylinders | 1 |
| num_doors | 1 |
| num_gears | 1 |
| num_seats | 1 |
| number_axles | 1 |
| number of /pojazdy method calls (ilosc-wyszukan) [Statystyki] | 1 |
| Number of adverts / advert volume | 1 |
| Number of auction runs | 1 |
| Number of Auctions Included | 1 |
| number of axles (liczba-osi) | 1 |
| Number of bids | 1 |
| number_of_bids_per_lot_iaai | 1 |
| Number of bolts | 1 |
| Number of chargers (turbo) | 1 |
| Number of cylinders | 1 |
| number_of_motors | 1 |
| number of photographs / too few pictures (flag) | 1 |
| Number of previous keepers | 1 |
| number_of_reviews | 1 |
| Number of Seat Rows | 1 |
| number_of_speeds | 1 |
| Number of strokes | 1 |
| Number of tyres | 1 |
| number_of_units_affected | 1 |
| number of vehicles registered in selected period | 1 |
| Number of Wheels | 1 |
| number_previous_keepers | 1 |
| numberOfPreviousKeepers [NV bulk] | 1 |
| numberOfPreviousOwners | 1 |
| numero_cambi_prezzo | 1 |
| numero_CNIT (D.2.1) | 1 |
| Numero de cilindros (cylinders/cylinderCapacity) | 1 |
| Numero de key fobs | 1 |
| Numero de llaves | 1 |
| Numero de marchas (gear/gears) | 1 |
| numero de plazas/seats (座位数) | 1 |
| numero_de_reception (K) | 1 |
| Numero di passaggi di proprieta (incl. minivolture) | 1 |
| Numero_veicoli | 1 |
| NumeroCilindri | 1 |
| NumeroElementiBatterie | 1 |
| NumeroLicenze | 1 |
| NumeroMarce | 1 |
| NumeroPassaggi | 1 |
| NumeroPorte | 1 |
| NumeroPosti | 1 |
| NumeroPostiAggiuntivi | 1 |
| NumeroPostiSottraibili | 1 |
| numOfDoors | 1 |
| NUTS3 level | 1 |
| NVD change dates (model year/price/options/equipment/tech) | 1 |
| OBD / OBDII diagnostic scan | 1 |
| obd_cause | 1 |
| obd_code | 1 |
| obd_definition | 1 |
| OBD diagnostic result (Assured/128) | 1 |
| OBD-II diagnostic deduction (coste de reparacion por fallo) | 1 |
| OBD-II trouble codes escaneados (109.000) / mapeados (11.000) | 1 |
| objetivo de electromovilidad por CCAA | 1 |
| observación (observation) | 1 |
| Observatoire: prix moyen/médian VO (€) | 1 |
| Observatoire: évolution des prix (% trimestre/an) | 1 |
| Observatoire: évolution par âge | 1 |
| Observatoire: évolution par motorisation | 1 |
| OC validity reminder (przypomnienie OC) [Moj Pojazd] | 1 |
| 车辆登记证书 OCR (registration certificate fields) | 1 |
| 车辆合格证 OCR 12字段: 合格证编号/车架号/排放标准/发动机编号 (conformity cert 12 fields) | 1 |
| 行驶证 OCR 21字段 (vehicle license 21 fields) | 1 |
| 驾驶证 OCR 9字段 (driver license 9 fields) | 1 |
| ocr_confidence | 1 |
| ocr_detected_plate_text | 1 |
| Odor | 1 |
| OEM build data (todos los OEM principales) | 1 |
| OEM build data validation (ChromeData) | 1 |
| OEM connection (ej. GM D2C2) | 1 |
| OEM customers per plant | 1 |
| oem_incentive_program | 1 |
| OEM marketing equipment description | 1 |
| oem_numbers | 1 |
| OEM pack content & configuration (VINView Pro) | 1 |
| OEM product plans | 1 |
| OEM rebates | 1 |
| OEM Recommended Maintenance Schedule (by mileage interval) | 1 |
| OEM Repair Methods/procedures | 1 |
| OEM service schedule (time-based interval) | 1 |
| OEM warning codes | 1 |
| OEM window sticker / Monroney (35M+, 16 marcas) | 1 |
| OEM window stickers (QR-enabled, synced) | 1 |
| OEM-Certified build data (Toyota/Lexus/Scion/Honda/Acura) | 1 |
| OEM-Linked Competitive Sets (like-mine vehicles) | 1 |
| oemCode | 1 |
| offer_price_offer_of_one | 1 |
| Offer status (draft/completed/processed) | 1 |
| offer targeting (model / individual vehicle / inventory age / geography / lead source) | 1 |
| offer trigger (page view / site reentry / KPI completion) | 1 |
| offer validity (7 dias / +250 millas) | 1 |
| OfficeCityState / 지역 (región del anuncio) | 1 |
| Offsite (badge) | 1 |
| Offsite address | 1 |
| Oil warning light | 1 |
| Oil/coolant contamination | 1 |
| Olor (odour) | 1 |
| omschrijving_defect | 1 |
| On-board charger standard indicator | 1 |
| On-board voltage (V) | 1 |
| on-site appraisal (real-life condition check at collection) | 1 |
| oneLineText (descripción de una línea) | 1 |
| online business plan | 1 |
| opcionais / itens opcionais (extras) | 1 |
| Opciones value-impacting vacs[] (add/deduct A/D, selected, mutex, disabled) | 1 |
| Open Repair Order (RO) alert | 1 |
| OPENLANE Inspect (EU): categorias de daño (mirrors, roof arcades) | 1 |
| OPENLANE Inspect (EU): descripcion de daños tecnicos | 1 |
| OPENLANE Inspect (EU): fotos offline de daño exterior/interior | 1 |
| OPENLANE Inspect (EU): identificacion de vehiculo + datos basicos -> OPENLANE Sell portal | 1 |
| openstaande_terugroepactie_indicator (recall abierto) | 1 |
| Operación E (sustituir) | 1 |
| Operación ET (sustitución parcial) | 1 |
| Operación H (tratamiento anticorrosivo) | 1 |
| Operación I (reparar, marcado con *) | 1 |
| Operación IT (tiempo de reparación parcial) | 1 |
| Operación N (desmontar/montar) | 1 |
| Operación P (comprobar) | 1 |
| Operación R (daños ocultos, posición 1000) | 1 |
| Operación S (conceptos varios, posición 1000) | 1 |
| Operación U (tratamiento de bajos) | 1 |
| Operación V (verificar/alinear/marcar) | 1 |
| operaciones de reparación | 1 |
| operador / sujeto obligado / entidad delegada | 1 |
| operating_lease | 1 |
| operatingHours | 1 |
| Operation/task type (Replace/Repair/Remove&refit/Paint/Anti-corrosion/Verify/Adjust/Strip-refit/Polish) | 1 |
| opgegeven_maximum_snelheid | 1 |
| oplegger_geremd | 1 |
| opmerkingen_rdw | 1 |
| opposition_OTCI_date (transfert certificat immatriculation) | 1 |
| opposition_OTCI_PV_date (amendes / proces-verbal) | 1 |
| opposition_OVE_date (vehicule endommage) | 1 |
| opposition_OVEI_date | 1 |
| Optiebedrag (importe opciones de fábrica) | 1 |
| Opties / Optiebedrag (autorrelleno por kenteken o selección manual) | 1 |
| optimal_buy_timing | 1 |
| optimal_sell_timing | 1 |
| optimización de costes (uso / mantenimiento / devolución) | 1 |
| Optimización E por I (diferencia % y € sustituir vs reparar) | 1 |
| Optimizacion de stock | 1 |
| [EQUIP·Seguridad] Ordenador de viaje | 1 |
| Order codes (OEM) | 1 |
| OreManoOpera | 1 |
| ORG document id | 1 |
| Original Equipment Guide (OEG) | 1 |
| Original in-service date | 1 |
| Originality (Original / Highly Original / Modified / Custom / Project) | 1 |
| originally right-hand drive (kierownica-po-prawej-stronie-pierwotnie) | 1 |
| Origination history adjustment (AVT) | 1 |
| originPrice / 신차가 (precio nuevo / MSRP) | 1 |
| ORVM Turn Indicators | 1 |
| other | 1 |
| Other Bus Info | 1 |
| Other factory extras/equipment (מפרט/אבזור) | 1 |
| Other issues (+ other_issues_repair_cost) | 1 |
| Other Motorcycle Info | 1 |
| Other Restraint System Info | 1 |
| Other Trailer Info | 1 |
| Other vehicle history report events (HAV input) | 1 |
| Other warning lights | 1 |
| OTR price | 1 |
| Out of Pocket Expenses (sum) | 1 |
| Outbound private-party leads (Facebook/Craigslist/Autotrader/Cars.com) | 1 |
| Outlier flag/asterisco (excluye ventas canadienses previas y vehículos <50 millas) | 1 |
| Outside Rear View Mirror (ORVM) | 1 |
| Over Speeding Alert | 1 |
| Over the Air (OTA) Updates | 1 |
| Over-average / Overdriven alert | 1 |
| overall condition (detailed) | 1 |
| Overall quality score (e.g. 7.9) | 1 |
| Overall rating (e.g. Excellent Buy) | 1 |
| Overall Vehicle Condition rating | 1 |
| overlay de datos de reventa reales sobre la curva | 1 |
| overlay.all_images | 1 |
| overlay.avg_kms | 1 |
| overlay.avg_odo | 1 |
| overlay.avg_price | 1 |
| overlay.contact_name | 1 |
| overlay.contact_number | 1 |
| overlay.cover_image_url (90 días) | 1 |
| overlay.drive_away_price | 1 |
| overlay.listing.price | 1 |
| overlay.listing.source | 1 |
| overlay.listing.url | 1 |
| overlay.price_before_govt_charges | 1 |
| overlay.price_drop_count | 1 |
| overlay.price_includes_govt_charges | 1 |
| overlay.price_when_new (RRP) | 1 |
| overlay.primary_description | 1 |
| overlay.rego | 1 |
| overlay.starting_price | 1 |
| overlay.stock_no | 1 |
| overlay.tag_ids (trash/damaged/writeoff) | 1 |
| Overstock reduction | 1 |
| Overturned/Rollover | 1 |
| overview marketing photo | 1 |
| Owed amount (saldo del prestamo) | 1 |
| own repair workshop indicator | 1 |
| Owned From (per owner) | 1 |
| Pérdidas | 1 |
| P11D / BIK percentages (3 tax years) | 1 |
| P11D value | 1 |
| país (country) | 1 |
| País de origen | 1 |
| pack pricing | 1 |
| pack.name | 1 |
| pack.price-excluding-vat | 1 |
| pack.price-including-vat | 1 |
| Pacote (option package) | 1 |
| Paese di origine estero | 1 |
| Pago de tenencias y contribuciones | 1 |
| Pago por transferencia bancaria | 1 |
| Paint defects | 1 |
| Paint material cost (AZT-sourced) | 1 |
| Paint Material Index (%) | 1 |
| Paint Meter Readings (repintado/chapa) | 1 |
| Paint operation/time | 1 |
| Paint system (Manufacturer/AZT/Cevismap/Centro Zaragoza/Manual/Without Paint) | 1 |
| pais de destino de envio (50-70+ paises) | 1 |
| Pan-EU RV benchmark (vía DAT/L'Argus/Quattroruote) | 1 |
| [EQUIP·Multimedia] Pantalla táctil orientable de 39,6 cm (15,6") | 1 |
| Par máximo (Nm) | 1 |
| paramrijweerstand_f0 (resistencia rodadura) | 1 |
| paramrijweerstand_f1 | 1 |
| paramrijweerstand_f2 | 1 |
| [EQUIP·Confort] Parasoles con espejos de cortesía iluminados | 1 |
| Parking Assist | 1 |
| Parking cost (₹) | 1 |
| Parking Sensors | 1 |
| parkingAssistants | 1 |
| Part code (TecDoc compatible) | 1 |
| Part description (descripcion de pieza) | 1 |
| part_drawing_scheme | 1 |
| Part identification (replaced OE numbers) | 1 |
| Part multi-reference | 1 |
| part_name | 1 |
| Part supersession (nuevo nº de pieza) | 1 |
| Part-exchange underwrite (Consumer Pro +) | 1 |
| Part-exchange valuation (retailer) | 1 |
| partial_plate_identification | 1 |
| partner_preferred_pricing | 1 |
| partner_targeted_incentives | 1 |
| partnership (dealer / centro de diagnóstico) | 1 |
| Parts availability (near real-time) | 1 |
| Parts history (subrogation audit) | 1 |
| Parts Platform Filter (%) | 1 |
| Parts price (near real-time) | 1 |
| Parts Query (nº OEM -> vehiculos/operaciones) | 1 |
| Parts recommendation (sourcing rules) | 1 |
| Parts Suppliers | 1 |
| passDoors | 1 |
| Passenger Airbag | 1 |
| passenger cars in operation | 1 |
| passenger_volume | 1 |
| passenger_volume_third_row | 1 |
| PassoMetri | 1 |
| Past / historical values | 1 |
| patents database (filterable) | 1 |
| pay GBP 1 above next bidder (once reserve hit) | 1 |
| payload_capacity | 1 |
| payload_volume_square_metres | 1 |
| Payment Calculator input: APR / interest rate | 1 |
| Payment Calculator input: credit score band | 1 |
| Payment Calculator input: down payment | 1 |
| Payment Calculator input: loan term | 1 |
| Payment Calculator: monthly payment | 1 |
| PDF report (idioma/tipo configurable) | 1 |
| Peak sale value | 1 |
| Pearlescent Uplift (%) | 1 |
| penalty points (punkty karne) [Moj Pojazd / Sprawdz punkty karne] | 1 |
| Pence-per-mile (PPM) / PCH valuation | 1 |
| Período de baja | 1 |
| Período de la baja | 1 |
| Per-category record counts (summary badges) | 1 |
| Per-lot IBB price analytics | 1 |
| per-site vs anonymised-competitor performance breakdown | 1 |
| percent change (vs prior period) | 1 |
| percent_similar_cars_priced_higher | 1 |
| Percorrenza | 1 |
| PercorrenzaPrevista | 1 |
| PerfectFit best-fit ranking | 1 |
| PerfectFit proprietary vehicle/equipment score | 1 |
| Perfil completo del vehiculo / full vehicle history (specs) | 1 |
| Perfil de comprador VO | 1 |
| Perfil de la gama de producto | 1 |
| Perfil mecánico / condición mecánica | 1 |
| performance_features | 1 |
| Performance optimization (turn & gross trends) | 1 |
| performance.da-0-1000m | 1 |
| performance.da-0-100kph (0-100 km/h) | 1 |
| performance.maximum-speed (V-max) | 1 |
| Period type (daily/monthly/yearly) | 1 |
| period.end-date | 1 |
| period.end-date-type | 1 |
| period.price-excluding-vat (prix HT) | 1 |
| period.price-including-vat (prix TTC) | 1 |
| period.start-date | 1 |
| period.start-date-type | 1 |
| Periodo | 1 |
| PeriodoFineQuotazione | 1 |
| PeriodoImmatricolazione | 1 |
| PeriodoInizioQuotazione | 1 |
| PeriodoProduzione | 1 |
| Periodos de reprise (trade-in periods) | 1 |
| permissible axle load (dopuszczalny-nacisk-osi) | 1 |
| permissible GVW of vehicle combination (dopuszczalna-masa-calkowita-zespolu-pojazdow) | 1 |
| permissible payload (dopuszczalna-ladownosc) | 1 |
| personal behaviors | 1 |
| personal_use_badge | 1 |
| Personalized Predictions (dealer-performance model) | 1 |
| pesos del vehículo | 1 |
| Pesos del vehiculo | 1 |
| Pet-free / smoke-free status | 1 |
| phase.full-nicename | 1 |
| phase.name | 1 |
| phase.position | 1 |
| phase.short-nicename | 1 |
| phone | 1 |
| photo | 1 |
| Photo availability indicator | 1 |
| Photo carousel | 1 |
| Photo categories (Exterior / Interior / Mechanical / Documents) | 1 |
| photo gallery | 1 |
| photo_links | 1 |
| photo_links_cached | 1 |
| Photo management (branded overlays, why-buy placeholders, intelligent photo tags) | 1 |
| Photo overlays de features/promociones | 1 |
| Photo principal | 1 |
| Photo upload (outline-match exterior/interior) | 1 |
| photo_url | 1 |
| photo.match_confidence (high/medium/low) | 1 |
| photo.type (stock/generated) | 1 |
| photo.url | 1 |
| Photos / Photo Gallery | 1 |
| Photos / Vidéo (galerie) | 1 |
| photos_availability | 1 |
| photos_count | 1 |
| photos_date | 1 |
| Photos[] gallery (type, location, updatedDate, ordering) | 1 |
| photos_interior_exterior | 1 |
| PianoManutenzione | 1 |
| Picotazos/defectos de cristal (mm) | 1 |
| Piezas de mantenimiento | 1 |
| Pilot Match: overlay concurrence | 1 |
| Pilot Match: overlay prix (sur sites externes/subastas/DMS) | 1 |
| Pilot Price: annonces concurrentes similaires (nº) | 1 |
| Pilot Price: décryptage marché (graphique évolution/distribution) | 1 |
| Pilot Price: marge | 1 |
| Pilot Price: modifications de prix | 1 |
| Pilot Price: nouvelles annonces publiées | 1 |
| Pilot Price: prix conseillé d'achat | 1 |
| Pilot Price: prix conseillé de vente | 1 |
| Pilot Price: recommandation IA en langage naturel (historique + demande locale) | 1 |
| Pilot Price: rotation estimée (days-to-sell) | 1 |
| Pilot Price: tension du marché | 1 |
| Pilot Price: véhicules vendus | 1 |
| Pilot Trends: tendances du marché | 1 |
| Pilot Trends: évolution des ventes par modèle commercial | 1 |
| [EQUIP·Decoración] Pintura (color) | 1 |
| [EQUIP·Decoración] Pintura metalizada | 1 |
| plaats_chassisnummer (ubicacion VIN) | 1 |
| plaatscode_as (voor/achter) | 1 |
| placa (plate; consulta placa→código) | 1 |
| places_assises (S.1) | 1 |
| places_debout (S.2) | 1 |
| plant | 1 |
| plant capacity | 1 |
| plant code | 1 |
| Plant Company Name | 1 |
| Plant Country | 1 |
| Plant State | 1 |
| Plant Status | 1 |
| plant utilization | 1 |
| Planta de producción | 1 |
| Plate change date | 1 |
| plate_change_list | 1 |
| Plate sequence number (10 plates) | 1 |
| platform_desc | 1 |
| platform.brakes (front/rear/parking/regenerative) | 1 |
| platform.chassis-material | 1 |
| platform.chassis-type | 1 |
| platform.euroncap-ratings | 1 |
| platform.front-suspension-type | 1 |
| platform.lcv-cab-type | 1 |
| platform.rear-suspension-type | 1 |
| platform.steering-wheel-lock-to-lock-turns | 1 |
| platform.turning-circle-between-kerbs | 1 |
| platform.turning-circle-wall-to-wall | 1 |
| Plazo de funding (hasta 150 dias) | 1 |
| Plug-in hibrido si/no (isPluginHybrid) | 1 |
| PM2.5过滤 | 1 |
| PneumaticiMontabili | 1 |
| Pneumatico | 1 |
| Poached Data (serviced vehicle appears on competitor lot) | 1 |
| POI Einschlagpunkt (punto de impacto, daño viejo vs nuevo) | 1 |
| Poids à vide | 1 |
| Point-in-time value (current or historical date) | 1 |
| Points forts (badges détectés par IA) | 1 |
| police_databases_checked_countries | 1 |
| Policy number | 1 |
| Pollution norm history | 1 |
| pooling credits & fine calculation | 1 |
| Poor Previous Paintwork (PPR) flag | 1 |
| popular_cars_rank | 1 |
| Popular Mention: Comfort | 1 |
| Popular Mention: Interior | 1 |
| Popular Mention: Looks | 1 |
| Popular Mention: Price | 1 |
| Popular Mention: Space | 1 |
| Porcentaje (código opcional) | 1 |
| [EQUIP·Confort] Portón trasero eléctrico | 1 |
| portas | 1 |
| PortataKgA | 1 |
| PortataKgDa | 1 |
| Portfolio valuation / risk | 1 |
| Posición del volante | 1 |
| Posicion de su vehiculo en el mercado | 1 |
| Positive Score Factors | 1 |
| Positive/negative equity flag | 1 |
| Possible Values | 1 |
| post_date | 1 |
| Potencia auxiliar (auxiliaryPower) | 1 |
| Potencia fiscal (CVF) | 1 |
| Potencia fiscal en CVF (POTENCIA_ITV) | 1 |
| Potencia máxima (CV / kW) | 1 |
| Potencia neta máxima (kW) | 1 |
| Potencial de facturación (provincia/código postal) | 1 |
| Potencial de postventa | 1 |
| Potencial de reparaciones (provincia/código postal) | 1 |
| potential / net transaction price | 1 |
| Potenza di ricarica (EV) | 1 |
| PotenzaCV | 1 |
| PotenzaFiscale | 1 |
| PotenzaKW | 1 |
| PotenzaMaxGiriMinuto | 1 |
| PotenzaPiccoCV | 1 |
| PotenzaPiccoKW | 1 |
| PotenzaRicaricakW | 1 |
| PotenzaRicaricaRapida | 1 |
| powerAssistedSteering | 1 |
| powerRPM | 1 |
| powerUnit | 1 |
| PPSR processing status | 1 |
| PPSR reference id | 1 |
| PPSR report (certificate URLs) | 1 |
| ppsr.has_changed | 1 |
| ppsr.has_expired | 1 |
| pre_bid | 1 |
| preço anunciado (asking price) | 1 |
| Preço por versão diferenciado (S / SE / SE Plus) | 1 |
| preço Tabela FIPE (referencia mostrada en la ficha) | 1 |
| Preço usado / seminovo (por tiempo de uso) | 1 |
| Pre-launch / opinion forecast | 1 |
| Precio de competidores (actualizado a diario) | 1 |
| Precio de reprise online garantizado | 1 |
| Precio de reserva (reserve price) | 1 |
| Precio del anuncio (€) | 1 |
| Precio en condicion Excellent | 1 |
| Precio en condicion Fair | 1 |
| Precio en condicion Good | 1 |
| Precio en condicion Very Good | 1 |
| Precio estimado de cierre / 'que precio voy a obtener' (output tasador) | 1 |
| precio FOB en USD (export) | 1 |
| Precio Instant Purchase / direct buy (compra inmediata) | 1 |
| Precio mínimo de venta / reserva (reserve price) | 1 |
| Precio medio de venta mayorista mensual (mean sales price por categoría) | 1 |
| precio medio del VO (€) | 1 |
| precio medio del VO hasta 10 años (€) | 1 |
| precio medio ponderado por motorización (ref. 3 años) | 1 |
| precio medio por motorización (gasolina/diésel/HEV/PHEV/BEV) | 1 |
| precio medio por tramo de antigüedad (0-1/2-5/6-10/11-15/15-20 años) | 1 |
| Precio medio VO (global / por antigüedad / por motorización) | 1 |
| Precio medio/estimado de mercado (valor medio de unidades similares) | 1 |
| Precio rebajado por profesional (traderReducedPrice) | 1 |
| Precio recomendado de venta (output tasador) | 1 |
| Precio retail base | 1 |
| Precio sin IVA / IVA deducible (netPrice/isVatLabelLegallyRequired) | 1 |
| Precio y referencia de lunas/cristales (AudaGlass) | 1 |
| Precios de transacciones reales (portales de venta online) | 1 |
| Precios de venta en tiempo real (live retail) | 1 |
| Precios EV | 1 |
| Precios reales de transacción (distribuidores/financieras) | 1 |
| Precision de valoracion (hasta 99%) | 1 |
| [EQUIP·Confort] Preclimatización del habitáculo | 1 |
| Predecessor-successor RV link | 1 |
| preDelivery | 1 |
| Prediccion de rendimiento del vehiculo (area local) | 1 |
| Prediccion de reparacion anual | 1 |
| Predicted accuracy (dentro de $100 del precio final) | 1 |
| Predicted likelihood vehicle on road in 5 years | 1 |
| Predicted outcome / action-based forecast | 1 |
| Predicted outcomes (action-based forecasts) | 1 |
| predicted purchase next 0-3 months / 90 days | 1 |
| Predictive Average Days to Sale | 1 |
| Predictive maintenance scheduling | 1 |
| predictive signal: company filings | 1 |
| predictive signal: deals (M&A / PE / VC) | 1 |
| predictive signal: jobs / hiring | 1 |
| predictive signal: news | 1 |
| predictive signal: patents | 1 |
| predictive signal: social media sentiment | 1 |
| Predictive vehicle value (per rooftop) | 1 |
| Preferred contact method (email/phone/text) | 1 |
| Preisänderung MoM/YoY % (price change) | 1 |
| Preisänderungen Wettbewerber (competitor price changes) | 1 |
| Preisbarometer average used price | 1 |
| Preisbarometer listing stock (Bestand) + YoY change | 1 |
| Preisbewertung-Label: Erhöhter Preis | 1 |
| Preisbewertung-Label: Fairer Preis | 1 |
| Preisbewertung-Label: Guter Preis | 1 |
| Preisbewertung-Label: Hoher Preis | 1 |
| Preisbewertung-Label: Sehr guter Preis | 1 |
| Preisdifferenz vs Markt (difference vs market price) | 1 |
| Preisempfehlung (precio recomendado para anunciar) | 1 |
| Preisentwicklung Wettbewerber (competitor price trend) | 1 |
| Preisspanne / Verhandlungsspielraum (price range + negotiation margin) | 1 |
| Preisspanne im Markt (market price range) | 1 |
| Preliminary ProQuote (valor predictivo salvamento) | 1 |
| Premium Imagery Sets (up to 75 photos) | 1 |
| premium service schedule | 1 |
| Premium Studio Still (front 3/4) | 1 |
| Preselection of the cheapest part | 1 |
| PresenzaDatiWltp | 1 |
| presupuesto detallado de reparación (estimado) | 1 |
| Pretensioner | 1 |
| Prevar.comparaison-3-vehicules | 1 |
| Prevar.historique-indices-decote | 1 |
| Prevar.indice-de-decote | 1 |
| Prevar.matrice-globale (durée×km) | 1 |
| Prevar.matrice-personnalisée | 1 |
| Prevar.profils (perfiles paramétricos) | 1 |
| Prevar.tarif-ttc | 1 |
| Prevar.vehicules-equivalents | 1 |
| preVerified | 1 |
| previous purchase | 1 |
| previous_title_status | 1 |
| Previous/last state of title | 1 |
| previousOwners (count) | 1 |
| previsión de margen comercial | 1 |
| previsión por horizonte (corto/medio plazo) | 1 |
| previsión variación % | 1 |
| Prevision de VR a 3 anos / hasta 120 meses (10 anos) | 1 |
| Prevision mercado VO turismos (ForCar VO) | 1 |
| Prevision VR al inicio de contrato (posicion de riesgo) | 1 |
| PrezziIvati | 1 |
| Prezzo | 1 |
| Prezzo di listino (nuovo) | 1 |
| Prezzo di listino del nuovo per il lead | 1 |
| Prezzo di listino iniziale + andamento svalutazione | 1 |
| Prezzo di vendita online Consigliato (StreetPrice) | 1 |
| Prezzo di vendita online Massimo (StreetPrice) | 1 |
| Prezzo di vendita online Minimo (StreetPrice) | 1 |
| prezzo_listino | 1 |
| prezzo_ritiro | 1 |
| PrezzoChiaviInMano | 1 |
| PrezzoListino | 1 |
| PrezzoMassimoAcquisto | 1 |
| PrezzoMercato | 1 |
| PrezzoMercatoPerc | 1 |
| PrezzoPreventivato | 1 |
| PrezzoVenditaPreventivato | 1 |
| Price below market / favorable pricing highlight | 1 |
| Price bracket (sub-£10k / over £10k / £25k cap) | 1 |
| Price category / VAT status (margin vs VAT-qualifying) | 1 |
| price_change_percent | 1 |
| Price Checker rating | 1 |
| price_development | 1 |
| Price development / tendencia de evolución de precio | 1 |
| price_drop_amount | 1 |
| price_drop_notification | 1 |
| price_drop_notification / price_alarm | 1 |
| price_drop_notifications | 1 |
| Price Evaluation: Abaixo da média (etiqueta) | 1 |
| Price Evaluation: Acima da média (etiqueta) | 1 |
| Price Evaluation: Dentro da média (etiqueta) [V live] | 1 |
| price_graph_transaction_distribution | 1 |
| Price Indicator: Fair price | 1 |
| Price Indicator: Good price | 1 |
| Price Indicator: Great price | 1 |
| Price Indicator: Higher price | 1 |
| Price Indicator label (Great/Good/Fair/Higher/Lower + £ variance) | 1 |
| Price Indicator: Lower price | 1 |
| Price Indicator: No Analysis (no label) flag | 1 |
| Price indicator rating band lower (GBP) | 1 |
| Price indicator rating band upper (GBP) | 1 |
| price inflation metric | 1 |
| Price movements | 1 |
| price_new / nieuwprijs (precio nuevo) | 1 |
| price not changed recently (flag) | 1 |
| price_predictor_retail | 1 |
| Price provisional flag | 1 |
| Price Radar: días en campaña / antigüedad de publicación | 1 |
| Price Radar: desviación respecto al precio medio de mercado (price-to-market %) | 1 |
| Price Radar: detección de activos tóxicos (stock estancado) | 1 |
| Price rank | 1 |
| price type | 1 |
| price vs IMV (%) | 1 |
| Price when new (at-new value) | 1 |
| priceassist_average_time_to_sell_days | 1 |
| priceassist_price_comparison_vs_similar | 1 |
| priceassist_recommended_price_for_target_time | 1 |
| priceassist_similar_cars_for_sale_now_count | 1 |
| priceassist_similar_cars_sold_12m_count | 1 |
| priceCommentary | 1 |
| priceDifferential / Savings (asking price vs IMV) | 1 |
| priceIndicatorRating (advert) | 1 |
| priceRange.high | 1 |
| priceRange.low | 1 |
| priceRating / AutoScore (Super price | Good price | Fair price | A bit pricey | Expensive) | 1 |
| priceRating label (VERY_GOOD_PRICE) | 1 |
| priceRating labelRange.from (EUR per tier) | 1 |
| priceRating labelRange.to (EUR per tier) | 1 |
| priceRating NO_RATING + reason codes (11) | 1 |
| prices.amount | 1 |
| prices.amountExVat | 1 |
| prices.currency / currencySymbol / countrycode | 1 |
| prices.priceType | 1 |
| prices.taxIncluded | 1 |
| prices.vatPercentage | 1 |
| priceValue (numeric) | 1 |
| PriceVantage: 10B+ monthly shopper intent signals | 1 |
| PriceVantage: IMS syndication (price push to Inventory Management System) | 1 |
| PriceVantage: IMV lookup | 1 |
| PriceVantage: lead-potential forecast (impact of price change before applying) | 1 |
| PriceVantage price recommendation (turn-time-based) | 1 |
| PriceVantage: turn time goal | 1 |
| Pricing alignment / adherence a la recomendacion | 1 |
| Pricing Comparison | 1 |
| pricing_intelligence | 1 |
| Pricing score | 1 |
| Pricing shifts | 1 |
| pricing strategy (avg price-to-market by age band) | 1 |
| Pricing Tool: increase-price-without-dropping-deal-rating opportunities | 1 |
| Pricing Tool: 'mark as sold' action (24h feed sync) | 1 |
| pricing_trends | 1 |
| PrimaImmatricolazioneEstera | 1 |
| primary_compression_ratio | 1 |
| primary_drive_rear_wheel | 1 |
| Primary point of impact (First Look AI) | 1 |
| primo_prezzo | 1 |
| Print Value Report | 1 |
| Prior-repair / Special Adjustment (e.g. rebuilt transmission) | 1 |
| priorización de tecnología de conectividad (encuesta a fabricantes) | 1 |
| private offer delivery (text / email / website overlay / API) | 1 |
| Private valuation (retailer) | 1 |
| Privati_custom | 1 |
| Privati_generica_autoscout24_medium | 1 |
| Privati_generica_subito_medium | 1 |
| Privati_hard | 1 |
| Privati_medium | 1 |
| Privati_soft | 1 |
| Privatverkaufswert [NO-VERIFICADO] | 1 |
| Privatverkaufswert / Marktwert (valor de venta privada / mercado) | 1 |
| Prix (€) | 1 |
| Prix du Neuf (initial-prices) | 1 |
| Prix neuf (€) | 1 |
| PRO: gestión de stock multi-tipología | 1 |
| PRO: iTasador (tasador integrado para aprovisionamiento) | 1 |
| PRO: multipublicación (coches.net + Milanuncios + web propia + >40 portales) | 1 |
| PRO: posicionamiento/subidas de stock (cada 3/6 días/mensual) | 1 |
| PRO: tracking telefónico (origen, atendidas/no atendidas, perdidas, estadísticas) | 1 |
| PRO: vídeos en anuncio / vídeos corporativos | 1 |
| procedure_VE_en_cours_PVE | 1 |
| Procurement channel mix (exchange %) | 1 |
| producción de comerciales+industriales (unidades) | 1 |
| producción de turismos (unidades) | 1 |
| producción de vehículos alternativos/electrificados (unidades) | 1 |
| producción mensual / acumulado / variación % | 1 |
| Product competitiveness | 1 |
| product_eenheid | 1 |
| Product image / photo | 1 |
| product launch timing / pipeline | 1 |
| product leakage to non-branded retailers | 1 |
| product_omschrijving | 1 |
| product portfolio per plant / supplier | 1 |
| production by bodystyle | 1 |
| production by plant / factory | 1 |
| production by platform | 1 |
| production by vehicle program | 1 |
| production forecast (plant capacity/export/body style) | 1 |
| production method (sposob-produkcji) | 1 |
| production_serial_numbers | 1 |
| Profesional: Call tracker | 1 |
| Profesional: Estadísticas de rendimiento por anuncio (vistas/contactos) | 1 |
| Profesional: Perfil do comprador (buyer profile data) | 1 |
| Profesional: Posición del anuncio en los resultados de búsqueda (tiempo real) | 1 |
| Profesional: Recomendaciones de ajuste de precio/marketing (modelos lentos) | 1 |
| profile-accuracy / re-guide flag (new damage) | 1 |
| Profiles & schemes management | 1 |
| Profit / gross projection (por vehiculo) | 1 |
| Profit corridor indicator | 1 |
| Profit Funnel report | 1 |
| Profit objective | 1 |
| Profit potential / ROI por vehiculo | 1 |
| Profit target / Business Plans (filtro por profit potential) | 1 |
| Profit target / profit potential | 1 |
| Profit vs speed (margin vs days-to-sale tradeoff) | 1 |
| Profitto | 1 |
| [MED·Maletero] Profundidad (cm) | 1 |
| Programmatic / proxy bidding (S.A.M.) | 1 |
| ProgressivoRCL | 1 |
| Projected front-end gross / PVR | 1 |
| Projected/forecasted value (next month) | 1 |
| Projector Headlamps | 1 |
| proof of purchase (if registered keeper < 3 months) | 1 |
| property_rights_restrictions | 1 |
| Propriétaire Première main (flag) | 1 |
| proprietaire_actuel_anonymise | 1 |
| Pros (Good Things) | 1 |
| Provenance (procedencia) | 1 |
| Provenance check (via Experian, separate subscription) | 1 |
| provenienza | 1 |
| province | 1 |
| province name (nazwa-wojewodztwa) [Statystyki] | 1 |
| Provision Appraised Value (sigue al vehiculo compra->venta) | 1 |
| Provisioning value | 1 |
| PTAC_kg (F.2) | 1 |
| PTAV_poids_a_vide_kg (G.1) | 1 |
| PTES_pt_en_service_kg (G) | 1 |
| PTRA_kg (F.3) [API] | 1 |
| PTTA_pt_techniquement_admissible_kg (F.1) | 1 |
| Public (badge) | 1 |
| publicatiedatum_rdw | 1 |
| publicationDate | 1 |
| publishable | 1 |
| publisher_name | 1 |
| publisher_phone | 1 |
| Publishes to AutoCheck VHR | 1 |
| Publishes to Carfax VHR | 1 |
| PUC certificate | 1 |
| Puissance DIN (ch) | 1 |
| Puissance fiscale (CV) | 1 |
| puissance_fiscale_ch | 1 |
| Puja actual (current bid) | 1 |
| Pujas de compradores profesionales | 1 |
| Puntos de interes (POI: hoteles/bancos/parking/gasolineras/restaurantes) | 1 |
| Puntos de severidad de daño | 1 |
| puntuacion del vehiculo (车辆评分) | 1 |
| Purchase price aseguradora (importador + lista) | 1 |
| purchase-likelihood score | 1 |
| purchase-rate lift multiplier (10x overall / 25x brand / 7x segment / 5x EV / 2.5x vs competitors) | 1 |
| Purpose (Buy / Sell) | 1 |
| qualityCheck descriptionLength (min 500 / optimal 1000 chars / current) | 1 |
| qualityCheck image overlays result | 1 |
| qualityCheck image vehicleFocus result | 1 |
| qualityCheck image vehicleVisibility result | 1 |
| qualityCheck imageQuality score | 1 |
| qualityCheck imageQuantity (min 10 / optimal 25 / current) | 1 |
| qualityCheck overallQualityCheck (0-100) | 1 |
| qualityCheck status | 1 |
| Quantidade de passageiros / plazas (QtdPassageiro) | 1 |
| Quantity (cantidad) | 1 |
| Quick Check (precio puntual) | 1 |
| quilometragem (km) | 1 |
| Quimica de celda y composicion de catodo | 1 |
| Équipements de sécurité (liste itemizada) | 1 |
| Équipements extérieur (liste) | 1 |
| Équipements intérieur (liste) | 1 |
| QuotazioneMensileRitiro | 1 |
| QuotazioneMensileVendita | 1 |
| QuotazioneRitiro | 1 |
| QuotazioneStandardRitiro | 1 |
| QuotazioneStandardVendita | 1 |
| QuotazioneStorica | 1 |
| QuotazioneVendita | 1 |
| QuotazioneVenditaPersonalizzata | 1 |
| Quote de movimiento (precio) | 1 |
| Quote manipulation indicators | 1 |
| Réf. pro / Réf. annonce | 1 |
| Régimen BPM más favorable (selección automática) | 1 |
| Régions et pays voisins (filtre) | 1 |
| Rachat Express: attestation de paiement <48h | 1 |
| Rachat Express: estimation gratuite (<2 min, plaque+km) | 1 |
| Rachat Express: offre de rachat ferme (€) | 1 |
| Rachat Express: RDV concessionnaire agréé (300) | 1 |
| radar equipment type (wyposazenie-i-rodzaj-urzadzenia-radarowego) | 1 |
| Radio de conduccion por minutos (isocronas) | 1 |
| [EQUIP·Multimedia] Radio digital | 1 |
| Radio functionality | 1 |
| RaggruppamentoVincolo | 1 |
| rang_titulaire (1er/2e...) | 1 |
| RangeAnni | 1 |
| rangeCombined (autonomía combinada) | 1 |
| rangeElectric (autonomía eléctrica) | 1 |
| RangeKm | 1 |
| RangeScarto | 1 |
| Rango de precio del listado (lowPrice–highPrice) | 1 |
| Rango/fecha de producción (DESDE mm-aaaa) | 1 |
| ranking de producción (2º de Europa / Top-10 mundial) | 1 |
| ranking internacional de países VA/VC | 1 |
| Rapport h/L pneu arrière | 1 |
| Rapport h/L pneu avant | 1 |
| rapport_puissance_masse [API] | 1 |
| RapportoPotenzaMassa | 1 |
| RapportoPotenzaMassima | 1 |
| Rated speed rpm (from/to) | 1 |
| Ratio VO:VN | 1 |
| RC status | 1 |
| RC verification (registration details, VAHAN) | 1 |
| RDW oordeel kilometerstand (juicio NAP: Logisch/Onlogisch) | 1 |
| RDW raw data estructurada | 1 |
| rdwConstruction | 1 |
| Re-auction recommendation (IntelliSeller) | 1 |
| Re-valoraciones ilimitadas multi-escenario (edad/km) | 1 |
| real auction outcomes (ML signal) | 1 |
| Real cash value / guaranteed offer (price.offer) | 1 |
| Real Market Value (RMV) — composite valuation | 1 |
| real_time_value_calculation | 1 |
| Real-time auction market data (~1.000 vehiculos/semana) | 1 |
| Real-time collaboration experto-reparador | 1 |
| Real-time daily valuation | 1 |
| Real-time market valuation (ACV VIPER) | 1 |
| Real-time notifications (new app) | 1 |
| Real-time SMS alerts (tire replacement + acquisition lead: mileage/title/recommended offer) | 1 |
| Real-time valuation (BCA Market Price) | 1 |
| Real-time vehicle offer (rooftop-specific) | 1 |
| Real-Time Vehicle Tracking | 1 |
| Rear AC Vents | 1 |
| rear_brake_diameter | 1 |
| Rear Camera | 1 |
| Rear Cross Traffic Alert | 1 |
| rear_head_room | 1 |
| rear_hip_room | 1 |
| rear_legroom | 1 |
| Rear Parcel Tray | 1 |
| Rear Seat Headrest | 1 |
| rear_seats | 1 |
| rear_shoulder_room | 1 |
| rear_suspension_size | 1 |
| rear_suspension_type | 1 |
| Rear tire age (excellent/good/poor) | 1 |
| rear_tire_order_code | 1 |
| rear_tire_pressure | 1 |
| rear_tire_size | 1 |
| rear_tire_type | 1 |
| Rear Tires condition | 1 |
| rear_track | 1 |
| Rear track size | 1 |
| rear_travel | 1 |
| Rear view mirror | 1 |
| Rear Visibility System | 1 |
| rear_wheel_dia | 1 |
| rear_wheel_diameter | 1 |
| Rear Window Defogger | 1 |
| Rear Window Washer | 1 |
| Rear Window Wiper | 1 |
| Reason for loss | 1 |
| reasonCode (KADOE) | 1 |
| Reasoning (key data signals + market factors) | 1 |
| Reasoning / key data signals (explicabilidad) | 1 |
| Rebuilt title (is_rebuilt_title) | 1 |
| Recargo perla/bicapa (+2% materiales) | 1 |
| Receipt document (generated) | 1 |
| Recent comparable sales (lista + grafico) | 1 |
| Recent comparable transaction data | 1 |
| recent_comparables | 1 |
| recent purchaser exclusion (suppression) | 1 |
| Recent Transactions - average kilometers driven | 1 |
| Recent Transactions (50, ult. 3 meses) - average selling price | 1 |
| Recent Transactions - highest selling price | 1 |
| Recent Transactions - lowest selling price | 1 |
| Recomendación de precio / precio final | 1 |
| Recomendacion de distribucion/canal de inventario | 1 |
| Recomendacion de reacondicionamiento | 1 |
| recommended / optimal price | 1 |
| Recommended acquisition / appraisal price (por canal) | 1 |
| Recommended price adjustment (subir/bajar) | 1 |
| Recon alerts (problemas comunes por year/make/model) | 1 |
| Recon estimate (at appraisal) | 1 |
| Recon plan templates | 1 |
| Recon step/stage tracking | 1 |
| Recon variance (estimate vs actual, VIN-level) | 1 |
| Recon variance breakdown by appraiser/advisor/source/store | 1 |
| Reconditioning cost (mecanico + cosmetico) | 1 |
| Reconditioning cost estimate | 1 |
| Reconditioning estimate | 1 |
| Reconditioning expectation (implied by grade) | 1 |
| Reconditioning issue flags (por YMM) | 1 |
| [EQUIP·Seguridad] Reconocimiento de señales de tráfico | 1 |
| reconstructed_title_issued_flag | 1 |
| record_confidence | 1 |
| record_source | 1 |
| recorded_selling_prices | 1 |
| Recovery status | 1 |
| [EQUIP·Varios] Recuperación de la energía de frenado | 1 |
| Recycling charge | 1 |
| RedBook ID | 1 |
| RedBook watermark | 1 |
| RedbookCodeLegacy | 1 |
| redemption (identity verified / fraud detection / 30s) | 1 |
| redline | 1 |
| reducción de fraude (trazabilidad y coherencia de datos) | 1 |
| reduced_price | 1 |
| reembolso integro vitalicio (accidente/incendio/inundacion) | 1 |
| reemplazo/garantia 30 dias | 1 |
| ref_miles | 1 |
| ref_miles_dt | 1 |
| ref_price | 1 |
| ref_price_dt | 1 |
| Ref. Expediente | 1 |
| Ref. Valoración | 1 |
| Reference Number | 1 |
| referenceNumber (KADOE) | 1 |
| referencia 3 / versión (line3) | 1 |
| referentiecode_producent | 1 |
| referentiecode_rdw (recall) | 1 |
| Referrals (listing analytics) | 1 |
| Refurbishment adjustment | 1 |
| Refurbishment cost (₹) | 1 |
| Região (12 macro-regiones comerciales B2B) | 1 |
| Regime IVA (corrente / 4% / personalizzato) | 1 |
| Register of Approved Vehicles (RAV) reference | 1 |
| registratie_datum_goedkeuring_afschrijvingsmoment_bpm | 1 |
| regulatory trends | 1 |
| Release / launch date | 1 |
| Release Date | 1 |
| release_month | 1 |
| remaining_lifespan (años de vida útil restante - metrica firma) | 1 |
| remarks (lead) | 1 |
| Remote Door Lock/Unlock | 1 |
| Remote ignition | 1 |
| Remove and install / R&I (estimate line) | 1 |
| Renewal pricing optimization (MOT tracking) | 1 |
| renewalDate | 1 |
| Rental / ex-hire deduction (השכרה / החכרה) | 1 |
| Rental cost reduction | 1 |
| Rental penetration (adjustable residual-sensitivity input) | 1 |
| Rentals flag | 1 |
| Repair / claim status (eRepair) | 1 |
| Repair authorisation (fleet/leasing) | 1 |
| Repair by Hail Formula (recargo aluminio/cavidad/adhesivo) | 1 |
| repair_decision | 1 |
| repair_description | 1 |
| Repair estimate | 1 |
| repair_estimates (CA) | 1 |
| Repair estimation data (AudaEnterpriseGold) | 1 |
| Repair or replace (estimate line) | 1 |
| repair_title | 1 |
| repair_value_id | 1 |
| Repairable vs total-loss determination | 1 |
| Reparaturen / Reparaturaufwand (reparaciones) | 1 |
| Reparaturkosten Markt (coste medio de reparacion) | 1 |
| Reparaturkostenkalkulation (damage repair cost) | 1 |
| Reparaturweg (via de reparacion) | 1 |
| Reparieren vs ersetzen (decision reparar vs sustituir) | 1 |
| replacement / holding time expectation | 1 |
| Replacement cost | 1 |
| Replacement value (valor de reemplazo, seguros) | 1 |
| Repo agent & vehicle release management | 1 |
| report_average_dom | 1 |
| report_average_price | 1 |
| Report: CarGurus Intelligence Report (monthly dealer-facing) | 1 |
| Report: Consumer Insights Report (annual survey 3000+ buyers/sellers) | 1 |
| report_date | 1 |
| report_ev_share_percent | 1 |
| Report generation date / fecha del informe | 1 |
| Report ID | 1 |
| report_price_band_distribution | 1 |
| Report reference number | 1 |
| Report Run Date/Time | 1 |
| report_total_listings | 1 |
| report_total_rooftops | 1 |
| report_url | 1 |
| report.source.build_data | 1 |
| report.source.ppsr | 1 |
| report.source.valuation | 1 |
| report.source.vehicle_details | 1 |
| Reporte de recuperación (vehículo recuperado) | 1 |
| Reporting entity address | 1 |
| Reporting entity category | 1 |
| Reporting entity contact (phone/email) | 1 |
| Reporting entity contact info | 1 |
| Reporting entity name | 1 |
| Reporting entity type (Individual / Insurer / Recycler / Salvage Pool / Shredder) | 1 |
| Repossessed flag | 1 |
| Repossession stock status | 1 |
| representación gráfica de KPI | 1 |
| representación métrica de KPI | 1 |
| Repricing advice | 1 |
| repricing recommendation | 1 |
| Reprise (estimation) | 1 |
| Request number (report ID) | 1 |
| requestDate | 1 |
| Requested-by (client) | 1 |
| requestedDate / returnedDate / href / count (metadatos API) | 1 |
| research report snippets | 1 |
| Reserve | 1 |
| Reserve price recommendation | 1 |
| reserve pricing | 1 |
| reserve_tank_capacity | 1 |
| Reserve-met indicator | 1 |
| reserved | 1 |
| Residual by vehicle age (1-10 years) | 1 |
| Residual sensitivity to incentives | 1 |
| Residual sensitivity to rental penetration | 1 |
| residual-value.custom_ratio | 1 |
| residual-value.custom_value | 1 |
| residual-value.input.customization_amount (±€) | 1 |
| residual-value.input.feature_ids | 1 |
| residual-value.input.initial_price | 1 |
| residual-value.input.release_at | 1 |
| residual-value.input.simulate_at (archive si pasado) | 1 |
| residual-value.input.vehicle_id | 1 |
| residual-value.manufacturer_price (prix neuf constructor) | 1 |
| residual-value.ratio (VR % = valor/prix neuf) | 1 |
| residual-value.return_at (fecha retorno) | 1 |
| residual-value.value (VR €) | 1 |
| residual.initial_kms | 1 |
| residual.kms | 1 |
| residual.score | 1 |
| residual.valuation | 1 |
| residual.yearly_kms | 1 |
| responseMetrics: advertViews | 1 |
| responseMetrics: naturalAdvertViews | 1 |
| responseMetrics: paidPPCAdvertViews | 1 |
| responseMetrics: searchViews | 1 |
| Rest-BPM (BPM residual usado importado) | 1 |
| restraint_systems_others | 1 |
| restraint type | 1 |
| restraintTypes | 1 |
| Restrições (Decoder) | 1 |
| Restwaarde actual (current residual value) | 1 |
| Restwaarde futura (future residual value) | 1 |
| Resultado de subasta en 48h | 1 |
| resumen del tasador (评估师总结) | 1 |
| Retail Accelerator alert: ageing / overage stock | 1 |
| Retail Accelerator alert: incorrect pricing | 1 |
| Retail Accelerator alert: out-of-strategy vehicle | 1 |
| Retail Accelerator alert: valuation change | 1 |
| Retail Accelerator: competitor activity review | 1 |
| Retail Accelerator: dynamic performance reporting | 1 |
| Retail Accelerator: overage policy (plan) | 1 |
| Retail Accelerator: pricing policy (plan) | 1 |
| Retail Accelerator: required stock turn (plan) | 1 |
| Retail ad performance | 1 |
| Retail Back: maximum price to pay (retail - costs - target gross margin) | 1 |
| Retail DMS sales transactions (input) | 1 |
| Retail equipped value | 1 |
| Retail Intelligence metrics | 1 |
| Retail photos / AI photo generation | 1 |
| Retail Rating (1-100) | 1 |
| Retail sales (units) | 1 |
| retail_turnover | 1 |
| retail vs business sales channel | 1 |
| Retail vs wholesale recommendation (por unidad) | 1 |
| Retail/wholesale exit strategy recommendation | 1 |
| retailAdverts.price | 1 |
| RetailPer4mance: sales experience | 1 |
| RetailPer4mance: traffic | 1 |
| RetailPer4mance: value proposition | 1 |
| Retained value comparison (like-for-like) | 1 |
| retained_value_pct (vs RRP) | 1 |
| Retainer/saved costs (rental) | 1 |
| Retención de valor a 3 años (%) (36 meses / 60.000 km) | 1 |
| retención de valor a 3 años por motorización (% sobre precio de tarifa) | 1 |
| [EQUIP·Seguridad] Retrovisor interior antideslumbramiento automático | 1 |
| [EQUIP·Seguridad] Retrovisores exteriores con calefacción | 1 |
| [EQUIP·Confort] Retrovisores exteriores con memoria | 1 |
| [EQUIP·Confort] Retrovisores exteriores orientables eléctricamente | 1 |
| [EQUIP·Confort] Retrovisores exteriores plegables eléctricamente | 1 |
| Returns | 1 |
| Review: Cons | 1 |
| Review: Edmunds says (verdict) | 1 |
| Review: Pros | 1 |
| Review: What's new | 1 |
| rfl_12_month_y1 (road tax) | 1 |
| rfl_12_month_y2_to_y6 | 1 |
| rfl_12_month_y2_to_y6_premium | 1 |
| rfl_6_month_y2_to_y6 | 1 |
| rfl_6_month_y2_to_y6_premium | 1 |
| rfrAndComments[]/defects[] (array) | 1 |
| RicambiCarrozzeria | 1 |
| RicambiMeccanica | 1 |
| RiduzionePianificata | 1 |
| right-hand drive (kierownica-po-prawej-stronie) | 1 |
| Rijklaarprijs | 1 |
| Rim diameter | 1 |
| Rim material | 1 |
| Rim screw-hole circle | 1 |
| risicobeoordeling_rdw | 1 |
| Risikobestand (inventario de riesgo >90 dias, % y EUR/dia) | 1 |
| Risk flag on user value modification | 1 |
| risk_models (origination/insurance) | 1 |
| RisultatoUnivoco | 1 |
| RitiroAssoluto | 1 |
| RitiroPerc | 1 |
| RitiroPercListino | 1 |
| RitiroPercPAC | 1 |
| RMS: profit uplift $/vehículo ($100-200) | 1 |
| RMS: Reconditioning Optimization (reparaciones VIN-específicas vía AutoGrade) | 1 |
| RMV: projected days to turn (how fast it'll turn) | 1 |
| RMV: projected retail sell price (what it'll sell for) | 1 |
| RMV: recommended price to pay (what to pay) | 1 |
| Road test result (<=10 mi, 70 mph) [128] | 1 |
| Roadside assistance (AssistFirst) | 1 |
| Roadworthiness issues | 1 |
| roadworthy | 1 |
| ROAS (return on ad spend) | 1 |
| roetfilter_af_fabriek_apk (OVI) | 1 |
| rollover_rating | 1 |
| RON Rating | 1 |
| roof is_two_tone | 1 |
| roof primary_rgb_code | 1 |
| roof secondary_rgb_code | 1 |
| roof_type | 1 |
| Rooftop-specific pricing | 1 |
| Rotazione | 1 |
| Rottamazione (allowance achatarramiento) | 1 |
| RPI like-for-like price growth (%) | 1 |
| RPI mix growth (%) | 1 |
| rrp_adjustment | 1 |
| rrp_overwrite | 1 |
| RTO: Insurer | 1 |
| RTO: PUCC Upto | 1 |
| RTO: RC Number | 1 |
| RTV (Real Time Valuation) | 1 |
| RTV Type: Base (base vehicle) | 1 |
| RTV Type: Market (option-equipped) | 1 |
| rubber price forecast | 1 |
| Rueckwirkende Bewertung zum Stichtag (valoracion retroactiva a fecha) | 1 |
| Run & Drive status | 1 |
| run_and_drive_status | 1 |
| Run list position | 1 |
| Run number | 1 |
| Running / side lights | 1 |
| Running cost per month | 1 |
| Running costs | 1 |
| runs_drives | 1 |
| rupsonderstelconfiguratiecode | 1 |
| Rutas de conduccion | 1 |
| RV ajustado por riesgo (risk outlook del usuario) | 1 |
| RV benchmark vs competitors | 1 |
| RV performance ranking | 1 |
| RV predecessor-successor tracking | 1 |
| RV pressure | 1 |
| RV risk metric | 1 |
| RV slice por periodo de tiempo | 1 |
| RV style & class | 1 |
| RV type (travel trailer/park model/motor home/truck camper/camping trailer) | 1 |
| RV value drivers / trends | 1 |
| S.A.M. Alerts (notifica para aprobar) | 1 |
| S.A.M. API / S.A.M. UI | 1 |
| S.A.M. Bids (proxy automatico 24/7) | 1 |
| SAAR (seasonally adjusted annualized rate) | 1 |
| SAE Automation Level From | 1 |
| SAE Automation Level To | 1 |
| SAE autonomous level (base) | 1 |
| safety_assist_score | 1 |
| Safety: IIHS ratings [campos NO-VERIFICADO] | 1 |
| Safety: NHTSA ratings [campos NO-VERIFICADO] | 1 |
| safety_overall_star_rating | 1 |
| safety_rating_source_org | 1 |
| safety_ratings | 1 |
| safety_score_explanation | 1 |
| safetyInfo.condition | 1 |
| safetyInfo.description | 1 |
| safetyInfo.note | 1 |
| safetyInfo.source (e.g. NHTSA) | 1 |
| safetyInfo.value (e.g. 5 Star) | 1 |
| saldo comercial de vehículos (€) | 1 |
| saldo comercial total de automoción (€) | 1 |
| Sale channel (Bid Now / Buy Now / Live Online / xBid / EuroShop) | 1 |
| Sale date/time | 1 |
| Sale day of week | 1 |
| sale_document | 1 |
| Sale format (timed / same-day / buy-now) | 1 |
| Sale format: 45-min auction (estados Upcoming/Active/Closing/Pending/Purchases, proxy bid) | 1 |
| Sale format: Open Sale / Timed (programadas) | 1 |
| Sale format: Simulcast (live, run list exportable, indicador LIVE, auto-bid, join <=1h) | 1 |
| Sale Info (sale date/time) | 1 |
| Sale light (semáforo condición/venta) | 1 |
| Sale light: Blue (title not present) | 1 |
| Sale light: Green (free of known major arbitrable defects, ride & drive) | 1 |
| Sale light: Green+Yellow (free except announced) | 1 |
| Sale light: Red / Limited As-Is | 1 |
| Sale light: Yellow / Limited Guarantee (announced condition, limits arbitration) | 1 |
| Sale price / hammer price | 1 |
| Sale price vs CAP | 1 |
| Sale results / run list | 1 |
| Sale results CSV download | 1 |
| Sale title state | 1 |
| Sale title type / Title code | 1 |
| Sale type (Bid / Buy Now / OVE Timed 24/7 / Live Sales) | 1 |
| sales (direct attribution) | 1 |
| Sales Count | 1 |
| Sales event history (images/mileage/price/text) | 1 |
| sales figures per territory | 1 |
| sales forecast (7 & 12 year, brand level) | 1 |
| sales generated | 1 |
| sales_history_date | 1 |
| sales performance | 1 |
| sales potential | 1 |
| sales_time_forecast (expected days to sell) | 1 |
| sales transactions PII-free (Cross-Sell) | 1 |
| Sales type (open/closed-tender/buy-now/bid-or-buy/live/24h) | 1 |
| salesperson performance | 1 |
| sampleSize (nº transacciones en la muestra) | 1 |
| saved_search_recommendations | 1 |
| Saved searches | 1 |
| Saved Searches / wish lists | 1 |
| Saved-vehicle alerts (comparables/cambios) | 1 |
| savingText (savings amount vs market) | 1 |
| Scenario forecast - Inflation | 1 |
| Scenario forecast - Long-Term Growth | 1 |
| Scenario forecast - Mild Recession | 1 |
| Scenario forecast - Severe Recession | 1 |
| Scenario forecast - Stagnation | 1 |
| Scenario-based residual - adverse economic | 1 |
| Scenario-based residual - baseline economic | 1 |
| Scenario-based residual - severe/stressed economic | 1 |
| Schade/daños (tasación ampliada) [A] | 1 |
| Schadenart (tipo de dano) | 1 |
| Schadensakte (expediente digital de siniestro) | 1 |
| Schadstoffklasse (emissions class) | 1 |
| Schatting waarde koop (rango mín-máx) | 1 |
| Schatting waarde verkoop (rango mín-máx) | 1 |
| Schedule test drive | 1 |
| Scheduled service items | 1 |
| Schwacke Tagespreis (daily live-retail price) | 1 |
| Schwacke-Code | 1 |
| schwackeCode | 1 |
| Sconti (percentuale o valore assoluto) | 1 |
| Score: Comfort | 1 |
| Score: Driving/Performance | 1 |
| Score factor: Vehicle Class | 1 |
| Score factor: Vehicle Use and Events | 1 |
| Score: Interior | 1 |
| Score position (below / within / above range) | 1 |
| Score: Storage/Utility | 1 |
| Score: Technology | 1 |
| Score: Value/Good Value | 1 |
| Score: Wildcard | 1 |
| scostamento_valutazione | 1 |
| scraped_at | 1 |
| scraped_at_date | 1 |
| scrapedAt / last_updated | 1 |
| scrappage rate development | 1 |
| scrappage schemes | 1 |
| Screen washers (front/rear) | 1 |
| search_alert (new-match + price-drop) | 1 |
| Search history en la misma pantalla | 1 |
| Search Page | 1 |
| Search Rank (e.g. '22 out of 436 based on this search') | 1 |
| Seasonal adjustment | 1 |
| Seasonal trend | 1 |
| Seasonal trends | 1 |
| Seasonality | 1 |
| seasonally adjusted (SA) volume | 1 |
| Seat Belt Type | 1 |
| Seat Capacity | 1 |
| seat_material | 1 |
| seat_type | 1 |
| seatCount / 승차정원 (asientos) | 1 |
| seated places (liczba-miejsc-siedzacych) | 1 |
| Seating / seats | 1 |
| seating_capacity / seats | 1 |
| seating_rows | 1 |
| seatingCapacity | 1 |
| Seats condition | 1 |
| seats photo (front + back) | 1 |
| Secondary market performance | 1 |
| sector / branch (industry of registrant) | 1 |
| sector scorecard ranking | 1 |
| Securitization valuation | 1 |
| security_deposit | 1 |
| Security Watch 'at risk' marker | 1 |
| [EQUIP·Seguridad] Selector de modo de conducción | 1 |
| Sell My Car: instant cash offer (<2 min, dealer network / The Car Buying Group UK) | 1 |
| Sell sub-type (To Individual / To Dealer) | 1 |
| selling price | 1 |
| sello de certificación + timestamp + id de transacción (signature/id) | 1 |
| SellType / 판매유형 (일반…) | 1 |
| selo Super Preço (5-15% abaixo da FIPE + calidad) | 1 |
| selo Vistoriado (coche inspeccionado) | 1 |
| Semaforo vincoli/gravami (verde/giallo/rosso) | 1 |
| Separation | 1 |
| Serie de precios desestacionalizada (descomposición aditiva a 12 meses) | 1 |
| serie de valor multi-año (valueModel[], curva de depreciación observada) | 1 |
| SerieOpzionale | 1 |
| SerieOpzionaleProgressivo | 1 |
| Series2 | 1 |
| Service & maintenance parts | 1 |
| Service & maintenance price | 1 |
| service & parts department profitability (aftersales FinancialView) | 1 |
| service advisor performance | 1 |
| service bay optimization (optimal number of bays) | 1 |
| Service cost benchmarking | 1 |
| Service cost by term & distance | 1 |
| Service Count | 1 |
| service_date | 1 |
| service_description (oil change/tire rotation/inspection/repair) | 1 |
| service_fee_450 | 1 |
| service intervals (mileage e.g. 10000mi / time e.g. 12mo) | 1 |
| Service intervals / schedules | 1 |
| service_reminders (oil/tire/safety/emission) | 1 |
| service retention rate | 1 |
| Service schedule | 1 |
| service_type | 1 |
| service-history value adjust | 1 |
| service-loyal customer defection | 1 |
| Service-to-acquisition outcome (traded/competitor/returned) | 1 |
| Service/Gate fee | 1 |
| Service/repair/maintenance performed | 1 |
| ServiceCopyCar (alerta VIN duplicado / DUPLICATION) | 1 |
| Serviceintervall (intervalo de servicio por km real) | 1 |
| ServiceMark (EncarMeetgo / EncarDiagnosisP1/P2) | 1 |
| Servicing / maintenance record | 1 |
| Servicio: Acesso a leilões BCA (sourcing wholesale) | 1 |
| Servicio: coche por suscripción/renting | 1 |
| Servicio del vehículo (particular/público/taxi/alquiler con-sin conductor/escuela/agrícola/obras/escolar/mercancías peligrosas) | 1 |
| Servicio: Entrega em casa | 1 |
| Servicio: Financiación | 1 |
| Servicio: Financiamento (cuota mensual ajustable a entrada y plazo; Santander Consumer/Cofidis) | 1 |
| Servicio: Histórico do veículo (carVertical: accidentes/daños, +40 países, -20%) | 1 |
| Servicio: Informe de vehículos (historial por matrícula; proveedor no verificado) | 1 |
| Servicio: Inspeção (Controlauto: 200-350 parâmetros, custos de reparação estimados) | 1 |
| Servicio: Serviço de retoma (trade-in) | 1 |
| [EQUIP·Multimedia] Servicios en la nube | 1 |
| [EQUIP·Varios] Servicios remotos | 1 |
| ServiziACI | 1 |
| Set Floor Price (reserve) | 1 |
| Set-to-loan ratio (LTV) | 1 |
| Settlement / total-loss valuation | 1 |
| Settlement figure (total loss) | 1 |
| settlement value (insurance) | 1 |
| severe service schedule | 1 |
| Severidad del daño (Noa) | 1 |
| share performance impact | 1 |
| shopper connections (text/chat leads + map clicks + website visits) | 1 |
| Shopper engagement data | 1 |
| Short-term forecast (1-36 / 3-36 months) | 1 |
| Short-term forecast value (% ajuste; 1-36 meses productos / 3-60 meses ALG) | 1 |
| short-term sales forecast / Nowcast (current + next month) | 1 |
| shortlist | 1 |
| Shoulder room | 1 |
| shoulder_room_front | 1 |
| shoulder_room_rear | 1 |
| shoulder_room_third_row | 1 |
| Show ratio / buy ratio (lead quality) | 1 |
| showroom visits | 1 |
| Side Airbag | 1 |
| Side Airbag-Rear | 1 |
| Siegel/Zertifizierung (certified seal, excluido del comparable) | 1 |
| sighting.at | 1 |
| sighting.lead_id | 1 |
| sighting.listing_title | 1 |
| sighting.listing_url | 1 |
| sigla_combustivel (G / A / D) | 1 |
| SiglaTipoBatterie | 1 |
| sillas eléctricas (electricChairs) | 1 |
| Similare | 1 |
| Simulcast (puja/compra en vivo online) | 1 |
| single bill of sale | 1 |
| single stock photo (full/thumb location) | 1 |
| Single-driver modifier — reduces leasing deduction (נהג יחיד) | 1 |
| sistema de alimentación (foodSystem) | 1 |
| sistema de impresión de etiquetas B2B (fabricantes/concesionarios/talleres/ITV) | 1 |
| sistemas ADAS (asistencia a la conducción) | 1 |
| Situação cadastral do veículo (Decoder) | 1 |
| Situación de baja (temporal/definitiva) | 1 |
| Situación legal / estatus jurídico (vínculo a proceso judicial) | 1 |
| size of PARC | 1 |
| Skill Level (T1/T2/T3) | 1 |
| skip_trace_data_feed | 1 |
| Small Sample Size icon (muestra insuficiente) | 1 |
| Small sample size indicator | 1 |
| Smart Fields (auto-pull trim/mileage/features) | 1 |
| Smart pricing / price guidance | 1 |
| Smart Repair / Spot Repair | 1 |
| SMART repair items (PDR, alloy refurb, glass, minor paint/trim) | 1 |
| smart search filters (body type SUV/EV/high-performance, make/model, mileage, age, price, condition) | 1 |
| Smart tags (damage annotation) | 1 |
| Smartwatch App | 1 |
| smog_rating | 1 |
| Smyle: Festpreis (fixed non-negotiable price) | 1 |
| Smyle: Garantie 12 Monate (Allianz warranty) | 1 |
| Smyle: Lieferkosten (delivery fee desde 599 EUR) | 1 |
| Smyle: TÜV-Restlaufzeit (TÜV validity ≥6m) | 1 |
| Smyle: Zustandskriterien (≤6 años / ≤100.000 km) | 1 |
| SnapLot 360 (spin 360 interior/exterior + video) | 1 |
| Social Plus auto-promotion (high-Standzeit vehicles) | 1 |
| socio-demographic data | 1 |
| sociodemographic data | 1 |
| Sold Listings | 1 |
| Sold price | 1 |
| Sold price + (S) sold indicator | 1 |
| sold_vins | 1 |
| soldDate | 1 |
| SONAR Argus Annonces® (anuncios comparables) | 1 |
| SONAR Argus Transactions® (transacciones anonimizadas comparables) | 1 |
| [EQUIP·Multimedia] Sonido Dynaudio de 12 altavoces | 1 |
| soort_erkenning_keuringsinstantie | 1 |
| soort_melding_ki_omschrijving | 1 |
| soort_toegevoegd_object_omschrijving | 1 |
| Source (auction house / dealer) + View Source link | 1 |
| sourceUrl | 1 |
| sourcing & commodity price forecast (10-year) | 1 |
| Sovralimentazione | 1 |
| Speakers | 1 |
| Special features / equipment (sat-nav, heated seats) | 1 |
| Special note | 1 |
| Special-edition texts | 1 |
| Specialist charge | 1 |
| Specialty equipment/feature adjustment | 1 |
| Specialty pre-loss market value | 1 |
| Specifica_custom | 1 |
| Specifica_hard | 1 |
| Specifica_medium | 1 |
| Specifica_soft | 1 |
| specifications | 1 |
| speedControl (cruise control) | 1 |
| SpeseMarketing | 1 |
| SpeseRipristino | 1 |
| spoorbreedte (ancho de via) | 1 |
| Spot price (current) | 1 |
| Spring type | 1 |
| squishVins | 1 |
| Staat/conditie (tasación ampliada) [A] | 1 |
| staatscourant_indeling (tarifa) | 1 |
| Stand-in value (seller internal) | 1 |
| Standard GVWR | 1 |
| standard tyre sizes | 1 |
| Standard Viewing Angle (2m, 90 +/-45) | 1 |
| standard-value (valor a km estándar) | 1 |
| standardCurbWeight | 1 |
| standardEquipment (equipamiento de serie) | 1 |
| standardGVWR | 1 |
| Standardised replacement value (valor de reemplazo estandarizado) | 1 |
| Standardized appraisals | 1 |
| Standardized digital condition summary | 1 |
| standardized service naming | 1 |
| standardPayload | 1 |
| standardTowingCapacity | 1 |
| standing buy order / limit order | 1 |
| standing places (liczba-miejsc-stojacych) | 1 |
| Standtage / Standzeit (dias en stock por combustible) | 1 |
| Standtage Wettbewerber (competitor days on market) | 1 |
| Standzeitprognose (standing-time forecast, días a venta) | 1 |
| Start Code (Run & Drive / Starts / Stationary) | 1 |
| Start Date / Modification Date | 1 |
| Start of Production (SOP) date | 1 |
| Start price | 1 |
| Start price recommendation | 1 |
| start pricing | 1 |
| Start support | 1 |
| start-of-sales date | 1 |
| Start-Stop system | 1 |
| starter | 1 |
| State / RTO | 1 |
| State and local fees (title/license/registration, 53k+) | 1 |
| State Fees (total + Y1-Y5; license, registration, sales tax) | 1 |
| state_for_pricing (estatal vs nacional) | 1 |
| State Title Brands check | 1 |
| Static gear selection | 1 |
| stationary_soundlevel_db | 1 |
| stationary_soundlevel_rpm | 1 |
| statistic.calls | 1 |
| statistic.emails | 1 |
| statistic.impressions | 1 |
| statistic.parkings (watchlist saves) | 1 |
| statistics date (data-statystyki) [Statystyki] | 1 |
| Stato/uso del veicolo (ajuste por condicion) | 1 |
| StatoFirma | 1 |
| stats.count | 1 |
| stats.max | 1 |
| stats.mean | 1 |
| stats.median | 1 |
| stats.min | 1 |
| stats.missing | 1 |
| stats.percentiles | 1 |
| stats.stddev | 1 |
| stats.sum | 1 |
| stats.sum_of_squares | 1 |
| 원동기 status (motor) | 1 |
| status_date | 1 |
| Steel / crushed-car (scrap) prices | 1 |
| Steering | 1 |
| Steering Column | 1 |
| Steering noise (full lock) | 1 |
| Steering score | 1 |
| Steering system / posicion volante (LHD/RHD) | 1 |
| Stimata | 1 |
| stock alerts (matching dealer preferences) | 1 |
| Stock alerts sent (count) | 1 |
| stock clearance discounts | 1 |
| Stock days / reducción de días en stock (claim de venta rápida) | 1 |
| stock_feed_id | 1 |
| Stock ID | 1 |
| stock_listing_activity | 1 |
| stock_no | 1 |
| Stock Optimizer: composition du stock | 1 |
| Stock Optimizer: recommandation de repositionnement/canal | 1 |
| Stock Optimizer: véhicules à rotation lente | 1 |
| Stock photos | 1 |
| Stock Policy match | 1 |
| Stock position (posición de stock) | 1 |
| Stock pricing (Stockview) | 1 |
| stock trends | 1 |
| stock_type (new/used/CPO) | 1 |
| Stock value (valor de stock) | 1 |
| stock vs trade recommendation | 1 |
| Stock-level decision data (reserve / rerun) | 1 |
| Stock/smart alerts | 1 |
| stockImage.filename | 1 |
| Stocking gaps | 1 |
| stocking recommendation (optimum stock to purchase) | 1 |
| Stocking strategy alignment | 1 |
| Stocking-level recommendation (segun mercado + preferencias + exit strategy) | 1 |
| stockNumber | 1 |
| stockStatus | 1 |
| Stockwave Max Bid (puja maxima recomendada para cumplir profit goal) | 1 |
| Stockwave Strategy Action (indicador numerico +/-) | 1 |
| stone chips declaration (mandatory) | 1 |
| storage_capacity | 1 |
| Storage cost reduction | 1 |
| Storage fee | 1 |
| Storico delle revisioni | 1 |
| strategic trend indicator (CV) | 1 |
| Strategy grid: historical sales 125-day | 1 |
| Strategy grid: overstock vs understock indicator | 1 |
| Strategy grid: price class/band (fila) | 1 |
| street | 1 |
| Stress-test scenario | 1 |
| StringaInterventi | 1 |
| Structural Condition (rocker panels, pillars, frame) | 1 |
| Structured description (overview / exterior condition / interior condition / terms) | 1 |
| study_best_value_for_money (5y/10y) | 1 |
| study_cargo_space_ranking | 1 |
| study_compared_to_average_multiplier | 1 |
| study_deals_availability_index (% vs media por mes/festivo) | 1 |
| study_gas_price_impact_by_state | 1 |
| study_most_popular_used_cars_by_city_state | 1 |
| study_percent_chance_reaching_250000_miles (longevidad) | 1 |
| study_reliability_rating | 1 |
| study_resale_value_percent | 1 |
| study_safety_ranking | 1 |
| study_towing_capacity_ranking | 1 |
| studyPrice.activeSafetyFeatures | 1 |
| studyPrice.passiveSafetyFeatures | 1 |
| style_id | 1 |
| style name | 1 |
| styleDescription | 1 |
| styleName | 1 |
| Styles | 1 |
| sub-style | 1 |
| Subcanal de venta | 1 |
| subcategorie_nederland | 1 |
| subcategorie_voertuig_europees | 1 |
| subdivision | 1 |
| Submittal type (565/566) | 1 |
| submodel.body | 1 |
| submodel.full-nicename | 1 |
| submodel.modelName | 1 |
| submodel.name | 1 |
| submodel.niceName | 1 |
| submodel.position-quote | 1 |
| submodel.short-nicename | 1 |
| Subprime green light | 1 |
| subscribeCount / 찜 (favoritos) | 1 |
| Subseries | 1 |
| subtitle (version/variant) | 1 |
| Subtotal | 1 |
| subtype (tipo de valor) | 1 |
| Suchaufrufe / Suchanfragen (search impressions) | 1 |
| Suggested price moves (raise/lower) | 1 |
| Sum Insured / premium-setting input | 1 |
| Sum of comparables ($) | 1 |
| Sun Roof | 1 |
| Sundry parts (% / importe / importe max) | 1 |
| sunroof (Schiebedach) | 1 |
| Sunroof / moonroof operation | 1 |
| Sunroof addition (גג נפתח / סאן רוף) | 1 |
| Superficie de pintura (dm²) | 1 |
| Supermarket value (channel-segmented retail) | 1 |
| Superseded part identification | 1 |
| Superseded title flag | 1 |
| Supplier order status | 1 |
| supplier performance | 1 |
| SureCheck: brakes check | 1 |
| SureCheck: claims period 7 days / 250 miles | 1 |
| SureCheck: direccion | 1 |
| SureCheck: frenos | 1 |
| SureCheck: inspector accreditation (IMI-approved / NAMA-accredited) | 1 |
| SureCheck level cars: Bronze / Silver / Gold / EV | 1 |
| SureCheck level LCV: LCV / LCV-EV | 1 |
| SureCheck: non-invasive multi-point mechanical check | 1 |
| SureCheck: safety & operational standards checklist (pass/fail) | 1 |
| SureCheck: steering check | 1 |
| SureCheck: transmision/caja | 1 |
| SureCheck: up to 56 check points | 1 |
| Surgical comp sets (trim/build/options drill-down) | 1 |
| Suspensión delantera: estructura | 1 |
| Suspensión delantera: resorte | 1 |
| suspensión trasera (rearSuspension) | 1 |
| Suspensión trasera: estructura | 1 |
| Suspensión trasera: resorte | 1 |
| suspension_date | 1 |
| suspension_motif | 1 |
| suspension_remise_du_titre | 1 |
| suspension_retrait_du_titre | 1 |
| Suspension score | 1 |
| suspension_type_front_cont | 1 |
| Suspicious non-disclosure detection | 1 |
| Swiss Stammnummer linking | 1 |
| SWOT analysis (RV Report OEM) | 1 |
| Symboling (insurance) | 1 |
| Syndication (500+ third-party integrations) | 1 |
| Syndication a 500+ sitios de 3os (CarGurus, Cars.com, Autotrader) | 1 |
| Syndication channels/status (Google/Facebook/Instagram/marketplaces) | 1 |
| Syndication targets (web dealer + Autotrader + terceros) | 1 |
| synthese_situation_administrative (veredicto Rien a signaler / anomalie) | 1 |
| System errors | 1 |
| systemId | 1 |
| Türen (doors) | 1 |
| tabela_de_referencia (parâmetro de entrada: mês/ano) | 1 |
| tacómetro (tachometer) | 1 |
| tachographCard.cardExpiryDate | 1 |
| tachographCard.cardNumber | 1 |
| tachographCard.cardStartOfValidityDate | 1 |
| tachographCard.cardStatus | 1 |
| Tailgate electric window | 1 |
| Tamano de mercado y penetracion EV | 1 |
| tank_1_capacity | 1 |
| tank_2_capacity | 1 |
| tank_capacity | 1 |
| tank.fuel | 1 |
| tank.fuel-total-capacity | 1 |
| tank.hydrogen | 1 |
| [EQUIP·Decoración] Tapicería de cuero | 1 |
| tapicería en cuero SI/NO (upholsteryLeatherShow) | 1 |
| Targa | 1 |
| TargaEstera | 1 |
| TargaPrecedente | 1 |
| Target gross margin (input) | 1 |
| Target group (fleet/retail) | 1 |
| tarief (EUR) | 1 |
| tariefclustering | 1 |
| tarifa / precio del distintivo (IVA incl.) | 1 |
| Tarifa €/hora de mano de obra | 1 |
| Tarifa de (mes/año) | 1 |
| task workflow status (notifications/escalations) | 1 |
| taxClass | 1 |
| taxes & fees (total loss) | 1 |
| taxi_indicator | 1 |
| Taxi valuation basis / deduction (מונית) | 1 |
| taxonomy: bodyTypes | 1 |
| taxonomy: cabTypes | 1 |
| taxonomy: fuelTypes | 1 |
| taxonomy: styles / subStyles | 1 |
| taxonomy: vehicleTypes | 1 |
| taxonomy: wheelbaseTypes | 1 |
| TCPA consent | 1 |
| tech-feature price premium (+91% in 2025) | 1 |
| Technical specifications | 1 |
| technicalSpec.group | 1 |
| technicalSpec.header | 1 |
| technicalSpec.measurementUnit | 1 |
| technicalSpec.title | 1 |
| technicalSpec.value.condition | 1 |
| technician performance | 1 |
| technician staffing requirement | 1 |
| technisch_toegestane_maximum_aslast | 1 |
| technisch_toelaatbaar_massa_koppelpunt | 1 |
| technisch_toelaatbaar_maximum_massa_rupsbandset | 1 |
| technische_max_massa_voertuig | 1 |
| technology | 1 |
| technology & convenience add-ons (VINView Pro) | 1 |
| technology_features | 1 |
| [EQUIP·Confort] Techo solar panorámico | 1 |
| techo solar/sunroof SI/NO (sunroofShow) | 1 |
| techSpec.description | 1 |
| techSpec.id | 1 |
| techSpec.name | 1 |
| techSpec.nameNoBrand | 1 |
| techSpec.rankingValue | 1 |
| techSpec.unitOfMeasure | 1 |
| techSpec.value | 1 |
| Tecnología de pintura (Solvent M.S./base agua) | 1 |
| Telematikdaten / Live-Kilometer (telematica km en vivo) | 1 |
| Tell-Tale icons | 1 |
| tellerstandoordeel (juicio km: Logisch/Onlogisch/Geen oordeel) | 1 |
| Tempi di giacenza media nel web (days-on-web) per allestimento | 1 |
| Tempi di riparazione carrozzeria | 1 |
| Tempi di riparazione meccanica | 1 |
| Tempo di ricarica (EV) | 1 |
| TempoRicaricaMinuti | 1 |
| TempoRicaricaOre | 1 |
| TempoRicaricaRapidaMin | 1 |
| TempoRicaricaSecondi | 1 |
| Ten (10) pricing proof points | 1 |
| tenaamstellen_mogelijk | 1 |
| Tendencia de niveles de restwaarde (mensual) | 1 |
| Tender proposal (propuesta de licitación seguros) | 1 |
| TensioneRicaricaRapida | 1 |
| TensioneRicaricaVolt | 1 |
| TensioneTotaleBatterie | 1 |
| Term (financiacion) | 1 |
| termination (network action) | 1 |
| territorial encroachment detection | 1 |
| terugroep_code_status (O=abierta/P=reparada) | 1 |
| terugroep_merk | 1 |
| terugroep_status | 1 |
| terugroep_type | 1 |
| test_drive_booking | 1 |
| Tested: 0-60 acceleration | 1 |
| Tested: braking distance | 1 |
| testResult (PASSED/FAILED/null) | 1 |
| Tetto | 1 |
| Text overlays (warranty/cert/pricing) | 1 |
| tgk_aantalwielen | 1 |
| tgk_voertuigcategorie | 1 |
| thematic scorecard score (company x theme) | 1 |
| theme map (top 10 themes: tech/macro/industry/ESG) | 1 |
| theme market size & growth forecast | 1 |
| theme timeline | 1 |
| Third-party pricing comparisons | 1 |
| Third-party pricing data | 1 |
| Third-party private-party leads (KBB ICO) | 1 |
| Thousands of images per drive-through (VIPER) | 1 |
| thread_size | 1 |
| Tiempo de carga (EV) | 1 |
| Tiempo de conduccion | 1 |
| tiempo de entrega (35-45 dias) | 1 |
| Tiempo en UT (unidades de trabajo) | 1 |
| Tiempos de servicio OEM | 1 |
| tiempos y baremos de reparación | 1 |
| Tiempos y baremos de reparacion (ES) | 1 |
| Tier 1 sales attribution lift | 1 |
| Tier 2 sales attribution lift | 1 |
| tijdstip_laatste_tenaamstelling (OVI) | 1 |
| Time left / countdown dinámico | 1 |
| Time remaining | 1 |
| time_to_prep | 1 |
| Time-to-line | 1 |
| Time-to-line / recon days (2.8 dias mas rapido) | 1 |
| Timeline: Data Source (State Agency/Motor Vehicle Dept./Auto Insurance Source/Police Report/Auction) | 1 |
| Timeline: Details/Event description | 1 |
| Timeline efficiencies | 1 |
| Timeline: Event Date | 1 |
| timeline_event_records | 1 |
| Timeline: service entry / piezas reemplazadas | 1 |
| Timeline: vehicle use - leasing/fleet | 1 |
| Timeline: vehicle use - rental | 1 |
| Timeline: vehicle use - taxi | 1 |
| timestamp | 1 |
| tipo (novo / seminovo / usado) | 1 |
| tipo de caja mecánica/automática (typeBox) | 1 |
| Tipo de combustível | 1 |
| tipo de dirección hidráulica/eléctrica (typeAddress) | 1 |
| tipo de energia (燃油/新能源) | 1 |
| tipo de faros halógeno/LED (typeHeadlights) | 1 |
| tipo de frenos (brakes) | 1 |
| tipo de listado (sealed-bid auction / live auction / buy-it-now) | 1 |
| Tipo de mercado nautico (nuevo/ocasion/importacion) | 1 |
| Tipo de moto/ciclomotor | 1 |
| Tipo de motorización (BEV/PHEV/HEV/gasolina/diésel) | 1 |
| Tipo de pintura (bicapa metálico/sólido) | 1 |
| Tipo de pricing (ranged vs gp) | 1 |
| tipo de transmision (变速箱 MT/AT) | 1 |
| tipo de vehículo: Autobuses | 1 |
| tipo de vehículo: Comercial ligero | 1 |
| tipo de vehículo: Industriales | 1 |
| tipo de vehículo: Motos/Ciclos/Quad | 1 |
| tipo de vehículo: Tractores | 1 |
| tipo de vehículo: Turismos | 1 |
| Tipo di corrente (EV) | 1 |
| Tipo di fase (EV) | 1 |
| Tipo di passaggio di proprieta | 1 |
| tipo_veiculo (1=carro, 2=moto, 3=caminhão) | 1 |
| Tipo y duración de carga | 1 |
| TipoCarrozzeria | 1 |
| TipoCatalizzatore | 1 |
| TipoCategoria | 1 |
| TipoCombustibile | 1 |
| TipoGuida | 1 |
| TipoIbridazione | 1 |
| TipoImpianto | 1 |
| TipologiaCorrentePresa | 1 |
| TipologiaDocumento | 1 |
| TipologiaTagliando | 1 |
| TipoSovralimentazione | 1 |
| [EQUIP·Decoración] Tiradores de puertas retráctiles eléctricamente | 1 |
| Tire condition scan (precision 1/32 pulgada) | 1 |
| Tire photos | 1 |
| Tire Pressure Monitor | 1 |
| Tire Pressure Monitoring System (TPMS) Type | 1 |
| Tire tread % remaining | 1 |
| Tire tread depth to nearest 1/32" (4 tires) | 1 |
| Tire tread images | 1 |
| Tires & Wheels (tamaño/condición/precio) | 1 |
| Title / Sale Document | 1 |
| title_check_branding | 1 |
| title_description | 1 |
| title fee | 1 |
| title_history | 1 |
| title information / title brands | 1 |
| title_issue_date | 1 |
| Title issue date / last title date | 1 |
| title_issued_or_updated | 1 |
| Title issues / branding (history factor) | 1 |
| title processing status / time | 1 |
| Title Procurement (state title law) | 1 |
| title_record | 1 |
| title_state | 1 |
| title_status | 1 |
| Title status / title history | 1 |
| Title status / Title Tracker | 1 |
| Title status / tracking (Title Express) | 1 |
| Title transferred to insurer name | 1 |
| title_type | 1 |
| Title type / event (original, duplicate, lien release, transfer, superseded) | 1 |
| title_washing_alert_police | 1 |
| title_washing_flag | 1 |
| titulaire_code_postal | 1 |
| titulaire_identite_nom_anonymise (particulier) | 1 |
| titulaire_prenoms_anonymises | 1 |
| titulaire_raison_sociale_anonymisee (personne morale) | 1 |
| titulaire_siren_anonymise | 1 |
| TMU flag (True Mileage Unknown) | 1 |
| TMV national price | 1 |
| tmvRecommendedRating | 1 |
| toegestane_maximum_massa_voertuig | 1 |
| toerental_geluidsniveau | 1 |
| [EQUIP·Confort] Toma de 12 voltios | 1 |
| Top 100 Markets ranking (crecimiento YoY del CMB) | 1 |
| Top bidder | 1 |
| top_features | 1 |
| Top models by CAP Clean | 1 |
| Top models by margin | 1 |
| Top Rated Awards (Car/SUV/Truck + EV + Best of the Best) | 1 |
| Top Sale (Highest Sale) | 1 |
| top_speed_mph | 1 |
| top VC deal trends | 1 |
| topSpeedMPH | 1 |
| torque_derived_from | 1 |
| torque_lbft | 1 |
| torque_nm | 1 |
| torqueRPM | 1 |
| totaal_aantal_voertuigen_terugroepactie | 1 |
| TOTAL | 1 |
| total acquisition cost (WLTP: incl registration + tax) | 1 |
| total_active_cars_for_ymmt | 1 |
| total API method calls per day (laczna-ilosc-wyswietlen) [Statystyki] | 1 |
| Total breakdown: Labour total | 1 |
| Total breakdown: Paint total | 1 |
| Total breakdown: Parts total | 1 |
| Total Car Check valuation | 1 |
| total_cars_sold_in_last_45_days | 1 |
| Total Connections (leads count) | 1 |
| Total cost estimate by zip | 1 |
| Total cost to acquire (buy fee + transporte + recon) | 1 |
| Total cost to acquire (buy fee + transporte + recon) vs retail target | 1 |
| Total cost to bidder (₹) | 1 |
| Total horas de reparación (UTS -> h/min) | 1 |
| Total Listings | 1 |
| Total M.O. | 1 |
| Total M.O. CH/MEC (UT + €) | 1 |
| total number of seats/places (liczba-miejsc-ogolem) | 1 |
| Total piezas (nº + importe) | 1 |
| Total pintura | 1 |
| Total € por operación | 1 |
| total_price | 1 |
| Total Saves (shopper saves count) | 1 |
| Total torque (Nm) | 1 |
| Total Varios | 1 |
| Total-loss recommendation (reparar vs pérdida total) | 1 |
| Total-loss threshold, varies by use (אובדן גמור/להלכה) | 1 |
| Total-loss weighted score (Loss Advisor) | 1 |
| Totale_db | 1 |
| TotaleManoOpera | 1 |
| TotaleRicambi | 1 |
| TotaleTagliando | 1 |
| Totalschaden (flag de siniestro total) | 1 |
| touch-up paint code (mfr code) | 1 |
| Touchscreen | 1 |
| Touchscreen Size | 1 |
| Tow Away Alert | 1 |
| tow_capacity_lb | 1 |
| tow hook / hitch fitted (hak) | 1 |
| tow_status | 1 |
| Towing agency | 1 |
| Towing suggestion (drivable vs needs tow) | 1 |
| town | 1 |
| tracción delantera/trasera/total (traction) | 1 |
| Tracking de pujas en tiempo real / mejor puja | 1 |
| Traction Control | 1 |
| Traction pack diagnostics | 1 |
| trade / wholesale price | 1 |
| Trade Average value (CAP Average) | 1 |
| Trade Below Average value (CAP Below) | 1 |
| Trade Capture report | 1 |
| Trade Clean value (CAP Clean) | 1 |
| Trade destination assignment (trade/subasta/sucursal) | 1 |
| Trade valuation (value excluding margin) | 1 |
| tradeAdverts.price | 1 |
| TradeGrade (point-of-appraisal bid/grade) | 1 |
| trail | 1 |
| trailer attachment type | 1 |
| trailer detail | 1 |
| trailer subtype | 1 |
| trailer type | 1 |
| Trailer Type Connection | 1 |
| Tramos de eslora | 1 |
| Transaccional: Autopago (escrow comprador-vendedor) | 1 |
| Transaccional: CarDelivery (compra 100% online) | 1 |
| Transaccional: Troca+Troco (cambio + diferencia en dinero) | 1 |
| transaction / sales price (dealer, anonymised) | 1 |
| transaction price | 1 |
| Transactions table (30-day sample, up to 100 comparables) | 1 |
| Transactions table - condition | 1 |
| Transactions table - sale date | 1 |
| Transactions table - sale price | 1 |
| Transfer disclosure requirements (app movil) | 1 |
| Transferencias (cambios de titularidad VO) | 1 |
| Transmisión (del VIN) | 1 |
| Transmisión: Número de relaciones/marchas | 1 |
| Transmisión: Tipo de embrague | 1 |
| Transmisión: Tipo de mando | 1 |
| Transmisión: Tipo de mecanismo | 1 |
| Transmisión: Tipo de tracción | 1 |
| Transmissie | 1 |
| Transport cost (en Bill of Sale, floorplanable) | 1 |
| Transport costs | 1 |
| Transport VAT | 1 |
| transportation / delivery (distancia ~600mi / ~7 dias) | 1 |
| Transportation cost | 1 |
| Transportation cost estimate | 1 |
| Trasmissione | 1 |
| Trazione | 1 |
| Trended historic valuation (6 months back) | 1 |
| trending influencer content | 1 |
| Trending Markets por tramo de precio (<$40K, <$100K, $100K–$500K, $500K–$1M, >$1M) | 1 |
| Treno | 1 |
| [EQUIP·Seguridad] Tres reposacabezas traseros | 1 |
| Triage recommendation (total loss vs repairable) | 1 |
| Trigger: auction announcement | 1 |
| Trigger: Buyback Protection eligibility | 1 |
| Trigger: CPO eligibility | 1 |
| Trigger: portfolio analysis | 1 |
| Trigger: vehicle repossession | 1 |
| Trim2 | 1 |
| trimLine | 1 |
| truck age (antiguedad) | 1 |
| truck asset description (descripcion detallada) | 1 |
| Truck class code & name (Class 4-8) | 1 |
| truck detail | 1 |
| truck photos (fotos del activo) | 1 |
| truck salePrice (precio de venta real) | 1 |
| true_cash_offer_valid_3_days | 1 |
| True/Fair market value (IBB) | 1 |
| truecar_price_estimate | 1 |
| trunk_volume | 1 |
| Trust flags (ExtendWarranty / HomeService) | 1 |
| tsb_date | 1 |
| tsb_number | 1 |
| tsb_pdf | 1 |
| tsb_summary | 1 |
| tsb_title | 1 |
| TSN (Typschluesselnummer) | 1 |
| ttl.cityTax | 1 |
| ttl.countyTax | 1 |
| ttl.federalTax | 1 |
| ttl.stateTax | 1 |
| Turbo | 1 |
| Turbo Charger | 1 |
| turn-time goal | 1 |
| turn-time performance (5x vs competidores) | 1 |
| turning_circle | 1 |
| Turning diameter | 1 |
| Turning Radius | 1 |
| Turnover data | 1 |
| Tutela (titular menor de edad / tutela judicial — COD_TUTELA) | 1 |
| tweede_kleur | 1 |
| Tweeters | 1 |
| type | 1 |
| type_approval_category | 1 |
| type_carrosserie_europese_omschrijving | 1 |
| Type d'utilisateur (acheteur/vendeur) | 1 |
| type_de_reception | 1 |
| Type de véhicule | 1 |
| Type de vendeur (Particulier / Professionnel / Pro vérifié) | 1 |
| type designation (typ) | 1 |
| type_gasinstallatie | 1 |
| Type name | 1 |
| type of car (SUV / marca lujo / segmento) | 1 |
| type_remsysteem_voertuig_code | 1 |
| type-subtype-purpose code (kod-rodzaj-podrodzaj-przeznaczenie) | 1 |
| typeaanduidingfabrikant | 1 |
| typegoedkeuringsnummer | 1 |
| Typical Value — National | 1 |
| Typical Value — State | 1 |
| Tyre condition | 1 |
| Tyre condition (%) / tyre life per wheel | 1 |
| Tyre cost | 1 |
| tyre cracked / split flag (perished) | 1 |
| Tyre cross-section (ratio) | 1 |
| Tyre design | 1 |
| Tyre diameter | 1 |
| Tyre load rating | 1 |
| Tyre prices (SMR) | 1 |
| Tyre profile | 1 |
| Tyre replacement timing & cost | 1 |
| Tyre Services (tarifas pactadas) | 1 |
| Tyre Size | 1 |
| Tyre speed index (ECE) | 1 |
| Tyre tread depth (per tyre x 3 points) | 1 |
| tyre tread depth & condition | 1 |
| tyre tread photos (head-on front + back) | 1 |
| Tyre Type | 1 |
| Tyre wall observations (cuts/wear/punctures/canvas) | 1 |
| tyre.construction-type | 1 |
| tyre.front | 1 |
| tyre.front-sizes.aspect-ratio | 1 |
| tyre.front-sizes.radial-construction | 1 |
| tyre.front-sizes.rim-diameter | 1 |
| tyre.rear | 1 |
| tyre.sparewheel-type | 1 |
| tyre.wheel-type | 1 |
| 凹み U1/U2/U3 (dent by size) | 1 |
| Ubicación / país de origen del vehículo | 1 |
| Ubicacion/tracking del vehiculo (ETA) | 1 |
| uitlaatemissieniveau | 1 |
| uitstoot_deeltjes_licht | 1 |
| uitstoot_deeltjes_zwaar | 1 |
| uitvoering | 1 |
| Uitvoering/versie (selección entre coincidencias) | 1 |
| UK car production | 1 |
| ukvd_body_shape | 1 |
| ukvd_mark | 1 |
| ukvd_series_desc | 1 |
| ultimo_prezzo | 1 |
| Umbral de pérdida total (% sobre valor, ~80%) | 1 |
| unbrakedTowingCapacity (sin freno) | 1 |
| Under-body Coating Matrix (UK) | 1 |
| underBodyPhotos / hasUnderBodyPhoto (fotos de bajos) | 1 |
| Undercarriage images | 1 |
| Undercarriage photos (Virtual Lift, 2.000+ fotos del bajo) | 1 |
| underwriting_rating_data (patented) | 1 |
| Unidades en plan / days on plan | 1 |
| unidades producidas (total) | 1 |
| Uniform Condition Adjustment (dealer-ready vs normal-wear) | 1 |
| Universal Condition Report (deducciones/adiciones itemizadas, consumer-facing) | 1 |
| Unnamed issue | 1 |
| up to 6 tracked vehicles (account) | 1 |
| Upcoming car price | 1 |
| updated_at | 1 |
| Updated date (recency) | 1 |
| Upgraded Simulcast (in-app) | 1 |
| Upholstery | 1 |
| uploadSticky | 1 |
| upstream_vehicle (descripción de la autoridad de matriculación) | 1 |
| €uropa-Code / Identify-Code (código de identificación del fabricante) | 1 |
| US: buyback/warranty returns (lemon) | 1 |
| US: current market value / valor de mercado actual | 1 |
| US dismantling shop: scrappage + reporting person | 1 |
| US: GVW (gross vehicle weight) | 1 |
| us_origin_flag | 1 |
| US: safety faults | 1 |
| US title records: issuance date | 1 |
| US title records: state | 1 |
| US use: agricultural | 1 |
| US use: police | 1 |
| US use: taxi | 1 |
| US use: test vehicle | 1 |
| usage_classification_personal_rental_commercial_government | 1 |
| usage_fleet | 1 |
| usage history | 1 |
| usage_lease | 1 |
| usage_livery | 1 |
| usage patterns / vehicle trends | 1 |
| Usage Types | 1 |
| usageType (e.g. CLASSIC) | 1 |
| USB Charger | 1 |
| USB Ports | 1 |
| USD/CNY exchange rate (dated) | 1 |
| Use: Commercial | 1 |
| Use: Fleet | 1 |
| Use: Government | 1 |
| Use: Lease | 1 |
| Use: Personal | 1 |
| Use: Police | 1 |
| Use: Rental | 1 |
| Use: Taxi | 1 |
| used_as_driving_school_vehicle | 1 |
| used_as_handicap_vehicle | 1 |
| used_as_police_vehicle | 1 |
| used_as_rental | 1 |
| used_as_taxi | 1 |
| used_as_transport_vehicle | 1 |
| Used Car Fair Purchase Price | 1 |
| Used car forecast | 1 |
| Used car price | 1 |
| Used car transactions | 1 |
| Used listing: AI Expert condition/price assessment | 1 |
| Used listing: Certified badge | 1 |
| Used listing: Descriptive Summary | 1 |
| Used listing: Featured Indicator | 1 |
| Used listing: Kilometers Driven | 1 |
| Used listing: Original Price | 1 |
| Used listing: Savings Amount | 1 |
| Used listing: Sort (Distance/Added Date/Price/Kms/Year) | 1 |
| Used price (current) | 1 |
| Used vehicle market value (real-time) | 1 |
| Used Vehicle Retention Index (points) | 1 |
| Used Vehicle Retention Index (UVI) value | 1 |
| Used-car market size (units) | 1 |
| used-car market valuation (via autobiz partner) | 1 |
| Used-vehicle performance | 1 |
| usedPrivateParty | 1 |
| User Id (header de auth) | 1 |
| User Operations (name/code/task/job/qty/price/labour time/group) | 1 |
| User Overall Rating (N reviews) | 1 |
| User Ratings and Reviews (de droom.in) | 1 |
| userId | 1 |
| Uso previo (previous usage) | 1 |
| Usuario creador de la valoracion | 1 |
| Vía delantera (mm) | 1 |
| Vía trasera (mm) | 1 |
| V5 document presence (logbook) | 1 |
| V5C (logbook) issue date | 1 |
| v5c_qty | 1 |
| V5C (logbook) serial number | 1 |
| Valet Mode | 1 |
| Valeur Argus Annonces® (displayed-selling-values, prix d'annonce conseillé) | 1 |
| Valeur Argus Transaction® B2B (btob-transaction-values) | 1 |
| Valeur Argus Transaction® B2C (btoc-transaction-values) | 1 |
| Valeur estimée € (cote) | 1 |
| Valeur résiduelle projetée par année (2026-2030) | 1 |
| validación / captura de expediente | 1 |
| validationErrorMessage | 1 |
| validVin | 1 |
| Valor (moto/ciclomotor/quad) | 1 |
| valor actual del vehículo | 1 |
| Valor actual del vehiculo | 1 |
| Valor ajustado por condicion | 1 |
| Valor B2B (trade/wholesale) | 1 |
| Valor B2C (retail profesional a particular) | 1 |
| Valor base Eurotax (ventas reales nacionales mes anterior) | 1 |
| Valor C2C (entre particulares) | 1 |
| valor comercial base (bcpp, miles de COP) | 1 |
| Valor de compra / recompra (trade) | 1 |
| Valor de cotação / valor comercial atualizado (ValCotacao) | 1 |
| Valor de cotação completo, com opcionais (ValCotacaoCompleto) | 1 |
| Valor de la lectura de kilómetros | 1 |
| Valor de mercado a nivel estatal | 1 |
| Valor de mercado a nivel nacional | 1 |
| valor de mercado del vehículo | 1 |
| Valor de mercado real | 1 |
| Valor de mercado VO (precio real de venta profesional→cliente final / retail) | 1 |
| Valor de portfolio / valoracion de flota | 1 |
| Valor de reposición/replacement value | 1 |
| Valor de subasta calculado al céntimo (AUTOonline) | 1 |
| valor de tasación / appraisal | 1 |
| Valor del índice de precios mayorista (puntos, base 100 = ene-2015) | 1 |
| Valor en el pasado (historico) | 1 |
| Valor fijo (código opcional) | 1 |
| valor médio de similares anunciados (above/below market) | 1 |
| Valor Médio Nacional | 1 |
| Valor Network (venta por distribuidores de la marca) | 1 |
| valor (preço médio em R$, à vista, mercado nacional, do mês de referência) — único valor, sem split venda/compra | 1 |
| Valor para comércio e financiamento (contexto legacy) | 1 |
| Valor para consulta/vistoria de sinistro (contexto legacy) | 1 |
| Valor SPOT (oferta VO regional en tiempo real) | 1 |
| valor Tabela Webmotors (precio medio de mercado real de la plataforma) | 1 |
| Valor Venal | 1 |
| valoración a diferentes fechas (retroactiva) | 1 |
| Valoración cross-border por mercado (22 mercados) | 1 |
| Valoración del vehículo usado (Boletín Blanco) | 1 |
| Valoración Euro NCAP (estrellas) | 1 |
| valoración masiva / por lotes (stock) | 1 |
| valoración pre / intermedia / post-proceso | 1 |
| Valoración VO de vehículos >12 años | 1 |
| Valoracion actualizada al final de contrato | 1 |
| Valoracion de equipamiento/extras (depreciacion de opciones) | 1 |
| Valoracion en tiempo real | 1 |
| valoraciones acumuladas (prueba social: 22.578.926 PPP desde 2018; 1M+ requests InstantVal desde 2018) | 1 |
| Valore commerciale veicolo attuale (lead) | 1 |
| Valore di permuta (trade-in) | 1 |
| Valore residuo accessori non di serie | 1 |
| Valore veicolo all'ultimo passaggio di proprieta | 1 |
| ValoreAcquisto | 1 |
| ValoreAssoluto | 1 |
| ValoreAtto | 1 |
| ValoreCasa | 1 |
| ValoreInstantWeb | 1 |
| ValorePercentuale | 1 |
| Valores de referencia de mercado | 1 |
| ValoreVendita | 1 |
| Valori residui degli accessori | 1 |
| Valori residui vs listini attuali/storici | 1 |
| Valori storici Eurotax (serie historica desde 2000) | 1 |
| valorization.input.business-target (btoc/btob) | 1 |
| valorization.input.calculated-for (fecha de cálculo / cote a fecha pasada) | 1 |
| valorization.input.feature-ids | 1 |
| valorization.input.offer (extended-market-values / past-stock-market-value / personnalisée / frais percent|fixed) | 1 |
| valorization.input.released-at (mise en circulation) | 1 |
| Valuador input alterno: Matrícula | 1 |
| Valuador input: Potência (opcional) | 1 |
| Valuador input: Quilometragem | 1 |
| Valuador input: Tipo de carroçaria | 1 |
| Valuador input: Tipo de combustível | 1 |
| Valuador input: Versão / Motorização | 1 |
| Valuador: intervalo de preços estimado (rango €, ej. EUR 26.140 - EUR 31.050) | 1 |
| Valuation amountExcludingVatGBP | 1 |
| Valuation amountGBP | 1 |
| Valuation amountNoVatGBP (commercial/VI) | 1 |
| Valuation certificate | 1 |
| Valuation date | 1 |
| valuation_input_condition | 1 |
| Valuation Input: Kilometers driven | 1 |
| Valuation Input: Overall condition | 1 |
| valuation_input_state | 1 |
| valuation_mode_buying | 1 |
| valuation_mode_selling | 1 |
| valuation_mode_trading_in | 1 |
| Valuation Notes (appraiser + system) | 1 |
| Valuation ratio (repair cost / value) | 1 |
| Valuation Total (Actual Cash Value / ACV) | 1 |
| valuation.auctionValue | 1 |
| valuation.created_at | 1 |
| valuation.historicalValue | 1 |
| valuation.kms | 1 |
| valuation.loanValue | 1 |
| valuation.price | 1 |
| valuation.pricing_id | 1 |
| valuation.retailValue | 1 |
| valuation.score (confidence 0-1) | 1 |
| valuation.wholesaleValue | 1 |
| valuationType (Auction | Fixed Price | Pickles Go Tenders | Pickles Online | Dealer Retail | Private Retail | Wholesale | Trade In | Wholesale Buy Price) | 1 |
| value (importe €) | 1 |
| value_adjustment_title_brands | 1 |
| value_adjustment_usage_type | 1 |
| Value factors (factores que aumentan/disminuyen valor — B2B) | 1 |
| Value Index (retail vs MSRP) | 1 |
| Value movement reason / which derivative moved | 1 |
| Value scenario: Buying Privately | 1 |
| Value scenario: Selling Privately | 1 |
| Value scenario: Trading In (with tax savings factored in) | 1 |
| value through equipment changes | 1 |
| value_tracking_over_time | 1 |
| Value trend / direccion (sube o baja) | 1 |
| value-chain position (leader / challenger) | 1 |
| Value-retention rating (3-year) | 1 |
| Valutazione_generica | 1 |
| Valutazione retrodatata (valore a fecha pasada, 2008/2011/2015 segun producto) | 1 |
| Valutazione_specifica | 1 |
| Valutazione veicolo in permuta | 1 |
| valve_gear | 1 |
| valve_timing | 1 |
| Valve Train Design | 1 |
| valves | 1 |
| ValvolePerCilindro | 1 |
| Variação de preço mensual % (0km / seminovo / usado) | 1 |
| Variação por idade (por ano modelo) | 1 |
| Variable cost | 1 |
| Variables macroeconomicas | 1 |
| variación % del comercio exterior (mensual/semestral/anual) | 1 |
| Variación acumulada en el año del índice (YTD %) | 1 |
| Variación interanual del índice (YoY %) | 1 |
| variación interanual del precio (%) | 1 |
| Variación mes a mes del índice (MoM %) | 1 |
| Variacion de VR por periodo | 1 |
| Variacion interanual de precio % (Car Digital Track) | 1 |
| Variazione valutazioni MoM (mensile) | 1 |
| Variazione valutazioni YoY (annuale) | 1 |
| VAT amount | 1 |
| VAT flag (UK) | 1 |
| VAT-inclusive valuation flag | 1 |
| vatable | 1 |
| vatMargin (BTW/marge) | 1 |
| vatNumber | 1 |
| vatRate | 1 |
| VDP views / engagement (+62% VDPs/coche) | 1 |
| VED cost for 12 months | 1 |
| Veh Adj (vehicle-description difference adjustment) | 1 |
| vehículo afectado (VIN / matrícula) | 1 |
| vehículo eléctrico (matrícula/VIN) | 1 |
| Vehículos comparables | 1 |
| vehículos totales transportados (logística) | 1 |
| Vehicle Affordability Index (semanas de ingreso medio para comprar) | 1 |
| Vehicle age / antiguedad | 1 |
| vehicle age distribution | 1 |
| Vehicle age mix (4-7yr share) | 1 |
| Vehicle archive photos / fotos historicas | 1 |
| Vehicle Aspect (grouping + vehicle count) | 1 |
| Vehicle assessment description | 1 |
| Vehicle attractiveness (atractividad del vehículo) | 1 |
| Vehicle Base Price (typical, market-specific) | 1 |
| Vehicle category/body — private/commercial/truck/bus/minibus/van/tow-truck/taxi | 1 |
| vehicle class M2/M3 (bus/coach) | 1 |
| vehicle class N1 (LCV/van) | 1 |
| vehicle class N2 (medium goods) | 1 |
| vehicle class N3 (heavy truck) | 1 |
| Vehicle condition / condition report | 1 |
| Vehicle condition tier (Below average / Average / Clean) | 1 |
| Vehicle data source (source / vehicle_source) | 1 |
| vehicle_description_pros_cons | 1 |
| Vehicle Descriptor | 1 |
| Vehicle desirability indicator | 1 |
| vehicle_detail_page_views | 1 |
| Vehicle Detail Pages (VDP) | 1 |
| Vehicle details (make/model/colour/engine/year/fuel) | 1 |
| vehicle details score | 1 |
| Vehicle disposition (SOLD/CRUSHED/TO BE DETERMINED) | 1 |
| Vehicle execution | 1 |
| Vehicle history — AutoCheck summary | 1 |
| Vehicle history — CarFax summary | 1 |
| vehicle_history_report_carfax_or_autocheck | 1 |
| Vehicle History Report (title, accidents, odometer, owners) via AutoCheck | 1 |
| Vehicle history timeline (manufacture to present) | 1 |
| Vehicle hotness / profit opportunity ranking | 1 |
| vehicle_id (AGID, AutoGrab ID canónico, color-agnóstico) | 1 |
| Vehicle image | 1 |
| Vehicle images (up to 20 interior/exterior compositions) | 1 |
| Vehicle intake | 1 |
| Vehicle Intelligence 360 (listing IA generativa + datos completos) | 1 |
| Vehicle Journey (ventas previas + actividad subasta + registros de servicio) | 1 |
| vehicle lifecycle charts | 1 |
| Vehicle lookup valuation (by VRM) | 1 |
| Vehicle of interest VOI (type new/cpo/used + YMM/VIN/stock/odometer) | 1 |
| vehicle origin / provenance (pochodzenie-pojazdu) | 1 |
| vehicle_passport_information | 1 |
| vehicle path (classic used / rental / daily registration) | 1 |
| Vehicle pedigree (rasgo del score) | 1 |
| vehicle plants (footprint) | 1 |
| Vehicle Prep / Pre-Titling event | 1 |
| vehicle purpose / intended use (przeznaczenie-pojazdu) | 1 |
| vehicle_recovered | 1 |
| Vehicle release/exit | 1 |
| vehicle_repossessed_flag | 1 |
| Vehicle reservation (reserva de vehículo) | 1 |
| vehicle sales history (Cross-Sell) | 1 |
| Vehicle Score severity band (Non-Repairable/Severe/Major/Moderate/Minor/Little) | 1 |
| Vehicle sold by insurer | 1 |
| vehicle_source_id | 1 |
| Vehicle Stability Control | 1 |
| vehicle_status | 1 |
| Vehicle status tags | 1 |
| Vehicle style | 1 |
| vehicle_summary (AI-generated) | 1 |
| vehicle_taxation_class | 1 |
| Vehicle technology details | 1 |
| Vehicle title doc type | 1 |
| Vehicle type code | 1 |
| Vehicle usage (history factor) | 1 |
| vehicle_usage_type (personal/lease/corporate-fleet/rental/taxi/police/commercial/government) | 1 |
| Vehicle usage type / fleet-rental-personal (HAV input) | 1 |
| Vehicle valuation trends (wholesale/retail) | 1 |
| vehicle_wheelbase_mm | 1 |
| vehicleAgeInMonths (rango 6-120) | 1 |
| vehicleClass | 1 |
| vehicleDescription (descripcion del vehiculo) | 1 |
| vehicleIdName (RedbookCode | GlassesCode | RegistrationPlate | VIN) | 1 |
| vehicleIdValue (identificador del vehiculo) | 1 |
| vehicleNo / 차량번호 (matrícula) | 1 |
| vehicles in operation (PARC) annual count | 1 |
| vehicles-in-operation (VIO/PARC) count | 1 |
| vehicleStatusMessage (stolen/scrapped/exported marker) | 1 |
| vehicleTarget (destino del vehículo) | 1 |
| vehicleType (turismo/moto/comercial/camper) | 1 |
| vehicule_a_usage_agricole | 1 |
| vehicule_a_usage_de_collection | 1 |
| vehicule_declare_vole (FOVeS) | 1 |
| VeicoliCommerciali | 1 |
| VeicoloIbrido | 1 |
| Veilingprijs | 1 |
| [MED·Prueba] Velocidad de la prueba de esquiva / moose test (km/h) | 1 |
| Velocidad máxima (km/h) | 1 |
| VelocitaMax | 1 |
| VenditaAssoluta | 1 |
| VenditaPerc | 1 |
| VenditaPercListino | 1 |
| VenditaPercPAC | 1 |
| Venditore | 1 |
| verbod_voor_rijden_op_de_weg (OVI, prohibicion de circular) | 1 |
| Verbundarbeiten (trabajos combinados) | 1 |
| Verbundmaterialanzeige (indicacion de material compuesto) | 1 |
| Verificación de valoración por reglas paramétricas (AudaCheck) | 1 |
| verificador autonómico (CCAA) | 1 |
| Verkäufertyp (dealer vs private) | 1 |
| Verkoop door een particulier | 1 |
| Verkoopwaarde / sales value (con y sin IVA) | 1 |
| verlengde_cabine_indicator | 1 |
| Vermogen (kW) | 1 |
| vermogen_massarijklaar (relacion potencia/masa) | 1 |
| Versión exacta | 1 |
| Verteilung Preise (price distribution chart) | 1 |
| verticale_belasting_koppelpunt_getrokken_voertuig | 1 |
| vervaldatum_apk | 1 |
| vervaldatum_keuring (APK) | 1 |
| vervaldatum_tachograaf | 1 |
| VFACTS build data | 1 |
| VFACTS paint data | 1 |
| VHR summary: Last Registered Province | 1 |
| VHR summary: U.S. History indicator | 1 |
| VI Data: 360-degree images | 1 |
| VI Data: 6 high-resolution images con hotspots | 1 |
| VI Data: Diagnostic Trouble Codes (DTC/OBD-II) | 1 |
| VI Data: High-value features highlighted | 1 |
| VI Data: Mechanical condition observations (ruido/transmisión/fugas/escape) | 1 |
| video | 1 |
| Video count | 1 |
| Video reviews | 1 |
| videos HD (视频) | 1 |
| videoUrl | 1 |
| vidrios eléctricos (electricGlasses) | 1 |
| vielversprechender Bestand (promising inventory) | 1 |
| View count (visibility) | 1 |
| viewCount (visitas) | 1 |
| Views (listing analytics) | 1 |
| Vignette Crit'Air (niveau) | 1 |
| Vincoli/constraints di pacchetti accessori | 1 |
| VINCUE Value Rank (proprietary dynamic algorithmic grade) | 1 |
| VINguard previous sales | 1 |
| VINguard vehicle title information | 1 |
| vinProcessed | 1 |
| vinSubmitted | 1 |
| VinTel OBD-II diagnostic report (technical condition) | 1 |
| VIO (Vehicles in Operation) | 1 |
| Visão 360º (foto + vídeo) | 1 |
| Visibilidad: % uplift de vistas por tier (+70% / +120% / +230%) | 1 |
| Visibilidad / posicionamiento de stock | 1 |
| Visibilidad: Super Ad | 1 |
| Visibilidad: To Top (subir a lo alto, ×2/×3/×4 por tier) | 1 |
| Visibilidad: Top Potencies | 1 |
| Visibilidad: Top Stand (20.000 impresiones) | 1 |
| VistaFoto | 1 |
| Vistoria: acessórios e extras | 1 |
| Vistoria: chapa suporte | 1 |
| Vistoria: condição do chassi nos vidros (parabrisa / portas / vigia) | 1 |
| Vistoria: data de vistoria | 1 |
| Vistoria: documentação / modificação no CRLV | 1 |
| Vistoria: estrutura veicular (pontos estruturais da carroceria) | 1 |
| Vistoria: ETA's (etiquetas autodestrutíveis: motor / batente porta / assoalho) | 1 |
| Vistoria: gravação do chassi | 1 |
| Vistoria: histórico de leilão | 1 |
| Vistoria: histórico de roubo/furto | 1 |
| Vistoria: histórico de sinistro | 1 |
| Vistoria: indicações de reparo | 1 |
| Vistoria: nº câmbio (BIN / veículo) | 1 |
| Vistoria: nº chassi (BIN / veículo / documento) | 1 |
| Vistoria: nº laudo | 1 |
| Vistoria: numeração do câmbio | 1 |
| Vistoria: numeração identificadora do chassi | 1 |
| Vistoria: placa | 1 |
| Vistoria: placa dianteira | 1 |
| Vistoria: placa traseira | 1 |
| Vistoria: RENAVAM | 1 |
| Visual Boost AI: overlay de daño exterior sobre 8 imagenes a 45 grados | 1 |
| Visual Boost AI: tipos de daño detectados (hail, paint peel, detached panels, broken lights, rust, scratches, dents, cracks) | 1 |
| Visual Boost AI: toggle on/off del comprador | 1 |
| Vitesse max (km/h) | 1 |
| vitesse_moteur_regime_min-1 (U.2) | 1 |
| vname | 1 |
| VO Certificado/CPO | 1 |
| VOC (Voice of Customer) | 1 |
| voertuigklasse (bus M2/M3: I/II/III, A/B) | 1 |
| voertuigklasse_omschrijving | 1 |
| voertuigsoort (tipo de vehiculo) | 1 |
| Volúmenes de stock (Cockpit) | 1 |
| [EQUIP·Seguridad] Volante con ajuste horizontal | 1 |
| [EQUIP·Seguridad] Volante con ajuste vertical | 1 |
| [EQUIP·Decoración] Volante con calefacción | 1 |
| [EQUIP·Decoración] Volante de cuero | 1 |
| volgnummer_wijziging_eu_typegoedkeuring | 1 |
| Vollmachten (poderes) | 1 |
| Voltaggio (EV) | 1 |
| Volume du coffre | 1 |
| Volume du réservoir (L) | 1 |
| Volume planning [RV driver] | 1 |
| Volumen de transacciones VO (censo real) | 1 |
| Volumen del segundo maletero (l) | 1 |
| volumen logístico - número de camiones | 1 |
| volumen logístico - número de trenes | 1 |
| volumen logístico - vehículos por puerto/barco | 1 |
| Volumen mínimo de maletero con dos filas (l) | 1 |
| volumen por tramo de antigüedad (unidades) | 1 |
| [MED·Maletero] Volumen VDA (l) | 1 |
| Évolution du prix (courbe de dépréciation future) | 1 |
| VPM: auto-consign tracking | 1 |
| VPM: centralized payment/settlement | 1 |
| VPM: In-service vehicle tracking (driver/mileage/location) | 1 |
| VPM: online remarketing | 1 |
| VPM: real-time vehicle status | 1 |
| VPM: transportation quote tracking | 1 |
| VPM: vehicle grounding | 1 |
| VR por mercado/pais | 1 |
| vRank (via conexion Provision) [RECONSTRUIDO] | 1 |
| vRank — posicion competitiva ponderando equipamiento y odometro | 1 |
| vSquare (recalculo en vivo de appraisal amount/profit objective/price rank/posicion) | 1 |
| vulnerable_road_user_protection_score | 1 |
| 補修・板金 W1/W2/W3 (repaint/repair quality) | 1 |
| wacht_op_keuren | 1 |
| Waiting Period | 1 |
| wam_verzekerd (seguro WAM) | 1 |
| Warning light ABS | 1 |
| Warning light AC | 1 |
| Warning light airbag | 1 |
| Warning light brake | 1 |
| Warning light SRS | 1 |
| Warning light suspension fault | 1 |
| Warning light TPMS | 1 |
| Warning light traction control | 1 |
| Warning lights (general) | 1 |
| Warning lights / dashboard lights | 1 |
| warranty | 1 |
| warranty_basic | 1 |
| warranty_check | 1 |
| warranty_corrosion | 1 |
| Warranty coverage (comparador) | 1 |
| Warranty Coverage Details (term/miles) | 1 |
| Warranty coverage status (active/expired) | 1 |
| Warranty Coverage Type (Basic/Battery/Corrosion/Powertrain/Roadside Assistance/Safety Restraint) | 1 |
| Warranty expiration | 1 |
| Warranty info | 1 |
| Warranty information | 1 |
| warranty miles | 1 |
| warranty months | 1 |
| warranty name | 1 |
| Warranty program validation | 1 |
| Warranty Remaining Miles | 1 |
| Warranty Remaining Time | 1 |
| warranty_roadside_assistance | 1 |
| Warranty transferability | 1 |
| warranty.anti-corrosion.years | 1 |
| warranty.basic | 1 |
| warranty.companyName | 1 |
| warranty.corrosionPerforation | 1 |
| warranty.maintenance | 1 |
| warranty.manufacturer.years | 1 |
| warranty.roadside | 1 |
| Waste EPA Charge (oil/tyres/other) | 1 |
| Watchlist / personal notes | 1 |
| Watchlist flag (seguir vehiculo) | 1 |
| wear and tear declaration (mandatory) | 1 |
| Wear part costs | 1 |
| weekly_value_update | 1 |
| weggedrag_code (suspension L/G/A) | 1 |
| Weighted/calculated online price (מחיר משוקלל) | 1 |
| Weiterempfehlungsrate (recommendation rate) | 1 |
| well_maintained_indicator | 1 |
| Werbemanager social reach (Instagram/Facebook) | 1 |
| Wettbewerbsposition / Preis-Ranking-Position (competitive position) | 1 |
| Wettbewerbspreise (competitor prices) | 1 |
| wettelijk_toegestane_maximum_aslast | 1 |
| What Others Have Paid (precios de transacciones comparables) | 1 |
| what-if scenario (EV adoption / policy / tariff / disruptive tech) | 1 |
| Wheel Base | 1 |
| Wheel Covers | 1 |
| wheel_dia | 1 |
| Wheel scratches / corrosion | 1 |
| Wheel Size Front (inches) | 1 |
| wheel_size_inches | 1 |
| Wheel Size Rear (inches) | 1 |
| wheel_tightening_torque | 1 |
| wheel track of steered and other axles (rozstaw-kol-osi-kierowanej-pozostalych-osi) | 1 |
| wheel_type | 1 |
| Wheelbase (inches) From | 1 |
| Wheelbase (inches) To | 1 |
| wheelbaseMM | 1 |
| wheelFormula | 1 |
| Wheelie Mitigation | 1 |
| white/transparent background | 1 |
| Whole life cost | 1 |
| Whole-of-market valuation | 1 |
| Wholesale flag | 1 |
| Wholesale Hub (holding wholesale + envio bulk a subasta) | 1 |
| Wholesale price | 1 |
| Wholesale price - Above | 1 |
| Wholesale price - Average | 1 |
| Wholesale price - Below | 1 |
| Wholesale sales (units) | 1 |
| Wholesale valuation | 1 |
| Wholesale/Retail Spread | 1 |
| widthMM | 1 |
| wielbasis | 1 |
| wielbasis_ondergrens_bovengrens | 1 |
| wijze_waarop_u_wordt_geinformeerd | 1 |
| Window sticker base price | 1 |
| window_sticker_data | 1 |
| window_sticker_info | 1 |
| Windows | 1 |
| windshield_features_rain_sensor_lane_departure | 1 |
| Wiper arm movement (front/rear) | 1 |
| Withdrawn Vehicles | 1 |
| 续航 WLTC | 1 |
| WLTP examinationDate / validUntil | 1 |
| WLTP values (per configuration) | 1 |
| WltpProvider | 1 |
| WMI code | 1 |
| WMI Date Available To Public | 1 |
| wmiCountry | 1 |
| wmiManufacturer | 1 |
| WOK status | 1 |
| WorldManufacturerIdentifier (WMI) | 1 |
| written_off_check | 1 |
| Written valuation report (B2B) | 1 |
| Written-Off History | 1 |
| Written-off vehicle assessment | 1 |
| WTF scores (Lotpop integration) | 1 |
| Yard name | 1 |
| Yard number | 1 |
| YearGroupId | 1 |
| your_price_net_after_incentives | 1 |
| YoY change (%) | 1 |
| Z-Moto (motocicletas, mano de obra media) | 1 |
| Zeitwert (valor temporal/depreciado) | 1 |
| zeroToOneHundredKMPHSeconds | 1 |
| zeroToSixtyMPHSeconds | 1 |
| zip | 1 |
| zip_code_localization | 1 |
| zip-code performance (Cross-Sell) | 1 |
| ZIP-level media opportunity | 1 |
| zuinigheidsclassificatie (etiqueta energetica A-G) | 1 |
| Zustandskriterien (criterios de estado/condicion) | 1 |