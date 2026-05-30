// URL del CSV Público
const CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDYehI-fc0b4CF4kVwykzGfnw5ePTfwHPmAlPSTsa0_cO534reW8_weCAm1J6igsird8qGi-PngLUL/pub?gid=1191075907&single=true&output=csv';

// Elementos del DOM
const container = document.getElementById('ranking-container');
const title = document.getElementById('title');
const subtitle = document.getElementById('subtitle');
const mainView = document.getElementById('main-view');

// Elementos de la Tarjeta
const overlay = document.getElementById('details-overlay');
const cardTeam = document.getElementById('card-team');
const cardQuote = document.getElementById('card-quote');
const cardMembers = document.getElementById('card-members');

// Panel
const panel = document.getElementById('control-panel');
const btnPlay = document.getElementById('btn-play');
const btnPause = document.getElementById('btn-pause');
const btnReset = document.getElementById('btn-reset');
const speedInput = document.getElementById('speed');
const speedVal = document.getElementById('speed-val');

// Variable global para la línea de tiempo principal
let tl;
let teamChart;
let historicalData = {};
const HISTORICAL_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDYehI-fc0b4CF4kVwykzGfnw5ePTfwHPmAlPSTsa0_cO534reW8_weCAm1J6igsird8qGi-PngLUL/pub?gid=371527432&single=true&output=csv';

async function init() {
  try {
    // 1. Fetch de datos
    const response = await fetch(CSV_URL);
    const text = await response.text();
    
    // 2. Parsear CSV básico (ignoramos header)
    const lines = text.trim().split('\n').slice(1);
    const top5 = lines.slice(0, 5).map(line => {
      const cols = line.split(',');
      return {
        posicion: cols[1]?.trim() || '',
        equipo: cols[2]?.trim() || '',
        puntaje: cols[3]?.trim() || '',
        retorno: cols[4]?.trim() || ''
      };
    });

    // 3. Renderizar filas
    container.innerHTML = '';
    top5.forEach((team) => {
      const isPositive = !team.retorno.startsWith('-');
      const returnText = isPositive ? `+${team.retorno.replace('+', '')}` : team.retorno;
      const returnClass = isPositive ? 'return-positive' : 'return-negative';

      const row = document.createElement('div');
      row.className = 'ranking-row';
      row.dataset.rank = team.posicion;
      row.innerHTML = `
        <div class="rank-number">${team.posicion}</div>
        <div class="team-info">
          <div class="team-name">${team.equipo}</div>
          <div class="team-stats">
            <div class="team-score">${team.puntaje}</div>
            <div class="team-return ${returnClass}">${returnText}</div>
          </div>
        </div>
      `;
      container.appendChild(row);
    });

    // Fetch datos históricos para el gráfico
    try {
      const histResponse = await fetch(HISTORICAL_CSV_URL);
      const histText = await histResponse.text();
      const histLines = histText.trim().split('\n');
      if (histLines.length > 0) {
        const headers = histLines[0].split(',').map(h => h.trim());
        historicalData.labels = [];
        historicalData.teams = {};
        for (let i = 1; i < headers.length; i++) {
          if (headers[i]) historicalData.teams[headers[i]] = [];
        }
        for (let i = 1; i < histLines.length; i++) {
          const cols = histLines[i].split(',');
          if (cols[0]) {
            historicalData.labels.push(cols[0].trim());
            for (let j = 1; j < headers.length; j++) {
              if (headers[j]) {
                const val = parseFloat(cols[j]);
                historicalData.teams[headers[j]].push(isNaN(val) ? null : val);
              }
            }
          }
        }
      }
    } catch (e) {
      console.error("Error al cargar historial", e);
    }

    // Inicializar Chart.js
    const ctx = document.getElementById('team-chart').getContext('2d');
    teamChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: historicalData.labels || [],
        datasets: [{
          label: 'Retorno',
          data: [],
          borderColor: '#098551',
          borderWidth: 3,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 4,
          fill: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { 
          legend: { display: false },
          tooltip: { mode: 'index', intersect: false }
        },
        scales: {
          x: { 
            display: true, 
            grid: { display: false },
            border: { display: false },
            ticks: { color: '#8A919E', font: { size: 10 } }
          },
          y: { 
            display: true,
            min: 0,
            max: 10,
            border: { display: false },
            grid: { color: '#EAECEF' },
            ticks: { 
              stepSize: 1, 
              color: '#8A919E', 
              font: { size: 10 },
              callback: function(value) { return value + '%'; }
            }
          }
        },
        layout: {
          padding: 10
        }
      },
      plugins: [{
        beforeDraw: (chart) => {
          const ctx = chart.ctx;
          const dataset = chart.data.datasets[0];
          ctx.save();
          ctx.shadowColor = dataset.borderColor;
          ctx.shadowBlur = 12;
          ctx.shadowOffsetX = 0;
          ctx.shadowOffsetY = 4;
        },
        afterDraw: (chart) => {
          chart.ctx.restore();
        }
      }]
    });

    // 4. Iniciar Animación
    startAnimation(top5);

  } catch (error) {
    console.error("Error cargando el ranking:", error);
    container.innerHTML = '<div style="color:white;text-align:center;font-size:24px;">Error al cargar datos en vivo.</div>';
  }
}

