-- 0076_adaptive_cadence.sql — F4, per-source adaptive change-rate cadence.
-- Additive, idempotent, reversible. (plans/cardeep-omni/00-marketplace-engine.md F4 / §5.3)
--
-- Closes the gap vs. Cho & Garcia-Molina (2003): the static 4-tier harvest_interval_hours
-- (24h/168h/720h/2160h, migration 0021) is a fixed table, blind to how often a source's
-- inventory actually changes. This migration adds the columns the F4 estimator writes:
-- an observed change-rate (lambda, per hour) computed from the source's OWN vehicle_event
-- history (pipeline/ops/cadence_estimator.py), a mode flag for gradual rollout, and the
-- computed interval the estimator derives from lambda. harvest_interval_hours (0021) is
-- NOT removed or renamed — it stays as the floor/ceiling clamp and as the value actually
-- used by _due_sources() for any source still in 'static' mode (the default).

ALTER TABLE source_health
    ADD COLUMN IF NOT EXISTS observed_change_rate DOUBLE PRECISION;

ALTER TABLE source_health
    ADD COLUMN IF NOT EXISTS cadence_mode TEXT NOT NULL DEFAULT 'static'
        CHECK (cadence_mode IN ('static', 'adaptive'));

ALTER TABLE source_health
    ADD COLUMN IF NOT EXISTS computed_interval_hours INTEGER;

ALTER TABLE source_health
    ADD COLUMN IF NOT EXISTS cadence_computed_at TIMESTAMPTZ;

COMMENT ON COLUMN source_health.observed_change_rate IS
    'Cho & Garcia-Molina (2003) MLE estimate of this source''s per-hour inventory change '
    'rate (lambda), from its own vehicle_event history via entity_source. NULL until the '
    'F4 estimator has run at least once for this source (insufficient sample -> stays NULL, '
    'the source keeps using harvest_interval_hours).';

COMMENT ON COLUMN source_health.cadence_mode IS
    'static (default): _due_sources() uses harvest_interval_hours (the 0021 4-tier table), '
    'unchanged pre-F4 behavior. adaptive: _due_sources() uses computed_interval_hours '
    '(clamped to [24, 2160] hours, the same floor/ceiling as the static tiers) instead. '
    'Gradual rollout (F4): flipped source-by-source via scripts/enable_adaptive_cadence.py '
    'after a passing backtest, never a blanket default.';

COMMENT ON COLUMN source_health.computed_interval_hours IS
    'The re-visit interval (hours) derived from observed_change_rate by the F4 estimator, '
    'clamped to [24, 2160] (the same safety floor/ceiling as the static tier table — never '
    'hammer more than hourly-scale, never abandon a source past 90 days). Only consulted '
    'by _due_sources() when cadence_mode=''adaptive''.';

COMMENT ON COLUMN source_health.cadence_computed_at IS
    'When the F4 estimator last recomputed observed_change_rate/computed_interval_hours for '
    'this source — lets an operator see a stale estimate (e.g. the cadence job stopped) '
    'independently of the harvest heartbeat itself (00-marketplace-engine.md §7 two-path '
    'verification discipline).';

-- Rollback:
-- ALTER TABLE source_health DROP COLUMN IF EXISTS cadence_computed_at;
-- ALTER TABLE source_health DROP COLUMN IF EXISTS computed_interval_hours;
-- ALTER TABLE source_health DROP COLUMN IF EXISTS cadence_mode;
-- ALTER TABLE source_health DROP COLUMN IF EXISTS observed_change_rate;
