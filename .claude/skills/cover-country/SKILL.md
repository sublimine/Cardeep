---
name: cover-country
description: Use when covering or onboarding a NEW country in the Cardeep census (e.g. NL, DE, FR, IT, PT) — any request to start, focus on, or advance a country through its lifecycle, or a country with no country_campaign row. Triggers include "cubre/cover <país>", "nuevo país/tenant", "onboard <CC>", "enfócate en <país>".
---

# cover-country — onboarding E2E de un país en el censo Cardeep

## Overview
Cubrir un país = llevarlo por la máquina de estados `REGISTERED → KNOW_COUNTRY → BOOTSTRAPPED → IN_COVERAGE → SEALED`.
**Principio rector (la biblia): _genérico ≠ uniforme_** — el MOTOR no cambia; el **pack del país es PROFUNDO y 100% a medida**, DERIVADO de la inteligencia de mercado. **Nada se ejecuta hasta CONOCER el país.**
Verdad: `docs/generic-engine-bible/COVER-NEW-COUNTRY.md`. Loop: `pipeline/ops/autopilot.py::run_campaign` + `pipeline/autopilot/state.py`.

## Cómo enfocar el 100% en un país
Al recibir un `country_code` (ISO-2, p.ej. `NL`): trabajar SOLO ese tenant — todo query/seed/seal va `WHERE country_code = $CC`. El incumbente **ES nunca se toca** (byte-identical). El progreso se persiste en `country_campaign.detail` (consultable). El loop **nunca se detiene** en un gate: PARQUEA PENDIENTE-OWNER (`state.mark_pending_gates`) y sigue.

## Las 4 fases

### 1 · KNOW_COUNTRY — el Dossier de País (Claude orquesta; owner firma lo legal)
Deep-research multi-fuente; **cada hecho VAM por ≥2 vías ortogonales**. El dossier tiene 7 secciones:
- **A · Identidad/idioma/legal** → idioma(s), moneda, huso, formato numérico; ley de datos (RGPD-eq) + autoridad; legalidad de scraping (robots/ToS); ID fiscal de empresa (VAT/USt-IdNr/SIREN) + formato.
- **B · Geografía admin** (el pack mayor) → árbol real (DE: Land→Kreis→Gemeinde; FR: région→département→commune), centroides, código-postal→unidad, alias; **nivel de sello** (equiv. "provincia" de ES).
- **C · Estructura de mercado** → canales y peso (concesionario / compraventa / OEM-VO / garaje / desguace / subasta); universo profesional estimado (sanity del denominador).
- **D · Plataformas/portales → roster + Tier-1** → los que DOMINAN (NL: marktplaats, autoscout24.nl), su anti-bot (Cloudflare/DataDome/Akamai/ninguno), si exponen API/sitemap, clasificación Tier-0/Tier-1.
- **E · Denominador — ≥3 listas ORTOGONALES** → registro mercantil (KvK / Handelsregister / Infogreffe), asociaciones del sector, registro de tráfico (DGT-eq), mapas (OSM/Overture). Sin solape ⇒ el MSE no mide cobertura.
- **F · Locale** → teléfono (E.164 `+CC`, longitud), dirección, sufijos comerciales (B.V./GmbH/SARL), taxonomía marca/modelo (capa LLM).
- **G · Egress** → reputación IP vs anti-bot dominante; proxies de contingencia €0 (`pipeline/engine/free_proxies.py`); cadencia de delta sostenible.

**Gate de salida:** dossier completo (A–G) · cada hecho ≥2 vías · ≥3 listas ortogonales. Hueco con causa declarada OK; hueco silencioso NO.

### 2 · BOOTSTRAPPED — derivar el pack 100% a medida
Generar `countries/<CC>/`: adaptador geo (árbol+centroides+alias), roster + recetas semilla, autoridad teléfono/dirección, anclas de denominador + listas ortogonales, routing LLM (modelo+gramática por idioma — `pipeline/recipe_extract_llm.py`, env `CARDEEP_LLM_MODEL`), y el REGISTRY de fuentes del scheduler.

### 3 · IN_COVERAGE — cosechar y paralelizar
El scheduler (`pipeline/ops/scheduler.py`, `heartbeat_tick`) cosecha las fuentes due. El **`recipe_cracker`** ataca Tier-1 con su escalera de rungs *cheap→expensive*: si una vía lo revuelca → prueba otra → afina → reintenta; warm-start del rung ganador; **sin fallo silencioso** (cada rung registra su razón). Drenar el bus: recetas Tier-1 difíciles + discrepancias VAM. Flujo: cage → VAM (quórum ≥2) → delta → API. Sellar 1 unidad geo golden → paralelizar el resto.

### 4 · SEALED — certificar
Todas las unidades + reconciliación nacional. "Sellado" = **intervalo de cobertura certificado** (cota inferior + margen), no un entero. Invariante mecánico: `v_country_proof_violations` DEBE ser 0 (country-proof, migs 0071 entity + 0072 vehicle) y `vam_verified` solo con quórum (trigger 0070).

## Quick reference
| Acción | Comando / código |
|--------|------------------|
| Registrar país | `state.register(conn, '<CC>')` → REGISTERED |
| Correr el loop (dry-run synthetic) | `run_campaign('<CC>', conn=…, pack_fixtures=…, dry_run=True)` |
| Ver gates parqueados | `state.pending_owner_gates(conn)` → `{CC:[gate]}` |
| Salud por país | `supervisor.health_rollup(conn, '<CC>')` |
| Cosecha acotada (verificar) | `python -m pipeline.platform.<source> --limit N` |
| Refrescar /stats | `python -m scripts.refresh_product_stats` (cadence job del scheduler) |
| Arrancar el sistema | `docker compose up -d` (pg → api + autopilot) |
| Runbook / gates owner | `plans/autonomy-e2e/06-RUNBOOK.md` · `05-OWNER-GATES.md` |

## Gates OWNER (parquean, NO detienen — la frontera honesta)
**LEGAL/ToS** del país (firmar el dossier legal) · **go-live N2** (SIEMPRE escala a owner) · **GASTO €>0** (`gates.BUDGET_ENV` = `CARDEEP_BUDGET_AUTHORIZED`; el €0/free-proxies va solo).

## Common mistakes
- Ejecutar cosecha antes de cerrar KNOW_COUNTRY (prohibido: nada sin conocer el país).
- Pack uniforme/copiado de ES — debe ser DERIVADO del dossier, a medida del país.
- <3 listas ortogonales de denominador ⇒ el MSE no puede medir solape ⇒ no se puede sellar.
- Tocar el incumbente ES — todo `WHERE country_code=$CC`; ES byte-identical.
- Declarar SEALED sin `v_country_proof_violations=0` o sin quórum VAM ≥2 (es maquillaje).
- Aplicar migraciones a prod tras un merge sin re-correr `migrate.py up` (deja gaps — lección 2026-06-29).
