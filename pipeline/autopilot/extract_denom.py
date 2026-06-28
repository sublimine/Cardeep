"""DENOMINATOR extractor (auto-pack pieza 5) — Eurostat SBS G45 + GLEIF.

Turns two €0, free-reuse public sources into a country census the MSE seal can
triangulate N̂ against (`pipeline/exhaustiveness/triangulation.py`):

  (a) **Eurostat SBS** — NACE Rev.2 **G45** ("Wholesale and retail trade and repair
      of motor vehicles and motorcycles"), enterprise counts per NUTS region.
      *Reuse:* Eurostat open data, free reuse with attribution. This is the
      AUTO-extractable, reliable figure: the national all-segment denominator.
  (b) **GLEIF LEI Golden Copy** — registered legal entities per jurisdiction.
      *Reuse:* CC0. An INDEPENDENT second mechanism (LEI issuance vs statistical
      business register) — but all-industry, so a corroboration, never a dealer
      denominator.

THE DOCTRINE THIS MODULE ENFORCES (the load-bearing checkpoint)
---------------------------------------------------------------
The **national all-segment** count is auto-extractable and tagged ``[MEDIDO]``.
The **per-segment split** (compraventa / concesionario / desguace) is **NOT**
auto-derivable:
  * NACE G45 does not separate franchised dealers from independent compraventa
    (both are 45.11), and scrappage / end-of-life-vehicle centres live in NACE
    38.31 — outside G45 entirely.
  * GLEIF has no industry/sector field, so it cannot isolate motor-trade entities.
So the split is a **CHECKPOINT (needs_audit)**: the extractor emits only the
national/region all-segment anchors and **never fabricates the split**, degrading
honestly exactly like the seal's ``no_anchor`` (mirrors how ES required FACONAUTO
+ DGT CAT — country-specific authorities — to obtain its split).

NETWORK ISOLATION
-----------------
Parsing is pure and deterministic (the tested core). The live HTTP fetch is the
separate ``fetch_*`` seam below; tests never touch it. Wiring/gating the live
fetch (and teaching ``triangulation.CENSUS_CSV_NAME`` to resolve this file by
default per-country) belongs to the orchestrator phase, not the extractor.
"""

from __future__ import annotations

import csv
import io
import re
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# --- provenance vocabulary (mirrors countries/ES/census/SOURCE.md) ----------------

MEASURED = "[MEDIDO]"
ESTIMATED = "[ESTIMADO DECLARADO]"

# Output census filename. Named for its true provenance (Eurostat SBS NACE G45),
# NOT the ES-legacy `dirce_cnae451.csv`: putting Eurostat/GLEIF data in a file
# called "dirce_cnae451" would misstate provenance. The seam reads it via an
# explicit `path=` (its documented back-compat entry point); resolving this name
# by default per-country is an engine open item (triangulation.py:27), not ours.
DENOM_CSV_NAME = "denominator_g45.csv"

# Eurostat SBS defaults. indic_sb V11110 = "Enterprises - number".
DEFAULT_NACE = "G45"
DEFAULT_INDIC = "V11110"
EUROSTAT_DATASET = "sbs_r_nuts2021"  # regional SBS, NACE Rev.2, per-NUTS

# Live endpoints. [ASSUMED endpoint shape] — the verified contract of this module
# is the PARSER; the exact query wiring is finalized + gated in the orchestrator.
EUROSTAT_API_BASE = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data"
)
GLEIF_GOLDEN_COPY_NOTE = "GLEIF LEI Golden Copy (Level 1, LEI-CDF), CC0."

