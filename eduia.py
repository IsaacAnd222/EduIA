from datetime import date
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

    # Laboratorios
    ("dónde están los laboratorios", "laboratorio"),
    ("cuál es el horario de los laboratorios", "laboratorio"),
    ("cómo puedo utilizar un laboratorio", "laboratorio"),
    ("qué laboratorios tiene la universidad", "laboratorio"),
    ("necesito reservar el laboratorio", "laboratorio"),
    ("puedo entrar al lavotatorio", "laboratorio"),


    # Cafetería
    ("dónde está la cafetería", "cafeteria"),
    ("cuál es el horario de la cafetería", "cafeteria"),
    ("qué alimentos vende la cafetería", "cafeteria"),
    ("cuánto cuesta la comida en la cafetería", "cafeteria"),
    ("la cafetería está abierta", "cafeteria"),
    ("qué menú tienen hoy", "cafeteria"),
    ("abre la cafetería los sábados", "cafeteria"),
    ("a qué hora abre la cafeteira", "cafeteria"),
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

vectorizador = TfidfVectorizer(
    strip_accents="unicode",
    stop_words=PALABRAS_IGNORADAS,
)
matriz_preguntas = vectorizador.fit_transform(preguntas_conocidas)

def buscar_respuesta(pregunta_usuario):
    vector_pregunta = vectorizador.transform([pregunta_usuario])

    similitudes = cosine_similarity(
        vector_pregunta,
        matriz_preguntas,
    )[0]

    indice_mejor_resultado = similitudes.argmax()
    confianza = float(similitudes[indice_mejor_resultado])
    confianza = max(0.0, min(1.0, confianza))

    if confianza < UMBRAL_CONFIANZA:
        categoria = "desconocida"
    else:
        categoria = categorias_conocidas[indice_mejor_resultado]

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