# -*- coding: utf-8 -*-
"""
generar_informe_en.py -- Escribe en/informe/index.html desde informe/index.html.

Por que un script y no un archivo a mano
-----------------------------------------
El informe son ~1.200 lineas con cinco graficos SVG dibujados a mano. Mantener
dos copias en paralelo es exactamente la trampa que este repo ya conoce: el
espejo se desincronizo sin que nadie lo notara, y un cambio en `index.html`
llego a produccion sin su CSS ni su markup por portarlo a mano. Con dos copias
del informe, el primer arreglo del grafico que alguien haga en espanol dejaria
la version en ingles mostrando otra cosa.

Aca la fuente de verdad es UNA (`informe/index.html`) y la traduccion es una
tabla. Si cambia el informe, se vuelve a correr esto.

**El script falla si queda texto en espanol sin traducir.** Es el punto: sin
esa barrera, un parrafo nuevo en el informe se publicaria en espanol dentro de
la pagina en ingles y nadie se enteraria hasta que lo viera un partner.

Uso
----
    python generar_informe_en.py            # revisa y reporta, no escribe
    python generar_informe_en.py --aplicar

Cuando correrlo: **cada vez que se toca `informe/index.html`**. Si aparece
texto nuevo, el script lo lista y hay que agregarlo a TRADUCCIONES.
"""

from __future__ import annotations
import argparse
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
FUENTE = RAIZ / "informe" / "index.html"
DESTINO = RAIZ / "en" / "informe" / "index.html"

# --------------------------------------------------------------------------
# Rutas: el informe vive a un nivel de la raiz y su version en ingles a dos.
# `../index.html` es la EXCEPCION y no se toca: desde en/informe/ apunta a
# en/index.html, que es justo donde queremos mandar a quien lee en ingles.
RUTAS = [
    ("../datos/",   "../../datos/"),
    ("../fuentes/", "../../fuentes/"),
    ("../logos/",   "../../logos/"),
    ("../torneo/",  "../../torneo/"),
]

# --------------------------------------------------------------------------
# Cabecera. Se reemplaza entera para que el canonical, los hreflang y las og
# apunten a la version correcta; si no, las dos paginas competirian entre si
# en un buscador y al compartir el link saldria el titulo en espanol.
CABECERA = [
('<html lang="es" class="no-js">', '<html lang="en" class="no-js">'),
('<title>Informe del Torneo Portafolio 2026 — FIG</title>',
 '<title>Portfolio Tournament 2026 Report — FIG</title>'),
('<link rel="canonical" href="https://feninvestmentgroup.com/informe/">',
 '<link rel="canonical" href="https://feninvestmentgroup.com/en/informe/">\n'
 '<link rel="alternate" hreflang="es" href="https://feninvestmentgroup.com/informe/">\n'
 '<link rel="alternate" hreflang="en" href="https://feninvestmentgroup.com/en/informe/">\n'
 '<link rel="alternate" hreflang="x-default" href="https://feninvestmentgroup.com/informe/">'),
('<meta property="og:url" content="https://feninvestmentgroup.com/informe/">',
 '<meta property="og:url" content="https://feninvestmentgroup.com/en/informe/">'),
("Informe del Torneo Portafolio 2026 — FIG", "Portfolio Tournament 2026 Report — FIG"),
("Informe con datos y gráficos del Torneo Portafolio 2026 de FEN Investment Group: rendimiento frente al MSCI ACWI, distribución de resultados, riesgo y retorno, movilidad del ranking y composición del puntaje.",
 "A data report on FEN Investment Group's Portfolio Tournament 2026: performance against the MSCI ACWI, spread of results, risk taken and how much the ranking moves."),
("Qué muestran los datos del Torneo Portafolio 2026: rendimiento frente al mercado, dispersión de resultados, riesgo asumido y movilidad del ranking.",
 "What the Portfolio Tournament 2026 data shows: performance against the market, spread of results, risk taken and movement in the ranking."),
("Datos y gráficos del Torneo Portafolio 2026 de FEN Investment Group.",
 "Data and charts from FEN Investment Group's Portfolio Tournament 2026."),
]

