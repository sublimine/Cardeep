# Carta de sub-proyecto — Pilar 06: Sistema de chats y contactos unificados (CRM)

> Programa: cardeep-omni · Clave: `06-unified-crm-chat` · Fecha: 2026-07-17
> Fase: SYNTHESIS (arquitectura). Este documento es la fuente de verdad del pilar
> hasta que una fase de ejecución lo enmiende con evidencia nueva.
> Doctrina aplicada: antialucinación tolerancia cero — cada afirmación lleva
> [VERIFICADO] (leída en código/DB/doc real, con archivo:línea) o [ASUMIDO]
> (declarada como suposición, jamás disfrazada de certeza).
> RECON base: 2026-07-16, re-verificación puntual 2026-07-17 (routers, migraciones,
> `types.ts`, `useApi.ts`, `useInbox.ts`, `deps.py`, nav de `Shell.tsx`).

> **NOTA DE TRACKER (2026-07-18, registrada por 05-multiposting F2, `00-MASTER.md` C-10
> "regla del primer llegado"):** `web/src/pages/Inbox.tsx` fue tocado antes de que este
> pilar aterrizara (Bloque 3 no ha empezado; 05 ejecutó su Bloque 2 F0-F2 primero). Per la
> regla del master, el primero en llegar retira el mock y deja un empty-state honesto sin
> reconstruir la página. Cambio real hecho por 05: `MOCK_CONVS` (líneas 14-19, conversaciones
> `mobile.de`/`autoscout24` fuera de alcance España + contactos ficticios) ELIMINADO;
> `conversations = data?.conversations ?? MOCK_CONVS` → `?? []`; el estado vacío de la lista
> ahora distingue "Bandeja aún no conectada" (cuando `useInbox()` trae `error`, el caso de
> HOY — `/inbox` no existe en `services/api`) de "Sin conversaciones" (caso post-F4, cuando
> el canal exista y esté simplemente vacío). `useInbox.ts`/`useConversation`/
> `useInboxMutations` **NO se tocaron** — siguen llamando exactamente los paths que esta carta
> ya documenta (`GET /inbox`, `GET /inbox/{id}`, `POST /inbox/{id}/reply`, `PATCH /inbox/{id}`)
> vía `web/src/api/client.ts`. Cuando F4 de este pilar construya `crm_inbox.py`, esos hooks
> deberían empezar a funcionar sin cambios adicionales en `Inbox.tsx` más allá de lo que ya
> está — el trabajo pendiente sigue siendo 100% el de esta carta ("F4 — Canal email real").

---

## 1. Estado actual

Siete páginas React ruteadas y en el nav — Chat, Contacts, Deals, Kanban, Notes, Inbox, Calendar — con shell visual trabajado (framer-motion, drawers, drag-and-drop, modales), pero **cada una es una isla con dataset hardcodeado, sin backend y sin cruce entre sí**. No existe ni un solo dato CRM real en todo el sistema.

### Superficie frontend: 7 páginas, 0 datos reales

- Rutas e imports: `web/src/App.tsx:11-32` (imports) y `:80-97` (rutas). Nav: `web/src/layout/Shell.tsx:40-52` — grupos "Deals/Kanban/Notas" y "OPERACIÓN: Inbox/Chat/Calendario". [VERIFICADO — Shell re-leído 2026-07-17]
- `web/src/pages/Chat.tsx` (720 líneas, leído completo en RECON): simulador de chat **INTERNO de equipo**, no de clientes — SEED de 5 conversaciones con 5 empleados ficticios (Carlos Ruiz, Ana Martínez, Pedro Gómez, Sofía López, Miguel Torres), 100% `useState` local, **cero** import de `api`/`fetch` en todo el archivo. Enviar un mensaje hace push a un array en memoria que muere al recargar. No es un canal de cliente. [VERIFICADO]
- `web/src/pages/Inbox.tsx` (283 líneas): la única página cableada a hooks reales — `web/src/hooks/useInbox.ts:16-48` llama `GET /inbox`, `GET /inbox/{id}`, `POST /inbox/{id}/reply`, `PATCH /inbox/{id}` vía `web/src/api/client.ts` (base `/api/v1`). Pero el backend NO tiene esos endpoints (ver abajo), así que toda llamada falla y la página enmascara el error: `Inbox.tsx:89` → `data?.conversations ?? MOCK_CONVS` (4 conversaciones fake definidas en `:14`). Matiz importante re-verificado 2026-07-17: `web/src/hooks/useApi.ts` NO tiene fallback propio — devuelve `{data: null, error}` honestamente; **es la página quien silencia el error con `?? MOCK_CONVS`**. El patrón de maquillaje vive en las páginas, no en el hook. [VERIFICADO]
- Los `sourcePlatform` mockeados del Inbox son `'mobile.de'`/`'autoscout24'`/`'manual'` — plataforma de anuncio de ORIGEN, no canal de comunicación. Ni siquiera el mock captura el concepto WhatsApp/email/SMS/formulario. [VERIFICADO RECON]
- `web/src/pages/Contacts.tsx` (592 líneas): llama `/contacts` (inexistente) → `MOCK_CONTACTS` de 12 nombres. El botón "Save contact" del modal solo ejecuta `handleClose()` — no persiste nada, ni siquiera a estado local. Los botones "Call"/"Email" del ContactDrawer no tienen `onClick`. [VERIFICADO RECON]
- `web/src/pages/Deals.tsx` (495 líneas) y `web/src/pages/Kanban.tsx` (315 líneas): ambos llaman `/deals` (inexistente) → `MOCK_DEALS` / `MOCK_BOARD` (Kanban.tsx:33, fallback :224). [VERIFICADO RECON]
- `web/src/pages/Notes.tsx` (581 líneas): persiste solo en `localStorage` (clave `cardeep_notes`) — no multiusuario, no multi-dispositivo, se pierde al limpiar caché. [VERIFICADO RECON]
- `web/src/pages/Calendar.tsx` (222 líneas): 100% `MOCK_EVENTS` estático, sin persistencia de ningún tipo; el botón "New event" no tiene handler. [VERIFICADO RECON]

### Modelo de tipos: bien diseñado, sin nada detrás

`web/src/types.ts` (128 líneas por `wc -l`, releído completo 2026-07-17): `Deal` (:33-47), `Contact` (:49-58), `Activity` (:60-67), `Conversation` (:69-86), `Message` (:88-99), `Template` (:101-109). Observaciones directas del código:
- `Contact` no tiene **ningún** campo de consentimiento (transaccional/marketing), ni normalización de teléfono (`phone: string` libre). [VERIFICADO types.ts:49-58]
- `Deal.stage` = `'lead'|'contacted'|'offer'|'negotiation'|'won'|'lost'` sin `probability` ni valor esperado. [VERIFICADO types.ts:38]
- `Conversation` no modela canal de comunicación como máquina de estados (sin ventana de sesión WhatsApp, sin plantilla aprobada); `sourcePlatform` y `sentVia` son `string` libres. [VERIFICADO types.ts:75,96]
- Todos los tipos llevan `tenantId` — pero ningún endpoint lo aplica (ver backend).

### Backend: CERO CRM

- `services/api/main.py` registra solo 5 routers: `ops, entities, geo, platforms, vehicles` (import en `:82`, `include_router` en `:146-150`). `ls services/api/routers/` → `entities.py, geo.py, ops.py, platforms.py, vehicles.py` — no existe `inbox.py`, `contacts.py`, `deals.py` ni nada CRM. [VERIFICADO — re-ejecutado 2026-07-17]
- Migraciones: **66 archivos `.sql` numerados 0001–0072 con huecos** (faltan 0008, 0010-0012, 0014-0015; contado con `ls | wc -l` 2026-07-17 — corrige el "72 migraciones" del RECON, que contaba por numeración). Grep de `CREATE TABLE` para conversation/contact/deal/note/calendar/message/kanban → **0 matches**. El schema vivo es 100% dominio de scraping (geo/entities/vehicles/events/dedup/country). [VERIFICADO]
- Integraciones de canal: grep de whatsapp/twilio/sendgrid/smtp/imap sobre `services/`, `pipeline/`, `scripts/` → 0 matches relevantes (las 35 coincidencias repo-wide son plugins de Obsidian, docs de competidores y nombres de scrapers). [VERIFICADO RECON]
- Tiempo real: grep de `EventSource|WebSocket|socket.io` en `web/src` → 0 matches. [VERIFICADO RECON]
- Auth existente: `services/api/deps.py:21-48` — `require_api_key`, **una clave global** vía env `CARDEEP_API_KEY` (público en dev, fail-closed en prod). NO existe multi-tenant, ni usuarios, ni sesiones. [VERIFICADO — leído 2026-07-17]