# GLEIF column candidates (Golden Copy LEI-CDF uses dotted names).
_GLEIF_JURIS = ("Entity.LegalJurisdiction", "LegalJurisdiction")
_GLEIF_COUNTRY = (
    "Entity.LegalAddress.Country",
    "LegalAddress.Country",
    "Entity.HeadquartersAddress.Country",
)
_GLEIF_STATUS = ("Registration.RegistrationStatus", "RegistrationStatus")
_GLEIF_ELF = (
    "Entity.LegalForm.EntityLegalFormCode",
    "LegalForm.EntityLegalFormCode",
    "LegalForm",
)
_GLEIF_ACTIVE = "ISSUED"  # the only active LEI registration status


# --- value parsing helpers --------------------------------------------------------

def _year_key(year: str) -> int:
    m = re.search(r"\d{4}", year or "")
    return int(m.group()) if m else -1


def _parse_value(cell: str) -> int | None:
    """Parse one Eurostat TSV value cell. ``:`` (and flag-only) means missing.

    Cells may carry a trailing flag letter after whitespace (e.g. ``1200 e``) and
    use ``:`` for not-available. Returns an int, or None when missing.
    """
    s = (cell or "").strip()
    if not s:
        return None
    tok = s.split()[0]  # drop flag letters (`1200 e` -> `1200`)
    if tok in (":", "-", ""):
        return None
    cleaned = re.sub(r"[^0-9.]", "", tok)
    if not cleaned or cleaned == ".":
        return None
    try:
        return int(round(float(cleaned)))
    except ValueError:
        return None


# --- parsed-source dataclasses ----------------------------------------------------

@dataclass(frozen=True)
class EurostatParse:
    national: int | None
    regions: dict[str, int]
    year: str | None
    nace: str
    indic: str


@dataclass(frozen=True)
class GleifParse:
    total: int
    by_legal_form: dict[str, int]
    active_only: bool


@dataclass(frozen=True)
class RegionRow:
    region_code: str
    n_external: int
    tag: str = MEASURED


@dataclass(frozen=True)
class GleifCrosscheck:
    total: int
    by_legal_form: dict[str, int]
    note: str


@dataclass(frozen=True)
class Checkpoint:
    name: str
    status: str
    reason: str


# --- (a) Eurostat SBS G45 ---------------------------------------------------------

def parse_eurostat_sbs_tsv(
    tsv_text: str,
    country_code: str,
    *,
    nace: str = DEFAULT_NACE,
    indic: str = DEFAULT_INDIC,
) -> EurostatParse:
    """Parse a Eurostat SBS bulk TSV into national + per-NUTS-region counts.

    Header form: ``dim1,dim2,...,geo\\TIME_PERIOD`` then tab-joined years; each data
    line is comma-joined dimension values, tab, then one value cell per year.

    Rows are filtered to ``nace_r2 == nace`` and ``indic_sb == indic``. The geo
    dimension classifies rows: ``geo == country_code`` is the national (NUTS0)
    figure; a longer ``geo`` starting with the country code is a sub-national
    region; anything else is ignored. The reference year is the latest year for
    which the national row has a value (else the latest year any region has one);
    every figure is read at that single year so nothing mixes periods.
    """
    cc = country_code.upper()
    lines = [ln for ln in tsv_text.splitlines() if ln.strip()]
    if not lines:
        return EurostatParse(None, {}, None, nace, indic)

    header = lines[0].split("\t")
    dim_names = header[0].split("\\")[0].split(",")
    years = [c.strip() for c in header[1:]]

    national_by_year: dict[str, int] = {}
    region_by_year: dict[str, dict[str, int]] = {}
    for ln in lines[1:]:
        cells = ln.split("\t")
        dims = dict(zip(dim_names, cells[0].split(",")))
        if dims.get("nace_r2") != nace or dims.get("indic_sb") != indic:
            continue
        geo = (dims.get("geo") or "").strip().upper()
        if geo == cc:
            target = national_by_year
        elif geo.startswith(cc) and len(geo) > len(cc):
            target = region_by_year.setdefault(geo, {})
        else:
            continue
        for yr, cell in zip(years, cells[1:]):
            val = _parse_value(cell)
            if val is not None:
                target[yr] = val

    def _latest(year_iter) -> str | None:
        ys = list(year_iter)
        return max(ys, key=_year_key) if ys else None

    ref_year = _latest(national_by_year.keys())
    if ref_year is None:
        all_region_years: set[str] = set()
        for dy in region_by_year.values():
            all_region_years |= set(dy)
        ref_year = _latest(all_region_years)

    national = national_by_year.get(ref_year) if ref_year else None
    regions: dict[str, int] = {}
    if ref_year:
        for geo, dy in region_by_year.items():
            if ref_year in dy:
                regions[geo] = dy[ref_year]
    return EurostatParse(national, dict(sorted(regions.items())), ref_year, nace, indic)


