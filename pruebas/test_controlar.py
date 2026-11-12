"""Prueba del control del final (paso 3): el resultado se compara contra la
tabla tal como llegó, y si algo no cierra frena diciendo qué regla falló.
Se rompen los resultados a propósito. Todo con datos inventados.
"""
import pandas
import pytest

from motor.controlar import validar_y_resumir_tabla_cruzada
from motor.recibir import crear_copia_con_estado
from pruebas.datos import tabla

# Un extracto inventado: tres movimientos y dos gastos bancarios, mezclados.
FILAS = [(1, "319", "TRANSFERENCIA", 25000000, "Movimiento"),
         (1, "236", "IMPUESTO LEY", -1250, "Gasto bancario"),
         (2, "005", "", -15000000, "Movimiento"),
         (2, "015", "COMISION", -950, "Gasto bancario"),
         (3, "319", "TRANSFERENCIA", 8000000, "Movimiento")]


def ya_cruzado():
    """Devuelve la tabla recibida y su resultado como lo dejaría el cruce:
    la primera fila "Cruzado", los otros dos movimientos "Sin cruzar".
    """
    recibida = tabla(FILAS)
    resultado = crear_copia_con_estado(recibida)
    resultado.loc[0, "Estado"] = "Cruzado"
    return recibida, resultado


def test_un_resultado_correcto_pasa_y_devuelve_el_resumen():
    recibida, resultado = ya_cruzado()
    assert validar_y_resumir_tabla_cruzada(resultado, recibida) == {
        "Entrada": (5, 25000000 - 1250 - 15000000 - 950 + 8000000),
        "Cruzado": (1, 25000000),
        "Sin cruzar": (2, -15000000 + 8000000),
        "Gasto bancario": (2, -1250 - 950)}


def test_cruzado_mas_sin_cruzar_mas_gasto_bancario_da_la_entrada():
    recibida, resultado = ya_cruzado()
    resumen = validar_y_resumir_tabla_cruzada(resultado, recibida)
    partes = [resumen["Cruzado"], resumen["Sin cruzar"], resumen["Gasto bancario"]]
    assert (sum(filas for filas, _ in partes), sum(suma for _, suma in partes)) == resumen["Entrada"]


def test_frena_si_se_pierde_una_fila():
    recibida, resultado = ya_cruzado()
    with pytest.raises(ValueError, match="llegaron 5 y quedaron 4"):
        validar_y_resumir_tabla_cruzada(resultado.iloc[:-1], recibida)


def test_frena_si_se_duplica_una_fila():
    recibida, resultado = ya_cruzado()
    with pytest.raises(ValueError, match="llegaron 5 y quedaron 6"):
        validar_y_resumir_tabla_cruzada(pandas.concat([resultado, resultado.iloc[[0]]]), recibida)


def test_frena_si_cambia_un_monto():
    recibida, resultado = ya_cruzado()
    resultado.loc[2, "Monto en centavos"] += 1
    with pytest.raises(ValueError, match="la suma no cierra"):
        validar_y_resumir_tabla_cruzada(resultado, recibida)


def test_frena_si_dos_montos_cambian_y_se_compensan():
    # La cantidad de filas y la suma siguen dando bien: lo atrapa la comparación fila por fila.
    recibida, resultado = ya_cruzado()
    resultado.loc[0, "Monto en centavos"] += 1
    resultado.loc[2, "Monto en centavos"] -= 1
    with pytest.raises(ValueError, match="la fila 1 no es la que llegó"):
        validar_y_resumir_tabla_cruzada(resultado, recibida)


def test_frena_si_las_filas_quedan_en_otro_orden():
    recibida, resultado = ya_cruzado()
    desordenado = resultado.iloc[[1, 0, 2, 3, 4]]
    with pytest.raises(ValueError, match="la fila 1 no es la que llegó"):
        validar_y_resumir_tabla_cruzada(desordenado, recibida)


def test_frena_si_cambia_la_clase_de_una_fila():
    recibida, resultado = ya_cruzado()
    resultado.loc[1, "Clase"] = "Movimiento"
    with pytest.raises(ValueError, match="la fila 2 no es la que llegó"):
        validar_y_resumir_tabla_cruzada(resultado, recibida)


def test_frena_si_una_fila_queda_con_un_estado_que_no_existe():
    recibida, resultado = ya_cruzado()
    resultado.loc[2, "Estado"] = "Otro"
    with pytest.raises(ValueError, match="fila 3: el Estado no es válido"):
        validar_y_resumir_tabla_cruzada(resultado, recibida)


def test_frena_si_un_gasto_bancario_queda_cruzado():
    recibida, resultado = ya_cruzado()
    resultado.loc[1, "Estado"] = "Cruzado"
    with pytest.raises(ValueError, match='fila 2: es un gasto bancario y quedó "Cruzado"'):
        validar_y_resumir_tabla_cruzada(resultado, recibida)


def test_frena_si_un_movimiento_queda_como_gasto_bancario():
    recibida, resultado = ya_cruzado()
    resultado.loc[2, "Estado"] = "Gasto bancario"
    with pytest.raises(ValueError, match='fila 3: es un movimiento y quedó "Gasto bancario"'):
        validar_y_resumir_tabla_cruzada(resultado, recibida)
