# Bitacora de cambios del sitio FIG

> Extraido de `CLAUDE.md` el 2026-09-02 para que no se cargue en cada sesion.
> Este es el repo ESPEJO: la fuente de verdad de casi todo esto es `fig-web`.
> Son las "tandas" fechadas de trabajo, del 2026-08-23 en adelante, tal
> cual estaban. Nada se perdio (cobertura verificada 2063/2063).
>
> **No se carga en cada sesion.** Leelo cuando necesites saber POR QUE algo
> quedo como quedo. Las lecciones vigentes estan destiladas en la seccion
> "Trampas conocidas" del `CLAUDE.md` de `fig-web`.

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

## Continuacion del 2026-08-30: ingles completo, informe publicado y movil

Sigue a la "Decima tanda". Todo pusheado a los dos repos y verificado en vivo.

### El lema: "Élite" -> "Líderes"

"Forjando la **Élite** del Mañana" paso a "Forjando los **Líderes** del
Mañana", pedido de Francisco: 14 lugares entre `<title>`, og/twitter
description, el `<h1>` animado del hero, el mono-tag, el brand-sub del pie y la
tarjeta descargable de `miembros/`. Ojo que el articulo tambien cambia (*la*
Élite -> *los* Líderes) y en el `<h1>` esas dos palabras viven en `<span>`
distintos porque el titulo se anima linea por linea.

**Trampa que costo una afirmacion equivocada:** `grep -i` en este shell **no
hace case-folding de caracteres no ASCII**, asi que buscar `elite\|élite` NO
encuentra "Élite" con mayuscula acentuada. Se dio por hecho que solo estaba en
la pagina en ingles. **Para buscar texto con acentos en este repo, usar Python
en UTF-8, no `grep -i`.**

### `en/index.html`: de one-pager a sitio

Francisco lo reviso dos veces; la segunda dijo, con razon, que era un resumen
de la portada. Ahora tiene nueve secciones y **tres se alimentan de los mismos
JSON que el sitio en espanol**, asi que no se desfasan: el ranking en vivo del
torneo (`torneo-portada.json`), la directiva completa (`club.json`) y la
bitacora de actividades (`eventos.json`).

Lo unico a mantener a mano es la traduccion, en el archivo nuevo
**`datos/en.json`**. **Un evento sin traduccion NO se muestra**, en vez de
aparecer en espanol en medio de una pagina en ingles; al crear un evento hay
que agregarle su linea ahi.

Detalle que costaria un bug: los nodos pintados DESPUES de que corrio el
IntersectionObserver no se revelan solos, por eso `ver()` les pone la clase
`in` a mano.

### `informe/` publicado en el espejo, y su version en ingles

Francisco pidio llevarlo a produccion con version en ingles. **No se
duplico el archivo**: son ~1.200 lineas con ocho graficos SVG a mano, y dos
copias es la trampa que este repo ya conoce. `generar_informe_en.py` toma el
informe en espanol, le aplica una tabla de traduccion y escribe
`en/informe/index.html`. **Correrlo cada vez que se toque `informe/index.html`.**

**El script falla si queda texto en espanol.** Tres agujeros que esa barrera
tuvo y que conviene no reabrir:

1. **Plurales.** Buscaba `\bcorte\b` y `\bsemana\b`, y dejo pasar "Cortes
   publicados" y "semanas 5 a 15" hasta el archivo generado. Toda palabra que
   se agregue va con su plural.
2. **La exencion saltaba el texto ENTERO** si contenia una marca exenta: un
   parrafo completo paso limpio por terminar en "FEN Investment Group". Ahora
   se quita la marca y se revisa lo que queda.
3. **El CSS tambien escribe texto** con `content:`, y no se revisaba.

Ademas hay un chequeo que compara los `id=` de las dos versiones y aborta si
difieren: traducir "Mercado" habia convertido `id="cMercado"` en `id="cMarket"`.
Funciono de casualidad porque el selector del JS cambio igual, pero el mismo
accidente sobre una clave de datos rompe la pagina en silencio. Por eso las
traducciones cortas llevan su contexto (`>Mercado</a>`).

Y si el ancla donde se inyecta `corteEN()` deja de calzar, el script aborta:
sin esa comprobacion la funcion quedaba sin definir, el `<script>` entero moria
con un ReferenceError y **los ocho graficos salian vacios sin decir por que**.

