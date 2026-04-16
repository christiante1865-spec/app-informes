from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# -------------------------
# DB
# -------------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


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

        db = get_db()
        user = db.execute(
            "SELECT * FROM usuarios WHERE email=?",
            (email,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["email"] = user["email"]

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

        hashed_password = generate_password_hash(password)

        db = get_db()
        try:
            db.execute(
                "INSERT INTO usuarios (email, password) VALUES (?, ?)",
                (email, hashed_password)
            )
            db.commit()

            flash("Usuario creado correctamente ✅")
            return redirect(url_for("auth.login"))

        except sqlite3.IntegrityError:
            flash("El usuario ya existe ❌")

        finally:
            db.close()

    return render_template("register.html")