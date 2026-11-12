# HotelFlow

Sistema de reservaciones hoteleras para el proyecto integrador del curso
**Creación de software con Agentes de IA**.

## Integrantes del equipo

- Astrid
- Grecia
- Martín
- Ángel

## Problema que resuelve

HotelFlow ayuda al recepcionista de un hotel a consultar disponibilidad y
gestionar reservaciones. Busca evitar los errores de llevar la información de
forma manual, especialmente las dobles reservaciones de una misma habitación
en fechas que se cruzan.

## Alcance

### Incluye

- Registro y consulta de habitaciones.
- Consulta de disponibilidad por fechas.
- Registro de huéspedes.
- Creación, modificación y cancelación de reservaciones.
- Listado de reservaciones activas.
- Validación de fechas y prevención de cruces entre reservaciones activas.
- Interfaz web para el recepcionista, con estados de carga, error y éxito.

### No incluye

- Pagos ni facturación.
- Reservaciones hechas directamente por huéspedes en línea.
- Manejo de varios hoteles.
- Tarifas por temporada ni descuentos.
- Envío de correos o mensajes de confirmación.
- Reportes avanzados.
- Inicio de sesión con roles.

## Tecnologías

- Python 3.
- FastAPI para la API.
- SQLite para los datos.
- HTML, CSS y JavaScript sin frameworks para la interfaz.
- pytest para las pruebas automatizadas.

## Instalación

Desde la raíz del repositorio, instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Inicia el servidor con:

```bash
uvicorn backend.main:app --reload
```

La aplicación sirve la interfaz web desde la ruta raíz y la API desde sus
endpoints correspondientes. La base de datos SQLite se crea localmente al
iniciar la aplicación.

## Pruebas

Ejecuta todas las pruebas desde la raíz del repositorio:

```bash
pytest
```

Las pruebas cubren la lógica de reservaciones, validación de fechas, cruces,
cancelaciones y endpoints de la API.

## Estructura del repositorio

```text
hotelflow/
├── backend/
│   ├── database.py          # Conexión y creación de tablas SQLite
│   ├── main.py              # Aplicación FastAPI y endpoints
│   └── reservaciones.py     # Lógica de reservaciones y regla de fechas
├── frontend/
│   ├── index.html           # Interfaz del recepcionista
│   ├── styles.css           # Estilos responsive
│   ├── app.js               # Interacción con la API
│   └── logo.svg             # Logotipo de HotelFlow
├── tests/
│   ├── test_api.py          # Pruebas de la API
│   └── test_reservaciones.py # Pruebas de la lógica de reservaciones
├── documentacion/           # Problema, alcance, requerimientos y decisiones
├── AGENTS.md                # Contexto y reglas de trabajo del proyecto
├── requirements.txt         # Dependencias de Python
└── README.md
```

## Herramientas de IA y forma de trabajo

El equipo utiliza **OpenCode** en la terminal de VS Code:

- **Modo plan:** analizar el contexto, leer los requerimientos y dividir cada
  incremento antes de implementarlo. No modifica archivos.
- **Modo build:** implementar una historia o incremento pequeño siguiendo el
  plan y `AGENTS.md`.
- **Subagente revisor:** revisa los cambios contra los requerimientos, la
  regla de fechas, las validaciones y las pruebas. No modifica archivos.
- **Subagente probador:** ejecuta `pytest`, informa cuántas pruebas pasaron o
  fallaron y señala pruebas faltantes. No modifica archivos.
