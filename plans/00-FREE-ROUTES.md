# CARDEEP - Rutas 100% gratuitas (cero dinero)

> Dossier institucional de las **money-gates** del censo CARDEEP y su ruta EUR0
> verificada. Para cada compuerta: la ruta ganadora, los fallbacks, los pasos de
> integracion, el riesgo residual y los huecos honestos. La doctrina del proyecto
> es **coste-cero hasta tener el sistema A->Z configurado**; el gasto, cuando
> exista, es la ultima fase y decision final del owner. Prosa en espanol; codigo,
> rutas y nombres de herramienta en ingles.
>
> Estado de la cosecha al redactar: **PARADA desde 2026-06-15**. Tier-1 antideteccion
> construido pero **nunca usado en cosecha real** (todo Tier-0 sobre IP del host).
> Bug vivo bloqueante: `pipeline/platform/coches_net_facet.py:295` (7 args vs 8
> requeridos) hace crashear el cosechador canonico de coches.net hoy mismo.

---

## Indice de compuertas

**Compuertas conocidas (sintesis por-gate)**
1. egress-ip — IP de salida grado-ES que pase el IP-gate de DataDome/PerimeterX y rote
2. antibot-engine — motor anti-bot FOSS sin AGPL para el cascade Tier-0->Tier-1
3. llm-edge — LLM EUR0 para extraccion de recetas P04 + tiebreak de identidad P06
4. geo-places — enumeracion de POIs sin Google Places para el vector GEO de P01
5. captcha-solve — DataDome / hCaptcha / reCAPTCHA a EUR0 sin solver de pago
6. photo-egress — descarga + pHash de ~1.68M fotos contra CDNs anti-bot

**Compuertas adicionales (barrido del repo)**
7. vps-hosting — hosting VPS recurrente (Hetzner/Hostinger) + Terraform
8. amass-premium-keys — API keys premium de fuentes OSINT para el descubrimiento
9. mse-compute — coste de runtime del quorum captura-recaptura (R + DR-ML)
10. lineage-service — servicio OpenLineage/Marquez (contenedor operativo extra)
11. redis-infra — Redis para cache + rate-limit distribuido del serving
12. observability-saas — SigNoz Enterprise / Grafana Cloud (backend observabilidad)

---

# 1. egress-ip — IP de salida grado-ES, que pase el IP-gate y rote

## Problema
CARDEEP necesita una IP de salida espanola que (a) pase el **IP-gate** de
DataDome/PerimeterX en coches.net y milanuncios, y (b) pueda **rotar** desde una
IP quemada a volumen, todo a EUR0. La costura de egress ya existe en codigo:
`pipeline/engine/proxies.py` (env `CARDEEP_PROXIES`, `sticky_for` por drain) y se
aplica en `pipeline/engine/fetch.py:156-157` como `curl_cffi proxies={http,https}`.
La capa IP es **necesaria pero no suficiente**: no vence el reto JS/conductual —
eso es trabajo de la capa de fingerprint headful (engines Tier-1 nodriver/camoufox),
ortogonal y fuera de scope aqui.

## Ruta ganadora
**Egress movil/4G DIY:** Raspberry Pi (o cualquier host siempre-encendido) + dongle
USB LTE (Huawei E3372) + **3proxy**, exponiendo **una** URL `socks5://` en
`CARDEEP_PROXIES`, con conmutacion de modo de red del modem para rotar entre drains.

**Por que gana.** Es el unico candidato verificado que satisface **ambas**
restricciones a la vez: una IP movil/CGNAT genuinamente ES (la clase mas
superviviente — proxies.sx: 89-95% exito vs DataDome, 90-94% vs PerimeterX/HUMAN,
es decir ~5-11% de bloqueo) **y** rotacion real (`huawei-lte-api` conmuta el modo de
red en segundos para tomar una CGNAT fresca entre drains). La ruta pura Tier-0
residencial/host-IP (linea de casa del operador) solo da ~14-22% de bloqueo y **no
puede rotar** — una IP estatica unica se quema por rate a volumen, que es la
debilidad documentada del host-IP hoy. El nodo 4G arregla exactamente eso sin
suscripcion de proxy. Integracion = un cambio de env de una linea: 3proxy expone
`socks5://user:pass@PI_LAN_IP:port`; `sticky_for(f'engine:{id}')` (fetch.py:150)
ancla un drain de un engine a la IP actual; luego conmutas el modem antes del
siguiente drain. Las IPs moviles son las estructuralmente mas dificiles de
bloquear: el WAF arriesga dano colateral a miles de usuarios reales que comparten
la CGNAT.

**Base de gratuidad.** 3proxy es libre (open source). `huawei-lte-api` es libre.
Sin suscripcion de proxy, sin tarifa por-GB residencial, sin key. Coste marginal de
scraping = EUR0 sobre una SIM ES existente/ilimitada.

## Fallbacks
- **Tethering USB/Wi-Fi del telefono (movil ES del operador)** — fallback EUR0
  **inmediato**, cero hardware, disponible ahora. Egresa por una IP movil ES genuina
  (misma clase top superviviente, 4-11% bloqueo). Mecanica: es ruta **host-IP**, asi
  que deja `CARDEEP_PROXIES` **SIN SETEAR** — cero cambio de codigo (verificado:
  `proxies.py` `next()` devuelve `None` -> host IP). Rotacion manual (cicla modo
  avion/red entre drains). Mejor para runs MANUALES a rafagas; mas debil para drenado
  autonomo 24/7 porque ocupa el telefono y algunos operadores ES limitan throughput
  de tethering. **Usar esto para DESBLOQUEAR hoy la cosecha parada** mientras se
  construye el nodo Pi+dongle.
