"""VECTOR 4 — Official registry census: BORME (Registro Mercantil) automotive incorporations.

The most orthogonal list to everything digital: its capture mechanism is *legal/fiscal*,
not commercial, so a dealer's probability of appearing here does not correlate with its
online presence. That is exactly what anchors the exhaustiveness denominator (§2) and
breaks capture heterogeneity. BORME also yields the **delta of altas** (new incorporations)
the delta engine barely exercises today.

Source: BOE open data API (https://www.boe.es/datosabiertos/api/borme) — free, no key.
Per day, section A ("Empresarios. Actos inscritos") lists, province by province, every
mercantile act. We read the per-province XML, keep **Constitución** acts whose *objeto
social* is automotive, and emit one DiscoveredEntity per new company (province from the
domicilio postcode, municipality from the domicilio).

Honesty: BORME-A carries the Registro Mercantil number and the objeto social text, but
**usually not the CIF** — so `cif` is filled only when a valid (checksum-verified) CIF
literally appears in the act. The automotive filter is on the objeto-social text, which
is the BORME-A proxy for CNAE 4511/4519/4520/4531/4532.

Recipe-first: CARDEEP_BORME_DATE pins one day; CARDEEP_BORME_DAYS sweeps the N most recent
published days (default 1); CARDEEP_BORME_MAX_PROV caps provinces per day for sampling.
Isolates cleanly if the BOE API is unreachable.
"""
from __future__ import annotations

import datetime as _dt
import os
import re

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_API = "https://www.boe.es/datosabiertos/api/borme/sumario/{date}"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0 Safari/537.36"

# Objeto-social keywords -> cardeep kind (BORME-A proxy for automotive CNAE 4511/4519/45.2/45.3).
_AUTOMOTIVE = (
    ("desguace", "desguace"),
    ("descontaminaci", "desguace"),  # "descontaminación de vehículos al final de su vida útil"
    ("compraventa de veh", "compraventa"),
    ("compra-venta de veh", "compraventa"),
    ("compraventa de autom", "compraventa"),
    ("venta de veh", "compraventa"),
    ("venta de autom", "compraventa"),
    ("comercio de veh", "compraventa"),
    ("concesionario", "concesionario_oficial"),
    ("taller", "garaje"),
    ("reparaci", "garaje"),  # qualified below by a vehicle co-term to avoid false hits
    ("recambios", "garaje"),
    ("neumatic", "garaje"),
    ("neumátic", "garaje"),
)
# A vehicle term must co-occur so generic "reparación"/"comercio" don't false-positive.
_VEHICLE_TERMS = ("veh", "autom", "coche", "turismo", "motocicl", "automóvil", "automovil")

_CIF_RE = re.compile(r"\b([ABCDEFGHJNPQRSUVW])(\d{7})([0-9A-J])\b")
_PARRAFO_RE = re.compile(r'<p class="parrafo">(.*?)</p>', re.S)
_ARTICULO_RE = re.compile(r'<p class="articulo">(.*?)</p>', re.S)


