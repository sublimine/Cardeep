"""Fase E2 — the COUNTRY-AUTOPILOT ORCHESTRATOR LOOP: the capstone that UNITES every
country-autopilot piece into one driveable machine (``plans/country-autopilot/01-ARCHITECTURE.md``
§E + ``docs/generic-engine-bible/COVER-NEW-COUNTRY.md``).

This module owns NOTHING new — it ORCHESTRATES what already exists, in the exact order of the
bible's COVER(CC) progression, for ONE synthetic country at a time:

    RESEARCH(KNOW_COUNTRY) -> PROPONER(countries/<CC>/ + country.toml + PLAN)
       -> AUDITAR(5 niveles) -> [PUERTA] -> EJECUTAR(dry-run/sintético; vivo=gate)
       -> SUPERVISAR(per-país) -> SELLAR(MSE/país)

The pieces it threads (all VERIFIED first-hand, nothing re-implemented):
  * ``pipeline.autopilot.state``        — the ``cover(CC)`` campaign state machine (mig 0067).
  * ``pipeline.autopilot.extract_geo``  — GeoNames -> ``countries/<CC>/geo/`` (RESEARCH).
  * ``pipeline.autopilot.extract_denom``— Eurostat SBS + GLEIF -> ``countries/<CC>/census/`` (RESEARCH).
  * ``pipeline.country_profile``        — the ``country.toml`` manifest assembled by PROPONER.
  * ``pipeline.autopilot.auditor``      — the 5-level ``audit_pack`` (AUDITAR).
  * ``pipeline.autopilot.gates``        — the GASTO/PROD/LEGAL ``evaluate_gates`` ([PUERTA], parks).
  * ``services.api.codes.cdp_pair``     — the REAL coder that mints the synthetic dealer's CDP-<CC>-.

THE HONEST FRONTIER, ENCODED (the answer to the owner's vision). The orchestrator AUTO-DRIVES
build + dry-run ONLY. Three structural limits are wired in code, not paperwork:

  1. AUDIT fail-closed.  A ``RECHAZA`` verdict STOPS the campaign at BOOTSTRAPPED (Law I — a
     provably broken pack never seeds). It is SAFE to delegate the rejection.
  2. AUDIT escalation.   An ``ESCALA`` verdict PARKS the campaign PENDIENTE-OWNER at BOOTSTRAPPED
     (the auditor cannot safely decide; the owner must). The loop records it and stops THIS
     campaign — it does not fabricate a "go".
  3. LIVE gates park.    The real-harvest action (a live :5433 write / scrape of a real country)
     is evaluated against ``gates.evaluate_gates`` and comes back GATED (PROD + LEGAL) —
     PENDIENTE-OWNER. The SYNTHETIC dry-run seed crosses NO gate (it harvests no real data and
     writes only the :5434 dry-run inside an aborted transaction). "Arrancar el país real" is
     structurally the owner's, by construction.

ES byte-identity / isolation (inviolable):
  * Every write lands ONLY on the caller-owned transaction (the test rolls it back -> zero
    residue). The synthetic pack is staged under a CALLER-SUPPLIED temp ``pack_root`` — the real
    repo ``countries/`` tree is never touched.
  * The dealer is minted by the REAL ``cdp_pair(country_code='XX')`` and lands as ``CDP-XX-…``,
    its own canonical (no ES bleed). ``v_country_proof_violations`` is read as the SUPERVISA gate
    and MUST be 0 — the SQL belt that proves XX never cross-merges with ES.

NO migration: the campaign rides ``country_campaign`` / ``country_campaign_transition`` (mig 0067,
already on :5434). The audit verdict is NOT persisted (a later increment owns
``country_pack_audit_verdict``); it is returned in the pure :class:`CampaignResult`.
"""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import asyncpg

