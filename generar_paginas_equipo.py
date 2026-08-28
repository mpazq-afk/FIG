"""
generar_paginas_equipo.py -- Escribe torneo/e/<id>.html, una micro-pagina por
equipo, para que el link de cada equipo tenga vista previa propia.

El problema que resuelve
------------------------
El ranking ya tiene deep link por equipo (torneo/index.html#beta-capital), pero
las etiquetas Open Graph son las de la pagina completa: cuando alguien pega su
link en LinkedIn, WhatsApp o Slack, los 54 equipos muestran exactamente la misma
tarjeta generica. Con 145 inscritos eso es el canal de difusion mas grande del
torneo desperdiciado.

GitHub Pages sirve archivos estaticos, no puede armar las etiquetas al vuelo, asi
que se generan de antemano: una pagina minima por equipo cuyo unico trabajo es
llevar las etiquetas correctas y mandar al visitante al ranking real.

Que escribe cada pagina
------------------------
  - <title> y og:title propios: "Beta capital - 1° de 54"
  - og:description con puntaje, retorno relativo y semana del corte
  - og:image: og/equipo-<id>.jpg si existe (la genera generar_og_equipos.js);
    si no, cae a la imagen del sitio, /og-image.png
  - canonical al ranking real, para que Google no las trate como paginas aparte
  - noindex,follow: son 54 paginas casi identicas, no queremos que compitan en
    el buscador con el ranking. Los rastreadores de redes sociales leen las
    etiquetas og igual -- ignoran noindex, que es justo lo que nos sirve
  - redireccion inmediata al ranking (JS + <meta refresh> de respaldo) y, para
    quien llegue sin JS, un enlace visible con los datos del equipo

Cuando correrlo
----------------
Cada vez que cambie el ranking, porque los puestos van en el texto:

    python generar_torneo.py --excel <Excel del corte> --semana N --corte "..."
    python generar_tabla.py
    node generar_og_equipos.js          # opcional, las imagenes (ver su cabecera)
    python generar_paginas_equipo.py

Es seguro correrlo siempre: reescribe torneo/e/ entero y borra las paginas de
equipos que ya no estan en el torneo, para no dejar links vivos apuntando a
equipos que salieron.
"""

from __future__ import annotations
import argparse
import html
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
TORNEO = RAIZ / "datos" / "torneo.json"
SALIDA = RAIZ / "torneo" / "e"
OG = RAIZ / "og"

# El dominio propio del sitio (el del CNAME del repo de deploy). Las etiquetas
# og:image y og:url tienen que ser ABSOLUTAS: los rastreadores de LinkedIn y
# WhatsApp no resuelven rutas relativas.
SITIO_POR_DEFECTO = "https://feninvestmentgroup.com"

PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- GENERADO por generar_paginas_equipo.py -- no editar a mano, se reescribe
     entero con cada corte. Su unico trabajo es llevar la vista previa correcta
     de {nombre} y mandar al ranking real. -->

<title>{titulo}</title>
<meta name="description" content="{descripcion}">
<link rel="canonical" href="{url_ranking}">
<!-- 54 paginas casi iguales no deben competir con el ranking en el buscador.
     Los rastreadores de redes sociales ignoran esto y leen las og igual. -->
<meta name="robots" content="noindex,follow">
<meta name="theme-color" content="#0A1128">

<meta property="og:type" content="website">
<meta property="og:site_name" content="FEN Investment Group">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descripcion}">
<meta property="og:url" content="{url_ranking}">
<meta property="og:image" content="{imagen}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="627">
<meta property="og:image:alt" content="Tarjeta del torneo de {nombre}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{titulo}">
<meta name="twitter:description" content="{descripcion}">
<meta name="twitter:image" content="{imagen}">

