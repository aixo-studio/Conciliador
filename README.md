# Conciliación v4 — el cruce entre banco y sistema

Etapa 2 de la conciliación bancaria. Recibe, para cada cuenta, las dos tablas
que devuelve la etapa 1 ("conciliacion v3"): el extracto del banco y el libro
del sistema, como DataFrames de cinco columnas (Fecha, Código, Descripción,
Monto en centavos y Clase). Cruza los movimientos y escribe un Excel que dice,
fila por fila, qué cruzó y con qué. Sin IA: todo son reglas fijas en código.

Hoy hace una sola pasada: el **cruce exacto** (misma fecha y mismo monto). Las
pasadas siguientes están en PENDIENTES.md.

**Lo que falta para correr de punta a punta es la comunicación con v3**
(APR-235): llamar a `convertir_documento()` de v3 para conseguir las tablas, y
la terminal. Hasta entonces, este repo se verifica con sus pruebas, que usan
tablas inventadas.

## Cómo se usa

La primera vez, en la terminal, dentro de esta carpeta. Hace falta Python
3.12, el mismo que usa v3:

```
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

El repo se usa desde Python: quien consigue las dos tablas de una cuenta
(APR-235) llama a una sola función, que corre todo el proceso y escribe el
Excel:

```python
from cruzar_cuenta import cruzar_cuenta

resumen = cruzar_cuenta(tabla_banco, tabla_sistema, "cruce - BBVA 2026-09.xlsx")
```

Si algo no cumple el contrato o un control no cierra, frena con un
`ValueError` que dice qué y dónde, y no escribe nada.

Para correr las pruebas: `python -m pytest` (así usa el Python del `.venv`
aunque haya otro instalado).

## El Excel de salida

| Hoja | Qué tiene |
|---|---|
| Resumen | Por cada lado: filas y suma de la entrada, de lo cruzado, de lo sin cruzar y de los gastos bancarios |
| Banco | Todas las filas del extracto, en el mismo orden, con su estado |
| Sistema | Todas las filas del libro del sistema, en el mismo orden, con su estado |

Columnas de Banco: Fecha · Código · Descripción · Monto · Clase · Estado ·
Fila en Sistema. En Sistema es igual, con "Fila en Banco".

- **Clase**: lo que dijo v3 de la fila ("Movimiento" o "Gasto bancario").
  Nunca cambia: es la evidencia de origen.
- **Estado**: lo que hizo este repo con la fila: "Cruzado", "Sin cruzar" o
  "Gasto bancario".
- **Fila en Sistema / Fila en Banco**: en qué fila de la otra hoja de este
  mismo archivo está la pareja. El encabezado es la fila 1 y los datos
  empiezan en la 2, así que el número se busca tal cual.
- **Monto**: en pesos, con dos decimales (adentro del programa se cuenta en
  centavos enteros).

## Mapa de carpetas

```
cruzar_cuenta.py       la puerta de entrada: recibe las dos tablas de una cuenta,
                       corre cada paso y escribe el Excel
motor/                 los pasos del proceso, un archivo por paso
  recibir.py           1. controla la forma de cada tabla y le pone su Estado inicial
  cruce_exacto.py      2. cruza por misma fecha y mismo monto, solo filas "Sin cruzar"
  controlar.py         3. compara el resultado de cada tabla contra la recibida
  salida.py            4. controla lo que une a los dos lados y escribe el Excel
pruebas/               una prueba por paso y una de la corrida completa, con datos inventados
  datos.py             arma tablas inventadas con la forma del contrato
CLAUDE.md              cómo se trabaja en este repo y el contrato con v3
PENDIENTES.md          lo que falta decidir y hacer
```

## Mapa del flujo

El camino de una cuenta desde que alguien llama a
`cruzar_cuenta(tabla_banco, tabla_sistema, ruta)` hasta que sale el Excel.
Entre paréntesis, el archivo donde está cada función.

```
cruzar_cuenta()  (cruzar_cuenta.py)
│
├─► 1. recibir_documento()  (motor/recibir.py)      ← una vez por tabla
│      ├─ controlar_forma()   chequeo 1: las cinco columnas, al menos una fila
│      │                      y el tipo de dato de cada columna, fila por fila;
│      │                      las filas con errores se informan todas juntas
│      └─ poner_estado()      en una copia, el Estado inicial de cada fila:
│                             "Sin cruzar" o "Gasto bancario", según su Clase
│      La tabla recibida queda intacta (chequeo 2: la foto).
│
├─► 2. cruzar_exacto()  (motor/cruce_exacto.py)
│      Solo toma filas "Sin cruzar": agrupa el sistema por fecha y monto y
│      recorre el banco en orden; los repetidos se emparejan en orden. A cada
│      par le pone "Cruzado" y la fila de su pareja en la otra hoja.
│
├─► 3. controlar()  (motor/controlar.py)            ← una vez por tabla
│      El cierre contra la foto (chequeo 3): mismas filas, misma suma, cada
│      fila igual a la que llegó, y cada Estado válido y acorde a su Clase.
│      Devuelve el resumen (filas y suma por Estado).
│
├─► 4. controlar_lados()  (motor/salida.py)
│      Lo que une a los dos lados: lo cruzado suma lo mismo en el banco y en
│      el sistema, y las parejas se apuntan entre sí.
│
└─► 4. escribir_excel()  (motor/salida.py)
       Escribe las hojas Resumen, Banco y Sistema.

