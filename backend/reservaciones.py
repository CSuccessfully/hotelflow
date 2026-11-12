from datetime import date
import sqlite3


def _validar_fechas(fecha_entrada: str, fecha_salida: str) -> tuple[str, str]:
    try:
        entrada = date.fromisoformat(fecha_entrada)
        salida = date.fromisoformat(fecha_salida)
    except (TypeError, ValueError) as error:
        raise ValueError("Las fechas deben ser válidas y usar el formato YYYY-MM-DD") from error

    if salida <= entrada:
        raise ValueError("La fecha de salida debe ser posterior a la fecha de entrada")

    return entrada.isoformat(), salida.isoformat()


def _verificar_huesped(conexion: sqlite3.Connection, huesped_id: int) -> None:
    existe = conexion.execute(
        "SELECT 1 FROM huespedes WHERE id = ?", (huesped_id,)
    ).fetchone()
    if existe is None:
        raise ValueError("El huésped no existe")


def _verificar_habitacion(
    conexion: sqlite3.Connection, habitacion_id: int
) -> None:
    existe = conexion.execute(
        "SELECT 1 FROM habitaciones WHERE id = ?", (habitacion_id,)
    ).fetchone()
    if existe is None:
        raise ValueError("La habitación no existe")


def _hay_cruce(
    conexion: sqlite3.Connection,
    habitacion_id: int,
    fecha_entrada: str,
    fecha_salida: str,
    excluir_id: int | None = None,
) -> bool:
    consulta = """
        SELECT 1
        FROM reservaciones
        WHERE habitacion_id = ?
          AND estado = 'activa'
          AND fecha_entrada < ?
          AND fecha_salida > ?
    """
    parametros: list[object] = [habitacion_id, fecha_salida, fecha_entrada]

    if excluir_id is not None:
        consulta += " AND id != ?"
        parametros.append(excluir_id)

    return conexion.execute(consulta, parametros).fetchone() is not None


def crear_reservacion(
    conexion: sqlite3.Connection,
    huesped_id: int,
    habitacion_id: int,
    fecha_entrada: str,
    fecha_salida: str,
) -> int:
    fecha_entrada, fecha_salida = _validar_fechas(
        fecha_entrada, fecha_salida
    )
    _verificar_huesped(conexion, huesped_id)
    _verificar_habitacion(conexion, habitacion_id)

    if _hay_cruce(conexion, habitacion_id, fecha_entrada, fecha_salida):
        raise ValueError("La habitación no está disponible en esas fechas")

    cursor = conexion.execute(
        """
        INSERT INTO reservaciones
            (huesped_id, habitacion_id, fecha_entrada, fecha_salida, estado)
        VALUES (?, ?, ?, ?, 'activa')
        """,
        (huesped_id, habitacion_id, fecha_entrada, fecha_salida),
    )
    conexion.commit()
    return cursor.lastrowid


def modificar_reservacion(
    conexion: sqlite3.Connection,
    reservacion_id: int,
    habitacion_id: int,
    fecha_entrada: str,
    fecha_salida: str,
) -> None:
    fecha_entrada, fecha_salida = _validar_fechas(
        fecha_entrada, fecha_salida
    )
    reservacion = conexion.execute(
        "SELECT estado FROM reservaciones WHERE id = ?", (reservacion_id,)
    ).fetchone()
    if reservacion is None:
        raise ValueError("La reservación no existe")
    if reservacion[0] != "activa":
        raise ValueError("La reservación no está activa")

    _verificar_habitacion(conexion, habitacion_id)
    if _hay_cruce(
        conexion,
        habitacion_id,
        fecha_entrada,
        fecha_salida,
        excluir_id=reservacion_id,
    ):
        raise ValueError("La habitación no está disponible en esas fechas")

    conexion.execute(
        """
        UPDATE reservaciones
        SET habitacion_id = ?, fecha_entrada = ?, fecha_salida = ?
        WHERE id = ?
        """,
        (habitacion_id, fecha_entrada, fecha_salida, reservacion_id),
    )
    conexion.commit()


def cancelar_reservacion(
    conexion: sqlite3.Connection, reservacion_id: int
) -> None:
    reservacion = conexion.execute(
        "SELECT estado FROM reservaciones WHERE id = ?", (reservacion_id,)
    ).fetchone()
    if reservacion is None:
        raise ValueError("La reservación no existe")
    if reservacion[0] != "activa":
        raise ValueError("La reservación no está activa")

    conexion.execute(
        "UPDATE reservaciones SET estado = 'cancelada' WHERE id = ?",
        (reservacion_id,),
    )
    conexion.commit()
