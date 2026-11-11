"""Prueba de la recepción (paso 1): el control de la forma de la tabla que llega
de la etapa 1 y el Estado con el que arranca cada fila. Se rompen las tablas a
propósito. Todo con datos inventados.
"""
import pandas
import pytest

from motor.recibir import COLUMNAS, controlar_forma, poner_estado, recibir_documento
from pruebas.datos import tabla

# Un extracto inventado: dos movimientos y dos gastos bancarios, mezclados.
FILAS = [(1, "319", "TRANSFERENCIA", 25000000, "Movimiento"),
         (1, "236", "IMPUESTO LEY", -1250, "Gasto bancario"),
         (2, "005", "", -15000000, "Movimiento"),
         (2, "015", "COMISION", -950, "Gasto bancario")]


def cambiada(columna, valor, fila=0):
    """Devuelve la tabla inventada con un valor cambiado en esa columna y esa fila."""
    rota = tabla(FILAS).astype({columna: object})
    rota.loc[fila, columna] = valor
    return rota


def test_una_tabla_correcta_pasa():
    controlar_forma(tabla(FILAS), es_sistema=False)
    # El libro del sistema: todas las filas son "Movimiento".
    controlar_forma(tabla([(1, "Orden de pago", "PAGO", -100, "Movimiento")]), es_sistema=True)


@pytest.mark.parametrize("romper", [
    lambda buena: buena.drop(columns="Clase"),                            # falta una columna
    lambda buena: buena.assign(Saldo=0),                                  # hay una de más
    lambda buena: buena[["Código", "Fecha"] + COLUMNAS[2:]],              # están en otro orden
    lambda buena: buena.rename(columns={"Monto en centavos": "Monto"}),   # una tiene otro nombre
])
def test_frena_si_las_columnas_no_son_las_acordadas(romper):
    with pytest.raises(ValueError, match="las columnas tienen que ser"):
        controlar_forma(romper(tabla(FILAS)), es_sistema=False)


def test_frena_si_no_tiene_filas():
    with pytest.raises(ValueError, match="no tiene movimientos"):
        controlar_forma(tabla([]), es_sistema=False)


@pytest.mark.parametrize("columna, valor, motivo", [
    ("Fecha", pandas.NaT, "la Fecha no es una fecha"),
    ("Fecha", "30-09-2026", "la Fecha no es una fecha"),
    ("Código", 236, "el Código no es texto"),
    ("Descripción", None, "la Descripción no es texto"),
    ("Monto en centavos", -1250.5, "el Monto en centavos no es un entero"),
    ("Monto en centavos", "100", "el Monto en centavos no es un entero"),
    ("Clase", "", "la Clase tiene que ser"),
    ("Clase", "gasto bancario", "la Clase tiene que ser"),
    ("Clase", "Movimiento ", "la Clase tiene que ser"),
])
def test_frena_si_una_fila_no_tiene_la_forma_acordada(columna, valor, motivo):
    with pytest.raises(ValueError, match=f"hay 1 fila con errores:\n  fila 1: {motivo}"):
        controlar_forma(cambiada(columna, valor), es_sistema=False)


def test_frena_si_el_monto_llega_con_decimales_en_toda_la_columna():
    rota = tabla(FILAS).astype({"Monto en centavos": float})
    with pytest.raises(ValueError, match="hay 4 filas con errores"):
        controlar_forma(rota, es_sistema=False)


def test_frena_si_el_libro_del_sistema_trae_un_gasto_bancario():
    with pytest.raises(ValueError, match="fila 2: es un gasto bancario"):
        controlar_forma(tabla(FILAS), es_sistema=True)


def test_informa_todas_las_filas_con_errores_juntas():
    rota = cambiada("Clase", "Otra", fila=0)
    rota.loc[2, "Código"] = 5
    with pytest.raises(ValueError) as error:
        controlar_forma(rota, es_sistema=False)
    mensaje = str(error.value)
    assert "hay 2 filas con errores" in mensaje
    assert "fila 1: la Clase" in mensaje and "fila 3: el Código" in mensaje


def test_muestra_los_primeros_20_errores_y_dice_cuantos_mas_hay():
    rota = tabla([(1, "319", "", 100, "Otra")] * 25)
    with pytest.raises(ValueError) as error:
        controlar_forma(rota, es_sistema=False)
    mensaje = str(error.value)
    assert "hay 25 filas con errores" in mensaje and "… y 5 más." in mensaje
    assert "fila 20:" in mensaje and "fila 21:" not in mensaje


def test_cada_fila_arranca_con_el_estado_de_su_clase():
    resultado = poner_estado(tabla(FILAS))
    assert list(resultado.columns) == COLUMNAS + ["Estado"]
    assert list(resultado["Estado"]) == ["Sin cruzar", "Gasto bancario", "Sin cruzar", "Gasto bancario"]


def test_la_tabla_recibida_no_cambia_al_poner_el_estado():
    recibida = tabla(FILAS)
    resultado = poner_estado(recibida)
    # La recibida sigue igual, sin la columna nueva; y la copia conserva las cinco columnas.
    assert recibida.equals(tabla(FILAS))
    assert resultado[COLUMNAS].equals(recibida)


def test_recibir_documento_devuelve_la_foto_y_la_copia_con_estado():
    foto, resultado = recibir_documento(tabla(FILAS), es_sistema=False)
    # La foto es lo que entró, sin la columna nueva; la copia la tiene.
    assert foto.equals(tabla(FILAS))
    assert list(resultado["Estado"]) == ["Sin cruzar", "Gasto bancario", "Sin cruzar", "Gasto bancario"]


def test_recibir_documento_frena_si_la_tabla_no_cumple_el_contrato():
    with pytest.raises(ValueError, match="la Clase tiene que ser"):
        recibir_documento(cambiada("Clase", "Otra"), es_sistema=False)


def test_tocar_la_copia_no_toca_la_foto():
    foto, resultado = recibir_documento(tabla(FILAS), es_sistema=False)
    resultado.loc[0, "Monto en centavos"] = 1
    resultado.loc[0, "Estado"] = "Cruzado"
    assert foto.equals(tabla(FILAS))
