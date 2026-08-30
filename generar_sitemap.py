"""
generar_sitemap.py -- Escribe sitemap.xml y robots.txt.

Por que
--------
El sitio no tenia ninguno de los dos. Sin sitemap, Google descubre las paginas
solo siguiendo enlaces, y varias (postula, en, valuation, miembros) cuelgan de
menus desplegables o de un solo enlace en el pie. Sin robots.txt, cada
rastreador decide por su cuenta que hacer con las 54 micro-paginas de equipo.

Que entra y que no
-------------------
ENTRAN las paginas reales del sitio.

NO ENTRA `torneo/e/*.html`: son 54 redirecciones casi identicas que existen solo
para que el link de cada equipo tenga vista previa propia al compartirlo. Ya
llevan `noindex` y un canonical al ranking; meterlas en el sitemap seria pedirle
a Google justo lo contrario de lo que dicen sus propias etiquetas.

Tampoco entran las guias internas (`GUIA_DRIVE_FIG.html`,
`MAPA_CONTENIDO_FIG.html`), que son para el equipo, ni `404.html`.

La fecha de cada URL sale del `git log` del archivo -- no de su mtime, que en
un clon reciente es la fecha del clon y no dice nada.

Uso:
    python generar_sitemap.py
"""

from __future__ import annotations
import json
import pathlib
import subprocess
import sys
import xml.sax.saxutils as saxutils

RAIZ = pathlib.Path(__file__).resolve().parent
SITIO_POR_DEFECTO = "https://feninvestmentgroup.com"

# Fuera del sitemap, con el motivo al lado.
EXCLUIDAS = {
    "404.html": "pagina de error",
    "GUIA_DRIVE_FIG.html": "guia interna del equipo",
    "MAPA_CONTENIDO_FIG.html": "guia interna del equipo",
    # Las dos pantallas no son paginas para leer: una corre en bucle en un TV y
    # la otra es la fuente del video semanal. Que aparezcan en un buscador seria
    # mandar a alguien a una animacion sin navegacion ni contexto.
    "torneo/pantalla.html": "pantalla en bucle para las TV",
    "torneo/pantalla-facultad.html": "fuente del video semanal",
}

# Prioridad relativa. Lo que no este aca va con 0.5.
PRIORIDAD = {
    "index.html": "1.0",
    "torneo/index.html": "0.9",
    "informe/index.html": "0.8",
    "eventos/index.html": "0.8",
    "miembros/index.html": "0.8",
    "postula/index.html": "0.8",
    "valuation/index.html": "0.7",
    "en/index.html": "0.6",
}

ROBOTS = """# Generado por generar_sitemap.py -- no editar a mano.

User-agent: *
Allow: /

# Las paginas por equipo son redirecciones al ranking, con vista previa propia
# para compartir. Ya llevan noindex; esto se lo dice tambien a los rastreadores
# que no leen la etiqueta. Los de redes sociales (LinkedIn, WhatsApp) ignoran
# robots.txt a proposito y siguen leyendo las og, que es lo que queremos.
Disallow: /torneo/e/

Sitemap: {sitio}/sitemap.xml
"""


def fecha_git(ruta: pathlib.Path) -> str | None:
    """Ultima fecha de commit del archivo (YYYY-MM-DD), o None si no hay git."""
    try:
        salida = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(ruta.relative_to(RAIZ))],
            cwd=RAIZ, capture_output=True, text=True, timeout=15,
        )
        v = salida.stdout.strip()
        return v or None
    except (OSError, subprocess.SubprocessError):
        return None


def main() -> int:
    sitio = SITIO_POR_DEFECTO
    club = RAIZ / "datos" / "club.json"
    if club.exists():
        try:
            cfg = json.loads(club.read_text(encoding="utf-8")).get("config") or {}
            sitio = (cfg.get("sitio") or sitio)
        except json.JSONDecodeError:
            pass
    sitio = sitio.rstrip("/")

    urls = []
    for ruta in sorted(RAIZ.rglob("*.html")):
        rel = str(ruta.relative_to(RAIZ)).replace("\\", "/")
        if rel.startswith("torneo/e/") or rel in EXCLUIDAS:   # ver EXCLUIDAS
            continue
        # index.html se publica como la carpeta, sin el nombre de archivo
        publica = rel[:-len("index.html")] if rel.endswith("index.html") else rel
        urls.append((f"{sitio}/{publica}", PRIORIDAD.get(rel, "0.5"), fecha_git(ruta)))

    lineas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<!-- Generado por generar_sitemap.py, no editar a mano. -->',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, prio, fecha in urls:
        lineas.append("  <url>")
        lineas.append(f"    <loc>{saxutils.escape(loc)}</loc>")
        if fecha:
            lineas.append(f"    <lastmod>{fecha}</lastmod>")
        lineas.append(f"    <priority>{prio}</priority>")
        lineas.append("  </url>")
    lineas.append("</urlset>")

    (RAIZ / "sitemap.xml").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    (RAIZ / "robots.txt").write_text(ROBOTS.format(sitio=sitio), encoding="utf-8")

    print(f"OK: sitemap.xml con {len(urls)} URLs y robots.txt")
    for loc, prio, fecha in urls:
        print(f"  {prio}  {loc}  {fecha or '(sin fecha de git)'}")
    print("\ntorneo/e/ queda fuera a proposito: son redirecciones con noindex.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
