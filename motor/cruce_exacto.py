"""Paso 2 del proceso: el cruce exacto.

Trabaja sobre las dos tablas de una cuenta (la del banco y la del sistema), ya
recibidas y con su columna Estado. Una fila del banco cruza con una del sistema
si tienen la misma fecha y el mismo monto (en centavos). Si la misma fecha y el
mismo monto se repiten de los dos lados, se emparejan en orden: el primero del
banco con el primero del sistema, el segundo con el segundo, y así.

Solo cruzan las filas "Sin cruzar": un gasto bancario nunca entra al cruce,
aunque tenga una pareja perfecta. Lo que no encuentra pareja queda "Sin cruzar".
"""
from collections import defaultdict, deque

import pandas

from motor.recibir import CRUZADO, ESTADO, SIN_CRUZAR

# La columna de la pareja de cada tabla. El número es la fila de la OTRA hoja
# del Excel de salida: el encabezado es la fila 1 y los datos empiezan en la 2,
# así que quien busca ese número en el archivo cae en la fila justa.
COLUMNA_PAREJA = {False: "Fila en Sistema", True: "Fila en Banco"}
PRIMERA_FILA_DE_DATOS = 2


def preparar_columna_de_pareja(tabla: pandas.DataFrame, es_sistema: bool) -> None:
    """Recibe una tabla y de qué lado es. Si todavía no tiene su columna de
    pareja, se la agrega vacía: enteros que admiten celdas vacías ("Int64"),
    porque una fila sin cruzar no lleva número. La completa el cruce.
    """
    columna = COLUMNA_PAREJA[es_sistema]
    if columna not in tabla.columns:
        tabla[columna] = pandas.array([pandas.NA] * len(tabla), dtype="Int64")


def cruzar_exacto(banco: pandas.DataFrame, sistema: pandas.DataFrame) -> int:
    """Modifica las dos tablas de trabajo que recibe.
    Para cada pareja con la misma fecha y el mismo monto, cambia el Estado de
    ambas filas a "Cruzado" y anota en cada una la fila de su pareja en el Excel.
    Devuelve solo la cantidad de parejas que cruzó.
    """
    preparar_columna_de_pareja(banco, es_sistema=False)
    preparar_columna_de_pareja(sistema, es_sistema=True)
    # Dónde está cada columna que se escribe, para marcar por posición de fila.
    estado_banco, pareja_banco = banco.columns.get_loc(ESTADO), banco.columns.get_loc("Fila en Sistema")
    estado_sistema, pareja_sistema = sistema.columns.get_loc(ESTADO), sistema.columns.get_loc("Fila en Banco")
    # Las filas del sistema que esperan pareja, agrupadas por fecha y monto, en
    # el orden del archivo. Los gastos bancarios no entran: no están "Sin cruzar".
    disponibles = defaultdict(deque)
    for posicion, (fecha, monto, estado) in enumerate(
            zip(sistema["Fecha"], sistema["Monto en centavos"], sistema[ESTADO])):
        if estado == SIN_CRUZAR:
            disponibles[(fecha, monto)].append(posicion)
    cruces = 0
    # Se recorre el banco en orden: cada fila "Sin cruzar" toma la primera del
    # sistema que coincide y que todavía no se usó.
    for posicion, (fecha, monto, estado) in enumerate(
            zip(banco["Fecha"], banco["Monto en centavos"], banco[ESTADO])):
        if estado != SIN_CRUZAR:
            continue
        candidatos = disponibles[(fecha, monto)]
        if not candidatos:
            continue
        del_sistema = candidatos.popleft()
        cruces += 1
        # Cada una queda "Cruzado" y anota la fila de su pareja en el otro lado.
        banco.iat[posicion, estado_banco] = CRUZADO
        banco.iat[posicion, pareja_banco] = del_sistema + PRIMERA_FILA_DE_DATOS
        sistema.iat[del_sistema, estado_sistema] = CRUZADO
        sistema.iat[del_sistema, pareja_sistema] = posicion + PRIMERA_FILA_DE_DATOS
    return cruces
