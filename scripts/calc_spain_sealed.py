"""
CARDEEP SPAIN_SEALED B6.4 — Calculo definitivo.
Todos los datos [VERIFICADO DB 2026-06-14].
NO mutacion de DB. Solo lectura y calculo.
"""

RATIO_451_45 = 23085 / 88621  # DIRCE 2025: grupo 451 / CNAE 45

# CNAE-45 locales por provincia 2024 [VERIFICADO CSV denominador_cnae45_provincia_2024.csv]
# suma real = 87.229; se usa ratio sobre base 2025 (88.621) por coherencia con DIRCE 451 2025
cnae45 = {
    "01": 467,   "02": 820,   "03": 3957,  "04": 1506,  "05": 339,
    "06": 1687,  "07": 1916,  "08": 8508,  "09": 649,   "10": 881,
    "11": 1805,  "12": 1099,  "13": 1097,  "14": 1672,  "15": 2235,
    "16": 508,   "17": 1574,  "18": 1809,  "19": 465,   "20": 950,
    "21": 892,   "22": 436,   "23": 1282,  "24": 990,   "25": 1114,
    "26": 566,   "27": 863,   "28": 11567, "29": 3589,  "30": 3112,
    "31": 1203,  "32": 739,   "33": 1724,  "34": 286,   "35": 2179,
    "36": 2010,  "37": 666,   "38": 2200,  "39": 951,   "40": 306,
    "41": 3858,  "42": 162,   "43": 1542,  "44": 292,   "45": 1760,
    "46": 4650,  "47": 817,   "48": 1464,  "49": 376,   "50": 1425,
    "51": 101,   "52": 163,
}

# Numerador canonico VENTA SERVIDA (v_canonical path B) [VERIFICADO DB 2026-06-14]
# COUNT(DISTINCT COALESCE(canonical_ulid, entity_ulid)) WHERE status=available
cv_served = {
    "01": 94,   "02": 123,  "03": 904,  "04": 216,  "05": 36,
    "06": 232,  "07": 484,  "08": 1994, "09": 137,  "10": 112,
    "11": 336,  "12": 202,  "13": 173,  "14": 306,  "15": 656,
    "16": 51,   "17": 451,  "18": 349,  "19": 73,   "20": 160,
    "21": 98,   "22": 75,   "23": 251,  "24": 162,  "25": 231,
    "26": 160,  "27": 271,  "28": 3247, "29": 889,  "30": 922,
    "31": 373,  "32": 205,  "33": 496,  "34": 35,   "35": 337,
    "36": 444,  "37": 236,  "38": 354,  "39": 228,  "40": 49,
    "41": 953,  "42": 25,   "43": 333,  "44": 33,   "45": 303,
    "46": 1260, "47": 153,  "48": 428,  "49": 71,   "50": 292,
    "51": 1,    "52": 2,
}

co_served = {
    "01": 4,   "02": 3,   "03": 22,  "04": 6,   "05": 2,
    "06": 6,   "07": 13,  "08": 60,  "09": 6,   "10": 2,
    "11": 13,  "12": 9,   "13": 4,   "14": 11,  "15": 14,
    "16": 1,   "17": 11,  "18": 10,  "19": 3,   "20": 3,
    "21": 3,   "22": 5,   "23": 7,   "24": 3,   "25": 4,
    "26": 5,   "27": 2,   "28": 119, "29": 46,  "30": 21,
    "31": 10,  "32": 5,   "33": 15,  "34": 4,   "35": 8,
    "36": 6,   "37": 6,   "38": 8,   "39": 11,  "40": 1,
    "41": 23,  "42": 1,   "43": 6,   "44": 1,   "45": 12,
    "46": 45,  "47": 8,   "48": 18,  "49": 2,   "50": 10,
    "51": 0,   "52": 0,
}

