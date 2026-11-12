# HotelFlow: definición del alcance (Fase 2)

## Usuarios principales

El usuario principal es el recepcionista de un hotel general. Es quien registra y consulta las habitaciones, atiende a los huéspedes y crea, modifica o cancela las reservaciones desde el mostrador. En esta versión no habrá otros tipos de usuario, como huéspedes que reserven por su cuenta o administradores con permisos distintos.

## Problema en una frase

Los recepcionistas de hoteles necesitan una forma rápida y confiable de consultar disponibilidad y gestionar reservaciones, porque hacerlo a mano provoca errores como dobles reservaciones.

## Solución propuesta

HotelFlow es una aplicación sencilla para el recepcionista. Le permite ver qué habitaciones están disponibles en unas fechas dadas, registrar al huésped y crear la reservación, y después modificarla, cancelarla o consultar todas las reservaciones activas. El sistema evita por sí mismo que una misma habitación se reserve dos veces en fechas que se cruzan.

## Qué incluye y qué no

El MVP incluye el registro y la consulta de habitaciones, el control de disponibilidad por fechas, el registro de huéspedes, la creación, modificación y cancelación de reservaciones, y el listado de reservaciones activas. El flujo principal que se va a demostrar es buscar disponibilidad, reservar y cancelar.

El MVP no incluye pagos ni facturación, reservaciones hechas por los propios huéspedes por internet, manejo de varios hoteles, tarifas por temporada ni descuentos, envío de correos o mensajes de confirmación, ni reportes avanzados. Tampoco incluye inicio de sesión con roles, que queda como mejora futura.

## Supuestos y riesgos

Se asume que el hotel tiene un número fijo de habitaciones y que cada reservación corresponde a una sola habitación y a un solo huésped titular. También se asume que el recepcionista usa la aplicación desde una computadora, con los datos guardados de forma local o en una base de datos sencilla.

El principal riesgo es el tiempo, porque el curso termina pronto y hay que mantener el alcance pequeño. Otro riesgo es la lógica de fechas: una validación mal hecha puede permitir dobles reservaciones, que es justo el problema que se quiere resolver, así que debe probarse con cuidado. Por último, como parte de la evidencia del problema sigue pendiente, conviene confirmarla antes de la presentación.

## Criterios de éxito

El MVP se considera exitoso si el recepcionista puede crear una reservación completa en un solo flujo sin errores, si el sistema rechaza una reservación que se cruza en fechas con otra de la misma habitación, si una cancelación libera la habitación para esas fechas, y si el listado de reservaciones activas refleja siempre el estado real. Además, otra persona debe poder ejecutar el proyecto siguiendo únicamente las instrucciones del README.
