"""Prueba del recorrido completo (conciliar.py): una cuenta inventada, del Excel
crudo hasta las tablas del cruce, y que cada error diga en qué parte pasó.
"""
from datetime import datetime

import openpyxl
import pytest

from conciliar import conciliar

ENCABEZADO_SUPERVIELLE = ["Fecha", "Hora", "Concepto", "Detalle", "Débito", "Crédito", "Saldo"]
ENCABEZADO_ERP = ["Año - mes", "Codigo cuenta", "Cuenta", "Fecha", "Comprobante", "Descripción",
                  "Debe", "Haber", "Documento", "Dimensión valor", "Detalle", "Cotizacion",
                  "Productoid", "Producto", "Empresa", "Organizacion transaccion",
                  "Debe", "Haber", "Tipo de documento"]


def guardar(ruta, filas):
    """Guarda las filas en un Excel nuevo y devuelve la ruta."""
    libro = openpyxl.Workbook()
    for fila in filas:
        libro.active.append(fila)
    libro.save(ruta)
    return ruta


def fila_erp(fecha, debe, haber, documento, tipo):
    """Arma una fila del libro del ERP con sus 19 columnas; las que no se usan van con relleno."""
    return ["2026-09", "1110000", "BANCO DE PRUEBA", fecha, "F-0001", "", debe, haber,
            documento, None, "", 1, None, None, "EMPRESA DE PRUEBA", "", 0, 0, tipo]


def crear_cuenta(carpeta):
    """Arma una cuenta inventada del Supervielle: un extracto con 3 movimientos
    (uno es gasto bancario) y un libro del ERP con su saldo inicial y 2 movimientos.
    Solo el crédito del 30/09 cruza. Devuelve las rutas del extracto y del libro.
    """
    extracto = guardar(carpeta / "extracto.xlsx", [
        ENCABEZADO_SUPERVIELLE,
        ["30/09/2026", "07:28", "CRED BCA ELECTR INTERBANC EXEN", "CUENTAS PROPIAS", 0, 5000, 0],
        ["29/09/2026", "02:28", "Impuesto Débitos y Créditos/DB", None, 9, 0, 0],
        ["29/09/2026", "02:28", "Pago Cheque de Cámara Recibida", "Número Cheque: 101", 1500, 0, 0],
    ])
    libro = guardar(carpeta / "libro.xlsx", [
        ENCABEZADO_ERP,
        fila_erp(datetime(2026, 8, 31), 0, 0, "Saldo Inicial", ""),
        fila_erp(datetime(2026, 9, 30), 5000, 0, "MOVFONDOS - 00001", "Movimiento de Fondos"),
        fila_erp(datetime(2026, 9, 28), 0, 1500, "PAGO - 00002", "Orden de pago"),
    ])
    return extracto, libro


def test_concilia_una_cuenta_de_punta_a_punta(tmp_path):
    extracto, libro = crear_cuenta(tmp_path)

    cruces, banco_pendiente, erp_pendiente, resumen = conciliar("Supervielle", extracto, libro)

    # Cruza el crédito del 30/09 con el movimiento de fondos (fila 0 del ERP).
    assert list(cruces["Código"]) == ["CRED BCA ELECTR INTERBANC EXEN"]
    assert list(cruces["Fila en ERP"]) == [0]
    # El cheque no cruza (el ERP lo tiene el 28/09) y el impuesto es gasto: no busca pareja.
    assert list(banco_pendiente["Clase"]) == ["Gasto bancario", "Movimiento"]
    assert list(erp_pendiente["Código"]) == ["Orden de pago"]
    # El resumen cierra contra lo que entró: 5.000 − 9 − 1.500 = 3.491 pesos.
    assert resumen["Banco"]["Entrada"] == (3, 349100)
    assert resumen["Banco"]["Gasto bancario"] == (1, -900)
    assert resumen["ERP"]["Entrada"] == (2, 350000)


def test_acepta_las_rutas_como_texto(tmp_path):
    extracto, libro = crear_cuenta(tmp_path)

    cruces, _, _, _ = conciliar("Supervielle", str(extracto), str(libro))

    assert len(cruces) == 1


def test_si_falla_el_extracto_lo_dice(tmp_path):
    _, libro = crear_cuenta(tmp_path)
    sin_fecha = guardar(tmp_path / "roto.xlsx", [["Hora", "Concepto", "Detalle", "Débito", "Crédito"]])

    with pytest.raises(ValueError, match="^extracto: "):
        conciliar("Supervielle", sin_fecha, libro)


def test_si_falla_el_libro_lo_dice(tmp_path):
    extracto, _ = crear_cuenta(tmp_path)
    sin_debe = guardar(tmp_path / "roto.xlsx", [["Fecha", "Descripción", "Documento"]])

    with pytest.raises(ValueError, match="^libro del ERP: "):
        conciliar("Supervielle", extracto, sin_debe)


def test_si_el_banco_no_esta_configurado_lo_dice(tmp_path):
    extracto, libro = crear_cuenta(tmp_path)

    with pytest.raises(ValueError, match="^extracto: .*no está en la configuración"):
        conciliar("Banco Inventado", extracto, libro)
