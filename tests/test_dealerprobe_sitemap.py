"""DealerProbe — generic €0 own-site auto-harvester: sitemap classifier (the king signal).

The recon workflow (wf_3fb0d564, 90 live-probed dealer sites) found that ~80% of detectable
dealers expose per-vehicle URLs through a dedicated sitemap, with a small, recurring set of
sitemap names and per-vehicle URL shapes. These pure classifiers turn that observation into
deterministic rules — no per-dealer REGISTRY, no JS. Tests are the real shapes seen live.
"""
import pytest

from pipeline.platform.dealerprobe import classify_loc, is_vehicle_sitemap

pytestmark = pytest.mark.unit


# --- is_vehicle_sitemap: does this child-sitemap name carry CARS? -----------------------------
@pytest.mark.parametrize("name", [
    "vehica_car-sitemap.xml",          # Vehica WP plugin (most common WP car fingerprint)
    "stock_listing_0-sitemap.xml",     # DealerK / MotorK
    "auto_usate_0-sitemap.xml",        # DealerK / MotorK (used)
    "auto_nuove_0-sitemap.xml",        # DealerK / MotorK (new)
    "sitemap.vehicles.xml",            # custom (automotordursan)
    "vehiculos.xml",                   # custom
    "coches-sitemap.xml",              # Yoast/RankMath custom post-type
    "product-sitemap.xml",             # WooCommerce (cars as products)
    "https://x.es/wp-sitemap-posts-listings-1.xml",  # WP custom post-type 'listings' (autosantpedor)
    "inventario-sitemap.xml",
])
def test_vehicle_sitemap_names_detected(name):
    assert is_vehicle_sitemap(name) is True


@pytest.mark.parametrize("name", [
    "wp-sitemap-posts-page-1.xml",     # WP pages — NOT cars
    "post-sitemap.xml",                # blog posts
    "category-sitemap.xml",
    "page-sitemap.xml",
    "author-sitemap.xml",
    "https://x.es/sitemap_index.xml",  # the index itself, not a leaf of cars
])
def test_non_vehicle_sitemap_names_rejected(name):
    assert is_vehicle_sitemap(name) is False


# --- classify_loc: is a <loc> a single car, a category/listing, or other? ---------------------
@pytest.mark.parametrize("url", [
    "https://x.es/buy/3f2a9c1e-1b2c-4d5e-8f90-abcdef123456",                  # DealCar.io Next /buy/<uuid>
    "https://x.es/coches-segunda-mano/bmw/x5/3-0d-xdrive-2019-90000-17769",   # custom per-version
    "https://x.es/vehiculos/audi-a4-2-0-tdi-2018",                            # slug make-model-spec
    "https://x.es/Vehiculos/nissan-qashqai/",                                 # WP custom post-type detail
    "https://x.es/detalles.php?vehiculo=12345-v-bmw-serie-3",                 # legacy php detail
    "https://x.es/coches/nuevos/opel/corsa/5-puertas/2024/",                  # DealerK per-config
    "https://x.es/producto/seat-leon-fr-2021-45000km",                        # Woo product = a car
    "https://x.es/listado/12345/audi-a3",                                     # id + slug
])
def test_per_vehicle_urls(url):
    assert classify_loc(url) == "per_vehicle"


@pytest.mark.parametrize("url", [
    "https://x.es/coches-segunda-mano/bmw",        # brand listing (no model/unit)
    "https://x.es/coches-ocasion/",                # ocasion listing root
    "https://x.es/vehiculos/",                     # listing root
    "https://x.es/coches-segunda-mano/elche",      # city listing (ocasionplus)
    "https://x.es/stock/",
])
def test_category_urls(url):
    assert classify_loc(url) == "category"


@pytest.mark.parametrize("url", [
    "https://x.es/contacto",
    "https://x.es/blog/como-comprar-coche-segunda-mano",
    "https://x.es/quienes-somos",
    "https://x.es/aviso-legal",
    "https://x.es/",
])
def test_other_urls(url):
    assert classify_loc(url) == "other"
