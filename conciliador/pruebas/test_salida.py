"""Prueba de la salida en CSV: los cuatro archivos, su forma (para que Excel los
abra bien) y que reemplacen a los de una corrida anterior. Con datos inventados.
"""
import pandas

from conciliador.cruzar_cuenta import cruzar_cuenta
from conciliador.motor.salida import escribir_csv
from conciliador.pruebas.datos import tabla

FILAS_BANCO = [(1, "319", "TRANSFERENCIA", 100, "Movimiento"),
               (1, "236", "IMPUESTO", -50, "Gasto bancario"),
               (2, "005", "", 700, "Movimiento")]
FILAS_ERP = [(3, "Recibo de Cobranzas", "", 900, "Movimiento"),
             (1, "Orden de pago", "PAGO", 100, "Movimiento")]


def leer(ruta):
    """Lee un CSV de la salida tal como lo escribió el programa, todo como texto."""
    return pandas.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)


def test_escribe_los_cuatro_csv(tmp_path):
    resultado = cruzar_cuenta(tabla(FILAS_BANCO), tabla(FILAS_ERP))

    rutas = escribir_csv(*resultado, tmp_path / "salida")

    assert [ruta.name for ruta in rutas] == ["cruces.csv", "banco_pendiente.csv",
                                            "erp_pendiente.csv", "resumen.csv"]
    # La transferencia del banco (fila 0) cruza con la orden de pago (fila 1 del ERP).
    cruces = leer(rutas[0])
    assert list(cruces.columns) == ["Fila", "Fecha", "Código", "Descripción",
                                    "Monto en centavos", "Clase", "Fila en ERP"]
    assert cruces.iloc[0].tolist() == ["0", "01/09/2026", "319", "TRANSFERENCIA",
                                       "100", "Movimiento", "1"]
    # Lo pendiente conserva su número de fila y el Código con sus ceros.
    banco = leer(rutas[1])
    assert list(banco["Fila"]) == ["1", "2"] and list(banco["Código"]) == ["236", "005"]
    assert list(leer(rutas[2])["Fila"]) == ["0"]


def test_el_resumen_tiene_una_fila_por_lado_y_parte(tmp_path):
    resultado = cruzar_cuenta(tabla(FILAS_BANCO), tabla(FILAS_ERP))

    resumen = leer(escribir_csv(*resultado, tmp_path)[3])

    assert list(resumen.columns) == ["Lado", "Parte", "Filas", "Suma en centavos"]
    assert resumen.iloc[0].tolist() == ["Banco", "Entrada", "3", "750"]
    assert resumen.iloc[3].tolist() == ["Banco", "Gasto bancario", "1", "-50"]
    assert resumen.iloc[-1].tolist() == ["ERP", "Pendiente", "1", "900"]


def test_excel_en_castellano_lo_abre_bien(tmp_path):
    resultado = cruzar_cuenta(tabla(FILAS_BANCO), tabla(FILAS_ERP))

    ruta = escribir_csv(*resultado, tmp_path)[0]

    # Empieza con la marca de utf-8 (los acentos) y separa con punto y coma.
    contenido = ruta.read_bytes()
    assert contenido.startswith(b"\xef\xbb\xbf")
    assert contenido.decode("utf-8-sig").splitlines()[0].startswith("Fila;Fecha;Código;")


def test_escribe_las_columnas_que_traiga_la_tabla(tmp_path):
    cruces, banco, erp, resumen = cruzar_cuenta(tabla(FILAS_BANCO), tabla(FILAS_ERP))
    # Una pasada futura podría agregar columnas: la salida las escribe igual.
    cruces["Criterio"] = "exacto"

    ruta = escribir_csv(cruces, banco, erp, resumen, tmp_path)[0]

    assert list(leer(ruta).columns)[-1] == "Criterio"


def test_reemplaza_los_csv_de_una_corrida_anterior(tmp_path):
    (tmp_path / "cruces.csv").write_text("lo de antes", encoding="utf-8")
    resultado = cruzar_cuenta(tabla(FILAS_BANCO), tabla(FILAS_ERP))

    escribir_csv(*resultado, tmp_path)

    assert list(leer(tmp_path / "cruces.csv")["Código"]) == ["319"]
