# CARDEEP — Scraping Tooling: 2026-07-15 Ten-Repo Evaluation & Prior-Art Reconciliation

> **Status: ADDENDUM, not a replacement.** This document adds to and reconciles with `docs/architecture/02-SCRAPING-ENGINE.md` (Tier-1 design doc), `plans/cardeep-program/02-extraction.md` (2026-06-23 EUR0 SOTA review), and `docs/architecture/tooling/TOOLING.md` (the project's own declared "single, authoritative Bill of Materials," compiled 2026-06-12 from audits T01–T16). **TOOLING.md remains the master BOM.** Nothing here overrides it; where this document's findings diverge from TOOLING.md's picks or from the other two docs, the divergence is called out explicitly (§3) and left for the BOM owner to close, not silently resolved by this document.

---

## 1. Executive summary

CARDEEP's shipped scraping/extraction engine already out-competes a naive off-the-shelf stack on the three axes that actually matter for this project: TLS/JA3/JA4 impersonation at Tier-0 (`curl_cffi`, session-coherent, already matching TOOLING.md's A1 pick exactly — `requirements.txt:34`), semantic ban classification (`ban_detector.py`'s OK/CHALLENGE/BANNED/NOT_FOUND verdict, which no evaluated framework — Scrapy, Crawlee-python, Scrapling's Spider, crawl4ai — replicates out of the box), and a verified, cost-sorted extraction ladder (`pipeline/recipe_cracker.py`'s `RUNG_REGISTRY`, gated by VAM count-quorum in `pipeline/verify.py`, not a self-consistency check against one sample). Of the ten external repos evaluated this cycle, **zero earned a clean ADOPT**, two earned **PARTIAL_ADOPT** as narrow, dev-only, out-of-hot-path tools (`browser-use` for semi-unattended long-tail recipe hunting; `microsoft/markitdown` for a real, documented, currently-zero-coverage PDF-census gap), and the remaining eight are **ALREADY_SUPERSEDED** or **REJECT** — in most cases because CARDEEP already built a narrower, more tightly verified equivalent of the same idea.

What is genuinely missing is not a scraping library — it is two pieces of operational hygiene the project's own docs already diagnosed and then didn't finish: (1) a live, current Tier-1 Chromium-stealth engine (`patchright`) that TOOLING.md wanted promoted on 2026-06-12 and that shipped code never wired, running instead on `camoufox` direct as of commits `c28d385`/`c5e2b90` (2026-06-20); and (2) a resolved pick for the Tier-0 high-throughput alternate client, where two of CARDEEP's own documents (`TOOLING.md` A2 and `02-extraction.md`'s chosen-technology table) independently name two different libraries for the same role, and neither is actually installed. Both are addressed as explicit reconciliation items in §3 and carried into the roadmap in §8 as additive, reversible, EUR0 PRs — not as new discoveries, but as closing gaps this project's own prior art already flagged.

---

## 2. Current state recap (condensed, cross-checked directly against the live repo this session)

