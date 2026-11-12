# HotelFlow: definición del alcance (Fase 2, versión 2)

## Usuarios principales

El usuario principal es el viajero que quiere encontrar y reservar un hotel. En esta versión no habrá cuentas de usuario, roles ni panel de administración. Los hoteles se cargan desde datos de demostración.

## Problema en una frase

Los viajeros necesitan una forma rápida y clara de comparar hoteles, precios y ubicación para unas fechas y un número de personas, y reservar sin errores como dobles reservaciones.

## Solución propuesta

HotelFlow es una página web estilo metabuscador. El viajero indica destino, fechas y número de huéspedes, y ve varios hoteles con precio total, comparativa de precios por proveedor, filtros y un mapa. Puede abrir el detalle de un hotel, reservar una habitación, modificar o cancelar su reservación y consultar las reservaciones activas. El sistema evita por sí mismo que una misma habitación se reserve dos veces en fechas que se cruzan.

## Qué incluye y qué no

Incluye: catálogo de hoteles y habitaciones, búsqueda por destino, fechas y huéspedes, precio total, comparativa de precios por proveedor (simulada), filtros y orden, mapa, detalle del hotel, registro de huésped, creación, modificación y cancelación de reservaciones, y listado de reservaciones activas. El flujo a demostrar es buscar, comparar, reservar y cancelar.

No incluye: pagos o facturación, vuelos, paquetes, ofertas de temporada, cuentas o inicio de sesión, favoritos, notificaciones, conexión a servicios reales de reservas, correos de confirmación, reportes avanzados, varios idiomas o monedas.

## Supuestos y riesgos

Se asume que los datos (hoteles, fotos, precios por proveedor) son simulados y que cada reservación corresponde a una habitación y un huésped titular. Se usa una sola moneda.

El principal riesgo es el tiempo: el alcance creció y hay que construir por incrementos pequeños, con la v1 como plan B. Otro riesgo es la lógica de fechas, que ahora también define la disponibilidad en la búsqueda y debe probarse con cuidado. Un tercer riesgo es depender de internet en la demo (mapa, fuentes, imágenes), por eso todo se guarda localmente.

## Criterios de éxito

El MVP se considera exitoso si el viajero puede buscar, comparar y reservar en un solo flujo sin errores, si la búsqueda no muestra habitaciones ocupadas ni sin capacidad, si el sistema rechaza una reservación que se cruza con otra de la misma habitación, si una cancelación libera la habitación, y si el listado de activas refleja el estado real. Además, otra persona debe poder ejecutar el proyecto siguiendo solo el README, y la demo debe funcionar sin internet.