<link rel="icon" href="../../logos/fig-oro.png">
<!-- respaldo por si el JS no corre; el redirect real lo hace el script de abajo -->
<meta http-equiv="refresh" content="0; url=../index.html#{id}">
<style>
  body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       background:#0A1128;color:#F7F4EC;font-family:system-ui,-apple-system,'Segoe UI',sans-serif;
       text-align:center;padding:24px;line-height:1.6}}
  a{{color:#D4AF37}}
  .pos{{font-size:2.4rem;font-weight:700;color:#D4AF37;margin:0 0 6px}}
  h1{{font-size:1.4rem;margin:0 0 14px;font-weight:600}}
  p{{margin:0 0 18px;color:rgba(247,244,236,.7);max-width:46ch}}
</style>
</head>
<body>
  <main>
    <div class="pos">{posicion}° de {total}</div>
    <h1>{nombre}</h1>
    <p>{descripcion}</p>
    <p><a href="../index.html#{id}">Ver el ranking completo del Torneo Portafolio 2026 &rarr;</a></p>
  </main>
<script>
/* Redirige de inmediato al ranking real. replace() en vez de href para no dejar
   esta pagina intermedia en el historial: si no, el boton "atras" del navegador
   rebotaria aca y volveria a mandar al ranking, dejando al visitante atrapado. */
location.replace("../index.html#{id}");
</script>
</body>
</html>
"""

LEEME = """Esta carpeta la escribe generar_paginas_equipo.py -- NO editar a mano.

Es una pagina por equipo del torneo, cuyo unico trabajo es que el link de ese
equipo tenga vista previa propia al compartirlo (LinkedIn, WhatsApp, Slack).
Cada una redirige al ranking real, torneo/index.html#<id>.

Se reescriben enteras con cada corte, porque los puestos van en el texto. Si un
equipo sale del torneo, su pagina se borra sola en la siguiente corrida.

Para regenerarlas:
    python generar_paginas_equipo.py

El link que se comparte es:
    https://feninvestmentgroup.com/torneo/e/<id>.html
"""


def formatear_pct(v) -> str:
    if v is None:
        return "s/d"
    return ("+" if v >= 0 else "") + f"{v * 100:.2f}".replace(".", ",") + "%"


def descripcion_de(eq: dict, total: int, semana) -> str:
    puntos = f"{eq.get('puntos', 0):.2f}".replace(".", ",")
    partes = [
        f"{eq['nombre']} va {eq['posicion']}° de {total} en el Torneo Portafolio 2026 "
        f"de FEN Investment Group, con {puntos} puntos de 100 y "
        f"{formatear_pct(eq.get('retRel'))} de retorno relativo al MSCI ACWI."
    ]
    if semana:
        partes.append(f"Corte de la semana {semana}.")
    return " ".join(partes)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default=None,
                    help=f"dominio absoluto del sitio (por defecto {SITIO_POR_DEFECTO}, "
                         "o config.sitio de datos/club.json si esta lleno)")
    args = ap.parse_args()

    if not TORNEO.exists():
        print("No existe datos/torneo.json -- nada que generar.")
        return 0

    sitio = args.sitio
    if not sitio:
        try:
            club = json.loads((RAIZ / "datos" / "club.json").read_text(encoding="utf-8"))
            sitio = (club.get("config") or {}).get("sitio") or ""
        except (OSError, json.JSONDecodeError):
            sitio = ""
    sitio = (sitio or SITIO_POR_DEFECTO).rstrip("/")

    datos = json.loads(TORNEO.read_text(encoding="utf-8"))
    equipos = datos.get("equipos", [])
    if not equipos:
        print("datos/torneo.json no trae equipos -- nada que generar.")
        return 0

    total = len(equipos)
    semana = datos.get("semana")
    SALIDA.mkdir(parents=True, exist_ok=True)

    vigentes = set()
    sin_imagen = 0
    for eq in equipos:
        eid = eq["id"]
        vigentes.add(f"{eid}.html")
        img_local = OG / f"equipo-{eid}.jpg"
        if img_local.exists():
            imagen = f"{sitio}/og/equipo-{eid}.jpg"
        else:
            imagen = f"{sitio}/og-image.png"
            sin_imagen += 1

        desc = descripcion_de(eq, total, semana)
        titulo = f"{eq['nombre']} · {eq['posicion']}° de {total} — Torneo Portafolio 2026"
        pagina = PLANTILLA.format(
            id=html.escape(eid, quote=True),
            nombre=html.escape(eq["nombre"]),
            titulo=html.escape(titulo, quote=True),
            descripcion=html.escape(desc, quote=True),
            imagen=html.escape(imagen, quote=True),
            url_ranking=html.escape(f"{sitio}/torneo/#{eid}", quote=True),
            posicion=eq["posicion"],
            total=total,
        )
        (SALIDA / f"{eid}.html").write_text(pagina, encoding="utf-8")

    # equipos que ya no estan: se borran para no dejar links vivos con datos viejos
    borradas = 0
    for viejo in SALIDA.glob("*.html"):
        if viejo.name not in vigentes:
            viejo.unlink()
            borradas += 1

    (SALIDA / "LEEME.txt").write_text(LEEME, encoding="utf-8")

    print(f"OK: {len(equipos)} paginas en torneo/e/")
    if sin_imagen:
        print(f"  {sin_imagen} sin imagen propia -> usan {sitio}/og-image.png")
        print("  (para generarlas: node generar_og_equipos.js -- ver su cabecera)")
    if borradas:
        print(f"  {borradas} pagina(s) de equipos que ya no estan, borradas")
    print(f"  link de ejemplo: {sitio}/torneo/e/{equipos[0]['id']}.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
