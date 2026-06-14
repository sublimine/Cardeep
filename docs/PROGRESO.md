# PROGRESO — ejecución autónoma hacia SPAIN-SEALED

> Estado vivo del bucle. Sobrevive compactación. El Director (Opus) orquesta + verifica (gate VAM
> ≥2 vías); Sonnet construye. HANDS-OFF total, sin parar, hasta 52/52 sellado.

## Regla de oro (corrección de método 2026-06-14)
NO re-scrapear lo que ya está en DB. El latido (B2 scheduler) ya re-cosecha; el geo residual lo
cierra solo. El esfuerzo va a COBERTURA NUEVA (dealers que NINGUNA fuente tiene aún) + denominador
medido + sello. Cada agente ataca algo nuevo o muere.

## Bloques
- B1 identidad · B2 latido · B3 auto-reparación+API — ✓ CERRADOS en main.
- B4 geo — MECANISMO ✓ (POS físicos: garaje 99,6% / concesionario 96,1% / desguace 98,8%;
  compraventa 83,6%; C2C límite-API confesado). Residual lo cierra el scheduler.
- B5 cobertura — EN CURSO. Recon✓ diseño✓. Camino crítico al sello = NUMERADOR (descubrir dealers
  del long-tail) + DENOMINADOR (Chapman/provincia) + FILTRADO.
- B6 sello 52/52 — pendiente (denominador medido + numerador VAM + gap-con-causa por provincia).

## Frentes
- AS24 scale ✓ (b6rd99ih5): +41.194 coches inventario, 379 dealers cosechados (364 TRUSTWORTHY / 15
  refuted), +31 entities netas nuevas + 7 provincias (39→46), geo 96,7%. APRENDIZAJE honesto: el
  1-sort RE-COSECHA dealers conocidos (inventario fresco = valor de delta) pero descubre POCOS nuevos
  (+31, no los 1.440 del recon). DESCUBRIMIENTO masivo de dealers = Overture (10.913); AS24 =
  INVENTARIO. No martillar AS24 a mano — el scheduler B2 lo recosecha en cadencia.
- Overture ✓ (4e7209f): 10.913 puntos de venta NUEVOS limpios (compraventa 10.659 + desguace 250 +
  subasta 4), geo 99,9%. GATE cazó+borró 21.346 talleres-ruido (automotive_repair mal mapeado a
  garaje); script arreglado en raíz. Leads sin inventario (a scrapear su web), ortogonales p/Chapman.
- Chapman ✓ (08cd270): denominador robusto NO calculable hoy — dedup B1 no cruza OSM↔digital (m~20,
  83% clusters de 1 sola fuente) → N̂ disparatado. SELLABLE ya: desguaces (N̂2061 vs censo DGT 1292).
- B6.1 dedup cruzado (en vuelo, afbeff23): construye matcher OSM×Overture×digital (geo100m/web/phone,
  overlay no-destructivo) + valida en muestra. Sube m → habilita Chapman + reduce overcount compraventa.

## Siguiente paso (camino al sello, tras AS24+Overture)
**Dedup cruzado OSM×digital×Overture** por (lat/lon ±100m) OR phone_hash OR website_domain — sube el
m de Chapman de ~20 a ~200-500 (IC útil) Y colapsa el overcount de compraventa (39.308 vs floor 1.662).
Luego re-correr `scripts/recon/b6_chapman_final.py` → denominador por provincia con IC → sello B6.
Es B1 territory: overlay entity_cluster NO-destructivo (reversible), VAM antes de servir.

## Bucle
leer estado → atacar cobertura nueva por la raíz → VAM gate (≥2 vías, conteo aterrizado en DB) →
commit+push main → actualizar este archivo → siguiente frente. Sin volver a base con gate a medias.

## Snapshot 2026-06-14
379.452 entities (328.776 particular / 50.167 POS) · 1.646.674 coches vivos · 610 VAM TRUSTWORTHY ·
2 alertas (degraded auto-cerrables). Geo municipio 85,5%.
