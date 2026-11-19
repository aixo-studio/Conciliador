"""Prueba del DataFrame que se devuelve: cada fila sale una sola vez, en el orden
del original, con su Clase ("Gasto bancario" o "Movimiento"); el libro del ERP
sale todo como "Movimiento". Todo con datos inventados.
"""
from datetime import date, datetime

from motor.armar import Movimiento
from motor.devolver import COLUMNAS, armar_dataframe


def movimiento(codigo, centavos):
    """Un movimiento inventado del 30/09/2026 con ese Código y monto."""
    return Movimiento(date(2026, 9, 30), codigo, "", centavos)


def test_cada_fila_sale_una_vez_con_su_clase_en_el_orden_del_original():
    reglas = {"gastos": ["236", "015"]}
    filas = [movimiento("319", 25000000), movimiento("236", -125000), movimiento("005", -15000000),
             movimiento("015", -95000), movimiento("319", 8000000)]
    tabla = armar_dataframe(filas, reglas)
    assert list(tabla["Código"]) == ["319", "236", "005", "015", "319"]
    assert list(tabla["Clase"]) == ["Movimiento", "Gasto bancario", "Movimiento", "Gasto bancario", "Movimiento"]
    # Ninguna fila se pierde: la suma es la del original, con los gastos incluidos.
    assert tabla["Monto en centavos"].sum() == 25000000 - 125000 - 15000000 - 95000 + 8000000


def test_sin_gastos_todo_es_movimiento():
    tabla = armar_dataframe([movimiento("319", 100), movimiento("005", -100)], {"gastos": ["236"]})
    assert list(tabla["Clase"]) == ["Movimiento", "Movimiento"]


def test_el_libro_del_erp_sale_todo_como_movimiento():
    # Las reglas del ERP no tienen lista de gastos.
    tabla = armar_dataframe([movimiento("Orden de pago", -100), movimiento("Recibo de Cobranzas", 100)], {})
    assert list(tabla["Clase"]) == ["Movimiento", "Movimiento"]


def test_columnas_y_tipos_fijos():
    tabla = armar_dataframe([movimiento("015", -950)], {"gastos": ["015"]})
    assert list(tabla.columns) == COLUMNAS
    assert tabla.iloc[0].to_dict() == {"Fecha": datetime(2026, 9, 30), "Código": "015", "Descripción": "",
                                       "Monto en centavos": -950, "Clase": "Gasto bancario"}
    # El Código sigue siendo el texto "015", no el número 15.
    assert isinstance(tabla.iloc[0]["Código"], str)


def test_sin_filas_devuelve_las_columnas_vacias():
    tabla = armar_dataframe([], {"gastos": ["015"]})
    assert list(tabla.columns) == COLUMNAS and tabla.empty
    assert str(tabla["Monto en centavos"].dtype) == "int64"
