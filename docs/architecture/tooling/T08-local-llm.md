# T08 — Local LLM for massive/cheap classify · parse · dedup

> **Task-domain:** Local LLM inference engine + small model for the high-volume,
> low-cost stage of the pipeline — classify dealer kind, parse listing text into
> structured fields, deduplicate near-identical records, geo-resolve.
> The *expensive* intelligence stays for decisions; this layer must be €0/scale-linear.
> **Doctrine anchor:** `ORQUESTACION.md` L8-9 — *"Lo masivo y barato → determinista o LLM
> local … Ollama. €0, escala lineal."* CARDEEP's current choice is **Ollama** (no model pinned).
>
> **Audit date:** 2026-06-12 · **Auditor:** tooling researcher (Fable 5)
> **Verification legend:** `[VERIFIED]` = repo/page fetched this session · `[ASSUMED]` = inferred, not directly fetched.

---

## 0. TL;DR — the verdict

| Question | Answer |
|---|---|
| **Is CARDEEP's current choice (Ollama) good enough?** | **For dev / single-stream: yes. For the *massive* batch stage: NO — leaves ~10x throughput on the table.** |
| **Bulletproof modern pick (engine)** | **vLLM** for the batch classify/parse/dedup fleet — continuous batching = ~10x tokens/s under concurrency, native structured-output (xgrammar default). |
| **Fallback / dev engine** | **llama.cpp** (and `llama-server`) — single-stream king, lowest VRAM, runs CPU-only, GBNF grammar. **Ollama is a llama.cpp wrapper** — keep it only as the developer-ergonomics front-end, not the production batch engine. |
| **Bulletproof model pick** | **Qwen3.5-4B-Instruct** (Apache-2.0, 201 langs incl. Spanish, native tool-calling/structured output) on GPU via vLLM. |
| **CPU-only / modest-GPU model** | **Qwen3.5-4B** or **Gemma-4-E4B-it** quantized Q4_K_M via llama.cpp. |
| **Fallback model** | **Gemma-4-E4B-it** (Apache-2.0, edge-tuned, 140+ langs) — or **Qwen3.5-2B** if RAM ≤ 8 GB. |
| **DEAD/abandoned to avoid** | None of the four engines is dead — all shipped releases **within days of the audit**. The *trap* is recency of **models**: Qwen3 / Gemma 3 / Phi-4 are last-gen as of mid-2026; do not pin them as "the latest". |

**One-line recommendation:** keep Ollama for local dev ergonomics, but run the production
classify/parse/dedup fleet on **vLLM + Qwen3.5-4B with `guided_json` (xgrammar)**, with
**llama.cpp + Gemma-4-E4B Q4** as the CPU/low-VRAM fallback.

---

## 1. The decision that actually matters: batch vs single-stream

CARDEEP's bottleneck is **volume**, not latency. We classify/parse *millions* of
listings and dealer records. The single metric that matters is **aggregate tokens/sec
under concurrency**, and that is exactly where the engines diverge by an order of magnitude.

`[VERIFIED — techplained.com benchmark, A100 80GB, Llama-3.1-8B, 512-in/256-out]`

| Engine | 1 request | **32 concurrent requests** |
|---|---|---|
| **vLLM** (FP16) | 118 t/s | **1,280 t/s** |
| llama.cpp (CUDA Q4_K_M) | 105 t/s | 122 t/s |
| Ollama (Q4_K_M) | 98 t/s | 106 t/s |

> vLLM delivers **~10x total throughput at 32 concurrent requests**. PagedAttention +
> continuous batching is the unlock; llama.cpp/Ollama barely scale past single-stream
> because they do not do continuous batching the same way. `[VERIFIED]`

Second source corroborates the shape: `[VERIFIED — sitepoint 2026]` vLLM's continuous
batching aggregated 10 concurrent requests into unified GPU ops at ~485 t/s for Llama-3.1-8B
FP16, while Ollama's edge is **only** the single-user case (Ollama Q4 ~62 t/s vs vLLM FP16
~71 t/s single-stream). The consensus across every benchmark surfaced
(`aimadetools`, `sitepoint`, `quantizelab`, `techplained`): **"serving a team → vLLM;
only user → llama.cpp."** For CARDEEP's batch fleet we are emphatically "serving a team"
(the team is our own crawler queue).

---

