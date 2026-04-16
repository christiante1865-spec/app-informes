from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from routes.auth import auth_bp
from routes.alumnos import alumnos_bp
from routes.informes import informes_bp
from routes.archivos import archivos_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------------
# BLUEPRINTS
# -------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(alumnos_bp)
app.register_blueprint(informes_bp)
app.register_blueprint(archivos_bp)

# -------------------------
# CONFIG
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# DB
# -------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
# 🔒 LOGIN REQUIRED
# -------------------------
def login_required(func):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# -------------------------
# 🌍 LANDING
# -------------------------
@app.route("/")
def landing():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

# -------------------------
# 🏠 DASHBOARD
# -------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()

    alumnos = db.execute(
        "SELECT * FROM alumnos WHERE usuario_id = ? ORDER BY id DESC LIMIT 5",
        (session["user_id"],)
    ).fetchall()

    db.close()

    return render_template("index.html", alumnos=alumnos)

# -------------------------
# CREAR ALUMNO
# -------------------------
@app.route("/crear_alumno", methods=["GET", "POST"])
@login_required
def crear_alumno():

    if request.method == "POST":
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")

        if not nombre or not edad:
            flash("Completa todos los campos ❌")
            return redirect(request.url)

        db = get_db()
        db.execute(
            "INSERT INTO alumnos (nombre, edad, usuario_id) VALUES (?, ?, ?)",
            (nombre, edad, session["user_id"])
        )
        db.commit()
        db.close()

        flash("Alumno creado correctamente ✅")
        return redirect(url_for("dashboard"))

    return render_template("crear_estudiante.html")

# -------------------------
# SUBIR ARCHIVO
# -------------------------
@app.route("/subir_archivo/<int:alumno_id>", methods=["GET", "POST"])
@login_required
def subir_archivo(alumno_id):

    db = get_db()

    alumno = db.execute(
        "SELECT * FROM alumnos WHERE id = ? AND usuario_id = ?",
        (alumno_id, session["user_id"])
    ).fetchone()

    db.close()

    if not alumno:
        return "Acceso no autorizado ❌", 403

    carpeta_alumno = os.path.join(app.config["UPLOAD_FOLDER"], f"alumno_{alumno_id}")
    os.makedirs(carpeta_alumno, exist_ok=True)

    if request.method == "POST":

        if "archivo" not in request.files:
            flash("No se seleccionó archivo ❌")
            return redirect(request.url)

        archivo = request.files["archivo"]

        if archivo.filename == "":
            flash("Nombre de archivo vacío ❌")
            return redirect(request.url)

        if not archivo.filename.endswith(".pdf"):
            flash("Solo se permiten archivos PDF ❌")
            return redirect(request.url)

        filename = secure_filename(archivo.filename)
        ruta = os.path.join(carpeta_alumno, filename)
        archivo.save(ruta)

        flash("Archivo subido correctamente ✅")
        return redirect(request.url)

    archivos = os.listdir(carpeta_alumno)

    return render_template(
        "subir_archivo.html",
        alumno=alumno,
        archivos=archivos,
        alumno_id=alumno_id
    )

# -------------------------
# ELIMINAR ARCHIVO
# -------------------------
@app.route("/eliminar_archivo/<int:alumno_id>/<nombre>")
@login_required
def eliminar_archivo(alumno_id, nombre):

    carpeta_alumno = os.path.join(app.config["UPLOAD_FOLDER"], f"alumno_{alumno_id}")
    ruta = os.path.join(carpeta_alumno, nombre)

    if os.path.exists(ruta):
        os.remove(ruta)
        flash("Archivo eliminado 🗑️")
    else:
        flash("Archivo no encontrado ❌")

    return redirect(request.referrer or url_for("dashboard"))

# -------------------------
# VER ARCHIVO
# -------------------------
@app.route("/uploads/<int:alumno_id>/<filename>")
@login_required
def uploaded_file(alumno_id, filename):

    carpeta_alumno = os.path.join(app.config["UPLOAD_FOLDER"], f"alumno_{alumno_id}")
    return send_file(os.path.join(carpeta_alumno, filename))

# -------------------------
# DESCARGAR PDF
# -------------------------
@app.route("/descargar_pdf/<int:id>")
@login_required
def descargar_pdf(id):

    import io

    db = get_db()
    informe = db.execute(
        "SELECT * FROM informes WHERE id = ?",
        (id,)
    ).fetchone()
    db.close()

    if not informe:
        return "Informe no encontrado"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    contenido = [Paragraph(informe["contenido"], styles["Normal"])]

    doc.build(contenido)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"informe_{id}.pdf")

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)