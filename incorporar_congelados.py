"""
incorporar_congelados.py -- Reinserta en datos/torneo.json a los equipos que el
pipeline oficial (Bases de Evaluacion, repo de Agustin) elimino del corte, pero
que Francisco decidio mantener EN ESPERA en el ranking publico de fig-web hasta
nuevo aviso (decision 2026-08-23, ver CLAUDE.md).

Que hace exactamente
---------------------
Los equipos congelados viven en datos/equipos_congelados.json con sus 5 metricas
crudas FIJAS en el ultimo corte real que jugaron (IR, Ret. Exceso, Sharpe, VaR95,
MDD). Ese dato no cambia nunca mas -- no vuelven a operar.

Su PUNTAJE si cambia semana a semana, porque el motor de scoring oficial
(src/scoring.py del repo torneo-bloomberg-oficial) no es una formula fija: cada
metrica se puntua por PERCENTIL CONTINUO entre el minimo y el maximo de TODOS los
equipos activos ese corte (Pts = (valor-MIN)/(MAX-MIN) * peso). Este script
reproduce esa misma formula (pesos y pisos verificados contra scoring.py,
2026-08-23) sobre el pool combinado (equipos reales del corte + los congelados),
así que el puntaje de un congelado -- y de paso el de todos los demas, si algun
congelado pasa a sostener un minimo o maximo -- se recalcula con datos frescos
cada vez que se corre.

Cuando correrlo
----------------
SIEMPRE despues de generar_torneo.py para el corte de la semana, nunca antes:

    python generar_torneo.py --excel <Excel del corte> --semana N --corte "..."
    python incorporar_congelados.py

Reporta por consola (y deja registro en ALERTAS_CONGELADOS.md) si algun equipo
congelado paso a sostener el minimo o el maximo de alguna metrica esa semana
("genera ruido"), y que tanto se movieron por eso los equipos reales.

Para sacar a un equipo de la espera (reincorporado de verdad al pipeline oficial,
o retirado en definitiva): borrarlo de datos/equipos_congelados.json y correr
este script de nuevo -- no hace falta tocar torneo.json a mano.
"""

from __future__ import annotations
import json
import pathlib
from datetime import datetime

RUTA_TORNEO = pathlib.Path("datos/torneo.json")
RUTA_CONGELADOS = pathlib.Path("datos/equipos_congelados.json")
RUTA_ALERTAS = pathlib.Path("ALERTAS_CONGELADOS.md")

# Pesos y reglas de piso -- EXACTOS a src/scoring.py de torneo-bloomberg-oficial.
# (columna metricas, peso, aplica piso si valor < 0 -> 0 pts)
METRICAS = [
    ("ir", 30, True),
    ("exc", 25, True),
    ("sharpe", 15, True),
    ("var95", 15, False),
    ("mdd", 15, False),
]

NOMBRE_METRICA = {
    "ir": "Information Ratio",
    "exc": "Ret. Exceso",
    "sharpe": "Sharpe",
    "var95": "VaR 95%",
    "mdd": "MDD",
}


def percentil_continuo(equipos: list[dict], clave: str, peso: float, piso_negativo: bool) -> dict[str, float]:
    """Replica _continuous_percentile de scoring.py: Pts=(v-MIN)/(MAX-MIN)*peso."""
    valores = {e["id"]: e["metricas"][clave] for e in equipos}
    lo, hi = min(valores.values()), max(valores.values())
    pts = {}
    for eid, v in valores.items():
        p = peso if hi == lo else (v - lo) / (hi - lo) * peso
        if piso_negativo and v < 0:
            p = 0.0
        pts[eid] = round(p, 6)
    return pts, lo, hi


