import json
import sqlite3


HOTELES = [
    {
        "clave": "casa-norte",
        "nombre": "Casa Norte",
        "ciudad": "Santiago Papasquiaro",
        "direccion": "Avenida del Valle 120",
        "latitud": 25.045,
        "longitud": -105.419,
        "estrellas": 3,
        "puntuacion": 4.2,
        "servicios": ["Wi-Fi", "Estacionamiento", "Desayuno"],
        "descripcion": "Hospedaje ficticio de ambiente tranquilo cerca del centro.",
        "fotos": ["hotel-casa-norte-1.webp", "hotel-casa-norte-2.webp"],
        "habitaciones": [("101", "sencilla", 2, 850), ("102", "sencilla", 2, 950), ("103", "sencilla", 2, 1050)],
        "tarifas": [("HotelFlow", 850), ("Portal Demo", 900), ("Agencia Demo", 875)],
    },
    {
        "clave": "patio-del-sol",
        "nombre": "Patio del Sol",
        "ciudad": "Durango",
        "direccion": "Calle del Sol 45",
        "latitud": 24.0277,
        "longitud": -104.6532,
        "estrellas": 4,
        "puntuacion": 4.6,
        "servicios": ["Wi-Fi", "Alberca", "Restaurante"],
        "descripcion": "Hotel ficticio con patio interior y espacios familiares.",
        "fotos": ["hotel-patio-del-sol-1.webp", "hotel-patio-del-sol-2.webp"],
        "habitaciones": [("201", "doble", 4, 1350), ("202", "doble", 4, 1800), ("203", "doble", 4, 2100)],
        "tarifas": [("HotelFlow", 1350), ("Portal Demo", 1425), ("Agencia Demo", 1390)],
    },
    {
        "clave": "jardin-serrano",
        "nombre": "Jardín Serrano",
        "ciudad": "Canatlán",
        "direccion": "Camino de los Pinos 8",
        "latitud": 24.516,
        "longitud": -104.776,
        "estrellas": 5,
        "puntuacion": 4.8,
        "servicios": ["Wi-Fi", "Estacionamiento", "Jardín", "Desayuno"],
        "descripcion": "Alojamiento ficticio rodeado de jardines y paisaje serrano.",
        "fotos": ["hotel-jardin-serrano-1.webp"],
        "habitaciones": [("301", "suite", 4, 2100), ("302", "suite", 4, 2900)],
        "tarifas": [("HotelFlow", 2100), ("Portal Demo", 2250), ("Agencia Demo", 2180)],
    },
]


def cargar_semilla(conexion: sqlite3.Connection) -> None:
    """Carga datos ficticios sin duplicarlos ni borrar datos existentes."""
    for hotel in HOTELES:
        resultado = conexion.execute(
            """
            INSERT OR IGNORE INTO hoteles
                (clave, nombre, ciudad, direccion, latitud, longitud,
                 estrellas, puntuacion, servicios, descripcion, fotos)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hotel["clave"], hotel["nombre"], hotel["ciudad"], hotel["direccion"],
                hotel["latitud"], hotel["longitud"], hotel["estrellas"], hotel["puntuacion"],
                json.dumps(hotel["servicios"], ensure_ascii=False), hotel["descripcion"],
                json.dumps(hotel["fotos"], ensure_ascii=False),
            ),
        )
        hotel_id = conexion.execute(
            "SELECT id FROM hoteles WHERE clave = ?", (hotel["clave"],)
        ).fetchone()[0]

        if resultado.rowcount != 1:
            continue

        for numero, tipo, capacidad, precio in hotel["habitaciones"]:
            conexion.execute(
                """
                INSERT OR IGNORE INTO habitaciones
                    (numero, tipo, capacidad, hotel_id, precio_noche)
                VALUES (?, ?, ?, ?, ?)
                """,
                (numero, tipo, capacidad, hotel_id, precio),
            )

        for proveedor, precio in hotel["tarifas"]:
            conexion.execute(
                """
                INSERT OR IGNORE INTO tarifas_proveedor
                    (hotel_id, proveedor, precio_noche, moneda)
                VALUES (?, ?, ?, 'MXN')
                """,
                (hotel_id, proveedor, precio),
            )

    conexion.commit()
