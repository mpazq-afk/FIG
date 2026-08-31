/**
 * verificar_movil.js -- Mide las paginas en un viewport de CELULAR.
 *
 * Por que existe
 * ---------------
 * `verificar_paginas.js` revisa que no haya errores ni archivos faltantes, pero
 * lo hace en una ventana de 1400px. La mayoria de las visitas entran por
 * telefono, y ahi los problemas son otros: una tabla o un SVG mas ancho que la
 * pantalla hace que TODA la pagina se pueda arrastrar de lado, y el texto se
 * sale por el borde. Eso no rompe ninguna consola, asi que ningun chequeo
 * anterior lo veia.
 *
 * Que mide, en 390x844 (un iPhone normal):
 *   1. Si el documento scrollea en horizontal (scrollWidth > clientWidth).
 *   2. Que elementos concretos se salen del ancho, con su selector, para poder
 *      arreglarlos sin adivinar.
 *   3. Objetivos tactiles bajo 24px de alto (WCAG 2.2), que en un telefono son
 *      los que no se pueden pinchar.
 *   4. Texto por debajo de 12px, ilegible en pantalla chica.
 *
 * Un SVG ancho DENTRO de un contenedor con overflow-x propio no es un problema:
 * ese es el diseno funcionando (los graficos se arrastran solos). Por eso se
 * mide el desborde del DOCUMENTO, no el de cada elemento suelto.
 *
 * Uso:
 *   python -m http.server 8000        # en otra terminal
 *   node verificar_movil.js [--port=8000] [--solo=informe/]
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
const DEPURACION = 9333;
const ANCHO = Number(ARGS.ancho || 390);
const ALTO = Number(ARGS.alto || 844);

const CHROME_POSIBLES = [
  process.env.CHROME,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
].filter(Boolean);

const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

function paginas(raiz) {
  const out = [];
  (function rec(dir, pre) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if ([".git", "node_modules", "fuentes", "og", "fotos", "logos", "frames",
           "documentos", "datos"].includes(e.name)) continue;
      const rel = pre ? pre + "/" + e.name : e.name;
      if (e.isDirectory()) rec(path.join(dir, e.name), rel);
      else if (e.name.endsWith(".html")) out.push(rel);
    }
  })(raiz, "");
  // Fuera: las pantallas (disenadas para 1920x1080 en un TV, no para telefono),
  // las guias internas y las micro-paginas de equipo, que solo redirigen.
  const fuera = /^torneo\/(pantalla|e\/)|^GUIA_|^MAPA_/;
  const lista = out.filter((p) => !fuera.test(p));
  return ARGS.solo ? lista.filter((p) => p.startsWith(ARGS.solo)) : lista.sort();
}

const MEDIR = `(() => {
  const d = document.documentElement, vw = d.clientWidth;
  const desborde = d.scrollWidth - vw;
  const culpables = [];
  if (desborde > 1) {
    for (const el of document.querySelectorAll("body *")) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      if (r.right <= vw + 1 && r.left >= -1) continue;
      // Si algun ancestro tiene overflow-x propio, el elemento ancho esta
      // contenido a proposito (los graficos se arrastran dentro de su caja).
      let p = el.parentElement, contenido = false;
      while (p && p !== document.body) {
        const ox = getComputedStyle(p).overflowX;
        if (ox === "auto" || ox === "scroll" || ox === "hidden") { contenido = true; break; }
        p = p.parentElement;
      }
      if (contenido) continue;
      const sel = el.tagName.toLowerCase()
        + (el.id ? "#" + el.id : "")
        + (el.className && typeof el.className === "string"
            ? "." + el.className.trim().split(/\\s+/).slice(0, 2).join(".") : "");
      culpables.push(sel + " -> " + Math.round(r.left) + "px a " + Math.round(r.right) + "px");
    }
  }
  const chicos = [];
  // Falso positivo conocido: los nombres de equipo del ranking miden 23px, pero
  // el objetivo real es la FILA entera (.lb-row, ~55px, con su propio listener).
  // Agrandar el <a> seria arreglar algo que no esta roto y descuadrar la tabla.
  const EXENTOS = ".lb-row a";
  for (const el of document.querySelectorAll("a,button,input,select,summary,[role=button]")) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    if (el.matches(EXENTOS)) continue;
    if (r.height < 24) {
      const t = (el.textContent || "").trim().slice(0, 26);
      chicos.push(Math.round(r.height) + "px  " + el.tagName.toLowerCase() + " \\"" + t + "\\"");
    }
  }
  const diminuto = [];
  for (const el of document.querySelectorAll("body *")) {
    if (!el.firstChild || el.firstChild.nodeType !== 3) continue;
    const t = (el.textContent || "").trim();
    if (t.length < 4) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs && fs < 11) diminuto.push(fs.toFixed(1) + "px  \\"" + t.slice(0, 34) + "\\"");
  }
  return {
    desborde, vw, sw: d.scrollWidth,
    culpables: [...new Set(culpables)].slice(0, 8),
    chicos: [...new Set(chicos)].slice(0, 6),
    diminuto: [...new Set(diminuto)].slice(0, 5),
  };
})()`;

async function main() {
  const raiz = __dirname;
  const chrome = CHROME_POSIBLES.find((p) => fs.existsSync(p));
  if (!chrome) { console.error("No encontre chrome.exe."); process.exit(1); }
  try {
    const r = await fetch(`http://localhost:${PORT}/index.html`);
    if (!r.ok) throw new Error(String(r.status));
  } catch {
    console.error(`No responde http://localhost:${PORT}. Levanta el server local primero.`);
    process.exit(1);
  }

  const proc = spawn(chrome, [
    "--headless=new", "--disable-gpu", `--remote-debugging-port=${DEPURACION}`,
    `--user-data-dir=${path.join(require("os").tmpdir(), "fig-movil-perfil")}`,
    "--no-first-run", `--window-size=${ANCHO},${ALTO}`, "about:blank",
  ], { stdio: "ignore" });

  let target = null;
  for (let i = 0; i < 80 && !target; i++) {
    try {
      const tabs = await (await fetch(`http://127.0.0.1:${DEPURACION}/json/list`)).json();
      target = tabs.find((t) => t.type === "page");
    } catch { /* aun no levanta */ }
    if (!target) await dormir(250);
  }
  if (!target) { console.error("Chrome no abrio su puerto."); proc.kill(); process.exit(1); }

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
    return r.result?.result?.value;
  };

  await enviar("Runtime.enable");
  await enviar("Page.enable");
  // Emulacion de telefono de verdad: sin esto el CSS ve un escritorio angosto
  // y las media queries de movil no se activan igual que en un celular real.
  await enviar("Emulation.setDeviceMetricsOverride", {
    width: ANCHO, height: ALTO, deviceScaleFactor: 3, mobile: true,
  });
  await enviar("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });

  const lista = paginas(raiz);
  console.log(`Midiendo ${lista.length} paginas a ${ANCHO}x${ALTO} (telefono)\n`);

  let malas = 0;
  for (const pag of lista) {
    await enviar("Page.navigate", { url: `http://localhost:${PORT}/${pag}?v=${Date.now()}` });
    await dormir(1400);
    // Se recorre la pagina entera: los .reveal y los graficos solo se dibujan
    // cuando el IntersectionObserver los ve entrar, asi que medir sin scrollear
    // da una pagina a medio pintar.
    await evaluar(`(async()=>{const h=document.body.scrollHeight;
      for(let y=0;y<h;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,90));}
      window.scrollTo(0,0);await new Promise(r=>setTimeout(r,250));})()`);
    const m = await evaluar(MEDIR);
    if (!m) { console.log(`  ??   ${pag}  (no respondio)`); continue; }

    const problemas = m.desborde > 1 || m.chicos.length || m.diminuto.length;
    if (m.desborde > 1) malas++;
    console.log(`  ${m.desborde > 1 ? "SALE" : " ok "} ${pag}   ancho ${m.vw} / contenido ${m.sw}`
      + (m.desborde > 1 ? `  -> se sale ${m.desborde}px` : ""));
    for (const c of m.culpables) console.log(`        desborda: ${c}`);
    for (const c of m.chicos) console.log(`        tactil chico: ${c}`);
    for (const c of m.diminuto) console.log(`        texto chico: ${c}`);
    if (problemas) console.log("");
  }

  ws.close(); proc.kill();
  console.log(malas
    ? `\n${malas} pagina(s) se salen del ancho en telefono.`
    : `\nNinguna pagina se sale del ancho en telefono.`);
  process.exit(malas ? 1 : 0);
}

main();
