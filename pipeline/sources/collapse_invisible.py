"""VECTOR 6 — Long-tail invisible: collapse to the real vendor by shared strong keys.

The hardest case of the mandate: the professional seller with no own web/marketplace
shop, present only as scattered records. This vector reconstructs the real vendor by
collapsing records that share a *rare strong identifier* — a checksum-valid CIF or an
E.164 phone that appears in only a handful of records — and emits one canonical vendor
entity carrying that key, so the orchestrator's cdp_code minting + the identity layer
fold the cluster into a single dealer (plano §1.3 V6 / §5).

Term-frequency discipline (the crux): a key shared by *few* records is a strong same-owner
signal; a key shared by *many* (a marketplace switchboard) is noise and is discarded. A
CIF is a legal identifier (kept from 2 upward, no cap); a phone is capped so generic
centralitas don't over-fuse. DBSCAN (haversine) over the cluster's coordinates confirms a
recurring physical point and is recorded as evidence.

Honesty: cardeep does not yet persist raw un-attributed ads (the `vehicle`/`platform_listing`
tables already attribute every listing to an entity), so V6 here operates over the
contact signals of the **existing entity table** — it is the collapser/record-linkage
contribution to the census. When a loose-ads table lands, the same engine extends to it
unchanged (the key extraction and TF logic are source-agnostic).

Pure-python, coste cero: E.164 normalization and CIF checksum are implemented inline
(no phonenumbers/stdnum dependency); DBSCAN via scikit-learn. Recipe-first via
CARDEEP_COLLAPSE_PROV (one province) and CARDEEP_COLLAPSE_LIMIT.
"""
from __future__ import annotations

import os
import re
import threading
from collections import defaultdict

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

_CIF_RE = re.compile(r"^([ABCDEFGHJNPQRSUVW])(\d{7})([0-9A-J])$")


def _run_async(coro):
    box: dict = {}

    def worker():
        import asyncio

        box["v"] = asyncio.new_event_loop().run_until_complete(coro)

    t = threading.Thread(target=worker)
    t.start()
    t.join()
    return box.get("v")


def normalize_phone_es(raw: str | None) -> str | None:
    """Best-effort Spanish E.164 normalization (no external lib)."""
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("0034"):
        digits = digits[4:]
    elif digits.startswith("34") and len(digits) == 11:
        digits = digits[2:]
    if len(digits) != 9:
        return None
    if digits[0] not in "6789":  # ES mobiles 6/7, landlines 8/9
        return None
    return "+34" + digits


def cif_control_ok(cif: str | None) -> bool:
    if not cif:
        return False
    m = _CIF_RE.match(cif.strip().upper())
    if not m:
        return False
    _org, digits, control = m.groups()
    s_even = sum(int(digits[i]) for i in (1, 3, 5))
    s_odd = 0
    for i in (0, 2, 4, 6):
        d = int(digits[i]) * 2
        s_odd += d // 10 + d % 10
    cd = (10 - ((s_even + s_odd) % 10)) % 10
    return control in (str(cd), "JABCDEFGHI"[cd])


async def _load_entities(prov: str | None, limit: int | None) -> list[dict]:
    import asyncpg

    conn = await asyncpg.connect(DSN)
    try:
        where = "WHERE status='active' AND (phone IS NOT NULL OR cif IS NOT NULL)"
        args: list = []
        if prov:
            args.append(prov)
            where += f" AND province_code = ${len(args)}"
        q = (f"SELECT entity_ulid, legal_name, trade_name, cif, phone, email, website, "
             f"province_code, municipality_code, lat, lon FROM entity {where} "
             f"ORDER BY entity_ulid")
        if limit:
            q += f" LIMIT {int(limit)}"
        return [dict(r) for r in await conn.fetch(q, *args)]
    finally:
        await conn.close()


def _dbscan_confirms(coords: list[tuple[float, float]], eps_km: float = 0.6) -> bool:
    """True if the cluster's geocoded members fall within a recurring ~eps_km point."""
    pts = [(a, b) for a, b in coords if a is not None and b is not None]
    if len(pts) < 2:
        return False
    try:
        import numpy as np
        from sklearn.cluster import DBSCAN

        rad = np.radians(np.array(pts))
        eps = eps_km / 6371.0  # haversine works in radians of earth radius
        labels = DBSCAN(eps=eps, min_samples=2, metric="haversine").fit_predict(rad)
        return any(l != -1 for l in labels)
    except Exception:  # noqa: BLE001 — sklearn missing/edge: geo is supporting evidence only
        return False


