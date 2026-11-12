from datetime import date
import json
import sqlite3


def _validar_fechas(fecha_entrada: str, fecha_salida: str) -> tuple[str, str]:
    try:
        entrada = date.fromisoformat(fecha_entrada)
        salida = date.fromisoformat(fecha_salida)
    except (TypeError, ValueError) as error:
        raise ValueError("Las fechas deben ser válidas y usar el formato YYYY-MM-DD") from error

    if salida <= entrada:
        raise ValueError("La fecha de salida debe ser posterior a la fecha de entrada")
    return entrada.isoformat(), salida.isoformat()


def _normalizar_servicios(servicios: str | list[str] | None) -> list[str]:
    if servicios is None:
        return []
    valores = servicios.split(",") if isinstance(servicios, str) else servicios
    resultado = [servicio.strip() for servicio in valores if servicio.strip()]
    if any(not servicio for servicio in resultado):
        raise ValueError("Los servicios deben ser válidos")
    return resultado


def _agregar_tarifas(
    conexion: sqlite3.Connection, resultados: list[dict], noches: int
) -> None:
    if not resultados:
        return

    ids = [hotel["id"] for hotel in resultados]
    marcadores = ",".join("?" for _ in ids)
    filas = conexion.execute(
        f"""
        SELECT hotel_id, proveedor, precio_noche, moneda
        FROM tarifas_proveedor
        WHERE hotel_id IN ({marcadores})
        ORDER BY hotel_id, precio_noche, proveedor
        """,
        ids,
    ).fetchall()
    tarifas_por_hotel: dict[int, list[sqlite3.Row]] = {}
    for fila in filas:
        tarifas_por_hotel.setdefault(fila["hotel_id"], []).append(fila)

    for hotel in resultados:
        tarifas = tarifas_por_hotel.get(hotel["id"], [])
        hotel["tarifas"] = [
            {
                "proveedor": tarifa["proveedor"],
                "precio_noche": tarifa["precio_noche"],
                "total": noches * tarifa["precio_noche"],
                "moneda": tarifa["moneda"],
                "es_mejor_precio": indice == 0,
            }
            for indice, tarifa in enumerate(tarifas)
        ]


def buscar_hoteles(
    conexion: sqlite3.Connection,
    destino: str,
    fecha_entrada: str,
    fecha_salida: str,
    huespedes: int,
    precio_max: float | None = None,
    estrellas: int | None = None,
    servicios: str | list[str] | None = None,
    orden: str = "precio",
) -> list[dict]:
    destino = destino.strip()
    if not destino:
        raise ValueError("El destino es obligatorio")
    if huespedes < 1:
        raise ValueError("El número de huéspedes debe ser mayor o igual a 1")
    if precio_max is not None and precio_max < 0:
        raise ValueError("El precio máximo no puede ser negativo")
    if estrellas is not None and not 1 <= estrellas <= 5:
        raise ValueError("Las estrellas deben estar entre 1 y 5")
    if orden not in {"precio", "puntuacion"}:
        raise ValueError("El orden debe ser 'precio' o 'puntuacion'")

    entrada, salida = _validar_fechas(fecha_entrada, fecha_salida)
    servicios_solicitados = _normalizar_servicios(servicios)
    noches = (date.fromisoformat(salida) - date.fromisoformat(entrada)).days
    filas = conexion.execute(
        """
        SELECT
            h.id AS hotel_id, h.clave, h.nombre, h.ciudad, h.direccion,
            h.latitud, h.longitud, h.estrellas, h.puntuacion,
            h.servicios, h.descripcion, h.fotos,
            a.id AS habitacion_id, a.numero, a.tipo, a.capacidad,
            a.precio_noche
        FROM hoteles AS h
        JOIN habitaciones AS a ON a.hotel_id = h.id
        WHERE (
            lower(h.ciudad) LIKE lower(?)
            OR lower(h.nombre) LIKE lower(?)
        )
          AND a.capacidad >= ?
          AND NOT EXISTS (
              SELECT 1
              FROM reservaciones AS r
              WHERE r.habitacion_id = a.id
                AND r.estado = 'activa'
                AND r.fecha_entrada < ?
                AND r.fecha_salida > ?
          )
        ORDER BY h.id, a.precio_noche, a.id
        """,
        (f"%{destino}%", f"%{destino}%", huespedes, salida, entrada),
    ).fetchall()

    resultados_por_hotel: dict[int, dict] = {}
    for fila in filas:
        datos_servicios = json.loads(fila["servicios"] or "[]")
        if estrellas is not None and fila["estrellas"] < estrellas:
            continue
        if any(servicio.lower() not in {item.lower() for item in datos_servicios}
               for servicio in servicios_solicitados):
            continue

        total = noches * fila["precio_noche"]
        if precio_max is not None and total > precio_max:
            continue
        if fila["hotel_id"] in resultados_por_hotel:
            continue

        resultados_por_hotel[fila["hotel_id"]] = {
            "id": fila["hotel_id"],
            "clave": fila["clave"],
            "nombre": fila["nombre"],
            "ciudad": fila["ciudad"],
            "direccion": fila["direccion"],
            "latitud": fila["latitud"],
            "longitud": fila["longitud"],
            "estrellas": fila["estrellas"],
            "puntuacion": fila["puntuacion"],
            "servicios": datos_servicios,
            "descripcion": fila["descripcion"],
            "fotos": json.loads(fila["fotos"] or "[]"),
            "noches": noches,
            "habitacion": {
                "id": fila["habitacion_id"],
                "numero": fila["numero"],
                "tipo": fila["tipo"],
                "capacidad": fila["capacidad"],
                "precio_noche": fila["precio_noche"],
                "total": total,
                "moneda": "MXN",
            },
        }

    resultados = list(resultados_por_hotel.values())
    if orden == "precio":
        resultados.sort(key=lambda hotel: (hotel["habitacion"]["total"], -hotel["puntuacion"]))
    else:
        resultados.sort(key=lambda hotel: (-hotel["puntuacion"], hotel["habitacion"]["total"]))
    _agregar_tarifas(conexion, resultados, noches)
    return resultados


