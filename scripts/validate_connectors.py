"""Local connector validation harness — smoke EVERY connector at MINIMAL scope (€0, free).

The user's pre-VPS rule: prove every connector/recipe WORKS on this terminal first; only what
works here goes to the VPS. This runs each connector with a tiny scope (--pages 1 / --limit),
captures its VAM verdict + cars caged + exit, and writes a results matrix. It is NOT a full
harvest (that is the VPS-scale phase) — it proves the config/recipe is functional.

Serial by design (single-producer — the AS24 scar: never two governors on the same host).
Per-connector timeout. Writes state/validation_matrix.json + prints a table.

Run:  python scripts/validate_connectors.py            # all
      python scripts/validate_connectors.py oem         # only modules matching 'oem'
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "state" / "validation_matrix.json"
TIMEOUT = 200  # seconds per connector; minimal scope should finish well under this

# (module, minimal-scope args). Scaled down from docs/runbook/VALIDATION-INDEX.md CLIs.
# audi + coches_net already proven by hand; included for completeness.
CONNECTORS: list[tuple[str, list[str]]] = [
    # --- OEM-VO portals (mostly t0_open, JSON-friendly) ---
    ("oem_audi_wholesale", ["--pages", "1"]),
    ("oem_ford_wholesale", ["--pages", "1"]),
    ("oem_toyota_lexus_wholesale", ["--pages", "1"]),
    ("oem_nissan_mazda_honda_wholesale", ["--pages", "1"]),
    ("oem_seat_cupra_wholesale", ["--pages", "1"]),
    ("oem_volvo_jlr_suzuki_wholesale", ["--pages", "1"]),
    ("renew_wholesale", ["--pages", "1"]),
    ("oem_mercedes_benz_wholesale", ["--pages", "1"]),
    ("oem_hyundai_wholesale", []),
    ("oem_kia_wholesale", []),
    ("oem_bmw_mini_wholesale", ["--brand", "bmw", "--dealers", "2"]),  # no --pages: --dealers bounds the roster
    ("spoticar_wholesale", ["--pages", "1"]),
    ("dasweltauto_wholesale", ["--provinces", "1", "--pages", "1"]),
    # --- Tier-1 marketplaces ---
    ("coches_net_wholesale", ["--pages", "1"]),
    ("milanuncios_wholesale", ["--pages", "1"]),
    ("coches_com_wholesale", ["--pages", "1"]),
    ("motor_es_wholesale", ["--max-cells", "1", "--limit", "50"]),  # no --pages: facet-grid crawler
    ("autocasion_facet", ["--makes", "audi", "--max-pages-per-slice", "1"]),
    # --- chains / rentacar / subastas ---
    ("group_vo_chains_wholesale", ["--members", "flexicar", "--pages", "1"]),
    ("group_rentacar_vo_wholesale", ["--member", "all", "--pages", "1"]),  # 1 page/member, safe choice value
    ("group_subastas_wholesale", []),
    # --- niche / classic ---
    ("carandclassic_wholesale", ["--pages", "1"]),
    ("miclasico_wholesale", ["--pages", "1"]),
    ("motorflash_wholesale", []),
    ("localizavo_wholesale", []),
    # --- long-tail CMS/DMS families (need real family members; --from-db is a smoke of the code path) ---
    ("family_dealerk_wholesale", ["--from-db", "--limit", "3"]),
    ("family_dms_vendor_platforms__wholesale", ["--seeds"]),
    ("family_cms_wordpress_dominated__wholesale", ["--from-db", "--limit", "3"]),
    ("family_generic_custom_wholesale", ["--all"]),
    ("family_framework_next_astro_nuxt_angular__wholesale", ["--from-db", "--limit", "3"]),
    ("family_builder_wix_ueni_google_sites_basekit__wholesale", ["--from-fingerprints", "--limit", "3"]),  # no --from-db
    ("family_unreachable_wholesale", ["--dealers", "hrmotor.com"]),
    # --- 2nd batch: real connectors missed in the first list (coverage honesty) ---
    ("wallapop_wholesale", ["--target", "651000"]),              # major C2C marketplace
    ("faciliteacoches_racc_wholesale", ["--members", "faciliteacoches", "--pages", "1"]),
    ("group_importador_wholesale", ["--pages", "1"]),
    ("subastacar_wholesale", []),
    ("autocasion_wholesale", ["--pages", "1"]),
]

# Deliberately NOT smoked here (documented — no silent cap):
#   autoscout24_wholesale          — AS24 ban-scar: needs the stealth campaign, not a free smoke.
#   coches_net_facet/segments      — alternate strategies of coches.net (host proven via _wholesale).
#   wallapop_facet                 — alternate strategy of wallapop (host smoked via _wholesale).
#   oem_seat_cupra_new_stock       — new-car stock variant (VO host proven via oem_seat_cupra_wholesale).
#   generic_dealer_site            — per-dealer helper used by family_* connectors; no standalone main.

_VERDICT_RE = re.compile(r"VAM verdict\s*[:=]\s*([A-Z_]+)")
_CAGED_RE = re.compile(r"cars (?:caged|ingested)\s*[:=]?\s*([\d,]+)")


def _smoke(module: str, args: list[str]) -> dict:
    cmd = [sys.executable, "-m", f"pipeline.platform.{module}", *args]
    t0 = time.monotonic()
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                           timeout=TIMEOUT, errors="replace")
        out = (r.stdout or "") + "\n" + (r.stderr or "")
        verdict = (_VERDICT_RE.search(out) or [None, None])[1] if _VERDICT_RE.search(out) else None
        caged_m = _CAGED_RE.search(out)
        caged = caged_m.group(1) if caged_m else None
        # Classify
        if r.returncode != 0:
            status = "ARG_OR_RUNTIME_ERROR"
        elif verdict:
            status = f"RAN ({verdict})"
        else:
            status = "RAN (no verdict line)"
        return {"module": module, "args": args, "exit": r.returncode, "status": status,
                "verdict": verdict, "cars_caged": caged,
                "secs": round(time.monotonic() - t0, 1),
                "tail": "\n".join(out.strip().splitlines()[-4:])}
    except subprocess.TimeoutExpired:
        return {"module": module, "args": args, "exit": None, "status": "TIMEOUT",
                "verdict": None, "cars_caged": None, "secs": TIMEOUT, "tail": "timeout"}


def main() -> None:
    # Accept multiple substring filters (OR match) so a targeted re-run can name
    # several modules: `validate_connectors.py bmw motor_es wallapop`.
    flts = sys.argv[1:]
    conns = [(m, a) for m, a in CONNECTORS if not flts or any(f in m for f in flts)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Merge into any existing matrix so a targeted re-run updates only its own
    # entries and preserves results from a prior full sweep (keyed by module).
    merged: dict[str, dict] = {}
    if OUT.exists():
        try:
            for r in json.loads(OUT.read_text(encoding="utf-8")):
                merged[r["module"]] = r
        except (ValueError, KeyError):
            pass
    for i, (module, args) in enumerate(conns, 1):
        print(f"[{i}/{len(conns)}] {module} {' '.join(args)} ...", flush=True)
        res = _smoke(module, args)
        merged[module] = res
        print(f"    -> {res['status']}  caged={res['cars_caged']}  ({res['secs']}s)", flush=True)
        OUT.write_text(json.dumps(list(merged.values()), indent=2), encoding="utf-8")
    # Summary over the FULL merged matrix
    results = list(merged.values())
    print("\n==================== VALIDATION MATRIX ====================")
    ok = [r for r in results if str(r.get("status", "")).startswith("RAN") and r.get("verdict")]
    print(f"  ran with verdict : {len(ok)}/{len(results)}")
    for r in sorted(results, key=lambda r: r["module"]):
        print(f"  {r['module']:<48} {r['status']:<24} caged={r['cars_caged']}")
    print(f"\n  matrix -> {OUT}")


if __name__ == "__main__":
    main()
