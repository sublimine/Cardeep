"""Executable-recipe schema — the §4 recipe-first contract.

A :class:`Recipe` is the durable, reproducible asset that lets Cardeep re-scrape a
dealer's inventory WITHOUT keeping the raw crude on disk. It captures every
dimension the harness needs to *replay* an extraction:

  * transport      — how bytes are fetched (engine, impersonation, base URL)
  * fingerprint    — the TLS/UA identity the transport presents
  * pagination     — how the dealer's full result set is enumerated
  * parsing        — the extraction engine + field-map that turns bytes into cars
  * evidence       — the VAM proof that the recipe actually worked (verdict + counts)

This module is the schema ONLY (data + round-trippable (de)serialization). The
runner that *executes* a recipe and the harness that *mints + verifies* one live
in :mod:`pipeline.recipe_harness`. Persistence reuses :func:`pipeline.recipe.write_recipe`
(YAML under ``countries/ES/recipes/``), so a recipe is a normal committed asset.

Status is a closed vocabulary so a reader never has to guess: a recipe is DRAFT
until verified, then VERIFIED (VAM did not refute it and the sample parsed with no
loss) or FAILED (with a human-readable ``reason`` — never a silent failure).
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

SCHEMA_VERSION = 2

# Closed status vocabulary (anti-ambiguity: a recipe is never in an unnamed state).
STATUS_DRAFT = "DRAFT"
STATUS_VERIFIED = "VERIFIED"
STATUS_FAILED = "FAILED"
_VALID_STATUS = {STATUS_DRAFT, STATUS_VERIFIED, STATUS_FAILED}


@dataclass
class Transport:
    """How bytes are fetched. ``engine`` selects the runner's fetch strategy."""
    engine: str = "http"                       # http | curl_cffi | browser
    base_url: str = ""                         # scheme+host the recipe is anchored to
    impersonate: str | None = None             # curl_cffi target (e.g. 'chrome146'); None for plain http
    timeout_s: int = 40


@dataclass
class Fingerprint:
    """The identity the transport presents. For Tier-0 this is just a UA string;
    Tier-1 recipes additionally pin a known-good JA3 (never randomized — §3)."""
    user_agent: str | None = None
    ja3: str | None = None                     # pinned allowlist fingerprint (Tier-1 only)


@dataclass
class Pagination:
    """How the dealer's full inventory is enumerated and where to stop."""
    strategy: str = "page_param"               # page_param | cursor | sitemap | single_page
    url_template: str = ""                     # e.g. '/profesionales/{slug}?atype=C&page={page}'
    page_size: int | None = None
    declared_path: str | None = None           # JSON key carrying the source's own total (the oracle)
    stop: str = "declared_reached"             # declared_reached | empty_page


@dataclass
class Parsing:
    """The extraction engine + field-map. ``engine`` follows the §4 cost ladder:
    structured (extruct/__NEXT_DATA__, cost 0) -> css selectors -> llm_local."""
    engine: str = "next_data"                  # next_data | jsonld | css | llm_local
    container_path: str | None = None          # where the listings array lives (e.g. 'listings')
    field_map: dict[str, str] = field(default_factory=dict)


@dataclass
class Evidence:
    """The VAM proof the recipe carries. Filled by the harness at verify time.

    ``vam_verdict`` is the verdict string returned by
    :func:`pipeline.verify.record_count_verdict` (or ``'OFFLINE'`` when verified
    without a DB seal). ``declared``/``fetched``/``parsed`` are the sample
    arithmetic; ``parse_loss = fetched - parsed`` must be 0 for VERIFIED.
    """
    verified_at: str | None = None             # ISO-8601 timestamp (injected; never Date.now-style)
    sample_k: int | None = None
    declared: int | None = None
    fetched: int | None = None
    parsed: int | None = None
    vam_verdict: str | None = None
    vam_paths: dict[str, int] = field(default_factory=dict)

    @property
    def parse_loss(self) -> int | None:
        if self.fetched is None or self.parsed is None:
            return None
        return self.fetched - self.parsed


@dataclass
class Recipe:
    """A complete, reproducible per-dealer extraction recipe."""
    source: str                                # 'autoscout24', 'autocasion', ...
    dealer_ref: str                            # the source's stable id/slug for the dealer
    kind: str = "compraventa"
    cdp_code: str | None = None                # set once the dealer is minted
    status: str = STATUS_DRAFT
    reason: str | None = None                  # why FAILED (or a VERIFIED note)
    schema_version: int = SCHEMA_VERSION
    transport: Transport = field(default_factory=Transport)
    fingerprint: Fingerprint = field(default_factory=Fingerprint)
    pagination: Pagination = field(default_factory=Pagination)
    parsing: Parsing = field(default_factory=Parsing)
    evidence: Evidence = field(default_factory=Evidence)

    def __post_init__(self) -> None:
        if self.status not in _VALID_STATUS:
            raise ValueError(
                f"Recipe.status must be one of {sorted(_VALID_STATUS)}, got {self.status!r}")

    # -- serialization -------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        """Plain nested dict, ready for :func:`pipeline.recipe.write_recipe` (YAML).

        Insertion order is meaningful for the committed YAML (human-readable top
        matter first), so the keys are emitted in a deliberate order rather than
        relying on ``asdict`` field order alone.
        """
        d = asdict(self)
        ordered = {
            "schema_version": d["schema_version"],
            "source": d["source"],
            "dealer_ref": d["dealer_ref"],
            "kind": d["kind"],
            "cdp_code": d["cdp_code"],
            "status": d["status"],
            "reason": d["reason"],
            "transport": d["transport"],
            "fingerprint": d["fingerprint"],
            "pagination": d["pagination"],
            "parsing": d["parsing"],
            "evidence": d["evidence"],
        }
        return ordered

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Recipe":
        """Rebuild a Recipe from a parsed YAML dict (the round-trip inverse).

        Unknown/extra keys are ignored defensively so a newer file does not crash an
        older loader; missing nested blocks fall back to dataclass defaults.
        """
        def _sub(key: str, klass):
            raw = d.get(key) or {}
            valid = {f for f in klass.__dataclass_fields__}
            return klass(**{k: v for k, v in raw.items() if k in valid})

        return cls(
            source=d["source"],
            dealer_ref=d["dealer_ref"],
            kind=d.get("kind", "compraventa"),
            cdp_code=d.get("cdp_code"),
            status=d.get("status", STATUS_DRAFT),
            reason=d.get("reason"),
            schema_version=d.get("schema_version", SCHEMA_VERSION),
            transport=_sub("transport", Transport),
            fingerprint=_sub("fingerprint", Fingerprint),
            pagination=_sub("pagination", Pagination),
            parsing=_sub("parsing", Parsing),
            evidence=_sub("evidence", Evidence),
        )
