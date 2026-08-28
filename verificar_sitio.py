"""
verificar_sitio.py -- Chequeo rapido antes de publicar.

Por que existe
--------------
Este sitio tiene datos que viven en mas de un lugar a la vez: archivos derivados
que hay que regenerar (datos/torneo-tabla.json, torneo/e/*.html, og/*.jpg) y
numeros escritos a mano en el HTML que tienen que calzar con el JSON (las meta
etiquetas dicen "54 equipos"). Cada vez que uno de esos se quedo atras hubo que
descubrirlo mirando la pagina: la correccion 63 -> 59 -> 54 se hizo tres veces, a
mano, y siempre quedo alguna mencion suelta (en/index.html estuvo meses con
"Sixty-three").

Esto lo revisa en un segundo. No arregla nada por su cuenta salvo que se lo pidas
con --arreglar, y ahi solo toca lo que es DERIVADO: nunca edita datos ni HTML
escrito por una persona.

Uso
----
    python verificar_sitio.py              # revisa y reporta
    python verificar_sitio.py --arreglar   # ademas regenera los derivados

Devuelve 1 si hay ERRORES (algo objetivamente desincronizado) y 0 si solo hay
AVISOS (cosas que conviene que mire una persona, como una mencion de un numero
en un texto historico que quiza deba quedarse como esta).
"""

from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
DATOS = RAIZ / "datos"

ERRORES: list[str] = []
AVISOS: list[str] = []
BIEN: list[str] = []


def error(msg: str) -> None:
    ERRORES.append(msg)


def aviso(msg: str) -> None:
    AVISOS.append(msg)


def bien(msg: str) -> None:
    BIEN.append(msg)


def rel(p: pathlib.Path) -> str:
    try:
        return str(p.relative_to(RAIZ)).replace("\\", "/")
    except ValueError:
        return str(p)


