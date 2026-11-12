from pathlib import Path
import sqlite3


ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = ROOT_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "hotelflow.db"


def obtener_conexion() -> sqlite3.Connection:
    DATABASE_DIR.mkdir(exist_ok=True)
    conexion = sqlite3.connect(DATABASE_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_base_de_datos() -> None:
    with obtener_conexion() as conexion:
        conexion.executescript(
            """
            CREATE TABLE IF NOT EXISTS habitaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL,
                capacidad INTEGER NOT NULL CHECK (capacidad > 0)
            );

            CREATE TABLE IF NOT EXISTS huespedes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT NOT NULL,
                correo TEXT
            );

            CREATE TABLE IF NOT EXISTS reservaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                huesped_id INTEGER NOT NULL,
                habitacion_id INTEGER NOT NULL,
                fecha_entrada TEXT NOT NULL,
                fecha_salida TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'activa'
                    CHECK (estado IN ('activa', 'cancelada')),
                FOREIGN KEY (huesped_id) REFERENCES huespedes (id),
                FOREIGN KEY (habitacion_id) REFERENCES habitaciones (id)
            );
            """
        )
        habitaciones = conexion.execute(
            "SELECT COUNT(*) FROM habitaciones"
        ).fetchone()[0]
        if habitaciones == 0:
            conexion.executemany(
                """
                INSERT INTO habitaciones (numero, tipo, capacidad)
                VALUES (?, ?, ?)
                """,
                [
                    ("101", "sencilla", 2),
                    ("102", "sencilla", 2),
                    ("103", "sencilla", 2),
                    ("201", "doble", 4),
                    ("202", "doble", 4),
                    ("203", "doble", 4),
                    ("301", "suite", 4),
                    ("302", "suite", 4),
                ],
            )
