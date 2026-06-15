# ADR — Dealer-identity resolution: authority + deferred compositions

> Audit P2 findings B-beta-resolver-dormant, B-particular-province-split, B-crosssource-dedup-ungated.
> Director decision record. Date: 2026-06-15.

## Authoritative served resolver

**`v_dealer_resolved` is THE authoritative dealer-identity resolver** consumed by `resolve_cluster`
(`services/api/deps.py`) and every entity/inventory endpoint. It composes two VAM-verified layers:

```
entity → B1  (v_canonical, run 'dealer-identity-det-v1', vam_verified=TRUE)
       → dedup (canonical_dedup, run 'canonical-dedup-deeplink-v1', vam_verified=TRUE, 2,385 merges,
                deep-link-evidence-backed)
       → resolved_cdp_code (the super-canonical)
```

This chain works because `canonical_dedup` is built ON TOP of B1's output (same cdp_code space), so the
2-layer COALESCE in the view is a correct composition.

## Parallel signals NOT composed into the served identity (and why)

| Signal | Status | Net-new merges vs served | Decision |
|---|---|---|---|
| **β — `entity_resolution`** (run `entity-resolution-fingerprint-v1`, vam_verified=TRUE, 20,951 merges; exposed by the dead view `v_resolved_dealer`, 0 consumers) | computed, sealed, **NOT served** | ~388 pairs | **DEFER composition** |
| **cross-source — `cross-source-dedup-v1`** (OSM × digital, vam_verified=**FALSE**, 688 merges) | computed, **NOT certified** | ~13 genuine | **DEFER certification** |
| **particular province-split** (same 8-char cdp suffix, different province prefix → one human as N codes) | ~~703 still split~~ → **SERVED** (706 collapsed, verdict 1423) | 706 | **DONE 2026-06-15 (cont.)** — see Update below |

### Rationale (Director, "lo mejor para el negocio")

1. **β-composition is a high-risk CORE-view rebuild for a ~1% gain.** β is fingerprint-based and
   *independent* of B1∘dedup — it is NOT built on their output, so composing it correctly is NOT a 3rd
   COALESCE layer but a **union-find transitive closure** over `{B1 edges, dedup edges, β edges}`. That
   rebuild changes `v_dealer_resolved`, which the WHOLE API + `resolve_cluster` consume — a subtle
   closure error (cycle, wrong canonical pick) would mis-merge real dealers in ways that pass spot-checks
   but corrupt at scale. **388 net-new merges (~1% of 38,555 dealers) does not justify risking the served
   dealer identity** ("código único por dealer" is the product's core promise).

2. **Merge certification is the Inquisitor's highest-stakes act.** Flipping `cross-source-dedup-v1` to
   `vam_verified=TRUE`, or merging the 703 particulares, makes those merges SERVED. A false-positive
   (two distinct dealers shown as one) corrupts the product core. Cross-source merges (OSM × digital)
   have NO deep_link — they rest on name+geo similarity, which needs **rigorous per-merge review** before
   certification. The doctrine is explicit: *"no dejar pasar ni un dato sin probar; mejor confesar un
   hueco que vender una mentira."* Certifying merges without that review would be selling a lie.

3. **None of these are service-breaking.** The served data already dedups via the authoritative chain;
   these would dedup ~1-2% MORE. They are *completeness* gains, not defect fixes — exactly the work the
   doctrine says to do *"una vez impecable, sin prisa"*, not rushed.

## When/how to execute (deliberate, fresh-context work)

- **β-composition:** rebuild `v_dealer_resolved` as a union-find closure over all VAM-verified merge
  edge-sets (B1, canonical_dedup, entity_resolution). Verify: 0 cycles, every member resolves to one
  canonical, counts sane; regression-test `resolve_cluster` + `/entities` + `/stats` before commit.
- **cross-source certification:** review each merge's name+geo+evidence; certify ONLY the evidence-backed
  ones (set `vam_verified=TRUE` on the run, or split-certify the genuine subset). Reject any fuzzy match.
- **particular-split:** extend the dedup over same-suffix-cross-province particulares using the deep-link
  signal that already proved 139/843; never merge on suffix alone.

## Update 2026-06-15 (cont.) — particular-split DE-RISKED by the canonical_key backfill

The original deferral rested on the missing safe discriminator: the 8-char cdp suffix alone (~40 bits)
can collide at 370k particulares, so merging on suffix was unsafe, and deep_link evidence only covered
139/843 groups. **That blocker is now removed.** This session's `entity.canonical_key` backfill (audit
P2 B-canonical-key) populated the literal pre-image `particular:{platform}:{seller_id}` for particulares,
re-hash-gated (written only when it re-hashes to the stored cdp_code → verified correct, never guessed).

