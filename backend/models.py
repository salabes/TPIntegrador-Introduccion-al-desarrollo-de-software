from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Jugador(db.Model):
    __tablename__ = 'jugadores'
    id = db.Column(db.Integer, primary_key=True)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'))
    posicion_id = db.Column(db.Integer, db.ForeignKey('posiciones.id'))
    nombre = db.Column(db.String[255], nullable=False)
    apellido = db.Column(db.String[255], nullable=False)
    edad = db.Column(db.Integer, nullable=True)
    pierna_habil = db.Column(db.String[255], nullable=True)
    puntaje = db.Column(db.Integer, nullable=True)
    imagen = db.Column(db.String[1024], nullable=True)
    lugar_en_formacion = db.Column(db.Integer, nullable=True)

class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String[255], nullable=False)
    escudo = db.Column(db.String[255], nullable=True)

class Posicion(db.Model):
    __tablename__ = 'posiciones'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String[255], nullable=False)
