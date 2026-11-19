"""Prueba del control: lo armado se compara contra el original, en filas y en
suma, y si algo no cierra frena con un error. Se rompen las listas a propósito.
Todo con datos inventados.
"""
from dataclasses import replace

import pytest

from motor.armar import armar_movimientos
from motor.configuracion import buscar_reglas
from motor.controlar import controlar

ENCABEZADO_BBVA = ["Fecha", "Fecha Valor", "Concepto", "Codigo", "Número Documento",
                   "Oficina", "Crédito", "Débito", "Detalle"]
REGLAS = buscar_reglas("BBVA", es_erp=False)
COLUMNAS = {nombre: posicion for posicion, nombre in enumerate(ENCABEZADO_BBVA)}
# Un extracto inventado: 319 y 005 son movimientos; 236 y 015 son gastos (lista real del BBVA).
DATOS = [(numero, ["30-09-2026", "30-09-2026", "X", codigo, "", "OF", credito, debito, ""])
         for numero, (codigo, credito, debito) in enumerate(
             [("319", 2500, ""), ("236", "", -12.5), ("005", "", -1500), ("015", "", -12.5)], start=2)]


def test_todo_bien_pasa():
    armados = armar_movimientos(COLUMNAS, DATOS, REGLAS)
    resumen = controlar(armados, COLUMNAS, DATOS, REGLAS)
    assert resumen["filas"] == 4 and resumen["suma"] == 250000 - 1250 - 150000 - 1250


def test_frena_si_se_pierde_una_fila_al_armar():
    armados = armar_movimientos(COLUMNAS, DATOS, REGLAS)
    with pytest.raises(ValueError, match="Se perdieron filas al armar: armadas 3, original 4"):
        controlar(armados[:-1], COLUMNAS, DATOS, REGLAS)


def test_frena_si_se_duplica_una_fila_al_armar():
    armados = armar_movimientos(COLUMNAS, DATOS, REGLAS)
    with pytest.raises(ValueError, match="Se perdieron filas al armar: armadas 5, original 4"):
        controlar(armados + [armados[0]], COLUMNAS, DATOS, REGLAS)


def test_frena_si_cambia_un_monto_al_armar():
    armados = armar_movimientos(COLUMNAS, DATOS, REGLAS)
    cambiado = [replace(armados[0], monto_centavos=armados[0].monto_centavos + 1)] + armados[1:]
    with pytest.raises(ValueError, match="La suma no cierra al armar"):
        controlar(cambiado, COLUMNAS, DATOS, REGLAS)
