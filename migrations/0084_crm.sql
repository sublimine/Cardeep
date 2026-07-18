-- 0084_crm.sql — 06-unified-crm-chat F1: CRM schema + minimal tenancy.
--
-- Tenancy resolution (00-MASTER.md C-3/C-4): NO crm_tenant/crm_user table — the tenant IS the
-- dealer's `entity_ulid`, reached via AUTH-0's `dealer_membership` (migrations/0073_auth.sql).
-- A CRM row's `entity_ulid` column always points at the CANONICAL entity of a dealer cluster
-- (the same resolution `resolve_cluster()` performs for every other cdp_code-scoped table in
-- this API) — routers enforce that scoping exactly like services/api/routers/dealer_ops.py's
-- `_authorize_vehicle` already does for fleet_ops.
--
-- Ownership: 06-unified-crm-chat.md owns this entire domain (C-4/C-5) — Contacts/Deals/
-- Kanban(deals)/Inbox/Calendar/Notes. 03-garage-fleet's `fleet_ops`/`fleet_ops_event`
-- (migrations/0080_fleet_ops.sql) stay untouched: vehicle OPERATIONAL state is theirs, buyer/lead
-- identity and conversation state is this migration's.
--
-- Design decisions carried from the carta (plans/cardeep-omni/06-unified-crm-chat.md §5):
--   * crm_contact: E.164 phone + lowercased email, both nullable but deduped per-tenant via
--     partial unique indexes (Chatwoot/MDM survivorship pattern — phone_raw preserves what was
--     typed, phone_e164 is what's ever compared/rendered).
--   * crm_contact_channel: Chatwoot's ContactInbox pattern — ties ONE channel identity (email
--     address, phone number, form submission id) to ONE contact; unique per (tenant, channel,
--     source_id) so the same human across email AND WhatsApp is one Contact, two channel rows.
--   * crm_consent: append-only ledger (transactional vs marketing, granted vs revoked) — the
--     LSSI-CE/LOPDGDD control; current state = latest row per (contact, channel, purpose).
--   * crm_conversation/crm_message: Twilio's "conversation is the thread, channel per participant"
--     model. `assignee_user_ulid` exists NOW (nullable, unused until a future carta) so multi-agent
--     assignment never needs a destructive migration later (carta §3, explicit decision).
--   * crm_deal/crm_deal_stage_event: Salesforce Amount×Probability model + Kanban University's
--     lead/cycle-time measurement via an append-only stage-change ledger (same pattern as
--     vehicle_event / fleet_ops_event — the repo's established append-only-ledger-plus-current-
--     state-row doctrine).
--   * crm_note/crm_event: replace Notes.tsx's localStorage and Calendar.tsx's MOCK_EVENTS with
--     real per-tenant persistence (F6 wires these; the tables land now so F1 is the only schema
--     migration this pilar needs).
--   * crm_template: response templates; `meta_approved` reserved for F7 (WhatsApp Business,
--     gated fase de gasto) — column exists now, unused until F7, to avoid a later migration.
--
-- Additive, idempotent, reversible. migrate.py applies only the forward section (strip_rollback).

-- ---------------------------------------------------------------------------
-- Enums (0005_types_and_guards.sql pattern: DO-block guarded by duplicate_object exception)
-- ---------------------------------------------------------------------------

DO $$ BEGIN
  CREATE TYPE crm_channel AS ENUM ('email', 'whatsapp', 'web_form', 'phone', 'walk_in');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE crm_conversation_status AS ENUM ('open', 'replied', 'closed', 'spam');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE crm_message_direction AS ENUM ('inbound', 'outbound');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Matches web/src/types.ts::Deal['stage'] exactly (frontend contract predates this schema).
DO $$ BEGIN
  CREATE TYPE crm_deal_stage AS ENUM ('lead', 'contacted', 'offer', 'negotiation', 'won', 'lost');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE crm_consent_purpose AS ENUM ('transactional', 'marketing');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE crm_consent_status AS ENUM ('granted', 'revoked');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Matches web/src/types.ts::Activity['type'] exactly.
DO $$ BEGIN
  CREATE TYPE crm_activity_type AS ENUM ('inquiry', 'reply', 'reminder', 'note', 'visit', 'call');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE crm_priority AS ENUM ('low', 'medium', 'high');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Matches web/src/pages/Calendar.tsx's CalEvent['type'] exactly.
