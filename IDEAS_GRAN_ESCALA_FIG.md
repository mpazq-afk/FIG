# Ideas de gran escala — ecosistema FIG
*Para un modelo con capacidad de ejecutar código, orquestar pipelines y tocar muchos archivos a la vez (tipo Fable 5 / Claude Code). No son retoques de una sesión: son proyectos con varias piezas moviéndose juntas — generación masiva, agentes, automatización end-to-end. Nada de esto está implementado. Ordenadas por área, con una nota de qué las hace "de gran escala" y qué necesitarían para arrancar.*

---

## 1. Motor de contenido generativo (la idea más grande)

**El problema de fondo:** cada pieza de contenido de FIG (tarjeta de equipo, resumen de evento, post de Instagram, certificado) hoy se genera una por una, a mano o con un botón que aprieta una persona. Con 63 equipos, 25 semanas y decenas de eventos, eso escala mal.

- 🏗️ **Fábrica de tarjetas semanales:** un agente que cada viernes (1) lee `ranking_ordenado`, (2) genera las 63 tarjetas PNG + HTML de una sola corrida (headless, reusando el motor canvas que ya existe en `torneo/index.html`), (3) las sube a una carpeta `tarjetas/semana-N/` en Drive, (4) redacta y envía el correo/WhatsApp a cada equipo con su tarjeta adjunta. Cero intervención humana el día viernes.
- 🏗️ **Generador de resúmenes de evento con IA a partir de las fotos crudas:** para los eventos que hoy dicen "[Resumen por completar]", un agente que mire el lote de fotos de la carpeta (`fotos/eventos/<evento>/`), infiera contexto (cuántas personas, tipo de espacio, capturas de pantalla vs fotos de grupo), cruce con la fecha/carpeta contenedora, y proponga un primer borrador de resumen para que un humano solo corrija en vez de escribir desde cero.
- 🔨 **Kit de prensa autogenerado:** a partir de `club.json` + `torneo.json` + logos del Drive, ensamblar automáticamente un PDF/HTML de media kit (misión, cifras, logos en distintos fondos, contactos) cada vez que cambien los datos base — sin que nadie tenga que armarlo manualmente en Canva.
- 🔨 **Traductor de "Excel crudo" a "JSON de producción" universal:** hoy cada página tiene su propio `generar_X.py`. Un agente que, dado *cualquier* Excel nuevo con una pestaña de datos razonablemente tabular, proponga automáticamente el mapeo de columnas → esquema JSON existente, en vez de escribir un script nuevo cada vez.

## 2. Certificación y credenciales verificables

- 🏗️ **Sistema de certificados con verificación pública:** al cierre del torneo, generar automáticamente un certificado por participante (PDF + versión web) con un código único, y una página `/verificar/<código>` donde cualquiera (un reclutador, por ejemplo) pueda confirmar que esa persona participó y en qué posición quedó su equipo. Esto vuelve el torneo un credential real, no solo una foto de pantalla.
- 🔨 **Insignias tipo LinkedIn "Add to profile":** generar el botón oficial de LinkedIn ("Agregar a perfil") para cada certificado, con el nombre del logro pre-rellenado ("Finalista — Torneo Portafolio 2026, FEN Investment Group"). Aumenta la visibilidad de FIG cada vez que alguien lo agrega a su perfil.
- 🔨 **Timeline profesional de cada alumno dentro de FIG:** agregando participación en torneos + charlas + rol en la directiva a lo largo de los semestres, un mini "CV interno" descargable — útil para quien postula a un cargo dentro del club o para referencias.

## 3. Inteligencia sobre el propio torneo (analítica)

- 🏗️ **Panel de analítica para la dirección del torneo** (no público): dashboard que cruza semana a semana la volatilidad de las decisiones de los equipos, detecta patrones raros (rebalanceos justo antes del cierre de ventana, posiciones concentradas cerca del 20% límite) y genera alertas automáticas de posible incumplimiento de las Bases — hoy eso se revisa a mano.
- 🔨 **Explicador automático de movimientos del ranking:** cada viernes, un texto generado ("Compass Advisors sube al 1° lugar impulsado por su Information Ratio, mientras Granite Partners cae tras activar la regla de piso en Sharpe") a partir de comparar el JSON de esta semana con el anterior. Esto es contenido gratis para redes sociales y para que los propios equipos entiendan su cambio de posición sin leer números crudos.
- 🔨 **Simulador "qué pasaría si":** una herramienta donde un equipo pueda simular cómo cambiaría su score si moviera su asignación de activos, usando la misma fórmula de percentil continuo — útil como herramienta educativa antes de una ventana de rebalanceo real.

