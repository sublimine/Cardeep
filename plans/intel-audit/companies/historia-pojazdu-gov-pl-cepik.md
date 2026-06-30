# Historia Pojazdu (gov.pl) / CEPiK — Auditoría atómica

> **slug:** `historia-pojazdu-gov-pl-cepik` · **subdominio de audit:** `official-data` · **web:** https://www.gov.pl/web/gov/sprawdz-historie-pojazdu (servicio: https://historiapojazdu.gov.pl/ → `moj.gov.pl/.../HistoriaPojazdu`) · **API:** https://api.cepik.gov.pl/doc
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[VERIFICADO]` = leído en fuente directa; `[VERIFICADO≥2]` = ≥2 fuentes; `[NO-VERIFICADO]` lo no confirmado; `[DISCREPANCIA]` cuando las fuentes chocan; nada inventado.
> **Método:** WebSearch + WebFetch a fondo sobre gov.pl/cepik.gov.pl/dane.gov.pl + **descarga directa del OpenAPI spec** (`apicepik.json`, 92 KB, parseado campo a campo = 69 atributos `VehicleDto` autoritativos) + **llamadas en vivo a la API** (`/slowniki/marka` HTTP 200, 7.922 valores con frecuencia; `/slowniki` y `/pojazdy` devolvieron 504 / timeout — ver §Gaps) + fuentes terciarias (NIK, autoDNA, autoexpert, autobaza, driverhub, gazetaprawna).
>
> **Veredicto express:** Historia Pojazdu **NO es una empresa ni una casa de valoración**: es el **servicio público gratuito del Estado polaco** (Ministerstwo Cyfryzacji, operado por COI) que expone al ciudadano la **fuente primaria de verdad registral** del parque polaco — la base **CEPiK / CEP** (Centralna Ewidencja Pojazdów). Es **el dato crudo institucional** del que beben los players comerciales (autoDNA, carVertical citan CEPiK como fuente). Su unidad de valor es el **hecho registral datado y de autoridad estatal** (matriculación, propietarios, inspección técnica + odómetro, OC vigente, baja/robo), **no el precio**. Tres superficies: (1) **Historia Pojazdu** — informe ciudadano gratis por matrícula+VIN+fecha; (2) **CEPiK Open API** (`api.cepik.gov.pl`) — **69 campos técnicos/registrales anonimizados** por voivodato, gratis, con **diccionarios-frecuencia** (censo del parque por atributo); (3) **descargas masivas** (`/pliki`, dane.gov.pl). Servicios hermanos sobre la misma base: **Bezpieczny Autobus**, **Mój Pojazd** (mObywatel), **Sprawdź punkty karne**.
> **Giro clave (2020-04-27):** el propio servicio gov **integra una "tabla de riesgos" de autoDNA** (0,5 mil M de registros, 16 países) + lecturas de odómetro extranjero — el Estado y el privado se **alimentan mutuamente**. La versión completa de autoDNA es upsell de pago (89,99 PLN, may-2026).
> **Patrón a copiar por cardeep:** (1) informe en **tres vistas/pestañas** — *Informacje* (ficha técnica) · *Oś czasu* (línea de tiempo cronológica = columna vertebral) · *Dane zagraniczne / tabela ryzyka* (tabla de riesgos extranjeros con **flags rojos**); (2) el **odómetro como serie temporal con detección de retroceso** alimentada por inspecciones técnicas datadas; (3) **propiedad como timeline tipo firma/persona** (sin PII, solo conteo+tipo); (4) **API pública con diccionarios que devuelven frecuencia por valor** (cuántos vehículos de cada marca/combustible) → censo del parque "gratis"; (5) **zona de autoridad estatal vs. zona de overlay comercial** claramente separadas en la misma ficha.
> **Sombra:** la NIK (Tribunal de Cuentas) califica CEPiK de **"costoso y en construcción perpetua (10+ años)"**; la API pública es **inestable** (en esta auditoría: `/slowniki` y `/pojazdy` devolvieron 504/timeout repetidos); la versión `beta` del API lleva años; cobertura **solo desde la 1ª matriculación EN POLONIA** (ciega al pre-import); **sin fotos** (hasta el piloto 2026 de SKP), **sin equipamiento de fábrica**, **sin historial de servicio**, **sin valoración**.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Naturaleza | **Servicio público estatal** (e-usługa), NO empresa privada. Sin owner societario, sin facturación, sin clientes de pago | [VERIFICADO≥2: gov.pl, cepik.gov.pl] |
| Nombre del servicio | **Historia Pojazdu** ("Sprawdź historię pojazdu" / Check Vehicle History) | [VERIFICADO≥2: gov.pl/web/gov, historiapojazdu.gov.pl] |
| Sistema/base subyacente | **SI CEPiK** = System Informatyczny **Centralnej Ewidencji Pojazdów i Kierowców** (Registro Central de Vehículos y Conductores). Componentes: **CEP** (vehículos) + **CEK** (conductores) | [VERIFICADO≥2: gov.pl/web/cyfryzacja, cepik.gov.pl] |
| Owner / autoridad responsable | **Ministerstwo Cyfryzacji** (Ministerio de Digitalización; antes MSWiA / KPRM en distintas etapas) | [VERIFICADO≥2: gov.pl, MSWiA archiwum] |
| Operador técnico (construye/explota) | **Centralny Ośrodek Informatyki (COI)** — contrato con el ministerio desde **2013** | [VERIFICADO≥2: NIK, swiatopon.info] |
| HQ / jurisdicción | **Polonia** (servicio nacional; portales `gov.pl`, `cepik.gov.pl`, `dane.gov.pl`) | [VERIFICADO] |
| Base legal | **Ustawa z dnia 20 czerwca 1997 r. Prawo o ruchu drogowym** (Ley de Tráfico 1997) + Directiva 2011/82/UE (intercambio transfronterizo de infracciones) | [VERIFICADO≥2: gov.pl/web/cyfryzacja] |
| Cronología | **CEP** operativo desde **2004**, **CEK** desde 2005; sistema construido **2003–2010**. **CEPiK 2.0**: contrato COI 2013 → **CEP 2.0** en **nov-2017** → CEPiK 2.0 pleno **13-jun-2018** | [VERIFICADO≥2: NIK, swiatopon, cepik.gov.pl] |
| Lanzamiento "Historia Pojazdu" | **junio 2014** (servicio gratuito); ampliación a **autos importados/no registrados en PL: 15-dic-2017** (vía CEPiK 2.0) | [VERIFICADO≥2: gov.pl/web/cyfryzacja, cepik.gov.pl] |
| Integración autoDNA | **27-abril-2020** — "tabla de riesgos" (tabela ryzyka) de autoDNA + odómetro extranjero embebidos en el servicio gov gratuito | [VERIFICADO≥2: autodna.pl, autoexpert.pl] |
| Contacto | uslugicepik2.0@cyfra.gov.pl · http://cepik.gov.pl | [VERIFICADO: gov.pl] |
| Reputación / control externo | **NIK** (Najwyższa Izba Kontroli / Tribunal de Cuentas) — informe crítico recurrente: "CEPiK, costoso y en construcción desde hace 10 años, sin final a la vista" | [VERIFICADO≥2: nik.gov.pl, prawo.pl] |

**Qué es:** el **registro estatal de matriculación** de Polonia, expuesto al ciudadano como informe de historial gratuito y a desarrolladores como API abierta. Es la **capa "official-data"**: dato de autoridad pública, no agregación comercial. Es a la vez **fuente upstream** de los informes comerciales (autoDNA, carVertical, EpicVIN beben de CEPiK) **y consumidor downstream** de uno de ellos (autoDNA, desde 2020).

### Categorías de "producto" (superficies de exposición del dato)
1. **Historia Pojazdu** — informe de historial ciudadano (B2C, gratis) por matrícula+VIN+fecha.
2. **CEPiK Open API** (`api.cepik.gov.pl`) — API REST JSON:API con datos técnicos/registrales anonimizados (B2B/devs, gratis).
3. **Descargas masivas / `pliki`** — ficheros de datos de vehículos + metadatos (dane.gov.pl dataset 1558).
4. **Słowniki (diccionarios-frecuencia)** — valores de referencia + **conteo de ocurrencias** por valor (censo del parque).
5. **Statystyki** — API de estadísticas de uso del propio servicio.
6. **Bezpieczny Autobus** — verificación de autobús/autocar por matrícula (B2C, gratis).
7. **Mój Pojazd** (mObywatel / mPojazd) — datos del **propio** vehículo del titular autenticado (incl. multas y puntos).
8. **Tabela ryzyka autoDNA** (overlay comercial dentro de Historia Pojazdu).

### Cliente objetivo
**Compradores particulares de usado** (núcleo del informe) · **vendedores** (demostrar transparencia) · **desarrolladores / analistas / aseguradoras / fabricantes / investigadores** (API abierta) · **pasajeros de autocar** (Bezpieczny Autobus) · **titulares de vehículo** (Mój Pojazd).

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Geografía | **Polonia** (parque nacional). Datos extranjeros vía **EUCARIS** (European Car and Driving Licence Information System) + overlay autoDNA | [VERIFICADO≥2: cepik.gov.pl, car-dossier] |
| Volumen del parque (CEP) | **~35,5 M vehículos** (todos los tipos, 2024). **10-jun-2024: ~7,15 M** matrículas marcadas "wygaśnięcie rejestracji" (caducidad) en una limpieza masiva de la base | [VERIFICADO≥2: gazetaprawna, gov.pl/web/cepik/statystyki] |
| Altas nuevas 2025 | **667.591** vehículos (597.435 turismos + 70.156 furgonetas) | [VERIFICADO: fleet.com.pl, samar.pl] |
| Diccionario de marcas (API en vivo) | **7.922 marcas** distintas, cada una con conteo de vehículos (`liczba-wystapien`) | [VERIFICADO: llamada en vivo `/slowniki/marka` HTTP 200, 423 KB, modificado 2024-10-19] |
| Países fuente de dato extranjero (CEP nativo / EUCARIS) | EE.UU., Canadá + UE selectos. Listas variables por fuente: gov.pl cita "US, CA, BE, NL, ES, SE, NO"; otra fuente "~20 mercados, ~4,5 M autos importados"; otra "15 países europeos, dato muy escaso" | [DISCREPANCIA de cifras — single-source cada una; ver Notas] |
| Países fuente del overlay autoDNA | **16**: Alemania, Francia, Bélgica, Eslovenia, Lituania, Letonia, Estonia, Suiza, Suecia, Austria, Noruega, Países Bajos, Chequia, Hungría, Rumanía, Dinamarca | [VERIFICADO≥2: autodna.pl, autoexpert.pl] |
| Profundidad temporal del odómetro | Lecturas desde **2014** (cada inspección técnica) + **control policial de carretera** + **historial de sustitución de cuentakilómetros desde 2020** | [VERIFICADO≥2: gov.pl, driverhub, autodna] |
| Szkody istotne (daños relevantes) | Desde **1-mar-2020** (dato de UFG/aseguradoras) | [VERIFICADO: driverhub, gov.pl/web/gov] |
| Coste | **Gratis** (bezpłatna) en todas las superficies estatales. Límite: **20 consultas/hora** de vehículo extranjero con Profil Zaufany; API: **20 req/s, máx 100/min** | [VERIFICADO≥2: gov.pl, api.cepik.gov.pl] |
| Disponibilidad | Online 24/7; resultado inmediato; PDF descargable | [VERIFICADO: gov.pl] |

### Scope de vehículo
- **Solo USADO / historial registral** (no hay catálogo de coche nuevo NVD ni libro de valores). El Open API sí permite filtrar **altas nuevas** por fecha (útil para censo de matriculaciones).
- Identificación ciudadana por **triple llave: matrícula (numer rejestracyjny) + VIN + data pierwszej rejestracji** (más estricta que los comerciales, que piden solo VIN).
- Tipos de vehículo: **todos los registrados en CEP** (turismos, furgonetas, camiones, **autobuses/autocares** → Bezpieczny Autobus, motos, remolques, tractores — el diccionario de marcas incluye remolques/caravanas: ABBEY, ABI, etc.).
- **Punto ciego estructural:** CEP "ve" el vehículo **desde su 1ª matriculación en Polonia**; el historial pre-importación lo aporta el overlay autoDNA/EUCARIS, no CEP.

---

## 3. Productos + campos atómicos

> Dos fuentes de verdad para campos: (a) el **OpenAPI spec** (`apicepik.json`) da los **69 atributos `VehicleDto`** del Open API, verbatim; (b) las **páginas del servicio + reviews** dan los campos del informe ciudadano. Se separan porque **NO son el mismo conjunto**: el Open API es anonimizado/técnico (sin VIN, sin matrícula, sin odómetro, sin PII), agregable por voivodato; el informe ciudadano sí da odómetro/propietarios/OC pero **no** los 69 campos técnicos completos.

### 3.1 Historia Pojazdu — informe ciudadano (producto estrella, gratis)

**Vista "Informacje" (ficha técnica / identidad):**
- `Marka` (marca) · `Model` (modelo) · `Typ/wariant/wersja` (tipo)
- `Rok produkcji` (año de producción)
- `Pojemność silnika` (cilindrada) · `Moc silnika` (potencia) · `Rodzaj paliwa` (combustible)
- `Masa własna` (masa propia/tara) · `Dopuszczalna masa całkowita` (MMA)
- `Liczba miejsc` (nº de plazas)
- `Data pierwszej rejestracji` (1ª matriculación) · `Data pierwszej rejestracji w Polsce`
- `Numer rejestracyjny` / `VIN` (eco de la entrada)
- `Rodzaj pojazdu` (tipo/categoría)

**Vista "Oś czasu" (línea de tiempo — columna vertebral cronológica):**
- `Liczba właścicieli` (nº de propietarios desde matriculación en PL, incluido el actual) + **co-propietarios**
- `Typ właściciela` por tramo: **firma / organización / osoba prywatna** (empresa/organización/persona física) — sin PII
- `Województwo rejestracji` (voivodato de matrícula)
- `Badania techniczne` (inspecciones técnicas): **fecha + resultado + vigencia actual + fecha próxima**
- `Odczyt drogomierza / przebieg` (lectura de odómetro) **por cada inspección, desde 2014** + **lecturas de control policial de carretera**
- `Historia wymiany drogomierza` (historial de **sustitución** del cuentakilómetros, desde 2020) → señal anti-rollback
- `Ubezpieczenie OC` (seguro obligatorio): **vigencia / hasta cuándo**
- `Szkody istotne` (daños "relevantes"/estructurales, dato UFG, desde 1-mar-2020)
- `Data wyrejestrowania` (baja) · `Czasowe wycofanie z ruchu` (retirada temporal) y re-alta
- Eventos de **kradzież** (robo) + **odzyskanie** (recuperación)

**Vista "Dane zagraniczne" / Tabela ryzyka (datos extranjeros — overlay autoDNA + EUCARIS):**
> Tabla de **flags binarios** (verde/rojo) — "alerta roja cuando una categoría se confirma". Conjunto actual (autoDNA, 9 categorías):
- `Szkoda całkowita` (siniestro total)
- `Uszkodzenie pojazdu` (daño del vehículo)
- `Kradzież` (robo — base internacional)
- `Zgodność VIN z normą ISO` (validez/consistencia del VIN según ISO)
- `Recall / akcja serwisowa producenta` (llamada a revisión del fabricante)
- `Złomowanie` (desguace/achatarramiento)
- `Zakaz ruchu / niedopuszczony do ruchu` (prohibición de circular)
- `Użytkowanie jako taxi` (uso como taxi)
- `Rozbieżności drogomierza` (discrepancias de odómetro)
- `Odczyty drogomierza zagraniczne` (lecturas de odómetro de los países donde estuvo matriculado antes, desde 2014, según disponibilidad)

> *(El conjunto original CEP/EUCARIS 2018 eran 7 categorías: Kradzież · Złomowanie · Powypadkowy · Uszkodzony · "Przekręcony" licznik · Niedopuszczony do ruchu · Służył jako taxi. El overlay autoDNA 2020 lo amplió/sustituyó por la tabla de 9.)*

**Nuevo (piloto 2026):** `Dokumentacja fotograficzna ze stacji kontroli pojazdów (SKP)` — **fotos de la estación de ITV**: exterior, matrícula y lectura del cuentakilómetros. [NO-VERIFICADO≥2: single-source driverhub; feature emergente]

**Entrega:** resultado inmediato en pantalla + **PDF** descargable (informativo, no documento oficial para juzgado/administración).

### 3.2 CEPiK Open API — `/pojazdy` (69 atributos `VehicleDto`, verbatim del spec)

> Anonimizado (sin VIN/matrícula/PII). Filtrable por `wojewodztwo` (TERYT, **obligatorio**) + `data-od`/`data-do` (máx. 2 años) + `typ-daty` (1=1ª matrícula PL, 2=última). Mecanismos: `filter[atributo]=valor`, `sort`, `fields`, `pokaz-wszystkie-pola`, `limit` (máx 500), `page`. ID técnico ≠ VIN ni matrícula.

**Identificación / nomenclatura:**
`marka` · `model` · `typ` · `wariant` · `wersja` · `nazwa-producenta` (fabricante) · `rodzaj-pojazdu` (tipo) · `podrodzaj-pojazdu` (subtipo) · `kategoria-pojazdu` · `przeznaczenie-pojazdu` (uso/destino) · `kod-rodzaj-podrodzaj-przeznaczenie` + `rodzaj-kodowania-...` · `kod-instytutu-transportu-samochodowego` (cód. ITS) · `sposob-produkcji` (modo de producción) · `rodzaj-tabliczki-znamionowej` (tipo de placa de datos) · `rok-produkcji`

**Motor / energía / emisiones:**
`pojemnosc-skokowa-silnika` (cilindrada) · `moc-netto-silnika` (potencia neta) · `max-moc-netto-silnikow-pojazdu-hybrydowego` (potencia máx. híbrido) · `rodzaj-paliwa` (combustible) · `rodzaj-pierwszego-paliwa-alternatywnego` · `rodzaj-drugiego-paliwa-alternatywnego` · `avg-zuzycie-paliwa` (consumo medio) · `poziom-emisji-co2` · `poziom-emisji-co2-pierwsze-paliwo-alternatwne` · `poziom-emisji-co2-drugie-paliwo-alternatwne` · `redukcja-emisji-spalin` (reducción por tech innovadora) · `katalizator-pochlaniacz` (catalizador, bool) · `stosunek-mocy-silnika-do-masy-wlasnej-motocykle` (relación potencia/peso, motos)

**Masas / dimensiones / ejes:**
`masa-wlasna` (tara) · `masa-pojazdu-gotowego-do-jazdy` (masa en orden de marcha) · `dopuszczalna-masa-calkowita` (MMA) · `maksymalna-masa-calkowita` · `dopuszczalna-masa-calkowita-zespolu-pojazdow` (MMA conjunto) · `dopuszczalna-ladownosc` (carga útil) · `maksymalna-ladownosc` · `max-masa-calkowita-ciagnietej-przyczepy-bez-hamulca` (remolque sin freno) · `max-masa-calkowita-przyczepy-bez-hamulca` (remolque con freno) · `liczba-osi` (nº ejes) · `dopuszczalny-nacisk-osi` · `maksymalny-nacisk-osi` (carga por eje) · `max-rozstaw-kol` · `min-rozstaw-kol` · `avg-rozstaw-kol` (vía/rozstaw de ruedas) · `rozstaw-kol-osi-kierowanej-pozostalych-osi` · `rodzaj-zwieszenia` (suspensión)

**Plazas:**
`liczba-miejsc-ogolem` (plazas totales) · `liczba-miejsc-siedzacych` (sentadas) · `liczba-miejsc-stojacych` (de pie)

**Equipamiento / configuración:**
`kierownica-po-prawej-stronie` (volante a la derecha, bool) · `kierownica-po-prawej-stronie-pierwotnie` (originalmente RHD) · `hak` (enganche/bola, bool) · `wyposazenie-i-rodzaj-urzadzenia-radarowego` (equipo radar)

**Registro / procedencia / fechas:**
`pochodzenie-pojazdu` (procedencia: nuevo/importado…) · `data-pierwszej-rejestracji` · `data-pierwszej-rejestracjiwkraju` (1ª en PL) · `data-pierwszej-rejestracji-za-granica` (1ª en extranjero) · `data-ostatniej-rejestracji-w-kraju` (última en PL) · `data-wprowadzenia-danych` (alta del dato) · `data-wyrejestrowania-pojazdu` (baja) · `przyczyna-wyrejestrowania-pojazdu` (motivo de baja)

**Geo (TERYT, anonimizado a nivel administrativo):**
`rejestracja-wojewodztwo` / `rejestracja-powiat` / `rejestracja-gmina` (lugar de matrícula: voivodato/condado/municipio) · `wojewodztwo-kod` (cód. TERYT) · `wlasciciel-wojewodztwo` / `wlasciciel-powiat` / `wlasciciel-gmina` (sede/domicilio del titular, nivel administrativo) · `wlasciciel-wojewodztwo-kod`

### 3.3 Słowniki — diccionarios-frecuencia (API)
- `GET /slowniki` (lista de diccionarios) · `GET /slowniki/{nazwa-slownika}` (p.ej. `marka`, `wojewodztwa`, `rodzaj-paliwa`).
- **Cada valor devuelve dos campos:** `klucz-slownika` (el valor, p.ej. "TOYOTA") + **`liczba-wystapien`** (nº de vehículos con ese valor en el registro). → es un **censo del parque por atributo** (cuántos hay de cada marca/combustible/voivodato). `marka` = **7.922** valores.
- Metadatos: `ilosc-rekordow-slownika` (total) + `schema:provider` (Ministerstwo Cyfryzacji) + `schema:dateModified`.

### 3.4 Statystyki — API de estadísticas de uso
- `StatisticsVehicleDto`: `data-statystyki` · `nazwa-wojewodztwa` · `ilosc-wyszukan` (nº de llamadas a `/pojazdy`).
- `StatisticsActivityDailyDto`/`HourlyDto`: `dzien-tygodnia` · `data-statystyki` · `laczna-ilosc-wyswietlen` (total de llamadas a métodos del API ese día/hora).
- Endpoints: `/statystyki/pojazdy/{data}`, `.../{wojewodztwo}`, `/statystyki/aktywnosc/{data}`, `/statystyki/pliki`, `/statystyki/slowniki/{data}`.

### 3.5 Pliki — descargas masivas (`/pliki` + dane.gov.pl 1558)
- `FileDto`: `url-do-pliku` · `url-do-metadanych-pliku` · `opis-zawartosci` (contenido) · `opis-formatu-pliku` (formato) · `typ-zasobu-bedacego-zawartoscia` (p.ej. "pojazdy") · `data-utworzenia-pliku`.
- El payload de cada fichero = los 69 campos `VehicleDto`. Licencia: **uso comercial y no comercial permitido con atribución**.

### 3.6 Bezpieczny Autobus — verificación de autocar (gratis, por matrícula)
- `Ważne badanie techniczne` + `do kiedy` (ITV vigente + hasta cuándo + próxima)
- `Ważne ubezpieczenie OC` (OC vigente)
- `Wyrejestrowany / kradziony` (baja / robado)
- `Dane techniczne` (técnicos, p.ej. `liczba miejsc` = nº de plazas)
- `Masa pojazdu` (masa)
- `Stan licznika z ostatniego badania technicznego` (odómetro de la última ITV)
- Solo autobuses registrados en CEP (Polonia); no extranjeros.

### 3.7 Mój Pojazd / mPojazd (mObywatel) — vehículo propio del titular autenticado
> Requiere **Profil Zaufany (eGO)**. Datos del propio vehículo + capa sancionadora del conductor.
- `Marka` · `Typ` · **`VIN`** (aquí sí, por ser el titular) · `Data pierwszej rejestracji` · `Termin badania technicznego` (fecha ITV)
- Datos técnicos: `pojemność i moc silnika` · `liczba miejsc` · `dopuszczalna masa całkowita` · `rozstaw osi`
- `Ważność OC` (vigencia seguro) + **recordatorios** de OC/ITV
- Eventos: `wyrejestrowanie`, `sprzedaż` (venta), baja
- **`Punkty karne`** (puntos de penalización — vía "Sprawdź punkty karne", desde 24-abr)
- **`Mandaty`** (multas): pagadas/impagadas + detalle (dónde, cuándo, vehículo en el que se recibió)
- Exportable a **PDF**.

---

## 4. Metodología / fuentes de datos

| Aspecto | Detalle | Estado |
|---|---|---|
| Naturaleza | **Registro de autoridad estatal** (dato administrativo primario), no agregación comercial ni modelo estadístico | [VERIFICADO≥2] |
| Instituciones que alimentan CEP | **starostwa** (oficinas de matriculación) · **Policja, ITD** (Inspección de Transporte), **Żandarmeria Wojskowa** · **SKP** (estaciones de ITV) · **UFG** (Insurance Guarantee Fund — OC y siniestros) · autoridades de permisos · **juzgados y fiscalías** · **wojewodowie** | [VERIFICADO≥2: gov.pl/web/cyfryzacja SI CEPiK] |
| Dato extranjero | **EUCARIS** (intercambio entre registros de EE.MM. UE) + **overlay autoDNA** (16 países, 0,5 mil M registros, desde 2020) | [VERIFICADO≥2: car-dossier, autodna.pl] |
| Odómetro | Capturado en **cada inspección técnica desde 2014** + **control policial**; sustitución de cuentakilómetros registrada desde 2020 | [VERIFICADO≥2: gov.pl, driverhub] |
| Daños | **Szkody istotne** (daños relevantes/estructurales) desde UFG, **desde 1-mar-2020** | [VERIFICADO: driverhub, gov.pl] |
| Naturaleza del dato | **Determinista/documental, de autoridad** (hechos registrales datados). **NO predictivo**: sin residual %, sin trade/retail, sin days-to-sell, sin price-to-market | [VERIFICADO por ausencia] |
| Diccionarios-frecuencia | El API expone **conteo de vehículos por valor de atributo** → permite censo del parque (parc) por marca/combustible/voivodato/año | [VERIFICADO: `/slowniki/marka` en vivo] |
| Limitaciones declaradas | "No contiene todos los eventos — p.ej. daños menores no reportados al seguro o reparaciones privadas"; "no debe ser único criterio de compra" | [VERIFICADO≥2: gov.pl] |
| Calidad/gobernanza | NIK: retrasos, sobrecoste, fallos de funcionamiento; API en `beta` permanente | [VERIFICADO≥2: NIK, spec version "beta"] |

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **Web / informe online** | `historiapojazdu.gov.pl` → SPA xForms en `moj.gov.pl`; resultado inmediato en 3 vistas | [VERIFICADO≥2: gov.pl, redirect observado] |
| **PDF** | Descargable/imprimible (informativo, no oficial) | [VERIFICADO≥2: gov.pl, autobaza] |
| **App móvil** | **mObywatel** (Bezpieczny Autobus, Mój Pojazd, multas, puntos) | [VERIFICADO≥2: info.mobywatel.gov.pl] |
| **API REST** | `api.cepik.gov.pl` — **JSON:API**; recursos `/pojazdy`, `/slowniki`, `/statystyki`, `/pliki`, `/prawa-jazdy`, `/uprawnienia`, `/version`; doc Swagger `/doc` + OpenAPI `apicepik.json` | [VERIFICADO: spec descargado] |
| **Descarga masiva** | `/pliki` + `dane.gov.pl/dataset/1558` (ficheros + metadatos); cross-list en `data.europa.eu` | [VERIFICADO≥2: dane.gov.pl, data.europa.eu] |
| **Idioma** | Polaco (servicio); doc API en polaco | [VERIFICADO] |
| **Autenticación** | Anónimo para vehículo PL; **Profil Zaufany (eGO)** para vehículo extranjero (máx 20/h) y para Mój Pojazd | [VERIFICADO≥2: gov.pl] |
| **NO ofrece** | Integración DMS, feed de inventario en vivo, dashboard de mercado, Excel de valoración, webhooks | [VERIFICADO por ausencia] |

---

## 6. Precio (descubrible)

| Producto | Precio | Notas | Estado |
|---|---|---|---|
| Historia Pojazdu (informe) | **Gratis** | incluye tabla de riesgos autoDNA básica + odómetro extranjero según disponibilidad | [VERIFICADO≥2: gov.pl, autodna] |
| CEPiK Open API | **Gratis** | 20 req/s, máx 100/min; sin clave/registro | [VERIFICADO≥2: api.cepik.gov.pl, gov.pl] |
| Descargas masivas / dane.gov.pl | **Gratis** | uso comercial y no comercial con atribución | [VERIFICADO: gov.pl/web/cepik] |
| Bezpieczny Autobus / Mój Pojazd | **Gratis** | | [VERIFICADO≥2] |
| **Upsell autoDNA** (informe completo) | **89,99 PLN** (may-2026) | producto comercial de autoDNA al que enlaza la tabla de riesgos; preview gratis de categorías | [NO-VERIFICADO≥2: single-source autocentrum/autodna, fecha may-2026] |

> Modelo: **bien público gratuito** financiado por presupuesto estatal. Sin ánimo de lucro. El único punto de pago es el **upsell a autoDNA** (tercero comercial), no el servicio gov en sí.

---

## 7. Placement (DÓNDE colocan cada dato) — núcleo para cardeep

> El informe ciudadano es una **SPA con 3 vistas/pestañas** (no scroll único). El orden es deliberado: **identidad estática → cronología de hechos → tabla de riesgos extranjeros**. El API separa **dato anonimizado por voivodato** (analítica) del **informe identificado** (consulta puntual).

| Dato / métrica | Dónde se coloca (vista / superficie) |
|---|---|
| Marca, modelo, año, motor, combustible, masa, plazas, fechas de matrícula | Vista **"Informacje"** (ficha técnica estática — lo primero) |
| Nº y tipo de propietarios (firma/persona) por tramo, voivodato | Vista **"Oś czasu"** (timeline) — eje de cambios de titularidad |
| Inspecciones técnicas (fecha + resultado + vigencia + próxima) | Vista **"Oś czasu"** — hitos de ITV |
| Odómetro/przebieg por inspección + control policial (serie temporal, detección de retroceso) | Vista **"Oś czasu"** — lecturas datadas junto a cada ITV; sustitución de cuentakm como flag |
| OC (vigencia/hasta cuándo) | Vista **"Oś czasu"** (estado legal) |
| Szkody istotne (daños relevantes UFG, desde 2020) | Vista **"Oś czasu"** — eventos de daño |
| Baja / robo / retirada temporal | Vista **"Oś czasu"** (estado legal) + tabla de riesgos |
| Tabla de riesgos extranjera (siniestro total, daño, robo intl., VIN-ISO, recall, desguace, zakaz ruchu, taxi, discrepancia odómetro) | Vista **"Dane zagraniczne" / Tabela ryzyka** — **flags verde/rojo**, rojo = confirmado (overlay autoDNA) |
| Odómetro extranjero (países previos) | Vista **"Dane zagraniczne"** (autoDNA, según disponibilidad) |
| Fotos de ITV (exterior/matrícula/cuentakm) | **Nueva sección 2026** (piloto SKP) [NO-VERIFICADO≥2] |
| 69 campos técnicos anonimizados, filtrables por voivodato+fecha | **CEPiK Open API `/pojazdy`** (superficie de analítica, no de consulta ciudadana) |
| Censo del parque por marca/combustible/voivodato (conteo por valor) | **`/slowniki/{nazwa}`** — `klucz-slownika` + `liczba-wystapien` |
| Datos del propio vehículo + multas + puntos | **Mój Pojazd** (mObywatel, autenticado) |
| OC/ITV/plazas/odómetro de autobús | **Bezpieczny Autobus** (por matrícula) |
| Upsell informe completo | enlace a **autoDNA** desde la tabla de riesgos |

**Lecciones de placement para cardeep:**
1. **Tres vistas, no scroll infinito:** *identidad técnica* (fría) · *línea de tiempo* (caliente, cronológica) · *tabla de riesgos* (veredicto rojo/verde). Separa el "qué es" del "qué le pasó" del "de qué hay que desconfiar".
2. **Odómetro como serie datada por evento de autoridad** (cada ITV/control), no como número suelto → el retroceso emerge solo.
3. **Propiedad como timeline tipo (firma vs. persona) sin PII** — replicable bajo RGPD: conteo + tipo, nunca el nombre.
4. **Diccionarios que devuelven frecuencia** = censo del parque gratis dentro del propio API. Patrón directo para el "censo" de cardeep: cada valor de un atributo trae su conteo.
5. **Zona estatal vs. zona de overlay comercial** visualmente distinguidas en la misma ficha (CEP = autoridad; tabla de riesgos = tercero). Modelo para mezclar dato propio con dato de socio sin engañar sobre la procedencia.
6. **Triple llave de identidad (matrícula+VIN+fecha)** como anti-scraping/anti-abuso del dato sensible, frente al "solo VIN" comercial.

---

## 8. Diferencial (lo que ofrece y otras no)

- **Autoridad estatal / fuente primaria:** es **el origen** del dato registral polaco. Los comerciales (autoDNA, carVertical, EpicVIN) **citan CEPiK como fuente**; aquí está sin intermediario, gratis. [VERIFICADO≥2]
- **Gratis y universal:** sin coste, sin registro para vehículo PL; cobertura del 100% del parque matriculado (lo que ningún comercial tiene). [VERIFICADO≥2]
- **Odómetro de autoridad** capturado en cada ITV oficial + control policial desde 2014 — dato difícil de falsear porque lo registra el Estado. [VERIFICADO≥2]
- **OC en tiempo real** (vigencia del seguro obligatorio) — dato regulatorio que un agregador no posee de forma autoritativa. [VERIFICADO≥2]
- **API abierta con diccionarios-frecuencia** → censo del parque por atributo (marca/combustible/voivodato/año) **gratis y oficial**; permite analítica de mercado del parque (no de precios). [VERIFICADO: en vivo]
- **Descarga masiva** de datos técnicos anonimizados (uso comercial permitido con atribución) — materia prima para terceros. [VERIFICADO]
- **Ecosistema de e-servicios** sobre la misma base: Bezpieczny Autobus, Mój Pojazd, puntos/multas — cobertura de casos de uso que un informe-VIN puro no toca. [VERIFICADO≥2]
- **Relación simbiótica con el privado:** integra autoDNA (riesgos+odómetro extranjero) en el servicio público — caso raro de partenariado Estado↔comercial bidireccional. [VERIFICADO≥2]

---

## 9. Gaps (lo que NO ofrece)

- **No es valoración:** sin **residual value %**, **trade/retail**, **days-to-sell**, **market days supply**, **price-to-market %**, curva de depreciación, índices oferta/demanda. Es historial registral, no inteligencia de precio. [VERIFICADO por ausencia]
- **Ciego al pre-importación:** CEP solo "ve" desde la **1ª matrícula en Polonia**; sin el overlay autoDNA/EUCARIS no hay historial extranjero. [VERIFICADO≥2: driverhub]
- **Sin fotos** del vehículo (hasta el piloto SKP 2026, aún emergente/no verificado≥2). [VERIFICADO≥2 ausencia histórica]
- **Sin equipamiento de fábrica** (PR-codes/opciones) en el informe ciudadano — el Open API da specs técnicas pero no la lista de opciones de fábrica. [VERIFICADO: driverhub, autobaza]
- **Sin historial de servicio/taller** (ASO), sin recalls propios (solo vía overlay autoDNA), sin coste de reparación. [VERIFICADO≥2]
- **Dato extranjero "muy escaso"** y de cifras inconsistentes (15–20 países según fuente). [VERIFICADO: driverhub]
- **API en `beta` e inestable:** en esta auditoría `/slowniki` (lista) devolvió **504** repetidos y `/pojazdy` **timeout (HTTP 000)**; solo `/slowniki/marka` respondió 200. Disponibilidad no garantizada. [VERIFICADO directamente]
- **Sin VIN/matrícula/PII en el API** (anonimizado) — no sirve para consulta por VIN programática; solo agregados por voivodato. [VERIFICADO: spec]
- **Triple llave obligatoria** (matrícula+VIN+fecha) para el informe — más fricción que el "solo VIN" comercial. [VERIFICADO≥2]
- **Sin DMS / feed / dashboard / Excel de mercado / webhooks.** [VERIFICADO por ausencia]
- **Gobernanza cuestionada (NIK):** sobrecoste y construcción perpetua → riesgo de fiabilidad/continuidad. [VERIFICADO≥2]
- **PDF no oficial:** explícitamente "no es documento para juzgado/administración". [VERIFICADO: gov.pl]

---

## 10. Fuentes

**Propias (Estado polaco):**
- https://www.gov.pl/web/gov/sprawdz-historie-pojazdu (servicio, campos, gratis, ryzyka extranjeros, límite 20/h)
- https://historiapojazdu.gov.pl/ → https://moj.gov.pl/.../HistoriaPojazdu (SPA del servicio; redirect observado)
- https://www.gov.pl/web/gov/sprawdz-autobus (Bezpieczny Autobus — campos)
- https://www.gov.pl/web/cyfryzacja/system-informatyczny-...-si-cepik- (instituciones que alimentan, base legal, e-servicios)
- https://www.gov.pl/web/cyfryzacja/otwieramy-przez-api-...-cepik (apertura API, datos estadísticos)
- https://www.gov.pl/web/cyfryzacja/nie-daj-sie-wywiesc-w-pole-nowa-usluga-w-historii-pojazdu (7 categorías extranjeras 2018, lanzamiento jun-2014)
- https://www.gov.pl/web/cepik/api-dla-...-api-do-cepik ("60+ parámetros", licencia comercial+atribución)
- https://www.gov.pl/web/cepik/statystyki + https://www.gov.pl/web/cepik/pojazdy-zarejestrowane-w-2025-roku (escala del parque)
- **https://api.cepik.gov.pl/swagger/apicepik.json** (OpenAPI spec descargado — **69 atributos `VehicleDto`** + endpoints + parámetros, version "beta" 1.2.3)
- **https://api.cepik.gov.pl/slowniki/marka** (llamada en vivo HTTP 200 — 7.922 marcas con `liczba-wystapien`)
- https://api.cepik.gov.pl/doc (Swagger UI)
- https://dane.gov.pl/pl/dataset/1558,... (dataset abierto, ficheros) + https://data.europa.eu (cross-list)
- http://www.cepik.gov.pl/ (portal; `/aktualnosci` Mój Pojazd, puntos karne, auta sprowadzane) [parcial: una página falló por SSL handshake antiguo del servidor]
- https://info.mobywatel.gov.pl/uslugi/bezpieczny-autobus + /dokumenty/moje-pojazdy (mObywatel)

**Terceros / verificación cruzada:**
- https://www.autodna.pl/blog/raporty-autodna-dostepne-rowniez-przez-usluge-historia-pojazdu-gov/ (partenariado 27-abr-2020, tabla 9 riesgos, 16 países, 0,5 mil M registros)
- https://autoexpert.pl/artykuly/autodna-historia-pojazdu (corrobora partenariado, odómetro extranjero, "mayor base gratis del mercado PL")
- https://www.nik.gov.pl/.../system-cepik.html + https://www.prawo.pl/samorzad/system-cepik-raport-nik-2024,527037.html (control NIK: sobrecoste, retrasos)
- https://www.swiatopon.info/artykuly/cepik-2-0-jednak-od-czerwca-2018 (cronología CEPiK 2.0 13-jun-2018, COI 2013)
- https://driverhub.pl/.../sprawdzenie-historii-pojazdu-kompletny-audyt-... (secciones del informe, szkody istotne 2020, fotos SKP 2026, comparación comercial)
- https://www.autobaza.pl/page/auto-ekspert/historia-pojazdu-gov-... (3 vistas Informacje/Oś czasu/Dane zagraniczne, gaps)
- https://car-dossier.com/poradnik/cepik-historia-pojazdu (EUCARIS, países, dato escaso)
- https://www.gazetaprawna.pl/.../9877782,7-mln-aut-nagle-zniknelo-z-cepik-2025... (35,5 M parque, −7,15 M limpieza 10-jun-2024)
- https://www.autocentrum.pl/.../vin-decoding-carfax-czy-autodna-... (upsell autoDNA 89,99 PLN may-2026) [single-source para precio]

---

### Notas de verificación
- **Naturaleza:** servicio público, no empresa → "owner"=Ministerstwo Cyfryzacji, operador=COI. Sin facturación/clientes de pago.
- **Campos del API:** los **69 atributos** proceden del **OpenAPI spec oficial parseado** (autoritativo), confirmados por `/slowniki/marka` en vivo y por la web ("60+ parámetros"). Anonimizados: **sin VIN/matrícula/PII**.
- **Campos del informe ciudadano:** reconstruidos de la página gov.pl (autoritativa para el alcance) + driverhub + autobaza (layout/secciones). La SPA xForms no renderiza headless → secciones tomadas de descripciones oficiales y reviews ≥2.
- **Categorías de riesgo extranjero:** dos conjuntos por época — **7 (CEP/EUCARIS, 2018)** vs **9 (overlay autoDNA, 2020+)**; se documentan ambos y se marca el origen. Solapan fuertemente.
- **Cifras de cobertura extranjera** (15 / 20 países, 4,5 M autos): **single-source y discrepantes** → marcadas [DISCREPANCIA]/[NO-VERIFICADO≥2].
- **Precio upsell autoDNA (89,99 PLN):** single-source, may-2026 → no verificado≥2.
- **Fotos SKP 2026:** single-source (driverhub) → feature emergente [NO-VERIFICADO≥2].
- **Fiabilidad API:** **verificada directamente** — `/slowniki` (lista) y `/pojazdy` devolvieron 504/timeout repetidos durante la auditoría; spec marcada "beta". Concuerda con el control NIK.
