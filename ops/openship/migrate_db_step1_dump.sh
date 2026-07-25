#!/usr/bin/env bash
# Cardeep DB migration — step 1 (run LOCAL, on this Windows machine via Git Bash).
# Dumps the live local Postgres in custom format (compressed, ~813MB confirmed
# 2026-07-25 vs ~10GB raw) and copies it to the VM. Step 2 (restore) runs on the VM
# itself, once `openship deploy` has the cardeep-pg service up — the exact container
# name depends on how Openship names services-mode containers, unverified until then.
set -euo pipefail

VM_IP="${1:?uso: migrate_db_step1_dump.sh <PUBLIC_IP>}"
SSH_KEY="/c/Users/elias/.cardeep-ops-secrets/oci/cardeep_vm_key"
DUMP_FILE="/tmp/cardeep_migration.dump"

echo "=== Dump local (custom format, comprimido) ==="
MSYS_NO_PATHCONV=1 docker exec cardeep-pg pg_dump -U cardeep -d cardeep -Fc -f "$DUMP_FILE"
MSYS_NO_PATHCONV=1 docker cp cardeep-pg:"$DUMP_FILE" ./cardeep_migration.dump
MSYS_NO_PATHCONV=1 docker exec cardeep-pg rm "$DUMP_FILE"
ls -la ./cardeep_migration.dump

echo "=== Copiando a la VM ($VM_IP) ==="
scp -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new ./cardeep_migration.dump ubuntu@"$VM_IP":/home/ubuntu/cardeep_migration.dump

echo "=== Dump copiado. Siguiente: restaurarlo DENTRO del contenedor cardeep-pg de la VM ==="
echo "(ver migrate_db_step2_restore.sh — requiere confirmar el nombre real del contenedor primero)"
rm ./cardeep_migration.dump
