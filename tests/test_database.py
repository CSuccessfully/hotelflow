import sqlite3

import pytest

from backend import database


@pytest.fixture
def base_temporal(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "hotelflow.db")
    return database


def test_inicializar_base_carga_ocho_habitaciones(base_temporal):
    base_temporal.inicializar_base_de_datos()

    with sqlite3.connect(base_temporal.DATABASE_PATH) as conexion:
        habitaciones = conexion.execute(
            "SELECT numero, tipo, capacidad FROM habitaciones ORDER BY numero"
        ).fetchall()

    assert habitaciones == [
        ("101", "sencilla", 2),
        ("102", "sencilla", 2),
        ("103", "sencilla", 2),
        ("201", "doble", 4),
        ("202", "doble", 4),
        ("203", "doble", 4),
        ("301", "suite", 4),
        ("302", "suite", 4),
    ]


def test_inicializar_base_no_duplica_habitaciones(base_temporal):
    base_temporal.inicializar_base_de_datos()
    base_temporal.inicializar_base_de_datos()

    with sqlite3.connect(base_temporal.DATABASE_PATH) as conexion:
        total = conexion.execute("SELECT COUNT(*) FROM habitaciones").fetchone()[0]

    assert total == 8


def test_inicializar_base_carga_hoteles_y_tarifas(base_temporal):
    base_temporal.inicializar_base_de_datos()

    with base_temporal.obtener_conexion() as conexion:
        hoteles = conexion.execute("SELECT COUNT(*) FROM hoteles").fetchone()[0]
        habitaciones = conexion.execute(
            "SELECT COUNT(*) FROM habitaciones WHERE hotel_id IS NOT NULL"
        ).fetchone()[0]
        tarifas = conexion.execute("SELECT COUNT(*) FROM tarifas_proveedor").fetchone()[0]
        datos = conexion.execute(
            "SELECT precio_noche, moneda FROM tarifas_proveedor"
        ).fetchall()

    assert hoteles == 3
    assert habitaciones == 8
    assert tarifas == 9
    assert all(precio > 0 and moneda == "MXN" for precio, moneda in datos)


def test_inicializar_base_no_duplica_hoteles_ni_tarifas(base_temporal):
    base_temporal.inicializar_base_de_datos()
    base_temporal.inicializar_base_de_datos()

    with base_temporal.obtener_conexion() as conexion:
        conteos = conexion.execute(
            "SELECT (SELECT COUNT(*) FROM hoteles), "
            "(SELECT COUNT(*) FROM tarifas_proveedor)"
        ).fetchone()

    assert tuple(conteos) == (3, 9)


def test_inicializar_base_conserva_habitaciones_existentes(base_temporal):
    base_temporal.inicializar_base_de_datos()
    with base_temporal.obtener_conexion() as conexion:
        conexion.execute(
            "DELETE FROM habitaciones WHERE numero = ?", ("302",)
        )
        conexion.execute(
            "INSERT INTO habitaciones (numero, tipo, capacidad) VALUES (?, ?, ?)",
            ("401", "suite", 6),
        )

    base_temporal.inicializar_base_de_datos()

    with sqlite3.connect(base_temporal.DATABASE_PATH) as conexion:
        habitaciones = conexion.execute(
            "SELECT numero FROM habitaciones ORDER BY numero"
        ).fetchall()

    assert len(habitaciones) == 8
    assert ("401",) in habitaciones
    assert ("302",) not in habitaciones