### El roadmap propio está equivocado y hay que corregirlo

`docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md` §3.10 (línea 277) afirma que las tablas `publish_job`/`platform_credentials`/`inbox_thread`/`message` llegan en "migraciones 0033-0035". **Falso**: `0033_evict.sql`, `0034_truncate_guards.sql`, `0035_append_only_row_guards.sql` son eviction ledger y guards de auditoría del pipeline de vehículos, sin relación con inbox/CRM. [VERIFICADO RECON — las 3 migraciones leídas]. La §3.11 etiqueta CRM como "[NEAR]" y la §3.14 lista WhatsApp+email como "future" — el propio plan reconoce que los canales no existen.

### Huecos estructurales consolidados

1. Backend CRM inexistente (ni router, ni tabla, ni servicio).
2. 0 integraciones de canal real (WhatsApp/email/SMS/formulario).
3. 0 tiempo real (ni SSE ni WebSocket).
4. `Chat.tsx` tiene la forma EQUIVOCADA para este pilar (mensajería interna ficticia, no canal de cliente) — necesita decisión de decomiso, no cableado.
5. 0 relación viva Contacts↔Deals↔Inbox↔censo — cada página es un array independiente.
6. Botones decorativos sin función (Save contact, Call, Email, New event).
7. Sin consentimiento/E.164/dedup en el modelo de Contact — riesgo legal directo si se activa mensajería real (LSSI-CE/LOPDGDD).
8. Sin multi-tenant ni usuarios (solo API-key global).
9. Blueprint con cita de migraciones falsa — inutilizable como referencia hasta corregirse.
10. **Hueco de RECON declarado**: no se verificó si existe algún dealer real usando la plataforma (usuarios/tenants = 0 tablas); el CRM se diseña para un usuario que aún no puede ni registrarse contra backend. Se resuelve como dependencia explícita en F1.

---

## 2. Investigación competitiva/adversarial

RESEARCH ejecutado sobre 20 referencias (Chatwoot, Front, Intercom, HubSpot Conversations, Twilio Conversations, WhatsApp Business Platform, Salesforce, Twenty CRM, Close, Kanban University, VinSolutions, Podium, Fullpath, Impel AI, DriveCentric, dealerdesk.com, RFC 6350/6352 + 5545/4791, E.164, TCPA/LSSI-CE-LOPDGDD, Informatica/Reltio MDM). Criterios EXACTOS extraídos:

### Arquitectura de identidad y canal (el corazón del pilar)

| Referencia | Criterio exacto |
|---|---|
| **Chatwoot** (código Rails público, auditable) | `Inbox → Channel (polymorphic, 13+ tipos)`. Tabla `ContactInbox` con **índice único `(inbox_id, source_id)`**: ata UNA identidad de canal (email, número WhatsApp, PSID de Facebook) a un Contact. Un Contact puede tener N filas ContactInbox (una por canal); las Conversations cuelgan de esa unión. El mismo humano por email y por WhatsApp = **un** Contact con dos identidades de canal, no dos contactos. |
| **Chatwoot** (merge) | Fusión CONSERVADORA: busca por identifier/email/phone, descarta claves en conflicto, y **NO fusiona automáticamente si el destino ya está "identified"** (evita fundir dos personas reales por error). |
| **Intercom** | Separación explícita lead (anónimo) vs user (identificado). Fusión automática SOLO con certeza criptográfica (cookie de sesión + login); el resto → "potential duplicates" con fusión manual asistida. Mismo patrón conservador. |
| **Twilio Conversations** | Modelo "Participant-centric": el recurso central es la Conversation (hilo único); cada Participant tiene identity; los mensajes salen NATIVOS por el canal de cada participante (SMS si SMS, WhatsApp si WhatsApp) pero viven en el mismo hilo. **La unificación ocurre a nivel de PARTICIPANT, no en post-proceso de UI.** |
| **WhatsApp Business Platform** (Meta) | Máquina de estados dura: ventana de servicio de **24h desde el último mensaje ENTRANTE** (se resetea con cada entrante); dentro, mensajes libres; fuera, SOLO plantillas pre-aprobadas por Meta. Desde el 1-oct-2026, los mensajes de servicio dentro de ventana se cobran por mensaje. Cualquier integración seria debe modelar esta máquina + su coste variable. `types.ts` no tiene ni campo de ventana ni de plantilla aprobada. |
| **HubSpot Conversations** | Flujo exacto: mensaje entrante → "conversation object" ligado a Contact vía email/chat-ID → si el contacto no existe, se AUTOGENERA registro básico → panel lateral con ticket asociado + historial de conversaciones pasadas del mismo contacto. |
| **Front** | Collision detection en tiempo real (quién está viendo/respondiendo), draft compartido editable en vivo, @mention para pedir revisión pre-envío, load balancing que asigna al agente con MENOS conversaciones abiertas (saltando Busy/OOO). Capacidades multi-agente que ninguna página de Cardeep tiene. |

### Pipeline de deals y kanban de verdad

| Referencia | Criterio exacto |
|---|---|
| **Salesforce** | Cada Opportunity: `Amount`, `Stage`, `Probability` (derivada de Stage, desacoplable), `Expected Revenue = Amount × Probability`; Stage mapea a 1 de 5 Forecast Categories (Pipeline/Best Case/Commit/Closed/Omitted). **El pipeline es un modelo cuantitativo que produce revenue esperado, no columnas decorativas.** `Deal` de Cardeep no tiene probability ni forecast. |
| **Kanban University** (Anderson) | 5 reglas: (1) visualizar el flujo; (2) **WIP limit** = nº máximo de tarjetas por columna; (3) sistema PULL (la tarjeta avanza solo si la columna destino tiene capacidad); (4) políticas explícitas de "definition of done" por columna; (5) medir el flujo (lead time / cycle time). `Kanban.tsx` no implementa NINGUNA de las 5 — es drag libre sobre MOCK_BOARD. |
| **Close CRM** | Cero context-switch: llamadas/SMS/email nativos desde la propia ficha del lead, transcripción + action items por IA, whisper/barge en vivo. Filosofía opuesta al patrón isla de Cardeep. |

### Vertical automotriz (los que ya hacen esto)

| Referencia | Criterio exacto |
|---|---|
| **dealerdesk.com** (DACH) | Referencia EUROPEA directa: unifica **mobile.de + AutoScout24 + leasingmarkt.de** + email + teléfono + redes + Excel de retornos en una plataforma, con tickets, distribución automática de leads, escalado anti-lead-perdido, y reclamo "100% DSGVO-konform". **Ya hace, sobre los mismos portales que Cardeep scrapea, lo que este pilar pretende.** |
| **VinSolutions** (Cox) | "Match & merge" en tiempo real entre Ventas y Servicio: el cliente que compró y luego trae el coche a revisión = UNA ficha. Exactamente el gap #5 de Cardeep. |
| **Fullpath** (Cox) | "Shopper identity resolution": CRM + DMS + anuncios Google/Facebook + historial de vistas en portales → un perfil único POR COMPRADOR. Es el análogo del VAM de Cardeep pero del lado comprador — dominio de datos que Cardeep NO tiene. |
| **Podium** | SMS/Facebook/Instagram/Google/webchat en un inbox único con agente IA que agenda test drives y citas de servicio. |
| **DriveCentric** | Texting/email/video nativos + agente IA 24/7 tipo BDC virtual — canales DENTRO del CRM, no add-ons. |
| **Impel AI** (framework de evaluación) | 4 criterios reutilizables para juzgar un CRM automotriz: (1) madurez de API (docs públicas + profundidad + bidireccionalidad); (2) IA/ML nativa vs integrada; (3) especialización automotriz = integraciones PRE-CONSTRUIDAS (DMS, scheduler de citas, equity mining); (4) resultados medibles (su Sales AI reporta +252% touchpoints/lead, +25% tasa de cita). Este pilar se auto-evaluará contra estos 4 criterios. |

