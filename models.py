import sqlite3

def get_connection():
    return sqlite3.connect("database.db")


def crear_tablas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        edad INTEGER,
        curso TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS informes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER,
        contenido TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(alumno_id) REFERENCES alumnos(id)
    )
    ''')

    conn.commit()
    conn.close()