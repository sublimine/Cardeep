# CARDEEP — Arquitectura de orquestación (estándar institucional)

> Cómo Cardeep cierra España al 100% sin trabajo artesanal: ejércitos de agentes y
> workflows en paralelo sobre un pipeline determinista, con la Inquisición (verificación
> adversarial) como cadena separada. El humano decide; los agentes ejecutan; el motor late.

## Doctrina de coste (mandato)
- **Lo masivo y barato → determinista o LLM local** (clasificar, parsear, deduplicar,
  geo-resolver, ingerir): código Python `pipeline/` + Ollama. €0, escala lineal.
- **La inteligencia cara → solo para decidir y cazar** (recetas Tier-1, desambiguar,
  verificación adversarial): flotas de agentes vía la herramienta `Workflow`.

## Dos planos, una verdad (main)
```
PLANO DETERMINISTA (pipeline/)            PLANO DE INTELIGENCIA (Workflow + agentes)
  - source adapters (1/fuente)              - flota que CONSTRUYE adaptadores en paralelo
  - discover / scrape / recipe                - flota que CAZA recetas Tier-1 (anti-bot)
  - ingest (delta) / verify (VAM)             - Inquisición: verificación adversarial
  - corre en bucle, barato                    - corre a ráfagas, cara, decide
        \                                         /
         ──────────►  PostgreSQL (cardeep-pg) + API viva  ◄──────────
```

## Sistemas permanentes (S-*)
| Sistema | Qué hace | Estado |
|---|---|---|
| **S-GEO** | backbone INE 52 prov / 8.132 munis + resolución nombre→código | ✅ |
| **S-CODE** | `cdp_code` inmutable determinista (dedup cross-fuente) | ✅ |
| **S-DISCOVER** | adaptadores de fuente → entidades + provenance + VAM | ✅ (DGT, Kia, +flota) |
| **S-INVENTORY** | scrapear→receta→ingest con motor de **delta** (NEW/GONE/Δprecio/Δfoto/Δkm) | ✅ (AS24) |
| **S-VAM** | quórum ≥2 vías; nada TRUSTWORTHY sin acuerdo | ✅ |
| **S-API** | sirve entidad/inventario/delta/geo (envelope consistente) | ✅ |
| **S-HEALTH** | watchdog por fuente + alerta origen-exacto + auto-repair | F7 (tabla lista) |
| **S-TIER1** | plataformas duras, **árbol y operación separados** del long-tail | F5 (en caza) |

## Workflows (WF-*) — orquestación en paralelo
- **WF-DISCOVERY-FLEET:** N agentes, cada uno construye+verifica EN VIVO un adaptador de
  fuente (OEM JSON, asociaciones, directorios). Salida: ficheros `pipeline/sources/*.py`
  verificados. El main-loop integra y corre la ingesta (idempotente, VAM cada una).
- **WF-TIER1-HUNT:** un agente por gigante (wallapop/coches.net/milanuncios/coches.com…)
  cazando la receta de cosecha con el arsenal libre; reporta método reproducible o el
  muro exacto que exige gasto. Tier-1 NUNCA se mezcla con el long-tail.
- **WF-INVENTORY-SCALE:** fan-out de cosecha de inventario por dealer (cada dealer = su
  stock completo + delta), sobre las plataformas abiertas (AS24) y las recetas Tier-1.
- **WF-INQUISITION (Audit):** cadena verificadora SEPARADA — re-deriva cada conteo por una
  vía independiente a la que lo produjo. Un agente que afirma; otro que refuta.

## Contrato anti-colisión (paralelismo seguro)
1. Los agentes de construcción escriben **un fichero distinto cada uno** (`sources/<key>.py`);
   nunca editan `discover.py` ni la DB → cero carreras.
2. La **ingesta a la DB la centraliza el main-loop** (o un único worker), idempotente por
   `cdp_code` → re-correr no duplica.
3. **Provenance multi-fuente** (`entity_source`): la misma entidad por N fuentes = 1 código,
   N atestiguaciones → dedup + capture-recapture del universo real.
4. Verificar SIEMPRE por vía ortogonal antes de consolidar (la salida de un agente es sospechosa).

## Orden de batalla por ROI (€0 primero)
1. **Desguaces** (DGT 1.292) ✅ + AEDRA cross-check.
2. **Concesionarios oficiales** (~all vía APIs OEM JSON: Kia✅, MG, BYD, Skoda, Toyota…).
3. **Inventario abierto** (AS24 278k atribuido por dealer) — fan-out en marcha.
4. **Long-tail** (OSM 12k geo + FSQ/Overture + registros CCAA talleres).
5. **Tier-1 gigantes** (wallapop/milanuncios/coches.net/spoticar) — recetas en caza; las
   que exijan IP residencial esperan el gate de gasto del owner.
6. **Resiliencia** (S-HEALTH: alertas + auto-repair).