### Estándares e higiene legal (no opcionales)

| Referencia | Criterio exacto |
|---|---|
| **E.164** (ITU-T) | Normalización de teléfono a `+[país][número]` ANTES de cualquier comparación de dedup; estudios citan hasta 35% menos comunicaciones fallidas. Requisito mínimo ausente del `Contact` actual. |
| **RFC 6350/vCard + CardDAV; RFC 5545/iCalendar + CalDAV** | Contacto/evento en estos formatos es sincronizable NATIVAMENTE con Google/Outlook/Apple sin desarrollo propietario. Notes (localStorage) y Calendar (sin persistencia) no exportan nada. |
| **TCPA + LSSI-CE/LOPDGDD** | (a) Flags de consentimiento SEPARADOS por tipo (transaccional vs marketing) en el registro del contacto; (b) supresión de opt-out UNIVERSAL y en tiempo real entre TODOS los canales (STOP por SMS suprime también WhatsApp/email); (c) España: 3 condiciones acumulativas para reenviar sin nuevo consentimiento (relación contractual previa + productos similares + opt-out fácil en cada envío). `Contact` sin campo de consentimiento = riesgo legal directo, no solo gap de producto. |
| **MDM (Informatica/Reltio)** | Match determinista + match difuso (errores tipográficos, transposiciones, fonética tipo SSA_NAME3) + reglas de **survivorship** explícitas (qué valor de cada campo sobrevive al fusionar). La disciplina que Cardeep YA aplica a vehículos/entidades (VAM) y que su CRM no aplica en absoluto. |

---

## 3. Objetivo Cardeep para este pilar — y el límite honesto

### El límite honesto, primero

**Cardeep NO tiene hoy ninguna ventaja estructural en este pilar**, y esta carta lo declara en vez de forzar la narrativa del censo donde no aplica:

1. **Dominio ortogonal.** El censo + delta + dedup + VAM resuelven identidad de VENDEDORES/VEHÍCULOS. El CRM resuelve identidad de COMPRADORES/LEADS y la infraestructura para hablarles. Problemas análogos (ambos son identity resolution), entidades distintas. Verificado: ni una tabla de las 66 migraciones cruza los dos dominios.
2. **El trabajo pesado es infraestructura commoditizada.** WhatsApp Cloud API, SMTP/IMAP, SMS/BSP, deliverability, anti-spam, cumplimiento — en esto Cardeep parte de cero exacto frente a Twilio/Meta/Chatwoot/Front, que llevan años. Ningún activo de Cardeep acorta esa distancia. Reconstruir esta capa sería reinventar lo que existe como API o como software libre.
3. **Los verticales ya existen.** dealerdesk.com opera en Europa sobre los MISMOS portales que Cardeep scrapea. Cox (VinSolutions/Fullpath), Podium y DriveCentric dominan el playbook. Cardeep parte DETRÁS en este frente.

### El objetivo, en consecuencia

**No competir horizontalmente con Front/Intercom/HubSpot. Construir el CRM mínimo-real que un dealer español necesita, con UNA ventaja que nadie más puede copiar: cada conversación y cada deal enriquecidos con el contexto de mercado vivo del censo.**

Concretamente: cuando un lead pregunta por un coche, el dealer ve en la misma tarjeta — sin salir del inbox — los días en mercado de ESE vehículo (de `vehicle.first_seen`), su historial de precio (de `vehicle_event`), y su posición frente al segmento (del pilar 01 cuando exista su capa de analítica). Ese dato no lo tiene Chatwoot, ni Front, ni HubSpot — por diseño no pueden — y ni siquiera Fullpath lo tiene a la granularidad cross-marketplace del scraping de Cardeep. **Esa es la única superación posible y es real, pero condicional**: se activa SOLO si (a) el canal real se INTEGRA (comprado/adoptado, no reconstruido) y (b) existe el cruce Contact↔Deal↔vehicle ULID↔entity CDP que hoy no existe.

Decisiones de arquitectura derivadas (firmes salvo evidencia nueva):
- **Canal 1 = email** (F4): es donde llegan HOY los leads reales de portales españoles (coches.net, Wallapop, Milanuncios notifican por email al dealer) y es el único canal integrable a coste ~€0 (IMAP/SMTP). WhatsApp Cloud API queda gateado como fase de gasto (F7) — requiere verificación de negocio Meta y coste por mensaje desde oct-2026.
- **Comprar/adoptar, no reconstruir**: si en F4 la ingesta email propia mide >2 semanas de esfuerzo, se evalúa Chatwoot self-hosted como sustrato de mensajería (open source, auditado en RESEARCH) con Cardeep como capa de enriquecimiento encima. La decisión se toma con datos en F4, no ahora. [ASUMIDO el umbral de 2 semanas — decisión de gestión, no dato]
- **`Chat.tsx` se decomisiona de este pilar**: chat interno de equipo es otro producto (YAGNI hoy). El "chat" del pilar es la conversación con el cliente en el Inbox. La ruta `/chat` sale del nav en F3 (el código puede quedar parkeado, sin ruta).
- **Colaboración multi-agente tipo Front (collision detection, draft compartido, load balancing least-open) queda explícitamente DIFERIDA**: el usuario objetivo (compraventa española de 1-3 usuarios) no la necesita en v1, y añadirla ahora sería speculative generality. El criterio queda registrado en §2 como listón futuro; si algún día entra, exigirá criterios nuevos en §4 (presence vía el SSE de F4, asignación `min(count(conversaciones abiertas))` por agente) y fase propia — no improvisación. Lo único que SÍ se hace ya: el campo `assignee` en `crm_conversation` nace en F1 para no exigir migración destructiva después.

---

## 4. Criterios de evaluación CONCRETOS (qué se muestra y cómo se calcula)

Nada aleatorio: cada número/badge/sección del frontend traza a un criterio de esta tabla. Si un dato no puede calcularse así, NO se muestra (se muestra el estado vacío honesto, jamás un mock).

### Inbox (bandeja unificada)

| Elemento en pantalla | Cálculo exacto | Fuente |
|---|---|---|
| Badge de canal por conversación | `crm_conversation.channel` (enum: `email`, `whatsapp`, `web_form`, `phone`, `walk_in`) — nunca string libre | Criterio Chatwoot: canal = tipo polimórfico, no texto |
| Contador "sin leer" | `COUNT(crm_message WHERE direction='inbound' AND read_at IS NULL)` por conversación; el total del nav = suma sobre conversaciones `status='open'` | Dato derivado, nunca campo manual |
| Badge "SIN RESPONDER + tiempo" | último mensaje `direction='inbound'` sin outbound posterior Y `now() − last_message_at > 1h` (umbral configurable por tenant, default 1h) | Criterio Front (SLA de respuesta) |
| Ventana WhatsApp (cuando exista F7) | countdown `last_inbound_at + 24h − now()`; expirada → composer bloqueado salvo plantilla con `template.meta_approved = true` | Máquina de estados Meta, literal |
| Chip de vehículo en la conversación | solo si `crm_conversation.vehicle_ulid` resuelve contra `vehicle` (join real); muestra `make model · price · días en mercado = now() − vehicle.first_seen` | Cruce censo (F5); si no resuelve, NO se muestra chip |
| Sugerencia "posible duplicado" | teléfono normalizado E.164 idéntico O email lowercased idéntico entre 2 contactos del tenant → banner con fusión MANUAL asistida; **nunca auto-merge si ambos tienen ≥1 deal `won`** | E.164 + regla conservadora Chatwoot/Intercom |

### Deals + Kanban