- **Conexion residencial de casa del operador (Tier-0, host IP puro)** — el default
  literal actual cuando `CARDEEP_PROXIES` esta vacio (`proxies.py` + comentario de
  `free_proxies.py`: 'headful browser on the host residential IP already wins
  coches.net'). Pasa el IP-gate a ~14-22% bloqueo. Baseline de estado estable para
  volumen bajo/medio. Su unica debilidad documentada es justo la restriccion que
  resolvemos: no rota y se quema por rate a volumen — por eso es fallback, no
  ganadora. Cero cambio de codigo; es el estado as-is.

## Pasos de integracion
1. **[Tethering, hoy, cero codigo]** Tetherea el host siempre-encendido al telefono
   ES del operador (USB preferible a Wi-Fi por estabilidad). Confirma que
   `CARDEEP_PROXIES` esta SIN SETEAR para que `ProxyPool` quede vacio -> `_lease_proxy()`
   (fetch.py:142-150) devuelva `None` -> egress por la IP movil del host. Corre un
   drain; verifica veredicto `ban_detector` OK sobre muestra de coches.net/milanuncios.
   Esto reanuda la cosecha parada desde 2026-06-15 sobre una clase de IP superviviente.
2. **[Nodo 4G, build]** En la Pi/caja siempre-encendida: conecta el Huawei E3372,
   inserta la SIM ES, levanta la interfaz LTE. Instala 3proxy y configura **UN** listener
   socks5 atado a la LAN, con auth (`socks -p1080` + linea de users + regla allow). Ancla
   el egress de 3proxy a la interfaz LTE para que nunca filtre la linea de casa.
3. **[Nodo 4G, hook de rotacion]** Instala `huawei-lte-api`. Escribe un script minusculo
   que conmute el modo de red del modem (LTE->3G->LTE) para forzar una CGNAT nueva
   (segundos; verificado por ScrapingFish — corrige el termino 'modo avion' del candidato,
   mismo efecto neto). Exponlo como comando local o endpoint HTTP que el orquestador
   (APScheduler+subprocess, per `project_cardeep.md`) llame entre drains.
4. **[Cablear en CARDEEP, una linea]** Setea
   `CARDEEP_PROXIES=socks5://user:pass@PI_LAN_IP:1080` en el entorno del proceso de
   cosecha. Cero codigo: `proxies.py` lo lee al importar; `fetch.py:106` `_lease_proxy()`
   -> `sticky_for(f'engine:{id(self)}')` ancla el drain entero a la IP movil actual
   (invariante de reuso de cookie, proxies.py:12-13,86-93); `fetch.py:156-157` lo aplica
   como `curl_cffi proxies={http,https}`. curl_cffi soporta `socks5://` nativamente, sin
   dependencia extra.
5. **[Cadencia de rotacion]** Un engine == una IP sticky para todo un drain (NO rotar
   mid-drain — rompe el binding cookie-de-clearance<->IP de proxies.py:1-13). Orquestacion:
   corre drain -> cierra engine -> llama al script de rotacion del modem -> el siguiente
   drain arrienda la IP fresca. Baja el tamano de drain si el bloqueo sube hacia la banda
   alta 5-11%.
6. **[Verificacion, reusar codigo existente]** Antes de confiar en el nuevo egress, corre
   `free_proxies.health_check(<socks5 URL>, tier1_url=<URL de listing coches.net>)`: hace
   fetch de un objetivo Tier-1 REAL via el proxy y setea `tier1_ok` via
   `ban_detector.classify` (free_proxies.py:121-157). `tier1_ok=True` es la senal
   go/no-go de que la IP movil realmente pasa el gate. Pasa cada rotacion del modem por
   este check.
7. **[Fenced el harvester de free-proxy de GitHub]** Deja `free_proxies.py` +
   `auto_proxy_refresh` cableado SOLO como ultimo recurso gateado-por-tier1 para
   endpoints **NO protegidos** (datacenter/hosts comprometidos se pre-marcan en el
   IP-gate; ~0 sobreviven coches.net/milanuncios per la tesis Techicy). Nunca lo apuntes
   a los dos objetivos protegidos. Confirma que `auto_proxy_refresh` queda `False` en los
   drains protegidos (fetch.py:87,101) para que no reemplace silenciosamente la IP movil
   por proxies datacenter muertos.
8. **[Recordatorio: solo capa IP]** Nada de lo anterior vence el reto JS/conductual.
   Manten la capa de fingerprint headful (engines Tier-1 nodriver/camoufox, headful por
   defecto en fetch.py:125-127) como capa companera. La IP movil pasa el IP-GATE; el
   browser headful pasa el RETO. Son ortogonales — entrega ambas.

## Riesgo residual
Bloqueo reducido, no nulo: la banda superviviente 5-11% aun produce fetches fallidos
a volumen; ajusta tamano de drain y acepta reintentos. La IP movil sola **NO** vence
el reto de fingerprint JS/conductual — si la capa Tier-1 headful (nodriver/camoufox)
no se ejercita realmente en cosecha (hoy esta construida pero **nunca usada** en runs
reales, bug #5 de `project_cardeep.md`), el arreglo IP rendira de menos; las dos capas
deben entregarse juntas. Un solo dongle LTE = espacio CGNAT finito y pequeno de un
operador; rotacion agresiva puede reciclar una IP recien quemada — mitiga espaciando
rotaciones y gateando cada una por `health_check(tier1_url=...)`. Latencia de rotacion:
unos segundos de re-attach del modem por drain reducen throughput; dimensiona drains en
consecuencia. `nodriver` es **AGPL-3.0** y es el default Tier-1 (bug #5) — nota de
licencia/operacion, no de coste de egress, pero senalala antes de distribuir.
ToS del operador y legalidad del scraping siguen siendo responsabilidad del operador.
Nota el bug vivo `coches_net_facet.py:295` (7 args vs 8) que crashea el cosechador
canonico de coches.net hoy — el arreglo de egress se desperdicia en coches.net hasta
arreglar ese call-site; verificalo antes de declarar la cosecha restaurada.

## Huecos honestos
VERIFIQUE en codigo toda la costura de egress (`proxies.py`
CARDEEP_PROXIES/sticky_for/next-None-host-IP, `fetch.py:106/142-150/156-157`,
`free_proxies.py` tier1_url gate via ban_detector). NO corri un fetch en vivo via IP
movil ES real contra coches.net/milanuncios en esta sesion — las cifras 89-95% / 4-11%
vienen de las fuentes proxies.sx y ScrapingFish de los candidatos verificados, no de un
run CARDEEP que yo ejecutara. Que curl_cffi acepta `socks5://` es consistente con que
el codigo pasa URLs de proxy arbitrarias directo a `cffi_requests proxies={}`, pero no
ejercite una URL socks5 end-to-end. El mecanismo de rotacion (toggle de modo de red) y
los detalles Huawei E3372 + `huawei-lte-api` vienen de la guia citada, no de hardware que
yo probara. **Conclusion de coste EUR0 asume SIM ES existente/ilimitada y host
siempre-encendido ya en propiedad**; si no existen, el hardware de un-solo-pago
(Pi ~EUR35 + E3372 ~EUR30) es el unico coste, y el workaround estricto-EUR0 es el
fallback de tethering (cero hardware, cero codigo).

---

# 2. antibot-engine — motor anti-bot FOSS sin AGPL para el cascade Tier-0->Tier-1

## Problema
CARDEEP necesita un motor anti-bot libre/OSS, **sin AGPL**, para alimentar su
cascade en vivo Tier-0 (`curl_cffi`) -> Tier-1 (browser) contra DataDome,
PerimeterX/HUMAN y Cloudflare en objetivos ES de venta de coches, de modo que la
cosecha (PARADA desde 2026-06-15) reanude sin el riesgo del hot-path nodriver/AGPL-3.0.
VERIFICADO en codigo: el cascade es real en `pipeline/engine/fetch.py` y
`pipeline/engine/tier1/browser.py`; Tier-0 ya usa `curl_cffi` (MIT); la cadena Tier-1
por defecto (fetch.py:119) resuelve solo a `('camoufox',)` — el unico engine permisivo
realmente cableado es la Camoufox BETA con gap de mantenimiento y degradacion de
rendimiento que el brief marco. `solve_challenge` (browser.py:62) aun pone por defecto
`engine='nodriver'` (AGPL-3.0) como footgun latente. BotBrowser y Patchright **no**
estan cableados. El gap real es calidad/diversidad de engine en el hot path permisivo,
no la arquitectura.

## Ruta ganadora
**Patchright (Apache-2.0)** como nuevo engine Tier-1 primario, cableado junto a la
Camoufox existente en `pipeline/engine/tier1/browser.py`.

**Por que gana.** Es el mejor default Tier-1 permisivo y hot-path-safe para CARDEEP hoy.
Apache-2.0 es plenamente sin-AGPL y satisface el mismo invariante no-AGPL que ya impone
`tests/test_engine_license_default.py` (pasaria `test_default_tier1_chain_runs_no_agpl_engine`
sin cambios). Es un Playwright undetected drop-in, asi que encaja en la costura exacta
`solve_challenge(url, engine=..., proxy=..., headless=...) -> BrowserResult(html, cookies,
user_agent)` ya usada por `_solve_camoufox`; integracion = una corutina `_solve_patchright`
nueva + una rama de dispatch — cero cambio de arquitectura. Lleva el unico dato de eficacia
de TERCERO de los candidatos permisivos (ianlpaterson 2026: 25/3/3 en 31 objetivos Cloudflare,
empatado con Camoufox, y lista DataDome como pasando), y a diferencia de Camoufox esta
mantenido activamente (release v1.61.0 + ultimo push 2026-06-17) sin gap admitido ni
regresion de rendimiento. Cura la debilidad viva: la cadena por defecto corre SOLO la
Camoufox beta degradada. Patchright + Camoufox da diversidad Chromium+Firefox en un hot
path limpio Apache/MPL retirando permanentemente el footgun nodriver-AGPL de browser.py:62.

**Base de gratuidad.** VERIFICADO via gh API: license=Apache-2.0, 3542 stars, release
v1.61.0/push 2026-06-17. Libreria y stealth gratis para siempre; lo unico no-libre son
enlaces de proxy sponsoreados de terceros (Swiftproxy/RapidProxy/NodeMaven) totalmente
separables y nunca importados. `pip install patchright && patchright install chromium` = EUR0.

## Fallbacks
- **BotBrowser** (botswin/BotBrowser, wrapper MIT sobre binario propietario distribuido
  gratis) como render Tier-1 de ULTIMO recurso para los objetivos ES DataDome+PerimeterX
  mas duros que Patchright y Camoufox fallan ambos. Hace la afirmacion mas fuerte contra el
  trio exacto DataDome+PerimeterX+Cloudflare con stealth compilado (no JS-inyectado).
  Cablearlo como ultimo eslabon de la cadena (`patchright -> camoufox -> botbrowser`) para
  que los engines coste-cero se prueben siempre primero. CAVEATS que lo dejan en fallback:
  el core de defeat es un **binario propietario cerrado** (MIT cubre solo el wrapper, no es
  OSS puro), y NO esta en el benchmark independiente de ianlpaterson, asi que la eficacia
  por-objetivo-ES es vendor-claimed — fija el release hash 149.0.7827.102 (2026-06-19) y
  valida por objetivo antes de confiar. El Standard Build gratis corre el cascade a EUR0.
- **Camoufox** (daijro/camoufox, MPL-2.0) — MANTEN el `_solve_camoufox` ya cableado como
  fallback de diversidad de engine (base Firefox vs el pack Chromium), degradado de
  sole-primary a secundario. Gratis, MPL-2.0 hot-path-safe, ya integrado y proxy/humanize-aware
  en browser.py:174. El caveat (gap de mantenimiento de un ano, degradacion auto-admitida,
  beta v150.0.2-beta.25) es justo por que NO debe seguir como unico default pero sirve como
  secundario fijado para diversidad de fingerprint. Cero codigo nuevo — se queda; Patchright
  simplemente se adelanta en la cadena.

## Pasos de integracion
1. En `pipeline/engine/tier1/browser.py`, anade `async def _solve_patchright(url, *, proxy,
   timeout, wait_after_load, headless)` espejo de `_solve_camoufox` (browser.py:174-194):
   import lazy `from patchright.async_api import async_playwright`, lanza persistent context
   con `channel='chrome'` + la postura no_viewport/headful (DataDome marca headless al instante
   — reusa el `_tier1_headless=False` por defecto), `proxy={'server': proxy}` cuando exista,
   `goto wait_until='domcontentloaded'`, sleep `wait_after_load`, y devuelve
   `BrowserResult(html=page.content, cookies={...}, user_agent=navigator.userAgent,
   final_url=page.url, engine='patchright', raw_cookies=list(...))`. El contrato BrowserResult
   no cambia, asi que el invariante de reuso de cookie (mismo UA+JA3+IP) en
   `fetch.py:_serve_with_cookies` sigue intacto.
2. En `browser.py`, extiende el set de validacion en la linea 74 a
   `('nodriver','camoufox','patchright','botbrowser')` y anade las ramas de dispatch en
   `_solve_async` (browser.py:117-124). Cambia el default de `solve_challenge` en la linea 62
   de `engine='nodriver'` a `engine='patchright'` para matar el footgun AGPL a nivel de funcion.
   Actualiza el docstring del modulo (browser.py:12-26) para nombrar Patchright como primario y
   nodriver como opt-in-only.
3. En `pipeline/engine/fetch.py`, cambia `_TIER1_ENGINE` (linea 57) de `'camoufox'` a
   `'patchright'` y la cadena por defecto (linea 119) de `(_TIER1_ENGINE, 'camoufox')` a
   `('patchright','camoufox')` — dando diversidad Chromium+Firefox en ruta Apache/MPL pura.
   Mantiene firmas publicas de `FetchEngine` y el opt-in `allow_tier1_escalation`
   (fetch.py:82-119); los 37 connectors no se afectan.
4. Anade `_solve_botbrowser` como cuarto engine y agrega `'botbrowser'` a la cola de la cadena
   (`'patchright','camoufox','botbrowser'`) para que el binario propietario solo se lance tras
   agotar ambos engines permisivos gratis — el fall-through multi-engine 'nunca pausar en un
   bloqueo, rodearlo' ya implementado en `fetch.py:_fetch_tier1` (lineas 313-346). BotBrowser se
   lanza como Chromium parcheado via CDP/Playwright; carga un perfil fijado y condúcelo por la
   misma API Playwright que la rama patchright.
5. Extiende `tests/test_engine_license_default.py`: manten el guard `_AGPL_ENGINES` (sigue
   pasando con patchright/camoufox) y anade asserts de que `chain[0]=='patchright'` y que
   `'patchright'` resuelve a un engine Apache-2.0. Extiende `tests/test_fetch_cascade.py` con un
   fake `solve_challenge` para `engine='patchright'` que pruebe que la escalacion Tier-0->Tier-1
   y el reuso de cookie lo selecciona primero. Corre `pytest -m unit` (sin red/browser).
6. Valida por objetivo ES antes de declarar done (doctrina VAM zero-trust): usa
   `scripts/pilot_tier1.py` contra los objetivos DataDome/PerimeterX en vivo (coches.net es
   DataDome-bound per comentario browser.py:336) para confirmar que patchright headful resuelve y
   que el reuso de cookie curl_cffi aguanta; escala un objetivo a BotBrowser solo si patchright+
   camoufox fallan ambos. Esto tambien desbloquea arreglar el crash de aridad
   `coches_net_facet.py:295`.
7. Requirements: `pip install patchright && patchright install chromium` (Apache-2.0, EUR0).
   BotBrowser: descarga el Standard Build gratis fijado a 149.0.7827.102 y referencia su path via
   config, NO dependencia pip, para que importar `pipeline.engine` nunca lo toque — espejo de como
   nodriver/camoufox se importan lazy dentro del solver (tier1/__init__.py:1-11).

## Riesgo residual
El UNICO coste residual son **proxies residenciales ES sticky**, ya nombrado y aislado en
codigo: `browser.py:56-59` `PENDING_CREDENTIAL_PROXY` declara explicitamente que Tier-1 contra
WAFs IP-bound (DataDome/Akamai vivos) necesita proxy residencial ES sticky; sin uno, el solve
corre sobre IP host/datacenter. **Ningun** engine — Patchright, Camoufox, BotBrowser — cambia
esto: la cookie de clearance (cf_clearance/datadome/_abck) esta atada a la IP que resuelve, y una
IP datacenter es la senal de bloqueo dominante contra DataDome/PerimeterX conductual. La eleccion
de engine es necesaria-pero-no-suficiente; la capa IP es el techo real. **WORKAROUND EUR0**:
CARDEEP ya trae `pipeline/engine/free_proxies.py` con auto_refresh y `pipeline/engine/proxies.py`
sticky leasing (fetch.py:99-106) — cablea `auto_proxy_refresh=True` para auto-arrendar proxies
GRATIS en vivo antes de resolver. Son de baja calidad/efimeros pero cuestan EUR0 y son el cribado
correcto antes de cualquier IP de pago. Segunda palanca EUR0: prefiere Tier-0 sobre APIs/sitemaps
abiertos donde existan (CARDEEP ya cosecha AS24/autocasion/coches.com via Tier-0 abierto). Solo si
un objetivo ES de alto valor sigue bloqueado desde datacenter+free IPs se vuelve inevitable un
proxy residencial de pago — gasto diferido, por-objetivo, gateado por owner, NO precondicion para
entregar este trabajo de engine.

## Huecos honestos
1) **No existe benchmark de TERCERO para DataDome ni PerimeterX especificamente** — el dato
ianlpaterson 2026 que citan brief y browser.py:16 testeo SOLO Cloudflare (31 objetivos). El '25/3/3'
de Patchright y las afirmaciones DataDome+PX de BotBrowser son Cloudflare-proven + vendor-claimed; el
paso 6 (validacion por-objetivo-ES via `scripts/pilot_tier1.py`) es obligatorio, no opcional, y NO lo
corri — con la cosecha PARADA no hay prueba en vivo actual. 2) El core stealth de BotBrowser es
**propietario cerrado**; solo el wrapper MIT es OSS, no satisface 'OSS puro' estricto aunque sea
distribuible gratis y sin-AGPL. 3) NO instale ni ejecute Patchright/BotBrowser en este entorno; los
pasos derivan de lectura VERIFICADA de fetch.py/browser.py (contrato BrowserResult, costura
solve_challenge, test no-AGPL) + facts gh-API del brief — las formas de codigo `_solve_patchright`/
`_solve_botbrowser` son ASUMIDAS-correctas contra la API Playwright-compatible y deben smoke-testearse.
4) La degradacion de rendimiento auto-admitida de Camoufox significa que su valor aqui es diversidad,
no fiabilidad; si resulta neto-negativo en el paso 6 debe caer, dejando `patchright -> botbrowser`.
5) Trate las verificaciones gh-API del brief (stars, licencias, fechas) como dadas en vez de
re-consultarlas — consistentes con lo que los comentarios del propio codigo CARDEEP afirman (curl_cffi
MIT, camoufox MPL-2.0, nodriver AGPL-3.0).