# --- (b) GLEIF LEI Golden Copy ----------------------------------------------------

def _first(row: dict[str, str], names: tuple[str, ...]) -> str:
    for n in names:
        v = row.get(n)
        if v:
            return v.strip()
    return ""


def parse_gleif_csv(
    csv_text: str,
    country_code: str,
    *,
    active_only: bool = True,
) -> GleifParse:
    """Count GLEIF legal entities in a jurisdiction (an independent cross-check).

    A row belongs to ``country_code`` when its legal jurisdiction's leading two
    letters match (covers sub-jurisdictions like ``XX-1``); failing a jurisdiction
    value, its legal-address country is used. When ``active_only`` (default), only
    ``ISSUED`` (active) registrations are counted. This is ALL-INDUSTRY: it is a
    corroboration of registry liveness, never a motor-trade denominator.
    """
    cc = country_code.upper()
    forms: Counter[str] = Counter()
    total = 0
    for row in csv.DictReader(io.StringIO(csv_text)):
        juris = _first(row, _GLEIF_JURIS).upper()
        country = _first(row, _GLEIF_COUNTRY).upper()
        status = _first(row, _GLEIF_STATUS).upper()
        belongs = (juris[:2] == cc) if juris else (country == cc)
        if not belongs:
            continue
        if active_only and status != _GLEIF_ACTIVE:
            continue
        total += 1
        elf = _first(row, _GLEIF_ELF)
        if elf:
            forms[elf] += 1
    return GleifParse(total, dict(sorted(forms.items())), active_only)


# --- the result ------------------------------------------------------------------

