"""Después del cruce, y solo si se pide: guardar el resultado en archivos CSV para revisarlo.

Recibe lo que devuelve cruzar_cuenta(), ya controlado (las tres tablas y el
resumen), y escribe cuatro CSV en la carpeta indicada: cruces, banco
pendiente, ERP pendiente y resumen. Si la carpeta ya tenía CSV con esos
nombres, los reemplaza.

No sabe cuántas pasadas tuvo el cruce: escribe todas las columnas que traiga
cada tabla, así una pasada nueva no obliga a cambiar este archivo.
"""
from pathlib import Path

import pandas

# Excel en castellano separa las columnas con punto y coma.
SEPARADOR = ";"
# utf-8 con una marca al principio: así Excel muestra bien los acentos.
CODIFICACION = "utf-8-sig"
FORMATO_FECHA = "%d/%m/%Y"
# La primera columna de cada tabla: su número de fila, el mismo que nombra "Fila en ERP".
COLUMNA_FILA = "Fila"


def escribir_csv(cruces: pandas.DataFrame, banco_pendiente: pandas.DataFrame,
                 erp_pendiente: pandas.DataFrame, resumen: dict, carpeta: Path | str) -> list[Path]:
    """Recibe las tres tablas y el resumen que devuelve cruzar_cuenta(), y una carpeta.
    Escribe en ella cruces.csv, banco_pendiente.csv, erp_pendiente.csv y
    resumen.csv, reemplazando los que hubiera. Devuelve las rutas escritas.
    """
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    tablas = {"cruces.csv": cruces, "banco_pendiente.csv": banco_pendiente,
              "erp_pendiente.csv": erp_pendiente}
    rutas = []
    for nombre, tabla in tablas.items():
        ruta = carpeta / nombre
        tabla.to_csv(ruta, sep=SEPARADOR, encoding=CODIFICACION, date_format=FORMATO_FECHA,
                     index=True, index_label=COLUMNA_FILA)
        rutas.append(ruta)
    ruta = carpeta / "resumen.csv"
    armar_tabla_resumen(resumen).to_csv(ruta, sep=SEPARADOR, encoding=CODIFICACION, index=False)
    rutas.append(ruta)
    return rutas


def armar_tabla_resumen(resumen: dict) -> pandas.DataFrame:
    """Recibe el resumen del cruce: por cada lado, las filas y la suma de cada parte.
    Devuelve una tabla con una fila por lado y parte: Lado, Parte, Filas y Suma en centavos.
    """
    filas = [(lado, parte, cantidad, suma)
             for lado, partes in resumen.items()
             for parte, (cantidad, suma) in partes.items()]
    return pandas.DataFrame(filas, columns=["Lado", "Parte", "Filas", "Suma en centavos"])
