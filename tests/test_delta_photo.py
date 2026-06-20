"""P08-S1: perceptual photo hash (free DCT pHash on PIL+numpy+scipy; no TF, no new dep).

Exit criterion (plans/P08.md S1): same image / different URL -> same pHash; JPEG recompression
-> Hamming <= threshold; different image -> Hamming > threshold. All OFFLINE (PIL-generated
fixtures, injected fetch). Seeded RNG -> deterministic.
"""
from __future__ import annotations

from io import BytesIO

import numpy as np
import pytest
from PIL import Image

from pipeline.delta_photo import (
    PHASH_HAMMING_MAX,
    PhotoHash,
    download_and_hash,
    hamming,
    hash_image_bytes,
    same_photo,
)


def _rich_png(seed: int) -> bytes:
    """A deterministic 'photo-like' image: low-res seeded noise upscaled to smooth blobs
    (rich low-frequency content -> stable, recompression-robust pHash)."""
    rng = np.random.default_rng(seed)
    base = rng.integers(0, 256, size=(16, 16), dtype=np.uint8)
    img = Image.fromarray(base, "L").resize((256, 256), Image.BICUBIC)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _recompress_jpeg(png_bytes: bytes, quality: int = 30) -> bytes:
    with Image.open(BytesIO(png_bytes)) as im:
        buf = BytesIO()
        im.convert("RGB").save(buf, format="JPEG", quality=quality)
        return buf.getvalue()


def _solid_png(value: int = 128) -> bytes:
    buf = BytesIO()
    Image.new("L", (256, 256), value).save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.unit
def test_same_image_same_phash_deterministic():
    data = _rich_png(7)
    a, b = hash_image_bytes(data), hash_image_bytes(data)
    assert len(a.phash) == 16
    assert a.phash == b.phash
    assert a.content_hash == b.content_hash
    assert hamming(a.phash, b.phash) == 0


@pytest.mark.unit
def test_recompression_is_same_photo_under_threshold():
    png = _rich_png(7)
    h_png = hash_image_bytes(png).phash
    h_jpeg = hash_image_bytes(_recompress_jpeg(png, quality=30)).phash
    d = hamming(h_png, h_jpeg)
    assert d <= PHASH_HAMMING_MAX, f"recompression Hamming {d} > {PHASH_HAMMING_MAX}"
    assert same_photo(h_png, h_jpeg)


@pytest.mark.unit
def test_different_image_exceeds_threshold():
    h1 = hash_image_bytes(_rich_png(7)).phash
    h2 = hash_image_bytes(_rich_png(99)).phash
    d = hamming(h1, h2)
    assert d > PHASH_HAMMING_MAX, f"distinct images Hamming {d} <= {PHASH_HAMMING_MAX}"
    assert not same_photo(h1, h2)


@pytest.mark.unit
def test_quality_separates_featureless_from_rich():
    rich = hash_image_bytes(_rich_png(7)).quality
    solid = hash_image_bytes(_solid_png()).quality
    assert solid < rich          # featureless stock photo scores lower
    assert solid < 1.0           # near-zero AC energy for a flat image


@pytest.mark.unit
def test_download_and_hash_uses_cache_and_injected_fetch():
    png = _rich_png(7)
    calls = {"n": 0}

    def _fetch(url):
        calls["n"] += 1
        return png

    cache: dict = {}
    r1 = download_and_hash("http://x/a.jpg", fetch=_fetch, cache=cache)
    r2 = download_and_hash("http://x/b.jpg", fetch=_fetch, cache=cache)  # diff URL, same bytes
    assert isinstance(r1, PhotoHash) and r1.phash == r2.phash
    assert calls["n"] == 2        # fetch is not URL-cached here (download dedup is upstream)
    assert len(cache) == 1        # identical bytes -> single cached hash (no re-hash)


@pytest.mark.unit
def test_download_and_hash_none_on_empty_fetch():
    assert download_and_hash("http://x/none.jpg", fetch=lambda u: None) is None
