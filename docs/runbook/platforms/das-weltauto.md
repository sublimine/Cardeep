# das_weltauto — das-weltauto
**Estado:** ✅ VALIDADO (verdict id=428, count=552, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-XWX9RHG7` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t1_soft` · is_tier1: `FALSE` · family: `vw_group` · data_surface: `next_data`

## Data-layer (la fuente real)
- Endpoint: `GET https://www.dasweltauto.es/esp/coches-de-segunda-mano-en-{provincia}?pagina=N` (sitio AEM SSR vw-dwa3 sobre feed Motorflash; la ruta nacional bare IGNORA `?pagina`). Origin 403 a fetch naïve; sirve a chrome131. Portal genérico multi-marca VW (VW, SEAT, Škoda, CUPRA, Audi certificados por su red).
- Tope/partición: enumerar POR PROVINCIA (`{provincia}` slug), `?pagina=N`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Enumerar por provincia, `?pagina=N`.
2. Por card: `data-configuration='{…}'` = coche (VehicleManufacturer, Model, Vehicle.VehicleId, Milage, RegistrationDate, FuelType, Price, Color) y `data-partner='{…}'` = dealer (InformationBnr, Name, City, ZIP).
3. **Señal de parada:** la última página CLAMP-REPITE → parar cuando una página añade CERO VehicleIds nuevos (no cuando está vacía).
4. Provincia = ZIP[:2].

## Receta / config
- Conector: `pipeline/platform/dasweltauto_wholesale.py`
- Governor: **STEALTH** (override per-host 1.0/3/0.8 en governor.py) · `defense_tier=t1_soft`
- Parser/identidad: `Vehicle.VehicleId` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=428 TRUSTWORTHY** · count=**552** coches / 56 dealers (slice capado; el portal anuncia >8.000 nacionales) · div 0.0.

## CLI (reproducible)
```bash
python -m pipeline.platform.dasweltauto_wholesale --provinces 3 --pages 8
```

## Trampas / notas
- La ruta nacional bare ignora `?pagina` → enumerar por provincia.
- Última página clamp-repite: parar al añadir 0 VehicleIds nuevos. La mitad Audi tiene además su portal propio; SEAT VO == este.
