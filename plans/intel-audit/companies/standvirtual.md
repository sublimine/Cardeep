# Standvirtual — Auditoría atómica

> **slug:** `standvirtual` · **subdominio de audit:** `portal-insights` · **web:** https://www.standvirtual.com/ · **valuador:** https://www.standvirtual.com/avaliacao-do-carro · **grupo:** https://www.olxgroup.com/brands/standvirtual/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[V]` = verificado leyendo la fuente (≥2 donde se indica), `[A]` = asumido/inferido (marcado), `[NV]` = no verificado / ausente. Nada inventado.
> **Método:** WebSearch + WebFetch sobre web propia, OLX Group / Prosus newsroom, prensa PT (pcguia, executivedigest, posvenda, dmark) y caso de diseño de Netguru (OLX Motors Europe) + **navegación en vivo con Playwright** del valuador, la lista de resultados y una **ficha de anuncio real** (Volvo XC 40, ID8PUoP7) para capturar verbatim el indicador de precio, el histórico de precio, los specs y el bloque de servicios. El sitio bloquea `curl` (CloudFront 403); las páginas se leyeron vía WebFetch y navegador real.
>
> **Veredicto express:** Standvirtual es **el marketplace nº 1 de coche en Portugal** (OLX Group → Prosus/Naspers; >6M visitas/mes, >40.000 vehículos, líder >18 años). Su "inteligencia de datos" **NO es una guía de tasación clásica** (Eurotax/Ganvam) ni un censo: es **inteligencia derivada de su propio inventario vivo portugués**, idéntica en arquitectura a la familia **OLX Motors Europe** (Otomoto-PL, Autovit-RO, La Centrale-FR), construida por el **Lisbon Data Science Team**. Tres capas: **(1) Price Evaluation** — indicador de **3 niveles** (`Abaixo da média` / `Dentro da média` / `Acima da média`) que compara el precio del anuncio con ofertas similares, **embebido en 5 superficies** (Listing Page, Ad Details, Posting Form, My Ads y **Sourcing Insights**); **(2) Avaliação do carro** — valuador B2C gratis (matrícula/VIN o specs → **intervalo de precio** estimado sobre **275.000+ anuncios**, recalibrado cada 2 semanas); **(3) AutoIQ** — el **"motors dealer operating system"** del grupo (pricing recommendations, **sales-velocity forecast** = días-a-venta + demand analytics, dealer insights, lead dashboard, descripción/imagen/vídeo por IA) que se despliega sobre Standvirtual, más **AutoGPT** (asistente agéntico sobre ChatGPT). Patrón directo para cardeep: **badge de precio de 3 niveles + histórico de precio ("Preço mais baixo" / bajada en €) en cada ficha, valuador de rango público, y un portal de profesional con pronóstico de venta + demanda por modelo + posición en búsqueda**.

> **Aviso de desambiguación (CRÍTICO):**
> - **Standvirtual** = marca de coche en **Portugal**, operada por **Fixeads S.A. / OLX Portugal, S.A.** → **OLX Group** → **Prosus N.V.** → **Naspers** (~57% de Prosus). [V] **NO confundir** con Adevinta (mobile.de) ni con AutoScout24 (Hellman&Friedman).
> - **OLX Motors Europe** = la plataforma compartida que agrupa **Otomoto (Polonia)**, **Autovit (Rumanía)**, **Standvirtual (Portugal)** y (desde 2025) **La Centrale (Francia)**. El motor de **Price Evaluation** y los productos de IA (**AutoIQ**, **AutoGPT**) son del grupo y se reusan marca-a-marca; muchas funciones se anuncian primero en **Otomoto** y luego **rolan a Standvirtual**. Marco como [V Standvirtual] lo confirmado en `standvirtual.com` y como [V grupo / rollout pendiente] lo verificado solo en Otomoto/OLX a nivel de plataforma.
> - **AutoTrader (Sudáfrica)** es OTRO brand de OLX Group; sus módulos "Comments Generator / Image Management / **Dealer Insights**" (techfinancials, CLAIM AI) son de **AutoTrader SA**, no necesariamente del stack PT — **no los atribuyo a Standvirtual** salvo lo que AutoIQ replica explícitamente.
> - **portal-insights.standvirtual.com** EXISTE (CloudFront `143.204.55.x`) pero responde **HTTP 403** a tráfico anónimo → es el **portal de insights del profesional tras login**, no servible público. La cuenta de profesional vive en `standvirtual.com/contapessoal/*` (redirige a `/authentication`). [V curl + Playwright]

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **Standvirtual** — "O Nº 1 em Carros" | [V ≥2: home, olxgroup brand] |
| Categoría | **Marketplace de clasificados de vehículos** (C2C + B2C/B2B) **con capa de datos/inteligencia**: price-evaluation, valuador, sales-velocity (días-a-venta), demand analytics, financiación, IA de anuncios | [V] |
| Owner / grupo | **OLX Group** (vertical motors) | [V ≥2: olxgroup brand, onlinemarketplaces] |
| Operador legal | **Fixeads S.A.** / **OLX Portugal, S.A.** (app id `com.fixeads.standvirtual`) | [V ≥2: Play Store pkg, Racius, Heróis PME] |
| Propiedad última | **Prosus N.V.** (división internacional de **Naspers**; Naspers ≈57% de Prosus) | [V ≥2: onlinemarketplaces, AIM] |
| Fundación | **2004** (como proyecto en la empresa "Fixe.com", fundadores **Miguel Mascarenhas** y Miguel Monteiro) → grupo **FixeAds** constituido **2007** | [V ≥2: Heróis PME, racius] |
| Entrada de Naspers | **2012** (Naspers entra en el capital de FixeAds; le confía la gestión de **OLX Portugal**; lanzan **Imovirtual**) | [V: Heróis PME] |
| HQ | **Lisboa, Portugal** | [V: olxgroup brand] |
| Antigüedad | **>18 años** operando | [V: olxgroup brand] |
| Visitas | **>6 millones de personas/mes** | [V: olxgroup brand] |
| Inventario | **>40.000 vehículos** anunciados | [V: olxgroup brand] |
| Marcas hermanas (FixeAds/PT) | **OLX, Standvirtual, Imovirtual, Coisas, Faturavirtual** | [V: Heróis PME] |
| Facturación Standvirtual | **No desglosada** (consolida en OLX Group / Prosus) | [NV — GAP, ver §9] |
| Reconocimiento | "Cinco Estrelas" / "Escolha do Consumidor" / mejor sitio de Comércio Automóvel Online (premios PT) | [V ≥2: doit.pt, imagensdemarca] |

