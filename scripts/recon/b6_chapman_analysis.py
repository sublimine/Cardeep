"""
B6 Chapman Analysis — Denominador capture-recapture por provincia para dealers.

READ-ONLY — zero writes, zero commits.

Metodologia Chapman/Lincoln-Petersen:
  N_hat = ((n1+1)(n2+1)/(m+1)) - 1
  Var   = ((n1+1)(n2+1)(n1-m)(n2-m)) / ((m+1)^2 (m+2))
  IC95  = N_hat +/- 1.96 * sqrt(Var)

Donde:
  n1 = dealers capturados SOLO por fuente A (o A+B+...)
  n2 = dealers capturados SOLO por fuente B (o B+...)
  m  = dealers capturados por AMBAS fuentes (overlap)

Fuentes candidatas a ortogonalidad:
  - wallapop_wholesale / milanuncios_wholesale: plataformas de anuncios (comerciales)
  - osm: directorio fisico geografico (OpenStreetMap)
  - coches_net_wholesale: plataforma anuncios Tier-1
  - dgt_cat: censo legal (desguaces)
  - Cualquier par con mecanismos de captura independientes

NOTA: Para Chapman valido se necesitan fuentes ORTOGONALES (mecanismo de
captura independiente). Si los dealers aparecen en ambas por las mismas razones
(ej. ambas dependen de que el dealer tenga presencia online), el supuesto de
independencia se viola y N_hat esta sesgado.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from typing import Optional

import psycopg2

DSN = "postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep"

# Tipos de dealer (no particulares, no plataformas)
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


@dataclass
class ChapmanResult:
    """Resultado Chapman para un par de fuentes en una provincia (o global)."""
    province_code: Optional[str]
    province_name: str
    source_a: str
    source_b: str
    n1: int           # dealers capturados por fuente A
    n2: int           # dealers capturados por fuente B
    m: int            # dealers capturados por AMBAS
    n_hat: float
    var_n: float
    ic_low: float
    ic_high: float
    numerator: int    # dealers actuales en DB para esta provincia

    @property
    def coverage_pct(self) -> str:
        if self.n_hat <= 0:
            return "N/A"
        return f"{100.0 * self.numerator / self.n_hat:.1f}%"

    @property
    def ic_str(self) -> str:
        return f"[{self.ic_low:.0f}, {self.ic_high:.0f}]"

    @property
    def se(self) -> float:
        return math.sqrt(max(self.var_n, 0.0))

    def is_valid(self) -> bool:
        """Chapman valido cuando m >= 1 y ambas muestras son suficientes."""
        return self.m >= 1 and self.n1 >= 5 and self.n2 >= 5


def chapman_estimate(n1: int, n2: int, m: int) -> tuple[float, float, float, float]:
    """Calcula N_hat, Var, IC_low, IC_high usando estimador Chapman."""
    if m < 0:
        m = 0
    n_hat = ((n1 + 1) * (n2 + 1) / (m + 1)) - 1

    # Varianza Chapman
    numerator_var = (n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m)
    denominator_var = (m + 1) ** 2 * (m + 2)
    if denominator_var == 0:
        var_n = float("inf")
    else:
        var_n = numerator_var / denominator_var

    se = math.sqrt(max(var_n, 0.0))
    ic_low = max(0.0, n_hat - 1.96 * se)
    ic_high = n_hat + 1.96 * se

    return n_hat, var_n, ic_low, ic_high


def main() -> None:
    print("=" * 70)
    print("B6 — Chapman capture-recapture denominador por provincia (READ-ONLY)")
    print("=" * 70)
    print()

    conn = psycopg2.connect(DSN)
    cur = conn.cursor()

    # -----------------------------------------------------------------------
    # PASO 1: Auditar solapamiento entre fuentes para dealers
    # -----------------------------------------------------------------------
    print("PASO 1 — Solapamiento entre pares de fuentes (dealers only)")
    print("-" * 60)

    # Fuentes con volumen relevante para dealers (no particulares)
    # Primero identificamos que fuentes tienen presencia real en dealers
    cur.execute("""
        SELECT es.source_key, COUNT(DISTINCT es.entity_ulid) AS n
        FROM entity_source es
        JOIN entity e ON e.entity_ulid = es.entity_ulid
        WHERE e.kind IN %s
        GROUP BY es.source_key
        ORDER BY n DESC
    """, (DEALER_KINDS,))
    dealer_sources = cur.fetchall()

    print("\nFuentes con presencia en dealers (kind != particular):")
    print(f"  {'source_key':<45} {'n_dealers':>10}")
    print(f"  {'-'*45} {'-'*10}")
    for src, n in dealer_sources:
        print(f"  {src:<45} {n:>10}")

    # -----------------------------------------------------------------------
    # PASO 2: Matriz de solapamiento entre las fuentes mas importantes
    # -----------------------------------------------------------------------
    print()
    print("PASO 2 — Matriz de solapamiento (dealers que aparecen en AMBAS fuentes)")
    print("-" * 60)

    # Candidatos a ser pares ortogonales: fuentes con >100 dealers
    candidate_sources = [r[0] for r in dealer_sources if r[1] >= 100]
    print(f"\nFuentes candidatas (>= 100 dealers): {len(candidate_sources)}")

    # Calcular overlap por par
    print("\nSolapamiento entre pares:")
    print(f"  {'Fuente A':<35} {'Fuente B':<35} {'n1':>6} {'n2':>6} {'m':>6} {'% overlap':>10}")
    print(f"  {'-'*35} {'-'*35} {'-'*6} {'-'*6} {'-'*6} {'-'*10}")

    overlap_pairs = []
    for i, src_a in enumerate(candidate_sources):
        n_a = next(r[1] for r in dealer_sources if r[0] == src_a)
        for src_b in candidate_sources[i + 1:]:
            n_b = next(r[1] for r in dealer_sources if r[0] == src_b)
            cur.execute("""
                SELECT COUNT(DISTINCT es_a.entity_ulid)
                FROM entity_source es_a
                JOIN entity_source es_b ON es_b.entity_ulid = es_a.entity_ulid
                    AND es_b.source_key = %s
                JOIN entity e ON e.entity_ulid = es_a.entity_ulid
                WHERE es_a.source_key = %s
                  AND e.kind IN %s
            """, (src_b, src_a, DEALER_KINDS))
            m = cur.fetchone()[0]

            pct_a = 100.0 * m / n_a if n_a > 0 else 0.0
            pct_b = 100.0 * m / n_b if n_b > 0 else 0.0
            overlap_pct = f"{pct_a:.1f}%/A  {pct_b:.1f}%/B"
            print(f"  {src_a:<35} {src_b:<35} {n_a:>6} {n_b:>6} {m:>6}  {overlap_pct}")
            overlap_pairs.append((src_a, src_b, n_a, n_b, m))

    # -----------------------------------------------------------------------
    # PASO 3: Chapman global por pares ortogonales candidatos
    # -----------------------------------------------------------------------
    print()
    print("PASO 3 — Chapman global (todas las provincias) por pares")
    print("-" * 60)

    # Total dealers en DB (numerador nacional)
    cur.execute("""
        SELECT COUNT(*) FROM entity WHERE kind IN %s
    """, (DEALER_KINDS,))
    total_dealers_db = cur.fetchone()[0]
    print(f"\nNumerador nacional (dealers en DB): {total_dealers_db}")

    print()
    print("Estimaciones Chapman globales:")
    print(f"  {'Par':<60} {'n1':>6} {'n2':>6} {'m':>6} {'N_hat':>8} {'IC95':>20} {'valid'}")
    print(f"  {'-'*60} {'-'*6} {'-'*6} {'-'*6} {'-'*8} {'-'*20} {'-'*5}")

    global_results = []
    for src_a, src_b, n1, n2, m in overlap_pairs:
        n_hat, var_n, ic_low, ic_high = chapman_estimate(n1, n2, m)
        is_valid = m >= 1 and n1 >= 5 and n2 >= 5
        pair_label = f"{src_a} x {src_b}"[:60]
        print(f"  {pair_label:<60} {n1:>6} {n2:>6} {m:>6} {n_hat:>8.0f} [{ic_low:>7.0f},{ic_high:>7.0f}]  {'OK' if is_valid else 'INSUF'}")
        global_results.append((src_a, src_b, n1, n2, m, n_hat, var_n, ic_low, ic_high, is_valid))

    # -----------------------------------------------------------------------
    # PASO 4: Chapman por provincia para el par mas ortogonal
    # Elegimos OSM (fisico, geografico) vs wallapop/milanuncios (digital, anuncios)
    # como el par con mayor ortogonalidad conceptual
    # -----------------------------------------------------------------------
    print()
    print("PASO 4 — Chapman por provincia (OSM x wallapop_wholesale)")
    print("         [OSM=directorio fisico; wallapop=plataforma digital anuncios]")
    print("-" * 60)

    # Verificar que el par OSM x wallapop tiene datos suficientes
    osm_vs_wp = next(
        ((a, b, n1, n2, m) for a, b, n1, n2, m in overlap_pairs
         if set([a, b]) == {"osm", "wallapop_wholesale"}),
        None
    )
    if osm_vs_wp:
        src_a, src_b, n1_global, n2_global, m_global = osm_vs_wp
        print(f"\n  Par seleccionado: {src_a} x {src_b}")
        print(f"  n1(OSM)={n1_global}, n2(wallapop)={n2_global}, m(overlap)={m_global}")
        m_pct = 100.0 * m_global / min(n1_global, n2_global) if min(n1_global, n2_global) > 0 else 0
        print(f"  Solapamiento: {m_pct:.1f}% de la fuente menor")
    else:
        print("  WARN: par OSM x wallapop no encontrado en candidatos, usando primera fuente disponible")

    # Provinces
    cur.execute("SELECT province_code, name FROM geo_province ORDER BY province_code")
    provinces = cur.fetchall()

    # Numerador por provincia (dealers actuales)
    cur.execute("""
        SELECT province_code, COUNT(*) AS n
        FROM entity
        WHERE kind IN %s
          AND province_code IS NOT NULL
        GROUP BY province_code
    """, (DEALER_KINDS,))
    numerator_by_prov = {r[0]: r[1] for r in cur.fetchall()}

    print()
    print("Tabla Chapman por provincia (OSM x wallapop_wholesale):")
    print(f"\n  {'Prov':<5} {'Nombre':<20} {'n_OSM':>6} {'n_WP':>6} {'m':>5} {'N_hat':>8} {'IC95':>20} {'Num':>6} {'Cob%':>7} {'Valid'}")
    print(f"  {'-'*5} {'-'*20} {'-'*6} {'-'*6} {'-'*5} {'-'*8} {'-'*20} {'-'*6} {'-'*7} {'-'*5}")

    chapman_by_prov = []
    for prov_code, prov_name in provinces:
        prov_code = prov_code.strip()

        # n1 = OSM dealers en esta provincia
        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es
            JOIN entity e ON e.entity_ulid = es.entity_ulid
            WHERE es.source_key = 'osm'
              AND e.kind IN %s
              AND e.province_code = %s
        """, (DEALER_KINDS, prov_code))
        n1 = cur.fetchone()[0]

        # n2 = wallapop dealers en esta provincia
        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es
            JOIN entity e ON e.entity_ulid = es.entity_ulid
            WHERE es.source_key = 'wallapop_wholesale'
              AND e.kind IN %s
              AND e.province_code = %s
        """, (DEALER_KINDS, prov_code))
        n2 = cur.fetchone()[0]

        # m = dealers que aparecen en AMBAS (OSM Y wallapop) en esta provincia
        cur.execute("""
            SELECT COUNT(DISTINCT es_a.entity_ulid)
            FROM entity_source es_a
            JOIN entity_source es_b ON es_b.entity_ulid = es_a.entity_ulid
                AND es_b.source_key = 'wallapop_wholesale'
            JOIN entity e ON e.entity_ulid = es_a.entity_ulid
            WHERE es_a.source_key = 'osm'
              AND e.kind IN %s
              AND e.province_code = %s
        """, (DEALER_KINDS, prov_code))
        m = cur.fetchone()[0]

        numerator = numerator_by_prov.get(prov_code, 0)

        if n1 >= 1 and n2 >= 1:
            n_hat, var_n, ic_low, ic_high = chapman_estimate(n1, n2, m)
            is_valid = m >= 1 and n1 >= 5 and n2 >= 5
            cob_pct = f"{100.0 * numerator / n_hat:.1f}%" if n_hat > 0 else "N/A"
            valid_str = "OK" if is_valid else ("m=0" if m == 0 else "INSUF")
        else:
            n_hat, var_n, ic_low, ic_high = 0, 0, 0, 0
            is_valid = False
            cob_pct = "N/A"
            valid_str = "NO_DATA"

        ic_str = f"[{ic_low:.0f},{ic_high:.0f}]" if n_hat > 0 else "---"
        n_hat_str = f"{n_hat:.0f}" if n_hat > 0 else "---"

        print(f"  {prov_code:<5} {prov_name[:20]:<20} {n1:>6} {n2:>6} {m:>5} {n_hat_str:>8} {ic_str:>20} {numerator:>6} {cob_pct:>7} {valid_str}")

        chapman_by_prov.append({
            "province_code": prov_code,
            "province_name": prov_name,
            "n1_osm": n1,
            "n2_wallapop": n2,
            "m": m,
            "n_hat": n_hat,
            "ic_low": ic_low,
            "ic_high": ic_high,
            "numerator": numerator,
            "is_valid": is_valid,
        })

    # -----------------------------------------------------------------------
    # PASO 5: Chapman OSM x milanuncios (segundo par ortogonal)
    # -----------------------------------------------------------------------
    print()
    print("PASO 5 — Chapman por provincia (OSM x milanuncios_wholesale)")
    print("-" * 60)

    print()
    print(f"  {'Prov':<5} {'Nombre':<20} {'n_OSM':>6} {'n_MN':>6} {'m':>5} {'N_hat':>8} {'IC95':>20} {'Num':>6} {'Cob%':>7} {'Valid'}")
    print(f"  {'-'*5} {'-'*20} {'-'*6} {'-'*6} {'-'*5} {'-'*8} {'-'*20} {'-'*6} {'-'*7} {'-'*5}")

    for prov_code, prov_name in provinces:
        prov_code = prov_code.strip()

        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es
            JOIN entity e ON e.entity_ulid = es.entity_ulid
            WHERE es.source_key = 'osm'
              AND e.kind IN %s
              AND e.province_code = %s
        """, (DEALER_KINDS, prov_code))
        n1 = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es
            JOIN entity e ON e.entity_ulid = es.entity_ulid
            WHERE es.source_key = 'milanuncios_wholesale'
              AND e.kind IN %s
              AND e.province_code = %s
        """, (DEALER_KINDS, prov_code))
        n2 = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT es_a.entity_ulid)
            FROM entity_source es_a
            JOIN entity_source es_b ON es_b.entity_ulid = es_a.entity_ulid
                AND es_b.source_key = 'milanuncios_wholesale'
            JOIN entity e ON e.entity_ulid = es_a.entity_ulid
            WHERE es_a.source_key = 'osm'
              AND e.kind IN %s
              AND e.province_code = %s
        """, (DEALER_KINDS, prov_code))
        m = cur.fetchone()[0]

        numerator = numerator_by_prov.get(prov_code, 0)

        if n1 >= 1 and n2 >= 1:
            n_hat, var_n, ic_low, ic_high = chapman_estimate(n1, n2, m)
            is_valid = m >= 1 and n1 >= 5 and n2 >= 5
            cob_pct = f"{100.0 * numerator / n_hat:.1f}%" if n_hat > 0 else "N/A"
            valid_str = "OK" if is_valid else ("m=0" if m == 0 else "INSUF")
        else:
            n_hat = var_n = ic_low = ic_high = 0
            is_valid = False
            cob_pct = "N/A"
            valid_str = "NO_DATA"

        ic_str = f"[{ic_low:.0f},{ic_high:.0f}]" if n_hat > 0 else "---"
        n_hat_str = f"{n_hat:.0f}" if n_hat > 0 else "---"
        print(f"  {prov_code:<5} {prov_name[:20]:<20} {n1:>6} {n2:>6} {m:>5} {n_hat_str:>8} {ic_str:>20} {numerator:>6} {cob_pct:>7} {valid_str}")

    # -----------------------------------------------------------------------
    # PASO 6: Diagnostico de supuestos Chapman
    # -----------------------------------------------------------------------
    print()
    print("PASO 6 — Diagnostico de supuestos Chapman")
    print("-" * 60)

    # Violacion supuesto 1: independencia de capturas
    # Si OSM y wallapop tienen alto solapamiento (m/n_min > 50%), las capturas son dependientes
    # Verificar: OSM incluye datos de wallapop? O los dos se basan en el mismo registro origin?

    print("""
SUPUESTO 1 — Independencia de capturas:
  OSM: datos geograficos de OpenStreetMap (contribucion ciudadana, presencia fisica)
  wallapop_wholesale: anuncios activos en la plataforma wallapop (presencia digital)
  milanuncios_wholesale: anuncios activos en milanuncios (presencia digital)

  Ortogonalidad:
  - OSM captura dealers que EXISTEN fisicamente y han sido mapeados por voluntarios
  - wallapop/milanuncios captura dealers que ANUNCIAN activamente en plataformas
  - Un dealer puede estar en OSM sin anunciar en wallapop/milanuncios (p.ej. solo tiene web propia)
  - Un dealer puede anunciar en wallapop sin estar en OSM (nuevo, no mapeado aun)
  => Ortogonalidad PARCIAL: mecanismos distintos pero correlacionados (ambos requieren
     que el dealer este activo)

SUPUESTO 2 — Poblacion cerrada:
  El universo de dealers ES es relativamente estable (no aparecen/desaparecen en semanas)
  => Supuesto RAZONABLEMENTE MET para una estimacion puntual

SUPUESTO 3 — Probabilidad de captura uniforme:
  VIOLADO parcialmente:
  - Grandes dealers con mucho stock tienen mayor probabilidad de estar en wallapop
  - Dealers rurales/pequenos tienen menor presencia en plataformas digitales
  - OSM tiene sesgo geografico (mejor cobertura en areas urbanas con mas mapeadores)
  => El N_hat puede estar SUBESTIMADO (dealers pequenos no visibles en ninguna fuente)

CONCLUSION DIAGNOSTICO:
  El estimador Chapman con OSM x wallapop/milanuncios es valido como COTA INFERIOR
  del universo real. El N_hat verdadero es >= al calculado. La heterogeneidad de
  probabilidad de captura sesga N_hat hacia abajo.
""")

    # -----------------------------------------------------------------------
    # PASO 7: Contraste contra cifras oficiales
    # -----------------------------------------------------------------------
    print()
    print("PASO 7 — Contraste N_hat nacional vs cifras oficiales")
    print("-" * 60)

    # Recalcular globales para los dos pares principales
    for pair_label, src_a, src_b in [
        ("OSM x wallapop", "osm", "wallapop_wholesale"),
        ("OSM x milanuncios", "osm", "milanuncios_wholesale"),
        ("wallapop x milanuncios", "wallapop_wholesale", "milanuncios_wholesale"),
    ]:
        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es
            JOIN entity e ON e.entity_ulid = es.entity_ulid
            WHERE es.source_key = %s
              AND e.kind IN %s
        """, (src_a, DEALER_KINDS))
        n1 = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT es.entity_ulid)
            FROM entity_source es
            JOIN entity e ON e.entity_ulid = es.entity_ulid
            WHERE es.source_key = %s
              AND e.kind IN %s
        """, (src_b, DEALER_KINDS))
        n2 = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT es_a.entity_ulid)
            FROM entity_source es_a
            JOIN entity_source es_b ON es_b.entity_ulid = es_a.entity_ulid
                AND es_b.source_key = %s
            JOIN entity e ON e.entity_ulid = es_a.entity_ulid
            WHERE es_a.source_key = %s
              AND e.kind IN %s
        """, (src_b, src_a, DEALER_KINDS))
        m = cur.fetchone()[0]

        if n1 > 0 and n2 > 0:
            n_hat, var_n, ic_low, ic_high = chapman_estimate(n1, n2, m)
            print(f"\n  {pair_label}: n1={n1}, n2={n2}, m={m}")
            print(f"    N_hat = {n_hat:.0f}  IC95=[{ic_low:.0f}, {ic_high:.0f}]")
            print(f"    Numerador DB = {total_dealers_db}")
            cov = 100.0 * total_dealers_db / n_hat if n_hat > 0 else 0
            print(f"    Cobertura estimada = {cov:.1f}%")
            m_pct = 100.0 * m / min(n1, n2) if min(n1, n2) > 0 else 0
            print(f"    Solapamiento m/n_min = {m_pct:.1f}% {'[ALTO — independencia debil]' if m_pct > 30 else '[razonable]'}")

    print()
    print("  CIFRAS OFICIALES REFERENCIA (de B5_COVERAGE_RECON.md):")
    print("    Concesionarios franquiciados: 2.143 grupos / 5.358 instalaciones (FACONAUTO/DBK)")
    print("    Desguaces CATs legales:      1.292 (DGT census exacto)")
    print("    CNAE 4511+4519 total:       ~39.334 empresas activas (incluye todo tipo)")
    print("    Compraventas PA floor:        1.662 | OSM: 3.516 | CNAE ceiling: 27k+")
    print()
    print(f"  CARDEEP DB actual (dealers): {total_dealers_db}")
    print("    => Si N_hat >> numerador DB: hay universo no cubierto")
    print("    => Si N_hat ~ numerador DB:  cobertura aproximada (pero N_hat es cota inferior)")
    print("    => Si N_hat < denominador oficial: Chapman esta subestimando (supuestos violados)")

    # -----------------------------------------------------------------------
    # PASO 8: Fuentes que FALTAN para Chapman robusto
    # -----------------------------------------------------------------------
    print()
    print("PASO 8 — Fuentes faltantes para Chapman robusto")
    print("-" * 60)
    print("""
