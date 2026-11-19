"""Prueba del libro del sistema con un archivo inventado que imita la forma del real."""
from datetime import date, datetime

import openpyxl
import pytest

from motor.armar import armar_movimientos
from motor.configuracion import buscar_reglas, columnas_que_se_usan
from motor.controlar import controlar
from motor.leer import encontrar_tabla, leer_filas

# Las reglas del ERP son las mismas para cualquier banco.
reglas = buscar_reglas("BBVA", es_erp=True)

ENCABEZADO = ["Año - mes", "Codigo cuenta", "Cuenta", "Fecha", "Comprobante", "Descripción",
              "Debe", "Haber", "Documento", "Dimensión valor", "Detalle", "Cotizacion",
              "Productoid", "Producto", "Empresa", "Organizacion transaccion",
              "Debe", "Haber", "Tipo de documento"]


def fila(fecha, descripcion, debe, haber, documento, tipo, debe_dolares=0, haber_dolares=0):
    """Arma una fila del libro con las 19 columnas, completando las que no importan."""
    return ["2026-09", "1110000", "BANCO DE PRUEBA", fecha, "F-0001", descripcion, debe, haber,
            documento, None, "", 1, None, None, "EMPRESA DE PRUEBA", "",
            debe_dolares, haber_dolares, tipo]


def crear_libro(carpeta, filas_de_datos, encabezado=ENCABEZADO):
    """Arma un libro inventado: el encabezado y debajo las filas que se le pasan."""
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.append(encabezado)
    for datos in filas_de_datos:
        hoja.append(datos)
    ruta = carpeta / "libro.xlsx"
    libro.save(ruta)
    return ruta


def convertir(ruta):
    """Corre los pasos del motor sobre el archivo de prueba y devuelve movimientos y resumen."""
    columnas, datos = encontrar_tabla(leer_filas(ruta), columnas_que_se_usan(reglas), reglas["seguidas"])
    movimientos = armar_movimientos(columnas, datos, reglas)
    return movimientos, controlar(movimientos, columnas, datos, reglas)


def test_convierte_a_cuatro_columnas(tmp_path):
    ruta = crear_libro(tmp_path, [
        fila(datetime(2026, 8, 31), "", 0, 0, "Saldo Inicial", ""),
        fila(datetime(2026, 9, 1), "Mvto. e/ ctas. propias", 500000, 0, "MOVFONDOS - 1",
             "Movimiento de Fondos", debe_dolares=330.5),
        fila(datetime(2026, 9, 2), "", 0, 125000.75, "PAGO - 2", "Orden de pago", haber_dolares=82.7),
    ])
    movimientos, resumen = convertir(ruta)

    assert [m.fecha for m in movimientos] == [date(2026, 9, 1), date(2026, 9, 2)]
    assert [m.codigo for m in movimientos] == ["Movimiento de Fondos", "Orden de pago"]
    assert [m.descripcion for m in movimientos] == ["Mvto. e/ ctas. propias", ""]
    # Usa el primer par de Debe y Haber (pesos), no el segundo (dólares).
    assert [m.monto_centavos for m in movimientos] == [50000000, -12500075]
    assert resumen["filas"] == 2
    assert resumen["ignoradas"] == 1
    assert resumen["suma"] == 50000000 - 12500075


def test_frena_si_el_saldo_inicial_tiene_monto(tmp_path):
    ruta = crear_libro(tmp_path, [
        fila(datetime(2026, 8, 31), "", 1000, 0, "Saldo Inicial", ""),
    ])
    with pytest.raises(ValueError, match="Fila 2: es una fila a ignorar pero tiene monto"):
        convertir(ruta)


def dolares_primero(lista):
    """Mueve el par en dólares (columnas 17 y 18) al principio de la fila."""
    return lista[16:18] + lista[:16] + lista[18:]


def test_usa_pesos_aunque_los_dolares_vengan_primero(tmp_path):
    ruta = crear_libro(tmp_path, [
        dolares_primero(fila(datetime(2026, 9, 1), "", 500000, 0, "MOVFONDOS - 1",
                             "Movimiento de Fondos", debe_dolares=330.5)),
    ], encabezado=dolares_primero(ENCABEZADO))
    movimientos, _ = convertir(ruta)
    assert [m.monto_centavos for m in movimientos] == [50000000]


def test_frena_si_las_columnas_de_pesos_no_estan_juntas(tmp_path):
    encabezado = ENCABEZADO[:6] + ["Columna nueva"] + ENCABEZADO[6:]
    datos = fila(datetime(2026, 9, 1), "", 500000, 0, "MOVFONDOS - 1", "Movimiento de Fondos")
    ruta = crear_libro(tmp_path, [datos[:6] + [None] + datos[6:]], encabezado=encabezado)
    with pytest.raises(ValueError, match="no están juntas y en ese orden"):
        convertir(ruta)
