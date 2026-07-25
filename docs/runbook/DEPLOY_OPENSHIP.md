# DEPLOY vía Openship — de local a servidor público

> Este doc cubre el despliegue **público** (servidor real, dominio, TLS, push-to-deploy).
> El [DEPLOY.md](DEPLOY.md) hermano cubre el bring-up **local** (€0, sin servidor) — sigue
> siendo el camino recomendado para desarrollo. Este doc es el siguiente paso, cuando el
> owner decida hacer Cardeep públicamente accesible.
>
> **Estado: dominio resuelto, servidor pendiente.** `openship.json` (raíz del repo) y
> `web/Dockerfile` están escritos, validados contra el JSON Schema oficial de Openship y con
> el build de `web/` verificado localmente (ver §4). Dominio decidido y verificado en vivo:
> **`deepcar.duckdns.org`** (DuckDNS, €0, A record resolviendo globalmente desde
> 2026-07-25). Falta solo el servidor — ver §0.

---

## 0. Bloqueante — decisión del owner, no ejecutable por IA

Openship es una plataforma de despliegue **autoalojada** (self-hosted): el "control plane"
puede correr localmente o en la nube de Openship, pero para que Cardeep quede **públicamente
accesible** —con push-to-deploy, TLS y dominio propio— hace falta:

1. Un **servidor Linux con Docker** (VPS) — Openship necesita host networking en Linux para
   su edge (`:80`/`:443`). **PENDIENTE, en curso**: decisión tomada — Oracle Cloud Always
   Free, shape Ampere A1 (ARM, 2 OCPU/12GB RAM), región Frankfurt. Cuenta en creación por el
   owner (verificación de identidad con tarjeta real — paso que ninguna IA puede completar).
2. Un **dominio** con su DNS apuntando a ese servidor — Openship exige el registro DNS
   *antes* de instalar. **RESUELTO 2026-07-25**: `deepcar.duckdns.org` (DuckDNS, cuenta
   `sublimine@github`, €0). Verificado en vivo: resuelve vía DNS público (`nslookup` contra
   8.8.8.8) y el mecanismo de actualización probado responde `OK`
   (`https://www.duckdns.org/update?domains=deepcar&token=...`). Token guardado FUERA del
   repo en `~/.cardeep-ops-secrets/duckdns.env` (permisos 600) — Cardeep es repo público,
   nunca se commitea. Apunta hoy a la IP doméstica del owner como placeholder operativo; se
   re-apunta a la IP real del VPS con el mismo comando en cuanto exista.

El VPS implica **gasto potencial** (el Ampere A1 es €0 dentro de cuota, pero Oracle recortó
la cuota Always Free en junio-2026 sin aviso y hay ambigüedad no resuelta sobre facturación
del excedente — detalle en PROGRESO.md) y **exposición externa** (el sistema pasa de privado
a público). Por doctrina del proyecto esto exige orden literal del owner — **recibida**
(autorización explícita a implementar todo A→Z). Lo que resta depende únicamente de que la
cuenta Oracle —gesto que solo el owner puede completar por la verificación de identidad—
quede lista.

**Alternativa sin VPS propio:** Openship Cloud (`openship.io`, gestionado) evita provisionar
un servidor, pero es un servicio de pago de terceros — misma decisión de gasto, forma
distinta. Evaluar cuando el owner decida.

---

## 1. Qué es Openship y por qué este diseño

