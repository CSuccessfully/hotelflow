import sqlite3

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

from backend import database
from backend.reservaciones import (
    cancelar_reservacion,
    consultar_habitaciones_disponibles,
    crear_reservacion,
    listar_reservaciones_activas,
    modificar_reservacion,
    obtener_reservacion,
)


database.inicializar_base_de_datos()
app = FastAPI(title="HotelFlow")


class HabitacionEntrada(BaseModel):
    numero: str
    tipo: str
    capacidad: int


class HuespedEntrada(BaseModel):
    nombre: str
    telefono: str
    correo: str | None = None


class ReservacionEntrada(BaseModel):
    huesped_id: int
    habitacion_id: int
    fecha_entrada: str
    fecha_salida: str


class ReservacionModificacion(BaseModel):
    habitacion_id: int
    fecha_entrada: str
    fecha_salida: str


def _validar_texto(valor: str, campo: str) -> str:
    valor_limpio = valor.strip()
    if not valor_limpio:
        raise HTTPException(
            status_code=422,
            detail=f"El campo {campo} es obligatorio",
        )
    return valor_limpio


def _validar_id(valor: int, campo: str) -> int:
    if valor <= 0:
        raise HTTPException(status_code=422, detail=f"El campo {campo} debe ser válido")
    return valor


def _error_reservacion(error: ValueError) -> HTTPException:
    mensaje = str(error)
    if "no existe" in mensaje:
        codigo = status.HTTP_404_NOT_FOUND
    elif "disponible" in mensaje or "activa" in mensaje:
        codigo = status.HTTP_409_CONFLICT
    else:
        codigo = 422
    return HTTPException(status_code=codigo, detail=mensaje)


def _representar_reservacion(fila) -> dict:
    return {
        "id": fila["id"],
        "huesped_id": fila["huesped_id"],
        "habitacion_id": fila["habitacion_id"],
        "fecha_entrada": fila["fecha_entrada"],
        "fecha_salida": fila["fecha_salida"],
        "estado": fila["estado"],
        "huesped": {
            "id": fila["huesped_id"],
            "nombre": fila["huesped_nombre"],
            "telefono": fila["huesped_telefono"],
            "correo": fila["huesped_correo"],
        },
        "habitacion": {
            "id": fila["habitacion_id"],
            "numero": fila["habitacion_numero"],
            "tipo": fila["habitacion_tipo"],
            "capacidad": fila["habitacion_capacidad"],
        },
    }


@app.post("/habitaciones", status_code=status.HTTP_201_CREATED)
def registrar_habitacion(habitacion: HabitacionEntrada) -> dict:
    numero = _validar_texto(habitacion.numero, "numero")
    tipo = _validar_texto(habitacion.tipo, "tipo")
    if habitacion.capacidad <= 0:
        raise HTTPException(
            status_code=422,
            detail="La capacidad debe ser mayor que cero",
        )

    try:
        with database.obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO habitaciones (numero, tipo, capacidad)
                VALUES (?, ?, ?)
                """,
                (numero, tipo, habitacion.capacidad),
            )
            fila = conexion.execute(
                "SELECT id, numero, tipo, capacidad FROM habitaciones WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed: habitaciones.numero" in str(error):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una habitación con ese número",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo registrar la habitación",
        ) from error

    return dict(fila)


@app.get("/habitaciones")
def consultar_habitaciones() -> list[dict]:
    with database.obtener_conexion() as conexion:
        filas = conexion.execute(
            "SELECT id, numero, tipo, capacidad FROM habitaciones ORDER BY numero"
        ).fetchall()
    return [dict(fila) for fila in filas]


@app.post("/huespedes", status_code=status.HTTP_201_CREATED)
def registrar_huesped(huesped: HuespedEntrada) -> dict:
    nombre = _validar_texto(huesped.nombre, "nombre")
    telefono = _validar_texto(huesped.telefono, "telefono")
    correo = huesped.correo.strip() if huesped.correo else None
    correo = correo or None

    with database.obtener_conexion() as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO huespedes (nombre, telefono, correo)
            VALUES (?, ?, ?)
            """,
            (nombre, telefono, correo),
        )
        fila = conexion.execute(
            "SELECT id, nombre, telefono, correo FROM huespedes WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return dict(fila)


@app.get("/habitaciones/disponibles")
def consultar_disponibilidad(fecha_entrada: str, fecha_salida: str) -> list[dict]:
    try:
        with database.obtener_conexion() as conexion:
            filas = consultar_habitaciones_disponibles(
                conexion, fecha_entrada, fecha_salida
            )
    except ValueError as error:
        raise _error_reservacion(error) from error
    return [dict(fila) for fila in filas]


@app.post("/reservaciones", status_code=status.HTTP_201_CREATED)
def registrar_reservacion(reservacion: ReservacionEntrada) -> dict:
    _validar_id(reservacion.huesped_id, "huesped_id")
    _validar_id(reservacion.habitacion_id, "habitacion_id")
    try:
        with database.obtener_conexion() as conexion:
            reservacion_id = crear_reservacion(
                conexion,
                reservacion.huesped_id,
                reservacion.habitacion_id,
                reservacion.fecha_entrada,
                reservacion.fecha_salida,
            )
            fila = obtener_reservacion(conexion, reservacion_id)
    except ValueError as error:
        raise _error_reservacion(error) from error
    return _representar_reservacion(fila)


@app.get("/reservaciones/activas")
def consultar_reservaciones_activas() -> list[dict]:
    with database.obtener_conexion() as conexion:
        filas = listar_reservaciones_activas(conexion)
    return [_representar_reservacion(fila) for fila in filas]


@app.put("/reservaciones/{reservacion_id}")
def actualizar_reservacion(
    reservacion_id: int, reservacion: ReservacionModificacion
) -> dict:
    _validar_id(reservacion_id, "reservacion_id")
    _validar_id(reservacion.habitacion_id, "habitacion_id")
    try:
        with database.obtener_conexion() as conexion:
            modificar_reservacion(
                conexion,
                reservacion_id,
                reservacion.habitacion_id,
                reservacion.fecha_entrada,
                reservacion.fecha_salida,
            )
            fila = obtener_reservacion(conexion, reservacion_id)
    except ValueError as error:
        raise _error_reservacion(error) from error
    return _representar_reservacion(fila)


@app.delete("/reservaciones/{reservacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reservacion(reservacion_id: int) -> Response:
    _validar_id(reservacion_id, "reservacion_id")
    try:
        with database.obtener_conexion() as conexion:
            cancelar_reservacion(conexion, reservacion_id)
    except ValueError as error:
        raise _error_reservacion(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
