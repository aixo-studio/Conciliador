# Conciliación v3 — preprocesamiento de documentos

Etapa 1 de la conciliación bancaria. Recibe un documento (el extracto de un
banco o el libro del ERP de esa cuenta) y lo devuelve limpio, como un
DataFrame de pandas con cinco columnas: **Fecha, Código, Descripción, Monto en
centavos y Clase**. Crédito en positivo, débito en negativo. La Clase dice si
la fila es un gasto bancario. Sin IA: todo son reglas fijas, escritas en
`configuracion.toml`.

No guarda ni borra ningún archivo: quien llama recibe el DataFrame.

Quien llama es la etapa 2, el cruce entre banco y sistema, que va en otro repo
(en GitHub "Conciliador", carpeta local "conciliacion v4"). Conciliador recibe
los dos archivos de una cuenta y llama a este repo una vez por cada uno.

## Cómo se usa

La primera vez, en la terminal, dentro de esta carpeta:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Desde Conciliador** (el uso normal):

```python
from convertir import convertir_documento

extracto = convertir_documento(Path("extracto.xls"), "BBVA", es_erp=False)
libro = convertir_documento(Path("libro.xlsx"), "BBVA", es_erp=True)
```

Cada llamada recibe un archivo, su banco y si es el libro del ERP, y devuelve
el DataFrame. Si algo no cierra, frena con un `ValueError` que dice por qué:
el banco que no está configurado, las columnas que faltan o todas las filas
con errores.

**Desde la terminal**, para probar un archivo y ver el resumen (no guarda nada):

```
source .venv/bin/activate
python convertir.py BBVA "ruta/extracto.xls"          el extracto del BBVA
python convertir.py BBVA "ruta/libro.xlsx" --erp      el libro del ERP de la cuenta BBVA
```

Muestra las filas (y las ignoradas), las columnas, la suma, cuántas filas son
gasto bancario y cuánto suman, y la primera y la última fecha.

Para correr las pruebas: `python -m pytest` (así usa el Python del `.venv`
aunque haya otro instalado, por ejemplo el de conda).

## Lo que se devuelve

Un DataFrame con una fila por movimiento, en el orden del original:

| Columna | Tipo | Qué es |
|---|---|---|
| Fecha | fecha (`datetime64`) | la fecha del movimiento |
| Código | texto | el valor puro de la columna que identifica el tipo de movimiento; con sus ceros (`"005"`) |
| Descripción | texto | puede estar vacía |
| Monto en centavos | entero (`int64`) | crédito positivo, débito negativo; en el sistema, Debe positivo y Haber negativo |
| Clase | texto | `"Gasto bancario"` o `"Movimiento"`; en el libro del ERP, siempre `"Movimiento"` |

Es el contrato con Conciliador: está en el CLAUDE.md, con su versión.

## Mapa de carpetas

```
convertir.py           la puerta de entrada: la función que llama Conciliador y la terminal
configuracion.toml     las reglas de cada banco y del ERP, con la lista de gastos de cada banco
motor/                 lo que es igual para todos los documentos
  configuracion.py     trae del config las reglas, controla la lista de gastos de
                       cada banco y reconoce si un Código es gasto
  leer.py              abre el Excel y encuentra la tabla
  armar.py             arma Fecha, Código, Descripción y Monto de cada fila
  controlar.py         controla filas y suma contra el original
  devolver.py          arma el DataFrame, con la Clase de cada fila
documentos/            un README.md por documento: cómo viene y los porqués (para personas; no repite el config)
  banco_bbva/
  banco_galicia/
  banco_supervielle/
  sistema_finnegans/     el libro del ERP (sirve para la cuenta de cualquier banco)
pruebas/               una prueba por documento, una de la entrada, una de los gastos,
                       una del control y una del DataFrame, con datos inventados
CLAUDE.md              cómo se trabaja en este repo y el contrato con Conciliador
PENDIENTES.md          lo abierto y lo hecho
```

## Mapa del flujo

