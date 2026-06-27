-- 0062_cdp_check_country_generic.sql -- generalise the two cdp_code CHECKs that
-- migration 0033 baked to Spain, so a SECOND country's eviction can persist.
--
-- THE BUG (red-team, verified live on the :5434 dry-run @ 0061):
--   migrations/0033_evict.sql shipped capacity_ledger and audit_eviction with a
--   cdp_code CHECK hard-coded to ES + a 2-DIGIT-NUMERIC province:
--       CHECK (cdp_code ~ '^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$')
--   pipeline/evict.py writes ONE row into each of these ledgers inside the single
--   eviction transaction (audit_eviction + capacity_ledger, see test_evict.py
--   TestEvictApply). For any country #2 dealer the minted cdp_code is e.g.
--   'CDP-DE-091-AB23CDEF' (country 'DE', German Kreis-width province '091') or
--   'CDP-FR-2A-CDEFGHJK' (Corsica's alphanumeric department '2A'). Both FAIL the
--   ES-baked regex -> the ledger INSERT is rejected -> the eviction transaction
--   ABORTS for the whole country #2. Proven live: both INSERTs raise
--   "violates check constraint ..._cdp_code_check"; the ES control row inserts.
--
-- THE GENERALISED PATTERN (mirror of the served-identity validator, justified by the
-- REAL code shape, NOT invented):
--       ^CDP-[A-Z]{2}-[0-9A-Z]{2,8}-[0-9A-HJKMNP-TV-Z]{8}$
--   How a cdp_code is actually formed -- services/api/codes.py::mint_code (the ONE
--   home of the prefix literal):
--       f"CDP-{country_code}-{province_code}-{_base32(digest)}"
--   * country_code : ISO-3166 alpha-2 -> '[A-Z]{2}'. This is the exact country
--     generalisation pipeline/complete.py::_CDP_CODE_RE adopted in commit 052fa8f
--     ('^CDP-[A-Z]{2}-...'), replacing the country-blind '^CDP-ES-'.
--   * province_code : LITERALLY geo_province.code. Migration 0059 widened that column
--     from the ES-sized CHAR(2) to VARCHAR(8) precisely so real non-ES sub-national
--     codes fit -- its own width justification: "FR DOM 3-digit, German Kreis AGS
--     5-digit, NUTS-2/3 up to 5 alphanumeric (e.g. 'ITI43') -- 8 is a safe ceiling".
--     The province segment is therefore ALPHANUMERIC and 2..8 wide, NOT numeric-2:
--       - lower bound 2 : mirrors complete.py's province group and ES's invariable
--                         2-char grid (01-52, plus the national '00' sentinel);
--       - upper bound 8 : mirrors 0059's VARCHAR(8) ceiling exactly;
--       - charset [0-9A-Z] : mirrors complete.py's uppercase-alphanumeric province
--                         class (Corsica '2A'/'2B', Italy 'RM'/'MI', NUTS 'ITI43').
--     (complete.py pins the province to exactly {2} because its synthetic goldens reuse
--     2-char provinces; the SCHEMA CHECK must instead admit every width mint_code can
--     emit over the 0059 backbone, so it uses {2,8}. Both share the country [A-Z]{2}
--     generalisation and the [0-9A-Z] charset -- the surface that was actually baked.)
--   * _base32(digest) : EXACTLY 8 Crockford-base32 chars; codes.py::_CROCKFORD =
--     "0123456789ABCDEFGHJKMNPQRSTVWXYZ" (no I, L, O, U) == regex class
--     '[0-9A-HJKMNP-TV-Z]'. Preserved BYTE-IDENTICAL from 0033.
--
-- ES IS A STRICT SUBSET -> ZERO REGRESSION: every string the old regex accepted, the
-- new one also accepts (country 'ES' in [A-Z]{2}; province [0-9]{2} in [0-9A-Z]{2,8};
-- suffix identical). So no existing row can be invalidated and ES behaviour is
-- byte-identical -- the constraint only WIDENS to admit country #2. The ADD CONSTRAINT
-- therefore re-validates every existing row trivially (the ledgers are small append-only
-- eviction logs), so no NOT VALID is needed.
--
-- SCOPE -- EXHAUSTIVE SWEEP (migrations/ grep + live pg_constraint scan of the whole
-- schema, 2026-06-27): these TWO are the ONLY cdp_code-shaped CHECK constraints in the
-- entire schema. The other regex CHECKs are country-agnostic ULID shapes
-- (entity_ulid_shape / org_ulid, 0006/0007: '^[0-9A-HJKMNP-TV-Z]{26}$') and the geo
-- province/municipality prefix CHECKs (0001/0053) which 0053 ALREADY country-guarded
-- ("country_code <> 'ES' OR left(code,2)=province_code"). No other CHECK bakes a country
-- or a numeric-2 province into a cdp_code pattern.
--
-- ADDITIVE · IDEMPOTENT (DROP ... IF EXISTS + ADD) · REVERSIBLE. No BEGIN/COMMIT here --
-- scripts/migrate.py wraps the whole file in one transaction (the 0052/0053/0059
-- convention). Constraint names are preserved so the rollback restores 0033 verbatim.

ALTER TABLE capacity_ledger DROP CONSTRAINT IF EXISTS capacity_ledger_cdp_code_check;
ALTER TABLE capacity_ledger ADD  CONSTRAINT capacity_ledger_cdp_code_check
    CHECK (cdp_code ~ '^CDP-[A-Z]{2}-[0-9A-Z]{2,8}-[0-9A-HJKMNP-TV-Z]{8}$');

ALTER TABLE audit_eviction DROP CONSTRAINT IF EXISTS audit_eviction_cdp_code_check;
ALTER TABLE audit_eviction ADD  CONSTRAINT audit_eviction_cdp_code_check
    CHECK (cdp_code ~ '^CDP-[A-Z]{2}-[0-9A-Z]{2,8}-[0-9A-HJKMNP-TV-Z]{8}$');

-- Rollback (restores the ES-baked 0033 constraints verbatim):
-- ALTER TABLE capacity_ledger DROP CONSTRAINT IF EXISTS capacity_ledger_cdp_code_check;
-- ALTER TABLE capacity_ledger ADD  CONSTRAINT capacity_ledger_cdp_code_check
--     CHECK (cdp_code ~ '^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$');
-- ALTER TABLE audit_eviction DROP CONSTRAINT IF EXISTS audit_eviction_cdp_code_check;
-- ALTER TABLE audit_eviction ADD  CONSTRAINT audit_eviction_cdp_code_check
--     CHECK (cdp_code ~ '^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$');
