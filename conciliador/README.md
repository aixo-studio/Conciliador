# Etapa 2: el conciliador

Cruza los movimientos de un extracto bancario con los del libro del sistema financiero (el ERP) para una cuenta. Devuelve tres tablas (los cruces, lo pendiente del banco y lo pendiente del ERP) y un resumen. `cruzar_cuenta()` no escribe ningún archivo; para guardar el resultado en CSV está `motor/salida.py`.

La instalación está en el README de la raíz del repo.

## Uso

`cruzar_cuenta()` recibe dos DataFrames ya preparados por la etapa 1 (`preconciliacion/`): el del extracto del banco y el del libro del ERP.

```python
from conciliador.cruzar_cuenta import cruzar_cuenta

cruces, banco_pendiente, erp_pendiente, resumen = cruzar_cuenta(tabla_banco, tabla_erp)
```

Ambas tablas deben tener al menos una fila y estas cinco columnas en orden:

| Columna | Valor esperado |
|---|---|
| `Fecha` | Fecha de pandas |
| `Código` | Texto, incluidos los ceros iniciales |
| `Descripción` | Texto. Puede estar vacío. |
| `Monto en centavos` | Entero con signo |
| `Clase` | `Movimiento` o `Gasto bancario`. En el libro del sistema, solo `Movimiento`. |

Devuelve cuatro cosas:

| Qué | Qué tiene |
|---|---|
| `cruces` | Las filas del banco que cruzaron, con las cinco columnas y una sexta, `Fila en ERP`: el número de fila de su pareja en la tabla del ERP tal como llegó (la primera fila es la 0). |
| `banco_pendiente` | Las filas del banco que no cruzaron, incluidos los gastos bancarios. |
| `erp_pendiente` | Las filas del ERP que no cruzaron. |
| `resumen` | Filas y suma en centavos de cada lado: lo que entró, lo cruzado y lo pendiente. En el banco, también los gastos bancarios. |

Las tablas conservan el orden y el número de fila con que llegaron. Las dos que entran no se modifican.

## Cómo funciona

1. **`motor/recibir.py`** valida que las dos tablas cumplan el contrato. No las modifica.
2. **`motor/cruce_exacto.py`** empareja movimientos con la misma fecha y el mismo monto. Si hay repetidos, los empareja en orden de aparición. Los gastos bancarios quedan fuera del cruce. Trabaja sobre copias y devuelve las tres tablas.
3. **`motor/controlar.py`** vuelve a armar lo que entró con lo que salió del cruce. Si alguna fila se perdió, se duplicó o cambió, o si lo cruzado no suma lo mismo en el banco y en el ERP, frena. Si todo cierra, devuelve el resumen.
4. **`motor/salida.py`** (solo si se pide, desde `conciliar.py --csv`) escribe lo que devolvió el paso 3 en cuatro CSV: `cruces.csv`, `banco_pendiente.csv`, `erp_pendiente.csv` y `resumen.csv`. Cada tabla lleva primero su número de fila (`Fila`), el mismo que nombra `Fila en ERP`, y después todas sus columnas. Separados por punto y coma y con los acentos bien, para que Excel en castellano los abra directo. Si la carpeta ya tenía esos archivos, los reemplaza.

Los importes se comparan y se suman en centavos enteros para mantener exactas las cuentas. Las tablas originales se conservan como referencia para verificar que el cruce respete todas las filas, sus datos y su orden.

## Pruebas

Están en `pruebas/` y usan datos inventados. Se corren desde la raíz del repo, junto con las de la etapa 1:

```bash
python -m pytest
```