### Contexto corporativo OLX Group (nivel grupo, no Standvirtual aislado) [V]
- **OLX Group**: marketplaces de motors/inmobiliario/empleo/bienes con **~29M usuarios/mes en 8 países** (foco Centro-Este de Europa) y **~60M de listings diarios en 7 mercados**. [V ≥2: Prosus La Centrale, businesswire jun-2026]
- **Financiero (ejercicio reportado 2025/H126):** ingresos del grupo **+28% a $992M**; **Adj. EBITDA +53%**, margen récord **49%** (+8pp); **Motors = segmento más fuerte, +42% YoY**, ~71% de la concentración de ingresos core. [V ≥2: businesswire nov-2025 + jun-2026]
- **Inversión IA:** **>$200M desde 2018**, **$30M** en el último ejercicio, **75-85+ casos de uso de IA** desplegados (10 agénticos en H1-26). [V ≥2: olxgroup AutoGPT, Prosus CLAIM AI]
- **Adquisición La Centrale (FR):** **€1.100M** a Providence, anunciada **26-sep-2025**, cerrada **nov-2025**; **~4,5M visitas/mes**, **~350.000 anuncios**, suite SaaS **Pilot** (pricing/sourcing/stock) para **10.000+ profesionales**; aportó **+13% tráfico / +30% leads** YoY. | [V ≥2: Prosus, businesswire] |

### Clientes objetivo [V]
1. **Particulares** (compra/venta C2C, valuador gratis, financiación, favoritos, mensajes).
2. **Profesionales / stands (B2B de pago)** — clientes de los paquetes Start→Expert; consumidores de las estadísticas, sales-velocity, posición en búsqueda, perfil del comprador y AutoIQ.
3. **Bancos / aseguradoras / partners de servicios** (Santander Consumer Bank, Cofidis, carVertical, Controlauto, BCA, OLX export).
4. **OEM / anunciantes** (display + visibilidad) — [A] inferido por naturaleza marketplace.

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| País | **Portugal** (mercado único; líder nacional) | [V] |
| Idioma | **Portugués (pt-PT)** | [V] |
| Tipos de vehículo | **Carros, Comerciais, Motos, Barcos, Autocaravanas, Pesados** (nav verbatim) | [V live: nav] |
| Nuevo/usado | **Usados = núcleo**; **Novos** presente (catálogo `/carros/novos/catalogo`) | [V live: nav] |
| Marcas | Todas (agnóstico — agrega inventario de stands + particulares) | [V] |
| Volumen vivo | **>40.000 vehículos** anunciados; **275.000+ anuncios usados** alimentan la estimación del valuador | [V ≥2: olxgroup brand, valuador] |
| Frescura | **"+7.000 anúncios publicados diariamente"** (cabecera del valuador) **vs "670 anúncios publicados por dia"** (caja de stats) — divergencia interna verbatim a anotar; modelo de avaliación **recalibrado cada 2 semanas** | [V live valuador] · divergencia 7000↔670 [V — sin explicación] |
| Base del Price Evaluation | Ofertas **similares vivas** en la propia plataforma (mismo make/model/versión/año/combustible/km) | [V ≥2: Netguru, help/cotação] |
| Cobertura del dato de mercado | **Mercado portugués real** (anuncios activos); contenido de mercado vía **Diário Automóvel** referencia datos **ACAP** (ej.: diesel ≈54% de transacciones VO 2024) | [V ≥2: diarioautomovel, search] |

---

## 3. Productos + campos atómicos

> Standvirtual expone **(A)** el objeto de anuncio (atributos de vehículo), **(B)** el **Price Evaluation** de 3 niveles + **histórico de precio**, **(C)** el **valuador B2C** (Avaliação do carro), **(D)** la **inteligencia de profesional** (sales-velocity / demanda / posición / perfil del comprador / estadísticas) y **AutoIQ**, **(E)** la pila de **IA** (descrição/respostas/vídeo/AI Seller Agent/AutoGPT), **(F)** los **servicios de valor** (histórico, inspección, financiación, seguro, retoma, entrega) y **(G)** la reputación del vendedor. Campos atómicos abajo.

