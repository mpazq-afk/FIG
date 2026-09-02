# CLAUDE.md — repo ESPEJO del sitio FIG (producción)

> Este archivo lo lee Claude Code automáticamente al abrir esta carpeta, **en cada
> sesión**. Por eso es corto a propósito.
>
> **Reestructurado el 2026-09-02**: antes eran 2063 líneas (~30 mil tokens en cada
> conversación). El contenido no se perdió, se movió a `docs/`.

## Lo primero que tienes que saber

**Este repo es el ESPEJO, no la fuente.** Tiene el `CNAME`
(`feninvestmentgroup.com`), o sea es el que **sirve producción** por GitHub Pages,
pero el trabajo se hace en el otro lado:

| | Repo | Rol |
|---|---|---|
| Fuente | `panchoscky/fig-web` — `OneDrive\Documentos\GitHub\fig-web` | Donde se desarrolla |
| **Este** | `mpazq-afk/mpazq-afk.github.io` | Donde se publica |

**No desarrolles acá.** Un cambio hecho directo en este repo se pierde en la próxima
sincronización. Haz el cambio en `fig-web` y publícalo con los scripts de allá:

```
# desde fig-web:
python sincronizar_espejo.py --aplicar
python despublicar_fiw.py --aplicar      # SIEMPRE inmediatamente después
# y después, DENTRO de este repo:
python generar_sitemap.py
```

Los dos primeros son un **par indivisible**: el primero copia, el segundo saca FIG
Woman. Correr el primero sin el segundo publica el área de mujeres acá, que es
exactamente lo que Francisco pidió que no pasara.

**Manuel edita este repo directamente** (es su repo, y el autor mayoritario con 109
commits). Antes de pushear acá, **siempre `git fetch` primero**: él trabaja sobre
producción y un push a ciegas puede rechazarse o pisarle trabajo.

## Dónde está cada cosa

| Necesitas… | Lee |
|---|---|
| Qué hace un archivo, dónde vive un dato | `docs/ARBOL_REPO.md` |
| El estado de una página antes de tocarla | `docs/ESTADO_PIEZAS.md` |
| Por qué algo quedó como quedó | `docs/BITACORA.md` |
| Las reglas duras y trampas vigentes | el `CLAUDE.md` de **`fig-web`** |

## Qué es esto

El ecosistema web de **FEN Investment Group (FIG)**, club de inversiones de la FEN —
Universidad de Chile. Páginas HTML autocontenidas (sin build step, sin framework,
compatibles con GitHub Pages) alimentadas por JSON bajo `datos/`.

**Filosofía no negociable:** Excel/Drive es la fuente de verdad → un script Python lo
convierte a JSON → las páginas HTML leen ese JSON y se renderizan solas. Nunca
hardcodear datos que van a cambiar.

**Paleta**: navy `#0A1128` + oro `#D4AF37`, Playfair Display + Inter + IBM Plex Mono
(autoalojadas en `fuentes/`).

## Qué se publica ACÁ y qué no

**12 páginas** (el sitemap las enumera): `index`, `torneo/`, `informe/`, `eventos/`,
`valuation/`, `portafolio/`, `trading/`, `postula/`, `juego/`, `desafio/`, `en/`,
`en/informe/`.

**No se publica acá, a propósito:**

- **`fiw/` — FIG Woman.** Decisión de Francisco. `despublicar_fiw.py` (que vive en
  `fig-web`) borra `fiw/`, `datos/fiw.json` y `fotos/fiw/`, y quita el área de 6
  páginas. **Si `/fiw/` responde acá, algo salió mal.**
- **`miembros/`** y sus datos — todavía no se publican.
- Las guías internas y las herramientas de video.

**Dos cosas de FIW quedan visibles acá a propósito, y no se tocan sin que Francisco lo
pida:** los cargos de las tres cofundadoras (Delia Avilán, Gabriela Domínguez, Victoria
Espinoza) en `club.json` — ocultar un área es una decisión de publicación, reescribirle
el currículum a una persona no — y el evento "Encuentro FEN Investment Woman" del
27-may en la bitácora, porque ocurrió y borrarlo sería editar la historia del club.

