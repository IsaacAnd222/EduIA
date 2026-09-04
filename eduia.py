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
    ("cuál es el proceso de nuevo ingreso", "inscripcion"),
    ("qué documentos necesito para nuevo ingreso", "inscripcion"),
    ("cuándo inicia el proceso de nuevo ingreso", "inscripcion"),
    ("dónde solicito mi ficha de ingreso", "inscripcion"),
    ("cómo ingreso al instituto irapuato", "inscripcion"),

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
    ("qué tipos de becas y apoyos financieros existen", "beca"),
    ("cuáles son los requisitos de la beca académica", "beca"),
    ("cómo solicito una beca deportiva", "beca"),
    ("qué necesito para una beca cultural", "beca"),
    ("cómo funciona el apoyo financiero familiar", "beca"),
    ("qué es el apoyo financiero de convenio", "beca"),
    ("cómo conservo o renuevo mi beca", "beca"),
    ("qué condiciones debo cumplir para mantener el apoyo", "beca"),
    ("dónde consulto los resultados de becas", "beca"),

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
    ("cuáles son las modalidades de titulación", "titulacion"),
    ("puedo titularme por excelencia académica", "titulacion"),
    ("qué necesito para titularme por tesis", "titulacion"),
    ("puedo titularme por informe de servicio social", "titulacion"),
    ("qué requiere el informe de experiencia profesional", "titulacion"),
    ("puedo titularme mediante estudios de posgrado", "titulacion"),
    ("qué puntaje necesito en el ceneval", "titulacion"),
    ("cómo funciona el curso de actualización profesional", "titulacion"),
    ("cuánto cuesta la titulación", "titulacion"),
    ("cuánto tarda la entrega del título", "titulacion"),
    ("cómo tramito mi cédula profesional", "titulacion"),
    ("dónde contacto al área de titulaciones", "titulacion"),

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


def construir_respuesta_biblioteca(pregunta):
    """Construye respuestas específicas sobre la biblioteca."""
    texto = normalizar_texto(pregunta)

    if any(
        palabra in texto
        for palabra in (
            "ubicacion",
            "donde esta",
            "donde queda",
            "donde se encuentra",
            "edificio",
            "localizar",
        )
    ):
        return (
            "El Instituto Irapuato cuenta con dos espacios de biblioteca:\n"
            "- Universidad: edificio A, planta baja.\n"
            "- Preparatoria: edificio G, planta baja."
        )

    if any(
        palabra in texto
        for palabra in (
            "horario",
            "hora",
            "abre",
            "abren",
            "cierra",
            "cierran",
            "sabado",
        )
    ):
        return (
            "Horario de Biblioteca:\n"
            "- Lunes a viernes: 9:00 a. m. a 5:00 p. m.\n"
            "- Sábados: 9:00 a. m. a 2:30 p. m."
        )

    if any(
        frase in texto
        for frase in (
            "cuantos libros",
            "cantidad de libros",
            "maximo de libros",
            "limite de libros",
        )
    ):
        return (
            "No tengo registrado el número máximo de libros que puede "
            "solicitar cada estudiante. Confirma este límite directamente "
            "en Biblioteca presentando tu credencial universitaria."
        )

    if any(
        palabra in texto
        for palabra in (
            "devolver tarde",
            "entrega tardia",
            "entregar tarde",
            "multa",
            "multas",
            "atraso",
            "atrasado",
            "retraso",
            "tarde un libro",
            "vencido",
            "penalizacion",
            "sancion",
        )
    ):
        return (
            "Como regla de referencia de EduIA, un material vencido debe "
            "devolverse antes de solicitar nuevos préstamos y el servicio "
            "puede suspenderse temporalmente mientras exista el retraso. "
            "No tengo registrada una multa económica oficial; confirma las "
            "consecuencias vigentes directamente en Biblioteca."
        )

    if any(
        palabra in texto
        for palabra in (
            "renovar",
            "renovacion",
            "duracion",
            "cuanto dura",
            "cuantos dias",
            "cuantas semanas",
            "devolver",
            "devolucion",
            "vence",
        )
    ):
        return (
            "El préstamo de libros tiene una duración de dos semanas. "
            "Si necesitas conservar el material por más tiempo, solicita "
            "la renovación en Biblioteca antes de la fecha de vencimiento; "
            "su autorización depende de la disponibilidad del ejemplar."
        )

    if any(
        palabra in texto
        for palabra in (
            "regla",
            "reglas",
            "permitido",
            "prohibido",
            "comer",
            "bebida",
            "gritar",
            "correr",
            "silencio",
        )
    ):
        return (
            "Reglas principales de Biblioteca:\n"
            "- Mantén un tono de voz bajo y respeta las zonas de estudio.\n"
            "- No corras, grites, comas ni introduzcas bebidas abiertas.\n"
            "- Cuida los libros, computadoras, mesas y demás instalaciones.\n"
            "- Devuelve los materiales dentro del plazo establecido.\n"
            "- Utiliza Internet y los equipos con fines académicos.\n"
            "- Sigue las indicaciones del personal responsable."
        )

    if any(
        palabra in texto
        for palabra in (
            "contacto",
            "correo",
            "telefono",
            "responsable",
            "comunicarme",
            "llamar",
        )
    ):
        return (
            "Puedes comunicarte con Biblioteca al teléfono "
            "(462) 623 5969 o al correo biblioteca@correo.edu.mx."
        )

    if any(
        palabra in texto
        for palabra in (
            "computadora",
            "computadoras",
            "internet",
            "wifi",
            "mesa",
            "mesas",
            "silla",
            "sillas",
            "sillon",
            "sillones",
            "estudiar",
            "estudio",
            "espacio",
            "espacios",
            "servicio",
            "servicios",
        )
    ):
        return (
            "La Biblioteca ofrece préstamo de libros, Internet Wi-Fi, "
            "computadoras y zonas de estudio. Cuenta con varias mesas y "
            "sillas, además de algunos sillones para lectura y trabajo "
            "académico."
        )

    if any(
        palabra in texto
        for palabra in (
            "credencial",
            "requisito",
            "requisitos",
            "solicitar",
            "sacar",
            "pedir",
            "prestar",
            "prestado",
            "llevarme",
        )
    ):
        return (
            "Para solicitar un libro en préstamo debes presentar tu "
            "credencial vigente de la Universidad. El préstamo tiene una "
            "duración de dos semanas y está sujeto a la disponibilidad "
            "del ejemplar."
        )

    return (
        "La Biblioteca del Instituto Irapuato ofrece préstamo de libros, "
        "Internet Wi-Fi, computadoras y espacios de estudio. Para solicitar "
        "material presenta tu credencial universitaria; el préstamo dura "
        "dos semanas. Puedes indicar si deseas consultar ubicación, horario, "
        "requisitos, renovación, servicios, reglas o contacto."
    )