from pipeline.autopilot import state
from pipeline.autopilot.supervisor import health_rollup
from pipeline.autopilot.auditor import (
    CountryPlan,
    Decision,
    PackAuditVerdict,
    PlanClaim,
    audit_pack,
)
from pipeline.autopilot.extract_denom import DENOM_CSV_NAME, DenominatorResult, extract_denominator
from pipeline.autopilot.extract_geo import (
    CrossWalk,
    GeoLevelMapping,
    GeoPack,
    build_geo_pack,
    parse_geonames,
    parse_hierarchy,
    write_backbone_csv,
    write_centroides_csv,
)
from pipeline.autopilot.gates import (
    CampaignAction,
    GateResult,
    evaluate_gates,
    parked,
)
from services.api.codes import cdp_pair

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
#: The SUPERVISA belt — the served-layer guard view (migration 0057). MUST be 0.
PROOF_VIEW: str = "v_country_proof_violations"

#: Provenance stamp on the synthetic dealer (so it is trivially identifiable / reversible).
SYNTHETIC_SOURCE: str = "autopilot_dry_run"

#: Crockford base32 alphabet (no I/L/O/U) — entity_ulid_shape ``^[0-9A-HJKMNP-TV-Z]{26}$``
#: (migrations/0006_entity_evolve.sql). Mirrors scripts/seed_pilot.py / pilot_country.py so the
#: orchestrator has no cross-script import coupling into the ``scripts`` layer.
_CROCKFORD: str = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: A dense 3-list projected overlap → MSE-identified, coverage_lower ≈ 0.999 (>= seal 0.95).
#: The PROPONER's projected capture matrix for the synthetic demonstration (calibrated against the
#: live estimator, mirrors tests/test_auditor.py OVERLAP_DENSE). Real countries derive this from
#: their roster's measured overlap; for synthetic XX it is the well-formed stand-in.
_DEMO_DENSE_OVERLAP: Mapping[tuple[int, ...], int] = {
    (1, 0, 0): 2, (0, 1, 0): 2, (0, 0, 1): 2,
    (1, 1, 0): 20, (1, 0, 1): 20, (0, 1, 1): 20, (1, 1, 1): 400,
}


def _mint_ulid() -> str:
    """A 26-char Crockford-base32 ULID matching ``entity_ulid_shape``.

    48-bit ms time + 80-bit randomness, time-ordered. Identical shape to
    scripts/seed_pilot.py::ulid (kept local to avoid a pipeline->scripts layering inversion).
    """
    num = (int(time.time() * 1000) << 80) | int.from_bytes(secrets.token_bytes(10), "big")
    out: list[str] = []
    for _ in range(26):
        out.append(_CROCKFORD[num & 0x1F])
        num >>= 5
    return "".join(reversed(out))


# ---------------------------------------------------------------------------
# Inputs — the synthetic country's RESEARCH sources + PROPONER knobs
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PackFixtures:
    """Everything the orchestrator needs to RESEARCH + PROPOSE a synthetic country pack.

    These are the country's raw, €0 public-source inputs (GeoNames dump, Eurostat SBS TSV, GLEIF
    CSV) plus the manifest/plan knobs. For a REAL country these arrive from the live extractors'
    network seam; for the synthetic demonstration the caller supplies fixture text. ``pack_root``
    is a CALLER-OWNED staging directory (a temp dir in tests) — the orchestrator writes
    ``pack_root/<CC>/`` there and NEVER into the repo's real ``countries/`` tree.
    """

    pack_root: Path
    # --- RESEARCH: geo (extract_geo) ---
    geonames_text: str
    hierarchy_text: str
    crosswalk: CrossWalk | None = None
    geo_mapping: GeoLevelMapping = field(default_factory=GeoLevelMapping)
    # --- RESEARCH: denominator (extract_denom) ---
    sbs_tsv: str = ""
    gleif_csv: str | None = None
    # --- PROPONER: country.toml manifest ---
    subdivision_regex: str = r"^[A-Z]{2}$"
    national_kinds: tuple[str, ...] = ("plataforma", "importador")
    taxonomy_yaml: str = "dealer_kinds: [generic]\npoint_of_sale: [generic]\n"
    recipe_yaml: str = "base_url: https://example.xx\n"
    # --- PROPONER: the PLAN (roster + numbers + projected overlap) ---
    roster: tuple[str, ...] = ("osm", "dgt_cat", "aedra")
    # The two ORTHOGONAL collector families that corroborate the geo subdivision count (N3 quorum).
    # ``verify._path_family`` maps these by keyword: "db_geo_backbone" -> 'db' (the count
    # materialized in the ingested backbone), "registral_geo_crosswalk" -> 'registral' (the
    # official Eurostat-LAU crosswalk). Both cover all subdivisions in the synthetic fixture, so
    # they genuinely agree on the province count — a real 2-family quorum, not a fabricated one.
    geo_count_paths: tuple[str, ...] = ("db_geo_backbone", "registral_geo_crosswalk")
    # The denominator authority is ALWAYS an owner decision (N2: "autoridad-de-denominador SIEMPRE
    # ESCALA") — a wrong denominator silently biases the whole census. So by default the plan does
    # NOT auto-certify it through N3 (that would fabricate an independent path the denom extractor
    # itself flags as needs_audit). Set ``certify_denominator=True`` only to exercise N3-on-denom.
    certify_denominator: bool = False
    denominator_paths: tuple[str, ...] = ("registral_eurostat_sbs", "db_geo_rollup")
    projected_overlap: Mapping[tuple[int, ...], int] = field(
        default_factory=lambda: dict(_DEMO_DENSE_OVERLAP)
    )
    external_anchor: float | None = None
    # --- EJECUTAR: the synthetic dealer ---
    dealer_domain: str = "example-dealer.xx"
    dealer_kind: str = "compraventa"