# DGT CAT censo por provincia [VERIFICADO DB triple: SQL + aritmetica + B6.3]
# source_group='desguace_network' en entity WHERE kind='desguace'
dgt_censo = {
    "01": 9,  "02": 21, "03": 53, "04": 29, "05": 9,
    "06": 33, "07": 24, "08": 76, "09": 19, "10": 25,
    "11": 25, "12": 15, "13": 29, "14": 33, "15": 40,
    "16": 12, "17": 25, "18": 40, "19": 11, "20": 18,
    "21": 17, "22": 8,  "23": 17, "24": 19, "25": 18,
    "26": 7,  "27": 37, "28": 48, "29": 37, "30": 41,
    "31": 19, "32": 12, "33": 35, "34": 7,  "35": 37,
    "36": 34, "37": 19, "38": 15, "39": 16, "40": 6,
    "41": 62, "42": 4,  "43": 27, "44": 9,  "45": 51,
    "46": 60, "47": 18, "48": 29, "49": 14, "50": 20,
    "51": 2,  "52": 1,
}

# Total desguaces en DB (DGT + directorios + OSM) [VERIFICADO DB]
dgt_total = {
    "01": 13, "02": 26, "03": 79, "04": 34, "05": 12,
    "06": 46, "07": 36, "08": 116,"09": 21, "10": 37,
    "11": 33, "12": 19, "13": 43, "14": 42, "15": 70,
    "16": 13, "17": 34, "18": 45, "19": 16, "20": 25,
    "21": 25, "22": 11, "23": 24, "24": 27, "25": 25,
    "26": 10, "27": 60, "28": 98, "29": 61, "30": 63,
    "31": 26, "32": 24, "33": 56, "34": 11, "35": 45,
    "36": 54, "37": 26, "38": 22, "39": 31, "40": 9,
    "41": 86, "42": 5,  "43": 38, "44": 11, "45": 78,
    "46": 99, "47": 24, "48": 37, "49": 20, "50": 26,
    "51": 2,  "52": 1,
}

# Leads sin inventario [VERIFICADO DB: entities sin vehiculo available]
cv_leads_no_inv = {
    "01": 105, "02": 129, "03": 730, "04": 181, "05": 45,
    "06": 201, "07": 449, "08": 1523,"09": 129, "10": 111,
    "11": 330, "12": 184, "13": 139, "14": 212, "15": 348,
    "16": 53,  "17": 295, "18": 281, "19": 76,  "20": 240,
    "21": 122, "22": 103, "23": 193, "24": 177, "25": 177,
    "26": 93,  "27": 146, "28": 1601,"29": 605, "30": 451,
    "31": 212, "32": 104, "33": 310, "34": 46,  "35": 60,
    "36": 286, "37": 114, "38": 58,  "39": 176, "40": 42,
    "41": 504, "42": 32,  "43": 256, "44": 43,  "45": 203,
    "46": 765, "47": 149, "48": 266, "49": 53,  "50": 232,
    "51": 21,  "52": 5,
}

co_leads_no_inv = {
    "01": 10, "02": 12, "03": 65, "04": 23, "05": 11,
    "06": 21, "07": 30, "08": 151,"09": 16, "10": 13,
    "11": 30, "12": 17, "13": 16, "14": 17, "15": 37,
    "16": 8,  "17": 41, "18": 23, "19": 8,  "20": 24,
    "21": 10, "22": 20, "23": 20, "24": 21, "25": 19,
    "26": 16, "27": 10, "28": 177,"29": 40, "30": 49,
    "31": 20, "32": 15, "33": 35, "34": 10, "35": 16,
    "36": 30, "37": 13, "38": 14, "39": 18, "40": 11,
    "41": 36, "42": 7,  "43": 27, "44": 10, "45": 28,
    "46": 73, "47": 18, "48": 33, "49": 10, "50": 14,
    "51": 3,  "52": 4,
}

