# HotelFlow: planeación (Fase 3, versión 2)

Este documento se coloca en `documentacion/requerimientos.md`. Reemplaza a la versión 1 (panel de recepcionista), que queda en la rama `v1-recepcionista`.

## 1. Requerimientos funcionales

- RF-01: El sistema guarda hoteles (nombre, ciudad, dirección, latitud, longitud, estrellas, puntuación, servicios, descripción) y permite consultarlos.
- RF-02: Cada hotel tiene habitaciones (número, tipo, capacidad de personas, precio por noche).
- RF-03: El sistema busca hoteles por destino, fecha de entrada, fecha de salida y número de huéspedes, y devuelve solo hoteles con al menos una habitación libre y con capacidad suficiente.
- RF-04: Para cada hotel encontrado, el sistema muestra el precio total de la estancia (noches x precio por noche) y la habitación disponible más barata.
- RF-05: El sistema muestra una comparativa de precios por proveedor (datos simulados) y destaca el mejor precio.
- RF-06: El sistema permite filtrar por precio máximo, estrellas y servicios, y ordenar por precio o por puntuación.
- RF-07: El sistema muestra en un mapa los hoteles de los resultados.
- RF-08: El sistema muestra el detalle de un hotel: fotos, servicios y habitaciones disponibles para las fechas buscadas.
- RF-09: El sistema permite registrar un huésped (nombre, teléfono, correo opcional).
- RF-10: El sistema permite crear una reservación asociando huésped, habitación, fechas y número de personas.
- RF-11: El sistema rechaza una reservación si la habitación ya está reservada en fechas que se cruzan o si la capacidad no alcanza.
- RF-12: El sistema permite modificar fechas o habitación de una reservación, con la misma validación de RF-11.
- RF-13: El sistema permite cancelar una reservación, y la habitación queda libre para esas fechas.
- RF-14: El sistema muestra el listado de reservaciones activas.

## 2. Requerimientos no funcionales

- RNF-01 (Usabilidad): un viajero puede buscar y reservar en menos de 2 minutos sin capacitación.
- RNF-02 (Confiabilidad): nunca deben existir dos reservaciones activas de la misma habitación con fechas cruzadas.
- RNF-03 (Validación): todas las entradas se validan (fechas válidas, salida posterior a entrada, huéspedes >= 1, campos obligatorios) y los errores se muestran con mensajes claros.
- RNF-04 (Portabilidad): el proyecto se instala y ejecuta en otra computadora siguiendo solo el README.
- RNF-05 (Seguridad básica): no se guardan secretos ni datos reales de personas en el repositorio.
- RNF-06 (Interfaz): la interfaz muestra estados de carga, error, éxito y sin resultados, y se ve bien en computadora y celular.
- RNF-07 (Honestidad de datos): hoteles, precios por proveedor y puntuaciones son simulados y la interfaz lo indica con el aviso "Datos de demostración".
- RNF-08 (Imágenes): toda imagen es local, tiene licencia libre o propia, texto alternativo y crédito registrado.
- RNF-09 (Demo sin internet): la aplicación funciona sin conexión (mapa, fuentes e íconos incluidos localmente, salvo los mosaicos del mapa, para los que hay captura de respaldo).
- RNF-10 (Consistencia visual): todas las pantallas siguen `documentacion/diseno.md`.
- RNF-11 (Rendimiento): una búsqueda responde en menos de 1 segundo con los datos semilla.

## 3. Historias de usuario y criterios de aceptación

**HU-01. Como viajero, quiero buscar hoteles por destino, fechas y número de personas para ver mis opciones.**
- Cuando ingreso destino, entrada, salida y huéspedes, veo hoteles con habitaciones libres y capacidad suficiente.
- Si la salida es anterior o igual a la entrada, o los huéspedes son menos de 1, veo un mensaje de error y no se ejecuta la búsqueda.
- Si no hay resultados, veo un mensaje claro que sugiere cambiar fechas o filtros.

**HU-02. Como viajero, quiero ver el precio total y comparar proveedores para elegir la mejor oferta.**
- Cada resultado muestra precio por noche, total de la estancia y precios por proveedor.
- El proveedor más barato aparece destacado como "Mejor precio".

**HU-03. Como viajero, quiero filtrar y ordenar los resultados para encontrar lo que se ajusta a mi presupuesto.**
- Al fijar un precio máximo o estrellas, solo veo hoteles que cumplen.
- Al ordenar por precio, la lista queda del más barato al más caro.

**HU-04. Como viajero, quiero ver los hoteles en un mapa para elegir por ubicación.**
- El mapa muestra un marcador por hotel de los resultados actuales.
- Al elegir un marcador veo el nombre y el precio del hotel.

