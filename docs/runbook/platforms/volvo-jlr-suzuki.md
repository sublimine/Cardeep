# volvo_jlr_suzuki — volvo-jlr-suzuki
**Estado:** ✅ VALIDADO (verdict id=571, count=1.801, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-T0G18J3M` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t1_soft` · is_tier1: `TRUE` · family: `volvo_jlr_suzuki_vo`

## Data-layer (la fuente real)
Frente multi-marca: Volvo Selekt + Jaguar/Land Rover Approved. DOS backends, UN conector. (Suzuki diferido — ver [NOT-VALIDATED.md](../NOT-VALIDATED.md).)
- **Volvo Selekt (Codeweavers):** `POST https://services.codeweavers.net/api/guest/initialise/proposal` (headers `x-cw-digitalretailstorereference`, `x-cw-applicationname: Storefront`, `x-cw-anti-cache`; body `{"ApiKey":"n1WG1lPrjpggL45z6p","OrganisationIdentifier":{"Type":"CodeweaversReference","Value":"55388"}}`) → `{"UserToken":"<guid>"}`. Luego `POST /api/vehicles/search/count` y `POST /api/vehicles/search-with-facets` (paginación FLAT `Page`+`ResultsPerPage`). ~1.311 coches.
- **JLR Approved (GForces NetDirector AVL, GraphQL):** `POST https://production-api.search-api.netdirector.auto/api/vehicle-search?uuid=…` (`getCount`+`getAll`), `Authorization` token cliente estático, marca por `companyHash`+`manufacturer`. Land Rover ~399 + Jaguar ~35.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Volvo: mint `UserToken` invitado → count → search-with-facets paginado.
2. JLR: `getCount` + `getAll` por `companyHash`/`manufacturer`.
3. GEO: Volvo `Retailer.Address.Postcode`; AVL `location.details.address.postcode`. Provincia = `postcode[:2]`.
4. Dedup por `Physical.ExternalVehicleId` (MDX-xxxx) o VIN — NUNCA por `Reference` (token rotatorio).

## Receta / config
- Conector: `pipeline/platform/oem_volvo_jlr_suzuki_wholesale.py` (cubre SOLO Volvo + JLR)
- Governor: **STEALTH** (ambos hosts) · `defense_tier=t1_soft` · `is_tier1=TRUE`
- Parser/identidad: `ExternalVehicleId`/VIN · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=571 TRUSTWORTHY** · count=**1.801** coches / 98 dealers (Volvo + JLR; Suzuki no incluido) · div 0.0339.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_volvo_jlr_suzuki_wholesale --pages 20
```

## Trampas / notas
- El nombre compuesto del fichero refleja el frente investigado, no la cobertura: Suzuki queda fuera (directorio per-dealer diferido a long-tail).
- Re-encode latin-1.