province_names = {
    "01": "Araba/Alava",      "02": "Albacete",          "03": "Alicante/Alacant",
    "04": "Almeria",           "05": "Avila",              "06": "Badajoz",
    "07": "Balears, Illes",   "08": "Barcelona",          "09": "Burgos",
    "10": "Caceres",           "11": "Cadiz",              "12": "Castellon/Castello",
    "13": "Ciudad Real",       "14": "Cordoba",            "15": "Coruna, A",
    "16": "Cuenca",            "17": "Girona",             "18": "Granada",
    "19": "Guadalajara",       "20": "Gipuzkoa",           "21": "Huelva",
    "22": "Huesca",            "23": "Jaen",               "24": "Leon",
    "25": "Lleida",            "26": "Rioja, La",          "27": "Lugo",
    "28": "Madrid",            "29": "Malaga",             "30": "Murcia",
    "31": "Navarra",           "32": "Ourense",            "33": "Asturias",
    "34": "Palencia",          "35": "Las Palmas",         "36": "Pontevedra",
    "37": "Salamanca",         "38": "S.C. Tenerife",      "39": "Cantabria",
    "40": "Segovia",           "41": "Sevilla",            "42": "Soria",
    "43": "Tarragona",         "44": "Teruel",             "45": "Toledo",
    "46": "Valencia/Valencia", "47": "Valladolid",         "48": "Bizkaia",
    "49": "Zamora",            "50": "Zaragoza",           "51": "Ceuta",
    "52": "Melilla",
}

FACONAUTO_TOTAL = 5358  # [ESTIMADO DECLARADO: instalaciones FACONAUTO 2024]

pop_ine = {
    "01": 334932,  "02": 388344,  "03": 1945642, "04": 748119,  "05": 162212,
    "06": 680168,  "07": 1230518, "08": 5761946, "09": 360143,  "10": 391481,
    "11": 1252213, "12": 603316,  "13": 489888,  "14": 793919,  "15": 1124770,
    "16": 196406,  "17": 804166,  "18": 933163,  "19": 275897,  "20": 724572,
    "21": 524922,  "22": 222418,  "23": 626690,  "24": 455649,  "25": 448282,
    "26": 317053,  "27": 331386,  "28": 6826616, "29": 1714849, "30": 1522671,
    "31": 668338,  "32": 308476,  "33": 1005966, "34": 157564,  "35": 1130177,
    "36": 955148,  "37": 330248,  "38": 1037066, "39": 591888,  "40": 154396,
    "41": 1974837, "42": 89621,   "43": 831956,  "44": 133823,  "45": 713818,
    "46": 2600432, "47": 519124,  "48": 1163844, "49": 170071,  "50": 970049,
    "51": 85144,   "52": 86421,
}
total_pop = sum(pop_ine.values())

gap_causa_map = {
    "51": "Ciudad autonoma; plataformas nacionales sin cobertura sistematica local",
    "52": "Ciudad autonoma; plataformas nacionales sin cobertura sistematica local",
    "05": "Long-tail rural; baja densidad dealers con presencia digital",
    "16": "Long-tail rural; baja densidad dealers con presencia digital",
    "44": "Long-tail rural; baja densidad dealers con presencia digital",
    "21": "Long-tail rural; dealers presentes en plataformas ya capturadas, no en web propia",
    "10": "Long-tail rural + denominador posiblemente inflado (CNAE 4520/4519 alto en Extremadura)",
}