DO $$ BEGIN
  CREATE TYPE crm_event_type AS ENUM ('visit', 'call', 'reminder', 'delivery');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Matches web/src/pages/Notes.tsx's NoteColor exactly.
DO $$ BEGIN
  CREATE TYPE crm_note_color AS ENUM ('neutral', 'amber', 'sky', 'emerald', 'rose');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---------------------------------------------------------------------------
-- crm_contact — the buyer/lead identity root
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_contact (
    contact_ulid   TEXT PRIMARY KEY,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid),
    name           TEXT NOT NULL DEFAULT '',
    email          TEXT,
    email_lower    TEXT GENERATED ALWAYS AS (lower(email)) STORED,
    phone_raw      TEXT,
    phone_e164     TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_contact_entity ON crm_contact (entity_ulid);

-- Dedup: same tenant + same normalized phone/email = same physical person (E.164 + MDM
-- survivorship pattern, carta §4 "posible duplicado"). Partial (nullable columns) so contacts
-- without a captured phone/email don't collide on NULL=NULL (PG treats NULLs as distinct in a
-- unique index by default, but the WHERE clause makes the intent explicit and matches the
-- repo's own partial-index idiom, e.g. crm_contact_channel below).
CREATE UNIQUE INDEX IF NOT EXISTS uq_crm_contact_phone
    ON crm_contact (entity_ulid, phone_e164) WHERE phone_e164 IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_crm_contact_email
    ON crm_contact (entity_ulid, email_lower) WHERE email_lower IS NOT NULL;

-- ---------------------------------------------------------------------------
-- crm_contact_channel — Chatwoot's ContactInbox pattern: ties ONE channel identity to
-- ONE contact. A contact reachable by email AND WhatsApp has two rows here, one Contact.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_contact_channel (
    channel_ulid   TEXT PRIMARY KEY,
    contact_ulid   TEXT NOT NULL REFERENCES crm_contact(contact_ulid) ON DELETE CASCADE,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid),
    channel        crm_channel NOT NULL,
    source_id      TEXT NOT NULL,   -- email address / phone in E.164 / form submission key
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (entity_ulid, channel, source_id)
);

CREATE INDEX IF NOT EXISTS idx_crm_contact_channel_contact ON crm_contact_channel (contact_ulid);

