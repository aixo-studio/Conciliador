"""Cómo se reconoce un gasto bancario.

La lista de lo que es gasto en cada banco no está en el código: está en
bancos.json, en la raíz del repo. Por cada banco que sabemos procesar, la lista
de valores de la columna Código que significan "gasto bancario". Se compara el
valor exacto, como texto.

Agregar un gasto o un banco es editar bancos.json, no este archivo.
Todavía no está conectado al cruce: solo responde si un código es gasto.
"""
import json
from pathlib import Path

ARCHIVO = Path(__file__).resolve().parent.parent / "bancos.json"
CAMPOS = {"gastos", "nota"}  # lo único que puede tener cada banco


def cargar_configuracion(ruta: Path = ARCHIVO) -> dict:
    """Recibe la ruta de bancos.json. Lo lee y controla que esté bien armado.
    Devuelve, por banco, el conjunto de códigos que son gasto.
    Frena si el archivo no existe, no es JSON válido, o algún banco está mal.
    """
    if not ruta.is_file():
        raise ValueError(f"no existe el archivo de configuración {ruta.name}.")
    try:
        contenido = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{ruta.name} está mal escrito (línea {error.lineno}): {error.msg}.") from None
    if not isinstance(contenido, dict) or not contenido:
        raise ValueError(f"{ruta.name} tiene que tener al menos un banco.")
    return {banco: controlar_banco(banco, datos) for banco, datos in contenido.items()}


def controlar_banco(banco: str, datos) -> frozenset:
    """Recibe un banco y lo que dice bancos.json de él. Controla que tenga una
    lista de gastos no vacía, de textos, sin repetidos, y ningún campo de más
    (así un error de tipeo como "gasto" en vez de "gastos" no pasa en silencio).
    Devuelve el conjunto de códigos de gasto.
    """
    if not isinstance(datos, dict):
        raise ValueError(f'banco "{banco}": tiene que tener "gastos".')
    de_mas = set(datos) - CAMPOS
    if de_mas:
        raise ValueError(f'banco "{banco}": campos desconocidos: {", ".join(sorted(de_mas))}.')
    gastos = datos.get("gastos")
    if not isinstance(gastos, list) or not gastos:
        raise ValueError(f'banco "{banco}": "gastos" tiene que ser una lista con al menos un código.')
    # Los códigos son texto: "005" no es lo mismo que 5.
    for codigo in gastos:
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError(f'banco "{banco}": el código {codigo!r} tiene que ser un texto no vacío.')
    # En la lista cada código va una sola vez: uno repetido suele ser un error al editarla.
    repetidos = sorted({codigo for codigo in gastos if gastos.count(codigo) > 1})
    if repetidos:
        raise ValueError(f'banco "{banco}": códigos repetidos en la lista: {", ".join(repetidos)}.')
    return frozenset(gastos)


def es_gasto(configuracion: dict, banco: str, codigo: str) -> bool:
    """Recibe la configuración, el banco (el nombre de su carpeta) y el Código de
    una fila. Devuelve True si ese código es un gasto bancario en ese banco.
    Frena si el banco no está en la configuración: no sabemos qué es gasto ahí.
    """
    if banco not in configuracion:
        raise ValueError(f'el banco "{banco}" no está en bancos.json: no sabemos qué es gasto en ese banco.')
    return codigo in configuracion[banco]
