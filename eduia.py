from datetime import date
from difflib import get_close_matches
import re
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from base_datos import (
    obtener_asignaciones_por_semestre,
    obtener_avisos_por_estudiante,
    obtener_calificaciones_por_estudiante,
    obtener_examenes_por_estudiante,
    obtener_horario_por_estudiante,
    obtener_materias_por_semestre,
    obtener_todas_las_materias,
    guardar_consulta_historial,
)
from academico import responder_consulta_academica

datos_entrenamiento = [
    # Saludos
    ("hola", "saludo"),
    ("buenos días", "saludo"),
    ("buenas tardes", "saludo"),
    ("qué tal", "saludo"),
    ("buen día", "saludo"),
    ("hola eduia", "saludo"),
    ("cómo estás", "saludo"),

    # Capacidades
    ("qué puedes hacer", "capacidades"),
    ("en qué me puedes ayudar", "capacidades"),
    ("cómo puedes ayudarme", "capacidades"),
    ("qué información puedes darme", "capacidades"),
    ("dime qué sabes hacer", "capacidades"),
    ("qué tipo de preguntas puedes responder", "capacidades"),
    ("para qué eres útil", "capacidades"),
    ("qué consultas puedes atender", "capacidades"),

    # Horarios
    ("cuál es mi horario", "horario"),
    ("qué horario tengo", "horario"),
    ("qué clases tengo", "horario"),
    ("a qué hora entro", "horario"),
    ("en qué salón tengo sistemas embebidos", "horario"),
    ("qué día tengo inteligencia artificial", "horario"),
    ("a qué hora tengo redes de computadoras ii", "horario"),
    ("dónde veo mi horario", "horario"),
    ("a qué hora comienzan mis clases", "horario"),
    ("a qué hora salgo", "horario"),
    ("dónde puedo consultar mis clases", "horario"),
    ("cuál es el salón de mi clase", "horario"),
    ("en qué salón me toca inteligencia artificial", "horario"),

    #materias
    ("qué materias tengo", "materia"),
    ("cuáles son mis materias", "materia"),
    ("qué materias curso", "materia"),
    ("lista de materias", "materia"),
    ("muéstrame mis materias", "materia"),
    ("qué asignaturas llevo", "materia"),
    ("cuáles son mis asignaturas", "materia"),
    ("qué materias tengo inscritas", "materia"),
    ("qué cursos llevo este semestre", "materia"),
    ("muéstrame mis asignaturas", "materia"),

    # Exámenes
    ("cuándo tengo examen", "examen"),
    ("cuándo es mi examen", "examen"),
    ("qué exámenes tengo", "examen"),
    ("fecha de mis exámenes", "examen"),
    ("cuándo presento mi parcial", "examen"),
    ("cuándo es mi examen de inteligencia artificial", "examen"),
    ("en qué salón es mi examen de sistemas embebidos", "examen"),
    ("a qué hora es el examen de redes de computadoras ii", "examen"),
    ("cuáles son mis próximas evaluaciones", "examen"),
    ("cuándo es mi próximo examen", "examen"),
    ("dónde presentaré mi examen", "examen"),
    ("muéstrame el horario de exámenes", "examen"),
    ("tengo algún examen pronto", "examen"),

    # Profesores
    ("quiénes son mis profesores", "profesor"),
    ("quiénes son mis maestros", "profesor"),
    ("quién me da clases", "profesor"),
    ("cómo se llama mi maestro", "profesor"),
    ("quién es mi profesor", "profesor"),
    ("quién es mi docente", "profesor"),
    ("quién imparte mis materias", "profesor"),
    ("quién imparte inteligencia artificial", "profesor"),
    ("quién da sistemas embebidos", "profesor"),
    ("quién es el profesor de redes de computadoras ii", "profesor"),
    ("cuáles son los docentes de mi semestre", "profesor"),
    ("qué maestros me dan clases", "profesor"),
    ("quién enseña mis asignaturas", "profesor"),
    ("muéstrame los datos de mis profesores", "profesor"),
    ("cuál es el correo de mi maestro", "profesor"),
    ("dame el correo del profesor de una materia", "profesor"),
    ("necesito el contacto de quien imparte una materia", "profesor"),
    ("cuál es el correo de quien enseña una materia", "profesor"),
    ("dame el contacto del docente de redes de computadoras ii", "profesor"),

    # Calificaciones
    ("cuáles son mis calificaciones", "calificacion"),
    ("quiero ver mis calificaciones", "calificacion"),
    ("quiero consultar mis notas", "calificacion"),
    ("qué resultados obtuve", "calificacion"),
    ("qué calificación tengo en inteligencia artificial", "calificacion"),
    ("cuál es mi promedio de sistemas embebidos", "calificacion"),
    ("cuánto saqué en redes de computadoras ii", "calificacion"),
    ("dónde veo mis notas", "calificacion"),
    ("cuánto saqué", "calificacion"),
    ("qué promedio tengo", "calificacion"),
    ("muéstrame los resultados de mis materias", "calificacion"),
    ("quiero consultar mi boleta", "calificacion"),
    ("qué nota obtuve en inteligencia artificial", "calificacion"),
    ("qué materias tengo reprobadas", "calificacion"),
    ("dónde miro mis calificasiones", "calificacion"),
    ("quiero saber si aprobé una materia", "calificacion"),
    ("cómo sé si pasé inteligencia artificial", "calificacion"),
    ("quiero saber si aprobé inteligencia artificial", "calificacion"),
    ("aprobé o reprobé una materia", "calificacion"),

    # Avisos escolares
    ("hay avisos escolares", "aviso"),
    ("cuáles son los avisos", "aviso"),
    ("hay alguna actividad escolar", "aviso"),
    ("qué eventos tiene la escuela", "aviso"),
    ("qué novedades hay en la universidad", "aviso"),
    ("muéstrame los comunicados escolares", "aviso"),
    ("tengo avisos pendientes", "aviso"),
    ("hay información escolar reciente", "aviso"),
    ("cuáles son los próximos eventos", "aviso"),

    # Ayuda académica
    ("ayúdame a estudiar", "academica"),
    ("no entiendo este tema", "academica"),
    ("explícame pseudocódigo", "academica"),
    ("explícame el modelo relacional", "academica"),
    ("explícame planificación de procesos", "academica"),
    ("explícame tf idf", "academica"),
    ("explícame rtos", "academica"),
    ("ponme un ejercicio", "academica"),
    ("hazme un resumen", "academica"),
    ("necesito ayuda con una materia", "academica"),
    ("dame un ejemplo", "academica"),
    ("ayúdame a entender un tema", "academica"),
    ("hazme una explicación", "academica"),
    ("dame un ejercicio de práctica", "academica"),

    # Inscripciones
    ("cuándo son las inscripciones", "inscripcion"),
    ("cómo puedo inscribirme", "inscripcion"),
    ("dónde realizo mi inscripción", "inscripcion"),
    ("qué necesito para inscribirme", "inscripcion"),
    ("cuál es el proceso de inscripción", "inscripcion"),
    ("qué documentos piden para la inscripción", "inscripcion"),
    ("quiero registrar mis materias para el próximo periodo","inscripcion"),
    ("cómo me inscribo al siguiente semestre", "inscripcion"),

    # Biblioteca
    ("dónde está la biblioteca", "biblioteca"),
    ("cuál es el horario de la biblioteca", "biblioteca"),
    ("puedo pedir libros prestados", "biblioteca"),
    ("qué servicios ofrece la biblioteca", "biblioteca"),
    ("cómo solicito un libro en la biblioteca", "biblioteca"),
    ("hay espacios para estudiar en la biblioteca", "biblioteca"),

    # Becas
    ("qué becas están disponibles", "beca"),
    ("cómo puedo solicitar una beca", "beca"),
    ("qué requisitos necesito para una beca", "beca"),
    ("cuándo abre la convocatoria de becas", "beca"),
    ("dónde consulto información sobre becas", "beca"),
    ("la universidad ofrece apoyo económico", "beca"),
    ("qué documentos solicitan para la beca", "beca"),
    ("hay alguna convocatoria para estudiantes", "beca"),
    ("dónde pregunto por las vecas", "beca"),
    ("hay ayuda económica para pagar mis estudios", "beca"),
    ("puedo recibir apoyo para estudiar", "beca"),

    # Titulación
    ("cómo puedo titularme", "titulacion"),
    ("qué opciones de titulación existen", "titulacion"),
    ("qué documentos necesito para titularme", "titulacion"),
    ("dónde inicio mi proceso de titulación", "titulacion"),
    ("cuáles son los requisitos de titulación", "titulacion"),
    ("de qué formas puedo obtener mi título", "titulacion"),
    ("puedo hacer una tesis para graduarme", "titulacion"),
    ("qué papeles debo entregar para mi título", "titulacion"),
    ("dónde pregunto por la titulasion", "titulacion"),
    ("qué modalidades existen para terminar la carrera", "titulacion"),
    ("dónde entrego mi expediente para obtener el grado", "titulacion"),
    ("cómo obtengo el grado al finalizar la carrera", "titulacion"),

    # Laboratorios
    ("dónde están los laboratorios", "laboratorio"),
    ("cuál es el horario de los laboratorios", "laboratorio"),
    ("cómo puedo utilizar un laboratorio", "laboratorio"),
    ("qué laboratorios tiene la universidad", "laboratorio"),
    ("necesito reservar el laboratorio", "laboratorio"),
    ("puedo entrar al lavotatorio", "laboratorio"),
    ("debo reservar el laboratorio para una práctica", "laboratorio"),
    ("cómo aparto un laboratorio antes de usarlo", "laboratorio"),

    # Cafetería
    ("dónde está la cafetería", "cafeteria"),
    ("cuál es el horario de la cafetería", "cafeteria"),
    ("qué alimentos vende la cafetería", "cafeteria"),
    ("cuánto cuesta la comida en la cafetería", "cafeteria"),
    ("la cafetería está abierta", "cafeteria"),
    ("qué menú tienen hoy", "cafeteria"),
    ("abre la cafetería los sábados", "cafeteria"),
    ("a qué hora abre la cafeteira", "cafeteria"),
    ("venden café en la cafetería", "cafeteria"),
    ("dónde puedo comprar café en la universidad", "cafeteria"),
]

