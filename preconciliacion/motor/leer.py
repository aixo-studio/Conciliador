"""Pasos 1 y 2 del proceso: abrir el archivo y encontrar la tabla de movimientos.

No sabe nada de ningún banco: recibe los encabezados de las columnas que usa
cada documento (salen de configuracion.toml) y busca la tabla que los tiene.
"""
from pathlib import Path

import openpyxl
import xlrd


def leer_filas(ruta: Path) -> list[list]:
    """Recibe la ruta de un Excel (.xls o .xlsx).
    Devuelve todas las filas de la primera hoja, cada una como una lista de valores.
    """
    # .xls es el formato viejo de Excel y lo lee xlrd; .xlsx lo lee openpyxl.
    if ruta.suffix.lower() == ".xls":
        hoja = xlrd.open_workbook(ruta).sheet_by_index(0)
        return [hoja.row_values(numero) for numero in range(hoja.nrows)]
    # Sin read_only: hay sistemas que guardan mal el tamaño de la hoja y en ese
    # modo el archivo se lee vacío.
    libro = openpyxl.load_workbook(ruta, data_only=True)
    return [list(fila) for fila in libro.worksheets[0].iter_rows(values_only=True)]


def encontrar_tabla(filas: list[list], encabezados: list[str],
                    seguidas: list[str] = None) -> tuple[dict, list]:
    """Recibe todas las filas del archivo y los encabezados que tiene que tener la tabla
    (solo las columnas que se usan; las demás pueden venir o no).
    Busca la fila que tiene todos esos encabezados y devuelve dos cosas:
    - dónde está cada columna: {"Fecha": 0, "Codigo": 3, ...}
    - las filas de abajo, cada una con su número de fila en el Excel original.
    Si no la encuentra, frena con un error que dice qué columnas faltan.

    "seguidas" es opcional: columnas que tienen que estar una al lado de la otra,
    en ese orden. Sirve cuando un nombre aparece dos veces en el archivo: se usa
    el que está en ese grupo. Si el grupo no está, frena en vez de elegir uno.

    Se busca por encabezados y no por número de fila para que siga funcionando
    si el banco agrega o saca líneas de título arriba.
    """
    for posicion, fila in enumerate(filas):
        nombres = [str(celda).strip() if celda is not None else "" for celda in fila]
        if all(encabezado in nombres for encabezado in encabezados):
            # index() da la primera aparición de cada encabezado.
            columnas = {encabezado: nombres.index(encabezado) for encabezado in encabezados}
            # Las columnas del grupo "seguidas" se toman de donde está el grupo.
            if seguidas:
                inicio = buscar_seguidas(nombres, seguidas)
                columnas.update({nombre: inicio + paso for paso, nombre in enumerate(seguidas)})
            # +2 porque Excel cuenta desde 1 y los datos empiezan debajo del encabezado.
            datos = [(posicion + 2 + indice, fila_de_datos)
                     for indice, fila_de_datos in enumerate(filas[posicion + 1:])]
            return columnas, datos
    raise ValueError(explicar_encabezados_faltantes(filas, encabezados))


def explicar_encabezados_faltantes(filas: list[list], encabezados: list[str]) -> str:
    """Recibe las filas del archivo y los encabezados esperados, cuando ninguna fila
    los tiene todos. Devuelve el mensaje de error: si una fila tiene al menos la
    mitad, dice en qué fila está y qué columnas le faltan; si no, que ninguna se parece.
    """
    mejor_posicion, mejor_faltantes = None, encabezados
    for posicion, fila in enumerate(filas):
        nombres = {str(celda).strip() for celda in fila if celda is not None}
        faltantes = [encabezado for encabezado in encabezados if encabezado not in nombres]
        if len(faltantes) < len(mejor_faltantes):
            mejor_posicion, mejor_faltantes = posicion, faltantes
    # Con menos de la mitad no es una columna que cambió: es otro documento.
    if mejor_posicion is None or len(mejor_faltantes) > len(encabezados) / 2:
        return "Ninguna fila tiene sus encabezados. Se esperaba: " + ", ".join(encabezados) + "."
    # +1 porque Excel cuenta las filas desde 1.
    return f"En la fila {mejor_posicion + 1} faltan estas columnas: " + ", ".join(mejor_faltantes) + "."


def buscar_seguidas(nombres: list[str], seguidas: list[str]) -> int:
    """Recibe los nombres de la fila de encabezados y un grupo de columnas.
    Devuelve dónde empieza el grupo, si sus columnas están juntas y en ese orden.
    Si no están así, frena con un error.
    """
    largo = len(seguidas)
    for inicio in range(len(nombres) - largo + 1):
        if nombres[inicio:inicio + largo] == seguidas:
            return inicio
    raise ValueError("Las columnas " + " | ".join(seguidas) + " no están juntas y en ese "
                     "orden. Revisá si cambió el formato del archivo.")
