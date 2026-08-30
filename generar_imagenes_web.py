#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_imagenes_web.py — deriva las versiones que el sitio realmente sirve.

POR QUE EXISTE
--------------
`optimizar_fotos.py` comprime el JPG ORIGINAL en su sitio (max 2000 px, q78).
Eso deja un archivo bueno para archivar, pero es el mismo archivo que el sitio
le manda a un telefono. Medido el 2026-08-28 con Chrome emulando 4G lento:

  - `eventos/index.html` bajaba 2,1 MB, de los cuales ~1,9 MB eran los FONDOS
    de las tarjetas: `.ev-bg` pedia `1.jpg` (250-330 KB) para pintar un
    rectangulo de 400 px de ancho.
  - La tira de fotos de la portada (`.photo-marquee`) hacia lo mismo con la
    primera foto de cada evento — y se dibuja al 13% de opacidad y en
    escala de grises.

O sea: se bajaban megabytes de detalle que nadie llega a ver nunca.

QUE GENERA (los originales NO se tocan)
---------------------------------------
    fotos/eventos/<ev>/<n>.webp        lado mayor 1600 — galeria y lightbox
    fotos/eventos/<ev>/mini/<n>.webp   lado mayor  720 — fondos y tira
    fotos/directiva/<slug>.webp        lado mayor  800 — ficha de persona
    fotos/directiva/mini/<slug>.webp   lado mayor  240 — avatares y thumbs
    datos/fotos.json                   manifiesto: que existe y de que tamano

EL MANIFIESTO
-------------
El sitio detecta fotos SONDEANDO (`1.jpg`, `2.jpg`... hasta que una falla).
Eso es comodo — se sube una foto y aparece sola — pero cuesta un 404 por
carpeta y, sobre todo, el navegador no sabe cuanto mide cada foto hasta que
la baja, asi que el texto salta mientras cargan.

`datos/fotos.json` resuelve las dos cosas sin perder la comodidad: si esta,
el JS lo lee y sabe de antemano cuantas fotos hay y sus dimensiones; si no
esta (o la carpeta es nueva y todavia no se regenero), el JS cae al sondeo
de siempre. Ninguna pagina depende de este archivo para funcionar.

WEBP Y CALIDAD
--------------
WebP con calidad 82 sobre una foto ya comprimida a JPG q78 pesa la mitad sin
diferencia visible — la perdida real ya ocurrio en el JPG, el WebP solo
guarda ese mismo resultado con mejor codificacion. Las miniaturas van a q72
porque se dibujan a 400 px o menos, y en la tira ademas en escala de grises
y al 13% de opacidad.

Todo HTML que las use tiene que caer al `.jpg` si el `.webp` falta: un
navegador viejo, o una foto subida despues de la ultima corrida.

Uso:
    python generar_imagenes_web.py              # genera lo que falte
    python generar_imagenes_web.py --forzar     # regenera todo
    python generar_imagenes_web.py --dry-run    # solo dice que haria

Requiere: Pillow.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
FOTOS = RAIZ / "fotos"
EXT_ORIGEN = (".jpg", ".jpeg", ".png")

# lado mayor en px y calidad WebP de cada derivado
GRANDE_EVENTO, Q_GRANDE = 1600, 82
MINI_EVENTO, Q_MINI = 720, 72
GRANDE_PERSONA, Q_PERSONA = 800, 82
MINI_PERSONA, Q_MINI_PERSONA = 240, 78


def abrir(ruta):
    from PIL import Image, ImageOps
    im = Image.open(ruta)
    im = ImageOps.exif_transpose(im)  # fotos de celular vienen rotadas por metadato
    return im.convert("RGB") if im.mode != "RGB" else im


