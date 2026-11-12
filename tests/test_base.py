import sqlite3

from fastapi.testclient import TestClient

from backend.database import DATABASE_PATH, inicializar_base_de_datos
from backend.main import app


def test_endpoint_salud():
    cliente = TestClient(app)

    respuesta = cliente.get("/salud")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "estado": "ok",
        "mensaje": "El servicio está funcionando",
    }


def test_base_de_datos_tiene_tablas_iniciales():
    inicializar_base_de_datos()

    with sqlite3.connect(DATABASE_PATH) as conexion:
        tablas = {
            fila[0]
            for fila in conexion.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table'"
            )
        }

    assert {"habitaciones", "huespedes", "reservaciones"} <= tablas