El camino de un archivo desde que Conciliador llama a
`convertir_documento(archivo, "BBVA", es_erp=False)` hasta que recibe el
DataFrame. Entre paréntesis, el archivo donde está cada función.

```
convertir_documento()  (convertir.py)
│  (Desde la terminal, main() hace lo mismo con convertir_con_resumen()
│   y muestra el resumen en vez de devolver el DataFrame.)
│
└─► convertir_con_resumen()  (convertir.py)
    │
    ├─► 1. buscar_reglas()  (motor/configuracion.py)
    │      Lee configuracion.toml. Si el banco no está, frena.
    │      Devuelve las reglas: las del ERP si es_erp, si no las del banco.
    │      └─ controlar_gastos()  si es un extracto de banco, revisa su lista de
    │                             gastos; si falta, está vacía o tiene repetidos,
    │                             frena
    │
    ├─► 2. limpiar_archivo()  (convertir.py)
    │      ├─ leer_filas()           (motor/leer.py) abre el Excel y trae las filas
    │      │                         de la primera hoja; si no puede, frena
    │      ├─ columnas_que_se_usan() (motor/configuracion.py) saca de las reglas qué
    │      │                         columnas tiene que traer el archivo
    │      ├─ encontrar_tabla()      (motor/leer.py) busca la fila que tiene esas
    │      │    │                    columnas; si no está, frena y dice cuáles faltan
    │      │    │                    (o que ninguna fila se parece: es otro documento)
    │      │    └─ buscar_seguidas() en el ERP, toma el Debe y Haber en pesos
    │      ├─ armar_movimientos()    (motor/armar.py) recorre todas las filas:
    │      │    ├─ esta_vacia()      saltea las filas vacías
    │      │    └─ armar_fila()      arma cada fila:
    │      │         ├─ es_ignorada()  saltea las de "ignorar" (el "Saldo Inicial")
    │      │         ├─ a_centavos()   pasa crédito y débito a centavos enteros
    │      │         ├─ a_fecha()      pasa la fecha a fecha real
    │      │         ├─ a_codigo()     toma el Código tal cual, como texto; si
    │      │         │                 viene como número, es un error (perdió sus ceros)
    │      │         └─ a_texto()      toma la Descripción tal cual
    │      │    Si alguna fila tiene un error, sigue con las demás y al final frena
    │      │    con un solo mensaje que las lista todas.
    │      │    → un Movimiento por fila: fecha, código, descripción, monto
    │      └─ controlar()            (motor/controlar.py) cuenta filas y suma directo
    │                                del original y las compara con lo armado; si no
    │                                cierra, frena
    │
    └─► 3. armar_dataframe()  (motor/devolver.py)
           Una fila por movimiento, con las cinco columnas. La Clase de cada
           fila la decide es_gasto() (motor/configuracion.py): "Gasto bancario"
           si su Código está en la lista del banco, "Movimiento" si no.
           → el DataFrame que recibe Conciliador
```

## Decisiones

Qué se decidió, por qué, qué se descartó y dónde puede fallar. Sirve para
defender el sistema sin abrir el código.

**1. Sin IA: todo con reglas fijas.**
Por qué: el mismo archivo da siempre el mismo resultado, y cada paso se puede
verificar y explicar. Se descartó: usar IA para leer los archivos (puede dar
resultados distintos y es difícil de auditar). Límite: si un banco cambia su
formato, el programa no se adapta solo; frena y hay que escribir la regla nueva.

**2. Quien llama dice qué es el archivo; el programa no lo confirma.**
Cada llamada recibe el banco y si es el libro del ERP; quien llama es
Conciliador, y es responsable de que el banco sea el correcto. Si el banco no
está en el config, frena y dice cuáles hay. El nombre del archivo nunca se
usa: lo pone una persona y cambia de un mes a otro. Por qué: el flujo queda
simple; confirmar el banco obligaría a cargar en el config columnas que no se
usan solo para reconocerlo. Se descartó: probar los encabezados de todos los
documentos y quedarse con el que encaja, y una lista extra de columnas "para
confirmar". Límite: si el archivo de un banco trae las columnas que usa otro,
se convierte con las reglas equivocadas sin aviso. Hoy pasa en un solo caso:
un extracto del BBVA presentado como Supervielle (el BBVA tiene Fecha,
Concepto, Detalle, Crédito y Débito). Los demás cruces frenan, porque a cada
uno le falta alguna columna.

