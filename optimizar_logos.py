#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
optimizar_logos.py — achica los PNG de logos/ SIN cambiarles el nombre ni el
formato, y solo cuando se puede hacer sin que se note.

POR QUE
-------
`logos/fig-oro.png` pesaba 38 KB y aparece en el preloader y el nav de LAS 14
paginas: despues de las tipografias era el archivo mas pesado de casi toda
carga. Pero un logo no es una foto — el de FIG usa 1673 colores en 500x500,
casi todos del mismo dorado. Guardado con paleta de 256 colores pesa 8 KB y la
diferencia media por pixel es de 0,11 sobre 255, o sea invisible.

EL UMBRAL, QUE ES LO IMPORTANTE
--------------------------------
Eso NO vale para todos. `logos/fen.png` tiene 13.504 colores y degradados
reales: con paleta baja de 94 a 19 KB, pero la diferencia media sube a 11,4
sobre 255, que sí se ve. Por eso este script no aplica la conversion a ciegas:
mide la diferencia contra el original y **solo escribe si queda bajo
`--umbral`** (1,0 por defecto, medido en niveles de 0 a 255). Un logo que no
pasa el umbral se deja exactamente como estaba y se reporta.

Es idempotente: un PNG ya convertido a paleta no gana nada y se salta solo
(no hay perdida acumulativa por correrlo dos veces, pero igual se evita).
Se conserva el canal alfa, que es lo que hace que un logo se pueda poner
sobre cualquier fondo.

NO TOCA los .jpg de fotos/ — de eso se encargan optimizar_fotos.py (el
original) y generar_imagenes_web.py (los derivados que sirve el sitio).

Uso:
    python optimizar_logos.py              # muestra que haria
    python optimizar_logos.py --aplicar
    python optimizar_logos.py --umbral 0.5 --aplicar   # mas exigente
"""
import argparse
import io
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
LOGOS = RAIZ / "logos"
UMBRAL_DEFECTO = 1.0   # niveles de 0 a 255, promediados sobre los 4 canales


def diferencia_media(a, b):
    """Promedio de |a-b| por canal entre dos imagenes RGBA del mismo tamano."""
    pa, pb = a.convert("RGBA"), b.convert("RGBA")
    da, db = list(pa.getdata()), list(pb.getdata())
    paso = max(1, len(da) // 20000)          # una muestra basta y es mucho mas rapido
    da, db = da[::paso], db[::paso]
    total = sum(sum(abs(x - y) for x, y in zip(p, q)) / 4 for p, q in zip(da, db))
    return total / len(da)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--aplicar", action="store_true", help="escribe los cambios")
    ap.add_argument("--umbral", type=float, default=UMBRAL_DEFECTO,
                    help=f"diferencia media maxima aceptada, 0-255 (default {UMBRAL_DEFECTO})")
    args = ap.parse_args()

    try:
        from PIL import Image
    except ImportError:
        sys.exit("Falta Pillow: pip install Pillow")

    if not LOGOS.exists():
        sys.exit("No existe logos/")

    convertidos = saltados = 0
    antes_total = despues_total = 0

    for ruta in sorted(LOGOS.rglob("*.png")):
        antes = ruta.stat().st_size
        with Image.open(ruta) as im:
            if im.mode == "P":                        # ya tiene paleta
                saltados += 1
                antes_total += antes
                despues_total += antes
                continue
            im = im.convert("RGBA")
            q = im.quantize(colors=256, method=Image.FASTOCTREE, dither=Image.FLOYDSTEINBERG)
            buf = io.BytesIO()
            q.save(buf, "PNG", optimize=True)
            despues = buf.tell()
            dif = diferencia_media(im, q)

        rel = ruta.relative_to(RAIZ).as_posix()
        antes_total += antes
        if dif > args.umbral:
            print(f"  SE DEJA IGUAL  {rel}: {antes//1024} KB -> seria {despues//1024} KB, "
                  f"pero la diferencia es {dif:.2f} (umbral {args.umbral})")
            saltados += 1
            despues_total += antes
            continue
        if despues >= antes:
            saltados += 1
            despues_total += antes
            continue

        print(f"  {'convertido' if args.aplicar else 'a convertir'}  {rel}: "
              f"{antes//1024} KB -> {despues//1024} KB   (diferencia {dif:.2f}, invisible)")
        convertidos += 1
        despues_total += despues
        if args.aplicar:
            ruta.write_bytes(buf.getvalue())

    print(f"\n{convertidos} logo(s) {'convertidos' if args.aplicar else 'por convertir'}, "
          f"{saltados} sin tocar.")
    print(f"logos/: {antes_total//1024} KB -> {despues_total//1024} KB"
          + ("" if args.aplicar else "  (estimado; corre con --aplicar)"))


if __name__ == "__main__":
    main()
