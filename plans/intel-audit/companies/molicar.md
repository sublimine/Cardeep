# Molicar (KBB Brasil — Tabela Molicar) — Auditoría atómica

> Slug: `molicar` · Subdominio cardeep: **valuation** · Región: **Brasil** (mercado único)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` / `[PARCIAL]` / `[NO-VERIFICADO]` donde no se confirmó al 100%.
> Naturaleza: **guía de precios de vehículos B2B/B2C** propiedad de **Cox Automotive** (Kelley Blue Book Brasil).
> Es la **alternativa "premium/multivalor" a la Tabela Fipe** en Brasil: precios **por región, por versión y por
> tipo de transacción**, ajustables por km/cor/opcionais. Marca operativa de **KBB Brasil** ("Tabela KBB Brasil =
> Molicar"). **Es el peer brasileño directo de cardeep: huella digital de precificación nacional, multivalor.**
> ⚠ Acceso bloqueado: `www.molicar.com.br`, `kbb.com.br` y todo `*.molicar.com.br` devuelven **HTTP 403** a
> WebFetch **y a navegador headless** (WAF + geobloqueo; solo IP Brasil). La reconstrucción de UI/campos se hizo
> vía: **Wayback Machine** (snapshots reales de las páginas, capturados antes del script de redirección),
> **coxautomotive.com.br** (corporativo, NO bloqueado), **informe MVP PDF** (descargado y extraído), **microservicio
> SOAP open-source** (`deividfortuna/molicar`, expone los nombres de campo reales del web service), y prensa/terceros.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre comercial | **Molicar** (Tabela Molicar / "Molicar Digital"). Operada como **Kelley Blue Book Brasil (KBB Brasil)** — "Tabela KBB Brasil (Molicar)" | molicar.com.br/QuemSomos; coxautomotive.com.br; alvesp |
| Razón social | **Molicar Publicações Automotivas Ltda** | LinkedIn (br.linkedin.com/company/molicar-publicações-automotivas-ltda) `[VERIFICADO]` |
| Propietario / grupo | **Cox Automotive Inc.** (división de **Cox Enterprises Inc.**, conglomerado familiar privado, +50.000 empleados, +US$21 bn ingresos). Cox compró **participación mayoritaria** en Molicar | prnewswire 2016; coxautoinc.com; MVP PDF "Sobre a Cox" `[VERIFICADO]` |
| Fecha de adquisición | **Anunciada 13-abr-2016**, cierre previsto inicios de mayo 2016. Cox pasó a tener valoraciones en los "3 mayores mercados de usados del mundo" | prnewswire.com/news-releases/cox-automotive-purchases-majority-stake-in-molicar `[VERIFICADO]` |
| Fundación | **1992**; primera tabla de precios publicada en **junio de 1994** | molicar.com.br/QuemSomos (verbatim) `[VERIFICADO]` |
| HQ | **São Paulo, SP, Brasil** | prnewswire ("based in Sao Paulo"); LinkedIn `[VERIFICADO]` |
| Hosting real | `www.molicar.com.br` → **AWS sa-east-1** (IPv4 `54.207.67.227`) | nslookup `[VERIFICADO]` |
| Marcas hermanas (Cox Brasil) | **Cox Automotive Brasil lidera 4 de las 26 empresas Cox**: **Kelley Blue Book Brasil, Molicar, Dealertrack, Manheim** (+ "CoxPraVocê") | MVP PDF; coxautomotive.com.br/marcas `[VERIFICADO]` |
| Sitios | `molicar.com.br` (consulta Tabela Molicar + app móvil) · `kbb.com.br` (portal hermano KBB Brasil) · `coxautomotive.com.br` (corporativo, informes MVP) | múltiples `[VERIFICADO]` |
| Desarrollo web | "Desenvolvido por **CSB Consulting**" (pie de molicar.com.br) | Wayback snapshot `[VERIFICADO]` |

**Posicionamiento (cita QuemSomos, verbatim):** *"…sempre se posicionando como uma empresa independente, sem
representar qualquer ligação com segmento de comercialização, financiamento ou seguro de automóveis. A empresa é
inteiramente focada em sua única atividade: apurar o valor comercial atualizado de todos os veículos leves,
pesados, motocicletas e também implementos rodoviários da frota circulante do mercado brasileiro."* `[VERIFICADO]`

**Categoría de producto:** **guía de valoración multivalor + catálogo de specs + decoder para crédito + analítica
de mercado (MVP)**. Más rico que FIPE (que es un precio medio único); es el "KBB/Black-Book brasileño".

**Cliente objetivo (cartera declarada, verbatim QuemSomos):** *"bancos, financeiras, seguradoras, advogados,
escritórios de cobrança, revendedores de veículos, montadoras, lojistas, imprensa especializada"* — además de
particulares (consulta web) y, vía Decoder, **instituciones financieras (esteira de crédito)**. `[VERIFICADO]`

---

## 2. Cobertura

- **Geografía:** **solo Brasil.** `[VERIFICADO]`
- **Granularidad regional (DIFERENCIAL vs FIPE):** precio **ajustado a la región**. Dos niveles de granularidad:
  - **Consulta web:** selector de **Estado** con los **27 UF** (los 26 estados + Distrito Federal). `[VERIFICADO: dropdown TabelaMolicar]`
  - **Banco de Dados (B2B):** **12 macro-regiones** comerciales: `Estado de São Paulo` · `Estado de Minas Gerais` ·
    `Estado do Rio de Janeiro` · `Estado do Espírito Santo` · `Estado do Paraná` · `Sul: RS SC` ·
    `CO: DF, MS, GO, MT, TO` · `Nordeste 1: BA SE` · `Nordeste 2: PE PB AL RN` · `Nordeste 3: CE PI MA` ·
    `Norte 1: AC AM RO RR` · `Norte 2: PA AP` (+ "Todos"). `[VERIFICADO: formulario Banco de Dados]`
- **Nuevo / seminuevo / usado:** los tres. Segmentación por **tiempo de uso**: **0 km**, **seminovos (até 3 anos)**,
  **usados (4 a 20 anos)**. Flag de entrada **0 km** (`pblnIndZeroKM`). `[VERIFICADO: MVP + SOAP]`
- **Tipos de vehículo (5 categorías en la UI):** `veículos` (automóveis e utilitários) · `motocicletas` ·
  `caminhões` · `ônibus` · `implementos rodoviários` (baús, cegonhas, tanque, etc.). En B2B se agrupa como
  **"Automóveis e Utilitários / Veículos Pesados / Motos / Todos"**. `[VERIFICADO: radios TabelaMolicar + form B2B + infocar]`
- **Antigüedad:** vehículos **fabricados en los últimos 35 años** (frota circulante). `[VERIFICADO: snippets oficiales "manufactured in the last 35 years"; el dropdown de año en usados llega a ~20 años de uso en MVP]`
- **Universo de marcas:** **~140 marcas** en el dropdown, incl. mass-market, premium, exóticos y **toda la oleada
  china**: ACURA, AGRALE, ALFA ROMEO, ASTON MARTIN, AUDI, BAIC, BENTLEY, BMW, **BYD**, CADILLAC, **CAOA CHERY**,
  **CAOA CHANGAN**, CHERY, CHEVROLET, CHRYSLER, CITROEN, **DENZA**, DODGE, **DONGFENG**, DS, EFFA, ENGESA, FERRARI,
  FIAT, FORD, FOTON, **GAC**, **GEELY**, GENESIS, GMC, GURGEL, **GWM**, HONDA, HYUNDAI, INFINITI, ISUZU, IVECO,
  **JAC**, **JAECOO**, JAGUAR, JEEP, **JETOUR**, KIA, LAMBORGHINI, LAND ROVER, **LEAPMOTOR**, LEXUS, LIFAN, MASERATI,
  MAZDA, MCLAREN, MERCEDES-BENZ, MINI, MITSUBISHI, **MORRIS GARAGES (MG)**, **NETA**, NISSAN, **OMODA**, PEUGEOT,
  PORSCHE, RAM, RENAULT, **RIDDARA**, **RIVIAN**, ROLLS ROYCE, SEAT, **SERES**, SsangYong, SUBARU, SUZUKI, **TESLA**,
  TOYOTA, TROLLER, VOLKSWAGEN, VOLVO, **ZEEKR**… `[VERIFICADO: dropdown completo capturado]`

---

## 3. Productos + campos atómicos

> Molicar/KBB Brasil es **multi-producto**. Núcleo = **Tabela Molicar** (consulta de valor multivalor). A su
> alrededor: **Banco de Dados Molicar** (B2B), **Web Service/API**, **Decoder KBB-Molicar** (crédito) y **MVP**
> (analítica de mercado). Productos legacy: **Molicar Book**, **Molicar Peças**, **Molicar Vistoria**.

### 3.1 Tabela Molicar / "Molicar Digital" — consulta de valor (producto núcleo)

**Entrada (drill-down, cascada):** `Categoria` → `Estado (UF)` → `Marca` → `Ano Fabricação` → `Ano Modelo` →
`Modelo` → `Versão` → **Enviar**. Alternativa: **"Busca rápida"** por **código Molicar** (input directo). `[VERIFICADO]`

**Campos atómicos de SALIDA (valor + specs).** Fuente primaria de los nombres reales: el **web service SOAP oficial**
`www.molicar.com.br/wsconsultamolicar.asmx`, mapeado verbatim por el microservicio open-source `deividfortuna/molicar`
(método de info del coche). ⚠ Es la API legacy/pública (~2017–2020); los **nombres de campo** son reales, las
**etiquetas de pantalla** del resultado autenticado están `[PARCIAL]` (tras login).

| Campo (SOAP real) | Significado atómico | Verif. |
|---|---|---|
| `CodMolicar` | **Código Molicar / KBB-Molicar** — identificador único de la versión-año (clave de unión del ecosistema) | `[VERIFICADO]` |
| `ValCotacao` | **Valor de cotação** — valor comercial actualizado (el precio base) | `[VERIFICADO]` |
| `ValCotacaoCompleto` | **Valor de cotação completo** — valor con opcionais/equipamiento incluido | `[VERIFICADO]` |
| `CodMarca` | Código de marca | `[VERIFICADO]` |
| `CodModelo` | Código de modelo | `[VERIFICADO]` |
| `CodCategoria` | Código de categoría (carro/moto/caminhão/ônibus/implemento) | `[VERIFICADO]` |
| `CodMacroCategoria` | Código de macro-categoría | `[VERIFICADO]` |
| `QtdPassageiro` | **Nº de pasajeros / plazas** | `[VERIFICADO]` |
| `QtdQuiloPeso` | **Peso (kg)** | `[VERIFICADO]` |
| `QtdCCMotor` | **Cilindrada del motor (cc)** | `[VERIFICADO]` |
| `QtdCV` | **Potencia (CV / cavalos)** | `[VERIFICADO]` |
| `plngCodVersao` (entrada) | Código de versión/trim | `[VERIFICADO]` |
| `plngCodAnoModelo` (entrada) | Código de año-modelo | `[VERIFICADO]` |
| `pblnIndZeroKM` (entrada) | **Indicador 0 km** (sí/no) | `[VERIFICADO]` |

**Valores multivalor por TIPO DE TRANSACCIÓN (núcleo del diferencial).** El mismo vehículo devuelve **distintos
precios** según la transacción (verbatim de KBB Brasil): *"…um preço para cada tipo de transação: **entre
particulares**; **particulares e lojistas**; e para **carros novos e usados**."* `[VERIFICADO: coxautomotive "por que trocar a Fipe"; alvesp; busca KBB]`

| Datum (tipo de valor) | Significado |
|---|---|
| **Preço entre particulares** | Particular ↔ particular (venta privada directa) |
| **Preço particular ↔ lojista/revenda** | Compra/venta con concesionaria (≈ trade-in / retail dealer) |
| **Preço 0 km** | Vehículo nuevo |
| **Preço usado / seminovo** | Por tiempo de uso |
| **Preço por versão** (S, SE, SE Plus…) | **Individualiza por variante** (FIPE da un solo precio por modelo) |
| **Preço ajustado por região/UF** | Auto-ajuste a la región del usuario |
| **Forecast / prognóstico** | KBB usa pronósticos, no medias simples (ver §4) |

**Ajustes editables por el usuario (modifican el valor):** `quilometragem` (km rodados) · `cor` (color) ·
`opcionais` / equipamiento (incl. **blindagem** y accesorios; ej. airbag, direção hidráulica) · `estado de
conservação`. `[VERIFICADO: alvesp; inter; infocar; verificarauto]`

**Contextos de valoración legacy (mismo coche, distinto propósito) — patrón histórico aún relevante:** la web
antigua exponía cotaciones separadas para **"Comércio e Financiamento"**, **"Contratação de Seguro"** y
**"Consulta/Vistoria de Sinistro"** (más "Reciclagem de Veículos"). `[VERIFICADO: enumeración CDX de URLs: ComercioEFinanciamento*.asp, ContratacaoDeSeguro*.asp, consultaDeSinistro.asp, VistoriaDeSinistro, menu_ReciclagemdeVeiculos.gif]`

### 3.2 Banco de Dados Molicar / "Molicar Corporate" — feed B2B

Verbatim: *"Molicar Corporate é a solução de catálogos de veículos destinado a empresas que necessitam de
informações atualizadas constantemente de forma customizada e integrada, para um alto volume de consultas diárias."*
Parámetros de contratación (selectores del formulario): **Periodicidade** (`Diário / Semanal / Quinzenal / Mensal`) ·
**Tipo de Veículo** (`Todos / Automóveis e Utilitários / Veículos Pesados / Motos`) · **Região do País** (las 12
macro-regiones de §2). Entrega: catálogo/feed completo + integración. `[VERIFICADO: página Banco-de-Dados-Molicar]`

### 3.3 Web Service / API Molicar

Existe canal de integración: icono "web_service" + `frmWebService.aspx` en el sitio; endpoint SOAP
`wsconsultamolicar.asmx` con auth por **`plngCodCliente` (código cliente) + `pstrDscSenha` (senha)**. El cliente
recibe "documento de integração + chave de acesso". `[VERIFICADO: CDX (web_service_icon.PNG, frmWebService.aspx); SOAP del microservicio; búsqueda "API Molicar"]`

### 3.4 Decoder KBB-Molicar — producto para esteira de crédito

Verbatim (MVP): *"Além da composição de **'marca, modelo, versão, ano, pacote, código KBB-Molicar'** de um veículo,
o Decoder KBB-Molicar é capaz de trazer um **cardápio de consultas** que alimenta as instituições com a **real
qualidade e atual situação cadastral** de cada veículo consultado."* Útil en financiación para **evaluar
restrições, gravames e situação cadastral**; se posiciona al **inicio de la esteira** (decodificación anticipada)
para reducir coste/tiempo de bureaus y evitar liberación de crédito sobre "preço irreal". `[VERIFICADO: MVP PDF + coxautomotive + búsqueda]`

| Datum Decoder | Significado |
|---|---|
| Marca / Modelo / Versão / Ano / Pacote | Composición exacta del vehículo |
| **Código KBB-Molicar** | Clave canónica del vehículo |
| **Situação cadastral** | Estado de registro actual del vehículo |
| **Restrições** | Restricciones administrativas |
| **Gravames** | Cargas/prendas (financiación previa) |
| (cardápio de consultas) | Menú ampliable de consultas que enriquece la decisión de crédito `[PARCIAL: lista completa no pública]` |

### 3.5 MVP — Monitor de Variação de Preços (analítica de mercado)

Informe **mensual** del "Núcleo de Estudos da KBB Brasil". Edición 66ª = **set/2025**. **23.622 versões** estudiadas
(0 km, seminovos até 3 anos, usados 4–20 anos). Dos líneas: **Leves** (autos+comerciales leves) y **Motos**. Variante
co-publicada **AutoAcrefi** (con ACREFI) en versión **Nacional + Regional + Motos**. `[VERIFICADO: MVP PDF + acrefi + cox]`

| Métrica / índice MVP | Detalle |
|---|---|
| **Variação de preço mensual (%)** | Mes vs mes anterior, separada por **0 km / seminovos / usados** (ej. set/25: 0km +0,02%, seminovos −0,32%, usados −0,24%) |
| **Comparativo por idade** | Variación % por **ano modelo** (0 km por año; seminovos por año; usados año a año 2006–2022) |
| **Comparativo por categoria** | Por carrocería: **Coupe, Roadster, Furgão, Sedan, Hatchback, Station Wagon, Picape, SUV, Minivan, Minibus** (+ Elétricos, Híbridos) × {0km, seminovo, usado} × {ago, set, média 2024} |
| **Comparativo por marca** | Variación % por marca × {0km/seminovo/usado} |
| **Comparativo por modelo** | Modelos más vendidos (Onix, HB20, Polo, Strada, Compass, Corolla, T-Cross…) |
| **Comparativo modelos elétricos / híbridos** | Bloques dedicados (Dolphin, Seal, BYD Song, etc.) |
| **Maior Valorização / Maior Desvalorização** | Destaques del mes (ej. usados: +0,71% [2012] / −1,11% [2015]) |
| **Média (2024)** | Referencia media anual de variación |
| **Valor Médio Nacional** | Base de los comparativos |
| Referencia metodológica | "única tabela especializada em precificação de veículos do mercado brasileiro" (claim de exclusividad) |

### 3.6 Productos legacy / satélite

- **Molicar Book** — guía de precios publicada (PDF/impresa), suscripción aparte (`Assine-O-Molicar-Book`). `[VERIFICADO: CDX]`
- **Molicar Peças** — precificación de **piezas/repuestos**. `[VERIFICADO: CDX molicarPecas/molicar_pecas/assinatura_peca]`
- **Molicar Vistoria** — **inspección** de vehículos. `[VERIFICADO: CDX molicar_vistoria/fale_visto]`
- **Mercado e Tendências / "O Mercado Esta Semana"** — contenido de tendencias de mercado. `[VERIFICADO: CDX]`
- **Integración Audatex** — vínculo con peritación de siniestros Audatex. `[VERIFICADO: CDX /deptos/audatex.htm]`

> **Recuento de campos atómicos únicos ≈ 45** (identificación+catálogo, valores multivalor, specs, decoder,
> índices MVP). Lista plana consolidada al final (`all_fields`).

---

## 4. Metodología / fuentes de datos

- **Volumen:** *"mais de **1 milhão de dados** sobre preços de veículos **mensalmente**"*; base de **+34 mil
  registros** (≈ **3× el portfólio de la Fipe**, ~9 mil). `[VERIFICADO: coxautomotive "por que trocar"; alvesp]`
- **Motor:** *"tecnologias de análise de dados e **Big Data** … processamento feito por um **algoritmo complexo
  alimentado semanalmente** por uma base com **mais de 800 mil informações de preços** de diferentes fontes de
  mercado, com **todos os dados avaliados diariamente por equipes especialistas**."* `[VERIFICADO: búsqueda KBB Brasil/cox]`
- **Recolección:** pesquisas **diárias** en "las fuentes más confiables y los principales centros económicos de
  Brasil", por un equipo de analistas especializado; construcción "isenta e científica". `[VERIFICADO: QuemSomos]`
- **Pronóstico (forecast):** KBB Brasil usa **prognósticos** (no medias simples) y un "algoritmo afinado validado
  diariamente"; los precios *"respeitam o histórico de cada modelo e o comportamento de preços atual"*. `[VERIFICADO: cox "por que trocar"]`
- **Individualización:** precio **por versão** (S/SE/SE Plus), **por região** y **por tipo de transação** (vs FIPE
  = un precio medio por modelo). `[VERIFICADO]`
- **Independencia:** sin vínculo con comercialización/financiación/seguro (neutralidad declarada). `[VERIFICADO: QuemSomos]`

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Portal web** | `molicar.com.br` (consulta logada, busca rápida por código + busca detalhada en cascada) | Oficial `[VERIFICADO]` |
| **App móvil** | App de la Tabela Molicar (iconos android/ios en assets) | `[VERIFICADO: assets CDX + snippets "aplicativos móveis"]` |
| **Portal hermano** | `kbb.com.br` (KBB Brasil) | `[VERIFICADO]` |
| **Banco de Dados / feed B2B** | Catálogo completo customizado, periodicidad **diario/semanal/quincenal/mensual**, por región y tipo de vehículo; alto volumen | `[VERIFICADO]` |
| **Web Service / API** | SOAP (`wsconsultamolicar.asmx`), auth por código de cliente + senha; "documento de integração + chave de acesso" | `[VERIFICADO el SOAP; si hoy hay REST = PARCIAL]` |
| **Informe PDF (MVP)** | Mensual, Leves + Motos, vía `coxautomotive.com.br`; co-edición AutoAcrefi | `[VERIFICADO]` |
| **Integración crédito (Decoder)** | Inyección del dossier de garantía en la **esteira de financiamento** de las IFs | `[VERIFICADO]` |
| **Integración peritación** | **Audatex** (siniestros) | `[VERIFICADO: CDX]` |
| Contacto comercial B2B | `comercial@coxautomotive.com.br` · `kbb.com.br` | `[VERIFICADO: MVP PDF]` |

---

## 6. Precio

- **Consulta web:** modelo **freemium** — registro gratuito con **consultas gratis limitadas** (terceros citan
  "**2 buscas gratuitas por conta**"), luego **suscripción de pago**. `[VERIFICADO freemium; nº exacto PARCIAL]`
- **Paquetes de cotações (modelo histórico verificado en assets):** botones **250 / 500 / 1000 / 2000** consultas +
  **"Ilimitada"**; pago por **boleto** y **tarjeta (Redecard)**. Páginas `planos.aspx` / `frmAssTabelaMolicar.aspx`. `[VERIFICADO: CDX btn_250/500/1000/2000, btn_ilimitada, boleto3.aspx, retornoredecard.aspx]`
- **Banco de Dados / Corporate / API / Decoder:** **precio por contrato** (cotización vía formulario; sin tarifa
  pública). `[VERIFICADO el modelo quote-based; importes NO-VERIFICADO]`
- **MVP:** informe **gratuito** descargable (coxautomotive.com.br). `[VERIFICADO]`
- ⚠ Importes exactos en R$ de las suscripciones actuales: **`[NO-VERIFICADO]`** (tras login).

---

## 7. Placement (patrón web — clave para cardeep)

> Molicar es el **arquetipo "multivalor regional" que cardeep debe imitar** para un país con guía rica (lo
> opuesto al patrón "ancla única" de FIPE). El flujo es **drill-down jerárquico** y el resultado es una **ficha
> con varios precios** (transacción × condición) sobre un **catálogo de specs**, todo **anclado a región**.

**A. Home ("Molicar Digital").** Hero con claim ("a melhor e mais completa ferramenta de precificação"), CTA
**ASSINE / Cadastre-se**, caja de **login del assinante** y CTA secundario **"Ver Banco de Dados"** (separación
clara consumidor vs corporativo). `[VERIFICADO]`

**B. Pantalla de consulta (TabelaMolicar) — dos modos:**
- **"Faça a busca rápida"** — input único por **código Molicar** → Enviar. (atajo experto)
- **"Faça a busca detalhada"** — formulario en pasos numerados:
  1. **Selecione a categoria** (radios con icono): veículos · motocicletas · caminhões · ônibus · implementos rodoviários.
  2. **Selecione o Estado** (dropdown 27 UF, "São Paulo" por defecto). ← **la región se elige ANTES del precio**.
  3. **Marca → Ano Fabricação → Ano Modelo → Modelo → Versão** (dropdowns en cascada) → **Enviar**.

**C. Ficha de resultado (cotação).** Specs del vehículo (plazas, peso, cc, CV, combustível) + **bloque de precios
multivalor** (particular-particular, particular-lojista, 0km/usado) + **controles editables** (km, cor, opcionais)
que **recalculan** el valor + **código Molicar** + opción **Imprimir**. Histórico: **fichas separadas por contexto**
(Comércio/Financiamento, Seguro, Sinistro). `[VERIFICADO estructura; etiquetas exactas PARCIAL tras login]`

**D. Planos / ContratarAssinatura.** Tarjetas de paquetes (250/500/1000/2000/ilimitada) → pago boleto/Redecard.
(La ruta actual `/TabelaMolicar/ContratarAssinatura` hace **302 → login**.) `[VERIFICADO]`

**E. Banco de Dados Molicar (B2B).** Formulario de cotización con 3 ejes: **Periodicidade / Tipo de Veículo /
Região do País** + datos de empresa (CNPJ). `[VERIFICADO]`

**F. MVP (PDF).** Sumário navegável: Introdução · Critérios · Relatório de Mercado · Comparativo por idade ·
por categoria · por marca · por modelo · (elétricos) · (híbridos) · Importante · Contato. Cada comparativo =
**tabla {ago, set, média 2024} × {0km, seminovo, usado}**. `[VERIFICADO]`

**Lección de colocación para cardeep:**
1. **Región primero, precio después** — el UF/región se selecciona en el paso 2 del drill-down, no como filtro
   posterior; el precio nace ya regionalizado. cardeep debe tratar la región como **dimensión de primera clase**.
2. **El resultado es una matriz, no un número** — colocar `transacción (particular/lojista) × condición (0km/usado)`
   como rejilla, con specs (cc/CV/plazas/peso) al lado y **controles km/cor/opcionais que recalculan en vivo**.
3. **Código Molicar = join key** (como `codigoFipe` o el VIN) → mostrarlo siempre como ancla de identidad.
4. **Doble vía de entrada:** "busca rápida" por código (experto) + "busca detalhada" en cascada (novato) → cardeep
   debería ofrecer ambos.
5. **Separar superficies por audiencia:** consumidor (ficha) · corporativo (feed/Banco de Dados) · crédito
   (Decoder, dossier en la esteira) · mercado (MVP/dashboard de variación). Cada dato vive donde su consumidor lo usa.
6. **El Decoder es el patrón "valor + situación cadastral en el punto de decisión de crédito"** — cardeep puede
   colocar la huella de precificación justo al inicio del flujo de financiación, no como consulta aislada.

---

## 8. Diferencial (lo que ofrece y otras —FIPE— no)

1. **Precio regional** (27 UF / 12 macro-regiones) — FIPE da **media nacional única**; KBB-global no regionaliza Brasil.
2. **Precio por versão/trim** (S/SE/SE Plus) — FIPE colapsa versiones en un precio por modelo.
3. **Multivalor por transacción** (particular↔particular, particular↔lojista, 0km, usado) — FIPE = un solo valor.
4. **Ajuste por km, cor, opcionais, blindagem y estado** — FIPE ignora todo eso (solo versión de fábrica).
5. **Catálogo de specs por versión** (plazas, peso, cc, CV, combustível) embebido en la cotación.
6. **Mayor cobertura de tipos:** carros, motos, caminhões, **ônibus** e **implementos rodoviários** (baús,
   cegonhas, tanque) — FIPE no cubre ónibus/implementos así.
7. **Decoder KBB-Molicar** para la **esteira de crédito** (situação cadastral, restrições, gravames) — único en el
   nicho de precificación brasileño.
8. **Analítica de mercado (MVP)** mensual con variación por idade/categoria/marca/modelo + elétricos/híbridos +
   maior valorização/desvalorização + co-edición AutoAcrefi (nacional+regional) — FIPE no publica analítica.
9. **Metodología forecast + Big Data** (800 mil precios/semana, 1M+ datos/mes, validación diaria) vs media simple.
10. **Respaldo Cox Automotive / marca KBB global** (escala, tecnología, integraciones DMS/crédito/peritación).
11. **Feed B2B configurable** por periodicidad/región/tipo (diario→mensual) + **Web Service**.

---

## 9. Gaps (lo que NO ofrece / no verificado)

1. **Solo Brasil** — hueco geográfico (cardeep es multinacional).
2. **Sin API REST pública documentada / sin developer portal** — la integración es **SOAP legacy + contrato + chave**;
   no hay docs abiertas. (El único cliente open-source quedó archivado en 2020 "por mudanças da Molicar".) `[VERIFICADO]`
3. **Sin historial de vehículo nativo** (siniestros, dueños, odómetro histórico, leilão). El **Decoder** da
   situação cadastral/restrições/gravames pero el **histórico completo** procede de **bureaus externos**, no de Molicar.
4. **Sin métricas de velocidad de mercado:** ni **days-to-sell**, ni **market days supply**, ni **price-to-market %**,
   ni **índice oferta/demanda**, ni volumen de anuncios. El MVP da **variación de precio**, no rotación de stock.
5. **Sin curva de depreciación / valor residual % a futuro** como producto publicado (usa forecast interno; no hay
   un producto tipo ALG/residual-value como tal). `[PARCIAL: forecast existe internamente]`
6. **Sin marketplace / inventario en vivo** (eso es Manheim/Autotrader del grupo, no Molicar).
7. **Sin MSRP/invoice de coche nuevo, sin incentivos/TCO, sin reviews/contenido editorial** (a diferencia de KBB.com US).
8. **Transparencia de salida limitada:** las **etiquetas exactas del resultado** y los **precios de suscripción**
   están **tras login** → `[PARCIAL]` / `[NO-VERIFICADO]`.
9. **Subdominio `valuation`:** **sin contenido público verificable** — `valuation.molicar.com.br` **no tiene
   registros en Wayback** y **no resuelve** un A record real (la "resolución" IPv6 observada es un comodín
   sintético del resolver local, mismo IP que un sitio israelí no relacionado). Probable endpoint interno/B2B o
   inactivo. **No se inventa contenido.** `[VERIFICADO la ausencia]`
10. **Acceso geobloqueado** (403 fuera de Brasil) → fricción para due-diligence externa y para scraping cross-border.
11. **"34 mil registros":** ambigüedad fuente (¿versiones vivas vs. price-records?); citado como "34 mil" / "+34 mil"
    de forma inconsistente. `[PARCIAL]`

---

## 10. Fuentes

- Propiedad / adquisición Cox (mayoría, 13-abr-2016): https://www.prnewswire.com/news-releases/cox-automotive-purchases-majority-stake-in-molicar-300251143.html · https://www.coxautoinc.com/kelley-blue-book-brazil-2/ · https://www.coxautoinc.com/stories/kelley-blue-book-brazil/
- Identidad / historia (fundación 1992, 1ª tabela jun/1994, independencia, cartera de clientes): `molicar.com.br/QuemSomos` (vía Wayback `web.archive.org/web/2026*/https://molicar.com.br/QuemSomos`) · LinkedIn `br.linkedin.com/company/molicar-publicações-automotivas-ltda` · Crunchbase `crunchbase.com/organization/molicar`
- Marcas hermanas Cox Brasil + "Sobre a Cox" (KBB Brasil, Molicar, Dealertrack, Manheim): MVP PDF (abajo) · https://www.coxautomotive.com.br/ · https://www.coxautomotive.com.br/marcas/ · https://www.coxautomotive.com.br/marcas/molicar/ · https://www.coxautomotive.com.br/marcas/kbb/
- Tabela Molicar — campos/UI/cascada/estados/marcas: `molicar.com.br/TabelaMolicar` (Wayback) · `molicar.com.br/` home "Molicar Digital" (Wayback)
- Banco de Dados / Molicar Corporate (periodicidade/tipo/região): `molicar.com.br/Solucoes-Corporativas/Banco-de-Dados-Molicar` (Wayback) · https://molicar.com.br/Solucoes-Corporativas/Banco-de-Dados-Molicar
- Campos SOAP reales (`CodMolicar`, `ValCotacao`, `ValCotacaoCompleto`, `QtdPassageiro/QuiloPeso/CCMotor/CV`, `CodMarca/Modelo/Categoria/MacroCategoria`, `plngCodVersao/AnoModelo`, `pblnIndZeroKM`, endpoint `wsconsultamolicar.asmx`): https://github.com/deividfortuna/molicar (lib/soap-molicar.js, app/car-info-repository.js, app/controller-v1.js)
- Multivalor (transacción), versión (S/SE/SE Plus), región, km/cor/opcionais, forecast, 34k vs 9k FIPE, 1M/mes: https://coxautomotive.com.br/por-que-voce-deve-trocar-a-fipe-pela-kbb-brasil/ · https://alvesp.com.br/kbb-brasil-molicar/ · https://blog.inter.co/tabela-molicar/ · https://infocar.com.br/blog/molicar-e-fipe-qual-a-diferenca-das-tabelas/ · https://tabelacarros.com/post/tabela-fipe-x-kbb-x-molicar-qual--a-melhor · https://verificarauto.com.br/tabela-molicar/
- Metodología Big Data (800 mil precios/semana, validación diaria), MVP 25k+ versões, segmentos: WebSearch KBB Brasil + https://www.coxautomotive.com.br/?page_id=112
- Informe MVP (set/2025, 23.622 versões, comparativos, Decoder KBB-Molicar, categorías de carrocería): https://www.coxautomotive.com.br/wp-content/uploads/2021/12/Relatorio-MVP-Setembro-2025-Final-2.pdf (PDF descargado y extraído con pdftotext) · MVP Motos: …/Relatorio-MVP-Motos-Novembro-2025-Final.pdf
- AutoAcrefi (nacional+regional+motos): https://acrefi.org.br/wp-content/uploads/2026/01/NOV-25-Cox-Acrefi_Leves-Nacional-Regional-Motos_Nov2025-1_compressed.pdf
- Decoder KBB-Molicar (situação cadastral/restrições/gravames, esteira de crédito): MVP PDF (diagrama "decoder antecipado") + WebSearch
- Cobertura de tipos (carros/motos/caminhões/ônibus/implementos baús/cegonhas/tanque), 35 años, freemium: https://infocar.com.br/blog/molicar-e-fipe-qual-a-diferenca-das-tabelas/ · https://www.molicar.com.br/ (Wayback) · https://blog.pier.digital/tabela-molicar/ · https://seucreditodigital.com.br/tabela-molicar-saiba-como-funciona-essa-tabela-de-avaliacao-de-veiculos/
- Productos/plan legacy + pago (Molicar Book/Peças/Vistoria, Audatex, planos 250/500/1000/2000/ilimitada, boleto/Redecard, Web Service): enumeración Wayback CDX `web.archive.org/cdx/search/cdx?url=molicar.com.br&matchType=domain`

