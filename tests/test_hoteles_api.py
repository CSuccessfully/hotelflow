import pytest
from fastapi.testclient import TestClient

from backend import database
from backend.main import app


@pytest.fixture
def cliente_hoteles(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "hotelflow.db")
    database.inicializar_base_de_datos()
    return TestClient(app)


def test_consultar_hoteles_api_devuelve_resultados(cliente_hoteles):
    respuesta = cliente_hoteles.get(
        "/hoteles",
        params={
            "destino": "Santiago",
            "entrada": "2026-06-10",
            "salida": "2026-06-13",
            "huespedes": 2,
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()[0]["habitacion"]["total"] == 2550
    assert respuesta.json()[0]["tarifas"][0]["es_mejor_precio"] is True
    assert respuesta.json()[0]["tarifas"][0]["moneda"] == "MXN"


def test_consultar_detalle_api_devuelve_habitaciones(cliente_hoteles):
    hotel_id = cliente_hoteles.get(
        "/hoteles",
        params={
            "destino": "Santiago",
            "entrada": "2026-06-10",
            "salida": "2026-06-13",
            "huespedes": 2,
        },
    ).json()[0]["id"]

    respuesta = cliente_hoteles.get(
        f"/hoteles/{hotel_id}",
        params={"entrada": "2026-06-10", "salida": "2026-06-13", "huespedes": 2},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["habitaciones"][0]["total"] == 2550


def test_consultar_detalle_api_rechaza_hotel_inexistente(cliente_hoteles):
    respuesta = cliente_hoteles.get(
        "/hoteles/999",
        params={"entrada": "2026-06-10", "salida": "2026-06-13", "huespedes": 2},
    )

    assert respuesta.status_code == 404


@pytest.mark.parametrize(
    "parametros,mensaje",
    [
        ({"destino": "Durango", "entrada": "2026-06-15", "salida": "2026-06-10", "huespedes": 2}, "salida"),
        ({"destino": "Durango", "entrada": "2026-06-10", "salida": "2026-06-15", "huespedes": 0}, "huéspedes"),
    ],
)
def test_consultar_hoteles_api_valida_parametros(cliente_hoteles, parametros, mensaje):
    respuesta = cliente_hoteles.get("/hoteles", params=parametros)

    assert respuesta.status_code == 422
    assert mensaje in respuesta.json()["detail"]
