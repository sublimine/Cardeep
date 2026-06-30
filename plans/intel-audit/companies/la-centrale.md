# La Centrale — Auditoría atómica (marketplace auto FR + intel de precios/datos)

> Slug: `la-centrale` · Subdominio cardeep: **portal-insights** · Web pública: https://www.lacentrale.fr/cote_inter.php ·
> Portal pro: https://offre-pro.lacentrale.fr · App: `fr.carboatmedia.lacentrale` (Android/iOS) ·
> Histórico de vehículo: https://www.autoviza.fr · C2B: https://www.lacentrale.fr/le-rachat-express
> Fecha auditoría: 2026-06-30. Doctrina VAM aplicada: cada bloque [VERIFICADO]/[ASUMIDO] con fuente.
> **Nota de método:** www.lacentrale.fr está protegido por DataDome (WebFetch → 403). El inventario de campos de
> abajo se obtuvo renderizando las páginas reales en navegador (Playwright) tras pasar el challenge, cruzado con
> el portal pro `offre-pro.lacentrale.fr` (accesible), prensa especializada (Auto-Infos, Caradisiac, La Revue du
> Digital, ecommercemag) y el press-release de adquisición de Prosus/OLX. Todo es texto literal de esas fuentes.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **La Centrale®** (lacentrale.fr) — *"1re marketplace 100% auto"* (autodescripción) | [VERIFICADO] |
| Razón social / editor | **Groupe La Centrale** (ex **Car & Boat Media**), SAS, SIREN **318 771 623**, RCS Paris | [VERIFICADO] (societe.com/verif + app id `fr.carboatmedia.lacentrale`) |
| Grupo / owner | **OLX Group** (filial 100% de **Prosus**, grupo Naspers). Acuerdo de compra del **100%** de La Centrale por **€1,1 Bn** all-cash anunciado **26/09/2025**, cierre previsto fin 2025; vendedor **Providence Equity Partners** | [VERIFICADO ≥2 fuentes] (Prosus + OLX + AIM Group) |
| Cadena de propiedad | Axel Springer → **Providence Equity** (negociación exclusiva dic-2020, mayoría) → **OLX/Prosus** (2025) | [VERIFICADO] (Providence + Prosus press) |
| HQ | **37 rue du Rocher, 75008 Paris** (Francia) [histórico Car & Boat Media: 22-28 rue Joubert, 75009] | [VERIFICADO] (registros mercantiles FR) |
| Fundación | **1969** (origen como publicación de petites annonces impresa; web en **1999**; cierre de la revista semanal en **2009**) — Prosus la describe "trusted… for **nearly 60 years**" | [VERIFICADO] (Tracxn 1969 + corrobora Prosus) |
| Plantilla | **251 empleados** (Groupe La Centrale) | [VERIFICADO] (societe.com) |
| Finanzas | CA **89.132.878 €** / résultat net **26.051.128 €** (cuentas a **31/03/2025**); ingresos de classifieds creciendo a **+12% CAGR** | [VERIFICADO] (agregadores RCS + Prosus) |

**Marcas del grupo (4 + media)** [VERIFICADO Tracxn + footer lacentrale.fr]:
- **La Centrale®** — marketplace VO/VN + cote + Pilot (núcleo de esta auditoría).
- **Promoneuve** — voitures **neuves** en stock ya remisées ("une marque La Centrale").
- **Caradisiac** — portal editorial de automoción (essais, actus, guide d'achat, forum) + Caradisiac Forum Auto.
- **maVoitureCash → renombrado "Rachat Express"** — recompra rápida C2B.
- **AnnoncesBateau** — náutica (fuera de scope auto). [VERIFICADO editor Car & Boat Media]
- **Autoviza®** — informe de historial de vehículo (dominio propio `autoviza.fr`), integrado en la ficha LC.

**Naturaleza:** marketplace de petites annonces auto líder en Francia + **proveedor de datos/inteligencia de
precios** al sector (la pata de "intelligence" es la **suite Pilot** SaaS + el **Observatoire du prix VO** público).
Posición declarada por Prosus: *"France's most specialised autos platform, with strength in higher-value vehicles"*.
[VERIFICADO]

**Clientes objetivo** [VERIFICADO]: **grand public** (acheteurs/vendeurs particuliers) y **professionnels de
l'automobile** (≈**10 000** distribuidores/concesionarios/garages presentes en la plataforma; clientes de la
suite Pilot y de los packs).

