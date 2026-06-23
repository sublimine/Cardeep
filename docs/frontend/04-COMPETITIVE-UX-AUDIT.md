# CARDEEP — Manual maestro de UX competitiva (síntesis de 17 dossiers)

> Síntesis de 15 plataformas Tier-1 europeas de automoción + Rockstar GTA VI + motionsites.ai.
> Atom-level, en español. Este documento DIRIGE el front de CARDEEP. Coherente con
> `01-DESIGN.md` (tokens), `02-REFERENCES.md` (tablero del owner) y `00-PLAN.md` (fases).
> Datos reales de CARDEEP citados: censo vivo (~2,35M coches / ~436k entidades), delta completo
> (altas/bajas/cambio precio/cambio foto + historial), geo país→provincia→ciudad, `cdp_code` por
> dealer, `ulid` por vehículo, veredicto VAM, segmentación por `kind` (concesionario/compraventa/
> garaje/desguace/plataforma/subasta) y Tier-1, mapa de cobertura 3D (SpainMap.tsx).
> Mandato del owner: nivel agencia, oscuro/cinematográfico, motion-rich, CADA botón con lógica.

---

## 0. Lectura estratégica del campo (qué aprende CARDEEP)

**El hallazgo central de los 15 marketplaces: TODOS son blancos, densos, funcionales y carecen de
motion cinematográfico.** AutoScout24, mobile.de, AutoTrader, CarGurus, Carwow, Cinch, heycar,
LaCentrale, Leboncoin, Aramisauto, AutoTrack, Carvago, Coches.net, Wallapop, Milanuncios —
todos sacrifican experiencia sensorial por velocidad de carga y densidad. Ninguno tiene 3D,
scroll-driven storytelling ni un hero que no sea un formulario de búsqueda sobre blanco.

Esto define la doble estrategia de CARDEEP:
1. **IGUALAR o SUPERAR su rigor de datos** (price-rating, hit-count en vivo, filtros densos,
   alertas, deep-links) — porque el usuario español está entrenado en estos patrones.
2. **DOMINAR la dimensión donde todos son débiles: la experiencia.** Robar las técnicas
   cinematográficas de GTA VI y motionsites (los únicos dos referentes de ejecución de élite del
   set) y aplicarlas a un producto de datos. Ese es el foso defensivo de marca.

**La ventaja estructural de CARDEEP que ningún competidor tiene:** cobertura del 100% del mercado.
Donde ellos muestran inventario parcial, CARDEEP muestra el censo entero — el mapa, el contador,
el price-rating, el observatorio de precios, las páginas de entidad. La exhaustividad verificada
(no la curaduría exclusiva tipo heycar, que quebró) es el moat. heycar perdió £30M curando;
Carvago/Carwow ganan con escala. CARDEEP gana con escala TOTAL.

---

## 1. PATRONES GANADORES POR SUPERFICIE (consolidado)

### (a) LANDING / HOME

| # | Patrón | Quién lo hace mejor | Adopción CARDEEP |
|---|--------|---------------------|------------------|
| 1 | **Hero = buscador, no imagen** (Airbnb/Booking-ización) | LaCentrale (rebrand Seenk 2024), AutoScout24, Aramisauto | SUPERAR: hero = **mapa 3D vivo de España** (el producto ES el hero) + barra flotante |
| 2 | **Contador de inventario dinámico en el CTA** ("Mostrar 253.302 resultados") | Coches.net, Cinch ("Search 9.283 cars"), Carvago ("1.048.411 Offers") | ROBAR: "Explorar 2.347.891 coches" — el volumen como declaración de dominio |
| 3 | **Toggle Comprar/Vender en el hero** (bifurca flujos sin navegar) | Coches.net | ADAPTAR: "Buscar coche / Soy profesional" (B2C vs B2B en 0 clics) |
| 4 | **Quick-filter pills de intención** bajo el hero | Carwow, Cinch, CarGurus (lifestyle), AutoTrader (AI categories) | ROBAR: pills por `kind` (Concesionarios/Compraventas/Particulares/Desguaces/Subastas) + por provincia |
| 5 | **Grid visual de carrocerías + marcas** (entrada sin saber marca) | AutoScout24 (8 tiles), AutoScout24.it, heycar, CarGurus | ROBAR, adaptado: tiles por carrocería + acceso por CCAA/provincia (geo es el core) |
| 6 | **Dual sell-funnel** (rápido vs precio máximo) | AutoScout24, mobile.de, LaCentrale, AutoScout24.it | ROBAR + tercera vía: "Vende a concesionario verificado" (red de entidades VAM) |
| 7 | **Trust architecture en capas** (rating + sello duro + freshness) | Carwow (Trustpilot + Top Rated + FCA), Carvago, AutoTrack (ANWB+BOVAG+RDW) | ROBAR: cobertura verificada + nº puntos de venta + **última sync del inventario** |
| 8 | **Observatorio de precios público** (autoridad editorial + SEO) | LaCentrale, Leboncoin, AutoScout24.it, CarGurus (Price Trends) | ROBAR: **primer observatorio de precios VO de España por provincia→ciudad** (CARDEEP tiene el censo) |
| 9 | **Comparativa directa vs competidores** en la landing | Carwow (vs Motorway/WeBuyAnyCar) | ROBAR: "CARDEEP tiene el 100% del mercado vs el inventario parcial de los demás" |
| 10 | **Tiles temáticos como puertas de entrada segmentadas** por precio/estado | Cinch, Aramisauto | ROBAR: "Recién publicados hoy", "Precio bajado", "Stock verificado hoy", "Delta de ayer: +X" |

