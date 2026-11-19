"""Prueba del control del cruce (paso 3): con lo que devolvió el cruce se
vuelve a armar lo que entró. Se rompen los resultados a propósito.
Todo con datos inventados.
"""
import pandas
import pytest

from conciliador.motor.controlar import validar_y_resumir_cruce
from conciliador.motor.cruce_exacto import COLUMNA_PAREJA, cruzar_exacto
from conciliador.pruebas.datos import tabla

# Una cuenta inventada: cruza la transferencia; quedan un gasto, un movimiento
# del banco y un movimiento del ERP.
FILAS_BANCO = [(1, "319", "TRANSFERENCIA", 100, "Movimiento"),
               (1, "236", "IMPUESTO", -50, "Gasto bancario"),
               (2, "005", "", 700, "Movimiento")]
FILAS_ERP = [(1, "Orden de pago", "PAGO", 100, "Movimiento"),
             (3, "Recibo de Cobranzas", "", 900, "Movimiento")]


def cuenta():
    """Devuelve las dos tablas que entran y las tres que devolvió el cruce."""
    tabla_banco, tabla_erp = tabla(FILAS_BANCO), tabla(FILAS_ERP)
    return (tabla_banco, tabla_erp) + cruzar_exacto(tabla_banco, tabla_erp)


def validar(tabla_banco, tabla_erp, cruces, banco, erp):
    """Llama al control con las tablas en el orden que espera."""
    return validar_y_resumir_cruce(cruces, banco, erp, tabla_banco, tabla_erp)


def test_un_cruce_correcto_pasa_y_devuelve_el_resumen():
    tabla_banco, tabla_erp, cruces, banco, erp = cuenta()
    resumen = validar(tabla_banco, tabla_erp, cruces, banco, erp)
    assert resumen["Banco"] == {"Entrada": (3, 750), "Cruzado": (1, 100),
                                "Pendiente": (2, 650), "Gasto bancario": (1, -50)}
    assert resumen["ERP"] == {"Entrada": (2, 1000), "Cruzado": (1, 100), "Pendiente": (1, 900)}


def test_cruzado_mas_pendiente_da_lo_que_entro():
    tabla_banco, tabla_erp, cruces, banco, erp = cuenta()
    resumen = validar(tabla_banco, tabla_erp, cruces, banco, erp)
    for lado in ("Banco", "ERP"):
        filas = resumen[lado]["Cruzado"][0] + resumen[lado]["Pendiente"][0]
        suma = resumen[lado]["Cruzado"][1] + resumen[lado]["Pendiente"][1]
        assert (filas, suma) == resumen[lado]["Entrada"]


def test_frena_si_falta_una_fila_del_banco():
    tabla_banco, tabla_erp, cruces, banco, erp = cuenta()
    with pytest.raises(ValueError, match="el banco pendiente no es lo que entró"):
        validar(tabla_banco, tabla_erp, cruces, banco.iloc[:-1], erp)


def test_frena_si_cambia_un_monto():
    tabla_banco, tabla_erp, cruces, banco, erp = cuenta()
    cruces.loc[0, "Monto en centavos"] = 101
    with pytest.raises(ValueError, match="no son las que entraron del banco"):
        validar(tabla_banco, tabla_erp, cruces, banco, erp)


def test_frena_si_el_erp_pendiente_trae_filas_que_ya_cruzaron():
    tabla_banco, tabla_erp, cruces, banco, erp = cuenta()
    with pytest.raises(ValueError, match="el ERP pendiente no es lo que entró"):
        validar(tabla_banco, tabla_erp, cruces, banco, tabla_erp)


def test_frena_si_un_gasto_bancario_cruzo():
    tabla_banco, tabla_erp, cruces, banco, erp = cuenta()
    # Se mete a la fuerza el gasto (fila 1 del banco) en la tabla de cruces.
    forzada = pandas.concat([cruces, tabla_banco.loc[[1]].assign(**{COLUMNA_PAREJA: 1})])
    with pytest.raises(ValueError, match="es un gasto bancario y cruzó"):
        validar(tabla_banco, tabla_erp, forzada, banco.drop(1), erp.drop(1))


def test_frena_si_una_fila_del_erp_cruzo_con_dos_del_banco():
    tabla_banco, tabla_erp, cruces, banco, erp = cuenta()
    otra = tabla_banco.loc[[2]].assign(**{COLUMNA_PAREJA: 0})
    with pytest.raises(ValueError, match="cruzó con más de una del banco"):
        validar(tabla_banco, tabla_erp, pandas.concat([cruces, otra]), banco.drop(2), erp)


def test_frena_si_apunta_a_una_fila_que_no_existe_en_el_erp():
    tabla_banco, tabla_erp, cruces, banco, erp = cuenta()
    cruces.loc[0, COLUMNA_PAREJA] = 9
    with pytest.raises(ValueError, match="filas que no existen en el ERP"):
        validar(tabla_banco, tabla_erp, cruces, banco, erp)
