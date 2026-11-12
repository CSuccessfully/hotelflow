const estado = { busqueda: null, hotel: null, habitacion: null };
const $ = (selector) => document.querySelector(selector);
const listaHoteles = $("#lista-hoteles");
const estadoResultados = $("#estado-resultados");
const contenedorResultados = $(".resultados");
let mapa = null;
let marcadores = null;

function escaparHtml(valor) {
  const elemento = document.createElement("span");
  elemento.textContent = valor ?? "";
  return elemento.innerHTML;
}

function mostrarEstado(titulo, texto, tipo = "inicial") {
  estadoResultados.className = `estado estado--${tipo}`;
  estadoResultados.innerHTML = `<h2>${escaparHtml(titulo)}</h2><p>${escaparHtml(texto)}</p>`;
  estadoResultados.hidden = false;
  listaHoteles.replaceChildren();
}

function mostrarErrorFormulario(texto) {
  const error = $("#error-busqueda");
  error.textContent = texto;
  error.hidden = !texto;
}

function validarBusqueda() {
  const destino = $("#destino").value.trim();
  const entrada = $("#entrada").value;
  const salida = $("#salida").value;
  const huespedes = Number($("#huespedes").value);
  if (!destino) throw new Error("Captura un destino.");
  if (!entrada || !salida) throw new Error("Captura las fechas de entrada y salida.");
  if (salida <= entrada) throw new Error("La fecha de salida debe ser posterior a la de entrada.");
  if (!Number.isInteger(huespedes) || huespedes < 1) throw new Error("Los huéspedes deben ser al menos 1.");
  return { destino, entrada, salida, huespedes };
}

function obtenerFiltros() {
  const servicios = Array.from($("#servicios").selectedOptions).map((opcion) => opcion.value);
  const estrella = document.querySelector('input[name="estrellas"]:checked')?.value || "";
  return {
    precio_max: $("#precio-max").value,
    estrellas: estrella,
    servicios: servicios.join(","),
    orden: $("#orden").value,
  };
}

function construirUrl() {
  const parametros = new URLSearchParams({ ...estado.busqueda, ...obtenerFiltros() });
  for (const [clave, valor] of parametros.entries()) {
    if (!valor) parametros.delete(clave);
  }
  return `/hoteles?${parametros.toString()}`;
}

async function pedirHoteles() {
  const respuesta = await fetch(construirUrl());
  if (!respuesta.ok) {
    let detalle = "No se pudo completar la búsqueda.";
    try {
      const cuerpo = await respuesta.json();
      detalle = cuerpo.detail || detalle;
    } catch (_) { /* Se conserva el mensaje genérico. */ }
    throw new Error(detalle);
  }
  return respuesta.json();
}

async function pedirJson(url, opciones = {}) {
  const respuesta = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...opciones,
  });
  if (!respuesta.ok) {
    let detalle = "No se pudo completar la operación.";
    try {
      const cuerpo = await respuesta.json();
      detalle = cuerpo.detail || detalle;
    } catch (_) { /* Se conserva el mensaje genérico. */ }
    throw new Error(detalle);
  }
  return respuesta.json();
}

function formatearPrecio(valor) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format(valor);
}

function mostrarFallbackMapa(mostrar) {
  $("#mapa-fallback").hidden = !mostrar;
}

function inicializarMapa() {
  if (!window.L || !$("#mapa")) {
    mostrarFallbackMapa(true);
    return;
  }

  try {
    mapa = L.map("mapa", { scrollWheelZoom: false }).setView([24.5, -105.1], 7);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap",
      maxZoom: 19,
    }).addTo(mapa).on("tileerror", () => mostrarFallbackMapa(true));
    marcadores = L.layerGroup().addTo(mapa);
    mostrarFallbackMapa(false);
  } catch (_) {
    mostrarFallbackMapa(true);
  }
}

function actualizarMapa(hoteles) {
  if (!mapa || !marcadores) return;
  marcadores.clearLayers();
  const hotelesConCoordenadas = hoteles.filter((hotel) =>
    Number.isFinite(Number(hotel.latitud)) && Number.isFinite(Number(hotel.longitud))
  );
  if (!hotelesConCoordenadas.length) {
    mapa.setView([24.5, -105.1], 7);
    return;
  }

  const limites = [];
  hotelesConCoordenadas.forEach((hotel) => {
    const posicion = [Number(hotel.latitud), Number(hotel.longitud)];
    const marcador = L.marker(posicion).bindPopup(`
      <strong>${escaparHtml(hotel.nombre)}</strong><br>
      Total: ${formatearPrecio(hotel.habitacion.total)} MXN
    `);
    marcador.addTo(marcadores);
    limites.push(posicion);
  });
  if (limites.length === 1) mapa.setView(limites[0], 13);
  else mapa.fitBounds(limites, { padding: [24, 24] });
}

