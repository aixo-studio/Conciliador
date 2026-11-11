"""La puerta de entrada: cruza una cuenta (el extracto del banco contra el
libro del sistema) de punta a punta.

Recibe las dos tablas tal como las devuelve la etapa 1 ("conciliacion v3") y
la ruta del Excel de salida. Conseguir las tablas (llamando a v3) y la
terminal son la comunicación entre los repos (APR-235, ver PENDIENTES.md).
"""
from pathlib import Path

import pandas

from motor.controlar import controlar
from motor.cruce_exacto import cruzar_exacto
from motor.recibir import recibir_documento
from motor.salida import controlar_lados, escribir_excel


def cruzar_cuenta(tabla_banco: pandas.DataFrame, tabla_sistema: pandas.DataFrame,
                  ruta_salida: Path | str) -> dict:
    """Recibe las dos tablas de una cuenta y dónde guardar el Excel.
    Corre todo el proceso: controla la forma, pone el Estado, cruza, controla
    que no se perdió nada y escribe el Excel. Si algo no cumple o no cierra,
    frena con un error que dice por qué, y no escribe nada.
    Devuelve los cruces y el resumen de cada lado (filas y suma por Estado).
    """
    recibida_banco, banco = recibir_documento(tabla_banco, es_sistema=False)
    recibida_sistema, sistema = recibir_documento(tabla_sistema, es_sistema=True)
    cruces = cruzar_exacto(banco, sistema)
    resumenes = {"Banco": controlar(banco, recibida_banco),
                 "Sistema": controlar(sistema, recibida_sistema)}
    controlar_lados(banco, sistema)
    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    escribir_excel(banco, sistema, resumenes, ruta)
    return {"cruces": cruces, **resumenes}
