"""TDD spec for the auto-pack AUTO-SOURCE-FINDER (Phase C, the missing piece).

``pipeline.autopilot.source_finder`` is the country source auto-discovery of the
country-autopilot. Given a country it fires per-bucket search queries (through an
INJECTED ``search_fn`` — never the network), extracts the candidate domains,
classifies each into one of the 7 ORTHOGONAL capture buckets
(GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG) and emits a PROPOSED adapter config per
candidate.

The load-bearing doctrine these tests pin (the CHECKPOINT of JUDGEMENT):
  * "is this source authoritative / orthogonal?" is a JUDGEMENT, not a mechanical
    fact. So every candidate carries a heuristic ``confidence`` AND
    ``needs_audit=True``. The finder PROPOSES; the auto-auditor (N1 orthogonality
    / N2 credibility) GATES. The finder NEVER auto-approves a source as
    authoritative (confidence is capped strictly below 1.0; needs_audit is always
    set).
  * coverage of ">= 3 orthogonal buckets" is REPORTED, and insufficiency is
    flagged — it is never silently assumed met.

Everything here is deterministic: an inline mocked ``search_fn``, zero network.
The live SearXNG/DDG search is a separate seam, never exercised by these tests.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from pipeline.autopilot import source_finder as SF
from pipeline.exhaustiveness import lists as L

pytestmark = pytest.mark.unit


# --- inline fixture: a mocked country 'XX' web-search corpus (no network) ----------
#
# Keyed by the EXACT query the finder emits per bucket template. Each hit is
# (url, title, snippet). The corpus is crafted so each of the 7 orthogonal buckets
# is reachable, plus two adversarial cases:
#   * a marketplace returned UNDER the DGT query (content must override the query
#     origin -> CENSUS, proving the classification is judgement, not query echo),
#   * a search-engine noise domain that must be filtered out entirely.

CC = "XX"

_HITS = {
    # DGT (official administrative registry) + the cross-origin marketplace + noise
    "DGT": [
        ("https://transportes.gob.xx/centros",
         "Registro oficial de centros autorizados - Ministerio de Transportes",
         "Listado oficial de talleres y concesionarios autorizados del gobierno"),
        # adversarial: a marketplace surfaced by the DGT query -> must classify CENSUS
        ("https://autoplaza.xx/ocasion",
         "AutoPlaza - compraventa de coches de ocasion",
         "marketplace de vehiculos de segunda mano y ocasion"),
        # adversarial: pure search-engine noise -> must be dropped
        ("https://www.google.xx/search?q=concesionarios",
         "concesionarios - Google", "resultados de busqueda"),
    ],
    # ASSOC (trade-association membership rolls)
    "ASSOC": [
        ("https://anc.xx",
         "Asociacion Nacional de Concesionarios de Automocion",
         "federacion de miembros y asociados del sector de automocion"),
    ],
    # OEM (manufacturer official VO networks) — domain slug also trips bucket_for
    "OEM": [
        ("https://mercedes.xx/concesionarios",
         "Concesionarios oficiales Mercedes-Benz XX",
         "Red de concesionarios oficiales - encuentra tu dealer locator"),
    ],
    # CENSUS (marketplace-as-census)
    "CENSUS": [
        ("https://cochesxx.xx",
         "CochesXX - anuncios clasificados de coches usados",
         "marketplace lider de compraventa y vehiculos de ocasion"),
    ],
    # REG (mercantile registry)
    "REG": [
        ("https://rmc.xx",
         "Registro Mercantil Central - sociedades",
         "company register / CNAE 4511 comercio de automoviles"),
    ],
    # GEO (physical-presence catalogue)
    "GEO": [
        ("https://mapa.xx/talleres",
         "Directorio en mapa - OpenStreetMap de talleres",
         "places / points of interest del sector del automovil"),
    ],
    # DORK (own-domain dealer site — the residual bucket; no authoritative signal)
    "DORK": [
        ("https://autoslopez.xx",
         "Autos Lopez - concesionario y taller en Villa XX",
         "venta de automoviles y servicio post-venta"),
    ],
}


def _corpus(cc: str) -> dict[str, list[tuple[str, str, str]]]:
    """Build {exact_query: hits} from the finder's own templates, per bucket."""
    out: dict[str, list[tuple[str, str, str]]] = {}
    for bucket, templates in SF.BUCKET_QUERIES.items():
        hits = _HITS.get(bucket, [])
        # Attach the bucket's hits to its FIRST template; the rest return nothing.
        for i, tmpl in enumerate(templates):
            out[tmpl.format(country=cc)] = hits if i == 0 else []
    return out