| Elemento | Cálculo exacto | Fuente |
|---|---|---|
| Valor esperado del pipeline (cabecera) | `Σ (deal.amount × probability(stage))` sobre deals abiertos; probability por defecto: lead 10%, contacted 25%, offer 50%, negotiation 75%, won 100%, lost 0% — editable por deal | Modelo Salesforce (Amount×Probability=Expected Revenue) |
| WIP limit por columna | contador `n/límite` en cabecera de columna (default 10, configurable); al exceder, la columna se marca en ámbar y el drop pide confirmación — no se bloquea (pull suave, no burocracia) | Kanban University regla 2, adaptada |
| Lead time | `AVG(won_at − created_at)` sobre deals `won` en ventana móvil de 90 días; se muestra en la cabecera del board | Kanban University regla 5 |
| Cycle time por etapa | derivado de `crm_deal_stage_event` (append-only): tiempo medio en cada stage | Mismo patrón append-only que `vehicle_event` (doctrina del repo) |
| Chip de contexto de mercado en tarjeta | idéntico al chip del Inbox (mismo cálculo, misma fuente) — un solo camino de código | Anti-duplicación |

### Contacts

| Elemento | Cálculo exacto | Fuente |
|---|---|---|
| Teléfono mostrado | siempre render de `phone_e164` formateado; el valor crudo tecleado se guarda en `phone_raw` (survivorship auditable) | E.164 + MDM survivorship |
| Badges de consentimiento | `crm_consent` por (contacto, canal, propósito): verde=granted con fecha+origen, gris=sin registro, rojo=revocado. El botón de envío de marketing se DESHABILITA sin consentimiento verde para ese canal | TCPA/LSSI-CE literal |
| Historial unificado del contacto | timeline = UNION de `crm_message` + `crm_activity` + `crm_deal_stage_event` ordenada por fecha, del contacto y sus deals | Criterio HubSpot (panel lateral con historial completo) |
| "Save contact" | POST real a `/api/v1/crm/contacts`; el modal NO cierra hasta 201; error → mensaje visible | Anti-botón-decorativo |

### Calendar + Notes

| Elemento | Cálculo | Fuente |
|---|---|---|
| Eventos | `crm_event` en PG; export `.ics` válido RFC 5545 por evento y por agenda | RFC 5545 |
| Notas | `crm_note` en PG (migradas desde localStorage una vez, con banner de migración) | Multi-dispositivo real |

### Regla transversal de honestidad de producto

**Prohibido `?? MOCK_*` en cualquier página CRM.** Si la API falla, se muestra el error y un estado vacío honesto ("No se pudo cargar — reintentar"). El patrón `Inbox.tsx:89` se erradica en F3. Este es el mismo estándar antialucinación del proyecto aplicado al producto: la UI jamás presenta un dato inventado con voz de dato real.

---

## 5. Modelo de datos + almacenamiento backend

### Lo que se REUTILIZA (existente, nombres reales verificados)

- **PostgreSQL del proyecto** (contenedor `cardeep-pg`; vivo según RECON de la carta 01: `docker ps` Up + `/health` `db:ok`). El CRM vive en la MISMA base, tablas con prefijo `crm_` para aislar el dominio del schema de scraping. [VERIFICADO infra; el prefijo es decisión de diseño de esta carta]
- `vehicle` y `vehicle_event` (`migrations/0003_vehicles_events.sql:4-26` y `:33-42`): fuente de `first_seen`/`last_seen`, precio e historial para el chip de contexto. Se referencian por ULID, **solo lectura** desde el CRM. [VERIFICADO en carta 01]
- `entity` (`migrations/0002_entities.sql`): el CDP de dealer es el candidato natural a raíz de tenant (un tenant CRM ↔ una entity del censo cuando el dealer es cliente). [VERIFICADO existencia; el mapeo tenant↔entity es diseño]
- `v_canonical_vehicle` (`migrations/0023_vehicle_cluster.sql`): para que el chip de contexto no cuente 3 veces el mismo coche multi-plataforma. [VERIFICADO en carta 01]
- Endpoints existentes de solo-lectura para el cruce: `vehicles.py` (`/vehicles/{ulid}`, `/vehicles/{ulid}/history`) y `entities.py` (`/entities/{cdp}/inventory`, `/entities/{cdp}/delta`). [VERIFICADO por grep en carta 01, routers re-listados 2026-07-17]
- `services/api/deps.py` (`require_api_key`, helpers de respuesta, DSN) y `services/api/ratelimit.py` (slowapi): los routers CRM se registran en `main.py` siguiendo el patrón exacto de los 5 existentes. [VERIFICADO deps.py:21-48, main.py:82,146-150]
- Frontend: `web/src/api/client.ts` (base `/api/v1`), `web/src/hooks/useApi.ts` (ya honesto: `{data,error,loading,reload}`), `web/src/types.ts` (los tipos se EXTIENDEN, no se reescriben desde cero), y el shell visual completo de las 7 páginas (el trabajo de UI ya hecho se conserva; se le cambia la sangre, no la piel). [VERIFICADO]

### Lo que se CREA (nuevo — nombres propuestos, migraciones 0073+; NO existen hoy)

Todas nuevas, ninguna colisiona con las 66 existentes (verificado por grep de `CREATE TABLE`):

| Tabla nueva | Contenido esencial |
|---|---|
| `crm_tenant` | raíz de tenancy; FK opcional a `entity(cdp)` del censo |
| `crm_user` | usuarios del dealer (email, hash, rol); base para sesiones |
| `crm_contact` | nombre, `email_lower`, `phone_raw`, `phone_e164`, tenant_id; índice único parcial por (tenant, phone_e164) y (tenant, email_lower) para dedup determinista |
| `crm_contact_channel` | patrón ContactInbox de Chatwoot: `(channel, source_id)` único por tenant — ata identidad de canal a contacto; N canales por contacto |
| `crm_consent` | (contact_id, channel, purpose transaccional/marketing, status, source, occurred_at) — append-only; el estado vigente es el último evento |
| `crm_conversation` | tenant, contact_id, channel (enum), vehicle_ulid nullable, deal_id nullable, status, assignee (crm_user nullable — reservado para la asignación multi-agente diferida en §3), last_inbound_at (para ventana 24h futura) |
| `crm_message` | conversation_id, direction, body, provider_message_id, provider_ack_at, read_at — **el mensaje se marca enviado SOLO con ACK del proveedor persistido** |
| `crm_deal` | contact_id, vehicle_ulid nullable, stage (enum), amount, probability, won_at/lost_at |
| `crm_deal_stage_event` | append-only de cambios de stage (mismo patrón que `vehicle_event`) |
| `crm_activity` | llamadas/visitas/recordatorios ligados a deal o contacto |
| `crm_note`, `crm_event` | notas y calendario persistidos; `crm_event` con campos suficientes para export RFC 5545 |
| `crm_template` | plantillas de respuesta; campo `meta_approved` reservado para F7 |

Guards: mismas disciplinas que el repo — `crm_consent` y `crm_deal_stage_event` append-only con row-guard (patrón de `0035_append_only_row_guards.sql`); enums PG en vez de TEXT+CHECK (patrón de `0005_types_and_guards.sql`). [VERIFICADO que esos patrones existen en el repo]

Servicios nuevos: `services/api/routers/crm_contacts.py`, `crm_deals.py`, `crm_inbox.py` (los paths que `useInbox.ts` YA espera: `/inbox`, `/inbox/{id}`, `/inbox/{id}/reply`, `PATCH /inbox/{id}` — el contrato frontend existente se respeta para minimizar reescritura); `services/crm/email_ingest.py` (worker IMAP, F4); SSE vía endpoint FastAPI `StreamingResponse` (F4, sin dependencia nueva).

**Hueco declarado**: no se ha verificado si el repo tiene ya infraestructura de workers programados reutilizable para el poller IMAP (el RECON de este pilar no auditó `pipeline/` a ese nivel). Se audita en F4 antes de escribir el worker; si existe scheduler durable (la memoria del proyecto sugiere que sí en `pipeline/`, pero NO está verificado aquí), se reutiliza.

---

## 6. Especificación de pantalla — en la piel del dealer

El usuario es el dueño o el comercial de una compraventa española: 30-300 coches, leads entrando por coches.net/Wallapop/Milanuncios al correo, WhatsApp personal quemado a mensajes, y una libreta o un Excel como "CRM". Su pregunta diaria no es "¿qué es un pipeline?" — es **"¿quién me ha escrito, por qué coche, y a quién se me está enfriando?"**.

### Bandeja (Inbox) — la pantalla donde vive

