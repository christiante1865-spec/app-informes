from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import Usuario

auth_bp = Blueprint('auth', __name__)


# -------------------------
# 🔐 LOGIN
# -------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Completa todos los campos ❌")
            return redirect(request.url)

        # ✅ Buscar usuario en PostgreSQL (NO sqlite)
        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # 🔥 CLAVE: mismo nombre que usamos en alumnos
            session["usuario_id"] = user.id
            session["email"] = user.email

            return redirect(url_for("dashboard"))
        else:
            flash("Credenciales incorrectas ❌")

    return render_template("login.html")


# -------------------------
# 🔓 LOGOUT
# -------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# -------------------------
# 📝 REGISTRO
# -------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Completa todos los campos ❌")
            return redirect(request.url)

        # Verificar si ya existe
        user_exist = Usuario.query.filter_by(email=email).first()
        if user_exist:
            flash("El usuario ya existe ❌")
            return redirect(request.url)

        hashed_password = generate_password_hash(password)

        try:
            nuevo_usuario = Usuario(
                email=email,
                password=hashed_password
            )

            db.session.add(nuevo_usuario)
            db.session.commit()

            flash("Usuario creado correctamente ✅")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            print("❌ ERROR REGISTRO:", e)
            flash("Error al crear usuario ❌")

    return render_template("register.html")