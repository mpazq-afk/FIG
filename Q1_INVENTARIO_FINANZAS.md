# Q1 — Inventario del Material Finanzas (Completado)

**Fecha:** 2026-07-16  
**Fuente:** Carpeta `Finanzas-20260716T225443Z-1-001/Finanzas/` en Google Drive personal  
**Total de archivos:** 189 (153 PDFs + 22 DOCs + 11 XLSs + 3 PPTs)

---

## Resumen de contenido

| Carpeta (Ramo) | Archivos | PDFs | Docs | Excels | PPTs | Estado |
|---|---|---|---|---|---|---|
| **Finanzas I** | 70 | 61 | 8 | 1 | — | ✅ |
| **Finanzas II** | 45 | 35 | 2 | 8 | — | ✅ |
| **Intro a Finanzas** | 67 | 50 | 12 | 2 | 3 | ✅ |
| **APF** | 7 | 7 | — | — | — | ✅ |
| **TOTAL** | **189** | **153** | **22** | **11** | **3** | — |

---

## Ramos identificados

| Ramo | ID propuesto | Estado | Ubicación Drive |
|---|---|---|---|
| Finanzas I | `finanzas-i` | ✅ Existe en index.json | `Finanzas I/` |
| Finanzas II | `finanzas-ii` | 🆕 NUEVO | `Finanzas II/` |
| Intro a Finanzas | `intro-finanzas` | 🆕 NUEVO | `Intro a Finanzas/` |
| APF | `apf` | 🆕 NUEVO | `APF/` |

---

## Mapeo propuesto: Temas × Ramos

### Finanzas I (70 archivos)
**Contenido:** Valoración, modelos de portfolio, derivados básicos, casos reales (LATAM)

**Temas asignados:**
- `renta-variable` ✅ (existente)
- `renta-fija` ✅ (existente)
- `historia-mercados` ✅ (existente)

**Ejemplos de archivos:** Solucionario del Hull, Guía Futuros y Forward, Resumen Solemne, Ejercicios Opciones, CAPM & Modelo Índice, Ayudantías (40+)

---

### Finanzas II (45 archivos)
**Contenido:** Opciones avanzadas, futuros, derivados complejos, estrategias

**Temas asignados:**
- `renta-variable` ✅ (existente)
- `derivados-opciones` 🆕 (NUEVO)
- `derivados-futuros` 🆕 (NUEVO)

**Ejemplos de archivos:** Black-Scholes, Opciones binomiales, Estrategias de opciones, Put-Call, Replica de opciones, Letras Griegas (6 XLSXs de ejercicios)

---

### Intro a Finanzas (67 archivos)
**Contenido:** Conceptos fundamentales, matemáticas financieras, introducción a modelos

**Temas asignados:**
- `macroeconomia` ✅ (existente)
- `matematica-financiera` 🆕 (NUEVO)

**Ejemplos de archivos:** Pauta Solemne 1 Bonilla, Modelo de Dos Periodos, Matemáticas Financieras (AFP), Pensiones, Seguros (50+ PDFs educativos)

---

### APF — Análisis y Planificación Financiera (7 archivos)
**Contenido:** Casos reales (LATAM), riesgo de crédito, análisis de estados financieros

**Temas asignados:**
- `renta-fija` ✅ (existente)
- `riesgo-crediticio` 🆕 (NUEVO)

**Ejemplos de archivos:** Examen APF Otoño 2019, Solemne APF, Pauta Solemne 2 APF (todos con análisis de casos reales y riesgos)

---

## Cambios necesarios en `index.json`

### Ramos nuevos a agregar
```json
{
  "id": "finanzas-ii",
  "nombre": "Finanzas II"
},
{
  "id": "intro-finanzas",
  "nombre": "Introducción a Finanzas"
},
{
  "id": "apf",
  "nombre": "Análisis y Planificación Financiera"
}
```

### Temas nuevos a agregar
```json
{
  "id": "derivados-opciones",
  "nombre": "Derivados: Opciones"
},
{
  "id": "derivados-futuros",
  "nombre": "Derivados: Futuros"
},
{
  "id": "matematica-financiera",
  "nombre": "Matemática Financiera"
},
{
  "id": "riesgo-crediticio",
  "nombre": "Riesgo de Crédito"
}
```

---

## Notas importantes (Q2 en adelante)

