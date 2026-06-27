# 🧭 EMPIEZA AQUÍ — Motor Genérico de Cobertura de País (Cardeep)
> Entrada única. Si eres una IA o persona retomando esto: lee este funnel y sabrás exactamente dónde está todo y por qué. Cero pérdida.

## Qué es
Un **motor genérico** que cubre el censo de huella digital del 100% de los puntos de venta de coches de **cualquier país**. España fue la primera ejecución (el banco de pruebas que lo endureció), **no** el producto. País nuevo = otra ejecución — nunca un rewrite.

## El funnel (de "quiero cubrir un país" a "sellado")
```
            cover(country_code)
                   │
   ┌───────────────▼───────────────┐
   │ 1. KNOW_COUNTRY                │  ← Claude investiga el país/mercado a fondo.
   │    Dossier de País (A–G)       │     NADA procede sin esto. → COVER-NEW-COUNTRY.md
   └───────────────┬───────────────┘
   ┌───────────────▼───────────────┐
   │ 2. BOOTSTRAPPED                │  ← del Dossier se DERIVA el pack 100%-personalizado
   │    pack por etapa (1–9)        │     de las 9 etapas. → stages/ + COUNTRY-PACK-CONTRACT.md
   └───────────────┬───────────────┘
   ┌───────────────▼───────────────┐
   │ 3. IN_COVERAGE                 │  ← el MOTOR (invariante) corre las 9 etapas sobre el pack;
   │    descubrir→…→servir          │     Claude drena el bus de decisiones. → stages/01..09
   └───────────────┬───────────────┘
   ┌───────────────▼───────────────┐
   │ 4. SEALED                      │  ← cobertura = INTERVALO certificado (cota inferior),
   │    certificación + delta vivo  │     no un entero. → stages/07-quality-seal.md
   └────────────────────────────────┘

 Capas transversales: orquestación (Claude + IA local + determinista) · enrutado LLM por tarea
 · observabilidad · invariantes (cdp_code, VAM cero-confianza, append-only, €0).
```

## Las 9 etapas del motor (qué hace cada una)
1. **Descubrir** — encuentra qué puntos de venta existen.
2. **Scrapear** — saca el stock de cada uno.
3. **Extraer/Normalizar** — crudo → datos limpios.
4. **Identidad** — un dealer real = un registro con código único.
5. **Vehículo** — el mismo coche físico = un registro, esté donde esté.
6. **Geo** — ubica dealer y coche (árbol administrativo del país).
7. **Calidad/Sello** — prueba cuánto del 100% real tienes (denominador + cobertura honesta).
8. **Servir** — la API que entrega todo con su delta e historial.
9. **Orquestar/Observar** — el daemon que lo mantiene vivo, fresco y avisa si algo cae.

## Mapa de documentos (dónde está cada cosa)
| Quiero… | Ir a |
|---|---|
| Entender el todo y las reglas | `00-MASTER.md` (constitución: decisiones, modelo 3-capas, invariantes, operación) |
| Onboardar un país nuevo | `COVER-NEW-COUNTRY.md` (KNOW_COUNTRY + estados cover(CC)) |
| El diseño A→Z de una etapa | `stages/01-discover.md … 10-automation.md` |
| Qué LLM lleva cada tarea | `LLM-ROUTING-MATRIX.md` |
| El contrato del country-pack | `COUNTRY-PACK-CONTRACT.md` |
| Las mejoras a nivel inalcanzable | `NEXT-LEVEL.md` |
| Cómo se blinda (anti-alucinación / anti-desvío / contexto total) | `ANTI-DRIFT-HARDENING.md` |
| El des-cegado de país (`country_code` en el esquema, no en la lógica) | `SPINE-COUNTRY-THREADING.md` (diagnóstico + programa unificado de remediación) |
| La genericidad auto-impuesta (anti false-merge de país) | `COUNTRY-PROOF-INVARIANT.md` |
| El backlog institucional (283 micro-proyectos por etapa) | `INSTITUTIONAL-BACKLOG.md` |
| El plan ejecutable PR-por-PR (bible → build) | `REMEDIATION-BLUEPRINT.md` |
| Estado vivo + reanudación hands-off | `PROGRESO.md` |
| Detección de punto de venta + taxonomía de tiers/grupos | `POS-DETECTION-AND-TIERS.md` *(Ola 2.5)* |

## Reglas no negociables (la "física")
- **Desconfianza total:** ningún número sin **≥2 vías ortogonales** (VAM, impuesto por triggers en la DB). Verificar es la única fuente de confianza.
- **Probado y funcional** antes de declarar nada hecho. Adversarial co-igual.
- **€0** de cimiento; el GPU/LLM masivo es palanca con firma del owner.
- **España se preserva:** tomar lo verificado → generalizar → mejorar.
- Cada cambio servido: dry-run(:5434) → golden → Ferrari → CI → integrar en serie.

## Estado (vivo)
Ver `00-MASTER.md` §Cadencia. En construcción: Ola 1 (etapas) + Ola 1.5 (LLM) en curso; síntesis y mejora después.
