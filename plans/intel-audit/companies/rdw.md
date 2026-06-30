# Auditoría atómica — RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Autoridad oficial del vehículo de los Países Bajos. Web: https://www.rdw.nl · Portal de datos: https://opendata.rdw.nl
> Subdominio (taxonomía Cardeep): **official-data** (fuente de verdad oficial / registro estatal, no valoración ni marketplace).
> Fecha auditoría: 2026-06-30.
> Método: (1) extracción de la **metadata cruda Socrata** de ~25 datasets vía `api/views/{id}.json` y del **catálogo completo** (`api/catalog/v1`, 206 entradas); (2) consultas en vivo a la **SODA API** (`/resource/{id}.json` con SoQL `$select/$group/$where`) para conteos de cobertura, valores de dominio y filas de tarifa reales; (3) **render EN VIVO con Playwright** de la herramienta oficial per-matrícula **OVI / RDW Kentekencheck** (`ovi.rdw.nl`) con matrícula real NL `H-804-XS` (VOLKSWAGEN GOLF, Diesel, 2017) — 3 de 4 pestañas capturadas a nivel de campo; (4) páginas corporativas RDW (NL/EN) + Wikipedia.
> Convención: **[V]** = verificado leyendo/observando la fuente · **[A]** = asumido/inferido/tercero (siempre marcado).
> Nota de entorno: la pestaña **Fiscaal** de OVI no se capturó a nivel de etiqueta porque el **navegador compartido fue redirigido por otro proceso** (a `repuve.gob.mx`) a mitad del recorrido; los campos fiscales se derivan del **modelo de datos verificado** del registro (catalogusprijs, bruto_bpm, afschrijvingsmoment BPM, zuinigheidsclassificatie) y se marcan como tales, sin inventar las cadenas exactas de la UI.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre | **RDW** (sigla histórica de *Rijksdienst voor het Wegverkeer*); razón jurídica actual **Dienst Wegverkeer**; nombre internacional **Netherlands Vehicle Authority** | [V] |
| Tipo de organización | **ZBO** — *zelfstandig bestuursorgaan* (organismo administrativo autónomo de derecho público), bajo supervisión del **Ministerie van Infrastructuur en Waterstaat** (Infraestructura y Gestión del Agua) | [V] |
| Fundación | **1 de septiembre de 1949** (fusión del Servicio Técnico de la Rijksverkeersinspectie + Bureau Inschrijvingen Motorrijtuigen en Aanhangwagens de Rijkswaterstaat) | [V] |
| Conversión a ZBO | **1 de enero de 1996** (Wet zelfstandige bestuursorganen) → autonomía operativa con tutela ministerial | [V] |
| HQ | **Zoetermeer** (Europaweg 205, 2711 ER, Zuid-Holland); 2º centro en **Veendam** (Skagerrak 10, 9642 CZ) | [V] |
| Oficinas exteriores | **Detroit (Michigan, EE.UU.)** y **Seúl (Corea del Sur)** — soporte a fabricantes para homologación europea | [V] |
| Plantilla | **~1.999 empleados** (fuente tercera ZoomInfo; orden de magnitud ~2.000) | [A/tercero] |
| Misión | *"Veiligheid, duurzaamheid en rechtszekerheid in mobiliteit"* (seguridad, sostenibilidad y seguridad jurídica en la movilidad); *"publieke dienstverlener in de mobiliteitsketen"* | [V] |
| Hitos | 2004 designado **EU notified body** para homologación de tipo; 2014 sustitución del kentekenbewijs de papel por la **Kentekencard** con chip; 2019 lanzamiento del *Self Driving Challenge* | [V] |

### Las 4 tareas estatutarias (statutory tasks) [V]
1. **Toelating / Type-approval & licensing** — admisión y homologación de tipo de vehículos y de partes para el mercado neerlandés y europeo. RDW es de los notified bodies más usados por fabricantes extranjeros (poca competencia industrial doméstica).
2. **Toezicht & controle / Supervisión** — supervisión de empresas erkend (talleres, fabricantes de placas, etc.) y vigilancia del estado técnico vía **APK** (ITV neerlandesa).
3. **Registratie & informatie / Registro e información** — *"gathering, storing, updating and managing data concerning vehicles, their owners and vehicle documentation and providing information about this data to interested parties"*. Mantiene el **kentekenregister** (Basisregistratie Voertuigen) y lo publica como **open data**.
4. **Documentafgifte / Emisión de documentos** — Kentekencard (permiso de circulación con chip), permiso de conducir físico (vale como DNI en NL), formularios APK.

