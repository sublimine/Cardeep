from scripts.associations.parse_aecs import parse_dealers


def test_parse_dealers_from_external_capture() -> None:
    source = """
    <section class="elementor-widget-text-editor">
      <div class="elementor-widget-container">Dealer &amp; Uno</div>
    </section>
    <section class="elementor-widget-text-editor">
      <div class="elementor-widget-container">MADRID</div>
    </section>
    <a class="elementor-button primary" href="https://dealer.example">Visitar</a>
    """

    assert parse_dealers(source) == [
        {
            "name": "Dealer & Uno",
            "province": "MADRID",
            "website": "https://dealer.example",
        }
    ]
