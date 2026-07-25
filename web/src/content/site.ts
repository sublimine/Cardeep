/**
 * Every word on the public site, in one typed module.
 *
 * Rules that govern this file live in `web/CONTENT.md`. The two that matter most:
 * nothing here is invented — no customer logos, testimonials or headshots — and
 * no internal vocabulary reaches the reader (no delta, VAM, receta, Tier-1).
 *
 * Figures come from `services/api/stats.py` against the live index and are stamped
 * with a date, because the public site does not yet talk to the API.
 */

export const BRAND = {
  name: 'Cardeep',
  tagline: 'El mercado del coche en España, entero y en vivo.',
  email: 'hola@cardeep.es',
  indexStamp: 'Índice actualizado · julio 2026',
} as const;

/* ------------------------------------------------------------------ figures */

export const FIGURES = {
  /** Resolved points of sale with at least one available car. */
  dealers: { value: '19.000', prefix: '+', label: 'puntos de venta activos' },
  vehicles: { value: '1,5', suffix: ' M', label: 'coches vivos en el índice' },
  provinces: { value: '52', label: 'provincias cubiertas' },
  municipalities: { value: '8.000', prefix: '+', label: 'municipios' },
  sources: { value: '7', label: 'plataformas indexadas' },
} as const;

/* --------------------------------------------------------------------- nav */

export const NAV_LINKS = [
  { label: 'Índice', href: '#indice' },
  { label: 'Producto', href: '#producto' },
  { label: 'Precios', href: '#precios' },
  { label: 'API', href: '#api' },
] as const;

export const PRIMARY_CTA = 'Pedir acceso';

/* -------------------------------------------------------------------- hero */

export const HERO = {
  badgeBrand: 'Cardeep',
  badgeNote: 'Índice nacional en vivo',
  badgeHref: '#indice',
  title: 'El mercado del coche en España, entero y en vivo.',
  subtitle:
    'Cada punto de venta, cada coche, cada movimiento de precio. Sin muestras ni estimaciones: el mercado real, actualizado mientras lo miras.',
  cta: PRIMARY_CTA,
  watermark: 'Cardeep',
} as const;

/* ------------------------------------------------------------ source wall */

/** The platforms the index reads. Framed as coverage, never as clients. */
export const SOURCES = [
  { name: 'coches.net', mark: 'coches', accent: '.net' },
  { name: 'AutoScout24', mark: 'AutoScout', accent: '24' },
  { name: 'Wallapop', mark: 'Wallapop', accent: '' },
  { name: 'Milanuncios', mark: 'Milanuncios', accent: '' },
  { name: 'Autocasión', mark: 'Autocasión', accent: '' },
  { name: 'coches.com', mark: 'coches', accent: '.com' },
  { name: 'motor.es', mark: 'motor', accent: '.es' },
] as const;

export const SOURCE_WALL_KICKER = 'Indexamos donde vive el mercado';

/* -------------------------------------------------------------------- bento */

export const BENTO = {
  heading: 'Deja de mirar el mercado por una rendija',
  feature: {
    title: 'Índice nacional',
    body: 'Cada compraventa, cada concesionario, cada garaje de pueblo. Con todo su stock y su ficha, ordenados hasta el último municipio.',
    cta: 'Ver el índice',
  },
  movements: {
    title: 'Movimientos del mercado',
    items: [
      { kind: 'precio', text: 'Bajada de precio · −1.200 €' },
      { kind: 'venta', text: 'Vendido · 41 días en stock' },
      { kind: 'stock', text: 'Stock nuevo · 6 unidades' },
    ],
  },
  coverage: { title: 'Cobertura de España' },
  price: {
    title: 'Precio real',
    query: 'Golf 2.0 TDI 150 CV · 2021 · Madrid',
    resultTitle: 'Tu anuncio',
    resultMeta: '18.900 € · 34 días publicado',
    resultVerdict: '1.340 € por encima de la mediana del mercado',
  },
  more: { title: 'Encargos, publicación y terminal' },
} as const;

/* ------------------------------------------------- product surfaces (grid) */

export type Surface = {
  id: string;
  title: string;
  body: string;
  tags: string;
  image: string;
  href: string;
};

export const SURFACES_HEADING = 'Lo que hay dentro';

