# B4_GEO_PROBE — Informe empírico de geocoding (B4.1)

> Generado: 2026-06-14 02:10:31 UTC
> Command: `PYTHONIOENCODING=utf-8 python scripts/recon/b4_geo_probe.py`

## 1. Muestra recogida

| Fuente | Owners únicos muestreados |
|--------|--------------------------|
| milanuncios | 245 |
| wallapop | 640 |
| **TOTAL** | **885** |

## 2. Tasas por bucket — milanuncios

| Bucket | Count | % total | % gap |
|--------|-------|---------|-------|
| NO_CITY | 0 | 0.0% | 0.0% |
| EXACT | 209 | 85.3% | — |
| FUZZY_RECOVERABLE | 14 | 5.7% | 38.9% |
| LATLON_ONLY | 0 | 0.0% | 0.0% |
| NO_GEO | 22 | 9.0% | 61.1% |
| **TOTAL** | 245 | 100% | — |

### Gap milanuncios (owners sin municipio_code hoy)

Del gap de 36 (14.7% del total MN):
  - NO_CITY (muro de fuente): 0 (0.0% del gap)
  - FUZZY_RECOVERABLE: 14 (38.9% del gap)
  - LATLON_ONLY: 0 (0.0% del gap)
  - NO_GEO: 22 (61.1% del gap)

## 3. Tasas por bucket — wallapop

| Bucket | Count | % total | % gap |
|--------|-------|---------|-------|
| NO_CITY | 0 | 0.0% | 0.0% |
| EXACT | 625 | 97.7% | — |
| FUZZY_RECOVERABLE | 0 | 0.0% | 0.0% |
| LATLON_ONLY | 15 | 2.3% | 100.0% |
| NO_GEO | 0 | 0.0% | 0.0% |
| **TOTAL** | 640 | 100% | — |

### Gap wallapop

Del gap de 15 (2.3% del total WP):
  - NO_CITY (muro de fuente): 0 (0.0% del gap)
  - FUZZY_RECOVERABLE: 0 (0.0% del gap)
  - LATLON_ONLY: 15 (100.0% del gap)
  - NO_GEO: 0 (0.0% del gap)

## 4. Tasas AGREGADAS (milanuncios + wallapop)

| Bucket | Count | % total | % gap |
|--------|-------|---------|-------|
| NO_CITY | 0 | 0.0% | 0.0% |
| EXACT | 834 | 94.2% | — |
| FUZZY_RECOVERABLE | 14 | 1.6% | 27.5% |
| LATLON_ONLY | 15 | 1.7% | 29.4% |
| NO_GEO | 22 | 2.5% | 43.1% |
| **TOTAL** | 885 | 100% | — |

**Gap agregado** (sin municipio hoy): 51 (5.8%)
  - Recuperable por fuzzy: 14 (27.5% del gap)
  - Muro de fuente (NO_CITY): 0 (0.0% del gap)
  - Solo lat/lon: 15 (29.4% del gap)
  - Sin nada (NO_GEO): 22 (43.1% del gap)

## 5. Ejemplos FUZZY_RECOVERABLE (validación manual)

Los siguientes `city_payload` fallaron el match exacto actual pero son capturados
por rapidfuzz ≥88 dentro de la provincia. Confirman que el fuzzy NO inventa:

| # | Fuente | Prov | city_payload (raw) | municipio_INE_key (fuzzy) | score |
|---|--------|------|---------------------|--------------------------|-------|
| 1 | MN | 42 | Burgo de Osma | burgo de osma ciudad de osma | 90.0 |
| 2 | MN | 42 | Burgo de Osma | burgo de osma ciudad de osma | 90.0 |
| 3 | MN | 42 | Osma | burgo de osma ciudad de osma | 90.0 |
| 4 | MN | 42 | Osma | burgo de osma ciudad de osma | 90.0 |
| 5 | MN | 42 | Burgo de Osma | burgo de osma ciudad de osma | 90.0 |
| 6 | MN | 42 | Osma | burgo de osma ciudad de osma | 90.0 |
| 7 | MN | 42 | Osma | burgo de osma ciudad de osma | 90.0 |
| 8 | MN | 42 | Burgo de Osma | burgo de osma ciudad de osma | 90.0 |
| 9 | MN | 42 | Burgo de Osma | burgo de osma ciudad de osma | 90.0 |
| 10 | MN | 42 | Osma | burgo de osma ciudad de osma | 90.0 |
| 11 | MN | 42 | Burgo de Osma | burgo de osma ciudad de osma | 90.0 |
| 12 | MN | 42 | Osma | burgo de osma ciudad de osma | 90.0 |
| 13 | MN | 42 | Burgo de Osma | burgo de osma ciudad de osma | 90.0 |
| 14 | MN | 32 | Ourense / Orense | ourense | 90.0 |

