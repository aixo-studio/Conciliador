"""Prueba de la lectura de la entrada (paso 1), con archivos inventados."""
from datetime import date

import pytest

from motor.entrada import encontrar_archivos, leer_movimientos, resumir
from pruebas.datos import carpeta_banco, dia, guardar_entrada


def test_lee_cada_fila_con_su_monto_en_centavos(tmp_path):
    ruta = guardar_entrada(tmp_path / "a.xlsx", [
        [dia(1), "TRANSFERENCIA", None, -1500],
        [dia(2), "DEPOSITO", "Cliente", 1500000.2499999],  # error mínimo de Excel
    ])
    primero, segundo = leer_movimientos(ruta)
    assert (primero.fila, primero.fecha, primero.descripcion, primero.monto_centavos) == (2, date(2026, 9, 1), "", -150000)
    assert (segundo.fila, segundo.monto_centavos, segundo.estado) == (3, 150000025, "Sin cruzar")


def test_el_codigo_se_lee_como_texto_con_sus_ceros(tmp_path):
    ruta = guardar_entrada(tmp_path / "a.xlsx", [[dia(1), "005", "", 1], [dia(1), None, "", 1]])
    assert [m.codigo for m in leer_movimientos(ruta)] == ["005", ""]


def test_resume_filas_suma_y_fechas(tmp_path):
    ruta = guardar_entrada(tmp_path / "a.xlsx", [[dia(5), "A", "", 10.5], [dia(1), "B", "", -0.25]])
    assert resumir(leer_movimientos(ruta)) == {
        "filas": 2, "suma": 1025, "desde": date(2026, 9, 1), "hasta": date(2026, 9, 5)}


def test_encuentra_el_archivo_del_banco_y_el_del_sistema(tmp_path):
    carpeta = carpeta_banco(tmp_path, [[dia(1), "A", "", 1]], [[dia(1), "A", "", 1]])
    banco, sistema = encontrar_archivos(carpeta)
    assert banco.name.startswith("banco_") and sistema.name.startswith("sistema_")


@pytest.mark.parametrize("nombres, mensaje", [
    (["banco_bbva - a.xlsx"], "hay 1 y 0"),
    (["banco_bbva - a.xlsx", "banco_bbva - b.xlsx", "sistema_finnegans - c.xlsx"], "hay 2 y 1"),
    (["banco_bbva - a.xlsx", "sistema_finnegans - c.xlsx", "otro.xlsx"], "otro.xlsx"),
])
def test_frena_si_no_hay_uno_de_cada_uno(tmp_path, nombres, mensaje):
    for nombre in nombres:
        guardar_entrada(tmp_path / nombre, [[dia(1), "A", "", 1]])
    with pytest.raises(ValueError, match=mensaje):
        encontrar_archivos(tmp_path)


def test_ignora_ocultos_y_temporales_de_excel(tmp_path):
    carpeta = carpeta_banco(tmp_path, [[dia(1), "A", "", 1]], [[dia(1), "A", "", 1]])
    (carpeta / "~$banco_bbva - extracto.xlsx").write_text("temporal")
    assert len(encontrar_archivos(carpeta)) == 2


def test_frena_si_no_existe_la_carpeta(tmp_path):
    with pytest.raises(ValueError, match="no existe"):
        encontrar_archivos(tmp_path / "Galicia")


@pytest.mark.parametrize("como, mensaje", [
    ({"hoja": "Hoja1"}, "una sola hoja"),
    ({"hojas_de_mas": ["Gastos"]}, "una sola hoja"),
    ({"encabezado": ("Fecha", "Concepto", "Descripción", "Monto")}, "encabezado"),  # el contrato viejo
    ({"encabezado": ("Fecha", "Código", "Detalle", "Monto")}, "encabezado"),
    ({"encabezado": ("Fecha", "Código", "Descripción", "Monto", "Saldo")}, "encabezado"),
])
def test_frena_si_la_hoja_o_el_encabezado_no_cumplen(tmp_path, como, mensaje):
    ruta = guardar_entrada(tmp_path / "a.xlsx", [[dia(1), "A", "", 1]], **como)
    with pytest.raises(ValueError, match=mensaje):
        leer_movimientos(ruta)


@pytest.mark.parametrize("filas, mensaje", [
    ([["01/09/2026", "A", "", 1]], "fila 2: la Fecha no es una fecha"),
    ([[dia(1), "A", "", None]], "fila 2: el Monto no es un número"),
    ([[dia(1), "A", "", "1.500,00"]], "fila 2: el Monto no es un número"),
    ([[dia(1), "A", "", 1], [None, None, None, None], [dia(2), "B", "", 2]], "fila 3: está vacía"),
    ([[dia(1), "A", "", 1, "extra"]], "fila 2: tiene datos fuera"),
    ([[dia(1), 5, "", 1]], "fila 2: el Código no es texto"),
    ([], "no tiene movimientos"),
])
def test_frena_si_una_fila_no_cumple(tmp_path, filas, mensaje):
    ruta = guardar_entrada(tmp_path / "a.xlsx", filas)
    with pytest.raises(ValueError, match=mensaje):
        leer_movimientos(ruta)
