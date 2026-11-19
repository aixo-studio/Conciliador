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

**Conciliar una cuenta** (las dos etapas, de punta a punta). Recibe el banco, el extracto y el libro del ERP de esa cuenta, muestra el resumen de cada lado y no guarda nada:

```bash
python conciliar.py BBVA "ruta/extracto.xls" "ruta/libro.xlsx"
```

**Guardar el resultado para revisarlo.** Con `--csv`, además escribe en esa carpeta `cruces.csv`, `banco_pendiente.csv`, `erp_pendiente.csv` y `resumen.csv`, que se abren directo en Excel. Si la carpeta ya los tenía, los reemplaza:

```bash
python conciliar.py BBVA "ruta/extracto.xls" "ruta/libro.xlsx" --csv "ruta/carpeta"
```

**Probar un documento solo** (etapa 1). Muestra su resumen y no guarda nada:

```bash
python -m preconciliacion.convertir BBVA "ruta/extracto.xls"
python -m preconciliacion.convertir BBVA "ruta/libro.xlsx" --erp
```

**Desde Python:**

```python
from conciliar import conciliar

cruces, banco_pendiente, erp_pendiente, resumen = conciliar("BBVA", "ruta/extracto.xls", "ruta/libro.xlsx")
```

Si un archivo no se puede convertir o algo no cierra, frena con un error que dice por qué y en qué parte (el extracto, el libro del ERP o el cruce), y no devuelve nada a medias.

## Estructura

```
conciliar.py         la puerta de entrada: concilia una cuenta de punta a punta
preconciliacion/     etapa 1: limpia cada documento
conciliador/         etapa 2: cruza las dos tablas de una cuenta
pruebas/             la prueba del recorrido completo, con archivos inventados
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

Los archivos de los clientes nunca se suben al repo: se guardan afuera y se le pasa al programa la ruta de cada uno. El programa nunca modifica un original. Solo escribe archivos si se pide con `--csv`; como tienen datos del cliente, conviene guardarlos fuera del repo (igual, git ignora los `*.csv`).

## Decisiones

Las de cada etapa están en su README. Estas son las de todo el sistema.

**1. Las dos etapas en un solo repo** (2026-11-19). Antes eran dos repos (Pre-procesamiento-bancario- y Conciliador). Se unieron porque la etapa 1 va a cambiar seguido (códigos de gasto y bancos nuevos) y, con dos repos, la etapa 2 podía quedar usando una versión vieja sin aviso. Se descartó instalar la etapa 1 como paquete en la etapa 2: tiene el mismo riesgo de versiones desfasadas. Límite: la etapa 1 ya no se puede usar sola sin separarla; la frontera entre etapas es una regla (la etapa 1 nunca usa nada de la etapa 2), no un repo. La historia de los dos repos quedó en este.

**2. La etapa 2 controla lo que recibe con su propia copia del contrato.** Aunque estén en el mismo repo, la etapa 2 no toma las columnas ni las clases de la etapa 1: las tiene escritas aparte. Así, si la etapa 1 cambia algo por error, la etapa 2 frena en vez de cruzar datos mal armados. Límite: si el contrato cambia a propósito, hay que cambiarlo en las dos etapas en el mismo commit.

**3. Un solo archivo conoce a las dos etapas: `conciliar.py`, en la raíz** (2026-11-19). Llama a la etapa 1 una vez por archivo y le pasa las dos tablas a la etapa 2. Así ninguna etapa depende de la otra y cada una se sigue probando sola. Se descartó que la etapa 2 llamara directo a la etapa 1: rompería la frontera y sus pruebas necesitarían archivos Excel. Si algo falla, el error dice en qué parte. Tiene una función (`conciliar`) para otros programas y la terminal para usarlo a mano, como `convertir.py`. Límite: el resultado solo se guarda si se pide (ver la decisión 4).

**4. El resultado se guarda en CSV, y solo si se pide** (2026-11-19). Con `--csv`, `conciliar.py` escribe las tres tablas y el resumen en cuatro CSV, para revisarlos en Excel. Los escribe `conciliador/motor/salida.py` con lo que devuelve `cruzar_cuenta()`, ya controlado, y con todas las columnas que traiga cada tabla, así una pasada nueva del cruce no obliga a cambiarlo. Se eligió CSV y no un Excel con cuatro hojas porque es el formato más simple y cualquier programa lo lee. Se descartó que `cruzar_cuenta()` escribiera los archivos: la etapa 2 dejaría de poder probarse sin archivos. El monto va solo en centavos, como en el contrato. Límites: es una salida para revisar, no la entrega final al cliente; si la carpeta ya tenía esos CSV, los reemplaza.