Para un Chapman con supuestos validos se necesitan >= 2 fuentes con:
  a) Mecanismo de captura REALMENTE independiente
  b) Cobertura geografica nacional (todas las 52 provincias)
  c) Suficiente solapamiento (m >= 10-20 por provincia para IC estrecho)

FUENTES ACTUALES y su ortogonalidad:
  wallapop_wholesale  — plataforma digital anuncios   (224.822 dealers)
  milanuncios_wholesale — plataforma digital anuncios (123.600 dealers)
  osm                 — directorio fisico geografico  (9.956 dealers)
  coches_net_wholesale — plataforma digital Tier-1    (7.269 dealers)
  dgt_cat             — CENSO LEGAL desguaces solo    (1.292 dealers)

PROBLEMA CRITICO:
  wallapop y milanuncios NO son ortogonales entre si:
  - Ambas requieren que el dealer tenga presencia activa en plataformas digitales
  - Un dealer que anuncia en wallapop probablemente tambien anuncia en milanuncios
  - El supuesto de independencia se viola -> N_hat(WP x MN) esta SESGADO

  OSM x [wallapop|milanuncios] es el mejor par disponible hoy, pero:
  - OSM tiene cobertura urbana sesgada (voluntarios concentrados en ciudades)
  - El solapamiento m es bajo -> N_hat con IC muy ancho -> poco preciso

