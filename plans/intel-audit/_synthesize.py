#!/usr/bin/env python3
"""Sintesis local de AUDITS.json -> MATRIX.md + PLACEMENT-MAP.md + CARDEEP-OFFERING.md.
Sin agentes (no consume cap). Re-ejecutable: al merge de las 109 se vuelve a correr."""
import json, re, collections, os
BASE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(BASE, "AUDITS.json"), encoding="utf-8"))
N = len(A)
def nf(s):
    s = (s or '').lower()
    s = re.sub(r'\[.*?\]', '', s); s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'[^a-z0-9%/&+. -]', ' ', s); s = re.sub(r'\s+', ' ', s).strip(' .-/')
    return s
# --- taxonomia canonica de metricas del sector (dominio) ---
CANON = [
 ("Valor residual % (RV%)", r"residual.*%|rv ?%|%.*residual|residual.*perc|valor residual.*%"),
 ("Valor residual — forecast", r"residual.*(forecast|future|prevision|prognos)|forecast.*residual|rv forecast|future.*residual|valor.*futuro"),
 ("Valor residual (abs)", r"residual value|valor residual|restwert|residualwert"),
 ("Trade / wholesale value", r"trade.?(value|price|in)|wholesale value|valor mayorista|precio de compra|ankauf|buy.?price"),
 ("Retail / private value", r"retail (value|price)|private (value|price)|precio de venta|verkaufspreis|particular|valor de venta"),
 ("List price (nuevo)", r"list price|new.?price|precio nuevo|neupreis|msrp|pvp|precio de cat|precio lista|sticker price"),
 ("Precio de mercado en vivo", r"advertised|asking price|listing price|live retail|precio anunciado|market price|precio de mercado|average advert"),
 ("Histórico / índice de precio", r"price history|historico de precio|price trend|tendencia de precio|price index|indice de precio|weekly price"),
 ("Ajuste por km", r"mileage.?adjust|km.?adjust|ajuste.*(km|kilometr|mileage)|adjusted.*mileage|mileage band"),
 ("Depreciación", r"depreciat|depreciaci|amortizaci|wertverlust"),
 ("Días en stock / time-to-sell", r"days.?to.?sell|time.?to.?sale|days on market|market days supply|stock duration|dias.*(venta|stock)|tiempo.*venta|rotaci|sell.?through|velocity|days.?supply"),
 ("Price-to-market / posición", r"price.?to.?market|price position|market position|pricing premium|vs market|posici.*precio|competitiv.*pric|competitor.?pric|price.?benchmark|deal rating|price rating"),
 ("Índice de demanda", r"demand|demanda|search volume|busqueda|popularity|interest level|consumer interest"),
 ("Oferta / inventario (volumen)", r"supply|inventory|stock (volume|level|count)|oferta|listings? count|n.*listings|parque|market volume"),
 ("Ventas / matriculaciones", r"sales (volume|by|data)|registration|matriculaci|new.?car.?sales|ventas|zulassung|units sold"),
 ("Cuota de mercado", r"market share|cuota de mercado|share of"),
 ("VIN", r"\bvin\b|vehicle identification|bastidor|fahrgestell|chassis (no|number)"),
 ("Matrícula (VRM)", r"\bvrm\b|\bvrn\b|registration (mark|number|plate)|matricula|number plate|kennzeichen|license plate"),
 ("Marca", r"\bmake\b|\bbrand\b|marca|hersteller|fabricante"),
 ("Modelo", r"\bmodel\b|modelo|modell"),
 ("Versión / trim", r"\btrim\b|version|variant|\bgrade\b|acabado|equipment level|ausstattungslinie|spec.*level"),
 ("Carrocería / segmento", r"body (type|style)|carrocer|karosserie|segment|segmento"),
 ("Año / fecha", r"\byear\b|build (year|date)|model year|\bano\b|\baño\b|baujahr|registration date|fecha.*matric|first reg"),
 ("Motor / potencia", r"engine|\bpower\b|\bkw\b|\bhp\b|\bcv\b|caballos|cilindrada|displacement|\bmotor\b|leistung|\bps\b|horsepower"),
 ("Combustible", r"fuel type|combustible|kraftstoff|petrol|diesel|gasolina|powertrain|propuls|energy type"),
 ("Transmisión", r"transmission|gearbox|cambio|caja de cambios|getriebe|automatic|\bmanual\b"),
 ("Tracción", r"drivetrain|drive type|traccion|antrieb|4x4|\bawd\b|\bfwd\b|\brwd\b|4wd"),
 ("Dimensiones / peso", r"dimension|\blength\b|\bwidth\b|\bheight\b|\bweight\b|\bpeso\b|curb weight|medidas|gewicht|abmess"),
 ("Color", r"colou?r|farbe"),
 ("CO2 / emisiones", r"\bco2\b|emission|emision|\bnox\b|euro ?\d"),
 ("Consumo / eficiencia", r"consumption|consumo|efficiency|verbrauch|\bmpg\b|l/100|fuel economy"),
 ("Autonomía EV", r"\brange\b|autonomia|reichweite|wltp range|electric range"),
 ("Batería EV", r"battery|bateria|\bkwh\b|cathode|state of health|\bsoh\b|cell (type|chem)"),
 ("Carga EV", r"charging|recarga|ladezeit|connector type|charge time|charging time"),
 ("Equipamiento de serie", r"standard equipment|serienausstattung|equipamiento de serie|standard feature"),
 ("Equipamiento opcional", r"option|optional|\bextra\b|sonderausstattung|equipamiento opcional|paquete|package|factory.?fitted"),
 ("Componentes / piezas", r"component|part (number|price|catalog|data)|despiece|\bpieza\b|ersatzteil|tecdoc|oem part|spare part"),
 ("Specs (ficha técnica)", r"\bspec(s|ification)?\b|ficha tecnica|technical data|datos tecnicos|\battribute"),
 ("Kilometraje / odómetro", r"mileage|odometer|kilometr|\bkm\b|laufleistung|kilometraje"),
 ("Historial de siniestros", r"accident|damage|siniestro|crash|collision|unfall|\bdaño|write.?off|salvage|total loss|scrapped"),
 ("Nº de propietarios", r"\bowner|propietario|\bhalter\b|\bkeeper\b|titular"),
 ("Check de robo", r"stolen|\brobo\b|theft|robado|gestohlen"),
 ("Carga financiera / prenda", r"finance|outstanding|prenda|carga financiera|reserva de dominio|\bhpi\b|embargo|lien"),
 ("ITV / MOT / inspección", r"\bmot\b|\bitv\b|inspection|inspecci|\btuv\b|hauptunters|technical inspection|revision tecnica"),
 ("Recall / campaña", r"recall|llamada a revision|rückruf|safety campaign"),
 ("Historial de servicio", r"service history|maintenance history|historial de mantenimiento|scheckheft|service record"),
 ("Import / export", r"\bimport|\bexport|importaci"),
 ("TCO (coste total)", r"\btco\b|total cost of ownership|coste total|cost of ownership|gesamtkosten"),
 ("Impuesto / matriculación", r"\btax\b|road tax|impuesto|registration cost|steuer|circulaci"),
 ("Coste mantenimiento / SMR", r"maintenance cost|\bsmr\b|servicing cost|coste de mantenimiento|wartungskosten|labour (time|rate)|paint (time|cost)|repair cost"),
 ("Seguro (coste/grupo)", r"insurance|seguro|versicherung|insurance group"),
 ("Coste por km / mensual", r"cost per (km|mile)|monthly cost|coste mensual|per km|cuota mensual|leasing rate|lease price"),
 ("Geolocalización / región", r"region|provincia|location|postcode|codigo postal|geo|zone|area|plz"),
 ("Concesionario / vendedor", r"dealer|concesionario|seller|vendedor|haendler|trader"),
]
CANON_C = [(c, re.compile(p)) for c, p in CANON]
def canonize(k):
    for c, rx in CANON_C:
        if rx.search(k): return c
    return None
