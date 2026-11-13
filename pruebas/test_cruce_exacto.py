"""Prueba del cruce exacto sobre las tablas (paso 2): solo cruzan las filas
"Sin cruzar", los repetidos se emparejan en orden y cada pareja se anota con
la fila de la otra hoja del Excel de salida. Todo con datos inventados.
"""
from motor.cruce_exacto import cruzar_exacto
from motor.recibir import crear_copia_con_estado
from pruebas.datos import tabla


def lados(filas_banco, filas_sistema):
    """Devuelve las dos tablas listas para cruzar (recibidas y con su Estado)."""
    banco = crear_copia_con_estado(tabla(filas_banco))
    sistema = crear_copia_con_estado(tabla(filas_sistema))
    return banco, sistema


def test_cruza_misma_fecha_y_mismo_monto():
    banco, sistema = lados([(1, "319", "", 100, "Movimiento")],
                           [(1, "Orden de pago", "", 100, "Movimiento")])
    assert cruzar_exacto(banco, sistema) == 1
    assert list(banco["Estado"]) == ["Cruzado"] and list(sistema["Estado"]) == ["Cruzado"]
    # Cada una apunta a la fila de la otra en el Excel: los datos empiezan en la fila 2.
    assert banco.loc[0, "Fila en Sistema"] == 2 and sistema.loc[0, "Fila en Banco"] == 2


def test_no_cruza_si_cambia_la_fecha_o_el_monto():
    banco, sistema = lados([(1, "319", "", 100, "Movimiento"), (2, "319", "", 200, "Movimiento")],
                           [(2, "OP", "", 100, "Movimiento"), (1, "OP", "", 200, "Movimiento")])
    assert cruzar_exacto(banco, sistema) == 0
    assert set(banco["Estado"]) == {"Sin cruzar"} and set(sistema["Estado"]) == {"Sin cruzar"}
    assert banco["Fila en Sistema"].isna().all() and sistema["Fila en Banco"].isna().all()


def test_los_repetidos_se_emparejan_en_orden():
    repetido = (2, "005", "", 700, "Movimiento")
    banco, sistema = lados([repetido] * 3, [repetido] * 2)
    assert cruzar_exacto(banco, sistema) == 2
    assert list(banco["Estado"]) == ["Cruzado", "Cruzado", "Sin cruzar"]
    assert list(banco["Fila en Sistema"].fillna(0)) == [2, 3, 0]
    assert list(sistema["Fila en Banco"].fillna(0)) == [2, 3]


def test_un_gasto_bancario_no_cruza_aunque_tenga_pareja_perfecta():
    banco, sistema = lados([(1, "236", "IMPUESTO", -50, "Gasto bancario")],
                           [(1, "OP", "", -50, "Movimiento")])
    assert cruzar_exacto(banco, sistema) == 0
    assert list(banco["Estado"]) == ["Gasto bancario"] and banco["Fila en Sistema"].isna().all()
    # Su "pareja" del sistema queda sin cruzar, para que la mire una persona.
    assert list(sistema["Estado"]) == ["Sin cruzar"]


def test_una_fila_cruzada_no_vuelve_a_cruzar():
    banco, sistema = lados([(1, "319", "", 100, "Movimiento")],
                           [(1, "OP", "", 100, "Movimiento"), (1, "OP", "", 100, "Movimiento")])
    assert cruzar_exacto(banco, sistema) == 1
    # Una segunda corrida no cruza nada más ni pisa las parejas ya anotadas.
    assert cruzar_exacto(banco, sistema) == 0
    assert banco.loc[0, "Fila en Sistema"] == 2
    assert list(sistema["Estado"]) == ["Cruzado", "Sin cruzar"]


def test_el_numero_de_pareja_cuenta_las_filas_del_excel():
    banco, sistema = lados([(1, "a", "", 1, "Movimiento"), (1, "b", "", 2, "Movimiento"),
                            (1, "c", "", 300, "Movimiento")],
                           [(1, "OP", "", 300, "Movimiento")])
    assert cruzar_exacto(banco, sistema) == 1
    # La tercera fila del banco es la fila 4 del Excel (el encabezado es la 1).
    assert sistema.loc[0, "Fila en Banco"] == 4 and banco.loc[2, "Fila en Sistema"] == 2
