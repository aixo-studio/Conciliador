"""Prueba de los controles entre los dos lados y del Excel de salida (paso 4).
Se rompen los cruces a propósito. Todo con datos inventados.
"""
import openpyxl
import pandas
import pytest

from motor.controlar import controlar
from motor.cruce_exacto import cruzar_exacto
from motor.recibir import recibir_documento
from motor.salida import controlar_lados, escribir_excel
from pruebas.datos import tabla

# Una cuenta inventada: un cruce (la transferencia), un gasto bancario y dos sin pareja.
FILAS_BANCO = [(1, "319", "TRANSFERENCIA", 100, "Movimiento"),
               (1, "236", "IMPUESTO", -50, "Gasto bancario"),
               (2, "005", "", 700, "Movimiento")]
FILAS_SISTEMA = [(1, "Orden de pago", "PAGO", 100, "Movimiento"),
                 (3, "Recibo de Cobranzas", "", 900, "Movimiento")]


def cuenta_cruzada():
    """Devuelve las dos tablas de la cuenta inventada, ya cruzadas."""
    _, banco = recibir_documento(tabla(FILAS_BANCO), es_sistema=False)
    _, sistema = recibir_documento(tabla(FILAS_SISTEMA), es_sistema=True)
    cruzar_exacto(banco, sistema)
    return banco, sistema


def test_un_cruce_correcto_pasa():
    banco, sistema = cuenta_cruzada()
    controlar_lados(banco, sistema)
    assert banco.loc[0, "Estado"] == "Cruzado" and sistema.loc[0, "Estado"] == "Cruzado"


def test_frena_si_lo_cruzado_no_suma_igual():
    banco, sistema = cuenta_cruzada()
    banco.loc[0, "Monto en centavos"] = 101
    with pytest.raises(ValueError, match="no suma lo mismo"):
        controlar_lados(banco, sistema)


def test_frena_si_una_fila_cruzada_quedo_sin_pareja():
    banco, sistema = cuenta_cruzada()
    banco.loc[0, "Fila en Sistema"] = pandas.NA
    with pytest.raises(ValueError, match="Banco fila 2: el estado no coincide con su pareja"):
        controlar_lados(banco, sistema)


def test_frena_si_una_fila_sin_cruzar_apunta_a_otra():
    banco, sistema = cuenta_cruzada()
    banco.loc[2, "Fila en Sistema"] = 3
    with pytest.raises(ValueError, match="Banco fila 4: el estado no coincide con su pareja"):
        controlar_lados(banco, sistema)


def test_frena_si_la_pareja_no_apunta_de_vuelta():
    banco, sistema = cuenta_cruzada()
    sistema.loc[0, "Fila en Banco"] = 4
    with pytest.raises(ValueError, match="Banco fila 2: dice que cruzó con la fila 2"):
        controlar_lados(banco, sistema)


def test_frena_si_apunta_a_una_fila_que_no_existe():
    banco, sistema = cuenta_cruzada()
    banco.loc[0, "Fila en Sistema"] = 9
    with pytest.raises(ValueError, match="no existe en el otro lado"):
        controlar_lados(banco, sistema)


def test_escribe_el_excel_con_sus_tres_hojas(tmp_path):
    recibida_banco, banco = recibir_documento(tabla(FILAS_BANCO), es_sistema=False)
    recibida_sistema, sistema = recibir_documento(tabla(FILAS_SISTEMA), es_sistema=True)
    cruzar_exacto(banco, sistema)
    resumenes = {"Banco": controlar(banco, recibida_banco),
                 "Sistema": controlar(sistema, recibida_sistema)}
    ruta = tmp_path / "cruce.xlsx"
    escribir_excel(banco, sistema, resumenes, ruta)
    libro = openpyxl.load_workbook(ruta)
    assert libro.sheetnames == ["Resumen", "Banco", "Sistema"]
    hoja = libro["Banco"]
    assert [celda.value for celda in hoja[1]] == ["Fecha", "Código", "Descripción", "Monto",
                                                  "Clase", "Estado", "Fila en Sistema"]
    # La fila del cruce: el monto en pesos y la pareja en la fila 2 de la hoja Sistema.
    assert [celda.value for celda in hoja[2]][1:] == ["319", "TRANSFERENCIA", 1.0,
                                                      "Movimiento", "Cruzado", 2]
    # El gasto bancario sale con su Clase, su Estado y sin pareja.
    assert [celda.value for celda in hoja[3]][4:] == ["Gasto bancario", "Gasto bancario", None]
    # El resumen tiene el renglón de los gastos, con la suma en pesos.
    filas_resumen = [tuple(celda.value for celda in fila) for fila in libro["Resumen"].iter_rows(min_row=2)]
    assert ("Banco", "Gasto bancario", 1, -0.5) in filas_resumen
