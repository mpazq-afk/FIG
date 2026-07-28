# CLAUDE.md — Contexto del proyecto Web FIG

> Este archivo lo lee Claude Code automáticamente al abrir esta carpeta.
> No lo borres ni lo muevas. Mantenlo actualizado: cuando algo cambie de
> estado (una página deja de ser demo, se conecta un enlace, etc.), edita
> la sección correspondiente en vez de dejar que quede desactualizado.

## Qué es esto

El ecosistema web de **FEN Investment Group (FIG)**, club de inversiones de
la FEN — Universidad de Chile. Un conjunto de páginas HTML autocontenidas
(sin build steps, sin framework, compatibles con GitHub Pages) que comparten
un mismo sistema de diseño y se alimentan de archivos JSON como capa de
datos, para que el contenido se edite sin tocar código.

**Filosofía no negociable de este proyecto:** Excel/Drive es la fuente de
verdad → un script Python lo convierte a JSON → las páginas HTML leen ese
JSON y se renderizan solas. Nunca hardcodear datos que van a cambiar
(rankings, personas, fotos, textos) directamente en el HTML/JS de una
página. Si algo cambia seguido, va en un `.json` bajo `datos/`.

## Estructura del repo

```
/
├── index.html              ← sitio principal FIG (hero, áreas, torneo resumen, historia, equipo, eventos resumen)
├── eventos/index.html      ← bitácora de actividades (torneos, visitas, charlas, comunidad)
├── fiw/index.html           ← página de FEN Investment Woman (paleta propia, editable)
├── valuation/index.html     ← página del área Valuation (paleta estándar; responsables + sección de Torneo del área que se activa con datos/valuation.json)
├── torneo/index.html        ← ranking oficial del Torneo Portafolio 2026 (con trayectoria por equipo)
├── postula/index.html       ← formulario de postulación al club
├── juego/index.html          ← "El Rally del Toro": juego de espera (runner con el toro; vender = asegurar puntaje)
├── desafio/index.html        ← "Desafío FIG": trivia de finanzas (banco en datos/preguntas/, validar con validar_preguntas.py)
├── en/index.html              ← one-pager en INGLÉS para partners internacionales (única página en inglés del sitio)
├── generar_torneo.py        ← Excel ranking_ordenado → datos/torneo.json (mantiene historial semanal)
├── generar_ics.py           ← datos/eventos.json → eventos/fig.ics (calendario iCal; correr tras editar eventos)
├── optimizar_fotos.py       ← comprime fotos/ automáticamente (máx 2000px, JPG 78%) — correr tras agregar fotos
├── validar_preguntas.py     ← barrera de calidad del banco de preguntas del Desafío FIG
├── HOJA_DE_RUTA_FIG.md      ← LISTA MAESTRA: backlog priorizado + protocolo de continuidad
├── MAPA_CONTENIDO_FIG.html  ← guía visual para Francisco: dónde subir fotos y editar texto de cada página (abrir con doble clic)
├── logos/                   ← logos oficiales bajados del Drive (FIG oro/blanco/navy, Itaú, BlackRock)
│   └── industria/            ← logos de empresas para "FIG en la industria" (ver LEEME.txt de la carpeta)
├── datos/
│   ├── club.json             ← personas, eventos resumen, historia, URLs del sitio principal
│   ├── cv_procesados.json    ← manifiesto anti-relectura de CV del Drive (fileId+modifiedTime, evita reprocesar los que no cambiaron)
│   ├── eventos.json           ← lista completa de eventos (bitácora)
│   ├── fiw.json                ← textos y equipo de FEN Investment Woman
│   ├── valuation.json           ← textos, responsables y datos del Torneo de Valuation (pegar formUrl del Forms para activar inscripciones)
│   └── torneo.json.ejemplo      ← ESQUEMA del ranking (ver "Pendiente" abajo — aún no existe torneo.json real)
├── fotos/
│   ├── eventos/<carpeta-evento>/  ← 1.jpg, 2.jpg, 3.jpg… por evento (numeradas, sin saltos)
│   ├── directiva/                  ← retratos de cofundadores: <nombre-slug>.jpg (ver LEEME.txt de la carpeta)
│   ├── fiw/                        ← 1.jpg, 2.jpg, 3.jpg… de la comunidad FIW
│   └── valuation/                   ← 1.jpg, 2.jpg, 3.jpg… para la tira de fondo del hero (aún vacía)
├── LEEME_PAGINAS.md          ← documentación de cómo se conectan las páginas nuevas
├── IDEAS_FIG.md               ← ideas de una sesión (rápidas)
├── IDEAS_GRAN_ESCALA_FIG.md    ← ideas de orquestación/pipeline (para Claude Code)
├── MAPEO_DRIVE_FIG.md           ← mapeo completo de la carpeta de Google Drive del club (solo lectura)
└── ACTIVIDADES_FIG.md            ← bitácora de actividades históricas extraída del Drive
```

