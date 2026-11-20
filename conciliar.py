"""La puerta de entrada de todo el sistema: concilia una cuenta de punta a punta.

Recibe el banco y los dos archivos de una cuenta: el extracto del banco y el
libro del ERP. Pasa cada archivo por la etapa 1 (preconciliacion/), que lo
devuelve limpio, y las dos tablas por la etapa 2 (conciliador/), que las cruza.
No guarda ni borra nada.

Desde la terminal, en la raíz del repo:
    python conciliar.py BBVA "extracto.xls" "libro.xlsx"
"""
import sys
from pathlib import Path

import pandas

from conciliador.cruzar_cuenta import cruzar_cuenta
from preconciliacion.convertir import convertir_documento, pesos


def conciliar(banco: str, ruta_extracto: Path | str, ruta_libro: Path | str) -> tuple:
    """Recibe el banco y dónde están el extracto y el libro del ERP de esa cuenta.
    Convierte los dos archivos y los cruza. Devuelve cuatro cosas: los cruces,
    el banco pendiente, el ERP pendiente y el resumen. Si algo falla, frena con
    un error que dice en qué parte: el extracto, el libro del ERP o el cruce.
    """
    # Cada etapa frena con su propio motivo; acá se le agrega en qué parte pasó.
    # Las rutas se pasan como Path, que es lo que espera la etapa 1.
    try:
        tabla_banco = convertir_documento(Path(ruta_extracto), banco, es_erp=False)
    except ValueError as error:
        raise ValueError(f"extracto: {error}") from None
    try:
        tabla_erp = convertir_documento(Path(ruta_libro), banco, es_erp=True)
    except ValueError as error:
        raise ValueError(f"libro del ERP: {error}") from None
    try:
        return cruzar_cuenta(tabla_banco, tabla_erp)
    except ValueError as error:
        raise ValueError(f"cruce: {error}") from None


def miles(numero: int) -> str:
    """Recibe un número entero. Lo devuelve como texto con punto de miles: 1.445"""
    return f"{numero:,}".replace(",", ".")


def mostrar_lado(nombre: str, resumen_del_lado: dict, fechas: pandas.Series) -> None:
    """Recibe el nombre de un lado (Banco o ERP), su resumen y las fechas de sus filas.
    Muestra en la terminal las filas y la suma de cada parte, y el rango de fechas.
    """
    print(f"  {nombre}   del {fechas.min():%d/%m/%Y} al {fechas.max():%d/%m/%Y}")
    for parte, (filas, suma) in resumen_del_lado.items():
        print(f"    {parte:<16}{miles(filas):>8} filas  {pesos(suma):>18}")


def main() -> None:
    """Recibe desde la terminal el banco, el extracto y el libro del ERP.
    Concilia la cuenta y muestra el resumen de cada lado. No guarda nada.
    Si falla, termina con un error que dice en qué parte.
    """
    argumentos = sys.argv[1:]
    if len(argumentos) != 3:
        sys.exit(__doc__)
    banco, ruta_extracto, ruta_libro = argumentos
    try:
        cruces, banco_pendiente, erp_pendiente, resumen = conciliar(banco, ruta_extracto, ruta_libro)
    except ValueError as error:
        sys.exit(f"✗ {banco}: no se pudo conciliar. {error}")
    # Las filas del ERP que cruzaron tienen la misma fecha que su pareja del
    # banco, así que sus fechas son las de los cruces más las de lo pendiente.
    fechas_banco = pandas.concat([cruces["Fecha"], banco_pendiente["Fecha"]])
    fechas_erp = pandas.concat([cruces["Fecha"], erp_pendiente["Fecha"]])
    print(f"✓ {banco}: {miles(len(cruces))} cruces")
    mostrar_lado("Banco", resumen["Banco"], fechas_banco)
    mostrar_lado("ERP", resumen["ERP"], fechas_erp)


if __name__ == "__main__":
    main()
