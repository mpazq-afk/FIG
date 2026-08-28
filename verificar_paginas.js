#!/usr/bin/env node
/*
 * verificar_paginas.js -- Abre todas las paginas del sitio en Chrome y falla si
 * alguna tira un error de consola o pide un archivo que no existe.
 *
 * Por que existe
 * ---------------
 * verificar_sitio.py revisa los DATOS (JSON que parsean, derivados al dia,
 * numeros que calzan). Nada revisaba las PAGINAS. El bug de la seccion de
 * creadores -- que quedaba invisible por una politica de cache -- lo descubrio
 * Francisco probando a mano, dias despues de publicarlo. Esto lo habria cazado
 * el mismo dia.
 *
 * Maneja el Chrome instalado por CDP crudo (WebSocket y fetch nativos de Node),
 * sin Playwright ni Puppeteer -- mismo patron que
 * grabar_pantalla_facultad_1_capturar.js y generar_og_equipos.js.
 *
 * LOS 404 QUE NO SON ERRORES
 * ---------------------------
 * Este sitio detecta fotos y logos SONDEANDO: prueba <slug>.jpg, .jpeg, .png,
 * .webp hasta que uno carga, y prueba fotos/eventos/<evento>/1.jpg, 2.jpg...
 * hasta que falla. O sea que los 404 de esas rutas son el mecanismo funcionando,
 * no una falla -- por eso van en RUTAS_SONDEADAS. Si se marcaran como error, el
 * chequeo daria rojo siempre y se volveria ruido que nadie mira.
 *
 * Uso:
 *   1) En otra terminal, desde la raiz del repo:
 *        python -m http.server 8000
 *   2) node verificar_paginas.js
 *      Flags:
 *        --port=8000    puerto del server local
 *        --espera=4500  ms a esperar por pagina antes de revisar
 *        --peso=300     limite de peso CRITICO por pagina en KB (avisa, no falla)
 *
 * El limite se mide sobre el peso CRITICO -- documento, CSS, JS, fuentes y JSON
 * --, no sobre el total. Las fotos quedan fuera a proposito: index.html y
 * eventos/index.html pasan de los 2 MB por las tiras de fotos de eventos, y
 * meterlas en el presupuesto haria que el aviso saltara siempre y dejara de
 * mirarse. Lo que este umbral cuida es que el HTML monolitico de cada pagina no
 * se vaya de las manos.
 *
 * Sale con 1 si encuentra errores de consola o 404 que no sean sondeos.
 */

const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const ARGS = Object.fromEntries(
  process.argv.slice(2).map((a) => {
    const [k, v] = a.replace(/^--/, "").split("=");
    return [k, v === undefined ? true : v];
  })
);
const PORT = ARGS.port || 8000;
const ESPERA = parseInt(ARGS.espera || "4500", 10);
const PESO_KB = parseInt(ARGS.peso || "300", 10);
const DEPURACION = 9423;

// Rutas donde un 404 es el mecanismo de deteccion, no un error. Ver arriba.
const RUTAS_SONDEADAS = [/\/fotos\//, /\/logos\/industria\//];

const CHROME_POSIBLES = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  process.env.CHROME,
].filter(Boolean);

const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

/** Todas las paginas del sitio, mas UNA micro-pagina de equipo de muestra. */
function paginas(raiz) {
  const fuera = new Set(["MAPA_CONTENIDO_FIG.html"]);
  const lista = [];
  (function recorrer(dir) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.name === ".git" || e.name === "node_modules") continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) {
        // las 54 micro-paginas son identicas salvo los datos: basta una
        if (path.relative(raiz, p).replace(/\\/g, "/") === "torneo/e") {
          const una = fs.readdirSync(p).find((f) => f.endsWith(".html"));
          if (una) lista.push("torneo/e/" + una);
          continue;
        }
        recorrer(p);
      } else if (e.name.endsWith(".html") && !fuera.has(e.name)) {
        lista.push(path.relative(raiz, p).replace(/\\/g, "/"));
      }
    }
  })(raiz);
  return lista.sort();
}