function tarjetaHotel(hotel) {
  const imagen = hotel.fotos?.[0] ? `img/${hotel.fotos[0]}` : "img/sin-imagen.svg";
  const servicios = (hotel.servicios || []).slice(0, 3)
    .map((servicio) => `<span class="etiqueta-servicio">${escaparHtml(servicio)}</span>`).join("");
  const estrellas = "★".repeat(hotel.estrellas) + "☆".repeat(5 - hotel.estrellas);
  const tarifas = (hotel.tarifas || []).map((tarifa) => `
    <li class="tarifa ${tarifa.es_mejor_precio ? "tarifa--mejor" : ""}">
      <span>${escaparHtml(tarifa.proveedor)}${tarifa.es_mejor_precio ? ' <strong class="insignia-mejor">Mejor precio</strong>' : ""}</span>
      <span><strong>${formatearPrecio(tarifa.total)}</strong><small>${formatearPrecio(tarifa.precio_noche)} por noche</small></span>
    </li>`).join("");
  const comparativa = tarifas
    ? `<div class="comparativa"><h4>Comparativa de precios <span>(datos simulados)</span></h4><ul>${tarifas || '<li class="tarifa-vacia">No hay tarifas de proveedores para este hotel.</li>'}</ul></div>`
    : "";
  return `
    <article class="hotel-card">
      <div class="hotel-card__imagen">
        <img src="${escaparHtml(imagen)}" alt="Imagen de ${escaparHtml(hotel.nombre)}" onerror="this.onerror=null;this.src='img/sin-imagen.svg';">
      </div>
      <div class="hotel-card__contenido">
        <div class="hotel-card__encabezado">
          <div>
            <p class="estrellas" aria-label="${hotel.estrellas} estrellas">${estrellas}</p>
            <h3>${escaparHtml(hotel.nombre)}</h3>
            <p class="ubicacion">${escaparHtml(hotel.ciudad)} · ${escaparHtml(hotel.direccion)}</p>
          </div>
          <strong class="puntuacion">${Number(hotel.puntuacion).toFixed(1)}</strong>
        </div>
        <div class="servicios">${servicios}</div>
        ${comparativa}
        <div class="hotel-card__precio">
          <div><span class="precio-noche">${formatearPrecio(hotel.habitacion.precio_noche)}</span> <span class="texto-suave">por noche</span><br><span class="texto-suave">${hotel.noches} noches · ${escaparHtml(hotel.habitacion.tipo)}</span></div>
          <div class="total"><span>Total</span><strong>${formatearPrecio(hotel.habitacion.total)}</strong></div>
        </div>
        <button class="boton boton--secundario boton--ancho boton-detalle" type="button" data-hotel-id="${hotel.id}">Ver hotel</button>
      </div>
    </article>`;
}

function parametrosDetalle() {
  return new URLSearchParams({
    entrada: estado.busqueda.entrada,
    salida: estado.busqueda.salida,
    huespedes: estado.busqueda.huespedes,
  });
}