# --------------------------------------------------------------------------
# Texto de cara al usuario. Se aplica de la mas larga a la mas corta para que
# una cadena corta no se coma un trozo de otra mas larga.
TRADUCCIONES = [
# ---- nav, hero y estados de carga ----
(">Inicio FIG</a>", ">FIG home</a>"),
(">Metodología</a>", ">Methodology</a>"),
(">Instrumentos</a>", ">Instruments</a>"),

(">Mercado</a>", ">Market</a>"),
(">Riesgo</a>", ">Risk</a>"),
(">Tabla</a>", ">Table</a>"),
("Informe · Torneo Portafolio 2026", "Report · Portfolio Tournament 2026"),
("Lo que dicen", "What the"),
("los datos", "tournament"),
("del torneo", "data says"),

("Cargando el corte vigente…", "Loading the current cut…"),
("Cargando datos del torneo…", "Loading tournament data…"),
("No se pudieron cargar los datos del torneo.", "The tournament data could not be loaded."),
("Este informe se alimenta de", "This report reads"),
("; si estás viendo esto, ese archivo no está disponible. El",
 "; if you are seeing this, that file is unavailable. The"),
("ranking oficial", "official ranking"),
("sigue funcionando.", "still works."),
("Abrir menú", "Open menu"),
("Cifras principales del torneo", "Headline tournament figures"),
# ---- secciones ----
("01 · Resumen", "01 · Summary"),
("Cinco cosas que muestran los números", "Five things the numbers show"),
("Todo lo que sigue está calculado desde el corte vigente. Las cifras se recalculan solas cada vez que se publica una semana nueva.",
 "Everything below is computed from the current cut. The figures recalculate themselves every time a new week is published."),
("02 · Frente al mercado", "02 · Against the market"),
("El torneo contra el", "The tournament against the"),

("Retorno acumulado: el torneo y su índice de referencia",
 "Cumulative return: the tournament and its benchmark"),
("La banda cubre del percentil 25 al 75 de los equipos; la línea dorada es la mediana.",
 "The band covers the 25th to 75th percentile of teams; the gold line is the median."),
("Retorno acumulado de los equipos frente al MSCI ACWI, por semana",
 "Cumulative return of the teams against the MSCI ACWI, by week"),
("03 · Dispersión", "03 · Spread"),
("Qué tan distintos son los resultados", "How different the results are"),

("Distribución del retorno relativo", "Distribution of relative return"),
("Cuántos equipos caen en cada tramo, en el corte vigente.",
 "How many teams fall in each band, at the current cut."),
("Histograma del retorno relativo de los equipos",
 "Histogram of the teams' relative return"),
("04 · Riesgo y retorno", "04 · Risk and return"),
("Cuánto se arriesgó para llegar ahí", "How much risk it took to get there"),

("Caída máxima frente a retorno relativo", "Maximum drawdown against relative return"),
("Un punto por equipo. Arriba a la izquierda es la esquina buena: más retorno con menos caída.",
 "One dot per team. Top left is the good corner: more return with a smaller drawdown."),
("Dispersión de caída máxima contra retorno relativo por equipo",
 "Scatter of maximum drawdown against relative return, by team"),
("05 · Movilidad", "05 · Movement"),
("El ranking se mueve más de lo que parece", "The ranking moves more than it looks"),
("Comparar la posición de la primera semana publicada con la de hoy muestra si la tabla se congeló temprano o si todavía se juega.",
 "Comparing each team's position in the first published week with today's shows whether the table froze early or is still in play."),
("Mayores cambios de posición", "Biggest changes in position"),
("Puestos ganados o perdidos entre la primera semana publicada y el corte vigente.",
 "Places gained or lost between the first published week and the current cut."),

("06 · Composición", "06 · Composition"),
("De dónde salen los puntos", "Where the points come from"),

("Desglose del puntaje, primeros diez equipos", "Score breakdown, top ten teams"),
("Cada barra suma el puntaje total del equipo sobre 100.",
 "Each bar adds up to the team's total score out of 100."),
("Composición del puntaje de los diez primeros equipos",
 "Score composition of the top ten teams"),
("07 · Instrumentos", "07 · Instruments"),
("Qué compraron los equipos", "What the teams bought"),
("El ranking mide el resultado; esto mira la decisión que lo produjo. Sale del registro de operaciones de Bloomberg, no del Excel semanal, así que cubre un período propio que se indica al pie de cada gráfico.",
 "The ranking measures the outcome; this looks at the decision behind it. It comes from the Bloomberg trade record, not the weekly spreadsheet, so it covers a period of its own, stated under each chart."),
("Los ETF más usados", "The most used ETFs"),
("Ordenados por cuántos equipos lo incorporaron a su cartera, no por número de operaciones: un equipo que compra el mismo ETF cuatro veces no lo hace más popular.",
 "Ranked by how many teams held them, not by number of trades: a team buying the same ETF four times does not make it more popular."),
("ETF más usados por los equipos del torneo", "ETFs most used by the tournament teams"),
("Mercados y sectores", "Markets and sectors"),
("Dónde se posicionaron. A la izquierda el mercado del ETF; a la derecha, solo los ETF sectoriales.",
 "Where they positioned themselves. On the left, the ETF's market; on the right, sector ETFs only."),
("Mercados y sectores elegidos por los equipos", "Markets and sectors chosen by the teams"),
("Factores, temáticos y apuestas país", "Factors, thematics and country bets"),
("Las tres capas más finas de decisión dentro del mismo universo. El porcentaje es sobre los equipos del torneo.",
 "The three finer layers of decision inside the same universe. The percentage is of the tournament's teams."),
("Factores, temáticos y apuestas país usados por los equipos",
 "Factors, thematics and country bets used by the teams"),
("08 · Detalle", "08 · Detail"),
("Todos los equipos", "Every team"),
("La misma información de los gráficos, en forma de tabla: sirve para buscar un equipo puntual y es la versión accesible de todo lo anterior.",
 "The same information as the charts, as a table: useful to look up one team, and the accessible version of everything above."),
("09 · Metodología", "09 · Methodology"),
("Cómo leer este informe", "How to read this report"),


("Creado por", "Made by"),
("← Volver a FEN Investment Group", "← Back to FEN Investment Group"),
# ---- encabezados de la tabla ----

('<th scope="col">Ret. relativo</th>', '<th scope="col">Rel. return</th>'),
('<th scope="col">Máx. caída</th>', '<th scope="col">Max. drawdown</th>'),
('<th scope="col">Δ posición</th>', '<th scope="col">Δ position</th>'),
('<th scope="col">Puntos</th>', '<th scope="col">Points</th>'),
('<th scope="col">Equipo</th>', '<th scope="col">Team</th>'),
# ---- cadenas del JS ----
('"Corte al "+D.corte+" · semana "+D.semana',
 '"Cut of "+corteEN(D.corte)+" · week "+D.semana'),
('l:"Equipos",s:"en el corte vigente"', 'l:"Teams",s:"at the current cut"'),
('l:"Participantes",s:conMiembros<EQ.length?("en "+conMiembros+" equipos con nómina registrada"):"inscritos en los equipos"',
 'l:"Participants",s:conMiembros<EQ.length?("across "+conMiembros+" teams with a registered roster"):"signed up across the teams"'),
('l:"Cortes publicados",s:"semanas "+SEM[0]+" a "+SEM[SEM.length-1]', 'l:"Cuts published",s:"weeks "+SEM[0]+" to "+SEM[SEM.length-1]'),
('l:"Capital simulado",s:"USD 10M por cartera"', 'l:"Simulated capital",s:"USD 10M per portfolio"'),
('"En la semana <b>"+sc+"</b>, última con dato del índice, <b>"+gan+" de "+rc.length+"</b> equipos ("+num(ganPct,0)+"%) acumulaban más retorno que el <b>MSCI ACWI</b>. El índice llevaba "+pctS(ACWI[sc])+" y la mediana del torneo "+pctS(cuantil(rc,.5))+"."',
 '"In week <b>"+sc+"</b>, the last with index data, <b>"+gan+" of "+rc.length+"</b> teams ("+num(ganPct,0)+"%) had accumulated more return than the <b>MSCI ACWI</b>. The index stood at "+pctS(ACWI[sc])+" and the tournament median at "+pctS(cuantil(rc,.5))+"."'),
('"Esa ventaja se fue cerrando: en la semana <b>"+ini.s+"</b> le ganaba al índice el <b>"+num(ini.p,0)+"%</b> del torneo, y en la <b>"+fin.s+"</b> el <b>"+num(fin.p,0)+"%</b>. El mercado no se quedó quieto mientras los equipos aprendían."',
 '"That edge narrowed: in week <b>"+ini.s+"</b>, <b>"+num(ini.p,0)+"%</b> of the tournament was beating the index, and by week <b>"+fin.s+"</b>, <b>"+num(fin.p,0)+"%</b>. The market did not stand still while the teams learned."'),
('"El corte vigente todavía no tiene capturado el valor del <b>MSCI ACWI</b>, que llega por un proceso aparte. Las comparaciones contra el índice de este informe llegan hasta la última semana que sí lo tiene."',
 '"The current cut does not yet have the <b>MSCI ACWI</b> value, which arrives through a separate process. The comparisons against the index in this report run to the last week that does have it."'),
('"La distancia entre extremos es enorme: <b>"+mejor.nombre+"</b> le saca <b>"+pctS(mejor.retRel)+"</b> al índice y <b>"+peor.nombre+"</b> queda <b>"+pctS(peor.retRel)+"</b>. Son <b>"+num(Math.abs(mejor.retRel-peor.retRel)*100,0)+" puntos porcentuales</b> de diferencia dentro de la misma competencia, con las mismas reglas y el mismo universo de instrumentos."',
 '"The gap between the extremes is enormous: <b>"+mejor.nombre+"</b> beats the index by <b>"+pctS(mejor.retRel)+"</b> while <b>"+peor.nombre+"</b> sits at <b>"+pctS(peor.retRel)+"</b>. That is <b>"+num(Math.abs(mejor.retRel-peor.retRel)*100,0)+" percentage points</b> of difference inside the same competition, with the same rules and the same instrument universe."'),
('"<b>"+pos+" de "+rU.length+"</b> equipos cierran el corte con retorno acumulado positivo, y la mediana del torneo va en <b>"+pctS(medU)+"</b>. Ganar plata y ganarle al mercado no son lo mismo: el punto de comparación de esta competencia no es cero, es el índice."',
 '"<b>"+pos+" of "+rU.length+"</b> teams close the cut with a positive cumulative return, and the tournament median sits at <b>"+pctS(medU)+"</b>. Making money and beating the market are not the same thing: the benchmark here is not zero, it is the index."'),
('"El ranking está lejos de estar resuelto: entre la semana <b>"+SEM[0]+"</b> y la <b>"+sU+"</b> cada equipo se movió en promedio <b>"+num(prom,1)+" puestos</b>, y <b>"+top.e.nombre+"</b> subió <b>"+top.d+"</b> lugares, del "+top.a+"° al "+top.b+"°."',
 '"The ranking is far from settled: between week <b>"+SEM[0]+"</b> and week <b>"+sU+"</b> each team moved an average of <b>"+num(prom,1)+" places</b>, and <b>"+top.e.nombre+"</b> climbed <b>"+top.d+"</b> spots, from "+top.a+" to "+top.b+"."'),
('fila("Mediana del torneo",pctS(d.p50))', 'fila("Tournament median",pctS(d.p50))'),
('t:"Mediana del torneo"', 't:"Tournament median"'),
('t:"Rango medio de los equipos (percentil 25–75)"', 't:"Middle range of teams (25th–75th percentile)"'),
('"Retorno acumulado desde el inicio del torneo. La banda muestra dónde cae la mitad central de los equipos: cuando se ensancha, la competencia se está separando."',
 '"Cumulative return since the tournament started. The band shows where the middle half of the teams falls: when it widens, the field is pulling apart."'),
('" <b>La línea del índice llega hasta la semana "+SEM_ACWI[SEM_ACWI.length-1]+"</b>: el valor del ACWI lo captura un proceso aparte y suele llegar un corte después. No se estima el dato que falta."',
 '" <b>The index line runs to week "+SEM_ACWI[SEM_ACWI.length-1]+"</b>: the ACWI value is captured by a separate process and usually arrives one cut later. The missing figure is not estimated."'),
('t:"Le gana al índice"', 't:"Beats the index"'),
('t:"Tramo que cruza el cero"', 't:"Band crossing zero"'),
('t:"Queda bajo el índice"', 't:"Trails the index"'),
('"De los <b>"+v.length+"</b> equipos, <b>"+sobre+"</b> cierran con retorno relativo positivo. La mediana está en <b>"+pctS(cuantil(v,.5))+"</b> y la desviación estándar en <b>"+pct(sd(v))+"</b>: una dispersión así, con reglas idénticas para todos, muestra cuánto pesan las decisiones de cada equipo."',
 '"Of the <b>"+v.length+"</b> teams, <b>"+sobre+"</b> close with a positive relative return. The median sits at <b>"+pctS(cuantil(v,.5))+"</b> and the standard deviation at <b>"+pct(sd(v))+"</b>: a spread like that, under identical rules, shows how much each team\\u2019s decisions weigh."'),
('" <b>Ojo con esta cifra:</b> medido en cambio como retorno acumulado menos el del índice, los equipos por delante del ACWI en la semana "+cmp.s+" eran <b>"+cmp.porRet+"</b>, no "+cmp.porExc+". Las dos medidas no coinciden — ver la nota de metodología."',
 '" <b>Careful with this figure:</b> measured instead as cumulative return minus the index, the teams ahead of the ACWI in week "+cmp.s+" were <b>"+cmp.porRet+"</b>, not "+cmp.porExc+". The two measures do not agree \\u2014 see the methodology note."'),
('fila("Posición",e.posicion+"°")', 'fila("Position",e.posicion+"")'),
('fila("Caída máxima",pct(e.metricas.mdd))', 'fila("Max. drawdown",pct(e.metricas.mdd))'),
('"Color por puntaje. La correlación entre caída máxima y retorno relativo es <b>"+num(r)+"</b>"',
 '"Coloured by score. The correlation between maximum drawdown and relative return is <b>"+num(r)+"</b>"'),
('", es decir <b>negativa</b>: en este torneo los equipos que más cayeron tendieron a rendir peor, no mejor. Asumir más riesgo no compró más retorno."',
 '", that is <b>negative</b>: in this tournament the teams that fell furthest tended to do worse, not better. Taking on more risk did not buy more return."'),
('", es decir <b>positiva</b>: quienes toleraron caídas más profundas tendieron a terminar con más retorno relativo. Es un premio al riesgo que conviene mirar con cuidado, porque también es un premio a la suerte."',
 '", that is <b>positive</b>: those who tolerated deeper drawdowns tended to finish with more relative return. That is a reward for risk worth reading carefully, because it is also a reward for luck."'),
('", prácticamente <b>nula</b>: el tamaño de la caída no explica el retorno. Los resultados se separan por otras razones que por cuánto riesgo se toleró."',
 '", effectively <b>nil</b>: the size of the drawdown does not explain the return. The results separate for reasons other than how much risk was tolerated."'),
('t:"Subió en la tabla"', 't:"Climbed the table"'),
('t:"Bajó en la tabla"', 't:"Fell in the table"'),
('"Se muestran los "+n+" que más subieron y los "+n+" que más bajaron. En promedio, cada equipo cambió <b>"+num(media(todos),1)+" puestos</b> entre ambos extremos y <b>"+num(media(sem),1)+" puestos</b> de una semana a la siguiente: la tabla se reordena de verdad, no solo en los márgenes."',
 '"Showing the "+n+" biggest climbers and the "+n+" biggest fallers. On average each team moved <b>"+num(media(todos),1)+" places</b> between the two ends and <b>"+num(media(sem),1)+" places</b> from one week to the next: the table genuinely reorders, not just at the margins."'),
('t:"Information Ratio"', 't:"Information Ratio"'),
('t:"Retorno en exceso"', 't:"Excess return"'),
('t:"Ratio de Sharpe"', 't:"Sharpe ratio"'),
('t:"Caída máxima"', 't:"Max. drawdown"'),
('"El puntaje reparte 100 puntos entre cinco métricas y se calcula por percentil <b>contra el resto del torneo</b>, no contra un valor fijo: por eso un equipo puede cambiar de puntaje sin que cambie su propia cartera. La mayor diferencia entre los diez primeros y el resto está en <b>"',
 '"The score splits 100 points across five metrics and is computed by percentile <b>against the rest of the tournament</b>, not against a fixed value: that is why a team\\u2019s score can move without its own portfolio changing. The biggest gap between the top ten and the rest is in <b>"'),
('" puntos de ventaja promedio, sobre "+brecha[0].peso+" posibles), y la menor en <b>"',
 '" points of average advantage, out of "+brecha[0].peso+" available), and the smallest in <b>"'),
('fila("Equipos que lo usaron",d.equipos+" ("+num(d.pctEquipos,1)+"%)")',
 'fila("Teams that used it",d.equipos+" ("+num(d.pctEquipos,1)+"%)")'),
('fila("Operaciones",d.operaciones)', 'fila("Trades",d.operaciones)'),
('fila("Monto aprox.","USD "+ent(d.usdAprox))', 'fila("Approx. amount","USD "+ent(d.usdAprox))'),
('"% DE LOS "+ETF.totales.equipos+" EQUIPOS QUE LO INCORPORÓ A SU CARTERA"',
 '"% OF THE "+ETF.totales.equipos+" TEAMS THAT HELD IT"'),
('"Sobre "+ent(ETF.totales.compras)+" operaciones de compra de "+ETF.totales.equipos+',
 '"Across "+ent(ETF.totales.compras)+" buy trades by "+ETF.totales.equipos+'),
('" equipos, hasta el "+ETF.ultimaOperacion+". El más usado es <b>"+ETF.topEtf[0].ticker+',
 '" teams, through "+ETF.ultimaOperacion+". The most used is <b>"+ETF.topEtf[0].ticker+'),
('"</b>, presente en "+ETF.topEtf[0].equipos+" carteras ("+num(ETF.topEtf[0].pctEquipos,0)+',
 '"</b>, held in "+ETF.topEtf[0].equipos+" portfolios ("+num(ETF.topEtf[0].pctEquipos,0)+'),
('"% del torneo)."+(g?" El <b>"+num(g.pctOperaciones,1)+"%</b> de las operaciones se hizo en ETF de iShares.":"")',
 '"% of the tournament)."+(g?" <b>"+num(g.pctOperaciones,1)+"%</b> of all trades were in iShares ETFs.":"")'),
('t:"Mercado del ETF"', 't:"ETF market"'),
('t:"ETF sectoriales"', 't:"Sector ETFs"'),
('"El mercado más elegido es <b>"+eeuu.nombre+"</b> ("+num(eeuu.pctOperaciones,1)+',
 '"The most chosen market is <b>"+eeuu.nombre+"</b> ("+num(eeuu.pctOperaciones,1)+'),
('"% de las operaciones, en "+eeuu.equipos+" equipos) y el sector más elegido es <b>"+sSem.nombre+',
 '"% of trades, across "+eeuu.equipos+" teams) and the most chosen sector is <b>"+sSem.nombre+'),
('"</b> ("+sSem.equipos+" equipos, "+num(sSem.pctEquipos,0)+"% del torneo). Un ETF sectorial se cuenta además en su mercado, así que las dos columnas no suman lo mismo."',
 '"</b> ("+sSem.equipos+" teams, "+num(sSem.pctEquipos,0)+"% of the tournament). A sector ETF also counts in its market, so the two columns do not add up to the same total."'),
('"Los factores son el <b>"+num(100*tot(ETF.factores)/c,0)+',
 '"Factors are <b>"+num(100*tot(ETF.factores)/c,0)+'),
('"%</b> de las operaciones, los temáticos el <b>"+num(100*tot(ETF.tematicos)/c,0)+',
 '"%</b> of trades, thematics <b>"+num(100*tot(ETF.tematicos)/c,0)+'),
('"%</b> y las apuestas por un país el <b>"+num(100*tot(ETF.paises)/c,0)+',
 '"%</b> and single-country bets <b>"+num(100*tot(ETF.paises)/c,0)+'),
('"%</b>. Son decisiones más finas que elegir un índice amplio, y muestran que el torneo no se jugó solo con carteras genéricas."',
 '"%</b>. These are finer decisions than picking a broad index, and they show the tournament was not played with generic portfolios alone."'),
('l:"En ETF de iShares",s:"de "+ent(t.compras)+" operaciones de compra"',
 'l:"In iShares ETFs",s:"of "+ent(t.compras)+" buy trades"'),
('l:"ETF distintos",s:"usados a lo largo del torneo"',
 'l:"Distinct ETFs",s:"used across the tournament"'),
('l:"Bolsas",s:"en "+t.divisas+" divisas distintas"',
 'l:"Exchanges",s:"in "+t.divisas+" different currencies"'),
('s:"el resto en renta fija, commodities y cripto"',
 's:"the rest in fixed income, commodities and crypto"'),
('"Los "+EQ.length+" equipos del corte al "+D.corte+" (semana "+D.semana+"). La columna Δ posición compara con el corte anterior."',
 '"The "+EQ.length+" teams at the cut of "+corteEN(D.corte)+" (week "+D.semana+"). The Δ position column compares with the previous cut."'),
# ---- metodologia ----
('["Fuente","Los datos vienen del Excel oficial del torneo, generado desde Bloomberg PORT por el área de Portafolio, y se transforman con <code>generar_torneo.py</code> a <code>datos/torneo.json</code>. Este informe lee ese archivo directamente: no hay una sola cifra escrita a mano en esta página."]',
 '["Source","The data comes from the tournament\\u2019s official spreadsheet, produced from Bloomberg PORT by the Portfolio desk, and is turned into <code>datos/torneo.json</code> by <code>generar_torneo.py</code>. This report reads that file directly: there is not a single hand-written figure on this page."]'),
('["Corte vigente","Semana <b>"+D.semana+"</b>, al <b>"+D.corte+"</b>. Se publican <b>"+SEM.length+"</b> cortes, de la semana "+SEM[0]+" a la "+SEM[SEM.length-1]+"."]',
 '["Current cut","Week <b>"+D.semana+"</b>, at <b>"+corteEN(D.corte)+"</b>. <b>"+SEM.length+"</b> cuts are published, from week "+SEM[0]+" to week "+SEM[SEM.length-1]+"."]'),
('["Retorno acumulado","Lo que ganó o perdió la cartera desde el inicio del torneo. Es la cifra de los gráficos de trayectoria."]',
 '["Cumulative return","What the portfolio gained or lost since the tournament began. It is the figure behind the trajectory charts."]'),
('["Retorno relativo","El <b>retorno en exceso</b> que entrega Bloomberg PORT. Es distinto del retorno acumulado y no hay que confundirlos: un equipo puede tener retorno positivo y retorno relativo negativo."]',
 '["Relative return","The <b>excess return</b> reported by Bloomberg PORT. It is different from cumulative return and the two should not be confused: a team can have a positive return and a negative relative return."]'),
('["Puntaje","100 puntos repartidos entre Information Ratio (30), retorno en exceso (25), Ratio de Sharpe (15), VaR 95% (15) y caída máxima (15). Cada métrica se puntúa por <b>percentil continuo contra los demás equipos</b>, así que el puntaje de un equipo depende de cómo le fue al resto."]',
 '["Score","100 points split across Information Ratio (30), excess return (25), Sharpe ratio (15), VaR 95% (15) and maximum drawdown (15). Each metric is scored by <b>continuous percentile against the other teams</b>, so a team\\u2019s score depends on how everyone else did."]'),
('["VaR y caída máxima","Vienen en negativo. El mejor valor es el más cercano a cero, no el mayor en magnitud."]',
 '["VaR and maximum drawdown","Both come as negative numbers. The best value is the one closest to zero, not the largest in magnitude."]'),
('["Dos medidas que no calzan","Hay dos formas de decir que un equipo <b>le gana al índice</b>, y en estos datos no dan lo mismo. Restando el retorno acumulado del ACWI al del equipo, en la semana <b>"+cmp.s+"</b> quedan por delante <b>"+cmp.porRet+" de "+cmp.n+"</b> equipos. Usando el <b>retorno en exceso de Bloomberg PORT</b> —el campo que alimenta el puntaje y los gráficos de retorno relativo— quedan <b>"+cmp.porExc+"</b>. La brecha por equipo es grande y sistemática, así que no es un redondeo: son dos cálculos distintos, y no está documentado en los datos con qué base construye PORT el suyo. Este informe muestra las dos en vez de elegir una, y <b>conviene que el área de Portafolio confirme cuál es la oficial</b> para comunicar resultados."]',
 '["Two measures that disagree","There are two ways to say a team <b>beats the index</b>, and in this data they do not agree. Subtracting the ACWI\\u2019s cumulative return from the team\\u2019s, in week <b>"+cmp.s+"</b> <b>"+cmp.porRet+" of "+cmp.n+"</b> teams come out ahead. Using <b>Bloomberg PORT\\u2019s excess return</b> \\u2014 the field that feeds the score and the relative-return charts \\u2014 <b>"+cmp.porExc+"</b> do. The gap per team is large and systematic, so it is not rounding: they are two different calculations, and the data does not document what base PORT builds its own on. This report shows both instead of picking one, and <b>the Portfolio desk should confirm which is official</b> for reporting results."]'),
('["Dato faltante","El <b>MSCI ACWI</b> se captura por un proceso aparte y suele llegar un corte después, así que "',
 '["Missing data","The <b>MSCI ACWI</b> is captured by a separate process and usually arrives one cut later, so "'),
('"la semana <b>"+faltaAcwi[0]+"</b> todavía no lo tiene"',
 '"week <b>"+faltaAcwi[0]+"</b> does not have it yet"'),
('"las semanas <b>"+faltaAcwi.join(", ")+"</b> todavía no lo tienen"',
 '"weeks <b>"+faltaAcwi.join(", ")+"</b> do not have it yet"'),
('". Donde falta, no se estima: la línea del índice simplemente se corta y las comparaciones se hacen contra el último corte que sí lo tiene."',
 '". Where it is missing it is not estimated: the index line simply stops, and comparisons are made against the last cut that does have it."'),
('["Nóminas","<b>"+sinNomina+"</b> "', '["Rosters","<b>"+sinNomina+"</b> "'),
('"equipo no tiene"', '"team has no"'),
('"equipos no tienen"', '"teams have no"'),
('" nómina de integrantes registrada en el archivo de datos, así que el conteo de participantes es un <b>piso</b>, no el total exacto."',
 '" member roster in the data file, so the participant count is a <b>floor</b>, not the exact total."'),
('["Actualización","Esta página se recalcula sola con cada corte semanal. Si el ranking oficial muestra una semana más nueva que la de arriba, es que este archivo se cargó desde la caché del navegador."]',
 '["Updates","This page recalculates itself with every weekly cut. If the official ranking shows a newer week than the one above, this file was served from the browser cache."]'),
# ---- mensajes de consola y errores internos ----
('new Error("sin equipos")', 'new Error("no teams")'),
('"informe: no se pudo cargar torneo.json"', '"report: could not load torneo.json"'),
('"informe: sección de instrumentos omitida ("', '"report: instruments section skipped ("'),
('"etf.json sin datos utilizables"', '"etf.json has no usable data"'),
# ---- textos exactos (el HTML los trae en una sola linea larga) ----
("Un corte transversal de la competencia: cómo le fue al conjunto frente al mercado, cuánto se parecen entre sí los resultados, qué riesgo se asumió para conseguirlos y qué tan estable ha sido el ranking.",
 "A cross-section of the competition: how the field did against the market, how alike the results are, what risk was taken to get them, and how stable the ranking has been."),
("Cada equipo compite contra el índice global de referencia. Esta es la trayectoria del conjunto —no de un equipo— comparada con ese índice, semana a semana y en retorno acumulado desde el inicio.",
 "Every team competes against the global benchmark. This is the path of the field as a whole, not of one team, against that index, week by week and in cumulative return since the start."),
("El retorno relativo es cuánto le saca —o le pierde— cada equipo al índice. Un torneo donde todos hacen lo mismo tendría una distribución angosta; este no la tiene.",
 "Relative return is how much each team beats, or trails, the index by. A tournament where everyone did the same thing would show a narrow distribution; this one does not."),
("La caída máxima (<em>drawdown</em>) es lo peor que perdió una cartera desde un máximo. Cruzarla contra el retorno relativo separa a quien ganó administrando el riesgo de quien ganó tolerándolo.",
 "Maximum drawdown is the worst a portfolio fell from a peak. Plotting it against relative return separates those who won by managing risk from those who won by tolerating it."),
("El puntaje reparte 100 puntos entre cinco métricas de Bloomberg. Ver el desglose explica por qué dos equipos con retornos parecidos pueden estar a veinte puestos de distancia.",
 "The score splits 100 points across five Bloomberg metrics. The breakdown explains why two teams with similar returns can sit twenty places apart."),
# ---- rotulos de los ejes SVG ----
('"IGUAL AL ÍNDICE"', '"LEVEL WITH THE INDEX"'),
('"CAÍDA MÁXIMA (MAGNITUD)"', '"MAXIMUM DRAWDOWN (MAGNITUDE)"'),
('"TEMÁTICO"', '"THEMATIC"'),
('"APUESTA PAÍS"', '"COUNTRY BET"'),
('"report: could not load torneo.json"', '"report: could not load torneo.json"'),
# ---- rotulos de ejes y de tooltip que el detector estricto saco a la luz ----
('"SEMANA DEL TORNEO"', '"TOURNAMENT WEEK"'),
('"RETORNO RELATIVO AL MSCI ACWI"', '"RELATIVE RETURN VS MSCI ACWI"'),
('"PUESTOS GANADOS O PERDIDOS ENTRE LA SEMANA "+s0+" Y LA "+sU',
 '"PLACES GAINED OR LOST BETWEEN WEEK "+s0+" AND WEEK "+sU'),
('"PUNTOS SOBRE 100"', '"POINTS OUT OF 100"'),
('"SIN CAMBIO"', '"NO CHANGE"'),
('"MERCADO",150', '"MARKET",150'),
('"SECTOR",150', '"SECTOR",150'),
('"FACTOR",140', '"FACTOR",140'),
('ligar(c,"<b>Semana "+d.s+"</b>"', 'ligar(c,"<b>Week "+d.s+"</b>"'),
('fila("MSCI ACWI","sin dato")', 'fila("MSCI ACWI","no data")'),
('fila("Diferencia",pctS(d.p50-a))', 'fila("Difference",pctS(d.p50-a))'),
('fila("Retorno relativo",pctS(e.retRel))', 'fila("Relative return",pctS(e.retRel))'),
('fila("Aporta al total",num(100*v/e.puntos,0)+"%")', 'fila("Share of total",num(100*v/e.puntos,0)+"%")'),
('fila("Puntaje total",num(e.puntos)+" / 100")', 'fila("Total score",num(e.puntos)+" / 100")'),
('<title id="cMovT">Equipos con mayor cambio de posición en el ranking</title>',
 '<title id="cMovT">Teams with the biggest change in ranking position</title>'),
# ---- ultimos cuatro rotulos, encontrados uno a uno ----
('var tF=txt(xF,yF+4,"TORNEO","dl"', 'var tF=txt(xF,yF+4,"TOURNAMENT","dl"'),
('"RETORNO RELATIVO","ax-txt"', '"RELATIVE RETURN","ax-txt"'),
('fila("Equipos",d.n)', 'fila("Teams",d.n)'),
('fila("Equipos",n)', 'fila("Teams",n)'),
('fila("Semana "+s0,m.a+"°")+fila("Semana "+sU,m.b+"°")',
 'fila("Week "+s0,m.a+"")+fila("Week "+sU,m.b+"")'),
# ---- marca del nav y aviso legal ----
('<div class="brand-name">Informe</div><span class="brand-sub">Torneo Portafolio</span>',
 '<div class="brand-name">Report</div><span class="brand-sub">Portfolio Tournament</span>'),
('aria-label="FEN Investment Group — Inicio"', 'aria-label="FEN Investment Group — Home"'),
('<b>Esto no es asesoría de inversión.</b> Las carteras del Torneo Portafolio son simuladas: ningún equipo administra dinero real y ninguna cifra de este informe constituye una recomendación de compra o venta. El torneo es una actividad formativa de FEN Investment Group.',
 '<b>This is not investment advice.</b> Portfolio Tournament portfolios are simulated: no team manages real money, and no figure in this report is a recommendation to buy or sell. The tournament is an educational activity run by FEN Investment Group.'),
# ---- conmutador de idioma: en la version en ingles apunta al reves ----
('<a href="../en/informe/index.html" hreflang="en" lang="en">English</a>',
 '<a href="../../informe/index.html" hreflang="es" lang="es">Español</a>'),
]