### Clientes / usuarios objetivo [V/A]
- **Reutilizadores de datos / mercado** (núcleo de open data): desarrolladores, fabricantes de software automoción, aseguradoras, leasing, portales (p.ej. **Autotelex**, **ANWB**, kentekencheck.nl, rdwdata.nl) construyen productos sobre los datos RDW. [V — RDW declara el objetivo de *"dat de markt eigen producten en diensten kan ontwikkelen op basis van betrouwbare voertuiggegevens"*]
- **Ciudadanos**: consulta per-matrícula gratuita vía OVI/Kentekencheck (APK, recalls, tellerstand, status). [V]
- **Empresas erkend (zakelijk)**: acceso autenticado ampliado ("Inloggen zakelijk" en OVI) y servicios de registro/tenaamstelling de pago (Kentekenloket). [V — botón observado / tarifas en Producten Catalogus]
- **Gobierno y terceros oficiales**: Belastingdienst (BPM/MRB se apoyan en datos RDW), policía, municipios (parkeren). [A/contexto]

---

## 2. Cobertura

### Geográfica [V]
- **Países Bajos** exclusivamente (registro nacional de matrículas / kenteken). Las matrículas extranjeras no se admiten en OVI (*"alleen Nederlandse kentekens toegestaan"*). RDW actúa además como notified body de homologación con efecto **UE**, pero el **registro de vehículos** es nacional NL.

### Volumen (verificado en vivo, SODA API, dataset `m9d7-ebf2`) [V]
- **16.813.330** registros de vehículos matriculados en el registro nacional.
- Desglose por `voertuigsoort` (tipo de vehículo):

| Tipo | Recuento |
|---|---|
| Personenauto (turismo) | 10.771.498 |
| Bedrijfsauto (comercial/furgoneta) | 1.509.697 |
| Bromfiets (ciclomotor) | 1.373.389 |
| Motorfiets (motocicleta) | 893.007 |
| Aanhangwagen (remolque) | 773.816 |
| Middenasaanhangwagen (remolque eje central) | 426.915 |
| Land-/bosbouwtrekker (tractor agrícola) | 356.607 |
| Land-/bosb aanhw of getr uitr (equipo agrícola arrastrado) | 268.956 |
| Oplegger (semirremolque) | 220.178 |
| Motorrijtuig met beperkte snelheid (vehículo velocidad limitada) | 114.256 |
| Driewielig motorrijtuig (triciclo motor) | 42.279 |
| Mobiele machine (máquina móvil) | 34.745 |
| Bus | 12.397 |
| Autonome aanhangwagen | 9.377 |
| Motorfiets met zijspan (moto con sidecar) | 6.213 |

### Scope de vehículos [V]
- **Todos los tipos** (turismo, comercial, moto, ciclomotor, bus, remolque/semirremolque, tractor agrícola, maquinaria, vehículos con orugas/rupsbanden). No se limita a turismos.
- **Nuevo y usado**: el registro cubre todo el ciclo de vida (alta `datum_eerste_toelating`, importación `datum_eerste_tenaamstelling_in_nederland`, cambios de titularidad, exportación `export_indicator`, baja).
- Identificación por **kenteken** (matrícula). El **VIN/chassisnummer** NO se publica en open data; sí su **ubicación** (`plaats_chassisnummer`). [V]
- Histórico parcial: nº de propietarios (solo en OVI), histórico de tellerstand (juicio agregado), histórico APK (meldingen), recalls.

---

## 3. Productos + campos atómicos

RDW no es un "producto" comercial único: es un **registro estatal expuesto como familias de datasets open data (Socrata)** + una **herramienta de consulta per-matrícula (OVI)** + **servicios de registro de pago**. A efectos de Cardeep, cada **dataset = un feed/producto** con su lista atómica de campos. Todos los campos de abajo están **verificados leyendo la metadata Socrata [V]**; las descripciones citadas son las oficiales del data dictionary RDW cuando existen.

> Patrón de unión: todos los datasets de vehículo se enlazan por **`kenteken`**; los de homologación por **`typegoedkeuringsnummer` + codes de variante/uitvoering**; los de recall por **`referentiecode_rdw`**. El dataset insignia incluye columnas `api_*` que son **deep-links REST a los sub-datasets** (assen, brandstof, carrosserie, voertuigklasse) → patrón de "expansión bajo demanda".

### 3.1 PRODUCTO ESTRELLA — `Gekentekende_voertuigen` (m9d7-ebf2) · cat. Voertuigen · **98 columnas** [V]
Registro base del vehículo (1 fila por matrícula). Campos atómicos:

**Identidad / homologación:** kenteken · voertuigsoort · merk · handelsbenaming · type · variant · uitvoering · typegoedkeuringsnummer · volgnummer_wijziging_eu_typegoedkeuring · europese_voertuigcategorie (+ toevoeging) · europese_uitvoeringcategorie_toevoeging · subcategorie_nederland · inrichting · plaats_chassisnummer · aanwijzingsnummer.

**Carrocería / dimensiones:** eerste_kleur · tweede_kleur · aantal_deuren · aantal_wielen · aantal_zitplaatsen · aantal_staanplaatsen · aantal_rolstoelplaatsen · aantal_passagiers_zitplaatsen_wettelijk · lengte (+ min/max) · breedte (+ min/max) · hoogte_voertuig (+ min/max) · wielbasis (+ min/max) · verl_cab_ind (cabina extendida) · aerodyn_voorz (aerodinámica).

