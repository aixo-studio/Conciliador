# Libro del sistema financiero (Finnegans)

Es el libro de una cuenta bancaria, exportado del sistema. Viene igual para
todas las cuentas: se comprobó con las de tres bancos distintos. Por eso hay
una sola carpeta para todos.

## De dónde sale

Se exporta del sistema como `.xlsx`, una cuenta por archivo, con una sola hoja
(`hoja1`).

## Cómo viene

- La primera fila son los encabezados; no hay títulos arriba.
- La segunda fila es el **"Saldo Inicial"**, con Debe y Haber en 0. No es un
  movimiento y se ignora (el resumen lo informa).
- Después, un movimiento por fila.
- Columnas: Año - mes · Codigo cuenta · Cuenta · Fecha · Comprobante ·
  Descripción · Debe · Haber · Documento · Dimensión valor · Detalle ·
  Cotizacion · Productoid · Producto · Empresa · Organizacion transaccion ·
  Debe · Haber · Tipo de documento.

## Condiciones

Qué columna va a cada lugar está en la sección `[erp]` de
`configuracion.toml`. Acá va lo que el config no explica.

- No tiene gastos bancarios: todas sus filas salen con Clase "Movimiento".
- **Debe y Haber aparecen dos veces.** Un par está en pesos y es el que se usa;
  el otro es el mismo importe en dólares. El de pesos se reconoce porque está
  entre Descripción y Documento (`seguidas` en `configuracion.toml`). Si esas cuatro
  columnas no vienen juntas y en ese orden, el programa frena: así nunca toma
  los dólares por error si el sistema cambia el orden de las columnas.
- Cada movimiento tiene Debe o Haber, uno solo. Si una fila trae los dos, o
  ninguno, el programa frena y dice qué fila es.
- La fila "Saldo Inicial" se ignora. Si algún día trajera un monto, el
  programa frena en vez de saltearla.
- En las órdenes de pago y los recibos, la columna Descripción viene vacía: a
  quién se pagó o quién pagó está en "Organizacion transaccion", que hoy no
  sale en el resultado.
- El número de cheque viene en "Detalle" y no sale en el resultado.
- No se usan: Año - mes, Codigo cuenta, Cuenta, Comprobante, Documento,
  Dimensión valor, Detalle, Cotizacion, Productoid, Producto, Empresa,
  Organizacion transaccion y el segundo par de Debe y Haber.

## Ejemplo (datos inventados)

Entra:

| Fecha      | Descripción            | Debe    | Haber  | Documento         | Tipo de documento    |
|------------|------------------------|---------|--------|-------------------|----------------------|
| 31/08/2026 |                        | 0       | 0      | Saldo Inicial     |                      |
| 01/09/2026 | Mvto. e/ ctas. propias | 500000  | 0      | MOVFONDOS - 00001 | Movimiento de Fondos |
| 01/09/2026 |                        | 0       | 125000 | PAGO - 00002      | Orden de pago        |

Sale:

| Fecha      | Código               | Descripción            | Monto en centavos | Clase      |
|------------|----------------------|------------------------|-------------------|------------|
| 01/09/2026 | Movimiento de Fondos | Mvto. e/ ctas. propias | 50000000          | Movimiento |
| 01/09/2026 | Orden de pago        |                        | −12500000         | Movimiento |
