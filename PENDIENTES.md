# Pendientes

## Abierto, en orden de prioridad

### 1. Comunicación con v3 (APR-235, lo tiene Luciano)

Lo que falta para correr de punta a punta, ahora que el cruce ya trabaja
sobre las tablas:

- Conseguir las dos tablas de una cuenta: llamar a `convertir_documento()` de
  v3, una vez por archivo, y pasárselas a `cruzar_cuenta()` con la ruta de
  salida.
- La terminal: qué recibe, qué muestra y dónde escribe. La vieja (`cruzar.py`)
  se borró junto con la entrada por Excel.
- Al fallar una corrida, borrar el resultado anterior de esa cuenta (lo hacía
  la terminal vieja; `cruzar_cuenta()` no escribe nada si algo falla, pero
  tampoco borra lo que había de antes).
- Verificar septiembre 2026 contra la referencia fija del CLAUDE.md: hasta
  ahora todo está probado con tablas inventadas.

### 2. Definir la lógica del cruce

Alcance decidido: dos pasadas de cruce, una después de la otra.

1. **Cruce exacto** (misma fecha y mismo monto). Hecho, ver abajo.
2. **Sumas del mismo día**: una fila de un documento contra 2 o 3 filas del
   otro documento, de la misma fecha, que sumadas dan su monto exacto. En las
   dos direcciones. Se evalúa con el resultado del cruce exacto a la vista.
   Con septiembre (y los gastos ya separados) cruzaría pocos grupos: 5 en
   BBVA, 2 en Galicia, 0 en Supervielle.

Decisiones a tomar:

- **Gastos bancarios**: los reconoce v3, con la lista de cada banco. Llegan
  con Clase "Gasto bancario" y quedan con Estado "Gasto bancario" desde el
  principio; ninguna pasada los toma (decidido el 2026-11-10, APR-223).
- **Más de un candidato** en la pasada de sumas: qué se hace (idea: no cruzar
  y anotar cuántos candidatos había).
- **Sumas**: si cruzan directo o quedan "a revisar" para que alguien confirme.
- **Pasada de sumas**: si lee el Excel del cruce exacto y completa solo lo
  "Sin cruzar", o si se corre todo junto.
- **Controles de mes**: qué hacer si una fila tiene fecha de otro mes.

### 3. Fuera del alcance actual (anotado para no perderlo)

Con septiembre, después del cruce exacto y de separar gastos:
- **Mismo monto con fecha cercana** (hasta 3 días, que cubre fines de semana):
  cruzaría 76 filas en BBVA, 3 en Galicia y 11 en Supervielle.
- **Diferencias de 1 a 5 centavos el mismo día**: 9 en BBVA.
- **Pagos partidos en muchas partes** (ej. haberes: una línea en el sistema y
  muchas transferencias en el banco): no los alcanza una suma de 2 o 3.

### 4. Datos que no llegan en el contrato de v3

El número de cheque del BBVA (Número Documento), el texto del Concepto del
BBVA y del Galicia y los datos extra del Galicia (Leyendas Adicionales) no
llegan. Si el cruce los necesita, hay que cambiar el contrato de v3.

### 5. Definir dónde termina la etapa

Qué entrega al final esta etapa y a quién.

### 6. Un tramo sin verificar en v3 (para hablar con Luciano)

v3 controla lo armado contra el archivo original, y después arma la tabla y
le pone la Clase a cada fila. Ese último paso no lo verifica nadie: este repo
controla contra la tabla que recibe, no contra el archivo del banco. El
riesgo es bajo (ese paso no mueve ni filtra filas), pero es un tramo sin
control. Si se quiere cerrar, lo haría v3 antes de devolver la tabla, sin
cambiar el contrato.

## Hecho

- 2026-11-11 — El cruce pasa al contrato del 2026-11-04 (APR-214):
  `cruzar_cuenta()` encadena recibir (chequeos y Estado), el cruce exacto solo
  sobre filas "Sin cruzar", el control contra la tabla recibida, los controles
  entre los dos lados y el Excel de siete columnas (entra Clase, sale
  Criterio; la pareja es la fila de la otra hoja, contando desde la 2). Se
  borran `cruzar.py` y `motor/entrada.py`. Probado con tablas inventadas; la
  corrida real y septiembre quedan para APR-235.
- 2026-11-10 — Control del contrato nuevo de v3 (APR-223): `motor/recibir.py`
  (la forma de la tabla que llega y el Estado inicial de cada fila) y
  `motor/controlar.py` (después del cruce, el resultado contra la tabla tal
  como llegó). Probado con tablas inventadas; **sin conectar** al programa
  hasta APR-214, y sin verificar con datos reales. El repo pasa a Python 3.12
  y suma pandas, como v3. El programa sigue corriendo igual que antes.
- 2026-11-06 — Se sacan `bancos.json` y `motor/gastos.py` (APR-226): qué es
  gasto bancario lo decide v3. La idea de avisar los códigos de gasto nunca
  vistos quedó en el PENDIENTES de v3, donde vive la lista. La salida no
  cambia.
- 2026-10-21 — bancos.json y motor/gastos.py: cómo se reconoce un gasto
  bancario en cada banco por su Código (APR-215, primera parte). Con
  septiembre reconoce BBVA 836 filas (−25.702.218,68), Galicia 387
  (−58.477.591,43) y Supervielle 89 (−986.203,99), igual que la separación
  manual. No está conectado al cruce: el Excel no cambia.
- 2026-10-19 — Base del repo: lectura de la entrada con control del contrato,
  cruce exacto (misma fecha y mismo monto; repetidos emparejados en orden) y
  Excel de salida con hojas Resumen, Banco y Sistema. Septiembre: BBVA 394
  cruces, Galicia 86, Supervielle 54.
- 2026-10-20 — La entrada pasa a tener "Código" en vez de "Concepto" (cambio de
  contrato de v3, commit 306da11): el valor puro de la columna que identifica
  el tipo de movimiento en cada banco. La lectura frena si el Código no es texto.
- 2026-10-19 — Cada fila cruzada dice en qué fila del otro documento está su
  pareja ("Fila en Sistema" / "Fila en Banco", numeradas como en el output de
  v3), en lugar de un número de cruce.
