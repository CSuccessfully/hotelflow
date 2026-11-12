from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]


def test_pantalla_de_busqueda_tiene_campos_y_aviso_de_demo():
    html = (RAIZ / "frontend" / "index.html").read_text(encoding="utf-8")

    for texto in ("form-busqueda", "destino", "entrada", "salida", "huespedes", "Datos de demostración"):
        assert texto in html


def test_frontend_referencia_api_y_estados_de_interfaz():
    javascript = (RAIZ / "frontend" / "app.js").read_text(encoding="utf-8")

    assert "/hoteles?" in javascript
    assert "Buscando hoteles" in javascript
    assert "No encontramos hoteles" in javascript
    assert "onerror" in javascript
    assert "Mejor precio" in javascript
    assert "Comparativa de precios" in javascript


def test_existe_reemplazo_local_de_imagen():
    assert (RAIZ / "frontend" / "img" / "sin-imagen.svg").exists()
    assert (RAIZ / "frontend" / "img" / "imagenes.json").exists()


def test_frontend_integra_mapa_local_y_marcadores():
    html = (RAIZ / "frontend" / "index.html").read_text(encoding="utf-8")
    javascript = (RAIZ / "frontend" / "app.js").read_text(encoding="utf-8")

    assert 'id="mapa"' in html
    assert "vendor/leaflet/leaflet.css" in html
    assert "vendor/leaflet/leaflet.js" in html
    assert "L.map" in javascript
    assert "L.marker" in javascript
    assert "latitud" in javascript
    assert "longitud" in javascript
    assert "tileerror" in javascript


def test_frontend_integra_detalle_y_reservacion():
    html = (RAIZ / "frontend" / "index.html").read_text(encoding="utf-8")
    javascript = (RAIZ / "frontend" / "app.js").read_text(encoding="utf-8")

    assert "Ver hotel" in javascript
    assert "/hoteles/${hotelId}" in javascript
    assert "form-reservacion" in html
    assert "nombre-reserva" in html
    assert "telefono-reserva" in html
    assert "numero_personas" in javascript
    assert "/huespedes" in javascript
    assert "/reservaciones" in javascript
