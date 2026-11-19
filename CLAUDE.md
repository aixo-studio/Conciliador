# CLAUDE.md — Conciliador (conciliación bancaria, etapas 1 y 2)

Este archivo es para Claude. Define cómo trabaja Claude en este repo junto con
Matias, de Aixo Studio: él es el usuario, aprueba cada cambio y hace los
commits y los push.

## Qué es este repo

Un programa en Python, sin IA, que concilia el extracto de un banco con el
libro del sistema financiero (el ERP) de esa cuenta, para el mismo mes. Tiene
dos etapas, cada una en su carpeta:

| Carpeta            | Etapa | Qué hace                                                           |
|--------------------|-------|--------------------------------------------------------------------|
| `preconciliacion/` | 1     | Recibe un documento crudo y lo devuelve limpio como un DataFrame.  |
| `conciliador/`     | 2     | Recibe las dos tablas de una cuenta y las cruza.                   |

- Cada etapa hace solo lo suyo. La etapa 1 nunca usa nada de la etapa 2. Cada
  pedido se hace en la etapa que le corresponde; si toca las dos, frenar y
  avisar.
- Lo que la etapa 1 entrega a la etapa 2 está fijado en el contrato (ver más
  abajo).
- `conciliar.py`, en la raíz, encadena las dos etapas de punta a punta: es el
  único archivo que conoce a las dos.
- **Dónde termina:** todavía a definir (ver PENDIENTES.md).

### Etapa 1: la preconciliación (`preconciliacion/`)

Recibe un documento crudo (el extracto de un banco o el libro del sistema
financiero) y lo devuelve limpio como un DataFrame de pandas: Fecha, Código,
Descripción, Monto en centavos y Clase. No guarda ni borra ningún archivo.
Termina cuando devuelve el DataFrame de un documento.

### Etapa 2: el conciliador (`conciliador/`)

Cruza los movimientos del extracto de un banco con los del libro del sistema
de esa cuenta.

- **Dónde empieza:** recibe las dos tablas (DataFrame) de una cuenta, tal como
  las devuelve la etapa 1: la del extracto del banco y la del libro del
  sistema. Lo primero que hace es controlar que cumplan el contrato; si no
  cumplen, frena y dice por qué.
- **Qué hace hoy:** hace el cruce exacto (misma fecha y mismo monto) entre las
  filas "Movimiento" (los gastos bancarios no cruzan), controla que no se
  perdió nada y devuelve tres tablas (cruces, banco pendiente y ERP pendiente)
  y un resumen. No escribe ningún archivo. Todo lo encadena `cruzar_cuenta()`
  (en `conciliador/cruzar_cuenta.py`).
- Cada pasada nueva del cruce (sumas, lo que venga) se decide primero en
  PENDIENTES.md y se construye solo con el OK del usuario.

### El repo y la carpeta local

| Carpeta local     | Repo en GitHub                             |
|-------------------|--------------------------------------------|
| conciliacion v4   | https://github.com/aixo-studio/Conciliador |

La carpeta local se renombra a "Conciliador", como el repo, al cerrar la unión.
La etapa 1 venía del repo Pre-procesamiento-bancario- (carpeta local
"conciliacion v3"). El 2026-11-19 entró a este repo con toda su historia; el
repo viejo se archiva.

## Cómo se trabaja

- Claude trabaja solo sobre la carpeta local del repo, en la computadora del
  usuario: ahí lee, crea y edita los archivos. Nunca clona el repo ni trabaja
  sobre una copia (en la nube o en otro lugar). Si no tiene acceso a la
  carpeta local, frena y avisa.
- Claude puede correr lo que solo verifica, sin cambiar nada: pytest, leer
  archivos y convertir archivos reales desde la terminal (solo lee y muestra
  el resumen; no guarda nada), para chequear su trabajo antes de pasarlo.
- Todo lo que genera, mueve o borra archivos fuera del código que Claude edita
  (crear o mover carpetas de datos, el .venv, git stash o checkout) lo corre el
  usuario. Claude le pasa cada comando listo para copiar, con qué hace y qué
  tiene que mostrar en pantalla.
- Los commits y los push los hace siempre el usuario. Claude le pasa los
  comandos y nunca los corre.
