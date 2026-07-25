# DEPLOY vía Openship — de local a servidor público

> Este doc cubre el despliegue **público** (servidor real, dominio, TLS, push-to-deploy).
> El [DEPLOY.md](DEPLOY.md) hermano cubre el bring-up **local** (€0, sin servidor) — sigue
> siendo el camino recomendado para desarrollo. Este doc es el siguiente paso, cuando el
> owner decida hacer Cardeep públicamente accesible.
>
> **Estado (2026-07-25): dominio resuelto, servidor en aprovisionamiento.** `openship.json`
> (raíz del repo) y `web/Dockerfile` están escritos, validados contra el JSON Schema oficial
> de Openship, con el build de `web/` verificado localmente (§3) y una auditoría adversarial
> completa (§4-§7 incorporan sus hallazgos, todos corregidos). Dominio decidido y verificado
> en vivo: **`deepcar.duckdns.org`**. Servidor: Oracle Cloud Always Free, Ampere A1 (ARM),
> **región eu-zurich-1** — ver §0 para por qué no es Frankfurt.

---

## 0. Bloqueante — decisión del owner, no ejecutable por IA

Openship es una plataforma de despliegue **autoalojada** (self-hosted): el "control plane"
puede correr localmente o en la nube de Openship, pero para que Cardeep quede **públicamente
accesible** —con push-to-deploy, TLS y dominio propio— hace falta:

1. Un **servidor Linux con Docker** (VPS) — Openship necesita host networking en Linux para
   su edge (`:80`/`:443`). **Decisión tomada, en aprovisionamiento**: Oracle Cloud Always
   Free, shape Ampere A1 (ARM, 2 OCPU/12GB RAM — Oracle recortó la cuota Always Free a la
   mitad en junio-2026 sin aviso, antes eran 4 OCPU/24GB). **Región: eu-zurich-1** (Switzerland
   North), NO Frankfurt — la home region de una tenancy OCI queda fijada permanentemente al
   crear la cuenta y Always Free solo se puede aprovisionar ahí (verificado contra
   `docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm`:
   "You must create the Always Free compute instances in your home region" — suscribirse a
   otra región da acceso de consola pero factura normal, no cuenta como Always Free).
   VCN/subnet/gateway/firewall ya creados vía API (OCID en el estado de sesión). Zúrich
   reportó capacidad ARM agotada de forma sostenida durante el aprovisionamiento — un proceso
   de reintento paciente (backoff ~90-150s, hasta ~14h) corre desacoplado de esta sesión.
2. Un **dominio** con su DNS apuntando a ese servidor — Openship exige el registro DNS
   *antes* de instalar. **RESUELTO 2026-07-25**: `deepcar.duckdns.org` (DuckDNS, cuenta
   `sublimine@github`, €0). Verificado en vivo: resuelve vía DNS público (`nslookup` contra
   8.8.8.8) y el mecanismo de actualización probado responde `OK`. Token guardado FUERA del
   repo en `~/.cardeep-ops-secrets/duckdns.env` (permisos 600) — Cardeep es repo público,
   nunca se commitea.

El VPS implica **gasto potencial** (el Ampere A1 es €0 dentro de cuota, pero hay ambigüedad
no resuelta sobre facturación del excedente tras el recorte de junio-2026 — detalle en
PROGRESO.md; mitigado usando exactamente 2 OCPU/12GB, la cuota documentada actual, nunca
4/24) y **exposición externa**. Por doctrina del proyecto esto exige orden literal del
owner — **recibida** (autorización explícita a implementar todo A→Z, incluyendo ejecución
directa con las credenciales Oracle que el owner entregó).

**Alternativa sin VPS propio:** Openship Cloud (`openship.io`, gestionado) evita provisionar
un servidor, pero es un servicio de pago de terceros — misma decisión de gasto, forma
distinta. No usada.

---

## 1. Qué es Openship y por qué este diseño

