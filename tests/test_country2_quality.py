"""P3 country-#2 readiness — the last batch of country-BLIND quality/degradation seams.

Six engineering seams that hard-coded ES (or :5433 PRODUCTION) where a second tenant needs a
parameter. Every fix DEFAULTS to ``ES`` so the single-tenant census is BYTE-IDENTICAL; passing a
different ``country_code`` is the only thing that changes behaviour.

  #13 splink_merge   — legal-form suffix set + phone key + dealer load are now country-aware.
  #14 gestionador    — pooled baselines/cohorts (field_loss, price_trap) partition by country;
                       per-subject detectors (fabrication) stamp the subject's real country.
  #15 price_sanity   — the EUR/ES €5M ceiling is a per-country hook (default 5M).
  #16 free_proxies   — the proxy egress country is a run parameter (default ES).
  #17 capture        — the module DSN derives from CARDEEP_DSN (was a :5433 PRODUCTION constant).
  #18 load_geo       — ``--country`` threads country_code into the geo INSERTs (default ES).

Pure unit — no DB, no network. The detector mocks mirror tests/test_gestionador.py (AsyncMock conn).
"""
from __future__ import annotations

import asyncio
import importlib
import inspect
import os
from unittest.mock import AsyncMock

import pytest

pytestmark = pytest.mark.unit


def _run(coro):
    return asyncio.run(coro)


# ===========================================================================
# #13 — splink_merge: country-aware legal-form suffix, phone key, dealer load
# ===========================================================================
class TestSplinkSuffixCountryAware:
    def test_es_default_byte_identical(self):
        """ES (default) strips its OWN legal forms EXACTLY as the frozen golden gate."""
        from pipeline.exhaustiveness import splink_merge as sm

        # the exact assertion pinned by test_exhaustiveness.test_splink_normalisers
        assert sm._norm_name("AUTOMOCIÓN del Oeste, S.L.") == "automocion del oeste"
        assert sm._norm_name("Talleres García S.L.U.") == "talleres garcia"
        # ES must NOT strip a German form (it is not an ES legal suffix)
        assert sm._norm_name("Muller GmbH") == "muller gmbh"

    def test_de_strips_german_legal_forms(self):
        """DE strips GmbH / AG / e.K. / GmbH & Co. KG; leaves the Spanish 's l' alone."""
        from pipeline.exhaustiveness import splink_merge as sm

        assert sm._norm_name("Müller Automobile GmbH", country_code="DE") == "muller automobile"
        assert sm._norm_name("Auto Becker AG", country_code="DE") == "auto becker"
        assert sm._norm_name("Schmidt e.K.", country_code="DE") == "schmidt"
        assert sm._norm_name("Weber GmbH & Co. KG", country_code="DE") == "weber"
        # a Spanish suffix is NOT a German legal form -> left intact under DE
        assert sm._norm_name("Auto S L", country_code="DE") == "auto s l"


class TestSplinkPhoneCountryAware:
    def test_es_valid_phone_byte_identical(self):
        """A valid ES number yields the SAME 9-digit national key (golden-gate parity)."""
        from pipeline.exhaustiveness import splink_merge as sm

        assert sm._digits("+34 911-22-33-44") == "911223344"
        assert sm._digits("612345678") == "612345678"

    def test_es_malformed_phone_now_rejected(self):
        """Hardened like cross_source_dedup: a malformed string is no longer a fragile last-9 key."""
        from pipeline.exhaustiveness import splink_merge as sm

        assert sm._digits("612345678100") is None   # number + extension (legacy gave '345678100')
        assert sm._digits("00") is None

    def test_de_phone_uses_e164_key(self):
        """A German number yields a collision-proof E.164 key, never a bogus last-9."""
        from pipeline.exhaustiveness import splink_merge as sm

        assert sm._digits("+49 30 12345678", country_code="DE") == "+493012345678"


class TestSplinkLoadDealersCountryFilter:
    def test_load_dealers_filters_by_country(self):
        """_load_dealers must scope the entity census to its country (province codes collide)."""
        from pipeline.exhaustiveness import splink_merge as sm

        captured: dict = {}

        class _Cur:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def execute(self, sql, params=None):
                captured["sql"] = sql
                captured["params"] = params

            def fetchall(self):
                return []

        class _Conn:
            def cursor(self):
                return _Cur()

        sm._load_dealers(_Conn(), country_code="DE")
        assert "country_code" in captured["sql"].lower(), "dealer load is not country-filtered"
        assert "DE" in (captured["params"] or ()), f"country param not bound: {captured['params']!r}"


