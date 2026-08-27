from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

preguntas_conocidas = [
    "hola",
    "qué puedes hacer",
    "cuál es mi horario",
    "cuándo tengo examen",
    "quiénes son mis profesores",
    "cuáles son mis calificaciones",
]

respuestas_conocidas = [
    "Hola, ¿en qué puedo ayudarte?",
    "Puedo ayudarte con horarios, exámenes, profesores y calificaciones.",
    "Puedo consultar tu horario escolar.",
    "Puedo consultar las fechas de tus exámenes.",
    "Puedo mostrarte la información de tus profesores.",
    "Puedo consultar tus calificaciones.",
]

vectorizador = TfidfVectorizer(strip_accents="unicode")
matriz_preguntas = vectorizador.fit_transform(preguntas_conocidas)

def buscar_respuesta(pregunta_usuario):
    vector_pregunta = vectorizador.transform([pregunta_usuario])

    similitudes = cosine_similarity(
        vector_pregunta,
        matriz_preguntas,
    )[0]

    indice_mejor_respuesta = similitudes.argmax()

    return respuestas_conocidas[indice_mejor_respuesta]

print("====================================")
print(" ASISTENTE VIRTUAL UNIVERSITARIO")
print("           EduIA                 ")
print("====================================")
print("Hola, soy el asistente virtual.")

while True:
    pregunta = input("Escribe tu pregunta: ")

    if pregunta.lower() == "salir":
        print("Hasta luego.")
        break

    respuesta = buscar_respuesta(pregunta)
    print(f"Asistente: {respuesta}")