# AUTH-0 — esquema de autenticación único (00-MASTER.md §2 C-3)

> Workstream transversal, no pilar con carta propia. Fusión de lo que 4 cartas (03-F1,
> 05-F3, 06-F1-tenancy, 08-F1) planeaban construir por separado en una migración y un
> router. Ejecutado 2026-07-17/18, dentro de BLOQUE 1 (`plans/cardeep-omni/PROGRESO.md`).
> Doctrina de etiquetado: [VERIFICADO] = comprobado en esta sesión contra el sistema real
> (migración aplicada a cardeep-pg viva, tests ejecutados, curl real). [ASUMIDO] = decisión
> de diseño declarada como tal.

---

## 1. La colisión que resuelve

Cuatro cartas mintaban esquemas de auth incompatibles, tres de ellas numeradas `0073`:

| Carta | Qué planeaba | Destino en AUTH-0 |
|---|---|---|
| 08-forum-community F1 | `app_user` (roles dealer/particular/staff, argon2id, verificación de rol dealer vía `tax_id.py`) + `user_session` + `user_notification` | **Adoptado como base** — es el esquema más general de los cuatro |
| 03-garage-fleet F1 | `dealer_account` + `dealer_membership` (user↔entity N:M, multi-rooftop) | `dealer_membership` **adoptado tal cual** (relación con `app_user`, no con un `dealer_account` separado); `dealer_account` **descartado** — `app_user` ya cubre esa cuenta |
| 05-multiposting F3 | `0073_dealer_account.sql` (`dealer_account` + `dealer_user`) | **Descartado íntegro** — semántica de tenant duplicada de 08/03 |
| 06-unified-crm-chat F1-tenancy | `crm_tenant` + `crm_user` | **Descartado íntegro** — el MASTER resuelve: "el tenant ES la entity del dealer vía membership". No existe `crm_tenant` |

Resolución literal del MASTER (`00-MASTER.md` §2 C-3): *"Esquema base = el más general de los
cuatro: `app_user` de 08 ... + la relación multi-rooftop de 03 (`dealer_membership`) +
`user_session` revocable + `user_notification` de 08. `crm_tenant` de 06 desaparece: el
tenant ES la entity del dealer vía membership."*

Cada carta afectada (03-F1+, 04-F7, 05-F3+, 06-F1+, 08-F1+) **consume** este esquema en su
propia fase futura; ninguna vuelve a crear uno.

---

## 2. Esquema — `migrations/0073_auth.sql` [VERIFICADO aplicada a cardeep-pg :5433]

Número real consumido: **0073** (`ls migrations/*.sql | sort | tail -1` verificado
inmediatamente antes de crear el archivo → `0072_vehicle_cluster_country_proof.sql`, sin
huecos ni colisión con otros frentes del mismo Bloque 1 corriendo en paralelo).

```
app_user
  user_ulid       TEXT PK
  email           TEXT
  email_lower     TEXT GENERATED ALWAYS AS (lower(email)) STORED   -- unique index
  password_hash   TEXT        -- argon2id
  name            TEXT
  role            TEXT CHECK IN ('dealer','particular','staff')    -- default 'particular'
  status          TEXT CHECK IN ('active','disabled')
  created_at, updated_at

dealer_membership                    -- user <-> entity N:M (multi-rooftop, carta 03)
  user_ulid    FK app_user
  entity_ulid  FK entity              -- EL TENANT (no crm_tenant/dealer_account)
  role_in_entity TEXT CHECK IN ('owner','staff')
  verified_at                         -- cuándo pasó el check tax_id <-> entity.cif
  PK (user_ulid, entity_ulid)

user_session                         -- revocable, NUNCA JWT desnudo
  session_ulid  TEXT PK
  user_ulid     FK app_user
  token_hash    TEXT UNIQUE           -- sha256(token crudo); el crudo NUNCA se persiste
  created_at, expires_at, revoked_at, last_seen_at

user_notification                    -- destinatario que `alert` no tiene (carta 08 §5.1)
  notification_ulid TEXT PK
  user_ulid          FK app_user
  type               TEXT
  payload            JSONB
  created_at, read_at
```

Aplicada en vivo: `python -m scripts.migrate up` → `applied 0073 0073_auth.sql`
[VERIFICADO — salida real capturada en esta sesión]. Las 4 tablas confirmadas por query
directa contra `information_schema.tables` tras la migración.

Sin guard append-only en `user_session`/`user_notification` (mutan legítimamente:
`revoked_at`, `last_seen_at`, `read_at`). `dealer_membership` no lo necesita — no hay código
que mute nada salvo el propio `ON CONFLICT DO NOTHING` del claim.

---

## 3. Router — `services/api/routers/auth.py`

Registrado en `services/api/main.py` junto a los 5 existentes (`ops, entities, geo, vehicles,
platforms`) → ahora 6.