# --------------------------------------------------------------------------
def revisar_json() -> dict:
    """Todos los .json de datos/ parsean. Devuelve el torneo ya leido."""
    rotos = []
    for ruta in sorted(DATOS.rglob("*.json")):
        try:
            json.loads(ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            rotos.append(f"{rel(ruta)}: {e}")
    if rotos:
        for r in rotos:
            error(f"JSON invalido -- {r}")
    else:
        bien(f"los {len(list(DATOS.rglob('*.json')))} JSON de datos/ parsean")

    ruta_t = DATOS / "torneo.json"
    if not ruta_t.exists():
        return {}
    try:
        return json.loads(ruta_t.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def revisar_tabla_derivada() -> bool:
    """datos/torneo-tabla.json corresponde al torneo.json actual."""
    fuente = DATOS / "torneo.json"
    derivado = DATOS / "torneo-tabla.json"
    if not fuente.exists():
        return True
    if not derivado.exists():
        aviso("falta datos/torneo-tabla.json -- la pagina carga el archivo completo "
              "(funciona, pero baja ~20 KB de mas). Generalo con generar_tabla.py")
        return False
    try:
        d = json.loads(derivado.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        error("datos/torneo-tabla.json no parsea")
        return False
    sha = hashlib.sha1(fuente.read_bytes()).hexdigest()
    if d.get("_fuenteSha1") != sha:
        error("datos/torneo-tabla.json quedo ATRAS respecto de datos/torneo.json "
              "-- corre generar_tabla.py")
        return False
    bien("datos/torneo-tabla.json al dia")
    return True


def revisar_paginas_equipo(torneo: dict) -> bool:
    """torneo/e/<id>.html existe para cada equipo y con el puesto correcto."""
    carpeta = RAIZ / "torneo" / "e"
    equipos = torneo.get("equipos", [])
    if not equipos:
        return True
    if not carpeta.exists():
        aviso("no existe torneo/e/ -- los links por equipo no tienen vista previa "
              "propia. Generalas con generar_paginas_equipo.py")
        return False

    total = len(equipos)
    esperados = {f"{e['id']}.html" for e in equipos}
    actuales = {p.name for p in carpeta.glob("*.html")}

    faltan = esperados - actuales
    sobran = actuales - esperados
    desfasadas = []
    for eq in equipos:
        p = carpeta / f"{eq['id']}.html"
        if not p.exists():
            continue
        texto = p.read_text(encoding="utf-8")
        # el puesto va en el <title>; si cambio, la vista previa miente
        if f"{eq['posicion']}° de {total}" not in texto:
            desfasadas.append(eq["id"])

    if faltan or sobran or desfasadas:
        if faltan:
            error(f"torneo/e/: faltan {len(faltan)} pagina(s) ({', '.join(sorted(faltan)[:3])}...)")
        if sobran:
            error(f"torneo/e/: sobran {len(sobran)} pagina(s) de equipos que ya no estan "
                  f"({', '.join(sorted(sobran)[:3])}...)")
        if desfasadas:
            error(f"torneo/e/: {len(desfasadas)} pagina(s) con el puesto viejo en la vista "
                  f"previa ({', '.join(desfasadas[:3])}...)")
        error("  -> corre generar_paginas_equipo.py")
        return False

    bien(f"torneo/e/: {total} paginas al dia")
    return True


def revisar_imagenes_og(torneo: dict) -> None:
    """og/equipo-<id>.jpg -- son opcionales, asi que esto solo avisa."""
    equipos = torneo.get("equipos", [])
    if not equipos:
        return
    carpeta = RAIZ / "og"
    sin = [e["id"] for e in equipos if not (carpeta / f"equipo-{e['id']}.jpg").exists()]
    if not carpeta.exists() or len(sin) == len(equipos):
        aviso("og/: ningun equipo tiene imagen de vista previa propia -- todos usan "
              "og-image.png. Opcional, ver generar_og_equipos.js")
    elif sin:
        aviso(f"og/: {len(sin)} equipo(s) sin imagen propia ({', '.join(sin[:3])}...) "
              "-- corre node generar_og_equipos.js")
    else:
        bien(f"og/: los {len(equipos)} equipos tienen imagen de vista previa")


def revisar_conteo_equipos(torneo: dict) -> None:
    """Las mencionas escritas a mano de "N equipos" calzan con el JSON."""
    equipos = torneo.get("equipos", [])
    if not equipos:
        return
    n = len(equipos)
    patron = re.compile(r"\b(\d{2,3})\s+equipos\b", re.IGNORECASE)
    malas = []
    for ruta in sorted(list(RAIZ.rglob("*.html")) + list(DATOS.rglob("*.json"))):
        if ".git" in ruta.parts or ruta.name.endswith(".demo.json"):
            continue
        if (RAIZ / "torneo" / "e") in ruta.parents:      # generadas, salen del JSON
            continue
        try:
            texto = ruta.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for linea_n, linea in enumerate(texto.splitlines(), 1):
            for m in patron.finditer(linea):
                if int(m.group(1)) != n:
                    malas.append(f"{rel(ruta)}:{linea_n} dice \"{m.group(0)}\"")
    if malas:
        aviso(f"hay {len(malas)} mencion(es) de un numero de equipos distinto de {n}:")
        for m in malas[:8]:
            aviso(f"    {m}")
        if len(malas) > 8:
            aviso(f"    ... y {len(malas) - 8} mas")
        aviso("    (revisalas a mano: algunas pueden ser historicas a proposito)")
    else:
        bien(f"todas las menciones escritas a mano dicen {n} equipos")


# Techo del HTML de una pagina, en KB de FUENTE (sin comprimir). Todo va inline
# en este sitio -- CSS, JS y datos de respaldo dentro del mismo archivo --, asi
# que el .html es casi todo el peso critico. Es un aviso, no un error: la idea
# es enterarse cuando una pagina crece, no prohibir que crezca.
# Medicion complementaria y mas fiel en verificar_paginas.js, que mide lo que de
# verdad se transfiere en un navegador; esta corre sin Chrome.
TECHO_HTML_KB = 200


def revisar_peso_html() -> None:
    grandes = []
    for ruta in sorted(RAIZ.rglob("*.html")):
        if ".git" in ruta.parts or (RAIZ / "torneo" / "e") in ruta.parents:
            continue
        kb = ruta.stat().st_size / 1024
        if kb > TECHO_HTML_KB:
            grandes.append((kb, rel(ruta)))
    if grandes:
        aviso(f"paginas por sobre {TECHO_HTML_KB} KB de fuente:")
        for kb, r in sorted(grandes, reverse=True):
            aviso(f"    {r}  {kb:.0f} KB")
    else:
        bien(f"ninguna pagina pasa los {TECHO_HTML_KB} KB de fuente")


def revisar_derivados_seo() -> None:
    """sitemap.xml y robots.txt existen y el sitemap no lista las micro-paginas."""
    sm, rb = RAIZ / "sitemap.xml", RAIZ / "robots.txt"
    if not sm.exists() or not rb.exists():
        aviso("faltan sitemap.xml y/o robots.txt -- generalos con generar_sitemap.py")
        return
    texto = sm.read_text(encoding="utf-8")
    if "/torneo/e/" in texto:
        error("sitemap.xml lista las micro-paginas de equipo, que van con noindex "
              "-- corre generar_sitemap.py")
        return
    bien(f"sitemap.xml ({texto.count('<url>')} URLs) y robots.txt al dia")


def revisar_creadores() -> None:
    """Cada nombre de torneo.creadores tiene ficha en personas.directiva."""
    ruta = DATOS / "club.json"
    if not ruta.exists():
        return
    try:
        club = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    creadores = ((club.get("torneo") or {}).get("creadores")) or []
    if not creadores:
        aviso("datos/club.json no trae torneo.creadores -- la seccion #creadores "
              "de torneo/index.html queda oculta")
        return
    directiva = {p.get("nombre") for p in ((club.get("personas") or {}).get("directiva") or [])}
    huerfanos = [c["nombre"] for c in creadores if c.get("nombre") not in directiva]
    if huerfanos:
        error("torneo.creadores tiene nombres sin ficha en personas.directiva "
              f"(su tarjeta NO se dibuja): {', '.join(huerfanos)}")
    else:
        bien(f"los {len(creadores)} creadores calzan con personas.directiva")


# --------------------------------------------------------------------------
def arreglar() -> None:
    """Regenera SOLO los archivos derivados. Nunca toca datos ni HTML a mano."""
    for script in ("generar_tabla.py", "generar_paginas_equipo.py", "generar_sitemap.py"):
        ruta = RAIZ / script
        if not ruta.exists():
            continue
        print(f"\n$ python {script}")
        subprocess.run([sys.executable, str(ruta)], cwd=RAIZ, check=False)
    print("\n(las imagenes og/ no se regeneran solas: necesitan Chrome y un server "
          "local -- ver node generar_og_equipos.js)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arreglar", action="store_true",
                    help="regenera los archivos derivados y vuelve a revisar")
    args = ap.parse_args()

    torneo = revisar_json()
    revisar_tabla_derivada()
    revisar_paginas_equipo(torneo)
    revisar_imagenes_og(torneo)
    revisar_conteo_equipos(torneo)
    revisar_creadores()
    revisar_derivados_seo()
    revisar_peso_html()

    if args.arreglar and (ERRORES or AVISOS):
        arreglar()
        ERRORES.clear(); AVISOS.clear(); BIEN.clear()
        print("\n--- de nuevo, ya regenerado ---")
        torneo = revisar_json()
        revisar_tabla_derivada()
        revisar_paginas_equipo(torneo)
        revisar_imagenes_og(torneo)
        revisar_conteo_equipos(torneo)
        revisar_creadores()
        revisar_derivados_seo()
        revisar_peso_html()

    print()
    for b in BIEN:
        print(f"  OK    {b}")
    for a in AVISOS:
        print(f"  AVISO {a}")
    for e in ERRORES:
        print(f"  ERROR {e}")

    print()
    if ERRORES:
        print(f"{len(ERRORES)} error(es). No publiques asi.")
        return 1
    if AVISOS:
        print(f"Sin errores, {len(AVISOS)} aviso(s) para mirar.")
        return 0
    print("Todo en orden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
