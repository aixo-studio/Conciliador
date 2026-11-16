"""La puerta de entrada: cruza una cuenta, el extracto del banco contra el
libro del ERP.

Recibe las dos tablas tal como las devuelve la etapa 1 ("conciliacion v3"),
corre cada paso y devuelve lo que cruzó y lo que quedó pendiente de cada lado.

Conseguir las tablas (llamando a la etapa 1) es la comunicación entre los dos
repos (APR-235). El Excel de salida se define cuando exista la segunda pasada
del cruce; hasta entonces, el resultado son las tres tablas (ver PENDIENTES.md).
"""
import pandas

from motor.controlar import validar_y_resumir_cruce
from motor.cruce_exacto import cruzar_exacto
from motor.recibir import validar_tabla_de_entrada


def cruzar_cuenta(tabla_banco: pandas.DataFrame, tabla_erp: pandas.DataFrame) -> tuple:
    """Recibe las dos tablas de una cuenta.
    Valida que cumplan el contrato, hace el cruce exacto y controla que no se
    haya perdido nada. Devuelve cuatro cosas: la tabla de cruces, el banco
    pendiente, el ERP pendiente y el resumen. Si algo no cumple o no cierra,
    frena con un error que dice por qué y no devuelve nada.
    """
    validar_tabla_de_entrada(tabla_banco, es_sistema=False)
    validar_tabla_de_entrada(tabla_erp, es_sistema=True)
    cruces, banco_pendiente, erp_pendiente = cruzar_exacto(tabla_banco, tabla_erp)
    resumen = validar_y_resumir_cruce(cruces, banco_pendiente, erp_pendiente,
                                      tabla_banco, tabla_erp)
    return cruces, banco_pendiente, erp_pendiente, resumen
