# 01 — Country-Autopilot: arquitectura integrada + plan de construcción
> Síntesis de los 4 recons (geo+denom · fuentes+recetas · orquestador+puertas · auditor) +
> `docs/generic-engine-bible/COUNTRY-PACK-CONTRACT.md`. **El autopilot NO es from-scratch:**
> ensambla lo ya construido o diseñado. Cada fase: spec→TDD→verify→commit, dry-run €0, ES byte-idéntico.

## El loop (final)
```
RESEARCH(KNOW_COUNTRY) → PROPONER(countries/<CC>/ + country.toml + PLAN)
   → AUDITAR(5 niveles, automático) → [PUERTA] → EJECUTAR(dry-run/sintético; vivo=gate)
   → SUPERVISAR(per-país) → SELLAR(MSE/país)
```

## El AUDITOR de 5 niveles (sobre VAM/Inquisición — todo EXISTE, falta orquestar sobre pack+PLAN)
| Nivel | Audita | Reutiliza [VERIFICADO] | Tipo | Auto vs Escala |
|---|---|---|---|---|
| **N0 Estructura** | 8 piezas del pack presentes/bien formadas; cdp por `mint_code(cc)`; sin blockers ES | contrato §1.8; lint ci.yml; `v_country_proof_violations` | DETERMINISTA | auto (fail-closed) |
| **N1 Ortogonalidad** | fuentes + ≥3 listas denominador realmente independientes | `indep_distance D≥2` (models.py:111); `_path_family` ≥2fam/≥2orig (verify.py:117) | determinista + agente | auto si ≥3; ESCALA si clasificación incierta |
| **N2 Credibilidad** | denominador autoritativo, Tier-1, legalidad scraping | VAM ≥2 vías; Lens D; gate KNOW_COUNTRY | council adversarial + JUICIO | **SIEMPRE ESCALA** legal + autoridad-denominador |
| **N3 VAM-quórum** | números del PLAN pasan re-prosecución | motor Inquisición íntegro (`emit_claim→prosecute→decide`, quorum.py) | DETERMINISTA | auto (solo sobre-refuta, nunca fabrica TRUSTWORTHY) |
| **N4 Cobertura proyectada** | ¿pack alcanza censo sellable ≥0.95? | sello MSE (seal.py) modo proyección | determinista + agente | ESCALA si no-identifica/triangulación inconsistente |
Confianza = **MIN (weakest-link**, espejo de `indep_score=min` y `coverage_lower`). APRUEBA(build+dry-run) / RECHAZA(fail-closed) / ESCALA(PENDIENTE-OWNER). Persistir en `country_pack_audit_verdict` (espejo `inquisition_verdict`).

## Las PUERTAS (PENDIENTE-OWNER, aparcan no detienen) [VERIFICADO recon a8eb8cfdd]
- **GASTO €>0** — primitivo `requires_env`/`_gated` (discover_schedule.py:60,120) EXISTE; 0 rutas €>0 hoy (todo €0).
- **PROD** — `pipeline/config_guard.py` fail-closed `CARDEEP_ENV=prod` EXISTE+robusto (wired scheduler/discover_schedule/api).
- **LEGAL/ToS** — doctrina (KNOW_COUNTRY dossier verifica legalidad); sin primitivo código → a construir como gate de campaña.
- Frontera: TODO se construye+valida en dry-run `:5434`/sintético (país "XX" o DE sintético, patrón `pilot_country.py` + golden `country-proof-invariant`). Cruzan puerta SOLO: escritura viva `:5433`+prod, cualquier €>0, scrape de país real.

## LA FRONTERA HONESTA (el límite real de la autonomía — la respuesta a la visión del owner)
El auto-auditor **auto-aprueba solo construcción + dry-run**. SIEMPRE escala: legal/ToS, prod-cutover, gasto, **autoridad-de-denominador** (un denominador errado sesga TODO el censo en silencio), ortogonalidad-incierta, **conteos-vivos** (Lens C abstiene en €0 pre-puerta). Doctrina Law I: seguro delegar el **RECHAZO** (fail-closed nunca vende mentira), NO el "go" sobre país vivo. ⇒ el sistema **auto-desarrolla + auto-audita TODO hasta las puertas irreducibles**; "arrancar país real" es estructuralmente del owner. **No es excusa — es la doctrina cero-confianza aplicada al propio pack.**

## Decomposición (fases — dry-run €0, ES byte-idéntico)
- **A · DE-CEGADO restante** (precondición de motor, una vez): OI-2 (31 platform mints → `mint_code(cc)`), OI-7 (numerador único `v_servable_dealer`), OI-8 (pHash write-path, gated egress), OI-10 (`source_health`/`harvest_run`/`scheduler_lease` + `country_code`; **fix zombie silence O5** `resolve_recovered_silence_alerts`).
- **B · PACK ABSTRACTION** (fundación): `country.toml` + `CountryProfile` loader + **split registry motor↔pack** (`get_harvest_registry(country)`/`active_countries()`, byte-idéntico con `['ES']`) + máquina de estados `cover(CC)` + tabla `country_campaign`.
- **C · AUTO-PACK EXTRACTORES** (€0, puerta none): `GeoSource` (GeoNames CC-BY + cross-walk Eurostat-LAU) · denominador (Eurostat-SBS-G45 + GLEIF) · auto-source-finder (clasificar fuentes país→7 buckets) · peldaños receta `css`/`llm_local` (extruct + Ollama local).
- **D · AUTO-AUDITOR**: linter del contrato (N0) + N1-N4 reusando Inquisición/seal/guard + `country_pack_audit_verdict` + council N2 (agentes adversariales D≥2).
- **E · ORQUESTADOR + SUPERVISIÓN**: `pipeline/ops/autopilot.py` (el loop sobre la state machine) + supervisor salud per-país (lee 0057/0058/0060/0064) + gate registry de campaña (GASTO/PROD/LEGAL).

## Orden de construcción
**B** (fundación) → **A** (de-cegado, paralelizable) → **C + D** (extractores + auditor) → **E** (orquestador que une) → **validación E2E** onboard de país sintético "XX" en `:5434` por el loop completo, con el golden `country-proof-invariant` verde + byte-identidad ES.

## Base de rama
`feature/country-autopilot` desde main (tiene country-proof + gestionador fix). El spine de-cegado P0-P3 vive en `feature/country-2-readiness` (no mergeada) → se **mergea al llegar a la validación E2E** (Fase E), donde el harvest sintético necesita el threading; las Fases B-D (meta-capa + extractores + auditor) son ficheros nuevos, no lo necesitan. Resolver el conflicto detect.py (P3 vs gestionador-fix) en ese merge.
