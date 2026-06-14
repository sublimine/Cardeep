"""B4.2 — GeoResolver fuzzy + locality gazetteer tests.

Covers:
  - Real fuzzy cases from the B4.1 probe (Burgo de Osma, Ourense/Orense)
  - Bilingual island variant (Palma de Mallorca -> 07040)
  - Locality / pedanía resolution (Fuentetoba -> 42095 Golmayo)
  - Asturian parroquia via gazetteer (Casomera -> 33015 Caso)
  - Galician parroquia via gazetteer (Pasaje/Al Burgo -> 15030 A Coruña)
  - Anti-false-positive: short tokens 'la'/'las'/'el' -> None
  - Anti-false-positive: non-existent names -> None
  - Exact-match regression: Madrid, Barcelona, Sevilla still resolve
  - No cross-province bleed: same fuzzy query in the wrong province -> None

Integration tests require the cardeep-pg instance (port 5433).
All DB tests are guarded with @pytest.mark.skipif when the DB is unreachable.
"""
from __future__ import annotations

import asyncio

import pytest


# ---------------------------------------------------------------------------
# DB availability guard
# ---------------------------------------------------------------------------

def _db_available() -> bool:
    try:
        import asyncpg

        async def _check() -> bool:
            try:
                conn = await asyncpg.connect(
                    "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep",
                    timeout=3,
                )
                await conn.close()
                return True
            except Exception:
                return False

        return asyncio.run(_check())
    except Exception:
        return False


_DB_SKIP = pytest.mark.skipif(
    not _db_available(),
    reason="cardeep-pg not reachable on localhost:5433",
)


# ---------------------------------------------------------------------------
# Shared fixture: GeoResolver loaded against the real DB (module scope)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def geo_resolver():
    """Load GeoResolver once per test module against the real cardeep-pg."""
    import asyncpg
    from pipeline.geo import GeoResolver

    async def _load():
        conn = await asyncpg.connect(
            "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
        )
        try:
            return await GeoResolver.load(conn)
        finally:
            await conn.close()

    return asyncio.run(_load())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve(geo_resolver, province: str, name: str) -> str | None:
    return geo_resolver.municipality_code(province, name)


# ===========================================================================
# Class 1 — Fuzzy matches (B4.1 probe cases, score >= 88 with WRatio)
# ===========================================================================

@_DB_SKIP
class TestFuzzyMatches:
    """Real-world fuzzy cases validated by the B4.1 probe."""

    def test_burgo_de_osma_resolves(self, geo_resolver) -> None:
        """'Burgo de Osma' (short form) -> 42043 Burgo de Osma-Ciudad de Osma."""
        assert resolve(geo_resolver, "42", "Burgo de Osma") == "42043"

    def test_osma_resolves(self, geo_resolver) -> None:
        """'Osma' (even shorter form) -> 42043 via WRatio token containment."""
        assert resolve(geo_resolver, "42", "Osma") == "42043"

    def test_ourense_orense_slash_resolves(self, geo_resolver) -> None:
        """'Ourense / Orense' (bilingual slash variant) -> 32054 Ourense."""
        assert resolve(geo_resolver, "32", "Ourense / Orense") == "32054"

    def test_orense_resolves(self, geo_resolver) -> None:
        """'Orense' (Castilian alias) -> 32054 Ourense via fuzzy."""
        assert resolve(geo_resolver, "32", "Orense") == "32054"

    def test_palma_de_mallorca_resolves(self, geo_resolver) -> None:
        """'Palma de Mallorca' -> 07040 Palma (official INE name is just 'Palma')."""
        assert resolve(geo_resolver, "07", "Palma de Mallorca") == "07040"

    def test_fuzzy_scoped_to_province(self, geo_resolver) -> None:
        """'Ourense / Orense' in wrong province (42) must NOT resolve."""
        # Province 42 = Soria; Ourense is in province 32 (Ourense).
        assert resolve(geo_resolver, "42", "Ourense / Orense") is None

    def test_ambiguous_bare_name_confesses_gap(self, geo_resolver) -> None:
        """A bare 'San Martin' is genuinely ambiguous in Asturias (33): two concejos
        (San Martín del Rey Aurelio, San Martín de Oscos). The ambiguity guard must
        confess the gap (None) rather than silently pick one. Better a hole than a lie."""
        assert resolve(geo_resolver, "33", "San Martin") is None

    def test_unambiguous_fuzzy_still_resolves_after_guard(self, geo_resolver) -> None:
        """The ambiguity guard must NOT block a clear winner: 'Burgo de Osma' has a single
        dominant match in Soria (42) and still resolves despite the guard."""
        assert resolve(geo_resolver, "42", "Burgo de Osma") == "42043"


# ===========================================================================
# Class 2 — Locality / pedanía gazetteer (B4.2 step 3)
# ===========================================================================