---

# 3. llm-edge — LLM EUR0 para extraccion de recetas P04 + tiebreak de identidad P06

## Problema
Elegir la ruta LLM genuinamente EUR0 (junio 2026) para la extraccion mint-once
HTML-a-schema de recetas P04 (+ self-heal de selectores) y el tiebreak de identidad
opcional de bajo volumen P06, con structured-output (JSON-schema/grammar) suficientemente
fuerte para HTML sucio de dealers. Contexto verificado en repo: `recipe_schema.py:67` ya
declara engine `'llm_local'` en el vocabulario cerrado de parsing; `recipe_extract_web.py:9`
nombra `'local-LLM'` como el siguiente peldano de la escalera §4 para sitios JS-rendered que
dan JSON-LD vacio; `gestionador/detect.py:906-910` ya corre un clasificador LLM LOCAL en su
golden-set nocturno. La doctrina es 'EUR0 hasta A->Z' y main=verdad-unica. P04 paga el LLM una
vez al mint, congela la receta YAML (`countries/ES/recipes/<cdp_code>.yaml`) y la replay
deterministicamente off-LLM (50k/dia = EUR0), asi que limites de rate ajustados en mint son
aceptables.

## Ruta ganadora
**llama.cpp (`llama-server`)** con decodificacion restringida GBNF / JSON-Schema-to-grammar.

**Por que gana.** Es el unico candidato que es a la vez (a) genuinamente EUR0 para siempre con
cero riesgo de proveedor, (b) garantizado-por-schema a nivel de token (GBNF + JSON-Schema-to-grammar
restringe la salida en decode, no por prompt, asi que JSON invalido es literalmente imposible), y (c)
ya la intencion de diseno declarada del proyecto. `recipe_schema.py:67` hard-codea `'llm_local'` como
valor valido y `recipe_extract_web.py:9` nombra explicitamente `'local-LLM'` como el siguiente peldano
§4; `gestionador/detect.py` ya corre un clasificador LOCAL nocturno, probando que la caja ya hace
inferencia local. P04 mint-once-luego-congela, asi que NO hay coste diario LLM NI rate-limit que pueda
morder el replay de produccion. Un free tier hosteado no puede ganar a 'sin cuenta, sin rate-limit, sin
deprecacion a mitad de mint, sin exposicion EU-residency/data-use, offline, corre en la caja de cosecha
existente'. Para P06 mantiene los datos de identidad del dealer en-caja (privacidad + EUR0). El
transporte curl_cffi/browser ya alimenta el harness; el LLM solo consume el HTML fetcheado, asi que
encaja detras del protocolo Extractor (`recipe_harness.py:65-75`) sin tocar transporte. Verificado MIT,
`/chat/completions` OpenAI-compatible con `response_format json_schema`.

**Base de gratuidad.** Self-hosted en hardware que el proyecto ya posee (la caja de cosecha/orquestacion
que corre APScheduler+subprocess y el clasificador local nocturno). Sin cuenta, sin token metering, sin
rate-limit, sin ToS de proveedor, offline. Cuantizacion GGUF (p.ej. un 7B-8B a Q4_K_M) mantiene la RAM
modesta y la inferencia CPU-only funciona; el mint es one-shot por dealer asi que la latencia es
irrelevante bajo el modelo de receta-congelada. Coste = solo electricidad/hardware existente = EUR0
incremental.

## Fallbacks
- **Mistral La Plateforme (free Experiment tier)** — el fallback hosteado mas fuerte para este proyecto
  basado en Espana: **EU-resident** (esquiva por completo el bloqueo EEA/UK/Suiza del free tier de Gemini),
  sin tarjeta (solo verificacion de telefono), ~1B tokens/mes, structured outputs via tu propio json_schema.
  Usalo como acelerador de mint masivo / segunda opinion cuando la caja local este ocupada o para paginas
  grandes que el modelo local sufra. Su enforcement de schema es supplied-schema, no el token-level mas
  fuerte de los strict modes, asi que **siempre re-valida el JSON contra `recipe_schema`** antes de
  persistir. Residual: sin SLA de produccion (irrelevante — la receta se congela, produccion es off-LLM).
- **Groq (free tier)** `gpt-oss-20b` / `gpt-oss-120b` con `strict:true` — adherencia de schema 100% a nivel
  de token (igual garantia que llama.cpp grammar) SOLO en los modelos gpt-oss; el resto es best-effort.
  Usalo como model-shootout rapido de diseno de mint y cross-check de calidad para el modelo local en
  paginas duras. Restricciones: strict mode prohibe streaming y tool use, exige todo campo `required` +
  `additionalProperties:false`; cuota ORG-level ~1,000 RPD en gpt-oss, ~30 RPM. Vale porque el mint es
  one-shot; nunca lo pongas en el replay diario. Trata el HTML del dealer como saliendo de la caja (solo
  paginas publicas de listing, no datos de identidad P06).

## Pasos de integracion
1. Levanta `llama-server` en la caja de cosecha/orquestacion existente (la misma que corre el clasificador
   local nocturno en `pipeline/gestionador/detect.py` y la flota APScheduler+subprocess). Baja un GGUF
   instruct (clase 7B-8B, Q4_K_M), lanza: `llama-server -m <model>.gguf --port 8081 --host 127.0.0.1`. Ata
   a localhost — sin exposicion externa, sin superficie de auth.
2. Escribe el JSON schema de un vehiculo extraido que refleje el shape de dict ya consumido por
   `recipe_harness Sample.parsed` (los mismos campos que `AS24_RECIPE.field_map` produce en
   `pipeline/recipe.py`: deep_link, vin_ref, make, model, year, km, price, fuel, transmission, photo_url,
   dealer, location). Este schema es la fuente unica de verdad para grammar y validacion post-hoc.
3. Anade `pipeline/recipe_extract_llm.py` implementando el protocolo Extractor de `pipeline/recipe_harness.py`
   (lineas 65-75): clase con `source='web_llm'`, un `recipe_template(dealer_ref)` que devuelve una Recipe
   DRAFT con `Parsing.engine = 'llm_local'` (valor ya legal en recipe_schema.py:67), y un `sample(dealer_ref, k)`
   que (a) reusa `pipeline.engine.fetch.fetch_text` para transporte (escalacion WAF al browser tier sin cambios),
   (b) recorta/limpia el HTML a la region del stock-list (reusa `find_stock_url` + `_STOCK_HINT` de
   recipe_extract_web.py), (c) POSTea al `/chat/completions` local con
   `response_format={type:'json_schema', json_schema:<schema>}`, (d) devuelve `Sample(declared, fetched, parsed,
   full_dealer)`.
4. Haz `recipe_extract_llm` el FALLBACK explicito: solo invocalo cuando `recipe_extract_web.py` devuelva una
   sample JSON-LD vacia (el caso 'empty sample' FALLADO decidido en `recipe_harness.decide_status`). Cablealo como
   siguiente peldano de la escalera §4 (structured/JSON-LD -> css -> llm_local) para que la ruta determinista barata
   siempre gane y el LLM se pague a lo sumo una vez por dealer JS-rendered.
5. Pasalo por el ciclo de harness SIN CAMBIOS: EXTRACT SAMPLE (k=3-5) -> PERSIST RECIPE -> VERIFY (VAM via
   `pipeline.verify.record_count_verdict`) -> DELETE SAMPLE. El harness ya impone cero-parse-loss + VAM-no-REFUTED
   antes de STATUS_VERIFIED, asi que una extraccion alucinada/corta del LLM se rechaza como FAILED con razon — sin
   codigo de confianza nuevo. En VERIFIED, `write_recipe` persiste `countries/ES/recipes/<cdp_code>.yaml` y la receta
   CONGELA; el replay diario es la ruta determinista off-LLM = EUR0.
6. Tiebreak P06: expon el mismo `llama-server` local a `pipeline/identity/resolve_entities.py` como corroborador
   de ULTIMO recurso SOLO TRAS correr los guards mecanicos (los guards anti-over-merge §8: chain guard, guard de
   nombre-de-ciudad INE, quorum centralita/Jaccard). Aliméntalo solo con las dos tuplas candidatas
   trade-name/address/phone con un json_schema booleano+confianza estricto; trátalo como una senal ortogonal mas,
   NUNCA como override de un BLOCK mecanico (chain guard y city-name guard quedan absolutos per el docstring). Manténlo
   en-caja para que los datos de identidad nunca salgan del host.
7. Anade un test de conformidad de schema offline (sin red) espejo del golden-set nocturno de `gestionador/detect.py`:
   alimenta fixtures HTML de dealer sucio por `recipe_extract_llm` contra el JSON schema congelado, asserta salida
   estructurada valida + cero parse loss. Guarda contra un swap de modelo/quant que regresione silenciosamente.
8. (Aceleracion opcional, sin coste recurrente) Si el backlog de mint masivo es grande, anade un provider-swap detras
   del mismo Extractor: apunta el cliente OpenAI-compatible `base_url` a Mistral La Plateforme Experiment tier (EU-resident,
   EUR0, ~1B tok/mes) para paginas publicas no-sensibles, manteniendo llama.cpp como default y para TODO trabajo P06.
   Siempre re-valida la salida Mistral contra `recipe_schema` antes de persistir.

## Riesgo residual
(1) La grammar de llama.cpp garantiza JSON VALIDO en forma, no CORRECTO en valores — un modelo local pequeno aun puede
emitir make/price/km plausible-pero-erroneo para HTML genuinamente adversarial. Mitigacion ya estructural: la VAM del
harness (quorum fetched vs parsed) rechaza parse-loss y la receta se samplea (k=3-5) y verdict-gatea antes de congelar;
anade el spot-check de valor de `price_sanity.py` sobre la sample minteada. (2) Techo de calidad del modelo local en los
sitios JS-rendered mas sucios — un 7B puede rendir menos que un frontier hosteado en layouts raros; mitiga con el cross-check
strict de Groq gpt-oss o Mistral en los dealers fallidos especificos (sigue EUR0). (3) Los fallbacks hosteados envian HTML de
listing publico fuera-de-caja — aceptable para paginas de marketplace, NO para tuplas de identidad P06, que quedan locales.
(4) Operacional: el server local es un proceso mas en la caja de cosecha ya cargada (cuya cosecha esta PARADA desde 15-jun y
cuyo cosechador canonico de coches.net crashea por el bug arg-shift de `recipe_extract_web`/`coches_net_facet`) — agenda runs
de mint off-peak; nada aqui pone el LLM en la ruta de replay diario.

