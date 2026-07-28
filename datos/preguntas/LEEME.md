# Banco de preguntas del Desafío FIG — Guía de autoría

> **Para quien escribe preguntas — humano o IA de cualquier tamaño.**
> Si sigues este documento al pie de la letra y `validar_preguntas.py`
> dice "TODO OK", tu trabajo tiene la calidad requerida. No necesitas
> entender el juego ni tocar su código: solo produces JSON válido aquí.

## Cómo funciona el banco

- `index.json` declara los **temas** (áreas de conocimiento), los **ramos**
  (asignaturas de las que sale el material) y la lista de **archivos**
  (shards) con las preguntas.
- Cada shard es un array JSON de preguntas. Máximo **~200 preguntas o
  150 KB por shard**; al superar eso, crear `tema-02.json`, `tema-03.json`…
  y agregarlo a `archivos` en el índice.
- La página `desafio/index.html` carga el índice y todos los shards. Si un
  shard rompe el esquema, el juego entero se degrada — por eso el validador
  es **obligatorio antes de cada commit**:

```
python3 validar_preguntas.py          # debe terminar en "TODO OK"
python3 validar_preguntas.py --stats  # ver balance por tema/ramo/dificultad
```

## Esquema de una pregunta (todos los campos obligatorios)

```json
{
  "id": "rf-014",
  "tema": "renta-fija",
  "ramo": "finanzas-i",
  "dificultad": 2,
  "pregunta": "¿Qué mide la duración (duration) de un bono?",
  "alternativas": [
    "La sensibilidad del precio ante cambios en la tasa",
    "Los años exactos hasta el vencimiento",
    "La probabilidad de default del emisor",
    "El total de cupones que quedan por cobrar"
  ],
  "correcta": 0,
  "explicacion": "La duración aproxima cuánto cae el precio ante un alza de 1% en la tasa. No es el plazo al vencimiento aunque se mida en años: un bono con cupones altos tiene duración menor que su plazo.",
  "fuente": "Finanzas I · Clase 07 - Renta Fija.pdf"
}
```

Reglas por campo:

| Campo | Regla |
|---|---|
| `id` | Único en TODO el banco. Prefijo corto del tema + correlativo: `rv-`, `rf-`, `mac-`, `his-`… |
| `tema` / `ramo` | Deben existir en `index.json`. Para un tema/ramo nuevo: agregarlo al índice EN EL MISMO COMMIT |
| `dificultad` | 1 = básico (cualquier estudiante), 2 = requiere haber estudiado, 3 = fino/avanzado. Apuntar a mezcla ~40/40/20 |
| `pregunta` | 15–300 caracteres. Autocontenida: se entiende sin ver las alternativas. En español, sin siglas sin expandir la primera vez |
| `alternativas` | 3 a 5, sin duplicados, largos comparables entre sí (que la correcta no sea "la más larga"). Distractores **plausibles**: errores que un estudiante real cometería, nunca opciones absurdas de relleno |
| `correcta` | Índice (0-based) de la alternativa correcta. **La página baraja las alternativas al mostrar**, así que da lo mismo la posición — lo cómodo es ponerla primera y apuntar `correcta: 0` |
| `explicacion` | 60–500 caracteres. Es la parte pedagógica del juego: explica **por qué** la correcta es correcta y, si aporta, por qué el error típico es tentador. Nunca solo "La respuesta es A" |
| `fuente` | De dónde salió: `"<Ramo> · <archivo o clase del Drive>"`. Permite auditar contra el material. Para preguntas sin material de origen: `"conocimiento-general"` |

## Estilo (lo que hace FIG a una pregunta)

1. **Enseña incluso al que falla.** La explicación es lo que el jugador lee
   al final — escríbela como un buen ayudante de cátedra: corta, concreta,
   con el "porqué" y, si cabe, la intuición o la lección práctica.
2. **Historias e hitos bienvenidos.** El tema `historia-mercados` existe para
   crisis, burbujas, personajes y anécdotas de la industria. Una buena
   pregunta de historia termina su explicación con la lección para el
   inversionista.
3. **Nada de trampas lingüísticas.** La dificultad debe venir del contenido,
   no de dobles negaciones ni de "todas las anteriores" (prohibido usar
   "todas/ninguna de las anteriores": se rompe al barajar).
4. **Español chileno neutro**, tono cercano pero riguroso. Cifras con punto
   de miles (10.000) y decimales con coma cuando sea texto.
5. **Precisión ante todo.** Si al redactar desde el material del Drive algo
   no calza o parece dudoso, NO inventar: dejar la pregunta fuera y anotar
   la duda en `HOJA_DE_RUTA_FIG.md` para revisión.

## Flujo de producción desde el material del Drive (el macro repositorio)

El material fuente vive en Google Drive (**solo lectura para IAs**). El
proceso por lotes, apto para dividir entre modelos:

1. **Inventario** (Haiku): listar la carpeta del Drive, mapear qué archivo
   pertenece a qué ramo, proponer temas nuevos si el material no calza en
   los existentes. Salida: tabla archivo → ramo → tema(s) en la hoja de ruta.
2. **Extracción** (Sonnet, lotes de 20–40 preguntas): leer un archivo del
   material, redactar preguntas según esta guía, guardarlas en el shard del
   tema que corresponda, correr el validador, commitear. Un commit por lote,
   citando la fuente en cada pregunta.
3. **Revisión pedagógica** (Opus/Fable, muestreo): tomar ~10% de cada lote
   y verificar precisión técnica, calidad de distractores y explicaciones.
   Corregir o eliminar lo que no pase.
4. **Balance** (cualquiera): `--stats` para vigilar que ningún tema quede
   raquítico ni ninguna dificultad desaparezca.

Regla de oro para modelos menores: **si dudas entre calidad y volumen,
calidad**. El validador atrapa los errores de forma; la precisión del
contenido es responsabilidad de quien redacta.
