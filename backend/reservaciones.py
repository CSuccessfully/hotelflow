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


def consultar_habitaciones_disponibles(
    conexion: sqlite3.Connection,
    fecha_entrada: str,
    fecha_salida: str,
) -> list[sqlite3.Row | tuple]:
    fecha_entrada, fecha_salida = _validar_fechas(
        fecha_entrada, fecha_salida
    )
    filas = conexion.execute(
        """
        SELECT h.id, h.numero, h.tipo, h.capacidad
        FROM habitaciones AS h
        WHERE NOT EXISTS (
            SELECT 1
            FROM reservaciones AS r
            WHERE r.habitacion_id = h.id
              AND r.estado = 'activa'
              AND r.fecha_entrada < ?
              AND r.fecha_salida > ?
        )
        ORDER BY h.numero
        """,
        (fecha_salida, fecha_entrada),
    ).fetchall()
    return filas


def obtener_reservacion(
    conexion: sqlite3.Connection, reservacion_id: int
) -> sqlite3.Row | tuple | None:
    return conexion.execute(
        """
        SELECT
            r.id,
            r.huesped_id,
            r.habitacion_id,
            r.fecha_entrada,
            r.fecha_salida,
            r.estado,
            h.nombre AS huesped_nombre,
            h.telefono AS huesped_telefono,
            h.correo AS huesped_correo,
            a.numero AS habitacion_numero,
            a.tipo AS habitacion_tipo,
            a.capacidad AS habitacion_capacidad
        FROM reservaciones AS r
        JOIN huespedes AS h ON h.id = r.huesped_id
        JOIN habitaciones AS a ON a.id = r.habitacion_id
        WHERE r.id = ?
        """,
        (reservacion_id,),
    ).fetchone()


def listar_reservaciones_activas(
    conexion: sqlite3.Connection,
) -> list[sqlite3.Row | tuple]:
    return conexion.execute(
        """
        SELECT
            r.id,
            r.huesped_id,
            r.habitacion_id,
            r.fecha_entrada,
            r.fecha_salida,
            r.estado,
            h.nombre AS huesped_nombre,
            h.telefono AS huesped_telefono,
            h.correo AS huesped_correo,
            a.numero AS habitacion_numero,
            a.tipo AS habitacion_tipo,
            a.capacidad AS habitacion_capacidad
        FROM reservaciones AS r
        JOIN huespedes AS h ON h.id = r.huesped_id
        JOIN habitaciones AS a ON a.id = r.habitacion_id
        WHERE r.estado = 'activa'
        ORDER BY r.fecha_entrada, r.id
        """
    ).fetchall()