def construir_respuesta_cafeteria(pregunta):
    """Construye respuestas específicas sobre las cafeterías."""
    texto = normalizar_texto(pregunta)

    if any(
        frase in texto
        for frase in (
            "ubicacion",
            "donde esta",
            "donde queda",
            "donde se encuentra",
            "como llego",
        )
    ):
        return (
            "El Instituto Irapuato cuenta con tres áreas de cafetería:\n"
            "- Una en el área de Preparatoria.\n"
            "- Una en la entrada del área de Universidad.\n"
            "- Una en la parte posterior izquierda del área de Universidad."
        )

    if any(
        palabra in texto
        for palabra in (
            "horario",
            "hora",
            "abre",
            "abren",
            "cierra",
            "cierran",
            "sabado",
        )
    ):
        return (
            "Horario de las cafeterías:\n"
            "- Lunes a viernes: 9:00 a. m. a 5:00 p. m.\n"
            "- Sábados: 9:00 a. m. a 2:00 p. m.\n"
            "El servicio se mantiene disponible durante ese horario, "
            "incluidos los recesos y las horas libres."
        )

    palabras_precio = (
        "precio",
        "precios",
        "cuanto cuesta",
        "cuanto cuestan",
        "costo",
        "costos",
        "vale",
    )

    if any(palabra in texto for palabra in palabras_precio):
        if "torta con queso" in texto:
            detalle = "La torta con queso cuesta aproximadamente $25."
        elif "torta" in texto:
            detalle = "La torta cuesta aproximadamente $20."
        elif "quesadilla" in texto:
            detalle = (
                "La quesadilla cuesta desde $20; el precio depende del guiso."
            )
        elif "taco" in texto:
            detalle = "Cada taco cuesta aproximadamente $15."
        elif "refresco" in texto:
            detalle = "El refresco cuesta aproximadamente $25."
        elif "sabritas" in texto:
            detalle = "Las Sabritas cuestan aproximadamente $20."
        elif "energetica" in texto:
            detalle = "La bebida energética cuesta aproximadamente $40."
        else:
            detalle = (
                "Precios aproximados:\n"
                "- Refresco: $25.\n"
                "- Sabritas: $20.\n"
                "- Taco: $15 cada uno.\n"
                "- Torta: $20.\n"
                "- Torta con queso: $25.\n"
                "- Quesadilla: desde $20; depende del guiso.\n"
                "- Bebida energética: $40."
            )

        return (
            f"{detalle}\n"
            "Los precios son aproximados y pueden cambiar. Consulta "
            "directamente en Cafetería los productos sin precio registrado."
        )

    if any(
        frase in texto
        for frase in (
            "metodo de pago",
            "metodos de pago",
            "forma de pago",
            "formas de pago",
            "pagar con",
            "aceptan tarjeta",
            "aceptan transferencia",
            "pago en efectivo",
        )
    ):
        return (
            "En las cafeterías puedes pagar en efectivo, mediante "
            "transferencia o con tarjeta de crédito o débito. Confirma "
            "la disponibilidad del medio de pago al momento de comprar."
        )

    if any(
        palabra in texto
        for palabra in (
            "alcohol",
            "alcoholica",
            "alcoholicas",
            "cerveza",
            "cigarro",
            "cigarros",
            "tabaco",
            "restriccion",
            "restricciones",
            "prohibido",
        )
    ):
        return (
            "Las cafeterías no venden bebidas alcohólicas, cigarros ni "
            "productos de tabaco. También se deben respetar las reglas de "
            "convivencia y limpieza de cada área."
        )

    if any(
        frase in texto
        for frase in (
            "durante el receso",
            "durante los recesos",
            "hora libre",
            "horas libres",
            "todo el tiempo",
            "todo momento",
            "siempre hay servicio",
        )
    ):
        return (
            "Las cafeterías brindan servicio continuo dentro de su horario, "
            "incluidos los recesos y las horas libres: de lunes a viernes de "
            "9:00 a. m. a 5:00 p. m. y los sábados de 9:00 a. m. a 2:00 p. m."
        )

    if any(
        palabra in texto
        for palabra in (
            "responsable",
            "contacto",
            "correo",
            "telefono",
            "queja",
            "sugerencia",
            "preguntar",
            "pregunto",
            "con quien",
        )
    ):
        return (
            "Para consultar el menú, los precios, la disponibilidad o dejar "
            "una sugerencia, dirígete directamente al personal de cualquiera "
            "de las tres cafeterías del Instituto Irapuato. No tengo "
            "registrado un teléfono o correo específico."
        )

    palabras_menu = (
        "menu",
        "venden",
        "venta",
        "comer",
        "comida",
        "alimento",
        "alimentos",
        "bebida",
        "bebidas",
        "refresco",
        "refrescos",
        "sabritas",
        "agua",
        "aguas",
        "energetica",
        "energeticas",
        "galleta",
        "galletas",
        "arroz",
        "burrito",
        "burritos",
        "sandwich",
        "sandwiches",
        "hamburguesa",
        "hamburguesas",
        "papas",
        "pizza",
        "taco",
        "tacos",
        "torta",
        "tortas",
        "quesadilla",
        "quesadillas",
    )

    if any(palabra in texto for palabra in palabras_menu):
        return (
            "En las cafeterías puedes encontrar refrescos, agua, bebidas "
            "energéticas, Sabritas y galletas. También ofrecen alimentos "
            "como arroz, burritos, sándwiches, hamburguesas, papas a la "
            "francesa, pizza, tacos, tortas y quesadillas. La disponibilidad "
            "puede variar durante el día."
        )

    return (
        "El Instituto Irapuato cuenta con tres cafeterías que ofrecen "
        "alimentos, botanas y bebidas. Atienden de lunes a viernes de "
        "9:00 a. m. a 5:00 p. m. y los sábados de 9:00 a. m. a 2:00 p. m. "
        "Puedes preguntar por ubicación, menú, precios, formas de pago, "
        "horarios o restricciones."
    )


def construir_respuesta_laboratorio(pregunta):
    """Construye respuestas específicas sobre los laboratorios."""
    texto = normalizar_texto(pregunta)

    if any(
        frase in texto
        for frase in (
            "ubicacion",
            "donde esta",
            "donde queda",
            "donde se encuentra",
            "como llego",
        )
    ):
        return (
            "El Instituto Irapuato cuenta con laboratorios en:\n"
            "- Universidad: edificio D, segunda planta.\n"
            "- Preparatoria: edificio G, segunda planta."
        )

    if any(
        palabra in texto
        for palabra in (
            "horario",
            "hora",
            "abre",
            "abren",
            "cierra",
            "cierran",
            "sabado",
        )
    ):
        return (
            "Horario de los laboratorios:\n"
            "- Lunes a viernes: 7:00 a. m. a 5:00 p. m.\n"
            "- Sábados: 7:00 a. m. a 2:00 p. m.\n"
            "El acceso depende de la disponibilidad y autorización del "
            "responsable o docente."
        )

    if any(
        palabra in texto
        for palabra in (
            "reservar",
            "reservacion",
            "apartar",
            "agendar",
            "solicitar uso",
        )
    ):
        return (
            "Para reservar un laboratorio, solicita previamente la "
            "autorización del encargado o del asesor de tu grupo. Si el "
            "laboratorio se utilizará durante una clase, el profesor debe "
            "apartarlo con anticipación. La reservación depende del horario "
            "y la disponibilidad del espacio."
        )

    if any(
        palabra in texto
        for palabra in (
            "entrar",
            "ingresar",
            "acceso",
            "requisito",
            "requisitos",
            "vestimenta",
            "bata",
            "calzado",
            "cabello",
            "gafas",
            "guantes",
            "mascarilla",
            "sandalia",
            "sandalias",
            "proteccion",
        )
    ):
        return (
            "Para ingresar al laboratorio necesitas autorización del "
            "encargado, asesor o profesor responsable. Durante las prácticas:\n"
            "- Usa bata limpia, de manga larga y abotonada.\n"
            "- Lleva calzado completamente cerrado.\n"
            "- Mantén recogido el cabello largo.\n"
            "- Utiliza gafas, guantes y mascarilla cuando la práctica lo "
            "requiera.\n"
            "- Evita accesorios o prendas sueltas."
        )

    if any(
        palabra in texto
        for palabra in (
            "regla",
            "reglas",
            "seguridad",
            "conducta",
            "prohibido",
            "comer",
            "beber",
            "pipetear",
            "limpieza",
            "correr",
            "mochila",
            "mochilas",
        )
    ):
        return (
            "Reglas principales de seguridad en los laboratorios:\n"
            "- No comas, bebas, fumes, almacenes alimentos ni uses "
            "cosméticos.\n"
            "- Nunca pipetees con la boca; utiliza instrumentos mecánicos.\n"
            "- Mantén limpia y ordenada el área de trabajo.\n"
            "- No coloques mochilas, libros u objetos personales sobre las "
            "mesas de práctica.\n"
            "- Evita bromas, carreras y cualquier distractor.\n"
            "- Usa el equipo de protección indicado y sigue las instrucciones "
            "del responsable."
        )

    if any(
        frase in texto
        for frase in (
            "tipo de laboratorio",
            "tipos de laboratorio",
            "que laboratorios",
            "cuales laboratorios",
        )
    ):
        return (
            "No tengo registrado un inventario oficial de los tipos de "
            "laboratorio disponibles. El espacio se asigna de acuerdo con la "
            "materia y la práctica; confirma con tu profesor, asesor o con el "
            "encargado cuál corresponde y si está disponible."
        )

    if any(
        palabra in texto
        for palabra in (
            "equipo",
            "equipos",
            "instrumento",
            "instrumentos",
            "herramienta",
            "herramientas",
            "computadora",
            "computadoras",
            "servicio",
            "servicios",
            "practica",
            "practicas",
        )
    ):
        return (
            "Los laboratorios se utilizan para prácticas académicas "
            "supervisadas. De forma general pueden contar con mesas de "
            "trabajo, computadoras, instrumentos de medición, herramientas "
            "y materiales acordes con cada asignatura. El equipo disponible "
            "y las condiciones de uso deben confirmarse con el encargado "
            "antes de la práctica."
        )

    if any(
        palabra in texto
        for palabra in (
            "responsable",
            "encargado",
            "autoriza",
            "autorizar",
            "contacto",
            "correo",
            "telefono",
            "comunicarme",
        )
    ):
        return (
            "Para este prototipo, el responsable simulado es el Ing. Adrián "
            "Morales Vega, encargado general de laboratorios. Contacto "
            "simulado: laboratorios@eduia.edu.mx y (462) 623 5969 ext. 245.\n"
            "Estos datos no son oficiales; para una solicitud real consulta "
            "a tu asesor, profesor o al personal del laboratorio."
        )

    return (
        "Los laboratorios del Instituto Irapuato se utilizan durante clases "
        "y prácticas académicas. Para ingresar o reservarlos necesitas la "
        "autorización del encargado, asesor o profesor responsable. Puedes "
        "preguntar por ubicación, horario, reservación, requisitos de "
        "ingreso, seguridad, equipos o contacto."
    )