preguntas_conocidas = [
    pregunta for pregunta, categoria in datos_entrenamiento
]

categorias_conocidas = [
    categoria for pregunta, categoria in datos_entrenamiento
]

PALABRAS_IGNORADAS = [
    "que",
    "cual",
    "cuales",
    "cuando",
    "quien",
    "quienes",
    "como",
    "donde",
    "es",
    "son",
    "mi",
    "mis",
    "tengo",
    "de",
    "del",
    "el",
    "la",
    "los",
    "las",
    "un",
    "una",
    "en",
    "me",
    "quiero",
    "ver",
    "consultar",
    "por",
    "favor",
]

UMBRAL_CONFIANZA = 0.30

RESPUESTA_DESCONOCIDA = (
    "No tengo información suficientemente confiable para responder. "
    "Intenta reformular tu pregunta."
)

RESPUESTAS_CATEGORIA = {
    "saludo": "Hola, ¿en qué puedo ayudarte?",
    "capacidades": (
        "Puedo ayudarte con horarios, materias, exámenes, profesores, "
        "calificaciones, inscripciones, biblioteca, becas, titulación, "
        "laboratorios, cafetería, avisos y temas académicos."
    ),
    "horario": "Puedo consultar tu horario escolar.",
    "materia": "Puedo consultar tus materias inscritas.",
    "examen": "Puedo consultar las fechas de tus exámenes.",
    "profesor": "Puedo mostrarte la información de tus profesores.",
    "calificacion": "Puedo consultar tus calificaciones.",
    "aviso": "Puedo mostrarte los avisos escolares disponibles.",
    "academica": (
        "Puedo explicarte el tema, mostrarte un ejemplo "
        "y proponerte un ejercicio."
    ),
    "inscripcion": (
        "Para realizar tu inscripción:\n"
        "1. Consulta el periodo de inscripciones vigente.\n"
        "2. Verifica los documentos y requisitos solicitados.\n"
        "3. Entrega la documentación o completa el registro indicado.\n"
        "4. Confirma que tus materias hayan quedado registradas.\n"
        "Para conocer fechas y requisitos oficiales, acude a Servicios Escolares."
    ),

    "biblioteca": (
        "La biblioteca ofrece préstamo de libros, consulta de material "
        "académico y espacios de estudio.\n"
        "Para utilizar el préstamo, presenta tu identificación o matrícula "
        "vigente y consulta la disponibilidad del material.\n"
        "Los horarios y condiciones del servicio pueden confirmarse "
        "directamente en la biblioteca."
    ),

    "beca": (
        "Para solicitar una beca:\n"
        "1. Consulta las convocatorias disponibles.\n"
        "2. Revisa los requisitos y fechas de registro.\n"
        "3. Prepara la documentación solicitada.\n"
        "4. Entrega tu solicitud dentro del periodo establecido.\n"
        "La información oficial se encuentra disponible en Servicios Escolares."
    ),

    "titulacion": (
        "Para iniciar tu proceso de titulación:\n"
        "1. Verifica que cumplas con los créditos y requisitos académicos.\n"
        "2. Consulta las modalidades de titulación disponibles.\n"
        "3. Reúne los documentos solicitados.\n"
        "4. Registra tu trámite en el área de Titulación o Servicios Escolares.\n"
        "Las opciones y requisitos pueden cambiar, por lo que debes consultar "
        "la convocatoria vigente."
    ),

    "laboratorio": (
        "Los laboratorios se utilizan para realizar prácticas académicas.\n"
        "Antes de ingresar, consulta el horario, la disponibilidad y las "
        "reglas de seguridad correspondientes.\n"
        "Si necesitas utilizar un laboratorio fuera de clase, solicita "
        "autorización o reservación con el profesor o responsable del área."
    ),

    "cafeteria": (
        "La cafetería universitaria ofrece alimentos y bebidas para los "
        "estudiantes.\n"
        "El menú, los precios y los horarios pueden variar, por lo que debes "
        "consultarlos directamente en la cafetería.\n"
        "Antes de acudir, verifica que el servicio se encuentre disponible."
    ),
    "desconocida": RESPUESTA_DESCONOCIDA,
}