# Meses del campo `corte`, que viene del dato ("21 · AGO · 2026"). Se traduce
# solo el mes: reescribir la fecha entera inventaria un formato que no calza
# con el que publica el ranking oficial.
AYUDANTE = '''
/* Traduce SOLO el mes del corte, que en los datos viene en espanol
   ("21 · AGO · 2026"). Generado por generar_informe_en.py. */
function corteEN(c){
  var M={ENE:"Jan",FEB:"Feb",MAR:"Mar",ABR:"Apr",MAY:"May",JUN:"Jun",
         JUL:"Jul",AGO:"Aug",SEP:"Sep",OCT:"Oct",NOV:"Nov",DIC:"Dec"};
  return String(c||"").replace(/[A-Z\\u00c1\\u00c9\\u00cd\\u00d3\\u00da]{3}/g,function(m){return M[m]||m});
}
'''

# Marcadores de que quedo espanol sin traducir en algo que se ve.
# OJO CON LOS PLURALES. La primera version buscaba \bcorte\b y \bsemana\b, y por
# eso dejo pasar "Cortes publicados" y "semanas 5 a 15" hasta la pagina generada:
# el chequeo decia "sin texto en espanol pendiente" con dos etiquetas en espanol
# a la vista. Cualquier palabra que se agregue aca va con su plural.
SOSPECHA = re.compile(
    r'[áéíóúñÁÉÍÓÚÑ¿¡]|'
    r'\b(el|la|los|las|un|una|unos|unas|del|al|que|con|por|para|sin|sobre|'
    r'este|esta|estos|estas|sus|son|hay|cada|todos|desde|entre|'
    r'equipos?|semanas?|cortes?|torneos?|puntajes?|retornos?|caidas?|indices?|'
    r'carteras?|simulad[oa]s?|publicad[oa]s?|capital|mercados?|riesgos?|'
    r'participantes?|posicion)\b',
    re.IGNORECASE)

