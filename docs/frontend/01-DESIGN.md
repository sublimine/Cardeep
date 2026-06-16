# CARDEEP Frontend — Síntesis de auditoría + Dirección de diseño

> Fuente: workflow `cardeep-competitor-ux-audit` (10 plataformas, teardown estructurado).
> Output íntegro: tasks/wxhwop5f9.output. Pinterest del owner: tras login (inaccesible) → carta blanca.

## Lo que la auditoría confirmó (consenso — patrones a ADOPTAR)
Trust-signals presentes en los líderes; se replican (elevados, no copiados):
1. **Price-rating badge** (Buen/Justo/Caro precio vs mercado) — mobile.de, AutoScout, AutoTrader, cars.com, CarGurus. Reduce fricción, construye confianza. **→ Es el puente natural a la capa de inteligencia (Indicata/GANVAM): la valoración hecha visible.**
2. **Filtros sidebar-izquierda siempre visibles** (desktop) — coches.net/milanuncios/wallapop/coches.com. El usuario ES está entrenado; desviarse crea fricción.
3. **Hit-count en vivo por faceta** ("Ver 1.243") — mobile.de, cars.com. Mata el dead-end.
4. **Tipo de vendedor** Particular/Profesional — faceta de alta señal del mercado ES.
5. **Make→Model dependiente** (modelo se activa al elegir marca) — wallapop.
6. **Cuota mensual** (financiación) en card + filtro — coches.net/coches.com (el comprador piensa en €/mes).
7. **Etiqueta medioambiental DGT** — España, legalmente resonante.
8. **CTA + precio sticky** (rail derecho) en la página de detalle — mobile.de, cars.com.
9. **Specs en una línea con separadores** (Combustible · Cambio · CV · Año · Km) en card — wallapop, denso+escaneable.
10. **Badge precio-rebajado / freshness** ("Precio rebajado", "online desde") — milanuncios.

Paletas de la competencia (todas **fondo blanco**): naranja (mobile.de #FF5E00, milanuncios), azul (AutoScout #1166A8, coches.com, AutoTrader #0534FF), rojo/coral (coches.net #E60E27, CarGurus), violeta (cars.com #8136B2), teal (wallapop #00C5AC).

## La oportunidad → Dirección CARDEEP
Como **todos son blancos, densos y se parecen**, CARDEEP se diferencia por contraste: **dark luxury / "command-center de inteligencia de mercado"**. Base casi-negra → el **mapa 3D de España y los datos brillan**; acento eléctrico propio; price-rating semántico como identidad visible (y puente a la inteligencia). Premium, ownable, 3D-first. NO clonamos a nadie.

### Paleta (design tokens)
```
Base/ink     #0A0E17   (fondo — deja brillar el 3D)
Surface      #121826 · #1A2234 · #232C42   (paneles, cards, elevación)
Línea/borde  #2A3450 (sutil) · #3A4straße… → #38445E
Texto        #EAEEF7 (primario) · #9AA6BE (secundario) · #5C6883 (terciario)
Acento (marca/acción)  #35E0D0  →  hover #5BEADD  (cian eléctrico — "señal de datos", ownable)
Acento-2 (profundidad) #6C5CE7  (violeta-índigo para foco/3D rim, no como CTA)
Price-rating (semántico, el ADN-inteligencia):
   buen precio   #22C55E
   precio justo  #F5B33C
   caro          #F0556B
Mapa: rampa de cobertura  GAP #F0556B → PARCIAL #F5B33C → SELLADO #35E0D0 (sobre ink)
```

### Tipografía
- Display/hero: una grotesca con carácter (p.ej. **Clash Display** / **Satoshi** variable) — peso alto, escala grande (el precio y los titulares son anclas visuales, lección de la auditoría).
- UI/cuerpo: **Inter** (o Geist) — legibilidad densa.
- Datos/monoespacio (cifras, cdp_code): **Geist Mono** / JetBrains Mono — las cifras alinean (terminal de inteligencia).
- Escala fluida `clamp()`; el precio en extra-bold oversized (ancla, como toda la competencia).

### Layout (adaptado, no copiado)
- **Landing**: héroe = mapa 3D de España (provincias extruidas por cobertura) + barra de búsqueda flotante. Stats vivas (1,7M coches · 40k dealers · 52 prov) animadas.
- **Explore**: split — sidebar-izq de filtros (facetas de la auditoría: marca→modelo, precio €/mes, año, km, combustible, cambio, tipo-vendedor, DGT, provincia) + grid de cards a la derecha; hit-counts en vivo. Toggle mapa↔grid.
- **Card**: foto + precio (oversized) + price-rating badge + specs-una-línea + dealer + freshness; hover/focus diseñados.
- **Detalle dealer** (`/dealer/{cdp}`): identidad + inventario (su API individual) + delta/historial + mapa de su ubicación.
- **Detalle vehículo** (`/vehicle/{ulid}`): galería + specs + precio + price-rating + CTA sticky derecha + historial Δ.
- Responsive 320→1920; sidebar → drawer en móvil; reduced-motion respetado.
