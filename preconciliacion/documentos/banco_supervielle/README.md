# Extracto del Supervielle

## De dónde sale

Banca de empresas del Supervielle → movimientos de la cuenta → exportar a
Excel. Llega como `.xlsx` con una hoja, "Supervielle". El nombre del archivo
trae la cuenta y la fecha de descarga (`Movimientos_Supervielle_<cuenta>_<fecha>.xlsx`).

## Cómo viene

- La primera fila son los encabezados; no hay títulos arriba ni saldo inicial.
- Un movimiento por fila, del más nuevo al más viejo.
- Columnas: Fecha · Hora · Concepto · Detalle · Débito · Crédito · Saldo.

## Cómo se convierte

Qué columna va a cada lugar y la lista de gastos bancarios están en la
sección `[bancos.Supervielle]` de `configuracion.toml`. Acá va lo que el
config no explica.

**Por qué el Código sale de "Concepto":** el banco no trae una columna de
código; el Concepto es el texto fijo que identifica el tipo de movimiento
(`Pago Cheque de Cámara Recibida`). Por eso los gastos se reconocen por el
Concepto exacto.

## Condiciones

- Débito y Crédito vienen los dos en positivo, en columnas separadas; la que no
  corresponde viene en 0. El programa pone el débito en negativo.
- Cada fila tiene crédito o débito, uno solo. Si una fila trae los dos, o
  ninguno, el programa frena y dice qué fila es.
- El Detalle viene vacío en el impuesto a los débitos y créditos y en algunos
  cargos del banco.
- El número de cheque queda en la Descripción ("Número Cheque: 2075").
- No se usan: Hora y Saldo. El Saldo se va a usar para el control de saldos
  (ver PENDIENTES.md).

## Ejemplo (datos inventados)

Entra:

| Fecha      | Hora  | Concepto                       | Detalle            | Débito | Crédito |
|------------|-------|--------------------------------|--------------------|--------|---------|
| 30/09/2026 | 07:28 | CRED BCA ELECTR INTERBANC EXEN | CUENTAS PROPIAS    | 0      | 500000  |
| 29/09/2026 | 02:28 | Pago Cheque de Cámara Recibida | Número Cheque: 101 | 150000 | 0       |

Sale:

| Fecha      | Código                         | Descripción        | Monto en centavos | Clase      |
|------------|--------------------------------|--------------------|-------------------|------------|
| 30/09/2026 | CRED BCA ELECTR INTERBANC EXEN | CUENTAS PROPIAS    | 50000000          | Movimiento |
| 29/09/2026 | Pago Cheque de Cámara Recibida | Número Cheque: 101 | −15000000         | Movimiento |