def make_search_fn(corpus):
    """A strict mock: returns the corpus hits, and RAISES on any query it was not
    asked to serve — proving the finder only ever consults the injected seam and
    builds its queries deterministically (no hidden network path)."""
    calls: list[str] = []

    def search_fn(query: str):
        calls.append(query)
        if query not in corpus:
            raise AssertionError(f"unexpected (non-injected) query: {query!r}")
        return [{"url": u, "title": t, "snippet": s} for (u, t, s) in corpus[query]]

    search_fn.calls = calls  # type: ignore[attr-defined]
    return search_fn


@pytest.fixture()
def candidates():
    return SF.find_sources(CC, search_fn=make_search_fn(_corpus(CC)))


def _by_domain(cands):
    return {c.domain: c for c in cands}


# --- classification correctness ----------------------------------------------------

def test_each_candidate_lands_in_the_expected_orthogonal_bucket(candidates):
    got = {c.domain: c.bucket for c in candidates}
    expected = {
        "transportes.gob.xx": "DGT",
        "anc.xx": "ASSOC",
        "mercedes.xx": "OEM",
        "cochesxx.xx": "CENSUS",
        "rmc.xx": "REG",
        "mapa.xx": "GEO",
        "autoslopez.xx": "DORK",
        "autoplaza.xx": "CENSUS",  # the cross-origin marketplace
    }
    for domain, bucket in expected.items():
        assert got.get(domain) == bucket, f"{domain}: got {got.get(domain)}, want {bucket}"
    # every emitted bucket is one of the 7 orthogonal capture classes
    assert all(c.bucket in L.ORTHOGONAL_LISTS for c in candidates)


def test_content_overrides_query_origin_the_judgement_not_the_echo(candidates):
    # autoplaza was returned by the DGT query but its CONTENT is a marketplace:
    # the classifier must follow the evidence (CENSUS), not the query intent (DGT).
    ap = _by_domain(candidates)["autoplaza.xx"]
    assert ap.bucket == "CENSUS"
    assert ap.origin_bucket == "DGT"


def test_search_engine_noise_is_filtered_out(candidates):
    assert all("google" not in c.domain for c in candidates)
    # exactly the eight signal domains survive (the noise hit dropped).
    assert len(candidates) == 8


# --- the CHECKPOINT: judgement is proposed, never auto-approved ---------------------

def test_every_candidate_needs_audit_with_a_bounded_confidence(candidates):
    assert candidates, "finder produced no candidates"
    assert SF.CONFIDENCE_CAP < 1.0  # the finder structurally cannot certify a source
    for c in candidates:
        assert c.needs_audit is True, f"{c.domain} was not flagged needs_audit"
        assert 0.0 < c.confidence <= SF.CONFIDENCE_CAP, f"{c.domain} conf={c.confidence}"
        # never auto-approved as authoritative truth
        assert c.confidence != 1.0


def test_authoritative_looking_dgt_source_still_needs_audit(candidates):
    # An official .gob registry is the MOST authoritative-looking hit; the finder
    # must STILL refuse to bless it — credibility is N2's call, always escalated.
    dgt = _by_domain(candidates)["transportes.gob.xx"]
    assert dgt.bucket == "DGT"
    assert dgt.needs_audit is True


# --- proposed adapter config per candidate -----------------------------------------

