import pytest
from fastapi.testclient import TestClient

from backend import database
from backend.main import app


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    ruta_bd = tmp_path / "hotelflow.db"
    monkeypatch.setattr(database, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", ruta_bd)
    database.inicializar_base_de_datos()
    with database.obtener_conexion() as conexion:
        conexion.execute("DELETE FROM habitaciones")
    return TestClient(app)


def test_registrar_y_consultar_habitacion(cliente):
    respuesta = cliente.post(
        "/habitaciones",
        json={"numero": "101", "tipo": "sencilla", "capacidad": 2},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["numero"] == "101"
    assert cliente.get("/habitaciones").json() == [respuesta.json()]


def test_consultar_habitaciones_sin_registros_devuelve_lista_vacia(cliente):
    assert cliente.get("/habitaciones").json() == []


@pytest.mark.parametrize(
    "datos,campo",
    [
        ({"tipo": "sencilla", "capacidad": 2}, "numero"),
        ({"numero": "101", "capacidad": 2}, "tipo"),
        ({"numero": "101", "tipo": "sencilla"}, "capacidad"),
    ],
)
def test_registrar_habitacion_rechaza_campo_faltante(cliente, datos, campo):
    respuesta = cliente.post("/habitaciones", json=datos)

    assert respuesta.status_code == 422
    assert campo in respuesta.text


def test_registrar_habitacion_rechaza_numero_repetido(cliente):
    datos = {"numero": "101", "tipo": "sencilla", "capacidad": 2}
    cliente.post("/habitaciones", json=datos)

    respuesta = cliente.post("/habitaciones", json=datos)

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "Ya existe una habitación con ese número"


def test_registrar_habitacion_rechaza_capacidad_no_positiva(cliente):
    respuesta = cliente.post(
        "/habitaciones",
        json={"numero": "101", "tipo": "sencilla", "capacidad": 0},
    )

    assert respuesta.status_code == 422
    assert "capacidad" in respuesta.json()["detail"]


def test_registrar_huesped_con_correo_opcional(cliente):
    respuesta = cliente.post(
        "/huespedes",
        json={"nombre": "Ana López", "telefono": "555-0101"},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["correo"] is None


@pytest.mark.parametrize(
    "datos,campo",
    [
        ({"telefono": "555-0101"}, "nombre"),
        ({"nombre": "Ana López"}, "telefono"),
    ],
)
def test_registrar_huesped_rechaza_campo_faltante(cliente, datos, campo):
    respuesta = cliente.post("/huespedes", json=datos)

    assert respuesta.status_code == 422
    assert campo in respuesta.text


@pytest.mark.parametrize(
    "datos,campo",
    [
        ({"nombre": "   ", "telefono": "555-0101"}, "nombre"),
        ({"nombre": "Ana López", "telefono": "   "}, "telefono"),
    ],
)
def test_registrar_huesped_rechaza_texto_vacio(cliente, datos, campo):
    respuesta = cliente.post("/huespedes", json=datos)

    assert respuesta.status_code == 422
    assert campo in respuesta.json()["detail"]


def preparar_reservacion(cliente):
    habitacion = cliente.post(
        "/habitaciones",
        json={"numero": "101", "tipo": "sencilla", "capacidad": 2},
    ).json()
    huesped = cliente.post(
        "/huespedes",
        json={"nombre": "Ana López", "telefono": "555-0101"},
    ).json()
    return habitacion, huesped


def test_crear_reservacion_api_caso_feliz(cliente):
    habitacion, huesped = preparar_reservacion(cliente)

    respuesta = cliente.post(
        "/reservaciones",
        json={
            "huesped_id": huesped["id"],
            "habitacion_id": habitacion["id"],
            "fecha_entrada": "2026-06-10",
            "fecha_salida": "2026-06-15",
            "numero_personas": 2,
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "activa"
    assert respuesta.json()["habitacion"]["id"] == habitacion["id"]
    assert respuesta.json()["numero_personas"] == 2


def test_crear_reservacion_rechaza_capacidad_insuficiente(cliente):
    habitacion, huesped = preparar_reservacion(cliente)

    respuesta = cliente.post(
        "/reservaciones",
        json={
            "huesped_id": huesped["id"],
            "habitacion_id": habitacion["id"],
            "fecha_entrada": "2026-06-10",
            "fecha_salida": "2026-06-15",
            "numero_personas": 3,
        },
    )

    assert respuesta.status_code == 422
    assert "capacidad" in respuesta.json()["detail"]


def test_crear_doble_reservacion_devuelve_conflicto(cliente):
    habitacion, huesped = preparar_reservacion(cliente)
    datos = {
        "huesped_id": huesped["id"],
        "habitacion_id": habitacion["id"],
        "fecha_entrada": "2026-06-10",
        "fecha_salida": "2026-06-15",
    }
    primera = cliente.post("/reservaciones", json=datos)

    segunda = cliente.post("/reservaciones", json=datos)

    assert primera.status_code == 201
    assert segunda.status_code == 409
    assert "disponible" in segunda.json()["detail"]
