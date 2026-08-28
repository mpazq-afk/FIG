"""
generar_tabla.py -- Deriva datos/torneo-tabla.json desde datos/torneo.json.

Por que existe
--------------
torneo/index.html pinta la tabla del ranking apenas puede, pero el archivo que
produce el pipeline trae ademas el HISTORIAL semana a semana de cada equipo, que
solo hace falta cuando alguien abre una ficha, el comparador o el replay.
Medido sobre el corte de la semana 15 (54 equipos, 11 semanas publicadas):

    datos/torneo.json          105,9 KB en crudo -> 27,7 KB comprimido
    datos/torneo-tabla.json     27,0 KB en crudo ->  7,1 KB comprimido

O sea, el historial es el 75% de lo que hoy se baja SIEMPRE para ver la tabla.
Este script escribe la version sin historial; la pagina pide esa primero y va a
buscar el historial aparte, de fondo o cuando se necesita.

Que cambia respecto del original
---------------------------------
  - se saca `historial` de cada equipo (lo unico que se saca);
  - se agrega `semanasPublicadas`, que la pagina usa para decidir si muestra el
    boton del replay sin tener que mirar el historial;
  - se agregan `_derivado` y `_fuenteSha1`, este ultimo para que
    verificar_sitio.py pueda detectar si el derivado quedo atras.

`acwi` se mantiene: son 304 bytes y evita un caso raro de grafico sin benchmark.

Cuando correrlo
----------------
Despues de CUALQUIER cosa que reescriba datos/torneo.json:

    python generar_torneo.py --excel <Excel del corte> --semana N --corte "..."
    python incorporar_congelados.py
    python generar_tabla.py            <-- siempre al final

Si se olvida, no se rompe nada: la pagina compara el corte del derivado con el
del completo y, si no calzan, repinta todo con el completo. Pero conviene no
depender de eso -- por eso verificar_sitio.py falla si el derivado esta viejo, y
`python verificar_sitio.py --arreglar` lo regenera.
"""

from __future__ import annotations
import hashlib
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
ENTRADA = RAIZ / "datos" / "torneo.json"
SALIDA = RAIZ / "datos" / "torneo-tabla.json"


def sha1_de(ruta: pathlib.Path) -> str:
    return hashlib.sha1(ruta.read_bytes()).hexdigest()


def derivar(completo: dict, sha1_fuente: str) -> dict:
    """Devuelve el mismo torneo sin el historial de los equipos."""
    semanas = set()
    equipos = []
    for eq in completo.get("equipos", []):
        for h in eq.get("historial", []) or []:
            if h.get("semana") is not None:
                semanas.add(h["semana"])
        equipos.append({k: v for k, v in eq.items() if k != "historial"})

    tabla = {k: v for k, v in completo.items() if k != "equipos"}
    tabla["equipos"] = equipos
    tabla["semanasPublicadas"] = len(semanas)
    tabla["_derivado"] = ("generado por generar_tabla.py desde datos/torneo.json "
                          "- no editar a mano")
    tabla["_fuenteSha1"] = sha1_fuente
    return tabla


def esta_al_dia() -> bool:
    """True si el derivado existe y corresponde al torneo.json actual."""
    if not SALIDA.exists() or not ENTRADA.exists():
        return False
    try:
        actual = json.loads(SALIDA.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return actual.get("_fuenteSha1") == sha1_de(ENTRADA)


def main() -> int:
    if not ENTRADA.exists():
        print(f"No existe {ENTRADA.relative_to(RAIZ)} -- nada que derivar.")
        print("La pagina funciona igual: sin el derivado carga el archivo completo.")
        return 0

    completo = json.loads(ENTRADA.read_text(encoding="utf-8"))
    tabla = derivar(completo, sha1_de(ENTRADA))

    # separadores compactos: el derivado no se lee a mano, se sirve
    SALIDA.write_text(
        json.dumps(tabla, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    kb_in = ENTRADA.stat().st_size / 1024
    kb_out = SALIDA.stat().st_size / 1024
    print(f"OK: {SALIDA.relative_to(RAIZ)} escrito.")
    print(f"  {len(tabla['equipos'])} equipos - {tabla['semanasPublicadas']} semanas publicadas")
    print(f"  {kb_in:.1f} KB -> {kb_out:.1f} KB en crudo ({100 - kb_out / kb_in * 100:.0f}% menos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