TIPOS_CATEGORIA = {
    "saludo": "general",
    "capacidades": "general",
    "horario": "escolar",
    "materia": "escolar",
    "examen": "escolar",
    "profesor": "escolar",
    "calificacion": "escolar",
    "aviso": "escolar",
    "academica": "académica",
    "inscripcion": "escolar",
    "biblioteca": "escolar",
    "beca": "escolar",
    "titulacion": "escolar",
    "laboratorio": "escolar",
    "cafeteria": "escolar",
    "desconocida": "desconocida",
}

vectorizador_palabras = TfidfVectorizer(
    strip_accents="unicode",
    stop_words=PALABRAS_IGNORADAS,
    ngram_range=(1, 1),
    sublinear_tf=True,
)

matriz_palabras = vectorizador_palabras.fit_transform(
    preguntas_conocidas
)

# Los n-gramas de caracteres permiten reconocer palabras aunque
# contengan sustituciones, omisiones o letras intercambiadas.
vectorizador_caracteres = TfidfVectorizer(
    analyzer="char_wb",
    strip_accents="unicode",
    ngram_range=(3, 5),
    sublinear_tf=True,
)

matriz_caracteres = vectorizador_caracteres.fit_transform(
    preguntas_conocidas
)

VOCABULARIO_CONOCIDO = set(
    vectorizador_palabras.get_feature_names_out()
)

PALABRAS_CLAVE_CORREGIBLES = {
    "horario",
    "horarios",
    "biblioteca",
    "libro",
    "libros",
    "beca",
    "becas",
    "titulacion",
    "titulo",
    "laboratorio",
    "laboratorios",
    "cafeteria",
    "calificacion",
    "calificaciones",
    "inscripcion",
    "inscripciones",
    "profesor",
    "profesores",
    "maestro",
    "maestros",
    "docente",
    "docentes",
    "examen",
    "examenes",
    "evaluacion",
    "evaluaciones",
    "materia",
    "materias",
    "aviso",
    "avisos",
}

CORRECCIONES_DIRECTAS = {
    "abiso": "aviso",
    "abisos": "avisos",
    "evaluasion": "evaluacion",
    "evaluasiones": "evaluaciones",
    "kuando": "cuando",
    "akademiko": "academico",
    "asta": "hasta",
    "benden": "venden",
    "beo": "veo",
    "komida": "comida",
    "komunicado": "comunicado",
    "komunicados": "comunicados",
    "konbocatoria": "convocatoria",
    "kiero": "quiero",
    "nuebo": "nuevo",
    "onde": "donde",
    "ora": "hora",
    "procsima": "proxima",
    "procsimo": "proximo",
    "reientes": "recientes",
    "rejistro": "registro",
    "renobar": "renovar",
    "rezultado": "resultado",
    "saver": "saber",
    "veka": "beca",
    "vekas": "becas",
    "veca": "beca",
    "vecas": "becas",
    "titulasion": "titulacion",
}

def corregir_ortografia(texto):
    texto_normalizado = normalizar_texto(texto)

    palabras = re.findall(
        r"\b\w+\b",
        texto_normalizado,
    )

    palabras_corregidas = []

    for palabra in palabras:
        if palabra in CORRECCIONES_DIRECTAS:
            palabras_corregidas.append(
                CORRECCIONES_DIRECTAS[palabra]
            )
            continue

        if (
            palabra in VOCABULARIO_CONOCIDO
            or palabra in PALABRAS_IGNORADAS
            or len(palabra) < 4
        ):
            palabras_corregidas.append(palabra)
            continue

        # Las palabras cortas necesitan un límite
        # ligeramente menor para detectar beka -> beca.
        if len(palabra) <= 4:
            limite = 0.75
        else:
            limite = 0.82

        coincidencias = get_close_matches(
            palabra,
            PALABRAS_CLAVE_CORREGIBLES,
            n=1,
            cutoff=limite,
        )

        if coincidencias:
            palabras_corregidas.append(
                coincidencias[0]
            )
        else:
            palabras_corregidas.append(palabra)

    return " ".join(palabras_corregidas)