def _best(records: list[dict], field: str) -> str | None:
    for r in records:
        v = r.get(field)
        if v:
            return v
    return None


class CollapseInvisibleAdapter(SourceAdapter):
    """V6 — collapse records to the real vendor by rare CIF/phone (+ geo confirmation)."""

    source_key = "collapse_invisible"

    def __init__(self) -> None:
        self._rows: list[DiscoveredEntity] | None = None
        self._isolated: str | None = None
        self._stats: dict = {}

    def _build(self) -> list[DiscoveredEntity]:
        prov = os.environ.get("CARDEEP_COLLAPSE_PROV")
        limit = os.environ.get("CARDEEP_COLLAPSE_LIMIT")
        phone_max = int(os.environ.get("CARDEEP_COLLAPSE_PHONE_MAX", "6"))
        ents = _run_async(_load_entities(prov, int(limit) if limit else None)) or []
        if not ents:
            self._isolated = "no entities with contact signals to collapse"
            return []
        # Build inverted indexes for the two strong keys.
        by_cif: dict[str, list[dict]] = defaultdict(list)
        by_phone: dict[str, list[dict]] = defaultdict(list)
        for e in ents:
            cif = (e.get("cif") or "").strip().upper()
            if cif_control_ok(cif):
                by_cif[cif].append(e)
            ph = normalize_phone_es(e.get("phone"))
            if ph:
                by_phone[ph].append(e)
        out: list[DiscoveredEntity] = []
        seen_keys: set[str] = set()

        def emit(key_kind: str, key: str, recs: list[dict]) -> None:
            if key in seen_keys:
                return
            seen_keys.add(key)
            coords = [(r.get("lat"), r.get("lon")) for r in recs]
            geo_ok = _dbscan_confirms(coords)
            rep = recs[0]
            out.append(DiscoveredEntity(
                kind="compraventa",  # inferred professional seller
                source_key=self.source_key,
                source_ref=f"{key_kind}:{key}",
                legal_name=_best(recs, "legal_name") or _best(recs, "trade_name"),
                trade_name=_best(recs, "trade_name") or _best(recs, "legal_name"),
                cif=key if key_kind == "cif" else _best(recs, "cif"),
                province_name=rep.get("province_code"),
                municipality_name=None,  # resolved from members' municipality at ingest below
                phone=key if key_kind == "phone" else _best(recs, "phone"),
                email=_best(recs, "email"),
                website=_best(recs, "website"),
                lat=rep.get("lat"),
                lon=rep.get("lon"),
                extra={"vector": 6, "collapse_key_kind": key_kind,
                       "cluster_size": len(recs), "geo_confirmed": geo_ok,
                       "member_ulids": [str(r["entity_ulid"]) for r in recs][:25]},
            ))

        # CIF: legal identifier — collapse from 2 upward, no cap (a shared valid CIF IS one firm).
        cif_clusters = phone_clusters = 0
        for cif, recs in by_cif.items():
            if len(recs) >= 2:
                cif_clusters += 1
                emit("cif", cif, recs)
        # Phone: TF-bounded — rare (2..max) shared number = same owner; above max = switchboard noise.
        for ph, recs in by_phone.items():
            n = len(recs)
            if 2 <= n <= phone_max:
                phone_clusters += 1
                emit("phone", ph, recs)
        self._stats = {"entities_scanned": len(ents), "cif_clusters": cif_clusters,
                       "phone_clusters": phone_clusters}
        return out

    def _load(self) -> list[DiscoveredEntity]:
        if self._rows is None:
            try:
                self._rows = self._build()
            except Exception as e:  # noqa: BLE001
                self._isolated = f"collapse error: {e!r}"
                self._rows = []
        return self._rows

    def declared_count(self) -> int | None:
        return None

    def fetch(self) -> list[DiscoveredEntity]:
        rows = self._load()
        if self._isolated:
            print(f"[collapse_invisible] ISOLATED — {self._isolated}")
            return []
        print(f"[collapse_invisible] {self._stats} vendors_emitted={len(rows)}")
        return rows