**3. La tabla se busca por las columnas que se usan, no por número de fila ni por todos los encabezados.**
(Desde el 2026-11-04, APR-218.) Lo que tiene que traer el archivo sale de las
reglas: las columnas de Fecha, Código, Descripción, crédito y débito, más las
de "ignorar" y "seguidas". Las demás pueden cambiar, aparecer o desaparecer.
Por qué: si el banco cambia una columna que no usamos, no tiene sentido que
deje de convertir; y los bancos agregan o sacan líneas de título arriba. Se
descartó (era lo anterior): pedir en el config la lista completa de
encabezados. Si no encuentra la tabla, dice qué falta: si una fila tiene al
menos la mitad de las columnas, dice en qué fila y cuáles le faltan; si no,
que ninguna fila se parece (es otro documento). Límites: se usa la primera
fila que tenga todas las columnas y solo se lee la primera hoja. Si alguien
agrega una hoja adelante con la misma tabla (pasó con un Galicia con una hoja
"Gastos Bancarios" hecha a mano), se convierte esa hoja sin aviso (ver
PENDIENTES.md).

**4. Los montos se cuentan y se entregan en centavos enteros.**
Por qué: los decimales en una computadora tienen errores mínimos (1500000.25
puede quedar como 1500000.2499999); con enteros, sumar y comparar es exacto.
Cada monto se pasa a centavos con `Decimal`, que no arrastra ese error. La
columna se llama "Monto en centavos" para que nadie la lea como pesos. Se
descartó: entregar pesos con decimales (Conciliador tendría que redondear al
leer, como hacía con el Excel). Límite: para mostrarle un monto a una persona
hay que dividir por 100.

**5. Se controlan filas y suma contra el original; si no cierra, frena.**
El original se cuenta y se suma directo de las filas del Excel, sin pasar por
el resto del programa, y se compara con lo armado: misma cantidad de filas y
misma suma. Mirar las dos juntas atrapa también una fila perdida y otra
duplicada. Por qué: ninguna fila se puede perder en silencio. Como la Clase es
una columna y no una separación, ninguna fila se mueve después del control:
no hace falta un segundo control (la versión de dos hojas lo tenía, ver la
decisión 17). Límites: no detecta un gasto que no se reconoció (decisión 16).
Y compara contra el mismo archivo que entró: si el banco entrega un extracto
al que le faltan días, el control da bien igual. Para detectarlo hace falta
un control de saldos (saldo final − saldo inicial), que todavía no está.

**6. Se devuelve un DataFrame: no se guarda ni se borra ningún archivo.**
(Desde el 2026-11-04.) Conciliador llama a este repo y recibe el resultado en
la respuesta, como entre dos servicios. Por qué: si no hay archivos en el
medio, no hay resultados viejos que se mezclen con nuevos ni nada que borrar;
el programa hace una sola cosa, convertir, y para el mismo archivo da siempre
lo mismo. Se descartó: un Excel en `conciliacion resultados/v3/output/<mes>/<banco>/`
(era lo anterior: para no dejar un resultado viejo, borraba el anterior de ese
banco y mes, aunque viniera de otro original) y el mismo Excel devuelto en
memoria (un formato para personas entre dos programas, y vuelve el problema de
los decimales). Límites: para que una persona revise el resultado hay que
correrlo desde la terminal (muestra el resumen) o mirar el DataFrame; el
contrato con Conciliador pasa a ser la forma del DataFrame (CLAUDE.md).

