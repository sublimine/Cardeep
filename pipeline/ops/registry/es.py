"""ES harvest pack — the Spanish ``source_key → SourceEntry`` registry (PIECE 4).

Moved VERBATIM out of ``pipeline/ops/scheduler.py`` by the motor↔pack split
(COUNTRY-PACK-CONTRACT.md §4). These ~50 entries are 100% ES-specific pack data; the
scheduler (motor) consumes them via ``get_harvest_registry('ES')``. Byte-identity with
the pre-split inline registry is pinned by ``tests/test_registry_split.py``.

# ---------------------------------------------------------------------------
# Source → module registry
#
# Built by grepping SOURCE_KEY/FAMILY_KEY/MB_SOURCE_KEY constants from
# pipeline/platform/*.py (verified 2026-06-14).
#
# Multi-source modules:
#   group_rentacar_vo_wholesale: 6 source_keys → same module, disambiguated
#     via --member <key> where key = source_key suffix after "group_rentacar_vo_"
#   faciliteacoches_racc_wholesale: 2 source_keys → same module, disambiguated
#     via --members <faciliteacoches|racc> (maps to "faciliteacoches" / "racc")
#   group_vo_chains_wholesale: 4 source_keys → same module, via --members <key>
#     where key = source_key suffix after "group_vo_chains_"
#   oem_bmw_mini_wholesale: 2 source_keys → same module, via --brand <bmw|mini>
#
# The "cmd" field is the full argv list that would be passed to subprocess.
# All entries use sys.executable so the correct interpreter (venv or system) is used.
# ---------------------------------------------------------------------------
"""
from __future__ import annotations

from pipeline.ops.registry import SourceEntry