**Masas / capacidades:** massa_ledig_voertuig · massa_rijklaar · toegestane_maximum_massa_voertuig · technische_max_massa_voertuig (+ min/max) · maximum_massa_samenstelling · massa_bedrijfsklaar_min/max · maximum_massa_trekken_ongeremd · maximum_trekken_massa_geremd · oplegger_geremd · aanhangwagen_autonoom_geremd · aanhangwagen_middenas_geremd · laadvermogen · gem_lading_wrde · massa_alt_aandr (masa adicional propulsión alternativa) · maximum_last_onder_de_vooras_sen_tezamen_koppeling · technisch_toelaatbaar_massa_koppelpunt · verticale_belasting_koppelpunt_getrokken_voertuig · afstand_hart_koppeling_tot_achterzijde · afstand_voorzijde_tot_hart_koppeling.

**Motor / prestaciones:** aantal_cilinders · cilinderinhoud · vermogen_massarijklaar (relación potencia/masa) · maximale_constructiesnelheid · afwijkende_maximum_snelheid · maximum_ondersteunende_snelheid (e-bike/speed-pedelec) · type_gasinstallatie · type_remsysteem_voertuig_code · rupsonderstelconfiguratiecode.

**Fechas / vencimientos / titularidad:** datum_eerste_toelating · datum_eerste_tenaamstelling_in_nederland · datum_tenaamstelling · vervaldatum_apk · vervaldatum_tachograaf · registratie_datum_goedkeuring (**afschrijvingsmoment BPM** = momento de depreciación fiscal) — todos con espejo `_dt` calendar_date.

**Fiscal / económico:** **catalogusprijs** (precio de catálogo/nuevo) · **bruto_bpm** (impuesto de matriculación bruto) · **zuinigheidsclassificatie** (etiqueta energética A–G).

**Estado / flags:** wam_verzekerd (seguro WAM) · export_indicator · **openstaande_terugroepactie_indicator** (recall abierto) · taxi_indicator · wacht_op_keuren · tenaamstellen_mogelijk.

**Antifraude cuentakilómetros (NAP):** **tellerstandoordeel** (juicio: *Logisch / Onlogisch / Geen oordeel / Niet geregistreerd*) · code_toelichting_tellerstandoordeel · jaar_laatste_registratie_tellerstand.

**Type-approval bounds:** wielbasis/lengte/breedte/hoogte/massa min–max (rangos de homologación). · API-links: api_gekentekende_voertuigen_{assen,brandstof,carrosserie,carrosserie_specifiek,voertuigklasse}.

### 3.2 `Gekentekende_voertuigen_brandstof` (8ys7-d773) · **36 columnas** [V] — Combustible, consumo, emisiones, eléctrico
brandstof_omschrijving · brandstof_volgnummer · **brandstofverbruik_gecombineerd** (NEDC, l/100km) · brandstof_verbruik_gecombineerd_wltp · brandstof_verbruik_gewogen_gecombineerd_wltp · brandstofverbruik_gewogen_gecombineerd · **co2_uitstoot_gecombineerd** · co2_uitstoot_gewogen · emissie_co2_gecombineerd_wltp · emis_co2_gewogen_gecombineerd_wltp · **co2_emissieklasse** · emissiecode_omschrijving (Emissieklasse) · uitlaatemissieniveau · milieuklasse_eg_goedkeuring_licht · milieuklasse_eg_goedkeuring_zwaar · uitstoot_deeltjes_licht (g/km) · uitstoot_deeltjes_zwaar (g/kWh) · emis_deeltjes_type1_wltp · geluidsniveau_stationair (dB(A)) · geluidsniveau_rijdend · toerental_geluidsniveau · nettomaximumvermogen (kW) · nominaal_continu_maximumvermogen · netto_max_vermogen_elektrisch · max_vermogen_15_minuten · **elektrisch_verbruik_enkel_elektrisch_wltp** · elektriciteitsverbruik_volledig_elektrisch · elektriciteitsverbruik_gewogen_gecombineerd · elektrisch_verbruik_extern_opladen_wltp · **actie_radius_enkel_elektrisch_wltp** (autonomía EV) · actieradius · actie_radius_extern_opladen_wltp · actieradius_extern_oplaadbaar · **klasse_hybride_elektrisch_voertuig** (OVC-HEV/NOVC-HEV/OVC-FCHV/NOVC-FCHV) · opgegeven_maximum_snelheid.

### 3.3 `Gekentekende_voertuigen_carrosserie` (vezc-m2t6, 4) + `_carrosserie_specificatie` (jhie-znh9, 5) [V]
carrosserietype · type_carrosserie_europese_omschrijving · carrosseriecode (cód. EU 2007/46/EG) · carrosserie_voertuig_nummer_europese_omschrijving · (volgnummers de unión).