Del campo `corte` solo se traduce el MES ("21 · AGO · 2026" -> "21 · Aug ·
2026"). Las dos versiones se enlazan con un conmutador de idioma en el nav.

### `sincronizar_espejo.py` y `despublicar_fiw.py` son un PAR

Se corren en ese orden, y despues `generar_sitemap.py` DENTRO del espejo. Como
el segundo reescribe 5 archivos, el primero **siempre** los reportara como "por
copiar" aunque no haya cambiado nada: no es un error.

### Telefono: `verificar_movil.js` (nuevo)

`verificar_paginas.js` mide en 1400px y no veia lo que falla en un telefono.
Este mide a 390x844 con emulacion movil real y reporta desborde horizontal del
documento (con los elementos culpables), objetivos tactiles bajo 24px y texto
bajo 11px. Recorre la pagina antes de medir, porque los `.reveal` y los
graficos solo se dibujan al entrar en pantalla.

**Resultado: ninguna pagina se sale del ancho.** Los ocho graficos y la tabla
estan en contenedores con `overflow-x:auto` (caja 300px, contenido 760px) y se
arrastran; se les agrego una **sombra de scroll** en CSS puro y sin texto (un
rotulo habria que traducirlo) para que se note que hay mas contenido.

**Objetivos tactiles: 0 bajo 24px en todo el sitio.** Se subieron `.a-link`,
`.p-linkedin`, `.p-link`, `.cre-in`, los `footer a` y los `.nav a.back`, con el
patron de siempre (padding + margen negativo que lo compensa).

**Dos hallazgos que valen la pena:**
- La regla `.f-bottom a{padding:6px 0;margin:-6px 0}` de la sexta tanda estaba
  escrita **DENTRO** del bloque `.f-bottom{` — CSS invalido. El navegador la
  descartaba, y por eso el credito del pie seguia en 13px pese a figurar como
  arreglado. Estaba igual en `index.html` y `miembros/index.html`.
- **El deslizador del replay del torneo tenia 4px de alto tocable.** La pista
  se ve fina a proposito, pero eso era todo lo agarrable. El input pasa a 24px
  transparente y los 4px se dibujan en `::-webkit-slider-runnable-track` /
  `::-moz-range-track`. El `margin-top:-6px` del pulgar es (4-16)/2: si se
  cambian los altos hay que recalcularlo.

**Falso positivo documentado:** los nombres de equipo del ranking miden 23px,
pero el objetivo real es la fila entera (`.lb-row`, ~55px). El script los exime.

**Trampa de medicion:** `chrome --screenshot --window-size=390,...` SIN
emulacion movil da una imagen enganosa — mostraba texto cortado en una pagina
sin ningun desborde. Para mirar el sitio en telefono, capturar por CDP con
`mobile:true`.

### Notas internas que se le mostraban al visitante (corregido)

En `eventos/index.html`, al abrir un evento se veian cuatro: la instruccion
"Sube imagenes a `fotos/eventos/<carpeta>/` nombradas 1.jpg…", el conteo con la
ruta interna del repo, el chip "Por confirmar" de participantes (en los 10
eventos, porque ninguno tiene lista) y lo mismo en modo proyeccion. Si el dato
no esta, no se anuncia.

### La rutina semanal, actualizada

```
python generar_torneo.py --excel <Excel del corte> --semana N --corte "..."
python generar_tabla.py
node generar_og_equipos.js            # OPCIONAL
python generar_paginas_equipo.py
python generar_informe_en.py --aplicar   # si se toco informe/index.html
python generar_sitemap.py
python verificar_sitio.py
python -m http.server 8000            # en otra terminal
node verificar_paginas.js
node verificar_movil.js               # telefono
node verificar_menu_movil.js          # SOLO si se toco el menu movil
python sincronizar_espejo.py --aplicar
python despublicar_fiw.py --aplicar   # SIEMPRE despues del anterior
cd ../mpazq-afk.github.io && python generar_sitemap.py
```


## Tanda del 2026-08-31: cinco desks, paginas de Portafolio y Trading

Francisco confirmo la estructura de areas que quedaba abierta desde el 26-ago
y pidio las dos paginas de area que faltaban. Todo se publico en
`panchoscky/fig-web` unicamente: **el espejo de Manuel NO se toco**.

### Quien dirige cada area (confirmado, no supuesto)

| Desk | Dirige | Pagina |
|---|---|---|
| PRT · Portafolio | Francisco Valenzuela | `portafolio/index.html` |
| TRD · Trading | **Manuel Paz** | `trading/index.html` |
| VAL · Valuation | **Jhosep Garcia** | `valuation/index.html` |
| FIW · FEN Investment Woman | Delia Avilan | `fiw/index.html` |
| ADM · Administracion | **nadie, a proposito** | — |

Dos cambian lo que decia el repo, asi que **no "corregirlos" hacia atras**:

- **Valuation cambio de lider.** El 27-ago se habia confirmado a Samuel
  Rodriguez Arnolds; el 31-ago Francisco dijo que es Jhosep Garcia. Samuel
  bajo a `Directivo · Valuation` y perdio el chip.
- **Trading por fin tiene lider**: Manuel Paz, que conserva el rol
  `Director · Portafolio y Trading` que el mismo publico en el espejo.
  Rafael Aliendre y Juan Pablo Diaz Cerda bajaron a `Directivo · Trading`,
  el mismo patron que se habia aplicado en Portafolio.
- **Juan Jose Limari ya no pertenece a Trading**: queda `Fundador` sin desk.
- **Administracion (ADM) es area nueva.** Francisco puso a Benjamin Saez como
  responsable "por el momento" pero eligio explicitamente que **nadie lleve el
  chip "Dirige el area"** ahi. Benja sigue mostrandose solo como Presidente.

### El orden de los desks vive en CINCO lugares

Al agregar o mover un area hay que tocar los cinco o el sitio se desalinea:

1. `datos/club.json` — `liderArea` de cada persona (fuente de verdad).
2. `AREAS` de `generar_miembros.py` — con `pagina` si el area tiene una.
3. `config.areas` de `datos/miembros.json` — se copia del anterior.
4. §Areas de `index.html` — la lista de tabs Y su `.dp-view`, en el MISMO
   orden: el conmutador trabaja por indice, no por codigo.
5. `AC={...}` de `miembros/index.html` — el color del desk, dos veces.

`index.html` trae ademas una copia embebida de `personas` como respaldo por si
`datos/club.json` no carga; estaba desactualizada y se puso al dia.

### Las paginas de area son UNA plantilla, no tres

`portafolio/` y `trading/` se sacaron de `valuation/index.html` conservando el
`<style>` y el `<script>` completos y todos los `id` (`heroBajada`,
`valResumen`, `valPilares`, `valResponsables`, `tv*`, `valEventosGrid`). Solo
cambian textos, metadatos, el `DATA` embebido, el JSON que cargan y el filtro
de eventos. **Al cambiar una, mirar siempre si aplica a las otras dos.**

Dos diferencias deliberadas entre ellas:

- **Portafolio** no pide inscripciones con un Forms: el Torneo Portafolio 2026
  ya esta en curso, asi que el CTA de esa seccion lleva al ranking en vivo y a
  las bases. El mecanismo de `formUrl` sigue intacto por si algun dia se usa.
- **Trading** no tiene torneo propio: su seccion va `hidden` con
  `torneo.activo:false` y **por eso tampoco hay item "Torneo" en su nav**. Al
  encenderla hay que devolverlo; el `_como_editar` del JSON lo recuerda.

### El filete dorado, ahora tambien en las paginas de area

Quien dirige el area lleva filete dorado al costado + chip "Dirige el area",
igual que en §Nosotros de `index.html`. Se PORTO, no se reinvento, pero con un
detalle: en el raiz la tarjeta es clara y el oro es `--gold`; en las paginas de
area la seccion es oscura y el oro es `--acc`. El borde usa `--acc-dim`, que ya
existia y es el mismo alfa .34 del original con el oro claro. El `:hover` se
redefine en ambos lados porque la regla base de `.p-card` reemplaza el
`box-shadow` completo y se comeria el filete.

Quien lo lleva se marca con `lidera:true` en el `responsables` del JSON del
area — uno solo por pagina.

### La Mesa: un bug que introdujo este mismo cambio

Al sacar a Limari de Trading quedo **nivel 1 y sin area**, y a la mesa se
sienta solo quien es *nivel 1 CON area* (los arcos) o *nivel 0* (la cabecera):
no calzaba en ninguno de los dos y **desaparecia del dibujo**. Paso a nivel 0,
igual que David Gonzalez Canon, el otro fundador sin desk. El script de parche
dejo una comprobacion: los 15 de la directiva tienen que aparecer, hoy 12 en
los arcos y 3 en la cabecera.

ADM no necesito nada: `codigos()` solo dibuja arco para desks con gente
sentada, y ADM todavia no tiene segunda linea, asi que no sale como arco vacio
y Benja sigue en el centro. El arco aparece solo cuando entre alguien.

Ademas, `config.areas` traia `pagina` desde siempre y la mesa **nunca la
usaba**: se entraba a un desk y no habia salida hacia su pagina. Ahora la
cabecera del desk ofrece "Conocer el area" cuando esa area tiene una.

### `datos/miembros.json` se parcheo A MANO, contra su propia nota

145 de sus 160 fichas vienen del Excel de miembros del Drive, que no esta en el
repo: regenerar sin `--excel` las borraria. **Cuando el Excel este a mano,
correr `generar_miembros.py --excel <ruta>`** y el parche queda de sobra. Los
`AREAS` y `CARGOS_DEMO` del generador ya quedaron alineados con esto, asi que
una regeneracion futura no revierte nada.

### El nav, y un menu movil que ya estaba roto

Francisco pidio Portafolio y Trading en el nav principal. En escritorio NO
hicieron falta items nuevos: ya existia el desplegable **"Areas"**, que traia
un solo enlace (Valuation) porque era la unica area con pagina. Ahora trae
las tres, en el orden canonico. FIG Woman sigue en "Comunidad" a proposito.

En movil el menu es una lista plana, y ahi aparecio lo importante:
`.m-menu` era un flex `justify-content:center` **sin scroll**. Cuando la lista
pasa del alto de la pantalla, un flex centrado empuja los PRIMEROS items a
offset negativo: quedan fuera del viewport y **no hay barra que arrastrar**.

Medido sobre lo que ya estaba publicado, con 11 enlaces:

| Telefono | Contenido | Resultado |
|---|---|---|
| 390x844 | 844px | entraba justo |
| 375x667 | 740px | **"Nosotros" y "Torneo 2026" inalcanzables** |
| 360x640 | 727px | **igual** |

O sea **no lo rompio este cambio, ya estaba roto**; sumar dos enlaces solo lo
habria empeorado. Arreglado con `flex-start` + `overflow-y:auto` + margenes
automaticos en el primer y ultimo hijo: centra mientras sobre espacio y
scrollea entero cuando no. Con 13 enlaces (999px) las tres pantallas pasan.

**`verificar_menu_movil.js` (nuevo)**: ningun verificador abria el menu, por
eso el bug vivio tanto. Abre `#mmenu` en los tres telefonos y avisa que enlace
queda inalcanzable. **Correrlo cada vez que se agregue o saque un enlace del
menu movil**; ya esta en la rutina semanal, justo despues de
`verificar_movil.js`.

### Lo que se miro y NO se toco

- El **Capitulo II de la historia** sigue diciendo "15 directores, 4 desks" y
  "cuatro subareas". Es narrativa fundacional y ADM nacio despues, asi que
  puede ser correcto tal cual; es decision de Francisco.
- **`en/index.html`** sigue con "Four areas". Cambiarlo obliga a tocar
  `despublicar_fiw.py`, que busca ESE texto exacto para sacar FIW del espejo.
- El chip `.p-tag` mide 8px (`font-size:.5rem`), bajo el umbral de 11px de
  `verificar_movil.js`. Es el mismo tamano que ya tenia en el raiz; subirlo
  obliga a subirlo en los dos lados para que no se desalineen.

### Verificacion

`verificar_paginas.js`: las 19 paginas cargan sin errores de consola ni
archivos faltantes. `verificar_movil.js`: ninguna se sale del ancho a 390px.
`verificar_sitio.py`: sin errores (los 3 avisos de numero de equipos son los
historicos de siempre). `sitemap.xml` regenerado, 14 URLs.

**Ojo con una falsa alarma**: medir `miembros/index.html` sola da 418 KB
criticos y en el barrido completo da 217 KB. No es una regresion — es
`datos/torneo.json` (209 KB), que en el barrido ya viene cacheado desde la
portada. Al medir una pagina suelta con `--solo=`, paga todo lo que comparte
con las demas.


## Tanda del 2026-09-01: Administracion se vuelve un desk de verdad

Francisco: *"en la pagina de miembros, en la mesa, aun no veo el area de
administracion, en ella pon a benjamin saes, davis y limari"*.

### Por que no se veia

No era un bug. La Mesa solo dibuja el arco de un desk si hay alguien
**sentado**, y `sentados()` pide `area===codigo && (nivel===1 || lidera)`.
Benjamin Saez era nivel 0 sin `lidera`, asi que caia en la **cabecera** (el
centro) y no en un arco; David y Limari no tenian area. ADM existia en los
datos pero no tenia a nadie que dibujar.

El detalle bonito: **esos tres eran exactamente los del centro**, bajo el
rotulo "PRESIDENCIA". Al pasarlos al desk la cabecera quedo vacia y el centro
paso a mostrar el sello FIG. Eso **ya estaba contemplado** en el codigo
(`cab.length ? "PRESIDENCIA" : "FEN INVESTMENT GROUP"`), no hubo que tocarlo.
Ahora los 15 de la directiva se sientan en un desk y ninguno flota al centro.

### Cambio de decision: ADM si tiene lider

El 31-ago Francisco habia elegido que Administracion fuera **sin** chip de
lider. El 01-sep lo cambio: **Benjamin Saez la dirige**, con chip, y sigue
siendo Presidente. David Gonzalez y Juan Jose Limari entran como
`Directivo · Administracion`, conservando su condicion de cofundadores en el
detalle y en los hitos (mismo patron que Rafael Aliendre en Trading).

### Dos trampas que aparecieron

**1. El area se deduce del TEXTO, no de un campo.** `generar_miembros.py` usa
`area_de_texto(rol, detalle)` — lee **solo `rol` y `detalle`, nunca la bio** —
y ademas descarta `liderArea` si no calza con el area deducida. El rol de
Benjamin es "Presidente" a secas, asi que sin escribir "Administracion" en su
**detalle** su `liderArea:"ADM"` se habria caido en la proxima regeneracion.
El parche dejo una comprobacion que replica `area_de_texto` y falla si los
tres no dan ADM.

**2. Presidir Y dirigir un area a la vez no existia.** `.p-card--lead` (filete
arriba, presidencia) y `.p-card--area` (filete al costado, dirige un desk)
escriben **las dos el `box-shadow` completo**, asi que ganaba la ultima
declarada y el presidente perdia su filete de arriba. Se agrego la regla
combinada `.p-card--lead.p-card--area` con los dos filetes, mas su `:hover`.

### Verificacion

Medido en el DOM ya pintado de `miembros/index.html`: cinco arcos
(PRT, TRD, VAL, FIW, **ADM · ADMINISTRACION**), **15 asientos**, centro en
"FEN INVESTMENT GROUP / FIG". `verificar_paginas.js`, `verificar_movil.js` y
`verificar_sitio.py` sin errores.


## Tanda del 2026-09-01 (2): Portafolio deja de ser un clon de la plantilla

Francisco: *"me gustaria algo mas de inovasion con la pagina de portafolio,
quiero que se sienta como una pagina de FIG, pero que tambien tenga sierta
personalidad propia"*. Eligio hacer **las dos cosas**: datos vivos Y
tratamiento visual propio.

El problema de fondo era real: `portafolio/`, `trading/` y `valuation/` eran
la misma pagina con otros textos.

### Donde se rompe la simetria (y donde NO)

Lo unico que se rompe a proposito es el **hero**. Valuation y Trading llevan
detras del titulo una tira de fotos (`.photo-marquee`, sondeando
`fotos/<area>/`). En Portafolio esa tira y los anillos salieron, y el fondo
pasa a ser un **campo de las 54 trayectorias reales** del torneo, una
polilinea por equipo, sin ejes ni rotulos: ahi son textura, no lectura.
El argumento: este desk se presenta con los datos que produce.

**`fotos/portafolio/` ya no se lee.** El mecanismo se retiro con la tira; esta
anotado en el `_como_editar` para que nadie llene una carpeta muerta.

Lo que NO cambia: navy + oro, tipografias autoalojadas, nav, pie con el
credito, preloader y beacon. Se sumo un acento secundario `--bmk` (#7BA7DE)
que **ya es el token con que el sitio dibuja el ACWI** en `index.html`, las
pantallas e `informe/`. Vale doble aca: oro = torneo, azul = benchmark.

### Los datos vivos, en dos tiempos

Mismo enfoque que `torneo/index.html`, y por el mismo motivo (`torneo.json`
pesa 205 KB y el 75% es historial):

1. `datos/torneo-tabla.json` (~7 KB) -> cinta del hero, cifras del corte y las
   5 metricas, de inmediato. Si no existe, cae al completo.
2. `datos/torneo.json` en tiempo ocioso -> historial -> campo del hero y
   grafico. Con `saveData` o en 2G no se pide.

**§El corte** trae un grafico que no existe en ninguna otra pagina: **mediana
de los 54 equipos + banda intercuartil contra el ACWI**, semana a semana. Se
eligio mediana+IQR y no un promedio porque las 54 trayectorias crudas van de
-11,3% a +22,1% y aplastaban las dos lineas que importan.

**§Como se evalua** explica las 5 metricas, que es lo que de verdad distingue
al desk: aca una cartera no se juzga por rentabilidad sola. **El peso de cada
metrica no esta escrito en ninguna parte**: se deriva del `max(puntosDetalle)`
sobre los 54 equipos, porque por percentil continuo el mejor de cada metrica
se lleva el peso completo. Da 30/25/15/15/15. Si cambia la formula, la pagina
se entera sola.

De paso murio otra cifra a mano: "Equipos en competencia" ahora lleva
`vLive:"equipos"` y sale del corte vigente.

### Verificado a mano, no solo por el informe del agente

Contrastado contra `datos/torneo.json` con Python: 54 equipos, semana 15,
corte 21-AGO-2026, puntero *Beta capital* 93,26, ultimo 1,58, rango 91,68, y
los pesos 30/25/15/15/15 salen efectivamente de los maximos por metrica.

**Degradacion probada bloqueando los JSON en el navegador**, tres escenarios
-- sin ningun dato del torneo, sin el historial, y completo. En los tres:
cero "NaN", cero desborde horizontal, los 6 responsables pintados con UN solo
filete, cero excepciones JS. Lo unico que cambia es cuanto texto queda en pie
(6508 / 7454 / 8103 caracteres): las piezas sin dato simplemente no se
muestran.

`verificar_paginas.js` (las 19 paginas), `verificar_movil.js`,
`verificar_menu_movil.js` y `verificar_sitio.py`: sin errores. Grep de
recursos externos en la pagina: ninguno.

### Detalle que se repitio

El menu movil de Portafolio paso de 5 a 7 enlaces, asi que hubo que portarle
el mismo arreglo de scroll que se le hizo a `index.html` el 31-ago
(`flex-start` + `overflow-y:auto` + margenes automaticos). **Es el segundo
menu que se topa con esto**: al agregar enlaces a CUALQUIER `.m-menu`, correr
`verificar_menu_movil.js --pag=<la pagina>`.


## Tanda del 2026-09-01 (3): Portafolio, segunda vuelta -- el dato deja de ser fondo

Francisco, sobre la version anterior: *"la idea de usar los datos en vivo de
fondo era buena, pero mal implementada, solo son lineas finas y no se
entiende... crea algo nuevo e inovador... se atrevido, ariesgate con ideas
nuevas y estilos disrubtivos"*.

Tenia razon y el diagnostico es exacto: el hero dibujaba las 54 trayectorias
crudas del torneo como polilineas de 1px al 26% de opacidad DETRAS del titulo.
Como textura no se leia, y como grafico tampoco: sin ejes, sin rotulos y con 54
series superpuestas no hay nada que entender ahi. La idea de fondo (que este
desk se presente con los datos que produce) se conservo entera; lo que cambio
es que **el dato dejo de ser fondo y paso a ser la pieza**.

### El plano de la frontera (`pintarPlano`)

El hero es ahora un **plano riesgo / retorno**, que es la imagen fundacional de
la gestion de carteras. Cada cartera del corte es un disco:

| | |
|---|---|
| x | `metricas.mdd` en valor absoluto -- la caida maxima, o sea el riesgo |
| y | `metricas.exc` (o `retRel`) -- el retorno sobre el iShares MSCI ACWI |
| r | `puntos` del corte |

La **linea azul del cero ES el indice** (mismo token `--bmk` de siempre): sobre
ella el disco va lleno, bajo ella queda calado. Y la **linea dorada es la
frontera**: recorriendo de menos a mas riesgo, las carteras que superan a todas
las de menos riesgo que ellas. Bajo esa linea siempre existe otra cartera que
rindio mas arriesgando menos.

Dato que hace que valga la pena: **la frontera no es el ranking**. En el corte
de la semana 15 la componen 6 carteras y son las posiciones 1, 2, 3, 6, 7 y 15
-- Black Swan Capital entra con el riesgo mas bajo del torneo (1,38%) pese a ir
15a. Verificado aparte con Python contra `datos/torneo.json`, no solo por el
render.

**Sale de `datos/torneo-tabla.json` (7 KB), no del historial.** Es una mejora
real de degradacion respecto de la version anterior: el campo de trayectorias
necesitaba los 205 KB de `torneo.json`, asi que con `saveData` o en 2G el hero
se quedaba sin su pieza. El plano esta en pie desde la primera pintada.

Cuidado si se toca el SVG: los margenes son `pl=64 / pt=32` **a proposito**. Con
los 46/22 originales, "+20,00%" se cortaba contra el borde y el rotulo del eje Y
--que iba rotado a 90 grados-- se encimaba con las marcas. El rotulo del eje Y
va horizontal arriba a la izquierda; rotado no cabe.

### Lo demas que cambio, y por que

- **La cinta bajo el hero** era una marquesina de PALABRAS ("Asignacion de
  activos - Top-down - Control de riesgo"), decoracion que repetia lo que ya
  decia la pagina. Ahora corre el estado real del corte: semana, fecha,
  carteras, lider, puntaje, cuantas le ganan al ACWI, el mejor de cada una de
  las 5 metricas y el ACWI. **Las palabras siguen en el HTML como respaldo**: si
  el ranking no carga, la cinta se ve como antes en vez de quedar vacia.
- **§El corte** paso de cuatro tarjetas redondeadas iguales a un **tablero** de
  12 columnas separado por filetes de 1px, donde cada dato ocupa el ancho que le
  toca (el lider media fila, porque es un nombre y no un numero). El grafico se
  pega por abajo con `margin-top:-1px` y cierra el mismo bloque. Celda nueva:
  **"Le ganan al indice", 16 de 54**, que es la lectura central de este desk y
  no existia en ninguna parte del sitio.
- **§Como se evalua** se llama ahora **§Los 100 puntos** y abre con una **barra
  de asignacion**: los 100 puntos repartidos en cinco tramos proporcionales al
  peso real de cada metrica. El peso de una metrica ES una asignacion --el mismo
  gesto que hace el desk con el capital-- y cinco tarjetas no muestran una
  asignacion. Debajo, una franja a lo ancho por metrica. Los anchos siguen sin
  estar escritos: salen de `pesos()`.
- **Pilares** y **§Nosotros** dejaron de ser tarjetas sueltas: franjas con el
  numeral calado al aire, y una ficha unica dividida por filetes.
- **Riel de secciones** fijo al costado, solo desde 1460px. Se numera SOLO con
  las secciones visibles (§El corte, §Torneo y §Actividades pueden estar
  ocultas), asi que un numero escrito a mano se desalinearia; y cambia a tinta
  oscura sobre las secciones claras.
- **Esquinas rectas en toda la pagina** (`border-radius:0` en las tarjetas
  compartidas). Es el gesto que separa a Portafolio de `valuation/` y
  `trading/` sin tocar la paleta ni las tipografias. El avatar queda fuera: es
  un circulo a proposito.

`fotos/portafolio/` sigue sin leerse y `trayectorias()` se borro con el campo.

### Verificacion

Contrastado con Python contra `datos/torneo.json`: 54 carteras, 16 con exceso
positivo (ninguna en cero exacto), riesgo de 1,38% a 18,26%, exceso de -37,28%
a +20,83%, frontera de 6 carteras, pesos 30/25/15/15/15.

**Degradacion probada bloqueando los JSON en el navegador**, tres escenarios --
completo, sin el historial, y sin ningun dato del torneo. En los tres: cero
"NaN", cero desborde horizontal, cero excepciones JS. Sin historial el plano
sigue en pie y solo cae el grafico de mediana e intercuartil; sin nada del
torneo caen el plano, §El corte y la barra de los 100 puntos, la cinta vuelve a
las 16 palabras, las cifras del hero vuelven a su texto de respaldo y el riel se
renumera solo de 01 a 06. Texto en pie: 9546 / 8878 / 6650 caracteres.

`verificar_paginas.js` (las 19 paginas), `verificar_movil.js`,
`verificar_menu_movil.js --pag=portafolio/index.html` (7 enlaces, entra entero
en las tres pantallas) y `verificar_sitio.py`: sin errores.