def construir_respuesta_inscripcion(pregunta):
    """Construye una respuesta específica sobre inscripción."""
    texto = normalizar_texto(pregunta)

    indicadores_reinscripcion = (
        "reinscri",
        "siguiente semestre",
        "proximo semestre",
        "proximo periodo",
        "registrar mis materias",
        "registrar el semestre",
        "registro semestral",
        "renovar mi carga",
        "renovar mi inscripcion",
        "primera colegiatura",
    )

    indicadores_nuevo_ingreso = (
        "nuevo ingreso",
        "aspirante",
        "admision",
        "ficha",
        "examen de admision",
        "ficha de ingreso",
        "solicitar mi ficha",
        "solicitar una ficha",
        "ingresar al instituto",
        "entrar al instituto",
        "primera vez",
    )

    es_reinscripcion = any(
        indicador in texto
        for indicador in indicadores_reinscripcion
    )
    es_nuevo_ingreso = any(
        indicador in texto
        for indicador in indicadores_nuevo_ingreso
    )

    if es_reinscripcion and not es_nuevo_ingreso:
        return (
            "Si ya eres estudiante del Instituto Irapuato, para "
            "reinscribirte solo debes pagar la primera colegiatura "
            "del nuevo semestre antes de la fecha límite indicada.\n"
            "Conserva tu comprobante de pago. No necesitas repetir "
            "el proceso de ficha, examen de admisión ni entrega de "
            "documentos de nuevo ingreso.\n"
            "La fecha exacta debe confirmarse en Servicios Escolares, "
            "ubicado en el edificio central."
        )

    if not es_nuevo_ingreso:
        return (
            "Para darte la información correcta, ¿te refieres al "
            "proceso de nuevo ingreso al Instituto Irapuato o a la "
            "reinscripción de un estudiante que ya está matriculado?"
        )

    palabras_documentos = (
        "documento",
        "documentos",
        "papel",
        "papeles",
        "requisito",
        "requisitos",
        "necesito",
    )

    if any(palabra in texto for palabra in palabras_documentos):
        return (
            "Para la inscripción de nuevo ingreso necesitas:\n"
            "- Recibo de pago o ficha de depósito.\n"
            "- Acta de nacimiento digital con código QR.\n"
            "- CURP digital vigente.\n"
            "- INE vigente, por ambos lados, del responsable de los pagos.\n"
            "- Certificado de preparatoria.\n"
            "Si el certificado es físico, entrega el original y una "
            "copia legalizada en Servicios Escolares. Adjunta los PDF "
            "digitales originales; no fotografías convertidas a PDF."
        )

    palabras_fechas = (
        "cuando",
        "fecha",
        "fechas",
        "periodo",
        "limite",
    )

    if any(palabra in texto for palabra in palabras_fechas):
        return (
            "Calendario de referencia para nuevo ingreso:\n"
            "- Ciclo 2026: solicitud de ficha desde el 1 de abril y "
            "entrega de documentos hasta el 5 de agosto de 2026.\n"
            "- Ciclo 2027: solicitud de ficha desde el 1 de abril y "
            "entrega de documentos hasta el 5 de agosto de 2027.\n"
            "Estas fechas son aproximadas para EduIA. Confirma la "
            "convocatoria vigente con Servicios Escolares."
        )

    palabras_contacto = (
        "donde",
        "ubicacion",
        "ubicado",
        "lugar",
        "horario",
        "contacto",
        "correo",
        "telefono",
        "whatsapp",
        "servicios escolares",
        "edificio central",
    )

    if any(palabra in texto for palabra in palabras_contacto):
        return (
            "Puedes recibir atención en Servicios Escolares, en el "
            "edificio central del Instituto Irapuato: Prolongación "
            "Mariano J. García 355, colonia San Miguelito, Irapuato, "
            "Guanajuato.\n"
            "Horario: lunes a viernes de 9:00 a. m. a 5:00 p. m. y "
            "sábados de 9:00 a. m. a 12:00 p. m.\n"
            "También puedes solicitar la ficha de nuevo ingreso en "
            "www.uii.edu.mx/ficha.\n"
            "Contacto general y de nuevo ingreso: "
            "informes@marketing.uii.edu.mx, conmutador (462) 623 5969, "
            "WhatsApp 462 188 2396 y 462 188 3869."
        )

    return (
        "Proceso de nuevo ingreso al Instituto Irapuato:\n"
        "1. Solicita tu ficha en las instalaciones o en "
        "www.uii.edu.mx/ficha.\n"
        "2. Recíbela por correo, normalmente dentro de 48 horas.\n"
        "3. Presenta en línea el examen de admisión.\n"
        "4. Consulta el resultado en www.uii.edu.mx/resultados.\n"
        "5. Si elegiste modalidad escolarizada, asiste a la entrevista "
        "indicada por Dirección Académica.\n"
        "6. Realiza el pago y completa el formulario en "
        "https://uii.edu.mx/inscripcion.\n"
        "7. Adjunta tus documentos y espera la confirmación de "
        "Servicios Escolares.\n"
        "Después recibirás información sobre el curso de inducción y "
        "el inicio de clases."
    )


