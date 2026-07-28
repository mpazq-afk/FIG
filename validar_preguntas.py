#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validar_preguntas.py — barrera de calidad del banco de preguntas del Desafío FIG.

OBLIGATORIO correrlo (y que salga "TODO OK") antes de commitear cualquier
cambio en datos/preguntas/. Es lo que permite que cualquier modelo (Haiku,
Sonnet…) agregue preguntas en volumen sin poder romper el juego: si el
validador pasa, la página las carga sin problemas.

Uso:
    python3 validar_preguntas.py            # valida índice + todos los shards
    python3 validar_preguntas.py --stats    # además imprime conteos por tema/ramo/dificultad

Reglas que verifica (esquema en datos/preguntas/LEEME.md):
- index.json: claves version/temas/ramos/archivos; ids de tema/ramo únicos y en kebab-case.
- Cada shard listado existe, es JSON válido y es un array de preguntas.
- Por pregunta: campos obligatorios (id, tema, ramo, dificultad, pregunta,
  alternativas, correcta, explicacion, fuente); id único en TODO el banco;
  tema/ramo declarados en el índice; dificultad 1-3; 3 a 5 alternativas no
  vacías y sin duplicados; correcta es índice válido; pregunta 15-300
  caracteres; explicacion 60-500 caracteres (debe ENSEÑAR, no solo repetir
  la respuesta); alternativas de largo razonable (2-160).
- Avisos (no bloquean): shard con más de 200 preguntas o más de 150 KB;
  texto de pregunta duplicado entre preguntas distintas.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent / "datos" / "preguntas"
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errores, avisos = [], []


def err(msg):
    errores.append(msg)


def warn(msg):
    avisos.append(msg)


def validar():
    idx_path = BASE / "index.json"
    if not idx_path.exists():
        err(f"No existe {idx_path}")
        return

    try:
        idx = json.loads(idx_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"index.json no es JSON válido: {e}")
        return

    for clave in ("version", "temas", "ramos", "archivos"):
        if clave not in idx:
            err(f"index.json: falta la clave '{clave}'")
    if errores:
        return

    temas, ramos = {}, {}
    for grupo, destino in (("temas", temas), ("ramos", ramos)):
        for item in idx[grupo]:
            iid = item.get("id", "")
            if not KEBAB.match(iid):
                err(f"index.json {grupo}: id '{iid}' no es kebab-case")
            if iid in destino:
                err(f"index.json {grupo}: id duplicado '{iid}'")
            if not item.get("nombre"):
                err(f"index.json {grupo} '{iid}': falta 'nombre'")
            destino[iid] = item.get("nombre")

    ids_vistos = {}
    textos = Counter()
    stats = {"tema": Counter(), "ramo": Counter(), "dif": Counter(), "total": 0}

    for archivo in idx["archivos"]:
        ruta = BASE / archivo
        if not ruta.exists():
            err(f"Shard listado en el índice pero inexistente: {archivo}")
            continue
        if ruta.stat().st_size > 150 * 1024:
            warn(f"{archivo}: pesa {ruta.stat().st_size // 1024} KB (>150 KB) — dividirlo en dos shards")
        try:
            shard = json.loads(ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(f"{archivo}: JSON inválido: {e}")
            continue
        if not isinstance(shard, list):
            err(f"{archivo}: debe ser un array de preguntas")
            continue
        if len(shard) > 200:
            warn(f"{archivo}: {len(shard)} preguntas (>200) — dividirlo en dos shards")

        for i, q in enumerate(shard):
            ref = f"{archivo}[{i}]"
            if not isinstance(q, dict):
                err(f"{ref}: no es un objeto")
                continue
            faltan = [c for c in ("id", "tema", "ramo", "dificultad", "pregunta",
                                  "alternativas", "correcta", "explicacion", "fuente") if c not in q]
            if faltan:
                err(f"{ref}: faltan campos {faltan}")
                continue
            qid = q["id"]
            ref = f"{archivo}:{qid}"
            if qid in ids_vistos:
                err(f"{ref}: id duplicado (ya usado en {ids_vistos[qid]})")
            ids_vistos[qid] = archivo
            if q["tema"] not in temas:
                err(f"{ref}: tema '{q['tema']}' no está declarado en index.json")
            if q["ramo"] not in ramos:
                err(f"{ref}: ramo '{q['ramo']}' no está declarado en index.json")
            if q["dificultad"] not in (1, 2, 3):
                err(f"{ref}: dificultad debe ser 1, 2 o 3")
            preg = str(q["pregunta"]).strip()
            if not 15 <= len(preg) <= 300:
                err(f"{ref}: pregunta de {len(preg)} caracteres (rango 15-300)")
            alts = q["alternativas"]
            if not isinstance(alts, list) or not 3 <= len(alts) <= 5:
                err(f"{ref}: deben ser 3 a 5 alternativas")
            else:
                limpias = [str(a).strip() for a in alts]
                if any(not a for a in limpias):
                    err(f"{ref}: alternativa vacía")
                if len(set(limpias)) != len(limpias):
                    err(f"{ref}: alternativas duplicadas")
                if any(len(a) > 160 or len(a) < 2 for a in limpias):
                    err(f"{ref}: alternativa fuera de rango de largo (2-160)")
                if not (isinstance(q["correcta"], int) and 0 <= q["correcta"] < len(alts)):
                    err(f"{ref}: 'correcta' debe ser un índice válido de alternativas")
            expl = str(q["explicacion"]).strip()
            if not 60 <= len(expl) <= 500:
                err(f"{ref}: explicacion de {len(expl)} caracteres (rango 60-500 — debe enseñar el porqué)")
            textos[preg.lower()] += 1
            stats["tema"][q["tema"]] += 1
            stats["ramo"][q["ramo"]] += 1
            stats["dif"][q.get("dificultad")] += 1
            stats["total"] += 1

    for texto, n in textos.items():
        if n > 1:
            warn(f"Pregunta repetida {n} veces: \"{texto[:70]}…\"")

    return stats


def main():
    stats = validar()
    for a in avisos:
        print(f"  AVISO: {a}")
    if errores:
        print(f"\n{len(errores)} ERROR(ES):")
        for e in errores:
            print(f"  ✗ {e}")
        sys.exit(1)
    print(f"TODO OK · {stats['total']} preguntas válidas")
    if "--stats" in sys.argv:
        print("\nPor tema:")
        for t, n in stats["tema"].most_common():
            print(f"  {t}: {n}")
        print("Por ramo:")
        for r, n in stats["ramo"].most_common():
            print(f"  {r}: {n}")
        print("Por dificultad:")
        for d in (1, 2, 3):
            print(f"  {d}: {stats['dif'].get(d, 0)}")


if __name__ == "__main__":
    main()
