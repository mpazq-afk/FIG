# Páginas nuevas — Eventos y FEN Investment Woman

Dos páginas que se conectan al sitio principal (index.html) y siguen su mismo
sistema de diseño. Igual que el sitio principal: sin build steps, GitHub Pages,
y todo el contenido editable por datos, no por código.

## Estructura (junto al index.html principal)

```
/
├── index.html               ← sitio principal (ya entregado)
├── eventos/index.html       ← NUEVA · bitácora de actividades
├── fiw/index.html           ← NUEVA · FEN Investment Woman
├── datos/
│   ├── club.json            (del sitio principal)
│   ├── eventos.json         ← NUEVA · lista de eventos
│   └── fiw.json             ← NUEVA · textos de FIW
└── fotos/
    ├── eventos/<carpeta>/   ← 1.jpg, 2.jpg, 3.jpg… por evento
    └── fiw/                 ← 1.jpg, 2.jpg, 3.jpg…
```

## Flujo de trabajo (el de siempre)

- **Agregar un evento** → una fila más en el Excel → regenerar `datos/eventos.json`
  (o editarlo a mano; el esquema está documentado dentro del propio JSON).
- **Participantes** → llenar la lista `participantes` del evento; aparecen como chips.
- **Resumen** → campo `resumen`; mientras diga "[Resumen por completar]" la página
  lo muestra igual, sin romperse.
- **Fotos** → subir a `fotos/eventos/<carpeta>/` como `1.jpg, 2.jpg, 3.jpg…`
  Se vuelven: portada de la tarjeta + fondo en slideshow del detalle + galería.
  Instrucciones completas en `fotos/LEEME.txt`.
- **FIW** → textos en `datos/fiw.json`; fotos en `fotos/fiw/` (fondo del hero +
  galería). **Colores oficiales de FIW**: editar las 4 variables `--acc*` al
  inicio del `<style>` de `fiw/index.html` — toda la página se re-tiñe sola.

Ambas páginas traen los datos embebidos como respaldo: funcionan al abrirlas
con doble clic, y al desplegarse leen los JSON automáticamente.

## Conectar con el sitio principal (2 ediciones de una línea)

En `index.html` (sitio principal):
1. En la sección Eventos, apuntar los enlaces de las tarjetas a `eventos/index.html`
   (o `eventos/index.html#torneo-portafolio-2026` para abrir un evento directo).
2. En el desk FIW de Áreas, apuntar "Conocer el área" a `fiw/index.html`.

Los enlaces de retorno ya están puestos en ambas páginas nuevas.

## Detalles de la experiencia

- **Eventos**: filtros por categoría (Torneos/Visitas/Charlas/Comunidad), tarjetas
  con la foto 1 de fondo y año fantasma, y al abrir un evento: panel de vidrio con
  las fotos del evento en slideshow Ken Burns de fondo, participantes en chips y
  galería. Cada evento tiene URL propia (#id) para compartir.
- **FIW**: hero con las fotos de la comunidad en slideshow, marquee editorial,
  pilares con brillo que sigue al cursor, galería tipo mosaico y CTA en oro rosa.
- Ambas: cursor crosshair, kickers con efecto decode, reveals, responsive completo,
  reduced-motion respetado y datos seed reales (los 9 eventos del mapeo del Drive).

---

## Torneo (agregada después)

- `torneo/index.html` — ranking oficial: podio, tabla con búsqueda, detalle por
  equipo (métricas PORT + desglose de puntos + miembros con LinkedIn) y
  descarga de tarjetas: **PNG 1080×1350** (Instagram/LinkedIn) y **HTML
  autocontenido**, generadas en el navegador del usuario, sin servidor.
- Arranca en **modo DEMO** (los 8 equipos ficticios del ejemplo de las Bases,
  con banner visible). Al publicar `datos/torneo.json` desde el pipeline
  semanal, el banner desaparece y muestra los datos reales.
- El esquema exacto está en `datos/torneo.json.ejemplo` (renombrar a
  `torneo.json` cuando tenga datos reales). El eslabón nuevo del pipeline:
  `generar_torneo.py` lee `ranking_ordenado` + el Excel de inscripciones
  (columna LinkedIn) y escribe ese JSON.
- Semana actual y countdown al próximo hito se calculan solos con las fechas
  oficiales del torneo.
