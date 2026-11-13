"""Ayudas para las pruebas: arman tablas de entrada inventadas, como las devuelve la etapa 1."""
from datetime import datetime

import pandas

from motor.recibir import COLUMNAS


def dia(numero):
    """Devuelve la fecha de ese día de septiembre de 2026."""
    return datetime(2026, 9, numero)


def tabla(filas):
    """Recibe filas (día, código, descripción, centavos, clase). Devuelve la tabla
    (DataFrame) con la forma y los tipos que entrega la etapa 1.
    """
    armadas = [(dia(numero), codigo, descripcion, centavos, clase)
               for numero, codigo, descripcion, centavos, clase in filas]
    return pandas.DataFrame(armadas, columns=COLUMNAS).astype(
        {"Fecha": "datetime64[ns]", "Código": str, "Descripción": str,
         "Monto en centavos": "int64", "Clase": str})