- Lista de conversaciones ordenada por urgencia real: primero las que llevan más tiempo **sin responder** (badge rojo "SIN RESPONDER · 3 h"), no por mera fecha.
- Cada fila: nombre del cliente, badge del canal (✉ Email · ⊞ Formulario · — WhatsApp llegará después y se dirá honestamente "próximamente", no un icono muerto), y **el coche por el que pregunta** como chip: "BMW 320d 2019 · 18.900 € · **34 días en tu stock**". Ese "34 días" sale del censo (`first_seen`), no de que nadie lo teclee.
- Al abrir: hilo completo a la izquierda; a la derecha, la ficha del cliente (todas sus conversaciones y deals anteriores — si preguntó por otro coche hace 2 meses, se ve) y la ficha del coche con su historial de precio real.
- Composer: responder por el MISMO canal por el que escribió el cliente (criterio Twilio: nativo por participante). Botón de plantillas ("Sigue disponible, ¿cuándo quieres verlo?"). El mensaje se marca "Enviado ✓" solo cuando el servidor de correo confirma — si falla, se dice "No se pudo enviar", nunca un check falso.
- Si el cliente ya existe (mismo teléfono/email), la conversación entra en SU ficha automáticamente (criterio HubSpot). Si se parece pero no es seguro: banner discreto "¿Es el mismo Juan Pérez de marzo?" con fusión en un clic — nunca fusión silenciosa.

### Tablero (Kanban) — su semana de un vistazo

- Columnas en su idioma: **Nuevo → Contactado → Oferta hecha → Negociando → Vendido / Perdido**.
- Cabecera del board: "**Tienes 41.300 € en juego**" (valor esperado = Σ importe × probabilidad de etapa) y "De contacto a venta: 12 días de media". Números que un dealer entiende sin manual.
- Columna con demasiadas tarjetas → se tiñe de ámbar: "8 ofertas sin mover — se te enfrían". Es el WIP limit contado en dinero y frío, no en jerga.
- Tarjeta: cliente + coche + días en la etapa + el mismo chip de mercado ("este coche lleva 61 días en stock — baja margen o muévelo").

### Contactos — su libreta, pero viva

- Buscar por nombre, teléfono o coche. Ficha = timeline único: mensajes, llamadas apuntadas, visitas, deals — todo mezclado por fecha.
- Consentimientos visibles como semáforo simple: "Puedes escribirle ofertas: SÍ (dio permiso el 12/05) / NO". Si es NO, el botón de campaña ni aparece — la ley integrada en la UI, no en un PDF.
- Exportar contacto a vCard (se abre en su iPhone/Android directamente).

### Calendario + Notas

- "Visita de Juan · BMW 320d · jueves 17:00" ligado al deal; export .ics → aparece en su Google Calendar sin explicarle qué es CalDAV.
- Notas sincronizadas entre el móvil del comercial y el PC de la oficina (hoy se pierden al limpiar caché — inaceptable).

### Lo que DESAPARECE

- `/chat` (empleados ficticios) sale del nav. Ningún dealer real chatea con "Sofía López".
- Todo mock: si no hay leads aún, la bandeja dice "Conecta tu correo de leads y aquí aparecerán" con el botón de configuración — un estado vacío que VENDE el paso siguiente, no 4 conversaciones falsas.

---

## 7. Protocolo de verificación (2 vías independientes por dato)

El mismo estándar antialucinación del proyecto, aplicado al producto. Un dato solo se muestra si sobrevive a dos caminos distintos del que lo produjo:

| Dato mostrado | Vía 1 | Vía 2 (independiente) |
|---|---|---|
| Conversaciones/mensajes del inbox | respuesta del endpoint `/api/v1/crm/inbox` | `psql` directo: `SELECT count(*) FROM crm_conversation/crm_message` con los mismos filtros — los conteos deben cuadrar en test E2E (Playwright + SQL en CI) |
| "Enviado ✓" de un mensaje | ACK del proveedor (`provider_message_id` + `provider_ack_at` persistidos) | verificación en la superficie real del canal: para email, el mensaje aparece en la carpeta Sent/el buzón receptor de prueba del test E2E — el check NO se pinta con solo el 200 del POST propio |
| "34 días en tu stock" (chip de mercado) | valor servido por el endpoint CRM (join con `vehicle`) | recomputado en test contra `vehicle.first_seen` leído por `/vehicles/{ulid}` (camino de código distinto: router vehicles vs router crm) — divergencia >0 días = fallo de build |
| Historial de precio del coche | `vehicle_event` vía join CRM | `/vehicles/{ulid}/history` (endpoint existente, código independiente) |
| "Posible duplicado" | match E.164/email en SQL | recomputación en test unitario con la librería de normalización sobre los valores `phone_raw` originales — el índice y el normalizador deben coincidir |
| Valor esperado del pipeline | suma servida por `/crm/deals/summary` | `SELECT SUM(amount * probability)` directo en el test de integración; además, invariante: suma de columnas = total del board |
| Consentimiento (semáforo) | último evento de `crm_consent` vía API | replay del append-only completo en test: el estado reconstruido desde el evento 1 debe igualar al vigente (mismo patrón de verificación que los ledgers del pipeline) |
| Contador "sin leer" | agregado del endpoint | invariante en E2E: abrir la conversación en el navegador (Playwright) → el contador decrementa exactamente en el nº de mensajes marcados; `read_at` visible por SQL |
| Export .ics / vCard | archivo generado | importación real del archivo en un cliente externo (test con librería de parsing independiente `icalendar`/vobject en CI; smoke manual en Google Calendar en la revisión de fase) |
| Ingesta de lead por email (F4) | fila creada en `crm_conversation` | correo de origen re-localizado por `Message-ID` en el buzón IMAP; parser reproducible: mismo .eml → mismo resultado (fixtures de correos reales de coches.net/Wallapop en tests) |

Regla de fallo: si las dos vías divergen, el dato NO se muestra y se abre incidencia — nunca se elige "la que queda mejor". Los checks de conteo cruzado (API vs SQL) corren en CI en cada PR que toque `services/api/routers/crm_*` o `web/src/pages/{Inbox,Contacts,Deals,Kanban,Calendar,Notes}.tsx`.

---

## 8. Uso de LLM (doctrina €0: local/barato para lo masivo, caro solo para decidir)

### Primero: donde NO hay LLM

- Parsing de emails de lead de portales conocidos (coches.net, Wallapop, Milanuncios): **parsers deterministas por portal** (regex/DOM sobre el HTML del correo). Los formatos son plantillas estables de cada portal; un LLM aquí sería coste y no-determinismo gratuitos. Fixtures reales en tests.
- Dedup de contactos: E.164 + email lowercased = SQL puro.
- Ventana 24h WhatsApp, SLA, WIP, valor esperado: aritmética.

### LLM local/barato (fuera del camino crítico — el pipeline funciona igual si el modelo está caído)

| Tarea | Modelo | Justificación |
|---|---|---|
| Emails de lead de formato DESCONOCIDO (portal nuevo, correo libre de un particular) | local/barato | extracción de nombre/teléfono/coche cuando el parser determinista falla; el resultado se marca "extracción asistida — confirmar" en la UI, nunca se persiste como verificado sin confirmación del dealer |
| Clasificación de intención del lead (compra / tasación / financiación / spam) | local/barato | etiqueta sugerida en la bandeja; error tolerable, volumen alto |
| Matching texto-libre→vehículo ("el BMW gris que tenéis por 19.000") | local/barato como ranker | genera candidatos contra el inventario del tenant (`/entities/{cdp}/inventory`); el dealer confirma con un clic; el chip solo se pinta tras confirmación (criterio §4) |
| Sugerencia de borrador de respuesta | local/barato | el dealer siempre edita/aprueba; nada se envía solo |
| Asistencia difusa al dedup (nombres con typos, fonética) | local/barato | genera CANDIDATOS para la fusión manual asistida; jamás fusiona (regla conservadora §2) |

### Lo que justificaría modelo caro — respuesta honesta: NADA en runtime

