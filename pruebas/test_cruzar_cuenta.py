"""Prueba de la corrida completa de una cuenta: de las dos tablas que entran a
las tres que salen. Si algo no cumple, no se devuelve nada.
Todo con datos inventados.
"""
import pytest

from cruzar_cuenta import cruzar_cuenta
from motor.cruce_exacto import COLUMNA_PAREJA
from pruebas.datos import tabla

FILAS_BANCO = [(1, "319", "TRANSFERENCIA", 100, "Movimiento"),
               (1, "236", "IMPUESTO", -50, "Gasto bancario"),
               (2, "005", "", 700, "Movimiento")]
FILAS_ERP = [(1, "Orden de pago", "PAGO", 100, "Movimiento"),
             (3, "Recibo de Cobranzas", "", 900, "Movimiento")]


def test_la_corrida_completa_devuelve_las_tres_tablas_y_el_resumen():
    cruces, banco, erp, resumen = cruzar_cuenta(tabla(FILAS_BANCO), tabla(FILAS_ERP))
    assert list(cruces[COLUMNA_PAREJA]) == [0]
    assert len(banco) == 2 and len(erp) == 1
    assert resumen["Banco"]["Entrada"] == (3, 750)
    assert resumen["Banco"]["Gasto bancario"] == (1, -50)
    assert resumen["ERP"]["Pendiente"] == (1, 900)


def test_si_la_entrada_no_cumple_el_contrato_frena():
    rota = tabla(FILAS_BANCO).astype({"Clase": object})
    rota.loc[0, "Clase"] = "Otra"
    with pytest.raises(ValueError, match="la Clase tiene que ser"):
        cruzar_cuenta(rota, tabla(FILAS_ERP))


def test_si_el_erp_trae_un_gasto_bancario_frena():
    with pytest.raises(ValueError, match="es un gasto bancario"):
        cruzar_cuenta(tabla(FILAS_BANCO), tabla([(1, "Orden de pago", "", 100, "Gasto bancario")]))