@_DB_SKIP
class TestLocalityGazetteer:
    """Pedanías, parroquias, and barrios resolved via the INE Nomenclátor."""

    def test_fuentetoba_resolves_to_golmayo(self, geo_resolver) -> None:
        """'Fuentetoba' is a pedanía of Golmayo (42095) — key B4.1 NO_GEO case."""
        assert resolve(geo_resolver, "42", "Fuentetoba") == "42095"

    def test_barcebal_resolves(self, geo_resolver) -> None:
        """'Barcebal' is a locality of Burgo de Osma-Ciudad de Osma (42043)."""
        assert resolve(geo_resolver, "42", "Barcebal") == "42043"

    def test_navalcaballo_resolves(self, geo_resolver) -> None:
        """'Navalcaballo' is a locality of Los Rábanos (42149)."""
        assert resolve(geo_resolver, "42", "Navalcaballo") == "42149"

    def test_asturian_parroquia_casomera(self, geo_resolver) -> None:
        """'Casomera' is a parroquia (parish) of concejo Caso (33015) in Asturias."""
        assert resolve(geo_resolver, "33", "Casomera") == "33015"

    def test_galician_parroquia_pasaje_al_burgo(self, geo_resolver) -> None:
        """'Pasaje/Al Burgo' (exact INE locality name) in province 15 -> 15030 (A Coruña).

        This entry exists in the INE Nomenclátor as a named locality within the
        municipality of A Coruña (15030). The full INE name is 'Pasaje (Al Burgo)'.
        """
        assert resolve(geo_resolver, "15", "Pasaje al Burgo") == "15030"

    def test_locality_scoped_to_province(self, geo_resolver) -> None:
        """Fuentetoba is in province 42; must NOT resolve in province 28."""
        assert resolve(geo_resolver, "28", "Fuentetoba") is None


# ===========================================================================
# Class 3 — Anti-false-positives
# ===========================================================================

@_DB_SKIP
class TestAntiFalsePositives:
    """Ensure the cascade does not over-match.

    These are the guard cases validated by the B4.1 probe (0 FP requirement).
    """

    def test_short_token_la_returns_none(self, geo_resolver) -> None:
        """'la' (bare article, 2 chars) must not match any municipality in Madrid."""
        assert resolve(geo_resolver, "28", "la") is None

    def test_short_token_las_returns_none(self, geo_resolver) -> None:
        """'las' (bare article, 3 chars) must not match any municipality in Madrid."""
        assert resolve(geo_resolver, "28", "las") is None

    def test_short_token_el_returns_none(self, geo_resolver) -> None:
        """'el' (bare article, 2 chars) must not match any municipality in Madrid."""
        assert resolve(geo_resolver, "28", "el") is None

    def test_nonexistent_name_returns_none(self, geo_resolver) -> None:
        """A completely invented name must not resolve anywhere."""
        assert resolve(geo_resolver, "28", "XyzInexistentePueblo") is None

    def test_nonexistent_name_soria_returns_none(self, geo_resolver) -> None:
        """Invented Soria name (same province as probe test cases) must return None."""
        assert resolve(geo_resolver, "42", "ZZZInventadoNoPueblo") is None

    def test_very_short_query_bilbao_province(self, geo_resolver) -> None:
        """'Bil' (3 chars, < minimum query length) must not match Bilbao in prov 48."""
        assert resolve(geo_resolver, "48", "Bil") is None

    def test_two_similar_short_names_no_cross_match(self, geo_resolver) -> None:
        """'Brea' should not accidentally resolve to 'Brea de Aragón' in Zaragoza (50)
        when queried in Madrid (28), even if fuzzy score is high."""
        # 'Brea de Tajo' exists in province 28 (28028). We verify correct scoping.
        result_28 = resolve(geo_resolver, "28", "Brea")
        result_50 = resolve(geo_resolver, "50", "Brea")
        # Each province should only resolve within itself
        if result_28 is not None:
            assert result_28.startswith("28"), (
                f"Brea in prov 28 resolved to {result_28} (not province 28)"
            )
        if result_50 is not None:
            assert result_50.startswith("50"), (
                f"Brea in prov 50 resolved to {result_50} (not province 50)"
            )

    def test_la_monjia_not_in_gazetteer(self, geo_resolver) -> None:
        """'La Monjia' is a barrio de Soria that does not appear in the INE Nomenclátor."""
        assert resolve(geo_resolver, "42", "La Monjia") is None


# ===========================================================================
# Class 4 — Exact-match regression (existing behaviour must not break)
# ===========================================================================

