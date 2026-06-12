# T07 — HTML/JSON Parsing + Extraction Tooling Audit

**Domain:** HTML/JSON parsing + extraction · DOM parsers (selectolax / lxml / parsel /
BeautifulSoup) · JSON-LD + microdata extraction · regex-vs-LLM decision boundary ·
structured extraction with local LLM (outlines / instructor / lm-format-enforcer).

**Date:** 2026-06-12 · **Auditor:** tooling researcher · **Audience:** CARDEEP scraping fleet.

**Anti-hallucination key:** `[VERIFIED]` = I fetched the repo/PyPI/page this session.
`[ASSUMED]` = inference or recalled fact not refetched. Every release date below carries
its source URL.

---

## 0. CARDEEP current state (ground truth, read from source)

`[VERIFIED]` Read `scrapers/requirements.txt`, `scrapers/discovery/meili_enricher.py`,
`scrapers/discovery/repair_pass.py`.

- **There is NO dedicated HTML parser in the dependency set.** `scrapers/requirements.txt`
  lists `httpx`, `playwright`, `curl_cffi`, `camoufox`, `markitdown` — but **no
  selectolax / lxml / parsel / beautifulsoup4 / extruct**. `[VERIFIED]`
- All structured extraction is **hand-rolled pure-Python regex + `json.loads`**, centralized
  in `meili_enricher.py` and reused by `repair_pass.py`:
  - `_extract_jsonld(html)` — `_RE_LD_BLOCK.findall(html)` to grab `<script type="ld+json">`
    bodies, `json.loads`, then a recursive `_walk_ld` over `@graph` / nested dicts pulling
    `Car/Vehicle/Product/Offer/AggregateOffer`. Has a fragile fallback that string-rewrites
    `}{` → `},{` and re-parses as an array. `[VERIFIED]` (lines 204-319)
  - `_extract_microdata`, `_extract_next_data` (`__NEXT_DATA__`), `_extract_nuxt_data`
    (`__NUXT__`), `_extract_dealerk_meta`, `_extract_all_vehicle_images` — all regex.
    `[VERIFIED]` (imported in `repair_pass.py` lines 27-40)
  - Body scrape: `_RE_PRICE` (`\d{1,3}[\s.,]\d{3}\s*€`, keep ≥2 occurrences, MAX in
    1k-500k band), `_RE_KM`, `_RE_YEAR`. `[VERIFIED]`
- ADRs: `0002-qwen-classificador-fiscal.md` shows an LLM (Qwen) is already used for **fiscal
  classification**, so a local-LLM inference path exists in the project, but it is **not**
  wired into field extraction. `[VERIFIED]` (file present in `docs/adr/`)

**Why this matters for the audit:** CARDEEP's "current choice" for parsing is *no parser* —
regex against raw HTML. That is the fastest possible option and survives malformed markup,
but it has a real failure mode: no DOM, no robust microdata/RDFa, and the `}{`→`},{` hack
will mis-merge legitimately adjacent JSON-LD blocks. The recommendation below is **not "rip
out regex"** — it is a targeted, surgical upgrade where regex is structurally wrong.

---

## 1. DOM parsers — the four-way comparison

### 1.1 selectolax (Modest/Lexbor binding) — **RECOMMENDED PRIMARY**

- **Alive?** **YES, actively maintained.** Latest **v0.4.10, released 2026-05-26**
  (~2 weeks before this audit). 1.6k stars, 10 open issues, 638 commits, 55 releases.
  `[VERIFIED]` https://github.com/rushter/selectolax · https://pypi.org/project/selectolax/
- **What it solves:** C-speed HTML5 parsing with CSS selectors. Cython binding to the
  **Lexbor** engine (the preferred backend as of 2024; the older Modest backend's underlying
  C lib is no longer maintained — use `from selectolax.lexbor import LexborHTMLParser`).
  `[VERIFIED]` (repo docs `docs/lexbor.rst`, CHANGES.md)
- **Strengths:**
  - Fastest mainstream parser. Independent benchmarks put it ~5-30× faster than
    BeautifulSoup and meaningfully faster than `lxml.html` on real homepages
    (one cited bench: selectolax-lexbor 2.39s vs lxml 9.09s vs BS4 61.02s extracting
    from top-domain homepages). `[VERIFIED]` (multiple 2025 benchmark writeups)
  - Lowest memory footprint of the tree parsers; will not become the bottleneck below
    ~50 req/s. `[VERIFIED]` (webscraping.fyi, aows.jpt.sh comparisons)
  - 0.4.10 specifically optimized `css_first` and fixed attribute-access segfaults — i.e.
    they are still fixing real production bugs in 2026. `[VERIFIED]`