[Openship](https://github.com/oblien/openship) (Apache-2.0, self-hosted) apunta a un repo,
detecta o usa un `openship.json`, construye, ejecuta en contenedores (nunca puerto público
directo) y un edge OpenResty enruta + emite TLS Let's Encrypt. Push-to-deploy por webhook de
GitHub en cada push a la rama trackeada (mecánica completa: §7).

`openship.json` soporta dos modos mutuamente excluyentes (verificado leyendo
`apps/api/src/modules/deployments/prepare.service.ts` del propio código de Openship):
declarar `services` (estilo docker-compose) **apaga globalmente** la autodetección de
framework/monorepo para ese proyecto. No hay punto intermedio, y por tanto **Cardeep es UN
solo proyecto Openship** (no 4) que despliega 4 contenedores — relevante en §7, donde solo
hace falta vincular GitHub una vez, no por servicio.

**Decisión: modo `services` puro**, isomorfo al `docker-compose.yml` que Cardeep ya usa y
tiene probado en local — no una re-derivación. Alternativa descartada: modo "monorepo"
(autodetección nativa de `fastapi` + `vite`, confirmada que existe en Openship) porque no
tiene un concepto de sidecar para Postgres ni para un daemon sin puerto HTTP (`autopilot`)
sin apostar a comportamiento no verificado. El único coste de la opción elegida es que el
frontend pierde la autodetección/caché nativa de Vite — compensado con un `web/Dockerfile`
estándar (§3).

---

## 2. `openship.json` — los 4 servicios

Traducción 1:1 del `docker-compose.yml` raíz + un servicio `web` nuevo:

| Servicio | Origen | Expuesto | Notas |
|---|---|---|---|
| `cardeep-pg` | `image: postgres:16` (igual que compose) | No | Volumen nombrado `cardeep_pg_data`, healthcheck `pg_isready` |
| `api` | `build: .` + `Dockerfile` raíz (el mismo ya probado) | Sí (`ports: ["8090"]`) | `migrate.py up && uvicorn`, healthcheck `/health` |
| `autopilot` | Misma imagen que `api`, comando distinto | No | `python -m pipeline.ops.scheduler`, sin puerto HTTP → sin healthcheck |
| `web` | `build: web` + `web/Dockerfile` (§3) | Sí (`ports: ["80"]`, `domain: "deepcar.duckdns.org"`) | SPA estática detrás de nginx |

Todos `restart: unless-stopped`, `api`/`autopilot` con `dependsOn: cardeep-pg`,
`CARDEEP_ENV: "prod"` (activa los guards de fail-fast del propio código — ver §4).

### Secretos: NUNCA en `openship.json` — este repo es público

Las credenciales en el archivo **commiteado** son el placeholder no-secreto
`cardeep_dev_only` (mismo patrón ya establecido y allowlisted en `.gitleaks.toml`,
`docker-compose.yml`, `.github/workflows/ci.yml`) — **intencional**, no un descuido.

Verificado leyendo el merge de env real de Openship
(`apps/api/src/modules/deployments/compose/deploy.service.ts:788-796`, comentario propio del
código: *"Merge: shared project env → current deploy shared env → service env. Service
values intentionally win..."*): el `env` de `openship.json` (capa 3) **pisa** las variables
de proyecto puestas vía `openship project env set` (capa 1) — así que esa vía NO sirve para
sobreescribir un secreto que también vive en el JSON commiteado. La ÚNICA capa que gana sobre
lo que hay en git es el env **con scope de servicio** (capa 4, `openship service env set`).
Y `openship.json` no es una plantilla de una sola vez: se re-lee en cada build/deploy real
(`reconcileComposeDrift`, `build.service.ts:426-457`) y sobreescribe `service.environment` en
cada redeploy salvo que el servicio haya "driftado" — por eso el placeholder committeado
importa tanto como el valor real puesto después.

**Antes de que `cardeep-pg` arranque por primera vez** (Postgres solo aplica
`POSTGRES_PASSWORD` al *initdb* de un data dir vacío — cambiarlo después NO cambia la
contraseña ya inicializada), fijar los secretos reales con scope de servicio:

```bash
openship service env set cardeep-pg --secret \
  POSTGRES_PASSWORD='<valor real, ver ~/.cardeep-ops-secrets/production.env>'

openship service env set api --secret \
  CARDEEP_DSN='postgresql://cardeep:<password-real>@cardeep-pg:5432/cardeep' \
  CARDEEP_ASYNCPG_DSN='postgresql://cardeep:<password-real>@cardeep-pg:5432/cardeep' \
  CARDEEP_DB_URL='postgresql+psycopg2://cardeep:<password-real>@cardeep-pg:5432/cardeep' \
  CARDEEP_API_KEY='<valor real, ver production.env>'

openship service env set autopilot --secret \
  CARDEEP_DSN='postgresql://cardeep:<password-real>@cardeep-pg:5432/cardeep' \
  CARDEEP_ASYNCPG_DSN='postgresql://cardeep:<password-real>@cardeep-pg:5432/cardeep' \
  CARDEEP_DB_URL='postgresql+psycopg2://cardeep:<password-real>@cardeep-pg:5432/cardeep'
```

Los valores reales (generados 2026-07-25, aleatorios, nunca en git) están en
`~/.cardeep-ops-secrets/production.env` en la máquina que ejecutó este despliegue.

**`domain: "deepcar.duckdns.org"` en `web`** — dominio real, ya resuelto (§0). `api` queda
sin `domain` a propósito: el diseño same-origin (§3) la sirve a través del proxy de `web` en
`/api/*` y `/api/v1/*`, así que no necesita su propio hostname público.

⚠️ **`ports` es obligatorio en todo servicio `exposed: true`, no cosmético.** Verificado
leyendo el código real de Openship (`apps/api/src/lib/public-endpoints.ts::resolveServicePublicEndpoints`
+ `deployable-service.ts::resolveServicePort`): en modo `services`, si un servicio no declara
`ports` ni `exposedPort`, `resolveServicePort` devuelve `null` y Openship genera **cero
endpoints públicos para ese servicio — sin error, sin log de aviso, deploy "exitoso" y sitio
100% inalcanzable.**

---

## 3. `web/Dockerfile` — build verificado localmente

Build multi-stage: `node:22-alpine` (misma versión que `frontend-build` en CI —
`npm ci && npm run build`) → `nginx:1.27-alpine` sirviendo `dist/` con fallback SPA.
`web/.dockerignore` excluye `node_modules`/`dist` locales del contexto (si no, `COPY . .`
pisaría el `npm ci` de Linux con binarios de Windows).

**Same-origin por defecto, cero CORS, cero dominio necesario para arrancar:**
`VITE_API_BASE=/api` se hornea en el build (Vite inlinea sus env vars en tiempo de build, no
runtime). `web/nginx.conf` reverse-proxea `/api/v1/*` y `/api/*` → `api:8090` (prefijo
recortado), replicando exactamente el proxy que `web/vite.config.ts` ya usa en dev; todo lo
demás → `index.html` (rutas de `react-router-dom`).

**Verificado en vivo (2026-07-25, `docker build` + `docker run` real, no solo lectura de
código) — 2 bugs reales cazados y corregidos:**

1. `nginx.conf` con `proxy_pass http://api:8090;` literal hacía que nginx **rehusara
   arrancar** (`host not found in upstream`) si "api" no resolvía al cargar la config —
   probado standalone sin el contenedor `api` presente. Fix: `resolver 127.0.0.11 valid=10s;`
   + `proxy_pass` por variable → resolución DNS por-petición, degrada a 502 en vez de crash.
2. `web/src/api/cardeep.ts` construye cada petición con `new URL(BASE + path)`, que exige
   URL absoluta — con `VITE_API_BASE=/api` (relativo) lanzaba `TypeError: Invalid URL` en
   cualquier navegador real (reproducido). Rompía casi toda la capa de datos (stats, mapa,
   entidades, arbitraje, terminal). Fix de raíz: `cardeep.ts` resuelve `BASE` contra
   `window.location.origin` antes de usarla — cero cambios en las ~30 funciones consumidoras.
   `web/src/api/client.ts` (el otro cliente, auth/CRM) nunca tuvo este bug: usa
   `fetch('/api/v1'+path)` con string relativo, sin pasar por `new URL()`.

Contenedor `web` standalone (sin `api` real): `GET /` → `200` (index.html real),
`GET /dashboard/whatever` → `200` (fallback SPA), `GET /api/*` → `502` limpio (proxy
funcionando, backend ausente, sin crash). `tsc --noEmit` limpio tras el fix de `cardeep.ts`.

---

## 4. Migraciones — deben correr contra el Postgres del VPS, nadie más lo hace

**Hallazgo crítico de la auditoría 2026-07-25**: ningún paso del despliegue original corría
`scripts/migrate.py up` contra el `cardeep-pg` nuevo. El volumen se crea vacío; `/health`
(`services/api/routers/ops.py`) solo hace `SELECT 1` — no toca ninguna tabla de la app — así
que reportaría "ok" mientras el resto de la API devuelve 500 por esquema inexistente.

**Fix aplicado en `openship.json`**: el `command` de `api` encadena la migración antes de
arrancar uvicorn: `sh -c "python scripts/migrate.py up && uvicorn services.api.main:app ..."`
— aplica los 96 archivos de `migrations/` (idempotente, ya verificado así en CI) en cada
arranque del contenedor, no solo el primero. `autopilot` NO repite la migración (evita una
carrera de dos procesos migrando a la vez); si arranca antes de que `api` termine de migrar,
sus queries fallarán y `restart: unless-stopped` lo reintentará hasta que el esquema exista —
mismo patrón ya aceptado para la carrera de arranque con Postgres (ver §6).

**`CARDEEP_ENV=prod`** (ya en `openship.json`, §2) activa el fail-fast real del código
(`pipeline/config_guard.py::assert_safe_dsn`): si el DSN todavía contiene el marcador
`cardeep_dev_only` con `CARDEEP_ENV=prod`, el proceso **rehúsa arrancar** — por diseño, no es
un bug. Por eso §2 exige fijar los secretos reales por servicio ANTES del primer `deploy`
exitoso: si se despliega con el placeholder y `CARDEEP_ENV=prod` a la vez, `api`/`autopilot`
crash-loopearán hasta que se corrijan los secretos — comportamiento correcto y esperado, no
un fallo del despliegue.

---

## 5. Migración de los datos reales (10GB / ~2,3M+ filas)

El runbook original no tenía procedimiento de migración de datos, solo una nota defensiva
sobre backups pre-push. Aparte:

**Paso 1 — dump local** (ya probado en vivo 2026-07-25: 813MB comprimido desde 10GB, 2m12s):

```bash
# Desde esta máquina, una vez el VPS tenga IP:
bash ops/openship/migrate_db_step1_dump.sh <IP-publica-del-VPS>
# (dump local + scp a /home/ubuntu/cardeep_migration.dump en el VPS)
```

**Paso 2 — restaurar dentro del contenedor `cardeep-pg` real.** El nombre exacto del
contenedor que Openship asigna en modo `services` **no está confirmado** hasta el primer
deploy — descúbrelo antes de escribir el comando final:

```bash
ssh -i cardeep_vm_key ubuntu@<IP> 'sudo docker ps --filter name=cardeep-pg --format "{{.Names}}"'
```

```bash
# En el VPS, con el nombre real del contenedor:
ssh -i cardeep_vm_key ubuntu@<IP> '
  sudo docker cp /home/ubuntu/cardeep_migration.dump <contenedor-real>:/tmp/restore.dump &&
  sudo docker exec <contenedor-real> pg_restore -U cardeep -d cardeep --clean --if-exists /tmp/restore.dump &&
  sudo docker exec <contenedor-real> rm /tmp/restore.dump
'
```

Ejecutar esto **después** de que `api` haya corrido las migraciones (§4) — `pg_restore
--clean --if-exists` reemplaza los datos de las tablas ya migradas, no requiere un esquema
vacío. Verificar tras restaurar: `SELECT count(*) FROM vehicle;` u otra tabla grande, y
comparar contra el conteo local conocido.

---

## 6. Checklist de verificación en el primer deploy real

- [ ] **DNS interno de servicios** (`api:8090`, `cardeep-pg:5432`): **verificado
      favorablemente por lectura de código** (`packages/adapters/src/runtime/docker.ts`,
      `ensureNetwork`/`reconcileNetworkMembership` conecta cada contenedor a la red del
      proyecto con `Aliases: [service.name]`) — confirmar con logs del primer build/run de
      todos modos, es el único nivel de certeza real.
- [ ] **Routing por dominio en modo `services`**: confirmar que el edge OpenResty enruta
      `deepcar.duckdns.org` → `web` correctamente (no solo verificado a nivel de schema).
- [ ] **Persistencia del volumen `cardeep_pg_data` entre redeploys** (push-to-deploy):
      confirmar que no se recrea vacío en cada push. Dump de respaldo antes de cada push que
      toque el esquema, hasta confirmar.
- [ ] **`api` y `autopilot` con el mismo `build:"."`**: confirmar si Openship deduplica la
      imagen o construye dos veces (solo coste de build, no correctitud).
- [ ] **`CARDEEP_OLLAMA_URL=http://127.0.0.1:11434/...`**: Ollama NO se instala por este
      bootstrap (recurso limitado en el free tier — 12GB RAM compartidos con Postgres+API+
      autopilot+web). **No bloqueante**: verificado leyendo `pipeline/recipe_cracker.py` +
      `pipeline/ops/scheduler.py` que ninguna llamada a Ollama ocurre en el arranque del
      proceso — solo en rutas de trabajo específicas (recipe cracking), envueltas en
      try/except que degradan sin tumbar el servicio. Instalar Ollama en el VPS es una
      decisión de capacidad aparte, no del owner todavía.
- [ ] **`dependsOn` no espera a que `cardeep-pg` esté healthy, solo fija orden de arranque**
      (verificado: el `healthCheck` del pipeline de deploy de Openship es un seam declarado
      sin implementar). Mitigado por `restart: unless-stopped` — ruido de arranque esperado,
      no downtime permanente.
- [ ] **ufw en imágenes Oracle Cloud**: reportes de la comunidad (incl. un empleado de
      Oracle) describen comportamiento poco fiable de ufw específicamente en OCI. Verificar
      `curl` externo (no localhost) a `:80`/`:443` tras el bootstrap; plan B documentado en
      `ops/openship/vm_bootstrap_phase2.sh`: firewalld.
- [ ] **Push-to-deploy real**: hacer un commit trivial + push a `main`, cronometrar hasta que
      `deepcar.duckdns.org` refleje el cambio, confirmar que ocurrió SIN ejecutar
      `openship deploy` a mano. Procedimiento completo: §7.

---

## 7. Push-to-deploy — mecánica real, verificada leyendo el código de Openship

Investigado a fondo 2026-07-25 (no estaba documentado antes — hallazgo CRITICAL de la
auditoría). Resumen de la mecánica real (self-hosted, `CLOUD_MODE=false`, sin conectar a
Openship Cloud):

- **NO requiere GitHub App.** `GITHUB_APP_SLUG=openship-io` solo aplica en modo
  `CLOUD_MODE=true` o si el operador corre su propia App. Self-hosted usa la estrategia
  `"repo"`: Openship registra el webhook directamente vía la API REST de GitHub
  (`POST /repos/:owner/:repo/hooks`) usando la credencial disponible.
- La imagen Docker oficial de la API **no trae el binario `gh`** — la única vía práctica en
  un VPS headless es un **Personal Access Token clásico** de GitHub.
- El webhook, una vez registrado, apunta a `https://deepcar.duckdns.org/api/proxy/api/webhooks/github`
  (el segmento `/api/proxy/*` es obligatorio — el proxy same-origin del dashboard hacia la
  API interna). No hace falta fijar `GITHUB_WEBHOOK_SECRET`: Openship genera y sube un
  secreto aleatorio por proyecto automáticamente.
- Cardeep es **un solo proyecto** Openship (modo `services`, §1) — el link de git y el
  webhook se configuran **una sola vez**, no por cada uno de los 4 servicios.

**Pasos, en orden, una vez el proyecto esté desplegado:**

```bash
# 1. Confirmar que OPENSHIP_PUBLIC_URL quedó fijado (ya lo hace `openship up --public-url`
#    en el bootstrap, §0/ops/openship/vm_bootstrap_phase2.sh) — sin esto el registro de webhook se bloquea.
openship status

# 2. Generar en GitHub un PAT clásico, scope "repo" (Settings → Developer settings →
#    Personal access tokens → Tokens (classic)), sobre la cuenta con permisos de escritura
#    en sublimine/Cardeep.

# 3. Cargarlo como credencial global de Openship:
openship api -X PATCH /settings/clone-credentials -d '{"token":"ghp_XXXX","asDefault":true}'

# 4. Vincular el repo al proyecto (registra el webhook automáticamente):
openship project git link <project-id> --owner sublimine --repo Cardeep --branch main

# 5. Si el link ya existía sin auto-deploy activo, forzarlo:
openship project git auto-deploy <project-id> --enable

# 6. Verificar del lado GitHub: Settings → Webhooks del repo debe mostrar una entrada con
#    Payload URL https://deepcar.duckdns.org/api/proxy/api/webhooks/github, evento "push".

# 7. Verificar del lado Openship:
openship api GET /projects/<project-id>/git
# debe devolver webhook_active:true, webhook_strategy:"repo"

# 8. Prueba real: commit trivial + push a main, confirmar el redeploy automático:
openship deployment list
```

**No verificado, pendiente de comprobar en el primer push real**: qué pasa si el build
disparado por el webhook falla — si la versión anterior sigue sirviendo (deseable) o el
servicio cae. Añadido al checklist §6.

---

## 8. Comandos — secuencia completa una vez el VPS exista

El bootstrap está partido en **dos fases con un reinicio real de la VM entre medias** — no
es opcional saltárselo. Verificado contra el propio bundle instalado de Openship: el grupo
`docker` que `usermod -aG docker` añade en la Fase 1 no llega al manager `systemd --user`
bajo el que corre `openship up` (y por tanto el motor que despliega los 4 contenedores de
Cardeep) hasta que ese manager se recrea desde cero — una reconexión SSH normal NO lo
garantiza en Ubuntu 24.04, un reinicio completo sí.

```bash
# 1. Re-apuntar el dominio a la IP real (mismo mecanismo probado en §0):
curl -s "https://www.duckdns.org/update?domains=deepcar&token=<ver ~/.cardeep-ops-secrets/duckdns.env>&ip=<IP-VPS>"
# (el proceso de aprovisionamiento automatiza esto en cuanto consigue la instancia)

# 2. Fase 1: sistema, Docker, firewall, hardening SSH — termina en un `sudo reboot`.
ssh -i ~/.cardeep-ops-secrets/oci/cardeep_vm_key ubuntu@<IP-VPS> 'bash -s' \
  < ops/openship/vm_bootstrap_phase1.sh

# Esperar ~30-60s a que la VM reinicie, luego:

# 3. Fase 2 (SESIÓN SSH NUEVA, después del reinicio): Openship + admin + edge TLS.
ssh -i ~/.cardeep-ops-secrets/oci/cardeep_vm_key ubuntu@<IP-VPS> 'bash -s' -- \
  deepcar.duckdns.org eliaskarrouch10@gmail.com \
  "Elias" eliaskarrouch10@gmail.com "<OPENSHIP_ADMIN_PASSWORD de production.env>" \
  < ops/openship/vm_bootstrap_phase2.sh

# 4. Fijar secretos reales de Cardeep — OBLIGATORIO antes del primer deploy (§2). Postgres
#    solo aplica POSTGRES_PASSWORD al initdb de un volumen vacío: si se salta este paso y
#    cardeep-pg arranca con el placeholder del repo, la única recuperación es borrar el
#    volumen y volver a desplegar desde cero. Sustituir los valores por los reales de
#    ~/.cardeep-ops-secrets/production.env antes de ejecutar:
openship service env set cardeep-pg --secret \
  POSTGRES_PASSWORD='<CARDEEP_PROD_PG_PASSWORD real>'
openship service env set api --secret \
  CARDEEP_DSN='postgresql://cardeep:<CARDEEP_PROD_PG_PASSWORD real>@cardeep-pg:5432/cardeep' \
  CARDEEP_ASYNCPG_DSN='postgresql://cardeep:<CARDEEP_PROD_PG_PASSWORD real>@cardeep-pg:5432/cardeep' \
  CARDEEP_DB_URL='postgresql+psycopg2://cardeep:<CARDEEP_PROD_PG_PASSWORD real>@cardeep-pg:5432/cardeep' \
  CARDEEP_API_KEY='<CARDEEP_PROD_API_KEY real>'
openship service env set autopilot --secret \
  CARDEEP_DSN='postgresql://cardeep:<CARDEEP_PROD_PG_PASSWORD real>@cardeep-pg:5432/cardeep' \
  CARDEEP_ASYNCPG_DSN='postgresql://cardeep:<CARDEEP_PROD_PG_PASSWORD real>@cardeep-pg:5432/cardeep' \
  CARDEEP_DB_URL='postgresql+psycopg2://cardeep:<CARDEEP_PROD_PG_PASSWORD real>@cardeep-pg:5432/cardeep'

# 5. Autenticar la CLI (desde esta máquina) contra la instancia remota. El PAT se crea a
#    mano en el dashboard (https://deepcar.duckdns.org → login con el admin de la Fase 2 →
#    Settings → Personal Access Tokens) — es un paso de navegador de una sola vez, no
#    scriptable sin herramientas de browser automation:
openship login --token <PAT creado en el dashboard> --api-url https://deepcar.duckdns.org

# 6. Crear el proyecto CON el origen de GitHub ya fijado (así `deploy` construye desde el
#    repo real, no sube archivos locales — confirmado: `deploy --branch/--commit` defaults a
#    "current branch"/"latest commit", es decir opera sobre el git remoto, no un upload):
openship project create --name cardeep --git-owner sublimine --git-repo Cardeep \
  --git-branch main --type services

# 7. Enlazar ESTE directorio (el repo local, cualquier clon de Cardeep) al proyecto recién
#    creado, y disparar el primer deploy:
cd Cardeep   # el repo, con openship.json ya en la raíz
openship init --project <project-id del paso 6>
openship deploy --watch

# 8. Migrar los datos reales (§5).

# 9. Configurar push-to-deploy (§7) — el link de git ya existe desde el paso 6, falta el PAT
#    con permiso de webhooks (§7 paso 2-3) y activar auto-deploy.

# 10. Recorrer el checklist §6 punto por punto contra el deploy real.
```