1. **Excels ignorados:** Se encontraron 11 archivos XLS/XLSX. Como per instrucciones, no se procesarán para preguntas (son mayormente ejercicios con datos numéricos).

2. **Volumen de contenido:** 153 PDFs + 22 DOCs = 175 documentos de texto procesables. Es un volumen muy alto (colosal, como se esperaba).

3. **Calidad del material:** Mezcla de:
   - Solucionarios y pautas (muy valiosos para preguntas)
   - Apuntes de cátedra (contenido pedagógico)
   - Guías de ejercicios (buena fuente de distractores plausibles)
   - Casos reales (para historia-mercados)

4. **Recomendación de orden Q2:** Comenzar con `Intro a Finanzas` (contenido más estructurado pedagógicamente) → `Finanzas I` (volumen mayor, más diversidad de temas) → `Finanzas II` (especializado, derivados) → `APF` (casos complejos para revisión pedagógica final).

---

## Registro de archivos procesados (leer ANTES de escanear más, para no repetir)

**Pausa de sesión: 2026-07-17.** Antes de escanear más archivos, comparar
el `fileId` candidato contra las listas de abajo. Si ya aparece en
"extraídos" o "descartados", NO releerlo. Si aparece en "escaneados pero
sin extraer", es contenido ya leído y evaluado como bueno pero nunca usado
en un lote — se puede extraer directamente sin releer el Drive (buscar el
resumen de su contenido en el detalle de §3 de `HOJA_DE_RUTA_FIG.md`,
lotes 6-10 para el primer grupo).

### Carpeta "Intro a Finanzas" (Drive fileId `1ud0kH9Gj_z43SdCz_Sg8UMJF4wgzgXLE`, 67 archivos)

**Extraídos en algún lote (`finanzas-01.json` a `finanzas-17.json`):**
`19VDBbLJ1IhdvV2URVa_hrwhpDogr3dxZ`, `1-_GVlZKlq9AKECWkB7XpnnnS1_1_TRHL`, `1Cr0dEU2wiKWJ5Wc8WioGhbt5GRRbE2c_`, `1YYtmDvXoulaigZa-nqh3NZXKZgiRtGSD`, `1TwHD4WB1_Jquyp8azOew9_depa5sXTR0`, `1gZG57Bb3aR-HNdnopmtpLncZhSPnnQ6-`, `1A_15u-dtLTD-dtKwm-i6-bsrLPPq7-Mn`, `1H1ZHTlc5wQ5RP2B6sbTHkMKoSDOq3w7F`, `1BLTYvkVxC5eRRNrcn1HeHUIGwlG_A6RH`, `1jQ8mIZSKOxGadghR2dindYbzUK8yVdfx`, `1jVkodScYNfkdqB6fuUFScERIO1W0zEPu`, `1YxGgOj15ZyfbW1QyGIu00NP0GtfmkwkC`, `1jP3pTSFKSLAkbxSZn-I3wKNR9hB2rVmB`, `1KrScSLYQM120CiqKSIFSC2Bvsybuymf9`, `1UMTdEoq4E31squ-91DdyjkOCVNdfKdmX`, `1zpVZlt7n8s-U5PjM0FOTcReMxcrj_EaQ` (parcial), `1P6HOjF674nm0zuWI66wMSk8hYccxexhK`, `1xMtZLxUg_OEOpTdA_osE2VdA6Ly6W1pi`, `16FQT7vZPj-lwk-rHqYREIAcOWHjMiy_J`, `15YyhYOlJYK-ZZK5IiH0wcKtmu7NYSkZa`, `1VfiM17iwf9zJMcikUtJhWKHMwfkmNi8t`

**Descartados (no usar, ya evaluados como no aprovechables):**
`1AAT7ri2s0e0n6O39MGlJ5m_kDmPzS7pZ` (fórmulas ilegibles), `1zlkVIUlNDX5azFY2QnBCBxpPLmKKenb_` (sin pauta resuelta)

**Escaneados pero SIN extraer todavía (contenido ya leído y evaluado bueno, disponible para un lote futuro sin releer):**
`1gFkFDRvNGKfYQD48ctKfF3wR6bixCrrP` (2018 Pauta Examen Marcelo González — excelente, 3 comentes + AFP/bonos), `1icnUbzRorvuWcemmlsQPiCKRVfA8dmIo` (2018 Pauta Ayudantía VAN González — bueno, comparación de créditos), `1aENt0ozeVGwsaCGhmKghj0fBtjgnW7b8` (2017 Verano Pauta Solemne González — mayormente duplicado, pero tiene un problema de bootstrapping de tasas spot sin usar)