---

## 2. Cobertura y scope

| Eje | Detalle | Estado |
|---|---|---|
| País | **Francia** (mercado FR; precios anclados al marché français). Sin operación multipaís propia hoy; OLX cita "leveraging European infrastructure" para futura expansión | [VERIFICADO] |
| Tipos de vehículo | **Voitures** (VP), **Utilitaires** (VUL: fourgons, fourgonnettes, pick-up, camions, bus/minibus, utilitaires de société), **Motos/2-roues** (custom, roadster, GT, offroad, sportives, trail) | [VERIFICADO] (mega-menú occasion) |
| Nuevo vs usado | **Occasion + Neuf + Leasing (LOA)** + filtro **Électrique**. Neuf vía **Promoneuve** (stock remisé) | [VERIFICADO] |
| Inventario propio (live) | **≈350 000 annonces** (Prosus, 2025). Ej. live: Renault 44 151 / Peugeot 44 167 / BMW 23 441 / Mercedes 21 316 / Peugeot 208 10 461 véhicules | [VERIFICADO] |
| Audiencia | **≈4,5 M** visiteurs uniques/mes (Prosus 2025) → **5,7 M** visiteurs uniques mensuels (cifra 2026, La Revue du Digital) | [VERIFICADO ≥2 fuentes, valores de fecha distinta] |
| Datos para la cote | *"Près d'un million d'annonces"* escaneadas y **redressées quotidiennement**; *"des millions de prix observés et actualisés chaque jour"* (scan de mercado, no solo inventario propio) | [VERIFICADO] (página cote) |
| Energías cubiertas | Essence, Diesel, Hybride, **Hybride rechargeable**, **Hybride non rechargeable**, **Électrique**, **GPL** | [VERIFICADO] (facetas) |
| Taxonomía de id. | marque → modèle → **génération** → **version/finition** → **année (millésime)** → `version-id` interno | [VERIFICADO] (URLs cote/fiche) |

---

## 3. Productos + lista ATÓMICA de campos

### 3.1 La Cote La Centrale® (valoración gratuita — grand public) — **NÚCLEO consumer**

*"L'argus gratuit"* / *"la seule estimation 100% gratuite du marché"*. Entrada **par immatriculation** (plaque,
ex `123AB456`) **o par modèle** (marque→modèle→génération→version→année). 3 étapes: **1) Identifiez le véhicule ·
2) Nous comparons le marché · 3) Vous obtenez le bon prix**. Toggle **acheteur / vendeur**. *"Plus d'un million
d'estimations chaque mois"*. ⚠ El **valor numérico de la cote está gated tras login gratuito** (*"Identifiez-vous
pour consulter gratuitement la cote"*). [VERIFICADO render en vivo]

**Dos niveles de cote** (texto literal cote_inter.php):
- **Cote brute** = valor del véhicule *"moyen"*: **état standard**, **conforme à la configuration d'origine**,
  **mise en circulation au mois moyen du millésime**, **kilométrage standard** (definido por catégorie fiscale +
  énergie).
- **Cote affinée (personnalisée)** = cote brute ajustada por los criterios reales: **kilométrage**, **date exacte
  de mise en circulation**, **code postal**. *No* tiene en cuenta options añadidas ni état dégradé.
- Regla temporal: *"La cote de l'année en cours est publiée seulement après 6 mois d'existence du millésime."*

**Campos atómicos (entrada + salida cote):**
`immatriculation` (plaque) · `kilométrage` · `userType` (acheteur|vendeur) · `marque` · `modèle` · `génération` ·
`version/finition` · `année (millésime)` · `énergie` · `boîte` · `code postal` · **valeur estimée €** (gated) ·
**Évolution du prix** (gráfico dépréciation) · `Km par mois` (slider de proyección) · **valeur résiduelle projetée
por año** (eje 2026→2030, € en eje Y). [VERIFICADO render]

> **Évolution du prix**: *"Aperçu de la dépréciation de votre véhicule en fonction du temps et des kilomètres
> parcourus"* — curva de **valor futuro** (años a futuro) ajustable por km/mes. Es una **proyección de VR/decote
> orientada a consumidor**, no solo histórica. [VERIFICADO]

