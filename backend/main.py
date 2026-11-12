import sqlite3

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from backend import database


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


def _validar_texto(valor: str, campo: str) -> str:
    valor_limpio = valor.strip()
    if not valor_limpio:
        raise HTTPException(
            status_code=422,
            detail=f"El campo {campo} es obligatorio",
        )
    return valor_limpio


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
