"""Puerta de entrada: cruza el extracto de cada banco con el libro del sistema.

Uso:
    python cruzar.py 2026-09            todos los bancos del mes
    python cruzar.py 2026-09 BBVA       un banco

Lee de  conciliacion resultados/v3/output/<mes>/<Banco>/   (lo que deja la etapa 1)
y deja  conciliacion resultados/v4/output/<mes>/<Banco>/cruce - <Banco> <mes>.xlsx
Cada banco se cruza por separado: si uno falla, los demás siguen.
"""
import re
import sys
from pathlib import Path

from motor.cruce_exacto import cruzar_exacto
from motor.entrada import CRUZADO, ENTRADA, SALIDA, SIN_CRUZAR, encontrar_archivos, leer_movimientos, resumir
from motor.salida import controlar, escribir_excel


def pesos(centavos: int) -> str:
    """Recibe un importe en centavos. Lo devuelve como texto en formato argentino: 1.234.567,89"""
    return f"{centavos / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def numero(cantidad: int) -> str:
    """Recibe una cantidad. La devuelve con punto de miles: 1.445"""
    return f"{cantidad:,}".replace(",", ".")


def cruzar_banco(carpeta_entrada: Path, carpeta_salida: Path, mes: str) -> bool:
    """Recibe la carpeta de un banco en la entrada, su carpeta de salida y el mes.
    Lee los dos archivos, los cruza, controla y escribe el Excel, mostrando el
    resumen. Devuelve True si salió bien. Si algo falla, no escribe nada, borra
    el resultado anterior (si había) y dice por qué.
    """
    banco = carpeta_entrada.name
    ruta = carpeta_salida / f"cruce - {banco} {mes}.xlsx"
    print(f"  {banco}")
    try:
        # Paso 1: leer la entrada y mostrar qué entró de cada lado.
        archivo_banco, archivo_sistema = encontrar_archivos(carpeta_entrada)
        lados = {}
        for lado, archivo in (("banco", archivo_banco), ("sistema", archivo_sistema)):
            try:
                lados[lado] = leer_movimientos(archivo)
            except ValueError as error:
                raise ValueError(f"{archivo.name}: {error}") from None
            resumen = resumir(lados[lado])
            print(f"    {lado:<8} {numero(resumen['filas']):>6} filas  {pesos(resumen['suma']):>18}   "
                  f"{resumen['desde']:%d/%m/%Y} → {resumen['hasta']:%d/%m/%Y}   {archivo.name}")
        # Paso 2: el cruce exacto.
        cruces = cruzar_exacto(lados["banco"], lados["sistema"])
        # Paso 3: controlar y escribir.
        conteos = controlar(lados["banco"], lados["sistema"])
    except ValueError as error:
        print(f"    ✗ No se cruzó: {error}")
        # Así nunca queda un resultado viejo que parezca el de esta corrida.
        if ruta.exists():
            ruta.unlink()
            print(f"      Se borró el resultado anterior: {ruta.name}")
        return False
    print(f"    cruce exacto: {numero(cruces)} cruces")
    for lado, conteo in conteos.items():
        print(f"    {lado.lower():<8} cruzado {numero(conteo[CRUZADO][0]):>6}   "
              f"sin cruzar {numero(conteo[SIN_CRUZAR][0]):>6}")
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    escribir_excel(lados["banco"], lados["sistema"], conteos, ruta)
    print(f"    ✓ {ruta.name}")
    return True


def main() -> None:
    """Recibe desde la terminal el mes y, opcionalmente, el banco.
    Cruza lo pedido y muestra el resumen. Si hubo errores, termina con error.
    """
    argumentos = sys.argv[1:]
    if not 1 <= len(argumentos) <= 2 or not re.fullmatch(r"\d{4}-\d{2}", argumentos[0]):
        sys.exit(__doc__)
    mes = argumentos[0]
    entrada_mes = ENTRADA / mes
    if not entrada_mes.is_dir():
        sys.exit(f"No existe la carpeta {entrada_mes}")
    # Qué bancos cruzar: el indicado o todas las carpetas del mes.
    if len(argumentos) == 2:
        carpetas = [entrada_mes / argumentos[1]]
        if not carpetas[0].is_dir():
            sys.exit(f"No existe la carpeta {carpetas[0]}")
    else:
        carpetas = sorted(carpeta for carpeta in entrada_mes.iterdir() if carpeta.is_dir())
    print(mes)
    errores = 0
    for carpeta in carpetas:
        if not cruzar_banco(carpeta, SALIDA / mes / carpeta.name, mes):
            errores += 1
    print(f"\n{len(carpetas) - errores} banco{'s' if len(carpetas) - errores != 1 else ''} cruzado"
          f"{'s' if len(carpetas) - errores != 1 else ''}, {errores} con error.")
    if errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