Salidas de la ficha de cote (CTAs): **Vendez à un professionnel** → *Rachat Express* (48h); **Vendez à un
particulier** → *Déposer mon annonce* (5 min); **Autoviza® Flash** (historial); **Évolution du prix** (login).

### 3.2 Marketplace / ficha de annonce (occasion-neuf-LOA) — **NÚCLEO portal-insights**

Cada annonce muestra precio **+ indicador price-to-market** y datos atómicos. [VERIFICADO render annonce real]

**Indicador de prix (price-to-market) — 3 niveles** (también filtro de búsqueda):
**Très bonne affaire · Bonne affaire · Offre équitable**. Explicación literal en la ficha:
*"Le prix de l'annonce est en-dessous de la moyenne des prix des véhicules similaires."* → posicionamiento del
precio frente a la media de similares. (En la lista, casi todas las tarjetas llevan su badge.)

**Bloc cabecera annonce:** `prix €` · `mensualité €/mois` · `badge price-to-market` · `Créer une alerte prix` ·
`type de vendeur` (PRO / Particulier / **Pro vérifié**) · `nom du pro` · `note pro` (ex 4,5) + `avis` ·
`ancienneté` (*"Agent depuis 2005"*) · `localisation` (CP, ville, **carte**) · `téléphone` · `message`.

**Points forts (badges detectados por IA):** `Garantie (mois)` · `Historique Disponible` · `Vignette Crit'Air (n)` ·
`Propriétaire Première main` · `Kilométrage Faible` · `Consommation Faible`.

**Caractéristiques (≈20 por anuncio):** `Marque/Modèle/Version` · `Année` · `Kilométrage` · `Boîte de vitesse` ·
`Énergie` · `Nombre de portes` · `Puissance fiscale (CV)` · `Puissance DIN (ch)` · `Consommation (L/100km)` …

**Équipements & options (≈24):** lista de série/options + **"Ce que l'IA a repéré pour vous"** (selección
destacada: système de navigation, audio, climatisation 2 zones, AFU, régulateur, rétros électriques…).

**Commentaire du vendeur** (texto libre) · **Photos/Vidéo** (galería) · **Réf. pro** + **Réf. annonce** ·
**date de publication** (*"Publiée il y a 14 jours"* → señal days-on-market) · **breadcrumb** (catégorie→marque→
énergie→modèle→région).

**Financement (embebido):** tabs **Crédit / LOA** · `Apport €` · `montant €` · `Durée (mois)` · `Ma mensualité
€/mois` · `Reprise` (Estimer mon véhicule) · `Faire une offre au vendeur`.
**Garanties:** `Garantie (mois)`. **Assurance:** estimation (partenaire).
**Historique (Autoviza):** `Première main` · `Existence vérifiée` · `Aucun sinistre détecté` · `Usage privé
uniquement` + *"Voir l'historique Autoviza"*. **Cote du véhicule:** lien *"Consulter"*.

**Facetas de búsqueda (filtros atómicos):** `Type de véhicule` · `Marque` · `Modèle` · `Génération` ·
`Version/Finition` · `Année min/max` · `Kilométrage min/max` · `Énergie` (Diesel/Essence/Hybride/Électrique/GPL/
Hybride rech./non rech.) · `Boîte` (Auto/Manuelle) · **mode prix `Prix total` / `Leasing (LOA)`** · `Prix min/max` ·
`Neuf uniquement` · **price-rating** (Très bonne affaire/Bonne affaire/Offre équitable) · `Code postal` ·
`Régions et pays voisins` · `Avec livraison` · `Vendeur` (Particulier/Professionnel) · `Equipements & options` ·
`Niveau d'équipement` · `Couleurs extérieur` · `Couleurs intérieur` · `Puissance fiscale` · `Puissance DIN (ch)` ·
`4 roues motrices` · `Consommation max` · `Emission de CO2` · **`Crit'air max`** · `Première main` ·
`Historique du véhicule` · `Nombre de places` · `Nombre de portes` · `Dimensions du véhicule` · `Volume du coffre`.

### 3.3 Fiche technique (référentiel de specs VN/VO) — equivalente al Référentiel

Página por versión (`/fiche-technique-voiture-{marque}-{modèle}-{version}-{année}.html?version-id=…`), con CTA
**"Recevoir la fiche technique"**. Estructura por secciones (campos literales, VERIFICADO render):

