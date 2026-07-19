-- 0096_app_user_plan.sql — AUTH-0 follow-up: subscription plan column on app_user.
--
-- Why: web/src/lib/entitlements.ts + PremiumGate.tsx already gate 6 UI surfaces (Dashboard
-- sourcing-ranking, Arbitrage sourcing-ranking, Marketing channel-radar, Inteligencia
-- cross-border-compare/market-position-detail/delta-feed-full) on `user.plan` — but no
-- backend column ever existed to hold it. `_serialize_user()` (services/api/routers/auth.py)
-- never returned a `plan` field, so `user?.plan ?? 'starter'` always fell back to the hardcoded
-- default for every single account (verified live 2026-07-19: zero rows anywhere ever set it).
-- The underlying API data behind every one of those gates (arbitrage.py, marketing.py,
-- geo.py) already has NO server-side enforcement — PremiumGate only blurs the DOM client-side
-- — so this column does not introduce a new access-control boundary; it wires up billing-tier
-- UI that was previously permanently unreachable by anyone, real subscription or not.
--
-- Additive, idempotent, reversible.

ALTER TABLE app_user
    ADD COLUMN IF NOT EXISTS plan TEXT NOT NULL DEFAULT 'starter'
        CHECK (plan IN ('starter', 'scale', 'enterprise'));

-- Rollback:
-- ALTER TABLE app_user DROP COLUMN IF EXISTS plan;