### 3.4 `Gekentekende_voertuigen_voertuigklasse` (kmfi-hrps, 5) [V]
voertuigklasse (clase de bus/M2-M3: I/II/III, A/B) · voertuigklasse_omschrijving.

### 3.5 `Gekentekende_voertuigen_assen` (3huj-srit) · **16 columnas** [V] — Ejes
as_nummer · aantal_assen · aangedreven_as (tracción J/N) · hefas (eje elevable) · plaatscode_as (voor/achter) · spoorbreedte (ancho de vía) · weggedrag_code (suspensión: L=neumática/G/A) · wettelijk_toegestane_maximum_aslast · technisch_toegestane_maximum_aslast · geremde_as_indicator · afstand_tot_volgende_as (+ min/max) · maximum_last_as_technisch (min/max).

### 3.6 `Gekentekende_voertuigen_rupsbanden` (3xwf-ince, 7) [V] — Orugas
geremde_rupsband_indicator · aangedreven_rupsband_indicator · technisch_toelaatbaar_maximum massa rupsbandset (+ min/max).

### 3.7 `Gekentekende_voertuigen_bijzonderheden` (7ug8-2dtt, 6) [V] — Particularidades/anotaciones
bijzonderheid_code · bijzonderheid_code_omschrijving · bijzonderheid_variabele_tekst · bijzonderheid_eenheid · (volgnummer).

### 3.8 `Gekentekende_voertuigen_subcategorie_voertuig` (2ba7-embk, 4) [V]
subcategorie_voertuig_europees · subcategorie_voertuig_europees_omschrijving (carrocería de propósito especial).

### 3.9 Familia KEURINGEN (APK / ITV) [V]
- **`Keuringen` (vkij-7mwc, 3):** kenteken · **vervaldatum_keuring** (vencimiento APK).
- **`Meldingen Keuringsinstantie` (sgfe-77wx, 11):** soort_erkenning_keuringsinstantie (+ omschrijving) · meld_datum/meld_tijd_door_keuringsinstantie · soort_melding_ki_omschrijving · vervaldatum_keuring · api_gebrek_constateringen · api_gebrek_beschrijving (deep-links a defectos).
- **`Geconstateerde Gebreken` (a34c-vvps, 8):** kenteken · gebrek_identificatie · **aantal_gebreken_geconstateerd** · meld_datum/tijd · soort_erkenning (+ omschrijving). → defectos detectados por matrícula en cada inspección.
- **`Gebreken` (hx2c-gt7k, 8):** catálogo maestro de defectos: gebrek_identificatie · **gebrek_omschrijving** · gebrek_artikel_nummer · gebrek_paragraaf_nummer · ingangsdatum/einddatum_gebrek.
- **`Toegevoegde Objecten` (sghb-dzxx, 11):** objetos incorporados (p.ej. instalación de gas): montagedatum · demontagedatum · soort_toe_te_voegen_object_omschrijving · merk_object_toegevoegd · gasinstallatie_tank_inhoud · classificatie_toegevoegd_obj.

### 3.10 Familia TERUGROEPACTIES (Recalls / llamadas a revisión) [V]
- **`Terugroep_actie` (j9yg-7rg9, 27):** referentiecode_rdw · publicatiedatum_rdw · **meldende_producent_distributeur** · referentiecode_producent · **omschrijving_defect** · **categorie_defect** · **materiele_gevolgen** (consecuencias materiales) · **beschrijving_van_het_herstel** (reparación) · meer_informatie_op_internet · meer_informatie_via_telefoonnummer · opmerkingen_rdw · datum_aankondiging_producent · datum_melding_bij_rdw · **risicobeoordeling_rdw** · datum_informeren_eigenaar · datum_eigenaren_geinformeerd · **totaal_aantal_voertuigen_terugroepactie** · nationaal_opgegeven_aantal_voertuigen.
- **`Terugroep_actie_risico` (9ihi-jgpf, 3):** code_mogelijk_gevaar (ONG=accidente con lesiones / TEL=mayor riesgo lesión / BRA=incendio / MIL=medioambiente) · mogelijk_gevaar.
- **`Terugroep_actie_status` (t49b-isb7, 4):** kenteken · referentiecode_rdw · **code_status** (O=abierta / P=reparada) · status. → recall **por matrícula**.
- **`Terugroep_informeren_eigenaar` (mh8w-8cup, 3):** code_wijze_informeren (BRI=carta/BEL=llamada/ADV=anuncio/NTB) · wijze_waarop_u_wordt_geinformeerd.
- **`Terugroep_voertuig_merk_type` (mu2x-mu5e, 3):** merk · type (marca/modelos afectados por la acción).

