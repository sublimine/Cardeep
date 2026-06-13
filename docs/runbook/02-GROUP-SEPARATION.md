# 02 · GROUP-SEPARATION — el eje que separa las fuentes

> Por qué Tier-1 ≠ OEM-VO ≠ cadenas ≠ rent-a-car ≠ subastas ≠ long-tail. La separación es
> **estructural** (tres columnas de `entity` + `entity_source`), no editorial. Drenado de
> `migrations/0016_tiering_groups.sql` y de las guías de dominio. Cada grupo tiene su capítulo en
> `groups/<grupo>.md`.

---

## 1. El eje de tres columnas

Cada fuente se sitúa por la tupla `(source_group, kind, defense_tier)`:

| Grupo | `source_group` | `kind` entidad-plataforma | `defense_tier` típico | Naturaleza | Capítulo |
|---|---|---|---|---|---|
| **Tier-1 marketplaces** | `marketplace_motor` / `marketplace_generalist` | `plataforma` | `t1_soft` | gigantes C2C+PRO | [tier1-marketplaces](groups/tier1-marketplaces.md) |
| **OEM-VO** | `oem_vo_portal` | `oem_vo_portal` | `t0_open` / `t1_soft` | VO certificado de marca | [oem-vo](groups/oem-vo.md) |
| **Cadenas** | `chain` | `cadena` | `t0_open` | cadenas nacionales VO | [chains](groups/chains.md) |
| **Rent-a-car VO** | `rentacar_vo` | `rent_a_car_vo` | `t1_soft` | ex-flota liquidada | [rentacar-vo](groups/rentacar-vo.md) |
| **Subastas** | `official_registry` | `subasta` (lote) / `plataforma` | `t0_open` / `t1_soft` / `t2_js_challenge` | remarketing B2B/B2C | [subastas](groups/subastas.md) |
| **Long-tail** | `long_tail_web` | `compraventa` / `concesionario_oficial` | `t0_open` / `t1_browser` | web propia del dealer | [long-tail](groups/long-tail.md) |

**Tier-1 separado absolutamente del resto.** El eje `defense_tier` (t0_open..t4_spend_gated) es
independiente del grupo: clasifica el muro técnico, no la naturaleza comercial. Un OEM-VO puede ser
`t0_open` (audi) o `t1_soft` (spoticar); una subasta puede ser `t0_open` (Ayvens), `t1_soft`
(Autorola) o `t2_js_challenge` (BCA).

---

## 2. El invariante común — doble membresía

Todos los grupos comparten el mismo modelo de propiedad (excepto long-tail own-site, que es una
simplificación de él):

- **Ownership** — `vehicle.entity_ulid` apunta SIEMPRE al **dealer / punto de venta / lote
  vendedor**, nunca a una plataforma. Un coche tiene **exactamente 1 dueño**.
- **Membership** — `platform_listing (vehicle_ulid, platform_entity_ulid, …)` es la arista plural
  (0..M): el mismo coche físico puede portar una arista de un grupo y otra de un marketplace sin
  cambiar de dueño.

**La excepción long-tail.** En la web propia del dealer NO hay marketplace intermediario: la web es
la fuente primaria del stock, así que **no hay arista `platform_listing`** — cada coche es
`vehicle.entity_ulid = el dealer`, propiedad singular y directa.

---

## 3. Cómo se aísla cada grupo en la DB (queries de separación)

| Grupo | Query de aislamiento del conjunto-plataforma |
|---|---|
| Tier-1 | `entity.kind='plataforma' AND source_group IN ('marketplace_motor','marketplace_generalist')` |
| OEM-VO | `entity.kind='oem_vo_portal'` → exactamente **14** entidades-portal |
| Cadenas | `entity.kind='cadena'` (4 cadenas) + sucursales `kind='compraventa'` con `source_key ~ '^group_vo_chains'` |
| Rent-a-car | `entity.kind='rent_a_car_vo'` → **3** operadores |
| Subastas | `entity.kind='subasta'` (94 vendedores-lote) + 3 plataformas `role='platform' AND source_group='official_registry'` |
| Long-tail | `entity.website IS NOT NULL AND NOT EXISTS (platform_listing edge)` → own-site cars |

> **Cuidado con `source_group` solo.** Filtrar por `source_group='oem_vo_portal'` devuelve también
> los **concesionarios poseídos** (`kind='compraventa'`), no solo las 14 plataformas. El conjunto de
> PORTALES se aísla con `entity.kind='oem_vo_portal'`. Lo mismo para chains: `source_group='chain'`
> incluye las 186+ sucursales; la CADENA es `kind='cadena'`.

---

## 4. Disjunción validada (ningún coche se comparte entre grupos)

`[VERIFICADO]` en DB viva 2026-06-13, por veredicto `group_vam`:

- **OEM-VO:** Σ de los 14 conteos por portal = 32.360 == `COUNT(DISTINCT vehicle_ulid)` sobre las 14
  aristas = 32.360. Cero coches compartidos entre portales (cada marca publica solo su marca). Solape
  mínimo de 3 dealers (concesionarios que venden bajo >1 programa); los coches NO se comparten.
- **Otros 3 grupos (veredictos 541/542/543):** `DISTINCT(edges ∪ owned)` sobre los tres = **46.201**
  = 39.201 (`chain`) + 215 (`rentacar_vo`) + 6.785 (`subastas`). Las sumas igualan el total distinto
  → ningún vehículo se comparte entre los tres grupos.

---

## 5. El precio-gate honesto (subastas)

La distinción central de subastas frente a los demás grupos: **el precio es de puja con login**, no
retail. Por eso `vehicle.price = NULL` y `platform_listing.platform_price = NULL` en los **6.785**
lotes de subasta (`price_gate='bid_login_gated'`): Ayvens `fixedPrice` solo en tender, BCA
`CanViewPricing=false`, Autorola `loginRequired=true`. El vehículo (make/model/año/km/foto/ubicación)
es público y se cagea; el precio jamás se inventa. Cadenas y rent-a-car publican precio retail real
→ 100 % no-NULL. Detalle en [groups/subastas.md](groups/subastas.md) §precio-gate.
