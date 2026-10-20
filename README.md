# Conciliación v4 — el cruce entre banco y sistema

Etapa 2 de la conciliación bancaria. Toma, para cada banco, los dos archivos
que deja la etapa 1 ("conciliacion v3"): el extracto del banco y el libro del
sistema, ya en cuatro columnas (Fecha, Código, Descripción, Monto). Los cruza
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

Columnas de Banco: Fecha · Código · Descripción · Monto · Estado · Fila en
Sistema · Criterio. En Sistema es igual, con "Fila en Banco".

- **Estado**: "Cruzado" o "Sin cruzar".
- **Fila en Sistema / Fila en Banco**: en qué fila del otro documento está la
  pareja. Si la fila 41 del banco dice 512, la fila 512 del sistema dice 41. Si
  cruzó con varias filas (pasada de sumas, a futuro), dice "41, 42, 43".
- **Criterio**: cómo se cruzó. Hoy siempre "Exacto".

Los números de fila son los del output de v3, que tiene exactamente las mismas
filas que estas hojas: la fila 512 de la hoja Sistema es la fila 512 de
`sistema_... .xlsx` en `v3/output`. Así se puede corroborar cada cruce en v3.

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
    │      criterio "Exacto" y, a cada una, la fila de su pareja.
    │
    ├─► 3. controlar()  (motor/salida.py)
    │      En cada lado, cruzado + sin cruzar tiene que dar la entrada (filas y
    │      suma); lo cruzado tiene que sumar igual en los dos lados; las parejas
    │      se tienen que apuntar entre sí. Si no, frena.
    │      ├─ contar()             filas y suma de la entrada, lo cruzado y lo sin cruzar
    │      └─ controlar_parejas()  si la 41 del banco dice 512, la 512 del sistema dice 41
    │
    └─► 3. escribir_excel()  (motor/salida.py)
           Escribe las hojas Resumen, Banco y Sistema.
           ├─ mostrar_filas()      la fila de la pareja: 512, o "41, 42, 43" si son varias
           └─ escribir_hoja()      arma cada hoja con su formato

