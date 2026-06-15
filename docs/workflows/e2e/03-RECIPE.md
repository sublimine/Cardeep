# 03-RECIPE — Creación y validación de recipe per-dealer

Crea o actualiza el `recipe.yaml` de un dealer concreto, clasificándolo en la familia de
conector correcta y verificando que cumple el gate G3 de `complete.py`.

---

## Disparador

- **Post-discover**: nuevo `cdp_code` sin recipe (`v_dealer_recipe.recipe_kind = 'none'`).
- **Manual**: `python -m pipeline.recipe --cdp CDP-ES-XX-XXXXXXXX`
- **Agente LLM recipe-hunter**: disparado manualmente por el Director para dealers Tier-1
  sin recipe conocida (path HARVEST-GATED).

---

## Entradas

| Entrada | Descripción |
|---|---|
| `cdp_code` | Identificador canónico del dealer |
| `entity` row | URL del dealer, `platform_slug` |
| `pipeline/platform/` | Catálogo de 44 conectores disponibles |
| Árbol geo | `countries/ES/{prov}/{comarca}/{muni}/dealers/{cdp}/` |
| Recipe de familia | `recipe.yaml` de dealers similares como referencia |

---

## Pasos átomo

1. **Clasificar familia**: determinar a qué conector pertenece el dealer —
   ¿autoscout24? ¿wordpress_cms? ¿OEM official? → mapeo a `pipeline/platform/{connector}.py`.
   Familias disponibles: Tier-1 marketplaces, OEM VO, grupos (importador, rentacar_vo,
   subastas, vo_chains), especializados, longtail (builder_wix_ueni, cms_wordpress, dealerk,
   dms_vendor, framework_next_astro_nuxt, generic_custom, unreachable).

2. **Path €0 — familia conocida**:
   - Copiar template de `recipe.yaml` de la familia correspondiente.
   - Ajustar `field_map`, `enumeration`, `access` al dealer concreto.
   - Ejecutar `pipeline/recipe.py` → valida sintaxis YAML y presencia de campos obligatorios:
     `version`, `source`, `engine`, `access`, `enumeration`, `field_map` (con `deep_link`).

3. **Path agente — Tier-1 sin familia conocida** (HARVEST-GATED):
   - LLM recipe-hunter inspecciona el site del dealer.
   - Identifica mecanismo de paginación, estructura `field_map`, tipo de `engine`.
   - Genera `recipe.yaml` candidato.
   - Revisión humana obligatoria antes de commit.

4. **Commit recipe**: escribir `countries/ES/recipes/{cdp_code}.yaml`
   (ruta real según `pipeline/recipe.py::write_recipe()`; el árbol geo completo
   `countries/ES/{prov}/{comarca}/{muni}/dealers/{cdp}/recipe.yaml` es la convención
   de organización geo pero `write_recipe()` usa la ruta plana `recipes/`).

5. **Actualizar DB**: no existe tabla `dealer_recipe`. La vista `v_dealer_recipe`
   se deriva de `entity` (columna `recipe_version`) + `entity_source` + `vehicle`.
   Para activar el gate G3, ingest.py escribe `recipe_version` en la fila de `entity`
   via `ON CONFLICT (cdp_code) DO UPDATE SET recipe_version = ...`.

6. **Verificar gate G3**: `v_dealer_recipe.recipe_kind <> 'none'` →
   `compute_completion(conn, cdp_code)` en `pipeline/complete.py` pasa G3.

---

## Gate de verificación

| Condición | Descripción |
|---|---|
| G3 `complete.py` | `v_dealer_recipe.recipe_kind <> 'none'` |
| Sintaxis YAML | `pipeline/recipe.py` valida estructura completa |
| Campos obligatorios | `source`, `engine`, `enumeration`, `field_map.deep_link` presentes |
| `deep_link` | URL absoluta (no path relativo) |

---

## Artefactos

- `countries/ES/recipes/{cdp_code}.yaml` — fichero en ruta plana (según `pipeline/recipe.py::write_recipe()`)
- `entity.recipe_version` actualizado (no existe tabla `dealer_recipe`; la vista `v_dealer_recipe` refleja el estado via `entity.recipe_version`)

---

## Fallo → routing

| Fallo | Acción |
|---|---|
| Familia desconocida (sistema propietario) | `gestion_item` lane RESEARCH + flag para agente recipe-hunter |
| Recipe sintácticamente inválida | error en `pipeline.recipe`, alert phase='recipe', sin gasto externo |
| `deep_link` con path relativo | error de validación, recipe rechazada, no commitear |

---

## Idempotencia

- Sobreescribir `recipe.yaml` en filesystem es seguro — idempotente por `cdp_code`.
- `entity.recipe_version`: se actualiza via `ON CONFLICT (cdp_code) DO UPDATE SET recipe_version = ...` en ingest.py — re-ejecución safe (no existe tabla `dealer_recipe`).

---

## Estado

**IMPLEMENTADO** — `pipeline/recipe.py`, árbol `countries/ES/`, vista `v_dealer_recipe`.
Cobertura actual: 98.4% de dealers con `recipe_kind <> 'none'` (migration 0029).
El path agente LLM recipe-hunter está diseñado pero es **HARVEST-GATED** (gasto LLM).

---

## €0 vs gasto

| Componente | Coste |
|---|---|
| Clasificación por familia | €0 |
| Copia de template + ajuste manual | €0 |
| Validación YAML + update DB | €0 |
| Agente LLM recipe-hunter (Tier-1 sin familia) | GASTO |