# ---------------------------------------------------------------------------
# Output — the pure result of one campaign run
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CampaignResult:
    """The pure, immutable record of one ``run_campaign`` pass — the demonstration's evidence.

    ``decision`` is the auditor's BUILD recommendation; ``live_gate`` (N2) is ALWAYS ESCALA (the
    owner-structural go-live). ``parked_gates`` are the live-harvest gates parked PENDIENTE-OWNER.
    ``sealed_as_checkpoint`` is the honest seal: a synthetic dry-run cannot certify real coverage,
    so SEALED is reached as a declared CHECKPOINT, never a coverage lie.
    """

    country_code: str
    states_visited: tuple[str, ...]
    final_state: str
    halted: bool
    halt_reason: str | None
    decision: Decision
    live_gate: Decision
    audit: PackAuditVerdict
    parked_gates: tuple[GateResult, ...]
    minted_cdp_code: str | None
    minted_canonical_key: str | None
    seeded_provinces: int
    seeded_municipalities: int
    proof_violations: int
    sealed_as_checkpoint: bool
    seal_note: str | None
    checkpoints: tuple[str, ...]
    pack_dir: str

    @property
    def pending_owner(self) -> bool:
        """True iff the campaign reached a live owner-frontier and is waiting on the owner: a build
        escalation, the always-on live gate, or any parked live-harvest gate. A fail-closed RECHAZA
        halt is NOT owner-pending — it is a dead campaign (Law I), so it returns False."""
        if self.halted:
            return False
        return (
            self.decision is Decision.ESCALA
            or self.live_gate is Decision.ESCALA
            or bool(self.parked_gates)
        )

    @property
    def parked_gate_names(self) -> tuple[str, ...]:
        return tuple(g.gate for g in self.parked_gates)

    @property
    def reached_seal(self) -> bool:
        return self.final_state == state.SEALED


# ---------------------------------------------------------------------------
# Step helpers (each does ONE phase; pure where possible)
# ---------------------------------------------------------------------------

def _research_geo(country_code: str, fx: PackFixtures) -> GeoPack:
    """RESEARCH (geo): parse the GeoNames dump + hierarchy, build the country geo pack."""
    rows = parse_geonames(fx.geonames_text)
    hierarchy = parse_hierarchy(fx.hierarchy_text)
    return build_geo_pack(
        rows, country_code=country_code, hierarchy=hierarchy,
        mapping=fx.geo_mapping, crosswalk=fx.crosswalk,
    )


def _research_denominator(country_code: str, fx: PackFixtures) -> DenominatorResult:
    """RESEARCH (denominator): build the all-segment census anchors from Eurostat SBS + GLEIF."""
    return extract_denominator(country_code, sbs_tsv=fx.sbs_tsv, gleif_csv=fx.gleif_csv)