### Notas de verificación
- **WAF + geobloqueo:** `*.molicar.com.br` y `kbb.com.br` → **403** a WebFetch y a Playwright headless. La UI/flujo
  se reconstruyó con **snapshots reales de Wayback** (capturados en el `navigate`, **antes** del script de
  redirección malicioso que llevaba a un dominio israelí no relacionado — artefacto del archivo). `coxautomotive.com.br`
  **sí** responde y aportó el corporativo + PDFs.
- **Campos atómicos (SOAP):** nombres **reales** del web service oficial vía espejo open-source; las **etiquetas de
  pantalla del resultado autenticado** son `[PARCIAL]`. La API legacy quedó "Não funciona devido a mudanças da
  Molicar" (archivado 2020) → si hoy migraron a REST = `[NO-VERIFICADO]`.
- **Subdominio `valuation`:** CDX devolvió **0 registros**; Chromium da `ERR_NAME_NOT_RESOLVED`; el `nslookup` IPv6
  era un **comodín sintético/hijack del resolver local**. Ausencia de contenido público **verificada**; no inventado.
- **Doble fuente** lograda en: propiedad Cox (prnewswire + coxautoinc + MVP), fundación 1992 (QuemSomos + LinkedIn),
  multivalor/versión/región (cox + alvesp + inter + infocar), 34k vs 9k (cox + alvesp), tipos de vehículo (UI + infocar).
- **No verificado (no inventado):** importes R$ de suscripción actuales · nº exacto de consultas gratis hoy ·
  lista completa del "cardápio" del Decoder · forma exacta de la API actual (REST/SOAP) · render pixel-exacto del
  resultado logado.
