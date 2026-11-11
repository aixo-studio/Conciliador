# CLAUDE.md — Conciliación v4 (etapa 2: el cruce)

Este archivo es para Claude. Define cómo trabaja Claude en este repo junto con
Matias, de Aixo Studio: él es el usuario, aprueba cada cambio y hace los
commits y los push.

## Qué es esta etapa, dónde empieza y dónde termina

Un programa en Python, sin IA, que cruza los movimientos del extracto de un
banco con los del libro del sistema financiero de esa cuenta, para el mismo
mes. Es la etapa 2 de la conciliación bancaria.

- **Dónde empieza:** recibe las dos tablas (DataFrame) de una cuenta, tal como
  las devuelve la etapa 1 (ver el contrato de más abajo): la del extracto del
  banco y la del libro del sistema. Lo primero que hace es controlar que
  cumplan ese contrato; si no cumplen, frena y dice por qué.
- **Qué hace hoy:** marca los gastos bancarios con su Estado, hace el cruce
  exacto (misma fecha y mismo monto) sobre el resto, controla que no se perdió
  nada y escribe el Excel donde le indique quien llama. Todo lo encadena
  `cruzar_cuenta()` (en `cruzar_cuenta.py`).
- **Quién consigue las tablas:** llamar a v3 y la terminal son la comunicación
  entre los repos (APR-235). Hasta que exista, este repo no se corre de punta
  a punta: se verifica con `python -m pytest`.
- **Dónde termina:** todavía a definir (ver PENDIENTES.md).
- Convertir documentos crudos a cuatro columnas NO va acá: es la etapa 1. Si un
  pedido es de la etapa 1, frenar y avisar.
- Cada pasada nueva del cruce (sumas, lo que venga) se
  decide primero en PENDIENTES.md y se construye solo con el OK del usuario.

Las carpetas locales y los repos de GitHub no se llaman igual:

| Carpeta local     | Repo en GitHub                                             | Etapa                             |
|-------------------|------------------------------------------------------------|-----------------------------------|
| conciliacion v3   | https://github.com/aixo-studio/Pre-procesamiento-bancario- | 1 (la que deja los archivos)      |
| conciliacion v4   | https://github.com/aixo-studio/Conciliador                 | 2 (este repo)                     |

## Cómo se trabaja

- Claude trabaja solo sobre la carpeta local del repo, en la computadora del
  usuario: ahí lee, crea y edita los archivos. Nunca clona el repo ni trabaja
  sobre una copia (en la nube o en otro lugar). Si no tiene acceso a la
  carpeta local, frena y avisa.
- Claude puede correr lo que solo verifica, sin cambiar nada: pytest y leer
  archivos, para chequear su trabajo antes de pasarlo.
- Todo lo que genera, mueve o borra archivos fuera del código que Claude edita
  (conversiones reales, crear o mover carpetas de datos, el .venv) lo corre el
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
   se puede defender meses después.
4. **No avanza** hasta que Matias confirme que puede defender lo nuevo.

Los comentarios en el código y el mapa del flujo siguen, como apoyo para
quien lea el repo, pero no son el objetivo.

Excepción: las pruebas de concepto, demos y experimentos no siguen esta regla.
Ahí manda la velocidad.

## Dónde están los datos

Los archivos reales viven fuera del repo y nunca se suben. Este repo ya no
lee ninguna carpeta: recibe las dos tablas por parámetro y escribe el Excel
del cruce en la ruta que le indica quien llama. Qué carpeta es esa y cómo se
corre todo junto se definen con la comunicación entre los repos (APR-235).

## La entrada: el contrato con la etapa 1

Las dos tablas que recibe `cruzar_cuenta()` son las que devuelve
`convertir_documento()` de v3, una llamada por archivo. Este repo controla al
recibirlas que cumplan el contrato; si algo no cumple, frena y dice qué fila
y por qué. Si v3 cambia esto, hay que cambiar este repo en el mismo paso.

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

## Orden del repositorio