`canonical_key` is a **definitive** same-seller key — it IS the platform's own unique user id, not a
hash, so it cannot collide. Grouping particulares by `canonical_key` (verified on live DB) yields exactly
**843 groups / 1,689 entities / 846 implied merges, 100% multi-province** — matching the audit's split
count. Same canonical_key ⟺ same platform seller account ⟺ same human, with zero false-positive risk
(stronger than the partial deep_link signal). This is precisely "evidence-backed, never suffix-alone".

**EXECUTED 2026-06-15 (cont.) — built, verified, gated, SERVED.** (`scripts/build_particular_dedup.py`
+ `scripts/gate_particular_dedup.py`)
1. Built run `particular-canonkey-v1` = a verbatim copy of the served run (`canonical-dedup-deeplink-v1`,
   dealers + 139 deep_link particular merges + the 2 cross-kind groups preserved) + 1,409 added rows
   mapping every still-split particular to a per-`canonical_key` representative (case A 703 / case B 140
   / case C 0). Started `vam_verified=FALSE` → inert.
2. Verified on live DB: **0 key_mismatch** (all 1,409 added pairs map particular→super sharing one
   `canonical_key`), **0 super-not-particular**, **0 orphan super**, **0 null resolved**; dealer rows
   byte-identical to the served run; v_dealer_resolved simulation = 369,561 distinct identities (706
   particular splits collapsed). resolve/cluster/canonical/dedup suite green pre- and post-gate.
3. Gated `vam_verified=TRUE` with TRUSTWORTHY verdict 1423 (quorum_n/family_n/origin_n = 2/2/2: the
   served count 369,561 confirmed by two independent paths). v_dealer_resolved now serves 369,561
   (was 370,267); `/stats.dealers` is unchanged (it excludes particulares, kind<>'particular'=40,016).
   **Reversible:** `gate_particular_dedup.py --revert` flips it back.

The discriminator was definitive (canonical_key, collision-free) so this carried zero false-positive
risk. β-composition and cross-source certification **remain deferred** — and a fresh investigation this
turn shows WHY they are NOT like particular-split:

- **particular-split was uniquely safe** = definitive discriminator (canonical_key) **AND a disjoint,
  additive mechanism** (each canonical_key group is independent; merges never chain with the dealer
  graph — verified: 843 groups, case-C cross-kind = 0). So it composed as pure INSERTs into
  canonical_dedup with zero union-find. Value was meaningful (706 humans).
- **cross-source** (`pipeline/identity/cross_source_dedup.py` → `entity_cluster` run, vam_verified=FALSE)
  HAS a hard-ID safe subset (Signal A phone fp≈0% + Signal B domain), so the *discriminator* problem is
  solvable. But its edges connect **distinct B1 super-canonicals** (OSM↔digital pairs B1 never merged),
  so serving them needs a **union-find closure** over {B1, canonical_dedup, cross-source} edges — NOT
  additive — for only **~13 genuine dealers (0.03% of 40,016)**. Risk (closure rebuild of the served
  view) ≫ value. Deferral confirmed.
- **β-composition** is the same union-find-rebuild class (388 merges ≈ 1%); fingerprint/Jaccard edges,
  independent of B1∘dedup. Same mechanism risk, modest value.

The line: do the merge when it is BOTH evidence-definitive AND mechanically additive (particular-split
was). When serving requires a transitive-closure rebuild of the core view for a sub-1% gain, the doctrine
("una vez impecable, sin prisa; no certificar sin probar") says defer to a focused, fully-regression-
tested rebuild — not bolt it on. The hard-ID subsets are pre-identified for that future build.

**Edge case (verified + handled):** the served run merges particulares and dealers in **2 cross-kind
super-canonical groups** (a particular sharing a deep_link with a dealer). These 2 are NOT in the 843
canonical_key split-groups (their particulares are canonical_key-singletons, not province-split), so the
build's case-C guard left them untouched (case C = 0 triggered) and the verbatim copy preserved them.
They remain a known follow-up for kind re-classification review — NOT corrupted by this merge.

## In-schema note

`v_resolved_dealer` is β-only and has **zero code consumers** — it is NOT the served resolver. The β data
lives in `entity_resolution` (the table) and remains available for the deferred composition above. Do not
wire `v_resolved_dealer` into any serving path; use `v_dealer_resolved`.