- Antes de cada push, el primer comando es `git remote -v`. Tiene que mostrar
  `https://github.com/aixo-studio/Conciliador.git` en las dos líneas (fetch y
  push). Si muestra otro repo (por ejemplo Pre-procesamiento-bancario-), no se
  pushea: se frena y se revisa.
- Primero el plan: qué se va a hacer, por qué y cómo queda el resultado. Si hay
  más de una forma, mostrar las opciones con pros y contras. No se construye
  sin el OK del usuario.
- Nada se crea, modifica ni borra sin aprobación explícita. Un paso a la vez;
  no adelantarse. Si aparece algo que cambia el alcance, frenar y avisar.
- Se trabaja solo con lo que trae el documento. Si una regla necesita datos
  que no están en el archivo, se anota en PENDIENTES.md.
- Nunca tocar la carpeta "(NO TOCAR)".
- Explicar en lenguaje claro: el usuario está aprendiendo programación.

## Poder defender lo que se entrega

Este repo es para un cliente. La regla es la "defensa en el pizarrón": Matias
tiene que poder explicar en cualquier momento, sin abrir el código, cómo
funciona el sistema y defender las decisiones que se tomaron. No hace falta
recordar nombres de funciones ni detalles de implementación. Sí tiene que
poder responder con seguridad preguntas como:

- ¿Por qué se hizo X y no Y?
- ¿Qué pasa si llega un archivo equivocado o con datos mal cargados, por error
  o a propósito?
- ¿Cómo se guardan y se comparan los datos, y por qué así?
- ¿Dónde falla o puede fallar?

Para eso Claude:

1. **Antes de construir**, explica la decisión con sus alternativas, pros y
   contras, en lenguaje claro.
2. **Al terminar cada cambio**, entrega la defensa: cómo funciona en pocas
   líneas, qué se decidió y por qué, qué pasa con datos malos y dónde falla.
3. **Anota cada decisión en el README**, en la sección "Decisiones": qué se
   decidió, por qué, qué alternativa se descartó y sus límites conocidos. Así
   se puede defender meses después. Va en el README de su etapa, o en el de la
   raíz si es de todo el sistema.
4. **No avanza** hasta que Matias confirme que puede defender lo nuevo.

Los comentarios en el código y el mapa del flujo siguen, como apoyo para
quien lea el repo, pero no son el objetivo.

Excepción: las pruebas de concepto, demos y experimentos no siguen esta regla.
Ahí manda la velocidad.

## Dónde están los datos

Los archivos reales viven fuera del repo y nunca se suben. Por costumbre, en
una carpeta al lado:

    <carpeta que contiene el repo>/
      conciliacion v4/                          este repo
      conciliacion resultados/v3/
        input/<AAAA-MM>/                        los crudos (pueden estar en otro lado)

El programa nunca modifica un original: la etapa 1 recibe la ruta de un
archivo, el banco y si es el libro del ERP, y devuelve su tabla; la etapa 2
recibe las dos tablas de una cuenta y devuelve el resultado. Armar el par
extracto + libro de cada cuenta es de quien llama. Solo se escriben archivos
si se pide con `--csv`: los 4 CSV del resultado, en la carpeta indicada. Como
tienen datos del cliente, van fuera del repo (por ejemplo, en
`conciliacion resultados/`); el `.gitignore` igual ignora los `*.csv`.

Cómo se prueba desde la terminal, en la raíz del repo (sin `--csv`, muestra el
resumen y no guarda nada):

    python conciliar.py BBVA "ruta/extracto.xls" "ruta/libro.xlsx"      la cuenta BBVA de punta a punta
    python conciliar.py BBVA "ruta/extracto.xls" "ruta/libro.xlsx" --csv "ruta/carpeta"     y guarda los 4 CSV
    python -m preconciliacion.convertir BBVA "ruta/extracto.xls"         el extracto del BBVA
    python -m preconciliacion.convertir BBVA "ruta/libro.xlsx" --erp     el libro del ERP de la cuenta BBVA

## El contrato entre las dos etapas

Las dos tablas que recibe `cruzar_cuenta()` son las que devuelve
`convertir_documento()`, una llamada por archivo. La etapa 2 controla al
recibirlas que cumplan el contrato; si algo no cumple, frena y dice qué fila
y por qué. Cualquier cambio en el contrato rompe la etapa 2: antes de hacerlo,
frenar y avisar, y cambiar las dos etapas en el mismo commit, con la fecha
nueva del contrato.

