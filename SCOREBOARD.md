# CARDEEP — MARCADOR VERIFICADO (checkpoint 2026-06-13)
> Cada número contado por el Director a mano contra la DB viva (cardeep-pg :5433), VAM ≥2 caminos.
> Estado MÓVIL: hay drenajes/workflows en vuelo; esto es la foto del checkpoint, no el cierre final.

## Tier-1 marketplaces (gigantes)
| Plataforma | Coches (verificado) | Estado |
|---|---|---|
| coches.net | 272.903 (155k dealers + 117k particular) | ✅ cerrado (falta new/km0/renting ~10k en backends Imperva aparte) |
| milanuncios | 259.034 (135k dealers + 124k particular) | ✅ cerrado (1 partición errada, barrido final) |
| coches.com | 111.498 (VO 95k + km0 15.6k + VN 826 + renting 13) | renting XHR 8.9k en cola |
| wallapop | drenando (cursor plano → 651k) | en vuelo |
| autocasion | drenando (VO 123k + VN/km0 segmentos) | en vuelo |
| motor.es | drenando (VO 51k + VN/renting) | en vuelo |

## Grupo OEM-VO (separado) — 14 portales, 22.222 coches, 1.171 dealers, VAM TRUSTWORTHY los 14
spoticar 5884 · audi 3798 · toyota_lexus 2024 · hyundai 1994 · volvo_jlr 1697 · nissan 1546 ·
cupra 1323 · kia 1036 · renew 918 · das_weltauto 552 · ford 543 · bmw 507 · mercedes 300 · mini 100.
(proof-slice → full en curso: MB 4804, toyota 3858, kia 1525, bmw/mini roster). Mazda/Honda/Suzuki = murados/sin data-layer (documentado).

## Otros grupos (Ola 2, WF-C en vuelo)
cadenas VO (Flexicar/Clicars/OcasionPlus) · rent-a-car VO (OK Mobility/Centauro/Sixt) · subastas (Autorola/BCA).

## Long-tail (WF-D en vuelo)
familias CMS/DMS sobre webs propias de dealers — el multiplicador.

## Global verificado este checkpoint
~910.729 vehículos · ~52/52 provincias · delta+historial vivo · API sirviendo (7 endpoints).

## HUECOS declarados (para el 100%)
1. coches.com renting XHR (8.9k) · 2. autocasion/motor.es segmentos VN/km0 (post-VO) ·
3. coches.net new/km0/renting Imperva (~10k, requiere browser) · 4. wallapop → 651k (en vuelo) ·
5. OEM proof-slice → full (en curso) · 6. otros grupos + long-tail (WF-C/WF-D) ·
7. calidad API (nombres particular vacíos) + S-HEALTH alertas E2E · 8. validador adversarial final + auditoría regresiones.
