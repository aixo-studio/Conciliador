"""Valida los DataFrames de entrada y prepara las copias para el cruce.

La tabla original tiene cinco columnas y sirve de referencia para el control
final. La copia de trabajo conserva esas columnas y agrega Estado como sexta.
Quien llama indica con es_sistema si la tabla es del libro del sistema.
"""
from datetime import datetime

import pandas

# Lo que este repo espera recibir de la etapa 1. Está escrito acá, y no se toma
# de v3, a propósito: si v3 cambiara algo por error, este control lo frena.
COLUMNAS = ["Fecha", "Código", "Descripción", "Monto en centavos", "Clase"]
CLASE_MOVIMIENTO = "Movimiento"
CLASE_GASTO_BANCARIO = "Gasto bancario"

# La columna que agrega este repo y sus tres estados posibles: con qué arranca
# cada Clase, y "Cruzado", que lo pone el cruce cuando encuentra la pareja.
ESTADO = "Estado"
SIN_CRUZAR = "Sin cruzar"
CRUZADO = "Cruzado"
GASTO_BANCARIO = "Gasto bancario"
ESTADO_INICIAL = {CLASE_MOVIMIENTO: SIN_CRUZAR, CLASE_GASTO_BANCARIO: GASTO_BANCARIO}

# Cuántos errores de fila se muestran en el mensaje; del resto se dice solo cuántos son.
ERRORES_A_MOSTRAR = 20


def validar_tabla_de_entrada(tabla: pandas.DataFrame, es_sistema: bool) -> None:
    """Verifica que estén las cinco columnas acordadas en orden y que haya movimientos.
    Revisa los datos de cada fila. Si es el libro del sistema, todas las filas
    deben tener Clase "Movimiento". Si la tabla es inválida, informa los errores.
    """
    if list(tabla.columns) != COLUMNAS:
        raise ValueError(f"las columnas tienen que ser {' · '.join(COLUMNAS)}; "
                         f"llegaron: {' · '.join(str(columna) for columna in tabla.columns)}.")
    if tabla.empty:
        raise ValueError("no tiene movimientos.")
    # Se revisan todas las filas y se informan juntas, así se corrigen de una vez.
    # En los errores, la fila 1 es el primer movimiento de la tabla.
    errores = []
    for numero, fila in enumerate(tabla.itertuples(index=False, name=None), start=1):
        error = detectar_error_de_fila(fila, es_sistema)
        if error:
            errores.append(f"fila {numero}: {error}")
    if errores:
        raise ValueError(formatear_errores_de_filas(errores))


def detectar_error_de_fila(fila: tuple, es_sistema: bool) -> str | None:
    """Recibe los cinco valores de una fila y si es del libro del sistema.
    Devuelve el primer error de la fila, o None si todos sus valores son válidos.
    """
    fecha, codigo, descripcion, monto, clase = fila
    # Una fecha vacía llega como NaT ("no es una fecha"); por eso se pregunta aparte.
    if not isinstance(fecha, datetime) or pandas.isna(fecha):
        return f"la Fecha no es una fecha ({fecha!r})."
    # El Código como número ya perdió sus ceros de adelante ("005" quedó en 5).
    if not isinstance(codigo, str):
        return f"el Código no es texto ({codigo!r})."
    if not isinstance(descripcion, str):
        return f"la Descripción no es texto ({descripcion!r})."
    # Para Python, verdadero/falso también es un entero; se descarta aparte.
    if isinstance(monto, bool) or not isinstance(monto, int):
        return f"el Monto en centavos no es un entero ({monto!r})."
    if clase not in ESTADO_INICIAL:
        return (f'la Clase tiene que ser "{CLASE_MOVIMIENTO}" o "{CLASE_GASTO_BANCARIO}" '
                f"({clase!r}).")
    if es_sistema and clase == CLASE_GASTO_BANCARIO:
        return "es un gasto bancario, y el libro del sistema no tiene gastos bancarios."
    return None


def formatear_errores_de_filas(errores: list[str]) -> str:
    """Recibe los errores de las filas. Devuelve un solo mensaje con los primeros
    y, si hay más, cuántos quedan sin mostrar.
    """
    titulo = f"hay {len(errores)} fila{'s' if len(errores) != 1 else ''} con errores:"
    lineas = [titulo] + [f"  {error}" for error in errores[:ERRORES_A_MOSTRAR]]
    if len(errores) > ERRORES_A_MOSTRAR:
        lineas.append(f"  … y {len(errores) - ERRORES_A_MOSTRAR} más.")
    return "\n".join(lineas)


def crear_copia_con_estado(tabla: pandas.DataFrame) -> pandas.DataFrame:
    """Recibe la tabla de un documento, ya controlada.
    Devuelve una copia con la columna Estado: "Sin cruzar" para los movimientos
    y "Gasto bancario" para los gastos bancarios. La tabla recibida no cambia.
    """
    tabla_de_trabajo = tabla.copy()
    tabla_de_trabajo[ESTADO] = tabla_de_trabajo["Clase"].map(ESTADO_INICIAL)
    return tabla_de_trabajo