def _write_pack(country_code: str, fx: PackFixtures, geo: GeoPack, denom: DenominatorResult) -> Path:
    """PROPONER (artifacts): assemble the physical ``countries/<CC>/`` pack under ``pack_root``.

    Writes the 8 contract pieces the N0 linter checks: country.toml, geo/backbone.csv (+
    centroides.csv), recipes/*.yaml, census/<denom>.csv, census/SOURCE.md, taxonomy.yaml.
    """
    pack = Path(fx.pack_root) / country_code
    geo_dir = pack / "geo"
    write_backbone_csv(geo, geo_dir / "backbone.csv")
    write_centroides_csv(geo, geo_dir / "centroides.csv")

    census_dir = pack / "census"
    denom.write_census_csv(census_dir / DENOM_CSV_NAME)
    denom.write_source_md(census_dir / "SOURCE.md")

    recipes_dir = pack / "recipes" / "_tier1"
    recipes_dir.mkdir(parents=True, exist_ok=True)
    (recipes_dir / "sample.yaml").write_text(fx.recipe_yaml, encoding="utf-8")

    (pack / "taxonomy.yaml").write_text(fx.taxonomy_yaml, encoding="utf-8")

    national = "".join(f'"{k}", ' for k in fx.national_kinds).rstrip(", ")
    (pack / "country.toml").write_text(
        f'country_code = "{country_code}"\n\n'
        "[subdivision]\n"
        f'regex = "{fx.subdivision_regex}"\n\n'
        "[kinds]\n"
        f"national = [{national}]\n",
        encoding="utf-8",
    )
    return pack


def _propose_plan(country_code: str, fx: PackFixtures, geo: GeoPack, denom: DenominatorResult) -> CountryPlan:
    """PROPONER (PLAN): derive the audit PLAN from the EXTRACTED numbers + the roster/overlap knobs.

    The geo claim asserts the SUBDIVISION (province) count the extractor produced, re-prosecuted by
    N3 across two genuinely orthogonal collector families (``verify._path_family``): the ingested
    backbone ('db') and the official Eurostat-LAU crosswalk ('registral'), which agree on the count
    in the fixture. The denominator authority is owner-gated at N2 (SIEMPRE ESCALA); it is only fed
    to N3 when ``certify_denominator`` is explicitly set (it never fabricates an independent path).
    """
    geo_n = str(len(geo.provinces))
    geo_claim = PlanClaim(
        subject_key=f"geo:{country_code}:provinces",
        subject_type="count",
        asserted_value=geo_n,
        paths={p: geo_n for p in fx.geo_count_paths},
    )
    denominator_anchor: PlanClaim | None = None
    if fx.certify_denominator:
        denom_n = str(denom.national_total)
        denominator_anchor = PlanClaim(
            subject_key=f"denominator:{country_code}",
            subject_type="denominator",
            asserted_value=denom_n,
            paths={p: denom_n for p in fx.denominator_paths},
        )
    return CountryPlan(
        country_code=country_code,
        orthogonal_lists=fx.roster,
        geo_counts=(geo_claim,),
        denominator_anchor=denominator_anchor,
        projected_overlap=dict(fx.projected_overlap),
        external_anchor=fx.external_anchor,
    )


def _harvest_gate_action(country_code: str) -> CampaignAction:
    """The LIVE-harvest action the [PUERTA] evaluates — the thing that WOULD go live.

    A real harvest writes the live :5433 census (``targets_prod=True``) and scrapes a real country
    (``legal_cleared=False`` until the owner signs the KNOW_COUNTRY legal/ToS dossier). Spend is €0
    (architecture: 0 rutas €>0 hoy). So PROD + LEGAL park PENDIENTE-OWNER; GASTO stays OPEN.
    """
    return CampaignAction(
        country_code=country_code,
        spend_eur=0.0,
        targets_prod=True,
        dsn=None,
        legal_cleared=False,
    )


