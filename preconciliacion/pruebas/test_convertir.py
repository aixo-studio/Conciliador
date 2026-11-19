"""Prueba de la entrada: convertir un archivo con su banco, verificar que sea el
documento indicado y devolver el DataFrame. Todo con archivos inventados.
"""
from datetime import datetime

import openpyxl
import pytest

from convertir import convertir_documento
from motor.devolver import COLUMNAS

ENCABEZADO_BBVA = ["Fecha", "Fecha Valor", "Concepto", "Codigo", "Número Documento",
                   "Oficina", "Crédito", "Débito", "Detalle"]
ENCABEZADO_GALICIA = ["Fecha", "Descripción", "Origen", "Débitos", "Créditos", "Grupo de Conceptos",
                      "Concepto", "Número de Terminal", "Observaciones Cliente", "Número de Comprobante",
                      "Leyendas Adicionales 1", "Leyendas Adicionales 2", "Leyendas Adicionales 3",
                      "Leyendas Adicionales 4", "Tipo de Movimiento", "Saldo"]
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


def extracto_bbva(ruta, fecha="30-09-2026"):
    """Un extracto del BBVA inventado, con una fila."""
    return guardar(ruta, [["Empresa:", "EMPRESA DE PRUEBA"], [], ENCABEZADO_BBVA,
                          [fecha, fecha, "TRANSFERENCI", "319", "", "OF", "", -1500, ""]])


def libro_erp(ruta):
    """Un libro del ERP inventado: saldo inicial y un movimiento."""
    fila = ["2026-09", "1", "BANCO", datetime(2026, 9, 1), "F", "", 0, 0, "Saldo Inicial",
            None, "", 1, None, None, "EMPRESA", "", 0, 0, ""]
    movimiento = fila[:6] + [0, 1500, "PAGO - 1"] + fila[9:16] + [0, 1, "Orden de pago"]
    return guardar(ruta, [ENCABEZADO_ERP, fila, movimiento])


def test_devuelve_el_dataframe_del_extracto_y_del_libro(tmp_path):
    tabla = convertir_documento(extracto_bbva(tmp_path / "extracto.xlsx"), "BBVA", False)
    assert list(tabla.columns) == COLUMNAS
    assert tabla.iloc[0].to_dict() == {"Fecha": datetime(2026, 9, 30), "Código": "319", "Descripción": "",
                                       "Monto en centavos": -150000, "Clase": "Movimiento"}
    # El libro del ERP: el Saldo Inicial no sale y todo es "Movimiento".
    tabla = convertir_documento(libro_erp(tmp_path / "libro.xlsx"), "BBVA", True)
    assert list(tabla["Código"]) == ["Orden de pago"]
    assert list(tabla["Monto en centavos"]) == [-150000]
    assert list(tabla["Clase"]) == ["Movimiento"]


def test_marca_los_gastos_bancarios_sin_sacarlos(tmp_path):
    # Dos filas: una transferencia (319) y un gasto bancario (236).
    ruta = guardar(tmp_path / "extracto.xlsx", [ENCABEZADO_BBVA,
        ["30-09-2026", "30-09-2026", "TRANSFERENCI", "319", "", "OF", "", -1500, ""],
        ["30-09-2026", "30-09-2026", "IMPUESTO LEY", "236", "", "OF", "", -9, ""]])
    tabla = convertir_documento(ruta, "BBVA", False)
    assert list(tabla["Clase"]) == ["Movimiento", "Gasto bancario"]
    assert tabla["Monto en centavos"].sum() == -150900  # el total cierra entero, con los gastos


def test_los_tipos_de_las_columnas_son_fijos(tmp_path):
    tabla = convertir_documento(extracto_bbva(tmp_path / "extracto.xlsx"), "BBVA", False)
    assert str(tabla["Fecha"].dtype) == "datetime64[ns]"
    assert str(tabla["Monto en centavos"].dtype) == "int64"


def test_no_guarda_ningun_archivo(tmp_path):
    ruta = extracto_bbva(tmp_path / "extracto.xlsx")
    convertir_documento(ruta, "BBVA", False)
    assert list(tmp_path.iterdir()) == [ruta]


def test_frena_si_el_banco_no_esta_configurado(tmp_path):
    with pytest.raises(ValueError, match='"Macro" no está en la configuración'):
        convertir_documento(extracto_bbva(tmp_path / "a.xlsx"), "Macro", False)