def identificar_categoria_prioritaria(texto):
    texto_normalizado = normalizar_texto(texto)

    palabras = set(
        re.findall(
            r"\b\w+\b",
            texto_normalizado,
        )
    )

    indicadores = {
        "capacidades": {
            "capaz",
            "capacidades",
            "funcion",
            "funciones",
        },
        "profesor": {
            "profesor",
            "profesores",
            "maestro",
            "maestros",
            "docente",
            "docentes",
            "correo",
            "contacto",
            "imparte",
            "ensena",
        },
        "calificacion": {
            "calificacion",
            "calificaciones",
            "nota",
            "notas",
            "promedio",
            "boleta",
            "resultado",
            "resultados",
            "aprobar",
            "aprobe",
            "pase",
            "reprobar",
            "reprobada",
            "reprobadas",
        },
        "examen": {
            "examen",
            "examenes",
            "evaluacion",
            "evaluaciones",
            "parcial",
            "parciales",
            "presentare",
        },
        "inscripcion": {
            "inscripcion",
            "inscripciones",
            "inscrito",
            "inscrita",
            "inscribirme",
            "reinscripcion",
            "reinscribirme",
            "reinscribo",
            "reinscrito",
            "reinscrita",
        },
        "horario": {
            "horario",
            "horarios",
            "hora",
            "salon",
            "clase",
            "clases",
            "momento",
        },
        "materia": {
            "materia",
            "materias",
            "asignatura",
            "asignaturas",
        },
        "aviso": {
            "aviso",
            "avisos",
            "comunicado",
            "comunicados",
            "anuncio",
            "anuncios",
            "notificacion",
            "notificaciones",
        },
        "biblioteca": {
            "biblioteca",
            "libro",
            "libros",
            "lectura",
            "prestamo",
        },
        "beca": {
            "beca",
            "becas",
            "financiera",
            "economico",
        },
        "titulacion": {
            "titulacion",
            "titulo",
            "titularme",
            "grado",
            "tesis",
        },
        "laboratorio": {
            "laboratorio",
            "laboratorios",
        },
        "cafeteria": {
            "cafeteria",
            "cafeteira",
            "almuerzo",
            "almuerzos",
            "bebida",
            "bebidas",
            "menu",
            "comida",
            "alimentos",
        },
    }

    # Algunas intenciones se expresan mejor mediante frases.
    frases_prioritarias = (
        ("profesor", ("a cargo",)),
        (
            "capacidades",
            (
                "puedes hacer",
                "eres capaz",
                "ayuda universitaria",
                "brindas orientacion",
                "informacion universitaria manejas",
                "servicios puedes consultar",
            ),
        ),
        (
            "aviso",
            (
                "informacion nueva",
                "mensaje importante",
                "novedades oficiales",
            ),
        ),
        (
            "inscripcion",
            (
                "confirmar mi carga",
                "formalizo mi registro",
                "registrar el semestre",
                "registrar mis materias",
                "registro semestral",
                "renovar mi carga",
                "renovar mi inscripcion",
            ),
        ),
        (
            "biblioteca",
            (
                "material de consulta",
                "material de lectura",
                "lugar silencioso",
                "prestamo bibliografico",
                "reglas de prestamo",
            ),
        ),
        (
            "beca",
            (
                "ayuda financiera",
                "apoyo economico",
                "apoyo escolar",
                "beneficiado con el apoyo",
                "convocatoria de beca",
                "convocatoria de becas",
            ),
        ),
        (
            "academica",
            (
                "para aprender",
                "para comprender",
                "para entender",
                "dame un ejemplo",
                "funcionamiento de una red",
                "un ejemplo de",
            ),
        ),
        (
            "laboratorio",
            (
                "agendar una practica",
                "apartar una practica",
                "reservar una practica",
                "reservo una practica",
            ),
        ),
        (
            "titulacion",
            (
                "modalidad con la que terminare la carrera",
                "procedimiento para obtener mi grado",
                "via puedo escoger para conseguir el titulo",
            ),
        ),
        (
            "materia",
            (
                "carga academica",
                "carga escolar",
                "unidades de aprendizaje",
            ),
        ),
    )

    for categoria, frases in frases_prioritarias:
        if any(
            frase in texto_normalizado
            for frase in frases
        ):
            return categoria

    # Las raíces permiten reconocer conjugaciones y variantes como
    # “impartir”, “acredité”, “inscrito” o “beneficiado”.
    raices_prioritarias = (
        ("profesor", ("impart", "docent", "maestr", "profesor")),
        ("titulacion", ("titul", "grado")),
        (
            "calificacion",
            (
                "acredit",
                "bolet",
                "calific",
                "desempen",
                "nota",
                "promed",
                "reprob",
            ),
        ),
        ("examen", ("exam", "evalu", "parcial")),
        ("inscripcion", ("inscri", "reinscri")),
        ("aviso", ("anunci", "avis", "comunic", "notific")),
        ("biblioteca", ("bibliotec", "lectur", "prestam")),
        ("beca", ("bec", "benefici", "financ")),
        ("laboratorio", ("laborator",)),
        ("cafeteria", ("aliment", "almuerz", "bebid", "cafeter", "comedor")),
        ("horario", ("clase", "horar", "salon")),
        ("materia", ("asignatur", "materi")),
        ("academica", ("algorit", "ejerc", "neuronal", "pseudocod")),
    )

    for categoria, raices in raices_prioritarias:
        if any(
            palabra.startswith(raiz)
            for palabra in palabras
            for raiz in raices
        ):
            return categoria

    # El orden evita que "evaluación de una materia" se confunda
    # con horario o que "registrar materias" se confunda con materia.
    orden_prioridad = (
        "capacidades",
        "profesor",
        "titulacion",
        "calificacion",
        "examen",
        "inscripcion",
        "aviso",
        "biblioteca",
        "beca",
        "laboratorio",
        "cafeteria",
        "horario",
        "materia",
    )

    for categoria in orden_prioridad:
        if palabras & indicadores[categoria]:
            return categoria

    return None

