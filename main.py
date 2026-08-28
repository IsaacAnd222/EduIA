from datetime import date

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from base_datos import (
    buscar_estudiante,
    crear_base_datos,
    obtener_asignaciones_por_semestre,
    obtener_avisos_por_estudiante,
    obtener_calificaciones_por_estudiante,
    obtener_examenes_por_estudiante,
    obtener_horario_por_estudiante,
    obtener_materias_por_semestre,
)

datos_entrenamiento = [
    # Saludos
    ("hola", "saludo"),
    ("buenos días", "saludo"),
    ("buenas tardes", "saludo"),
    ("qué tal", "saludo"),

    # Capacidades
    ("qué puedes hacer", "capacidades"),
    ("en qué me puedes ayudar", "capacidades"),

    # Horarios y materias
    ("cuál es mi horario", "horario"),
    ("qué horario tengo", "horario"),
    ("qué clases tengo", "horario"),
    ("qué materias tengo", "materia"),
    ("a qué hora entro", "horario"),
    ("cuáles son mis materias", "materia"),
    ("qué materias curso", "materia"),
    ("lista de materias", "materia"),
    ("muéstrame mis materias", "materia"),

    # Exámenes
    ("cuándo tengo examen", "examen"),
    ("cuándo es mi examen", "examen"),
    ("qué exámenes tengo", "examen"),
    ("fecha de mis exámenes", "examen"),
    ("cuándo presento mi parcial", "examen"),

    # Profesores
    ("quiénes son mis profesores", "profesor"),
    ("quiénes son mis maestros", "profesor"),
    ("quién me da clases", "profesor"),
    ("cómo se llama mi maestro", "profesor"),
    ("quién es mi profesor", "profesor"),
    ("quién es mi docente", "profesor"),
    ("quién imparte mis materias", "profesor"),

    # Calificaciones
    ("cuáles son mis calificaciones", "calificacion"),
    ("quiero ver mis calificaciones", "calificacion"),
    ("quiero consultar mis notas", "calificacion"),
    ("qué resultados obtuve", "calificacion"),

    # Avisos escolares
    ("hay avisos escolares", "aviso"),
    ("cuáles son los avisos", "aviso"),
    ("hay alguna actividad escolar", "aviso"),
    ("qué eventos tiene la escuela", "aviso"),

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
        "Puedo ayudarte con horarios, exámenes, profesores, "
        "calificaciones, avisos y temas académicos."
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

    if confianza < UMBRAL_CONFIANZA:
        categoria = "desconocida"
    else:
        categoria = categorias_conocidas[indice_mejor_resultado]

    tipo = TIPOS_CATEGORIA[categoria]
    respuesta = RESPUESTAS_CATEGORIA[categoria]

    return respuesta, tipo, categoria, confianza

def iniciar_sesion():
    print("\nINICIO DE SESIÓN")

    while True:
        matricula = input(
            "Escribe tu matrícula o 'salir': "
        ).strip()

        if matricula.casefold() == "salir":
            return None

        if not matricula:
            print("La matrícula no puede quedar vacía.")
            continue

        estudiante = buscar_estudiante(matricula)

        if estudiante is None:
            print("No se encontró un estudiante con esa matrícula.")
            print("Inténtalo nuevamente.")
            continue

        print("\nEstudiante identificado correctamente.")
        print(f"Nombre: {estudiante['nombre']}")
        print(f"Carrera: {estudiante['carrera']}")
        print(f"Semestre: {estudiante['semestre']}")
        print(f"Grupo: {estudiante['grupo']}")

        return estudiante

def construir_respuesta_horario(matricula):
    horario = obtener_horario_por_estudiante(matricula)

    if not horario:
        return (
            "No encontré un horario registrado "
            "para este estudiante."
        )

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

def construir_respuesta_profesores(semestre):
    asignaciones = obtener_asignaciones_por_semestre(
        semestre
    )

    if not asignaciones:
        return (
            "No encontré profesores asignados "
            "para tu semestre."
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

def construir_respuesta_calificaciones(matricula):
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

    lineas = ["Estas son tus calificaciones:"]

    for calificacion in calificaciones:
        lineas.append(
            f"- {calificacion['materia']}: "
            f"P1 {calificacion['parcial_1']:.1f}, "
            f"P2 {calificacion['parcial_2']:.1f}, "
            f"P3 {calificacion['parcial_3']:.1f}, "
            f"promedio "
            f"{calificacion['promedio']:.2f}."
        )

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

def construir_respuesta_examenes(matricula):
    examenes = obtener_examenes_por_estudiante(
        matricula
    )

    if not examenes:
        return (
            "No encontré exámenes registrados "
            "para este estudiante."
        )

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

def ejecutar_eduia():
    crear_base_datos()

    print("====================================")
    print(" ASISTENTE VIRTUAL UNIVERSITARIO")
    print("             EduIA")
    print("====================================")
    print("Hola, soy EduIA, tu asistente virtual.")

    while True:
        estudiante_actual = iniciar_sesion()

        if estudiante_actual is None:
            print("Hasta luego.")
            return

        print(
            f"\nBienvenido, {estudiante_actual['nombre']}."
        )
        print(
            "Puedes escribir 'cerrar sesión' para cambiar "
            "de estudiante."
        )
        print("También puedes escribir 'salir' para terminar.")

        while True:
            pregunta = input(
                "\nEscribe tu pregunta: "
            ).strip()

            comando = pregunta.casefold()

            if comando == "salir":
                print("Hasta luego.")
                return

            if comando in {
                "cerrar sesión",
                "cerrar sesion",
                "cerrar secion",
                "cambiar sesión",
                "cambiar sesion",
                "cambiar secion",
            }:
                print("La sesión se cerró correctamente.")
                break

            if not pregunta:
                print("Escribe una pregunta para continuar.")
                continue

            respuesta, tipo, categoria, confianza = (
                buscar_respuesta(pregunta)
            )

            if categoria == "horario":
                respuesta = construir_respuesta_horario(
                    estudiante_actual["matricula"]
                )

            elif categoria == "materia":
                respuesta = construir_respuesta_materias(
                    estudiante_actual["semestre"]
                )

            elif categoria == "profesor":
                respuesta = construir_respuesta_profesores(
                    estudiante_actual["semestre"]
                )

            elif categoria == "calificacion":
                respuesta = (
                    construir_respuesta_calificaciones(
                        estudiante_actual["matricula"]
                    )
                )

            elif categoria == "examen":
                respuesta = construir_respuesta_examenes(
                    estudiante_actual["matricula"]
                )

            elif categoria == "aviso":
                respuesta = construir_respuesta_avisos(
                    estudiante_actual["matricula"]
                )

            print(f"EduIA: {respuesta}")
            print(f"Tipo: {tipo}")
            print(f"Categoría: {categoria}")
            print(f"Confianza: {confianza:.0%}")


if __name__ == "__main__":
    ejecutar_eduia()