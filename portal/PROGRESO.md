# Portal — progreso (Claude Design → standalone HTML)

Fuente: claude.ai/design **"Cardeep"** (`cd99ab8f-851c-47e9-90ee-da85cae146df`) · destino: `cardeep/portal/*.html`.
Método: strip DC→HTML plano vía `_build/strip_dc.py` (ver README). Preview: `python -m http.server 8777`.

## ESTADO: 10/10 pantallas VIVAS — matriz 200, CERO 404
| # | Pantalla | Archivo | Verificación |
|---|----------|---------|--------------|
| 1 | Landing (insignia) | `index.html` | ✅ render Playwright (hero glass + filtro funcional) |
| 2 | Analítica | `analitica.html` | ✅ render Playwright (KPIs/gauge/área/tabla) |
| 3 | Resumen | `dashboard.html` | ✅ render Playwright (KPIs/chart/equipo) |
| 4 | Dealers | `dealers.html` | ✅ matriz 200 (hero estático) |
| 5 | Dossier | `dossier.html` | ✅ render Playwright (**coche 3D** + asistente) |
| 6 | Finanzas | `finanzas.html` | ✅ matriz 200 (cashflow/P&L) |
| 7 | Garaje 360° | `garaje.html` | ✅ render Playwright (tabla + simulador reprecio) |
| 8 | Inteligencia | `inteligencia.html` | ✅ matriz 200 (residual/sweet-spot) |
| 9 | Marketplace | `marketplace.html` | ✅ render Playwright (**motor de filtros** + 9 fichas) |
| 10| Plano 3D | `plano.html` | ✅ render Playwright (**garaje 3D** WebGL) |

Las 2 pantallas 3D y el motor de filtros corren con **0 errores de consola**. `index/analitica` se portaron a mano
(equivalentes al stripper); las otras 8 vía `_build/strip_dc.py` (re-ejecutable).

## RECONSTRUCCIÓN BYTE-PERFECTA + ASSETS REALES (2026-06-29, RESUELTO)
El owner aportó el ZIP `Cardeep Claude Design.zip` (`design_handoff_cardeep/`). Se **reconstruyeron los 10
`.html` desde los `.dc.html` byte-perfectos** del ZIP vía `_build/strip_dc.py` (cero transcripción a mano → se
eliminó toda deriva; p.ej. la `Analitica.dc.html` real = 26.675 B). **Assets reales colocados** en la ruta exacta
que referencia cada pantalla (leídas del fuente, no de memoria):
- `uploads/hero-video.mp4` (8,2 MB) — vídeo hero de la landing ✅
- `uploads/car-suv-white.png` · `car-hatch-silver.png` · `car-estate-blue.png` (~2,5 MB c/u) — fichas Marketplace ✅
- `assets/dash-shot.png` (24 KB) — mockup Dealers ✅ · `assets/cd-icon.png` (173 KB) — logo ✅
Verificado en navegador: Landing con vídeo, Marketplace con coches reales, ambas 3D — **0 errores de consola**.
Nota: el límite de `DesignSync get_file` (256 KiB → truncaba binarios) queda obsoleto al traer el ZIP local.
No usados por ninguna pantalla (en el ZIP, ignorados): `cardeep-car-topdown.png`, `hero-kids-light.png`.
Re-sync futuro: nuevo ZIP → copiar `.dc.html` a `_build/src/` + assets → `python _build/strip_dc.py`.

## SIGUIENTE FASE (cuando quieras)
1. Cablear datos vivos: `web/src/api/cardeep.ts` → API `:8090` (`/stats`, `/geo/seal`, `/geo/{prov}/entities`,
   `/entities/{cdp}/inventory`) para sustituir los números prototipo del diseño.
2. Promover `portal/` a frontend canónico y retirar el `web/` sintético (cliente censo muerto + landing con cifras
   fabricadas).
3. Re-sync de diseño: cuando cambies algo en claude.ai/design, re-`get_file` la pantalla a `_build/src/` y
   `python _build/strip_dc.py`.
