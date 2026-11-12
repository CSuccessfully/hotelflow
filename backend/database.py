from pathlib import Path
import sqlite3

from backend.semilla import cargar_semilla


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
            CREATE TABLE IF NOT EXISTS hoteles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                ciudad TEXT NOT NULL,
                direccion TEXT NOT NULL,
                latitud REAL NOT NULL,
                longitud REAL NOT NULL,
                estrellas INTEGER NOT NULL CHECK (estrellas BETWEEN 1 AND 5),
                puntuacion REAL NOT NULL CHECK (puntuacion BETWEEN 0 AND 5),
                servicios TEXT NOT NULL DEFAULT '[]',
                descripcion TEXT NOT NULL DEFAULT '',
                fotos TEXT NOT NULL DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS habitaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL,
                capacidad INTEGER NOT NULL CHECK (capacidad > 0),
                hotel_id INTEGER REFERENCES hoteles (id),
                precio_noche REAL NOT NULL DEFAULT 0 CHECK (precio_noche >= 0)
            );

            CREATE TABLE IF NOT EXISTS tarifas_proveedor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_id INTEGER NOT NULL,
                proveedor TEXT NOT NULL,
                precio_noche REAL NOT NULL CHECK (precio_noche > 0),
                moneda TEXT NOT NULL DEFAULT 'MXN',
                UNIQUE (hotel_id, proveedor),
                FOREIGN KEY (hotel_id) REFERENCES hoteles (id)
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
                numero_personas INTEGER NOT NULL DEFAULT 1
                    CHECK (numero_personas > 0),
                estado TEXT NOT NULL DEFAULT 'activa'
                    CHECK (estado IN ('activa', 'cancelada')),
                FOREIGN KEY (huesped_id) REFERENCES huespedes (id),
                FOREIGN KEY (habitacion_id) REFERENCES habitaciones (id)
            );
            """
        )

        # Compatibilidad con bases creadas antes del catálogo de hoteles.
        columnas = {
            fila[1]
            for fila in conexion.execute("PRAGMA table_info(habitaciones)")
        }
        if "hotel_id" not in columnas:
            conexion.execute(
                "ALTER TABLE habitaciones ADD COLUMN hotel_id INTEGER REFERENCES hoteles(id)"
            )
        if "precio_noche" not in columnas:
            conexion.execute(
                "ALTER TABLE habitaciones ADD COLUMN precio_noche REAL NOT NULL DEFAULT 0"
            )
        columnas_reservaciones = {
            fila[1]
            for fila in conexion.execute("PRAGMA table_info(reservaciones)")
        }
        if "numero_personas" not in columnas_reservaciones:
            conexion.execute(
                "ALTER TABLE reservaciones ADD COLUMN numero_personas INTEGER NOT NULL DEFAULT 1"
            )

        cargar_semilla(conexion)