Si algo frena, no se escribe nada: el error dice qué regla falló y dónde.
```

## Decisiones

Qué se decidió, por qué, qué se descartó y dónde tiene límites. Sirve para
explicar y defender el sistema sin abrir el código.

### El cruce recibe las tablas de v3; no lee archivos
- **Qué es:** la entrada son los DataFrames que devuelve `convertir_documento()`
  de v3, de memoria a memoria. Este repo ya no lee los Excel que v3 escribía.
- **Por qué:** sin archivos en el medio no hay resultados viejos que se mezclen
  con nuevos ni decimales releídos de un Excel. Y el cruce no sabe nada de
  cada banco: los documentos ya llegan todos iguales.
- **Descartado:** leer los Excel de `v3/output` (era lo anterior) y un solo
  programa que lea crudos y cruce (mezcla dos problemas).
- **Límite:** este repo confía en que v3 hizo bien su trabajo: controla la
  forma de lo que llega, no que los movimientos sean los del extracto real.

### La segunda columna es "Código", no "Concepto"
- **Qué es:** en cada documento lleva el valor puro de la columna que el banco
  usa para identificar el tipo de movimiento: Codigo en BBVA, Grupo de
  Conceptos en Galicia, Concepto en Supervielle (en el sistema, Tipo de
  documento). El nombre es genérico para que sea igual en todos.
- **Por qué:** cada banco identifica sus gastos bancarios con esa columna, y
  con el valor puro la separación es comparar valores exactos.
- **Límite:** el texto del concepto del BBVA y del Galicia no llega (ej. el
  CUIT de una transferencia). Para revisar un "Sin cruzar" hay que ir al
  extracto original. Si un cruce futuro lo necesita, se pide a v3.
- **Resguardo:** el Código siempre llega como texto ("005" no es 5). Si llega
  como número, el programa frena.

### Este repo no sabe qué es un gasto bancario
- **Qué es:** qué códigos son gasto en cada banco lo decide v3, con la lista
  de su `configuracion.toml`; acá cada fila llega con su Clase puesta. En este
  repo no hay nada propio de un banco.
- **Por qué:** una sola lista no se puede desincronizar. Agregar un gasto o un
  banco nuevo es trabajo solo de v3; este repo no se toca.
- **Descartado:** una copia de la lista acá (`bancos.json`, APR-215/226).
- **Límite:** un gasto con un código que no está en la lista de v3 llega como
  "Movimiento" y se cruza como uno más.

### El control son tres chequeos por documento (APR-223)
- **Qué es:** dos al entrar y uno al final. 1) *La forma:* la tabla cumple el
  contrato. 2) *La foto:* la tabla recibida se guarda intacta; nada la
  modifica. 3) *El cierre:* después del cruce, el resultado se compara contra
  esa tabla.
- **Por qué acá y no en v3:** v3 ya controla su parte (lo armado contra el
  archivo original). Quien aparta los gastos del cruce es este repo, así que
  acá está el riesgo de perder una fila.
- **Por qué dos al entrar:** el primero frena antes de hacer nada si llega algo
  mal formado, con el motivo exacto. Sin él, una Clase mal escrita se vería
  recién al final, como "falta una fila".

### La forma se controla contra una copia propia del contrato
- **Qué es:** los nombres de las cinco columnas y de las dos clases están
  escritos en `motor/recibir.py`; no se toman del código de v3.
- **Por qué:** quien recibe controla contra lo que espera. Si se tomaran de v3
  y v3 cambiara un nombre por error, este repo lo aceptaría sin enterarse.
- **Qué se exige:** Fecha es una fecha; Código y Descripción son texto (pueden
  estar vacíos); Monto en centavos es un entero; Clase es "Movimiento" o
  "Gasto bancario", exacto. En el libro del sistema, todas "Movimiento".
- **Descartado:** aceptar un monto con decimales aunque sea redondo (100.0):
  reabre el problema del redondeo. Y revisar si un Código es gasto: es de v3.
- **Los errores se informan juntos:** todas las filas con errores en un solo
  mensaje (las primeras 20 y cuántas más hay), como en v3. En los errores, la
  fila 1 es el primer movimiento de la tabla.

### Los gastos bancarios no se separan: se marcan con el Estado
- **Qué es:** las filas no se mueven. Cada fila tiene un Estado: "Sin cruzar",
  "Cruzado" o "Gasto bancario". Las que llegan con Clase "Gasto bancario"
  arrancan (y quedan) con Estado "Gasto bancario".
- **Por qué:** si nada se mueve, nada se puede perder al separar. Es menos
  código y mantiene una sola tabla que cierra entera contra la entrada.
- **Clase y Estado son dos columnas:** la Clase dice qué es la fila (lo dijo
  v3) y nunca cambia; el Estado dice qué pasó con ella acá. Que la Clase quede
  intacta es lo que permite controlarla contra el Estado al final.
- **Descartado:** partir la tabla en dos (movimientos y gastos): habría filas
  que cambian de lugar y haría falta controlar que las partes sumen el todo.
- **Riesgo y resguardos:** que un cambio futuro haga que el cruce tome un
  gasto. Lo frenan tres cosas: el cruce solo toma filas "Sin cruzar"; una
  prueba que lo intenta a propósito (un gasto con pareja perfecta no cruza);
  y el control final, que frena si un gasto no termina como "Gasto bancario".

### El control del final compara contra la tabla tal como llegó
- **Qué es:** al final se compara el resultado contra la tabla recibida, en
  este orden, y frena en la primera regla que falla: misma cantidad de filas;
  misma suma; cada fila idéntica a la que llegó, en sus cinco columnas; cada
  Estado válido; Clase y Estado de gasto siempre juntos.
- **Por qué contra la tabla entera y no contra dos números:** contar y sumar
  no ve dos errores que se compensan, ni una Clase cambiada, ni filas en otro
  orden. Comparar fila por fila sí. Es el criterio de v3: contra el original,
  que nadie tocó.
- **Cada regla tiene su mensaje,** y el mensaje dice dónde mirar: un gasto
  "Cruzado" es un problema del cruce; una fila que falta, de un paso que
  perdió filas.
- **Además, entre los dos lados** (`controlar_lados`): lo cruzado suma lo
  mismo en el banco y en el sistema, y cada pareja se apunta con la otra.
- **Límite:** no ve un gasto que v3 no reconoció: llega como "Movimiento" y
  pasa. Y el tramo de v3 entre su propio control y la entrega de la tabla no
  lo verifica nadie (ver PENDIENTES.md).

### El cruce exacto exige misma fecha y mismo monto
- **Por qué:** es la regla más segura. Si dos movimientos tienen la misma
  fecha y el mismo monto al centavo, casi seguro son el mismo.
- **Descartado (por ahora):** fechas cercanas, sumas, diferencias de centavos.
  Cruzan más, pero con más riesgo de cruzar mal. Están en PENDIENTES.md y se
  suman de a una, decidiendo cada una.
- **Límite:** un movimiento que el banco registró el lunes y el sistema el
  viernes no cruza, aunque sea el mismo. Queda "Sin cruzar".

### Los montos se comparan en centavos enteros
- **Por qué:** las computadoras guardan los decimales con errores mínimos
  (1500000.25 puede leerse como 1500000.2499999). En centavos enteros no hay
  error posible. v3 ya los entrega así; se comparan y suman tal cual.
- **Descartado:** comparar con "casi igual" (una tolerancia). Abre la puerta a
  cruzar montos que en realidad son distintos.

### Los repetidos se emparejan en orden
- **Qué es:** si el mismo día hay 3 movimientos de $100 en el banco y 2 en el
  sistema, se cruza el 1.º con el 1.º, el 2.º con el 2.º, y el 3.º del banco
  queda "Sin cruzar".
- **Por qué:** como son idénticos en fecha y monto, cualquier emparejamiento
  da los mismos totales. En orden es lo más simple y siempre da lo mismo.
- **Límite:** si los conceptos de esos repetidos son distintos, la pareja
  puede no ser la "real". Para la conciliación del saldo no cambia nada, pero
  quien revise fila por fila puede verlo.

### Cómo se busca la pareja (la estructura de datos)
- **Qué se hace:** las filas del sistema que esperan pareja se agrupan por
  (fecha, monto), cada grupo una fila de espera en el orden del archivo. Cada
  fila del banco va directo a su grupo y toma la primera que espera.
- **Por qué:** es rápido (no compara cada fila contra todas) y respeta el
  orden, que es lo que empareja a los repetidos en orden.
- **Descartado:** comparar todas contra todas. Funciona, pero es más lento y
  hay que cuidar a mano no usar dos veces la misma fila.

### Ante cualquier cosa rara, frena en vez de seguir
- **Qué es:** una columna que falta o sobra, una fecha que no es fecha, un
  monto con decimales, una Clase desconocida, un gasto en el libro del
  sistema, un control que no cierra: se frena con el motivo y no se escribe
  nada.
- **Por qué:** es una conciliación: una fila salteada en silencio es plata que
  desaparece del control. Mejor que no salga nada a que salga algo incompleto
  que parezca correcto.
- **Nota:** borrar el resultado viejo de una corrida anterior cuando una nueva
  falla lo hacía la terminal; queda para APR-235.

### Una hoja por lado, con todas las filas y su estado
- **Por qué:** cada hoja tiene exactamente las filas de la entrada, en el
  mismo orden. Así es imposible que una fila se pierda, y las pasadas que
  vengan solo cambian el estado de las "Sin cruzar".
- **Descartado:** una hoja de pares (banco | sistema uno al lado del otro).
  Se lee fácil, pero una suma junta 1 fila con 2 o 3, y eso no entra en pares.

### La hoja muestra la Clase y el Estado por separado
- **Qué es:** siete columnas. La Clase es la entrada (lo que dijo v3); el
  Estado es el resultado (lo que hizo este repo).
- **Por qué:** quien revisa puede verificar a ojo que coinciden — la misma
  idea del control, pero visible — y "¿por qué esta fila no cruzó?" se
  contesta en la misma fila.
- **Descartado:** mostrar solo el Estado. Hoja más limpia, pero sin la
  evidencia de origen.
- **Límite:** en los gastos las dos columnas repiten el mismo texto.

### Cada fila cruzada dice la fila de su pareja, en este mismo archivo
- **Qué es:** "Fila en Sistema" (en la hoja Banco) y "Fila en Banco" (en la
  hoja Sistema): la fila de la pareja en la otra hoja de este mismo Excel. El
  encabezado es la fila 1 y los datos empiezan en la 2, así que el número se
  busca tal cual.
- **Por qué:** v3 ya no escribe archivos, así que el único lugar donde mirar
  las filas es este Excel. El archivo se corrobora solo, sin depender de nada
  externo.
- **Descartado:** un número de cruce (no sirve para ir a buscar la pareja) y
  numerar desde 1 por la posición en la tabla (quien busca en el Excel caería
  una fila arriba, corrido por el encabezado).
- **Nota:** los mensajes de error del programa cuentan "fila 1 = primer
  movimiento". Son audiencias distintas: el error lo lee quien programa; el
  Excel, quien concilia.

### La columna Criterio se sacó
- **Por qué:** había un solo criterio ("Exacto"), así que decía lo mismo en
  todas las filas cruzadas. Vuelve cuando exista una segunda pasada y haya
  algo que distinguir (decidido el 2026-11-10).

### pandas es una dependencia
- **Por qué:** la tabla que devuelve v3 es un DataFrame de pandas. Trabajar
  sobre esa misma tabla evita convertirla a otra estructura, que sería un
  paso más donde perder filas.
- **Límite:** una dependencia más. Su versión está fija en `requirements.txt`,
  la misma que usa v3.

### Dónde falla o puede fallar hoy
- **No corre de punta a punta:** conseguir las tablas (llamar a v3) y la
  terminal son APR-235. Hasta entonces, todo está probado con tablas
  inventadas y la referencia de septiembre está sin verificar en esta versión.
- **Un gasto que v3 no reconoció** llega como "Movimiento" y se cruza como
  uno más, sin aviso.
- **Controles de mes:** una fila con fecha de otro mes se cruza igual. Está en
  PENDIENTES.md.
- **El tramo final de v3** (entre su control y la entrega de la tabla) no lo
  verifica nadie. Está en PENDIENTES.md, para hablar con Luciano.