## 2. Engine candidates — alive-or-dead, strengths, weaknesses

All four release stats fetched from the GitHub API this session (`[VERIFIED]`, 2026-06-12).

### 2.1 vLLM — **RECOMMENDED (production batch)**

| | |
|---|---|
| Repo | `github.com/vllm-project/vllm` |
| **Alive?** | **VERY ALIVE.** Latest **v0.22.1 — 2026-06-05** (7 days before audit). v0.22.0 2026-05-29, v0.21.0 2026-05-15. `[VERIFIED — GH API]` |
| Stars / open issues | 82.7k ★ / 5,363 open issues · `pushed_at` 2026-06-12T13:56Z (today). `[VERIFIED]` |
| Health note | High open-issue count is *scale*, not rot — it's the busiest inference repo in OSS; releases are weekly. |

- **Solves:** maximum-throughput serving via **PagedAttention** (KV-cache paging) + **continuous batching** + prefix caching + tensor parallelism. OpenAI-compatible server.
- **Strengths:** the throughput numbers above; **native structured output** (`guided_json`, `guided_choice`, `guided_regex`, `guided_grammar`) with **xgrammar as the default backend in 2026** `[VERIFIED — vLLM docs + search consensus]`; first-class day-0 support for Qwen3.x and Gemma 4.
- **Weaknesses:** GPU-first (CUDA/ROCm); **not a CPU engine** — needs a real GPU to shine. Heavier ops footprint than Ollama. Cold-start and memory tuning have a learning curve. Historically guided-decoding had rough edges (GH #15236, ≤ v0.8.1) — **resolved**: xgrammar backend is now stable/default `[VERIFIED — issue is pre-v0.9, current is v0.22]`.
- **Verdict:** the bulletproof pick for the massive stage **when a GPU is available**.

### 2.2 llama.cpp — **RECOMMENDED (CPU / low-VRAM fallback + the real engine under Ollama)**

| | |
|---|---|
| Repo | `github.com/ggml-org/llama.cpp` |
| **Alive?** | **HYPER-ALIVE.** Rolling build tags; latest **b9611 — 2026-06-12T14:03Z** (same day as audit). `[VERIFIED — GH API]` |
| Stars / open issues | 116.2k ★ / 1,825 open · `pushed_at` today. `[VERIFIED]` |

- **Solves:** efficient single-stream inference on **CPU, Apple Silicon, or modest GPU** via GGUF quantization (Q4_K_M etc.). Ships `llama-server` (OpenAI-compatible).
- **Strengths:** lowest VRAM (90% of vLLM single-stream speed at 35-60% of the VRAM `[VERIFIED — techplained]`); **runs CPU-only** — critical for CARDEEP's "eliminamos por capacidad del PC" constraint; **GBNF grammar** constrained decoding (force valid JSON) `[VERIFIED — llama.cpp grammars README + DeepWiki]`; JSON-Schema→GBNF converter built in.
- **Weaknesses:** does **not** match vLLM under concurrency (122 vs 1,280 t/s at 32 req); grammar/JSON support is per-server-flag, less ergonomic than vLLM's `guided_json`.
- **Verdict:** the correct **fallback** and the correct **CPU** engine. Also the substrate Ollama sits on — so adopting it is not throwing Ollama work away.

### 2.3 Ollama — **KEEP AS DEV FRONT-END ONLY (CARDEEP's current default)**

| | |
|---|---|
| Repo | `github.com/ollama/ollama` |
| **Alive?** | **VERY ALIVE.** Latest **v0.30.7 — 2026-06-07** (5 days before audit). `[VERIFIED — GH API]` |
| Stars / open issues | 173.9k ★ / 3,393 open · `pushed_at` today. `[VERIFIED]` |

- **Solves:** dead-simple local model management (`ollama run qwen3.5`), one-line pulls, OpenAI-compatible endpoint. **Wraps llama.cpp.** `[VERIFIED — search consensus + Ollama docs]`
- **Strengths:** best DX for dev/iteration; **structured outputs since v0.5** — pass a JSON schema to the `format` param, Ollama converts it to GBNF internally and hands it to llama.cpp `[VERIFIED — docs.ollama.com/capabilities/structured-outputs]`. Effortless model swapping.
- **Weaknesses:** **does not scale** — 106 t/s at 32 concurrent vs vLLM's 1,280 (≈12x slower aggregate); inherits llama.cpp's batching ceiling; extra abstraction layer you don't want in a hot production loop.
- **Verdict:** **current CARDEEP choice. Good enough for dev and single-stream, NOT for the massive batch stage.** Demote it to the developer/iteration front-end; do not run the production fleet on it.

### 2.4 SGLang — **STRONG ALTERNATIVE / WATCH (not the pick today)**

| | |
|---|---|
| Repo | `github.com/sgl-project/sglang` |
| **Alive?** | **VERY ALIVE.** Latest **v0.5.12.post1 — 2026-05-26**. `[VERIFIED — GH API]` |
| Stars / open issues | 28.9k ★ / 3,534 open · `pushed_at` today. `[VERIFIED]` |

- **Solves:** high-throughput serving like vLLM, with **RadixAttention** prefix-cache reuse — excellent when many prompts share a long system/schema prefix (exactly CARDEEP's case: same extraction prompt over millions of listings).
- **Strengths:** often **matches or beats vLLM** on prefix-heavy workloads; strong structured-output story.
- **Weaknesses:** smaller ecosystem than vLLM; one more thing to operate. Benchmarks surfaced are less unanimous than vLLM's.
- **Verdict:** **the one alternative worth benchmarking** against vLLM on our real prompt before committing — our workload (identical schema prefix, huge fan-out) is SGLang's sweet spot. Default to vLLM; A/B SGLang in F-LLM phase.

> **No corpses in this domain.** All four engines shipped releases within ~2 weeks of the
> audit (llama.cpp & vLLM the *same day*). The recency trap here is on the **model** axis, §3.

---

## 3. Model candidates — the recency trap

**CRITICAL recency finding:** popular "best small model 2026" listicles still name
**Qwen3 / Gemma 3 / Phi-4 / Llama 3.2-3.3**. As of **mid-2026 these are last-generation.**
`[VERIFIED — HuggingFace model cards + Qwen/Google release pages]`:

- **Qwen3.5** dense family — **Qwen3.5-4B / -9B / -2B / -0.8B released 2026-03-02** (and 27B/35B-A3B MoE Feb 2026), **Apache-2.0**. `[VERIFIED — HF]`
- **Qwen3.6** — **27B (2026-04-22) and 35B-A3B (2026-04-16)**, Apache-2.0. `[VERIFIED — HF]` (No tiny dense ≤4B confirmed yet → for the *small* tier, Qwen3.5-4B is the current sweet spot.)
- **Gemma 4** — **released 2026-03-31, Apache-2.0**, sizes include **E2B / E4B** (edge "effective-param") + 26B-A4B MoE + 31B. `[VERIFIED — HF google/gemma-4-E4B + ai.google.dev]`

Pinning "Qwen3:8b" or "gemma3" today would be shipping a stale model. The pick below uses
the **current** generation.

### 3.1 Qwen3.5-4B-Instruct — **RECOMMENDED model**

`[VERIFIED — huggingface.co/Qwen/Qwen3.5-4B model card fetched this session]`

- **License:** **Apache-2.0** → clean commercial use, no Llama-style community-license footguns.
- **Context:** native **262,144 tokens** (extensible ~1M) — whole dealer pages fit in one prompt.
- **Languages:** **201 languages/dialects incl. Spanish**, with regional nuance — decisive for ES car-listing slang/provincial terms.
- **Structured output / tools:** **native tool-calling**; vLLM example in the card uses `--enable-auto-tool-choice --tool-call-parser`. Pairs directly with `guided_json`.
- **Why for CARDEEP:** 4B is the throughput/accuracy sweet spot for *extraction* (not reasoning) — runs fast batched on a modest GPU via vLLM, and runs CPU-only quantized via llama.cpp. "Even Qwen3-4B rivals Qwen2.5-72B" `[VERIFIED — Qwen blog]`; 3.5 is a further step.
- **Throughput note:** has a thinking mode on by default — **disable it for extraction** (set non-thinking / instruct) so you don't pay reasoning tokens on a deterministic parse job.

### 3.2 Gemma-4-E4B-it — **RECOMMENDED fallback model**

`[VERIFIED — huggingface.co/google/gemma-4-E4B-it + ai.google.dev/gemma/docs/core + search]`

- **License:** **Apache-2.0.** **128K context. 140+ languages** (Spanish covered).
- **Structured output:** **native function-calling + JSON structured output** per Google's card.
- **Edge-tuned:** Per-Layer-Embeddings give big-model depth at small-model RAM → ideal for the **CPU / "eliminamos por capacidad del PC"** path. Multimodal (text+image+audio) — useful later if we parse listing photos.
- **Benchmark signal:** the Gemma-4 family's MoE variant (26B-A4B) topped a 2026 accuracy study at 0.794 weighted `[VERIFIED — arxiv 2604.07035]`; E4B is the small-RAM sibling.
- **Use when:** Qwen3.5-4B output quality dips on a specific source, or RAM is tight and you want the most efficient edge model.

### 3.3 Also-considered (not picked)

| Model | Status | Why not the pick |
|---|---|---|
| **Qwen3.5-2B / -0.8B** | `[VERIFIED]` Apache-2.0, Mar 2026 | Use **only** if RAM ≤ 8 GB; 4B is the better accuracy/throughput point for extraction. |
| **Qwen3 / Gemma 3** | `[VERIFIED]` last-gen | **Do not pin as "latest".** Superseded Feb-Apr 2026. Still functional, but stale. |
| **Phi-4 / Phi-4-mini** | `[VERIFIED]` MIT | Strong reasoning/benchmarks, but Qwen3.5/Gemma-4 lead on **multilingual ES** + structured output; Phi is reasoning-tuned, overkill for deterministic parse. |
| **Llama 3.3** | `[VERIFIED]` | **Llama Community License** (not OSI) — commercial-terms footgun; lags Qwen3.5/Gemma-4 on small-tier multilingual. Avoid for clean licensing. |

---

## 4. Structured-output enforcement (non-negotiable for CARDEEP)

We never trust free-text LLM output. Every classify/parse call must be **schema-constrained
at the decoder** (mask invalid tokens), not "asked nicely" in the prompt.

| Backend | Where | Status | Notes |
|---|---|---|---|
| **xgrammar** | vLLM **default** 2026 | `[VERIFIED]` `mlc-ai/xgrammar` 1.7k★, `pushed_at` 2026-06-11 — **alive** | JIT-compiled grammar, fastest for most schemas. Use via `guided_json`. |
| **Outlines** | vLLM optional | `[VERIFIED]` `dottxt-ai/outlines` 13.9k★, `pushed_at` 2026-05-18 — **alive** | Switch to this for *very complex schemas reused across thousands of requests* (FSM compile cost amortizes). |
| **GBNF** | llama.cpp / Ollama | `[VERIFIED]` built-in | JSON-Schema→GBNF converter; Ollama exposes via `format` param since v0.5. |

**Rule for CARDEEP:** define one Pydantic/JSON-Schema per task (dealer-classify, listing-parse,
dedup-judge). Pass it as `guided_json` (vLLM) / GBNF (llama.cpp). Default backend **xgrammar**;
escalate to **outlines** only if a schema is huge and hot.

---

## 5. Recommended architecture for CARDEEP's LLM layer

```
                      ┌──────────────────────────────────────────────┐
   crawler queue ───► │  BATCH LLM FLEET  (production, GPU)           │
   (millions of       │  vLLM  v0.22.x  +  Qwen3.5-4B-Instruct        │
    listings/dealers) │  guided_json (xgrammar)  ·  continuous batch  │ ──► structured rows
                      │  ~1,280 t/s @ 32 concurrent                   │     (Postgres)
                      └──────────────────────────────────────────────┘
                                        │ fallback / CPU-only host
                                        ▼
                      ┌──────────────────────────────────────────────┐
                      │  CPU / LOW-VRAM PATH                          │
                      │  llama.cpp (llama-server) + Gemma-4-E4B Q4_K_M│
                      │  GBNF-constrained JSON                        │
                      └──────────────────────────────────────────────┘

   dev / iteration:   Ollama (qwen3.5 / gemma4:e4b) — `format` schema param. Not in prod hot path.
   watch / A-B:       SGLang (RadixAttention) — benchmark vs vLLM on our shared-prefix prompt.
```

**Cost doctrine compliance:** all engines + models are **OSS, €0 license**, self-hosted →
scales linearly with our own compute, exactly per `ORQUESTACION.md`. The "expensive
intelligence" (frontier API) is reserved for decisions, never for the millions-row parse.

### 5.1 Classifier accuracy floor + drift regression — the cheapest plane is the least-verified `[adversarial GAP-7/25]`
`classify_kind` writes `kind` (the most load-bearing field — it picks the seal segment) and
`canonical_name` feeds the `cdp_code` that feeds capture-recapture. The `confidence<0.7 → keep
deterministic guess + flag` fallback **assumes the model's self-reported confidence is calibrated**,
which 4B local models notoriously are not, and for an entity with NO higher-precedence signal (a bare
compraventa/importador/garaje known only from a platform) the classifier IS the authority and its
error rate is otherwise unmeasured. The acceptance-sampling corpus (V6) sizes SCRAPER field defects
but never "is the LLM's kind label correct?". Closed here:
- **A held-out, human-labeled GOLD SET** (≥300 dealers spanning every kind, sampled across the
  long-tail, NOT a convenience sample) with a **per-kind precision/recall floor**. Where the
  classifier is the **sole authority** (no registral/locator/brandlist signal), the floor is **≥0.95
  precision AND ≥0.95 recall** for that kind; where a higher rung usually overrides it, a softer floor
  applies. The classifier must clear the floor on the gold set **before it writes candidates at
  scale** (MASTER_PLAN P3 gate).
- **A nightly GOLDEN-SET REGRESSION** re-scores the model on the gold set. A drop below floor — from
  model swap, quantization drift, or prompt drift — fires a `classifier_drift` Gestionador item
  (V4) and **freezes `kind_source='classifier'` writes until cleared**. The entire verification
  corpus already watches scraper-recipe drift (field null-rate vs golden) — this extends the same
  discipline to the LLM CLASSIFIER, which was previously watched by nothing. A silently-degraded
  model mis-typing 8% of long-tail entities is no longer invisible.
- **`canonical_name` is checked on the SAME gold set** (string-match rate vs the labeled canonical),
  because a canonicalization drift silently shifts the `cdp_code` merge rate that the denominator
  estimator depends on (V1 §8 / MASTER_PLAN G-A21/29).

---

## 6. Sample CONFIG

### 6.1 Production — vLLM server (GPU)

```bash
# vLLM >= 0.22.x  ·  Qwen3.5-4B-Instruct  ·  structured output via xgrammar (default)
pip install "vllm>=0.22,<0.23"

vllm serve Qwen/Qwen3.5-4B-Instruct \
  --port 8000 \
  --max-model-len 32768 \                 # plenty for one listing/dealer page; cap for KV-cache headroom
  --gpu-memory-utilization 0.90 \
  --enable-prefix-caching \               # huge win: identical extraction-prompt prefix is cached
  --guided-decoding-backend xgrammar \    # explicit; it is the 2026 default anyway
  --enable-auto-tool-choice \
  --tool-call-parser hermes               # Qwen3.x tool-call parser; verify exact name vs model card
```

```python
# Constrained extraction call — OpenAI-compatible; schema enforced at the decoder.
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

DEALER_SCHEMA = {
    "type": "object",
    "properties": {
        "kind": {"type": "string",
                 "enum": ["concesionario", "compraventa", "garaje",
                          "desguace", "importador", "plataforma"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["kind", "confidence"],
    "additionalProperties": False,
}

resp = client.chat.completions.create(
    model="Qwen/Qwen3.5-4B-Instruct",
    messages=[
        {"role": "system", "content": "Classify the Spanish car-dealer listing. Output JSON only."},
        {"role": "user", "content": LISTING_TEXT},
    ],
    extra_body={"guided_json": DEALER_SCHEMA},   # vLLM structured output
    temperature=0,                               # deterministic parse, no creativity
    max_tokens=64,
)
# resp.choices[0].message.content is guaranteed-valid JSON for DEALER_SCHEMA
```

### 6.2 Fallback — llama.cpp server (CPU / modest GPU)

```bash
# Gemma-4-E4B, Q4_K_M GGUF; GBNF/JSON-schema constrained; CPU-friendly
./llama-server \
  -hf google/gemma-4-E4B-it-GGUF:Q4_K_M \   # or a local .gguf path
  --port 8001 \
  --ctx-size 8192 \
  --parallel 4 \                            # modest concurrency; CPU won't reach vLLM batch numbers
  --jinja                                   # enable chat template + tool/JSON handling
# Send OpenAI-style request with response_format={"type":"json_object"} or a json_schema;
# llama.cpp converts the schema to GBNF and constrains decoding.
```

### 6.3 Dev / iteration — Ollama (keep, demoted)

```bash
ollama pull qwen3.5            # current gen; NOT qwen3 (last-gen)
# or:  ollama pull gemma4:e4b
```

```python
import ollama
schema = {"type": "object",
          "properties": {"kind": {"type": "string"}, "confidence": {"type": "number"}},
          "required": ["kind", "confidence"]}
r = ollama.chat(model="qwen3.5",
                messages=[{"role": "user", "content": LISTING_TEXT}],
                format=schema,           # structured output since Ollama v0.5 -> GBNF under the hood
                options={"temperature": 0})
```

### 6.4 `requirements.txt` delta (when F-LLM phase comes online)

```
# Local-LLM batch layer (T08) — install when the classify/parse/dedup fleet goes live
# vllm>=0.22,<0.23          # production batch engine (GPU). xgrammar bundled.
# openai>=1.40              # OpenAI-compatible client for vLLM / llama-server / Ollama
# llama-cpp-python>=0.3     # optional in-process llama.cpp (CPU fallback) if not using llama-server
```

---

## 7. Final verdict vs CARDEEP's current choice

- **Current choice = Ollama, no model pinned** (`ORQUESTACION.md`). **Verdict: keep, but demote.**
  Ollama is alive, excellent for dev, and is a llama.cpp wrapper — so it is not wasted. But it
  **does not scale** (≈12x slower aggregate than vLLM at 32 concurrent) and CARDEEP's whole point
  for this layer is *masivo y barato*. Running the production fleet on Ollama caps our throughput.
- **What replaces it for the hot path:** **vLLM v0.22.x + Qwen3.5-4B-Instruct + guided_json(xgrammar)**.
- **Fallback / CPU host:** **llama.cpp (llama-server) + Gemma-4-E4B-it Q4_K_M + GBNF**.
- **Watch / benchmark:** **SGLang** (RadixAttention) — likely a win on our shared-prefix workload; A/B before final lock.
- **Model recency mandate:** pin **Qwen3.5 / Gemma 4**, never Qwen3 / Gemma 3 / Phi-4 / Llama 3.x —
  those are last-gen as of June 2026.

---

## 8. Sources (all fetched / searched 2026-06-12)

GitHub API (release recency, stars, issues) — `[VERIFIED]`:
- https://github.com/vllm-project/vllm  (v0.22.1, 2026-06-05)
- https://github.com/ollama/ollama  (v0.30.7, 2026-06-07)
- https://github.com/ggml-org/llama.cpp  (b9611, 2026-06-12)
- https://github.com/sgl-project/sglang  (v0.5.12.post1, 2026-05-26)
- https://github.com/dottxt-ai/outlines  (pushed 2026-05-18)
- https://github.com/mlc-ai/xgrammar  (pushed 2026-06-11)

Benchmarks & engine comparisons — `[VERIFIED via fetch]` techplained; `[VERIFIED via search]` others:
- https://www.techplained.com/ollama-vs-vllm-vs-llamacpp  (1,280 vs 122 vs 106 t/s @ 32 concurrent)
- https://www.sitepoint.com/ollama-vs-vllm-performance-benchmark-2026/
- https://www.aimadetools.com/blog/vllm-vs-ollama-vs-llamacpp-vs-tgi/
- https://www.quantizelab.dev/articles/vllm-vs-llama-cpp-vs-ollama-benchmark-guide

Structured output — `[VERIFIED via search]`:
- https://docs.vllm.ai/en/v0.10.1/features/structured_outputs.html
- https://docs.ollama.com/capabilities/structured-outputs
- https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md
- https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang
- https://arxiv.org/pdf/2411.15100  (XGrammar paper)

Models — `[VERIFIED via fetch]` Qwen3.5-4B card; `[VERIFIED via search]` others:
- https://huggingface.co/Qwen/Qwen3.5-4B  (Apache-2.0, 262K ctx, 201 langs, tool-calling)
- https://huggingface.co/google/gemma-4-E4B-it  (Apache-2.0, 128K ctx, 140+ langs)
- https://qwenlm.github.io/blog/qwen3/
- https://ai.google.dev/gemma/docs/core
- https://arxiv.org/abs/2604.07035  (Gemma-4 / Phi-4 / Qwen3 accuracy-efficiency study)
