/* ============================================================
   Construye una carta de jugador estilo FIFA / FUT.
   Uso:  const carta = crearCartaFifa(jugador, [boton1, boton2])
   Devuelve un elemento listo para insertar en el DOM.
   ============================================================ */

const FUT_POSICIONES = {
    1: "ARQ",
    2: "LD",
    3: "DFC",
    4: "LI",
    5: "MD",
    6: "MC",
    7: "MI",
    8: "DEL",
};

function futTier(puntaje) {
    if (puntaje === null || puntaje === undefined) return "fut--bronze";
    if (puntaje >= 88) return "fut--elite";
    if (puntaje >= 80) return "fut--gold";
    if (puntaje >= 75) return "fut--silver";
    return "fut--bronze";
}

function futPieAbrev(pie) {
    if (!pie) return "-";
    const p = pie.toLowerCase();
    if (p.startsWith("i")) return "IZQ";
    if (p.startsWith("d")) return "DER";
    return pie.toUpperCase();
}

function futIniciales(nombre, apellido) {
    const a = (nombre || "").trim().charAt(0);
    const b = (apellido || "").trim().charAt(0);
    return (a + b).toUpperCase() || "?";
}

/* Avatar generado localmente (no usa internet): SVG con las iniciales.
   Se usa como respaldo si el jugador no tiene foto o si la URL falla. */
function futAvatarLocal(nombre, apellido) {
    const iniciales = futIniciales(nombre, apellido);
    const svg =
        "<svg xmlns='http://www.w3.org/2000/svg' width='104' height='104'>" +
        "<rect width='104' height='104' fill='#243240'/>" +
        "<text x='52' y='52' dy='.35em' text-anchor='middle' " +
        "font-family='Arial' font-size='42' font-weight='bold' fill='#ffffff'>" +
        iniciales + "</text></svg>";
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
}

function crearCartaFifa(jugador, botones) {
    const puntaje = jugador.puntaje;
    const posicion = FUT_POSICIONES[jugador.posicion_id] || "";
    const nombreCarta = jugador.apellido || jugador.nombre || "";

    const carta = document.createElement("div");
    carta.className = `fut ${futTier(puntaje)}`;

    const respaldo = futAvatarLocal(jugador.nombre, jugador.apellido);

    carta.innerHTML = `
        <div class="fut__header">
            <div>
                <div class="fut__rating">${puntaje !== null && puntaje !== undefined ? puntaje : "--"}</div>
                <div class="fut__pos">${posicion}</div>
            </div>
            <div class="fut__pie">${futPieAbrev(jugador.pierna_habil)}<small>pie</small></div>
        </div>
        <img class="fut__photo" src="${jugador.imagen || respaldo}" alt="${nombreCarta}">
        <div class="fut__name" title="${jugador.nombre || ""} ${jugador.apellido || ""}">${nombreCarta}</div>
        <div class="fut__stats">
            <div class="fut__stat"><b>${jugador.edad != null ? jugador.edad : "-"}</b>edad</div>
            <div class="fut__stat"><b>${futPieAbrev(jugador.pierna_habil)}</b>pie</div>
            <div class="fut__stat"><b>${posicion || "-"}</b>pos</div>
        </div>
    `;

    /* Si la foto remota falla (sin internet o bloqueada), usa el avatar local. */
    const foto = carta.querySelector(".fut__photo");
    foto.addEventListener("error", function () {
        if (foto.src !== respaldo) {
            foto.src = respaldo;
        }
    });

    const wrap = document.createElement("div");
    wrap.className = "fut-wrap";
    wrap.append(carta);

    if (botones && botones.length) {
        const acciones = document.createElement("div");
        acciones.className = "fut-acciones";
        botones.forEach((boton) => acciones.append(boton));
        wrap.append(acciones);
    }

    return wrap;
}