**7. Se convierte de a un archivo; armar el par extracto + libro es de Conciliador.**
Por qué: la entrada queda mínima (un archivo, su banco y si es ERP). Se
descartó (era lo anterior): recorrer la carpeta de cada banco y exigir 1
extracto y 1 libro. Límite: el programa no controla que el libro del ERP sea
de la cuenta de ese banco; si se lo pasa con el banco equivocado, se convierte
igual, sin aviso (el ERP es el mismo para todos los bancos).

**8. Las fechas de otro mes salen tal cual; las controla Conciliador.**
Por qué: pueden ser válidas (un movimiento del 31 registrado el 1), y quien
sabe qué mes se concilia es Conciliador, que lo calcula con la columna Fecha.
Por eso esta etapa ya no recibe el mes. Se descartó (era lo anterior): recibir
el mes y avisar acá. La terminal muestra la primera y la última fecha, para
que una persona lo vea de un vistazo.

**9. En el libro del sistema, el Debe y Haber en pesos se toman por su lugar.**
Por qué: el libro trae dos pares con el mismo nombre, uno en pesos y otro en
dólares. El de pesos es el que está entre Descripción y Documento. Se
descartó: tomar el primero que aparece. Límite: si el sistema cambia el orden
de esas columnas, el programa frena en vez de usar los dólares.

**10. El saldo inicial se ignora; si trae monto, frena.**
Por qué: no es un movimiento. Se reconoce por el texto "Saldo Inicial". Límite:
si el sistema cambia ese texto, la fila no se ignora y el programa frena
porque no tiene monto; no pasa en silencio.

**11. Las fechas se entregan como fecha real, no como texto.**
Por qué: un texto como "01/09/2026" se lee distinto según la configuración de
la computadora; una fecha real es la misma en cualquier lado.

**12. Los archivos de un cliente nunca están en el repo.**
Por qué: no se suben a GitHub. Los originales pueden estar en cualquier
carpeta: cada llamada recibe la ruta. Las pruebas del repo usan datos
inventados; el `.gitignore` bloquea `.xls`, `.xlsx` y `.csv`.

**13. Los gastos bancarios se reconocen en esta etapa.**
Se decidió el 2026-10-27 (APR-219); antes salían sin marcar y los reconocía la
etapa 2. Cómo se reconocen está en la decisión 16 y cómo se entregan en la 17.

**14. La segunda columna es "Código", no "Concepto".**
Por qué: cada banco identifica sus gastos con una columna distinta (BBVA:
Codigo; Galicia: Grupo de Conceptos; Supervielle: Concepto; sistema: Tipo de
documento). Se toma el valor puro de esa columna, sin mezclar, con un nombre
igual para todos. Se descartó: el Concepto, que en el BBVA mezcla el tipo con
otros datos. Límites: en el BBVA el texto del Concepto (con el CUIT o la
referencia del cheque) no sale en el resultado. Si el Código llega como número
(por ejemplo, si alguien abrió y guardó el archivo en Excel), "005" pudo
quedar en 5: el archivo no se convierte y se pide bajarlo de nuevo del banco.

**15. Las reglas de todos los documentos están en un solo archivo: `configuracion.toml`.**
Una sección por banco (reglas del extracto y lista de gastos) y una para el
ERP. Por qué: agregar un banco es agregar una sección, sin tocar código; el
`motor/` no tiene nada propio de un banco. Se eligió TOML porque se lee fácil,
admite comentarios y Python lo lee sin dependencias nuevas. Se descartó: un
`reglas.py` por documento más una tabla de bancos dentro del `motor/` (era lo
anterior: había que tocar dos lugares), JSON (no admite comentarios) y Python
(es código, no configuración). Límite: el motor solo sabe leer crédito y
débito en columnas separadas; un banco con una sola columna de monto
necesitaría un cambio en el `motor/`.