async function main() {
  const raiz = __dirname;
  const chrome = CHROME_POSIBLES.find((p) => fs.existsSync(p));
  if (!chrome) { console.error("No encontre chrome.exe. Pasalo con la variable CHROME."); process.exit(1); }
  try {
    const r = await fetch(`http://localhost:${PORT}/index.html`);
    if (!r.ok) throw new Error(String(r.status));
  } catch {
    console.error(`No responde http://localhost:${PORT}. Levanta el server local primero:`);
    console.error("    python -m http.server " + PORT);
    process.exit(1);
  }

  const proc = spawn(chrome, [
    "--headless=new", "--disable-gpu", `--remote-debugging-port=${DEPURACION}`,
    `--user-data-dir=${path.join(require("os").tmpdir(), "fig-verif-perfil")}`,
    "--no-first-run", "--window-size=1400,1400", "about:blank",
  ], { stdio: "ignore" });

  let target = null;
  for (let i = 0; i < 80 && !target; i++) {
    try {
      const tabs = await (await fetch(`http://127.0.0.1:${DEPURACION}/json/list`)).json();
      target = tabs.find((t) => t.type === "page");
    } catch { /* aun no levanta */ }
    if (!target) await dormir(250);
  }
  if (!target) { console.error("Chrome no abrio su puerto de depuracion."); proc.kill(); process.exit(1); }

  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res) => ws.addEventListener("open", res));
  let id = 0;
  const pend = new Map();
  let consola = [];
  let fallidos = [];
  ws.addEventListener("message", (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
    if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error")
      consola.push("console.error: " + m.params.args.map((a) => a.value ?? a.description).join(" "));
    if (m.method === "Runtime.exceptionThrown")
      consola.push("excepcion: " + (m.params.exceptionDetails.exception?.description
        || m.params.exceptionDetails.text));
    if (m.method === "Network.responseReceived") {
      const { status, url } = m.params.response;
      if (status >= 400 && !RUTAS_SONDEADAS.some((re) => re.test(url))) fallidos.push(status + " " + url);
    }
  });
  const enviar = (method, params = {}) =>
    new Promise((res) => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  const evaluar = async (expression) => {
    const r = await enviar("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
    return r.result?.result?.value;
  };

  await enviar("Runtime.enable");
  await enviar("Page.enable");
  await enviar("Network.enable");

  const lista = paginas(raiz);
  console.log(`Revisando ${lista.length} paginas en http://localhost:${PORT} ...\n`);

  let conProblemas = 0;
  const pesados = [];
  for (const pag of lista) {
    consola = []; fallidos = [];
    // el ?v= evita que Chrome sirva una version cacheada de una corrida anterior
    await enviar("Page.navigate", { url: `http://localhost:${PORT}/${pag}?v=${Date.now()}${id}` });
    await dormir(ESPERA);

    const medida = await evaluar('(function(){'
      + 'var rs=performance.getEntriesByType("resource")'
      + '  .concat(performance.getEntriesByType("navigation"));'
      + 'var total=0,critico=0;'
      + 'rs.forEach(function(r){'
      + '  var b=r.transferSize||0; total+=b;'
      /* imagen y video no entran en el presupuesto critico */
      + '  if(!/[.](jpe?g|png|webp|gif|svg|avif|mp4|webm|ico)([?]|$)/i.test(r.name))critico+=b;'
      + '});'
      + 'return JSON.stringify({total:Math.round(total/1024),critico:Math.round(critico/1024)});'
      + '})()');
    const { total: kb, critico } = JSON.parse(medida || '{"total":0,"critico":0}');
    if (critico > PESO_KB) pesados.push(`${pag}: ${critico} KB criticos (${kb} KB en total)`);

    const problemas = consola.concat(fallidos);
    if (problemas.length) {
      conProblemas++;
      console.log(`  FALLA  ${pag}  (${critico} KB criticos / ${kb} KB total)`);
      for (const p of problemas.slice(0, 6)) console.log(`           ${p}`);
      if (problemas.length > 6) console.log(`           ... y ${problemas.length - 6} mas`);
    } else {
      console.log(`  ok     ${pag}  (${critico} KB criticos / ${kb} KB total)`);
    }
  }

  if (pesados.length) {
    console.log(`\nAVISO -- por encima de ${PESO_KB} KB criticos (las imagenes no cuentan).`);
    console.log(`Son un TECHO: python -m http.server no comprime y GitHub Pages si,`);
    console.log(`asi que en produccion cada pagina pesa bastante menos que esto.`);
    for (const p of pesados) console.log(`  ${p}`);
  }

  console.log();
  ws.close(); proc.kill();
  if (conProblemas) {
    console.log(`${conProblemas} de ${lista.length} paginas con problemas. No publiques asi.`);
    process.exit(1);
  }
  console.log(`Las ${lista.length} paginas cargan sin errores de consola ni archivos faltantes.`);
  process.exit(0);
}

main().catch((e) => { console.error(e); process.exit(1); });
