-- 0092_adcopy_generation.sql — 07-marketing F5: grounded ad copy (C7).
--
-- Every generation is persisted WITH its full provenance (input_snapshot + claims),
-- whether it passed the grounding gate ('grounded') or was caught inventing an
-- ungrounded numeral ('rejected') — carta S5.2: "lo rechazado tambien se persiste
-- (auditoria del gate)". The snapshot's content hash is the cache key (carta S8:
-- "Cacheable por (vehicle_ulid, hash(input_snapshot)): si ni el coche ni sus
-- comparables cambiaron, cero re-gasto").
--
-- Additive, idempotent, reversible. migrate.py applies only the forward section.

CREATE TABLE IF NOT EXISTS adcopy_generation (
    gen_ulid         TEXT PRIMARY KEY,
    vehicle_ulid     TEXT NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    input_snapshot   JSONB NOT NULL,
    snapshot_hash    TEXT NOT NULL,
    claims           JSONB NOT NULL,
    output_text      TEXT,                        -- NULL when status='rejected'
    model_used       TEXT NOT NULL,
    status           TEXT NOT NULL
        CHECK (status IN ('grounded', 'rejected')),
    unbacked_numerals JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_adcopy_vehicle ON adcopy_generation (vehicle_ulid, created_at DESC);
-- Cache lookup: reuse a prior GROUNDED generation for the SAME (vehicle, snapshot) pair
-- instead of re-spending on the expensive model (carta S8's cache key).
CREATE INDEX IF NOT EXISTS idx_adcopy_cache_key
    ON adcopy_generation (vehicle_ulid, snapshot_hash)
    WHERE status = 'grounded';

-- Rollback:
-- DROP TABLE IF EXISTS adcopy_generation;