**16. Los gastos bancarios se reconocen con una lista por banco en `configuracion.toml`.**
Cada banco tiene una línea `gastos` con los valores del Código que son gasto.
Una fila es gasto si su Código está en esa lista, comparado exacto ("015" no
es "15", "IVA" no es "iva"). Funciona porque el Código de cada banco ya es la
columna con la que ese banco identifica sus gastos (decisión 14). Las listas
las armó la persona que concilia. El ERP no tiene lista: no tiene gastos
bancarios. Antes de usar la lista de un banco, el programa frena si falta, si
está vacía o si tiene un código repetido, para que un error al editarla a
mano no pase en silencio.
Verificado con septiembre 2026: BBVA 836 filas (−25.702.218,68) y Supervielle
89 (−986.203,99), igual que la separación a mano y que lo medido en la etapa
2. Galicia 387 está verificado en la versión de dos hojas (2026-10-30); con
esta versión, sin verificar (falta el extracto original del banco).
Por qué: la lista es de cada banco y cambia poco; en el mismo archivo que sus
otras reglas queda versionada en git y se revisa en un PR. Se descartó: un
archivo aparte (`bancos.json` en la etapa 2, era lo anterior: la información
de un banco quedaba en dos repos), reglas por texto ("si dice IMPUESTO") que
adivinan, e IA. Límites: un gasto con un código nuevo, que no está en la
lista, no se reconoce y sale como "Movimiento", sin aviso; si el banco cambia
cómo escribe un código (un espacio, una mayúscula), pasa lo mismo.

**17. Los gastos se marcan con la columna Clase; no se separan.**
(Desde el 2026-11-04; reemplaza a la segunda hoja "Gastos bancarios" del
2026-10-30, APR-222.) Cada fila sale una sola vez, en el orden del original,
con Clase "Gasto bancario" o "Movimiento". Conciliador concilia las de
"Movimiento" y usa las de "Gasto bancario" para el control final.
Por qué: con un DataFrame, separar es una línea para quien lo recibe
(`tabla[tabla["Clase"] == "Movimiento"]`), y el resultado sigue siendo uno
solo que cierra entero contra el original. Se descartó: dos hojas o dos
DataFrames (lo de antes: hacía falta un segundo control para que ninguna fila
quedara en las dos o en ninguna) y una columna sí/no (un texto se lee mejor y
admite otra clase si algún día hace falta). Límite: si Conciliador se olvida
de filtrar, cruzaría los gastos junto con los movimientos.

**18. Los errores de fila se juntan y se informan todos juntos.**
(Desde el 2026-11-04.) Si una fila no se puede leer (una fecha mal escrita,
crédito y débito juntos, un Código que llegó como número, un importe que no
es número, una fila a ignorar con monto), el programa sigue con las demás y al
final frena con un solo mensaje que dice cuántas son y, de cada una, el número
de fila y el motivo. Muestra las primeras 20 y dice cuántas más hay. Por qué:
así se corrigen todas de una vez, en vez de ir descubriéndolas de a una. Se
descartó (era lo anterior): frenar en el primer error. Límite: igual que
antes, con un solo error no se devuelve nada.

**19. pandas es una dependencia.**
Por qué: el DataFrame de pandas es el formato estándar para pasar tablas entre
programas en Python, y es lo que espera Conciliador. Se descartó: una lista de
diccionarios (sin tipos fijos por columna) y un Excel (decisión 6). Límite: es
una dependencia más para instalar; se fija su versión en `requirements.txt`.

## Documentos disponibles

| Documento | Sección en configuracion.toml | Estado |
|---|---|---|
| Extracto BBVA | `bancos.BBVA` | Funciona |
| Extracto Galicia | `bancos.Galicia` | Funciona (sin verificar con el extracto original del banco) |
| Extracto Supervielle | `bancos.Supervielle` | Funciona |
| Libro del ERP | `erp` | Funciona (con el banco de su cuenta) |

## Agregar un banco

Agregar su sección `[bancos.<Banco>]` en `configuracion.toml`: qué columna va a
cada salida (`fecha`, `codigo`, `descripcion`, `credito`, `debito`, con el nombre
exacto del encabezado) y su lista de `gastos`. Sumar su
`documentos/<documento>/README.md` y su prueba en `pruebas/`. No hace falta
tocar el `motor/`; si hiciera falta, primero se discute.
