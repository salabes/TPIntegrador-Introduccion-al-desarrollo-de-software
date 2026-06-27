r"""
Script para cargar jugadores en la base de datos.

USO:
  1. Edita la lista JUGADORES de abajo con los que quieras.
  2. Corre:  ..\venv\Scripts\python.exe seed.py
     (parado en la carpeta backend, con el backend SIN necesidad de estar corriendo)

Cada jugador indica su equipo y posicion POR NOMBRE. Si el equipo o la
posicion no existen todavia, el script los crea automaticamente.

Campos de cada jugador:
  - nombre            (texto, obligatorio)
  - apellido          (texto, obligatorio)
  - edad              (numero, opcional -> None)
  - pierna_habil      "Derecha" / "Izquierda" (opcional -> None)
  - equipo            nombre del equipo (obligatorio)
  - posicion          nombre de la posicion (obligatorio)
  - lugar_en_formacion  numero 1..11 si entra en la formacion titular,
                        o None si esta "en el banco" (opcional -> None)
"""

from main import app
from models import db, Jugador, Equipo, Posicion

# ---------------------------------------------------------------------------
# EDITA ESTA LISTA CON LOS JUGADORES QUE QUIERAS CARGAR
# ---------------------------------------------------------------------------
JUGADORES = [
    {
        "nombre": "Emiliano",
        "apellido": "Martinez",
        "edad": 32,
        "pierna_habil": "Derecha",
        "equipo": "Argentina",
        "posicion": "Arquero",
        "lugar_en_formacion": 1,
    },
    {
        "nombre": "Lionel",
        "apellido": "Messi",
        "edad": 38,
        "pierna_habil": "Izquierda",
        "equipo": "Argentina",
        "posicion": "Delantero",
        "lugar_en_formacion": 10,
    },
    {
        "nombre": "Julian",
        "apellido": "Alvarez",
        "edad": 25,
        "pierna_habil": "Derecha",
        "equipo": "Argentina",
        "posicion": "Delantero",
        "lugar_en_formacion": None,   # en el banco
    },
]
# ---------------------------------------------------------------------------


def get_or_create_equipo(nombre):
    equipo = Equipo.query.filter_by(nombre=nombre).first()
    if equipo is None:
        equipo = Equipo(nombre=nombre, escudo=None)
        db.session.add(equipo)
        db.session.flush()  # para que tenga id antes del commit
        print(f"  + Equipo creado: {nombre}")
    return equipo


def get_or_create_posicion(nombre):
    posicion = Posicion.query.filter_by(nombre=nombre).first()
    if posicion is None:
        posicion = Posicion(nombre=nombre)
        db.session.add(posicion)
        db.session.flush()
        print(f"  + Posicion creada: {nombre}")
    return posicion


def cargar_jugadores():
    creados = 0
    omitidos = 0

    for datos in JUGADORES:
        equipo = get_or_create_equipo(datos["equipo"])
        posicion = get_or_create_posicion(datos["posicion"])

        # Evita duplicar el mismo jugador (mismo nombre+apellido en el mismo equipo)
        ya_existe = Jugador.query.filter_by(
            nombre=datos["nombre"],
            apellido=datos["apellido"],
            equipo_id=equipo.id,
        ).first()

        if ya_existe:
            print(f"  = Ya existia, se omite: {datos['nombre']} {datos['apellido']} ({datos['equipo']})")
            omitidos += 1
            continue

        jugador = Jugador(
            nombre=datos["nombre"],
            apellido=datos["apellido"],
            edad=datos.get("edad"),
            pierna_habil=datos.get("pierna_habil"),
            equipo_id=equipo.id,
            posicion_id=posicion.id,
            lugar_en_formacion=datos.get("lugar_en_formacion"),
        )
        db.session.add(jugador)
        print(f"  + Jugador cargado: {datos['nombre']} {datos['apellido']} ({datos['equipo']} - {datos['posicion']})")
        creados += 1

    db.session.commit()
    print(f"\nListo. {creados} jugador(es) nuevo(s), {omitidos} omitido(s).")


if __name__ == "__main__":
    # main.py solo hace db.init_app(app) dentro de su bloque __main__,
    # asi que al importarlo desde aca hay que inicializar la conexion.
    if "sqlalchemy" not in app.extensions:
        db.init_app(app)
    with app.app_context():
        db.create_all()  # por las dudas, asegura que existan las tablas
        cargar_jugadores()