# Lo que puede tener espanol legitimamente y no se revisa.
EXENTO = re.compile(
    # Nombres de archivo y de ruta: `torneo.json` y `generar_torneo.py` llevan
    # "torneo" dentro y no son texto para nadie. Sin esto el chequeo marcaba
    # como "sin traducir" un mensaje de consola que ya estaba en ingles.
    r'\w+\.(json|py|js|html|css|png|webp)|'
    r'fig-oro|FEN Investment Group|Portafolio|Francisco Valenzuela|Manuel Paz|'
    # "Español" es la etiqueta del conmutador de idioma: tiene que quedar
    # en espanol, es justo lo que le dice a un hispanohablante donde pinchar.
    r'Español|'
    r'feninvestmentgroup|Simulated capital|Total score|class=|posicion<=|innerHTML|textContent')


def revisar_identificadores(fuente: str, generado: str) -> list:
    """Los id= y class= tienen que ser IDENTICOS en las dos versiones.

    Una traduccion corta puede colarse dentro de un identificador: "Mercado"
    convirtio `id="cMercado"` en `id="cMarket"`. Ahi funciono de casualidad,
    porque el selector del JS cambio igual; si el mismo accidente cae sobre una
    clave de datos (`d.mercado`) o sobre una clase que solo esta en el CSS, la
    pagina se rompe en silencio. Esto lo caza en el acto.
    """
    def ids(h):
        return sorted(set(re.findall(r'id="([^"]+)"', h)))
    a, b = ids(fuente), ids(generado)
    if a == b:
        return []
    return ["id que cambio: " + x for x in
            sorted(set(a) ^ set(b))]


