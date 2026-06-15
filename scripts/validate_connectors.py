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
    ("oem_bmw_mini_wholesale", ["--brand", "bmw", "--pages", "1"]),
    ("spoticar_wholesale", ["--pages", "1"]),
    ("dasweltauto_wholesale", ["--provinces", "1", "--pages", "1"]),
    # --- Tier-1 marketplaces ---
    ("coches_net_wholesale", ["--pages", "1"]),
    ("milanuncios_wholesale", ["--pages", "1"]),
    ("coches_com_wholesale", ["--pages", "1"]),
    ("motor_es_wholesale", ["--pages", "1"]),
    ("autocasion_facet", ["--makes", "audi"]),
    # --- chains / rentacar / subastas ---
    ("group_vo_chains_wholesale", ["--members", "flexicar", "--pages", "1"]),
    ("group_rentacar_vo_wholesale", ["--member", "okmobility"]),
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
    ("family_builder_wix_ueni_google_sites_basekit__wholesale", ["--from-db", "--limit", "3"]),
    ("family_unreachable_wholesale", ["--dealers", "hrmotor.com"]),
]

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
    flt = sys.argv[1] if len(sys.argv) > 1 else None
    conns = [(m, a) for m, a in CONNECTORS if not flt or flt in m]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = []
    for i, (module, args) in enumerate(conns, 1):
        print(f"[{i}/{len(conns)}] {module} {' '.join(args)} ...", flush=True)
        res = _smoke(module, args)
        results.append(res)
        print(f"    -> {res['status']}  caged={res['cars_caged']}  ({res['secs']}s)", flush=True)
        OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")  # incremental save
    # Summary
    print("\n==================== VALIDATION MATRIX ====================")
    ok = [r for r in results if r["status"].startswith("RAN") and r["verdict"]]
    print(f"  ran with verdict : {len(ok)}/{len(results)}")
    for r in results:
        print(f"  {r['module']:<48} {r['status']:<24} caged={r['cars_caged']}")
    print(f"\n  matrix -> {OUT}")


if __name__ == "__main__":
    main()