- **Tier-0 (HTTP, no browser):** `curl_cffi>=0.15,<0.16` is pinned and live (`requirements.txt:34`), matching TOOLING.md's A1 pick (`curl_cffi PICK, >=0.15.0,<0.16`) exactly. It is a module-level import in the `dasweltauto` / `mercedes_benz` / `milanuncios` wholesale connectors, i.e. not aspirational — it runs today.
- **Tier-1 (stealth browser):** `pipeline/engine/tier1/browser.py` ships `camoufox` as the hard-coded default (`engine: str = "camoufox"`, line 67 — `[VERIFIED]`) and `nodriver` as an explicit **opt-in-only** engine behind a license box quoting the AGPL-3.0 network-copyleft risk in the module's own docstring. The same docstring already names `patchright` as "the staged upgrade for Chrome-shaped WAFs once installed; camoufox remains the permissive baseline meanwhile" — i.e. the code is self-aware of the gap, not silently ignorant of it. `git log` confirms the camoufox-default / AGPL-fenced-nodriver shape shipped in two commits: `c28d385` and `c5e2b90`, both dated **2026-06-20** — `[VERIFIED]`.
- **Zero Scrapling/patchright wiring:** a repo-wide check for `scrapling` in `pipeline/` returns exactly one hit — `pipeline/recipe_extract_css.py`, and it is prose, not an import ("the rung auto-derives the selectors from the DOM, **scrapling-style**"). The extractor is a bespoke `lxml`-based inducer; `import scrapling` occurs nowhere in `pipeline/`.
- **`requirements.txt:42-44`** lists `scrapling>=0.4.9`, `camoufox[geoip]`, and `browserforge` all **commented out** — `[VERIFIED]`. This means the currently-shipped Tier-1 *default* (`camoufox`, imported directly in `browser.py`) is not even guaranteed by the pinned dependency file — a clean install cannot run Tier-1 until someone installs `camoufox[geoip]` out-of-band, independent of anything to do with Scrapling.
- **Extraction ladder:** `pipeline/recipe_cracker.py`'s `RUNG_REGISTRY` runs platform-specific data-layer extractors first (cost 0–3: `AutoScout24Extractor`, `CochesComExtractor`, etc.), then `CssAdaptiveExtractor` (`recipe_extract_css.py`, registered `cost=4`), then `LlmFieldMapExtractor` over local Ollama (`recipe_extract_llm.py`, registered `cost=7`, wired ~2026-07-04), then `GenericWebExtractor` — every rung gated by `pipeline/verify.py`'s `record_count_verdict` (VAM count-quorum) before a recipe is trusted, and persisted versioned via `pipeline/recipe_schema.py`.
- **Governance layer:** `governor.py` (per-host token bucket), `fingerprints.py` (rotate-on-ban), `ban_detector.py` (semantic OK/CHALLENGE/BANNED/NOT_FOUND classification) — none of these have an out-of-the-box equivalent in any of the ten evaluated frameworks (see §6).
- **Discovery layer:** `pipeline/sources/*.py` has **zero PDF ingestion** today, and `pipeline/platform/dealerprobe.py`'s `_ASSET_EXT_RE` actively excludes `.pdf` from the crawl as a non-page asset — `[VERIFIED]`. A documented census source (SIGRAUTO, 595 CATs + 25 fragmentadoras, PDF-per-CCAA, `docs/research/SOURCES_ES.md:147` — `[VERIFIED]`) sits unconnected as a result.
- **Obscura:** installed, Apache-2.0, MCP-wired (`mcp__obscura__*`), per CARDEEP's own `CLAUDE.md` explicitly not yet benchmarked against real WAFs and not connected to `pipeline/engine/`.

---

## 3. Two confirmed prior-art discrepancies

### 3a. Scrapling/patchright plan vs. shipped camoufox-direct

**The conflict, stated plainly.** TOOLING.md (§3.1, 2026-06-12) instructs: *"Promote [Scrapling] to live; use Adaptor/StealthyFetcher (patchright-backed), NOT its Spider"* and separately (§4) records that stock camoufox was to be dropped as the Tier-1 default in favor of `patchright>=1.60.0` + `nodriver` (escalation). `docs/architecture/02-SCRAPING-ENGINE.md` independently reaches the same conclusion in its own "GAP-20" adversarial note: *"Canonical: the primary injector is patchright (the Scrapling default); camoufox is demoted to an OPTIONAL, pinned, vendored injector."* Two of CARDEEP's own architecture documents agree patchright should be the Tier-1 default. **Shipped reality is the opposite**: `pipeline/engine/tier1/browser.py` ships `camoufox` as the hard default (commits `c28d385`/`c5e2b90`, 2026-06-20 — eight days *after* the TOOLING.md BOM), `nodriver` as AGPL-gated opt-in, and neither `patchright` nor `Scrapling` is imported anywhere in `pipeline/`.