async def _seed_geo_pack(conn: asyncpg.Connection, geo: GeoPack) -> tuple[int, int]:
    """EJECUTAR (geo): country-scoped INSERT of the pack's provinces then municipalities.

    asyncpg sibling of ``extract_geo.load_geo_pack`` (same SQL, same ON CONFLICT idempotence) so
    the whole synthetic seed lives on the caller's single transaction. Provinces first (the
    municipality composite FK targets them)."""
    if geo.provinces:
        await conn.executemany(
            "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
            "VALUES ($1, $2, $3, $4, $5) "
            "ON CONFLICT (country_code, code) DO NOTHING",
            [(p.code, p.name, p.region_code, p.region_name, p.country_code) for p in geo.provinces],
        )
    if geo.municipalities:
        await conn.executemany(
            "INSERT INTO geo_municipality "
            "(code, name, province_code, comarca_id, lat, lon, country_code) "
            "VALUES ($1, $2, $3, NULL, $4, $5, $6) "
            "ON CONFLICT (country_code, code) DO NOTHING",
            [(m.code, m.name, m.province_code, m.lat, m.lon, m.country_code) for m in geo.municipalities],
        )
    return len(geo.provinces), len(geo.municipalities)


async def _seed_dealer(
    conn: asyncpg.Connection, country_code: str, fx: PackFixtures, geo: GeoPack
) -> tuple[str, str, str, str]:
    """EJECUTAR (dealer): mint ONE synthetic dealer via the REAL ``cdp_pair`` and INSERT it.

    The dealer is placed in the first (sorted) municipality so its composite geo FK is guaranteed
    to resolve to a just-seeded XX province (never ES). Returns (canonical_key, cdp_code,
    province_code, municipality_code). The minted code is ``CDP-<CC>-<prov>-…`` — its own canonical.
    """
    muni = sorted(geo.municipalities, key=lambda m: m.code)[0]
    key, code = cdp_pair(
        province_code=muni.province_code, domain=fx.dealer_domain, country_code=country_code
    )
    await conn.execute(
        """
        INSERT INTO entity (entity_ulid, cdp_code, kind, country_code,
                            province_code, municipality_code, canonical_key,
                            status, kind_source, trade_name, first_discovered_source)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'active', 'manual', $8, $9)
        """,
        _mint_ulid(), code, fx.dealer_kind, country_code,
        muni.province_code, muni.code, key,
        f"{country_code} Synthetic Dealer", SYNTHETIC_SOURCE,
    )
    return key, code, muni.province_code, muni.code


# ---------------------------------------------------------------------------
# The LOOP
# ---------------------------------------------------------------------------

