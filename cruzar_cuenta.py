"""La puerta de entrada: cruza una cuenta (el extracto del banco contra el
libro del sistema) de punta a punta.

Recibe las dos tablas tal como las devuelve la etapa 1 ("conciliacion v3") y
la ruta del Excel de salida. Conseguir las tablas (llamando a v3) y la
terminal son la comunicación entre los repos (APR-235, ver PENDIENTES.md).
"""
from pathlib import Path

import pandas

from motor.controlar import validar_y_resumir_tabla_cruzada
from motor.cruce_exacto import cruzar_exacto
from motor.recibir import crear_copia_con_estado, validar_tabla_de_entrada
from motor.salida import validar_cruce_entre_tablas, escribir_excel


def cruzar_cuenta(tabla_banco: pandas.DataFrame, tabla_sistema: pandas.DataFrame,
                  ruta_salida: Path | str) -> dict:
    """Recibe las dos tablas de una cuenta y dónde guardar el Excel.
    Corre todo el proceso: controla la forma, pone el Estado, cruza, controla
    que no se perdió nada y escribe el Excel. Si algo no cumple o no cierra,
    frena con un error que dice por qué, y no escribe nada.
    Devuelve los cruces y el resumen de cada lado (filas y suma por Estado).
    """
    validar_tabla_de_entrada(tabla_banco, es_sistema=False)
    validar_tabla_de_entrada(tabla_sistema, es_sistema=True)
    banco_para_cruce = crear_copia_con_estado(tabla_banco)
    sistema_para_cruce = crear_copia_con_estado(tabla_sistema)
    cruces = cruzar_exacto(banco_para_cruce, sistema_para_cruce)
    resumenes = {
        "Banco": validar_y_resumir_tabla_cruzada(banco_para_cruce, tabla_banco),
        "Sistema": validar_y_resumir_tabla_cruzada(sistema_para_cruce, tabla_sistema),
    }
    validar_cruce_entre_tablas(banco_para_cruce, sistema_para_cruce)
    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    escribir_excel(banco_para_cruce, sistema_para_cruce, resumenes, ruta)
    return {"cruces": cruces, **resumenes}
