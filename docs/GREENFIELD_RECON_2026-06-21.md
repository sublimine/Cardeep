# CARDEEP — Greenfield own-site recon (2026-06-21)

> Workflow `wrtdqoctu` (33 agentes: 24 investigadores WebFetch + verificacion adversarial + sintesis).
> Muestra: 24 dealers sin inventario con web propia unica (1/provincia), de 6.628 candidatos.

## Veredicto
- CONFIRMED cosechable (web propia + inventario real de coches, pasa adversarial): **8/24 = 33%**.
- Extrapolado a 6.628: ~2.200 sitios (IC Wilson 1.180-3.500; CAVEAT: muestreo 1/provincia no aleatorio = orden de magnitud).
- 2/3 ruido 0-legitimo: 7 subdominio-OEM (ya cosechado), 5 no-coches (maquinaria/taller), 2 presencia-only, 2 muertos.
- ROI GATED por SOLAPAMIENTO no medido: el stock own-site suele estar tambien en marketplaces ya cosechados.
- Cableado fragmentado: 1/8 DealerK (escala), 3/8 WordPress (heterogeneos), 4/8 bespoke (no escala).

## 8 CONFIRMED (web propia con inventario real)
- CDP-ES-02-AXRVMCKM `https://www.albacoches.com` -> family_generic_custom | https://www.albacoches.com/vehiculos/
- CDP-ES-10-AY6Z3EVW `https://valhondoautomocion.com/` -> family_cms_wp | https://valhondoautomocion.com/autos
- CDP-ES-11-N9FBPJA7 `https://www.acautomocion.com` -> family_generic_custom | https://www.acautomocion.com/assets/pages/listado.php
- CDP-ES-12-NMZ41WQB `https://horizontauto.com` -> family_generic_custom | https://www.horizontauto.com/coches-segunda-mano-valencia/suv/
- CDP-ES-14-S02ZPQ9T `https://willysautos.es` -> family_cms_wp | https://willysautos.es/coches-de-segunda-mano-y-ocasion-cordoba/
- CDP-ES-15-3T7N4N2S `http://www.autoscalvino.com` -> family_generic_custom | http://www.autoscalvino.com/automovilesocasion.asp
- CDP-ES-23-HZAC8M63 `https://valenza.es` -> family_cms_wp | https://valenza.es/vehiculos/
- CDP-ES-24-M0WMJRV0 `https://www.eslauto.es/citroen/` -> family_dms_vendor | https://www.eslauto.es/coches/nuevos-entrega-inmediata+segunda-mano+km0/?ref_brand=citroen

## Proximo paso (€0, antes de cablear): MEDIR SOLAPAMIENTO
Cruzar el stock de los 8 CONFIRMED (marca+modelo+año+km+precio) contra el grafo CARDEEP ya cosechado.
- solapamiento >70% -> greenfield own-site = espejismo -> profundizar marketplaces walled (coches.net/wallapop/milanuncios).
- solapamiento <40% -> valor incremental real -> cablear SOLO DealerK + extractor WP heuristico (escalan); long-tail bespoke = manual/nunca.
