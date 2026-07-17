-- 0075_lifetime_link.sql — vehicle lifetime re-identification overlay (Pillar 02-history-reports F1).
--
-- Mirrors 0023_vehicle_cluster.sql exactly in structure: a non-destructive overlay that identifies
-- the SAME physical car across SEQUENTIAL episodes (GONE -> reappears weeks/months later, possibly
-- at a different dealer, possibly on a different platform) WITHOUT ever mutating a single row in
-- vehicle or vehicle_event. Every vehicle_ulid survives untouched (PG MVCC doctrine: INSERT new,
-- never UPDATE a row that isn't the write path's own).
--
-- Resolution logic (pipeline/identity/link_lifetimes.py):
--   Primary signal (at least one required): vin_ref exact (pattern-valid 17-char VIN, after
--     trim+uppercase) OR photo_hash exact (excluding high-collision/catalogue hashes, same
--     over-collision guard pattern as 0023's PHOTO_HIGH_COLLISION_K).
--   Corroborating signal (required): the OTHER of the two signals also matching (match_signal=
--     'both') OR firma (make+model+year exact) + temporal order (predecessor's last_seen strictly
--     before successor's first_seen, within a bounded window).
--   Anti-FP hard guards: never link cross-country; never use a predecessor whose 0023 cluster still
--     has an 'available' sibling (the car hasn't actually left the market, just one listing did);
--     a firma mismatch (make/model/year) on an otherwise-matching primary signal REJECTS the edge
--     outright rather than persisting a low-confidence row (mirrors cluster_vehicles.py: rejected
--     candidates are not written, not just hidden).
--
-- vam_verified=FALSE until the Director manually gates it TRUE (same pattern as vehicle_cluster_run,
-- 0023:16/31). Only lifetime_link_run rows with vam_verified=TRUE are exposed by
-- v_vehicle_lifetime — this is the ONLY gate the frontend/API can ever read past (§7 of the pillar
-- letter: "sin 2 señales independientes el eslabón NO se muestra").

-- ---------------------------------------------------------------------------
-- lifetime_link_run: one execution of the lifetime resolver
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lifetime_link_run (
    run_id           TEXT        PRIMARY KEY,               -- caller-supplied id
    run_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolver         TEXT        NOT NULL,                   -- 'sequential-bucket-chain-deterministic'
    resolver_version TEXT,
    scope            TEXT        NOT NULL,                   -- SQL condition used to filter vehicles
    blocking_rules   JSONB,                                  -- audit / reproducibility
    n_in             INTEGER,                                -- vehicles fed to the resolver
    n_chains         INTEGER,                                -- distinct lifetime chains (>=2 episodes)
    n_linked         INTEGER,                                -- edges written (vehicle_ulid pairs)
    vam_verified     BOOLEAN     NOT NULL DEFAULT FALSE,     -- TRUE only after Director VAM gate
    vam_verdict_id   BIGINT      REFERENCES verification_verdict(id),
    notes            TEXT
);

-- ---------------------------------------------------------------------------
-- lifetime_link: one directed edge per (predecessor -> successor) transition.
-- A full lifetime chain of N episodes is N-1 edges, walked at read time by
-- v_vehicle_lifetime / the API — no chain_id is precomputed (mirrors the
-- pillar letter §5: "si el perfil de latencia lo exige, la decisión de
-- cachear se toma en F2 con medición, no ahora").
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lifetime_link (
    run_id            TEXT    NOT NULL
                          REFERENCES lifetime_link_run(run_id) ON DELETE CASCADE,
    vehicle_ulid_from TEXT    NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    vehicle_ulid_to   TEXT    NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    match_signal      TEXT    NOT NULL CHECK (match_signal IN ('vin_ref', 'photo_hash', 'both')),
    match_probability DOUBLE PRECISION,
    evidence          JSONB   NOT NULL,   -- the exact readings that justified the link (C11)
    PRIMARY KEY (run_id, vehicle_ulid_from, vehicle_ulid_to),
    CHECK (vehicle_ulid_from <> vehicle_ulid_to)
);

CREATE INDEX IF NOT EXISTS idx_ll_from ON lifetime_link (run_id, vehicle_ulid_from);
CREATE INDEX IF NOT EXISTS idx_ll_to   ON lifetime_link (run_id, vehicle_ulid_to);
CREATE INDEX IF NOT EXISTS idx_ll_run_sig ON lifetime_link (run_id, match_signal);

-- ---------------------------------------------------------------------------
-- v_vehicle_lifetime: served resolution (most recent vam_verified=TRUE run) —
-- the ONLY read path the API/frontend may use (mirrors v_canonical_vehicle, 0023:57).
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_vehicle_lifetime AS
SELECT
    ll.vehicle_ulid_from,
    ll.vehicle_ulid_to,
    ll.match_signal,
    ll.match_probability,
    ll.evidence,
    ll.run_id
FROM lifetime_link ll
WHERE ll.run_id = (
    SELECT run_id
    FROM lifetime_link_run
    WHERE vam_verified = TRUE
    ORDER BY run_at DESC
    LIMIT 1
);

-- Rollback:
-- DROP VIEW  IF EXISTS v_vehicle_lifetime;
-- DROP TABLE IF EXISTS lifetime_link CASCADE;
-- DROP TABLE IF EXISTS lifetime_link_run CASCADE;
