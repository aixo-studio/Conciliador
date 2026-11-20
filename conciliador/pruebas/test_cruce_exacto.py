"""Prueba del cruce exacto (paso 2): qué cruza, qué queda pendiente de cada
lado y con qué fila del ERP cruzó cada una. Todo con datos inventados.
"""
from conciliador.motor.cruce_exacto import COLUMNA_PAREJA, cruzar_exacto
from conciliador.motor.recibir import COLUMNAS
from conciliador.pruebas.datos import tabla


def test_cruza_misma_fecha_y_mismo_monto():
    cruces, banco, erp = cruzar_exacto(tabla([(1, "319", "", 100, "Movimiento")]),
                                       tabla([(1, "Orden de pago", "", 100, "Movimiento")]))
    assert list(cruces.columns) == COLUMNAS + [COLUMNA_PAREJA]
    # Cruzó la única fila del banco con la fila 0 del ERP, y no quedó nada.
    assert list(cruces.index) == [0] and list(cruces[COLUMNA_PAREJA]) == [0]
    assert banco.empty and erp.empty


def test_no_cruza_si_cambia_la_fecha_o_el_monto():
    cruces, banco, erp = cruzar_exacto(
        tabla([(1, "319", "", 100, "Movimiento"), (2, "319", "", 200, "Movimiento")]),
        tabla([(2, "OP", "", 100, "Movimiento"), (1, "OP", "", 200, "Movimiento")]))
    assert cruces.empty and len(banco) == 2 and len(erp) == 2


def test_los_repetidos_se_emparejan_en_orden():
    repetido = (2, "005", "", 700, "Movimiento")
    cruces, banco, erp = cruzar_exacto(tabla([repetido] * 3), tabla([repetido] * 2))
    # El 1.º con el 1.º y el 2.º con el 2.º; el 3.º del banco queda pendiente.
    assert list(cruces.index) == [0, 1] and list(cruces[COLUMNA_PAREJA]) == [0, 1]
    assert list(banco.index) == [2] and erp.empty


def test_un_gasto_bancario_no_cruza_aunque_tenga_pareja_perfecta():
    cruces, banco, erp = cruzar_exacto(tabla([(1, "236", "IMPUESTO", -50, "Gasto bancario")]),
                                       tabla([(1, "OP", "", -50, "Movimiento")]))
    assert cruces.empty
    # El gasto queda pendiente en el banco, y su pareja perfecta, en el ERP.
    assert len(banco) == 1 and len(erp) == 1


def test_los_gastos_siempre_quedan_en_el_banco_pendiente():
    cruces, banco, erp = cruzar_exacto(
        tabla([(1, "319", "", 100, "Movimiento"), (1, "236", "", -50, "Gasto bancario"),
               (2, "015", "", -950, "Gasto bancario")]),
        tabla([(1, "OP", "", 100, "Movimiento")]))
    assert list(cruces.index) == [0]
    assert list(banco.index) == [1, 2] and list(banco["Clase"]) == ["Gasto bancario"] * 2


def test_las_tablas_que_entran_no_se_modifican():
    filas_banco = [(1, "319", "", 100, "Movimiento")]
    filas_erp = [(1, "OP", "", 100, "Movimiento")]
    tabla_banco, tabla_erp = tabla(filas_banco), tabla(filas_erp)
    cruces, banco, erp = cruzar_exacto(tabla_banco, tabla_erp)
    # Tocar lo que salió del cruce no toca lo que entró: las dos siguen siendo
    # el testigo contra el que compara el control del final.
    cruces.loc[0, "Monto en centavos"] = 1
    assert tabla_banco.equals(tabla(filas_banco)) and tabla_erp.equals(tabla(filas_erp))


def test_no_se_pierde_ninguna_fila():
    filas_banco = [(1, "319", "", 100, "Movimiento"), (1, "236", "", -50, "Gasto bancario"),
                   (2, "005", "", 700, "Movimiento")]
    filas_erp = [(1, "OP", "", 100, "Movimiento"), (3, "RC", "", 900, "Movimiento")]
    cruces, banco, erp = cruzar_exacto(tabla(filas_banco), tabla(filas_erp))
    assert len(cruces) + len(banco) == len(filas_banco)
    assert len(cruces) + len(erp) == len(filas_erp)


def test_si_no_cruza_nada_la_tabla_de_cruces_sale_vacia_pero_con_sus_columnas():
    cruces, banco, erp = cruzar_exacto(tabla([(1, "319", "", 100, "Movimiento")]),
                                       tabla([(2, "OP", "", 300, "Movimiento")]))
    assert cruces.empty and list(cruces.columns) == COLUMNAS + [COLUMNA_PAREJA]
    # El tipo de la columna no depende de que haya cruzado algo.
    assert str(cruces[COLUMNA_PAREJA].dtype) == "int64"


def test_con_los_mismos_datos_siempre_da_el_mismo_resultado():
    filas_banco = [(1, "319", "", 100, "Movimiento"), (1, "236", "", -50, "Gasto bancario"),
                   (2, "005", "", 700, "Movimiento"), (2, "005", "", 700, "Movimiento")]
    filas_erp = [(2, "OP", "", 700, "Movimiento"), (1, "OP", "", 100, "Movimiento"),
                 (2, "OP", "", 700, "Movimiento")]
    primera = cruzar_exacto(tabla(filas_banco), tabla(filas_erp))
    segunda = cruzar_exacto(tabla(filas_banco), tabla(filas_erp))
    for una, otra in zip(primera, segunda):
        assert una.equals(otra)
