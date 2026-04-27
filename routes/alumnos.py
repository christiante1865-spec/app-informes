from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import Alumno

alumnos_bp = Blueprint("alumnos", __name__)

# -------------------------
# CREAR ALUMNO
# -------------------------
@alumnos_bp.route("/crear_alumno", methods=["GET", "POST"])
def crear_alumno():

    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            nombre = request.form.get("nombre")
            edad = request.form.get("edad")

            if not nombre or not edad:
                flash("Todos los campos son obligatorios ❌")
                return redirect(url_for("alumnos.crear_alumno"))

            nuevo_alumno = Alumno(
                nombre=nombre,
                edad=int(edad),
                usuario_id=usuario_id
            )

            db.session.add(nuevo_alumno)
            db.session.commit()

            flash("Alumno creado correctamente ✅")
            return redirect(url_for("dashboard"))

        except Exception as e:
            db.session.rollback()
            print("❌ ERROR CREAR ALUMNO:", e)
            flash("Error al crear alumno ❌")
            return redirect(url_for("alumnos.crear_alumno"))

    return render_template("crear_alumno.html")


# -------------------------
# LISTAR ALUMNOS
# -------------------------
@alumnos_bp.route("/alumnos")
def listar_alumnos():

    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión")
        return redirect(url_for("auth.login"))

    alumnos = Alumno.query.filter_by(usuario_id=usuario_id).order_by(Alumno.id.desc()).all()

    return render_template("alumnos.html", alumnos=alumnos)


# -------------------------
# PERFIL ALUMNO (🔴 ESTE TE FALTABA)
# -------------------------
@alumnos_bp.route("/alumno/<int:id>")
def perfil_alumno(id):

    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión")
        return redirect(url_for("auth.login"))

    alumno = Alumno.query.filter_by(id=id, usuario_id=usuario_id).first()

    if not alumno:
        flash("Alumno no encontrado ❌")
        return redirect(url_for("alumnos.listar_alumnos"))

    return render_template("perfil_alumno.html", alumno=alumno)