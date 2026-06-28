"""OI-2 de-blinding guard: every platform mint routes through ``services.api.codes.mint_code``.

The contract (``docs/generic-engine-bible/COUNTRY-PACK-CONTRACT.md`` §6 OI-2) names the
seam: 31 ``pipeline/platform/*`` connectors minted their entity ``cdp_code`` with a
hardcoded ``f"CDP-ES-{prov}-{base32}"`` literal, bypassing the single ``mint_code`` home.
A 2nd-country harvest through such a connector would silently mint ``CDP-ES-`` and corrupt
identity. This test pins, per connector, that the literal is gone and the prefix now flows
through ``mint_code``.

For each touched connector it asserts:
  (a) BYTE-IDENTITY (ES) — the default output equals the EXACT legacy literal the connector
      produced before the routing edit (captured pre-change). ``cdp_code`` is the immutable
      dedup key of the live census; a single drifted code re-keys entities = catastrophe.
  (b) COUNTRY SEAM — passing ``country_code="DE"`` flips ONLY the 2-letter country segment
      to ``CDP-DE-`` while the province + base32 tail stay byte-identical. This is provable
      only if the prefix comes from ``mint_code`` (the one place the country segment lives),
      so it is the per-connector proof that OI-2 is closed.
  (c) NO hardcoded mint literal (``return f"CDP-..."``) survives under ``pipeline/platform``.

DB-free and pure (sha256 + mint_code), so it runs in the ``-m unit`` CI job.
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
# Fixed, arbitrary domain for the three generic ``domain``-taking mints. The value is
# irrelevant — the pin only proves the SAME input yields a byte-identical code pre/post.
_PIN_DOMAIN = "pin.example"

# (module, fn_name, arg_kind, expected_es_code).
# ``expected_es_code`` is the legacy ``f"CDP-ES-{prov}-{base32}"`` literal each connector
# emitted BEFORE OI-2 routing — captured by replaying the pre-change functions. arg_kind:
#   "noarg"        -> fn()
#   "domain"       -> fn(_PIN_DOMAIN)
#   "member:<key>" -> fn(MEMBERS[<key>])     (real instance from the committed registry)
#   "brand:<key>"  -> fn(BRANDS[<key>])      (real instance from the committed registry)
_GOLDEN: list[tuple[str, str, str, str]] = [
    ("autocasion_wholesale", "autocasion_platform_cdp_code", "noarg", "CDP-ES-00-QY06GW0B"),
    ("carandclassic_wholesale", "cc_platform_cdp_code", "noarg", "CDP-ES-00-WS3ZTNX7"),
    ("coches_com_wholesale", "coches_platform_cdp_code", "noarg", "CDP-ES-00-XM91J1NZ"),
    ("coches_net_wholesale", "coches_platform_cdp_code", "noarg", "CDP-ES-00-TKRV45RP"),
    ("dasweltauto_wholesale", "dwa_platform_cdp_code", "noarg", "CDP-ES-00-XWX9RHG7"),
    ("autoscout24_wholesale", "as24_platform_cdp_code", "noarg", "CDP-ES-00-VMCZWW5N"),
    ("miclasico_wholesale", "mc_platform_cdp_code", "noarg", "CDP-ES-00-TSJFC4J2"),
    ("group_subastas_wholesale", "ayvens_platform_cdp_code", "noarg", "CDP-ES-00-H1VCV020"),
    ("milanuncios_wholesale", "milanuncios_platform_cdp_code", "noarg", "CDP-ES-00-E382JYEH"),
    ("localizavo_wholesale", "localizavo_platform_cdp_code", "noarg", "CDP-ES-00-HFR3D62Y"),
    ("oem_audi_wholesale", "audi_platform_cdp_code", "noarg", "CDP-ES-00-NP3AWN4X"),
    ("motorflash_wholesale", "mf_platform_cdp_code", "noarg", "CDP-ES-00-WN1DMGRN"),
    ("oem_ford_wholesale", "ford_platform_cdp_code", "noarg", "CDP-ES-00-ZB6C77HC"),
    ("motor_es_wholesale", "motor_platform_cdp_code", "noarg", "CDP-ES-00-HSV4XZ2H"),
    ("oem_hyundai_wholesale", "hy_platform_cdp_code", "noarg", "CDP-ES-00-C2SVJWB5"),
    ("oem_kia_wholesale", "kia_platform_cdp_code", "noarg", "CDP-ES-00-YK54F18S"),
    ("oem_mercedes_benz_wholesale", "mercedes_benz_platform_cdp_code", "noarg", "CDP-ES-00-A57R0YK8"),
    ("oem_nissan_mazda_honda_wholesale", "nissan_platform_cdp_code", "noarg", "CDP-ES-00-TDWVVTAF"),
    ("oem_seat_cupra_new_stock", "scn_platform_cdp_code", "noarg", "CDP-ES-00-5R30HVA7"),
    ("oem_toyota_lexus_wholesale", "tl_platform_cdp_code", "noarg", "CDP-ES-00-GNAJ5S16"),
    ("oem_seat_cupra_wholesale", "sc_platform_cdp_code", "noarg", "CDP-ES-00-3N995HG6"),
    ("oem_volvo_jlr_suzuki_wholesale", "vjs_platform_cdp_code", "noarg", "CDP-ES-00-T0G18J3M"),
    ("renew_wholesale", "renew_platform_cdp_code", "noarg", "CDP-ES-00-DT59NK3D"),
    ("spoticar_wholesale", "spoticar_platform_cdp_code", "noarg", "CDP-ES-00-D6X2282Y"),
    ("subastacar_wholesale", "subastacar_platform_cdp_code", "noarg", "CDP-ES-00-S3K8PK50"),
    ("wallapop_wholesale", "wallapop_platform_cdp_code", "noarg", "CDP-ES-00-EMRH0TWQ"),
    ("faciliteacoches_racc_wholesale", "platform_cdp_code", "domain", "CDP-ES-00-7892EY0E"),
    ("group_importador_wholesale", "importer_cdp_code", "domain", "CDP-ES-00-7892EY0E"),
    ("group_vo_chains_wholesale", "chain_cdp_code", "domain", "CDP-ES-00-7892EY0E"),
    ("group_rentacar_vo_wholesale", "member_cdp_code", "member:arval", "CDP-ES-28-CVV4S3CJ"),
    ("oem_bmw_mini_wholesale", "platform_cdp_code", "brand:bmw", "CDP-ES-00-ZXZD056M"),
]

_IDS = [f"{mod}:{fn}" for mod, fn, _, _ in _GOLDEN]


def _resolve(module: str, fn_name: str):
    mod = importlib.import_module(f"pipeline.platform.{module}")
    return mod, getattr(mod, fn_name)


def _invoke(mod, fn, arg_kind: str, *, country_code: str | None = None):
    kw = {} if country_code is None else {"country_code": country_code}
    if arg_kind == "noarg":
        return fn(**kw)
    if arg_kind == "domain":
        return fn(_PIN_DOMAIN, **kw)
    kind, _, key = arg_kind.partition(":")
    if kind == "member":
        return fn(mod.MEMBERS[key], **kw)
    if kind == "brand":
        return fn(mod.BRANDS[key], **kw)
    raise AssertionError(f"unknown arg_kind {arg_kind!r}")


@pytest.mark.unit
@pytest.mark.parametrize("module,fn_name,arg_kind,expected_es", _GOLDEN, ids=_IDS)
class TestPlatformMintRouting:
    """Per-connector byte-identity + country seam."""

    def test_es_default_byte_identical(self, module, fn_name, arg_kind, expected_es):
        mod, fn = _resolve(module, fn_name)
        # Default (no country arg) reproduces the legacy literal byte-for-byte.
        assert _invoke(mod, fn, arg_kind) == expected_es, (
            f"{module}.{fn_name} drifted from its legacy CDP-ES- literal — re-keys the census")
        # Explicit country_code='ES' must equal the default (the seam exists and defaults ES).
        assert _invoke(mod, fn, arg_kind, country_code="ES") == expected_es

    def test_country_seam_flips_only_prefix(self, module, fn_name, arg_kind, expected_es):
        mod, fn = _resolve(module, fn_name)
        de = _invoke(mod, fn, arg_kind, country_code="DE")
        # Only the 2-letter country segment changes; province + base32 tail are byte-identical.
        # This is provable only if the prefix is minted by mint_code (OI-2 closed for this connector).
        assert de == "CDP-DE-" + expected_es[len("CDP-ES-"):], (
            f"{module}.{fn_name} did not route the country segment through mint_code")
        assert de.rsplit("-", 1)[1] == expected_es.rsplit("-", 1)[1]


@pytest.mark.unit
def test_no_hardcoded_mint_literal_under_platform():
    """No connector may hardcode the prefix: ``return f"CDP-..."`` must not survive.

    The legitimate mints now return ``mint_code(...)``; a re-introduced literal would
    re-blind a country. (Docstrings/recipe-id comments like ``CDP-ES-00-TKRV45RP`` are
    not ``return f"CDP-`` statements, so they do not trip this guard.)
    """
    platform_dir = _REPO_ROOT / "pipeline" / "platform"
    rx = re.compile(r'return\s+f"CDP-')
    offenders = []
    for py in sorted(platform_dir.glob("*.py")):
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            if rx.search(line):
                offenders.append(f"{py.name}:{i}: {line.strip()}")
    assert not offenders, (
        "OI-2 regression — hardcoded mint literal(s) bypass mint_code:\n" + "\n".join(offenders))
