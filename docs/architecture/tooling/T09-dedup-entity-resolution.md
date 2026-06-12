# T09 — Dedup / Entity Resolution: Live 2026 Tooling Audit

> **Domain:** Cross-source entity resolution for CARDEEP — resolving the *same physical
> car point-of-sale* (and the same chain/organization) when it surfaces under different
> names, addresses, domains, and IDs across AutoScout24, OEM locators, Coches.net,
> Wallapop, the F1 census, etc. Plus the sub-problems: fuzzy string matching,
> embedding-based blocking, and address/name normalization for Spanish dealers.
>
> **Audited:** 2026-06-12. **Marking discipline:** every tool is **[VERIFIED]** (I fetched
> the repo / PyPI / release page this session, URL cited) or **[ASSUMED]** (inferred, not
> opened). No corpses are recommended.
>
> **Recency bar:** a library with no release in ~12 months is *suspect*; no commit in
> ~12 months is *dead for our purposes*. Stated explicitly per tool.

---

## 0. The CARDEEP-specific problem (why generic benchmarks lie)

The incumbent is **not** a library — it is `services/api/codes.py::cdp_code` **[VERIFIED, read
this session]**: a *deterministic* SHA-256 over a canonical key with priority
`domain > CIF > normalized(name|municipality_code[|address])`. `_normalize` does
`NFKD → strip-non-ASCII → lowercase → drop everything but [a-z0-9]`.

Consequences, all load-bearing for the mandate ("a unique code per dealer", dual
platform membership, branch-vs-chain):

1. **Zero fuzzy tolerance.** `cdp_code` collapses *exact* normalized strings only.
   `"Talleres García S.L."` and `"Talleres Garcia SL"` normalize identically (good),
   but `"Auto García Motor"` vs `"Automóviles García"` vs `"García Automoción"` mint
   **three different codes** for one dealer. Cross-source overlap (AS24 slug vs OEM
   locator name vs Coches.net display name) is exactly this case and is **currently
   unresolved**.
2. **No probabilistic linkage anywhere.** There is no Fellegi-Sunter, no learned match
   weights, no blocking. `requirements.txt` **[VERIFIED]** lists *no* dedup/fuzzy
   library (`asyncpg`, `fastapi`, `uvicorn`, `openpyxl` + commented scraping stack).
   **This is a greenfield pick, not a replacement.**
3. **Two-tier identity.** Deterministic keys (domain, CIF) are *authoritative and must
   stay deterministic* — when a domain or a Spanish CIF/NIF matches, that is a hard
   link, no probability needed. Fuzzy/probabilistic linkage is only for the
   **name+address+geo** records that lack a shared hard key. The right architecture is
   **deterministic-first, probabilistic-fallback**, not "replace cdp_code with an ML
   model".

So the tool we pick must: (a) ingest blocking on cheap deterministic keys, (b) apply
Spanish-aware name+address comparison, (c) emit calibrated match probabilities and
clusters that map back to `cdp_code`/`org_code`, (d) run on a laptop/single node over
~13k entities today and stay sane at 100k+ as coverage scales, (e) be **alive in 2026**.

---

## 1. Verdict up front

| Layer | Pick | Status | Why |
|---|---|---|---|
| **Probabilistic record linkage / clustering** | **Splink 4** | ✅ **alive** (4.0.16, 2026-03-11) | Fellegi-Sunter on DuckDB, unsupervised EM, runs in-process next to nothing, MoJ-maintained, production-proven 2026 |
| **Fuzzy string comparison (inside Splink + standalone)** | **RapidFuzz** | ✅ **alive** (3.14.5, 2026-04-07) | Fastest, C++ core, the de-facto standard; `thefuzz`/`fuzzywuzzy` are wrappers/legacy |
| **Phonetic / Spanish-aware name keys** | **jellyfish** | ✅ **alive** (1.2.1, 2025-10-11) | Rust core, Match-Rating + metaphone for name blocking keys; complements RapidFuzz, doesn't compete |
| **Address parse + normalize** | **pypostal / libpostal** | ✅ **revived** (last commit 2025-12-06) | Only credible OSS multilingual address parser; Senzing re-trained the model (v1.2.0) |
| **Embedding blocking (optional, scale tier)** | **model2vec** (+ sentence-transformers fallback) | ✅ **alive** (0.8.2, 2026-05-29 / 5.5.1, 2026-05-20) | Static embeddings, ~500× faster than ST, CPU-only — viable for blocking; full ST only if accuracy demands |
| **dedupe (dedupeio)** | *fallback only* | 🟡 **slowing** (3.0.3, 2024-08-15; last commit 2025-07-29) | Works, active-learning UX is nice, but release cadence stalled and DuckDB-scale story is weaker than Splink |
| **recordlinkage** | ❌ **do not use** | 💀 **stale** (0.16, 2023-07-20; last commit 2023-07-20) | ~3 years no release *and* no commit. Teaching-grade, pandas-bound, does not scale. **Corpse for our purpose.** |

