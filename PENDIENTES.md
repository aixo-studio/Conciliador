# Pendientes

## Abierto, en orden de prioridad

### General

1. **Unión de los repos (APR-235), lo que falta:** PR a main, archivar
   Pre-procesamiento-bancario-, renombrar la carpeta local a "Conciliador" y
   recrear el `.venv`. La carpeta "conciliacion v3" se guarda un tiempo como
   respaldo.
2. **Archivos originales del cliente:** pedir septiembre tal como sale del
   banco y del sistema (sin abrir ni guardar en Excel), de los 3 bancos, y
   probarlos. Hoy se prueba con copias armadas por nosotros.
3. **Salida en CSV** de las tres tablas del cruce. Después de la unión.
4. **Dónde termina el sistema:** qué se entrega al final y a quién.

### Etapa 1 (preconciliación)

1. **Completar las listas de gastos** de cada banco con otros meses: hoy salen
   solo de septiembre.
2. **Frenar si el archivo trae más de una hoja.** Hoy lee la primera sin
   avisar (pasó con un Galicia con una hoja de gastos hecha a mano adelante).
3. **Prueba automática con archivos reales:** una lista de referencia por mes,
   fuera del repo, que `pytest` compare sola; si los archivos no están, se
   saltea.
4. **Controlar que el libro del ERP sea de la cuenta del banco** (columna
   "Cuenta" del libro).
5. **Control de saldos** para detectar un extracto incompleto (el Supervielle
   trae Saldo).
6. **Avisar los códigos de gasto nunca vistos.** Hoy un gasto con código nuevo
   sale como "Movimiento" sin aviso.
7. **Un tramo sin control:** después de controlar contra el original, se arma
   la tabla y se pone la Clase; ese paso no lo verifica nadie. Riesgo bajo.
8. **Bancos con una sola columna de monto** (con signo, o importe + D/C).
   Toca el `motor/`: esperar un extracto real.
9. **Bancos nuevos** (APR-221): esperar los extractos del cliente.
10. **La ruta como texto:** `convertir_documento("archivo.xls", …)` falla con
    "no se pudo abrir como Excel"; hay que pasarla como `Path`. Aceptar
    texto o dar un error claro.

### Etapa 2 (conciliador)

1. **Segunda pasada: sumas del mismo día.** Una fila contra 2 o 3 del otro
   lado, misma fecha, en las dos direcciones (septiembre: 5 grupos en BBVA, 2
   en Galicia, 0 en Supervielle). A decidir: qué pasa con más de un
   candidato, si cruzan directo o quedan "a revisar", y si trabaja sobre lo
   pendiente del cruce exacto.
2. **Filas con fecha de otro mes:** qué se hace con ellas.
3. **Recuperar las Decisiones del README**, que se perdieron el 2026-11-12;
   revisar cuáles siguen vigentes.
4. **Datos que no llegan en el contrato:** cheque y Concepto del BBVA,
   Concepto y Leyendas del Galicia. Si el cruce los necesita, es un cambio de
   contrato.
5. **Fuera del alcance por ahora** (septiembre): mismo monto con fecha cercana
   de hasta 3 días (76 BBVA, 3 Galicia, 11 Supervielle), diferencias de 1 a 5
   centavos (9 BBVA) y pagos partidos en muchas partes.

## Hecho

### General

- 2026-11-19 — `conciliar.py`: concilia una cuenta de punta a punta (las dos
  etapas). Septiembre da igual a la referencia en los 3 bancos (BBVA 394
  cruces, Galicia 86, Supervielle 54).
- 2026-11-19 — Unión de los repos, pasos 1 a 4: cada etapa en su carpeta,
  la preconciliación con su historial, un solo `pytest.ini`, `requirements.txt`,
  CLAUDE.md, PENDIENTES y README general. Solo cambiaron rutas de imports.
  83 pruebas y septiembre igual.

### Etapa 1 (preconciliación)

- 2026-11-04 — Verificación de formato (APR-218): solo las columnas que se
  usan; si falta una, dice cuál y en qué fila; todas las filas con errores en
  un solo mensaje.
- 2026-11-04 — Devuelve un DataFrame en vez de escribir Excel; los gastos se
  marcan con la columna Clase. Sale el mes.
- 2026-11-03 — El contrato queda igual en los dos CLAUDE.md, con fecha (APR-227).
- 2026-10-30 — Gastos en una hoja aparte y control antes de separar
  (APR-222, APR-223). Reemplazado el 2026-11-04 por la columna Clase.
- 2026-10-28 — Lista `gastos` por banco en `configuracion.toml`, comparación
  exacta del Código (APR-219).
- 2026-10-26 — Un documento por corrida; las reglas pasan a
  `configuracion.toml`.

### Etapa 2 (conciliador)

- 2026-11-16 — El cruce devuelve tres tablas y un resumen (APR-214). Salen la
  columna Estado, el Excel y `motor/salida.py`.
- 2026-11-11 — El cruce pasa al contrato del 2026-11-04 (APR-214).
- 2026-11-10 — Control del contrato al recibir y control del resultado
  contra lo recibido (APR-223).
- 2026-11-06 — Qué es gasto bancario lo decide la etapa 1 (APR-226).
- 2026-10-20 — La entrada usa "Código" en vez de "Concepto".
- 2026-10-19 — Base: cruce exacto (misma fecha y mismo monto; repetidos en
  orden) y cada cruce dice la fila de su pareja.
