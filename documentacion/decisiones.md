# Decisiones del proyecto

- Tecnología: Python con FastAPI, SQLite y HTML/JS. Motivo: simple y fácil de ejecutar.
- Regla de fechas: el día de salida cuenta como libre para una nueva entrada.
- 12 nov 2026 - Cambio de dirección: el profesor pidió que HotelFlow sea un buscador de hoteles tipo Trivago (varios hoteles, precios, huéspedes, mapa). Se pasa del panel del recepcionista al viajero. Se conserva la v1 en la rama/etiqueta `v1-recepcionista` como plan B.
- Se mantiene el motor de reservaciones y la regla de fechas de la v1; ahora también decide la disponibilidad en la búsqueda.
- Los hoteles, fotos y precios por proveedor son simulados (semilla). No se conecta a Booking, Expedia ni otros servicios. La interfaz muestra "Datos de demostración". Motivo: no hay acceso a APIs reales y hay que ser honestos con los límites.
- El diseño base se generó con Stitch y se guarda como referencia en `documentacion/diseno/estilo.html`. Se reescribe en HTML y CSS planos: no se usa Tailwind por la regla de "sin frameworks" y porque su CDN exige internet.
- Mapa con Leaflet y OpenStreetMap, con Leaflet copiado localmente. Motivo: no requiere clave de API.
- Las imágenes y fuentes son locales, con licencia libre y créditos registrados. Motivo: demo sin internet y respeto a licencias.
- Se agregan dos subagentes: `@disenador` (edita solo `frontend/`) y `@imagenes` (edita solo `frontend/img/` y los créditos). `@revisor` y `@probador` se actualizan para revisar diseño, imágenes, precios y búsqueda.
- Alcance recortado: se quitan del diseño Vuelos, Paquetes, Ofertas de temporada, cuenta de usuario, favoritos y notificaciones.
- Moneda: MXN (pendiente de confirmar por el equipo).
