#!/usr/bin/env bash
# Supervised road-to-13 cutover — applies migrations 0070 (vam_verified trigger) + 0071 (entity_cluster
# country-proof trigger) to the :5433 PRODUCTION database SAFELY, then any later pending migrations the
# repo HEAD carries. THE OWNER RUNS THIS (it writes DDL to :5433 serving-of-record); the agent does not.
#
# Why it is safe to run:
#   - additive / forward-only: the triggers reject only FUTURE invalid writes; existing rows untouched.
#   - reversible: DROP TRIGGER reverts in seconds (printed at the end).
#   - all writers audited compatible: gate_particular_dedup (verdict), build_canonical_dedup (FALSE),
#     build_residual_namemuni_dedup (verdict, fixed f363d9a), cross_source_dedup + cluster_dealers
#     (mono-country). See plans/road-to-13/PROGRESO.md.
#   - aborts on ANY error (set -e); takes a backup first; post-check confirms triggers present,
#     0 NEW country-proof violations, and served-count unchanged (triggers must not move data).
#
# Usage:   bash scripts/cutover_road13.sh
# Rollback: printed at the end (DROP TRIGGER on both tables).
set -euo pipefail

PROD_CONTAINER="${PROD_CONTAINER:-cardeep-pg}"
DSN="${CARDEEP_DSN:-postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep}"
TS="$(date +%Y%m%d_%H%M%S)"
BACKUP="cutover_r13_backup_${TS}.sql"

psql_prod() { docker exec "${PROD_CONTAINER}" psql -U cardeep -d cardeep -tAc "$1"; }

echo "== road-to-13 cutover -> :5433 (container ${PROD_CONTAINER}) =="

# 1. DB reachable
docker exec "${PROD_CONTAINER}" pg_isready -U cardeep -d cardeep >/dev/null 2>&1 || {
  echo "ABORT: ${PROD_CONTAINER} not ready. Start it first:  docker compose up -d cardeep-pg"; exit 1; }

# 2. Pre-state: what is applied, no drift, served snapshot
DB_HEAD="$(psql_prod "SELECT COALESCE(max(version),'<none>') FROM schema_migrations")"
echo "-- pre-state: :5433 migration HEAD=${DB_HEAD} (repo HEAD=0071) --"
echo "   migrate verify (must be drift-free before applying):"
CARDEEP_DSN="${DSN}" python scripts/migrate.py verify
SERVED_BEFORE="$(psql_prod "SELECT count(DISTINCT resolved_cdp_code) FROM v_dealer_resolved")"
echo "   served identities before: ${SERVED_BEFORE}"
echo "   NOTE: migrate up applies EVERY pending migration above ${DB_HEAD}, not only 0070/0071. Review."

# 3. Backup the tables the triggers touch (restore target if anything goes wrong)
echo "-- backup -> ${BACKUP} --"
docker exec "${PROD_CONTAINER}" pg_dump -U cardeep -d cardeep \
  -t canonical_dedup_run -t entity_cluster -t verification_verdict > "${BACKUP}"
echo "   backup written: ${BACKUP} ($(wc -c < "${BACKUP}") bytes)"

# 4. Apply
echo "-- applying pending migrations --"
CARDEEP_DSN="${DSN}" python scripts/migrate.py up

# 5. Post-check (fail-closed on the structural checks; warn on data deltas for human review)
echo "-- post-check --"
N_TRIG="$(psql_prod "SELECT count(*) FROM pg_trigger WHERE tgname IN ('trg_canonical_dedup_vam_proof','trg_entity_cluster_country')")"
[ "${N_TRIG}" = "2" ] || { echo "ABORT: expected 2 triggers, found ${N_TRIG}. Check migrate output."; exit 1; }
VIOL="$(psql_prod "SELECT count(*) FROM v_country_proof_violations")"
SERVED_AFTER="$(psql_prod "SELECT count(DISTINCT resolved_cdp_code) FROM v_dealer_resolved")"
echo "   triggers present: ${N_TRIG}/2 | country-proof violations: ${VIOL} | served: ${SERVED_BEFORE} -> ${SERVED_AFTER}"
[ "${VIOL}" = "0" ] || echo "   WARN: ${VIOL} country-proof violation(s) — pre-existing data, review (trigger blocks only NEW ones)."
[ "${SERVED_AFTER}" = "${SERVED_BEFORE}" ] || echo "   WARN: served count moved — triggers are additive and should NOT change it; review."

echo "== CUTOVER OK — vam_verified + country-proof are now MECHANICAL on :5433 (serving-of-record). =="
echo "Rollback (reversible, additive triggers):"
echo "  docker exec ${PROD_CONTAINER} psql -U cardeep -d cardeep -c \"DROP TRIGGER IF EXISTS trg_canonical_dedup_vam_proof ON canonical_dedup_run; DROP TRIGGER IF EXISTS trg_entity_cluster_country ON entity_cluster;\""
