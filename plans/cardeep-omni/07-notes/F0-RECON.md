# F0 — Recon SQL real (07-marketing), 2026-07-18

> Ejecutado en vivo contra `cardeep-pg` (healthy, 13h+ de uptime en el momento de la
> medición). Script re-ejecutable: `scripts/f0_marketing_recon.py`. Cierra el hueco
> declarado en `07-marketing.md` §5.2 ("el volumen real de filas en `platform_listing`
> con `platform_price` no-nulo y la densidad de `vin_ref`/`photo_url` en `vehicle` NO
> se verificaron por SQL en esta síntesis").

## Resultado literal

```
vehicle total: 2670828
vehicle available: 2124671
vin_ref present (available): 30752 (1.45%)
photo_url present (available): 1963278 (92.40%)
photo_hash present (available): 14 (0.00%)
fuel+transmission present (available): 1119963 (52.71%)
title-rich make+model+year (available): 1717715 (80.85%)
price>0 present (available): 2096724 (98.68%)
km present (available): 2005124 (94.37%)
platform_listing total rows: 2430136
platform_listing listed: 1938891
platform_listing listed w/ platform_price: 1923884 (99.23%)
platform_listing listed w/ price DIVERGENT vs vehicle.price: 10664
vehicles w/ >=2 downward PRICE_CHANGE in 30d, still available (c11 signal): 26436
vehicle_event GONE total: 567858
GONE vehicles with >=1 platform_listing edge (any status): 505487
dealers with >=1 available vehicle listed on >=1 platform: 378121
```

## Lectura para C1 (auditoría de anuncio)

| Check | Densidad real | Lectura |
|---|---|---|
| c1 `price>0` | 98.68% | señal fuerte, casi universal |
| c2 `make`/`model` | ≥80.85% (proxy title-rich) | fuerte |
| c3 `year` | incluido en el 80.85% anterior | fuerte |
| c4 `km` | 94.37% | fuerte |
| c5 `vin_ref` | **1.45%** | **débil** — coherente con el hallazgo de 04-F6 (contaminación masiva de `vin_ref` con listing-IDs de AS24, remediada solo parcialmente: ~15 conectores más siguen sin corregir según `PROGRESO.md` BLOQUE 2). La mayoría de anuncios recibirá 0/12 en c5 hoy — HONESTO, no maquillado; mejora automáticamente según 04-F6 avance. |
| c6 `fuel`/`transmission` | 52.71% | media — la mitad de la flota disponible falla este check hoy |
| c7 foto presente | 92.40% | fuerte |
| c8 foto ≥800×600 | no medido aquí (exige descarga real de imagen, job de F1) | pendiente — se mide en el motor de F1, no en este recon estático |
| c9 título rico | 80.85% (proxy) | fuerte |
| c10 coherencia de precio cross-plataforma | 10.664 divergencias reales sobre 1.923.884 aristas con precio (0.55%) | señal real, minoritaria — la mayoría de anuncios YA son coherentes |
| c11 sin estancamiento | 26.436 vehículos con ≥2 bajadas de precio en 30d aún disponibles | señal real y no trivial — sustrato suficiente para el check |

`photo_hash` (0.00%, 14/2.124.671) confirma — por tercera vía independiente tras 02-F0
y 04-F6 — que la señal de identidad por imagen sigue inexistente; no se usa en C1 (que
solo exige `photo_url`, no `photo_hash`).

## Lectura para C3/C4/C5 (radar de canales)

- 1.938.891 aristas `platform_listing` en estado `listed`, 99.23% con `platform_price` —
  sustrato amplio para C3 (cobertura) y C4 (divergencia).
- 505.487 vehículos GONE (de 567.858 totales, 89%) tienen al menos una arista de
  plataforma — sustrato amplio para C5 (días-hasta-baja por plataforma).
- `dealers with >=1 edge`: 378.121 — esto es `COUNT(DISTINCT entity_ulid)` SIN
  canonicalizar (pre-`v_dealer_resolved`), no el conteo de dealers canónicos (~19.509
  citado en otras cartas). Declarado para que no se confunda con la cifra de producto;
  el endpoint real (F1/F4) siempre opera por `cdp_code` ya resuelto vía
  `resolve_cluster`, igual que el resto de la API.

## Decisión operativa derivada

Con esta densidad, el motor C1 (F1) es viable de producción HOY sobre el 100% del
censo servable — no hace falta esperar a que 04-F6 termine de remediar `vin_ref` ni a
que exista `photo_hash`: el score simplemente reflejará la realidad (mayoría de
anuncios perderá los 12 puntos de c5 hasta que la remediación avance). Nada se
maquilla; el score de hoy es el score real de hoy.
