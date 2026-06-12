# T11 — Perceptual Image Hashing / Photo-Delta Detection Audit

> Domain: Perceptual image hashing for photo-delta detection — detecting
> near-duplicate / re-listed / VIN-swapped vehicle photos across sources, and
> tracking photo changes in the live delta. Robustness to JPEG re-encode,
> watermark, crop, resize; speed at fleet scale.
> Candidates audited: **goimagehash** (CARDEEP's current choice) ·
> **ajdnik/imghash** (Go) · **JohannesBuchner/ImageHash** (Python) ·
> **Facebook PDQ / python-threatexchange** · **blockhash** ·
> **CLIP / SSCD / DinoHash embeddings** · **imagededup**.
> Audit date: **2026-06-12**. All recency claims fetched live this date.
> Anti-hallucination: every claim tagged `[VERIFIED]` (I fetched the repo/page/API)
> or `[ASSUMED]` (inference, not directly read). Source URLs inline.

---

## TL;DR — Verdict

**CARDEEP already runs perceptual hashing today.** Validator `V16` in
`quality/internal/validator/v16_photo_phash/v16.go` downloads each photo, computes
a **64-bit pHash via `github.com/corona10/goimagehash`** (`PerceptionHash`), and
flags near-duplicates at **Hamming distance ≤ 4 / 64** against a SQLite hash store.
`[VERIFIED]` — read the source file.

The **strategy is correct** (perceptual hash as a fast first-pass dedup/fraud
signal is exactly right for fleet scale). The **tool underneath is stale**:
`goimagehash` last shipped a release in **May 2022** and last committed **Jan
2024** — ~2.4 years cold, single algorithm (DCT pHash + aHash only), no PDQ. It is
not dead, but it is frozen, and 64-bit pHash @ Hamming≤4 is brittle to the exact
transformations dealers use to disguise re-listings (crop, watermark, text overlay).

| Decision | Pick |
|---|---|
| **Primary hash (replace goimagehash)** | **`ajdnik/imghash` v2.5.2 (pure Go, PDQ default)** — last commit **2026-06-09** |
| **Fallback / cross-check** | **Facebook PDQ via `python-threatexchange` 1.2.16** (canonical reference, FAISS index) |
| **Heavy-hitter for hard adversarial cases** | **DinoHash (ICML 2025)** or **CLIP/SigLIP embeddings** as a second-stage re-rank on flagged pairs only |
| **Python turnkey alternative** | `JohannesBuchner/ImageHash` 4.3.2 (alive) + `imagededup` 5.6k★ (alive) |
| **DEAD — do not adopt** | **SSCD** (archived Aug 2022), **MTRNord/pdqhash-go** (0★, dead), **blockhash-python** (no push since Oct 2023) |

**Bottom line:** CARDEEP's current `goimagehash` choice is *good enough to run* but
*not good enough to be best*. Swap the hasher to **`ajdnik/imghash` with PDQ**
(pure Go, drop-in, no cgo, actively maintained, 256-bit PDQ ≫ 64-bit pHash on
robustness) and keep the exact same V16 store/threshold architecture.

---

## Why pHash@64bit/Hamming≤4 is the weak link (the problem statement)

CARDEEP's fraud signal is "same photo re-listed under a different vehicle." Dealers
defeat naive pHash by re-encoding, adding a dealer watermark/plate-blur, cropping
the frame, or overlaying price text. Verified robustness profile of classical
perceptual hashes:

- **pHash / dHash handle minor edits well** (resize, JPEG recompression, small
  brightness shifts) but **degrade sharply on crop, rotation, mirroring, and
  heavy stylization**. Source: arXiv *State of the Art: Image Hashing* and
  *Hamming Distributions of Popular Perceptual Hashing Techniques*
  (https://arxiv.org/pdf/2108.11794, https://arxiv.org/pdf/2212.08035) `[VERIFIED]`
  (read search abstracts; full PDF was binary-unreadable — robustness *direction*
  is `[VERIFIED]`, exact per-transform Hamming figures `[ASSUMED]`).
- Industry comparison: perceptual hashing achieves **~25% recall on heavily
  modified images** vs **~67% recall for AI fingerprinting (SSCD/DinoHash)**.
  Source: https://www.scoredetect.com/blog/posts/content-fingerprinting-ai-vs-perceptual-hashing `[VERIFIED]`
- 2025/2026 academic consensus: perceptual hashes are excellent for *exact /
  near-exact* dedup but "drastically deteriorate in near-duplicate and transformed
  scenarios"; deep embeddings win on crops/overlays/screenshots at a speed/cost
  premium. Source: MDPI *Electronics* 15(7):1493, 2026
  (https://www.mdpi.com/2079-9292/15/7/1493) `[VERIFIED]` (abstract + finding read
  via search; full HTML returned HTTP 403, so exact accuracy tables are `[ASSUMED]`).

The takeaway: **upgrade the hash from 64-bit pHash to 256-bit PDQ** (cheap, same
class of tool, big robustness gain), and **reserve embeddings for a narrow
second stage** on already-flagged pairs (keeps cost bounded at fleet scale).

---

## Candidate 1 — `ajdnik/imghash` (Go)  ✅ ADOPT (primary, replaces goimagehash)

- **Repo:** https://github.com/ajdnik/imghash
- **Latest tag:** **v2.5.2** `[VERIFIED]` (gh api tags)
- **Last commit:** **2026-06-09** `[VERIFIED]` · **Pushed:** 2026-06-10 `[VERIFIED]`
  — actively maintained, commits within days of this audit.
- **Stars:** 58 `[VERIFIED]` · **Archived:** no `[VERIFIED]` · **Language:** pure Go,
  **no cgo / no OpenCV** `[VERIFIED]` (README states pure-Go, no external deps).

### What it solves
A single pure-Go library exposing **~20 hash families** — PDQ, pHash, dHash,
aHash, median, **block-mean (blockhash)**, wavelet, color, plus research hashes
(Zernike, radial-variance, Marr-Hildreth) and even a **DinoHash** binding.
README explicitly recommends: *"If you're unsure which hash to pick, start with
PDQ."* Source: https://github.com/ajdnik/imghash README `[VERIFIED]`

### Strengths
- **PDQ out of the box, pure Go, no cgo.** This is the single biggest win: PDQ is
  Facebook's hardened 256-bit DCT hash (evolution of pHash) and CARDEEP gets it
  without a Python sidecar or a C toolchain in the Go quality service.
- **Drop-in shape** matches V16's existing flow: hash → compare (Hamming) →
  threshold. Minimal blast radius.
- **One dependency covers the whole spectrum** — if PDQ ever needs swapping for
  block-mean or wavelet on a specific source, it's a one-line hasher change.
- **Versioned & tagged** (v2.5.2, semver) — unlike goimagehash which has shipped
  no release since v1.1.0 (2022).

### Weaknesses
- **Low star count (58)** — younger/less-battle-tested than goimagehash (834★) or
  Python ImageHash (3.8k★). Mitigated by: it implements the *same* canonical
  algorithms, and PDQ has an independent reference (python-threatexchange) to
  cross-validate against.
- Single maintainer `[ASSUMED]` — bus-factor risk; mitigated because PDQ output is
  spec-defined and portable across implementations.

### Recommendation + integration notes
**Replace `goimagehash.PerceptionHash` with `imghash` PDQ inside V16.** Keep the
HashStore interface, the SQLite index, and the "different vehicle ⇒ WARNING" logic
exactly as-is. Change two things: (1) hasher, (2) threshold/width — PDQ is 256-bit,
so the Hamming≤4/64 threshold becomes a PDQ threshold (Facebook's recommended
match band is **Hamming ≤ 30–31 / 256** for confident matches; tune down to
~10–20 for the stricter "this is literally the same photo" fraud signal).
Source for PDQ threshold: arXiv 1912.07745 PDQ test-drive
(https://ar5iv.labs.arxiv.org/html/1912.07745) `[VERIFIED]`.

```go
// V16 — replace goimagehash with ajdnik/imghash PDQ (pure Go, no cgo)
import (
    "image"
    "github.com/ajdnik/imghash/v2"
)

// construct once, reuse (hashers are cheap, stateless)
var pdq = imghash.NewPDQ()

func computePDQ(img image.Image) (imghash.Hash, error) {
    return pdq.Calculate(img) // 256-bit PDQ hash
}

// match decision: PDQ Compare returns Hamming Distance over 256 bits
const pdqDuplicateMax = 16 // strict "same photo" fraud band; PDQ paper match band ≤ 30/256

func isDuplicate(a, b imghash.Hash) bool {
    return pdq.Compare(a, b) <= pdqDuplicateMax
}
```
> API note: README quick-start shows `NewPDQ()` + `HashFile()` + `pdq.Compare()`
> returning a `Distance`. `[VERIFIED]`. The `image.Image`-based `Calculate` form
> above is `[ASSUMED]` from the package's documented hasher interface — confirm the
> exact method name (`Calculate` vs `Hash`) against `pkg.go.dev/github.com/ajdnik/imghash/v2`
> at integration time before relying on it.

---

## Candidate 2 — Facebook PDQ via `python-threatexchange` / `pdqhash`  ✅ FALLBACK (canonical reference)

- **Core repo:** https://github.com/facebook/ThreatExchange
  — **Pushed 2026-06-04**, 1,340★, 51 open issues, not archived `[VERIFIED]` (gh api).
  Very much alive — this is Meta's actively developed trust-&-safety stack.
- **Python package `threatexchange`:** **v1.2.16, released 2026-06-03**
  `[VERIFIED]` (PyPI); monthly cadence (1.2.12 Jan → 1.2.16 Jun 2026). Ships
  `PDQSignal` + **FAISS-backed index** for scaled matching. `[VERIFIED]`
- **Python bindings `pdqhash` (faustomorales):** **v0.2.8, 2025-05-28**
  `[VERIFIED]` (PyPI); repo pushed 2025-05-28, 38★, 1 open issue, not archived
  `[VERIFIED]`. Wheels for py3.9–3.13, macOS/Win/Linux.

### What it solves
The **canonical 256-bit PDQ** + quality score, plus a production-grade FAISS index
for matching at millions scale, plus vPDQ for video. This is the reference
implementation every other PDQ port is validated against.

### Strengths
- **Gold-standard PDQ + FAISS index** already wired for billion-scale matching.
- **Most actively maintained tool in this whole audit** (core repo pushed 4 days
  before audit; PyPI release monthly).
- 256-bit hash + published match threshold (≤30/256) with a quality gate.

### Weaknesses
- **Python, not Go.** CARDEEP's quality service is Go — adopting this as the
  *primary* means a Python sidecar/microservice or cgo. That's why it's the
  **fallback / cross-validation reference**, not the in-process primary.
- PDQ shares pHash's structural weakness on **heavy crop/rotation** (verified: PDQ
  "struggled with cropping — removing even 5% pushed results beyond threshold;
  rotation mirrored cropping; ~half of heavily watermarked images fell below
  match"). Source: arXiv 1912.07745 `[VERIFIED]`. PDQ is *better* than 64-bit pHash
  but is **not** a crop-robust silver bullet — that's the embedding tier's job.

### Recommendation
Use as the **authoritative PDQ oracle**: if CARDEEP ever needs to (a) sanity-check
the Go `imghash` PDQ output bit-for-bit, or (b) scale the dedup index to hundreds
of millions with FAISS, stand up `python-threatexchange` as a dedicated matching
microservice. Config sketch:

```python
# pip install pdqhash threatexchange faiss-cpu
import cv2, pdqhash
img = cv2.imread("photo.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
hash_vec, quality = pdqhash.compute(img)   # 256-bit vector + 0..100 quality
# Match band: Hamming <= 31/256 (Facebook default). Tighten to ~16 for "same photo".
```

---

## Candidate 3 — `JohannesBuchner/ImageHash` (Python)  ✅ ALIVE (turnkey Python alt)

- **Repo:** https://github.com/JohannesBuchner/imagehash
- **Pushed 2025-04-17**, **3,835★**, 26 open issues, **not archived** `[VERIFIED]` (gh api).
- **PyPI v4.3.2, 2025-02-01** `[VERIFIED]`. Deps: Pillow, numpy, scipy.

### What it solves
The de-facto Python perceptual hash: aHash, **pHash**, dHash, **wHash (wavelet)**,
colorhash, and **crop-resistant hashing** (added v4.2). The crop-resistant variant
is directly relevant to CARDEEP's crop-disguise problem.

### Strengths / Weaknesses
- **Strength:** huge install base, well-documented, the `crop_resistant_hash`
  function specifically targets the crop weakness that plagues plain pHash.
- **Weakness:** no PDQ; pure-Python pHash is slower than Go; releases are
  infrequent (4.3.1 in 2022 → 4.3.2 in 2025) though the repo *is* still pushed-to.
  Python, not Go — same sidecar friction as PDQ. **Alive, not dead.**
- **Recommendation:** the right choice *only if* CARDEEP builds a Python image
  microservice anyway. Otherwise `imghash` (Go) keeps it in-process.

```python
# pip install ImageHash
import imagehash
from PIL import Image
h1 = imagehash.phash(Image.open("a.jpg"))           # 64-bit pHash
hc = imagehash.crop_resistant_hash(Image.open("a.jpg"))  # crop-robust variant
print(h1 - imagehash.phash(Image.open("b.jpg")))    # Hamming distance
```

---

## Candidate 4 — `imagededup` (idealo, Python)  ✅ ALIVE (turnkey dedup pipeline)

- **Repo:** https://github.com/idealo/imagededup
- **Pushed 2025-08-15**, **5,638★**, 38 open issues, not archived `[VERIFIED]` (gh api).
- Apache-2.0, Python 3.9+. PHash/DHash/WHash/AHash **+ CNN** in one API. `[VERIFIED]`

### What it solves
A batteries-included dedup pipeline: `find_duplicates()` with a hashing *or* a CNN
backend, encode/threshold/evaluate helpers. Best documented "find duplicate photos"
turnkey. CNN backend gives the embedding-tier robustness without writing it.

### Strengths / Weaknesses
- **Strength:** most stars of any tool here, one API spans fast-hash and CNN; ideal
  for offline batch dedup audits over the whole CARDEEP photo corpus.
- **Weakness:** Python; the CNN path needs torch/GPU for speed; oriented at batch
  dedup, not per-listing streaming validation. **Alive, not dead.**
- **Recommendation:** excellent **offline corpus-audit / backfill** tool to seed
  the duplicate index and to *evaluate* thresholds — not the per-listing hot path.

---

## Candidate 5 — Embedding tier: DinoHash / CLIP / SigLIP / SSCD  ✅ ADOPT NARROWLY (2nd-stage re-rank)

This is the **robustness ceiling** — what catches the crops/watermarks/overlays
PDQ misses. Use it on **flagged pairs only**, never on every photo (cost).

- **DinoHash** — ICML 2025, repo `proteus-photos/dinohash-perceptual-hash`,
  **pushed 2025-10-31**, 24★, not archived `[VERIFIED]` (gh api). DINOv2-based +
  adversarial training; **+12% avg bit-accuracy over SOTA watermarking/perceptual
  hashing**, "CLIP-level performance at 20× smaller model and 100× shorter hash,"
  robust to filters/compression/crops, released PyTorch+ONNX+npm. Source:
  https://github.com/proteus-photos/dinohash-perceptual-hash, arXiv 2503.11195
  `[VERIFIED]` (repo + abstract read). **The modern SOTA pick for the embedding tier.**
- **CLIP / SigLIP embeddings** — 2025 benchmarks: SigLIP best at duplicate ID
  (~59% precision) vs CLIP-ViT ~33%, Nomic ~49%; embeddings catch crops/overlays/
  screenshots that hashing misses. Source: MDPI 15(7):1493 (via search) `[VERIFIED]`
  abstract; exact table `[ASSUMED]`. Off-the-shelf, ONNX-exportable, well-supported.
- **SSCD** (`facebookresearch/sscd-copy-detection`) — ❌ **DEAD / ARCHIVED**. Last
  push **2022-08-02**, repo **archived: true**, 404★, 1 issue `[VERIFIED]` (gh api).
  Still cited as a robustness *baseline* in papers, but the repo is frozen and
  archived — **do not adopt as a live dependency.** Prefer DinoHash, which
  explicitly supersedes it on the same benchmark family.

### Recommendation
Two-stage cascade: **PDQ (imghash) as the cheap fleet-scale first filter →
embedding re-rank (DinoHash preferred, CLIP/SigLIP acceptable) only on pairs PDQ
puts in the "suspicious but uncertain" band.** This caps GPU/embedding cost while
recovering the crop/watermark/overlay recall PDQ alone loses. Matches the verified
industry "hash-first, AI-second hybrid" guidance.

---

## DEAD / ABANDONED — do not adopt (corpses flagged)

| Tool | Last push | Status | Why dead |
|---|---|---|---|
| **`facebookresearch/sscd-copy-detection`** | 2022-08-02 | **ARCHIVED** `[VERIFIED]` | Repo archived read-only; superseded by DinoHash. |
| **`MTRNord/pdqhash-go`** | 2024-02-25 | **0★, effectively dead** `[VERIFIED]` | cgo PDQ binding, zero traction; `ajdnik/imghash` does PDQ in pure Go, fresher. |
| **`commonsmachinery/blockhash-python`** | 2023-10-31 | **STALE (~2.6 yr)** `[VERIFIED]` | 130★ but no push since Oct 2023; blockhash algorithm available inside live `imghash` instead. Algorithm fine; *this repo* is a corpse. |
| **`corona10/goimagehash` (CURRENT)** | 2024-01-21 commit / v1.1.0 May-2022 release | **FROZEN (suspect)** `[VERIFIED]` | Not archived, 834★, but no release in ~4 yr, no commit in ~2.4 yr, pHash/aHash only, no PDQ. Functional but stagnant — **replace.** |

---

## Final answer — is CARDEEP's current choice good enough?

**No — adequate, not best.** `goimagehash` 64-bit pHash @ Hamming≤4 (V16) runs and
catches exact/near-exact re-encodes, but it is (1) on a **frozen** library (no
release since 2022, no commit since Jan 2024), (2) **single-algorithm** (no PDQ),
and (3) **brittle to the crop/watermark/overlay tricks** dealers use to disguise
re-listings.

**Replacement, minimal blast radius:**
1. **Swap the hasher to `ajdnik/imghash` v2.5.2 (PDQ, pure Go, last commit
   2026-06-09)** — keep V16's store, index, and warning logic; widen the hash to
   256-bit PDQ and retune the threshold (~≤16/256 strict, ≤30/256 loose).
2. **Keep `python-threatexchange` 1.2.16 PDQ + FAISS** in reserve as the canonical
   oracle and the scale-out matching index if the corpus outgrows SQLite.
3. **Add a narrow embedding second stage (DinoHash preferred, CLIP/SigLIP
   acceptable)** that runs *only* on PDQ-flagged uncertain pairs, to recover
   crop/watermark/overlay recall without per-photo GPU cost.
4. **Use `imagededup` offline** to backfill/seed the duplicate index and to
   empirically tune the PDQ threshold against CARDEEP's real photo corpus.

This keeps the fast hash-first architecture CARDEEP already chose, moves it onto a
**maintained, PDQ-capable, pure-Go** foundation, and adds a bounded embedding
safety net for the adversarial cases classical hashing provably misses.

---

## Sources (all fetched 2026-06-12)

- goimagehash repo (current choice): https://github.com/corona10/goimagehash `[VERIFIED]` (gh api)
- ajdnik/imghash (Go, recommended): https://github.com/ajdnik/imghash `[VERIFIED]`
- JohannesBuchner/ImageHash: https://github.com/JohannesBuchner/imagehash · https://pypi.org/project/ImageHash/ `[VERIFIED]`
- Facebook PDQ / ThreatExchange: https://github.com/facebook/ThreatExchange · https://pypi.org/project/threatexchange/ `[VERIFIED]`
- pdqhash bindings: https://github.com/faustomorales/pdqhash-python · https://pypi.org/project/pdqhash/ `[VERIFIED]`
- blockhash: https://github.com/commonsmachinery/blockhash-python `[VERIFIED]` (gh api)
- imagededup: https://github.com/idealo/imagededup `[VERIFIED]` (gh api)
- SSCD (DEAD): https://github.com/facebookresearch/sscd-copy-detection `[VERIFIED]` (gh api, archived)
- DinoHash: https://github.com/proteus-photos/dinohash-perceptual-hash · https://arxiv.org/abs/2503.11195 `[VERIFIED]`
- PDQ test-drive (thresholds, crop/rotation/watermark robustness): https://ar5iv.labs.arxiv.org/html/1912.07745 `[VERIFIED]`
- Hamming distributions of perceptual hashes: https://arxiv.org/pdf/2212.08035 `[VERIFIED]` (abstract; full PDF binary-unreadable)
- State of the Art: Image Hashing: https://arxiv.org/pdf/2108.11794 `[VERIFIED]` (abstract)
- MDPI Electronics 15(7):1493 (2026) perceptual hash vs deep embedding: https://www.mdpi.com/2079-9292/15/7/1493 `[VERIFIED]` (abstract; full HTML HTTP 403)
- AI vs perceptual hashing fingerprinting (recall numbers): https://www.scoredetect.com/blog/posts/content-fingerprinting-ai-vs-perceptual-hashing `[VERIFIED]`
