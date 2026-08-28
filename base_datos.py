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

ASIGNACIONES_INICIALES = [
    # Primer semestre
    ("Análisis y Diseño de Algoritmos", "P001"),
    ("Introducción a la Ingeniería en Sistemas Digitales","P002"),
    ("Álgebra Lineal", "P003"),
    ("Geometría Analítica", "P003"),
    ("Química", "P004"),
    ("Comunicación Oral y Escrita", "P005"),
    ("Inglés I", "P006"),

    # Tercer semestre
    ("Estructuras de Datos", "P001"),
    ("Diseño de Bases de Datos", "P007"),
    ("Sistemas Digitales I", "P002"),
    ("Electricidad y Magnetismo", "P004"),
    ("Cálculo Diferencial e Integral", "P003"),
    ("Comunicación Organizacional", "P005"),
    ("Inglés III", "P006"),

    # Quinto semestre
    ("Administración de Sistemas Operativos", "P012"),
    ("Ingeniería del Software", "P007"),
    ("Circuitos Eléctricos II", "P004"),
    ("Electrónica Analógica", "P004"),
    ("Cálculo Vectorial", "P003"),
    ("Emprendimiento e Innovación", "P011"),
    ("Metodología de la Investigación", "P011"),

    # Séptimo semestre
    ("Negocios Electrónicos", "P011"),
    ("Redes de Computadoras II", "P008"),
    ("Sistemas Embebidos", "P009"),
    ("Inteligencia Artificial", "P010"),
    ("Investigación de Operaciones", "P010"),
    ("Seminario de Titulación", "P011"),
]

BLOQUES_MATUTINOS = [
    ("Lunes", "07:00", "09:00"),
    ("Lunes", "09:00", "11:00"),
    ("Martes", "07:00", "09:00"),
    ("Martes", "09:00", "11:00"),
    ("Miércoles", "07:00", "09:00"),
    ("Jueves", "07:00", "09:00"),
    ("Viernes", "07:00", "09:00"),
    ("Viernes", "09:00", "11:00"),
]

BLOQUES_VESPERTINOS = [
    ("Lunes", "13:00", "15:00"),
    ("Lunes", "15:00", "17:00"),
    ("Martes", "13:00", "15:00"),
    ("Martes", "15:00", "17:00"),
    ("Miércoles", "13:00", "15:00"),
    ("Jueves", "13:00", "15:00"),
    ("Viernes", "13:00", "15:00"),
    ("Viernes", "15:00", "17:00"),
]

BLOQUES_POR_SEMESTRE = {
    1: BLOQUES_MATUTINOS,
    3: BLOQUES_VESPERTINOS,
    5: BLOQUES_MATUTINOS,
    7: BLOQUES_VESPERTINOS,
}

CALIFICACIONES_ISAAC = [
    (10.0, 10.0, 10.0),
    (9.7, 10.0, 9.9),
    (9.9, 10.0, 10.0),
    (10.0, 10.0, 10.0),
    (10.0, 9.9, 10.0),
    (10.0, 10.0, 9.9),
]

