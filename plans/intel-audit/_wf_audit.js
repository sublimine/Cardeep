// Fase 2 — auditoria atomica por empresa (109 del shortlist).
// Cada agente investiga a fondo por web, ESCRIBE companies/<slug>.md (informe completo)
// y devuelve un resumen compacto (campos atomicos + placement + gaps) para la sintesis.
export const meta = {
  name: 'intel-company-audit',
  description: 'Auditoria atomica de 109 empresas de inteligencia de automocion (productos/campos/entrega/precio/placement/gaps)',
  phases: [
    { title: 'Cargar', detail: 'leer el shortlist de 109' },
    { title: 'Auditoria', detail: '1 agente/empresa, investigacion web profunda multi-fuente, escribe .md' },
  ],
}
const REPO = 'C:/Users/elias/projects/cardeep/plans/intel-audit'
const LIST_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['companies'],
  properties: { companies: { type: 'array', items: {
    type: 'object', additionalProperties: false,
    properties: { name: { type: 'string' }, url: { type: 'string' }, region: { type: 'string' }, subdomain: { type: 'string' }, priority: { type: 'number' } } } } },
}
const SUMMARY = {
  type: 'object', additionalProperties: false,
  required: ['slug', 'name', 'products', 'all_fields', 'gaps', 'placement', 'sources'],
  properties: {
    slug: { type: 'string' }, name: { type: 'string' }, subdomain: { type: 'string' },
    products: { type: 'array', items: { type: 'object', additionalProperties: false, properties: { name: { type: 'string' }, n_fields: { type: 'number' } }, required: ['name'] } },
    all_fields: { type: 'array', items: { type: 'string' } },
    delivery: { type: 'array', items: { type: 'string' } },
    pricing: { type: 'string' },
    placement: { type: 'array', items: { type: 'object', additionalProperties: false, properties: { datum: { type: 'string' }, where: { type: 'string' } }, required: ['datum', 'where'] } },
    differentials: { type: 'array', items: { type: 'string' } },
    gaps: { type: 'array', items: { type: 'string' } },
    sources: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string' },
  },
}
const slugify = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50)
phase('Cargar')
const loaded = await agent(
  `Lee el fichero ${REPO}/_audit_input.json (array JSON de empresas) con la tool Read y devuelve {companies:[...]} con name,url,region,subdomain,priority de CADA entrada, verbatim. No omitas ninguna.`,
  { label: 'load-shortlist', phase: 'Cargar', schema: LIST_SCHEMA })
const companies = (loaded && loaded.companies) || []
log(`Shortlist cargado: ${companies.length} empresas a auditar`)
phase('Auditoria')
const promptFor = (co) => {
  const slug = slugify(co.name)
  return `Auditoria ATOMICA, nivel institucional de elite, de la empresa de datos/inteligencia de automocion "${co.name}" (web: ${co.url || 'buscala'}; subdominio: ${co.subdomain}).
Carga herramientas web con ToolSearch (query "select:WebSearch,WebFetch" y tambien "exa search semantic") y USALAS A FONDO: navega su web, paginas de PRODUCTO, datasheets, docs de API, paginas de precios, casos de uso, notas de prensa, demos y reviews. NADA superficial ni generico.
Extrae con maximo detalle:
- Identidad (grupo/owner, HQ, fundacion), categorias, clientes objetivo, cobertura (paises), scope (nuevo/usado, tipos de vehiculo).
- PRODUCTOS: por cada producto, su lista ATOMICA de campos/metricas concretas (ej.: valor residual %, retail/trade price, days-to-sell, market days supply, price-to-market %, indice demanda/oferta, curva de depreciacion, ajuste por km, specs/equipamiento, atributos por VIN, historico de siniestros/km, etc.). Quiero TODOS los campos, no categorias vagas.
- Metodologia/fuentes de datos, ENTREGA (API/dashboard/portal web/informe/feed/Excel/integracion DMS), modelo de PRECIO si es descubrible.
- PLACEMENT (clave para cardeep): DONDE en su UI/web colocan CADA metrica importante (ficha de coche, panel/overview de mercado, comparador, alertas, informe PDF...) — describe la seccion/pantalla. Es el patron que cardeep copiara para ubicar cada dato.
- DIFERENCIAL (lo que ofrece y otras no) y GAPS (lo que NO ofrece).
Verifica con >=2 fuentes (URLs) cuando puedas; marca lo no verificado, JAMAS inventes.
OBLIGATORIO: escribe el informe COMPLETO en markdown estructurado en el fichero ${REPO}/companies/${slug}.md usando la tool Write (secciones: Identidad, Cobertura, Productos+campos, Metodologia, Entrega, Precio, Placement, Diferencial, Gaps, Fuentes).
Devuelve ADEMAS el resumen del schema (slug="${slug}"; all_fields = lista plana de TODOS los campos atomicos que ofrece).`
}
const audits = await parallel(companies.map((co) => () => agent(promptFor(co), { label: 'audit:' + (co.name || '?'), phase: 'Auditoria', schema: SUMMARY })))
const ok = audits.filter(Boolean)
log(`Auditadas ${ok.length}/${companies.length} empresas (informes en companies/*.md)`)
return { audited: ok.length, total: companies.length, audits: ok }
