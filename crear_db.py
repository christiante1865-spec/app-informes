import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# 🔐 TABLA USUARIOS
c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

# 👤 TABLA ALUMNOS (CORREGIDO)
c.execute("""
CREATE TABLE IF NOT EXISTS alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    edad INTEGER,
    usuario_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")

# 📄 TABLA INFORMES (CORREGIDO)
c.execute("""
CREATE TABLE IF NOT EXISTS informes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER,
    contenido TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
)
""")

# 📂 TABLA ARCHIVOS (OPCIONAL FUTURO)
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

print("Base de datos corregida y lista ✅")