**Contrato del 2026-11-04.** Lo que devuelve la etapa 1 (`preconciliacion/`)
a la etapa 2 (`conciliador/`).

- La llamada: `convertir_documento(ruta_archivo, banco, es_erp)`, en
  `preconciliacion/convertir.py`. Una por archivo: se llama dos veces por
  cuenta, con el extracto del banco (`es_erp=False`) y con el libro del
  sistema (`es_erp=True`), y en las dos se pasa el mismo `banco` (BBVA,
  Galicia, Supervielle, como en `preconciliacion/configuracion.toml`).
- Si el archivo no se puede convertir (banco desconocido, faltan columnas,
  filas que no se pueden leer, filas o suma que no cierran), frena con un
  `ValueError` que dice por qué: qué columnas faltan y en qué fila, o todas
  las filas con errores y su motivo. No devuelve nada a medias.
- Lo que devuelve: un DataFrame de pandas, una fila por movimiento, en el
  orden del original, con estas cinco columnas en este orden:

      Fecha               fecha (datetime64)
      Código              texto
      Descripción         texto (puede estar vacío)
      Monto en centavos   entero (int64)
      Clase               texto: "Gasto bancario" o "Movimiento"

- Código: el valor puro de la columna que identifica el tipo de movimiento en
  cada documento, sin mezclar nada. Siempre texto, tal cual el original, con
  sus ceros adelante ("005", nunca 5).

      extracto BBVA         Codigo               ej. 236
      extracto Galicia      Grupo de Conceptos   ej. 000901 - Impuestos
      extracto Supervielle  Concepto             ej. Impuesto Débitos y Créditos/DB
      libro del sistema     Tipo de documento    ej. Orden de pago

- Monto en centavos: entero, sin decimales (−136550 es −1.365,50). Crédito
  positivo, débito negativo. En el sistema, Debe (entra al banco) es positivo
  y Haber negativo. Se compara y se suma tal cual, sin redondear.
- Clase: "Gasto bancario" si el Código está en la lista `gastos` del banco en
  `preconciliacion/configuracion.toml` (comparación exacta); si no,
  "Movimiento". En el libro del sistema, todas son "Movimiento". La etapa 2
  cruza las filas "Movimiento" y usa las "Gasto bancario" para el control
  final.
- Las filas con fecha de otro mes salen tal cual: controlarlas es de la
  etapa 2.
- El saldo inicial del libro del sistema no sale.
- Lo que no llega: el texto del Concepto del BBVA y del Galicia, el número de
  cheque del BBVA (Número Documento), las Leyendas Adicionales del Galicia y
  el saldo del extracto. Si la etapa 2 necesita alguno, es un cambio de
  contrato.

Cambios:
- 2026-11-19: los dos repos se unen en este. El contrato queda en un solo
  lugar; no cambia nada de lo que se entrega.
- 2026-11-04: v3 deja de escribir Excel en carpetas y devuelve un DataFrame.
  El monto pasa a centavos enteros y los gastos se marcan con la columna
  Clase en vez de ir a una hoja aparte. v3 ya no recibe el mes.
- 2026-10-30 (APR-222 de v3): el extracto pasa a tener dos hojas; los gastos
  bancarios salen separados en "Gastos bancarios".
- 2026-10-20 (commit 306da11 de v3): la segunda columna pasa de Concepto a
  Código.

## Orden del repositorio

- Una carpeta por etapa, `preconciliacion/` y `conciliador/`, cada una con su
  puerta de entrada, su `motor/`, sus `pruebas/` y su README.
- En la raíz: `conciliar.py` (la puerta de entrada de punta a punta: la
  función `conciliar` y la terminal), `pruebas/` (la prueba del recorrido
  completo), este CLAUDE.md, el README.md general, PENDIENTES.md, `pytest.ini`
  (corre las pruebas de las dos etapas y la del recorrido), `requirements.txt`
  (un solo `.venv` para todo) y `.gitignore`.
- Cada archivo hace una sola cosa. Nada de archivos sueltos ni de código para
  necesidades que todavía no existen. Menos código es mejor.

### Etapa 1 (`preconciliacion/`)

- `convertir.py` es la puerta de entrada: la función que llama la etapa 2
  (`convertir_documento`) y la terminal (`main`). Recibe archivo, banco y si
  es el ERP, y devuelve el DataFrame (la terminal muestra el resumen).