# ===========================================================================
# #14 — gestionador: pooled baselines/cohorts partition by country
# ===========================================================================
def _baseline(country, total, price_null=0, year_null=0, km_null=0, photo_url_null=0):
    return {
        "country_code": country, "total": total, "price_null": price_null,
        "year_null": year_null, "km_null": km_null, "photo_url_null": photo_url_null,
    }


class TestFieldLossBaselinePerCountry:
    def test_baseline_is_per_country_not_pooled(self):
        """An ES source's null-rate is judged against the ES baseline ALONE.

        A degenerate DE baseline (80% price-null) would, if POOLED, lift p0 to ~0.41 and MASK the
        ES source's real 0.012 -> 0.457 spike. Per-country keeps ES vs ES -> the spike fires.
        """
        from pipeline.gestionador.detect import detect_field_loss

        baselines = [
            _baseline("ES", 10_000, price_null=120),     # ES global p0 = 0.012
            _baseline("DE", 10_000, price_null=8_000),   # degenerate DE (would poison a pooled p0)
        ]
        recent = [{
            "country_code": "ES", "source_key": "coches_net", "n": 140,
            "price_null": 64, "year_null": 0, "km_null": 0, "photo_url_null": 0,  # p1 = 0.457
        }]
        conn = AsyncMock()
        conn.fetch = AsyncMock(side_effect=[baselines, recent])

        results = _run(detect_field_loss(conn))
        price = [r for r in results if r.measured.get("field") == "price"]
        assert len(price) == 1, "ES price-null spike must fire against the ES (not pooled) baseline"
        assert price[0].country_code == "ES"
        assert price[0].severity == "critical"


class TestFabricationStampsCountry:
    def test_oob_stamps_subject_country(self):
        """An out-of-band DE vehicle item carries country_code='DE' (not the default 'ES')."""
        from pipeline.gestionador.detect import detect_fabrication, _daily_bucket

        oob_de = {"vehicle_ulid": "01DEVEHICLE0000000000000001", "cdp_code": "CDP-DE-28-ABC12345",
                  "price": -5, "year": 2018, "km": 100, "country_code": "DE"}
        conn = AsyncMock()
        conn.fetch = AsyncMock(side_effect=[[oob_de], [], []])

        results = _run(detect_fabrication(conn))
        veh = [r for r in results if r.subject_type == "vehicle"]
        assert len(veh) == 1
        assert veh[0].country_code == "DE", "fabrication item must carry the subject's real country"
        # subject is globally-unique (vehicle_ulid) -> dedupe_key is NOT country-prefixed (byte-identical)
        assert veh[0].dedupe_key == f"fabrication|01DEVEHICLE0000000000000001|{_daily_bucket()}"

    def test_oob_defaults_es_when_country_absent(self):
        """Byte-identity guard: a row without country_code (legacy mock) defaults to 'ES'."""
        from pipeline.gestionador.detect import detect_fabrication

        oob = {"vehicle_ulid": "01ESVEHICLE0000000000000001", "cdp_code": "CDP-ES-08-AAA",
               "price": 15000, "year": 2018, "km": 1_100_000}  # no country_code key
        conn = AsyncMock()
        conn.fetch = AsyncMock(side_effect=[[oob], [], []])

        veh = [r for r in _run(detect_fabrication(conn)) if r.subject_type == "vehicle"]
        assert len(veh) == 1 and veh[0].country_code == "ES"


