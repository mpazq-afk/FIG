#!/usr/bin/env node
/*
 * generar_og_equipos.js
 *
 * Genera una imagen de vista previa por equipo (og/equipo-<id>.jpg, 1200x627)
 * para las micro-paginas torneo/e/<id>.html que escribe
 * generar_paginas_equipo.py. Es lo que se ve cuando alguien pega el link de su
 * equipo en LinkedIn, WhatsApp o Slack.
 *
 * No dibuja nada nuevo: reutiliza la MISMA tarjeta de LinkedIn que ya ofrece la
 * pagina en "Comparte tu resultado" (drawLi, 1200x627 -- justo la medida que
 * piden las vistas previas). Se llega a ella por el gancho window.__figCards
 * que torneo/index.html ya exponia. O sea: la vista previa y la imagen que el
 * equipo se descarga son la misma pieza, y si se rediseña una cambia la otra.
 *
 * Maneja el Chrome instalado en la maquina por su protocolo de depuracion
 * (CDP), con el WebSocket y el fetch nativos de Node -- sin Playwright ni
 * Puppeteer, mismo patron "CDP crudo" que grabar_pantalla_facultad_1_capturar.js.
 *
 * Uso:
 *   1) Desde la raiz de fig-web, en OTRA terminal:
 *        python -m http.server 8000
 *      (hace falta: la pagina hace fetch() a ../datos/torneo.json, que el
 *      navegador bloquea si se abre como archivo suelto file://)
 *   2) node generar_og_equipos.js
 *      Flags:
 *        --port=8000     puerto del server local
 *        --out=og        carpeta donde deja los .jpg
 *        --calidad=0.82  calidad JPEG (0-1). Ver la nota de PESO mas abajo.
 *        --solo=id1,id2  genera solo esos equipos (util para probar)
 *
 * PESO -- leer antes de meter esto en la rutina semanal:
 * son ~55 imagenes que se REESCRIBEN cada corte, y git guarda cada version.
 * A 0.82 de calidad cada una ronda los 60-90 KB, o sea ~4 MB por corte y unos
 * 90 MB de historia a lo largo del torneo. Si eso incomoda, generar_paginas_equipo.py
 * corre igual sin imagenes: cada micro-pagina cae a la imagen del sitio
 * (/og-image.png) y conserva lo que de verdad diferencia una vista previa de
 * otra, que es el TITULO ("Beta capital - 1° de 54"). Por eso las imagenes son
 * un paso aparte y opcional, no parte de generar_paginas_equipo.py.
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
const OUT = path.resolve(ARGS.out || "og");
const CALIDAD = parseFloat(ARGS.calidad || "0.82");
const SOLO = ARGS.solo ? String(ARGS.solo).split(",") : null;
const DEPURACION = 9422;

const CHROME_POSIBLES = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  process.env.CHROME,
].filter(Boolean);

const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const chrome = CHROME_POSIBLES.find((p) => fs.existsSync(p));
  if (!chrome) {
    console.error("No encontre chrome.exe. Pasalo con la variable CHROME.");
    process.exit(1);
  }
  try {
    const r = await fetch(`http://localhost:${PORT}/datos/torneo.json`);
    if (!r.ok) throw new Error(String(r.status));
  } catch {
    console.error(`No responde http://localhost:${PORT}. Levanta el server local primero:`);
    console.error("    python -m http.server " + PORT);
    process.exit(1);
  }

  fs.mkdirSync(OUT, { recursive: true });

  const proc = spawn(chrome, [
    "--headless=new",
    "--disable-gpu",
    `--remote-debugging-port=${DEPURACION}`,
    `--user-data-dir=${path.join(require("os").tmpdir(), "fig-og-perfil")}`,
    "--no-first-run",
    "--window-size=1400,1000",
    "about:blank",
  ], { stdio: "ignore" });

  let target = null;
  for (let i = 0; i < 80 && !target; i++) {
    try {
      const tabs = await (await fetch(`http://127.0.0.1:${DEPURACION}/json/list`)).json();
      target = tabs.find((t) => t.type === "page");
    } catch { /* todavia no levanta */ }
    if (!target) await dormir(250);
  }
  if (!target) { console.error("Chrome no abrio su puerto de depuracion."); proc.kill(); process.exit(1); }

  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res) => ws.addEventListener("open", res));
  let id = 0;
  const pend = new Map();
  ws.addEventListener("message", (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  });
  const enviar = (method, params = {}) =>
    new Promise((res) => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  const evaluar = async (expression) => {
    const r = await enviar("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
    if (r.result?.exceptionDetails) {
      throw new Error(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text);
    }
    return r.result?.result?.value;
  };

  await enviar("Runtime.enable");
  await enviar("Page.enable");
  await enviar("Page.navigate", { url: `http://localhost:${PORT}/torneo/index.html` });

  // esperar a que la pagina tenga datos REALES (no el modo demo) y sus logos
  let listo = false;
  for (let i = 0; i < 60 && !listo; i++) {
    await dormir(500);
    try { listo = await evaluar('!!(window.__figCards && !window.__figCards.data().demo)'); } catch { /* aun cargando */ }
  }
  if (!listo) {
    console.error("La pagina no cargo datos reales de torneo.json (¿esta en modo demo?).");
    ws.close(); proc.kill(); process.exit(1);
  }
  // el historial se carga aparte (ver torneo/index.html): sin el, la tarjeta
  // sale con el cartel de "trayectoria disponible desde la semana N"
  await evaluar('window.__figCards.conHistorial()');
  await evaluar('window.__figCards.loadLogos().then(function(){return document.fonts.ready})');

  const equipos = await evaluar('JSON.stringify(window.__figCards.data().equipos.map(function(e){return {id:e.id,nombre:e.nombre,posicion:e.posicion}}))');
  const lista = JSON.parse(equipos).filter((e) => !SOLO || SOLO.includes(e.id));
  console.log(`Generando ${lista.length} imagenes en ${path.relative(process.cwd(), OUT) || OUT}/ ...`);

  let total = 0;
  for (const eq of lista) {
    // se dibuja en un canvas suelto, del mismo modo que el boton "Imagen LinkedIn"
    const dataUri = await evaluar(`(function(){
      var D=window.__figCards.data();
      var t=D.equipos.filter(function(x){return x.id===${JSON.stringify(eq.id)}})[0];
      if(!t)return null;
      var cv=document.createElement("canvas");cv.width=1200;cv.height=627;
      window.__figCards.drawLi(cv.getContext("2d"),t,1,1);
      return cv.toDataURL("image/jpeg",${CALIDAD});
    })()`);
    if (!dataUri) { console.warn(`  ! ${eq.id}: no pude dibujarlo`); continue; }
    const buf = Buffer.from(dataUri.split(",")[1], "base64");
    fs.writeFileSync(path.join(OUT, `equipo-${eq.id}.jpg`), buf);
    total += buf.length;
    process.stdout.write(`  ${String(eq.posicion).padStart(3)}. ${eq.id} (${(buf.length / 1024).toFixed(0)} KB)\n`);
  }

  console.log(`\nOK: ${lista.length} imagenes, ${(total / 1024 / 1024).toFixed(1)} MB en total.`);
  console.log("Ahora corre:  python generar_paginas_equipo.py");
  ws.close(); proc.kill(); process.exit(0);
}

main().catch((e) => { console.error(e); process.exit(1); });
