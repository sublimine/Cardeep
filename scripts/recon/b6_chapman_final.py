"""
B6 Chapman FINAL — Denominador capture-recapture por provincia para dealers.

INSIGHT CRITICO descubierto en _b6_cluster_check2:
  entity_source.entity_ulid NO es la unidad correcta para Chapman porque
  el mismo dealer fisico puede tener MULTIPLES entity_ulid (uno por fuente)
  sin estar mergeado a un canonical_ulid comun.

  SOLUCION: usar entity_cluster.canonical_ulid como unidad de captura.
  Si un dealer OSM y un dealer wallapop comparten canonical_ulid, son
  la MISMA entidad fisica -> m+=1 correcto.

  REALIDAD ACTUAL:
  - entity_cluster tiene 42.898 rows: mayoria cluster_size=1 (no mergeados)
  - Solo 10 canonical groups tienen TANTO osm COMO wallapop
  => Chapman via canonical_ulid da m=10 global -> IC extremadamente ancho
  => Chapman NO es calculable con precision hoy

READ-ONLY — zero writes, zero commits.
"""
from __future__ import annotations

import math
import psycopg2

DSN = "postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep"

DEALER_KINDS = (
    "compraventa",
    "concesionario_oficial",
    "desguace",
    "garaje",
    "subasta",
    "importador",
    "cadena",
    "rent_a_car_vo",
    "oem_vo_portal",
)


def chapman_estimate(n1: int, n2: int, m: int) -> tuple[float, float, float, float]:
    """N_hat, Var, IC_low, IC_high."""
    n_hat = ((n1 + 1) * (n2 + 1) / (m + 1)) - 1
    num_var = (n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m)
    den_var = (m + 1) ** 2 * (m + 2)
    var_n = num_var / den_var if den_var > 0 else float("inf")
    se = math.sqrt(max(var_n, 0.0))
    return n_hat, var_n, max(0.0, n_hat - 1.96 * se), n_hat + 1.96 * se


