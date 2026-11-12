import pytest

from backend import database
from backend.hoteles import buscar_hoteles, obtener_detalle_hotel
from backend.reservaciones import crear_reservacion


@pytest.fixture
def conexion(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "hotelflow.db")
    database.inicializar_base_de_datos()
    conexion = database.obtener_conexion()
    yield conexion
    conexion.close()


def test_busqueda_devuelve_habitacion_con_capacidad_y_total(conexion):
    resultados = buscar_hoteles(
        conexion, "Santiago", "2026-06-10", "2026-06-13", 2
    )

    assert len(resultados) == 1
    assert resultados[0]["habitacion"]["numero"] == "101"
    assert resultados[0]["noches"] == 3
    assert resultados[0]["habitacion"]["total"] == 2550
    assert resultados[0]["tarifas"][0] == {
        "proveedor": "HotelFlow",
        "precio_noche": 850,
        "total": 2550,
        "moneda": "MXN",
        "es_mejor_precio": True,
    }
    assert sum(tarifa["es_mejor_precio"] for tarifa in resultados[0]["tarifas"]) == 1


def test_detalle_devuelve_hotel_y_habitaciones_disponibles(conexion):
    hotel_id = conexion.execute(
        "SELECT id FROM hoteles WHERE clave = 'casa-norte'"
    ).fetchone()[0]

    detalle = obtener_detalle_hotel(
        conexion, hotel_id, "2026-06-10", "2026-06-13", 2
    )

    assert detalle["nombre"] == "Casa Norte"
    assert detalle["fotos"]
    assert detalle["servicios"]
    assert detalle["habitaciones"][0]["numero"] == "101"
    assert detalle["habitaciones"][0]["total"] == 2550


def test_detalle_excluye_habitaciones_ocupadas_y_sin_capacidad(conexion):
    hotel_id = conexion.execute(
        "SELECT id FROM hoteles WHERE clave = 'casa-norte'"
    ).fetchone()[0]
    huesped = conexion.execute(
        "INSERT INTO huespedes (nombre, telefono) VALUES ('Demo', '555')"
    )
    habitacion = conexion.execute(
        "SELECT id FROM habitaciones WHERE numero = '101'"
    ).fetchone()[0]
    conexion.commit()
    crear_reservacion(
        conexion, huesped.lastrowid, habitacion, "2026-06-10", "2026-06-13", 2
    )

    detalle = obtener_detalle_hotel(
        conexion, hotel_id, "2026-06-10", "2026-06-13", 3
    )

    assert detalle["habitaciones"] == []


def test_comparativa_se_ordena_y_calcula_total_por_proveedor(conexion):
    resultado = buscar_hoteles(
        conexion, "Durango", "2026-06-10", "2026-06-12", 2
    )[0]

    assert [tarifa["proveedor"] for tarifa in resultado["tarifas"]] == [
        "HotelFlow", "Agencia Demo", "Portal Demo"
    ]
    assert [tarifa["total"] for tarifa in resultado["tarifas"]] == [2700, 2780, 2850]


def test_hotel_sin_tarifas_conserva_resultado(conexion):
    conexion.execute("DELETE FROM tarifas_proveedor")
    conexion.commit()

    resultado = buscar_hoteles(
        conexion, "Santiago", "2026-06-10", "2026-06-12", 2
    )[0]

    assert resultado["tarifas"] == []


def test_busqueda_excluye_habitacion_ocupada_y_acepta_siguiente(conexion):
    huesped = conexion.execute(
        "INSERT INTO huespedes (nombre, telefono) VALUES ('Demo', '555')"
    )
    conexion.commit()
    habitacion = conexion.execute(
        "SELECT id FROM habitaciones WHERE numero = '101'"
    ).fetchone()[0]
    crear_reservacion(conexion, huesped.lastrowid, habitacion, "2026-06-10", "2026-06-13")

    resultados = buscar_hoteles(
        conexion, "Santiago", "2026-06-10", "2026-06-13", 2
    )
    assert resultados[0]["habitacion"]["numero"] == "102"

    resultados = buscar_hoteles(
        conexion, "Santiago", "2026-06-13", "2026-06-15", 2
    )
    assert resultados[0]["habitacion"]["numero"] == "101"


def test_busqueda_aplica_filtros_y_orden(conexion):
    resultados = buscar_hoteles(
        conexion, "o", "2026-06-10", "2026-06-12", 2,
        estrellas=4, servicios="Wi-Fi", orden="puntuacion",
    )

    assert [hotel["nombre"] for hotel in resultados] == ["Jardín Serrano", "Patio del Sol"]

    baratos = buscar_hoteles(
        conexion, "o", "2026-06-10", "2026-06-12", 2, precio_max=2800
    )
    assert all(hotel["habitacion"]["total"] <= 2800 for hotel in baratos)


@pytest.mark.parametrize(
    "datos,mensaje",
    [
        (("Durango", "2026-06-15", "2026-06-10", 2), "salida"),
        (("Durango", "2026-06-10", "2026-06-15", 0), "huéspedes"),
    ],
)
def test_busqueda_rechaza_entradas_invalidas(conexion, datos, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        buscar_hoteles(conexion, *datos)
