# Motor de antidetección Tier-1 (P2)

Implementación del motor de antidetección agresivo diseñado en el Plano Maestro V2 §3
(`docs/MASTER_PLAN_CARDEEP_V2_2026-06-20.md`). Eleva el Tier-0 de un único fingerprint
estático (`chrome131`) a un motor en cascada con rotación real, detección semántica de
bloqueo y escalado a navegador real con reuso de cookies.

## Arquitectura — cascada de 3 capas

```
fetch_text(url, tier=0)
   │
   ├─ Tier-0  curl_cffi, fingerprint COHERENTE rotado del pool (fingerprints.py)
   │     └─ ban_detector.classify(status, body, headers)
   │            OK        → devuelve contenido
   │            NOT_FOUND → FetchError (no escala; la URL ya no existe)
   │            CHALLENGE/BANNED:
   │                 1) rota a OTRO fingerprint real coherente y reintenta
   │                 2) si sigue bloqueado y allow_tier1_escalation → Tier-1
   │                 3) si escalado off → FetchError (fail-loud, nunca el interstitial)
   │
   └─ Tier-1  navegador real (tier1/browser.py)
         nodriver (primario)  ó  camoufox (secundario)
         resuelve el challenge UNA vez → mintea cookie de clearance
         → inyecta la cookie en la sesión curl_cffi (mismo UA) → sirve barato
```

## Componentes (solo archivos de este motor)

| Archivo | Rol |
|---|---|
| `fingerprints.py` | Pool de fingerprints reales recientes + rotación coherente (anti-JA3-random). |
| `ban_detector.py` | Clasificación semántica de respuesta (OK/CHALLENGE/BANNED/NOT_FOUND). Markers CF/DataDome/Akamai/PerimeterX. |
| `fetch.py` | Motor en cascada. **Interfaz pública sin cambios** (`FetchEngine`, `fetch_text`, `FetchError`). |
| `tier1/browser.py` | Capa de navegador real: nodriver/camoufox, patrón cookie-reuse. |
| `tier1/__init__.py` | Reexporta `solve_challenge`, `BrowserResult`, `Tier1Error`. |

Tests: `tests/test_fingerprints.py`, `tests/test_ban_detector.py`, `tests/test_fetch_cascade.py`.

## ⚠️ DECISIÓN DE LICENCIA — nodriver es AGPL-3.0 (del usuario)

**`nodriver` está licenciado bajo AGPL-3.0 (copyleft de red).** Si cardeep expone un
**servicio en red** que use nodriver, la AGPL-3.0 puede **obligar a publicar el código
derivado** que ofrece ese servicio. Esto NO se oculta: es una decisión del propietario.

- **Por defecto** el motor usa nodriver (es el único con **0 bloqueos** en el benchmark
  independiente de Ian L. Paterson, 651 verdictos, 2026-05-13) porque la tarea pide la
  antidetección más agresiva.
- **Para evitar la AGPL** basta construir el motor con `tier1_engine="camoufox"`
  (Camoufox es MPL-2.0, mucho más permisiva) o ponerlo como default cambiando
  `_TIER1_ENGINE` en `fetch.py`.

La elección final (asumir AGPL en la API viva vs. usar Camoufox por defecto) es del
usuario. El código deja ambas vías abiertas y marcadas.

## Coste cero hoy — proxy PENDIENTE DE CREDENCIAL

El reuso de cookies de clearance está atado a la **IP que resolvió el challenge**. Para
targets Tier-1 reales con WAF que filtra por IP (DataDome/Akamai en vivo) hace falta un
**proxy residencial ES sticky**. Hoy **no hay credencial de pago wired** → el navegador
resuelve sobre la IP del host (coste cero). El parámetro `proxy=` está cableado de punta a
punta (`FetchEngine(proxy=...)` → `solve_challenge(proxy=...)`) y marcado
`PENDING_CREDENTIAL_PROXY`; se activa pasando `"http://user:pass@host:port"` cuando se
provisione, sin tocar el resto del motor.

## Compatibilidad con los 37 conectores

La interfaz de la que dependen los conectores es **idéntica**:
- `FetchEngine()` / `FetchEngine(polite_min=, polite_max=)` siguen funcionando.
- `engine.fetch_text(url, *, tier=0, headers=None) -> str` sin cambios de firma.
- `fetch_text(...)` módulo y `FetchError` sin cambios.
- Atributos `impersonate`, `last_status`, `fetch_count` preservados (+ nuevos
  `last_tier`, `last_verdict`).

Diferencia de comportamiento (mejora, no ruptura): un challenge/ban detectado ahora
**falla en voz alta** (`FetchError`) en vez de devolver silenciosamente el cuerpo del
interstitial como si fuera inventario. El escalado a navegador es **opt-in** por motor
(`allow_tier1_escalation=True`) o explícito (`tier>=1`), así que ningún conector que no lo
pida cambia su semántica.

## Uso

```python
from pipeline.engine.fetch import FetchEngine

# Tier-0 con rotación (un fingerprint coherente por sesión):
eng = FetchEngine()
html = eng.fetch_text("https://www.autocasion.com/...")

# Pinned (reproducir una receta):
eng = FetchEngine(impersonate="chrome146")

# Con escalado automático a navegador ante bloqueo:
eng = FetchEngine(allow_tier1_escalation=True)            # nodriver (AGPL) por defecto
eng = FetchEngine(allow_tier1_escalation=True, tier1_engine="camoufox")  # MPL-2.0

# Forzar Tier-1 explícito (resuelve challenge en navegador y sirve por cookie-reuse):
html = eng.fetch_text("https://walled.example/", tier=1)
```

## Verificación piloto

`scripts/pilot_tier1.py` ejecuta el motor sobre 1-2 entidades reales y reporta, por cada
una: status final, tier que resolvió, fingerprint usado y veredicto del detector. Usa
muestras pequeñas (recipe-first) y no persiste nada.
