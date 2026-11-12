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
