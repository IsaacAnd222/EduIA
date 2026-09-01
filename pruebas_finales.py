from collections import defaultdict

from eduia import buscar_respuesta


PRUEBAS_FINALES = [
    # ==============================================
    # 30 variaciones naturales: 2 por intención
    # ==============================================

    ("Natural", "Saludos, EduIA", "saludo"),
    ("Natural", "Qué onda, EduIA", "saludo"),

    (
        "Natural",
        "¿Qué dudas eres capaz de resolver?",
        "capacidades",
    ),
    (
        "Natural",
        "Descríbeme las funciones que tienes",
        "capacidades",
    ),

    (
        "Natural",
        "¿En qué momento tengo Redes de Computadoras II?",
        "horario",
    ),
    (
        "Natural",
        "Ubica mi clase de Sistemas Embebidos en el horario",
        "horario",
    ),

    (
        "Natural",
        "Dime qué asignaturas forman mi semestre",
        "materia",
    ),
    (
        "Natural",
        "Consulta mi carga de materias",
        "materia",
    ),

    (
        "Natural",
        "¿Cuál es la próxima evaluación de Inteligencia Artificial?",
        "examen",
    ),
    (
        "Natural",
        "Necesito saber cuándo presentaré Sistemas Embebidos",
        "examen",
    ),

    (
        "Natural",
        "Dame los datos del maestro que lleva Inteligencia Artificial",
        "profesor",
    ),
    (
        "Natural",
        "¿Quién está a cargo de Redes de Computadoras II?",
        "profesor",
    ),

    (
        "Natural",
        "¿Pasé Sistemas Embebidos?",
        "calificacion",
    ),
    (
        "Natural",
        "Consulta mi resultado de Redes de Computadoras II",
        "calificacion",
    ),

    (
        "Natural",
        "¿Existe información nueva para estudiantes?",
        "aviso",
    ),
    (
        "Natural",
        "Muéstrame los anuncios universitarios",
        "aviso",
    ),

    (
        "Natural",
        "Ayúdame a comprender RTOS",
        "academica",
    ),
    (
        "Natural",
        "Prepárame una práctica de TF-IDF",
        "academica",
    ),

    (
        "Natural",
        "¿En qué fechas puedo registrar el semestre?",
        "inscripcion",
    ),
    (
        "Natural",
        "Explícame cómo renovar mi inscripción",
        "inscripcion",
    ),

    (
        "Natural",
        "¿Dónde consigo material de consulta?",
        "biblioteca",
    ),
    (
        "Natural",
        "Quiero conocer las reglas de préstamo",
        "biblioteca",
    ),

    (
        "Natural",
        "¿Ofrecen ayuda financiera a los alumnos?",
        "beca",
    ),
    (
        "Natural",
        "¿Dónde entrego una solicitud de apoyo escolar?",
        "beca",
    ),

    (
        "Natural",
        "¿Qué camino debo seguir para obtener el grado?",
        "titulacion",
    ),
    (
        "Natural",
        "¿Puedo titularme mediante un proyecto?",
        "titulacion",
    ),

    (
        "Natural",
        "¿Cómo solicito acceso al laboratorio?",
        "laboratorio",
    ),
    (
        "Natural",
        "Necesito saber si debo agendar una práctica",
        "laboratorio",
    ),

    (
        "Natural",
        "¿Hay servicio de comida en el instituto?",
        "cafeteria",
    ),
    (
        "Natural",
        "¿Dónde consulto los precios del menú?",
        "cafeteria",
    ),

    # ==============================================
    # 10 errores ortográficos nuevos
    # ==============================================

    (
        "Ortográfica",
        "Nesesito mi orario del martes",
        "horario",
    ),
    (
        "Ortográfica",
        "¿Qué materias curzo?",
        "materia",
    ),
    (
        "Ortográfica",
        "¿Cuándo es mi próximo ecsamen de inteligencia artificial?",
        "examen",
    ),
    (
        "Ortográfica",
        "¿Kien es mi docemte de inteligencia artificial?",
        "profesor",
    ),
    (
        "Ortográfica",
        "¿Qué calificasion tengo en redes de computadoras dos?",
        "calificacion",
    ),
    (
        "Ortográfica",
        "¿Hay abisos para mi grupo?",
        "aviso",
    ),
    (
        "Ortográfica",
        "Quiero reinscrivirme al procsimo semestre",
        "inscripcion",
    ),
    (
        "Ortográfica",
        "¿Puedo pedir livross en la viblioteca?",
        "biblioteca",
    ),
    (
        "Ortográfica",
        "¿Cuáles son los requicitos para la titulazion?",
        "titulacion",
    ),
    (
        "Ortográfica",
        "Necesito reservar el lavoratorio",
        "laboratorio",
    ),

    # ==============================================
    # 10 consultas ambiguas
    # ==============================================

    (
        "Ambigua",
        "¿Dónde lo consulto?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Qué necesito llevar?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Quién lo da?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿A qué hora abre?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Cuál es el precio?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Puedo solicitarlo?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Hay alguno disponible?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Cuándo comienza el proceso?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Dónde entrego los papeles?",
        "desconocida",
    ),
    (
        "Ambigua",
        "¿Qué opciones existen?",
        "desconocida",
    ),

    # ==============================================
    # 10 consultas fuera del alcance
    # ==============================================

    (
        "Desconocida",
        "¿Cómo estará el clima este fin de semana?",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Cuál es la ruta del autobús al centro?",
        "desconocida",
    ),
    (
        "Desconocida",
        "Recomiéndame un restaurante cercano",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Qué película puedo ver esta noche?",
        "desconocida",
    ),
    (
        "Desconocida",
        "Pon una canción para estudiar",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Quién ganó el último partido?",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Dónde puedo consultar a un médico?",
        "desconocida",
    ),
    (
        "Desconocida",
        "Explícame cómo cocinar pasta",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Cuáles son las noticias políticas de hoy?",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Dónde puedo comprar una computadora?",
        "desconocida",
    ),
]


def ejecutar_pruebas_finales():
    resultados = []
    resumen_grupos = defaultdict(
        lambda: {
            "total": 0,
            "correctas": 0,
        }
    )

    print("=" * 110)
    print("EVALUACIÓN FINAL INDEPENDIENTE DE EDUIA")
    print("=" * 110)

    for numero, (
        grupo,
        pregunta,
        categoria_esperada,
    ) in enumerate(PRUEBAS_FINALES, start=1):
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
    print("RESULTADOS FINALES POR TIPO")
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
    print("RESUMEN FINAL")
    print("=" * 110)
    print(f"Total de pruebas: {total}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {errores}")
    print(f"Precisión final independiente: {precision:.2%}")

    if errores:
        print("\nERRORES FINALES")
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
    ejecutar_pruebas_finales()