# ===========================================================================
# #15 — price_sanity: EUR/ES €5M ceiling is a per-country hook
# ===========================================================================
class TestPriceBandPerCountry:
    def test_es_default_byte_identical(self):
        from pipeline import price_sanity as ps

        assert ps.sanitize_price(5_000_000) == 5_000_000     # exactly the ceiling kept
        assert ps.sanitize_price(5_000_001) is None          # one euro over -> nulled
        assert ps.sanitize_price(5_000_001, country_code="ES") is None

    def test_band_is_parametrizable_per_country(self, monkeypatch):
        from pipeline import price_sanity as ps

        # OPS onboards a country with a different ceiling; the engineering hook must honour it.
        monkeypatch.setitem(ps._PRICE_MAX_BY_COUNTRY, "ZZ", 10_000_000)
        assert ps.sanitize_price(8_000_000, country_code="ZZ") == 8_000_000
        assert ps.sanitize_price(8_000_000) is None          # ES default still €5M
        assert ps.price_max_for("ES") == 5_000_000
        assert ps.price_max_for("UNKNOWN") == 5_000_000       # falls back to the default ceiling


# ===========================================================================
# #16 — free_proxies: egress country is a run parameter
# ===========================================================================
class TestFreeProxyCountryParam:
    def test_source_urls_default_es(self):
        from pipeline.engine import free_proxies as fp

        urls = fp._source_urls()
        assert urls and all("country=ES" in u for u in urls)

    def test_source_urls_parametrized(self):
        from pipeline.engine import free_proxies as fp

        urls = fp._source_urls("DE")
        assert urls and all("country=DE" in u for u in urls)
        assert not any("country=ES" in u for u in urls)

    def test_public_surface_accepts_country(self):
        from pipeline.engine import free_proxies as fp

        for fn in (fp.fetch_candidates, fp.harvest_alive, fp.refresh_pool_urls):
            assert "country" in inspect.signature(fn).parameters, f"{fn.__name__} missing country param"


# ===========================================================================
# #17 — capture: module DSN derives from CARDEEP_DSN (isolation smell)
# ===========================================================================
class TestCaptureDsnFromEnv:
    _DEFAULT = "postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep"

    @staticmethod
    def _reload_capture():
        import pipeline.exhaustiveness.capture as cap
        return importlib.reload(cap)

    def test_dsn_honors_env(self):
        import pipeline.exhaustiveness.capture as cap

        orig = os.environ.get("CARDEEP_DSN")
        try:
            os.environ["CARDEEP_DSN"] = "postgres://u:p@localhost:5434/dryrun"
            cap = self._reload_capture()
            assert cap.DSN == "postgres://u:p@localhost:5434/dryrun"
        finally:
            if orig is None:
                os.environ.pop("CARDEEP_DSN", None)
            else:
                os.environ["CARDEEP_DSN"] = orig
            self._reload_capture()  # restore the module to the ambient env

    def test_dsn_default_byte_identical(self):
        orig = os.environ.get("CARDEEP_DSN")
        try:
            os.environ.pop("CARDEEP_DSN", None)
            cap = self._reload_capture()
            assert cap.DSN == self._DEFAULT      # unchanged when the env is unset
        finally:
            if orig is not None:
                os.environ["CARDEEP_DSN"] = orig
            self._reload_capture()


# ===========================================================================
# #18 — load_geo: --country threads country_code into the geo INSERTs
# ===========================================================================
class TestLoadGeoCountry:
    def test_parse_args_country_default_and_override(self):
        from scripts import load_geo as lg

        assert lg.parse_args([]).country == "ES"
        assert lg.parse_args(["--country", "DE"]).country == "DE"

    def test_main_threads_country_into_inserts(self, monkeypatch):
        from scripts import load_geo as lg

        calls: list = []

        class _Conn:
            async def executemany(self, sql, rows):
                calls.append((sql, list(rows)))

            async def fetchval(self, *a, **k):
                return 0

            async def close(self):
                return None

        async def _fake_connect(dsn, **k):
            return _Conn()

        monkeypatch.setattr(lg.asyncpg, "connect", _fake_connect)
        monkeypatch.setattr(lg, "read_municipalities", lambda *a, **k: [("28001", "Madrid", "28")])

        _run(lg.main(country="DE"))

        prov = next(c for c in calls if "geo_province" in c[0])
        muni = next(c for c in calls if "geo_municipality" in c[0])
        assert "country_code" in prov[0].lower() and "country_code" in muni[0].lower()
        assert all(row[0] == "DE" for row in prov[1]), "province rows must carry the --country code"
        assert all(row[0] == "DE" for row in muni[1]), "municipality rows must carry the --country code"