**Archivos de Finanzas I mezclados dentro de esta carpeta (encabezado real distinto al de la carpeta), ya extraídos:**
`1CM7h4-TOsLlKs6PvA7CR9ECudfJ1ZT_K`, `1CgtcgvCmDfsUPFbI_TQ1AJYFeDT87hAA`, `1jH2_vicziJoI0iav9NkaaxvJIxCyuEJI` (descartado), `1wUKgCjuqnM1UCuXb216jCCnRs1w8CqsC`, `1GIU1hnCR2PW3eWi2oZxR_HfoMU8qrdjQ`, `1c07YbJXyO7DUtHHYl5qhuw-P1tlZ_4EN`, `1SNJ_SFwjKX9BuadKYE91Q9pprGLNxDBR`, `19RwQnYbdAOzmjFZnlSudH3liRRijeaFi`, `1DBlecqi9J1HRNNJfQN7D0APJuOtGcWUi`, `1k-4NPMD0ZvbS-nlwJZ-6uka4WtThLvyY`, `1k5GNnJjAqcpXBebHDj0PqMIHueoDCmG6`, `1TPPDwgJLatto3Zq6XepLtA4ANtKEwCum`, `1JxpnwOVQ5w1IWUABsYVfNP3KWxV6JT-W`, `1uRb6mRvh0rOYdu5FqmYsQo4YblqHvec7`, `1SNwKiHCAwPm6lehutMZv5ZxTu0e6vkfL`, `1uso2U_sphU2qsiFvY3p-UTiKQJvsxNUw`, `1s2tDCeMuinYCCnDS8scsYcDRXrjauVsN` (descartado), `1ARxVykYTVeoStufvpCbo_YLM6VHos-9s`, `14Scgf-W76sSwVAseRc9XhpxEBvrOfbAM`

**Sin tocar aún** (candidatos vistos en el listado completo de la carpeta pero nunca escaneados): `1FGKWjVViKxDm5eY-htGAU7h0s_8tG4Ss` (Solucionario Ross/Westerfield/Jaffe, textbook grande), `155RWXjjiNql8BhA3-tK7K0LAqSVjoYto`, `1CbostGWnlJHivjafrw6M5INCgBNhMMgw`, `1ViG0Or9xAjl97dVBJLEfur42yxnz4A9V` (tabla, bajo valor), `1K2VzCZDRKXGD9mbLFKMDRbxMpYqwUhwJ`, `1aGilYqPeMAm0H5INj9lHxhAfCKO4NhMP`, `1bK5me79srSKs-mmVI8keAgVgTE5tekvW`, `17Q22zM-8Y4L0zZAcKbwA2tFyoiOHr1O1`, `1OWWp3xItQDinR9d95nMfzDpT2JVZ4Wxi`, `1KwzzlUk-7WGHpsEEeJdZWztzfCweq1L9`, `1bjEOeZaw_fEztikWN6Viq9lXUiR431Uz` (más 2 .ppt y `Formulario.pdf`/`Tabla_ratios.pdf`, bajo valor esperado)

### Carpeta "Finanzas I" (Drive fileId `1LLI7QPeir3BWVK3y5JKvqfpVoXqnX-6b`, 70 archivos — OJO: mezcla contenido real de "Finanzas II" con profesor Jorge Gregoire, derivados)

