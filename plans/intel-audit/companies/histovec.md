# HistoVec — Auditoría de inteligencia competitiva

> **Slug:** `histovec` · **Web:** https://histovec.interieur.gouv.fr · **Subdominio asignado:** `official-data`
> **Fecha auditoría:** 2026-06-30 · **Categoría:** Registro/historial oficial de vehículo por matrícula (dato administrativo de Estado), NO analítica de mercado ni valoración/residuales.
> **Método:** WebSearch + WebFetch a fuentes oficiales (service-public.gouv.fr, beta.gouv.fr, securite-routiere.gouv.fr, comunicados Ministère de l'Intérieur) + lectura íntegra del **código fuente abierto** (GitHub `histovec/histovec-beta`, GPLv3) vía `gh api`: mapeo de campos del API público (`vehiculeMapping`), servicio SIV, constantes (contrôles techniques, opérations, critair, usage), tabs del informe y **tests Cypress E2E por pestaña** (placement y etiquetas exactas). El SPA del informe no renderiza headless; su estructura se reconstruyó desde el código fuente real (no inventada).

Etiquetas: `[V]` = verificado (leído en fuente directa) · `[V2]` = verificado en ≥2 fuentes · `[A]` = asumido/inferido (marcado, nunca presentado como hecho).

> **AVISO DE NATURALEZA (clave):** HistoVec **no es una empresa** ni un proveedor comercial de datos. Es un **servicio público gratuito y oficial del Estado francés** (Ministère de l'Intérieur). Es la **FUENTE AUTORITATIVA primaria** del dato administrativo del vehículo en Francia — exactamente el tipo de "official-data" que muchos competidores comerciales (Carfax, carVertical, AutoDNA, carVertical) revenden o agregan. Para cardeep representa el **patrón canónico de "dato oficial de Estado"**: qué campos publica un registro nacional, cómo los etiqueta y dónde los coloca.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre | **HistoVec** (de "historique du véhicule") | [V2] |
| Naturaleza | Servicio público gratuito y oficial del Estado francés | [V2] |
| Operador / owner | **Ministère de l'Intérieur** (Ministerio del Interior de Francia) | [V2] |
| Constructor | **La Fabrique Numérique du Ministère de l'Intérieur** (incubadora de startups d'État) | [V] (beta.gouv.fr) |
| Sponsor / dirección | **Délégation à la Sécurité Routière (DSR)** | [V] (beta.gouv.fr) |
| Programa | **beta.gouv.fr** — "Startup d'État" (modelo de servicio público digital) | [V2] |
| HQ | Francia (Ministère de l'Intérieur, París) | [V] |
| Investigación/construcción | **2018-03-01** | [V] (beta.gouv.fr) |
| Lanzamiento beta | **2018-07** (julio 2018) | [V2] |
| Lanzamiento oficial | **2019-01** (enero 2019) | [V2] |
| Estado del programa | **"Transféré"** (graduado de la incubadora, transferido a la administración, 2019-07) | [V] |
| Equipo (actual/histórico) | Christophe Le Coz (adjunto jefe de bureau), Leo-Tena Gassama N'Diaye (accesibilidad), ex: Richard Violet (intraemprendedor), Philippe Bron (dir. lab), Philippe Libat (Dev/Ops) | [V] (beta.gouv.fr) |
| Licencia del código | **GNU GPL v3.0**, open source en GitHub `histovec/histovec-beta` | [V] |
| Stack técnico | Vue.js 2.6, Elasticsearch 6.7+, nginx 1.15+, Redis (cache UTAC), Docker; UI sobre **DSFR** (Système de Design de l'État, clases `fr-*`) | [V] (README + tests) |
| App móvil | "**Histovec Check**" en App Store iOS (editor a verificar; posible tercero, no confirmado oficial) | [A] |
| Problema que ataca | "~la mitad de las ventas de ocasión contienen fraude" (estudio DGCCRF 2015) | [V] (beta.gouv.fr) |

**Posicionamiento:** transparencia en la compraventa de ocasión **entre particulares** (y profesionales) mediante el **dato oficial del registro nacional**. El vendedor genera y **comparte** el informe; el comprador compra "en conocimiento de causa". El servicio "debería revestir carácter **obligatorio** a término" (declarado en el propio README del Ministerio). | [V2]

**Métricas de uso:**
- README del repo (era ~2019-2021): **2.500–3.500 informes únicos/día**; el carácter obligatorio lo llevaría a **~15.000/día**. | [V]
- Fuentes terciarias (dic-2025): **~300.000 informes/mes** y **>9.000.000 informes** acumulados desde la creación. | [V] (≥2 terceros citan la misma cifra → tratar como aprox.)

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| País | **Solo Francia** (matriculaciones francesas) | [V2] |
| Fuente primaria | **SIV** — Système d'Immatriculation des Véhicules (fichero nacional de matriculación) | [V2] |
| Fuente secundaria | **UTAC-OTC / UTAC-CERAM** (organismo técnico) para historial de contrôles techniques + kilometraje, vía interfaz API con cache Redis | [V] |
| Formato de matrícula | **SIV** (post-2009, formato AA-123-AA) y **FNI/IVT** (pre-2009, formato antiguo) | [V2] |
| Tipos de vehículo | **Todos**: motos, coches (VP), vehículos pesados/camiones, agrícolas, colección, etc. (sin restricción de género) | [V2] |
| Scope | **Vehículo de ocasión** (usado) — historial administrativo. NO valoración ni estado mecánico. | [V2] |
| Limitación de antigüedad | Matrículas antiguas (FNI, pre-2009): datos parciales/incompletos (ficheros papel mal transcritos, errores antiguos de captura). Sin kilometraje si el coche nunca pasó CT francés. | [V2] |
| Vehículos extranjeros | **Fuera de scope** (solo registro francés) | [V] |
| Idioma | Francés (servicio nacional) | [V] |

### Volumen de datos de desarrollo (orden de magnitud del dataset de pruebas)
- Jeu de données de dev: ~2.000 vehículos SIV (post-2009) + ~700 IVT (pre-2009) = ~3.000 registros en el índice Elasticsearch `siv` de pruebas. (El dataset real de producción del SIV cubre **todo el parque francés**, decenas de millones.) | [V] (README; producción = parque nacional [A])

---

## 3. Productos + campos atómicos

HistoVec es esencialmente **un único producto** (el informe oficial por matrícula) entregado por varios canales. No vende métricas sueltas; expone el **estado administrativo y técnico oficial** del vehículo tal como consta en el SIV + UTAC.

### P1 — Rapport HistoVec (informe oficial; modo vendedor/propietario y acheteur)
El informe se organiza en **7 pestañas** (`REPORT_TABS`). Campos atómicos **verificados leyendo el mapeo del API público (`vehiculeMapping`) + tests Cypress por pestaña** (etiquetas y códigos de carte grise exactos):

#### 3.0 Synthèse (resumen / "Résumé") — campos derivados
- **Modèle**: marca + nombre comercial (ej. "CITROEN C1")
- **Puissance fiscale** (ch)
- **Propriétaire actuel**: nombre anonimizado (ej. "H**** S******"), **duración de tenencia** (años), **rango de titular** (1er, 2e, … titulaire)
- **Immatriculation**: fecha de primera matriculación
- **Situation administrative (síntesis)**: bandera con icono + veredicto ("Rien à signaler" / anomalía) cubriendo gages, opposition, vol…

#### 3.1 Véhicule — "Caractéristiques techniques" (26 campos, cada uno con su código de carte grise)
| # | Campo | Código carte grise |
|---|---|---|
| 1 | Marque (marca) | D.1 |
| 2 | Type variante version (TVV) | D.2 |
| 3 | Numéro CNIT | D.2.1 |
| 4 | Nom commercial (modelo comercial) | D.3 |
| 5 | Couleur (color) | — |
| 6 | Type de réception | — |
| 7 | Numéro d'identification véhicule (**VIN**, anonimizado) | E |
| 8 | PT techniquement admissible (kg) — PTTA | F.1 |
| 9 | PTAC (kg) | F.2 |
| 10 | PT en service (kg) — PTES | G |
| 11 | PTAV — poids à vide (kg) | G.1 |
| 12 | Catégorie (CE) — categoría UE | J |
| 13 | Genre (National) | J.1 |
| 14 | Carrosserie (CE) | J.2 |
| 15 | Carrosserie (National) | J.3 |
| 16 | Numéro de réception | K |
| 17 | Cylindrée (cm³) | P.1 |
| 18 | Puissance nette max (kW) | P.2 |
| 19 | Energie (tipo de combustible/energía) | P.3 |
| 20 | Puissance CV (fiscal) | P.6 |
| 21 | Places assises (plazas sentado) | S.1 |
| 22 | Places debout (plazas de pie) | S.2 |
| 23 | Niveau sonore (db(A)) | U.1 |
| 24 | Vitesse moteur (min⁻¹) — régimen | U.2 |
| 25 | CO2 (g/km) | V.7 |
| 26 | Classe environnement (CE) — clase ambiental | V.9 |

> Campos adicionales presentes en el **API** pero no mostrados en estas 26 filas de UI: **PTRA (F.3)** y **rapport_puissance_masse** (relación potencia/masa). El backend también deriva la **vignette Crit'Air** (`1`,`2`,`3`,`4`,`5`,`ELECTRIQUE`,`NON_CLASSE`). | [V]

#### 3.2 Titulaire et Titre — datos del titular y del título
- **Identité** (titular anonimizado: nombre y apellidos, o razón social + SIREN si persona moral)
- **Code postal** (anonimizado parcial)
- **Date de première immatriculation**
- **Date du certificat d'immatriculation actuel**
- **Nombre de titulaires** (nº de propietarios sucesivos)

#### 3.3 Situation administrative (la sección crítica) — cada ítem con estado NON/OUI + detalle
- **Gages** (prendas/financiación pendiente): por registro → **fecha** + **nom_creancier** (acreedor). Enlaza a service-public.fr F34107.
- **Oppositions** (oposiciones a la cesión), de 4 tipos:
  - **OVE** — opposition véhicule endommagé (procédure de réparation contrôlée): fecha
  - **OVEI** — opposition véhicule endommagé (variante): fecha
  - **OTCI** — opposition au transfert du certificat d'immatriculation: fecha
  - **OTCI-PV** — OTCI por amendes/procès-verbal (multas): fecha
- **Véhicule — Déclaré volé** (vehículo declarado robado, FOVeS): NON/OUI
- **Déclarations valant saisie (DVS)**: por registro → fecha + **nom_personne_morale** (autoridad)
- **Suspensions**: por registro → fecha + **motif** + **remise du titre** + **retrait du titre**
- **Certificat d'immatriculation (estado del título)**: **Déclaré volée** (CI robada), **Déclaré perdue** (CI perdida), **Duplicata** — cada uno NON/OUI; + **annulé** + **date_annulation** (en API)

#### 3.4 État véhicule / Procédures VE (véhicule endommagé) — daños "controlados"
- **Nombre de procédures VE** (nº de sinistres a réparation contrôlée)
- **Date dernière procédure VE** (último sinistro)
- **Date fin dernière procédure VE** (resolución)
- **Procédure VE en cours** (PVE activa)
- **Apte à circuler** (apto para circular tras el sinistro)
- **Usage agricole** (booleano)
- **Usage de collection** (booleano)

#### 3.5 Import en France (si importado)
- **Véhicule importé depuis l'étranger** (booleano)
- **Date d'import**
- **Date de première immatriculation à l'étranger**

#### 3.6 Historique — "Historique des opérations en France" (tabla Date | Opération)
Cronología completa de operaciones SIV. Vocabulario de **~120 tipos de operación** (`operations.json`), entre ellos:
- Primeras matriculaciones: véhicule neuf / véhicule d'occasion / à l'étranger / diplomatique / W Garage / provisoire
- **Changement de titulaire** (normal / pré-demande internet / diplomatique), **Changement de locataire** (LOA/LLD)
- **Procédure de réparation contrôlée (DEC_VE)**, **Premier/Second rapport d'expert**
- Gages: **Inscription / Cession / Radiation / Prorogation** d'un gage
- Oposiciones: **Inscrire/Lever OTCI**, **Inscrire/Lever opposition**, **Inscrire/Lever OVE**
- DVS: **Inscription/Levée/Renouvellement** d'une déclaration valant saisie
- **Déclaration de cession (vente)**, **Achat/reprise par un professionnel**
- **Déclaration d'intention de destruction**, **Destruction physique**
- **Duplicata**, **Perte du certificat**, **Modification caractéristiques techniques**, **Modification d'adresse / état civil**
- **Retrait de la circulation**, **Sortie de territoire**, **Réimmatriculation à l'étranger**, **Immobilisation (administrative)**, etc.
- Cada operación lleva **date** + **type** (+ **date_annulation** si anulada)

#### 3.7 Contrôles techniques (desde 2021-01-12, vía UTAC) — tabla Date | Nature | Résultat | Kilométrage
- **Date** del control
- **Nature** (`ct_nature` + libellé): **VTP** Contrôle/Visite Technique Périodique · **VTC** Contrôle/Visite Technique Complémentaire (Pollution) · **CV** Contre-Visite · **CVC** Contre-Visite Complémentaire (libellés cambian antes/después de la reforma del **2018-05-20**)
- **Résultat** (`ct_resultat` + libellé): **A/AP** Favorable · **S/SP** Défavorable (por defaillances majeures, desde 2018) · **R/RP** Défavorable por défaillances critiques · **X** Report de la visite
- **Kilométrage** registrado en cada paso (ej. "160,532 km") — base de detección de manipulación de cuentakilómetros
- **Date de mise à jour** del bloque CT; bandera **donnée_disponible** + mensaje de **erreur** si falla UTAC

#### 3.8 Kilométrage (pestaña dedicada)
- Misma serie de lecturas (fecha + km) de los contrôles techniques, presentada como **evolución del kilometraje** para detectar incoherencias/rollback. | [V]

### P2 — Certificat de Situation Administrative (CSA, ex-"certificat de non-gage") en PDF
- HistoVec **genera el CSA** descargable (código `frontend/src/utils/csaAsPdf/`), documento **legalmente obligatorio** que el vendedor debe entregar al comprador antes de la cesión. Reúne gages + oppositions. | [V] (código) / [V2] (rol legal en guías)

### P3 — Modo Professionnel
- La home ofrece "vendeur" o "**professionnel**" (`TYPE_PERSONNE = PARTICULIER | PRO`). Entrada por **raison sociale + SIREN**. El SIV gestiona "comptes partenaires" e integra aplicaciones ANTS para profesionales. Interfaz con herramientas terceras citadas en el código: **Capsule**, **UTAC-Ceram**. | [V]

### P4 — API pública (en el código fuente)
- Plugin `public-api` con **documentación Swagger** y validación Joi. Dos rutas:
  - **POST `/report_by_data`**: payload = titular (particulier `nom`+`prenoms` / personne_morale `raison_sociale`+`siren`) + `numero_immatriculation` + `numero_formule` (SIV) **o** `date_emission_certificat_immatriculation` (FNI) + opción `controles_techniques` (boolean, off por defecto).
  - **POST `/report_by_code`**: recupera el informe por un código (uuid) — usado para el rapport compartido (`/rapport-acheteur?key=<uuid>`).
- Salida JSON = el árbol `vehiculeMapping` completo (todos los campos de §3.1–3.7). | [V]
- **Disponibilidad/condiciones de acceso públicas: NO claramente documentadas.** Existe una rama `production_without_api_grand_public` (sugiere que el "API grand public" puede estar **desactivado en producción**) y el issue #336 ("API histovec ?", 2018) se cerró como baja prioridad sin compromiso público. → El API existe en el código y alimenta el frontend, pero **no consta un programa de acceso B2B abierto y documentado**. | [V] código / [A] disponibilidad externa

> **Requisito de identidad (privacidad RGPD):** no es una búsqueda libre por matrícula. Para generar el informe hay que aportar **datos identificativos del titular + nº de formule de la carte grise** — es decir, hay que **poseer la carte grise**. El comprador solo accede al informe **que el vendedor le comparte** (vía key/uuid). | [V2]

---

## 4. Metodología y fuentes de datos

- **Origen único y autoritativo:** el **SIV** (Système d'Immatriculation des Véhicules), fichero nacional del Ministère de l'Intérieur. HistoVec **no agrega fuentes de terceros** ni modela/estima nada: **republica el dato oficial**. | [V2]
- **Contrôles techniques + kilometraje:** integrados desde **2021-01-12** mediante interfaz con **UTAC-OTC** (organismo de control técnico), con **cache Redis** para limitar las llamadas. | [V2]
- **Seguridad/privacidad:** datos en base **cifrados AES256**; datos personales **hasheados SHA256**; titulares **anonimizados** en el informe (nombre enmascarado, VIN/plaque parcialmente ocultos). | [V] (README)
- **Frescura:** la base de datos se **actualiza una vez al día**; cada informe se **cachea 24 h** por búsqueda distinta. | [V]
- **Identificación:** por **matrícula + nº de formule** (SIV) o **matrícula + fecha de emisión del CI** (FNI). | [V]
- **Limitación estructural reconocida:** solo refleja lo que está en el SIV/UTAC. **Un accidente NO declarado al seguro / sin réparation contrôlée NO aparece.** Datos pre-2009 (FNI) incompletos. | [V2]

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **Informe web (SPA)** | `histovec.interieur.gouv.fr` — 7 pestañas; modo vendedor (`/rapport-vendeur`) y comprador (`/rapport-acheteur?key=<uuid>`) | [V2] |
| **Compartir** | Tras "Transmettre le rapport": enlace **copiable**, por **email**, **SMS** o **QR-code** | [V2] (README + guías) |
| **PDF — CSA** | Certificat de Situation Administrative descargable (documento legal) | [V] |
| **App móvil** | "Histovec Check" (iOS) | [A] |
| **API** | `/report_by_data`, `/report_by_code` (en código; acceso externo no documentado) | [V]/[A] |
| **Modo profesional** | Entrada por raison sociale + SIREN; integraciones SIV/ANTS (Capsule, UTAC-Ceram) | [V] |
| Velocidad | Informe en **< 30 s** | [V] (guías) |
| Validez del enlace compartido | **15 días** (varias guías) o **30 días** (otras) — **discrepancia entre fuentes, sin confirmación oficial directa** | [A] (reportado, no resuelto) |
| **NO ofrece** | feed/Excel masivo, dashboard analítico, valoración, integración DMS nombrada, búsqueda libre por matrícula | [V] (ausencia, ver Gaps) |

---

## 6. Precio

- **100% GRATUITO.** Servicio público financiado por el Estado; sin tarifas, sin suscripción, sin coste por informe, para particulares y profesionales. | [V2]
- **Aviso de fraude oficial:** ante el éxito del servicio, proliferan **sitios fraudulentos de pago** que imitan HistoVec y cobran por un dato gratuito; el Ministère advierte que el **único sitio oficial** es `histovec.interieur.gouv.fr`. | [V] (prensa lesfurets + comunicados)

---

## 7. Placement (DÓNDE se coloca cada dato — patrón a copiar por cardeep)

Estructura = **informe de pestañas** (DSFR `fr-tabs`, 7 pestañas fijas). Patrón: **pestaña Synthèse que resume con veredictos**, luego pestañas-detalle por dominio. Cada hecho administrativo se muestra como **par etiqueta → valor** con veredicto **NON/OUI** de alto contraste; las series temporales (CT, kilometraje, historial) como **tablas cronológicas**.

| Dato / métrica | Pestaña / pantalla | Forma de presentación |
|---|---|---|
| Modelo, puissance fiscale, propietario actual (tenencia, rango), 1ª matrícula, **síntesis de situación admin.** | **Synthèse** (pestaña 0, abre el informe) | 2 columnas, 4 bloques h4; veredicto con icono "Rien à signaler" |
| 26 características técnicas + códigos carte grise (D.1…V.9) | **Véhicule** (pestaña 1) | Tabla de 3 columnas: etiqueta · código · valor |
| Titular anonimizado, código postal, fechas de matrícula/CI | **Titulaire et Titre** (pestaña 2) | Lista etiqueta→valor + sub-bloque "Certificat d'immatriculation" |
| Gages, oppositions (OVE/OVEI/OTCI/OTCI-PV), volé, DVS, suspensions, estado del CI | **Situation administrative** (pestaña 3) | 2 columnas × 3 secciones h3; cada una con veredicto **NON/OUI** + enlace legal + detalle por registro (fecha, acreedor, motivo) |
| Cronología de operaciones SIV (matriculación, cesiones, gages, expert, destrucción…) | **Historique** (pestaña 4) | Tabla **Date \| Opération** |
| Contrôles techniques: nature, résultat, km | **Contrôles techniques** (pestaña 5) | Tabla **Date \| Nature \| Résultat \| Kilométrage** |
| Evolución del kilometraje | **Kilométrage** (pestaña 6) | Serie temporal (fecha + km) para detectar rollback |

**Lecciones de placement para cardeep:**
1. **Pestaña-síntesis primero** con veredictos binarios de alto contraste ("Rien à signaler") y los 4 hechos que más importan (modelo, propietario, 1ª matrícula, estado legal) antes de cualquier detalle.
2. Cada dato administrativo es **etiqueta → NON/OUI → detalle**, con **enlace a la norma** que lo define (didáctico/confianza).
3. Las **características técnicas** se muestran con su **código de documento oficial** (carte grise D.1…V.9): trazabilidad total dato↔fuente.
4. **Series temporales** (CT, kilometraje, historial) siempre como **tabla cronológica** con fecha; el kilometraje se aísla en su propia pestaña porque es la señal anti-fraude estrella.
5. **Anonimización por diseño** del titular/VIN/plaque en la cara visible.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Es la FUENTE oficial primaria**, no un agregador: el dato del SIV es el que Carfax/carVertical/AutoDNA intentan revender de segunda mano. Autoridad legal máxima en Francia. | [V2]
2. **Gratis y de Estado**: coste cero frente a los €15–35/informe de los comerciales. | [V2]
3. **Doble función legal**: genera el **Certificat de Situation Administrative (CSA / ex-non-gage)**, documento obligatorio para la venta. | [V]
4. **Contrôles techniques + kilometraje oficiales de UTAC** (desde 2021): lecturas km certificadas en cada inspección, no autodeclaradas. | [V2]
5. **Situación administrativa granular y normada**: 4 tipos de oposición (OVE/OVEI/OTCI/OTCI-PV), gages con acreedor, DVS con autoridad, suspensiones con motivo — vocabulario jurídico exacto. | [V]
6. **Procédures VE** (réparation contrôlée) con apto/no apto para circular: daño grave "oficial". | [V]
7. **Historial completo de ~120 tipos de operación** del registro (cesiones, destrucción, importación, immobilisation…). | [V]
8. **Privacidad por diseño** (RGPD): solo el poseedor de la carte grise genera; compartición por key; AES256/SHA256; anonimización. | [V2]
9. **Código abierto (GPLv3)** y servicio reproducible (modelo beta.gouv.fr). | [V]
10. **Crit'Air** derivado y características técnicas con códigos de carte grise. | [V]

---

## 9. Gaps (lo que NO ofrece)

1. **Cero inteligencia de mercado / valoración.** No hay: precio retail/trade, valor residual %, days-to-sell, market days supply, price-to-market %, índices demanda/oferta, curva de depreciación, ajuste por km a precio. Es **dato administrativo puro**, no analítica. | [V]
2. **Solo Francia.** No cubre vehículos extranjeros ni otros países (un competidor europeo necesita 27 "HistoVec" distintos). | [V2]
3. **No es búsqueda libre por matrícula.** Requiere datos del titular + carte grise (privacidad). El comprador depende de que el vendedor comparta. | [V2]
4. **Solo lo declarado al SIV/UTAC.** Accidentes no declarados al seguro, reparaciones informales, daños menores → **invisibles**. | [V2]
5. **Sin estado mecánico ni precio de compra**; no hay tasación ni inspección física. | [V] |
6. **Sin fotos** del vehículo ni evidencia visual. | [V] (ausencia)
7. **Pre-2009 (FNI) incompleto**; sin kilometraje si nunca pasó CT francés. | [V2]
8. **Sin API B2B abierta y documentada** (el API existe en código pero sin programa de acceso público claro; posible desactivado en prod). | [V]/[A]
9. **Sin feed/Excel/integración DMS** nombrada para uso masivo comercial. | [V] (ausencia)
10. **Sin curva de valor ni forecast**; sin safety/NCAP, recalls, desastres naturales (que sí dan competidores comerciales). | [V] (ausencia)
11. **Frescura diaria** (no tiempo real) y cache 24 h. | [V]

---

## 10. Fuentes

- https://histovec.interieur.gouv.fr/ — sitio oficial (home, vendedor, acheteur, FAQ). [V2]
- https://github.com/histovec/histovec-beta — **código fuente abierto (GPLv3)**: fuente atómica de los campos. [V]
  - `backend/src/plugins/public-api/util/mapping.js` — **árbol completo de campos del API** (`vehiculeMapping`, `controlesTechniquesMapping`). [V]
  - `backend/src/services/siv.js` — consulta Elasticsearch al índice SIV (campos `v`, `utac_ask_ct`, `utac_encrypted_immat/vin`). [V]
  - `backend/src/plugins/public-api/routes/reportByData.js` / `reportByCode.js` — **API payload/rutas** (Joi + Swagger). [V]
  - `backend/src/constant/controlesTechniques.js` — enums NATURE (VTP/VTC/CV/CVC) y RESULTAT (A/AP/S/SP/R/RP/X) + reforma 2018-05-20. [V]
  - `backend/src/constant/critair.js`, `usage.js`, `type.js` — Crit'Air, usos (AGR/COL), tipos (SIV/FNI, PARTICULIER/PRO). [V]
  - `frontend/src/assets/json/operations.json` — **~120 tipos de operación** del historial SIV. [V]
  - `frontend/src/constants/reportTabs.js` — las **7 pestañas** del informe (placement). [V]
  - `frontend/cypress/e2e/rapport/onglet*/casSimple.cy.js` — **etiquetas y placement exactos** por pestaña (Synthèse, Véhicule, Titulaire et Titre, Situation administrative, Historique, Contrôles techniques, Kilométrage). [V]
  - `README.md` — operador, stack, AES256/SHA256, 2.500–3.500 informes/día, plan obligatorio ~15.000/día, UTAC-CERAM, compartir por mail/SMS/QR. [V]
- https://www.service-public.gouv.fr/particuliers/vosdroits/R52957 — descripción oficial + campos del informe. [V2]
- https://beta.gouv.fr/startups/histovec.html — Startup d'État: constructor (Fabrique Numérique), sponsor (DSR), timeline 2018→transféré, equipo, fraude DGCCRF 2015. [V]
- https://www.securite-routiere.gouv.fr/.../histovec — confirmación oficial (gratuito/oficial). [V] (intento de fetch directo falló por timeout; confirmado vía índice de búsqueda y comunicados) 
- https://www.interieur.gouv.fr/.../histovec-un-service-gratuit-et-officiel... — comunicado del Ministère (gratuito, oficial, SIV). [V]
- https://iautos.fr/guides/histovec-gratuit-guide — guía detallada: secciones del informe, OTCI/FOVeS/VEI, generación < 30 s, límites. [V]
- https://www.toyota.fr/.../comment-utiliser-histovec — paso a paso vendedor/comprador, SIV vs FNI, enlace seguro. [V]
- https://www.lesfurets.com/.../histovec-au-succes-plate-forme-sites-frauduleux-fleurissent — éxito + sitios fraudulentos imitadores. [V]
- Fuentes terciarias (verifiervoiture.fr, carverif.fr, allure-automobile, business-auto, lolivier, eurofil) — ~300.000/mes y >9M acumulados, validez del enlace, contenido del rapport. [V] (concordantes; cifras tratadas como aprox.)

> **Aviso anti-alucinación:** (1) HistoVec es servicio público, **no empresa**; cualquier marco "empresarial" se ha adaptado a esa realidad. (2) Los **campos atómicos están leídos del código fuente real** (mapeo del API + tests), no inferidos. (3) La **disponibilidad pública del API** B2B NO está confirmada (existe en el código, rama `production_without_api_grand_public` sugiere posible desactivación en prod; issue #336 cerrado sin compromiso) → marcado [A]. (4) La **validez del enlace compartido** difiere entre guías (15 vs 30 días) y no se halló confirmación oficial directa → marcado [A]. (5) El editor de la app iOS "Histovec Check" no se confirmó como oficial → [A]. (6) Las cifras de uso (9M / 300k mes) provienen de terceros concordantes, no de un dashboard oficial leído → aprox.
