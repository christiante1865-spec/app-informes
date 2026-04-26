import sqlite3
import os

# 📁 Ruta absoluta (CLAVE para evitar errores)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

# 🔗 Conexión correcta
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 🔐 TABLA USUARIOS
c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

# 👤 TABLA ALUMNOS
c.execute("""
CREATE TABLE IF NOT EXISTS alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    edad INTEGER,
    usuario_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")

# 📄 TABLA INFORMES
c.execute("""
CREATE TABLE IF NOT EXISTS informes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER,
    contenido TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
)
""")

# 📂 TABLA ARCHIVOS
c.execute("""
CREATE TABLE IF NOT EXISTS archivos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER,
    nombre_archivo TEXT,
    ruta TEXT,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
)
""")

conn.commit()
conn.close()

print("✅ Base de datos creada correctamente en:", db_path)