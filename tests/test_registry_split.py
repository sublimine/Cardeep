"""Golden — Fase B foundation, PIECE 4 split: harvest registry motor↔pack.

COUNTRY-PACK-CONTRACT.md §4 («registry/<cc>.py y el split motor↔pack») prescribes
extracting the inline ES ``REGISTRY`` out of ``pipeline/ops/scheduler.py`` into a
country-pack package ``pipeline/ops/registry/`` exposing:

    get_harvest_registry(country_code) -> list[SourceEntry]
    active_countries()                 -> list[str]

with the ~50 ES entries moved VERBATIM to ``registry/es.py``. With
``active_countries() == ['ES']`` the behaviour is **byte-identical** to the pre-split
scheduler: the scheduler harvests exactly the same sources, in the same order.

This golden pins that byte-identity. ``EXPECTED_ES`` is a frozen snapshot of the
authoritative ES registry captured from the live ``_build_registry()`` BEFORE the split
(50 ordered ``(source_key, module, extra_args)`` tuples). Any drift — a renamed key, a
dropped entry, a mutated CLI arg, a reordering — fails here.
"""
from __future__ import annotations

import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ops.registry import (
    SourceEntry,
    active_countries,
    get_harvest_registry,
)
from pipeline.ops import scheduler


# ---------------------------------------------------------------------------
# Byte-identity snapshot: the 50 ES entries, in authoritative order, exactly as
# the pre-split scheduler._build_registry() produced them.
# ---------------------------------------------------------------------------
EXPECTED_ES: list[tuple[str, str, list[str]]] = [
    ('autocasion_wholesale', 'pipeline.platform.autocasion_facet', ['--segment', 'all', '--makes', 'all']),
    ('coches_com_wholesale', 'pipeline.platform.coches_com_wholesale', ['--all', '--segment', 'all']),
    ('coches_net_wholesale', 'pipeline.platform.coches_net_facet', []),
    ('coches_net_segments', 'pipeline.platform.coches_net_segments', []),
    ('milanuncios_wholesale', 'pipeline.platform.milanuncios_wholesale', []),
    ('motor_es_wholesale', 'pipeline.platform.motor_es_wholesale', ['--segment', 'all', '--max-cells', '40', '--limit', '12000', '--cursor']),
    ('wallapop_wholesale', 'pipeline.platform.wallapop_facet', []),
    ('as24_wholesale', 'pipeline.platform.autoscout24_wholesale', []),
    ('carandclassic_wholesale', 'pipeline.platform.carandclassic_wholesale', []),
    ('dasweltauto_wholesale', 'pipeline.platform.dasweltauto_wholesale', []),
    ('faciliteacoches_wholesale', 'pipeline.platform.faciliteacoches_racc_wholesale', ['--members', 'faciliteacoches']),
    ('racc_ocasion_wholesale', 'pipeline.platform.faciliteacoches_racc_wholesale', ['--members', 'racc']),
    ('group_importador_modrive', 'pipeline.platform.group_importador_wholesale', []),
    ('group_rentacar_vo_athlon', 'pipeline.platform.group_rentacar_vo_wholesale', ['--member', 'athlon']),
    ('group_rentacar_vo_okmobility', 'pipeline.platform.group_rentacar_vo_wholesale', ['--member', 'okmobility']),
    ('group_rentacar_vo_centauro', 'pipeline.platform.group_rentacar_vo_wholesale', ['--member', 'centauro']),
    ('group_rentacar_vo_recordgo', 'pipeline.platform.group_rentacar_vo_wholesale', ['--member', 'recordgo']),
    ('group_rentacar_vo_arval', 'pipeline.platform.group_rentacar_vo_wholesale', ['--member', 'arval']),
    ('group_rentacar_vo_northgate', 'pipeline.platform.group_rentacar_vo_wholesale', ['--member', 'northgate']),
    ('group_subastas_wholesale', 'pipeline.platform.group_subastas_wholesale', []),
    ('group_vo_chains_flexicar', 'pipeline.platform.group_vo_chains_wholesale', ['--members', 'flexicar']),
    ('group_vo_chains_ocasionplus', 'pipeline.platform.group_vo_chains_wholesale', ['--members', 'ocasionplus']),
    ('group_vo_chains_clicars', 'pipeline.platform.group_vo_chains_wholesale', ['--members', 'clicars']),
    ('group_vo_chains_carplus', 'pipeline.platform.group_vo_chains_wholesale', ['--members', 'carplus']),
    ('localizavo_wholesale', 'pipeline.platform.localizavo_wholesale', []),
    ('mercedes_benz_wholesale', 'pipeline.platform.oem_mercedes_benz_wholesale', []),
    ('miclasico_wholesale', 'pipeline.platform.miclasico_wholesale', []),
    ('motorflash_wholesale', 'pipeline.platform.motorflash_wholesale', []),
    ('nissan_intelligent_choice_wholesale', 'pipeline.platform.oem_nissan_mazda_honda_wholesale', []),
    ('oem_audi_wholesale', 'pipeline.platform.oem_audi_wholesale', []),
    ('oem_bmw_premium_selection_wholesale', 'pipeline.platform.oem_bmw_mini_wholesale', ['--brand', 'bmw']),
    ('oem_mini_next_wholesale', 'pipeline.platform.oem_bmw_mini_wholesale', ['--brand', 'mini']),
    ('oem_ford_wholesale', 'pipeline.platform.oem_ford_wholesale', []),
    ('oem_hyundai_wholesale', 'pipeline.platform.oem_hyundai_wholesale', []),
    ('oem_kia_wholesale', 'pipeline.platform.oem_kia_wholesale', []),
    ('oem_seat_cupra_new_stock', 'pipeline.platform.oem_seat_cupra_new_stock', []),
    ('oem_seat_cupra_wholesale', 'pipeline.platform.oem_seat_cupra_wholesale', []),
    ('oem_toyota_lexus_wholesale', 'pipeline.platform.oem_toyota_lexus_wholesale', []),
    ('oem_volvo_jlr_suzuki_wholesale', 'pipeline.platform.oem_volvo_jlr_suzuki_wholesale', []),
    ('renew_wholesale', 'pipeline.platform.renew_wholesale', []),
    ('spoticar_wholesale', 'pipeline.platform.spoticar_wholesale', []),
    ('subastacar_wholesale', 'pipeline.platform.subastacar_wholesale', []),
    ('dealerprobe_ownsite', 'pipeline.platform.dealerprobe_wholesale', ['--from-db', '--limit', '2000', '--concurrency', '24']),
    ('family_builder_wholesale', 'pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale', []),
    ('family_cms_wp', 'pipeline.platform.family_cms_wordpress_dominated__wholesale', []),
    ('family_dealerk_wp', 'pipeline.platform.family_dealerk_wholesale', []),
    ('family_dms_vendor_platforms', 'pipeline.platform.family_dms_vendor_platforms__wholesale', []),
    ('family_framework_webbuilder', 'pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale', []),
    ('family_generic_custom', 'pipeline.platform.family_generic_custom_wholesale', []),
    ('family_unreachable', 'pipeline.platform.family_unreachable_wholesale', []),
]


