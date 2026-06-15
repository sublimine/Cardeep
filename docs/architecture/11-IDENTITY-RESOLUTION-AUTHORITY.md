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
| **particular province-split** (same 8-char cdp suffix, different province prefix → one human as N codes) | 703 still split in the served view | 703 | **DEFER merge** |

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

## In-schema note

`v_resolved_dealer` is β-only and has **zero code consumers** — it is NOT the served resolver. The β data
lives in `entity_resolution` (the table) and remains available for the deferred composition above. Do not
wire `v_resolved_dealer` into any serving path; use `v_dealer_resolved`.
