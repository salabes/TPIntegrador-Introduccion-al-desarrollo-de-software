r"""
Precarga de la base de datos con selecciones historicas.

OJO: este script RESETEA la base (borra todo y la vuelve a crear) y la
deja cargada con las posiciones, los equipos y los planteles completos.

USO (parado en la carpeta backend, con el backend FRENADO):
    ..\venv\Scripts\python.exe precarga.py

Las imagenes son avatares generados a partir del nombre (siempre se ven).
Si queres una foto real, reemplaza el campo "imagen" del jugador por la URL
de la foto en la lista de abajo, o editalo despues desde la app.
"""

import os
import unicodedata
from urllib.parse import quote

from main import app
from models import db, Jugador, Equipo, Posicion

# Carpeta donde dejas las fotos de los jugadores (servida por el frontend en /img)
IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "img")
EXTENSIONES = (".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif")

# ---------------------------------------------------------------------------
# Posiciones (los IDs son fijos: el frontend los tiene hardcodeados)
#   lugar_en_formacion -> posicion:  1->1, 2->2, 3y4->3, 5->4,
#                                     6->5, 7y8->6, 9->7, 10y11->8
# ---------------------------------------------------------------------------
POSICIONES = [
    (1, "Arquero"),
    (2, "Lateral derecho"),
    (3, "Defensor central"),
    (4, "Lateral izquierdo"),
    (5, "Volante derecho"),
    (6, "Mediocampista central"),
    (7, "Volante izquierdo"),
    (8, "Delantero"),
]

# ---------------------------------------------------------------------------
# Equipos y planteles.
# Cada jugador: (lugar_en_formacion, posicion_id, nombre, apellido, edad, pie, puntaje)
#   - lugar_en_formacion = 1..11 para titulares, None para suplentes (banco)
# ---------------------------------------------------------------------------
EQUIPOS = [
    {
        "nombre": "Argentina 1986",
        "escudo": "https://flagcdn.com/w320/ar.png",
        "color": "6CB4EE",
        "jugadores": [
            (1,  1, "Nery",   "Pumpido",         28, "Derecha",   82),
            (2,  2, "Jose Luis", "Cuciuffo",     25, "Derecha",   80),
            (3,  3, "Jose Luis", "Brown",        30, "Derecha",   83),
            (4,  3, "Oscar",  "Ruggeri",         24, "Derecha",   86),
            (5,  4, "Julio",  "Olarticoechea",   28, "Izquierda", 80),
            (6,  5, "Ricardo", "Giusti",         30, "Derecha",   81),
            (7,  6, "Sergio", "Batista",         23, "Derecha",   82),
            (8,  6, "Hector", "Enrique",         24, "Derecha",   81),
            (9,  7, "Jorge",  "Burruchaga",      23, "Derecha",   86),
            (10, 8, "Diego",  "Maradona",        25, "Izquierda", 99),
            (11, 8, "Jorge",  "Valdano",         30, "Derecha",   87),
            # Suplentes
            (None, 3, "Daniel", "Passarella",    33, "Derecha",   88),
            (None, 8, "Pedro",  "Pasculli",      26, "Derecha",   80),
            (None, 6, "Claudio", "Borghi",       22, "Derecha",   79),
        ],
    },
    {
        "nombre": "Brasil 1970",
        "escudo": "https://flagcdn.com/w320/br.png",
        "color": "009C3B",
        "jugadores": [
            (1,  1, "Felix",   "Mielli",         32, "Derecha",   78),
            (2,  2, "Carlos",  "Alberto",        25, "Derecha",   90),
            (3,  3, "Hercules", "Brito",         30, "Derecha",   82),
            (4,  3, "Wilson",  "Piazza",         27, "Derecha",   83),
            (5,  4, "Everaldo", "Marques",       25, "Izquierda", 80),
            (6,  5, "Clodoaldo", "Tavares",      21, "Derecha",   84),
            (7,  6, "Gerson",  "de Oliveira",    29, "Izquierda", 88),
            (8,  6, "Roberto", "Rivelino",       24, "Izquierda", 89),
            (9,  7, "Jair",    "Jairzinho",      25, "Derecha",   89),
            (10, 8, "Edson",   "Pele",           29, "Derecha",   99),
            (11, 8, "Eduardo", "Tostao",         23, "Derecha",   87),
            # Suplentes
            (None, 7, "Paulo", "Cesar Lima",     21, "Derecha",   81),
            (None, 8, "Jonas", "Edu",            20, "Izquierda", 80),
            (None, 8, "Dario", "Maravilha",      24, "Derecha",   79),
        ],
    },
    {
        "nombre": "Francia 1998",
        "escudo": "https://flagcdn.com/w320/fr.png",
        "color": "0055A4",
        "jugadores": [
            (1,  1, "Fabien", "Barthez",         27, "Derecha",   86),
            (2,  2, "Lilian", "Thuram",          26, "Derecha",   88),
            (3,  3, "Marcel", "Desailly",        29, "Derecha",   88),
            (4,  3, "Laurent", "Blanc",          32, "Derecha",   86),
            (5,  4, "Bixente", "Lizarazu",       28, "Izquierda", 85),
            (6,  5, "Christian", "Karembeu",     27, "Derecha",   81),
            (7,  6, "Didier", "Deschamps",       29, "Derecha",   85),
            (8,  6, "Emmanuel", "Petit",         27, "Izquierda", 84),
            (9,  7, "Zinedine", "Zidane",        26, "Derecha",   97),
            (10, 8, "Youri",  "Djorkaeff",       30, "Derecha",   85),
            (11, 8, "Stephane", "Guivarch",      27, "Derecha",   78),
            # Suplentes
            (None, 8, "Thierry", "Henry",        20, "Derecha",   84),
            (None, 8, "David",  "Trezeguet",     20, "Derecha",   82),
            (None, 6, "Patrick", "Vieira",       22, "Derecha",   84),
            (None, 7, "Robert", "Pires",         24, "Derecha",   83),
        ],
    },
]


