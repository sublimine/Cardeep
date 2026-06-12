# CARDEEP — PLAN MAESTRO (A→Z)

> Diseñado por el Director Soberano el 2026-06-12 bajo el mandato de CLAUDE.md.
> Documento VIVO: se muta con registro (commit), nunca se pisa sin rastro.

## Misión (una frase)
Base de datos viva y verificada que contiene, estructurada hasta el último átomo,
el 100% de los dealers y plataformas de España y todo su inventario de coches en
tiempo real. Las recetas la mantienen, el motor la late, la API la sirve.

## Producto final — criterios duros de "terminado"
- 100% de puntos de venta de España (concesionarios, compraventas, garajes,
  desguaces) con **código único** por entidad y geo **provincia → comarca → municipio**.
- Inventario completo por entidad + **delta vivo**: altas, bajas, Δprecio, Δfoto,
  historial íntegro retenido.
- **API** que sirve por entidad y por geo; **receta versionada** por dealer
  (re-obtenible sin el crudo).
- **Resiliencia**: fallo → alerta con origen exacto → auto-reparación; ninguna
  pieza tumba el sistema.
- **Tier-1 separado absolutamente** del resto (datos, código y operación).
- **VAM transversal**: ningún número es TRUSTWORTHY sin quórum ≥2 vías ortogonales.

## Fases y gates

| Fase | Contenido | Gate (binario, verificado ≥2 vías) |
|---|---|---|
| **F0 FUNDACIÓN** [EN CURSO] | Repo main, doctrina, plan, bitácora | Commit fundacional + remoto GitHub privado con push |
| **F1 CENSO ÁTOMO ES** [LANZADO] | Universo de fuentes de descubrimiento (oficial, asociaciones, OEM/VO, plataformas, directorios, desguaces) + censo de defensas Tier-1 + arsenal OSS | `docs/research/SOURCES_ES.md`: toda fuente high verificada VIVA; denominador estimado por capture-recapture entre fuentes ortogonales |
| **F2 COLUMNA DE DATOS** | Esquema canónico (entidad, vehículo, evento-delta, foto-hash), código único, geo ES (INE: 50 prov. + comarcas + ~8.1k municipios), almacén + migraciones, API esqueleto | Migraciones E2E (apply→rollback→re-apply) + API sirviendo una entidad piloto real |
| **F3 WORKFLOWS ÁTOMO** | `descubrir / scrapear / receta / api / borrar / verificar` + orquestador `dealer-e2e`; agentes propios en `.claude/agents/` | 1 dealer real E2E 5/5 verde con VAM, evicción + tombstone probados |
| **F4 LONG-TAIL POR FAMILIA** | Clasificar webs por CMS/DMS, receta por familia (multiplicador), drenado provincia a provincia | Provincia piloto: ≥95% de entidades con inventario o veredicto justificado (sin web / sin stock online) |
| **F5 TIER-1** | Caza de receta por plataforma (Camoufox + arsenal), una a una, separadas del resto | Por plataforma: conteo 2-vías + muestra ciega verificada campo a campo |
| **F6 DELTA + HISTORIAL** | Motor de eventos: SEEN/GONE/Δprecio/Δfoto (hash perceptual), retención completa | Delta demostrado en dealer y en plataforma con evidencia re-derivada |
| **F7 RESILIENCIA** | Health por fuente, alertas origen-exacto, auto-repair (re-receta automática), watchdogs | Fallo inyectado → alerta correcta + reparación sin caída del sistema |
| **F8 SELLO 100%** | Cierre por provincia: censo vs cobertura, capture-recapture, parte honesto | 50/50 provincias selladas o gap declarado con causa exacta |

F4 y F5 corren en paralelo tras F3; F6-F7 se cablean en cuanto F3 produce datos vivos.

## Decisiones técnicas
**Tomadas:**
- LLM local para lo masivo (clasificar, parsear, deduplicar); inteligencia cara
  solo para decidir. (Mandato §coste.)
- Crudo efímero en `data/` (gitignored); evicción LRU por watermark de disco SOLO
  con 3 gates verdes: ingesta TRUSTWORTHY + receta/config commiteadas + conteos
  cuadrados. Tombstone como prueba de vida.
- Delta por INSERT de lo nuevo + DELETE/cierre de lo desaparecido; jamás UPDATE
  de filas no mutadas. `last_seen` + historial append-only.
- Conventional Commits por fase; main = única fuente de verdad.

**Abiertas (se cierran al inicio de F2, informadas por los volúmenes reales de F1):**
- Motor de almacén (inclinación: PostgreSQL 16 en Docker + FastAPI; decisión con
  números de F1 en la mano).
- Esquema del código único de dealer (formato, inmutabilidad, colisiones).
- Hash perceptual para Δfoto (pHash vs dHash; coste por foto a volumen).

## Reglas de operación (no negociables)
1. PROGRESO.md se actualiza tras CADA bloque; el estado no vive solo en contexto.
2. La salida de todo subagente es SOSPECHOSA: se re-verifica por vía independiente
   antes de consolidarla. El Inquisidor no delega el veredicto.
3. Gate rojo → se aborta el dealer/fuente y se registra el fallo; jamás se oculta.
4. Mejor confesar un hueco que vender una mentira.