- `cruzar_cuenta.py` es la puerta de entrada: `cruzar_cuenta(tabla_banco,
  tabla_sistema, ruta_salida)` recibe las dos tablas de una cuenta, corre cada
  paso y escribe el Excel. Es lo que llama quien consigue las tablas (APR-235).
- `motor/` tiene los pasos del proceso, un archivo por paso: `recibir.py`
  (controlar la forma de cada tabla y ponerle su Estado inicial),
  `cruce_exacto.py` (misma fecha y mismo monto, solo filas "Sin cruzar"),
  `controlar.py` (después del cruce, cada tabla contra la recibida) y
  `salida.py` (los controles que unen a los dos lados y el Excel).
- Este repo no tiene nada propio de un banco: qué es gasto bancario lo decide
  v3, y acá llega en la columna Clase.
- `pruebas/` tiene una prueba por archivo de `motor/` y una de la corrida
  completa, con datos inventados; `pruebas/datos.py` arma esas tablas.
- La salida tiene tres hojas: "Resumen", "Banco" y "Sistema". Banco y Sistema
  llevan todas las filas de la entrada, en el mismo orden, con siete columnas:
  Fecha · Código · Descripción · Monto · Clase · Estado · "Fila en Sistema" /
  "Fila en Banco" (la fila de la pareja en la otra hoja de este mismo archivo;
  el encabezado es la fila 1 y los datos empiezan en la 2). Cada pasada nueva
  solo cambia el estado de filas "Sin cruzar"; nunca agrega ni saca filas.
- Cada archivo hace una sola cosa. Nada de archivos sueltos ni de código para
  necesidades que todavía no existen. Menos código es mejor.

## Verificación

- `python -m pytest` antes de cada commit (así usa el Python del `.venv`).
  Cada regla tiene su prueba.
- Al leer archivos reales, mostrar el resumen de cada lado: filas, suma y
  rango de fechas.
- Referencia fija: la lectura de septiembre 2026 tiene que dar exactamente
  esto. Si un cambio la mueve, frenar y avisar antes de seguir.

      BBVA         banco 1.445 filas  −30.550.126,57 | sistema 529 filas  362.494.482,03
      Galicia      banco   500 filas      493.725,04 | sistema  99 filas  151.123.160,45
      Supervielle  banco   172 filas      856.523,72 | sistema  65 filas   22.508.801,85

  Cruce exacto de septiembre 2026:

      BBVA         394 cruces | banco sin cruzar 1.051 | sistema sin cruzar 135
      Galicia       86 cruces | banco sin cruzar   414 | sistema sin cruzar  13
      Supervielle   54 cruces | banco sin cruzar   118 | sistema sin cruzar  11

  (La referencia se vuelve a comprobar cuando APR-235 conecte v3; hasta
  entonces, las pruebas usan tablas inventadas.)

- Lo que no se comprobó se informa como "sin verificar". Nunca presentar como
  comprobado algo que no se comprobó.
- Al terminar: qué se cambió, qué se verificó y qué quedó pendiente.

## Reglas del producto

- Sin IA. Todo lo decide el código con reglas fijas.
- Ninguna fila se pierde en silencio. Cada movimiento que entra tiene que
  aparecer en el resultado, y la cantidad de filas y la suma tienen que cerrar
  contra la entrada. Si no cierran, no se genera el resultado y se dice por qué.
- La entrada nunca se modifica.
- Los archivos reales de un cliente nunca se suben al repo (ni a GitHub). Las
  pruebas usan datos inventados. Ningún nombre de cliente en el código ni en
  la documentación.

## Código

- Python 3.12, el mismo que v3. Dependencias mínimas: `openpyxl`, `pandas` y
  `pytest`.
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
  decisiones (con su porqué, la alternativa descartada y sus límites).
- PENDIENTES.md: lo abierto, en orden de prioridad, y lo hecho con su fecha.
- No dejar documentación desactualizada. Distinguir lo hecho de lo propuesto.