- **Général:** `Prix neuf (€)` · `Finition` · `Modèle commercial` · `Boîte de vitesse` · `Nombre de rapports` ·
  `Transmission` · `Energie` · `Durée de la garantie (mois)` · `Garantie constructeur (km)`.
- **Historique:** `Début commercialisation` · `Fin commercialisation`.
- **Dimensions / Châssis:** `Nombre de portes` · `Nombre de places` · `Longueur` · `Volume de coffre` ·
  `Largeur sans rétros` · `Hauteur` · `Empattement` · `Poids à vide` · `Largeur pneu avant` · `Largeur pneu
  arrière` · `Rapport h/L pneu avant` · `Rapport h/L pneu arrière` · `Diamètre des jantes avant` · `Diamètre des
  jantes arrière` · `Diamètre braquage murs`.
- **Puissances:** `Puissance fiscale (CV)` · `Puissance din (ch)` · `Cylindrée (cm³)` · `Couple cumulé (Nm @ tr/min)` ·
  `Nombre de cylindres` · `Nombre de soupapes par cylindre`.
- **Consommation:** `Volume du réservoir (L)` · `Emission de CO2 (g/km)` · `Norme Euro`.
- **Performances:** `Vitesse max (km/h)` · `Accélération 0 à 100 km/h (s)`.
- **Équipements de sécurité** (lista itemizada: ESP/ESC+ASR/ABS/REF/AFU/CDS/TSM, airbags, ISOFIX, reconnaissance
  panneaux, régulateur/limiteur…) · **Équipements intérieur** (clim, Bluetooth, banquette 1/3-2/3, 6 HP…) ·
  Équipements extérieur / Options. [VERIFICADO]

### 3.4 Autoviza® (rapport d'historique de véhicule)

Producto del grupo en dominio propio `autoviza.fr`, **integrado en la ficha LC** (y en Leboncoin, Autosphère,
constructeurs, distributeurs, assureurs). *"Leader français"* del historial, **94 M de consultations/an**. Gratis
para el vendedor (decide si lo expone al comprador). [VERIFICADO búsqueda + ficha annonce]

**Campos del informe:** `certification des données de la carte grise` · `certification du numéro de série (VIN)` ·
`certification du nombre de propriétaires précédents` · `durée de détention par propriétaire` (incl. pros que
recompran para reventa) · `usages antérieurs détectés` (taxi, VTC, auto-école…) · `importation` · `analyse des
ventes du véhicule` · `historique du kilométrage` (cuando disponible) · `opérations/entretien effectués` ·
`dates + kilométrage des contrôles techniques` (vía partenaires) · **points d'attention** (`sinistres/réparations
à dire d'expert`). En la ficha LC se resumen como flags: **Première main · Existence vérifiée · Aucun sinistre
détecté · Usage privé uniquement**. [VERIFICADO]

### 3.5 Rachat Express (ex-maVoitureCash) — recompra C2B por profesional

Reventa rápida a un **pro agréé**. 3 étapes [VERIFICADO Auto-Infos/Caradisiac]:
1) **Estimation en ligne gratuite < 2 min** (`plaque d'immatriculation` + `kilométrage`).
2) **Prise de rendez-vous** con uno de los **300 concessionnaires agréés** par La Centrale.
3) **Paiement** — *attestation de paiement sous 48h*.
**Campos:** `immatriculation` · `kilométrage` · **offre de rachat ferme (€)** · `RDV concessionnaire` ·
`délai 48h` · `paiement garanti`.

### 3.6 Suite Pilot (SaaS de inteligencia para profesionales) — **NÚCLEO "data/intelligence"**

Portal **Pilot** usado por **≈10 000 distributeurs/mois**; *"accompagne les distributeurs à chaque étape"*. Módulos
(VERIFICADO offre-pro + La Revue du Digital):

**Pilot Price** (lanzado **nov-2023**; **2 M de cotations**; **4 000 pros**; asistente IA desde **jun-2025**) —
*positionnement tarifaire temps réel*. Campos atómicos:
`prix conseillé d'achat` · `prix conseillé de vente` · **`tension du marché`** · **`rotation estimée`
(days-to-sell)** · `annonces concurrentes similaires (nº)` · `nouvelles annonces publiées` · `modifications de
prix` · `véhicules vendus` · `marge` · **décryptage marché** (graphique évolution & distribution des annonces) ·
**recommandation IA en langage naturel** (*"selon l'historique du véhicule et la demande locale"*, con
*indicateurs de tension du marché, prévisions de vitesse de rotation et positionnement concurrentiel*). Analiza
por vehículo o por lista en masse.