def compute():
    results = []
    for cod in sorted(province_names.keys()):
        prov = province_names[cod]
        den_venta = round(cnae45[cod] * RATIO_451_45)
        num_cv = cv_served[cod]
        num_co = co_served[cod]
        num_venta = num_cv + num_co
        cob_venta = (num_venta / den_venta * 100) if den_venta > 0 else 0

        cv_total = num_cv + cv_leads_no_inv.get(cod, 0)
        co_total = num_co + co_leads_no_inv.get(cod, 0)
        disc_venta = cv_total + co_total
        cob_disc_venta = (disc_venta / den_venta * 100) if den_venta > 0 else 0
        gap_leads = cv_leads_no_inv.get(cod, 0) + co_leads_no_inv.get(cod, 0)

        num_dgt = dgt_censo[cod]
        tot_desg = dgt_total[cod]
        cob_disc_desg = (tot_desg / num_dgt * 100) if num_dgt > 0 else 0

        den_co = round(FACONAUTO_TOTAL * pop_ine[cod] / total_pop)
        cob_co_serv = (num_co / den_co * 100) if den_co > 0 else 0
        cob_co_disc = (co_total / den_co * 100) if den_co > 0 else 0

        if cob_venta >= 85:
            verdict_v = "SELLADO"
        elif cob_venta >= 50:
            verdict_v = "COB-PARCIAL"
        else:
            verdict_v = "GAP-CON-CAUSA"

        verdict_dgt_disc = "SELLADO" if cob_disc_desg >= 100 else "GAP-CON-CAUSA"

        if cod in gap_causa_map:
            gap_causa = gap_causa_map[cod]
        else:
            gap_causa = f"{gap_leads} leads sin E2E scraping (Overture+directorios pendiente)"

        results.append({
            "cod": cod, "prov": prov,
            "num_cv": num_cv, "num_co": num_co, "num_venta": num_venta,
            "den_venta": den_venta, "cob_venta": cob_venta,
            "disc_venta": disc_venta, "cob_disc_venta": cob_disc_venta,
            "gap_leads": gap_leads, "gap_causa": gap_causa,
            "verdict_v": verdict_v,
            "dgt_censo": num_dgt, "dgt_total": tot_desg,
            "cob_disc_desg": cob_disc_desg,
            "verdict_dgt_disc": verdict_dgt_disc,
            "co_disc": co_total, "den_co": den_co,
            "cob_co_serv": cob_co_serv, "cob_co_disc": cob_co_disc,
        })
    return results


def main():
    results = compute()

    n_sellado_v = sum(1 for r in results if r["verdict_v"] == "SELLADO")
    n_parcial_v = sum(1 for r in results if r["verdict_v"] == "COB-PARCIAL")
    n_gap_v = sum(1 for r in results if r["verdict_v"] == "GAP-CON-CAUSA")
    n_dgt_sellado = sum(1 for r in results if r["verdict_dgt_disc"] == "SELLADO")
    tot_venta_serv = sum(r["num_venta"] for r in results)
    tot_disc_venta = sum(r["disc_venta"] for r in results)
    tot_den_venta = sum(r["den_venta"] for r in results)

    print("=== CHECKS ===")
    print(f"  CNAE45 CSV suma: {sum(cnae45.values())}")
    print(f"  DGT censo suma: {sum(dgt_censo.values())}")
    print(f"  venta servida (excl XX): {tot_venta_serv}")
    print(f"  venta servida + XX (206): {tot_venta_serv + 206}")
    print(f"  den venta estimado 52 provs: {tot_den_venta}  (DIRCE 451 nacional: 23085)")
    print(f"  cob servida nacional: {(tot_venta_serv + 206) / 23085 * 100:.1f}%")
    print(f"  cob discovery nacional: {tot_disc_venta / 23085 * 100:.1f}%")
    print(f"  SELLADO venta: {n_sellado_v}/52")
    print(f"  COB-PARCIAL venta: {n_parcial_v}/52")
    print(f"  GAP-CON-CAUSA venta: {n_gap_v}/52")
    print(f"  DGT discovery SELLADO: {n_dgt_sellado}/52")
    print()

    print("=== TABLA ===")
    hdr = ("cod|provincia|cv_serv|co_serv|venta_serv|den_venta_est|"
           "cob_serv%|disc_venta|cob_disc%|gap_leads|verdict_v|"
           "dgt_censo|dgt_total|cob_disc_desg%|verdict_dgt|"
           "co_disc|den_co_est|cob_co_serv%")
    print(hdr)
    for r in results:
        line = (
            f"{r['cod']}|{r['prov']}|{r['num_cv']}|{r['num_co']}|"
            f"{r['num_venta']}|{r['den_venta']}|{r['cob_venta']:.1f}|"
            f"{r['disc_venta']}|{r['cob_disc_venta']:.1f}|{r['gap_leads']}|"
            f"{r['verdict_v']}|{r['dgt_censo']}|{r['dgt_total']}|"
            f"{r['cob_disc_desg']:.0f}|{r['verdict_dgt_disc']}|"
            f"{r['co_disc']}|{r['den_co']}|{r['cob_co_serv']:.1f}"
        )
        print(line)


if __name__ == "__main__":
    main()