def recalcular(equipos_reales: list[dict], equipos_congelados: list[dict]):
    pool = equipos_reales + equipos_congelados
    puntos_por_metrica = {}
    rangos = {}
    for clave, peso, piso in METRICAS:
        pts, lo, hi = percentil_continuo(pool, clave, peso, piso)
        puntos_por_metrica[clave] = pts
        rangos[clave] = (lo, hi)

    resultados = []
    for e in pool:
        detalle = {clave: puntos_por_metrica[clave][e["id"]] for clave, _, _ in METRICAS}
        total = round(sum(detalle.values()), 6)
        resultados.append({"id": e["id"], "puntosDetalle": detalle, "puntos": round(total, 2)})

    resultados.sort(key=lambda r: -r["puntos"])
    for i, r in enumerate(resultados, start=1):
        r["posicion"] = i

    return {r["id"]: r for r in resultados}, rangos


def detectar_ruido(equipos_congelados: list[dict], rangos: dict, rangos_sin_congelados: dict) -> list[str]:
    avisos = []
    ids_congelados = {e["id"] for e in equipos_congelados}
    for clave, _, _ in METRICAS:
        lo, hi = rangos[clave]
        lo_sin, hi_sin = rangos_sin_congelados[clave]
        # Quien sostiene cada extremo con los congelados adentro
        for e in equipos_congelados:
            v = e["metricas"][clave]
            if v == lo or v == hi:
                extremo = "el MINIMO" if v == lo else "el MAXIMO"
                rango_con = hi - lo
                rango_sin = hi_sin - lo_sin
                cambio = (rango_con - rango_sin) / rango_sin * 100 if rango_sin else 0.0
                avisos.append(
                    f"- **{e['nombre']}** (congelado) sostiene {extremo} de "
                    f"{NOMBRE_METRICA[clave]} ({v}). El rango de esa metrica queda "
                    f"{cambio:+.1f}% distinto de lo que seria sin los congelados "
                    f"-- afecta el puntaje de TODOS los equipos en esa metrica, no solo el suyo."
                )
    return avisos


