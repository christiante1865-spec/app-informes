from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from functools import wraps
from flask_compress import Compress
import io
from sqlalchemy import text
from flask_migrate import Migrate

# DB
from extensions import db

# 🔥 IMPORTANTE: importar modelos
from models import *

# BLUEPRINTS
from routes.auth import auth_bp
from routes.alumnos import alumnos_bp
from routes.informes import informes_bp
from routes.archivos import archivos_bp

# -------------------------
# INIT APP
# -------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

Compress(app)

# -------------------------
# DATABASE CONFIG
# -------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# INIT DB
db.init_app(app)

# ✅ MIGRATIONS
migrate = Migrate(app, db)

# -------------------------
# CONFIG
# -------------------------
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
INSTANCE_FOLDER = os.path.join(BASE_DIR, "instance")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(INSTANCE_FOLDER, exist_ok=True)

# -------------------------
# CACHE
# -------------------------
@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

# -------------------------
# BLUEPRINTS
# -------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(alumnos_bp)
app.register_blueprint(informes_bp)
app.register_blueprint(archivos_bp)

# -------------------------
# LOGIN REQUIRED
# -------------------------
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper

# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def landing():
    return redirect(url_for("auth.login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        alumnos = db.session.execute(
            text("SELECT * FROM alumnos WHERE usuario_id = :uid ORDER BY id DESC LIMIT 5"),
            {"uid": session["usuario_id"]}
        ).fetchall()
    except Exception as e:
        print("❌ ERROR DASHBOARD:", e)
        alumnos = []

    return render_template("index.html", alumnos=alumnos)

@app.route("/crear_alumno", methods=["GET", "POST"])
@login_required
def crear_alumno():

    if request.method == "POST":
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")

        if not nombre or not edad:
            flash("Completa todos los campos ❌")
            return redirect(request.url)

        try:
            db.session.execute(
                text("INSERT INTO alumnos (nombre, edad, usuario_id) VALUES (:n, :e, :u)"),
                {"n": nombre, "e": edad, "u": session["usuario_id"]}
            )
            db.session.commit()
            flash("Alumno creado correctamente ✅")
        except Exception as e:
            db.session.rollback()
            print("❌ ERROR CREAR ALUMNO:", e)
            flash("Error al crear alumno ❌")

        return redirect(url_for("dashboard"))

    return render_template("crear_estudiante.html")

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)