## Lo que difiere de `fig-web` a propósito

- **`index.html` NUNCA se copia entero.** Acá el nav no tiene Miembros y FIG Woman está
  oculta, así que "Comunidad ▾" se dejó como "Equipo" suelto. Para portar un cambio hay
  que llevar **solo el bloque tocado** y verificar después que el nav siga intacto.
  Casi siempre son TRES tramos separados: el `<style>`, el markup y el `<script>`.
- **Acá se publican CUATRO áreas** (PRT · Portafolio, TRD · Trading, VAL · Valuation,
  ADM · Administración), no cinco. El `h-sec` dice "Cuatro desks" y el stat
  "5 Áreas especializadas" de `fig-web` **no se aplica acá**.
- **ADM es `data-desk`/`view="3"`, no `"4"`** — este repo no tiene panel FIW.
- En `portafolio/` y `trading/`, la frase "junto a … y FEN Investment Woman" se cambió a
  **"entre otras"**.
- **`MAPA_CONTENIDO_FIG.html` tiene dos scripts propios de Manuel** que limpian la URL
  (le sacan `/index.html` y el `#`). Está en `NO_SE_COPIAN`: copiar la versión de
  `fig-web` se los borraría.
- **`config.sitio` está vacío en `fig-web` a propósito** (usa el origen del navegador).

## Trampa que cuesta cada vez: los finales de línea

**Este repo guarda TODO en CRLF y `fig-web` está en LF.** Copiar un archivo a lo bruto
hace que git muestre cada archivo como si hubieran cambiado sus 3.000 líneas, y el
cambio real queda invisible.

`sincronizar_espejo.py` ya lo respeta (`copiar_conservando_fin_de_linea()`, y compara
ignorando el fin de línea — sin eso reportaría los mismos 30 archivos como pendientes
para siempre). Si portas algo a mano, normaliza tú.

En Python de Windows, `pathlib.read_text()` **no acepta `newline=`**: usa
`io.open(..., newline='')` para no destrozar los finales de línea al reescribir.

Y ojo: **`sincronizar_espejo.py` siempre reportará 5 archivos "por copiar"** aunque nada
haya cambiado, porque `despublicar_fiw.py` se los reescribe después. No es un error.

## Reglas duras

- **Nunca `git push` acá sin autorización explícita de Francisco.** Es el repo de otra
  persona, y además es producción en vivo.
- **`git fetch` antes de cualquier push**: Manuel trabaja directo sobre este repo.
- **FIG Woman no se publica acá.**
- **Nunca** commitear datos personales más allá de nombre + rol + LinkedIn público.
- **Sin build step**: HTML/CSS/JS planos, sin npm ni bundler.
- `generar_sitemap.py` se corre **dentro de este repo** al final de cada publicación,
  porque acá se publican menos páginas y el sitemap tiene que enumerar las que de
  verdad existen (hoy 12).

## Verificar antes de dar algo por publicado

```
python -m http.server 8000     # en otra terminal
node verificar_paginas.js      # errores de consola y archivos faltantes
node verificar_movil.js        # teléfono, 390x844
python verificar_sitio.py      # datos y derivados
```

**Este sitio hace 404 a propósito**: las fotos y logos se detectan sondeando rutas hasta
que una carga. Esos 404 van en `RUTAS_SONDEADAS` y no son errores.

`verificar_sitio.py` marca como **AVISO** (no error) que falte una página de
`CANONICAS`: acá se publican menos páginas a propósito.

## Estado (2026-09-02)

Último commit: `194bdbb` — cinco desks (nace Administración, llegan las páginas de
Portafolio y Trading). Los dos repos están al día y sincronizados por el script.

Torneo: **48 equipos, semana 16** (corte 28-ago-2026), ACWI al día.