async def run_campaign(
    country_code: str,
    *,
    conn: asyncpg.Connection,
    pack_fixtures: PackFixtures,
    dry_run: bool = True,
) -> CampaignResult:
    """Drive ONE country through the full COVER(CC) loop on the caller-owned transaction.

    The caller MUST own the transaction boundary (open it, optionally seed an incumbent baseline,
    call this, assert, then ROLL BACK) — exactly like ``tests/test_autopilot_state.py``. This
    function NEVER commits, so the dry-run leaves zero residue. It HARD-REFUSES a live-prod DSN by
    contract: the caller must point ``conn`` at the :5434 dry-run (the integration suite pins it).

    Phases (each maps to one COVER(CC) hop):
      REGISTERED                       — ``state.register`` (idempotent birth).
      -> KNOW_COUNTRY   (RESEARCH)     — extract geo + denominator, stage ``countries/<CC>/``.
      -> BOOTSTRAPPED   (PROPONER)     — assemble country.toml + the PLAN.
         AUDITAR                       — ``audit_pack``: RECHAZA halts (fail-closed); ESCALA parks
                                         PENDIENTE-OWNER; APRUEBA proceeds. N2/live_gate ALWAYS ESCALA.
         [PUERTA]                      — ``evaluate_gates`` on the live-harvest action -> PROD+LEGAL
                                         park PENDIENTE-OWNER. The synthetic dry-run seed crosses no gate.
      -> IN_COVERAGE    (EJECUTAR)     — seed synthetic geo + 1 ``CDP-<CC>-`` dealer (dry-run only).
         SUPERVISAR                    — ``v_country_proof_violations`` MUST be 0 (else fail-closed halt).
      -> SEALED         (SELLAR)       — reached as a declared CHECKPOINT (synthetic dry-run cannot
                                         certify real coverage; the real seal awaits the gated harvest).

    With ``dry_run=False`` the loop AUDITS + proposes but REFUSES to auto-seed a live country: it
    parks at BOOTSTRAPPED PENDIENTE-OWNER (the honest frontier — "arrancar país real" is the owner's).
    """
    cc = country_code.strip().upper()
    states_visited: list[str] = []
    checkpoints: list[str] = []

    async def _advance(to_state: str, note: str, detail: dict[str, Any] | None = None) -> None:
        await state.transition(conn, cc, to_state, actor="autopilot", note=note, detail=detail)
        states_visited.append(to_state)

    # --- REGISTERED: idempotent birth -------------------------------------------------
    born = await state.register(conn, cc, actor="autopilot", detail={"dry_run": dry_run})
    states_visited.append(born)

    # --- RESEARCH -> KNOW_COUNTRY -----------------------------------------------------
    geo = _research_geo(cc, pack_fixtures)
    denom = _research_denominator(cc, pack_fixtures)
    await _advance(
        state.KNOW_COUNTRY, "RESEARCH: geo + denominator extracted",
        detail={
            "phase": "RESEARCH",
            "geo_provinces": len(geo.provinces),
            "geo_municipalities": len(geo.municipalities),
            "denominator_national": denom.national_total,
        },
    )
    # The denominator's per-segment split is a declared needs_audit checkpoint (the extractor never
    # fabricates it) — surface it on the campaign so the honesty travels with the result.
    for cp in denom.checkpoints:
        checkpoints.append(f"denominator.{cp.name}={cp.status}")

    # --- PROPONER -> BOOTSTRAPPED -----------------------------------------------------
    pack_dir = _write_pack(cc, pack_fixtures, geo, denom)
    plan = _propose_plan(cc, pack_fixtures, geo, denom)
    await _advance(
        state.BOOTSTRAPPED, "PROPONER: pack + PLAN assembled",
        detail={"phase": "PROPOSE", "pack_dir": str(pack_dir), "roster": list(plan.orthogonal_lists)},
    )
    checkpoints.append(
        "denominator.authority=OWNER-GATED (N2 SIEMPRE ESCALA; not auto-certified by the loop)"
    )

    # --- AUDITAR (5 niveles) ----------------------------------------------------------
    verdict = audit_pack(cc, pack_dir, plan)
    live_gate = verdict.live_gate  # N2 — ALWAYS ESCALA (the owner-structural go-live)

    def _result(
        *, halted: bool, halt_reason: str | None,
        parked_gates: tuple[GateResult, ...] = (),
        minted_cdp_code: str | None = None, minted_canonical_key: str | None = None,
        seeded_provinces: int = 0, seeded_municipalities: int = 0,
        proof_violations: int = 0,
        sealed_as_checkpoint: bool = False, seal_note: str | None = None,
    ) -> CampaignResult:
        return CampaignResult(
            country_code=cc,
            states_visited=tuple(states_visited),
            final_state=states_visited[-1],
            halted=halted,
            halt_reason=halt_reason,
            decision=verdict.decision,
            live_gate=live_gate,
            audit=verdict,
            parked_gates=parked_gates,
            minted_cdp_code=minted_cdp_code,
            minted_canonical_key=minted_canonical_key,
            seeded_provinces=seeded_provinces,
            seeded_municipalities=seeded_municipalities,
            proof_violations=proof_violations,
            sealed_as_checkpoint=sealed_as_checkpoint,
            seal_note=seal_note,
            checkpoints=tuple(checkpoints),
            pack_dir=str(pack_dir),
        )

    if verdict.decision is Decision.RECHAZA:
        # Law I: a provably broken/refuted pack NEVER seeds. Stop the campaign at BOOTSTRAPPED.
        checkpoints.append(f"audit=RECHAZA:{verdict.reason_code}")
        return _result(halted=True, halt_reason=f"audit RECHAZA: {verdict.reason_code}")

    if verdict.decision is Decision.ESCALA:
        # The auditor cannot safely decide — park PENDIENTE-OWNER at BOOTSTRAPPED (never a fabricated go).
        checkpoints.append(f"audit=ESCALA:{verdict.reason_code}")
        return _result(halted=False, halt_reason=f"audit ESCALA (PENDIENTE-OWNER): {verdict.reason_code}")

    # APRUEBA (build + dry-run). Record the always-on live gate.
    checkpoints.append(f"live_gate=ESCALA (N2 owner go-live): {verdict.level('N2').reason_code}")

    # --- [PUERTA]: the live-harvest gates park PENDIENTE-OWNER -------------------------
    gate_results = evaluate_gates(_harvest_gate_action(cc))
    parked_gates = parked(gate_results)
    for g in parked_gates:
        checkpoints.append(f"gate.{g.gate}=PENDIENTE-OWNER")
    # 1.2: persist the parked gates as CONSULTABLE resume state (not just in-memory + the audit
    # trail), so a supervisor/owner can ask the DB which countries are blocked on which gate.
    await state.mark_pending_gates(conn, cc, [(g.gate, g.reason) for g in parked_gates])

    # The honest frontier in code: a NON-dry-run would target the live harvest, which is gated.
    # The orchestrator REFUSES to auto-go-live — it parks at BOOTSTRAPPED.
    if not dry_run:
        return _result(
            halted=False,
            halt_reason="live harvest is owner-gated (PROD/LEGAL) — PENDIENTE-OWNER; "
                        "autopilot never auto-starts a real country",
            parked_gates=parked_gates,
        )

    # --- EJECUTAR (dry-run synthetic) -> IN_COVERAGE ----------------------------------
    n_prov, n_muni = await _seed_geo_pack(conn, geo)
    key, code, prov_code, muni_code = await _seed_dealer(conn, cc, pack_fixtures, geo)
    await _advance(
        state.IN_COVERAGE, "EJECUTAR: synthetic geo + dealer seeded (dry-run)",
        detail={
            "phase": "EXECUTE",
            "audit_decision": verdict.decision.value,
            "live_gate": live_gate.value,
            "parked_gates": [g.gate for g in parked_gates],
            "minted_cdp_code": code,
            "seeded_provinces": n_prov,
            "seeded_municipalities": n_muni,
        },
    )

    # --- SUPERVISAR: full per-tenant health roll-up (1.1) — not just the proof count --
    # The loop now reads the COMPLETE isolated health (violations + servable + seal + sources), so the
    # campaign result carries observability, not only the fail-closed proof flag. contaminated is the
    # SAME fail-closed signal (violations > 0) the proof-only check used, so behaviour is preserved.
    health = await health_rollup(conn, cc)
    proof_violations = health.violations
    checkpoints.append(
        f"SUPERVISA: servable={health.servable_dealers} "
        f"sources={health.sources.healthy}/{health.sources.total}(silent={health.sources.silent}) "
        f"seal_segments={health.seal.sealed_segments}"
    )
    if health.contaminated:
        # A country-blind cross-merge contaminated the served layer — fail-closed (do NOT seal a lie).
        checkpoints.append(f"SUPERVISA={PROOF_VIEW}={proof_violations} (CONTAMINATION)")
        return _result(
            halted=True,
            halt_reason=f"{PROOF_VIEW}={proof_violations}: cross-country contamination — fail-closed",
            parked_gates=parked_gates,
            minted_cdp_code=code, minted_canonical_key=key,
            seeded_provinces=n_prov, seeded_municipalities=n_muni,
            proof_violations=proof_violations,
        )

    # --- SELLAR -> SEALED (honest CHECKPOINT) -----------------------------------------
    # A synthetic dry-run cannot certify REAL coverage: the real harvest + MSE seal await the
    # owner-gated live run. So SEALED is reached as a DECLARED checkpoint, not a coverage claim.
    seal_note = (
        "CHECKPOINT seal: synthetic dry-run reached the full lifecycle; REAL coverage is pending "
        "the owner-gated live harvest (no coverage figure is asserted)."
    )
    checkpoints.append("seal=CHECKPOINT (synthetic; no real coverage asserted)")
    await _advance(
        state.SEALED, "SELLAR: checkpoint seal (synthetic dry-run)",
        detail={"phase": "SEAL", "seal_kind": "CHECKPOINT", "note": seal_note},
    )

    return _result(
        halted=False, halt_reason=None,
        parked_gates=parked_gates,
        minted_cdp_code=code, minted_canonical_key=key,
        seeded_provinces=n_prov, seeded_municipalities=n_muni,
        proof_violations=proof_violations,
        sealed_as_checkpoint=True, seal_note=seal_note,
    )


__all__ = [
    "PROOF_VIEW",
    "SYNTHETIC_SOURCE",
    "PackFixtures",
    "CampaignResult",
    "run_campaign",
]
