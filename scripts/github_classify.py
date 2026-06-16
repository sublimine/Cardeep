#!/usr/bin/env python3
"""Project the Cardeep A->F sealing backlog onto GitHub as a filterable board.

Single source of truth for the per-unit detail and verification evidence stays
in ``docs/SUPERPLAN.md``.  This script renders a thin *classification* layer on
top of GitHub so the same backlog becomes filterable by letter / status / gate /
area:

* labels   -> taxonomy (letter, status, gate, area)
* milestones -> the spend-gate phases (foundation, EUR0 config, spend, terminal)
* one issue per Sealing Unit (SU), linking back to SUPERPLAN for the full story

The script is **idempotent**: labels are upserted with ``--force``; milestones
and issues are matched by title and updated in place, never duplicated.  Sealed
units are created and then closed so the board honestly shows *open == remaining
work*, *closed == sealed*.  Safe to re-run after every SUPERPLAN edit.

Usage::

    python scripts/github_classify.py            # apply to GitHub
    python scripts/github_classify.py --dry-run  # print the plan, touch nothing

Requires an authenticated ``gh`` CLI with the ``repo`` scope.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO = "sublimine/Cardeep"
BLOB = f"https://github.com/{REPO}/blob/main"
SUPERPLAN = f"{BLOB}/docs/SUPERPLAN.md"

# --------------------------------------------------------------------------- #
# gh helpers
# --------------------------------------------------------------------------- #


def gh(*args: str, check: bool = True) -> str:
    """Run a gh command and return stdout (UTF-8).  Raises on non-zero exit."""
    proc = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"gh {' '.join(args)} failed ({proc.returncode}):\n{proc.stderr.strip()}"
        )
    return proc.stdout


# --------------------------------------------------------------------------- #
# Taxonomy
# --------------------------------------------------------------------------- #

# name -> (hex color, description)  -- ASCII names only (Windows-console safe)
LABELS: dict[str, tuple[str, str]] = {
    # by letter
    "A:producto": ("1D76DB", "A - El producto (DB viva servida)"),
    "B:obsesion": ("5319E7", "B - Verificar TODO"),
    "C:tier-1": ("B60205", "C - Tier-1 + arsenal anti-deteccion"),
    "D:coste": ("0E8A16", "D - Coste / LLM local"),
    "E:huella": ("006B75", "E - Huella + organizacion"),
    "F:metodo": ("FBCA04", "F - Metodo (los poderes)"),
    "fase-0": ("BFDADC", "Fase 0 - cimiento (prerequisito de A-F)"),
    "gaps-rojos": ("D93F0B", "Gaps rojos - desarrollar"),
    "terminal": ("0B0B0B", "Terminal - SPAIN-SEALED 52/52"),
    # by status
    "estado:sellado": ("0E8A16", "Sellado y verificado (cerrado)"),
    "estado:e0-completo": ("C2E0C6", "Completo a techo EUR0 (resto gated)"),
    "estado:parcial": ("FBCA04", "Parcial / deuda declarada"),
    "estado:pendiente": ("CCCCCC", "Pendiente / greenfield"),
    # by gate (what blocks the remainder)
    "gate:e0": ("0E8A16", "Hacible a EUR0 - sin bloqueo"),
    "gate:gasto": ("B60205", "Bloqueado por decision de gasto del Owner"),
    "gate:harvest": ("D93F0B", "Bloqueado por correr cosecha a escala"),
    "gate:data": ("D4A72C", "Bloqueado por datos externos"),
    "gate:hardware": ("5319E7", "Bloqueado por hardware (RAM/GPU)"),
    # by area
    "area:verificacion": ("1D76DB", "Stack de verificacion (VAM/ledger/Inquisicion)"),
    "area:conectores": ("006B75", "Conectores / scrapers / cosecha"),
    "area:identidad": ("8250DF", "Identidad: dealer/coche, dedup, cdp_code"),
    "area:geo": ("0E8A16", "Geo: pais/provincia/comarca/ciudad"),
    "area:delta": ("FBCA04", "Delta: altas/bajas/precio/foto/historial"),
    "area:api": ("B60205", "API viva + hardening"),
    "area:ops": ("D93F0B", "Ops: scheduler, alertas, auto-repair, evict"),
    "area:descubrimiento": ("BFD4F2", "Descubrimiento / denominador"),
}

# title -> description
MILESTONES: dict[str, str] = {
    "Fase 0 - Cimiento (EUR0)": (
        "Higiene, verdad y reproducibilidad. Prerequisito de todo A-F. COMPLETO."
    ),
    "EUR0 - Config A-Z (prerequisito de gasto)": (
        "Toda la implementacion hacible sin gastar: deploy reproducible, CI, "
        "runbooks, verificacion, API, delta, identidad, recetas. Es el "
        "prerequisito que el Owner puso para abrir gasto. COMPLETO."
    ),
    "Fase de gasto - Harvest / Data / Hardware": (
        "Lo que se desbloquea cuando el Owner abre gasto: drains a escala, "
        "fuentes de datos externas, LLM local. Diferido por decision del Owner."
    ),
    "Terminal - SPAIN-SEALED 52/52": (
        "Sello por provincia: denominador medido + numerador VAM-estable + "
        "vehicle-recall. Capa A firmable EUR0; Capa B = roadmap deferido."
    ),
}

M_FASE0 = "Fase 0 - Cimiento (EUR0)"
M_E0 = "EUR0 - Config A-Z (prerequisito de gasto)"
M_GASTO = "Fase de gasto - Harvest / Data / Hardware"
M_TERMINAL = "Terminal - SPAIN-SEALED 52/52"


@dataclass
class SU:
    id: str
    title: str
    summary: str
    labels: list[str]
    milestone: str
    closed: bool  # True -> sealed -> create then close
    recon: str | None = None  # path under repo root, if a recon doc exists

    @property
    def issue_title(self) -> str:
        return f"{self.id} - {self.title}"

    def body(self) -> str:
        lines = [
            f"**Punto:** {self.summary}",
            "",
            f"**Detalle autoritativo + evidencia de verificacion:** "
            f"[`docs/SUPERPLAN.md` SS4 - {self.id}]({SUPERPLAN})",
        ]
        if self.recon:
            lines.append(f"**Recon / dossier:** [`{self.recon}`]({BLOB}/{self.recon})")
        lines += [
            "",
            "---",
            "_Issue generado por `scripts/github_classify.py` desde SUPERPLAN "
            "(fuente de verdad). No editar a mano: re-sincroniza el script._",
        ]
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# The backlog (mirrors docs/SUPERPLAN.md SS4)
# --------------------------------------------------------------------------- #

SUS: list[SU] = [
    # ----- FASE 0 (all sealed) -----
    SU("SU-0.1", "Eliminar frontend (D2)",
       "cardeep-web archivado + folder borrado; sin frontend por decision del Owner.",
       ["fase-0", "estado:sellado", "gate:e0", "area:ops"], M_FASE0, True),
    SU("SU-0.2", "Reconciliar ledger de migraciones",
       "schema_migrations == schema vivo; rebuild reproduce el schema sin error.",
       ["fase-0", "estado:sellado", "gate:e0", "area:verificacion"], M_FASE0, True),
    SU("SU-0.3", "Commitear todo lo untracked",
       "git status limpio salvo gitignored; codigo+recetas en main.",
       ["fase-0", "estado:sellado", "gate:e0", "area:ops"], M_FASE0, True),
    SU("SU-0.4", "Linkar verdicts de sellos",
       "todo *_run sellado con vam_verdict_id -> verification_verdict no-NULL.",
       ["fase-0", "estado:sellado", "gate:e0", "area:verificacion"], M_FASE0, True),
    SU("SU-0.5", "Corregir ontologia cadena",
       "0 entity kind='cadena' (reasignadas a organization); Flexicar rollup sano.",
       ["fase-0", "estado:sellado", "gate:e0", "area:identidad"], M_FASE0, True),
    SU("SU-0.6", "Auditoria de disco + eviccion",
       "politica de eviccion configurada+verificada; margen de disco evaluado.",
       ["fase-0", "estado:sellado", "gate:e0", "area:ops"], M_FASE0, True),
    # ----- A - EL PRODUCTO -----
    SU("SU-A1", "Codigo unico (B1) - dealer canonico",
       "dup<0,1% por >=2 vias; v_canonical integra; dealer-count 40.016 servido; verdict 1121.",
       ["A:producto", "estado:sellado", "gate:e0", "area:identidad"], M_E0, True),
    SU("SU-A2", "Descubrir - denominador P",
       "beta SELLADO (S_obs 38.555); phi/Chao2 GATEADO (data); ancla oficial CNAE-451 (F8 94,3%).",
       ["A:producto", "estado:parcial", "gate:data", "area:descubrimiento"], M_GASTO, False),
    SU("SU-A3", "Scrapear TODO el stock - exhaustividad",
       "B9 gate corrido; ~34 fuentes disparan declared_total (EUR0 hecho); drains reales = harvest-gated.",
       ["A:producto", "estado:parcial", "gate:harvest", "area:conectores"], M_GASTO, False,
       recon="docs/recon/SUA3_EXHAUSTIVIDAD_RECON.md"),
    SU("SU-A4", "Delta uniforme - altas/bajas/precio/foto/historial",
       "NEW(todos)+PRICE/KM/PHOTO(26 conectores)+GONE(auto 34 fuentes). 2a-pasada en vivo = harvest-gated.",
       ["A:producto", "estado:parcial", "gate:harvest", "area:delta"], M_GASTO, False,
       recon="docs/recon/SUA4_DELTA_RECON.md"),
    SU("SU-A5", "Receta guardada - bundle per-dealer",
       "v_dealer_recipe: 37.041 connector + 537 per-dealer cubiertos. recipe-hunting (23.894 sin inv) = Fase-B.",
       ["A:producto", "estado:parcial", "gate:harvest", "area:conectores"], M_GASTO, False,
       recon="docs/recon/SUA5_RECETAS_RECON.md"),
    SU("SU-A6", "Geo pais/provincia/ciudad + jerarquia",
       "comarca 99,93% + sentinel-drift 0 + within-province 0 hard. muni-gap 6.601 = DATA-blocked.",
       ["A:producto", "estado:parcial", "gate:data", "area:geo"], M_GASTO, False,
       recon="docs/recon/SUA6_GEO_RECON.md"),
    SU("SU-A7", "Codigo unico por dealer (cdp_code inmutable)",
       "390.621 entities = 390.621 cdp distintos, 0 nulls; DB-enforced; minter determinista.",
       ["A:producto", "estado:e0-completo", "gate:e0", "area:identidad"], M_E0, True),
    SU("SU-A8", "Falla -> alerta -> auto-repara -> no cae",
       "lazo EUR0 cerrado (record_run->breaker->auto_repair->alert-origen-exacto->recovery); test inyeccion 8 verde.",
       ["A:producto", "estado:sellado", "gate:e0", "area:ops"], M_E0, True,
       recon="docs/recon/SUA8_AUTOREPAIR_RECON.md"),
    SU("SU-A9", "API viva sirviendo solo sellado",
       "FastAPI sirve v_canonical/v_canonical_vehicle; sin hazard sin-LIMIT; envelope; auth; suite 85 verde.",
       ["A:producto", "estado:sellado", "gate:e0", "area:api"], M_E0, True),
    # ----- B - LA OBSESION -----
    SU("SU-B1", "Ledger de verificacion profundo (0026)",
       "quorum CHECK + audit hash-chain + rol inquisitor read-only; rebuild 0001->0026 OK.",
       ["B:obsesion", "estado:sellado", "gate:e0", "area:verificacion"], M_E0, True),
    SU("SU-B2", "Inquisicion V3 + completion (V2/V3/V4)",
       "139 tests inquisition; 5 lentes + prosecutor atomico + invariante DB. G5/Lens-C live = harvest-gated.",
       ["B:obsesion", "estado:e0-completo", "gate:harvest", "area:verificacion"], M_GASTO, False,
       recon="docs/recon/SUB2_INQUISITION_RECON.md"),
    SU("SU-B3", "Confesar gaps (UNVERIFIED/REFUTED first-class)",
       "veredictos no-confiables servidos etiquetados o retenidos; doctrina aplicada.",
       ["B:obsesion", "estado:sellado", "gate:e0", "area:verificacion"], M_E0, True),
    # ----- C - TIER-1 + ARSENAL -----
    SU("SU-C1", "P0.5 anti-deteccion spike",
       "re-probar 5 OPEN + 2 walled; ClientHello byte-diff vs Chrome; Wallapop/Adevinta token.",
       ["C:tier-1", "estado:pendiente", "gate:gasto", "area:conectores"], M_GASTO, False),
    SU("SU-C2", "Cazar receta de cada Tier-1",
       "7 Tier-1 con receta reproducible + 2-way count verificado libre (EUR0). Correr a escala = harvest.",
       ["C:tier-1", "estado:e0-completo", "gate:harvest", "area:conectores"], M_GASTO, False),
    SU("SU-C3", "Sellar B7 (dedup coches)",
       "1.486.285 coches unicos servidos via v_canonical_vehicle; verdict UNVERIFIED (mono-metodo, excepcion declarada).",
       ["C:tier-1", "estado:e0-completo", "gate:e0", "area:identidad"], M_E0, True),
    # ----- D - COSTE / LLM -----
    SU("SU-D1", "LLM local para lo masivo",
       "Ollama+3 modelos instalados; correrlos ahogaria la DB viva (2,1GB RAM libre, sin CUDA). Diferido hardware.",
       ["D:coste", "estado:parcial", "gate:hardware", "area:ops"], M_GASTO, False),
    SU("SU-D2", "Eficiente y blindado (rate-limit + cache)",
       "API rate-limit (slowapi) + cache TTL (cachetools, no cachea vivo); governor anti-cicatriz 25/25.",
       ["D:coste", "estado:e0-completo", "gate:e0", "area:api"], M_E0, True),
    # ----- E - HUELLA + ORGANIZACION -----
    SU("SU-E1", "Todo a main documentado (runbook A-Z)",
       "verification stack documentado A-Z + DEPLOY/OPERATE runbooks; arbol limpio en main.",
       ["E:huella", "estado:e0-completo", "gate:e0", "area:ops"], M_E0, True,
       recon="docs/architecture/10-VERIFICATION-STACK.md"),
    SU("SU-E2", "Separacion fisica Tier-1 + reshape geo",
       "580 recetas via git mv a countries/ES/<prov>/<comarca>/<city>/dealers/<cdp>/ + _tier1/ + _platforms/.",
       ["E:huella", "estado:e0-completo", "gate:e0", "area:ops"], M_E0, True),
    # ----- F - METODO -----
    SU("SU-F1", "Workflows de OPS continua",
       "scheduler durable crash-safe (APScheduler+PG jobstore) + cadencia delta cada 6h. E2E-harvest = gated.",
       ["F:metodo", "estado:e0-completo", "gate:e0", "area:ops"], M_E0, True),
    SU("SU-F2", "Integrar herramientas (free+viable)",
       "lxml+bs4 suficientes; selectolax/extruct/libpostal evaluados y diferidos anti-YAGNI con causa.",
       ["F:metodo", "estado:e0-completo", "gate:e0", "area:ops"], M_E0, True),
    SU("SU-F3", "Agotar alternativas antes de aceptar limite",
       "ceilings solo tras probar, declarados con causa; doctrina aplicada en cada gate.",
       ["F:metodo", "estado:sellado", "gate:e0", "area:ops"], M_E0, True),
    # ----- GAPS ROJOS -----
    SU("SU-R1", "Desguace E2E (numerador)",
       "1.895 desguaces, 283 con web, 0 inventario. Greenfield (Opisto/own-site). Frontera del numerador EUR0.",
       ["gaps-rojos", "estado:pendiente", "gate:harvest", "area:conectores"], M_GASTO, False),
    SU("SU-R2", "Concesionario harvest (mas alla de OEM-VO)",
       "cosecha FACONAUTO; servido sube de 11,6% con VAM.",
       ["gaps-rojos", "estado:pendiente", "gate:harvest", "area:conectores"], M_GASTO, False),
    SU("SU-R3", "Filtrado sells_cars (sin ruido)",
       "6 garajes con inventario marcados EUR0; 7.195 sin inventario = DATA-gated (mejor hueco que mentira).",
       ["gaps-rojos", "estado:parcial", "gate:data", "area:identidad"], M_GASTO, False),
    SU("SU-R4", "Cobertura 100% + cierre (Canarias/Ceuta/Melilla)",
       "cada segmento sellado o gap-con-causa; islas/ciudades autonomas cerradas.",
       ["gaps-rojos", "estado:pendiente", "gate:harvest", "area:descubrimiento"], M_GASTO, False),
    # ----- TERMINAL -----
    SU("SU-SEAL", "SPAIN-SEALED 52/52",
       "por provincia: denominador medido + numerador VAM-estable + recall. Capa A EUR0; Capa B deferido.",
       ["terminal", "estado:parcial", "gate:gasto", "area:verificacion"], M_TERMINAL, False),
]


# --------------------------------------------------------------------------- #
# Sync logic
# --------------------------------------------------------------------------- #


def ensure_labels(dry: bool) -> None:
    print(f"== labels ({len(LABELS)}) ==")
    for name, (color, desc) in LABELS.items():
        if dry:
            print(f"  [dry] upsert label {name} #{color}")
            continue
        gh("label", "create", name, "--color", color, "--description", desc,
           "--force", "--repo", REPO)
        print(f"  ok   {name}")


def ensure_milestones(dry: bool) -> None:
    existing = {
        m["title"]: m["number"]
        for m in json.loads(
            gh("api", f"repos/{REPO}/milestones", "--paginate",
               "-q", "[.[] | {title, number}]") or "[]"
        )
    }
    print(f"== milestones ({len(MILESTONES)}) ==")
    for title, desc in MILESTONES.items():
        if title in existing:
            if not dry:
                gh("api", f"repos/{REPO}/milestones/{existing[title]}", "-X", "PATCH",
                   "-f", f"description={desc}")
            print(f"  ok   (exists) {title}")
            continue
        if dry:
            print(f"  [dry] create milestone {title}")
            continue
        gh("api", f"repos/{REPO}/milestones", "-f", f"title={title}",
           "-f", f"description={desc}", "-f", "state=open")
        print(f"  ok   (new) {title}")


def load_existing_issues() -> dict[str, dict]:
    raw = gh("issue", "list", "--repo", REPO, "--state", "all", "--limit", "500",
             "--json", "number,title,state")
    return {i["title"]: i for i in json.loads(raw or "[]")}


def ensure_issue(su: SU, existing: dict[str, dict], dry: bool) -> None:
    title = su.issue_title
    body = su.body()
    cur = existing.get(title)
    if dry:
        action = "update" if cur else "create"
        state = "closed" if su.closed else "open"
        print(f"  [dry] {action:6} #{cur['number'] if cur else '?'} [{state}] "
              f"{title}  {su.labels}")
        return

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(body)
        body_file = fh.name
    try:
        if cur is None:
            args = ["issue", "create", "--repo", REPO, "--title", title,
                    "--body-file", body_file, "--milestone", su.milestone]
            for lab in su.labels:
                args += ["--label", lab]
            url = gh(*args).strip()
            num = url.rstrip("/").split("/")[-1]
            print(f"  ok   create #{num} {title}")
        else:
            num = str(cur["number"])
            args = ["issue", "edit", num, "--repo", REPO, "--body-file", body_file,
                    "--milestone", su.milestone]
            for lab in su.labels:
                args += ["--add-label", lab]
            gh(*args)
            print(f"  ok   update #{num} {title}")
        # converge state
        want_closed = su.closed
        is_closed = cur is not None and cur["state"].upper() == "CLOSED"
        if want_closed and not is_closed:
            gh("issue", "close", num, "--repo", REPO,
               "--reason", "completed")
        elif (not want_closed) and is_closed:
            gh("issue", "reopen", num, "--repo", REPO)
    finally:
        Path(body_file).unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="print plan, touch nothing")
    args = ap.parse_args()
    dry = args.dry_run

    # sanity: gh authed + repo reachable
    gh("repo", "view", REPO, "--json", "name")

    ensure_labels(dry)
    ensure_milestones(dry)

    existing = {} if dry else load_existing_issues()
    if dry:
        try:
            existing = load_existing_issues()
        except Exception:
            existing = {}
    print(f"== issues ({len(SUS)}) ==")
    closed = sum(1 for s in SUS if s.closed)
    print(f"   (sealed->closed: {closed} | open: {len(SUS) - closed})")
    for su in SUS:
        ensure_issue(su, existing, dry)

    print("done." if not dry else "dry-run complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