def calcular_similitud_clasificacion(texto):
    vector_palabras = vectorizador_palabras.transform(
        [texto]
    )

    similitudes_palabras = cosine_similarity(
        vector_palabras,
        matriz_palabras,
    )[0]

    vector_caracteres = vectorizador_caracteres.transform(
        [texto]
    )

    similitudes_caracteres = cosine_similarity(
        vector_caracteres,
        matriz_caracteres,
    )[0]

    # Las palabras conservan el mayor peso semántico y los
    # caracteres aportan tolerancia ante errores ortográficos.
    similitudes = (
        0.65 * similitudes_palabras
        + 0.35 * similitudes_caracteres
    )

    indice = int(similitudes.argmax())
    confianza = float(similitudes[indice])
    confianza = max(0.0, min(1.0, confianza))

    return similitudes, indice, confianza

def obtener_respuesta_aclaracion(texto):
    texto_normalizado = normalizar_texto(texto)

    palabras = set(
        re.findall(
            r"\b\w+\b",
            texto_normalizado,
        )
    )

    palabras_registro = {
        "registrar",
        "registrarme",
        "registrarse",
        "registro",
    }

    contexto_registro = {
        "actividad",
        "actividades",
        "beca",
        "becas",
        "biblioteca",
        "carrera",
        "grado",
        "inscripcion",
        "inscripciones",
        "laboratorio",
        "laboratorios",
        "materia",
        "materias",
        "modalidad",
        "modalidades",
        "periodo",
        "reinscripcion",
        "reinscripciones",
        "semestre",
        "semestral",
        "taller",
        "talleres",
        "titularme",
        "titulacion",
        "titulo",
    }

    if (
        palabras & palabras_registro
        and not palabras & contexto_registro
    ):
        return (
            "Necesito un poco más de información. "
            "¿Te refieres a realizar tu inscripción escolar, "
            "registrarte en una beca, taller o algún otro servicio?"
        )

    # Una calificación sin materia, examen o periodo puede referirse
    # a distintos resultados. EduIA debe pedir el dato que falta.
    frases_calificacion_sin_contexto = {
        "cuanto saque",
        "cual es la calificacion",
        "que calificacion tengo",
        "cual fue mi resultado",
    }

    contexto_calificacion = {
        "asignatura",
        "asignaturas",
        "examen",
        "examenes",
        "materia",
        "materias",
        "parcial",
        "parciales",
        "semestre",
    }

    es_calificacion_sin_contexto = any(
        frase in texto_normalizado
        for frase in frases_calificacion_sin_contexto
    )

    if es_calificacion_sin_contexto:
        texto_sin_materias = eliminar_nombres_materias(
            texto_normalizado
        )
        tiene_materia = (
            texto_sin_materias != texto_normalizado
        )

        if (
            not palabras & contexto_calificacion
            and not tiene_materia
        ):
            return (
                "¿De qué materia, examen o periodo quieres "
                "consultar la calificación?"
            )

    frases_lugar_sin_contexto = {
        "donde esta el lugar",
        "donde se encuentra el lugar",
        "donde queda el lugar",
    }

    if any(
        frase in texto_normalizado
        for frase in frases_lugar_sin_contexto
    ):
        return (
            "¿Qué lugar o servicio universitario deseas localizar?"
        )

    palabras_profesor = {
        "docente",
        "docentes",
        "maestro",
        "maestros",
        "profesor",
        "profesores",
    }

    palabras_opinion = {
        "agradable",
        "agradables",
        "buena",
        "bueno",
        "mal",
        "mala",
        "malo",
        "mejor",
        "onda",
        "peor",
    }

    if (
        palabras & palabras_profesor
        and palabras & palabras_opinion
    ):
        return (
            "No puedo emitir opiniones personales sobre tus profesores. "
            "Puedo indicarte quién imparte cada materia y mostrarte "
            "sus datos académicos. ¿Quieres consultar esa información?"
        )

    return None

