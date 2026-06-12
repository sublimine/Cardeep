# CARDEEP — V3 · The Inquisition (Adversarial Verifier Chain)

> **The deepest validator in CARDEEP. CARDEEP NEVER SELLS LIES.**
>
> The VAM (`pipeline/verify.py`, `migrations/0004`) is a *count-quorum*: it asks "do
> ≥2 paths agree on a number?" That is necessary but **not sufficient** — it cannot
> catch a claim where every path shares the same blind spot (a silent cap that all
> three counters inherit, a stale snapshot all paths read, a fabricated row no path
> re-fetches). The **Inquisition** is the layer above the VAM: a *separate adversarial
> verifier chain that defaults every load-bearing claim to REFUTED and forces it to
> survive N orthogonal skeptics who never share state, tools, or sources with the path
> that produced the claim.*
>
> This document **supersedes and expands** the light `05-VERIFICATION-VAM` written by
> the master-architecture workflow. The VAM remains as the *first-pass producer-side*
> quorum; the Inquisition is the *authoritative adversary* that the VAM verdict must
> itself survive.
>
> **Anchor reality (read before designing):**
> - `pipeline/verify.py` — the existing VAM count-quorum [VERIFIED, read this session].
> - `migrations/0004_verification_health.sql` — `verification_verdict`, `source_health`,
>   `alert` tables [VERIFIED].
> - `docs/research/SOURCES_ES.md` §6 (capture-recapture denominator ~44k floor / 50-90k
>   ceiling), §7 (owner's 5/5 hand-verified quorum), §8 (honest refutations: VW OneHub
>   HTTP 500, Das WeltAuto SEO doorways, Dacia 404) [VERIFIED].
> - `docs/ARCHITECTURE.md` (entity/vehicle/event schema), `docs/architecture/01-ENTITY-ONTOLOGY.md`
>   (live DB: **12.862 entities / 39.068 vehicles**, kind mis-assignment bug at ingest)
>   [VERIFIED].
>
> **Marking discipline:** every claim is **[VERIFIED]** (read from repo/DB/live fetch
> this session) or **[ASSUMED]** (inferred, not opened). No placeholders, no stubs.

---

## 0. The lie taxonomy — what the Inquisition exists to kill

A "lie" in CARDEEP is **any served value that does not correspond to verified reality.**
Lies are not malicious; they are *emergent* from a pipeline of agents, scrapers, and
caches. The Inquisition enumerates seven lie-classes, each with a worked failure that is
**real or structurally possible in the current repo**:

| # | Lie class | Concrete CARDEEP failure | Why the VAM alone misses it |
|---|---|---|---|
| L1 | **Inflated count** | Flexicar sitemap "23.769" includes SEO landing pages, not real stock [VERIFIED, SOURCES_ES.md §2.1]. | If all paths count the same inflated sitemap, the count-quorum *agrees* on the inflated number. |
| L2 | **Silent cap** | Aggregator caps pagination at ~1000–2000 / ~20 pages [VERIFIED, 02-SCRAPING-ENGINE §1 law 4]; a 5000-car dealer silently truncates to 1000. | Every path drains the same capped surface → all three return 1000 → quorum says TRUSTWORTHY. |
| L3 | **Silently-dropped field** | `pipeline/ingest.py` could ingest a dealer with `price=NULL` on 40% of rows; the count is right, the *content* is hollow. | Count-quorum verifies row *count*, never field *fill-rate* or *plausibility*. |
| L4 | **Staleness** | `unoauto.com` sitemap is stale — PDPs 404 [VERIFIED, SOURCES_ES.md §2.1]; rows exist in DB with `last_seen` 30 days old, served as "live". | The VAM has no freshness axis; a stale count quora-agrees with itself forever. |
| L5 | **Fabrication** | An LLM enrichment agent hallucinates a `cif`/`cnae`/phone that was never on the page. | No path re-fetches the *source bytes*; the fabricated field is internally consistent across DB reads. |
| L6 | **Coverage gap** | We serve "100% of Madrid dealers" but only discovered the AS24 subset; the registral CNAE-45 + Places tail (50-90k ceiling) is missing [VERIFIED, SOURCES_ES.md §6]. | The VAM verifies what *was* collected, never what *should* exist (the denominator). |
| L7 | **Kind mis-attribution** | `ingest.py:52` hardcodes `kind='concesionario_oficial'` for **every** AS24 dealer — `ok-cars`, `autohero-*`, `flexicar-*` are falsely "official" [VERIFIED, 01-ENTITY-ONTOLOGY §0]. | Count and identity are correct; the *semantic label* is a lie no count-quorum tests. |

> **The doctrine that follows from L1–L7:** never verify a claim with the path that
> produced it, and never verify it on a single axis. Each lie-class above is killed by a
> *different orthogonal lens* (§3). Redundancy (three counters of the same surface) is
> replaced by **orthogonality** (one re-query, one raw recount, one blind live re-fetch,
> one cross-source corroboration, one denominator bound).

---

## 1. The Inquisition's three inviolable laws

