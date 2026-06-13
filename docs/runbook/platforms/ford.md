# ford — ford
**Estado:** ✅ VALIDADO (verdict id=488, count=543, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-ZB6C77HC` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t1_soft` · is_tier1: `TRUE` · family: `ford_vo`

## Data-layer (la fuente real)
- Endpoint: `POST https://www.servicescache.ford.com/api/eUsed/v1/searchVehicles` (SPA AngularJS GUXFOE sobre el servicio Ford eUsed/eUSL).
- Headers (Akamai + gate de consumidor, todo reproducible cliente-side): `Referer: https://secure.ford.es/`, `Origin`, `x-eusl-consumer: b-gux_approved_used-prod` (`b-{appName}-{env}`), `x-eusl-k: base64("{epoch_millis}:{nonce-16-bytes-hex}")` **fresco por request** (replay rechazado). NO bearer, NO cookie, NO login.
- Body: búsqueda GEO-RADIO `longLatCoordinates="{lng},{lat}"` + `distance` (km) + `pagination:{maxRecords:20000, startingRecord:0}`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Generar headers por request (`x-eusl-k` fresco).
2. UNA query nacional desde el centro de España con `distance>=2000` km cubre península + Canarias; `maxRecords=20000` devuelve los 543 en una respuesta (FLAT).
3. `data.VehicleInventoryList.VehicleInventoryItem[]`: coche (`Vehicle.*`) + dealer (`VendorInformation.*`: VendorCode, VendorName, Address+PostCode+coords).
4. Provincia = PostCode[:2].

## Receta / config
- Conector: `pipeline/platform/oem_ford_wholesale.py`
- Governor: **STEALTH** · `defense_tier=t1_soft` (Akamai + gate blando) · `is_tier1=TRUE` (akamai-grn)
- Parser/identidad: `VendorCode`/`Vehicle.*` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=488 TRUSTWORTHY** · count=**543** coches / 31 dealers · div 0.0; re-run idempotente añadió 0.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_ford_wholesale --pages 1
```

## Trampas / notas
- `x-eusl-k` es un nonce base64 fresco por request (replay rechazado), reproducible cliente-side sin login.
- Una query GEO-RADIO nacional (distance>=2000 km, maxRecords=20000) trae todo FLAT.
