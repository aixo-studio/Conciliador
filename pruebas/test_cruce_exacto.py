"""Prueba del cruce exacto (paso 2), con movimientos inventados."""
from datetime import date

from motor.cruce_exacto import cruzar_exacto
from motor.entrada import Movimiento


def movimiento(fila, dia, centavos):
    """Un movimiento inventado de septiembre de 2026."""
    return Movimiento(fila=fila, fecha=date(2026, 9, dia), codigo="", descripcion="", monto_centavos=centavos)


def test_cruza_solo_misma_fecha_y_mismo_monto():
    banco = [movimiento(2, 1, -150000), movimiento(3, 2, 5000), movimiento(4, 3, 7000)]
    sistema = [movimiento(2, 1, -150000), movimiento(3, 3, 5000), movimiento(4, 3, 7001)]
    assert cruzar_exacto(banco, sistema) == 1
    assert [(m.estado, m.filas_cruzadas, m.criterio) for m in banco] == [
        ("Cruzado", [2], "Exacto"), ("Sin cruzar", [], ""), ("Sin cruzar", [], "")]
    assert [m.estado for m in sistema] == ["Cruzado", "Sin cruzar", "Sin cruzar"]


def test_cada_fila_anota_la_fila_de_su_pareja_en_el_otro_documento():
    banco = [movimiento(2, 1, 100), movimiento(41, 30, -168090754)]
    sistema = [movimiento(512, 30, -168090754)]
    cruzar_exacto(banco, sistema)
    assert banco[1].filas_cruzadas == [512]
    assert sistema[0].filas_cruzadas == [41]


def test_los_repetidos_se_emparejan_en_orden_y_sobra_uno():
    banco = [movimiento(2, 1, 100), movimiento(3, 1, 100)]
    sistema = [movimiento(2, 1, 100), movimiento(3, 1, 100), movimiento(4, 1, 100)]
    assert cruzar_exacto(banco, sistema) == 2
    assert [m.filas_cruzadas for m in banco] == [[2], [3]]
    assert [m.filas_cruzadas for m in sistema] == [[2], [3], []]


def test_sin_coincidencias_no_cruza_nada():
    assert cruzar_exacto([movimiento(2, 1, 100)], [movimiento(2, 2, 100)]) == 0