def avatar(nombre, apellido, color):
    """Avatar generado a partir del nombre. Siempre se ve."""
    nombre_completo = quote(f"{nombre} {apellido}")
    return (
        f"https://ui-avatars.com/api/?name={nombre_completo}"
        f"&size=256&background={color}&color=fff&bold=true&format=png"
    )


def slug(nombre, apellido):
    """Nombre de archivo esperado para la foto: 'Diego Maradona' -> 'diego-maradona'."""
    base = f"{nombre} {apellido}".strip().lower()
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")
    base = base.replace(" ", "-")
    return "".join(c for c in base if c.isalnum() or c == "-")


def resolver_imagen(nombre, apellido, color):
    """Si hay una foto en frontend/img con el nombre del jugador, la usa.
    Si no, cae en el avatar generado."""
    s = slug(nombre, apellido)
    for ext in EXTENSIONES:
        if os.path.exists(os.path.join(IMG_DIR, s + ext)):
            return f"/img/{s}{ext}"
    return avatar(nombre, apellido, color)


def precargar():
    print("Reseteando la base...")
    db.drop_all()
    db.create_all()

    print("Cargando posiciones...")
    for pos_id, nombre in POSICIONES:
        db.session.add(Posicion(id=pos_id, nombre=nombre))
    db.session.flush()

    total_jugadores = 0
    fotos_reales = [0]
    for datos_equipo in EQUIPOS:
        equipo = Equipo(nombre=datos_equipo["nombre"], escudo=datos_equipo["escudo"])
        db.session.add(equipo)
        db.session.flush()  # para tener equipo.id
        print(f"  + Equipo: {equipo.nombre}")

        color = datos_equipo["color"]
        for lugar, pos_id, nombre, apellido, edad, pie, puntaje in datos_equipo["jugadores"]:
            imagen = resolver_imagen(nombre, apellido, color)
            if imagen.startswith("/img/"):
                print(f"      foto: {nombre} {apellido} -> {imagen}")
                fotos_reales[0] += 1

            jugador = Jugador(
                nombre=nombre,
                apellido=apellido,
                edad=edad,
                pierna_habil=pie,
                puntaje=puntaje,
                imagen=imagen,
                equipo_id=equipo.id,
                posicion_id=pos_id,
                lugar_en_formacion=lugar,
            )
            db.session.add(jugador)
            total_jugadores += 1

    db.session.commit()
    print(f"\nListo. {len(EQUIPOS)} equipos y {total_jugadores} jugadores cargados.")
    print(f"{fotos_reales[0]} con foto propia de frontend/img, el resto con avatar.")


if __name__ == "__main__":
    if "sqlalchemy" not in app.extensions:
        db.init_app(app)
    with app.app_context():
        precargar()
