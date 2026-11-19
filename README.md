# Conciliador

Conciliación bancaria sin IA: cruza el extracto de un banco con el libro del sistema financiero (el ERP) de esa cuenta, para el mismo mes. Todo lo deciden reglas fijas.

Trabaja en dos etapas, cada una en su carpeta:

| Etapa | Carpeta | Qué hace |
|---|---|---|
| 1. Preconciliación | [`preconciliacion/`](preconciliacion/README.md) | Recibe un documento crudo (el extracto del banco o el libro del ERP) y lo devuelve limpio, como una tabla de cinco columnas. Marca cuáles filas son gastos bancarios. |
| 2. Conciliador | [`conciliador/`](conciliador/README.md) | Recibe las dos tablas de una cuenta y cruza los movimientos con la misma fecha y el mismo monto. Devuelve lo que cruzó y lo que quedó pendiente de cada lado. |

Bancos configurados: BBVA, Galicia y Supervielle.

## Requisitos

- Python 3.12
- macOS o Linux

## Instalación

```bash
git clone https://github.com/aixo-studio/Conciliador.git
cd Conciliador
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Cada vez que se abre una terminal nueva, se activa el entorno desde la raíz del repo:

```bash
source .venv/bin/activate
```

## Uso

Todos los comandos se corren desde la raíz del repo.

**Probar un documento** (etapa 1). Muestra el resumen y no guarda nada:

```bash
python -m preconciliacion.convertir BBVA "ruta/extracto.xls"
python -m preconciliacion.convertir BBVA "ruta/libro.xlsx" --erp
```

**Cruzar una cuenta** (etapas 1 y 2), desde Python:

```python
from pathlib import Path

from preconciliacion.convertir import convertir_documento
from conciliador.cruzar_cuenta import cruzar_cuenta

tabla_banco = convertir_documento(Path("ruta/extracto.xls"), "BBVA", es_erp=False)
tabla_erp = convertir_documento(Path("ruta/libro.xlsx"), "BBVA", es_erp=True)
cruces, banco_pendiente, erp_pendiente, resumen = cruzar_cuenta(tabla_banco, tabla_erp)
```

Si un archivo no se puede convertir o algo no cierra, frena con un error que dice por qué y no devuelve nada a medias.

Un comando que corra las dos etapas de punta a punta (`conciliar.py`) está en construcción.

## Estructura

```
preconciliacion/     etapa 1: limpia cada documento
conciliador/         etapa 2: cruza las dos tablas de una cuenta
CLAUDE.md            cómo se trabaja en el repo y el contrato entre las dos etapas
PENDIENTES.md        lo abierto y lo hecho
pytest.ini           corre las pruebas de las dos etapas
requirements.txt     las librerías: pandas, openpyxl, xlrd y pytest
```

## Pruebas

Las pruebas usan datos inventados.

```bash
python -m pytest
```

## Datos reales

Los archivos de los clientes nunca se suben al repo: se guardan afuera y se le pasa al programa la ruta de cada uno. El programa nunca modifica un original y no escribe ningún archivo.

## Decisiones

Las de cada etapa están en su README. Estas son las de todo el sistema.

**1. Las dos etapas en un solo repo** (2026-11-19). Antes eran dos repos (Pre-procesamiento-bancario- y Conciliador). Se unieron porque la etapa 1 va a cambiar seguido (códigos de gasto y bancos nuevos) y, con dos repos, la etapa 2 podía quedar usando una versión vieja sin aviso. Se descartó instalar la etapa 1 como paquete en la etapa 2: tiene el mismo riesgo de versiones desfasadas. Límite: la etapa 1 ya no se puede usar sola sin separarla; la frontera entre etapas es una regla (la etapa 1 nunca usa nada de la etapa 2), no un repo. La historia de los dos repos quedó en este.

**2. La etapa 2 controla lo que recibe con su propia copia del contrato.** Aunque estén en el mismo repo, la etapa 2 no toma las columnas ni las clases de la etapa 1: las tiene escritas aparte. Así, si la etapa 1 cambia algo por error, la etapa 2 frena en vez de cruzar datos mal armados. Límite: si el contrato cambia a propósito, hay que cambiarlo en las dos etapas en el mismo commit.
