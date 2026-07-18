"""c8 support — real photo dimensions, decoupled from the scoring engine
(pipeline/marketing/listing_audit.py never fetches anything itself).

Two layers, same separation as pipeline/delta_photo.py:
  1. ``image_dimensions`` — pure, offline: bytes -> (width, height). Trivially testable
     with a synthetic in-memory image, no network needed.
  2. ``fetch_photo_dimensions`` — network: paced through the SAME per-host token-bucket
     governor the harvest fleet uses (pipeline/engine/governor.py) so a batch job
     measuring thousands of photo URLs across hundreds of CDN hosts never becomes an
     uncoordinated hammer against any one of them (00-MASTER.md S5.4: "todo job batch...
     respeta la doctrina" of paced, coordinated egress). Uses curl_cffi (already a
     hard dependency, requirements.txt:52) rather than adding a new HTTP client.
"""
from __future__ import annotations

import asyncio
from io import BytesIO

from pipeline.engine.governor import acquire, host_of

# Generous but bounded — a single oversized/slow CDN response must not stall the whole
# batch job (S8: cheap/deterministic path, no per-photo retry storm).
FETCH_TIMEOUT_S: float = 12.0
MAX_BYTES: int = 8 * 1024 * 1024  # 8MB — no legitimate car-listing photo is larger


class PhotoFetchError(RuntimeError):
    """Raised when a photo URL cannot be downloaded or decoded — the caller (the
    audit job) MUST treat this as "dimensions unknown" (c8's honest not-measured
    state), never as a silent 0x0 or a fabricated pass."""


def image_dimensions(data: bytes) -> tuple[int, int]:
    """Pure: raw image bytes -> (width, height). Raises PhotoFetchError on
    undecodable bytes (mirrors hash_image_bytes's contract in delta_photo.py)."""
    from PIL import Image  # lazy import, same rationale as delta_photo.py's _imaging()

    try:
        with Image.open(BytesIO(data)) as img:
            img.verify()
        with Image.open(BytesIO(data)) as img:
            return img.size  # (width, height)
    except Exception as exc:  # noqa: BLE001 — any PIL decode failure is the same outcome here
        raise PhotoFetchError(f"undecodable image bytes ({len(data)} bytes): {exc}") from exc


def _sync_download(url: str) -> bytes:
    from curl_cffi import requests as curl_requests

    resp = curl_requests.get(url, timeout=FETCH_TIMEOUT_S, impersonate="chrome")
    if resp.status_code != 200:
        raise PhotoFetchError(f"HTTP {resp.status_code} fetching {url}")
    content = resp.content
    if len(content) > MAX_BYTES:
        raise PhotoFetchError(f"photo exceeds {MAX_BYTES} bytes ({len(content)}) at {url}")
    return content


async def fetch_photo_dimensions(url: str) -> tuple[int, int]:
    """Governed network fetch + decode. Raises PhotoFetchError on any failure — the
    caller decides what "unknown" means for its run (c8 stays False/None, never a
    fabricated pass)."""
    await acquire(host_of(url))
    data = await asyncio.to_thread(_sync_download, url)
    return image_dimensions(data)
