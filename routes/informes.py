from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

informes_bp = Blueprint('informes', __name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# 🔥 CREAR INFORME
# -------------------------
@informes_bp.route('/crear_informe/<int:id>', methods=["GET", "POST"])
def crear_informe(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alumnos WHERE id = ?", (id,))
    alumno = cursor.fetchone()

    if not alumno:
        conn.close()
        return "Alumno no encontrado"

    if request.method == "POST":

        conducta = request.form.getlist("conducta[]")
        rendimiento = request.form.getlist("rendimiento[]")
        observaciones = request.form.get("observaciones")

        if not conducta or not rendimiento:
            flash("Debes completar los campos ❌")
            conn.close()
            return redirect(request.url)

        texto = generar_informe(
            alumno["nombre"],
            alumno["edad"],
            conducta,
            rendimiento,
            observaciones
        )

        cursor.execute(
            "INSERT INTO informes (alumno_id, contenido) VALUES (?, ?)",
            (id, texto)
        )

        conn.commit()
        conn.close()

        flash("Informe generado ✅")

        return redirect(url_for("alumnos.perfil_alumno", id=id))

    conn.close()
    return render_template("crear_informe.html", alumno=alumno)


# -------------------------
# 🧠 GENERADOR TEXTO
# -------------------------
def generar_informe(nombre, edad, conducta, rendimiento, observaciones):

    texto = f"Informe del alumno {nombre}, {edad} años.\n\n"

    texto += "Conducta:\n"
    if "atencion" in conducta:
        texto += "- Mantiene la atención\n"
    if "respeto" in conducta:
        texto += "- Respeta normas\n"
    if "impulsividad" in conducta:
        texto += "- Presenta impulsividad\n"
    if "participacion" in conducta:
        texto += "- Participa en clases\n"

    texto += "\nRendimiento:\n"
    if "comprension" in rendimiento:
        texto += "- Buena comprensión\n"
    if "tareas" in rendimiento:
        texto += "- Cumple tareas\n"
    if "evaluaciones" in rendimiento:
        texto += "- Buen desempeño\n"
    if "autonomia" in rendimiento:
        texto += "- Trabaja autónomamente\n"

    if observaciones:
        texto += f"\nObservaciones:\n{observaciones}\n"

    return texto


# -------------------------
# 📄 DESCARGAR PDF
# -------------------------
@informes_bp.route('/descargar_pdf/<int:id>')
def descargar_pdf(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM informes WHERE id = ?", (id,))
    informe = cursor.fetchone()

    conn.close()

    if not informe:
        return "Informe no encontrado"

    # 🔥 Generar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    contenido = []

    contenido.append(Paragraph("<b>INFORME PEDAGÓGICO</b>", styles["Title"]))
    contenido.append(Spacer(1, 20))

    for linea in informe["contenido"].split("\n"):
        contenido.append(Paragraph(linea, styles["Normal"]))
        contenido.append(Spacer(1, 10))

    doc.build(contenido)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"informe_{id}.pdf",
        mimetype="application/pdf"
    )