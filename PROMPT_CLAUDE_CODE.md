# Prompt de arranque — primera sesión de Claude Code en este proyecto

> Cómo usar esto: abre Claude Code **en esta carpeta** (la que contiene
> CLAUDE.md, index.html, eventos/, fiw/, torneo/, datos/, fotos/). Pega el
> bloque de abajo como tu primer mensaje. Claude Code ya lee CLAUDE.md
> automáticamente, así que este prompt es corto a propósito: le da la
> tarea concreta del día, no repite el contexto que ya tiene.

---

## Prompt para copiar y pegar

```
Lee CLAUDE.md completo antes de hacer nada. Es el proyecto web de FEN
Investment Group (FIG) — ya tiene 4 páginas construidas (index.html,
eventos/, fiw/, torneo/) que comparten diseño y se alimentan de JSON en
datos/. La tabla "Estado actual de cada pieza" de CLAUDE.md te dice qué
está en producción, qué está en modo demo, y qué falta.

Hazme un resumen breve (5-8 líneas) de tu entendimiento del proyecto y del
estado actual antes de tocar cualquier archivo, para que confirme que
quedó claro. Después de mi confirmación, quiero que trabajes en:

[DESCRIBE AQUÍ LA TAREA DE HOY — ver ejemplos abajo]

Reglas que ya están en CLAUDE.md pero recalco: nada de build steps (HTML/
CSS/JS planos), nunca escribas en Google Drive, y sigue el patrón
Excel/JSON → HTML que ya usa el resto del proyecto para cualquier dato
nuevo que agregues.
```

---

## Ejemplos de tarea para la sección `[DESCRIBE AQUÍ LA TAREA DE HOY]`

Usa uno de estos (o el tuyo propio) según lo que quieras avanzar. Estos son
los pendientes ya identificados en CLAUDE.md, en el orden en que probablemente
convenga hacerlos:

### 1. Conectar las páginas entre sí (la más rápida, hazla primero)
```
Conecta los enlaces cruzados: en index.html, la sección Eventos debe
enlazar a eventos/index.html (las tarjetas individuales pueden usar
eventos/index.html#<id-del-evento> para abrir directo ese evento), el
desk FIW dentro de Áreas debe enlazar a fiw/index.html, y la sección
Torneo debe enlazar a torneo/index.html. Revisa que los botones "Ver
ranking semanal" también apunten a torneo/index.html en vez de a la URL
externa del sitio antiguo, salvo que prefiera mantener ambas.
```

### 2. El eslabón que falta del pipeline del torneo
```
Escribe generar_torneo.py siguiendo el esquema documentado en
datos/torneo.json.ejemplo. Debe leer la hoja ranking_ordenado del Excel
oficial del torneo (Excel_Oficial_FIG_PORT_2026_.xlsx) y cruzarla con
Inscripciones_Torneo_Portafolio_2026.xlsx para sacar nombre + LinkedIn de
cada integrante por equipo. Sigue el mismo estilo de los scripts que ya
existen en el pipeline (ordenar_tmsg.py, reconstruir_nav.py,
build_outputs.py) para mantenerlo consistente. Al terminar, corre el
script contra los datos de ejemplo disponibles y muéstrame el
datos/torneo.json resultante antes de darlo por bueno.
```

### 3. Poblar fotos y resúmenes de eventos
```
Tengo fotos para el evento <nombre-del-evento> — te las voy a ir pasando.
Ayúdame a redimensionarlas a ~1600px de ancho, numerarlas 1.jpg, 2.jpg,
3.jpg... sin saltos, y dejarlas en fotos/eventos/<carpeta-correcta>/
(revisa el campo "carpeta" de ese evento en datos/eventos.json). También
quiero reemplazar el resumen "[Resumen por completar]" de ese evento por
un texto real que te voy a dictar.
```

### 4. Confirmar y aplicar los colores de FIW
```
Delia ya definió los colores oficiales de FEN Investment Woman: son
[pega los hex aquí]. Actualiza las 4 variables --acc*, --acc-light,
--acc-deep y --acc-warm al inicio del <style> de fiw/index.html, y
revisa visualmente (puedes abrir el archivo y describir qué contraste
tendría cada uso) que el texto siga siendo legible sobre esos colores en
todos los estados (hover, fondo claro, fondo oscuro).
```

### 5. Trabajar cualquier idea de los archivos de ideas
```
Abre IDEAS_GRAN_ESCALA_FIG.md y ayúdame a construir [nombre de la idea,
ej: "el explicador automático de movimientos del ranking"]. Antes de
escribir código, propónme cómo lo estructurarías (qué archivos crea, qué
lee, qué produce) y espera mi aprobación.
```

---

## Notas para sesiones futuras (no hace falta repetir esto cada vez)

- Claude Code relee CLAUDE.md automáticamente en cada sesión nueva dentro
  de esta carpeta — no hace falta volver a explicar el proyecto.
- Si el estado de algo cambia (ej: torneo.json ya existe con datos reales,
  o los colores de FIW ya están confirmados), pídele a Claude Code que
  actualice la tabla "Estado actual de cada pieza" en CLAUDE.md como parte
  de esa misma tarea, para que la próxima sesión arranque con información
  correcta.
- Si agregas una página o carpeta nueva al proyecto, pídele a Claude Code
  que también actualice la sección "Estructura del repo" de CLAUDE.md.