def _as_tuples(entries: list[SourceEntry]) -> list[tuple[str, str, list[str]]]:
    return [(e.source_key, e.module, e.extra_args) for e in entries]


# ---------------------------------------------------------------------------
# active_countries
# ---------------------------------------------------------------------------

class TestActiveCountries:
    def test_only_es_active(self) -> None:
        assert active_countries() == ["ES"]

    def test_returns_fresh_list(self) -> None:
        """Mutating the result must not corrupt the canonical set."""
        a = active_countries()
        a.append("XX")
        assert active_countries() == ["ES"]


# ---------------------------------------------------------------------------
# get_harvest_registry — the byte-identity contract
# ---------------------------------------------------------------------------

class TestHarvestRegistryES:
    def test_es_registry_is_byte_identical_snapshot(self) -> None:
        """get_harvest_registry('ES') == the pre-split _build_registry() set, same order."""
        reg = get_harvest_registry("ES")
        assert _as_tuples(reg) == EXPECTED_ES

    def test_all_entries_are_source_entry(self) -> None:
        for e in get_harvest_registry("ES"):
            assert isinstance(e, SourceEntry)

    def test_exactly_50_entries_no_dups(self) -> None:
        reg = get_harvest_registry("ES")
        assert len(reg) == 50
        assert len({e.source_key for e in reg}) == 50

    def test_returns_fresh_list_each_call(self) -> None:
        """Caller mutation must not leak into the canonical registry."""
        reg = get_harvest_registry("ES")
        reg.append(SourceEntry("inject", "x", []))
        assert len(get_harvest_registry("ES")) == 50


