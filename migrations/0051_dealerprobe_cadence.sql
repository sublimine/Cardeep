-- 0051_dealerprobe_cadence.sql — tune dealerprobe_ownsite to a daily drain cadence.
--
-- dealerprobe_ownsite is now scheduler-mapped (pipeline/ops/scheduler.py REGISTRY, --from-db drain).
-- Its source_health row was created by the connector's first record_run with the COALESCE default
-- of 168 h (weekly). With a real backlog of dealers-with-website-not-yet-probed, a weekly cadence
-- drains it in ~weeks; a daily (24 h) cadence drains it in ~days, then idles near zero (only newly
-- DISCOVERED dealers reappear, since the monotonic dealerprobe_probed marker excludes probed ones).
-- Ban-safe: own-site probing is spread across thousands of distinct dealer hosts (no single-host
-- hammering, no AS24-style scar), so daily is gentle. silence_watchdog at 24 h alerts only after a
-- 48 h gap, which a healthy daily run never reaches.
--
-- GUARDED + idempotent: only flips the row that is still on the 168 h default, so it never clobbers
-- a future manual/operator cadence tune and re-running is a no-op (the WHERE matches nothing once
-- already 24). Does NOT create the row (the connector/REGISTRY own its existence).

UPDATE source_health
   SET harvest_interval_hours = 24
 WHERE source_key = 'dealerprobe_ownsite'
   AND harvest_interval_hours = 168;

-- Rollback:
-- UPDATE source_health
--    SET harvest_interval_hours = 168
--  WHERE source_key = 'dealerprobe_ownsite'
--    AND harvest_interval_hours = 24;