### Law I — DEFAULT-REFUTED (presumption of falsehood)
A claim enters the Inquisition with verdict `REFUTED`. It earns `TRUSTWORTHY` **only** by
surviving a quorum of independent skeptics (Law III). **Absence of refutation is not
proof.** If a skeptic cannot independently reproduce the claim — for *any* reason
(source down, tool missing, timeout) — that skeptic returns `REFUTE`, never `ABSTAIN→pass`.
The burden is always on the claim, never on the doubter. This is the inversion of the
VAM's optimism ("TRUSTWORTHY when modal value supported by ≥2"): the Inquisition starts
from guilt.

### Law II — PRODUCER EXCLUSION (the path that made it cannot judge it)
No skeptic may share **any** of the four state dimensions with the producer:

```
PRODUCER STATE = ⟨ source, tool, cache/snapshot, code-path ⟩
```

A skeptic is *independent* iff it differs on **≥2 of these 4 dimensions** AND never on
zero. Concretely, if the producer was `⟨autoscout24, curl_cffi, snapshot_T0, ingest.py⟩`,
a valid skeptic is e.g. `⟨coches.net, browser, live_T1, recount.sql⟩` (differs on all 4).
An *invalid* skeptic re-runs `ingest.py` against the same `autoscout24` snapshot — that is
the producer wearing a mask. §4 formalizes the independence score and the hard gate.

### Law III — ORTHOGONAL QUORUM (≥2 independent paths must agree; majority-refute kills)
A claim is `TRUSTWORTHY` iff **≥2 mutually-independent skeptics ASSERT it within
tolerance AND no rival assertion also reaches ≥2 (clean majority) AND no skeptic returns
a *hard* refutation** (a hard refutation is a contradiction of bytes, not a mere
divergence — §5.3). If the majority of independent skeptics REFUTE, the claim is
**killed** regardless of how many ASSERT. This generalizes `verify.py`'s modal-quorum to
N orthogonal lenses with a veto for hard contradictions.

> These three laws are the whole soul of the Inquisition. Everything below is the
> machinery that makes them concrete, numeric, and impossible to fake.

---

## 2. Architecture — the chain, never the loop

The Inquisition is a **chain external to the producer**, not a callback the producer
invokes. The producer writes a *claim*; a wholly separate process (different code module,
different DB role, different network egress) picks the claim off a queue and prosecutes it.

```
 PRODUCER SIDE                          INQUISITION SIDE (separate process / DB role)
 ─────────────                          ──────────────────────────────────────────────
 scraper / ingest / LLM enrich          claim_queue  ──►  PROSECUTOR (assigns lenses)
        │                                                      │
        │ writes claim envelope                                ├─► spawn N skeptics (§3)
        ▼                                                      │      each: different
 inquisition_claim ───────────────────────────────────►       │      ⟨source,tool,cache,path⟩
 (status=PENDING)                                              │
                                                               ▼
                                              skeptic verdicts ──► QUORUM ENGINE (§5)
                                                               │
                                                               ▼
                                            inquisition_verdict (TRUSTWORTHY|REFUTED|
                                                  INCONCLUSIVE|QUARANTINED)
                                                               │
                                                               ▼
                                       MANAGER ROUTER (§7): fix | research | quarantine | escalate
```

**Independence by construction, not by promise:**
- The Inquisition process runs under a **read-only DB role** (`cardeep_inquisitor`,
  `GRANT SELECT` only) so it physically cannot write the rows it judges. [ASSUMED — role
  to be created in a migration; design requirement, not yet in repo.]
- Live re-fetch skeptics egress through a **different network identity** than the producer
  (different proxy pool / exit IP / TLS profile) so a source serving stale-cached bytes to
  the producer's IP cannot serve the same staleness to the skeptic.
- Skeptics receive **only the claim envelope** (the assertion + subject key), never the
  producer's working data, intermediate counts, or cache handles. Zero shared memory.

### 2.1 The claim envelope (what the producer must emit)

```jsonc
{
  "claim_id": "ULID",
  "subject_type": "count|entity_field|inventory|coverage|kind|delta|denominator",
  "subject_key": "ES-28 | CDP-ES-28-XXXX | autoscout24 | ...",
  "claim": "human + machine assertion",          // e.g. "province ES-28 has 4128 active dealers"
  "asserted_value": "4128",                        // typed
  "producer_state": {                              // for Producer Exclusion (Law II)
    "source": "autoscout24",
    "tool": "curl_cffi",
    "snapshot_id": "snap_2026-06-12T08:00Z",
    "code_path": "ingest.py@a1b2c3"
  },
  "load_bearing": true,                            // only load-bearing claims get full N skeptics
  "tolerance": 0.01,                               // claim-class default, overridable (§5.1)
  "evidence_uri": "raw://as24/ES-28/snap_.../",   // bytes the producer used, for cross-check
  "created_at": "..."
}
```

> `evidence_uri` is **not** trusted as proof — it is the *defendant's exhibit*, used by
> skeptics to detect fabrication (compare served field vs source bytes) but never to
> *confirm* a claim (a producer that fabricates can fabricate its own evidence).