-- ---------------------------------------------------------------------------
-- crm_consent — append-only ledger; current state = latest row per (contact, channel, purpose)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_consent (
    consent_ulid   TEXT PRIMARY KEY,
    contact_ulid   TEXT NOT NULL REFERENCES crm_contact(contact_ulid) ON DELETE CASCADE,
    channel        crm_channel NOT NULL,
    purpose        crm_consent_purpose NOT NULL,
    status         crm_consent_status NOT NULL,
    source         TEXT,            -- e.g. 'web_form', 'verbal_recorded', 'reply_stop'
    occurred_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_consent_contact ON crm_consent (contact_ulid, channel, purpose, occurred_at DESC);

-- ---------------------------------------------------------------------------
-- crm_template — response templates; meta_approved reserved for F7 (WhatsApp, gated)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_template (
    template_ulid  TEXT PRIMARY KEY,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid),
    name           TEXT NOT NULL,
    language       TEXT NOT NULL DEFAULT 'es',
    subject        TEXT,
    body           TEXT NOT NULL,
    is_system      BOOLEAN NOT NULL DEFAULT FALSE,
    meta_approved  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_template_entity ON crm_template (entity_ulid);

-- ---------------------------------------------------------------------------
-- crm_deal — Salesforce Amount x Probability model
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_deal (
    deal_ulid      TEXT PRIMARY KEY,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid),
    contact_ulid   TEXT NOT NULL REFERENCES crm_contact(contact_ulid),
    vehicle_ulid   TEXT REFERENCES vehicle(vehicle_ulid),
    stage          crm_deal_stage NOT NULL DEFAULT 'lead',
    amount         NUMERIC(12, 2),
    probability    NUMERIC(5, 2),      -- 0..100; app sets stage defaults, editable per-deal (carta §4)
    assignee_user_ulid TEXT REFERENCES app_user(user_ulid),
    priority       crm_priority,
    won_at         TIMESTAMPTZ,
    lost_at        TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_deal_entity_stage ON crm_deal (entity_ulid, stage);
CREATE INDEX IF NOT EXISTS idx_crm_deal_contact ON crm_deal (contact_ulid);
CREATE INDEX IF NOT EXISTS idx_crm_deal_vehicle ON crm_deal (vehicle_ulid) WHERE vehicle_ulid IS NOT NULL;

-- ---------------------------------------------------------------------------
-- crm_deal_stage_event — append-only; same doctrine as vehicle_event/fleet_ops_event.
-- Lead time / cycle time (Kanban University rule 5) is derived from this ledger.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_deal_stage_event (
    event_ulid     TEXT PRIMARY KEY,
    deal_ulid      TEXT NOT NULL REFERENCES crm_deal(deal_ulid) ON DELETE CASCADE,
    from_stage     crm_deal_stage,
    to_stage       crm_deal_stage NOT NULL,
    actor_user_ulid TEXT REFERENCES app_user(user_ulid),
    changed_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_deal_stage_event_deal ON crm_deal_stage_event (deal_ulid, changed_at);

-- ---------------------------------------------------------------------------
-- crm_conversation — Twilio's "thread is the resource" model. vehicle_ulid/deal_ulid
-- nullable — F5 (census cross-reference) populates vehicle_ulid once a lead's car is resolved.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_conversation (
    conversation_ulid TEXT PRIMARY KEY,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid),
    contact_ulid   TEXT NOT NULL REFERENCES crm_contact(contact_ulid),
    channel        crm_channel NOT NULL,
    vehicle_ulid   TEXT REFERENCES vehicle(vehicle_ulid),
    deal_ulid      TEXT REFERENCES crm_deal(deal_ulid),
    source_platform TEXT,            -- origin AD platform (coches.net/wallapop/manual), NOT the comm channel
    subject        TEXT,
    status         crm_conversation_status NOT NULL DEFAULT 'open',
    -- Reserved for future multi-agent assignment (carta §3, deliberately unused today — exists
    -- now so it never requires a destructive migration later).
    assignee_user_ulid TEXT REFERENCES app_user(user_ulid),
    last_inbound_at TIMESTAMPTZ,      -- WhatsApp 24h window base (F7); also drives SLA badge (F4)
    last_message_at TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_conversation_entity_status ON crm_conversation (entity_ulid, status, last_message_at DESC);
CREATE INDEX IF NOT EXISTS idx_crm_conversation_contact ON crm_conversation (contact_ulid);
CREATE INDEX IF NOT EXISTS idx_crm_conversation_vehicle ON crm_conversation (vehicle_ulid) WHERE vehicle_ulid IS NOT NULL;

-- ---------------------------------------------------------------------------
-- crm_message — one row per message, native per-channel (Twilio Participant-centric model).
-- provider_message_id: RFC 5322 Message-ID (email) for idempotent IMAP re-ingestion and for the
-- "Enviado check" only paints after a real provider ACK (carta §7 protocol; never a bare 200).
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_message (
    message_ulid   TEXT PRIMARY KEY,
    conversation_ulid TEXT NOT NULL REFERENCES crm_conversation(conversation_ulid) ON DELETE CASCADE,
    direction      crm_message_direction NOT NULL,
    sender_name    TEXT,
    sender_email   TEXT,
    body           TEXT NOT NULL,
    template_ulid  TEXT REFERENCES crm_template(template_ulid),
    sent_via       crm_channel NOT NULL,
    provider_message_id TEXT,        -- email Message-ID; unique globally when present (dedup)
    provider_ack_at TIMESTAMPTZ,     -- populated only on real SMTP/provider confirmation
    read_at        TIMESTAMPTZ,
    sent_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_message_conversation ON crm_message (conversation_ulid, sent_at);
CREATE UNIQUE INDEX IF NOT EXISTS uq_crm_message_provider_id
    ON crm_message (provider_message_id) WHERE provider_message_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- crm_activity — calls/visits/reminders/notes tied to a contact or a deal
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_activity (
    activity_ulid  TEXT PRIMARY KEY,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid),
    contact_ulid   TEXT REFERENCES crm_contact(contact_ulid) ON DELETE CASCADE,
    deal_ulid      TEXT REFERENCES crm_deal(deal_ulid) ON DELETE CASCADE,
    type           crm_activity_type NOT NULL,
    body           TEXT NOT NULL,
    actor_user_ulid TEXT REFERENCES app_user(user_ulid),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_activity_contact ON crm_activity (contact_ulid, created_at DESC) WHERE contact_ulid IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_crm_activity_deal ON crm_activity (deal_ulid, created_at DESC) WHERE deal_ulid IS NOT NULL;

-- ---------------------------------------------------------------------------
-- crm_note — replaces Notes.tsx's localStorage (F6)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_note (
    note_ulid      TEXT PRIMARY KEY,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid),
    author_user_ulid TEXT REFERENCES app_user(user_ulid),
    title          TEXT NOT NULL DEFAULT '',
    body           TEXT NOT NULL DEFAULT '',
    color          crm_note_color NOT NULL DEFAULT 'neutral',
    pinned         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_note_entity ON crm_note (entity_ulid, pinned DESC, updated_at DESC);

-- ---------------------------------------------------------------------------
-- crm_event — replaces Calendar.tsx's MOCK_EVENTS (F6); export target for RFC 5545 .ics
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_event (
    event_ulid     TEXT PRIMARY KEY,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid),
    title          TEXT NOT NULL,
    starts_at      TIMESTAMPTZ NOT NULL,
    ends_at        TIMESTAMPTZ,
    event_type     crm_event_type NOT NULL DEFAULT 'visit',
    location       TEXT,
    contact_ulid   TEXT REFERENCES crm_contact(contact_ulid),
    deal_ulid      TEXT REFERENCES crm_deal(deal_ulid),
    created_by_user_ulid TEXT REFERENCES app_user(user_ulid),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_event_entity_starts ON crm_event (entity_ulid, starts_at);

-- ---------------------------------------------------------------------------
-- Append-only guards (0005/0035 pattern: cardeep_block_mutation() blocks ALL UPDATE/DELETE)
-- ---------------------------------------------------------------------------

DROP TRIGGER IF EXISTS trg_crm_consent_noupd ON crm_consent;
CREATE TRIGGER trg_crm_consent_noupd
  BEFORE UPDATE OR DELETE ON crm_consent
  FOR EACH ROW EXECUTE FUNCTION cardeep_block_mutation();

DROP TRIGGER IF EXISTS trg_crm_deal_stage_event_noupd ON crm_deal_stage_event;
CREATE TRIGGER trg_crm_deal_stage_event_noupd
  BEFORE UPDATE OR DELETE ON crm_deal_stage_event
  FOR EACH ROW EXECUTE FUNCTION cardeep_block_mutation();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_crm_deal_stage_event_noupd ON crm_deal_stage_event;
-- DROP TRIGGER IF EXISTS trg_crm_consent_noupd ON crm_consent;
-- DROP TABLE IF EXISTS crm_event;
-- DROP TABLE IF EXISTS crm_note;
-- DROP TABLE IF EXISTS crm_activity;
-- DROP TABLE IF EXISTS crm_message;
-- DROP TABLE IF EXISTS crm_conversation;
-- DROP TABLE IF EXISTS crm_deal_stage_event;
-- DROP TABLE IF EXISTS crm_deal;
-- DROP TABLE IF EXISTS crm_template;
-- DROP TABLE IF EXISTS crm_consent;
-- DROP TABLE IF EXISTS crm_contact_channel;
-- DROP TABLE IF EXISTS crm_contact;
-- DROP TYPE IF EXISTS crm_note_color;
-- DROP TYPE IF EXISTS crm_event_type;
-- DROP TYPE IF EXISTS crm_priority;
-- DROP TYPE IF EXISTS crm_activity_type;
-- DROP TYPE IF EXISTS crm_consent_status;
-- DROP TYPE IF EXISTS crm_consent_purpose;
-- DROP TYPE IF EXISTS crm_deal_stage;
-- DROP TYPE IF EXISTS crm_message_direction;
-- DROP TYPE IF EXISTS crm_conversation_status;
-- DROP TYPE IF EXISTS crm_channel;
