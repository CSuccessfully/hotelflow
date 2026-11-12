# HotelFlow

Sistema de reservaciones hoteleras para el proyecto integrador del curso
**Creación de software con Agentes de IA**.

## Integrantes del equipo

- Astrid
- Grecia
- Martín
- Ángel

## Problema que resuelve

HotelFlow ayuda al viajero a buscar hoteles por destino, fechas y número de huéspedes, comparar precios y ubicación en un mapa, y reservar sin dobles reservaciones de una misma habitación.

> Nota: los hoteles, fotos y precios por proveedor son datos de demostración, no reales.

## Alcance

### Incluye

- Catálogo de hoteles y habitaciones.
- Búsqueda por destino, fechas y huéspedes, con solo habitaciones libres y con capacidad suficiente.
- Precio total y comparativa de precios por proveedor (simulada).
- Filtros, orden y mapa de resultados.
- Detalle del hotel.
- Registro de huéspedes y creación, modificación y cancelación de reservaciones.
- Listado de reservaciones activas.

### No incluye

- Pagos ni facturación.
- Vuelos ni paquetes.
- Cuentas, inicio de sesión, favoritos ni notificaciones.
- Conexión a servicios reales de reservas.
- Correos de confirmación.
- Reportes avanzados.

## Tecnologías (agregar)

- Leaflet y OpenStreetMap para el mapa (archivos locales).

## Estructura del repositorio (cambios)

```text
hotelflow/
├── .opencode/agents/        # Subagentes: disenador, imagenes, revisor, probador
├── backend/
│   ├── hoteles.py           # Búsqueda, filtros, precios y comparativa
│   └── semilla.py           # Hoteles, habitaciones y precios de demostración
├── frontend/
│   ├── img/                 # Imágenes locales e imagenes.json
│   └── vendor/              # Leaflet y fuentes locales
└── documentacion/
    ├── diseno.md            # Guía de diseño
    ├── diseno/estilo.html   # Diseño original de Stitch (referencia)
    └── creditos-imagenes.md # Fuente y licencia de cada imagen
```

## Herramientas de IA y forma de trabajo (reemplaza la lista de agentes)

El equipo utiliza **OpenCode** en la terminal de VS Code, además de **Stitch** para generar el diseño base:

- **Modo plan:** analiza el contexto y divide cada incremento. No modifica archivos.
- **Modo build:** implementa un incremento pequeño siguiendo el plan y `AGENTS.md`.
- **Subagente `@disenador`:** crea y modifica la interfaz en `frontend/` siguiendo `documentacion/diseno.md`.
- **Subagente `@imagenes`:** consigue y registra las imágenes en `frontend/img/`.
- **Subagente `@revisor`:** revisa cambios, diseño, imágenes y pruebas. No modifica archivos.
- **Subagente `@probador`:** ejecuta `pytest` e informa los resultados. No modifica archivos.