- `configuracion.toml` tiene las reglas de cada documento: una sección por
  banco (reglas del extracto y lista de gastos bancarios) y una para el ERP.
- `motor/` tiene lo que es igual para todos los documentos: traer las reglas
  del config, leer, armar las columnas, controlar y armar el DataFrame. No
  lleva nada propio de un banco.
- `documentos/<documento>/README.md` explica, para personas, lo que el config
  no dice: de dónde sale el documento, cómo viene, por qué se eligió cada
  columna, sus condiciones y un ejemplo. No repite el config (qué columna va
  a cada lugar, la lista de gastos): eso vive solo en su sección, así no
  quedan dos versiones que se contradigan.
- Agregar un banco es agregar su sección en `configuracion.toml`, su README y
  su prueba. Si para eso hay que tocar el `motor/`, frenar y avisar.

### Etapa 2 (`conciliador/`)

- `cruzar_cuenta.py` es la puerta de entrada: `cruzar_cuenta(tabla_banco,
  tabla_erp)` recibe las dos tablas de una cuenta, corre cada paso y devuelve
  los cruces, el banco pendiente, el ERP pendiente y el resumen.
- `motor/` tiene los pasos del proceso, un archivo por paso: `recibir.py`
  (controlar que cada tabla cumpla el contrato, sin modificarla),
  `cruce_exacto.py` (misma fecha y mismo monto, solo filas "Movimiento"; devuelve
  las tres tablas) y `controlar.py` (con lo que devolvió el cruce se vuelve a
  armar lo que entró: si no da igual, frena; si da, devuelve el resumen).
- `motor/salida.py` escribe los 4 CSV (cruces, banco pendiente, ERP pendiente
  y resumen) con lo que devuelve `cruzar_cuenta()`, ya controlado. No lo llama
  `cruzar_cuenta()`: lo llama `conciliar.py`, solo con `--csv`. Escribe todas
  las columnas que traiga cada tabla, así una pasada nueva del cruce no lo
  obliga a cambiar.
- La etapa 2 no tiene nada propio de un banco: qué es gasto bancario lo decide
  la etapa 1, y acá llega en la columna Clase.
- `pruebas/` tiene una prueba por archivo de `motor/` y una de la corrida
  completa, con datos inventados; `pruebas/datos.py` arma esas tablas.
- El resultado son tres tablas. "Cruces": las filas del banco que cruzaron,
  con las cinco columnas del contrato y una sexta, "Fila en ERP" (el número de
  fila de su pareja en la tabla del ERP tal como llegó; la primera es la 0).
  "Banco pendiente" y "ERP pendiente": las filas que no cruzaron, con las cinco
  columnas; los gastos bancarios quedan en el banco pendiente. Cada tabla
  conserva el orden y el número de fila con que llegó; entre las tres están
  todas las filas que entraron, ni una más ni una menos.

## Verificación

- `python -m pytest` antes de cada commit (así usa el Python del `.venv` y no
  el de conda). Corre las pruebas de las dos etapas. Cada regla tiene su
  prueba.
- Al convertir archivos reales (etapa 1), mostrar el resumen de cada uno:
  filas, filas ignoradas, suma y gastos bancarios.
- Al cruzar archivos reales (etapa 2), mostrar el resumen de cada lado: filas,
  suma y rango de fechas.
- Referencia fija: septiembre 2026 tiene que dar exactamente esto. Si un
  cambio la mueve, frenar y avisar antes de seguir.

  Etapa 1, conversión:

      BBVA         extracto 1.445 filas  −30.550.126,57 | sistema 529 filas  362.494.482,03
      Galicia      extracto   500 filas      493.725,04 | sistema  99 filas  151.123.160,45
      Supervielle  extracto   172 filas      856.523,72 | sistema  65 filas   22.508.801,85
      (en cada libro del sistema se ignora 1 fila de "Saldo Inicial")

      Gastos bancarios del extracto:
      BBVA 836 filas −25.702.218,68 · Galicia 387 filas −58.477.591,43 · Supervielle 89 filas −986.203,99

  Las listas de gastos se armaron con los documentos de septiembre. Hacen
  falta otros meses para confirmar que estén todos los códigos (ver
  PENDIENTES.md).

  Etapa 2, cruce exacto:

      BBVA         394 cruces | banco sin cruzar 1.051 | sistema sin cruzar 135
      Galicia       86 cruces | banco sin cruzar   414 | sistema sin cruzar  13
      Supervielle   54 cruces | banco sin cruzar   118 | sistema sin cruzar  11

  (Comprobado de punta a punta con `conciliar.py` el 2026-11-19.)

