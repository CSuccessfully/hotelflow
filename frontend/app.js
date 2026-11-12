const estado = {
  fechaEntrada: "",
  fechaSalida: "",
  habitacion: null,
};

const $ = (selector) => document.querySelector(selector);
const mensaje = $("#mensaje");

function mostrarMensaje(texto, tipo) {
  mensaje.textContent = texto;
  mensaje.className = `mensaje mensaje--${tipo}`;
  mensaje.hidden = false;
}

function ocultarMensaje() {
  mensaje.hidden = true;
}

function errorDeRespuesta(respuesta) {
  return respuesta.json()
    .then((cuerpo) => {
      if (typeof cuerpo.detail === "string") return cuerpo.detail;
      if (Array.isArray(cuerpo.detail)) {
        return cuerpo.detail.map((item) => item.msg).join(". ");
      }
      return "No se pudo completar la operación.";
    })
    .catch(() => "No se pudo completar la operación.");
}

async function pedirApi(url, opciones = {}) {
  const respuesta = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(opciones.headers || {}) },
    ...opciones,
  });
  if (!respuesta.ok) throw new Error(await errorDeRespuesta(respuesta));
  if (respuesta.status === 204) return null;
  return respuesta.json();
}

function validarFechas() {
  const entrada = $("#fecha-entrada").value;
  const salida = $("#fecha-salida").value;
  if (!entrada || !salida) throw new Error("Captura la fecha de entrada y la fecha de salida.");
  if (salida <= entrada) throw new Error("La fecha de salida debe ser posterior a la de entrada.");
  return { entrada, salida };
}

function mostrarHabitaciones(habitaciones) {
  const contenedor = $("#resultados-disponibilidad");
  contenedor.replaceChildren();
  if (!habitaciones.length) {
    contenedor.innerHTML = '<p class="vacio">No hay habitaciones disponibles para esas fechas.</p>';
    return;
  }
  const plantilla = $("#plantilla-habitacion");
  habitaciones.forEach((habitacion) => {
    const elemento = plantilla.content.cloneNode(true);
    const tarjeta = elemento.querySelector(".habitacion");
    elemento.querySelector(".habitacion__numero").textContent = `Habitación ${habitacion.numero}`;
    elemento.querySelector(".habitacion__detalle").textContent = `${habitacion.tipo} · Capacidad para ${habitacion.capacidad}`;
    elemento.querySelector("button").addEventListener("click", () => seleccionarHabitacion(habitacion, tarjeta));
    contenedor.appendChild(elemento);
  });
}

function seleccionarHabitacion(habitacion, tarjeta) {
  estado.habitacion = habitacion;
  document.querySelectorAll(".habitacion").forEach((item) => item.classList.remove("seleccionada"));
  tarjeta.classList.add("seleccionada");
  $("#habitacion-seleccionada").className = "seleccion seleccion--activa";
  $("#habitacion-seleccionada").textContent = `Habitación ${habitacion.numero} seleccionada · ${habitacion.tipo}`;
  $("#boton-reservar").disabled = false;
}

async function buscarDisponibilidad(evento) {
  evento.preventDefault();
  try {
    const fechas = validarFechas();
    estado.fechaEntrada = fechas.entrada;
    estado.fechaSalida = fechas.salida;
    mostrarMensaje("Buscando habitaciones disponibles...", "cargando");
    const habitaciones = await pedirApi(`/habitaciones/disponibles?fecha_entrada=${encodeURIComponent(fechas.entrada)}&fecha_salida=${encodeURIComponent(fechas.salida)}`);
    estado.habitacion = null;
    $("#boton-reservar").disabled = true;
    $("#habitacion-seleccionada").className = "seleccion aviso";
    $("#habitacion-seleccionada").textContent = "Primero busca y elige una habitación.";
    mostrarHabitaciones(habitaciones);
    mostrarMensaje(`${habitaciones.length} habitación(es) disponible(s).`, "exito");
  } catch (error) {
    mostrarMensaje(error.message, "error");
  }
}

