# Ideas para el ecosistema web de FIG
*Lluvia de ideas — ninguna está implementada salvo que se indique. Ordenadas por área, con notas de esfuerzo (⚡ = una sesión, 🔨 = varias sesiones, 🏗️ = proyecto).*

## Torneo Portafolio
- ⚡ **Replay del ranking (bar chart race):** animación semana a semana de cómo se movieron los equipos, usando los históricos que ya guarda el pipeline. Botón "Ver la carrera hasta hoy".
- ⚡ **Badges por métrica:** distinciones automáticas en el ranking — "Mejor Sharpe", "Gestor de Riesgo" (menor MDD), "Cazador de Alfa" (mayor IR), "Remontada de la semana" (mayor delta). Sale gratis de los datos que ya existen.
- ⚡ **Comparador de equipos:** seleccionar 2 equipos y verlos lado a lado, métrica por métrica (útil para rivalidades y para la final).
- ⚡ **Modo TV/kiosko:** URL `?tv=1` que rota automáticamente podio → tabla → countdown en pantalla completa, para proyectar en el Bloomberg Lab los viernes de publicación.
- 🔨 **Tarjetas semanales automáticas:** el generador PNG de la página puede correr headless (Puppeteer) dentro del pipeline y producir las 63 tarjetas de una vez, listas para enviar a cada equipo por correo/WhatsApp.
- 🔨 **Certificado final descargable** para todos los participantes al cierre (mismo motor de tarjetas, plantilla distinta), y diploma especial para finalistas.
- 🔨 **Gráfico histórico multi-línea** en la página (evolución del top 5 por semana) — el esquema del JSON ya lo soporta agregando un arreglo `historico`.
- 🔨 **Predicciones internas ("quiniela"):** la comunidad vota quién será top 3 antes de cada corte; tabla de aciertos aparte. Engagement sin tocar el scoring real.
- 🏗️ **Notificaciones:** correo automático a cada equipo con su tarjeta + posición al publicar el ranking (Apps Script, ya usan uno para postulaciones).

## Sitio principal
- ⚡ **Conectar los enlaces cruzados:** tarjetas de Eventos → eventos/, desk FIW → fiw/, sección Torneo → torneo/ (2-3 líneas).
- ⚡ **Strip de sponsors** (BlackRock, Itaú — logos ya están en el Drive) bajo el hero o antes del footer.
- ⚡ **Open Graph images:** una imagen para compartir por página (el motor de tarjetas puede generarlas).
- 🔨 **Muro de la Fama con trofeos:** tarjetas 3D CSS que giran al hover mostrando el equipo campeón por edición; se alimenta del histórico de torneos.
- 🔨 **Testimonios de la comunidad** (carrusel con citas de miembros/egresados) y **contador en vivo** de la comunidad desde el Sheet de registro.
- 🔨 **Timeline de Historia con fotos reales:** el Historial Audiovisual de Primavera 2025 ya tiene material; conectar las fotos del Drive a los capítulos de la línea de tiempo.

## Eventos
- ⚡ **Botón "Agregar a calendario" (.ics)** por evento futuro.
- ⚡ **Lightbox** en las galerías (foto a pantalla completa con flechas).
- 🔨 **Inscripción integrada:** reutilizar el endpoint de Apps Script del formulario de postulación para inscribirse a charlas/talleres desde la propia página.
- 🔨 **Compresión automática de fotos:** GitHub Action que al subir fotos las redimensione a 1600px (evita que las fotos de cámara de 8MB hagan lenta la página).

## FEN Investment Woman
- ⚡ **Definir colores oficiales** con Delia y fijarlos en las 4 variables --acc*.
- 🔨 **Sección "Referentes":** entrevistas breves a mujeres de la industria (formato tarjeta + quote), alimentada por Excel como todo lo demás.
- 🔨 **Programa de mentoras:** matching sencillo mentora-estudiante vía formulario.

## Infraestructura / pipeline
- ⚡ **generar_torneo.py:** el eslabón que falta — lee ranking_ordenado + inscripciones (con LinkedIn) y escribe datos/torneo.json. Encaja en el prompt semanal de Claude Code existente.
- ⚡ **generar_eventos.py / generar_fiw.py:** Excel → JSON para las páginas nuevas, mismo patrón que Nosotros_FIG.xlsx.
- 🔨 **GitHub Action "Excel push → JSON":** al subir el Excel al repo, regenera los JSON automáticamente (ya existe el patrón para club.json).
- 🔨 **PWA ligera:** manifest + service worker para que el ranking se pueda "instalar" en el teléfono y cargar al instante.
- 🏗️ **API pública de solo lectura:** exponer datos/torneo.json documentado como API para que los propios equipos construyan cosas encima (muy alineado con el espíritu del club).

## Contenido / redes
- ⚡ **Hashtag y footer unificados** en todas las tarjetas descargables (#TorneoPortafolio2026 ya va incluido).
- 🔨 **Conectar el overlay OBS existente** (ranking-video del Drive) con datos/torneo.json en vez del CSV de Sheets — una sola fuente de verdad.
- 🔨 **Página de prensa/media kit:** logos, colores, descripciones cortas — todo ya está en el Drive, solo hay que exponerlo.
