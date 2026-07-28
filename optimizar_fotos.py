#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
optimizar_fotos.py — comprime automáticamente las fotos de fotos/ antes de subirlas.

Aplica la misma regla que MAPA_CONTENIDO_FIG.html le pide a Francisco a mano:
máximo 1600-2000px de lado largo, JPG calidad 78%. Corre sobre TODO lo que
haya en fotos/eventos/*/ y fotos/fiw/ — es idempotente (si una foto ya está
dentro del límite, la deja intacta) así que se puede correr las veces que
sea sin degradar calidad de más.

Uso:
    python3 optimizar_fotos.py              # optimiza todo fotos/
    python3 optimizar_fotos.py --dry-run     # solo muestra qué haría, no escribe nada
    python3 optimizar_fotos.py --max 1800 --calidad 80   # ajustar parámetros

Requiere: Pillow (pip install Pillow).

Se recomienda correrlo SIEMPRE antes de un commit que agregue fotos nuevas
(o dejar que el hook de pre-commit lo haga solo, ver sección al final del
archivo para instalarlo).
"""
import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CARPETAS = [RAIZ / "fotos" / "eventos", RAIZ / "fotos" / "fiw"]
EXTENSIONES = (".jpg", ".jpeg")
MAX_LADO_DEFECTO = 2000
CALIDAD_DEFECTO = 78


def encontrar_fotos():
    fotos = []
    for base in CARPETAS:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in EXTENSIONES:
                fotos.append(p)
    return sorted(fotos)


def optimizar(ruta, max_lado, calidad, dry_run):
    try:
        from PIL import Image, ImageOps
    except ImportError:
        sys.exit("Falta Pillow: pip install Pillow")

    antes = ruta.stat().st_size
    with Image.open(ruta) as im:
        im = ImageOps.exif_transpose(im)  # respeta la orientación de fotos de celular
        if im.mode != "RGB":
            im = im.convert("RGB")
        cambio_tamano = max(im.size) > max_lado
        if cambio_tamano:
            im.thumbnail((max_lado, max_lado), Image.LANCZOS)
        if dry_run:
            return antes, antes, cambio_tamano
        im.save(ruta, "JPEG", quality=calidad, optimize=True)
    despues = ruta.stat().st_size
    return antes, despues, cambio_tamano


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--max", type=int, default=MAX_LADO_DEFECTO, help=f"lado largo máximo en px (default {MAX_LADO_DEFECTO})")
    ap.add_argument("--calidad", type=int, default=CALIDAD_DEFECTO, help=f"calidad JPEG 1-95 (default {CALIDAD_DEFECTO})")
    ap.add_argument("--dry-run", action="store_true", help="mostrar qué haría sin modificar archivos")
    args = ap.parse_args()

    fotos = encontrar_fotos()
    if not fotos:
        print("No hay fotos en fotos/eventos/*/ ni fotos/fiw/ todavía.")
        return

    total_antes = total_despues = 0
    tocadas = 0
    for ruta in fotos:
        antes, despues, cambio = optimizar(ruta, args.max, args.calidad, args.dry_run)
        total_antes += antes
        total_despues += despues if not args.dry_run else antes
        rel = ruta.relative_to(RAIZ)
        if antes > 500 * 1024 or cambio:  # solo mostrar las que valen la pena reportar
            marca = "SE COMPRIMIRÍA" if args.dry_run else "comprimida"
            despues_kb = "?" if args.dry_run else f"{despues // 1024}"
            print(f"  {rel}: {antes // 1024} KB -> {despues_kb} KB ({marca})")
            tocadas += 1

    print(f"\n{len(fotos)} fotos revisadas, {tocadas} {'a comprimir' if args.dry_run else 'comprimidas'}.")
    print(f"Total: {total_antes // 1024 // 1024} MB -> {total_despues // 1024 // 1024} MB"
          + (" (estimado, corre sin --dry-run para aplicar)" if args.dry_run else ""))


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------
# Hook de pre-commit opcional (para que esto corra solo, sin que nadie tenga
# que acordarse): crear .git/hooks/pre-commit con este contenido y darle
# permiso de ejecución (chmod +x):
#
#   #!/bin/sh
#   python3 optimizar_fotos.py
#   git add fotos/
#
# No se instala automáticamente porque .git/hooks/ no se versiona en el
# repo — hay que crearlo una vez por clon local. Documentado también en
# HOJA_DE_RUTA_FIG.md.
# ---------------------------------------------------------------------------
