from flask import Blueprint, render_template, session
from utils.auth import login_required
import sqlite3
import os

alumnos_bp = Blueprint('alumnos', __name__)

# -------------------------
# DB
# -------------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# 🔥 LISTAR ALUMNOS (MULTIUSUARIO)
# -------------------------
@alumnos_bp.route("/alumnos")
@login_required
def listar_alumnos():

    db = get_db()

    alumnos = db.execute(
        "SELECT * FROM alumnos WHERE usuario_id = ?",
        (session["user_id"],)
    ).fetchall()

    db.close()

    return render_template("alumnos.html", alumnos=alumnos)


# -------------------------
# 🔥 PERFIL DEL ALUMNO
# -------------------------
@alumnos_bp.route("/perfil_alumno/<int:id>")
@login_required
def perfil_alumno(id):

    db = get_db()

    alumno = db.execute(
        "SELECT * FROM alumnos WHERE id = ? AND usuario_id = ?",
        (id, session["user_id"])
    ).fetchone()

    if not alumno:
        db.close()
        return "Acceso no autorizado ❌", 403

    informes = db.execute(
        "SELECT * FROM informes WHERE alumno_id = ? ORDER BY id DESC",
        (id,)
    ).fetchall()

    db.close()

    # 🔥 ARCHIVOS DEL ALUMNO
    carpeta_alumno = os.path.join("uploads", f"alumno_{id}")

    if os.path.exists(carpeta_alumno):
        archivos = os.listdir(carpeta_alumno)
    else:
        archivos = []

    return render_template(
        "perfil_alumno.html",
        alumno=alumno,
        informes=informes,
        archivos=archivos
    )