- Lo que no se comprobó se informa como "sin verificar". Nunca presentar como
  comprobado algo que no se comprobó.
- Al terminar: qué se cambió, qué se verificó y qué quedó pendiente.

## Reglas del producto

- Sin IA. Todo lo decide el código con reglas fijas.
- Ninguna fila se pierde en silencio. Cada movimiento que entra tiene que
  aparecer en el resultado, y la cantidad de filas y la suma tienen que cerrar
  contra la entrada. Si no cierran, no se devuelve nada: frena con un error
  que dice por qué.
- El archivo original y las tablas que recibe cada etapa nunca se modifican.
- No se borra ningún archivo. El resultado son DataFrames; solo se escriben
  archivos si se pide con `--csv` (los 4 CSV del resultado, que reemplazan a
  los de una corrida anterior en esa carpeta).
- Los archivos reales de un cliente nunca se suben al repo (ni a GitHub). Las
  pruebas usan datos inventados. Ningún nombre de cliente en el código ni en
  la documentación.

### Etapa 1

- Cada documento sale entero, en un solo DataFrame, una fila por movimiento y
  en el orden del original. Cada fila lleva su Clase: "Gasto bancario" o
  "Movimiento". En el libro del ERP todas son "Movimiento".
- Un gasto bancario se reconoce porque su Código está en la lista `gastos` de
  su banco en `configuracion.toml`, comparado exacto. Cada banco tiene que
  tener su lista, no vacía y sin repetidos; si no, el programa frena.
- Qué columna del original va a cada columna del DataFrame lo define la
  sección de cada documento en `configuracion.toml`, y nada más. No se agregan
  columnas a la Descripción.
- Quien llama dice qué es el archivo (el banco y si es el ERP), nunca el
  nombre del archivo, y es responsable de que sea el correcto. Si el banco no
  está en el config, el archivo no se convierte y se dice cuáles hay.
- El archivo tiene que traer solo las columnas que se usan (las de las reglas
  de su documento); las demás pueden cambiar. Si falta una, no se convierte y
  se dice cuál y en qué fila.
- Si hay filas que no se pueden leer, se informan todas juntas (fila y motivo)
  en un solo error, y no se devuelve nada.
- El saldo inicial no es un movimiento: se saca siempre. Si un documento lo
  trae, se indica en su sección del config (`ignorar`) y la terminal lo informa.
- Las filas con fecha de otro mes salen tal cual. Controlarlas es de la
  etapa 2, que sabe qué mes concilia.

## Código

- Python 3.12. Dependencias mínimas: `openpyxl`, `xlrd`, `pandas` y `pytest`.
- Nombres en español, completos y sin abreviaturas: funciones y variables en
  `snake_case`, clases en `PascalCase`, constantes en `MAYUSCULAS`.
- Los montos se controlan en centavos enteros, para que la suma no falle por
  decimales.
- Comentarios en español, cortos, que expliquen el por qué.
- Todo tiene arriba una descripción breve de lo que hace, en lenguaje simple,
  para que se entienda sin saber programar:
  - cada archivo empieza diciendo qué hace y en qué paso del proceso está;
  - cada función tiene arriba una o dos líneas: qué recibe, qué hace y qué
    devuelve;
  - cada bloque que no se entiende solo tiene arriba una línea que lo explica.
  No se comenta línea por línea lo que ya se lee en el código.

## Documentación

- README.md de la raíz: qué es, cómo se usa, el mapa de carpetas, el mapa del
  flujo y las decisiones de todo el sistema (con su porqué, la alternativa
  descartada y sus límites).
- README.md de cada etapa: cómo funciona por dentro y sus decisiones.
- `preconciliacion/documentos/<documento>/README.md`: cómo viene ese documento
  y los porqués de su conversión; lo que ya dice el config no se repite.
- PENDIENTES.md: lo abierto, en orden de prioridad, y lo hecho con su fecha.
- No dejar documentación desactualizada. Distinguir lo hecho de lo propuesto.
