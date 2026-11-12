# AGENTS.md: contexto del proyecto HotelFlow (v2, estilo metabuscador)

## Qué es este proyecto

HotelFlow es un MVP de buscador y reservador de hoteles, con interfaz tipo Trivago. Es el proyecto integrador del curso "Creación de software con Agentes de IA" (Congreso Ciencias Revueltas 2026, ITS Santiago Papasquiaro). Lo desarrolla un equipo de estudiantes usando OpenCode.

Cambio de dirección: la v1 era un panel para el recepcionista. La v2 es una página donde un viajero busca hoteles, compara precios y reserva. La v1 sigue guardada en la rama/etiqueta `v1-recepcionista` y es el plan B de la demo.

## Usuario y problema

El usuario principal es el viajero. El problema: comparar hoteles, precios y ubicación en varios sitios toma tiempo y es confuso. HotelFlow muestra varios hoteles en una sola búsqueda (destino, fechas y número de huéspedes), con precio total, comparativa de precios por proveedor, filtros y mapa, y permite reservar sin dobles reservaciones.

## Alcance del MVP

Incluye:
- Catálogo de hoteles (con ubicación, estrellas, servicios y fotos) y sus habitaciones (tipo, capacidad, precio por noche).
- Búsqueda por destino, fechas y número de huéspedes, solo con habitaciones libres y con capacidad suficiente.
- Precio total por estancia y comparativa de precios por proveedor, con el mejor precio destacado.
- Filtros (precio máximo, estrellas, servicios) y orden (precio, puntuación).
- Mapa con los hoteles de los resultados.
- Detalle del hotel.
- Registro de huésped y creación, modificación y cancelación de reservaciones.
- Listado de reservaciones activas.

No incluye (no lo implementes aunque se sugiera): pagos o facturación, vuelos, paquetes, inicio de sesión o cuentas, favoritos, notificaciones, scraping o conexión a APIs reales de Booking/Expedia/etc., correos de confirmación, reportes, varios idiomas o monedas, panel de administración.

## Datos de demostración (honestidad)

Los hoteles, fotos, puntuaciones y precios por proveedor son SIMULADOS y viven en un archivo semilla (`backend/semilla.py`). La interfaz debe mostrar siempre un aviso visible: "Datos de demostración". Nunca presentes precios, reseñas o estadísticas inventadas como si fueran reales (por ejemplo "200 portales" o "ahorra 40%").

## Regla de negocio más importante

Dos reservaciones activas de la misma habitación NO pueden cruzarse en fechas. Hay cruce cuando la entrada de una es anterior a la salida de la otra Y la salida de la primera es posterior a la entrada de la otra. El día de salida cuenta como libre para una nueva entrada. Una reservación cancelada no cuenta para el cruce. Esta regla también decide qué habitaciones aparecen en la búsqueda.

Reglas de precio: noches = salida - entrada; total = noches x precio por noche de la habitación. Se calcula en el backend, nunca en el frontend. Moneda: MXN (el diseño de Stitch trae euros; hay que cambiarlo).

## Tecnología

- Python 3 con FastAPI (API), SQLite (datos) y pytest (pruebas).
- Interfaz: HTML, CSS y JavaScript sin frameworks (no uses Tailwind ni React), en `frontend/`.
- Mapa: Leaflet + OpenStreetMap, con los archivos de Leaflet copiados localmente en `frontend/vendor/`.
- Tipografías e íconos: locales o SVG propios, para que la demo funcione sin internet.

## Estructura del repositorio

- `backend/main.py`: aplicación FastAPI y endpoints.
- `backend/database.py`: conexión y creación de tablas SQLite.
- `backend/reservaciones.py`: lógica de reservaciones y regla de fechas (sin código de interfaz).
- `backend/hoteles.py`: búsqueda, filtros, precios y comparativa (sin código de interfaz).
- `backend/semilla.py`: hoteles, habitaciones y precios simulados.
- `frontend/`: interfaz (`index.html`, `styles.css`, `app.js`, `vendor/`).
- `frontend/img/`: imágenes locales y `imagenes.json` (manifiesto con textos alternativos).
- `tests/`: pruebas automatizadas.
- `documentacion/`: problema, alcance, requerimientos, decisiones y diseño. Léelos antes de planear.
- `documentacion/diseno.md`: guía de diseño (colores, tipografía, componentes). Léela en lugar del HTML completo.
- `documentacion/diseno/estilo.html`: diseño original generado con Stitch. Es solo referencia: no se sirve ni se copia tal cual.
- `documentacion/creditos-imagenes.md`: fuente y licencia de cada imagen.