### 3.A Objeto de anuncio / atributos de vehículo (ficha de detalle — verbatim live) [V]
Capturados en vivo de una ficha real (`Especificações técnicas`):
- **Identidad:** `Marca`, `Modelo`, `Versão` (ej. "2.0 D3 Geartronic").
- **Estado/condición:** `Estado` (Usado/Novo), **mes+año de 1ª matriculación** (ej. "Dezembro · 2018"), `Com garantia` (flag garantía), `Valor Fixo` (flag precio fijo/no negociable).
- **Uso:** `Quilómetros` (ej. 126 000 km).
- **Mecánica:** `Combustível` (Diesel/Gasolina/Híbrido/Elétrico/…), `Tipo de Caixa` (Automática/Manual), `Cilindrada` (cm³), `Potência` (cv), `Segmento` (SUV/TT, Citadino, …).
- **Carrocería:** `Cor` (+ tipo de color), `Nº de portas`.
- **Identificación:** **`VIN`** (botón "Mostrar VIN" — VIN presente). `Matrícula` usada por el valuador.
- **Equipamiento (agrupado por categorías):** **`Áudio e Multimédia`** (Bluetooth, Rádio, Porta USB, Sistema de navegação, Ecrã táctil), **`Conforto e Outros Equipamentos`**, **`Electrónica e Assistência à Condução`**, **`Segurança`**.
- **Pestañas de ficha:** `Especificações técnicas` y **`Estado e histórico`**.
- [A] Campos adicionales habituales del esquema OLX/Standvirtual no capturados en esta unidad concreta (porque la ficha solo muestra los rellenados): `Nº de proprietários`, `Origem/Importado`, `Livro de revisões`, `Não fumador`, `Registo de serviço`, `Norma de emissões`, `Emissões CO2`, `IUC`, `Lugares`, `Tração`, `Capacidade da bateria`/`Autonomia` (EV). Marcados [A] — presentes en el formulario de inserción del grupo pero no verificados verbatim en esta auditoría.

### 3.B Price Evaluation — el indicador de precio (la métrica-firma) [V]
Indicador del grupo OLX Motors creado **en cooperación con el Lisbon Data Science Team + Otomoto/Autovit/Standvirtual**. Definición oficial (Netguru): *"an indicator that shows whether a specific car is within an average price range compared to similar offers, lower or higher."* [V]
- **3 niveles (verbatim PT):** **`Abaixo da média`** (por debajo de la media) · **`Dentro da média`** (dentro de la media — **VERIFICADO EN VIVO** junto al precio de la ficha) · **`Acima da média`** (por encima de la media). [V ≥2: ficha live "Dentro da média" + search results pt]
- **Comparable:** ofertas **similares vivas** del propio inventario PT (mismo modelo/versión/año/combustible/km).
- **Sin valor numérico de "fair price" mostrado al comprador** en la ficha (es etiqueta cualitativa de 3 escalones, no un € objetivo público); el € objetivo aparece en el flujo del profesional / valuador.

### 3.C Histórico / dinámica de precio (verbatim live) [V]
En la ficha, **junto al precio**, Standvirtual muestra señales de dinámica de precio:
- **`- 1 000 EUR`** — **importe de la bajada** de precio (delta vs precio anterior).
- **Precio anterior tachado** (ej. `24 900 EUR`) → **precio actual** (`23 900 EUR`).
- **`Preço mais baixo`** — badge que marca que el precio actual es **el más bajo** alcanzado por ese anuncio. [V live — captura directa]

### 3.D Avaliação do carro — valuador B2C gratuito [V]
Tool gratis (`/avaliacao-do-carro`), heading **"Quanto vale o seu carro?"**.
- **Inputs (wizard, "Passo 1 de 2"):** `Ano*` (`first_registration_year`) → `Marca*` (`make`) → (revela) `Modelo`, `Versão/Motorização`, `Tipo de carroçaria`, `Tipo de combustível`, `Quilometragem`, (opt) `Potência`. **Vía alterna:** `Matrícula` **o** `VIN` + km → estimación en **~60 s**. [V ≥2: live form + search snippets] · campos del paso 2 [A parcial]
- **Output:** **`intervalo de preços estimado`** (ej. real mostrado: **`EUR 26.140 - EUR 31.050`**). Es **rango**, no punto único. [V live]
- **Método (3 pasos verbatim):** **`Identificação`** (identifican los datos principales) → **`Análise`** (comparan con coches semejantes en Standvirtual) → **`Cálculo`** (intervalo estimado con datos pormenorizados). [V live]
- **Stats verbatim ("Defina o seu preço com confiança"):** **10.000+** avaliações gratis/mes · **275.000+** anuncios usados para la estimación · **670** anuncios/día (caja) · **99%** de usuarios la consideran útil. [V live]
- **Disclaimer:** es estimación para **venta particular** ("se vender o seu carro por conta própria"); **la retoma en stand suele ser inferior**; la avaliación **cambia con el tiempo** (mercado). [V ≥2: WebFetch + FAQ live]