**Extraídos (lotes 18-23):**
`1kSbcx7fuQXhz7aFCbPxyQVfbbtqXQHKY`, `1u6mSFXZevjqnXxaY3Z1MZodrI7no9DM_`, `1RnFEnrztn411Ynf_Vmfjh7DlLHA_U-LB`, `1gneVjNF79lXRbKq_h_gwqInrowjsP-Mh`, `1v45H6bU1y2ylDKD620SjGumew_0y710D`, `1ERkrCp0_glRju_LDycWDZjPW1EVe3nDN`, `1n7-5LLLQL5FY-5_Bg6lEf2sltAbHedi9`, `1zVh2fB9SkhI7shYi5oaYWocIM6cV7kXB`, `1bT8Euuy7j5tpD2BdksaZaGg1NXarNdU9`, `1zz_HKpuAvf0DwQwNHPyzxnw1OX-QZ5Wt`, `1VSgB_7z77QjaOrGmVzs0uhWckSly_kqQ`, `1dXngn70Xh70vo2rNAHKjcM5bsZDjdYv1`, `1cg1-pBT9E1tXZ9HL3hIBY5sFd6XjBm0U`, `1zl2yUWZQ1m-qyaGPQcqtLpAG5MJARurd`, `1ATO1dEme4A2Mg_41fB6nP-a3l-1zBhtb`, `1FKlgkKgKRuy6K50EiPG33GZy-EC93ErU`, `1FBR89eUVb_kDlNmm7nwsC8VqVsKZ29F9`, `1nG6RcrlLZQDo-cIYDQ0katwF-tzyDXyG`, `1R_Hvcphjv9ZAEsvLiAqf7u0r-x-1Ovb9`, `192kK9_OTBiYjioh0N0GmG6Gy0RUBliZA`, `1zLMf7cHIRCH_9giJQleIHOurVHL7mQIW`, `1Bm88klsH8xATNiLI59JhZJePD9b4EGlP`, `1zp47W-Ca6ZxEu08twNHcXoGOjyuhx9ar`, `1Y6fD0oBTOcpBabI862W49IrwgvtM7Xlz`, `1BeX2hkMvS5n0te-OiLcM_F6NBqT0US8M`

**Sin tocar aún** (candidatos vistos en el listado completo de la carpeta, ~30-40 archivos restantes, mayormente Ayudantías/Ejercicios de opciones-futuros de Gregoire con nombres como `Ejercicios Opciones*.pdf`, `Ejercicio bonos y opciones.pdf`, `Ejercicios Bonos*.doc`, `Clase futuros.pdf`, `Clase opciones.pdf`, `Ayudantia 2/3 Otono 2014.pdf`, `Ayudantia 5/6/7 Verano/Otoño 2009.pdf`, `Guía Contratos Forwards y Futuros.pdf`, `Guía Futuros y Forward.pdf`, `2021 Primavera - Resumen...Hansen.pdf`, `2020 Verano - Compilado...Marcet.pdf`, `Ejemplo Portafolio Eficiente 2012.xls` (excel, excluir)) — se espera solapamiento creciente con lo ya extraído, revisar con escaneo de calidad antes de comprometerse a un lote completo.

---

## Estado

- ✅ **Q1 completado:** 2026-07-16 23:35
- 🔄 **Q2 en curso:** 23 lotes hechos (2026-07-17) — `finanzas-01.json` a `finanzas-23.json`, **300 preguntas totales** (hito redondo) cubriendo 12 temas: matemática financiera, análisis de ratios, renta fija (incl. duración/convexidad avanzada), riesgo financiero (incl. VaR, Basilea vs RiskMetrics), evaluación de proyectos, CAPM/portafolios/CML avanzado (incl. Sharpe/Treynor/Jensen, eficiencia de mercado), estructura de capital, historia de mercados, macroeconomía, fundamentos/gobierno corporativo, y **derivados-futuros**/**derivados-opciones** (forwards, futuros, cobertura, opciones, Black-Scholes, árboles binomiales, delta hedging, CDS, cotas de arbitraje, valoración neutral al riesgo). Desde 77 archivos distintos entre "Intro a Finanzas" y "Finanzas I" (esta última carpeta también contiene material claramente de "Finanzas II" mezclado — revisar encabezados). 4 archivos descartados. Antes de extraer se hace siempre un escaneo rápido de calidad — de los últimos 50 archivos de "Finanzas I" escaneados en 5 rondas, casi todos resultaron aprovechables, aunque el solapamiento de contenido entre archivos va en aumento (señal de que la carpeta se acerca a agotarse). Queda poco material sin escanear en "Finanzas I" (70 archivos totales), más el resto de "Intro a Finanzas" + "Finanzas II" (45) + APF (7)
- ⏳ **Q3 pendiente:** Revisión pedagógica (Opus/Fable, muestreo ~10%)
- ⏳ **Q4 pendiente:** Balance del banco

---

**Generado por:** Claude Code (Haiku 4.5)  
**Sesión:** claude/material-finanzas-roadmap-vmd3lw