def obtener_detalle_hotel(
    conexion: sqlite3.Connection,
    hotel_id: int,
    fecha_entrada: str,
    fecha_salida: str,
    huespedes: int,
) -> dict | None:
    if hotel_id <= 0:
        raise ValueError("El hotel debe ser válido")
    if huespedes < 1:
        raise ValueError("El número de huéspedes debe ser mayor o igual a 1")

    entrada, salida = _validar_fechas(fecha_entrada, fecha_salida)
    noches = (date.fromisoformat(salida) - date.fromisoformat(entrada)).days
    hotel = conexion.execute(
        """
        SELECT id, clave, nombre, ciudad, direccion, latitud, longitud,
               estrellas, puntuacion, servicios, descripcion, fotos
        FROM hoteles
        WHERE id = ?
        """,
        (hotel_id,),
    ).fetchone()
    if hotel is None:
        return None

    habitaciones = conexion.execute(
        """
        SELECT a.id, a.numero, a.tipo, a.capacidad, a.precio_noche
        FROM habitaciones AS a
        WHERE a.hotel_id = ?
          AND a.capacidad >= ?
          AND NOT EXISTS (
              SELECT 1
              FROM reservaciones AS r
              WHERE r.habitacion_id = a.id
                AND r.estado = 'activa'
                AND r.fecha_entrada < ?
                AND r.fecha_salida > ?
          )
        ORDER BY a.precio_noche, a.id
        """,
        (hotel_id, huespedes, salida, entrada),
    ).fetchall()

    return {
        "id": hotel["id"],
        "clave": hotel["clave"],
        "nombre": hotel["nombre"],
        "ciudad": hotel["ciudad"],
        "direccion": hotel["direccion"],
        "latitud": hotel["latitud"],
        "longitud": hotel["longitud"],
        "estrellas": hotel["estrellas"],
        "puntuacion": hotel["puntuacion"],
        "servicios": json.loads(hotel["servicios"] or "[]"),
        "descripcion": hotel["descripcion"],
        "fotos": json.loads(hotel["fotos"] or "[]"),
        "noches": noches,
        "habitaciones": [
            {
                "id": habitacion["id"],
                "numero": habitacion["numero"],
                "tipo": habitacion["tipo"],
                "capacidad": habitacion["capacidad"],
                "precio_noche": habitacion["precio_noche"],
                "total": noches * habitacion["precio_noche"],
                "moneda": "MXN",
            }
            for habitacion in habitaciones
        ],
    }