def es_consulta_ambigua_o_fuera(texto):
    texto_normalizado = normalizar_texto(texto)

    palabras = set(
        re.findall(
            r"\b\w+\b",
            texto_normalizado,
        )
    )

    # Temas que EduIA todavía no atiende.
    palabras_fuera_alcance = {
        "aeropuerto",
        "banco",
        "bitcoin",
        "bullying",
        "cancion",
        "canciones",
        "celular",
        "chiste",
        "clima",
        "cocinar",
        "contrasena",
        "dentista",
        "doctor",
        "doctora",
        "eleccion",
        "elecciones",
        "festeja",
        "festejo",
        "futbol",
        "gripe",
        "hospital",
        "horoscopo",
        "llover",
        "lonche",
        "lonches",
        "medica",
        "medico",
        "mochila",
        "mochilas",
        "musica",
        "noticia",
        "noticias",
        "novia",
        "novio",
        "oferta",
        "ofertas",
        "partido",
        "pelea",
        "peleas",
        "pelicula",
        "plazoleta",
        "politica",
        "politicas",
        "polinesios",
        "receta",
        "recetas",
        "restaurante",
        "restaurantes",
        "ruta",
        "salud",
        "taxi",
        "telefono",
        "trafico",
        "transporte",
        "videojuego",
        "videojuegos",
        "virus",
        "vuelo",
        "vuelos",
        "wifi",
    }

    if palabras & palabras_fuera_alcance:
        return True

    # Algunas consultas externas se reconocen mejor como frases,
    # porque sus palabras aisladas también pueden usarse en la escuela.
    frases_fuera_alcance = {
        "me siento mal",
        "sentirme mal",
        "puerto vallarta",
        "de que esta hecho el cafe",
        "como se prepara el cafe",
    }

    if any(
        frase in texto_normalizado
        for frase in frases_fuera_alcance
    ):
        return True

    # Comprar productos externos no forma parte de los servicios
    # de EduIA. Se permite cuando la consulta habla de alimentos
    # o de la cafetería universitaria.
    palabras_compra = {
        "comprar",
        "compro",
        "venden",
    }

    contexto_cafeteria = {
        "alimento",
        "alimentos",
        "bebida",
        "bebidas",
        "cafe",
        "cafeteria",
        "cafeteira",
        "comida",
        "desayuno",
        "menu",
    }

    if (
        palabras & palabras_compra
        and not palabras & contexto_cafeteria
    ):
        return True

    # Palabras que sí proporcionan un contexto universitario
    # suficiente para interpretar una consulta.
    contexto_universitario = {
        "academica",
        "academico",
        "asignatura",
        "asignaturas",
        "anuncio",
        "anuncios",
        "aviso",
        "avisos",
        "beca",
        "becas",
        "biblioteca",
        "boleta",
        "cafe",
        "cafeteria",
        "cafeteira",
        "calificacion",
        "calificaciones",
        "carrera",
        "clase",
        "clases",
        "comida",
        "comunicado",
        "comunicados",
        "convocatoria",
        "convocatorias",
        "correo",
        "docente",
        "docentes",
        "evaluacion",
        "evaluaciones",
        "ejemplo",
        "examen",
        "examenes",
        "grado",
        "horario",
        "inscripcion",
        "inscripciones",
        "inscribirme",
        "inscrito",
        "inscrita",
        "laboratorio",
        "laboratorios",
        "libro",
        "libros",
        "maestro",
        "maestros",
        "materia",
        "materias",
        "modalidad",
        "modalidades",
        "menu",
        "nota",
        "notas",
        "parcial",
        "parciales",
        "planificacion",
        "prestamo",
        "profesor",
        "profesores",
        "promedio",
        "reinscripcion",
        "reinscribirme",
        "reinscrito",
        "reinscrita",
        "registrarme",
        "salon",
        "tesis",
        "titulacion",
        "titularme",
        "titulo",
    }

    # La mención de una materia concreta también proporciona contexto,
    # aunque sus palabras no aparezcan en el conjunto anterior.
    texto_sin_materias = eliminar_nombres_materias(
        texto_normalizado
    )
    tiene_materia = texto_sin_materias != texto_normalizado

    tiene_contexto = bool(
        palabras & contexto_universitario
    ) or tiene_materia

    # Pronombres y referencias como “lo” o “alguno” necesitan
    # información previa que EduIA no debe inventar.
    referencias_sin_contexto = {
        "algo",
        "alguna",
        "alguno",
        "algunas",
        "algunos",
        "eso",
        "esa",
        "ese",
        "esto",
        "lo",
        "solicitarlo",
    }

    if (
        palabras & referencias_sin_contexto
        and not tiene_contexto
    ):
        return True

    # Términos demasiado generales requieren indicar de qué
    # servicio, trámite o recurso se está hablando.
    terminos_genericos = {
        "cupo",
        "disponible",
        "disponibles",
        "escoger",
        "elegir",
        "fecha",
        "hacerlo",
        "limite",
        "opcion",
        "opciones",
        "presentarme",
        "pregunto",
        "proceso",
        "procesos",
        "renovarlo",
        "realiza",
        "resultado",
        "completar",
        "tramite",
        "tramites",
        "ubicado",
        "ubicada",
    }

    if (
        palabras & terminos_genericos
        and not tiene_contexto
    ):
        return True

    frases_sin_contexto = {
        "necesito llevar",
        "debo llevar",
        "tengo que llevar",
    }

    if (
        any(
            frase in texto_normalizado
            for frase in frases_sin_contexto
        )
        and not tiene_contexto
    ):
        return True

    # “Documentos” necesita indicar para qué trámite.
    palabras_documentos = {
        "documento",
        "documentos",
        "papel",
        "papeles",
        "requisito",
        "requisitos",
    }

    contexto_documentos = {
        "inscripcion",
        "inscripciones",
        "inscribirme",
        "reinscripcion",
        "reinscribirme",
        "beca",
        "becas",
        "titulacion",
        "titulo",
        "titularme",
    }

    if (
        palabras & palabras_documentos
        and not palabras & contexto_documentos
    ):
        return True

    # “Abierto” necesita indicar qué servicio.
    palabras_apertura = {
        "abre",
        "abierto",
        "abierta",
    }

    contexto_apertura = {
        "cafeteria",
        "cafeteira",
        "biblioteca",
        "inscripcion",
        "inscripciones",
        "laboratorio",
        "laboratorios",
        "reinscripcion",
        "reinscripciones",
    }

    if (
        palabras & palabras_apertura
        and not palabras & contexto_apertura
    ):
        return True

    # “Cuánto cuesta” necesita indicar el producto.
    palabras_precio = {
        "cuesta",
        "costo",
        "precio",
        "vale",
    }

    contexto_precio = {
        "cafeteria",
        "comida",
        "alimento",
        "alimentos",
        "menu",
        "desayuno",
        "bebida",
        "bebidas",
    }

    if (
        palabras & palabras_precio
        and not palabras & contexto_precio
    ):
        return True

    return False

def eliminar_nombres_materias(texto):
    texto_sin_materias = normalizar_texto(texto)

    materias = obtener_todas_las_materias()
    variantes = set()

    for materia in materias:
        nombre = normalizar_texto(
            materia["nombre"]
        )

        variantes.add(nombre)

        # Reconocer II, 2 y “dos” como equivalentes.
        if nombre.endswith(" ii"):
            nombre_base = nombre[:-3]

            variantes.add(f"{nombre_base} 2")
            variantes.add(f"{nombre_base} dos")

        # Reconocer I, 1 y “uno” como equivalentes.
        elif nombre.endswith(" i"):
            nombre_base = nombre[:-2]

            variantes.add(f"{nombre_base} 1")
            variantes.add(f"{nombre_base} uno")

    # Abreviaciones comunes de materias.
    variantes.update(
        {
            "ia",
            "redes ii",
            "redes 2",
            "redes dos",
        }
    )

    for variante in sorted(
        variantes,
        key=len,
        reverse=True,
    ):
        patron = rf"\b{re.escape(variante)}\b"

        texto_sin_materias = re.sub(
            patron,
            " ",
            texto_sin_materias,
        )

    texto_sin_materias = re.sub(
        r"\s+",
        " ",
        texto_sin_materias,
    )

    return texto_sin_materias.strip()