CALIFICACIONES_GENERALES = [
    (8.4, 8.9, 9.1),
    (7.5, 8.2, 8.0),
    (9.0, 9.2, 8.8),
    (6.8, 7.5, 7.9),
    (9.5, 9.1, 9.3),
    (8.0, 7.8, 8.5),
    (7.2, 6.9, 7.6),
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

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS asignaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                materia_id INTEGER NOT NULL,
                profesor_id INTEGER NOT NULL,
                grupo TEXT NOT NULL,
                FOREIGN KEY (materia_id)
                    REFERENCES materias (id),
                FOREIGN KEY (profesor_id)
                    REFERENCES profesores (id),
                UNIQUE (materia_id, grupo)
            )
            """
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS horarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asignacion_id INTEGER NOT NULL UNIQUE,
                dia TEXT NOT NULL
                    CHECK (
                        dia IN (
                            'Lunes',
                            'Martes',
                            'Miércoles',
                            'Jueves',
                            'Viernes'
                        )
                    ),
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT NOT NULL,
                salon TEXT NOT NULL,
                FOREIGN KEY (asignacion_id)
                    REFERENCES asignaciones (id)
                    ON DELETE CASCADE,
                CHECK (hora_fin > hora_inicio),
                UNIQUE (salon, dia, hora_inicio)
            )
            """
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS inscripciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_matricula TEXT NOT NULL,
                asignacion_id INTEGER NOT NULL,
                fecha_inscripcion TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'activa'
                    CHECK (
                        estado IN (
                            'activa',
                            'baja',
                            'finalizada'
                        )
                    ),
                FOREIGN KEY (estudiante_matricula)
                    REFERENCES estudiantes (matricula)
                    ON DELETE CASCADE,
                FOREIGN KEY (asignacion_id)
                    REFERENCES asignaciones (id)
                    ON DELETE CASCADE,
                UNIQUE (
                    estudiante_matricula,
                    asignacion_id
                )
            )
            """
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS calificaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inscripcion_id INTEGER NOT NULL UNIQUE,
                parcial_1 REAL NOT NULL
                    CHECK (
                        parcial_1 BETWEEN 0 AND 10
                    ),
                parcial_2 REAL NOT NULL
                    CHECK (
                        parcial_2 BETWEEN 0 AND 10
                    ),
                parcial_3 REAL NOT NULL
                    CHECK (
                        parcial_3 BETWEEN 0 AND 10
                    ),
                promedio REAL NOT NULL
                    CHECK (
                        promedio BETWEEN 0 AND 10
                    ),
                FOREIGN KEY (inscripcion_id)
                    REFERENCES inscripciones (id)
                    ON DELETE CASCADE
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

        for nombre_materia, numero_empleado in (
            ASIGNACIONES_INICIALES
        ):
            materia = conexion.execute(
                """
                SELECT
                    id,
                    semestre
                FROM materias
                WHERE nombre = ?
                """,
                (nombre_materia,),
            ).fetchone()

            profesor = conexion.execute(
                """
                SELECT id
                FROM profesores
                WHERE numero_empleado = ?
                """,
                (numero_empleado,),
            ).fetchone()

            if materia is None:
                raise ValueError(
                    f"No existe la materia: {nombre_materia}"
                )

            if profesor is None:
                raise ValueError(
                    f"No existe el profesor: {numero_empleado}"
                )

            materia_id = materia[0]
            semestre = materia[1]
            profesor_id = profesor[0]
            grupo = f"{semestre}A"

            conexion.execute(
                """
                INSERT INTO asignaciones (
                    materia_id,
                    profesor_id,
                    grupo
                )
                VALUES (?, ?, ?)
                ON CONFLICT (materia_id, grupo)
                DO UPDATE SET
                    profesor_id = excluded.profesor_id
                """,
                (
                    materia_id,
                    profesor_id,
                    grupo,
                ),
            )

        asignaciones = conexion.execute(
            """
            SELECT
                a.id,
                a.profesor_id,
                a.grupo,
                m.semestre,
                m.orden
            FROM asignaciones AS a
            INNER JOIN materias AS m
                ON m.id = a.materia_id
            ORDER BY
                m.semestre,
                m.orden
            """
        ).fetchall()

        for asignacion in asignaciones:
            asignacion_id = asignacion[0]
            profesor_id = asignacion[1]
            grupo = asignacion[2]
            semestre = asignacion[3]
            orden = asignacion[4]

            bloques = BLOQUES_POR_SEMESTRE.get(semestre)

            if bloques is None:
                continue

            if orden > len(bloques):
                raise ValueError(
                    f"No existe un bloque para el orden {orden}"
                )

            dia, hora_inicio, hora_fin = bloques[orden - 1]
            salon = f"A-{semestre}{orden:02d}"

            conflicto_grupo = conexion.execute(
                """
                SELECT h.id
                FROM horarios AS h
                INNER JOIN asignaciones AS a
                    ON a.id = h.asignacion_id
                WHERE a.grupo = ?
                    AND h.dia = ?
                    AND h.asignacion_id != ?
                    AND h.hora_inicio < ?
                    AND h.hora_fin > ?
                """,
                (
                    grupo,
                    dia,
                    asignacion_id,
                    hora_fin,
                    hora_inicio,
                ),
            ).fetchone()

            if conflicto_grupo is not None:
                raise ValueError(
                    f"Choque de horario para el grupo {grupo}"
                )

            conflicto_profesor = conexion.execute(
                """
                SELECT h.id
                FROM horarios AS h
                INNER JOIN asignaciones AS a
                    ON a.id = h.asignacion_id
                WHERE a.profesor_id = ?
                    AND h.dia = ?
                    AND h.asignacion_id != ?
                    AND h.hora_inicio < ?
                    AND h.hora_fin > ?
                """,
                (
                    profesor_id,
                    dia,
                    asignacion_id,
                    hora_fin,
                    hora_inicio,
                ),
            ).fetchone()

            if conflicto_profesor is not None:
                raise ValueError(
                    "Un profesor tiene dos clases "
                    "en el mismo horario."
                )

            conexion.execute(
                """
                INSERT INTO horarios (
                    asignacion_id,
                    dia,
                    hora_inicio,
                    hora_fin,
                    salon
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (asignacion_id)
                DO UPDATE SET
                    dia = excluded.dia,
                    hora_inicio = excluded.hora_inicio,
                    hora_fin = excluded.hora_fin,
                    salon = excluded.salon
                """,
                (
                    asignacion_id,
                    dia,
                    hora_inicio,
                    hora_fin,
                    salon,
                ),
            )

        conexion.execute(
            """
            INSERT OR IGNORE INTO inscripciones (
                estudiante_matricula,
                asignacion_id,
                fecha_inscripcion,
                estado
            )
            SELECT
                e.matricula,
                a.id,
                '2026-08-01',
                'activa'
            FROM estudiantes AS e
            INNER JOIN asignaciones AS a
                ON a.grupo = e.grupo
            """
        )

        inscripciones = conexion.execute(
            """
            SELECT
                i.id,
                i.estudiante_matricula,
                m.orden
            FROM inscripciones AS i
            INNER JOIN asignaciones AS a
                ON a.id = i.asignacion_id
            INNER JOIN materias AS m
                ON m.id = a.materia_id
            ORDER BY
                i.estudiante_matricula,
                m.orden
            """
        ).fetchall()

        for inscripcion in inscripciones:
            inscripcion_id = inscripcion[0]
            matricula = inscripcion[1]
            orden = inscripcion[2]

            if matricula == "2026001":
                indice = (
                    orden - 1
                ) % len(CALIFICACIONES_ISAAC)

                parciales = CALIFICACIONES_ISAAC[indice]
            else:
                ultimo_digito = int(matricula[-1])

                indice = (
                    ultimo_digito + orden - 2
                ) % len(CALIFICACIONES_GENERALES)

                parciales = CALIFICACIONES_GENERALES[
                    indice
                ]

            parcial_1 = parciales[0]
            parcial_2 = parciales[1]
            parcial_3 = parciales[2]

            promedio = round(
                (
                    parcial_1
                    + parcial_2
                    + parcial_3
                ) / 3,
                2,
            )

            if (
                matricula == "2026001"
                and promedio <= 9.6
            ):
                raise ValueError(
                    "Isaac debe tener promedios "
                    "mayores a 9.6."
                )

            conexion.execute(
                """
                INSERT INTO calificaciones (
                    inscripcion_id,
                    parcial_1,
                    parcial_2,
                    parcial_3,
                    promedio
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (inscripcion_id)
                DO UPDATE SET
                    parcial_1 = excluded.parcial_1,
                    parcial_2 = excluded.parcial_2,
                    parcial_3 = excluded.parcial_3,
                    promedio = excluded.promedio
                """,
                (
                    inscripcion_id,
                    parcial_1,
                    parcial_2,
                    parcial_3,
                    promedio,
                ),
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

def obtener_asignaciones_por_semestre(semestre):
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        asignaciones = conexion.execute(
            """
            SELECT
                a.id,
                m.nombre AS materia,
                m.semestre,
                m.orden,
                a.grupo,
                p.numero_empleado,
                p.nombre AS profesor,
                p.correo,
                p.especialidad
            FROM asignaciones AS a
            INNER JOIN materias AS m
                ON m.id = a.materia_id
            INNER JOIN profesores AS p
                ON p.id = a.profesor_id
            WHERE m.semestre = ?
            ORDER BY m.orden
            """,
            (semestre,),
        ).fetchall()

    return [
        dict(asignacion)
        for asignacion in asignaciones
    ]

def contar_asignaciones():
    with closing(conectar()) as conexion:
        resultado = conexion.execute(
            """
            SELECT COUNT(*)
            FROM asignaciones
            """
        ).fetchone()

    return resultado[0]

def obtener_horario_por_estudiante(matricula):
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        horario = conexion.execute(
            """
            SELECT
                h.dia,
                h.hora_inicio,
                h.hora_fin,
                h.salon,
                m.nombre AS materia,
                p.nombre AS profesor,
                a.grupo
            FROM estudiantes AS e
            INNER JOIN asignaciones AS a
                ON a.grupo = e.grupo
            INNER JOIN materias AS m
                ON m.id = a.materia_id
            INNER JOIN profesores AS p
                ON p.id = a.profesor_id
            INNER JOIN horarios AS h
                ON h.asignacion_id = a.id
            WHERE e.matricula = ?
            ORDER BY
                CASE h.dia
                    WHEN 'Lunes' THEN 1
                    WHEN 'Martes' THEN 2
                    WHEN 'Miércoles' THEN 3
                    WHEN 'Jueves' THEN 4
                    WHEN 'Viernes' THEN 5
                END,
                h.hora_inicio
            """,
            (matricula,),
        ).fetchall()

    return [
        dict(clase)
        for clase in horario
    ]


def contar_horarios():
    with closing(conectar()) as conexion:
        resultado = conexion.execute(
            """
            SELECT COUNT(*)
            FROM horarios
            """
        ).fetchone()

    return resultado[0]

def obtener_inscripciones_por_estudiante(matricula):
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        inscripciones = conexion.execute(
            """
            SELECT
                i.id,
                i.fecha_inscripcion,
                i.estado,
                m.nombre AS materia,
                m.semestre,
                m.orden,
                p.nombre AS profesor,
                a.grupo
            FROM inscripciones AS i
            INNER JOIN asignaciones AS a
                ON a.id = i.asignacion_id
            INNER JOIN materias AS m
                ON m.id = a.materia_id
            INNER JOIN profesores AS p
                ON p.id = a.profesor_id
            WHERE i.estudiante_matricula = ?
            ORDER BY m.orden
            """,
            (matricula,),
        ).fetchall()

    return [
        dict(inscripcion)
        for inscripcion in inscripciones
    ]

def obtener_resumen_inscripciones():
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        resumen = conexion.execute(
            """
            SELECT
                e.matricula,
                e.nombre,
                e.grupo,
                COUNT(i.id) AS total_inscripciones
            FROM estudiantes AS e
            LEFT JOIN inscripciones AS i
                ON i.estudiante_matricula = e.matricula
            GROUP BY
                e.matricula,
                e.nombre,
                e.grupo
            ORDER BY e.matricula
            """
        ).fetchall()

    return [
        dict(estudiante)
        for estudiante in resumen
    ]


def contar_inscripciones():
    with closing(conectar()) as conexion:
        resultado = conexion.execute(
            """
            SELECT COUNT(*)
            FROM inscripciones
            """
        ).fetchone()

    return resultado[0]

def obtener_calificaciones_por_estudiante(matricula):
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        calificaciones = conexion.execute(
            """
            SELECT
                m.nombre AS materia,
                m.orden,
                c.parcial_1,
                c.parcial_2,
                c.parcial_3,
                c.promedio
            FROM calificaciones AS c
            INNER JOIN inscripciones AS i
                ON i.id = c.inscripcion_id
            INNER JOIN asignaciones AS a
                ON a.id = i.asignacion_id
            INNER JOIN materias AS m
                ON m.id = a.materia_id
            WHERE i.estudiante_matricula = ?
            ORDER BY m.orden
            """,
            (matricula,),
        ).fetchall()

    return [
        dict(calificacion)
        for calificacion in calificaciones
    ]


def contar_calificaciones():
    with closing(conectar()) as conexion:
        resultado = conexion.execute(
            """
            SELECT COUNT(*)
            FROM calificaciones
            """
        ).fetchone()

    return resultado[0]

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

        asignaciones = (
            obtener_asignaciones_por_semestre(semestre)
        )

        print(
            f"\nAsignaciones de {semestre}.º semestre:"
        )

        for asignacion in asignaciones:
            print(
                f"{asignacion['orden']}. "
                f"{asignacion['materia']} - "
                f"{asignacion['profesor']} - "
                f"Grupo {asignacion['grupo']}"
            )

        print(
            f"\nTotal de asignaciones registradas: "
            f"{contar_asignaciones()}"
        )

        horario = obtener_horario_por_estudiante(
            matricula_ingresada
        )

        print(
            f"\nHorario de "
            f"{estudiante_encontrado['nombre']}:"
        )

        for clase in horario:
            print(
                f"{clase['dia']} "
                f"{clase['hora_inicio']} - "
                f"{clase['hora_fin']} | "
                f"{clase['materia']} | "
                f"{clase['profesor']} | "
                f"Salón {clase['salon']}"
            )

        print(
            f"\nTotal de horarios registrados: "
            f"{contar_horarios()}"
        )

        inscripciones = (
            obtener_inscripciones_por_estudiante(
                matricula_ingresada
            )
        )

        print(
            f"\nInscripciones de "
            f"{estudiante_encontrado['nombre']}: "
            f"{len(inscripciones)}"
        )

        for inscripcion in inscripciones:
            print(
                f"- {inscripcion['materia']} | "
                f"{inscripcion['estado']} | "
                f"{inscripcion['fecha_inscripcion']}"
            )

        print("\nResumen de inscripciones:")

        for estudiante in obtener_resumen_inscripciones():
            print(
                f"{estudiante['matricula']} - "
                f"{estudiante['nombre']} - "
                f"{estudiante['grupo']}: "
                f"{estudiante['total_inscripciones']}"
            )

        print(
            f"\nTotal de inscripciones registradas: "
            f"{contar_inscripciones()}"
        )

        calificaciones = (
            obtener_calificaciones_por_estudiante(
                matricula_ingresada
            )
        )

        print(
            f"\nCalificaciones de "
            f"{estudiante_encontrado['nombre']}:"
        )

        for calificacion in calificaciones:
            print(
                f"- {calificacion['materia']} | "
                f"P1: {calificacion['parcial_1']:.1f} | "
                f"P2: {calificacion['parcial_2']:.1f} | "
                f"P3: {calificacion['parcial_3']:.1f} | "
                f"Promedio: "
                f"{calificacion['promedio']:.2f}"
            )

        if calificaciones:
            promedio_general = round(
                sum(
                    calificacion["promedio"]
                    for calificacion in calificaciones
                ) / len(calificaciones),
                2,
            )

            print(
                f"Promedio general: "
                f"{promedio_general:.2f}"
            )

        print(
            f"\nTotal de calificaciones registradas: "
            f"{contar_calificaciones()}"
        )