**Mejor landing global del set automoción:** ninguna destaca (todas funcionales). La referencia de
ejecución es GTA VI (§3). El consenso de dominio es LaCentrale + Coches.net por la lógica de funnel.

### (b) MARKETPLACE / BÚSQUEDA

| # | Patrón | Quién lo hace mejor | Adopción CARDEEP |
|---|--------|---------------------|------------------|
| 1 | **Filtros sidebar-izquierda densos siempre visibles** (desktop) | mobile.de (30+), AutoScout24 (23 dims), AutoScout24.it, Cinch, heycar | ROBAR pero con JERARQUÍA: 6 filtros de alta conversión arriba (marca→modelo, precio, km, combustible, provincia, tipo vendedor) + avanzados colapsados |
| 2 | **Hit-count en vivo por faceta** ("423.422 Offerte") | AutoScout24.it, mobile.de, Coches.net, Cinch | ROBAR: contador que se actualiza al filtrar — mata el dead-end |
| 3 | **Make→Model dependiente** (modelo se activa al elegir marca) | Wallapop, mobile.de, todos | ROBAR (patrón base esperado) |
| 4 | **Filtro por cuota mensual** (no solo precio total) | Coches.net (pionero ES), AutoTrader (toggle €total↔€/mes), heycar, Cinch | ROBAR: toggle precio total ↔ €/mes estimado |
| 5 | **Filtro por tipo de vendedor** (Particular/Profesional) | Wallapop, Leboncoin, Milanuncios, todos | SUPERAR: filtro por `kind` granular (6 tipos, no binario) — ventaja directa |
| 6 | **Etiqueta DGT como filtro de primera clase** | Coches.net, Wallapop | ROBAR: filtro + badge en card (0/ECO/C/B) |
| 7 | **Toggle "solo ofertas/precio bajado"** como filtro prominente | Cinch ("Only show discounted (1.951)"), Carvago ("Best deal"), AutoScout24.it (filtro valutazione) | ROBAR: toggle "Solo precio bajado" + "Solo buen precio vs mercado" (CARDEEP tiene el delta y el VAM) |
| 8 | **Grid view por defecto + infinite scroll** (validado por eye-tracking) | AutoTrader (30h eye-tracking), Wallapop, Cinch | ROBAR el grid; CUIDADO con infinite scroll puro → preferir paginación + URL persistente (ver anti-patrón Milanuncios) |
| 9 | **Vista mapa de resultados** | mobile.de (la tiene); Leboncoin/AutoScout24/Coches.net NO la tienen (debilidad) | SUPERAR: **split mapa+lista es el core** (#49/#52/#84 del tablero). Mayor debilidad del campo = mayor fortaleza CARDEEP |
| 10 | **Guardar búsqueda + alerta** (push/email cuando entra match) | TODOS (AutoTrader, mobile.de, LaCentrale, Leboncoin…) | ROBAR + POTENCIAR: con delta en tiempo real, "3 nuevos Golf TDI en Madrid desde tu última visita" |
| 11 | **Ordenación por deal-quality por defecto** (no por revenue) | CarGurus (declarado como integridad) | ROBAR: orden por relevancia + opción "mejor precio vs mercado primero" |
| 12 | **URL semántica por faceta** (SEO long-tail auto-generado) | Wallapop (/coches/eco/madrid), Milanuncios, AutoScout24.it, LaCentrale | ROBAR: cada combinación geo×marca×modelo×kind = landing indexable. **Estado persistente en URL** (corrige el bug de Milanuncios) |

**Mejor marketplace del set:** mobile.de (profundidad de filtros) + AutoTrader (rigor data-driven,
grid eye-tracked) + LaCentrale (IA conversacional). El split mapa+lista es territorio libre.

### (c) CARD DE RESULTADO

**Anatomía consolidada (la card ganadora = unión de las mejores):**

| Elemento | Fuente del mejor patrón | En CARDEEP |
|----------|-------------------------|------------|
| **Carrusel de fotos navegable DENTRO de la card** (indicador 1/N) | Wallapop, AutoTrader (4 visibles en grid) | ROBAR: swipe sin entrar a la ficha — sube conversión pre-clic |
| **Price-rating badge** (semáforo vs mercado) | mobile.de, AutoScout24, CarGurus, AutoTrader (5 niveles), AutoScout24.it (diario), heycar | ROBAR — es el patrón #1 del campo. CARDEEP: VAM → badge (buen/justo/caro vs mediana provincial) |
| **Delta €/€ vs mercado explícito** ("1.767€ por debajo del mercado") | CarGurus (el nº absoluto, no solo %) | ROBAR: convierte el dato abstracto en argumento |
| **Precio oversized** (ancla visual) | Wallapop, todos | ROBAR (extra-bold, lección de toda la auditoría) |
| **Cuota mensual** ("desde 199€/mes") | Coches.net, heycar (inline), Cinch, AutoTrader | ROBAR: estimación inline en la card |
| **Specs en una línea iconificada** (Combustible · Cambio · CV · Año · Km) | Wallapop, todos | ROBAR: máxima densidad / mínimo espacio |
| **Badge de tipo de vendedor** (visualmente diferenciado) | Leboncoin, Milanuncios, Wallapop | SUPERAR: badge por `kind` (6 tipos) + Tier-1 |
| **Etiqueta DGT** (icono color) | Coches.net | ROBAR |
| **Freshness / delta badge** ("Nuevo hoy" / "Lleva X días" / "Precio bajado") | Milanuncios, Cinch ("Currently reserved"), CarGurus (days on market) | ROBAR: con `first_seen`/`last_seen` reales → "Nuevo hoy" o "Precio bajado ayer" |
| **Sin logo de dealer en la card** (eye-tracking: el ojo no lo mira) | AutoTrader (lo eliminó tras 30h eye-tracking) | ROBAR: card 100% vehicle-centric, sin ruido de branding |
| **Icono favorito (corazón)** | Todos | ROBAR |

**Mejor card:** AutoTrader (eye-tracked, vehicle-centric, price-indicator) + Wallapop (carrusel inline).

### (d) FICHA DE VEHÍCULO (`/vehicle/{ulid}`)

| Elemento | Fuente del mejor patrón | En CARDEEP |
|----------|-------------------------|------------|
| **Galería rica + 360°** (interior/exterior) | AutoTrack (1º NL en 360°, SpinCar), AutoScout360°, Carvago (50+ fotos por zona), LaCentrale (hasta 50) | SUPERAR: 360° NATIVO con Three.js/R3F (ya en stack), sin coste por anuncio ni dependencia externa |
| **CTA + precio STICKY** (rail derecho) | mobile.de, cars.com | ROBAR |
| **Price-rating + delta vs mercado** con explicación | CarGurus, AutoScout24, todos | ROBAR (VAM visible) |
| **Price History / days-on-market** | CarGurus, Cinch | ROBAR + SUPERAR: CARDEEP trackea delta completo → gráfico de historial de precio real como arma de negociación |
| **Specs table completa** + "ver todas" (progressive disclosure) | AutoTrader, Carwow, Carvago | ROBAR |
| **Calculadora de financiación inline** (cuota recalculada en vivo) | Aramisauto, AutoTrader (Zuto), heycar, Carvago, LaCentrale (LOA) | ROBAR (estimación con partners ES) |
| **Historial de vehículo integrado** (DGT/ITV/cargas) | LaCentrale (HistoVec gob FR), Leboncoin (Autoviza), AutoTrack (Carfax+NAP), AutoTrader (Vehicle Check) | ROBAR: integrar/enlazar informe DGT-ES ("CARDEEP Report") — brecha enorme en ES |
| **Deep-link al anuncio original** | (patrón propio CARDEEP, mandato del owner) | OBLIGATORIO: cada vehículo con URL directa a la fuente real |
| **Card de entidad/vendedor** (rating, distancia, link a perfil) | mobile.de, AutoScout24, todos | ROBAR: link a `/dealer/{cdp}` |
| **Contacto: WhatsApp primero** | AutoScout24 (>100K anuncios), AutoScout24.it | ROBAR: en ES penetración WhatsApp ~90% → primer CTA, no el formulario |
| **Breadcrumb + similares** | Todos | ROBAR |

**Mejor ficha:** AutoTrader (Deal Builder + Vehicle Check) + Carvago (CarAudit™ shareable) + LaCentrale (HistoVec).

### (e) PÁGINA DE DEALER / ENTIDAD (`/dealer/{cdp}`)

| Elemento | Fuente del mejor patrón | En CARDEEP |
|----------|-------------------------|------------|
| **Inventario completo filtrable inline** (mismo sidebar que SERP) | heycar, AutoScout24, mobile.de, Coches.net | ROBAR: filtros completos dentro del perfil de entidad |
| **Identidad humanizada** (manager nombrado, abierto/cerrado en vivo, servicios con icono) | Aramisauto (subdominio agences., manager visible) | ROBAR: datos SIRENE/identidad por entidad, estado, servicios |
| **Reviews post-contacto automáticas** (solo quien contactó valora) | mobile.de, Coches.net (1 semana), AutoScout24.it (60k reviews), AutoTrader (Highly Rated, auditado CMA), CarGurus | ROBAR: review vinculada a evento — elimina reviews de relleno |
| **Badge de acreditación con criterio duro** | AutoTrader (Highly Rated: ≥10 reviews, ≥4★, 95% respuesta), Carwow (Top Rated ≤0.5% quejas) | ROBAR: "CARDEEP Verificado" = mayor cobertura inventario + identidad SIRENE + historial limpio |
| **Score/ranking de entidad** (actividad, rotación, transparencia precio) | (territorio propio: VAM + delta) | SUPERAR: rankings de entidades por velocidad de rotación, transparencia de precio, cobertura |
| **Dashboard B2B** (métricas, AI pricing, leads) | AutoScout24 (HändlerIQ), mobile.de (Sale Probability AI), Coches.net (Price Radar), LaCentrale (Pilot), AutoTrack (Analytics) | ROADMAP B2B: panel de inteligencia para dealers (VAM + trends por provincia) = producto B2B natural |
| **Delta/historial de inventario** de la entidad | (territorio propio CARDEEP) | SUPERAR: "este dealer subió 12 coches esta semana, bajó precio en 4" |

**Mejor dealer-page:** AutoTrader (Highly Rated auditado) + LaCentrale (Pilot como producto B2B
independiente) + Aramisauto (humanización). Nota: Cinch/Carvago NO tienen dealer-page (modelo D2C)
— CARDEEP SÍ la tiene y es ventaja diferencial (indexa ~436k entidades).

---

## 2. CATÁLOGO DE BOTONES + LÓGICA (exhaustivo, por superficie)

> Regla del owner: **cada botón tiene una lógica detrás, nada decorativo.** Cada uno declara su acción.

### LANDING

| Botón | Lógica |
|-------|--------|
| **Explorar [N] coches** (CTA hero, contador dinámico) | Submit del buscador flotante → `/explore` con params en URL. El nº se actualiza al teclear marca/provincia. Volumen = validación de dominio antes del clic. |
| **Toggle Buscar / Soy profesional** | Bifurca B2C (buscador) vs B2B (acceso a dashboard de entidad / API) sin navegar. |
| **Pills de `kind`** (Concesionarios / Compraventas / Particulares / Desguaces / Subastas / Plataformas) | Cada pill = filtro pre-aplicado a `/explore?kind=X`. Segmenta audiencia sin formulario. |
| **Tiles de provincia / CCAA** (sobre el mapa 3D) | Click en provincia del mapa → `/explore?provincia=X`. El mapa ES el navegador geográfico. |
| **Tiles temáticos** (Nuevos hoy / Precio bajado / Stock verificado hoy) | Filtros de delta pre-aplicados. Explotan el dato vivo que nadie más tiene. |
| **Ver observatorio de precios** | → `/datos` (subsite): índice de precios VO por provincia/ciudad. Autoridad editorial + SEO. |
| **Estimar mi coche** (CTA secundario vendedor) | Entrada matrícula → valoración VAM instantánea. Top-of-funnel del lado vendedor. |
| **Acceso anticipado / Solicitar demo** (wishlist-first, de GTA VI) | Captura email/interés antes de exponer la API completa. Lead magnet, no conversión prematura. |

### MARKETPLACE / EXPLORE

| Botón | Lógica |
|-------|--------|
| **Aplicar filtro** (cada faceta) | Re-ejecuta query, actualiza hit-count en vivo y la URL (estado persistente — corrige bug Milanuncios). |
| **Toggle precio total ↔ €/mes** | Cambia el paradigma de búsqueda a cuota mensual (mercado ES financia ~60%). |
| **Toggle "Solo precio bajado"** | Filtra por delta de precio negativo reciente. Conversión pura. |
| **Toggle "Solo buen precio vs mercado"** | Filtra por veredicto VAM favorable. Cierra el loop valoración↔búsqueda. |
| **Toggle mapa ↔ lista** | El diferenciador. Mapa vivo de resultados al lado de la lista rica. |
| **Ordenar por** | Relevancia (default) / precio asc-desc / €mes / km / año / **mejor precio vs mercado** / recién publicado. |
| **Guardar búsqueda + crear alerta** | Persiste filtros → push/email con delta ("X nuevos desde tu visita"). Retención sin coste de adquisición. |
| **Limpiar todo** | Reset de filtros en 1 acción. Evita abandono por sobre-filtrado → 0 resultados. |
| **Favorito (corazón)** en card | Guarda en garaje personal + activa alerta de bajada de precio del vehículo. |
| **Carrusel ◄ ►** en card | Navega fotos sin entrar a la ficha. |

### FICHA DE VEHÍCULO (`/vehicle/{ulid}`)

| Botón | Lógica |
|-------|--------|
| **Contactar por WhatsApp** (CTA primario sticky) | Abre WhatsApp con mensaje pre-cargado del vehículo. Fricción mínima en mobile ES. |
| **Ver teléfono** | Número oculto → revelado al clic (anti-scraping + mide intención real). |
| **Ver anuncio original** (deep-link) | Abre la URL de la fuente real. Mandato del owner: cada coche con enlace directo. |
| **Calcular financiación** | Calculadora inline: entrada + plazo → cuota recalculada en vivo. Precio total → cuota asequible. |
| **Ver CARDEEP Report** (historial) | Informe DGT/ITV/cargas + historial de precio propio. Trust-builder, posible upsell/partner. |
| **Ver historial de precio** (gráfico) | Días en mercado + bajadas. Arma de negociación. CARDEEP trackea el delta completo. |
| **360° (arrastrar para girar)** | Viewer R3F nativo. Sustituto digital del test drive físico. |
| **Guardar en garaje** (favorito) | Lista personal + alerta de bajada de precio. |
| **Compartir** | WhatsApp / email / link. |
| **Ver vendedor** | → `/dealer/{cdp}`. |

### PÁGINA DE DEALER / ENTIDAD (`/dealer/{cdp}`)

| Botón | Lógica |
|-------|--------|
| **Filtrar inventario** (sidebar inline) | Mismo motor de filtros del SERP dentro del perfil de entidad. |
| **Seguir a este vendedor** | Push cuando la entidad publica nuevo stock. Fidelización sin coste de adquisición. |
| **Contactar entidad** (WhatsApp/teléfono/form) | Lead. Dispara review post-contacto automática a la semana. |
| **Cómo llegar** | Mapa + ruta (Google Maps). Cierra el funnel offline. |
| **Ver ranking / score VAM** | Muestra veredicto VAM, transparencia de precio, velocidad de rotación de la entidad. |
| **Acceder al panel (B2B)** | Para la propia entidad: dashboard de inteligencia (VAM, trends, leads). Roadmap monetización. |

### VENDEDOR (flujo de venta, futuro)

| Botón | Lógica |
|-------|--------|
| **Estimar mi coche** | Matrícula → VAM instantánea. Lead de vendedor. |
| **Publicar / Vender a particular** | Flujo C2C (auto-relleno por matrícula). |
| **Vender a concesionario verificado** | Subasta inversa contra la red de entidades VAM (tercera vía propia). |

---

## 3. LO CINEMATOGRÁFICO — 6 técnicas a adoptar (de GTA VI + motionsites)

> Los dos únicos referentes de ejecución de élite del set. CARDEEP es producto de datos: el motion
> debe ser DELIBERADO (dirigir la atención al dato), no decorativo. Regla operativa: si quitas la
> animación y el significado no cambia, la animación no debe existir (GTA VI).

| # | Técnica | Origen | Aplicación CARDEEP | Stack |
|---|---------|--------|--------------------|-------|
| 1 | **Scroll-as-storytelling** (eje vertical único, sin paradoja de elección) | GTA VI | Los primeros ~100vh cuentan QUÉ es CARDEEP (censo vivo del 100% de España) antes de ofrecer la herramienta. Convierte visitantes en creyentes. | GSAP ScrollTrigger + Lenis |
| 2 | **Video/mapa scrubbing** (el scroll controla el avance frame a frame) | GTA VI (pinned video) | El scroll enciende el mapa 3D de España provincia a provincia por cobertura (GAP→PARCIAL→SELLADO). El usuario "dirige la cámara" sobre el censo. SpainMap.tsx ya existe → sincronizar a scroll. | GSAP `scrub:true` + R3F |
| 3 | **Pinned sections** (el contenedor se congela mientras el scroll interno ejecuta timeline) | GTA VI | Sección del mapa 3D "pinned": el usuario explora la cobertura sin que el viewport se mueva. Reveals de stats por capas. | GSAP pin + ScrollTrigger |
| 4 | **SplitText char-by-char + parallax por capas** (reveals con stagger y profundidad) | GTA VI, motionsites | Titulares y precios oversized aparecen letra a letra con easing confiado (lento, no frenético). Fondos a velocidad distinta del texto → profundidad 3D sin 3D real. | GSAP SplitText |
| 5 | **Jerarquía de card en 4 pasos** (identidad→emoción→info→acción) | GTA VI (character cards) | Cada card de entidad/vehículo: (1) imagen cinematográfica (2) nombre/tipo (3) dato clave en 1 línea (4) CTA único. Cero ruido decorativo. | CSS + reveal scroll |
| 6 | **Tipografía custom + paleta cinematográfica oscura** (cada detalle intencionado) | GTA VI (Colophon custom font, neón sunset), motionsites | Base casi-negra (`#0A0E17`) deja brillar el 3D y los datos. Display con carácter (Clash/Satoshi), datos en mono (Geist Mono — terminal de inteligencia). Acento cian eléctrico `#35E0D0` como "señal de datos" ownable. | Tokens de `01-DESIGN.md` |

**Disciplina anti-slop (del tablero + GTA VI):** movimiento confiado y lento (mapea a la estética
sunset/command-center), no microinteracciones frenéticas. Compatibilidad como decisión de producto:
priorizar la experiencia máxima (Chrome 115+ para scroll-driven CSS) con degradación elegante.
GTA VI aceptó esa brecha conscientemente.

**Lección de retención de Carvago/AutoTrader vía la lente cinematográfica:** un video real de 2 min
"cómo CARDEEP indexa España" (spiders → datos → VAM) como prueba de autenticidad del inventario =
el equivalente al video de delivery de Carvago / al trailer de GTA VI.

---

## 4. ARQUITECTURA DE INFORMACIÓN DE CARDEEP

### Sitemap

```
/                          Landing — hero mapa 3D + buscador flotante + stats vivas + observatorio teaser
/explore                   Marketplace — split MAPA ↔ LISTA, filtros sidebar, hit-count vivo, URL persistente
  /explore?provincia=…&kind=…&marca=…&modelo=…&precio=…&dgt=…&vendedor=…   (facetas → URL semántica indexable)
/dealer/:cdp               Entidad — identidad SIRENE + inventario filtrable + delta/historial + score VAM + mapa + reviews
/vehicle/:ulid             Vehículo — galería+360° + precio oversized + price-rating(VAM) + specs + historial Δ + financiación + deep-link + CTA sticky
/datos                     Subsite — Observatorio de precios por CCAA→provincia→ciudad (autoridad editorial + SEO masivo)
/cobertura                 Subsite — desglose de cobertura por geo × kind (el "only-in-leonida" de CARDEEP, para analistas/B2B)
/vender                    Flujo vendedor (futuro) — estimar (VAM) → publicar C2C / vender a entidad verificada
/pro                       Acceso B2B — dashboard de inteligencia para entidades (VAM, trends, leads, API)
/guardados                 Garaje personal — favoritos + búsquedas guardadas + alertas (delta)
```

### Landing — desglose sección a sección

1. **Nav minimalista** (colapsada, no roba protagonismo — patrón GTA VI). Logo · Explorar · Datos · Pro · Acceder.
2. **Hero full-viewport: mapa 3D de España** (SpainMap.tsx) extruido por cobertura (rampa
   GAP `#F0556B` → PARCIAL `#F5B33C` → SELLADO `#35E0D0`). Barra de búsqueda flotante encima. Stats
   animadas que respiran: "2.347.891 coches · ~436.000 puntos de venta · 52 provincias". Contador =
   CTA implícito (Carvago/Coches.net).
3. **Scroll-storytelling** (GTA VI técnica 1+2): al hacer scroll, el mapa se enciende provincia a
   provincia (scrubbing) mientras un titular SplitText cuenta el QUÉ. Pinned hasta completar España.
4. **Quick-filter pills de `kind`** + tiles temáticos de delta ("Nuevos hoy", "Precio bajado").
5. **Dual funnel**: "Buscar coche" vs "Soy profesional" / "Estimar mi coche".
6. **Trust en capas**: cobertura verificada + nº entidades + **última sync** (freshness signal único).
7. **Observatorio teaser** (autoridad): mini-gráfico de precio medio VO ES + CTA a `/datos`.
8. **Comparativa vs competidores**: "100% del mercado vs inventario parcial" (Carwow).
9. **Footer SEO** + acceso a subsites + apps (futuro).

### /explore — desglose

- **Layout split** (#49/#52/#84 del tablero): sidebar-izq filtros · centro lista de cards · der/toggle mapa vivo.
- **Filtros jerarquizados**: 6 de alta conversión arriba (marca→modelo, precio €total/€mes, km,
  combustible, provincia→ciudad, `kind`) + avanzados colapsados (año, cambio, CV, color, DGT, Tier-1,
  freshness, distancia/radio).
- **Hit-count en vivo** por faceta. **URL persistente** (query params + restauración al volver).
- **Cards**: carrusel inline · foto · precio oversized · **price-rating VAM** · **delta €/€ vs mercado** ·
  €/mes · specs-1-línea · badge `kind`+Tier-1 · DGT · freshness/delta · favorito. Sin logo dealer (eye-tracking).
- **Toggle mapa↔lista** + ordenación + guardar búsqueda/alerta.

### /dealer/:cdp — desglose

- Cabecera: identidad (nombre, `cdp_code` en mono, `kind`, provincia/ciudad, SIRENE/identidad, estado).
- **Score VAM** + badge "CARDEEP Verificado" (criterio duro).
- Inventario completo con sidebar de filtros inline (heycar).
- **Delta/historial de inventario** de la entidad (territorio propio: "+12 esta semana, −4 precio").
- Reviews post-contacto + mapa de ubicación + CTAs (seguir, contactar, cómo llegar).

### /vehicle/:ulid — desglose

- Galería full-width + **360° R3F nativo**.
- Precio oversized + **price-rating VAM** + delta vs mercado.
- Specs table (progressive disclosure) + etiqueta DGT.
- **Historial de precio** (gráfico, delta completo) + días en mercado.
- Calculadora financiación inline (€/mes).
- **CARDEEP Report** (DGT/ITV/historial).
- **Deep-link al anuncio original** (mandato owner).
- Card de entidad (link `/dealer/:cdp`).
- **CTA sticky rail-derecha**: WhatsApp (primario) · Ver teléfono · Guardar · Compartir.
- Vehículos similares.

---

## 5. TABLA RESUMEN POR PLATAFORMA (posicionamiento + mejor patrón robable)

| Plataforma | País | Posicionamiento | Mejor patrón robable |
|------------|------|-----------------|----------------------|
| **AutoScout24** | DE/pan-EU | El mayor marketplace de Europa (40M usuarios/mes) | **Price Rating Badge** en cada card + dual sell funnel + WhatsApp nativo |
| **mobile.de** | DE | Nº1 alemán (~1,4M anuncios), rebrand 2025 | **Preisbewertung** (semáforo 70+ factores) + "Parkplatz" (favoritos con identidad) + Sale Probability AI |
| **Coches.net** | ES | Líder ES (11,9M visitas/mes) | **Contador dinámico en el CTA** + **filtro por cuota mensual** (pionero ES) + toggle Comprar/Vender + IA NET |
| **Wallapop** | ES | C2C nº1 (15M usuarios) | **Carrusel inline en card** + chips curados + URL semántica por faceta + alertas |
| **Milanuncios** | ES | Clasificado generalista (22M/mes) | **Alertas + ver-teléfono-oculto + SEO geo×marca**. EVITAR: pérdida de filtros al volver (URL persistente) |
| **AutoTrader UK** | UK | Líder UK (84M/mes) | **Price Indicator 5 niveles** + grid eye-tracked + **eliminar logos dealer en card** + Deal Builder |
| **CarGurus** | UK/US | Transparencia de precio (Deal Rating) | **Deal Rating 5 colores + delta €/€ explícito** + orden por deal-quality + Price History |
| **Carwow** | UK | Subasta inversa, ciclo completo | **Subasta inversa como narrativa** + quick-filter pills + comparativa directa vs competidores |
| **Cinch** | UK | D2C "faff-free", 100% online | **CTA con conteo en vivo** + toggle "solo ofertas" + identidad tonal con concepto rector |
| **heycar** | UK/DE | Curado premium (quebró: lección) | **Precio €/mes inline + AI natural-language search**. APRENDER: exhaustividad > curaduría exclusiva |
| **LaCentrale** | FR | Nº1 auto FR (9M/mes), 55 años | **Cote gratuita como gancho** + **asistente IA conversacional** + Observatoire de precios + Pilot B2B |
| **Leboncoin** | FR | Clasificado dominante (27M/mes) | **Filtro pago-seguro elegible** + badge precio mercado + Email Spotlight. SUPERAR: NO tiene mapa nativo |
| **Aramisauto** | FR/ES | D2C reacondicionado industrial | **Posicionamiento de corte** + página de agencia humanizada (manager nombrado) + callback embebido |
| **AutoScout24.it** | IT | El mayor de Europa (IT) | **Badge de precio algorítmico diario** + filtro por valutazione + arquitectura SEO por geo |
| **AutoTrack** | NL | Mayor NL, triple sello ANWB+BOVAG+RDW | **360° nativo** + multiselect en filtros + badge verificación institucional + búsqueda por matrícula |
| **Carvago** | EU cross-border | Intermediario con riesgo propio (CarAudit™) | **Informe brandeable shareable (CarAudit™→CARDEEP Report)** + contador inventario + cuota en card |
| **GTA VI** | ref. cinematográfica | Landing-film de scroll más cinematográfica del mundo | **Scroll-as-storytelling + video/mapa scrubbing + pinned sections + SplitText + motion restringido** |
| **motionsites.ai** | ref. ejecución | Estándar de motion-rich agency-grade | Calidad de motion deliberado + tipografía custom + paleta cinematográfica (ver `03-MOTIONSITES-AUDIT.md`) |

---

## 6. SÍNTESIS FINAL — el ADN de CARDEEP

CARDEEP no clona a nadie. **Roba el rigor de datos del campo (price-rating VAM, hit-count vivo,
filtros densos jerarquizados, alertas con delta, deep-links, observatorio de precios) y lo monta
sobre la experiencia cinematográfica que NINGÚN competidor tiene** (mapa 3D scrubbed, scroll-
storytelling, motion deliberado, dark luxury). La exhaustividad del censo (100% de España) es el
moat estructural; el split mapa+lista y el 360° nativo son las fortalezas donde el campo es más
débil; el price-rating VAM es el puente visible hacia la capa de inteligencia de mercado.

**El estándar:** rigor de mobile.de + AutoTrader, transparencia de CarGurus, autoridad editorial de
LaCentrale, ejecución cinematográfica de GTA VI. Todo sobre un dato que solo CARDEEP posee entero.
