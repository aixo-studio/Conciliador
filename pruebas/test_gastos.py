"""Prueba de cómo se reconoce un gasto bancario, con configuraciones inventadas."""
import json

import pytest

from motor.gastos import ARCHIVO, cargar_configuracion, es_gasto


def configuracion_de(tmp_path, contenido):
    """Guarda un bancos.json inventado y lo carga."""
    ruta = tmp_path / "bancos.json"
    ruta.write_text(contenido if isinstance(contenido, str) else json.dumps(contenido), encoding="utf-8")
    return cargar_configuracion(ruta)


def test_reconoce_un_gasto_por_su_codigo_exacto(tmp_path):
    configuracion = configuracion_de(tmp_path, {"BBVA": {"gastos": ["005", "236"]}})
    assert es_gasto(configuracion, "BBVA", "236")
    assert es_gasto(configuracion, "BBVA", "005")
    assert not es_gasto(configuracion, "BBVA", "5")      # sin los ceros es otro código
    assert not es_gasto(configuracion, "BBVA", "319")    # no está en la lista
    assert not es_gasto(configuracion, "BBVA", "")       # vacío nunca es gasto


def test_frena_si_el_banco_no_esta_en_la_configuracion(tmp_path):
    configuracion = configuracion_de(tmp_path, {"BBVA": {"gastos": ["236"]}})
    with pytest.raises(ValueError, match='"Santander" no está en bancos.json'):
        es_gasto(configuracion, "Santander", "236")


@pytest.mark.parametrize("contenido, mensaje", [
    ('{"BBVA": {"gastos": ["236",]}}', "mal escrito"),
    ({}, "al menos un banco"),
    ({"BBVA": ["236"]}, 'tiene que tener "gastos"'),
    ({"BBVA": {"gastos": []}}, "al menos un código"),
    ({"BBVA": {"gasto": ["236"]}}, "campos desconocidos: gasto"),
    ({"BBVA": {"gastos": [236]}}, "tiene que ser un texto"),
    ({"BBVA": {"gastos": ["236", " "]}}, "tiene que ser un texto"),
    ({"BBVA": {"gastos": ["236", "236"]}}, "repetidos en la lista: 236"),
])
def test_frena_si_la_configuracion_esta_mal(tmp_path, contenido, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        configuracion_de(tmp_path, contenido)


def test_frena_si_no_existe_el_archivo(tmp_path):
    with pytest.raises(ValueError, match="no existe"):
        cargar_configuracion(tmp_path / "bancos.json")


def test_el_bancos_json_del_repo_esta_bien_armado():
    configuracion = cargar_configuracion(ARCHIVO)
    assert set(configuracion) == {"BBVA", "Galicia", "Supervielle"}
    assert (len(configuracion["BBVA"]), len(configuracion["Galicia"]), len(configuracion["Supervielle"])) == (20, 3, 8)
