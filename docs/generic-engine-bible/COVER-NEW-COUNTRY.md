# COVER(country_code) — Biblia operativa de onboarding de país
> Cómo el motor genérico cubre un país nuevo. Orquesta: Claude (capa-3). Estado: capítulo 1 (KNOW_COUNTRY) escrito; el resto se completa con Olas 1/1.5/2.
> Máquina de estados: `REGISTERED → KNOW_COUNTRY → BOOTSTRAPPED → IN_COVERAGE → SEALED`.

## Principio rector
**Genérico ≠ uniforme.** El motor (maquinaria) no cambia; el **pack del país es PROFUNDO y 100% a medida**. Y nada se ejecuta hasta **conocer el país**. La inteligencia de mercado **DERIVA** el pack de las 9 etapas — no al revés.

---

## FASE 1 · `KNOW_COUNTRY` — Inteligencia de país/mercado (la que manda el owner: "conocer el país ANTES de proceder")

**Misión:** producir el **Dossier de País** — el documento verificado del que se deriva el pack 100%-personalizado de cada etapa. Sin dossier sellado, no se pasa a BOOTSTRAPPED.
**Quién:** Claude orquesta un workflow de deep-research multi-fuente; la IA local resume; Claude decide y firma. VAM = cada hecho del dossier por **≥2 vías ortogonales**.
**Entrada:** `country_code` (ISO). **Salida:** `Dossier de País` (estructurado + humano) + el `country_pack` derivado.

### El Dossier de País — qué hay que conocer (organizado por la etapa que lo consume)

**A. Identidad, idioma y legal** → packs de extracción, identidad, legal/compliance
- Idioma(s) oficial(es) y de los anuncios; moneda; huso; formato numérico (decimal/miles).
- Marco legal: ley de protección de datos (RGPD-equivalente), autoridad competente; legalidad de scraping (robots/ToS/anti-circumvention en esa jurisdicción); estatus legal de PII de vendedores particulares (¿el teléfono/matrícula es dato personal protegido?).
- Identificador fiscal de empresa (CIF→VAT/USt-IdNr/SIREN…); su formato y disponibilidad pública.

**B. Geografía administrativa** → pack de geo (el más grande)
- Árbol administrativo real y su profundidad (DE: Land→Kreis→Gemeinde; FR: région→département→commune; etc.). Fuente canónica del árbol: oficial nacional > GeoNames ADM1–5 > OSM `admin_level`.
- Centroides por unidad; formato de código postal y su mapeo a unidad; tabla de alias/variantes ortográficas.
- A qué **nivel** se sella por defecto en ese país (equivalente al "provincia" de ES).

**C. Estructura del mercado de venta de coches** → packs de descubrimiento, scraping, denominador
- Canales y su peso: concesionario oficial, compraventa independiente, OEM-VO (portales de marca de ocasión), garajes/talleres que venden, desguace (fuera del sello de venta), subasta.
- Particularidades culturales del canal (p.ej. dominio de un marketplace, ventas C2C vs profesional, importación paralela).
- Tamaño estimado del universo profesional (para sanity-check del denominador).

**D. Plataformas y portales** → pack de scraping (roster) + Tier-1
- Los marketplaces/portales que **dominan** ese mercado (DE: mobile.de, autoscout24.de; FR: lacentrale.fr, leboncoin.fr; IT: subito.it, automobile.it; PT: standvirtual.com, olx.pt; NL: marktplaats/autoscout24.nl; …) — verificado, no asumido.
- Para cada uno: defensa anti-bot probable (Cloudflare/DataDome/Akamai/ninguna), si expone API/sitemap, estructura de ficha, y su clasificación Tier-0/Tier-1.
- Portales OEM-VO de las marcas presentes; directorios/asociaciones locales.

**E. Fuentes de denominador (lo que hace falsable el 100%)** → pack de calidad/sello
- Registro mercantil equivalente a BORME (DE: Handelsregister/Unternehmensregister; FR: RNE/Infogreffe; IT: Registro Imprese; …) y su accesibilidad €0.
- Asociaciones del sector (equivalentes a FACONAUTO/GANVAM/ANCERA) y sus padrones.
- Registro de matriculación / autoridad de tráfico (equivalente DGT) si publica censo de puntos de venta o concesionarios.
- Mapas (Overture/OSM/Google POI) como lista ortogonal geográfica; clasificación CNAE-equivalente del sector.
- ≥3 listas **ortogonales** entre sí para que el MSE (captura-recaptura) tenga solape medible.

**F. Locale de datos** → packs de identidad y extracción
- Formato de teléfono (prefijo país E.164, longitud, líderes válidos) → autoridad de teléfono del país.
- Formato de dirección; convenciones de nombres comerciales (sufijos GmbH/SARL/SRL…).
- Taxonomía local de marca/modelo/acabado e idioma para la normalización (capa LLM).

**G. Egress / infraestructura** → pack de scraping (operación)
- Reputación de IP del servidor frente a los anti-bot dominantes de ese mercado; ¿hace falta presencia/latencia local?; ¿proxies de contingencia para la minoría dura?
- Volumen estimado y cadencia de delta sostenible al ritmo seguro desde la(s) IP(s) disponibles.

### Gate de salida de `KNOW_COUNTRY`
SELLADO ⇔ el Dossier está **completo** (las 7 secciones A–G), cada hecho cargado **verificado por ≥2 vías**, y **3 listas ortogonales de denominador** identificadas. Hueco con causa declarada permitido; hueco silencioso, no. → pasa a `BOOTSTRAPPED`.

### Rol de Claude (capa-3) en esta fase
Orquesta el deep-research por país; resuelve las ambigüedades (qué portal es Tier-1, qué fuente de denominador es fiable, cómo mapea el árbol admin); firma el Dossier. La IA local solo resume/clasifica candidatos; **decide Claude**.

---

## FASE 2 · `BOOTSTRAPPED` — Derivar el pack 100%-personalizado
Del Dossier se generan, por cada etapa, los artefactos del pack: registro de adaptadores de descubrimiento, roster de plataformas + recetas semilla, adaptador geo (árbol+centroides+alias), autoridad de teléfono/dirección, ancla(s) de denominador + listas ortogonales, config de enrutado LLM (modelos+gramáticas por idioma), y el REGISTRY de fuentes del scheduler. *(Detalle por etapa: `stages/01..10` — Ola 1.)*

## FASE 3 · `IN_COVERAGE` — Ejecutar y paralelizar
El motor corre las 9 etapas sobre el pack; Claude drena el bus de decisiones (recetas Tier-1, discrepancias VAM); se sella unidad geo golden → se paraleliza el resto.

## FASE 4 · `SEALED` — Certificar
Todas las unidades selladas + reconciliación nacional. "Sellado" = **intervalo de cobertura certificado** (cota inferior con su margen), no un entero. *(Detalle: `stages/07-quality-seal` + `NEXT-LEVEL`.)*

---

> **Pendiente de completar con las Olas:** las Fases 2–4 se rellenan con los diseños por etapa (Ola 1), la matriz de enrutado LLM (Ola 1.5) y la síntesis (Ola 2). Este capítulo `KNOW_COUNTRY` es la piedra angular: ningún país procede sin él.
