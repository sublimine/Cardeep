#!/usr/bin/env python3
"""Strip Claude Design Components (.dc.html) into dependency-free standalone .html.

Reads every  portal/_build/src/<Name>.dc.html  and writes  portal/<name>.html .

A .dc.html is: <x-dc>  <helmet>…fonts/style…</helmet>  <div id=cd-root>…markup…</div>  </x-dc>
followed by  <script type="text/x-dc" data-dc-script> class Component extends DCLogic {…} </script>.
The claude.ai/design host mounts it via support.js + window.React. Those globals are absent
standalone, but the screen body is pure DOM (React adds nothing), so we:
  - <helmet> inner            -> <head>
  - <x-dc> inner (minus helmet) -> <body>
  - the DCLogic subclass kept VERBATIM but made executable: a DCLogic stub is defined first,
    then the class runs on DOMContentLoaded via `new Component().componentDidMount()`.
  - inter-screen links  "X.dc.html" -> "x.html".
No React, no support.js, no claude.ai coupling. Deterministic — no hand transcription.
"""
import re
from pathlib import Path

BUILD = Path(__file__).resolve().parent      # portal/_build
SRC   = BUILD / "src"
OUT   = BUILD.parent                          # portal/

# Claude Design stem -> (output stem, page <title>)
NAME_MAP = {
    "Cardeep - Landing": ("index",        "cardeep · El mercado entero, en un índice vivo"),
    "Analitica":         ("analitica",    "Analítica · cardeep"),
    "Dashboard":         ("dashboard",    "Resumen · cardeep"),
    "Dealers":           ("dealers",      "Dealers · cardeep"),
    "Dossier":           ("dossier",      "Dossier · cardeep"),
    "Finanzas":          ("finanzas",     "Finanzas · cardeep"),
    "Garaje":            ("garaje",       "Garaje 360° · cardeep"),
    "Inteligencia":      ("inteligencia", "Inteligencia · cardeep"),
    "Marketplace":       ("marketplace",  "Marketplace · cardeep"),
    "Plano":             ("plano",        "Plano 3D · cardeep"),
}
HREF_MAP = {f"{src}.dc.html": f"{dst}.html" for src, (dst, _t) in NAME_MAP.items()}
# Some screens link to the landing with an EM DASH ("Cardeep — Landing.dc.html") while the
# real file uses a hyphen. Map the em-dash variant to index.html too.
HREF_MAP["Cardeep — Landing.dc.html"] = "index.html"

TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link rel="icon" href="assets/cd-icon.png">
__HELMET__
</head>
<body>
<!-- Ported from Claude Design "__SRC__.dc.html" by _build/strip_dc.py.
     Standalone: no React, no support.js. The DCLogic class runs on DOMContentLoaded. -->
__BODY__
__SCRIPTS__
</body>
</html>
"""


def strip(text, src_stem, title):
    xdc = re.search(r"<x-dc(?:\s[^>]*)?>(.*)</x-dc>", text, re.S)
    if not xdc:
        raise ValueError(f"{src_stem}: no <x-dc> block found")
    inner = xdc.group(1)

    helmet_inner = ""
    hm = re.search(r"<helmet>(.*?)</helmet>", inner, re.S)
    if hm:
        helmet_inner = hm.group(1).strip()
        inner = inner[:hm.start()] + inner[hm.end():]
    body_inner = inner.strip()

    dc_js = ""
    sm = re.search(r'<script[^>]*\bdata-dc-script\b[^>]*>(.*?)</script>', text, re.S)
    if sm:
        dc_js = sm.group(1).strip()

    if dc_js:
        scripts = (
            '<script>class DCLogic{constructor(){}renderVals(){return {};}}</script>\n'
            '<script>\n' + dc_js + '\n</script>\n'
            '<script>document.addEventListener("DOMContentLoaded",function(){'
            'try{new Component().componentDidMount();}'
            'catch(e){console.error("[cardeep portal] init error:",e);}});</script>'
        )
    else:
        scripts = '<!-- static screen: no DC script -->'
    doc = (TEMPLATE
           .replace("__TITLE__", title)
           .replace("__HELMET__", helmet_inner)
           .replace("__SRC__", src_stem)
           .replace("__BODY__", body_inner)
           .replace("__SCRIPTS__", scripts))
    for a, b in HREF_MAP.items():
        doc = doc.replace(a, b)
    return doc


def main():
    if not SRC.is_dir():
        raise SystemExit(f"no src dir: {SRC}")
    done = []
    for f in sorted(SRC.glob("*.dc.html")):
        stem = f.name[:-len(".dc.html")]
        if stem not in NAME_MAP:
            print(f"SKIP (unknown): {f.name}")
            continue
        dst_stem, title = NAME_MAP[stem]
        out = OUT / f"{dst_stem}.html"
        out.write_text(strip(f.read_text(encoding="utf-8"), stem, title), encoding="utf-8")
        done.append(f"{f.name} -> {out.name}")
    print("STRIPPED:")
    for d in done:
        print("  " + d)
    if not done:
        print("  (nothing — put <Name>.dc.html files in _build/src/)")


if __name__ == "__main__":
    main()