**This evaluation's own Scrapling verdict independently confirms the capability gap is real** — patchright-backed `StealthyFetcher` is genuinely stronger than raw camoufox on Chrome-fingerprinted WAFs today, since Scrapling itself moved off Camoufox at v0.3.13. But it also concludes the *vehicle* should not be the Scrapling package — Scrapling's other surface (Adaptor parser, Spider, CLI/shell, MCP server) is redundant with `CssAdaptiveExtractor`, `LlmFieldMapExtractor`, and `recipe_cracker.py`, all more tightly bound to VAM verification than Scrapling's generic equivalents, and TOOLING.md's own §0 doctrine (rule 5) already forbids adopting frameworks that would evict the in-house control plane.

**Recommendation:** neither "formalize shipped reality" nor "execute the original TOOLING.md plan" wholesale — split the two. (1) **Execute the capability** TOOLING.md and the GAP-20 note both wanted: add `patchright` as a **direct** dependency (Apache-2.0, per TOOLING.md A3, pin `>=1.60.0`) and a `_solve_patchright()` function beside the existing `_solve_camoufox`/`_solve_nodriver` in `tier1/browser.py`'s engine-string dispatch, reusing the proven `BrowserResult`/mint-then-drain contract, then live-test it against a real Cloudflare Turnstile target before trusting it over camoufox. (2) **Do not** add the `Scrapling` package itself — its parsing/self-heal role is already superseded by shipped code. (3) Fix `requirements.txt:42-44` regardless of (1)/(2) — uncomment and pin `camoufox[geoip]`, since it is the live default and a clean install cannot run Tier-1 without it today.

This discrepancy affects two of the ten repos in this evaluation directly and indirectly: **Scrapling** directly (it is the literal subject of the deviation), and it indirectly frames how the **browser-use** and **AutoScraper** verdicts should be read — both were evaluated against "what CARDEEP's Tier-1/extraction ladder already does," which today means camoufox-direct, not the patchright-first target state TOOLING.md and GAP-20 intended.

### 3b. primp vs. rnet/wreq-python — same role, two picks, neither installed

`plans/cardeep-program/02-extraction.md` (2026-06-23) picks **`primp`** (Rust `rquest` binding, `github.com/deedy5/primp`, MIT) for "Tier-0 high-throughput fallback." `TOOLING.md` §1.1 A2 (2026-06-12, eleven days earlier) picks **`rnet` / `wreq-python`** (`FB, ==0.12.0`, Rust/PyO3 over BoringSSL) for the same role. **Neither package appears in `requirements.txt`** — `[VERIFIED]` — so this is a pure documentation conflict, not yet a code conflict; there is no live behavior at stake, only which name gets built out next.

