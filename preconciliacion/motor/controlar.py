"""Paso 4 del proceso: controlar que no se perdió nada."""
from motor.armar import Movimiento, a_centavos, es_ignorada, esta_vacia


def controlar(movimientos: list[Movimiento], columnas: dict, datos: list, reglas: dict) -> dict:
    """Recibe los movimientos armados y las filas originales.
    Vuelve a contar filas y a sumar créditos y débitos directo del original, y los
    compara con los movimientos. Si algo no cierra, frena con un error.
    Devuelve el resumen: filas, filas ignoradas, créditos, débitos y suma (en centavos).
    """
    con_datos = [(numero, fila) for numero, fila in datos if not esta_vacia(fila)]
    filas_original = [(numero, fila) for numero, fila in con_datos if not es_ignorada(fila, columnas, reglas)]
    ignoradas = len(con_datos) - len(filas_original)
    creditos = sum(abs(a_centavos(fila[columnas[reglas["credito"]]], numero)) for numero, fila in filas_original)
    debitos = sum(abs(a_centavos(fila[columnas[reglas["debito"]]], numero)) for numero, fila in filas_original)
    suma = sum(movimiento.monto_centavos for movimiento in movimientos)
    if len(movimientos) != len(filas_original):
        raise ValueError(f"Se perdieron filas al armar: armadas {len(movimientos)}, original {len(filas_original)}.")
    if suma != creditos - debitos:
        raise ValueError(f"La suma no cierra al armar: armado {suma / 100}, original {(creditos - debitos) / 100}.")
    return {"filas": len(movimientos), "ignoradas": ignoradas,
            "creditos": creditos, "debitos": debitos, "suma": suma}