def derivar(origen, destino, lado, calidad, forzar, dry_run):
    """Escribe `destino` como WebP de lado mayor `lado`. Devuelve KB ahorrados."""
    if destino.exists() and not forzar and destino.stat().st_mtime >= origen.stat().st_mtime:
        return 0, False
    if dry_run:
        return origen.stat().st_size // 1024, True
    destino.parent.mkdir(parents=True, exist_ok=True)
    with abrir(origen) as im:
        if max(im.size) > lado:
            from PIL import Image as _Im
            im.thumbnail((lado, lado), _Im.LANCZOS)
        im.save(destino, "WEBP", quality=calidad, method=5)
    return (origen.stat().st_size - destino.stat().st_size) // 1024, True


def numeradas(carpeta):
    """Las fotos `1.jpg`, `2.jpg`... de una carpeta de evento, en orden."""
    salida = []
    n = 1
    while True:
        hallada = next((carpeta / f"{n}{e}" for e in EXT_ORIGEN if (carpeta / f"{n}{e}").exists()), None)
        if hallada is None:
            return salida
        salida.append((n, hallada))
        n += 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--forzar", action="store_true", help="regenerar aunque el derivado ya exista")
    ap.add_argument("--dry-run", action="store_true", help="mostrar que haria sin escribir")
    args = ap.parse_args()

    try:
        import PIL  # noqa: F401
    except ImportError:
        sys.exit("Falta Pillow: pip install Pillow")

    manifiesto = {"generado": date.today().isoformat(), "eventos": {}, "directiva": {}}
    ahorro = hechos = 0

    # --- eventos -----------------------------------------------------------
    base = FOTOS / "eventos"
    for carpeta in sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []:
        fotos = numeradas(carpeta)
        if not fotos:
            continue
        lista = []
        for n, origen in fotos:
            with abrir(origen) as im:
                ancho, alto = im.size
            for destino, lado, q in (
                (carpeta / f"{n}.webp", GRANDE_EVENTO, Q_GRANDE),
                (carpeta / "mini" / f"{n}.webp", MINI_EVENTO, Q_MINI),
            ):
                kb, tocado = derivar(origen, destino, lado, q, args.forzar, args.dry_run)
                ahorro += kb
                hechos += 1 if tocado else 0
            # dimensiones del derivado grande: es lo que el navegador va a pintar
            escala = min(1.0, GRANDE_EVENTO / max(ancho, alto))
            lista.append({"i": n, "w": round(ancho * escala), "h": round(alto * escala)})
        manifiesto["eventos"][carpeta.name] = lista
        print(f"  eventos/{carpeta.name}: {len(fotos)} fotos")

    # --- directiva ---------------------------------------------------------
    base = FOTOS / "directiva"
    for origen in sorted(base.glob("*")) if base.exists() else []:
        if not origen.is_file() or origen.suffix.lower() not in EXT_ORIGEN:
            continue
        slug = origen.stem
        for destino, lado, q in (
            (base / f"{slug}.webp", GRANDE_PERSONA, Q_PERSONA),
            (base / "mini" / f"{slug}.webp", MINI_PERSONA, Q_MINI_PERSONA),
        ):
            kb, tocado = derivar(origen, destino, lado, q, args.forzar, args.dry_run)
            ahorro += kb
            hechos += 1 if tocado else 0
        with abrir(origen) as im:
            ancho, alto = im.size
        escala = min(1.0, GRANDE_PERSONA / max(ancho, alto))
        manifiesto["directiva"][slug] = {"w": round(ancho * escala), "h": round(alto * escala)}
    print(f"  directiva: {len(manifiesto['directiva'])} personas")

    if not args.dry_run:
        (RAIZ / "datos" / "fotos.json").write_text(
            json.dumps(manifiesto, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    verbo = "se generarian" if args.dry_run else "generados"
    print(f"\n{hechos} derivados {verbo}. Ahorro aproximado: {ahorro // 1024} MB.")
    if not args.dry_run:
        print("Manifiesto escrito en datos/fotos.json.")


if __name__ == "__main__":
    main()
