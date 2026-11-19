"""Paso 2 del proceso: el cruce exacto.

Recibe las dos tablas de una cuenta tal como llegaron y trabaja sobre copias:
las originales no se tocan y quedan de referencia para el control del final.

Una fila del banco cruza con una del ERP si tienen la misma fecha y el mismo
monto. Si la misma fecha y el mismo monto se repiten de los dos lados, se
emparejan en orden: la primera del banco con la primera del ERP, la segunda
con la segunda, y así.

Solo se cruzan los movimientos: un gasto bancario no busca pareja ni puede ser
la pareja de nadie, aunque coincida exacto.

Devuelve tres tablas: la de los cruces y lo que quedó pendiente de cada lado.
"""
from collections import defaultdict, deque

import pandas

from motor.recibir import CLASE_MOVIMIENTO, MONTO

# La sexta columna de la tabla de cruces: el número de fila del ERP con el que
# cruzó cada fila del banco. Es el número tal cual lo nombra la tabla que
# llegó, así que sirve para ir a buscarla sin ninguna cuenta en el medio.
COLUMNA_PAREJA = "Fila en ERP"


def cruzar_exacto(tabla_banco: pandas.DataFrame, tabla_erp: pandas.DataFrame
                  ) -> tuple[pandas.DataFrame, pandas.DataFrame, pandas.DataFrame]:
    """Recibe las dos tablas de una cuenta, con las cinco columnas del contrato.
    Devuelve tres tablas, en este orden: los cruces (las filas del banco que
    cruzaron, con el número de fila de su pareja en el ERP), el banco pendiente
    (lo que no cruzó, más los gastos bancarios) y el ERP pendiente.
    Las dos tablas que entran no se modifican.
    """
    banco = tabla_banco.copy()
    erp = tabla_erp.copy()
    parejas = buscar_parejas(banco, erp)
    filas_del_banco = [del_banco for del_banco, _ in parejas]
    filas_del_erp = [del_erp for _, del_erp in parejas]
    cruces = banco.loc[filas_del_banco].copy()
    # El tipo se fija siempre, aunque no haya cruzado nada: quien recibe la
    # tabla encuentra la columna con números enteros, esté vacía o llena.
    cruces[COLUMNA_PAREJA] = pandas.array(filas_del_erp, dtype="int64")
    return cruces, banco.drop(filas_del_banco), erp.drop(filas_del_erp)


def buscar_parejas(banco: pandas.DataFrame, erp: pandas.DataFrame) -> list[tuple[int, int]]:
    """Recorre una vez cada tabla. Devuelve los pares (fila del banco, fila del
    ERP) que cruzaron, en el orden del banco.
    """
    # Las filas del ERP que esperan pareja, agrupadas por fecha y monto, en el
    # orden de la tabla. Un gasto bancario no entra: no puede ser pareja de nadie.
    disponibles = defaultdict(deque)
    for fila, fecha, monto, clase in zip(erp.index, erp["Fecha"], erp[MONTO], erp["Clase"]):
        if clase == CLASE_MOVIMIENTO:
            disponibles[(fecha, monto)].append(fila)
    parejas = []
    for fila, fecha, monto, clase in zip(banco.index, banco["Fecha"], banco[MONTO], banco["Clase"]):
        # Un gasto bancario del banco ni siquiera busca pareja.
        if clase != CLASE_MOVIMIENTO:
            continue
        # Se consulta con get: preguntar por una fecha y un monto que el ERP no
        # tiene no los agrega a la lista de los que esperan.
        esperando = disponibles.get((fecha, monto))
        if not esperando:
            continue
        parejas.append((fila, esperando.popleft()))
    return parejas
