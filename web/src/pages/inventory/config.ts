// CARDEEP Inventory — dealer + threshold configuration.
//
// The real API is geo -> entity -> inventory, read-only, with no auth that maps
// a logged-in user to a dealer (see AuthContext DEV_BYPASS). Until that exists,
// this page renders ONE real, verified dealer. Single point of change.
//
// Chosen dealer: GYATA, servicio oficial Ford (Madrid). 468 real available
// vehicles verified live against cardeep-pg on 2026-07-16, single alias
// (n_aliases=1, clean identity — no cross-dealer cluster merge ambiguity),
// 100% photo/price/km/fuel/transmission coverage on the first 200 rows.
export const DEALER_CDP = 'CDP-ES-28-YCZB8JYW'

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
