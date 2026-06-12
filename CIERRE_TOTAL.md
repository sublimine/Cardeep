# CARDEEP — CIERRE TOTAL (campaña hands-off, 2026-06-13)
> Objetivo (CLAUDE.md): API viva y verificada con el 100% de los puntos de venta de
> España + plataformas y TODO su inventario (usados, NUEVOS, km0, renting, particulares)
> en tiempo real, con delta, receta, geo y código único; auto-reparable; Tier-1 separado.
> Estándar: NINGÚN número sin verificar por ≥2 caminos (VAM). Mejor confesar hueco que mentir.

## Estado base verificado (2026-06-13, por mi mano)
- API viva: 545k coches · 69k vendedores · 52/52 provincias · 549k eventos delta.
- coches.net CERRADO 100%: 272.903 (155.086 dealers + 117.817 particulares), VAM TRUSTWORTHY.
- 7 plataformas + 3 OEM-VO conectadas. Schema 0001-0017. Todo en GitHub main.

## HUECOS DECLARADOS (lo que falta para el 100% — sin maquillaje)
| # | Frente | Hueco | Criterio de aceptación (verificable) |
|---|--------|-------|--------------------------------------|
| A | Segmentos Tier-1 | Conectores drenan solo 1-2 segmentos. coches.com solo VO (falta vn.xml NUEVOS + renting). Auditar TODAS por segmento perdido (VN/km0/renting). | Por plataforma: Σ segmentos en DB == Σ counts publicados por la fuente, VAM ≥2 caminos. |
| B | Grupo OEM-VO | Solo renew/dasweltauto/spoticar. Faltan MB, Hyundai, Toyota/Lexus, Kia, Ford, Seat/Cupra, Audi, BMW, Nissan, Mazda, Honda, Volvo... | Cada portal OEM-VO ES con superficie real → conector + inventario verificado. |
| C | Otros grupos | rent-a-car VO, subastas, importadores sin cubrir. | ≥1 fuente real por grupo conectada y verificada. |
| D | Long-tail | Webs propias de dealers sin cosechar (el multiplicador). | Clasificación CMS + receta por familia top + N dealers cosechados de su web. |
| E | API + calidad | Particulares con trade_name vacío; verificar API sirve todo; S-HEALTH alertas vivas. | API sirve todos los kinds; 0 nombres basura; breaker+alerta+auto_repair E2E. |
| F | Verificación final | VAM adversarial por plataforma; auditoría de regresiones. | Validador supremo PASS por plataforma; 0 regresiones. |

## Olas (paralelo + cascada)
- **Ola 1 (AHORA)**: WF-A segment-completion · WF-B oem-vo-expansion · WF-D longtail-multiplier · + drenajes en vuelo.
- **Ola 2**: WF-C otros-grupos · WF-E api-calidad+resiliencia.
- **Ola 3**: WF-F validador-supremo adversarial + auditoría regresiones + drenajes full por mi mano.
- **Cierre**: re-verificar cada criterio A-F por mi mano, commit+push, parte de entrega honesto.

## Reglas
- Cada número → VAM ≥2 caminos o UNVERIFIED. Lo verifico YO contra DB.
- Estado a PROGRESO.md tras cada ola. Drenajes largos por mi mano en background.
- Todo a GitHub main. Tier-1 separado de los demás grupos siempre.