def test_frena_si_el_extracto_es_de_otro_banco(tmp_path):
    ruta = guardar(tmp_path / "galicia.xlsx", [ENCABEZADO_GALICIA])
    with pytest.raises(ValueError, match="no es un extracto de BBVA"):
        convertir_documento(ruta, "BBVA", False)


def test_frena_si_se_confunde_extracto_y_libro(tmp_path):
    with pytest.raises(ValueError, match="no es el libro del ERP"):
        convertir_documento(extracto_bbva(tmp_path / "a.xlsx"), "BBVA", True)
    with pytest.raises(ValueError, match="no es un extracto de BBVA"):
        convertir_documento(libro_erp(tmp_path / "b.xlsx"), "BBVA", False)


def test_frena_si_el_archivo_no_se_puede_abrir(tmp_path):
    ruta = tmp_path / "roto.xlsx"
    ruta.write_text("no es un Excel")
    with pytest.raises(ValueError, match="no se pudo abrir como Excel"):
        convertir_documento(ruta, "BBVA", False)


def test_las_fechas_de_otro_mes_salen_tal_cual(tmp_path):
    # Decidir qué hacer con ellas es de Conciliador, que sabe qué mes concilia.
    tabla = convertir_documento(extracto_bbva(tmp_path / "a.xlsx", fecha="31-08-2026"), "BBVA", False)
    assert list(tabla["Fecha"]) == [datetime(2026, 8, 31)]


def test_dice_que_columna_falta(tmp_path):
    # El encabezado está en la fila 3 y le falta "Codigo".
    sin_codigo = [columna for columna in ENCABEZADO_BBVA if columna != "Codigo"]
    ruta = guardar(tmp_path / "a.xlsx", [["Empresa:", "EMPRESA DE PRUEBA"], [], sin_codigo])
    with pytest.raises(ValueError, match="no es un extracto de BBVA. En la fila 3 faltan estas columnas: Codigo."):
        convertir_documento(ruta, "BBVA", False)


def test_si_cambia_una_columna_que_no_se_usa_convierte_igual(tmp_path):
    # "Oficina" pasa a llamarse "Sucursal" y "Fecha Valor" desaparece: el programa no las usa.
    encabezado = ["Fecha", "Concepto", "Codigo", "Número Documento", "Sucursal", "Crédito", "Débito", "Detalle"]
    ruta = guardar(tmp_path / "a.xlsx", [encabezado, ["30-09-2026", "X", "319", "", "OF", "", -1500, ""]])
    assert list(convertir_documento(ruta, "BBVA", False)["Código"]) == ["319"]


def test_lista_todas_las_filas_con_errores(tmp_path):
    ruta = guardar(tmp_path / "a.xlsx", [ENCABEZADO_BBVA,
        ["2026/09/30", "", "X", "319", "", "OF", "", -1500, ""],   # fila 2: fecha mal escrita
        ["30-09-2026", "", "X", "319", "", "OF", "", -1500, ""],   # fila 3: bien
        ["30-09-2026", "", "X", "319", "", "OF", 100, -100, ""],   # fila 4: crédito y débito
        ["30-09-2026", "", "X", 5, "", "OF", "", -1500, ""]])      # fila 5: Código como número
    with pytest.raises(ValueError) as error:
        convertir_documento(ruta, "BBVA", False)
    mensaje = str(error.value)
    assert mensaje.startswith("hay 3 filas con errores:")
    assert "Fila 2: fecha" in mensaje and "Fila 4: tiene que tener crédito o débito" in mensaje
    assert "Fila 5: el Código viene como número" in mensaje and "Fila 3" not in mensaje


def test_con_muchos_errores_muestra_los_primeros_y_cuenta_el_resto(tmp_path):
    filas_malas = [["sin fecha", "", "X", "319", "", "OF", "", -1500, ""]] * 25
    ruta = guardar(tmp_path / "a.xlsx", [ENCABEZADO_BBVA] + filas_malas)
    with pytest.raises(ValueError) as error:
        convertir_documento(ruta, "BBVA", False)
    mensaje = str(error.value)
    assert mensaje.startswith("hay 25 filas con errores:")
    assert mensaje.count("fecha que no se puede leer") == 20 and mensaje.endswith("… y 5 más.")