async function crearReservacion(evento) {
  evento.preventDefault();
  if (!estado.habitacion) {
    mostrarMensaje("Elige una habitación disponible antes de reservar.", "error");
    return;
  }
  const boton = $("#boton-reservar");
  boton.disabled = true;
  try {
    mostrarMensaje("Registrando huésped...", "cargando");
    const huesped = await pedirApi("/huespedes", {
      method: "POST",
      body: JSON.stringify({
        nombre: $("#nombre").value,
        telefono: $("#telefono").value,
        correo: $("#correo").value || null,
      }),
    });
    mostrarMensaje("Creando reservación...", "cargando");
    await pedirApi("/reservaciones", {
      method: "POST",
      body: JSON.stringify({
        huesped_id: huesped.id,
        habitacion_id: estado.habitacion.id,
        fecha_entrada: estado.fechaEntrada,
        fecha_salida: estado.fechaSalida,
      }),
    });
    mostrarMensaje("Reservación creada correctamente.", "exito");
    $("#form-reservacion").reset();
    estado.habitacion = null;
    boton.disabled = true;
    $("#habitacion-seleccionada").className = "seleccion aviso";
    $("#habitacion-seleccionada").textContent = "Primero busca y elige una habitación.";
    await cargarReservacionesActivas();
  } catch (error) {
    boton.disabled = false;
    mostrarMensaje(error.message, "error");
  }
}

function mostrarReservaciones(reservaciones) {
  const lista = $("#reservaciones-activas");
  lista.replaceChildren();
  if (!reservaciones.length) {
    lista.innerHTML = '<p class="vacio">No hay reservaciones activas.</p>';
    return;
  }
  reservaciones.forEach((reservacion) => {
    const tarjeta = document.createElement("article");
    tarjeta.className = "reservacion";
    tarjeta.innerHTML = `
      <div>
        <p class="reservacion__nombre">${escaparHtml(reservacion.huesped.nombre)}</p>
        <p class="reservacion__detalle">Habitación ${escaparHtml(reservacion.habitacion.numero)} · ${escaparHtml(reservacion.huesped.telefono)}</p>
        <p class="reservacion__fecha">${reservacion.fecha_entrada} → ${reservacion.fecha_salida}</p>
      </div>
      <button class="boton boton--pequeno" type="button">Cancelar</button>`;
    tarjeta.querySelector("button").addEventListener("click", () => cancelarReservacion(reservacion.id));
    lista.appendChild(tarjeta);
  });
}

function escaparHtml(valor) {
  const elemento = document.createElement("span");
  elemento.textContent = valor ?? "";
  return elemento.innerHTML;
}

async function cargarReservacionesActivas() {
  const lista = $("#reservaciones-activas");
  lista.innerHTML = '<p class="vacio">Cargando reservaciones...</p>';
  try {
    mostrarReservaciones(await pedirApi("/reservaciones/activas"));
  } catch (error) {
    lista.innerHTML = `<p class="vacio">${escaparHtml(error.message)}</p>`;
  }
}

async function cancelarReservacion(id) {
  if (!window.confirm("¿Deseas cancelar esta reservación?")) return;
  try {
    mostrarMensaje("Cancelando reservación...", "cargando");
    await pedirApi(`/reservaciones/${id}`, { method: "DELETE" });
    mostrarMensaje("Reservación cancelada. La habitación quedó disponible.", "exito");
    await cargarReservacionesActivas();
  } catch (error) {
    mostrarMensaje(error.message, "error");
  }
}

$("#form-disponibilidad").addEventListener("submit", buscarDisponibilidad);
$("#form-reservacion").addEventListener("submit", crearReservacion);
$("#boton-actualizar").addEventListener("click", cargarReservacionesActivas);
cargarReservacionesActivas();
