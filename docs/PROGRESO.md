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

## Frentes en vuelo (gate del Director al volver)
- AS24 drain cobertura (compraventas: 262 dealers de 278k coches → descubrir miles).
- Overture Maps (POIs car_dealer nuevos, long-tail, €0, ortogonal a plataformas).
- Chapman denominador por provincia (camino directo al sello).

## Bucle
leer estado → atacar cobertura nueva por la raíz → VAM gate (≥2 vías, conteo aterrizado en DB) →
commit+push main → actualizar este archivo → siguiente frente. Sin volver a base con gate a medias.

## Snapshot 2026-06-14
379.452 entities (328.776 particular / 50.167 POS) · 1.646.674 coches vivos · 610 VAM TRUSTWORTHY ·
2 alertas (degraded auto-cerrables). Geo municipio 85,5%.