def main():
    torneo = json.loads(RUTA_TORNEO.read_text(encoding="utf-8"))
    congelados_data = json.loads(RUTA_CONGELADOS.read_text(encoding="utf-8"))

    equipos_reales = torneo["equipos"]
    equipos_congelados = congelados_data["equipos"]
    semana = torneo["semana"]
    corte = torneo["corte"]

    ids_reales = {e["id"] for e in equipos_reales}
    ids_congelados = {e["id"] for e in equipos_congelados}
    if ids_reales & ids_congelados:
        raise SystemExit(
            f"ERROR: {ids_reales & ids_congelados} aparece en torneo.json Y en "
            f"equipos_congelados.json -- probablemente ya se corrio este script, "
            f"o el equipo volvio a competir de verdad. Revisar a mano antes de seguir."
        )

    posiciones_previas = {}
    for e in equipos_reales:
        if e.get("historial"):
            anteriores = [h for h in e["historial"] if h["semana"] < semana]
            if anteriores:
                posiciones_previas[e["id"]] = anteriores[-1]["posicion"]
    for e in equipos_congelados:
        anteriores = [h for h in e.get("historial_previo", []) if h["semana"] < semana]
        if anteriores:
            posiciones_previas[e["id"]] = anteriores[-1]["posicion"]

    puntos_previos_reales = {e["id"]: e["puntos"] for e in equipos_reales}

    recalculo, rangos_con = recalcular(equipos_reales, equipos_congelados)
    _, rangos_sin = recalcular(equipos_reales, [])

    # --- actualizar equipos reales ---
    nuevos_equipos = []
    for e in equipos_reales:
        r = recalculo[e["id"]]
        e["puntos"] = r["puntos"]
        e["posicion"] = r["posicion"]
        e["puntosDetalle"] = r["puntosDetalle"]
        prev = posiciones_previas.get(e["id"])
        e["delta"] = (prev - r["posicion"]) if prev is not None else 0
        if e.get("historial") and e["historial"][-1]["semana"] == semana:
            e["historial"][-1]["puntos"] = r["puntos"]
            e["historial"][-1]["posicion"] = r["posicion"]
        nuevos_equipos.append(e)

    # --- insertar equipos congelados ---
    for e in equipos_congelados:
        r = recalculo[e["id"]]
        prev = posiciones_previas.get(e["id"])
        nuevo = {
            "id": e["id"],
            "nombre": e["nombre"],
            "posicion": r["posicion"],
            "puntos": r["puntos"],
            "retRel": e["retRel"],
            "delta": (prev - r["posicion"]) if prev is not None else 0,
            "metricas": e["metricas"],
            "puntosDetalle": r["puntosDetalle"],
            "miembros": e["miembros"],
            "congelado": True,
            "congelado_desde_semana": e["congelado_desde_semana"],
            "historial": list(e.get("historial_previo", [])) + [{
                "semana": semana,
                "puntos": r["puntos"],
                "posicion": r["posicion"],
                "ret": e["retRel"],
                **e["metricas"],
            }],
        }
        nuevos_equipos.append(nuevo)

    nuevos_equipos.sort(key=lambda x: x["posicion"])
    torneo["equipos"] = nuevos_equipos
    RUTA_TORNEO.write_text(json.dumps(torneo, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- reporte ---
    avisos_ruido = detectar_ruido(equipos_congelados, rangos_con, rangos_sin)

    movidos = []
    for eid, pts_antes in puntos_previos_reales.items():
        pts_despues = recalculo[eid]["puntos"]
        diff = round(pts_despues - pts_antes, 2)
        if abs(diff) >= 0.05:
            nombre = next(e["nombre"] for e in equipos_reales if e["id"] == eid)
            movidos.append((nombre, pts_antes, pts_despues, diff))
    movidos.sort(key=lambda x: -abs(x[3]))

    lineas = []
    lineas.append(f"## Semana {semana} · {corte}\n")
    lineas.append(f"{len(equipos_congelados)} equipos en espera reinsertados: "
                   f"{', '.join(e['nombre'] for e in equipos_congelados)}.\n")
    if avisos_ruido:
        lineas.append("**Ruido detectado -- un congelado sostiene un extremo:**\n")
        lineas.extend(a + "\n" for a in avisos_ruido)
    else:
        lineas.append("Sin ruido: ningun congelado sostiene el minimo ni el maximo de "
                       "ninguna metrica esta semana. El puntaje de los equipos reales "
                       "no se vio afectado por su presencia.\n")
    if movidos:
        lineas.append(f"\n**Equipos reales cuyo puntaje se movio >= 0.05 pts por la "
                       f"presencia de los congelados ({len(movidos)}):**\n")
        for nombre, antes, despues, diff in movidos[:15]:
            signo = "+" if diff > 0 else ""
            lineas.append(f"- {nombre}: {antes:.2f} -> {despues:.2f} ({signo}{diff:.2f})\n")
        if len(movidos) > 15:
            lineas.append(f"- ...y {len(movidos)-15} equipos mas con cambios menores.\n")
    else:
        lineas.append("\nNingun equipo real cambio de puntaje por la presencia de los congelados.\n")
    lineas.append("\n---\n\n")

    reporte = "".join(lineas)
    existente = RUTA_ALERTAS.read_text(encoding="utf-8") if RUTA_ALERTAS.exists() else (
        "# Alertas -- equipos en espera (congelados)\n\n"
        "Registro semanal de `incorporar_congelados.py`: si algun equipo eliminado "
        "que Francisco mantiene en espera empieza a perturbar el puntaje de los "
        "demas (sostener un minimo/maximo de metrica), queda anotado aca.\n\n"
    )
    RUTA_ALERTAS.write_text(existente + reporte, encoding="utf-8")

    print(reporte)
    print(f"OK: datos/torneo.json actualizado -- {len(nuevos_equipos)} equipos "
          f"({len(equipos_reales)} activos + {len(equipos_congelados)} en espera).")


if __name__ == "__main__":
    main()
