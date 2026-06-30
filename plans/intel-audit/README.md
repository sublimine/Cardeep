# Auditoría de Inteligencia de Automoción — índice

> Encargo (owner, 2026-06-30): cardeep vende inteligencia. Auditar al átomo a TODAS las empresas de datos
> del sector, extraer todo lo que ofrecen, los gaps, qué puede vender cardeep, y dónde colocar cada dato
> copiando sus patrones web. Nivel institucional. Cada dato verificado multi-fuente.

## Cómo leer esto
| Fichero | Qué es |
|---|---|
| **`CARDEEP-OFFERING.md`** | **Empieza aquí.** Qué vende cardeep, priorizado (baseline → diferenciadores del censo vivo → premium/arbitrage). |
| **`MATRIX.md`** | Catálogo de campos canonicalizado (99 métricas) × cobertura: table-stakes vs diferenciadores vs catálogo completo. |
| **`PLACEMENT-MAP.md`** | 1.353 patrones de DÓNDE coloca el sector cada dato → dónde va en cardeep. |
| **`ARBITRAGE.md`** | Señales de arbitrage (buy-side, cross-platform, time, geo, spread) + producto. |
| **`UNIVERSE.json`** (693) · `UNIVERSE_tiered.json` | El universo completo mapeado del sector. |
| **`AUDITS.json`** + **`companies/*.md`** (109) | La auditoría atómica por empresa (productos, campos, entrega, precio, placement, gaps, fuentes). |
| `_wf_audit*.js`, `_synthesize.py`, `_canon.py` | Pipeline reproducible (descubrir → auditar → sintetizar → canonicalizar). |

## Números
- **693** empresas descubiertas · **109 auditadas al átomo** (multi-fuente, antialucinación).
- **99 métricas canónicas** · **44 table-stakes** · **1.353** patrones de colocación · **1.127 gaps** · **958 diferenciales**.

## Los 4 hallazgos que importan
1. **El edge:** las 109 trabajan con MUESTRA + MODELO; cardeep tiene **censo VIVO 100% + delta + dedup
   cross-platform + verificación VAM**. Vende *observado y verificado*, no *estimado*.
2. **Table-stakes** (lo obligatorio): identidad/spec, valoración (retail/trade/residual/depreciación),
   historial (siniestros/km/propietarios/financiera), mercado (oferta/precio-vivo/ventas).
3. **Diferenciadores que SOLO cardeep puede poseer:** precio de mercado real (no modelado), price-position vs
   mercado completo, days-to-sell real, **delta en vivo (SEEN/GONE/Δprecio — nadie a censo completo)**,
   cross-platform gap, micro-geo (prov→comarca→muni), provenance auditable.
4. **Arbitrage:** deal-score + sourcing sobre la pata retail completa que el wholesale-only no ve.

## Estado
- F1 Universo ✅ · F2 Auditoría 109/109 ✅ · F3 Síntesis+canonicalización ✅ · F4 Arbitrage ✅ — todo en `main` (CI verde).
- Forks abiertos (decisión del owner): (a) deep-audit de los **584 restantes** del universo; (b) **BUILD** —
  integrar la inteligencia en las pantallas Inteligencia + Arbitrage del portal según `PLACEMENT-MAP.md`.
