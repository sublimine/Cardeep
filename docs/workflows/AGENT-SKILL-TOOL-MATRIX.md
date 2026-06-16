# Matriz Agente / Skill / Herramienta por Caso de Uso

Define qué corre como Python determinista €0, qué usa agente/LLM/gasto, y qué
skills/tools aplican a cada caso de uso del pipeline Cardeep.

---

## Doctrina

- **Pipeline masivo**: Python determinista €0. Sin LLM en el camino crítico.
  El LLM introduce latencia, coste y no-determinismo; ninguna de esas
  propiedades es aceptable en ingest, verification o scheduling.
- **Agentes solo para 2 casos**:
  1. Recipe-hunting Tier-1: identificar paginación y field_map de dealers cuya
     estructura no cae en ninguna familia conocida.
  2. Verificación adversarial con Lens C: live re-fetch HTTP cuando A/B/D/E no
     alcanzan quórum y C es determinante.
- **Verificación DB y estadística**: €0 siempre. Los constraints de PG son la
  única autoridad; no se delega en ningún agente para escribir verdicts.

---

## Tabla de casos de uso

| Caso de uso | Módulo / CLI | Modo | Agente / Skill | €0 / Gasto |
|-------------|-------------|------|---------------|------------|
| Descubrimiento de entidades | `pipeline/discover.py` | Python determinista | — | €0 |
| Scraping Tier-0 (open HTTP) | `pipeline/platform/*.py` + `fetch.py` + `governor.py` | Python determinista | — | €0 |
| Scraping Tier-1 (anti-bot) | `pipeline/platform/*.py` + camoufox | Python + proxies premium | — | GASTO (proxies) |
| Recipe-hunting Tier-1 nuevo dealer | `pipeline/recipe.py` | LLM agente | `cardex-pipeline` skill, Playwright browser | GASTO (LLM + proxies) |
| Recipe template (familia conocida) | `pipeline/recipe.py` | Python determinista | — | €0 |
| Ingesta + delta | `pipeline/ingest.py` + `pipeline/delta.py` | Python determinista | — | €0 |
| VAM count verdict (L1) | `pipeline/verify.py` | Python determinista | — | €0 |
| Deep Ledger δ cadencia (L2) | `pipeline/ops/inquisition_schedule.py` | Python determinista | — | €0 |
| Inquisition Lens A (requery) | `pipeline/inquisition/_lens_a.py` | Python determinista | — | €0 |
| Inquisition Lens B (raw recount) | `pipeline/inquisition/lenses.py` | Python determinista | — | €0 |
| Inquisition Lens C (live re-fetch) | `pipeline/inquisition/lenses.py` (stub) | LLM agente + HTTP | `cardex-pipeline` skill | HARVEST-GATED |
| Inquisition Lens D (cross-source) | `pipeline/inquisition/_lens_d.py` | Python determinista | — | €0 |
| Inquisition Lens E (batch hash) | `pipeline/inquisition/lenses.py` | Python determinista | — | €0 |
| Inquisition quórum + routing | `pipeline/inquisition/quorum.py` + `router.py` | Python determinista | — | €0 |
| Gestionador detección | `pipeline/gestionador/detect.py` | Python determinista | — | €0 |
| Gestionador routing + SLA | `pipeline/gestionador/route.py` | Python determinista | — | €0 |
| Heartbeat scheduling | `pipeline/ops/scheduler.py` | Python determinista | — | €0 (lógica) / GASTO (scraping Tier-1) |
| Silence watchdog | `pipeline/ops/silence_watchdog.py` | Python determinista | — | €0 |
| API serving | `services/api/main.py` | FastAPI determinista | — | €0 |
| Borrar dealer (EVICT) | `pipeline/evict.py` + `migrations/0033_evict.sql` (IMPLEMENTADO · `--apply` nunca corrido) | Python determinista | — | €0 |
| Completeness gates | `pipeline/complete.py` | Python determinista | — | €0 |
| Coverage verify | `pipeline/ops/coverage_verify.py` | Python determinista | — | €0 |

---

## Skills activadas por caso de uso

| Skill | Cuándo activar |
|-------|---------------|
| `cardex-pipeline` | Recipe-hunting Tier-1 nuevo dealer; Lens C live re-fetch cuando es determinante; debugging de conectores de plataforma |
| `systematic-debugging` | Cuando un detector del gestionador dispara una anomalía y la causa raíz no es obvia en los logs |
| `deep-research` | Análisis de cobertura de mercado; estudio de dealers no identificados; benchmarking de fuentes alternativas |
| `code-reviewer` | Tras cualquier modificación en `inquisition/`, `gestionador/` u `ops/` |
| `security-reviewer` | Antes de cualquier push con cambios a auth, API o manejo de datos externos |
| `database-reviewer` | Antes de cualquier nueva migración o cambio de schema en las tablas de verificación |

---

## Cuándo NO usar agentes

Las situaciones siguientes siempre son Python determinista. Usar un agente/LLM
aquí sería introducir coste, latencia y no-determinismo sin beneficio:

| Operación | Motivo de no usar agente |
|-----------|--------------------------|
| Ingest masivo de vehículos | Volumen y frecuencia requieren determinismo; un LLM no escala |
| VAM verdicts | DB-enforced; la lógica es un count modal, no razonamiento |
| Deep Ledger constraints | PG ejecuta el constraint; no hay interfaz para un agente |
| Scheduling (heartbeat, watchdog) | APScheduler es determinista; un agente introduciría deriva |
| Gestionador detect/route | Detectores son reads puros con umbrales fijos; routing es tabla de 13 reglas |
| API serving | FastAPI sirve endpoints deterministas; el LLM no añade valor aquí |
| Coverage verify | Cálculo estadístico puro sobre DB |

---

## Resumen de fronteras

```
€0 determinista (Python + PG)
├── Ingest, delta, discover
├── Verify (VAM L1, Deep Ledger L2)
├── Inquisition A / B / D / E
├── Gestionador detect + route
├── Ops: scheduler, watchdog, inquisition_schedule
└── API serving, completeness gates

HARVEST-GATED (requiere autorización explícita)
├── Inquisition Lens C (live re-fetch HTTP)
└── Scraping Tier-1 (anti-bot, proxies premium)

GASTO autorizado (LLM + proxies)
└── Recipe-hunting Tier-1 nuevo dealer
    (solo cuando ninguna familia conocida aplica)
```
