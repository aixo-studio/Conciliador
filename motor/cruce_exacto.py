"""Paso 2 del proceso: el cruce exacto.

Una fila del banco cruza con una del sistema si tienen la misma fecha y el
mismo monto (en centavos). Si la misma fecha y el mismo monto se repiten de los
dos lados, se emparejan en orden: el primero del banco con el primero del
sistema, el segundo con el segundo, y así. Lo que sobra queda "Sin cruzar".
"""
from collections import defaultdict, deque

from motor.entrada import CRUZADO, Movimiento

CRITERIO = "Exacto"


def cruzar_exacto(banco: list[Movimiento], sistema: list[Movimiento]) -> int:
    """Recibe los movimientos del banco y los del sistema.
    Marca como "Cruzado" cada par con la misma fecha y el mismo monto, y le pone
    el mismo número de cruce a las dos filas. Devuelve cuántos cruces hubo.
    """
    # Las filas del sistema, agrupadas por fecha y monto, en el orden del archivo.
    disponibles = defaultdict(deque)
    for movimiento in sistema:
        disponibles[(movimiento.fecha, movimiento.monto_centavos)].append(movimiento)
    cruces = 0
    # Se recorre el banco en orden: cada fila toma la primera del sistema que coincide
    # y que todavía no se usó.
    for del_banco in banco:
        candidatos = disponibles[(del_banco.fecha, del_banco.monto_centavos)]
        if not candidatos:
            continue
        del_sistema = candidatos.popleft()
        cruces += 1
        for movimiento in (del_banco, del_sistema):
            movimiento.estado = CRUZADO
            movimiento.numero_cruce = cruces
            movimiento.criterio = CRITERIO
    return cruces