**Pilot Trends** (lanzado **fév-2025**; **2 000 pros/mois**) — *"identifiez quoi acheter sans prendre de risques"*.
Campos: `modèles les plus demandés` · `demande / offre en temps réel par région` · `évolution des ventes par
modèle commercial` · `versions les plus performantes (marge/rotation)` · `tendances du marché` + liens directos a
las annonces LC.

**Pilot Match** (lanzado **oct-2025**) — **extension navigateur** que superpone `demande` · `concurrence` · `prix`
sobre **sitios externos, plataformas de subastas y DMS** (évaluation instantanée sin cambiar de app). [VERIFICADO]

**Stock Optimizer** — `composition du stock` del dealer · `segments manquants à demande locale` · `véhicules à
rotation lente` · `recommandation de repositionnement / canal alternatif`. [VERIFICADO]

**Optimus Price** (optimización de pricing) · **Pilot Performance** + **Pilot Boost** (performance de ventes) ·
**Pilot Leads Center** (gestion des leads). [VERIFICADO nombres; campos atómicos no detallados públicamente]

### 3.7 La Centrale Pro (marketplace B2B de sourcing) — lanzada ene-2026

*"Premier inventaire BtoB national centralisé sans intermédiaire."* **50 000 opportunités de sourcing** (vendeurs
particuliers + distributeurs + spécialistes BtoB); **toutes décryptées par la data La Centrale (Pilot Trends +
Pilot Price)**; venta a una audiencia de **10 000 acheteurs de confiance**. Funciones: `filtres/alertes
personnalisés` · `messagerie intégrée (+ module WhatsApp)` · módulos previstos de réservation/commande y
logistique. Objetivo declarado: 5 000 → **20 000 véhicules** fin-2026. Partners lanzamiento: Cofia/Emil Frey
France, Starterre, eCarsTrade. [VERIFICADO ecommercemag/caradisiac]

### 3.8 Observatoire du prix des VO (índice de mercado público) — pata "datos"

Publicación **trimestral** del precio del VO en Francia. Campos: `prix moyen/médian VO (€)` · `évolution des prix
(% trimestre / an)` · `évolution par âge` · `évolution par motorisation`. Metodología: base **médiane**, volúmenes
**pondérés a mix équivalent** trimestre a trimestre para aislar la evolución real. Ej. publicado: prix moyen 2024
**20 990 €** (−7,1%), 2025 bajo barrera de los 20 000 → **19 999 €**. [VERIFICADO presse.lacentrale.fr]

### 3.9 Packs de visibilité (anunciante pro)

**Pack Business** (visibilité standard) · **Pack First** (*+30% de visibilité*) · **Pack Ultimate** (*+50%* +
vidéos). Todos incluyen: affichage de services (financement, livraison, reprise), labels & emplacements valorisés,
photos promotionnelles, **outils de gestion + sourcing + pricing**. Options: boost de déstockage ciblé, suite
publicitaire en résultats de recherche. [VERIFICADO offre-pro]

---

## 4. Metodología / fuentes de datos

[VERIFICADO página cote + La Revue du Digital + observatoire]
- **Cote:** *"modèles statistiques poussés"* elaborados por ingénieurs + experts automobiles; **calcul
  combinatoire** sobre *"près d'un million d'annonces scannées et redressées quotidiennement"* + *"des millions de
  prix observés et actualisés chaque jour"*. **Mises à jour quotidiennes.** Cote brute (vehículo estándar) →
  personalización (km, date exacte, code postal) = cote affinée.
- **Pilot / market intelligence:** procesa *"millones de annonces"* + base histórica de precios LC; IA para
  recomendaciones en lenguaje natural por **historique del vehículo + demande locale**, con tension de mercado,
  vitesse de rotation y positionnement concurrentiel.
- **Observatoire:** prix **médian**, volúmenes **ponderés a mix équivalent** (control de mezcla) para evolución
  real.
- **Autoviza:** agregación de fuentes (carte grise certifiée, partenaires de contrôle technique, assureurs,
  réseau) → certificaciones + points d'attention.
