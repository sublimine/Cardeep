"""DealerProbe component 4a — async sitemap frontier (the king path: robots -> sitemap_index ->
car sitemaps -> per-vehicle URL frontier). Tested with an injected fake fetch (no network):
the fetch is a plain async (url)->str|None, so the cascade is fully unit-testable offline.
"""
import asyncio

import pytest

from pipeline.platform.dealerprobe_wholesale import probe_sitemap_frontier

pytestmark = pytest.mark.unit


def _run(coro):
    return asyncio.run(coro)


# robots -> sitemap_index -> (vehica_car-sitemap kept, page-sitemap dropped) -> per-vehicle locs
PAGES = {
    "https://x.es/robots.txt": "User-agent: *\nAllow: /\nSitemap: https://x.es/sitemap_index.xml\n",
    "https://x.es/sitemap_index.xml": """<?xml version="1.0"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <sitemap><loc>https://x.es/wp-sitemap-posts-page-1.xml</loc></sitemap>
          <sitemap><loc>https://x.es/vehica_car-sitemap.xml</loc></sitemap>
        </sitemapindex>""",
    "https://x.es/vehica_car-sitemap.xml": """<?xml version="1.0"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://x.es/coches/bmw-x5-2019-90000-101</loc></url>
          <url><loc>https://x.es/coches/audi-a4-2018-60000-102</loc></url>
          <url><loc>https://x.es/coches-ocasion/</loc></url>
          <url><loc>https://x.es/contacto</loc></url>
        </urlset>""",
    # the page sitemap MUST NOT be fetched/used; if it were, these would pollute the frontier
    "https://x.es/wp-sitemap-posts-page-1.xml": """<urlset><url><loc>https://x.es/quienes-somos</loc></url></urlset>""",
}


def test_frontier_follows_robots_then_index_to_car_sitemap():
    fr = _run(probe_sitemap_frontier(lambda u: _async(PAGES.get(u)), "x.es"))
    assert set(fr) == {
        "https://x.es/coches/bmw-x5-2019-90000-101",
        "https://x.es/coches/audi-a4-2018-60000-102",
    }
    # category/other locs excluded; page-sitemap never contributed
    assert not any("quienes-somos" in u or "contacto" in u or u.endswith("/coches-ocasion/") for u in fr)


def test_frontier_fallback_when_no_robots():
    pages = {
        "https://y.es/sitemap.xml": """<urlset><url><loc>https://y.es/vehiculos/seat-leon-2020-111</loc></url>
            <url><loc>https://y.es/blog/post</loc></url></urlset>""",
    }
    fr = _run(probe_sitemap_frontier(lambda u: _async(pages.get(u)), "y.es"))
    assert fr == ["https://y.es/vehiculos/seat-leon-2020-111"]


def test_frontier_cap_respected():
    locs = "".join(f"<url><loc>https://z.es/coches/c-{i}-2020-{i}{i}{i}{i}</loc></url>" for i in range(50))
    pages = {"https://z.es/sitemap.xml": f"<urlset>{locs}</urlset>"}
    fr = _run(probe_sitemap_frontier(lambda u: _async(pages.get(u)), "z.es", cap=10))
    assert len(fr) == 10


def test_frontier_empty_when_dead():
    fr = _run(probe_sitemap_frontier(lambda u: _async(None), "dead.es"))
    assert fr == []


async def _async(v):
    return v