function startAnimation(top5) {
  const rows = document.querySelectorAll('.ranking-row');
  const totalTeams = top5.length;
  
  // Configuración inicial de GSAP
  gsap.set([title, subtitle], { opacity: 0, y: -30 });
  gsap.set(rows, { opacity: 0, y: 30 });
  gsap.set(overlay, { opacity: 0, pointerEvents: 'none' });
  gsap.set(mainView, { scale: 1, y: 0, transformOrigin: "center top" });

  // Timeline (30 segundos)
  tl = gsap.timeline({ repeat: -1 });

  // === FASE 1: VISTA GENERAL Y BARRIDO (0-5s) ===
  tl.to([title, subtitle], { opacity: 1, y: 0, duration: 1, stagger: 0.2, ease: 'power3.out' }, 0);
  tl.to(rows, { opacity: 1, y: 0, duration: 1, stagger: 0.15, ease: 'power3.out' }, 0.5);
  
  // Paneo muy lento para dar vida (eliminado por solicitud)
  // tl.to(mainView, { y: -20, duration: 4.5, ease: 'sine.inOut' }, 0.5);

  // === FASE 2: FOCO SECUENCIAL (5-25s) ===
  // 5 posiciones x 4 segundos cada una = 20 segundos
  top5.forEach((team, index) => {
    const startTime = 5 + (index * 4);
    
    // Encontrar datos del JSON
    const details = window.TEAM_MEMBERS ? window.TEAM_MEMBERS[team.equipo] : null;
    const membersHTML = details?.members?.map((m, i) => {
      const photoHtml = m.photo ? `<img class="member-photo" src="../torneo-app/public${m.photo}" alt="${m.name}" />` : `<img class="member-photo" src="./default-avatar.png" alt="${m.name}" />`;
      return `
      <div class="member-item">
        ${photoHtml}
        <div class="member-role">${i === 0 ? 'Líder' : 'Integrante'}</div>
        <div class="member-name">${m.name}</div>
      </div>
    `}).join('') || '<div class="member-item"><div class="member-name">Datos no disponibles</div></div>';
    
    const quoteText = details?.quote || `"Enfocados en el Alfa"`;
    const isPositive = !team.retorno.startsWith('-');
    const returnText = isPositive ? `+${team.retorno.replace('+', '')}` : team.retorno;
    const returnClass = isPositive ? 'fin-value-tr return-positive' : 'fin-value-tr return-negative';

    // 1. Preparar la tarjeta ANTES de mostrarla
    tl.call(() => {
      document.getElementById('card-team').innerHTML = `<span style="color: #0052FF; margin-right: 8px;">#${team.posicion}</span>${team.equipo}`;
      document.getElementById('card-score').textContent = team.puntaje;
      const cardReturnEl = document.getElementById('card-return');
      cardReturnEl.textContent = returnText;
      cardReturnEl.className = returnClass;
      document.getElementById('card-quote').textContent = quoteText;
      document.getElementById('card-members').innerHTML = membersHTML;

      // Actualizar Gráfico
      let teamData = historicalData.teams && historicalData.teams[team.equipo] ? historicalData.teams[team.equipo].filter(v => v !== null) : [];
      let chartLabels = ["May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov"];

      // Si no hay datos, usar el retorno actual en el primer mes (Mayo)
      if (teamData.length === 0) {
        teamData = [parseFloat(team.retorno) || 0];
      }

      teamChart.data.labels = chartLabels;
      teamChart.data.datasets[0].data = teamData;
      teamChart.data.datasets[0].borderColor = isPositive ? '#098551' : '#CF2030';
      teamChart.data.datasets[0].pointBackgroundColor = isPositive ? '#098551' : '#CF2030';
      // Si solo hay 1 dato (ej. Mayo), mostrar el punto porque una línea de 1 dato no se dibuja
      teamChart.data.datasets[0].pointRadius = teamData.length === 1 ? 4 : 0;
      teamChart.update();

      // Actualizar el Badge del Gráfico
      const chartBadge = document.getElementById('chart-badge');
      if (chartBadge) {
        chartBadge.textContent = returnText;
        chartBadge.style.color = isPositive ? '#098551' : '#CF2030';
        chartBadge.style.background = isPositive ? 'rgba(9,133,81,0.1)' : 'rgba(207,32,48,0.1)';
      }
    }, [], startTime - 0.1);

    // 2. Efecto de Zoom de cámara sobre el contenedor principal
    // Calculamos qué tanto bajar la tabla para centrar la fila
    const rowOffset = 100 * index; 
    tl.to(mainView, {
      scale: 1.15,
      y: -rowOffset,
      duration: 1.5,
      ease: 'power3.inOut'
    }, startTime);

    // Atenuar la tabla general para dar protagonismo a la tarjeta
    tl.to([title, subtitle, ...rows], {
      opacity: 0.15,
      filter: 'blur(4px)',
      duration: 1,
      ease: 'power2.inOut'
    }, startTime);

    // 3. Mostrar el Overlay y Tarjeta
    tl.to(overlay, {
      opacity: 1,
      duration: 1,
      ease: 'power2.out'
    }, startTime + 0.5);

    // Animación interna de la tarjeta
    tl.fromTo('.details-card', 
      { scale: 0.9, y: 30 }, 
      { scale: 1, y: 0, duration: 1, ease: 'back.out(1.5)' }, 
    startTime + 0.5);

    // 4. Ocultar la tarjeta antes del siguiente
    if (index < totalTeams - 1) {
      tl.to(overlay, {
        opacity: 0,
        duration: 0.8,
        ease: 'power2.in'
      }, startTime + 3.2);
    }
  });

  // Ocultar el último overlay
  tl.to(overlay, { opacity: 0, duration: 0.8, ease: 'power2.in' }, 25 - 0.8);

  // === FASE 3: CIERRE (25-30s) ===
  tl.addLabel("cierre", 25);
  
  // Pull-back rápido
  tl.to(mainView, {
    scale: 1,
    y: 0,
    duration: 1.5,
    ease: 'power4.inOut'
  }, "cierre");

  // Restaurar tabla
  tl.to([title, subtitle, ...rows], {
    opacity: 1,
    filter: 'blur(0px)',
    duration: 1.5,
    ease: 'power3.inOut'
  }, "cierre");

  // Fade out final suave para que el loop sea impecable
  tl.to([title, subtitle, ...rows], {
    opacity: 0,
    duration: 1,
    ease: 'power2.inOut'
  }, 29);
}

// ==== CONTROLES DE OBS ====
document.addEventListener('keydown', (e) => {
  if (e.key.toLowerCase() === 'h') {
    panel.classList.toggle('hidden');
  }
});

btnPlay.addEventListener('click', () => tl && tl.play());
btnPause.addEventListener('click', () => tl && tl.pause());
btnReset.addEventListener('click', () => tl && tl.restart());
speedInput.addEventListener('input', (e) => {
  const val = e.target.value;
  speedVal.textContent = val + 'x';
  if (tl) tl.timeScale(parseFloat(val));
});

// Arrancar
init();
