# cardeep · Auditoría integral de empresas de inteligencia de automoción

> Goal owner (2026-06-30): cardeep VENDE inteligencia. Auditar al átomo a **todas** las empresas de
> información/inteligencia de automoción (Indicata, GANVAM, JATO… y muchísimas más), extraer TODO lo que
> ofrecen, encontrar los gaps entre ellas, y estructurarlo: dato crudo → limpio → **dónde colocarlo en
> cardeep copiando el patrón web de cada empresa**. Nivel institucional de élite. Nada básico. No parar.
> Cada dato VERIFICADO por ≥2 vías (doctrina VAM de cardeep aplicada a la propia investigación).

## Principios
- **Antialucinación:** cada campo extraído lleva fuente (URL) y, donde se pueda, ≥2 fuentes ortogonales.
  Si algo no se verifica, se marca `[NO-VERIFICADO]` — jamás se inventa.
- **Exhaustividad (sin techo):** el universo no son 3 empresas; son todas (valoración, specs/catálogo,
  VIN/historial, analítica de mercado, wholesale/subasta/arbitraje, telemática, asociaciones, portales,
  datos oficiales) en EU + global. Nicho, regionales y emergentes incluidas.
- **Orquestación:** recon y auditoría por Workflow (fan-out paralelo), síntesis encadenada.
- **Persistencia por fases:** `companies/<slug>.md` (audit atómico) · `UNIVERSE.json` (lista) ·
  `MATRIX.md` (matriz + gaps) · `CARDEEP-OFFERING.md` (qué vende cardeep + mapa de colocación).

## Schema de auditoría atómica por empresa
1. **Identidad:** nombre, marcas/AKA, grupo/owner, HQ, fundación, sitio(s).
2. **Categorías** + cliente objetivo (dealer / OEM / leasing / aseguradora / flota / gobierno / particular).
3. **Cobertura:** países/mercados · scope (nuevo/usado, turismo/VI/moto, segmentos).
4. **Productos de datos (núcleo):** por producto → nombre + qué es + **lista ATÓMICA de campos/métricas**
   (p.ej. valor residual %, retail/trade price, days-to-sell, market days supply, price-to-market %,
   índice demanda/oferta, curva depreciación, ajuste por km, specs/equipamiento, atributos VIN, histórico…).
5. **Metodología / fuentes de datos** (de dónde sacan el dato).
6. **Entrega:** API / dashboard / portal web / informe / feed / Excel / integración DMS.
7. **Modelo de precio** (si es descubrible): suscripción / por consulta / tiers.
8. **Patrón de COLOCACIÓN web (clave):** DÓNDE en su UI/web sitúan cada métrica (ficha de coche, panel de
   mercado, comparador, alertas…) + sección/layout. Esto es lo que cardeep imita para ubicar cada dato.
9. **Diferencial:** qué ofrece que otras no.
10. **Gaps:** qué NO ofrece.
11. **Fuentes** (URLs) por afirmación.

## Fases
- **F1 · Universo** (Workflow paralelo por categoría) → `UNIVERSE.json` (lista deduplicada, verificada).
- **F2 · Auditoría atómica** (Workflow, 1 agente/empresa) → `companies/<slug>.md` por empresa.
- **F3 · Síntesis** → `MATRIX.md` (matriz campo×empresa + gaps) + `CARDEEP-OFFERING.md` (qué puede vender
  cardeep, priorizado, con mapa de colocación derivado de los patrones reales).
- **F4 · Arbitrage** → mismo tratamiento para sistemas/empresas de arbitraje (wholesale, mispricing,
  cross-platform, buy-side chollos) → `ARBITRAGE.md`.

## Estado
- [x] **F1 Universo** — 693 empresas (`UNIVERSE.json`, tiered) → shortlist 109.
- [x] **F2 Auditoría atómica** — 109/109 (`companies/*.md`), multi-fuente, antialucinación (cap de sesión
      cortó 47 a mitad → reanudadas tras reset 6am Berlín; cerradas todas).
- [x] **F3 Síntesis** — `MATRIX.md` (26 métricas table-stakes canónicas + catálogo completo), `PLACEMENT-MAP.md`
      (1.353 patrones), `CARDEEP-OFFERING.md` (narrativa de oferta priorizada).
- [x] **F4 Arbitrage** — `ARBITRAGE.md` (señales buy-side/cross-platform/time/geo/spread + producto + placement).
- [ ] Pendiente (NO bloqueante): canonicalización fina por agente sobre `AUDITS.json`; deep-audit de tiers
      T2/T3 (584 restantes del universo) si se pide; BUILD/integración de la inteligencia en cardeep.
