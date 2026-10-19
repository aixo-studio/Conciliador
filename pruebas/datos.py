"""Ayudas para las pruebas: arman archivos de entrada inventados, como los deja la etapa 1."""
from datetime import datetime

import openpyxl

from motor.entrada import ENCABEZADO


def guardar_entrada(ruta, filas, hoja="Movimientos", encabezado=ENCABEZADO, hojas_de_mas=()):
    """Guarda un Excel con el encabezado y las filas dadas, y devuelve la ruta."""
    libro = openpyxl.Workbook()
    libro.active.title = hoja
    libro.active.append(list(encabezado))
    for fila in filas:
        libro.active.append(list(fila))
    for nombre in hojas_de_mas:
        libro.create_sheet(nombre)
    libro.save(ruta)
    return ruta


def dia(numero):
    """Devuelve la fecha de ese día de septiembre de 2026."""
    return datetime(2026, 9, numero)


def carpeta_banco(base, banco_filas, sistema_filas, nombre="BBVA"):
    """Arma <base>/<nombre>/ con un archivo del banco y uno del sistema. Devuelve la carpeta."""
    carpeta = base / nombre
    carpeta.mkdir(parents=True)
    guardar_entrada(carpeta / "banco_bbva - extracto.xlsx", banco_filas)
    guardar_entrada(carpeta / "sistema_finnegans - libro.xlsx", sistema_filas)
    return carpeta