### 3.E Inteligencia del profesional + AutoIQ (núcleo del negocio de datos B2B) [V]
**Sales-velocity forecasting** (OLX Group, ene-2026) — modelo IA que **pronostica cuánto tardará en venderse un coche usado** ("forecast how long it will take to sell a used car"), analizando **datos de millones de usuarios/mes**:
- Da a los stands **decisiones en tiempo real de precio, canales promocionales y gestión de inventario**.
- Da **demand analytics por tipo de vehículo** → el stand evalúa si su stock **encaja con la demanda actual**; para alta demanda actúa rápido, para modelos lentos **recibe recomendaciones de ajustar precio/marketing**. [V ≥2: AIM, businesswire]
- **Posición del anuncio en los resultados de búsqueda en tiempo real** (el profesional ve si un anuncio necesita destaque). [V: search/dmark]
- **Perfil del comprador** (`buyer profile data`) y estadísticas de rendimiento por anuncio. [V: dmark, package tiers]

**AutoIQ** — *"the automotive intelligence operating system"* / *"24/7 analyst and consultant for car dealers"* (Prosus CLAIM AI). Disponible en Otomoto y **StandVirtual**. Capacidades:
- **Pricing recommendations** + **dealer insights**.
- **Instant inventory summaries** (resúmenes de inventario).
- **AI-generated listing descriptions** que **preservan la voz del dealer**.
- **Centralized lead dashboard** (panel de leads centralizado).
- **Video-to-listing** y **ad-to-short-form content** (anuncio → contenido corto vertical).
- **Visual experience enhancement** (mejora de imágenes).
- **Métricas de impacto:** anuncios publicados hasta **36% más rápido**, **+12% responsiveness** del dealer, **engagement semanal del dealer 21%** y creciendo, **21% retención WoW**. [V ≥2: Prosus, businesswire, techfinancials]
- ⚠ Los módulos nombrados "Comments Generator / Image Management / **Dealer Insights** (market demand/pricing trends/supply levels)" pertenecen, según techfinancials, a **AutoTrader SA**; AutoIQ replica funciones equivalentes pero **no verifico esos nombres exactos en el stack PT**. [V atribución AutoTrader SA; AutoIQ-PT = funciones equivalentes]

### 3.F Pila de IA (B2C + profesional) [V]
- **Descrição Automática do Anúncio** — genera texto estructurado adaptado al estilo del vendedor; **ahorra ~5 min/anuncio (≈40% del tiempo)**, **87% de adopción** entre profesionales. [V ≥2: pcguia, echoboomer]
- **Respostas Automáticas** — responde dudas de compradores en tiempo real **24/7** según los datos del anuncio. [V: pcguia]
- **Vídeo Automático** — crea vídeos promocionales cortos desde fotos + datos (formato vertical, Reels). [V: pcguia]
- **AI Seller Agent** *(coming / 2026)* — asistente para **creación masiva de anuncios por lectura de matrícula**, subida de ficheros + inserción en lote, e interfaz tipo chat para acceder a **info del anuncio, datos de rendimiento y pagos pendientes**. [V: pcguia]
- **Instant Ad** *(2026)* — crear un anuncio **solo desde foto/vídeo**. [V: search]
- **AutoGPT** — asistente **agéntico conversacional sobre ChatGPT** (con OpenAI), entrenado en datos propios de OLX: **resale value trends, regional pricing patterns, dealer performance metrics, buyer behaviour** + transacciones verificadas de millones de ventas; el comprador describe en lenguaje natural y recibe shortlist + market insights (**≥20% más rápido** que el filtrado tradicional). **Live en Otomoto (PL); rollout programado a La Centrale (FR), Autovit (RO) y Standvirtual (PT)**. [V ≥2: olxgroup, businesswire] · **en Standvirtual = pendiente de rollout** [V]

### 3.G Reputación del vendedor (ratings) [V live]
Bloque "Informações sobre o vendedor" en la ficha:
- **`Classificação` global** (ej. **4.9**) + **nº de classificações** (ej. "12 classificações").
- **Sub-dimensiones de excelencia** ("Este vendedor destaca-se em:") — ej. **`Conhecimento` 5.0** (otras dimensiones típicas: comunicación/rapidez). + enlace "Como funcionam as classificações?".
- Solo valoran usuarios que **interactuaron** con el vendedor. [V live]

### 3.H Servicios de valor (en ficha / nav) [V live]
- **Verificar histórico do veículo** — partner **carVertical** (registros de accidentes y daños, historial de **+40 países**, **-20%** dto., "Obter relatório de histórico" de pago). [V live + nav]
- **Inspecionar estado atual** — partner **Controlauto** (`carros.standvirtual.com/verificar-controlauto`): inspección presencial, **200–350 parâmetros verificados**, **custos de reparação estimados**, "Marcar inspeção". [V live + nav]
- **Financiamento** — **simulador en el anuncio**: cuota mensual personalizada (ajustable a entrada y plazo) + envío de propuesta directa al banco partner y al profesional. Integrado con **Santander Consumer Bank** (disponible en profesionales seleccionados); partnership con **Cofidis** para servicios digitales. [V ≥2: executivedigest, posvenda]
- **Seguro automóvel**, **Entrega em casa** (entrega a domicilio), **Serviço de retoma** (trade-in) — listados como "Principais serviços do vendedor". [V live]