- **Weaknesses:**
  - CSS selectors only — **no XPath**. For the deep, conditional traversals CARDEEP's
    `_walk_ld` does over `@graph`, you still do that in Python (which is fine — JSON-LD is
    JSON, not DOM).
  - No built-in structured-data (microdata/JSON-LD) extractor; it gives you a fast tree,
    you write the selectors.
  - Historical edge case: a malformed CSS selector could hang (issue #36). Validate
    selectors; they are static in CARDEEP so this is a non-issue. `[VERIFIED]`
- **Fit for CARDEEP:** Replaces the brittle regex for **microdata** and for grabbing the
  `<script type="application/ld+json">` block bodies cleanly (no `}{` hack). Keeps the
  JSON-LD *walk* in Python. Drop-in next to httpx/curl_cffi.

### 1.2 lxml — **RECOMMENDED FALLBACK / where XPath is needed**

- **Alive?** **YES, very actively maintained.** 6.0.0 (2025-06-26) → 6.0.4 (2026-04-12).
  6.0.3/6.0.4 fixed OOM→`MemoryError` cases and a namespace-cleanup regression. `[VERIFIED]`
  https://github.com/lxml/lxml/releases · https://lxml.de/6.0/changes-6.0.0.html
- **What it solves:** The mature libxml2/libxslt binding. Full XPath 1.0, CSS via cssselect,
  the most memory-efficient tree, and the de-facto backend other libs sit on.
- **Strengths:** XPath (which selectolax lacks), battle-tested, security-patched wheels,
  fastest *pure*-tree after selectolax. It is also the engine under parsel and BeautifulSoup's
  `lxml` mode, so you may pull it in transitively anyway.
- **Weaknesses:** Slower than selectolax; heavier C deps (libxml2) than the single-purpose
  Lexbor; API less ergonomic than parsel/selectolax. Security note: keep ≥6.0.1 — older
  versions left `resolve_entities=True` for `iterparse`/`ETCompatXMLParser` (XXE risk).
  `[VERIFIED]`
- **Fit for CARDEEP:** Use **only** when a source needs XPath axis traversal that CSS can't
  express. Otherwise selectolax wins. Already a likely transitive dep.

### 1.3 parsel — **RECOMMENDED for ergonomics if a unified selector API is wanted**

- **Alive?** **YES, healthy.** Latest **1.11.0, 2026-01-29** (1.10.0 2025-01-17,
  1.9.1 2024-04-08). 1.3k stars, maintained by the Scrapy/Zyte org. `[VERIFIED]`
  https://pypi.org/project/parsel/ · https://github.com/scrapy/parsel/releases
- **What it solves:** A thin, pleasant wrapper over `lxml.html` giving **CSS + XPath + regex
  in one `Selector` object**, and — critically for CARDEEP — `Selector(...).jmespath(...)`
  for querying **JSON** (and mixed HTML/JSON) with the same API.
- **Strengths:** Minimal overhead on top of lxml.html (benchmarks show near-lxml speed);
  one API for HTML, XML, JSON; chainable; the same engine Scrapy uses in production.
  `[VERIFIED]` (parsel docs, webscraping.fyi)
- **Weaknesses:** Slower than selectolax (it is lxml underneath). Pulls lxml + cssselect +
  jmespath. Slightly more abstraction than CARDEEP needs if the only goal is "grab ld+json
  bodies fast."
- **Fit for CARDEEP:** Strong candidate if the team wants **one selector tool** for the whole
  fleet (HTML + the `__NEXT_DATA__`/`__NUXT__` JSON blobs via jmespath) instead of regex per
  CMS. Trades raw speed for a much cleaner, less error-prone recipe layer.

### 1.4 BeautifulSoup (bs4) — **NOT RECOMMENDED for the hot path** (alive, but wrong tool)

- **Alive?** **YES.** 4.14.3, 2025-11-30. Actively maintained. `[VERIFIED]`
  https://pypi.org/project/beautifulsoup4/ · https://www.crummy.com/software/BeautifulSoup/
- **What it solves:** Forgiving, beginner-friendly HTML navigation. Pure-Python tree wrapper
  (delegates parsing to `lxml`/`html.parser`/`html5lib`).
- **Strengths:** Most tolerant of garbage markup; huge ecosystem; great for one-off / low-volume
  scripts.
- **Weaknesses:** **The slowest and most memory-hungry of the four.** Benchmarks: ~5-30×
  slower than selectolax; becomes a bottleneck above ~10 req/s. For a fleet indexing
  333k+ vehicles this is the wrong default. `[VERIFIED]`
- **Verdict:** **Not dead, but disqualified** for CARDEEP's throughput. Acceptable only in a
  cold one-off analysis script, never in the spider/reaper/indexer hot path.

### DOM parser scoreboard

| Tool | Latest release | Maint. | Speed | XPath | JSON query | Verdict |
|---|---|---|---|---|---|---|
| **selectolax (lexbor)** | 0.4.10 · 2026-05-26 | Active | ★★★★★ | No | No | **PRIMARY** |
| **lxml** | 6.0.4 · 2026-04-12 | Active | ★★★★ | Yes | No | **FALLBACK (XPath)** |
| **parsel** | 1.11.0 · 2026-01-29 | Active | ★★★ | Yes | jmespath | **Ergonomic option** |
| BeautifulSoup | 4.14.3 · 2025-11-30 | Active | ★ | No (CSS only) | No | Avoid in hot path |

No corpse here — all four are alive. The differentiator is **throughput + API fit**, and
selectolax-lexbor wins for the fleet.

---

## 2. JSON-LD / microdata extraction

### 2.1 extruct — alive but SLOWING, the only purpose-built all-in-one

- **Alive?** **SUSPECT (slowing).** Latest release **0.18.0, 2024-11-08** — **~19 months
  ago at audit time**, which trips the "12+ months = suspect" rule. BUT the master branch
  has commits as recent as **2025-03-24** ("Skip empty JSON-LD scripts" #240), Feb-2025
  coverage CI, 39 open issues / 15 open PRs. So: **not abandoned, but no recent cut release.**
  `[VERIFIED]` https://pypi.org/project/extruct/ · https://github.com/scrapinghub/extruct ·
  commits page (last commit 2025-03-24).
- **What it solves:** One call — `extruct.extract(html, base_url=…, syntaxes=[…])` — returns
  **JSON-LD + Microdata + RDFa + OpenGraph + Microformat + Dublin Core** in one shot. This is
  exactly the surface CARDEEP currently reimplements by hand across `_extract_jsonld` +
  `_extract_microdata`. `[VERIFIED]`
- **Strengths:** Correct, spec-aware microdata/RDFa parsing (which regex cannot do robustly —
  microdata is a DOM `itemscope`/`itemprop` tree, not a flat pattern). Saves CARDEEP from
  maintaining its own microdata walker. Uses lxml under the hood.
- **Weaknesses:** **Release cadence has stalled** — depend on it with a pinned version and a
  vendored fallback, not blind `>=`. Pulls lxml + rdflib (heavier). Slower than a targeted
  selectolax+`json.loads` for the *JSON-LD-only* case.
- **Verdict / recommendation for CARDEEP:**
  - For **microdata + RDFa** (where regex is structurally wrong): adopt extruct, but **pin
    `extruct==0.18.0`** and treat it as frozen — watch the repo for a 2026 release; if it
    goes >12 months past last *commit* (currently 2025-03), re-evaluate. It is the best
    available and there is no actively-released competitor that bundles all syntaxes.
  - For **JSON-LD** (the common, high-value case): **keep a thin custom path** but parse the
    `<script type="application/ld+json">` bodies via a real parser (selectolax `css('script[
    type="application/ld+json"]')`), not the `_RE_LD_BLOCK` regex + `}{`→`},{` hack. Then
    feed bodies to `json.loads` and keep your existing `_walk_ld`. This removes the single
    most fragile line in the current code while staying fast.

### 2.2 Why not pure regex for JSON-LD/microdata (the current approach)

- **JSON-LD:** regex to *find* the `<script>` body is OK-ish, but CARDEEP's fallback that
  rewrites `}{`→`},{` will **corrupt two valid sibling JSON-LD objects** that legitimately
  abut, and silently drop on `JSONDecodeError`. A parser-extracted `<script>` body + tolerant
  JSON loader (or per-script `json.loads`) is strictly safer for ~zero cost. `[VERIFIED]`
  (read `_extract_jsonld`, lines 204-219)
- **Microdata:** `itemscope`/`itemprop` is inherently nested DOM scope resolution. Regex
  cannot track scope boundaries → CARDEEP's `_extract_microdata` is necessarily approximate.
  This is the clearest case to hand to extruct or a selectolax tree walk. `[ASSUMED:
  implementation detail of `_extract_microdata` not read line-by-line; its regex nature is
  VERIFIED from imports + the no-parser dependency set]`

---

## 3. The regex-vs-LLM decision boundary

This is a budget + reliability decision, not a fashion one. The rule for CARDEEP:

| Signal | Use | Why |
|---|---|---|
| Structured island present (JSON-LD, `__NEXT_DATA__`, `__NUXT__`, microdata) | **Parser + key walk** | Deterministic, free, fastest. ~99% of dealer CMS sites expose one. |
| Fixed visible-HTML pattern (price `nnn.nnn €`, `nnn.nnn km`, 4-digit year) | **Regex / CSS selector** | CARDEEP's body scrape already nails this. Cheap, auditable, no GPU. |
| Per-source stable layout, high volume | **Per-source recipe (CSS/XPath selectors)** | One-time author cost, deterministic forever. The "recipe" layer. |
| Unstructured prose, no island, layout varies per listing, long-tail low-volume sources | **Local LLM structured extraction** | Only here does the GPU cost pay off. |
| Need normalization/disambiguation (free-text fuel/trim → enum) | **LLM as classifier** (already done: Qwen fiscal, ADR-0002) | Fuzzy mapping is where LLMs beat regex. |

**Boundary statement:** Regex/parser is the default and covers the overwhelming majority of
CARDEEP's surface (dealer CMSs are JSON-LD-rich). Reserve the LLM for the **long tail**: pages
with no structured island and irregular prose, and for **value normalization**. Grammar-
constrained decoding slows generation 30-80% (typ. ~½ token rate for JSON schema), so an
LLM-per-listing default would wreck throughput at 333k+ vehicles. `[VERIFIED]` (InsiderLLM /
agenta.ai structured-output benchmarks)

---

## 4. Structured extraction with a local LLM (the long-tail tool)

CARDEEP already runs a local LLM (Qwen, ADR-0002). When a page has no structured island,
constrain the model to emit a Pydantic-shaped vehicle record. Three live tools:

### 4.1 outlines — **RECOMMENDED for the constrained-decoding engine**

- **Alive?** **YES, very active.** **v1.3.0, 2026-05-13.** 14k stars, 89 open issues,
  87 releases. Maintained by .txt (commercial steward). `[VERIFIED]`
  https://github.com/dottxt-ai/outlines
- **What it solves:** Token-level constrained generation from a JSON Schema / Pydantic model /
  regex / CFG — the output is *guaranteed* to match the schema. Backends: **transformers,
  vLLM, llama.cpp, MLX, Ollama, plus OpenAI/Gemini** (Ollama support is newer than older
  blog posts claim). `[VERIFIED]`
- **Strengths:** Strongest guarantee (structure enforced during decoding, not validated
  after); broadest local-backend coverage incl. vLLM (CARDEEP's likely serving path);
  "same code across backends." Best raw engine for a self-hosted, high-volume extractor.
- **Weaknesses:** Lower-level than instructor (you manage the model/backend); constrained
  decoding carries the 30-80% slowdown noted above (inherent to the technique, not the lib).
- **Fit:** The **engine** for CARDEEP's long-tail extractor when serving via vLLM/llama.cpp.

### 4.2 instructor — **RECOMMENDED for the ergonomic application layer**

- **Alive?** **YES, very active.** **v1.15.1, 2026-04-03.** 13.2k stars, 13 open issues,
  108 releases, 1,560 commits. `[VERIFIED]` https://github.com/567-labs/instructor
- **What it solves:** "Give me a Pydantic model, get a validated instance back." Wraps the
  provider call + retries-on-validation-failure. 15+ providers incl. **Ollama (local)**:
  `instructor.from_provider("ollama/llama3.2")`. Built on Pydantic. `[VERIFIED]`
- **Strengths:** Lowest-friction path; Pydantic validation + automatic re-ask on failure;
  same code local (Ollama) and cloud; matches CARDEEP's existing Pydantic 2.7 usage in
  `scrapers/requirements.txt`. `[VERIFIED]` (pydantic==2.7.4 present)
- **Weaknesses:** Reliability via **retry/validate**, not hard token-constraint — a stubborn
  local model can still need several round-trips (cost). Use a backend that *also* constrains
  (e.g. Ollama JSON mode / a grammar) for the strong guarantee.
- **Fit:** The **API layer** the extractor code calls. Pair with a constrained backend.

### 4.3 lm-format-enforcer — **VIABLE alternative engine (slightly behind on cadence)**

- **Alive?** **YES, but slower cadence.** **v0.11.2, 2025-08-09** (~10 months ago — under
  the 12-month line, still OK). 2k stars, 40 open issues, 21 releases. `[VERIFIED]`
  https://github.com/noamgat/lm-format-enforcer
- **What it solves:** Token-filtering format enforcement (JSON Schema / JSON mode / regex)
  across **transformers, llama.cpp, vLLM, LangChain, LlamaIndex, Haystack, TensorRT-LLM,
  ExLlamaV2**. Preserves model freedom on whitespace/field order. `[VERIFIED]`
- **Strengths:** Very broad backend list incl. TensorRT-LLM/ExLlamaV2; mature character-level
  + tokenizer-prefix-tree approach.
- **Weaknesses:** Release pace lags outlines (last release Aug-2025 vs outlines May-2026);
  fewer stars/mindshare. Functional overlap with outlines — pick one engine, not both.
- **Fit:** Drop-in alternative to outlines if you standardize on TensorRT-LLM/ExLlamaV2 or
  need its specific integrations. Otherwise outlines is the more momentum-backed pick.

### LLM-extraction recommended stack

> **instructor (Pydantic API surface) → over → a constrained backend.**
> Self-hosted/high-volume: **instructor + outlines/vLLM** (hard token constraint).
> Simplicity/low-volume: **instructor + Ollama JSON mode**.
> outlines and lm-format-enforcer are *engine* choices — **use exactly one**.

---

## 5. Verdict — is CARDEEP's current choice good enough?

**Current choice = "no parser, pure regex."** For JSON-LD-rich dealer CMS pages it is *fast
and largely fine*, but it has two concrete defects and one structural gap:

1. **Defect — JSON-LD `}{`→`},{` rewrite** can corrupt valid adjacent JSON-LD objects.
   **Fix:** extract `<script type="application/ld+json">` bodies with a real parser and
   `json.loads` each block; keep `_walk_ld`. Near-zero cost, removes the worst line.
2. **Defect/gap — regex "microdata"** can't resolve `itemscope` nesting.
   **Fix:** route microdata/RDFa through **extruct (pinned 0.18.0)** or a selectolax tree walk.
3. **Structural gap — no DOM at all.** Any future per-source recipe that needs "the price is
   the 2nd `<span class=...>` inside the offer card" is impossible with regex and trivial with
   a parser.

### Recommendations (ranked, surgical — do NOT rip out the working regex)

1. **Add `selectolax` (lexbor) as the fleet HTML parser.** `[VERIFIED] best-in-class, alive
   2026-05].` Use it to (a) pull `ld+json` script bodies cleanly, (b) author per-source CSS
   recipes, (c) walk microdata. Keep the existing regex body-scrape as the universal fallback.
2. **Pin `extruct==0.18.0`** for microdata + RDFa + the all-syntax cases the hand-rolled code
   approximates. Treat as frozen; re-audit if no release/commit by ~mid-2026. `[VERIFIED
   slowing, not dead].`
3. **Keep regex/CSS as the default extraction path.** Reserve LLM strictly for the long tail
   and for value normalization. The cost math (333k+ vehicles × 30-80% decode penalty)
   forbids an LLM-by-default extractor.
4. **For the long-tail LLM extractor:** **instructor + outlines** over the already-present
   local model (Qwen, ADR-0002), output validated against the same Pydantic 2.7 models the
   scrapers use. `[VERIFIED both alive 2026].`
5. **parsel** is the alternative to #1 if the team prefers one unified CSS/XPath/jmespath
   selector API across HTML and the `__NEXT_DATA__`/`__NUXT__` JSON blobs — accept ~lxml
   speed instead of selectolax speed. `[VERIFIED alive 2026-01].`

### Dead / disqualified

- **No fully dead tools in this domain** — all candidates had a release or commit within the
  last ~19 months.
- **BeautifulSoup:** alive but **disqualified from the hot path** on throughput (5-30× slower,
  bottleneck >10 req/s). One-off scripts only.
- **selectolax Modest backend:** its underlying C lib is unmaintained — **use the Lexbor
  backend only** (`from selectolax.lexbor import LexborHTMLParser`). `[VERIFIED].`
- **lm-format-enforcer:** not dead, but lower momentum than outlines — pick one engine.

---

## 6. Sample CONFIG

`requirements.txt` additions (pinned, audit-dated):

```text
# --- T07 parsing/extraction (audited 2026-06-12) ---
selectolax==0.4.10          # lexbor backend; fleet HTML parser (released 2026-05-26)
extruct==0.18.0             # microdata + RDFa + all-syntax; PINNED, release cadence slowed
# parsel==1.11.0            # OPTIONAL alt to selectolax: unified CSS/XPath/jmespath (2026-01-29)
# lxml is pulled transitively by extruct/parsel; if used directly, require >=6.0.1 (XXE fix)

# --- long-tail LLM structured extraction (only if/when wired in) ---
instructor>=1.15.1          # Pydantic-validated extraction API (2026-04-03)
outlines>=1.3.0             # token-constrained decoding engine, vLLM/llama.cpp (2026-05-13)
```

JSON-LD extraction — replace the regex `_RE_LD_BLOCK` find + `}{` hack:

```python
# Before: _RE_LD_BLOCK.findall(html)  + json.loads("[" + block.replace("}{","},{") + "]")
# After: parse the DOM once, json.loads each script body independently.
from selectolax.lexbor import LexborHTMLParser
import json

def extract_jsonld_blocks(html: str) -> list:
    tree = LexborHTMLParser(html)
    out = []
    for node in tree.css('script[type="application/ld+json"]'):
        body = (node.text() or "").strip()
        if not body:
            continue
        try:
            out.append(json.loads(body))   # per-block; no sibling-merge corruption
        except json.JSONDecodeError:
            continue                        # skip malformed, keep the rest
    return out
# Feed each parsed object into the EXISTING _walk_ld(out, item) — unchanged.
```

Microdata + RDFa via extruct (pinned), used only when JSON-LD is absent:

```python
import extruct
data = extruct.extract(
    html, base_url=url,
    syntaxes=["json-ld", "microdata", "rdfa", "opengraph"],
    uniform=True,
)
# data["microdata"] / data["rdfa"] are spec-correct trees regex cannot produce.
```

Long-tail LLM extraction (instructor + local model), only when no structured island:

```python
import instructor
from pydantic import BaseModel  # reuse the scrapers' existing vehicle model

class VehicleFields(BaseModel):
    make: str | None = None
    model: str | None = None
    year: int | None = None
    price_eur: float | None = None
    mileage_km: int | None = None
    fuel_type: str | None = None

client = instructor.from_provider("ollama/qwen2.5")  # reuse ADR-0002 local model
fields = client.chat.completions.create(
    response_model=VehicleFields,
    messages=[{"role": "user",
               "content": f"Extract the vehicle fields from this listing:\n{visible_text}"}],
    max_retries=2,
)
# For a HARD schema guarantee at high volume, serve via vLLM + outlines instead of Ollama.
```

---

## 7. Sources (all visited this session unless noted)

- selectolax: https://github.com/rushter/selectolax · https://pypi.org/project/selectolax/
- lxml: https://github.com/lxml/lxml/releases · https://lxml.de/6.0/changes-6.0.0.html
- parsel: https://github.com/scrapy/parsel/releases · https://pypi.org/project/parsel/
- BeautifulSoup: https://pypi.org/project/beautifulsoup4/ · https://www.crummy.com/software/BeautifulSoup/
- extruct: https://github.com/scrapinghub/extruct · https://github.com/scrapinghub/extruct/commits/master · https://pypi.org/project/extruct/
- outlines: https://github.com/dottxt-ai/outlines
- instructor: https://github.com/567-labs/instructor · https://python.useinstructor.com/
- lm-format-enforcer: https://github.com/noamgat/lm-format-enforcer
- benchmarks: webscraping.fyi (selectolax vs lxml/bs4), aows.jpt.sh/parsing, rushter.com/blog/python-fast-html-parser, dev.to "Best Data Parsing Tools"
- structured-output cost: insiderllm.com structured-output guide · agenta.ai structured-outputs guide
- CARDEEP source (read this session): `scrapers/requirements.txt`,
  `scrapers/discovery/meili_enricher.py`, `scrapers/discovery/repair_pass.py`,
  `docs/adr/0002-qwen-classificador-fiscal.md` (presence)