Si algo frena, cruzar_banco() no escribe, borra el resultado anterior de ese
banco y lo informa. Al final, main() muestra cuántos bancos se cruzaron.
```

## Decisiones

Qué se decidió, por qué, qué se descartó y dónde tiene límites. Sirve para
explicar y defender el sistema sin abrir el código.

### El cruce lee el output de v3, no los extractos crudos
- **Por qué:** cada banco entrega su extracto distinto. La etapa 1 ya los deja
  todos iguales (4 columnas, una hoja), así que el cruce no tiene que saber
  nada de cada banco. Si mañana entra otro banco, se toca v3 y este repo no.
- **Descartado:** un solo programa que lea crudos y cruce. Mezcla dos
  problemas y un cambio en un banco puede romper el cruce.
- **Límite:** este repo confía en que v3 hizo bien su trabajo. Controla la
  forma de los archivos (hoja, encabezado, tipos de dato), no que los
  movimientos sean los del extracto real.

### La segunda columna es "Código", no "Concepto"
- **Qué es:** en cada documento lleva el valor puro de la columna que el banco
  usa para identificar el tipo de movimiento: Codigo en BBVA, Grupo de
  Conceptos en Galicia, Concepto en Supervielle (en el sistema, Tipo de
  documento). El nombre es genérico para que el encabezado sea igual en todos.
- **Por qué:** cada banco identifica sus gastos bancarios con una columna
  distinta, y con esa sola columna alcanza (verificado con septiembre). Con el
  valor puro, la separación de gastos es comparar valores exactos.
- **Descartado:** mezclar código y texto en la misma celda ("236 - IVA TASA
  GRA"), o agregar una quinta columna.
- **Límite:** el texto del concepto del BBVA y del Galicia ya no llega (ej. el
  CUIT de una transferencia). Para revisar un "Sin cruzar" hay que ir al
  extracto original. Si un cruce futuro lo necesita, se pide a v3.
- **Resguardo:** el Código siempre llega como texto ("005" no es 5). Si llega
  como número, el programa frena, porque ya no coincidiría con las listas.

### El cruce exacto exige misma fecha y mismo monto
- **Por qué:** es la regla más segura. Si dos movimientos tienen la misma
  fecha y el mismo monto al centavo, casi seguro son el mismo.
- **Descartado (por ahora):** fechas cercanas, sumas, diferencias de
  centavos. Cruzan más, pero con más riesgo de cruzar mal. Están en
  PENDIENTES.md y se suman de a una, decidiendo cada una.
- **Límite:** un movimiento que el banco registró el lunes y el sistema el
  viernes no cruza, aunque sea el mismo. Queda "Sin cruzar".

### Los montos se comparan en centavos enteros
- **Por qué:** las computadoras guardan los decimales con errores mínimos
  (1500000.25 puede leerse como 1500000.2499999). Comparados así, dos montos
  iguales podrían parecer distintos. En centavos enteros (150000025) no hay
  error posible.
- **Descartado:** comparar con "casi igual" (una tolerancia). Abre la puerta a
  cruzar montos que en realidad son distintos.

### Los repetidos se emparejan en orden
- **Qué es:** si el mismo día hay, por ejemplo, 3 movimientos de $100 en el
  banco y 2 en el sistema, se cruza el 1.º con el 1.º, el 2.º con el 2.º, y
  el 3.º del banco queda "Sin cruzar".
- **Por qué:** como son idénticos en fecha y monto, cualquier emparejamiento
  da los mismos totales. Hacerlo en orden es lo más simple y siempre da el
  mismo resultado.
- **Límite:** si los conceptos de esos repetidos son distintos, la pareja
  puede no ser la "real" (el pago a A cruzado con el registro del pago a B
  por el mismo monto). Para la conciliación del saldo no cambia nada, pero
  quien revise fila por fila puede verlo.

### Cómo se busca la pareja (la estructura de datos)
- **Qué se hace:** las filas del sistema se agrupan por (fecha, monto) en una
  fila de espera cada grupo, en el orden del archivo. Cada fila del banco va
  directo a su grupo y toma la primera que espera.
- **Por qué:** es rápido (no compara cada fila del banco contra todas las del
  sistema) y respeta el orden, que es lo que hace que los repetidos se
  emparejen en orden.
- **Descartado:** comparar todas contra todas. Funciona, pero es más lento y
  hay que cuidar a mano no usar dos veces la misma fila.

### Ante cualquier cosa rara, frena en vez de seguir
- **Qué es:** si falta un archivo, sobra uno, la hoja no se llama
  "Movimientos", el encabezado no es exacto, hay una fila vacía, una fecha que
  no es fecha o un monto que no es número, ese banco no se cruza y se dice
  qué archivo, qué fila y por qué.
- **Por qué:** es una conciliación: una fila salteada en silencio es plata que
  desaparece del control. Es preferible que no salga nada a que salga algo
  incompleto que parezca correcto.
- **Descartado:** saltear filas vacías o "arreglar" datos raros. Es cómodo,
  pero esconde errores.
- **Además:** si un banco falla, se borra su resultado anterior, para que
  nadie use uno viejo creyendo que es el de esta corrida.

### Una hoja por lado, con todas las filas y su estado
- **Por qué:** cada hoja tiene exactamente las filas de la entrada, en el
  mismo orden. Así es imposible que una fila se pierda, y las pasadas que
  vengan (sumas, gastos) solo cambian el estado de las "Sin cruzar".
- **Descartado:** una hoja de pares (banco | sistema uno al lado del otro).
  Se lee fácil, pero una suma junta 1 fila con 2 o 3, y eso no entra en pares.

### Cada fila cruzada dice la fila de su pareja
- **Qué es:** "Fila en Sistema" (en la hoja Banco) y "Fila en Banco" (en la
  hoja Sistema). Los números son los del output de v3, que tiene las mismas
  filas que estas hojas.
- **Por qué:** permite corroborar cada cruce yendo directo a la fila del otro
  documento, en v4 o en v3.
- **Descartado:** un número de cruce (1, 2, 3…). Une las dos filas, pero no
  sirve para ir a buscar la pareja.
- **Límite:** los números valen mientras el output de v3 no cambie. Si se
  vuelve a correr v3 con otros archivos, hay que volver a correr este repo.

### Los controles antes de escribir
- **Qué se controla:** en cada lado, cruzado + sin cruzar = entrada (filas y
  suma); lo cruzado suma igual en los dos lados; cada pareja se apunta entre
  sí. La hoja Resumen muestra esos números para revisarlos sin correr nada.
- **Por qué:** si el código tuviera un error, el control lo frena antes de
  entregar un resultado equivocado.

### Dónde falla o puede fallar hoy
- **Archivo de otro banco u otro mes en la carpeta:** se reconoce el banco y
  el sistema solo por el principio del nombre ("banco_" y "sistema_"). No se
  controla que el extracto sea del banco de la carpeta ni que las fechas sean
  del mes. Se ve en pantalla (el rango de fechas y el nombre del archivo),
  pero no frena. Está en PENDIENTES.md (controles de mes).
- **Alguien edita a mano el output de v3:** si respeta la forma (hoja,
  encabezado, tipos), este repo lo acepta. El resguardo es que v3 se puede
  volver a correr desde los originales y dar el mismo resultado.
- **Movimientos que no cruzan por regla:** fechas desfasadas, pagos partidos,
  gastos bancarios. Hoy quedan todos "Sin cruzar"; es esperable, no un error.

