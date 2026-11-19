"""Puerta de entrada: limpia un documento y lo devuelve como DataFrame.

Lo llama Conciliador, una vez por archivo, con convertir_documento(): le dice
qué banco es y si es el libro del ERP, y recibe el DataFrame
(Fecha · Código · Descripción · Monto en centavos · Clase). No guarda ni borra nada.

Desde la terminal sirve para probar un archivo y ver el resumen:
    python convertir.py BBVA "extracto.xls"           el extracto del BBVA
    python convertir.py BBVA "libro.xlsx" --erp       el libro del ERP de la cuenta BBVA

Las reglas de cada banco y del ERP están en configuracion.toml.
"""
import sys
from pathlib import Path

import pandas

from motor.armar import armar_movimientos
from motor.configuracion import buscar_reglas, columnas_que_se_usan
from motor.controlar import controlar
from motor.devolver import CLASE_GASTO_BANCARIO, armar_dataframe
from motor.leer import encontrar_tabla, leer_filas


def pesos(centavos: int) -> str:
    """Recibe un importe en centavos. Lo devuelve como texto en formato argentino: 1.234.567,89"""
    return f"{centavos / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def limpiar_archivo(ruta_archivo: Path, reglas: dict, que_se_espera: str) -> tuple[list, dict]:
    """Recibe un archivo, las reglas para limpiarlo y qué documento se espera (para el error).
    Lo abre, verifica sus encabezados, arma las columnas y controla filas y suma.
    Devuelve los movimientos y el resumen. Si algo no cierra, frena con un error.
    """
    # Un archivo que falta, está dañado o no es Excel de verdad no se puede abrir.
    try:
        filas = leer_filas(ruta_archivo)
    except Exception:
        raise ValueError("no se pudo abrir como Excel.") from None
    # Solo se buscan las columnas que se usan: si cambia otra, no importa.
    try:
        columnas, datos = encontrar_tabla(filas, columnas_que_se_usan(reglas), reglas.get("seguidas"))
    except ValueError as error:
        raise ValueError(f"no es {que_se_espera}. {error}") from None
    movimientos = armar_movimientos(columnas, datos, reglas)
    return movimientos, controlar(movimientos, columnas, datos, reglas)


def convertir_con_resumen(ruta_archivo: Path, banco: str, es_erp: bool) -> tuple[pandas.DataFrame, dict]:
    """Recibe un archivo, su banco y si es el libro del ERP.
    Lo limpia con las reglas que le tocan. Devuelve el DataFrame y el resumen
    (filas, ignoradas, créditos, débitos y suma). Si algo falla, frena con un error.
    """
    reglas = buscar_reglas(banco, es_erp)
    que_se_espera = "el libro del ERP" if es_erp else f"un extracto de {banco}"
    movimientos, resumen = limpiar_archivo(ruta_archivo, reglas, que_se_espera)
    return armar_dataframe(movimientos, reglas), resumen


def convertir_documento(ruta_archivo: Path, banco: str, es_erp: bool) -> pandas.DataFrame:
    """Recibe un archivo, su banco y si es el libro del ERP.
    Devuelve el DataFrame con sus movimientos. Es lo que llama Conciliador.
    Si algo falla, frena con un error que dice por qué.
    """
    tabla, _ = convertir_con_resumen(ruta_archivo, banco, es_erp)
    return tabla


def main() -> None:
    """Recibe desde la terminal el banco, el archivo y, si es el libro del ERP, --erp.
    Convierte el archivo y muestra el resumen. No guarda nada. Si falla, termina con error.
    """
    argumentos = sys.argv[1:]
    es_erp = "--erp" in argumentos
    argumentos = [argumento for argumento in argumentos if argumento != "--erp"]
    if len(argumentos) != 2:
        sys.exit(__doc__)
    banco, archivo = argumentos
    ruta_archivo = Path(archivo)
    try:
        tabla, resumen = convertir_con_resumen(ruta_archivo, banco, es_erp)
    except ValueError as error:
        sys.exit(f"✗ {ruta_archivo.name}: no se pudo convertir. {error}")
    gastos = tabla[tabla["Clase"] == CLASE_GASTO_BANCARIO]
    print(f"✓ {ruta_archivo.name}")
    print(f"  filas:       {resumen['filas']} (ignoradas: {resumen['ignoradas']})")
    print(f"  columnas:    {' · '.join(tabla.columns)}")
    print(f"  suma:        {pesos(resumen['suma'])}")
    print(f"  gastos:      {len(gastos)} filas, {pesos(int(gastos['Monto en centavos'].sum()))}")
    if not tabla.empty:
        print(f"  fechas:      del {tabla['Fecha'].min():%d/%m/%Y} al {tabla['Fecha'].max():%d/%m/%Y}")


if __name__ == "__main__":
    main()
