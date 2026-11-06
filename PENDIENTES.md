# Pendientes

## Abierto, en orden de prioridad

### 1. Definir la lógica del cruce

Alcance decidido: dos pasadas de cruce, una después de la otra.

1. **Cruce exacto** (misma fecha y mismo monto). Hecho, ver abajo.
2. **Sumas del mismo día**: una fila de un documento contra 2 o 3 filas del
   otro documento, de la misma fecha, que sumadas dan su monto exacto. En las
   dos direcciones. Se evalúa con el resultado del cruce exacto a la vista.
   Con septiembre (y los gastos ya separados) cruzaría pocos grupos: 5 en
   BBVA, 2 en Galicia, 0 en Supervielle.

Decisiones a tomar:

- **Gastos bancarios**: los reconoce v3, con la lista de cada banco. Este repo
  los aparta antes de las sumas (así no generan sumas falsas). Cómo los recibe
  se define al adaptar la entrada al contrato del 2026-11-04 de v3.
- **Más de un candidato** en la pasada de sumas: qué se hace (idea: no cruzar
  y anotar cuántos candidatos había).
- **Sumas**: si cruzan directo o quedan "a revisar" para que alguien confirme.
- **Pasada de sumas**: si lee el Excel del cruce exacto y completa solo lo
  "Sin cruzar", o si se corre todo junto.
- **Controles de mes**: qué hacer si una fila tiene fecha de otro mes.

### 2. Fuera del alcance actual (anotado para no perderlo)

Con septiembre, después del cruce exacto y de separar gastos:
- **Mismo monto con fecha cercana** (hasta 3 días, que cubre fines de semana):
  cruzaría 76 filas en BBVA, 3 en Galicia y 11 en Supervielle.
- **Diferencias de 1 a 5 centavos el mismo día**: 9 en BBVA.
- **Pagos partidos en muchas partes** (ej. haberes: una línea en el sistema y
  muchas transferencias en el banco): no los alcanza una suma de 2 o 3.

### 3. Datos que no llegan en el contrato de v3

El número de cheque del BBVA (Número Documento), el código del BBVA y los datos
extra del Galicia (Leyendas Adicionales) no están en las 4 columnas. Si el
cruce los necesita, hay que cambiar el contrato de v3.

### 4. Definir dónde termina la etapa

Qué entrega al final esta etapa y a quién.

## Hecho

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
