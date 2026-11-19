# Pendientes

## Abierto (en orden de prioridad)

1. **Adaptar Conciliador al contrato del 2026-11-04.** Llamar a
   `convertir_documento()` una vez por archivo en vez de leer los Excel de
   `output/`; cruzar solo las filas con Clase "Movimiento"; tomar el monto en
   centavos sin redondear; controlar las fechas de otro mes (esta etapa ya no
   lo hace); sacar `bancos.json` y `motor/gastos.py` (APR-226); y copiar el
   bloque del contrato a su CLAUDE.md (APR-227). Hasta entonces Conciliador no
   puede usar esta versión. Ojo: acá figuraba como hecho el 2026-11-03 que
   Conciliador aceptaba las dos hojas (APR-224), pero en el GitHub de
   Conciliador no hay ningún commit de eso; queda reemplazado por este punto.
2. **Frenar si el archivo trae más de una hoja.** Hoy se lee solo la primera,
   sin aviso. Pasó con un Galicia con una hoja "Gastos Bancarios" hecha a mano
   adelante de "Movimientos": se convirtieron 3 filas en vez de 500. Pasa lo
   mismo con las planillas de conciliación hechas a mano.
3. **Verificar el Galicia con un extracto bajado directo del banco.** La copia
   de `input/2026-09` tiene dos hojas (ver el punto 2). Con el DataFrame, el
   extracto del Galicia está sin verificar.
4. **Pruebas con archivos reales.** Una prueba genérica en el repo que lea, de
   afuera del repo, una lista de referencia por mes (archivo, banco, si es ERP,
   filas, suma, gastos) y la compare. Si los archivos no están, se saltea. Así
   la referencia de septiembre se controla sola en cada `pytest`.
5. **Controlar que el libro del ERP sea de la cuenta del banco indicado.** Hoy
   no se controla. Se podría usar la columna "Cuenta" del libro.
6. **Control de saldos** (saldo final − saldo inicial) para detectar un
   extracto incompleto. El Supervielle trae la columna Saldo.
7. **Bancos con una sola columna de monto** (con signo, o importe + D/C).
   Necesita un cambio en el `motor/`. Esperar a tener un extracto real.
8. **Avisar los códigos de gasto nunca vistos.** Si el banco empieza a cobrar
   un gasto con un código que no está en la lista `gastos` de su banco, sale
   como "Movimiento" sin aviso (decisión 16). Idea: avisar los códigos que
   nunca se vieron; para eso habría que guardar también la lista de los
   códigos que no son gasto. Viene del Conciliador (APR-226).
9. **Bancos nuevos** (APR-221): esperar los extractos que tiene que mandar el
   cliente.

## Hecho

- 2026-11-04 — Verificación de formato (APR-218). El config pide solo las
  columnas que se usan (se saca la lista `encabezados`); si falta una, el
  error dice cuál y en qué fila, o que ninguna fila se parece. Los errores de
  fila se juntan y se informan todos en un solo mensaje (los primeros 20 y
  cuántos más). Se decide no confirmar el banco con columnas extra: un
  extracto del BBVA presentado como Supervielle se convierte sin aviso
  (decisión 2). Verificado con septiembre: la referencia no cambia.
- 2026-11-04 — Se devuelve un DataFrame (Fecha · Código · Descripción · Monto
  en centavos · Clase) en vez de escribir Excel en carpetas. Los gastos se
  marcan con la columna Clase en vez de ir a una hoja aparte; se mantienen la
  lista y el control de la lista de APR-219. Se sacan la escritura del Excel,
  las carpetas, el borrado del resultado anterior y el mes. pandas pasa a ser
  dependencia. Se incorporan a `documento-unico` las ramas `gastos-bancarios`,
  `separar-gastos` y `controlar-separacion`. Verificado con septiembre: BBVA
  (extracto 1.445 filas −30.550.126,57, 836 gastos −25.702.218,68; libro 529),
  Supervielle (extracto 172 filas 856.523,72, 89 gastos −986.203,99; libro
  65) y libro del Galicia (99): todo igual a la referencia. Extracto del
  Galicia, sin verificar.
- 2026-11-03 — El contrato queda igual en los dos CLAUDE.md, con fecha
  (APR-227).
- 2026-10-30 — Rama `controlar-separacion` (APR-223): la separación pasa a
  hacerse antes del control, y el control compara el original contra lo
  armado y contra Movimientos + Gastos, en filas y suma, diciendo en qué paso
  falló. Verificado con septiembre: los resultados son idénticos a los del
  APR-222. (Reemplazado el 2026-11-04: ya no hay dos hojas.)
- 2026-10-30 — Rama `separar-gastos` (APR-222): el extracto de un banco sale
  con dos hojas, "Movimientos" y "Gastos bancarios" (siempre las dos); el
  libro del ERP con una. Verificado con septiembre: mismas filas que antes
  repartidas en las dos hojas, en orden, y la hoja de gastos igual a la
  separación a mano. (Reemplazado el 2026-11-04 por la columna Clase.)
- 2026-10-28 — Rama `gastos-bancarios` (APR-219): cada banco tiene su lista
  `gastos` en `configuracion.toml`; se controla que no falte, no esté vacía
  y no tenga repetidos, y se reconoce un gasto comparando el Código exacto.
  Verificado con septiembre: BBVA 836, Galicia 387, Supervielle 89.
- 2026-10-26 — Rama `documento-unico`: cada corrida convierte un archivo
  (mes, banco, ruta y `--erp`). Las reglas pasan a `configuracion.toml`. Se
  sacan el recorrido de carpetas y el reconocimiento entre todos los
  documentos. Referencia de septiembre verificada en BBVA (extracto y libro),
  Supervielle (extracto y libro) y libro del Galicia.