## Huecos honestos
Lo que NO pude verificar de primera mano: (a) la CPU/RAM/GPU exacta de la caja de cosecha CARDEEP, asi que no puedo prometer
un tamano/latencia de modelo especifico — la recomendacion usa deliberadamente quants GGUF CPU-viables y un mint one-shot
latencia-insensible, pero el throughput real debe medirse en-caja. (b) Las cifras de free-tier (Mistral ~1B tok/mes, Groq
~1,000 RPD org-level, Cerebras cap 8K contexto, OpenRouter 50->1,000 RPD) vienen del dossier verificado, no re-fetcheadas en
vivo esta sesion; los free tiers cambian sin aviso, re-chequea la pagina del proveedor antes de cualquier mint hosteado.
(c) El free tier de Gemini esta correctamente EXCLUIDO: es EUR0 en tokens pero el ToS de Google fuerza Paid Services para apps
que sirven usuarios EEA/UK/Suiza, asi que un CARDEEP basado en Espana no puede usarlo legitimamente — no existe workaround EUR0
para Gemini especificamente (el workaround es usar las rutas local o EU-resident de arriba). (d) La ruta pura-EUR0 de OpenRouter
(50 RPD) y Cloudflare Workers AI (10k neurons/dia, JSON solo best-effort) son reales pero estrictamente mas debiles y no
seleccionadas. (e) NO corri el nuevo `LlmLocalExtractor` — es un diseno fundamentado en el protocolo Extractor verificado y el
valor `'llm_local'` existente, no codigo ejecutado todavia; trata los pasos 1-7 como el build, no un estado-hecho. **No existe
coste EUR residual en la ruta recomendada**: el unico 'coste' es electricidad/hardware existente (EUR0 incremental); todo
fallback hosteado es tambien EUR0 (sin tarjeta).

---

# 4. geo-places — enumeracion de POIs sin Google Places para el vector GEO de P01

## Problema
Un motor de enumeracion de POIs EUR0 y sin-Google para el vector de descubrimiento GEO de P01
(V2 'geo-grid', `plans/P01.md` §3 componente C y paso P01-S5), que suministra listas de dealers
de presencia fisica que alimentan `pipeline/exhaustiveness/capture.py` -> el sello de cobertura MSE
(`v_exhaustiveness_seal`). La necesidad: una alternativa/backup gratis a Google Places de pago que
ademas anada una lista de captura genuinamente ORTOGONAL (contribuyentes distintos) para subir el
solapamiento `m` y apretar `N̂`, hoy catastroficamente bajo en los estratos dominantes
(Madrid×compraventa coverage_lower=0.021).

## Ruta ganadora
**Motor DuckDB-sobre-GeoParquet (ya en repo)** corriendo Overture Maps + OSM/Overpass +
Foursquare OS Places como tres listas ortogonales de presencia fisica, con FSQ anadida como nueva
tercera lista GEO (P01-S5).

**Por que gana.** El motor YA esta construido y probado en repo: `pipeline/sources/overture.py`
(248 lineas) corre DuckDB httpfs+spatial sobre un bucket GeoParquet publico con bbox pushdown, aísla
limpio offline, mintea `DiscoveredEntity`, y ya esta registrado en `discover.py:ADAPTERS`, `lists.py`
(bucket GEO) y `discover_schedule.py` (overture, 720h). OSM `shop=car` esta vivo tambien
(`pipeline/sources/osm.py` via Overpass, ~9.956 entidades en DB). La UNICA pieza faltante para
completar el motor GEO gratis es la tercera lista ortogonal, y P01-S5 ya la especifica:
`pipeline/sources/fsq_places.py` 'calcado de overture.py'. FSQ es el anadido de mayor valor porque el
cuello de botella nombrado en el plan y en `b6_chapman_final.py` es **muy pocas listas ortogonales**,
no compute: una tercera lista de contribuyente-independiente sube `m` por estrato y encoge el IC del
que depende el sello. Facts verificados que lo hacen seguro: FSQ es Apache-2.0, gratis, categoria
automotive 'Car Dealership' id `4eb1c1623b7b52c0e1adc2ec` confirmada; Overture es dual-license gratis
(Apache-2.0/CDLA-Permissive/CC0) con taxonomia automotive>automotive_dealer>car_dealer; OSM `shop=car`
es ODbL, ~163k mundial / ~3.5k Espana. Compute = DuckDB MIT. Coste neto: EUR0.

**Base de gratuidad.** Los tres datasets gratis bajo licencias permisivas (FSQ Apache-2.0, Overture
Apache-2.0/CDLA/CC0, OSM ODbL) y el motor de compute es DuckDB MIT. Cero API key, cero cuenta para
Overture/OSM. FSQ solo requiere aceptacion una-vez de los terminos HuggingFace (gratis, sin tarjeta).
El egress se evita por descarga una-vez; el bbox pushdown trae solo el subset de Espana.

## Fallbacks
- **OpenStreetMap `shop=car` via extract bulk Geofabrik (Espana PBF)** en vez de Overpass en vivo —
  ya cableado como `pipeline/sources/osm.py` pero usando Overpass en vivo hoy. Para un barrido nacional
  ilimitado sin limites de fair-use, cambia el loader a una descarga una-vez de Espana `.osm.pbf` parseada
  localmente (osmium/pyrosm) — EUR0, sin rate-limit, sin key. Usa esto cuando el barrido de saturacion del
  quadtree necesite martillar GEO sin tropezar con el fair-use de Overpass. Atribucion ODbL requerida.
- **Geoapify Places API free tier** (3,000 creditos/dia, 5 req/s, SIN tarjeta) como helper de
  geocoding/enriquecimiento para celdas donde las listas parquet sean delgadas — pero NO como lista MSE
  ortogonal. CAVEAT HONESTO: Geoapify es OSM-derived, NO es independiente de la lista OSM (doble-conteo,
  infla cobertura); y su set de categorias en vivo solo tiene el bucket grueso `commercial.vehicle`, sin
  categoria dealer dedicada. Mantenlo FUERA de `lists.py ORTHOGONAL_LISTS`; usalo solo para backfill
  oportunista de telefono/web dentro del cap diario EUR0, con atribucion 'Powered by Geoapify' obligatoria.
- **Google Places API (New)** gateado detras del quadtree DuckDB como backup de pago de cola-larga SOLO
  para celdas infra-saturadas en Overture+FSQ+OSM. La maquinaria de quadtree adaptativo (algoritmo
  comarquet/maps-scraper, MIT) es el motor correcto; overture.py ya documenta el quadtree reservado para
  esta capa Google capada. El cap free por-SKU es ~5,000 llamadas Pro/mes (Text/Nearby Search); gatear a
  solo el punado de celdas urbanas genuinamente saturadas mantiene la operacion normal dentro del cap free
  = efectivamente EUR0, mas un credito GCP one-time de $300. Esta es la ruta decision-owner-final; entrega
  primero todas las rutas gratis.

## Pasos de integracion
1. Construye el adapter FSQ (P01-S5) como `pipeline/sources/fsq_places.py`, clonado de
   `pipeline/sources/overture.py`: mismo helper de conexion DuckDB (INSTALL spatial/httpfs), mismo `_BBOX`
   de Espana (-18.3..4.6 / 27.5..44.0 incl. Canarias/Ceuta/Melilla), bbox pushdown, `CARDEEP_FSQ_LIMIT`
   para sampling recipe-first, auto-aislamiento limpio (declared=None, fetch=[]) offline. Filtra a categorias
   automotive FSQ (Car Dealership `4eb1c1623b7b52c0e1adc2ec` y hermanas) y mintea
   `DiscoveredEntity(source_key='fsq_places', extra={'vector':2})`.
2. **CORRECCION CRITICA de acceso** — NO copies la ruta S3-publica de overture.py para FSQ. El propio
   `plans/00-MASTER-BLUEPRINT.md` linea 117 (riesgo H2) registra que FSQ migro off S3-publico a token/Iceberg
   en oct-2025; la evidencia VERIFICADA confirma que los bytes vivos, gratis y sin-gate viven en HuggingFace
   (`datasets/foursquare/fsq-os-places`, release `dt=2026-06-11`, Apache-2.0, gateado solo por aceptacion
   gratis de terminos). Apunta `read_parquet` de DuckDB al path de release HuggingFace (`hf://` o las URLs
   parquet https resueltas), acepta terminos una vez, y fija el release via `CARDEEP_FSQ_RELEASE`. Aviso de
   footprint: el release completo es ~216 GB Parquet (NO ~11 GB como afirman algunas notas) — confia en
   predicate pushdown bbox/categoria para leer solo el slice automotive de Espana; nunca bajes el planeta.
3. Registra el adapter exactamente donde overture/osm: anade `FsqPlacesAdapter` a `ADAPTERS` en
   `pipeline/discover.py`, y anade `'fsq_places':'GEO'` a `_EXACT` en `pipeline/exhaustiveness/lists.py`
   para que el VAM count-gate (discover.py:155-163) y la matriz de captura (capture.py) lo recojan automaticamente.
4. Resuelve la decision de ortogonalidad que el plan marca como riesgo abierto (P01.md §7 y §2). `lists.py`
   hoy colapsa osm+overture+geo_sweep en UNA clase GEO, lo que DESPERDICIARIA la independencia de FSQ — y la nota
   VERIFICADA avisa que filas de origen-FSQ aparecen tambien dentro de Overture (Foursquare alimenta Overture),
   parcialmente correlacionadas. Tras la primera ola FSQ, mide el solapamiento pairwise Overture<->FSQ<->OSM por
   estrato en capture.py: si FSQ anade capturas materialmente independientes, escindela en su propia lista MSE
   (p.ej. GEO_FSQ) en ORTHOGONAL_LISTS; si el solapamiento es excesivo, mantenla en GEO pero usa la columna de
   source-attribution de Overture para restar filas origen-FSQ y no doble-contar el mismo dealer. Decision
   data-driven diferida a P02.
5. Cablea la orquestacion continua (P01-S6): anade un `fsq_places` DiscoveryJob a `DISCOVERY_REGISTRY` en
   `pipeline/discover_schedule.py` con `cadence_hours=720` (mensual, igual que la cadencia de release FSQ y las 720h
   de Overture) y `orthogonal=True`; corre `--seed` para crear su fila source_health y `--dry-run` para confirmar
   que aparece DUE.
6. Recertifica (P01-S7): tras la ola, repuebla la matriz de captura con
   `python -m pipeline.exhaustiveness.capture --build run-p01-fsq`, luego lee `v_exhaustiveness_seal` — confirma que
   el `k_lists` nacional sube sobre 7 y `coverage_lower` sube sobre el baseline 0.553, atendiendo especialmente
   Madrid×compraventa (0.021). Documenta el delta con el `build_run_id` en
   `docs/architecture/07-COVERAGE-STRATEGY.md`.
7. Manten Google Places estrictamente gateado (control de coste, no lista gratis): dejalo FUERA de discover.py y
   lists.py. Implementa el quadtree adaptativo (algoritmo comarquet/maps-scraper MIT) como barrido gateado separado
   que corre SOLO en celdas que el motor DuckDB reporte infra-saturadas en Overture+FSQ+OSM. Cachea cada respuesta
   Places para respetar el ToS de Maps y nunca re-pagar; con gating, las llamadas residuales quedan dentro del cap
   free ~5,000/mes Pro. Decision owner-final, tras probar todas las rutas gratis.

## Riesgo residual
1) **NO-ORTOGONALIDAD PARCIAL**: filas FSQ estan embebidas dentro de Overture (Foursquare alimenta Overture), asi
que tratar FSQ y Overture como listas MSE plenamente independientes SOBRE-estimaria cobertura (inflar el sello — el
maquillaje exacto que la doctrina prohibe). Mitigacion obligatoria y data-driven (paso 4): medir solapamiento y o
escindir FSQ solo si es genuinamente independiente, o restar filas origen-FSQ de Overture via source attribution.
2) **DRIFT DE ACCESO FSQ**: la migracion S3-publico->HuggingFace/Iceberg (H2) hace del path de acceso la parte fragil;
fija el release tag y manten auto-aislamiento limpio para que un bucket movido degrade a 'GEO cae a Overture+OSM', nunca
a crash. 3) **SUELO DE SESGO GEO**: los tres son catalogos de presencia fisica con sesgo de mapper urbano; sub-capturan
el 'garaje de montana' rural pase lo que pase — esa cola larga la poseen los vectores NO-geo ortogonales (DORK, REG/BORME,
web-propia CT/CCWEB), asi que GEO no debe sobre-confiarse como prueba de cobertura sola. 4) **PRECISION DE DEALER**: las
categorias automotive Overture/FSQ incluyen talleres y vendedores de repuestos, no solo puntos de venta; el mapeo de kind
debe enrutar filas no-venta a 'garaje' (overture.py ya lo hace) para no contaminar el estrato compraventa.

