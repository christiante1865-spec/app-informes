from flask import Blueprint, request, redirect, send_from_directory
import os
from werkzeug.utils import secure_filename

archivos_bp = Blueprint('archivos', __name__)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 🔥 SUBIR ARCHIVO (USANDO id)
@archivos_bp.route("/subir_archivo/<int:id>", methods=["POST"])
def subir_archivo(id):

    if "archivo" not in request.files:
        return "No se envió archivo"

    file = request.files["archivo"]

    if file.filename == "":
        return "Archivo vacío"

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)

        carpeta = os.path.join("uploads", f"alumno_{id}")
        os.makedirs(carpeta, exist_ok=True)

        ruta = os.path.join(carpeta, filename)
        file.save(ruta)

    return redirect(f"/perfil_alumno/{id}")


# 🔥 VER ARCHIVO (ESTO SOLUCIONA EL ERROR 404)
@archivos_bp.route("/uploads/alumno_<int:id>/<filename>")
def uploaded_file(id, filename):
    carpeta = os.path.join("uploads", f"alumno_{id}")
    return send_from_directory(carpeta, filename)


# 🔥 ELIMINAR ARCHIVO (OPCIONAL PERO RECOMENDADO)
@archivos_bp.route("/eliminar_archivo/<int:id>/<nombre>")
def eliminar_archivo(id, nombre):
    carpeta = os.path.join("uploads", f"alumno_{id}")
    ruta = os.path.join(carpeta, nombre)

    if os.path.exists(ruta):
        os.remove(ruta)

    return redirect(f"/perfil_alumno/{id}")