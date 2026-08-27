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

MATERIAS_POR_SEMESTRE = {
    1: [
        "Análisis y Diseño de Algoritmos",
        "Introducción a la Ingeniería en Sistemas Digitales",
        "Álgebra Lineal",
        "Geometría Analítica",
        "Química",
        "Comunicación Oral y Escrita",
        "Inglés I",
    ],
    2: [
        "Programación Orientada a Objetos",
        "Arquitectura de Computadoras",
        "Diseño Asistido por Computadora",
        "Matemáticas Discretas",
        "Física",
        "Ética Profesional",
        "Estrategias de Aprendizaje",
        "Inglés II",
    ],
    3: [
        "Estructuras de Datos",
        "Diseño de Bases de Datos",
        "Sistemas Digitales I",
        "Electricidad y Magnetismo",
        "Cálculo Diferencial e Integral",
        "Comunicación Organizacional",
        "Inglés III",
    ],
    4: [
        "Desarrollo de Aplicaciones con Base de Datos",
        "Sistemas Digitales II",
        "Circuitos Eléctricos I",
        "Ecuaciones Diferenciales Ordinarias",
        "Probabilidad y Estadística",
        "Derecho Informático",
        "Responsabilidad Social",
        "Inglés IV",
    ],
    5: [
        "Administración de Sistemas Operativos",
        "Ingeniería del Software",
        "Circuitos Eléctricos II",
        "Electrónica Analógica",
        "Cálculo Vectorial",
        "Emprendimiento e Innovación",
        "Metodología de la Investigación",
    ],
    6: [
        "Programación Web",
        "Redes de Computadoras I",
        "Electrónica Digital",
        "Microprocesadores y Microcontroladores",
        "Métodos Numéricos",
        "Diseño de Empresas",
        "Habilidades Directivas",
    ],
    7: [
        "Negocios Electrónicos",
        "Redes de Computadoras II",
        "Sistemas Embebidos",
        "Inteligencia Artificial",
        "Investigación de Operaciones",
        "Seminario de Titulación",
    ],
    8: [
        "Cómputo en la Nube",
        "Bases de Datos Multidimensionales",
        "Dispositivos Lógicos Programables",
        "Electrónica de Potencia",
        "Desarrollo Sustentable",
    ],
}

PROFESORES_INICIALES = [
    (
        "P001",
        "Mariana López Vargas",
        "mariana.lopez@eduia.edu.mx",
        "Programación",
    ),
    (
        "P002",
        "Roberto Hernández Silva",
        "roberto.hernandez@eduia.edu.mx",
        "Sistemas Digitales",
    ),
    (
        "P003",
        "Claudia Ramírez Soto",
        "claudia.ramirez@eduia.edu.mx",
        "Matemáticas",
    ),
    (
        "P004",
        "Fernando Torres Méndez",
        "fernando.torres@eduia.edu.mx",
        "Electrónica",
    ),
    (
        "P005",
        "Patricia Gómez Lara",
        "patricia.gomez@eduia.edu.mx",
        "Comunicación y Humanidades",
    ),
    (
        "P006",
        "Alejandro Ruiz Ortega",
        "alejandro.ruiz@eduia.edu.mx",
        "Idiomas",
    ),
    (
        "P007",
        "Verónica Castillo Núñez",
        "veronica.castillo@eduia.edu.mx",
        "Bases de Datos e Ingeniería de Software",
    ),
    (
        "P008",
        "Miguel Ángel Navarro Cruz",
        "miguel.navarro@eduia.edu.mx",
        "Redes de Computadoras",
    ),
    (
        "P009",
        "Gabriela Mendoza Reyes",
        "gabriela.mendoza@eduia.edu.mx",
        "Sistemas Embebidos",
    ),
    (
        "P010",
        "Ricardo Salazar Campos",
        "ricardo.salazar@eduia.edu.mx",
        "Inteligencia Artificial",
    ),
    (
        "P011",
        "Daniela Pérez Fuentes",
        "daniela.perez@eduia.edu.mx",
        "Administración e Investigación",
    ),
    (
        "P012",
        "Jorge Alberto Vega Morales",
        "jorge.vega@eduia.edu.mx",
        "Infraestructura y Cómputo",
    ),
]

def conectar():
    CARPETA_DATOS.mkdir(exist_ok=True)

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion

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

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS materias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                semestre INTEGER NOT NULL
                    CHECK (semestre BETWEEN 1 AND 8),
                orden INTEGER NOT NULL
                    CHECK (orden > 0),
                UNIQUE (semestre, nombre),
                UNIQUE (semestre, orden)
            )
            """
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS profesores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_empleado TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                especialidad TEXT NOT NULL
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

        materias_iniciales = [
            (nombre, semestre, orden)
            for semestre, materias in MATERIAS_POR_SEMESTRE.items()
            for orden, nombre in enumerate(materias, start=1)
        ]

        conexion.executemany(
            """
            INSERT OR IGNORE INTO materias (
                nombre,
                semestre,
                orden
            )
            VALUES (?, ?, ?)
            """,
            materias_iniciales,
        )

        conexion.executemany(
            """
            INSERT OR IGNORE INTO profesores (
                numero_empleado,
                nombre,
                correo,
                especialidad
            )
            VALUES (?, ?, ?, ?)
            """,
            PROFESORES_INICIALES,
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

def obtener_materias_por_semestre(semestre):
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        materias = conexion.execute(
            """
            SELECT
                id,
                nombre,
                semestre,
                orden
            FROM materias
            WHERE semestre = ?
            ORDER BY orden
            """,
            (semestre,),
        ).fetchall()

    return [dict(materia) for materia in materias]


def contar_materias():
    with closing(conectar()) as conexion:
        resultado = conexion.execute(
            """
            SELECT COUNT(*)
            FROM materias
            """
        ).fetchone()

    return resultado[0]

def obtener_profesores():
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        profesores = conexion.execute(
            """
            SELECT
                id,
                numero_empleado,
                nombre,
                correo,
                especialidad
            FROM profesores
            ORDER BY numero_empleado
            """
        ).fetchall()

    return [dict(profesor) for profesor in profesores]

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

        semestre = estudiante_encontrado["semestre"]
        materias = obtener_materias_por_semestre(semestre)

        print(f"\nMaterias de {semestre}.º semestre:")

        for materia in materias:
            print(
                f"{materia['orden']}. {materia['nombre']}"
            )

        print(
            f"\nTotal de materias registradas: "
            f"{contar_materias()}"
        )

        profesores = obtener_profesores()

        print(
            f"\nProfesores registrados: "
            f"{len(profesores)}"
        )

        for profesor in profesores:
            print(
                f"{profesor['numero_empleado']} - "
                f"{profesor['nombre']} - "
                f"{profesor['especialidad']}"
            )