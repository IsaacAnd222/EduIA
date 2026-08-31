from eduia import buscar_respuesta


PRUEBAS = [
    # Inscripciones
    ("¿Cuáles son las fechas para reinscribirme?", "inscripcion"),
    ("¿Qué documentos piden para la inscripción?", "inscripcion"),
    ("Quiero registrar mis materias para el próximo periodo", "inscripcion"),
    ("¿En qué ventanilla reviso mi inscripción?", "inscripcion"),
    ("¿Cómo me inscribo al siguiente semestre?", "inscripcion"),

    # Horarios
    ("¿Qué clases me corresponden mañana?", "horario"),
    ("¿A qué hora empieza mi primera clase?", "horario"),
    ("¿En qué salón me toca Inteligencia Artificial?", "horario"),
    ("¿A qué hora salgo de la universidad?", "horario"),
    ("Quiero consultar mi horario semanal", "horario"),

    # Biblioteca
    ("Necesito sacar un libro prestado", "biblioteca"),
    ("¿A qué hora cierra la biblioteca?", "biblioteca"),
    ("¿Dónde puedo devolver un libro?", "biblioteca"),
    ("¿Hay espacios para estudiar en la biblioteca?", "biblioteca"),
    ("¿Qué servicios tiene la bibloteca?", "biblioteca"),

    # Becas
    ("¿La universidad ofrece apoyo económico?", "beca"),
    ("¿Qué documentos solicitan para la beca?", "beca"),
    ("¿Hay alguna convocatoria para estudiantes?", "beca"),
    ("¿Qué debo hacer para conservar mi beca?", "beca"),
    ("¿Dónde pregunto por las vecas?", "beca"),

    # Titulación
    ("¿De qué formas puedo obtener mi título?", "titulacion"),
    ("Quiero comenzar los trámites para titularme", "titulacion"),
    ("¿Puedo hacer una tesis para graduarme?", "titulacion"),
    ("¿Qué papeles debo entregar para mi título?", "titulacion"),
    ("¿Dónde pregunto por la titulasion?", "titulacion"),

    # Laboratorios
    ("¿Cómo reservo el laboratorio de electrónica?", "laboratorio"),
    ("¿Qué reglas de seguridad tiene el laboratorio?", "laboratorio"),
    ("¿Hay laboratorios de computación?", "laboratorio"),
    ("¿Quién autoriza el uso del laboratorio?", "laboratorio"),
    ("¿Puedo entrar al lavotatorio?", "laboratorio"),

    # Cafetería
    ("¿Qué menú tienen hoy?", "cafeteria"),
    ("¿Dónde puedo comprar comida?", "cafeteria"),
    ("¿Cuánto cuesta el desayuno?", "cafeteria"),
    ("¿Abre la cafetería los sábados?", "cafeteria"),
    ("¿A qué hora abre la cafeteira?", "cafeteria"),

    # Calificaciones
    ("¿Cuál es mi promedio final?", "calificacion"),
    ("¿Qué nota obtuve en Inteligencia Artificial?", "calificacion"),
    ("¿Dónde puedo revisar mi boleta?", "calificacion"),
    ("¿Qué materias tengo reprobadas?", "calificacion"),
    ("¿Dónde miro mis calificasiones?", "calificacion"),
]


def ejecutar_pruebas():
    correctas = 0
    resultados = []

    print("=" * 110)
    print("PRUEBAS DE CLASIFICACIÓN DE EDUIA")
    print("=" * 110)

    for numero, (pregunta, categoria_esperada) in enumerate(
        PRUEBAS,
        start=1,
    ):
        (
            _respuesta,
            _tipo,
            categoria_obtenida,
            confianza,
        ) = buscar_respuesta(pregunta)

        es_correcta = categoria_obtenida == categoria_esperada

        if es_correcta:
            correctas += 1
            estado = "CORRECTO"
        else:
            estado = "ERROR"

        resultados.append(
            (
                numero,
                pregunta,
                categoria_esperada,
                categoria_obtenida,
                confianza,
                estado,
            )
        )

        print(f"\nPrueba {numero}")
        print(f"Pregunta:   {pregunta}")
        print(f"Esperado:   {categoria_esperada}")
        print(f"Resultado:  {categoria_obtenida}")
        print(f"Confianza:  {confianza:.0%}")
        print(f"Evaluación: {estado}")

    total = len(PRUEBAS)
    errores = total - correctas
    precision = correctas / total

    print("\n" + "=" * 110)
    print("RESUMEN")
    print("=" * 110)
    print(f"Total de pruebas: {total}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {errores}")
    print(f"Precisión: {precision:.2%}")

    if errores:
        print("\nPREGUNTAS CON ERROR")
        print("-" * 110)

        for resultado in resultados:
            (
                numero,
                pregunta,
                esperada,
                obtenida,
                confianza,
                estado,
            ) = resultado

            if estado == "ERROR":
                print(
                    f"{numero}. {pregunta}\n"
                    f"   Esperado: {esperada} | "
                    f"Obtenido: {obtenida} | "
                    f"Confianza: {confianza:.0%}"
                )


if __name__ == "__main__":
    ejecutar_pruebas()