def construir_respuesta_beca(pregunta):
    """Construye una respuesta específica sobre becas y apoyos."""
    texto = normalizar_texto(pregunta)

    if any(
        frase in texto
        for frase in (
            "que es una beca",
            "que son las becas",
            "que es un apoyo financiero",
            "que son los apoyos financieros",
            "diferencia entre beca",
        )
    ):
        return (
            "En el Instituto Irapuato, una beca y un apoyo financiero "
            "consisten en la exención de un porcentaje de las cuotas "
            "escolares para alumnos activos. El porcentaje lo determina "
            "el Comité de Becas y Apoyos Financieros conforme a la "
            "convocatoria y al reglamento.\n"
            "Quienes reciben determinados apoyos financieros pueden "
            "tener que prestar servicio institucional en áreas académicas, "
            "administrativas, culturales o deportivas."
        )

    if any(
        palabra in texto
        for palabra in (
            "contacto",
            "responsable",
            "correo",
            "telefono",
            "whatsapp",
            "donde pregunto",
            "donde solicito",
            "a quien",
            "con quien",
        )
    ):
        return (
            "El Departamento de Vinculación y Apoyos Financieros "
            "orienta y da seguimiento a las solicitudes.\n"
            "- Felipe Santellano, auxiliar administrativo: "
            "(462) 623 5969 ext. 232, WhatsApp (462) 188 5024, "
            "felipesantellano@vinculacion.uii.edu.mx.\n"
            "- Vanessa Ruiz, directora del departamento: "
            "(462) 623 5969 ext. 237, "
            "vanessaruiz@vinculacion.uii.edu.mx."
        )

    if any(
        frase in texto
        for frase in (
            "que becas",
            "cuales becas",
            "tipos de beca",
            "tipos de apoyo",
            "becas disponibles",
            "apoyos disponibles",
            "que apoyos",
        )
    ) and "nuevo ingreso" not in texto:
        return (
            "El Instituto Irapuato contempla estas becas y apoyos:\n"
            "- Apoyos para nuevo ingreso.\n"
            "- Apoyo financiero de convenio.\n"
            "- Apoyo financiero familiar.\n"
            "- Beca académica.\n"
            "- Beca deportiva.\n"
            "- Beca cultural.\n"
            "Los beneficios no son acumulables y el porcentaje final "
            "depende de la convocatoria y del Comité de Becas y "
            "Apoyos Financieros."
        )

    if "convenio" in texto:
        return (
            "El apoyo financiero de convenio está dirigido al personal "
            "y a familiares directos de empresas o instituciones que "
            "mantengan un convenio vigente con el Instituto Irapuato.\n"
            "Para nuevo ingreso en julio-diciembre de 2026, el registro "
            "fue del 1 de junio al 11 de julio de 2026 y se solicitó "
            "promedio mínimo de 8.0. El primer pago se cubre al 100 %.\n"
            "Para conservarlo se requiere promedio de 8.5, no reprobar "
            "materias y mantener continuidad escolar. El porcentaje "
            "depende del convenio y no es acumulable con otro beneficio."
        )

    if "familiar" in texto or "familia" in texto:
        return (
            "El apoyo financiero familiar beneficia a familiares directos "
            "cuando ya existe un alumno activo en el Instituto Irapuato.\n"
            "Otorga 25 % al segundo integrante inscrito y puede aplicarse "
            "hasta a dos familiares beneficiarios. El alumno previamente "
            "inscrito no recibe este beneficio.\n"
            "Para julio-diciembre de 2026, las solicitudes se recibieron "
            "del 1 de junio al 11 de julio. El primer pago se cubre al "
            "100 % y el beneficio depende de que el familiar de referencia "
            "continúe activo. No es acumulable con otros apoyos."
        )

    if "cultural" in texto or "artist" in texto or "talento" in texto:
        return (
            "La beca cultural para alumnos activos reconoce habilidades "
            "artísticas o culturales. Para la convocatoria "
            "julio-diciembre de 2026 se solicitó:\n"
            "- Promedio mínimo de 8.5 y no tener adeudos.\n"
            "- Solicitud en línea del 8 al 13 de junio de 2026.\n"
            "- Justificación, comprobantes de domicilio e ingresos, INE "
            "del responsable, fotografía personal y fotos del domicilio.\n"
            "- Video corto demostrando el talento, enviado a "
            "becasalumno@vinculacion.uii.edu.mx.\n"
            "También se indicó registrarse en un taller cultural del 3 al "
            "7 de agosto. La renovación exige promedio mínimo de 8 y no "
            "reprobar materias."
        )

    if "deport" in texto or any(
        deporte in texto
        for deporte in (
            "futbol",
            "basquetbol",
            "voleibol",
            "taekwondo",
            "porra",
        )
    ):
        return (
            "La beca deportiva para alumnos activos apoya a quienes "
            "representan al Instituto Irapuato. Para la convocatoria "
            "julio-diciembre de 2026 se solicitó promedio mínimo de 8.5, "
            "no tener adeudos y enviar la solicitud del 8 al 13 de junio.\n"
            "Las disciplinas admitidas fueron futbol, basquetbol, voleibol, "
            "taekwondo y porra. Las pruebas físicas se programaron para el "
            "16 de junio de 2026 a las 14:00 horas.\n"
            "La renovación exige promedio mínimo de 8 y no reprobar "
            "materias. Los resultados se programaron del 3 al 31 de "
            "agosto de 2026."
        )

    if "academica" in texto or "socioeconomico" in texto:
        return (
            "La beca académica para alumnos activos se solicita después "
            "de concluir el ciclo escolar. Para julio-diciembre de 2026 "
            "se requirió:\n"
            "- Promedio general mínimo de 8.5, sin materias reprobadas "
            "ni adeudos de colegiatura.\n"
            "- Solicitud en línea del 8 al 13 de junio de 2026.\n"
            "- Justificación, comprobante del estudio socioeconómico, "
            "comprobantes de domicilio e ingresos, INE del responsable, "
            "fotografía personal y fotos del domicilio.\n"
            "El estudio socioeconómico costó $250 y se pagó del 1 al 6 "
            "de junio. Los resultados se programaron del 1 al 31 de agosto."
        )

    es_egresado_uii = (
        "egresado" in texto
        or "prepa uii" in texto
        or "preparatoria uii" in texto
        or "30" in texto
    )

    if es_egresado_uii:
        return (
            "El apoyo de 30 % para egresados de preparatorias UII "
            "matutina y vespertina tuvo un límite de 20 beneficios para "
            "el ingreso julio-diciembre de 2026.\n"
            "El registro fue del 1 de junio al 11 de julio. Se debía "
            "completar el proceso de admisión y cubrir el primer pago al "
            "100 %. El retroactivo se aplicaría en el segundo pago.\n"
            "Para conservarlo durante la carrera se requiere promedio "
            "mínimo de 8.5, no reprobar y mantener ocho semestres "
            "continuos. No es acumulable."
        )

    es_apoyo_20 = (
        "20" in texto
        or "apoyo de nuevo ingreso" in texto
        or "apoyo nuevo ingreso" in texto
    )

    if es_apoyo_20:
        return (
            "El apoyo financiero de 20 % para nuevo ingreso contempló "
            "20 beneficios para licenciaturas escolarizadas en el periodo "
            "julio-diciembre de 2026.\n"
            "Se solicitó promedio mínimo de 8.5, completar la admisión, "
            "cubrir el primer pago al 100 % y enviar la solicitud del 1 de "
            "junio al 11 de julio de 2026. La comprobación del promedio "
            "debía entregarse antes del 3 de agosto.\n"
            "La renovación es automática con promedio de 8.5 y sin "
            "materias reprobadas. No es acumulable."
        )

    if "nuevo ingreso" in texto or "aspirante" in texto:
        return (
            "Para nuevo ingreso se contemplaron los apoyos de convenio, "
            "familiar, 20 % para nuevo ingreso y 30 % para egresados de "
            "preparatorias UII. Solo puede elegirse un beneficio.\n"
            "El aspirante debe solicitar ficha, aprobar el examen, realizar "
            "el primer pago al 100 % y entregar sus documentos antes de "
            "enviar la solicitud en línea. Para julio-diciembre de 2026, "
            "los registros fueron del 1 de junio al 11 de julio.\n"
            "Indica cuál apoyo deseas consultar para mostrarte sus "
            "requisitos particulares."
        )

    if any(
        palabra in texto
        for palabra in (
            "conservar",
            "conservo",
            "continuar",
            "mantener",
            "mantengo",
            "renovar",
            "renovacion",
            "renueva",
            "renuevo",
            "perder",
            "pierdo",
        )
    ):
        return (
            "Las condiciones de renovación dependen del beneficio:\n"
            "- Beca académica y apoyos de convenio o nuevo ingreso: "
            "promedio mínimo de 8.5.\n"
            "- Becas cultural y deportiva: promedio mínimo de 8.0.\n"
            "- No debes reprobar materias; una materia reprobada puede "
            "ocasionar la pérdida del beneficio.\n"
            "- El apoyo familiar continúa mientras el familiar de referencia "
            "permanezca activo.\n"
            "La renovación suele ser automática, pero debe verificarse con "
            "Vinculación y Apoyos Financieros."
        )

    if "resultado" in texto or "inconformidad" in texto or "queja" in texto:
        return (
            "Los resultados de las becas académica y cultural de 2026 se "
            "programaron del 1 al 31 de agosto; los de la beca deportiva, "
            "del 3 al 31 de agosto. El Comité de Becas determina el "
            "porcentaje otorgado.\n"
            "Para presentar una inconformidad escribe a "
            "becasalumno@vinculacion.uii.edu.mx e incluye nombre, carrera, "
            "semestre, modalidad y motivo. La respuesta estimada es de una "
            "semana."
        )

    if any(
        palabra in texto
        for palabra in (
            "documento",
            "documentos",
            "papel",
            "papeles",
            "requisito",
            "requisitos",
        )
    ):
        return (
            "Los documentos cambian según la beca o apoyo financiero. "
            "¿Deseas consultar los requisitos de la beca académica, "
            "cultural, deportiva, de convenio, familiar o de nuevo ingreso?"
        )

    es_pregunta_fecha = any(
        palabra in texto
        for palabra in (
            "cuando",
            "fecha",
            "fechas",
            "periodo",
            "limite",
        )
    )

    if (
        ("solicit" in texto or "inscrib" in texto)
        and not es_pregunta_fecha
    ):
        return (
            "Para solicitar una beca o apoyo financiero:\n"
            "1. Identifica el beneficio que corresponde a tu situación.\n"
            "2. Revisa promedio, restricciones y documentos de la "
            "convocatoria.\n"
            "3. Completa la solicitud en línea y adjunta los comprobantes.\n"
            "4. Envíala dentro del periodo establecido.\n"
            "Los aspirantes de nuevo ingreso deben completar la admisión, "
            "entregar documentos y cubrir el primer pago al 100 %. Los "
            "alumnos activos deben cumplir los requisitos particulares de "
            "la beca elegida. Indica cuál te interesa para darte los detalles."
        )

    if any(
        palabra in texto
        for palabra in (
            "cuando",
            "fecha",
            "fechas",
            "convocatoria",
            "registro",
            "solicitar",
            "solicitud",
            "inscrib",
        )
    ):
        return (
            "En la convocatoria julio-diciembre de 2026, los apoyos para "
            "nuevo ingreso se solicitaron del 1 de junio al 11 de julio. "
            "Las becas académica, cultural y deportiva para alumnos activos "
            "se solicitaron del 8 al 13 de junio. Estos periodos ya "
            "concluyeron.\n"
            "Consulta la siguiente convocatoria en el sitio del Instituto "
            "Irapuato o con Vinculación y Apoyos Financieros."
        )

    return (
        "Para orientarte correctamente, indica qué deseas consultar: "
        "tipos de becas, nuevo ingreso, beca académica, deportiva, cultural, "
        "apoyo de convenio, apoyo familiar, requisitos, fechas, resultados "
        "o renovación. Los beneficios no son acumulables y el porcentaje "
        "final lo determina el Comité de Becas y Apoyos Financieros."
    )


