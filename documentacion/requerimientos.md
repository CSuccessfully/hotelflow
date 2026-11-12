# HotelFlow: planeación (Fase 3)

Este documento se coloca en `documentacion/requerimientos.md` dentro del repositorio.

## 1. Requerimientos funcionales

- RF-01: El sistema permite registrar habitaciones (número, tipo, capacidad) y consultarlas.
- RF-02: El sistema permite consultar qué habitaciones están disponibles para un rango de fechas.
- RF-03: El sistema permite registrar huéspedes (nombre, teléfono, correo opcional).
- RF-04: El sistema permite crear una reservación asociando un huésped, una habitación y un rango de fechas.
- RF-05: El sistema rechaza una reservación si la habitación ya está reservada en fechas que se cruzan.
- RF-06: El sistema permite modificar las fechas o la habitación de una reservación, con la misma validación de RF-05.
- RF-07: El sistema permite cancelar una reservación, y la habitación queda libre para esas fechas.
- RF-08: El sistema muestra el listado de reservaciones activas.

## 2. Requerimientos no funcionales

- RNF-01 (Usabilidad): el recepcionista debe poder crear una reservación en menos de 1 minuto sin capacitación.
- RNF-02 (Confiabilidad): nunca deben existir dos reservaciones activas de la misma habitación con fechas cruzadas.
- RNF-03 (Validación): todas las entradas se validan (fechas válidas, salida posterior a entrada, campos obligatorios) y los errores se muestran con mensajes claros.
- RNF-04 (Portabilidad): el proyecto se instala y ejecuta en otra computadora siguiendo solo el README.
- RNF-05 (Seguridad básica): no se guardan secretos ni datos reales de personas en el repositorio.
- RNF-06 (Interfaz): la interfaz muestra estados de carga, error y éxito, y se ve bien en pantallas de computadora y de celular.

## 3. Historias de usuario y criterios de aceptación

**HU-01. Como recepcionista, quiero consultar la disponibilidad por fechas para ofrecer una habitación al huésped.**
- Dado que hay habitaciones registradas, cuando ingreso fecha de entrada y de salida, entonces veo solo las habitaciones libres en ese rango.
- Si la salida es anterior o igual a la entrada, veo un mensaje de error y no se ejecuta la búsqueda.

**HU-02. Como recepcionista, quiero registrar a un huésped para asociarlo a su reservación.**
- Cuando capturo nombre y teléfono, el huésped queda guardado y disponible para reservar.
- Si falta un campo obligatorio, el sistema lo indica y no guarda.

**HU-03. Como recepcionista, quiero crear una reservación para asegurar la habitación al huésped.**
- Cuando elijo huésped, habitación libre y fechas, la reservación queda registrada como activa.
- Si la habitación ya está reservada en fechas que se cruzan, el sistema rechaza la reservación y explica el motivo.

**HU-04. Como recepcionista, quiero modificar una reservación para atender cambios del huésped.**
- Cuando cambio las fechas a un rango libre, la reservación se actualiza.
- Si el nuevo rango se cruza con otra reservación de esa habitación, se rechaza y la reservación original no cambia.

**HU-05. Como recepcionista, quiero cancelar una reservación para liberar la habitación.**
- Cuando cancelo una reservación, deja de aparecer en las activas y la habitación vuelve a estar disponible en esas fechas.

**HU-06. Como recepcionista, quiero ver las reservaciones activas para saber el estado del hotel.**
- El listado muestra huésped, habitación y fechas de cada reservación activa, y no muestra las canceladas.

**HU-07. Como recepcionista, quiero registrar habitaciones para que el sistema conozca el inventario del hotel.**
- Cuando capturo número y tipo, la habitación queda guardada. No se permiten dos habitaciones con el mismo número.

Regla de fechas: dos reservaciones de la misma habitación se cruzan cuando la entrada de una es anterior a la salida de la otra y la salida de la primera es posterior a la entrada de la otra. El día de salida cuenta como libre para una nueva entrada.

## 4. Arquitectura inicial

Se propone una aplicación web de tres capas, simple y fácil de ejecutar:

- Interfaz: páginas HTML con JavaScript que usa el recepcionista en el navegador.
- API: un backend con endpoints para habitaciones, huéspedes y reservaciones, donde vive toda la lógica y la validación (incluida la regla de fechas).
- Datos: una base de datos SQLite con tres tablas (habitaciones, huéspedes, reservaciones), donde cada reservación apunta a un huésped y a una habitación y tiene un estado (activa o cancelada).

Tecnología sugerida: Python con FastAPI para la API, SQLite para los datos y HTML/JS para la interfaz. Es una propuesta y el equipo puede cambiarla, pero debe quedar registrada en el README.

## 5. Roles de agentes y subagentes (OpenCode)

El equipo trabaja con OpenCode en la terminal de VS Code, usando el modo plan para pensar y el modo build para implementar. Los roles propuestos, cada uno con permisos acordes a su función:

- **Planificador** (modo plan, solo lectura): analiza el contexto, propone cómo resolver cada historia y divide el trabajo en pasos. No modifica archivos.
- **Constructor** (modo build, con permiso de editar): implementa una historia a la vez, en incrementos pequeños, siguiendo el plan y `AGENTS.md`.
- **Revisor y probador** (subagente, solo lectura y ejecución de pruebas): revisa los cambios, ejecuta las pruebas y reporta fallos. No edita el código, para que su revisión sea independiente.

El `AGENTS.md` del repositorio describe el problema, el alcance, la arquitectura, la regla de fechas, las convenciones de código y qué no tocar. Es el contexto que comparten todos los agentes. Los equipos deben poder explicar qué hizo el agente y qué decidió el equipo.

## 6. Plan de pruebas

**Automatizadas** (sobre la lógica de reservaciones y la API):
- Reservar una habitación libre funciona.
- Reservar con fechas que se cruzan se rechaza (cruce total, parcial y contenido).
- Reservar con salida el mismo día de otra entrada funciona (el día de salida es libre).
- Cancelar libera la habitación.
- Modificar a fechas cruzadas se rechaza y no altera la reservación original.
- Fechas inválidas (salida antes de entrada) devuelven error.

**Manuales** (matriz que se completa en la Fase 5):
- Flujo completo: buscar disponibilidad, registrar huésped, reservar, ver en activas, cancelar.
- Caso de error: intentar una doble reservación y ver el mensaje.
- Revisión de interfaz en computadora y celular, con estados de carga, error y éxito.
- Que otra persona ejecute el proyecto solo con el README.
