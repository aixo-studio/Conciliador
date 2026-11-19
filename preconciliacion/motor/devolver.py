"""Último paso del proceso: armar el DataFrame que se devuelve a quien llama (Conciliador).

Una fila por movimiento, en el orden del original, con cinco columnas:
Fecha · Código · Descripción · Monto en centavos · Clase.
La Clase dice si la fila es un gasto bancario; lo decide es_gasto(), con la
lista de cada banco en configuracion.toml. El libro del ERP no tiene lista:
todas sus filas son "Movimiento".
"""
import pandas

from motor.armar import Movimiento
from motor.configuracion import es_gasto

COLUMNAS = ["Fecha", "Código", "Descripción", "Monto en centavos", "Clase"]
CLASE_MOVIMIENTO = "Movimiento"
CLASE_GASTO_BANCARIO = "Gasto bancario"


def armar_dataframe(movimientos: list[Movimiento], reglas: dict) -> pandas.DataFrame:
    """Recibe los movimientos ya controlados y las reglas del documento.
    Devuelve el DataFrame con las cinco columnas, una fila por movimiento.
    """
    filas = [[movimiento.fecha, movimiento.codigo, movimiento.descripcion, movimiento.monto_centavos,
              CLASE_GASTO_BANCARIO if es_gasto(movimiento.codigo, reglas) else CLASE_MOVIMIENTO]
             for movimiento in movimientos]
    tabla = pandas.DataFrame(filas, columns=COLUMNAS)
    # Tipos fijos, aunque no haya filas: fecha real, texto y centavos enteros.
    return tabla.astype({"Fecha": "datetime64[ns]", "Código": str, "Descripción": str,
                         "Monto en centavos": "int64", "Clase": str})
