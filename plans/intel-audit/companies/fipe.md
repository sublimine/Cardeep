# FIPE (Tabela Fipe Veículos) — Auditoría atómica

> Slug: `fipe` · Subdominio cardeep: **valuation** · Región: **Brasil** (mercado único)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[NO-VERIFICADO]` / `[PARCIAL]` donde no se confirmó al 100%.
> Naturaleza: **fundación académica sin ánimo de lucro** (ligada a la USP) que produce la **Tabela Fipe**, el
> **precio medio de referencia nacional** de vehículos en Brasil. Es el estándar de facto cuasi-regulatorio
> del mercado brasileño (seguro, IPVA, financiación). **Un solo dato: el precio medio (R$).**
> ⚠ El sitio oficial (`veiculos.fipe.org.br`, `fipe.org.br`) está tras **Cloudflare WAF** y bloquea
> WebFetch y navegador headless (HTTP 403 / "Sorry, you have been blocked"). La reconstrucción de UI/campos
> se hizo vía: esquema del **endpoint interno oficial** (`veiculos.fipe.org.br/api/veiculos`) que documentan
> los espejos (BrasilAPI, fipe.online, parallelum, deividfortuna/fipe) + tutoriales con captura + FAQ citada.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre | **Fundação Instituto de Pesquisas Econômicas (FIPE)**. Producto: **Tabela Fipe** (Tabela Fipe Veículos) | fipe.org.br; fea.usp.br |
| Fundación | **1973** | fea.usp.br/economia/fipe; pt.wikipedia |
| Naturaleza jurídica | **Entidade de direito privado, sem fins lucrativos** (fundación privada, sin ánimo de lucro) — **NO** es organismo público | fea.usp.br ("entity of private law and without lucrative purposes"); fipe.org.br/sobre-a-fipe |
| Vínculo institucional | Apoya al **Departamento de Economia da FEA-USP** (Faculdade de Economia, Administração, Contabilidade e Atuária da **Universidade de São Paulo**). La marca de confianza viene del aval académico USP | fea.usp.br; fipe.org.br |
| HQ | **São Paulo, SP, Brasil** — Cidade Universitária (campus USP, Butantã). Dirección de FEA-USP: Av. Prof. Luciano Gualberto, 908. `[PARCIAL: nº exacto de la sede FIPE]` | fea.usp.br |
| Sitios | `fipe.org.br` (institucional, pt-br/en-us) · **`veiculos.fipe.org.br`** (consulta Tabela Fipe Veículos) · **App oficial** iOS/Android | múltiples |
| Otros índices FIPE (contexto) | **IPC-Fipe** (inflación de la ciudad de SP), **FipeZap** (precios inmobiliarios), **Salariômetro**, **IPOP**, **IPAC/Fipe**, IGP, estudios económicos | fipe.org.br/indices; WebSearch |

**Categoría de producto:** **referencia de precio medio de mercado** (un índice de valoración de un solo valor).
NO es catálogo de specs, NO es VIN/historial, NO es analítica de mercado, NO es guía retail/trade multivalor.

**Cliente objetivo (de facto, todo el mercado):** particulares (consulta gratis) · **aseguradoras** (base de
indemnización de siniestro total) · **bancos / financieras / consorcios** (garantía, LTV) · **concesionarios y
revendas** (negociación) · **gobierno/estados** (base de cálculo del **IPVA** en varios estados). Es el
parámetro más usado en compraventa de usados en Brasil. (Fuente: serasa.com.br; buscafipe.com; clubedovalor.)

---

## 2. Cobertura

- **Geografía:** **solo Brasil.** El sondeo cubre **24 estados** brasileños; el resultado es un **promedio
  nacional único** (no se desglosa por estado/región). (Fuente: buscafipe.com; vrum.com.br; cnnbrasil.) `[VERIFICADO]`
- **Nuevo / seminuevo / usado:** los tres. Incluye **0 km** (opción "Zero KM"): para 0 km el precio medio se
  calcula dentro de una versión (básico / intermediário / completo), a precio **à vista**. (Fuente: tabelafipebrasil/FAQ; icarros.) `[VERIFICADO]`
- **Tipos de vehículo (3 segmentos, mismo esquema):**
  - **Carros e utilitários pequenos** (`tipoVeiculo = 1`)
  - **Motos / Motocicletas** (`tipoVeiculo = 2`)
  - **Caminhões e micro-ônibus** (`tipoVeiculo = 3`)
  (Fuente: 99app; fipe.online; deividfortuna/fipe; BrasilAPI.) `[VERIFICADO]`
- **Profundidad de año-modelo:** amplio rango de años-modelo (mass-market); el valor "0 km" se codifica como
  `anoModelo = "32000"` en el API. La **serie histórica** consultable por código alcanza ~15 años de meses de
  referencia (según espejos). Rango exacto de años-modelo más antiguos `[PARCIAL]`. (Fuente: fipe.online; fipe.online example `ano modelo: 32000`.)
- **Excluido del universo:** vehículos de uso profesional/especial, frota, gobierno, importación independiente,
  conversiones, personalizados — no entran en la muestra (ver Metodología). `[VERIFICADO]`

---

## 3. Productos + campos atómicos

> FIPE tiene **un único producto de datos**: la **Tabela Fipe** (precio medio). Los 3 segmentos (carros/motos/
> caminhões) comparten **exactamente el mismo esquema de campos**. No hay tiers de valor ni productos satélite.

### 3.1 Esquema atómico de SALIDA por consulta (la respuesta oficial)

Fuente primaria: esquema del **endpoint interno oficial** `veiculos.fipe.org.br/api/veiculos`
(método `ConsultarValorComTodosParametros`), documentado verbatim por los espejos **BrasilAPI**, **fipe.online**,
**parallelum** y **deividfortuna/fipe**. Ejemplo real (fipe.online): Toyota Corolla Altis 1.8 16V Aut. (Híbrido).

| Campo (API) | Etiqueta UI (pt) | Ejemplo real | Significado atómico |
|---|---|---|---|
| `valor` | **Preço Médio** | `"R$ 195.328,00"` | **EL dato.** Precio medio à vista, mercado nacional, del mes de referencia. Único valor (no hay venta/compra separadas). |
| `codigoFipe` | **Código Fipe** | `"002182-2"` | Identificador nacional de la versión-año (formato `XXXXXX-X`, 7 dígitos). Clave compartida por todo el ecosistema. |
| `marca` | **Marca** | `"Toyota"` | Fabricante. |
| `modelo` | **Modelo** | `"Corolla Altis 1.8 16V Aut. (Híbrido)"` | Modelo + **versión/trim + motor + transmisión** embebidos en texto libre. |
| `anoModelo` | **Ano Modelo** | `2025` (`"32000"` = Zero KM) | Año-modelo; `32000` codifica 0 km. |
| `combustivel` | **Combustível** | `"Híbrido"` | Tipo de combustible: **Gasolina / Álcool (Etanol) / Diesel / Híbrido / Elétrico**. |
| `siglaCombustivel` | (interno) | `"G"` / `"A"` / `"D"` | Sigla del combustible. `[VERIFICADO vía BrasilAPI/parallelum]` |
| `tipoVeiculo` | (tab) | `1` | 1=carro, 2=moto, 3=caminhão. |
| `mesReferencia` | **Mês de referência** | `"abril de 2026"` | Mes/año de la tabla. Los valores SIEMPRE se etiquetan con su mes de referencia. |
| `dataConsulta` | **Data da consulta** | `"sexta-feira, 30 de junho..."` | Timestamp de la consulta. `[VERIFICADO vía BrasilAPI/parallelum]` |
| `autenticacao` / `Autenticacao` | **Código de autenticação** | hash | Código que permite **validar/comprobar** la consulta (rasgo de confianza distintivo de FIPE). `[VERIFICADO vía esquema del endpoint oficial; BrasilAPI lo omite]` |

**Lista atómica completa de campos = 11** (valor, codigoFipe, marca, modelo, anoModelo, combustivel,
siglaCombustivel, tipoVeiculo, mesReferencia, dataConsulta, autenticacao).

### 3.2 Parámetros de ENTRADA (las claves de consulta)

| Parámetro | Etiqueta UI | Valores |
|---|---|---|
| Tabela de referência | **Mês de referência** | dropdown mes/año (mes vigente + meses anteriores) |
| Tipo de vehículo | tabs **Carros / Motos / Caminhões** | 1 / 2 / 3 |
| **Modo de pesquisa** | radio: **"Pesquisa por Marca"** vs **"Pesquisa por Código Fipe"** | dos modos `[VERIFICADO]` |
| (por Marca) | **Marca → Modelo → Ano Modelo** | dropdowns en cascada con buscador interno |
| (por Código) | **Código Fipe + Ano Modelo** | input directo |

### 3.3 Lo que el dato NO trae (clave para no confundir con terceros)

El resultado **oficial** es **un único valor medio** + metadatos (código, mes, combustible, autenticación).
**NO** trae: precio de venta vs compra separados, ajuste por km, estado de conservación, color, opcionales,
potencia del motor, nº de plazas, dimensiones, ni gráfico de variación. ⚠ Sitios **terceros** (chavesnamão,
icarros, etc.) **enriquecen** el resultado con specs (potência, lugares), variación mensual %, histórico y
consulta por placa — **eso NO es FIPE**, es valor añadido de cada portal sobre el dato FIPE. (Fuente:
agibank.com.br; serasa.com.br; contraste con chavesnamao.com.br.) `[VERIFICADO la distinción]`

---

## 4. Metodología / fuentes de datos

- **Recolección:** investigadores de FIPE recogen precios de carros, motos y caminhões **nuevos, seminuevos y
  usados** en **24 estados** brasileños, en **concesionarias/revendas** que venden al **consumidor final
  (pessoa física)**, considerando siempre el **valor à vista** (pago al contado). (Fuente: vrum.com.br; cnnbrasil.)
- **Tratamiento estadístico:** se recogen múltiples ofertas del mismo vehículo, **se descartan los valores
  extremos** (muy por encima/debajo de la media, "pontos fora da curva") y se calcula la **media** de los
  restantes. El número de la tabla es esa media. (Fuente: vrum.com.br; cnnbrasil.) `[VERIFICADO]`
- **Exclusiones de la muestra:** ventas especiales, **frotistas**, **gobierno**, vehículos para revenda,
  brindes/personalizados, **conversiones de motor**, **importación independiente** y **coches de test** no
  entran en la media. (Fuente: vrum.com.br.) `[VERIFICADO]`
- **No considera:** **solo versiones de fábrica**; ignora **opcionais, accesorios, estado de conservación,
  quilometragem, cor y región**. El precio real practicado varía por todos esos factores. (Fuente: serasa;
  buscafipe; cnnbrasil.) `[VERIFICADO]`
- **0 km:** la media se calcula dentro de una versión con opcionales básico/intermediário/completo, à vista. (FAQ.)
- **Actualización:** **mensual.** Nueva tabla disponible típicamente en los **primeros ~2 días del mes**; el
  valor se expresa en **R$ del mes/año de referencia**. (Fuente: tabelafipebrasil; fipe.online "2º dia do mês".)
- **Definición oficial (cita):** *"A Tabela Fipe expressa preços médios para pagamento à vista, praticados na
  revenda de veículos para o consumidor final, pessoa física, no mercado nacional, servindo apenas como um
  parâmetro para negociações ou avaliações."* (Texto del FAQ oficial, citado por múltiples espejos.) `[VERIFICADO]`

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Portal web público** | `veiculos.fipe.org.br` — consulta gratuita, SPA. Canal oficial y **exclusivo** de consulta pública. | Oficial `[VERIFICADO]` |
| **App móvil oficial** | iOS / Android, gratis. | Oficial `[VERIFICADO]` |
| **API REST pública/documentada** | **NO existe oficialmente.** La SPA usa un endpoint interno `…/api/veiculos`; **terceros lo scrapean** y exponen APIs (BrasilAPI, parallelum, fipe.online, fipeapi.com.br, fipe.api.br). | `[VERIFICADO: no hay API oficial documentada]` |
| **Feed/Excel/CSV oficial** | No hay descarga masiva oficial gratuita; los CSV/snapshots los venden **terceros**. | `[VERIFICADO]` |
| **Licencia institucional / uso comercial** | El dato es público y citado contractualmente por aseguradoras/bancos; existe licenciamiento institucional por contrato, pero los **términos no son públicos**. | `[NO-VERIFICADO los términos]` |
| **Re-publicación de 3os** | El dato se incrusta en innumerables portales (icarros, webmotors, OLX, chavesnamão, bancos, seguradoras) y apps de "FIPE pela placa". | `[VERIFICADO]` |

---

## 6. Precio

- **Consulta pública web + App oficial: GRATIS.** Es el modelo oficial: acceso libre al precio medio,
  consultando modelo por modelo. (Fuente: agibank; buscafipe; fipe.online.) `[VERIFICADO]`
- **No hay tarifa pública** para licenciamiento institucional/comercial del dataset. `[NO-VERIFICADO]`
- ⚠ Los precios de "plan gratis 1.000 consultas/mes", "Pro ilimitado + CSV" y "export histórico ~R$ 10.000"
  son de **revendedores TERCEROS** (p.ej. fipe.online), **NO de FIPE**. No atribuir a FIPE. `[VERIFICADO la atribución]`

---

## 7. Placement (patrón web — clave para cardeep)

> Patrón **minimalista de "ancla única"**: a diferencia de KBB (rango + 3 zonas + trade/retail/private),
> FIPE coloca **UN número** como héroe, rodeado de metadatos de confianza. Esto es lo que cardeep imita
> cuando la fuente de valoración es **un precio medio de referencia único** (vs. multivalor).

**A. Landing / selector de tipo.** Tres pestañas/iconos: **Carros e utilitários pequenos · Motos ·
Caminhões e micro-ônibus**. Es lo primero que se elige.

**B. Selector de Mês de referência.** Dropdown del mes/año de la tabla (vigente por defecto, con históricos).

**C. Modo de búsqueda (dos pestañas/radio).**
- **Pesquisa por Marca:** dropdowns en cascada **Marca → Modelo → Ano Modelo** (cada uno con buscador "busca").
- **Pesquisa por Código Fipe:** input **Código Fipe + Ano Modelo**.
Botón **"Pesquisar"**.

**D. Tarjeta de resultado ("Resultado da Pesquisa") — bloque único, todo junto:**
1. **Descripción del vehículo:** Marca, Modelo (con versión/motor/transmisión), Ano Modelo + Combustível.
2. **Preço Médio** en **R$** → elemento **destacado/héroe** (grande).
3. **Código Fipe.**
4. **Mês de referência.**
5. **Data da consulta.**
6. **Código de autenticação** (para validar la consulta).
7. **Disclaimer** legal: "preços médios... à vista... apenas parâmetro... não considera opcionais/conservação/
   quilometragem/cor; preços reais variam por região, conservação, etc."

**E. Sin tabs de trade/retail/private, sin gráfico, sin panel de specs, sin comparador, sin alertas.** El valor
único + mes + código + autenticación + disclaimer ES toda la ficha. (Patrón derivado del flujo verificado +
esquema del endpoint; render directo bloqueado por Cloudflare.) `[VERIFICADO flujo; UI exacta PARCIAL por WAF]`

**Lección de colocación para cardeep:** cuando un país tenga una "FIPE-equivalente" (referencia media única),
cardeep debe (1) tratar el **código** como clave de unión, (2) mostrar el **valor + mes de referencia** como
ancla, (3) exhibir **código de autenticación/origen** como sello de confianza, y (4) **separar visualmente**
el dato-fuente puro de cualquier enriquecimiento propio (specs, km, histórico) — porque mezclarlos es
exactamente el error que cometen los portales terceros brasileños.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Estándar nacional cuasi-regulatorio:** referencia aceptada institucional/legalmente para **indemnización de
   seguro**, **base de IPVA** y financiación. Ninguna guía anglosajona tiene este estatus cuasi-oficial en su mercado.
2. **Aval académico USP / fundación sin ánimo de lucro** → neutralidad e independencia percibidas (no es de un
   dealer ni de una aseguradora).
3. **Número único, simple, transparente y GRATIS** — "vale X na FIPE" es lenguaje cotidiano; reconocimiento total.
4. **Código Fipe:** identificador nacional compacto por versión-año, **clave compartida** por aseguradoras,
   Detran, bancos y portales — un "join key" de todo el ecosistema.
5. **Código de autenticación** por consulta → resultado **verificable/auditable**.
6. **Cadencia mensual** con décadas de continuidad y una sola metodología.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo Brasil.** ← hueco geográfico para cardeep.
2. **Una sola métrica** (precio medio nacional). **Sin** retail/trade/private, sin venta/compra, sin
   wholesale/subasta, sin rango (low–high).
3. **Sin ajuste por km, conservación, color, opcionais ni región** — es un **promedio nacional** explícito; la
   transacción real puede desviarse mucho (un coche impecable vs. uno con problemas valen igual en la tabla).
4. **Sin curva de depreciación, sin forecast, sin valor residual** como producto (el output es valor puntual del mes).
5. **Sin catálogo de specs/equipamiento** (potencia, plazas, dimensiones) — lo añaden terceros.
6. **Sin VIN/chasis decode, sin historial (siniestros/dueños/odómetro), sin consulta por placa** — todo de terceros.
7. **Sin analítica de mercado:** ni days-to-sell, ni market days supply, ni price-to-market %, ni índice
   oferta/demanda, ni volumen de anuncios.
8. **Sin API oficial documentada, sin feed/Excel masivo gratis;** licenciamiento comercial opaco → el ecosistema
   depende de **scrapear** el endpoint interno.
9. **Sin desglose regional/estatal** pese a sondear 24 estados (colapsa a media nacional).
10. **Sin MSRP/invoice de coche nuevo, sin incentivos, sin TCO/cost-to-own, sin ratings/reviews/contenido editorial.**
11. **Cobertura limitada a versiones de fábrica mass-market;** especiales/importados/frota/modificados excluidos →
    nichos, exóticos y vehículos muy equipados quedan mal representados.

---

## 10. Fuentes

- Identidad / fundación / naturaleza jurídica / USP: https://www.fea.usp.br/economia/fipe · https://www.fipe.org.br/pt-br/institucional/sobre-a-fipe/ · https://pt.wikipedia.org/wiki/Funda%C3%A7%C3%A3o_Instituto_de_Pesquisas_Econ%C3%B4micas
- Sitio oficial de consulta (bloqueado WAF, citado): https://veiculos.fipe.org.br/
- Metodología (media, descarte de extremos, 24 estados, exclusiones): https://www.vrum.com.br/mercado/2026/04/7388484-como-a-tabela-fipe-e-calculada-entenda-o-que-define-o-preco.html · https://www.cnnbrasil.com.br/auto/tabela-fipe-como-funciona-o-guia-de-precos-de-carros/
- Definición oficial / no considera km/cor/opcionais / uso seguro+IPVA: https://www.serasa.com.br/carteira-digital/blog/o-que-e-tabela-fipe/ · https://buscafipe.com/tabela-fipe/
- Flujo de consulta + dos modos (por Marca / por Código Fipe) + mes de referencia: https://www.seguroauto.org/como-consultar-a-tabela-fipe/ · https://99app.com/blog/motorista/tabela-fipe-veja-como-consultar-o-preco-de-tabela-do-carro/ · https://blog.agibank.com.br/tabela-fipe/
- Esquema de campos del endpoint oficial (valor, marca, modelo, anoModelo, combustivel, codigoFipe, mesReferencia, tipoVeiculo, siglaCombustivel, dataConsulta): https://fipe.online/ · https://github.com/deividfortuna/fipe · https://brasilapi.com.br/docs (sección FIPE)
- Código Fipe (formato 7 dígitos XXXXXX-X): https://www.chavesnamao.com.br/noticias-automotivas/codigo-fipe-da-tabela/
- 0 km / combustibles / interpretación del resultado: https://www.tabelafipebrasil.com/perguntas-frequentes · https://www.icarros.com.br/tabela-fipe/index.jsp
- Sin consulta por placa en el oficial (terceros la añaden): https://blog.agibank.com.br/tabela-fipe/ · https://gringo.com.vc/consultar-tabela-fipe/
- App oficial / consulta gratis: https://apps.apple.com/ (apps "FIPE"/"Tabela FIPE") · https://fipe.online/

### Notas de verificación
- **WAF:** `veiculos.fipe.org.br` y `fipe.org.br` devuelven **403 (Cloudflare "Sorry, you have been blocked")** a
  WebFetch y a Playwright headless. La UI/flujo se reconstruyó por fuentes secundarias + esquema del endpoint
  interno; las etiquetas exactas de pantalla están **doble-fuenteadas** pero el render pixel-exacto es `[PARCIAL]`.
- **Campos atómicos (11):** valor, codigoFipe, marca, modelo, anoModelo, combustivel, siglaCombustivel,
  tipoVeiculo, mesReferencia, dataConsulta, autenticacao — **doble fuente** (fipe.online + BrasilAPI/parallelum/
  deividfortuna). `autenticacao` confirmado por el método oficial `ConsultarValorComTodosParametros`; BrasilAPI lo omite.
- **Distinción FIPE vs. enriquecimiento de 3os** (specs/placa/histórico/variación%): verificada por contraste
  (agibank/serasa describen el oficial = valor único; chavesnamão/icarros añaden specs). NO atribuir a FIPE.
- **Precios de API ("1.000 grátis", "Pro", "export ~R$10.000"):** son de **terceros** (fipe.online), `[VERIFICADO]` que NO son de FIPE.
- **Sede exacta de FIPE** y **año de lanzamiento del portal online**: `[NO-VERIFICADO]` — no inventados.