**Contrato de respuesta — deliberadamente distinto del resto de la API.** Los 5 routers de
datos envuelven todo en `{ok, data, error, meta}`. `auth.py` devuelve JSON plano
(`{token, expires_in, user}`, `{user}`, 204 sin cuerpo) porque `web/src/auth/AuthContext.tsx`
y `web/src/api/client.ts` **ya llamaban con ese contrato exacto** desde antes de esta sesión
(el frontend fue escrito años-código-atrás esperando un backend real detrás de
`DEV_BYPASS`). Adoptar el envelope de datos habría exigido un SEGUNDO recableo del frontend
sin ningún beneficio — se documenta la decisión en vez de maquillarla.

| Endpoint | Método | Auth | Rate limit | Devuelve |
|---|---|---|---|---|
| `/auth/register` | POST | — | `RATE_AUTH` (10/min/IP) | `{token, expires_in, user}` |
| `/auth/login` | POST | — | `RATE_AUTH` | `{token, expires_in, user}` |
| `/auth/me` | GET | Bearer | `RATE_DEFAULT` | `{user}` |
| `/auth/logout` | POST | Bearer | `RATE_DEFAULT` | 204 |
| `/auth/refresh` | POST | Bearer | `RATE_AUTH` | `{token, expires_in}` (rota el token) |
| `/auth/claim-dealer` | POST | Bearer | `RATE_AUTH` | `{user}` (role→'dealer' si pasa el check) |

`role` de registro público: **siempre `'particular'`**. El rol `dealer` no es
autoasignable — se gana vía `/auth/claim-dealer` (§4). El rol `staff` no tiene vía de
autoservicio (hueco declarado: cuentas staff se crean por operación manual de base de
datos; no hay superficie de admin en este workstream — YAGNI hasta que exista un
consumidor real).

---

## 4. Anti dealer-disfrazado — `/auth/claim-dealer` [VERIFICADO por test + curl]

Carta 08 §4.7: *"el rol `dealer` exige `cdp_code` verificado contra el censo (`entity`) vía
`services/api/tax_id.py`"*. Implementado como:

1. `tax_id.canonical_tax_id(tax_id_del_caller)` — debe pasar su checksum oficial BOE
   (NIF/NIE/CIF). Si no pasa → 400.
2. `resolve_cluster(cdp_code)` — si la entidad no existe → 404.
3. `entity.cif` de la entidad canónica se normaliza con el MISMO validador. Si la entidad no
   tiene CIF verificable en el censo → 409 (hueco declarado, no se puede comprobar, la
   reclamación se rechaza — nunca se hace un bypass silencioso).
