#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_ics.py — datos/eventos.json → eventos/fig.ics

Genera el calendario suscribible/descargable de FIG (formato iCalendar,
RFC 5545) a partir de la bitácora de eventos. Cada evento del JSON se
convierte en un VEVENT de día completo usando su campo `fecha`.

Correr SIEMPRE después de editar datos/eventos.json:

    python3 generar_ics.py

La página eventos/index.html enlaza a eventos/fig.ics ("Calendario FIG").
Una vez desplegado en GitHub Pages, la URL pública del .ics también sirve
para SUSCRIBIRSE (Google Calendar → "Agregar por URL"), y se actualiza
sola con cada regeneración + push.

Sin dependencias externas: solo biblioteca estándar.
"""
import json
import os
import sys
from datetime import datetime, timedelta

RAIZ = os.path.dirname(os.path.abspath(__file__))
ENTRADA = os.path.join(RAIZ, "datos", "eventos.json")
SALIDA = os.path.join(RAIZ, "eventos", "fig.ics")


def escapar(texto):
    """Escapa texto según RFC 5545 (comas, puntos y coma, saltos)."""
    return (str(texto or "")
            .replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n"))


def plegar(linea):
    """Pliega líneas a máx 75 octetos (RFC 5545 §3.1), continuación con espacio."""
    out = []
    datos = linea.encode("utf-8")
    while len(datos) > 74:
        corte = 74
        # no partir en medio de un carácter UTF-8 multibyte
        while corte > 0 and (datos[corte] & 0xC0) == 0x80:
            corte -= 1
        out.append(datos[:corte].decode("utf-8"))
        datos = b" " + datos[corte:]
    out.append(datos.decode("utf-8"))
    return "\r\n".join(out)


def main():
    with open(ENTRADA, encoding="utf-8") as f:
        eventos = json.load(f).get("eventos", [])

    ahora = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lineas = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//FEN Investment Group//Bitacora FIG//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:FEN Investment Group",
        "X-WR-CALDESC:Actividades de FEN Investment Group — torneos\\, visitas\\, "
        "charlas y comunidad. Universidad de Chile.",
        "X-WR-TIMEZONE:America/Santiago",
    ]

    n = 0
    for ev in eventos:
        fecha = ev.get("fecha")
        if not fecha:
            continue
        try:
            d0 = datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            print("  ⚠ fecha inválida en %s: %r — omitido" % (ev.get("id"), fecha))
            continue
        d1 = d0 + timedelta(days=1)
        desc = ev.get("resumen", "")
        if ev.get("fechaTexto"):
            desc = desc + ("\n" if desc else "") + "Fecha: " + ev["fechaTexto"]
        lineas += [
            "BEGIN:VEVENT",
            plegar("UID:%s@feninvestmentgroup" % ev.get("id", "evento-%d" % n)),
            "DTSTAMP:" + ahora,
            "DTSTART;VALUE=DATE:" + d0.strftime("%Y%m%d"),
            "DTEND;VALUE=DATE:" + d1.strftime("%Y%m%d"),
            plegar("SUMMARY:" + escapar(ev.get("titulo", "Evento FIG"))),
            plegar("LOCATION:" + escapar(ev.get("lugar", ""))),
            plegar("DESCRIPTION:" + escapar(desc)),
            plegar("CATEGORIES:" + escapar((ev.get("tipo") or "evento").upper())),
            "END:VEVENT",
        ]
        n += 1

    lineas.append("END:VCALENDAR")
    with open(SALIDA, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lineas) + "\r\n")
    print("✅ %s — %d eventos" % (os.path.relpath(SALIDA, RAIZ), n))


if __name__ == "__main__":
    sys.exit(main())
