"""CountryProfile — loader for the ``countries/<CC>/country.toml`` pack manifest.

COUNTRY-PACK-CONTRACT.md pieces 1 (``country_code``) + 8 (``CDP-{CC}-`` prefix) + the §4 physical
form. ``country.toml`` is the manifest that names the country and the two engine constants a pack
must override per country:

  * ``subdivision.regex`` — the first-level subdivision validator that replaces
    ``pipeline/complete.py:_PROVINCE_RE`` (open item OI-5).
  * ``kinds.national`` — the national-kinds override of ``pipeline/complete.py:_NATIONAL_KINDS``.

Scope (Fase B foundation): this module is JUST the loader + the data accessor. It does NOT rewire
``complete.py`` to consume the profile — that de-cegado is Fase A/E. ES behaviour is untouched.

Uses ``tomllib`` (stdlib, Python 3.11+). Validation is fail-fast at the system boundary: a missing
manifest, a country_code mismatch, or a malformed/absent required field raises rather than guessing.
"""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

# Repo root = the parent of the ``pipeline`` package directory; country packs live in
# ``<root>/countries/<CC>/``.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_COUNTRIES_DIR = _REPO_ROOT / "countries"

# ISO-3166 alpha-2 shape (contract piece 1 gate: country_code matches ^[A-Z]{2}$).
_CC_RE = re.compile(r"^[A-Z]{2}$")


@dataclass(frozen=True)
class CountryProfile:
    """Immutable view over a country pack manifest.

    Attributes
    ----------
    country_code : str
        ISO-3166 alpha-2 tenant code (e.g. ``"ES"``).
    subdivision_regex : str
        Anchored regex string validating a first-level subdivision code (replacement for
        ``complete.py:_PROVINCE_RE``). Use :meth:`matches_subdivision` to test a code.
    national_kinds : frozenset[str]
        Dealer kinds that operate country-wide and carry a NULL ``province_code`` by design
        (override of ``complete.py:_NATIONAL_KINDS``).
    geo, census : Mapping[str, str]
        Optional reference sections (pieces 2 / 5). Empty when the manifest omits them.
    """

    country_code: str
    subdivision_regex: str
    national_kinds: frozenset[str]
    geo: Mapping[str, str]
    census: Mapping[str, str]

    def matches_subdivision(self, code: str) -> bool:
        """Return True iff ``code`` is a valid first-level subdivision for this country.

        The ES pattern is fully anchored (``^…$``); ``re.match`` therefore enforces a full match.
        The ``re`` module caches compiled patterns, so repeated calls stay cheap without holding a
        compiled object on this frozen dataclass.
        """
        return re.match(self.subdivision_regex, code) is not None

    @classmethod
    def load(cls, country_code: str) -> "CountryProfile":
        """Load ``countries/<CC>/country.toml`` for ``country_code``.

        Raises
        ------
        ValueError
            If ``country_code`` is not ISO-3166 alpha-2 shaped, or the manifest is malformed,
            or its declared ``country_code`` disagrees with the request.
        FileNotFoundError
            If no manifest exists for the country.
        """
        cc = country_code.strip().upper()
        if not _CC_RE.match(cc):
            raise ValueError(
                f"country_code must match ^[A-Z]{{2}}$, got {country_code!r}"
            )
        path = _COUNTRIES_DIR / cc / "country.toml"
        if not path.is_file():
            raise FileNotFoundError(f"country pack manifest not found: {path}")
        with path.open("rb") as fh:
            data: dict[str, Any] = tomllib.load(fh)
        return cls._from_manifest(cc, data, path)

    @classmethod
    def load_dir(cls, pack_dir: "Path | str") -> "CountryProfile":
        """Load a pack manifest from an ARBITRARY directory (``pack_dir/country.toml``).

        Unlike :meth:`load`, this does NOT hard-code the canonical ``countries/<CC>/`` location:
        it validates whatever pack lives at ``pack_dir`` and derives the ``country_code`` from the
        manifest itself. This is the loader the country-autopilot auditor (Fase D) uses to lint a
        PROPOSED or staged pack — including synthetic packs under a temp dir — before it is blessed
        into the repo. ``load`` is left untouched, so ES stays byte-identical.

        Raises
        ------
        FileNotFoundError
            If ``pack_dir/country.toml`` does not exist.
        ValueError
            If the manifest's ``country_code`` is not ISO-3166 alpha-2 shaped, or the manifest is
            malformed (missing/invalid ``[subdivision].regex``, bad ``[kinds].national``).
        """
        path = Path(pack_dir) / "country.toml"
        if not path.is_file():
            raise FileNotFoundError(f"country pack manifest not found: {path}")
        with path.open("rb") as fh:
            data: dict[str, Any] = tomllib.load(fh)
        declared = data.get("country_code")
        if not isinstance(declared, str) or not _CC_RE.match(declared):
            raise ValueError(
                f"{path}: country_code must match ^[A-Z]{{2}}$, got {declared!r}"
            )
        return cls._from_manifest(declared, data, path)

    @classmethod
    def _from_manifest(
        cls, cc: str, data: Mapping[str, Any], path: Path
    ) -> "CountryProfile":
        declared = data.get("country_code")
        if declared != cc:
            raise ValueError(
                f"{path}: declared country_code {declared!r} != requested {cc!r}"
            )

        subdivision = data.get("subdivision") or {}
        regex = subdivision.get("regex")
        if not isinstance(regex, str) or not regex:
            raise ValueError(f"{path}: [subdivision].regex is required and must be a string")
        try:
            re.compile(regex)
        except re.error as exc:
            raise ValueError(
                f"{path}: [subdivision].regex is not a valid regex: {exc}"
            ) from exc

        kinds = data.get("kinds") or {}
        national = kinds.get("national", [])
        if not isinstance(national, list) or not all(isinstance(k, str) for k in national):
            raise ValueError(f"{path}: [kinds].national must be a list of strings")

        geo = {str(k): str(v) for k, v in (data.get("geo") or {}).items()}
        census = {str(k): str(v) for k, v in (data.get("census") or {}).items()}

        return cls(
            country_code=cc,
            subdivision_regex=regex,
            national_kinds=frozenset(national),
            geo=MappingProxyType(geo),
            census=MappingProxyType(census),
        )
