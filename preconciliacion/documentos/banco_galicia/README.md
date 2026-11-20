# Extracto del Galicia

## De dónde sale

Banca de empresas del Galicia → movimientos de la cuenta → exportar a Excel.
Llega como `.xlsx` con una hoja, "Movimientos".

Sin verificar: el archivo con el que se armó esto fue guardado de nuevo desde
Excel. Falta compararlo con uno bajado directo del banco (ver PENDIENTES.md).

## Cómo viene

- La primera fila son los encabezados; no hay títulos arriba ni saldo inicial.
- Un movimiento por fila, del primero al último día del mes.
- Columnas: Fecha · Descripción · Origen · Débitos · Créditos · Grupo de
  Conceptos · Concepto · Número de Terminal · Observaciones Cliente · Número
  de Comprobante · Leyendas Adicionales 1 a 4 · Tipo de Movimiento · Saldo.

## Cómo se convierte

Qué columna va a cada lugar y la lista de gastos bancarios están en la
sección `[bancos.Galicia]` de `configuracion.toml`. Acá va lo que el config no
explica.

**Por qué el Código sale de "Grupo de Conceptos" y no de "Concepto":** el
Galicia agrupa sus operaciones en unos pocos grupos (Impuestos, Comisiones,
Intereses, Transferencias…) y el grupo alcanza solo para reconocer los gastos
bancarios. El "Concepto" es mucho más detallado
(`907268 - TRANSF INMED CP`) y casi lo mismo ya sale en la Descripción.
Por eso los gastos se reconocen con solo tres grupos (Impuestos, Comisiones e
Intereses).

## Condiciones

- Débitos y Créditos vienen los dos en positivo, en columnas separadas; la que
  no corresponde viene en 0. El programa pone el débito en negativo.
- Cada fila tiene crédito o débito, uno solo. Si una fila trae los dos, o
  ninguno, el programa frena y dice qué fila es.
- En las comisiones por depósito de cheque, la Descripción trae el número de
  cheque pegado (`Com. Deposito De Cheque      475`). Se copia tal cual.
- No se usan: Origen, Concepto, Número de Terminal, Observaciones Cliente,
  Número de Comprobante, Leyendas Adicionales 1 a 4, Tipo de Movimiento y
  Saldo.

## Ejemplo (datos inventados)

Entra:

| Fecha      | Descripción     | Débitos | Créditos | Grupo de Conceptos      | Concepto                  |
|------------|-----------------|---------|----------|-------------------------|---------------------------|
| 01/09/2026 | Transf Inmed Cp | 150000  | 0        | 000907 - Transferencias | 907268 - TRANSF INMED CP  |
| 02/09/2026 | Credito Prestamo| 0       | 800000   | 000083 - Pagos          | 917133 - CREDITO PRESTAMO |

Sale:

| Fecha      | Código                  | Descripción      | Monto en centavos | Clase      |
|------------|-------------------------|------------------|-------------------|------------|
| 01/09/2026 | 000907 - Transferencias | Transf Inmed Cp  | −15000000         | Movimiento |
| 02/09/2026 | 000083 - Pagos          | Credito Prestamo | 80000000          | Movimiento |
