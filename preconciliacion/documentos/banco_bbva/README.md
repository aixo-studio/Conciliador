# Extracto del BBVA

## De dónde sale

Banca de empresas del BBVA → Movimientos Históricos → exportar a Excel.
Llega como `.xls` (el formato viejo de Excel), con una sola hoja:
"Movimientos Históricos".

## Cómo viene

- Arriba hay unas filas de título (empresa, cuenta, sucursal, saldo y período)
  y una fila vacía. No son movimientos y se ignoran.
- Después viene la fila de encabezados y debajo un movimiento por fila.
- Columnas: Fecha · Fecha Valor · Concepto · Codigo · Número Documento ·
  Oficina · Crédito · Débito · Detalle. Al final hay una columna sin nombre
  que a veces dice "Saldo Disponible: …".

## Cómo se convierte

Qué columna va a cada lugar y la lista de gastos bancarios están en la
sección `[bancos.BBVA]` de `configuracion.toml`. Acá va lo que el config no
explica.

**Por qué el Código sale de "Codigo" y no de "Concepto":** "Codigo" es un
número corto que identifica el tipo de movimiento (por ejemplo `236` es el
IVA) y alcanza solo para reconocer los gastos bancarios. El
"Concepto" mezcla el tipo con otros datos (`TRANSFERENCI 20111111112` trae el
CUIT), así que no sirve para comparar contra una lista. La lista de gastos la
armó la persona que concilia.

## Condiciones

- El débito ya viene con signo menos. El programa lo toma sin signo y lo pone
  negativo, así no depende de cómo venga.
- Cada fila tiene crédito o débito, uno solo. Si una fila trae los dos, o
  ninguno, el programa frena y dice qué fila es.
- "Codigo" tiene que venir como texto. Si viene como número (pasa si alguien
  abre el archivo en Excel y lo vuelve a guardar), `005` puede haber quedado
  en `5`: el programa frena y pide bajar el archivo de nuevo del banco.
- No se usan: Fecha Valor, Concepto, Número Documento, Oficina y la columna
  sin nombre. El texto del Concepto (con el CUIT o la referencia del cheque)
  no sale en el resultado.
- El número de cheque viene en "Número Documento" y no sale en el resultado.

## Ejemplo (datos inventados)

Entra:

| Fecha      | Concepto                     | Codigo | Crédito | Débito   | Detalle          |
|------------|------------------------------|--------|---------|----------|------------------|
| 30-09-2026 | CH/CLEAR.48  000000000001    | 005    |         | -150000  |                  |
| 29-09-2026 | TRANSFERENCI 20111111112     | 319    | 250000  |          | CTE 000011110001 |

Sale:

| Fecha      | Código | Descripción      | Monto en centavos | Clase      |
|------------|--------|------------------|-------------------|------------|
| 30/09/2026 | 005    |                  | −15000000         | Movimiento |
| 29/09/2026 | 319    | CTE 000011110001 | 25000000          | Movimiento |