En este pilar no hay ninguna decisión en producción que justifique un modelo caro por petición: las tareas son clasificar/parsear/deduplicar (dominio explícito del modelo local en la doctrina del CLAUDE.md). El razonamiento caro se gasta UNA vez, en tiempo de diseño (esta carta y las revisiones de fase), no N veces en el camino del dato. Si en el futuro se plantea un "agente BDC" tipo DriveCentric que negocie citas de forma autónoma, ESO exigiría carta propia, evaluación y gate de gasto del owner — fuera del alcance de este pilar.

---

## 9. Fases de construcción (orden, con criterio de verificación por fase)

Hay autoridad para reemplazar/reestructurar código existente. Cada fase cierra con build + test + revisión real antes de abrir la siguiente.

**F0 — Saneamiento documental y decisiones (½ día)**
Corregir `docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md` §3.10 (la cita falsa a migraciones 0033-0035); registrar en el blueprint las decisiones de esta carta (email primero, Chat.tsx fuera de nav, WhatsApp gateado a gasto).
*Verificación*: grep del blueprint sin referencias a 0033-0035 como origen CRM; PR revisada; enlace cruzado carta↔blueprint en ambos sentidos.

**F1 — Schema CRM + tenancy mínima (migraciones 0073+)**
Tablas de §5 con enums, índices de dedup, append-only guards (patrón 0035) y `crm_tenant`/`crm_user` mínimos. Resolver aquí el hueco #10 de §1: decidir el mecanismo de sesión (extensión del `require_api_key` actual a clave-por-tenant como paso mínimo viable, sin inventar un sistema de login completo prematuro).
*Verificación*: migración aplica sobre DB LIMPIA en CI (patrón seeded-snapshot ya usado en el repo) y sobre la DB viva; test de guards (INSERT/UPDATE prohibidos fallan); revisión adversarial del schema (un agente intenta violar invariantes: duplicar contact_channel, mutar consent).

**F2 — Routers CRM (contacts/deals) + registro en main.py**
`crm_contacts.py` y `crm_deals.py` con CRUD paginado, scoping por tenant en CADA query, siguiendo el patrón exacto de `entities.py` (deps, ratelimit, response helpers). Respetar el contrato que el frontend ya espera donde exista.
*Verificación*: pytest ≥80% sobre los routers nuevos (estándar del repo); curl real contra API viva; conteos API vs `psql` (protocolo §7); OpenAPI diff revisado; suite existente sin regresión (los 5 routers actuales intactos).

**F3 — Recableado frontend: Contacts, Deals, Kanban + erradicación de mocks**
Conectar las 3 páginas a los routers de F2. Eliminar `MOCK_CONTACTS`/`MOCK_DEALS`/`MOCK_BOARD` y todo patrón `?? MOCK_*`; estados vacíos/error honestos. Arreglar botones muertos (Save contact → POST real; Call/Email → `tel:`/`mailto:` como mínimo funcional). Sacar `/chat` del nav (`Shell.tsx`). Añadir probability/expected value y WIP/lead time al Kanban (criterios §4).
*Verificación*: `grep -rn "MOCK_" web/src/pages/{Contacts,Deals,Kanban}.tsx` → 0; build verde; Playwright E2E: crear contacto → visible vía GET y vía SQL; crear deal → arrastrar de columna → `crm_deal_stage_event` registrado; revisión de diseño contra el sistema visual existente (cero estilo huérfano).

**F4 — Canal email real (ingesta IMAP + envío SMTP) + Inbox vivo + SSE**
Router `crm_inbox.py` sirviendo los paths que `useInbox.ts:16-48` ya espera. Worker de ingesta IMAP (buzón/alias de leads por tenant) con parsers deterministas coches.net/Wallapop/Milanuncios (fixtures .eml reales) y auto-creación de contacto (criterio HubSpot). Envío SMTP con ACK persistido antes de pintar "enviado". SSE para refresco de bandeja. Antes de escribir el worker: auditar si `pipeline/` ya tiene scheduler durable reutilizable (hueco declarado en §5). **Gate de decisión comprar-vs-construir**: si la ingesta propia supera el presupuesto de esfuerzo, evaluar Chatwoot self-hosted como sustrato.
*Verificación*: round-trip completo en E2E contra buzón de prueba real (mandar correo → aparece conversación <60s → responder → llega al buzón receptor); doble vía §7 (Message-ID re-localizado por IMAP); parser reproducible sobre fixtures; caída del worker no rompe la API (aislamiento verificado matando el proceso en test).

**F5 — Cruce con el censo (la ventaja)**
`vehicle_ulid` en conversation/deal; chip de contexto (días en mercado, historial de precio) desde `vehicle`/`vehicle_event`/`v_canonical_vehicle`; matcher texto→inventario (LLM local como ranker, confirmación humana, §8). Si el pilar 01 ya sirve price-position, integrarlo; si no, el chip muestra SOLO lo computable hoy (first_seen, historial) — sin inventar el dato que falta.
*Verificación*: doble vía §7 (chip vs `/vehicles/{ulid}` recomputado, divergencia = build rojo); E2E: lead menciona coche → candidatos → confirmar → chip con días reales; test negativo: vehículo GONE del censo → el chip lo dice ("ya no está anunciado"), no muestra datos stale como vivos.

**F6 — Notes + Calendar persistidos + interop estándar**
`crm_note`/`crm_event` + routers; migración one-shot de localStorage con banner; export .ics (RFC 5545) y vCard (RFC 6350); handler real en "New event".
*Verificación*: .ics importado con librería independiente en CI + smoke manual en Google Calendar; notas visibles desde segundo navegador (multi-dispositivo real); localStorage ya no es fuente de verdad (grep `cardeep_notes` como escritura → 0).

**F7 — WhatsApp Business Cloud API (GATEADA — fase de gasto, requiere OK del owner)**
Verificación de negocio Meta, número, plantillas aprobadas; máquina de estados de ventana 24h (§4) sobre `last_inbound_at`; coste por mensaje (tarificación oct-2026) visible al dealer antes de enviar; enforcement de `crm_consent` bloqueando envíos de marketing sin permiso (LSSI-CE, §4).
*Verificación*: unit tests exhaustivos de la máquina de estados (dentro/fuera de ventana, reset por entrante, solo-plantilla fuera); sandbox Meta end-to-end; test legal: envío de marketing sin consentimiento → bloqueado en API (no solo en UI); revisión de seguridad (credenciales de canal = secretos, jamás en repo).

**F8 — Auditoría final y sello del pilar**
Barrido completo antes de declarar nada terminado (orden de batalla del proyecto): checklist de §4 punto por punto con evidencia (cada elemento en pantalla trazado a su criterio y a sus 2 vías de §7); regresión confirmada en los 5 routers existentes y en las páginas no-CRM del frontend; `grep -rn "MOCK_" web/src/pages/` limitado a páginas fuera del pilar o a cero; presupuestos de rendimiento del repo (CWV/bundle) medidos sobre Inbox y Kanban; actualización de `PROGRESO.md` y del blueprint con el estado real.
*Verificación*: parte de entrega honesto con cada criterio marcado verificado/no-verificado (nunca asumido); cualquier hueco restante declarado como tal en el propio parte — el pilar no se sella con ítems abiertos sin bloqueo real declarado.

Orden justificado: el schema (F1) desbloquea todo; Contacts/Deals (F2-F3) dan valor sin depender de ningún canal externo; el email (F4) es el primer canal real y el más barato; el cruce censo (F5) es la ventaja y necesita F4 vivo para tener conversaciones que enriquecer; WhatsApp (F7) es la única fase con gasto y dependencia de terceros; F8 cierra el pilar con la auditoría final.

---

## Resumen

El pilar 06 es hoy 7 páginas de atrezzo (≈3.200 líneas de frontend sin un dato real, 0 tablas, 0 routers, 0 canales) y su propio blueprint cita migraciones que no son. Cardeep no tiene ventaja estructural en mensajería —eso es infraestructura commoditizada donde Twilio/Meta/Chatwoot llevan años— y esta carta lo admite: la única superación real es enriquecer cada conversación y cada deal con el contexto vivo del censo (días en mercado, historial de precio del coche exacto por el que pregunta el lead), un dato que ningún CRM horizontal puede tener. El plan: schema `crm_*` + tenancy mínima (F1), routers y recableado sin mocks (F2-F3), email como primer canal real a coste ~€0 (F4), cruce con el censo (F5), interop estándar (F6) y WhatsApp gateado como fase de gasto (F7) — cada dato mostrado verificado por 2 vías independientes y ni un solo `?? MOCK_` superviviente.

