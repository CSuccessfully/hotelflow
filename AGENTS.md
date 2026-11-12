# AGENTS.md: contexto del proyecto HotelFlow

## Qué es este proyecto

HotelFlow es un MVP de sistema de reservaciones para un hotel general. Es el proyecto integrador del curso "Creación de software con Agentes de IA" (Congreso Ciencias Revueltas 2026, ITS Santiago Papasquiaro). Lo desarrolla un equipo de estudiantes usando OpenCode.

## Usuario y problema

El usuario principal es el recepcionista del hotel. El problema: llevar reservaciones a mano provoca errores como dobles reservaciones. HotelFlow le permite consultar disponibilidad por fechas y crear, modificar y cancelar reservaciones de forma rápida y confiable.

## Alcance del MVP

Incluye: registro y consulta de habitaciones, disponibilidad por fechas, registro de huéspedes, crear/modificar/cancelar reservaciones, y listado de reservaciones activas.

No incluye (no lo implementes aunque se sugiera): pagos o facturación, reservas hechas por huéspedes en línea, varios hoteles, tarifas por temporada, correos o mensajes de confirmación, reportes avanzados, inicio de sesión con roles.

## Regla de negocio más importante

Dos reservaciones activas de la misma habitación NO pueden cruzarse en fechas. Hay cruce cuando la entrada de una es anterior a la salida de la otra Y la salida de la primera es posterior a la entrada de la otra. El día de salida cuenta como libre para una nueva entrada. Una reservación cancelada no cuenta para el cruce.

## Tecnología

- Python 3 con FastAPI (API), SQLite (datos) y pytest (pruebas).
- Interfaz: HTML, CSS y JavaScript sin frameworks, en `frontend/`.

## Estructura del repositorio

- `backend/main.py`: aplicación FastAPI y endpoints.
- `backend/database.py`: conexión y creación de tablas SQLite.
- `backend/reservaciones.py`: lógica de reservaciones y regla de fechas (sin código de interfaz).
- `frontend/`: interfaz del recepcionista.
- `tests/`: pruebas automatizadas.
- `documentacion/`: problema, alcance, requerimientos y decisiones. Léelos antes de planear.

## Comandos

- Instalar: `pip install -r requirements.txt`
- Ejecutar: `uvicorn backend.main:app --reload`
- Probar: `pytest`

## Reglas de trabajo para los agentes

1. Trabaja un incremento pequeño a la vez, solo el que se te pidió.
2. Antes de implementar, consulta `documentacion/requerimientos.md` para respetar requerimientos y criterios de aceptación.
3. Escribe o actualiza pruebas para todo cambio en la lógica de reservaciones y ejecuta `pytest` antes de dar algo por terminado.
4. Valida todas las entradas de la API (fechas válidas, salida posterior a entrada, campos obligatorios) y devuelve mensajes de error claros.
5. La lógica de negocio va en `backend/reservaciones.py`, no en los endpoints ni en el frontend.
6. Código simple y legible, con nombres en español para el dominio (habitación, huésped, reservación).
7. No borres archivos ni cambies la estructura sin avisar antes.
8. Nunca escribas claves, contraseñas ni datos personales reales en el código. No crees ni versiones archivos `.env`.
9. No modifiques los archivos de `documentacion/` salvo que se pida explícitamente.
10. Al terminar, explica en pocas líneas qué cambiaste y por qué, para que el equipo pueda revisarlo y entenderlo.
