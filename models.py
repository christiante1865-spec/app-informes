from extensions import db
from datetime import datetime

# -------------------------
# USUARIO
# -------------------------
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    alumnos = db.relationship("Alumno", backref="usuario", lazy=True)


# -------------------------
# ALUMNO
# -------------------------
class Alumno(db.Model):
    __tablename__ = "alumnos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    informes = db.relationship("Informe", backref="alumno", lazy=True)


# -------------------------
# INFORME
# -------------------------
class Informe(db.Model):
    __tablename__ = "informes"

    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)

    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"), nullable=False)

    fecha = db.Column(db.DateTime, default=datetime.utcnow)