---

## 10. Estado real de ejecución F1-F6 (2026-07-18) — [VERIFICADO salvo lo marcado ASUMIDO]

> Ejecutado en una sola sesión, en el MISMO working directory que otros 3 frentes corriendo
> en paralelo (00/01-market-intelligence terminado, 09-terminal, 07-marketing). Colisiones
> de archivo compartido detectadas y resueltas sin pérdida de trabajo ajeno — registradas
> en §10.6.

### F1 — Schema CRM [CERRADO]

Migración real consumida: **`migrations/0084_crm.sql`** (verificado `ls migrations/*.sql | sort | tail -1` inmediatamente antes de crear el archivo → `0083_vin_ref_remediation.sql`; los 3 frentes paralelos numeraron 0085-0092 encima sin colisión, verificado después). 11 tablas nuevas aplicadas a cardeep-pg viva: `crm_contact`, `crm_contact_channel`, `crm_consent`, `crm_template`, `crm_deal`, `crm_deal_stage_event`, `crm_conversation`, `crm_message`, `crm_activity`, `crm_note`, `crm_event`. Tenancy: **sin `crm_tenant`/`crm_user`** — el tenant es `entity_ulid` vía `dealer_membership` (AUTH-0, ya ejecutado por otro bloque antes de esta sesión), exactamente como manda C-3/C-4 del MASTER. Guards append-only (`cardeep_block_mutation()`) en `crm_consent`/`crm_deal_stage_event`, mismo patrón que `0005`/`0035`.

Bug real encontrado y corregido durante la ejecución: el propio comentario de cabecera de la migración contenía el literal `$$`, lo que desincronizaba el parser de `scripts/migrate.py::split_statements` (cuenta apariciones de `$$` por línea, incluso dentro de comentarios) y producía una sentencia SQL corrupta. Corregido reformulando el comentario.

Verificación: `tests/test_crm_schema.py` (12 tests) — dedup por tenant (teléfono/email), `crm_contact_channel` único (patrón Chatwoot), guards append-only bloquean UPDATE/DELETE incluso en cascada, replay del ledger de `crm_deal_stage_event` reconstruye el estado, dedup de `provider_message_id`, FKs contra el censo real (vehículo GYATA). 12/12 verdes.

Hallazgo de diseño (no bug): un guard append-only bloquea el DELETE también cuando llega por `ON DELETE CASCADE` desde el padre — mismo comportamiento ya aceptado por `fleet_ops_event` en 03-garage-fleet. Los tests dejan un rastro de auditoría permanente y etiquetado (`ZZTEST_`) para las filas con hijos guardados, documentado en el propio test.

### F2 — Routers Contacts/Deals [CERRADO]

`services/api/routers/crm_contacts.py` (CRUD completo + export vCard) y `crm_deals.py` (CRUD + `/deals/summary` + `/deals/vehicle-search`), registrados en `main.py`. Tenancy resuelta por `services/api/crm_deps.py::require_tenant` (nuevo módulo compartido): header `X-Tenant-ID` → `resolve_cluster` + verificación de `dealer_membership`, o membership más antigua como fallback — mismo patrón que `dealer_ops.py`. **Contrato de respuesta: JSON plano** (no el envelope `{ok,data,error,meta}` de los 5 routers de censo) — mismo precedente que `auth.py`, porque `useApi`/`useDeals`/`useKanban` ya esperaban esa forma exacta desde antes de que este backend existiera.

Probabilidad por defecto por etapa (carta §4): `lead=10, contacted=25, offer=50, negotiation=75, won=100, lost=0`, recalculada automáticamente en cada cambio de etapa salvo que la llamada la fije explícitamente en la misma petición (estilo Salesforce).

Verificación: `tests/test_crm_contacts_router.py` (14 tests) + `tests/test_crm_deals_router.py` (14 tests, incluye F5) contra cardeep-pg viva vía `TestClient`; aislamiento entre tenants probado con una segunda entidad real (`CDP-ES-01-7FAFJXW8`). curl real end-to-end contra una instancia uvicorn efímera (login GYATA demo → crear contacto → 409 por duplicado → crear deal → mover de etapa → `/deals/summary`). Regresión: 0 en los routers preexistentes (`test_auth_router.py`, `test_dealer_ops_router.py`, `test_arbitrage_router.py`, `test_market_router*.py`).

### F3 — Recableado frontend [CERRADO]

`Contacts.tsx`/`Deals.tsx`/`Kanban.tsx`: `MOCK_CONTACTS`/`MOCK_DEALS`/`MOCK_BOARD` eliminados por completo (`grep -rn "MOCK_" web/src/pages/{Contacts,Deals,Kanban}.tsx` → 0 coincidencias, verificado). "Save contact" hace POST real y no cierra el modal hasta 201 (409 se muestra inline). Call/Email del `ContactDrawer` navegan a `tel:`/`mailto:` reales. "New deal" abre un modal real con selector de contacto + buscador de vehículo (F5) + precio + prioridad. `/chat` retirado del nav (`Shell.tsx`) y de las rutas (`App.tsx`) — `Chat.tsx` queda parkeado sin ruta, tal como ordena la carta. Kanban/Deals muestran `expectedValue`/`avgLeadTimeDays` servidos por `/deals/summary` (un solo cálculo, no una segunda fórmula cliente).

Build verificado: `tsc --noEmit` limpio + `vite build` verde (bundle generado, warnings de tamaño de chunk preexistentes y no introducidos por este pilar).

### F4 — Canal email real [CERRADO]

`services/api/routers/crm_inbox.py` sirviendo exactamente los paths que `useInbox.ts` ya esperaba (`GET /inbox`, `GET /inbox/{id}`, `POST /inbox/{id}/reply`, `PATCH /inbox/{id}`) + `GET /inbox/stream` (SSE). `services/crm/email_send.py` (SMTP, stdlib puro) y `services/crm/email_ingest.py` (IMAP, stdlib puro) + `services/crm/lead_parsers.py` (parsers deterministas coches.net/Wallapop/Milanuncios + fallback genérico, portal detectado por dominio del remitente).

Bug real encontrado y corregido: `/inbox/stream` estaba declarado DESPUÉS de `/inbox/{conversation_ulid}` en el router, así que FastAPI capturaba `"stream"` como `conversation_ulid` antes de llegar nunca a la ruta SSE (mismo tipo de bug que `/deals/summary` ya evitaba). Corregido reordenando la declaración — mismo patrón aplicado consistentemente en `crm_deals.py`.

**Hueco declarado, no maquillado**: no existe una cuenta de correo real con credenciales en este entorno, así que el round-trip verdadero IMAP servidor-real → worker → SMTP servidor-real → buzón receptor NO se ha ejecutado. Lo que SÍ está verificado: (a) la lógica de negocio de ingesta (`ingest_message`) contra la DB viva — contacto nuevo, reutilización de contacto/conversación existente, idempotencia por `Message-ID`; (b) la orquestación IMAP (`run_once`) contra un `imaplib.IMAP4_SSL` mockeado — login/select/search/fetch/store llamados correctamente; (c) el envío SMTP (`send_email`) contra un cliente SMTP stub inyectado — construcción del mensaje, threading `In-Reply-To`, y que TODO fallo (host no configurado, conexión rechazada, destinatario rechazado) levanta `EmailSendError` y jamás persiste un mensaje como enviado; (d) el router completo vía `TestClient` + DB real, incluyendo el camino sin SMTP configurado devolviendo 502 "No se pudo enviar" (nunca un check falso) y el camino feliz con `send_email` sustituido. Los parsers de coches.net/Wallapop/Milanuncios están etiquetados `[ASUMIDO]` en su propio docstring: modelados sobre el formato públicamente conocido de cada portal, sin una muestra `.eml` real capturada disponible en este entorno — se degradan honestamente al parser genérico ante cualquier no-coincidencia, nunca fabrican un dato.

