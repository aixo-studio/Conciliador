"""Paso 3 del proceso: controlar, después del cruce, que no se perdió nada.

Compara el resultado de un documento contra su tabla tal como llegó de la
etapa 1, que nunca se modificó. Si algo no cierra, frena y dice qué regla
falló; así el error indica en qué parte del proceso está el problema.
"""
import pandas

from motor.entrada import CRUZADO, SIN_CRUZAR
from motor.recibir import CLASE_GASTO_BANCARIO, COLUMNAS, ESTADO, GASTO_BANCARIO

MONTO = "Monto en centavos"
# Los únicos estados con los que puede terminar una fila.
ESTADOS = [CRUZADO, SIN_CRUZAR, GASTO_BANCARIO]


def controlar(resultado: pandas.DataFrame, recibida: pandas.DataFrame) -> dict:
    """Recibe el resultado de un documento (sus cinco columnas más el Estado) y
    la tabla tal como llegó. Controla que estén todas las filas, que sumen lo
    mismo, que cada fila sea la que llegó y que cada Estado sea válido y
    coincida con su Clase. Si algo no cierra, frena con un error.
    Devuelve el resumen: filas y suma (en centavos) de la entrada y de cada Estado.
    """
    # 1. Ninguna fila perdida ni duplicada.
    if len(resultado) != len(recibida):
        raise ValueError(f"se perdieron o se duplicaron filas: llegaron {len(recibida)} "
                         f"y quedaron {len(resultado)}.")
    # 2. La plata es la misma. Son centavos enteros: la comparación es exacta.
    llego, quedo = int(recibida[MONTO].sum()), int(resultado[MONTO].sum())
    if quedo != llego:
        raise ValueError(f"la suma no cierra: llegó {llego / 100:.2f} y quedó {quedo / 100:.2f}.")
    # 3. Cada fila es la que llegó, en el mismo lugar. Atrapa lo que las dos
    #    cuentas de arriba no ven: dos errores que se compensan, o un dato cambiado.
    filas_que_llegaron = recibida.itertuples(index=False, name=None)
    filas_que_quedaron = resultado[COLUMNAS].itertuples(index=False, name=None)
    for numero, (fila_llego, fila_quedo) in enumerate(zip(filas_que_llegaron, filas_que_quedaron), start=1):
        if fila_quedo != fila_llego:
            raise ValueError(f"la fila {numero} no es la que llegó: llegó {fila_llego} y quedó {fila_quedo}.")
    # 4 y 5. Cada Estado es uno de los tres, y coincide con su Clase: un gasto
    #    bancario termina como "Gasto bancario" y un movimiento nunca.
    for numero, (clase, estado) in enumerate(zip(resultado["Clase"], resultado[ESTADO]), start=1):
        if estado not in ESTADOS:
            raise ValueError(f"fila {numero}: el Estado no es válido ({estado!r}).")
        if clase == CLASE_GASTO_BANCARIO and estado != GASTO_BANCARIO:
            raise ValueError(f'fila {numero}: es un gasto bancario y quedó "{estado}".')
        if clase != CLASE_GASTO_BANCARIO and estado == GASTO_BANCARIO:
            raise ValueError(f'fila {numero}: es un movimiento y quedó "{estado}".')
    # Con todo lo anterior, Cruzado + Sin cruzar + Gasto bancario da la entrada.
    resumen = {"Entrada": (len(recibida), llego)}
    for estado in ESTADOS:
        montos = resultado.loc[resultado[ESTADO] == estado, MONTO]
        resumen[estado] = (len(montos), int(montos.sum()))
    return resumen
