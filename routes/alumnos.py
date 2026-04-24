from flask import Blueprint, render_template, session
from sqlalchemy import text
from app import db
from functools import wraps

# Si ya tienes login_required en utils.auth puedes importar ese en vez de este
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            from flask import redirect, url_for
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper

alumnos_bp = Blueprint('alumnos', __name__)

# -------------------------
# 🔥 LISTAR ALUMNOS (MULTIUSUARIO)
# -------------------------
@alumnos_bp.route("/alumnos")
@login_required
def listar_alumnos():

    alumnos = db.session.execute(
        text("SELECT * FROM alumnos WHERE usuario_id = :uid"),
        {"uid": session["user_id"]}
    ).fetchall()

    return render_template("alumnos.html", alumnos=alumnos)


# -------------------------
# 🔥 PERFIL DEL ALUMNO
# -------------------------
@alumnos_bp.route("/perfil_alumno/<int:id>")
@login_required
def perfil_alumno(id):

    alumno = db.session.execute(
        text("SELECT * FROM alumnos WHERE id = :id AND usuario_id = :uid"),
        {"id": id, "uid": session["user_id"]}
    ).fetchone()

    if not alumno:
        return "Acceso no autorizado ❌", 403

    informes = db.session.execute(
        text("SELECT * FROM informes WHERE alumno_id = :id ORDER BY id DESC"),
        {"id": id}
    ).fetchall()

    # 📂 Archivos del alumno
    import os
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