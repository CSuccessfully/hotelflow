# HotelFlow: guía de diseño

Resumen del diseño generado con Stitch (`documentacion/diseno/estilo.html`). Los agentes deben usar esta guía y consultar el HTML original solo por fragmentos.

## Identidad

- Nombre en pantalla: HotelFlow (el diseño original dice "hotelcompare"; hay que cambiarlo).
- Tono: claro, limpio, fondo azul muy claro, tarjetas blancas, énfasis en el precio.
- Aviso fijo y visible: "Datos de demostración".

## Colores (variables CSS)

| Variable | Valor | Uso |
|---|---|---|
| --color-primario | #004e99 | Títulos de marca, enlaces, botones principales |
| --color-primario-contenedor | #0a66c2 | Botón buscar, elementos activos |
| --color-acento | #ff6840 | Etiquetas de ahorro y llamadas a la acción secundarias |
| --color-exito | #005b33 | "Mejor precio" y confirmaciones |
| --color-error | #ba1a1a | Mensajes de error |
| --color-fondo | #f9f9ff | Fondo de página |
| --color-superficie | #ffffff | Tarjetas y cabecera |
| --color-superficie-suave | #f0f3ff / #e7eeff | Secciones alternas |
| --color-texto | #111c2d | Texto principal |
| --color-texto-suave | #414752 | Texto secundario |
| --color-borde | #c1c6d4 | Bordes |

## Tipografía

- Títulos: Plus Jakarta Sans (700). Cuerpo y etiquetas: Inter.
- Escala: precio destacado 28px/800, título de página 32-48px, título de sección 22px, texto 14-16px, etiquetas 11-12px.
- Las fuentes se guardan localmente en `frontend/vendor/fuentes/`; si no cargan, usar la pila `system-ui, sans-serif`.

## Espaciado y forma

- Contenedor máximo 1280px, margen lateral 2rem (1rem en celular).
- Espacios: 0.25, 0.5, 1, 1.5 y 2.5rem. Bordes redondeados: 0.25rem, 0.5rem y 0.75rem.
- Sombra suave en cabecera y tarjetas.

## Estructura de la página principal

1. Cabecera fija: logotipo y nombre, menú (solo "Hoteles" y "Mis reservaciones").
2. Hero con el buscador: destino, fechas (entrada y salida), huéspedes y botón "Buscar".
3. Resultados: tarjetas de hotel y filtros (precio máximo, estrellas, servicios) con selector de orden.
4. Mapa con marcadores de los resultados.
5. Destinos populares (opcional, como atajos que llenan el campo de destino).
6. Pie de página.

Secciones del diseño original que NO se implementan: bloque de ahorro garantizado, testimonios, preguntas frecuentes, logos de proveedores reales, Vuelos, Paquetes, Mi cuenta, favoritos y notificaciones. Si se quiere una sección informativa, debe decir la verdad (datos de demostración).

## Componentes

- **Buscador**: tres campos con etiqueta visible y botón; errores en línea.
- **Tarjeta de hotel**: foto, nombre, estrellas, puntuación, ubicación, servicios (máximo 3 etiquetas), tabla corta de precios por proveedor con "Mejor precio" en verde, precio por noche y total, botón "Ver hotel".
- **Filtros**: controles agrupados, con botón "Limpiar".
- **Mapa**: marcador por hotel con ventana emergente (nombre y precio).
- **Detalle de hotel**: galería, servicios, lista de habitaciones libres con total y botón "Reservar".
- **Formulario de reservación**: nombre, teléfono, correo opcional, resumen (hotel, habitación, fechas, huéspedes, total) y botón "Confirmar reservación".
- **Estados**: carga (indicador), error (rojo, con explicación), éxito (verde, con resumen) y sin resultados (mensaje y sugerencia).

## Accesibilidad y responsive

- Contraste suficiente, foco visible, etiquetas en todos los campos, textos alternativos en imágenes.
- En celular: buscador en una columna, filtros plegables, mapa debajo de la lista.