# Authoritative ES harvest entries, in scheduling order. Order is part of the
# byte-identity contract (the scheduler keys a dict off this list).
ENTRIES: list[SourceEntry] = [
    # ── Tier-1 (24h) ─────────────────────────────────────────────────
    # Audit 2026-06-15 Phase 2: production scheduled the PROOF/capped strategy for EVERY Tier-1
    # platform — autocasion (10k SSR cap), coches.net (~500-car 5-page slice), wallapop (flat
    # ~347k vs 651k), coches.com (16k VO-only), motor.es (10k VO-only). Each entry below now runs
    # the CANONICAL COMPLETE harvester. The source_key is KEPT equal to the *_SOURCE_KEY the
    # connector writes to source_health (facets import their wholesale's SOURCE_KEY), so
    # health/breaker/harvest_run continuity and due-selection matching hold — this also repairs
    # the F-autocasion-orphaned regression (a renamed key orphaned autocasion from scheduling).
    SourceEntry("autocasion_wholesale",   # key=AC_SOURCE_KEY (facet imports it); module=facet
                "pipeline.platform.autocasion_facet", ["--segment", "all", "--makes", "all"]),
    SourceEntry("coches_com_wholesale",   # no facet module; --all --segment all = full uncapped drain
                "pipeline.platform.coches_com_wholesale", ["--all", "--segment", "all"]),
    SourceEntry("coches_net_wholesale",   # key=COCHES_SOURCE_KEY (facet imports it); module=facet
                "pipeline.platform.coches_net_facet", []),
    SourceEntry("coches_net_segments",    # own key (audit C-cochesnet-segments); new/km0/renting, seeded 0039
                "pipeline.platform.coches_net_segments", []),
    SourceEntry("milanuncios_wholesale",
                "pipeline.platform.milanuncios_wholesale", []),
    SourceEntry("motor_es_wholesale",     # BOUNDED resumable slice (FASE 4 trigger-fix): the prior
                # --full --segment all drained the ~51k census in one ~4.7h run -> exceeded the 4h
                # SUBPROCESS_TIMEOUT wall -> SIGKILLed before record_run -> silent re-timeout each
                # cadence (last_ok stuck 2026-06-15). --cursor advances a persistent per-segment cell
                # offset across ticks so ~ceil(cells/40) runs cover the whole make->model partition,
                # each finishing well inside the wall and writing last_ok (watchdog clears, breaker 0).
                "pipeline.platform.motor_es_wholesale",
                ["--segment", "all", "--max-cells", "40", "--limit", "12000", "--cursor"]),
    SourceEntry("wallapop_wholesale",     # key=WP_SOURCE_KEY (facet imports it); module=facet
                "pipeline.platform.wallapop_facet", []),

    # ── OEM / groups / subastas (168h) ───────────────────────────────
    # AS24 (audit C-as24-unscheduled): schedule autoscout24_wholesale — it WRITES record_run and is
    # governor-paced. NOT the literal 'as24' per-dealer driver (scale_as24.py), which never writes
    # last_ok -> would be perpetually DUE every 15-min tick = the AS24 ban scar. Ban-safe 168h cadence
    # lives in the 0039 seed row (the connector doesn't pass harvest_interval_hours). This 12-page
    # proof slice closes the cadence/auto-repair gap, NOT full ~278k coverage (that stays operator-run).
    SourceEntry("as24_wholesale",
                "pipeline.platform.autoscout24_wholesale", []),
    SourceEntry("carandclassic_wholesale",
                "pipeline.platform.carandclassic_wholesale", []),
    SourceEntry("dasweltauto_wholesale",
                "pipeline.platform.dasweltauto_wholesale", []),
    # faciliteacoches_wholesale and racc_ocasion_wholesale share a module;
    # each is invoked independently via --members to guarantee individual
    # record_run writes and independent health tracking.
    SourceEntry("faciliteacoches_wholesale",
                "pipeline.platform.faciliteacoches_racc_wholesale",
                ["--members", "faciliteacoches"]),
    SourceEntry("racc_ocasion_wholesale",
                "pipeline.platform.faciliteacoches_racc_wholesale",
                ["--members", "racc"]),
    # group_importador: single source key
    SourceEntry("group_importador_modrive",
                "pipeline.platform.group_importador_wholesale", []),
    # group_rentacar_vo: 6 source keys, same module, --member <suffix>
    SourceEntry("group_rentacar_vo_athlon",
                "pipeline.platform.group_rentacar_vo_wholesale",
                ["--member", "athlon"]),
    SourceEntry("group_rentacar_vo_okmobility",
                "pipeline.platform.group_rentacar_vo_wholesale",
                ["--member", "okmobility"]),
    SourceEntry("group_rentacar_vo_centauro",
                "pipeline.platform.group_rentacar_vo_wholesale",
                ["--member", "centauro"]),
    SourceEntry("group_rentacar_vo_recordgo",
                "pipeline.platform.group_rentacar_vo_wholesale",
                ["--member", "recordgo"]),
    SourceEntry("group_rentacar_vo_arval",
                "pipeline.platform.group_rentacar_vo_wholesale",
                ["--member", "arval"]),
    SourceEntry("group_rentacar_vo_northgate",
                "pipeline.platform.group_rentacar_vo_wholesale",
                ["--member", "northgate"]),
    # group_subastas: single source key (AYVENS_SOURCE_KEY = group_subastas_wholesale)
    SourceEntry("group_subastas_wholesale",
                "pipeline.platform.group_subastas_wholesale", []),
    # group_vo_chains: 4 source keys, same module, --members <suffix>
    SourceEntry("group_vo_chains_flexicar",
                "pipeline.platform.group_vo_chains_wholesale",
                ["--members", "flexicar"]),
    SourceEntry("group_vo_chains_ocasionplus",
                "pipeline.platform.group_vo_chains_wholesale",
                ["--members", "ocasionplus"]),
    SourceEntry("group_vo_chains_clicars",
                "pipeline.platform.group_vo_chains_wholesale",
                ["--members", "clicars"]),
    SourceEntry("group_vo_chains_carplus",
                "pipeline.platform.group_vo_chains_wholesale",
                ["--members", "carplus"]),
    SourceEntry("localizavo_wholesale",
                "pipeline.platform.localizavo_wholesale", []),
    SourceEntry("mercedes_benz_wholesale",
                "pipeline.platform.oem_mercedes_benz_wholesale", []),
    SourceEntry("miclasico_wholesale",
                "pipeline.platform.miclasico_wholesale", []),
    SourceEntry("motorflash_wholesale",
                "pipeline.platform.motorflash_wholesale", []),
    SourceEntry("nissan_intelligent_choice_wholesale",
                "pipeline.platform.oem_nissan_mazda_honda_wholesale", []),
    SourceEntry("oem_audi_wholesale",
                "pipeline.platform.oem_audi_wholesale", []),
    # oem_bmw_mini: 2 source keys, same module, --brand <bmw|mini>
    SourceEntry("oem_bmw_premium_selection_wholesale",
                "pipeline.platform.oem_bmw_mini_wholesale",
                ["--brand", "bmw"]),
    SourceEntry("oem_mini_next_wholesale",
                "pipeline.platform.oem_bmw_mini_wholesale",
                ["--brand", "mini"]),
    SourceEntry("oem_ford_wholesale",
                "pipeline.platform.oem_ford_wholesale", []),
    SourceEntry("oem_hyundai_wholesale",
                "pipeline.platform.oem_hyundai_wholesale", []),
    SourceEntry("oem_kia_wholesale",
                "pipeline.platform.oem_kia_wholesale", []),
    SourceEntry("oem_seat_cupra_new_stock",
                "pipeline.platform.oem_seat_cupra_new_stock", []),
    SourceEntry("oem_seat_cupra_wholesale",
                "pipeline.platform.oem_seat_cupra_wholesale", []),
    SourceEntry("oem_toyota_lexus_wholesale",
                "pipeline.platform.oem_toyota_lexus_wholesale", []),
    SourceEntry("oem_volvo_jlr_suzuki_wholesale",
                "pipeline.platform.oem_volvo_jlr_suzuki_wholesale", []),
    SourceEntry("renew_wholesale",
                "pipeline.platform.renew_wholesale", []),
    SourceEntry("spoticar_wholesale",
                "pipeline.platform.spoticar_wholesale", []),
    SourceEntry("subastacar_wholesale",
                "pipeline.platform.subastacar_wholesale", []),

    # ── Own-site €0 drain (host-distributed, ban-free) ──────────────────
    # dealerprobe_ownsite: the generic own-site harvester. --from-db selects the next un-probed
    # *drainable* batch (the connector's _drainable_website filter excludes OEM-red/marketplace/
    # social hosts) and stamps a monotonic 'dealerprobe_probed' marker, so successive DUE ticks
    # drain the dealers-with-website backlog idempotently and idle near zero once drained (only
    # newly-DISCOVERED dealers reappear). Bare no-args probes NOTHING (empty targets) — --from-db
    # is mandatory; --limit bounds the per-tick batch well within the 4h subprocess wall. Ban-free:
    # probes are spread across thousands of distinct dealer hosts, not one host (no AS24 scar).
    # (Audit deferred-harvest gap: was KNOWN_UNMAPPED; now wired so the own-site drain is hands-off.)
    #
    # SAFE ACCELERATION (2026-06-23): --limit 500 -> 2000, --concurrency 16 -> 24. The own-site
    # frontier audit (LIVE PG, 2026-06-23) put real drainable backlog at ~5,052 hosts; at 500/24h
    # that is ~10 days, at 2000/24h ~2.5 days. Ban-free by construction: --concurrency widens only
    # DEALER-level parallelism (distinct hosts); per-HOST pressure is the unchanged pdp_conc=6
    # semaphore (dealerprobe_wholesale.py:364), and --pdp-conc/--pdp-delay defaults (the politeness
    # contract per host) are left untouched. Sizing within the 4h wall: 2000 dealers / 24 parallel
    # waves ~= 84 serial waves; even at a pessimistic 60s/wave ~= 84 min << 4h SUBPROCESS_TIMEOUT.
    # asyncpg pool max_size=12 / write_sem=12 caps concurrent cages (held only ~<100ms, never during
    # network I/O), so 24 parallel dealers do not starve the pool. Do NOT also raise --pdp-conc.
    SourceEntry("dealerprobe_ownsite",
                "pipeline.platform.dealerprobe_wholesale",
                ["--from-db", "--limit", "2000", "--concurrency", "24"]),

    # ── Families (720h) ───────────────────────────────────────────────
    SourceEntry("family_builder_wholesale",
                "pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale",
                []),
    SourceEntry("family_cms_wp",
                "pipeline.platform.family_cms_wordpress_dominated__wholesale", []),
    SourceEntry("family_dealerk_wp",
                "pipeline.platform.family_dealerk_wholesale", []),
    SourceEntry("family_dms_vendor_platforms",
                "pipeline.platform.family_dms_vendor_platforms__wholesale", []),
    SourceEntry("family_framework_webbuilder",
                "pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale",
                []),
    SourceEntry("family_generic_custom",
                "pipeline.platform.family_generic_custom_wholesale", []),
    SourceEntry("family_unreachable",
                "pipeline.platform.family_unreachable_wholesale", []),
]
