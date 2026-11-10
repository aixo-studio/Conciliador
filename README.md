# Conciliación v4 — el cruce entre banco y sistema

Etapa 2 de la conciliación bancaria. Toma, para cada banco, los dos archivos
que deja la etapa 1 ("conciliacion v3"): el extracto del banco y el libro del
sistema, ya en cuatro columnas (Fecha, Código, Descripción, Monto). Los cruza
y deja un Excel que dice, fila por fila, qué cruzó y con qué. Sin IA: todo son
reglas fijas en código.

Hoy hace una sola pasada: el **cruce exacto** (misma fecha y mismo monto). Las
pasadas siguientes están en PENDIENTES.md.

**En curso: pasar al contrato nuevo de v3.** Desde el 2026-11-04 v3 ya no
escribe esos Excel: devuelve una tabla (un DataFrame) con cinco columnas, la
quinta es la Clase ("Movimiento" o "Gasto bancario"). Este repo todavía lee
los Excel. Lo primero que se hizo para el contrato nuevo es el control
(APR-223): está construido y probado, pero **todavía no está conectado** al
programa. Se conecta cuando el cruce pase a trabajar con la tabla (APR-214).
En este README, lo que es del contrato nuevo está marcado como "sin conectar".

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

La primera vez, en la terminal, dentro de esta carpeta. Hace falta Python
3.12, el mismo que usa v3:

```
python3.12 -m venv .venv
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

Para correr las pruebas: `python -m pytest` (así usa el Python del `.venv`
aunque haya otro instalado).

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
  recibir.py           (sin conectar) controla la forma de la tabla que llega de v3
                       y le pone el Estado inicial a cada fila
  controlar.py         (sin conectar) después del cruce, compara el resultado
                       contra la tabla tal como llegó
pruebas/               una prueba por paso, con datos inventados
  datos.py             ayudas para armar archivos y tablas inventados
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

**Sin conectar todavía (contrato nuevo, APR-223).** Así va a quedar el camino
de cada documento cuando se conecte en APR-214:

```
la tabla que devuelve v3 (una del banco y una del sistema)
│
├─► controlar_forma()  (motor/recibir.py)        chequeo 1
│      Las cinco columnas, al menos una fila y el tipo de dato de cada
│      columna, fila por fila. Si hay filas mal, las informa todas juntas.
│      └─ problema_de_la_fila()   qué tiene mal una fila (lo primero que encuentra)
│
├─► la tabla recibida se guarda intacta          chequeo 2 (la foto)
│
├─► poner_estado()  (motor/recibir.py)
│      En una copia, agrega la columna Estado: "Sin cruzar" a los
│      movimientos y "Gasto bancario" a los gastos bancarios.
│
├─► el cruce: solo toca las filas "Sin cruzar"   (APR-214)
│
└─► controlar()  (motor/controlar.py)            chequeo 3
       Compara el resultado contra la tabla recibida: mismas filas, misma
       suma, cada fila igual a la que llegó, y cada Estado válido y acorde
       a su Clase. Devuelve el resumen: filas y suma por Estado.
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

### Este repo no sabe qué es un gasto bancario
- **Qué es:** qué códigos son gasto en cada banco lo decide v3, con la lista
  de cada banco en su `configuracion.toml`. En este repo no hay nada propio de
  un banco.
- **Por qué:** una sola lista no se puede desincronizar. Agregar un gasto o un
  banco nuevo es trabajo solo de v3; este repo no se toca.
- **Descartado:** tener una copia de la lista acá (`bancos.json` y
  `motor/gastos.py`, APR-215). Nunca se conectó al cruce y se sacó (APR-226).
- **Límite:** este repo confía en que v3 reconoció bien los gastos. Un gasto
  con un código nuevo, que no está en la lista de v3, llega como un movimiento
  común.

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

### El control del contrato nuevo son tres chequeos (APR-223, sin conectar)
- **Qué es:** dos chequeos al entrar y uno al final, por cada documento.
  1. *La forma:* la tabla que llega de v3 tiene las cinco columnas del
     contrato, al menos una fila y el tipo de dato correcto en cada fila.
  2. *La foto:* la tabla recibida se guarda intacta; nada la modifica.
  3. *El cierre:* después del cruce, el resultado se compara contra esa tabla.
- **Por qué acá y no en v3:** v3 ya controla su parte (lo armado contra el
  archivo original). Con el contrato nuevo, quien aparta los gastos del cruce
  es este repo, así que acá está el riesgo de perder una fila.
- **Por qué dos al entrar:** el primero frena antes de hacer nada si llega algo
  mal formado, con el motivo exacto. Sin él, una Clase mal escrita se vería
  recién al final, como "falta una fila".
- **Límite:** controla contra lo que llegó de v3, no contra el archivo del
  banco. El tramo de v3 entre su control y la entrega de la tabla no lo
  verifica nadie (ver PENDIENTES.md).