function mostrarDetalleCargando() {
  $("#detalle-hotel").hidden = false;
  $("#detalle-contenido").innerHTML = '<div class="estado estado--cargando"><h2>Cargando detalle...</h2><p>Consultando habitaciones disponibles.</p></div>';
  $("#seccion-reserva").hidden = true;
  $("#detalle-hotel").scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderizarDetalle(hotel) {
  const fotos = hotel.fotos?.length ? hotel.fotos : ["sin-imagen.svg"];
  const galeria = fotos.map((foto) => `<img src="img/${escaparHtml(foto)}" alt="Imagen de ${escaparHtml(hotel.nombre)}" onerror="this.onerror=null;this.src='img/sin-imagen.svg';">`).join("");
  const habitaciones = hotel.habitaciones.map((habitacion) => `
    <article class="habitacion-detalle">
      <div><h4>${escaparHtml(habitacion.tipo)} · Habitación ${escaparHtml(habitacion.numero)}</h4><p>Capacidad para ${habitacion.capacidad} personas</p></div>
      <div class="habitacion-detalle__precio"><strong>${formatearPrecio(habitacion.total)}</strong><small>${formatearPrecio(habitacion.precio_noche)} por noche</small><button class="boton boton--principal" type="button" data-habitacion-id="${habitacion.id}">Reservar</button></div>
    </article>`).join("");
  $("#detalle-contenido").innerHTML = `
    <div class="detalle__encabezado"><div><p class="sobretitulo">Detalle del hotel</p><h2 id="titulo-detalle">${escaparHtml(hotel.nombre)}</h2><p class="ubicacion">${escaparHtml(hotel.ciudad)} · ${escaparHtml(hotel.direccion)}</p></div><strong class="puntuacion">${Number(hotel.puntuacion).toFixed(1)}</strong></div>
    <div class="galeria-detalle">${galeria}</div>
    <p class="detalle__descripcion">${escaparHtml(hotel.descripcion)}</p>
    <div class="servicios">${(hotel.servicios || []).map((servicio) => `<span class="etiqueta-servicio">${escaparHtml(servicio)}</span>`).join("")}</div>
    <h3 class="subtitulo-detalle">Habitaciones disponibles · ${hotel.noches} noches</h3>
    <div class="habitaciones-detalle">${habitaciones || '<p class="estado-vacio">No hay habitaciones disponibles para estas fechas.</p>'}</div>`;
  document.querySelectorAll("[data-habitacion-id]").forEach((boton) => {
    boton.addEventListener("click", () => seleccionarHabitacion(hotel, Number(boton.dataset.habitacionId)));
  });
}

async function abrirDetalle(hotelId) {
  if (!estado.busqueda) return;
  mostrarDetalleCargando();
  try {
    const hotel = await pedirJson(`/hoteles/${hotelId}?${parametrosDetalle()}`);
    estado.hotel = hotel;
    renderizarDetalle(hotel);
  } catch (error) {
    $("#detalle-contenido").innerHTML = `<div class="estado estado--error"><h2>No se pudo cargar el hotel</h2><p>${escaparHtml(error.message)}</p></div>`;
  }
}

function seleccionarHabitacion(hotel, habitacionId) {
  estado.hotel = hotel;
  estado.habitacion = hotel.habitaciones.find((habitacion) => habitacion.id === habitacionId);
  $("#seccion-reserva").hidden = false;
  $("#personas-reserva").value = estado.busqueda.huespedes;
  $("#resumen-reserva").textContent = `${hotel.nombre} · Habitación ${estado.habitacion.numero} · Total ${formatearPrecio(estado.habitacion.total)} MXN`;
  $("#mensaje-reserva").textContent = "";
  $("#seccion-reserva").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function confirmarReservacion(evento) {
  evento.preventDefault();
  if (!estado.hotel || !estado.habitacion) return;
  const personas = Number($("#personas-reserva").value);
  const mensaje = $("#mensaje-reserva");
  if (!$("#nombre-reserva").value.trim() || !$("#telefono-reserva").value.trim()) {
    mensaje.className = "mensaje-reserva mensaje-reserva--error";
    mensaje.textContent = "El nombre y el teléfono son obligatorios.";
    return;
  }
  if (!Number.isInteger(personas) || personas < 1 || personas > estado.habitacion.capacidad) {
    mensaje.className = "mensaje-reserva mensaje-reserva--error";
    mensaje.textContent = "El número de personas no es válido para esta habitación.";
    return;
  }
  try {
    mensaje.className = "mensaje-reserva mensaje-reserva--cargando";
    mensaje.textContent = "Registrando tu reservación...";
    const huesped = await pedirJson("/huespedes", { method: "POST", body: JSON.stringify({
      nombre: $("#nombre-reserva").value, telefono: $("#telefono-reserva").value, correo: $("#correo-reserva").value || null,
    }) });
    const reservacion = await pedirJson("/reservaciones", { method: "POST", body: JSON.stringify({
      huesped_id: huesped.id, habitacion_id: estado.habitacion.id,
      fecha_entrada: estado.busqueda.entrada, fecha_salida: estado.busqueda.salida,
      numero_personas: personas,
    }) });
    mensaje.className = "mensaje-reserva mensaje-reserva--exito";
    mensaje.textContent = `Reservación confirmada. Total: ${formatearPrecio(reservacion.total)} MXN.`;
    $("#form-reservacion").reset();
    cargarReservaciones();
  } catch (error) {
    mensaje.className = "mensaje-reserva mensaje-reserva--error";
    mensaje.textContent = error.message;
  }
}

function mostrarHoteles(hoteles) {
  if (!hoteles.length) {
    mostrarEstado("No encontramos hoteles", "Prueba con otras fechas, destino o filtros.", "vacio");
    $("#resumen-busqueda").textContent = "0 resultados";
    actualizarMapa([]);
    return;
  }
  estadoResultados.hidden = true;
  listaHoteles.innerHTML = hoteles.map(tarjetaHotel).join("");
  $("#resumen-busqueda").textContent = `${hoteles.length} resultado${hoteles.length === 1 ? "" : "s"}`;
  actualizarMapa(hoteles);
  document.querySelectorAll(".boton-detalle").forEach((boton) => {
    boton.addEventListener("click", () => abrirDetalle(Number(boton.dataset.hotelId)));
  });
}

function mostrarEstadoReservaciones(titulo, texto, tipo = "inicial") {
  const estadoReservaciones = $("#estado-reservaciones");
  estadoReservaciones.className = `estado estado--${tipo}`;
  estadoReservaciones.innerHTML = `<h3>${escaparHtml(titulo)}</h3><p>${escaparHtml(texto)}</p>`;
  estadoReservaciones.hidden = false;
  $("#lista-reservaciones").replaceChildren();
}

function tarjetaReservacion(reservacion) {
  const habitacion = reservacion.habitacion || {};
  return `<article class="reservacion-card">
    <div><h3>${escaparHtml(reservacion.hotel?.nombre || "Hotel")}</h3>
      <p>${escaparHtml(habitacion.tipo || "Habitación")} · Habitación ${escaparHtml(habitacion.numero || "")}</p>
      <p>Para ${escaparHtml(reservacion.huesped?.nombre || "Huésped")} · ${escaparHtml(reservacion.fecha_entrada)} al ${escaparHtml(reservacion.fecha_salida)}</p>
    </div>
    <div class="reservacion-card__total"><span>Total</span><strong>${formatearPrecio(reservacion.total)}</strong><small>Reservación activa</small></div>
  </article>`;
}

async function cargarReservaciones() {
  mostrarEstadoReservaciones("Cargando reservaciones...", "Consultando tus reservaciones activas.", "cargando");
  try {
    const reservaciones = await pedirJson("/reservaciones/activas");
    if (!reservaciones.length) {
      mostrarEstadoReservaciones("No tienes reservaciones activas", "Cuando confirmes una estancia aparecerá aquí.", "vacio");
      return;
    }
    $("#estado-reservaciones").hidden = true;
    $("#lista-reservaciones").innerHTML = reservaciones.map(tarjetaReservacion).join("");
  } catch (error) {
    mostrarEstadoReservaciones("No se pudieron cargar tus reservaciones", error.message, "error");
  }
}

async function buscar(evento) {
  evento?.preventDefault();
  try {
    mostrarErrorFormulario("");
    estado.busqueda = validarBusqueda();
    mostrarEstado("Buscando hoteles...", "Estamos consultando disponibilidad.", "cargando");
    contenedorResultados.setAttribute("aria-busy", "true");
    mostrarHoteles(await pedirHoteles());
  } catch (error) {
    mostrarErrorFormulario(error.message);
    mostrarEstado("No se pudo realizar la búsqueda", error.message, "error");
  } finally {
    contenedorResultados.setAttribute("aria-busy", "false");
  }
}

function limpiarFiltros() {
  $("#form-filtros").reset();
  $("input[name='estrellas'][value='']").checked = true;
  if (estado.busqueda) buscar();
}

function cerrarDetalle() {
  $("#detalle-hotel").hidden = true;
  estado.hotel = null;
  estado.habitacion = null;
}

$("#form-busqueda").addEventListener("submit", buscar);
$("#form-filtros").addEventListener("submit", buscar);
$("#limpiar-filtros").addEventListener("click", limpiarFiltros);
$("#volver-resultados").addEventListener("click", cerrarDetalle);
$("#form-reservacion").addEventListener("submit", confirmarReservacion);
$("#cargar-reservaciones").addEventListener("click", cargarReservaciones);
$("#enlace-reservaciones").addEventListener("click", cargarReservaciones);
$("input[name='estrellas'][value='']").checked = true;
inicializarMapa();