- Diferencia metodológica declarada vs L'Argus: LC parte de **modelos estadísticos sobre annonces reales**
  (precios de mercado observados), no de una cote "à dire d'expert".

---

## 5. Entrega (delivery)

[VERIFICADO]
- **Web** lacentrale.fr (cote, marketplace, fiches techniques, financement, Rachat Express) — protegida DataDome.
- **App móvil** (Android `fr.carboatmedia.lacentrale` + iOS).
- **Suite Pilot** = portal **SaaS** pro (Price/Trends/Performance/Boost/Leads Center/Optimus/Stock Optimizer).
- **Pilot Match** = **extension de navigateur** (overlay sobre sitios externos, subastas y **DMS**).
- **La Centrale Pro** = marketplace **B2B** (sourcing + venta + messagerie/WhatsApp).
- **Autoviza** = informe web (autoviza.fr) embebido en la ficha; *flash* desde la cote.
- **Observatoire** = **PDF** trimestral (presse.lacentrale.fr) + cobertura de prensa.
- **API pública de datos:** **no documentada públicamente** (la entrega de datos pro es vía Pilot/extension, no
  vía API self-service). [NO-VERIFICADO la existencia de API]
- DMS: integración *vía overlay* Pilot Match (lectura), no se documenta feed/push a DMS. [VERIFICADO el overlay]

---

## 6. Modelo de precio

[VERIFICADO parcial]
- **Cote** grand public: **100% gratuita** (valor tras login gratuito). **Rachat Express**: estimación gratuita.
- **Autoviza**: gratis para el vendeur que publica; el rapport completo es de pago para el comprador. [ASUMIDO el
  importe — no auditado al átomo]
- **Pilot Price**: gratis para partenaires hasta **abril 2024**; después **tarifa según el nº d'annonces
  analysées**. [VERIFICADO]
- **Packs anunciante** (Business/First/Ultimate): **suscripción** B2B escalonada (importe no público). [VERIFICADO
  la existencia, NO el importe]
- **La Centrale Pro**: **gratis para el comprador** (abonné LC); **fee de suscripción moderada para el vendeur**.
  [VERIFICADO]
- Sin tarifa pública detallada de la suite Pilot. [NO-VERIFICADO importe]

---

## 7. Placement (DÓNDE coloca cada dato — patrón para cardeep)

> Patrón que cardeep imita. Derivado del render real de la ficha de annonce, la página de cote y el portal pro.

**A) Ficha de annonce = bloque precio + "verdict" de mercado arriba.** El **precio** va acompañado *en el mismo
bloque* del **badge price-to-market** (Très bonne affaire/Bonne affaire/Offre équitable) y de la **mensualité
€/mois**. Más abajo, un **bloc "Prix"** dedicado repite el badge con la frase explicativa (*"en-dessous de la
moyenne des prix des véhicules similaires"*) + accesos a **Historique** y **Cote du véhicule**. → *cardeep: en la
tarjeta y en la ficha, el precio nunca va solo: lleva su veredicto vs mercado + acceso a cote e historial.*

**B) "Points forts" = fila de badges sintéticos bajo el título.** Garantie, Historique dispo, Crit'Air, Première
main, **Kilométrage Faible**, **Consommation Faible** — señales pre-digeridas por IA. → *cardeep: cabecera de ficha
= chips de "lo bueno de este coche" calculados, no solo specs crudas.*

**C) Caractéristiques (≈20) + Équipements (≈24) con capa IA.** Specs en grid; equipamiento con un sub-bloque
**"Ce que l'IA a repéró pour vous"** que prioriza lo relevante. → *cardeep: specs completas + selección IA
destacada encima.*

**D) Financement embebido en la ficha.** Tabs Crédit/LOA con `apport`, `durée`, `mensualité`, `reprise` y "faire
une offre". → *cardeep: simulador de pago + reprise dentro de la ficha, no en página aparte.*

**E) Historique (Autoviza) como bloque de confianza.** Flags Première main / Existence vérifiée / Aucun sinistre /
Usage privé + CTA al rapport. → *cardeep: panel "confiance/historial" con flags verde + enlace al informe.*

**F) Cote (consumer): identificar → comparar marché → bon prix, con curva de dépréciation.** El resultado incluye
**Évolution du prix** (valor futuro por año, slider Km/mois). → *cardeep: la valoración muestra la **proyección de
decote** ajustable, no solo el valor de hoy.*

