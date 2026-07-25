# DEPLOY del frontend en Vercel — vivo desde 2026-07-25

> **Estado: EN PRODUCCIÓN.** https://cardeep.vercel.app
>
> Este doc cubre el frontend (`web/`) desplegado en Vercel, que es lo que está
> **público y funcionando hoy**. El backend (API + Postgres + `autopilot`) NO vive aquí —
> ver [DEPLOY_OPENSHIP.md](DEPLOY_OPENSHIP.md) para la ruta autoalojada completa, pendiente
> de que Oracle libere capacidad ARM.

---

## 0. Por qué dos rutas y por qué no se pisan

Vercel **no puede** correr Cardeep entero, verificado contra sus límites reales (2026):

| Pieza | Vercel Free | Veredicto |
|---|---|---|
| Frontend Vite/React estático | Sí, con CDN + TLS + push-to-deploy | ✅ vive aquí |
| API FastAPI | Solo funciones serverless, 10s máx. de ejecución | ❌ |
| Daemon `autopilot` (APScheduler, siempre encendido) | Imposible por arquitectura: sin proceso persistente | ❌ |
| Postgres 10GB | Supabase Free da 500MB (20x por debajo) | ❌ |

Así que el reparto es: **Vercel sirve el frontend, Openship/Oracle servirá el backend.**

**Lo que hace que trasladarlo sea trivial** (requisito explícito del owner): las dos rutas usan
la MISMA arquitectura de origen único. El frontend siempre llama a `/api/*` en su propio
dominio; lo único que cambia es quién hace de proxy hacia la API:

- En Openship/Oracle → `web/nginx.conf` (`proxy_pass` a `api:8090`)
- En Vercel → un `rewrite` en `web/vercel.json`

`VITE_API_BASE=/api` se hornea en tiempo de build en ambos casos, así que **apuntar el
frontend al backend cuando exista es añadir una regla de rewrite — no un rebuild, ni un
cambio de código, ni tocar el bundle.**

---

## 1. Configuración (`web/vercel.json`)

Preset Vite, `npm ci` + `npm run build` → `dist/`, fallback SPA para `react-router-dom`, y
cuatro cabeceras de seguridad (`X-Content-Type-Options`, `X-Frame-Options`,
`Referrer-Policy`, `Strict-Transport-Security`) — las cuatro verificadas en vivo con `curl -I`
contra el dominio ya desplegado.

⚠️ **El schema de Vercel es draft-04 y `rewrites` es `additionalProperties: false`.** Una
clave `comment` explicativa dentro de un rewrite **hace que Vercel rechace el archivo**. Se
detectó validando contra el schema oficial antes de desplegar, no en el deploy. Para validar
cambios futuros hace falta un validador draft-04 real (`jsonschema.Draft4Validator` en
Python); `ajv-cli` sin el paquete draft-04 falla con "no schema with key or ref draft-04".

## 2. Ajustes del proyecto que NO están en `vercel.json`

Dos cosas son ajustes de proyecto (viven en Vercel, no en el repo) y **si se pierden, los
builds por push fallan en silencio**:

- **Root Directory = `web`** — obligatorio. Por defecto queda en `.` (raíz del repo), que es
  el proyecto Python sin `package.json`: todo build disparado por git fallaría. Se fijó vía
  API (`PATCH /v9/projects/{id}` con `{"rootDirectory": "web"}`).
- **Repo de git conectado** — `sublimine/Cardeep`, vía
  `vercel git connect https://github.com/sublimine/Cardeep.git` (hay que pasar la URL
  explícita: ejecutado desde `web/` el CLI no encuentra el `.git`, que está en la raíz).

## 3. ⚠️ Trampa del email de git — bloquea el deploy sin construir nada

El plan Hobby de Vercel verifica que el email del **committer** esté asociado a una cuenta de
GitHub. Este repo tenía `user.email = elias@cardeep.local` (dominio inventado, no verificable)
— con eso Vercel **bloquea el deploy y ni siquiera arranca el build**, con un error genérico
sobre colaboración de proyecto (`Builds: . [0ms]`).

Ya fijado en el repo local: `git config --local user.email srkarrouch@gmail.com`.

**Si un deploy aparece en ERROR sin logs de build, esto es lo primero que hay que mirar** —
no la config de build. Es un fallo de atribución del committer, no del código.

## 4. Cuando el backend exista — conectar frontend con API

Añadir los rewrites ANTES del catch-all de SPA (el orden importa: gana la primera coincidencia)
en `web/vercel.json`:

```json
"rewrites": [
  { "source": "/api/v1/:path*", "destination": "https://<backend>/:path*" },
  { "source": "/api/:path*",    "destination": "https://<backend>/:path*" },
  { "source": "/(.*)",          "destination": "/index.html" }
]
```

Commit + push y listo — el frontend ya está construido para hablar con `/api/*`.

Alternativa si se prefiere el backend en su propio subdominio en vez de proxy: reconstruir con
`VITE_API_BASE=https://api.<dominio>` (y entonces habría que habilitar CORS en FastAPI, que
hoy no hace falta porque todo es mismo-origen).

## 5. Comportamiento actual sin backend (verificado en navegador real)

La landing renderiza **completa**: hero, marketplace, dashboard del dealer, inteligencia de
mercado, cobertura, footer. Lo único que no aparece son los **números de estadísticas en
vivo**, que muestran su placeholder de carga porque `/api/*` no tiene backend detrás.

Ese fallo es limpio y está manejado: el catch-all de SPA devuelve `index.html` para `/api/*`,
`web/src/api/cardeep.ts` intenta `res.json()`, falla, y lanza un `CardeepApiError`
("non-JSON response") que la UI trata como estado de error/carga. No hay pantalla en blanco
ni excepción sin capturar.

> Nota al margen, decisión de copy pendiente del owner: `web/index.html` declara
> `<title>CARDEEP Workspace</title>` y `description="CARDEEP Workspace — Dealer CRM Dashboard"`.
> Para una landing pública eso describe una herramienta interna, no el producto. No se cambió
> porque es criterio de marca, no un bug.

## 6. Operación

```bash
# Deploy manual a producción (desde web/):
vercel deploy --prod --scope habanalegacy-2390s-projects

# Ver ajustes del proyecto (incluido Root Directory):
vercel project inspect cardeep --scope habanalegacy-2390s-projects

# Push-to-deploy: automático en cada push a `main` (repo conectado, §2).
```
