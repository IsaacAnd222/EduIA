from collections import defaultdict

from eduia import buscar_respuesta


PRUEBAS = [
    # -------------------------------------------------
    # Variaciones naturales: 30 preguntas
    # -------------------------------------------------

    # Saludos
    ("Natural", "Hola, espero que estés bien", "saludo"),
    ("Natural", "Muy buenas, EduIA", "saludo"),

    # Capacidades
    (
        "Natural",
        "¿Con qué tipo de consultas trabajas?",
        "capacidades",
    ),
    (
        "Natural",
        "Cuéntame en qué eres útil",
        "capacidades",
    ),

    # Horarios
    (
        "Natural",
        "¿Cuál es la hora de mi clase del martes?",
        "horario",
    ),
    (
        "Natural",
        "Necesito saber dónde será mi clase de Sistemas Embebidos",
        "horario",
    ),

    # Materias
    (
        "Natural",
        "¿Qué asignaturas aparecen en mi carga académica?",
        "materia",
    ),
    (
        "Natural",
        "Enséñame las unidades de aprendizaje que curso",
        "materia",
    ),

    # Exámenes
    (
        "Natural",
        "¿Tengo evaluaciones programadas esta semana?",
        "examen",
    ),
    (
        "Natural",
        "Dime la fecha del parcial de Inteligencia Artificial",
        "examen",
    ),

    # Profesores
    (
        "Natural",
        "¿Qué docente imparte Sistemas Embebidos?",
        "profesor",
    ),
    (
        "Natural",
        "Necesito el correo de quien enseña Redes de Computadoras II",
        "profesor",
    ),

    # Calificaciones
    (
        "Natural",
        "¿Aprobé Inteligencia Artificial?",
        "calificacion",
    ),
    (
        "Natural",
        "Muéstrame mis resultados académicos",
        "calificacion",
    ),

    # Avisos
    (
        "Natural",
        "¿Hay comunicados nuevos para mi grupo?",
        "aviso",
    ),
    (
        "Natural",
        "¿Se anunció alguna actividad próxima?",
        "aviso",
    ),

    # Ayuda académica
    (
        "Natural",
        "Enséñame cómo funciona TF-IDF",
        "academica",
    ),
    (
        "Natural",
        "Necesito practicar pseudocódigo",
        "academica",
    ),

    # Inscripciones
    (
        "Natural",
        "¿Ya comenzó el periodo para registrarme?",
        "inscripcion",
    ),
    (
        "Natural",
        "¿Qué pasos sigo para la reinscripción?",
        "inscripcion",
    ),

    # Biblioteca
    (
        "Natural",
        "¿Me permiten llevar un libro a casa?",
        "biblioteca",
    ),
    (
        "Natural",
        "Busco un lugar silencioso para estudiar",
        "biblioteca",
    ),

    # Becas
    (
        "Natural",
        "¿Existe algún apoyo para pagar mis estudios?",
        "beca",
    ),
    (
        "Natural",
        "¿Cómo conozco los resultados de la convocatoria de becas?",
        "beca",
    ),

    # Titulación
    (
        "Natural",
        "¿Qué modalidad puedo elegir para terminar la carrera?",
        "titulacion",
    ),
    (
        "Natural",
        "¿Con quién entrego el expediente para obtener el grado?",
        "titulacion",
    ),

    # Laboratorios
    (
        "Natural",
        "¿Debo apartar el laboratorio antes de una práctica?",
        "laboratorio",
    ),
    (
        "Natural",
        "¿Quién es responsable del laboratorio de cómputo?",
        "laboratorio",
    ),

    # Cafetería
    (
        "Natural",
        "¿Venden alimentos dentro del campus?",
        "cafeteria",
    ),
    (
        "Natural",
        "¿Puedo comprar café por la mañana?",
        "cafeteria",
    ),

    # -------------------------------------------------
    # Errores ortográficos nuevos: 8 preguntas
    # -------------------------------------------------
    (
        "Ortográfica",
        "¿Qué nezesito para reinscrivirme?",
        "inscripcion",
    ),
    (
        "Ortográfica",
        "¿Cuál es mi orario de mañana?",
        "horario",
    ),
    (
        "Ortográfica",
        "¿La viblioteca presta livros?",
        "biblioteca",
    ),
    (
        "Ortográfica",
        "¿Hay apoyo para una beka?",
        "beca",
    ),
    (
        "Ortográfica",
        "Quiero iniciar mi tramite de titulazion",
        "titulacion",
    ),
    (
        "Ortográfica",
        "¿Cómo puedo reservar el labortorio?",
        "laboratorio",
    ),
    (
        "Ortográfica",
        "¿Tienen menu en la cafeteriaa?",
        "cafeteria",
    ),
    (
        "Ortográfica",
        "¿Dónde consulto mis calificaziones?",
        "calificacion",
    ),

    # -------------------------------------------------
    # Preguntas ambiguas: 6 preguntas
    # Sin suficiente información deben ser desconocidas
    # -------------------------------------------------
    (
        "Ambigua",
        "¿Dónde tengo que ir?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Cuándo es?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Qué documentos necesito?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Está abierto?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Quién es el responsable?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Cuánto cuesta?",
        "desconocida",
    ),

    # -------------------------------------------------
    # Consultas fuera del alcance: 6 preguntas
    # -------------------------------------------------
    (
        "Desconocida",
        "¿Cómo estará el clima mañana?",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Quién ganó el partido de fútbol?",
        "desconocida",
    ),
    (
        "Desconocida",
        "Cuéntame un chiste",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Qué ruta de transporte debo tomar?",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Cuál es la contraseña del wifi?",
        "desconocida",
    ),
    (
        "Desconocida",
        "Recomiéndame una película",
        "desconocida",
    ),
]


