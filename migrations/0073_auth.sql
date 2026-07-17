-- 0073_auth.sql — AUTH-0: unified auth schema.
--
-- Resolution: 00-MASTER.md §2 C-3 ("Cuatro esquemas de auth incompatibles"). Four cartas
-- (03-garage-fleet F1, 05-multiposting F3, 06-unified-crm-chat F1-tenancy, 08-forum-community F1)
-- each independently planned to mint their own auth schema — three of them numbered 0073. This
-- migration is the single fusion the MASTER mandates instead:
--
--   * `app_user`        — base schema = 08's design: roles (dealer/particular/staff), argon2id
--                          password hashing (services/api/auth_security.py), dealer-role claims
--                          verified against the census via services/api/tax_id.py (08 §4.7,
--                          anti dealer-disfrazado).
--   * `dealer_membership` — 03's design: user <-> entity N:M relation for multi-rooftop dealers.
--                          THE TENANT IS THE ENTITY reached via this membership — no separate
--                          `crm_tenant` (06) and no separate `dealer_account` (05) are created;
--                          the MASTER explicitly retires both in favour of this single edge.
--   * `user_session`    — revocable server-side sessions (08's design): opaque token, only its
--                          SHA-256 hash is persisted, never a bare JWT with no revocation path.
--   * `user_notification` — 08's design: notifications to a user. Reuses nothing from `alert`
--                          (migrations/0004_verification_health.sql) because `alert` has no
--                          recipient column — it is pipeline-operational, not user-facing.
--
-- Every carta that still needs auth (03-F1+, 04-F7, 05-F3+, 06-F1+, 08-F1+) CONSUMES this schema
-- in its own fase; none of them mints a second one (MASTER "Reglas operativas" #4).
--
-- Additive, idempotent, reversible.

CREATE TABLE IF NOT EXISTS app_user (
    user_ulid      TEXT PRIMARY KEY,
    email          TEXT NOT NULL,
    -- Generated lower(email) column backs the case-insensitive uniqueness index below —
    -- avoids depending on the citext extension being installed on every environment.
    email_lower    TEXT GENERATED ALWAYS AS (lower(email)) STORED,
    password_hash  TEXT NOT NULL,               -- argon2id, see services/api/auth_security.py
    name           TEXT,
    role           TEXT NOT NULL DEFAULT 'particular'
        CHECK (role IN ('dealer', 'particular', 'staff')),
    status         TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'disabled')),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_app_user_email_lower ON app_user (email_lower);

-- dealer_membership: user <-> entity N:M (03's design). Multi-rooftop = N rows for one user.
-- role_in_entity distinguishes the account that claimed the dealer (owner, verified via
-- tax_id.py at claim time) from staff seats added later by that owner (future carta work).
CREATE TABLE IF NOT EXISTS dealer_membership (
    user_ulid      TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    role_in_entity TEXT NOT NULL DEFAULT 'owner'
        CHECK (role_in_entity IN ('owner', 'staff')),
    verified_at    TIMESTAMPTZ NOT NULL DEFAULT now(),  -- when the tax_id/entity.cif match passed
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_ulid, entity_ulid)
);

CREATE INDEX IF NOT EXISTS idx_dealer_membership_entity ON dealer_membership (entity_ulid);

-- user_session: revocable sessions. Only a SHA-256 hash of the opaque bearer token is stored;
-- the raw token is handed to the client exactly once (register/login/refresh response) and is
-- never logged or persisted. Revocation and expiry are both explicit columns so "is this
-- session still good" is one indexed WHERE clause, never bare JWT trust.
CREATE TABLE IF NOT EXISTS user_session (
    session_ulid  TEXT PRIMARY KEY,
    user_ulid     TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    token_hash    TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at    TIMESTAMPTZ NOT NULL,
    revoked_at    TIMESTAMPTZ,
    last_seen_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_user_session_token_hash ON user_session (token_hash);
CREATE INDEX IF NOT EXISTS idx_user_session_user ON user_session (user_ulid);
-- Fast "is this session still valid" lookups and future expired-row cleanup jobs.
CREATE INDEX IF NOT EXISTS idx_user_session_active
    ON user_session (user_ulid, expires_at) WHERE revoked_at IS NULL;

-- user_notification: notifications addressed to a specific user (08's design). Consumers
-- (e.g. 08-forum-community's wanted_match alerts) are future cartas; this migration only
-- opens the table so they never need a second schema for the same concept.
CREATE TABLE IF NOT EXISTS user_notification (
    notification_ulid TEXT PRIMARY KEY,
    user_ulid         TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    type              TEXT NOT NULL,
    payload           JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    read_at           TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_user_notification_user ON user_notification (user_ulid, read_at);

-- Rollback:
-- DROP TABLE IF EXISTS user_notification;
-- DROP TABLE IF EXISTS user_session;
-- DROP TABLE IF EXISTS dealer_membership;
-- DROP TABLE IF EXISTS app_user;