# --- catalogo de campos (canonicalizado) ---
field_co = collections.defaultdict(set); field_ex = {}; raw_unmatched = collections.defaultdict(set)
for a in A:
    nm = a.get("name", "?")
    for f in (a.get("all_fields") or []):
        k = nf(f)
        if len(k) < 3: continue
        c = canonize(k)
        if c:
            field_co[c].add(nm); field_ex[c] = c
        else:
            field_co[k].add(nm); field_ex.setdefault(k, f.strip()); raw_unmatched[k].add(nm)
cat = sorted(field_co.items(), key=lambda kv: (-len(kv[1]), kv[0]))
# --- placement ---
plc = collections.defaultdict(list)
for a in A:
    for p in (a.get("placement") or []):
        d = nf(p.get("datum", ""))
        if d: plc[d].append((a.get("name", "?"), p.get("where", "")))
plc_sorted = sorted(plc.items(), key=lambda kv: -len(kv[1]))
# --- gaps / diferenciales ---
gaps = [(a.get("name"), g) for a in A for g in (a.get("differentials") and [] or []) ]  # placeholder
gaps = [(a.get("name"), g) for a in A for g in (a.get("gaps") or [])]
diffs = [(a.get("name"), d) for a in A for d in (a.get("differentials") or [])]
by_sub = collections.Counter(a.get("subdomain", "?") for a in A)
TS = max(2, round(N * 0.35))  # umbral table-stakes

