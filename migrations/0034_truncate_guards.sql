-- 0034_truncate_guards.sql — seal append-only ledgers against TRUNCATE (audit F2)
--
-- The row-level immutability guards (0005 cardeep_block_mutation, 0026 cdp_audit_immutable,
-- 0033 audit_eviction_immutable) fire on UPDATE/DELETE FOR EACH ROW. TRUNCATE does NOT fire
-- row-level triggers, so an append-only ledger could be wiped wholesale despite its row guard
-- (and `cardeep` is superuser). This adds a BEFORE TRUNCATE FOR EACH STATEMENT guard to every
-- append-only table — defence-in-depth against accidental/non-superuser truncation.
--
-- cardeep_block_mutation() (0005) references only TG_TABLE_NAME/TG_OP (no OLD/NEW), so it is
-- reused verbatim — TG_OP resolves to 'TRUNCATE' in the statement-level context.
--
-- Tables covered: vehicle_event, verdict_audit, gestion_transition, audit_eviction.
-- Verified (live, 2026-06-15): none had a TRUNCATE trigger; no code path TRUNCATEs them
-- (archival of cold months uses DROP PARTITION — DDL, intentionally unaffected per 0005).
--
-- SEPARATE FINDING (documented, NOT sealed here): vehicle_event and gestion_transition are
-- documented append-only but have NO row-level UPDATE/DELETE guard in the live schema — a wider
-- gap needing a usage review before enforcement. This migration blocks only TRUNCATE, which is
-- unambiguously never legitimate on a history/audit table.
--
-- Additive, idempotent, reversible. migrate.py applies only the forward section.

DROP TRIGGER IF EXISTS trg_vehicle_event_notrunc ON vehicle_event;
CREATE TRIGGER trg_vehicle_event_notrunc
  BEFORE TRUNCATE ON vehicle_event
  FOR EACH STATEMENT EXECUTE FUNCTION cardeep_block_mutation();

DROP TRIGGER IF EXISTS trg_verdict_audit_notrunc ON verdict_audit;
CREATE TRIGGER trg_verdict_audit_notrunc
  BEFORE TRUNCATE ON verdict_audit
  FOR EACH STATEMENT EXECUTE FUNCTION cardeep_block_mutation();

DROP TRIGGER IF EXISTS trg_gestion_transition_notrunc ON gestion_transition;
CREATE TRIGGER trg_gestion_transition_notrunc
  BEFORE TRUNCATE ON gestion_transition
  FOR EACH STATEMENT EXECUTE FUNCTION cardeep_block_mutation();

DROP TRIGGER IF EXISTS trg_audit_eviction_notrunc ON audit_eviction;
CREATE TRIGGER trg_audit_eviction_notrunc
  BEFORE TRUNCATE ON audit_eviction
  FOR EACH STATEMENT EXECUTE FUNCTION cardeep_block_mutation();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_vehicle_event_notrunc ON vehicle_event;
-- DROP TRIGGER IF EXISTS trg_verdict_audit_notrunc ON verdict_audit;
-- DROP TRIGGER IF EXISTS trg_gestion_transition_notrunc ON gestion_transition;
-- DROP TRIGGER IF EXISTS trg_audit_eviction_notrunc ON audit_eviction;
