"""P08-S1 — content-aware photo delta: perceptual hashing of listing images.

Closes the photo_hash=0/1.68M gap (migrations/0003:18). Instead of comparing the photo_url
STRING (which misses a re-photographed car kept on the same URL, and false-fires when a CDN
rotates the URL of an unchanged image), CARDEEP hashes the image PIXELS with a 64-bit
perceptual hash (pHash); the delta then fires on Hamming distance, not on a URL string.

FREE BY CONSTRUCTION: the canonical DCT pHash (same algorithm as imagehash.phash) is
implemented here on PIL + numpy + scipy ONLY -- no TensorFlow (imagededup), no new dependency.
The bytes-cache key uses hashlib.blake2b (stdlib; the BLAKE3 library is not installed, blake2b
is the free, equivalent BLAKE-family stand-in).

The network download is INJECTED (the `fetch` callable; in production the governor-wrapped
fetch_bytes) so the pure hashing core stays offline-testable and the egress stays gated behind
the per-host token bucket. The mass backfill over the live fleet is P08-S3 (gated on a free
egress route). The diff_vehicle rewrite to use pHash is P08-S2 (separate step).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from io import BytesIO
from typing import Callable

import numpy as np
from PIL import Image
from scipy.fftpack import dct

# pHash geometry: imagehash convention (hash_size=8, highfreq_factor=4 -> resize to 32x32,
# keep the top-left 8x8 low-frequency block). 64 bits -> 16 hex chars.
_HASH_SIZE = 8
_HIGHFREQ_FACTOR = 4
_IMG_SIDE = _HASH_SIZE * _HIGHFREQ_FACTOR

# Max Hamming distance (of 64) below which two photos are the SAME image (recompression /
# minor CDN re-encode); above it -> a genuinely different photo. Starting point from P08/V6
# (PHASH_HAMMING_MAX=10); to be CALIBRATED against real car photos before relied upon (ASSUMED).
PHASH_HAMMING_MAX = 10

try:  # Pillow >=10 moved resampling constants; keep a backward-compatible alias.
    _RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:  # pragma: no cover - old Pillow
    _RESAMPLE = Image.LANCZOS


@dataclass(frozen=True)
class PhotoHash:
    phash: str          # 16-char hex (64-bit pHash)
    quality: float      # AC-energy proxy (>=0); higher = more visual features, ~0 = featureless
    content_hash: str   # blake2b hex of the raw bytes (cache key; skip re-hashing identical bytes)


def _dct2(values: np.ndarray) -> np.ndarray:
    """2D type-II orthonormal DCT (separable)."""
    return dct(dct(values, axis=0, norm="ortho"), axis=1, norm="ortho")


def _lowfreq_block(img: "Image.Image") -> np.ndarray:
    """Grayscale -> resize -> 2D DCT -> top-left 8x8 low-frequency coefficient block."""
    gray = img.convert("L").resize((_IMG_SIDE, _IMG_SIDE), _RESAMPLE)
    return _dct2(np.asarray(gray, dtype=np.float64))[:_HASH_SIZE, :_HASH_SIZE]


def _bits_to_hex(bits: np.ndarray) -> str:
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bool(bit))
    return format(value, "016x")


def hash_image_bytes(data: bytes) -> PhotoHash:
    """Pure, offline: raw image bytes -> PhotoHash. Raises on undecodable bytes."""
    with Image.open(BytesIO(data)) as img:
        img.load()
        low = _lowfreq_block(img)
    bits = low > np.median(low)
    ac = low.copy()
    ac[0, 0] = 0.0  # drop DC (overall brightness) so quality measures STRUCTURE, not exposure
    return PhotoHash(
        phash=_bits_to_hex(bits),
        quality=float(np.std(ac)),
        content_hash=hashlib.blake2b(data, digest_size=16).hexdigest(),
    )


def hamming(phash_a: str, phash_b: str) -> int:
    """Hamming distance between two 64-bit hex pHashes."""
    return bin(int(phash_a, 16) ^ int(phash_b, 16)).count("1")


def same_photo(phash_a: str, phash_b: str, max_distance: int = PHASH_HAMMING_MAX) -> bool:
    """True when two pHashes are the SAME image within the recompression tolerance."""
    return hamming(phash_a, phash_b) <= max_distance


def download_and_hash(
    url: str,
    *,
    fetch: Callable[[str], bytes | None],
    cache: dict | None = None,
) -> PhotoHash | None:
    """Fetch (via the injected governor-wrapped `fetch`) then perceptual-hash a photo URL.

    `cache` (optional dict keyed by the bytes content-hash) skips RE-HASHING byte-identical
    downloads -- e.g. the same stock photo reused across listings. Returns None when the fetch
    yields no bytes. This function never opens a socket itself; the egress stays gated in `fetch`.
    (URL-level download dedup is an upstream concern of the governor / clearance cache.)
    """
    data = fetch(url)
    if not data:
        return None
    key = hashlib.blake2b(data, digest_size=16).hexdigest()
    if cache is not None and key in cache:
        return cache[key]
    result = hash_image_bytes(data)
    if cache is not None:
        cache[key] = result
    return result