### 3.I Paquetes de profesional + visibilidad (tarifa) [V — 3º (Dmark) + tarifa oficial existe]
4 niveles, cobro **por anuncio en ciclos renovables de 15 días** (no hay paquete único de stock):
| Paquete | €/anuncio/15d | Visibilidad | Incluye (resumen) |
|---|---|---|---|
| **Start** | **€19,99** | base | herramientas IA, mini-site del stand, **call tracker**, logo en anuncio, multi-usuario |
| **Standard** | **€23,49** | **+70% vistas** | + "To Top" ×2/ciclo, **dados do perfil do comprador**, logo en resultados, 10% dto. destaques |
| **Advanced** | **€32,49** | **+120% vistas** | + "To Top" ×3, **Top Potencies** (3 días), **Super Ad**, site premium, 20% dto. |
| **Expert** | **€44,99** | **+230% vistas** | + "To Top" ×4, **Top Stand** (20.000 impresiones), **exportação automática para OLX**, **acesso a leilões BCA**, 30% dto. |
- **Add-ons sueltos:** "To a Top" desde **€1,00/día** (3–14 días); "Top Potencies" desde **€1,78/día**. [V: dmark]
- **Tarifario oficial:** existe (`ajuda.standvirtual.com/.../tarifrio-para-vendedores-profissionais-V21` y particulares V22) pero **JS-rendered** (no leído verbatim). [V existencia; importes via Dmark 3º]

---

## 4. Metodología y fuentes de datos

| Aspecto | Detalle | Estado |
|---|---|---|
| Naturaleza del dato | **Precio de ANUNCIO** (asking price) del propio inventario vivo PT — no precio de transacción confirmado (aunque AutoGPT cita "transacciones verificadas" a nivel grupo) | [V] |
| Fuente | **Inventario propietario** (>40.000 vivos; **275.000+ anuncios** para el valuador) de stands + particulares; primer-party, no metasearch | [V ≥2: brand, valuador] |
| Constructor del motor | **Lisbon Data Science Team** + equipos locales Otomoto/Autovit/Standvirtual (price evaluation común OLX Motors) | [V: Netguru] |
| Método valuador | Comparación contra coches **semejantes** en Standvirtual (make/model/versão/año/combustible/km) → **intervalo** de precio; **recalibrado cada 2 semanas** | [V ≥2: valuador live, WebFetch] |
| Sales-velocity | Modelo IA que pronostica **días-a-venta** + demanda por tipo, sobre datos de **millones de usuarios/mes** | [V ≥2: AIM, businesswire] |
| Price Evaluation | Clasificación cualitativa de **3 niveles** vs media de ofertas similares (within/lower/higher) | [V ≥2: Netguru, live] |
| IA generativa | Descripción/imagen/vídeo + AI Seller Agent (matrícula→anuncio) + **AutoGPT** (LLM agéntico OpenAI sobre datos OLX) | [V ≥2: pcguia, olxgroup] |
| Confidence / score numérico | **No expone** banda de confianza ni score numérico al comprador (etiqueta de 3 niveles + rango en el valuador) | [V — ausente] |
| Frecuencia | Price-evaluation/posición en búsqueda **en tiempo real**; valuador **recalibra cada 2 semanas**; histórico de precio por anuncio en vivo | [V] |
| Inversión tecnológica | OLX Group **>$200M en IA desde 2018**; **75-85+** casos de uso; price evaluation + sales-velocity = casos motors | [V] |

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **Web/App B2C** | `standvirtual.com` + apps iOS/Android (`com.fixeads.standvirtual`) | [V ≥2: live, Play Store] |
| **Badge en ficha** | Price Evaluation (`Dentro da média`…) + histórico de precio (`- 1 000 EUR`, `Preço mais baixo`) junto al precio | [V live] |
| **Valuador web** | `/avaliacao-do-carro` (resultado = intervalo €) | [V live] |
| **Portal de profesional (gated)** | `standvirtual.com/contapessoal/*` (redirige a `/authentication`) + **`portal-insights.standvirtual.com` (403, tras login)**: estadísticas, sales-velocity, demanda, posición en búsqueda, perfil del comprador, AutoIQ | [V curl+Playwright host; contenido atómico vía press] |
| **AutoIQ** | "Operating system" del dealer (panel de leads, inventory summaries, pricing recs, IA de contenido) | [V: Prosus] |
| **AutoGPT** | Asistente agéntico **sobre ChatGPT** (rollout a Standvirtual pendiente) | [V: olxgroup] |
| **OLX export** | Exportación automática de anuncios a **OLX** (tier Expert) | [V: dmark] |
| **Leilões BCA** | Acceso a **subastas BCA** desde el tier Expert (sourcing wholesale) | [V: dmark] |
| **Servicios partner** | carVertical (histórico), Controlauto (inspección), Santander Consumer/Cofidis (financiación), seguro, entrega, retoma | [V ≥2: live, press] |
| **Insights abiertos** | **Diário Automóvel** (guías, cotación, barómetros de precio VO, tendencias; cita ACAP) | [V ≥2: diarioautomovel] |
| **API pública** | **No hay API oficial pública** de consulta/valuación; el acceso de datos lo hacen scrapers de **terceros** (Carapis) — no oficial | [V — ausente oficial] |

---

## 6. Precio (modelo)

