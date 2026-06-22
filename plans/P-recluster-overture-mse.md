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

## Pasos FK-safe (ejecución, cada uno verificado antes del siguiente)
0. **Snapshot rollback** (anotar): `SELECT count(DISTINCT resolved_cdp_code) FROM v_dealer_resolved`;
   sello servido actual (`/geo/seal` o v_exhaustiveness_seal); `SELECT count(*) FROM entity_cluster
   WHERE cluster_run_id='dealer-identity-det-v1'`.
1. **Liberar el FK** (1 txn, reversible): `DELETE FROM canonical_dedup_run WHERE
   source_cluster_run='dealer-identity-det-v1';` (cascade borra canonical_dedup hijos). Verificar 0 filas.
2. **Re-cluster B1:** `python -m pipeline.identity.cluster_dealers` → leer VERIFICATION REPORT.
   ANTI-FP: la tasa de merge no debe dispararse (overture POIs con nombres genéricos podrían sobre-mergear
   distintos dealers en una misma muni). Comparar n_merged/n_clusters vs snapshot; si el merge-rate sube
   anómalo → STOP, investigar el blocking (raíz, no forzar).
3. **Re-build super-canónico:** `python -m scripts.build_canonical_dedup` (regenera canonical_dedup_run
   referenciando el run fresco). Verificar la fila nueva.
4. **Verificar resolved:** `SELECT count(DISTINCT resolved_cdp_code) FROM v_dealer_resolved` — debe SUBIR
   sensatamente (no colapsar). API `/health` coherente.
5. **Re-evaluar MSE:** `python -m pipeline.exhaustiveness.cli run --run-id <new> --threshold 0.95
   --unit resolved` (+ `--unit splink --splink-run-id <...>`). Comparar sello servido: pudo MOVERSE
   (overture sube `m`). Reportar el número honesto (suba o no, con causa).
6. **Auditoría:** suite Ferrari completa 0 failed; API sirve cifras coherentes; PROGRESO+memoria.

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