export const SURFACES: readonly Surface[] = [
  {
    id: 'indice',
    title: 'Índice nacional',
    body: 'Cada punto de venta de España con su inventario entero, su ficha y su código propio.',
    tags: 'Ficha por punto de venta · Inventario completo',
    image: '/shots/indice.webp',
    href: '#indice',
  },
  {
    id: 'precio',
    title: 'Precio real',
    body: 'El precio al que se vende de verdad. La distribución completa del mercado y tu posición exacta dentro de ella.',
    tags: 'Distribución de mercado · Tu posición',
    image: '/shots/precio.webp',
    href: '#producto',
  },
  {
    id: 'cobertura',
    title: 'Cobertura',
    body: 'Provincia, comarca y municipio. Sabemos qué está cerrado y qué seguimos ampliando, y te lo enseñamos.',
    tags: '52 provincias · +8.000 municipios',
    image: '/shots/cobertura.webp',
    href: '#cobertura',
  },
  {
    id: 'historial',
    title: 'Historial',
    body: 'La vida entera de un coche desde que apareció: cada precio que tuvo y cada foto que cambió.',
    tags: 'Altas y bajas · Cada cambio de precio',
    image: '/shots/historial.webp',
    href: '#producto',
  },
  {
    id: 'oportunidades',
    title: 'Oportunidades',
    body: 'Los coches que piden menos de lo que valen, ordenados por margen, zona y segmento.',
    tags: 'Puntuación por anuncio · Margen y zona',
    image: '/shots/oportunidades.webp',
    href: '#producto',
  },
  {
    id: 'terminal',
    title: 'Terminal',
    body: 'El mercado tratado como un mercado: curva por modelo, buscador de señales y ritmo de venta.',
    tags: 'Curva por modelo · Screener',
    image: '/shots/terminal.webp',
    href: '#producto',
  },
];

/* ------------------------------------------------ capabilities (carousel) */

export type Capability = {
  id: string;
  mark: string;
  title: string;
  body: string;
};

export const CAPABILITIES_HEADING = 'Un índice que no se cae';
export const CAPABILITIES_CTA = 'Hablar con nosotros';

export const CAPABILITIES: readonly Capability[] = [
  {
    id: 'cobertura',
    mark: 'Cobertura',
    title: 'Sabemos qué falta',
    body: 'No decimos “casi todo”. Cada provincia tiene su estado, y si una zona no está cerrada, aparece como no cerrada.',
  },
  {
    id: 'contraste',
    mark: 'Contraste',
    title: 'Ningún número solo',
    body: 'Un dato no llega a tu pantalla hasta que se confirma por caminos distintos al que lo produjo.',
  },
  {
    id: 'historial',
    mark: 'Historial',
    title: 'Nada se borra',
    body: 'Cada precio que existió sigue existiendo mañana, aunque el anuncio haya desaparecido del portal.',
  },
  {
    id: 'alertas',
    mark: 'Alertas',
    title: 'Si algo falla, lo sabes',
    body: 'Salta un aviso con el origen exacto, el sistema se repara solo y el índice sigue en pie.',
  },
  {
    id: 'api',
    mark: 'API',
    title: 'Abierto por diseño',
    body: 'Todo lo que ves en pantalla está disponible por API para llevarlo a tu propio sistema.',
  },
];

/* ----------------------------------------------------------------- scaling */

export const SCALING = {
  heading: 'Construido para el mercado español',
  counterValue: 19000,
  counterSuffix: '+',
  counterLabel: 'puntos de venta activos',
  body: 'De la plataforma nacional al garaje de un pueblo de ochocientos habitantes. Si vende coches, está en el índice.',
  teamKicker: 'Un mercado entero, provincia a provincia',
  teamCta: PRIMARY_CTA,
  quote:
    '“Una muestra te da una media. El mercado entero te da una decisión. Por eso Cardeep no muestrea: lo indexa todo.”',
  quoteAuthor: 'Cardeep',
  quoteRole: 'Principio de diseño',
  sourcesLabel: 'Fuentes que indexamos',
} as const;

/* -------------------------------------------------------------- comparison */

export const COMPARISON = {
  heading: 'Cardeep frente a mirar portales a mano',
  us: 'Con Cardeep',
  them: 'A mano, portal por portal',
  rows: [
    { label: 'Alcance', us: 'Todo el mercado en un índice', them: 'Los portales que te da tiempo a mirar' },
    { label: 'Precio', us: 'La distribución real del mercado', them: 'Lo que pide el de al lado' },
    { label: 'Historial', us: 'Cada cambio desde el primer día', them: 'Lo que recuerdas' },
    { label: 'Oportunidades', us: 'Ordenadas por margen', them: 'Las que aciertas a ver' },
    { label: 'Cobertura', us: '52 provincias, hasta el municipio', them: 'Tu zona' },
    { label: 'Publicación', us: 'Un stock, todos los portales', them: 'Uno a uno, a mano' },
    { label: 'Decisión', us: 'Con el mercado delante', them: 'A ojo' },
  ],
  freeLabel: 'Empieza gratis',
  primaryCta: PRIMARY_CTA,
  secondaryCta: 'Ver precios',
  perks: [
    { title: 'Sin instalación', body: 'Entras y está todo dentro. No hay que migrar nada ni conectar tu gestión.' },
    { title: 'Sin permanencia', body: 'Empiezas en el plan gratuito y subes cuando el índice te haya pagado el mes.' },
    { title: 'Sin ruido', body: 'Solo lo que mueve tu negocio. Ni una gráfica de más.' },
  ],
} as const;

