# Conciliador

Cruza los movimientos de un extracto bancario con los del libro del sistema financiero para una cuenta. Genera un Excel con el resumen y el detalle de los movimientos cruzados, pendientes y clasificados como gastos bancarios.

## Requisitos e instalación

Requiere **Python 3.12**. Desde la carpeta del repositorio, en macOS o Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Uso

`cruzar_cuenta()` recibe dos DataFrames ya preparados por la etapa de preconciliación y la ruta donde guardar el Excel.

```python
from cruzar_cuenta import cruzar_cuenta

resumen = cruzar_cuenta(tabla_banco, tabla_sistema, "resultados/conciliacion.xlsx")
```

Ambas tablas deben tener al menos una fila y estas cinco columnas en orden:

| Columna | Valor esperado |
|---|---|
| `Fecha` | Fecha de pandas |
| `Código` | Texto, incluidos los ceros iniciales |
| `Descripción` | Texto. Puede estar vacío. |
| `Monto en centavos` | Entero con signo |
| `Clase` | `Movimiento` o `Gasto bancario`. En el libro del sistema, solo `Movimiento`. |

El Excel tiene tres hojas: `Resumen`, `Banco` y `Sistema`. Las hojas de detalle conservan el orden de entrada e indican el estado de cada movimiento y, cuando hay cruce, la fila de su pareja en la otra hoja.

## Cómo funciona

1. **`motor/recibir.py`** valida las tablas y crea copias de trabajo con la columna `Estado`.
2. **`motor/cruce_exacto.py`** empareja movimientos con la misma fecha y el mismo monto. Si hay repetidos, los empareja en orden de aparición. Los gastos bancarios quedan fuera del cruce.
3. **`motor/controlar.py`** compara cada tabla cruzada con su original y resume las filas y los montos por estado.
4. **`motor/salida.py`** comprueba que los totales cruzados coincidan y que las referencias entre parejas sean recíprocas. Después escribe el Excel.

Los importes se comparan y se suman en centavos enteros para mantener exactas las cuentas. Las tablas originales se conservan como referencia para verificar que el cruce respete todas las filas, sus datos y su orden.

## Pruebas

Las pruebas usan datos inventados.

```bash
python -m pytest
```
