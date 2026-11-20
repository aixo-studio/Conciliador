"""Paso 3 del proceso: controlar que el cruce no perdió ni cambió nada.

La idea es simple: con lo que devolvió el cruce se vuelve a armar lo que entró.
Si al sacarle a una tabla original las filas que cruzaron no queda exactamente
lo pendiente, algo se perdió, se duplicó o se modificó, y no se entrega nada.
"""
import pandas

from conciliador.motor.cruce_exacto import COLUMNA_PAREJA
from conciliador.motor.recibir import CLASE_GASTO_BANCARIO, COLUMNAS, MONTO


def validar_y_resumir_cruce(cruces: pandas.DataFrame, banco_pendiente: pandas.DataFrame,
                            erp_pendiente: pandas.DataFrame, tabla_banco: pandas.DataFrame,
                            tabla_erp: pandas.DataFrame) -> dict:
    """Recibe las tres tablas que devolvió el cruce y las dos que entraron.
    Controla que no se haya perdido, duplicado ni cambiado ninguna fila.
    Devuelve el resumen de cada lado: filas y suma, en centavos, de lo que
    entró, lo que cruzó y lo que quedó pendiente. Si algo no cierra, frena.
    """
    validar_parejas(cruces, tabla_erp)
    validar_que_no_cruzaron_gastos(cruces)
    filas_del_erp = list(cruces[COLUMNA_PAREJA])
    # El banco: las filas de la tabla de cruces tienen que ser tal cual las que
    # entraron, y lo pendiente, todo el resto.
    if not cruces[COLUMNAS].equals(tabla_banco.loc[cruces.index]):
        raise ValueError("las filas de la tabla de cruces no son las que entraron del banco.")
    if not banco_pendiente.equals(tabla_banco.drop(cruces.index)):
        raise ValueError("el banco pendiente no es lo que entró menos lo que cruzó.")
    # El ERP: lo pendiente tiene que ser lo que entró menos las filas que nombra
    # la columna de parejas.
    if not erp_pendiente.equals(tabla_erp.drop(filas_del_erp)):
        raise ValueError("el ERP pendiente no es lo que entró menos lo que cruzó.")
    cruzado_del_erp = tabla_erp.loc[filas_del_erp]
    # Cada pareja es por el mismo monto, así que los dos lados tienen que sumar
    # lo mismo. Si no, las parejas se desalinearon.
    if medir(cruces)[1] != medir(cruzado_del_erp)[1]:
        raise ValueError("lo cruzado no suma lo mismo en el banco y en el ERP.")
    gastos = banco_pendiente[banco_pendiente["Clase"] == CLASE_GASTO_BANCARIO]
    return {"Banco": {"Entrada": medir(tabla_banco), "Cruzado": medir(cruces),
                      "Pendiente": medir(banco_pendiente), "Gasto bancario": medir(gastos)},
            "ERP": {"Entrada": medir(tabla_erp), "Cruzado": medir(cruzado_del_erp),
                    "Pendiente": medir(erp_pendiente)}}


def validar_parejas(cruces: pandas.DataFrame, tabla_erp: pandas.DataFrame) -> None:
    """Controla que cada fila cruce una sola vez de cada lado y que los números
    de la columna de parejas sean filas que existen en el ERP.
    """
    if cruces.index.has_duplicates:
        raise ValueError("hay filas del banco que cruzaron más de una vez.")
    filas = cruces[COLUMNA_PAREJA]
    repetidas = filas[filas.duplicated()]
    if len(repetidas):
        raise ValueError(f"la fila {int(repetidas.iloc[0])} del ERP cruzó con más de una del banco.")
    desconocidas = [str(int(fila)) for fila in filas if fila not in tabla_erp.index]
    if desconocidas:
        raise ValueError(f'la columna "{COLUMNA_PAREJA}" nombra filas que no existen '
                         f'en el ERP: {", ".join(desconocidas[:5])}.')


def validar_que_no_cruzaron_gastos(cruces: pandas.DataFrame) -> None:
    """Un gasto bancario no se cruza nunca: no puede aparecer en los cruces."""
    gastos = cruces.index[cruces["Clase"] == CLASE_GASTO_BANCARIO]
    if len(gastos):
        raise ValueError(f"la fila {int(gastos[0])} del banco es un gasto bancario y cruzó.")


def medir(tabla: pandas.DataFrame) -> tuple[int, int]:
    """Devuelve cuántas filas tiene una tabla y cuánto suman sus montos, en centavos."""
    return len(tabla), int(tabla[MONTO].sum())
