"""Paso 4 del proceso: los controles entre los dos lados y el Excel de salida.

Los controles de cada tabla por separado ya corrieron (motor/controlar.py).
Acá se controla lo que une a los dos lados y se escribe el Excel con tres
hojas: "Resumen" (los números de los controles), "Banco" y "Sistema" (todas
las filas de la entrada, en el mismo orden, con su estado y su pareja).
"""
from pathlib import Path

import pandas
from openpyxl import Workbook
from openpyxl.styles import Font

from motor.controlar import MONTO
from motor.cruce_exacto import COLUMNA_PAREJA, PRIMERA_FILA_DE_DATOS
from motor.recibir import CRUZADO, ESTADO

COLUMNAS_DE_LA_HOJA = ("Fecha", "Código", "Descripción", "Monto", "Clase", "Estado")


def controlar_lados(banco: pandas.DataFrame, sistema: pandas.DataFrame) -> None:
    """Recibe las dos tablas ya cruzadas y controladas por separado.
    Controla lo que las une: lo cruzado suma lo mismo en las dos, y las parejas
    se apuntan entre sí. Si algo no cierra, frena con un error.
    """
    sumas = {lado: int(tabla.loc[tabla[ESTADO] == CRUZADO, MONTO].sum())
             for lado, tabla in (("Banco", banco), ("Sistema", sistema))}
    if sumas["Banco"] != sumas["Sistema"]:
        raise ValueError(f"lo cruzado no suma lo mismo en el banco ({sumas['Banco'] / 100:.2f}) "
                         f"y en el sistema ({sumas['Sistema'] / 100:.2f}).")
    controlar_parejas("Banco", banco, sistema, es_sistema=False)
    controlar_parejas("Sistema", sistema, banco, es_sistema=True)


def controlar_parejas(lado: str, propios: pandas.DataFrame, otros: pandas.DataFrame,
                      es_sistema: bool) -> None:
    """Recibe un lado y el otro. Controla que cada fila "Cruzado" apunte a una
    fila "Cruzado" del otro lado que la apunte de vuelta, y que las demás no
    apunten a ninguna. Si no, frena.
    """
    for posicion, (estado, pareja) in enumerate(zip(propios[ESTADO], propios[COLUMNA_PAREJA[es_sistema]])):
        fila = posicion + PRIMERA_FILA_DE_DATOS
        # Una fila lleva pareja si y solo si está "Cruzado".
        if (estado == CRUZADO) == pandas.isna(pareja):
            raise ValueError(f"{lado} fila {fila}: el estado no coincide con su pareja.")
        if pandas.isna(pareja):
            continue
        posicion_ajena = int(pareja) - PRIMERA_FILA_DE_DATOS
        if not 0 <= posicion_ajena < len(otros):
            raise ValueError(f"{lado} fila {fila}: apunta a la fila {int(pareja)}, "
                             "que no existe en el otro lado.")
        apuntada = otros[COLUMNA_PAREJA[not es_sistema]].iat[posicion_ajena]
        if (otros[ESTADO].iat[posicion_ajena] != CRUZADO
                or pandas.isna(apuntada) or int(apuntada) != fila):
            raise ValueError(f"{lado} fila {fila}: dice que cruzó con la fila {int(pareja)} "
                             "del otro lado, pero esa fila no la apunta de vuelta.")


def filas_de_la_hoja(tabla: pandas.DataFrame, es_sistema: bool):
    """Recibe una tabla cruzada. Devuelve sus filas listas para la hoja:
    el monto en pesos y la pareja como número, o la celda vacía si no cruzó.
    """
    for fecha, codigo, descripcion, monto, clase, estado, pareja in zip(
            tabla["Fecha"], tabla["Código"], tabla["Descripción"], tabla[MONTO],
            tabla["Clase"], tabla[ESTADO], tabla[COLUMNA_PAREJA[es_sistema]]):
        yield (fecha, codigo, descripcion, int(monto) / 100, clase, estado,
               None if pandas.isna(pareja) else int(pareja))


def escribir_hoja(libro: Workbook, titulo: str, encabezado, filas, formatos: dict, anchos) -> None:
    """Recibe el libro, el nombre de la hoja, el encabezado, las filas, el formato
    de cada columna (letra → formato) y los anchos. Agrega la hoja al libro.
    """
    hoja = libro.create_sheet(titulo)
    hoja.append(list(encabezado))
    for celda in hoja[1]:
        celda.font = Font(bold=True)
    for fila in filas:
        hoja.append(list(fila))
    for letra, formato in formatos.items():
        for (celda,) in hoja.iter_rows(min_row=2, min_col=ord(letra) - 64, max_col=ord(letra) - 64):
            celda.number_format = formato
    for numero, ancho in enumerate(anchos):
        hoja.column_dimensions[chr(65 + numero)].width = ancho
    hoja.freeze_panes = "A2"  # el encabezado queda fijo al bajar


def escribir_excel(banco: pandas.DataFrame, sistema: pandas.DataFrame,
                   resumenes: dict, ruta: Path) -> None:
    """Recibe las dos tablas cruzadas, el resumen de cada lado (lo devuelve el
    control) y la ruta donde guardar. Escribe el Excel con las hojas "Resumen",
    "Banco" y "Sistema".
    """
    libro = Workbook()
    libro.remove(libro.active)  # se arranca sin la hoja vacía que trae por defecto
    filas_resumen = [(lado, nombre, cantidad, suma / 100)
                     for lado, resumen in resumenes.items()
                     for nombre, (cantidad, suma) in resumen.items()]
    escribir_hoja(libro, "Resumen", ("Lado", "Qué", "Filas", "Suma"), filas_resumen,
                  {"D": "#,##0.00"}, (10, 16, 10, 20))
    for titulo, es_sistema, tabla in (("Banco", False, banco), ("Sistema", True, sistema)):
        escribir_hoja(libro, titulo, COLUMNAS_DE_LA_HOJA + (COLUMNA_PAREJA[es_sistema],),
                      filas_de_la_hoja(tabla, es_sistema),
                      {"A": "DD/MM/YYYY", "D": "#,##0.00"}, (12, 26, 44, 16, 15, 12, 15))
    libro.save(ruta)
