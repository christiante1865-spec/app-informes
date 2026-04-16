from flask import Blueprint, request, redirect
import os
from werkzeug.utils import secure_filename

archivos_bp = Blueprint('archivos', __name__)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@archivos_bp.route("/subir_archivo/<int:alumno_id>", methods=["POST"])
def subir_archivo(alumno_id):

    if "archivo" not in request.files:
        return "No se envió archivo"

    file = request.files["archivo"]

    if file.filename == "":
        return "Archivo vacío"

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)

        carpeta = os.path.join("uploads", f"alumno_{alumno_id}")
        os.makedirs(carpeta, exist_ok=True)

        ruta = os.path.join(carpeta, filename)
        file.save(ruta)

    return redirect(f"/perfil_alumno/{alumno_id}")