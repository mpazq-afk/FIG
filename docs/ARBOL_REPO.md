# Arbol del repo, anotado

> Extraido de `CLAUDE.md` el 2026-09-02 para que no se cargue en cada sesion.
> Este es el repo ESPEJO: la fuente de verdad de casi todo esto es `fig-web`.
> Ojo: describe el arbol de `fig-web`. El espejo publica MENOS cosas
> (sin `miembros/`, sin `fiw/`, sin las herramientas de datos y video).

## Estructura del repo

```
/
├── index.html              ← sitio principal FIG (hero, áreas, torneo resumen, historia, equipo, eventos resumen)
├── eventos/index.html      ← bitácora de actividades (torneos, visitas, charlas, comunidad)
├── fiw/index.html           ← página de FEN Investment Woman (paleta propia, editable)
├── valuation/index.html     ← página del área Valuation (paleta estándar; responsables + sección de Torneo del área que se activa con datos/valuation.json)
├── portafolio/index.html    ← página del área Portafolio (2026-09-01; YA NO es la plantilla de valuation/: hero con el plano riesgo/retorno del torneo, cinta de datos vivos, tablero del corte y barra de asignación de los 100 puntos — ver la tanda del 2026-09-01 (3))
├── trading/index.html       ← página del área Trading (2026-08-31; MISMA plantilla que valuation/. Su sección de Torneo va `hidden` con `torneo.activo:false`: el desk aún no tiene torneo propio, y por eso tampoco hay ítem "Torneo" en su nav — al encenderlo hay que devolverlo)
├── torneo/index.html        ← ranking oficial del Torneo Portafolio 2026 (con trayectoria por equipo)
├── torneo/pantalla.html      ← PANTALLA para las TV de la facultad (1920x1080, bucle, se alimenta sola de torneo.json)
├── miembros/index.html      ← LA MESA: directiva, organigrama por desk, buscador "Terminal FIG" y ficha por persona (se alimenta de datos/miembros.json)
├── postula/index.html       ← formulario de postulación al club
├── juego/index.html          ← "El Rally del Toro": juego de espera (runner con el toro; vender = asegurar puntaje)
├── desafio/index.html        ← "Desafío FIG": trivia de finanzas (banco en datos/preguntas/, validar con validar_preguntas.py)
├── en/index.html              ← one-pager en INGLÉS para partners internacionales (única página en inglés del sitio)
├── generar_torneo.py        ← Excel ranking_ordenado → datos/torneo.json (mantiene historial semanal)
├── completar_metricas_historial.py ← INJERTO QUIRÚRGICO: rellena métricas faltantes en semanas ya publicadas del historial, SIN regenerar el JSON (usar esto, nunca `--excels`, para no borrar los integrantes)
├── grabar_pantalla_facultad_1_capturar.js ← Paso 1/2 para grabar torneo/pantalla-facultad.html: Chrome headless por CDP crudo (sin Playwright, sin instalar nada), captura fotograma a fotograma a frames/*.png. Necesita un server local corriendo antes (ver su cabecera). Detalle completo más abajo, sección "Pixelación al proyectar"
├── grabar_pantalla_facultad_2_codificar.py ← Paso 2/2: arma el MP4 final desde frames/*.png con PyAV, uno por uno (nunca todos en memoria)
├── incorporar_congelados.py ← **DORMIDO desde el 2026-08-26** (la directiva eliminó en definitiva a los 5 equipos; ver el final de la fila de `torneo/index.html`). Hace no-op si `datos/equipos_congelados.json` está vacío. Cuando tenía equipos: los reinsertaba en `torneo.json` recalculando el puntaje de TODOS vía percentil continuo (réplica de `scoring.py` del repo torneo-bloomberg-oficial), a correr SIEMPRE después de `generar_torneo.py`. Se deja en el repo por si se decide congelar a otro equipo eliminado en el futuro
├── generar_miembros.py      ← club.json (directiva) + Excel del Drive → datos/miembros.json; cruza solo los resultados de torneo y las actividades
├── PLANILLA_MIEMBROS_FIG.md  ← qué columnas debe tener la planilla de miembros del Drive y qué NUNCA se publica (léelo antes de tocar la sección de Miembros)
├── generar_tabla.py         ← datos/torneo.json → datos/torneo-tabla.json (el mismo sin `historial`, 27,7→7,1 KB comprimido). Lo pide primero torneo/index.html para pintar la tabla; el historial se trae aparte
├── generar_paginas_equipo.py ← datos/torneo.json → torneo/e/<id>.html, una micro-página por equipo SOLO para que el link tenga vista previa propia al compartirlo (redirige al ranking real)
├── generar_og_equipos.js     ← Node + Chrome por CDP crudo: og/equipo-<id>.jpg (1200x627), la imagen de esa vista previa. Reusa `drawLi`, la MISMA tarjeta de LinkedIn que ya ofrece la página. Opcional, ver la nota de PESO en su cabecera
├── verificar_paginas.js      ← CHEQUEO EN NAVEGADOR: abre las 15 paginas en Chrome (CDP crudo) y falla si alguna tira un error de consola o pide un archivo que no existe. OJO: los 404 de `fotos/` y `logos/industria/` son el sondeo de deteccion funcionando, no errores
├── generar_sitemap.py        ← sitemap.xml + robots.txt (deja fuera `torneo/e/`, las pantallas y las guias internas)
├── sincronizar_espejo.py     ← copia al espejo lo que corresponde; `index.html` y `MAPA_CONTENIDO_FIG.html` NUNCA se pisan (difieren a proposito). Nunca borra nada alla
├── descargar_fuentes.py      ← baja las 3 familias de Google y arma `fuentes/fig.css` (solo subconjuntos latin/latin-ext)
├── usar_fuentes_locales.py   ← apunta las paginas a `fuentes/fig.css`; NO toca el <link> de la tarjeta descargable de `torneo/index.html`
├── verificar_sitio.py        ← CHEQUEO ANTES DE PUBLICAR: JSON que parsean, derivados al día (torneo-tabla, torneo/e/, og/), menciones de "N equipos" escritas a mano vs el JSON, y creadores que calcen con la directiva. `--arreglar` regenera los derivados
├── generar_ics.py           ← datos/eventos.json → eventos/fig.ics (calendario iCal; correr tras editar eventos)
├── optimizar_fotos.py       ← comprime fotos/ automáticamente (máx 2000px, JPG 78%) — correr tras agregar fotos
├── validar_preguntas.py     ← barrera de calidad del banco de preguntas del Desafío FIG
├── HOJA_DE_RUTA_FIG.md      ← LISTA MAESTRA: backlog priorizado + protocolo de continuidad
├── MAPA_CONTENIDO_FIG.html  ← guía visual para Francisco: dónde subir fotos y editar texto de cada página (abrir con doble clic)
├── GUIA_DRIVE_FIG.html       ← guía para el equipo: estructura de la carpeta del Drive, dónde van las fotos, pasos para crear un evento (abrir con doble clic)
├── GUIA_DRIVE_FIG.jpg         ← infografía resumen de la guía anterior (para compartir rápido, ej. WhatsApp)
├── logos/                   ← logos oficiales bajados del Drive (FIG oro/blanco/navy, FEN, Itaú, BlackRock)
│   └── industria/            ← logos de empresas para "FIG en la industria" (ver LEEME.txt de la carpeta)
├── fuentes/                 ← GENERADA por descargar_fuentes.py: las tipografias autoalojadas (.woff2 + fig.css + LICENCIAS.txt). No editar a mano
├── sitemap.xml, robots.txt  ← GENERADOS por generar_sitemap.py
├── og/                      ← GENERADAS por generar_og_equipos.js: una imagen de vista previa por equipo. No editar a mano
├── torneo/e/                ← GENERADAS por generar_paginas_equipo.py: una micro-página por equipo. No editar a mano (tiene su LEEME.txt)
├── datos/
│   ├── torneo-tabla.json     ← DERIVADO de torneo.json por generar_tabla.py (sin `historial`). No editar a mano; si queda viejo la página lo detecta y se corrige sola, y verificar_sitio.py falla
│   ├── club.json             ← personas, eventos resumen, historia, URLs del sitio principal. Desde el 2026-08-27 trae también `torneo.creadores`: la lista EXPLÍCITA de quiénes crearon el Torneo Portafolio 2026, que alimenta la sección `#creadores` de `torneo/index.html` (solo nombre + aporte; el cargo, el LinkedIn y la foto se resuelven en vivo contra `personas.directiva`)
│   ├── cv_procesados.json    ← manifiesto anti-relectura de CV del Drive (fileId+modifiedTime, evita reprocesar los que no cambiaron)
│   ├── eventos.json           ← lista completa de eventos (bitácora); campo opcional `area` conecta un evento con la sección "Actividades" de su área (hoy solo valuation)
│   ├── mercado.json            ← calendario de mercado (RPM/IPoM del Banco Central + FOMC de la Fed); fechas oficiales, se actualizan a mano una vez por semestre — se muestran en la misma línea de tiempo que los hitos del torneo y los eventos del club
│   ├── linea_tiempo.json       ← hitos estructurales del Torneo (rebalanceos, cierres, final); se combina con eventos.json en la línea de tiempo de index.html y eventos/index.html — editable desde el Drive (`Linea_Tiempo_Hitos_Torneo` en `00_MAESTRO`)
│   ├── fiw.json                ← textos y equipo de FEN Investment Woman
│   ├── valuation.json           ← textos, responsables y datos del Torneo de Valuation (pegar formUrl del Forms para activar inscripciones)
│   ├── portafolio.json          ← lo mismo para portafolio/index.html
│   ├── trading.json             ← lo mismo para trading/index.html (`torneo.activo:false` hasta que el desk tenga uno; el `_como_editar` explica cómo encenderlo)
│   ├── miembros.json             ← GENERADO por generar_miembros.py (no editar a mano): personas del club con ticker, área, nivel del organigrama y sus resultados de torneo cruzados
│   ├── (miembros.demo.json)        ← BORRADO el 2026-08-28, ya no está en el repo: la base real está cargada. Era el modo `?demo=1` (personas reales con cargos SUPUESTOS + personas que NO EXISTEN, `demo:true`). Se regenera con `python generar_miembros.py --demo` cuando haga falta; mientras no exista, `?demo=1` cae a la base real
│   ├── equipos_congelados.json   ← **VACÍO desde el 2026-08-26** (`{"equipos": []}`): los 5 equipos que estuvieron "en espera" 23→26-ago fueron eliminados en definitiva. Antes traía sus 5 métricas crudas FIJAS (semana 14) + `historial_previo` (semanas 5-14); ese contenido está en git (commit `c7c4f98` y el estado previo a la eliminación). Repoblarlo solo si se congela a otro equipo (ver `incorporar_congelados.py`)
│   └── torneo.json.ejemplo      ← ESQUEMA del ranking (ver "Pendiente" abajo — aún no existe torneo.json real)
├── fotos/
│   ├── eventos/<carpeta-evento>/  ← 1.jpg, 2.jpg, 3.jpg… por evento (numeradas, sin saltos)
│   ├── directiva/                  ← retratos de cofundadores: <nombre-slug>.jpg (ver LEEME.txt de la carpeta)
│   ├── miembros/                    ← retratos del resto del club: <id>.jpg (ver LEEME.txt). La página busca acá primero y en directiva/ después, así que a un directivo NO se le copia la foto dos veces
│   ├── fiw/                        ← 1.jpg, 2.jpg, 3.jpg… de la comunidad FIW
│   └── valuation/                   ← 1.jpg, 2.jpg, 3.jpg… para la tira de fondo del hero (aún vacía)
├── LEEME_PAGINAS.md          ← documentación de cómo se conectan las páginas nuevas
├── IDEAS_FIG.md               ← ideas de una sesión (rápidas)
├── IDEAS_GRAN_ESCALA_FIG.md    ← ideas de orquestación/pipeline (para Claude Code)
├── MAPEO_DRIVE_FIG.md           ← mapeo completo de la carpeta de Google Drive del club (solo lectura)
└── ACTIVIDADES_FIG.md            ← bitácora de actividades históricas extraída del Drive
```

Todas las páginas comparten: navy `#0A1128` + oro `#D4AF37`, tipografías
Playfair Display + Inter + IBM Plex Mono, reveals on-scroll, y respeto
total a `prefers-reduced-motion` (el cursor circular personalizado que
seguía al mouse se eliminó el 2026-08-02, pedido de Francisco). La página
`fiw/index.html` es la única con paleta propia (oro rosa, variables `--acc*`
al inicio de su `<style>`) — no tocar esos 4 valores sin pedirlo
explícitamente a Francisco, son la identidad visual de esa área.

