import sqlite3

from contextlib import closing
from pathlib import Path


CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_DATOS = CARPETA_PROYECTO / "data"
RUTA_BASE_DATOS = CARPETA_DATOS / "eduia.db"


ESTUDIANTES_INICIALES = [
    (
        "2026001",
        "Isaac Andrade Quiroz",
        "Ingeniería en Sistemas Digitales",
        7,
        "7A",
    ),
    (
        "2026002",
        "Ana Laura Hernández Hernández",
        "Ingeniería en Sistemas Digitales",
        5,
        "5A",
    ),
    (
        "2026003",
        "Kevin Guadalupe Caudillo Cárdenas",
        "Ingeniería en Sistemas Digitales",
        7,
        "7A",
    ),
    (
        "2026004",
        "Carlo Giovanni Gutiérrez Rivera",
        "Ingeniería en Sistemas Digitales",
        3,
        "3A",
    ),
    (
        "2026005",
        "Lucia Sanchez Sanchez",
        "Ingeniería en Sistemas Digitales",
        1,
        "1A",
    ),
    (
        "2026006",
        "Lourdes Estefanía Oliva Díaz",
        "Ingeniería en Sistemas Digitales",
        5,
        "5A",
    ),
]


def conectar():
    CARPETA_DATOS.mkdir(exist_ok=True)

    return sqlite3.connect(RUTA_BASE_DATOS)


def crear_base_datos():
    with closing(conectar()) as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS estudiantes (
                matricula TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                carrera TEXT NOT NULL,
                semestre INTEGER NOT NULL
                    CHECK (semestre BETWEEN 1 AND 8),
                grupo TEXT NOT NULL
            )
            """
        )

        conexion.executemany(
            """
            INSERT OR IGNORE INTO estudiantes (
                matricula,
                nombre,
                carrera,
                semestre,
                grupo
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            ESTUDIANTES_INICIALES,
        )

        conexion.commit()


def buscar_estudiante(matricula):
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        estudiante = conexion.execute(
            """
            SELECT
                matricula,
                nombre,
                carrera,
                semestre,
                grupo
            FROM estudiantes
            WHERE matricula = ?
            """,
            (matricula,),
        ).fetchone()

    if estudiante is None:
        return None

    return dict(estudiante)


if __name__ == "__main__":
    crear_base_datos()

    print("Base de datos creada correctamente.")
    print(f"Ubicación: {RUTA_BASE_DATOS}")

    matricula_ingresada = input("Escribe una matrícula: ").strip()
    estudiante_encontrado = buscar_estudiante(matricula_ingresada)

    if estudiante_encontrado is None:
        print("No se encontró un estudiante con esa matrícula.")
    else:
        print("Estudiante encontrado:")
        print(f"Nombre: {estudiante_encontrado['nombre']}")
        print(f"Carrera: {estudiante_encontrado['carrera']}")
        print(f"Semestre: {estudiante_encontrado['semestre']}")
        print(f"Grupo: {estudiante_encontrado['grupo']}")