### La forma se controla contra una copia propia del contrato
- **Qué es:** los nombres de las cinco columnas y de las dos clases están
  escritos en `motor/recibir.py`. No se toman del código de v3.
- **Por qué:** quien recibe controla contra lo que espera. Si se tomaran de v3
  y v3 cambiara un nombre por error, este repo lo aceptaría sin enterarse.
- **Qué se exige:** Fecha es una fecha; Código y Descripción son texto (pueden
  estar vacíos); Monto en centavos es un entero; Clase es "Movimiento" o
  "Gasto bancario", exacto. En el libro del sistema, todas "Movimiento".
- **Descartado:** aceptar un monto con decimales aunque sea redondo (100.0).
  El contrato dice entero; aceptar decimales reabre el problema del redondeo.
  También se descartó revisar si un Código es gasto: eso es de v3.
- **Los errores se informan juntos:** se revisan todas las filas y sale un
  solo mensaje con el número de fila y el motivo de cada una (las primeras 20
  y cuántas más hay), igual que en v3. La fila 1 es el primer movimiento de la
  tabla.

### Los gastos bancarios no se separan: se marcan con el Estado
- **Qué es:** las filas no se mueven. Cada documento es una sola tabla, y cada
  fila tiene un Estado: "Sin cruzar", "Cruzado" o "Gasto bancario". Las que
  llegan con Clase "Gasto bancario" arrancan con Estado "Gasto bancario"; el
  cruce solo toma las "Sin cruzar".
- **Por qué:** si nada se mueve, nada se puede perder al separar. Es menos
  código y es como este repo ya trabajaba (una fila, un estado).
- **Clase y Estado son dos columnas:** la Clase dice qué es la fila (lo dijo
  v3) y nunca cambia; el Estado dice qué pasó con ella acá. Que la Clase quede
  intacta es lo que permite controlar el Estado contra ella al final.
- **Descartado:** partir la tabla en dos (movimientos y gastos). El cruce no
  vería los gastos, pero habría filas que cambian de lugar y haría falta
  controlar que las dos partes juntas den el total.
- **Riesgo y resguardos:** que un cambio futuro haga que el cruce tome un
  gasto. Lo frenan tres cosas: el cruce solo toma "Sin cruzar"; una prueba
  que lo intenta a propósito (va con el cruce, APR-214); y el control del
  final, que frena si un gasto bancario no termina como "Gasto bancario".

### El control del final compara contra la tabla tal como llegó
- **Qué es:** la tabla recibida nunca se modifica (el Estado se agrega en una
  copia). Al final se compara el resultado contra ella, en este orden, y frena
  en la primera regla que falla:
  1. misma cantidad de filas;
  2. misma suma (centavos enteros: la comparación es exacta);
  3. cada fila es la que llegó, en el mismo lugar, en sus cinco columnas;
  4. cada Estado es uno de los tres;
  5. Clase y Estado coinciden: un gasto bancario termina "Gasto bancario" y
     un movimiento nunca.
- **Por qué contra la tabla entera y no contra dos números:** contar filas y
  sumar no ve dos errores que se compensan (un monto sube un peso y otro
  baja un peso), ni una Clase cambiada, ni filas en otro orden. Comparar fila
  por fila sí. Es el mismo criterio de v3: se compara contra el original, que
  nadie tocó.
- **Cruzado + Sin cruzar + Gasto bancario = lo que entró** sale de las reglas
  1, 2 y 4 juntas. El control devuelve esos números (el resumen).
- **Cada regla tiene su mensaje,** y el mensaje dice dónde mirar: un gasto
  "Cruzado" es un problema del cruce; una fila que falta, de algún paso que
  perdió filas.
- **Límites:** frena en el primer error (acá un error es una falla del
  programa, no un dato a corregir). Corre una vez por documento: las reglas
  que comparan banco contra sistema (lo cruzado suma igual, las parejas se
  apuntan) siguen en `motor/salida.py` hasta APR-214. No ve un gasto que v3
  no reconoció: llega como "Movimiento" y pasa.

### pandas es una dependencia
- **Por qué:** la tabla que devuelve v3 es un DataFrame de pandas. Trabajar
  sobre esa misma tabla evita convertirla a otra estructura, que sería un paso
  más donde perder filas.
- **Límite:** una dependencia más para instalar. Su versión está fija en
  `requirements.txt`, la misma que usa v3.

### La columna Criterio se va a sacar (decidido, se aplica en APR-214)
- **Por qué:** hoy hay un solo criterio ("Exacto"), así que dice lo mismo en
  todas las filas cruzadas. Vuelve cuando exista una segunda pasada.
- **Se queda:** la fila de la pareja, que es lo que permite corroborar cada
  cruce.

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

