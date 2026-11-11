"""Paso 1 del proceso: recibir la tabla de un documento y dejarla lista para el cruce.

La tabla es el DataFrame que devuelve la etapa 1 ("conciliacion v3"). Acá se
controla que tenga la forma acordada y se le agrega el Estado de cada fila.
La tabla recibida nunca se modifica: el Estado va en una copia y la original
queda de testigo, para comparar contra ella en el control del final.
"""
from datetime import datetime

import pandas

from motor.entrada import SIN_CRUZAR

# Lo que este repo espera recibir de la etapa 1. Está escrito acá, y no se toma
# de v3, a propósito: si v3 cambiara algo por error, este control lo frena.
COLUMNAS = ["Fecha", "Código", "Descripción", "Monto en centavos", "Clase"]
CLASE_MOVIMIENTO = "Movimiento"
CLASE_GASTO_BANCARIO = "Gasto bancario"

# La columna que agrega este repo, y el estado con el que arranca cada Clase.
ESTADO = "Estado"
GASTO_BANCARIO = "Gasto bancario"
ESTADO_INICIAL = {CLASE_MOVIMIENTO: SIN_CRUZAR, CLASE_GASTO_BANCARIO: GASTO_BANCARIO}

# Cuántos errores de fila se muestran en el mensaje; del resto se dice solo cuántos son.
ERRORES_A_MOSTRAR = 20


def controlar_forma(tabla: pandas.DataFrame, es_sistema: bool) -> None:
    """Recibe la tabla de un documento y si es el libro del sistema.
    Controla que tenga la forma acordada con la etapa 1: las cinco columnas, al
    menos una fila y, en cada fila, el tipo de dato de cada columna. Si algo no
    cumple, frena con un error que dice qué. No devuelve nada.
    """
    if list(tabla.columns) != COLUMNAS:
        raise ValueError(f"las columnas tienen que ser {' · '.join(COLUMNAS)}; "
                         f"llegaron: {' · '.join(str(columna) for columna in tabla.columns)}.")
    if tabla.empty:
        raise ValueError("no tiene movimientos.")
    # Se revisan todas las filas y se informan juntas, así se corrigen de una vez.
    # La fila 1 es el primer movimiento de la tabla.
    errores = []
    for numero, fila in enumerate(tabla.itertuples(index=False, name=None), start=1):
        problema = problema_de_la_fila(fila, es_sistema)
        if problema:
            errores.append(f"fila {numero}: {problema}")
    if errores:
        raise ValueError(explicar_errores_de_filas(errores))


def problema_de_la_fila(fila: tuple, es_sistema: bool) -> str | None:
    """Recibe los cinco valores de una fila y si es del libro del sistema.
    Devuelve qué tiene mal (lo primero que encuentra), o None si está bien.
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


def explicar_errores_de_filas(errores: list[str]) -> str:
    """Recibe los errores de las filas. Devuelve un solo mensaje con los primeros
    y, si hay más, cuántos quedan sin mostrar.
    """
    titulo = f"hay {len(errores)} fila{'s' if len(errores) != 1 else ''} con errores:"
    lineas = [titulo] + [f"  {error}" for error in errores[:ERRORES_A_MOSTRAR]]
    if len(errores) > ERRORES_A_MOSTRAR:
        lineas.append(f"  … y {len(errores) - ERRORES_A_MOSTRAR} más.")
    return "\n".join(lineas)


def recibir_documento(tabla: pandas.DataFrame, es_sistema: bool) -> tuple[pandas.DataFrame, pandas.DataFrame]:
    """Recibe la tabla de un documento y si es el libro del sistema. Es la única
    puerta por la que un documento entra al proceso.
    Controla la forma (si no cumple, frena sin devolver nada) y devuelve dos
    tablas: la recibida, intacta, que queda de testigo para el control del
    final, y la copia con el Estado, sobre la que trabaja el cruce.
    """
    controlar_forma(tabla, es_sistema)
    return tabla, poner_estado(tabla)


def poner_estado(tabla: pandas.DataFrame) -> pandas.DataFrame:
    """Recibe la tabla de un documento, ya controlada.
    Devuelve una copia con la columna Estado: "Sin cruzar" para los movimientos
    y "Gasto bancario" para los gastos bancarios. La tabla recibida no cambia.
    """
    resultado = tabla.copy()
    resultado[ESTADO] = tabla["Clase"].map(ESTADO_INICIAL)
    return resultado
