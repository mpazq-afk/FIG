/**
 * verificar_menu_movil.js -- Abre el MENU MOVIL y comprueba que se alcance entero.
 *
 * Por que existe
 * ---------------
 * `verificar_movil.js` mide la PAGINA, pero nunca abre el menu hamburguesa, asi
 * que un menu roto no lo veia nadie. Y estaba roto: `.m-menu` era un flex
 * `justify-content:center` SIN scroll, y cuando la lista pasaba del alto de la
 * pantalla los PRIMEROS items quedaban con offset negativo -- fuera del
 * viewport y sin barra que arrastrar. Medido el 2026-08-31 sobre lo que estaba
 * publicado: en un iPhone SE (375x667) "Nosotros" y "Torneo 2026" eran
 * inalcanzables. Nadie lo habia notado porque en un telefono grande entraba
 * justo. Se arreglo con flex-start + margenes automaticos en los extremos.
 *
 * Que mide, en tres telefonos (390x844, 375x667, 360x640):
 *   1. Alto del contenido del menu contra el alto de la pantalla.
 *   2. Si el contenedor puede scrollear cuando no entra.
 *   3. Que enlace queda con offset negativo, es decir, inalcanzable.
 *
 * Correrlo cada vez que se agregue o saque un enlace del menu movil.
 *
 * Uso:
 *   python -m http.server 8000        # en otra terminal
 *   node verificar_menu_movil.js [--port=8000] [--pag=index.html]
 */
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const ARGS = Object.fromEntries(process.argv.slice(2).map((a) => {
  const [k, v] = a.replace(/^--/, "").split("=");
  return [k, v === undefined ? true : v];
}));
const PORT = ARGS.port || 8000;
const DEPURACION = 9333;
const REPO = ARGS.repo || process.cwd();

// Tres telefonos reales: uno normal, uno chico y uno muy chico.
const PANTALLAS = [
  { nombre: "iPhone 14 / Pixel", ancho: 390, alto: 844 },
  { nombre: "iPhone SE",         ancho: 375, alto: 667 },
  { nombre: "Galaxy S8 / chico", ancho: 360, alto: 640 },
];

const CHROME_POSIBLES = [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  path.join(process.env.LOCALAPPDATA || "", "Google\\Chrome\\Application\\chrome.exe"),
];
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const chrome = CHROME_POSIBLES.find((p) => p && fs.existsSync(p));
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
    `--user-data-dir=${path.join(require("os").tmpdir(), "fig-menu-perfil")}`,
    "--no-first-run", "--window-size=390,844", "about:blank",
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
  const enviar = (method, params = {}) => new Promise((res) => {
    const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
  });
  const evaluar = async (expression) => {
    const r = await enviar("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
    return r.result?.result?.value;
  };

  await enviar("Runtime.enable");
  await enviar("Page.enable");

  let malas = 0;
  for (const p of PANTALLAS) {
    await enviar("Emulation.setDeviceMetricsOverride", {
      width: p.ancho, height: p.alto, deviceScaleFactor: 3, mobile: true,
    });
    await enviar("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
    await enviar("Page.navigate", { url: `http://localhost:${PORT}/${ARGS.pag || "index.html"}?v=${Date.now()}` });
    await dormir(1600);

    const r = await evaluar(`(() => {
      const m = document.getElementById("mmenu");
      if (!m) return { error: "no existe #mmenu" };
      m.classList.add("open");
      const cs = getComputedStyle(m);
      const enlaces = [...m.querySelectorAll("a")];
      const caja = m.getBoundingClientRect();
      // Alcanzable = su caja cae dentro del area visible del menu una vez
      // scrolleado hasta el, contando que el contenedor puede scrollear.
      const alcanzable = (el) => {
        const t = el.offsetTop, h = el.offsetHeight;
        return t >= 0 && (t + h) <= m.scrollHeight + 1;
      };
      const fuera = enlaces.filter((a) => !alcanzable(a)).map((a) => a.textContent.trim());
      return {
        enlaces: enlaces.length,
        alto_contenido: m.scrollHeight,
        alto_visible: m.clientHeight,
        scrollea: m.scrollHeight > m.clientHeight + 1,
        overflowY: cs.overflowY,
        justify: cs.justifyContent,
        primero: enlaces[0]?.textContent.trim(),
        ultimo: enlaces[enlaces.length - 1]?.textContent.trim(),
        fuera,
      };
    })()`);

    if (r.error) { console.log(`  ${p.nombre}: ${r.error}`); malas++; continue; }
    const estado = r.fuera.length ? "PROBLEMA" : "ok      ";
    console.log(`  ${estado} ${p.nombre.padEnd(20)} ${p.ancho}x${p.alto}`);
    console.log(`           ${r.enlaces} enlaces · contenido ${r.alto_contenido}px / pantalla ${r.alto_visible}px`
      + ` · ${r.scrollea ? "SCROLLEA" : "entra entero"} (overflow-y:${r.overflowY})`);
    console.log(`           primero "${r.primero}" · ultimo "${r.ultimo}"`);
    if (r.fuera.length) {
      console.log(`           INALCANZABLES: ${r.fuera.join(", ")}`);
      malas++;
    }
  }

  ws.close(); proc.kill();
  console.log(malas ? `\n${malas} pantalla(s) con items inalcanzables.`
                    : "\nEl menu es alcanzable entero en las tres pantallas.");
  process.exit(malas ? 1 : 0);
}
main();