Verificación: `tests/test_lead_parsers.py` (15), `tests/test_email_send.py` (7), `tests/test_email_ingest.py` (5), `tests/test_crm_inbox_router.py` (10) — 37/37 verdes. curl real: login → seed de conversación → `GET /inbox` → `GET /inbox/{id}` → `PATCH` → SSE real verificado con `curl -N` recibiendo un evento `data: {"type":"inbox_updated",...}` en vivo, y rechazo 401 con token inválido.

### F5 — Cruce con el censo [CERRADO]

`services/api/vehicle_context.py`: `compute_vehicle_context` (detalle completo + historial de precio) y `batch_vehicle_summaries` (N vehículos en una sola query, sin N+1) — **mismo cálculo** que `vehicles.py` sirve en `/vehicles/{ulid}` (`days_in_stock = now() - vehicle.first_seen`, idéntico en ambos caminos). Wireado en `crm_deals.py` (`vehicleContext` en cada Deal) y `crm_inbox.py` (`vehicleContext` en cada Conversation). Matcher texto→inventario: `GET /deals/vehicle-search` — SQL determinista (ILIKE sobre make/model/title) acotado al cluster COMPLETO del dealer (`TenantContext.member_ulids`, extendido para esto), nunca LLM (declarado explícitamente: sin runtime de LLM local disponible en este entorno, sustituido por matching determinista — desviación declarada de la §8 original, no maquillada).

Frontend: `types.ts` extendido con `VehicleContext`; chip de "días en tu stock"/precio en `Deals.tsx` (modal de detalle), `Kanban.tsx` (tarjetas) e `Inbox.tsx` (lista de conversaciones y cabecera del hilo) — en los tres sitios, honesto: si `vehicleContext` es `null` no se pinta nada, y si `stillListed=false` se muestra "ya no está anunciado" en vez de datos obsoletos como vivos. `NewDealModal` reemplaza el campo de texto libre "Vehicle ULID" por un buscador real con candidatos y confirmación de un clic.

Doble vía de verificación (protocolo §7): `tests/test_crm_deals_router.py::test_days_in_stock_matches_vehicles_endpoint_independently` calcula `daysInStock` por DOS caminos de código independientes (el chip vía `crm_deals.py` y una recomputación en Python a partir de `first_seen` leído de `GET /vehicles/{ulid}`) y afirma que coinciden.

### F6 — Notes + Calendar + interop [CERRADO]

`services/api/routers/crm_notes.py` (CRUD completo) y `crm_calendar.py` (CRUD + `GET /calendar/events/{id}/ics`) + export vCard en `crm_contacts.py` (`GET /contacts/{id}/vcard`). Serialización RFC 5545/RFC 6350 hand-rolled en `services/api/ics_vcard.py` (stdlib puro, CRLF + folding + escapado literal de ambos RFCs) — **verificada con librerías independientes que el propio módulo nunca importa** (`icalendar`/`vobject`, añadidas a `requirements-dev.txt`), exactamente el protocolo que exige la carta §7.

`Notes.tsx`: localStorage retirado como fuente de verdad (`grep -n "localStorage.setItem" web/src/pages/Notes.tsx` → 0 coincidencias) y sustituido por `hooks/useNotes.ts`. Migración one-shot con banner: si el servidor no tiene notas y `localStorage['cardeep_notes']` sí, se ofrece migrar con un botón — nunca automático, nunca silencioso — y solo entonces se limpia el storage local. `Calendar.tsx`: reescrito completo sobre `hooks/useCalendarEvents.ts`, "New event" abre un modal real, cada evento tiene botón de descarga `.ics` real (fetch autenticado + blob, ya que `<a href>` no puede llevar `Authorization`) y botón de borrado real.

Verificación: `tests/test_ics_vcard.py` (9 tests, parseo independiente) + `tests/test_crm_notes_calendar_router.py` (9 tests) — 18/18 verdes. curl real: crear nota → listar → export .ics parseado por `icalendar` en vivo → export vCard con teléfono ya normalizado a E.164 (`+34655443322`).

### 10.5 Regresión final

Suite completa CRM (F1-F6, 8 archivos de test nuevos, ~130 tests) + regresión de los routers preexistentes (`auth`, `dealer_ops`, `arbitrage`, `market*`) ejecutada varias veces durante la sesión, siempre en verde. Un falso-positivo detectado y corregido en el propio proceso de verificación: un `DiskFullError` transitorio de Postgres (presión de memoria compartida del contenedor bajo la carga simultánea de los 4 frentes paralelos, no un bug de este pilar) que desapareció al reintentar — documentado en vez de ignorado.

### 10.6 Colisiones de archivo compartido detectadas

- `services/api/main.py`: tocado en paralelo por 07-marketing (router `marketing`) y 09-terminal (router `terminal`) mientras esta sesión registraba `crm_contacts`/`crm_deals`/`crm_inbox`/`crm_notes`/`crm_calendar`. Cada edición se aplicó por sección (import ordenado + una línea `include_router` cada vez), releyendo el archivo antes de cada escritura — coexisten sin corrupción, verificado (`python -c "from services.api.main import app"` en verde tras cada ronda).
- `web/src/layout/Shell.tsx`: 00-marketplace-engine añadió el grupo "MOTOR" en paralelo a la retirada de `/chat` de este pilar. Coexisten sin conflicto.
- `web/src/App.tsx`: 07-marketing añadió la ruta `/marketing` en paralelo a la retirada de `/chat`. Coexisten sin conflicto.
- `web/src/pages/Assistant.tsx`: **no es propiedad de este pilar** (fuera de la tabla de ownership CRM) — detectado con un error de sintaxis transitorio (`esbuild`/`tsc`) durante `npm run build` mientras otro frente lo editaba en vivo; NO tocado por esta sesión. `git status` confirma `M` (modificado, no comiteado) por esa otra sesión. Declarado aquí, no resuelto por mí — fuera de mandato.

### 10.7 Huecos declarados (no bloqueantes, no maquillados)

1. **F4 round-trip real**: sin credenciales de un buzón IMAP/SMTP real en este entorno, el camino servidor-real→servidor-real no se ha ejecutado; la lógica está verificada por las tres vías posibles sin acceso externo (unit, mock de protocolo, integración contra DB real).
2. **Parsers de portal**: modelados sobre formato públicamente conocido, no sobre `.eml` capturados reales — se degradan honestamente, nunca fabrican.
3. **Matcher F5**: determinista (SQL), no el ranker LLM local que la carta §8 proponía como v1 — sin runtime de LLM local disponible en este entorno; el resultado es igualmente honesto (nunca auto-asigna, siempre requiere confirmación de un clic) pero con menos tolerancia a errores tipográficos que un ranker semántico.
4. **F7 (WhatsApp)**: no ejecutado — gateado explícitamente a fase de gasto por la propia carta, fuera del mandato F1-F6 de esta sesión.
5. **F8 (auditoría final del pilar completo)**: no ejecutado — fuera del mandato F1-F6 de esta sesión; esta §10 cubre la verificación de cada fase individualmente, no el barrido de cierre de pilar completo que F8 exige (CWV/bundle medidos específicamente sobre Inbox/Kanban, etc.).

### 10.8 Archivos nuevos/tocados (resumen)

Backend: `migrations/0084_crm.sql`, `services/api/crm_deps.py`, `services/api/vehicle_context.py`, `services/api/ics_vcard.py`, `services/api/routers/{crm_contacts,crm_deals,crm_inbox,crm_notes,crm_calendar}.py`, `services/crm/{__init__,email_send,email_ingest,lead_parsers}.py`, `services/api/main.py` (registro de routers). Tests: `tests/test_{crm_schema,lead_parsers,email_send,email_ingest,ics_vcard,crm_contacts_router,crm_deals_router,crm_inbox_router,crm_notes_calendar_router}.py`. `requirements-dev.txt` (+icalendar, +vobject). Frontend: `web/src/types.ts` (extendido), `web/src/hooks/{useContacts,useNotes,useCalendarEvents}.ts` (nuevos), `web/src/hooks/{useDeals,useInbox}.ts` (extendidos), `web/src/pages/{Contacts,Deals,Kanban,Inbox,Notes,Calendar}.tsx` (recableados), `web/src/layout/Shell.tsx` + `web/src/App.tsx` (retirada de `/chat`).
