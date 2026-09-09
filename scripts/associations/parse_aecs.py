"""Parse AECS (Stellantis dealers) Elementor page into structured JSON.

Pattern per dealer: text-editor widget (NAME) -> text-editor widget (PROVINCE)
-> button widget (WEBSITE). We walk text-editor contents in order and pair each
name with the following province + the next website button.
"""
from __future__ import annotations

import argparse
import html as _html
import json
import os
import re
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_RAW = Path(ROOT) / "data" / "raw" / "associations" / "aecs.html"
DEFAULT_OUT = Path(ROOT) / "docs" / "research" / "associations" / "aecs_members.json"

PROVINCES = {
    "MADRID", "BARCELONA", "VALENCIA", "SEVILLA", "ZARAGOZA", "MALAGA", "MÁLAGA",
    "MURCIA", "ALICANTE", "CADIZ", "CÁDIZ", "CORDOBA", "CÓRDOBA", "GRANADA",
    "ALMERIA", "ALMERÍA", "JAEN", "JAÉN", "HUELVA", "BADAJOZ", "CACERES", "CÁCERES",
    "TOLEDO", "CIUDAD REAL", "ALBACETE", "CUENCA", "GUADALAJARA", "BURGOS", "LEON",
    "LEÓN", "VALLADOLID", "SALAMANCA", "ZAMORA", "PALENCIA", "AVILA", "ÁVILA",
    "SEGOVIA", "SORIA", "ASTURIAS", "CANTABRIA", "LA RIOJA", "NAVARRA", "ALAVA",
    "ÁLAVA", "GUIPUZCOA", "GUIPÚZCOA", "VIZCAYA", "BIZKAIA", "LA CORUÑA", "CORUÑA",
    "A CORUÑA", "LUGO", "ORENSE", "OURENSE", "PONTEVEDRA", "TARRAGONA", "LLEIDA",
    "LERIDA", "LÉRIDA", "GIRONA", "GERONA", "CASTELLON", "CASTELLÓN", "HUESCA",
    "TERUEL", "BALEARES", "ISLAS BALEARES", "LAS PALMAS", "SANTA CRUZ DE TENERIFE",
    "TENERIFE", "CEUTA", "MELILLA", "GIPUZKOA",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse an externally captured AECS directory page."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_RAW,
        help="Raw HTML input (default: ignored data/raw/associations/aecs.html)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT,
        help="Structured JSON output",
    )
    return parser.parse_args()


def parse_dealers(source: str) -> list[dict[str, str]]:
    # Build an ORDERED token stream of two kinds: ('text', value) and ('btn', href).
    # Walk it so a website binds to the dealer it physically follows.
    tokens = []
    for m in re.finditer(
        r'elementor-widget-text-editor[^>]*>\s*<div class="elementor-widget-container">\s*(.*?)\s*</div>'
        r'|class="elementor-button[^"]*"\s+href="([^"]+)"',
        source, re.DOTALL):
        if m.group(1) is not None:
            val = _html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
            if val:
                tokens.append(("text", val))
        elif m.group(2) is not None:
            href = m.group(2)
            if href.startswith("http") and "asociacionstellantis" not in href:
                tokens.append(("btn", href))

    dealers = []
    i = 0
    while i < len(tokens) - 1:
        k0, v0 = tokens[i]
        k1, v1 = tokens[i + 1]
        if (k0 == "text" and k1 == "text" and v1.upper() in PROVINCES
                and v0.upper() not in PROVINCES and len(v0) > 2):
            d = {"name": v0, "province": v1}
            # next token, if a button, is this dealer's website
            if i + 2 < len(tokens) and tokens[i + 2][0] == "btn":
                d["website"] = tokens[i + 2][1]
                i += 3
            else:
                i += 2
            dealers.append(d)
        else:
            i += 1

    return dealers


def main():
    args = parse_args()
    dealers = parse_dealers(args.input.read_text(encoding="utf-8"))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(dealers, f, ensure_ascii=False, indent=1)
    print(f"WROTE {args.output}: {len(dealers)} dealers, {sum(1 for d in dealers if d.get('website'))} with website")
    for d in dealers[:6]:
        print(" ", d)
    print("  ...")
    for d in dealers[-3:]:
        print(" ", d)


if __name__ == "__main__":
    main()