---

## 3. The five orthogonal lenses (perspective-diverse skepticism)

The Inquisition's power is that its skeptics are **perspective-diverse**, not redundant.
Five canonical lenses, each tuned to a different lie-class. For a load-bearing claim the
Prosecutor selects the lenses *applicable to the subject_type* (§3.6) and spawns one
independent skeptic per selected lens.

### 3.1 Lens A — RE-QUERY (orthogonal aggregation)
Recompute the claimed value by a **different aggregation path over the same canonical DB**,
deliberately routed to *not* reuse the producer's query plan or cache.

- *Targets:* L1 (inflated), L3 (dropped field), L7 (kind).
- *Method:* the producer counted via `ingest.py`'s in-memory accumulator; the skeptic
  issues an independent `SELECT count(*) … WHERE …` that re-derives from the *persisted
  rows*, plus a **field-fill cross-tab** (`count(*) FILTER (WHERE price IS NOT NULL)`) and
  a **kind-distribution** (`GROUP BY kind`). A claim of "4128 dealers" with a re-query of
  4128 but 41% `price IS NULL` triggers an L3 hard-refute on the *inventory* sub-claim.
- *Why independent:* differs on tool (SQL vs Python accumulator) and code-path; same
  source/snapshot — so this lens alone is **not** sufficient (it shares the snapshot,
  cannot catch staleness/fabrication). It must be paired with a live lens. (Encoded in
  the independence gate, §4.)

### 3.2 Lens B — RAW RECOUNT (count from the bytes, not the model)
Recount directly from the **producer's raw evidence bytes** (`evidence_uri`), bypassing
the entire ingest/transform code-path.

- *Targets:* L2 (silent cap), L1 (inflated), L3 (dropped field).
- *Method:* parse the raw JSON-LD / `__NEXT_DATA__` / sitemap the producer captured and
  count **distinct stable ids** independently. If the raw bytes contain 4128 distinct
  `AutoDealer` ids but the DB has 3990, ingest silently dropped 138 (collision/skip) →
  hard-refute. If the raw bytes themselves carry a `numberOfResults: 5000` header while
  only 1000 records are present, that is a **smoking-gun L2 silent cap** — refute with
  the cap value as evidence.
- *Why independent:* differs on tool + code-path; this is the lens that catches the
  *ingest layer lying about its own input*.

### 3.3 Lens C — BLIND LIVE RE-FETCH (different identity, different time)
Re-fetch the claim **live, from the source, through a different network/TLS identity, at a
different time**, with **no knowledge of the producer's snapshot**.

- *Targets:* L4 (staleness), L5 (fabrication), L2 (silent cap that is server-side and
  IP-pinned).