def buscar_respuesta(pregunta_usuario):
    pregunta_corregida = corregir_ortografia(
        pregunta_usuario
    )

    respuesta_aclaracion = obtener_respuesta_aclaracion(
        pregunta_corregida
    )

    if respuesta_aclaracion is not None:
        return (
            respuesta_aclaracion,
            TIPOS_CATEGORIA["desconocida"],
            "desconocida",
            0.0,
        )

    if es_consulta_ambigua_o_fuera(
        pregunta_corregida
    ):

        categoria = "desconocida"
        confianza = 0.0

        return (
            RESPUESTAS_CATEGORIA[categoria],
            TIPOS_CATEGORIA[categoria],
            categoria,
            confianza,
        )

    pregunta_sin_materia = eliminar_nombres_materias(
        pregunta_corregida
    )

    (
        similitudes_originales,
        indice_original,
        confianza_original,
    ) = calcular_similitud_clasificacion(
        pregunta_corregida
    )

    (
        similitudes_sin_materia,
        indice_sin_materia,
        confianza_sin_materia,
    ) = calcular_similitud_clasificacion(
        pregunta_sin_materia
    )

    categoria_prioritaria = identificar_categoria_prioritaria(
        pregunta_usuario
    )

    if categoria_prioritaria is None:
        categoria_prioritaria = identificar_categoria_prioritaria(
            pregunta_corregida
        )

    if categoria_prioritaria is not None:
        categoria = categoria_prioritaria

        indices_categoria = [
            indice
            for indice, categoria_ejemplo
            in enumerate(categorias_conocidas)
            if categoria_ejemplo == categoria
        ]

        confianza = max(
            (
                max(
                    similitudes_originales[indice],
                    similitudes_sin_materia[indice],
                )
                for indice in indices_categoria
            ),
            default=0.0,
        )

        # Una regla explícita aporta confianza semántica,
        # aunque la semejanza textual sea pequeña.
        confianza = max(0.60, float(confianza))

    else:
        if confianza_original >= confianza_sin_materia:
            indice_mejor_resultado = indice_original
            confianza = confianza_original
        else:
            indice_mejor_resultado = indice_sin_materia
            confianza = confianza_sin_materia

        if confianza < UMBRAL_CONFIANZA:
            categoria = "desconocida"
        else:
            categoria = categorias_conocidas[
                indice_mejor_resultado
            ]

    confianza = max(0.0, min(1.0, confianza))

    tipo = TIPOS_CATEGORIA[categoria]
    respuesta = RESPUESTAS_CATEGORIA[categoria]

    return respuesta, tipo, categoria, confianza

def normalizar_texto(texto):
    texto_normalizado = unicodedata.normalize(
        "NFD",
        texto.lower(),
    )

    return "".join(
        caracter
        for caracter in texto_normalizado
        if unicodedata.category(caracter) != "Mn"
    )


def identificar_materia(pregunta):
    materias = obtener_todas_las_materias()

    pregunta_normalizada = normalizar_texto(
        pregunta
    )

    materias_ordenadas = sorted(
        materias,
        key=lambda materia: len(materia["nombre"]),
        reverse=True,
    )

    for materia in materias_ordenadas:
        nombre_normalizado = normalizar_texto(
            materia["nombre"]
        )

        if nombre_normalizado in pregunta_normalizada:
            return materia

    return None

def construir_respuesta_horario(
    matricula,
    materia_buscada=None,
):
    horario = obtener_horario_por_estudiante(
        matricula
    )

    if not horario:
        return (
            "No encontré un horario registrado "
            "para este estudiante."
        )

    if materia_buscada is not None:
        horario = [
            clase
            for clase in horario
            if clase["materia"] == materia_buscada
        ]

        if not horario:
            return (
                f"No encontré un horario registrado "
                f"para {materia_buscada}."
            )

        lineas = [
            f"Tu horario de {materia_buscada} es:"
        ]
    else:
        lineas = ["Este es tu horario:"]

    for clase in horario:
        lineas.append(
            f"- {clase['dia']} "
            f"{clase['hora_inicio']} - "
            f"{clase['hora_fin']}: "
            f"{clase['materia']}, "
            f"con {clase['profesor']}, "
            f"en el salón {clase['salon']}."
        )

    return "\n".join(lineas)

def construir_respuesta_materias(semestre):
    materias = obtener_materias_por_semestre(semestre)

    if not materias:
        return (
            "No encontré materias registradas "
            "para tu semestre."
        )

    lineas = [
        f"Tus materias de {semestre}.º semestre son:"
    ]

    for materia in materias:
        lineas.append(
            f"{materia['orden']}. {materia['nombre']}"
        )

    return "\n".join(lineas)

def construir_respuesta_profesores(
    semestre,
    materia_buscada=None,
):
    asignaciones = obtener_asignaciones_por_semestre(
        semestre
    )

    if not asignaciones:
        return (
            "No encontré profesores asignados "
            "para tu semestre."
        )

    if materia_buscada is not None:
        for asignacion in asignaciones:
            if asignacion["materia"] == materia_buscada:
                return (
                    f"La materia {asignacion['materia']} "
                    f"es impartida por "
                    f"{asignacion['profesor']} "
                    f"({asignacion['especialidad']}). "
                    f"Correo: {asignacion['correo']}."
                )

        return (
            f"No encontré un profesor asignado "
            f"para {materia_buscada}."
        )

    lineas = [
        "Estos son tus profesores:"
    ]

    for asignacion in asignaciones:
        lineas.append(
            f"- {asignacion['materia']}: "
            f"{asignacion['profesor']} "
            f"({asignacion['especialidad']}). "
            f"Correo: {asignacion['correo']}."
        )

    return "\n".join(lineas)

def construir_respuesta_calificaciones(
    matricula,
    materia_buscada=None,
):
    calificaciones = (
        obtener_calificaciones_por_estudiante(
            matricula
        )
    )

    if not calificaciones:
        return (
            "No encontré calificaciones registradas "
            "para este estudiante."
        )

    consulta_especifica = (
        materia_buscada is not None
    )

    if consulta_especifica:
        calificaciones = [
            calificacion
            for calificacion in calificaciones
            if calificacion["materia"]
            == materia_buscada
        ]

        if not calificaciones:
            return (
                f"No encontré calificaciones "
                f"registradas para "
                f"{materia_buscada}."
            )

        lineas = [
            f"Estas son tus calificaciones de "
            f"{materia_buscada}:"
        ]
    else:
        lineas = [
            "Estas son tus calificaciones:"
        ]

    for calificacion in calificaciones:
        lineas.append(
            f"- {calificacion['materia']}: "
            f"P1 {calificacion['parcial_1']:.1f}, "
            f"P2 {calificacion['parcial_2']:.1f}, "
            f"P3 {calificacion['parcial_3']:.1f}, "
            f"promedio "
            f"{calificacion['promedio']:.2f}."
        )

    if not consulta_especifica:
        promedio_general = round(
            sum(
                calificacion["promedio"]
                for calificacion in calificaciones
            ) / len(calificaciones),
            2,
        )

        lineas.append(
            f"Tu promedio general es "
            f"{promedio_general:.2f}."
        )

    return "\n".join(lineas)