FUENTES NECESARIAS para Chapman robusto (no en DB hoy):

  1. OVERTURE MAPS (prioridad ALTA, GRATIS)
     - Licencia permisiva (CC BY 4.0 Overture)
     - Covers toda Espana: ~10k+ POIs car_dealer + automotive
     - Origen: Google Maps + Meta + Apple Maps + TomTom fusionados
     - ORTOGONAL a OSM y a wallapop: captura por presencia en mapas comerciales,
       no por anuncios activos
     - Disponible: DuckDB + Parquet dump mensual
     - Faltante: no ingested en entity_source aun
     - Esperado: proporcionaria la 2a captura robusta para Chapman

  2. PAGINAS AMARILLAS directorio fisico
     - ~1.662 compraventas declaradas + talleres que venden
     - Ortogonal a plataformas digitales: captura por registro de negocio fisico
     - Ya citado en arquitectura como fuente Discovery; NO en entity_source aun

  3. REGISTRO CNAE CCAA (registros publicos)
     - Alta ortogonalidad: captura por declaracion fiscal (IAE/CNAE)
     - Mecanismo completamente distinto a wallapop/OSM
     - Fuente: INE DIRCE, eInforma CNAE 4511+4519
     - Faltante: no ingested aun

CONCLUSION FINAL:
  Con las fuentes actuales en entity_source, Chapman da una COTA INFERIOR valida
  pero con IC muy ancho por bajo solapamiento OSM x digital.
  El N_hat robusto require ingestar Overture Maps como 2a fuente ortogonal.
  Sin Overture/PA/CNAE-registros, el denominador sigue siendo [1.662 floor, 27k+ ceiling]
  con Chapman como cota inferior provisional.
""")

    conn.close()
    print()
    print("=" * 70)
    print("FIN — zero writes, zero commits ejecutados.")
    print("=" * 70)


if __name__ == "__main__":
    main()