@dataclass
class DenominatorResult:
    country_code: str
    national_total: int
    national_tag: str
    regions: list[RegionRow]
    gleif: GleifCrosscheck | None
    checkpoints: list[Checkpoint]
    source_meta: dict = field(default_factory=dict)

    def census_rows(self) -> list[tuple[str, str, str]]:
        """CSV rows ``(province_code, segment, n_external)`` — ALL-SEGMENT only.

        ``segment`` is always blank: the per-segment split is a checkpoint, not
        data. Regions (sorted) come first, the national roll-up last — mirroring
        the ES anchor's province-then-national ordering.
        """
        rows = [
            (r.region_code, "", str(r.n_external))
            for r in sorted(self.regions, key=lambda x: x.region_code)
        ]
        rows.append(("", "", str(self.national_total)))
        return rows

    def write_census_csv(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(("province_code", "segment", "n_external"))
            for row in self.census_rows():
                w.writerow(row)
        return path

    def write_source_md(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._source_md(), encoding="utf-8")
        return path

    def _source_md(self) -> str:
        m = self.source_meta
        cc = self.country_code
        out: list[str] = []
        A = out.append
        A(f"# External triangulation anchor — {cc} (auto-pack)")
        A("")
        A(f"> Provenance for `{DENOM_CSV_NAME}`, the independent census the")
        A("> exhaustiveness seal contrasts against N̂")
        A("> (`pipeline/exhaustiveness/triangulation.py`). €0, free-reuse sources only.")
        A("> Auto-derived by `pipeline/autopilot/extract_denom.py`. No fabricated figures.")
        A("")
        A("The CSV header is `province_code,segment,n_external`; a blank `province_code`")
        A("and/or `segment` encodes a national / all-segment anchor (the `(None, ...)`")
        A("keys `seal.compute` consumes). `province_code` carries this country's L1")
        A("region code (the NUTS->pack-L1 cross-walk is the geo pack's responsibility).")
        A("")
        A("## What is measured vs estimated")
        A("")
        A(f"- **{MEASURED}** — a direct external count, no apportionment.")
        A(f"- **{ESTIMATED}** — an honest apportionment of a real national figure,")
        A("  declared as such; never presented as a measured figure.")
        A("")
        A("## National anchor")
        A("")
        A("| key | value | basis | tag |")
        A("|-----|-------|-------|-----|")
        A(
            f"| `(,)` all-segment | {self.national_total} | Eurostat SBS {m.get('nace')} "
            f"`{m.get('indic')}` ({m.get('dataset')}, {m.get('year')}); "
            f"{m.get('rollup_note')} | {self.national_tag} |"
        )
        A("")
        A(f"The national all-segment figure is the count of NACE Rev.2 {m.get('nace')}")
        A("motor-vehicle trade enterprises — the AUTO-extractable, reliable")
        A("denominator. It is a registral universe (sale + repair of motor vehicles),")
        A("read as a ceiling over the dealer point-of-sale count.")
        A("")
        if self.regions:
            A("## Per-region anchors (all-segment)")
            A("")
            A("| region_code | value | basis | tag |")
            A("|-------------|-------|-------|-----|")
            for r in sorted(self.regions, key=lambda x: x.region_code):
                A(
                    f"| {r.region_code} | {r.n_external} | Eurostat SBS {m.get('nace')} "
                    f"per-NUTS ({m.get('dataset')}, {m.get('year')}) | {r.tag} |"
                )
            A("")
        A("## Independent cross-check — GLEIF LEI Golden Copy")
        A("")
        if self.gleif is not None:
            A(
                f"- Active LEI-registered legal entities in jurisdiction `{cc}`: "
                f"**{self.gleif.total}**. {self.gleif.note}"
            )
            if self.gleif.by_legal_form:
                forms = ", ".join(
                    f"{k}={v}" for k, v in sorted(self.gleif.by_legal_form.items())
                )
                A(f"- By legal form (ELF): {forms}.")
            A("- GLEIF is a **different mechanism** (LEI issuance vs statistical business")
            A("  register), which is what makes it a valid orthogonal corroboration; it is")
            A("  **all-industry**, so it is NOT emitted as an `n_external` denominator row.")
        else:
            A("- (not provided for this extraction)")
        A("")
        A("## CHECKPOINT — per-segment split (needs_audit)")
        A("")
        for c in self.checkpoints:
            A(f"- **{c.name}** — status `{c.status}`.")
            A(f"  {c.reason}")
        A("")
        A("Consequently this census emits **only all-segment anchors**. For per-segment")
        A("strata the seal reports `no_anchor` rather than triangulating against a")
        A("fabricated split — the honest degradation.")
        A("")
        A("## Refresh procedure")
        A("")
        A(f"1. Re-fetch Eurostat SBS `{m.get('dataset')}` for NACE `{m.get('nace')}`,")
        A(f"   indicator `{m.get('indic')}`, country `{cc}` (latest year).")
        A("2. Re-fetch the GLEIF Golden Copy and recount active entities for the")
        A("   jurisdiction.")
        A(f"3. Re-run `pipeline/autopilot/extract_denom.py` to rebuild `{DENOM_CSV_NAME}`")
        A("   and this SOURCE.md, then re-run `tests/test_extract_denom.py`.")
        A("")
        return "\n".join(out) + "\n"


_SEGMENT_SPLIT_CHECKPOINT = Checkpoint(
    name="segment_split",
    status="needs_audit",
    reason=(
        "The per-segment split (compraventa / concesionario / desguace) is NOT "
        "derivable from Eurostat G45 (NACE does not separate franchised dealers "
        "from independent compraventa - both are 45.11 - and scrappage/ELV centres "
        "sit in NACE 38.31, outside G45) nor from GLEIF (all-industry, no sector "
        "field). Resolving it requires country-specific authorities (a franchised-"
        "dealer association register + an ELV/scrappage register), exactly as ES "
        "used FACONAUTO + DGT CAT. The extractor emits only the all-segment anchors "
        "and leaves the split as a judgment checkpoint; it is never invented."
    ),
)


def extract_denominator(
    country_code: str,
    *,
    sbs_tsv: str,
    gleif_csv: str | None = None,
    nace: str = DEFAULT_NACE,
    indic: str = DEFAULT_INDIC,
    dataset: str = EUROSTAT_DATASET,
) -> DenominatorResult:
    """Build a ``DenominatorResult`` from Eurostat SBS + (optional) GLEIF text.

    Pure and deterministic: no network. The national all-segment figure is taken
    from the NUTS0 row when present, else rolled up from the measured regions;
    both are ``[MEDIDO]``. If neither exists the function raises ``ValueError``
    rather than fabricating a denominator. The per-segment split is always emitted
    as a ``needs_audit`` checkpoint and never invented.
    """
    cc = country_code.upper()
    parsed = parse_eurostat_sbs_tsv(sbs_tsv, cc, nace=nace, indic=indic)
    regions = [RegionRow(code, n) for code, n in sorted(parsed.regions.items())]

    national = parsed.national
    rollup_note = "direct NUTS0 figure"
    if national is None:
        if regions:
            national = sum(r.n_external for r in regions)
            rollup_note = "sum of measured NUTS regions (no NUTS0 row present)"
        else:
            raise ValueError(
                f"no Eurostat SBS {nace}/{indic} figure for {cc!r}: refusing to "
                "fabricate a denominator (honest hard-fail)."
            )

    gleif = None
    if gleif_csv is not None:
        g = parse_gleif_csv(gleif_csv, cc)
        gleif = GleifCrosscheck(
            total=g.total,
            by_legal_form=g.by_legal_form,
            note=(
                "Independent registry mechanism (LEI issuance), ALL-INDUSTRY: a "
                "corroboration of registry liveness, NOT a motor-trade denominator."
            ),
        )

    return DenominatorResult(
        country_code=cc,
        national_total=national,
        national_tag=MEASURED,
        regions=regions,
        gleif=gleif,
        checkpoints=[_SEGMENT_SPLIT_CHECKPOINT],
        source_meta={
            "dataset": dataset,
            "nace": nace,
            "indic": indic,
            "year": parsed.year,
            "rollup_note": rollup_note,
        },
    )


# --- network seam (LIVE; never exercised by tests) --------------------------------

def fetch_url_text(url: str, *, timeout: int = 60) -> str:
    """LIVE network GET -> decoded text. Isolated so parsing stays pure/testable."""
    req = urllib.request.Request(url, headers={"User-Agent": "cardeep-autopilot/1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (vetted host)
        return resp.read().decode("utf-8", errors="replace")


def eurostat_sbs_url(
    country_code: str,
    *,
    nace: str = DEFAULT_NACE,
    indic: str = DEFAULT_INDIC,
    dataset: str = EUROSTAT_DATASET,
) -> str:
    """Build the Eurostat dissemination TSV URL. [ASSUMED endpoint shape]."""
    params = {"format": "TSV", "nace_r2": nace, "indic_sb": indic, "geo": country_code}
    return f"{EUROSTAT_API_BASE}/{dataset}/?{urllib.parse.urlencode(params)}"


def fetch_eurostat_sbs_tsv(country_code: str, **kw) -> str:
    """LIVE: fetch the Eurostat SBS TSV for a country. Not used by tests."""
    return fetch_url_text(eurostat_sbs_url(country_code, **kw))
