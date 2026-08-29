import sqlite3

from contextlib import closing
from datetime import date, datetime, timedelta
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
        "7° ISD",
    ),
    (
        "2026002",
        "Ana Laura Hernández Hernández",
        "Ingeniería en Sistemas Digitales",
        5,
        "5° ISD",
    ),
    (
        "2026003",
        "Kevin Guadalupe Caudillo Cárdenas",
        "Ingeniería en Sistemas Digitales",
        7,
        "7° ISD",
    ),
    (
        "2026004",
        "Carlo Giovanni Gutiérrez Rivera",
        "Ingeniería en Sistemas Digitales",
        3,
        "3° ISD",
    ),
    (
        "2026005",
        "Lucia Sanchez Sanchez",
        "Ingeniería en Sistemas Digitales",
        1,
        "1° ISD",
    ),
    (
        "2026006",
        "Lourdes Estefanía Oliva Díaz",
        "Ingeniería en Sistemas Digitales",
        5,
        "5° ISD",
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

FECHAS_BASE_EXAMENES = {
    1: date(2026, 9, 14),
    2: date(2026, 10, 19),
    3: date(2026, 11, 23),
}

DESPLAZAMIENTOS_EXAMEN = [
    0,
    1,
    2,
    3,
    4,
    7,
    8,
    9,
]

AVISOS_INICIALES = [
    (
        "A001",
        "Registro a talleres extracurriculares",
        (
            "Ya está disponible el registro para "
            "los talleres académicos y culturales."
        ),
        "2026-08-25",
        "2026-09-05",
        None,
    ),
    (
        "A002",
        "Mantenimiento de la plataforma escolar",
        (
            "La plataforma escolar estará en "
            "mantenimiento durante la mañana."
        ),
        "2026-08-27",
        "2026-09-12",
        None,
    ),
    (
        "A003",
        "Acompañamiento para primer semestre",
        (
            "Se realizará una sesión de orientación "
            "para estudiantes de nuevo ingreso."
        ),
        "2026-08-26",
        "2026-09-04",
        1,
    ),
    (
        "A004",
        "Práctica integradora de Sistemas Digitales I",
        (
            "El grupo de tercer semestre realizará "
            "una práctica integradora en laboratorio."
        ),
        "2026-08-26",
        "2026-09-18",
        3,
    ),
    (
        "A005",
        "Feria de emprendimiento e innovación",
        (
            "Los estudiantes de quinto semestre "
            "presentarán sus propuestas de negocio."
        ),
        "2026-08-26",
        "2026-09-24",
        5,
    ),
    (
        "A006",
        "Avance de Seminario de Titulación",
        (
            "El grupo de séptimo semestre deberá "
            "presentar su primer avance de proyecto."
        ),
        "2026-08-26",
        "2026-09-21",
        7,
    ),
]

CONTENIDOS_ACADEMICOS = [
    (
        "C001",
        "Pseudocódigo",
        "Análisis y Diseño de Algoritmos",
        (
            "pseudocódigo, algoritmo, variables, "
            "condicional, ciclo, diagrama de flujo"
        ),
        (
            "El pseudocódigo describe un algoritmo "
            "mediante instrucciones ordenadas y fáciles "
            "de comprender, sin depender de la sintaxis "
            "de un lenguaje de programación."
        ),
        (
            "Para sumar dos números: leer A y B, "
            "calcular SUMA = A + B y mostrar SUMA."
        ),
        (
            "Diseña un pseudocódigo que lea tres "
            "calificaciones, calcule el promedio e "
            "indique si el estudiante aprobó."
        ),
        1,
    ),
    (
        "C002",
        "Modelo relacional",
        "Diseño de Bases de Datos",
        (
            "modelo relacional, tabla, atributo, "
            "registro, llave primaria, llave foránea"
        ),
        (
            "El modelo relacional organiza la información "
            "en tablas. Cada fila representa un registro, "
            "cada columna representa un atributo y las "
            "llaves permiten relacionar tablas."
        ),
        (
            "La tabla estudiantes utiliza matrícula como "
            "llave primaria. La tabla inscripciones utiliza "
            "esa matrícula como llave foránea."
        ),
        (
            "Diseña las tablas necesarias para relacionar "
            "clientes, pedidos y productos, indicando sus "
            "llaves primarias y foráneas."
        ),
        3,
    ),
    (
        "C003",
        "Planificación Round Robin",
        "Administración de Sistemas Operativos",
        (
            "round robin, planificación, procesos, "
            "quantum, cola, cpu"
        ),
        (
            "Round Robin asigna a cada proceso un intervalo "
            "llamado quantum. Cuando el tiempo termina, el "
            "proceso vuelve al final de la cola si todavía "
            "no ha finalizado."
        ),
        (
            "Con quantum 2, los procesos P1=5 y P2=3 "
            "se ejecutan: P1(2), P2(2), P1(2), "
            "P2(1) y P1(1)."
        ),
        (
            "Simula Round Robin con quantum 3 para los "
            "procesos P1=7, P2=4 y P3=5."
        ),
        5,
    ),
    (
        "C004",
        "Ciclo de vida del software",
        "Ingeniería del Software",
        (
            "ciclo de vida, requisitos, análisis, diseño, "
            "desarrollo, pruebas, mantenimiento"
        ),
        (
            "El ciclo de vida del software organiza un "
            "proyecto en etapas: requisitos, análisis, "
            "diseño, desarrollo, pruebas, implementación "
            "y mantenimiento."
        ),
        (
            "En EduIA primero se definieron las consultas, "
            "después se diseñó la base de datos, se programó "
            "la lógica y finalmente se realizaron pruebas."
        ),
        (
            "Describe las etapas que seguirías para crear "
            "un sistema de control escolar."
        ),
        5,
    ),
    (
        "C005",
        "TF-IDF y similitud del coseno",
        "Inteligencia Artificial",
        (
            "tf-idf, similitud del coseno, vectorizador, "
            "texto, palabras, clasificación"
        ),
        (
            "TF-IDF convierte documentos en vectores "
            "numéricos y asigna mayor importancia a las "
            "palabras representativas. La similitud del "
            "coseno compara la dirección de esos vectores."
        ),
        (
            "EduIA transforma una pregunta del estudiante "
            "y la compara con ejemplos conocidos. La "
            "categoría con mayor similitud se selecciona "
            "si supera el nivel de confianza."
        ),
        (
            "Escribe tres formas diferentes de preguntar "
            "por un horario y explica qué palabras serían "
            "más importantes para clasificarlas."
        ),
        7,
    ),
    (
        "C006",
        "RTOS",
        "Sistemas Embebidos",
        (
            "rtos, tiempo real, tarea, prioridad, "
            "interrupción, semáforo, scheduler"
        ),
        (
            "Un RTOS es un sistema operativo diseñado para "
            "ejecutar tareas con tiempos de respuesta "
            "predecibles. Utiliza prioridades, planificación "
            "y mecanismos de comunicación entre tareas."
        ),
        (
            "Una tarea lee un sensor cada 100 ms, otra "
            "actualiza una pantalla y una interrupción "
            "atiende una alarma de alta prioridad."
        ),
        (
            "Propón tres tareas para un sistema de control "
            "de temperatura e indica su prioridad."
        ),
        7,
    ),
    (
        "C007",
        "Método de Newton-Raphson",
        "Métodos Numéricos",
        (
            "newton-raphson, método numérico, raíz, "
            "función, derivada, iteración"
        ),
        (
            "Newton-Raphson aproxima una raíz utilizando "
            "la fórmula x siguiente = x actual menos "
            "f(x actual) dividida entre su derivada. "
            "El proceso se repite hasta reducir el error."
        ),
        (
            "Para f(x)=x²-2 y x inicial=1.5, se sustituye "
            "en la fórmula para aproximar la raíz de 2."
        ),
        (
            "Realiza dos iteraciones de Newton-Raphson "
            "para f(x)=x²-4, usando x inicial=3."
        ),
        6,
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

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS examenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asignacion_id INTEGER NOT NULL,
                parcial INTEGER NOT NULL
                    CHECK (parcial BETWEEN 1 AND 3),
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                salon TEXT NOT NULL,
                FOREIGN KEY (asignacion_id)
                    REFERENCES asignaciones (id)
                    ON DELETE CASCADE,
                UNIQUE (
                    asignacion_id,
                    parcial
                )
            )
            """
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS avisos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                titulo TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                fecha_publicacion TEXT NOT NULL,
                fecha_evento TEXT NOT NULL,
                semestre INTEGER,
                activo INTEGER NOT NULL DEFAULT 1
                    CHECK (activo IN (0, 1)),
                CHECK (
                    semestre IS NULL
                    OR semestre BETWEEN 1 AND 8
                )
            )
            """
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS contenido_academico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                tema TEXT NOT NULL UNIQUE,
                materia TEXT NOT NULL,
                palabras_clave TEXT NOT NULL,
                explicacion TEXT NOT NULL,
                ejemplo TEXT NOT NULL,
                ejercicio TEXT NOT NULL,
                semestre_recomendado INTEGER NOT NULL
                    CHECK (
                        semestre_recomendado
                        BETWEEN 1 AND 8
                    )
            )
            """
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS historial_consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_matricula TEXT NOT NULL,
                consulta TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                tipo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                confianza REAL NOT NULL
                    CHECK (
                        confianza BETWEEN 0 AND 1
                    ),
                fecha_hora TEXT NOT NULL,
                FOREIGN KEY (estudiante_matricula)
                    REFERENCES estudiantes (matricula)
                    ON DELETE CASCADE
            )
            """
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS retroalimentaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                historial_id INTEGER NOT NULL UNIQUE,
                fue_util INTEGER NOT NULL
                    CHECK (fue_util IN (0, 1)),
                fecha_hora TEXT NOT NULL,
                FOREIGN KEY (historial_id)
                    REFERENCES historial_consultas (id)
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
            grupo = f"{semestre}° ISD"

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

        asignaciones_examen = conexion.execute(
            """
            SELECT
                a.id,
                m.orden,
                h.hora_inicio,
                h.salon
            FROM asignaciones AS a
            INNER JOIN materias AS m
                ON m.id = a.materia_id
            INNER JOIN horarios AS h
                ON h.asignacion_id = a.id
            ORDER BY
                m.semestre,
                m.orden
            """
        ).fetchall()

        for asignacion in asignaciones_examen:
            asignacion_id = asignacion[0]
            orden = asignacion[1]
            hora = asignacion[2]
            salon = asignacion[3]

            desplazamiento = (
                DESPLAZAMIENTOS_EXAMEN[orden - 1]
            )

            for parcial, fecha_base in (
                FECHAS_BASE_EXAMENES.items()
            ):
                fecha_examen = (
                    fecha_base
                    + timedelta(days=desplazamiento)
                ).isoformat()

                conexion.execute(
                    """
                    INSERT INTO examenes (
                        asignacion_id,
                        parcial,
                        fecha,
                        hora,
                        salon
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT (
                        asignacion_id,
                        parcial
                    )
                    DO UPDATE SET
                        fecha = excluded.fecha,
                        hora = excluded.hora,
                        salon = excluded.salon
                    """,
                    (
                        asignacion_id,
                        parcial,
                        fecha_examen,
                        hora,
                        salon,
                    ),
                )

        conexion.executemany(
            """
            INSERT INTO avisos (
                codigo,
                titulo,
                mensaje,
                fecha_publicacion,
                fecha_evento,
                semestre,
                activo
            )
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT (codigo)
            DO UPDATE SET
                titulo = excluded.titulo,
                mensaje = excluded.mensaje,
                fecha_publicacion =
                    excluded.fecha_publicacion,
                fecha_evento = excluded.fecha_evento,
                semestre = excluded.semestre,
                activo = excluded.activo
            """,
            AVISOS_INICIALES,
        )

        conexion.executemany(
            """
            INSERT INTO contenido_academico (
                codigo,
                tema,
                materia,
                palabras_clave,
                explicacion,
                ejemplo,
                ejercicio,
                semestre_recomendado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (codigo)
            DO UPDATE SET
                tema = excluded.tema,
                materia = excluded.materia,
                palabras_clave =
                    excluded.palabras_clave,
                explicacion = excluded.explicacion,
                ejemplo = excluded.ejemplo,
                ejercicio = excluded.ejercicio,
                semestre_recomendado =
                    excluded.semestre_recomendado
            """,
            CONTENIDOS_ACADEMICOS,
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

def obtener_examenes_por_estudiante(matricula):
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        examenes = conexion.execute(
            """
            SELECT
                m.nombre AS materia,
                m.orden,
                ex.parcial,
                ex.fecha,
                ex.hora,
                ex.salon,
                p.nombre AS profesor
            FROM examenes AS ex
            INNER JOIN asignaciones AS a
                ON a.id = ex.asignacion_id
            INNER JOIN inscripciones AS i
                ON i.asignacion_id = a.id
            INNER JOIN materias AS m
                ON m.id = a.materia_id
            INNER JOIN profesores AS p
                ON p.id = a.profesor_id
            WHERE i.estudiante_matricula = ?
            ORDER BY
                ex.fecha,
                ex.hora,
                m.orden
            """,
            (matricula,),
        ).fetchall()

    return [
        dict(examen)
        for examen in examenes
    ]


def contar_examenes():
    with closing(conectar()) as conexion:
        resultado = conexion.execute(
            """
            SELECT COUNT(*)
            FROM examenes
            """
        ).fetchone()

    return resultado[0]

def obtener_avisos_por_estudiante(matricula):
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        avisos = conexion.execute(
            """
            SELECT
                av.codigo,
                av.titulo,
                av.mensaje,
                av.fecha_publicacion,
                av.fecha_evento,
                av.semestre
            FROM avisos AS av
            INNER JOIN estudiantes AS e
                ON e.matricula = ?
            WHERE av.activo = 1
                AND (
                    av.semestre IS NULL
                    OR av.semestre = e.semestre
                )
            ORDER BY
                av.fecha_evento,
                av.codigo
            """,
            (matricula,),
        ).fetchall()

    return [
        dict(aviso)
        for aviso in avisos
    ]


def contar_avisos():
    with closing(conectar()) as conexion:
        resultado = conexion.execute(
            """
            SELECT COUNT(*)
            FROM avisos
            """
        ).fetchone()

    return resultado[0]

def obtener_contenidos_academicos():
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        contenidos = conexion.execute(
            """
            SELECT
                codigo,
                tema,
                materia,
                palabras_clave,
                explicacion,
                ejemplo,
                ejercicio,
                semestre_recomendado
            FROM contenido_academico
            ORDER BY codigo
            """
        ).fetchall()

    return [
        dict(contenido)
        for contenido in contenidos
    ]


def contar_contenidos_academicos():
    with closing(conectar()) as conexion:
        resultado = conexion.execute(
            """
            SELECT COUNT(*)
            FROM contenido_academico
            """
        ).fetchone()

    return resultado[0]

def guardar_consulta_historial(
    matricula,
    consulta,
    respuesta,
    tipo,
    categoria,
    confianza,
):
    fecha_hora = datetime.now().isoformat(
        timespec="seconds"
    )

    with closing(conectar()) as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO historial_consultas (
                estudiante_matricula,
                consulta,
                respuesta,
                tipo,
                categoria,
                confianza,
                fecha_hora
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                matricula,
                consulta,
                respuesta,
                tipo,
                categoria,
                confianza,
                fecha_hora,
            ),
        )

        conexion.commit()

    return cursor.lastrowid

def obtener_historial_por_estudiante(
    matricula,
    limite=50,
):
    with closing(conectar()) as conexion:
        conexion.row_factory = sqlite3.Row

        historial = conexion.execute(
            """
            SELECT
                id,
                consulta,
                respuesta,
                tipo,
                categoria,
                confianza,
                fecha_hora
            FROM historial_consultas
            WHERE estudiante_matricula = ?
            ORDER BY
                fecha_hora DESC,
                id DESC
            LIMIT ?
            """,
            (
                matricula,
                limite,
            ),
        ).fetchall()

    return [
        dict(consulta)
        for consulta in historial
    ]

def guardar_retroalimentacion(
    historial_id,
    fue_util,
):
    valor_utilidad = 1 if fue_util else 0

    fecha_hora = datetime.now().isoformat(
        timespec="seconds"
    )

    with closing(conectar()) as conexion:
        conexion.execute(
            """
            INSERT INTO retroalimentaciones (
                historial_id,
                fue_util,
                fecha_hora
            )
            VALUES (?, ?, ?)
            ON CONFLICT (historial_id)
            DO UPDATE SET
                fue_util = excluded.fue_util,
                fecha_hora = excluded.fecha_hora
            """,
            (
                historial_id,
                valor_utilidad,
                fecha_hora,
            ),
        )

        conexion.commit()