4. Comparación normalizada `claim == registrado` → si difiere, 403 ("tax_id does not match
   this entity's registered records"). Reclamar el perfil de otro dealer exige conocer su
   CIF real, no solo su `cdp_code` público.
5. Éxito → `INSERT ... ON CONFLICT DO NOTHING` en `dealer_membership` + `role='dealer'` en
   `app_user` (solo si el rol previo era `particular`; `staff` no puede reclamar).

Verificado con una entidad real de la DB viva: `CDP-ES-01-7FAFJXW8` / CIF `B01530682`
(checksum válido confirmado independientemente por `services.api.tax_id.canonical_tax_id`,
entidad auto-canónica confirmada vía `resolve_cluster`). Test `test_claim_dealer_success_path`
prueba el camino feliz completo; `test_rejects_invalid_checksum` /
`test_rejects_mismatched_tax_id` / `test_rejects_unknown_cdp_code` prueban los tres rechazos.

---

## 5. Seguridad — decisiones y verificación

Regla del repo: código de auth/autorización dispara review de seguridad obligatoria antes de
cerrar. Hallazgos y decisiones de esta sesión:

- **Contraseñas**: argon2id vía `argon2-cffi` (`services/api/auth_security.py`), parámetros
  por defecto de la librería (recomendados OWASP). Nunca se trunca ni se rehashea con un
  esquema más débil. `needs_rehash()` expuesto para una futura migración de parámetros
  (no consumido aún — YAGNI hasta que se suban los costes de argon2).
- **Anti-enumeración por timing**: `verify_password()` corre argon2 SIEMPRE, incluso cuando
  la cuenta no existe (contra un hash señuelo precalculado una vez en el import), así que
  "no existe" y "contraseña incorrecta" tardan lo mismo y devuelven el mismo 401.
- **Anti-enumeración de respuesta**: login unifica ambos casos en 401 idéntico
  (`test_login_unknown_email_same_401_as_wrong_password`). `/auth/register` SÍ revela
  "email already registered" (409) — decisión consciente, no un descuido: es una práctica
  extendida en registro B2B/B2C y el `RATE_AUTH` (10/min/IP) acota el abuso de sondeo.
- **Sesiones opacas, nunca JWT desnudo**: token = `secrets.token_urlsafe(32)` (256 bits),
  solo su SHA-256 vive en `user_session.token_hash`. El crudo se entrega al cliente una vez
  (respuesta de register/login/refresh) y nunca se loguea ni se persiste.
- **Revocación real**: `/auth/logout` marca `revoked_at` server-side — no es un borrado de
  token solo en el cliente. Verificado: `test_logout_revokes_the_session` prueba que el mismo
  token deja de servir `/auth/me` inmediatamente después.
- **Rotación en refresh**: `/auth/refresh` revoca la sesión presentada y mint una nueva
  (transacción atómica) — acota la ventana de repetición de un token filtrado a un ciclo de
  refresco, no al TTL completo de 24h. Verificado: `test_refresh_rotates_token` prueba que el
  token viejo muere y el nuevo sirve.
- **Rate limiting**: `RATE_AUTH = 10/minute` por IP (vs `RATE_DEFAULT = 120/minute`) en las
  4 superficies de adivinación de credenciales (`register`, `login`, `refresh`,
  `claim-dealer`) — deliberadamente más estricto porque cada llamada gasta un hash argon2
  (caro por diseño) y es el objetivo de mayor valor de fuerza bruta de toda la API.
- **CORS ampliado con disciplina**: `main.py` pasó de `allow_methods=["GET","OPTIONS"]` a
  incluir `POST` (los 5 routers previos eran 100% lectura; estos son los primeros
  endpoints de escritura de la API) y `allow_headers` ganó `Authorization` + `X-Tenant-ID`
  (sin esto, el navegador bloquea el preflight y el frontend real nunca podría llamar a
  `/auth/*` — verificado con un preflight `OPTIONS` real, §7).
- **Sin secreto de firma que gestionar**: al no usar JWT, no hay `SECRET_KEY` que rotar ni
  fugar — una superficie de riesgo menos frente a la alternativa JWT.
- **Sin nuevo gate de prod**: `auth.py` no necesita `require_prod_secrets` — no depende de
  ningún secreto nuevo (los tokens son aleatorios, no firmados).

### Hueco de seguridad declarado (no bloqueante, registrado para el futuro)

- No hay job de purga de `user_session` expiradas/revocadas (crecimiento no acotado a muy
  largo plazo). Registrado como deuda menor — el registro `RATE_AUTH` y el volumen esperado
  de usuarios en esta fase del programa lo hacen no urgente; cuando exista el scheduler
  durable de pilar de producto, un job de limpieza diaria es trivial de añadir.
- `staff` no tiene ruta de creación — deliberado (YAGNI), declarado, no un olvido.

---

## 6. Frontend — `DEV_BYPASS` desmontado, una sola vez

- `web/src/auth/AuthContext.tsx`: **eliminado por completo** `DEV_BYPASS`/`DEV_USER` — el
  contexto habla siempre con `/auth/*` real. Añadida `register()` (antes solo existía
  `login()`); `logout()` ahora revoca la sesión en el servidor vía `fetch` crudo (no
  `api.post`, para no reentrar el propio manejador del evento `auth:unauthorized` en un
  bucle si el token ya es inválido).
- `web/src/pages/Register.tsx`: llamaba `login(email, password)` (un bug latente: nunca
  registraba nada, solo fingía iniciar sesión bajo `DEV_BYPASS`) → ahora llama `register(...)`
  con nombre real y distingue el 409 (email duplicado) con un mensaje propio.
- `web/src/pages/inventory/config.ts`: comentario que refería a `DEV_BYPASS` como ausencia de
  mapeo usuario→dealer se deja intacto (sigue siendo cierto: ese mapeo real para el
  inventario del dealer es trabajo de 03-F1, que consume este esquema — fuera del alcance de
  AUTH-0 por diseño del MASTER).
- `ResetPassword.tsx` / `TwoStep.tsx`: no llaman a `AuthContext` ni a ningún endpoint — fuera
  de alcance, sin cambios.
- Build verificado: `npm run build` (`tsc --noEmit && vite build`) verde, cero errores de
  tipos, bundle generado [VERIFICADO, esta sesión].

---

## 7. Verificación real ejecutada

1. **Migración aplicada a cardeep-pg viva** (:5433) — `scripts.migrate up`, 4 tablas
   confirmadas por query directa.
2. **Suite pytest nueva** `tests/test_auth_router.py` — 20 tests, **20/20 verdes** contra la
   DB viva (register happy/weak-password/malformed-email/duplicate/duplicate-case-insensitive;
   login happy/wrong-password/unknown-email-no-enumeration; me válido/sin-token/token-basura;
   logout revoca de verdad; refresh rota de verdad; claim-dealer con los 4 rechazos + el
   camino feliz contra una entidad real; guard de rate-limit). Cada test crea usuarios bajo
   el dominio reservado `@authtest.invalid` (RFC 2606) y un fixture de módulo los purga al
   cerrar — **verificado tras el run: 0 filas residuales** en `app_user`/`dealer_membership`.
3. **Regresión del resto de la API** — 18 archivos de test que importan `services.api`
   (incluye `test_api_auth.py`, `test_api_pagination.py`, `test_api_ratelimit_cache.py`,
   `test_api_seal.py`, `test_api_gaps.py`, `test_api_canonical.py`,
   `test_api_exhaustiveness.py`, `test_spanish_tax_id.py`, etc.) — ejecutados tras el cambio
   de `main.py`/`ratelimit.py`/`requirements.txt` para confirmar cero regresión en los 5
   routers preexistentes.
4. **Login real de extremo a extremo vía curl** contra una instancia uvicorn efímera
   (puerto 8091, misma DB viva), incluyendo el preflight CORS `OPTIONS` real desde el origen
   `http://localhost:5173` (el que usa `vite dev`): preflight 200 con
   `Access-Control-Allow-Methods: GET, POST, OPTIONS` y `Authorization`/`X-Tenant-ID` en
   `Allow-Headers` → register → `/auth/me` con el token real → `/auth/me` sin token (401) →
   login de nuevo → contraseña incorrecta (401) → logout → `/auth/me` post-logout (401).
   Usuario de prueba purgado de la DB inmediatamente después; instancia efímera detenida.
5. **Build de frontend** verde (`npm run build` en `web/`).

---

## 8. Archivos tocados

| Archivo | Cambio |
|---|---|
| `migrations/0073_auth.sql` | Nuevo — esquema completo (§2) |
| `services/api/auth_security.py` | Nuevo — hashing argon2id, tokens opacos, política de contraseña |
| `services/api/routers/auth.py` | Nuevo — router `/auth/*` (§3) |
| `services/api/main.py` | Registra `auth.router`; CORS: `+POST`, `+Authorization`/`+X-Tenant-ID` |
| `services/api/ratelimit.py` | `+RATE_AUTH` (10/min) |
| `requirements.txt` | `+argon2-cffi>=23,<26` |
| `tests/test_auth_router.py` | Nuevo — 20 tests (§7) |
| `web/src/auth/AuthContext.tsx` | `DEV_BYPASS` eliminado; `+register()`; `logout()` revoca en servidor |
| `web/src/pages/Register.tsx` | Llama `register()` real en vez de `login()`; copy de contraseña corregida (10, no 8) |
| `plans/cardeep-omni/AUTH-0.md` | Este documento |
| `plans/cardeep-omni/PROGRESO.md` | Marca AUTH-0 ejecutado dentro de BLOQUE 1 |

---

## 9. Qué NO hace este workstream (alcance deliberado, no descuido)

- No crea UI de "conectar tu cuenta de dealer" para `/auth/claim-dealer` — esa pantalla es
  trabajo de 03-F1 (el MASTER lo asigna explícitamente: *"03-F1+ ... consumen este esquema,
  no creando el suyo"*).
- No siembra la cuenta demo de GYATA — también 03-F1 (*"GYATA queda como cuenta demo
  sembrada"* es su fase, no la de AUTH-0).
- No construye `crm_*`, `dealer_lead`/`dealer_deal`, ni ninguna superficie de CRM — pilar 06,
  bloqueado detrás de este workstream pero no ejecutado por él.
- No implementa 2FA (la página `/2fa` existe en el frontend pero no llama a ningún backend;
  fuera del alcance de las 4 cartas fusionadas).
- No implementa recuperación de contraseña real (`/reset` es UI sin backend) — ninguna de las
  4 cartas fusionadas la especificaba.

---

## Resumen

Cuatro esquemas de auth en colisión (tres numerados `0073`) resueltos en una única migración
(`0073_auth.sql`, número real verificado en el momento de crearla) y un único router
(`auth.py`, 6 endpoints). Esquema = `app_user` (08) + `dealer_membership` (03) +
`user_session` + `user_notification` (08); `crm_tenant`/`dealer_account` descartados por
mandato del MASTER — el tenant es la entity vía membership. Seguridad: argon2id,
anti-enumeración por timing y por respuesta, sesiones opacas revocables con rotación en
refresh, rate-limit dedicado más estricto, CORS corregido para las primeras escrituras reales
de la API. `DEV_BYPASS` desmontado una sola vez del frontend (no tres). Verificado: migración
aplicada en vivo, 20/20 tests propios verdes con teardown limpio comprobado, 0 regresión en
los 18 archivos de test que tocan `services.api`, login real de extremo a extremo por curl
con preflight CORS real, build de frontend verde.