### 3.11 Familia TYPEGOEDKEURING — TGK (Homologación de tipo, granularidad uitvoering) [V]
Catálogo técnico por **typegoedkeuringsnummer + variante + uitvoering** (12+ datasets). Núcleo:
- **`TGK Basis Uitvoering` (byxc-wwua, 48):** voertuigcategorie · codelinksrechtsrijdend · aantalwielen · y **rangos ondergrens/bovengrens** de: wielbasis, aantaldeuren, lengte, breedte, hoogte, aantalpassagiers, aantalzitplaatsen (+ stilstaand), aantalrolstoelplaatsen, maximummassa, massarijklaar, massaledig, minimummassavoltooid, maxconstructiesnelheidahw, maxondersteundesnelheid, maxverticalebelastopkopp · **parámetros de resistencia a la rodadura** paramrijweerstandF0/F1/F2 (ondergrens/bovengrens) · begin/einddatum revisie.
- **`TGK Merk Uitvoering` (kyri-nuah, 6):** merkcoderdw.
- **`TGK Handelsbenaming Fabrikant` (x5v3-sewk, 7):** **handelsbenamingfabrikant** · **typeaanduidingfabrikant**.
- Otros (no expandidos campo a campo, [V] existen en catálogo): TGK Aandrijving / As / Carrosserie / Energiebron / Koppeling / Rupsbandset / Speciale Doeleinden / Versnelling Uitvoering, TGK Intrekking Typegoedkeuring + *Begrippenlijst TGK-datasets* (data dictionary).

### 3.12 Familia ERKENDE BEDRIJVEN (Empresas reconocidas/erkend) [V]
- **`Erkende Bedrijven` (5k74-3jha, 10):** naam_bedrijf · gevelnaam · straat · huisnummer (+toevoeging) · postcode · plaats · (volgnummer + api_bedrijf_erkenningen).
- **`Erkenningen` (nmwb-dqkz, 2):** **erkenning** (tipo de reconocimiento/bevoegdheid: APK, gasinstallatie, tachograaf, export OREH, demontage ORAD, bedrijfsvoorraad BV, handelaarskenteken HKB, Kentekenloket, kentekenplaatfabrikant...). → directorio de talleres/operadores autorizados.

### 3.13 `Producten Catalogus` (v23s-d6km, 5) [V] — Catálogo OFICIAL de tarifas (Staatscourant)
staatscourant_indeling · tariefclustering · omschrijving · eenheid · **tarief** (€). Es la lista de precios estatutaria de los **servicios de pago** de RDW (no de los datos).

### 3.14 PRODUCTO — OVI / RDW Kentekencheck (`ovi.rdw.nl`) [V — render en vivo]
Consulta **per-matrícula** orientada a ciudadano/empresa. Es la "ficha de coche" oficial (ver Placement §7 para el mapa exacto). Expone, además de los campos open data, **datos que NO están en open data**:
- **Aantal eigenaren privé / zakelijk** (nº de propietarios particulares / empresa) — en el coche probado **4 / 1**. [V]
- **Gestolen** (robado: Sí/No) — estado de robo, **explícitamente excluido del open data**, sí visible en OVI. [V]
- **Datum inschrijving voertuig in Nederland**, **Datum/Tijdstip laatste tenaamstelling**. [V]
- **Roetfilter Af-Fabriek APK** (filtro de partículas de fábrica: Sí/No). [V]
- Códigos comunitarios EU (J, D.1, D.2, D.3, R, K, B, I, G, F.1–F.3, O.1, O.2) junto a cada campo del kentekenbewijs. [V]

---

## 4. Metodología y fuentes de datos

