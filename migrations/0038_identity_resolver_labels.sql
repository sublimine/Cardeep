-- 0038_identity_resolver_labels.sql — in-schema authority labels for the dealer-identity resolvers
-- (audit P2 B-beta-resolver-dormant; see docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md).
--
-- Resolves the "ambiguous authority / two parallel resolvers" finding at the schema level: anyone
-- inspecting the DB now sees which view is served and which is the deferred β composition. Comments
-- only — no structural change. Additive, idempotent, reversible.

COMMENT ON VIEW v_dealer_resolved IS
  'AUTHORITATIVE served dealer-identity resolver: B1 (v_canonical) composed with canonical_dedup, both vam_verified. Consumed by resolve_cluster + all entity/inventory endpoints. See docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md';

COMMENT ON VIEW v_resolved_dealer IS
  'BETA fingerprint resolution (entity_resolution run, vam_verified) — COMPUTED BUT NOT SERVED (0 code consumers). Composing it into v_dealer_resolved is a deferred union-find rebuild (audit P2 B-beta-resolver). Do NOT wire into any serving path; use v_dealer_resolved. See ADR 11.';

-- Rollback:
-- COMMENT ON VIEW v_dealer_resolved IS NULL;
-- COMMENT ON VIEW v_resolved_dealer IS NULL;