| Producto | Modelo | Estado |
|---|---|---|
| **Paquetes profesional** | **Start €19,99 / Standard €23,49 / Advanced €32,49 / Expert €44,99** por anuncio/15 días (ciclos renovables) | [V: dmark 3º] · tarifa oficial existe [V] |
| **Add-ons visibilidad** | "To a Top" desde €1,00/día; "Top Potencies" desde €1,78/día; Super Ad, Top Stand, destaques con dto. por tier | [V: dmark] |
| **Valuador B2C** | **Gratis** | [V live] |
| **Price Evaluation / histórico** | **Gratis** (embebido en cada anuncio) | [V live] |
| **AutoIQ / sales-velocity / insights** | Dentro de la cuenta de profesional (incluido por tier; importe exacto no público) | [V: dmark] · tarifa exacta [NV] |
| **Histórico carVertical** | **De pago** (-20% vía Standvirtual) | [V live] |
| **Inspección Controlauto** | **De pago** | [V] |
| **Financiación** | Sin coste de uso del simulador; producto del banco partner | [V] |
| **Diário Automóvel / insights** | **Gratis/abierto** (SEO/marketing) | [V] |

---

## 7. Placement — dónde se ubica cada dato (patrón a copiar por cardeep)

> Fuente **explícita** (Netguru, OLX Motors Europe): el **Price Evaluation aparece en 5 superficies → Listing Page, Ad Details, Posting Form, My Ads y Sourcing Insights**. El resto del mapeo es **verificado en vivo** sobre la ficha real.

| Dato / métrica | Dónde se coloca (pantalla/sección) | Estado |
|---|---|---|
| **Price Evaluation (3 niveles)** | **Listing Page** (resultados) · **Ad Details** (ficha, junto al precio: "Dentro da média") · **Posting Form** (al crear anuncio) · **My Ads** (mis anuncios) · **Sourcing Insights** (profesional) | [V ≥2: Netguru + ficha live] |
| **Histórico de precio** (`- 1 000 EUR`, precio tachado, `Preço mais baixo`) | **Junto al precio** en la ficha (Ad Details) | [V live] |
| **Specs del vehículo** (marca/modelo/versão/ano/km/combustível/caixa/cilindrada/potência/segmento/cor/portas/VIN) | Pestaña **`Especificações técnicas`** de la ficha | [V live] |
| **Estado e histórico** (garantía, histórico, inspección) | Pestaña **`Estado e histórico`** + bloque **"Verifique antes de comprar"** (carVertical -20% / Controlauto 200–350 parâmetros) | [V live] |
| **Equipamiento** (Áudio/Multimédia, Conforto, Electrónica/Assistência, Segurança) | Sección **`Equipamento`** de la ficha (agrupado por categoría) | [V live] |
| **Servicios del vendedor** (financiamento/seguro/entrega/retoma) | Bloque **"Principais serviços do vendedor"** en la ficha | [V live] |
| **Simulador de financiación** (cuota mensual ajustable) | **Dentro del anuncio** (Ad Details), para profesionales seleccionados | [V: press] |
| **Reputación del vendedor** (4.9 + sub-dimensiones "destaca-se em") | Bloque **"Informações sobre o vendedor"** en la ficha | [V live] |
| **Resultado del valuador** (intervalo €) | **Pantalla de resultado** de `/avaliacao-do-carro` (tras wizard 2 pasos) | [V live] |
| **Sales-velocity (días-a-venta) / demanda por modelo** | **Portal de profesional** (gated `contapessoal` / `portal-insights`) + **Sourcing Insights** | [V: press + host] |
| **Posición del anuncio en búsqueda (tiempo real)** | **Portal de profesional** (por anuncio) | [V: dmark] |
| **Perfil del comprador** (`buyer profile data`) | **Portal de profesional** (tier Standard+) | [V: dmark] |
| **AutoIQ** (lead dashboard, inventory summaries, pricing recs, IA contenido) | **Portal de profesional / app AutoIQ** | [V: Prosus] |
| **Insights de mercado abiertos** | **Diário Automóvel** (editorial, separado del per-vehículo) | [V] |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Liderazgo nacional PT de primer-party**: >6M visitas/mes + >40.000 vehículos vivos + 275.000+ anuncios al motor — el dato sale del mercado portugués real que ellos operan, no de una guía teórica (Eurotax/Ganvam). [V]
2. **Price Evaluation de 3 niveles embebido en 5 superficies** (Listing/Ad Details/Posting/My Ads/Sourcing Insights) — confianza instantánea comprador + guía de pricing vendedor; métrica-firma copiable. [V]
3. **Histórico de precio en la ficha** (`- 1 000 EUR`, precio anterior tachado, **`Preço mais baixo`**) — transparencia de la dinámica de precio del propio anuncio (pocas guías lo muestran). [V]
4. **Sales-velocity forecast (días-a-venta) + demand analytics por modelo** nativos del marketplace líder PT — análogo a INDICATA/MDS pero con datos de millones de usuarios PT. [V]
5. **AutoIQ = "dealer operating system"** completo (pricing recs + inventory summaries + lead dashboard + IA de descripción/imagen/vídeo) con métricas duras (36% más rápido, +12% responsiveness, 21% engagement). [V]
6. **Pila de IA agéntica del grupo** (AI Seller Agent matrícula→anuncio en lote; **AutoGPT** sobre ChatGPT entrenado en resale-value/pricing/dealer-performance/buyer-behaviour). [V]
7. **Plataforma multinacional reutilizable** (OLX Motors Europe: Otomoto/Autovit/Standvirtual/La Centrale + Pilot suite) — economías de escala de modelo y producto. [V]
8. **Ecosistema de servicios integrado en la ficha**: financiación (Santander/Cofidis), histórico (carVertical), inspección (Controlauto), seguro, entrega, retoma, **export OLX**, **subastas BCA**. [V]
9. **Reputación del vendedor con sub-dimensiones** (no solo estrella global: "destaca-se em: Conhecimento"). [V]
10. **Insights abiertos (Diário Automóvel)** = autoridad de mercado + generación de demanda SEO. [V]