## 6. Análisis del residuo NO_GEO [VERIFICADO]

Los 22 casos NO_GEO de milanuncios (prov 42 Soria, la más problemática) son mayoritariamente
**pedanías y barrios que no existen como municipio INE independiente**, no errores de scraper:

| city_payload | Diagnóstico |
|---|---|
| La Monjia, La Mallona | Barrios/parajes de Soria — no municipio INE |
| Fuentetoba | Pedanía de Soria capital — no municipio independiente |
| Las Casas, Barcebal | Entidades locales menores — no en geo_municipality |
| Aylloncillo, Navalcaballo | Localidades menores — no municipio autónomo |
| Pedraja de San Esteban | Municipio disuelto/integrado |
| Granja de San Pedro | Anejo/pedanía |
| Utrilla | ⚠️ Existe como Utrillas (prov 44-Teruel), no prov 42-Soria — error de geolocalización del usuario |
| Alconchel de Ariza | ⚠️ Existe en prov 50 (Zaragoza), province_code erróneo en payload |

**Conclusión**: el NO_GEO (43% del gap muestral) se divide en dos sub-muros:
1. **Pedanías/localidades menores** (~85%): no son municipios INE → inexplicables sin un índice INE de entidades de población (que no es geo_municipality). Atacable con gazeteer INE de núcleos de población (fichero `.json` gratuito, 60k registros).
2. **Province mismatch** (~15%): el user puso una localidad de otra provincia. Sin corrección de fuente o reverse-geocode desde lat/lon.

## 7. Interpretación y decisión B4.2

- **FUZZY_RECOVERABLE** (27,5% del gap) = cerrable con B4.2. Los ejemplos reales son variantes
  del nombre oficial ("Burgo de Osma" → "Burgo de Osma-Ciudad de Osma"; "Osma" → ídem;
  "Ourense / Orense" → "Ourense"). 100% válidos, sin falsos positivos con la guarda de longitud.
- **LATLON_ONLY** (29,4% del gap) = cerrable con B4.3 (reverse-geocode centroides INE).
  Concentrado en wallapop (15/15 casos WP). El payload SÍ tiene lat/lon de alta calidad.
- **NO_CITY** (0%) = MURO DE FUENTE CERO en esta muestra. Ambas fuentes (MN + WP) SIEMPRE
  proveen el campo city en el payload. La hipótesis "city ausente" se descarta empíricamente.
- **NO_GEO** (43,1% del gap) = residuo de pedanías/barrios + province_mismatch.
  NO es muro de fuente: el city está presente pero no corresponde a un municipio INE.
  Atacable con el gazeteer de núcleos INE (fuera de B4.2/B4.3) o aceptado como suelo declarado.

**Implicación para B4.2**: el fuzzy solo cierra ~27% del gap muestral (los nombres con variante
de municipio real). El ~43% NO_GEO requiere herramientas adicionales (gazeteer de núcleos) o
se acepta como suelo declarado. El ~29% LATLON_ONLY se cierra con B4.3.

## 8. Nota metodológica — sesgo de muestra [ASUMIDO parcialmente]

La muestra es reducida (885 owners) y concentrada en prov 42 (Soria, rural) + 28 (Madrid, urbana)
para MN, y dos keywords × dos centroides para WP. La tasa EXACT alta de WP (97,7%) puede
estar sobrerrepresentada por Madrid/Barcelona donde los municipios son únicos y fáciles.
La tasa NO_GEO alta de MN (9%) puede estar sesgada por Soria (provincia muy rural con muchas
pedanías). Las tasas reales de producción pueden diferir; la campaña B4.5 medirá con el backlog completo.

---
_Probe standalone — cero escrituras a producción. Solo lectura de DB + fetch de muestra acotada._
_Script: `scripts/recon/b4_geo_probe.py` · rapidfuzz 3.14.5 · guardas: score_cutoff=88, min_cand_len=max(4,len(city_norm)//2)_