## 4. Automatización de la operación del club (no solo la web)

- 🏗️ **Agente de triage del Drive:** dado que ya existe un mapeo completo de la carpeta, un agente que corra periódicamente, detecte archivos nuevos sin clasificar (fotos sueltas, PDFs nuevos), proponga a qué carpeta/evento pertenecen por fecha y contenido, y arme un borrador de "qué subir a las páginas web" sin tocar nada del Drive directamente (solo lectura + propuesta).
- 🔨 **Onboarding automático de nuevos miembros:** desde que alguien llena el formulario de postulación (Apps Script), disparar automáticamente: creación de su fila en el Sheet de miembros, correo de bienvenida personalizado, y — si aplica — su tarjeta de "nuevo integrante" para redes.
- 🔨 **Calendario maestro generado, no mantenido a mano:** unificar automáticamente fechas de torneo (ventanas de rebalanceo, cortes semanales), eventos (`datos/eventos.json`) y actividades históricas en un solo `.ics` público que la comunidad pueda suscribirse, regenerado cada vez que cualquiera de esas fuentes cambie.

## 5. Multi-torneo / escalar más allá de Portafolio 2026

- 🏗️ **Generalizar el motor de ranking a cualquier torneo futuro:** el sistema de podio/tabla/tarjetas de `torneo/index.html` está hecho pensando solo en Portafolio 2026. Un agente podría abstraerlo en una plantilla reutilizable (`torneo-base/`) que reciba un esquema de scoring distinto (por ejemplo, si Trading o Valuation lanzan su propio torneo) sin reescribir la página desde cero cada vez.
- 🔨 **Archivo histórico navegable de todas las ediciones:** una vez que exista más de un torneo con datos reales, una página `/torneos/` que liste todas las ediciones (2025, 2026, 2027…) con su propio podio congelado — construido automáticamente al archivar cada `torneo.json` al cierre de cada edición.

## 6. Voz y multimedia (más allá de texto/imagen)

- 🏗️ **Video-resumen semanal automático:** a partir del `torneo.json` de la semana, generar un guion corto + storyboard (texto) para el video de ranking que hoy se arma a mano con GSAP/Chart.js (`ranking-video` del Drive) — cerrando el círculo entre los datos y el overlay que ya existe, sin que alguien tenga que actualizar `data.js` manualmente cada semana.
- 🔨 **Locución generada para el overlay de OBS:** un guion de 30 segundos narrando el top 5 de la semana, listo para grabar o para texto-a-voz, coherente con el tono de marca de FIG.

## 7. Gobernanza de datos y confianza

- 🏗️ **Auditoría automática de integridad del scoring:** un script que, cada semana, recalcule el score de los 63 equipos desde cero (percentil continuo + reglas de piso) de forma independiente al pipeline de producción, y alerte si hay una discrepancia — una segunda fuente de verdad que protege contra errores silenciosos antes de publicar el ranking oficial.
- 🔨 **Registro de cambios (changelog) de las Bases:** ya existen al menos dos versiones del PDF de bases en el Drive (borrador y final). Un agente que compare versiones futuras y genere automáticamente un resumen de "qué cambió" para que los equipos no tengan que releer el documento completo cada vez.

---

## Qué necesitaría cada bloque para arrancar (resumen práctico)

| Bloque | Requiere | Complejidad |
|---|---|---|
| Fábrica de tarjetas semanales | Acceso de escritura a Drive/correo, headless canvas | 🏗️ Alta |
| Certificados verificables | Página nueva + generación de códigos + PDF | 🏗️ Alta |
| Explicador automático del ranking | Solo el histórico de `torneo.json` (ya existe el esquema) | 🔨 Media |
| Auditoría de integridad del scoring | Reimplementar la fórmula de las Bases en un script aparte | 🔨 Media |
| Generalizar el motor a multi-torneo | Refactor de `torneo/index.html` a plantilla | 🏗️ Alta |
| Agente de triage del Drive | Solo lectura (ya compatible con la política actual) | 🔨 Media |

*Nota: todo lo anterior respeta la misma filosofía del resto del ecosistema — Excel/Drive como fuente de verdad, JSON como capa intermedia, páginas que solo leen. Nada de esto requiere que una persona escriba código para operarlo día a día; el trabajo de "escribirlo" es justamente lo que un modelo como Fable 5 puede organizar y construir de punta a punta.*