/* ----------------------------------------------------------------- pricing */

export type Plan = {
  id: string;
  name: string;
  badge: string;
  badgeTone: 'quiet' | 'good';
  title: string;
  titleAccent: string;
  price: string;
  period: string;
  cta: string;
  features: readonly string[];
};

export const PRICING = {
  heading: 'Planes claros',
  note: '¿Dudas? Escríbenos a',
  noteCta: 'hablamos',
  plans: [
    {
      id: 'starter',
      name: 'Starter',
      badge: 'Gratis, para siempre',
      badgeTone: 'good',
      title: 'Tu gestión diaria completa',
      titleAccent: 'sin pagar nada',
      price: '0 €',
      period: '',
      cta: 'Empezar gratis',
      features: [
        'Inventario, clientes, ofertas y facturas sin límite',
        'Ficha de vehículo completa',
        'Tu precio frente a la mediana del mercado',
        'Resumen de historial por coche',
        'Asistente, chat y calendario',
        '1 usuario',
      ],
    },
    {
      id: 'scale',
      name: 'Scale',
      badge: 'El salto',
      badgeTone: 'good',
      title: 'El mercado real',
      titleAccent: 'delante de ti',
      price: '249 €',
      period: '/mes',
      cta: 'Pedir acceso',
      features: [
        'Todo lo de Starter',
        'Precio real: la distribución entera, no un punto',
        'Movimientos en vivo: altas, bajas y cambios de precio',
        'Provincia, comarca y municipio',
        'Comparativa con Europa',
        'Historial completo por coche',
        'Origen de cada dato, auditable',
        '5 usuarios',
      ],
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      badge: 'A medida',
      badgeTone: 'quiet',
      title: 'Comprar mejor,',
      titleAccent: 'con el margen calculado',
      price: 'A medida',
      period: '',
      cta: 'Hablar con nosotros',
      features: [
        'Todo lo de Scale',
        'Oportunidades puntuadas anuncio por anuncio',
        'Ranking con filtros de margen, zona y segmento',
        'Alertas en el momento',
        'API con cuota alta',
        'Gestor de cuenta',
        'Usuarios ilimitados',
      ],
    },
  ] satisfies readonly Plan[],
  annualNote: 'Scale sale a 199 €/mes pagando el año.',
} as const;

/* ----------------------------------------------------------------- mission */

export const MISSION = {
  kicker: 'La misión',
  imageAlt: 'Puntos de venta de coches sobre el mapa de España',
  paragraphs: [
    'Hoy nadie tiene el mercado del coche español entero. Los portales solo ven lo suyo. Las tasadoras trabajan con muestras. Y tú compites contra precios que no puedes ver.',
    'Cardeep existe para arreglar eso: encontrar todos los puntos de venta de España, sacar su inventario completo, guardarlo con su historial y servirlo vivo. De la plataforma nacional al garaje perdido en la montaña.',
  ],
  closing:
    'No es un panel bonito montado sobre datos de otros. Es el mapa, hecho desde cero y verificado dato a dato.',
  stats: [
    { value: '+19.000', label: 'puntos de venta' },
    { value: '1,5 M', label: 'coches' },
    { value: '52', label: 'provincias' },
  ],
} as const;

/* -------------------------------------------------------------- principles */

export type Principle = { id: string; mark: string; title: string; body: string };

export const PRINCIPLES_HEADING = 'Cómo trabajamos';
export const PRINCIPLES_CTA = 'Hablar con nosotros';

