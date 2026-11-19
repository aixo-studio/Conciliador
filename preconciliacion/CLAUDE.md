# CLAUDE.md — Conciliación v3 (etapa 1: preprocesamiento de documentos)

Este archivo es para Claude. Define cómo trabaja Claude en este repo junto con
Matias, de Aixo Studio: él es el usuario, aprueba cada cambio y hace los
commits y los push.

## Qué es esta etapa y dónde termina

Un programa en Python, sin IA, que recibe un documento crudo (el extracto de
un banco o el libro del sistema financiero) y lo devuelve limpio como un
DataFrame de pandas: Fecha, Código, Descripción, Monto en centavos y Clase.
No guarda ni borra ningún archivo.

Es la etapa 1 de la conciliación bancaria. Termina cuando devuelve el
DataFrame de un documento. El cruce entre banco y sistema NO va acá: es la
etapa 2, en otro repo (en GitHub "Conciliador", carpeta local "conciliacion
v4"), que recibe los dos archivos de una cuenta y llama a este repo una vez
por cada uno. Si un pedido es del cruce, frenar y avisar.

Las carpetas locales y los repos de GitHub no se llaman igual:

| Carpeta local     | Repo en GitHub                                             | Etapa                             |
|-------------------|------------------------------------------------------------|-----------------------------------|
| conciliacion v3   | https://github.com/aixo-studio/Pre-procesamiento-bancario- | 1 (este repo)                     |
| conciliacion v4   | https://github.com/aixo-studio/Conciliador                 | 2 (llama a este)                  |

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
  `https://github.com/aixo-studio/Pre-procesamiento-bancario-.git` en las dos
  líneas (fetch y push). Si muestra otro repo (por ejemplo Conciliador), no se
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
   se puede defender meses después.
4. **No avanza** hasta que Matias confirme que puede defender lo nuevo.

Los comentarios en el código y el mapa del flujo siguen, como apoyo para
quien lea el repo, pero no son el objetivo.

Excepción: las pruebas de concepto, demos y experimentos no siguen esta regla.
Ahí manda la velocidad.

## Dónde están los datos

Los originales viven fuera del repo. Por costumbre, en una carpeta al lado:

    <carpeta que contiene el repo>/
      conciliacion v3/                          este repo
      conciliacion resultados/v3/
        input/<AAAA-MM>/                        los crudos (pueden estar en otro lado)

Cada llamada convierte un archivo: recibe la ruta, el banco y si es el libro
del ERP. Armar el par extracto + libro de cada cuenta es de quien llama
(Conciliador). El programa nunca modifica un original y no escribe nada.

Cómo se prueba un archivo desde la terminal (muestra el resumen, no guarda nada):

    python convertir.py BBVA "ruta/extracto.xls"         el extracto del BBVA
    python convertir.py BBVA "ruta/libro.xlsx" --erp     el libro del ERP de la cuenta BBVA

## Orden del repositorio

- `convertir.py` es la puerta de entrada: la función que llama Conciliador
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
- Cada archivo hace una sola cosa. Nada de archivos sueltos ni de código para
  necesidades que todavía no existen. Menos código es mejor.

## Verificación

- `python -m pytest` antes de cada commit (así usa el Python del `.venv` y no
  el de conda). Cada regla de un documento tiene su prueba.
- Al convertir archivos reales, mostrar el resumen de cada uno: filas,
  filas ignoradas, suma y gastos bancarios.
- Referencia fija: septiembre 2026 tiene que dar exactamente esto. Si un
  cambio la mueve, frenar y avisar antes de seguir.

      BBVA         extracto 1.445 filas  −30.550.126,57 | sistema 529 filas  362.494.482,03
      Galicia      extracto   500 filas      493.725,04 | sistema  99 filas  151.123.160,45
      Supervielle  extracto   172 filas      856.523,72 | sistema  65 filas   22.508.801,85
      (en cada libro del sistema se ignora 1 fila de "Saldo Inicial")

      Gastos bancarios del extracto:
      BBVA 836 filas −25.702.218,68 · Galicia 387 filas −58.477.591,43 · Supervielle 89 filas −986.203,99
      (el Galicia, sin verificar con el DataFrame: falta su extracto original)

- Lo que no se comprobó se informa como "sin verificar". Nunca presentar como
  comprobado algo que no se comprobó.
- Al terminar: qué se cambió, qué se verificó y qué quedó pendiente.

## Reglas del producto

- Sin IA. Todo lo decide el código con reglas fijas.
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
- Ninguna fila se pierde en silencio. La cantidad de filas y la suma del
  monto tienen que cerrar contra el original. Si no cierran, no se devuelve
  nada: frena con un error que dice por qué.
- No se guarda ni se borra ningún archivo: el resultado es el DataFrame.
- El saldo inicial no es un movimiento: se saca siempre. Si un documento lo
  trae, se indica en su sección del config (`ignorar`) y la terminal lo informa.
- Las filas con fecha de otro mes salen tal cual. Controlarlas es de
  Conciliador, que sabe qué mes concilia.
- El archivo original nunca se modifica.
- Los archivos reales de un cliente nunca se suben al repo. Las pruebas usan
  datos inventados. Ningún nombre de cliente en el código ni en la
  documentación.

## La salida es el contrato con la etapa 2

Conciliador (en GitHub "Conciliador", carpeta "conciliacion v4") llama a este
repo y usa el DataFrame tal como sale. Cualquier cambio en el contrato rompe
ese repo: antes de hacerlo, frenar y avisar, y cambiarlo en los dos repos en
el mismo paso.

<!-- CONTRATO v3 → v4 · INICIO. Este bloque es igual, palabra por palabra, en el
     CLAUDE.md de "conciliacion v3" y en el de "conciliacion v4". Si cambia,
     cambia en los dos en el mismo paso, con la fecha nueva. -->

**Contrato del 2026-11-04.** Lo que devuelve la etapa 1 (carpeta "conciliacion
v3", en GitHub Pre-procesamiento-bancario-) a la etapa 2 (carpeta
"conciliacion v4", en GitHub Conciliador), que la llama.

- La llamada: `convertir_documento(ruta_archivo, banco, es_erp)`, en
  `convertir.py`. Una por archivo: v4 la llama dos veces por cuenta, con el
  extracto del banco (`es_erp=False`) y con el libro del sistema
  (`es_erp=True`), y en las dos pasa el mismo `banco` (BBVA, Galicia,
  Supervielle, como en `configuracion.toml` de v3).
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
  `configuracion.toml` de v3 (comparación exacta); si no, "Movimiento". En el
  libro del sistema, todas son "Movimiento". v4 cruza las filas
  "Movimiento" y usa las "Gasto bancario" para el control final.
- Las filas con fecha de otro mes salen tal cual: controlarlas es de v4.
- El saldo inicial del libro del sistema no sale.
- Lo que no llega: el texto del Concepto del BBVA y del Galicia, el número de
  cheque del BBVA (Número Documento), las Leyendas Adicionales del Galicia y
  el saldo del extracto. Si la etapa 2 necesita alguno, es un cambio de
  contrato.

Cambios:
- 2026-11-04: v3 deja de escribir Excel en carpetas y devuelve un DataFrame.
  El monto pasa a centavos enteros y los gastos se marcan con la columna
  Clase en vez de ir a una hoja aparte. v3 ya no recibe el mes.
- 2026-10-30 (APR-222 de v3): el extracto pasa a tener dos hojas; los gastos
  bancarios salen separados en "Gastos bancarios".
- 2026-10-20 (commit 306da11 de v3): la segunda columna pasa de Concepto a
  Código.

<!-- CONTRATO v3 → v4 · FIN -->

## Código

- Python 3. Dependencias mínimas: `openpyxl`, `xlrd`, `pandas` y `pytest`.
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

- README.md: qué es, cómo se usa, el mapa de carpetas, el mapa del flujo y las
  decisiones.
- documentos/<documento>/README.md: cómo viene ese documento y los porqués de
  su conversión; lo que ya dice el config no se repite.
- PENDIENTES.md: lo abierto, en orden de prioridad, y lo hecho con su fecha.
- No dejar documentación desactualizada. Distinguir lo hecho de lo propuesto.