@_DB_SKIP
class TestExactMatchRegression:
    """Verify that municipalities that resolved before B4.2 still resolve identically."""

    def test_madrid_exact(self, geo_resolver) -> None:
        assert resolve(geo_resolver, "28", "Madrid") == "28079"

    def test_barcelona_exact(self, geo_resolver) -> None:
        assert resolve(geo_resolver, "08", "Barcelona") == "08019"

    def test_sevilla_exact(self, geo_resolver) -> None:
        assert resolve(geo_resolver, "41", "Sevilla") == "41091"

    def test_ourense_exact(self, geo_resolver) -> None:
        """'Ourense' (exact official INE name) -> 32054, no fuzzy needed."""
        assert resolve(geo_resolver, "32", "Ourense") == "32054"

    def test_none_province_returns_none(self, geo_resolver) -> None:
        assert resolve(geo_resolver, None, "Madrid") is None  # type: ignore[arg-type]

    def test_none_name_returns_none(self, geo_resolver) -> None:
        assert resolve(geo_resolver, "28", None) is None  # type: ignore[arg-type]

    def test_empty_string_returns_none(self, geo_resolver) -> None:
        assert resolve(geo_resolver, "28", "") is None


# ===========================================================================
# Class 5 — Unit tests (no DB required, test pure functions)
# ===========================================================================

class TestNormFunction:
    """Unit tests for the _norm helper (no DB needed)."""

    def test_strips_accents(self) -> None:
        from pipeline.geo import _norm
        assert _norm("Córdoba") == "cordoba"

    def test_strips_accents_catalan(self) -> None:
        from pipeline.geo import _norm
        assert _norm("Lleida") == "lleida"

    def test_normalises_slash_bilingual(self) -> None:
        from pipeline.geo import _norm
        # 'Ourense / Orense' should normalise to tokens without punctuation
        result = _norm("Ourense / Orense")
        assert "ourense" in result
        assert "orense" in result

    def test_sorted_key_order_independent(self) -> None:
        from pipeline.geo import _sorted_key
        assert _sorted_key("La Rioja") == _sorted_key("Rioja La")

    def test_norm_strips_special_chars(self) -> None:
        from pipeline.geo import _norm
        assert _norm("Sant Boi de Llobregat") == "sant boi de llobregat"


class TestLoadGazetteer:
    """Unit test for _load_gazetteer (no DB, uses the real CSV file)."""

    def test_gazetteer_loads_nonempty(self) -> None:
        from pipeline.geo import _load_gazetteer
        index = _load_gazetteer()
        assert len(index) > 0, "Gazetteer must load at least one province"

    def test_gazetteer_has_prov42(self) -> None:
        from pipeline.geo import _load_gazetteer
        index = _load_gazetteer()
        assert "42" in index, "Province 42 (Soria) must be present"

    def test_gazetteer_fuentetoba_present(self) -> None:
        from pipeline.geo import _load_gazetteer, _norm
        index = _load_gazetteer()
        prov42 = index.get("42", {})
        assert _norm("Fuentetoba") in prov42, "Fuentetoba key missing from province 42 gazetteer"
        # Values are sets of municipality codes (ambiguity-aware index). Fuentetoba is a
        # unique locality, so its set is exactly {42095} (Golmayo).
        assert prov42[_norm("Fuentetoba")] == {"42095"}, "Fuentetoba should map to {42095} (Golmayo)"

    def test_gazetteer_no_diseminado_keys(self) -> None:
        from pipeline.geo import _load_gazetteer, _norm
        index = _load_gazetteer()
        diseminado_key = _norm("*Diseminado*")
        for prov, d in index.items():
            assert diseminado_key not in d, (
                f"'*Diseminado*' must not appear as a locality key (found in province {prov})"
            )

    def test_gazetteer_all_codes_5digits(self) -> None:
        from pipeline.geo import _load_gazetteer
        index = _load_gazetteer()
        for prov, d in index.items():
            for key, codes in d.items():
                for code in codes:  # values are sets of codes (ambiguity-aware index)
                    assert len(code) == 5, f"Municipality code {code!r} must be 5 digits"
                    assert code.startswith(prov), (
                        f"Code {code!r} in province {prov!r} does not start with province prefix"
                    )

    def test_gazetteer_asturias_coverage(self) -> None:
        """Province 33 (Asturias) must have > 1000 locality entries."""
        from pipeline.geo import _load_gazetteer
        index = _load_gazetteer()
        assert len(index.get("33", {})) > 1000, (
            "Asturias (prov 33) locality index should have > 1000 entries"
        )

    def test_gazetteer_ambiguous_locality_keeps_all_codes(self) -> None:
        """A generic locality name shared across municipalities must retain EVERY code,
        so the resolver detects ambiguity instead of binding to the first row read.
        'San Martín' recurs as a hamlet across several Asturian concejos (prov 33)."""
        from pipeline.geo import _load_gazetteer, _norm
        index = _load_gazetteer()
        codes = index.get("33", {}).get(_norm("San Martin"), set())
        assert len(codes) >= 2, (
            "ambiguous locality 'San Martin' must retain >1 municipality code for the guard"
        )
