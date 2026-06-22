# PLAN — Re-cluster dealers (fold Overture) + re-evaluate MSE seal

**Estado:** LISTO PARA EJECUTAR (inventario verificado 2026-06-22). Ejecutar en iteración fresca.
**Owner gate:** ninguno (todo €0, reversible, datos servidos pero operación determinista+verificable).

## Objetivo
Plegar las entidades nuevas de Overture al resolved/served layer y re-medir el sello MSE.
Overture aportó (verificado): **18.313 compraventa + 86 concesionario = 18.399 EN scope de venta**;
**13.369 net-new (solo overture)** + **7.513 overlap** (sube el `m` del MSE). Hoy están en `entity`
pero NO en `v_dealer_resolved` (requieren cluster_dealers) → no cuentan en censo servido ni en el MSE.

## Inventario verificado (no asumir)
- `pipeline/identity/cluster_dealers.py`: RUN_ID="dealer-identity-det-v1", union-find determinista
  sobre **~79.821 entidades kind<>particular** (carga en memoria línea 236-257) + edges fuzzy en PG
  temp-table con blocking por muni (línea 262-379). **LIGERO** (~79k, no millones): NO necesita parar
  workers. (El "4-6GB RAM" de notas previas era cluster_VEHICLES, 1.9M — NO esto.)
- Escritura (581-635): en 1 txn, `DELETE entity_cluster WHERE cluster_run_id=RUN_ID` →
  `DELETE entity_cluster_run WHERE cluster_run_id=RUN_ID` → re-INSERT. Imprime VERIFICATION REPORT (643+).
- **FK que bloquea** (0027:48-49): `canonical_dedup_run.source_cluster_run REFERENCES
  entity_cluster_run(cluster_run_id)` **SIN ON DELETE CASCADE** → el DELETE de entity_cluster_run falla
  si existe una fila canonical_dedup_run con source_cluster_run='dealer-identity-det-v1'.
- `canonical_dedup.run_id REFERENCES canonical_dedup_run(run_id) ON DELETE CASCADE` (0027:70-71) →
  borrar la fila canonical_dedup_run arrastra sus hijos canonical_dedup automáticamente.
- Super-canónico regenerado por `scripts/build_canonical_dedup.py` (→ canonical_dedup_run/canonical_dedup).
- `v_dealer_resolved` / `v_canonical` = vistas derivadas (refrescan solas).

## ⚠ HALLAZGO CRÍTICO (2026-06-23, snapshot en vivo — corrige el plan original)
El FK que bloquea el re-cluster lo cumplen **LAS 3** filas de canonical_dedup_run, TODAS con
`source_cluster_run='dealer-identity-det-v1'`: `canonical-dedup-deeplink-v1`, `particular-canonkey-v1`,
y **`residual-namemuni-v1`** (la SERVIDA: v_dealer_resolved usa `latest_run = canonical_dedup_run WHERE
vam_verified=true ORDER BY run_id DESC LIMIT 1` → residual-namemuni-v1). Por tanto re-clusterizar exige
borrar las 3 y REGENERAR las 3 (no solo deep-link). Generadores (verificado): build_canonical_dedup.py →
deeplink; build_particular_dedup.py(+gate_particular_dedup.py) → particular-canonkey; build_residual_
namemuni_dedup.py(--commit) → residual-namemuni. Gate vam_verified=TRUE/FALSE = gate_particular_dedup.py
(REVERSIBLE). Entre borrado y re-gate, v_dealer_resolved cae al fallback B1 (COALESCE a b1_cdp) — sirve,
sin la capa super-canónica, temporalmente.

## Pasos (ejecución en iteración fresca, cada uno verificado antes del siguiente)
0. **Snapshot rollback** (anotar): resolved_cdp_code distinct en v_dealer_resolved (baseline 2026-06-23 =
   408.663); B1 entity_cluster_run (n_in=61.551, out=42.259, merged=19.292); las 3 canonical_dedup_run
   (run_id, vam_verified, n_super_canonicals); sello servido.
1. **Liberar el FK** (reversible): `DELETE FROM canonical_dedup_run WHERE source_cluster_run=
   'dealer-identity-det-v1';` (cascade borra canonical_dedup hijos de las 3). Verificar 0 filas.
2. **Re-cluster B1:** `python -m pipeline.identity.cluster_dealers` (input ~91.319 no-particular) → LEER
   VERIFICATION REPORT. ANTI-FP: merge-rate no debe dispararse (overture/collapse con nombres genéricos +
   sin muni → riesgo sobre-merge por phone/host; entidades sin muni quedan singletons = bajo riesgo).
   Si merge-rate anómalo → STOP, raíz (no forzar).
3. **Regenerar LAS 3 super-canónicas** (en orden; cada una verifica su fila):
   a. `python -m scripts.build_canonical_dedup`            (→ canonical-dedup-deeplink-v1)
   b. `python -m scripts.build_particular_dedup`           (→ particular-canonkey-v1)
   c. `python -m scripts.build_residual_namemuni_dedup --commit`  (→ residual-namemuni-v1, la servida)
4. **Gate la servida vam_verified=TRUE** si el builder no lo dejó (verificar; gate_particular_dedup.py
   apply para el run servido). Confirmar v_dealer_resolved.latest_run resuelve a residual-namemuni-v1.
5. **Verificar resolved:** resolved_cdp_code distinct debe SUBIR sensatamente (no colapsar) vs 408.663.
   API `/health` coherente. Anti-FP de cifras servidas.
6. **Re-evaluar MSE:** `python -m pipeline.exhaustiveness.cli run --run-id <new> --threshold 0.95
   --unit resolved` (+ `--unit splink --splink-run-id <...>`). Sello servido pudo MOVERSE (overture sube
   `m`). Reportar honesto (suba o no, con causa). NO maquillar.
7. **Auditoría:** suite Ferrari completa 0 failed; API coherente; PROGRESO+memoria+doc.

## Rollback ampliado
Cada builder + el gate son reversibles (re-ejecutables / `gate ... --revert` → vam_verified=FALSE).
cluster_dealers determinista (mismo RUN_ID). Si algo falla a mitad: el fallback B1 de v_dealer_resolved
mantiene servicio; re-ejecutar la cadena 2→4 restaura. Snapshot paso 0 = baseline de comparación.

## Riesgos y mitigación
- **Sobre-merge** (overture genérico) → VERIFICATION REPORT anti-FP (paso 2); si anómalo, STOP+raíz.
- **Mutación de datos servidos** → determinista+re-ejecutable (mismo RUN_ID); snapshot paso 0 para comparar;
  los workers siguen vivos (operación ligera, no los paro).
- **FK** → resuelto por paso 1.
- **Sello baja** (más universo, menos cobertura aparente) → es honesto; reportar con causa, NO maquillar.

## Aceptación
- VERIFICATION REPORT limpio (merge-rate sano), resolved sube sin colapso, sello re-medido honesto,
  Ferrari 0 failed, API coherente, PROGRESO+memoria+doc.

## Rollback
- Paso 1 reversible re-corriendo build_canonical_dedup tras un cluster_dealers. cluster_dealers es
  idempotente/determinista (mismo RUN_ID): re-correr restaura. Vistas derivadas. Snapshot paso 0 = baseline.
