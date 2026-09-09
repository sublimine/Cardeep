// Verifies that Cardeep's versioned raw catalog fragments collapse to the
// PRINCIPAL designations stored in submodels.gen.json. All inputs are local on
// purpose: this repository must not depend on another project's checkout or
// Git history.
//   'C 220 d 4MATIC 194cv' -> 'C 220'   |  '320d 163cv' -> '320'
//   'C 63 AMG S 510cv' -> 'C 63 AMG'     |  '40 TDI quattro 190cv' -> '40 TDI'
//   '2.0 TDI 150cv' -> '2.0 TDI'         |  'Pro S 77 kWh 204cv' -> 'Pro S'
// Body-style variants of a model (Clase C / C Cabrio / C Coupé / C Estate) are
// UNIONED under the collapsed base nameplate, matching the curated catalog.
// Fuel/power/drivetrain-specific variants stay for the marketplace advanced filter.
// Canonical map: submodels.gen.json  { "<normBrand>|<modelBaseKey>": ["C 160","C 180",...] }
import { readdirSync, readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const HERE = dirname(fileURLToPath(import.meta.url))
const OUT = join(HERE, 'submodels.gen.json')
const SOURCE_DIR = join(HERE, '.gen')
const canonical = JSON.parse(readFileSync(OUT, 'utf8'))

// ── load local raw fragments ────────────────────────────────────────────────────────
const data = {} // brand -> { model -> [rawSubs] }
for (const file of readdirSync(SOURCE_DIR).filter((name) => name.endsWith('.json')).sort()) {
  const document = JSON.parse(readFileSync(join(SOURCE_DIR, file), 'utf8'))
  for (const brand of document.brands || []) {
    data[brand.name] = data[brand.name] || {}
    for (const model of brand.models || []) {
      data[brand.name][model.name] = data[brand.name][model.name] || []
      data[brand.name][model.name].push(...(model.submodels || []))
    }
  }
}

// ── collapse rule ────────────────────────────────────────────────────────────
const DRIVETRAIN = new Set(['4matic', '4matic+', 'xdrive', 'quattro', '4motion', '4drive', 'awd', 'sdrive', '4x4', '4wd'])
const FUEL = new Set(['d', 'i', 'cdi', 'cgi', 'tdi', 'tsi', 'tfsi', 'fsi', 'bluetec', 'e', 'hybrid', 'ehybrid', 'mpi', 'etsi', 'tgi', 'hdi', 'dci', 'bitdi', 'hsd', 'vvt-i', 'vvti', 'd-4d', 'valvematic', 'mhev', 'phev'])
const TRIM_LEAD = /^(Touring Sports|Touring|Trek|Avant|Sportback|Variant|Allspace|Alltrack|Shooting Brake|Gran Tourer|Gran Coupé|Active Tourer|Beach|Coast|Ocean|Dune|Cross|Kombi|PanAmericana|Aventura|Black Edition|Elegance|IQ\.DRIVE|R-Line|Allroad|Sport|Luxury|Style|Advance|Business|Tech|Edition)\s+/i
const MERC_AMG = new Set(['43', '45', '53', '55', '63', '65'])

const PERF = [
  'John Cooper Works', 'Type R', 'GR Sport', 'GR',
  'RS Q3', 'RS Q8', 'RS3', 'RS4', 'RS5', 'RS6', 'RS7', 'RS',
  'SQ5', 'SQ7', 'SQ8', 'S4', 'S5', 'S6', 'S7', 'S8', 'S3',
  'Clubsport', 'AMG', 'GTI', 'GTE', 'GTD', 'GTS', 'GLI', 'GTX',
  'Cupra', 'VZ', 'Nismo', 'ST', 'e-Hybrid', 'eHybrid',
]
const EV_TRIM = ['Pro S', 'Pure Performance', 'Pure', 'Pro Performance', 'Pro', 'GTX', 'Tour', 'Max', 'Cargo', 'Long Range', 'Standard Range', 'Performance', 'Plaid', 'Dual Motor', 'Single Motor']

// canonical engine-family casing
const CANON = { tsi: 'TSI', etsi: 'eTSI', tdi: 'TDI', tfsi: 'TFSI', fsi: 'FSI', hev: 'HEV', hybrid: 'HEV', hsd: 'HEV', 'vvt-i': 'VVT-I', vvti: 'VVT-I', 'd-4d': 'D-4D', valvematic: 'Valvematic', hdi: 'HDi', dci: 'dCi', bitdi: 'BiTDI', mpi: 'MPI', tgi: 'TGI', t: 'T', v6: 'V6', v8: 'V8', v10: 'V10', v12: 'V12', w12: 'W12' }
const canon = (t) => CANON[t.toLowerCase()] || t.toUpperCase()

function stripPower(s) {
  return s
    .replace(/(\d\.\d)T\b/g, '$1 T')                  // Toyota 1.2T -> 1.2 T
    .replace(/\b\d{2,4}\s?cv\b/gi, ' ')
    .replace(/\b\d{1,3}(?:\.\d+)?\s?kwh\b/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function collapse(rawSub) {
  let s = stripPower(rawSub)
  if (!s) return null

  for (const t of EV_TRIM) {
    const re = new RegExp(`(?:^|\\s)(?:X\\s+)?${t.replace(/[-+]/g, '\\$&')}(?:\\s|$)`, 'i')
    if (re.test(s)) {
      if (!/^[A-Z]{1,3}\s+\d{2,3}\b/.test(s) && !/^\d{3}[a-z]{0,2}\b/.test(s)) return t
    }
  }

  const hasPerf = PERF.some(p => new RegExp(`(?:^|\\s)${p.replace(/[-+.]/g, '\\$&')}(?:\\s|$)`).test(s))
  if (!hasPerf) { let prev; do { prev = s; s = s.replace(TRIM_LEAD, '') } while (s !== prev) }

  let tk = s.split(/\s+/)

  // MERCEDES: class letters + number
  if (/^[A-Z]{1,3}$/.test(tk[0]) && /^\d{2,3}$/.test(tk[1] || '')) {
    const cls = tk[0], num = tk[1]
    if (/amg/i.test(s) || MERC_AMG.has(num)) return `${cls} ${num} AMG`
    return `${cls} ${num}`
  }

  // BMW: 3-digit code optionally + letters
  if (/^\d{3}[a-z]{0,2}$/i.test(tk[0])) return tk[0].replace(/[a-z]+$/i, '')
  if (/^M\d/i.test(tk[0])) return tk[0]

  // PERF sub-brand anywhere
  for (const p of PERF) {
    const re = new RegExp(`(?:^|\\s)(${p.replace(/[-+.]/g, '\\$&')})(?:\\s|$)`)
    if (re.test(s)) return p
  }

  // AUDI modern P-level
  if (/^\d{2}$/.test(tk[0]) && ['30', '35', '40', '45', '50', '55', '60'].includes(tk[0])) {
    const fam = tk.slice(1).find(t => /^(TDI|TFSI|TSI|FSI|HEV|e)$/i.test(t))
    return fam ? `${tk[0]} ${canon(fam)}` : tk[0]
  }

  // DISPLACEMENT: 1.8 / 2.0 / 1.33 (+ first real engine family)
  if (/^\d\.\d{1,2}$/.test(tk[0])) {
    let fam = null
    for (let i = 1; i < tk.length; i++) {
      const low = tk[i].toLowerCase()
      if (DRIVETRAIN.has(low) || low === 'dual') continue
      if (/^(tdi|tsi|tfsi|fsi|hev|hybrid|hsd|d-4d|vvt-i|vvti|valvematic|hdi|dci|bitdi|mpi|etsi|tgi|t|v6|v8|v10|v12|w12)$/i.test(tk[i])) { fam = tk[i]; break }
    }
    return fam ? `${tk[0]} ${canon(fam)}` : tk[0]
  }

  // FALLBACK
  const kept = tk.filter(t => {
    const low = t.toLowerCase().replace(/[+]/g, '')
    if (DRIVETRAIN.has(low)) return false
    if (FUEL.has(low)) return false
    if (/^\d{2,4}cv$/i.test(t)) return false
    return true
  })
  return kept.join(' ').trim() || null
}

// ── model base key: strip "Clase" prefix + trailing body-style words ─────────
const BODY = /\s+(Cabriolet|Cabrio|Coupé|Coupe|Sedan|Sedán|Berlina|Estate|Touring|Variant|Avant|Sportback|Allroad|Shooting Brake|Gran Coupé|Gran Turismo|Gran Tourer|Active Tourer|Sports Tourer|Allspace|Fastback|Liftback|Hatchback|SW|Break|Kombi|Familiar|Long|LWB|SWB|4 puertas)$/i
function modelBaseKey(model) {
  let m = model.replace(/^Clas?se?\s+/i, '')
  let prev; do { prev = m; m = m.replace(BODY, '') } while (m !== prev)
  return m.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '')
}
const normBrand = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '')

// ── apply + UNION across body variants + dedupe ──────────────────────────────
const acc = {} // key -> {set, list}
for (const [brand, models] of Object.entries(data)) {
  for (const [model, subs] of Object.entries(models)) {
    if (!subs.length) continue
    const key = `${normBrand(brand)}|${modelBaseKey(model)}`
    if (!acc[key]) acc[key] = { set: new Set(), list: [] }
    for (const raw of subs) {
      const c = collapse(raw)
      if (c && !acc[key].set.has(c)) { acc[key].set.add(c); acc[key].list.push(c) }
    }
  }
}

// These keys are intentionally curated in the canonical map because duplicate
// raw fragments disagree. Keep the list explicit so new drift still fails.
const CURATED_OVERRIDE_KEYS = new Set([
  'abarth|124spider', 'abarth|500', 'abarth|500c', 'abarth|595', 'abarth|595c',
  'cadillac|ats', 'cadillac|cts', 'cadillac|escalade', 'cadillac|xt4', 'cadillac|xt5',
  'cadillac|xt6', 'chevrolet|aveo', 'chevrolet|camaro', 'chevrolet|captiva',
  'chevrolet|corvette', 'chevrolet|cruze', 'chevrolet|orlando', 'chevrolet|trax',
  'cupra|terramar', 'seat|mii', 'volkswagen|up',
])
const EXPECTED_OMITTED_RAW_KEYS = new Set(['seat|miielectric'])
const mismatches = []
const missing = []
let n = 0
for (const [key, value] of Object.entries(acc)) {
  n += value.list.length
  if (!(key in canonical)) missing.push(key)
  else if (JSON.stringify(canonical[key]) !== JSON.stringify(value.list)) mismatches.push(key)
}
const unexpectedMissing = missing.filter((key) => !EXPECTED_OMITTED_RAW_KEYS.has(key))
const absentMissing = [...EXPECTED_OMITTED_RAW_KEYS].filter((key) => !missing.includes(key))
const unexpectedOverrides = mismatches.filter((key) => !CURATED_OVERRIDE_KEYS.has(key))
const absentOverrides = [...CURATED_OVERRIDE_KEYS].filter((key) => !mismatches.includes(key))
if (unexpectedMissing.length || absentMissing.length || unexpectedOverrides.length || absentOverrides.length) {
  throw new Error(
    `Catalog reconciliation drifted; unexpected-missing=[${unexpectedMissing.join(', ')}] ` +
    `absent-missing=[${absentMissing.join(', ')}] ` +
    `unexpected-overrides=[${unexpectedOverrides.join(', ')}] ` +
    `absent-overrides=[${absentOverrides.join(', ')}]`
  )
}
console.log(
  `verified ${Object.keys(acc).length} locally sourced model keys / ${n} collapsed submodels; ` +
  `${mismatches.length} explicit curated overrides; ${missing.length} intentional omission; ` +
  `${Object.keys(canonical).length} canonical keys`
)

const checks = [
  ['Mercedes', 'Clase C'], ['Mercedes', 'Clase E'], ['Mercedes', 'GLC'],
  ['BMW', 'Serie 3'], ['Audi', 'A4'], ['Volkswagen', 'Golf'], ['Toyota', 'Corolla'], ['SEAT', 'León'],
]
for (const [b, m] of checks) {
  const k = `${normBrand(b)}|${modelBaseKey(m)}`
  console.log(`\n${b} ${m} -> ${canonical[k]?.length ?? 0}:\n  ${canonical[k]?.join(' · ') ?? '(none)'}`)
}
