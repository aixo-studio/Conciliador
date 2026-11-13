"""Prueba de la corrida completa de una cuenta: de las dos tablas al Excel.
Si algo no cumple, no se escribe nada. Todo con datos inventados.
"""
import openpyxl
import pytest

from cruzar_cuenta import cruzar_cuenta
from pruebas.datos import tabla

FILAS_BANCO = [(1, "319", "TRANSFERENCIA", 100, "Movimiento"),
               (1, "236", "IMPUESTO", -50, "Gasto bancario"),
               (2, "005", "", 700, "Movimiento")]
FILAS_SISTEMA = [(1, "Orden de pago", "PAGO", 100, "Movimiento"),
                 (3, "Recibo de Cobranzas", "", 900, "Movimiento")]


def test_la_corrida_completa_escribe_el_excel_y_devuelve_el_resumen(tmp_path):
    ruta = tmp_path / "cruce - BBVA 2026-09.xlsx"
    resultado = cruzar_cuenta(tabla(FILAS_BANCO), tabla(FILAS_SISTEMA), ruta)
    assert resultado["cruces"] == 1
    assert resultado["Banco"]["Entrada"] == (3, 750)
    assert resultado["Banco"]["Gasto bancario"] == (1, -50)
    assert resultado["Sistema"]["Sin cruzar"] == (1, 900)
    assert openpyxl.load_workbook(ruta).sheetnames == ["Resumen", "Banco", "Sistema"]


def test_si_la_entrada_no_cumple_no_se_escribe_nada(tmp_path):
    ruta = tmp_path / "cruce.xlsx"
    rota = tabla(FILAS_BANCO).astype({"Clase": object})
    rota.loc[0, "Clase"] = "Otra"
    with pytest.raises(ValueError, match="la Clase tiene que ser"):
        cruzar_cuenta(rota, tabla(FILAS_SISTEMA), ruta)
    assert not ruta.exists()


def test_si_el_sistema_trae_un_gasto_no_se_escribe_nada(tmp_path):
    ruta = tmp_path / "cruce.xlsx"
    sistema = tabla([(1, "Orden de pago", "", 100, "Gasto bancario")])
    with pytest.raises(ValueError, match="es un gasto bancario"):
        cruzar_cuenta(tabla(FILAS_BANCO), sistema, ruta)
    assert not ruta.exists()