## Comandos

- Instalar: `pip install -r requirements.txt`
- Ejecutar: `uvicorn backend.main:app --reload`
- Probar: `pytest`

## Reglas de trabajo para los agentes

1. Trabaja un incremento pequeño a la vez, solo el que se te pidió.
2. Antes de implementar, consulta `documentacion/requerimientos.md` para respetar requerimientos y criterios de aceptación.
3. Escribe o actualiza pruebas para todo cambio en la lógica de reservaciones, búsqueda o precios, y ejecuta `pytest` antes de dar algo por terminado.
4. Valida todas las entradas de la API (fechas válidas, salida posterior a entrada, huéspedes >= 1, campos obligatorios) y devuelve mensajes de error claros.
5. La lógica de negocio va en `backend/reservaciones.py` y `backend/hoteles.py`, no en los endpoints ni en el frontend.
6. Código simple y legible, con nombres en español para el dominio (hotel, habitación, huésped, reservación, tarifa).
7. No borres archivos ni cambies la estructura sin avisar antes.
8. Nunca escribas claves, contraseñas ni datos personales reales en el código. No crees ni versiones archivos `.env`.
9. No modifiques los archivos de `documentacion/` salvo que se pida explícitamente (excepto `creditos-imagenes.md`, que mantiene el subagente de imágenes).
10. Al terminar, explica en pocas líneas qué cambiaste y por qué, para que el equipo pueda revisarlo y entenderlo.
11. No hagas commits ni cambies de rama: eso lo hace el equipo.

## Equipo de agentes y cuándo delegar

- Planificador (modo plan, solo lectura): divide cada incremento en pasos antes de construir.
- Constructor (modo build): implementa backend, pruebas y la conexión del frontend con la API.
- `@disenador` (subagente): crea y modifica HTML, CSS y la apariencia de `frontend/`, siguiendo `documentacion/diseno.md`. No toca el backend.
- `@imagenes` (subagente): consigue, optimiza y registra las imágenes en `frontend/img/`. No toca código.
- `@revisor` (subagente, solo lectura): revisa los cambios contra requerimientos, regla de fechas, validaciones, pruebas, diseño y accesibilidad.
- `@probador` (subagente, ejecuta pruebas): corre `pytest` y reporta.

Reparto de responsabilidades: si un cambio toca el diseño y la lógica, primero el Constructor entrega el endpoint, luego `@disenador` arma la pantalla, `@imagenes` aporta los recursos, y al final `@revisor` y `@probador`.

## Reglas de diseño (para @disenador y el Constructor)

- Sigue `documentacion/diseno.md`: mismos colores, tipografías y componentes en todas las pantallas.
- Diseño responsive (celular y computadora), con estados de carga, error, éxito y "sin resultados".
- Botones y campos con etiquetas, contraste suficiente y navegación con teclado.
- No incluyas enlaces o botones que aparenten funcionar y no hagan nada (Vuelos, Paquetes, Mi cuenta): quítalos o muéstralos desactivados.
- Todo el texto de la interfaz en español.

## Reglas para imágenes (para @imagenes)

- Solo imágenes propias, generadas con herramientas del equipo, o con licencia libre (Unsplash, Pexels, Wikimedia). Registra fuente, autor y licencia en `documentacion/creditos-imagenes.md`.
- Los hoteles son ficticios: no uses fotos de hoteles reales presentándolas como otro hotel.
- Guarda las imágenes en `frontend/img/` en formato `.webp` o `.jpg`, de máximo 200 KB, con nombre `hotel-<slug>-<n>.webp`. No dependas de enlaces externos.
- Cada imagen tiene texto alternativo en `frontend/img/imagenes.json`.
- Incluye un SVG de reemplazo (`frontend/img/sin-imagen.svg`) para cuando falte una foto.
