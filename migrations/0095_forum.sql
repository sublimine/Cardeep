-- 0095_forum.sql — 08-forum-community F4: the conversation layer (PRIORITY 2, carta §3),
-- built on top of the "Se busca" board's infra (auth, geo, votes-as-reputation-source).
--
-- Six tables (carta §5.2):
--   forum_thread     — the hilo. thread_type='price_check' is Edmunds' "Values & Prices Paid"
--                       pattern (§2.5): a first-class thread type whose anchor is obligatory
--                       (enforced at the router, not the DB — a post-insert-time rule, same
--                       as the rest of this migration's polymorphic anchors).
--   forum_post       — hilo body IS its first post (is_first_post=TRUE), replies follow.
--   post_anchor      — polymorphic anchor (vehicle/entity/province) + JSONB snapshot at anchor
--                       time (carta §7.5 drift detection: "el autor citó X; hoy Y").
--   post_vote        — one vote per (post, user), +-1, UNIQUE — changing a vote UPDATEs this
--                       row; the ledger below is a SEPARATE append-only record of the
--                       REPUTATION consequence, never conflated with the vote itself.
--   reputation_event — append-only ledger (same doctrine as vehicle_event/fleet_ops_event:
--                       "NEVER updated or deleted"). `related_user_ulid` is who CAUSED the
--                       delta (the voter, for vote-driven events) — needed for the anti-
--                       inflado dedup window (carta §4.5, eBay-exact: same voter->author pair
--                       counts once per 7 days for REPUTATION, even though the vote itself
--                       always counts for the post's own ranking, carta §7.4 invariant).
--   moderation_flag  — flag queue; UNIQUE(post, flagger) so the SAME flagger cannot inflate
--                       the (deliberately unpublished, carta §4.5 Craigslist-exact) hide
--                       threshold by flagging twice.
--
-- Reuses AUTH-0 (app_user) and geo_province — no second schema of either (00-MASTER.md
-- "Reglas operativas" #4). `source_wanted_ulid` on reputation_event closes the loop with
-- 08's OWN F2: "+15 petición cerrada como comprado vía match" is how the very first users
-- ever cross the votar >= rep 10 threshold before a single forum vote has been cast — the
-- carta's own "tablón antes que foro" order (§9) is the bootstrap mechanism for this exact
-- cold-start problem, not a coincidence.
--
-- Additive, idempotent, reversible.

CREATE TABLE IF NOT EXISTS forum_thread (
    thread_ulid      TEXT PRIMARY KEY,
    author_user_ulid TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    title            TEXT NOT NULL,
    country_code     CHAR(2) NOT NULL DEFAULT 'ES',
    province_code    VARCHAR(8),
    thread_type      TEXT NOT NULL DEFAULT 'discussion'
        CHECK (thread_type IN ('discussion', 'price_check')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_reply_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    reply_count      INT NOT NULL DEFAULT 0,
    FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code)
);

CREATE INDEX IF NOT EXISTS idx_forum_thread_last_reply ON forum_thread (last_reply_at DESC);
CREATE INDEX IF NOT EXISTS idx_forum_thread_province ON forum_thread (country_code, province_code);
CREATE INDEX IF NOT EXISTS idx_forum_thread_author ON forum_thread (author_user_ulid);

CREATE TABLE IF NOT EXISTS forum_post (
    post_ulid        TEXT PRIMARY KEY,
    thread_ulid      TEXT NOT NULL REFERENCES forum_thread(thread_ulid) ON DELETE CASCADE,
    author_user_ulid TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    body             TEXT NOT NULL,
    is_first_post    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_forum_post_thread ON forum_post (thread_ulid, created_at);
CREATE INDEX IF NOT EXISTS idx_forum_post_author ON forum_post (author_user_ulid);

CREATE TABLE IF NOT EXISTS post_anchor (
    anchor_ulid   TEXT PRIMARY KEY,
    post_ulid     TEXT NOT NULL REFERENCES forum_post(post_ulid) ON DELETE CASCADE,
    anchor_type   TEXT NOT NULL CHECK (anchor_type IN ('vehicle', 'entity', 'province')),
    anchor_ref    TEXT NOT NULL,  -- vehicle_ulid | cdp_code | province_code (polymorphic —
                                  -- existence verified at render time, carta §4.2, not by FK)
    snapshot      JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_post_anchor_post ON post_anchor (post_ulid);
CREATE INDEX IF NOT EXISTS idx_post_anchor_ref ON post_anchor (anchor_type, anchor_ref);

CREATE TABLE IF NOT EXISTS post_vote (
    post_ulid   TEXT NOT NULL REFERENCES forum_post(post_ulid) ON DELETE CASCADE,
    user_ulid   TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    value       SMALLINT NOT NULL CHECK (value IN (-1, 1)),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (post_ulid, user_ulid)
);

CREATE INDEX IF NOT EXISTS idx_post_vote_post ON post_vote (post_ulid);

CREATE TABLE IF NOT EXISTS reputation_event (
    event_ulid         TEXT PRIMARY KEY,
    user_ulid          TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    delta              INT NOT NULL,
    reason             TEXT NOT NULL CHECK (reason IN (
        'upvote_anchor', 'upvote_no_anchor', 'wanted_closed_bought',
        'downvote_received', 'downvote_cast', 'staff_grant'
    )),
    related_user_ulid  TEXT REFERENCES app_user(user_ulid) ON DELETE SET NULL,
    source_post_ulid    TEXT REFERENCES forum_post(post_ulid) ON DELETE SET NULL,
    source_wanted_ulid  TEXT REFERENCES wanted_listing(wanted_ulid) ON DELETE SET NULL,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reputation_event_user ON reputation_event (user_ulid, created_at);
-- Anti-inflado dedup lookup (carta §4.5, eBay-exact 7-day same-pair window):
CREATE INDEX IF NOT EXISTS idx_reputation_event_pair
    ON reputation_event (user_ulid, related_user_ulid, created_at)
    WHERE related_user_ulid IS NOT NULL;

CREATE TABLE IF NOT EXISTS moderation_flag (
    flag_ulid             TEXT PRIMARY KEY,
    post_ulid             TEXT NOT NULL REFERENCES forum_post(post_ulid) ON DELETE CASCADE,
    flagger_user_ulid     TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    reason                TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at           TIMESTAMPTZ,
    resolved_by_user_ulid TEXT REFERENCES app_user(user_ulid),
    resolution            TEXT CHECK (resolution IN ('removed', 'dismissed')),
    UNIQUE (post_ulid, flagger_user_ulid)
);

CREATE INDEX IF NOT EXISTS idx_moderation_flag_pending
    ON moderation_flag (created_at) WHERE resolved_at IS NULL;

-- Rollback:
-- DROP TABLE IF EXISTS moderation_flag;
-- DROP TABLE IF EXISTS reputation_event;
-- DROP TABLE IF EXISTS post_vote;
-- DROP TABLE IF EXISTS post_anchor;
-- DROP TABLE IF EXISTS forum_post;
-- DROP TABLE IF EXISTS forum_thread;
