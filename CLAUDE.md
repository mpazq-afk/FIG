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

## Estado actual de cada pieza (revisar y actualizar esta sección seguido)

| Pieza | Estado | Detalle |
|---|---|---|
| `index.html` | ✅ Producción | Sitio principal completo. Orden de secciones (2026-07-19, pedido de Francisco): inicio → nosotros → **eventos** → áreas → torneo → historia → equipo. Nav con ese mismo orden + enlace **FIG Woman** + menú **"Jugar ▾"** (desplegable hover/focus con El Rally del Toro y el Desafío FIG; en móvil van como enlaces directos). Fondos claros SIN cuadrícula gris (se eliminó el patrón de líneas de 72px, solo queda el glow radial dorado). Ticker bursátil al pie con el top 5 del torneo — aparece solo cuando exista `datos/torneo.json` real (hoy oculto). Footer enlaza `en/index.html`. **Nav actualizado (2026-07-24, pedido de Francisco)**: se agregó un enlace directo **Valuation** (nav desktop y menú móvil) y "Eventos" ahora lleva a la página completa `eventos/index.html` en vez de anclar a `#eventos` de esta misma página. **Expediente de cofundadores**: clic en cualquier tarjeta de §Nosotros abre un overlay con ficha completa (bio + trayectoria desde `perfil` en `club.json`, foto grande si existe en `fotos/directiva/<slug>.jpg` — ver `fotos/directiva/LEEME.txt` —, monograma dorado si no), flechas ←/→ para recorrer el grupo, ✕/Esc para cerrar, navegable por teclado. **Miniaturas con foto real** en la grilla de §Nosotros (mismo `probeFoto()`, ahora en alcance global). **"FIG en la industria"** agrupada por empresa (no por persona): logo real si existe `logos/industria/<slug>.*` (ver `logos/industria/LEEME.txt`) o chip de iniciales si no, tooltip al hover/foco con quiénes de FIG han pasado por esa empresa enlazados a su LinkedIn. **Tira de fotos reales de eventos en movimiento** detrás del hero y de §Historia (`.photo-marquee`, detectadas solas desde `datos/eventos.json` + `fotos/eventos/`, opacidad baja para no tapar el texto, respeta reduced-motion) — no está en §Áreas porque esa sección ya tiene sus propias fotos y se veía recargado. **"Universidad de Chile" quitado del texto visible (2026-07-24, pedido de Francisco)**: se borraron las 4 apariciones visibles (subtítulo de marca en el nav, kicker del hero, párrafo de marca del footer y línea del footer inferior); quedan intactas las menciones en `<meta>` (no se muestran en la página) y la del bio de Benjamín Disi (dato personal de su propio magíster, no de marca). **Logos de "FIG en la industria" completados (2026-07-24)**: subidos por el equipo al Drive y bajados a `logos/industria/` — ahora hay logo real para Itaú (reemplazado, más nítido), CODELCO, MoonValley Capital, LarraínVial, HSBC, BCI Seguros y Next Consultores (7 de 8 empresas); CMF (Victoria Espinoza) sigue sin logo subido, muestra el chip de iniciales de respaldo. Se descartó un archivo `ASAS.png` subido en la misma carpeta del Drive porque no corresponde a ninguna empresa de `personas.industria` — pendiente preguntarle a Francisco a qué corresponde. **Correcciones menores (2026-08-02, pedido de Francisco)**: el contador de equipos del torneo en el hero y las menciones de "63 equipos"/"USD 630M simulados en total" quedaban desactualizadas frente al dato real (59 equipos, `datos/torneo.json`) — corregido en `index.html`, `datos/club.json`, `eventos/index.html`, `datos/eventos.json`, `torneo/index.html` y `en/index.html`. Se eliminó el círculo dorado que seguía al mouse (`#cursorDot`/`#cursorRing`, CSS+JS) en las 5 páginas que lo tenían (`index.html`, `eventos/index.html`, `fiw/index.html`, `torneo/index.html`, `valuation/index.html`) — pedido explícito de Francisco, sin reemplazo. El rol de David González Cañón se corrigió de "Director · Valuation" a "Fundador · Valuation" (solo tiene el cargo de fundador, no de director) en `datos/club.json` y en el fallback JS + la ficha estática de §Nosotros de `index.html`. No se agregó FIG Woman a esa actualización (petición explícita). **2026-08-03, pedido de Francisco**: (1) enlace a FIG Woman **deshabilitado de nuevo** — se restauró el comentario `FIW_TEMP_OCULTO` en los 4 archivos que lo tenían reactivado (`index.html`, `postula/index.html`, `eventos/index.html`, `404.html`); (2) el rol de David González Cañón pasó de "Fundador · Valuation" a solo **"Fundador"** (sin distintivo de área) en `datos/club.json` y en `index.html`; (3) el antiguo "Eje de hitos" del torneo (`.axis-wrap`) se **reconstruyó** manteniendo el formato horizontal con scroll y el marcador "HOY" que avanza solo con el tiempo (interpolado entre los dos puntos vecinos según su fecha real, igual que el original), pero ahora integra también las actividades del club: combina los hitos estructurales de `datos/linea_tiempo.json` (nuevo archivo, editable desde el Drive — ver `Linea_Tiempo_Hitos_Torneo` en `00_MAESTRO`) con `datos/eventos.json`, ordenados cronológicamente. Cada punto (`.ax`) se agranda al pasar el cursor (o tocar) y muestra una tarjeta flotante con su resumen (`#axPop`, `position:fixed` para no recortarse con el scroll del eje); clic navega directo (un hito de torneo va a `torneo/index.html#metodologia`, una actividad va a `eventos/index.html#<id>`). El marcador "HOY" en cambio es `position:absolute` dentro del propio eje (no `fixed`) para que se recorte junto con el scroll horizontal en vez de "flotar" fuera de la tarjeta — bug real detectado y corregido con Playwright antes de mergear. Misma línea de tiempo (versión completa) agregada también en `eventos/index.html`, donde el clic sobre una actividad abre su ficha localmente (reusa `openEvento()`) en vez de recargar la página. **2026-08-05, pedido de Francisco**: el eje ahora arranca con scroll horizontal centrado en el punto HOY por defecto (antes arrancaba en el extremo izquierdo, con el marcador fuera de vista si había muchos hitos pasados) — mismo cambio en las dos páginas. **Calendario de mercado en la línea de tiempo + enlace de bases arreglado (2026-08-05)**: la línea de tiempo ahora combina TRES fuentes (`datos/linea_tiempo.json` + `datos/eventos.json` + el nuevo `datos/mercado.json`); los eventos de mercado se distinguen en **azul** (`#3C6DA8` sobre fondo claro, `#7BA7DE` sobre oscuro — mismo azul que ya usa el benchmark ACWI en `torneo/index.html`), llevan el tag `MERCADO` y al hacer clic abren la **fuente oficial** en otra pestaña (bcentral.cl / federalreserve.gov) en vez de navegar dentro del sitio. Además se arregló el botón **"Descargar las bases"** de §Torneo, que apuntaba a `#` desde siempre: `CONFIG.urls.bases` y `config.urls.bases` de `club.json` ahora tienen el PDF real que ya se usaba en `torneo/index.html`. **Sigue pendiente `contacto`** (aún en `#`, falta que Francisco defina correo o formulario). **Conteo de directores corregido (2026-08-05, pedido de Francisco: "no somos 18")**: el número real es **15** (mismo total que `datos/club.json`, que ya lo tenía correcto en su historia); se corrigieron 6 menciones desactualizadas de "18" en `index.html` (hero__meta, stat contador `data-target`, párrafo de §Nosotros, tarjeta "Capítulo II" de §Historia — tanto la estática como el fallback JS `CLUB_DATA`). De paso se eliminó el tile "+N Directiva completa" (`p-card--more`) del final de la grilla de §Nosotros en las 3 copias (`datos/club.json`, HTML estático, fallback JS): con los 15 perfiles reales ya cargados de punta a punta, ese chip decía "Los 18 perfiles se cargan... al conectar el pipeline", una promesa de "más gente por venir" que ya no es cierta — se sacó en vez de solo corregirle el número, para no dejar un dato igual de falso con otra cifra |
| `eventos/index.html` | ✅ Producción | 9 eventos reales con resúmenes completos en `datos/eventos.json`; filtros por tipo Y año; botón de calendario `fig.ics` (regenerar con `generar_ics.py`); modo proyección `?pantalla=1` (fotos fullscreen para TVs, enlazado en el footer). **2026-08-03, pedido de Francisco**: nueva sección "El torneo y la vida del club" (línea de tiempo completa, entre el hero y los filtros — ver detalle en la fila de `index.html`, mismo dato y motor). Nuevo filtro **Pasados / Próximos** (junto a los de tipo y año) que compara la fecha de cada evento contra hoy — el Torneo Portafolio 2026 (`live:true`) siempre cae en "Próximos" mientras esté en curso, sin importar su fecha de inicio. Las tarjetas ahora muestran un chip **PRÓXIMO** cuando corresponde |
| `en/index.html` | ✅ Producción | One-pager en inglés para partners (BlackRock, bancos): áreas + torneo con solo datos verificados. Única página del sitio con texto en inglés — es su propósito |
| `fiw/index.html` | ⚠️ Placeholder, **enlaces deshabilitados de nuevo** | Estructura y datos completos (3 co-fundadoras: Delia Avilán, Gabriela Domínguez y Victoria Espinoza), pero **colores de marca aún no confirmados** por el equipo FIW — usa un oro rosa provisional. Sin fotos en `fotos/fiw/` todavía. La página en sí sigue intacta y accesible por URL directa. **2026-08-03, pedido de Francisco**: se deshabilitaron de nuevo los 9 enlaces (nav desktop/móvil + desk 04 de §Áreas + footer de `index.html`, nav de `postula/index.html`, nav desktop/móvil de `eventos/index.html`, nav desktop/móvil de `404.html`) envolviéndolos otra vez en el comentario `FIW_TEMP_OCULTO` en los 4 archivos — mismo mecanismo que la vez anterior (2026-07-27), solo que en sentido inverso. Pendiente: colores de marca (P0-3), fotos reales, y que Francisco confirme cuándo volver a reactivarlos |
| `valuation/index.html` | ✅ Producción | Página del área Valuation (2026-07-21, pedido de Francisco). Paleta estándar navy+oro (no propia). Secciones: hero → qué es Valuation → cómo trabajamos (3 pilares research/valorización/tesis) → **Torneo del área** → responsables → CTA. Los 3 **responsables** (Jhosep García, Benjamín Sáez Molina, Samuel Rodríguez Arnolds) salen de `datos/valuation.json` con foto real detectada sola desde `fotos/directiva/<slug>.jpg`, rol y LinkedIn. **Torneo activado (2026-07-24)**: "Valuation Challenge 2026" con Itaú (Corporate & Investment Banking) y BDO (Deal Advisory) como partners — `torneo.formUrl` ya tiene el Google Form real, así que el botón "Inscríbete →" está activo; datos reales de formato (caso de M&A + defensa ante comité), equipos (2-3 personas desde 2° año), fechas de inscripción (18-26 jul) y competencia (3-31 ago), y premios (1°: práctica Itaú + premio tecnológico, 2°: práctica BDO). Falta `torneo.basesUrl` (aparece "Ver las bases" solo cuando se llene). Enlazada desde el desk "VAL · Valuation" de §Áreas en `index.html` y ahora también desde el nav principal (2026-07-24). **Logo corregido (2026-07-24)**: preloader y nav usaban por error `fig-blanco.png` (el logo blanco de FIW); como esta página usa la paleta estándar navy+oro, se cambió a `fig-oro.png` como en el resto del sitio. **Tira de fotos en movimiento en el hero** (2026-07-22, pedido de Francisco: "igual que se ve en la página principal") — mismo `.photo-marquee` que el index, pero leyendo de `fotos/valuation/1.jpg, 2.jpg…` (numeradas, sin saltos, ver `fotos/valuation/LEEME.txt`) en vez de las carpetas de eventos; mientras la carpeta esté vacía el hero se ve igual que antes, sin errores. **Sección "Actividades" (2026-08-03, pedido de Francisco)**: nueva sección entre Torneo y Responsables con eventos ya realizados por el área, mismo estilo de tarjeta que `eventos/index.html` (foto, fecha, tipo, resumen, participantes) — reutiliza `datos/eventos.json` filtrando por el campo nuevo y opcional `area:"valuation"`, así que un evento etiquetado así aparece EN AMBAS páginas (esta y la bitácora general), nunca solo en una. La tarjeta enlaza a `eventos/index.html#<id>` para reusar el overlay de detalle ya existente en vez de duplicarlo. La sección y el enlace de nav "Actividades" quedan `hidden` y solo aparecen cuando exista al menos un evento con esa etiqueta — hoy ninguno de los 9 eventos existentes es de Valuation, así que queda oculta hasta el próximo evento real del área. **2026-08-03**: las tarjetas de esta sección ahora muestran un chip **PRÓXIMO** cuando la fecha del evento es futura (mismo criterio que en `eventos/index.html`) |
| `torneo/index.html` | ✅ Datos reales · historial de 9 semanas (5 a 13) · **badges automáticos + comparador + replay (2026-08-05)** | `datos/torneo.json` con 59 equipos reales. La página salió del modo DEMO sola. **Corte semanal al 07-ago-2026 (semana 13) cargado el 2026-08-07** — Manuel subió el Excel a la misma carpeta del Drive sin fecha en el nombre; la semana se calculó con `semanaHoy()`. El conector de Drive de esta sesión no pudo bajar el binario del Excel sin corromperlo, así que se reconstruyó un `.xlsx` equivalente con `openpyxl` desde el texto plano de `read_file_content` (mismas 4 hojas que el script espera). Movimiento destacado: Los Default subió 11 puestos. **Corte anterior al 31-jul-2026 (semana 12) cargado el 2026-08-05** — el Excel lo sube el equipo de Portafolio a una carpeta NUEVA del Drive: `02_Areas/PORTAFOLIO/Tablas semanales torneo/` (antes los cortes llegaban sueltos por chat). Ahí están los 8 Excels semanales del torneo, uno por corte, con el mismo formato de siempre. Para actualizar: bajar el Excel más reciente y correr `python3 generar_torneo.py --excel <archivo> --semana N --corte "DD · MMM · 2026"` — **sin `--inscripciones`**, porque el script conserva los integrantes del `torneo.json` anterior y así no se reintroduce el bug de integrantes duplicados que se corrigió a mano en 4 equipos (ver más abajo). Overlay con gráfico de 3 líneas (retorno equipo/promedio/ACWI — el ACWI queda vacío por ahora, no hay benchmark en ningún Excel visto todavía). Tarjetas: Feed PNG, **Story PNG**, LinkedIn PNG, HTML y **videos animados** Feed/Story con intro (logo→nombre→colaboradores→ficha). En celular, los botones de tarjetas **comparten directo con el panel nativo del sistema** (`navigator.share`, Instagram queda a un toque) en vez de forzar una descarga; en iPhone la tarjeta Story además intenta abrir Instagram directo en el compositor de Historias (truco de portapapeles + `instagram-stories://`, con fallback automático). Grabación de video a 24fps con progreso visible en el botón. Logos de colaboradores en hero y tarjetas. La línea temporal de §Metodología integra las actividades del club desde `datos/eventos.json` (tags por tipo + descripción al hover, tarea #16 ✅). **Historial completo reconstruido (2026-07-24)**: Francisco compartió los 7 Excels semanales oficiales (`Excel_Oficial_FIG_PORT_2026_2026-06-12.xlsx` hasta `...2026-07-24.xlsx`, uno por corte); `generar_torneo.py` ganó un modo nuevo `--excels a.xlsx,b.xlsx,...` (ver P0-2 y la sección del script abajo) que lee la fecha de cada nombre de archivo, saca posición/puntos/métricas de cada semana desde su propio `ranking_ordenado`/`Tabla`/`puntos`, y el retorno since-inception de cada semana desde la hoja `Retornos por corte` del corte más reciente (ya trae la serie completa). El número de semana real (5 a 11, no 1 a 7) se calcula con la misma fórmula que usa `torneo/index.html` (`semanaHoy()`, desde el inicio real del torneo el 11 de mayo) — de paso corrigió una semana mal etiquetada como "1" que en realidad era la semana 6. Con las 7 semanas reales, el gráfico de 3 líneas y los indicadores de cambio de posición (▲▼) ahora muestran datos reales en vez del placeholder/guión que se agregó horas antes para el caso de una sola semana (`chartPlaceholder()` sigue en el código, solo que ya no se activa — vuelve a activarse solo si algún día se publica una semana sin historial previo). **Distinciones automáticas (2026-08-05, tarea #18 del backlog)**: `calcBadges()` deriva 4 badges de las métricas que `torneo.json` YA trae, sin tocar el scoring oficial ni pedir datos nuevos — "Cazador de alfa" (mayor IR), "Mejor Sharpe", "Gestor de riesgo" (menor drawdown) y "Remontada +N" (mayor `delta` positivo). Se calculan sobre la lista COMPLETA de equipos, no sobre la filtrada por el buscador, así que no cambian al buscar. Guarda importante: un IR o un Sharpe negativos NO se premian aunque sean el mejor de la tabla (sería premiar al menos malo) — en ese caso el badge simplemente no aparece. `mdd` y `var95` son negativos, así que el mejor es el MÁXIMO (el más cercano a cero), no el mínimo. **Comparador de equipos (2026-08-05, tarea #21 del backlog)**: botón "⇄ Comparar equipos" junto al buscador y "⇄ Comparar con otro equipo" dentro de la ficha de cada equipo (abre el comparador ya con ese equipo cargado). Overlay `#cmpOverlay` con dos `<select>` de los 59 equipos: muestra posición, puntos, retorno relativo y las 5 métricas —cada una con su valor Y los puntos que aportó— marcando con ▲ dorado al equipo que gana esa fila, más un gráfico con las dos trayectorias superpuestas (oro vs azul). Es una vista nueva sobre datos que YA están en `torneo.json`, no toca el scoring. Dato clave de la implementación: en las 5 métricas de Bloomberg PORT el valor MÁS ALTO siempre gana, incluso en `var95` y `mdd` (vienen negativos, el más cercano a cero es el que menos perdió) — la única fila invertida es POSICIÓN, donde 1° gana. Verificado contra el `puntosDetalle` oficial: en VaR y drawdown el comparador marca al mismo equipo al que el torneo le da más puntos. **Replay del ranking (2026-08-05, tarea #24 del backlog)**: botón "▶ Replay del ranking" junto al buscador → overlay `#rpOverlay` con una carrera de barras que recorre las semanas publicadas (hoy 5→12), animando el top 12 con `transform:translateY` (las filas se reordenan deslizándose, las que entran o salen del top aparecen desde el borde). Play/pausa + deslizador de semana; en cada corte el pie muestra el líder y el equipo que más subió respecto de la semana anterior (ej. CLB +21 en la semana 12). Con `prefers-reduced-motion` no arranca solo y se recorre a mano. Dato clave: el orden de cada semana sale de la **`posicion` guardada** en el historial, NO de ordenar por `puntos` — en las semanas 5, 6 y 8 hay un empate exacto de puntos entre dos equipos (Vantedge/Terra, Bull Market Boys/Indarra, SeriosFc/Fat fingers) y el desempate del Excel no coincide con un orden descendente; las 59 posiciones siguen siendo únicas, así que es un artefacto de desempate y no un dato corrupto. El botón se oculta solo si algún día hay menos de dos cortes publicados. **Vista "Evolución por métrica" (2026-08-08, pedido de Francisco)**: el replay ahora tiene dos pestañas — la carrera de barras de siempre y un gráfico de líneas con los 59 equipos superpuestos, semana a semana, para una métrica elegida. Los 5 primeros del último corte van en tonos de oro con su nombre al final de la línea (las etiquetas se separan solas para no encaballarse), el resto queda de fondo tenue, y un `<select>` permite destacar cualquier equipo entre todos. **Las 8 métricas ya se pueden graficar (2026-08-15)**: `generar_torneo.py` ahora persiste las 5 métricas de Bloomberg (IR, exceso, Sharpe, VaR, MDD) en cada punto del `historial`, no solo en `t.metricas` del corte vigente (función `punto_historial()`). El selector se llena solo con `rpMetsDisponibles()`, que ofrece únicamente las métricas con al menos dos semanas de dato, así que no hay que tocar código cuando aparezcan más cortes. El eje X del gráfico se ajusta solo a las semanas que tienen dato de la métrica elegida —si no, quedaban aplastadas contra el borde derecho de un eje S5→S14— y una nota al pie dice cuántas de cuántas semanas se están graficando. **Las 8 series ya cubren las 10 semanas (2026-08-16)**: las 5 de Bloomberg solo existían en S13-S14, así que se recargaron los Excels de las semanas 5 a 12 y se fusionaron 2360 métricas al historial (59 equipos × 8 semanas × 5) con `completar_metricas_historial.py` — ver la fila de ese script más abajo. La nota al pie quedó oculta sola y el selector ofrece las 8 métricas sin que se tocara la lógica. **Ojo, trampa real:** NO se usó `generar_torneo.py --excels` para esto, aunque el comentario anterior lo recomendaba. Ese modo regenera el JSON completo y `procesar_multiples()` hace `eq["miembros"] = insc.get(eq["id"], [])`: sin `--inscripciones` deja a los 59 equipos SIN integrantes, y con `--inscripciones` los reescribe desde el Excel pisando las correcciones a mano de 4 equipos. Además recalcularía `acwi`, `delta`, `retRel` y las posiciones, que ya estaban correctos. Para rellenar una métrica en semanas ya publicadas, usar siempre el script quirúrgico | **Tarjetas y videos (2026-08-08, pedido de Francisco)**: (1) se quitó el hashtag en blanco marfil del pie de Feed y Story —era el único texto fuera de la paleta y se leía suelto—; `footerRow()` conserva el parámetro `tag` en la firma para no romper llamadas. (2) Las 4 distinciones de `calcBadges()` ahora se dibujan también en la tarjeta y el video (`drawBadges()`), con los mismos 3 estilos que en la web; la función devuelve el alto que ocupa y el gráfico se encoge lo mismo, así métricas, colaboradores y pie no se mueven cuando un equipo tiene badges. (3) **Podio**: los puestos 1-3 llevan tratamiento propio —paleta metálica oro/plata/bronce (`podio()`), sello "CAMPEÓN / 2° LUGAR / 3ER LUGAR" en vez de la etiqueta "POS", número y anillo de puntaje teñidos del metal, glow del fondo del mismo tono y un marco fino (`podioMarco()`)—; del 4° en adelante nada cambia. (4) **Peso de los videos**: `videoBitsPerSecond` pasó de 8 Mbps fijo a 3.2 (Feed) y 4.5 (Story). Medido contra el canvas original: bajar el bitrate cuesta ~0.2 dB de PSNR y el texto fino queda idéntico, porque la tarjeta es contenido casi estático; los archivos quedan ~45% más livianos (Feed 1.19→0.64 MB, Story 1.50→0.90 MB) | **Corte al 21-ago-2026 (semana 15) cargado el 2026-08-21** — Francisco pasó los datos en dos formatos (un JSON con el ranking ya calculado y el Excel oficial); se compararon cruzados antes de aplicar nada, coincidían exactamente. Se usó el Excel con `generar_torneo.py --excel ... --semana 15 --corte "21 · AGO · 2026"` (sin `--inscripciones`), como siempre. **5 equipos eliminados esta semana** (Fencashticos, Free Riders, Market Moggers, Mosqueteros, Pink Capital) — el torneo queda en **54 equipos**. Ojo: `generar_torneo.py` arma `equipos[]` desde cero a partir del Excel del corte actual, así que un equipo ausente del Excel desaparece de `torneo.json` POR COMPLETO, incluido su historial de semanas pasadas (S5-S14) — no queda ni rastro en el replay ni en "Evolución por métrica", aunque compitieron esas semanas legítimamente. Se le preguntó a Francisco antes de aplicarlo (con `AskUserQuestion`) y confirmó aceptar este comportamiento tal cual — no se agregó ningún flag `eliminado:true` para preservarles el historial. El dato no se pierde para siempre: sigue disponible en el historial de git de antes de ese commit. De paso se corrigieron 7 menciones hardcodeadas de "59 equipos"/"USD 590M" a "54 equipos"/"USD 540M" en el resto del sitio (`index.html`, `eventos/index.html`, `torneo/pantalla.html`, `datos/club.json`, `datos/eventos.json`, `datos/miembros.json`) — mismo patrón que la corrección 63→59 del 2026-08-02. Se dejó intacto a propósito el párrafo histórico de "Capítulo IV" en `club.json` (describe en pasado el lanzamiento del torneo con los números de ese momento) y `datos/miembros.demo.json` (fuera de uso como fuente). **Revertido el 2026-08-23** — ver la entrada siguiente: Francisco decidió mantener a los 5 en espera en el ranking público, así que las 7 menciones de "54 equipos"/"USD 540M" volvieron a "59 equipos"/"USD 590M" en todo el sitio (`index.html`, `eventos/index.html`, `torneo/pantalla.html`, `torneo/index.html` (meta tags), `datos/club.json`, `datos/eventos.json`, `datos/miembros.json`) y de paso se corrigió `en/index.html`, que tenía "Sixty-three" sin actualizar desde la corrección 63→59 del 2026-08-02 (nunca se había tocado en ninguna de las dos correcciones anteriores).

**Reincorporación como "en espera" (2026-08-23, decisión de Francisco)**: en vez de la eliminación total de arriba, Francisco pidió mantener a los 5 equipos en el ranking público con sus datos Bloomberg congelados (no vuelven a operar) pero el PUNTAJE recalculado cada corte — porque el motor de scoring oficial (`scoring.py` del repo torneo-bloomberg-oficial) puntúa por percentil continuo sobre el MIN/MAX de todos los equipos activos, así que su puntaje puede moverse aunque su dato no cambie, según cómo se mueva el resto del campo. Se creó `datos/equipos_congelados.json` (los 5, con sus 5 métricas crudas fijas en el último corte real que jugaron — semana 14 — y su `historial_previo` semanas 5-14 completo, rescatado del commit `c7c4f98`, el último antes de la eliminación, porque ya traía las 5 métricas por semana backfileadas) y el script `incorporar_congelados.py` (ver su fila en la tabla de archivos), que se corre SIEMPRE después de `generar_torneo.py` — nunca antes, porque necesita el snapshot fresco de los 54 equipos activos de ese corte para recalcular el pool completo de 59. Marca a los 5 con `"congelado": true` en `torneo.json` (campo nuevo, no rompe nada que ya lea el JSON). Primera corrida (semana 15): Free Riders quedó sosteniendo el mínimo de MDD de los 59 (-19.2%, el peor de todos), lo que movió el puntaje de 50 de los 54 equipos reales en +0.05 a +0.79 puntos — nada dramático, pero es exactamente el tipo de "ruido" que hay que vigilar corte a corte (queda registrado en `ALERTAS_CONGELADOS.md`). **Pendiente de decisión de Francisco**: si además de los datos hace falta una marca visual en la UI (badge "en espera" en las tarjetas/comparador/replay) para que los visitantes no confundan a estos 5 con equipos activos normales — hoy no hay ningún indicador visual, solo el campo en el JSON.

**Eliminación definitiva (2026-08-26, decisión de la directiva de FIG)**: Francisco lo habló con el resto de la directiva y acordaron **eliminar en definitiva** a los 5. Se deshizo la reincorporación: `datos/torneo.json` se restauró al estado del commit `b2b382b` (54 equipos, semana 15, con el ACWI ya backfilleado — el commit justo anterior a `9ab21d4`), así que el puntaje/posición/delta de los 54 vuelve a calcularse sobre el pool limpio de 54, y su historial de replay/métricas ya no incluye a los congelados. Las menciones de "59 equipos"/"USD 590M" volvieron a "54"/"USD 540M" en `index.html`, `en/index.html`, `eventos/index.html`, `torneo/index.html` (meta tags + hero + nota del replay), `torneo/pantalla.html`, `datos/club.json`, `datos/eventos.json`, `datos/miembros.json` (se dejó igual el párrafo histórico de "Capítulo IV" en `club.json`, que describe el lanzamiento en pasado, y `datos/miembros.demo.json`, fuera de uso). `datos/equipos_congelados.json` quedó **vacío** (`{"equipos": []}`) e `incorporar_congelados.py` **dormido** con un guard que hace no-op si el JSON está vacío — la maquinaria sigue en el repo por si se decide congelar a otro equipo en el futuro (repoblar el JSON + correr el script tras `generar_torneo.py`). Registro de cierre en `ALERTAS_CONGELADOS.md`.
| `torneo/pantalla.html` | ✅ Producción | **Pantalla para las TV de la facultad** (2026-07-27, pedido de Francisco). 1920×1080, corre en bucle infinito: basta abrirla en pantalla completa (F11) en la TV. Se alimenta sola de `datos/torneo.json`, así que **cada semana que se regenera el ranking la pantalla muestra el corte nuevo sin tocar código**. Secuencia: logo FIG → nombre del club → Área de Portafolio → colaboradores → título del torneo → 3er lugar → 2do → 1ro (uno por uno, cerrando en el campeón) → podio de barras + logos. Cada equipo muestra un **gráfico de área** con su trayectoria real semana a semana (degradado, línea con brillo, punto por semana) contra la **línea punteada del promedio de los 59 equipos**, calculado en vivo desde el mismo JSON. La animación es **determinística**: todo es función de un único reloj (`seek(t)`), sin animaciones CSS — por eso se puede grabar fotograma a fotograma a 60 fps sin cuadros perdidos (`scratchpad/grabar_pantalla.py` congela el reloj con `window.__manual()` y pide cada instante con `window.__seek(ms)`, mandando las capturas por tubería a ffmpeg). En el podio de cierre la **altura de las barras va por puesto, no por puntaje**: los tres primeros suelen tener puntajes muy parecidos (94/86/81) y las barras salían casi iguales, que es justo lo que un podio no debe comunicar — el puntaje real va escrito sobre cada barra. Los integrantes se muestran sin repetidos y con el calce normalizado (el Excel de inscripciones trae a una persona dos veces y nombres en minúscula). **Logo de la FEN ya incorporado (2026-07-28)**: Francisco lo subió al Drive y se bajó a `logos/fen.png`; como el archivo oficial trae el texto casi negro sobre fondo transparente (invisible sobre el navy), va montado sobre una placa clara (`.fen-plate`) para que se lea sin alterar los colores de la marca. **Escena nueva "Cómo leer los resultados" (2026-07-28)**: antes de los podios explica qué significan el gráfico (línea dorada = retorno acumulado del equipo, punteada = promedio de los 59) y las tres métricas en pantalla (Puntos/100 con el desglose real 30/25/15/15/15, Retorno vs ACWI y Ratio de Sharpe). **Duración recortada** de 57s a 42s a pedido de Francisco. **Fondo simplificado (2026-07-28, pedido de Francisco)**: se eliminaron la cuadrícula dorada tenue y la línea de mercado del borde inferior; queda solo el glow radial, el polvo dorado y la viñeta. Se graba a **30 fps** mientras se revisa; el grabador sube a 60 cambiando una constante |
| `torneo/pantalla-facultad.html` | ✅ Producción (2026-08-11, pedido de Francisco) | **Video semanal para mandar a la facultad**, distinto de `pantalla.html` (esa es para dejar abierta en vivo en la TV; esta es un `.mp4` que se genera y se envía). Recrea el diseño de una propuesta que se había hecho en una sesión anterior y nunca se implementó (`Propuesta_Video_FIG.mp4`, fondo blanco + azul `#0052FF`, una tarjeta por equipo con integrantes y mini gráfico) — mismo motor determinístico que `pantalla.html` (`seek(t)` único, ganchos `window.__ready/__total/__manual()/__seek(ms)`), así que **se alimenta sola de `datos/torneo.json`** en vez de ser un video fijo. Secuencia: intro (logo + "FEN Investment Group") → "En alianza con" (FEN UChile + Itaú + BlackRock) → Ranking Top 5 → una tarjeta por equipo (logos, posición, puntaje, integrantes con iniciales, mini gráfico de evolución del retorno) → Ranking Top 5 de cierre. Los 3 logos y el ícono del toro navy (`logos/fig-navy.png`) ya existían en el repo, no hubo que pedir nada nuevo. **Cambio deliberado frente a la propuesta original**: esa maqueta rotulaba el retorno "RETORNO VS ACWI", pero `datos/torneo.json` no trae el benchmark ACWI cargado (`acwi:[]`) — mostrar una comparación contra un dato vacío sería inventarlo, así que acá dice "RETORNO ACUMULADO" hasta que exista ese dato real. **Gráfico contra el promedio del torneo (2026-08-15, pedido de Francisco)**: cada tarjeta ahora dibuja DOS líneas — el retorno acumulado del equipo (verde, sólida) y el promedio acumulado de los 59 equipos (gris, punteada), con la banda entre ambas teñida de verde o rojo según el equipo cierre por sobre o bajo el promedio. El promedio se calcula en vivo desde el mismo `torneo.json` (`promediosTorneo()`), no hay dato que mantener a mano. Lleva una leyenda que nombra cada línea con su valor, porque sin ella no se distinguían. Se evaluaron 3 variantes y Francisco eligió esta; la descartada (barras de variación semanal) quedó documentada como tarea 26 del backlog por si se usa después. **Bug de rótulo corregido en el mismo cambio**: el recuadro de la tarjeta mostraba `retRel` bajo la etiqueta "Retorno acumulado", pero `retRel` es el retorno RELATIVO (exceso) — son dos cifras distintas (ej. Beta capital: +18.92% relativo vs +11.90% acumulado) y quedaban las dos en la misma tarjeta con el mismo nombre. Ahora dice "Retorno relativo", igual que el resto del sitio (`torneo/index.html` ya usaba "RET. RELATIVO"). **Logos más grandes, en dos pasadas (2026-08-15)**: primero de 74px a 112px en la escena "En alianza con" y de 48px a 68px en cada tarjeta; después Francisco pidió agrandarlos más y se llegó al tamaño actual — **196px** en la escena de auspiciadores (a pantalla completa, la fila mide 1482px de 1920, con 219px de aire por lado), **132px** el nombre del torneo —subió en dos pasos, 56→84 el 15-ago y 84→132 el 16-ago— con el toro a 142px; ojo que a 132px el tope no es el ancho (el bloque mide 1443px de 1920) sino el alto: hubo que subir `#head` de 118px a 86px para que el título no tocara la tarjeta, y con eso quedan 27px de aire sobre la tarjeta más alta del top 5, y solo **84px** la fila de logos DENTRO de cada tarjeta. Esa asimetría es deliberada: el alto de la fila de la tarjeta empuja todo su contenido hacia abajo, y la tarjeta más alta del top 5 (un equipo de 3 integrantes, hoy CLB) se mete bajo el pie de página — medido, a 100px ya lo invade y a 115px el `@fen.investment.group` se dibuja encima de la tarjeta blanca. Para agrandarlos más habría que subir `#cardPanel` o bajarle el padding, no basta con el número. Antes de grabar se compararon 4 tamaños (actual/+25/+50/+75) con capturas reales. **Observaciones de la Escuela (2026-08-20)**: tras el visto bueno de Decanato, la Escuela pidió cambios. Aplicados: (1) los logos salieron de la cabecera de cada tarjeta de equipo y pasaron a una franja de marca al pie **visible en TODAS las láminas** — pero **el 2026-08-20 Francisco pidió sacar del pie los tres logos de los colaboradores**, así que hoy ahí solo van el toro y el `@fen.investment.group`; los colaboradores conservan su lámina propia a pantalla completa ("En alianza con"), que es donde se lucen. Se mantuvo que el pie se vea en todas las láminas, porque eso era una mejora aparte, incluidas intro y cierre — antes el pie aparecía recién desde la lista y solo llevaba el toro; de paso la tarjeta perdió ~118px de alto y la más alta del top 5 dejó de rozar el pie (pasó de −21px a +57px de holgura); (2) la intro dice ahora **"Organización estudiantil de la Facultad de Economía y Negocios"** — se nombra la Facultad pero NO "Universidad de Chile", que Francisco pidió sacar del texto visible el 2026-07-24, así se cumplen las dos instrucciones. (3) el logo de la FEN pasó a la **versión con escudo**: Francisco mandó el archivo oficial y quedó como `logos/fen-escudo.png` (500×288, con transparencia), usado SOLO en este video — `logos/fen.png` sigue intacto para `torneo/pantalla.html`, que no se tocó por no venir pedido. En la franja del pie cada logo lleva su propio alto (FEN 78px, Itaú 62px, BlackRock 42px, toro 56px): el del escudo es más cuadrado (ratio 1.74 vs 2.09 del anterior) y su texto ocupa solo la mitad inferior, así que a la misma altura que los otros quedaba ilegible — se equilibran ópticamente, no por número. (4) la frase de organización estudiantil subió de 27px a 38px. **No aplica**: la Escuela pidió cambiar por azul "las franjas negras de arriba y abajo", pero se verificó decodificando el MP4 que el archivo es blanco de borde a borde (RGB 249-255) en todos los fotogramas — esas franjas son el letterbox del reproductor, no algo que el video traiga. **Formato de lienzo elegible (2026-08-20, pedido de Francisco)**: la página acepta `?formato=16x9|16x10|4x3|1x1|4x5|9x16` (o `?w=&h=` libre) y `?banda=blanco|azul|navy`. El **escenario sigue midiendo siempre 1920×1080** y se escala/centra dentro del lienzo elegido (`#stage` con `transform: scale()`), así la composición no se rediseña por formato — es la misma ya verificada — y las bandas sobrantes **las pintamos nosotros** en vez de dejárselas al reproductor, que las pone negras. Eso resuelve la observación de la Escuela sobre "las franjas negras": no estaban en el archivo (es letterbox), pero ahora se puede exportar en la proporción exacta de la pantalla de destino, o con banda azul si sobra espacio. La página trae un **selector visible** arriba a la derecha que se oculta solo al grabar (`window.__manual()`), y expone `window.__w`/`window.__h` para que el grabador abra el navegador del tamaño correcto: `python3 grabar_pantalla_facultad.py [formato] [banda]`. Ojo: el diseño es apaisado, así que en 9x16/4x5/1x1 el contenido queda chico y con bandas grandes — para vertical de verdad habría que rediseñar la composición, no solo cambiar el lienzo. Se graba con `scratchpad/grabar_pantalla_facultad.py` a **60 fps, 1920×1080, H.264 CRF 16** vía PyAV (el `ffmpeg` de este entorno no trae decoder/encoder H.264, solo VP8/VP9 — PyAV trae su propio build completo) |
| Enlaces cruzados | ✅ Conectados | `index.html` ya enlaza a `eventos/`, `fiw/`, `torneo/` y `postula/` (CTAs, footer, `CONFIG.urls` y `datos/club.json`) |
| `generar_torneo.py` | ✅ Probado con el Excel real | Lee `ranking_ordenado` (+ `Tabla`/`puntos` como respaldo para métricas más completas que trae el Excel oficial) + Excel de inscripciones → escribe `datos/torneo.json`, conserva el `historial` semanal y calcula `delta`. Ya soporta el formato ancho real del Excel de inscripciones (columnas Líder/Int2/Int3 Nombre+LinkedIn) además del formato largo original. Solo copia `nombre` + `linkedin` de cada integrante (nunca correo/carrera/ingreso, regla dura de PII). Modo `--demo` disponible. **Modo nuevo `--excels a.xlsx,b.xlsx,...` (2026-07-24)**: reconstruye el `historial` completo de una sola pasada a partir de varios cortes semanales del Excel oficial — saca la fecha de cada nombre de archivo, el snapshot semana a semana de cada `ranking_ordenado` propio, y el retorno since-inception de la hoja `Retornos por corte` del corte más reciente (esa hoja ya trae la serie completa hasta esa fecha, no hace falta pegar los `ret` uno por uno). Calcula el número de semana real con la misma fórmula que usa la página (desde el inicio del torneo el 11 de mayo), así que no requiere pasarle `--semana`/`--corte` a mano. Uso: `python3 generar_torneo.py --excels sem1.xlsx,sem2.xlsx,... --inscripciones insc.xlsx`. **Advertencia sobre `--excels` (2026-08-16):** `procesar_multiples()` asigna `eq["miembros"] = insc.get(eq["id"], [])` sin conservar lo anterior — a diferencia de `integrar_historial()`, que sí lo hace. O sea que este modo BORRA los integrantes si no se le pasa `--inscripciones`, y los reescribe desde el Excel si se le pasa. Úsalo solo para reconstruir el historial desde cero; para completar un dato puntual usa `completar_metricas_historial.py` |
| `miembros/index.html` | ✅ Verificado en navegador (2026-08-16) | **"La mesa"**: UNA sola experiencia, no tres pestañas. La primera versión tenía conmutador de vistas MESA/ESTRUCTURA/DIRECTORIO y Francisco la rechazó con razón: demasiados controles antes del contenido, y la "mesa" eran cuatro rectángulos con burbujas, un diagrama genérico que podía ser de cualquier cosa. **Rediseño completo (2026-08-16)**: una mesa REDONDA con un asiento por directivo, agrupados en arcos por desk. Toda la geometría se calcula en JS desde el número real de personas —los arcos se reparten los 360° en proporción a cuánta gente tiene cada desk— así que la mesa se reordena sola cuando el club crezca; no hay una sola coordenada escrita a mano. Los radios están **encadenados a propósito** (`R_SILLA` → nombre → rótulo → `R_ARCO`): si se toca uno hay que recalcular el otro, porque el bug que hubo fue justamente que los nombres se metían dentro del anillo. Las etiquetas de los desks siguen la curva con `textPath`, invirtiendo el sentido del camino en la mitad inferior para que no salgan de cabeza. La presidencia y los cofundadores van DENTRO del disco central: no pertenecen a un desk, presiden el conjunto. **Entrar a un desk**: el arco elegido se abre hasta los 360° mientras su radio exterior crece fuera del lienzo — deja de ser un arco y se vuelve el fondo, o sea literalmente devora la pantalla— y recién ahí aparece la estructura del área. **Dentro del área**, un organigrama de tres estratos (líder → dirección → segunda línea) dibujado con un RIEL, no con curvas de un nodo a varios: como todos los nodos miden 170px con 18px de gap, la horizontal va de 85px a 85px de cada borde y toca exacto el centro del primero y del último. Por eso no se cruza nunca ninguna línea, que era el otro reclamo. **El corte deliberado**: los miembros sin cargo no se dibujan ni se sientan a la mesa — cada desk cierra con "+N miembros" que salta al buscador filtrado. Con 200 personas cualquier organigrama completo vuelve a ser ilegible. **El buscador es el único control de la página**: no hay pestañas ni filtros, escribir es la única acción y los resultados aparecen abajo. Entiende nombres, tickers (`BSM`), desks (`PRT`), generaciones y `ALUMNI`; `/` lo enfoca, ↑↓ recorre, Enter abre; ignora tildes. Al filtrar, los asientos que no calzan se atenúan en vez de desaparecer. **Ficha** con deep link propio (`miembros/#BSM`), bio, hitos, torneo con la curva real del equipo, actividades, "Su aporte" y la tarjeta descargable. **Fotos**: se detectan solas (`fotos/miembros/<id>` y luego `fotos/directiva/<id>`), con caché por persona porque cada sondeo prueba hasta 8 rutas en serie; cuando hay retrato el ticker se oculta, porque encima de una cara no se lee ni él ni ella. **Verificado en navegador**: se manejó Chrome headless por CDP (sin instalar nada: el Chrome de la máquina + el WebSocket nativo de Node 24) para ver la página, entrar a cada desk, abrir una ficha por deep link y generar la tarjeta interceptando el canvas. |
| `generar_miembros.py` + `datos/miembros.json` | ✅ Fase 1 de la sección de Miembros (2026-08-16) | Genera `datos/miembros.json` fundiendo cuatro fuentes sin duplicar ninguna: la **directiva** sale de `datos/club.json` (sigue siendo su única fuente de verdad, acá solo se lee), el **resto del club** de un Excel del Drive que todavía no existe (columnas en `PLANILLA_MIEMBROS_FIG.md`), los **resultados de torneo** cruzados contra `datos/torneo.json` y las **actividades** contra `participantes` de `datos/eventos.json`. Hoy corre con los 15 de la directiva como semilla, así que la página se puede construir y probar antes de que exista la base consolidada. **Ticker de 3 letras por persona** (`Benjamín Sáez Molina → BSM`), único y garantizado por el script: es la clave del buscador y el ancla de la URL de cada ficha (`miembros/#BSM`) — las `iniciales` de 2 letras de `club.json` YA colisionan (Benjamín Sáez Molina y Benjamín Solís son ambos "BS"). **El calce con el torneo no puede ser literal**: el Excel de inscripciones trae el nombre civil completo y `club.json` la forma corta, así que hay un tercer intento por subconjunto de tokens que exige que TODOS los tokens del nombre corto estén en el largo Y que el primer nombre coincida — con eso Jhosep García calza con "Jhosep Gabriel García Suarez" y Juan José Limari con "Juan José Limarí Campos" (4 de 15 calzan), mientras que "Manuel Paz" NO calza con "Victoria Paz Tapia Rivera" ni "Francisco Valenzuela" con "Lucas Daniel Valenzuela Pavez". Si el subconjunto calza con más de un equipo no se asigna nada y se avisa: un dato ambiguo es peor que uno ausente. **Privacidad**: solo se leen las columnas de `ALIAS_MIEMBROS`, así que si la planilla del Drive trae RUT/correo/teléfono nunca llegan al JSON; y cada persona controla qué se publica con la columna `muestra` — lo no autorizado no se escribe al archivo, porque el JSON también es público. **Decisión de Francisco (2026-08-16): no se alojan PDFs de CV**, la ficha del miembro ES su CV público (un CV real trae RUT y teléfono). **Campo `liderArea` en `club.json` (2026-08-16)**: quién dirige un desk NO se puede adivinar por jerarquía/orden alfabético — eso fue justo lo que eligió mal a Agustín Arriagada como líder de Portafolio en vez de a Francisco Valenzuela, el director real del área. Se agregó `liderArea` (opcional) a la entrada de cada persona en `club.json → personas.directiva`; `desde_club_json()` lo traduce a `lidera` solo si calza con la propia `area` de la persona. Hoy solo Francisco lo tiene (`"liderArea":"PRT"`, confirmado por él mismo el 2026-08-16). Trading, Valuation y FIG Woman siguen con el líder AUTO-ELEGIDO por `marcar_lideres()` (Juan José Limari, Samuel Rodríguez Arnolds, Delia Avilán) — no se tocaron porque nadie ha confirmado quién los dirige de verdad; ver P0.5 y la pregunta 6 de la sección 6 sobre Valuation, que sigue sin resolverse por la misma razón. Modos útiles: `--auditar` (cómo calzó cada uno), `--candidatos` (los 145 inscritos del torneo que aún no tienen ficha) y `--csv-candidatos RUTA` (los exporta como CSV con los encabezados de la planilla ya puestos, para abrirlo en Sheets — **guardarlo fuera del repo**, son personas que aún no autorizaron nada). Pendiente que depende del club: `participantes` está vacío en los 10 eventos de `eventos.json`, así que ninguna ficha muestra actividades todavía aunque el cruce ya funciona |
| `completar_metricas_historial.py` | ✅ Probado (2026-08-16) | Rellena métricas que falten en semanas YA publicadas del historial de `datos/torneo.json`, leyéndolas de los Excels semanales. Es un injerto quirúrgico: solo AGREGA claves de métrica ausentes, jamás pisa un valor existente ni crea/borra semanas, equipos o campos — y si detecta que cambió cualquier otra cosa, aborta sin escribir. Trae un chequeo de integridad que compara posición y puntos guardados contra el Excel y reporta discrepancias sin corregirlas. Idempotente: correrlo dos veces sobre los mismos Excels agrega 0. Uso: `python3 completar_metricas_historial.py --excels a.xlsx,b.xlsx,...` (dry-run) y luego `--aplicar`. Existe porque `generar_torneo.py --excels` regenera el JSON completo y en el camino borra los integrantes (ver fila de arriba) |
| `postula/index.html` | ✅ Endpoint conectado (sin verificar en vivo) | Formulario de postulación completo; envía (con `tipo:"postulacion"`) a `config.figEndpoint` (el Apps Script COMPARTIDO del sitio) de `datos/club.json` — la URL ya está pegada (2026-07-18), pero nadie ha confirmado aún que una postulación real llegue a la planilla (este entorno no puede alcanzar `script.google.com`); Francisco debe probarlo una vez |
| `desafio/index.html` | ✅ Funcional (banco real) | Trivia: modo desafío (secuencial, puntaje decae, malas descuentan, revisión con explicaciones, áreas fuerte/débil, ranking local) y modo estudio (por tema o ramo, sin reloj). Banco en `datos/preguntas/` — **348 preguntas reales en 12 temas y 5 ramos** (ahora incluye `finanzas-ii` y `apf`) extraídas del material de finanzas del Drive (P1.5 Q2, lotes 1-31; validar siempre con `validar_preguntas.py`). **Auditoría de calidad completa (2026-07-23)**: las 348 preguntas fueron revisadas por precisión técnica/coherencia (no solo esquema JSON) — se corrigió 1 error numérico real, 1 bug de metadata (`ramo` mal etiquetado), 2 reclasificaciones de tema y ~35 mejoras de estilo/distractores; nadie encontró alternativas "correctas" objetivamente erróneas, así que el contenido de fondo ya era sólido. **Dificultad subida (2026-07-20)**: `armarDesafio()` prioriza preguntas de dificultad 2-3 (solo cae a dificultad 1 si el tema no tiene suficientes), el puntaje decae más rápido (20s→14s) y la penalización por respuesta mala subió de 25 a 32 pts; la fase de lectura también se acortó un poco. Idea pendiente de Francisco: selector de dificultad (1/2/3) en el juego — el campo `dificultad` ya existe en todas las preguntas |
| `juego/index.html` | ✅ Funcional | "El Rally del Toro": runner canvas con un **toro dorado dibujado a mano** (silueta embistiendo inspirada en el logo, galope de 4 patas, cola y cuernos animados — ya no se usa la imagen del logo en el canvas); velas rojas, **vela gigante (flash crash)**, burbujas y **pozo del SII** (un vacío en el suelo con las letras "SII" — hay que saltarlo; si caes, overlay "Te fuiste en cana" con la moraleja de integridad, raro ~5.5%) como obstáculos; VENDER asegura el puntaje y ofrece **descargar una tarjeta PNG 1080×1350** del resultado (monto, % ganancia, el toro, cita del club) — filosofía "saber cuándo salir". **Dificultad rebalanceada (2026-07-22, pedido de Francisco: "al llegar a 3x ya no es posible avanzar")**: la velocidad ahora tiene MESETA (`speed=6+min(elapsed,34000)/10000`, techo ~9.4) y el ritmo de spawn un piso de 640ms — lo único que sigue subiendo es el `mult` de recompensa, así el juego siempre es jugable y la tensión es "cuánto aguantas". **Evento "posición en corto"**: cada ~18s (luego cada 16-24s) el mundo se da vuelta con un aviso previo (banner) — el toro corre por el TECHO (gravedad invertida, `mode="short"`) y hay que **CUBRIR (saltar ↓)** las alzas verdes que cuelgan del techo, con un botón distinto; a los ~6.5s vuelve a normal. Controles: SALTAR (Espacio/↑) en largo, CUBRIR (↓/K) en corto; en móvil el tap del lienzo hace la acción del modo; dos botones en pantalla muestran cuál está activo. **Panel lateral "Tu rendimiento"** (`.side`): curva de equity de la corrida en vivo + línea punteada del siguiente en la tabla con "faltan USD X para pasar a [nombre]" y "Vas #N en vivo" (se calcula contra `RANK`, el ranking local o global). Ranking: lee `config.figEndpoint` de `datos/club.json` (el Apps Script COMPARTIDO del sitio) y muestra "Ranking global"; si el endpoint está vacío o el fetch falla, cae automático a localStorage por navegador. **Endpoint ya conectado (2026-07-18)**, pendiente de que Francisco confirme que una corrida real llega a la pestaña `Ranking` de la planilla. Nota: hay un espejo de estado (`window.__rallyState`) que solo se activa con el flag de prueba `window.__rallyFast` — inerte en producción |
| Fotos de eventos | ⚠️ Parcial | 7 de 9 eventos con fotos curadas y comprimidas (ver `HOJA_DE_RUTA_FIG.md` tarea #5). Faltan `torneo-portafolio-2026` y `charla-analisis-tecnico-2025` (sin carpeta en el Drive) y más variedad en `lanzamiento-club-2025` (fotos Samsung de 7-9 MB, por encima del límite del conector de Drive) |
| Fotos de la directiva | ✅ Completa (15/15) | `fotos/directiva/` tiene foto real de las 15 personas de `personas.directiva` (Francisco subió las 4 que faltaban — Agustín Arriagada, Juan José Limari, Delia Avilán y Gabriela Domínguez — el 2026-07-24, y Victoria Espinoza llegó con foto real desde el inicio). Fotos de baja resolución (ej. Agustín, ~96×96 desde LinkedIn) se reescalaron con Lanczos + realce de nitidez, mismo tratamiento que se le dio a Manuel Paz. Notas: Samuel Rodríguez Arnolds se sumó a `personas.directiva` el 2026-07-18 (co-encargado de Valuation junto a Jhosep, confirmado por Francisco); Delia Avilán, Gabriela Domínguez y Victoria Espinoza son co-fundadoras de FEN Investment Woman (confirmado por Francisco el 2026-07-24, tras detectar que los 3 CV se autodescribían con el mismo rol). **Foto de Francisco Valenzuela actualizada (2026-08-05)**: subió una foto profesional nueva a la carpeta `CV/Fotos` del Drive ("Foto FV") — se recortó a cuadrado 800×800 centrado en el rostro (mismo formato que el resto del equipo; la anterior era 704×1058, único caso no cuadrado) y se reemplazó `fotos/directiva/francisco-valenzuela.jpg` |
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
4. ✅ **URL de `bases`** resuelta (2026-08-23) — el link apuntaba a
   `https://mpazq-afk.github.io/torneoportafolio2026/documentos/...pdf`, que
   daba 404 (esa ruta nunca existió en el repo de deploy). Francisco subió el
   PDF real a Drive (`02_Areas/PORTAFOLIO/Bases_finales_torneo_portafolio_2026.pdf`);
   se copió a `documentos/` en este repo y se apuntaron `CONFIG.urls.bases`
   (`index.html`), `config.urls.bases` (`datos/club.json`) y el botón directo
   de `torneo/index.html` al archivo local. `contacto` sigue pendiente (P0-4).
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

## Cambios del 2026-08-23 (segunda tanda, tras la reincorporación de los 5)

**Bug real corregido**: el botón "Torneo 2026" del nav de `eventos/index.html`
(escritorio y móvil) apuntaba a `https://feninvestmentgroup.com/torneoportafolio2026/`
— un sitio externo viejo que da 404 (verificado con curl). Era el único link
del sitio con este problema; se cambió a `../torneo/index.html` en ambos
repos. Reportado por Francisco: Inicio → Torneo → Eventos → intentar volver
a Torneo desde ahí daba 404.

**Nav de `index.html` reordenado** (pedido de Francisco: "hay demasiadas
cosas"): de 11 ítems planos a 6 — Nosotros, Torneo, **Áreas ▾** (Valuation),
**Comunidad ▾** (Miembros, FIG Woman), **Actividades ▾** (Eventos, Historia),
Jugar ▾ (sin cambios, ya era desplegable). La clase CSS `.nav__play` se
renombró a `.nav__drop` (genérica, la reusan los 4 desplegables). **Ojo con
un bug que casi se introduce**: los triggers de "Áreas ▾" y "Comunidad ▾" no
deben repetir el mismo `href="#areas"`/`#equipo"` que ya usa su propio
submenú — el JS de "link activo del nav" (`.nav__links a`, busca por
`getAttribute("href").slice(1)`) arma un mapa por id de sección, y dos `<a>`
con el mismo hash se pisan entre sí, dejando el trigger visible SIN el
resaltado dorado cuando esa sección está en pantalla. Por eso el submenú de
Áreas solo tiene "Valuation" y el de Comunidad solo "Miembros"/"FIG Woman"
— el trigger mismo ya cubre la sección ancla, no hace falta repetirla adentro.
**En el repo de Manuel se adaptó distinto**: como ahí no existe Miembros y
FIG Woman sigue oculta (`FIW_TEMP_OCULTO`), "Comunidad ▾" habría quedado
como un desplegable vacío — se dejó "Equipo" como ítem suelto en su lugar,
sin agrupar.

**ACWI real agregado a `torneo/pantalla.html` y `torneo/pantalla-facultad.html`**
(pedido explícito de Francisco: "quiero que aparezcan las dos" — ACWI Y
promedio del torneo, no una en vez de la otra). Hasta ahora ambas pantallas
solo comparaban cada equipo contra el promedio de los 59, aunque el
benchmark real ya se captura desde Bloomberg desde el 2026-08-21
(`datos/torneo.json.acwi`, ver el otro repo). Ahora dibujan una tercera
línea (azul `#3C6DA8` sobre fondo claro en pantalla-facultad, `#7BA7DE` sobre
fondo oscuro en pantalla — mismos tokens que usa el resto del sitio para
ACWI). Si el corte más reciente todavía no tiene el valor de ACWI capturado
(le puede faltar un corte, el pipeline de Bloomberg lo agrega aparte), la
línea de ACWI simplemente no llega hasta la última semana — no se inventa
el dato ni se rompe el gráfico.

**`torneo/pantalla-facultad.html` agrandado** (Francisco lo proyectó con el
equipo y acordaron que se veía chico/pixelado): nombres de integrantes
24px→32px, rol 16px→20px, avatar 56px→68px; intro (escena 1) con logo
150px→190px, título "FEN Investment Group" 96px→124px, kicker y línea de
organización también más grandes. **Detalle técnico importante**: el ancho
de la máscara que revela el título letra por letra era un número fijo en
px (`1010`, calculado a mano para el font-size viejo) — con el font-size
nuevo el texto real es más ancho que esos 1010px, así que se habría cortado
a la mitad. Se cambió a medir el `scrollWidth` real del `<h1>` en vivo
(`MASK_W`, ver `medirMascara()`), con `document.fonts.ready` para esperar
a que Playfair Display esté cargada antes de medir — así un futuro cambio
de tamaño no vuelve a romperlo.

**Pixelación al proyectar — script de grabación reconstruido (2026-08-23),
AÚN NO SE HA CORRIDO**. El script viejo (`scratchpad/grabar_pantalla_facultad.py`)
vivía en el scratchpad efímero de una sesión anterior de Claude Code y se
perdió al cerrarla — por eso este nuevo queda **en la raíz del repo, no en
un scratchpad**, para que no vuelva a pasar.

Hardware de la máquina de Francisco (verificado 2026-08-23, relevante para
cualquier ajuste futuro): Intel Pentium Gold 7505, 2 núcleos/4 hilos, **solo
3.8 GB de RAM** (con frecuencia menos de 1 GB libre), GPU integrada. Con eso
en mente, el diseño evita Playwright/Puppeteer (bajan ~300MB de Chromium
aparte) y evita acumular fotogramas en memoria.

Son DOS scripts nuevos en la raíz del repo:
- `grabar_pantalla_facultad_1_capturar.js` (Node, **sin instalar nada**:
  usa el Chrome/Edge ya instalado + el `fetch`/`WebSocket` nativos de Node
  24, manejando el navegador por CDP crudo — mismo patrón que se usó para
  verificar `miembros/index.html`). Necesita un server local corriendo
  primero (`python -m http.server 8000` desde la raíz del repo, porque la
  página hace `fetch()` a `../datos/torneo.json` y eso lo bloquea `file://`).
  Congela el reloj de la página (`window.__manual()`), espera
  `document.fonts.ready` (importante: sin esto los primeros fotogramas
  podrían capturarse con el título del intro sin revelar del todo — ver
  `medirMascara()` en `pantalla-facultad.html`) y recorre `window.__seek(ms)`
  fotograma a fotograma, escribiendo cada uno a `frames/frame_NNNNN.png` y
  descartándolo de memoria antes del siguiente. Por defecto 30fps (no 60:
  la mitad de fotogramas, mismo resultado visual en un video sin movimiento
  rápido, la mitad de riesgo para 3.8GB de RAM).
- `grabar_pantalla_facultad_2_codificar.py` (Python + `av`/PyAV, instalado
  el 2026-08-23 con permiso de Francisco — Pillow ya estaba de
  `optimizar_fotos.py`). Lee los `.png` de `frames/` uno por uno y los
  codifica directo al MP4 final (nunca los tiene todos en memoria a la
  vez), CRF configurable (18 por defecto, buena calidad/peso razonable para
  subir a Drive — más bajo = más calidad y más peso, ver el docstring del
  script).

Uso completo:
```
python -m http.server 8000                              # terminal 1, dejarla corriendo
node grabar_pantalla_facultad_1_capturar.js              # terminal 2
python grabar_pantalla_facultad_2_codificar.py           # terminal 2, después
```
Estimado en esa máquina (NO cronometrado todavía, es una proyección): unos
15-20 minutos a 30fps, archivo final entre 20 y 50 MB. **Antes de correrlo
de verdad, avisarle a Francisco** — accedió a que se armara el script pero
pidió no correrlo todavía en la sesión donde se escribió.

## Cambios del 2026-08-27: cargos del área Portafolio + sección de creadores

**Un solo Director de Portafolio.** Cinco personas figuraban como
"Director · Portafolio" en `datos/club.json`. Francisco aclaró que **el
director del área es él**; Manuel Paz, Agustín Arriagada, Benjamín Disi y
Benjamín Solís pasaron a **"Directivo · Portafolio"** (él eligió ese rótulo
sobre "Administrador"). El cambio tocó, por persona y solo dentro de su
propia ficha, el campo `rol`, la primera entrada de `hitos` y la bio (que
decía "y director del área Portafolio" → "y **directivo** del área
Portafolio"): `datos/club.json`, el HTML estático y el literal JS `CLUB_DATA`
de `index.html`, y `datos/miembros.json` (`rol`, `rolCompleto`, `hitos`).
La bio de Francisco es la única que conserva "director del área Portafolio",
y `liderArea:"PRT"` sigue siendo suyo y de nadie más. **Los 3 "Director ·
Trading" NO se tocaron** — no venía pedido, pero es el mismo patrón por si
algún día se aclara quién dirige esa área (ver P0.5).

**Benjamín Sáez no cofundó el área de Portafolio.** Decía "Co-fundador ·
Área Portafolio" en el `detalle` y en `hitos`, y su bio decía "Lidera el
área Portafolio y la dirección estratégica del club" — las dos cosas
chocaban con que el director del área sea Francisco. Francisco lo corrigió:
**él cofundó el CLUB, como el resto de la directiva, y es el presidente
actual**. Quedó `detalle: "Co-fundador de FEN Investment Group."`, el hito
como "Co-fundador de FIG" y la bio como "Lidera la dirección estratégica
del club".

**Sección nueva `#creadores` en `torneo/index.html`** (pedido de Francisco:
"que se vean los creadores del torneo"). Va después de §Metodología, antes
del footer, con enlace propio en el nav (desktop y móvil). Vuelve al fondo
navy — Metodología es la única sección clara de la página — así el cierre
de créditos se lee como bloque aparte y engancha con el footer.

Detalle importante de dónde vive el dato: **la LISTA de creadores es
explícita**, en `datos/club.json` → `torneo.creadores` (nombre + `aporte`).
No se deriva de quién tiene hoy un rol de Portafolio, a propósito: haber
creado el torneo 2026 es un hecho histórico, no un cargo vigente — si el
año que viene entra alguien nuevo al área, no pasa a ser creador. En cambio
el **cargo, el LinkedIn y la foto NO se repiten** ahí: `initCreadores()` los
resuelve en vivo contra `personas.directiva` calzando por nombre, así que un
cambio de cargo se refleja solo. Si alguien de la lista no tiene ficha en
`directiva`, esa tarjeta se omite en vez de inventarle el cargo; y la
sección arranca con el atributo `hidden`, que solo se saca si de verdad se
dibujó al menos una tarjeta (un `club.json` roto no deja un título con la
grilla vacía). Las fotos se sondean como en el resto del sitio
(`../fotos/directiva/<slug>.<ext>`), con monograma dorado de respaldo del
mismo tamaño para que la tarjeta no salte si falta el archivo.

Son 6: Benjamín Sáez (presidencia y alianzas), Francisco (co-creador y
plataforma web), Benjamín Disi (reglas y metodología), Benjamín Solís
(arquitectura), Agustín Arriagada (capacitación en Bloomberg) y Manuel Paz
(comunicaciones). Cada `aporte` sale de la bio o los hitos que esa persona
ya tenía en `club.json` — no se inventó mérito nuevo.

**Verificado en navegador** (Chrome headless por CDP crudo, mismo patrón que
`miembros/index.html`): las 6 tarjetas renderizan con foto real y cargo
correcto, sin errores de consola, en los dos repos; y la grilla corta bien
3 → 2 → 1 columnas sin desborde horizontal. **Dos trampas que costaron
tiempo y conviene no repetir** al verificar cualquier sección de este sitio:
(1) el `clip` de `Page.captureScreenshot` va en coordenadas del **documento**,
no del viewport — hay que sumarle `scrollY` al `getBoundingClientRect()`;
(2) hay que **scrollear la sección a la vista y esperar >0.9s** antes de
capturar, porque los `.reveal` recién reciben la clase `in` cuando el
IntersectionObserver los ve entrar en pantalla — si no, se captura un
rectángulo navy vacío y parece que la sección está rota cuando no lo está.

## Segunda tanda del 2026-08-27: jerarquía visual y correcciones de crédito

**Tres niveles de marco en §Nosotros** (pedido de Francisco: "que quede claro
que yo lidero el área"), en `index.html` de los dos repos:

| Nivel | Quién | Marca visual |
|---|---|---|
| Presidencia | `destacado:true` en `club.json` | Filete dorado **arriba** + avatar dorado (ya existía) |
| Dirige un área | `liderArea` en `club.json` | Filete dorado **al costado** + chip "Dirige el área" |
| Resto | — | Tarjeta normal |

`liderArea` ahora está **declarado explícito** para los tres líderes
confirmados: Francisco (`PRT`), **Delia Avilán (`FIW`)** y **Samuel Rodríguez
Arnolds (`VAL`)** — antes solo Francisco lo tenía y los otros dos quedaban
bien únicamente porque `marcar_lideres()` de `generar_miembros.py` los
auto-elegía, o sea por suerte. **Trading va sin `liderArea` a propósito**:
Francisco todavía no tiene claro quién lo dirige, así que ninguna tarjeta de
Trading lleva marco. Ojo que `datos/miembros.json` **sí** trae
`lidera:"TRD"` en Juan José Limari, auto-elegido y sin confirmar — es previo
a este cambio y quedó tal cual; si se regenera ese archivo, revisarlo.

Detalle de CSS que hay que respetar si se tocan estos marcos: `.p-card:hover`
reemplaza el `box-shadow` **completo**, así que `.p-card--lead:hover` y
`.p-card--area:hover` tienen que repetir el filete además de la sombra, o el
filete desaparece al pasar el cursor. Mismo patrón en `.cre--lead`/`.cre--area`
de `torneo/index.html`.

**Otro desfase que conviene tener presente**: el respaldo embebido de
`index.html` (el literal JS `CLUB_DATA` + las tarjetas estáticas) tiene **12
personas** y `club.json` tiene **15** — faltan ahí Samuel Rodríguez Arnolds,
Gabriela Domínguez y Victoria Espinoza. No se nota en vivo porque `club.json`
pisa el respaldo al cargar, pero significa que **a Samuel no se le pudo poner
la marca en el respaldo** (no existe en él). Es previo a esta sesión.

**Sección de creadores, segunda pasada.** Orden pedido por Francisco: Sáez,
Francisco, Agustín, Manuel, Disi, Solís (antes iban en orden narrativo).
Aportes nuevos: Agustín pasó de "capacitación en Bloomberg" a
"**infraestructura digital y datos de Bloomberg**"; Francisco de "co-creador"
a "**infraestructura digital y la plataforma web**"; Manuel a "**comunicación
y coordinación**"; y a Solís se le quitó lo de la arquitectura, quedando
**sin línea de aporte** (decisión explícita de Francisco: prefirió dejarlo en
blanco antes que inventarle otro mérito). Por eso `aporte` es **opcional** en
`torneo.creadores` — si falta, no se dibuja el `<p>`.

**Las dos correcciones se propagaron a todo el sitio**, no solo a la sección
de creadores, porque son correcciones de hecho y dejarlas en otras páginas
sería publicar algo que ya sabemos que está mal:
- **Solís no diseñó la arquitectura del torneo** — fuera de su `detalle`, su
  bio y sus hitos, en `club.json` y `miembros.json`.
- **Francisco no es "co-creador"** — *todos* los del área lo son, así que
  destacarlo solo a él engañaba. Su crédito quedó como infraestructura
  digital y plataforma web, en `detalle`, bio y hitos.

Queda un rastro a propósito en `datos/miembros.demo.json`, que está fuera de
uso como fuente.

**Inconsistencia conocida que Francisco decidió NO tocar por ahora**: la bio
de Jhosep García (Vicepresidente) sigue diciendo que **él** lidera el área
Valuation, aunque el líder confirmado es Samuel, que es quien lleva el marco.
Preguntar antes de cambiarla.

## Tercera tanda del 2026-08-27: mejoras al torneo (6 de 7 ideas propuestas)

Tras arreglar la sección de creadores (ver la tanda anterior), Francisco pidió
una lista de mejoras para la página del torneo y luego pidió implementarlas
**todas menos una**. La que quedó fuera a propósito es el **aviso de dato
viejo** (un chip que avisara si el pipeline no corrió un viernes): decisión
explícita suya, no está pendiente.

Antes de proponer nada se verificó qué ya existía; varias ideas se descartaron
ahí mismo por estar hechas (el desglose de puntos por métrica con barras ya
estaba en la ficha, los deep links por equipo ya funcionaban con `replaceState`).

### 1. Vista previa propia por equipo al compartir el link

El deep link `torneo/index.html#beta-capital` ya existía, pero las etiquetas
Open Graph son las de la página completa: los 54 equipos mostraban la misma
tarjeta genérica en LinkedIn/WhatsApp. Con 145 inscritos, ese era el canal de
difusión más grande del torneo desaprovechado.

GitHub Pages no puede armar las etiquetas al vuelo, así que se generan de
antemano: `generar_paginas_equipo.py` escribe **una micro-página por equipo** en
`torneo/e/<id>.html` cuyo único trabajo es llevar las etiquetas correctas
(`<title>`, `og:title`, `og:description` con puesto/puntaje/retorno/semana,
`og:image`) y **redirigir al ranking real**. Detalles que importan:

- **`location.replace()`, no `href`**: si no, la intermedia queda en el
  historial y el botón "atrás" rebota y devuelve al ranking, dejando al
  visitante atrapado. Verificado: `history.length` queda en 2, no en 3.
- **`noindex,follow` + `canonical` al ranking**: son 54 páginas casi idénticas y
  no deben competir con el ranking en Google. Los rastreadores de redes sociales
  ignoran `noindex` y leen las `og` igual, que es justo lo que sirve.
- **URLs absolutas** en `og:image`/`og:url`: los rastreadores de LinkedIn y
  WhatsApp no resuelven rutas relativas. El dominio sale de `config.sitio` de
  `club.json` si está lleno (hoy está **vacío**) y si no cae a
  `https://feninvestmentgroup.com`, el del CNAME del repo de deploy.
- **Se reescriben enteras cada corte** (el puesto va en el texto) y las de
  equipos que salieron del torneo se borran solas, para no dejar links vivos
  mintiendo.

La **imagen** la genera aparte `generar_og_equipos.js` (Node + Chrome por CDP
crudo, mismo patrón que `grabar_pantalla_facultad_1_capturar.js`). No dibuja
nada nuevo: llama a `drawLi` por el gancho `window.__figCards`, o sea usa **la
misma tarjeta de LinkedIn** que la página ya ofrece en "Comparte tu resultado"
— que además mide 1200x627, exactamente la medida de una vista previa. Si se
rediseña una, cambia la otra.

**Es un paso opcional y separado a propósito, por peso**: son 54 JPG de ~57 KB
(3,1 MB por corte) que se reescriben cada semana, y git guarda cada versión.
Sin imágenes las micro-páginas funcionan igual y caen a `/og-image.png`,
conservando lo que de verdad diferencia una vista previa de otra, que es el
título ("Beta capital · 1° de 54").

### 2. `torneo/pantalla.html` ahora se recarga sola

La pantalla de las TV corre en bucle sin nadie delante: el viernes que se
publica el corte nuevo no había quien la recargara y seguía mostrando el
anterior hasta que alguien se acordaba. **Verificado que no tenía ni un
`setInterval` ni un `location.reload`.**

Ahora cada 5 minutos vuelve a pedir `torneo.json`. Tres decisiones de diseño:

- **El cambio queda EN ESPERA hasta que el ciclo de animación da la vuelta**
  (`t < prev` en el bucle de `arrancar()`). Cambiar a mitad de una transición se
  ve como una falla delante de la gente; el ciclo dura 42 s, nunca espera mucho.
- **Si la red se cae no se toca nada**: se queda con el último corte bueno. Lo
  mismo si el archivo llega a medio publicar (sin equipos): se descarta.
- **Apagado mientras se graba** (`window.__manual()`): el guion de grabación
  necesita que los datos no se muevan debajo.

`pantalla-facultad.html` **no** se tocó: esa no es una pantalla en vivo, es la
fuente del video semanal, y un refresco ahí solo podría arruinar una grabación.

### 3. Carga en dos partes de `torneo.json`

Medido sobre el corte de la semana 15: el archivo completo pesa **27,7 KB
comprimido** y el `historial` semanal es el **75%** de eso — pero solo hace
falta al abrir una ficha, el comparador o el replay. `generar_tabla.py` deriva
`datos/torneo-tabla.json` (el mismo sin historial, **7,1 KB comprimido**), que
es lo que la página pide primero.

El historial se trae después: **de fondo con `requestIdleCallback`** para que
abrir una ficha sea instantáneo, **salvo** que el visitante tenga `saveData` o
venga en 2G, donde se espera a que lo pida de verdad — que es justo el caso en
que ahorrar esos 20 KB importa.

Como `torneo-tabla.json` es un **archivo derivado**, tiene dos salvavidas:

1. si no existe, se carga `torneo.json` completo y todo funciona como siempre
   (el camino viejo sigue entero);
2. si existe pero su `corte`/`semana`/nº de equipos no calza con el completo,
   al llegar el completo **se repinta todo con él**. Quedarse atrás se corrige
   solo y nunca queda un dato viejo en pantalla.

Los dos casos se probaron de verdad en Chrome headless (borrando el derivado, y
ensuciándolo con otro corte y 10 equipos falsos: se auto-corrigió a los 54
reales con el score correcto).

**Regresión que esto causó y hay que tener presente**: las tarjetas y videos
(`descargarPng`, `grabarVideo`, `descargarHtml`) dibujan la trayectoria desde
`t.historial`. Con la carga en dos partes salían con el cartel *"trayectoria
disponible desde la semana N"* si el historial aún no había llegado. **Lo
detectó el propio generador de imágenes OG**, que produjo una primera tanda de
tarjetas sin curva. Las tres funciones quedaron envueltas en `conHistorial()`.
Si mañana se agrega otra cosa que lea `historial`, envolverla igual.

### 4. La tabla se puede ordenar por columna

Click en **SCORE / 100** o **RET. RELATIVO** reordena; volver a pulsar invierte.
POS es el orden oficial y el de entrada. Los encabezados son `<button>` de
verdad (los alcanza el tabulador) y el estado va en `aria-sort` del
`role="columnheader"`; la flecha es un `<i>` `aria-hidden`, puro adorno.

**Ordenar NO renumera a nadie**: la columna POS sigue mostrando el puesto
oficial de cada equipo, porque el ranking del torneo es uno solo y no depende de
cómo mire la tabla el visitante. Verificado: ordenando por retorno relativo las
tres primeras filas muestran POS 3, 1 y 8.

### 5. La tabla ya se anuncia como tabla

Eran 54 filas de `div`s con grid: un lector de pantalla las leía como texto
suelto, sin columnas ni encabezados. **No se pasó a `<table>` real a propósito**
— el diseño depende de `grid-template-columns` (incluido el colapso a 3 columnas
en móvil), y poner `display:grid` sobre elementos de tabla les **borra** los
roles ARIA implícitos en los navegadores, que es la trampa clásica. Se pusieron
los roles explícitos (`table` / `row` / `columnheader` / `cell`), que dan el
mismo resultado sin tocar una línea de layout.

De paso la fila dejó de ser un `<button>` gigante y el nombre del equipo pasó a
ser un **`<a href="#id">` real**: le da al teclado un destino, al lector de
pantalla un nombre corto ("Beta capital" en vez de la fila entera leída de
corrido) y al visitante un link que puede copiar con botón derecho. El clic lo
sigue atendiendo el JS.

También se agregó un **`hashchange`**, que antes no existía: pegar un link con
`#equipo` ya abierta la página, o el botón atrás, ahora funcionan. Ojo:
`openTeam`/`closeTeam` usan `replaceState`, que **no** dispara `hashchange`, así
que no hay bucle — por ahí solo entran los cambios que hace el visitante.

### 6. Hitos de trayectoria en la ficha

Bloque nuevo `#tmHitos` sobre el gráfico, derivado del `historial` que
`torneo.json` ya guarda — no pide ningún dato nuevo al pipeline: mejor puesto,
peor puesto, mejor score, "desde su peor semana +N puestos" (solo si de verdad
ganó) y "racha sin ceder puestos" (solo desde 2 semanas). Ojo con el sentido de
"mejor": en posiciones el mejor es el **menor**, al revés que en puntos.

### La rutina semanal quedó así

```
python generar_torneo.py --excel <Excel del corte> --semana N --corte "..."
python generar_tabla.py               # derivado que pinta la tabla
node generar_og_equipos.js            # OPCIONAL: las imágenes (ver su peso)
python generar_paginas_equipo.py      # micro-páginas por equipo
python verificar_sitio.py             # chequeo final
```

`verificar_sitio.py --arreglar` regenera los derivados por su cuenta (nunca toca
datos ni HTML escrito por una persona).

### Lo que encontró el verificador en su primera corrida

Compara las menciones escritas a mano de "N equipos" contra `datos/torneo.json`
y sacó 4. Tres son correctas como están (la bio de Agustín dice "capacitó a más
de 65 equipos", que es acumulado y no el conteo del torneo — está en `club.json`
y `miembros.json` —, y un comentario de código que dice "~55 equipos"). La
cuarta es real y **sigue en vivo**:

> `datos/club.json` → `historia[]` → **"Capítulo IV · 2026"** dice **"59 equipos
> y más de 150 estudiantes"**, cuando el torneo quedó en 54.

Esto es lo que Francisco venía pidiendo que se le recordara. **Trampa que costó
una afirmación equivocada en esta misma sesión**: en `index.html` el bloque
estático y el literal JS `CLUB_DATA` **ya dicen 54**, así que mirando solo ahí
parece corregido — pero `club.json` los pisa en runtime y es el que se ve.
Confirmado con `curl` contra `feninvestmentgroup.com/datos/club.json`. Para
verificar un texto de este sitio, mirar el JSON que lo alimenta, nunca el
fallback. **No se cambió**: el número correcto para un párrafo que describe el
lanzamiento en pasado es una decisión de Francisco, no nuestra.

### Verificación

Todo en Chrome headless por CDP crudo (Chrome de la máquina + WebSocket nativo
de Node, sin instalar nada), **sin un solo error de consola** en ninguna
corrida: 54 filas desde el derivado, roles ARIA, orden por las dos columnas con
`aria-sort`, POS que no se renumera, ficha con los 5 hitos y la curva, replay
con sus 54 filas, comparador con curva, deep link directo al cargar, navegación
por hash, botón atrás, foco de teclado en el nombre, micro-página que redirige
al equipo correcto sin ensuciar el historial, los dos salvavidas del derivado, y
la recarga de la pantalla con corte nuevo + caída de red.

## Cuarta tanda del 2026-08-27: el gráfico del hero de `index.html`

Francisco lo miró y dijo que "no debería verse así", con la sospecha de que el
conjunto del torneo le estaba rentando más que el ACWI. Tenía razón en que algo
estaba mal, pero por dos motivos distintos del que él pensaba.

**Los números reales del corte de la semana 15** (promedio del campo `ret` del
historial, que ya viene acumulado since-inception, contra `acwi[].ret`, que está
en las mismas unidades):

| | S5 | S10 | S13 | S14 | S15 |
|---|---|---|---|---|---|
| ACWI | +0,70% | −0,24% | +3,90% | +4,45% | s/d |
| Promedio de los 54 | +3,19% | +0,28% | +3,39% | +4,49% | +3,56% |
| Promedio del top 5 | +5,40% | +4,69% | +9,23% | +10,15% | +10,11% |

O sea: el promedio del torneo **le gana al ACWI en 9 de las 10 semanas
comparables**, pero la ventaja se fue cerrando hasta **+0,04 puntos** en la S14
—un empate— y en la S15 cae a +3,56% contra el último ACWI conocido de +4,45%.
La intuición de Francisco valía para casi todo el torneo, pero ya no para el
cierre.

### Dos defectos reales que sí había

**1. Los rótulos del extremo se encimaban.** Iban los dos clavados en la misma
X (`W-pr+10`) con la Y de su propia línea. Cuando las dos series terminan casi
juntas —que es exactamente lo que pasa cuando el torneo empata con el
benchmark, o sea el momento más interesante del gráfico— "FIG" y "ACWI"
quedaban uno encima del otro y se leía como un borrón. Ahora cada rótulo sigue
el final de SU línea (`fE.x+9` / `bE.x+9`) y, si quedan más cerca que el alto de
una línea, se separan a la fuerza la mitad cada uno.

**2. La portada iba una semana atrasada.** `datosReales()` recortaba las dos
series a la **intersección** de semanas con dato. Como el ACWI lo captura el
pipeline de Bloomberg aparte y suele llegar un corte después, el último corte
publicado no aparecía nunca en la portada: el hero mostraba hasta la S14 con el
torneo ya en la S15. Ahora el eje son las semanas con dato de EQUIPOS y la línea
del ACWI se corta donde se acaba su dato (`BMK_TOP`), que es el mismo criterio
que ya usaban `torneo/pantalla.html` y `pantalla-facultad.html`. El crosshair
dice "ACWI s/d" en esa semana en vez de mostrar un delta inventado.

### `HERO_TOP`: qué cartera va en el gráfico

Francisco dio una regla: mostrar el conjunto si le está rentando más al ACWI, y
si no, el top 5. Con los números de arriba la condición no se cumple, así que
quedó en **top 5**.

La constante `HERO_TOP` (arriba del IIFE del gráfico en `index.html`) manda:
`0` = promedio de todos los equipos, `N` = promedio del top N. **El título, la
leyenda, el rótulo del extremo de la línea, el crosshair y el `aria-label` se
escriben SOLOS desde ese número** (`rotularHero()` + `ETIQ_FIG`), así que no hay
forma de que el rótulo diga una cosa y la línea muestre otra. Para volver al
conjunto completo basta poner `0`.

Detalle que importa: el top N se recorta por la **posición del corte vigente**,
no se recalcula semana a semana. Un top N recalculado en cada semana sería otra
cosa —una cartera que rota— y quedaría siempre arriba **por construcción**, que
es justo lo que no queremos afirmar. Así, la línea es la trayectoria real de los
que hoy van primeros.

### Ojo al tocar `index.html`

El `index.html` del espejo **no es idéntico** al de este repo: difiere en 17
líneas del nav (allá no existe Miembros y FIG Woman sigue oculta, así que
"Comunidad ▾" se dejó como "Equipo" suelto). **No se puede copiar el archivo
entero al espejo.** Lo que se hizo fue portar solo el bloque del gráfico (desde
el comentario `Gráfico del hero + crosshair` hasta el `Conmutador de desks`) y
verificar después que el nav del espejo siguiera con "Equipo".

## Quinta tanda del 2026-08-28: nueve mejoras mas (todas menos CI)

Francisco pidio otra ronda de ideas y luego implementarlas **todas menos una**:
quedo fuera montar GitHub Actions, por decision suya. Las herramientas de
chequeo existen igual y se corren a mano.

### En el hero de `index.html`

**Cifras de cierre visibles sin interactuar.** El crosshair es `pointermove`:
en el telefono, donde entra la mayoria, **no existia**, y quien llegaba veia dos
lineas y ningun numero. Ahora arriba del lienzo va la fila `#ccCifras` con el
cierre de cada serie y la diferencia en puntos, rellenada por `pintarCifras()`
desde los mismos datos. Compara los **ultimos puntos de cada serie aunque sean
de semanas distintas** (el ACWI suele venir un corte atras) y lo dice: "TOP 5 ·
S15" contra "ACWI · S14". Esconder la semana buena del torneo para forzar un
empate de fechas seria peor.

**Crosshair con el dedo.** `pointermove` cubre mouse, lapiz y dedo, pero en
tactil el navegador solo lo emite si no interpreta el gesto como scroll — y
sobre un lienzo ancho casi siempre lo interpreta asi. Con
`touch-action: pan-y` el gesto horizontal pasa a ser nuestro y el scroll
vertical de la pagina sigue funcionando. Se agregaron `pointerdown`/`pointerup`/
`pointercancel` para que el toque pinte y el levantar el dedo limpie.

### En `torneo/index.html`

**La tabla se pliega a 10 filas.** 54 filas de golpe hacian del podio un detalle.
`LB_PLIEGUE=10` y un boton "Ver los 54 equipos". Dos reglas: con el **buscador
activo no se pliega** (esconderle a alguien su equipo del puesto 30 detras de un
boton seria absurdo) y una vez abierta **se queda abierta** — ordenar no la
vuelve a plegar.

**El rival mas cercano en la ficha** (`#tmRival`, `renderRival()`). "A 0.61
puntos de Aconcagua Capital (2°) · 5.13 de ventaja sobre B&JP Capitals (4°)".
Sale entero de la tabla que ya esta en memoria, asi que se pinta apenas abre la
ficha, sin esperar el historial. Dos casos borde resueltos: al **lider** se le
dice "Lidera por X sobre el 2°" y se le omite la segunda mitad, que le repetia
el mismo equipo; al **ultimo** se le omite la parte de abajo.

### Tipografias autoalojadas (`descargar_fuentes.py` + `usar_fuentes_locales.py`)

Las 14 paginas pedian 3 familias y 12 variantes a `fonts.googleapis.com` en cada
carga. Eso bloqueaba la primera pintada tras resolver DNS+TLS de dos dominios
nuevos, y le mandaba la IP de cada visitante a Google en un sitio que no pone ni
una cookie. Ahora viven en `fuentes/` (12 `.woff2`, 373 KB en el repo) y se
sirven del mismo origen.

Detalles que importan:
- **Solo los subconjuntos `latin` y `latin-ext`.** Google sirve ademas cirilico,
  griego y vietnamita: con `unicode-range` no costarian nada en carga, pero eran
  63 archivos y 543 KB versionados para siempre en un sitio escrito en espanol.
- **Las tres familias son OFL**, redistribuibles. Queda `fuentes/LICENCIAS.txt`.
- **Una pagina cargada baja ~179 KB de fuentes** (solo las variantes que usa) y
  **cero pedidos a Google** — verificado en el navegador.
- **NO se toco** el `<link>` a Google que va dentro de la tarjeta HTML que
  genera `descargarHtml()` en `torneo/index.html`: ese archivo se abre suelto en
  el computador de quien lo baja, donde `../fuentes/` no existe. Se distingue
  sola porque usa otra URL (menos pesos), y `usar_fuentes_locales.py` reemplaza
  solo la URL exacta del sitio.

### `verificar_paginas.js` — el chequeo que faltaba

`verificar_sitio.py` revisa los DATOS; nada revisaba las PAGINAS. Este abre las
15 en Chrome por CDP crudo y falla si alguna tira un error de consola o pide un
archivo que no existe. El bug de la seccion de creadores lo habria cazado el
mismo dia en vez de que lo encontrara Francisco probando.

**Trampa que hay que respetar: este sitio hace 404 a proposito.** Las fotos y
los logos se detectan SONDEANDO (`<slug>.jpg`, `.jpeg`, `.png`, `.webp` hasta
que uno carga; `1.jpg`, `2.jpg`... hasta que falla). Esos 404 son el mecanismo
funcionando, y van en `RUTAS_SONDEADAS`. Si se marcaran como error el chequeo
daria rojo siempre y se volveria ruido que nadie mira.

Encontro dos cosas en su primera corrida: `GUIA_DRIVE_FIG.html` era la unica
pagina sin `<link rel="icon">`, asi que el navegador pedia `/favicon.ico` y se
llevaba un 404 (corregido), y el peso real de cada pagina.

El presupuesto de peso mide **solo lo critico** — documento, CSS, JS, fuentes,
JSON — y deja fuera las imagenes: `index.html` y `eventos/index.html` pasan los
2 MB por las tiras de fotos, y meterlas haria que el aviso saltara siempre. Los
numeros locales son un TECHO: `python -m http.server` no comprime y GitHub Pages
si. Hay ademas un chequeo de tamano de fuente en `verificar_sitio.py`
(`TECHO_HTML_KB`), que corre sin navegador.

### `generar_sitemap.py` — sitemap.xml y robots.txt

No existia ninguno de los dos. El sitemap lleva **10 URLs**: las paginas reales.
Quedan fuera a proposito las 54 `torneo/e/*.html` (son redirecciones con
`noindex`; meterlas seria pedirle a Google lo contrario de lo que dicen sus
propias etiquetas), las dos pantallas (`pantalla.html` corre en bucle en un TV,
`pantalla-facultad.html` es la fuente del video), las guias internas y el 404.
La fecha de cada URL sale del `git log`, no del mtime, que en un clon reciente
es la fecha del clon.

Ojo: un `--` dentro de un comentario XML lo vuelve mal formado. El primer
sitemap generado no parseaba por eso.

### `sincronizar_espejo.py` — la pieza que faltaba hace tiempo

El espejo se copiaba a mano, y **ya habia divergido sin que nadie lo notara**:
las fotos de eventos de produccion eran las de julio, anteriores a la
renormalizacion del 23-ago. El script hace explicito lo que vivia en la cabeza
de alguien — que se copia, que no, y que difiere a proposito — y nunca borra
nada del espejo.

Lo que **no** viaja (con el motivo escrito al lado, en `NO_SE_COPIAN`): la
carpeta `miembros/` y sus datos, que todavia no se publican; las herramientas de
datos y de video; las guias internas.

Lo que **difiere a proposito y nunca se pisa** (`DIFIEREN`): `index.html`, cuyo
nav en el espejo no tiene Miembros ni FIG Woman. Para portar un cambio hay que
llevar solo el bloque tocado, como se hizo con el grafico del hero y con el
`<link>` de las fuentes.

Dos cosas que aparecieron al escribirlo y conviene no olvidar:
- **`MAPA_CONTENIDO_FIG.html` del espejo tiene dos scripts propios** que limpian
  la URL (le sacan `/index.html` y el `#`). Copiar la version de aca se los
  borraria: quedo en `NO_SE_COPIAN`.
- **`datos/club.json` difiere en 400 lineas pero solo por formato.** Comparados
  como datos, la unica diferencia real es `config.sitio: ""`, que aca existe
  vacio. **Se dejo vacio a proposito**: el propio comentario de
  `miembros/index.html` explica que con `config.sitio` vacio se usa el origen
  del navegador, que es lo correcto cuando la pagina ya esta publicada donde
  corresponde. Llenarlo haria que un server local generara links de produccion.
  Los scripts que necesitan el dominio absoluto caen a
  `https://feninvestmentgroup.com` por su cuenta.

### La rutina semanal, actualizada

```
python generar_torneo.py --excel <Excel del corte> --semana N --corte "..."
python generar_tabla.py
node generar_og_equipos.js            # OPCIONAL: las imagenes de vista previa
python generar_paginas_equipo.py
python generar_sitemap.py
python verificar_sitio.py             # datos y derivados
python -m http.server 8000            # en otra terminal
node verificar_paginas.js             # las paginas en un navegador de verdad
python sincronizar_espejo.py --aplicar
```

### Verificacion

Las **15 paginas de `fig-web` y las 13 del espejo** cargan sin un solo error de
consola ni archivo faltante, con las fuentes locales y cero pedidos a Google.
Probado ademas a mano en headless: cifras del hero, pliegue de la tabla (que el
buscador no lo active y que ordenar no lo revierta), linea del rival en el
lider, en un equipo del medio y en el ultimo, y que el nav propio del espejo
siguiera intacto despues de portarle el cambio de fuentes.

## Sexta tanda del 2026-08-28: rendimiento en telefono y ajustes de movil

Francisco pidio "mejoras de optimizacion para PC y para telefonos sin perder
calidad, y mejoras de diseno". Todo quedo **aplicado en local y SIN commit**:
el pidio revisarlo primero.

### Lo que se midio antes de tocar nada

Chrome real emulando telefono (4G lento, 1.6 Mbps + CPU 4x) y PC. Primera
pintada y peso total por pagina:

| | FCP movil antes | FCP movil despues | peso antes | despues |
|---|---|---|---|---|
| `index.html` | 620 ms | ~900 ms* | **2284 KB** | **173 KB** |
| `eventos/` | 1804 ms | 732 ms | **2122 KB** | **70 KB** |
| `torneo/` | 2540 ms | 660 ms | 400 KB | 166 KB |
| `miembros/` | 2764 ms | 728 ms | 244 KB | 88 KB |

*El FCP de la portada oscila entre 600 y 1300 ms entre corridas; no hay
regresion, es el ruido de la medicion. Los pesos salen de
`verificar_paginas.js` y son un TECHO (el server local no comprime).

### 1. Las imagenes: `generar_imagenes_web.py` (nuevo)

**El hallazgo mas grande.** `.ev-bg` de `eventos/index.html` pedia el JPG
original (250-330 KB) para pintar el fondo de una tarjeta de 400px, tapado
ademas por `.ev-veil`. Con diez eventos eran ~1,9 MB tirados. La tira de la
portada (`.photo-marquee`) hacia lo mismo, y se dibuja **al 13% de opacidad y
en escala de grises**.

El script deriva, sin tocar los originales:

```
fotos/eventos/<ev>/<n>.webp        1600px q82  galeria y lightbox
fotos/eventos/<ev>/mini/<n>.webp    720px q72  fondos de tarjeta y tira
fotos/directiva/<slug>.webp         800px q82  ficha de persona
fotos/directiva/mini/<slug>.webp    240px q78  avatares
datos/fotos.json                    manifiesto: que hay y cuanto mide
```

Ejemplo real: `visita-santander-2026/1.jpg` 325 KB -> `1.webp` 167 KB ->
`mini/1.webp` **33 KB**. Los 34 JPG de eventos (8,8 MB) pesan 4,5 MB en
WebP grande y 1,0 MB en miniatura.

**Todo consumidor cae al `.jpg` si falta el `.webp`** (navegador viejo, o una
foto subida despues de la ultima corrida). El manifiesto es un ATAJO, no un
requisito: si no esta, el sondeo de siempre sigue funcionando — y ademas
permite declarar `width`/`height` en la galeria, que antes saltaba al cargar.

**Trampa que costo una regresion silenciosa**: `miembros/index.html` llama a
`probeFoto` desde DOS lugares — `montarAvatares()` y los asientos del SVG de
la mesa (`[data-foto]`). Se cambio solo el primero y la mesa siguio bajando
los retratos de 800px: 490 KB en avatares de 20px. Se detecto listando los
recursos reales que baja la pagina, no leyendo el codigo.

### 2. `torneo.json` se bajaba DOS VECES en la portada

El ticker del pie y el grafico del hero son IIFE independientes y cada uno
hacia su `fetch`: 205 KB x 2 = 410 KB, mas de la mitad del peso de la portada
en un telefono. Ahora `window.figTorneoJSON()` memoiza la promesa y los dos
comparten la misma.

### 3. `cache:"no-store"` -> `no-cache` en los 31 fetch de `datos/*.json`

`no-store` PROHIBE guardar: cada visita, cada pagina y hasta el boton atras
rebajaban el archivo entero. `no-cache` revalida siempre —la frescura es
identica, nunca se muestra un corte viejo— pero si no cambio, la respuesta es
un 304 sin cuerpo. De paso se elimino el ultimo `force-cache`, que es el que
habia causado el bug de la seccion de creadores.

### 4. El preload de fuentes: PROBADO Y DESCARTADO

Parecia obvio adelantar los `.woff2` con `<link rel=preload>`. Medido, sale
**peor**: 856 ms sin preload contra 1684-1768 ms con el. El motivo es propio
de este sitio — cada pagina es un HTML monolitico de 150 KB con todo su CSS
adentro, asi que la primera pintada depende de que ESE archivo llegue, y el
preload se pone a competir por el mismo ancho de banda. El modo `--preload`
de `usar_fuentes_locales.py` quedo escrito y documentado con los numeros
**para que nadie lo vuelva a intentar a ciegas**. No usarlo.

`content-visibility` se descarto por lo mismo: se midio el DOM de cada seccion
y es chico (el peso esta en el CSS y el JS inline), asi que no habia layout
que ahorrar — y `#axPop` es `position:fixed` dentro de la seccion Torneo, que
un `contain` habria roto.

### 5. `optimizar_logos.py` (nuevo): 690 KB -> 231 KB en `logos/`

`fig-oro.png` pesaba 38 KB y esta en el preloader y el nav de las 14 paginas.
Un logo no es una foto: 1673 colores en 500x500. Guardado con paleta de 256
queda en 8 KB con una diferencia media de **0,12 sobre 255**, invisible.

**Lo importante es el umbral, no la conversion.** El script mide la diferencia
contra el original y solo escribe si queda bajo `--umbral` (1,0 por defecto).
Asi `logos/fen.png` (13.504 colores, degradados) se dejo intacto: daria 11,42
de diferencia, que si se ve. `fen-escudo.png` daria 141. Los dos quedaron
fuera solos, sin que nadie tuviera que acordarse.

Mismo nombre y mismo formato, asi que **no hubo que tocar una sola linea de
HTML**.

### 6. Diseno de telefono

- **El ticker se tapaba a si mismo**: "TORNEO · SEMANA 15" ocupaba 150 de los
  390px y de la cinta solo se leia un pedazo de nombre sin principio ni fin.
  Bajo 640px se abrevia a "S15" (dos spans, uno visible por ancho) y los items
  se juntan. Ojo: hubo que poner `gap:0` en `.tk-tag`, porque el gap del flex
  metia un espacio en medio de "S15".
- **Las cifras del hero** se partian 2+1 con la ultima suelta. Ahora en
  vertical son columnas iguales, cifra sobre rotulo, con filete. Se aplico
  igual en `index`, `eventos`, `fiw` y `valuation` con
  `repeat(auto-fit,minmax(0,1fr))`, que reparte las que haya sin depender de
  cuantas sean.
- **Los tres chips del torneo** quedaban apilados en tres filas de anchos
  distintos. Bajo 640px pierden la capsula y son una linea de datos. Dos
  detalles que costaron dos pasadas: el separador es una **barra**, no un
  punto (la fecha ya trae puntos: "21 · AGO · 2026"), y va en `::after` del
  dato anterior, no en `::before` del siguiente, o la segunda linea empezaba
  con una barra suelta.

### 7. Objetivos tactiles (WCAG 2.2) y contraste

Se midio con un script propio. **El contraste pasa AA en todo el sitio** — no
hubo nada que corregir ahi. Los objetivos tactiles bajo 24px si: los enlaces
del footer (17px), el credito del pie (14px), el input del buscador de
miembros (20px de alto dentro de una caja de 48) y el link del ticker.

Todos se arreglaron con **padding + margen negativo que lo compensa exacto**,
asi que el dibujo no cambia ni un pixel y lo unico que crece es donde se puede
tocar. Ojo con un error que se cometio y hubo que deshacer: al agregar
`margin` a `.demo-bar a` se borro su `margin-left:auto` y el link perdio la
alineacion a la derecha; quedo como `margin:-6px -10px -6px auto`.

**Falso positivo que NO se toco**: los nombres de equipo de la tabla del
torneo miden 23px, pero el objetivo real es la fila entera (`.lb-row`, ~55px,
con su propio listener). Cambiarlos habria sido arreglar algo que no estaba
roto.

**La mesa de `miembros/` tampoco se toco**: parecia cortada por los costados
en las capturas, pero se midio el bbox de cada texto contra el viewBox y
**ningun elemento se sale**. Esta pegada al borde a proposito — el propio
codigo lo explica: a 390px cada pixel cuenta.

### Efecto colateral que conviene saber

Ahora que la tira de fotos de la portada pesa 30 KB por imagen en vez de 300,
**en el telefono alcanza a cargarse de verdad**: el fondo del hero, que antes
casi siempre se veia navy liso porque las fotos no llegaban a tiempo, ahora
muestra las fotos al 13% como estaba disenado. Se ve bien y el texto se lee,
pero es un cambio visible respecto de lo que se veia antes en movil — si no
gusta, se baja la opacidad de `.photo-marquee` en el `@media(max-width:640px)`
que ya existe.

### Como seguir

Nada esta commiteado. Para revisar: `git status` y `git diff`. Para publicar
haria falta el commit en `panchoscky/fig-web` y despues
`python sincronizar_espejo.py --aplicar` (ojo: `index.html` NUNCA se copia
entero al espejo, hay que portar los bloques tocados — el ticker, las cifras
del hero y la tira de fotos son tres tramos separados).

**Las 15 paginas cargan sin un solo error de consola ni archivo faltante**
(`verificar_paginas.js`) y `verificar_sitio.py` sale sin errores, con los 3
avisos de conteo de siempre (los "65 equipos" de la bio de Agustin, que son
acumulados, y el comentario de codigo con "~55 equipos").

La rutina semanal gana dos pasos, los dos **opcionales y solo cuando se
agregan imagenes**:

```
python generar_imagenes_web.py      # al subir fotos nuevas
python optimizar_logos.py --aplicar # al subir un logo nuevo
```

## Septima tanda del 2026-08-28: menos pedidos, no menos bytes

Continuacion directa de la sexta. Francisco pidio seguir optimizando. Igual que
la anterior, **aplicado en local y SIN commit**.

La sexta tanda bajo el PESO. Esta baja la CANTIDAD DE PEDIDOS y el momento en
que se hacen, que en un telefono en 4G es lo que de verdad se siente: la
latencia de cada ida y vuelta pesa mas que los kilobytes.

Medido sobre la portada sola, en frio (`--solo`, ver mas abajo):

| | antes | despues |
|---|---|---|
| pedidos a `datos/` | 7 | **5** |
| `torneo.json` en la portada | 205 KB | **4,3 KB** (derivado) |
| pedidos a `fotos/directiva/` | 12 | **0** |
| pedidos a `logos/industria/` | 12 (5 eran 404) | **0** |

### 1. `datos/torneo-portada.json`: el tercer derivado

La portada no muestra el ranking -- solo la cinta del pie (top 5) y el grafico
del hero (trayectoria promedio del top 5 contra el ACWI). Para eso bajaba los
54 equipos con sus metricas, su detalle de puntaje, sus integrantes y las nueve
cifras por semana de cada uno, y usaba **dos campos**.

`generar_tabla.py` ahora escribe los DOS derivados (mismo `_fuenteSha1`, un
solo chequeo los cubre, la rutina semanal no gana ningun paso). El nuevo se
queda con los `TOP_PORTADA` primeros y poda el historial a `{semana, ret}`:
**204,7 KB -> 4,3 KB, 98% menos.**

`figTorneoJSON()` en `index.html` pide ese y **se cae solo al archivo completo**
si no esta o si vino corto para `HERO_TOP` -- vale mas bajar 205 KB que dibujar
un "TOP 5" promediando cuatro equipos. `verificar_sitio.py` compara `HERO_TOP`
contra `topPortada` y **falla** si alguien los desalinea, porque ese desajuste
no se ve: el grafico sale perfecto, con el numero equivocado.

### 2. `window.figJSON(url)`: un pedido por archivo

`club.json` se pedia DOS veces en cinco paginas (los enlaces del pie y el
beacon de metricas, cada uno con su fetch) y `eventos.json` dos veces en dos.
Con `no-cache` la segunda vuelve 304 sin cuerpo, asi que casi no pesa -- pero
paga la ida y vuelta igual. **16 fetch colapsados a 8**, en seis paginas.

Guarda el TEXTO, no el objeto ya parseado: si dos bloques compartieran el mismo
objeto, uno que le agregue o le pise un campo se lo estaria cambiando al otro
sin que nadie lo note. Reparsear 23 KB cuesta una fraccion de milisegundo; ese
bug no.

### 3. El hallazgo: **sondear derrota a `loading="lazy"`**

Las miniaturas de la grilla de personas se resolvian con `probeFoto`/
`probeLogo`: un `new Image()` por tarjeta que iba probando extensiones y, al
acertar, copiaba la URL al `<img>`. El `<img>` tenia su `loading="lazy"` puesto
y **no servia de nada**: para saber SI hay foto hay que bajarla, asi que cuando
el navegador llegaba a decidir si la aplazaba, el sondeo ya la habia bajado
entera. Las 15 fotos de la directiva y los 6 logos de industria se descargaban
en cada carga de la portada, este o no §Nosotros en pantalla.

Dos arreglos distintos porque el respaldo es distinto en cada pagina:

- **`index.html`**: el monograma es una capa DEBAJO del `<img>`, asi que la
  cadena de candidatos se encadena en el `onerror` del propio `<img>`
  (`montarMiniatura()`). El navegador aplaza de verdad, y si ningun candidato
  carga la clase `ok` nunca se pone y se ve el monograma, igual que antes.
- **`miembros/index.html`**: ahi el monograma es un `<span>` que se REEMPLAZA
  por el `<img>` recien cuando se sabe que la foto existe, asi que no se puede
  encadenar. Lo que se aplaza es el sondeo mismo, con un IntersectionObserver
  (`alAcercarse()`, `rootMargin:300px`). Importa en el directorio de 160
  personas, no en la carga inicial.

`probeLogo()` quedo sin ningun consumidor y se elimino; `probeFoto()` perdio su
parametro `mini` (la grilla era la unica que lo usaba) y quedo como uso
exclusivo del Expediente, donde sondear SI corresponde: necesita la URL antes
de armar la ficha y solo corre cuando alguien abre una tarjeta.

**Lo que NO se toco**: los 18 asientos de la mesa de `miembros/` (`[data-foto]`,
otra ruta) siguen sondeando al cargar, y esta bien: la mesa esta arriba, en
pantalla. Aplazar lo que ya se ve no ahorra nada y agrega un salto.

### 4. La tira de fotos de la portada arranca en idle

Es adorno: ocho miniaturas detras del hero, al 13% de opacidad y en escala de
grises. Desde la sexta tanda alcanzan a llegar en un telefono -- que era lo que
queriamos -- pero llegaban compitiendo por el ancho de banda con las fuentes y
el JSON del torneo durante la PRIMERA pintada, que es lo que el visitante si
esta esperando. Ahora espera al `requestIdleCallback`, y con `saveData` o en 2G
no arranca: el hero queda navy liso, exactamente como se veia antes de que las
miniaturas existieran.

### 5. Las fuentes: MEDIDAS Y YA ESTAN EN SU PISO

En una visita fria la portada baja 166,7 KB de tipografia -- mas que el HTML.
Vale la pena saber por que no se toco:

    Inter latin (variable, cubre 400-700)   47,1 KB
    Playfair Display latin, redonda         37,5 KB
    Playfair Display latin, BASTARDILLA     37,9 KB
    IBM Plex Mono latin 400 / 500 / 600     44,2 KB

- No bloquean la pintada (`display=swap`), asi que son ancho de banda, no FCP
  -- por eso el preload de la sexta tanda salia peor y quedo descartado.
- Se probo pedirle a Google Playfair como rango variable
  (`0,500..700`) en vez de las cinco variantes sueltas: **devuelve exactamente
  los mismos 4 archivos y los mismos 118,9 KB**. No hay nada que ganar ahi.
- La bastardilla parece un lujo de 37,9 KB hasta que uno mira donde se usa:
  `.hero h1 em` y `.h-sec em`, o sea el titulo de CADA seccion de casi todas
  las paginas. Es identidad visual, no decoracion suelta.

Sacar un peso de IBM Plex Mono (~15 KB) o la bastardilla es lo unico que
quedaria, y las dos son decisiones de diseno de Francisco, no optimizaciones.

### 6. Herramientas

- `verificar_sitio.py` tiene `revisar_portada_derivada()`: derivado al dia +
  el chequeo `HERO_TOP <= topPortada`. Probado a mano subiendo HERO_TOP a 20:
  falla con el mensaje correcto.
- `verificar_paginas.js --solo=index.html` revisa una sola pagina (prefijo, no
  "contiene", o `index.html` matchea las diez). **Sin esto no se puede medir
  nada**: las 15 paginas se mezclan en el mismo log del server local y no hay
  como saber quien pidio que.

### Trampa de medicion que costo un rato

`chrome --headless --virtual-time-budget=N --dump-dom` **baja igual todas las
imagenes con `loading="lazy"`**, esten o no en pantalla. Sirve para comprobar
que algo se DIBUJA, no para comprobar que algo se APLAZA -- ahi parecia que el
cambio no habia servido de nada. Para medir el aplazamiento hay que usar el
camino de `verificar_paginas.js` (CDP, ventana real, espera real) y contar los
pedidos en el log de `python -m http.server`.

## Octava tanda del 2026-08-28: el bug del panel de desk y una limpieza de SEO

Francisco reporto que al entrar a un area en `miembros/` "aparecia un marco
blanco y luego cargaba". El bug existia, era peor de lo que parecia, y buscarlo
destapo otras cuatro cosas visibles en produccion. **Esta tanda SI se commitea**
junto con la sexta y la septima, que seguian sin commitear.

### 1. El panel de desk se quedaba sin fondo (el bug reportado)

`.area` es `position:fixed;inset:0;overflow-y:auto` y su fondo vivia en un
`::before` con `position:absolute;inset:0`. Un absoluto dentro de un contenedor
que scrollea mide UN viewport y **se va con el contenido**: en cuanto el desk
era mas alto que la ventana, la mitad de abajo del panel quedaba transparente y
se veia la portada de la mesa por debajo -- el titular "La directiva sentada por
desk...", el buscador y el aviso, mezclados con las tarjetas de las personas.
Texto sobre texto, ilegible.

**No se ve en pantallas altas**, por eso nadie lo habia cazado: reproducido a
1200x650 con el desk PRT.

El fondo paso a `.area` directamente y el `::before` se elimino. El fondo de un
contenedor con `overflow:auto` **no** scrollea con su contenido, asi que ahora
cubre siempre, sin importar cuanta gente tenga el desk.

### 2. `color-scheme:dark` -- faltaba en las 15 paginas

En un sitio 100% navy, Chrome dibujaba las barras de scroll nativas con la
paleta CLARA: pista `rgb(241,241,241)` cruzando la linea de tiempo de
`eventos/` y bajando por el borde de cada pagina. Tambien pinta el lienzo en
blanco antes de la primera pintada. Es la fuente mas probable de cualquier
"destello blanco" que se vea en este sitio.

Con `color-scheme:dark` en `:root` las barras pasan a pista `rgb(44,44,44)` con
pulgar `rgb(159,159,159)` -- medido, no supuesto.

De paso, `html{scrollbar-gutter:stable}`: seis paginas hacen
`document.body.style.overflow="hidden"` al abrir un panel u overlay, y sin el
hueco reservado la pagina entera se corre 15px al costado cada vez.

### 3. El aviso de "Demostracion" se estaba mostrando con los datos reales

`<div id="demoBar" hidden>` NUNCA se ocultaba: el `display:none` del atributo
`hidden` viene de la hoja del navegador, y `.demo-bar{display:flex}` se lo comia.
Cualquiera que entrara a Miembros leia "personas que no existen" arriba de la
directiva real -- medido con `getComputedStyle`: `display:flex`, 620x105 px.

Se blindo la clase entera con `[hidden]{display:none!important}` en las 15
paginas. Se reviso el resto: era el unico `[hidden]` roto del sitio, pero la
trampa vuelve cada vez que alguien le pone `display` a algo que tambien usa
`hidden`. **Ojo en `torneo/index.html`**: el reset `*{margin:0...}` aparece DOS
veces y la segunda vive dentro de la tarjeta HTML descargable -- esa no se toca.

Verificado que `?demo=1` sigue mostrando el aviso.

### 4. El buscador prometia filtros que la base no puede responder

El placeholder decia `nombre, ticker, PRT, 2025...` y el rotulo "o generacion",
pero `generacion` viene **nula en las 160 personas** y `estado` es "activo" en
todas: escribir "2025" o "ALUMNI" devolvia **0 de 160**, que se lee como un
buscador roto.

`rotularBuscador()` arma el placeholder y el rotulo desde lo que la lista trae
de verdad. Cuando la planilla del Drive gane las columnas `area` y `generacion`,
se enciende solo. Verificado: con `?demo=1` (que si trae generaciones) el
placeholder vuelve a ofrecer "2025" sin tocar codigo.

**Lo que esto NO arregla, porque es dato y no codigo**: de las 160 personas,
**146 no tienen `area`**, 160 no tienen bio ni foto y 100 no tienen LinkedIn.
Por eso los 4 desks solo muestran a la directiva y el boton "+N miembros sin
cargo" no aparece nunca. Se arregla en la planilla, no aca.

### 5. Notas internas que estaban a la vista del publico

- `eventos/`: la charla con Roberto Bonifaz mostraba **"Resumen por completar."**
  en la tarjeta (su `resumen` esta vacio en el JSON). Ahora un resumen que falta
  se **omite**; no se anuncia.
- Las 10 tarjetas decian "PARTICIPANTES POR CONFIRMAR" (`participantes` esta
  vacio en los 10 eventos): una nota interna repetida diez veces. El hueco queda
  vacio -- `.ev-foot` es `space-between`, asi que el enlace sigue a la derecha.
- El overlay decia "Por confirmar - **se cargan desde el Excel**". Quedo solo
  "Por confirmar".
- Mismo arreglo en `valuation/index.html`, que comparte el molde de tarjeta.

### 6. Los filtros de `eventos/` se leian como un error

Tres filas seguidas que empezaban con una pildora dorada casi identica ("Todos",
"Todos", "Todos los anos"). Ahora cada fila lleva su rotulo mono -- TIPO /
CUANDO / ANO -- con `min-width` para que las pildoras arranquen alineadas, y el
chip del ano perdio el "los anos", que paso a ser redundante. `#yearRow:empty`
sigue funcionando porque `buildYearRow()` limpia la fila entera cuando hay menos
de dos anos.

### 7. SEO: lo que faltaba de verdad

- **`rel="canonical"` no existia en ninguna pagina.** El sitio se sirve desde
  DOS dominios (produccion y el espejo de GitHub Pages): para un buscador eran
  dos copias del mismo contenido compitiendo entre si. Las 10 paginas publicas
  ya declaran la suya, mas su `og:url`.
- **`hreflang`** entre `/` y `/en/` (+ `x-default`), que tampoco estaba.
- **`desafio/` y `juego/` no tenian NINGUNA etiqueta Open Graph**: compartidas
  por WhatsApp o LinkedIn salian sin titulo ni imagen. Ahora llevan el bloque
  completo.
- **JSON-LD**. En `index.html` va un `Organization` escrito a mano, con datos
  ESTABLES nada mas (nombre, logo, redes) -- y `verificar_sitio.py` compara sus
  `sameAs` contra `config.urls` de `club.json` y **falla** si alguien cambia una
  y no la otra, porque un JSON-LD desfasado no se ve en pantalla. En `eventos/`
  los `Event` se **arman desde `eventos.json`** en vez de escribirse: un bloque
  copiado quedaria viejo al siguiente evento, y publicar una fecha equivocada en
  Google es peor que no publicar nada. Solo entran los eventos con resumen y
  lugar cargados -- hoy 9 de 10.

### 8. Foco de teclado al salir de un desk

Cerrar un desk dejaba el foco en el `<body>`: quien navega con teclado volvia al
principio de la pagina en vez de al desk del que salio. `entrar()` guarda el arco
en `VOLVER_A` y `salir()` se lo devuelve. Verificado: tras "Volver a la mesa" el
`activeElement` es el arco `TRD`.

### Lo que se miro y NO se toco

- **El panel de desk NO se cierra "de golpe"**: `.mesa-holder` ya tiene
  `transition` de opacidad, transform y filter, asi que salir es un crossfade.
  Se reviso el CSS antes de agregar una animacion que no hacia falta.
- **`datos/miembros.demo.json`: BORRADO** (Francisco lo pidio el mismo dia,
  despues de leer esta lista). Era la tarea pendiente #27 de la hoja de ruta:
  se borra cuando la base real esta cargada, y lo esta. `generar_miembros.py
  --demo` lo vuelve a escribir cuando haga falta. `bajarBase()` en
  `miembros/index.html` hace que `?demo=1` **caiga a la base real** si el
  archivo no esta, en vez de dejar la pagina muerta con "La base de miembros
  aun no esta publicada"; el aviso de Demostracion no sale porque el archivo
  real trae `demo:false`.
- **`fotos/` pesa 17 MB** en el repo (originales JPG + los WebP derivados). Hoy
  no molesta; si sigue creciendo hay que decidir si los originales siguen
  versionados o pasan al Drive. Decision de Francisco.
- **Trading sigue sin lider declarado** (`liderArea`), que es lo unico que le
  falta a la jerarquia visual de la seccion Nosotros. Falta que Francisco lo
  confirme.

### Verificacion

`verificar_sitio.py` sin errores, con los 3 avisos de conteo de siempre y dos
chequeos nuevos en verde (`revisar_canonicas`, `revisar_datos_estructurados`).
`verificar_paginas.js`: las 15 paginas cargan sin un solo error de consola ni
archivo faltante. Ademas, a mano en Chrome: panel de desk scrolleado hasta abajo
sin filtracion, barras de scroll medidas en RGB antes y despues, aviso de
demostracion oculto con datos reales y visible con `?demo=1`, placeholder que se
adapta a la base, JSON-LD de eventos con 9 fichas y la fecha correcta, y el foco
que vuelve al arco.

**Nada de esto se llevo al repo de Manuel** -- Francisco pidio explicitamente no
tocarlo todavia. Cuando se quiera portar: `python sincronizar_espejo.py`, y ojo
con `index.html`, que NUNCA se copia entero (el canonical, el JSON-LD y el
`color-scheme` son tres tramos separados de la cabecera y el `<style>`).

## Novena tanda del 2026-08-30: `informe/index.html`, la pagina de analisis

Francisco pidio "un informe, con datos, graficos y demas del torneo de
portafolio, como una pagina extra". Es la pagina 16 del sitio.

### Que es

Un informe de analisis del Torneo Portafolio, distinto del ranking: `torneo/`
responde "quien va ganando", este responde "que muestran los datos". Ocho
secciones: resumen ejecutivo, el torneo frente al ACWI, dispersion de
resultados, riesgo vs retorno, movilidad del ranking, composicion del puntaje,
la tabla completa y metodologia.

**No tiene una sola cifra escrita a mano.** Todo se calcula en vivo desde
`datos/torneo.json`, incluido el texto de los cinco hallazgos del resumen: las
frases estan escritas alrededor de numeros que rellena el JS. Es la unica forma
de que un informe no quede desfasado del corte siguiente, que es exactamente
como mueren los informes escritos a mano.

Los cinco graficos son SVG generado en JS, sin ninguna libreria (el sitio no
tiene build step y la CSP no dejaria cargar una). Todos con tooltip al pasar el
cursor, leyenda y rotulos directos.

### Hallazgo real: hay DOS medidas de "le gana al indice" y no calzan

Escribiendo el resumen aparecio una contradiccion entre dos secciones, y no era
un error de redaccion:

- **`ret` − `acwi`** (retorno acumulado publicado menos el del indice): en la
  semana 14 quedan por delante **29 de 54** equipos.
- **`exc`** (el retorno en exceso de Bloomberg PORT, que es lo mismo que
  `retRel` y lo que alimenta el puntaje): quedan **15**.

La brecha por equipo es grande y sistematica, no un redondeo: para Beta capital
en la S14, la primera cuenta da +7,45% y la segunda +18,92%. **No esta
documentado en los datos con que base calcula PORT su retorno en exceso**, asi
que el informe no elige una ni inventa una explicacion: muestra las dos y deja
anotado en Metodologia que **el area de Portafolio tiene que confirmar cual es
la oficial** para comunicar resultados. Vale la pena preguntarlo, porque las dos
cifras cuentan historias distintas del torneo.

### Decisiones de los graficos

La paleta de series salio del **validador de paletas** (contraste, separacion
para daltonismo, piso de vision normal), no del ojo:

- **5 categorias** del desglose de puntaje: `#c98500 #3987e5 #199e70 #9085e9
  #d55181`. Pasa las cinco pruebas sobre el fondo `#101731`. Ojo con el ORDEN:
  las pruebas de separacion se corren sobre pares adyacentes, y varias
  ordenaciones de esos mismos cinco colores fallan (aqua junto a magenta da
  Delta-E 1.6 con deuteranopia, o sea se ven iguales).
- **Divergente** (polaridad sobre/bajo el indice, subio/bajo en la tabla):
  azul `#3987e5` / rojo `#e66767`, gris al medio.
- **Excepcion deliberada**: el par oro/azul del grafico de mercado son los
  tokens de marca que YA usan `torneo/pantalla.html` y el hero de `index.html`
  para "FIG vs ACWI". El validador los marca fuera de banda de luminosidad,
  pero su separacion es Delta-E 22.9 con daltonismo y 23.5 en vision normal
  -- muy sobre el piso -- y romper la lectura entre paginas costaba mas.

Tres cosas que se vieron recien al mirar las capturas, no al leer el codigo:

1. **La rampa secuencial del scatter va OSCURO→CLARO**, al reves de como se
   usaria sobre fondo blanco. Sobre el navy el paso mas claro es el que mas
   resalta, y con la rampa al derecho los que mas brillaban eran los ULTIMOS de
   la tabla.
2. **`ticksNice()` corta en 1,5/3/7 y no en 1/2/5.** Exigir el paso redondo
   inmediatamente mayor dejaba ejes de dos marcas (un rango de 11 puntos
   saltaba a pasos de 5).
3. El numero de la barra mas alta del histograma se encimaba con el rotulo
   "IGUAL AL INDICE". El rotulo quedo al costado de la linea del cero.

### Trampas de este sitio que volvieron a aparecer

- **La captura de pantalla completa sale vacia.** Los `.reveal` solo reciben la
  clase `in` cuando el IntersectionObserver los ve entrar en pantalla, asi que
  hay que scrollear cada seccion y esperar ~1s antes de capturar. Ya estaba
  documentado y volvio a pasar.
- **Un atributo de presentacion SVG pierde contra una regla CSS.** Poner
  `font-family` como atributo no hacia nada frente a `.ax-txt{font-family:mono}`;
  hay que usar el atributo `style`, que si gana.
- **`b:first-child` tambien matchea un `<b>` que abre un parrafo**, no solo el
  rotulo: frases como "el retorno en exceso" salian en versalitas mono a media
  oracion. Quedo como `div > b:first-child`.

### De paso

- `verificar_sitio.py` estaba dando **2 errores en `main` desde antes** de esta
  tanda: `torneo-tabla.json` y `torneo-portada.json` habian quedado atras
  respecto de `torneo.json` (venia del commit `8e03e98`, el que elimino en
  definitiva a los 5 equipos). Se corrio `generar_tabla.py`. Ahora sale sin
  errores, con los 3 avisos de conteo de siempre.
- La pagina entro al nav de `torneo/index.html` (escritorio y movil) y a
  `generar_sitemap.py` con prioridad 0.8. El sitemap quedo en 11 URLs.
- **`verificar_paginas.js` no corre en un contenedor como root**: le falta
  `--no-sandbox`. No se toco el script, porque en la maquina de Francisco anda
  bien; se uso una copia temporal con ese flag. Si alguna vez hay que correrlo
  en CI, ahi si convendria agregarlo condicionado a que el usuario sea root.

**Nada de esto se llevo al repo de Manuel.**

## Decima tanda del 2026-08-30: instrumentos, ingles y FIW fuera del espejo

Sesion preparando la reunion del area de Portafolio con BlackRock.

### `informe/` gana la seccion "07 · Instrumentos"

El informe respondia "que muestran los datos del ranking". Ahora tambien
responde **que compraron los equipos**, que es lo que le interesa a BlackRock:
4 cifras (96,4% de las operaciones en ETF de iShares, 199 ETF distintos, 14
bolsas en 7 divisas, 87,9% renta variable) y 3 graficos SVG — los 12 ETF mas
usados, mercados contra sectores, y factores/tematicos/apuestas pais.

**El dato viene de OTRO pipeline**, no del Excel semanal: sale del registro de
operaciones de Bloomberg, que procesa `src/analisis_etf.py` del repo
`torneo-bloomberg-oficial` (nuevo, mas `config/clasificacion_etf.csv` con los
202 tickers clasificados a mano por gestora/clase/mercado/tema). Escribe
`datos/etf.json`. Dos consecuencias que el codigo respeta:

- La seccion arranca `hidden` y solo se muestra si el fetch trae datos
  utilizables. Probado borrando el archivo: la seccion desaparece y el resto
  del informe sigue entero. Un dato opcional de otro pipeline no puede tumbar
  la pagina.
- **Su periodo NO es el del ranking.** El ledger llega al 2026-08-05 y el corte
  vigente es la semana 15 (21-ago). Se dice en el pie de cada grafico en vez de
  dejar que el lector suponga que es el mismo periodo.

Ojo con dos cifras que hay que confirmar antes de mostrarlas afuera (estan
detalladas en `INFORME_ETF_TORNEO.md`): cual es la medida oficial de "le gano
al indice" (29/54 por `ret−acwi` contra 16/54 por `exc`), y si las bases
permitian ETF fuera de iShares — hay 23 compras que no lo son, incluidas 2 de
IBM, que es una accion individual.

### `en/index.html`: "Tomorrow's Leaders" y estado real del torneo

- **"Forging Tomorrow's Elite" paso a "Forging Tomorrow's Leaders"** (pedido de
  Francisco), en el `<h1>` y en la `og:description`.
- Seccion nueva "Where it stands" con las cifras reales: 136 estudiantes, 812
  operaciones, 199 ETF, 14 bolsas, el ETF mas tenido (SOXX, 65% de los equipos)
  y los 58 puntos entre el primero y el ultimo. Es la pagina que se le muestra
  a un partner internacional, asi que vale que traiga datos y no solo relato.
- **No enlaza a `informe/`** a proposito: esa carpeta no se publica en el
  espejo, y un enlace ahi seria un 404 en produccion.

### FIW fuera del espejo: `despublicar_fiw.py` (nuevo)

Francisco pidio que desde el repo de Manuel **no se pueda acceder al area de
mujeres ni sea visible**. Hasta ahora solo estaban ocultos los ENLACES
(`FIW_TEMP_OCULTO`), que resulto ser bastante menos de lo que parecia: `/fiw/`
seguia respondiendo por URL directa, el sitemap se la declaraba a Google, y el
area se veia en el selector de desks de la portada, en el panel 04, en el
`<option>` del formulario de postulacion, en la tarjeta "Area 04" del ingles y
en el nav del 404 (ahi como enlace visible, no comentado).

El script **borra** `fiw/`, `datos/fiw.json` y `fotos/fiw/` del espejo y quita
el area de 6 paginas. Va como paso APARTE despues de `sincronizar_espejo.py`, no
como exclusiones dentro de el: si esos archivos quedaran en `NO_SE_COPIAN`, el
espejo dejaria de recibir todas las mejoras futuras de `eventos/`, `postula/`,
`valuation/`, `en/` y `404.html` solo para esconder una seccion.

**Los dos scripts son un par**: sincronizar primero, despublicar despues, y
`generar_sitemap.py` DENTRO del espejo al final. Como el segundo reescribe 5
archivos, el primero siempre los reportara como "por copiar" aunque no haya
cambiado nada — esta documentado en su cabecera para que nadie lo lea como un
error.

**Lo que NO se toco, y es una decision pendiente de Francisco:**

1. **Los cargos de las tres cofundadoras.** Delia Avilan, Gabriela Dominguez y
   Victoria Espinoza figuran en `club.json` como "Co-fundadora · FEN Investment
   Woman", con bios que cuentan que fundaron el area. Eso no es una seccion del
   sitio: es el merito publico de tres personas reales. Ocultar un area es una
   decision de publicacion; reescribirle el curriculum a alguien no. Por eso el
   nombre SIGUE visible en §Nosotros del espejo — es una limitacion deliberada,
   no un descuido.
2. **El evento "Encuentro FEN Investment Woman"** del 27-may-2026 en la
   bitacora. Es una actividad que ocurrio; borrarla es editar la historia del
   club. Hay un flag `QUITAR_EVENTO` en el script para cuando se decida.

### La primera sincronizacion de verdad del espejo

`sincronizar_espejo.py` existia desde la quinta tanda pero **nunca se habia
corrido con `--aplicar`**. El espejo estaba 137 archivos atras: sin los WebP
(produccion servia los JPG pesados), con los logos sin optimizar (`fig-oro.png`
a 38 KB en vez de 8), sin `torneo-portada.json`, y sin las tandas 6 a 9.

Dos cosas que hubo que arreglar para que la sincronizacion fuera revisable:

- **El espejo esta en CRLF y fig-web en LF.** Copiando a lo bruto, git mostraba
  cada archivo como si hubieran cambiado sus 3.000 lineas y el cambio real
  quedaba invisible. Ahora `copiar_conservando_fin_de_linea()` respeta el final
  que el archivo ya tenia alla, y `iguales()` compara ignorandolo — sin eso el
  script reportaria los mismos 30 archivos como pendientes para siempre. El
  diff real quedo en 1.584 inserciones y 166 borrados, legible.
- **`torneo/index.html` entro a `DIFIEREN`**: su nav enlaza a `../informe/`, que
  alla no existe. Copiarlo entero dejaba dos enlaces a un 404 en produccion.

**Bug que aparecio de paso:** el sitemap del espejo declaraba `/miembros/`, que
alla da 404 — le estaba pidiendo a Google una pagina inexistente desde que se
creo. Se arregla solo al generar el sitemap dentro del espejo, que enumera los
`.html` que de verdad existen. Quedo en 9 URLs.

**Y en `verificar_sitio.py`:** marcaba ERROR si una pagina de `CANONICAS` no
existia. Ahora que el mismo script corre en los dos repos y el espejo publica
menos paginas a proposito, eso es un AVISO. Una pagina que no se publica no
puede tener mal su canonical.

### Verificacion

`verificar_paginas.js` en los dos repos: todas las paginas cargan sin un solo
error de consola ni archivo faltante (16 en fig-web, 12 en el espejo). Los dos
`verificar_sitio.py` salen sin errores. Ademas, a mano en Chrome sobre el
espejo: `/fiw/` da 404, y el texto visible de las 6 paginas afectadas no nombra
el area en ninguna — solo quedan las menciones de las tres cofundadoras y el
evento de la bitacora, que son las dos exclusiones deliberadas de arriba.

**Nada esta commiteado ni pusheado en ninguno de los tres repos.**