def _strip(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def _cif_control_ok(cif: str) -> bool:
    """Validate a Spanish CIF checksum (letter + 7 digits + control digit/letter)."""
    m = _CIF_RE.fullmatch(cif.strip().upper())
    if not m:
        return False
    _org, digits, control = m.groups()
    s_even = sum(int(digits[i]) for i in (1, 3, 5))           # positions 2,4,6 (0-based 1,3,5)
    s_odd = 0
    for i in (0, 2, 4, 6):                                     # positions 1,3,5,7
        d = int(digits[i]) * 2
        s_odd += d // 10 + d % 10
    total = s_even + s_odd
    cd = (10 - (total % 10)) % 10
    control_letter = "JABCDEFGHI"[cd]
    return control in (str(cd), control_letter)


def _http_json(url: str):
    import requests

    r = requests.get(url, headers={"User-Agent": _UA, "Accept": "application/json"}, timeout=30)
    if r.status_code != 200:
        return None
    return r.json()


def _http_text(url: str) -> str | None:
    import requests

    r = requests.get(url, headers={"User-Agent": _UA}, timeout=30)
    return r.text if r.status_code == 200 else None


def _classify(objeto: str) -> str | None:
    low = objeto.lower()
    has_vehicle = any(t in low for t in _VEHICLE_TERMS)
    for kw, kind in _AUTOMOTIVE:
        if kw in low:
            if kw in ("reparaci", "taller", "recambios") and not has_vehicle:
                continue  # generic repair/parts with no vehicle term -> not automotive
            return kind
    return None


class BormeCnaeAdapter(SourceAdapter):
    """V4 — BORME automotive incorporations (fiscal/legal, max orthogonality)."""

    source_key = "borme_cnae"

    def __init__(self) -> None:
        self._rows: list[DiscoveredEntity] | None = None
        self._isolated: str | None = None
        self._days_used: list[str] = []

    def _recent_dates(self) -> list[str]:
        pinned = os.environ.get("CARDEEP_BORME_DATE")
        if pinned:
            return [pinned]
        days = int(os.environ.get("CARDEEP_BORME_DAYS", "1"))
        # BORME is not published on weekends/holidays; walk back from yesterday until we
        # collect `days` published editions (probe up to 14 calendar days back).
        out: list[str] = []
        base = _dt.date(2026, 6, 20)
        env_today = os.environ.get("CARDEEP_BORME_TODAY")  # testable clock override
        if env_today:
            base = _dt.date(int(env_today[:4]), int(env_today[4:6]), int(env_today[6:8]))
        for back in range(1, 15):
            d = (base - _dt.timedelta(days=back)).strftime("%Y%m%d")
            out.append(d)
            if len(out) >= days * 3:  # over-collect candidates; published ones filtered in _build
                break
        return out

    def _build(self) -> list[DiscoveredEntity]:
        max_prov = os.environ.get("CARDEEP_BORME_MAX_PROV")
        max_prov_n = int(max_prov) if max_prov else None
        want_days = int(os.environ.get("CARDEEP_BORME_DAYS", "1")) \
            if not os.environ.get("CARDEEP_BORME_DATE") else 1
        out: list[DiscoveredEntity] = []
        seen: set[str] = set()
        reached = 0
        for date in self._recent_dates():
            if reached >= want_days:
                break
            j = _http_json(_API.format(date=date))
            if not j or j.get("status", {}).get("code") != "200":
                continue
            try:
                diario = j["data"]["sumario"]["diario"]
            except (KeyError, TypeError):
                continue
            reached += 1
            self._days_used.append(date)
            for d in diario:
                for sec in d.get("seccion", []):
                    if sec.get("codigo") != "A":
                        continue
                    items = sec.get("item", [])
                    if max_prov_n:
                        items = items[:max_prov_n]
                    for it in items:
                        xml = _http_text(it.get("url_xml") or "")
                        if not xml:
                            continue
                        out.extend(self._parse_province(xml, it.get("titulo"), seen))
        return out

    def _parse_province(self, xml: str, prov_title: str | None, seen: set[str]) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        # The XML interleaves <p class="articulo"> (company) and <p class="parrafo"> (act).
        # Walk in document order, pairing each company with its following act paragraph.
        blocks = re.findall(r'<p class="(articulo|parrafo)">(.*?)</p>', xml, re.S)
        current: str | None = None
        reg: str | None = None
        for cls, raw in blocks:
            text = _strip(raw)
            if cls == "articulo":
                m = re.match(r"(\d+)\s*-\s*(.+)", text)
                if m:
                    reg, current = m.group(1), m.group(2)
                else:
                    reg, current = None, text
                continue
            if cls != "parrafo" or not current:
                continue
            if "constituci" not in text.lower():
                continue  # only new incorporations (altas) — the delta of registral births
            mobj = re.search(r"objeto social:\s*(.+?)(?:domicilio:|capital:|$)", text, re.I)
            objeto = mobj.group(1) if mobj else text
            kind = _classify(objeto)
            if not kind:
                continue
            postcode = None
            muni = None
            mdom = re.search(r"domicilio:\s*(.+?)(?:capital:|$)", text, re.I)
            if mdom:
                dom = mdom.group(1)
                mcp = re.search(r"\b(\d{5})\b", dom)
                if mcp:
                    postcode = mcp.group(1)
                mmu = re.search(r"\(([^)]+)\)", dom)
                if mmu:
                    muni = mmu.group(1).strip()
            province = postcode[:2] if postcode else None
            cif = None
            mcif = _CIF_RE.search(text)
            if mcif and _cif_control_ok(mcif.group(0)):
                cif = mcif.group(0)
            ref = f"{reg or current}"
            if ref in seen:
                continue
            seen.add(ref)
            out.append(DiscoveredEntity(
                kind=kind,
                source_key=self.source_key,
                source_ref=ref,
                legal_name=current,
                trade_name=current,
                cif=cif,
                cnae="4511",  # BORME-A automotive proxy; refined by harvest if a precise CNAE appears
                province_name=province or (prov_title or None),
                municipality_name=muni,
                postcode=postcode,
                extra={"vector": 4, "objeto_social": objeto[:300],
                       "registro_mercantil": reg, "borme_province": prov_title},
            ))
        return out

    def _load(self) -> list[DiscoveredEntity]:
        if self._rows is not None:
            return self._rows
        try:
            self._rows = self._build()
        except Exception as e:  # noqa: BLE001
            self._isolated = f"BORME source error: {e!r}"
            self._rows = []
        if not self._rows and not self._days_used:
            self._isolated = self._isolated or "no BORME edition reachable (offline?)"
        return self._rows

    def declared_count(self) -> int | None:
        # No independent count oracle (we filter to automotive constituciones).
        return None

    def fetch(self) -> list[DiscoveredEntity]:
        rows = self._load()
        if self._isolated:
            print(f"[borme_cnae] ISOLATED — {self._isolated}")
            return []
        print(f"[borme_cnae] days={self._days_used} automotive_incorporations={len(rows)}")
        return rows
