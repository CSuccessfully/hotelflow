from fastapi import FastAPI

from backend.database import inicializar_base_de_datos


inicializar_base_de_datos()

app = FastAPI(title="HotelFlow")


@app.get("/salud")
def consultar_salud() -> dict[str, str]:
    return {
        "estado": "ok",
        "mensaje": "El servicio está funcionando",
    }
