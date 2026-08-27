from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

datos_entrenamiento = [
    ("hola", "Hola, ¿en qué puedo ayudarte?"),
    ("buenos días", "Hola, ¿en qué puedo ayudarte?"),
    ("buenas tardes", "Hola, ¿en qué puedo ayudarte?"),
    ("qué tal", "Hola, ¿en qué puedo ayudarte?"),

    (
        "qué puedes hacer",
        "Puedo ayudarte con horarios, exámenes, profesores y calificaciones.",
    ),
    (
        "en qué me puedes ayudar",
        "Puedo ayudarte con horarios, exámenes, profesores y calificaciones.",
    ),

    ("cuál es mi horario", "Puedo consultar tu horario escolar."),
    ("qué horario tengo", "Puedo consultar tu horario escolar."),
    ("qué clases tengo", "Puedo consultar tu horario escolar."),
    ("qué materias tengo", "Puedo consultar tu horario escolar."),
    ("a qué hora entro", "Puedo consultar tu horario escolar."),

    ("cuándo tengo examen", "Puedo consultar las fechas de tus exámenes."),
    ("cuándo es mi examen", "Puedo consultar las fechas de tus exámenes."),
    ("qué exámenes tengo", "Puedo consultar las fechas de tus exámenes."),
    ("fecha de mis exámenes", "Puedo consultar las fechas de tus exámenes."),

    (
        "quiénes son mis profesores",
        "Puedo mostrarte la información de tus profesores.",
    ),
    (
        "quiénes son mis maestros",
        "Puedo mostrarte la información de tus profesores.",
    ),
    (
        "quién me da clases",
        "Puedo mostrarte la información de tus profesores.",
    ),
    (
        "cómo se llama mi maestro",
        "Puedo mostrarte la información de tus profesores.",
    ),
    (
        "quién es mi profesor",
        "Puedo mostrarte la información de tus profesores.",
    ),
    (
        "quién es mi docente",
        "Puedo mostrarte la información de tus profesores.",
    ),
    (
        "quién imparte mis materias",
        "Puedo mostrarte la información de tus profesores.",
    ),

    ("cuáles son mis calificaciones", "Puedo consultar tus calificaciones."),
    ("quiero ver mis calificaciones", "Puedo consultar tus calificaciones."),
    ("quiero consultar mis notas", "Puedo consultar tus calificaciones."),
    ("qué resultados obtuve", "Puedo consultar tus calificaciones."),
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

preguntas_conocidas = [
    pregunta for pregunta, respuesta in datos_entrenamiento
]

respuestas_conocidas = [
    respuesta for pregunta, respuesta in datos_entrenamiento
]

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

    indice_mejor_respuesta = similitudes.argmax()
    confianza = float(similitudes[indice_mejor_respuesta])

    if confianza < UMBRAL_CONFIANZA:
        return RESPUESTA_DESCONOCIDA, confianza

    respuesta = respuestas_conocidas[indice_mejor_respuesta]

    return respuesta, confianza

print("====================================")
print(" ASISTENTE VIRTUAL UNIVERSITARIO")
print("           EduIA                 ")
print("====================================")
print("Hola, soy EduIA, tu asistente virtual.")

while True:
    pregunta = input("Escribe tu pregunta: ")

    if pregunta.lower() == "salir":
        print("Hasta luego.")
        break

    respuesta, confianza = buscar_respuesta(pregunta)

    print(f"EduIA: {respuesta}")
    print(f"Confianza: {confianza:.0%}")