- **Fuente primaria = registro estatal propio** [V]: la **Basisregistratie Voertuigen** (kentekenregister), alimentada por los propios procesos RDW de **homologación de tipo** (TGK), **alta/tenaamstelling**, **APK** (vía estaciones erkend que reportan a RDW) y **notificaciones de fabricantes** (recalls). No es un agregador de terceros: RDW **es** el productor del dato.
- **Tellerstandoordeel (juicio NAP de cuentakilómetros)** [V]: desde el **1 de enero de 2014** RDW es responsable del registro de tellerstanden; emite un juicio sobre la *serie* de lecturas. Valores en vivo (16,8M filas): **Logisch 8.277.062 · Niet geregistreerd 4.883.478 · Geen oordeel 3.363.676 · Onlogisch 289.114**. Códigos de toelichting (00–07, NG) explican el porqué (p.ej. 04 = lectura inferior a la previa → posible rollback; 05 = vehículo estuvo registrado fuera de NL; 07 = juicio heredado de Stichting NAP). → **detección de fraude de km a escala nacional**.
- **Emisiones / consumo** [V]: doble estándar **NEDC y WLTP** (RDW mantiene ambas columnas), más mediciones de partículas, ruido (dB(A) estacionario/rodando) y autonomía/consumo eléctrico — todo medido en banco según directiva.
- **Recalls** [V]: el fabricante/distribuidor notifica a RDW; RDW publica con su propia referencia, **evaluación de riesgo** (risicobeoordeling_rdw), categoría de peligro y estado **por matrícula** (abierta/reparada).
- **Privacidad** [V]: el open data **excluye el dominio "rojo"** (datos sensibles): **no** se publican datos del **titular/propietario** (PII) ni el **indicador de robo** ("registered as stolen or missing is not offered via open data"). Esos datos sí existen en el registro y afloran selectivamente en OVI (nº de propietarios agregado, flag gestolen) o en verstrekkingen autenticadas.
- **Actualización** [V]: los datasets se actualizan **a diario** (los `_dt` y `rowsUpdatedAt` confirman refresco continuo).
- **Licencia** [V]: **Creative Commons 0 (CC0)** / dominio público para el open data.

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **Portal Open Data** | `opendata.rdw.nl` (plataforma **Socrata**); navegación, filtros, visualizaciones, export | [V] |
| **SODA API (REST)** | `https://opendata.rdw.nl/resource/{id}.json` con **SoQL** (`$select,$where,$group,$order,$limit,$offset,$q`); **sin API key**, sin límite de uso | [V — consultado en vivo] |
| **Formatos** | JSON, CSV, XML, RDF, XLSX (export Socrata estándar) | [V — JSON/CSV verificados; resto estándar Socrata] |
| **Mirror gubernamental** | también catalogado en `data.overheid.nl` | [V] |
| **Data dictionary / handleidingen** | manuales con descripción de cada dataset y campo; **foro** de usuarios (Google Group `voertuigen-open-data`) | [V] |
| **OVI / Kentekencheck** | `ovi.rdw.nl` — webapp per-matrícula (ciudadano), con **"Inloggen zakelijk"** para empresas (datos ampliados) | [V] |
| **Servicios de registro de pago** | tenaamstelling/Kentekenloket, erkenningen, verstrekking de datos a empresas erkend — tarifados (Producten Catalogus) | [V — existencia + tarifas] |
| **Documentos físicos** | Kentekencard (chip), permiso de conducir, formularios APK | [V] |
| **Integración DMS/feed B2B propietario** | **no** se halló un feed/SDK comercial tipo "DMS plugin"; la integración la hace el mercado sobre la SODA API abierta + servicios erkend | [A — ausencia] |

---

## 6. Precio

- **Open data: GRATIS, sin API key, sin límite, CC0.** [V] — *"De open data zijn voor elke gebruiker gratis en zonder beperking beschikbaar."*
- **Servicios de pago (Producten Catalogus, tarifas oficiales Staatscourant, en €)** [V — filas reales]:
  - Basiserkenning **44,55** · Erkenning APK **526,25** · Erkenning gasinstallatie **452,15** · Erkenning tachograaf (TA) **351,50** · Erkenning BCT (boordcomputer taxi) **492,00** · Erkenning bedrijfsvoorraad/handelaarskenteken/export/demontage/inschrijving **246,00** c/u · Erkenning kentekenplaatfabrikant/lamineerder/foliefabrikant **488,50** · **Erkenning tenaamstelling voor derden (Kentekenloket) 1.891,00** · **Registratie als EETS-aanbieder 8.474,00** · Annulering aanvraag 53,70.
  - (Unidades: STK=pieza, KI=instancia keuring, VE=entidad, WP=puesto trabajo, etc.)
- **Naturaleza**: el modelo de precio cubre **erkenningen, homologaciones, matriculación y verstrekkingen**, no la venta del dato abierto. No hay "suscripción de datos" porque el dato es público. [V]

---

## 7. Placement — dónde se ubica cada dato en la UI
> Doble patrón a copiar por Cardeep: (A) **ficha per-matrícula OVI** (consumidor) y (B) **página de dataset Socrata** (datos en bruto/reutilizador).

### A) OVI / RDW Kentekencheck — ficha per-matrícula [V — render en vivo H-804-XS]
**Cabecera:** título grande **MARCA + MODELO** (VOLKSWAGEN / GOLF); **buscador de kenteken** persistente arriba (placeholder "TIK HIER", botón "Zoek", aviso *"alleen Nederlandse kentekens"*); enlace **"Inloggen zakelijk"** (acceso empresa) y logo→rdw.nl.

**4 PESTAÑAS (tabs):** `Overzicht` · `Motor & Milieu` · `Technisch` · `Fiscaal`.

