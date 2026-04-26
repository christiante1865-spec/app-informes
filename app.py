from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from functools import wraps
from flask_compress import Compress
import io
from sqlalchemy import text

# DB
from extensions import db

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

# 🔥 CREAR TABLAS AUTOMÁTICAMENTE (SOLUCIÓN ERROR)
with app.app_context():
    db.create_all()

# -------------------------
# CONFIG
# -------------------------
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
INSTANCE_FOLDER = os.path.join(BASE_DIR, "instance")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# crear carpetas si no existen (IMPORTANTE EN RENDER)
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
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

# -------------------------
# LANDING
# -------------------------
@app.route("/")
def landing():
    return redirect(url_for("auth.login"))

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    alumnos = db.session.execute(
        text("SELECT * FROM alumnos WHERE usuario_id = :uid ORDER BY id DESC LIMIT 5"),
        {"uid": session["user_id"]}
    ).fetchall()

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

        db.session.execute(
            text("INSERT INTO alumnos (nombre, edad, usuario_id) VALUES (:n, :e, :u)"),
            {"n": nombre, "e": edad, "u": session["user_id"]}
        )
        db.session.commit()

        flash("Alumno creado correctamente ✅")
        return redirect(url_for("dashboard"))

    return render_template("crear_estudiante.html")

# -------------------------
# GENERADOR DE TEXTO
# -------------------------
def generar_texto_informe(alumno, conducta, rendimiento, observaciones):
    texto = f"Informe del estudiante {alumno.nombre}, {alumno.edad} años.\n\n"

    texto += "Conducta:\n"
    if "atencion" in conducta:
        texto += "- Mantiene la atención.\n"
    if "respeto" in conducta:
        texto += "- Respeta normas.\n"
    if "impulsividad" in conducta:
        texto += "- Presenta impulsividad.\n"
    if "participacion" in conducta:
        texto += "- Participa activamente.\n"

    texto += "\nRendimiento académico:\n"
    if "comprension" in rendimiento:
        texto += "- Buena comprensión.\n"
    if "tareas" in rendimiento:
        texto += "- Cumple tareas.\n"
    if "evaluaciones" in rendimiento:
        texto += "- Buen desempeño en evaluaciones.\n"
    if "autonomia" in rendimiento:
        texto += "- Trabaja de forma autónoma.\n"

    if observaciones:
        texto += f"\nObservaciones:\n{observaciones}\n"

    texto += "\nConclusión:\nSe recomienda continuar reforzando su desarrollo académico."

    return texto

# -------------------------
# GENERAR PDF
# -------------------------
def generar_pdf(texto):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    contenido = []

    contenido.append(Paragraph("<b>INFORME PEDAGÓGICO</b>", styles["Title"]))
    contenido.append(Spacer(1, 20))

    for linea in texto.split("\n"):
        contenido.append(Paragraph(linea, styles["Normal"]))
        contenido.append(Spacer(1, 10))

    contenido.append(Spacer(1, 20))
    contenido.append(Paragraph("Firma profesional", styles["Normal"]))

    doc.build(contenido)
    buffer.seek(0)

    return buffer

# -------------------------
# CREAR INFORME
# -------------------------
@app.route("/crear_informe/<int:alumno_id>", methods=["GET", "POST"])
@login_required
def crear_informe(alumno_id):

    alumno = db.session.execute(
        text("SELECT * FROM alumnos WHERE id = :id AND usuario_id = :uid"),
        {"id": alumno_id, "uid": session["user_id"]}
    ).fetchone()

    if not alumno:
        return "No autorizado ❌", 403

    if request.method == "POST":
        conducta = request.form.getlist("conducta[]")
        rendimiento = request.form.getlist("rendimiento[]")
        observaciones = request.form.get("observaciones")

        texto = generar_texto_informe(alumno, conducta, rendimiento, observaciones)

        db.session.execute(
            text("INSERT INTO informes (alumno_id, contenido) VALUES (:a, :c)"),
            {"a": alumno_id, "c": texto}
        )
        db.session.commit()

        pdf_buffer = generar_pdf(texto)

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"informe_{alumno_id}.pdf",
            mimetype="application/pdf"
        )

    return render_template("crear_informe.html", alumno=alumno)

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)