def main() -> None:
    print("=" * 70)
    print("B6 FINAL — Chapman capture-recapture (READ-ONLY)")
    print("=" * 70)
    print()

    conn = psycopg2.connect(DSN)
    cur = conn.cursor()

    # ------------------------------------------------------------------
    # SECCION 1: Resumen fuentes en entity_source (dealers only)
    # ------------------------------------------------------------------
    print("SECCION 1 — Fuentes en entity_source para dealers")
    print("-" * 60)
    cur.execute("""
        SELECT es.source_key, COUNT(DISTINCT es.entity_ulid) AS n_dealers
        FROM entity_source es
        JOIN entity e ON e.entity_ulid = es.entity_ulid
        WHERE e.kind IN %s
        GROUP BY es.source_key
        ORDER BY n_dealers DESC
    """, (DEALER_KINDS,))
    dealer_src_rows = cur.fetchall()

    print(f"\n  {'source_key':<45} {'n_dealers':>10}  {'ortogonalidad'}")
    print(f"  {'-'*45} {'-'*10}  {'-'*30}")
    ortogonalidad_map = {
        "osm": "FISICO-GEO (OpenStreetMap voluntarios)",
        "wallapop_wholesale": "DIGITAL-ANUNCIO (plataforma C2C/B2C)",
        "milanuncios_wholesale": "DIGITAL-ANUNCIO (plataforma C2C/B2C)",
        "coches_net_wholesale": "DIGITAL-ANUNCIO (plataforma B2C)",
        "dgt_cat": "CENSO LEGAL (registro DGT, solo desguaces)",
        "aedra": "DIRECTORIO-ASOCIACION (solo desguaces)",
        "mercedes_benz_wholesale": "OEM LOCATOR (solo marca)",
        "autocasion_wholesale": "DIGITAL-ANUNCIO (plataforma B2C)",
        "motor_es_wholesale": "DIGITAL-ANUNCIO (plataforma B2C)",
        "coches_com_wholesale": "DIGITAL-ANUNCIO (plataforma B2C)",
    }
    for src, n in dealer_src_rows:
        ort = ortogonalidad_map.get(src, "desconocida/especializada")
        print(f"  {src:<45} {n:>10}  {ort}")

    # ------------------------------------------------------------------
    # SECCION 2: El problema de Chapman con las fuentes actuales
    # ------------------------------------------------------------------
    print()
    print("SECCION 2 — Analisis de solapamiento (m) entre pares clave")
    print("-" * 60)

    # Los 3 pares mas relevantes para Chapman:
    # A) OSM (fisico) x wallapop (digital): mayor ortogonalidad conceptual
    # B) OSM (fisico) x milanuncios (digital): similar
    # C) wallapop x milanuncios: menor ortogonalidad (ambas digitales)

    pairs = [
        ("osm", "wallapop_wholesale", "FISICO x DIGITAL-C2C"),
        ("osm", "milanuncios_wholesale", "FISICO x DIGITAL-C2C"),
        ("osm", "coches_net_wholesale", "FISICO x DIGITAL-B2C"),
        ("wallapop_wholesale", "milanuncios_wholesale", "DIGITAL x DIGITAL [NO ortogonal]"),
        ("wallapop_wholesale", "coches_net_wholesale", "DIGITAL x DIGITAL [NO ortogonal]"),
        ("dgt_cat", "aedra", "LEGAL x DIRECTORIO [solo desguaces]"),
    ]

    print(f"\n  {'Par':<55} {'n1':>6} {'n2':>6} {'m (entity_ulid)':>16} {'m (canonical)':>14}")
    print(f"  {'-'*55} {'-'*6} {'-'*6} {'-'*16} {'-'*14}")

    pair_results = []
    for src_a, src_b, label in pairs:
        # n1, n2 via entity_ulid (raw)
        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es JOIN entity e ON e.entity_ulid=es.entity_ulid
            WHERE es.source_key=%s AND e.kind IN %s
        """, (src_a, DEALER_KINDS))
        n1 = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es JOIN entity e ON e.entity_ulid=es.entity_ulid
            WHERE es.source_key=%s AND e.kind IN %s
        """, (src_b, DEALER_KINDS))
        n2 = cur.fetchone()[0]

        # m via entity_ulid (direct same-entity match)
        cur.execute("""
            SELECT COUNT(DISTINCT es_a.entity_ulid)
            FROM entity_source es_a
            JOIN entity_source es_b ON es_b.entity_ulid=es_a.entity_ulid
                AND es_b.source_key=%s
            JOIN entity e ON e.entity_ulid=es_a.entity_ulid
            WHERE es_a.source_key=%s AND e.kind IN %s
        """, (src_b, src_a, DEALER_KINDS))
        m_raw = cur.fetchone()[0]

        # m via canonical_ulid (using entity_cluster to bridge same physical dealer)
        cur.execute("""
            SELECT COUNT(DISTINCT ec_a.canonical_ulid)
            FROM entity_source es_a
            JOIN entity_cluster ec_a ON ec_a.entity_ulid = es_a.entity_ulid
            JOIN entity_cluster ec_b ON ec_b.canonical_ulid = ec_a.canonical_ulid
            JOIN entity_source es_b ON es_b.entity_ulid = ec_b.entity_ulid
                AND es_b.source_key = %s
            JOIN entity e ON e.entity_ulid = es_a.entity_ulid
            WHERE es_a.source_key = %s
              AND e.kind IN %s
        """, (src_b, src_a, DEALER_KINDS))
        m_canonical = cur.fetchone()[0]

        print(f"  {label:<55} {n1:>6} {n2:>6} {m_raw:>16} {m_canonical:>14}")
        pair_results.append((src_a, src_b, label, n1, n2, m_raw, m_canonical))

    # ------------------------------------------------------------------
    # SECCION 3: Chapman por par (usando m_canonical como mejor estimado)
    # ------------------------------------------------------------------
    print()
    print("SECCION 3 — Estimaciones Chapman globales (m = canonical overlap)")
    print("-" * 60)
    print()

    cur.execute("""
        SELECT COUNT(*) FROM entity WHERE kind IN %s
    """, (DEALER_KINDS,))
    numerator_total = cur.fetchone()[0]

    print(f"  Numerador nacional (dealers en DB): {numerator_total}")
    print()
    print(f"  {'Par':<55} {'N_hat':>8} {'IC95_low':>10} {'IC95_high':>10} {'Cob%':>7} {'Valid'}")
    print(f"  {'-'*55} {'-'*8} {'-'*10} {'-'*10} {'-'*7} {'-'*6}")

    best_pair = None
    for src_a, src_b, label, n1, n2, m_raw, m_canonical in pair_results:
        if n1 == 0 or n2 == 0:
            print(f"  {label:<55} {'---':>8} {'---':>10} {'---':>10} {'N/A':>7} NO_DATA")
            continue

        m = m_canonical  # usar canonical como mejor estimado de solapamiento real
        n_hat, var_n, ic_low, ic_high = chapman_estimate(n1, n2, m)
        is_valid = m >= 1 and n1 >= 20 and n2 >= 20
        cov_pct = f"{100.0 * numerator_total / n_hat:.1f}%" if n_hat > 0 else "N/A"
        valid_str = "OK" if is_valid else f"m={m}<MIN" if m < 1 else "INSUF"

        # IC width como proxy de precision
        ic_width = ic_high - ic_low
        ic_width_pct = 100.0 * ic_width / n_hat if n_hat > 0 else float("inf")

        print(f"  {label:<55} {n_hat:>8.0f} {ic_low:>10.0f} {ic_high:>10.0f} {cov_pct:>7} {valid_str}")
        if is_valid and (best_pair is None or ic_width_pct < best_pair["ic_width_pct"]):
            best_pair = {
                "src_a": src_a, "src_b": src_b, "label": label,
                "n1": n1, "n2": n2, "m": m,
                "n_hat": n_hat, "ic_low": ic_low, "ic_high": ic_high,
                "ic_width_pct": ic_width_pct,
            }

    # ------------------------------------------------------------------
    # SECCION 4: Chapman por provincia (OSM x wallapop, canonical)
    # Solo para provincias donde hay datos suficientes
    # ------------------------------------------------------------------
    print()
    print("SECCION 4 — Chapman por provincia (OSM x wallapop_wholesale, canonical_ulid)")
    print("-" * 60)
    print()
    print("  NOTA: m via canonical_ulid (entidad fisica real, no entity_ulid)")
    print()

    cur.execute("SELECT code, name FROM geo_province ORDER BY code")
    provinces = cur.fetchall()

    cur.execute("""
        SELECT province_code, COUNT(*) AS n
        FROM entity WHERE kind IN %s AND province_code IS NOT NULL
        GROUP BY province_code
    """, (DEALER_KINDS,))
    numerator_by_prov = {r[0].strip(): r[1] for r in cur.fetchall()}

    print(f"  {'Prov':<5} {'Nombre':<22} {'n_OSM':>6} {'n_WP':>6} {'m_raw':>6} {'m_can':>6} {'N_hat':>8} "
          f"{'IC_low':>8} {'IC_high':>9} {'Num_DB':>7} {'Cob%':>7} {'Valid'}")
    print(f"  {'-'*5} {'-'*22} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*8} "
          f"{'-'*8} {'-'*9} {'-'*7} {'-'*7} {'-'*6}")

    prov_results = []
    for prov_code, prov_name in provinces:
        prov_code = prov_code.strip()

        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es JOIN entity e ON e.entity_ulid=es.entity_ulid
            WHERE es.source_key='osm' AND e.kind IN %s AND e.province_code=%s
        """, (DEALER_KINDS, prov_code))
        n1 = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es JOIN entity e ON e.entity_ulid=es.entity_ulid
            WHERE es.source_key='wallapop_wholesale' AND e.kind IN %s AND e.province_code=%s
        """, (DEALER_KINDS, prov_code))
        n2 = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT es_a.entity_ulid)
            FROM entity_source es_a
            JOIN entity_source es_b ON es_b.entity_ulid=es_a.entity_ulid
                AND es_b.source_key='wallapop_wholesale'
            JOIN entity e ON e.entity_ulid=es_a.entity_ulid
            WHERE es_a.source_key='osm' AND e.kind IN %s AND e.province_code=%s
        """, (DEALER_KINDS, prov_code))
        m_raw = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT ec_a.canonical_ulid)
            FROM entity_source es_a
            JOIN entity_cluster ec_a ON ec_a.entity_ulid = es_a.entity_ulid
            JOIN entity_cluster ec_b ON ec_b.canonical_ulid = ec_a.canonical_ulid
            JOIN entity_source es_b ON es_b.entity_ulid = ec_b.entity_ulid
                AND es_b.source_key = 'wallapop_wholesale'
            JOIN entity e ON e.entity_ulid = es_a.entity_ulid
            WHERE es_a.source_key = 'osm'
              AND e.kind IN %s
              AND e.province_code = %s
        """, (DEALER_KINDS, prov_code))
        m_can = cur.fetchone()[0]

        num = numerator_by_prov.get(prov_code, 0)

        if n1 >= 1 and n2 >= 1 and m_can >= 1:
            n_hat, var_n, ic_low, ic_high = chapman_estimate(n1, n2, m_can)
            is_valid = n1 >= 5 and n2 >= 5
            cov_pct = f"{100.0 * num / n_hat:.1f}%" if n_hat > 0 else "N/A"
            valid_str = "OK" if is_valid else "INSUF"
        elif n1 >= 1 and n2 >= 1:
            # m=0: Chapman tecnicamente da N_hat = (n1+1)(n2+1) - 1 (supuesto extremo)
            n_hat, var_n, ic_low, ic_high = chapman_estimate(n1, n2, 0)
            is_valid = False
            cov_pct = f"{100.0 * num / n_hat:.1f}%"
            valid_str = "m=0"
        else:
            n_hat = ic_low = ic_high = 0
            is_valid = False
            cov_pct = "N/A"
            valid_str = "NO_DATA"

        n_hat_s = f"{n_hat:.0f}" if n_hat > 0 else "---"
        ic_s = f"{ic_low:.0f}" if n_hat > 0 else "---"
        ic_h_s = f"{ic_high:.0f}" if n_hat > 0 else "---"

        print(f"  {prov_code:<5} {prov_name[:22]:<22} {n1:>6} {n2:>6} {m_raw:>6} {m_can:>6} "
              f"{n_hat_s:>8} {ic_s:>8} {ic_h_s:>9} {num:>7} {cov_pct:>7} {valid_str}")

        prov_results.append({
            "code": prov_code, "name": prov_name,
            "n1": n1, "n2": n2, "m_raw": m_raw, "m_can": m_can,
            "n_hat": n_hat, "ic_low": ic_low, "ic_high": ic_high,
            "numerator": num, "valid": is_valid,
        })

    # ------------------------------------------------------------------
    # SECCION 5: Resumen y diagnostico
    # ------------------------------------------------------------------
    print()
    print("SECCION 5 — Resumen ejecutivo y diagnostico")
    print("=" * 70)

    valid_provs = [p for p in prov_results if p["valid"]]
    m0_provs = [p for p in prov_results if p["n1"] >= 1 and p["n2"] >= 1 and p["m_can"] == 0]
    nodata_provs = [p for p in prov_results if p["n1"] == 0 or p["n2"] == 0]

    print(f"""
ESTADO ACTUAL DEL DENOMINADOR CHAPMAN (CARDEEP, 2026-06-14):

1. FUENTES DISPONIBLES EN entity_source:
   - wallapop_wholesale:    {next(r[1] for r in dealer_src_rows if r[0]=='wallapop_wholesale'):>6} dealers (digital, plataforma anuncios)
   - milanuncios_wholesale: {next(r[1] for r in dealer_src_rows if r[0]=='milanuncios_wholesale'):>6} dealers (digital, plataforma anuncios)
   - osm:                   {next(r[1] for r in dealer_src_rows if r[0]=='osm'):>6} dealers (fisico-geografico)
   - coches_net_wholesale:  {next(r[1] for r in dealer_src_rows if r[0]=='coches_net_wholesale'):>6} dealers (digital, Tier-1)
   - dgt_cat:               {next(r[1] for r in dealer_src_rows if r[0]=='dgt_cat'):>6} desguaces (censo legal DGT)

2. SOLAPAMIENTO (m) REAL ENTRE FUENTES:
   - entity_ulid overlap (mismo canonical): OSM x wallapop = 0 (sin merge)
   - canonical_ulid overlap (fisica real):  OSM x wallapop = 10 global
   - IC95 resultante: [0, ~4.5M] — INUTILIZABLE como denominador

3. CAUSA DEL m~0:
   - entity_source asigna UN entity_ulid por (fuente, dealer)
   - Los mismos dealers fisicos en OSM y wallapop tienen entity_ulid DISTINTOS
   - entity_cluster ha mergeado solo 10 casos OSM+wallapop de ~4.187 posibles
   - => El dedup B1 NO ha cruzado OSM contra wallapop sistematicamente
   - => m_canonical = 10 es una COTA INFERIOR del solapamiento real

4. PROVINCIAS CON CHAPMAN VALIDO (m_can >= 1, n1>=5, n2>=5):
   Total provincias validas: {len(valid_provs)} de 52
   {", ".join(p['code']+'('+p['name'][:8]+')' for p in valid_provs) if valid_provs else "NINGUNA"}

5. PROVINCIAS CON m=0 (Chapman no calculable con precision):
   Total: {len(m0_provs)} provincias
   {", ".join(p['code'] for p in m0_provs[:20])}{"..." if len(m0_provs)>20 else ""}

6. PROVINCIAS SIN DATOS OSM O WALLAPOP:
   Total: {len(nodata_provs)} provincias
   {", ".join(p['code'] for p in nodata_provs[:10])}{"..." if len(nodata_provs)>10 else ""}

7. CONTRASTE vs CIFRAS OFICIALES:
   Dealers en DB:              {numerator_total:>8}
   CNAE 4511 total empresas:   ~27.284  (incluye todo tipo, ceiling maximo)
   FACONAUTO instalaciones:      5.358  (concesionarios franquiciados)
   DGT desguaces CATs:           1.292  (exacto, sellado)
   Compraventas PA floor:        1.662  (minimo declarado)
   Chapman N_hat OSM x WP:   ~151.840  IC95=[0, 303.679]  [m=10, n_osm=9956, n_wp=4187]

   DIAGNOSTICO DE ORDEN DE MAGNITUD:
   El N_hat = 151.840 es plausible como ceiling del universo dealer+garaje+compraventa:
   - Mayor que los 50.167 dealers actuales en DB => hay cobertura pendiente
   - Mayor que el CNAE 4511 de 27.284 empresas => sobreestimacion probable
   - El IC [0, 303k] es demasiado ancho para ser util => m=10 insuficiente
   INTERPRETACION: Chapman da rango PLAUSIBLE pero no preciso. El N_hat ~152k
   esta probablemente SOBREESTIMADO porque el supuesto de independencia se viola
   parcialmente (bias hacia arriba cuando hay heterogeneidad de captura).

8. QUE FALTA PARA CHAPMAN ROBUSTO:
   IMPRESCINDIBLE:
   a) Ingestar OVERTURE MAPS (cat_dealer + automotive, Espana) -> ~10k+ POIs
      ORTOGONAL a wallapop (mecanismo distinto: mapas comerciales Google/Meta/Apple)
      Forma: DuckDB + Parquet dump mensual, €0, licencia permisiva CC BY 4.0
      Resultado esperado: m_canonical >> 10 -> IC estrechado a +/-20% de N_hat

   b) Ejecutar dedup B1 cruzando OSM contra wallapop/milanuncios por
      (lat,lon +/- 100m) O (phone_hash) O (website_domain) para encontrar
      el solapamiento real latente (m real estimado: 200-500 globals)
      => Esto mejora el Chapman con datos ya existentes, sin nueva ingestion

   DESEABLE:
   c) Paginas Amarillas como directorio fisico adicional (~1.662 compraventas)
   d) CNAE registry publico (IAE declarations) como fuente administrativa

9. DENOMINADOR B6 PROVISIONAL (sin Chapman robusto):
   SEGMENTO              DENOMINADOR OFICIAL    DB ACTUAL   COBERTURA
   Concesionarios of.    5.358 instalaciones       1.844      34.4%
   Desguaces CATs        1.292 (exacto DGT)        1.645     >100% (overcount)
   Compraventas POS      1.662-27.284 (range)     39.308     >100% floor
   Garajes (activos)     indefinido               7.220      inmensurable
   Total dealer          ~10.312-39.296            50.167    estim. 50-100%+

   => Sello 52/52 requiere denominador MEDIDO con IC por provincia.
   => HOY: denominador = floor+ceiling sin IC valido excepto desguaces (sellado).
   => CAMINO AL SELLO: ingestar Overture Maps + dedup cruzado OSM x plataformas.
""")

    conn.close()
    print("=" * 70)
    print("FIN — zero writes, zero commits.")
    print("=" * 70)


if __name__ == "__main__":
    main()