def revisar(html: str) -> list:
    """Busca texto de cara al usuario que haya quedado en espanol."""
    problemas = []
    cuerpo = html.split('</head>', 1)[1]
    sin_codigo = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', cuerpo,
                        flags=re.S | re.I)
    sin_codigo = re.sub(r'<!--.*?-->', '', sin_codigo, flags=re.S)
    for x in re.split(r'<[^>]+>', sin_codigo):
        x = ' '.join(x.split())
        # Se QUITAN las marcas exentas y se revisa lo que queda. Antes se
        # saltaba el texto entero si contenia una: un parrafo integro en
        # espanol paso limpio solo porque terminaba en "FEN Investment Group".
        resto = EXENTO.sub(' ', x)
        if len(resto.strip()) > 3 and SOSPECHA.search(resto):
            problemas.append('texto visible: ' + x[:110])

    # El CSS tambien puede escribir texto en pantalla con `content:`, y hasta
    # ahora nadie lo revisaba: una regla como `content:"Desliza"` habria llegado
    # a la version en ingles sin que el chequeo dijera nada.
    css = ''.join(re.findall(r'<style[^>]*>(.*?)</style>', html, re.S))
    for lit in re.findall(r'content\s*:\s*"([^"]{3,})"', css):
        if SOSPECHA.search(EXENTO.sub(' ', lit)):
            problemas.append('CSS content: ' + lit[:80])

    js = ''.join(re.findall(r'<script[^>]*>(.*?)</script>', html, re.S))
    js = re.sub(r'/\*.*?\*/', ' ', js, flags=re.S)
    js = re.sub(r'(?m)^\s*//.*$', ' ', js)
    for lit in re.findall(r'"((?:[^"\\\n]|\\.){4,}?)"', js):
        resto = EXENTO.sub(' ', lit)
        if SOSPECHA.search(resto):
            problemas.append('cadena JS: ' + lit[:110])
    return problemas


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera la version en ingles del informe")
    ap.add_argument("--aplicar", action="store_true", help="escribe el archivo")
    args = ap.parse_args()

    if not FUENTE.exists():
        print(f"ERROR: falta {FUENTE}", file=sys.stderr)
        return 1

    html = FUENTE.read_text(encoding="utf-8")

    for a, b in CABECERA:
        if a not in html:
            print(f"ERROR: no encontre en la cabecera -> {a[:80]}", file=sys.stderr)
            return 1
        html = html.replace(a, b)

    for a, b in RUTAS:
        html = html.replace(a, b)

    sin_usar = []
    for a, b in sorted(TRADUCCIONES, key=lambda p: -len(p[0])):
        if a in html:
            html = html.replace(a, b)
        else:
            sin_usar.append(a)

    # El ayudante de fechas va al principio del <script> grande del informe.
    # OJO: si esta ancla deja de calzar, `corteEN` queda sin definir y el script
    # ENTERO muere con un ReferenceError -- los graficos salen vacios y la
    # pagina parece rota sin decir por que. Paso de verdad al escribir esto, por
    # eso se comprueba en vez de confiar.
    ANCLA = "<script>\n/* ====="
    if ANCLA not in html:
        print("ERROR: no encontre donde inyectar corteEN(); sin eso la pagina "
              "queda rota.", file=sys.stderr)
        return 1
    html = html.replace(ANCLA, "<script>\n" + AYUDANTE + "/* =====", 1)
    if "function corteEN" not in html:
        print("ERROR: corteEN no quedo definido.", file=sys.stderr)
        return 1

    # Aviso de archivo generado, para que nadie lo edite a mano.
    html = html.replace("<head>",
        "<head>\n<!-- GENERADO por generar_informe_en.py desde informe/index.html.\n"
        "     No editar a mano: el proximo `python generar_informe_en.py --aplicar`\n"
        "     lo pisa. Para cambiar el texto, edita TRADUCCIONES en ese script. -->", 1)

    problemas = revisar(html) + revisar_identificadores(
        FUENTE.read_text(encoding="utf-8"), html)

    if sin_usar:
        print(f"AVISO -- {len(sin_usar)} traduccion(es) que ya no calzan "
              "(el informe cambio; revisa si sobran o si el texto es otro):")
        for x in sin_usar[:12]:
            print("   ", x[:100])
    if problemas:
        print(f"\nERROR -- queda texto en espanol sin traducir ({len(problemas)}):",
              file=sys.stderr)
        for x in problemas[:25]:
            print("   ", x, file=sys.stderr)
        print("\nAgregalos a TRADUCCIONES y vuelve a correr. No se escribio nada.",
              file=sys.stderr)
        return 1

    print("OK: sin texto en espanol pendiente.")
    if not args.aplicar:
        print(f"Corre con --aplicar para escribir {DESTINO}.")
        return 0

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(html, encoding="utf-8")
    print(f"escrito {DESTINO} ({len(html)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
