# kia — kia
**Estado:** ✅ VALIDADO (verdict id=570, count=1.519, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-YK54F18S` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t1_soft` · is_tier1: `FALSE` · family: `kia_vo`

## Data-layer (la fuente real)
- Endpoint: `POST https://kiaokasion.net/kia/async/metodos.aspx` (servlet multiplexado por campo `accion`; backend "Kia Okasión" ASP.NET/IIS). Headers: `Content-Type: application/x-www-form-urlencoded`, `X-Requested-With: XMLHttpRequest`, `Origin/Referer: https://www.kia.com`. (IIS raíz 403 a curl pelado; sirve a chrome131.)
- `accion=actualizarCoches` → coches; `accion=actualizarTodoBuscador` → facetas.
- **Hecho estructural — PARTICIÓN POR CLUSTER:** el catálogo se particiona por `idconcesionario` (el `__kiaClienteId` inline = id de GRUPO/cluster, NO un solo dealer). `idconcesionario=0` → 0 coches; solo ~55 clusters vivos (ids 331..1810) traen stock. `km=nacional` solo relaja el radio DENTRO de un cluster, NO agrega.

## Micro-acciones (cómo se scrapea, paso a paso)
1. BARRER `idconcesionario` exhaustivamente 1..2000.
2. Por cluster vivo, `accion=actualizarCoches` paginado.
3. Stock nacional = UNIÓN sobre todos los clusters.
4. `concesionario` (nombre) + `poblacion` (ciudad) por coche → provincia vía `GeoResolver.resolve_city_global` (sin CP en lista). `dealerId` = compuesto (cluster + nombre + ciudad).

## Receta / config
- Conector: `pipeline/platform/oem_kia_wholesale.py`
- Governor: **JSON_API** (`kiaokasion.net` registrado — el barrido de ~2000 probes exige ritmo alto) · `defense_tier=t1_soft`
- Parser/identidad: `dealerId` compuesto · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=570 TRUSTWORTHY** · count=**1.519** coches / 63 dealers · div 0.0039.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_kia_wholesale
python -m pipeline.platform.oem_kia_wholesale --limit 500   # ~target de coches
```

## Trampas / notas
- El `idconcesionario` es un cluster/grupo, no un dealer: barrer exhaustivo 1..2000, unir. Re-encode latin-1.
