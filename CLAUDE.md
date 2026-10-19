# CLAUDE.md — Conciliación v4 (etapa 2: el cruce)

Este archivo es para Claude. Define cómo trabaja Claude en este repo junto con
Matias, de Aixo Studio: él es el usuario, aprueba cada cambio y hace los
commits y los push.

## Qué es esta etapa, dónde empieza y dónde termina

Un programa en Python, sin IA, que cruza los movimientos del extracto de un
banco con los del libro del sistema financiero de esa cuenta, para el mismo
mes. Es la etapa 2 de la conciliación bancaria.

- **Dónde empieza:** lee los archivos que deja la etapa 1 (el repo
  "conciliacion v3"), tal como dice el contrato de más abajo. Lo primero que
  hace es controlar que la entrada cumpla ese contrato; si no cumple, frena y
  dice por qué.
- **Qué hace hoy:** el cruce exacto (misma fecha y mismo monto) y escribe, por
  banco, `conciliacion resultados/v4/output/<AAAA-MM>/<Banco>/cruce - <Banco> <AAAA-MM>.xlsx`.
- **Dónde termina:** todavía a definir (ver PENDIENTES.md).
- Convertir documentos crudos a cuatro columnas NO va acá: es la etapa 1. Si un
  pedido es de la etapa 1, frenar y avisar.
- Cada pasada nueva del cruce (sumas, gastos bancarios, lo que venga) se
  decide primero en PENDIENTES.md y se construye solo con el OK del usuario.

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
- Primero el plan: qué se va a hacer, por qué y cómo queda el resultado. Si hay
  más de una forma, mostrar las opciones con pros y contras. No se construye
  sin el OK del usuario.
- Nada se crea, modifica ni borra sin aprobación explícita. Un paso a la vez;
  no adelantarse. Si aparece algo que cambia el alcance, frenar y avisar.
- Se trabaja solo con lo que trae el documento. Si una regla necesita datos
  que no están en el archivo, se anota en PENDIENTES.md.
- Nunca tocar la carpeta "(NO TOCAR)".
- Explicar en lenguaje claro: el usuario está aprendiendo programación.

## Entender el código antes de avanzar

Matias tiene que poder seguir el código sin leer cada línea. Para eso:

1. **Comentarios en español.** Arriba de cada archivo, de cada función y de
   cada bloque va una explicación corta y clara de qué hace y para qué sirve
   dentro del flujo. Nada de comentarios en inglés ni técnicos sin explicar.
2. **Mapa del flujo.** El README tiene el camino completo desde que se corre
   `cruzar.py` hasta el resultado: qué función llama a cuál y qué hace cada
   una. Cada vez que el flujo cambia, el mapa se actualiza en el mismo paso.
3. **Freno antes de avanzar.** Cada vez que se agrega o se cambia una función,
   Claude explica qué hace y en qué parte del flujo entra. No se pasa al
   siguiente paso hasta que Matias confirme que lo entendió.

## Dónde están los datos

Los datos viven fuera de los repos, en una carpeta al lado de ellos:

    Documents/
      conciliacion v3/                  repo de la etapa 1
      conciliacion v4/                  este repo
      conciliacion resultados/
        v3/output/<AAAA-MM>/<Banco>/    la entrada de este repo (la escribe v3)
        v4/output/<AAAA-MM>/<Banco>/    la salida de este repo

El repo encuentra la carpeta de datos al lado de él (ruta relativa). Este
repo nunca escribe en `v3/` ni modifica un archivo de entrada.

Cómo se corre:

    python cruzar.py 2026-09            todos los bancos del mes
    python cruzar.py 2026-09 BBVA       un banco

## La entrada: el contrato con la etapa 1

Así deja los archivos "conciliacion v3". Este repo lo controla al leer: si
algo no cumple, frena y dice qué archivo, qué fila y por qué. Si v3 cambia
esto, hay que cambiar este repo en el mismo paso.

- Carpeta: `conciliacion resultados/v3/output/<AAAA-MM>/<Banco>/`.
- En cada carpeta de banco hay exactamente un archivo del banco y uno del
  sistema.
- Nombre: `<documento> - <nombre del original sin extensión>.xlsx`. Si
  `<documento>` empieza con `banco_` es el extracto del banco; si empieza con
  `sistema_`, el libro del sistema.
- Una sola hoja, "Movimientos".
- Fila 1, el encabezado: Fecha · Concepto · Descripción · Monto. Debajo, un
  movimiento por fila, en el orden del original.
- Fecha: fecha real de Excel. Concepto y Descripción: texto (puede estar
  vacío). Monto: número con dos decimales (si es redondo puede venir como
  entero); crédito positivo, débito negativo. En el sistema, Debe (entra al
  banco) es positivo y Haber negativo.
- Los gastos bancarios vienen incluidos en el extracto: v3 no los separa.
- Al leer el Monto se pasa a centavos enteros redondeando, y se compara y suma
  en centavos: un decimal leído de un Excel puede venir con un error mínimo
  (1500000.2499999 en vez de 1500000.25).

## Orden del repositorio

- `cruzar.py` es la puerta de entrada: recibe el mes (y opcionalmente el
  banco), corre cada paso y muestra el resumen.
- `motor/` tiene los pasos del proceso, un archivo por paso: `entrada.py`
  (encontrar, controlar y leer los dos archivos), `cruce_exacto.py` (misma
  fecha y mismo monto) y `salida.py` (controlar y escribir el Excel).
- `pruebas/` tiene una prueba por archivo de `motor/`, con datos inventados;
  `pruebas/datos.py` arma esos archivos.
- La salida tiene tres hojas: "Resumen", "Banco" y "Sistema". Banco y Sistema
  llevan todas las filas de la entrada, en el mismo orden, con tres columnas
  más: Estado ("Cruzado" / "Sin cruzar"), N° de cruce (une las filas que
  cruzaron entre sí) y Criterio (cómo se cruzó). Cada pasada nueva solo cambia
  el estado de filas "Sin cruzar"; nunca agrega ni saca filas.
- Cada archivo hace una sola cosa. Nada de archivos sueltos ni de código para
  necesidades que todavía no existen. Menos código es mejor.

## Verificación

- `pytest` antes de cada commit. Cada regla tiene su prueba.
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

- Python 3. Dependencias mínimas: `openpyxl` y `pytest`.
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

- README.md: qué es, cómo se usa, el mapa de carpetas y el mapa del flujo.
- PENDIENTES.md: lo abierto, en orden de prioridad, y lo hecho con su fecha.
- No dejar documentación desactualizada. Distinguir lo hecho de lo propuesto.
