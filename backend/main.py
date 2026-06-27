from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Jugador, Equipo, Posicion

app = Flask(__name__)
CORS(app)
port = 5000

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/seleccioneshistoricas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/equipos', methods=['GET'])
def get_equipos():
    try:
        equipos = Equipo.query.all()
        equipos_data = []
        for equipo in equipos:
            equipo_data = {
                'id': equipo.id,
                'nombre': equipo.nombre,
                'escudo': equipo.escudo
            }
            equipos_data.append(equipo_data)
        return jsonify(equipos_data)
    except:
        return jsonify({'mensaje': 'No hay equipos'}), 204

@app.route('/equipos/<id_equipo>/formacion', methods=['GET'])
def get_jugadores_en_formacion(id_equipo):
    try:
        jugadores = Jugador.query.filter(
            Jugador.equipo_id == id_equipo,
            Jugador.lugar_en_formacion != None
        ).all()
    
        jugadores_data = []
        for jugador in jugadores:
            jugador_data = {
                'id': jugador.id,
                'equipo_id': jugador.equipo_id,
                'posicion_id': jugador.posicion_id,
                'nombre': jugador.nombre,
                'apellido': jugador.apellido,
                'edad': jugador.edad,
                'pierna_habil': jugador.pierna_habil,
                'puntaje': jugador.puntaje,
                'imagen': jugador.imagen,
                'lugar_en_formacion': jugador.lugar_en_formacion
            }
            jugadores_data.append(jugador_data)
        return jsonify(jugadores_data)
    except:
        return jsonify({'mensaje': 'No hay jugadores en la formación'}), 204

@app.route('/equipos/<id_equipo>/posiciones/<id_posicion>', methods=['GET'])
def get_jugadores_por_posicion(id_equipo, id_posicion):
    try:
        jugadores = Jugador.query.filter(
            Jugador.equipo_id == id_equipo, 
            Jugador.posicion_id == id_posicion,
            Jugador.lugar_en_formacion == None
        ).all()

        jugadores_data = []
        for jugador in jugadores:
            jugador_data = {
                'id': jugador.id,
                'equipo_id': jugador.equipo_id,
                'posicion_id': jugador.posicion_id,
                'nombre': jugador.nombre,
                'apellido': jugador.apellido,
                'edad': jugador.edad,
                'pierna_habil': jugador.pierna_habil,
                'puntaje': jugador.puntaje,
                'imagen': jugador.imagen,
                'lugar_en_formacion': jugador.lugar_en_formacion
            }
            jugadores_data.append(jugador_data)
        return jsonify(jugadores_data)
    except:
        return jsonify({'mensaje': 'No hay jugadores en esa posición'}), 204

@app.route('/equipos/<id_equipo>/jugadores', methods=['POST'])
def crear_jugador(id_equipo):
    try:
        nombre = request.json.get('nombre')
        apellido = request.json.get('apellido')
        edad = request.json.get('edad')
        pierna_habil = request.json.get('pierna_habil')
        posicion_id = request.json.get('posicion_id')
        puntaje = request.json.get('puntaje')
        imagen = request.json.get('imagen')

        if puntaje is not None and (puntaje < 0 or puntaje > 100):
            return jsonify({'mensaje': 'El puntaje debe estar entre 0 y 100'}), 400

        nuevo_jugador = Jugador(
            nombre=nombre,
            apellido=apellido,
            edad=edad,
            pierna_habil=pierna_habil,
            puntaje=puntaje,
            imagen=imagen,
            equipo_id=id_equipo,
            posicion_id=posicion_id
        )
        db.session.add(nuevo_jugador)
        db.session.commit()

        return jsonify({'mensaje': 'El jugador se ha creado correctamente'}), 201
    except:
        return jsonify({'mensaje': 'Error al crear el jugador'}), 500


@app.route('/jugadores/<id_jugador>', methods=['DELETE'])
def eliminar_jugador(id_jugador):
    try:
        jugador = Jugador.query.filter(
            Jugador.id == id_jugador
        ).first()

        if not jugador:
            return jsonify({'mensaje': 'Jugador no encontrado'}), 404

        db.session.delete(jugador)
        db.session.commit()

        return jsonify({'mensaje': 'El jugador ha sido eliminado correctamente'}), 200
    except:
        return jsonify({'mensaje': 'Error al eliminar el jugador'}), 500

@app.route('/jugadores/<id_jugador>', methods=['PUT'])
def agregar_jugador_formacion(id_jugador):
    try:
        lugar_en_formacion = request.json.get('lugar_formacion')

        if lugar_en_formacion is None:
            return jsonify({'mensaje': 'Debes ingresar un lugar en la formacion'}), 400
        
        if lugar_en_formacion < 1 or lugar_en_formacion > 11 :
            return jsonify({'mensaje': 'El lugar en la formacion que ingreso es invalido'}), 400
        

        jugador = db.session.get(Jugador, id_jugador)

        if jugador is None:
            return jsonify({'mensaje': 'Jugador no encontrado'}), 404
        
        jugador_reeemplazado = Jugador.query.filter(
            Jugador.equipo_id == jugador.equipo_id,
            Jugador.lugar_en_formacion == lugar_en_formacion
        ).first()
        
        if jugador_reeemplazado:
            jugador_reeemplazado.lugar_en_formacion = None
            db.session.commit()

        jugador.lugar_en_formacion = lugar_en_formacion
        db.session.commit()

        return jsonify({'mensaje': 'Ubicación en la formación actualizada correctamente'}), 200
    except:
        return jsonify({'mensaje': 'Error al actualizar la ubicación en la formación'}), 500

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(port=port, debug=True)