**Bottom line:** CARDEEP has *no* current ER library to grade — the deterministic
`cdp_code` is good and should stay as the hard-key layer. The bulletproof modern stack
to add is **Splink 4 (orchestrator) + RapidFuzz (comparators) + jellyfish (phonetic
keys) + pypostal (address normalization)**, with **model2vec** held in reserve for
embedding-based blocking once entity counts cross ~100k. **dedupe** is the fallback if a
human-in-the-loop active-learning labeling UX is wanted; **recordlinkage** is dead — do
not adopt.

---

## 2. Probabilistic record linkage — the orchestrator layer

### 2.1 Splink — **RECOMMENDED** ✅

- **Repo:** https://github.com/moj-analytical-services/splink — **[VERIFIED]** 2.2k★, MIT,
  ~9,952 commits, 206 open issues.
- **PyPI:** https://pypi.org/project/splink/ — **[VERIFIED]** latest **4.0.16, released
  2026-03-11**. Cadence is healthy: 4.0.15 (2026-02-17), 4.0.14 (2026-02-15), 4.0.13
  (2026-02-12), 4.0.12 (2025-12-22), 4.0.11 (2025-11-12). `5.0.0.dev*` pre-releases exist
  → v5 in active development. **Python >=3.9,<4.0.**
- **Backends [VERIFIED]:** DuckDB (default, in-process), Spark, AWS Athena, PostgreSQL.
- **Alive?** Emphatically. Backed by the UK Ministry of Justice analytical services team;
  there is a **2026-01-29 "Running Splink in Production at the MoJ"** blog post
  **[VERIFIED title via search]** (https://moj-analytical-services.github.io/splink/blog/2026/01/29/running-splink-in-production.html).

**What it solves.** Probabilistic record linkage and deduplication using the
**Fellegi-Sunter** model. You declare *blocking rules* (candidate-pair generators) and
*comparisons* (per-field similarity levels, e.g. exact / Jaro-Winkler>0.9 / Levenshtein),
and Splink learns the `m`/`u` match weights **unsupervised via Expectation-Maximisation**
(no labeled training data required), then clusters the pairwise scores into entities via
connected components. Term-frequency adjustments downweight common tokens (huge for
Spanish dealer names full of "Automóviles", "Talleres", "Motor", "S.L.").

**Strengths.**
- **No labels needed.** EM learns weights from the data itself — decisive for CARDEEP,
  which has no gold-standard match set today.
- **Scale on a laptop.** Robin Linacre (the author) documents **7M records deduped in ~2
  minutes for <\$1** on DuckDB **[VERIFIED via search]**. CARDEEP's 13k → 100k+ is
  trivial in comparison; the DuckDB backend runs in the same Python process, no cluster.
- **PostgreSQL backend exists** — CARDEEP's store is Postgres (`asyncpg`), so linkage can
  run server-side without exporting, *or* on DuckDB reading from Postgres. Architectural fit.
- **Calibrated probabilities + explainability.** Per-comparison match-weight waterfall
  charts; every link is auditable — aligns with CARDEEP's "machine-checkable" mandate and
  the V3-INQUISITION verification posture.
- **Composable comparators.** Comparison levels can call any SQL function incl.
  Jaro-Winkler, Levenshtein, and **custom UDFs** — so RapidFuzz/jellyfish-derived keys and
  pypostal-normalized fields plug straight in.

**Weaknesses / honest risks.**
- **Learning curve.** Fellegi-Sunter + blocking + EM is conceptually heavier than
  `dedupe`'s "label 20 pairs" flow. Mitigated by excellent docs and worked DuckDB examples.
- **You design blocking.** Bad blocking = missed links or combinatorial blow-up. This is
  skill, not a button. (CARDEEP already has natural blocks: province_code, municipality,
  first-3-chars of normalized name — see config below.)
- **206 open issues** — normal for a 2.2k★ project; not a red flag, triage is active given
  the 2026 release stream.

**Integration notes for CARDEEP.**
1. Keep `cdp_code` as the **deterministic hard layer**: domain-match and CIF-match are
   *forced* links, fed to Splink as deterministic rules (`blocking_rules_to_generate_predictions`
   plus a deterministic pre-pass) so they never get probabilistically second-guessed.
2. Run Splink only over the **residual** records sharing no hard key, blocked by
   `province_code` + name/geo keys.
3. Cluster output (`cluster_id`) becomes the **entity identity**; mint/attach `cdp_code`
   per cluster. Branch-vs-chain (the `01-ENTITY-ONTOLOGY.md` D-problem) is a *second*
   Splink model at the `organization` grain (looser blocking, name-core comparison) feeding
   `org_code`.
4. Use **DuckDB backend** for batch re-linkage jobs (weekly per the MoJ production guidance:
   retrain ~yearly, not weekly — Fellegi-Sunter tolerates drift). Postgres backend for
   incremental in-DB linkage if export latency hurts.

**Sample config (`pipeline/dedup/splink_entity.py`):**
```python
import splink.comparison_library as cl
from splink import DuckDBAPI, Linker, SettingsCreator, block_on

# Records: one row per (source, raw entity). Columns pre-normalized by pypostal + _normalize:
#   name_norm, name_phonetic (jellyfish metaphone-es), street_norm, municipality_code,
#   province_code, postcode, domain, cif, lat, lon
settings = SettingsCreator(
    link_type="dedupe_only",
    # --- BLOCKING: only compare plausibly-same records (cheap deterministic keys) ---
    blocking_rules_to_generate_predictions=[
        block_on("province_code", "name_phonetic"),                 # same province, same phonetic name
        block_on("municipality_code", "substr(name_norm, 1, 4)"),   # same town, same name stem
        block_on("postcode"),                                       # same postcode bucket
        block_on("domain"),                                         # shared domain → near-certain
    ],
    # --- COMPARISONS: per-field similarity ladders (Splink learns the weights via EM) ---
    comparisons=[
        cl.NameComparison("name_norm").configure(term_frequency_adjustments=True),
        cl.LevenshteinAtThresholds("street_norm", [1, 3]),
        cl.ExactMatch("municipality_code").configure(term_frequency_adjustments=True),
        cl.ExactMatch("postcode"),
        # geo proximity comparison (deg) — same building vs different branch
        cl.DistanceInKMAtThresholds("lat", "lon", [0.05, 0.2, 1.0]),
    ],
    retain_matching_columns=True,
    retain_intermediate_calculation_columns=True,
)

linker = Linker(df_records, settings, db_api=DuckDBAPI())
# Unsupervised training — no labels:
linker.training.estimate_probability_two_random_records_match(
    [block_on("domain")], recall=0.9
)
linker.training.estimate_u_using_random_sampling(max_pairs=2_000_000)
linker.training.estimate_parameters_using_expectation_maximisation(
    block_on("municipality_code", "substr(name_norm,1,4)")
)
preds = linker.inference.predict(threshold_match_probability=0.9)
clusters = linker.clustering.cluster_pairwise_predictions_at_threshold(
    preds, threshold_match_probability=0.95
)  # cluster_id → maps to cdp_code per physical POS
```
**Pin:** `splink>=4.0.16,<5` (v5 is in dev; pin to 4.x until v5 stabilizes).

---

### 2.2 dedupe (dedupeio) — **FALLBACK** 🟡

- **Repo:** https://github.com/dedupeio/dedupe — **[VERIFIED]** 4.5k★, ~3,333 commits,
  77 open issues, **last commit 2025-07-29** ("Update benchmark-bot.yml").
- **PyPI:** https://pypi.org/project/dedupe/ — **[VERIFIED]** latest **3.0.3, released
  2024-08-15** (3.0.2 2024-07-03, 3.0.1 2024-07-01, 3.0.0 2024-06-27). **Python >=3.8.**
- **Alive?** 🟡 **Slowing.** ~22 months since last *release*, ~10.5 months since last
  *commit* as of this audit. Not dead, but the cadence has clearly cooled vs Splink.

**What it solves.** Active-learning record linkage/dedup: it asks a human to label ~10–30
uncertain pairs, trains a logistic-regression matcher on those labels, then blocks +
scores + clusters. The labeling UX (`dedupe.console_label`) is genuinely pleasant.

**Strengths.** Lowest-friction *supervised* path; good when you *want* a human to curate a
labeled set; mature clustering; long pedigree.

**Weaknesses.** (a) Needs human labeling — CARDEEP wants unsupervised first. (b) pandas/SQLite
flavored; the big-data story (`dedupe` + Postgres) is doable but more bespoke than Splink's
DuckDB/Spark backends. (c) Release cadence stalled — the single biggest reason it is fallback,
not primary, under our 12-month recency bar (release is past it; commits are borderline inside it).

**When to pick it over Splink:** if CARDEEP later wants an *interactive human-in-the-loop
labeling tool* to build a gold set (e.g. to validate Splink's unsupervised output), dedupe's
`console_label` is the better UX. Otherwise Splink wins.

**Sample config (active-learning, fallback path):**
```python
import dedupe
fields = [
    dedupe.variables.String("name_norm"),
    dedupe.variables.String("street_norm"),
    dedupe.variables.Exact("municipality_code"),
    dedupe.variables.String("postcode", has_missing=True),
]
deduper = dedupe.Dedupe(fields)
deduper.prepare_training(records_dict)  # records_dict: {id: {field: value}}
dedupe.console_label(deduper)           # human labels ~20 pairs
deduper.train()
clusters = deduper.partition(records_dict, threshold=0.5)
```

---

### 2.3 recordlinkage — **DEAD, DO NOT USE** 💀

- **Repo:** https://github.com/J535D165/recordlinkage — **[VERIFIED]** 1.1k★, 912 commits,
  61 open issues, **last commit 2023-07-20** ("Update CI pipeline for publishing package").
- **PyPI:** https://pypi.org/project/recordlinkage/ — **[VERIFIED]** latest **0.16, released
  2023-07-20**. Prior: 0.15 (2022-04-19), 0.14 (2019-12-01). **Python >=3.8 (3.8–3.11 only).**
- **Alive?** 💀 **No.** ~3 years with *neither a release nor a commit*. Fails the recency
  bar on both axes by a wide margin. Capped at Python 3.11 — already a friction point on
  modern stacks.

**What it solved.** A pandas-based teaching/research toolkit: index (blocking) → compare →
classify. Clean API for learning the *concepts* of record linkage.

**Why not for CARDEEP.** Abandoned; pandas-bound (no DuckDB/Spark/Postgres scale path);
Python ceiling at 3.11; everything it does, Splink does faster, at scale, and maintained.
**Recommending it would be recommending a corpse.** Excluded.

---

## 3. Fuzzy string matching — the comparator layer

### 3.1 RapidFuzz — **RECOMMENDED** ✅

- **Repo:** https://github.com/rapidfuzz/RapidFuzz — **[VERIFIED]** (maintainer Max Bachmann).
- **PyPI:** https://pypi.org/project/rapidfuzz/ — **[VERIFIED]** latest **3.14.5, released
  2026-04-07**. Recent: 3.14.3 (2025-11-01), 3.14.2 (2025-10-31), 3.14.1 (2025-09-08),
  3.13.0 (2025-04-03). Uses Trusted Publishing + Sigstore attestations.
- **Alive?** ✅ Very. Steady 2025→2026 releases.

**What it solves.** Fast fuzzy string similarity: ratio, partial-ratio, token-sort/set,
Levenshtein, Jaro, Jaro-Winkler, Indel, LCS — C++ core with SIMD/algorithmic optimizations.
**The de-facto modern standard;** `thefuzz`/`fuzzywuzzy` are thin or legacy wrappers around
this family — do not add them.

**Strengths.** Fastest in class — a 2025 multilingual study **[VERIFIED via search]**
(ijeedu.com / researchgate "A Comparative Analysis of Python Text Matching Libraries")
clocks RapidFuzz at ~2,500 pairs/s vs jellyfish ~1,600/s single-threaded, ~40% faster
across cases. MIT, C++ core, `process.cdist` for vectorized many-to-many scoring, drop-in
`process.extract` API.

**Weaknesses.** Pure *edit-distance/token* similarity — no phonetic, no semantic. For
"García" vs "Garzía" vs "Garcia" it shines; for "Automóviles del Sur" vs "AutoSur Motor"
(same dealer, different naming) it under-detects — that needs phonetic keys (jellyfish) +
token-set + Splink term-frequency.

**Integration.** Two roles: (a) **inside Splink** as the comparator behind Jaro-Winkler /
Levenshtein comparison levels (DuckDB ships these natively; use RapidFuzz when computing
candidate features in Python or for a custom UDF); (b) **standalone** for cheap pre-blocking
similarity and the AS24-slug ↔ OEM-name reconciliation in `pipeline/ingest.py`.

**Sample config:**
```python
from rapidfuzz import fuzz, process, utils
# many-to-many candidate scoring for a blocking shortlist
score = fuzz.token_set_ratio("automoviles garcia motor", "garcia automocion",
                             processor=utils.default_process)  # ~ token-aware
best = process.extract("talleres garcia sl", candidate_names,
                       scorer=fuzz.WRatio, score_cutoff=85, limit=5)
```
**Pin:** `rapidfuzz>=3.14,<4`.

### 3.2 jellyfish — **RECOMMENDED (complement)** ✅

- **Repo:** https://github.com/jamesturk/jellyfish — **[VERIFIED]** newest tag **v1.2.1
  (2025-10-11)**; prior v1.2.0/v1.1.4 (2025-03-31), v1.1.3 (2024-12-14). Rust-cored.
- **PyPI:** https://pypi.org/project/jellyfish/ — **[VERIFIED]** `info.version` = **1.2.1**.
- **Alive?** ✅ Yes (release 2025-10, ~8 months — inside the bar).

**What it solves.** Phonetic encoders (Soundex, Metaphone, NYSIIS, Match-Rating) + string
distances (Damerau-Levenshtein, Jaro-Winkler, Hamming). It is **complementary, not a
competitor** to RapidFuzz: use jellyfish to build **phonetic blocking keys** (so
"García"/"Garzia"/"Garssia" land in the same block) that Splink then scores. RapidFuzz is
faster for raw distance; jellyfish owns phonetics.

**Weakness / Spanish caveat.** Soundex/Metaphone are English-tuned. For Spanish dealer
names this is *good enough as a blocking key* (over-generates candidates, which Splink then
filters), but it is **[ASSUMED]** — validate against a Spanish name sample before trusting
it as a sole key. Pair it with `substr(name_norm,1,4)` blocks as belt-and-suspenders.

**Sample config:**
```python
import jellyfish
key = jellyfish.metaphone("García Automoción")     # phonetic blocking key
d   = jellyfish.jaro_winkler_similarity("garcia", "garzia")  # 0.0–1.0
```
**Pin:** `jellyfish>=1.2,<2`.

---

## 4. Address & name normalization

### 4.1 pypostal / libpostal — **RECOMMENDED** ✅

- **libpostal repo:** https://github.com/openvenues/libpostal — **[VERIFIED]** **last commit
  2025-12-06** ("Update Senzing data versions to v1.2.0 release").
- **pypostal:** https://github.com/openvenues/pypostal — Python C-bindings.
- **Alive?** ✅ **Revived.** Long dormant after 2016, but **Senzing re-trained the model on
  ~1.2B records (40% more data) and shipped data v1.2.0**, with the binding repo updated
  **2025-12-06** **[VERIFIED]**. Supports normalization in 60 languages incl. Spanish,
  parsing in 100+ countries.

**What it solves.** The single hard part of address dedup: parsing free-text Spanish
addresses ("C/ Mayor 12, 3ºB, 28013 Madrid") into structured components (`road`,
`house_number`, `postcode`, `city`, `state`) and **expanding** abbreviations ("C/"→"calle",
"Avda"→"avenida") so two spellings of one address normalize to one string. This directly
fixes the `address` arm of `cdp_code` (today a raw `_normalize` strip that does NOT
canonicalize "C/" vs "Calle").

**Strengths.** Only credible OSS multilingual parser; statistical NLP over OSM, not regex;
the de-facto choice (Senzing, PostGIS `pgsql-postal` use it).

**Weaknesses.** Native C dependency — build/install friction on Windows (CARDEEP dev host is
Win11, prod likely Linux). Heavy model download (~2GB). Mitigation: run it in the Linux
ingest container, expose normalized fields; or use the maintained Docker image. If the C
build is a blocker in dev, fall back to a deterministic Spanish abbreviation map for the
common cases and let libpostal run only in the pipeline container.

**Integration.** Run in `pipeline/normalize.py` *before* `cdp_code`: feed
`expand_address()` + `parse_address()` output into `street_norm`/`postcode`/`city`, replacing
the raw address strip. Improves both the deterministic key AND the Splink comparison quality.

**Sample config:**
```python
from postal.expand import expand_address
from postal.parser import parse_address
variants = expand_address("Avda. de la Constitución 5, 41001 Sevilla")
parts = dict((label, val) for val, label in parse_address(variants[0]))
street_norm = parts.get("road", "")
postcode    = parts.get("postcode", "")
```
**Install:** native libpostal + `postal` (PyPI) in the Linux pipeline image.

### 4.2 Name normalization — keep `_normalize`, extend it
The existing `_normalize` (NFKD → ASCII → `[a-z0-9]`) is a fine *base*. Extend with a small
Spanish legal-suffix stripper (`s.l.`, `s.a.`, `sl`, `sa`, `scp`, `cb`) and stopword removal
(`automoviles`, `talleres`, `motor`, `auto`) **only for the phonetic/blocking key**, never
for the stored display name. Splink's `term_frequency_adjustments` handles the rest
statistically — do not over-engineer the normalizer.

---

## 5. Embedding-based blocking (scale tier, optional)

When deterministic + phonetic + token blocks miss semantically-equivalent names
("Concesionario Oficial SEAT Sevilla Sur" ↔ "SEAT Sevilla — Polígono Sur"), embedding
similarity catches them. **Not needed at 13k entities; relevant at 100k+.**

### 5.1 model2vec — **RECOMMENDED for the embedding tier** ✅
- **PyPI:** https://pypi.org/project/model2vec/ — **[VERIFIED]** latest **0.8.2, released
  2026-05-29** (0.8.1 2026-03-27, 0.8.0 2026-03-26, 0.7.0 2025-10-05). MIT, by MinishLab.
- **Alive?** ✅ Very. **What it solves:** distills any sentence-transformer into a *static*
  embedding model — up to **50× smaller, ~500× faster, CPU-only**. Perfect for blocking:
  embed all entity names once, ANN-nearest-neighbours → candidate pairs for Splink. Cheap
  enough to run on every ingest with no GPU.
- **Weakness:** static embeddings lose some contextual nuance vs full transformers —
  acceptable for *blocking* (recall-oriented; Splink does precision). **[ASSUMED]** the
  accuracy is sufficient for name blocking; validate on a sample before trusting as sole block.

```python
from model2vec import StaticModel
model = StaticModel.from_pretrained("minishlab/potion-base-8M")
emb = model.encode(entity_names)  # CPU, fast; feed to FAISS/usearch ANN → candidate pairs
```

### 5.2 sentence-transformers — **FALLBACK (accuracy tier)** ✅
- **PyPI:** https://pypi.org/project/sentence-transformers/ — **[VERIFIED]** latest **5.5.1,
  released 2026-05-20** (5.5.0 2026-05-12, 5.4.1 2026-04-14). Maintained by Tom Aarsen / HF.
- **Alive?** ✅ Very. Use **only if** model2vec's static embeddings miss too many true links
  and a GPU is available. For blocking, model2vec's speed wins; reserve full ST for a
  high-accuracy pass on the residual hard cases. A multilingual model (e.g.
  `paraphrase-multilingual-MiniLM-L12-v2`) handles Spanish.

---

## 6. Is the current CARDEEP choice good enough? — final answer

**There is no current ER library** — the incumbent is the deterministic `cdp_code` generator.

- **Keep `cdp_code` as the deterministic hard-key layer.** It is correct and fast for
  domain/CIF/exact-normalized matches. Do **not** replace it.
- **It is NOT good enough alone** for cross-source resolution: it has zero fuzzy/probabilistic
  capability, so the same dealer under different names across AS24/OEM/Coches.net mints
  multiple `cdp_code`s — directly violating "a unique code per dealer" and blocking the
  branch-vs-chain (`org_code`) requirement.
- **What to add (the bulletproof modern stack):**
  1. **pypostal/libpostal** → normalize addresses *before* keying (fixes the address arm).
  2. **Splink 4** → unsupervised probabilistic linkage + clustering over the residual
     records with no shared hard key; emits the entity clusters that own `cdp_code`, and a
     second model at organization grain for `org_code` (branch↔chain).
  3. **RapidFuzz + jellyfish** → comparators and phonetic blocking keys feeding Splink.
  4. **model2vec** (fallback **sentence-transformers**) → embedding blocking, switched on
     only when entity counts and missed-link rate justify it (~100k+).
- **Explicitly rejected:** **recordlinkage** (dead, ~3y no commit/release, Py≤3.11). **dedupe**
  demoted to fallback (release cadence stalled; supervised/active-learning only). `fuzzywuzzy`
  / `thefuzz` not added (legacy wrappers over the RapidFuzz family).

**One-line requirements addition (pipeline tier, Linux container):**
```
splink>=4.0.16,<5
rapidfuzz>=3.14,<4
jellyfish>=1.2,<2
postal>=1.1            # native libpostal required
model2vec>=0.8,<1      # embedding blocking, scale tier
# sentence-transformers>=5.5  # accuracy-tier fallback, GPU optional
```

---

## 7. Source ledger (all [VERIFIED] = fetched this session unless noted)

- Splink PyPI (4.0.16, 2026-03-11): https://pypi.org/project/splink/
- Splink repo (2.2k★, MIT, 206 issues): https://github.com/moj-analytical-services/splink
- Splink prod blog 2026-01-29 *(via search, title verified)*: https://moj-analytical-services.github.io/splink/blog/2026/01/29/running-splink-in-production.html
- Splink 7M/2min benchmark *(via search)*: https://www.robinlinacre.com/fast_deduplication/
- dedupe PyPI (3.0.3, 2024-08-15): https://pypi.org/project/dedupe/
- dedupe repo (4.5k★, last commit 2025-07-29): https://github.com/dedupeio/dedupe + https://api.github.com/repos/dedupeio/dedupe/commits
- recordlinkage PyPI (0.16, 2023-07-20): https://pypi.org/project/recordlinkage/
- recordlinkage repo (last commit 2023-07-20): https://github.com/J535D165/recordlinkage + https://api.github.com/repos/J535D165/recordlinkage/commits
- RapidFuzz PyPI (3.14.5, 2026-04-07): https://pypi.org/project/rapidfuzz/
- RapidFuzz repo: https://github.com/rapidfuzz/RapidFuzz
- jellyfish PyPI (1.2.1): https://pypi.org/pypi/jellyfish/json
- jellyfish tags (v1.2.1, 2025-10-11): https://github.com/jamesturk/jellyfish/tags
- RapidFuzz vs jellyfish benchmark study 2025 *(via search)*: https://ijeedu.com/index.php/ijeedu/article/view/188
- libpostal repo (last commit 2025-12-06, Senzing data v1.2.0): https://github.com/openvenues/libpostal + https://api.github.com/repos/openvenues/libpostal/commits
- pypostal repo: https://github.com/openvenues/pypostal
- Senzing libpostal re-train *(via search)*: https://senzing.com/what-is-libpostal/
- sentence-transformers PyPI (5.5.1, 2026-05-20): https://pypi.org/project/sentence-transformers/
- model2vec PyPI (0.8.2, 2026-05-29): https://pypi.org/project/model2vec/
- CARDEEP incumbent: `services/api/codes.py`, `requirements.txt`, `docs/architecture/01-ENTITY-ONTOLOGY.md`, `docs/architecture/03-DATA-MODEL.md` *(read this session, repo-local)*