def test_each_candidate_carries_a_proposed_adapter_config(candidates):
    for c in candidates:
        cfg = c.proposed_config
        assert cfg is not None
        assert cfg.bucket == c.bucket
        assert cfg.base_url == f"https://{c.domain}"
        assert cfg.source_key and cfg.adapter
        # honest: kind prior is set only where the bucket implies one segment,
        # blank (never fabricated) for the mixed-segment registry/assoc buckets.
        assert isinstance(cfg.kind, str)


def test_oem_proposed_source_key_round_trips_through_bucket_for(candidates):
    # The project's own taxonomy fn must agree the proposed OEM key is OEM — the
    # one bucket where the source_key is constructed to round-trip.
    oem = _by_domain(candidates)["mercedes.xx"]
    assert oem.bucket == "OEM"
    assert L.bucket_for(oem.proposed_config.source_key) == "OEM"


# --- orthogonality coverage report (>=3 or insufficiency) --------------------------

def test_reports_three_or_more_orthogonal_buckets_when_covered(candidates):
    report = SF.assess_orthogonality(candidates)
    assert report.n_orthogonal >= SF.MIN_ORTHOGONAL_BUCKETS
    assert report.meets_threshold is True
    assert report.insufficient is False
    # the four discoverable authorities the mandate names are all present
    assert {"DGT", "ASSOC", "CENSUS", "OEM"}.issubset(set(report.buckets_covered))


def test_insufficiency_is_flagged_not_silently_assumed():
    # A corpus that only yields CENSUS + DORK (2 buckets) must be flagged short of
    # the >=3 orthogonality floor, naming the missing buckets.
    thin = {}
    for bucket, templates in SF.BUCKET_QUERIES.items():
        hits = _HITS.get(bucket, []) if bucket in ("CENSUS", "DORK") else []
        for i, tmpl in enumerate(templates):
            thin[tmpl.format(country=CC)] = hits if i == 0 else []
    cands = SF.find_sources(CC, search_fn=make_search_fn(thin))
    report = SF.assess_orthogonality(cands)
    assert report.n_orthogonal < SF.MIN_ORTHOGONAL_BUCKETS
    assert report.meets_threshold is False
    assert report.insufficient is True
    assert "DGT" in report.missing and "ASSOC" in report.missing
    assert "INSUFFICIENT" in report.reason.upper()


# --- network isolation -------------------------------------------------------------

def test_finder_only_consults_the_injected_search_fn():
    fn = make_search_fn(_corpus(CC))
    SF.find_sources(CC, search_fn=fn)
    # every query the finder issued was one of its own templated queries (the mock
    # raises otherwise); and it issued at least one query per bucket.
    assert fn.calls
    assert len(set(fn.calls)) >= len(SF.BUCKET_QUERIES)


# --- determinism / golden ----------------------------------------------------------

_GOLDEN = pathlib.Path(__file__).parent / "golden" / "source_finder_xx.json"


def _dump(cands):
    return [
        {
            "domain": c.domain,
            "bucket": c.bucket,
            "confidence": c.confidence,
            "needs_audit": c.needs_audit,
            "origin_bucket": c.origin_bucket,
            "query": c.query,
            "evidence": c.evidence,
            "proposed_config": {
                "source_key": c.proposed_config.source_key,
                "bucket": c.proposed_config.bucket,
                "kind": c.proposed_config.kind,
                "adapter": c.proposed_config.adapter,
                "base_url": c.proposed_config.base_url,
                "notes": c.proposed_config.notes,
            },
        }
        for c in cands
    ]


def test_output_is_byte_deterministic_across_runs():
    a = SF.find_sources(CC, search_fn=make_search_fn(_corpus(CC)))
    b = SF.find_sources(CC, search_fn=make_search_fn(_corpus(CC)))
    assert _dump(a) == _dump(b)


def test_matches_committed_golden(candidates):
    assert _GOLDEN.exists(), f"golden missing: {_GOLDEN}"
    expected = json.loads(_GOLDEN.read_text(encoding="utf-8"))
    assert _dump(candidates) == expected