Todas las páginas comparten: navy `#0A1128` + oro `#D4AF37`, tipografías
Playfair Display + Inter + IBM Plex Mono, cursor crosshair personalizado,
reveals on-scroll, y respeto total a `prefers-reduced-motion`. La página
`fiw/index.html` es la única con paleta propia (oro rosa, variables `--acc*`
al inicio de su `<style>`) — no tocar esos 4 valores sin pedirlo
explícitamente a Francisco, son la identidad visual de esa área.

## Estado actual de cada pieza (revisar y actualizar esta sección seguido)

| Pieza | Estado | Detalle |
|---|---|---|
| `index.html` | ✅ Producción | Sitio principal completo. Orden de secciones (2026-07-19, pedido de Francisco): inicio → nosotros → **eventos** → áreas → torneo → historia → equipo. Nav con ese mismo orden + enlace **FIG Woman** + menú **"Jugar ▾"** (desplegable hover/focus con El Rally del Toro y el Desafío FIG; en móvil van como enlaces directos). Fondos claros SIN cuadrícula gris (se eliminó el patrón de líneas de 72px, solo queda el glow radial dorado). Ticker bursátil al pie con el top 5 del torneo — aparece solo cuando exista `datos/torneo.json` real (hoy oculto). Footer enlaza `en/index.html`. **Nav actualizado (2026-07-24, pedido de Francisco)**: se agregó un enlace directo **Valuation** (nav desktop y menú móvil) y "Eventos" ahora lleva a la página completa `eventos/index.html` en vez de anclar a `#eventos` de esta misma página. **Expediente de cofundadores**: clic en cualquier tarjeta de §Nosotros abre un overlay con ficha completa (bio + trayectoria desde `perfil` en `club.json`, foto grande si existe en `fotos/directiva/<slug>.jpg` — ver `fotos/directiva/LEEME.txt` —, monograma dorado si no), flechas ←/→ para recorrer el grupo, ✕/Esc para cerrar, navegable por teclado. **Miniaturas con foto real** en la grilla de §Nosotros (mismo `probeFoto()`, ahora en alcance global). **"FIG en la industria"** agrupada por empresa (no por persona): logo real si existe `logos/industria/<slug>.*` (ver `logos/industria/LEEME.txt`) o chip de iniciales si no, tooltip al hover/foco con quiénes de FIG han pasado por esa empresa enlazados a su LinkedIn. **Tira de fotos reales de eventos en movimiento** detrás del hero y de §Historia (`.photo-marquee`, detectadas solas desde `datos/eventos.json` + `fotos/eventos/`, opacidad baja para no tapar el texto, respeta reduced-motion) — no está en §Áreas porque esa sección ya tiene sus propias fotos y se veía recargado. **"Universidad de Chile" quitado del texto visible (2026-07-24, pedido de Francisco)**: se borraron las 4 apariciones visibles (subtítulo de marca en el nav, kicker del hero, párrafo de marca del footer y línea del footer inferior); quedan intactas las menciones en `<meta>` (no se muestran en la página) y la del bio de Benjamín Disi (dato personal de su propio magíster, no de marca). **Logos de "FIG en la industria" completados (2026-07-24)**: subidos por el equipo al Drive y bajados a `logos/industria/` — ahora hay logo real para Itaú (reemplazado, más nítido), CODELCO, MoonValley Capital, LarraínVial, HSBC, BCI Seguros y Next Consultores (7 de 8 empresas); CMF (Victoria Espinoza) sigue sin logo subido, muestra el chip de iniciales de respaldo. Se descartó un archivo `ASAS.png` subido en la misma carpeta del Drive porque no corresponde a ninguna empresa de `personas.industria` — pendiente preguntarle a Francisco a qué corresponde |
| `eventos/index.html` | ✅ Producción | 9 eventos reales con resúmenes completos en `datos/eventos.json`; filtros por tipo Y año; botón de calendario `fig.ics` (regenerar con `generar_ics.py`); modo proyección `?pantalla=1` (fotos fullscreen para TVs, enlazado en el footer) |
| `en/index.html` | ✅ Producción | One-pager en inglés para partners (BlackRock, bancos): áreas + torneo con solo datos verificados. Única página del sitio con texto en inglés — es su propósito |
| `fiw/index.html` | ⚠️ Placeholder + **enlaces ocultos temporalmente** | Estructura y datos completos (ahora con 3 co-fundadoras: Delia Avilán, Gabriela Domínguez y Victoria Espinoza), pero **colores de marca aún no confirmados** por el equipo FIW — usa un oro rosa provisional. Sin fotos en `fotos/fiw/` todavía. **2026-07-24, pedido de Francisco**: se ocultaron (comentario `<!-- FIW_TEMP_OCULTO -->`, NO se borró nada) todos los botones/enlaces que llevan a esta página — nav desktop y móvil de `index.html`, la tarjeta del desk 04 en §Áreas, el footer de `index.html`, y los nav de `404.html`, `postula/index.html` y `eventos/index.html` — porque el área se publica recién en una etapa posterior al lanzamiento de mañana. La página en sí sigue intacta y accesible por URL directa; para reactivarla, buscar `FIW_TEMP_OCULTO` en esos 5 archivos y descomentar |
| `valuation/index.html` | ✅ Producción | Página del área Valuation (2026-07-21, pedido de Francisco). Paleta estándar navy+oro (no propia). Secciones: hero → qué es Valuation → cómo trabajamos (3 pilares research/valorización/tesis) → **Torneo del área** → responsables → CTA. Los 3 **responsables** (Jhosep García, Benjamín Sáez Molina, Samuel Rodríguez Arnolds) salen de `datos/valuation.json` con foto real detectada sola desde `fotos/directiva/<slug>.jpg`, rol y LinkedIn. **Torneo activado (2026-07-24)**: "Valuation Challenge 2026" con Itaú (Corporate & Investment Banking) y BDO (Deal Advisory) como partners — `torneo.formUrl` ya tiene el Google Form real, así que el botón "Inscríbete →" está activo; datos reales de formato (caso de M&A + defensa ante comité), equipos (2-3 personas desde 2° año), fechas de inscripción (18-26 jul) y competencia (3-31 ago), y premios (1°: práctica Itaú + premio tecnológico, 2°: práctica BDO). Falta `torneo.basesUrl` (aparece "Ver las bases" solo cuando se llene). Enlazada desde el desk "VAL · Valuation" de §Áreas en `index.html` y ahora también desde el nav principal (2026-07-24). **Logo corregido (2026-07-24)**: preloader y nav usaban por error `fig-blanco.png` (el logo blanco de FIW); como esta página usa la paleta estándar navy+oro, se cambió a `fig-oro.png` como en el resto del sitio. **Tira de fotos en movimiento en el hero** (2026-07-22, pedido de Francisco: "igual que se ve en la página principal") — mismo `.photo-marquee` que el index, pero leyendo de `fotos/valuation/1.jpg, 2.jpg…` (numeradas, sin saltos, ver `fotos/valuation/LEEME.txt`) en vez de las carpetas de eventos; mientras la carpeta esté vacía el hero se ve igual que antes, sin errores |
| `torneo/index.html` | ✅ Datos reales cargados, con historial completo de 7 semanas | `datos/torneo.json` con 59 equipos reales. La página salió del modo DEMO sola. Overlay con gráfico de 3 líneas (retorno equipo/promedio/ACWI — el ACWI queda vacío por ahora, no hay benchmark en ningún Excel visto todavía). Tarjetas: Feed PNG, **Story PNG**, LinkedIn PNG, HTML y **videos animados** Feed/Story con intro (logo→nombre→colaboradores→ficha). En celular, los botones de tarjetas **comparten directo con el panel nativo del sistema** (`navigator.share`, Instagram queda a un toque) en vez de forzar una descarga; en iPhone la tarjeta Story además intenta abrir Instagram directo en el compositor de Historias (truco de portapapeles + `instagram-stories://`, con fallback automático). Grabación de video a 24fps con progreso visible en el botón. Logos de colaboradores en hero y tarjetas. La línea temporal de §Metodología integra las actividades del club desde `datos/eventos.json` (tags por tipo + descripción al hover, tarea #16 ✅). **Historial completo reconstruido (2026-07-24)**: Francisco compartió los 7 Excels semanales oficiales (`Excel_Oficial_FIG_PORT_2026_2026-06-12.xlsx` hasta `...2026-07-24.xlsx`, uno por corte); `generar_torneo.py` ganó un modo nuevo `--excels a.xlsx,b.xlsx,...` (ver P0-2 y la sección del script abajo) que lee la fecha de cada nombre de archivo, saca posición/puntos/métricas de cada semana desde su propio `ranking_ordenado`/`Tabla`/`puntos`, y el retorno since-inception de cada semana desde la hoja `Retornos por corte` del corte más reciente (ya trae la serie completa). El número de semana real (5 a 11, no 1 a 7) se calcula con la misma fórmula que usa `torneo/index.html` (`semanaHoy()`, desde el inicio real del torneo el 11 de mayo) — de paso corrigió una semana mal etiquetada como "1" que en realidad era la semana 6. Con las 7 semanas reales, el gráfico de 3 líneas y los indicadores de cambio de posición (▲▼) ahora muestran datos reales en vez del placeholder/guión que se agregó horas antes para el caso de una sola semana (`chartPlaceholder()` sigue en el código, solo que ya no se activa — vuelve a activarse solo si algún día se publica una semana sin historial previo) |
| Enlaces cruzados | ✅ Conectados | `index.html` ya enlaza a `eventos/`, `fiw/`, `torneo/` y `postula/` (CTAs, footer, `CONFIG.urls` y `datos/club.json`) |
| `generar_torneo.py` | ✅ Probado con el Excel real | Lee `ranking_ordenado` (+ `Tabla`/`puntos` como respaldo para métricas más completas que trae el Excel oficial) + Excel de inscripciones → escribe `datos/torneo.json`, conserva el `historial` semanal y calcula `delta`. Ya soporta el formato ancho real del Excel de inscripciones (columnas Líder/Int2/Int3 Nombre+LinkedIn) además del formato largo original. Solo copia `nombre` + `linkedin` de cada integrante (nunca correo/carrera/ingreso, regla dura de PII). Modo `--demo` disponible. **Modo nuevo `--excels a.xlsx,b.xlsx,...` (2026-07-24)**: reconstruye el `historial` completo de una sola pasada a partir de varios cortes semanales del Excel oficial — saca la fecha de cada nombre de archivo, el snapshot semana a semana de cada `ranking_ordenado` propio, y el retorno since-inception de la hoja `Retornos por corte` del corte más reciente (esa hoja ya trae la serie completa hasta esa fecha, no hace falta pegar los `ret` uno por uno). Calcula el número de semana real con la misma fórmula que usa la página (desde el inicio del torneo el 11 de mayo), así que no requiere pasarle `--semana`/`--corte` a mano. Uso: `python3 generar_torneo.py --excels sem1.xlsx,sem2.xlsx,... --inscripciones insc.xlsx` |
| `postula/index.html` | ✅ Endpoint conectado (sin verificar en vivo) | Formulario de postulación completo; envía (con `tipo:"postulacion"`) a `config.figEndpoint` (el Apps Script COMPARTIDO del sitio) de `datos/club.json` — la URL ya está pegada (2026-07-18), pero nadie ha confirmado aún que una postulación real llegue a la planilla (este entorno no puede alcanzar `script.google.com`); Francisco debe probarlo una vez |
| `desafio/index.html` | ✅ Funcional (banco real) | Trivia: modo desafío (secuencial, puntaje decae, malas descuentan, revisión con explicaciones, áreas fuerte/débil, ranking local) y modo estudio (por tema o ramo, sin reloj). Banco en `datos/preguntas/` — **348 preguntas reales en 12 temas y 5 ramos** (ahora incluye `finanzas-ii` y `apf`) extraídas del material de finanzas del Drive (P1.5 Q2, lotes 1-31; validar siempre con `validar_preguntas.py`). **Auditoría de calidad completa (2026-07-23)**: las 348 preguntas fueron revisadas por precisión técnica/coherencia (no solo esquema JSON) — se corrigió 1 error numérico real, 1 bug de metadata (`ramo` mal etiquetado), 2 reclasificaciones de tema y ~35 mejoras de estilo/distractores; nadie encontró alternativas "correctas" objetivamente erróneas, así que el contenido de fondo ya era sólido. **Dificultad subida (2026-07-20)**: `armarDesafio()` prioriza preguntas de dificultad 2-3 (solo cae a dificultad 1 si el tema no tiene suficientes), el puntaje decae más rápido (20s→14s) y la penalización por respuesta mala subió de 25 a 32 pts; la fase de lectura también se acortó un poco. Idea pendiente de Francisco: selector de dificultad (1/2/3) en el juego — el campo `dificultad` ya existe en todas las preguntas |
| `juego/index.html` | ✅ Funcional | "El Rally del Toro": runner canvas con un **toro dorado dibujado a mano** (silueta embistiendo inspirada en el logo, galope de 4 patas, cola y cuernos animados — ya no se usa la imagen del logo en el canvas); velas rojas, **vela gigante (flash crash)**, burbujas y **pozo del SII** (un vacío en el suelo con las letras "SII" — hay que saltarlo; si caes, overlay "Te fuiste en cana" con la moraleja de integridad, raro ~5.5%) como obstáculos; VENDER asegura el puntaje y ofrece **descargar una tarjeta PNG 1080×1350** del resultado (monto, % ganancia, el toro, cita del club) — filosofía "saber cuándo salir". **Dificultad rebalanceada (2026-07-22, pedido de Francisco: "al llegar a 3x ya no es posible avanzar")**: la velocidad ahora tiene MESETA (`speed=6+min(elapsed,34000)/10000`, techo ~9.4) y el ritmo de spawn un piso de 640ms — lo único que sigue subiendo es el `mult` de recompensa, así el juego siempre es jugable y la tensión es "cuánto aguantas". **Evento "posición en corto"**: cada ~18s (luego cada 16-24s) el mundo se da vuelta con un aviso previo (banner) — el toro corre por el TECHO (gravedad invertida, `mode="short"`) y hay que **CUBRIR (saltar ↓)** las alzas verdes que cuelgan del techo, con un botón distinto; a los ~6.5s vuelve a normal. Controles: SALTAR (Espacio/↑) en largo, CUBRIR (↓/K) en corto; en móvil el tap del lienzo hace la acción del modo; dos botones en pantalla muestran cuál está activo. **Panel lateral "Tu rendimiento"** (`.side`): curva de equity de la corrida en vivo + línea punteada del siguiente en la tabla con "faltan USD X para pasar a [nombre]" y "Vas #N en vivo" (se calcula contra `RANK`, el ranking local o global). Ranking: lee `config.figEndpoint` de `datos/club.json` (el Apps Script COMPARTIDO del sitio) y muestra "Ranking global"; si el endpoint está vacío o el fetch falla, cae automático a localStorage por navegador. **Endpoint ya conectado (2026-07-18)**, pendiente de que Francisco confirme que una corrida real llega a la pestaña `Ranking` de la planilla. Nota: hay un espejo de estado (`window.__rallyState`) que solo se activa con el flag de prueba `window.__rallyFast` — inerte en producción |
| Fotos de eventos | ⚠️ Parcial | 7 de 9 eventos con fotos curadas y comprimidas (ver `HOJA_DE_RUTA_FIG.md` tarea #5). Faltan `torneo-portafolio-2026` y `charla-analisis-tecnico-2025` (sin carpeta en el Drive) y más variedad en `lanzamiento-club-2025` (fotos Samsung de 7-9 MB, por encima del límite del conector de Drive) |
| Fotos de la directiva | ✅ Completa (15/15) | `fotos/directiva/` tiene foto real de las 15 personas de `personas.directiva` (Francisco subió las 4 que faltaban — Agustín Arriagada, Juan José Limari, Delia Avilán y Gabriela Domínguez — el 2026-07-24, y Victoria Espinoza llegó con foto real desde el inicio). Fotos de baja resolución (ej. Agustín, ~96×96 desde LinkedIn) se reescalaron con Lanczos + realce de nitidez, mismo tratamiento que se le dio a Manuel Paz. Notas: Samuel Rodríguez Arnolds se sumó a `personas.directiva` el 2026-07-18 (co-encargado de Valuation junto a Jhosep, confirmado por Francisco); Delia Avilán, Gabriela Domínguez y Victoria Espinoza son co-fundadoras de FEN Investment Woman (confirmado por Francisco el 2026-07-24, tras detectar que los 3 CV se autodescribían con el mismo rol) |
| Fotos de Valuation | ⚠️ Vacía (2026-07-22) | `fotos/valuation/` creada con `LEEME.txt`, lista para recibir fotos numeradas (tira de fondo del hero). Carpeta paralela en Drive (`06_Valuation/Fotos`, con su propio LEEME) para que el equipo del área las suba primero — pasan al repo cuando Francisco pida la revisión |

## Lo que YA existe fuera de esta carpeta (contexto crítico, no reinventar)

- **Ya existe un sitio FIG distinto, en producción real**, en el Drive
  (`WEB/fen-investments-web/`), con URLs reales confirmadas:
  - LinkedIn: `https://www.linkedin.com/company/fen-investment-group`
  - Instagram: `https://www.instagram.com/fen.investment.group/`
  - Torneo (GitHub Pages): `https://feninvestmentgroup.com/torneoportafolio2026/`
  - Form de postulación (Apps Script): endpoint documentado en `MAPEO_DRIVE_FIG.md`
  Antes de inventar una URL nueva para algo, revisar si ya existe una real
  en ese mapeo.
- **Ya existe una app real del torneo** (`torneo-app`, Vite+TS+Tailwind) y
  un **generador de overlay de video para OBS** (`ranking-video`) que hoy
  lee un CSV público de Google Sheets — candidato a conectarse a
  `datos/torneo.json` en vez de al CSV (ver `IDEAS_GRAN_ESCALA_FIG.md` §6).
- El repo de GitHub Pages del torneo vive bajo el usuario `mpazq-afk`.
- Todo el detalle de assets, logos, ids de Drive y hallazgos está en
  `MAPEO_DRIVE_FIG.md` — léelo antes de pedir a Francisco un logo o una URL
  que probablemente ya está mapeada ahí.

## Cómo se edita cada tipo de contenido (para explicarle esto a Francisco, no lo hagas tú directamente salvo que te lo pida)

- **Texto/personas/eventos** → Francisco edita un Excel → un script
  `generar_*.py` (algunos existen, otros hay que crearlos) produce el JSON
  correspondiente en `datos/`.
- **Fotos** → se suben directo a la carpeta correcta en `fotos/`, numeradas
  `1.jpg, 2.jpg, 3.jpg…` sin saltos. Las páginas las detectan solas
  (`probeFotos()` en el JS de cada página prueba extensiones y números
  hasta fallar). No requiere tocar ningún JSON.
- **Ranking del torneo** → sale del pipeline semanal ya existente
  (`ordenar_tmsg.py` → `reconstruir_nav.py` → `build_outputs.py`) — falta
  el último eslabón `generar_torneo.py` que traduzca `ranking_ordenado` al
  esquema de `datos/torneo.json.ejemplo`.

## Pendiente / próximos pasos conocidos

**La lista maestra vive en `HOJA_DE_RUTA_FIG.md`** (backlog priorizado,
decisiones tomadas, protocolo de continuidad entre sesiones/modelos —
leerla SIEMPRE al retomar el proyecto y actualizarla al terminar).
Resumen de bloqueadores:

1. ✅ **Endpoint COMPARTIDO del sitio** — Francisco lo creó y desplegó
   (2026-07-18), URL ya pegada en `config.figEndpoint` de `datos/club.json`.
   Pendiente: que confirme en vivo que las 3 pestañas reciben datos (ver
   `HOJA_DE_RUTA_FIG.md` P0-1).
2. ✅ **Primer `datos/torneo.json` real** (2026-07-20) — generado con
   `generar_torneo.py` desde el Excel Oficial FIG (snapshot al 19·jun·2026,
   no la versión más nueva del torneo, pero Francisco pidió usarlo para
   poder probar todo el flujo) + LinkedIn de "Copia de Inscripciones
   Torneo Portafolio 2026.xlsx". Pendiente: reemplazar por el corte más
   reciente cuando Francisco tenga el Excel actualizado (mismo comando, ver
   `HOJA_DE_RUTA_FIG.md` P0-2 para el detalle técnico de qué cambió en el
   script).
3. **Colores oficiales de FIW** con Delia → variables `--acc*` (P0-3).
4. **URLs de `bases` y `contacto`** en `CONFIG.urls` / `club.json` (P0-4).
5. **Fotos reales** en `fotos/eventos/*` y `fotos/fiw/` (P0-5, solo Francisco).

## Reglas duras (no romper)

- **Google Drive es de solo lectura por defecto** (instrucción directa de
  Francisco, actualizada 2026-07-20). Excepción acotada:
  - Se puede **crear** un archivo/carpeta nuevo en Drive únicamente si
    Francisco lo pide explícitamente en ese momento y confirma antes de
    que se ejecute (no crear nada "por si acaso" ni de forma proactiva).
  - Una vez creado por una IA, ese mismo archivo **sí se puede editar**
    después sin pedir permiso de nuevo para cada edición.
  - **Nunca** editar ni borrar un archivo/carpeta que ya existía en el
    Drive de Francisco antes de esta sesión (o que no fue creado por una
    IA) — eso sigue siendo estrictamente solo lectura.
  - Después de crear o editar algo en Drive, **avisarle a Francisco** qué
    se hizo (qué archivo, dónde, y un resumen del contenido/cambio).
  - Si hace falta leer un archivo del Drive que no fue creado por una IA,
    sigue aplicando lo de siempre: pedírselo a él o dejar instrucciones
    claras de qué bajar y dónde ponerlo.
- **Nunca** commitear datos personales sensibles más allá de nombre + rol +
  LinkedIn público (eso sí está aprobado para el torneo).
- Mantener las páginas **sin build step**: HTML/CSS/JS planos, sin npm ni
  bundler, porque así es como se despliegan a GitHub Pages hoy.
- Todo texto de cara al usuario va en **español** (única excepción:
  `en/index.html`, el brief para partners internacionales — ese va en inglés
  a propósito).
- Las 9 páginas llevan al pie del footer el crédito **"Creado por
  Francisco Valenzuela y Manuel Paz"** (en inglés en `en/index.html`:
  "Made by... and..."), cada nombre enlazado a su LinkedIn real. Al
  agregar una página nueva, copiar ese `<span>` del footer de cualquier
  página existente.
- Las 9 páginas llevan un **beacon de métricas anónimas** (sin cookies:
  página + fecha + origen) que envía con `tipo:"visita"` al mismo
  `config.figEndpoint` compartido, y queda inerte mientras esté vacío.
  Al agregar una página nueva, copiar el snippet del final de cualquier
  página existente.
- **Un solo Apps Script para todo el sitio** (`config.figEndpoint` en
  `club.json`): postulaciones, ranking del Rally del Toro y métricas de
  visitas comparten el mismo Web App y la misma planilla (3 pestañas). No
  crear un endpoint nuevo por feature — sumar un `tipo` más al `doPost`/
  `doGet` existente (código completo en `HOJA_DE_RUTA_FIG.md`, P0-1).
- Antes de escribir un script nuevo `generar_X.py`, revisar si el patrón ya
  existe para otro dato (todos siguen la misma forma: leer Excel → validar
  → volcar JSON con el esquema documentado en el propio archivo o en su
  `.ejemplo`).