**HU-05. Como viajero, quiero ver el detalle de un hotel para decidir si reservo.**
- Veo fotos, servicios, ubicación y las habitaciones libres para mis fechas, con su precio total.

**HU-06. Como viajero, quiero reservar una habitación para asegurarla.**
- Cuando capturo nombre y teléfono y elijo una habitación libre, la reservación queda registrada como activa y veo una confirmación.
- Si falta un campo obligatorio, el sistema lo indica y no guarda.
- Si la habitación ya está reservada en fechas que se cruzan, el sistema rechaza la reservación y explica el motivo.

**HU-07. Como viajero, quiero modificar una reservación para atender cambios.**
- Cuando cambio las fechas a un rango libre, la reservación se actualiza.
- Si el nuevo rango se cruza con otra reservación de esa habitación, se rechaza y la reservación original no cambia.

**HU-08. Como viajero, quiero cancelar una reservación para liberar la habitación.**
- Cuando cancelo, deja de aparecer en las activas y la habitación vuelve a estar disponible en esas fechas.

**HU-09. Como viajero, quiero ver mis reservaciones activas.**
- El listado muestra hotel, habitación, huésped, fechas y total de cada reservación activa, y no muestra las canceladas.

Regla de fechas: dos reservaciones de la misma habitación se cruzan cuando la entrada de una es anterior a la salida de la otra y la salida de la primera es posterior a la entrada de la otra. El día de salida cuenta como libre para una nueva entrada.

## 4. Arquitectura

Aplicación web de tres capas:

- Interfaz: HTML, CSS y JavaScript sin frameworks (buscador, resultados, mapa con Leaflet, detalle y formulario de reservación).
- API (FastAPI): endpoints para hoteles (búsqueda y detalle), huéspedes y reservaciones. Toda la lógica vive en `backend/hoteles.py` y `backend/reservaciones.py`.
- Datos (SQLite): tablas hoteles, habitaciones, tarifas_proveedor (precios simulados), huéspedes y reservaciones. Los datos de demostración se cargan desde `backend/semilla.py`.

Endpoints previstos (el Planificador puede ajustarlos):
- `GET /hoteles?destino=&entrada=&salida=&huespedes=&precio_max=&estrellas=&orden=`
- `GET /hoteles/{id}?entrada=&salida=&huespedes=`
- `POST /huespedes`
- `POST /reservaciones`, `PUT /reservaciones/{id}`, `DELETE /reservaciones/{id}` (cancela)
- `GET /reservaciones` (activas)

## 5. Roles de agentes y subagentes (OpenCode)

- **Planificador** (modo plan, solo lectura): divide cada incremento en pasos. No modifica archivos.
- **Constructor** (modo build): implementa backend, pruebas y conexión del frontend con la API, un incremento a la vez.
- **@disenador** (subagente, edita solo `frontend/`, sin imágenes ni bash): convierte el diseño de Stitch a HTML/CSS planos y mantiene la consistencia visual.
- **@imagenes** (subagente, edita solo `frontend/img/` y los créditos): consigue, optimiza y registra las imágenes.
- **@revisor** (subagente, solo lectura): revisa código, diseño, imágenes y pruebas contra este documento.
- **@probador** (subagente, ejecuta pruebas, sin editar): corre `pytest` y reporta.

## 6. Plan de incrementos

1. Datos: tablas y semilla (hoteles, habitaciones, tarifas por proveedor).
2. API de búsqueda con disponibilidad, capacidad, precio total, filtros y orden, con pruebas.
3. Pantalla de búsqueda y resultados (@disenador, @imagenes).
4. Comparativa de precios y mejor precio.
5. Mapa con marcadores.
6. Detalle del hotel y reservación (reutiliza la lógica de la v1).
7. Modificar, cancelar y listado de activas.
8. Pulido, validación en celular, demo sin internet.

## 7. Plan de pruebas

**Automatizadas:**
- Reservar una habitación libre funciona.
- Reservar con fechas que se cruzan se rechaza (cruce total, parcial y contenido).
- Reservar con salida el mismo día de otra entrada funciona.
- Cancelar libera la habitación.
- Modificar a fechas cruzadas se rechaza y no altera la reservación original.
- Fechas inválidas y huéspedes menores a 1 devuelven error.
- La búsqueda no devuelve habitaciones ocupadas ni con capacidad insuficiente.
- El precio total es noches x precio por noche.
- Filtros y orden devuelven lo esperado.
- El mejor precio de la comparativa es el más bajo.

**Manuales** (matriz de la Fase 5):
- Flujo completo: buscar, filtrar, ver mapa, ver detalle, reservar, ver en activas, cancelar.
- Caso de error: doble reservación y fechas inválidas.
- Búsqueda sin resultados.
- Revisión de interfaz en computadora y celular, y demo sin internet.
- Que otra persona ejecute el proyecto solo con el README.