**Pestaña 1 — Overzicht (Resumen)** → 6 **secciones acordeón** colapsables, cada fila con su **código comunitario EU** a la izquierda y botón **"Meer informatie"** (tooltip explicativo):
1. **Algemeen:** Voertuigcategorie [J] · Carrosserietype · Inrichting · Merk [D.1] · Type [D.2] · Variant [D.2] · Uitvoering [D.2] · Kleur [R] · Handelsbenaming [D.3] · Typegoedkeuringsnummer [K] · **Aantal eigenaren privé/zakelijk**.
2. **Vervaldata en historie:** Vervaldatum APK · Datum eerste tenaamstelling in NL · Datum eerste toelating [B] · Datum inschrijving in NL · Datum/Tijdstip laatste tenaamstelling [I].
3. **Gewichten:** Massa rijklaar [G] · Massa ledig · Technische max massa [F.1] · Toegestane max massa [F.2] · Maximum massa samenstel [F.3] · Aanhangwagen geremd [O.1] · ongeremd [O.2].
4. **Tellerstanden:** Jaar laatste registratie · **Oordeel** (en el coche probado: *Onlogisch*) · **Toelichting** (texto explicativo del juicio).
5. **Status van het voertuig:** Gestolen · Geëxporteerd · Voldoet aan WAM · Verbod voor rijden op de weg · Tenaamstellen mogelijk.
6. **Terugroepacties:** Status terugroepactie(s) (abiertas/ninguna).

**Pestaña 2 — Motor & Milieu** → 3 secciones [V]:
- **Motor:** Cilinderinhoud · Aantal cilinders · Emissieklasse diesel · Brandstof · **Brandstofverbruik NEDC** vs **WLTP** · Elektrisch verbruik NEDC/WLTP · Elektrische actieradius NEDC/WLTP · Geluidsniveau stationair/rijdend · Toerental · Nettomaximumvermogen (kW) · Nominaal continu/Netto elektrisch.
- **Milieuprestaties:** Brandstof · Uitstoot deeltjes (licht/zwaar) · **Roetfilter Af-Fabriek APK**.
- **Uitstoot:** **CO2-uitstoot NEDC** vs **WLTP** · Emissieklasse · **Milieuklasse EG** (EURO 6 W) · Goedkeuring licht/zwaar.

**Pestaña 3 — Technisch** → secciones [V]:
- **Eigenschappen:** Aantal zitplaatsen · rolstoelplaatsen · aantal assen · aantal wielen · Wielbasis · Afstand voorzijde tot koppeling.
- **Assen → As 1 / As 2 (una sub-sección por eje):** Aangedreven as · Plaats as (Voor/Achter) · Spoorbreedte · Weggedrag · Technisch/Wettelijk toegestane maximum aslast.

**Pestaña 4 — Fiscaal** [A — no capturada a nivel de etiqueta por redirección del navegador compartido]: por el modelo de datos del registro contiene **Catalogusprijs**, **Bruto BPM**, **afschrijvingsmoment BPM** (registratie_datum_goedkeuring) y **zuinigheidsclassificatie** (etiqueta energética). Marcado [A]; no se inventan las cadenas exactas de UI.

**Patrón clave para Cardeep:** ficha = **buscador per-matrícula** + **tabs temáticos** (Resumen / Motor&Medioambiente / Técnico / Fiscal) + dentro de Resumen, **acordeones** (Identidad, Fechas&Historia, Pesos, **Cuentakilómetros con veredicto**, **Estado legal**, **Recalls**), cada dato con **tooltip "Meer informatie"** y **código normativo** al lado. El veredicto antifraude (Onlogisch) y el estado (robado/exportado/WAM) se muestran **inline en el resumen**, no escondidos.

### B) Página de dataset (Socrata) — para reutilizadores [V]
Cada dataset (`opendata.rdw.nl/.../{id}`) presenta: **grid de datos** filtrable/ordenable; panel **About** con metadata (categoría, licencia CC0, attribution "Team Open Data RDW", última actualización); **lista de columnas** con tipo y descripción (data dictionary); botones **Visualize / Export / API** (con el endpoint `/resource/{id}.json` y documentación SoQL). Las columnas `api_*` enlazan a sub-datasets relacionados (expansión por relación).

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Fuente de verdad oficial y autoritativa** (registro estatal, no estimación). Para NL, RDW **es** el dato canónico de identidad/spec/estado del vehículo — el papel que en ES juega DGT, en DE el KBA, en UK el DVLA. Cardeep, en su subdominio **official-data**, debe tratarlo como **ancla de verdad**, no como competidor de valoración.
- [V] **Gratis, sin API key, sin límite, CC0** + **SODA API** completa con SoQL → reutilización masiva trivial. Casi todo el ecosistema NL (Autotelex, ANWB, kentekencheck) se apoya en RDW.
- [V] **Cobertura universal de tipos** (16,8M vehículos; turismos→tractores→orugas→speed-pedelec) y **profundidad técnica de homologación** (TGK con rangos por uitvoering, resistencia a la rodadura F0/F1/F2) que las listas comerciales no publican.
- [V] **Juicio antifraude de cuentakilómetros a escala nacional** (tellerstandoordeel Logisch/Onlogisch con explicación y trazabilidad post-2014) — dato de integridad que pocos exponen tan limpio.
- [V] **Registro de recalls por matrícula** con riesgo, consecuencias, reparación y estado abierto/reparado.
- [V] **Doble emisión NEDC + WLTP**, partículas, ruido, autonomía EV y clase híbrida — granularidad medioambiental oficial.
- [V] **Estado legal completo** (gestolen, export, WAM, verbod, tenaamstellen mogelijk) y **nº de propietarios** vía OVI.
- [V] **Daily update** + espejo en data.overheid.nl + data dictionary + foro.