class TestHarvestRegistryNonActive:
    def test_non_active_country_returns_empty(self) -> None:
        assert get_harvest_registry("DE") == []

    def test_unknown_country_returns_empty(self) -> None:
        assert get_harvest_registry("XX") == []

    def test_empty_country_returns_empty(self) -> None:
        assert get_harvest_registry("") == []


# ---------------------------------------------------------------------------
# Scheduler byte-identity: the scheduler must consume the new path and produce
# the SAME REGISTRY dict (content + order) it had before the split.
# ---------------------------------------------------------------------------

class TestSchedulerByteIdentical:
    def test_scheduler_registry_matches_es_pack(self) -> None:
        reg = get_harvest_registry("ES")
        assert scheduler.REGISTRY == {e.source_key: e for e in reg}

    def test_scheduler_registry_order_preserved(self) -> None:
        reg = get_harvest_registry("ES")
        assert list(scheduler.REGISTRY.values()) == reg

    def test_scheduler_registry_is_full_snapshot(self) -> None:
        assert _as_tuples(list(scheduler.REGISTRY.values())) == EXPECTED_ES

    def test_sourceentry_reexported_from_scheduler(self) -> None:
        """test_encoding.py builds sched.SourceEntry(...) — the name must stay importable."""
        assert scheduler.SourceEntry is SourceEntry
        e = scheduler.SourceEntry(source_key="k", module="m", extra_args=[])
        assert (e.source_key, e.module, e.extra_args) == ("k", "m", [])


# ---------------------------------------------------------------------------
# Regression: the structural invariants previously guarded by
# test_scheduler_due.py::TestRegistry — re-asserted here against the ES pack so
# the signal survives without touching the live :5433 DB those tests also probe.
# ---------------------------------------------------------------------------

class TestRegistryStructuralInvariants:
    def test_all_tier1_present(self) -> None:
        keys = {e.source_key for e in get_harvest_registry("ES")}
        for k in (
            "autocasion_wholesale", "coches_com_wholesale", "coches_net_wholesale",
            "milanuncios_wholesale", "motor_es_wholesale", "wallapop_wholesale",
        ):
            assert k in keys

    def test_rentacar_six_members(self) -> None:
        by_key = {e.source_key: e for e in get_harvest_registry("ES")}
        for member in ("athlon", "okmobility", "centauro", "recordgo", "arval", "northgate"):
            e = by_key[f"group_rentacar_vo_{member}"]
            assert e.module == "pipeline.platform.group_rentacar_vo_wholesale"
            assert e.extra_args == ["--member", member]

    def test_bmw_mini_share_module_with_brand_arg(self) -> None:
        by_key = {e.source_key: e for e in get_harvest_registry("ES")}
        bmw = by_key["oem_bmw_premium_selection_wholesale"]
        mini = by_key["oem_mini_next_wholesale"]
        assert bmw.module == mini.module == "pipeline.platform.oem_bmw_mini_wholesale"
        assert bmw.extra_args == ["--brand", "bmw"]
        assert mini.extra_args == ["--brand", "mini"]

    def test_faciliteacoches_racc_separate_same_module(self) -> None:
        by_key = {e.source_key: e for e in get_harvest_registry("ES")}
        faci = by_key["faciliteacoches_wholesale"]
        racc = by_key["racc_ocasion_wholesale"]
        assert faci.module == racc.module
        assert "faciliteacoches" in faci.extra_args
        assert "racc" in racc.extra_args

    def test_dealerprobe_ownsite_drives_db_drain(self) -> None:
        by_key = {e.source_key: e for e in get_harvest_registry("ES")}
        e = by_key["dealerprobe_ownsite"]
        assert e.module == "pipeline.platform.dealerprobe_wholesale"
        assert "--from-db" in e.extra_args
        assert "--limit" in e.extra_args

    def test_seven_family_sources_present(self) -> None:
        keys = {e.source_key for e in get_harvest_registry("ES")}
        for k in (
            "family_builder_wholesale", "family_cms_wp", "family_dealerk_wp",
            "family_dms_vendor_platforms", "family_framework_webbuilder",
            "family_generic_custom", "family_unreachable",
        ):
            assert k in keys
