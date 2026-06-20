"""autocasion CENSUS adapter — Vector 1 (marketplace-as-census), §1.

The distinction that makes this NOT a duplicate of ``autocasion_wholesale``:

  * WHOLESALE harvests *inventory* and discovers a dealer only as a by-product — it
    mints a dealer entity ONLY when a harvested car PDP happens to carry that dealer's
    AutoDealer block, and only for the capped inventory slice it drained. A dealer with a
    directory page but no car in the slice is invisible.
  * CENSUS enumerates the *seller* as a first-class entity from autocasion's own dealer
    directory sitemap (``…/stock/stock.xml`` — ~2.9k professional sellers, ``lastmod``
    daily), regardless of whether any of their inventory was ever harvested. This is the
    deliberate national seller census the mandate asks for, and the orthogonal "list" the
    §2 exhaustiveness framework needs.

Identity is engineered to dedup PERFECTLY against the wholesale dealers at the cdp_code
level: each dealer's cdp is minted from ``domain=None + name + municipality +
address='profesional:{slug}'`` — byte-for-byte the same inputs ``autocasion_wholesale``'s
``cdp_code_dealer`` uses. So a dealer already present via wholesale collapses on the
``ON CONFLICT (cdp_code)`` in ``pipeline.discover`` (only a new ``entity_source`` row with
``source_key='autocasion_census'`` is added); a dealer that wholesale never saw mints a
fresh cdp_code — that is the census's real, measurable new contribution.

Transport: the directory sitemap + each ``/profesional/{slug}`` profile page are FREE to a
Chrome TLS fingerprint (curl_cffi chrome impersonation; Cloudflare-permissive, t1_soft),
exactly like the wholesale surface. Each profile carries one server-rendered JSON-LD
``AutoDealer`` block: name, telephone, full PostalAddress (street, locality, postcode).

Run via the canonical pipeline:  python -m pipeline.discover autocasion_census
"""
from __future__ import annotations

import json
import logging
import re
import time
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

log = logging.getLogger(__name__)

_SITEMAP = "https://www.autocasion.com/uploads/sitemap-ng/stock/stock.xml"
_PROFILE = "https://www.autocasion.com/profesional/{slug}"
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
_LDJSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

# The 52 province INDEX slugs that share the /profesional/<slug> namespace with real
# dealers but are NOT sellers (they are geographic landing pages). This is a CLOSED set
# (Spain has exactly 52 provinces) — a blocklist is safer than pattern-matching dealer
# slugs, whose forms vary (…-adv-<hex>, <name>-<numericid>, bare <name>).
_PROVINCE_SLUGS = frozenset({
    "alava", "albacete", "alicante", "almeria", "asturias", "avila", "badajoz",
    "barcelona", "burgos", "caceres", "cadiz", "cantabria", "castellon", "ceuta",
    "ciudad-real", "cordoba", "cuenca", "girona", "granada", "guadalajara", "guipuzcoa",
    "huelva", "huesca", "islas-baleares", "jaen", "la-coruna", "la-rioja", "las-palmas",
    "leon", "lleida", "lugo", "madrid", "malaga", "melilla", "murcia", "navarra",
    "orense", "palencia", "pontevedra", "salamanca", "segovia", "sevilla", "soria",
    "sta-c-de-tenerife", "tarragona", "teruel", "toledo", "valencia", "valladolid",
    "vizcaya", "zamora", "zaragoza",
})


def _http_get(url: str, timeout: int = 30, retries: int = 3) -> str:
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:  # type: ignore[attr-defined]
            if e.code == 404:
                raise  # a dead directory entry — caller skips it, do not waste retries
            last_err = e
            time.sleep(1.5 * (attempt + 1))
        except Exception as e:  # noqa: BLE001 — transient network blip
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise last_err if last_err else RuntimeError(f"GET failed: {url}")


def dealer_slugs_from_sitemap(xml: str) -> list[str]:
    """Every /profesional/<slug> loc in the directory sitemap that is a real seller
    (i.e. not one of the 52 province index pages, nor the bare /profesional root)."""
    out: list[str] = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", xml):
        m = re.search(r"/profesional/([^/<>?#]+)/?$", loc)
        if not m:
            continue
        slug = m.group(1)
        if slug in _PROVINCE_SLUGS:
            continue
        out.append(slug)
    return out