## Huecos honestos
No re-verificado en esta sesion (confesado): (a) el conteo real de POIs automotive de FSQ para Espana — requiere una query
DuckDB en vivo contra el release HuggingFace; el propio §confianza del plan confiesa el mismo hueco. (b) La magnitud exacta
del solapamiento Overture<->FSQ<->OSM en Espana, que decide si FSQ es 2a o genuinamente 3a lista MSE — solo medible tras el
primer ingest (diferido a P02 por diseno). (c) Si el httpfs de DuckDB puede leer el parquet FSQ hosteado-en-HuggingFace tan
suave como el bucket S3 publico de Overture (auth header / soporte hf://) — el detalle de capa de acceso del paso 2 es
[ASUMIDO desde la evidencia VERIFICADA 'descarga HuggingFace gratis' + la nota H2 del repo], no corrido en vivo aqui. (d) El
~3,499 conteo ES de OSM `shop=car` del candidato no se re-fetcheo (el mundial 163,308 SI se confirmo via taginfo). **NO existe
coste EUR residual** en la ruta recomendada ni en los dos primeros fallbacks; la unica ruta de dinero es Google Places, gateada
deliberadamente para quedar a EUR0 en operacion normal (bajo el cap free ~5,000/mes Pro) y es decision owner-final, nunca
prerequisito.

---

# 5. captcha-solve — DataDome / hCaptcha / reCAPTCHA a EUR0 sin solver de pago

## Problema
Manejar retos DataDome, hCaptcha y reCAPTCHA en la capa de cosecha de CARDEEP a EUR0, sin API de
solver de pago. Verdad-base verificada en repo: el motor YA es un stack tiered avoidance-first que
empareja exactamente la conclusion estrategica. `pipeline/engine/fetch.py` = Tier-0 curl_cffi browser
impersonation con un cookie jar persistente; `pipeline/engine/ban_detector.py` clasifica OK / CHALLENGE
/ BANNED con marcadores DataDome+hCaptcha+reCAPTCHA+PerimeterX; `pipeline/engine/tier1/browser.py` =
Tier-1 headful browser (camoufox default MPL-2.0, nodriver opt-in AGPL-3.0) que resuelve un reto UNA VEZ
y mintea una cookie de clearance (cf_clearance/datadome/_abck) que Tier-0 replay bajo el MISMO UA+JA3+IP;
`clearance_cache.py` persiste la cookie. El hueco honesto: `solve_challenge()` solo maneja retos PASIVOS
(espera JS + scroll conductual). Cuando el browser recibe un captcha INTERACTIVO (reCAPTCHA v2 grid/audio,
hCaptcha imagen), devuelve el HTML aun-retado, `ban_detector` re-marca CHALLENGE, y el solve falla. Ningun
solver gratis esta cableado en esa rama. Tambien verificado: cosecha PARADA desde 2026-06-15; Tier-1
construido pero NUNCA usado en cosecha real; solo 1.570/12.587 dealers activos (12%) tienen web cosechable,
asi que el problema captcha esta acotado a ese 12% menos las plataformas API-abiertas.

## Ruta ganadora
**Avoidance-first como PRIMARIO** (ya en repo: mint de cookie camoufox/nodriver Tier-1 + replay curl_cffi
Tier-0), **mas un solver local-only de captcha INTERACTIVO** atornillado a la rama CHALLENGE existente de
`solve_challenge()`: `faster-whisper` (audio) + `recognizer`/YOLO+CLIP (imagen) para reCAPTCHA v2, y
`hcaptcha-challenger` local-ONNX para hCaptcha. DataDome queda en pura avoidance (no existe solver
end-to-end gratis).

**Por que gana.** No es un stack nuevo — es **terminar** el que CARDEEP ya construyo.
fetch.py/ban_detector.py/browser.py/clearance_cache.py implementan la tesis avoidance-first al pie de la
letra (reuso de cookie, deteccion fail-loud de CHALLENGE, humanizacion conductual). La UNICA pieza faltante
es un solver para el sub-caso de captcha interactivo de CHALLENGE, y todo componente es FOSS 100%-local con
cero API keys: `faster-whisper` (lib madura, modelo ~75MB int8, CPU-only) transcribe el reto de audio de
reCAPTCHA v2; `recognizer` (Vinyzu, GPL-3.0) corre YOLO11m-seg+CLIP local para el grid de imagen v2 como
fallback cuando el audio se bloquea; `hcaptcha-challenger` (GPL-3.0) fija un release ONNX pre-Gemini para
hCaptcha sin cuota. curl_cffi ya es el engine Tier-0 asi que la capa de avoidance TLS/JA3 no cambia. Para
DataDome — verificado que NO hay solver end-to-end gratis creible en 2026 — la respuesta durable es el mint
de cookie de clearance camoufox/nodriver con scroll conductual (ya codificado), y el baseline ~25% stealth-only
se sube con navegacion de warm-up + route-around de fuente (`pipeline/engine/source_fallback.py` ya fetchea
PRIMERO la web PROPIA del dealer, que no tiene WAF de marketplace).

**Base de gratuidad.** Todo solver recomendado es FOSS, local-only, sin API key, sin tarifa por-solve.
`faster-whisper`: lib MIT + descarga una-vez de modelo, solo tiempo CPU. `recognizer`: GPL-3.0, pesos
locales, sin servicio anti-captcha. `hcaptcha-challenger` ruta local-ONNX: GPL-3.0, EUR0. curl_cffi: MIT,
presets Chrome/Firefox gratis. camoufox: MPL-2.0. El copyleft GPL/MPL esta bien para un crawler cerrado
interno; la unica trampa de licencia es `nodriver`=AGPL-3.0 network-copyleft, ya marcado en browser.py y ya
por-defecto OFF en favor de camoufox.

## Fallbacks
- **FALLBACK 1 (reCAPTCHA v2, port de menor esfuerzo)**: `playwright-recaptcha` (Xewdy444, MIT). Su ruta de
  audio usa el endpoint SpeechRecognition gratis de Google (sin key) y su ruta v3 parsea el token
  `g-recaptcha-response` que el browser ya emite. Usar como referencia/quick-win para el flujo de audio, PERO
  fija la version y testea primero — esta 2 anos sin tocar (v0.5.1, 2024-06-10) y los internals de reCAPTCHA
  cambian. NUNCA pongas `image_challenge=True`: esa ruta exige `CAPSOLVER_API_KEY` (DE PAGO). Requiere FFmpeg
  (gratis). Rol: ruta mas rapida a un solver v2 audio funcional que portar desde cero; el patron faster-whisper
  de saifyxpro es el engine durable EUR0 al que migrar.
- **FALLBACK 2 (hCaptcha a bajo volumen / cuando la cobertura ONNX se degrada)**: ruta Gemini de
  `hcaptcha-challenger` con una API key Gemini GRATIS. Techos free-tier VERIFICADOS a 2026: Gemini 2.5 Flash
  ~10 RPM / 250 RPD, Flash-Lite ~15 RPM / 1000 RPD (las cuotas se recortaron 50-80% en dic-2025 y son revocables
  sin aviso). EUR0 estrictamente solo dentro de esos caps diarios — presupuesta el techo, maneja HTTP 429, y
  tratalo como solver de desborde, nunca la ruta primaria de crawl masivo. Dado solo ~1.570 dealers
  web-cosechables y siendo hCaptcha una fraccion de esos, 1000 RPD/key es plausiblemente suficiente.
- **FALLBACK 3 (escape manual-operador interactivo para cualquier captcha, incl. el interstitial
  `geo.captcha-delivery` de DataDome)**: Buster: Captcha Solver for Humans (dessant, GPL-3.0, v3.4.0 2026-06-20,
  9.1k stars). Extension de browser que resuelve reCAPTCHA v2 audio via STT free-tier (Wit.ai / Web Speech API /
  free tiers de IBM Watson, Google Cloud, Azure — multiples opciones STT EUR0, corrige la afirmacion previa de que
  solo Wit.ai era gratis). UX click-the-headphone, incomoda para crawl headless, asi que rol = fallback de operador
  manual en sesion Tier-1 headful cuando los solvers automaticos fallan y hay humano supervisando el warm-up de un
  dealer duro.

## Pasos de integracion
1. **Acota el problema primero (sin codigo).** Consulta la DB viva para enumerar cuales de los 1.570 dealers
   web-cosechables realmente pegan `ban_detector` `Verdict.CHALLENGE` con un captcha INTERACTIVO vs uno pasivo (los
   pasivos ya los maneja `solve_challenge`). El trabajo de solver solo importa para el subset interactivo —
   dimensionalo antes de construir. Cita: `pipeline/engine/ban_detector.py` (enum Verdict, `_CHALLENGE_MARKERS` /
   `_STRONG_BLOCK_MARKERS`).
2. Anade un clasificador de tipo-de-captcha a `pipeline/engine/ban_detector.py`: extiendelo para distinguir
   PASSIVE_CHALLENGE (cf managed / DataDome JS interstitial -> scroll+wait existente funciona) de
   INTERACTIVE_RECAPTCHA_V2 (presencia de g-recaptcha / iframe api2/anchor) e INTERACTIVE_HCAPTCHA (iframe hcaptcha.com).
   Los marcadores ya existen en `_CHALLENGE_MARKERS`; anade un sub-clasificador que devuelva el vendor para que
   browser.py enrute. Manten fail-loud: captcha desconocido -> Tier1Error.
3. Cablea el solver en `pipeline/engine/tier1/browser.py` dentro de `_solve_nodriver` / `_solve_camoufox`, DESPUES
   del wait_after_load + scroll conductual existente y ANTES de `get_content()`. Nuevo flujo: si la pagina aun muestra
   captcha interactivo, dispatch por vendor. Esta es la rama faltante exacta — hoy la funcion devuelve el HTML aun-retado
   y el solve falla silenciosamente el re-check de ban_detector.
4. **Engine reCAPTCHA v2** (modulo nuevo `pipeline/engine/tier1/solve_recaptcha.py`): PORTA el patron faster-whisper
   de saifyxpro (NO anadas el repo POC de 1-commit como dependencia — tratalo como referencia). Depende solo de
   `faster-whisper` (maduro) + FFmpeg. Click al boton de audio, baja el mp3, transcribe local con un modelo base int8,
   teclea la respuesta. Anade `recognizer` (Vinyzu) como fallback de grid de imagen para cuando Google bloquee el reto de
   audio — corre YOLO11m-seg+CLIP local, sin key. Los docs de `recognizer` exigen un browser undetected, que CARDEEP ya
   provee (camoufox/nodriver), asi que el emparejamiento es consistente.
5. **Engine hCaptcha** (modulo nuevo `pipeline/engine/tier1/solve_hcaptcha.py`): vendoriza `hcaptcha-challenger` y fija
   un release ONNX PRE-Gemini para EUR0/sin-cuota estricto. Expon una ruta Gemini-key opcional (Fallback 2) detras de un
   flag de config, default OFF, con presupuesto RPD explicito + manejo 429. Nunca hagas la ruta LLM el default.
6. **DataDome: NO intentes un solver. Refuerza solo avoidance.** (a) Baja el riesgo baseline de host-IP haciendo que
   `source_fallback.py` pruebe PRIMERO la web PROPIA del dealer (ya su prioridad default — verifica que realmente se invoca
   en `harvest_dealer.py`, que hoy ni siquiera importa la capa fetch/tier1). (b) Anade un paso de navegacion de warm-up en
   browser.py antes de pegar la URL objetivo (visita el home del marketplace, dwell, luego la pagina del dealer) para subir
   el baseline DataDome ~25% nodriver-only. (c) Manten el reuso de cookie de `clearance_cache.py` para que un solve DataDome
   exitoso amortice todo el drain paginado.
7. **Activa Tier-1 en la ruta de cosecha real.** VERIFICADO que Tier-1 esta construido pero nunca usado: `harvest_dealer.py`
   no importa `pipeline.engine.fetch` ni tier1. O bien enruta la cosecha via `FetchEngine(allow_tier1_escalation=True,
   tier1_engine='camoufox')` o via source_fallback. Este es el cambio de mayor palanca — los solvers son inertes hasta que la
   cosecha realmente llame al motor tiered.
8. **PRIMERO arregla los dos bloqueantes** que hacen crashear/mentir la cosecha antes de cualquier trabajo captcha, per bugs
   vivos verificados: (a) `pipeline/platform/coches_net_facet.py:295` llama `_ingest_window` con 7 args, la firma necesita 8
   (`prov_names` anadido en 9e36df9) -> el cosechador SCHEDULED canonico de coches.net crashea hoy. (b) 10 recetas web_generic
   con sample vacia (fetched:0) cargan `vam_verdict` TRUSTWORTHY (raiz: `_path_family` mapea fetched->http, parsed->db) — un
   captcha que da 0 listings NO debe certificarse TRUSTWORTHY; asegura que la ruta de fallo del solver devuelva un fallo real,
   no una VAM-certified empty.
9. **Gate de licencia (decision owner, superficia no escondas):** manten `tier1_engine` default = camoufox (MPL-2.0).
   `recognizer` + `hcaptcha-challenger` son GPL-3.0 y `faster-whisper` es MIT — todos bien para un crawler interno, pero el GPL
   se vuelve copyleft SI ese codigo se embarca dentro del binario del servicio API publico de CARDEEP. Manten los solvers en un
   proceso/modulo separado invocado por el worker de cosecha, no linkeado en el servicio FastAPI, para mantener la API limpia de
   GPL/AGPL. nodriver (AGPL) queda opt-in only.
10. **Verifica, no asumas.** Anade tests bajo el harness existente (83 files / 1066 funcs) para: clasificacion de
    captcha-vendor de ban_detector; el solver devuelve Tier1Error en fallo (fail-loud, nunca un fake-OK empty page); el pinning
    de cookie+UA sobrevive el replay Tier-0. NOTA el gap de CI verificado: CI solo corre `pytest --collect-only` (NO ejecuta los
    tests); '937 green' es historico. Estos tests deben correr localmente y arreglar CI para que realmente ejecute, o el verde es
    teatro.

## Riesgo residual
DataDome es el residual duro: no existe solver end-to-end gratis en 2026, y el baseline stealth-only nodriver es ~25%
(VERIFICADO via Scrapfly). Lo que lo sube materialmente — proxies residenciales ES sticky — es el coste recurrente real y esta
FUERA de scope de 'captcha solver' pero ES el coste al que todo guia converge. browser.py ya marca proxy como PENDING-CREDENTIAL.
La cookie de clearance esta atada a la IP que resuelve, asi que sobre la host IP el reuso se rompe en cuanto la IP se marca. Los
solvers reCAPTCHA/hCaptcha son fragiles-por-diseno: Google cada vez mas rehusa servir el reto de audio a bots sospechosos (mata la
ruta faster-whisper), hCaptcha rota tipos de reto y erosiona la cobertura ONNX con el tiempo, y los internals de receta derivan
(playwright-recaptcha ya 2 anos stale). Los solvers deben fijarse y re-testearse en agenda, no set-and-forget. Las cuotas free de
Gemini se recortaron 50-80% en dic-2025 y son revocables sin aviso. Finalmente: incluso un solver perfecto cierra a lo sumo el 12%
de dealers (1.570/12.587) con web cosechable — no toca el 88% sin web, ni arregla el gap estructural de descubrimiento/exhaustividad
(el cuello real ~5.9/10 per el diagnostico V2).

## Huecos honestos
Coste residual EXACTO nombrado: proxies ES rotativos residenciales para WAFs IP-bound DataDome/Akamai. Workarounds EUR0 mas baratos,
en orden: (1) route-around de `source_fallback.py` — fetchea PRIMERO la web PROPIA del dealer; la web propia casi nunca esta tras
DataDome, asi que el WAF del marketplace se bypassa entero para el inventario de ese dealer (ya codificado, solo no cableado en
harvest_dealer.py). (2) Rotacion de free proxies — `pipeline/engine/free_proxies.py` YA EXISTE en repo; las listas gratis son baja
calidad/efimeras pero EUR0 y ciclables agresivamente con el `ban_detector` existente para descartar quemadas. (3) Ciclado IP
Sequana/CGNAT — un reset de conexion casa/movil rota la IP de egress gratis a bajo volumen. (4) Amortizacion agresiva de cookie de
clearance — un solve host-IP, luego drena el inventario paginado entero detras de esa unica cookie antes de quemar la IP
(clearance_cache.py ya lo soporta), minimizando la frecuencia de solve. HONESTO: ninguno alcanza la fiabilidad de proxy-residencial-de-pago;
a EUR0 estricto contra DataDome vivo la postura realista es ~25% + route-around + own-site-first, aceptando que algunos dealers
marketplace-only duros no cerraran hasta aprobar presupuesto de proxy (que el mandato difiere a la ultima fase). NO runtime-testee
ningun solver contra un captcha vivo en esta sesion — las afirmaciones de viabilidad estan VERIFICADAS a nivel de libreria/repo
(licencias, madurez, local-only, no-key) pero la TASA de exito end-to-end contra el reCAPTCHA/hCaptcha/DataDome 2026 actual debe medirse
empiricamente antes de confiar; el sizing del paso-1 + un spike en vivo son obligatorios antes de comprometer la cosecha.

---

# 6. photo-egress — descarga + pHash de ~1.68M fotos contra CDNs anti-bot

## Problema
Descargar/perceptual-hash ~1.68M fotos de vehiculos ES para un backfill de pHash a EUR0, contra CDNs anti-bot,
alimentando el validador V16 Photo pHash Deduplication de CARDEEP.

## Ruta ganadora
**Dedup-antes-de-fetch (distinct photo_url) + sampling estadistico para el umbral + rewriting de endpoints
thumbnail/low-res**, todo enrutado por el motor fetcher curl_cffi EXISTENTE ya en `enrich_worker.py` — NO un cliente
HTTP nuevo.

**Por que gana.** Es el unico stack a la vez gratis, viable Y ban-superviviente contra los CDNs ES anti-bot en scope.
Verificado contra codigo vivo: V16 (`quality/internal/validator/v16_photo_phash/v16.go`) hoy fetchea cada imagen dentro
de `computePHash()` con un cliente `net/http` pelado (cableado `NewWithClient` en
`quality/cmd/quality-service/main.go:164`) y DESCARTA el hash (corre sobre el `noopHashStore` default, asi que
`StoreHash`/`FindSimilar` son no-ops). Eso significa que tres de las cuatro palancas raiz no estan construidas todavia, y la
unica ruta de fetch que existe tiene cero JA3 impersonation — seria bloqueada por Cloudflare/DataDome en los CDNs de dealer ES.
El movimiento ganador apila los cortes multiplicativos que no necesitan infra nueva: (1) fetchea cada photo_url DISTINTA una vez
(la palanca imagededup/SQL DISTINCT — factor de dedup no-medido pero el mecanismo es SQL+set puro, EUR0); (2) ajusta
`PHASH_HAMMING_MAX` desde una muestra estadisticamente valida (n=9,604 a +-1%, z=1.96, p=0.5 — exacto per Penn State STAT200) para
que el backfill calibre sobre miles, no millones; (3) reescribe cada URL a la variante thumbnail/low-res de la fuente (pHash
redimensiona a 32x32 igual, asi que un thumb de 200-320px da un hash casi-identico — jenssegers confirma que la familia siempre
downsamplea), cortando egress 10-50x. Crucial: enruta todo via `enrich_worker.make_engine_fetcher` (la sesion curl_cffi cacheada
por-(domain,country) ya JA3-coherente y country-correcta per el invariante de binding), para que el egress sobreviva la capa
anti-bot en vez de pelearla.

**Base de gratuidad.** Todo software es FOSS: imagededup Apache-2.0, curl_cffi MIT (ya dependencia de la flota viva), goimagehash
ya vendorizado en V16. Los fetches corren sobre hardware que CARDEEP ya posee (el VPS scraper que corre la flota). Cero servicio
nuevo, cero cuenta, cero tarifa por-request. La matematica de sampling y el colapso DISTINCT REDUCEN el conteo de bytes en vez de
comprar capacidad, asi que no hay gasto que compensar.

## Fallbacks
- **wsrv.nl free image-resize proxy** (Cloudflare-fronted, BSD-3-Clause, sin cuenta) como ESCUDO-IP y generador de thumbnails para
  la pasada SAMPLE (~9.6k-16k): oculta la IP de egress de CARDEEP del CDN de dealer Y sirve la imagen reducida. Residual: cap DURO
  2,500 req sin-cache/IP por 10 min luego bloqueo 1h (~15k/h techo) — confirmado contra politica actual; la evidencia del candidato
  (issue #196) esta mal-fuenteada (afirma la cifra vieja 700/3min) pero el numero 2,500/10min es correcto. Cubre la sample comodo;
  NO puede hacer el set completo deduped desde una IP. SLA best-effort. Usar solo para la muestra de calibracion.
- **Self-host weserv/images** (BSD-3-Clause, libvips, Docker) O imgproxy (core Apache-2.0 — NO MIT como afirmo el candidato) sobre el
  hardware PROPIO scraper de CARDEEP para remover el cap 2,500/10min entero y hacer resize-thumbnail ilimitado del set deduped completo.
  Sobre hardware propio la afirmacion EUR0 es solida. NO dependas de Oracle Always-Free ARM: se recorto a 2 OCPU/12GB ~2026-06-15 y esta
  cronicamente 'Out of Capacity', asi que la premisa de 'VM gratis perpetua' ya no es fiable — self-host en la caja que la flota ya corre.
- **Conditional GET (ETag/If-Modified-Since -> 304)** sobre el engine fetcher para la fase de MANTENIMIENTO (mantener photo_hash VIVO tras
  el backfill, no el backfill en si). curl_cffi soporta los headers custom. Cero beneficio en la primera pasada e inutil donde un CDN de
  dealer omite validators, asi que es un byte-saver de fase-mantenimiento, no una palanca de backfill.

## Pasos de integracion
1. **MIDE PRIMERO (bloquea todo el estimado):** corre `SELECT COUNT(*), COUNT(DISTINCT photo_url)` contra la tabla PostgreSQL
   vehicles/media para el factor de dedup real. `psql` NO estaba en PATH durante la verificacion, asi que el '1.68M' y cualquier
   multiplicador de 'gran ahorro' es ASUMIDO, no medido. Hasta que este numero exista, la magnitud del payoff EUR0 no esta probada.
   (Modulo: `services/entity_api` o `scripts/init-pg.sql` define la columna photo; `thumbnail_url` + `photo_urls` originan en
   `scrapers/enrich_worker.py record_to_payload`, lineas 152-154.)
2. Construye el indice pHash persistente que V16 hoy carece. V16 (`quality/internal/validator/v16_photo_phash/v16.go`) define una
   interfaz `HashStore` (`FindSimilar`/`StoreHash`) pero esta cableada al `noopHashStore` en `quality/cmd/quality-service/main.go:164`
   via `NewWithClient` — asi que cada hash computado se tira hoy. Implementa un `HashStore` real sobre el store SQLite existente
   (`quality/internal/storage/storage.go`) y cambia el cableado a `NewWithStore`. Sin esto no hay estado de dedup y el backfill no puede
   resumir ni deduplicar. Respeta el invariante de que `scrapers/engine.db` queda SQLite — pon la tabla pHash en el KG SQLite de quality,
   no en PG.
3. Anade un guard distinct-URL frente a `computePHash`: antes de fetchear, chequea StoreHash/un indice por el photo_url exacto (no solo el
   hash) para que una URL vista en cualquier vehiculo previo nunca se re-descargue. Esta es la palanca dedup-antes-de-fetch y convierte el
   conteo de fetch en `COUNT(DISTINCT photo_url)`. imagededup (Apache-2.0) puede computar el PHash/DHash si prefieres dedup Python-side, pero
   goimagehash ya esta vendorizado, asi que no hace falta dependencia nueva.
4. **REEMPLAZA el cliente de egress de V16.** `computePHash` (v16.go:172) usa un cliente `net/http` pelado SIN JA3 impersonation, y
   main.go:164 le pasa `http.Client{Timeout:15s}`. Contra CDNs ES anti-bot esto es muerto-a-la-llegada. Enruta el fetch del backfill por la
   MISMA factory de sesion curl_cffi por-(domain,country) que `enrich_worker.make_engine_fetcher` ya construye (`scrapers/enrich_worker.py:478-530`),
   que el sistema confia como JA3-coherente y country-correcta (invariante de binding: TLS impersonate a nivel SESION, mismo JA3 pagina 1->N,
   floor Chrome-actual >=136). Manten el guard SSRF `safeurl.CheckURL` (v16.go:173) y el cap de decode 20 MiB (v16.go:46) en la ruta nueva — no los tires.
5. **URL-rewrite a thumbnail/low-res antes de fetch:** por cada source_key, halla el param de size/thumbnail y reescribe photo_url a la variante
   ~200-320px. Valida UNA VEZ por fuente computando el bit-delta entre pHash full-res y thumb (el guard 'verify bit delta first' del candidato) y solo
   confia el thumbnail cuando el delta esta dentro de tolerancia — pHash downsamplea a 32x32 asi que el delta es tipicamente <=3-4 bits. Este es el corte
   de egress 10-50x. Guarda la regla de rewrite validada por fuente (`configs/portals/<s>.json` es el hogar de config por-fuente existente).
6. **CALIBRA el umbral sobre muestra, no sobre el set completo:** saca una muestra aleatoria estratificada (por source_key y value-tier) de n=9,604 URLs
   distintas (+-1%, z=1.96, p=0.5 — exacto) para ajustar `PHASH_HAMMING_MAX`. Nota: el '+-0.78% needs 16,512' del candidato es un ~5% sobre-conteo; la cifra
   correcta es 15,786. El `maxDist` de V16 esta hard-codeado a 4 (v16.go:52) — promuevelo a un set tunable desde el resultado de la sample antes del run completo.
7. **Throttlea a los rate limits de supervivencia-de-fuente de la flota** (jitter 1.2+-0.4s/pagina, floor DIRECT 0.5-1 req/s per el invariante). A 0.7 req/s la
   sample de calibracion es trivialmente gratis; el set completo deduped+thumbnailed esta acotado por el conteo DISTINCT del paso 1.
8. **Persiste progreso a PROGRESO.md tras cada batch** (invariante estado-a-disco) para que el backfill multi-dia sea resumible, y verifica la cobertura pHash
   final via quorum VAM (>=2 rutas ortogonales) antes de declarar el backfill TRUSTWORTHY — el CHECK de la DB lo impone.

## Riesgo residual
Tres riesgos, todos EUR0-mitigables. (1) MAGNITUD NO-PROBADA: '1.68M' y el multiplicador de dedup nunca se midieron (psql no en PATH); si el colapso distinct-URL
es pequeno el volumen de bytes queda alto — mitigado porque el paso 1 cuesta una query, y porque incluso con dedup pobre el thumbnail rewrite da 10-50x. (2) BAN EN
LA COLA DURA: los params de thumbnail no existen en todo CDN, y algunos CDNs de dealer ES retaran incluso una sesion curl_cffi JA3-coherente. El workaround EUR0 para la
cola es el stack residential-proxy aprobado (Decodo/Oxylabs) SOLO cuando una fuente se gatea abierta por politica — pero eso es gasto metered, ver huecos. La opcion
pura-EUR0 de la cola es Tor (`socks5h://127.0.0.1:9050` + stem NEWNYM), aceptada como ultimo recurso fino solo para thumbnails; el exito esperado contra DataDome/PerimeterX
es pobre porque la lista de exits Tor es publica y proactivamente blocklisteada, asi que no planees throughput sobre ella. (3) SLA de wsrv.nl: best-effort, cap 2,500/10min/IP,
bloqueo 1h en breach — bien para la sample, nunca la ruta-completa unica; self-hosting weserv remueve el cap en hardware propio.

## Huecos honestos
NO se da respuesta 'necesita dinero', y aqui esta el unico lugar donde un euro podria esconderse, nombrado exacto con su workaround EUR0: el egress aprobado residential-proxy
Decodo/Oxylabs (CARDEX Strategy B) es METERED por-GB y es lo unico con tasa de exito real contra los CDNs ES anti-bot mas duros. NO es requerido para el backfill — su coste se
evita entero por (a) el thumbnail rewrite que encoge cada fetch 10-50x, (b) el colapso DISTINCT, y (c) enrutar por las sesiones curl_cffi engine ya pagadas en hardware propio. Si
una fuente especifica sigue bloqueando tras los tres, el fallback EUR0 es Tor para la cola de esa fuente (aceptando bajo yield) en vez de pagar GB de proxy. Otros huecos honestos:
(1) el conteo real de fotos y el factor de dedup estan SIN MEDIR — el paso 1 debe correr antes de confiar cualquier promesa de throughput; trata 1.68M como placeholder. (2) El
dedup de V16 es hoy un no-op en produccion (noopHashStore en main.go:164) — el HashStore persistente es trabajo neto-nuevo, no un flip de config. (3) Las afirmaciones de licencia
del candidato tenian errores que corregi: imgproxy core es Apache-2.0 (no MIT), cdx_toolkit es Apache-2.0 (no MIT); el yield de Common Crawl para CDNs de dealer ES es genuinamente
BAJO (ancho-no-profundo, respeta robots) asi que NO lo incluí ni como fallback. (4) Oracle Always-Free ARM ya no es VM gratis fiable (recortado ~2026-06-15, Out-of-Capacity cronico) —
self-host en la caja scraper existente.

---

# Compuertas adicionales (barrido del repo)

> Estas seis compuertas de dinero NO estaban en el set conocido de sintesis y aparecen por barrido de los
> planes P10-P14 y P01-P02. Cada una verificada en codigo con su `file:line`. Todas comparten la misma doctrina:
> **coste-cero hasta A->Z**, gasto externo = decision final del owner. La ruta EUR0 de cada una es el self-host /
> el tier OSS / el diferimiento.

## 7. vps-hosting — hosting VPS recurrente + Terraform
- **Evidencia:** `plans/P13.md:28` ('Compose en un VPS Hetzner (~20-50 EUR/mes)'); reforzado en P13.md:42
  (modulo Terraform hcloud declara server+volume+firewall), P13.md:94 ('terraform apply y la creacion del VPS son
  IRREVERSIBLES y con coste real'), P13.md:70 (P13.6 modulo hetzner).
- **Ruta ganadora EUR0:** correr el `docker-compose.yml` con perfiles (`core`/`app`/`llm`/`obs`, P13.4) en el host
  siempre-encendido que el operador YA posee (la misma caja de cosecha/orquestacion que corre APScheduler+subprocess y
  el clasificador local). El single-producer de la flota (scheduler.py: un subproceso en vuelo, max_instances=1, disenado
  para 16GB) cabe en hardware existente. El VPS Hetzner solo se vuelve necesario para serving publico 24/7 con SLA.
- **Fallbacks:** (a) entorno local + tunel (cloudflared/ngrok free tier) para exponer la API en demos sin VPS; (b)
  diferir el VPS hasta tener A->Z + certificado de cobertura emitido (el gate de Fase 6, P13.md:46).
- **Pasos de integracion:** mantener `terraform plan` / `terraform validate` corriendo limpio SIN `apply` (P13.6 exit
  criteria); el `apply` queda como accion irreversible gateada por instruccion literal del owner. El estado vive en backend
  remoto cifrado; `terraform destroy` revierte.
- **Riesgo residual:** `terraform apply` es irreversible y con coste real (P13.md:94) — jamas ejecutar sin orden literal.
  Self-host carece de la disponibilidad/ancho de banda de un VPS para serving publico a escala.
- **Huecos honestos:** NO verifique en vivo los recursos exactos que la imagen R+Splink exige en runtime (P13 §7 lo deja
  como estimacion de rango, no medicion); si el host existente no soporta la capa R, el VPS deja de ser opcional. El rango
  20-50 EUR/mes es del plan, no cotizado por mi esta sesion.

## 8. amass-premium-keys — API keys premium de fuentes OSINT
- **Evidencia:** `plans/P01.md:85` ('el quadtree de Google Places y amass con API keys de fuentes premium tienen coste').
- **Ruta ganadora EUR0:** correr **Amass v5.1.1 (Apache-2.0) SOLO con sus 80+ fuentes pasivas gratis / sin-key**. Amass funciona
  sin ninguna API key; las keys premium (clase SecurityTrails/Censys) solo amplian la enumeracion de subdominios. Para el vector de
  descubrimiento CARDEEP, las fuentes gratis de Amass + los vectores ortogonales ya gratis del repo (CT crt.sh, PDNS, Common Crawl
  CCWEB, FSQ, wallapop api/v3) cubren el descubrimiento sin pagar keys.
- **Fallbacks:** (a) Certificate Transparency via crt.sh (gratis, ya planificado como adapter CT) en lugar de las fuentes premium de
  subdominio; (b) Common Crawl columnar index + cdx_toolkit (Apache-2.0) para descubrir dominios .es desde el crawl publico.
- **Pasos de integracion:** entregar primero las vias gratis (CT/CCWEB/FSQ/wallapop, P01.md:85); configurar Amass sin bloque de keys;
  dejar las keys premium como bloque de config opcional desactivado.
- **Riesgo residual:** sin keys premium la profundidad de enumeracion de subdominios es menor; mitigado por la redundancia ortogonal
  CT+PDNS+CCWEB (P01.md:80 ya prescribe redundancia precisamente por los rate-limits de crt.sh).
- **Huecos honestos:** NO medí cuanta cobertura de descubrimiento adicional aportarian las keys premium sobre las fuentes gratis; el
  plan las trata como decision final del owner, no como prerequisito. Amass v5.1.1 Apache-2.0 / 80+ fuentes verificado en P01 §confianza.

## 9. mse-compute — coste de runtime del quorum captura-recaptura
- **Evidencia:** `plans/P02.md:107` ('dga+LCMCR+SparseMSE+DR-ML por ~209 estratos x varias olas puede ser lento; mitigable con
  batch.estimates y BLB paralelo, pero el quorum completo no es gratis (decision de coste del owner)').
- **Ruta ganadora EUR0:** correr el quorum **localmente sobre el R-portable + CPU del host existente**, con `batch.estimates` y
  **Bag of Little Bootstraps (BLB) paralelo** para que ~209 estratos x olas quepan en el hardware propio. Es coste de CPU/electricidad,
  no de servicio: EUR0 incremental sobre la caja que ya corre el clasificador nocturno y la flota. El cost-router LLM-local-first de P13
  hace que re-ejecutar la prueba completa sea ~$0 (P13.md:87), permitiendo emitir el certificado en cada push sin gasto.
- **Fallbacks:** (a) ejecucion por lotes nocturna (off-peak) en vez de en-linea; (b) reducir la cadencia del quorum completo a
  semanal/por-release y servir entre-medias el ultimo certificado cacheado; (c) limitar el quorum a los estratos que cambiaron desde la
  ultima ola (incremental).
- **Pasos de integracion:** usar `batch.estimates` + BLB paralelo (P02.md:107 mitigacion ya nombrada); acoplar la emision del certificado
  al job `behavioral-suite` de CI (P13.6 beyond-SOTA) para que el coste marginal sea ~$0 por push.
- **Riesgo residual:** el quorum completo (dga+LCMCR+SparseMSE+DR-ML) sobre 209 estratos x varias olas es lento; en CPU modesta una corrida
  completa puede tardar horas — mitigado por paralelismo BLB y lotes, pero no instantaneo. Si el host se queda corto de CPU, escalar compute
  es la decision de coste del owner.
- **Huecos honestos:** NO verifiqué si MSETools/SparseMSE estan ya instalados en el R-portable (P02 §confianza lo asume NO, de ahi el paso de
  instalacion en S3). NO medí el tiempo de pared real del quorum completo en el hardware CARDEEP — el plan lo describe cualitativamente como
  'lento', sin benchmark. La portabilidad del estimador DR de population-size (paper Dulce Rubio 2026, sin codigo publicado) es ASUMIDA.

## 10. lineage-service — servicio OpenLineage/Marquez (contenedor operativo extra)
- **Evidencia:** `plans/P14.md:93` ('OpenLineage/Marquez (S7) anade un servicio operativo (otro contenedor) - coste de mantenimiento');
  P14.md:70 despliega Marquez via compose.
- **Ruta ganadora EUR0:** **emitir eventos OpenLineage** (libreria, EUR0) en el path fetch->parse->ingest->served **sin desplegar Marquez todavia**.
  La emision de eventos con DataQuality facet es lo que la VAM necesita (P14.md:79); el visor Marquez es un lujo diferible. Self-host de Marquez via
  compose en el host existente (EUR0 incremental) solo cuando el valor de auditoria lo justifique.
- **Fallbacks:** (a) loggear los eventos OpenLineage a fichero/tabla y consultarlos con SQL en vez de levantar el visor Marquez; (b) diferir S7 entero
  — P14.md:70 lo marca como 'el paso mas diferible', gateado por valor real para VAM.
- **Pasos de integracion:** implementar la emision de eventos (P14-S7 criterio: cada ingest emite evento con inputs fuente/receta + outputs entidad/vehicle +
  facet de calidad) ANTES de desplegar Marquez; el contenedor Marquez se levanta solo si la procedencia visual se vuelve necesaria.
- **Riesgo residual:** Marquez es otro contenedor con coste de mantenimiento operativo (CPU/RAM/parcheo) en el host; el paso es el mas diferible de P14.
- **Huecos honestos:** NO verifiqué el acoplamiento exacto proceso-API vs proceso-scraping que condiciona el dimensionado de S3/S7 (P14 §confianza lo marca
  ASUMIDO). La licencia de `datacontract-cli`/`soda-core` (NOASSERTION en GitHub) debe confirmarse leyendo el LICENSE antes de adoptarlas — riesgo de
  coherencia con la propia politica de licencias.

## 11. redis-infra — Redis para cache + rate-limit distribuido del serving
- **Evidencia:** `plans/P11.md:94` ('Introducir Redis (cache+ratelimit distribuidos) anade una dependencia de infra con coste; la doctrina es coste-cero
  hasta A-Z. Mitigacion: Redis self-host local en el VPS (€0 incremental) y el gasto externo es decision final del owner').
- **Ruta ganadora EUR0:** mantener el **fallback in-process** (cache + rate-limit en memoria del proceso API) para dev y volumen bajo, y cuando haga falta
  cache distribuido, **self-host Redis en el host/VPS propio** (EUR0 incremental, un contenedor mas en el compose). El Redis gestionado externo (Upstash/
  ElastiCache) es decision final del owner.
- **Fallbacks:** (a) cache in-process documentado (P11.md:94 ya lo nombra como fallback para dev); (b) rate-limit por-proceso si solo hay un worker de API
  (consistente con el single-producer de la flota).
- **Pasos de integracion:** mantener el fallback in-process como default; anadir Redis self-host como servicio del compose solo cuando se escale a multiples
  workers de API que necesiten estado compartido de cache/rate-limit.
- **Riesgo residual:** sin Redis, cache y rate-limit no se comparten entre multiples procesos de API — limita el escalado horizontal del serving. Self-host
  Redis anade un contenedor a mantener.
- **Huecos honestos:** NO verifiqué cuantos workers de API se planean en produccion (determina si el cache distribuido es necesario). El '€0 incremental' del
  self-host asume que el VPS/host ya tiene RAM holgada para Redis — no medido.

## 12. observability-saas — SigNoz Enterprise / Grafana Cloud (backend observabilidad)
- **Evidencia:** `plans/P10.md:24` (SigNoz 'NOASSERTION (MIT core + Enterprise license para modulos cloud)'); P10.md:22 anticipa 'Prometheus hoy,
  SigNoz/Grafana Cloud manana'.
- **Ruta ganadora EUR0:** instrumentar con **OpenTelemetry Python SDK + PrometheusMetricReader** (Apache-2.0, P10.md:21-22) y servir las metricas con el
  **Prometheus+Grafana self-hosted** que P13.7 ya provisiona como codigo (perfil `obs` del compose). El SigNoz CORE es self-hostable gratis via Docker Compose
  (P10.md:25); solo los modulos Enterprise/cloud son de pago. El estandar OTel garantiza no-lock-in: Prometheus hoy, migrar a SigNoz-core o Grafana Cloud manana
  sin re-instrumentar.
- **Fallbacks:** (a) SigNoz core self-hosted (un contenedor OTLP, P10.md:25) en vez de Prometheus+Grafana separados — gratis; (b) Prometheus+Grafana+Alertmanager
  self-hosted (P13.7) como baseline; (c) diferir cualquier backend SaaS hasta produccion.
- **Pasos de integracion:** instrumentar una vez con OTel SDK (Counter harvest_runs, repair_attempts; Histogram harvest_latency; Gauge breaker_open, label
  domain=origen — P10.md:22) y apuntar a Prometheus self-hosted; el SaaS (Grafana Cloud / SigNoz Enterprise) queda como destino opcional futuro, decision del owner.
- **Riesgo residual:** el self-host de observabilidad consume CPU/RAM del host y exige cuidado de cardinalidad de labels (~181 sources x phases, P10.md:22) para no
  explotar las series. El tier cloud/Enterprise no se adopta — presentado como destino futuro, no compromiso.
- **Huecos honestos:** baja confianza — esta compuerta esta presentada como destino opcional futuro, no adoptada hoy; superficiada por completitud. La licencia de
  SigNoz es NOASSERTION (MIT core + Enterprise) per metadata de GitHub, a confirmar leyendo el LICENSE si se adopta el core.

---

# Tabla resumen

| # | Gate | Ruta gratis (ganadora) | EUR0 | Confianza |
|---|------|------------------------|------|-----------|
| 1 | egress-ip | DIY 4G: Pi + Huawei E3372 + 3proxy (`socks5://` en `CARDEEP_PROXIES`) + rotacion `huawei-lte-api` | with-residual (banda 5-11% bloqueo; HW one-time si no hay SIM/host) | Alta (codigo); Media (eficacia no corrida en vivo) |
| 2 | antibot-engine | Patchright (Apache-2.0) como primario Tier-1 + Camoufox secundario | with-residual (proxy residencial ES sticky es el techo IP, no el engine) | Alta (contrato/licencias); Media (no smoke-test) |
| 3 | llm-edge | llama.cpp `llama-server` + GBNF/JSON-Schema grammar, self-hosted | yes (EUR0 incremental sobre HW existente; mint-once+freeze) | Alta (intencion de diseno en codigo); Media (no ejecutado) |
| 4 | geo-places | DuckDB + Overture + OSM + FSQ (HuggingFace) — motor ya en repo, falta adapter FSQ | yes (licencias permisivas; bbox pushdown; sin key) | Alta (motor en repo); Media (conteos/solape ES no medidos) |
| 5 | captcha-solve | Avoidance-first (ya en repo) + solvers locales faster-whisper / recognizer / hcaptcha-challenger ONNX | with-residual (DataDome sin solver gratis; ~25% + route-around + proxy ES = techo) | Alta (libreria/repo); Media (tasa e2e no medida en vivo) |
| 6 | photo-egress | Dedup-before-fetch + sampling estadistico + thumbnail rewrite, via curl_cffi de enrich_worker | yes (reduce bytes, no compra capacidad; cola dura -> Tor EUR0) | Alta (codigo V16); Baja (conteo 1.68M y dedup SIN medir) |
| 7 | vps-hosting | docker-compose con perfiles en host propio; VPS Hetzner diferido a Fase 6 | yes (self-host; VPS = owner decision) | Alta (P13 verificado); Media (recursos R+Splink no medidos) |
| 8 | amass-premium-keys | Amass v5.1.1 con 80+ fuentes gratis/sin-key + CT/CCWEB/FSQ/wallapop ortogonales | yes (keys premium opcionales, off) | Alta (P01 verificado); Media (delta de cobertura no medido) |
| 9 | mse-compute | Quorum R local + batch.estimates + BLB paralelo en CPU propia, acoplado a CI | yes (CPU/electricidad; ~$0 marginal por push) | Alta (P02/P13 verificado); Media (tiempo de pared no benchmarkeado) |
| 10 | lineage-service | Emitir eventos OpenLineage (lib EUR0); diferir/self-host Marquez | yes (eventos gratis; Marquez self-host EUR0 incremental, diferible) | Alta (P14 verificado); Media (acoplamiento proceso no medido) |
| 11 | redis-infra | Fallback in-process para dev; Redis self-host en host propio cuando escale | yes (self-host EUR0 incremental; gestionado = owner) | Alta (P11 verificado); Media (Nº workers/RAM no medido) |
| 12 | observability-saas | OTel SDK + Prometheus+Grafana self-hosted (P13.7) / SigNoz core; SaaS diferido | yes (core self-host gratis; Enterprise/cloud = owner) | Media-baja (destino futuro opcional, no adoptado) |

**Veredicto global:** 12/12 compuertas tienen ruta EUR0. Ocho son **yes** (EUR0 limpio: llm-edge, geo-places,
photo-egress, vps-hosting, amass-premium-keys, mse-compute, lineage-service, redis-infra, observability-saas).
Cuatro son **with-residual**: egress-ip (banda 5-11% de bloqueo + HW one-time si no hay SIM/host), antibot-engine
y captcha-solve (ambas convergen al mismo techo: el proxy residencial ES sticky, diferido a la ultima fase por
mandato), y photo-egress (cola dura de CDN -> Tor EUR0 con bajo yield). En ningun caso el dinero es prerequisito
para entregar; el gasto, donde existe, es la ultima fase y decision final del owner.

---
_Confianza del dossier: las seis compuertas conocidas provienen de sintesis por-gate con verificacion in-code
declarada por cada candidato (costuras proxies.py/fetch.py/browser.py/ban_detector.py/free_proxies.py/v16.go citadas
con file:line). Las seis compuertas adicionales las VERIFIQUE yo leyendo `plans/P13.md:28,42,70,94`, `plans/P01.md:85`,
`plans/P02.md:107`, `plans/P14.md:70,93`, `plans/P11.md:94`, `plans/P10.md:22,24` — citas confirmadas linea a linea
en HEAD del repo. Huecos transversales no resueltos esta sesion: (1) ningun solver/engine/IP fue runtime-testeado en
vivo contra los WAFs 2026 — las tasas de exito deben medirse antes de comprometer la cosecha; (2) el conteo real de
fotos (1.68M) y el factor de dedup estan SIN medir (psql no en PATH); (3) los recursos de hardware del host CARDEEP no
se inventariaron, asi que las promesas de 'EUR0 incremental' en self-host (VPS/Redis/MSE/observabilidad/LLM) asumen RAM/CPU
holgadas. El bug vivo `coches_net_facet.py:295` (7 args vs 8) bloquea el cosechador canonico de coches.net y debe arreglarse
antes de que cualquier arreglo de egress/engine/captcha rinda en coches.net._
