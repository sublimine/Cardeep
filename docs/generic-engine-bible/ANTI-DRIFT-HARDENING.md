# BLINDAJE — Anti-alucinación · Anti-desvío · Contexto total
> Mandato owner 2026-06-27. Tres garantías **mecánicas** (impuestas por construcción, no por buena voluntad). La confianza nace SOLO de verificación multi-vía. Aplica a TODO componente: motor determinista, IA local, agentes de Claude, orquestación.

## 1 · Anti-alucinación — *nada se inventa*
1. **Decodificación restringida** (gramática GBNF/JSON-Schema): el LLM es *físicamente incapaz* de emitir un valor fuera de vocabulario o un JSON inválido → 0 parse-fails, 0 enum-inventado.
2. **Provenance obligatoria** por campo/afirmación: fuente + modelo/regla + offset. Toda salida es trazable a su origen.
3. **VAM por triggers de DB**: ningún número es TRUSTWORTHY sin **quórum ≥2 vías ortogonales** (`chk_trustworthy_needs_quorum`). No es política — es un CHECK en la base.
4. **Etiqueta `[VERIFIED]` / `[ASSUMED]`** obligatoria en todo agente y documento. Un ASSUMED jamás se presenta como VERIFIED.
5. **Cross-check LLM ↔ determinista**: donde ambos opinan (precio/km/año), gana el determinista; el desacuerdo se marca y escala.
6. **Golden-set + gate de CI**: cualquier regresión de exactitud/F1 (por cambio de modelo/prompt/gramática/código) bloquea el merge.
7. **Hash-chain tamper-evident** (`verdict_audit`): el historial de veredictos no se puede reescribir.

## 2 · Anti-desvío ("desviamiento de vía") — *nada se sale de vía*
1. **Contrato autocontenido por job/agente**: input-schema, output-schema, criterio de éxito. Sin contrato no corre → cero free-roaming.
2. **Máquina de estados** (`work_item` + `cover(CC)`): un componente solo puede ejecutar **el siguiente paso legal**; toda transición es idempotente y transaccional (crash-safe).
3. **Regla de oro — prohibido adivinar:** ante incertidumbre que no puede resolver EN VÍA, el componente **ESCALA** (`decision_request` → Claude), NUNCA improvisa. Adivinar = desviarse; el sistema lo enruta a la capa-3 en lugar de permitirlo.
4. **Gates de avance** (G1–G5, sellado, dry-run:5434 → golden → Ferrari → CI): no se progresa fuera de spec; un gate rojo es un STOP.
5. **Vía `EXHAUSTED` no se reintenta**: corta el bucle de desvío infinito.
6. **Aislamiento por item**: un fallo aislado no arrastra al resto (*Cardeep no se cae* a nivel de item).

## 2bis · Resiliencia de producción — *ningún error para el todo* (supervisión activa)
1. **Fault-isolation a todo nivel:** un agente que falla NO para su ola; una ola con un hueco NO para la campaña. El orquestador (Claude) **aísla → verifica multi-vía → recupera (re-lanza la pieza) → avanza**. Nunca congela. Es el "Cardeep no se cae" elevado al nivel de producción/desarrollo.
2. **La etiqueta no es prueba:** todo "fallo" reportado se contrasta contra disco/DB antes de actuar (caso real 2026-06-27: 2 "fallos" de Ola 2 = archivos SÍ escritos; falló la salida estructurada de retorno, no la obra).
3. **Supervisión activa continua, no por lotes:** en cada aterrizaje → QC del artefacto (red-flags/estructura/`[VERIFIED]`) + recuperación de lo fallido + encadenado de la siguiente ola, sin pausa.
4. **Los gates PENDING-OWNER no son fallos:** parquean el residual con causa, no detienen el loop. Prohibido declarar 100% con residual gated abierto.

## 3 · Contexto total — *todo sabe qué hacer en todo momento*
1. **Contexto permanente** disponible para todo agente: `README` (funnel) + `00-MASTER` (constitución) + `COUNTRY-PACK-CONTRACT` + el **Dossier de País** vigente.
2. **Brief autocontenido por work-item**: un agente fresco lo ejecuta **en frío** sin perder el hilo (patrón blueprint). El item lleva su objetivo, su contrato y su contexto.
3. **El orquestador (Claude) siempre tiene** `00-MASTER` + `PROGRESO` + el estado del bus de decisiones.
4. **La DB es la verdad operativa consultable**: estado + provenance + veredictos siempre disponibles → ningún componente opera a ciegas.

## Cómo se PRUEBA (multi-vía = única fuente de confianza)
Cada mecanismo de arriba no se declara "blindado" hasta tener **las tres**:
- **(a)** un test que lo demuestra (verde en CI),
- **(b)** un intento adversarial que trata de romperlo (y falla en romperlo),
- **(c)** una verificación por **vía independiente** del que lo produjo.
Sin las tres, el mecanismo está `[ASSUMED]`, no `[VERIFIED]`.

## Ambición
El listón: que ningún intelecto —humano o IA— pueda replicar en años lo bien blindado y orquestado que está. Cada componente, exprimido al máximo, sabiendo exactamente su trabajo, con contexto total, sin inventar y sin desviarse.