def _norm_phone_es(raw: str | None) -> str | None:
    """Normalize an autocasion telephone ('+34 - 919374458', '919 374 458') to E.164-ish
    '+34XXXXXXXXX'. Conservative: only emits when it resolves to a 9-digit ES national
    number, else None (a wrong number is worse than no number for V6 collapse)."""
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("0034"):
        digits = digits[4:]
    elif digits.startswith("34") and len(digits) == 11:
        digits = digits[2:]
    if len(digits) == 9 and digits[0] in "6789":
        return f"+34{digits}"
    return None


def parse_profile(html: str) -> dict | None:
    """Extract the AutoDealer fields from a profile page's JSON-LD. None if absent."""
    for block in _LDJSON.findall(html):
        try:
            d = json.loads(block)
        except json.JSONDecodeError:
            continue
        if not isinstance(d, dict):
            continue
        t = d.get("@type")
        is_dealer = t == "AutoDealer" or (isinstance(t, list) and "AutoDealer" in t)
        if not is_dealer:
            continue
        addr = d.get("address") or {}
        if isinstance(addr, list):
            addr = addr[0] if addr else {}
        return {
            "name": (d.get("name") or "").strip() or None,
            "phone": _norm_phone_es(d.get("telephone")),
            "street": (addr.get("streetAddress") or "").strip() or None,
            "city": (addr.get("addressLocality") or "").strip() or None,
            "postcode": (str(addr.get("postalCode")).strip() or None) if addr.get("postalCode") else None,
        }
    return None


def _province_from_postcode(postcode: str | None) -> str | None:
    if postcode and len(postcode) >= 2 and postcode[:2].isdigit():
        cc = postcode[:2]
        if "01" <= cc <= "52":
            return cc
    return None


class AutocasionCensusAdapter(SourceAdapter):
    """Enumerates professional sellers from the autocasion dealer directory.

    Parameters
    ----------
    max_dealers:
        Cap the number of profile fetches (sampling). None = full census (~2.9k).
    sleep_s:
        Polite delay between profile fetches.
    """

    source_key = "autocasion_census"

    def __init__(self, max_dealers: int | None = None, sleep_s: float = 0.25) -> None:
        self._max = max_dealers
        self._sleep = sleep_s
        self._slugs: list[str] | None = None
        self._entities: list[DiscoveredEntity] | None = None
        self.excluded_count = 0  # read by pipeline.discover for the run log

    def _slug_universe(self) -> list[str]:
        if self._slugs is None:
            xml = _http_get(_SITEMAP, timeout=45)
            slugs = dealer_slugs_from_sitemap(xml)
            self._slugs = slugs if self._max is None else slugs[: self._max]
        return self._slugs

    def declared_count(self) -> int | None:
        """The source oracle: how many professional sellers this run targets from the
        directory sitemap (the full universe, or the capped sample)."""
        return len(self._slug_universe())

    def fetch(self) -> list[DiscoveredEntity]:
        if self._entities is not None:
            return self._entities
        slugs = self._slug_universe()
        out: list[DiscoveredEntity] = []
        excluded = 0
        total = len(slugs)
        for i, slug in enumerate(slugs, 1):
            try:
                html = _http_get(_PROFILE.format(slug=slug))
            except Exception as exc:  # noqa: BLE001 — a dead/blocked profile is an expected outcome
                excluded += 1
                log.warning("autocasion_census: profile fetch failed slug=%s (%s)", slug, exc)
                continue
            rec = parse_profile(html)
            if not rec or not rec.get("name"):
                excluded += 1
                continue
            prov = _province_from_postcode(rec.get("postcode"))
            out.append(DiscoveredEntity(
                kind="compraventa",
                source_key=self.source_key,
                source_ref=slug,
                legal_name=rec["name"],
                trade_name=rec["name"],
                province_name=prov,            # INE 2-digit code; geo.province_code accepts it
                municipality_name=rec.get("city"),
                # IDENTITY-MATCHING with autocasion_wholesale.cdp_code_dealer: the stable slug
                # in the address slot makes the minted cdp_code byte-identical, so an already-
                # known dealer collapses on ON CONFLICT instead of duplicating.
                address=f"profesional:{slug}",
                postcode=rec.get("postcode"),
                phone=rec.get("phone"),
                website=None,                  # NEVER the autocasion profile URL (would collapse all by domain)
                extra={
                    "source_group": "marketplace_census",
                    "vector": 1,
                    "street": rec.get("street"),
                    "profile_url": _PROFILE.format(slug=slug),
                },
            ))
            if self._sleep:
                time.sleep(self._sleep)
            if i % 100 == 0:
                log.info("autocasion_census: %d/%d profiles (%d entities, %d excluded)",
                         i, total, len(out), excluded)
        self.excluded_count = excluded
        self._entities = out
        return out
