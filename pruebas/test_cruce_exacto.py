"""Prueba del cruce exacto (paso 2), con movimientos inventados."""
from datetime import date

from motor.cruce_exacto import cruzar_exacto
from motor.entrada import Movimiento


def movimiento(fila, dia, centavos):
    """Un movimiento inventado de septiembre de 2026."""
    return Movimiento(fila=fila, fecha=date(2026, 9, dia), concepto="", descripcion="", monto_centavos=centavos)


def test_cruza_solo_misma_fecha_y_mismo_monto():
    banco = [movimiento(2, 1, -150000), movimiento(3, 2, 5000), movimiento(4, 3, 7000)]
    sistema = [movimiento(2, 1, -150000), movimiento(3, 3, 5000), movimiento(4, 3, 7001)]
    assert cruzar_exacto(banco, sistema) == 1
    assert [(m.estado, m.numero_cruce, m.criterio) for m in banco] == [
        ("Cruzado", 1, "Exacto"), ("Sin cruzar", None, ""), ("Sin cruzar", None, "")]
    assert [m.estado for m in sistema] == ["Cruzado", "Sin cruzar", "Sin cruzar"]


def test_los_repetidos_se_emparejan_en_orden_y_sobra_uno():
    banco = [movimiento(2, 1, 100), movimiento(3, 1, 100)]
    sistema = [movimiento(2, 1, 100), movimiento(3, 1, 100), movimiento(4, 1, 100)]
    assert cruzar_exacto(banco, sistema) == 2
    assert [m.numero_cruce for m in banco] == [1, 2]
    assert [m.numero_cruce for m in sistema] == [1, 2, None]


def test_sin_coincidencias_no_cruza_nada():
    assert cruzar_exacto([movimiento(2, 1, 100)], [movimiento(2, 2, 100)]) == 0
