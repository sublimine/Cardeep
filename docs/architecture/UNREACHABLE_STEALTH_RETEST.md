# 'Unreachable' long-tail — stealth-browser re-test (2026-06-13)

The 92 `family=unreachable` long-tail domains (`docs/_longtail_fingerprints.json`,
`family=='unreachable'`) were declared dead/walled by a curl_cffi + status-checking
basic-browser probe. Per owner mandate (the subastas/Autorola/BCA case proved non-JS
verdicts can lie), every domain was RE-TESTED with a real JS **stealth browser**
(camoufox 135, anti-detect Firefox, humanised fingerprint, ES locale) on a
**status-blind rendered-body gate**: full headers, JS settle, cookie-accept, and a
canonical Spanish used-car **listing-path sweep**.

- Harness: `scripts/unreachable_stealth_reprobe.py` (crash-resumable, per-domain flush)
- Evidence: `docs/_unreachable_stealth_result.json` (per-domain bucket + swept detail)
- DB tally: `scripts/unreachable_db_verify.py`

## Result — every number DB-verified against `cardeep-pg :5433`

| bucket | n | meaning |
|---|---:|---|
| **recovered-free (caged)** | **1** | serves own-site stock under stealth; in DB as `family_unreachable` |
| genuinely dead — NXDOMAIN | 39 | DNS does not resolve on www. or bare host (no browser fixes this) |
| genuinely dead — hard wall | 50 | resolves but never clears the body-gate in stealth |
| resolves, no own-site listing | 2 | renders, but no own-site car inventory surface |
| **total** | **92** | |

**Genuinely dead total = 89** (39 NXDOMAIN + 50 hard wall).

### (a) Recovered-free — 1, already caged
- **hrmotor.com** — `CDP-ES-25-K2DCKE63`, `entity_source=family_unreachable`,
  **246 own-site cars** (no platform_listing edge) live in DB. Home renders 768 KB of
  real listing HTML under an HTTP 403 honeypot; status-blind body-gate reads it. This
  was the single recovery the existing connector already found; the stealth sweep adds
  **zero** new recoveries.

### (b) Genuinely dead — 89, with evidence
- **39 NXDOMAIN** — `socket.getaddrinfo` fails on both host variants (e.g. pirenauto.es,
  covesaford.com, reneult.es, autosasua.com). Includes 1 malformed source record
  (`website="http://."`, "Autosman"). Dead businesses / expired domains.
- **50 hard wall**, by failure type (from swept detail):
  - 19 tiny block stubs (<6 KB body): Cloudflare 107-byte 403, 303–319-byte 202
    challenge stubs (mgvalladolid.com, cochesinternet.net, tayre.es, bydmadrid.com,
    sheltergarage.com 107-byte 403s).
  - 10 broken SSL/cert (alcauto.es `SSL_ERROR_UNKNOWN`, waycar.es `SSL_ERROR_BAD_CERT_DOMAIN`).
  - 8 nav timeouts (no response within 18 s on any path/host).
  - 6 connection errors (`NS_ERROR_*`).
  - 5 explicit "robot challenge screen" (chelsea1979.com, arrojoaudi.com — DataDome/CF
    challenge that never clears under stealth).
  - 2 CF/challenge interstitials.

### (c) Resolves, no own-site listing — 2
- **avolo.net** — best render HTTP 500 (server error shell), no inventory.
- **renaultleioa.es** — renders 105 KB at `/segunda-mano/` (HTTP 200) but **0 € prices,
  0 "precio", 0 own-site vehicle PDPs**; its only vehicle links point off-site to
  external aggregators. No own-site stock to cage.

## Verdict
The stealth browser **confirms the original 'unreachable' verdict** for 91 of 92
domains. The non-JS probe was NOT lying here: the cohort is genuinely dead (DNS gone)
or genuinely hard-walled (Cloudflare/DataDome stubs, broken TLS, server errors) —
verified by a real anti-detect browser, not a status code. Nothing new was caged;
`family_unreachable` stands at **1 dealer / 246 own-site cars** (DB-live).