def construir_respuesta_titulacion(pregunta):
    """Construye respuestas específicas sobre titulación."""
    texto = normalizar_texto(pregunta)

    if any(
        frase in texto
        for frase in (
            "que es la titulacion",
            "que significa titularme",
            "en que consiste la titulacion",
        )
    ):
        return (
            "La titulación es el proceso mediante el cual un egresado "
            "cumple una modalidad académica y los requisitos administrativos "
            "para obtener su título profesional. La modalidad debe ser "
            "autorizada y el trámite se realiza con Servicios Escolares y "
            "el área de Titulaciones del Instituto Irapuato."
        )

    palabras_costo = (
        "costo",
        "costos",
        "cuesta",
        "precio",
        "pagar",
        "pago",
    )

    if any(palabra in texto for palabra in palabras_costo):
        if "curso" in texto and "extern" in texto:
            detalle = "Curso de actualización externo: $10,000."
        elif "curso" in texto:
            detalle = "Curso de actualización interno: $13,000."
        elif "posgrado" in texto or "maestria" in texto:
            detalle = "Estudios de Posgrado: $11,000."
        elif "tesis" in texto:
            detalle = "Tesis: $10,000."
        elif "excelencia" in texto:
            detalle = "Excelencia Académica: $10,000."
        elif "servicio social" in texto:
            detalle = "Informe de Servicio Social: $10,000."
        elif "experiencia profesional" in texto:
            detalle = "Informe de Experiencia Profesional: $10,000."
        elif "ceneval" in texto or "examen general" in texto:
            detalle = "CENEVAL: $10,000."
        else:
            detalle = (
                "Tesis, Excelencia Académica, Informe de Servicio Social, "
                "Informe de Experiencia Profesional y CENEVAL: $10,000 cada "
                "modalidad; Estudios de Posgrado: $11,000; Curso de "
                "actualización interno: $13,000; curso externo: $10,000."
            )

        return (
            f"Costo de referencia, con título incluido: {detalle} "
            "Confirma el importe vigente con Titulaciones y espera la "
            "autorización antes de efectuar el pago."
        )

    if "excelencia" in texto:
        return (
            "Para titularte por Excelencia Académica debes:\n"
            "- Haber concluido completamente el plan de estudios.\n"
            "- Tener promedio general mínimo de 9.5, sin redondeo.\n"
            "- Haber aprobado todas las materias en la primera oportunidad.\n"
            "- Ser alumno regular y no haber causado baja temporal.\n"
            "- Cumplir todos los requisitos administrativos.\n"
            "La autorización se solicita por escrito a la Comisión de "
            "Titulación mediante Servicios Escolares. Esta modalidad debe "
            "iniciarse dentro del primer año posterior al egreso."
        )

    if "tesis" in texto:
        return (
            "La tesis es un trabajo de investigación que puede iniciarse "
            "desde 7.º semestre y desarrollarse individualmente o en pareja.\n"
            "Debes concluir el plan de estudios, cumplir los requisitos "
            "administrativos y obtener la aprobación escrita del asesor y "
            "los sinodales. Después se presenta un examen recepcional.\n"
            "El anteproyecto tiene un plazo máximo de dos meses; una vez "
            "aprobado, el trabajo final debe concluirse en diez meses, con "
            "posibilidad de solicitar una prórroga de dos meses."
        )

    if "ceneval" in texto or "examen general de egreso" in texto:
        return (
            "Para titularte mediante el Examen General de Egreso de "
            "Licenciatura (CENEVAL) debes solicitar autorización escrita a "
            "Servicios Escolares antes de presentar el examen, haber "
            "concluido el plan de estudios y obtener al menos 1000 puntos "
            "en todas las áreas.\n"
            "El examen puede presentarse un máximo de tres veces y el "
            "resultado se comprueba con la constancia de CENEVAL. Esta opción "
            "no aplica para Relaciones Industriales, Psicología Educativa ni "
            "Relaciones Laborales y Recursos Humanos."
        )

    if (
        "servicio social" in texto
        or "informe social" in texto
        or "magis" in texto
    ):
        return (
            "La modalidad de Informe de Servicio Social documenta un proyecto "
            "relacionado con la carrera, realizado durante el servicio social. "
            "La opción MAGIS añade impacto social y valores institucionales.\n"
            "Puede iniciarse desde 7.º semestre, cuando el servicio social ya "
            "haya comenzado o terminado. El trabajo puede ser individual o en "
            "pareja y requiere aprobación del asesor y los sinodales, además "
            "de los requisitos administrativos y el examen recepcional."
        )

    if "experiencia profesional" in texto or "experiencia laboral" in texto:
        return (
            "El Informe de Experiencia Profesional documenta y analiza un "
            "proyecto o práctica laboral relacionada con la carrera.\n"
            "Puede iniciarse desde 7.º semestre, pero se requieren dos años "
            "de experiencia profesional comprobable antes de solicitar la "
            "modalidad. El trabajo puede ser individual o en pareja y debe "
            "ser aprobado por el asesor y los sinodales. También requiere "
            "cumplir los requisitos administrativos y presentar examen "
            "recepcional."
        )

    if any(
        frase in texto
        for frase in (
            "estudios de posgrado",
            "estudios de maestria",
            "por posgrado",
            "por maestria",
        )
    ):
        return (
            "Para titularte mediante Estudios de Posgrado debes solicitar "
            "autorización a Servicios Escolares antes de inscribirte al "
            "posgrado, haber concluido la licenciatura y aprobar al menos "
            "50 % de los créditos o materias de una maestría o doctorado con "
            "reconocimiento oficial.\n"
            "Si estudias en otra institución, debes presentar el certificado "
            "parcial; si estudias en el Instituto Irapuato, una constancia de "
            "calificaciones y del porcentaje cursado."
        )

    if any(
        frase in texto
        for frase in (
            "curso de actualizacion",
            "curso profesional",
            "vision global",
            "diplomado de titulacion",
        )
    ):
        return (
            "La modalidad de Curso de Actualización Profesional requiere "
            "haber concluido el plan de estudios, cumplir los requisitos "
            "administrativos y aprobar con mínimo 8.0. Los cursos internos "
            "deben cubrir entre 80 y 100 horas; los externos, 100 horas y "
            "autorización previa.\n"
            "Convocatoria 2026, Visión Global de Estrategias Empresariales: "
            "curso virtual del 3 de septiembre al 10 de diciembre, los jueves "
            "de 4:00 p. m. a 9:00 p. m.; costo de $13,000. Las solicitudes "
            "fueron del 23 al 27 de julio y el pago del 11 al 15 de agosto, "
            "por lo que esos periodos ya concluyeron."
        )

    if any(
        frase in texto
        for frase in (
            "modalidades de titulacion",
            "opciones de titulacion",
            "formas de titularme",
            "formas de obtener mi titulo",
            "como puedo titularme",
            "modalidad puedo elegir",
        )
    ):
        return (
            "Las modalidades de titulación para licenciatura e ingeniería "
            "son:\n"
            "1. Excelencia Académica.\n"
            "2. Tesis.\n"
            "3. Informe de Servicio Social, normal o MAGIS.\n"
            "4. Informe de Experiencia Profesional.\n"
            "5. Estudios de Posgrado.\n"
            "6. Curso de Actualización Profesional.\n"
            "7. Examen General de Egreso de Licenciatura (CENEVAL).\n"
            "La modalidad debe ser autorizada conforme a tu carrera y "
            "situación académica."
        )

    if any(
        palabra in texto
        for palabra in (
            "documento",
            "documentos",
            "papel",
            "papeles",
            "requisito",
            "requisitos",
            "fotografia",
            "fotografias",
        )
    ):
        return (
            "Requisitos administrativos generales para titulación:\n"
            "- Certificado total de estudios original.\n"
            "- Servicio social liberado.\n"
            "- Créditos culturales y deportivos liberados en modalidad "
            "escolarizada.\n"
            "- No tener adeudos en Finanzas ni Biblioteca.\n"
            "- Comprobante de pago de la modalidad.\n"
            "- Acta de nacimiento y certificado de preparatoria cuando el "
            "programa esté incorporado a SEG.\n"
            "- Nueve fotografías tamaño título, blanco y negro, papel mate "
            "autoadherible, fondo gris claro, ropa formal, sin lentes y sin "
            "alteraciones digitales.\n"
            "Algunas carreras y modalidades solicitan documentos adicionales."
        )

    if any(
        frase in texto
        for frase in (
            "cuanto tiempo tengo",
            "plazo para titularme",
            "fecha limite para titularme",
            "cuando debo titularme",
            "prorroga",
        )
    ):
        return (
            "Después de aprobar todas las materias tienes un máximo de dos "
            "años para iniciar la titulación. Para Excelencia Académica el "
            "límite es un año.\n"
            "Antes de vencer los primeros dos años puede solicitarse ante "
            "Rectoría una prórroga excepcional de hasta dos años. Si se "
            "excede el plazo sin prórroga, la modalidad disponible será "
            "Estudios de Posgrado."
        )

    if any(
        frase in texto
        for frase in (
            "cuanto tarda",
            "tiempo de entrega",
            "cuando entregan",
            "entrega del titulo",
        )
    ):
        return (
            "Para expedir el título debes contar con el certificado total de "
            "estudios registrado por SEP o SEG y haber pagado la modalidad. "
            "Los documentos proporcionados señalan un tiempo estimado de "
            "entrega de 10 meses después de iniciar la validación y "
            "legalización; para CENEVAL se indica un estimado de 4 meses. "
            "Confirma el plazo actual con Titulaciones."
        )

    if "cedula" in texto:
        return (
            "La cédula profesional es un trámite posterior que el egresado "
            "debe realizar personalmente ante la Dirección General de "
            "Profesiones o las instancias de Servicios Escolares e "
            "Incorporaciones correspondientes. La titulación del Instituto "
            "no sustituye este trámite. Solicita requisitos y costos vigentes "
            "al área de Titulaciones."
        )

    if any(
        frase in texto
        for frase in (
            "donde inicio",
            "donde registro",
            "donde entrego",
            "area de titulacion",
            "area de titulaciones",
            "contacto de titulacion",
            "contactar titulaciones",
            "correo de titulacion",
            "telefono de titulacion",
            "con quien",
        )
    ):
        return (
            "El trámite se inicia con Servicios Escolares y el área de "
            "Titulaciones del Instituto Irapuato.\n"
            "Solicitud en línea: "
            "https://uii.edu.mx/se/tramite/titulo/licenciaturas/.\n"
            "Contacto: titulaciones@serviciosescolares.uii.edu.mx, "
            "teléfono (462) 623 5969 ext. 236 y celular 462 188 0618.\n"
            "Espera el correo de autorización antes de efectuar cualquier pago."
        )

    if any(
        palabra in texto
        for palabra in (
            "procedimiento",
            "proceso",
            "pasos",
            "tramite",
        )
    ):
        return (
            "Proceso general de titulación:\n"
            "1. Consulta la modalidad con tu coordinación académica.\n"
            "2. Solicita la revisión y autorización de Servicios Escolares.\n"
            "3. Cumple los requisitos académicos y administrativos.\n"
            "4. Realiza el pago autorizado.\n"
            "5. Completa y acredita la modalidad elegida.\n"
            "6. Entrega comprobantes, documentos y nueve fotografías.\n"
            "7. Espera la liberación y expedición del título.\n"
            "Las modalidades escritas incluyen asesor, anteproyecto, revisión "
            "de sinodales y examen recepcional."
        )

    return (
        "Puedo informarte sobre modalidades, requisitos, documentos, costos, "
        "plazos, procedimiento, curso de actualización 2026, entrega del "
        "título, cédula profesional y contacto del área de Titulaciones. "
        "Indica qué aspecto deseas consultar."
    )

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
    "cocumemto": "documento",
    "cocumemtos": "documentos",
    "cocumento": "documento",
    "cocumentos": "documentos",
    "evaluasion": "evaluacion",
    "evaluasiones": "evaluaciones",
    "exelencia": "excelencia",
    "exelensia": "excelencia",
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
    "requicito": "requisito",
    "requicitos": "requisitos",
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

    # Cuando se menciona explícitamente una beca o un apoyo financiero,
    # esa intención debe prevalecer sobre términos como inscripción,
    # registro o nuevo ingreso.
    if (
        palabras & {"beca", "becas"}
        or "apoyo financiero" in texto_normalizado
        or "apoyos financieros" in texto_normalizado
    ):
        return "beca"

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
            "bata",
            "cabello",
            "gafas",
            "guantes",
            "mascarilla",
            "mochila",
            "mochilas",
            "pipetear",
            "sandalia",
            "sandalias",
            "seguridad",
        },
        "cafeteria": {
            "cafeteria",
            "cafeteira",
            "almuerzo",
            "almuerzos",
            "arroz",
            "burrito",
            "burritos",
            "desayuno",
            "desayunos",
            "bebida",
            "bebidas",
            "energetica",
            "energeticas",
            "galleta",
            "galletas",
            "hamburguesa",
            "hamburguesas",
            "menu",
            "comida",
            "alimentos",
            "pizza",
            "quesadilla",
            "quesadillas",
            "refresco",
            "refrescos",
            "sabritas",
            "sandwich",
            "sandwiches",
            "taco",
            "tacos",
            "torta",
            "tortas",
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
                "avance de seminario de titulacion",
                "eventos escolares",
                "informacion nueva",
                "mantenimiento de la plataforma",
                "mensaje importante",
                "novedades oficiales",
                "registrarme a los talleres",
                "registro a talleres",
            ),
        ),
        (
            "inscripcion",
            (
                "confirmar mi carga",
                "formalizo mi registro",
                "ingresar al instituto",
                "nuevo ingreso",
                "registrar el semestre",
                "registrar mis materias",
                "registro semestral",
                "renovar mi carga",
                "renovar mi inscripcion",
                "solicitar mi ficha",
                "solicitar una ficha",
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
            "cafeteria",
            (
                "abierto durante el receso",
                "abren durante el receso",
                "servicio durante el receso",
                "servicio durante los recesos",
            ),
        ),
        (
            "beca",
            (
                "ayuda financiera",
                "apoyo economico",
                "apoyo escolar",
                "apoyo financiero",
                "apoyos financieros",
                "beneficiado con el apoyo",
                "convocatoria de beca",
                "convocatoria de becas",
                "beca academica",
                "beca cultural",
                "beca deportiva",
                "apoyo familiar",
                "apoyo de convenio",
                "apoyo financiero familiar",
                "apoyo financiero de convenio",
                "conservar el apoyo",
                "mantener el apoyo",
                "renovar el apoyo",
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
                "cabello largo",
                "entrar un estudiante sin profesor",
                "ingresar con sandalias",
                "ingresar sin profesor",
                "mochila sobre la mesa",
                "reservar una practica",
                "reglas de seguridad",
                "reservo una practica",
                "utilizar gafas y guantes",
            ),
        ),
        (
            "titulacion",
            (
                "curso de actualizacion profesional",
                "cedula profesional",
                "excelencia academica",
                "examen general de egreso",
                "informe de experiencia profesional",
                "informe de servicio social",
                "estudios de maestria",
                "estudios de posgrado",
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
        (
            "titulacion",
            (
                "ceneval",
                "titul",
                "grado",
            ),
        ),
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
        (
            "cafeteria",
            (
                "aliment",
                "almuerz",
                "bebid",
                "burrit",
                "cafeter",
                "comedor",
                "gallet",
                "hamburgues",
                "pizza",
                "quesadill",
                "refresc",
                "sandwich",
                "taco",
                "torta",
            ),
        ),
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

    # La palabra "requisitos" por sí sola no permite saber si el
    # estudiante pregunta por inscripción, becas o titulación. No se
    # reutiliza automáticamente el tema del mensaje anterior, por lo que
    # conviene solicitar el trámite o la modalidad correspondiente.
    palabras_requisitos = {
        "documento",
        "documentos",
        "papel",
        "papeles",
        "requisito",
        "requisitos",
    }

    contexto_requisitos = {
        "admision",
        "beca",
        "becas",
        "ceneval",
        "curso",
        "deportiva",
        "deportivo",
        "excelencia",
        "experiencia",
        "familiar",
        "ingreso",
        "inscripcion",
        "inscribirme",
        "maestria",
        "modalidad",
        "modalidades",
        "nuevo",
        "posgrado",
        "reinscripcion",
        "servicio",
        "social",
        "tesis",
        "titulacion",
        "titularme",
        "titulo",
    }

    if (
        palabras & palabras_requisitos
        and not palabras & contexto_requisitos
    ):
        return (
            "¿De qué trámite deseas consultar los requisitos: "
            "nuevo ingreso, reinscripción, becas, titulación u otro "
            "servicio? Si es sobre titulación, también puedes indicar "
            "la modalidad específica."
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

    referencias_uso = {
        "usarlo",
        "usarla",
        "utilizarlo",
        "utilizarla",
    }

    contexto_uso = {
        "biblioteca",
        "cafeteria",
        "computadora",
        "equipo",
        "laboratorio",
        "libro",
        "salon",
    }

    if (
        palabras & referencias_uso
        and not palabras & contexto_uso
    ):
        return (
            "¿Qué espacio, equipo o servicio universitario deseas "
            "utilizar? Por ejemplo, un laboratorio, la biblioteca o una "
            "computadora."
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
        "trafico",
        "transporte",
        "videojuego",
        "videojuegos",
        "virus",
        "vuelo",
        "vuelos",
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
        "contrasena del wifi",
        "marcas de mochilas",
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
        "arroz",
        "bebida",
        "bebidas",
        "burrito",
        "burritos",
        "cafe",
        "cafeteria",
        "cafeteira",
        "comida",
        "desayuno",
        "galleta",
        "galletas",
        "hamburguesa",
        "hamburguesas",
        "menu",
        "pizza",
        "quesadilla",
        "quesadillas",
        "refresco",
        "refrescos",
        "sabritas",
        "sandwich",
        "sandwiches",
        "taco",
        "tacos",
        "torta",
        "tortas",
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
        "admision",
        "ficha",
        "ingreso",
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
        "receso",
        "recesos",
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
        "admision",
        "ficha",
        "ingreso",
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
        "beca",
        "becas",
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
        "actualizacion",
        "arroz",
        "cafeteria",
        "ceneval",
        "comida",
        "alimento",
        "alimentos",
        "burrito",
        "burritos",
        "menu",
        "desayuno",
        "bebida",
        "bebidas",
        "energetica",
        "energeticas",
        "galleta",
        "galletas",
        "grado",
        "hamburguesa",
        "hamburguesas",
        "excelencia",
        "maestria",
        "modalidad",
        "pizza",
        "posgrado",
        "quesadilla",
        "quesadillas",
        "refresco",
        "refrescos",
        "sabritas",
        "sandwich",
        "sandwiches",
        "taco",
        "tacos",
        "tesis",
        "torta",
        "tortas",
        "titulacion",
        "titulo",
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

    if categoria == "inscripcion":
        respuesta = construir_respuesta_inscripcion(
            pregunta_corregida
        )

    elif categoria == "biblioteca":
        respuesta = construir_respuesta_biblioteca(
            pregunta_corregida
        )

    elif categoria == "beca":
        respuesta = construir_respuesta_beca(
            pregunta_corregida
        )

    elif categoria == "titulacion":
        respuesta = construir_respuesta_titulacion(
            pregunta_corregida
        )

    elif categoria == "laboratorio":
        respuesta = construir_respuesta_laboratorio(
            pregunta_corregida
        )

    elif categoria == "cafeteria":
        respuesta = construir_respuesta_cafeteria(
            pregunta_corregida
        )

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

def construir_respuesta_avisos(pregunta, matricula):
    avisos = obtener_avisos_por_estudiante(
        matricula
    )

    if not avisos:
        return (
            "No hay avisos escolares disponibles "
            "para este estudiante."
        )

    pregunta_normalizada = normalizar_texto(pregunta)

    temas_aviso = (
        (
            ("taller", "extracurricular"),
            ("taller",),
        ),
        (
            ("mantenimiento", "plataforma"),
            ("mantenimiento",),
        ),
        (
            ("acompanamiento", "orientacion", "nuevo ingreso"),
            ("acompanamiento", "orientacion"),
        ),
        (
            ("practica integradora", "sistemas digitales"),
            ("practica integradora",),
        ),
        (
            ("feria", "emprendimiento", "innovacion"),
            ("feria", "emprendimiento"),
        ),
        (
            ("seminario", "titulacion", "avance"),
            ("seminario", "avance"),
        ),
    )

    avisos_filtrados = []
    tema_solicitado = False

    for palabras_consulta, palabras_aviso in temas_aviso:
        if any(
            palabra in pregunta_normalizada
            for palabra in palabras_consulta
        ):
            tema_solicitado = True
            avisos_filtrados = [
                aviso
                for aviso in avisos
                if any(
                    palabra in normalizar_texto(
                        f"{aviso['titulo']} {aviso['mensaje']}"
                    )
                    for palabra in palabras_aviso
                )
            ]
            break

    if avisos_filtrados:
        avisos = avisos_filtrados
        lineas = ["Este es el aviso que encontré:"]
    elif tema_solicitado:
        return (
            "No encontré ese aviso entre los comunicados "
            "generales o correspondientes a tu semestre."
        )
    else:
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


def crear_contexto_conversacional():
    return {
        "ultima_categoria": None,
        "ultimo_tema": None,
        "ultima_intencion": None,
        "ultima_pregunta": None,
    }


def extraer_tema_contextual(pregunta):
    texto = normalizar_texto(pregunta)

    temas = (
        "seminario de titulacion",
        "torta con queso",
        "bebida energetica",
        "mantenimiento",
        "talleres",
        "taller",
        "practica integradora",
        "feria de emprendimiento",
        "orientacion",
        "quesadilla",
        "torta",
        "taco",
        "wifi",
        "prestamo",
        "renovacion",
        "tesis",
        "ceneval",
        "cedula profesional",
        "bata",
        "seguridad",
    )

    for tema in temas:
        if tema in texto:
            return tema

    materia = identificar_materia(pregunta)

    if materia is not None:
        return materia["nombre"]

    return None


def extraer_intencion_contextual(pregunta):
    texto = normalizar_texto(pregunta)

    intenciones = (
        (("cuanto cuesta", "precio", "vale"), "precio"),
        (("a que hora", "hasta que hora", "horario"), "horario"),
        (("cuando", "fecha", "que dia"), "fecha"),
        (("donde", "ubicacion", "ubicado"), "ubicacion"),
        (("quien", "contacto", "correo", "telefono"), "contacto"),
        (("reserv", "apart"), "reservacion"),
        (("requisito", "necesito", "debo llevar"), "requisitos"),
    )

    for palabras, intencion in intenciones:
        if any(palabra in texto for palabra in palabras):
            return intencion

    return None


def resolver_pregunta_con_contexto(pregunta, contexto):
    if not contexto:
        return pregunta, None

    categoria_anterior = contexto.get(
        "ultima_categoria"
    )

    if categoria_anterior in {
        None,
        "saludo",
        "capacidades",
        "desconocida",
    }:
        return pregunta, None

    texto = normalizar_texto(pregunta).strip()
    texto = re.sub(r"^[^\w]+", "", texto)

    frases_seguimiento = (
        "a que hora",
        "hasta que hora",
        "cuanto cuesta",
        "cuando es",
        "donde esta",
        "donde se encuentra",
        "quien lo",
        "quien la",
        "como lo",
        "como la",
        "puedo hacerlo",
        "puedo usarlo",
        "puedo utilizarlo",
    )

    es_seguimiento = (
        texto.startswith("y ")
        or texto.startswith("tambien ")
        or any(
            frase in texto
            for frase in frases_seguimiento
        )
        or bool(
            re.search(
                r"\b(ahi|alli|eso|ese|esa|esto|este|esta|lo)\b",
                texto,
            )
        )
    )

    if not es_seguimiento:
        return pregunta, None

    categoria_mencionada = identificar_categoria_prioritaria(
        pregunta
    )

    if (
        categoria_mencionada is not None
        and categoria_mencionada != "horario"
        and categoria_mencionada != categoria_anterior
    ):
        return pregunta, None

    etiquetas_categoria = {
        "horario": "horario de clases",
        "materia": "materias",
        "examen": "examen",
        "profesor": "profesor",
        "calificacion": "calificaciones",
        "aviso": "aviso escolar",
        "academica": "tema academico",
        "inscripcion": "inscripcion",
        "biblioteca": "biblioteca",
        "beca": "beca",
        "titulacion": "titulacion",
        "laboratorio": "laboratorio",
        "cafeteria": "cafeteria",
    }

    etiqueta = etiquetas_categoria.get(
        categoria_anterior,
        categoria_anterior,
    )
    tema_actual = extraer_tema_contextual(pregunta)
    tema = tema_actual or contexto.get("ultimo_tema")
    intencion_actual = extraer_intencion_contextual(
        pregunta
    )
    intencion = (
        intencion_actual
        or contexto.get("ultima_intencion")
    )

    etiquetas_intencion = {
        "precio": "cuanto cuesta",
        "horario": "horario",
        "fecha": "fecha",
        "ubicacion": "ubicacion",
        "contacto": "contacto",
        "reservacion": "reservacion",
        "requisitos": "requisitos",
    }

    partes = [pregunta, etiqueta]

    if tema is not None and tema_actual is None:
        partes.append(tema)

    etiqueta_intencion = etiquetas_intencion.get(intencion)

    if (
        etiqueta_intencion is not None
        and intencion_actual is None
    ):
        partes.append(etiqueta_intencion)

    return " ".join(partes), categoria_anterior


def actualizar_contexto_conversacional(
    contexto,
    categoria,
    pregunta_original,
    pregunta_procesada,
):
    if contexto is None:
        return

    if categoria not in {
        "saludo",
        "capacidades",
        "desconocida",
    }:
        contexto["ultima_categoria"] = categoria

        tema = extraer_tema_contextual(
            pregunta_procesada
        )

        if tema is not None:
            contexto["ultimo_tema"] = tema
        else:
            contexto["ultimo_tema"] = None

        intencion = extraer_intencion_contextual(
            pregunta_procesada
        )

        if intencion is not None:
            contexto["ultima_intencion"] = intencion
        else:
            contexto["ultima_intencion"] = None

    contexto["ultima_pregunta"] = pregunta_original


def procesar_consulta(
    pregunta,
    estudiante,
    contexto=None,
):
    (
        pregunta_procesada,
        categoria_contextual,
    ) = resolver_pregunta_con_contexto(
        pregunta,
        contexto,
    )

    respuesta, tipo, categoria, confianza = (
        buscar_respuesta(pregunta_procesada)
    )

    if categoria_contextual is not None:
        categoria = categoria_contextual
        tipo = TIPOS_CATEGORIA[categoria]
        confianza = max(0.60, confianza)
        respuesta = RESPUESTAS_CATEGORIA[categoria]

        if categoria == "inscripcion":
            respuesta = construir_respuesta_inscripcion(
                pregunta_procesada
            )
        elif categoria == "biblioteca":
            respuesta = construir_respuesta_biblioteca(
                pregunta_procesada
            )
        elif categoria == "beca":
            respuesta = construir_respuesta_beca(
                pregunta_procesada
            )
        elif categoria == "titulacion":
            respuesta = construir_respuesta_titulacion(
                pregunta_procesada
            )
        elif categoria == "laboratorio":
            respuesta = construir_respuesta_laboratorio(
                pregunta_procesada
            )
        elif categoria == "cafeteria":
            respuesta = construir_respuesta_cafeteria(
                pregunta_procesada
            )

    if categoria == "horario":
        materia_identificada = identificar_materia(
            pregunta_procesada
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
            pregunta_procesada
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
            pregunta_procesada
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
            pregunta_procesada
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
            pregunta_procesada,
            estudiante["matricula"]
        )

    elif categoria == "academica":
        (
            respuesta_academica,
            confianza_tema,
            tema_academico,
        ) = responder_consulta_academica(
            pregunta_procesada,
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

    actualizar_contexto_conversacional(
        contexto,
        categoria,
        pregunta,
        pregunta_procesada,
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
