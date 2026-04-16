from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3

informes_bp = Blueprint('informes', __name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# 🔥 CREAR INFORME
@informes_bp.route('/crear_informe/<int:alumno_id>', methods=["GET", "POST"])
def crear_informe(alumno_id):
    conn = get_db()
    cursor = conn.cursor()

    # 🔍 Obtener alumno
    cursor.execute("SELECT * FROM alumnos WHERE id = ?", (alumno_id,))
    alumno = cursor.fetchone()

    if not alumno:
        conn.close()
        return "Alumno no encontrado"

    # 🔥 POST (guardar informe)
    if request.method == "POST":

        conducta = request.form.get("conducta")
        rendimiento = request.form.get("rendimiento")
        observaciones = request.form.get("observaciones")

        # ✅ Validación
        if not conducta or not rendimiento:
            flash("Debes completar todos los campos obligatorios ❌")
            conn.close()
            return redirect(request.url)

        # 🔥 Generar informe
        informe = generar_informe(
            alumno["nombre"],
            alumno["edad"],
            conducta,
            rendimiento,
            observaciones
        )

        cursor.execute(
            "INSERT INTO informes (alumno_id, contenido) VALUES (?, ?)",
            (alumno_id, informe)
        )

        conn.commit()
        conn.close()

        flash("Informe generado correctamente ✅")

        return redirect(url_for("alumnos.perfil_alumno", id=alumno_id))

    conn.close()
    return render_template("crear_informe.html", alumno=alumno)


# 🔥 GENERADOR DE INFORME
def generar_informe(nombre, edad, conducta, rendimiento, observaciones):

    texto = "INFORME PSICOEMOCIONAL\n"
    texto += "----------------------------------------\n\n"

    texto += f"Nombre del alumno: {nombre}\n"
    texto += f"Edad: {edad} años\n\n"

    # 🔥 Área Conductual
    texto += "Área Conductual:\n"
    if conducta == "impulsivo":
        texto += "El alumno presenta conductas impulsivas, lo que puede afectar su interacción y el cumplimiento de normas.\n\n"
    elif conducta == "normal":
        texto += "El alumno presenta una conducta adecuada, favoreciendo la convivencia.\n\n"

    # 🔥 Área Académica
    texto += "Área Académica:\n"
    if rendimiento == "bajo":
        texto += "Se observan dificultades en el rendimiento académico, requiriendo apoyo adicional.\n\n"
    elif rendimiento == "medio":
        texto += "El rendimiento académico se encuentra dentro de lo esperado.\n\n"
    elif rendimiento == "alto":
        texto += "El alumno destaca por un rendimiento superior al promedio.\n\n"

    # 🔥 Área Socioemocional
    if observaciones:
        texto += "Área Socioemocional:\n"
        texto += f"{observaciones}\n\n"

    # 🔥 Recomendaciones
    texto += "Recomendaciones:\n"

    if conducta == "impulsivo":
        texto += "- Trabajar estrategias de autorregulación emocional.\n"

    if rendimiento == "bajo":
        texto += "- Reforzamiento pedagógico focalizado.\n"

    texto += "- Seguimiento continuo.\n"
    texto += "- Comunicación con la familia.\n"

    texto += "\n----------------------------------------\n"
    texto += "Informe generado automáticamente por el sistema."

    return texto