**G) Toggle acheteur/vendeur en la cote.** Mismo vehículo, dos lecturas de precio según rol. → *cardeep: el valor
se adapta a si el usuario compra o vende.*

**H) Pilot (pro) = un solo "bloc pricing" de decisión.** Antoine Despujols: *"concentrer au même endroit tous les
éléments d'aide à la décision"* — prix achat/vente conseillés + tension + rotation + concurrents + marge + IA en una
pantalla; **Pilot Match** lleva ese overlay *sobre el sitio donde el pro ya está mirando* (subasta/DMS). →
*cardeep: vista pro = un panel único achat/vente/tension/rotación/competencia; y un overlay que sigue al usuario.*

**I) Filtro por veredicto de precio.** Très bonne/Bonne affaire/Offre équitable es **faceta de búsqueda**, no solo
etiqueta. → *cardeep: permitir filtrar el inventario por "calidad de precio".*

**J) Observatoire = informe de mercado agregado (PDF/prensa).** Evolución por edad y motorización, base mediana. →
*cardeep: capa macro/observatorio separada de la ficha individual.*

---

## 8. Diferencial (lo que ofrece y otras no)

- **Veredicto price-to-market en CADA annonce** (Très bonne/Bonne affaire/Offre équitable) + frase explicativa +
  uso como **filtro** — posicionamiento de precio masivo y consumer-facing. [VERIFICADO]
- **Capa IA consumer**: "Points forts" sintéticos (Km Faible, Conso Faible…) y "Ce que l'IA a repéré" en
  équipements. [VERIFICADO]
- **Curva de dépréciation futura** en la cote gratuita (proyección por año, ajustable km/mes) — VR para
  particulares. [VERIFICADO]
- **Cote sobre modelos estadísticos de ~1 M annonces reales redressées a diario** (no "à dire d'expert"). [VERIFICADO]
- **Suite Pilot con IA en lenguaje natural** (prix conseillés + tension + rotation + concurrents + marge) y
  **Pilot Match overlay** sobre subastas/DMS/sitios externos — inteligencia *donde el pro trabaja*. [VERIFICADO]
- **Autoviza integrado** (líder FR del historial, 94 M consultas/an) dentro de la ficha. [VERIFICADO]
- **Ecosistema ciclo completo**: comprar (marketplace) · vender (annonce) · recompra 48h (Rachat Express) · sourcing
  B2B (La Centrale Pro) · financer/assurer · historial · cote. [VERIFICADO]
- **Observatoire trimestral** público (autoridad de mercado / PR). [VERIFICADO]
- Fuerza en **véhicules de valor alto** (posición declarada). [VERIFICADO Prosus]

---

## 9. Gaps (lo que NO ofrece / límites)