def construir_respuesta_examenes(
    matricula,
    materia_buscada=None,
):
    examenes = obtener_examenes_por_estudiante(
        matricula
    )

    if not examenes:
        return (
            "No encontré exámenes registrados "
            "para este estudiante."
        )

    if materia_buscada is not None:
        examenes = [
            examen
            for examen in examenes
            if examen["materia"] == materia_buscada
        ]

        if not examenes:
            return (
                f"No encontré exámenes registrados "
                f"para {materia_buscada}."
            )

        lineas = [
            f"Estos son tus exámenes de "
            f"{materia_buscada}:"
        ]
    else:
        lineas = ["Estos son tus exámenes:"]

    for examen in examenes:
        fecha = date.fromisoformat(
            examen["fecha"]
        ).strftime("%d/%m/%Y")

        lineas.append(
            f"- Parcial {examen['parcial']} de "
            f"{examen['materia']}: "
            f"{fecha}, a las {examen['hora']}, "
            f"en el salón {examen['salon']}."
        )

    return "\n".join(lineas)

def construir_respuesta_avisos(matricula):
    avisos = obtener_avisos_por_estudiante(
        matricula
    )

    if not avisos:
        return (
            "No hay avisos escolares disponibles "
            "para este estudiante."
        )

    lineas = ["Estos son tus avisos escolares:"]

    for aviso in avisos:
        fecha = date.fromisoformat(
            aviso["fecha_evento"]
        ).strftime("%d/%m/%Y")

        if aviso["semestre"] is None:
            alcance = "aviso general"
        else:
            alcance = (
                f"aviso de {aviso['semestre']}.º semestre"
            )

        lineas.append(
            f"- {aviso['titulo']} ({fecha}, "
            f"{alcance}): {aviso['mensaje']}"
        )

    return "\n".join(lineas)

def procesar_consulta(pregunta, estudiante):
    respuesta, tipo, categoria, confianza = (
        buscar_respuesta(pregunta)
    )
    if categoria == "horario":
        materia_identificada = identificar_materia(
            pregunta
        )

        if (
            materia_identificada is not None
            and materia_identificada["semestre"]
            != estudiante["semestre"]
        ):
            respuesta = (
                f"La materia "
                f"{materia_identificada['nombre']} "
                f"pertenece al "
                f"{materia_identificada['semestre']}.º "
                f"semestre y no aparece entre tus "
                f"materias inscritas de "
                f"{estudiante['semestre']}.º semestre."
            )
        else:
            materia_buscada = None

            if materia_identificada is not None:
                materia_buscada = (
                    materia_identificada["nombre"]
                )

            respuesta = construir_respuesta_horario(
                estudiante["matricula"],
                materia_buscada,
            )

    elif categoria == "materia":
        respuesta = construir_respuesta_materias(
            estudiante["semestre"]
        )

    elif categoria == "profesor":
        materia_identificada = identificar_materia(
            pregunta
        )

        if (
            materia_identificada is not None
            and materia_identificada["semestre"]
            != estudiante["semestre"]
        ):
            respuesta = (
                f"La materia "
                f"{materia_identificada['nombre']} "
                f"pertenece al "
                f"{materia_identificada['semestre']}.º "
                f"semestre y no aparece entre tus "
                f"materias inscritas de "
                f"{estudiante['semestre']}.º semestre."
            )
        else:
            materia_buscada = None

            if materia_identificada is not None:
                materia_buscada = (
                    materia_identificada["nombre"]
                )

            respuesta = construir_respuesta_profesores(
                estudiante["semestre"],
                materia_buscada,
            )
            
    elif categoria == "calificacion":
        materia_identificada = identificar_materia(
            pregunta
        )

        if (
            materia_identificada is not None
            and materia_identificada["semestre"]
            != estudiante["semestre"]
        ):
            respuesta = (
                f"La materia "
                f"{materia_identificada['nombre']} "
                f"pertenece al "
                f"{materia_identificada['semestre']}.º "
                f"semestre y no aparece entre tus "
                f"materias inscritas de "
                f"{estudiante['semestre']}.º semestre."
            )
        else:
            materia_buscada = None

            if materia_identificada is not None:
                materia_buscada = (
                    materia_identificada["nombre"]
                )

            respuesta = (
                construir_respuesta_calificaciones(
                    estudiante["matricula"],
                    materia_buscada,
                )
            )

    elif categoria == "examen":
        materia_identificada = identificar_materia(
            pregunta
        )

        if (
            materia_identificada is not None
            and materia_identificada["semestre"]
            != estudiante["semestre"]
        ):
            respuesta = (
                f"La materia "
                f"{materia_identificada['nombre']} "
                f"pertenece al "
                f"{materia_identificada['semestre']}.º "
                f"semestre y no aparece entre tus "
                f"materias inscritas de "
                f"{estudiante['semestre']}.º semestre."
            )
        else:
            materia_buscada = None

            if materia_identificada is not None:
                materia_buscada = (
                    materia_identificada["nombre"]
                )

            respuesta = construir_respuesta_examenes(
                estudiante["matricula"],
                materia_buscada,
            )

    elif categoria == "aviso":
        respuesta = construir_respuesta_avisos(
            estudiante["matricula"]
        )

    elif categoria == "academica":
        (
            respuesta_academica,
            confianza_tema,
            tema_academico,
        ) = responder_consulta_academica(
            pregunta,
            estudiante["semestre"],
        )

        respuesta = respuesta_academica

        if tema_academico is not None:
            respuesta += (
                f"\nTema identificado: "
                f"{tema_academico}"
            )

        respuesta += (
            f"\nConfianza del tema académico: "
            f"{confianza_tema:.0%}"
        )

    historial_id = guardar_consulta_historial(
        estudiante["matricula"],
        pregunta,
        respuesta,
        tipo,
        categoria,
        confianza,
    )

    return (
        respuesta,
        tipo,
        categoria,
        confianza,
        historial_id,
    )
