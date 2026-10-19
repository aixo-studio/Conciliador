# Conciliación v4 — el cruce entre banco y sistema

Etapa 2 de la conciliación bancaria. Toma, para cada banco, los dos archivos
que deja la etapa 1 ("conciliacion v3"): el extracto del banco y el libro del
sistema, ya en cuatro columnas (Fecha, Concepto, Descripción, Monto). Los cruza
y deja un Excel que dice, fila por fila, qué cruzó y con qué. Sin IA: todo son
reglas fijas en código.

Hoy hace una sola pasada: el **cruce exacto** (misma fecha y mismo monto). Las
pasadas siguientes están en PENDIENTES.md.

## Dónde están los datos

Fuera de los repos, en una carpeta al lado:

```
Documents/
  conciliacion v3/                    repo de la etapa 1
  conciliacion v4/                    este repo
  conciliacion resultados/
    v3/output/<AAAA-MM>/<Banco>/      la entrada: un archivo del banco y uno del sistema
    v4/output/<AAAA-MM>/<Banco>/      lo que escribe este repo
```

## Cómo se usa

La primera vez, en la terminal, dentro de esta carpeta:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Después, cada vez:

```
source .venv/bin/activate
python cruzar.py 2026-09            todos los bancos del mes
python cruzar.py 2026-09 BBVA       un banco
```

Por cada banco queda `v4/output/<mes>/<Banco>/cruce - <Banco> <mes>.xlsx`. En
pantalla sale lo que entró de cada lado (filas, suma y fechas) y cuánto cruzó.
Si algo no cumple, ese banco no se escribe, se borra su resultado anterior y
se dice por qué; los demás siguen.

Para correr las pruebas: `pytest`

## El Excel de salida

| Hoja | Qué tiene |
|---|---|
| Resumen | Por cada lado: filas y suma de la entrada, de lo cruzado y de lo sin cruzar |
| Banco | Todas las filas del extracto, en el mismo orden, con su estado |
| Sistema | Todas las filas del libro del sistema, en el mismo orden, con su estado |

Columnas de Banco y Sistema: Fecha · Concepto · Descripción · Monto · Estado ·
N° de cruce · Criterio.

- **Estado**: "Cruzado" o "Sin cruzar".
- **N° de cruce**: une las filas que cruzaron entre sí. El cruce 12 del banco
  es el cruce 12 del sistema.
- **Criterio**: cómo se cruzó. Hoy siempre "Exacto".

## Mapa de carpetas

```
cruzar.py              la puerta de entrada: lo que se corre en la terminal
motor/                 los pasos del proceso, un archivo por paso
  entrada.py           1. encuentra los 2 archivos, controla el contrato y los lee
  cruce_exacto.py      2. cruza por misma fecha y mismo monto
  salida.py            3. controla que no se perdió nada y escribe el Excel
pruebas/               una prueba por paso, con datos inventados
  datos.py             ayudas para armar archivos inventados
CLAUDE.md              cómo se trabaja en este repo
PENDIENTES.md          lo que falta decidir y hacer
```

## Mapa del flujo

El camino de un banco desde que se corre `python cruzar.py 2026-09` hasta que
sale el Excel. Entre paréntesis, el archivo donde está cada función.

```
main()  (cruzar.py)
│  Lee lo que escribiste en la terminal: el mes y, si lo pusiste, el banco.
│  Busca las carpetas de banco del mes en v3/output.
│
└─► cruzar_banco()  (cruzar.py)            ← una vez por cada banco
    │
    ├─► 1. encontrar_archivos()  (motor/entrada.py)
    │      Busca el archivo "banco_..." y el "sistema_...". Tiene que haber uno
    │      de cada uno; si no, frena.
    │      └─ es_excel()           deja solo los .xlsx (saltea ocultos y temporales)
    │
    ├─► 1. leer_movimientos()  (motor/entrada.py)   ← una vez por cada archivo
    │      Controla que tenga una sola hoja "Movimientos" y el encabezado exacto.
    │      Lee fila por fila y arma un Movimiento por fila, "Sin cruzar".
    │      ├─ esta_vacia()         una fila vacía o con datos de más frena
    │      └─ a_centavos()         pasa el Monto a centavos enteros, redondeando
    │      └─► resumir()           filas, suma y fechas, para mostrar en pantalla
    │
    ├─► 2. cruzar_exacto()  (motor/cruce_exacto.py)
    │      Agrupa las filas del sistema por fecha y monto. Recorre el banco en
    │      orden: cada fila toma la primera del sistema con la misma fecha y el
    │      mismo monto que todavía no se usó. A las dos les pone "Cruzado", el
    │      mismo N° de cruce y el criterio "Exacto".
    │
    ├─► 3. controlar()  (motor/salida.py)
    │      En cada lado, cruzado + sin cruzar tiene que dar la entrada (filas y
    │      suma); lo cruzado tiene que sumar igual en los dos lados; cada N° de
    │      cruce tiene que estar una vez en cada lado. Si no, frena.
    │      └─ contar()             filas y suma de la entrada, lo cruzado y lo sin cruzar
    │
    └─► 3. escribir_excel()  (motor/salida.py)
           Escribe las hojas Resumen, Banco y Sistema.
           └─ escribir_hoja()      arma cada hoja con su formato

Si algo frena, cruzar_banco() no escribe, borra el resultado anterior de ese
banco y lo informa. Al final, main() muestra cuántos bancos se cruzaron.
```