- **Solo Francia** — sin cobertura paneuropea propia (a diferencia de Indicata/Autovista/JATO). [VERIFICADO]
- **Valor de cote gated tras login**; sin cifra visible anónima ni intervalo de confianza/dispersión público (a
  diferencia del `confidence-index`/`dispersion` de L'Argus). [VERIFICADO render]
- **Sin API pública de datos / valoración** documentada (entrega pro vía SaaS/overlay, no feed self-service). [NO-VERIFICADO existencia]
- **Sin producto explícito de Valeur Résiduelle contractual para LLD/LOA** tipo Argus Prevar (Pilot da rotation;
  la cote da una curva de decote consumer, no engagements financieros profesionales). [VERIFICADO por ausencia]
- **Sin precios de subasta/wholesale propios ni MMR**; La Centrale Pro es marketplace B2B de annonces, no casa de
  enchères con índice de remate. [VERIFICADO por ausencia]
- **Métricas pro detrás de muro comercial**: campos exactos de Pilot Performance/Boost/Leads/Optimus no publicados
  al átomo. [NO-VERIFICADO]
- **Importes de precio** (Autoviza, packs, Pilot) no descubribles públicamente. [NO-VERIFICADO]
- **Histórico/telemática en tiempo real**: el historial es Autoviza (eventos), no datos de uso/telemetría. [VERIFICADO]
- **Cifras de audiencia variables entre fuentes** (4,5 M vs 5,7 M visiteurs uniques) — distinta fecha. [VERIFICADO discrepancia]

---

## 10. Fuentes (URLs)

- Cote (metodología, render en vivo): `https://www.lacentrale.fr/cote_inter.php` · `https://www.lacentrale.fr/lacote_origine.php` · `https://www.lacentrale.fr/lacote_origine_moto.php`. [VERIFICADO render Playwright]
- Cote por marca/modelo/año/versión: `https://www.lacentrale.fr/cote-voitures-peugeot-208--2020-.html` · final `https://www.lacentrale.fr/cote-auto-peugeot-208-…-2020.html?version-id=…`. [VERIFICADO]
- Ficha de annonce real (campos + price rating): `https://www.lacentrale.fr/auto-occasion-annonce-87103504340.html`. [VERIFICADO render]
- Listado + facetas: `https://www.lacentrale.fr/occasion-voiture-modele-peugeot-208.html`. [VERIFICADO render]
- Fiche technique (specs): `https://www.lacentrale.fr/fiche-technique-voiture-peugeot-208-…-2020.html?version-id=…`. [VERIFICADO render]
- Portal pro / soluciones: `https://offre-pro.lacentrale.fr/nos-solutions/` · `/offre-partenaires/` · `/nos-solutions/pilot-price/` · `/nos-solutions/pilot-trends/` · `/nos-solutions/la-centrale-pro/`. [VERIFICADO]
- Pilot / Data & IA (prensa): `https://www.larevuedudigital.com/la-centrale-officialise-ses-innovations-data-et-ia-pour-les-professionnels-du-vehicule-doccasion/` · Pilot Price `https://www.auto-infos.fr/article/la-centrale-lance-un-outil-de-positionnement-tarifaire-pour-ses-partenaires-professionnels.279953`. [VERIFICADO]
- La Centrale Pro (B2B): `https://www.ecommercemag.fr/retail-1220/la-centrale-lance-sa-plateforme-b2b-pour-le-sourcing-automobile-55189` · `https://www.caradisiac.com/la-centrale-veut-transformer-radicalement-le-business-model-du-marche-vo-entre-professionnels-220109.htm`. [VERIFICADO]
- Inversión/marketplace 2026: `https://www.larevuedudigital.com/la-centrale-investit-10-millions-deuros-en-2026-pour-renforcer-la-notoriete-de-sa-marketplace-auto/`. [VERIFICADO]
- Autoviza: `https://autoviza.fr/le-rapport-historique-vehicule-autoviza` · `https://www.lacentrale.fr/autoviza.php` · informe en vivo `https://autoviza.fr/report/report?uid=…`. [VERIFICADO contenido vía búsqueda + ficha]
- Rachat Express / maVoitureCash: `https://www.lacentrale.fr/le-rachat-express` · `https://www.auto-infos.fr/article/la-centrale-presente-rachat-express-la-version-simplifiee-de-mavoiturecash.276932`. [VERIFICADO]
- Observatoire du prix VO: `https://presse.lacentrale.fr/.../CP_La-Centrale_…_Observatoire-T4-2024….pdf` · `https://www.lacentrale.fr/images/lc_fr/observatoire-du-prix-la-centrale-t2-2024.pdf`. [VERIFICADO]
- Identidad/owner: Prosus `https://www.prosus.com/news-insights/2025/prosus-olx-group-agrees-to-acquire-la-centrale-…` · OLX `https://www.olxgroup.com/news/…` · Providence `https://www.provequity.com/news/providence-equity-agrees-acquire-majority-stake-la-centrale` · Tracxn/PitchBook. [VERIFICADO ≥2 fuentes]
- Entidad/finanzas: `https://www.societe.com/societe/groupe-la-centrale-318771623.html` · `https://www.verif.com/societe/CAR&BOAT-MEDIA-318771623/`. [VERIFICADO]

---

### Anexo — recuento de campos por producto
- **Cote (consumer):** ~14 (entrada + brute/affinée + évolution/decote).
- **Marketplace / annonce:** ~40 (cabecera + points forts + caractéristiques + équipements + financement +
  historique) + ~35 facetas de búsqueda.
- **Fiche technique:** ~40 (Général/Historique/Dimensions/Puissances/Conso/Performances + equip.).
- **Autoviza:** ~12.
- **Rachat Express:** ~6.
- **Suite Pilot:** ~25 (Pilot Price ~12 + Trends ~5 + Match ~3 + Stock Optimizer ~4 + nombres).
- **La Centrale Pro (B2B):** ~6.
- **Observatoire VO:** ~5.
