# Qué vende cardeep — la oferta de inteligencia (síntesis de 109 auditorías)

> Construido sobre la auditoría atómica de 109 empresas del sector (ver `companies/*.md`, `MATRIX.md`,
> `PLACEMENT-MAP.md`, y los pools de gaps/diferenciales en `AUDITS.json` / `_offering_data.md`). Datos base:
> 44 métricas table-stakes, 1.127 gaps declarados, 958 diferenciales, 1.353 patrones de colocación. Esto es
> la ESTRATEGIA; el detalle por campo y empresa vive en los ficheros de datos.

## 0. Tesis y edge estructural
Las 109 empresas comparten un límite: **trabajan con MUESTRA y MODELO**. Sacan precio/residual de un panel,
de transacciones parciales, de paneles de expertos o de scraping incompleto, y lo **modelan**. cardeep parte
de algo que ninguna tiene: el **censo VIVO del 100% de la huella digital** de un territorio, con
**delta+historial**, **dedup cross-platform** y **verificación multi-fuente (VAM, cero-confianza)**.

Traducción comercial: donde Autovista/JATO/Indicata dicen *"estimamos que este coche vale X"*, cardeep dice
*"este coche está AHORA a la venta a X en N plataformas, lleva D días, su precio bajó Y, y el mercado real de
su gemelo está en Z"* — **observado, no estimado, y verificado**. Eso es lo que se vende.

## 1. Capa 0 — Baseline (table-stakes: obligatorio para competir)
Las 44 métricas que ofrece la mayoría de los 109 (frecuencias en `MATRIX.md`). cardeep las debe servir todas;
ya tiene la materia prima del censo para casi todas:
- **Identidad + ficha:** Marca, Modelo, Versión/trim, Carrocería/segmento, Año, Motor/potencia, VIN,
  Combustible, Transmisión, Color, Dimensiones, CO2, Consumo, Autonomía/batería EV, Equipamiento opcional.
- **Valoración:** List price (nuevo), Retail/private value, Trade/wholesale value, Depreciación.
- **Historial:** Siniestros, Kilometraje, Nº de propietarios, Carga financiera/prenda.
- **Mercado:** Oferta/inventario (volumen), Precio de mercado en vivo, Ventas/matriculaciones, Geo.
Sin estas, cardeep no entra. Con estas, empata. **El billete está en la Capa 1.**

## 2. Capa 1 — Diferenciadores que cardeep PUEDE POSEER (del censo vivo)
1. **Precio de mercado REAL (observado, no modelado):** el precio del 100% de anuncios vivos; distribución
   completa (p25/mediana/p75), no un punto modelado.
2. **Price-position vs el mercado COMPLETO:** "−8% bajo su mercado real" contra TODO el inventario comparable
   vivo (robust-z / sweet-spot — ya prototipado en la pantalla Inteligencia).
3. **Days-to-sell / market-days-supply sobre inventario real:** rotación medida sobre el censo + delta
   (desaparición = venta), no estimada. Casi nadie a 100% de cobertura.
4. **DELTA EN VIVO (SEEN / GONE / Δprecio) — la joya:** altas, bajas (=ventas), bajadas de precio, cambios de
   km/ficha, en tiempo real. **Ningún competidor lo audita a censo completo.** Base de alertas y arbitrage.
5. **Dedup cross-platform:** mismo coche en N plataformas por VIN/foto/huella → gaps de precio + duplicados.
6. **Micro-geo (provincia → comarca → municipio, INE):** demanda/oferta/precio por zona fina, no por país.
7. **Provenance verificado (VAM):** cada dato con ≥2 fuentes ortogonales y trazabilidad → *"dato auditable"*
   frente a la opacidad de fuente del sector.

## 3. Capa 2 — Premium / arbitrage
Inteligencia accionable de compra-venta → `ARBITRAGE.md` (señales buy-side, cross-platform, wholesale-retail
spread, time-arbitrage), apoyada en los audits wholesale (Manheim/MMR, BCA, AUTO1, OPENLANE, ACV, CarOffer…).

## 4. Gaps del sector a explotar (de los 1.127 gaps declarados)
- **Tiempo real:** el sector publica semanal/mensual; cardeep es continuo.
- **Muestra, no censo:** modelos sobre panel vs observación 100%.
- **Cross-border like-for-like a escala:** solo Autovista lo presume; cardeep genérico por país.
- **Verificación/transparencia de fuente:** casi nadie expone provenance; cardeep sí (VAM).
- **Particulares + cross-platform:** el sector mira dealer/trade; cardeep ve TODO el online.

## 5. Mapa de colocación (resumen — detalle en `PLACEMENT-MAP.md`, 1.353 patrones)
- **Ficha de coche:** valoración (retail/trade/residual), **price-position + days-to-sell**, historial
  (siniestros/km/propietarios), specs, badges de confianza. (Patrón Autovista VIN-view, CARFAX HBV, AutoUncle, cap hpi.)
- **Panel / market-overview:** índices de precio, oferta/demanda, rankings de modelo, tendencias (Overview +
  Detailed — patrón Autovista Intelligence/Tableau, Indicata).
- **Comparador / market view:** like-for-like, competidor, cross-platform gap.
- **Alertas / monitoring:** delta (Δprecio, GONE=vendido, altas), reprecio sugerido (CARFAX VIN-monitoring + delta cardeep).
- **Informe / PDF:** dossier por vehículo o por mercado.

## 6. Prioridad de construcción (qué vender primero)
1. **Baseline servible** (Capa 0) sobre el censo → entra al mercado.
2. **Price-position + days-to-sell + delta en vivo** (Capa 1) → el diferencial que cobra.
3. **Alertas/monitoring + arbitrage** (Capa 2) → el premium recurrente (el billete).
4. **Provenance/verificación como sello** transversal → defendible y premium.

> Método: matriz canonicalizada por heurística de dominio (~55 métricas). Refinamiento pendiente (pase de
> canonicalización por agente sobre `AUDITS.json`) para colapsar el long-tail de ~6,7k variantes en el catálogo
> canónico final — no bloquea la estrategia, ya sólida.
