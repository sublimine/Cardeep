-- 0039_schedule_segments_as24.sql — seed source_health so the durable scheduler can pick up two
-- newly-registered sources on their FIRST tick (audit P2 C-cochesnet-segments + C-as24-unscheduled).
--
-- _due_sources reads source_health; a key with no row is invisible to the scheduler, and a key not in
-- REGISTRY is skipped — so a source needs BOTH a seeded row AND a REGISTRY entry (added in scheduler.py).
-- This is the autocasion-orphan lesson: a new source_key has no source_health row, so the scheduler
-- cannot launch it the first time without one.
--
-- WATCHDOG-SAFE SEED (reviewer-mandated): last_fail is seeded to a past sentinel that is OLDER than
-- harvest_interval_hours (so the row is immediately DUE) but NEWER than 2*harvest_interval_hours (so
-- silence_watchdog — which flags now()-COALESCE(last_ok,last_fail,epoch) > 2*interval — does NOT raise a
-- false :silence alert on the NULL/NULL state; a successful :scrape run would NOT clear a :silence alert).
-- status='unknown' + consecutive_fails=0 keep the breaker CLOSED so _due_sources won't skip.
-- ON CONFLICT DO NOTHING: idempotent; never reverts a live cadence row.

INSERT INTO source_health (source_key, is_tier1, harvest_interval_hours, status,
                           consecutive_fails, last_ok, last_fail)
VALUES ('coches_net_segments', FALSE, 24, 'unknown', 0, NULL, now() - interval '25 hours')
ON CONFLICT (source_key) DO NOTHING;

INSERT INTO source_health (source_key, is_tier1, harvest_interval_hours, status,
                           consecutive_fails, last_ok, last_fail)
VALUES ('as24_wholesale', FALSE, 168, 'unknown', 0, NULL, now() - interval '169 hours')
ON CONFLICT (source_key) DO NOTHING;

-- Rollback:
-- DELETE FROM source_health
--  WHERE source_key IN ('coches_net_segments','as24_wholesale')
--    AND last_ok IS NULL AND status='unknown' AND consecutive_fails=0;
