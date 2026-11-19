"""Prueba del extracto del Galicia con un archivo inventado que imita la forma del real."""
from datetime import date, datetime

import openpyxl

from motor.armar import Movimiento, armar_movimientos
from motor.configuracion import buscar_reglas, columnas_que_se_usan
from motor.controlar import controlar
from motor.devolver import armar_dataframe
from motor.leer import encontrar_tabla, leer_filas

reglas = buscar_reglas("Galicia", es_erp=False)

# Los encabezados del extracto real; el programa usa solo algunos.
ENCABEZADO = ["Fecha", "Descripción", "Origen", "Débitos", "Créditos", "Grupo de Conceptos",
              "Concepto", "Número de Terminal", "Observaciones Cliente", "Número de Comprobante",
              "Leyendas Adicionales 1", "Leyendas Adicionales 2", "Leyendas Adicionales 3",
              "Leyendas Adicionales 4", "Tipo de Movimiento", "Saldo"]


def fila(fecha, descripcion, debito, credito, grupo, concepto="000000 - CONCEPTO"):
    """Arma una fila del extracto con las 16 columnas, completando las que no importan."""
    return [fecha, descripcion, None, debito, credito, grupo, concepto, None, None,
            None, "LEYENDA", None, None, None, "Imputado", 1000]


def test_convierte_a_cuatro_columnas(tmp_path):
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.append(ENCABEZADO)
    hoja.append(fila(datetime(2026, 9, 1), "Transf Inmed Cp", 150000, 0, "000907 - Transferencias", "907268 - TRANSF INMED CP"))
    hoja.append(fila(datetime(2026, 9, 2), "Com. Deposito De Cheque      475", 1234.56, 0, "000808 - Comisiones", "907188 - COM. DEPOSITO"))
    hoja.append(fila(datetime(2026, 9, 3), "Credito Prestamo", 0, 800000, "000083 - Pagos", "917133 - CREDITO PRESTAMO"))
    ruta = tmp_path / "extracto.xlsx"
    libro.save(ruta)

    columnas, datos = encontrar_tabla(leer_filas(ruta), columnas_que_se_usan(reglas))
    movimientos = armar_movimientos(columnas, datos, reglas)
    resumen = controlar(movimientos, columnas, datos, reglas)

    assert [m.fecha for m in movimientos] == [date(2026, 9, 1), date(2026, 9, 2), date(2026, 9, 3)]
    # El Código sale de "Grupo de Conceptos", no de "Concepto".
    assert [m.codigo for m in movimientos] == ["000907 - Transferencias", "000808 - Comisiones", "000083 - Pagos"]
    assert movimientos[1].descripcion == "Com. Deposito De Cheque      475"  # tal cual, con los espacios
    assert [m.monto_centavos for m in movimientos] == [-15000000, -123456, 80000000]
    assert resumen["filas"] == 3 and resumen["ignoradas"] == 0


def test_reconoce_los_tres_grupos_de_gasto():
    movimientos = [Movimiento(date(2026, 9, 1), codigo, "", -100) for codigo in
                   ("000901 - Impuestos", "000808 - Comisiones", "000814 - Intereses", "000907 - Transferencias")]
    tabla = armar_dataframe(movimientos, reglas)
    assert list(tabla["Clase"]) == ["Gasto bancario"] * 3 + ["Movimiento"]
