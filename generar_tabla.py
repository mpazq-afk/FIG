"""
generar_tabla.py -- Deriva los dos archivos livianos del torneo desde
datos/torneo.json: datos/torneo-tabla.json y datos/torneo-portada.json.

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

Los dos llevan el mismo `_fuenteSha1`, asi que un solo chequeo los cubre.

`acwi` se mantiene: son 304 bytes y evita un caso raro de grafico sin benchmark.

El segundo derivado: datos/torneo-portada.json
-----------------------------------------------
La PORTADA no muestra el ranking: solo la cinta del pie (top 5) y el grafico
del hero (la trayectoria promedio del top 5 contra el ACWI). Para eso bajaba
los 205 KB del archivo completo -- 54 equipos con sus metricas, su detalle de
puntaje, sus integrantes y las 9 cifras por semana de cada uno -- y usaba dos
campos por equipo.

    datos/torneo.json            204,7 KB en crudo -> 23,4 KB comprimido
    datos/torneo-portada.json      ~3 KB en crudo  ->  ~1 KB comprimido

Se queda con los TOP_PORTADA primeros y, de cada uno, solo lo que la portada
lee de verdad: posicion, nombre, puntos, retRel, delta y un historial podado a
{semana, ret}. El campo `topPortada` dice cuantos trae, para que la pagina
pueda darse cuenta sola si le quedo corto (ver HERO_TOP en index.html) y
volver al archivo completo en vez de dibujar un grafico incompleto.

Cuando correrlo
----------------
Despues de CUALQUIER cosa que reescriba datos/torneo.json:

    python generar_torneo.py --excel <Excel del corte> --semana N --corte "..."
    python incorporar_congelados.py
    python generar_tabla.py            <-- siempre al final

Si se olvida, no se rompe nada: la pagina compara el corte del derivado con el
del completo y, si no calzan, repinta todo con el completo; y la portada, si no
encuentra su derivado o lo ve corto, pide el archivo entero como siempre. Pero
conviene no depender de eso -- por eso verificar_sitio.py falla si los derivados
estan viejos, y `python verificar_sitio.py --arreglar` los regenera.
"""

from __future__ import annotations
import hashlib
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
ENTRADA = RAIZ / "datos" / "torneo.json"
SALIDA = RAIZ / "datos" / "torneo-tabla.json"
SALIDA_PORTADA = RAIZ / "datos" / "torneo-portada.json"

# Cuantos equipos lleva el derivado de la portada. Hoy la cinta usa 5 y el
# grafico del hero tambien (HERO_TOP en index.html); van 10 para dejar aire
# sin que cueste nada. Si alguna vez HERO_TOP sube de aca, verificar_sitio.py
# lo avisa antes de que la portada dibuje un promedio con menos equipos de los
# que dice el rotulo.
TOP_PORTADA = 10


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


def derivar_portada(completo: dict, sha1_fuente: str) -> dict:
    """El top de la tabla con lo justo que pinta la portada.

    Poda dos veces: se queda con los TOP_PORTADA primeros, y de cada uno con
    los cinco campos que la cinta y el grafico leen. El historial tambien se
    poda -- de las nueve cifras por semana el hero usa `ret` y nada mas.
    """
    orden = sorted(completo.get("equipos", []),
                   key=lambda e: e.get("posicion") or 9999)
    equipos = []
    for eq in orden[:TOP_PORTADA]:
        hist = [{"semana": h["semana"], "ret": h["ret"]}
                for h in (eq.get("historial") or [])
                if h.get("semana") is not None and h.get("ret") is not None]
        equipos.append({
            "posicion": eq.get("posicion"),
            "nombre": eq.get("nombre"),
            "puntos": eq.get("puntos"),
            "retRel": eq.get("retRel"),
            "delta": eq.get("delta"),
            "historial": hist,
        })

    return {
        "semana": completo.get("semana"),
        "corte": completo.get("corte"),
        "acwi": completo.get("acwi", []),
        "equipos": equipos,
        "topPortada": len(equipos),
        "_derivado": ("generado por generar_tabla.py desde datos/torneo.json "
                      "- no editar a mano"),
        "_fuenteSha1": sha1_fuente,
    }


def esta_al_dia() -> bool:
    """True si LOS DOS derivados existen y corresponden al torneo.json actual."""
    if not ENTRADA.exists():
        return False
    sha = sha1_de(ENTRADA)
    for salida in (SALIDA, SALIDA_PORTADA):
        if not salida.exists():
            return False
        try:
            actual = json.loads(salida.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        if actual.get("_fuenteSha1") != sha:
            return False
    return True


def main() -> int:
    if not ENTRADA.exists():
        print(f"No existe {ENTRADA.relative_to(RAIZ)} -- nada que derivar.")
        print("La pagina funciona igual: sin el derivado carga el archivo completo.")
        return 0

    completo = json.loads(ENTRADA.read_text(encoding="utf-8"))
    sha = sha1_de(ENTRADA)
    tabla = derivar(completo, sha)
    portada = derivar_portada(completo, sha)

    # separadores compactos: los derivados no se leen a mano, se sirven
    for salida, dato in ((SALIDA, tabla), (SALIDA_PORTADA, portada)):
        salida.write_text(
            json.dumps(dato, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

    kb_in = ENTRADA.stat().st_size / 1024
    kb_tabla = SALIDA.stat().st_size / 1024
    kb_port = SALIDA_PORTADA.stat().st_size / 1024
    print(f"OK: {SALIDA.relative_to(RAIZ)} escrito.")
    print(f"  {len(tabla['equipos'])} equipos - {tabla['semanasPublicadas']} semanas publicadas")
    print(f"  {kb_in:.1f} KB -> {kb_tabla:.1f} KB en crudo ({100 - kb_tabla / kb_in * 100:.0f}% menos)")
    print(f"OK: {SALIDA_PORTADA.relative_to(RAIZ)} escrito.")
    print(f"  top {portada['topPortada']} - lo unico que pinta la portada")
    print(f"  {kb_in:.1f} KB -> {kb_port:.1f} KB en crudo ({100 - kb_port / kb_in * 100:.0f}% menos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