## 9. Gaps (lo que NO ofrece)
- [V] **Cero valoración / precio de mercado**: NO hay retail/trade value, residual %, days-to-sell, market days supply, price-to-market, curva de depreciación ni índice oferta/demanda. Solo `catalogusprijs` (precio nuevo de catálogo) y `bruto_bpm` (impuesto). → Es el **input crudo** sobre el que terceros (Autotelex/ANWB) construyen la valoración.
- [V] **Sin PII del propietario** en open data (nombre/dirección del titular excluidos); solo agregados/derivados en OVI (nº de propietarios) o verstrekkingen autenticadas.
- [V] **Estado de robo (gestolen) NO en open data** (solo en OVI per-matrícula).
- [V] **Sin VIN/chassisnummer** publicado (solo su ubicación `plaats_chassisnummer`).
- [V] **Sin lectura de km exacta**: expone el **juicio** sobre la serie, no el valor histórico de odómetro km a km.
- [V] **Solo Países Bajos** (matrículas NL); no es multi-país pese al rol UE de homologación.
- [A] **Sin fotos, anuncios, ni equipamiento/opciones de fábrica detallado** a nivel consumidor (la riqueza de equipamiento vive en TGK por código, no como lista legible de opciones).
- [A] **Sin previsión/forecast, sin TCO, sin comparador de mercado** (no es su misión; es registro, no analítica).
- [A] **Sin feed/DMS comercial propietario**: la integración se delega al mercado sobre la API abierta; no hay SLA comercial de producto de datos.

---

## 10. Fuentes (URLs)
- https://opendata.rdw.nl/ — portal Socrata (catálogo). [V]
- `https://opendata.rdw.nl/api/catalog/v1?domains=opendata.rdw.nl` — catálogo completo (206 entradas; 25+ datasets de datos). [V]
- `https://opendata.rdw.nl/api/views/{id}.json` — metadata/columnas de: m9d7-ebf2 (98), 8ys7-d773 (36), 3huj-srit (16), vezc-m2t6 (4), jhie-znh9 (5), kmfi-hrps (5), 7ug8-2dtt (6), 3xwf-ince (7), 2ba7-embk (4), vkij-7mwc (3), sgfe-77wx (11), a34c-vvps (8), hx2c-gt7k (8), sghb-dzxx (11), j9yg-7rg9 (27), 9ihi-jgpf (3), t49b-isb7 (4), mh8w-8cup (3), mu2x-mu5e (3), byxc-wwua (48), kyri-nuah (6), x5v3-sewk (7), 5k74-3jha (10), nmwb-dqkz (2), v23s-d6km (5), jqs4-4kvw (2). [V]
- `https://opendata.rdw.nl/resource/m9d7-ebf2.json?$select=count(*)` → 16.813.330; `$group=voertuigsoort`; tellerstandoordeel `$group`. [V — en vivo]
- `https://opendata.rdw.nl/resource/v23s-d6km.json` — tarifas reales (Producten Catalogus). [V]
- `https://opendata.rdw.nl/resource/jqs4-4kvw.json` — códigos de toelichting tellerstandoordeel (00–07, NG). [V]
- **https://ovi.rdw.nl/** (deep-link `?kenteken=H804XS`) — render en vivo de la ficha per-matrícula; 4 tabs, 6 secciones de Overzicht, Motor&Milieu y Technisch capturadas a nivel de campo. [V]
- https://www.rdw.nl/over-rdw + /over-rdw/organisatie + /en/about-us/rdw-is-the-netherlands-vehicle-authority — identidad, ZBO, 4 tareas, HQ. [V]
- https://www.rdw.nl/over-rdw/dienstverlening/open-data + /algemene-informatie — entrega, gratis/sin límite, exclusión de datos sensibles/robo, data dictionary, foro. [V]
- https://en.wikipedia.org/wiki/RDW_(organization) — 1949, ZBO 1996, Zoetermeer, Detroit/Seoul, notified body 2004, Kentekencard 2014. [V]
- WebSearch corroborante: Socrata/SODA, "updated daily", rdwdata.nl/kentekencheck (terceros sobre RDW). [V/contexto]

> **Verificación**: identidad, las 4 tareas y estatus ZBO = fuente primaria/Wikipedia [V]. Cobertura (16,8M + desglose) y todos los conteos = **SODA API en vivo** [V]. El inventario atómico de campos (~330 columnas en 25+ datasets) = **metadata Socrata leída** [V]. Placement OVI (3 de 4 tabs) = **render Playwright en vivo** [V]; pestaña Fiscaal = [A] derivada del modelo de datos por redirección del navegador compartido, sin inventar etiquetas. Tarifas = filas reales del catálogo oficial [V]. Plantilla ~1.999 = tercero [A].
