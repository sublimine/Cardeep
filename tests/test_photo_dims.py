"""Pure/offline tests for pipeline/marketing/photo_dims.py's ``image_dimensions``.
The network leg (``fetch_photo_dimensions``) is exercised only by the production job
and its own manual verification pass (07-marketing.md S7 protocol row 2) — this suite
never touches the network, per the pure/offline-testable split the module documents.
"""
from __future__ import annotations

from io import BytesIO

import pytest

from pipeline.marketing.photo_dims import MAX_BYTES, PhotoFetchError, image_dimensions


def _make_png_bytes(width: int, height: int) -> bytes:
    from PIL import Image

    buf = BytesIO()
    Image.new("RGB", (width, height), color=(120, 130, 140)).save(buf, format="PNG")
    return buf.getvalue()


class TestImageDimensions:
    def test_reads_exact_dimensions(self):
        data = _make_png_bytes(1024, 768)
        assert image_dimensions(data) == (1024, 768)

    def test_reads_small_dimensions(self):
        data = _make_png_bytes(320, 240)
        assert image_dimensions(data) == (320, 240)

    def test_undecodable_bytes_raise_photo_fetch_error(self):
        with pytest.raises(PhotoFetchError):
            image_dimensions(b"not an image, just garbage bytes")

    def test_empty_bytes_raise_photo_fetch_error(self):
        with pytest.raises(PhotoFetchError):
            image_dimensions(b"")


class TestConstants:
    def test_max_bytes_is_sane(self):
        assert MAX_BYTES == 8 * 1024 * 1024
