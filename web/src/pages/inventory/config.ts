// CARDEEP Inventory — dealer + threshold configuration.
//
// 03-garage-fleet F1: the hardcoded DEALER_CDP constant that used to live here is
// GONE. AUTH-0 (migrations/0073_auth.sql + services/api/routers/auth.py) is the
// real mechanism that maps a logged-in user to a dealer: session -> app_user ->
// dealer_membership -> entity.cdp_code, surfaced on the frontend as
// `useAuthContext().user.tenantId`. Every page in this directory now takes `cdp`
// as an explicit parameter/prop sourced from that session tenant, never from a
// module-level constant — see `pages/inventory/index.tsx`.
//
// GYATA, servicio oficial Ford (Madrid, CDP-ES-28-YCZB8JYW) remains the seeded
// DEMO dealer account (scripts/seed_demo_dealer.py) — 468 real available
// vehicles verified live against cardeep-pg on 2026-07-16, single alias
// (n_aliases=1, clean identity), 100% photo/price/km/fuel/transmission coverage
// on the first 200 rows. It is seeded directly (GYATA has no `cif` on record —
// verified live: `entity.cif` is empty for this row — so the real
// POST /auth/claim-dealer self-service path, which requires a checksum-valid
// tax ID matching the census record, is not usable for this specific entity;
// the seed script documents this honestly rather than faking a claim).

// Pagination — /entities/{cdp}/inventory allows size<=200; 468 vehicles fit in
// 3 requests, comfortably inside the endpoint's 30/min rate limit.
export const PAGE_SIZE = 200

// "Days in stock" thresholds — computed from the real `first_seen` field
// (first time CARDEEP detected the listing), the only honest proxy available.
export const FRESH_DAYS = 7
export const STALE_DAYS = 90

// Real-photo overlay budget for the 3D garage.
//
// IMPORTANT — verified 2026-07-16: the real vehicle photo CDNs (wallapop
// CloudFront, autocasion) do NOT send Access-Control-Allow-Origin headers
// (checked with curl -I against live URLs from the GYATA inventory). A plain
// <img> displays them fine, but `fetch()` + `createImageBitmap()` into a
// WebGL texture is blocked by the browser's CORS policy — that would make
// every 3D card silently fall back to a placeholder, defeating the whole
// point of a photo-real garage. So the garage does NOT texture-map photos
// onto meshes. Instead, every card is a cheap WebGL placeholder mesh, and a
// bounded number of the cards nearest the camera (+ hovered/selected) get a
// real <img> promoted via drei's <Html transform> — true DOM photos
// billboarded in 3D space, no CORS restriction, and sharper than a
// downscaled texture would have been anyway.
export const PHOTO_OVERLAY_BUDGET = 24

// Progressive reveal batch size for the dense table view.
export const ROW_BATCH = 60

// Framer Motion stagger is capped at this many items — beyond it the linear
// per-item delay would make the entrance animation take longer than a user's
// patience (24 items * 0.03s = 0.72s, a reasonable cascade).
export const STAGGER_CAP = 24
