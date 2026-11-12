"""Paso 3: valida cada tabla después del cruce y resume sus movimientos."""
import pandas

from motor.recibir import CLASE_GASTO_BANCARIO, COLUMNAS, CRUZADO, ESTADO, GASTO_BANCARIO, SIN_CRUZAR

MONTO = "Monto en centavos"
# Los únicos estados con los que puede terminar una fila.
ESTADOS = [CRUZADO, SIN_CRUZAR, GASTO_BANCARIO]


def validar_y_resumir_tabla_cruzada(
    tabla_cruzada: pandas.DataFrame, tabla_original: pandas.DataFrame
) -> dict:
    """Compara la tabla cruzada de siete columnas con la original de cinco.
    Verifica que se conserven las filas, su orden y sus datos, y que cada
    Estado sea válido para su Clase. Si falla un control, informa el error.
    Devuelve la cantidad de filas y el total en centavos de la entrada y de cada Estado.
    """
    # 1. Ninguna fila perdida ni duplicada.
    if len(tabla_cruzada) != len(tabla_original):
        raise ValueError(f"se perdieron o se duplicaron filas: llegaron {len(tabla_original)} "
                         f"y quedaron {len(tabla_cruzada)}.")
    # 2. La plata es la misma. Son centavos enteros: la comparación es exacta.
    total_original_en_centavos = int(tabla_original[MONTO].sum())
    total_de_tabla_cruzada_en_centavos = int(tabla_cruzada[MONTO].sum())
    if total_de_tabla_cruzada_en_centavos != total_original_en_centavos:
        raise ValueError(f"la suma no cierra: llegó {total_original_en_centavos / 100:.2f} "
                         f"y quedó {total_de_tabla_cruzada_en_centavos / 100:.2f}.")
    # 3. Compara las cinco columnas de entrada en la misma posición.
    #    Así detecta cambios que se compensan en el total. Estado se valida aparte.
    filas_originales = tabla_original.itertuples(index=False, name=None)
    filas_cruzadas = tabla_cruzada[COLUMNAS].itertuples(index=False, name=None)
    for numero, (fila_original, fila_cruzada) in enumerate(zip(filas_originales, filas_cruzadas), start=1):
        if fila_cruzada != fila_original:
            raise ValueError(f"la fila {numero} no es la que llegó: llegó {fila_original} y quedó {fila_cruzada}.")
    # 4 y 5. Cada Estado es uno de los tres, y coincide con su Clase: un gasto
    #    bancario termina como "Gasto bancario" y un movimiento nunca.
    for numero, (clase, estado) in enumerate(zip(tabla_cruzada["Clase"], tabla_cruzada[ESTADO]), start=1):
        if estado not in ESTADOS:
            raise ValueError(f"fila {numero}: el Estado no es válido ({estado!r}).")
        if clase == CLASE_GASTO_BANCARIO and estado != GASTO_BANCARIO:
            raise ValueError(f'fila {numero}: es un gasto bancario y quedó "{estado}".')
        if clase != CLASE_GASTO_BANCARIO and estado == GASTO_BANCARIO:
            raise ValueError(f'fila {numero}: es un movimiento y quedó "{estado}".')
    # Con todo lo anterior, Cruzado + Sin cruzar + Gasto bancario da la entrada.
    resumen = {"Entrada": (len(tabla_original), total_original_en_centavos)}
    for estado in ESTADOS:
        montos = tabla_cruzada.loc[tabla_cruzada[ESTADO] == estado, MONTO]
        resumen[estado] = (len(montos), int(montos.sum()))
    return resumen