---

## 9. Gaps (lo que NO ofrece / límites)

1. **Asking price, NO transaction price** a nivel de ficha — el dato visible es de anuncio; el "transacciones verificadas" se cita a nivel grupo (AutoGPT) pero no se expone por vehículo. [V]
2. **Sin API pública oficial** de consulta/valuación — el acceso programático lo cubren scrapers de **terceros** (Carapis), no Standvirtual. [V — ausente]
3. **Sin valor residual (RV) forward / curvas de depreciación** como producto — no compite con Eurotax/Autovista RVM/Schwacke en RV% a 12-60 meses; su dato es precio+specs de anuncio + intervalo presente. [V — ausente]
4. **Sin provenance/VIN history propio** — lo **externaliza a carVertical** (partner de pago); no es un Carfax/autoDNA nativo. [V]
5. **Price Evaluation cualitativo de 3 niveles, sin € objetivo ni banda de confianza** mostrados al comprador (menos granular que los 5 niveles + `labelRanges` de mobile.de/AutoScout24). [V]
6. **Inteligencia de profesional (sales-velocity, demanda, posición, perfil, AutoIQ) gated tras login** — `portal-insights.standvirtual.com` = 403; el detalle atómico se reconstruyó de prensa, no se leyó la UI interna. [V host; contenido [A] parcial]
7. **AutoGPT aún no live en Standvirtual** (live solo en Otomoto-PL; PT en rollout). [V]
8. **Tarifa exacta del profesional no 100% pública** (importes vía Dmark 3º; tarifário oficial JS-rendered no leído verbatim). [V tendencia; importes [V 3º]]
9. **Facturación de Standvirtual no desglosada** (consolida en OLX Group/Prosus). [NV — GAP]
10. **Divergencia interna de cifras** ("+7.000 anúncios/dia" cabecera vs "670/dia" caja de stats del mismo valuador) — sin explicación oficial. [V la divergencia]
11. **Cobertura = solo Portugal** (no índice pan-europeo multi-país por marca única; la escala multinacional es del grupo OLX Motors, no de Standvirtual). [V]
12. **Riesgo de atribución**: módulos "Comments Generator/Image Management/Dealer Insights" son de **AutoTrader SA**; mapearlos a Standvirtual sería error — AutoIQ-PT replica funciones, no necesariamente los nombres. [V — riesgo de fuente]
13. **Datos de equipamiento por VIN código-a-código no son su core** (usa equipamiento declarado en el anuncio, no build-data OEM por VIN tipo JATO/DAT). [V — naturaleza marketplace]

---

## 10. Fuentes