export const PRINCIPLES: readonly Principle[] = [
  {
    id: 'contraste',
    mark: '01',
    title: 'Ningún número sin contrastar',
    body: 'Si un dato no se confirma por dos caminos distintos, no te lo enseñamos. Preferimos un hueco declarado a una cifra bonita.',
  },
  {
    id: 'entero',
    mark: '02',
    title: 'El mercado entero, no una muestra',
    body: 'Una muestra te da una media. El mercado entero te da una decisión. Por eso indexamos hasta el último garaje.',
  },
  {
    id: 'historial',
    mark: '03',
    title: 'El historial no se borra',
    body: 'Cada precio que existió sigue existiendo. Aunque el anuncio ya no esté en ningún portal.',
  },
  {
    id: 'alertas',
    mark: '04',
    title: 'Si algo falla, lo sabes',
    body: 'Con el origen exacto y sin que tengas que preguntar. El sistema se repara solo y el índice no se cae.',
  },
  {
    id: 'datos',
    mark: '05',
    title: 'Tus datos son tuyos',
    body: 'Tu inventario y tu cartera de clientes no alimentan el índice público ni acaban en manos de nadie.',
  },
];

/* --------------------------------------------------------------------- faq */

export const FAQ = {
  heading: 'Preguntas frecuentes',
  note: '¿Te queda alguna? Escríbenos a',
  cardTitle: '¿Quieres verlo con tus coches delante?',
  cardBody: 'Te enseñamos el índice con tu provincia y tu stock, y decides si te sirve.',
  cardCta: PRIMARY_CTA,
  items: [
    {
      q: '¿De dónde salen los datos?',
      a: 'Del mercado abierto: los portales donde los profesionales publican y las webs de los propios puntos de venta. Nada privado y nada comprado a terceros.',
    },
    {
      q: '¿Cada cuánto se actualiza?',
      a: 'De forma continua. El índice no se regenera una vez al día: va incorporando altas, bajas y cambios de precio según ocurren, y guarda cada uno con su fecha.',
    },
    {
      q: '¿Cubre toda España?',
      a: 'Las 52 provincias y más de 8.000 municipios. Cada zona tiene su estado de cobertura y, si una no está cerrada del todo, lo verás marcado en vez de escondido.',
    },
    {
      q: '¿Me sirve si vendo pocos coches?',
      a: 'Sobre todo si vendes pocos. Cuando cada unidad cuenta, equivocarte en el precio de compra o tener un coche parado dos meses se nota mucho más.',
    },
    {
      q: '¿Tengo que cambiar mi forma de trabajar?',
      a: 'No. El plan gratuito es un gestor completo, y si ya usas otro programa puedes quedarte solo con la parte de mercado.',
    },
    {
      q: '¿Puedo llevar los datos a mi sistema?',
      a: 'Sí. Todo lo que ves en pantalla está disponible por API, con tu cuota según el plan.',
    },
    {
      q: '¿Mis coches y mis clientes se comparten?',
      a: 'No. Tu inventario privado y tu cartera son tuyos, no entran en el índice público y no se ceden a nadie.',
    },
    {
      q: '¿Cuándo puedo entrar?',
      a: 'Estamos abriendo por invitación mientras cerramos cobertura provincia a provincia. Pide acceso y te avisamos en cuanto la tuya esté lista.',
    },
  ],
} as const;

/* ------------------------------------------------------------------ footer */

export const FOOTER = {
  ctaTitle: 'El mercado entero.\nEn tu pantalla.',
  blurb: 'El mapa vivo del mercado del coche en España.',
  cta: PRIMARY_CTA,
  watermark: 'Cardeep',
  columns: [
    {
      title: 'Producto',
      links: [
        { label: 'Índice nacional', href: '#indice' },
        { label: 'Precio real', href: '#producto' },
        { label: 'Cobertura', href: '#cobertura' },
        { label: 'Oportunidades', href: '#producto' },
        { label: 'Terminal', href: '#producto' },
      ],
    },
    {
      title: 'Empezar',
      links: [
        { label: 'Precios', href: '#precios' },
        { label: 'Pedir acceso', href: '#precios' },
        { label: 'API', href: '#api' },
        { label: 'Preguntas frecuentes', href: '#faq' },
      ],
    },
    {
      title: 'Cardeep',
      links: [
        { label: 'La misión', href: '#mision' },
        { label: 'Cómo trabajamos', href: '#principios' },
        { label: 'Cobertura por provincia', href: '#cobertura' },
        { label: 'Contacto', href: 'mailto:hola@cardeep.es' },
      ],
    },
    {
      title: 'Legal',
      links: [
        { label: 'Privacidad', href: '#legal' },
        { label: 'Condiciones', href: '#legal' },
        { label: 'Cookies', href: '#legal' },
      ],
    },
  ],
  legal: '© 2026 Cardeep · Todos los derechos reservados',
} as const;