- *Method:* hit the source's own count surface (e.g. AS24 `numberOfResults`, DGT CATV
  `returnCountOnly`, Kia `dealerName` count) from a clean session. This is *exactly the
  owner's §7 hand-verification* (`docs/research/SOURCES_ES.md §7`): agent said 278.163,
  owner's independent curl said **278.329**, Δ+166 → ✓ drift-tolerant pass. [VERIFIED]
  The Inquisition automates that lens. For a *field* claim (a dealer's phone), it
  re-fetches the dealer's page and string-matches the served field against live bytes →
  any mismatch is an L5 fabrication hard-refute.
- *Why independent:* differs on **all four** dimensions (source-fresh, different tool,
  live-not-cached, different path). This is the **gold lens** and the only one that can
  refute staleness and server-side fabrication. A claim that survives Lens C survives the
  hardest test.

### 3.4 Lens D — CROSS-SOURCE CORROBORATION (capture-recapture orthogonality)
Confirm or bound the claim from a **wholly different source** that should independently
witness the same fact.

- *Targets:* L1 (inflated), L6 (coverage gap), L7 (kind), denominator claims.
- *Method:* `docs/research/SOURCES_ES.md §6` is the playbook — DGT CAT (1.292) vs
  DesguacesDirecto (1.386) vs AEDRA (615) bound the desguace count; FACONAUTO (2.018) vs
  Páginas Amarillas (11.202) bound official dealers. A claim "Spain has 1.292 desguaces"
  is corroborated by the *registral DGT* path being orthogonal to the *directory* path.
  For a single entity, corroborate `cif` against BORME, `kind` against the OEM locator
  (an entity in Kia's 242-dealer API list **is** an official Kia dealer — orthogonal
  proof of `kind`).
- *Why independent:* differs on source (the whole point); the capture-recapture estimator
  (§6) lives here.

### 3.5 Lens E — BATCH HASH / DRIFT WITNESS (tamper + churn detection)
Hash the **canonical content of the claimed set** and compare against (a) the producer's
declared hash and (b) the prior verified hash, to detect silent mutation and quantify
churn.

- *Targets:* L4 (staleness — zero churn over many cycles is *suspicious stillness*), L5
  (post-verification tampering), regression detection.
- *Method:* `set_hash = SHA256(sorted(stable_id ‖ price ‖ last_seen-bucket))` over the
  claimed rows. If the producer claims "delta: 12 NEW, 3 GONE" but the set-hash is
  *identical* to last cycle's, the delta is fabricated/empty → refute. Conversely a
  set-hash that changed on 90% of rows when the claim says "3 PRICE_CHANGE" reveals an
  un-emitted-event L3 lie.
- *Why independent:* a pure function of persisted bytes, computed by a different code-path;
  catches the *delta* and *event-stream* lies the count-quorum is blind to.

### 3.6 Lens-to-subject routing matrix [decision table]

| subject_type | A re-query | B raw recount | C live re-fetch | D cross-source | E batch hash | min skeptics |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `count` (per geo/source) | ✓ | ✓ | ✓ | ✓ | ◦ | 3 (must incl. C) |
| `inventory` (entity stock) | ✓ | ✓ | ✓ | ◦ | ✓ | 3 (must incl. C) |
| `entity_field` (cif/phone/kind) | ◦ | ✓ | ✓ | ✓ | — | 2 (must incl. C **or** D live) |
| `coverage` / `denominator` | ✓ | — | ◦ | ✓ | — | 2 (D mandatory) |
| `delta` (NEW/GONE/Δprice) | ✓ | ◦ | ✓ | — | ✓ | 3 (E mandatory) |
| `kind` (L7) | ✓ | — | ◦ | ✓ | — | 2 (D mandatory) |

✓ = mandatory · ◦ = optional/escalation · — = not applicable.
**Hard rule:** every load-bearing claim's skeptic set must include **at least one lens
that differs on all four producer-state dimensions** (in practice, Lens C live or Lens D
live). A skeptic set drawn only from A+B (which share the producer's snapshot) is rejected
by the independence gate before any verdict is computed (§4). *This is the formal cure for
L4/L5 — the lies the VAM cannot see.*

---

## 4. Independence — the formal gate (Law II made numeric)

Each skeptic `s` carries a state tuple `St(s) = ⟨source, tool, cache, path⟩`. Define the
**independence distance** between skeptic and producer:

```
D(s, P) = Σ_{d ∈ {source, tool, cache, path}} 𝟙[ St(s).d ≠ St(P).d ]      (∈ {0,1,2,3,4})
```

**Per-skeptic admission gate:** a skeptic is admitted iff `D(s, P) ≥ 2`. (`D=0` is the
producer; `D=1` is a near-clone — e.g. same source+snapshot, only a different SQL phrasing
— too weak to break a shared blind spot.)

**Mutual independence within the quorum** (skeptics must also be orthogonal to *each
other*, else two skeptics sharing a blind spot are a single witness counted twice). For
skeptics `s_i, s_j` define `D(s_i, s_j)` the same way; require:

```
∀ asserting pair (s_i, s_j) used for quorum:  D(s_i, s_j) ≥ 2
```

**Quorum-set independence score** (the number persisted on the verdict):

```
INDEP = min over all asserting pairs ( D(s_i, s_j) )           # weakest link in the agreeing set
```

A claim may only reach `TRUSTWORTHY` when `INDEP ≥ 2`. Worked example:

> Producer `P = ⟨autoscout24, curl_cffi, snap_T0, ingest⟩` claims **4128**.
> - `s1` (Lens A) `= ⟨autoscout24, sql, snap_T0, recount.sql⟩` → `D(s1,P)=2` ✓ admitted.
> - `s2` (Lens C) `= ⟨autoscout24-LIVE, browser, live_T1, live_count⟩` → `D(s2,P)=3` ✓
>   (source counts as "different" because it is the live surface, not the cached snapshot;
>   tool, cache, path all differ).
> - `s3` (Lens D) `= ⟨coches.net, curl_cffi, live_T1, xsrc⟩` → `D(s3,P)=3` ✓ (different
>   source; note tool matches producer → only 3, still ≥2).
> - Mutual: `D(s1,s2)=4`, `D(s1,s3)=3` (diff source+cache+path), `D(s2,s3)=2` (same cache
>   bucket live_T1 and… source differs, tool differs, path differs → actually 3). Weakest
>   agreeing pair ≥2 → `INDEP = 2`. **Gate passes.**
>
> Counter-example that the gate **kills**: a producer that "verifies" 4128 by re-running
> `ingest.py` twice on the same snapshot → both skeptics have `D=0` → `INDEP` undefined →
> **auto-REFUTED with reason `NO_INDEPENDENT_PATH`.** This is the single most common way
> agents fake verification, and the gate makes it structurally impossible to pass.

---

## 5. The assert-vs-refute protocol & quorum math

### 5.1 Per-skeptic verdict
Each skeptic returns one of `{ASSERT(v, conf), REFUTE_SOFT(v, reason), REFUTE_HARD(reason),
ABSTAIN(reason)}` where `v` is the value it independently measured.

- **ASSERT(v)** iff its measured `v` matches `asserted_value` within the claim's
  `tolerance` (§5.2). Carries a confidence `conf ∈ [0,1]` from lens reliability × source
  health.
- **REFUTE_SOFT(v)** — measured a *different but plausible* value (e.g. drift beyond
  tolerance, or a count that diverges but both are internally consistent). A divergence,
  not a contradiction.
- **REFUTE_HARD** — found a *contradiction of bytes*: a silent cap header (L2), a
  served field absent from live source bytes (L5 fabrication), a raw-vs-DB id mismatch
  (L3 drop), a stale `last_seen` past the freshness SLA (L4). Hard refutations **veto**
  (§5.4).
- **ABSTAIN** — could not measure (source down, parse fail). **Per Law I, an ABSTAIN on a
  load-bearing claim counts as REFUTE for the quorum** (default-refuted); it is recorded
  separately so the Manager can route to `research` rather than `fix`.

### 5.2 Tolerance model (drift-aware, lie-intolerant)
Live counters drift; the protocol must pass honest drift and kill dishonest gaps. Two
tolerance regimes by subject:

```
EXACT subjects   (registral/official: DGT CAT, OEM locator counts, cif, kind):
    tol = 0        — any deviation is a refutation. DGT 1292 vs 1292 → ASSERT; 1292 vs 1290 → REFUTE.

DRIFT subjects   (live platform inventory counts):
    relative tolerance with a floor:
        tol(v) = max( τ_rel · v , τ_abs )
    defaults [ASSUMED, calibrate from §7 owner data]:  τ_rel = 0.005 (0.5%),  τ_abs = 50
```

Worked, from the owner's real §7 numbers [VERIFIED]:
> AS24 agent=278.163, live=278.329, Δ=166. `tol = max(0.005·278329, 50) = max(1391,50) =
> 1391`. `|166| ≤ 1391` → **ASSERT** (honest drift). ✓ — matches the owner's manual ✓.
> coches.net agent=248.920, live=249.139, Δ=219, `tol = max(1245,50)=1245`, `219 ≤ 1245`
> → ASSERT ✓. A *fabricated* claim of 350.000 against live 278.329: `Δ=71.671 ≫ 1391` →
> **REFUTE_SOFT** with measured 278.329 as the counter-value.

> **Cap-aware refinement (kills L2 that drift-tolerance would otherwise hide):** if a
> DRIFT count lands suspiciously *exactly* on a known pagination cap (1000, 2000) AND the
> raw bytes (Lens B) expose a larger `numberOfResults`, escalate from ASSERT to
> **REFUTE_HARD(silent_cap)** regardless of tolerance. Tolerance never excuses a cap.

### 5.3 Soft vs hard — why the distinction is load-bearing
- A **soft** refutation is a *disagreement about a value* → the quorum decides by count
  (§5.4). Two honest paths can soft-disagree on a drifting counter without either lying.
- A **hard** refutation is *proof of a lie* (bytes contradict the claim) → it **vetoes**.
  One credible hard refutation kills the claim even against a unanimous ASSERT majority,
  because a contradiction of source bytes cannot coexist with a true claim. (A hard
  refutation is itself re-checkable: if challenged, it must be reproducible by a second
  independent skeptic before it vetoes — see §5.5 false-veto guard.)

### 5.4 Quorum decision function (the authoritative rule)

```
Inputs (over admitted, mutually-independent skeptics only):
  A    = multiset of ASSERT values
  Rs   = count of REFUTE_SOFT
  Rh   = count of credible REFUTE_HARD (post false-veto guard, §5.5)
  Ab   = count of ABSTAIN (already folded into "refute" for quorum, kept for routing)
  INDEP = quorum-set independence score (§4)

Decision:
  1. if Rh ≥ 1                          → REFUTED   (hard veto; reason = the hard finding)
  2. if INDEP < 2                       → REFUTED   (reason = NO_INDEPENDENT_PATH)
  3. let (v*, n*) = modal ASSERT value and its support
     let rival     = ∃ v ≠ v* with ≥2 ASSERTs   (a competing quorum)
  4. if n* ≥ 2 and not rival and (Rs + Ab) < n*   → TRUSTWORTHY   (value = v*)
  5. if rival OR (Rs + Ab) ≥ n*         → REFUTED   (majority-refute / split quorum kills)
  6. else                              → INCONCLUSIVE (1 assert, no independent second; re-queue)
```

Rule 4 generalizes `verify.py`'s "modal value supported by ≥2, no rival, primary agrees":
here the *primary/producer is excluded entirely* and the agreement must come from ≥2
**independent skeptics**, and the asserting majority must *exceed* the combined
soft-refute + abstain mass (so a 2-assert / 2-refute tie does **not** pass — it is a split
quorum, killed by Rule 5; this is stricter than the VAM, by design).

### 5.5 False-veto guard (a skeptic can lie too)
A `REFUTE_HARD` is powerful enough to be a denial-of-service or an honest skeptic error.
Guard: a hard refutation **vetoes only if reproduced by a second independent skeptic**
(`D ≥ 2` from the first refuter) OR if it is byte-deterministic (a cap header, a
checksum mismatch — facts that cannot be wrong). A lone, non-deterministic hard refutation
demotes the verdict to `INCONCLUSIVE` and re-queues with an extra skeptic, rather than
silently killing a possibly-true claim. **The Inquisition distrusts its own inquisitors.**

### 5.6 Worked end-to-end example (a coverage claim, the hardest class)

> **Claim:** "CARDEEP serves 100% of desguaces (CAT) in Spain — 1.292 entities."
> Producer `P = ⟨dgt_catv, curl_cffi, snap_T0, ingest⟩`, subject_type=`coverage`, EXACT.
>
> Lenses selected (§3.6 coverage row): A re-query (✓), D cross-source (mandatory).
> - **s1 Lens A** (`sql, snap_T0`): `SELECT count(*) FROM entity WHERE kind='desguace'` →
>   **1.292**. `D(s1,P)=2`. ASSERT(1292).
> - **s2 Lens C live** (`dgt_catv-LIVE, curl_cffi, live_T1`): DGT CATV `returnCountOnly`
>   → **1.292** (the owner's §7 exact match, Δ=0). `D=3`. ASSERT(1292).
> - **s3 Lens D** (`desguacesdirecto, browser, live`): independent directory → **1.386**.
>   `D=3`. This is the capture-recapture witness. 1386 ≠ 1292 (EXACT) → REFUTE_SOFT(1386).
> - **s4 Lens D** (`aedra, curl_cffi, live`): → **615**. REFUTE_SOFT(615).
>
> Quorum: A = {1292, 1292}, Rs = 2 (1386, 615 — both *higher floors/partials*, not
> contradictions of the DGT official count), Rh = 0, INDEP = 2.
> Modal v*=1292, n*=2, no rival quorum (1386 and 615 each have support 1). But
> `(Rs+Ab)=2 ≥ n*=2` → **Rule 5: REFUTED as a coverage claim.** ✓ **Correct** — and this
> is the deep point: the *count* of 1.292 ingested entities is TRUSTWORTHY (matches DGT
> official, §7), but the **coverage claim "100%"** is **REFUTED** because the cross-source
> witnesses prove the denominator is contested (DesguacesDirecto sees 1.386). The
> Inquisition splits the trustworthy count from the dishonest coverage claim — exactly
> "better to confess a gap than sell a lie." The Manager routes this to `research`
> (reconcile the 94 extra DesguacesDirecto fichas: closed CATs? unofficial? new?), not to
> `fix`. The served API answer becomes *"1.292 official CAT registered (DGT); directory
> sources see up to 1.386 — 94 under reconciliation"* — a confessed bound, never a lie.

---

## 6. The denominator problem — bounding "100%" (kills L6 with statistics)

The single hardest CARDEEP claim is *"we have 100%."* You cannot verify a coverage
fraction without an independent estimate of the denominator `N` (true number of entities).
The Inquisition bounds `N` with the **Chapman capture-recapture estimator** over orthogonal
sources (`docs/research/SOURCES_ES.md §6` already mandates this for F8) [VERIFIED].

For two independent sources A, B with sizes `|A|`, `|B|` and overlap `m = |A ∩ B|`
(matched via `cdp_code` identity, §ARCHITECTURE):

```
N̂_Chapman = ((|A|+1)(|B|+1) / (m+1)) − 1

Var(N̂)    = ((|A|+1)(|B|+1)(|A|−m)(|B|−m)) / ((m+1)²(m+2))
95% CI    = N̂ ± 1.96·√Var
```

Worked, desguaces, using census numbers [VERIFIED |A|,|B| from SOURCES_ES.md §6]:
> A = DGT CAT = 1.292, B = DesguacesDirecto = 1.386. Suppose identity-match overlap
> `m = 1.180` [ASSUMED — to be computed by `cdp_code` join, illustrative].
> `N̂ = (1293·1387/1181) − 1 ≈ 1.518.6 − 1 ≈ 1.518`. So the *true* desguace universe is
> ~1.518, not 1.292. **Coverage of a 1.292-row DB = 1292/1518 ≈ 85%, not 100%.**
> The Inquisition therefore *caps every coverage claim at `served / N̂_lower`* and refuses
> any "100%" assertion whose `N̂` CI excludes the served count.

**Coverage verdict rule:**
```
coverage_fraction = served_verified / N̂_lower95
COVERAGE_TRUSTWORTHY   iff  the *claimed* fraction ≤ coverage_fraction AND skeptics agree on served
COVERAGE_REFUTED        iff  claim asserts a fraction the denominator estimate cannot support
```
Three+ sources use the log-linear / Lincoln-Petersen extension (`N̂` via the multi-source
model); the design requires **≥3 orthogonal sources before any "100%" claim is even
eligible** for TRUSTWORTHY — two sources can only ever yield a *bound*, never a certified
total. This is the formal reason the census already says coverage "se cierra de verdad en
F8" [VERIFIED, SOURCES_ES.md §6].

---

## 7. The Manager Router — detection → action

Every Inquisition verdict that is not clean-`TRUSTWORTHY` is routed by the Manager to
exactly one of four actions. Routing is **deterministic on the verdict's reason code**, so
the same lie always routes the same way (auditable, no agent discretion):

| Verdict / reason | Lie class | Action | What it does |
|---|---|---|---|
| `REFUTED:raw_vs_db_mismatch` | L3 drop | **fix** | Re-run ingest for the subject; file `alert(origin=source_key, sev=critical)`; the drop is a *code* bug. |
| `REFUTED:silent_cap` | L2 | **fix** | Trigger facet-partition harvest (02-SCRAPING-ENGINE §7) to drain under the cap; re-claim. |
| `REFUTED:fabrication` | L5 | **quarantine** | Move the row to `quarantine` (not served), strip the fabricated field, `alert(sev=critical)`; never auto-fixable. |
| `REFUTED:stale` | L4 | **fix** | Force a fresh harvest of the subject; if source is `down` in `source_health`, escalate. |
| `REFUTED:coverage` / denominator | L6 | **research** | Open a denominator-reconciliation task (find the missing tail via §6 capture-recapture); serve a *confessed bound*, never 100%. |
| `REFUTED:kind_contradiction` | L7 | **fix** | Re-classify via the OEM-locator / cross-source `kind` proof (Lens D); patch `ingest.py:52` mis-type. |
| `INCONCLUSIVE:no_independent_second` | — | **escalate** | Re-queue with +1 skeptic of a new lens; after K=3 re-queues, escalate to human (`alert(sev=warning)`). |
| `REFUTED:no_independent_path` | — | **escalate** | The verification itself was non-independent → process bug; alert engineering. |

The router writes to the **existing** `alert` table (`migrations/0004`, `origin` =
exact source_key / cdp_code) and updates `source_health` — no new alerting machinery,
the Inquisition reuses the repo's resilience layer [VERIFIED schema].

> **Confession over lying (the prime directive made operational):** any subject with an
> open `REFUTED:coverage` or `quarantine` row causes the API layer to serve the value
> **with an explicit caveat** (`meta.verification = {verdict, bound, under_reconciliation}`),
> never the bare number. A consumer of CARDEEP can always distinguish a `TRUSTWORTHY`
> value from a *confessed bound*. This is enforced at the API envelope (`{ok, data, error,
> meta}`, ARCHITECTURE.md §API) — the Inquisition verdict rides in `meta`.

---

## 8. Persistence — schema the Inquisition needs (additive to `migrations/0004`)

Proposed `migrations/0005_inquisition.sql` (additive, idempotent, reversible — same
doctrine as existing migrations [VERIFIED pattern, ARCHITECTURE.md]). Design spec, not yet
in repo:

```sql
-- Claims entering the Inquisition (producer-emitted)
CREATE TABLE IF NOT EXISTS inquisition_claim (
    claim_id        TEXT PRIMARY KEY,                 -- ULID
    subject_type    TEXT NOT NULL,                    -- count|entity_field|inventory|coverage|kind|delta|denominator
    subject_key     TEXT NOT NULL,
    claim           TEXT NOT NULL,
    asserted_value  TEXT,
    producer_state  JSONB NOT NULL,                   -- ⟨source,tool,snapshot,code_path⟩ for Law II
    load_bearing    BOOLEAN NOT NULL DEFAULT TRUE,
    tolerance       DOUBLE PRECISION NOT NULL DEFAULT 0.005,
    evidence_uri    TEXT,
    status          TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING','PROSECUTING','DECIDED')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One row per skeptic (the audit trail of who tested what, independently)
CREATE TABLE IF NOT EXISTS inquisition_skeptic (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    claim_id        TEXT NOT NULL REFERENCES inquisition_claim(claim_id) ON DELETE CASCADE,
    lens            TEXT NOT NULL CHECK (lens IN ('A_requery','B_raw_recount','C_live_refetch','D_cross_source','E_batch_hash')),
    skeptic_state   JSONB NOT NULL,                   -- its ⟨source,tool,cache,path⟩
    indep_distance  INT NOT NULL,                     -- D(s,P) ∈ 0..4
    measured_value  TEXT,
    verdict         TEXT NOT NULL CHECK (verdict IN ('ASSERT','REFUTE_SOFT','REFUTE_HARD','ABSTAIN')),
    confidence      DOUBLE PRECISION,
    reason          TEXT,
    evidence        JSONB,                            -- bytes/headers that justify the verdict
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_skeptic_claim ON inquisition_skeptic (claim_id);

-- The Inquisition's authoritative verdict (supersedes the VAM's verification_verdict for load-bearing claims)
CREATE TABLE IF NOT EXISTS inquisition_verdict (
    claim_id        TEXT PRIMARY KEY REFERENCES inquisition_claim(claim_id) ON DELETE CASCADE,
    verdict         TEXT NOT NULL
        CHECK (verdict IN ('TRUSTWORTHY','REFUTED','INCONCLUSIVE','QUARANTINED')),
    decided_value   TEXT,
    indep_score     INT NOT NULL,                     -- INDEP (§4); must be ≥2 for TRUSTWORTHY
    assert_n        INT NOT NULL DEFAULT 0,
    refute_soft_n   INT NOT NULL DEFAULT 0,
    refute_hard_n   INT NOT NULL DEFAULT 0,
    abstain_n       INT NOT NULL DEFAULT 0,
    reason_code     TEXT,                             -- routes the Manager (§7)
    denom_estimate  DOUBLE PRECISION,                 -- N̂ for coverage claims (§6)
    denom_ci_low    DOUBLE PRECISION,
    routed_action   TEXT CHECK (routed_action IN ('fix','research','quarantine','escalate','none')),
    decided_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- A TRUSTWORTHY verdict is only valid with an independent quorum:
    CONSTRAINT trustworthy_needs_independence
        CHECK (verdict <> 'TRUSTWORTHY' OR (indep_score >= 2 AND assert_n >= 2 AND refute_hard_n = 0))
);
CREATE INDEX IF NOT EXISTS idx_inq_verdict ON inquisition_verdict (verdict);
CREATE INDEX IF NOT EXISTS idx_inq_routed ON inquisition_verdict (routed_action) WHERE routed_action <> 'none';

-- Rollback:
-- DROP TABLE IF EXISTS inquisition_verdict;
-- DROP TABLE IF EXISTS inquisition_skeptic;
-- DROP TABLE IF EXISTS inquisition_claim;
```

> The `CONSTRAINT trustworthy_needs_independence` makes Law II + Law III a **database
> invariant**: it is physically impossible to persist a `TRUSTWORTHY` verdict without ≥2
> asserting skeptics, an independence score ≥2, and zero un-vetoed hard refutations. The
> lie cannot be written even by a buggy prosecutor. The read-only `cardeep_inquisitor`
> role (§2) writes these three tables; the producer roles have no grant on them.

---

## 9. Relationship to the VAM (`pipeline/verify.py`) — supersession map

| Concern | VAM (`verify.py`, today) [VERIFIED] | Inquisition (this doc) |
|---|---|---|
| Default posture | Optimistic (TRUSTWORTHY if modal ≥2) | Pessimistic (default REFUTED, Law I) |
| Who verifies | Producer-supplied `paths` dict | Separate read-only process, producer-excluded (Law II) |
| Independence | Implicit ("orthogonal paths" by convention) | Numeric gate `INDEP ≥ 2`, DB-enforced (§4, §8) |
| Lenses | Count-only | Five orthogonal lenses incl. live re-fetch (§3) |
| Lie coverage | L1 partial (count agreement) | L1–L7 all (§0) |
| Staleness / fabrication | Blind | Lens C live re-fetch + Lens E hash (§3.3, §3.5) |
| Denominator / 100% | Not modeled | Chapman capture-recapture bound (§6) |
| Hard contradiction | None | `REFUTE_HARD` veto + false-veto guard (§5.3, §5.5) |
| Action on failure | Writes verdict only | Manager router → fix/research/quarantine/escalate (§7) |

**Migration of behavior:** `record_count_verdict` remains the **fast producer-side
pre-check** (a cheap optimistic quorum to catch gross errors early). Every claim it marks
`TRUSTWORTHY` is then **re-prosecuted by the Inquisition** before that value is served as
verified; the Inquisition's `inquisition_verdict` is authoritative and can *downgrade* a
VAM-`TRUSTWORTHY` to `REFUTED` (e.g. when Lens C reveals staleness the count-quorum could
never see). The VAM verdict is an opinion; the Inquisition verdict is the ruling.

---

## 10. What this design guarantees (and what it honestly does not)

**Guarantees [by construction]:**
- No load-bearing value is served as *verified* unless ≥2 mutually-independent lenses
  (one of which differs on all four producer dimensions) asserted it AND no un-vetoed hard
  contradiction exists — enforced as a DB invariant (§8).
- Every lie-class L1–L7 has a dedicated lens that can refute it (§0, §3.6 matrix).
- "100%" coverage is mathematically un-assertable without ≥3 orthogonal sources and a
  Chapman denominator whose CI supports the claim (§6).
- A refuted claim never silently disappears — it serves as a *confessed bound* with a
  `meta.verification` caveat, and is deterministically routed to an action (§7).

**Honest limits [ASSUMED / out of scope here]:**
- The read-only `cardeep_inquisitor` DB role, the separate-egress network identity for
  Lens C, and `migrations/0005` are **design requirements not yet in the repo**; they
  must be implemented for the independence guarantees to be physical rather than
  procedural.
- Chapman assumes source independence and a closed population; real sources have
  correlated coverage (PA and OSM both miss rural long-tail). The estimator yields a
  *defensible lower bound*, not a proven truth — which is exactly why the design **refuses
  "100%" and serves a bound** rather than over-claiming.
- Lens C live re-fetch costs real requests against defended sources; the Inquisition runs
  it on a *sampled cadence* for high-volume drift subjects and on *every* registral/EXACT
  and field-fabrication claim. Sampling rate is a calibration parameter, not yet measured.

> The Inquisition's final promise is the project's first principle, made structural:
> **CARDEEP confesses every gap it cannot close and refuses to serve a single number it
> cannot prove by a path other than the one that made it.**