| # | URL | Qué verifica |
|---|---|---|
| 1 | https://www.olxgroup.com/brands/standvirtual/ | Identidad: OLX Group, Lisboa, >18 años, >6M visitas/mes, >40.000 vehículos, compra/venta PT |
| 2 | https://www.standvirtual.com/avaliacao-do-carro | **(live Playwright)** Valuador: heading "Quanto vale o seu carro?", inputs `Ano*`/`Marca*` (wizard 2 pasos), stats (10.000+/mes, 275.000+ anuncios, 670/día, 99% útil), 3 pasos (Identificação/Análise/Cálculo), ejemplo EUR 26.140-31.050, FAQ (retoma inferior, cambia con el tiempo), "+7.000 anúncios/dia" cabecera |
| 3 | https://www.standvirtual.com/carros/anuncio/volvo-xc-40-ver-2-0-d3-geartronic-ID8PUoP7.html | **(live Playwright)** Ficha real: **Price Evaluation "Dentro da média"** junto al precio; histórico **"- 1 000 EUR" / "24 900 EUR" tachado / "Preço mais baixo"**; specs (Usado·Dezembro·2018, Com garantia, Valor Fixo, km, combustível, caixa, segmento, cilindrada, potência, marca/modelo/versão, cor, portas, VIN); equipamiento (Áudio/Multimédia, Conforto, Electrónica/Assistência, Segurança); servicios (financiamento/seguro/entrega/retoma); "Verifique antes de comprar" (carVertical -20%, Controlauto 200-350 parâmetros); reputación vendedor 4.9 + "destaca-se em: Conhecimento 5.0" |
| 4 | https://www.netguru.com/clients/olx-product-design-consulting | **Price Evaluation** OLX Motors Europe: definición (within/lower/higher vs ofertas similares); **5 superficies (Listing Page, Ad Details, Posting Form, My Ads, Sourcing Insights)**; creado con **Lisbon Data Science Team** + Otomoto/Autovit/Standvirtual |
| 5 | https://aimgroup.com/2026/01/28/olx-deploys-ai-to-predict-used-car-sales/ (vía search) | **Sales-velocity forecasting**: pronostica días-a-venta; demand analytics por tipo; decisiones de precio/inventario/promoción; datos de millones de usuarios/mes; Otomoto + operaciones europeas |
| 6 | https://www.olxgroup.com/news/olx-launches-autogpt-agentic-ai-assistant-transforming-automotive-search-across-europe/ | **AutoGPT**: LLM agéntico OpenAI sobre ChatGPT; datos (resale value trends, regional pricing, dealer performance, buyer behaviour, transacciones verificadas); live Otomoto, rollout La Centrale/Autovit/**Standvirtual**; 20% más rápido; pairs con **AutoIQ**; >$200M IA desde 2018 |
| 7 | https://www.prosus.com/news-insights/2026/olx-launches-agentic-ai-products-...-claim-ai-in-lisbon | **AutoIQ** = "automotive intelligence operating system / 24/7 analyst"; pricing recs, dealer insights, inventory summaries, lead dashboard, descripción IA (voz del dealer), video-to-listing, ad-to-short-form; 36% más rápido, +12% responsiveness, 21% engagement; $30M IA/año, 75+ casos, 10 agénticos H1-26; CompassGPT (property) |
| 8 | https://www.businesswire.com/news/home/20260628483782/... (vía Yahoo mirror) | OLX Group jun-2026: AutoIQ "dealer OS" 21% retención WoW; **Motors +42% YoY**; grupo **+28% a $992M**; EBITDA +53%; ~60M listings/día en 7 mercados; La Centrale +13% tráfico/+30% leads; $30M IA, 85+ casos |
| 9 | https://www.prosus.com/news-insights/2025/prosus-olx-group-agrees-to-acquire-la-centrale-... | **La Centrale €1.100M** (26-sep-2025, cierre 2025); 4,5M visitas/mes, 350k anuncios, suite **Pilot** (pricing/sourcing/stock), 10.000+ pros; OLX ~29M usuarios/mes en 8 países |
| 10 | https://www.pcguia.pt/2026/02/standvirtual-convoca-varias-ferramentas-de-ia-... | IA Standvirtual: **Descrição Automática** (5 min/-40%), **Respostas Automáticas** (24/7), **Vídeo Automático** (vertical), **AI Seller Agent** (matrícula→anuncio lote + chat de rendimiento/pagos); -40% tiempo publicación |
| 11 | https://dmark.pt/quanto-custa-anunciar-standvirtual-2026/ | **Paquetes**: Start €19,99 / Standard €23,49 (+70%) / Advanced €32,49 (+120%) / Expert €44,99 (+230%); por anuncio/15d; features (call tracker, perfil do comprador, To Top, Top Potencies, Super Ad, Top Stand 20k, export OLX, **leilões BCA**); add-ons €1,00/€1,78 día |
| 12 | https://executivedigest.sapo.pt/standvirtual-lanca-funcionalidade-para-simular-financiamento-automovel/ ; https://posvenda.pt/cofidis-e-standvirtual-em-parceria-estrategica/ | **Financiación en anuncio**: cuota mensual personalizada (entrada/plazo) → propuesta directa a banco + profesional; integrado con **Santander Consumer Bank** (profesionales seleccionados); partnership **Cofidis** |
| 13 | https://heroispme.pt/historias/edicao-1/olx-fixeads-sa ; https://www.racius.com/marcas/standvirtual-o-n1-em-carros/ | Historia: Standvirtual **2004** (Miguel Mascarenhas, "Fixe.com"); **FixeAds 2007**; **Naspers 2012** (OLX PT + Imovirtual); marcas FixeAds (OLX/Standvirtual/Imovirtual/Coisas/Faturavirtual) |
| 14 | https://www.standvirtual.com/diarioautomovel ; .../cotacao-de-carros-usados-onde-encontrar | **Diário Automóvel**: insights abiertos (cotación, valor VO, barómetros, tendencias); referencia precio medio de semejantes con filtros; cita ACAP (diesel ≈54% VO 2024) |
| 15 | (search) www.standvirtual.com/carros?page=8 ; help center | **Etiquetas Price Evaluation 3 niveles**: `Abaixo da média` / `Dentro da média` / `Acima da média` |
| 16 | `curl -I https://portal-insights.standvirtual.com/` → **403 CloudFront** (143.204.55.x) ; `standvirtual.com/contapessoal/package-comparison` → 301/redirect a `/authentication` | Portal de insights del profesional **EXISTE, gated tras login**; comparador de paquetes requiere autenticación |
| 17 | https://carapis.com/platforms/western-europe/standvirtual | **(3º, no oficial)** Parser de campos: make, model, trim, model year, fuel, transmission, mileage, price, seller type, location, fotos — confirma esquema mínimo de anuncio |

> **Nota de método:** identidad/owner con ≥2 fuentes (OLX Group brand + onlinemarketplaces/AIM + Heróis PME). **Price Evaluation, histórico de precio, specs, equipamiento, servicios y reputación = [V] leídos EN VIVO** de una ficha real con Playwright (CloudFront bloquea curl). Las **5 superficies de placement = [V] Netguru** (caso oficial OLX Motors). **Sales-velocity, AutoIQ y AutoGPT = [V] press OLX/Prosus/AIM** (a nivel plataforma; rollout PT de AutoGPT pendiente). Importes de paquetes = [V vía Dmark 3º] + tarifário oficial existe (JS, no verbatim). Campos atómicos de anuncio no mostrados en la unidad concreta marcados **[A]**. Facturación de Standvirtual y detalle interno del portal gated = **GAP** declarado. Sin invención: lo no leído va como [A]/[NV].