This document does not have — and none of the ten repo-verdict agents that fed it had — the comparative benchmark data (req/s, RAM under fan-out, HTTP/3 support trade-off, PQ-correctness under CARDEEP's actual worker concurrency) to pick a winner between them. **This is an explicit open item for whoever owns TOOLING.md to close**: benchmark both against the same 2026 adversarial criteria already used elsewhere in these docs, pick one, and update both `TOOLING.md` §1.1 A2 and `02-extraction.md`'s chosen-technology table to agree. Until then, neither should be pinned (see §9).

---

## 4. Per-repo verdict table

| # | Repo | Verdict | One-line rationale | Effort | Already in TOOLING.md? |
|---|---|---|---|---|---|
| 1 | firecrawl/firecrawl | **REJECT** | AGPL-3.0 core engine *is* the extraction path (not a swappable component); self-hosted lacks Fire-engine anti-bot (capability downgrade vs. Tier-0/1 already shipped); `/extract` is self-admitted Beta, fails the VAM count-quorum gate every rung must clear | High | No |
| 2 | unclecode/crawl4ai | **ALREADY_SUPERSEDED** | Apache-2.0, RAG/Markdown-oriented framework; its LLM-field-map and CSS-`generate_schema` ideas are both already built tighter in-house (`LlmFieldMapExtractor`, `CssAdaptiveExtractor`) with VAM verification crawl4ai lacks | Medium | No |
| 3 | browser-use/browser-use | **PARTIAL_ADOPT** | MIT; LLM-per-step agent structurally unfit for `RUNG_REGISTRY` or Tier-1 drain (OSS build ships no stealth — paid Cloud-only); genuinely fills the undocumented-recipe / long-tail-dealers-without-inventory slice Obscura's manual primitives don't cover unattended | Low | No |
| 4 | apify/crawlee + crawlee-python | **ALREADY_SUPERSEDED** | Apache-2.0; Node package is a hard stack mismatch (Node 16+ requirement vs. pure-Python monorepo); Python port's `SessionPool`/`ConcurrencySettings` are coarser than `ban_detector.py` (semantic) and `governor.py` (per-host token bucket) already shipped | Trivial | No |
| 5 | scrapy/scrapy | **ALREADY_SUPERSEDED** | BSD-3; re-confirms TOOLING.md §4 Demoted verdict ("no gain over the custom coordinator"); native downloader has no TLS impersonation or semantic ban detection, and closing that gap means re-opening `scrapy-impersonate`, already deferred once in `02-extraction.md` | High | **Yes** (TOOLING.md §4 Demoted) |
| 6 | microsoft/markitdown | **PARTIAL_ADOPT** | MIT; zero overlap with the web-extraction stack; fills a real, documented, currently-zero-coverage gap (SIGRAUTO 595 CAT + 25 fragmentadora PDF census) that `dealerprobe.py` actively excludes today | Low | No |
| 7 | D4Vinci/Scrapling | **ALREADY_SUPERSEDED** (as a package to adopt) | BSD-3; TOOLING.md already PICKed/KEEPed this (A3/A4) on 2026-06-12 — this evaluation reconfirms the *pick was sound* but finds the shipped code never wired it; the real fix is a direct `patchright` dependency, not the Scrapling wrapper (see §3a) | Medium | **Yes** (TOOLING.md A3 PICK / A4 KEEP) |
| 8 | Genymobile/scrcpy | **REJECT** | Apache-2.0; categorically out of scope by the owner's own documented decree (`02-extraction.md`: digital-footprint-only, no mobile-app-only sources); not a scraping tool at all | Trivial | No |
| 9 | alirezamika/autoscraper | **ALREADY_SUPERSEDED** | MIT; dormant (~13 months since last push, no tagged release since 2022); single-labeled-example DOM-path matcher, strictly weaker than the already-shipped `CssAdaptiveExtractor` + `recipe_cracker.py` ladder | Trivial | No |
| 10 | lwthiker/curl-impersonate | **ALREADY_SUPERSEDED** | MIT; origin repo dormant (~2 years stale, presets capped at Chrome 116/Firefox 117, both 2023-era); the technique's active lineage is `lexiforest/curl-impersonate`, already consumed live via `curl_cffi` (`requirements.txt:34`) | Trivial | No |

---

## 5. Detailed sections — ADOPT / PARTIAL_ADOPT, and the two repos TOOLING.md already names

### 5.1 browser-use/browser-use — PARTIAL_ADOPT

**What it is not for:** a Tier-1 drain engine or a `RUNG_REGISTRY` rung. Its own README concedes the OSS build ships no stealth/fingerprinting (paid Cloud-only), and its per-navigation-step LLM call is structurally incompatible with a cheap→expensive, VAM-verified, warm-started ladder — registering it as a rung would mean a live, unattended LLM agent inside production recipe-cracking, which is exactly the anti-pattern the cost ladder exists to avoid.

**What it is for:** the batch/semi-unattended slice of recipe-hunting neither `recipe_cracker.py` (needs a target already crackable by a registered `Extractor`) nor Obscura's raw MCP primitives (need a human or live Claude Code session driving every click) cover today.

- **Integration mechanism:** a new standalone script, `scripts/browser_use_recipe_hunt.py`, following the exact precedent already in `scripts/` (human/agent-invoked, one-off, outside `pipeline/`'s hot path). `browser-use` is an optional/dev dependency only — never added to pinned production `requirements.txt`, mirroring the existing commented-out treatment of `scrapling`/`camoufox[geoip]`/`browserforge` there.
- **Concrete first PR-sized step:** point a `browser-use` Agent at one stubborn long-tail target that has already failed VAM verification through `CssAdaptiveExtractor` / `LlmFieldMapExtractor` / `GenericWebExtractor`, and ask it to locate the actual data layer — consistent with CARDEEP's own "target the data layer, never fight HTML" law. A human reviews the output and hand-encodes a new platform-specific `Extractor`, registered normally via `register_rung("<source>", <factory>, cost=<N>)`. From that point on `browser-use` is out of the loop entirely.
- **Effort:** Low. **Risk:** OSS build has no anti-detection — treat every hard-target session as throwaway, never scheduled or cron'd; drives Chrome over raw CDP (same detection-risk class as `nodriver`, unbenchmarked); per-step LLM calls make cost/output non-deterministic — never let it touch a target twice without human review in between.

### 5.2 microsoft/markitdown — PARTIAL_ADOPT

**The gap is real, not hypothetical:** `docs/research/SOURCES_ES.md:147` documents SIGRAUTO — 595 CATs (desguaces) + 25 fragmentadoras, PDF-per-CCAA at known URLs — and it sits unconnected: `pipeline/sources/` has zero PDF ingestion, and `dealerprobe.py`'s `_ASSET_EXT_RE` actively excludes `.pdf` from crawl.

- **Integration mechanism, two separate entry points, neither touching the inventory hot path:**
  1. Discovery layer — new `pipeline/sources/sigrauto.py`, downloading via the existing Tier-0 `curl_cffi` session, passing bytes to `markitdown` (`pip install 'markitdown[pdf]'` — pure-Python extras, no system binary, no OCR, no cost), parsed into entity/address/CAT-registration rows feeding the same `discovery_candidates` contract other sources use.
  2. Research tool — `markitdown-mcp` registered as a local MCP server alongside Obscura, for second-brain research sessions that already read INE DIRCE / BORME PDFs by hand.
- **Concrete first PR-sized step:** fetch and inspect one real SIGRAUTO PDF to confirm it has a native text layer (markitdown's `pdf` extra has **no OCR** — a scanned image PDF would silently return empty/garbage) before writing `sigrauto.py`. This check is unverified in this session and must be done before implementation, not assumed.
- **Effort:** Low. **Risk:** no-OCR blind spot; scope-creep risk — the evidence supports one small, low-cadence census adapter, not general "ingest any PDF" in the 42-connector pipeline.

### 5.3 scrapy/scrapy — CONFIRMS TOOLING.md's existing verdict

TOOLING.md §4 already lists Scrapy under "Demoted (alive but wrong-sized, not dead): ... **Scrapy (no gain over the custom coordinator)**" — a decision dated 2026-06-12. This evaluation is **not a fresh discovery**; it is an independent re-check that **confirms** the original call and adds the specific mechanism: Scrapy's native downloader has no TLS/JA3 impersonation (closing that gap means `scrapy-impersonate`, already deferred once in `02-extraction.md`), its `AutoThrottle` is status-code/latency-only with no notion of a soft (200-with-CAPTCHA) challenge the way `ban_detector.py` already classifies, and its Item Pipeline offers hook-sequencing with no DB-enforced invariant equivalent to the 4-layer VAM/Deep-Ledger/Gestionador/Inquisición stack. No action item results — the verdict stands as-is.

### 5.4 D4Vinci/Scrapling — UPDATES TOOLING.md's operational status, does not overturn its pick

TOOLING.md §1.1 A3/A4 (2026-06-12) PICKs/KEEPs Scrapling for patchright-backed `StealthyFetcher` and adaptive-selector parsing, and §3.1 explicitly wanted it "promoted to live." This evaluation does **not** overturn that technology judgment — Scrapling remains an excellent, actively maintained project and its patchright backend genuinely beats raw camoufox on Chrome-fingerprinted WAFs today. What this evaluation **updates** is the *implementation status*: the pick was never executed. Eight days after the BOM shipped, `browser.py` shipped camoufox-direct instead, and no file in `pipeline/` imports `scrapling` or `patchright` to this day. The refined recommendation (§3a) is narrower than TOOLING.md's original instruction: take the *capability* (patchright as a Tier-1 engine option) directly, not the *package* (Scrapling's full framework surface, most of which duplicates code CARDEEP already shipped tighter). This is a refinement of a dated decision, not a new one.

---

## 6. Every REJECT / ALREADY_SUPERSEDED / DEFER repo not detailed above

**firecrawl/firecrawl — REJECT.** Core engine is AGPL-3.0, and unlike `nodriver` — which CARDEEP already gates to opt-in-only because it is a peripheral, swappable Tier-1 component — Firecrawl's engine would *be* the extraction path serving CARDEEP's public API, a deeper and less isolable exposure. Self-hosting explicitly lacks Fire-engine, a capability *downgrade* versus the Tier-0/Tier-1 stack already shipped. `/extract` is LLM-per-page, self-declared Beta with acknowledged run-to-run inconsistency — incompatible with the VAM count-quorum + zero-parse-loss gate every recipe must clear. The hosted SaaS avoids the license/self-host problems but converts them into recurring metered spend, violating EUR0.

**unclecode/crawl4ai — ALREADY_SUPERSEDED.** Apache-2.0, actively maintained. Its central value proposition — "LLM-ready Markdown for RAG/agents" — targets a problem CARDEEP does not have (it writes verified Postgres rows, not prose for an agent). Its narrower ideas (`LLMExtractionStrategy`, `JsonCssExtractionStrategy.generate_schema()`) are both weaker versions of already-shipped code: `LlmFieldMapExtractor` needs no multi-provider LiteLLM abstraction (CARDEEP only ever targets local Ollama), and `generate_schema()` validates against one sample with no count-quorum, versus `CssAdaptiveExtractor`'s domain-signal induction wrapped in `recipe_cracker.py`'s full ladder.

**apify/crawlee + apify/crawlee-python — ALREADY_SUPERSEDED.** Apache-2.0. The primary `crawlee` package is Node/TS-first — a stack mismatch against CARDEEP's pure-Python monorepo, disqualifying on fit alone. The Python port's `SessionPool` retires sessions on HTTP status codes only (no content/semantic classification, unlike `ban_detector.py`'s 4-state verdict), and its `ConcurrencySettings` is a global task-rate, not the per-host token bucket `governor.py` already implements. One narrow idea worth a future look, not a reason to adopt the dependency: `AdaptivePlaywrightCrawler`'s continuous randomized re-validation of the cheap tier to catch layout drift automatically.

**Genymobile/scrcpy — REJECT.** Apache-2.0, actively maintained. Zero functional overlap: it mirrors/controls a physical or virtual Android device over USB-ADB or LAN, with no HTTP/web relationship at all. Out of scope by the project owner's own explicit decree in `02-extraction.md` (digital-footprint-only, no mobile-app-only sources) — no CARDEEP source today is documented as mobile-app-only with zero web equivalent, so there is no live case to weigh it against.

**alirezamika/autoscraper — ALREADY_SUPERSEDED.** MIT, but functionally dormant (~13 months since last push, no tagged release since 2022, upstream Issues locked). Its entire trick — infer a DOM extraction path from one labeled example — is already implemented and exceeded by `CssAdaptiveExtractor`, which needs no human-supplied example at all, wrapped in `recipe_cracker.py`'s cost-ladder-plus-count-quorum, which AutoScraper has no equivalent of.

**lwthiker/curl-impersonate — ALREADY_SUPERSEDED.** MIT, but the named repo is dormant (last push mid-2024, presets capped at Chrome 116/Firefox 117 — both 2023-era). Its technique lineage did not die, it relocated: `lexiforest/curl-impersonate` (active fork) is what `lexiforest/curl_cffi` — CARDEEP's already-pinned Tier-0 client — actually wraps. One residual, unresolved risk worth flagging: confirm CARDEEP's pinned `curl_cffi` build actually vendors current `lexiforest/curl-impersonate` presets rather than an older release — a freshness concern, not a repo-adoption concern.

---

## 7. Gap analysis — what none of the ten repos solve

1. **PDF ingestion for census/discovery sources** — genuinely unsolved by any of the nine web-scraping-oriented repos; solved narrowly by `markitdown` (§5.2), but that is a discovery-layer gap-fill, not a scraping-engine gap.
2. **Semi-unattended recipe discovery for the long-tail backlog** — no framework evaluated offers an autonomous "find where the data lives" agent; only `browser-use` addresses this, and only as a scoped, human-reviewed, dev-only tool (§5.1) — it produces candidate recipes for humans/agents to hand-encode, it does not close the backlog by itself.
3. **The Tier-0 high-throughput-alternate pick itself** — unresolved between `primp` and `rnet`/`wreq-python` (§3b); none of the ten repos evaluated this cycle bear on that decision at all.
4. **The Tier-1 patchright gap** — none of the ten repos *solve* this either; Scrapling could have been the vehicle but this evaluation recommends against using it as one (§3a/§5.4). The gap remains open until `patchright` is wired directly into `tier1/browser.py`.
5. **`requirements.txt` / shipped-default inconsistency** — `camoufox[geoip]` is commented out while it is the live Tier-1 default import; an operational bug independent of any of the ten repos.
6. **`curl_cffi` fingerprint currency** — flagged as a latent risk by the `curl-impersonate` evaluation, not resolved by it: whether CARDEEP's pinned build tracks current Chrome-124/135-class presets or something older is unverified and should be checked directly against the installed wheel.

None of these six gaps require adopting a new scraping framework. All six are closable with narrow, additive, in-house changes.

---

## 8. Prioritized roadmap (EUR0-first, each item ~1 PR, additive, reversible)

1. **Fix `requirements.txt:42-44`** — uncomment and pin `camoufox[geoip]` (it is the live Tier-1 default and currently un-pinned). Zero new capability, closes a clean-install breakage. *(§2/§7.5)*
2. **Wire `patchright` directly into `tier1/browser.py`'s engine dispatch** (`_solve_patchright()` beside `_solve_camoufox`/`_solve_nodriver`), pin `patchright>=1.60.0` (Apache-2.0, per TOOLING.md A3). Live-test against one real Cloudflare Turnstile target before promoting it over camoufox as default. **Do not** add the `Scrapling` package. *(§3a)*
3. **Resolve the primp-vs-rnet/wreq-python conflict** — benchmark both against the existing 2026 adversarial-bench methodology already used for curl_cffi/nodriver/camoufox in `02-extraction.md`; update both `TOOLING.md` §1.1 A2 and `02-extraction.md`'s chosen-technology table to name the same winner. *(§3b)*
4. **Verify the SIGRAUTO PDF has a native text layer**, then build `pipeline/sources/sigrauto.py` using `markitdown[pdf]` (MIT, pure-Python). *(§5.2)*
5. **Install `markitdown-mcp` as a local research tool** alongside Obscura, for second-brain PDF-reading sessions. *(§5.2)*
6. **Write `scripts/browser_use_recipe_hunt.py`** as a dev-only, out-of-hot-path discovery script, scoped to one hard target at a time, never scheduled. *(§5.1)*
7. **Confirm `curl_cffi`'s vendored fingerprint currency** against the pinned wheel — a verification task, not a code change. *(§7.6)*

---

## 9. Dependencies to pin

**Production `requirements.txt`, EUR0, low-risk:**
- `camoufox[geoip]` — uncomment/pin the existing live default (MPL-2.0). *(fixes existing gap, not a new addition)*
- `patchright>=1.60.0` — Apache-2.0, per TOOLING.md A3; new Tier-1 engine option, additive, not a default-flip until live-tested.
- `markitdown[pdf]` — MIT; `pdfminer.six` + `pdfplumber` only, pure-Python, no system binary, no OCR, no network cost.

**Dev-only / never in production `requirements.txt`** (mirrors the existing commented-out treatment of `scrapling`/`camoufox[geoip]`/`browserforge` precedent):
- `browser-use` — MIT; `scripts/` only, never imported by `pipeline/`.
- `markitdown-mcp` — MIT; local MCP research tool alongside Obscura, never touches production data path.

**Explicitly not pinned, pending an open decision (§3b):**
- `primp` and `rnet`/`wreq-python` — do not pin either until the TOOLING.md owner closes the conflict; pinning one preemptively would itself create a third undocumented deviation.

**Explicitly rejected, per the AGPL/network-service doctrine already established for `nodriver`:**
- `firecrawl` (self-hosted or as a dependency) — REJECT outright, not opt-in-gated, because unlike `nodriver` (a peripheral, swappable Tier-1 component that CAN be isolated behind an opt-in flag) Firecrawl's AGPL-3.0 engine would sit directly in the served-data path if self-hosted, and the hosted-SaaS alternative reintroduces the same license risk as recurring paid spend, which EUR0 doctrine blocks independently.

No other repo among the ten produces an AGPL or network-service candidate; the nodriver-style opt-in-only pattern has no additional application this cycle.

---

## 10. Sources

**Reconciled against (internal, authoritative prior art):**
- `docs/architecture/tooling/TOOLING.md` (compiled 2026-06-12, 16 domain audits T01–T16) — master BOM, not superseded.
- `docs/architecture/02-SCRAPING-ENGINE.md` — Tier-1 design doc, including its own GAP-20 adversarial reconciliation note.
- `plans/cardeep-program/02-extraction.md` — 2026-06-23 EUR0 SOTA review and chosen-technology table.

**Cross-checked directly against the live repo (Read/Grep/Bash, `C:\Users\elias\projects\cardeep`):**
- `pipeline/engine/tier1/browser.py` (full ENGINES docstring; engine dispatch)
- `requirements.txt` (full file)
- `pipeline/recipe_extract_css.py` (docstring)
- `git log`/`git show` for commits `c28d385`, `c5e2b90` (both 2026-06-20)
- `docs/architecture/02-SCRAPING-ENGINE.md` (GAP-20 note)
- `plans/cardeep-program/02-extraction.md` (chosen-technology table)

**Ten repos evaluated** (each independently fetched live, dated 2026-07-15, by dedicated research agents): `firecrawl/firecrawl`, `unclecode/crawl4ai`, `browser-use/browser-use`, `apify/crawlee` + `apify/crawlee-python`, `scrapy/scrapy`, `microsoft/markitdown`, `D4Vinci/Scrapling`, `Genymobile/scrcpy`, `alirezamika/autoscraper`, `lwthiker/curl-impersonate`.

---

## 11. Independent verification of this document (2026-07-16)

The orchestration run that produced this document hit an operational failure (the internal audit sub-agent hung across four retry attempts over ~14 hours before being stopped manually) — recorded here for the project's own honesty discipline, not as a badge. Before publishing, the four most load-bearing internal-repo claims in this document were spot-checked directly against the live repo, independent of the agent pipeline that produced the draft:

| Claim | Check | Result |
|---|---|---|
| `browser.py` default engine at line 67 | `sed -n '60,70p' pipeline/engine/tier1/browser.py` | Exact match: `engine: str = "camoufox"` |
| `requirements.txt:34` = `curl_cffi` pin; `:42-44` = commented scrapling/camoufox/browserforge | `sed -n '28,45p' requirements.txt` | Exact match, both line ranges |
| Commits `c28d385`/`c5e2b90`, dated 2026-06-20 | `git log --format='%H %ai %s'` | Exact match, including verbatim commit message quoted in §2 |
| `docs/research/SOURCES_ES.md:147` SIGRAUTO citation | `sed -n '145,149p' docs/research/SOURCES_ES.md` | Exact match: "SIGRAUTO 595+25 (PDF/CCAA)" |

All four passed exactly. The ten external-repo verdicts feeding this document were produced by dedicated research agents using live `WebFetch`/`gh api` calls against each target repository (verified license, maintenance activity, and version-specific claims per repo, recorded in each verdict's own `verified_facts` field) — those external facts were not independently re-fetched a second time for this addendum.
