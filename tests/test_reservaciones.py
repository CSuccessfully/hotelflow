import sqlite3

import pytest

from backend.reservaciones import (
    cancelar_reservacion,
    crear_reservacion,
    modificar_reservacion,
)


@pytest.fixture
def conexion():
    conexion = sqlite3.connect(":memory:")
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.executescript(
        """
        CREATE TABLE habitaciones (
            id INTEGER PRIMARY KEY,
            numero TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            capacidad INTEGER NOT NULL,
            precio_noche REAL NOT NULL DEFAULT 850
        );
        CREATE TABLE huespedes (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT
        );
        CREATE TABLE reservaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            huesped_id INTEGER NOT NULL,
            habitacion_id INTEGER NOT NULL,
            fecha_entrada TEXT NOT NULL,
            fecha_salida TEXT NOT NULL,
            numero_personas INTEGER NOT NULL DEFAULT 1,
            estado TEXT NOT NULL DEFAULT 'activa',
            FOREIGN KEY (huesped_id) REFERENCES huespedes (id),
            FOREIGN KEY (habitacion_id) REFERENCES habitaciones (id)
        );
        """
    )
    conexion.execute(
        "INSERT INTO habitaciones (numero, tipo, capacidad) VALUES (?, ?, ?)",
        ("101", "sencilla", 2),
    )
    conexion.execute(
        "INSERT INTO habitaciones (numero, tipo, capacidad) VALUES (?, ?, ?)",
        ("102", "doble", 4),
    )
    conexion.execute(
        "INSERT INTO huespedes (nombre, telefono) VALUES (?, ?)",
        ("Ana López", "555-0101"),
    )
    conexion.execute(
        "INSERT INTO huespedes (nombre, telefono) VALUES (?, ?)",
        ("Luis Pérez", "555-0102"),
    )
    conexion.commit()
    yield conexion
    conexion.close()


def reservar(conexion, entrada="2026-06-10", salida="2026-06-20", habitacion=1):
    return crear_reservacion(conexion, 1, habitacion, entrada, salida)


def test_reservar_habitacion_libre_funciona(conexion):
    reservacion_id = reservar(conexion)

    reservacion = conexion.execute(
        "SELECT habitacion_id, fecha_entrada, fecha_salida, estado "
        "FROM reservaciones WHERE id = ?",
        (reservacion_id,),
    ).fetchone()

    assert reservacion == (1, "2026-06-10", "2026-06-20", "activa")


@pytest.mark.parametrize(
    "entrada,salida",
    [
        ("2026-06-12", "2026-06-18"),  # cruce contenido
        ("2026-06-05", "2026-06-12"),  # cruce parcial inicial
        ("2026-06-18", "2026-06-25"),  # cruce parcial final
        ("2026-06-05", "2026-06-25"),  # cruce total
    ],
)
def test_reservar_con_fechas_que_se_cruzan_se_rechaza(
    conexion, entrada, salida
):
    reservar(conexion)

    with pytest.raises(ValueError, match="disponible"):
        reservar(conexion, entrada, salida)


def test_el_dia_de_salida_es_libre_para_una_nueva_entrada(conexion):
    reservar(conexion, "2026-06-10", "2026-06-15")

    nueva_id = reservar(conexion, "2026-06-15", "2026-06-20")

    assert nueva_id > 1


def test_cancelar_libera_la_habitacion(conexion):
    reservacion_id = reservar(conexion)

    cancelar_reservacion(conexion, reservacion_id)
    nueva_id = reservar(conexion)

    estado = conexion.execute(
        "SELECT estado FROM reservaciones WHERE id = ?", (reservacion_id,)
    ).fetchone()[0]
    assert estado == "cancelada"
    assert nueva_id != reservacion_id


def test_modificar_a_fechas_libres_funciona(conexion):
    reservacion_id = reservar(conexion)

    modificar_reservacion(
        conexion, reservacion_id, 2, "2026-07-01", "2026-07-05"
    )

    datos = conexion.execute(
        "SELECT habitacion_id, fecha_entrada, fecha_salida "
        "FROM reservaciones WHERE id = ?",
        (reservacion_id,),
    ).fetchone()
    assert datos == (2, "2026-07-01", "2026-07-05")


def test_modificar_a_fechas_cruzadas_no_altera_la_reservacion_original(conexion):
    primera_id = reservar(conexion)
    reservar(conexion, "2026-07-25", "2026-07-30")

    with pytest.raises(ValueError, match="disponible"):
        modificar_reservacion(
            conexion, primera_id, 1, "2026-07-20", "2026-07-27"
        )

    datos = conexion.execute(
        "SELECT habitacion_id, fecha_entrada, fecha_salida, estado "
        "FROM reservaciones WHERE id = ?",
        (primera_id,),
    ).fetchone()
    assert datos == (1, "2026-06-10", "2026-06-20", "activa")


@pytest.mark.parametrize(
    "entrada,salida",
    [("2026-06-20", "2026-06-10"), ("2026-06-10", "2026-06-10")],
)
def test_fechas_invalidas_se_rechazan(conexion, entrada, salida):
    with pytest.raises(ValueError, match="salida"):
        reservar(conexion, entrada, salida)

    assert conexion.execute("SELECT COUNT(*) FROM reservaciones").fetchone()[0] == 0


def test_reservacion_cancelada_no_bloquea_nuevas_fechas(conexion):
    reservacion_id = reservar(conexion)
    cancelar_reservacion(conexion, reservacion_id)

    assert reservar(conexion) > reservacion_id


def test_no_se_puede_reservar_con_huesped_inexistente(conexion):
    with pytest.raises(ValueError, match="huésped"):
        crear_reservacion(conexion, 999, 1, "2026-06-10", "2026-06-20")


def test_no_se_puede_reservar_con_habitacion_inexistente(conexion):
    with pytest.raises(ValueError, match="habitación"):
        crear_reservacion(conexion, 1, 999, "2026-06-10", "2026-06-20")