def ejecutar_validacion():
    resultados = []
    resumen_grupos = defaultdict(
        lambda: {
            "total": 0,
            "correctas": 0,
        }
    )

    print("=" * 110)
    print("VALIDACIÓN INDEPENDIENTE DE EDUIA")
    print("=" * 110)

    for numero, (
        grupo,
        pregunta,
        categoria_esperada,
    ) in enumerate(PRUEBAS, start=1):
        (
            _respuesta,
            _tipo,
            categoria_obtenida,
            confianza,
        ) = buscar_respuesta(pregunta)

        correcta = categoria_obtenida == categoria_esperada

        resumen_grupos[grupo]["total"] += 1

        if correcta:
            resumen_grupos[grupo]["correctas"] += 1
            estado = "CORRECTO"
        else:
            estado = "ERROR"

        resultados.append(
            (
                numero,
                grupo,
                pregunta,
                categoria_esperada,
                categoria_obtenida,
                confianza,
                estado,
            )
        )

        print(f"\nPrueba {numero} — {grupo}")
        print(f"Pregunta:   {pregunta}")
        print(f"Esperado:   {categoria_esperada}")
        print(f"Resultado:  {categoria_obtenida}")
        print(f"Confianza:  {confianza:.0%}")
        print(f"Evaluación: {estado}")

    total = len(resultados)

    correctas = sum(
        1
        for resultado in resultados
        if resultado[6] == "CORRECTO"
    )

    errores = total - correctas
    precision = correctas / total

    print("\n" + "=" * 110)
    print("RESULTADOS POR TIPO DE PREGUNTA")
    print("=" * 110)

    for grupo, datos in resumen_grupos.items():
        precision_grupo = (
            datos["correctas"] / datos["total"]
        )

        print(
            f"{grupo}: "
            f"{datos['correctas']}/{datos['total']} "
            f"({precision_grupo:.2%})"
        )

    print("\n" + "=" * 110)
    print("RESUMEN GENERAL")
    print("=" * 110)
    print(f"Total de pruebas: {total}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {errores}")
    print(f"Precisión independiente: {precision:.2%}")

    if errores:
        print("\nPREGUNTAS CON ERROR")
        print("-" * 110)

        for resultado in resultados:
            (
                numero,
                grupo,
                pregunta,
                esperada,
                obtenida,
                confianza,
                estado,
            ) = resultado

            if estado == "ERROR":
                print(
                    f"{numero}. [{grupo}] {pregunta}\n"
                    f"   Esperado: {esperada} | "
                    f"Obtenido: {obtenida} | "
                    f"Confianza: {confianza:.0%}"
                )


if __name__ == "__main__":
    ejecutar_validacion()