[Openship](https://github.com/oblien/openship) (Apache-2.0, self-hosted) apunta a un repo,
detecta o usa un `openship.json`, construye, ejecuta en contenedores (nunca puerto público
directo) y un edge OpenResty enruta + emite TLS Let's Encrypt. Push-to-deploy por webhook de
GitHub en cada push a la rama trackeada.

`openship.json` soporta dos modos mutuamente excluyentes (verificado leyendo
`apps/api/src/modules/deployments/prepare.service.ts` del propio código de Openship):
declarar `services` (estilo docker-compose) **apaga globalmente** la autodetección de
framework/monorepo para ese proyecto. No hay punto intermedio.

**Decisión: modo `services` puro**, isomorfo al `docker-compose.yml` que Cardeep ya usa y
tiene probado en local — no una re-derivación. Alternativa descartada: modo "monorepo"
(autodetección nativa de `fastapi` + `vite`, confirmada que existe en Openship) porque no
tiene un concepto de sidecar para Postgres ni para un daemon sin puerto HTTP (`autopilot`)
sin apostar a comportamiento no verificado. El único coste de la opción elegida es que el
frontend pierde la autodetección/caché nativa de Vite — compensado con un `web/Dockerfile`
estándar (ver §3).

---

## 2. `openship.json` — los 4 servicios

Traducción 1:1 del `docker-compose.yml` raíz + un servicio `web` nuevo:

| Servicio | Origen | Expuesto | Notas |
|---|---|---|---|
| `cardeep-pg` | `image: postgres:16` (igual que compose) | No | Volumen nombrado `cardeep_pg_data`, healthcheck `pg_isready` |
| `api` | `build: .` + `Dockerfile` raíz (el mismo ya probado) | Sí | `uvicorn services.api.main:app`, puerto 8090, healthcheck `/health` |
| `autopilot` | Misma imagen que `api`, comando distinto | No | `python -m pipeline.ops.scheduler`, sin puerto HTTP → sin healthcheck |
| `web` | `build: web` + `web/Dockerfile` (nuevo, ver §3) | Sí | SPA estática detrás de nginx |

Todos `restart: unless-stopped`, `api`/`autopilot` con `dependsOn: cardeep-pg`. Las
credenciales usan el mismo placeholder no-secreto `cardeep_dev_only` que el resto del repo
(allowlisted en `.gitleaks.toml`) — **no son secretos reales**, y están marcadas
`secret: true` en el JSON para que Openship las cifre en reposo de todos modos.

⚠️ **Antes del primer deploy público real**, sustituir `cardeep_dev_only` por una contraseña
fuerte vía el dashboard de Openship (o su editor de env por servicio) — el placeholder es
válido para levantar y probar, no para producción expuesta.

**`domain: "deepcar.duckdns.org"` en `web`** — dominio real, ya resuelto (§0). `api` queda
sin `domain` a propósito: el diseño same-origin (§3) la sirve a través del proxy de `web` en
`/api/*` y `/api/v1/*`, así que no necesita su propio hostname público. Si el owner quisiera
más adelante el API en un subdominio independiente (p. ej. un segundo hostname DuckDNS), se
añade directo en el JSON.

⚠️ **`ports` es obligatorio en todo servicio `exposed: true`, no cosmético.** Verificado
leyendo el código real de Openship (`apps/api/src/lib/public-endpoints.ts::resolveServicePublicEndpoints`
+ `deployable-service.ts::resolveServicePort`): en modo `services`, si un servicio no declara
`ports` ni `exposedPort`, `resolveServicePort` devuelve `null` y Openship genera **cero
endpoints públicos para ese servicio — sin error, sin log de aviso, deploy "exitoso" y sitio
100% inalcanzable.** Primera versión de este archivo lo omitía en `api`/`web`; corregido
(`"ports": ["8090"]` en `api`, `"ports": ["80"]` en `web`) tras una revisión de código que
leyó el pipeline de routing real, no solo el schema de forma.

---

## 3. `web/Dockerfile` — build verificado localmente

Build multi-stage: `node:22-alpine` (misma versión que `frontend-build` en CI —
`npm ci && npm run build`) → `nginx:1.27-alpine`
sirviendo `dist/` con fallback SPA. `web/.dockerignore` nuevo excluye `node_modules`/`dist`
locales del contexto (si no, `COPY . .` pisaría el `npm ci` de Linux con binarios de Windows).

**Same-origin por defecto, cero CORS, cero dominio necesario para arrancar:**
`VITE_API_BASE=/api` se hornea en el build (Vite inlinea sus env vars en tiempo de build, no
runtime). `web/nginx.conf` nuevo reverse-proxea:

- `/api/v1/*` → `api:8090` (prefijo recortado) — replica **exactamente** el proxy que
  `web/vite.config.ts` ya usa en dev para `web/src/api/client.ts` (auth/CRM/dealer_ops).
- `/api/*` → `api:8090` (prefijo recortado) — para `web/src/api/cardeep.ts`
  (`VITE_API_BASE`), que hoy apunta a `http://127.0.0.1:8090` en dev.
- todo lo demás → `index.html` (rutas de `react-router-dom`).

Si el owner prefiere el API en su propio subdominio (`api.<dominio>`) en vez de mismo-origen,
reconstruir con `docker build --build-arg VITE_API_BASE=https://api.<dominio> web/` — ambas
formas conviven con el mismo `nginx.conf`; es una elección del owner, no decidida aquí.

**Verificado en vivo (2026-07-25, local, `docker build` + `docker run` real, no solo lectura
de código):**
- Build completo con `node:22-alpine`: `npm ci` (421 paquetes) + `tsc --noEmit && vite build`
  → `dist/` generado, imagen exportada sin error.
- **Bug real cazado y corregido**: `nginx.conf` con `proxy_pass http://api:8090;` literal
  hace que nginx **rehúse arrancar** (`host not found in upstream "api"`) si el hostname
  `api` no resuelve en el instante de cargar la config — probado standalone, sin el
  contenedor `api` presente. Fix aplicado: `resolver 127.0.0.11 valid=10s;` (DNS embebido de
  Docker) + `proxy_pass` vía variable (`set $api_upstream api:8090;`), que fuerza resolución
  DNS por-petición en vez de al arrancar. Sin este fix, cualquier reinicio del servicio `api`
  se habría llevado por delante todo el frontend.
- Contenedor `web` corriendo standalone (sin `api` real): `GET /` → `200` (index.html real,
  no placeholder), `GET /dashboard/whatever` → `200` (fallback SPA), `GET /api/stats` y
  `GET /api/v1/auth/me` → `502` limpio (el proxy lo intenta y falla al no haber backend —
  degradación correcta, no crash de nginx).
- **No verificable sin servidor real** (queda en §4): que el hostname `api` efectivamente
  resuelva dentro de la red que Openship gestiona en modo `services` — el resolver
  `127.0.0.11` es el DNS embebido estándar de Docker en redes bridge definidas por el
  usuario, que es como docker-compose (y se asume, no confirmado, Openship) monta sus redes.
- **Segundo bug real cazado por code review (no por las pruebas curl anteriores) y
  corregido**: `web/src/api/cardeep.ts` construye cada petición con `new URL(BASE + path)`,
  que **exige una URL absoluta** — con `VITE_API_BASE=/api` (el default de este
  `Dockerfile`), `new URL('/api' + '/stats')` lanza `TypeError: Invalid URL` en cualquier
  motor (Node/navegador, reproducido). Las pruebas `curl` a rutas fijas de nginx no lo
  detectaron porque nunca ejecutan el bundle JS real; hacía falta leer el código consumidor,
  no solo probar el servidor. Rompía prácticamente toda la capa de datos del producto
  (stats, mapa, entidades, arbitraje, terminal — todo lo que pasa por `getData`/`getPaged`/
  `getPagedWithMeta`). Fix de raíz (no un parche en el Dockerfile): `cardeep.ts` ahora
  resuelve una `BASE` relativa contra `window.location.origin` antes de usarla, así que
  `new URL(...)` recibe siempre una URL absoluta — cero cambios en las ~30 funciones
  consumidoras. Re-verificado: `tsc --noEmit` limpio, simulación directa de la nueva lógica
  sin excepción, rebuild Docker completo + contenedor corriendo con el mismo resultado
  `200`/`200`/`502` de antes (el fix no cambió el comportamiento HTTP observable desde
  fuera, corrige lo que pasa DENTRO del navegador al construir la URL).

---

## 4. Checklist de verificación en el primer deploy real

Cosas que **no se pueden verificar sin servidor** — quedan como lista explícita, no como
supuestos silenciosos (ninguna está "asumida como buena", todas están marcadas pendiente):

- [ ] **DNS interno de servicios**: `api:8090` y `cardeep-pg:5432` como hostname asumen que
      Openship en modo `services` resuelve por nombre de servicio igual que docker-compose
      nativo. **Parcialmente mitigado** (§3): `web/nginx.conf` ya no puede tumbar el
      contenedor entero si la resolución falla o llega tarde (degrada a 502 por-petición, no
      crash). Sigue pendiente confirmar que "api" resuelve de verdad en la red real de
      Openship — verificar con logs del primer build/run.
- [ ] **Routing por dominio en modo `services`**: los campos `exposed`/`domain` existen por
      servicio en el schema — confirmar que el edge OpenResty realmente enruta cada dominio
      al servicio correcto (no solo verificado a nivel de schema).
- [ ] **Persistencia del volumen `cardeep_pg_data` entre redeploys** (push-to-deploy):
      confirmar que no se recrea vacío en cada push. Hasta confirmar, tratar cada redeploy
      como potencialmente destructivo — dump de respaldo antes del primer push real.
- [ ] **`api` y `autopilot` con el mismo `build:"."`**: confirmar si Openship deduplica la
      imagen o construye dos veces (solo afecta coste de build, no correctitud).
- [ ] **`CARDEEP_OLLAMA_URL=http://host.docker.internal:11434/...`**: en local apunta al
      Ollama del host Windows. En un VPS nuevo **no habrá Ollama ahí** — instalar Ollama en
      el VPS o apuntar la env var a una instancia alcanzable. No resuelto por este documento
      a propósito: depende de dónde decida el owner correr el LLM local en producción.
- [ ] Sustituir el placeholder `cardeep_dev_only` por una contraseña real (§2).
- [ ] **`dependsOn` no espera a que `cardeep-pg` esté healthy, solo fija orden de arranque**
      (verificado leyendo `deploy-pipeline.ts` de Openship: el `healthCheck` del pipeline de
      deploy es un seam declarado sin implementar — "no runtime implements this yet"; en modo
      `services` nunca se asigna). `services/api/main.py` crea el pool de `asyncpg` sin retry
      propio. Riesgo: en el primer deploy o un redeploy completo, si Postgres tarda en aceptar
      conexiones, `api`/`autopilot` pueden morir y reiniciar 1-2 veces antes de estabilizar
      (`restart: unless-stopped` los recupera solos — no es downtime permanente, sí ruido no
      documentado). Fuera del alcance de esta integración añadir retry/backoff en
      `services/api/main.py` (toca arranque del backend, no solo el empaquetado de deploy) —
      queda anotado para que el owner decida si lo quiere antes del primer deploy real.

## 5. Comandos, en cuanto exista el VPS

Dominio ya resuelto (§0): `deepcar.duckdns.org`. Antes de `openship up`, re-apuntar el A
record a la IP real del VPS (mismo comando probado en §0, solo cambia el valor de `ip`):

```bash
curl -s "https://www.duckdns.org/update?domains=deepcar&token=<token en ~/.cardeep-ops-secrets/duckdns.env>&ip=<IP pública del VPS>"
```

```bash
# En el VPS (Linux + Docker), con el DNS ya apuntando ahí:
curl -fsSL https://get.openship.io | sh
openship up --public-url https://deepcar.duckdns.org

# Desde una máquina con el repo (puede ser esta misma):
cd Cardeep
openship init         # enlaza este directorio al proyecto (crea .openship/project.json)
openship deploy        # primer build+run+route de los 4 servicios
```

A partir de ahí, cada `git push` a `main` re-despliega vía webhook (una vez configurado en
el dashboard de Openship).
