# Cardeep — content bible for the public site

Single source of truth for every word, figure and asset on `cardeep.vercel.app`.
Sections keep the reference layout, motion and component anatomy exactly; only the
content and the surface material change.

---

## 1. Who is reading

Independent used-car dealers, compraventas and small dealer groups in Spain.
They price by instinct, chase stock across half a dozen portals, and find out a
competitor dropped a price when the car is already gone.

They do not care how the data is produced. They care about **seeing the whole
market before everyone else does**.

## 2. Voice

- Spanish (Spain). Direct, confident, warm. Short sentences.
- Sell the outcome, never the plumbing.
- One idea per line. No stacked adjectives. No exclamation marks.
- Concrete beats clever: "1,5 millones de coches" beats "datos masivos".

### Banned vocabulary — internal words the reader has never heard

| Never write | Say instead |
|---|---|
| delta | cada movimiento · qué cambió · altas y bajas |
| VAM · quórum · provenance | contrastado · verificado por varias vías |
| receta · adapter · scraper | — (never surfaces) |
| Tier-1 · long-tail | plataformas · portales |
| censo · entity · cdp_code | índice · punto de venta · ficha |
| servable · canonical · dedup | disponible · ficha única |
| endpoint · payload · schema | (only inside the API section, where it is the audience's language) |

## 3. Figures — only these, nothing invented

Computed by `services/api/stats.py` against the live index. The dealer count is
the **honest** definition the owner enforced (a resolved, non-private,
non-scrapyard point of sale with at least one available car) — not the inflated
~54.6k that counted empty records.

| Figure | Value | Where it may appear |
|---|---|---|
| Puntos de venta activos | **+19.000** | hero band, scaling counter |
| Coches vivos en el índice | **1,5 M** | stats band |
| Provincias cubiertas | **52** | stats band, coverage card |
| Municipios | **+8.000** | coverage card |
| Plataformas indexadas | **7** | source wall |

Every screen that shows a figure carries the stamp **"Índice actualizado · julio 2026"**.
Nothing is presented as a live counter, because the public site does not talk to
the API yet.

### Per-province figures in the artwork

`tools/mockups/build-map.mjs` reads the real territorial research in
`docs/research/territorial/coverage_province.json`. That file counts **every**
discovered record, including empty ones and scrapyards — the inflated definition
the owner rejected (33.611 nationally). The generator therefore keeps the real
*relative distribution* between provinces and normalises it to the published
19.048, so no screen contradicts another. Provinces whose real `covB` (our count
against INE's official register of vehicle-sales businesses) is under 0.8 are
marked amber as still being widened — 19 of 53 today.

### Never fabricate

No invented customer logos, testimonials, ratings, case studies or headshots.
Where the reference template used social proof we do not have, the slot is
re-cast as a truthful statement of capability, keeping the same visual shape.

## 4. The seven platforms indexed

coches.net · AutoScout24 · Wallapop · Milanuncios · Autocasión · coches.com · motor.es

Framing: **"Indexamos donde vive el mercado"** — not "clientes", not "partners".

## 5. What Cardeep offers (product surfaces)

Derived from the real API. Each becomes a card with its own UI spoiler.

| Surface | One-line promise | Proof detail |
|---|---|---|
| **Índice nacional** | Cada punto de venta de España y todo su stock. | Ficha por dealer, inventario completo, código único |
| **Precio real** | El precio al que se vende de verdad, no una estimación. | Distribución completa del mercado, tu posición dentro |
| **Cobertura** | Provincia, comarca y municipio. Sin puntos ciegos. | 52 provincias · +8.000 municipios · demanda por zona |
| **Historial** | La vida entera de un coche, desde que apareció. | Altas, bajas, cada cambio de precio y de foto |
| **Oportunidades** | Los coches que valen menos de lo que valen. | Puntuación por anuncio, margen, zona y segmento |
| **Terminal** | El mercado como un mercado. | Curva por modelo, screener, señal de venta |
| **Publicación** | Un stock, todos los portales. | Publicación y auditoría de tus anuncios |
| **Encargos** | Demanda real de compradores, en abierto. | Peticiones activas y coches que encajan |

## 6. Section-by-section content map

### Navbar
`Índice` · `Producto` · `Precios` · `API` — CTA **"Pedir acceso"**.

### Hero
- Badge → `Cardeep` / `Índice nacional en vivo` (links to `#indice`)
- H1 → **El mercado del coche en España, entero y en vivo.**
- Sub → **Cada punto de venta, cada coche, cada movimiento de precio. Sin muestras ni estimaciones: el mercado real, actualizado mientras lo miras.**
- CTA → **Pedir acceso**
- Watermark → `Cardeep`

### Source wall (was "Trusted by fast-growing startups")
Kicker: **Indexamos donde vive el mercado**. The seven platform wordmarks.

### Bento (was "Replace your Engineering Team")
Heading: **Deja de mirar el mercado por una rendija**
- Big card: **Índice nacional** — "Cada compraventa, cada concesionario, cada garaje de pueblo. Con su stock entero y su ficha." CTA "Ver el índice".
- **Movimientos del mercado** — the notification stack, re-cast as live market events (bajada de precio, coche vendido, stock nuevo).
- **Cobertura de España** — the dotted map, re-cast as sales points over Spain.
- **Precio real** — the search card, re-cast as a price-position readout.
- **Y todo lo demás** — encargos, publicación, terminal.

### Projects → **"Lo que hay dentro"**
Six product surfaces, each with a real UI spoiler image (see §7).

### Insights carousel → **"Un índice que no se cae"**
Five capability cards (the same card shape, no fake people): cobertura verificada,
contraste por varias vías, historial íntegro, alertas de origen, API abierta.

### Scaling → **Construido para el mercado español**
Counter **19.000+ puntos de venta**, the coverage mosaic, the seven sources.

### Comparison → **Cardeep frente a mirar portales a mano**
Rows: alcance, precio, historial, oportunidades, publicación, tiempo, decisión.

### Pricing (real plans, recovered from the product)
- **Starter — 0 €**: el CRM completo del dealer y la ficha del vehículo.
- **Scale — 249 €/mes** (199 € anual): precio real de mercado, movimientos en vivo, micro-geo, historial completo.
- **Enterprise — a medida**: oportunidades, alertas, API y cuenta dedicada.

### Founder's desk → **La misión**
The real mission, first person, no invented biography: build the complete, living
map of a market nobody has whole.

### Feedback carousel → **Cómo trabajamos** (five principles, black cards)
Ningún número sin contrastar · El mercado entero, no una muestra · Historial que no
se borra · Si algo falla, lo sabes · Tus datos son tuyos.

### FAQ — eight real dealer questions
See `src/content/site.ts` for the final strings.

### Footer
Real columns, real anchors, `hola@cardeep.es`, © Cardeep.

## 7. Multimedia — all bespoke, all free

No stock photography and no AI-generated imagery (it garbles interface text and
the owner's rule is zero spend). Everything is authored:

1. **UI spoilers** — real Cardeep interfaces built as HTML/CSS in
   `tools/mockups/`, rendered headless at 2x and exported to `public/shots/*.webp`.
   Crisp, on-brand, real text, and they genuinely show what is inside.
2. **Coverage artwork** — Spain drawn from the same dot matrix the reference used,
   re-plotted so the dots trace the peninsula and the sales points sit on real cities.
3. **Source wordmarks** — typographic SVG marks, one consistent family.
4. **Hero atmosphere** — the existing vector light-arc kept; it already reads as a
   horizon coming into view, which is the product's promise.
5. **Brand mark** — `src/components/ui/logo.tsx`. A "C" drawn as a 5x5 dot matrix,
   with one accent dot. It shares a language with the dot arrow inside every CTA
   and the dotted map of Spain, and being a grid it stays legible at 16px.
   `public/shots/mark.webp` is the same matrix rendered dark on the accent yellow,
   used as the portrait the CTA reveals on hover — where the template showed a
   founder's face, Cardeep shows its own mark.

## 8. Glassmorphism

Structure, spacing and motion stay exactly as they are. Only the material changes:

- Surfaces become translucent: `background: rgba(255,255,255,0.55)` over the warm
  page, `rgba(255,255,255,0.06)` over dark sections.
- `backdrop-filter: blur(20px) saturate(160%)`.
- Hairline borders `rgba(255,255,255,0.6)` on light, `rgba(255,255,255,0.10)` on dark.
- One soft inner top highlight per panel, never a heavy shadow.
- Accent stays the reference yellow `#fc0`; Cardeep blue `#2563eb` is the single
  supporting hue for data and links.
- Contrast is never traded for translucency: body text keeps AA.