def w(fn, s): open(os.path.join(BASE, fn), "w", encoding="utf-8").write(s)

# ===== MATRIX.md =====
m = [f"# Catálogo de campos × cobertura (matriz)\n",
     f"> Derivado de **{N}** auditorías. {len(cat)} campos atómicos únicos (normalizados, pre-canonicalización).",
     f"> Subdominios: " + ", ".join(f"{k} {v}" for k, v in by_sub.most_common()) + "\n",
     f"## Table-stakes (≥{TS}/{N} empresas) — cardeep DEBE tenerlos\n",
     "| Campo | nº | Empresas (muestra) |", "|---|---|---|"]
for k, co in cat:
    if len(co) >= TS:
        m.append(f"| {field_ex.get(k,k)} | {len(co)} | {', '.join(sorted(co)[:6])} |")
m += ["\n## Diferenciadores / nicho (≤2 empresas) — oportunidad para cardeep\n",
      "| Campo | nº | Empresa(s) |", "|---|---|---|"]
for k, co in cat:
    if len(co) <= 2:
        m.append(f"| {field_ex.get(k,k)} | {len(co)} | {', '.join(sorted(co))} |")
m += ["\n## Catálogo completo (todos los campos, por frecuencia)\n", "| Campo | nº |", "|---|---|"]
for k, co in cat:
    m.append(f"| {field_ex.get(k,k)} | {len(co)} |")
w("MATRIX.md", "\n".join(m))

# ===== PLACEMENT-MAP.md =====
p = [f"# Mapa de colocación — dónde poner cada dato en cardeep\n",
     f"> Patrón derivado de DÓNDE {N} empresas sitúan cada métrica en su UI. Agrupado por dato (frecuencia).\n"]
for d, lst in plc_sorted:
    p.append(f"### {d}  ·  ({len(lst)} empresas lo colocan)")
    for co, where in lst[:8]:
        p.append(f"- **{co}**: {where}")
    p.append("")
w("PLACEMENT-MAP.md", "\n".join(p))

# ===== CARDEEP-OFFERING.md =====
o = [f"# Qué vende cardeep — síntesis de la oferta (borrador {N}/109)\n",
     "> Construido desde el catálogo de campos + gaps + diferenciales de las auditorías. "
     "El edge estructural de cardeep: censo VIVO 100% del territorio, delta+historial, verificación "
     "multi-fuente (VAM), cross-platform — capacidades que la mayoría NO tiene.\n",
     "## 1. Núcleo obligatorio (table-stakes del sector)",
     "Los campos que ofrece la mayoría; cardeep los necesita para competir:\n"]
o += [f"- {field_ex.get(k,k)}  _({len(co)}/{N})_" for k, co in cat if len(co) >= TS]
o += ["\n## 2. Diferenciadores explotables (pocos los ofrecen)",
      "Campos raros = si cardeep los da, gana ventaja:\n"]
o += [f"- {field_ex.get(k,k)}  _({', '.join(sorted(co))})_" for k, co in cat if len(co) <= 2][:120]
o += ["\n## 3. Gaps declarados por las empresas (lo que NO hacen) → terreno de cardeep\n"]
o += [f"- _{n}_: {g}" for n, g in gaps][:150]
o += ["\n## 4. Diferenciales que cada empresa presume (para igualar/superar)\n"]
o += [f"- _{n}_: {d}" for n, d in diffs][:150]
w("_offering_data.md", "\n".join(o))  # data pool; la narrativa institucional vive en CARDEEP-OFFERING.md (escrita a mano)

print(f"sintetizado N={N} | campos unicos={len(cat)} | table-stakes(>={TS})={sum(1 for _,c in cat if len(c)>=TS)} | nicho(<=2)={sum(1 for _,c in cat if len(c)<=2)} | placement-data={len(plc_sorted)} | gaps={len(gaps)} | diffs={len(diffs)}")
print("escritos: MATRIX.md, PLACEMENT-MAP.md, CARDEEP-OFFERING.md")
